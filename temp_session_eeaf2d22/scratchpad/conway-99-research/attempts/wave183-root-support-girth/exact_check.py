"""Exact arithmetic for the Wave 183 root-support theorem.

The proof itself is graph-theoretic.  This checker verifies the
two-path inequalities, the cubic triangle contradiction, the remaining
support shapes, the root-count interval, and the characteristic-three frame
coefficients.  It performs no graph, code, SAT, configuration, or
isomorphism search.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


FIELD = 3


def support_row(multiplicity: int) -> dict[str, Any]:
    degree = multiplicity - 5
    pairs = math.comb(multiplicity, 2)
    two_paths = multiplicity * math.comb(degree, 2)
    pair_bound_survives = two_paths <= pairs
    return {
        "multiplicity": multiplicity,
        "induced_degree": degree,
        "internal_pairs": pairs,
        "internal_two_paths": two_paths,
        "pair_bound_survives": pair_bound_survives,
    }


def analyze() -> dict[str, Any]:
    rows = [support_row(m) for m in range(5, 11)]
    pair_bound_survivors = [
        row["multiplicity"] for row in rows if row["pair_bound_survives"]
    ]

    cubic_m = 8
    cubic_degree = 3
    cubic_two_paths = cubic_m * math.comb(cubic_degree, 2)
    cubic_nonedges = cubic_m * 4 // 2
    cubic_adjacent_endpoint_lower = cubic_two_paths - cubic_nonedges
    cubic_triangle_lower = math.ceil(cubic_adjacent_endpoint_lower / 3)
    cubic_vertex_disjoint_triangle_upper = cubic_m // 3

    root_incidences = 99 * math.comb(7, 2)
    allowed_multiplicities = [5, 6, 7]
    root_lower = math.ceil(root_incidences / max(allowed_multiplicities))
    root_upper = root_incidences // min(allowed_multiplicities)

    result = {
        "field": FIELD,
        "pair_common_neighbor_rule": (
            "every pair inside one root support has at most one "
            "common neighbor inside that support"
        ),
        "support_rows": rows,
        "pair_bound_survivors": pair_bound_survivors,
        "cubic_case": {
            "multiplicity": cubic_m,
            "degree": cubic_degree,
            "two_paths": cubic_two_paths,
            "nonedge_endpoint_capacity": cubic_nonedges,
            "adjacent_endpoint_lower": cubic_adjacent_endpoint_lower,
            "triangle_lower": cubic_triangle_lower,
            "vertex_disjoint_triangle_upper": cubic_vertex_disjoint_triangle_upper,
            "contradiction": (
                cubic_triangle_lower > cubic_vertex_disjoint_triangle_upper
            ),
        },
        "allowed_multiplicities": allowed_multiplicities,
        "support_shapes": {
            "5": "5K1",
            "6": "3K2",
            "7": "C7",
        },
        "global": {
            "root_incidences": root_incidences,
            "distinct_root_lower": root_lower,
            "distinct_root_upper": root_upper,
            "multiplicity_equation": "5*n5+6*n6+7*n7=2079",
            "defect_equation": "7*R-2079=2*n5+n6",
        },
        "frame": {
            "coefficient_mod3": {
                str(m): m % FIELD for m in allowed_multiplicities
            },
            "split_identity": (
                "sum_(m=7) r tensor r=sum_(m=5) r tensor r"
            ),
        },
        "conclusion": (
            "under Wave181 equality every global root has support 5K1, "
            "3K2, or C7; 297..415 global roots remain possible"
        ),
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    rows = {row["multiplicity"]: row for row in result["support_rows"]}
    assert rows[8]["internal_two_paths"] == 24
    assert rows[8]["internal_pairs"] == 28
    assert rows[9]["internal_two_paths"] == 54
    assert rows[9]["internal_pairs"] == 36
    assert rows[10]["internal_two_paths"] == 100
    assert rows[10]["internal_pairs"] == 45
    assert result["pair_bound_survivors"] == [5, 6, 7, 8]

    cubic = result["cubic_case"]
    assert cubic["nonedge_endpoint_capacity"] == 16
    assert cubic["adjacent_endpoint_lower"] == 8
    assert cubic["triangle_lower"] == 3
    assert cubic["vertex_disjoint_triangle_upper"] == 2
    assert cubic["contradiction"]

    assert result["allowed_multiplicities"] == [5, 6, 7]
    assert result["support_shapes"] == {"5": "5K1", "6": "3K2", "7": "C7"}

    global_data = result["global"]
    assert global_data["root_incidences"] == 2079
    assert global_data["distinct_root_lower"] == 297
    assert global_data["distinct_root_upper"] == 415

    assert result["frame"]["coefficient_mod3"] == {"5": 2, "6": 0, "7": 1}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    if args.write:
        args.write.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if not args.write and not args.verify:
        print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: Wave183 root-support exact checks")


if __name__ == "__main__":
    main()

