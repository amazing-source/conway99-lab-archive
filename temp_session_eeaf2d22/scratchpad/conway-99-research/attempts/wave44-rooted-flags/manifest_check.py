#!/usr/bin/env python3
"""Verify the frozen Wave 44 package manifest with the standard library."""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "attempts/wave44-rooted-flags/package-manifest.sha256"
EXPECTED = {
    "agents/2026-07-27-wave44-rooted-flags.md",
    "attempts/wave44-rooted-flags/README.md",
    "attempts/wave44-rooted-flags/derivation.md",
    "attempts/wave44-rooted-flags/discover_z3.py",
    "attempts/wave44-rooted-flags/exact-results.json",
    "attempts/wave44-rooted-flags/exact_check.py",
    "attempts/wave44-rooted-flags/failed-routes.md",
    "attempts/wave44-rooted-flags/input-freeze.sha256",
    "attempts/wave44-rooted-flags/manifest_check.py",
    "attempts/wave44-rooted-flags/rooted-witness.json",
    "attempts/wave44-rooted-flags/row-system.json",
    "attempts/wave44-rooted-flags/run-report.yaml",
    "attempts/wave44-rooted-flags/test-results.txt",
    "attempts/wave44-rooted-flags/test_exact_check.py",
    "attempts/wave44-rooted-flags/verify_frozen.py",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    require(MANIFEST.is_file(), "package manifest is missing")
    records: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        MANIFEST.read_text(encoding="utf-8").splitlines(), start=1
    ):
        require(raw_line and "  " in raw_line, f"bad manifest line {line_number}")
        digest, relative = raw_line.split("  ", 1)
        posix = PurePosixPath(relative)
        require(
            len(digest) == 64
            and all(character in "0123456789abcdef" for character in digest),
            f"bad SHA-256 on line {line_number}",
        )
        require(
            not posix.is_absolute()
            and ".." not in posix.parts
            and relative == posix.as_posix(),
            f"unsafe path on line {line_number}",
        )
        require(relative not in records, f"duplicate path {relative}")
        records[relative] = digest
    require(set(records) == EXPECTED, "manifest file set changed")
    for relative, expected_digest in records.items():
        path = ROOT.joinpath(*PurePosixPath(relative).parts)
        require(path.is_file(), f"missing package file {relative}")
        require(
            sha256_file(path) == expected_digest,
            f"SHA-256 mismatch for {relative}",
        )
    print(
        f"PASS {len(records)} files "
        f"manifest_sha256={sha256_file(MANIFEST)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
