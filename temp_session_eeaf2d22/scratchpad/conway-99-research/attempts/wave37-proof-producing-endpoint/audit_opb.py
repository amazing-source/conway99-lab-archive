#!/usr/bin/env python3
"""Stream-audit OPB syntax and metadata without importing the exporter."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


HEADER_RE = re.compile(
    rb"^\* #variable= ([1-9][0-9]*) #constraint= ([1-9][0-9]*)\n$"
)
CONSTRAINT_RE = re.compile(
    rb"^(?P<terms>(?:\+1 (?:~)?x[1-9][0-9]* )+)"
    rb">= (?P<rhs>-?[0-9]+) ;\n$"
)
VARIABLE_RE = re.compile(rb"\+1 (?:~)?x([1-9][0-9]*)")


def audit(opb: Path, metadata_path: Path) -> dict[str, object]:
    payload = opb.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if b"\r" in payload:
        raise ValueError("OPB is not canonical LF text")
    lines = payload.splitlines(keepends=True)
    if not lines or not lines[-1].endswith(b"\n"):
        raise ValueError("OPB must end in LF")

    header_match = HEADER_RE.fullmatch(lines[0])
    if header_match is None:
        raise ValueError("invalid OPB header")
    variable_count = int(header_match.group(1))
    declared_constraints = int(header_match.group(2))

    term_histogram: Counter[int] = Counter()
    rhs_histogram: Counter[int] = Counter()
    variables_seen: set[int] = set()
    complemented_terms = 0
    total_terms = 0
    for line_number, line in enumerate(lines[1:], start=2):
        match = CONSTRAINT_RE.fullmatch(line)
        if match is None:
            raise ValueError(f"invalid constraint syntax at line {line_number}")
        variables = [int(raw) for raw in VARIABLE_RE.findall(match.group("terms"))]
        if not variables:
            raise AssertionError("constraint had no variables")
        if max(variables) > variable_count:
            raise ValueError(f"variable out of range at line {line_number}")
        term_histogram[len(variables)] += 1
        rhs_histogram[int(match.group("rhs"))] += 1
        variables_seen.update(variables)
        complemented_terms += match.group("terms").count(b"~")
        total_terms += len(variables)

    actual_constraints = len(lines) - 1
    if actual_constraints != declared_constraints:
        raise ValueError("header constraint count does not match body")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    declared_opb = metadata["opb"]
    expected = {
        "bytes": len(payload),
        "constraint_count": actual_constraints,
        "path": opb.as_posix(),
        "sha256": digest,
    }
    if declared_opb != expected:
        raise ValueError("formula metadata does not match OPB bytes")

    return {
        "format": "wave37-opb-stream-audit-v1",
        "status": "PASS",
        "scope": "syntax, canonical bytes, declared counts, and metadata binding",
        "opb": expected,
        "header": {
            "variables": variable_count,
            "constraints": declared_constraints,
        },
        "body": {
            "minimum_variable": min(variables_seen),
            "maximum_variable": max(variables_seen),
            "distinct_variables": len(variables_seen),
            "total_terms": total_terms,
            "complemented_terms": complemented_terms,
            "term_count_histogram": {
                str(key): term_histogram[key] for key in sorted(term_histogram)
            },
            "rhs_histogram": {
                str(key): rhs_histogram[key] for key in sorted(rhs_histogram)
            },
        },
        "limitations": [
            "This audit does not independently derive the SRG encoding.",
            "This audit does not decide satisfiability.",
            "This audit is not an UNSAT proof check or a graph-witness check.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--opb", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.opb, args.metadata)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
