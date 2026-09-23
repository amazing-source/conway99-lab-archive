from __future__ import annotations

import hashlib
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
OUTPUT = PACKAGE / "package-manifest.sha256"
INCLUDED = (
    "README.md",
    "derivation.md",
    "exact-results.json",
    "exact_check.py",
    "failed-routes.md",
    "input-freeze.sha256",
    "protocol.md",
    "run-report.yaml",
    "seal_package.py",
    "test_exact_check.py",
    "verifier-request.md",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    for name in INCLUDED:
        if not (PACKAGE / name).is_file():
            raise FileNotFoundError(name)
    lines = [
        f"{sha256(PACKAGE / name)}  attempts/wave128-alternative-spaces/{name}"
        for name in INCLUDED
    ]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")


if __name__ == "__main__":
    main()
