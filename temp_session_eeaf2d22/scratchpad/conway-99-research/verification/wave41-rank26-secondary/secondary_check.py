#!/usr/bin/env python3
"""Independent exact checker for the Wave 41 rank-26 claim.

This module is intentionally self-contained.  It consumes only the frozen
Wave 40 mathematical premises recorded beside it and does not import any
Wave 41 discovery or primary-verifier code.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Iterator, Sequence


P = 7
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
X = tuple(range(3, 15))
Y = tuple(range(15, 27))

FROZEN_INPUTS = {
    "CONJECTURE.md":
        "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "verification/2026-07-27-wave40-orchestrator.md":
        "a136b971ba4e675a5edfe62780e7754b7c716ff1753507be0201eadf3042dfbf",
    "verification/2026-07-27-wave40-integration-audit.md":
        "afc812a8740210c2c181b1bd0775da0a3526aa95e8706437cb918815f4543e10",
    "verification/wave40-exact-coupling-model/README.md":
        "33201f7cac66df7c65f254d0c3b054cd17cfa67ae54b67cbc5032bee299b924e",
    "verification/wave40-exact-coupling-model/independent_check.py":
        "d87c7a5eb9377cc3095fff21eec7ff17d94445bef911e4adb092f2db6228bc6e",
    "verification/wave40-exact-coupling-model/independent-results.json":
        "ff7916d0f5c74c47c8d7787c5cbcc84785cbccd3644d8d03d73e47b73908c0f5",
    "verification/wave40-exact-coupling-model/run-report.yaml":
        "128bea1e5f7ff347f13e435888d62a6272ebe0968a5f8dc6a0eb2ba22fb99177",
    "verification/2026-07-27-wave39-orchestrator.md":
        "094db8281faf23f402f5093a617c43ebe428dae6f8ce1eceae8621472fc37111",
    "verification/wave39-edge-local-rank/README.md":
        "ed749e5788c19a23629cee9f331cce0ef161500d9cb0d939eef3211085c0a405",
    "verification/wave39-edge-local-rank/independent-results.json":
        "85b8d36d6ce5ebd638e957e1731864eff75f38405935f5e51ad5b629edea5966",
    "verification/wave39-edge-local-rank/run-report.yaml":
        "0c16b53a1015f2aa8cd5e96767a97736c1da5ced6691d8ad4085f6579b44cad1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_frozen_inputs() -> dict[str, str]:
    actual = {name: sha256(ROOT / name) for name in FROZEN_INPUTS}
    if actual != FROZEN_INPUTS:
        differences = {
            name: {"expected": FROZEN_INPUTS[name], "actual": actual[name]}
            for name in FROZEN_INPUTS
            if actual[name] != FROZEN_INPUTS[name]
        }
        raise ValueError(f"Wave 40 input freeze mismatch: {differences}")
    return actual


def positive_partitions(total: int, ceiling: int | None = None) -> Iterator[tuple[int, ...]]:
    """Generate every positive integer partition in nonincreasing order."""

    if total == 0:
        yield ()
        return
    largest = min(total, total if ceiling is None else ceiling)
    for first in range(largest, 0, -1):
        for tail in positive_partitions(total - first, first):
            yield (first, *tail)


def rref(rows: Iterable[Sequence[int]], pivot_limit: int | None = None) -> tuple[list[list[int]], list[int]]:
    matrix = [[value % P for value in row] for row in rows]
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
        inverse = pow(matrix[next_row][column], -1, P)
        matrix[next_row] = [(inverse * value) % P for value in matrix[next_row]]
        for row in range(len(matrix)):
            if row == next_row:
                continue
            factor = matrix[row][column]
            if factor:
                matrix[row] = [
                    (value - factor * pivot) % P
                    for value, pivot in zip(matrix[row], matrix[next_row])
                ]
        pivots.append(column)
        next_row += 1
        if next_row == len(matrix):
            break
    return matrix, pivots


def rank(rows: Iterable[Sequence[int]]) -> int:
    return len(rref(rows)[1])


def nullspace(matrix: Sequence[Sequence[int]]) -> list[tuple[int, ...]]:
    if not matrix:
        raise ValueError("nullspace needs a known-width matrix")
    reduced, pivots = rref(matrix)
    width = len(matrix[0])
    free_columns = [column for column in range(width) if column not in pivots]
    basis: list[tuple[int, ...]] = []
    for free in free_columns:
        vector = [0] * width
        vector[free] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = (-reduced[row][free]) % P
        basis.append(tuple(vector))
    return basis


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    if not matrix:
        return []
    return [list(column) for column in zip(*matrix)]


def matmul(left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]) -> list[list[int]]:
    if not left:
        return []
    if not right:
        return [[] for _ in left]
    if len(left[0]) != len(right):
        raise ValueError("incompatible matrix product")
    columns = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) % P for column in columns]
        for row in left
    ]


def add(left: Sequence[Sequence[int]], right: Sequence[Sequence[int]], factor: int = 1) -> list[list[int]]:
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right)):
        raise ValueError("incompatible matrix sum")
    return [
        [(a + factor * b) % P for a, b in zip(row_a, row_b)]
        for row_a, row_b in zip(left, right)
    ]


def solve_columns(matrix: Sequence[Sequence[int]], rhs: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return the canonical free-variables-zero solution of matrix*X=rhs."""

    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("coefficient matrix must be nonempty and square")
    if len(rhs) != size:
        raise ValueError("right side has the wrong height")
    width = len(rhs[0]) if rhs else 0
    if any(len(row) != width for row in rhs):
        raise ValueError("ragged right side")
    augmented = [[*a, *b] for a, b in zip(matrix, rhs)]
    reduced, pivots = rref(augmented, pivot_limit=size)
    for row in reduced:
        if not any(row[:size]) and any(row[size:]):
            raise ValueError("inconsistent linear system")
    answer = [[0] * width for _ in range(size)]
    for row, pivot in enumerate(pivots):
        answer[pivot] = reduced[row][size:]
    return answer


def canonical_solve_operator(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    """Linear operator giving the free-variables-zero solution on col(matrix)."""

    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("coefficient matrix must be nonempty and square")
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
    if a == b or graph[a][b] or graph[b][a]:
        raise ValueError("invalid repeated or loop edge")
    graph[a][b] = graph[b][a] = 1


def local_graph(partition: Sequence[int]) -> list[list[int]]:
    if tuple(partition) not in set(positive_partitions(6)):
        raise ValueError("not a positive partition of six")
    graph = [[0] * 27 for _ in range(27)]
    for a, b in ((0, 1), (0, 2), (1, 2)):
        connect(graph, a, b)
    for vertex in X:
        connect(graph, 0, vertex)
    for vertex in Y:
        connect(graph, 1, vertex)
    offset = 0
    for part in partition:
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


def matching_component_partition(graph: Sequence[Sequence[int]]) -> tuple[int, ...]:
    remaining = set(X + Y)
    answer: list[int] = []
    while remaining:
        component: set[int] = set()
        stack = [min(remaining)]
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            stack.extend(
                neighbor
                for neighbor in X + Y
                if graph[vertex][neighbor] and neighbor not in component
            )
        remaining.difference_update(component)
        if len(component) % 4:
            raise AssertionError("three-matching component is not a multiple of four")
        answer.append(len(component) // 4)
    return tuple(sorted(answer, reverse=True))


def transported(graph: Sequence[Sequence[int]]) -> list[list[int]]:
    size = len(graph)
    return [
        [
            (1 - int(row == column) - 2 * graph[row][column]) % P
            for column in range(size)
        ]
        for row in range(size)
    ]


def border_matrix(permutation: Sequence[int]) -> list[list[int]]:
    if sorted(permutation) != list(range(12)):
        raise ValueError("border relation is not a permutation")
    matrix = [[1] * 12 for _ in range(27)]
    for column, y_index in enumerate(permutation):
        for row in (2, X[column], Y[y_index]):
            matrix[row][column] = P - 1
    return matrix


def within_z_block(matching: Sequence[tuple[int, int]]) -> list[list[int]]:
    mates: dict[int, int] = {}
    for a, b in matching:
        if a == b or a not in range(12) or b not in range(12):
            raise ValueError("malformed Z matching edge")
        if a in mates or b in mates:
            raise ValueError("Z matching repeats a vertex")
        mates[a] = b
        mates[b] = a
    if len(mates) != 12:
        raise ValueError("Z relation is not a perfect matching")
    return [
        [
            (1 - int(i == j) - 2 * int(mates.get(i) == j)) % P
            for j in range(12)
        ]
        for i in range(12)
    ]


def all_pairings(vertices: tuple[int, ...] = tuple(range(12))) -> Iterator[tuple[tuple[int, int], ...]]:
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        rest = vertices[1:index] + vertices[index + 1 :]
        for tail in all_pairings(rest):
            yield ((first, second), *tail)


def full_block(partition: Sequence[int], permutation: Sequence[int], matching: Sequence[tuple[int, int]]) -> list[list[int]]:
    s = transported(local_graph(partition))
    u = border_matrix(permutation)
    w = within_z_block(matching)
    return [
        [*s[row], *u[row]] for row in range(27)
    ] + [
        [*[u[row][column] for row in range(27)], *w[column]]
        for column in range(12)
    ]


def quotient_data(partition: Sequence[int], permutation: Sequence[int]) -> dict[str, object]:
    s = transported(local_graph(partition))
    u = border_matrix(permutation)
    radical = nullspace(s)
    f = matmul(radical, u)
    # nullspace() expects equations as rows, so its vectors are columns spanning
    # the canonical right kernel of F.
    right_kernel_columns = nullspace(f)
    z = transpose(right_kernel_columns)
    uz = matmul(u, z)
    x = solve_columns(s, uz)
    target = matmul(transpose(uz), x)
    return {
        "S": s,
        "U": u,
        "radical_rows": radical,
        "F": f,
        "F_rank": rank(f),
        "right_kernel_columns": right_kernel_columns,
        "Z": z,
        "target": target,
    }


def partition_context(partition: Sequence[int]) -> dict[str, object]:
    """Precompute all 144 border signatures and pairwise Schur interactions."""

    s = transported(local_graph(partition))
    radical = nullspace(s)
    solve_operator = canonical_solve_operator(s)
    candidates: list[tuple[int, ...]] = []
    signatures: list[tuple[int, ...]] = []
    for i in range(12):
        for j in range(12):
            vector = [1] * 27
            for row in (2, X[i], Y[j]):
                vector[row] = P - 1
            candidates.append(tuple(vector))
            signatures.append(
                tuple(
                    sum(a * b for a, b in zip(radical_row, vector)) % P
                    for radical_row in radical
                )
            )
    candidate_matrix = transpose(candidates)
    interaction = matmul(
        transpose(candidate_matrix),
        matmul(solve_operator, candidate_matrix),
    )
    return {
        "S": s,
        "radical_rows": radical,
        "solve_operator": solve_operator,
        "candidates": candidates,
        "signatures": signatures,
        "interaction": interaction,
    }


def fast_quotient_data(context: dict[str, object], permutation: Sequence[int]) -> dict[str, object]:
    indices = [12 * left + right for left, right in enumerate(permutation)]
    selected_signatures = [context["signatures"][index] for index in indices]
    f = transpose(selected_signatures)
    right_kernel_columns = nullspace(f)
    z = transpose(right_kernel_columns)
    full_target = [
        [context["interaction"][a][b] for b in indices]
        for a in indices
    ]
    target = matmul(transpose(z), matmul(full_target, z))
    if target != transpose(target):
        raise AssertionError("restricted target is not symmetric")
    return {
        "F": f,
        "F_rank": rank(f),
        "right_kernel_columns": right_kernel_columns,
        "Z": z,
        "full_target": full_target,
        "target": target,
    }


def restricted_form(z: Sequence[Sequence[int]], w: Sequence[Sequence[int]]) -> list[list[int]]:
    return matmul(transpose(z), matmul(w, z))


def schur_residual(partition: Sequence[int], permutation: Sequence[int], matching: Sequence[tuple[int, int]]) -> list[list[int]]:
    data = quotient_data(partition, permutation)
    return add(restricted_form(data["Z"], within_z_block(matching)), data["target"], -1)


def canonical_span(vectors: Iterable[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = rref(vectors)
    return tuple(tuple(reduced[row]) for row in range(len(pivots)))


def projective(vector: Sequence[int]) -> tuple[int, ...]:
    first = next((value % P for value in vector if value % P), None)
    if first is None:
        raise ValueError("zero vector has no projective normalization")
    inverse = pow(first, -1, P)
    return tuple((inverse * value) % P for value in vector)


def belongs(vector: Sequence[int], basis: Sequence[Sequence[int]]) -> bool:
    return len(canonical_span([*basis, vector])) == len(basis)


def signature_table(partition: Sequence[int]) -> dict[tuple[int, int], tuple[int, ...]]:
    s = transported(local_graph(partition))
    radical = nullspace(s)
    answer = {}
    for i in range(12):
        for j in range(12):
            u = [1] * 27
            for row in (2, X[i], Y[j]):
                u[row] = P - 1
            answer[(i, j)] = tuple(
                sum(a * b for a, b in zip(radical_row, u)) % P
                for radical_row in radical
            )
    return answer


def generated_spaces(lines: Sequence[tuple[int, ...]], dimension: int) -> list[tuple[tuple[int, ...], ...]]:
    if dimension == 0:
        return [()]
    spaces = {
        canonical_span(generators)
        for generators in itertools.combinations(lines, dimension)
    }
    return sorted(space for space in spaces if len(space) == dimension)


def permutations_in_support(allowed: set[tuple[int, int]]) -> Iterator[tuple[int, ...]]:
    choices = {
        left: tuple(right for right in range(12) if (left, right) in allowed)
        for left in range(12)
    }
    if any(not values for values in choices.values()):
        return
    order = tuple(sorted(range(12), key=lambda left: (len(choices[left]), left)))
    assignment = [-1] * 12

    def visit(depth: int, used: int) -> Iterator[tuple[int, ...]]:
        if depth == 12:
            yield tuple(assignment)
            return
        left = order[depth]
        for right in choices[left]:
            bit = 1 << right
            if used & bit:
                continue
            assignment[left] = right
            yield from visit(depth + 1, used | bit)
        assignment[left] = -1

    yield from visit(0, 0)


def minimum_f_permutations(partition: Sequence[int]) -> tuple[int, list[tuple[int, ...]], dict[str, int]]:
    signatures = signature_table(partition)
    even_parts = sum(part % 2 == 0 for part in partition)
    lines = sorted({projective(v) for v in signatures.values() if any(v)})
    spaces = generated_spaces(lines, even_parts)
    winners = 0
    permutations: set[tuple[int, ...]] = set()
    for space in spaces:
        allowed = {edge for edge, vector in signatures.items() if belongs(vector, space)}
        found = list(permutations_in_support(allowed))
        if found:
            winners += 1
            permutations.update(found)
    for permutation in permutations:
        if rank([signatures[(left, right)] for left, right in enumerate(permutation)]) != even_parts:
            raise AssertionError("minimum-F enumeration emitted wrong-rank permutation")
    return even_parts, sorted(permutations), {
        "observed_projective_lines": len(lines),
        "candidate_subspaces": len(spaces),
        "winning_subspaces": winners,
    }


def matrix_key(matrix: Sequence[Sequence[int]]) -> bytes:
    return bytes(value % P for row in matrix for value in row)


def symmetric_extension(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    """Symmetrize without changing the form induced on any admissible kernel."""

    inverse_two = pow(2, -1, P)
    return [
        [
            inverse_two * (matrix[i][j] + matrix[j][i]) % P
            for j in range(len(matrix))
        ]
        for i in range(len(matrix))
    ]


def valid_w_block(matrix: Sequence[Sequence[int]]) -> bool:
    if len(matrix) != 12 or any(len(row) != 12 for row in matrix):
        return False
    if matrix != transpose(matrix):
        return False
    if any(matrix[i][i] != 0 for i in range(12)):
        return False
    mates = []
    for i in range(12):
        if any(matrix[i][j] not in (1, P - 1) for j in range(12) if i != j):
            return False
        row_mates = [j for j in range(12) if i != j and matrix[i][j] == P - 1]
        if len(row_mates) != 1:
            return False
        mates.append(row_mates[0])
    return all(mates[mates[i]] == i for i in range(12))


def rank_one_candidate_w_blocks(
    context: dict[str, object], permutation: Sequence[int]
) -> tuple[list[list[list[int]]], dict[str, object]]:
    """Reconstruct every possible W from the mate of one pivot coordinate.

    If c spans row(F), equality of the two forms on ker(c) is tested in the
    basis e_i-c_i e_p.  Every perfect matching is in exactly one of the eleven
    branches according to the mate of p; the remaining W entries are then
    forced by the form equations.
    """

    indices = [12 * left + right for left, right in enumerate(permutation)]
    selected_signatures = [context["signatures"][index] for index in indices]
    first_signature = next((vector for vector in selected_signatures if any(vector)), None)
    if first_signature is None:
        raise ValueError("rank-one reconstruction received rank-zero F")
    signature_pivot = next(i for i, value in enumerate(first_signature) if value)
    line_scale = pow(first_signature[signature_pivot], -1, P)
    line = tuple(line_scale * value % P for value in first_signature)
    if any(
        any(vector)
        and projective(vector) != line
        for vector in selected_signatures
    ):
        raise ValueError("rank-one reconstruction requires rank(F)=1")
    c = [vector[signature_pivot] % P for vector in selected_signatures]
    pivot = next(i for i, value in enumerate(c) if value)
    scale = pow(c[pivot], -1, P)
    c = [(scale * value) % P for value in c]
    raw_target = [
        [context["interaction"][a][b] for b in indices]
        for a in indices
    ]
    target = symmetric_extension(raw_target)
    free = [i for i in range(12) if i != pivot]
    z = [
        [
            (P - c[column]) % P if row == pivot else int(row == column)
            for column in free
        ]
        for row in range(12)
    ]
    q = {
        (i, j): (
            target[i][j]
            - c[j] * target[i][pivot]
            - c[i] * target[pivot][j]
            + c[i] * c[j] * target[pivot][pivot]
        ) % P
        for i in free
        for j in free
    }
    candidates: list[list[list[int]]] = []
    diagonal_survivors = 0
    for mate in free:
        w_to_pivot = {
            i: (P - 1 if i == mate else 1)
            for i in free
        }
        if any(
            q[(i, i)] != (-2 * c[i] * w_to_pivot[i]) % P
            for i in free
        ):
            continue
        diagonal_survivors += 1
        w = [[0] * 12 for _ in range(12)]
        for i in free:
            w[i][pivot] = w[pivot][i] = w_to_pivot[i]
        for left_index, i in enumerate(free):
            for j in free[left_index + 1 :]:
                value = (
                    q[(i, j)]
                    + c[j] * w_to_pivot[i]
                    + c[i] * w_to_pivot[j]
                ) % P
                w[i][j] = w[j][i] = value
        if valid_w_block(w):
            candidates.append(w)
    return candidates, {
        "mate_branches": 11,
        "matchings_partitioned": 10395,
        "matchings_per_mate_branch": 945,
        "diagonal_survivors": diagonal_survivors,
        "valid_W_candidates": len(candidates),
        "canonical_kernel_pivot": pivot,
        "canonical_kernel_dimension": 11,
        "canonical_right_kernel_sha256": hashlib.sha256(
            matrix_key(z)
        ).hexdigest(),
        "canonical_kernel_target_sha256": hashlib.sha256(
            bytes(c) + bytes(q[(i, j)] for i in free for j in free)
        ).hexdigest(),
    }


def pairing_index_data() -> tuple[list[tuple[int, int]], list[tuple[int, ...]], set[bytes]]:
    edges = list(itertools.combinations(range(12), 2))
    edge_to_index = {edge: index for index, edge in enumerate(edges)}
    pairing_indices: list[tuple[int, ...]] = []
    w_keys: set[bytes] = set()
    for pairing in all_pairings():
        pairing_indices.append(tuple(edge_to_index[edge] for edge in pairing))
        w_keys.add(matrix_key(within_z_block(pairing)))
    if len(pairing_indices) != 10395 or len(w_keys) != 10395:
        raise AssertionError("perfect-matching universe is incomplete or duplicated")
    return edges, pairing_indices, w_keys


def packed_upper(matrix: Sequence[Sequence[int]]) -> tuple[int, ...]:
    return tuple(
        matrix[i][j] % P
        for i in range(len(matrix))
        for j in range(i, len(matrix))
    )


def pairing_target_hits_numpy(
    z: Sequence[Sequence[int]],
    target: Sequence[Sequence[int]],
    edges: Sequence[tuple[int, int]],
    pairing_indices: Sequence[Sequence[int]],
) -> int:
    """Count exact matching-form hits with an independently vectorized census."""

    import numpy as np

    z_array = np.asarray(z, dtype=np.int16)
    sums = z_array.sum(axis=0, dtype=np.int16)
    base_matrix = np.outer(sums, sums) - z_array.T @ z_array
    upper = np.triu_indices(z_array.shape[1])
    base = np.asarray(base_matrix[upper] % P, dtype=np.int16)
    contributions = []
    for i, j in edges:
        zi = z_array[i]
        zj = z_array[j]
        contribution = -2 * (np.outer(zi, zj) + np.outer(zj, zi))
        contributions.append(np.asarray(contribution[upper] % P, dtype=np.int16))
    contribution_array = np.asarray(contributions, dtype=np.int16)
    pairing_array = np.asarray(pairing_indices, dtype=np.int16)
    values = (
        base[None, :]
        + contribution_array[pairing_array].sum(axis=1, dtype=np.int16)
    ) % P
    wanted = np.asarray(packed_upper(target), dtype=np.int16)
    return int(np.all(values == wanted[None, :], axis=1).sum())


def maximum_bipartite_matching(
    edges: Iterable[tuple[int, int]]
) -> tuple[int, list[tuple[int, int]]]:
    neighbors = {left: [] for left in range(12)}
    for left, right in sorted(set(edges)):
        if left not in range(12) or right not in range(12):
            raise ValueError("bipartite edge outside 12 by 12 universe")
        neighbors[left].append(right)
    owners: dict[int, int] = {}

    def augment(left: int, visited: set[int]) -> bool:
        for right in neighbors[left]:
            if right in visited:
                continue
            visited.add(right)
            if right not in owners or augment(owners[right], visited):
                owners[right] = left
                return True
        return False

    size = sum(augment(left, set()) for left in range(12))
    return size, sorted((left, right) for right, left in owners.items())


def partition_from_two_matchings(
    second: Sequence[tuple[int, int]]
) -> tuple[int, ...]:
    fixed = tuple((2 * index, 2 * index + 1) for index in range(6))
    adjacency = {vertex: [] for vertex in range(12)}
    for left, right in (*fixed, *second):
        adjacency[left].append(right)
        adjacency[right].append(left)
    remaining = set(range(12))
    parts: list[int] = []
    while remaining:
        component: set[int] = set()
        stack = [min(remaining)]
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            stack.extend(
                neighbor
                for neighbor in adjacency[vertex]
                if neighbor not in component
            )
        remaining.difference_update(component)
        if len(component) % 2:
            raise AssertionError("two-matching component has odd order")
        parts.append(len(component) // 2)
    return tuple(sorted(parts, reverse=True))


def matching_partition_census() -> dict[str, int]:
    census = Counter(partition_from_two_matchings(pairing) for pairing in all_pairings())
    return {
        "+".join(map(str, partition)): census[partition]
        for partition in positive_partitions(6)
    }


def all_odd_schur_audit(
    partition: Sequence[int], matching_w_keys: set[bytes]
) -> dict[str, object]:
    context = partition_context(partition)
    allowed = {
        (left, right)
        for left in range(12)
        for right in range(12)
        if context["interaction"][12 * left + right][12 * left + right] == 0
    }
    matching_size, witness = maximum_bipartite_matching(allowed)
    zero_diagonal_permutations = list(permutations_in_support(allowed))
    exact_w_hits = 0
    candidate_records = []
    for permutation in zero_diagonal_permutations:
        data = fast_quotient_data(context, permutation)
        if data["F_rank"] != 0:
            raise AssertionError("all-odd type unexpectedly has nonzero F")
        target = data["target"]
        hit = int(matrix_key(target) in matching_w_keys)
        exact_w_hits += hit
        candidate_records.append(
            {
                "permutation": list(permutation),
                "target_sha256": hashlib.sha256(matrix_key(target)).hexdigest(),
                "target_diagonal": [target[i][i] for i in range(12)],
                "off_diagonal_values": sorted(
                    {target[i][j] for i in range(12) for j in range(i)}
                ),
                "off_diagonal_values_outside_W_alphabet": sum(
                    target[i][j] not in (1, P - 1)
                    for i in range(12)
                    for j in range(i)
                ),
                "matching_W_hit": bool(hit),
            }
        )
    return {
        "partition": list(partition),
        "zero_diagonal_allowed_edges": len(allowed),
        "left_degree_sequence": [
            sum((left, right) in allowed for right in range(12))
            for left in range(12)
        ],
        "maximum_zero_diagonal_matching": matching_size,
        "maximum_matching_witness": [list(edge) for edge in witness],
        "zero_diagonal_permutation_count": len(zero_diagonal_permutations),
        "zero_diagonal_candidates": candidate_records,
        "exact_W_hits_among_10395": exact_w_hits,
        "rank_25_completion_exists": bool(exact_w_hits),
    }


def first_canonical_record(
    context: dict[str, object], permutation: Sequence[int]
) -> dict[str, object]:
    data = fast_quotient_data(context, permutation)
    return {
        "permutation": list(permutation),
        "F_rank": data["F_rank"],
        "right_kernel_columns": [
            list(column) for column in data["right_kernel_columns"]
        ],
        "target": data["target"],
        "right_kernel_sha256": hashlib.sha256(matrix_key(data["Z"])).hexdigest(),
        "target_sha256": hashlib.sha256(matrix_key(data["target"])).hexdigest(),
    }


def even_partition_audit(
    partition: Sequence[int],
    edges: Sequence[tuple[int, int]],
    pairing_indices: Sequence[Sequence[int]],
) -> dict[str, object]:
    even_parts, permutations, subspace_census = minimum_f_permutations(partition)
    if even_parts == 0:
        raise ValueError("even-partition audit received an all-odd partition")
    context = partition_context(partition)
    permutation_stream = hashlib.sha256()
    kernel_target_stream = hashlib.sha256()
    unique_kernel_targets: set[bytes] = set()
    unique_right_kernels: set[bytes] = set()
    hit_distribution: Counter[int] = Counter()
    diagonal_survivor_distribution: Counter[int] = Counter()
    total_hits = 0
    first = first_canonical_record(context, permutations[0])
    if even_parts == 1:
        for permutation in permutations:
            permutation_stream.update(bytes(permutation))
            candidates, meta = rank_one_candidate_w_blocks(context, permutation)
            hits = len(candidates)
            total_hits += hits
            hit_distribution[hits] += 1
            diagonal_survivor_distribution[meta["diagonal_survivors"]] += 1
            digest = bytes.fromhex(meta["canonical_kernel_target_sha256"])
            kernel_target_stream.update(bytes(permutation) + digest)
            unique_kernel_targets.add(digest)
            unique_right_kernels.add(
                bytes.fromhex(meta["canonical_right_kernel_sha256"])
            )
        method = (
            "Every R is assigned to one of 11 branches by the mate of the "
            "canonical pivot; each branch contains 9!!=945 matchings. "
            "The diagonal kernel-form equations reject every branch."
        )
    else:
        for permutation in permutations:
            permutation_stream.update(bytes(permutation))
            data = fast_quotient_data(context, permutation)
            hits = pairing_target_hits_numpy(
                data["Z"], data["target"], edges, pairing_indices
            )
            total_hits += hits
            hit_distribution[hits] += 1
            payload = matrix_key(data["Z"]) + matrix_key(data["target"])
            digest = hashlib.sha256(payload).digest()
            kernel_target_stream.update(bytes(permutation) + payload + hits.to_bytes(4, "big"))
            unique_kernel_targets.add(digest)
            unique_right_kernels.add(hashlib.sha256(matrix_key(data["Z"])).digest())
        method = (
            "For every minimum-F permutation, vectorize the exact upper "
            "triangle of Z^T W_R Z over all 10,395 enumerated R matchings "
            "and compare entrywise over F7 with the canonical target."
        )
    return {
        "partition": list(partition),
        "even_part_count": even_parts,
        "local_rank_F7": rank(context["S"]),
        "minimum_F_rank": even_parts,
        "minimum_F_permutation_count": len(permutations),
        "minimum_F_subspace_census": subspace_census,
        "minimum_F_permutation_stream_sha256": permutation_stream.hexdigest(),
        "canonical_kernel_target_stream_sha256": kernel_target_stream.hexdigest(),
        "distinct_canonical_right_kernels": len(unique_right_kernels),
        "unique_raw_canonical_kernel_targets": len(unique_kernel_targets),
        "canonical_right_kernel_dimension": 12 - even_parts,
        "first_canonical_right_kernel_target": first,
        "R_matching_count_per_permutation": 10395,
        "R_instances_covered": len(permutations) * 10395,
        "R_coverage_method": method,
        "diagonal_survivor_distribution": {
            str(key): diagonal_survivor_distribution[key]
            for key in sorted(diagonal_survivor_distribution)
        },
        "R_hit_distribution": {
            str(key): hit_distribution[key]
            for key in sorted(hit_distribution)
        },
        "total_rank_25_R_hits": total_hits,
        "rank_25_completion_exists": bool(total_hits),
    }


def decomposition_positive_controls(
    partitions: Sequence[tuple[int, ...]],
    selected_permutations: dict[tuple[int, ...], tuple[int, ...]],
) -> list[dict[str, object]]:
    matching = next(all_pairings())
    controls = []
    for partition in partitions:
        permutation = selected_permutations.get(partition, tuple(range(12)))
        data = quotient_data(partition, permutation)
        residual = add(
            restricted_form(data["Z"], within_z_block(matching)),
            data["target"],
            -1,
        )
        actual = rank(full_block(partition, permutation, matching))
        predicted = rank(data["S"]) + 2 * data["F_rank"] + rank(residual)
        if actual != predicted:
            raise AssertionError("39-block decomposition failed a direct control")
        controls.append(
            {
                "partition": list(partition),
                "permutation": list(permutation),
                "R": [list(edge) for edge in matching],
                "rank_S": rank(data["S"]),
                "rank_F": data["F_rank"],
                "rank_residual": rank(residual),
                "direct_rank_K39": actual,
                "decomposition_rank_K39": predicted,
            }
        )
    return controls


def pairing_search(partition: Sequence[int], permutation: Sequence[int]) -> tuple[int, Counter[int]]:
    data = quotient_data(partition, permutation)
    target_key = matrix_key(data["target"])
    matches = 0
    residual_ranks: Counter[int] = Counter()
    for pairing in all_pairings():
        form = restricted_form(data["Z"], within_z_block(pairing))
        if matrix_key(form) == target_key:
            matches += 1
        residual_ranks[rank(add(form, data["target"], -1))] += 1
    return matches, residual_ranks


def compute() -> dict[str, object]:
    frozen = audit_frozen_inputs()
    partitions = tuple(positive_partitions(6))
    if len(partitions) != 11:
        raise AssertionError("positive partition generator did not yield eleven types")
    edges, pairing_indices, matching_w_keys = pairing_index_data()
    pairing_stream = hashlib.sha256()
    for pairing in all_pairings():
        pairing_stream.update(bytes(value for edge in pairing for value in edge))
    local_types = {}
    for partition in partitions:
        graph = local_graph(partition)
        local_types["+".join(map(str, partition))] = {
            "partition": list(partition),
            "component_partition": list(matching_component_partition(graph)),
            "even_part_count": sum(part % 2 == 0 for part in partition),
            "rank_F7_S": rank(transported(graph)),
        }
    odd_partitions = tuple(
        partition
        for partition in partitions
        if not any(part % 2 == 0 for part in partition)
    )
    even_partitions = tuple(
        partition
        for partition in partitions
        if any(part % 2 == 0 for part in partition)
    )
    all_odd = {
        "+".join(map(str, partition)): all_odd_schur_audit(
            partition, matching_w_keys
        )
        for partition in odd_partitions
    }
    even = {}
    selected_permutations = {}
    for partition in even_partitions:
        entry = even_partition_audit(partition, edges, pairing_indices)
        key = "+".join(map(str, partition))
        even[key] = entry
        selected_permutations[partition] = tuple(
            entry["first_canonical_right_kernel_target"]["permutation"]
        )
    result = {
        "format": "wave41-rank26-secondary-v1",
        "role": "secondary_verifier",
        "verdict": "PASS",
        "claim_label": "VERIFIED",
        "scope": (
            "Universal theorem rank_F7(M)>=26 for every hypothetical "
            "srg(99,14,1,2), via one edge, its triangle mate, and the "
            "mate's complete 12-vertex neighbor fibre."
        ),
        "frozen_inputs": frozen,
        "independence": {
            "wave41_discovery_read_before_checker_and_tests_frozen": False,
            "wave41_primary_verifier_read_before_checker_and_tests_frozen": False,
            "discovery_code_imported_or_executed": False,
            "primary_verifier_code_imported_or_executed": False,
            "automorphism_assumed": False,
            "reason": (
                "The eleven local types come from all 10,395 labelled "
                "two-matching configurations. Every minimum-F border "
                "permutation is enumerated as a labelled permutation, and "
                "the complete labelled R universe is checked without orbit "
                "division."
            ),
        },
        "rank_transport": {
            "premises": [
                "N M N^T=27I-9A+J, hence K=J-I-2A over F7",
                "N^T N M=3M",
                "M is symmetric",
            ],
            "derivation": (
                "Because 3 is invertible in F7, Nv=0 for v in im(M) gives "
                "0=N^T Nv=3v and v=0. Thus N is injective on im(M), so "
                "rank(NM)=rank(M); symmetry gives rank(MN^T)=rank(M), and "
                "injectivity again gives rank(NMN^T)=rank(M). Any principal "
                "rank of K is therefore a lower bound for rank_F7(M)."
            ),
            "conclusion": "rank_F7(K)=rank_F7(M)",
        },
        "partition_completeness": {
            "positive_partitions_of_six": [list(partition) for partition in partitions],
            "partition_count": len(partitions),
            "labelled_matching_count": len(pairing_indices),
            "labelled_matching_stream_sha256": pairing_stream.hexdigest(),
            "partition_census": matching_partition_census(),
            "sum_partition_census": sum(matching_partition_census().values()),
        },
        "local_types": local_types,
        "block_reduction": {
            "block": "K39=[[S,U],[U^T,W_R]] over F7",
            "S_rank": "25-2e for e even parts",
            "F": "F=H^T U, where rows(H) are a basis of ker(S)",
            "Z": "columns(Z) are the canonical right-kernel basis of F",
            "target": (
                "T=Z^T U^T X, where S X=U Z; T is independent of the "
                "chosen solution X"
            ),
            "exact_rank_formula": (
                "rank(K39)=rank(S)+2 rank(F)+rank(Z^T W_R Z-T)"
            ),
            "rank_25_iff": (
                "rank(K39)=25 iff rank(F)=e and Z^T W_R Z=T"
            ),
            "why": (
                "Congruence splits S into an invertible summand and its "
                "radical, leaving [[0,F],[F^T,C]]. A second congruence "
                "splits 2 rank(F) hyperbolic directions and leaves exactly "
                "the restriction of C to ker(F)."
            ),
            "direct_positive_controls": decomposition_positive_controls(
                partitions, selected_permutations
            ),
        },
        "all_odd_schur_obstructions": all_odd,
        "even_partition_audits": even,
        "exhaustive_totals": {
            "all_odd_partition_types": len(all_odd),
            "even_partition_types": len(even),
            "minimum_F_permutations": sum(
                entry["minimum_F_permutation_count"] for entry in even.values()
            ),
            "distinct_canonical_right_kernels": sum(
                entry["distinct_canonical_right_kernels"] for entry in even.values()
            ),
            "distinct_canonical_kernel_targets": sum(
                entry["unique_raw_canonical_kernel_targets"] for entry in even.values()
            ),
            "R_instances_covered_for_even_types": sum(
                entry["R_instances_covered"] for entry in even.values()
            ),
            "rank_25_R_hits": sum(
                entry["total_rank_25_R_hits"] for entry in even.values()
            ),
        },
        "universal_deduction": {
            "inherited_floor": "rank_F7(M)>=25 (Wave 40 VERIFIED)",
            "rank_25_excluded": True,
            "theorem": "rank_F7(M)>=26",
        },
        "status_wall": {
            "universal_rank_F7_M_lower_bound": 26,
            "graph_constructed": False,
            "endpoint_n3_4158_excluded": False,
            "general_upper_bound_improved_below_4158": False,
            "strongest_general_upper_bound": "n3<=4158",
            "conway_99_status": "UNKNOWN",
            "novelty_or_priority": "UNKNOWN",
        },
    }
    validate(result)
    return result


def validate(result: dict[str, object]) -> None:
    if result.get("verdict") != "PASS" or result.get("claim_label") != "VERIFIED":
        raise ValueError("secondary verifier did not pass the scoped theorem")
    completeness = result["partition_completeness"]
    expected_partition_census = {
        "6": 3840,
        "5+1": 2304,
        "4+2": 1440,
        "4+1+1": 720,
        "3+3": 640,
        "3+2+1": 960,
        "3+1+1+1": 160,
        "2+2+2": 120,
        "2+2+1+1": 180,
        "2+1+1+1+1": 30,
        "1+1+1+1+1+1": 1,
    }
    if completeness["partition_count"] != 11:
        raise ValueError("partition coverage is not eleven")
    if completeness["labelled_matching_count"] != 10395:
        raise ValueError("labelled matching universe is incomplete")
    if completeness["partition_census"] != expected_partition_census:
        raise ValueError("labelled matching partition census changed")
    if completeness["sum_partition_census"] != 10395:
        raise ValueError("partition census does not sum to 10,395")
    if set(result["local_types"]) != set(expected_partition_census):
        raise ValueError("local type coverage changed")
    for key, entry in result["local_types"].items():
        if entry["component_partition"] != entry["partition"]:
            raise ValueError(f"local component mismatch for {key}")
        if entry["rank_F7_S"] != 25 - 2 * entry["even_part_count"]:
            raise ValueError(f"local rank formula mismatch for {key}")
    expected_odd = {
        "5+1": (10, 0),
        "3+3": (12, 1),
        "3+1+1+1": (6, 0),
        "1+1+1+1+1+1": (0, 0),
    }
    odd = result["all_odd_schur_obstructions"]
    if set(odd) != set(expected_odd):
        raise ValueError("all-odd case coverage changed")
    for key, (matching_size, candidate_count) in expected_odd.items():
        entry = odd[key]
        if entry["maximum_zero_diagonal_matching"] != matching_size:
            raise ValueError(f"wrong all-odd matching obstruction for {key}")
        if entry["zero_diagonal_permutation_count"] != candidate_count:
            raise ValueError(f"wrong all-odd candidate count for {key}")
        if entry["exact_W_hits_among_10395"] != 0:
            raise ValueError(f"false all-odd rank-25 completion for {key}")
        if entry["rank_25_completion_exists"]:
            raise ValueError(f"all-odd status inflation for {key}")
    expected_even_counts = {
        "6": 2592,
        "4+2": 64,
        "4+1+1": 768,
        "3+2+1": 80640,
        "2+2+2": 32,
        "2+2+1+1": 192,
        "2+1+1+1+1": 80640,
    }
    expected_right_kernels = {
        "6": 2,
        "4+2": 4,
        "4+1+1": 2,
        "3+2+1": 2,
        "2+2+2": 32,
        "2+2+1+1": 8,
        "2+1+1+1+1": 2,
    }
    even = result["even_partition_audits"]
    if set(even) != set(expected_even_counts):
        raise ValueError("even case coverage changed")
    for key, expected_count in expected_even_counts.items():
        entry = even[key]
        if entry["minimum_F_permutation_count"] != expected_count:
            raise ValueError(f"wrong minimum-F count for {key}")
        if entry["distinct_canonical_right_kernels"] != expected_right_kernels[key]:
            raise ValueError(f"wrong canonical right-kernel count for {key}")
        if entry["R_matching_count_per_permutation"] != 10395:
            raise ValueError(f"incomplete R universe for {key}")
        if entry["R_instances_covered"] != expected_count * 10395:
            raise ValueError(f"incomplete R instance count for {key}")
        if entry["R_hit_distribution"] != {"0": expected_count}:
            raise ValueError(f"nonzero or incomplete R hit census for {key}")
        if entry["total_rank_25_R_hits"] != 0:
            raise ValueError(f"rank-25 completion found for {key}")
        if entry["rank_25_completion_exists"]:
            raise ValueError(f"rank-25 status inflation for {key}")
        if entry["canonical_right_kernel_dimension"] != 12 - entry["even_part_count"]:
            raise ValueError(f"wrong right-kernel dimension for {key}")
    for control in result["block_reduction"]["direct_positive_controls"]:
        if control["direct_rank_K39"] != control["decomposition_rank_K39"]:
            raise ValueError("direct 39-block control disagrees with reduction")
    totals = result["exhaustive_totals"]
    if totals != {
        "all_odd_partition_types": 4,
        "even_partition_types": 7,
        "minimum_F_permutations": 164928,
        "distinct_canonical_right_kernels": 52,
        "distinct_canonical_kernel_targets": 164278,
        "R_instances_covered_for_even_types": 1714426560,
        "rank_25_R_hits": 0,
    }:
        raise ValueError("exhaustive totals changed")
    if not result["universal_deduction"]["rank_25_excluded"]:
        raise ValueError("rank 25 was not excluded")
    if result["universal_deduction"]["theorem"] != "rank_F7(M)>=26":
        raise ValueError("wrong universal theorem")
    wall = result["status_wall"]
    if wall["universal_rank_F7_M_lower_bound"] != 26:
        raise ValueError("wrong rank floor")
    if wall["graph_constructed"] or wall["endpoint_n3_4158_excluded"]:
        raise ValueError("graph or endpoint status inflation")
    if wall["general_upper_bound_improved_below_4158"]:
        raise ValueError("general-bound status inflation")
    if wall["strongest_general_upper_bound"] != "n3<=4158":
        raise ValueError("wrong general upper bound")
    if wall["conway_99_status"] != "UNKNOWN":
        raise ValueError("problem-status inflation")
    if wall["novelty_or_priority"] != "UNKNOWN":
        raise ValueError("novelty status inflation")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write and args.verify:
        raise SystemExit("--write and --verify are mutually exclusive")
    fresh = compute()
    if args.write:
        args.write.write_text(
            json.dumps(fresh, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE: {args.write}")
    elif args.verify:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        validate(stored)
        if stored != fresh:
            raise SystemExit("stored result differs from independent replay")
        print(f"VERIFIED: {args.verify}")
    else:
        print(json.dumps(fresh, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
