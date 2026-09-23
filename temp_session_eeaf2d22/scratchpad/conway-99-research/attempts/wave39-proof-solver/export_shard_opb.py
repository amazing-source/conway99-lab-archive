#!/usr/bin/env python3
"""Export the exact branch-15 ``x187=1`` OPB shard by streaming.

The exporter changes only the declared constraint count and appends the single
unit assumption.  It validates both compressed and decompressed hashes of the
published Wave 37 source before writing.  The raw OPB is local-only; the
deterministic gzip and metadata are suitable for publication.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = (
    REPOSITORY_ROOT
    / "attempts"
    / "wave37-proof-producing-endpoint"
    / "branch-15.opb.gz"
)
SOURCE_GZIP_SHA256 = (
    "7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e"
)
SOURCE_RAW_SHA256 = (
    "4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5"
)
SOURCE_HEADER = b"* #variable= 289338 #constraint= 574615\n"
SHARD_HEADER = b"* #variable= 289338 #constraint= 574616\n"
ASSUMPTION = b"+1 x187 >= 1 ;\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def validated_output(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise ValueError(f"{label} must resolve inside the repository") from error
    if not relative.parts:
        raise ValueError(f"{label} must name a file below the repository root")
    return resolved


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def export_shard(
    source: Path,
    raw_output: Path,
    gzip_output: Path,
    metadata_output: Path,
) -> dict[str, object]:
    raw_output = validated_output(raw_output, "raw OPB output")
    gzip_output = validated_output(gzip_output, "gzip OPB output")
    metadata_output = validated_output(metadata_output, "metadata output")
    if len({raw_output, gzip_output, metadata_output}) != 3:
        raise ValueError("all outputs must be distinct")
    if sha256_file(source) != SOURCE_GZIP_SHA256:
        raise ValueError("source gzip SHA-256 mismatch")

    raw_output.parent.mkdir(parents=True, exist_ok=True)
    gzip_output.parent.mkdir(parents=True, exist_ok=True)
    metadata_output.parent.mkdir(parents=True, exist_ok=True)
    raw_temporary = raw_output.with_suffix(raw_output.suffix + ".tmp")
    gzip_temporary = gzip_output.with_suffix(gzip_output.suffix + ".tmp")
    source_digest = hashlib.sha256()
    shard_digest = hashlib.sha256()
    shard_bytes = 0
    source_constraint_count = 0
    try:
        with gzip.open(source, "rb") as source_stream, raw_temporary.open(
            "wb"
        ) as output:
            source_header = source_stream.readline()
            source_digest.update(source_header)
            if source_header != SOURCE_HEADER:
                raise ValueError("source OPB header mismatch")
            output.write(SHARD_HEADER)
            shard_digest.update(SHARD_HEADER)
            shard_bytes += len(SHARD_HEADER)
            for line in source_stream:
                source_digest.update(line)
                source_constraint_count += 1
                output.write(line)
                shard_digest.update(line)
                shard_bytes += len(line)
            output.write(ASSUMPTION)
            shard_digest.update(ASSUMPTION)
            shard_bytes += len(ASSUMPTION)
        if source_digest.hexdigest() != SOURCE_RAW_SHA256:
            raise ValueError("decompressed source OPB SHA-256 mismatch")
        if source_constraint_count != 574615:
            raise ValueError("source OPB constraint count mismatch")
        os.replace(raw_temporary, raw_output)

        with raw_output.open("rb") as source_stream, gzip_temporary.open(
            "wb"
        ) as target:
            with gzip.GzipFile(
                filename="",
                mode="wb",
                fileobj=target,
                compresslevel=9,
                mtime=0,
            ) as compressed:
                while block := source_stream.read(1024 * 1024):
                    compressed.write(block)
        os.replace(gzip_temporary, gzip_output)
    finally:
        if raw_temporary.exists():
            raw_temporary.unlink()
        if gzip_temporary.exists():
            gzip_temporary.unlink()

    metadata = {
        "format": "wave39-branch15-primary-polarity-shard-opb-v1",
        "role": "construction",
        "claim_label": "CANDIDATE_FORMULA_ONLY",
        "scope": "refined endpoint branch 15 conjoined with x187=1",
        "source": {
            "path": source.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
            "gzip_sha256": SOURCE_GZIP_SHA256,
            "raw_sha256": SOURCE_RAW_SHA256,
            "constraints": 574615,
        },
        "transformation": {
            "kind": "append_unit_constraint",
            "assumption": "x187=1",
            "constraint": ASSUMPTION.decode("ascii").rstrip("\n"),
        },
        "opb": {
            "raw_path": raw_output.relative_to(REPOSITORY_ROOT).as_posix(),
            "raw_bytes": shard_bytes,
            "raw_sha256": shard_digest.hexdigest(),
            "gzip_path": gzip_output.relative_to(REPOSITORY_ROOT).as_posix(),
            "gzip_bytes": gzip_output.stat().st_size,
            "gzip_sha256": sha256_file(gzip_output),
            "variables": 289338,
            "constraints": 574616,
        },
        "coverage": {
            "closed_endpoint_cases_before_solving": 0,
            "total_endpoint_cases": 33,
        },
        "limitations": [
            "Formula export is not a satisfiability conclusion.",
            "The formula is one polarity shard inside refined branch 15.",
            "The raw OPB is local-only and regenerated from the published gzip.",
            "UNSAT promotion requires retained proof and independent replay.",
        ],
    }
    metadata_output.write_bytes(canonical_payload(metadata))
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--gzip", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()
    result = export_shard(args.source, args.raw, args.gzip, args.metadata)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
