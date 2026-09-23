#!/usr/bin/env python3
"""Extract a checkable generalized-unit closure from one exact OPB formula.

This is a proof-producing presolve scout, not a SAT solver.  Every supported
constraint has the form

    sum(unit-weight literals) >= bound.

If the number of literals already true plus the number still unassigned is
equal to ``bound``, then every unassigned literal is forced true.  If that
maximum is below ``bound``, the current assignments are contradictory.

The default source is the frozen Wave 37 refined endpoint branch 15.  The
output binds the compressed and raw formula hashes, every source line used,
and the order of all derived assignments.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


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
EXPECTED_VARIABLES = 289_338
EXPECTED_CONSTRAINTS = 574_615
PRIMARY_VARIABLES = 3_486

HEADER_RE = re.compile(
    rb"^\* #variable= ([1-9][0-9]*) #constraint= ([1-9][0-9]*)\n$"
)
TERM_RE = re.compile(rb"\+1 (~)?x([1-9][0-9]*)")
BOUND_RE = re.compile(rb">= ([0-9]+) ;\n$")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


@dataclass(frozen=True)
class Constraint:
    literals: tuple[tuple[int, bool], ...]
    bound: int


def parse_constraint(raw_line: bytes) -> Constraint:
    bound_match = BOUND_RE.search(raw_line)
    if bound_match is None:
        raise ValueError("unsupported OPB bound syntax")
    terms = tuple(
        (int(match.group(2)), match.group(1) is None)
        for match in TERM_RE.finditer(raw_line)
    )
    if not terms:
        raise ValueError("constraint has no supported unit-weight literal")
    variables = [variable for variable, _ in terms]
    if len(variables) != len(set(variables)):
        raise ValueError("constraint repeats a variable")
    reconstructed = b" ".join(
        (
            b"+1 x" if positive else b"+1 ~x"
        )
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
    assignments: dict[int, bool],
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


def iter_formula_lines(path: Path) -> Iterable[tuple[int, bytes]]:
    with gzip.open(path, "rb") as stream:
        yield from enumerate(stream, start=1)


def inspect_source(path: Path) -> dict[str, object]:
    compressed = path.read_bytes()
    gzip_sha256 = sha256_bytes(compressed)
    if gzip_sha256 != EXPECTED_GZIP_SHA256:
        raise ValueError("source gzip SHA-256 does not match the frozen formula")
    raw_digest = hashlib.sha256()
    variables = None
    constraints = None
    observed_constraints = 0
    for line_number, raw_line in iter_formula_lines(path):
        raw_digest.update(raw_line)
        if line_number == 1:
            match = HEADER_RE.fullmatch(raw_line)
            if match is None:
                raise ValueError("unsupported OPB header")
            variables = int(match.group(1))
            constraints = int(match.group(2))
        else:
            parse_constraint(raw_line)
            observed_constraints += 1
    raw_sha256 = raw_digest.hexdigest()
    if raw_sha256 != EXPECTED_RAW_SHA256:
        raise ValueError("raw OPB SHA-256 does not match the frozen formula")
    if variables != EXPECTED_VARIABLES:
        raise ValueError("unexpected variable count")
    if constraints != EXPECTED_CONSTRAINTS:
        raise ValueError("unexpected declared constraint count")
    if observed_constraints != EXPECTED_CONSTRAINTS:
        raise ValueError("observed constraint count differs from the header")
    return {
        "path": path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
        "gzip_bytes": len(compressed),
        "gzip_sha256": gzip_sha256,
        "raw_sha256": raw_sha256,
        "variables": variables,
        "constraints": constraints,
    }


def propagate(path: Path) -> dict[str, object]:
    source = inspect_source(path)
    assignments: dict[int, bool] = {}
    derivations: list[dict[str, object]] = []
    passes: list[dict[str, int]] = []
    contradiction: dict[str, object] | None = None
    pass_index = 0

    while True:
        pass_index += 1
        start_count = len(assignments)
        constraints_scanned = 0
        for line_number, raw_line in iter_formula_lines(path):
            if line_number == 1:
                continue
            constraints_scanned += 1
            constraint = parse_constraint(raw_line)
            status, forced = evaluate_constraint(constraint, assignments)
            if status == "CONTRADICTION":
                contradiction = {
                    "pass": pass_index,
                    "source_line": line_number,
                    "source_line_sha256": sha256_bytes(raw_line),
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
                            "source_line": line_number,
                            "source_line_sha256": sha256_bytes(raw_line),
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
                    {
                        "index": len(derivations) + 1,
                        "pass": pass_index,
                        "variable": variable,
                        "value": value,
                        "source_line": line_number,
                        "source_line_sha256": sha256_bytes(raw_line),
                        "source_term_count": len(constraint.literals),
                        "source_bound": constraint.bound,
                    }
                )
            if contradiction is not None:
                break
        passes.append(
            {
                "pass": pass_index,
                "constraints_scanned": constraints_scanned,
                "assignments_before": start_count,
                "assignments_after": len(assignments),
                "new_assignments": len(assignments) - start_count,
            }
        )
        if contradiction is not None or len(assignments) == start_count:
            break

    primary = {
        variable: value
        for variable, value in assignments.items()
        if variable <= PRIMARY_VARIABLES
    }
    positive_primary = sorted(
        variable for variable, value in primary.items() if value
    )
    negative_primary = sorted(
        variable for variable, value in primary.items() if not value
    )
    return {
        "format": "wave41-generalized-unit-closure-certificate-v1",
        "role": "construction",
        "claim_label": "CANDIDATE",
        "scope": (
            "generalized-unit propagation closure of the frozen refined "
            "endpoint branch 15 formula"
        ),
        "source": source,
        "rule": (
            "For sum(unit-weight literals)>=b, if true plus unassigned equals "
            "b, every unassigned literal is forced true; if it is below b, "
            "the assignments contradict the constraint."
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
            "positive_primary_count": len(positive_primary),
            "negative_primary_count": len(negative_primary),
            "positive_primary_variables": positive_primary,
            "negative_primary_variables": negative_primary,
            "primary_variables_total": PRIMARY_VARIABLES,
            "unfixed_primary_variables": PRIMARY_VARIABLES - len(primary),
        },
        "coverage": {
            "refined_branch": 15,
            "endpoint_cases_closed": 0,
            "endpoint_cases_total": 33,
        },
        "limitations": [
            "This is a discovery-agent certificate pending independent replay.",
            "A propagation fixed point is not a SAT result.",
            "No complete endpoint case is closed unless a contradiction is independently checked.",
            "The source formula contains only the parent branch's six fixed-triangle prism families.",
            "Even an UNSAT proof for this source would close only refined branch 15.",
            "No graph, endpoint exclusion, upper-bound improvement, or novelty claim follows.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = propagate(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_payload(result))
    print(json.dumps(result["result"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
