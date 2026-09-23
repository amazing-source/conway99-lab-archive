"""Exact Wave196 proof-B audit replay.

This evaluates two fixed extremal set families and an exact rational
coefficient identity.  It performs no graph or configuration search.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path


VARIABLES = (
    "C H n1 n2 n3 p2 p3 a1 a2 a3 b1 b3 c1 c2 "
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


def templates() -> dict[str, set[frozenset[int]]]:
    points = set(range(7))
    special = 0
    triple = frozenset({1, 2, 3})
    h_family = {triple}
    for pair in combinations(points - {special}, 2):
        member = frozenset({special, *pair})
        if member & triple:
            h_family.add(member)
    k_family = {
        frozenset(member)
        for member in combinations(points, 3)
        if len(set(member) & set(triple)) >= 2
    }
    return {"H": h_family, "K": k_family}


def local_geometry() -> dict[str, object]:
    fiber_size = 2 * 2
    fibers = 21
    nonneighbors = fibers * fiber_size
    checked = {}
    for name, family in templates().items():
        degrees: Counter[frozenset[int]] = Counter()
        for member in family:
            for pair in combinations(member, 2):
                degrees[frozenset(pair)] += 1
        degree_five = sum(degree == 5 for degree in degrees.values())
        forced_repeats = sum(
            max(0, degree - fiber_size) for degree in degrees.values()
        )
        assert len(family) == 13
        assert degree_five == 3
        assert forced_repeats >= 3
        checked[name] = {
            "members": len(family),
            "pair_types_of_degree_five": degree_five,
            "forced_repeats": forced_repeats,
            "leaf_union_cap": 3 * len(family) - forced_repeats,
        }
    assert nonneighbors == 84
    return {
        "local_matching_edges": 7,
        "two_edge_types": fibers,
        "fiber_size": fiber_size,
        "partitioned_nonneighbors": nonneighbors,
        "templates": checked,
        "common_star_flag_cap": 12,
        "universal_flag_cap": 13,
        "universal_label_cap": 36,
        "global_flag_cap": 99 * 13,
        "global_label_cap": 99 * 36,
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
        "S36": add(
            v["H"],
            scale(-1, v["C"]),
            v["n1"],
            scale(2, v["n2"]),
            scale(-1, v["a3"]),
            scale(-1, v["b3"]),
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
        ("SI", Fraction(2, 3), slacks["SI"]),
        ("S2", Fraction(4, 3), slacks["S2"]),
        ("SE2", Fraction(1, 6), slacks["SE2"]),
        ("RA", Fraction(2, 3), slacks["RA"]),
        ("SL", Fraction(1, 3), slacks["SL"]),
        ("S36", Fraction(1, 6), slacks["S36"]),
        ("a1", Fraction(1, 6), v["a1"]),
        ("b3", Fraction(1, 2), v["b3"]),
        ("c2", Fraction(1, 6), v["c2"]),
        ("W", Fraction(1, 3), v["W"]),
    ]
    right = add(*(scale(k, vector) for _, k, vector in terms))
    difference = add(
        q0,
        scale(Fraction(-11, 6), v["C"]),
        scale(Fraction(1, 6), v["H"]),
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

    c = 4158
    hcap = 3564
    target = Fraction(11 * c - hcap, 6)
    assert target == 7029
    null = {
        "C": c,
        "H": hcap,
        "n2=p2": 297,
        "n3": 1287,
        "p3=c1": 3564,
        "b1": 594,
        "r1": 4158,
        "all_other_split_pool_variables": 0,
        "asserted_object": False,
    }
    return {
        "identity": (
            "Q0-(11*C-H)/6=2SI/3+4S2/3+SE2/6+2RA/3+SL/3+"
            "S36/6+a1/6+b3/2+c2/6+W/3"
        ),
        "reduced_difference": reduced,
        "target": str(target),
        "integer_Q_lower_bound": int(target),
        "null_control": null,
    }


def derive() -> dict[str, object]:
    geometry = local_geometry()
    result = {
        "claim_label": "AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "local_geometry": geometry,
        "global_rows": {
            "F": "n3+h+g<=1287",
            "J": "J<=3564",
            "S36": "3564-C+n1+2*n2-a3-b3>=0",
        },
        "certificate": certificate(),
        "search_scope": (
            "two fixed Hilton-Milner templates and exact rational algebra; "
            "no graph, code, cover, SAT, LP, configuration, enumeration, "
            "isomorphism, or brute-force search"
        ),
    }
    assert geometry["global_flag_cap"] == 1287
    assert geometry["global_label_cap"] == 3564
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
        print("PASS: Wave196 proof-B audit matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
