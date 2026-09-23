#!/usr/bin/env python3
"""Create a deterministic gzip package for a Wave 37 OPB formula."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path


CHUNK = 1024 * 1024


def hash_stream(handle) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    while block := handle.read(CHUNK):
        digest.update(block)
        size += len(block)
    return digest.hexdigest(), size


def package(source: Path, output: Path) -> dict[str, object]:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    source_digest = hashlib.sha256()
    source_size = 0

    with source.open("rb") as inp, temporary.open("wb") as raw_out:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw_out,
            compresslevel=9,
            mtime=0,
        ) as compressed:
            while block := inp.read(CHUNK):
                source_digest.update(block)
                source_size += len(block)
                compressed.write(block)

    # Normalize the platform-specific gzip OS byte.
    with temporary.open("r+b") as handle:
        header = handle.read(10)
        if len(header) != 10 or header[:3] != b"\x1f\x8b\x08":
            raise ValueError("unexpected gzip header")
        handle.seek(9)
        handle.write(b"\xff")
    os.replace(temporary, output)

    with output.open("rb") as compressed_input:
        compressed_sha, compressed_size = hash_stream(compressed_input)
    with gzip.open(output, "rb") as restored:
        restored_sha, restored_size = hash_stream(restored)
    expected = (source_digest.hexdigest(), source_size)
    if (restored_sha, restored_size) != expected:
        raise AssertionError("gzip round trip does not reproduce the exact OPB")

    return {
        "format": "wave37-deterministic-opb-gzip-v1",
        "status": "PASS",
        "source": {
            "path": source.as_posix(),
            "bytes": source_size,
            "sha256": source_digest.hexdigest(),
        },
        "compressed": {
            "path": output.as_posix(),
            "bytes": compressed_size,
            "sha256": compressed_sha,
            "format": (
                "gzip deflate level 9, mtime 0, empty filename, OS byte 255"
            ),
        },
        "round_trip": {
            "bytes": restored_size,
            "sha256": restored_sha,
            "exact": True,
        },
        "publication_choice": {
            "ordinary_git_include": "compressed OPB plus deterministic exporter",
            "ordinary_git_exclude": (
                "raw OPB; regenerate it or decompress the committed gzip exactly"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    result = package(args.source, args.output)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
