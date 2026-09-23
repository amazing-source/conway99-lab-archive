#!/usr/bin/env python3
"""SAT scout for the surviving all-``q=2`` Wave 13 active frontier.

The encoded object has fifteen active labels, an 8-regular graph ``K``, and
a linear point hypergraph with point sizes two or three.  Every label occurs
in exactly three points.  The common-point/Berge-triangle rule and every
meeting-point crossing rule are encoded exactly.  A size-three point is also
forbidden from receiving more than twelve units from its overlapping
size-three co-points.

This is intentionally not a completed ``srg(99,14,1,2)`` encoding.  In
particular it does not require the remaining fixed-point support, inactive
vertices, or every global lambda/mu equality.  A SAT output is therefore a
machine-readable weakened survivor.  An UNSAT solver return is recorded only
as ``UNSAT_UNVERIFIED`` because this discovery script does not emit a checked
proof trace.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

import pysat
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


ORDER = 15
K_DEGREE = 8
ROOT_POINT = frozenset((0, 1, 2))
ALLOWED_SIZE3_COUNTS = tuple(range(1, 12, 2))
ROOT_MODES = ("111", "122", "222", "223")
FULL_CANDIDATE_SCHEMA = "conway99-wave13-n3-45-active-local-v2"
DIAGNOSTIC_CANDIDATE_SCHEMA = (
    "conway99-wave13-n3-45-active-local-diagnostic-v2"
)
ROOT_JUSTIFICATION = (
    "odd total incidence forces a size-three point; the full S_15 "
    "active-label action names it {0,1,2}, and its setwise stabilizer "
    "gives the recorded rooted-mode representative"
)
BASE_RESTRICTIONS = (
    "active_labels_only",
    "point_sizes_restricted_to_2_or_3_after_local_proof",
    "one_size3_point_fixed_by_full_label_relabeling",
    "one_of_four_root_modes_fixed_by_its_label_stabilizer",
    "meeting_crossings_and_overlap_fixed_point_upper_bound_only",
    "remaining_fixed_point_support_not_encoded",
    "inactive_vertices_not_encoded",
    "no_complete_99_vertex_adjacency_matrix",
    "no_global_lambda_mu_equalities",
)
OMITTED_PREMISES = {
    "no_overlap_cap": (
        "size-three full-L overlap contribution at most twelve"
    ),
    "no_common_point": "common-point/Berge-triangle prohibition",
    "k_degree_at_most": (
        "exact K-degree eight weakened to K-degree at most eight"
    ),
}
SCOUT_VARIANTS = (
    "full",
    "no_overlap_cap",
    "no_common_point",
    "k_degree_at_most",
)
ROOT_NORMALIZATION_KEYS = frozenset(
    (
        "point",
        "local_mode",
        "justification",
        "completed_graph_automorphism_assumed",
    )
)
DETERMINISTIC_SOLVER_STATISTIC_KEYS = frozenset(
    (
        "variant",
        "python",
        "python_sat",
        "solver",
        "conflict_budget",
        "result",
        "proof_trace",
        "variables",
        "clauses",
        "cnf_sha256",
        "candidate_point_variables",
        "candidate_K_edge_variables",
        "candidate_full_overlap_variables",
    )
)
DIAGNOSTIC_CANDIDATE_KEYS = frozenset(
    (
        "schema",
        "claim_label",
        "target_result",
        "novelty_status",
        "proof_trace_status",
        "variant",
        "active_order",
        "q_values",
        "K_degree",
        "size3_point_count",
        "root_mode",
        "point_sets",
        "K_edges",
        "root_normalization",
        "restrictions",
        "solver_statistics",
        "diagnostics",
        "omitted_premise",
        "builder_source_sha256",
        "core_semantic_sha256",
        "integrity_sha256",
    )
)
FULL_CANDIDATE_KEYS = frozenset(
    (
        "schema",
        "claim_label",
        "target_result",
        "novelty_status",
        "proof_trace_status",
        "variant",
        "active_order",
        "q_values",
        "K_degree",
        "size3_point_count",
        "root_mode",
        "point_sets",
        "K_edges",
        "root_normalization",
        "restrictions",
        "solver_statistics",
        "builder_source_sha256",
        "integrity_sha256",
    )
)
SCAN_BRANCHES = (
    (1, "111"),
    (3, "111"),
    (3, "122"),
    (5, "111"),
    (5, "122"),
    (5, "222"),
    (5, "223"),
    (7, "111"),
    (7, "122"),
    (7, "222"),
    (7, "223"),
    (9, "111"),
    (9, "122"),
    (9, "222"),
    (9, "223"),
    (11, "222"),
    (11, "223"),
)


def edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise ValueError("loops are not graph edges")
    return (left, right) if left < right else (right, left)


def all_edges() -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(ORDER), 2))


def all_points() -> tuple[frozenset[int], ...]:
    return tuple(
        frozenset(value)
        for size in (2, 3)
        for value in itertools.combinations(range(ORDER), size)
    )


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_sha256() -> str:
    return sha256_bytes(Path(__file__).resolve().read_bytes())


def require_exact_keys(
    value: object,
    expected: frozenset[str],
    *,
    name: str,
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise AssertionError(f"{name} must be an object")
    observed = frozenset(value)
    if observed != expected:
        missing = sorted(expected - observed)
        unknown = sorted(observed - expected)
        raise AssertionError(
            f"{name} schema mismatch: missing={missing}, unknown={unknown}"
        )
    return value


def canonical_point_records(value: object) -> tuple[tuple[int, ...], ...]:
    if not isinstance(value, list):
        raise AssertionError("point_sets must be a list")
    records = []
    for raw in value:
        if not isinstance(raw, list) or len(raw) not in (2, 3):
            raise AssertionError("point record must be a size-two/three list")
        if any(type(vertex) is not int for vertex in raw):
            raise AssertionError("point labels must be integers")
        record = tuple(raw)
        if tuple(sorted(record)) != record or len(set(record)) != len(record):
            raise AssertionError("point record is not strictly canonical")
        if not all(0 <= vertex < ORDER for vertex in record):
            raise AssertionError("point label is out of range")
        records.append(record)
    canonical = sorted(records, key=lambda item: (len(item), item))
    if records != canonical:
        raise AssertionError("point_sets are not in canonical order")
    if len(set(records)) != len(records):
        raise AssertionError("duplicate point record")
    return tuple(records)


def canonical_edge_records(value: object) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, list):
        raise AssertionError("K_edges must be a list")
    records = []
    for raw in value:
        if not isinstance(raw, list) or len(raw) != 2:
            raise AssertionError("K edge record must be a two-label list")
        if any(type(vertex) is not int for vertex in raw):
            raise AssertionError("K edge labels must be integers")
        left, right = raw
        if not (0 <= left < right < ORDER):
            raise AssertionError("K edge record is not strictly canonical")
        records.append((left, right))
    if records != sorted(records):
        raise AssertionError("K_edges are not in canonical order")
    if len(set(records)) != len(records):
        raise AssertionError("duplicate K edge record")
    return tuple(records)


def cnf_sha256(cnf: CNF, variable_count: int) -> str:
    """Hash the exact deterministic DIMACS clause stream without writing it."""

    digest = hashlib.sha256()
    digest.update(
        f"p cnf {variable_count} {len(cnf.clauses)}\n".encode("ascii")
    )
    for clause in cnf.clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    return digest.hexdigest()


def deterministic_candidate_statistics(
    runtime_statistics: dict[str, object],
) -> dict[str, object]:
    return {
        "variant": runtime_statistics["variant"],
        "python": runtime_statistics["python"],
        "python_sat": runtime_statistics["python_sat"],
        "solver": runtime_statistics["solver"],
        "conflict_budget": runtime_statistics["conflict_budget"],
        "result": "SAT_WEAKENED_MODEL",
        "proof_trace": "NOT_EMITTED",
        "variables": runtime_statistics["variables"],
        "clauses": runtime_statistics["clauses"],
        "cnf_sha256": runtime_statistics["cnf_sha256"],
        "candidate_point_variables": runtime_statistics[
            "candidate_point_variables"
        ],
        "candidate_K_edge_variables": runtime_statistics[
            "candidate_K_edge_variables"
        ],
        "candidate_full_overlap_variables": runtime_statistics[
            "candidate_full_overlap_variables"
        ],
    }


def candidate_core_semantic(
    candidate: dict[str, object],
) -> dict[str, object]:
    return {
        "variant": candidate["variant"],
        "point_sets": candidate["point_sets"],
        "K_edges": candidate["K_edges"],
        "diagnostics": candidate["diagnostics"],
    }


def candidate_integrity_payload(
    candidate: dict[str, object],
) -> dict[str, object]:
    keys = (
        DIAGNOSTIC_CANDIDATE_KEYS
        if candidate.get("schema") == DIAGNOSTIC_CANDIDATE_SCHEMA
        else FULL_CANDIDATE_KEYS
    )
    return {
        key: candidate[key]
        for key in sorted(keys - {"integrity_sha256"})
    }


def candidate_json_bytes(candidate: dict[str, object]) -> bytes:
    return (
        json.dumps(candidate, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def add_equals(
    cnf: CNF,
    pool: IDPool,
    literals: Iterable[int],
    bound: int,
) -> None:
    encoded = CardEnc.equals(
        lits=list(literals),
        bound=bound,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    cnf.extend(encoded.clauses)


def add_at_most(
    cnf: CNF,
    pool: IDPool,
    literals: Iterable[int],
    bound: int,
) -> None:
    values = list(literals)
    if len(values) <= bound:
        return
    encoded = CardEnc.atmost(
        lits=values,
        bound=bound,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    cnf.extend(encoded.clauses)


def build_instance(
    size3_count: int,
    root_mode: str,
    variant: str = "full",
) -> tuple[
    CNF,
    IDPool,
    tuple[frozenset[int], ...],
    dict[frozenset[int], int],
    dict[tuple[int, int], int],
    dict[tuple[int, int], int],
    dict[tuple[frozenset[int], frozenset[int]], int],
]:
    if size3_count not in ALLOWED_SIZE3_COUNTS:
        raise ValueError(f"size3_count must lie in {ALLOWED_SIZE3_COUNTS}")
    if root_mode not in ROOT_MODES:
        raise ValueError(f"root_mode must lie in {ROOT_MODES}")
    if variant not in SCOUT_VARIANTS:
        raise ValueError(f"variant must lie in {SCOUT_VARIANTS}")
    minimum_points = {"111": 1, "122": 3, "222": 4, "223": 5}
    if size3_count < minimum_points[root_mode]:
        raise ValueError(
            f"root mode {root_mode} needs at least "
            f"{minimum_points[root_mode]} size-three points"
        )

    points = all_points()
    edges = all_edges()
    pool = IDPool()
    selected = {
        point: pool.id(("point", tuple(sorted(point)))) for point in points
    }
    k_edge = {item: pool.id(("K", item)) for item in edges}
    f_edge = {item: pool.id(("F", item)) for item in edges}
    full_overlap: dict[
        tuple[frozenset[int], frozenset[int]], int
    ] = {}
    cnf = CNF()

    # Every active label belongs to exactly three original point sets.
    for vertex in range(ORDER):
        add_equals(
            cnf,
            pool,
            (selected[point] for point in points if vertex in point),
            3,
        )
    add_equals(
        cnf,
        pool,
        (selected[point] for point in points if len(point) == 3),
        size3_count,
    )

    # Every feasible order-fifteen system has at least one size-three point
    # because its total incidence count is odd.  The full S_15 label action
    # therefore allows one selected size-three point to be named {0,1,2}.
    # This is search-label normalization, not a completed-graph automorphism.
    cnf.append([selected[ROOT_POINT]])
    if size3_count == 1:
        for point in points:
            if len(point) == 3 and point != ROOT_POINT:
                cnf.append([-selected[point]])
        # The setwise stabilizer S_3 x S_12 of ROOT_POINT can name the two
        # size-two mates at its three labels in three consecutive pairs.
        # A non-root label cannot be reused across two root labels, since
        # that would create a forbidden primal triangle with an edge of the
        # selected root point.
        normalized_root_mates = (
            (0, 3),
            (0, 4),
            (1, 5),
            (1, 6),
            (2, 7),
            (2, 8),
        )
        for item in normalized_root_mates:
            cnf.append([selected[frozenset(item)]])

    # Cover the four exact local modes of the named root point.  The setwise
    # stabilizer of {0,1,2}, followed by relabeling outside that set, gives
    # the displayed representatives.  For mode 223 the two co-points at the
    # degree-three root occurrence are distinguished by whether their
    # crossing with ROOT_POINT is empty or full in L.
    root_mode_data: dict[
        str, tuple[tuple[tuple[int, int, int], str], ...]
    ] = {
        "111": (),
        "122": (
            ((1, 3, 4), "full_L"),
            ((2, 5, 6), "full_L"),
        ),
        "222": (
            ((0, 3, 4), "full_L"),
            ((1, 5, 6), "full_L"),
            ((2, 7, 8), "full_L"),
        ),
        "223": (
            ((0, 3, 4), "empty_L"),
            ((0, 5, 6), "full_L"),
            ((1, 7, 8), "full_L"),
            ((2, 9, 10), "full_L"),
        ),
    }
    root_co_points = {
        frozenset(point): crossing
        for point, crossing in root_mode_data[root_mode]
    }
    for point in root_co_points:
        cnf.append([selected[point]])
    for point in points:
        if (
            len(point) == 3
            and point != ROOT_POINT
            and point & ROOT_POINT
            and point not in root_co_points
        ):
            cnf.append([-selected[point]])
    for point, crossing in root_co_points.items():
        common = next(iter(point & ROOT_POINT))
        cross_edges = [
            edge(first, second)
            for first in point - {common}
            for second in ROOT_POINT - {common}
        ]
        for item in cross_edges:
            cnf.append(
                [k_edge[item] if crossing == "empty_L" else -k_edge[item]]
            )
    if root_mode == "111" and size3_count > 1:
        # Every other size-three point is disjoint from ROOT_POINT.  One of
        # them may therefore be named {3,4,5}.
        cnf.append([selected[frozenset((3, 4, 5))]])

    # F is the union of point-clique edges.  Linearity is an at-most-one
    # owner constraint for each active-label pair.
    for item in edges:
        owners = [
            selected[point] for point in points if set(item) <= point
        ]
        add_at_most(cnf, pool, owners, 1)
        for owner in owners:
            cnf.append([-owner, f_edge[item]])
        cnf.append([-f_edge[item], *owners])

    # Every selected point is a clique in K.
    for point in points:
        for item in itertools.combinations(sorted(point), 2):
            cnf.append([-selected[point], k_edge[item]])

    # In a linear point hypergraph, the common-point rule says that any
    # triangle of the primal F graph must be owned by its size-three point.
    if variant != "no_common_point":
        for triple in itertools.combinations(range(ORDER), 3):
            ab, ac, bc = itertools.combinations(triple, 2)
            triple_point = frozenset(triple)
            cnf.append(
                [
                    -f_edge[ab],
                    -f_edge[ac],
                    -f_edge[bc],
                    selected[triple_point],
                ]
            )

    size3_points = tuple(point for point in points if len(point) == 3)
    overlap_by_point: dict[frozenset[int], list[int]] = {
        point: [] for point in size3_points
    }

    interaction_points = (
        tuple(
            point
            for point in points
            if len(point) == 2 or point == ROOT_POINT
        )
        if size3_count == 1
        else points
    )

    # Meeting point sets are actual neighboring original vertices.  After
    # deleting their common active triangle, every L-crossing degree is zero
    # or two.  Thus a singleton-side crossing is empty, while a 2-by-2
    # crossing is empty or complete.
    for left_index, left in enumerate(interaction_points):
        for right in interaction_points[left_index + 1 :]:
            intersection = left & right
            if len(intersection) != 1:
                continue
            common = next(iter(intersection))
            left_external = sorted(left - {common})
            right_external = sorted(right - {common})
            crossing = [
                k_edge[edge(first, second)]
                for first in left_external
                for second in right_external
            ]
            if len(left_external) == 1 or len(right_external) == 1:
                for literal in crossing:
                    cnf.append(
                        [-selected[left], -selected[right], literal]
                    )
                continue

            first = crossing[0]
            for literal in crossing[1:]:
                cnf.append(
                    [
                        -selected[left],
                        -selected[right],
                        -first,
                        literal,
                    ]
                )
                cnf.append(
                    [
                        -selected[left],
                        -selected[right],
                        first,
                        -literal,
                    ]
                )

            # With at most three selected size-three points, no one point can
            # have four full overlaps, so the fixed-point upper bound is
            # automatic and these auxiliaries are unnecessary.  Larger
            # branches receive the exact reified cap below.
            if size3_count >= 5 and variant != "no_overlap_cap":
                # w <-> selected(left) & selected(right) & not K(first).
                key = (left, right)
                witness = pool.id(
                    (
                        "full_L_overlap",
                        tuple(sorted(left)),
                        tuple(sorted(right)),
                    )
                )
                full_overlap[key] = witness
                overlap_by_point[left].append(witness)
                overlap_by_point[right].append(witness)
                cnf.append([-witness, selected[left]])
                cnf.append([-witness, selected[right]])
                cnf.append([-witness, -first])
                cnf.append(
                    [
                        -selected[left],
                        -selected[right],
                        first,
                        witness,
                    ]
                )

    # Each full 2-by-2 overlap contributes four to a size-three point's
    # fixed-point total of twelve.
    if size3_count >= 5 and variant != "no_overlap_cap":
        for point in size3_points:
            add_at_most(cnf, pool, overlap_by_point[point], 3)

    # K is exactly 8-regular in the full model.  The named scout mutation
    # keeps only the necessary upper bound to test whether regular completion
    # is doing hidden work.
    for vertex in range(ORDER):
        literals = [
            k_edge[edge(vertex, other)]
            for other in range(ORDER)
            if other != vertex
        ]
        if variant == "k_degree_at_most":
            add_at_most(cnf, pool, literals, K_DEGREE)
        else:
            add_equals(cnf, pool, literals, K_DEGREE)

    return (
        cnf,
        pool,
        points,
        selected,
        k_edge,
        f_edge,
        full_overlap,
    )


def vertex_degrees(
    graph_edges: Iterable[tuple[int, int]],
) -> tuple[int, ...]:
    values = [0] * ORDER
    for left, right in graph_edges:
        values[left] += 1
        values[right] += 1
    return tuple(values)


def validate_candidate(candidate: dict[str, object]) -> dict[str, object]:
    require_exact_keys(
        candidate,
        FULL_CANDIDATE_KEYS,
        name="full candidate",
    )
    if candidate["schema"] != FULL_CANDIDATE_SCHEMA:
        raise AssertionError("candidate schema mismatch")
    if candidate["claim_label"] != "CANDIDATE":
        raise AssertionError("candidate status inflation")
    if candidate["target_result"] != "UNKNOWN":
        raise AssertionError("target status inflation")
    if candidate["novelty_status"] != "UNKNOWN":
        raise AssertionError("novelty status inflation")
    if candidate["proof_trace_status"] != "NOT_EMITTED":
        raise AssertionError("candidate falsely claims a proof trace")
    if candidate["variant"] != "full":
        raise AssertionError("full candidate has the wrong variant")
    if candidate["active_order"] != ORDER:
        raise AssertionError("wrong active order")
    if candidate["K_degree"] != K_DEGREE:
        raise AssertionError("wrong K-degree metadata")
    if candidate["q_values"] != [2] * ORDER:
        raise AssertionError("candidate is not the all-q=2 frontier")
    size3_count = candidate["size3_point_count"]
    if type(size3_count) is not int or size3_count not in ALLOWED_SIZE3_COUNTS:
        raise AssertionError("invalid size-three count")
    root_mode = candidate["root_mode"]
    if root_mode not in ROOT_MODES:
        raise AssertionError("invalid rooted local mode")
    root_metadata = require_exact_keys(
        candidate["root_normalization"],
        ROOT_NORMALIZATION_KEYS,
        name="root_normalization",
    )
    if root_metadata != {
        "point": sorted(ROOT_POINT),
        "local_mode": root_mode,
        "justification": ROOT_JUSTIFICATION,
        "completed_graph_automorphism_assumed": False,
    }:
        raise AssertionError("root-normalization metadata mismatch")

    point_records = canonical_point_records(candidate["point_sets"])
    points = tuple(frozenset(item) for item in point_records)
    if ROOT_POINT not in points:
        raise AssertionError("root normalization is absent")
    if sum(len(point) == 3 for point in points) != size3_count:
        raise AssertionError("size-three count mismatch")
    incidence = Counter(vertex for point in points for vertex in point)
    if tuple(incidence[vertex] for vertex in range(ORDER)) != (3,) * ORDER:
        raise AssertionError("point incidence is not three at every label")

    pair_owner: dict[tuple[int, int], frozenset[int]] = {}
    for point in points:
        for item in itertools.combinations(sorted(point), 2):
            if item in pair_owner:
                raise AssertionError("point hypergraph is not linear")
            pair_owner[item] = point
    for triple in itertools.combinations(range(ORDER), 3):
        pair_items = tuple(itertools.combinations(triple, 2))
        if all(item in pair_owner for item in pair_items):
            if frozenset(triple) not in points:
                raise AssertionError("forbidden common-point Berge triangle")

    edge_records = canonical_edge_records(candidate["K_edges"])
    k_edges = frozenset(edge_records)
    if vertex_degrees(k_edges) != (K_DEGREE,) * ORDER:
        raise AssertionError("K is not 8-regular")
    if not set(pair_owner) <= k_edges:
        raise AssertionError("a point is not a clique in K")

    crossing_count = 0
    full_overlaps: list[tuple[int, int]] = []
    overlap_degree = [0] * len(points)
    for left_index, left in enumerate(points):
        for right_index in range(left_index + 1, len(points)):
            right = points[right_index]
            intersection = left & right
            if len(intersection) != 1:
                continue
            crossing_count += 1
            common = next(iter(intersection))
            left_external = sorted(left - {common})
            right_external = sorted(right - {common})
            l_matrix = [
                [
                    edge(first, second) not in k_edges
                    for second in right_external
                ]
                for first in left_external
            ]
            row_degrees = [sum(row) for row in l_matrix]
            column_degrees = [
                sum(l_matrix[row][column] for row in range(len(l_matrix)))
                for column in range(len(right_external))
            ]
            if any(
                value not in (0, 2)
                for value in (*row_degrees, *column_degrees)
            ):
                raise AssertionError("meeting crossing degree is not zero or two")
            if len(left) == len(right) == 3 and sum(row_degrees) == 4:
                full_overlaps.append((left_index, right_index))
                overlap_degree[left_index] += 1
                overlap_degree[right_index] += 1

    if any(
        overlap_degree[index] > 3
        for index, point in enumerate(points)
        if len(point) == 3
    ):
        raise AssertionError("size-three overlap contribution exceeds twelve")

    t_values = tuple(
        sum(len(point) == 3 and vertex in point for point in points)
        for vertex in range(ORDER)
    )
    local_types = Counter(
        tuple(sorted(t_values[vertex] for vertex in point))
        for point in points
        if len(point) == 3
    )
    allowed_types = {(1, 1, 1), (1, 2, 2), (2, 2, 2), (2, 2, 3)}
    if not set(local_types) <= allowed_types:
        raise AssertionError("candidate has a forbidden local t-profile")
    observed_root_mode = "".join(
        map(str, sorted(t_values[vertex] for vertex in ROOT_POINT))
    )
    if observed_root_mode != root_mode:
        raise AssertionError("rooted local mode mismatch")

    if candidate["restrictions"] != list(BASE_RESTRICTIONS):
        raise AssertionError("candidate restriction boundary changed")

    statistics = require_exact_keys(
        candidate["solver_statistics"],
        DETERMINISTIC_SOLVER_STATISTIC_KEYS,
        name="solver_statistics",
    )
    if (
        statistics["variant"] != "full"
        or statistics["python"] != sys.version.split()[0]
        or statistics["python_sat"] != pysat.__version__
        or statistics["solver"] != "cadical195"
        or statistics["result"] != "SAT_WEAKENED_MODEL"
        or statistics["proof_trace"] != "NOT_EMITTED"
    ):
        raise AssertionError("full candidate solver metadata mismatch")
    (
        cnf,
        pool,
        candidate_points,
        _selected,
        candidate_k_edges,
        _f_edges,
        full_overlap,
    ) = build_instance(size3_count, root_mode, "full")
    formula_statistics = {
        "variables": pool.top,
        "clauses": len(cnf.clauses),
        "cnf_sha256": cnf_sha256(cnf, pool.top),
        "candidate_point_variables": len(candidate_points),
        "candidate_K_edge_variables": len(candidate_k_edges),
        "candidate_full_overlap_variables": len(full_overlap),
    }
    for key, expected in formula_statistics.items():
        if statistics[key] != expected:
            raise AssertionError(f"formula metadata mismatch: {key}")
    if candidate["builder_source_sha256"] != source_sha256():
        raise AssertionError("candidate is not bound to the current builder")
    integrity_sha256 = sha256_bytes(
        canonical_json_bytes(candidate_integrity_payload(candidate))
    )
    if candidate["integrity_sha256"] != integrity_sha256:
        raise AssertionError("candidate integrity hash mismatch")

    semantic = {
        "active_order": ORDER,
        "q_values": [2] * ORDER,
        "point_sets": [sorted(point) for point in points],
        "K_edges": [list(item) for item in sorted(k_edges)],
        "full_L_overlaps": [list(item) for item in full_overlaps],
    }
    return {
        "status": "PASS weakened n3=45 active-local SAT candidate",
        "point_count": len(points),
        "size2_point_count": sum(len(point) == 2 for point in points),
        "size3_point_count": size3_count,
        "K_edge_count": len(k_edges),
        "meeting_crossings_checked": crossing_count,
        "full_L_overlap_count": len(full_overlaps),
        "t_degree_histogram": {
            str(key): value for key, value in sorted(Counter(t_values).items())
        },
        "size3_local_type_histogram": {
            "".join(map(str, key)): value
            for key, value in sorted(local_types.items())
        },
        "semantic_sha256": sha256_bytes(canonical_json_bytes(semantic)),
        "cnf_sha256": formula_statistics["cnf_sha256"],
        "integrity_sha256": integrity_sha256,
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty_status": "UNKNOWN",
    }


def weakened_assignment_diagnostics(
    points: Sequence[frozenset[int]],
    k_edges: frozenset[tuple[int, int]],
) -> dict[str, object]:
    """Measure every full-model premise on a deliberately weakened model."""

    incidence = Counter(vertex for point in points for vertex in point)
    owners: dict[tuple[int, int], list[int]] = {
        item: [] for item in all_edges()
    }
    missing_point_clique_edges = 0
    for point_index, point in enumerate(points):
        for item in itertools.combinations(sorted(point), 2):
            owners[item].append(point_index)
            if item not in k_edges:
                missing_point_clique_edges += 1

    berge_triangles = []
    point_set = set(points)
    for triple in itertools.combinations(range(ORDER), 3):
        pair_items = tuple(itertools.combinations(triple, 2))
        if all(owners[item] for item in pair_items):
            if frozenset(triple) not in point_set:
                berge_triangles.append(list(triple))

    crossing_violations = 0
    full_overlap_degree = [0] * len(points)
    full_overlaps = []
    for left_index, left in enumerate(points):
        for right_index in range(left_index + 1, len(points)):
            right = points[right_index]
            intersection = left & right
            if len(intersection) != 1:
                continue
            common = next(iter(intersection))
            left_external = sorted(left - {common})
            right_external = sorted(right - {common})
            l_matrix = [
                [
                    edge(first, second) not in k_edges
                    for second in right_external
                ]
                for first in left_external
            ]
            row_degrees = [sum(row) for row in l_matrix]
            column_degrees = [
                sum(l_matrix[row][column] for row in range(len(l_matrix)))
                for column in range(len(right_external))
            ]
            if any(
                value not in (0, 2)
                for value in (*row_degrees, *column_degrees)
            ):
                crossing_violations += 1
            if len(left) == len(right) == 3 and sum(row_degrees) == 4:
                full_overlaps.append((left_index, right_index))
                full_overlap_degree[left_index] += 1
                full_overlap_degree[right_index] += 1

    size3_overlap_degrees = [
        full_overlap_degree[index]
        for index, point in enumerate(points)
        if len(point) == 3
    ]
    t_values = tuple(
        sum(len(point) == 3 and vertex in point for point in points)
        for vertex in range(ORDER)
    )
    local_types = Counter(
        tuple(sorted(t_values[vertex] for vertex in point))
        for point in points
        if len(point) == 3
    )
    return {
        "point_count": len(points),
        "size2_point_count": sum(len(point) == 2 for point in points),
        "size3_point_count": sum(len(point) == 3 for point in points),
        "incidence_degrees": [incidence[vertex] for vertex in range(ORDER)],
        "linear_pair_owner_violations": sum(
            len(indices) > 1 for indices in owners.values()
        ),
        "missing_point_clique_edges": missing_point_clique_edges,
        "K_degree_sequence": list(vertex_degrees(k_edges)),
        "common_point_Berge_triangle_count": len(berge_triangles),
        "first_common_point_Berge_triangles": berge_triangles[:10],
        "meeting_crossing_violations": crossing_violations,
        "full_L_overlap_count": len(full_overlaps),
        "maximum_size3_full_L_overlap_degree": max(
            size3_overlap_degrees, default=0
        ),
        "size3_points_over_fixed_point_cap": sum(
            value > 3 for value in size3_overlap_degrees
        ),
        "t_degree_histogram": {
            str(key): value for key, value in sorted(Counter(t_values).items())
        },
        "size3_local_type_histogram": {
            "".join(map(str, key)): value
            for key, value in sorted(local_types.items())
        },
    }


def validate_weakened_candidate(
    candidate: dict[str, object],
) -> dict[str, object]:
    require_exact_keys(
        candidate,
        DIAGNOSTIC_CANDIDATE_KEYS,
        name="diagnostic candidate",
    )
    expected_scalars = {
        "schema": DIAGNOSTIC_CANDIDATE_SCHEMA,
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty_status": "UNKNOWN",
        "proof_trace_status": "NOT_EMITTED",
        "active_order": ORDER,
        "K_degree": K_DEGREE,
    }
    for key, expected in expected_scalars.items():
        if candidate[key] != expected:
            raise AssertionError(f"diagnostic metadata mismatch: {key}")
    if candidate["q_values"] != [2] * ORDER:
        raise AssertionError("diagnostic q metadata mismatch")

    variant = candidate["variant"]
    if variant not in OMITTED_PREMISES:
        raise AssertionError("diagnostic variant mismatch")
    if candidate["omitted_premise"] != OMITTED_PREMISES[variant]:
        raise AssertionError("omitted-premise metadata mismatch")
    expected_restrictions = [
        *BASE_RESTRICTIONS,
        f"diagnostic_variant_{variant}",
    ]
    if candidate["restrictions"] != expected_restrictions:
        raise AssertionError("diagnostic restriction boundary changed")

    size3_count = candidate["size3_point_count"]
    if type(size3_count) is not int or size3_count not in ALLOWED_SIZE3_COUNTS:
        raise AssertionError("invalid size-three metadata")
    root_mode = candidate["root_mode"]
    if root_mode not in ROOT_MODES:
        raise AssertionError("invalid root-mode metadata")

    root_metadata = require_exact_keys(
        candidate["root_normalization"],
        ROOT_NORMALIZATION_KEYS,
        name="root_normalization",
    )
    if root_metadata != {
        "point": sorted(ROOT_POINT),
        "local_mode": root_mode,
        "justification": ROOT_JUSTIFICATION,
        "completed_graph_automorphism_assumed": False,
    }:
        raise AssertionError("root-normalization metadata mismatch")

    point_records = canonical_point_records(candidate["point_sets"])
    edge_records = canonical_edge_records(candidate["K_edges"])
    points = tuple(frozenset(item) for item in point_records)
    k_edges = frozenset(edge_records)
    if ROOT_POINT not in points:
        raise AssertionError("normalized root point is absent")
    if sum(len(point) == 3 for point in points) != size3_count:
        raise AssertionError("size-three metadata does not match the core")

    observed = weakened_assignment_diagnostics(points, k_edges)
    archived_diagnostics = require_exact_keys(
        candidate["diagnostics"],
        frozenset(observed),
        name="diagnostics",
    )
    if observed != archived_diagnostics:
        raise AssertionError("diagnostic recomputation mismatch")
    if observed["incidence_degrees"] != [3] * ORDER:
        raise AssertionError("diagnostic lost exact point incidence")
    if observed["linear_pair_owner_violations"]:
        raise AssertionError("diagnostic lost linearity")
    if observed["missing_point_clique_edges"]:
        raise AssertionError("diagnostic lost the point-clique premise")
    if variant == "k_degree_at_most":
        if max(observed["K_degree_sequence"], default=0) > K_DEGREE:
            raise AssertionError("upper-bound diagnostic exceeds K-degree eight")
    elif observed["K_degree_sequence"] != [K_DEGREE] * ORDER:
        raise AssertionError("diagnostic K is not 8-regular")
    if observed["meeting_crossing_violations"]:
        raise AssertionError("diagnostic lost the meeting-crossing premise")

    t_values = tuple(
        sum(len(point) == 3 and vertex in point for point in points)
        for vertex in range(ORDER)
    )
    actual_root_mode = "".join(
        map(str, sorted(t_values[vertex] for vertex in ROOT_POINT))
    )
    if actual_root_mode != root_mode:
        raise AssertionError("claimed root mode is not present in the core")

    if variant == "no_common_point":
        if observed["common_point_Berge_triangle_count"] == 0:
            raise AssertionError("no-common-point diagnostic does not violate it")
        if observed["size3_points_over_fixed_point_cap"]:
            raise AssertionError("no-common-point diagnostic also violates overlap cap")
    elif variant == "no_overlap_cap":
        if observed["common_point_Berge_triangle_count"]:
            raise AssertionError("no-overlap diagnostic violates common-point premise")
        if observed["size3_points_over_fixed_point_cap"] == 0:
            raise AssertionError("no-overlap diagnostic does not violate its omission")
    else:
        if observed["common_point_Berge_triangle_count"]:
            raise AssertionError("K-upper-bound diagnostic violates common point")
        if observed["size3_points_over_fixed_point_cap"]:
            raise AssertionError("K-upper-bound diagnostic violates overlap cap")
        if observed["K_degree_sequence"] == [K_DEGREE] * ORDER:
            raise AssertionError("K-upper-bound diagnostic is already regular")

    statistics = require_exact_keys(
        candidate["solver_statistics"],
        DETERMINISTIC_SOLVER_STATISTIC_KEYS,
        name="solver_statistics",
    )
    if statistics["variant"] != variant:
        raise AssertionError("solver variant metadata mismatch")
    if statistics["python"] != sys.version.split()[0]:
        raise AssertionError("solver Python version metadata mismatch")
    if statistics["python_sat"] != pysat.__version__:
        raise AssertionError("solver PySAT version metadata mismatch")
    if statistics["solver"] != "cadical195":
        raise AssertionError("canonical diagnostic solver changed")
    if statistics["conflict_budget"] != 300_000:
        raise AssertionError("canonical diagnostic conflict budget changed")
    if statistics["result"] != "SAT_WEAKENED_MODEL":
        raise AssertionError("diagnostic solver result metadata mismatch")
    if statistics["proof_trace"] != "NOT_EMITTED":
        raise AssertionError("diagnostic falsely claims a proof trace")

    (
        cnf,
        pool,
        candidate_points,
        _selected,
        candidate_k_edges,
        _f_edges,
        full_overlap,
    ) = build_instance(size3_count, root_mode, variant)
    expected_formula_statistics = {
        "variables": pool.top,
        "clauses": len(cnf.clauses),
        "cnf_sha256": cnf_sha256(cnf, pool.top),
        "candidate_point_variables": len(candidate_points),
        "candidate_K_edge_variables": len(candidate_k_edges),
        "candidate_full_overlap_variables": len(full_overlap),
    }
    for key, expected in expected_formula_statistics.items():
        if statistics[key] != expected:
            raise AssertionError(f"formula metadata mismatch: {key}")

    current_source_sha256 = source_sha256()
    if candidate["builder_source_sha256"] != current_source_sha256:
        raise AssertionError("candidate is not bound to the current builder")
    core_sha256 = sha256_bytes(
        canonical_json_bytes(candidate_core_semantic(candidate))
    )
    if candidate["core_semantic_sha256"] != core_sha256:
        raise AssertionError("diagnostic core semantic hash mismatch")
    integrity_sha256 = sha256_bytes(
        canonical_json_bytes(candidate_integrity_payload(candidate))
    )
    if candidate["integrity_sha256"] != integrity_sha256:
        raise AssertionError("diagnostic integrity hash mismatch")
    return {
        "status": "PASS weakened active-local diagnostic",
        "variant": variant,
        "cnf_sha256": expected_formula_statistics["cnf_sha256"],
        "core_semantic_sha256": core_sha256,
        "integrity_sha256": integrity_sha256,
        "omitted_premise_violation_count": (
            observed["common_point_Berge_triangle_count"]
            if variant == "no_common_point"
            else observed["size3_points_over_fixed_point_cap"]
            if variant == "no_overlap_cap"
            else sum(
                K_DEGREE - value
                for value in observed["K_degree_sequence"]
            )
        ),
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty_status": "UNKNOWN",
    }


def candidate_from_model(
    *,
    size3_count: int,
    root_mode: str,
    variant: str,
    points: Sequence[frozenset[int]],
    selected: dict[frozenset[int], int],
    k_edge: dict[tuple[int, int], int],
    model: Sequence[int],
    solver_statistics: dict[str, object],
) -> dict[str, object]:
    positive = {literal for literal in model if literal > 0}
    chosen_points = tuple(
        point for point in points if selected[point] in positive
    )
    chosen_k = tuple(
        item for item, variable in k_edge.items() if variable in positive
    )
    candidate = {
        "schema": (
            FULL_CANDIDATE_SCHEMA
            if variant == "full"
            else DIAGNOSTIC_CANDIDATE_SCHEMA
        ),
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty_status": "UNKNOWN",
        "proof_trace_status": "NOT_EMITTED",
        "variant": variant,
        "active_order": ORDER,
        "q_values": [2] * ORDER,
        "K_degree": K_DEGREE,
        "size3_point_count": size3_count,
        "root_mode": root_mode,
        "point_sets": [sorted(point) for point in chosen_points],
        "K_edges": [list(item) for item in chosen_k],
        "root_normalization": {
            "point": sorted(ROOT_POINT),
            "local_mode": root_mode,
            "justification": ROOT_JUSTIFICATION,
            "completed_graph_automorphism_assumed": False,
        },
        "restrictions": list(BASE_RESTRICTIONS),
        "solver_statistics": deterministic_candidate_statistics(
            solver_statistics
        ),
        "builder_source_sha256": source_sha256(),
    }
    if variant != "full":
        candidate["restrictions"].append(f"diagnostic_variant_{variant}")
    if variant == "full":
        candidate["integrity_sha256"] = sha256_bytes(
            canonical_json_bytes(candidate_integrity_payload(candidate))
        )
        validate_candidate(candidate)
    else:
        candidate["diagnostics"] = weakened_assignment_diagnostics(
            chosen_points, frozenset(chosen_k)
        )
        candidate["omitted_premise"] = OMITTED_PREMISES[variant]
        candidate["core_semantic_sha256"] = sha256_bytes(
            canonical_json_bytes(candidate_core_semantic(candidate))
        )
        candidate["integrity_sha256"] = sha256_bytes(
            canonical_json_bytes(candidate_integrity_payload(candidate))
        )
        validate_weakened_candidate(candidate)
    return candidate


def solve(
    size3_count: int,
    root_mode: str,
    conflict_budget: int | None,
    solver_name: str,
    variant: str = "full",
) -> tuple[str, dict[str, object], dict[str, object] | None]:
    (
        cnf,
        pool,
        points,
        selected,
        k_edge,
        _f_edge,
        full_overlap,
    ) = build_instance(size3_count, root_mode, variant)
    formula_sha256 = cnf_sha256(cnf, pool.top)
    with Solver(
        name=solver_name,
        bootstrap_with=cnf.clauses,
        use_timer=True,
    ) as solver:
        if conflict_budget is None:
            satisfiable = solver.solve()
        else:
            solver.conf_budget(conflict_budget)
            satisfiable = solver.solve_limited()
        model = solver.get_model() if satisfiable is True else None
        statistics: dict[str, object] = {
            "variant": variant,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "python_sat": pysat.__version__,
            "solver": solver_name,
            "conflict_budget": conflict_budget,
            "solver_time_seconds": solver.time_accum(),
            "accumulated_stats": solver.accum_stats(),
            "variables": pool.top,
            "clauses": len(cnf.clauses),
            "cnf_sha256": formula_sha256,
            "candidate_point_variables": len(points),
            "candidate_K_edge_variables": len(k_edge),
            "candidate_full_overlap_variables": len(full_overlap),
        }
    status = (
        "SAT_WEAKENED_MODEL"
        if satisfiable is True
        else "UNSAT_UNVERIFIED"
        if satisfiable is False
        else "UNKNOWN_BUDGET_EXHAUSTED"
    )
    candidate = (
        candidate_from_model(
            size3_count=size3_count,
            root_mode=root_mode,
            variant=variant,
            points=points,
            selected=selected,
            k_edge=k_edge,
            model=model,
            solver_statistics=statistics,
        )
        if model is not None
        else None
    )
    return status, statistics, candidate


def scan_all_branches(
    conflict_budget: int | None,
    solver_name: str,
) -> dict[str, object]:
    rows = []
    for size3_count, root_mode in SCAN_BRANCHES:
        status, statistics, candidate = solve(
            size3_count,
            root_mode,
            conflict_budget,
            solver_name,
            "full",
        )
        rows.append(
            {
                "size3_point_count": size3_count,
                "root_mode": root_mode,
                "status": status,
                "proof_trace_status": "NOT_EMITTED",
                "statistics": statistics,
                "candidate_validation": (
                    validate_candidate(candidate)
                    if candidate is not None
                    else None
                ),
            }
        )
        print(
            f"m={size3_count} root={root_mode} status={status} "
            f"conflicts={statistics['accumulated_stats'].get('conflicts')} "
            f"time={statistics['solver_time_seconds']}",
            file=sys.stderr,
            flush=True,
        )
    all_unsat = all(row["status"] == "UNSAT_UNVERIFIED" for row in rows)
    result = {
        "schema": "conway99-wave13-n3-45-active-local-sat-scan-v1",
        "status": (
            "COMPLETE_BRANCH_COVER_UNSAT_UNVERIFIED"
            if all_unsat
            else "BRANCH_COVER_HAS_SURVIVOR_OR_UNKNOWN"
        ),
        "branch_cover": [list(branch) for branch in SCAN_BRANCHES],
        "branch_count": len(rows),
        "branches": rows,
        "cover_justification": [
            "point-incidence parity makes the number m of size-three points odd",
            "the exact local modes are 111,122,222,223",
            "m=13 and m=15 have no integer incidence signatures",
            "a root of type 111,122,222,223 needs at least 1,3,4,5 size-three points respectively",
            "the sole m=11 incidence signature uses only root types 222 and 223",
            "the named root point and each rooted representative use only the full active-label relabeling action",
            "no automorphism of a completed graph is assumed",
        ],
        "proof_boundary": (
            "solver UNSAT returns have no emitted or independently checked "
            "proof trace and are not nonexistence certificates"
        ),
        "proof_trace_status": "NOT_EMITTED",
        "builder_source_sha256": source_sha256(),
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty_status": "UNKNOWN",
    }
    semantic = {
        "schema": result["schema"],
        "status": result["status"],
        "branch_cover": result["branch_cover"],
        "branches": [
            {
                "size3_point_count": row["size3_point_count"],
                "root_mode": row["root_mode"],
                "status": row["status"],
                "proof_trace_status": row["proof_trace_status"],
                "variables": row["statistics"]["variables"],
                "clauses": row["statistics"]["clauses"],
                "cnf_sha256": row["statistics"]["cnf_sha256"],
            }
            for row in rows
        ],
        "proof_trace_status": result["proof_trace_status"],
        "builder_source_sha256": result["builder_source_sha256"],
        "claim_label": result["claim_label"],
        "target_result": result["target_result"],
        "novelty_status": result["novelty_status"],
    }
    result["semantic_sha256"] = sha256_bytes(canonical_json_bytes(semantic))
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size3", type=int, choices=ALLOWED_SIZE3_COUNTS)
    parser.add_argument("--root-mode", choices=ROOT_MODES)
    parser.add_argument("--variant", choices=SCOUT_VARIANTS, default="full")
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--conflict-budget", type=int)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--scan-output", type=Path)
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)

    if arguments.conflict_budget is not None and arguments.conflict_budget < 1:
        parser.error("--conflict-budget must be positive")
    if arguments.validate is not None:
        candidate = json.loads(arguments.validate.read_text(encoding="utf-8"))
        result = (
            validate_weakened_candidate(candidate)
            if candidate.get("schema")
            == DIAGNOSTIC_CANDIDATE_SCHEMA
            else validate_candidate(candidate)
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if arguments.scan:
        if arguments.size3 is not None or arguments.root_mode is not None:
            parser.error("--scan cannot be combined with --size3/--root-mode")
        if arguments.candidate is not None:
            parser.error("--scan cannot write one --candidate")
        if arguments.variant != "full":
            parser.error("--scan uses the full variant only")
        scan = scan_all_branches(
            arguments.conflict_budget,
            arguments.solver,
        )
        rendered = json.dumps(scan, indent=2, sort_keys=True) + "\n"
        if arguments.scan_output is not None:
            arguments.scan_output.parent.mkdir(parents=True, exist_ok=True)
            arguments.scan_output.write_text(
                rendered, encoding="utf-8", newline="\n"
            )
        print(rendered, end="")
        return 0
    if arguments.size3 is None:
        parser.error("--size3 is required unless --validate is used")
    if arguments.root_mode is None:
        parser.error("--root-mode is required unless --validate is used")
    status, statistics, candidate = solve(
        arguments.size3,
        arguments.root_mode,
        arguments.conflict_budget,
        arguments.solver,
        arguments.variant,
    )
    if arguments.candidate is not None:
        if candidate is None:
            raise SystemExit("--candidate requested but no SAT model was found")
        arguments.candidate.parent.mkdir(parents=True, exist_ok=True)
        arguments.candidate.write_bytes(candidate_json_bytes(candidate))
    output = {
        "status": status,
        "size3_point_count": arguments.size3,
        "root_mode": arguments.root_mode,
        "variant": arguments.variant,
        "statistics": statistics,
        "candidate": (
            str(arguments.candidate).replace("\\", "/")
            if arguments.candidate is not None and candidate is not None
            else None
        ),
        "candidate_validation": (
            (
                validate_candidate(candidate)
                if candidate["variant"] == "full"
                else validate_weakened_candidate(candidate)
            )
            if candidate is not None
            else None
        ),
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
    }
    if arguments.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(status)
        print("size3_point_count", arguments.size3)
        print("root_mode", arguments.root_mode)
        print("variant", arguments.variant)
        print("variables", statistics["variables"])
        print("clauses", statistics["clauses"])
        print("solver_time_seconds", statistics["solver_time_seconds"])
        if candidate is not None:
            if candidate["variant"] == "full":
                validation = validate_candidate(candidate)
                print(validation["status"])
                print(
                    "semantic_sha256",
                    validation["semantic_sha256"],
                )
            else:
                validation = validate_weakened_candidate(candidate)
                print(
                    "weakened_candidate_diagnostics",
                    json.dumps(validation, sort_keys=True),
                )
        print("claim_label CANDIDATE")
        print("target_result UNKNOWN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
