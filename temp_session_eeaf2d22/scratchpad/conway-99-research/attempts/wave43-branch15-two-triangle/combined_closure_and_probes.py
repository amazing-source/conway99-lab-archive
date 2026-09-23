#!/usr/bin/env python3
"""Extend Wave 42 closure and run bounded probes with two-triangle cuts.

The exact fixed-point extension is cheap: every newly active coordinate-pair
cut has four unassigned negative literals at the Wave 42 closure, so none is a
generalized unit.  The script nevertheless parses every retained row and
records the complete state histogram.

For a bounded attempt to extract more information, it then selects the 32
unfixed coordinate-triangle controller variables with highest incidence in
the active cut family and replays both polarities through the complete frozen
Wave 37 OPB, the Wave 42 seventh-triangle delta, and the new raw cut family.
Contradictions would be retained with row-addressed derivations, but are still
only discovery claims pending independent proof checking.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
WAVE42_ROOT = REPOSITORY_ROOT / "attempts" / "wave42-endpoint-certificate"
for import_root in (HERE, WAVE42_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import coordinate_triangle_cuts as cuts  # noqa: E402
import combined_propagation as wave42_propagation  # noqa: E402
import seventh_triangle_strengthen as wave42  # noqa: E402


SOURCE_RESULT = HERE / "branch-15-two-coordinate-triangle-result.json"
SOURCE_DELTA = HERE / "branch-15-two-coordinate-triangle-delta.opb.gz"
SOURCE_ACTIVE_DELTA = (
    HERE / "branch-15-two-coordinate-triangle-active-delta.opb.gz"
)
EXPECTED_RESULT_SHA256 = (
    "1ab1cc6ad5a3727fec508b8b3f2eb9b52d4034f6aa6768b25feef8f219c45ec8"
)
EXPECTED_DELTA_GZIP_SHA256 = (
    "82a13e78e514cf35f27190da665bdedaf4fed28c7a6fa2856e22badf63f32797"
)
EXPECTED_DELTA_RAW_SHA256 = (
    "23fc3b22b4b235cc631bfd0b53ed2806394273aa1b4c691c883ebe343788d3f1"
)
EXPECTED_DELTA_CONSTRAINTS = 40_800
EXPECTED_ACTIVE_GZIP_SHA256 = (
    "858f2a5c66d251497e4c13fb4d633c18fe65afe657937b84444cde55b1a4a631"
)
EXPECTED_ACTIVE_RAW_SHA256 = (
    "0ed3c553d6323632b0466157f0eb7e18cb7597a16ce8eca6654d086c70314476"
)
EXPECTED_ACTIVE_CONSTRAINTS = 34_340
DEFAULT_CLOSURE = HERE / "branch-15-two-coordinate-triangle-closure.json"
DEFAULT_PROBES = HERE / "branch-15-two-coordinate-triangle-probes.json"
PROBE_VARIABLE_COUNT = 32


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_result() -> dict[str, object]:
    result = cuts.strict_json(SOURCE_RESULT, EXPECTED_RESULT_SHA256)
    if result.get("format") != cuts.RESULT_FORMAT:
        raise ValueError("unsupported coordinate-cut result format")
    return result


def load_clauses(
    path: Path,
    *,
    expected_gzip_sha256: str,
    expected_raw_sha256: str,
    expected_constraints: int,
) -> tuple[cuts.Clause, ...]:
    return tuple(
        cuts.iter_negative_clauses(
            path,
            expected_gzip_sha256=expected_gzip_sha256,
            expected_raw_sha256=expected_raw_sha256,
            expected_constraints=expected_constraints,
        )
    )


def exact_closure_extension() -> dict[str, object]:
    result = load_result()
    assignments, wave42_closure = cuts.load_wave42_closure()
    raw_clauses = load_clauses(
        SOURCE_DELTA,
        expected_gzip_sha256=EXPECTED_DELTA_GZIP_SHA256,
        expected_raw_sha256=EXPECTED_DELTA_RAW_SHA256,
        expected_constraints=EXPECTED_DELTA_CONSTRAINTS,
    )
    active_clauses = load_clauses(
        SOURCE_ACTIVE_DELTA,
        expected_gzip_sha256=EXPECTED_ACTIVE_GZIP_SHA256,
        expected_raw_sha256=EXPECTED_ACTIVE_RAW_SHA256,
        expected_constraints=EXPECTED_ACTIVE_CONSTRAINTS,
    )

    raw_states: Counter[str] = Counter()
    raw_residual_widths: Counter[int] = Counter()
    for clause in raw_clauses:
        state, residual = cuts.simplify_clause(clause, assignments)
        raw_states[state] += 1
        if state == "ACTIVE":
            raw_residual_widths[len(residual)] += 1

    active_states: Counter[str] = Counter()
    active_slacks: Counter[int] = Counter()
    active_catalog: set[cuts.Clause] = set()
    for clause in active_clauses:
        state, residual = cuts.simplify_clause(clause, assignments)
        active_states[state] += 1
        if state != "ACTIVE" or residual != clause:
            raise ValueError("retained active delta is not closure-normalized")
        active_slacks[len(residual) - 1] += 1
        active_catalog.add(clause)
    if len(active_catalog) != len(active_clauses):
        raise ValueError("active delta repeats a clause")
    if active_states != Counter({"ACTIVE": EXPECTED_ACTIVE_CONSTRAINTS}):
        raise ValueError("active delta state histogram changed")
    if active_slacks.get(0, 0):
        raise ValueError("new active delta contains a generalized unit")

    wave42_result = wave42_closure.get("result")
    if not isinstance(wave42_result, dict):
        raise ValueError("Wave 42 closure result is missing")
    result_summary = result.get("result")
    if not isinstance(result_summary, dict):
        raise ValueError("coordinate-cut result summary is missing")
    return {
        "format": "wave43-branch15-two-coordinate-triangle-closure-v1",
        "role": "proof_b",
        "claim_label": "DERIVED",
        "git_commit": "e28f90464d00b98d37672b0b2b23dba15399a6f2",
        "scope": (
            "exact generalized-unit fixed-point extension for branch 15 "
            "after adding the two-unfixed-coordinate-triangle prism cuts"
        ),
        "sources": {
            "wave42_closure": {
                "path": cuts.SOURCE_CLOSURE.relative_to(
                    REPOSITORY_ROOT
                ).as_posix(),
                "sha256": cuts.EXPECTED_CLOSURE_SHA256,
                "forced_variables": len(assignments),
            },
            "cut_result": {
                "path": SOURCE_RESULT.relative_to(REPOSITORY_ROOT).as_posix(),
                "sha256": EXPECTED_RESULT_SHA256,
            },
            "raw_delta": {
                "path": SOURCE_DELTA.relative_to(REPOSITORY_ROOT).as_posix(),
                "gzip_sha256": EXPECTED_DELTA_GZIP_SHA256,
                "raw_sha256": EXPECTED_DELTA_RAW_SHA256,
                "constraints": len(raw_clauses),
            },
            "active_delta": {
                "path": SOURCE_ACTIVE_DELTA.relative_to(
                    REPOSITORY_ROOT
                ).as_posix(),
                "gzip_sha256": EXPECTED_ACTIVE_GZIP_SHA256,
                "raw_sha256": EXPECTED_ACTIVE_RAW_SHA256,
                "constraints": len(active_clauses),
            },
        },
        "rule": (
            "For a unit-weight inequality sum(literals)>=b, contradiction "
            "occurs when true plus unassigned is below b; all unassigned "
            "literals are forced true exactly when true plus unassigned "
            "equals b."
        ),
        "audit": {
            "raw_state_histogram": dict(sorted(raw_states.items())),
            "raw_active_residual_width_histogram": {
                str(width): count
                for width, count in sorted(raw_residual_widths.items())
            },
            "active_state_histogram": dict(sorted(active_states.items())),
            "active_slack_histogram": {
                str(slack): count
                for slack, count in sorted(active_slacks.items())
            },
            "distinct_active_rows": len(active_catalog),
        },
        "result": {
            "status": "DERIVED_PROPAGATION_FIXED_POINT",
            "contradiction": None,
            "new_forced_variables": 0,
            "total_forced_variables": len(assignments),
            "forced_primary_variables": wave42_result.get(
                "forced_primary_variables"
            ),
            "assignments_exactly_wave42_closure": True,
            "branch15": "UNKNOWN",
            "endpoint_cases_closed": 0,
        },
        "argument": (
            "The SHA-bound Wave 42 assignment is already a fixed point for "
            "the base OPB plus seventh-triangle delta. Every new active row "
            "has slack three at exactly that assignment. Therefore no old "
            "or new row is contradictory or forcing, so the same assignment "
            "is the exact generalized-unit fixed point of the union."
        ),
        "limitations": [
            "The Wave 42 closure is an input and must be replayed independently.",
            "A noncontradictory propagation fixed point is not a SAT witness.",
            "No UNSAT proof, branch exclusion, or endpoint exclusion is claimed.",
        ],
    }


def raw_coordinate_constraint_line(clause: Sequence[int]) -> bytes:
    return (
        " ".join(f"+1 ~x{variable}" for variable in clause) + " >= 1 ;\n"
    ).encode("ascii")


def iter_full_constraints(
    wave42_clauses: Sequence[cuts.Clause],
    coordinate_clauses: Sequence[cuts.Clause],
) -> Iterable[
    tuple[str, int, bytes, wave42_propagation.Constraint]
]:
    yield from wave42_propagation.iter_combined_constraints(wave42_clauses)
    for row_number, clause in enumerate(coordinate_clauses, start=1):
        raw_line = raw_coordinate_constraint_line(clause)
        yield (
            "two_coordinate_triangle_delta",
            row_number,
            raw_line,
            wave42_propagation.Constraint(
                tuple((variable, False) for variable in clause),
                1,
            ),
        )


def select_probe_variables(
    active_clauses: Sequence[cuts.Clause],
    assignments: dict[int, bool],
) -> tuple[tuple[int, ...], list[dict[str, int]]]:
    labels = wave42.rooted_labels()
    variable_ids = wave42.residual_variable_ids()
    controllers = {
        triangle[3]
        for triangle in cuts.coordinate_triangles(labels, variable_ids)
        if triangle[3] not in assignments
    }
    incidence = Counter(
        variable
        for clause in active_clauses
        for variable in clause
        if variable in controllers
    )
    ordered = tuple(
        variable
        for variable, _ in sorted(
            incidence.items(),
            key=lambda item: (-item[1], item[0]),
        )[:PROBE_VARIABLE_COUNT]
    )
    if len(ordered) != PROBE_VARIABLE_COUNT:
        raise ValueError("too few unfixed coordinate controllers to probe")
    return ordered, [
        {"variable": variable, "active_cut_occurrences": incidence[variable]}
        for variable in ordered
    ]


def run_bounded_probes() -> dict[str, object]:
    load_result()
    base_assignments, _ = cuts.load_wave42_closure()
    coordinate_clauses = load_clauses(
        SOURCE_DELTA,
        expected_gzip_sha256=EXPECTED_DELTA_GZIP_SHA256,
        expected_raw_sha256=EXPECTED_DELTA_RAW_SHA256,
        expected_constraints=EXPECTED_DELTA_CONSTRAINTS,
    )
    active_clauses = load_clauses(
        SOURCE_ACTIVE_DELTA,
        expected_gzip_sha256=EXPECTED_ACTIVE_GZIP_SHA256,
        expected_raw_sha256=EXPECTED_ACTIVE_RAW_SHA256,
        expected_constraints=EXPECTED_ACTIVE_CONSTRAINTS,
    )
    wave42_clauses, _ = wave42.enumerate_delta_clauses()
    probe_variables, selection = select_probe_variables(
        active_clauses,
        base_assignments,
    )
    probes = [
        wave42_propagation.Probe(
            variable=variable,
            assumed_value=value,
            assignments={**base_assignments, variable: value},
        )
        for variable in probe_variables
        for value in (False, True)
    ]

    pass_index = 0
    while any(not probe.fixed for probe in probes):
        pass_index += 1
        starts = {id(probe): len(probe.assignments) for probe in probes}
        scanned = {
            id(probe): {
                "base": 0,
                "wave42": 0,
                "coordinate": 0,
            }
            for probe in probes
        }
        for source_kind, source_row, raw_line, constraint in (
            iter_full_constraints(wave42_clauses, coordinate_clauses)
        ):
            active_probes = [probe for probe in probes if not probe.fixed]
            if not active_probes:
                break
            row_digest: str | None = None
            for probe in active_probes:
                if source_kind == "base_opb":
                    scanned[id(probe)]["base"] += 1
                elif source_kind == "seventh_triangle_delta":
                    scanned[id(probe)]["wave42"] += 1
                else:
                    scanned[id(probe)]["coordinate"] += 1
                status, forced = wave42_propagation.evaluate_constraint(
                    constraint,
                    probe.assignments,
                )
                if status == "CONTRADICTION":
                    if row_digest is None:
                        row_digest = sha256_bytes(raw_line)
                    probe.contradiction = {
                        "pass": pass_index,
                        "source_kind": source_kind,
                        "source_row": source_row,
                        "source_row_sha256": row_digest,
                    }
                    probe.fixed = True
                    continue
                if status != "FORCE":
                    continue
                if row_digest is None:
                    row_digest = sha256_bytes(raw_line)
                for variable, value in forced:
                    prior = probe.assignments.get(variable)
                    if prior is not None:
                        if prior is not value:
                            probe.contradiction = {
                                "pass": pass_index,
                                "source_kind": source_kind,
                                "source_row": source_row,
                                "source_row_sha256": row_digest,
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
                        wave42_propagation.assignment_record(
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
                    "base_constraints_scanned": scanned[id(probe)]["base"],
                    "wave42_constraints_scanned": scanned[id(probe)]["wave42"],
                    "coordinate_constraints_scanned": scanned[id(probe)][
                        "coordinate"
                    ],
                }
            )
            if not probe.fixed and end == start:
                probe.fixed = True

    records: list[dict[str, object]] = []
    candidate_implications: list[dict[str, object]] = []
    for probe in probes:
        coordinate_derivations = sum(
            derivation["source_kind"] == "two_coordinate_triangle_delta"
            for derivation in probe.derivations
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
                "status": (
                    "CANDIDATE_CONTRADICTION"
                    if probe.contradiction is not None
                    else "PROPAGATION_FIXED_POINT_NO_CONCLUSION"
                ),
                "contradiction": probe.contradiction,
                "new_forced_variables": len(probe.derivations),
                "coordinate_delta_sourced_derivations": (
                    coordinate_derivations
                ),
                "passes": probe.passes,
                "derivations": probe.derivations,
            }
        )

    by_variable: dict[int, list[dict[str, object]]] = {}
    for record in records:
        by_variable.setdefault(int(record["variable"]), []).append(record)
    doubly_failed = [
        variable
        for variable, pair in by_variable.items()
        if all(item["contradiction"] is not None for item in pair)
    ]
    return {
        "format": "wave43-branch15-two-coordinate-triangle-probes-v1",
        "role": "proof_b",
        "claim_label": "CANDIDATE",
        "git_commit": "e28f90464d00b98d37672b0b2b23dba15399a6f2",
        "scope": (
            "both-polarity generalized-unit probes for the 32 highest-"
            "incidence unfixed coordinate-triangle controllers in branch 15"
        ),
        "sources": {
            "base_formula_gzip_sha256": wave42.EXPECTED_GZIP_SHA256,
            "wave42_delta_gzip_sha256": (
                cuts.EXPECTED_WAVE42_DELTA_GZIP_SHA256
            ),
            "wave42_closure_sha256": cuts.EXPECTED_CLOSURE_SHA256,
            "coordinate_delta_gzip_sha256": (
                EXPECTED_DELTA_GZIP_SHA256
            ),
            "coordinate_active_delta_gzip_sha256": (
                EXPECTED_ACTIVE_GZIP_SHA256
            ),
        },
        "selection": selection,
        "probe_variables": list(probe_variables),
        "probe_count": len(probes),
        "records": records,
        "candidate_implications": candidate_implications,
        "doubly_failed_variables": doubly_failed,
        "result": {
            "candidate_implication_count": len(candidate_implications),
            "doubly_failed_variable_count": len(doubly_failed),
            "probes_with_coordinate_delta_derivations": sum(
                record["coordinate_delta_sourced_derivations"] > 0
                for record in records
            ),
            "total_coordinate_delta_derivations": sum(
                int(record["coordinate_delta_sourced_derivations"])
                for record in records
            ),
            "branch15_candidate_unsat_by_failed_literal": bool(doubly_failed),
            "branch15": "UNKNOWN",
            "endpoint_cases_closed": 0,
        },
        "limitations": [
            "Only 32 deterministically selected controller variables were probed.",
            "A noncontradictory fixed point is not a SAT witness.",
            "Any candidate contradiction requires independent proof replay.",
            "Propagation closure alone is not promoted as branch UNSAT.",
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
    closure_path: Path = DEFAULT_CLOSURE,
    probe_path: Path = DEFAULT_PROBES,
) -> dict[str, object]:
    expected_closure = exact_closure_extension()
    if closure_path.read_bytes() != canonical_payload(expected_closure):
        raise ValueError("committed closure differs from exact regeneration")
    expected_probes = run_bounded_probes()
    if probe_path.read_bytes() != canonical_payload(expected_probes):
        raise ValueError("committed probes differ from exact regeneration")
    return {
        "status": "PASS_EXACT_REPLAY",
        "closure_sha256": sha256_bytes(closure_path.read_bytes()),
        "probe_sha256": sha256_bytes(probe_path.read_bytes()),
        "new_forced_variables": expected_closure["result"][
            "new_forced_variables"
        ],
        "candidate_implications": expected_probes["result"][
            "candidate_implication_count"
        ],
        "coordinate_delta_derivations": expected_probes["result"][
            "total_coordinate_delta_derivations"
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closure", type=Path, default=DEFAULT_CLOSURE)
    parser.add_argument("--probes", type=Path, default=DEFAULT_PROBES)
    parser.add_argument("--skip-probes", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify:
        print(
            json.dumps(
                verify_committed(args.closure, args.probes),
                sort_keys=True,
            )
        )
        return 0

    closure = exact_closure_extension()
    atomic_write(args.closure, canonical_payload(closure))
    summary: dict[str, object] = {"closure": closure["result"]}
    if not args.skip_probes:
        probes = run_bounded_probes()
        atomic_write(args.probes, canonical_payload(probes))
        summary["probes"] = probes["result"]
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
