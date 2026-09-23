"""Exact coefficient checks for Wave194 proof A.

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
    "y",
    "g",
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
        C=Fraction(-5, 3),
        n1=1,
        n2=1,
        n3=2,
        r1=1,
        r2=1,
        h=2,
        y=1,
        g=2,
        W=1,
    )
    slacks = [
        vector(C=-2, n1=2, n2=2, n3=3, p2=1, p3=1),
        vector(p2=1, n2=-1),
        vector(
            h=3,
            y=1,
            g=3,
            a2=-1,
            a3=-1,
            b3=-2,
            c2=-1,
        ),
        vector(C=-1, n1=1, n2=2, c1=1, r2=2, y=1, W=2),
    ]
    weights = [
        Fraction(2, 3),
        Fraction(1),
        Fraction(2, 3),
        Fraction(1, 3),
    ]
    remainder = objective
    for weight, slack in zip(weights, slacks):
        remainder = add(remainder, slack, -weight)
    return substitute_raw_identities(remainder)


def equality_row(c: int, t: int) -> dict[str, int]:
    if c % 3:
        raise ValueError("C must be divisible by three")
    if not 0 <= t <= c // 3:
        raise ValueError("equality parameter outside 0<=t<=C/3")
    row = {name: 0 for name in VARIABLES}
    row.update(
        {
            "C": c,
            "n1": 3 * t,
            "n3": c // 3 - t,
            "p3": c - 3 * t,
            "a3": 3 * t,
            "c1": c - 3 * t,
            "r1": c - 3 * t,
            "h": t,
        }
    )
    return row


def evaluate_row(row: dict[str, int]) -> dict[str, int]:
    c = row["C"]
    incidence = (
        2 * row["n1"]
        + 2 * row["n2"]
        + 3 * row["n3"]
        + row["p2"]
        + row["p3"]
    )
    q0 = (
        row["n1"]
        + row["n2"]
        + 2 * row["n3"]
        + row["r1"]
        + row["r2"]
        + 2 * row["h"]
        + row["y"]
        + 2 * row["g"]
        + row["W"]
    )
    return {
        "I": incidence,
        "Q0": q0,
        "incidence_slack": incidence - 2 * c,
        "p2_slack": row["p2"] - row["n2"],
        "p3_slack": row["p3"] - row["n3"],
        "exact2_slack": 2 * row["r2"] - row["a2"] - row["c2"],
        "exact3_slack": 3 * row["h"] - row["a3"] - row["b3"],
        "residual_slack": (
            3 * row["h"]
            + row["y"]
            + 3 * row["g"]
            - row["a2"]
            - row["a3"]
            - 2 * row["b3"]
            - row["c2"]
        ),
        "leaf_slack": (
            row["n1"]
            + 2 * row["n2"]
            + row["c1"]
            + 2 * row["r2"]
            + row["y"]
            + 2 * row["W"]
            - c
        ),
    }


def derive() -> dict[str, object]:
    remainder = certificate_remainder()
    expected_remainder = vector(
        a1=Fraction(1, 3),
        b1=Fraction(1, 6),
        b3=Fraction(1, 2),
        r2=Fraction(1, 3),
        W=Fraction(1, 3),
    )
    assert remainder == expected_remainder

    c = 4158
    q_bound = 5 * c // 3
    control_parameters = (0, c // 6, c // 3)
    controls = []
    for t in control_parameters:
        row = equality_row(c, t)
        evaluation = evaluate_row(row)
        assert row["a1"] + row["a2"] + row["a3"] == row["n1"]
        assert row["b1"] + row["b3"] == 2 * row["p2"]
        assert row["c1"] + row["c2"] == row["p3"]
        assert row["a1"] + row["b1"] + row["c1"] == row["r1"]
        assert evaluation["I"] == 2 * c
        assert evaluation["Q0"] == q_bound
        assert evaluation["p3_slack"] >= 0
        assert all(
            evaluation[name] == 0
            for name in (
                "incidence_slack",
                "p2_slack",
                "exact2_slack",
                "exact3_slack",
                "residual_slack",
                "leaf_slack",
            )
        )
        controls.append(
            {
                "parameter_t": t,
                "row": row,
                **evaluation,
                "is_object": False,
            }
        )

    result = {
        "certificate": {
            "scaled": "3*Q>=5*C",
            "unscaled": "Q>=5*C/3",
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
            "5C_over_3": str(Fraction(5 * c, 3)),
            "Q": q_bound,
            "edge_added_projective": q_bound + 693,
            "circuit_scalar_words": 2 * (q_bound + 693),
        },
        "capacity_rows": {
            "residual": "3*h+y+3*g>=a2+a3+2*b3+c2",
            "leaf_joint": "n1+2*n2+c1+2*r2+y+2*W>=C",
        },
        "equality_face": {
            "parameter": "0<=t<=C/3",
            "nonzero_formulas": {
                "h": "t",
                "n3": "C/3-t",
                "n1": "3*t",
                "a3": "3*t",
                "p3": "C-3*t",
                "c1": "C-3*t",
                "r1": "C-3*t",
            },
            "zero_variables": [
                "n2",
                "p2",
                "a1",
                "a2",
                "b1",
                "b3",
                "c2",
                "r2",
                "y",
                "g",
                "W",
            ],
            "packet_identity": "h+n3=C/3",
            "controls": controls,
            "is_construction": False,
        },
        "search_scope": (
            "fixed rational coefficient identity and symbolic equality-face "
            "formulas with three arithmetic controls; no graph, code, cover, "
            "SAT, LP, configuration, enumeration, or isomorphism search"
        ),
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
    }

    assert q_bound == 6930
    assert result["bound"]["edge_added_projective"] == 7623
    assert result["bound"]["circuit_scalar_words"] == 15246
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
        print("PASS: Wave194 proof-A exact result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
