"""Draft exact checker for Wave164.

This file was prepared under a host-memory pause and has not yet been run.
It uses only the Python standard library and writes no files.
"""

from __future__ import annotations

from itertools import combinations


def adjacency(order: int, edges: set[tuple[int, int]]) -> list[list[int]]:
    matrix = [[0] * order for _ in range(order)]
    for left, right in edges:
        if left == right:
            raise AssertionError("loop")
        left, right = sorted((left, right))
        matrix[left][right] = 1
        matrix[right][left] = 1
    return matrix


def cube() -> list[list[int]]:
    edges = {
        tuple(sorted((vertex, vertex ^ bit)))
        for vertex in range(8)
        for bit in (1, 2, 4)
    }
    return adjacency(8, edges)


def wagner() -> list[list[int]]:
    edges = {
        tuple(sorted((vertex, (vertex + step) % 8)))
        for vertex in range(8)
        for step in (1, 4)
    }
    return adjacency(8, edges)


def cycle5() -> list[list[int]]:
    return adjacency(
        5,
        {
            tuple(sorted((vertex, (vertex + 1) % 5)))
            for vertex in range(5)
        },
    )


def matmul(
    left: list[list[int]], right: list[list[int]]
) -> list[list[int]]:
    return [
        [
            sum(left[row][mid] * right[mid][column] for mid in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix, strict=True)]


def gram_target(graph: list[list[int]]) -> list[list[int]]:
    order = len(graph)
    square = matmul(graph, graph)
    return [
        [
            12 * (row == column)
            - graph[row][column]
            + 2
            - square[row][column]
            for column in range(order)
        ]
        for row in range(order)
    ]


def explicit_factor(target: list[list[int]], outside: int) -> list[list[int]]:
    order = len(target)
    columns: list[list[int]] = []
    for left, right in combinations(range(order), 2):
        for _ in range(target[left][right]):
            column = [0] * order
            column[left] = 1
            column[right] = 1
            columns.append(column)

    used = [sum(column[row] for column in columns) for row in range(order)]
    for row in range(order):
        for _ in range(target[row][row] - used[row]):
            column = [0] * order
            column[row] = 1
            columns.append(column)

    while len(columns) < outside:
        columns.append([0] * order)
    if len(columns) != outside:
        raise AssertionError("factor uses too many columns")
    return transpose(columns)


def edges_of(graph: list[list[int]]) -> set[tuple[int, int]]:
    return {
        (left, right)
        for left, right in combinations(range(len(graph)), 2)
        if graph[left][right]
    }


def assert_cubic_triangle_free(graph: list[list[int]]) -> None:
    assert len(graph) == 8
    assert len(edges_of(graph)) == 12
    assert all(sum(row) == 3 for row in graph)
    for triple in combinations(range(8), 3):
        assert sum(graph[left][right] for left, right in combinations(triple, 2)) < 3


def assert_matching_supports(
    graph: list[list[int]], factor: list[list[int]]
) -> None:
    for column in zip(*factor, strict=True):
        support = [index for index, value in enumerate(column) if value]
        degrees = {
            vertex: sum(graph[vertex][other] for other in support)
            for vertex in support
        }
        assert all(degree <= 1 for degree in degrees.values())


def induced_cycle5_count(graph: list[list[int]]) -> int:
    count = 0
    for subset in combinations(range(len(graph)), 5):
        degrees = [
            sum(graph[vertex][other] for other in subset)
            for vertex in subset
        ]
        if degrees == [2] * 5:
            count += 1
    return count


def check_eight_vertex_graph(graph: list[list[int]], name: str) -> dict[str, object]:
    assert_cubic_triangle_free(graph)
    target = gram_target(graph)
    factor = explicit_factor(target, 91)
    assert matmul(factor, transpose(factor)) == target
    assert_matching_supports(graph, factor)
    off_diagonal_sum = sum(
        target[left][right] for left, right in combinations(range(8), 2)
    )
    assert off_diagonal_sum == 20
    assert all(target[index][index] == 11 for index in range(8))
    assert all(sum(target[index]) - 11 == 5 for index in range(8))
    return {
        "name": name,
        "edges": 12,
        "factor_shape": [8, 91],
        "pair_columns": 20,
        "singleton_columns": 48,
        "zero_columns": 23,
        "incidence_profile": {"size_2": 12, "size_1": 32, "size_0": 187},
        "induced_cycle5_count": induced_cycle5_count(graph),
    }


def main() -> None:
    cube_result = check_eight_vertex_graph(cube(), "cube")
    wagner_result = check_eight_vertex_graph(wagner(), "wagner")
    assert cube_result["induced_cycle5_count"] == 0
    assert wagner_result["induced_cycle5_count"] == 8

    c5 = cycle5()
    c5_target = gram_target(c5)
    expected = [
        [12 if row == column else 1 for column in range(5)]
        for row in range(5)
    ]
    assert c5_target == expected
    c5_factor = explicit_factor(c5_target, 94)
    assert matmul(c5_factor, transpose(c5_factor)) == c5_target
    assert_matching_supports(c5, c5_factor)

    print(
        {
            "claim_label": "DRAFT_CHECK_PASSED_NOT_INDEPENDENTLY_VERIFIED",
            "cube": cube_result,
            "wagner": wagner_result,
            "c5_factor_shape": [5, 94],
            "global_status": "UNKNOWN",
        }
    )


if __name__ == "__main__":
    main()
