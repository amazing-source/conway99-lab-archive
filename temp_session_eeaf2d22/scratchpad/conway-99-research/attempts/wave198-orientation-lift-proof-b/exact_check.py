"""Exact checks for the Wave198 orientation-lift row.

Only fixed incidence arithmetic and exact rational coefficient expansion
are used.  There is no graph, code, cover, SAT, LP, configuration,
enumeration, isomorphism, or brute-force search.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


VARIABLES = (
    "C V n1 n2 n3 p2 p3 a1 a2 a3 b1 b3 c1 c2 "
    "r1 r2 h y g W"
).split()


def basis(name: str) -> dict[str, Fraction]:
    return {v: Fraction(v == name) for v in VARIABLES}


def add(*vectors: dict[str, Fraction]) -> dict[str, Fraction]:
    return {
        v: sum((vector[v] for vector in vectors), Fraction())
        for v in VARIABLES
    }


def scale(k: Fraction | int, vector: dict[str, Fraction]) -> dict[str, Fraction]:
    return {v: Fraction(k) * vector[v] for v in VARIABLES}


def orientation_row() -> dict[str, object]:
    orientations = 2
    flags_per_orientation = 5
    unordered_capacity = orientations * flags_per_orientation
    private_bonus = flags_per_orientation - 1
    assert unordered_capacity == 10
    assert private_bonus == 4
    return {
        "orientations_per_nonedge": orientations,
        "flags_per_orientation": flags_per_orientation,
        "unordered_capacity": unordered_capacity,
        "private_selected_multiplicity": 1,
        "private_weight_bonus": private_bonus,
        "selected_row": "3*n3+4*p3<=5*T",
        "full_row": "S5=5*H-3*n3-4*p3-5*a3-5*b3>=0",
        "wave197_relation": "S10=2*S5+(3*n3-p3)",
        "wave197_active_null_S5": -165,
    }


def certificate() -> dict[str, object]:
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
        "SE2": add(
            scale(2, v["r2"]), scale(-1, v["a2"]), scale(-1, v["c2"])
        ),
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
        "S5": add(
            scale(180, v["V"]),
            scale(-3, v["n3"]),
            scale(-4, v["p3"]),
            scale(-5, v["a3"]),
            scale(-5, v["b3"]),
        ),
        "SH": add(
            scale(3, v["h"]), scale(-1, v["a3"]), scale(-1, v["b3"])
        ),
        "SF": add(
            scale(13, v["V"]),
            scale(-1, v["n3"]),
            scale(-1, v["h"]),
            scale(-1, v["g"]),
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
        ("SI", Fraction(4, 5), slacks["SI"]),
        ("S2", Fraction(6, 5), slacks["S2"]),
        ("SE2", Fraction(1, 5), slacks["SE2"]),
        ("RA", Fraction(7, 10), slacks["RA"]),
        ("SL", Fraction(3, 10), slacks["SL"]),
        ("S5", Fraction(1, 40), slacks["S5"]),
        ("SH", Fraction(3, 40), slacks["SH"]),
        ("SF", Fraction(13, 40), slacks["SF"]),
        ("a1", Fraction(1, 10), v["a1"]),
        ("b3", Fraction(3, 5), v["b3"]),
        ("c2", Fraction(1, 5), v["c2"]),
        ("g", Fraction(9, 40), v["g"]),
        ("W", Fraction(2, 5), v["W"]),
    ]
    right = add(*(scale(k, vector) for _, k, vector in terms))
    difference = add(
        q0,
        scale(Fraction(-76, 40), v["C"]),
        scale(Fraction(349, 40), v["V"]),
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
                reduced.get(target, Fraction()) + difference[name] * multiplier
            )
    reduced = {name: str(value) for name, value in reduced.items() if value}
    assert reduced == {}

    c = Fraction(4158)
    vertices = Fraction(99)
    target = (76 * c - 349 * vertices) / 40
    assert target == Fraction(281457, 40)

    null = {name: Fraction() for name in VARIABLES}
    null.update(
        {
            "C": c,
            "V": vertices,
            "n1": Fraction(297, 20),
            "a2": Fraction(297, 20),
            "y": Fraction(297, 20),
            "n2": Fraction(6237, 20),
            "p2": Fraction(6237, 20),
            "n3": Fraction(1287),
            "p3": Fraction(13959, 4),
            "c1": Fraction(13959, 4),
            "b1": Fraction(6237, 10),
            "r1": Fraction(82269, 20),
            "r2": Fraction(297, 40),
        }
    )

    def evaluate(vector: dict[str, Fraction]) -> Fraction:
        return sum(vector[name] * null[name] for name in VARIABLES)

    null_slacks = {name: evaluate(vector) for name, vector in slacks.items()}
    assert all(value == 0 for value in null_slacks.values())
    assert evaluate(q0) == target
    assert null["n1"] == null["a1"] + null["a2"] + null["a3"]
    assert 2 * null["p2"] == null["b1"] + null["b3"]
    assert null["p3"] == null["c1"] + null["c2"]
    assert null["r1"] == null["a1"] + null["b1"] + null["c1"]

    return {
        "identity": (
            "Q0-(76*C-349*V)/40=4SI/5+6S2/5+SE2/5+7RA/10+"
            "3SL/10+S5/40+3SH/40+13SF/40+a1/10+3b3/5+"
            "c2/5+9g/40+2W/5"
        ),
        "reduced_difference": reduced,
        "target": str(target),
        "integer_Q_lower_bound": 7037,
        "edge_added_projective": 7037 + 693,
        "circuit_scalar_words": 2 * (7037 + 693),
        "rational_null": {
            "n1=a2=y": "297/20",
            "n2=p2": "6237/20",
            "n3": "1287",
            "p3=c1": "13959/4",
            "b1": "6237/10",
            "r1": "82269/20",
            "r2": "297/40",
            "all_other_split_pool_variables": "0",
            "all_eight_slacks_zero": True,
            "asserted_object": False,
        },
    }


def derive() -> dict[str, object]:
    result = {
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "orientation_row": orientation_row(),
        "global_rows": {
            "H": "36*V=3564",
            "S5": "5*H-3*n3-4*p3-5*a3-5*b3>=0",
            "SH": "3*h-a3-b3>=0",
            "SF": "13*V-n3-h-g>=0",
        },
        "certificate": certificate(),
        "search_scope": (
            "fixed orientation incidence and exact rational algebra; no graph, "
            "code, cover, SAT, LP, configuration, enumeration, isomorphism, "
            "or brute-force search"
        ),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print("PASS: Wave198 orientation-lift bound matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
