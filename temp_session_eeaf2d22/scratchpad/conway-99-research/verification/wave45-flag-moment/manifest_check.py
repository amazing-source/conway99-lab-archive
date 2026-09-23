#!/usr/bin/env python3
"""Verify the frozen Wave 45 clean-room verifier package."""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "verification/wave45-flag-moment/package-manifest.sha256"
EXPECTED = {
    "agents/2026-07-27-wave45-flag-moment-verifier.md",
    "verification/wave45-flag-moment/README.md",
    "verification/wave45-flag-moment/compare_discovery.py",
    "verification/wave45-flag-moment/comparison-results.json",
    "verification/wave45-flag-moment/failed-routes.md",
    "verification/wave45-flag-moment/independent-freeze.sha256",
    "verification/wave45-flag-moment/independent-results.json",
    "verification/wave45-flag-moment/independent_verify.py",
    "verification/wave45-flag-moment/manifest_check.py",
    "verification/wave45-flag-moment/protocol-freeze.md",
    "verification/wave45-flag-moment/run-report.yaml",
    "verification/wave45-flag-moment/test-results.txt",
    "verification/wave45-flag-moment/test_comparison.py",
    "verification/wave45-flag-moment/test_independent_verify.py",
    "verification/wave45-flag-moment/verification-report.md",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    require(MANIFEST.is_file(), "package manifest is missing")
    records: dict[str, str] = {}
    for line_number, line in enumerate(
        MANIFEST.read_text(encoding="utf-8").splitlines(), start=1
    ):
        require(line and "  " in line, f"bad manifest line {line_number}")
        digest, relative = line.split("  ", 1)
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
        require(relative not in records, f"duplicate manifest path {relative}")
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
