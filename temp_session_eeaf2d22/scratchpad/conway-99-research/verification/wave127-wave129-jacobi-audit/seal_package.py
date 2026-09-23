from __future__ import annotations

import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FILES = (
    "README.md",
    "comparison.md",
    "independent-results.json",
    "independent_verify.py",
    "input-freeze.sha256",
    "protocol.md",
    "run-report.yaml",
    "test_independent_verify.py",
    "verification-report.md",
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


lines = []
for name in FILES:
    path = HERE / name
    relative = path.relative_to(ROOT).as_posix()
    lines.append(f"{digest(path)}  {relative}")
(HERE / "package-manifest.sha256").write_text(
    "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
)
