#!/usr/bin/env python3
"""Write a deterministic SHA-256 manifest for the compact Wave 47 package."""

from __future__ import annotations

import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FILES = (
    HERE / "three_root_moment.py",
    HERE / "compact_handoff.py",
    HERE / "seal_package.py",
    HERE / "test_three_root_moment.py",
    HERE / "compact-handoff.json",
    HERE / "README.md",
    HERE / "run-report.yaml",
    ROOT / "agents/2026-07-27-wave47-three-root-moment.md",
    HERE / "test-results.txt",
)


def main() -> None:
    lines = []
    for path in FILES:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        relative = path.relative_to(ROOT).as_posix()
        lines.append(f"{digest}  {relative}")
    (HERE / "package-manifest.sha256").write_text(
        "\n".join(lines) + "\n", encoding="ascii", newline="\n"
    )
    print(f"sealed {len(lines)}/{len(FILES)} compact files")


if __name__ == "__main__":
    main()
