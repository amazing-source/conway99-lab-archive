#!/usr/bin/env python3
"""Post-freeze comparison of Wave 99 discovery with the clean-room result."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATTEMPT = ROOT / "attempts" / "wave99-transition-pair-moment"
ATTEMPT_MANIFEST = ATTEMPT / "package-manifest.sha256"
INDEPENDENT = HERE / "independent-results.json"
OUTPUT = HERE / "comparison.json"
EXPECTED_ATTEMPT_MANIFEST_HASH = (
    "e3a30e37bbf08dcd60e4fff7df6f8f4e51780987ba3446e96ff136954e94a9e6"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_attempt_manifest() -> dict[str, str]:
    require(
        sha256(ATTEMPT_MANIFEST) == EXPECTED_ATTEMPT_MANIFEST_HASH,
        "Wave99 package manifest hash changed after freeze",
    )
    entries: dict[str, str] = {}
    for line in ATTEMPT_MANIFEST.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split(maxsplit=1)
        relative = relative.strip().lstrip("*")
        require(relative not in entries, f"duplicate manifest path: {relative}")
        path = ROOT / Path(relative)
        require(path.is_file(), f"manifest input missing: {relative}")
        require(sha256(path) == expected, f"manifest hash mismatch: {relative}")
        entries[relative] = expected
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ATTEMPT.iterdir()
        if path.is_file() and path.name != ATTEMPT_MANIFEST.name
    }
    require(actual == set(entries), "attempt manifest is not file-complete")
    return entries


def comparison() -> dict[str, Any]:
    entries = verify_attempt_manifest()
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    discovery = json.loads(
        (ATTEMPT / "exact-results.json").read_text(encoding="utf-8")
    )

    require(
        independent["precomparison_verdict"]["discovery_comparison"]
        == "NOT_YET_PERFORMED",
        "independent result was not sealed as precomparison work",
    )
    require(discovery["claim_label"] == "DERIVED", "discovery self-promoted")

    independent_cap = independent["coincidence_cap"][
        "per_transition_coincidence_cap"
    ]
    discovery_cap = discovery["canonical_local_check"][
        "co_incidence_per_transition_max"
    ]
    require(independent_cap == discovery_cap == 18, "cap comparison failed")

    independent_moments = independent["moment_certificate"]
    discovery_moments = discovery["moments"]
    compared_moments = {
        "first": (
            independent_moments["first_moment_exact"],
            discovery_moments["first_transition_seed_moment"],
        ),
        "unordered_pair_upper": (
            independent_moments["unordered_pair_moment_upper"],
            discovery_moments["pair_transition_seed_moment_upper"],
        ),
        "zero_seed_upper": (
            independent_moments["zero_transition_seed_upper_bound"],
            discovery_moments["valid_seed_upper"],
        ),
    }
    require(
        all(left == right for left, right in compared_moments.values()),
        "moment comparison failed",
    )

    independent_n14 = independent["sign_and_root_conversion"][
        "N14_upper_bound"
    ]
    discovery_n14 = discovery["bounds"]["N14_upper"]
    require(independent_n14 == discovery_n14 == 4950, "N14 comparison failed")

    weighted = 2_387 * Fraction(1_997_236, 341) - 2_387 * 4_950
    require(weighted == 2_165_002, "independent weighted arithmetic failed")
    require(
        discovery["bounds"]["rank28_weighted_shell_inequality"]
        == "407*N16+43*N18>=2165002",
        "weighted discovery conclusion differs",
    )

    scope = discovery["scope"]
    require(scope["requires_prism_free_endpoint"], "P=0 scope missing")
    require(scope["requires_n3"] == 4158, "endpoint n3 scope missing")
    require(
        not scope["rank_28_used_for_n14_bound"],
        "rank 28 was incorrectly mixed into N14",
    )
    require(
        scope["rank_28_used_for_weighted_corollary"],
        "rank 28 was omitted from weighted conclusion",
    )
    require(scope["n14_counts_both_signs"], "N14 sign convention missing")
    status = discovery["status"]
    require(status["Conway_99"] == "UNKNOWN", "global status inflated")
    require(
        status["strict_n3_upper_bound"] == "NOT_PROVED",
        "strict endpoint status inflated",
    )
    require(
        not status["prism_free_rank28_excluded"],
        "rank row incorrectly excluded",
    )

    return {
        "format": "wave99-transition-pair-moment-comparison-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "attempt_manifest_sha256": EXPECTED_ATTEMPT_MANIFEST_HASH,
        "attempt_manifest_entries_verified": len(entries),
        "clean_room_seal": {
            "precomparison_hashes": "precomparison.sha256",
            "independent_result_claim_label": independent["claim_label"],
        },
        "agreement": {
            "per_transition_coincidence_cap": independent_cap,
            "first_moment": compared_moments["first"][0],
            "unordered_pair_moment_upper": compared_moments[
                "unordered_pair_upper"
            ][0],
            "zero_transition_seed_upper": compared_moments[
                "zero_seed_upper"
            ][0],
            "N14_upper": independent_n14,
            "rank28_weighted_lower": int(weighted),
        },
        "scope_audit": {
            "N14_requires_P0_n3_4158": True,
            "N14_requires_rank28": False,
            "weighted_conclusion_requires_P0_and_rank28_q16": True,
            "scope_mixing_found": False,
        },
        "verdict": (
            "VERIFIED SCOPED: under P=0, N14<=4950; under the additional "
            "rank-28/q=16 hypothesis, 407*N16+43*N18>=2165002"
        ),
        "status_boundary": {
            "strict_n3_upper_bound": "NOT_PROVED",
            "prism_free_rank28_excluded": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--verify", action="store_true")
    arguments = parser.parse_args()
    rendered = canonical_json(comparison())
    if arguments.verify:
        require(arguments.output.is_file(), "comparison output missing")
        require(
            arguments.output.read_text(encoding="utf-8") == rendered,
            "comparison output mismatch",
        )
    else:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    print("PASS: Wave99 discovery agrees with independent reconstruction")


if __name__ == "__main__":
    main()
