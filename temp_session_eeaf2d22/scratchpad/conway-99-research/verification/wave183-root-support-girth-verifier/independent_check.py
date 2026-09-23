"""Independent exact arithmetic checks for the Wave 183 verifier.

This script does not enumerate graphs.  The structural implications are
proved in audit.md; here we reproduce every numerical boundary exactly.
"""

from __future__ import annotations

import json
import math


def support_rows() -> list[dict[str, int | bool]]:
    rows: list[dict[str, int | bool]] = []
    for multiplicity in range(5, 11):
        degree = multiplicity - 5
        paths = multiplicity * math.comb(degree, 2)
        pairs = math.comb(multiplicity, 2)
        rows.append(
            {
                "multiplicity": multiplicity,
                "induced_degree": degree,
                "internal_two_paths": paths,
                "internal_pairs": pairs,
                "pair_bound_survives": paths <= pairs,
            }
        )
    return rows


def build_results() -> dict[str, object]:
    rows = support_rows()
    survivors = [
        int(row["multiplicity"])
        for row in rows
        if bool(row["pair_bound_survives"])
    ]

    cubic_vertices = 8
    cubic_degree = 3
    complement_degree = 4
    cubic_paths = cubic_vertices * math.comb(cubic_degree, 2)
    nonedge_capacity = cubic_vertices * complement_degree // 2
    adjacent_lower = cubic_paths - nonedge_capacity
    triangle_lower = math.ceil(adjacent_lower / 3)
    disjoint_triangle_upper = cubic_vertices // 3

    incidences = 2079
    min_support = 5
    max_support = 7

    return {
        "verdict": "VERIFIED_WITH_SCOPE",
        "pair_common_neighbor_rule": {
            "adjacent_case": "lambda=1",
            "nonadjacent_case": (
                "canonical-C4 orthogonality plus exact nonedge-root uniqueness"
            ),
            "maximum_inside_support": 1,
        },
        "support_rows": rows,
        "pair_bound_survivors": survivors,
        "cubic_case": {
            "multiplicity": cubic_vertices,
            "degree": cubic_degree,
            "two_paths": cubic_paths,
            "nonedge_endpoint_capacity": nonedge_capacity,
            "adjacent_endpoint_lower": adjacent_lower,
            "triangle_edge_divisor": 3,
            "triangle_lower": triangle_lower,
            "triangles_vertex_disjoint": True,
            "vertex_disjoint_triangle_upper": disjoint_triangle_upper,
            "contradiction": triangle_lower > disjoint_triangle_upper,
        },
        "allowed_multiplicities": [5, 6, 7],
        "support_shapes": {"5": "5K1", "6": "3K2", "7": "C7"},
        "global": {
            "root_incidences": incidences,
            "distinct_root_lower": math.ceil(incidences / max_support),
            "distinct_root_upper": incidences // min_support,
            "multiplicity_equation": "5*n5+6*n6+7*n7=2079",
            "defect_equation": "7*R-2079=2*n5+n6",
        },
        "frame": {
            "coefficient_mod3": {"5": 5 % 3, "6": 6 % 3, "7": 7 % 3},
            "split_identity": (
                "sum_(m=7) r tensor r=sum_(m=5) r tensor r"
            ),
            "contradiction_obtained": False,
        },
        "endpoint_status": "UNKNOWN",
    }


if __name__ == "__main__":
    print(json.dumps(build_results(), indent=2, sort_keys=True))
