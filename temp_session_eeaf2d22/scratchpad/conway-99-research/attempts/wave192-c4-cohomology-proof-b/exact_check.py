"""Exact scalar and local-vector checks for Wave 192 proof B.

This checks fixed F_3 vectors and equality arithmetic only.  It performs no
graph, cover, code, SAT, LP, configuration, or isomorphism search.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def add_mod3(left: Iterable[int], multiplier: int, right: Iterable[int]) -> list[int]:
    return [(a + multiplier * b) % 3 for a, b in zip(left, right)]


def support(vector: Iterable[int]) -> list[int]:
    return [index for index, value in enumerate(vector) if value % 3]


def profile(vector: list[int], split: int = 7) -> list[int]:
    return [
        sum(value != 0 for value in vector[:split]),
        sum(value != 0 for value in vector[split:]),
    ]


def derive() -> dict[str, object]:
    c = 4158
    q_old = 3 * c // 2
    q_strict = q_old + 1

    # Two nonadjacent seven-stars.  The canonical conic has two coordinates
    # on each side and checkerboard signs.
    conic = [1, 2, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0]
    star_x = [1] * 7 + [0] * 7
    axis_plus = add_mod3(conic, 1, star_x)
    axis_minus = add_mod3(conic, 2, star_x)

    # Equality after excluding exact-two residuals.
    equality = {
        "p2": 0,
        "n2": 0,
        "p3_equals_n3": True,
        "n1_plus_2n3": c,
        "h": 0,
        "Y": 0,
        "Z": 0,
        "r": c // 2,
        "r1_equals_n3": True,
        "exact2_raw_circuits": "n1/2",
        "type1_assignments_per_conic": 2,
    }

    # After the unused-axis obstruction forces n1=0.
    n1 = 0
    n3 = c // 2
    private_labels = n3
    selected_incidences = 3 * n3
    shared_labels = c - private_labels
    shared_incidences = selected_incidences - private_labels

    result = {
        "claim_label": "DERIVED",
        "search_scope": (
            "fixed F3 vectors and scalar identities only; no graph, cover, "
            "code, SAT, LP, configuration, enumeration, or isomorphism search"
        ),
        "constants": {
            "C": c,
            "wave191_Q": q_old,
            "strict_Q": q_strict,
            "edge_isolated": 693,
            "all_projective_short_circuits": q_strict + 693,
            "scalar_short_circuit_words": 2 * (q_strict + 693),
        },
        "axis_coset": {
            "conic": conic,
            "star_x": star_x,
            "plus": axis_plus,
            "minus": axis_minus,
            "plus_profile": profile(axis_plus),
            "minus_profile": profile(axis_minus),
            "plus_support": support(axis_plus),
            "minus_support": support(axis_minus),
            "distinct_missing_square_coordinates": (
                support(axis_plus)[0] != support(axis_minus)[0]
            ),
        },
        "equality_face": equality,
        "all_type3_face": {
            "n1": n1,
            "n3": n3,
            "private_labels": private_labels,
            "selected_label_incidences": selected_incidences,
            "shared_labels": shared_labels,
            "shared_label_incidences": shared_incidences,
            "shared_label_multiplicity": shared_incidences // shared_labels,
        },
    }

    assert c % 2 == 0
    assert q_old == 6237
    assert q_strict == 6238
    assert profile(axis_plus) == [6, 2]
    assert profile(axis_minus) == [6, 2]
    assert support(axis_plus) != support(axis_minus)
    assert not set(support(conic)).issubset(support(axis_plus))
    assert not set(support(conic)).issubset(support(axis_minus))
    assert shared_labels == 2079
    assert shared_incidences == 2 * shared_labels
    assert result["constants"]["all_projective_short_circuits"] == 6931
    assert result["constants"]["scalar_short_circuit_words"] == 13862

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
        print("PASS: Wave192 exact result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

