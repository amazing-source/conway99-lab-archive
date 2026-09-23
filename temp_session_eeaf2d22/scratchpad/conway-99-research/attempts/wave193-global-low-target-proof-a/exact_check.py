"""Exact coefficient checks for Wave193 proof A.

No graph, code, cover, SAT, LP, configuration, enumeration, or isomorphism
search is performed.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


VARIABLES = (
    "C",
    "n1",
    "n2",
    "n3",
    "p2",
    "p3",
    "a1",
    "a2",
    "a3",
    "b1",
    "b3",
    "c1",
    "c2",
    "r1",
    "r2",
    "h",
    "Y",
    "W",
)


def vector(**entries: int | Fraction) -> dict[str, Fraction]:
    return {name: Fraction(entries.get(name, 0)) for name in VARIABLES}


def add(
    left: dict[str, Fraction],
    right: dict[str, Fraction],
    scalar: Fraction = Fraction(1),
) -> dict[str, Fraction]:
    return {name: left[name] + scalar * right[name] for name in VARIABLES}


def substitute_raw_identities(
    expression: dict[str, Fraction],
) -> dict[str, Fraction]:
    substitutions = {
        "n1": {"a1": Fraction(1), "a2": Fraction(1), "a3": Fraction(1)},
        "p2": {"b1": Fraction(1, 2), "b3": Fraction(1, 2)},
        "p3": {"c1": Fraction(1), "c2": Fraction(1)},
        "r1": {"a1": Fraction(1), "b1": Fraction(1), "c1": Fraction(1)},
    }
    result = vector()
    for name, coefficient in expression.items():
        if name in substitutions:
            for target, scalar in substitutions[name].items():
                result[target] += coefficient * scalar
        else:
            result[name] += coefficient
    return result


def certificate_remainder() -> dict[str, Fraction]:
    objective = vector(
        C=Fraction(-59, 39),
        n1=1,
        n2=1,
        n3=2,
        r1=1,
        r2=1,
        h=2,
        Y=1,
        W=1,
    )
    slacks = [
        vector(C=-2, n1=2, n2=2, n3=3, p2=1, p3=1),
        vector(p2=1, n2=-1),
        vector(p3=1, n3=-1),
        vector(r2=2, a2=-1, c2=-1),
        vector(h=3, a3=-1, b3=-1),
        vector(
            h=3,
            Y=Fraction(3, 2),
            a2=-1,
            a3=-1,
            b3=-1,
            c2=-1,
        ),
        vector(C=-1, n1=2, n2=4, r1=1, r2=2, Y=1, W=2),
    ]
    weights = [
        Fraction(29, 39),
        Fraction(23, 39),
        Fraction(3, 13),
        Fraction(38, 117),
        Fraction(2, 117),
        Fraction(76, 117),
        Fraction(1, 39),
    ]
    remainder = objective
    for weight, slack in zip(weights, slacks):
        remainder = add(remainder, slack, -weight)
    return substitute_raw_identities(remainder)


def derive() -> dict[str, object]:
    remainder = certificate_remainder()
    expected_remainder = vector(
        a1=Fraction(17, 39),
        a2=Fraction(17, 39),
        a3=Fraction(5, 39),
        b1=Fraction(4, 13),
        r2=Fraction(35, 117),
        W=Fraction(37, 39),
    )
    assert remainder == expected_remainder

    c = 4158
    numerator = 59 * c
    denominator = 39
    q_bound = (numerator + denominator - 1) // denominator

    null = {
        "C": c,
        "n1": 0,
        "n2": 640,
        "n3": 1599,
        "p2": 640,
        "p3": 1599,
        "a1": 0,
        "a2": 0,
        "a3": 0,
        "b1": 0,
        "b3": 1280,
        "c1": 1599,
        "c2": 0,
        "r1": 1599,
        "r2": 0,
        "h": 427,
        "Y": 0,
        "W": 0,
    }
    incidence = (
        2 * null["n1"]
        + 2 * null["n2"]
        + 3 * null["n3"]
        + null["p2"]
        + null["p3"]
    )
    q0 = (
        null["n1"]
        + null["n2"]
        + 2 * null["n3"]
        + null["r1"]
        + null["r2"]
        + 2 * null["h"]
        + null["Y"]
        + null["W"]
    )
    exact3_slack = 3 * null["h"] - null["a3"] - null["b3"]
    residual_slack = (
        3 * null["h"]
        + Fraction(3, 2) * null["Y"]
        - null["a2"]
        - null["a3"]
        - null["b3"]
        - null["c2"]
    )
    leaf_slack = (
        2 * null["n1"]
        + 4 * null["n2"]
        + null["r1"]
        + 2 * null["r2"]
        + null["Y"]
        + 2 * null["W"]
        - c
    )

    result = {
        "certificate": {
            "scaled": "117*Q>=177*C",
            "unscaled": "Q>=59*C/39",
            "remainder_coefficients": {
                name: str(value)
                for name, value in remainder.items()
                if value
            },
            "all_remainder_coefficients_nonnegative": all(
                value >= 0 for value in remainder.values()
            ),
        },
        "bound": {
            "C": c,
            "59C_over_39": f"{numerator}/{denominator}",
            "floor": numerator // denominator,
            "remainder": numerator % denominator,
            "Q": q_bound,
            "edge_added_projective": q_bound + 693,
            "circuit_scalar_words": 2 * (q_bound + 693),
        },
        "integer_null": {
            "row": null,
            "I": incidence,
            "Q0": q0,
            "exact3_slack": exact3_slack,
            "residual_slack": str(residual_slack),
            "leaf_slack": leaf_slack,
            "is_object": False,
        },
        "capacity_rows": {
            "residual": "3*h+(3/2)*Y>=a2+a3+b3+c2",
            "leaf": "2*n1+4*n2+r1+2*r2+Y+2*W>=C",
        },
        "search_scope": (
            "fixed rational coefficient identity and one arithmetic row; "
            "no graph, code, cover, SAT, LP, configuration, enumeration, "
            "or isomorphism search"
        ),
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
    }

    assert incidence == 2 * c
    assert q0 == 6291
    assert exact3_slack == 1
    assert residual_slack == 1
    assert leaf_slack == 1
    assert q_bound == 6291
    assert result["bound"]["edge_added_projective"] == 6984
    assert result["bound"]["circuit_scalar_words"] == 13968
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
        print("PASS: Wave193 proof-A exact result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
