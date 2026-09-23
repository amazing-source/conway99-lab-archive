#!/usr/bin/env python3
"""Exact Wave 41 multi-edge rank-packing checks for Conway-99.

This discovery-side program has three deliberately separated purposes.

1. It rules out equality in the Wave 40 rank-25 bound for the four
   edge-local alternating types whose partition parts are all odd.
2. It identifies a universal three-dimensional compact-support kernel inside
   every 39-point triangle block.  This is the precise obstruction to simply
   adding a symmetric-border contribution from the remaining 60 vertices.
3. It emits low-rank, fully specified three-fibre controls showing that local
   triangle blocks alone cannot support much larger claimed floors.

Only the Python standard library is used.  This is discovery code and does
not verify its own mathematical conclusions.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


FORMAT = "wave41-multiedge-rank-packing-v1"
PRIME = 7
SIDE = 12
CORE = 36
BLOCK = 39
FROZEN_COMMIT = "4f1754a28723a8e0e4ea3025312cd264b1b117d2"
INPUTS = {
    "CONJECTURE.md": (
        "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58"
    ),
    "attempts/wave40-exact-coupling-model/exact-results.json": (
        "8613c05c94a9a5f88c45eddbeccbf4c8906c3783aab25747e439f50423bde9ce"
    ),
    "attempts/wave40-exact-coupling-model/subspace-certificate.json": (
        "90b8eb3f88424ffe6ae7618a3063620a2dedff604ad2fac10894fb6278f17c9a"
    ),
    "attempts/wave40-exact-coupling-model/full-block-scout-results.json": (
        "9e03c6d3a465bbbebbe0837910732aeaedfe64a3a595da047f1255458d9ddcc3"
    ),
    "verification/wave40-exact-coupling-model/independent-results.json": (
        "ff7916d0f5c74c47c8d7787c5cbcc84785cbccd3644d8d03d73e47b73908c0f5"
    ),
}


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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
        require(left != right, "matching contains a loop")
        require(result[left] == result[right] == -1, "matching repeats a point")
        result[left] = right
        result[right] = left
    require(all(value >= 0 for value in result), "matching is incomplete")
    return tuple(result)


STANDARD_MATCHING = tuple(index ^ 1 for index in range(SIDE))


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
        require(size % 2 == 0, "alternating component has odd order")
        parts.append(size // 2)
    return tuple(sorted(parts))


@functools.lru_cache(maxsize=1)
def matching_catalog() -> dict[tuple[int, ...], dict[str, object]]:
    catalog: dict[tuple[int, ...], dict[str, object]] = {
        partition: {"count": 0, "representative": None}
        for partition in integer_partitions(6)
    }
    total = 0
    for edges in pairings(tuple(range(SIDE))):
        matching = matching_map(edges)
        partition = cycle_partition(STANDARD_MATCHING, matching)
        entry = catalog[partition]
        entry["count"] = int(entry["count"]) + 1
        representative = entry["representative"]
        if representative is None or matching < representative:
            entry["representative"] = matching
        total += 1
    require(total == 10_395, "labelled matching census changed")
    require(len(catalog) == 11, "partition census changed")
    require(
        all(entry["representative"] is not None for entry in catalog.values()),
        "a partition type has no representative",
    )
    return catalog


def identity(size: int) -> list[list[int]]:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def permutation_matrix(permutation: Sequence[int]) -> list[list[int]]:
    size = len(permutation)
    require(sorted(permutation) == list(range(size)), "not a permutation")
    return [
        [int(permutation[row] == column) for column in range(size)]
        for row in range(size)
    ]


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def matrix_add(
    left: Sequence[Sequence[int]],
    right: Sequence[Sequence[int]],
    prime: int = PRIME,
) -> list[list[int]]:
    return [
        [(a + b) % prime for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def matrix_subtract(
    left: Sequence[Sequence[int]],
    right: Sequence[Sequence[int]],
    prime: int = PRIME,
) -> list[list[int]]:
    return [
        [(a - b) % prime for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def scalar_multiply(
    scalar: int, matrix: Sequence[Sequence[int]], prime: int = PRIME
) -> list[list[int]]:
    return [[scalar * entry % prime for entry in row] for row in matrix]


def matrix_multiply(
    left: Sequence[Sequence[int]],
    right: Sequence[Sequence[int]],
    prime: int = PRIME,
) -> list[list[int]]:
    require(bool(left) and bool(right), "empty matrix product")
    require(len(left[0]) == len(right), "matrix dimensions do not match")
    right_t = transpose(right)
    return [
        [
            sum(a * b for a, b in zip(left_row, right_column)) % prime
            for right_column in right_t
        ]
        for left_row in left
    ]


def rref(
    matrix: Sequence[Sequence[int]], prime: int = PRIME
) -> tuple[list[list[int]], tuple[int, ...]]:
    if not matrix:
        return [], ()
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "ragged matrix")
    work = [[entry % prime for entry in row] for row in matrix]
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
        inverse = pow(work[pivot_row][column], -1, prime)
        work[pivot_row] = [
            entry * inverse % prime for entry in work[pivot_row]
        ]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (entry - factor * pivot_entry) % prime
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(work):
            break
    return work, tuple(pivots)


def rank_mod_prime(
    matrix: Sequence[Sequence[int]], prime: int = PRIME
) -> int:
    return len(rref(matrix, prime)[1])


def inverse_mod_prime(
    matrix: Sequence[Sequence[int]], prime: int = PRIME
) -> list[list[int]]:
    size = len(matrix)
    require(
        size > 0 and all(len(row) == size for row in matrix),
        "inverse requires a square matrix",
    )
    augmented = [
        [entry % prime for entry in row] + identity(size)[index]
        for index, row in enumerate(matrix)
    ]
    reduced, pivots = rref(augmented, prime)
    require(pivots[:size] == tuple(range(size)), "matrix is singular")
    inverse = [row[size:] for row in reduced]
    require(
        matrix_multiply(matrix, inverse, prime) == identity(size),
        "inverse reconstruction failed",
    )
    return inverse


def add_edge(adjacency: list[list[int]], left: int, right: int) -> None:
    require(left != right, "loop edge")
    require(not adjacency[left][right], "repeated edge")
    adjacency[left][right] = 1
    adjacency[right][left] = 1


def core_adjacency(
    q_matching: Sequence[int],
    r_matching: Sequence[int],
    yz_permutation: Sequence[int],
) -> list[list[int]]:
    """Build the 36-point three-fibre cubic core."""

    require(len(q_matching) == len(r_matching) == SIDE, "matching size changed")
    require(len(yz_permutation) == SIDE, "permutation size changed")
    adjacency = [[0] * CORE for _ in range(CORE)]
    for offset, matching in (
        (0, STANDARD_MATCHING),
        (SIDE, q_matching),
        (2 * SIDE, r_matching),
    ):
        for left, right in enumerate(matching):
            if left < right:
                add_edge(adjacency, offset + left, offset + right)
    for index in range(SIDE):
        add_edge(adjacency, index, SIDE + index)
        add_edge(adjacency, index, 2 * SIDE + index)
        add_edge(
            adjacency,
            SIDE + index,
            2 * SIDE + yz_permutation[index],
        )
    require(all(sum(row) == 3 for row in adjacency), "core is not cubic")
    return adjacency


def laplacian_three(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            (3 * int(row == column) - adjacency[row][column]) % PRIME
            for column in range(len(adjacency))
        ]
        for row in range(len(adjacency))
    ]


def triangle_block(adjacency_core: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return K=J-I-2A on a triangle and its 36 outside neighbours."""

    require(len(adjacency_core) == CORE, "core order changed")
    adjacency = [[0] * BLOCK for _ in range(BLOCK)]
    for left, right in ((0, 1), (1, 2), (2, 0)):
        add_edge(adjacency, left, right)
    for fibre in range(3):
        for point in range(SIDE):
            add_edge(adjacency, fibre, 3 + fibre * SIDE + point)
    for left in range(CORE):
        for right in range(left + 1, CORE):
            if adjacency_core[left][right]:
                add_edge(adjacency, 3 + left, 3 + right)
    return [
        [
            (1 - int(row == column) - 2 * adjacency[row][column]) % PRIME
            for column in range(BLOCK)
        ]
        for row in range(BLOCK)
    ]


def component_sizes(adjacency: Sequence[Sequence[int]]) -> list[int]:
    unseen = set(range(len(adjacency)))
    sizes: list[int] = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        stack = [start]
        size = 0
        while stack:
            vertex = stack.pop()
            size += 1
            for neighbor, entry in enumerate(adjacency[vertex]):
                if entry and neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
        sizes.append(size)
    return sorted(sizes)


def triangle_count(adjacency: Sequence[Sequence[int]]) -> int:
    size = len(adjacency)
    return sum(
        adjacency[first][second]
        and adjacency[first][third]
        and adjacency[second][third]
        for first in range(size)
        for second in range(first + 1, size)
        for third in range(second + 1, size)
    )


def repeat_local_map(local_map: Sequence[int], repeats: int) -> tuple[int, ...]:
    width = len(local_map)
    return tuple(
        repeat * width + local_map[index]
        for repeat in range(repeats)
        for index in range(width)
    )


def full_block_rank_record(
    q_matching: Sequence[int],
    r_matching: Sequence[int],
    yz_permutation: Sequence[int],
) -> dict[str, object]:
    adjacency = core_adjacency(q_matching, r_matching, yz_permutation)
    laplacian = laplacian_three(adjacency)
    block = triangle_block(adjacency)
    laplacian_rank = rank_mod_prime(laplacian)
    block_rank = rank_mod_prime(block)
    require(
        block_rank == 1 + laplacian_rank,
        "rank(K39)=1+rank(3I-Acore) failed",
    )
    return {
        "q_matching": list(q_matching),
        "r_matching": list(r_matching),
        "yz_permutation": list(yz_permutation),
        "core_component_sizes": component_sizes(adjacency),
        "core_triangle_count": triangle_count(adjacency),
        "laplacian_rank_F7": laplacian_rank,
        "laplacian_nullity_F7": CORE - laplacian_rank,
        "K39_rank_F7": block_rank,
    }


def quadratic_value(
    symmetric: Sequence[Sequence[int]], vector: Sequence[int]
) -> int:
    return (
        sum(
            vector[row] * symmetric[row][column] * vector[column]
            for row in range(len(vector))
            for column in range(len(vector))
        )
        % PRIME
    )


def all_odd_equality_obstruction() -> dict[str, object]:
    """Rule out K39 rank 25 for every all-odd partition type.

    Eliminate the X fibre from L=3I-Acore.  Since

        (3I-P)^(-1)=3I+P  over F_7,

    the remaining 24-block, up to a harmless global sign, is

        H = [ P+Q       F+(3I+P) ]
            [ F^T+(3I+P)   P+R   ].

    If all alternating parts of (P,Q) are odd, P+Q is invertible.  Therefore
    rank(K39)=25 would force the Schur complement to vanish:

        P+R=(F^T+T)(P+Q)^(-1)(F+T),  T=3I+P.

    The left side has zero diagonal.  Checking the 144 possible preimage /
    column pairs gives a complete necessary assignment graph.  Three types
    have an empty column.  Type 3+3 has one forced permutation, but its forced
    R is not a zero-one fixed-point-free matching matrix.
    """

    p_matrix = permutation_matrix(STANDARD_MATCHING)
    i_matrix = identity(SIDE)
    t_matrix = matrix_add(scalar_multiply(3, i_matrix), p_matrix)
    require(
        matrix_multiply(
            matrix_subtract(scalar_multiply(3, i_matrix), p_matrix),
            t_matrix,
        )
        == i_matrix,
        "(3I-P)^(-1)=3I+P failed",
    )

    records: dict[str, object] = {}
    for partition, entry in matching_catalog().items():
        if any(part % 2 == 0 for part in partition):
            continue
        key = "+".join(map(str, partition))
        q_matching = entry["representative"]
        require(isinstance(q_matching, tuple), "missing representative")
        q_matrix = permutation_matrix(q_matching)
        leading = matrix_add(p_matrix, q_matrix)
        require(rank_mod_prime(leading) == SIDE, "all-odd leading block singular")
        leading_inverse = inverse_mod_prime(leading)

        allowed_preimages: list[list[int]] = []
        for column in range(SIDE):
            allowed: list[int] = []
            for preimage in range(SIDE):
                vector = [0] * SIDE
                vector[preimage] = (vector[preimage] + 1) % PRIME
                vector[column] = (vector[column] + 3) % PRIME
                mate = STANDARD_MATCHING[column]
                vector[mate] = (vector[mate] + 1) % PRIME
                if quadratic_value(leading_inverse, vector) == 0:
                    allowed.append(preimage)
            allowed_preimages.append(allowed)

        impossible_columns = [
            column
            for column, allowed in enumerate(allowed_preimages)
            if not allowed
        ]
        record: dict[str, object] = {
            "partition": list(partition),
            "representative_q_matching": list(q_matching),
            "rank_P_plus_Q_F7": rank_mod_prime(leading),
            "diagonal_isotropy_allowed_preimage_counts": [
                len(allowed) for allowed in allowed_preimages
            ],
            "impossible_columns": impossible_columns,
            "rank_25_equality_possible": False,
        }
        if impossible_columns:
            record["exclusion"] = (
                "A rank-25 equality would require a zero diagonal Schur "
                "target, but at least one F column has no isotropic preimage."
            )
        else:
            require(
                all(len(allowed) == 1 for allowed in allowed_preimages),
                "nonempty equality assignment is not forced",
            )
            inverse_permutation = tuple(
                allowed[0] for allowed in allowed_preimages
            )
            require(
                sorted(inverse_permutation) == list(range(SIDE)),
                "forced preimages do not form a permutation",
            )
            yz_permutation = [0] * SIDE
            for column, preimage in enumerate(inverse_permutation):
                yz_permutation[preimage] = column
            f_matrix = permutation_matrix(yz_permutation)
            border = matrix_add(f_matrix, t_matrix)
            schur_target = matrix_multiply(
                matrix_multiply(transpose(border), leading_inverse),
                border,
            )
            forced_r = matrix_subtract(schur_target, p_matrix)
            histogram = Counter(
                entry for row in forced_r for entry in row
            )
            is_matching = (
                forced_r == transpose(forced_r)
                and all(forced_r[index][index] == 0 for index in range(SIDE))
                and all(
                    entry in (0, 1)
                    for row in forced_r
                    for entry in row
                )
                and all(sum(row) == 1 for row in forced_r)
            )
            require(not is_matching, "rank-25 equality unexpectedly survived")
            record.update(
                {
                    "forced_inverse_permutation": list(inverse_permutation),
                    "forced_yz_permutation": yz_permutation,
                    "forced_R_entry_histogram_F7": {
                        str(value): histogram[value]
                        for value in sorted(histogram)
                    },
                    "forced_R_is_perfect_matching": is_matching,
                    "forced_R_rows_F7": forced_r,
                    "exclusion": (
                        "The unique diagonal-isotropic F forces a symmetric "
                        "zero-diagonal R target with entries 2 and 3, not a "
                        "zero-one perfect matching."
                    ),
                }
            )
        records[key] = record

    require(
        set(records) == {
            "1+1+1+1+1+1",
            "1+1+1+3",
            "1+5",
            "3+3",
        },
        "all-odd partition set changed",
    )
    return {
        "scope": (
            "Every fully specified 39-point triangle block whose selected "
            "base edge has an all-odd alternating partition."
        ),
        "schur_formula": (
            "rank_F7(K39)=25+rank_F7(P+R-(F^T+3I+P)"
            "(P+Q)^(-1)(F+3I+P))"
        ),
        "complete_assignment_checks": 4 * SIDE * SIDE,
        "records": records,
        "candidate_conclusion": "rank_F7(K39)>=26 for every all-odd edge type",
        "global_candidate_consequence": (
            "If a hypothetical Conway-99 graph contains an all-odd edge "
            "type, then rank_F7(M)>=26."
        ),
    }


def structural_compact_kernel_record() -> dict[str, object]:
    """Record the exact three-dimensional border-packing obstruction."""

    catalog = matching_catalog()
    block_checks: dict[str, object] = {}
    for partition, entry in catalog.items():
        q_matching = entry["representative"]
        require(isinstance(q_matching, tuple), "missing matching representative")
        adjacency = core_adjacency(
            q_matching,
            STANDARD_MATCHING,
            tuple(range(SIDE)),
        )
        block = triangle_block(adjacency)
        vectors: list[list[int]] = []
        for fibre in range(3):
            vector = [0] * BLOCK
            vector[fibre] = 4
            for other in range(3):
                if other != fibre:
                    vector[other] = 1
            for point in range(SIDE):
                vector[3 + fibre * SIDE + point] = 1
            product = [
                sum(row[column] * vector[column] for column in range(BLOCK))
                % PRIME
                for row in block
            ]
            require(product == [0] * BLOCK, "structural vector left block kernel")
            vectors.append(vector)
        require(rank_mod_prime(vectors) == 3, "structural vectors lost independence")
        block_checks["+".join(map(str, partition))] = {
            "kernel_vectors_checked": 3,
            "kernel_vector_rank_F7": 3,
        }

    # Exact integer polynomial multiplication:
    # (J-I-2A)(A+4I)=14J-7A-28I.
    polynomial_product = {"J": 14, "A": -7, "I": -28}
    require(
        all(coefficient % PRIME == 0 for coefficient in polynomial_product.values()),
        "global compact-kernel polynomial is not divisible by seven",
    )
    outside_triangle_contribution = 4 + 1 + 1
    outside_fibre_contribution = (SIDE - 2) - 2
    outside_dot = outside_triangle_contribution + outside_fibre_contribution
    require(outside_dot == 14 and outside_dot % PRIME == 0, "outside dot changed")

    return {
        "vector_for_vertex_v": (
            "h_v=(A+4I)e_v: value 4 at v, value 1 on N(v), and 0 elsewhere."
        ),
        "support": (
            "For every graph triangle T containing v, supp(h_v) is contained "
            "in T union (N(T)-T), the associated 39-point triangle block."
        ),
        "global_kernel_identity_over_integers": (
            "(J-I-2A)(A+4I)=14J-7A-28I"
        ),
        "global_kernel_identity_mod_7": "K(A+4I)=0",
        "three_vectors_per_triangle": (
            "The three h_v for v in T are independent because their "
            "restriction to T is the 3 by 3 matrix with diagonal 4 and "
            "off-diagonal 1, of rank 3 over F_7."
        ),
        "outside_column_check": {
            "triangle_contribution": outside_triangle_contribution,
            "one_fibre_contribution": outside_fibre_contribution,
            "integer_total": outside_dot,
            "residue_mod_7": outside_dot % PRIME,
            "reason": (
                "An outside vertex is nonadjacent to all three vertices of T "
                "and has exactly two neighbours in each twelve-point fibre."
            ),
        },
        "block_checks": block_checks,
        "packing_obstruction": (
            "For any kernel-basis matrix H of the 39-block and its 39 by 60 "
            "border U, ker(H^T U) has dimension at least three.  Therefore "
            "the symmetric-border lemma cannot make the six-dimensional "
            "projection full rank in a minimum-rank block, and overlapping "
            "triangle blocks cannot be added without quotienting these "
            "globally repeated vertex-star kernel directions."
        ),
        "global_span_context": {
            "K_mod_7": "J-2(A+4I)",
            "rank_relation": (
                "rank_F7(A+4I)=rank_F7(K)+1; im(K) lies in the augmentation "
                "hyperplane, while 1 lies in im(A+4I)."
            ),
        },
    }


def low_rank_controls() -> dict[str, object]:
    """Return exact controls limiting any one-block-only strengthening."""

    # Three repeated connected 12-vertex components.  Each component has
    # Laplacian nullity three and two core triangles.
    local_q_4 = (2, 3, 0, 1)
    local_r_4 = (2, 3, 0, 1)
    local_f_4 = (0, 2, 1, 3)
    generic = full_block_rank_record(
        repeat_local_map(local_q_4, 3),
        repeat_local_map(local_r_4, 3),
        repeat_local_map(local_f_4, 3),
    )
    require(generic["core_component_sizes"] == [12, 12, 12], "generic components changed")
    require(generic["core_triangle_count"] == 6, "generic triangle count changed")
    require(generic["laplacian_nullity_F7"] == 9, "generic nullity changed")
    require(generic["K39_rank_F7"] == 28, "generic control rank changed")

    # Two repeated connected 18-vertex components.  This core is triangle
    # free, hence compatible with the local prism-free condition at T.
    local_q_6 = (2, 4, 0, 5, 1, 3)
    local_r_6 = (2, 5, 0, 4, 3, 1)
    local_f_6 = (5, 3, 4, 1, 0, 2)
    triangle_free = full_block_rank_record(
        repeat_local_map(local_q_6, 2),
        repeat_local_map(local_r_6, 2),
        repeat_local_map(local_f_6, 2),
    )
    require(
        triangle_free["core_component_sizes"] == [18, 18],
        "triangle-free components changed",
    )
    require(
        triangle_free["core_triangle_count"] == 0,
        "triangle-free control acquired a core triangle",
    )
    require(
        triangle_free["laplacian_nullity_F7"] == 8,
        "triangle-free nullity changed",
    )
    require(
        triangle_free["K39_rank_F7"] == 29,
        "triangle-free control rank changed",
    )

    return {
        "generic_three_fibre_control": {
            **generic,
            "scope": (
                "Fully specified theorem-forced three-fibre matching data. "
                "It is a local relaxation with core triangles and is not a "
                "completed 99-vertex graph."
            ),
        },
        "triangle_free_three_fibre_control": {
            **triangle_free,
            "scope": (
                "Fully specified triangle-free three-fibre matching data, "
                "compatible with the one-triangle prism-free condition.  It "
                "does not include the 60 outside vertices and is not an "
                "endpoint graph or extension certificate."
            ),
        },
        "consequence": (
            "A proof using only the forced 39-point triangle block cannot "
            "claim a universal floor above 28, or a prism-free local floor "
            "above 29, without additional outside/global compatibility."
        ),
    }


def seven_star_assessment() -> dict[str, object]:
    return {
        "greedy_independent_set": (
            "A graph of order 99 and maximum degree 14 has an independent "
            "set of size at least ceil(99/15)=7."
        ),
        "triangle_indices": (
            "The seven 7-triangle vertex stars are pairwise disjoint, giving "
            "49 triangle indices, because independent vertices cannot occur "
            "in one graph triangle."
        ),
        "conditional_endpoint_diagonal_blocks": "Each 7 by 7 star block of M is 4I.",
        "rank_target": (
            "Since rank_Q(M)=44, the 49 by 49 principal block must have "
            "nullity at least five."
        ),
        "pairwise_cross_block_data": (
            "For each nonadjacent vertex pair the 7 by 7 cross block has row "
            "and column sums (-2,-2,1,1,1,1,1), up to the two common-neighbour "
            "labels."
        ),
        "status": "OPEN_COMPATIBILITY_TARGET",
        "obstruction": (
            "The 21 pair blocks cannot be selected independently: their "
            "entries reuse graph edges, common-neighbour vertices, and "
            "triangle labels, and the assembled matrix must also satisfy "
            "M^2=21M.  Wave 35 supplies only one relaxed pair control.  No "
            "49-block enumeration or gluing certificate is available here."
        ),
    }


@functools.lru_cache(maxsize=1)
def exact_record() -> dict[str, object]:
    observed_inputs = {
        path: sha256_file(Path(path)) for path in INPUTS
    }
    require(observed_inputs == INPUTS, "a frozen input hash changed")
    catalog = matching_catalog()
    return {
        "format": FORMAT,
        "role": "proof_a",
        "claim_label": "CANDIDATE",
        "git_commit": FROZEN_COMMIT,
        "scope": (
            "Universal and prism-free multi-edge rank-packing consequences "
            "starting from the Wave 40 rank_F7(M)>=25 theorem."
        ),
        "inputs": observed_inputs,
        "matching_normalization": {
            "labelled_perfect_matchings": sum(
                int(entry["count"]) for entry in catalog.values()
            ),
            "alternating_partition_types": len(catalog),
            "canonical_representatives": {
                "+".join(map(str, partition)): list(entry["representative"])
                for partition, entry in sorted(catalog.items())
            },
            "automorphism_warning": (
                "Canonicalizing (P,Q) uses only a local relabelling; F remains "
                "an arbitrary permutation and R remains an arbitrary perfect "
                "matching.  No completed-graph automorphism is assumed."
            ),
        },
        "all_odd_rank_equality_obstruction": all_odd_equality_obstruction(),
        "structural_compact_kernel": structural_compact_kernel_record(),
        "low_rank_controls": low_rank_controls(),
        "seven_star_49_block_assessment": seven_star_assessment(),
        "conclusion": {
            "candidate_scoped_rank_improvement": (
                "An all-odd edge type forces rank_F7(M)>=26."
            ),
            "new_universal_rank_floor_proved": False,
            "new_endpoint_rank_floor_proved": False,
            "endpoint_excluded": False,
            "new_general_upper_bound_on_n3": False,
            "strongest_general_upper_bound_on_n3": 4158,
            "conway_99_status": "UNKNOWN",
            "novelty": "UNKNOWN",
            "strongest_exact_obstruction": (
                "Every 39-point triangle block has a 3D compact-support "
                "kernel spanned by vertex-star vectors (A+4I)e_v; a naive "
                "symmetric-border or overlapping-block sum must quotient it."
            ),
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "The rank-26 conclusion is conditional on the presence of an all-odd edge type.",
            "The five even-part edge types are not excluded from rank 25 by this package.",
            "The two low-rank controls are local relaxations, not 99-vertex graphs.",
            "The seven-star 49-block route is assessed but not enumerated or closed.",
            "No endpoint exclusion, upper-bound improvement, graph construction, or novelty claim is made.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output", type=Path)
    mode.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = canonical_json(exact_record())
    if args.verify:
        if args.verify.read_bytes() != payload:
            raise SystemExit("stored exact result differs from regeneration")
        print(f"PASS: {args.verify} matches exact regeneration")
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    else:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
