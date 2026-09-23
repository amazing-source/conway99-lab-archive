"""Create or verify the Wave 124 verifier package manifest."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "package-manifest.sha256"
INCLUDED = (
    "README.md",
    "protocol.md",
    "verification-report.md",
    "run-report.yaml",
    "discovery-inventory-preinspection.tsv",
    "precomparison.sha256",
    "independent_verify.py",
    "independent-results.json",
    "independent_jacobi_audit.py",
    "independent-jacobi-results.json",
    "compare_sealed.py",
    "comparison.json",
    "test_independent_verify.py",
    "test_independent_jacobi_audit.py",
    "seal_checkpoint.py",
)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def payload() -> str:
    return "".join(
        f"{sha256(HERE / name)}  {name}\n" for name in INCLUDED
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.write == args.verify:
        raise SystemExit("choose exactly one of --write or --verify")
    expected = payload()
    if args.write:
        MANIFEST.write_text(expected, encoding="utf-8", newline="\n")
    elif MANIFEST.read_text(encoding="utf-8") != expected:
        raise SystemExit("package manifest mismatch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
