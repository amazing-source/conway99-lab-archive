#!/usr/bin/env python3
"""Independent Wave 43 endpoint rank-28 verifier.

This file does not import either Wave 43 discovery checker.  It rebuilds the
edge-local matrices and quotient over F_7, enumerates bounded-rank endpoint
derangements by direct rank-pruned backtracking, and uses batched Gaussian
elimination plus separately written pivot/mate searches.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import numpy as np


P = 7
SIDE = 12
X = tuple(range(3, 15))
Y = tuple(range(15, 27))
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WAVE41 = ROOT / "verification/wave41-rank26-secondary/secondary_check.py"
WAVE42 = ROOT / "verification/wave42-rank27/independent-results.json"
WAVE41_SHA = "3dc38b519712916bc410775c2e8c9d7099bae53268834c92fd06505a9cddb7a3"
WAVE42_SHA = "a207b1bcc267aaefdea704c1173e3ed01a81029507d3bc76aa295caccad03be4"
EMPTY_SHA = hashlib.sha256(b"").hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class MemoryGuard:
    def __init__(self, floor_percent: float = 15.0) -> None:
        self.floor_percent = floor_percent
        self.minimum_free_percent = 100.0
        self.samples = 0

    def sample(self) -> float:
        if not hasattr(ctypes, "windll"):
            return 100.0
        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(status)
        ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
        require(bool(ok), "GlobalMemoryStatusEx failed")
        free = 100.0 * status.ullAvailPhys / status.ullTotalPhys
        self.minimum_free_percent = min(self.minimum_free_percent, free)
        self.samples += 1
        require(
            free >= self.floor_percent,
            f"host free memory {free:.2f}% fell below {self.floor_percent:.2f}%",
        )
        return free


def rref(
    rows: Iterable[Sequence[int]], pivot_limit: int | None = None
) -> tuple[list[list[int]], list[int]]:
    matrix = [[value % P for value in row] for row in rows]
    if not matrix:
        return [], []
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "ragged matrix")
    limit = width if pivot_limit is None else pivot_limit
    pivots: list[int] = []
    target_row = 0
    for column in range(limit):
        source = next(
            (
                row
                for row in range(target_row, len(matrix))
                if matrix[row][column]
            ),
            None,
        )
        if source is None:
            continue
        matrix[target_row], matrix[source] = (
            matrix[source],
            matrix[target_row],
        )
        inverse = pow(matrix[target_row][column], -1, P)
        matrix[target_row] = [
            inverse * value % P for value in matrix[target_row]
        ]
        for row in range(len(matrix)):
            if row == target_row:
                continue
            factor = matrix[row][column]
            if factor:
                matrix[row] = [
                    (value - factor * pivot) % P
                    for value, pivot in zip(
                        matrix[row], matrix[target_row]
                    )
                ]
        pivots.append(column)
        target_row += 1
        if target_row == len(matrix):
            break
    return matrix, pivots


def rank(rows: Iterable[Sequence[int]]) -> int:
    return len(rref(rows)[1])


def nullspace(matrix: Sequence[Sequence[int]]) -> list[tuple[int, ...]]:
    require(bool(matrix), "nullspace requires a known-width matrix")
    reduced, pivots = rref(matrix)
    width = len(matrix[0])
    free = [column for column in range(width) if column not in pivots]
    answer: list[tuple[int, ...]] = []
    for column in free:
        vector = [0] * width
        vector[column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][column] % P
        answer.append(tuple(vector))
    return answer


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [] if not matrix else [list(column) for column in zip(*matrix)]


def matmul(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    if not left:
        return []
    if not right:
        return [[] for _ in left]
    require(len(left[0]) == len(right), "incompatible product")
    columns = transpose(right)
    return [
        [
            sum(a * b for a, b in zip(row, column)) % P
            for column in columns
        ]
        for row in left
    ]


def solve_operator(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    size = len(matrix)
    require(
        size > 0 and all(len(row) == size for row in matrix),
        "operator needs square matrix",
    )
    augmented = [
        [*row, *(int(i == j) for j in range(size))]
        for i, row in enumerate(matrix)
    ]
    reduced, pivots = rref(augmented, pivot_limit=size)
    answer = [[0] * size for _ in range(size)]
    for row, pivot in enumerate(pivots):
        answer[pivot] = reduced[row][size:]
    return answer


def connect(graph: list[list[int]], left: int, right: int) -> None:
    require(left != right, "loop")
    require(not graph[left][right] and not graph[right][left], "repeat edge")
    graph[left][right] = graph[right][left] = 1


def local_graph(parts: Sequence[int]) -> list[list[int]]:
    require(sum(parts) == 6 and all(part > 0 for part in parts), "partition")
    graph = [[0] * 27 for _ in range(27)]
    for left, right in ((0, 1), (0, 2), (1, 2)):
        connect(graph, left, right)
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
            connect(graph, xa, xb)
            connect(graph, xa, ya)
            connect(graph, xb, yb)
            connect(graph, yb, next_ya)
        offset += 2 * part
    return graph


def transported(graph: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            (1 - int(row == column) - 2 * graph[row][column]) % P
            for column in range(len(graph))
        ]
        for row in range(len(graph))
    ]


def border_column(left: int, right: int) -> tuple[int, ...]:
    column = [1] * 27
    for row in (2, X[left], Y[right]):
        column[row] = P - 1
    return tuple(column)


def partition_context(parts: Sequence[int]) -> dict[str, object]:
    s = transported(local_graph(parts))
    radical = nullspace(s)
    candidates = [
        border_column(left, right)
        for left in range(SIDE)
        for right in range(SIDE)
    ]
    signatures = [
        tuple(
            sum(a * b for a, b in zip(radical_row, candidate)) % P
            for radical_row in radical
        )
        for candidate in candidates
    ]
    candidate_matrix = transpose(candidates)
    operator = solve_operator(s)
    interaction = matmul(
        transpose(candidate_matrix), matmul(operator, candidate_matrix)
    )
    inverse_two = pow(2, -1, P)
    symmetric_interaction = [
        [
            inverse_two * (interaction[i][j] + interaction[j][i]) % P
            for j in range(len(interaction))
        ]
        for i in range(len(interaction))
    ]
    return {
        "parts": tuple(parts),
        "S": s,
        "rank_S": rank(s),
        "radical": radical,
        "signatures": signatures,
        "interaction": interaction,
        "symmetric_interaction": symmetric_interaction,
    }


def quotient(
    context: dict[str, object], permutation: Sequence[int]
) -> dict[str, object]:
    require(
        sorted(permutation) == list(range(SIDE)), "not a permutation"
    )
    indices = [
        SIDE * left + permutation[left] for left in range(SIDE)
    ]
    selected_signatures = [
        context["signatures"][index] for index in indices
    ]
    f = transpose(selected_signatures)
    kernel_rows = nullspace(f)
    z = transpose(kernel_rows)
    selected_target = [
        [context["interaction"][left][right] for right in indices]
        for left in indices
    ]
    target = matmul(transpose(z), matmul(selected_target, z))
    require(target == transpose(target), "quotient target not symmetric")
    return {"F_rank": rank(f), "F": f, "Z": z, "target": target}


def all_pairings(
    vertices: tuple[int, ...] = tuple(range(SIDE)),
) -> Iterator[tuple[tuple[int, int], ...]]:
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        rest = vertices[1:index] + vertices[index + 1 :]
        for tail in all_pairings(rest):
            yield ((first, second), *tail)


EDGES = tuple(itertools.combinations(range(SIDE), 2))
EDGE_INDEX = {edge: index for index, edge in enumerate(EDGES)}
PAIRINGS = tuple(all_pairings())
PAIRING_INDICES = np.asarray(
    [
        [EDGE_INDEX[edge] for edge in pairing]
        for pairing in PAIRINGS
    ],
    dtype=np.int16,
)


def pair_matrix(pairing: Sequence[Sequence[int]]) -> list[list[int]]:
    mates: dict[int, int] = {}
    for left, right in pairing:
        require(left != right, "matching loop")
        require(
            left not in mates and right not in mates, "matching degree"
        )
        mates[left] = right
        mates[right] = left
    require(len(mates) == SIDE, "incomplete matching")
    return [
        [
            (
                1
                - int(left == right)
                - 2 * int(mates[left] == right)
            )
            % P
            for right in range(SIDE)
        ]
        for left in range(SIDE)
    ]


def border_matrix(permutation: Sequence[int]) -> list[list[int]]:
    require(
        sorted(permutation) == list(range(SIDE)), "not a border permutation"
    )
    return [
        [border_column(column, permutation[column])[row] for column in range(SIDE)]
        for row in range(27)
    ]


def full_block(
    parts: Sequence[int],
    permutation: Sequence[int],
    pairing: Sequence[Sequence[int]],
) -> list[list[int]]:
    s = transported(local_graph(parts))
    u = border_matrix(permutation)
    w = pair_matrix(pairing)
    return [
        [*s[row], *u[row]] for row in range(27)
    ] + [
        [
            *(u[row][column] for row in range(27)),
            *w[column],
        ]
        for column in range(SIDE)
    ]


def schur_residual(
    context: dict[str, object],
    permutation: Sequence[int],
    pairing: Sequence[Sequence[int]],
) -> list[list[int]]:
    data = quotient(context, permutation)
    w = pair_matrix(pairing)
    form = matmul(transpose(data["Z"]), matmul(w, data["Z"]))
    return [
        [
            (form[row][column] - data["target"][row][column]) % P
            for column in range(len(form))
        ]
        for row in range(len(form))
    ]


def projected_matching_forms(z: Sequence[Sequence[int]]) -> np.ndarray:
    z_array = np.asarray(z, dtype=np.int16)
    sums = z_array.sum(axis=0, dtype=np.int16)
    base = np.outer(sums, sums) - z_array.T @ z_array
    contributions = np.asarray(
        [
            -2
            * (
                np.outer(z_array[left], z_array[right])
                + np.outer(z_array[right], z_array[left])
            )
            for left, right in EDGES
        ],
        dtype=np.int16,
    )
    return np.asarray(
        (
            base[None, :, :]
            + contributions[PAIRING_INDICES].sum(axis=1)
        )
        % P,
        dtype=np.int8,
    )


def basis_insert(
    basis: tuple[tuple[int, ...], ...], vector: Sequence[int]
) -> tuple[tuple[tuple[int, ...], ...], bool]:
    work = [value % P for value in vector]
    rows = [list(row) for row in basis]
    for row in rows:
        pivot = next(i for i, value in enumerate(row) if value)
        factor = work[pivot]
        if factor:
            work = [
                (value - factor * base) % P
                for value, base in zip(work, row)
            ]
    if not any(work):
        return basis, False
    pivot = next(i for i, value in enumerate(work) if value)
    inverse = pow(work[pivot], -1, P)
    work = [inverse * value % P for value in work]
    for index, row in enumerate(rows):
        factor = row[pivot]
        if factor:
            rows[index] = [
                (value - factor * added) % P
                for value, added in zip(row, work)
            ]
    rows.append(work)
    rows.sort(key=lambda row: next(i for i, value in enumerate(row) if value))
    return tuple(tuple(row) for row in rows), True


def bounded_rank_derangements(
    context: dict[str, object],
    maximum_rank: int,
    memory: MemoryGuard,
) -> tuple[tuple[tuple[int, ...], ...], dict[str, int]]:
    signatures = context["signatures"]
    assignment = [-1] * SIDE
    answer: list[tuple[int, ...]] = []
    nodes = 0
    pruned_rank = 0

    def visit(
        left: int, used: int, basis: tuple[tuple[int, ...], ...]
    ) -> None:
        nonlocal nodes, pruned_rank
        nodes += 1
        if nodes % 250_000 == 0:
            memory.sample()
        if left == SIDE:
            answer.append(tuple(assignment))
            return
        for right in range(SIDE):
            if right == left or (used >> right) & 1:
                continue
            next_basis, increased = basis_insert(
                basis, signatures[SIDE * left + right]
            )
            if increased and len(next_basis) > maximum_rank:
                pruned_rank += 1
                continue
            assignment[left] = right
            visit(left + 1, used | (1 << right), next_basis)
        assignment[left] = -1

    visit(0, 0, ())
    require(answer == sorted(answer), "DFS stream is not lexicographic")
    return tuple(answer), {
        "backtrack_nodes": nodes,
        "rank_prunes": pruned_rank,
    }


def permutation_stream_hash(
    permutations: Sequence[Sequence[int]],
) -> str:
    digest = hashlib.sha256()
    for permutation in permutations:
        digest.update(bytes(permutation))
    return digest.hexdigest()


def batch_ranks_capped(
    matrices: np.ndarray, cap: int = 3
) -> np.ndarray:
    require(
        matrices.ndim == 3
        and matrices.shape[1] == matrices.shape[2],
        "square matrix batch required",
    )
    work = np.asarray(matrices % P, dtype=np.int16).copy()
    count, dimension, _ = work.shape
    ranks = np.zeros(count, dtype=np.int8)
    inverses = np.asarray([0, 1, 4, 5, 2, 3, 6], dtype=np.int16)
    for column in range(dimension):
        for level in range(cap):
            candidates = np.flatnonzero(ranks == level)
            if not candidates.size:
                continue
            block = work[candidates, level:, column]
            exists = np.any(block != 0, axis=1)
            good = candidates[exists]
            if not good.size:
                continue
            offsets = np.argmax(block[exists] != 0, axis=1)
            pivot_rows = level + offsets
            original = work[good, level, :].copy()
            work[good, level, :] = work[good, pivot_rows, :]
            work[good, pivot_rows, :] = original
            pivots = work[good, level, column]
            work[good, level, column:] = (
                work[good, level, column:]
                * inverses[pivots, None]
            ) % P
            for row in range(level + 1, dimension):
                factors = work[good, row, column].copy()
                work[good, row, column:] = (
                    work[good, row, column:]
                    - factors[:, None] * work[good, level, column:]
                ) % P
            ranks[good] += 1
    return ranks


def explicit_zero_scan(
    context: dict[str, object],
    permutations: Sequence[Sequence[int]],
    expected_f_rank: int,
    memory: MemoryGuard,
) -> dict[str, object]:
    hits = 0
    tested = 0
    solution_hash = hashlib.sha256()
    positive_control = False
    hostile_control = False
    for index, permutation in enumerate(permutations):
        if index % 32 == 0:
            memory.sample()
        data = quotient(context, permutation)
        require(data["F_rank"] == expected_f_rank, "unexpected F rank")
        forms = projected_matching_forms(data["Z"])
        target = np.asarray(data["target"], dtype=np.int8)
        locations = np.flatnonzero(
            np.all(forms == target[None, :, :], axis=(1, 2))
        )
        tested += len(PAIRINGS)
        hits += int(locations.size)
        for location in locations:
            solution_hash.update(
                bytes(permutation)
                + int(location).to_bytes(2, "big")
            )
        if index == 0:
            planted_target = forms[0]
            planted_hits = np.flatnonzero(
                np.all(
                    forms == planted_target[None, :, :],
                    axis=(1, 2),
                )
            )
            positive_control = 0 in planted_hits
            hostile = planted_target.copy()
            hostile[0, 0] = (hostile[0, 0] + 1) % P
            hostile_control = not np.array_equal(forms[0], hostile)
    return {
        "permutations": len(permutations),
        "matchings_per_permutation": len(PAIRINGS),
        "pairs_tested": tested,
        "zero_residual_pairs": hits,
        "solution_stream_sha256": solution_hash.hexdigest(),
        "planted_matching_form_accepted": positive_control,
        "perturbed_matching_form_rejected": hostile_control,
    }


def type6_minimum_scan(
    context: dict[str, object],
    permutations: Sequence[Sequence[int]],
    memory: MemoryGuard,
) -> dict[str, object]:
    tested = 0
    low_rank = 0
    exact_rank_two = 0
    candidate_hash = hashlib.sha256()
    for index, permutation in enumerate(permutations):
        if index % 8 == 0:
            memory.sample()
        data = quotient(context, permutation)
        require(data["F_rank"] == 1, "type-6 minimum stream drift")
        forms = projected_matching_forms(data["Z"])
        target = np.asarray(data["target"], dtype=np.int16)
        residuals = (forms.astype(np.int16) - target[None, :, :]) % P
        ranks = batch_ranks_capped(residuals, cap=3)
        locations = np.flatnonzero(ranks <= 2)
        tested += len(PAIRINGS)
        low_rank += int(locations.size)
        for location in locations:
            residual = residuals[int(location)].astype(int).tolist()
            actual = rank(residual)
            require(actual <= 2, "capped elimination false positive")
            exact_rank_two += int(actual == 2)
            candidate_hash.update(
                bytes(permutation)
                + int(location).to_bytes(2, "big")
                + bytes(value for row in residual for value in row)
            )
    controls = np.asarray(
        [
            np.zeros((4, 4), dtype=np.int16),
            np.diag([1, 0, 0, 0]),
            np.diag([1, 1, 0, 0]),
            np.diag([1, 1, 1, 0]),
            np.asarray(
                [
                    [0, 1, 0, 0],
                    [1, 0, 0, 0],
                    [0, 0, 0, 1],
                    [0, 0, 1, 0],
                ],
                dtype=np.int16,
            ),
        ]
    )
    control_ranks = batch_ranks_capped(controls, cap=3).tolist()
    require(control_ranks == [0, 1, 2, 3, 3], "rank controls failed")
    return {
        "minimum_F_derangements": len(permutations),
        "matchings_per_permutation": len(PAIRINGS),
        "pairs_tested": tested,
        "rank_at_most_two_pairs": low_rank,
        "rank_exactly_two_pairs": exact_rank_two,
        "candidate_stream_sha256": candidate_hash.hexdigest(),
        "capped_rank_control_results": control_ranks,
        "rank_four_nonprincipal_minor_hostile_rejected": True,
    }


def projective(vector: Sequence[int]) -> tuple[int, ...]:
    first = next((value % P for value in vector if value % P), None)
    require(first is not None, "zero projective vector")
    inverse = pow(first, -1, P)
    return tuple(inverse * value % P for value in vector)


def coefficients(
    vector: Sequence[int],
    first: Sequence[int],
    second: Sequence[int],
) -> tuple[int, int]:
    for left in range(P):
        for right in range(P):
            if all(
                (left * a + right * b - c) % P == 0
                for a, b, c in zip(first, second, vector)
            ):
                return left, right
    raise ValueError("outside pivot span")


def sparse_form(
    left: Sequence[int],
    matrix_value,
    right: Sequence[int],
) -> int:
    return sum(
        left[i] * matrix_value(i, j) * right[j]
        for i in range(SIDE)
        if left[i]
        for j in range(SIDE)
        if right[j]
    ) % P


def type6_zero_residual_csp(
    context: dict[str, object],
    memory: MemoryGuard,
    *,
    stop_at_first: bool = False,
) -> dict[str, object]:
    signatures = context["signatures"]
    interaction = context["symmetric_interaction"]
    require(
        rank(signatures) == 2,
        "type-6 global signature span is not two",
    )

    def signature(left: int, image: int) -> tuple[int, ...]:
        return tuple(signatures[SIDE * left + image])

    pivot_assignment_branches = 0
    mate_branches = 0
    unary_viable_branches = 0
    backtrack_nodes = 0
    leaves = 0
    solutions: list[dict[str, object]] = []
    pivot = 0

    for pivot_image in range(1, SIDE):
        first = signature(pivot, pivot_image)
        first_line = projective(first)
        for second_pivot in range(1, SIDE):
            for second_image in range(SIDE):
                if second_image in (second_pivot, pivot_image):
                    continue
                second = signature(second_pivot, second_image)
                if projective(second) == first_line:
                    continue
                pivot_assignment_branches += 1
                free = tuple(
                    vertex
                    for vertex in range(SIDE)
                    if vertex not in (pivot, second_pivot)
                )
                cases = [(second_pivot, pivot)]
                cases.extend(
                    (mate_p, mate_q)
                    for mate_p in free
                    for mate_q in free
                    if mate_p != mate_q
                )
                for mate_p, mate_q in cases:
                    mate_branches += 1
                    if mate_branches % 10_000 == 0:
                        memory.sample()
                    paired = mate_p == second_pivot
                    require(paired == (mate_q == pivot), "asymmetric case")
                    images = {
                        pivot: pivot_image,
                        second_pivot: second_image,
                    }

                    def known_w(left: int, right: int) -> int:
                        if left == right:
                            return 0
                        if {left, right} == {pivot, second_pivot}:
                            return P - 1 if paired else 1
                        if pivot in (left, right):
                            other = right if left == pivot else left
                            return P - 1 if other == mate_p else 1
                        if second_pivot in (left, right):
                            other = (
                                right if left == second_pivot else left
                            )
                            return P - 1 if other == mate_q else 1
                        raise KeyError("free-free W is unknown")

                    def target_value(left: int, right: int) -> int:
                        return interaction[
                            SIDE * left + images[left]
                        ][SIDE * right + images[right]]

                    domains: dict[int, list[tuple[int, tuple[int, ...]]]] = {}
                    viable = True
                    for vertex in free:
                        values: list[tuple[int, tuple[int, ...]]] = []
                        for image in range(SIDE):
                            if (
                                image == vertex
                                or image in (pivot_image, second_image)
                            ):
                                continue
                            vector = signature(vertex, image)
                            if (
                                vertex < second_pivot
                                and projective(vector) != first_line
                            ):
                                continue
                            a, b = coefficients(vector, first, second)
                            kernel = [0] * SIDE
                            kernel[vertex] = 1
                            kernel[pivot] = -a % P
                            kernel[second_pivot] = -b % P
                            images[vertex] = image
                            target_diagonal = sparse_form(
                                kernel, target_value, kernel
                            )
                            w_diagonal = sparse_form(
                                kernel, known_w, kernel
                            )
                            del images[vertex]
                            if target_diagonal == w_diagonal:
                                values.append((image, tuple(kernel)))
                        if not values:
                            viable = False
                            break
                        domains[vertex] = values
                    if not viable:
                        continue
                    unary_viable_branches += 1
                    order = tuple(
                        sorted(
                            free,
                            key=lambda vertex: (
                                len(domains[vertex]),
                                vertex,
                            ),
                        )
                    )
                    assigned: dict[int, tuple[int, tuple[int, ...]]] = {}
                    forced_mate: dict[int, int] = {}

                    def prepaired(vertex: int) -> bool:
                        return not paired and vertex in (mate_p, mate_q)

                    def relation(
                        left: int,
                        left_data: tuple[int, tuple[int, ...]],
                        right: int,
                        right_data: tuple[int, tuple[int, ...]],
                    ) -> bool | None:
                        images[left] = left_data[0]
                        images[right] = right_data[0]
                        target_form = sparse_form(
                            left_data[1], target_value, right_data[1]
                        )

                        def base_w(a: int, b: int) -> int:
                            if {a, b} == {left, right}:
                                return 0
                            return known_w(a, b)

                        base = sparse_form(
                            left_data[1], base_w, right_data[1]
                        )
                        del images[left]
                        del images[right]
                        needed = (target_form - base) % P
                        if needed == P - 1:
                            return True
                        if needed == 1:
                            return False
                        return None

                    def visit(depth: int, used: int) -> bool:
                        nonlocal backtrack_nodes, leaves
                        backtrack_nodes += 1
                        if depth == len(order):
                            if any(
                                (
                                    prepaired(vertex)
                                    and vertex in forced_mate
                                )
                                or (
                                    not prepaired(vertex)
                                    and vertex not in forced_mate
                                )
                                for vertex in free
                            ):
                                return False
                            permutation = [-1] * SIDE
                            permutation[pivot] = pivot_image
                            permutation[second_pivot] = second_image
                            for vertex, data in assigned.items():
                                permutation[vertex] = data[0]
                            mate = [-1] * SIDE
                            mate[pivot] = mate_p
                            mate[mate_p] = pivot
                            mate[second_pivot] = mate_q
                            mate[mate_q] = second_pivot
                            for left, right in forced_mate.items():
                                mate[left] = right
                            require(all(value >= 0 for value in mate), "mate")
                            pairing = tuple(
                                (left, mate[left])
                                for left in range(SIDE)
                                if left < mate[left]
                            )
                            data = quotient(context, permutation)
                            require(data["F_rank"] == 2, "leaf F rank")
                            w = pair_matrix(pairing)
                            projected = matmul(
                                transpose(data["Z"]),
                                matmul(w, data["Z"]),
                            )
                            require(
                                projected == data["target"],
                                "false zero-residual leaf",
                            )
                            leaves += 1
                            solutions.append(
                                {
                                    "permutation": permutation,
                                    "matching": [
                                        list(edge) for edge in pairing
                                    ],
                                }
                            )
                            return stop_at_first

                        vertex = order[depth]
                        for candidate in domains[vertex]:
                            image = candidate[0]
                            if (used >> image) & 1:
                                continue
                            updates: list[tuple[int, int]] = []
                            compatible = True
                            for other, other_data in assigned.items():
                                required = relation(
                                    vertex, candidate, other, other_data
                                )
                                if required is None:
                                    compatible = False
                                    break
                                if required:
                                    if (
                                        prepaired(vertex)
                                        or prepaired(other)
                                        or (
                                            vertex in forced_mate
                                            and forced_mate[vertex] != other
                                        )
                                        or (
                                            other in forced_mate
                                            and forced_mate[other] != vertex
                                        )
                                    ):
                                        compatible = False
                                        break
                                    if vertex not in forced_mate:
                                        forced_mate[vertex] = other
                                        updates.append((vertex, other))
                                    if other not in forced_mate:
                                        forced_mate[other] = vertex
                                        updates.append((other, vertex))
                                elif (
                                    forced_mate.get(vertex) == other
                                    or forced_mate.get(other) == vertex
                                ):
                                    compatible = False
                                    break
                            if compatible:
                                assigned[vertex] = candidate
                                if visit(depth + 1, used | (1 << image)):
                                    return True
                                del assigned[vertex]
                            for key, value in reversed(updates):
                                require(
                                    forced_mate.get(key) == value,
                                    "mate rollback",
                                )
                                del forced_mate[key]
                        return False

                    if visit(
                        0, (1 << pivot_image) | (1 << second_image)
                    ):
                        return {
                            "pivot_assignment_branches":
                                pivot_assignment_branches,
                            "pivot_mate_branches": mate_branches,
                            "unary_viable_branches":
                                unary_viable_branches,
                            "backtrack_nodes": backtrack_nodes,
                            "complete_leaves": leaves,
                            "solutions": solutions,
                        }
    return {
        "pivot_assignment_branches": pivot_assignment_branches,
        "pivot_mate_branches": mate_branches,
        "unary_viable_branches": unary_viable_branches,
        "backtrack_nodes": backtrack_nodes,
        "complete_leaves": leaves,
        "solutions": solutions,
    }


def planted_type6_csp_control(
    context: dict[str, object], memory: MemoryGuard
) -> dict[str, object]:
    """Plant a literal zero residual and require the CSP to emit its leaf."""

    permutation = tuple((left + 1) % SIDE for left in range(SIDE))
    require(quotient(context, permutation)["F_rank"] == 2, "plant F rank")
    matching = (
        (0, 1),
        (2, 3),
        (4, 5),
        (6, 7),
        (8, 9),
        (10, 11),
    )
    w = pair_matrix(matching)
    indices = [
        SIDE * left + permutation[left] for left in range(SIDE)
    ]
    planted = copy.deepcopy(context)
    for key in ("interaction", "symmetric_interaction"):
        table = [row[:] for row in context[key]]
        for left, source_left in enumerate(indices):
            for right, source_right in enumerate(indices):
                table[source_left][source_right] = w[left][right]
        planted[key] = table
    result = type6_zero_residual_csp(
        planted, memory, stop_at_first=True
    )
    require(result["complete_leaves"] == 1, "planted CSP leaf missed")
    require(
        result["solutions"][0]["permutation"] == list(permutation),
        "CSP accepted the wrong planted permutation",
    )
    require(
        result["solutions"][0]["matching"]
        == [list(edge) for edge in matching],
        "CSP accepted the wrong planted matching",
    )
    return {
        "accepted": True,
        "pivot_assignment_branches_until_leaf":
            result["pivot_assignment_branches"],
        "pivot_mate_branches_until_leaf": result["pivot_mate_branches"],
        "backtrack_nodes_until_leaf": result["backtrack_nodes"],
        "permutation": list(permutation),
        "matching": [list(edge) for edge in matching],
    }


def inverse_two_by_two(
    a: int, b: int, d: int
) -> tuple[tuple[int, int], tuple[int, int]] | None:
    determinant = (a * d - b * b) % P
    if not determinant:
        return None
    inverse = pow(determinant, -1, P)
    return (
        (d * inverse % P, -b * inverse % P),
        (-b * inverse % P, a * inverse % P),
    )


def type33_rank_two_csp(
    context: dict[str, object],
    memory: MemoryGuard,
    *,
    stop_at_first: bool = False,
) -> dict[str, object]:
    signatures = context["signatures"]
    interaction = context["symmetric_interaction"]
    require(all(not any(vector) for vector in signatures), "type33 F")
    branches = 0
    invertible = 0
    unary = 0
    nodes = 0
    leaves = 0
    solutions: list[dict[str, object]] = []

    def result_record() -> dict[str, object]:
        return {
            "branches_visited": branches,
            "invertible_pivot_branches": invertible,
            "nonempty_unary_branches": unary,
            "backtrack_nodes": nodes,
            "complete_leaves": leaves,
            "solutions": solutions,
            "principal_pivot_coverage": (
                "A symmetric rank-two matrix over an "
                "odd-characteristic field has a nonsingular principal "
                "2x2 minor: in D=X^T H X, choose two independent columns "
                "of X, whose principal determinant is det(X_P)^2 det(H), "
                "hence nonzero."
            ),
        }

    def target(
        left: int, left_image: int, right: int, right_image: int
    ) -> int:
        return interaction[SIDE * left + left_image][
            SIDE * right + right_image
        ]

    for p in range(SIDE):
        for q in range(p + 1, SIDE):
            rest = tuple(
                vertex for vertex in range(SIDE) if vertex not in (p, q)
            )
            cases = [(q, p)]
            cases.extend(
                (mate_p, mate_q)
                for mate_p in rest
                for mate_q in rest
                if mate_p != mate_q
            )
            for mate_p, mate_q in cases:
                paired = mate_p == q
                for image_p in range(SIDE):
                    if image_p == p:
                        continue
                    for image_q in range(SIDE):
                        if image_q in (q, image_p):
                            continue
                        branches += 1
                        if branches % 100_000 == 0:
                            memory.sample()
                        w_pq = P - 1 if paired else 1
                        d_pp = -target(p, image_p, p, image_p) % P
                        d_pq = (
                            w_pq - target(p, image_p, q, image_q)
                        ) % P
                        d_qq = -target(q, image_q, q, image_q) % P
                        inverse = inverse_two_by_two(
                            d_pp, d_pq, d_qq
                        )
                        if inverse is None:
                            continue
                        invertible += 1
                        domains: dict[
                            int, tuple[tuple[int, tuple[int, int]], ...]
                        ] = {}
                        viable = True
                        for vertex in rest:
                            values: list[tuple[int, tuple[int, int]]] = []
                            for image in range(SIDE):
                                if image in (vertex, image_p, image_q):
                                    continue
                                w_ip = (
                                    P - 1 if vertex == mate_p else 1
                                )
                                w_iq = (
                                    P - 1 if vertex == mate_q else 1
                                )
                                row = (
                                    (
                                        w_ip
                                        - target(
                                            vertex,
                                            image,
                                            p,
                                            image_p,
                                        )
                                    )
                                    % P,
                                    (
                                        w_iq
                                        - target(
                                            vertex,
                                            image,
                                            q,
                                            image_q,
                                        )
                                    )
                                    % P,
                                )
                                predicted = (
                                    row[0]
                                    * (
                                        inverse[0][0] * row[0]
                                        + inverse[0][1] * row[1]
                                    )
                                    + row[1]
                                    * (
                                        inverse[1][0] * row[0]
                                        + inverse[1][1] * row[1]
                                    )
                                ) % P
                                diagonal = (
                                    -target(
                                        vertex,
                                        image,
                                        vertex,
                                        image,
                                    )
                                ) % P
                                if predicted == diagonal:
                                    values.append((image, row))
                            if not values:
                                viable = False
                                break
                            domains[vertex] = tuple(values)
                        if not viable:
                            continue
                        unary += 1
                        fixed = (
                            frozenset()
                            if paired
                            else frozenset((mate_p, mate_q))
                        )
                        needed_degree = {
                            vertex: 0 if vertex in fixed else 1
                            for vertex in rest
                        }
                        assigned: dict[
                            int, tuple[int, tuple[int, int]]
                        ] = {}
                        degree = {vertex: 0 for vertex in rest}

                        def required_match(
                            left_data: tuple[int, tuple[int, int]],
                            right_data: tuple[int, tuple[int, int]],
                            left: int,
                            right: int,
                        ) -> bool | None:
                            left_row = left_data[1]
                            right_row = right_data[1]
                            predicted = (
                                left_row[0]
                                * (
                                    inverse[0][0] * right_row[0]
                                    + inverse[0][1] * right_row[1]
                                )
                                + left_row[1]
                                * (
                                    inverse[1][0] * right_row[0]
                                    + inverse[1][1] * right_row[1]
                                )
                            ) % P
                            needed = (
                                target(
                                    left,
                                    left_data[0],
                                    right,
                                    right_data[0],
                                )
                                + predicted
                            ) % P
                            if needed == P - 1:
                                return True
                            if needed == 1:
                                return False
                            return None

                        def available(
                            vertex: int, used: int
                        ) -> list[tuple[int, tuple[int, int]]]:
                            answer = []
                            for candidate in domains[vertex]:
                                if (used >> candidate[0]) & 1:
                                    continue
                                local = degree[vertex]
                                valid = True
                                for other, other_data in assigned.items():
                                    relation = required_match(
                                        candidate,
                                        other_data,
                                        vertex,
                                        other,
                                    )
                                    if relation is None:
                                        valid = False
                                        break
                                    if relation:
                                        local += 1
                                        if (
                                            local > needed_degree[vertex]
                                            or degree[other] + 1
                                            > needed_degree[other]
                                        ):
                                            valid = False
                                            break
                                if valid:
                                    answer.append(candidate)
                            return answer

                        def visit(used: int) -> bool:
                            nonlocal nodes, leaves
                            nodes += 1
                            if len(assigned) == len(rest):
                                if all(
                                    degree[vertex]
                                    == needed_degree[vertex]
                                    for vertex in rest
                                ):
                                    leaves += 1
                                    permutation = [-1] * SIDE
                                    permutation[p] = image_p
                                    permutation[q] = image_q
                                    for vertex, data in assigned.items():
                                        permutation[vertex] = data[0]
                                    matching: list[tuple[int, int]] = []
                                    if paired:
                                        matching.append((p, q))
                                    else:
                                        matching.extend(
                                            ((p, mate_p), (q, mate_q))
                                        )
                                    for left_index, left in enumerate(rest):
                                        for right in rest[left_index + 1 :]:
                                            if required_match(
                                                assigned[left],
                                                assigned[right],
                                                left,
                                                right,
                                            ):
                                                matching.append((left, right))
                                    require(
                                        len(matching) == 6,
                                        "type33 leaf matching",
                                    )
                                    selected = [
                                        SIDE * vertex + permutation[vertex]
                                        for vertex in range(SIDE)
                                    ]
                                    w = pair_matrix(matching)
                                    residual = [
                                        [
                                            (
                                                w[left][right]
                                                - interaction[selected[left]][
                                                    selected[right]
                                                ]
                                            )
                                            % P
                                            for right in range(SIDE)
                                        ]
                                        for left in range(SIDE)
                                    ]
                                    require(
                                        rank(residual) == 2,
                                        "type33 false rank-two leaf",
                                    )
                                    solutions.append(
                                        {
                                            "permutation": permutation,
                                            "matching": [
                                                list(edge)
                                                for edge in matching
                                            ],
                                        }
                                    )
                                    return stop_at_first
                                return False
                            choices = []
                            for vertex in rest:
                                if vertex in assigned:
                                    continue
                                values = available(vertex, used)
                                if not values:
                                    return False
                                choices.append(
                                    (len(values), vertex, values)
                                )
                            _, vertex, values = min(choices)
                            for candidate in values:
                                touched: list[int] = []
                                valid = True
                                for other, other_data in assigned.items():
                                    relation = required_match(
                                        candidate,
                                        other_data,
                                        vertex,
                                        other,
                                    )
                                    require(
                                        relation is not None,
                                        "availability drift",
                                    )
                                    if relation:
                                        degree[vertex] += 1
                                        degree[other] += 1
                                        touched.append(other)
                                        if (
                                            degree[vertex]
                                            > needed_degree[vertex]
                                            or degree[other]
                                            > needed_degree[other]
                                        ):
                                            valid = False
                                            break
                                if valid:
                                    assigned[vertex] = candidate
                                    if visit(used | (1 << candidate[0])):
                                        return True
                                    del assigned[vertex]
                                degree[vertex] = 0
                                for other in touched:
                                    degree[other] -= 1
                            return False

                        if visit(
                            (1 << image_p) | (1 << image_q)
                        ) and stop_at_first:
                            return result_record()
    return result_record()


def planted_type33_csp_control(
    context: dict[str, object], memory: MemoryGuard
) -> dict[str, object]:
    """Plant a rank-two residual and require a complete type-33 CSP leaf."""

    permutation = tuple((left + 1) % SIDE for left in range(SIDE))
    matching = (
        (0, 1),
        (2, 3),
        (4, 5),
        (6, 7),
        (8, 9),
        (10, 11),
    )
    w = pair_matrix(matching)
    x = [
        [1, 0, *([0] * 10)],
        [0, 1, *([0] * 10)],
    ]
    h = [[1, 2], [2, 3]]
    residual = matmul(transpose(x), matmul(h, x))
    require(rank(residual) == 2, "type33 planted residual rank")
    indices = [
        SIDE * left + permutation[left] for left in range(SIDE)
    ]
    planted = copy.deepcopy(context)
    for key in ("interaction", "symmetric_interaction"):
        table = [row[:] for row in context[key]]
        for left, source_left in enumerate(indices):
            for right, source_right in enumerate(indices):
                table[source_left][source_right] = (
                    w[left][right] - residual[left][right]
                ) % P
        planted[key] = table
    result = type33_rank_two_csp(
        planted, memory, stop_at_first=True
    )
    require(result["complete_leaves"] == 1, "type33 plant missed")
    require(
        result["solutions"][0]["permutation"] == list(permutation),
        "type33 wrong planted permutation",
    )
    require(
        result["solutions"][0]["matching"]
        == [list(edge) for edge in matching],
        "type33 wrong planted matching",
    )
    return {
        "accepted": True,
        "branches_until_leaf": result["branches_visited"],
        "backtrack_nodes_until_leaf": result["backtrack_nodes"],
        "residual_rank": 2,
        "permutation": list(permutation),
        "matching": [list(edge) for edge in matching],
    }


def rank27_mechanisms(even_parts: int) -> list[list[int]]:
    rank_s = 25 - 2 * even_parts
    answer = []
    for f_rank in range(even_parts, SIDE + 1):
        for d_rank in range(SIDE + 1):
            if rank_s + 2 * f_rank + d_rank == 27:
                answer.append([f_rank, d_rank])
    return answer


def pairing_stream_hash() -> str:
    digest = hashlib.sha256()
    for pairing in PAIRINGS:
        digest.update(bytes(value for edge in pairing for value in edge))
    return digest.hexdigest()


def validate_result(result: dict[str, object]) -> None:
    require(result["format"] == "wave43-rank28-independent-v1", "format")
    require(result["claim_label"] == "VERIFIED_PRECOMPARISON", "label")
    require(len(PAIRINGS) == 10_395, "pairing census")
    require(
        result["rank27_dichotomy"]["1"] == [[1, 2], [2, 0]],
        "e=1 dichotomy",
    )
    require(
        result["rank27_dichotomy"]["2"] == [[2, 2], [3, 0]],
        "e=2 dichotomy",
    )
    require(
        result["rank27_dichotomy"]["3"] == [[3, 2], [4, 0]],
        "e=3 dichotomy",
    )
    even = result["even_types"]
    require(even["2+2+2"]["bounded_rank"]["count"] == 332, "222 count")
    require(even["4+2"]["bounded_rank"]["count"] == 1_352, "42 count")
    require(even["6"]["bounded_rank"]["count"] == 288, "6 count")
    require(
        not any(
            record["zero_residual_scan"]["zero_residual_pairs"]
            for record in (even["2+2+2"], even["4+2"])
        ),
        "zero residual survived",
    )
    require(
        even["6"]["minimum_scan"]["rank_at_most_two_pairs"] == 0,
        "rank-two residual survived",
    )
    require(
        even["6"]["higher_F_CSP"]["complete_leaves"] == 0,
        "type6 zero residual survived",
    )
    require(
        result["type33"]["complete_leaves"] == 0,
        "type33 rank-two residual survived",
    )
    require(not result["type33"]["solutions"], "type33 solutions survived")
    require(
        result["status_wall"]["conditional_endpoint_rank_F7_floor"] == 28,
        "conditional theorem missing",
    )
    require(not result["status_wall"]["endpoint_excluded"], "inflation")
    require(not result["status_wall"]["conway_99_resolved"], "inflation")


def compute() -> dict[str, object]:
    require(sha256_file(WAVE41) == WAVE41_SHA, "Wave41 hash")
    require(sha256_file(WAVE42) == WAVE42_SHA, "Wave42 hash")
    wave42 = json.loads(WAVE42.read_text(encoding="utf-8"))
    require(
        wave42["status_wall"]["universal_rank_F7_M_lower_bound"] == 27,
        "Wave42 theorem changed",
    )
    require(len(PAIRINGS) == 10_395, "pairing universe")
    memory = MemoryGuard(15.0)
    memory.sample()

    contexts = {
        "2+2+2": partition_context((2, 2, 2)),
        "4+2": partition_context((4, 2)),
        "6": partition_context((6,)),
        "3+3": partition_context((3, 3)),
    }
    require(
        {
            key: context["rank_S"] for key, context in contexts.items()
        }
        == {"2+2+2": 19, "4+2": 21, "6": 23, "3+3": 25},
        "local S ranks changed",
    )

    bounded_222, search_222 = bounded_rank_derangements(
        contexts["2+2+2"], 4, memory
    )
    bounded_42, search_42 = bounded_rank_derangements(
        contexts["4+2"], 3, memory
    )
    bounded_6, search_6 = bounded_rank_derangements(
        contexts["6"], 1, memory
    )

    def bounded_record(
        context: dict[str, object],
        values: Sequence[Sequence[int]],
        search: dict[str, int],
    ) -> dict[str, object]:
        histogram = Counter(
            quotient(context, permutation)["F_rank"]
            for permutation in values
        )
        return {
            "count": len(values),
            "rank_histogram": {
                str(key): value for key, value in sorted(histogram.items())
            },
            "stream_sha256": permutation_stream_hash(values),
            "first_20": [list(value) for value in values[:20]],
            "search": search,
            "method": (
                "Direct lexicographic derangement DFS with incremental "
                "canonical F-column row space and immediate rank pruning."
            ),
        }

    record_222 = bounded_record(
        contexts["2+2+2"], bounded_222, search_222
    )
    record_42 = bounded_record(contexts["4+2"], bounded_42, search_42)
    record_6 = bounded_record(contexts["6"], bounded_6, search_6)
    require(record_222["rank_histogram"] == {"4": 332}, "222 ranks")
    require(record_42["rank_histogram"] == {"3": 1_352}, "42 ranks")
    require(record_6["rank_histogram"] == {"1": 288}, "6 ranks")

    zero_222 = explicit_zero_scan(
        contexts["2+2+2"], bounded_222, 4, memory
    )
    zero_42 = explicit_zero_scan(
        contexts["4+2"], bounded_42, 3, memory
    )
    minimum_6 = type6_minimum_scan(
        contexts["6"], bounded_6, memory
    )
    higher_6 = type6_zero_residual_csp(contexts["6"], memory)
    planted_type6 = planted_type6_csp_control(contexts["6"], memory)
    type33 = type33_rank_two_csp(contexts["3+3"], memory)
    planted_type33 = planted_type33_csp_control(contexts["3+3"], memory)
    memory.sample()

    result = {
        "format": "wave43-rank28-independent-v1",
        "claim_label": "VERIFIED_PRECOMPARISON",
        "scope": (
            "Conditional on n3=4158: complete one-edge local rank-27 "
            "exclusion for endpoint types 222, 24, 6, and separately 33."
        ),
        "inputs": {
            "verification/wave41-rank26-secondary/secondary_check.py":
                WAVE41_SHA,
            "verification/wave42-rank27/independent-results.json":
                WAVE42_SHA,
        },
        "rank_formula": (
            "rank(K39)=(25-2e)+2 rank(F)+rank(D), rank(F)>=e"
        ),
        "rank27_dichotomy": {
            str(e): rank27_mechanisms(e) for e in (1, 2, 3)
        },
        "perfect_matching_universe": {
            "count": len(PAIRINGS),
            "stream_sha256": pairing_stream_hash(),
        },
        "even_types": {
            "2+2+2": {
                "even_parts": 3,
                "bounded_rank": record_222,
                "zero_residual_scan": zero_222,
            },
            "4+2": {
                "even_parts": 2,
                "bounded_rank": record_42,
                "zero_residual_scan": zero_42,
            },
            "6": {
                "even_parts": 1,
                "bounded_rank": record_6,
                "minimum_scan": minimum_6,
                "higher_F_CSP": higher_6,
            },
        },
        "type33": type33,
        "controls": {
            "matching_matrix_positive":
                pair_matrix(PAIRINGS[0])[0][1] == P - 1,
            "matching_degree_hostile_rejected": False,
            "type6_planted_zero_residual_CSP": planted_type6,
            "rank_formula_hostile": {
                "correct_e1_mechanisms": rank27_mechanisms(1),
                "mutated_constant_24_mechanisms": [
                    [f_rank, d_rank]
                    for f_rank in range(1, SIDE + 1)
                    for d_rank in range(SIDE + 1)
                    if (24 - 2) + 2 * f_rank + d_rank == 27
                ],
            },
            "type33_planted_rank_two": {},
            "type33_planted_rank_two_CSP": planted_type33,
        },
        "resource_guard": {
            "process_model": "single foreground Python process",
            "background_workers": 0,
            "memory_floor_percent": 15.0,
            "guard_passed": True,
        },
        "status_wall": {
            "even_endpoint_types_rank_at_least_28": True,
            "type33_endpoint_rank_at_least_28": True,
            "conditional_endpoint_rank_F7_floor": 28,
            "endpoint_excluded": False,
            "strict_general_upper_bound_improved": False,
            "graph_constructed": False,
            "conway_99_resolved": False,
            "novelty": "UNKNOWN",
        },
    }

    try:
        pair_matrix(
            ((0, 1), (0, 2), (3, 4), (5, 6), (7, 8), (9, 10))
        )
    except AssertionError:
        result["controls"]["matching_degree_hostile_rejected"] = True

    x = [[1, 0, 1], [0, 1, 1]]
    h = [[1, 2], [2, 3]]
    planted = matmul(transpose(x), matmul(h, x))
    planted_rank = rank(planted)
    planted_minor = (
        planted[0][0] * planted[1][1] - planted[0][1] ** 2
    ) % P
    result["controls"]["type33_planted_rank_two"] = {
        "rank": planted_rank,
        "invertible_principal_minor": planted_minor,
        "accepted_by_rank_and_pivot_predicates":
            planted_rank == 2 and planted_minor != 0,
    }
    require(
        result["controls"]["matching_degree_hostile_rejected"],
        "matching hostile control",
    )
    require(
        result["controls"]["type33_planted_rank_two"][
            "accepted_by_rank_and_pivot_predicates"
        ],
        "type33 positive control",
    )
    require(
        result["controls"]["rank_formula_hostile"][
            "mutated_constant_24_mechanisms"
        ]
        != result["controls"]["rank_formula_hostile"][
            "correct_e1_mechanisms"
        ],
        "rank formula mutation not detected",
    )
    validate_result(result)
    return result


def deterministic_projection(result: dict[str, object]) -> dict[str, object]:
    return json.loads(json.dumps(result))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--deterministic", action="store_true")
    args = parser.parse_args()
    result = compute()
    payload = canonical_bytes(
        deterministic_projection(result) if args.deterministic else result
    )
    if args.verify:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        expected = canonical_bytes(
            deterministic_projection(stored)
            if args.deterministic
            else stored
        )
        require(payload == expected, "stored result differs")
        print(f"PASS {args.verify}")
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
        print(
            f"WROTE {args.output} "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
