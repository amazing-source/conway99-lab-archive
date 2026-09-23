"""Exact rational certificate replay for the Wave 193 proof-B audit.

No graph, cover, code, SAT, LP, configuration, or isomorphism search is
performed.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


VARIABLES = (
    "C n1 n2 n3 p2 p3 a1 a2 a3 b1 b3 c1 c2 "
    "r1 r2 h Y W"
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
        "S3": add(v["p3"], scale(-1, v["n3"])),
        "SE2": add(scale(2, v["r2"]), scale(-1, v["a2"]), scale(-1, v["c2"])),
        "SE3": add(scale(3, v["h"]), scale(-1, v["a3"]), scale(-1, v["b3"])),
        "SR": add(
            scale(3, v["h"]),
            scale(Fraction(3, 2), v["Y"]),
            scale(-1, v["a2"]),
            scale(-1, v["a3"]),
            scale(-1, v["b3"]),
            scale(-1, v["c2"]),
        ),
        "SL": add(
            scale(2, v["n1"]),
            scale(4, v["n2"]),
            v["r1"],
            scale(2, v["r2"]),
            v["Y"],
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
        v["Y"],
        v["W"],
    )

    terms = [
        (Fraction(29, 39), slacks["SI"]),
        (Fraction(23, 39), slacks["S2"]),
        (Fraction(3, 13), slacks["S3"]),
        (Fraction(38, 117), slacks["SE2"]),
        (Fraction(2, 117), slacks["SE3"]),
        (Fraction(76, 117), slacks["SR"]),
        (Fraction(1, 39), slacks["SL"]),
        (Fraction(17, 39), add(v["a1"], v["a2"])),
        (Fraction(5, 39), v["a3"]),
        (Fraction(4, 13), v["b1"]),
        (Fraction(35, 117), v["r2"]),
        (Fraction(37, 39), v["W"]),
    ]
    right = add(*(scale(coefficient, vector) for coefficient, vector in terms))
    difference = add(
        q0,
        scale(Fraction(-59, 39), v["C"]),
        scale(-1, right),
    )

    # Eliminate n1, p2, p3, r1 using the four split identities.
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
        name: coefficient
        for name, coefficient in reduced.items()
        if coefficient
    }

    c = 4158
    numerator = 59 * c
    denominator = 39
    strict_bound = (numerator + denominator - 1) // denominator

    return {
        "claim_label": "DERIVED",
        "audit_verdict": "PASS",
        "certificate": {
            "reduced_difference": {
                name: str(coefficient) for name, coefficient in reduced.items()
            },
            "multipliers": [
                "29/39",
                "23/39",
                "3/13",
                "38/117",
                "2/117",
                "76/117",
                "1/39",
                "17/39",
                "5/39",
                "4/13",
                "35/117",
                "37/39",
            ],
            "identity": "Q0-59*C/39=sum(nonnegative multiplier*slack)",
        },
        "bound": {
            "C": c,
            "fraction": f"{numerator}/{denominator}",
            "reduced_fraction": "81774/13",
            "Q": strict_bound,
            "edge_added_projective": strict_bound + 693,
            "scalar_short_circuit_words": 2 * (strict_bound + 693),
        },
        "collision_rows": {
            "SR": "3*h+3*Y/2>=a2+a3+b3+c2",
            "SL": "2*n1+4*n2+r1+2*r2+Y+2*W>=C",
        },
        "search_scope": (
            "exact rational coefficient replay only; no graph, cover, code, "
            "SAT, LP, configuration, enumeration, or isomorphism search"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    assert result["certificate"]["reduced_difference"] == {}
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print("PASS: Wave193 proof-B audit exact result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

