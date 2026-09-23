#!/usr/bin/env python3
"""Clean-room six-vertex checks for Reimbayev (2024).

This standard-library script enumerates every labeled graph on six vertices,
canonicalizes under S_6, applies the necessary induced-subgraph common-neighbor
bounds for an srg(v,k,1,2), and checks the determinant-plus-perfect-matching
coefficient used in the paper's characteristic-polynomial identity.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, permutations


ORDER = 6
EDGES = tuple(combinations(range(ORDER), 2))
EDGE_INDEX = {edge: index for index, edge in enumerate(EDGES)}
PERMUTATIONS = tuple(permutations(range(ORDER)))


def permute_mask(mask: int, permutation: tuple[int, ...]) -> int:
    result = 0
    for bit, (first, second) in enumerate(EDGES):
        if mask >> bit & 1:
            image = tuple(sorted((permutation[first], permutation[second])))
            result |= 1 << EDGE_INDEX[image]
    return result


def canonical(mask: int) -> int:
    return min(permute_mask(mask, permutation) for permutation in PERMUTATIONS)


def adjacency(mask: int) -> list[list[int]]:
    matrix = [[0] * ORDER for _ in range(ORDER)]
    for bit, (first, second) in enumerate(EDGES):
        if mask >> bit & 1:
            matrix[first][second] = matrix[second][first] = 1
    return matrix


def compatible(mask: int) -> bool:
    matrix = adjacency(mask)
    for first, second in EDGES:
        common = sum(
            matrix[first][third] and matrix[second][third]
            for third in range(ORDER)
        )
        if common > (1 if matrix[first][second] else 2):
            return False
    return True


def connected(mask: int) -> bool:
    matrix = adjacency(mask)
    seen = {0}
    stack = [0]
    while stack:
        first = stack.pop()
        for second in range(ORDER):
            if matrix[first][second] and second not in seen:
                seen.add(second)
                stack.append(second)
    return len(seen) == ORDER


def determinant(matrix: list[list[int]]) -> int:
    """Return an exact determinant using Bareiss elimination."""

    work = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for column in range(len(work) - 1):
        if work[column][column] == 0:
            pivot = next(
                (
                    row
                    for row in range(column + 1, len(work))
                    if work[row][column]
                ),
                None,
            )
            if pivot is None:
                return 0
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        for row in range(column + 1, len(work)):
            for inner in range(column + 1, len(work)):
                work[row][inner] = (
                    work[row][inner] * pivot_value
                    - work[row][column] * work[column][inner]
                ) // previous
        previous = pivot_value
    return sign * work[-1][-1]


def perfect_matchings(mask: int) -> int:
    matrix = adjacency(mask)

    def recurse(vertices: tuple[int, ...]) -> int:
        if not vertices:
            return 1
        first = vertices[0]
        return sum(
            recurse(vertices[1:index] + vertices[index + 1 :])
            for index, second in enumerate(vertices[1:], 1)
            if matrix[first][second]
        )

    return recurse(tuple(range(ORDER)))


def mask_from_edges(edges: list[tuple[int, int]]) -> int:
    mask = 0
    for first, second in edges:
        mask |= 1 << EDGE_INDEX[tuple(sorted((first, second)))]
    return mask


def coefficient(mask: int) -> int:
    return determinant(adjacency(mask)) + perfect_matchings(mask)


def characteristic_prefix(eigenvalues: list[int], degree: int) -> list[int]:
    coefficients = [1]
    for value in eigenvalues:
        updated = [0] * min(len(coefficients) + 1, degree + 1)
        for index, coefficient_value in enumerate(coefficients):
            updated[index] += coefficient_value
            if index + 1 < len(updated):
                updated[index + 1] -= value * coefficient_value
        coefficients = updated
    return coefficients


def main() -> int:
    representatives = {
        canonical(mask) for mask in range(1 << len(EDGES))
    }
    allowed = sorted(mask for mask in representatives if compatible(mask))
    connected_allowed = [mask for mask in allowed if connected(mask)]
    nonzero = [mask for mask in allowed if coefficient(mask)]

    coefficient_distribution = sorted(Counter(map(coefficient, nonzero)).items())
    print("unlabeled_graphs", len(representatives))
    print("compatible_unlabeled", len(allowed))
    print("compatible_connected", len(connected_allowed))
    print("nonzero_det_plus_pm", len(nonzero))
    print("nonzero_connected", sum(connected(mask) for mask in nonzero))
    print("coefficient_distribution", coefficient_distribution)

    cycle6 = mask_from_edges([(index, (index + 1) % 6) for index in range(6)])
    k2_plus_c4 = mask_from_edges(
        [(0, 1), (2, 3), (3, 4), (4, 5), (5, 2)]
    )
    two_k3 = mask_from_edges(
        [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)]
    )

    vertices, degree = 99, 14
    base = (
        vertices
        * degree
        * (degree - 2)
        * (2 * degree**2 - 21 * degree + 53)
        // 12
    )
    relation_rhs = vertices * degree * (degree - 2) // 4
    characteristic = characteristic_prefix([degree] + [3] * 54 + [-4] * 44, 6)

    assert len(representatives) == 156
    assert len(allowed) == 62
    assert len(connected_allowed) == 33
    assert len(nonzero) == 14
    assert sum(connected(mask) for mask in nonzero) == 12
    assert coefficient_distribution == [(-2, 3), (2, 8), (4, 3)]
    assert coefficient(cycle6) == -2
    assert coefficient(k2_plus_c4) == 2
    assert coefficient(two_k3) == 4
    assert base == 209_286
    assert relation_rhs == 4_158
    assert characteristic[6] == -47_288_703

    print("target_hexagon_base", base)
    print("target_relation_3n1_plus_n3", relation_rhs)
    print("target_characteristic_c6", characteristic[6])
    print("PASS Reimbayev six-vertex clean-room checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
