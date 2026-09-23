"""Create or verify the sealed Wave 124 package manifest."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "package-manifest.sha256"
INCLUDED = (
    "README.md",
    "protocol.md",
    "derivation.md",
    "failed-routes.md",
    "literature-freeze.md",
    "run-report.yaml",
    "input-freeze.sha256",
    "exact_check.py",
    "exact-results.json",
    "test_exact_check.py",
    "seal_checkpoint.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def payload() -> str:
    return "".join(f"{sha256(HERE / name)}  {name}\n" for name in INCLUDED)


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
