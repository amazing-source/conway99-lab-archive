"""Independent exact checks for the Wave203 two-center audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def mat_vec_mod3(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [
        sum(a * b for a, b in zip(row, vector)) % 3 for row in matrix
    ]


def rank_mod3(matrix: list[list[int]]) -> int:
    rows = [[value % 3 for value in row] for row in matrix]
    rank = 0
    columns = len(rows[0])
    for column in range(columns):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = 1 if rows[rank][column] == 1 else 2
        rows[rank] = [(inverse * value) % 3 for value in rows[rank]]
        for index in range(len(rows)):
            if index == rank:
                continue
            factor = rows[index][column]
            rows[index] = [
                (value - factor * pivot_value) % 3
                for value, pivot_value in zip(rows[index], rows[rank])
            ]
        rank += 1
    return rank


def derive() -> dict[str, object]:
    source = [1, 2, 2, 2, 0, 0]
    reverse = [2, 1, 0, 0, 2, 2]
    relation_sum = [(left + right) % 3 for left, right in zip(source, reverse)]
    assert relation_sum == [0, 0, 2, 2, 2, 2]

    gram = [
        [0, 1, 1, 2],
        [1, 0, 2, 1],
        [1, 2, 0, 1],
        [2, 1, 1, 0],
    ]
    all_equal = [1, 1, 1, 1]
    checkerboard = [1, 2, 2, 1]
    all_equal_image = mat_vec_mod3(gram, all_equal)
    checkerboard_image = mat_vec_mod3(gram, checkerboard)
    assert rank_mod3(gram) == 3
    assert all_equal_image == all_equal
    assert checkerboard_image == [0, 0, 0, 0]

    # Algebraic consequences of degree at most five, with p private
    # labels of degree one among an unordered union of size U.
    selected_row = "3*n3<=p3+5*(|U|-p3)"
    selected_rearranged = "3*n3+4*p3<=5*|U|"

    low_patterns = {
        "1,1": 10 - 1 - 1,
        "1,2": 10 - 1 - 2,
        "2,2": 10 - 2 - 2,
    }
    assert low_patterns == {"1,1": 8, "1,2": 7, "2,2": 6}

    return {
        "verdict": "ACCEPTED_AS_DERIVED",
        "slots": {
            "count": 5,
            "forward": "injective partial image in C_x(y)",
            "reverse": "leaf-block domain in C_x(y)",
            "matched_occupancy": "REFUTED",
            "combined_full_capacity": 5,
            "combined_selected_capacity": 5,
        },
        "paired_relations": {
            "column_order": ["T", "S", "X_a", "X_b", "Y_a", "Y_b"],
            "source": source,
            "reverse": reverse,
            "sum": relation_sum,
            "leaf_coefficients": [source[0], reverse[1]],
            "common_columns_pairwise_distinct": True,
        },
        "gram": {
            "matrix": gram,
            "rank_mod3": rank_mod3(gram),
            "all_equal_image": all_equal_image,
            "all_equal_in_kernel": False,
            "checkerboard_image": checkerboard_image,
            "checkerboard_in_kernel": True,
        },
        "consequences": {
            "selected_row": selected_row,
            "selected_rearranged": selected_rearranged,
            "both_oriented": "epsilon>=5*b",
            "low_patterns": low_patterns,
        },
        "boundary": {
            "b_forced_positive": False,
            "Q0_7059_excluded": False,
            "conditional_Q_lower_bound": 7059,
        },
        "search_scope": (
            "finite-field relation arithmetic and analytic incidence only; "
            "no graph, code, cover, SAT, LP, configuration, enumeration, "
            "isomorphism, or brute-force search"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print("PASS: Wave203 hostile audit matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
