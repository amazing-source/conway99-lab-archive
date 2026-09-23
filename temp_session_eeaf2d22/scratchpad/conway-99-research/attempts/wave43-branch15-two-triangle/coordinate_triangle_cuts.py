#!/usr/bin/env python3
"""Enumerate exact branch-15 prism cuts with two unfixed coordinate triangles.

Every residual vertex has a frozen two-coordinate label.  For a coordinate
``c`` and two residual vertices whose labels both contain ``c``, the three
vertices form a triangle exactly when their residual edge variable is true.
This script takes every pair of such triangles whose controlling edge
variables are still unfixed after the independently checked Wave 42 closure,
requires the triangles to be vertex-disjoint, and enumerates all six perfect
matchings between them.

At the conditional endpoint ``n3=4158`` there are no triangular prisms.
Consequently, for each compatible matching, the conjunction of the two
triangle edges and the nonfixed matching edges is forbidden.  The resulting
all-negative clauses are sound individually; selecting the Wave 42-unfixed
triangle pairs is only a bounded completeness scope, not a symmetry
assumption.

The program publishes:

* the exact new unsimplified clause family;
* its exact simplification under the SHA-bound Wave 42 closure; and
* counts and hashes sufficient for an independent clean-room replay.

It is a derivation/exporter, not an UNSAT prover.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
WAVE42_ROOT = REPOSITORY_ROOT / "attempts" / "wave42-endpoint-certificate"
if str(WAVE42_ROOT) not in sys.path:
    sys.path.insert(0, str(WAVE42_ROOT))

import seventh_triangle_strengthen as wave42  # noqa: E402


SOURCE_CLOSURE = (
    WAVE42_ROOT / "branch-15-combined-propagation-certificate.json"
)
SOURCE_WAVE42_DELTA = (
    WAVE42_ROOT / "branch-15-seventh-triangle-delta.opb.gz"
)
EXPECTED_CLOSURE_SHA256 = (
    "ab05feb596c25d0fbb872a0d92978355638218350bdf7606c248ca98ae2469ce"
)
EXPECTED_WAVE42_DELTA_GZIP_SHA256 = (
    "0840524515920a59fd3d0f0666b496f9e639476dd887d0d90df5bb58a9e8904e"
)
EXPECTED_WAVE42_DELTA_RAW_SHA256 = (
    "348dc5f4bc9ee99511286a8078d0e4ef79786b57ba39ae572c032e42747be77e"
)
EXPECTED_WAVE42_DELTA_CONSTRAINTS = 64_932
RESULT_FORMAT = "wave43-branch15-two-coordinate-triangle-cuts-v1"
DEFAULT_RESULT = HERE / "branch-15-two-coordinate-triangle-result.json"
DEFAULT_DELTA = HERE / "branch-15-two-coordinate-triangle-delta.opb.gz"
DEFAULT_ACTIVE_DELTA = (
    HERE / "branch-15-two-coordinate-triangle-active-delta.opb.gz"
)
DELTA_RELATIVE_PATH = (
    "attempts/wave43-branch15-two-triangle/"
    "branch-15-two-coordinate-triangle-delta.opb.gz"
)
ACTIVE_DELTA_RELATIVE_PATH = (
    "attempts/wave43-branch15-two-triangle/"
    "branch-15-two-coordinate-triangle-active-delta.opb.gz"
)

HEADER_RE = re.compile(
    rb"^\* #variable= ([1-9][0-9]*) #constraint= ([1-9][0-9]*)\n$"
)
TERM_RE = re.compile(rb"\+1 (~)?x([1-9][0-9]*)")
BOUND_RE = re.compile(rb">= ([0-9]+) ;\n$")

Clause = tuple[int, ...]
Triangle = tuple[int, int, int, int]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def strict_json(path: Path, expected_sha256: str) -> dict[str, object]:
    payload = path.read_bytes()
    if sha256_bytes(payload) != expected_sha256:
        raise ValueError(f"{path.name} SHA-256 mismatch")
    data = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=wave42.no_duplicate_object_keys,
    )
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def load_wave42_closure() -> tuple[dict[int, bool], dict[str, object]]:
    data = strict_json(SOURCE_CLOSURE, EXPECTED_CLOSURE_SHA256)
    if data.get("format") != "wave42-branch15-combined-propagation-v1":
        raise ValueError("unsupported Wave 42 closure format")
    result = data.get("result")
    if not isinstance(result, dict) or result.get("contradiction") is not None:
        raise ValueError("Wave 42 closure is malformed or contradictory")
    if result.get("total_forced_variables") != 830:
        raise ValueError("Wave 42 forced-variable count changed")
    if result.get("forced_primary_variables") != 174:
        raise ValueError("Wave 42 forced-primary count changed")
    assignments: dict[int, bool] = {}
    derivations = data.get("derivations")
    if not isinstance(derivations, list):
        raise ValueError("Wave 42 closure derivations are missing")
    for expected_index, item in enumerate(derivations, start=1):
        if not isinstance(item, dict) or item.get("index") != expected_index:
            raise ValueError("Wave 42 derivation ordering changed")
        variable = item.get("variable")
        value = item.get("value")
        if type(variable) is not int or type(value) is not bool:
            raise ValueError("Wave 42 derivation assignment is malformed")
        if variable in assignments:
            raise ValueError("Wave 42 assigns a variable twice")
        assignments[variable] = value
    if len(assignments) != 830:
        raise ValueError("Wave 42 assignment catalogue length changed")
    return assignments, data


def coordinate_triangles(
    labels: Sequence[tuple[int, int]],
    variable_ids: Mapping[tuple[int, int], int],
) -> tuple[Triangle, ...]:
    """Return ``(anchor, residual_a, residual_b, controller)`` records."""

    records: list[Triangle] = []
    for coordinate in range(wave42.COORDINATE_COUNT):
        containing = [
            index for index, label in enumerate(labels) if coordinate in label
        ]
        if len(containing) != 12:
            raise AssertionError("coordinate fibre size changed")
        for first, second in itertools.combinations(containing, 2):
            controller = variable_ids[(first, second)]
            records.append(
                (
                    wave42.COORDINATE_OFFSET + coordinate,
                    wave42.RESIDUAL_OFFSET + first,
                    wave42.RESIDUAL_OFFSET + second,
                    controller,
                )
            )
    if len(records) != 924:
        raise AssertionError("coordinate-triangle catalogue size changed")
    if len(set(records)) != len(records):
        raise AssertionError("coordinate-triangle catalogue repeats")
    return tuple(records)


def triangle_vertices(triangle: Triangle) -> tuple[int, int, int]:
    return triangle[:3]


def pair_clause(
    labels: Sequence[tuple[int, int]],
    variable_ids: Mapping[tuple[int, int], int],
    first: Triangle,
    second_vertices: Sequence[int],
) -> Clause | None:
    first_vertices = triangle_vertices(first)
    second_tuple = tuple(second_vertices)
    required_edges = (
        tuple(itertools.combinations(first_vertices, 2))
        + tuple(itertools.combinations(second_tuple, 2))
        + tuple(zip(first_vertices, second_tuple, strict=True))
    )
    return wave42.required_positive_variables(
        labels,
        variable_ids,
        required_edges,
    )


def enumerate_two_unfixed_clauses(
    assignments: Mapping[int, bool],
) -> tuple[tuple[Clause, ...], dict[str, object], tuple[Triangle, ...]]:
    labels = wave42.rooted_labels()
    variable_ids = wave42.residual_variable_ids()
    all_triangles = coordinate_triangles(labels, variable_ids)
    eligible = tuple(
        triangle
        for triangle in all_triangles
        if triangle[3] not in assignments
    )

    forced_true = sum(
        assignments.get(triangle[3]) is True for triangle in all_triangles
    )
    forced_false = sum(
        assignments.get(triangle[3]) is False for triangle in all_triangles
    )
    if len(eligible) + forced_true + forced_false != len(all_triangles):
        raise AssertionError("triangle closure classification is incomplete")

    pair_visits = 0
    disjoint_pairs = 0
    disjoint_mate_anchor_pairs = 0
    matching_visits = 0
    killed_by_fixed_nonedge = 0
    accepted_visits = 0
    accepted_mate_anchor_visits = 0
    accepted_anchor_to_anchor_visits = 0
    clauses: set[Clause] = set()
    for first_index, first in enumerate(eligible):
        first_vertex_set = frozenset(triangle_vertices(first))
        for second in eligible[first_index + 1 :]:
            pair_visits += 1
            second_vertices = triangle_vertices(second)
            if first_vertex_set.intersection(second_vertices):
                continue
            disjoint_pairs += 1
            anchors_are_mates = (
                (first[0] - wave42.COORDINATE_OFFSET) // 2
                == (second[0] - wave42.COORDINATE_OFFSET) // 2
            )
            disjoint_mate_anchor_pairs += anchors_are_mates
            for permuted in itertools.permutations(second_vertices):
                matching_visits += 1
                clause = pair_clause(
                    labels,
                    variable_ids,
                    first,
                    permuted,
                )
                if clause is None:
                    killed_by_fixed_nonedge += 1
                    continue
                if first[3] not in clause or second[3] not in clause:
                    raise AssertionError("unfixed triangle controller disappeared")
                if len(clause) < 2:
                    raise AssertionError("two-unfixed-triangle clause is too short")
                if not anchors_are_mates:
                    raise AssertionError(
                        "a nonmate anchor pair admitted a compatible matching"
                    )
                accepted_mate_anchor_visits += 1
                if permuted[0] != second[0]:
                    raise AssertionError(
                        "a compatible matching did not pair the anchors"
                    )
                accepted_anchor_to_anchor_visits += 1
                accepted_visits += 1
                clauses.add(clause)

    ordered = tuple(sorted(clauses))
    if accepted_visits != 2 * disjoint_mate_anchor_pairs:
        raise AssertionError(
            "each mate-anchor triangle pair must admit two residual matchings"
        )
    if accepted_visits != accepted_mate_anchor_visits:
        raise AssertionError("accepted matching escaped mate-anchor classification")
    if accepted_visits != accepted_anchor_to_anchor_visits:
        raise AssertionError("accepted matching escaped anchor-pair classification")
    return ordered, {
        "all_coordinate_triangle_count": len(all_triangles),
        "wave42_forced_true_coordinate_triangles": forced_true,
        "wave42_forced_false_coordinate_triangles": forced_false,
        "wave42_unfixed_coordinate_triangles": len(eligible),
        "unordered_eligible_pair_visits": pair_visits,
        "vertex_disjoint_eligible_pairs": disjoint_pairs,
        "vertex_disjoint_mate_anchor_pairs": disjoint_mate_anchor_pairs,
        "perfect_matching_visits": matching_visits,
        "matchings_killed_by_fixed_scaffold_nonedges": killed_by_fixed_nonedge,
        "accepted_matching_visits_before_deduplication": accepted_visits,
        "accepted_matching_visits_with_mate_anchors": (
            accepted_mate_anchor_visits
        ),
        "accepted_matching_visits_pairing_the_anchors": (
            accepted_anchor_to_anchor_visits
        ),
        "distinct_clauses_before_existing_row_removal": len(ordered),
    }, eligible


def parse_negative_clause(raw_line: bytes) -> Clause | None:
    bound = BOUND_RE.search(raw_line)
    if bound is None or bound.group(1) != b"1":
        return None
    terms = tuple(TERM_RE.finditer(raw_line))
    if not terms or any(term.group(1) is None for term in terms):
        return None
    reconstructed = (
        b" ".join(b"+1 ~x" + term.group(2) for term in terms)
        + b" >= 1 ;\n"
    )
    if reconstructed != raw_line:
        raise ValueError("unsupported all-negative OPB clause syntax")
    clause = tuple(sorted(int(term.group(2)) for term in terms))
    if len(clause) != len(set(clause)):
        raise ValueError("negative OPB clause repeats a variable")
    return clause


def iter_negative_clauses(
    path: Path,
    *,
    expected_gzip_sha256: str,
    expected_raw_sha256: str,
    expected_constraints: int,
) -> Iterable[Clause]:
    compressed = path.read_bytes()
    if sha256_bytes(compressed) != expected_gzip_sha256:
        raise ValueError(f"{path.name} compressed SHA-256 mismatch")
    raw_digest = hashlib.sha256()
    observed = 0
    with gzip.open(path, "rb") as stream:
        header = stream.readline()
        raw_digest.update(header)
        match = HEADER_RE.fullmatch(header)
        if match is None:
            raise ValueError(f"{path.name} has an unsupported OPB header")
        if int(match.group(1)) != wave42.EXPECTED_VARIABLES:
            raise ValueError(f"{path.name} variable count changed")
        if int(match.group(2)) != expected_constraints:
            raise ValueError(f"{path.name} declared constraint count changed")
        for raw_line in stream:
            observed += 1
            raw_digest.update(raw_line)
            clause = parse_negative_clause(raw_line)
            if clause is not None:
                yield clause
    if observed != expected_constraints:
        raise ValueError(f"{path.name} observed constraint count changed")
    if raw_digest.hexdigest() != expected_raw_sha256:
        raise ValueError(f"{path.name} raw SHA-256 mismatch")


def simplify_clause(
    clause: Clause,
    assignments: Mapping[int, bool],
) -> tuple[str, Clause]:
    if any(assignments.get(variable) is False for variable in clause):
        return "SATISFIED", ()
    residual = tuple(
        variable
        for variable in clause
        if assignments.get(variable) is not True
    )
    if not residual:
        return "CONTRADICTION", ()
    return "ACTIVE", residual


def existing_clause_catalogues(
    assignments: Mapping[int, bool],
) -> tuple[set[Clause], set[Clause], dict[str, int]]:
    raw: set[Clause] = set()
    active: set[Clause] = set()
    base_rows = 0
    wave42_rows = 0
    for clause in iter_negative_clauses(
        wave42.SOURCE_OPB_GZIP,
        expected_gzip_sha256=wave42.EXPECTED_GZIP_SHA256,
        expected_raw_sha256=wave42.EXPECTED_RAW_SHA256,
        expected_constraints=wave42.EXPECTED_CONSTRAINTS,
    ):
        base_rows += 1
        raw.add(clause)
        state, residual = simplify_clause(clause, assignments)
        if state == "ACTIVE":
            active.add(residual)
    for clause in iter_negative_clauses(
        SOURCE_WAVE42_DELTA,
        expected_gzip_sha256=EXPECTED_WAVE42_DELTA_GZIP_SHA256,
        expected_raw_sha256=EXPECTED_WAVE42_DELTA_RAW_SHA256,
        expected_constraints=EXPECTED_WAVE42_DELTA_CONSTRAINTS,
    ):
        wave42_rows += 1
        raw.add(clause)
        state, residual = simplify_clause(clause, assignments)
        if state == "ACTIVE":
            active.add(residual)
    return raw, active, {
        "base_all_negative_rows": base_rows,
        "wave42_delta_rows": wave42_rows,
        "distinct_existing_raw_negative_clauses": len(raw),
        "distinct_existing_active_negative_clauses": len(active),
    }


def width_histogram(clauses: Sequence[Clause]) -> dict[str, int]:
    counts = Counter(map(len, clauses))
    return {str(width): counts[width] for width in sorted(counts)}


def clause_catalog_sha256(clauses: Sequence[Clause]) -> str:
    payload = json.dumps(
        [list(clause) for clause in clauses],
        separators=(",", ":"),
    ).encode("ascii")
    return sha256_bytes(payload)


def opb_payload(clauses: Sequence[Clause]) -> bytes:
    lines = [
        f"* #variable= {wave42.EXPECTED_VARIABLES} #constraint= {len(clauses)}"
    ]
    lines.extend(
        " ".join(f"+1 ~x{variable}" for variable in clause) + " >= 1 ;"
        for clause in clauses
    )
    return ("\n".join(lines) + "\n").encode("ascii")


def deterministic_gzip(payload: bytes) -> bytes:
    return gzip.compress(payload, compresslevel=9, mtime=0)


def build_artifacts() -> tuple[dict[str, object], bytes, bytes]:
    assignments, closure = load_wave42_closure()
    clauses, enumeration, eligible = enumerate_two_unfixed_clauses(assignments)
    existing_raw, existing_active, existing_counts = (
        existing_clause_catalogues(assignments)
    )

    raw_overlap = set(clauses).intersection(existing_raw)
    new_clauses = tuple(
        clause for clause in clauses if clause not in existing_raw
    )
    satisfied = 0
    contradictions = 0
    active_candidates: set[Clause] = set()
    for clause in new_clauses:
        state, residual = simplify_clause(clause, assignments)
        if state == "SATISFIED":
            satisfied += 1
        elif state == "CONTRADICTION":
            contradictions += 1
        else:
            active_candidates.add(residual)
    active_overlap = active_candidates.intersection(existing_active)
    active = tuple(sorted(active_candidates.difference(existing_active)))

    raw_payload = opb_payload(new_clauses)
    raw_gzip = deterministic_gzip(raw_payload)
    active_payload = opb_payload(active)
    active_gzip = deterministic_gzip(active_payload)

    controlling_variables = sorted({triangle[3] for triangle in eligible})
    if len(controlling_variables) != len(eligible):
        raise AssertionError("an unfixed controller belongs to two anchors")
    closure_result = closure.get("result")
    if not isinstance(closure_result, dict):
        raise AssertionError("closure result disappeared")
    result = {
        "format": RESULT_FORMAT,
        "role": "proof_b",
        "claim_label": "DERIVED",
        "git_commit": "e28f90464d00b98d37672b0b2b23dba15399a6f2",
        "scope": (
            "complete prism-cut family for vertex-disjoint pairs of "
            "coordinate-anchored triangles whose controller variables are "
            "unfixed at the SHA-bound Wave 42 branch-15 closure, conditional "
            "on n3=4158"
        ),
        "sources": {
            "base_formula": {
                "path": wave42.SOURCE_OPB_GZIP.relative_to(
                    REPOSITORY_ROOT
                ).as_posix(),
                "gzip_sha256": wave42.EXPECTED_GZIP_SHA256,
                "raw_sha256": wave42.EXPECTED_RAW_SHA256,
                "constraints": wave42.EXPECTED_CONSTRAINTS,
            },
            "wave42_seventh_triangle_delta": {
                "path": SOURCE_WAVE42_DELTA.relative_to(
                    REPOSITORY_ROOT
                ).as_posix(),
                "gzip_sha256": EXPECTED_WAVE42_DELTA_GZIP_SHA256,
                "raw_sha256": EXPECTED_WAVE42_DELTA_RAW_SHA256,
                "constraints": EXPECTED_WAVE42_DELTA_CONSTRAINTS,
            },
            "wave42_closure": {
                "path": SOURCE_CLOSURE.relative_to(REPOSITORY_ROOT).as_posix(),
                "sha256": EXPECTED_CLOSURE_SHA256,
                "forced_variables": closure_result.get(
                    "total_forced_variables"
                ),
                "forced_primary_variables": closure_result.get(
                    "forced_primary_variables"
                ),
                "contradiction": closure_result.get("contradiction"),
            },
        },
        "derivation": {
            "coordinate_triangle_rule": (
                "For coordinate c and two residual labels containing c, "
                "the coordinate-residual edges are fixed true and the "
                "residual edge variable is the sole triangle controller."
            ),
            "prism_rule": (
                "For two vertex-disjoint triangles, each of the six perfect "
                "matchings is forbidden at P=0; extra cross edges are "
                "impossible in SRG(99,14,1,2) because an adjacent pair has "
                "exactly one common neighbor."
            ),
            "compatibility_classification": (
                "A compatible matching exists exactly when the coordinate "
                "anchors are scaffold mates and are matched to each other. "
                "For nonmate anchors, reciprocal coordinate-residual "
                "adjacency would require the same residual label {c,d} in "
                "both disjoint triangles. For mate anchors, that label is "
                "excluded from the rooted residual catalogue, so the anchors "
                "must match; the remaining two residual pairs are variable."
            ),
            "four_variable_cut_form": (
                "not(controller_left AND controller_right AND "
                "cross_edge_1 AND cross_edge_2)"
            ),
            "selection_rule": (
                "both triangle-controller variables are absent from the "
                "Wave 42 closure assignment catalogue"
            ),
            "completed_graph_automorphism_assumed": False,
            "individual_clause_soundness_depends_on_selection_rule": False,
            "controlling_variable_count": len(controlling_variables),
            "controlling_variable_catalog_sha256": sha256_bytes(
                json.dumps(
                    controlling_variables,
                    separators=(",", ":"),
                ).encode("ascii")
            ),
        },
        "enumeration": enumeration,
        "existing_rows": {
            **existing_counts,
            "exact_raw_overlap_count": len(raw_overlap),
            "exact_active_overlap_count": len(active_overlap),
        },
        "delta": {
            "path": DELTA_RELATIVE_PATH,
            "constraints": len(new_clauses),
            "width_histogram": width_histogram(new_clauses),
            "clause_catalog_sha256": clause_catalog_sha256(new_clauses),
            "raw_bytes": len(raw_payload),
            "raw_sha256": sha256_bytes(raw_payload),
            "gzip_bytes": len(raw_gzip),
            "gzip_sha256": sha256_bytes(raw_gzip),
            "serialization": (
                "canonical sorted all-negative OPB rows and deterministic "
                "gzip with mtime zero"
            ),
        },
        "wave42_closure_simplification": {
            "satisfied_new_raw_clauses": satisfied,
            "empty_residual_contradictions": contradictions,
            "distinct_active_candidates_before_existing_row_removal": len(
                active_candidates
            ),
            "existing_active_exact_row_overlap": len(active_overlap),
            "new_active_constraints": len(active),
            "active_width_histogram": width_histogram(active),
            "immediate_negative_units": sum(
                len(clause) == 1 for clause in active
            ),
            "active_clause_catalog_sha256": clause_catalog_sha256(active),
            "active_catalog": {
                "path": ACTIVE_DELTA_RELATIVE_PATH,
                "constraints": len(active),
                "raw_bytes": len(active_payload),
                "raw_sha256": sha256_bytes(active_payload),
                "gzip_bytes": len(active_gzip),
                "gzip_sha256": sha256_bytes(active_gzip),
            },
        },
        "result": {
            "status": (
                "CANDIDATE_PROPAGATION_CONTRADICTION"
                if contradictions
                else "CANDIDATE_STRONGER_REDUCTION"
            ),
            "immediate_contradiction": bool(contradictions),
            "immediate_new_units": sum(len(clause) == 1 for clause in active),
            "branch15_sat": "UNKNOWN",
            "branch15_unsat": "UNKNOWN",
            "endpoint_cases_closed": 0,
            "endpoint_cases_total": 33,
        },
        "limitations": [
            "This proof-agent derivation requires independent clean-room replay.",
            "The completeness scope covers only pairs of coordinate-anchored triangles that are unfixed at the frozen Wave 42 closure.",
            "Prisms involving a triangle without a coordinate anchor remain omitted.",
            "A propagation fixed point is neither a SAT witness nor an UNSAT certificate.",
            "No branch closure counts unless an UNSAT proof is retained and independently checked.",
            "No endpoint exclusion, strict upper bound, graph, or Conway-99 resolution follows from this export alone.",
        ],
    }
    return result, raw_gzip, active_gzip


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
    result_path: Path = DEFAULT_RESULT,
    delta_path: Path = DEFAULT_DELTA,
    active_path: Path = DEFAULT_ACTIVE_DELTA,
) -> dict[str, object]:
    expected, expected_delta, expected_active = build_artifacts()
    if result_path.read_bytes() != canonical_payload(expected):
        raise ValueError("committed result differs from exact regeneration")
    if delta_path.read_bytes() != expected_delta:
        raise ValueError("committed delta differs from exact regeneration")
    if active_path.read_bytes() != expected_active:
        raise ValueError("committed active delta differs from exact regeneration")
    return {
        "status": "PASS_EXACT_REPLAY",
        "result_sha256": sha256_bytes(result_path.read_bytes()),
        "delta_gzip_sha256": sha256_bytes(delta_path.read_bytes()),
        "active_delta_gzip_sha256": sha256_bytes(active_path.read_bytes()),
        "constraints": expected["delta"]["constraints"],
        "active_constraints": expected["wave42_closure_simplification"][
            "new_active_constraints"
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--delta", type=Path, default=DEFAULT_DELTA)
    parser.add_argument(
        "--active-delta",
        type=Path,
        default=DEFAULT_ACTIVE_DELTA,
    )
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify:
        print(
            json.dumps(
                verify_committed(args.result, args.delta, args.active_delta),
                sort_keys=True,
            )
        )
        return 0

    result, delta, active = build_artifacts()
    atomic_write(args.delta, delta)
    atomic_write(args.active_delta, active)
    atomic_write(args.result, canonical_payload(result))
    print(json.dumps(result["result"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
