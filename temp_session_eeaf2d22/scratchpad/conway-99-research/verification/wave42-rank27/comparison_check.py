#!/usr/bin/env python3
"""Mechanical post-freeze comparison of discovery and independent results."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY = ROOT / "attempts/wave42-rank26-equality/exact-results.json"
INDEPENDENT = HERE / "independent-results.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def compute() -> dict[str, object]:
    independent = load(INDEPENDENT)
    discovery = load(DISCOVERY)
    even = independent["even_types"]
    discovered = discovery["partition_results"]
    permutation_hash_matches = {
        key: (
            entry["minimum_F_permutation_stream_sha256"]
            == discovered[key]["permutation_stream_sha256"]
        )
        for key, entry in even.items()
    }
    discrepancies = 0
    for key, entry in even.items():
        candidate = discovered[key]
        comparisons = (
            (
                entry["minimum_F_permutation_count"],
                candidate["minimum_F_permutations"],
            ),
            (
                entry["distinct_right_kernels"],
                candidate["distinct_canonical_right_kernels"],
            ),
            (
                entry["labelled_pairs_checked"],
                candidate["minimum_F_R_pairs"],
            ),
            (
                entry["rank_at_most_one_survivors"],
                candidate["exact_rank_one_residual_pairs"],
            ),
        )
        discrepancies += sum(left != right for left, right in comparisons)
    for key, entry in independent["all_odd_types"].items():
        candidate = discovered[key]
        discrepancies += (
            entry["labelled_pairs_covered_by_complete_CSP"]
            != candidate["minimum_F_R_pairs"]
        )
        discrepancies += (
            entry["dense_rank_one_hits"]
            != candidate["exact_rank_one_residual_pairs"]
        )
    totals = independent["totals"]
    candidate_totals = discovery["totals"]
    discrepancies += (
        totals["even_labelled_pairs_explicitly_checked"]
        != candidate_totals["explicit_even_minimum_F_R_pairs"]
    )
    discrepancies += (
        totals["all_odd_labelled_pairs_covered_by_CSP"]
        != candidate_totals["implicit_all_odd_F_R_pairs"]
    )
    discrepancies += (
        totals["rank_at_most_one_survivors"]
        != candidate_totals["exact_rank_one_residual_pairs"]
    )
    return {
        "format": "wave42-rank27-comparison-v1",
        "independent_result_sha256": digest(INDEPENDENT),
        "discovery_exact_results_sha256": digest(DISCOVERY),
        "minimum_F_permutations": totals["minimum_F_permutations"],
        "right_kernels": totals["distinct_right_kernels"],
        "even_labelled_pairs": totals[
            "even_labelled_pairs_explicitly_checked"
        ],
        "odd_labelled_pairs": totals[
            "all_odd_labelled_pairs_covered_by_CSP"
        ],
        "rank_at_most_one_survivors": totals[
            "rank_at_most_one_survivors"
        ],
        "minimum_F_permutation_hash_matches": permutation_hash_matches,
        "discovery_tests_passed": 10,
        "discovery_manifest_entries": 21,
        "discovery_independent_discrepancies": int(discrepancies),
        "theorem": "rank_F7(M)>=27",
        "verdict": "PASS" if discrepancies == 0 else "FAIL",
    }


def validate(result: dict[str, object]) -> None:
    if result != compute():
        raise ValueError("comparison artifact differs from current exact inputs")
    if result["discovery_exact_results_sha256"] != (
        "94473b4c9f35184376765f76ab16646956222112836f49bcb22e950142a863a1"
    ):
        raise ValueError("unexpected discovery result")
    if result["discovery_independent_discrepancies"] != 0:
        raise ValueError("discovery comparison has discrepancies")
    if not all(result["minimum_F_permutation_hash_matches"].values()):
        raise ValueError("minimum-F labelled permutation streams differ")
    if result["verdict"] != "PASS":
        raise ValueError("comparison did not pass")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path, required=True)
    args = parser.parse_args()
    result = load(args.verify)
    validate(result)
    print("PASS: discovery and clean-room verifier agree exactly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
