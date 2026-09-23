#!/usr/bin/env python3
"""Generate the minimal generalized-unit proof for one branch-15 shard.

The source formula is the published, gzip-compressed Wave 37 OPB.  This
generator does not solve it.  It extracts four SHA-bound constraints and
records a generalized-unit propagation proof that branch 15 together with
``x187 = 1`` is inconsistent.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = (
    REPOSITORY_ROOT
    / "attempts"
    / "wave37-proof-producing-endpoint"
    / "branch-15.opb.gz"
)
EXPECTED_GZIP_SHA256 = (
    "7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e"
)
EXPECTED_RAW_SHA256 = (
    "4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5"
)
SOURCE_LINES = (106, 285938, 286004, 571132)
TERM_RE = re.compile(r"\+1\s+(~)?x([1-9][0-9]*)")
CONSTRAINT_RE = re.compile(
    r"^(?:\+1\s+(?:~)?x[1-9][0-9]*\s+)+>=\s+([0-9]+)\s+;\s*$"
)


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def parse_constraint(text: str) -> tuple[tuple[tuple[int, bool], ...], int]:
    match = CONSTRAINT_RE.fullmatch(text)
    if match is None:
        raise ValueError("unsupported OPB constraint syntax")
    literals = tuple(
        (int(term.group(2)), term.group(1) is None)
        for term in TERM_RE.finditer(text)
    )
    variables = [variable for variable, _ in literals]
    if len(variables) != len(set(variables)):
        raise ValueError("constraint repeats a variable")
    return literals, int(match.group(1))


def read_source(path: Path) -> tuple[bytes, dict[int, str], str, int]:
    compressed = path.read_bytes()
    if sha256_bytes(compressed) != EXPECTED_GZIP_SHA256:
        raise ValueError("source gzip SHA-256 does not match the frozen formula")
    digest = hashlib.sha256()
    selected: dict[int, str] = {}
    constraint_count = 0
    with gzip.open(path, "rb") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            digest.update(raw_line)
            if line_number == 1:
                if raw_line != b"* #variable= 289338 #constraint= 574615\n":
                    raise ValueError("unexpected OPB header")
                continue
            constraint_count += 1
            if line_number in SOURCE_LINES:
                selected[line_number] = raw_line.decode("ascii").rstrip("\n")
    if digest.hexdigest() != EXPECTED_RAW_SHA256:
        raise ValueError("decompressed OPB SHA-256 does not match the frozen formula")
    if constraint_count != 574615:
        raise ValueError("unexpected OPB constraint count")
    if set(selected) != set(SOURCE_LINES):
        raise ValueError("one or more proof source lines are missing")
    return compressed, selected, digest.hexdigest(), constraint_count


def source_record(line_number: int, text: str) -> dict[str, object]:
    literals, bound = parse_constraint(text)
    return {
        "line": line_number,
        "sha256": sha256_bytes((text + "\n").encode("ascii")),
        "term_count": len(literals),
        "bound": bound,
    }


def build_certificate(source: Path) -> dict[str, object]:
    compressed, lines, raw_sha256, constraint_count = read_source(source)
    source_path = source.resolve().relative_to(REPOSITORY_ROOT).as_posix()
    records = {
        str(line): source_record(line, lines[line]) for line in SOURCE_LINES
    }
    return {
        "format": "wave39-generalized-unit-shard-certificate-v1",
        "role": "construction",
        "claim_label": "CANDIDATE",
        "scope": (
            "refined endpoint branch 15 conjoined with the primary-edge "
            "assumption x187=1"
        ),
        "source": {
            "path": source_path,
            "gzip_bytes": len(compressed),
            "gzip_sha256": sha256_bytes(compressed),
            "raw_sha256": raw_sha256,
            "variables": 289338,
            "constraints": constraint_count,
        },
        "branch": {
            "refined_branch": 15,
            "parent_branch": 4,
            "assumption": {"variable": 187, "value": True},
            "assumption_edge": {
                "residual_indices": [2, 24],
                "residual_labels": [[0, 4], [2, 4]],
            },
            "complementary_open_shard": {
                "variable": 187,
                "value": False,
            },
        },
        "source_constraints": records,
        "trace": [
            {
                "rule": "generalized_unit",
                "source_line": 285938,
                "derive": {"variable": 24, "value": True},
            },
            {
                "rule": "generalized_unit",
                "source_line": 286004,
                "derive": {"variable": 2, "value": True},
            },
            {
                "rule": "generalized_unit",
                "source_line": 571132,
                "derive": {"variable": 3591, "value": False},
            },
            {
                "rule": "contradiction",
                "source_line": 106,
            },
        ],
        "logical_summary": {
            "normalized_edge_unit": "x24=1",
            "refinement_edge_unit": "x2=1",
            "common_neighbor_capacity": (
                "line 571132 and x2=1 force x3591=0"
            ),
            "wedge_clause": (
                "line 106, x24=1, x187=1, and x3591=0 are inconsistent"
            ),
            "entailed_primary_literal": "x187=0",
        },
        "coverage": {
            "closed_shards": 1,
            "exhaustive_polarity_shards": 2,
            "closed_shard": "branch15 AND x187=1",
            "open_shard": "branch15 AND x187=0",
            "closed_endpoint_cases": 0,
            "total_endpoint_cases": 33,
        },
        "limitations": [
            "This closes only one polarity shard inside refined branch 15.",
            "It does not close refined branch 15 or any complete endpoint case.",
            "The complete endpoint proof coverage therefore remains 0/33 cases.",
            "The source formula has only the six fixed-triangle prism families.",
            "The proof uses an independently replayable project-local rule, not VeriPB or CakePB.",
            "Independent verification is required before promotion to VERIFIED.",
            "No graph, endpoint exclusion, upper-bound improvement, or novelty claim follows.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    certificate = build_certificate(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_payload(certificate))
    print(
        json.dumps(
            {
                "status": "CANDIDATE_SHARD_CERTIFICATE_WRITTEN",
                "closed_shard": certificate["coverage"]["closed_shard"],
                "closed_endpoint_cases": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
