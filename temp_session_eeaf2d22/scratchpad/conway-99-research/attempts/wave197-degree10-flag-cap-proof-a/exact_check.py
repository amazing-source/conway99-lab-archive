"""Exact symbolic checks for Wave197 proof A.

This verifies the degree-ten incidence row, flag-cap row, exact Q>=7033
certificate, and rational scalar null. It performs no graph, code, cover,
SAT, LP, configuration, enumeration, or isomorphism search.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


VARIABLES = (
    "V",
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


def local_arithmetic() -> dict[str, object]:
    triangles_through_leaf = 7
    triangles_meeting_common_neighbors = 2
    one_orientation = triangles_through_leaf - triangles_meeting_common_neighbors
    unoriented_degree = 2 * one_orientation
    vertices = 99
    local_flag_cap = 13
    local_label_cap = 36
    assert one_orientation == 5
    assert unoriented_degree == 10
    assert vertices * local_flag_cap == 1287
    assert vertices * local_label_cap == 3564
    return {
        "triangles_through_leaf": triangles_through_leaf,
        "triangles_blocked_by_common_neighbors": triangles_meeting_common_neighbors,
        "flag_supports_per_orientation": one_orientation,
        "selected_exact3_degree_cap": unoriented_degree,
        "vertices_V": vertices,
        "global_flag_cap": vertices * local_flag_cap,
        "global_oriented_label_cap": vertices * local_label_cap,
        "S10": "360*V-3*n3-9*p3-10*a3-10*b3>=0",
        "SH": "3*h-a3-b3>=0",
        "SF": "13*V-n3-h-g>=0",
    }


def certificate_remainder() -> dict[str, Fraction]:
    objective = vector(
        V=Fraction(263, 30),
        C=Fraction(-57, 30),
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
    slacks = {
        "SI": vector(C=-2, n1=2, n2=2, n3=3, p2=1, p3=1),
        "S2": vector(p2=1, n2=-1),
        "SE2": vector(r2=2, a2=-1, c2=-1),
        "RA": vector(
            h=3,
            y=1,
            g=3,
            a2=-1,
            a3=-1,
            b3=-2,
            c2=-1,
        ),
        "SL": vector(C=-1, n1=1, n2=2, c1=1, r2=2, y=1, W=2),
        "S10": vector(V=360, n3=-3, p3=-9, a3=-10, b3=-10),
        "SH": vector(h=3, a3=-1, b3=-1),
        "SF": vector(V=13, n3=-1, h=-1, g=-1),
    }
    weights = {
        "SI": Fraction(4, 5),
        "S2": Fraction(6, 5),
        "SE2": Fraction(1, 5),
        "RA": Fraction(7, 10),
        "SL": Fraction(3, 10),
        "S10": Fraction(1, 90),
        "SH": Fraction(4, 45),
        "SF": Fraction(11, 30),
    }
    remainder = objective
    for name, slack in slacks.items():
        remainder = add(remainder, slack, -weights[name])
    return substitute_raw_identities(remainder)


def evaluate_row(row: dict[str, Fraction]) -> dict[str, Fraction]:
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
        "SI": incidence - 2 * row["C"],
        "S2": row["p2"] - row["n2"],
        "SE2": 2 * row["r2"] - row["a2"] - row["c2"],
        "RA": (
            3 * row["h"]
            + row["y"]
            + 3 * row["g"]
            - row["a2"]
            - row["a3"]
            - 2 * row["b3"]
            - row["c2"]
        ),
        "SL": (
            row["n1"]
            + 2 * row["n2"]
            + row["c1"]
            + 2 * row["r2"]
            + row["y"]
            + 2 * row["W"]
            - row["C"]
        ),
        "S10": (
            360 * row["V"]
            - 3 * row["n3"]
            - 9 * row["p3"]
            - 10 * row["a3"]
            - 10 * row["b3"]
        ),
        "SH": 3 * row["h"] - row["a3"] - row["b3"],
        "SF": 13 * row["V"] - row["n3"] - row["h"] - row["g"],
        "S36": (
            36 * row["V"]
            - row["C"]
            + row["n1"]
            + 2 * row["n2"]
            - row["a3"]
            - row["b3"]
        ),
    }


def rational_null_row() -> dict[str, object]:
    row = vector(
        V=99,
        C=4158,
        n1=Fraction(33, 5),
        n2=Fraction(1518, 5),
        n3=1287,
        p2=Fraction(1518, 5),
        p3=3531,
        a2=Fraction(33, 5),
        b1=Fraction(3036, 5),
        c1=3531,
        r1=Fraction(20691, 5),
        r2=Fraction(33, 10),
        y=Fraction(33, 5),
    )
    evaluation = evaluate_row(row)
    assert row["a1"] + row["a2"] + row["a3"] == row["n1"]
    assert row["b1"] + row["b3"] == 2 * row["p2"]
    assert row["c1"] + row["c2"] == row["p3"]
    assert row["a1"] + row["b1"] + row["c1"] == row["r1"]
    assert all(
        evaluation[name] == 0
        for name in ("SI", "S2", "SE2", "RA", "SL", "S10", "SH", "SF")
    )
    assert evaluation["S36"] == Fraction(99, 5)
    target = Fraction(57 * row["C"] - 263 * row["V"], 30)
    assert evaluation["Q0"] == target == Fraction(70323, 10)
    return {
        "row": {
            name: str(value)
            for name, value in row.items()
            if value
        },
        "evaluation": {
            name: str(value)
            for name, value in evaluation.items()
        },
        "target": str(target),
        "is_object": False,
    }


def derive() -> dict[str, object]:
    local = local_arithmetic()
    remainder = certificate_remainder()
    expected_remainder = vector(
        a1=Fraction(1, 10),
        b3=Fraction(3, 5),
        c2=Fraction(1, 5),
        g=Fraction(4, 15),
        W=Fraction(2, 5),
    )
    assert remainder == expected_remainder

    c = 4158
    vertices = 99
    target = Fraction(57 * c - 263 * vertices, 30)
    assert target == Fraction(70323, 10)
    integer_q = (target.numerator + target.denominator - 1) // target.denominator
    assert integer_q == 7033
    edge_added = integer_q + 693
    scalar_words = 2 * edge_added
    assert edge_added == 7726
    assert scalar_words == 15452

    return {
        "local_incidence": local,
        "certificate": {
            "identity_target": "(57*C-263*V)/30",
            "slack_weights": {
                "SI": "4/5",
                "S2": "6/5",
                "SE2": "1/5",
                "RA": "7/10",
                "SL": "3/10",
                "S10": "1/90",
                "SH": "4/45",
                "SF": "11/30",
            },
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
            "V": vertices,
            "rational_Q0": str(target),
            "integral_Q": integer_q,
            "edge_added_projective": edge_added,
            "circuit_scalar_words": scalar_words,
        },
        "rational_null_control": rational_null_row(),
        "claim": {
            "degree": "d(e)<=10",
            "new_slack": "35640-3*n3-9*p3-10*a3-10*b3>=0",
            "flag_cap": "1287-n3-h-g>=0",
            "bound": "Q>=7033",
        },
        "search_scope": (
            "exact SRG incidence identities and rational coefficient "
            "algebra only; no graph, code, cover, SAT, LP, configuration, "
            "enumeration, or isomorphism search"
        ),
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print("PASS: Wave197 proof-A exact result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
