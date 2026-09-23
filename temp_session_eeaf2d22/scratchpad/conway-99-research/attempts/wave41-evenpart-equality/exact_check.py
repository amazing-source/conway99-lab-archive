#!/usr/bin/env python3
"""Exact equality search for the seven even-part three-fibre edge types.

This discovery-side checker starts with the 36 by 36 matrix

    L = 3I - A_core

over F_7 for the cubic graph on the three twelve-point fibres around a graph
triangle.  After eliminating the first fibre, rank_F7(K_39)=25 is equivalent
to rank 12 for

    H = [ A    B ]       A=P+Q,  B=F+3I+P,  C=P+R,
        [ B^T  C ]

where P,Q,R are perfect-matching matrices and F is a permutation matrix.

For singular A, let N span ker(A), let D=N^T B, and let W span ker(D).
The minimum possible rank is attained exactly when

    rank(D) = (# even parts)

and

    W^T R W = W^T (B^T A^- B - P) W.                 (*)

Here A^- denotes any solution operator on im(A); the right side of (*) is
well-defined because B W is contained in im(A).  The program completely
enumerates all minimum-rank F via observed projection subspaces and tests all
10,395 labelled perfect matchings R against (*).

Only the Python standard library is used.  This is discovery code and cannot
promote its own conclusions to VERIFIED.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence


FORMAT = "wave41-evenpart-equality-v1"
PRIME = 7
SIDE = 12
FROZEN_COMMIT = "4f1754a28723a8e0e4ea3025312cd264b1b117d2"
STANDARD_MATCHING = tuple(index ^ 1 for index in range(SIDE))
EVEN_PARTITIONS = (
    (2, 2, 2),
    (2, 4),
    (6,),
    (1, 1, 2, 2),
    (1, 1, 4),
    (1, 1, 1, 1, 2),
    (1, 2, 3),
)
EXPECTED_MINIMUM_PERMUTATIONS = {
    (1, 1, 1, 1, 2): 80_640,
    (1, 1, 2, 2): 192,
    (1, 1, 4): 768,
    (1, 2, 3): 80_640,
    (2, 2, 2): 32,
    (2, 4): 64,
    (6,): 2_592,
}
INPUTS = {
    "CONJECTURE.md": (
        "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58"
    ),
    "attempts/wave40-exact-coupling-model/exact-results.json": (
        "8613c05c94a9a5f88c45eddbeccbf4c8906c3783aab25747e439f50423bde9ce"
    ),
    "attempts/wave41-multiedge-rank-packing/exact-results.json": (
        "0c20f53b056e0b94f14094d46d957b1b4c5ccd5c6c1920de80ea8ce4e49fdac1"
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def integer_partitions(total: int, minimum: int = 1) -> Iterable[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for tail in integer_partitions(total - first, first):
            yield (first,) + tail


def pairings(vertices: tuple[int, ...]) -> Iterable[tuple[tuple[int, int], ...]]:
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        remainder = vertices[1:index] + vertices[index + 1 :]
        for tail in pairings(remainder):
            yield ((first, second),) + tail


def matching_map(
    edges: Sequence[tuple[int, int]], size: int = SIDE
) -> tuple[int, ...]:
    result = [-1] * size
    for left, right in edges:
        require(left != right, "matching loop")
        require(result[left] == result[right] == -1, "matching repeats a point")
        result[left] = right
        result[right] = left
    require(all(value >= 0 for value in result), "matching incomplete")
    return tuple(result)


def cycle_partition(
    first: Sequence[int], second: Sequence[int]
) -> tuple[int, ...]:
    unseen = set(range(len(first)))
    parts: list[int] = []
    while unseen:
        vertex = min(unseen)
        relation = 0
        size = 0
        while vertex in unseen:
            unseen.remove(vertex)
            size += 1
            vertex = (first if relation == 0 else second)[vertex]
            relation ^= 1
        require(size % 2 == 0, "odd alternating component")
        parts.append(size // 2)
    return tuple(sorted(parts))


@functools.lru_cache(maxsize=1)
def all_matchings() -> tuple[tuple[int, ...], ...]:
    result = tuple(
        matching_map(edges) for edges in pairings(tuple(range(SIDE)))
    )
    require(len(result) == 10_395, "matching census changed")
    require(len(set(result)) == len(result), "duplicate matching")
    return result


@functools.lru_cache(maxsize=1)
def matching_representatives() -> dict[tuple[int, ...], tuple[int, ...]]:
    records: dict[tuple[int, ...], list[tuple[int, ...]]] = defaultdict(list)
    for matching in all_matchings():
        records[cycle_partition(STANDARD_MATCHING, matching)].append(matching)
    require(set(records) == set(integer_partitions(6)), "partition census changed")
    return {partition: min(values) for partition, values in records.items()}


def identity(size: int) -> list[list[int]]:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def permutation_matrix(permutation: Sequence[int]) -> list[list[int]]:
    require(sorted(permutation) == list(range(len(permutation))), "not a permutation")
    return [
        [int(permutation[row] == column) for column in range(len(permutation))]
        for row in range(len(permutation))
    ]


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def matrix_add(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    return [
        [(a + b) % PRIME for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def matrix_subtract(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    return [
        [(a - b) % PRIME for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def matrix_multiply(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    require(bool(left) and bool(right), "empty matrix product")
    require(len(left[0]) == len(right), "matrix product mismatch")
    right_t = transpose(right)
    return [
        [
            sum(a * b for a, b in zip(left_row, right_column)) % PRIME
            for right_column in right_t
        ]
        for left_row in left
    ]


def rref(
    matrix: Sequence[Sequence[int]],
) -> tuple[list[list[int]], tuple[int, ...]]:
    if not matrix:
        return [], ()
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "ragged matrix")
    work = [[entry % PRIME for entry in row] for row in matrix]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(pivot_row, len(work))
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][column], -1, PRIME)
        work[pivot_row] = [
            entry * inverse % PRIME for entry in work[pivot_row]
        ]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (entry - factor * pivot_entry) % PRIME
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(work):
            break
    return work, tuple(pivots)


def rank_mod_prime(matrix: Sequence[Sequence[int]]) -> int:
    return len(rref(matrix)[1])


def kernel_basis(
    matrix: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = rref(matrix)
    width = len(matrix[0])
    free = [column for column in range(width) if column not in pivots]
    result: list[tuple[int, ...]] = []
    for free_column in free:
        vector = [0] * width
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = (-reduced[row][free_column]) % PRIME
        require(
            all(
                sum(a * b for a, b in zip(matrix_row, vector)) % PRIME == 0
                for matrix_row in matrix
            ),
            "kernel reconstruction failed",
        )
        result.append(tuple(vector))
    return tuple(result)


def solve_linear(
    matrix: Sequence[Sequence[int]], rhs: Sequence[int]
) -> tuple[int, ...]:
    require(len(matrix) == len(rhs), "linear solve height mismatch")
    augmented = [
        [entry % PRIME for entry in row] + [rhs[index] % PRIME]
        for index, row in enumerate(matrix)
    ]
    reduced, pivots = rref(augmented)
    width = len(matrix[0])
    require(width not in pivots, "inconsistent linear system")
    solution = [0] * width
    for row, pivot in enumerate(pivots):
        if pivot < width:
            solution[pivot] = reduced[row][width]
    require(
        [
            sum(a * b for a, b in zip(row, solution)) % PRIME
            for row in matrix
        ]
        == [value % PRIME for value in rhs],
        "linear solution reconstruction failed",
    )
    return tuple(solution)


Basis = tuple[tuple[int, ...], ...]


def canonical_basis(vectors: Sequence[Sequence[int]], width: int) -> Basis:
    if not vectors:
        return ()
    require(all(len(vector) == width for vector in vectors), "basis width")
    reduced, pivots = rref(vectors)
    return tuple(tuple(reduced[row]) for row in range(len(pivots)))


def in_span(vector: Sequence[int], basis: Basis) -> bool:
    work = [entry % PRIME for entry in vector]
    for row in basis:
        pivot = next(index for index, entry in enumerate(row) if entry)
        if work[pivot]:
            factor = work[pivot]
            work = [
                (left - factor * right) % PRIME
                for left, right in zip(work, row)
            ]
    return not any(work)


def observed_lines(projections: Mapping[tuple[int, int], tuple[int, ...]]) -> tuple[Basis, ...]:
    width = len(next(iter(projections.values())))
    return tuple(
        sorted(
            {
                canonical_basis((vector,), width)
                for vector in projections.values()
                if any(vector)
            }
        )
    )


def extend_subspaces(
    previous: Sequence[Basis], lines: Sequence[Basis], dimension: int, width: int
) -> tuple[Basis, ...]:
    return tuple(
        sorted(
            {
                candidate
                for basis in previous
                for line in lines
                for candidate in (canonical_basis((*basis, line[0]), width),)
                if len(candidate) == dimension
            }
        )
    )


def supported_permutations(
    projections: Mapping[tuple[int, int], tuple[int, ...]],
    basis: Basis,
) -> Iterable[tuple[int, ...]]:
    allowed = [
        tuple(
            right
            for right in range(SIDE)
            if in_span(projections[(left, right)], basis)
        )
        for left in range(SIDE)
    ]
    order = sorted(range(SIDE), key=lambda left: (len(allowed[left]), left))
    assignment = [-1] * SIDE

    def recurse(position: int, used: int) -> Iterable[tuple[int, ...]]:
        if position == SIDE:
            yield tuple(assignment)
            return
        left = order[position]
        for right in allowed[left]:
            bit = 1 << right
            if used & bit:
                continue
            assignment[left] = right
            yield from recurse(position + 1, used | bit)
            assignment[left] = -1

    yield from recurse(0, 0)


def maximum_support_matching_size(
    projections: Mapping[tuple[int, int], tuple[int, ...]],
    basis: Basis,
) -> int:
    allowed = {
        left: tuple(
            right
            for right in range(SIDE)
            if in_span(projections[(left, right)], basis)
        )
        for left in range(SIDE)
    }
    owner: dict[int, int] = {}

    def augment(left: int, seen: set[int]) -> bool:
        for right in allowed[left]:
            if right in seen:
                continue
            seen.add(right)
            previous = owner.get(right)
            if previous is None or augment(previous, seen):
                owner[right] = left
                return True
        return False

    return sum(augment(left, set()) for left in range(SIDE))


def minimum_permutation_cover(
    projections: Mapping[tuple[int, int], tuple[int, ...]],
    target_dimension: int,
) -> tuple[tuple[tuple[int, ...], ...], dict[str, object]]:
    width = len(next(iter(projections.values())))
    if target_dimension == 0:
        levels = ((),)
    else:
        lines = observed_lines(projections)
        levels = lines
        for dimension in range(2, target_dimension + 1):
            levels = extend_subspaces(levels, lines, dimension, width)
    permutations: set[tuple[int, ...]] = set()
    successful = 0
    generated_with_duplicates = 0
    support_sizes: Counter[int] = Counter()
    for basis in levels:
        maximum = maximum_support_matching_size(projections, basis)
        if maximum < SIDE:
            support_sizes[0] += 1
            continue
        supported = tuple(supported_permutations(projections, basis))
        support_sizes[len(supported)] += 1
        if supported:
            successful += 1
            generated_with_duplicates += len(supported)
            permutations.update(supported)
    # Directly check that every retained permutation spans the target dimension.
    for permutation in permutations:
        columns = [
            projections[(left, permutation[left])] for left in range(SIDE)
        ]
        require(
            rank_mod_prime(transpose(columns)) == target_dimension,
            "retained permutation has nonminimum projection rank",
        )
    return tuple(sorted(permutations)), {
        "ambient_projection_dimension": width,
        "observed_projective_lines": len(observed_lines(projections)),
        "enumerated_target_subspaces": len(levels),
        "successful_target_subspaces": successful,
        "support_permutation_count_with_duplicates": generated_with_duplicates,
        "support_size_histogram": {
            str(size): support_sizes[size] for size in sorted(support_sizes)
        },
        "distinct_minimum_permutations": len(permutations),
        "coverage_argument": (
            "The columns of every target-rank permutation span a target-dimensional "
            "subspace generated by observed projection lines. All such generated "
            "subspaces were enumerated, and every supported bipartite perfect "
            "matching was traversed. Deduplication therefore loses no permutation."
        ),
    }


def projection_signature(
    basis: Sequence[Sequence[int]], matching: Sequence[int]
) -> tuple[int, ...]:
    """Upper-triangular entries of W^T R W for matching matrix R."""

    dimension = len(basis)
    return tuple(
        sum(
            basis[first][vertex] * basis[second][matching[vertex]]
            for vertex in range(SIDE)
        )
        % PRIME
        for first in range(dimension)
        for second in range(first, dimension)
    )


def symmetric_signature(matrix: Sequence[Sequence[int]]) -> tuple[int, ...]:
    require(matrix == transpose(matrix), "matrix is not symmetric")
    return tuple(
        matrix[first][second] % PRIME
        for first in range(len(matrix))
        for second in range(first, len(matrix))
    )


def inverse_permutation(permutation: Sequence[int]) -> tuple[int, ...]:
    result = [-1] * len(permutation)
    for left, right in enumerate(permutation):
        result[right] = left
    require(sorted(result) == list(range(len(permutation))), "inverse failed")
    return tuple(result)


def block_matrix(
    top_left: Sequence[Sequence[int]],
    top_right: Sequence[Sequence[int]],
    bottom_right: Sequence[Sequence[int]],
) -> list[list[int]]:
    return [
        list(top_left[row]) + list(top_right[row])
        for row in range(len(top_left))
    ] + [
        list(row) + list(bottom_right[index])
        for index, row in enumerate(transpose(top_right))
    ]


def equality_constraint(
    a_matrix: Sequence[Sequence[int]],
    b_matrix: Sequence[Sequence[int]],
    p_matrix: Sequence[Sequence[int]],
    radical: Basis,
    expected_projection_rank: int,
) -> tuple[Basis, tuple[int, ...], list[list[int]]]:
    d_matrix = matrix_multiply([list(row) for row in radical], b_matrix)
    require(
        rank_mod_prime(d_matrix) == expected_projection_rank,
        "permutation does not have minimum projection rank",
    )
    right_kernel = kernel_basis(d_matrix)
    bw_columns = matrix_multiply(b_matrix, transpose(right_kernel))
    solutions = [
        solve_linear(a_matrix, column) for column in transpose(bw_columns)
    ]
    cross = matrix_multiply(transpose(bw_columns), transpose(solutions))
    wpw = matrix_multiply(
        matrix_multiply([list(row) for row in right_kernel], p_matrix),
        transpose(right_kernel),
    )
    target = matrix_subtract(cross, wpw)
    require(target == transpose(target), "equality target lost symmetry")
    return right_kernel, symmetric_signature(target), target


def full_k39_rank(
    q_matching: Sequence[int],
    r_matching: Sequence[int],
    column_to_y: Sequence[int],
) -> tuple[int, int]:
    p_matrix = permutation_matrix(STANDARD_MATCHING)
    q_matrix = permutation_matrix(q_matching)
    r_matrix = permutation_matrix(r_matching)
    yz_permutation = inverse_permutation(column_to_y)
    f_matrix = permutation_matrix(yz_permutation)
    t_matrix = matrix_add(
        [[3 * entry % PRIME for entry in row] for row in identity(SIDE)],
        p_matrix,
    )
    h_matrix = block_matrix(
        matrix_add(p_matrix, q_matrix),
        matrix_add(f_matrix, t_matrix),
        matrix_add(p_matrix, r_matrix),
    )
    h_rank = rank_mod_prime(h_matrix)
    return h_rank, 13 + h_rank


def partition_search(partition: tuple[int, ...]) -> dict[str, object]:
    p_matrix = permutation_matrix(STANDARD_MATCHING)
    q_matching = matching_representatives()[partition]
    q_matrix = permutation_matrix(q_matching)
    a_matrix = matrix_add(p_matrix, q_matrix)
    radical = kernel_basis(a_matrix)
    even_parts = sum(part % 2 == 0 for part in partition)
    require(len(radical) == 2 * even_parts, "radical dimension formula changed")
    t_matrix = matrix_add(
        [[3 * entry % PRIME for entry in row] for row in identity(SIDE)],
        p_matrix,
    )

    # B has one 1 in row y of column z, plus the fixed T column.  The
    # enumerated permutation is z -> y; the actual Y-Z row permutation is its
    # inverse.
    projections = {
        (z_index, y_index): tuple(
            (
                radical_row[y_index]
                + sum(
                    radical_row[row] * t_matrix[row][z_index]
                    for row in range(SIDE)
                )
            )
            % PRIME
            for radical_row in radical
        )
        for z_index in range(SIDE)
        for y_index in range(SIDE)
    }
    minimum_permutations, cover = minimum_permutation_cover(
        projections, even_parts
    )
    require(
        len(minimum_permutations) == EXPECTED_MINIMUM_PERMUTATIONS[partition],
        "minimum-permutation diagnostic count changed",
    )

    constraints_by_kernel: dict[
        Basis, dict[tuple[int, ...], list[tuple[int, ...]]]
    ] = defaultdict(lambda: defaultdict(list))
    target_matrices: dict[tuple[Basis, tuple[int, ...]], list[list[int]]] = {}
    for column_to_y in minimum_permutations:
        yz_permutation = inverse_permutation(column_to_y)
        f_matrix = permutation_matrix(yz_permutation)
        b_matrix = matrix_add(f_matrix, t_matrix)
        right_kernel, target_signature, target = equality_constraint(
            a_matrix, b_matrix, p_matrix, radical, even_parts
        )
        constraints_by_kernel[right_kernel][target_signature].append(column_to_y)
        target_matrices[(right_kernel, target_signature)] = target

    surviving_constraints: list[dict[str, object]] = []
    tested_matching_constraints = 0
    realized_f: set[tuple[int, ...]] = set()
    kernel_records: list[dict[str, object]] = []
    for right_kernel, target_groups in sorted(constraints_by_kernel.items()):
        targets = set(target_groups)
        target_hits: dict[tuple[int, ...], tuple[int, ...]] = {}
        signature_histogram: Counter[tuple[int, ...]] = Counter()
        for r_matching in all_matchings():
            signature = projection_signature(right_kernel, r_matching)
            signature_histogram[signature] += 1
            tested_matching_constraints += 1
            if signature in targets and signature not in target_hits:
                target_hits[signature] = r_matching
        for signature, r_matching in sorted(target_hits.items()):
            f_values = target_groups[signature]
            realized_f.update(f_values)
            witness_f = min(f_values)
            h_rank, k39_rank = full_k39_rank(
                q_matching, r_matching, witness_f
            )
            require(h_rank == 12 and k39_rank == 25, "witness rank is not 25")
            surviving_constraints.append(
                {
                    "right_kernel_basis": [list(row) for row in right_kernel],
                    "target_signature": list(signature),
                    "target_matrix_F7": target_matrices[(right_kernel, signature)],
                    "minimum_F_count_for_constraint": len(f_values),
                    "witness_column_to_y_permutation": list(witness_f),
                    "witness_y_to_z_permutation": list(
                        inverse_permutation(witness_f)
                    ),
                    "witness_r_matching": list(r_matching),
                    "H24_rank_F7": h_rank,
                    "K39_rank_F7": k39_rank,
                }
            )
        kernel_records.append(
            {
                "right_kernel_basis": [list(row) for row in right_kernel],
                "target_constraint_count": len(targets),
                "distinct_R_projection_signatures": len(signature_histogram),
                "realized_target_constraint_count": len(target_hits),
                "R_projection_signature_histogram_sha256": sha256_bytes(
                    canonical_json(
                        sorted(
                            (list(signature), count)
                            for signature, count in signature_histogram.items()
                        )
                    )
                ),
            }
        )

    return {
        "partition": list(partition),
        "representative_q_matching": list(q_matching),
        "even_part_count": even_parts,
        "rank_P_plus_Q_F7": rank_mod_prime(a_matrix),
        "radical_dimension": len(radical),
        "radical_basis": [list(row) for row in radical],
        "minimum_permutation_cover": cover,
        "distinct_right_kernels": len(constraints_by_kernel),
        "distinct_equality_constraints": sum(
            len(targets) for targets in constraints_by_kernel.values()
        ),
        "R_catalog_size_per_right_kernel": len(all_matchings()),
        "tested_R_projection_evaluations": tested_matching_constraints,
        "realized_equality_constraint_count": len(surviving_constraints),
        "minimum_F_with_some_rank25_R": len(realized_f),
        "rank25_exists": bool(surviving_constraints),
        "kernel_records": kernel_records,
        "rank25_witnesses_one_per_realized_constraint": surviving_constraints,
    }


@functools.lru_cache(maxsize=1)
def exact_record() -> dict[str, object]:
    observed_inputs = {path: sha256_file(Path(path)) for path in INPUTS}
    require(observed_inputs == INPUTS, "frozen input hash changed")
    results: dict[str, object] = {}
    atomic_outputs: dict[str, object] = {}
    for partition in EVEN_PARTITIONS:
        key = "+".join(map(str, partition))
        path = Path("attempts") / "wave41-evenpart-equality" / f"partial-{key}.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        require(record["partition"] == list(partition), "atomic partition changed")
        require(
            record["minimum_permutation_cover"]["distinct_minimum_permutations"]
            == EXPECTED_MINIMUM_PERMUTATIONS[partition],
            "atomic minimum-permutation count changed",
        )
        require(not record["rank25_exists"], "atomic rank-25 survivor appeared")
        require(
            record["realized_equality_constraint_count"] == 0,
            "atomic equality survivor appeared",
        )
        results[key] = record
        atomic_outputs[key] = {
            "path": path.as_posix(),
            "sha256": sha256_file(path),
        }
    positive = [
        key for key, record in results.items() if record["rank25_exists"]
    ]
    excluded = [
        key for key, record in results.items() if not record["rank25_exists"]
    ]
    return {
        "format": FORMAT,
        "role": "proof_b",
        "claim_label": "CANDIDATE",
        "git_commit": FROZEN_COMMIT,
        "scope": (
            "Exact K39 rank-25 equality compatibility for all seven edge-local "
            "alternating partition types containing an even part."
        ),
        "inputs": observed_inputs,
        "atomic_outputs": atomic_outputs,
        "normalization": {
            "P": list(STANDARD_MATCHING),
            "Q_representatives": {
                "+".join(map(str, partition)): list(
                    matching_representatives()[partition]
                )
                for partition in EVEN_PARTITIONS
            },
            "labelled_R_perfect_matchings": len(all_matchings()),
            "automorphism_warning": (
                "Only local fibre relabelling fixes P and selects one Q per "
                "alternating partition. Every minimum F and every labelled R "
                "is then tested; no automorphism of a completed graph is assumed."
            ),
        },
        "rank_derivation": {
            "elimination": (
                "Eliminating 3I-P contributes rank 12 and "
                "rank(K39)=13+rank(H24)."
            ),
            "H24": "[P+Q,F+3I+P;(F+3I+P)^T,P+R]",
            "singular_equality_condition": (
                "If N spans ker(P+Q), D=N^T(F+3I+P), and W spans ker(D), "
                "rank(K39)=25 iff rank(D)=e and "
                "W^T R W=W^T(B^T(P+Q)^-B-P)W, where e is the number of "
                "even alternating parts."
            ),
        },
        "partition_results": results,
        "summary": {
            "positive_rank25_types": positive,
            "excluded_rank25_types": excluded,
            "universal_rank26_candidate": not positive,
            "classification": (
                "COMPLETE_LOCAL_EQUALITY_CLASSIFICATION_PENDING_VERIFICATION"
            ),
            "global_graph_status": "UNKNOWN",
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "A local rank-25 witness is not a 99-vertex graph or extension certificate.",
            "A local exclusion only strengthens the universal rank floor after independent verification.",
            "No endpoint exclusion, general n3 upper-bound improvement, or novelty claim is made.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output", type=Path)
    mode.add_argument("--verify", type=Path)
    parser.add_argument(
        "--partition",
        help="Run one diagnostic partition, such as 2+2+2, instead of the package.",
    )
    args = parser.parse_args()
    if args.partition:
        partition = tuple(int(value) for value in args.partition.split("+"))
        require(partition in EVEN_PARTITIONS, "unknown even partition")
        payload = canonical_json(partition_search(partition))
    else:
        payload = canonical_json(exact_record())
    if args.verify:
        require(args.verify.read_bytes() == payload, "stored result differs")
        print(f"PASS: {args.verify} matches exact regeneration")
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
        print(f"WROTE {args.output} sha256={sha256_bytes(payload)}")
    else:
        print(payload.decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
