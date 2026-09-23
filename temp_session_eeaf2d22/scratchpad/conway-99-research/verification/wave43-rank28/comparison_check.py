#!/usr/bin/env python3
"""Mechanical comparison of independent and Wave 43 discovery results."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INDEPENDENT = HERE / "independent-results.json"
EVEN_DISCOVERY = ROOT / "attempts/wave43-rank28-motif/exact-results.json"
TYPE33_DISCOVERY = ROOT / "attempts/wave43-type33-rank2/exact-results.json"
EXPECTED_HASHES = {
    "verification/wave43-rank28/independent-results.json":
        "4e6bc6a04fb65b6dd2a873c9b446d305d65aaca46fecf8703da2886aa1859025",
    "attempts/wave43-rank28-motif/exact-results.json":
        "8878b40898ba9577ef01fb51ab5631632fb0e6bca3394c594b9c399d51385230",
    "attempts/wave43-type33-rank2/exact-results.json":
        "f9f023a7f5da0b51df1f825c83a2405de16a6e4d5245965332df4ace46e8bd8d",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def manifest_check(path: Path) -> dict[str, object]:
    checked = 0
    failures = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        expected, relative = raw.split(maxsplit=1)
        relative = relative.strip().lstrip("*")
        target = ROOT / relative
        actual = sha256(target) if target.is_file() else "MISSING"
        checked += 1
        if actual != expected:
            failures.append(
                {
                    "path": relative,
                    "expected": expected,
                    "actual": actual,
                }
            )
    return {"entries_checked": checked, "failures": failures}


def compute() -> dict[str, object]:
    actual_hashes = {
        relative: sha256(ROOT / relative)
        for relative in EXPECTED_HASHES
    }
    require(actual_hashes == EXPECTED_HASHES, "input result hash drift")
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    even = json.loads(EVEN_DISCOVERY.read_text(encoding="utf-8"))
    type33 = json.loads(TYPE33_DISCOVERY.read_text(encoding="utf-8"))

    checks: list[dict[str, object]] = []

    def compare(name: str, left: object, right: object) -> None:
        checks.append(
            {
                "field": name,
                "discovery": left,
                "independent": right,
                "match": left == right,
            }
        )

    for key in ("2+2+2", "4+2"):
        discovery_cover = even["low_F_derangement_covers"][key]
        independent_cover = independent["even_types"][key]["bounded_rank"]
        compare(
            f"{key}.bounded_count",
            discovery_cover["low_F_derangement_permutation_count"],
            independent_cover["count"],
        )
        compare(
            f"{key}.rank_histogram",
            discovery_cover["low_F_derangement_rank_histogram"],
            independent_cover["rank_histogram"],
        )
        compare(
            f"{key}.permutation_stream_sha256",
            discovery_cover[
                "low_F_derangement_permutation_stream_sha256"
            ],
            independent_cover["stream_sha256"],
        )
        compare(
            f"{key}.first_20",
            discovery_cover["low_F_derangements_first_20"],
            independent_cover["first_20"],
        )
        discovery_scan = even["higher_F_zero_residual_explicit"][key]
        independent_scan = independent["even_types"][key][
            "zero_residual_scan"
        ]
        compare(
            f"{key}.pairs_tested",
            discovery_scan["tested_derangement_R_pairs"],
            independent_scan["pairs_tested"],
        )
        compare(
            f"{key}.zero_residual_pairs",
            discovery_scan["zero_residual_pairs"],
            independent_scan["zero_residual_pairs"],
        )
        compare(
            f"{key}.solution_stream_sha256",
            discovery_scan["solution_stream_sha256"],
            independent_scan["solution_stream_sha256"],
        )

    discovery_minimum = even["type6_minimum_F_rank2_residual"]
    independent_minimum = independent["even_types"]["6"]["minimum_scan"]
    independent_6_cover = independent["even_types"]["6"]["bounded_rank"]
    for name, discovery_value, independent_value in (
        (
            "6.minimum_derangements",
            discovery_minimum["minimum_F_derangements"],
            independent_minimum["minimum_F_derangements"],
        ),
        (
            "6.minimum_permutation_stream_sha256",
            discovery_minimum["permutation_stream_sha256"],
            independent_6_cover["stream_sha256"],
        ),
        (
            "6.pairing_stream_sha256",
            discovery_minimum["pairing_stream_sha256"],
            independent["perfect_matching_universe"]["stream_sha256"],
        ),
        (
            "6.minimum_pairs_tested",
            discovery_minimum["tested_minimum_F_derangement_R_pairs"],
            independent_minimum["pairs_tested"],
        ),
        (
            "6.rank_at_most_two_pairs",
            discovery_minimum["rank_at_most_two_residual_pairs"],
            independent_minimum["rank_at_most_two_pairs"],
        ),
        (
            "6.rank_exactly_two_pairs",
            discovery_minimum["rank_exactly_two_residual_pairs"],
            independent_minimum["rank_exactly_two_pairs"],
        ),
        (
            "6.candidate_stream_sha256",
            discovery_minimum["candidate_stream_sha256"],
            independent_minimum["candidate_stream_sha256"],
        ),
    ):
        compare(name, discovery_value, independent_value)

    discovery_higher = even["type6_next_F_zero_residual"]
    independent_higher = independent["even_types"]["6"]["higher_F_CSP"]
    for field in (
        "pivot_assignment_branches",
        "pivot_mate_branches",
        "unary_viable_branches",
        "backtrack_nodes",
    ):
        compare(
            f"6.higher.{field}",
            discovery_higher[field],
            independent_higher[field],
        )
    compare(
        "6.higher.complete_leaves",
        discovery_higher["complete_permutations"],
        independent_higher["complete_leaves"],
    )
    compare(
        "6.higher.zero_residual_pairs",
        discovery_higher["residual_zero_pairs"],
        len(independent_higher["solutions"]),
    )

    independent_type33 = independent["type33"]
    for field in (
        "branches_visited",
        "invertible_pivot_branches",
        "nonempty_unary_branches",
        "backtrack_nodes",
        "complete_leaves",
    ):
        compare(
            f"3+3.{field}",
            type33["search"][field],
            independent_type33[field],
        )
    compare("3+3.solution_count", len(type33["solutions"]), 0)

    compare(
        "combined.conditional_endpoint_rank_floor",
        28,
        independent["status_wall"][
            "conditional_endpoint_rank_F7_floor"
        ],
    )
    compare(
        "combined.endpoint_excluded",
        False,
        independent["status_wall"]["endpoint_excluded"],
    )
    compare(
        "combined.Conway_99_not_resolved",
        False,
        independent["status_wall"]["conway_99_resolved"],
    )

    discovery_manifest = manifest_check(
        ROOT / "attempts/wave43-rank28-motif/package-manifest.sha256"
    )
    require(
        discovery_manifest["entries_checked"] == 11,
        "discovery manifest entry count",
    )
    require(
        not discovery_manifest["failures"], "discovery manifest failures"
    )
    discrepancies = [check for check in checks if not check["match"]]
    result = {
        "format": "wave43-rank28-comparison-v1",
        "claim_label": "VERIFIED",
        "inputs": actual_hashes,
        "comparison_count": len(checks),
        "discrepancy_count": len(discrepancies),
        "discrepancies": discrepancies,
        "checks": checks,
        "discovery_even_package_manifest": discovery_manifest,
        "verdict": (
            "PASS_EXACT_AGREEMENT" if not discrepancies else "FAIL"
        ),
        "status_wall": {
            "conditional_endpoint_rank_F7_floor": 28,
            "endpoint_excluded": False,
            "conway_99_resolved": False,
        },
    }
    require(not discrepancies, f"comparison discrepancies: {discrepancies}")
    return result


def validate(result: dict[str, object]) -> None:
    require(result["format"] == "wave43-rank28-comparison-v1", "format")
    require(result["verdict"] == "PASS_EXACT_AGREEMENT", "verdict")
    require(result["comparison_count"] == 36, "comparison count")
    require(result["discrepancy_count"] == 0, "discrepancies")
    require(result["discovery_even_package_manifest"]["entries_checked"] == 11, "manifest")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = compute()
    validate(result)
    payload = canonical_bytes(result)
    if args.verify:
        require(args.verify.read_bytes() == payload, "stored comparison drift")
        print(f"PASS {args.verify}")
        return 0
    if args.output:
        args.output.write_bytes(payload)
        print(
            f"WROTE {args.output} "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
