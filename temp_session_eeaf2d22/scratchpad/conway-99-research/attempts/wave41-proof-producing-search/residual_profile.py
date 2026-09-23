#!/usr/bin/env python3
"""Profile the exact branch-15 OPB after generalized-unit propagation.

The profile identifies the variables that occur most often in constraints
with exactly one unit of residual slack.  Falsifying such a literal triggers
new generalized-unit propagation, so these are deterministic candidates for
bounded failed-literal probes.  The profile itself proves no new literal.
"""

from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter
from pathlib import Path

from propagation_scout import (
    DEFAULT_SOURCE,
    EXPECTED_GZIP_SHA256,
    EXPECTED_RAW_SHA256,
    PRIMARY_VARIABLES,
    canonical_payload,
    parse_constraint,
    sha256_bytes,
)


def load_closure(path: Path) -> tuple[dict[int, bool], dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("format") != "wave41-generalized-unit-closure-certificate-v1":
        raise ValueError("unsupported closure certificate format")
    source = data.get("source")
    if not isinstance(source, dict):
        raise ValueError("closure source record is missing")
    if source.get("gzip_sha256") != EXPECTED_GZIP_SHA256:
        raise ValueError("closure binds the wrong gzip source")
    if source.get("raw_sha256") != EXPECTED_RAW_SHA256:
        raise ValueError("closure binds the wrong raw source")
    if data.get("result", {}).get("contradiction") is not None:
        raise ValueError("cannot profile a contradictory closure")
    assignments: dict[int, bool] = {}
    for derivation in data.get("derivations", []):
        variable = derivation.get("variable")
        value = derivation.get("value")
        if type(variable) is not int or type(value) is not bool:
            raise ValueError("malformed closure derivation")
        if variable in assignments:
            raise ValueError("closure assigns a variable twice")
        assignments[variable] = value
    return assignments, data


def build_profile(
    source_path: Path,
    closure_path: Path,
    top_count: int,
) -> dict[str, object]:
    assignments, closure = load_closure(closure_path)
    compressed = source_path.read_bytes()
    if sha256_bytes(compressed) != EXPECTED_GZIP_SHA256:
        raise ValueError("source gzip SHA-256 mismatch")

    slack_histogram: Counter[int] = Counter()
    width_histogram: Counter[int] = Counter()
    tight_literal_counts: Counter[tuple[int, bool]] = Counter()
    tight_primary_counts: Counter[int] = Counter()
    tight_constraints = 0
    open_constraints = 0
    with gzip.open(source_path, "rb") as stream:
        header = stream.readline()
        if not header.startswith(b"* #variable="):
            raise ValueError("unexpected OPB header")
        for raw_line in stream:
            constraint = parse_constraint(raw_line)
            true_count = 0
            unassigned: list[tuple[int, bool]] = []
            for variable, positive in constraint.literals:
                value = assignments.get(variable)
                if value is None:
                    unassigned.append((variable, positive))
                elif value is positive:
                    true_count += 1
            if not unassigned:
                continue
            residual_required = constraint.bound - true_count
            slack = len(unassigned) - residual_required
            if slack < 1:
                raise ValueError("closure is not at a noncontradictory fixed point")
            open_constraints += 1
            slack_histogram[slack] += 1
            width_histogram[len(unassigned)] += 1
            if slack == 1:
                tight_constraints += 1
                for literal in unassigned:
                    tight_literal_counts[literal] += 1
                    if literal[0] <= PRIMARY_VARIABLES:
                        tight_primary_counts[literal[0]] += 1

    ranked_literals = sorted(
        (
            {
                "variable": variable,
                "literal_value": value,
                "tight_occurrences": count,
                "primary": variable <= PRIMARY_VARIABLES,
            }
            for (variable, value), count in tight_literal_counts.items()
        ),
        key=lambda row: (
            -int(row["tight_occurrences"]),
            not bool(row["primary"]),
            int(row["variable"]),
            not bool(row["literal_value"]),
        ),
    )
    ranked_primary = sorted(
        (
            {"variable": variable, "tight_occurrences": count}
            for variable, count in tight_primary_counts.items()
        ),
        key=lambda row: (-int(row["tight_occurrences"]), int(row["variable"])),
    )
    return {
        "format": "wave41-branch15-residual-profile-v1",
        "role": "construction",
        "claim_label": "CANDIDATE_DIAGNOSTIC",
        "scope": "branch 15 after the candidate generalized-unit fixed point",
        "source": {
            "path": closure["source"]["path"],
            "gzip_sha256": EXPECTED_GZIP_SHA256,
            "raw_sha256": EXPECTED_RAW_SHA256,
        },
        "closure": {
            "path": closure_path.as_posix(),
            "sha256": sha256_bytes(closure_path.read_bytes()),
            "forced_variables": len(assignments),
        },
        "open_constraints": open_constraints,
        "tight_slack_one_constraints": tight_constraints,
        "slack_histogram": {
            str(slack): slack_histogram[slack]
            for slack in sorted(slack_histogram)
        },
        "residual_width_histogram": {
            str(width): width_histogram[width]
            for width in sorted(width_histogram)
        },
        "top_tight_literals": ranked_literals[:top_count],
        "top_primary_probe_variables": ranked_primary[:top_count],
        "limitations": [
            "This is a branching diagnostic, not a SAT or UNSAT result.",
            "High tight-constraint incidence does not imply either polarity fails.",
            "No endpoint case, endpoint value, or global Conway claim is decided.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--closure", type=Path, required=True)
    parser.add_argument("--top", type=int, default=32)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.top < 1:
        raise SystemExit("--top must be positive")
    result = build_profile(args.source, args.closure, args.top)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_payload(result))
    print(
        json.dumps(
            {
                "open_constraints": result["open_constraints"],
                "tight_slack_one_constraints": result[
                    "tight_slack_one_constraints"
                ],
                "top_primary_probe_variables": result[
                    "top_primary_probe_variables"
                ][:10],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
