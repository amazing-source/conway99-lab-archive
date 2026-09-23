#!/usr/bin/env python3
"""Independent exact verifier for the Wave 72 order-11 fixed-point theorem.

This module does not import or execute discovery code.  It reconstructs the
fixed-graph arithmetic, seals an independent result, and only then optionally
compares selected mathematical fields with the discovery JSON.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


V = 99
K = 14
LAMBDA = 1
MU = 2
P = 11
SCHEMA = "wave72-order11-independent-v1"


def semantic_sha256(payload: dict[str, Any]) -> str:
    core = {key: value for key, value in payload.items() if key != "semantic_sha256"}
    raw = json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def fixed_count_candidates() -> list[int]:
    """Fixed-point counts allowed by 1- or P-element vertex orbits."""
    return [f for f in range(V + 1) if (V - f) % P == 0]


def fixed_degree_options() -> list[int]:
    """Fixed-neighbor counts allowed in an invariant K-element neighborhood."""
    return [d for d in range(K + 1) if (K - d) % P == 0]


def invariant_small_set_is_pointwise_fixed(size: int) -> bool:
    """An invariant set smaller than P has no nontrivial C_P orbit."""
    if not 0 <= size < P:
        raise ValueError("the lemma is scoped to set sizes in [0,P)")
    return True


def row_sum_rhs(f: int) -> int:
    """Row sum forced by diagonal, adjacent, and nonadjacent pair counts."""
    return 2 * f - 2


def high_type_neighbor_count(f: int, degree: int) -> int | None:
    """Solve 14*x + 3*(degree-x) = 2*f-2 exactly."""
    solutions = [
        x
        for x in range(degree + 1)
        if 14 * x + 3 * (degree - x) == row_sum_rhs(f)
    ]
    if not solutions:
        return None
    if len(solutions) != 1:
        raise AssertionError("the coefficient difference 14-3 must give uniqueness")
    return solutions[0]


def enumerate_fixed_graph_relaxation() -> list[dict[str, int]]:
    """Enumerate every degree-type model satisfying necessary graph equations.

    A low vertex has fixed degree 3 and a high vertex fixed degree 14.  Besides
    the row identity, this independent relaxation enforces cross-edge balance,
    parity, and elementary simple-graph capacity constraints.  Rejecting every
    positive nonidentity model is therefore a valid necessary-condition
    certificate, not an existence search.
    """

    models: list[dict[str, int]] = []
    for f in fixed_count_candidates():
        for low_vertices in range(f + 1):
            high_vertices = f - low_vertices

            if low_vertices and 3 > f - 1:
                continue
            if high_vertices and 14 > f - 1:
                continue

            low_to_high = (
                high_type_neighbor_count(f, 3) if low_vertices else 0
            )
            high_to_high = (
                high_type_neighbor_count(f, 14) if high_vertices else 0
            )
            if low_to_high is None or high_to_high is None:
                continue

            low_to_low = 3 - low_to_high
            high_to_low = 14 - high_to_high

            if low_vertices and not 0 <= low_to_high <= high_vertices:
                continue
            if high_vertices and not 0 <= high_to_low <= low_vertices:
                continue
            if low_vertices and not 0 <= low_to_low <= low_vertices - 1:
                continue
            if high_vertices and not 0 <= high_to_high <= high_vertices - 1:
                continue
            if low_vertices * low_to_high != high_vertices * high_to_low:
                continue
            if (low_vertices * low_to_low) % 2:
                continue
            if (high_vertices * high_to_high) % 2:
                continue

            models.append(
                {
                    "f": f,
                    "degree3_vertices": low_vertices,
                    "degree14_vertices": high_vertices,
                    "degree14_neighbors_of_degree3_vertex": low_to_high,
                    "degree14_neighbors_of_degree14_vertex": high_to_high,
                }
            )
    return models


def case_audit() -> dict[str, Any]:
    """Expose the proof's hostile boundary cases."""
    return {
        "f11": {
            "degree14_possible_in_simple_graph": False,
            "all_degree3_lhs": 3 * 3,
            "required_rhs": row_sum_rhs(11),
            "contradiction": 3 * 3 != row_sum_rhs(11),
        },
        "f22": {
            "degree14_neighbors_of_degree3": high_type_neighbor_count(22, 3),
            "degree14_neighbors_of_degree14": high_type_neighbor_count(22, 14),
            "cross_edge_equation": "3*degree3_vertices=14*degree14_vertices",
            "integer_partition_solutions": [
                [a, b]
                for a in range(23)
                for b in range(23)
                if a + b == 22 and 3 * a == 14 * b
            ],
        },
        "f99": {
            "surviving_model_is_identity": True,
            "permutation_order": 1,
            "excluded_by_exact_order_11_scope": True,
        },
    }


def build_result() -> dict[str, Any]:
    models = enumerate_fixed_graph_relaxation()
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "claim_label": "VERIFIED",
        "parameters": {
            "v": V,
            "k": K,
            "lambda": LAMBDA,
            "mu": MU,
            "prime": P,
        },
        "fixed_count_candidates": fixed_count_candidates(),
        "fixed_degree_options": fixed_degree_options(),
        "small_common_neighbor_sets_pointwise_fixed": {
            "adjacent_pair_size": LAMBDA,
            "nonadjacent_pair_size": MU,
            "both_less_than_prime": LAMBDA < P and MU < P,
        },
        "two_step_identity": "sum_neighbor_fixed_degrees=2*f-2",
        "case_audit": case_audit(),
        "feasible_fixed_degree_models": models,
        "positive_nonidentity_models": [
            model for model in models if 0 < model["f"] < V
        ],
        "primary_conclusion": "every_exact_order_11_automorphism_is_fixed_point_free",
        "fixed_free_orbit_count": V // P,
        "conditional_implication": {
            "premise": "separate_complete_semiregular_C11_exclusion",
            "no_order11_automorphism": True,
            "no_vertex_transitive_realization": True,
            "group_steps": [
                "orbit_stabilizer_makes_11_divide_automorphism_group_order",
                "cauchy_supplies_an_element_of_order_11",
            ],
        },
        "identity_scope": {
            "identity_satisfies_g_to_11_equals_identity": True,
            "identity_order": 1,
            "identity_not_covered_by_primary_theorem": True,
        },
        "limitations": [
            "wave69_not_verified_here",
            "conditional_symmetry_exclusion_does_not_exclude_asymmetric_graphs",
            "unrestricted_conway_99_remains_UNKNOWN",
            "novelty_not_assessed",
        ],
    }
    result["semantic_sha256"] = semantic_sha256(result)
    return result


def verify_result(payload: dict[str, Any]) -> None:
    assert payload == build_result()
    assert payload["semantic_sha256"] == semantic_sha256(payload)
    assert payload["fixed_degree_options"] == [3, 14]
    assert payload["small_common_neighbor_sets_pointwise_fixed"] == {
        "adjacent_pair_size": 1,
        "nonadjacent_pair_size": 2,
        "both_less_than_prime": True,
    }
    assert payload["positive_nonidentity_models"] == []
    assert [model["f"] for model in payload["feasible_fixed_degree_models"]] == [
        0,
        99,
    ]
    assert payload["case_audit"]["f11"]["contradiction"] is True
    assert payload["case_audit"]["f22"]["integer_partition_solutions"] == []
    assert payload["case_audit"]["f99"]["permutation_order"] == 1


def verify_inventory(repo: Path, inventory: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with inventory.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            path = repo / row["path"]
            raw = path.read_bytes()
            actual = hashlib.sha256(raw).hexdigest()
            entry = {
                "path": row["path"],
                "expected_bytes": int(row["bytes"]),
                "actual_bytes": len(raw),
                "expected_sha256": row["sha256"],
                "actual_sha256": actual,
                "match": len(raw) == int(row["bytes"]) and actual == row["sha256"],
            }
            rows.append(entry)
    if not rows or not all(row["match"] for row in rows):
        raise AssertionError("discovery inventory changed after preinspection freeze")
    return rows


def compare_discovery(independent: dict[str, Any], discovery: dict[str, Any]) -> dict[str, Any]:
    mappings = {
        "parameters": "parameters",
        "fixed_count_candidates": "fixed_count_candidates",
        "fixed_degree_options": "fixed_degree_options",
        "two_step_identity": "two_step_identity",
        "feasible_fixed_degree_models": "feasible_fixed_degree_models",
        "fixed_free_orbit_count": "fixed_free_orbit_count",
    }
    comparisons = []
    for independent_key, discovery_key in mappings.items():
        match = independent[independent_key] == discovery[discovery_key]
        comparisons.append(
            {
                "independent_key": independent_key,
                "discovery_key": discovery_key,
                "match": match,
            }
        )
    result = {
        "schema": "wave72-order11-comparison-v1",
        "compared_fields": len(comparisons),
        "mismatches": sum(not row["match"] for row in comparisons),
        "comparisons": comparisons,
        "scope_note": "discovery code was not imported or executed by this comparison",
    }
    if result["mismatches"]:
        raise AssertionError("independent/discovery mathematical field mismatch")
    return result


def write_canonical(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    package_dir = Path(__file__).resolve().parent
    parser.add_argument(
        "--output", type=Path, default=package_dir / "independent-results.json"
    )
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--repo", type=Path, default=package_dir.parents[1])
    parser.add_argument(
        "--inventory",
        type=Path,
        default=package_dir / "discovery-inventory-preinspection.tsv",
    )
    parser.add_argument("--discovery-results", type=Path)
    parser.add_argument("--comparison-output", type=Path)
    args = parser.parse_args()

    inventory_rows = verify_inventory(args.repo, args.inventory)
    expected = build_result()

    if args.verify:
        actual = json.loads(args.output.read_text(encoding="utf-8"))
        verify_result(actual)
        assert actual == expected
    else:
        write_canonical(args.output, expected)

    comparison = None
    if args.discovery_results is not None:
        discovery = json.loads(args.discovery_results.read_text(encoding="utf-8"))
        comparison = compare_discovery(expected, discovery)
        if args.comparison_output is not None:
            write_canonical(args.comparison_output, comparison)

    print(
        json.dumps(
            {
                "status": "PASS",
                "semantic_sha256": expected["semantic_sha256"],
                "inventory_files_unchanged": len(inventory_rows),
                "positive_nonidentity_models": 0,
                "comparison_mismatches": (
                    None if comparison is None else comparison["mismatches"]
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
