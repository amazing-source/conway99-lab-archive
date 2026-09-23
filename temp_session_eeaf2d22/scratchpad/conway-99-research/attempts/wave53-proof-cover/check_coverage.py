#!/usr/bin/env python3
"""Fail-closed replay of the Wave 53 derived branch-coverage certificate."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ATTEMPT_ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ATTEMPT_ROOT / "build_coverage.py"


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_bytes(),
        object_pairs_hook=strict_object,
        parse_constant=reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("certificate is not a JSON object")
    return value


def builder():
    specification = importlib.util.spec_from_file_location(
        "wave53_coverage_builder", BUILDER_PATH
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load coverage builder")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def check(certificate: dict[str, Any]) -> dict[str, Any]:
    expected = builder().build()
    if certificate != expected:
        raise ValueError("stored coverage certificate differs from exact replay")
    coverage = certificate["coverage"]
    proof = certificate["proof_status"]
    if coverage["branch_cover_exhaustive_under_endpoint_assumptions"] is not True:
        raise ValueError("branch cover is not marked exhaustive")
    if proof["complete_cases_checked_unsat"] != 0:
        raise ValueError("complete-case proof coverage was inflated")
    if proof["complete_case_proof_coverage"] != "0/33":
        raise ValueError("complete-case proof coverage string changed")
    if proof["endpoint_excluded"] is not False or proof["endpoint_status"] != "UNKNOWN":
        raise ValueError("endpoint status was inflated")
    if any(case["complete_case_status"] != "UNKNOWN" for case in certificate["case_definitions"]):
        raise ValueError("a complete case was promoted without a certificate")
    return {
        "format": "wave53-endpoint-proof-cover-check-v1",
        "role": "proof_a",
        "claim_label": "DERIVED",
        "scope": "deterministic replay of exact case definitions and coverage accounting",
        "branch_cover_exhaustive_under_endpoint_assumptions": True,
        "complete_case_proof_coverage": "0/33",
        "verified_partial_shards": 1,
        "complete_cases_closed_by_partial_shards": 0,
        "next_open_shard": "branch15 AND x187=0",
        "endpoint_status": "UNKNOWN",
        "limitations": [
            "This checker is in the discovery lane and does not independently verify itself.",
            "Exact branch coverage is not a proof that any branch is UNSAT.",
        ],
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--certificate",
        type=Path,
        default=ATTEMPT_ROOT / "coverage-certificate.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ATTEMPT_ROOT / "coverage-check.json",
    )
    arguments = parser.parse_args()
    result = check(load_json(arguments.certificate))
    arguments.output.write_text(canonical_json(result), encoding="utf-8", newline="\n")
    print(canonical_json(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
