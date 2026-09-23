#!/usr/bin/env python3
"""Run bounded generalized-unit failed-literal probes on branch 15.

Each selected primary variable is tested under both truth values, starting
from the SHA-bound candidate propagation closure.  All probes are advanced in
one streaming pass over the OPB at a time so the 29.8 MB raw formula is parsed
once per round rather than once per probe.

A contradictory polarity is a candidate proof that the opposite value is
entailed.  A noncontradictory fixed point is only a diagnostic and is not a
SAT result.
"""

from __future__ import annotations

import argparse
import gzip
import json
from dataclasses import dataclass, field
from pathlib import Path

from propagation_scout import (
    DEFAULT_SOURCE,
    EXPECTED_GZIP_SHA256,
    EXPECTED_RAW_SHA256,
    REPOSITORY_ROOT,
    canonical_payload,
    evaluate_constraint,
    parse_constraint,
    sha256_bytes,
)
from residual_profile import load_closure


@dataclass
class Probe:
    variable: int
    assumed_value: bool
    assignments: dict[int, bool]
    derivations: list[dict[str, object]] = field(default_factory=list)
    passes: list[dict[str, int]] = field(default_factory=list)
    contradiction: dict[str, object] | None = None
    fixed: bool = False


def parse_variables(text: str) -> tuple[int, ...]:
    try:
        values = tuple(int(part) for part in text.split(",") if part)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "variables must be comma-separated positive integers"
        ) from error
    if not values or any(value < 1 for value in values):
        raise argparse.ArgumentTypeError("variables must be positive")
    if len(values) != len(set(values)):
        raise argparse.ArgumentTypeError("variables must not repeat")
    return values


def run_probes(
    source_path: Path,
    closure_path: Path,
    variables: tuple[int, ...],
) -> dict[str, object]:
    base_assignments, _ = load_closure(closure_path)
    if sha256_bytes(source_path.read_bytes()) != EXPECTED_GZIP_SHA256:
        raise ValueError("source gzip SHA-256 mismatch")
    overlap = sorted(set(variables).intersection(base_assignments))
    if overlap:
        raise ValueError(f"probe variables are already forced: {overlap}")

    probes = [
        Probe(
            variable=variable,
            assumed_value=value,
            assignments={**base_assignments, variable: value},
        )
        for variable in variables
        for value in (False, True)
    ]
    pass_index = 0
    while any(not probe.fixed for probe in probes):
        pass_index += 1
        starts = {id(probe): len(probe.assignments) for probe in probes}
        scanned = {id(probe): 0 for probe in probes}
        with gzip.open(source_path, "rb") as stream:
            header = stream.readline()
            if not header.startswith(b"* #variable="):
                raise ValueError("unexpected OPB header")
            for line_number, raw_line in enumerate(stream, start=2):
                active = [probe for probe in probes if not probe.fixed]
                if not active:
                    break
                constraint = parse_constraint(raw_line)
                line_sha256 = None
                for probe in active:
                    scanned[id(probe)] += 1
                    status, forced = evaluate_constraint(
                        constraint, probe.assignments
                    )
                    if status == "CONTRADICTION":
                        if line_sha256 is None:
                            line_sha256 = sha256_bytes(raw_line)
                        probe.contradiction = {
                            "pass": pass_index,
                            "source_line": line_number,
                            "source_line_sha256": line_sha256,
                        }
                        probe.fixed = True
                        continue
                    if status != "FORCE":
                        continue
                    if line_sha256 is None:
                        line_sha256 = sha256_bytes(raw_line)
                    for variable, value in forced:
                        prior = probe.assignments.get(variable)
                        if prior is not None:
                            if prior is not value:
                                probe.contradiction = {
                                    "pass": pass_index,
                                    "source_line": line_number,
                                    "source_line_sha256": line_sha256,
                                    "assignment_conflict": {
                                        "variable": variable,
                                        "prior": prior,
                                        "forced": value,
                                    },
                                }
                                probe.fixed = True
                                break
                            continue
                        probe.assignments[variable] = value
                        probe.derivations.append(
                            {
                                "index": len(probe.derivations) + 1,
                                "pass": pass_index,
                                "variable": variable,
                                "value": value,
                                "source_line": line_number,
                                "source_line_sha256": line_sha256,
                                "source_term_count": len(constraint.literals),
                                "source_bound": constraint.bound,
                            }
                        )

        for probe in probes:
            if probe.passes and probe.fixed:
                continue
            start = starts[id(probe)]
            end = len(probe.assignments)
            probe.passes.append(
                {
                    "pass": pass_index,
                    "constraints_scanned": scanned[id(probe)],
                    "assignments_before": start,
                    "assignments_after": end,
                    "new_assignments": end - start,
                }
            )
            if not probe.fixed and end == start:
                probe.fixed = True

    records: list[dict[str, object]] = []
    candidate_implications: list[dict[str, object]] = []
    for probe in probes:
        status = (
            "CANDIDATE_CONTRADICTION"
            if probe.contradiction is not None
            else "PROPAGATION_FIXED_POINT_NO_CONCLUSION"
        )
        if probe.contradiction is not None:
            candidate_implications.append(
                {
                    "variable": probe.variable,
                    "entailed_value": not probe.assumed_value,
                    "failed_assumption": probe.assumed_value,
                }
            )
        records.append(
            {
                "variable": probe.variable,
                "assumed_value": probe.assumed_value,
                "status": status,
                "contradiction": probe.contradiction,
                "new_forced_variables": len(probe.derivations),
                "passes": probe.passes,
                "derivations": probe.derivations,
            }
        )

    by_variable: dict[int, list[dict[str, object]]] = {}
    for record in records:
        by_variable.setdefault(int(record["variable"]), []).append(record)
    doubly_failed = [
        variable
        for variable, variable_records in by_variable.items()
        if all(record["contradiction"] is not None for record in variable_records)
    ]
    return {
        "format": "wave41-branch15-failed-literal-scout-v1",
        "role": "construction",
        "claim_label": "CANDIDATE",
        "scope": (
            "bounded two-polarity generalized-unit probes inside refined "
            "endpoint branch 15"
        ),
        "source": {
            "path": source_path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
            "gzip_sha256": EXPECTED_GZIP_SHA256,
            "raw_sha256": EXPECTED_RAW_SHA256,
        },
        "closure": {
            "path": closure_path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
            "sha256": sha256_bytes(closure_path.read_bytes()),
            "forced_variables": len(base_assignments),
        },
        "probe_variables": list(variables),
        "probe_count": len(probes),
        "records": records,
        "candidate_implications": candidate_implications,
        "doubly_failed_variables": doubly_failed,
        "result": {
            "candidate_implication_count": len(candidate_implications),
            "doubly_failed_variable_count": len(doubly_failed),
            "branch15_candidate_unsat_by_failed_literal": bool(doubly_failed),
            "endpoint_cases_closed": 0,
        },
        "limitations": [
            "Discovery-agent implications require independent replay.",
            "A noncontradictory propagation fixed point is not a SAT witness.",
            "Unless both polarities of one variable fail, branch 15 is not closed.",
            "The source formula contains only the parent branch's six fixed-triangle prism families.",
            "No endpoint exclusion or general upper-bound improvement is claimed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--closure", type=Path, required=True)
    parser.add_argument("--variables", type=parse_variables, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_probes(args.source, args.closure, args.variables)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_payload(result))
    summary = {
        **result["result"],
        "candidate_implications": result["candidate_implications"],
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
