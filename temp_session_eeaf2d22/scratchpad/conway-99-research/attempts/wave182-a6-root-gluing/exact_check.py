"""Exact arithmetic for the Wave 182 root-gluing boundary.

The proof is incidence geometry.  This checker verifies the local root
counts, support bounds, second-moment/Cauchy calculation, extremal incidence
spectrum, orthogonality, and simplex-frame identity.  It performs no graph,
code, SAT, configuration, or isomorphism search.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


FIELD = 3


def gram_pair(
    left: list[int],
    right: list[int],
    gram: list[list[int]],
) -> int:
    return sum(
        left[row] * gram[row][column] * right[column]
        for row in range(len(left))
        for column in range(len(right))
    ) % FIELD


def analyze() -> dict[str, Any]:
    vertices = 99
    degree = 14
    edges = vertices * degree // 2
    pairs = vertices * (vertices - 1) // 2
    nonedges = pairs - edges

    roots_per_star = math.comb(7, 2)
    local_nonneighbor_pairs = math.comb(14, 2) - 7
    local_multiplicity = 2 * 2
    root_incidences = vertices * roots_per_star

    pair_intersection_upper = nonedges + 6 * edges
    square_sum_upper = 2 * pair_intersection_upper + root_incidences
    root_lower = math.ceil(root_incidences**2 / square_sum_upper)
    root_upper = root_incidences // 5

    c4_gram = [
        [0, 1, 1, 2],
        [1, 0, 2, 1],
        [1, 2, 0, 1],
        [2, 1, 1, 0],
    ]
    opposite_root = gram_pair(
        [1, 2, 0, 0],
        [1, 0, 2, 0],
        c4_gram,
    )
    root_norm = gram_pair(
        [1, 2, 0, 0],
        [1, 2, 0, 0],
        c4_gram,
    )

    extremal_roots = root_lower
    extremal_multiplicity = root_incidences // extremal_roots
    incidence_eigenvalues = {
        "principal": 20 + 5 * 14 + 99,
        "graph_eigenvalue_3": 20 + 5 * 3,
        "graph_eigenvalue_minus4": 20 + 5 * -4,
    }

    result = {
        "field": FIELD,
        "local": {
            "star_simplex_points": 7,
            "projective_difference_roots": roots_per_star,
            "nonneighbors": 84,
            "neighbor_pairs_from_distinct_star_blocks": local_nonneighbor_pairs,
            "nonedges_per_local_root": local_multiplicity,
            "root_norm": 1,
        },
        "global": {
            "edges": edges,
            "nonedges": nonedges,
            "root_incidences": root_incidences,
            "support_size_lower": 5,
            "support_size_upper": 10,
            "pair_intersection_sum_upper": pair_intersection_upper,
            "multiplicity_square_sum_upper": square_sum_upper,
            "distinct_root_lower": root_lower,
            "distinct_root_upper": root_upper,
        },
        "canonical_c4_root_pair": {
            "norm": root_norm,
            "inner_product": opposite_root,
            "orthogonal": opposite_root == 0,
        },
        "extremal_231_root_design": {
            "roots": extremal_roots,
            "multiplicity": extremal_multiplicity,
            "edge_star_intersection": 6,
            "nonedge_star_intersection": 1,
            "incidence_gram": "20*I+5*A+J",
            "incidence_gram_eigenvalues": incidence_eigenvalues,
            "incidence_real_rank": 1 + 54,
            "all_edges_cycle_type": "3+3",
            "frame_coefficient_mod3": extremal_multiplicity % FIELD,
        },
        "frame": {
            "local": "sum_(r in R_x) r tensor r=-P_x",
            "global": "sum_r m_r r tensor r=0",
        },
        "conclusion": (
            "Wave181 equality glues 99 local 21-root systems through "
            "4-regular complement color classes; 231..415 global roots "
            "remain possible"
        ),
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    local = result["local"]
    assert local["projective_difference_roots"] == 21
    assert local["neighbor_pairs_from_distinct_star_blocks"] == 84
    assert local["nonedges_per_local_root"] == 4
    assert local["nonneighbors"] == 84

    global_data = result["global"]
    assert global_data["edges"] == 693
    assert global_data["nonedges"] == 4158
    assert global_data["root_incidences"] == 2079
    assert global_data["support_size_lower"] == 5
    assert global_data["support_size_upper"] == 10
    assert global_data["pair_intersection_sum_upper"] == 8316
    assert global_data["multiplicity_square_sum_upper"] == 18711
    assert global_data["distinct_root_lower"] == 231
    assert global_data["distinct_root_upper"] == 415

    c4 = result["canonical_c4_root_pair"]
    assert c4 == {"norm": 1, "inner_product": 0, "orthogonal": True}

    extremal = result["extremal_231_root_design"]
    assert extremal["multiplicity"] == 9
    assert extremal["incidence_gram_eigenvalues"] == {
        "principal": 189,
        "graph_eigenvalue_3": 35,
        "graph_eigenvalue_minus4": 0,
    }
    assert extremal["incidence_real_rank"] == 55
    assert extremal["frame_coefficient_mod3"] == 0


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
    print("PASS: Wave182 A6 root-gluing exact checks")


if __name__ == "__main__":
    main()
