#!/usr/bin/env python3
"""Clean-room verification of the Wave 42 branch-15 triangle delta.

This checker does not import discovery code. It replays generalized-unit
propagation from the frozen Wave 37 OPB, reconstructs the rooted 99-vertex
scaffold and residual-edge variable numbering, proves that x2 closes one
additional fixed triangle, and enumerates every prism clause based at that
triangle.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "attempts" / "wave37-proof-producing-endpoint" / "branch-15.opb.gz"
EXPECTED_GZIP_SHA256 = (
    "7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e"
)
EXPECTED_RAW_SHA256 = (
    "4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5"
)
EXPECTED_VARIABLES = 289_338
EXPECTED_CONSTRAINTS = 574_615
EXPECTED_CLOSURE_SIZE = 830
EXPECTED_RAW_COUNT = 64_932
EXPECTED_ACTIVE_COUNT = 33_778

HEADER = re.compile(
    rb"^\* #variable= ([1-9][0-9]*) #constraint= ([1-9][0-9]*)\n$"
)
TERM = re.compile(rb"\+1 (~)?x([1-9][0-9]*)")
BOUND = re.compile(rb">= ([0-9]+) ;\n$")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def strict_load(path: Path) -> dict[str, object]:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def canonical(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def parse_constraint(line: bytes) -> tuple[tuple[tuple[int, bool], ...], int]:
    bound_match = BOUND.search(line)
    if bound_match is None:
        raise ValueError("unsupported OPB bound")
    literals = tuple(
        (int(match.group(2)), match.group(1) is None)
        for match in TERM.finditer(line)
    )
    if not literals:
        raise ValueError("empty OPB constraint")
    if len({variable for variable, _ in literals}) != len(literals):
        raise ValueError("repeated variable in OPB constraint")
    rebuilt = b" ".join(
        (b"+1 x" if positive else b"+1 ~x")
        + str(variable).encode("ascii")
        for variable, positive in literals
    )
    expected = rebuilt + b" >= " + bound_match.group(1) + b" ;\n"
    if expected != line:
        raise ValueError("noncanonical or weighted OPB constraint")
    return literals, int(bound_match.group(1))


def replay_closure() -> tuple[dict[int, bool], dict[str, object]]:
    compressed = SOURCE.read_bytes()
    if sha256(compressed) != EXPECTED_GZIP_SHA256:
        raise ValueError("frozen OPB gzip hash mismatch")

    assignments: dict[int, bool] = {}
    raw_digest = hashlib.sha256()
    pass_records: list[dict[str, int]] = []
    x2_derivation: dict[str, object] | None = None
    observed_constraints = 0
    variables = constraints = None

    while True:
        before = len(assignments)
        scanned = 0
        with gzip.open(SOURCE, "rb") as stream:
            header = stream.readline()
            if not pass_records:
                raw_digest.update(header)
            match = HEADER.fullmatch(header)
            if match is None:
                raise ValueError("bad OPB header")
            variables = int(match.group(1))
            constraints = int(match.group(2))
            for line_number, line in enumerate(stream, start=2):
                if not pass_records:
                    raw_digest.update(line)
                literals, bound = parse_constraint(line)
                scanned += 1
                true_count = 0
                unassigned: list[tuple[int, bool]] = []
                for variable, positive in literals:
                    value = assignments.get(variable)
                    if value is None:
                        unassigned.append((variable, positive))
                    elif value is positive:
                        true_count += 1
                maximum = true_count + len(unassigned)
                if maximum < bound:
                    raise ValueError(f"propagation contradiction at line {line_number}")
                if unassigned and maximum == bound:
                    line_digest = sha256(line)
                    for variable, positive in unassigned:
                        prior = assignments.get(variable)
                        if prior is not None and prior is not positive:
                            raise ValueError("conflicting forced assignment")
                        if prior is None:
                            assignments[variable] = positive
                            if variable == 2:
                                x2_derivation = {
                                    "source_line": line_number,
                                    "source_line_sha256": line_digest,
                                    "source_term_count": len(literals),
                                    "source_bound": bound,
                                    "value": positive,
                                }
        observed_constraints = scanned
        pass_records.append(
            {
                "pass": len(pass_records) + 1,
                "assignments_before": before,
                "assignments_after": len(assignments),
                "new_assignments": len(assignments) - before,
                "constraints_scanned": scanned,
            }
        )
        if len(assignments) == before:
            break

    if variables != EXPECTED_VARIABLES or constraints != EXPECTED_CONSTRAINTS:
        raise ValueError("unexpected OPB header counts")
    if observed_constraints != EXPECTED_CONSTRAINTS:
        raise ValueError("unexpected observed OPB constraint count")
    if raw_digest.hexdigest() != EXPECTED_RAW_SHA256:
        raise ValueError("frozen raw OPB hash mismatch")
    if len(assignments) != EXPECTED_CLOSURE_SIZE:
        raise ValueError("generalized-unit closure size changed")
    if assignments.get(2) is not True or x2_derivation is None:
        raise ValueError("x2 is not independently forced true")
    assignment_stream = b"".join(
        f"{variable}={int(assignments[variable])}\n".encode("ascii")
        for variable in sorted(assignments)
    )
    return assignments, {
        "passes": pass_records,
        "x2_derivation": x2_derivation,
        "forced_variables": len(assignments),
        "forced_primary_variables": sum(v <= 3_486 for v in assignments),
        "positive_primary_variables": sum(
            v <= 3_486 and value for v, value in assignments.items()
        ),
        "negative_primary_variables": sum(
            v <= 3_486 and not value for v, value in assignments.items()
        ),
        "assignment_stream_sha256": sha256(assignment_stream),
    }


def rooted_scaffold() -> tuple[
    list[tuple[int, int]], dict[tuple[int, int], int]
]:
    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[1] != (pair[0] ^ 1)
    ]
    if len(labels) != 84:
        raise AssertionError("wrong residual label count")
    variables = {
        edge: index
        for index, edge in enumerate(itertools.combinations(range(84), 2), 1)
    }
    if len(variables) != 3_486:
        raise AssertionError("wrong residual edge-variable count")
    return labels, variables


def edge_status(
    first: int,
    second: int,
    labels: list[tuple[int, int]],
    variables: dict[tuple[int, int], int],
) -> bool | int:
    """Return fixed truth value or a positive residual-edge variable."""

    if first > second:
        first, second = second, first
    if first == second:
        raise ValueError("loops are not graph edges")
    if first == 0:
        return 1 <= second <= 14
    if second <= 14:
        return (second - 1) == ((first - 1) ^ 1)
    if first <= 14:
        return (first - 1) in labels[second - 15]
    return variables[(first - 15, second - 15)]


def clause_digest(clauses: Iterable[tuple[int, ...]]) -> str:
    stream = hashlib.sha256()
    for clause in sorted(clauses):
        stream.update(",".join(map(str, clause)).encode("ascii") + b"\n")
    return stream.hexdigest()


def enumerate_delta(
    assignments: dict[int, bool],
) -> tuple[set[tuple[int, ...]], set[tuple[int, ...]], dict[str, object]]:
    labels, variables = rooted_scaffold()
    triangle = (1, 15, 17)
    triangle_edges = [
        edge_status(a, b, labels, variables)
        for a, b in itertools.combinations(triangle, 2)
    ]
    if triangle_edges != [True, True, 2]:
        raise AssertionError("x2 triangle reconstruction failed")
    if assignments.get(2) is not True:
        raise ValueError("triangle-closing edge x2 is not forced")

    raw: set[tuple[int, ...]] = set()
    remaining = [vertex for vertex in range(99) if vertex not in triangle]
    for other_triangle in itertools.combinations(remaining, 3):
        internal = [
            edge_status(a, b, labels, variables)
            for a, b in itertools.combinations(other_triangle, 2)
        ]
        if any(value is False for value in internal):
            continue
        for order in itertools.permutations(other_triangle):
            required = internal + [
                edge_status(triangle[index], order[index], labels, variables)
                for index in range(3)
            ]
            if any(value is False for value in required):
                continue
            clause = tuple(
                sorted(
                    {
                        value
                        for value in required
                        if type(value) is int and value != 2
                    }
                )
            )
            if not clause:
                raise ValueError("fixed scaffold already contains a prism")
            raw.add(clause)

    active: set[tuple[int, ...]] = set()
    closure_satisfied = 0
    for clause in raw:
        if any(assignments.get(variable) is False for variable in clause):
            closure_satisfied += 1
            continue
        reduced = tuple(
            variable
            for variable in clause
            if assignments.get(variable) is not True
        )
        if not reduced:
            raise ValueError("triangle delta contradicts the closure")
        active.add(reduced)

    metadata = {
        "triangle_full_vertices_zero_based": list(triangle),
        "triangle_description": [
            "root coordinate 0",
            "residual label (0,2)",
            "residual label (0,4)",
        ],
        "triangle_closing_variable": 2,
        "raw_clause_count": len(raw),
        "raw_width_distribution": {
            str(width): count
            for width, count in sorted(Counter(map(len, raw)).items())
        },
        "raw_clause_stream_sha256": clause_digest(raw),
        "closure_satisfied_raw_clauses": closure_satisfied,
        "active_clause_count": len(active),
        "active_width_distribution": {
            str(width): count
            for width, count in sorted(Counter(map(len, active)).items())
        },
        "active_clause_stream_sha256": clause_digest(active),
        "active_unit_count": sum(len(clause) == 1 for clause in active),
        "active_empty_count": sum(len(clause) == 0 for clause in active),
        "first_active_clauses": [list(clause) for clause in sorted(active)[:10]],
        "last_active_clauses": [list(clause) for clause in sorted(active)[-10:]],
    }
    return raw, active, metadata


def compute() -> dict[str, object]:
    assignments, propagation = replay_closure()
    raw, active, delta = enumerate_delta(assignments)
    if len(raw) != EXPECTED_RAW_COUNT or len(active) != EXPECTED_ACTIVE_COUNT:
        raise ValueError("triangle-delta clause count changed")
    return {
        "format": "wave42-branch15-triangle-delta-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED_REDUCTION",
        "scope": (
            "one additional fixed-triangle prism-clause family inside refined "
            "endpoint branch 15, conditional on n3=4158"
        ),
        "source": {
            "path": "attempts/wave37-proof-producing-endpoint/branch-15.opb.gz",
            "gzip_sha256": EXPECTED_GZIP_SHA256,
            "raw_sha256": EXPECTED_RAW_SHA256,
            "variables": EXPECTED_VARIABLES,
            "constraints": EXPECTED_CONSTRAINTS,
        },
        "propagation": propagation,
        "delta": delta,
        "result": {
            "branch_15_closed": False,
            "endpoint_cases_closed": 0,
            "endpoint_cases_total": 33,
            "endpoint_n3_4158": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
        "limitations": [
            "The independently checked delta strengthens only refined branch 15.",
            "No active unit or empty clause is produced.",
            "A stronger formula is not a SAT or UNSAT certificate.",
            "The endpoint and Conway-99 remain UNKNOWN.",
        ],
    }


def validate(result: dict[str, object]) -> None:
    if result.get("claim_label") != "VERIFIED_SCOPED_REDUCTION":
        raise ValueError("wrong scoped verifier label")
    propagation = result.get("propagation")
    if not isinstance(propagation, dict):
        raise ValueError("missing propagation replay")
    if propagation.get("forced_variables") != 830:
        raise ValueError("wrong closure size")
    if propagation.get("forced_primary_variables") != 174:
        raise ValueError("wrong primary closure size")
    if propagation.get("positive_primary_variables") != 7:
        raise ValueError("wrong positive primary count")
    if propagation.get("negative_primary_variables") != 167:
        raise ValueError("wrong negative primary count")
    x2 = propagation.get("x2_derivation")
    if not isinstance(x2, dict) or x2.get("value") is not True:
        raise ValueError("x2 is not independently forced")
    delta = result.get("delta")
    if not isinstance(delta, dict):
        raise ValueError("missing delta")
    if delta.get("raw_clause_count") != EXPECTED_RAW_COUNT:
        raise ValueError("wrong raw clause count")
    if delta.get("active_clause_count") != EXPECTED_ACTIVE_COUNT:
        raise ValueError("wrong active clause count")
    if delta.get("raw_width_distribution") != {"3": 132, "5": 64_800}:
        raise ValueError("wrong raw width distribution")
    if delta.get("active_width_distribution") != {
        "3": 91,
        "4": 580,
        "5": 33_107,
    }:
        raise ValueError("wrong active width distribution")
    if delta.get("active_unit_count") != 0 or delta.get("active_empty_count") != 0:
        raise ValueError("scope inflated to a propagation or contradiction claim")
    outcome = result.get("result")
    if not isinstance(outcome, dict):
        raise ValueError("missing outcome")
    if outcome.get("branch_15_closed") is not False:
        raise ValueError("branch 15 is not closed")
    if outcome.get("endpoint_cases_closed") != 0:
        raise ValueError("no endpoint case is closed")
    if outcome.get("conway_99") != "UNKNOWN":
        raise ValueError("Conway-99 status inflation")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    observed = compute()
    validate(observed)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical(observed))
    else:
        expected = strict_load(args.verify)
        validate(expected)
        if canonical(observed) != canonical(expected):
            raise ValueError("independent replay differs from archived result")
    print(json.dumps(observed["result"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
