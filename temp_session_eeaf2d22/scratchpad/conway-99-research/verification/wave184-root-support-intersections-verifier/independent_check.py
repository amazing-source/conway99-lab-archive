"""Independent exact arithmetic certificate for Wave 184.

The structural proofs are in audit.md.  This module performs no graph or
code enumeration.
"""

from __future__ import annotations

import json


def build_results() -> dict[str, object]:
    sub_twelve: list[dict[str, int]] = []
    for n7 in (0, 1):
        maximum_n6 = (11 - 7 * n7) // 3
        for n6 in range(maximum_n6 + 1):
            sub_twelve.append(
                {
                    "n6": n6,
                    "n7": n7,
                    "E": 3 * n6 + 7 * n7,
                    "incidence_residue_mod5": (n6 + 2 * n7) % 5,
                }
            )

    sharpness = {"n5": 411, "n6": 4, "n7": 0}
    sharpness_incidence = (
        5 * sharpness["n5"]
        + 6 * sharpness["n6"]
        + 7 * sharpness["n7"]
    )
    sharpness_edge_count = 3 * sharpness["n6"] + 7 * sharpness["n7"]

    canonical_projective = 2079
    new_projective_lower = 12
    total_projective_lower = canonical_projective + new_projective_lower
    scalar_representatives = 2

    return {
        "verdict": "VERIFIED_WITH_SCOPE",
        "support_intersections": {
            "maximum_for_distinct_roots": 2,
            "size_two_type": "graph edge",
            "reason": "nonedge uniqueness plus triangle-free supports",
            "root_pair_identity": (
                "number meeting twice=sum_(xy in E(G)) binom(c_xy,2)"
            ),
        },
        "edge_root_circuit": {
            "shared_triangle_excluded": True,
            "distinct_columns": 4,
            "nonzero_coefficients": 4,
            "dual_distance_lower": 4,
            "weight": 4,
            "projective_root_recoverable": True,
        },
        "injectivity": {
            "different_roots_same_edge": True,
            "different_graph_edges": True,
            "disjoint_from_canonical_nonedge_conics": True,
        },
        "support_edge_counts": {"5K1": 0, "3K2": 3, "C7": 7},
        "edge_root_circuit_count": "E=3*n6+7*n7",
        "root_incidence_equation": "5*n5+6*n6+7*n7=2079",
        "mod5_constraint": "n6+2*n7=4 mod 5",
        "sub_twelve_candidates": sub_twelve,
        "sub_twelve_valid_residue_count": sum(
            row["incidence_residue_mod5"] == 4 for row in sub_twelve
        ),
        "edge_projective_weight4_lower": new_projective_lower,
        "scalar_sharpness": {
            "distribution": sharpness,
            "root_incidences": sharpness_incidence,
            "E": sharpness_edge_count,
            "geometric_construction": False,
        },
        "weight4_count": {
            "canonical_projective": canonical_projective,
            "new_edge_projective_lower": new_projective_lower,
            "total_projective_lower": total_projective_lower,
            "nonzero_scalars_per_projective_class": scalar_representatives,
            "B4_lower": scalar_representatives * total_projective_lower,
        },
        "endpoint_status": "UNKNOWN",
    }


if __name__ == "__main__":
    print(json.dumps(build_results(), indent=2, sort_keys=True))
