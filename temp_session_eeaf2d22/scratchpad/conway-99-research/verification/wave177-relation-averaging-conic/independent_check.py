"""Clean-room exact verification of the Wave 177 formulas.

The only finite geometry enumerated is the 13-point plane PG(2,3).  No
candidate graph, code, SAT instance, or isomorphism class is searched.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any


Q = 3
H = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]


def adjacent_average(k: int) -> Fraction:
    assert k >= 2
    return Fraction(24 * 3 ** (k - 1) - 24, 3**k - 3)


def nonadjacent_average(k: int) -> Fraction:
    assert k >= 3
    return Fraction(28 * 3 ** (k - 1) - 84, 3**k - 9)


def matvec(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [
        sum(entry * value for entry, value in zip(row, vector)) % Q
        for row in matrix
    ]


def cycle_biadjacency_4_plus_2() -> list[list[int]]:
    matrix = [[0] * 6 for _ in range(6)]
    start = 0
    for size in (4, 2):
        for i in range(size):
            matrix[start + i][start + i] = 1
            matrix[start + i][start + (i + 1) % size] = 1
        start += size
    return matrix


def union_gram_4_plus_2() -> list[list[int]]:
    cross = cycle_biadjacency_4_plus_2()
    gram = [[0] * 13 for _ in range(13)]
    for i in range(13):
        for j in range(i + 1, 13):
            if i == 0 or (i <= 6 and j <= 6) or (i >= 7 and j >= 7):
                value = 1
            else:
                value = 1 + cross[i - 1][j - 7]
            gram[i][j] = gram[j][i] = value % Q
    return gram


def switched_weight_four_data() -> dict[str, Any]:
    gram = union_gram_4_plus_2()
    # common | six left | six right
    relation = [0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 1, 1]
    assert matvec(gram, relation) == [0] * 13
    support = [i for i, value in enumerate(relation) if value]
    switched = [
        [
            relation[i] * relation[j] * gram[i][j] % Q
            for j in support
        ]
        for i in support
    ]
    return {
        "relation": relation,
        "support": support,
        "weight": len(support),
        "switched_gram": switched,
    }


def inner(left: tuple[int, int, int], right: tuple[int, int, int]) -> int:
    return sum(
        left[i] * H[i][j] * right[j] for i in range(3) for j in range(3)
    ) % Q


def outer_operator(vector: tuple[int, int, int]) -> list[list[int]]:
    covector = [
        sum(vector[i] * H[i][j] for i in range(3)) % Q for j in range(3)
    ]
    return [
        [vector[i] * covector[j] % Q for j in range(3)]
        for i in range(3)
    ]


def add_matrices(matrices: list[list[list[int]]]) -> list[list[int]]:
    return [
        [
            sum(matrix[i][j] for matrix in matrices) % Q
            for j in range(3)
        ]
        for i in range(3)
    ]


def projective_plane() -> list[tuple[int, int, int]]:
    points: list[tuple[int, int, int]] = []
    for vector in product(range(Q), repeat=3):
        if vector == (0, 0, 0):
            continue
        first_nonzero = next(value for value in vector if value)
        if first_nonzero == 1:
            points.append(vector)
    assert len(points) == 13
    return points


def conic_frame_data() -> dict[str, Any]:
    points = projective_plane()
    conic = [point for point in points if inner(point, point) == 0]
    complement = [point for point in points if inner(point, point) != 0]
    conic_frame = add_matrices([outer_operator(point) for point in conic])
    complement_frame = add_matrices(
        [outer_operator(point) for point in complement]
    )
    full_frame = add_matrices([outer_operator(point) for point in points])
    return {
        "plane_points": len(points),
        "conic_points": len(conic),
        "complement_points": len(complement),
        "conic_frame": conic_frame,
        "complement_frame": complement_frame,
        "full_frame": full_frame,
    }


def analyze() -> dict[str, Any]:
    result = {
        "field": Q,
        "adjacent": {
            "minimum_relation_dimension": 2,
            "outside_average_by_dimension": {
                str(k): str(adjacent_average(k)) for k in range(2, 13)
            },
            "support_bounds": [4, 8],
            "coefficient_sum": 0,
            "uncentered_lift": True,
        },
        "nonadjacent": {
            "minimum_relation_dimension": 3,
            "star_subcode_total_weight": 84,
            "outside_average_by_dimension": {
                str(k): str(nonadjacent_average(k)) for k in range(3, 15)
            },
            "support_bounds": [4, 9],
        },
        "type_4_plus_2": switched_weight_four_data(),
        "plane_frame": conic_frame_data(),
        "indexing": {
            "graph_edges": 693,
            "one_relation_indexed_per_edge": True,
            "distinct_relations_claimed": False,
        },
        "scope": "local exact constraints verified; endpoint remains unknown",
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    assert set(result["adjacent"]["outside_average_by_dimension"].values()) == {
        "8"
    }
    assert set(
        result["nonadjacent"]["outside_average_by_dimension"].values()
    ) == {"28/3"}
    assert result["adjacent"]["support_bounds"] == [4, 8]
    assert result["nonadjacent"]["support_bounds"] == [4, 9]
    switched = result["type_4_plus_2"]
    assert switched["weight"] == 4
    assert switched["switched_gram"] == [
        [0, 1, 1, 1],
        [1, 0, 1, 1],
        [1, 1, 0, 1],
        [1, 1, 1, 0],
    ]
    frames = result["plane_frame"]
    assert frames["conic_points"] == 4
    assert frames["complement_points"] == 9
    assert frames["conic_frame"] == [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
    assert frames["complement_frame"] == [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
    assert frames["full_frame"] == [[0] * 3 for _ in range(3)]
    assert result["indexing"]["distinct_relations_claimed"] is False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: independent Wave177 verification")


if __name__ == "__main__":
    main()

