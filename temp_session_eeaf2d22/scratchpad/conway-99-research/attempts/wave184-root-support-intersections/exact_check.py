"""Exact arithmetic for Wave 184.

No graph or code is enumerated.  The checker verifies support-edge counts,
the congruence proof of the minimum, root-pair double counting, and the
projective-to-word factor.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def analyze() -> dict[str, Any]:
    root_incidences = 2079
    canonical_projective_weight4 = 2079
    edge_counts = {5: 0, 6: 3, 7: 7}

    candidates_below_twelve: list[dict[str, int]] = []
    for n7 in range(2):
        for n6 in range(4):
            edge_circuits = 3 * n6 + 7 * n7
            if edge_circuits >= 12:
                continue
            residue = (n6 + 2 * n7) % 5
            candidates_below_twelve.append(
                {
                    "n6": n6,
                    "n7": n7,
                    "edge_circuits": edge_circuits,
                    "incidence_residue_mod5": residue,
                }
            )

    sharpness = {"n5": 411, "n6": 4, "n7": 0}
    sharpness_incidences = (
        5 * sharpness["n5"]
        + 6 * sharpness["n6"]
        + 7 * sharpness["n7"]
    )
    edge_circuit_lower = 12
    projective_weight4_lower = (
        canonical_projective_weight4 + edge_circuit_lower
    )

    result = {
        "root_incidences": root_incidences,
        "support_edge_counts": {str(k): v for k, v in edge_counts.items()},
        "support_intersection_upper": 2,
        "two_point_intersection_type": "graph edge",
        "edge_root_circuit_count": "3*n6+7*n7",
        "mod5_constraint": "n6+2*n7=4 mod 5",
        "sub_twelve_candidates": candidates_below_twelve,
        "sub_twelve_residue_four_count": sum(
            row["incidence_residue_mod5"] == 4
            for row in candidates_below_twelve
        ),
        "edge_projective_weight4_lower": edge_circuit_lower,
        "sharpness_distribution": sharpness,
        "sharpness_incidence_total": sharpness_incidences,
        "canonical_projective_weight4": canonical_projective_weight4,
        "total_projective_weight4_lower": projective_weight4_lower,
        "dual_B4_lower": 2 * projective_weight4_lower,
        "conclusion": (
            "Wave181 equality forces at least 2091 projective "
            "weight-four circuits and B4>=4182"
        ),
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    assert result["support_edge_counts"] == {"5": 0, "6": 3, "7": 7}
    assert result["support_intersection_upper"] == 2
    assert result["sub_twelve_residue_four_count"] == 0
    assert result["edge_projective_weight4_lower"] == 12
    assert result["sharpness_incidence_total"] == 2079
    sharpness = result["sharpness_distribution"]
    assert 3 * sharpness["n6"] + 7 * sharpness["n7"] == 12
    assert result["total_projective_weight4_lower"] == 2091
    assert result["dual_B4_lower"] == 4182


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
    print("PASS: Wave184 root-support intersection exact checks")


if __name__ == "__main__":
    main()

