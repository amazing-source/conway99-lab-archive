#!/usr/bin/env python3
"""Post-freeze comparison against Wave 41 discovery and primary verifier."""

from __future__ import annotations

import argparse
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
    "verification/wave41-evenpart-equality/discovery-comparison.json":
        "6ece1335fa595e4feed57b45cf63e6229697d0f410b2ebae1c32cde9e1cdcc1c",
    "verification/wave41-multiedge-rank-packing/independent-results.json":
        "20cfac8928e1a9d52a586a833d8e52cc7f64f7998bdd641467ded5121e2da133",
}
LABELS = {
    "2+1+1+1+1": "1+1+1+1+2",
    "2+2+1+1": "1+1+2+2",
    "2+2+2": "2+2+2",
    "3+2+1": "1+2+3",
    "4+1+1": "1+1+4",
    "4+2": "2+4",
    "6": "6",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute() -> dict[str, object]:
    actual_hashes = {name: sha256(ROOT / name) for name in EXPECTED_HASHES}
    if actual_hashes != EXPECTED_HASHES:
        raise ValueError("post-freeze comparison input hash mismatch")
    secondary = json.loads(
        (HERE / "secondary-results.json").read_text(encoding="utf-8")
    )
    discovery = json.loads(
        (ROOT / "attempts/wave41-evenpart-equality/exact-results.json")
        .read_text(encoding="utf-8")
    )
    primary = json.loads(
        (ROOT / "verification/wave41-evenpart-equality/independent-results.json")
        .read_text(encoding="utf-8")
    )
    primary_comparison = json.loads(
        (ROOT / "verification/wave41-evenpart-equality/discovery-comparison.json")
        .read_text(encoding="utf-8")
    )
    comparisons = {}
    discrepancies = []
    for secondary_label, discovery_label in LABELS.items():
        ours = secondary["even_partition_audits"][secondary_label]
        theirs = discovery["partition_results"][discovery_label]
        primary_entry = primary["partition_results"][secondary_label]
        values = {
            "minimum_F_permutations": {
                "secondary": ours["minimum_F_permutation_count"],
                "discovery": theirs["minimum_permutation_cover"]
                ["distinct_minimum_permutations"],
                "primary": primary_entry["minimum_projection_permutation_count"],
            },
            "canonical_right_kernels": {
                "secondary": ours["distinct_canonical_right_kernels"],
                "discovery": theirs["distinct_right_kernels"],
                "primary": primary_entry["distinct_right_kernels"],
            },
            "canonical_targets": {
                "secondary": ours["unique_raw_canonical_kernel_targets"],
                "discovery": theirs["distinct_equality_constraints"],
                "primary": primary_entry["distinct_kernel_target_pairs"],
            },
            "rank_25_survivors": {
                "secondary": ours["total_rank_25_R_hits"],
                "discovery": theirs["realized_equality_constraint_count"],
                "primary": primary_entry["rank_25_compatible_cases"],
            },
        }
        agrees = all(
            len(set(field.values())) == 1
            for field in values.values()
        )
        if not agrees:
            discrepancies.append(
                {"partition": secondary_label, "values": values}
            )
        comparisons[secondary_label] = {
            "discovery_label": discovery_label,
            "agrees": agrees,
            **values,
        }
    secondary_totals = secondary["exhaustive_totals"]
    primary_totals = primary["totals"]
    aggregate = {
        "minimum_F_permutations": {
            "secondary": secondary_totals["minimum_F_permutations"],
            "primary": primary_totals["minimum_projection_permutations"],
        },
        "canonical_right_kernels": {
            "secondary": secondary_totals["distinct_canonical_right_kernels"],
            "primary": primary_totals["distinct_right_kernels"],
        },
        "canonical_targets": {
            "secondary": secondary_totals["distinct_canonical_kernel_targets"],
            "primary": primary_totals["distinct_kernel_target_pairs"],
        },
        "rank_25_survivors": {
            "secondary": secondary_totals["rank_25_R_hits"],
            "primary": primary_totals["rank_25_compatible_cases"],
        },
    }
    if any(len(set(field.values())) != 1 for field in aggregate.values()):
        discrepancies.append({"aggregate": aggregate})
    result = {
        "format": "wave41-rank26-secondary-comparison-v1",
        "comparison_input_hashes": actual_hashes,
        "discovery_final_sha_verified": (
            actual_hashes[
                "attempts/wave41-evenpart-equality/exact-results.json"
            ]
            == EXPECTED_HASHES[
                "attempts/wave41-evenpart-equality/exact-results.json"
            ]
        ),
        "partition_comparison": comparisons,
        "aggregate_comparison": aggregate,
        "all_odd_comparison": {
            "secondary_types": sorted(
                secondary["all_odd_schur_obstructions"]
            ),
            "primary_composition_types": sorted(
                "+".join(map(str, partition))
                for partition in primary_comparison["composition"]["all_odd_types"]
            ),
            "agrees": sorted(
                secondary["all_odd_schur_obstructions"]
            ) == sorted(
                "+".join(map(str, partition))
                for partition in primary_comparison["composition"]["all_odd_types"]
            ),
            "note": (
                "The secondary verifier independently covered the four "
                "all-odd types inside its own checker. The primary verifier "
                "composed a separate frozen all-odd package."
            ),
        },
        "method_difference": (
            "Discovery and primary group 164,928 permutations into 52 "
            "right kernels and perform 540,540 kernel-level matching scans. "
            "The secondary checker independently recovers the same 52 "
            "kernels and 164,278 targets; for rank-one F it partitions the "
            "10,395 R universe into 11 pivot-mate branches of 945 and forces "
            "W entrywise, while for ranks two and three it vector-scans all "
            "10,395 R for every minimum-F permutation."
        ),
        "primary_positive_control_note": (
            "A transient primary-verifier positive-control lift bug reported "
            "during development is not present in the frozen primary result "
            "compared here and did not affect any legal-matching absence "
            "count or the rank-26 theorem."
        ),
        "discrepancies": discrepancies,
        "verdict": "AGREES" if not discrepancies else "DISCREPANCY",
    }
    validate(result)
    return result


def validate(result: dict[str, object]) -> None:
    if not result["discovery_final_sha_verified"]:
        raise ValueError("specified discovery SHA was not verified")
    if result["discrepancies"]:
        raise ValueError("comparison contains discrepancies")
    if result["verdict"] != "AGREES":
        raise ValueError("comparison did not agree")
    if not result["all_odd_comparison"]["agrees"]:
        raise ValueError("all-odd type composition mismatch")
    for label, entry in result["partition_comparison"].items():
        if not entry["agrees"]:
            raise ValueError(f"partition comparison failed for {label}")
        for field in (
            "minimum_F_permutations",
            "canonical_right_kernels",
            "canonical_targets",
            "rank_25_survivors",
        ):
            if len(set(entry[field].values())) != 1:
                raise ValueError(f"{field} mismatch for {label}")
    for field in result["aggregate_comparison"].values():
        if len(set(field.values())) != 1:
            raise ValueError("aggregate comparison mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write and args.verify:
        raise SystemExit("--write and --verify are mutually exclusive")
    fresh = compute()
    if args.write:
        args.write.write_text(
            json.dumps(fresh, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE: {args.write}")
    elif args.verify:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        validate(stored)
        if stored != fresh:
            raise SystemExit("stored comparison differs from replay")
        print(f"VERIFIED: {args.verify}")
    else:
        print(json.dumps(fresh, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
