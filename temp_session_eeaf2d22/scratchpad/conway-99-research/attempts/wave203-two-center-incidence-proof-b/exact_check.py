"""Exact checks for the independent Wave203 two-center theorem.

This checks finite-field relation algebra and the resulting capacity
formulas. It performs no graph, flag-family, or configuration search.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MODULUS = 3
CANONICAL_GRAM = (
    (0, 1, 1, 2),
    (1, 0, 2, 1),
    (1, 2, 0, 1),
    (2, 1, 1, 0),
)


def mat_vec(
    matrix: tuple[tuple[int, ...], ...], vector: tuple[int, ...]
) -> tuple[int, ...]:
    return tuple(
        sum(entry * value for entry, value in zip(row, vector))
        % MODULUS
        for row in matrix
    )


def rank_mod3(matrix: tuple[tuple[int, ...], ...]) -> int:
    rows = [list(row) for row in matrix]
    rank = 0
    columns = len(rows[0])
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(rank, len(rows))
                if rows[row][column] % MODULUS
            ),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = 1 if rows[rank][column] % MODULUS == 1 else 2
        rows[rank] = [
            inverse * value % MODULUS for value in rows[rank]
        ]
        for row in range(len(rows)):
            if row == rank:
                continue
            factor = rows[row][column] % MODULUS
            if factor:
                rows[row] = [
                    (left - factor * right) % MODULUS
                    for left, right in zip(rows[row], rows[rank])
                ]
        rank += 1
    return rank


def relation_addition() -> dict[str, object]:
    # Column order: T, S, X_a, X_b, Y_a, Y_b.
    source = (1, 2, 2, 2, 0, 0)
    reverse = (2, 1, 0, 0, 2, 2)
    total = tuple(
        (left + right) % MODULUS
        for left, right in zip(source, reverse)
    )
    normalized = tuple(2 * value % MODULUS for value in total)
    assert total == (0, 0, 2, 2, 2, 2)
    assert normalized == (0, 0, 1, 1, 1, 1)
    return {
        "column_order": ["T", "S", "X_a", "X_b", "Y_a", "Y_b"],
        "global_column_normalization": (
            "same frozen z_R columns; each c4 leaf coefficient is 1"
        ),
        "four_common_columns_pairwise_distinct": True,
        "source_c4": list(source),
        "reverse_c4": list(reverse),
        "sum": list(total),
        "normalized_four_column_word": list(normalized[2:]),
    }


def orientation_deficit(
    multiplicity_xy: int, multiplicity_yx: int
) -> int:
    assert multiplicity_xy >= 1
    assert multiplicity_yx >= 1
    assert multiplicity_xy + multiplicity_yx <= 5
    deficit = (5 - multiplicity_xy) + (5 - multiplicity_yx)
    assert deficit >= 5
    return deficit


def derive() -> dict[str, object]:
    all_equal = (1, 1, 1, 1)
    checkerboard = (1, 2, 2, 1)
    all_equal_image = mat_vec(CANONICAL_GRAM, all_equal)
    checkerboard_image = mat_vec(CANONICAL_GRAM, checkerboard)
    gram_rank = rank_mod3(CANONICAL_GRAM)
    assert all_equal_image == (1, 1, 1, 1)
    assert checkerboard_image == (0, 0, 0, 0)
    assert gram_rank == 3

    patterns = {
        "1,1": orientation_deficit(1, 1),
        "1,2": orientation_deficit(1, 2),
        "2,2": orientation_deficit(2, 2),
    }
    assert patterns == {"1,1": 8, "1,2": 7, "2,2": 6}

    return {
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "candidate_geometry": {
            "star_blocks_per_center": 7,
            "common_neighbor_blocks_per_center": 2,
            "opposite_candidate_slots": 5,
            "common_slot_identification": "identity bijection",
            "third_block_map": "injective partial map",
            "surjective_on_all_five": False,
            "matched_reverse_third_block": "T",
            "matched_pair_involution": True,
        },
        "paired_flag_relation": relation_addition(),
        "canonical_quadrilateral": {
            "gram": [list(row) for row in CANONICAL_GRAM],
            "rank_mod3": gram_rank,
            "all_equal_word": list(all_equal),
            "all_equal_image": list(all_equal_image),
            "all_equal_is_relation": False,
            "checkerboard_word": list(checkerboard),
            "checkerboard_image": list(checkerboard_image),
        },
        "capacity": {
            "combined_directional_flag_cap": 5,
            "selected_incidence_row": "3*n3+4*p3<=5*|U|",
            "both_oriented_label_deficit": "epsilon_e>=5",
            "global_both_oriented_row": "epsilon>=5*b",
            "low_multiplicity_patterns": patterns,
        },
        "boundary": {
            "matched_reverse_flag": "REFUTED",
            "extra_circuit_from_low_multiplicity": False,
            "extra_private_label_from_low_multiplicity": False,
            "extra_local_fiber_loss_from_low_multiplicity": False,
            "endpoint_contradiction": False,
        },
        "search_scope": (
            "finite-field relation algebra and analytic incidence only; "
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
        print("PASS: Wave203 proof-B two-center theorem matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
