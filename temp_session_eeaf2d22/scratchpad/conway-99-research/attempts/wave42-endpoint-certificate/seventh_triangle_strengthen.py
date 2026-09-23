#!/usr/bin/env python3
"""Derive the missing seventh fixed-triangle prism family for branch 15.

Wave 37 adds prism clauses for the six triangles fixed by parent branch 4.
Refined branch 15 additionally fixes residual edge ``x2``.  In the canonical
root labels this edge is ``(0,2)--(0,4)``, so it creates the seventh triangle
on full vertices ``(1,15,17)`` through coordinate 0.

This program independently reconstructs the rooted labels and primary edge
numbering, enumerates every prism clause implied by that triangle, proves the
clauses are absent as exact rows from the frozen branch-15 OPB, and publishes
a deterministic compressed OPB delta.  It also reports the diagnostic
simplification under the Wave 41 generalized-unit closure.  The latter is not
needed for soundness of the unsimplified delta.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_OPB_GZIP = (
    REPOSITORY_ROOT
    / "attempts"
    / "wave37-proof-producing-endpoint"
    / "branch-15.opb.gz"
)
SOURCE_METADATA = SOURCE_OPB_GZIP.with_name("branch-15-formula.json")
SOURCE_CLOSURE = (
    REPOSITORY_ROOT
    / "attempts"
    / "wave41-proof-producing-search"
    / "branch-15-propagation-certificate.json"
)
DEFAULT_OUTPUT = Path(__file__).with_name("branch-15-seventh-triangle-result.json")
DEFAULT_DELTA = Path(__file__).with_name("branch-15-seventh-triangle-delta.opb.gz")
DEFAULT_ACTIVE_DELTA = Path(__file__).with_name(
    "branch-15-seventh-triangle-active-delta.opb.gz"
)

EXPECTED_GZIP_SHA256 = (
    "7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e"
)
EXPECTED_RAW_SHA256 = (
    "4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5"
)
EXPECTED_METADATA_SHA256 = (
    "3a6d4181445a2bdd7859faa0b493376891b4498eb0987989dcdcdc4b8ffe97d6"
)
EXPECTED_CLOSURE_SHA256 = (
    "3da90e49e4e9469bdc397af107d877ee7075ad551a6f8df1afbd8d5d1150707f"
)
EXPECTED_VARIABLES = 289_338
EXPECTED_CONSTRAINTS = 574_615
PRIMARY_VARIABLES = 3_486
COORDINATE_COUNT = 14
RESIDUAL_COUNT = 84
FULL_VERTEX_COUNT = 99
ROOT_VERTEX = 0
COORDINATE_OFFSET = 1
RESIDUAL_OFFSET = 15
REFINEMENT_VARIABLE = 2
REFINEMENT_EDGE = (0, 2)
REFINEMENT_TRIANGLE = (1, 15, 17)
REFINEMENT_UNIT_LINE = 286_004
REFINEMENT_UNIT_SHA256 = (
    "dbe041511085ba55c17be80495ef443dbbe3d3eee2ce42e1f07865d8041d7da5"
)
RESULT_FORMAT = "wave42-branch15-seventh-triangle-strengthening-v1"
DELTA_RELATIVE_PATH = (
    "attempts/wave42-endpoint-certificate/"
    "branch-15-seventh-triangle-delta.opb.gz"
)
ACTIVE_DELTA_RELATIVE_PATH = (
    "attempts/wave42-endpoint-certificate/"
    "branch-15-seventh-triangle-active-delta.opb.gz"
)

HEADER_RE = re.compile(
    rb"^\* #variable= ([1-9][0-9]*) #constraint= ([1-9][0-9]*)\n$"
)
TERM_RE = re.compile(rb"\+1 (~)?x([1-9][0-9]*)")
BOUND_RE = re.compile(rb">= ([0-9]+) ;\n$")

VariableEdge = tuple[int, int]
Clause = tuple[int, ...]
EdgeState = bool | VariableEdge


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def no_duplicate_object_keys(
    pairs: Sequence[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_strict_json(path: Path, expected_sha256: str) -> dict[str, object]:
    payload = path.read_bytes()
    if sha256_bytes(payload) != expected_sha256:
        raise ValueError(f"{path.name} SHA-256 does not match the frozen input")
    data = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=no_duplicate_object_keys,
    )
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def rooted_labels() -> tuple[tuple[int, int], ...]:
    labels = tuple(
        (first, second)
        for first, second in itertools.combinations(range(COORDINATE_COUNT), 2)
        if first // 2 != second // 2
    )
    if len(labels) != RESIDUAL_COUNT:
        raise AssertionError("rooted residual label count changed")
    return labels


def residual_variable_ids() -> dict[VariableEdge, int]:
    result = {
        edge: variable
        for variable, edge in enumerate(
            itertools.combinations(range(RESIDUAL_COUNT), 2),
            start=1,
        )
    }
    if len(result) != PRIMARY_VARIABLES:
        raise AssertionError("primary edge-variable count changed")
    return result


def canonical_edge(first: int, second: int) -> tuple[int, int]:
    if first == second:
        raise ValueError("loops are not graph edges")
    return (first, second) if first < second else (second, first)


def rooted_edge_state(
    labels: Sequence[tuple[int, int]],
    first: int,
    second: int,
) -> EdgeState:
    first, second = canonical_edge(first, second)
    if not 0 <= first < second < FULL_VERTEX_COUNT:
        raise ValueError("full edge endpoint is outside 0..98")

    if first == ROOT_VERTEX:
        return COORDINATE_OFFSET <= second < RESIDUAL_OFFSET

    if first < RESIDUAL_OFFSET and second < RESIDUAL_OFFSET:
        left = first - COORDINATE_OFFSET
        right = second - COORDINATE_OFFSET
        return left // 2 == right // 2 and left != right

    if first < RESIDUAL_OFFSET:
        coordinate = first - COORDINATE_OFFSET
        label = labels[second - RESIDUAL_OFFSET]
        return coordinate in label

    return (
        first - RESIDUAL_OFFSET,
        second - RESIDUAL_OFFSET,
    )


def possible_neighbors(
    labels: Sequence[tuple[int, int]],
    vertex: int,
    excluded: frozenset[int],
) -> tuple[int, ...]:
    return tuple(
        other
        for other in range(FULL_VERTEX_COUNT)
        if other != vertex
        and other not in excluded
        and rooted_edge_state(labels, vertex, other) is not False
    )


def required_positive_variables(
    labels: Sequence[tuple[int, int]],
    variable_ids: Mapping[VariableEdge, int],
    edges: Iterable[tuple[int, int]],
) -> Clause | None:
    variables: set[int] = set()
    for first, second in edges:
        state = rooted_edge_state(labels, first, second)
        if state is False:
            return None
        if state is not True:
            variables.add(variable_ids[state])
    if not variables:
        raise AssertionError("the rooted scaffold already contains a prism")
    return tuple(sorted(variables))


def enumerate_delta_clauses() -> tuple[tuple[Clause, ...], dict[str, object]]:
    labels = rooted_labels()
    variable_ids = residual_variable_ids()
    if variable_ids[REFINEMENT_EDGE] != REFINEMENT_VARIABLE:
        raise AssertionError("refinement edge no longer maps to x2")
    if labels[REFINEMENT_EDGE[0]] != (0, 2):
        raise AssertionError("first refinement endpoint label changed")
    if labels[REFINEMENT_EDGE[1]] != (0, 4):
        raise AssertionError("second refinement endpoint label changed")

    states = tuple(
        rooted_edge_state(labels, first, second)
        for first, second in itertools.combinations(REFINEMENT_TRIANGLE, 2)
    )
    if states != (True, True, REFINEMENT_EDGE):
        raise AssertionError("refinement triangle derivation changed")

    excluded = frozenset(REFINEMENT_TRIANGLE)
    neighbor_lists = tuple(
        possible_neighbors(labels, vertex, excluded)
        for vertex in REFINEMENT_TRIANGLE
    )
    raw_clause_visits = 0
    repeated_matched_vertices = 0
    impossible_patterns = 0
    clauses: set[Clause] = set()
    for matched in itertools.product(*neighbor_lists):
        raw_clause_visits += 1
        if len(set(matched)) != 3:
            repeated_matched_vertices += 1
            continue
        required_edges = tuple(
            (REFINEMENT_TRIANGLE[index], matched[index])
            for index in range(3)
        ) + tuple(itertools.combinations(matched, 2))
        variables = required_positive_variables(
            labels,
            variable_ids,
            required_edges,
        )
        if variables is None:
            impossible_patterns += 1
            continue
        clauses.add(variables)

    ordered = tuple(sorted(clauses))
    return ordered, {
        "neighbor_list_sizes": [len(items) for items in neighbor_lists],
        "matched_vertex_products_visited": raw_clause_visits,
        "products_with_repeated_matched_vertices": repeated_matched_vertices,
        "patterns_killed_by_fixed_scaffold_nonedges": impossible_patterns,
        "accepted_pattern_visits_before_deduplication": (
            raw_clause_visits
            - repeated_matched_vertices
            - impossible_patterns
        ),
    }


def inspect_source(
    clauses: Sequence[Clause],
) -> tuple[dict[str, object], set[Clause]]:
    compressed = SOURCE_OPB_GZIP.read_bytes()
    if sha256_bytes(compressed) != EXPECTED_GZIP_SHA256:
        raise ValueError("source gzip SHA-256 mismatch")

    raw_digest = hashlib.sha256()
    declared_variables: int | None = None
    declared_constraints: int | None = None
    observed_constraints = 0
    refinement_unit_matches: list[dict[str, object]] = []
    existing_negative_clauses: set[Clause] = set()
    with gzip.open(SOURCE_OPB_GZIP, "rb") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            raw_digest.update(raw_line)
            if line_number == 1:
                match = HEADER_RE.fullmatch(raw_line)
                if match is None:
                    raise ValueError("unsupported source OPB header")
                declared_variables = int(match.group(1))
                declared_constraints = int(match.group(2))
                continue

            observed_constraints += 1
            if raw_line == b"+1 x2 >= 1 ;\n":
                refinement_unit_matches.append(
                    {
                        "source_line": line_number,
                        "source_line_sha256": sha256_bytes(raw_line),
                    }
                )

            bound_match = BOUND_RE.search(raw_line)
            if bound_match is None or bound_match.group(1) != b"1":
                continue
            terms = tuple(TERM_RE.finditer(raw_line))
            if not terms or any(match.group(1) is None for match in terms):
                continue
            reconstructed = (
                b" ".join(
                    b"+1 ~x" + match.group(2)
                    for match in terms
                )
                + b" >= 1 ;\n"
            )
            if reconstructed != raw_line:
                raise ValueError("unsupported negative source clause syntax")
            existing_negative_clauses.add(
                tuple(sorted(int(match.group(2)) for match in terms))
            )

    if raw_digest.hexdigest() != EXPECTED_RAW_SHA256:
        raise ValueError("source raw OPB SHA-256 mismatch")
    if declared_variables != EXPECTED_VARIABLES:
        raise ValueError("source variable count changed")
    if declared_constraints != EXPECTED_CONSTRAINTS:
        raise ValueError("source constraint count changed")
    if observed_constraints != EXPECTED_CONSTRAINTS:
        raise ValueError("source observed constraint count changed")
    if refinement_unit_matches != [
        {
            "source_line": REFINEMENT_UNIT_LINE,
            "source_line_sha256": REFINEMENT_UNIT_SHA256,
        }
    ]:
        raise ValueError("frozen x2 refinement unit is missing or duplicated")

    overlaps = set(clauses).intersection(existing_negative_clauses)
    return {
        "path": SOURCE_OPB_GZIP.relative_to(REPOSITORY_ROOT).as_posix(),
        "gzip_bytes": len(compressed),
        "gzip_sha256": EXPECTED_GZIP_SHA256,
        "raw_sha256": EXPECTED_RAW_SHA256,
        "variables": declared_variables,
        "constraints": declared_constraints,
        "observed_constraints": observed_constraints,
        "existing_distinct_negative_clause_rows": len(
            existing_negative_clauses
        ),
        "refinement_unit": refinement_unit_matches[0],
        "exact_delta_clause_overlap_count": len(overlaps),
    }, overlaps


def validate_metadata() -> dict[str, object]:
    metadata = load_strict_json(SOURCE_METADATA, EXPECTED_METADATA_SHA256)
    if metadata.get("refined_branch") != 15:
        raise ValueError("source metadata is not refined branch 15")
    branch = metadata.get("branch")
    if not isinstance(branch, dict):
        raise ValueError("source metadata has no branch object")
    if branch.get("refinement_literal") != REFINEMENT_VARIABLE:
        raise ValueError("source metadata refinement literal changed")
    if branch.get("refinement_edge") != list(REFINEMENT_EDGE):
        raise ValueError("source metadata refinement edge changed")
    strengthening = branch.get("fixed_triangle_prism_strengthening")
    if not isinstance(strengthening, dict):
        raise ValueError("source metadata has no prism strengthening record")
    triangles = strengthening.get("per_triangle")
    if not isinstance(triangles, list):
        raise ValueError("source metadata triangle list is missing")
    catalog = {
        tuple(item.get("triangle", []))
        for item in triangles
        if isinstance(item, dict)
    }
    if len(catalog) != 6:
        raise ValueError("source metadata no longer freezes six parent triangles")
    if REFINEMENT_TRIANGLE in catalog:
        raise ValueError("seventh triangle unexpectedly appears in source metadata")
    return {
        "path": SOURCE_METADATA.relative_to(REPOSITORY_ROOT).as_posix(),
        "sha256": EXPECTED_METADATA_SHA256,
        "refined_branch": 15,
        "parent_triangle_count": len(catalog),
        "refinement_triangle_already_listed": False,
    }


def load_closure_assignments() -> tuple[dict[int, bool], dict[str, object]]:
    closure = load_strict_json(SOURCE_CLOSURE, EXPECTED_CLOSURE_SHA256)
    if closure.get("format") != "wave41-generalized-unit-closure-certificate-v1":
        raise ValueError("unsupported Wave 41 closure format")
    source = closure.get("source")
    if not isinstance(source, dict):
        raise ValueError("Wave 41 closure source is missing")
    if source.get("gzip_sha256") != EXPECTED_GZIP_SHA256:
        raise ValueError("Wave 41 closure binds the wrong compressed formula")
    if source.get("raw_sha256") != EXPECTED_RAW_SHA256:
        raise ValueError("Wave 41 closure binds the wrong raw formula")
    result = closure.get("result")
    if not isinstance(result, dict) or result.get("contradiction") is not None:
        raise ValueError("Wave 41 closure is contradictory or malformed")

    assignments: dict[int, bool] = {}
    derivations = closure.get("derivations")
    if not isinstance(derivations, list):
        raise ValueError("Wave 41 closure derivations are missing")
    for index, derivation in enumerate(derivations, start=1):
        if not isinstance(derivation, dict):
            raise ValueError("Wave 41 closure derivation is malformed")
        if derivation.get("index") != index:
            raise ValueError("Wave 41 closure derivation index changed")
        variable = derivation.get("variable")
        value = derivation.get("value")
        if type(variable) is not int or type(value) is not bool:
            raise ValueError("Wave 41 closure assignment is malformed")
        if variable in assignments:
            raise ValueError("Wave 41 closure assigns a variable twice")
        assignments[variable] = value
    if len(assignments) != result.get("total_forced_variables"):
        raise ValueError("Wave 41 closure assignment count changed")
    if assignments.get(REFINEMENT_VARIABLE) is not True:
        raise ValueError("Wave 41 closure does not retain x2=true")
    return assignments, {
        "path": SOURCE_CLOSURE.relative_to(REPOSITORY_ROOT).as_posix(),
        "sha256": EXPECTED_CLOSURE_SHA256,
        "claim_label": closure.get("claim_label"),
        "forced_variables": len(assignments),
        "forced_primary_variables": sum(
            variable <= PRIMARY_VARIABLES for variable in assignments
        ),
    }


def simplify_clauses(
    clauses: Sequence[Clause],
    assignments: Mapping[int, bool],
) -> tuple[tuple[Clause, ...], dict[str, int]]:
    active: set[Clause] = set()
    satisfied = 0
    contradictions = 0
    for clause in clauses:
        if any(assignments.get(variable) is False for variable in clause):
            satisfied += 1
            continue
        residual = tuple(
            variable
            for variable in clause
            if assignments.get(variable) is not True
        )
        if not residual:
            contradictions += 1
        else:
            active.add(residual)
    return tuple(sorted(active)), {
        "satisfied_by_forced_false_variable": satisfied,
        "empty_residual_contradictions": contradictions,
    }


def width_histogram(clauses: Sequence[Clause]) -> dict[str, int]:
    counts = Counter(len(clause) for clause in clauses)
    return {str(width): counts[width] for width in sorted(counts)}


def clause_catalog_sha256(clauses: Sequence[Clause]) -> str:
    payload = json.dumps(
        [list(clause) for clause in clauses],
        separators=(",", ":"),
    ).encode("ascii")
    return sha256_bytes(payload)


def delta_opb_payload(clauses: Sequence[Clause]) -> bytes:
    lines = [
        f"* #variable= {EXPECTED_VARIABLES} #constraint= {len(clauses)}"
    ]
    lines.extend(
        " ".join(f"+1 ~x{variable}" for variable in clause) + " >= 1 ;"
        for clause in clauses
    )
    return ("\n".join(lines) + "\n").encode("ascii")


def deterministic_gzip(payload: bytes) -> bytes:
    return gzip.compress(payload, compresslevel=9, mtime=0)


def build_artifacts() -> tuple[dict[str, object], bytes, bytes]:
    metadata_source = validate_metadata()
    clauses, enumeration = enumerate_delta_clauses()
    opb_source, overlaps = inspect_source(clauses)
    if overlaps:
        raise ValueError("delta clauses duplicate exact source OPB rows")

    assignments, closure_source = load_closure_assignments()
    active, simplification = simplify_clauses(clauses, assignments)
    if simplification["empty_residual_contradictions"]:
        diagnostic_status = "CANDIDATE_PROPAGATION_CONTRADICTION"
    else:
        diagnostic_status = "CANDIDATE_STRONGER_REDUCTION"

    delta_raw = delta_opb_payload(clauses)
    delta_gzip = deterministic_gzip(delta_raw)
    active_delta_raw = delta_opb_payload(active)
    active_delta_gzip = deterministic_gzip(active_delta_raw)
    result = {
        "format": RESULT_FORMAT,
        "role": "construction",
        "claim_label": "CANDIDATE",
        "git_commit": "ef49b60aafd67f9007f6c218c39fd50392453a1b",
        "scope": (
            "exact additional prism-blocking family forced by refined branch "
            "15's seventh fixed triangle, conditional on n3=4158"
        ),
        "sources": {
            "formula": opb_source,
            "formula_metadata": metadata_source,
            "wave41_closure_diagnostic_only": closure_source,
        },
        "derivation": {
            "primary_edge_numbering": (
                "lexicographic combinations of the 84 residual labels"
            ),
            "refinement_variable": REFINEMENT_VARIABLE,
            "refinement_edge": list(REFINEMENT_EDGE),
            "refinement_endpoint_labels": [[0, 2], [0, 4]],
            "shared_coordinate": 0,
            "full_vertex_triangle": list(REFINEMENT_TRIANGLE),
            "argument": (
                "x2 joins residual vertices 15 and 17, both adjacent to "
                "coordinate vertex 1. For every disjoint second triangle and "
                "perfect matching to this fixed triangle, P=0 forbids the "
                "conjunction of all nonfixed required residual edges."
            ),
            "no_completed_graph_automorphism_assumed": True,
        },
        "enumeration": enumeration,
        "delta": {
            "path": DELTA_RELATIVE_PATH,
            "raw_bytes": len(delta_raw),
            "raw_sha256": sha256_bytes(delta_raw),
            "gzip_bytes": len(delta_gzip),
            "gzip_sha256": sha256_bytes(delta_gzip),
            "variables": EXPECTED_VARIABLES,
            "constraints": len(clauses),
            "clause_width_histogram": width_histogram(clauses),
            "clause_catalog_sha256": clause_catalog_sha256(clauses),
            "clause_catalog_serialization": (
                "compact JSON array of sorted positive-variable-ID arrays"
            ),
            "opb_serialization": (
                "canonical header followed by sorted rows '+1 ~xID ... >= 1 ;'"
            ),
            "exact_rows_already_in_source": len(overlaps),
            "new_exact_rows": len(clauses) - len(overlaps),
        },
        "wave41_closure_simplification": {
            "status": diagnostic_status,
            **simplification,
            "distinct_active_clauses": len(active),
            "active_width_histogram": width_histogram(active),
            "active_clause_catalog_sha256": clause_catalog_sha256(active),
            "active_clause_catalog_serialization": (
                "compact JSON array of sorted positive-variable-ID arrays"
            ),
            "active_catalog": {
                "path": ACTIVE_DELTA_RELATIVE_PATH,
                "raw_bytes": len(active_delta_raw),
                "raw_sha256": sha256_bytes(active_delta_raw),
                "gzip_bytes": len(active_delta_gzip),
                "gzip_sha256": sha256_bytes(active_delta_gzip),
                "variables": EXPECTED_VARIABLES,
                "constraints": len(active),
                "opb_serialization": (
                    "canonical header followed by sorted rows "
                    "'+1 ~xID ... >= 1 ;'"
                ),
            },
            "immediate_negative_units": sum(
                len(clause) == 1 for clause in active
            ),
            "note": (
                "The closure simplification is diagnostic only. The published "
                "unsimplified delta is sound without trusting Wave 41's "
                "discovery-agent closure."
            ),
        },
        "result": {
            "status": diagnostic_status,
            "new_branch15_constraints": len(clauses),
            "active_after_wave41_closure": len(active),
            "immediate_contradiction": bool(
                simplification["empty_residual_contradictions"]
            ),
            "immediate_new_units": sum(len(clause) == 1 for clause in active),
            "branch15_sat": "UNKNOWN",
            "branch15_unsat": "UNKNOWN",
            "endpoint_cases_closed": 0,
            "endpoint_cases_total": 33,
        },
        "publication": {
            "method": "same-directory temporary, file fsync, atomic replace",
            "result_and_delta_regenerated_before_publication": True,
        },
        "limitations": [
            "This discovery package requires independent replay before promotion.",
            "The delta strengthens only refined endpoint branch 15.",
            "The delta still does not enumerate prisms whose two triangles are both unfixed.",
            "No immediate unit or contradiction follows after the Wave 41 closure.",
            "No SAT assignment or checked UNSAT proof was obtained.",
            "No endpoint case is closed and n3=4158 remains unknown.",
            "No graph, endpoint exclusion, upper-bound improvement, or global Conway result follows.",
        ],
    }
    return result, delta_gzip, active_delta_gzip


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
    output_path: Path = DEFAULT_OUTPUT,
    delta_path: Path = DEFAULT_DELTA,
    active_delta_path: Path = DEFAULT_ACTIVE_DELTA,
) -> dict[str, object]:
    expected_result, expected_delta, expected_active_delta = build_artifacts()
    actual_result = output_path.read_bytes()
    if actual_result != canonical_payload(expected_result):
        raise ValueError("committed result does not match exact regeneration")
    actual_delta = delta_path.read_bytes()
    if actual_delta != expected_delta:
        raise ValueError("committed compressed delta does not match regeneration")
    actual_active_delta = active_delta_path.read_bytes()
    if actual_active_delta != expected_active_delta:
        raise ValueError(
            "committed active compressed delta does not match regeneration"
        )
    raw_delta = gzip.decompress(actual_delta)
    if sha256_bytes(raw_delta) != expected_result["delta"]["raw_sha256"]:
        raise ValueError("committed delta raw SHA-256 mismatch")
    return {
        "status": "PASS_EXACT_REPLAY",
        "result_sha256": sha256_bytes(actual_result),
        "delta_gzip_sha256": sha256_bytes(actual_delta),
        "delta_raw_sha256": sha256_bytes(raw_delta),
        "active_delta_gzip_sha256": sha256_bytes(actual_active_delta),
        "active_delta_raw_sha256": sha256_bytes(
            gzip.decompress(actual_active_delta)
        ),
        "new_branch15_constraints": expected_result["result"][
            "new_branch15_constraints"
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--delta-gzip", type=Path, default=DEFAULT_DELTA)
    parser.add_argument(
        "--active-delta-gzip",
        type=Path,
        default=DEFAULT_ACTIVE_DELTA,
    )
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify:
        print(
            json.dumps(
                verify_committed(
                    args.output,
                    args.delta_gzip,
                    args.active_delta_gzip,
                ),
                sort_keys=True,
            )
        )
        return 0

    result, delta_gzip, active_delta_gzip = build_artifacts()
    atomic_write(args.delta_gzip, delta_gzip)
    atomic_write(args.active_delta_gzip, active_delta_gzip)
    atomic_write(args.output, canonical_payload(result))
    print(json.dumps(result["result"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
