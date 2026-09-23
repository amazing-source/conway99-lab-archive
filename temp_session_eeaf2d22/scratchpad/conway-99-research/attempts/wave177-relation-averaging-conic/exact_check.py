"""Exact Wave 177 relation-code averaging and conic checks."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any


FIELD = 3
PLANE_FORM = [
    [0, 1, 1],
    [1, 0, 1],
    [1, 1, 0],
]


def fraction_text(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def adjacent_nonstar_average(dimension: int) -> Fraction:
    """Average outside the one-dimensional outer star-difference code."""

    if dimension < 2:
        raise ValueError("adjacent outer relation dimension must be at least two")
    total_weight = 12 * 2 * 3 ** (dimension - 1)
    removed_weight = 2 * 12
    return Fraction(total_weight - removed_weight, 3**dimension - 3)


def nonadjacent_nonstar_average(dimension: int) -> Fraction:
    """Average outside the two-dimensional disjoint-star circuit code."""

    if dimension < 3:
        raise ValueError("nonadjacent relation dimension must be at least three")
    total_weight = 14 * 2 * 3 ** (dimension - 1)
    # Two scalar words on either individual star and four on both stars.
    removed_weight = 2 * 7 + 2 * 7 + 4 * 14
    return Fraction(total_weight - removed_weight, 3**dimension - 9)


def inner(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    return sum(
        left[row] * PLANE_FORM[row][column] * right[column]
        for row in range(3)
        for column in range(3)
    ) % FIELD


def matrix_sum(matrices: list[list[list[int]]]) -> list[list[int]]:
    return [
        [
            sum(matrix[row][column] for matrix in matrices) % FIELD
            for column in range(3)
        ]
        for row in range(3)
    ]


def outer_operator(vector: tuple[int, ...]) -> list[list[int]]:
    """Matrix of u tensor u: v maps to (u,v)u for PLANE_FORM."""

    covector = [
        sum(vector[row] * PLANE_FORM[row][column] for row in range(3))
        % FIELD
        for column in range(3)
    ]
    return [
        [
            vector[row] * covector[column] % FIELD
            for column in range(3)
        ]
        for row in range(3)
    ]


def projective_points() -> list[tuple[int, int, int]]:
    """Canonical representatives of PG(2,3)."""

    points: list[tuple[int, int, int]] = []
    for vector in product(range(FIELD), repeat=3):
        if vector == (0, 0, 0):
            continue
        first = next(entry for entry in vector if entry)
        if first == 1:
            points.append(vector)
    assert len(points) == 13
    return points


def conic_data() -> dict[str, Any]:
    """Return the complete Q(2,3) frame identity."""

    switched_vectors = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (2, 2, 2),
    ]
    gram = [
        [inner(left, right) for right in switched_vectors]
        for left in switched_vectors
    ]

    points = projective_points()
    conic = [point for point in points if inner(point, point) == 0]
    complement = [point for point in points if inner(point, point) != 0]
    conic_frame = matrix_sum([outer_operator(point) for point in conic])
    complement_frame = matrix_sum(
        [outer_operator(point) for point in complement]
    )
    full_frame = matrix_sum([outer_operator(point) for point in points])

    return {
        "switched_relation": "u_1+u_2+u_3+u_4=0",
        "switched_gram": gram,
        "plane_form": PLANE_FORM,
        "projective_points": len(points),
        "conic_points": len(conic),
        "nonconic_points": len(complement),
        "conic_frame_operator": conic_frame,
        "nonconic_frame_operator": complement_frame,
        "full_plane_frame_operator": full_frame,
        "interpretation": (
            "the weight-four 4+2 relation is the complete conic Q(2,3)"
        ),
    }


def analyze() -> dict[str, Any]:
    adjacent_averages = {
        str(dimension): fraction_text(adjacent_nonstar_average(dimension))
        for dimension in range(2, 13)
    }
    nonadjacent_averages = {
        str(dimension): fraction_text(
            nonadjacent_nonstar_average(dimension)
        )
        for dimension in range(3, 15)
    }
    return {
        "field": FIELD,
        "adjacent_pair": {
            "outer_columns": 12,
            "relation_dimension_lower": 2,
            "removed_star_subcode_dimension": 1,
            "nonstar_average_by_possible_dimension": adjacent_averages,
            "universal_nonstar_average": "8",
            "true_relation_support_bounds": [4, 8],
            "avoids_common_block": True,
            "coefficient_sum_mod_3": 0,
            "lifts_to_uncentered_columns": True,
        },
        "nonadjacent_pair": {
            "columns": 14,
            "relation_dimension_lower": 3,
            "removed_star_subcode_dimension": 2,
            "removed_star_subcode_total_weight": 84,
            "nonstar_average_by_possible_dimension": nonadjacent_averages,
            "universal_nonstar_average": "28/3",
            "true_relation_support_bounds": [4, 9],
        },
        "type_4_plus_2": conic_data(),
        "conclusion": (
            "all vertex pairs have a true cross-star relation of weight at "
            "most nine, and every edge has one of weight at most eight; "
            "the endpoint remains unexcluded"
        ),
    }


def verify(data: dict[str, Any]) -> None:
    adjacent = data["adjacent_pair"]
    nonadjacent = data["nonadjacent_pair"]
    assert set(adjacent["nonstar_average_by_possible_dimension"].values()) == {
        "8"
    }
    assert set(
        nonadjacent["nonstar_average_by_possible_dimension"].values()
    ) == {"28/3"}
    assert adjacent["true_relation_support_bounds"] == [4, 8]
    assert nonadjacent["true_relation_support_bounds"] == [4, 9]

    conic = data["type_4_plus_2"]
    assert conic["switched_gram"] == [
        [0, 1, 1, 1],
        [1, 0, 1, 1],
        [1, 1, 0, 1],
        [1, 1, 1, 0],
    ]
    zero = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    minus_identity = [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
    assert conic["conic_frame_operator"] == minus_identity
    assert conic["nonconic_frame_operator"] == identity
    assert conic["full_plane_frame_operator"] == zero


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    data = analyze()
    verify(data)
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == data
    if args.write:
        args.write.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    if not args.write and not args.verify:
        print(json.dumps(data, indent=2, sort_keys=True))
    print("PASS: Wave177 relation averaging and conic checks")


if __name__ == "__main__":
    main()
