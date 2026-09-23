#!/usr/bin/env python3
"""Merge exact per-candidate prism cuts into a cumulative deterministic pool."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from complete_endpoint import build_cut_pool, validate_cut_pool


def no_duplicate_object_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> tuple[bytes, dict[str, object]]:
    raw = path.read_bytes()
    parsed = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=no_duplicate_object_keys,
    )
    if not isinstance(parsed, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return raw, parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, action="append", default=[])
    parser.add_argument("--pool", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    if args.verify_only:
        if args.pool is None:
            raise SystemExit("--verify-only requires --pool")
        if not args.catalog:
            raise SystemExit("--verify-only requires every source --catalog")
        _, pool = load_json(args.pool)
        catalogs = []
        for path in args.catalog:
            raw, catalog = load_json(path)
            catalogs.append((hashlib.sha256(raw).hexdigest(), catalog))
        cuts = validate_cut_pool(
            pool,
            source_catalogs=catalogs,
            require_sources=True,
        )
        print(
            json.dumps(
                {
                    "status": "PASS_SOURCE_BOUND_POOL",
                    "cut_count": len(cuts),
                },
                sort_keys=True,
            )
        )
        return 0

    if not args.catalog or args.output is None:
        raise SystemExit("merge mode requires one or more --catalog and --output")
    catalogs = []
    for path in args.catalog:
        raw, catalog = load_json(path)
        catalogs.append((hashlib.sha256(raw).hexdigest(), catalog))
    result = build_cut_pool(catalogs)
    validate_cut_pool(result, source_catalogs=catalogs, require_sources=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "source_catalog_count": len(catalogs),
                "cut_count": result["deduplicated_cut_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
