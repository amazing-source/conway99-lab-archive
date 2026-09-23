#!/usr/bin/env python3
"""Verify exact bytes in the sealed Wave 63 package."""

from __future__ import annotations

import hashlib
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
MANIFEST = PACKAGE / "package-manifest.sha256"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_manifest() -> dict:
    checked = 0
    names = set()
    for line in MANIFEST.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        expected, name = line.split("  ", 1)
        if name in names:
            raise AssertionError(f"duplicate manifest entry: {name}")
        names.add(name)
        path = PACKAGE / name
        if not path.is_file():
            raise AssertionError(f"missing manifest file: {name}")
        actual = sha256(path)
        if actual != expected:
            raise AssertionError(
                f"manifest mismatch for {name}: {actual} != {expected}"
            )
        checked += 1
    actual_names = {
        path.name
        for path in PACKAGE.iterdir()
        if path.is_file() and path.name != MANIFEST.name
    }
    if names != actual_names:
        raise AssertionError(
            f"manifest coverage differs: missing={actual_names - names}, "
            f"stale={names - actual_names}"
        )
    return {"manifest_entries_checked": checked, "status": "PASS"}


if __name__ == "__main__":
    print(verify_manifest())
