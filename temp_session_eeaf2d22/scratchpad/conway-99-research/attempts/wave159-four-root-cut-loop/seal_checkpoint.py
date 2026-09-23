#!/usr/bin/env python3
"""Write the Wave159 package manifest."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "package-manifest.sha256"


def main() -> int:
    paths = sorted(
        path
        for path in HERE.iterdir()
        if path.is_file()
        and path != OUTPUT
        and not path.name.endswith((".tmp", ".stdout.txt", ".stderr.txt"))
    )
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  "
        f"{path.relative_to(ROOT).as_posix()}"
        for path in paths
    ]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sealed {len(paths)} files in {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
