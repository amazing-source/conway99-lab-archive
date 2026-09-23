"""Exact replay for the Wave 194 proof-B audit.

The checker uses fixed F_3 support vectors and rational coefficient
identities only.  It performs no graph, cover, code, SAT, LP,
configuration, enumeration, or isomorphism search.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


VARIABLES = (
    "C n1 n2 n3 p2 p3 a1 a2 a3 b1 b3 c1 c2 "
    "r1 r2 h y g W"
).split()


def basis(name: str) -> dict[str, Fraction]:
    return {variable: Fraction(variable == name) for variable in VARIABLES}


def add(*vectors: dict[str, Fraction]) -> dict[str, Fraction]:
    return {
        variable: sum((vector[variable] for vector in vectors), Fraction())
        for variable in VARIABLES
    }


def scale(multiplier: Fraction | int, vector: dict[str, Fraction]) -> dict[str, Fraction]:
    return {
        variable: Fraction(multiplier) * vector[variable]
        for variable in VARIABLES
    }


def add_mod3(left: list[int], right: list[int]) -> list[int]:
    return [(a + b) % 3 for a, b in zip(left, right)]


def support(vector: list[int]) -> list[int]:
    return [index for index, value in enumerate(vector) if value]


def profile(vector: list[int]) -> list[int]:
    return [
        sum(value != 0 for value in vector[:7]),
        sum(value != 0 for value in vector[7:]),
    ]


def derive() -> dict[str, object]:
    v = {name: basis(name) for name in VARIABLES}
    incidence = add(
        scale(2, v["n1"]),
        scale(2, v["n2"]),
        scale(3, v["n3"]),
        v["p2"],
        v["p3"],
    )
    slacks = {
        "SI": add(incidence, scale(-2, v["C"])),
        "S2": add(v["p2"], scale(-1, v["n2"])),
        "RA": add(
            scale(3, v["h"]),
            v["y"],
            scale(3, v["g"]),
            scale(-1, v["a2"]),
            scale(-1, v["a3"]),
            scale(-2, v["b3"]),
            scale(-1, v["c2"]),
        ),
        "SL": add(
            v["n1"],
            scale(2, v["n2"]),
            v["c1"],
            scale(2, v["r2"]),
            v["y"],
            scale(2, v["W"]),
            scale(-1, v["C"]),
        ),
    }
    q0 = add(
        v["n1"],
        v["n2"],
        scale(2, v["n3"]),
        v["r1"],
        v["r2"],
        scale(2, v["h"]),
        v["y"],
        scale(2, v["g"]),
        v["W"],
    )
    terms = [
        (Fraction(2, 3), slacks["SI"]),
        (Fraction(1), slacks["S2"]),
        (Fraction(2, 3), slacks["RA"]),
        (Fraction(1, 3), slacks["SL"]),
        (Fraction(1, 3), v["a1"]),
        (Fraction(1, 6), v["b1"]),
        (Fraction(1, 2), v["b3"]),
        (Fraction(1, 3), v["r2"]),
        (Fraction(1, 3), v["W"]),
    ]
    right = add(*(scale(coefficient, vector) for coefficient, vector in terms))
    difference = add(
        q0,
        scale(Fraction(-5, 3), v["C"]),
        scale(-1, right),
    )

    substitutions = {
        "n1": {"a1": Fraction(1), "a2": Fraction(1), "a3": Fraction(1)},
        "p2": {"b1": Fraction(1, 2), "b3": Fraction(1, 2)},
        "p3": {"c1": Fraction(1), "c2": Fraction(1)},
        "r1": {"a1": Fraction(1), "b1": Fraction(1), "c1": Fraction(1)},
    }
    reduced = {
        name: coefficient
        for name, coefficient in difference.items()
        if name not in substitutions
    }
    for name, replacement in substitutions.items():
        for target, multiplier in replacement.items():
            reduced[target] = (
                reduced.get(target, Fraction())
                + difference[name] * multiplier
            )
    reduced = {
        name: str(coefficient)
        for name, coefficient in reduced.items()
        if coefficient
    }

    # Canonical conic in two nonadjacent seven-stars.  Translate once at
    # each endpoint, choosing signs that cancel one conic coordinate.
    conic = [1, 2, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0]
    star_x = [1] * 7 + [0] * 7
    star_y = [0] * 7 + [1] * 7
    parent_x = add_mod3(conic, star_x)
    parent_y = add_mod3(conic, star_y)
    parent_intersection = sorted(set(support(parent_x)) & set(support(parent_y)))

    c = 4158
    q_bound = 5 * c // 3
    result = {
        "claim_label": "DERIVED",
        "audit_verdict": "PASS",
        "certificate": {
            "identity": "Q0-5*C/3=sum(nonnegative multiplier*slack)",
            "multipliers": [
                "2/3",
                "1",
                "2/3",
                "1/3",
                "1/3",
                "1/6",
                "1/2",
                "1/3",
                "1/3",
            ],
            "reduced_difference": reduced,
        },
        "local_type2": {
            "conic": conic,
            "parent_x_profile": profile(parent_x),
            "parent_y_profile": profile(parent_y),
            "parent_x_support": support(parent_x),
            "parent_y_support": support(parent_y),
            "parent_intersection": parent_intersection,
            "parent_intersection_size": len(parent_intersection),
            "dual_distance": 4,
        },
        "rows": {
            "RA": "3*h+y+3*g>=a2+a3+2*b3+c2",
            "SL": "n1+2*n2+c1+2*r2+y+2*W>=C",
        },
        "bound": {
            "C": c,
            "Q": q_bound,
            "edge_added_projective": q_bound + 693,
            "scalar_short_circuit_words": 2 * (q_bound + 693),
        },
        "null_control": {
            "n3": c // 3,
            "p3": c,
            "c1": c,
            "r1": c,
            "Q0": 2 * (c // 3) + c,
            "all_other_split_variables": 0,
            "asserted_object": False,
        },
        "search_scope": (
            "fixed F3 vectors and exact rational identities only; no graph, "
            "cover, code, SAT, LP, configuration, enumeration, or "
            "isomorphism search"
        ),
    }

    assert reduced == {}
    assert profile(parent_x) == [6, 2]
    assert profile(parent_y) == [2, 6]
    assert len(parent_intersection) == 2
    assert len(parent_intersection) < result["local_type2"]["dual_distance"]
    assert q_bound == 6930
    assert result["bound"]["edge_added_projective"] == 7623
    assert result["bound"]["scalar_short_circuit_words"] == 15246
    assert result["null_control"]["Q0"] == q_bound

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
        print("PASS: Wave194 proof-B audit exact result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
