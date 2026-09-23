#!/usr/bin/env python3
"""Verify the frozen Wave 46 package manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).resolve().parent / "package-manifest.sha256"


def main() -> int:
    checked = 0
    for line_number, raw in enumerate(
        MANIFEST.read_text(encoding="ascii").splitlines(), 1
    ):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            expected, relative = line.split(maxsplit=1)
        except ValueError as error:
            raise ValueError(f"malformed manifest line {line_number}") from error
        path = ROOT / relative
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            raise ValueError(
                f"hash mismatch for {relative}: {observed} != {expected}"
            )
        checked += 1
    if checked == 0:
        raise ValueError("empty package manifest")
    print(f"PASS: {checked} Wave46 package hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
