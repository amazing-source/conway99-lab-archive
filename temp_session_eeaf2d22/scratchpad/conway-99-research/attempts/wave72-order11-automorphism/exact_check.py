#!/usr/bin/env python3
"""Exact arithmetic audit for the Wave 72 fixed-point theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


V = 99
K = 14
LAMBDA = 1
MU = 2
P = 11
SCHEMA = "wave72-order11-fixed-point-v1"


def semantic_sha256(payload: dict[str, Any]) -> str:
    core = {key: value for key, value in payload.items() if key != "semantic_sha256"}
    raw = json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def fixed_degree_options() -> list[int]:
    """Possible fixed-neighbor counts in an invariant K-element neighborhood."""
    return [d for d in range(K + 1) if (K - d) % P == 0]


def local_type_solution(f: int, degree: int) -> int | None:
    """Number of degree-14 neighbors forced by the two-step identity."""
    for high_neighbors in range(degree + 1):
        total = 14 * high_neighbors + 3 * (degree - high_neighbors)
        if total == 2 * f - 2:
            return high_neighbors
    return None


def feasible_fixed_degree_models() -> list[dict[str, int]]:
    """Enumerate the exact integer relaxation implied by the human proof.

    A model specifies counts a,b of fixed vertices of H-degree 3 and 14.
    Local equations force the number of degree-14 neighbors for each type.
    Degree bounds, parity, and cross-edge balance are all enforced.
    """

    models: list[dict[str, int]] = []
    for f in range(0, V + 1, P):
        for a in range(f + 1):
            b = f - a

            if a and 3 > f - 1:
                continue
            if b and 14 > f - 1:
                continue

            x3 = local_type_solution(f, 3) if a else 0
            x14 = local_type_solution(f, 14) if b else 0
            if (a and x3 is None) or (b and x14 is None):
                continue
            assert x3 is not None and x14 is not None

            # A degree-3 vertex has x3 neighbors in the degree-14 class.
            # A degree-14 vertex has 14-x14 neighbors in the degree-3 class.
            if a * x3 != b * (14 - x14):
                continue

            # Same-type half-edge counts must form ordinary undirected edges.
            if a * (3 - x3) % 2:
                continue
            if b * x14 % 2:
                continue

            models.append(
                {
                    "f": f,
                    "degree3_vertices": a,
                    "degree14_vertices": b,
                    "degree14_neighbors_of_degree3_vertex": x3,
                    "degree14_neighbors_of_degree14_vertex": x14,
                }
            )
    return models


def build_result() -> dict[str, Any]:
    models = feasible_fixed_degree_models()
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "claim_label": "DERIVED",
        "parameters": {"v": V, "k": K, "lambda": LAMBDA, "mu": MU, "prime": P},
        "fixed_count_candidates": list(range(0, V + 1, P)),
        "fixed_degree_options": fixed_degree_options(),
        "two_step_identity": "sum_neighbor_fixed_degrees=2*f-2",
        "feasible_fixed_degree_models": models,
        "nonidentity_order11_positive_fixed_models": [
            model for model in models if 0 < model["f"] < V
        ],
        "conclusion": "every_order_11_automorphism_is_fixed_point_free",
        "fixed_free_orbit_count": V // P,
        "conditional_corollaries": [
            "wave69_semiregular_exclusion_plus_this_theorem_excludes_order11_automorphisms",
            "that_combination_plus_orbit_stabilizer_and_cauchy_excludes_vertex_transitivity",
        ],
        "limitations": [
            "discovery_not_independent_verification",
            "wave69_not_reverified_here",
            "no_global_nonexistence_claim",
        ],
    }
    result["semantic_sha256"] = semantic_sha256(result)
    return result


def verify_result(payload: dict[str, Any]) -> None:
    assert payload["schema"] == SCHEMA
    assert payload["parameters"] == {
        "v": 99,
        "k": 14,
        "lambda": 1,
        "mu": 2,
        "prime": 11,
    }
    assert payload["fixed_count_candidates"] == [0, 11, 22, 33, 44, 55, 66, 77, 88, 99]
    assert payload["fixed_degree_options"] == [3, 14]
    assert payload["feasible_fixed_degree_models"] == [
        {
            "f": 0,
            "degree3_vertices": 0,
            "degree14_vertices": 0,
            "degree14_neighbors_of_degree3_vertex": 0,
            "degree14_neighbors_of_degree14_vertex": 0,
        },
        {
            "f": 99,
            "degree3_vertices": 0,
            "degree14_vertices": 99,
            "degree14_neighbors_of_degree3_vertex": 0,
            "degree14_neighbors_of_degree14_vertex": 14,
        },
    ]
    assert payload["nonidentity_order11_positive_fixed_models"] == []
    assert payload["fixed_free_orbit_count"] == 9
    assert payload["semantic_sha256"] == semantic_sha256(payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument(
        "--artifact",
        type=Path,
        default=Path(__file__).with_name("exact-results.json"),
    )
    args = parser.parse_args()

    expected = build_result()
    if args.verify:
        actual = json.loads(args.artifact.read_text(encoding="utf-8"))
        verify_result(actual)
        assert actual == expected
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "schema": SCHEMA,
                    "semantic_sha256": actual["semantic_sha256"],
                    "surviving_models": len(actual["feasible_fixed_degree_models"]),
                    "nonidentity_positive_fixed_models": 0,
                },
                sort_keys=True,
            )
        )
        return 0

    print(json.dumps(expected, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
