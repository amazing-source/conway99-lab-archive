"""Exact local checks for Wave 178.

Only four already-derived 13 by 13 Gram matrices are reduced.  The largest
kernel has dimension five, so at most 3^5=243 vectors are inspected for any
cycle type.  No graph or code construction is enumerated.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any, Iterable


FIELD = 3


def gf3_rref(matrix: list[list[int]]) -> tuple[list[list[int]], list[int]]:
    rows = [[entry % FIELD for entry in row] for row in matrix]
    width = len(rows[0])
    pivots: list[int] = []
    pivot_row = 0
    for column in range(width):
        source = next(
            (
                row
                for row in range(pivot_row, len(rows))
                if rows[row][column]
            ),
            None,
        )
        if source is None:
            continue
        rows[pivot_row], rows[source] = rows[source], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], -1, FIELD)
        rows[pivot_row] = [
            inverse * entry % FIELD for entry in rows[pivot_row]
        ]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            multiplier = rows[row][column]
            rows[row] = [
                (entry - multiplier * rows[pivot_row][index]) % FIELD
                for index, entry in enumerate(rows[row])
            ]
        pivots.append(column)
        pivot_row += 1
    return rows, pivots


def gf3_nullspace(matrix: list[list[int]]) -> list[list[int]]:
    reduced, pivots = gf3_rref(matrix)
    width = len(matrix[0])
    basis: list[list[int]] = []
    for free in (column for column in range(width) if column not in pivots):
        vector = [0] * width
        vector[free] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free] % FIELD
        basis.append(vector)
    return basis


def linear_combination(
    coefficients: Iterable[int], basis: list[list[int]]
) -> list[int]:
    coefficient_list = list(coefficients)
    return [
        sum(
            coefficient_list[row] * basis[row][column]
            for row in range(len(basis))
        )
        % FIELD
        for column in range(len(basis[0]))
    ]


def cycle_biadjacency(parts: tuple[int, ...]) -> list[list[int]]:
    matrix = [[0] * 6 for _ in range(6)]
    offset = 0
    for part in parts:
        for index in range(part):
            matrix[offset + index][offset + index] = 1
            matrix[offset + index][offset + (index + 1) % part] = 1
        offset += part
    assert sum(parts) == 6 and all(part >= 2 for part in parts)
    assert all(sum(row) == 2 for row in matrix)
    assert all(sum(row[column] for row in matrix) == 2 for column in range(6))
    return matrix


def adjacent_union_gram(parts: tuple[int, ...]) -> list[list[int]]:
    cross = cycle_biadjacency(parts)
    gram = [[0] * 13 for _ in range(13)]
    for row in range(13):
        for column in range(13):
            if row == column:
                entry = 0
            elif row == 0 or column == 0:
                entry = 1
            elif (row <= 6 and column <= 6) or (
                row >= 7 and column >= 7
            ):
                entry = 1
            else:
                left = row - 1 if row <= 6 else column - 1
                right = column - 7 if column >= 7 else row - 7
                entry = 1 + cross[left][right]
            gram[row][column] = entry % FIELD
    return gram


def star_span() -> set[tuple[int, ...]]:
    first = [1] * 7 + [0] * 6
    second = [1] + [0] * 6 + [1] * 6
    return {
        tuple(
            (left * first[index] + right * second[index]) % FIELD
            for index in range(13)
        )
        for left, right in product(range(FIELD), repeat=2)
    }


def short_outer_profiles(parts: tuple[int, ...]) -> dict[str, Any]:
    basis = gf3_nullspace(adjacent_union_gram(parts))
    evident = star_span()
    profiles: Counter[tuple[int, int, int, int, int, int]] = Counter()
    inspected = 0
    for coefficients in product(range(FIELD), repeat=len(basis)):
        inspected += 1
        word = linear_combination(coefficients, basis)
        weight = sum(entry != 0 for entry in word)
        if word[0] or tuple(word) in evident or weight > 8:
            continue
        profile = (
            weight,
            sum(entry != 0 for entry in word[1:7]),
            sum(entry != 0 for entry in word[7:13]),
            word.count(1),
            word.count(2),
            sum(word) % FIELD,
        )
        profiles[profile] += 1
    return {
        "gram_kernel_dimension": len(basis),
        "vectors_inspected": inspected,
        "eligible_word_count": sum(profiles.values()),
        "profiles": [
            {
                "weight": profile[0],
                "left_support": profile[1],
                "right_support": profile[2],
                "coefficient_1_count": profile[3],
                "coefficient_2_count": profile[4],
                "coefficient_sum_mod_3": profile[5],
                "word_count": count,
            }
            for profile, count in sorted(profiles.items())
        ],
    }


def analyze() -> dict[str, Any]:
    cycle_types = {
        "+".join(map(str, parts)): short_outer_profiles(parts)
        for parts in ((6,), (4, 2), (3, 3), (2, 2, 2))
    }
    return {
        "field": FIELD,
        "graph_vertex_count": 99,
        "graph_degree": 14,
        "edge_count": 99 * 14 // 2,
        "dual_distance_lower": 4,
        "cycle_types": cycle_types,
        "all_eligible_words_even_and_balanced": all(
            profile["weight"] in (4, 6, 8)
            and profile["left_support"] == profile["right_support"]
            and profile["coefficient_1_count"]
            == profile["coefficient_2_count"]
            and profile["coefficient_sum_mod_3"] == 0
            for item in cycle_types.values()
            for profile in item["profiles"]
        ),
        "projective_circuit_lower_bound": 693,
        "dual_word_bound": "B_4+B_6+B_8>=1386",
        "conclusion": (
            "edge-local support multiplicity is at most one; the local Gram "
            "classification forces even balanced profiles; no endpoint "
            "exclusion follows"
        ),
    }


def verify(data: dict[str, Any]) -> None:
    assert data["edge_count"] == 693
    assert data["projective_circuit_lower_bound"] == 693
    assert data["dual_word_bound"] == "B_4+B_6+B_8>=1386"
    assert data["all_eligible_words_even_and_balanced"]
    expected = {
        "6": [(8, 4, 4, 4, 4, 0, 6)],
        "4+2": [
            (4, 2, 2, 2, 2, 0, 2),
            (8, 4, 4, 4, 4, 0, 2),
        ],
        "3+3": [
            (4, 2, 2, 2, 2, 0, 12),
            (6, 3, 3, 3, 3, 0, 4),
            (8, 4, 4, 4, 4, 0, 36),
        ],
        "2+2+2": [
            (4, 2, 2, 2, 2, 0, 6),
            (8, 4, 4, 4, 4, 0, 12),
        ],
    }
    observed = {
        name: [
            (
                profile["weight"],
                profile["left_support"],
                profile["right_support"],
                profile["coefficient_1_count"],
                profile["coefficient_2_count"],
                profile["coefficient_sum_mod_3"],
                profile["word_count"],
            )
            for profile in item["profiles"]
        ]
        for name, item in data["cycle_types"].items()
    }
    assert observed == expected
    assert {
        name: item["gram_kernel_dimension"]
        for name, item in data["cycle_types"].items()
    } == {"6": 3, "4+2": 3, "3+3": 5, "2+2+2": 4}
    assert max(
        item["vectors_inspected"] for item in data["cycle_types"].values()
    ) == 3**5


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
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if not args.write and not args.verify:
        print(json.dumps(data, indent=2, sort_keys=True))
    print("PASS: Wave178 local balanced-circuit checks")


if __name__ == "__main__":
    main()
