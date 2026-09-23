#!/usr/bin/env python3
"""Clean-room verifier for the seven even-part Wave 41 equality cases.

The program consumes only frozen, independently verified Wave 39/40 premises
until its own implementation is frozen.  It never imports discovery code.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import numpy as np


FIELD = 7
ROOT = Path(__file__).resolve().parents[2]
XV = tuple(range(3, 15))
YV = tuple(range(15, 27))
EVEN_TYPES = (
    (2, 1, 1, 1, 1),
    (2, 2, 1, 1),
    (4, 1, 1),
    (3, 2, 1),
    (2, 2, 2),
    (4, 2),
    (6,),
)
INPUT_HASHES = {
    "verification/2026-07-27-wave40-integration-audit.md":
        "afc812a8740210c2c181b1bd0775da0a3526aa95e8706437cb918815f4543e10",
    "verification/wave40-exact-coupling-model/README.md":
        "33201f7cac66df7c65f254d0c3b054cd17cfa67ae54b67cbc5032bee299b924e",
    "verification/wave40-exact-coupling-model/independent-results.json":
        "ff7916d0f5c74c47c8d7787c5cbcc84785cbccd3644d8d03d73e47b73908c0f5",
    "verification/wave40-exact-coupling-model/independent_check.py":
        "d87c7a5eb9377cc3095fff21eec7ff17d94445bef911e4adb092f2db6228bc6e",
    "verification/wave40-exact-coupling-model/run-report.yaml":
        "128bea1e5f7ff347f13e435888d62a6272ebe0968a5f8dc6a0eb2ba22fb99177",
    "verification/wave39-edge-local-rank/README.md":
        "ed749e5788c19a23629cee9f331cce0ef161500d9cb0d939eef3211085c0a405",
    "verification/wave39-edge-local-rank/independent-results.json":
        "85b8d36d6ce5ebd638e957e1731864eff75f38405935f5e51ad5b629edea5966",
    "verification/wave39-edge-local-rank/run-report.yaml":
        "0c16b53a1015f2aa8cd5e96767a97736c1da5ced6691d8ad4085f6579b44cad1",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def freeze_inputs() -> dict[str, str]:
    actual = {name: digest(ROOT / name) for name in INPUT_HASHES}
    if actual != INPUT_HASHES:
        raise ValueError(
            "frozen input mismatch: "
            + repr(
                {
                    name: {"expected": INPUT_HASHES[name], "actual": actual[name]}
                    for name in INPUT_HASHES
                    if actual[name] != INPUT_HASHES[name]
                }
            )
        )
    return actual


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    if not matrix:
        return []
    return [list(column) for column in zip(*matrix)]


def matmul(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    if not left:
        return []
    if not right:
        return [[] for _ in left]
    if len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not conform")
    rt = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) % FIELD for column in rt]
        for row in left
    ]


def matsub(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    if len(left) != len(right) or any(
        len(a) != len(b) for a, b in zip(left, right)
    ):
        raise ValueError("matrix dimensions differ")
    return [
        [(a - b) % FIELD for a, b in zip(row_a, row_b)]
        for row_a, row_b in zip(left, right)
    ]


def row_reduce(rows: Iterable[Sequence[int]]) -> tuple[list[list[int]], list[int]]:
    matrix = [[value % FIELD for value in row] for row in rows]
    if not matrix:
        return [], []
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("ragged matrix")
    pivots: list[int] = []
    target = 0
    for column in range(width):
        source = next(
            (row for row in range(target, len(matrix)) if matrix[row][column]),
            None,
        )
        if source is None:
            continue
        matrix[target], matrix[source] = matrix[source], matrix[target]
        inverse = pow(matrix[target][column], -1, FIELD)
        matrix[target] = [(inverse * value) % FIELD for value in matrix[target]]
        for row in range(len(matrix)):
            coefficient = matrix[row][column]
            if row != target and coefficient:
                matrix[row] = [
                    (value - coefficient * pivot) % FIELD
                    for value, pivot in zip(matrix[row], matrix[target])
                ]
        pivots.append(column)
        target += 1
        if target == len(matrix):
            break
    return matrix, pivots


def matrix_rank(matrix: Sequence[Sequence[int]]) -> int:
    return len(row_reduce(matrix)[1])


def canonical_span(
    vectors: Iterable[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = row_reduce(vectors)
    return tuple(tuple(reduced[i]) for i in range(len(pivots)))


def nullspace(matrix: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = row_reduce(matrix)
    width = len(matrix[0])
    free = [column for column in range(width) if column not in pivots]
    answer = []
    for free_column in free:
        vector = [0] * width
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = (-reduced[row][free_column]) % FIELD
        answer.append(tuple(vector))
    return tuple(answer)


def solve_many(
    matrix: Sequence[Sequence[int]], rhs: Sequence[Sequence[int]]
) -> list[list[int]]:
    """Return the canonical free-variables-zero solution of A X = rhs."""

    n = len(matrix)
    if n == 0 or len(rhs) != n:
        raise ValueError("bad solve dimensions")
    m = len(rhs[0]) if rhs else 0
    augmented = [
        [value % FIELD for value in matrix[row]]
        + [value % FIELD for value in rhs[row]]
        for row in range(n)
    ]
    target = 0
    pivots: list[int] = []
    for column in range(len(matrix[0])):
        source = next(
            (row for row in range(target, n) if augmented[row][column]), None
        )
        if source is None:
            continue
        augmented[target], augmented[source] = augmented[source], augmented[target]
        inverse = pow(augmented[target][column], -1, FIELD)
        augmented[target] = [
            inverse * value % FIELD for value in augmented[target]
        ]
        for row in range(n):
            coefficient = augmented[row][column]
            if row != target and coefficient:
                augmented[row] = [
                    (a - coefficient * b) % FIELD
                    for a, b in zip(augmented[row], augmented[target])
                ]
        pivots.append(column)
        target += 1
        if target == n:
            break
    for row in range(target, n):
        if not any(augmented[row][: len(matrix[0])]) and any(
            augmented[row][len(matrix[0]) :]
        ):
            raise ValueError("inconsistent linear system")
    solution = [[0] * m for _ in range(len(matrix[0]))]
    for row, pivot in enumerate(pivots):
        solution[pivot] = augmented[row][len(matrix[0]) :]
    if matmul(matrix, solution) != [
        [value % FIELD for value in row] for row in rhs
    ]:
        raise AssertionError("linear solve failed")
    return solution


def solve_operator(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return G such that S G b=b for every b in im(S)."""

    n = len(matrix)
    augmented = [
        [value % FIELD for value in matrix[row]]
        + [int(row == column) for column in range(n)]
        for row in range(n)
    ]
    target = 0
    pivots: list[int] = []
    for column in range(n):
        source = next(
            (row for row in range(target, n) if augmented[row][column]), None
        )
        if source is None:
            continue
        augmented[target], augmented[source] = augmented[source], augmented[target]
        inverse = pow(augmented[target][column], -1, FIELD)
        augmented[target] = [
            inverse * value % FIELD for value in augmented[target]
        ]
        for row in range(n):
            coefficient = augmented[row][column]
            if row != target and coefficient:
                augmented[row] = [
                    (a - coefficient * b) % FIELD
                    for a, b in zip(augmented[row], augmented[target])
                ]
        pivots.append(column)
        target += 1
    operator = [[0] * n for _ in range(n)]
    for row, pivot in enumerate(pivots):
        operator[pivot] = augmented[row][n:]
    if matmul(matrix, matmul(operator, matrix)) != [
        [value % FIELD for value in row] for row in matrix
    ]:
        raise AssertionError("particular-solution operator failed")
    return operator


def belongs(
    vector: Sequence[int], basis: Sequence[Sequence[int]]
) -> bool:
    return matrix_rank([*basis, vector]) == len(basis)


def projective(vector: Sequence[int]) -> tuple[int, ...]:
    first = next((value % FIELD for value in vector if value % FIELD), None)
    if first is None:
        raise ValueError("zero vector has no projective representative")
    inverse = pow(first, -1, FIELD)
    return tuple(inverse * value % FIELD for value in vector)


def connect(graph: list[list[int]], a: int, b: int) -> None:
    if a == b:
        raise ValueError("loop")
    graph[a][b] = graph[b][a] = 1


def local_graph(parts: Sequence[int]) -> list[list[int]]:
    if sum(parts) != 6 or any(part <= 0 for part in parts):
        raise ValueError("not a positive partition of six")
    graph = [[0] * 27 for _ in range(27)]
    for a, b in ((0, 1), (0, 2), (1, 2)):
        connect(graph, a, b)
    for vertex in XV:
        connect(graph, 0, vertex)
    for vertex in YV:
        connect(graph, 1, vertex)
    start = 0
    for part in parts:
        for i in range(part):
            xa, xb = XV[start + 2 * i : start + 2 * i + 2]
            ya, yb = YV[start + 2 * i : start + 2 * i + 2]
            next_ya = YV[start + 2 * ((i + 1) % part)]
            connect(graph, xa, xb)
            connect(graph, xa, ya)
            connect(graph, xb, yb)
            connect(graph, yb, next_ya)
        start += 2 * part
    return graph


def transported(graph: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            (1 - int(row == column) - 2 * graph[row][column]) % FIELD
            for column in range(len(graph))
        ]
        for row in range(len(graph))
    ]


def border_column(x_index: int, y_index: int) -> tuple[int, ...]:
    column = [1] * 27
    for vertex in (2, XV[x_index], YV[y_index]):
        column[vertex] = FIELD - 1
    return tuple(column)


def border_matrix(permutation: Sequence[int]) -> list[list[int]]:
    if sorted(permutation) != list(range(12)):
        raise ValueError("third-fibre relation is not a permutation")
    return transpose(
        [border_column(x_index, permutation[x_index]) for x_index in range(12)]
    )


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


def maximum_matching(edges: Iterable[tuple[int, int]]) -> int:
    neighbors = {left: [] for left in range(12)}
    for left, right in sorted(set(edges)):
        neighbors[left].append(right)
    owner: dict[int, int] = {}

    def augment(left: int, seen: set[int]) -> bool:
        for right in neighbors[left]:
            if right in seen:
                continue
            seen.add(right)
            if right not in owner or augment(owner[right], seen):
                owner[right] = left
                return True
        return False

    return sum(augment(left, set()) for left in range(12))


def perfect_permutations(
    edges: Iterable[tuple[int, int]],
) -> Iterator[tuple[int, ...]]:
    neighbors = {
        left: tuple(sorted(right for a, right in set(edges) if a == left))
        for left in range(12)
    }
    chosen = [-1] * 12

    def visit(unassigned: frozenset[int], free_right: frozenset[int]):
        if not unassigned:
            yield tuple(chosen)
            return
        left = min(
            unassigned,
            key=lambda item: (
                sum(right in free_right for right in neighbors[item]),
                item,
            ),
        )
        for right in neighbors[left]:
            if right not in free_right:
                continue
            chosen[left] = right
            yield from visit(unassigned - {left}, free_right - {right})
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
    raw = 1 if dimension == 0 else 0
    spaces: set[tuple[tuple[int, ...], ...]]
    if dimension == 0:
        spaces = {()}
    else:
        spaces = set()
        for generators in itertools.combinations(lines, dimension):
            raw += 1
            span = canonical_span(generators)
            if len(span) == dimension:
                spaces.add(span)
    supporting = 0
    permutations: dict[
        tuple[int, ...], tuple[tuple[int, ...], ...]
    ] = {}
    for space in sorted(spaces):
        edges = [
            pair
            for pair, signature in signatures.items()
            if belongs(signature, space)
        ]
        if maximum_matching(edges) != 12:
            continue
        supporting += 1
        for permutation in perfect_permutations(edges):
            b = transpose(
                [signatures[(i, permutation[i])] for i in range(12)]
            )
            rowspace = canonical_span(b)
            if len(rowspace) != dimension:
                raise AssertionError(
                    "a lower-dimensional permutation escaped the exhausted search"
                )
            permutations[permutation] = rowspace
    return sorted(permutations.items()), {
        "observed_projective_lines": len(lines),
        "raw_generator_subsets": raw,
        "canonical_dimension_e_subspaces": len(spaces),
        "subspaces_supporting_permutation": supporting,
    }


def perfect_matchings(vertices: tuple[int, ...] = tuple(range(12))):
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        rest = vertices[1:index] + vertices[index + 1 :]
        for tail in perfect_matchings(rest):
            yield ((first, second),) + tail


def matching_adjacency(
    matching: Sequence[Sequence[int]], order: int = 12
) -> list[list[int]]:
    adjacency = [[0] * order for _ in range(order)]
    used: set[int] = set()
    for pair in matching:
        if len(pair) != 2:
            raise ValueError("bad matching pair")
        a, b = pair
        if a == b or a in used or b in used:
            raise ValueError("not a matching")
        used.update((a, b))
        adjacency[a][b] = adjacency[b][a] = 1
    if used != set(range(order)):
        raise ValueError("matching is not perfect")
    return adjacency


def w_block(matching: Sequence[Sequence[int]]) -> list[list[int]]:
    adjacency = matching_adjacency(matching)
    return [
        [
            (1 - int(i == j) - 2 * adjacency[i][j]) % FIELD
            for j in range(12)
        ]
        for i in range(12)
    ]


def block_matrix(
    s: Sequence[Sequence[int]],
    u: Sequence[Sequence[int]],
    w: Sequence[Sequence[int]],
) -> list[list[int]]:
    ut = transpose(u)
    return [
        [*s[row], *u[row]] for row in range(len(s))
    ] + [
        [*ut[row], *w[row]] for row in range(len(w))
    ]


def equality_data(
    s: Sequence[Sequence[int]],
    kernel: Sequence[Sequence[int]],
    permutation: Sequence[int],
) -> dict[str, object]:
    u = border_matrix(permutation)
    b = matmul(kernel, u)
    right_rows = nullspace(b)
    r = transpose(right_rows)
    ur = matmul(u, r)
    x = solve_many(s, ur)
    w0 = [
        [(1 - int(i == j)) % FIELD for j in range(12)]
        for i in range(12)
    ]
    target = matsub(matmul(transpose(r), matmul(w0, r)), matmul(transpose(ur), x))
    if target != transpose(target):
        raise AssertionError("equality target is not symmetric")
    return {
        "u": u,
        "b": b,
        "right_kernel_rows": right_rows,
        "r": r,
        "x": x,
        "target": tuple(tuple(row) for row in target),
    }


def schur_pairing_table(
    solve_map: Sequence[Sequence[int]],
) -> list[list[int]]:
    columns = [
        border_column(i, j) for i in range(12) for j in range(12)
    ]
    solved = matmul(solve_map, transpose(columns))
    return matmul(columns, solved)


def fast_equality_target(
    permutation: Sequence[int],
    right_rows: Sequence[Sequence[int]],
    pairings: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    selected = [12 * i + permutation[i] for i in range(12)]
    schur = [
        [pairings[selected[i]][selected[j]] for j in range(12)]
        for i in range(12)
    ]
    w0 = [
        [(1 - int(i == j)) % FIELD for j in range(12)]
        for i in range(12)
    ]
    r = transpose(right_rows)
    target = matmul(transpose(r), matmul(matsub(w0, schur), r))
    if target != transpose(target):
        raise AssertionError("fast equality target is not symmetric")
    return tuple(tuple(row) for row in target)


def matching_core(
    r: Sequence[Sequence[int]], matching: Sequence[Sequence[int]]
) -> list[list[int]]:
    adjacency = matching_adjacency(matching)
    return [
        [(2 * value) % FIELD for value in row]
        for row in matmul(transpose(r), matmul(adjacency, r))
    ]


def edge_core_table(
    r: Sequence[Sequence[int]],
) -> dict[tuple[int, int], tuple[tuple[int, ...], ...]]:
    dimension = len(r[0])
    table = {}
    for a in range(12):
        for b in range(a + 1, 12):
            table[(a, b)] = tuple(
                tuple(
                    (
                        2
                        * (
                            r[a][i] * r[b][j]
                            + r[b][i] * r[a][j]
                        )
                    )
                    % FIELD
                    for j in range(dimension)
                )
                for i in range(dimension)
            )
    return table


def matching_core_fast(
    edge_table: dict[tuple[int, int], tuple[tuple[int, ...], ...]],
    matching: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    dimension = len(next(iter(edge_table.values())))
    total = [[0] * dimension for _ in range(dimension)]
    for raw_a, raw_b in matching:
        a, b = sorted((raw_a, raw_b))
        contribution = edge_table[(a, b)]
        for i in range(dimension):
            for j in range(dimension):
                total[i][j] = (total[i][j] + contribution[i][j]) % FIELD
    return tuple(tuple(row) for row in total)


def matching_core_counter_numpy(
    r: Sequence[Sequence[int]],
    matchings: Sequence[Sequence[Sequence[int]]],
) -> Counter[bytes]:
    """Vectorized exact integer census of all matching-induced forms."""

    edges = list(itertools.combinations(range(12), 2))
    edge_index = {edge: index for index, edge in enumerate(edges)}
    dimension = len(r[0])
    contributions = np.zeros((len(edges), dimension, dimension), dtype=np.int64)
    for index, (a, b) in enumerate(edges):
        for i in range(dimension):
            for j in range(dimension):
                contributions[index, i, j] = (
                    2 * (r[a][i] * r[b][j] + r[b][i] * r[a][j])
                ) % FIELD
    indices = np.asarray(
        [
            [edge_index[tuple(sorted(pair))] for pair in matching]
            for matching in matchings
        ],
        dtype=np.int16,
    )
    cores = contributions[indices].sum(axis=1) % FIELD
    cores = cores.astype(np.uint8, copy=False)
    return Counter(core.tobytes() for core in cores)


def matrix_bytes(matrix: Sequence[Sequence[int]]) -> bytes:
    return bytes(value % FIELD for row in matrix for value in row)


def equality_core(
    target: Sequence[Sequence[int]],
    r: Sequence[Sequence[int]],
    matching: Sequence[Sequence[int]],
) -> list[list[int]]:
    return matsub(target, matching_core(r, matching))


def core_laplacian(
    local: Sequence[Sequence[int]],
    permutation: Sequence[int],
    matching: Sequence[Sequence[int]],
) -> list[list[int]]:
    adjacency = [[0] * 36 for _ in range(36)]

    def add(a: int, b: int) -> None:
        adjacency[a][b] = adjacency[b][a] = 1

    for i in range(12):
        for j in range(i + 1, 12):
            if local[XV[i]][XV[j]]:
                add(i, j)
            if local[YV[i]][YV[j]]:
                add(12 + i, 12 + j)
        y = next(j for j in range(12) if local[XV[i]][YV[j]])
        add(i, 12 + y)
        add(i, 24 + i)
        add(12 + permutation[i], 24 + i)
    for a, b in matching:
        add(24 + a, 24 + b)
    if [sum(row) for row in adjacency] != [3] * 36:
        raise AssertionError("neighbor core is not cubic")
    return [
        [
            (3 * int(i == j) - adjacency[i][j]) % FIELD
            for j in range(36)
        ]
        for i in range(36)
    ]


def canonical_key(matrix: Sequence[Sequence[int]]) -> str:
    payload = json.dumps(matrix, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def lift_symmetric_form(
    right_rows: Sequence[Sequence[int]], target: Sequence[Sequence[int]]
) -> list[list[int]]:
    """Build symmetric W with R^T W R=target, as a positive control."""

    r = transpose(right_rows)
    d = len(right_rows)
    chosen: tuple[int, ...] | None = None
    for rows in itertools.combinations(range(12), d):
        minor = [[r[row][column] for column in range(d)] for row in rows]
        if matrix_rank(minor) == d:
            chosen = rows
            break
    if chosen is None:
        raise AssertionError("right-kernel basis lost column rank")
    minor = [[r[row][column] for column in range(d)] for row in chosen]
    inverse_columns = []
    for column in range(d):
        rhs = [[int(row == column)] for row in range(d)]
        inverse_columns.append([row[0] for row in solve_many(minor, rhs)])
    inverse = transpose(inverse_columns)
    left_inverse = [[0] * 12 for _ in range(d)]
    for column, row_index in enumerate(chosen):
        for row in range(d):
            left_inverse[row][row_index] = inverse[row][column]
    if matmul(left_inverse, r) != [
        [int(i == j) for j in range(d)] for i in range(d)
    ]:
        raise AssertionError("left inverse construction failed")
    return matmul(transpose(left_inverse), matmul(target, left_inverse))


def partition_label(parts: Sequence[int]) -> str:
    return "+".join(map(str, parts))


def verify_type(
    parts: Sequence[int], matchings: Sequence[Sequence[Sequence[int]]]
) -> dict[str, object]:
    local = local_graph(parts)
    s = transported(local)
    e = sum(part % 2 == 0 for part in parts)
    expected_local_rank = 25 - 2 * e
    local_rank = matrix_rank(s)
    if local_rank != expected_local_rank:
        raise AssertionError("frozen local rank formula failed")
    kernel = nullspace(s)
    signatures = projected_signatures(kernel)
    permutation_records, search = minimum_projection_permutations(signatures, e)
    if not permutation_records:
        raise AssertionError("no minimum-projection permutation")
    by_kernel: defaultdict[
        tuple[tuple[int, ...], ...], list[tuple[int, ...]]
    ] = defaultdict(list)
    for permutation, rowspace in permutation_records:
        by_kernel[nullspace(rowspace)].append(permutation)
    solve_map = solve_operator(s)
    pairings = schur_pairing_table(solve_map)

    matching_list_digest = hashlib.sha256(
        json.dumps(matchings, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    kernel_records = []
    total_checks = 0
    total_zeros = 0
    direct_samples = 0
    min_actual_rank = 39
    positive_controls = 0
    total_targets = 0
    for right_rows, kernel_permutations in sorted(
        by_kernel.items(), key=lambda item: canonical_key(item[0])
    ):
        r = transpose(right_rows)
        edge_table = edge_core_table(r)
        matching_core_counter = matching_core_counter_numpy(r, matchings)
        total_checks += len(matchings)
        if sum(matching_core_counter.values()) != 10395:
            raise AssertionError("matching-core census is incomplete")

        target_counter: Counter[
            tuple[tuple[int, ...], ...]
        ] = Counter()
        representative_by_target = {}
        for permutation in kernel_permutations:
            target = fast_equality_target(permutation, right_rows, pairings)
            target_counter[target] += 1
            representative_by_target.setdefault(target, permutation)
            target_key = matrix_bytes(target)
            if target_key in matching_core_counter:
                total_zeros += matching_core_counter[target_key]
        total_targets += len(target_counter)
        if total_zeros:
            raise AssertionError("rank-25 equality matching found")

        target = min(target_counter, key=canonical_key)
        permutation = representative_by_target[target]
        first_matching = matchings[0]
        first_core_rank = matrix_rank(
            matsub(target, matching_core_fast(edge_table, first_matching))
        )
        if first_core_rank == 0:
            raise AssertionError("representative unexpectedly attains equality")

        # Direct dense verification for the closest genuine matching.
        u = border_matrix(permutation)
        k39 = block_matrix(s, u, w_block(first_matching))
        direct_rank = matrix_rank(k39)
        laplacian_rank = matrix_rank(
            core_laplacian(local, permutation, first_matching)
        )
        if direct_rank != 1 + laplacian_rank:
            raise AssertionError("39-block/core-Laplacian identity failed")
        if direct_rank != 25 + first_core_rank:
            raise AssertionError("Schur equality-core rank formula failed")
        direct_samples += 1
        min_actual_rank = min(min_actual_rank, direct_rank)

        # Positive hostile control: a symmetric lower-right block can attain
        # equality, so rejection depends on the perfect-matching constraint.
        selected = [12 * i + permutation[i] for i in range(12)]
        selected_schur = [
            [pairings[selected[i]][selected[j]] for j in range(12)]
            for i in range(12)
        ]
        schur_target = matmul(
            transpose(r), matmul(selected_schur, r)
        )
        target_w = lift_symmetric_form(right_rows, schur_target)
        positive_rank = matrix_rank(block_matrix(s, u, target_w))
        if positive_rank != 25:
            raise AssertionError("positive equality control did not attain rank 25")
        positive_controls += 1

        target_digest = hashlib.sha256(
            b"".join(
                (
                    canonical_key(item).encode("ascii")
                    + b":"
                    + str(target_counter[item]).encode("ascii")
                    + b"\n"
                )
                for item in sorted(target_counter, key=canonical_key)
            )
        ).hexdigest()
        kernel_records.append(
            {
                "right_kernel_sha256": canonical_key(right_rows),
                "minimum_projection_permutations": len(kernel_permutations),
                "distinct_equality_targets": len(target_counter),
                "equality_target_multiset_sha256": target_digest,
                "representative_equality_target_sha256": canonical_key(target),
                "representative_permutation": list(permutation),
                "right_kernel_dimension": len(right_rows),
                "labelled_Z_matchings_checked": 10395,
                "distinct_matching_cores": len(matching_core_counter),
                "matching_core_multiset_sha256": hashlib.sha256(
                    b"".join(
                        (
                            item.hex().encode("ascii")
                            + b":"
                            + str(matching_core_counter[item]).encode("ascii")
                            + b"\n"
                        )
                        for item in sorted(matching_core_counter)
                    )
                ).hexdigest(),
                "equality_compatible_permutation_matching_pairs": 0,
                "direct_sample_matching": [list(pair) for pair in first_matching],
                "direct_sample_equality_core_rank": first_core_rank,
                "direct_39_block_rank": direct_rank,
                "core_laplacian_rank": laplacian_rank,
                "positive_mutation_39_block_rank": positive_rank,
            }
        )

    if total_zeros:
        raise AssertionError("F7 incompatibility failed")
    return {
        "partition": list(parts),
        "even_part_count": e,
        "local_rank_F7": local_rank,
        "local_kernel_dimension": len(kernel),
        "minimum_projection_rank": e,
        "minimum_projection_permutation_count": len(permutation_records),
        "minimum_projection_search": search,
        "distinct_right_kernels": len(by_kernel),
        "distinct_kernel_target_pairs": total_targets,
        "labelled_Z_matching_count": len(matchings),
        "labelled_Z_matchings_sha256": matching_list_digest,
        "kernel_target_matching_checks": total_checks,
        "rank_25_compatible_cases": total_zeros,
        "minimum_direct_39_block_rank_over_target_samples": min_actual_rank,
        "direct_rank_samples": direct_samples,
        "positive_rank_25_mutation_controls": positive_controls,
        "right_kernels": kernel_records,
        "verdict": "VERIFIED_INCOMPATIBLE_WITH_RANK_25",
    }


def results_skeleton(
    frozen: dict[str, str],
    matchings: Sequence[Sequence[Sequence[int]]],
) -> dict[str, object]:
    return {
        "format": "wave41-evenpart-equality-independent-v1",
        "claim_label": "VERIFIED_SCOPED",
        "field": 7,
        "frozen_inputs": frozen,
        "equality_criterion": {
            "statement": (
                "For B=H^T U of minimum rank e and R spanning ker(B), solve "
                "S X=U R. Then rank([[S,U],[U^T,W]])=25 iff "
                "R^T(W R-U^T X)=0."
            ),
            "basis_invariance": (
                "Replacing R by R C congruently transforms the equality core "
                "by C^T(-)C; changing X by a kernel-valued solution changes "
                "U^T X by a term annihilated between R^T and R."
            ),
            "core_laplacian_identity": (
                "For the cubic 36-vertex neighbor core A_core, "
                "rank_F7(K_39)=1+rank_F7(3I-A_core)."
            ),
        },
        "labelled_Z_matchings": {
            "count": len(matchings),
            "expected_formula": "(11)!!=10,395",
            "sha256": hashlib.sha256(
                json.dumps(matchings, separators=(",", ":")).encode("ascii")
            ).hexdigest(),
        },
        "partition_results": {},
        "status_wall": {
            "seven_even_part_types": "VERIFIED_SCOPED",
            "universal_rank_F7_M_at_least_26": (
                "REQUIRES_SEPARATE_FROZEN_ALL_ODD_COMPOSITION"
            ),
            "conway_99": "UNKNOWN",
            "n3_endpoint_excluded": "NO",
            "general_upper_bound_below_4158": "NOT_PROVED",
            "novelty": "UNKNOWN",
            "priority": "UNKNOWN",
        },
    }


def finalize_totals(results: dict[str, object]) -> dict[str, object]:
    if set(results["partition_results"]) != {
        partition_label(parts) for parts in EVEN_TYPES
    }:
        raise AssertionError("results do not cover exactly seven even-part types")
    if any(
        item["rank_25_compatible_cases"] != 0
        or item["verdict"] != "VERIFIED_INCOMPATIBLE_WITH_RANK_25"
        for item in results["partition_results"].values()
    ):
        raise AssertionError("an even-part type has not passed")
    results["totals"] = {
        "even_types": len(EVEN_TYPES),
        "minimum_projection_permutations": sum(
            item["minimum_projection_permutation_count"]
            for item in results["partition_results"].values()
        ),
        "distinct_right_kernels": sum(
            item["distinct_right_kernels"]
            for item in results["partition_results"].values()
        ),
        "distinct_kernel_target_pairs": sum(
            item["distinct_kernel_target_pairs"]
            for item in results["partition_results"].values()
        ),
        "kernel_target_matching_checks": sum(
            item["kernel_target_matching_checks"]
            for item in results["partition_results"].values()
        ),
        "rank_25_compatible_cases": 0,
    }
    return results


def build_results() -> dict[str, object]:
    frozen = freeze_inputs()
    matchings = list(perfect_matchings())
    if len(matchings) != 10395 or len(set(matchings)) != 10395:
        raise AssertionError("labelled perfect-matching generator is incomplete")
    results = results_skeleton(frozen, matchings)
    for parts in EVEN_TYPES:
        results["partition_results"][partition_label(parts)] = verify_type(
            parts, matchings
        )
    return finalize_totals(results)


def assemble_partials(paths: Sequence[Path]) -> dict[str, object]:
    frozen = freeze_inputs()
    matchings = list(perfect_matchings())
    results = results_skeleton(frozen, matchings)
    for path in paths:
        partial = strict_load(path)
        if partial.get("format") != "wave41-evenpart-equality-partial-v1":
            raise ValueError(f"wrong partial format: {path}")
        item = partial["partition_result"]
        parts = tuple(item["partition"])
        if parts not in EVEN_TYPES:
            raise ValueError(f"unexpected partition in {path}")
        label = partition_label(parts)
        if label in results["partition_results"]:
            raise ValueError(f"duplicate partition {label}")
        if item["labelled_Z_matchings_sha256"] != results[
            "labelled_Z_matchings"
        ]["sha256"]:
            raise ValueError(f"matching universe mismatch in {path}")
        results["partition_results"][label] = item
    return finalize_totals(results)


def validate_results(results: object) -> None:
    if not isinstance(results, dict):
        raise ValueError("results root must be an object")
    if results.get("format") != "wave41-evenpart-equality-independent-v1":
        raise ValueError("wrong results format")
    if results.get("claim_label") != "VERIFIED_SCOPED":
        raise ValueError("wrong scoped claim label")
    if results.get("field") != FIELD:
        raise ValueError("wrong field")
    if results.get("frozen_inputs") != INPUT_HASHES:
        raise ValueError("frozen inputs changed")
    matching_summary = results.get("labelled_Z_matchings", {})
    if matching_summary.get("count") != 10395:
        raise ValueError("wrong labelled matching count")
    partitions = results.get("partition_results")
    if not isinstance(partitions, dict) or set(partitions) != {
        partition_label(parts) for parts in EVEN_TYPES
    }:
        raise ValueError("partition coverage is not exactly the seven even types")
    for parts in EVEN_TYPES:
        label = partition_label(parts)
        item = partitions[label]
        e = sum(part % 2 == 0 for part in parts)
        if item.get("partition") != list(parts):
            raise ValueError(f"partition payload changed for {label}")
        if item.get("even_part_count") != e:
            raise ValueError(f"even-part count changed for {label}")
        if item.get("local_rank_F7") != 25 - 2 * e:
            raise ValueError(f"local rank changed for {label}")
        if item.get("minimum_projection_rank") != e:
            raise ValueError(f"minimum projection rank changed for {label}")
        if item.get("labelled_Z_matching_count") != 10395:
            raise ValueError(f"matching count changed for {label}")
        if item.get("kernel_target_matching_checks") != (
            10395 * item.get("distinct_right_kernels", -1)
        ):
            raise ValueError(f"incomplete kernel matching census for {label}")
        if item.get("rank_25_compatible_cases") != 0:
            raise ValueError(f"rank-25 compatibility introduced for {label}")
        if item.get("verdict") != "VERIFIED_INCOMPATIBLE_WITH_RANK_25":
            raise ValueError(f"scoped verdict changed for {label}")
        kernels = item.get("right_kernels")
        if not isinstance(kernels, list) or len(kernels) != item.get(
            "distinct_right_kernels"
        ):
            raise ValueError(f"right-kernel records incomplete for {label}")
        if sum(
            record.get("minimum_projection_permutations", 0)
            for record in kernels
        ) != item.get("minimum_projection_permutation_count"):
            raise ValueError(f"minimum permutations incomplete for {label}")
        for record in kernels:
            if record.get("labelled_Z_matchings_checked") != 10395:
                raise ValueError(f"kernel matching census changed for {label}")
            if record.get(
                "equality_compatible_permutation_matching_pairs"
            ) != 0:
                raise ValueError(f"kernel equality case introduced for {label}")
            if record.get("positive_mutation_39_block_rank") != 25:
                raise ValueError(f"positive control changed for {label}")
            direct = record.get("direct_39_block_rank")
            laplacian = record.get("core_laplacian_rank")
            core = record.get("direct_sample_equality_core_rank")
            if direct != 1 + laplacian or direct != 25 + core:
                raise ValueError(f"direct rank identities changed for {label}")
            if direct < 26:
                raise ValueError(f"actual matching attained rank 25 for {label}")
    totals = results.get("totals", {})
    expected_totals = {
        "even_types": 7,
        "minimum_projection_permutations": sum(
            item["minimum_projection_permutation_count"]
            for item in partitions.values()
        ),
        "distinct_right_kernels": sum(
            item["distinct_right_kernels"] for item in partitions.values()
        ),
        "distinct_kernel_target_pairs": sum(
            item["distinct_kernel_target_pairs"] for item in partitions.values()
        ),
        "kernel_target_matching_checks": sum(
            item["kernel_target_matching_checks"] for item in partitions.values()
        ),
        "rank_25_compatible_cases": 0,
    }
    if totals != expected_totals:
        raise ValueError("totals changed")
    wall = results.get("status_wall", {})
    if wall.get("universal_rank_F7_M_at_least_26") != (
        "REQUIRES_SEPARATE_FROZEN_ALL_ODD_COMPOSITION"
    ):
        raise ValueError("universal theorem promoted before composition")
    for key in ("conway_99", "novelty", "priority"):
        if wall.get(key) != "UNKNOWN":
            raise ValueError(f"{key} status inflated")


def strict_load(path: Path) -> object:
    def reject(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument(
        "--partition",
        help="run one canonical even type, for bounded journal generation",
    )
    parser.add_argument(
        "--assemble-partials",
        nargs="+",
        type=Path,
        help="assemble seven independently generated bounded journals",
    )
    args = parser.parse_args()
    if args.partition and args.assemble_partials:
        raise SystemExit("--partition and --assemble-partials are exclusive")
    partial_mode = False
    if args.assemble_partials:
        actual = assemble_partials(args.assemble_partials)
    elif args.partition:
        partial_mode = True
        wanted = tuple(int(value) for value in args.partition.split("+"))
        if wanted not in EVEN_TYPES:
            raise SystemExit("partition is not one of the seven frozen even types")
        freeze_inputs()
        generated_matchings = list(perfect_matchings())
        actual = {
            "format": "wave41-evenpart-equality-partial-v1",
            "partition_result": verify_type(wanted, generated_matchings),
        }
    else:
        actual = build_results()
    if not partial_mode:
        validate_results(actual)
    if args.verify:
        expected = strict_load(args.verify)
        validate_results(expected)
        if actual != expected:
            raise SystemExit("verification mismatch")
        print(f"VERIFIED {args.verify}")
    else:
        payload = json.dumps(actual, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(payload, encoding="utf-8", newline="\n")
            print(args.output)
        else:
            print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
