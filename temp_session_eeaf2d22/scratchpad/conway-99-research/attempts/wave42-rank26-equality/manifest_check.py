#!/usr/bin/env python3
"""Validate the Wave 42 package SHA-256 manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).resolve().parent / "package-manifest.sha256"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate() -> int:
    entries = []
    for number, raw in enumerate(
        MANIFEST.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw:
            continue
        digest, separator, name = raw.partition("  ")
        if not separator or len(digest) != 64:
            raise ValueError(f"malformed manifest line {number}")
        path = ROOT / name
        if not path.is_file():
            raise ValueError(f"missing manifest file: {name}")
        actual = sha256(path)
        if actual != digest:
            raise ValueError(
                f"hash mismatch for {name}: expected {digest}, actual {actual}"
            )
        entries.append(name)
    if len(entries) != len(set(entries)):
        raise ValueError("duplicate manifest entry")
    print(f"PASS manifest entries={len(entries)}")
    return len(entries)


if __name__ == "__main__":
    validate()
