from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "package-manifest.sha256"
EXCLUDED = {MANIFEST.name, "__pycache__"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    repo = ROOT.parents[1]
    rows = []
    for path in sorted(ROOT.iterdir(), key=lambda item: item.name):
        if path.name in EXCLUDED or not path.is_file():
            continue
        relative = path.relative_to(repo).as_posix()
        rows.append(f"{sha256(path)}  {relative}")
    MANIFEST.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"sealed {len(rows)} files in {MANIFEST}")


if __name__ == "__main__":
    main()
