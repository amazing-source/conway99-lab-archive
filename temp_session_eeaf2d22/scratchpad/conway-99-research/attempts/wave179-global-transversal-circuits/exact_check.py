"""Arithmetic and finite-case bookkeeping for Wave 179.

The proof itself is incidence-theoretic.  This checker records only the
closed-form pair counts, multiplicity cases, and projective scalar factor.
It performs no construction search.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def analyze() -> dict[str, Any]:
    vertices = 99
    degree = 14
    edges = vertices * degree // 2
    pairs = vertices * (vertices - 1) // 2
    nonedges = pairs - edges
    max_pair_multiplicity = 3
    edge_projective_circuits = edges
    nonedge_projective_circuits = nonedges // max_pair_multiplicity
    projective_circuits = (
        edge_projective_circuits + nonedge_projective_circuits
    )
    return {
        "graph_parameters_used": {
            "vertices": vertices,
            "degree": degree,
            "lambda": 1,
        },
        "pair_counts": {
            "edges": edges,
            "nonedges": nonedges,
            "all_unordered_pairs": pairs,
        },
        "circuit_support_range": [4, 9],
        "edge_circuit_support_range": [4, 8],
        "realizing_pair_multiplicity": {
            "pairwise_intersecting_case_upper": 3,
            "disjoint_case_upper": 2,
            "global_upper": max_pair_multiplicity,
            "balanced_edge_circuit_global_upper": 1,
        },
        "edge_projective_circuit_lower_bound": edge_projective_circuits,
        "additional_nonedge_projective_circuit_lower_bound": (
            nonedge_projective_circuits
        ),
        "projective_circuit_lower_bound": projective_circuits,
        "ternary_nonzero_scalars_per_projective_class": 2,
        "dual_word_lower_bound": 2 * projective_circuits,
        "dual_word_inequality": "B_4+B_5+B_6+B_7+B_8+B_9>=4158",
        "retained_edge_inequality": "B_4+B_6+B_8>=1386",
        "conclusion": (
            "isolated edge circuits plus bounded-multiplicity nonedge "
            "circuits force at least 2079 projective circuits of size "
            "4..9; the conditional endpoint remains unexcluded"
        ),
    }


def verify(data: dict[str, Any]) -> None:
    counts = data["pair_counts"]
    assert counts == {
        "edges": 693,
        "nonedges": 4158,
        "all_unordered_pairs": 4851,
    }
    multiplicity = data["realizing_pair_multiplicity"]
    assert multiplicity["pairwise_intersecting_case_upper"] == 3
    assert multiplicity["disjoint_case_upper"] == 2
    assert multiplicity["global_upper"] == 3
    assert multiplicity["balanced_edge_circuit_global_upper"] == 1
    assert counts["nonedges"] % multiplicity["global_upper"] == 0
    assert data["edge_projective_circuit_lower_bound"] == 693
    assert data["additional_nonedge_projective_circuit_lower_bound"] == 1386
    assert data["projective_circuit_lower_bound"] == 2079
    assert data["dual_word_lower_bound"] == 4158
    assert (
        data["dual_word_inequality"]
        == "B_4+B_5+B_6+B_7+B_8+B_9>=4158"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    data = analyze()
    verify(data)
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == data
    if args.write:
        args.write.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if not args.write and not args.verify:
        print(json.dumps(data, indent=2, sort_keys=True))
    print("PASS: Wave179 exact-transversal count checks")


if __name__ == "__main__":
    main()
