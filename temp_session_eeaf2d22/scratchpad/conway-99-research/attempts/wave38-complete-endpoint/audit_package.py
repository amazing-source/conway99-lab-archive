#!/usr/bin/env python3
"""Deterministically replay the Wave 38 construction package artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from complete_endpoint import (
    build_cut_pool,
    cut_catalog,
    static_size_inventory,
    validate_cut_catalog,
    validate_cut_pool,
)
from prism_oracle import load_candidate


PACKAGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_input_freeze(path: Path) -> list[dict[str, object]]:
    records = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line:
            continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"invalid freeze row {line_number}") from error
        target = REPOSITORY_ROOT / relative
        actual = sha256_path(target)
        if actual != expected:
            raise ValueError(f"freeze mismatch for {relative}")
        records.append(
            {
                "path": relative,
                "sha256": actual,
            }
        )
    return records


def audit() -> dict[str, object]:
    inventory_path = PACKAGE_ROOT / "static-schema-estimate.json"
    inventory_payload = canonical_payload(static_size_inventory())
    if inventory_path.read_bytes() != inventory_payload:
        raise ValueError("static schema inventory does not replay byte-identically")

    fixture_path = PACKAGE_ROOT / "fixture-residual-prism.json"
    vertex_count, edges = load_candidate(fixture_path)
    expected_catalog = cut_catalog(vertex_count, edges)
    catalog_path = PACKAGE_ROOT / "fixture-residual-prism-cuts.json"
    if catalog_path.read_bytes() != canonical_payload(expected_catalog):
        raise ValueError("fixture cut catalog does not replay byte-identically")
    cuts = validate_cut_catalog(
        expected_catalog,
        candidate_edges=edges,
        require_complete=True,
    )

    catalog_raw = catalog_path.read_bytes()
    expected_pool = build_cut_pool(
        [(hashlib.sha256(catalog_raw).hexdigest(), expected_catalog)]
    )
    pool_path = PACKAGE_ROOT / "fixture-cut-pool.json"
    if pool_path.read_bytes() != canonical_payload(expected_pool):
        raise ValueError("fixture cut pool does not replay byte-identically")
    source_catalogs = [
        (hashlib.sha256(catalog_raw).hexdigest(), expected_catalog)
    ]
    pooled_cuts = validate_cut_pool(
        expected_pool,
        source_catalogs=source_catalogs,
        require_sources=True,
    )
    if cuts != pooled_cuts:
        raise AssertionError("fixture catalog and cut pool disagree")

    frozen_inputs = validate_input_freeze(PACKAGE_ROOT / "input-freeze.sha256")
    return {
        "format": "wave38-complete-endpoint-construction-audit-v1",
        "role": "construction",
        "claim_label": "DERIVED",
        "status": "PASS",
        "checks": {
            "static_inventory_byte_identical": True,
            "fixture_catalog_byte_identical": True,
            "fixture_pool_byte_identical": True,
            "fixture_prism_witnesses": expected_catalog["prism_witness_count"],
            "fixture_exact_cuts": len(cuts),
            "frozen_input_count": len(frozen_inputs),
            "endpoint_refined_case_count": inventory_payload.count(
                b'"refined_branch"'
            ),
        },
        "frozen_inputs": frozen_inputs,
        "artifacts": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256_path(path),
            }
            for path in (
                inventory_path,
                fixture_path,
                catalog_path,
                pool_path,
            )
        },
        "limitations": [
            "This is a construction replay, not independent verification.",
            "No target OPB formula was generated or solved.",
            "No SAT witness or UNSAT proof was produced.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    payload = canonical_payload(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    else:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
