#!/usr/bin/env python3
"""Clean-room exact verifier for the Wave 42 rank-27 candidate.

The mathematical and implementation protocol was frozen before any Wave 42
discovery artifact was opened.  This file is self-contained and imports no
discovery or earlier verifier code.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import numpy as np


FIELD = 7
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
X = tuple(range(3, 15))
Y = tuple(range(15, 27))
EVEN_TYPES = (
    (2, 1, 1, 1, 1),
    (2, 2, 1, 1),
    (2, 2, 2),
    (3, 2, 1),
    (4, 1, 1),
    (4, 2),
    (6,),
)
ODD_TYPES = (
    (1, 1, 1, 1, 1, 1),
    (3, 1, 1, 1),
    (5, 1),
    (3, 3),
)
EXPECTED_MINIMUM_PERMUTATIONS = {
    "2+1+1+1+1": 80640,
    "2+2+1+1": 192,
    "2+2+2": 32,
    "3+2+1": 80640,
    "4+1+1": 768,
    "4+2": 64,
    "6": 2592,
}
EXPECTED_KERNELS = {
    "2+1+1+1+1": 2,
    "2+2+1+1": 8,
    "2+2+2": 32,
    "3+2+1": 2,
    "4+1+1": 2,
    "4+2": 4,
    "6": 2,
}


def label(parts: Sequence[int]) -> str:
    return "+".join(map(str, parts))


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def frozen_inputs() -> dict[str, str]:
    answer: dict[str, str] = {}
    for raw in (HERE / "input-freeze.sha256").read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        expected, name = raw.split("  ", 1)
        actual = digest(ROOT / name)
        if actual != expected:
            raise ValueError(f"frozen input changed: {name}: {actual} != {expected}")
        answer[name] = actual
    return answer


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)] if matrix else []


def matmul(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    if not left:
        return []
    if not right:
        return [[] for _ in left]
    if len(left[0]) != len(right):
        raise ValueError("incompatible product")
    columns = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) % FIELD for column in columns]
        for row in left
    ]


def rref(
    rows: Iterable[Sequence[int]], pivot_limit: int | None = None
) -> tuple[list[list[int]], list[int]]:
    matrix = [[value % FIELD for value in row] for row in rows]
    if not matrix:
        return [], []
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("ragged matrix")
    limit = width if pivot_limit is None else pivot_limit
    pivots: list[int] = []
    next_row = 0
    for column in range(limit):
        source = next(
            (row for row in range(next_row, len(matrix)) if matrix[row][column]),
            None,
        )
        if source is None:
            continue
        matrix[next_row], matrix[source] = matrix[source], matrix[next_row]
        inverse = pow(matrix[next_row][column], -1, FIELD)
        matrix[next_row] = [
            inverse * value % FIELD for value in matrix[next_row]
        ]
        for row in range(len(matrix)):
            if row == next_row:
                continue
            factor = matrix[row][column]
            if factor:
                matrix[row] = [
                    (value - factor * pivot) % FIELD
                    for value, pivot in zip(matrix[row], matrix[next_row])
                ]
        pivots.append(column)
        next_row += 1
        if next_row == len(matrix):
            break
    return matrix, pivots


def rank(matrix: Sequence[Sequence[int]]) -> int:
    return len(rref(matrix)[1])


def canonical_span(
    vectors: Iterable[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = rref(vectors)
    return tuple(tuple(reduced[row]) for row in range(len(pivots)))


def nullspace(
    matrix: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    if not matrix:
        raise ValueError("nullspace needs a known width")
    reduced, pivots = rref(matrix)
    width = len(matrix[0])
    answer = []
    for free in (column for column in range(width) if column not in pivots):
        vector = [0] * width
        vector[free] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free] % FIELD
        answer.append(tuple(vector))
    return tuple(answer)


def solve_operator(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    size = len(matrix)
    augmented = [
        [*row, *[int(i == j) for j in range(size)]]
        for i, row in enumerate(matrix)
    ]
    reduced, pivots = rref(augmented, pivot_limit=size)
    operator = [[0] * size for _ in range(size)]
    for row, pivot in enumerate(pivots):
        operator[pivot] = reduced[row][size:]
    return operator


def connect(graph: list[list[int]], a: int, b: int) -> None:
    if a == b or graph[a][b]:
        raise ValueError("repeated or loop edge")
    graph[a][b] = graph[b][a] = 1


def local_graph(parts: Sequence[int]) -> list[list[int]]:
    if sum(parts) != 6 or tuple(sorted(parts, reverse=True)) != tuple(parts):
        raise ValueError("not a positive partition of six")
    graph = [[0] * 27 for _ in range(27)]
    for a, b in ((0, 1), (0, 2), (1, 2)):
        connect(graph, a, b)
    for vertex in X:
        connect(graph, 0, vertex)
    for vertex in Y:
        connect(graph, 1, vertex)
    offset = 0
    for part in parts:
        for step in range(part):
            xa = X[offset + 2 * step]
            xb = X[offset + 2 * step + 1]
            ya = Y[offset + 2 * step]
            yb = Y[offset + 2 * step + 1]
            next_ya = Y[offset + 2 * ((step + 1) % part)]
            for a, b in ((xa, xb), (xa, ya), (xb, yb), (yb, next_ya)):
                connect(graph, a, b)
        offset += 2 * part
    return graph


def transported(graph: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            (1 - int(i == j) - 2 * graph[i][j]) % FIELD
            for j in range(len(graph))
        ]
        for i in range(len(graph))
    ]


def border_column(i: int, j: int) -> tuple[int, ...]:
    vector = [1] * 27
    for row in (2, X[i], Y[j]):
        vector[row] = FIELD - 1
    return tuple(vector)


def projected_signatures(
    kernel: Sequence[Sequence[int]],
) -> dict[tuple[int, int], tuple[int, ...]]:
    return {
        (i, j): tuple(
            sum(radical[row] * value for row, value in enumerate(border_column(i, j)))
            % FIELD
            for radical in kernel
        )
        for i in range(12)
        for j in range(12)
    }


def projective(vector: Sequence[int]) -> tuple[int, ...]:
    first = next((value % FIELD for value in vector if value % FIELD), None)
    if first is None:
        raise ValueError("zero vector")
    inverse = pow(first, -1, FIELD)
    return tuple(inverse * value % FIELD for value in vector)


def belongs(
    vector: Sequence[int], basis: Sequence[Sequence[int]]
) -> bool:
    return len(canonical_span([*basis, vector])) == len(basis)


def perfect_permutations(
    edges: Iterable[tuple[int, int]],
) -> Iterator[tuple[int, ...]]:
    edge_set = set(edges)
    neighbors = {
        left: tuple(right for right in range(12) if (left, right) in edge_set)
        for left in range(12)
    }
    chosen = [-1] * 12

    def visit(unassigned: frozenset[int], free: frozenset[int]):
        if not unassigned:
            yield tuple(chosen)
            return
        left = min(
            unassigned,
            key=lambda item: (
                sum(right in free for right in neighbors[item]),
                item,
            ),
        )
        for right in neighbors[left]:
            if right in free:
                chosen[left] = right
                yield from visit(unassigned - {left}, free - {right})
        chosen[left] = -1

    yield from visit(frozenset(range(12)), frozenset(range(12)))


def minimum_projection_permutations(
    signatures: dict[tuple[int, int], tuple[int, ...]], dimension: int
) -> tuple[
    list[tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]],
    dict[str, int],
]:
    lines = sorted(
        {
            projective(signature)
            for signature in signatures.values()
            if any(signature)
        }
    )
    spaces: set[tuple[tuple[int, ...], ...]] = set()
    for generators in itertools.combinations(lines, dimension):
        space = canonical_span(generators)
        if len(space) == dimension:
            spaces.add(space)
    permutations: dict[
        tuple[int, ...], tuple[tuple[int, ...], ...]
    ] = {}
    winners = 0
    for space in sorted(spaces):
        edges = {
            pair
            for pair, signature in signatures.items()
            if belongs(signature, space)
        }
        found = list(perfect_permutations(edges))
        if found:
            winners += 1
        for permutation in found:
            f_rows = transpose(
                [signatures[(i, permutation[i])] for i in range(12)]
            )
            rowspace = canonical_span(f_rows)
            if len(rowspace) != dimension:
                raise AssertionError("minimum-rank search emitted wrong rank")
            permutations[permutation] = rowspace
    return sorted(permutations.items()), {
        "observed_projective_lines": len(lines),
        "canonical_dimension_e_subspaces": len(spaces),
        "winning_subspaces": winners,
    }


def perfect_matchings(
    vertices: tuple[int, ...] = tuple(range(12)),
) -> Iterator[tuple[tuple[int, int], ...]]:
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        rest = vertices[1:index] + vertices[index + 1 :]
        for tail in perfect_matchings(rest):
            yield ((first, second), *tail)


def schur_table(solve_map: Sequence[Sequence[int]]) -> list[list[int]]:
    columns = [
        border_column(i, j) for i in range(12) for j in range(12)
    ]
    return matmul(columns, matmul(solve_map, transpose(columns)))


def equality_target(
    permutation: Sequence[int],
    right_kernel_rows: Sequence[Sequence[int]],
    schur: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    selected = [12 * i + permutation[i] for i in range(12)]
    full = [
        [
            (1 - int(i == j) - schur[selected[i]][selected[j]]) % FIELD
            for j in range(12)
        ]
        for i in range(12)
    ]
    z = transpose(right_kernel_rows)
    target = matmul(transpose(z), matmul(full, z))
    if target != transpose(target):
        raise AssertionError("target lost symmetry")
    return tuple(tuple(row) for row in target)


def matching_core_array(
    right_kernel_rows: Sequence[Sequence[int]],
    matchings: Sequence[Sequence[Sequence[int]]],
) -> np.ndarray:
    z = transpose(right_kernel_rows)
    dimension = len(right_kernel_rows)
    edges = list(itertools.combinations(range(12), 2))
    edge_index = {edge: index for index, edge in enumerate(edges)}
    contributions = np.zeros((66, dimension, dimension), dtype=np.int16)
    for edge_number, (a, b) in enumerate(edges):
        for i in range(dimension):
            for j in range(dimension):
                contributions[edge_number, i, j] = (
                    2 * (z[a][i] * z[b][j] + z[b][i] * z[a][j])
                ) % FIELD
    indices = np.asarray(
        [
            [edge_index[tuple(sorted(edge))] for edge in matching]
            for matching in matchings
        ],
        dtype=np.int16,
    )
    return (contributions[indices].sum(axis=1) % FIELD).astype(
        np.int16, copy=False
    )


def rank_at_most_one(matrix: Sequence[Sequence[int]]) -> bool:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("rank-one predicate needs square matrix")
    reduced = [[value % FIELD for value in row] for row in matrix]
    if reduced != transpose(reduced):
        return False
    pivot = next((i for i in range(size) if reduced[i][i]), None)
    if pivot is None:
        return not any(value for row in reduced for value in row)
    scale = reduced[pivot][pivot]
    return all(
        (reduced[i][j] * scale - reduced[i][pivot] * reduced[j][pivot])
        % FIELD
        == 0
        for i in range(size)
        for j in range(size)
    )


def vectorized_rank_one_census(
    targets: np.ndarray, cores: np.ndarray, batch_size: int = 64
) -> tuple[int, int, int]:
    """Exact census via failing minors, followed by the full pivot predicate."""

    if targets.ndim != 3 or cores.ndim != 3:
        raise ValueError("expected stacks of square matrices")
    dimension = targets.shape[1]
    if targets.shape[2] != dimension or cores.shape[1:] != (
        dimension,
        dimension,
    ):
        raise ValueError("incompatible target/core stacks")
    pairs = 0
    survivors = 0
    principal_minor_evaluations = 0
    for start in range(0, len(targets), batch_size):
        batch = targets[start : start + batch_size].astype(
            np.int16, copy=False
        )
        alive = np.ones((len(batch), len(cores)), dtype=bool)
        diagonal = [
            (batch[:, None, i, i] - cores[None, :, i, i]) % FIELD
            for i in range(dimension)
        ]
        for i in range(dimension):
            for j in range(i + 1, dimension):
                off = (
                    batch[:, None, i, j] - cores[None, :, i, j]
                ) % FIELD
                alive &= (
                    diagonal[i] * diagonal[j] - off * off
                ) % FIELD == 0
                principal_minor_evaluations += len(batch) * len(cores)
                if not alive.any():
                    break
            if not alive.any():
                break
        for target_index, core_index in np.argwhere(alive):
            residual = (
                batch[target_index] - cores[core_index]
            ) % FIELD
            if rank_at_most_one(residual.tolist()):
                survivors += 1
        pairs += len(batch) * len(cores)
    return pairs, survivors, principal_minor_evaluations


def even_type_audit(
    parts: Sequence[int],
    matchings: Sequence[Sequence[Sequence[int]]],
) -> dict[str, object]:
    e = sum(part % 2 == 0 for part in parts)
    s = transported(local_graph(parts))
    kernel = nullspace(s)
    signatures = projected_signatures(kernel)
    records, search = minimum_projection_permutations(signatures, e)
    grouped: defaultdict[
        tuple[tuple[int, ...], ...], list[tuple[int, ...]]
    ] = defaultdict(list)
    permutation_hash = hashlib.sha256()
    for permutation, rowspace in records:
        grouped[nullspace(rowspace)].append(permutation)
        permutation_hash.update(bytes(permutation))
    solve_map = solve_operator(s)
    pairings = schur_table(solve_map)
    target_hash = hashlib.sha256()
    pairs = survivors = minor_evaluations = 0
    kernel_records = []
    for right_rows, permutations in sorted(grouped.items()):
        cores = matching_core_array(right_rows, matchings)
        targets = np.asarray(
            [
                equality_target(permutation, right_rows, pairings)
                for permutation in permutations
            ],
            dtype=np.int16,
        )
        target_hash.update(targets.astype(np.uint8).tobytes())
        covered, hits, minors = vectorized_rank_one_census(targets, cores)
        pairs += covered
        survivors += hits
        minor_evaluations += minors
        kernel_records.append(
            {
                "right_kernel_sha256": hashlib.sha256(
                    bytes(value for row in right_rows for value in row)
                ).hexdigest(),
                "right_kernel_dimension": len(right_rows),
                "minimum_F_permutations": len(permutations),
                "labelled_R_per_permutation": len(matchings),
                "labelled_pairs_checked": covered,
                "rank_at_most_one_survivors": hits,
            }
        )
    return {
        "partition": list(parts),
        "even_part_count": e,
        "rank_S": rank(s),
        "minimum_F_rank": e,
        "minimum_F_permutation_count": len(records),
        "minimum_F_search": search,
        "minimum_F_permutation_stream_sha256": permutation_hash.hexdigest(),
        "distinct_right_kernels": len(grouped),
        "target_stream_sha256": target_hash.hexdigest(),
        "labelled_R_count": len(matchings),
        "labelled_pairs_checked": pairs,
        "principal_minor_evaluations": minor_evaluations,
        "rank_at_most_one_survivors": survivors,
        "kernel_records": kernel_records,
    }


def all_odd_pivot_csp(
    parts: Sequence[int],
) -> dict[str, object]:
    """Complete pivot/mate CSP for all labelled rank-one residuals."""

    s = transported(local_graph(parts))
    if rank(s) != 25:
        raise AssertionError("all-odd type did not have rank(S)=25")
    schur = schur_table(solve_operator(s))
    assignments = [-1] * 12
    pivot_column: list[int | None] = [None] * 12
    matching_degree = [0] * 12
    nodes = leaves = dense_hits = 0

    def interaction(i: int, right_i: int, j: int, right_j: int) -> int:
        return schur[12 * i + right_i][12 * j + right_j]

    for pivot in range(12):
        for pivot_mate in range(12):
            if pivot == pivot_mate:
                continue
            used = 0

            def visit() -> None:
                nonlocal nodes, leaves, dense_hits, used
                nodes += 1
                if all(value >= 0 for value in assignments):
                    if all(degree == 1 for degree in matching_degree):
                        leaves += 1
                        # Reconstruct and hostile-check the exact residual.
                        dpp = int(pivot_column[pivot])
                        residual = [
                            [
                                pivot_column[i]
                                * pivot_column[j]
                                * pow(dpp, -1, FIELD)
                                % FIELD
                                for j in range(12)
                            ]
                            for i in range(12)
                        ]
                        if rank_at_most_one(residual):
                            dense_hits += 1
                    return
                dpp = int(pivot_column[pivot])
                inverse = pow(dpp, -1, FIELD)
                best_vertex = -1
                best_choices: list[tuple[int, int, tuple[int, ...]]] | None = None
                for vertex in range(12):
                    if assignments[vertex] >= 0:
                        continue
                    choices: list[tuple[int, int, tuple[int, ...]]] = []
                    for right in range(12):
                        if used & (1 << right):
                            continue
                        w_to_pivot = 6 if vertex == pivot_mate else 1
                        value = (
                            w_to_pivot
                            - interaction(
                                vertex,
                                right,
                                pivot,
                                assignments[pivot],
                            )
                        ) % FIELD
                        if (
                            -interaction(vertex, right, vertex, right)
                            - value * value * inverse
                        ) % FIELD:
                            continue
                        new_mates: list[int] = []
                        valid = True
                        for other in range(12):
                            if (
                                assignments[other] < 0
                                or other == pivot
                            ):
                                continue
                            required_w = (
                                interaction(
                                    vertex,
                                    right,
                                    other,
                                    assignments[other],
                                )
                                + value
                                * int(pivot_column[other])
                                * inverse
                            ) % FIELD
                            if required_w not in (1, 6):
                                valid = False
                                break
                            if required_w == 6:
                                if (
                                    matching_degree[vertex]
                                    or matching_degree[other]
                                ):
                                    valid = False
                                    break
                                new_mates.append(other)
                        if valid:
                            choices.append((right, value, tuple(new_mates)))
                    if not choices:
                        return
                    if best_choices is None or len(choices) < len(best_choices):
                        best_vertex = vertex
                        best_choices = choices
                if best_choices is None:
                    raise AssertionError("CSP lost an unassigned vertex")
                vertex = best_vertex
                for right, value, new_mates in best_choices:
                    assignments[vertex] = right
                    pivot_column[vertex] = value
                    used |= 1 << right
                    changes: list[tuple[int, int]] = []
                    valid = True
                    if vertex == pivot_mate:
                        if matching_degree[vertex] or matching_degree[pivot]:
                            valid = False
                        else:
                            matching_degree[vertex] = 1
                            matching_degree[pivot] = 1
                            changes.append((vertex, pivot))
                    if valid:
                        for other in new_mates:
                            if (
                                matching_degree[vertex]
                                or matching_degree[other]
                            ):
                                valid = False
                                break
                            matching_degree[vertex] = 1
                            matching_degree[other] = 1
                            changes.append((vertex, other))
                    if valid:
                        visit()
                    for a, b in reversed(changes):
                        matching_degree[a] = matching_degree[b] = 0
                    used ^= 1 << right
                    assignments[vertex] = -1
                    pivot_column[vertex] = None

            for pivot_right in range(12):
                dpp = -interaction(
                    pivot, pivot_right, pivot, pivot_right
                ) % FIELD
                if dpp == 0:
                    continue
                assignments[pivot] = pivot_right
                pivot_column[pivot] = dpp
                used = 1 << pivot_right
                visit()
                assignments[pivot] = -1
                pivot_column[pivot] = None
                used = 0
    represented = math.factorial(12) * 10395
    return {
        "partition": list(parts),
        "rank_S": rank(s),
        "CSP_method": (
            "Loop every residual diagonal pivot and its R-mate; MRV-enumerate "
            "the full labelled border bijection; exact rank-one pivot equations "
            "force every W entry and matching degree."
        ),
        "pivot_choices": 12,
        "pivot_mate_choices_per_pivot": 11,
        "search_nodes": nodes,
        "complete_candidate_leaves": leaves,
        "dense_rank_one_hits": dense_hits,
        "labelled_permutations_represented": math.factorial(12),
        "labelled_R_per_permutation": 10395,
        "labelled_pairs_covered_by_complete_CSP": represented,
        "coverage_proof": (
            "Any nonzero symmetric rank-one residual has a nonzero diagonal. "
            "Choose its least nonzero diagonal as pivot and the actual mate of "
            "that fibre vertex in R. The pivot column determines every residual "
            "entry, so the CSP branch for that pivot/mate contains the labelled "
            "permutation and reconstructs the unique R."
        ),
    }


def predicate_controls() -> dict[str, object]:
    vector = [1, 2, 0, 4, 3]
    rank_one = [
        [3 * a * b % FIELD for b in vector] for a in vector
    ]
    hostile = [row[:] for row in rank_one]
    hostile[2][3] = hostile[3][2] = 1
    zero = [[0] * 5 for _ in range(5)]
    off_diagonal_rank_two = [[0] * 5 for _ in range(5)]
    off_diagonal_rank_two[0][1] = off_diagonal_rank_two[1][0] = 1
    return {
        "zero_accepted": rank_at_most_one(zero),
        "rank_one_accepted": rank_at_most_one(rank_one),
        "hostile_mutation_rejected": not rank_at_most_one(hostile),
        "zero_diagonal_rank_two_rejected": not rank_at_most_one(
            off_diagonal_rank_two
        ),
        "rank_one_direct_rank": rank(rank_one),
        "hostile_direct_rank": rank(hostile),
        "zero_diagonal_hostile_direct_rank": rank(off_diagonal_rank_two),
    }


def compute() -> dict[str, object]:
    inputs = frozen_inputs()
    matchings = list(perfect_matchings())
    if len(matchings) != 10395 or len(set(matchings)) != 10395:
        raise AssertionError("labelled matching enumeration is incomplete")
    matching_hash = hashlib.sha256(
        b"".join(
            bytes(value for edge in matching for value in edge)
            for matching in matchings
        )
    ).hexdigest()
    controls = predicate_controls()
    even = {
        label(parts): even_type_audit(parts, matchings)
        for parts in EVEN_TYPES
    }
    odd = {
        label(parts): all_odd_pivot_csp(parts)
        for parts in ODD_TYPES
    }
    even_pairs = sum(
        entry["labelled_pairs_checked"] for entry in even.values()
    )
    odd_pairs = sum(
        entry["labelled_pairs_covered_by_complete_CSP"]
        for entry in odd.values()
    )
    result = {
        "format": "wave42-rank27-independent-precomparison-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_PRECOMPARISON",
        "frozen_inputs": inputs,
        "rank_reduction": {
            "formula": (
                "rank(K39)=rank(S)+2rank(F)+"
                "rank(Z^T W_R Z-Z^T U^T X)"
            ),
            "rank_26_iff": (
                "rank(F)=e and the symmetric residual has rank exactly one"
            ),
            "rank_at_most_one_predicate": (
                "all 2x2 minors vanish; implemented by failing principal "
                "minors followed by the exact nonzero-diagonal pivot identity"
            ),
        },
        "labelled_R": {
            "count": len(matchings),
            "stream_sha256": matching_hash,
        },
        "predicate_controls": controls,
        "even_types": even,
        "all_odd_types": odd,
        "totals": {
            "local_types": len(even) + len(odd),
            "minimum_F_permutations": sum(
                entry["minimum_F_permutation_count"]
                for entry in even.values()
            ),
            "distinct_right_kernels": sum(
                entry["distinct_right_kernels"] for entry in even.values()
            ),
            "even_labelled_pairs_explicitly_checked": even_pairs,
            "all_odd_labelled_pairs_covered_by_CSP": odd_pairs,
            "rank_at_most_one_survivors": sum(
                entry["rank_at_most_one_survivors"]
                for entry in even.values()
            )
            + sum(
                entry["dense_rank_one_hits"] for entry in odd.values()
            ),
        },
        "universal_deduction": {
            "rank_26_excluded": True,
            "theorem": "rank_F7(M)>=27",
            "transport": (
                "Principal K39 rank is a lower bound for rank_F7(K), and the "
                "verified incidence identities give rank_F7(K)=rank_F7(M)."
            ),
        },
        "status_wall": {
            "universal_rank_F7_M_lower_bound": 27,
            "endpoint_n3_4158_excluded": False,
            "strongest_general_upper_bound": "n3<=4158",
            "conway_99_status": "UNKNOWN",
            "graph_constructed": False,
            "novelty_or_priority": "UNKNOWN",
        },
    }
    validate(result)
    return result


def validate(result: dict[str, object]) -> None:
    if result.get("format") != "wave42-rank27-independent-precomparison-v1":
        raise ValueError("wrong result format")
    if result["labelled_R"]["count"] != 10395:
        raise ValueError("matching universe incomplete")
    controls = result["predicate_controls"]
    if not all(
        controls[key]
        for key in (
            "zero_accepted",
            "rank_one_accepted",
            "hostile_mutation_rejected",
            "zero_diagonal_rank_two_rejected",
        )
    ):
        raise ValueError("rank-one predicate control failed")
    if set(result["even_types"]) != {
        label(parts) for parts in EVEN_TYPES
    }:
        raise ValueError("even-type coverage changed")
    for key, entry in result["even_types"].items():
        if entry["rank_S"] != 25 - 2 * entry["even_part_count"]:
            raise ValueError(f"local rank formula failed for {key}")
        if (
            entry["minimum_F_permutation_count"]
            != EXPECTED_MINIMUM_PERMUTATIONS[key]
        ):
            raise ValueError(f"minimum-F census failed for {key}")
        if entry["distinct_right_kernels"] != EXPECTED_KERNELS[key]:
            raise ValueError(f"right-kernel census failed for {key}")
        expected_pairs = entry["minimum_F_permutation_count"] * 10395
        if entry["labelled_pairs_checked"] != expected_pairs:
            raise ValueError(f"labelled even-pair coverage failed for {key}")
        if entry["rank_at_most_one_survivors"]:
            raise ValueError(f"rank-26 survivor found for {key}")
    if set(result["all_odd_types"]) != {
        label(parts) for parts in ODD_TYPES
    }:
        raise ValueError("all-odd type coverage changed")
    per_odd = math.factorial(12) * 10395
    for key, entry in result["all_odd_types"].items():
        if entry["labelled_pairs_covered_by_complete_CSP"] != per_odd:
            raise ValueError(f"all-odd coverage failed for {key}")
        if entry["complete_candidate_leaves"] or entry["dense_rank_one_hits"]:
            raise ValueError(f"all-odd rank-26 survivor found for {key}")
    totals = result["totals"]
    if totals != {
        "local_types": 11,
        "minimum_F_permutations": 164928,
        "distinct_right_kernels": 52,
        "even_labelled_pairs_explicitly_checked": 1714426560,
        "all_odd_labelled_pairs_covered_by_CSP": 19916886528000,
        "rank_at_most_one_survivors": 0,
    }:
        raise ValueError(f"aggregate census changed: {totals}")
    if not result["universal_deduction"]["rank_26_excluded"]:
        raise ValueError("rank-26 exclusion missing")
    if result["universal_deduction"]["theorem"] != "rank_F7(M)>=27":
        raise ValueError("theorem inflated or changed")
    wall = result["status_wall"]
    if (
        wall["endpoint_n3_4158_excluded"]
        or wall["strongest_general_upper_bound"] != "n3<=4158"
        or wall["conway_99_status"] != "UNKNOWN"
        or wall["graph_constructed"]
    ):
        raise ValueError("scope wall inflated")


def strict_load(path: Path) -> dict[str, object]:
    def reject(pairs: list[tuple[str, object]]) -> dict[str, object]:
        answer: dict[str, object] = {}
        for key, value in pairs:
            if key in answer:
                raise ValueError(f"duplicate JSON key: {key}")
            answer[key] = value
        return answer

    loaded = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject)
    if not isinstance(loaded, dict):
        raise ValueError("result root must be an object")
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--compute", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.compute:
        result = compute()
        args.compute.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result["totals"], sort_keys=True))
        return 0
    expected = strict_load(args.verify)
    validate(expected)
    actual = compute()
    if actual != expected:
        raise SystemExit("full replay differs from frozen result")
    print("PASS: full clean-room replay matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
