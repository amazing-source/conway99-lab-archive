"""Independent exact audit of the Wave198 orientation-lift theorem."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


NAMES = tuple(
    "V C n1 n2 n3 p2 p3 a1 a2 a3 b1 b3 c1 c2 "
    "r1 r2 h y g W".split()
)


def vec(**values: int | Fraction) -> dict[str, Fraction]:
    return {name: Fraction(values.get(name, 0)) for name in NAMES}


def plus(
    left: dict[str, Fraction],
    right: dict[str, Fraction],
    scale: Fraction = Fraction(1),
) -> dict[str, Fraction]:
    return {name: left[name] + scale * right[name] for name in NAMES}


def raw_substitute(expression: dict[str, Fraction]) -> dict[str, Fraction]:
    rules = {
        "n1": {"a1": Fraction(1), "a2": Fraction(1), "a3": Fraction(1)},
        "p2": {"b1": Fraction(1, 2), "b3": Fraction(1, 2)},
        "p3": {"c1": Fraction(1), "c2": Fraction(1)},
        "r1": {"a1": Fraction(1), "b1": Fraction(1), "c1": Fraction(1)},
    }
    result = vec()
    for name, coefficient in expression.items():
        if name in rules:
            for target, factor in rules[name].items():
                result[target] += coefficient * factor
        else:
            result[name] += coefficient
    return result


def independent_remainder() -> dict[str, Fraction]:
    objective = vec(
        V=Fraction(349, 40),
        C=Fraction(-76, 40),
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
        "SI": vec(C=-2, n1=2, n2=2, n3=3, p2=1, p3=1),
        "S2": vec(p2=1, n2=-1),
        "SE2": vec(r2=2, a2=-1, c2=-1),
        "RA": vec(
            h=3, y=1, g=3, a2=-1, a3=-1, b3=-2, c2=-1
        ),
        "SL": vec(C=-1, n1=1, n2=2, c1=1, r2=2, y=1, W=2),
        "S5": vec(V=180, n3=-3, p3=-4, a3=-5, b3=-5),
        "SH": vec(h=3, a3=-1, b3=-1),
        "SF": vec(V=13, n3=-1, h=-1, g=-1),
    }
    weights = {
        "SI": Fraction(4, 5),
        "S2": Fraction(6, 5),
        "SE2": Fraction(1, 5),
        "RA": Fraction(7, 10),
        "SL": Fraction(3, 10),
        "S5": Fraction(1, 40),
        "SH": Fraction(3, 40),
        "SF": Fraction(13, 40),
    }
    remainder = objective
    for name, slack in slacks.items():
        remainder = plus(remainder, slack, -weights[name])
    return raw_substitute(remainder)


def evaluate(row: dict[str, Fraction]) -> dict[str, Fraction]:
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
        "S5": (
            180 * row["V"]
            - 3 * row["n3"]
            - 4 * row["p3"]
            - 5 * row["a3"]
            - 5 * row["b3"]
        ),
        "SH": 3 * row["h"] - row["a3"] - row["b3"],
        "SF": 13 * row["V"] - row["n3"] - row["h"] - row["g"],
    }


def rational_null() -> dict[str, object]:
    row = vec(
        V=99,
        C=4158,
        n1=Fraction(297, 20),
        n2=Fraction(6237, 20),
        n3=1287,
        p2=Fraction(6237, 20),
        p3=Fraction(13959, 4),
        a2=Fraction(297, 20),
        b1=Fraction(6237, 10),
        c1=Fraction(13959, 4),
        r1=Fraction(82269, 20),
        r2=Fraction(297, 40),
        y=Fraction(297, 20),
    )
    assert row["n1"] == row["a1"] + row["a2"] + row["a3"]
    assert 2 * row["p2"] == row["b1"] + row["b3"]
    assert row["p3"] == row["c1"] + row["c2"]
    assert row["r1"] == row["a1"] + row["b1"] + row["c1"]
    values = evaluate(row)
    assert all(values[name] == 0 for name in values if name != "Q0")
    assert values["Q0"] == Fraction(281457, 40)
    return {
        "row": {name: str(value) for name, value in row.items() if value},
        "slacks": {name: str(value) for name, value in values.items()},
        "asserted_object": False,
    }


def derive() -> dict[str, object]:
    remainder = independent_remainder()
    expected = vec(
        a1=Fraction(1, 10),
        b3=Fraction(3, 5),
        c2=Fraction(1, 5),
        g=Fraction(9, 40),
        W=Fraction(2, 5),
    )
    assert remainder == expected

    # Coefficient identity relating the old unordered and new oriented rows.
    # S10 - 2*S5 = 3*n3-p3.
    s10 = vec(V=360, n3=-3, p3=-9, a3=-10, b3=-10)
    s5 = vec(V=180, n3=-3, p3=-4, a3=-5, b3=-5)
    relation = plus(s10, s5, Fraction(-2))
    assert relation == vec(n3=3, p3=-1)

    target = Fraction(76 * 4158 - 349 * 99, 40)
    assert target == Fraction(281457, 40)
    integer_bound = (target.numerator + target.denominator - 1) // target.denominator
    assert integer_bound == 7037

    return {
        "verdict": "ACCEPTED_AS_DERIVED",
        "orientation": {
            "flags_per_fixed_orientation": 5,
            "private_selected_multiplicity": 1,
            "selected_row": "3*n3+4*p3<=5*T",
            "global_row": "180*V-3*n3-4*p3-5*a3-5*b3>=0",
            "old_row_relation": "S10=2*S5+(3*n3-p3)",
        },
        "certificate": {
            "target": str(target),
            "integer_Q_lower_bound": integer_bound,
            "edge_added_projective": integer_bound + 693,
            "scalar_words": 2 * (integer_bound + 693),
            "remainder": {
                name: str(value) for name, value in remainder.items() if value
            },
        },
        "rational_null": rational_null(),
        "search_scope": (
            "oriented incidence and exact rational algebra only; no graph, "
            "code, cover, SAT, LP, configuration, enumeration, isomorphism, "
            "or brute-force search"
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
        print("PASS: Wave198 hostile audit matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
