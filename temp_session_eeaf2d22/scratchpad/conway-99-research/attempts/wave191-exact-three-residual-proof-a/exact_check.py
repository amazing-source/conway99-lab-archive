"""Fixed exact checks for Wave191 proof A.

This module checks local coefficient subtraction and global scalar
identities. It performs no graph, cover, code, SAT, LP, or isomorphism
search.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def sub_mod3(left: Iterable[int], multiplier: int, right: Iterable[int]) -> list[int]:
    return [(a - multiplier * b) % 3 for a, b in zip(left, right)]


def profile(vector: list[int], split: int) -> list[int]:
    return [
        sum(value != 0 for value in vector[:split]),
        sum(value != 0 for value in vector[split:]),
    ]


def derive() -> dict[str, object]:
    # Coordinates are x-side (3), then the six available y-star coordinates.
    leaf = [2] * 9

    # Hypothetical exact-three raw centered at x: it must use all three
    # x-side blocks and one y-side leaf block.
    owner_c4 = [2, 2, 2, 1, 0, 0, 0, 0, 0]
    owner_difference = sub_mod3(leaf, 1, owner_c4)

    # Target center y is forced to have T in A_y. Coordinates after the
    # split are A_y\{T} (2), then B_y (4). The target c5 uses S and all B_y.
    target_c5 = [1, 0, 0, 0, 0, 1, 1, 1, 1]
    c5_difference = sub_mod3(leaf, 2, target_c5)

    canonical_gram = [
        [0, 1, 1, 2],
        [1, 0, 2, 1],
        [1, 2, 0, 1],
        [2, 1, 1, 0],
    ]
    all_equal = [2, 2, 2, 2]
    checkerboard_kernel = [1, 2, 2, 1]

    def gram_product(vector: list[int]) -> list[int]:
        return [
            sum(entry * value for entry, value in zip(row, vector)) % 3
            for row in canonical_gram
        ]

    # Wave181 exact-two checkerboard containment control.
    checkerboard = [1, 2, 0, 2, 1, 0, 0, 0, 0]
    checkerboard_one = sub_mod3(leaf, 1, checkerboard)
    checkerboard_two = sub_mod3(leaf, 2, checkerboard)

    coefficients = [18, 12, 24, 16, 12]
    identity = [
        9 * 2,
        9 * 2 - 6,
        9 * 3 - 3,
        9 + 6 + 1,
        9 + 3,
    ]

    c = 4158
    lower_numerator = 3 * c
    lower_denominator = 2
    q_bound = (lower_numerator + lower_denominator - 1) // lower_denominator

    null_row = {
        "n1": 0,
        "n2": 0,
        "n3": 2079,
        "p2": 0,
        "p3": 2079,
        "r": 1040,
        "r1": 1,
        "h": 0,
        "delta": 1,
        "Y": 1039,
        "Q": 6237,
    }
    a = null_row["n1"] + 2 * null_row["p2"] + null_row["p3"]
    b = null_row["n1"] + null_row["n2"] + 2 * null_row["n3"]
    incidence = (
        2 * null_row["n1"]
        + 2 * null_row["n2"]
        + 3 * null_row["n3"]
        + null_row["p2"]
        + null_row["p3"]
    )

    result = {
        "local": {
            "leaf": leaf,
            "owner_center_c4": owner_c4,
            "owner_center_difference": owner_difference,
            "owner_center_difference_profile": profile(owner_difference, 3),
            "target_c5_difference": c5_difference,
            "target_c5_difference_profile": profile(c5_difference, 3),
            "canonical_gram": canonical_gram,
            "all_equal_word": all_equal,
            "all_equal_gram_product": gram_product(all_equal),
            "checkerboard_kernel": checkerboard_kernel,
            "checkerboard_gram_product": gram_product(checkerboard_kernel),
            "checkerboard_difference_profiles": [
                profile(checkerboard_one, 3),
                profile(checkerboard_two, 3),
            ],
        },
        "capacity": {
            "type3_and_unused_exact1": "p3+u<=delta+Z<=delta+2*Y",
            "type2_and_unused_exact1": "2*p2<=u+3*h",
            "type3": "delta+2*Y>=p3",
            "joint": "delta+3*h+2*Y>=2*p2+p3",
            "penalty": "delta/2+h/2+Y>=p2/3+p3/2",
        },
        "coefficient_certificate": {
            "coefficient_row": coefficients,
            "identity_row": identity,
            "identity": (
                "12Q>=9I+6*(p2-n2)+p2+3*(p3-n3)>=18C"
            ),
            "C": c,
            "three_C_over_two": q_bound,
            "edge_added_projective": q_bound + 693,
            "circuit_scalar_words": 2 * (q_bound + 693),
        },
        "null_control": {
            "row": null_row,
            "A": a,
            "B": b,
            "I": incidence,
            "delta_definition": 2 * null_row["r"] + 3 * null_row["h"] - a,
            "raw_capacity": 2 * null_row["r"] - null_row["r1"] + 3 * null_row["h"],
            "residual_capacity": 2 * null_row["Y"],
            "counted_Q": b + null_row["r"] + 2 * null_row["h"] + null_row["Y"],
        },
        "search_scope": (
            "fixed F3 vectors and scalar identities only; no graph, cover, "
            "code, SAT, LP, configuration, enumeration, or isomorphism search"
        ),
        "claim_label": (
            "DERIVED_INDEPENDENT_AUDIT_PASS_PENDING_SEALED_VERIFICATION"
        ),
    }

    assert profile(owner_difference, 3) == [0, 6]
    assert profile(c5_difference, 3) == [2, 2]
    assert gram_product(all_equal) != [0, 0, 0, 0]
    assert gram_product(checkerboard_kernel) == [0, 0, 0, 0]
    assert profile(checkerboard_one, 3) == [2, 5]
    assert profile(checkerboard_two, 3) == [2, 5]
    assert coefficients == identity
    assert q_bound == 6237
    assert result["coefficient_certificate"]["edge_added_projective"] == 6930
    assert result["coefficient_certificate"]["circuit_scalar_words"] == 13860
    assert incidence == 2 * c
    assert null_row["p3"] == null_row["n3"]
    assert result["null_control"]["delta_definition"] == null_row["delta"]
    assert result["null_control"]["raw_capacity"] == a
    assert result["null_control"]["residual_capacity"] == null_row["p3"] - null_row["r1"]
    assert result["null_control"]["counted_Q"] == null_row["Q"]

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print("PASS: Wave191 proof-A exact result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
