"""Exact arithmetic checks for Wave 185.

This checks the hand-derived local transition table, capacity consequence,
root multiplicity parameterization, and rainbow-triangle arithmetic.  It does
not search for a graph or a transition configuration.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FORMAT = "wave185-local-a6-transition-collapse-v1"


def transition_row(internal_degree: int) -> dict[str, int]:
    if internal_degree not in (0, 1):
        raise AssertionError("prism-free four-cell has internal degree 0 or 1")
    incident_total = 4 - 2 * internal_degree
    transition = 2
    incident_disjoint = incident_total - transition
    orthogonal = 10 - internal_degree - incident_disjoint
    row = {
        "internal": internal_degree,
        "incident_transition": transition,
        "incident_disjoint": incident_disjoint,
        "orthogonal_disjoint": orthogonal,
    }
    if sum(row.values()) != 12:
        raise AssertionError("transition row lost residual degree 12")
    return row


def multiplicity_profiles() -> list[dict[str, int]]:
    profiles: list[dict[str, int]] = []
    for u in range(67):
        n5 = 15 + 6 * u
        n6 = 334 - 5 * u
        if n6 < 0 or 5 * n5 + 6 * n6 != 2079:
            raise AssertionError("invalid multiplicity profile")
        profiles.append(
            {"u": u, "n5": n5, "n6": n6, "roots": n5 + n6}
        )
    return profiles


def derive() -> dict[str, Any]:
    type5 = transition_row(0)
    type6 = transition_row(1)
    profiles = multiplicity_profiles()
    minimum_companions = 5 * 2
    raw_n5_floor = 1 + minimum_companions
    congruence_floor = min(n for n in range(raw_n5_floor, 100) if n % 6 == 3)
    min_n6 = min(row["n6"] for row in profiles)
    monochromatic_max = 4158 - 4 * min_n6
    rainbow_min = 98406 - monochromatic_max
    return {
        "format": FORMAT,
        "conditional_status": "DERIVED",
        "global_status": "UNKNOWN",
        "cell": {
            "possible_internal_opposite_corner_edges": 2,
            "maximum_internal_degree": 1,
            "multiplicity_seven_excluded": True,
        },
        "transition_rows": {"m5": type5, "m6": type6},
        "incident_disjoint_capacity": 6,
        "type5_companions": {
            "per_support_vertex": 2,
            "support_size": 5,
            "distinct_companions": minimum_companions,
            "raw_n5_floor": raw_n5_floor,
            "n5_mod_6": 3,
            "congruence_n5_floor": congruence_floor,
        },
        "multiplicity_equation": "5*n5+6*n6=2079",
        "profiles": profiles,
        "root_interval": [
            min(row["roots"] for row in profiles),
            max(row["roots"] for row in profiles),
        ],
        "rainbow_triangles": {
            "complement_total": 98406,
            "minimum_n6": min_n6,
            "maximum_monochromatic": monochromatic_max,
            "minimum_rainbow": rainbow_min,
        },
        "limitations": [
            "No transition configuration or graph was searched for.",
            "The arithmetic profiles are not constructions.",
            "Wave181 equality and Conway-99 remain UNKNOWN.",
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
        print(f"PASS Wave 185 exact verification: {args.verify}")
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
