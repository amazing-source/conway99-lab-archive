#!/usr/bin/env python3
"""Post-freeze comparison and eleven-type universal composition."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXPECTED_HASHES = {
    "attempts/wave41-evenpart-equality/exact-results.json":
        "8a9e58aaa1073ae4a87e183f904ce7f43eaa620bbac5a6f5d1f8445dd795dc85",
    "verification/wave41-evenpart-equality/independent-results.json":
        "ec371dad71c794d57d4e27b21d17b08fac1d17e22167749ef797d950c18299e4",
    "verification/wave41-evenpart-equality/independent_check.py":
        "d27d70af72df6f7824a0c32f15fb1f70ba32036564c903e36a991b1d88b0cf81",
    "verification/wave41-evenpart-equality/test_independent_check.py":
        "dd0670b3d0b987f67a1b21d2cc4fb7365e1efb0f61a286d0b1f33e11827df659",
    "verification/wave41-multiedge-rank-packing/independent-results.json":
        "20cfac8928e1a9d52a586a833d8e52cc7f64f7998bdd641467ded5121e2da133",
    "verification/wave41-multiedge-rank-packing/package-manifest.sha256":
        "83572b7721755066906165da79680934d258510007c9a3de19b1206a0527c913",
}
TYPE_MAP = {
    "2+1+1+1+1": "1+1+1+1+2",
    "2+2+1+1": "1+1+2+2",
    "4+1+1": "1+1+4",
    "3+2+1": "1+2+3",
    "2+2+2": "2+2+2",
    "4+2": "2+4",
    "6": "6",
}
ODD_TYPES = {"1^6", "1^3+3", "1+5", "3+3"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def strict_load(path: Path) -> object:
    def reject(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject)


def verify_hashes() -> dict[str, str]:
    actual = {path: digest(ROOT / path) for path in EXPECTED_HASHES}
    if actual != EXPECTED_HASHES:
        raise ValueError(
            "post-freeze input hash mismatch: "
            + repr(
                {
                    path: {
                        "expected": EXPECTED_HASHES[path],
                        "actual": actual[path],
                    }
                    for path in EXPECTED_HASHES
                    if actual[path] != EXPECTED_HASHES[path]
                }
            )
        )
    return actual


def positive_partitions(total: int, maximum: int | None = None):
    if total == 0:
        yield ()
        return
    if maximum is None or maximum > total:
        maximum = total
    for first in range(maximum, 0, -1):
        for tail in positive_partitions(total - first, first):
            yield (first,) + tail


def odd_label_to_partition(label: str) -> tuple[int, ...]:
    return {
        "1^6": (1, 1, 1, 1, 1, 1),
        "1^3+3": (3, 1, 1, 1),
        "1+5": (5, 1),
        "3+3": (3, 3),
    }[label]


def build_comparison() -> dict[str, object]:
    hashes = verify_hashes()
    independent = strict_load(
        HERE / "independent-results.json"
    )
    discovery = strict_load(
        ROOT / "attempts/wave41-evenpart-equality/exact-results.json"
    )
    odd = strict_load(
        ROOT
        / "verification/wave41-multiedge-rank-packing/independent-results.json"
    )
    if independent["claim_label"] != "VERIFIED_SCOPED":
        raise ValueError("even verifier is not scoped-verified")
    if discovery["claim_label"] != "CANDIDATE":
        raise ValueError("discovery status changed")
    if odd["claim_label"] != "VERIFIED_SCOPED":
        raise ValueError("all-odd verifier is not scoped-verified")

    comparisons = {}
    for independent_label, discovery_label in TYPE_MAP.items():
        left = independent["partition_results"][independent_label]
        right = discovery["partition_results"][discovery_label]
        invariants = {
            "partition": (
                sorted(left["partition"])
                == right["partition"]
            ),
            "even_part_count": (
                left["even_part_count"] == right["even_part_count"]
            ),
            "minimum_projection_permutations": (
                left["minimum_projection_permutation_count"]
                == right["minimum_permutation_cover"][
                    "distinct_minimum_permutations"
                ]
            ),
            "distinct_right_kernels": (
                left["distinct_right_kernels"]
                == right["distinct_right_kernels"]
            ),
            "distinct_equality_targets": (
                left["distinct_kernel_target_pairs"]
                == right["distinct_equality_constraints"]
            ),
            "matching_evaluations": (
                left["kernel_target_matching_checks"]
                == right["tested_R_projection_evaluations"]
            ),
            "no_rank25_survivor": (
                left["rank_25_compatible_cases"] == 0
                and right["realized_equality_constraint_count"] == 0
                and right["rank25_exists"] is False
            ),
        }
        if not all(invariants.values()):
            raise ValueError(
                f"discovery disagreement for {independent_label}: {invariants}"
            )
        comparisons[independent_label] = {
            "discovery_label": discovery_label,
            "invariants": invariants,
            "minimum_projection_permutations": left[
                "minimum_projection_permutation_count"
            ],
            "distinct_right_kernels": left["distinct_right_kernels"],
            "distinct_equality_targets": left[
                "distinct_kernel_target_pairs"
            ],
            "matching_evaluations": left[
                "kernel_target_matching_checks"
            ],
            "rank25_survivors": 0,
        }

    if set(odd["type_results"]) != ODD_TYPES:
        raise ValueError("all-odd package does not cover exactly four types")
    for label, item in odd["type_results"].items():
        if item["scoped_rank_F7_K39_lower_bound"] != 26:
            raise ValueError(f"all-odd lower bound changed for {label}")
        if item["rank_25_schur_obstruction"][
            "candidate_targets_decoding_as_legal_Z_matchings"
        ] != 0:
            raise ValueError(f"all-odd rank-25 target survived for {label}")
    if odd["rank_transport"]["conclusion"] != (
        "rank_F7(N M N^T)=rank_F7(M)"
    ):
        raise ValueError("rank transport is missing")

    even_partitions = {
        tuple(sorted(item["partition"], reverse=True))
        for item in independent["partition_results"].values()
    }
    odd_partitions = {odd_label_to_partition(label) for label in ODD_TYPES}
    all_partitions = set(positive_partitions(6))
    if even_partitions & odd_partitions:
        raise ValueError("odd/even type overlap")
    if even_partitions | odd_partitions != all_partitions:
        raise ValueError("eleven-type cover is incomplete")

    return {
        "format": "wave41-rank26-composition-v1",
        "claim_label": "VERIFIED",
        "post_freeze_inputs": hashes,
        "discovery_comparison": {
            "status": "AGREES",
            "types": comparisons,
            "aggregate": {
                "minimum_projection_permutations": independent["totals"][
                    "minimum_projection_permutations"
                ],
                "distinct_right_kernels": independent["totals"][
                    "distinct_right_kernels"
                ],
                "distinct_equality_targets": independent["totals"][
                    "distinct_kernel_target_pairs"
                ],
                "matching_evaluations": independent["totals"][
                    "kernel_target_matching_checks"
                ],
                "rank25_survivors": 0,
            },
        },
        "composition": {
            "all_positive_partitions_of_six": [
                list(parts) for parts in sorted(all_partitions, reverse=True)
            ],
            "even_part_types": [
                list(parts) for parts in sorted(even_partitions, reverse=True)
            ],
            "all_odd_types": [
                list(parts) for parts in sorted(odd_partitions, reverse=True)
            ],
            "type_count": 11,
            "coverage_complete": True,
            "every_type_has_rank_F7_K39_at_least": 26,
            "rank_transport": "rank_F7(N M N^T)=rank_F7(M)",
            "universal_conclusion": (
                "Every hypothetical srg(99,14,1,2) satisfies "
                "rank_F7(M)>=26."
            ),
            "universal_rank_F7_M_lower_bound": 26,
        },
        "discrepancies": [],
        "status_wall": {
            "universal_rank_F7_M_at_least_26": "VERIFIED",
            "endpoint_n3_4158": "UNKNOWN",
            "general_upper_bound_below_4158": "NOT_PROVED",
            "best_general_n3_upper_bound": 4158,
            "conway_99": "UNKNOWN",
            "graph_construction": "NONE",
            "novelty": "UNKNOWN",
            "priority": "UNKNOWN",
        },
    }


def validate_comparison(results: object) -> None:
    if not isinstance(results, dict):
        raise ValueError("comparison root must be an object")
    if results.get("format") != "wave41-rank26-composition-v1":
        raise ValueError("wrong comparison format")
    if results.get("claim_label") != "VERIFIED":
        raise ValueError("wrong claim label")
    comparison = results.get("discovery_comparison", {})
    if comparison.get("status") != "AGREES":
        raise ValueError("discovery comparison does not agree")
    if set(comparison.get("types", {})) != set(TYPE_MAP):
        raise ValueError("even-type comparison is incomplete")
    if any(
        not all(record["invariants"].values())
        or record["rank25_survivors"] != 0
        for record in comparison["types"].values()
    ):
        raise ValueError("an even comparison invariant failed")
    composition = results.get("composition", {})
    if (
        composition.get("type_count") != 11
        or composition.get("coverage_complete") is not True
        or composition.get("every_type_has_rank_F7_K39_at_least") != 26
        or composition.get("universal_rank_F7_M_lower_bound") != 26
    ):
        raise ValueError("universal composition is incomplete")
    wall = results.get("status_wall", {})
    if wall.get("universal_rank_F7_M_at_least_26") != "VERIFIED":
        raise ValueError("rank-26 theorem was not promoted")
    if wall.get("conway_99") != "UNKNOWN":
        raise ValueError("Conway status inflated")
    if wall.get("endpoint_n3_4158") != "UNKNOWN":
        raise ValueError("endpoint status inflated")
    if wall.get("general_upper_bound_below_4158") != "NOT_PROVED":
        raise ValueError("upper-bound status inflated")
    for key in ("novelty", "priority"):
        if wall.get(key) != "UNKNOWN":
            raise ValueError(f"{key} status inflated")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    actual = build_comparison()
    validate_comparison(actual)
    if args.verify:
        expected = strict_load(args.verify)
        validate_comparison(expected)
        if actual != expected:
            raise SystemExit("comparison verification mismatch")
        print(f"VERIFIED {args.verify}")
    else:
        payload = json.dumps(actual, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(payload, encoding="utf-8", newline="\n")
            print(args.output)
        else:
            print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
