"""Fail-closed checker for the committed Wave 34 structural result."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("reduction.py")
SPEC = importlib.util.spec_from_file_location("wave34_rooted_reduction", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load hash-local reduction module")
reduction = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reduction)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full-census",
        action="store_true",
        help="independently rerun the exhaustive cycle-type census",
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=Path(__file__).with_name("results.json"),
    )
    args = parser.parse_args()

    committed = json.loads(args.results.read_text(encoding="utf-8"))
    regenerated = reduction.analyze(include_full_census=args.full_census)

    if not args.full_census:
        committed = dict(committed)
        domain = dict(committed["domain"])
        domain.pop("two_factor_cycle_census", None)
        committed["domain"] = domain

    if regenerated != committed:
        raise SystemExit("FAIL: regenerated result differs from committed JSON")
    print("PASS: exact structural result matches committed JSON")


if __name__ == "__main__":
    main()
