#!/usr/bin/env python3
"""Compare frozen Wave 51 discovery bytes with the independent reconstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave51-seidel-smith" / "exact-results.json"
INDEPENDENT = HERE / "independent-result.json"
OUTPUT = HERE / "comparison.json"

EXPECTED_DISCOVERY_SHA256 = (
    "10ae5fe8d05776f008fe31ce4b614044680f7cebf9efe482b1aa299f2c5caff6"
)
EXPECTED_INDEPENDENT_SHA256 = (
    "1dda847b1180ac881f2ccce80285a2a50d9cab1f0f910f7dbdf9a6087d53d793"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen(path: Path, expected_hash: str) -> dict[str, object]:
    actual = sha256(path)
    if actual != expected_hash:
        raise RuntimeError(f"hash mismatch for {path}: {actual}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_comparison() -> dict[str, object]:
    discovery = load_frozen(DISCOVERY, EXPECTED_DISCOVERY_SHA256)
    independent = load_frozen(INDEPENDENT, EXPECTED_INDEPENDENT_SHA256)
    discovery_profiles = discovery["smith_normal_form"]["profiles"]
    independent_profiles = independent["smith_logic"]["profiles"]
    profile_agreement = []
    for left, right in zip(discovery_profiles, independent_profiles):
        profile_agreement.append(
            left["rank"] == right["rank_f7"]
            and left["factor_count"] == right["factor_count"]
            and left["divisibility_chain"] == right["divisibility_chain"]
            and left["determinant_matches"]
            and right["absolute_product"]
            == discovery["fixed_identities"]["absolute_determinant"]
            and left["rank_mod_2"] == right["rank_mod_2"]
            and left["rank_mod_5"] == right["rank_mod_5"]
            and left["rank_mod_7"] == right["rank_mod_7"]
        )
    discovery_spectrum = discovery["fixed_identities"]["seidel_spectrum"]
    corrected_spectrum = independent["rational_spectra"]["seidel"]
    checks = {
        "all_49_smith_profiles_agree": len(profile_agreement) == 49
        and all(profile_agreement),
        "absolute_determinant_agrees": (
            discovery["fixed_identities"]["absolute_determinant"]
            == independent["rational_spectra"]["absolute_determinant"]
        ),
        "jordan_formula_agrees": (
            discovery["modular_jordan_form"]["formula"]
            == "J2(0)^r direct_sum J1(0)^(99-2r)"
            == independent["mod_7_jordan"]["formula"]
        ),
        "symmetric_square_rank_agrees": (
            discovery["symmetric_square"]["gram_rank_mod_7"]
            == independent["symmetric_square"]["gram_rank_mod_7"]
            == 98
        ),
        "symmetric_square_floor_agrees": (
            discovery["symmetric_square"]["derived_floor"]
            == independent["symmetric_square"]["derived_floor"]
            == 14
        ),
        "endpoint_survivors_agree": (
            discovery["endpoint"]["surviving_integer_ranks"]
            == independent["endpoint"]["surviving_ranks"]
            == list(range(28, 45))
        ),
        "discovery_spectrum_is_incorrect": (
            discovery_spectrum == {"-70": 1, "-7": 54, "7": 44}
            and corrected_spectrum == {"-70": 1, "-7": 44, "7": 54}
        ),
    }
    return {
        "claim_label": "VERIFIED",
        "scope": "comparison of frozen discovery and independent exact artifacts",
        "input_hashes": {
            str(DISCOVERY.relative_to(ROOT)).replace("\\", "/"): sha256(DISCOVERY),
            str(INDEPENDENT.relative_to(ROOT)).replace("\\", "/"): sha256(INDEPENDENT),
        },
        "checks": checks,
        "all_corrected_structural_claims_agree": all(checks.values()),
        "correction": {
            "claim_label": "REFUTED",
            "field": "fixed_identities.seidel_spectrum",
            "discovery_value": discovery_spectrum,
            "correct_value": corrected_spectrum,
            "impact": (
                "the false signed multiplicities do not change the absolute "
                "determinant or any checked Smith/Jordan/rank conclusion"
            ),
        },
        "endpoint": {
            "claim_label": "UNKNOWN",
            "contradiction_found": False,
        },
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    encoded = canonical_bytes(build_comparison())
    if args.verify:
        if args.output.read_bytes() != encoded:
            raise SystemExit("comparison artifact differs from recomputation")
        print(f"verified {args.output}")
        return 0
    args.output.write_bytes(encoded)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

