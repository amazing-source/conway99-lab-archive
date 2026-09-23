"""Exact symbolic checks for Wave 186.

The checker validates the two star-translation support calculations and the
integer cover bound.  It does not enumerate a graph, code, cover, or
configuration.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


FORMAT = "wave186-star-translation-cover-v1"
NONEDGES = 4158
EDGE_CIRCUITS = 693


def add_mod3(left: list[int], right: list[int], scalar: int = 1) -> list[int]:
    if len(left) != len(right):
        raise AssertionError("vector lengths differ")
    return [(a + scalar * b) % 3 for a, b in zip(left, right)]


def support(word: list[int]) -> set[int]:
    return {i for i, value in enumerate(word) if value % 3}


def multiplicity_two_translates() -> dict[str, Any]:
    conic = [1, 2, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0]
    star_x = [1] * 7 + [0] * 7
    star_y = [0] * 7 + [1] * 7
    tx = add_mod3(conic, star_x, 2)
    ty = add_mod3(conic, star_y, 1)
    sx, sy = support(tx), support(ty)
    if (len(sx & set(range(7))), len(sx & set(range(7, 14)))) != (6, 2):
        raise AssertionError("x-translate lost its 6+2 profile")
    if (len(sy & set(range(7))), len(sy & set(range(7, 14)))) != (2, 6):
        raise AssertionError("y-translate lost its 2+6 profile")
    return {
        "conic_weight": len(support(conic)),
        "x_translate_profile": [6, 2],
        "y_translate_profile": [2, 6],
        "translate_weights": [len(sx), len(sy)],
        "translated_support_intersection": len(sx & sy),
        "dual_distance_floor": 4,
        "forced_distinct_circuits_per_private_label": 2,
    }


def multiplicity_three_translate() -> dict[str, Any]:
    # Coordinates: seven x-star columns, then T and six outer y-star columns.
    conic4 = [2, 2, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    companion5 = [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    star_y = [0] * 7 + [1] * 7
    leaf_translate = add_mod3(conic4, star_y, 2)
    translated = support(leaf_translate)
    return {
        "conic_weight": len(support(conic4)),
        "companion_weight": len(support(companion5)),
        "leaf_translate_profile": [
            len(translated & set(range(7))),
            len(translated & set(range(7, 14))),
        ],
        "leaf_translate_weight": len(translated),
        "contains_T": 7 in translated,
        "conic_translate_intersection": len(translated & support(conic4)),
        "companion_translate_intersection": len(
            translated & support(companion5)
        ),
        "forced_distinct_circuits_per_private_label": 2,
    }


def cover_bound() -> dict[str, Any]:
    ratio = Fraction(8, 9)
    nonedge_lower = ratio * NONEDGES
    if nonedge_lower.denominator != 1:
        raise AssertionError("8/9 bound is unexpectedly nonintegral")
    q_lower = int(nonedge_lower)
    projective_total = q_lower + EDGE_CIRCUITS
    arithmetic_control = {
        "n1": 0,
        "n2": 0,
        "n3": 1848,
        "selected_label_incidences": 3 * 1848,
        "private_labels": 2772,
        "outside_circuits": 1848,
    }
    if 3 * arithmetic_control["outside_circuits"] != 2 * arithmetic_control[
        "private_labels"
    ]:
        raise AssertionError("arithmetic control lost assignment equality")
    if arithmetic_control["outside_circuits"] != arithmetic_control["n3"]:
        raise AssertionError("arithmetic control lost companion equality")
    if arithmetic_control["n3"] + arithmetic_control["outside_circuits"] != q_lower:
        raise AssertionError("arithmetic control lost Q equality")
    return {
        "covered_nonedges": NONEDGES,
        "cover_ratio": "8/9",
        "nonedge_projective_lower": q_lower,
        "edge_isolated_projective": EDGE_CIRCUITS,
        "total_projective_lower": projective_total,
        "dual_short_word_lower": 2 * projective_total,
        "arithmetic_control_not_construction": arithmetic_control,
        "inequality_certificate": {
            "private_assignment": (
                "6*O+8*n1+8*n2+12*n3>=8*C"
            ),
            "triple_companions": "3*O+n1+n2-3*n3>=0",
            "sum": "9*(N+O)>=8*C",
        },
    }


def derive() -> dict[str, Any]:
    return {
        "format": FORMAT,
        "conditional_status": "DERIVED",
        "global_status": "UNKNOWN",
        "multiplicity_two": multiplicity_two_translates(),
        "multiplicity_three": multiplicity_three_translate(),
        "cover": cover_bound(),
        "former_equality_Q_2079_excluded": True,
        "limitations": [
            "No graph, code, cover, or configuration was enumerated.",
            "The arithmetic equality profile is not a circuit cover.",
            "The rank-11 endpoint and Conway-99 remain UNKNOWN.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise AssertionError("frozen result differs from exact derivation")
        print(f"PASS Wave 186 exact verification: {args.verify}")
    elif args.output is not None:
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(args.output)
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
