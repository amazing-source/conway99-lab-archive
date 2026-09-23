#!/usr/bin/env python3
"""Create and verify a deterministic gzip publication artifact for the CNF."""

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
    while True:
        block = handle.read(CHUNK)
        if not block:
            break
        digest.update(block)
        size += len(block)
    return digest.hexdigest(), size


def package(source: Path, output: Path) -> dict[str, object]:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    source_digest = hashlib.sha256()
    source_size = 0
    with source.open("rb") as inp, temporary.open("wb") as raw_out:
        # Empty embedded filename plus mtime=0 makes the bytes independent of
        # path and wall clock.  The OS byte emitted by gzip is normalized below.
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw_out, compresslevel=9, mtime=0
        ) as compressed:
            while True:
                block = inp.read(CHUNK)
                if not block:
                    break
                source_digest.update(block)
                source_size += len(block)
                compressed.write(block)
    # Python's gzip header records an OS marker.  Normalize it to 255
    # ("unknown") for cross-platform deterministic bytes.
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
    if (restored_sha, restored_size) != (source_digest.hexdigest(), source_size):
        raise AssertionError("gzip round trip does not reproduce the exact source")
    return {
        "schema_version": 1,
        "status": "PASS",
        "source": {
            "path": str(source),
            "bytes": source_size,
            "sha256": source_digest.hexdigest(),
        },
        "compressed": {
            "path": str(output),
            "bytes": compressed_size,
            "sha256": compressed_sha,
            "format": "gzip deflate level 9, mtime 0, empty filename, OS byte 255",
        },
        "round_trip": {
            "bytes": restored_size,
            "sha256": restored_sha,
            "exact": True,
        },
        "publication_choice": {
            "ordinary_git_include": [
                "deterministic generator",
                "criterion specification and audits",
                "compressed CNF artifact",
            ],
            "ordinary_git_exclude": "raw rooted-complete.cnf (retained locally; regenerate or decompress exactly)",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    result = package(args.source, args.output)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
