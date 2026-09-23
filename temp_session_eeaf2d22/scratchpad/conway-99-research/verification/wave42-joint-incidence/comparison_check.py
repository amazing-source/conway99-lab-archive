#!/usr/bin/env python3
"""Post-freeze comparison of independent and discovery Wave 42 results."""

from __future__ import annotations

import argparse
import copy
import itertools
import json
from collections import Counter
from pathlib import Path

import independent_check as independent


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave42-joint-incidence" / "exact-results.json"
DISCOVERY_SHA256 = "40bfee8fd082972d5e7ea0a5ef959be2b1b5c75232076ec8510d42b6c98be9cc"
INDEPENDENT = HERE / "independent-results.json"
INDEPENDENT_SHA256 = "4032826b875d8ebadcd4d9b864a9789068546e33705c62970001c9011ba76b13"


def load_json_at_hash(path: Path, expected: str) -> dict:
    actual = independent.sha256_file(path)
    if actual != expected:
        raise ValueError(f"hash mismatch for {path}: {actual}")
    return json.loads(path.read_text(encoding="utf-8"))


def core_four_cycles(adjacency: list[list[int]]) -> int:
    opposite_pairs = 0
    for u, v in itertools.combinations(range(36), 2):
        common = sum(adjacency[u][w] * adjacency[v][w] for w in range(36))
        opposite_pairs += common * (common - 1) // 2
    if opposite_pairs % 2:
        raise ValueError("odd opposite-pair four-cycle total")
    return opposite_pairs // 2


def validate_discovery_two_fibre(discovery: dict) -> dict:
    data = independent.load_frozen_input()
    core = independent.reconstruct_core(data)
    adjacency = core["adjacency"]
    q = independent.derive_gram(adjacency)
    pairs = independent.fibre_pairs(q)
    permutation = discovery["two_fibre_positive_control"]["certificate"]
    payload = {
        "format": "wave42-discovery-two-fibre-adapter-v1",
        "scope": discovery["two_fibre_positive_control"]["scope"],
        "left_fibre": 0,
        "right_fibre": 1,
        "left_pairs_lexicographic": [list(x) for x in pairs[0]],
        "right_pairs_lexicographic": [list(x) for x in pairs[1]],
        "right_pair_index_for_each_left_pair": permutation,
        "target_gram_block": [[q[u][v] for v in range(12, 24)] for u in range(12)],
    }
    payload["target_gram_block_sha256"] = independent.digest_json(
        payload["target_gram_block"]
    )
    payload["certificate_sha256"] = independent.digest_json(payload)
    independent.verify_two_fibre_payload(payload)
    return {
        "discovery_certificate_valid": True,
        "discovery_certificate_adapter_sha256": payload["certificate_sha256"],
        "independent_certificate_is_distinct": (
            permutation != list(independent.TWO_FIBRE_PERMUTATION)
        ),
    }


def compare_payloads(independent_result: dict, discovery: dict) -> dict:
    if discovery["input"][
        "verification/wave41-allquotient-lifts/independent-results.json"
    ] != independent_result["input"]["sha256"]:
        raise ValueError("discovery and verifier used different Wave 41 inputs")
    if discovery["input"]["canonical_mask"] != independent_result["input"]["selected_mask"]:
        raise ValueError("discovery and verifier selected different masks")

    independent_components = independent_result["reconstruction"]["component_vertices"]
    discovery_core = discovery["canonical_core"]
    if discovery_core["components"] != independent_components:
        raise ValueError("component vertex sets differ")
    if discovery_core["component_sizes"] != independent_result["reconstruction"]["component_orders"]:
        raise ValueError("component orders differ")
    if (
        discovery_core["component_fibre_balances"]
        != independent_result["reconstruction"]["component_fibre_balances"]
    ):
        raise ValueError("component fibre balances differ")

    q = independent_result["gram"]["matrix"]
    full_distribution = Counter(value for row in q for value in row)
    expected_full_distribution = {str(k): full_distribution[k] for k in sorted(full_distribution)}
    if discovery_core["forced_gram_entry_distribution"] != expected_full_distribution:
        raise ValueError("full Gram distributions differ")
    if discovery_core["forced_gram_diagonal"] != independent_result["gram"]["diagonal_set"][0]:
        raise ValueError("Gram diagonal differs")
    if discovery_core["forced_gram_row_sum"] != independent_result["gram"]["row_sum_set"][0]:
        raise ValueError("Gram row sum differs")

    reduction = discovery["exhaustive_B_reduction"]
    verifier_inventory = independent_result["pair_inventory"]
    if reduction["nonmatching_pairs_per_fibre"] != verifier_inventory[
        "allowed_pair_count_per_fibre"
    ]:
        raise ValueError("nonmatching-pair counts differ")
    if (
        reduction["pair_small_component_count_distribution_per_fibre"]
        != verifier_inventory["component_count_per_pair"]
    ):
        raise ValueError("component pair inventories differ")

    discovery_patterns = {
        key.strip("()").replace(" ", ""): value
        for key, value in reduction["required_60_block_component_patterns"].items()
    }
    if discovery_patterns != verifier_inventory["forced_column_component_patterns"]:
        raise ValueError("forced component pattern multiplicities differ")

    census = reduction["candidate_census"]
    discovery_counts = [
        census["raw_pair_triples"],
        census["gram_support_legal"],
        census["after_forced_component_equality"],
        census["after_mixed_BH_nonnegativity"],
    ]
    if discovery_counts != independent_result["six_set_census"]["counts"]:
        raise ValueError("six-set census differs")

    discovery_h = discovery["forced_H_boundary_if_B_exists"]
    independent_h = independent_result["conditional_outside_counts"]
    overlap_counts = [
        discovery_h["block_overlap_pair_counts_0_1_2"][str(i)] for i in range(3)
    ]
    edge_counts = [
        discovery_h["H_edges_by_block_overlap"][str(i)] for i in range(3)
    ]
    if overlap_counts != independent_h["column_pair_overlap_0_1_2"]:
        raise ValueError("outside-column overlap census differs")
    if edge_counts != independent_h["H_edges_by_column_overlap_0_1_2"]:
        raise ValueError("outside H edge-overlap census differs")
    if discovery_h["H_triangles"] != independent_h["H_triangle_count"]:
        raise ValueError("conditional H triangle count differs")
    if discovery_h["H_four_cycles"] != independent_h["H_four_cycle_count"]:
        raise ValueError("conditional H four-cycle count differs")

    data = independent.load_frozen_input()
    core = independent.reconstruct_core(data)
    c4 = core_four_cycles(core["adjacency"])
    if c4 != discovery_core["four_cycle_count"] or c4 != 10:
        raise ValueError("core four-cycle census differs")

    status = discovery["status_wall"]
    if status["canonical_full_B"] != "UNKNOWN":
        raise ValueError("discovery inflates full-B status")
    if status["compatible_8_regular_H"] != "UNKNOWN":
        raise ValueError("discovery inflates H status")
    if status["endpoint_excluded"] or status["conway_99_resolved"]:
        raise ValueError("discovery inflates global status")

    two_fibre = validate_discovery_two_fibre(discovery)
    return {
        "format": "wave42-joint-incidence-comparison-v1",
        "claim_label": "VERIFIED_SCOPED_CONDITIONAL_REDUCTION",
        "precomparison_independent_result_sha256": INDEPENDENT_SHA256,
        "discovery_result_sha256": DISCOVERY_SHA256,
        "exact_matches": {
            "input_and_mask": True,
            "component_vertices_orders_and_fibre_balances": True,
            "gram_distribution_diagonal_and_row_sum": True,
            "pair_inventory_and_component_patterns": True,
            "six_set_filter_counts": discovery_counts,
            "outside_column_overlaps": overlap_counts,
            "H_edges_by_overlap": edge_counts,
            "H_triangles": discovery_h["H_triangles"],
            "H_four_cycles": discovery_h["H_four_cycles"],
            "core_four_cycles": c4,
        },
        "two_fibre_positive_controls": two_fibre,
        "method_comparison": {
            "discovery_final_filter": "nonnegativity of the mixed BH target",
            "independent_final_filter": (
                "equivalent pointwise lambda/mu common-neighbour bounds, "
                "implemented without discovery imports"
            ),
        },
        "status_wall": independent_result["status_wall"],
    }


def build_comparison() -> dict:
    independent_result = load_json_at_hash(INDEPENDENT, INDEPENDENT_SHA256)
    discovery = load_json_at_hash(DISCOVERY, DISCOVERY_SHA256)
    return compare_payloads(independent_result, discovery)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    comparison = build_comparison()
    if args.output:
        args.output.write_text(
            json.dumps(comparison, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify or not args.output:
        print(json.dumps({
            "claim_label": comparison["claim_label"],
            "six_set_filter_counts": comparison["exact_matches"]["six_set_filter_counts"],
            "distinct_positive_controls": comparison["two_fibre_positive_controls"][
                "independent_certificate_is_distinct"
            ],
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

