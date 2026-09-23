#!/usr/bin/env python3
"""Replay generalized-unit reasoning on branch 15 plus the Wave 42 delta.

The base formula and seventh-triangle delta are streamed in a fixed order.
Every derived assignment records its exact source row and hash.  The same
engine can run bounded two-polarity probes on the 32 Wave 41 high-pressure
primary variables.  A noncontradictory fixed point is not a SAT witness.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import seventh_triangle_strengthen as delta_builder


REPOSITORY_ROOT = delta_builder.REPOSITORY_ROOT
SOURCE_OPB_GZIP = delta_builder.SOURCE_OPB_GZIP
WAVE41_CLOSURE = delta_builder.SOURCE_CLOSURE
WAVE41_FAILED_LITERAL = (
    REPOSITORY_ROOT
    / "attempts"
    / "wave41-proof-producing-search"
    / "branch-15-failed-literal-scout.json"
)
EXPECTED_WAVE41_FAILED_LITERAL_SHA256 = (
    "bf08994b8709da64684800ede9706e46c8de34ff30b9db2f831d0b0f4c4d37c3"
)
DEFAULT_CLOSURE_OUTPUT = HERE / "branch-15-combined-propagation-certificate.json"
DEFAULT_PROBE_OUTPUT = HERE / "branch-15-combined-failed-literal-scout.json"
PROBE_VARIABLES = (
    13,
    175,
    188,
    178,
    1727,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    94,
    106,
    189,
    190,
    191,
    192,
    193,
    194,
    195,
)


@dataclass(frozen=True)
class Constraint:
    literals: tuple[tuple[int, bool], ...]
    bound: int


@dataclass
class Probe:
    variable: int
    assumed_value: bool
    assignments: dict[int, bool]
    derivations: list[dict[str, object]] = field(default_factory=list)
    passes: list[dict[str, int]] = field(default_factory=list)
    contradiction: dict[str, object] | None = None
    fixed: bool = False


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def parse_constraint(raw_line: bytes) -> Constraint:
    bound_match = delta_builder.BOUND_RE.search(raw_line)
    if bound_match is None:
        raise ValueError("unsupported OPB bound syntax")
    terms = tuple(
        (int(match.group(2)), match.group(1) is None)
        for match in delta_builder.TERM_RE.finditer(raw_line)
    )
    if not terms:
        raise ValueError("constraint has no supported unit-weight literal")
    variables = [variable for variable, _ in terms]
    if len(variables) != len(set(variables)):
        raise ValueError("constraint repeats a variable")
    reconstructed = b" ".join(
        (b"+1 x" if positive else b"+1 ~x")
        + str(variable).encode("ascii")
        for variable, positive in terms
    )
    expected = (
        reconstructed
        + b" >= "
        + bound_match.group(1)
        + b" ;\n"
    )
    if expected != raw_line:
        raise ValueError("constraint contains unsupported syntax")
    return Constraint(terms, int(bound_match.group(1)))


def evaluate_constraint(
    constraint: Constraint,
    assignments: Mapping[int, bool],
) -> tuple[str, tuple[tuple[int, bool], ...]]:
    true_count = 0
    unassigned: list[tuple[int, bool]] = []
    for variable, positive in constraint.literals:
        value = assignments.get(variable)
        if value is None:
            unassigned.append((variable, positive))
        elif value is positive:
            true_count += 1
    maximum = true_count + len(unassigned)
    if maximum < constraint.bound:
        return "CONTRADICTION", ()
    if unassigned and maximum == constraint.bound:
        return "FORCE", tuple(unassigned)
    return "OPEN", ()


def delta_constraint_line(clause: Sequence[int]) -> bytes:
    return (
        " ".join(f"+1 ~x{variable}" for variable in clause) + " >= 1 ;\n"
    ).encode("ascii")


def iter_combined_constraints(
    delta_clauses: Sequence[delta_builder.Clause],
) -> Iterable[tuple[str, int, bytes, Constraint]]:
    with gzip.open(SOURCE_OPB_GZIP, "rb") as stream:
        header = stream.readline()
        match = delta_builder.HEADER_RE.fullmatch(header)
        if match is None:
            raise ValueError("unsupported base OPB header")
        if int(match.group(1)) != delta_builder.EXPECTED_VARIABLES:
            raise ValueError("base OPB variable count changed")
        if int(match.group(2)) != delta_builder.EXPECTED_CONSTRAINTS:
            raise ValueError("base OPB constraint count changed")
        for line_number, raw_line in enumerate(stream, start=2):
            yield "base_opb", line_number, raw_line, parse_constraint(raw_line)
    for row_number, clause in enumerate(delta_clauses, start=1):
        raw_line = delta_constraint_line(clause)
        yield (
            "seventh_triangle_delta",
            row_number,
            raw_line,
            Constraint(tuple((variable, False) for variable in clause), 1),
        )


def assignment_record(
    *,
    index: int,
    pass_index: int,
    variable: int,
    value: bool,
    source_kind: str,
    source_row: int,
    raw_line: bytes,
    constraint: Constraint,
) -> dict[str, object]:
    return {
        "index": index,
        "pass": pass_index,
        "variable": variable,
        "value": value,
        "source_kind": source_kind,
        "source_row": source_row,
        "source_row_sha256": sha256_bytes(raw_line),
        "source_term_count": len(constraint.literals),
        "source_bound": constraint.bound,
    }


def propagate_combined() -> dict[str, object]:
    clauses, _ = delta_builder.enumerate_delta_clauses()
    assignments: dict[int, bool] = {}
    derivations: list[dict[str, object]] = []
    passes: list[dict[str, int]] = []
    contradiction: dict[str, object] | None = None
    pass_index = 0

    while True:
        pass_index += 1
        start_count = len(assignments)
        base_scanned = 0
        delta_scanned = 0
        for source_kind, source_row, raw_line, constraint in iter_combined_constraints(
            clauses
        ):
            if source_kind == "base_opb":
                base_scanned += 1
            else:
                delta_scanned += 1
            status, forced = evaluate_constraint(constraint, assignments)
            if status == "CONTRADICTION":
                contradiction = {
                    "pass": pass_index,
                    "source_kind": source_kind,
                    "source_row": source_row,
                    "source_row_sha256": sha256_bytes(raw_line),
                }
                break
            if status != "FORCE":
                continue
            for variable, value in forced:
                prior = assignments.get(variable)
                if prior is not None:
                    if prior is not value:
                        contradiction = {
                            "pass": pass_index,
                            "source_kind": source_kind,
                            "source_row": source_row,
                            "source_row_sha256": sha256_bytes(raw_line),
                            "assignment_conflict": {
                                "variable": variable,
                                "prior": prior,
                                "forced": value,
                            },
                        }
                        break
                    continue
                assignments[variable] = value
                derivations.append(
                    assignment_record(
                        index=len(derivations) + 1,
                        pass_index=pass_index,
                        variable=variable,
                        value=value,
                        source_kind=source_kind,
                        source_row=source_row,
                        raw_line=raw_line,
                        constraint=constraint,
                    )
                )
            if contradiction is not None:
                break
        passes.append(
            {
                "pass": pass_index,
                "assignments_before": start_count,
                "assignments_after": len(assignments),
                "new_assignments": len(assignments) - start_count,
                "base_constraints_scanned": base_scanned,
                "delta_constraints_scanned": delta_scanned,
            }
        )
        if contradiction is not None or len(assignments) == start_count:
            break

    old_assignments, old_source = delta_builder.load_closure_assignments()
    assignments_match = assignments == old_assignments
    delta_derivations = sum(
        derivation["source_kind"] == "seventh_triangle_delta"
        for derivation in derivations
    )
    primary = {
        variable: value
        for variable, value in assignments.items()
        if variable <= delta_builder.PRIMARY_VARIABLES
    }
    syntactically_open_base = 0
    syntactically_open_delta = 0
    active_base = 0
    active_delta = 0
    slack_one_base = 0
    slack_one_delta = 0
    satisfied_base = 0
    satisfied_delta = 0
    for source_kind, _, _, constraint in iter_combined_constraints(clauses):
        true_count = 0
        unassigned = 0
        for variable, positive in constraint.literals:
            value = assignments.get(variable)
            if value is None:
                unassigned += 1
            elif value is positive:
                true_count += 1
        if unassigned:
            if source_kind == "base_opb":
                syntactically_open_base += 1
            else:
                syntactically_open_delta += 1
        if true_count >= constraint.bound:
            if source_kind == "base_opb":
                satisfied_base += 1
            else:
                satisfied_delta += 1
            continue
        if not unassigned:
            raise AssertionError("combined closure contains a contradiction")
        residual_required = constraint.bound - true_count
        slack = unassigned - residual_required
        if slack < 1:
            raise AssertionError("combined closure is not a fixed point")
        if source_kind == "base_opb":
            active_base += 1
            slack_one_base += slack == 1
        else:
            active_delta += 1
            slack_one_delta += slack == 1

    return {
        "format": "wave42-branch15-combined-propagation-v1",
        "role": "construction",
        "claim_label": "CANDIDATE",
        "git_commit": "ef49b60aafd67f9007f6c218c39fd50392453a1b",
        "scope": (
            "generalized-unit closure of frozen refined branch 15 plus the "
            "exact seventh-fixed-triangle prism delta"
        ),
        "sources": {
            "base_opb": {
                "path": SOURCE_OPB_GZIP.relative_to(REPOSITORY_ROOT).as_posix(),
                "gzip_sha256": delta_builder.EXPECTED_GZIP_SHA256,
                "raw_sha256": delta_builder.EXPECTED_RAW_SHA256,
                "constraints": delta_builder.EXPECTED_CONSTRAINTS,
            },
            "delta": {
                "path": delta_builder.DELTA_RELATIVE_PATH,
                "clause_catalog_sha256": delta_builder.clause_catalog_sha256(
                    clauses
                ),
                "constraints": len(clauses),
            },
            "wave41_comparison": old_source,
        },
        "rule": (
            "For sum(unit-weight literals)>=b, if true plus unassigned equals "
            "b, every unassigned literal is forced true; if below b, the "
            "assignments contradict the constraint."
        ),
        "passes": passes,
        "derivations": derivations,
        "result": {
            "status": (
                "CANDIDATE_PROPAGATION_CONTRADICTION"
                if contradiction is not None
                else "CANDIDATE_PROPAGATION_FIXED_POINT"
            ),
            "contradiction": contradiction,
            "total_forced_variables": len(assignments),
            "forced_primary_variables": len(primary),
            "forced_auxiliary_variables": len(assignments) - len(primary),
            "positive_primary_count": sum(primary.values()),
            "negative_primary_count": len(primary) - sum(primary.values()),
            "delta_sourced_derivations": delta_derivations,
            "assignments_exactly_match_wave41_closure": assignments_match,
            "syntactically_open_combined_constraints": (
                syntactically_open_base + syntactically_open_delta
            ),
            "syntactically_open_base_constraints": syntactically_open_base,
            "syntactically_open_delta_constraints": syntactically_open_delta,
            "active_combined_constraints": active_base + active_delta,
            "active_base_constraints": active_base,
            "active_delta_constraints": active_delta,
            "wave41_open_base_plus_active_delta": (
                syntactically_open_base + active_delta
            ),
            "combined_slack_one_constraints": (
                slack_one_base + slack_one_delta
            ),
            "slack_one_base_constraints": slack_one_base,
            "slack_one_delta_constraints": slack_one_delta,
            "satisfied_closed_base_constraints": satisfied_base,
            "satisfied_closed_delta_constraints": satisfied_delta,
            "branch15": "UNKNOWN",
            "endpoint_cases_closed": 0,
        },
        "limitations": [
            "This discovery-agent certificate requires independent replay.",
            "An unchanged propagation fixed point is not a SAT witness.",
            "The delta strengthens only refined endpoint branch 15.",
            "No checked UNSAT proof or complete graph was obtained.",
            "No endpoint case, endpoint value, or global Conway claim is decided.",
        ],
    }


def load_combined_closure(
    path: Path,
) -> tuple[dict[int, bool], dict[str, object]]:
    data = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=delta_builder.no_duplicate_object_keys,
    )
    if data.get("format") != "wave42-branch15-combined-propagation-v1":
        raise ValueError("unsupported combined closure format")
    if data.get("result", {}).get("contradiction") is not None:
        raise ValueError("combined closure is contradictory")
    assignments: dict[int, bool] = {}
    for expected_index, derivation in enumerate(data.get("derivations", []), start=1):
        if derivation.get("index") != expected_index:
            raise ValueError("combined derivation order changed")
        variable = derivation.get("variable")
        value = derivation.get("value")
        if type(variable) is not int or type(value) is not bool:
            raise ValueError("malformed combined assignment")
        if variable in assignments:
            raise ValueError("combined closure assigns a variable twice")
        assignments[variable] = value
    return assignments, data


def load_wave41_probe_comparison() -> dict[tuple[int, bool], dict[str, object]]:
    data = delta_builder.load_strict_json(
        WAVE41_FAILED_LITERAL,
        EXPECTED_WAVE41_FAILED_LITERAL_SHA256,
    )
    records = data.get("records")
    if not isinstance(records, list):
        raise ValueError("Wave 41 probe records are missing")
    result: dict[tuple[int, bool], dict[str, object]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Wave 41 probe record is malformed")
        key = (record.get("variable"), record.get("assumed_value"))
        if type(key[0]) is not int or type(key[1]) is not bool:
            raise ValueError("Wave 41 probe key is malformed")
        if key in result:
            raise ValueError("Wave 41 probe key repeats")
        result[key] = record
    return result


def run_combined_probes(
    closure_path: Path,
    variables: Sequence[int] = PROBE_VARIABLES,
) -> dict[str, object]:
    clauses, _ = delta_builder.enumerate_delta_clauses()
    base_assignments, closure = load_combined_closure(closure_path)
    overlap = sorted(set(variables).intersection(base_assignments))
    if overlap:
        raise ValueError(f"probe variables are already forced: {overlap}")
    if len(variables) != len(set(variables)):
        raise ValueError("probe variables repeat")
    old_records = load_wave41_probe_comparison()

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
        scanned_base = {id(probe): 0 for probe in probes}
        scanned_delta = {id(probe): 0 for probe in probes}
        for source_kind, source_row, raw_line, constraint in iter_combined_constraints(
            clauses
        ):
            active = [probe for probe in probes if not probe.fixed]
            if not active:
                break
            row_sha256: str | None = None
            for probe in active:
                if source_kind == "base_opb":
                    scanned_base[id(probe)] += 1
                else:
                    scanned_delta[id(probe)] += 1
                status, forced = evaluate_constraint(
                    constraint,
                    probe.assignments,
                )
                if status == "CONTRADICTION":
                    if row_sha256 is None:
                        row_sha256 = sha256_bytes(raw_line)
                    probe.contradiction = {
                        "pass": pass_index,
                        "source_kind": source_kind,
                        "source_row": source_row,
                        "source_row_sha256": row_sha256,
                    }
                    probe.fixed = True
                    continue
                if status != "FORCE":
                    continue
                if row_sha256 is None:
                    row_sha256 = sha256_bytes(raw_line)
                for variable, value in forced:
                    prior = probe.assignments.get(variable)
                    if prior is not None:
                        if prior is not value:
                            probe.contradiction = {
                                "pass": pass_index,
                                "source_kind": source_kind,
                                "source_row": source_row,
                                "source_row_sha256": row_sha256,
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
                        assignment_record(
                            index=len(probe.derivations) + 1,
                            pass_index=pass_index,
                            variable=variable,
                            value=value,
                            source_kind=source_kind,
                            source_row=source_row,
                            raw_line=raw_line,
                            constraint=constraint,
                        )
                    )

        for probe in probes:
            if probe.passes and probe.fixed:
                continue
            start = starts[id(probe)]
            end = len(probe.assignments)
            probe.passes.append(
                {
                    "pass": pass_index,
                    "assignments_before": start,
                    "assignments_after": end,
                    "new_assignments": end - start,
                    "base_constraints_scanned": scanned_base[id(probe)],
                    "delta_constraints_scanned": scanned_delta[id(probe)],
                }
            )
            if not probe.fixed and end == start:
                probe.fixed = True

    records: list[dict[str, object]] = []
    candidate_implications: list[dict[str, object]] = []
    delta_changed_probes = 0
    for probe in probes:
        old_record = old_records[(probe.variable, probe.assumed_value)]
        delta_derivations = sum(
            derivation["source_kind"] == "seventh_triangle_delta"
            for derivation in probe.derivations
        )
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
        old_status = old_record.get("status")
        old_forced = old_record.get("new_forced_variables")
        changed = (
            status != old_status
            or len(probe.derivations) != old_forced
            or delta_derivations != 0
        )
        delta_changed_probes += changed
        records.append(
            {
                "variable": probe.variable,
                "assumed_value": probe.assumed_value,
                "status": status,
                "contradiction": probe.contradiction,
                "new_forced_variables": len(probe.derivations),
                "delta_sourced_derivations": delta_derivations,
                "changed_from_wave41_probe": changed,
                "passes": probe.passes,
                "derivations": probe.derivations,
            }
        )

    by_variable: dict[int, list[dict[str, object]]] = {}
    for record in records:
        by_variable.setdefault(int(record["variable"]), []).append(record)
    doubly_failed = [
        variable
        for variable, items in by_variable.items()
        if all(item["contradiction"] is not None for item in items)
    ]
    return {
        "format": "wave42-branch15-combined-failed-literal-scout-v1",
        "role": "construction",
        "claim_label": "CANDIDATE",
        "git_commit": "ef49b60aafd67f9007f6c218c39fd50392453a1b",
        "scope": (
            "bounded two-polarity generalized-unit probes on refined branch "
            "15 plus the seventh-fixed-triangle delta"
        ),
        "sources": {
            "combined_closure": {
                "path": closure_path.relative_to(REPOSITORY_ROOT).as_posix(),
                "sha256": sha256_bytes(closure_path.read_bytes()),
                "forced_variables": len(base_assignments),
            },
            "base_opb_gzip_sha256": delta_builder.EXPECTED_GZIP_SHA256,
            "delta_clause_catalog_sha256": delta_builder.clause_catalog_sha256(
                clauses
            ),
            "wave41_probe_comparison": {
                "path": WAVE41_FAILED_LITERAL.relative_to(
                    REPOSITORY_ROOT
                ).as_posix(),
                "sha256": EXPECTED_WAVE41_FAILED_LITERAL_SHA256,
            },
        },
        "probe_variables": list(variables),
        "probe_count": len(probes),
        "records": records,
        "candidate_implications": candidate_implications,
        "doubly_failed_variables": doubly_failed,
        "result": {
            "candidate_implication_count": len(candidate_implications),
            "doubly_failed_variable_count": len(doubly_failed),
            "delta_changed_probe_count": delta_changed_probes,
            "branch15_candidate_unsat_by_failed_literal": bool(doubly_failed),
            "branch15": "UNKNOWN",
            "endpoint_cases_closed": 0,
        },
        "limitations": [
            "Discovery-agent implications require independent replay.",
            "A noncontradictory propagation fixed point is not a SAT witness.",
            "Unless both polarities of one variable fail, branch 15 is not closed.",
            "Only the prior 32 high-pressure primary variables were probed.",
            "No endpoint exclusion or general upper-bound improvement is claimed.",
        ],
    }


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def verify_committed(
    closure_path: Path = DEFAULT_CLOSURE_OUTPUT,
    probe_path: Path = DEFAULT_PROBE_OUTPUT,
) -> dict[str, object]:
    expected_closure = propagate_combined()
    actual_closure = closure_path.read_bytes()
    if actual_closure != canonical_payload(expected_closure):
        raise ValueError("committed combined closure does not replay exactly")
    expected_probes = run_combined_probes(closure_path)
    actual_probes = probe_path.read_bytes()
    if actual_probes != canonical_payload(expected_probes):
        raise ValueError("committed combined probes do not replay exactly")
    return {
        "status": "PASS_EXACT_REPLAY",
        "closure_sha256": sha256_bytes(actual_closure),
        "probe_sha256": sha256_bytes(actual_probes),
        "forced_variables": expected_closure["result"][
            "total_forced_variables"
        ],
        "candidate_implications": expected_probes["result"][
            "candidate_implication_count"
        ],
        "delta_changed_probes": expected_probes["result"][
            "delta_changed_probe_count"
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--closure-output",
        type=Path,
        default=DEFAULT_CLOSURE_OUTPUT,
    )
    parser.add_argument(
        "--probe-output",
        type=Path,
        default=DEFAULT_PROBE_OUTPUT,
    )
    parser.add_argument("--skip-probes", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify:
        print(
            json.dumps(
                verify_committed(args.closure_output, args.probe_output),
                sort_keys=True,
            )
        )
        return 0

    closure = propagate_combined()
    atomic_write(args.closure_output, canonical_payload(closure))
    summary: dict[str, object] = {"closure": closure["result"]}
    if not args.skip_probes:
        probes = run_combined_probes(args.closure_output)
        atomic_write(args.probe_output, canonical_payload(probes))
        summary["probes"] = probes["result"]
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
