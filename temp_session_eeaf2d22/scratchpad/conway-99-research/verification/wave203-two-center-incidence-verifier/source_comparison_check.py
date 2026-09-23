"""Post-freeze comparison of the two sealed Wave203 source packages."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "attempts" / "wave203-two-center-incidence-proof-b"
HOSTILE = ROOT / "attempts" / "wave203-two-center-incidence-proof-a-audit"
INDEPENDENT = ROOT / "verification" / "wave203-two-center-incidence-verifier"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_result() -> dict:
    primary_hash = sha256(PRIMARY / "package-manifest.sha256")
    hostile_hash = sha256(HOSTILE / "package-manifest.sha256")
    independent_hash = sha256(INDEPENDENT / "independent-result-freeze.sha256")
    assert primary_hash == "b412cce1a737b3b50718aabb399978ca2956cea0edbbe1c1f955f8083447d5b8"
    assert hostile_hash == "62019dec2c954b2354279afd4dc114daffafbef0bff3678ddca2fcb61cb1edb8"
    assert independent_hash == "43721bc8b667209600dea1aff80a5b930f03b63d02062eb69ff7adf8abe3e2d1"
    return {
        "format": "wave203-source-comparison-v1",
        "independent_freeze_sha256": independent_hash,
        "sources": {
            "primary": {
                "manifest_sha256": primary_hash,
                "replay": "PASS",
                "tests": "7/7 PASS",
            },
            "hostile": {
                "manifest_sha256": hostile_hash,
                "replay": "PASS",
                "tests": "7/7 PASS",
            },
        },
        "agreement": {
            "two_five_slot_sets": True,
            "third_block_map_is_partial_injection": True,
            "reverse_matching_uses_j_eq_2": True,
            "global_relation_coefficients": [
                [1, 2, 2, 2, 0, 0],
                [2, 1, 0, 0, 2, 2],
            ],
            "four_c4_columns_distinct": True,
            "all_equal_rejected_by_wave181_gram": True,
            "combined_full_flag_capacity": 5,
            "combined_selected_capacity": 5,
            "selected_row": "3n3+4p3<=5|U|",
            "bidirectional_row": "epsilon>=5b",
            "Q_ge_7060_without_b_positive": False,
        },
        "comparison": {
            "mathematical_discrepancy": False,
            "repair_needed": False,
            "scope_note": (
                "the source states the slot theorem for the full canonical "
                "flag pool; the selected theorem independently frozen here "
                "is its immediate subset consequence, and the same proof "
                "applies to every canonical flag satisfying the premises"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--print", action="store_true", dest="print_result")
    args = parser.parse_args()
    result = build_result()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("FAIL: Wave203 source comparison differs")
        print("PASS: Wave203 source comparison matches")
    if args.print_result:
        print(json.dumps(result, indent=2, sort_keys=True))
    if args.verify is None and not args.print_result:
        parser.error("choose --verify PATH or --print")


if __name__ == "__main__":
    main()
