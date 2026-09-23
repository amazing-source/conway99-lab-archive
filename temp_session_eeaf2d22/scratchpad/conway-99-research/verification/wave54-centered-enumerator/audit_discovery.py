#!/usr/bin/env python3
"""Byte and value audit of the Wave54 discovery package.

This script consumes the already-produced independent result.  It never calls
or imports the discovery checker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INDEPENDENT = ROOT / "verification/wave54-centered-enumerator/independent-results.json"
DISCOVERY = ROOT / "attempts/wave54-centered-enumerator/exact-results.json"
INPUT_MANIFEST = ROOT / "attempts/wave54-centered-enumerator/input-freeze.sha256"
PACKAGE_MANIFEST = (
    ROOT / "attempts/wave54-centered-enumerator/package-manifest.sha256"
)

EXPECTED = {
    "discovery_exact_results_sha256": (
        "d7f8da8862c74da08e5d122e028f95125051d4e3032287f8e2e7f5490ded3cd8"
    ),
    "discovery_input_manifest_sha256": (
        "6d3983f7e67211eff34b08960cd11ef1d0d07514fc23a1dfea2e47f666d61932"
    ),
    "discovery_package_manifest_sha256": (
        "4e6fa530dee3c30be6423d9b08f87e6389a59f20d972a5df999ca97541a2db23"
    ),
    "discovery_agent_report_sha256": (
        "531bed27e505a9db18b97ab6062ce1e002a0cf3bc488b01086b89be1ad566e76"
    ),
}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        pieces = line.split(None, 1)
        if len(pieces) != 2 or len(pieces[0]) != 64:
            raise ValueError(f"malformed manifest line {path}:{line_number}")
        entries.append((pieces[0].lower(), pieces[1]))
    return entries


def validate_manifest(path: Path) -> dict[str, object]:
    entries = []
    for expected, relative in parse_manifest(path):
        target = ROOT / relative
        actual = sha256_path(target)
        entries.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "pass": actual == expected,
            }
        )
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256_path(path),
        "entry_count": len(entries),
        "entries": entries,
        "all_entries_pass": all(entry["pass"] for entry in entries),
    }


def compare_payloads(independent: dict, discovery: dict) -> dict[str, object]:
    independent_a = independent["candidate_A"]
    discovery_a = [
        discovery["primal_enumerator_nonzero"].get(str(i), 0)
        for i in range(232)
    ]
    independent_b = independent["macwilliams"]["B"]
    discovery_b = [
        discovery["dual_enumerator_nonzero"].get(str(i), 0)
        for i in range(232)
    ]
    return {
        "all_232_A_coefficients_equal": independent_a == discovery_a,
        "all_232_B_coefficients_equal": independent_b == discovery_b,
        "independent_B_count": len(independent_b),
        "discovery_nonzero_B_count": sum(value != 0 for value in discovery_b),
        "zero_B_indices": [
            i for i, value in enumerate(independent_b) if value == 0
        ],
        "selected_B": {
            str(i): independent_b[i]
            for i in (0, 1, 2, 7, 12, 13, 14, 198, 231)
        },
        "dual_sum": sum(independent_b),
        "expected_dual_sum_3^220": 3**220,
    }


def build_audit() -> dict[str, object]:
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    comparison = compare_payloads(independent, discovery)
    input_manifest = validate_manifest(INPUT_MANIFEST)
    package_manifest = validate_manifest(PACKAGE_MANIFEST)
    hashes = {
        "discovery_exact_results_sha256": sha256_path(DISCOVERY),
        "discovery_input_manifest_sha256": sha256_path(INPUT_MANIFEST),
        "discovery_package_manifest_sha256": sha256_path(PACKAGE_MANIFEST),
        "discovery_agent_report_sha256": sha256_path(
            ROOT / "agents/2026-07-27-wave54-centered-enumerator.md"
        ),
    }
    hash_checks = {
        name: hashes[name] == expected for name, expected in EXPECTED.items()
    }
    all_pass = (
        comparison["all_232_A_coefficients_equal"]
        and comparison["all_232_B_coefficients_equal"]
        and comparison["dual_sum"] == comparison["expected_dual_sum_3^220"]
        and input_manifest["all_entries_pass"]
        and package_manifest["all_entries_pass"]
        and all(hash_checks.values())
    )
    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": "Wave54 discovery byte/value comparison only",
        "comparison": comparison,
        "hashes": hashes,
        "expected_hash_checks": hash_checks,
        "input_manifest": input_manifest,
        "package_manifest": package_manifest,
        "all_checks_pass": all_pass,
        "status_boundary": {
            "formal_listed_constraint_feasibility": "VERIFIED",
            "actual_linear_code": "NOT_CONSTRUCTED",
            "complete_weight_enumerator": "NOT_CONSTRUCTED",
            "endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "general_upper_bound_improved": False,
            "novelty": "UNKNOWN",
        },
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    audit = build_audit()
    if not audit["all_checks_pass"]:
        raise SystemExit("discovery audit failed")
    text = canonical_json(audit)
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8", newline="\n")
        print(f"WROTE {args.output}")
        return 0
    if args.verify.read_text(encoding="utf-8") != text:
        print(f"MISMATCH {args.verify}")
        return 1
    print(f"VERIFIED {args.verify}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
