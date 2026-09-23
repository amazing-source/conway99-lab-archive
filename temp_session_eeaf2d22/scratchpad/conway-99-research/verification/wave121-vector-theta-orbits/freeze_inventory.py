"""Freeze Wave 121 discovery bytes before semantic inspection."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "attempts" / "wave121-vector-theta-orbits"
OUTPUT = Path(__file__).resolve().parent / "discovery-inventory-preinspection.tsv"
EXPECTED_MANIFEST_HASH = (
    "ab3ede13ea60315885ac077cd8e0b3e7b124f34329d51e82fa2f4d08434cf803"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    manifest = SOURCE / "package-manifest.sha256"
    actual = sha256(manifest)
    if actual != EXPECTED_MANIFEST_HASH:
        raise SystemExit(f"manifest mismatch: {actual}")
    rows = ["path\tbytes\tsha256\n"]
    for path in sorted(item for item in SOURCE.rglob("*") if item.is_file()):
        rel = path.relative_to(ROOT).as_posix()
        rows.append(f"{rel}\t{path.stat().st_size}\t{sha256(path)}\n")
    OUTPUT.write_text("".join(rows), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
