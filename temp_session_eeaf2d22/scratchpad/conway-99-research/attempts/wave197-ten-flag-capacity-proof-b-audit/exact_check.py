"""Exact Wave197 proof-B audit replay.

Only fixed SRG counts and exact rational coefficient algebra are used.
There is no graph, code, cover, SAT, LP, configuration, enumeration,
isomorphism, or brute-force search.
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


def local_capacity() -> dict[str, object]:
    triangles_through_leaf = 14 // 2
    common_neighbor_triangles = 2
    per_orientation = triangles_through_leaf - common_neighbor_triangles
    per_unordered_label = 2 * per_orientation
    assert triangles_through_leaf == 7
    assert per_orientation == 5
    assert per_unordered_label == 10
    return {
        "triangles_through_leaf": triangles_through_leaf,
        "triangles_meeting_center": common_neighbor_triangles,
        "flags_per_orientation": per_orientation,
        "flags_per_unordered_nonedge": per_unordered_label,
        "private_label_selected_multiplicity": 1,
        "weighted_selected_row": "3*n3+9*p3<=10*|U|",
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
        "S10": add(
            scale(360, v["V"]),
            scale(-3, v["n3"]),
            scale(-9, v["p3"]),
            scale(-10, v["a3"]),
            scale(-10, v["b3"]),
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
        ("S10", Fraction(1, 90), slacks["S10"]),
        ("SH", Fraction(4, 45), slacks["SH"]),
        ("SF", Fraction(11, 30), slacks["SF"]),
        ("a1", Fraction(1, 10), v["a1"]),
        ("b3", Fraction(3, 5), v["b3"]),
        ("c2", Fraction(1, 5), v["c2"]),
        ("g", Fraction(4, 15), v["g"]),
        ("W", Fraction(2, 5), v["W"]),
    ]
    right = add(*(scale(k, vector) for _, k, vector in terms))
    difference = add(
        q0,
        scale(Fraction(-57, 30), v["C"]),
        scale(Fraction(263, 30), v["V"]),
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
    target = (57 * c - 263 * vertices) / 30
    assert target == Fraction(70323, 10)

    null = {name: Fraction() for name in VARIABLES}
    null.update(
        {
            "C": c,
            "V": vertices,
            "n1": Fraction(33, 5),
            "a2": Fraction(33, 5),
            "n2": Fraction(1518, 5),
            "p2": Fraction(1518, 5),
            "n3": Fraction(1287),
            "p3": Fraction(3531),
            "c1": Fraction(3531),
            "b1": Fraction(3036, 5),
            "r1": Fraction(20691, 5),
            "r2": Fraction(33, 10),
            "y": Fraction(33, 5),
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
            "Q0-(57*C-263*V)/30=4SI/5+6S2/5+SE2/5+7RA/10+"
            "3SL/10+S10/90+4SH/45+11SF/30+a1/10+3b3/5+"
            "c2/5+4g/15+2W/5"
        ),
        "reduced_difference": reduced,
        "target": str(target),
        "integer_Q_lower_bound": 7033,
        "edge_added_projective": 7033 + 693,
        "circuit_scalar_words": 2 * (7033 + 693),
        "active_null": {
            "n1=a2=y": "33/5",
            "n2=p2": "1518/5",
            "n3": "1287",
            "p3=c1": "3531",
            "b1": "3036/5",
            "r1": "20691/5",
            "r2": "33/10",
            "all_other_split_pool_variables": "0",
            "all_eight_slacks_zero": True,
            "asserted_object": False,
        },
    }


def derive() -> dict[str, object]:
    result = {
        "claim_label": "AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "local_capacity": local_capacity(),
        "global_rows": {
            "H": "36*V=3564",
            "S10": "10*H-3*n3-9*p3-10*a3-10*b3>=0",
            "SH": "3*h-a3-b3>=0",
            "SF": "13*V-n3-h-g>=0",
        },
        "certificate": certificate(),
        "search_scope": (
            "fixed SRG triangle counts and exact rational algebra; no graph, "
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
        print("PASS: Wave197 proof-B audit matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
