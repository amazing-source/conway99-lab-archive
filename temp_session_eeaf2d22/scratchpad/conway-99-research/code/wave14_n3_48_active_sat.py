#!/usr/bin/env python3
"""Deterministic PySAT scouts for the conditional ``n3=48`` active frontier.

The formulas cover only the active-label auxiliary object inherited from the
audited Wave 6--13 framework.  They do not encode a completed automorphism or
a 99-vertex graph.  SAT assignments are exported as finite active-local
certificates.  UNSAT and bounded/timeout returns are explicitly
non-evidentiary because this program emits no checked proof traces.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
import threading
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import pysat
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

from wave14_n3_48_profiles import (
    TARGET_N3,
    branch_cover,
    canonical_json_bytes,
    k_degrees,
    profile_id,
    sha256_bytes,
    surviving_profile_rows,
)


FULL = "full"
NO_COMMON_POINT_CONTROL = "no_common_point_control"
K_DEGREE_UPPER_CONTROL = "k_degree_upper_control"
VARIANTS = (FULL, NO_COMMON_POINT_CONTROL, K_DEGREE_UPPER_CONTROL)


@dataclass(frozen=True)
class ProfileSpec:
    profile_id: str
    q_values: tuple[int, ...]
    k_degrees: tuple[int, ...]

    @property
    def order(self) -> int:
        return len(self.q_values)

    @property
    def q2_count(self) -> int:
        return self.q_values.count(2)

    @property
    def q3_count(self) -> int:
        return self.q_values.count(3)


@dataclass
class Instance:
    spec: ProfileSpec
    variant: str
    cnf: CNF
    pool: IDPool
    points: tuple[frozenset[int], ...]
    selected: dict[frozenset[int], int]
    k_edge: dict[tuple[int, int], int]
    f_edge: dict[tuple[int, int], int]
    full_overlap: dict[
        tuple[frozenset[int], frozenset[int]], int
    ]
    build_seconds: float


def profile_specs() -> dict[str, ProfileSpec]:
    output = {}
    for row in surviving_profile_rows():
        q_values = tuple(map(int, row["q_values"]))
        spec = ProfileSpec(
            profile_id=str(row["profile_id"]),
            q_values=q_values,
            k_degrees=k_degrees(q_values),
        )
        output[spec.profile_id] = spec
    return output


def edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise ValueError("loops are not edges")
    return (left, right) if left < right else (right, left)


def all_edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


def all_points(order: int) -> tuple[frozenset[int], ...]:
    return tuple(
        frozenset(point)
        for size in (2, 3)
        for point in itertools.combinations(range(order), size)
    )


def add_equals(
    cnf: CNF,
    pool: IDPool,
    literals: Iterable[int],
    bound: int,
) -> None:
    values = list(literals)
    encoded = CardEnc.equals(
        lits=values,
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


def build_instance(spec: ProfileSpec, variant: str = FULL) -> Instance:
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}")
    started = time.perf_counter()
    order = spec.order
    points = all_points(order)
    edges = all_edges(order)
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

    # Exactly three non-singleton indexed point sets pass through each label.
    for vertex in range(order):
        add_equals(
            cnf,
            pool,
            (
                selected[point]
                for point in points
                if vertex in point
            ),
            3,
        )

    # Point-family linearity and F as the exact union of point-clique edges.
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

    # In a linear point family, the common-point rule is exactly that every
    # F-triangle is owned by its selected size-three point.
    if variant != NO_COMMON_POINT_CONTROL:
        for triple in itertools.combinations(range(order), 3):
            ab, ac, bc = itertools.combinations(triple, 2)
            cnf.append(
                [
                    -f_edge[ab],
                    -f_edge[ac],
                    -f_edge[bc],
                    selected[frozenset(triple)],
                ]
            )
    else:
        # Require a real violation, so a positive weakened control cannot
        # accidentally satisfy the omitted common-point premise.
        berge_witnesses = []
        for triple in itertools.combinations(range(order), 3):
            triple_point = frozenset(triple)
            ab, ac, bc = itertools.combinations(triple, 2)
            witness = pool.id(("unowned_F_triangle", triple))
            berge_witnesses.append(witness)
            cnf.append([-witness, f_edge[ab]])
            cnf.append([-witness, f_edge[ac]])
            cnf.append([-witness, f_edge[bc]])
            cnf.append([-witness, -selected[triple_point]])
            cnf.append(
                [
                    -f_edge[ab],
                    -f_edge[ac],
                    -f_edge[bc],
                    selected[triple_point],
                    witness,
                ]
            )
        cnf.append(berge_witnesses)

    size3_points = tuple(point for point in points if len(point) == 3)
    overlaps_by_point: dict[frozenset[int], list[int]] = {
        point: [] for point in size3_points
    }

    # Exact meeting-crossing rule.  With a singleton external side the
    # L-crossing is empty.  A 2-by-2 crossing is empty or complete in L.
    for left_index, left in enumerate(points):
        for right in points[left_index + 1 :]:
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
            guard = [-selected[left], -selected[right]]
            if len(left_external) == 1 or len(right_external) == 1:
                for literal in crossing:
                    cnf.append([*guard, literal])
                continue

            first = crossing[0]
            for literal in crossing[1:]:
                cnf.append([*guard, -first, literal])
                cnf.append([*guard, first, -literal])

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
            overlaps_by_point[left].append(witness)
            overlaps_by_point[right].append(witness)
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

    # Each full overlap contributes four to the inherited fixed-point sum
    # 2*sum(q over P).  Other (disjoint/inactive) support is deliberately
    # unencoded, so only this necessary upper bound is imposed.
    for point in size3_points:
        cap = sum(spec.q_values[vertex] for vertex in point) // 2
        add_at_most(cnf, pool, overlaps_by_point[point], cap)

    # Exact profile degrees, except in the named weakened upper-bound control.
    for vertex, degree in enumerate(spec.k_degrees):
        literals = [
            k_edge[edge(vertex, other)]
            for other in range(order)
            if other != vertex
        ]
        if variant == K_DEGREE_UPPER_CONTROL:
            add_at_most(cnf, pool, literals, degree)
        else:
            add_equals(cnf, pool, literals, degree)
    if variant == K_DEGREE_UPPER_CONTROL:
        # Force the omitted equality to fail at a named ordinary label.
        if spec.q_values[0] != 2:
            raise AssertionError("canonical label zero must have q=2")
        literals = [
            k_edge[edge(0, other)]
            for other in range(order)
            if other != 0
        ]
        add_at_most(cnf, pool, literals, spec.k_degrees[0] - 1)

    return Instance(
        spec=spec,
        variant=variant,
        cnf=cnf,
        pool=pool,
        points=points,
        selected=selected,
        k_edge=k_edge,
        f_edge=f_edge,
        full_overlap=full_overlap,
        build_seconds=time.perf_counter() - started,
    )


def canonical_root(spec: ProfileSpec, root_q3_count: int) -> frozenset[int]:
    if not 0 <= root_q3_count <= min(3, spec.q3_count):
        raise ValueError("invalid root q=3 multiplicity")
    ordinary_needed = 3 - root_q3_count
    if ordinary_needed > spec.q2_count:
        raise ValueError("not enough q=2 labels for the root")
    ordinary = tuple(range(ordinary_needed))
    special = tuple(
        range(spec.q2_count, spec.q2_count + root_q3_count)
    )
    root = frozenset((*ordinary, *special))
    if len(root) != 3:
        raise AssertionError("canonical root does not have size three")
    return root


def branch_assumptions(
    instance: Instance, branch_id: str
) -> tuple[int, ...]:
    triples = tuple(
        point for point in instance.points if len(point) == 3
    )
    if branch_id == "no-size3":
        return tuple(-instance.selected[point] for point in triples)
    prefix = "root-q3x"
    if not branch_id.startswith(prefix):
        raise ValueError(f"unknown branch {branch_id!r}")
    root_q3_count = int(branch_id[len(prefix) :])
    root = canonical_root(instance.spec, root_q3_count)
    return (instance.selected[root],)


def branch_description(spec: ProfileSpec, branch_id: str) -> dict[str, object]:
    if branch_id == "no-size3":
        return {
            "branch_id": branch_id,
            "root_q3_count": None,
            "root_point": None,
            "normalization": (
                "no label symmetry is fixed; every size-three point is absent"
            ),
        }
    root_q3_count = int(branch_id.split("x", 1)[1])
    root = canonical_root(spec, root_q3_count)
    return {
        "branch_id": branch_id,
        "root_q3_count": root_q3_count,
        "root_point": sorted(root),
        "root_q_values": sorted(spec.q_values[vertex] for vertex in root),
        "normalization": (
            "choose one selected triple with this q-composition and map it "
            "to the displayed labels using only permutations within equal-q classes"
        ),
    }


def materialized_cnf_sha256(
    instance: Instance, assumptions: Sequence[int]
) -> str:
    digest = hashlib.sha256()
    clause_count = len(instance.cnf.clauses) + len(assumptions)
    digest.update(
        f"p cnf {instance.pool.top} {clause_count}\n".encode("ascii")
    )
    for clause in instance.cnf.clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    for literal in assumptions:
        digest.update(f"{literal} 0\n".encode("ascii"))
    return digest.hexdigest()


def vertex_degrees(
    order: int, graph_edges: Iterable[tuple[int, int]]
) -> tuple[int, ...]:
    values = [0] * order
    for left, right in graph_edges:
        values[left] += 1
        values[right] += 1
    return tuple(values)


def assignment_diagnostics(
    spec: ProfileSpec,
    points: Sequence[frozenset[int]],
    k_edges: frozenset[tuple[int, int]],
) -> dict[str, object]:
    order = spec.order
    point_index = {point: index for index, point in enumerate(points)}
    incidence = Counter(vertex for point in points for vertex in point)
    pair_owners: dict[tuple[int, int], list[int]] = {
        item: [] for item in all_edges(order)
    }
    missing_clique_edges = []
    for index, point in enumerate(points):
        for item in itertools.combinations(sorted(point), 2):
            pair_owners[item].append(index)
            if item not in k_edges:
                missing_clique_edges.append(item)

    berge_triangles = []
    point_set = set(points)
    for triple in itertools.combinations(range(order), 3):
        pair_items = tuple(itertools.combinations(triple, 2))
        if all(pair_owners[item] for item in pair_items):
            if frozenset(triple) not in point_set:
                berge_triangles.append(list(triple))

    crossing_violations = []
    full_overlaps: list[list[object]] = []
    full_overlap_degree: Counter[frozenset[int]] = Counter()
    meeting_count = 0
    for left_index, left in enumerate(points):
        for right in points[left_index + 1 :]:
            intersection = left & right
            if len(intersection) != 1:
                continue
            meeting_count += 1
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
                sum(
                    l_matrix[row][column]
                    for row in range(len(left_external))
                )
                for column in range(len(right_external))
            ]
            if any(
                value not in (0, 2)
                for value in (*row_degrees, *column_degrees)
            ):
                crossing_violations.append(
                    {
                        "left": sorted(left),
                        "right": sorted(right),
                        "row_degrees": row_degrees,
                        "column_degrees": column_degrees,
                    }
                )
            if (
                len(left) == len(right) == 3
                and sum(row_degrees) == 4
            ):
                full_overlap_degree[left] += 1
                full_overlap_degree[right] += 1
                full_overlaps.append(
                    [sorted(left), sorted(right)]
                )

    overlap_cap_violations = []
    for point in points:
        if len(point) != 3:
            continue
        cap = sum(spec.q_values[vertex] for vertex in point) // 2
        observed = full_overlap_degree[point]
        if observed > cap:
            overlap_cap_violations.append(
                {
                    "point": sorted(point),
                    "observed": observed,
                    "cap": cap,
                }
            )

    t_values = tuple(
        sum(len(point) == 3 and vertex in point for point in points)
        for vertex in range(order)
    )
    local_type_histogram = Counter(
        (
            tuple(sorted(spec.q_values[vertex] for vertex in point)),
            tuple(sorted(t_values[vertex] for vertex in point)),
        )
        for point in points
        if len(point) == 3
    )
    f_edges = tuple(
        item for item, owners in pair_owners.items() if owners
    )
    return {
        "point_count": len(points),
        "size2_point_count": sum(len(point) == 2 for point in points),
        "size3_point_count": sum(len(point) == 3 for point in points),
        "incidence_degrees": [
            incidence[vertex] for vertex in range(order)
        ],
        "linear_pair_owner_violations": sum(
            len(owners) > 1 for owners in pair_owners.values()
        ),
        "f_edge_count": len(f_edges),
        "missing_point_clique_edges": [
            list(item) for item in sorted(set(missing_clique_edges))
        ],
        "k_edge_count": len(k_edges),
        "k_degree_sequence": list(vertex_degrees(order, k_edges)),
        "common_point_Berge_triangle_count": len(berge_triangles),
        "common_point_Berge_triangles": berge_triangles,
        "meeting_crossings_checked": meeting_count,
        "meeting_crossing_violation_count": len(crossing_violations),
        "meeting_crossing_violations": crossing_violations,
        "full_L_overlap_count": len(full_overlaps),
        "full_L_overlaps": full_overlaps,
        "overlap_cap_violation_count": len(overlap_cap_violations),
        "overlap_cap_violations": overlap_cap_violations,
        "t_values": list(t_values),
        "size3_local_q_t_histogram": {
            (
                "q"
                + "".join(map(str, q_type))
                + "-t"
                + "".join(map(str, t_type))
            ): multiplicity
            for (q_type, t_type), multiplicity in sorted(
                local_type_histogram.items()
            )
        },
        "point_index_checksum": sha256_bytes(
            canonical_json_bytes(
                [
                    [index, sorted(point)]
                    for point, index in sorted(
                        point_index.items(), key=lambda item: item[1]
                    )
                ]
            )
        ),
    }


ENCODED_PREMISES = [
    "exactly three selected non-singleton point sets through each active label",
    "point sizes are two or three after the finite flower reductions",
    "point-family linearity",
    "F is the exact union of selected point-clique edges",
    "every selected point is a clique in K",
    "common-point/Berge-triangle rule unless named as the omitted control premise",
    "exact two-sided degree-{0,2} crossing for every pair of meeting selected points",
    "fixed-point upper cap on full-L overlaps at every selected size-three point",
    "profile-specific K degrees, or only upper bounds in the named control",
]

UNENCODED_PREMISES = [
    "inactive point sets and inactive graph vertices",
    "which disjoint active point sets represent adjacent original vertices",
    "fixed support contributed by disjoint point sets",
    "equality completion of every fixed-point support sum",
    "the 693-vertex H graph",
    "a 99-vertex adjacency matrix",
    "global SRG lambda/mu equations",
]


def candidate_from_model(
    instance: Instance,
    branch_id: str,
    model: Sequence[int],
    formula: dict[str, object],
) -> dict[str, object]:
    positive = {literal for literal in model if literal > 0}
    points = tuple(
        point
        for point in instance.points
        if instance.selected[point] in positive
    )
    k_edges = frozenset(
        item
        for item, variable in instance.k_edge.items()
        if variable in positive
    )
    diagnostics = assignment_diagnostics(instance.spec, points, k_edges)
    core = {
        "profile_id": instance.spec.profile_id,
        "q_values": list(instance.spec.q_values),
        "branch": branch_description(instance.spec, branch_id),
        "variant": instance.variant,
        "point_sets": [sorted(point) for point in points],
        "K_edges": [list(item) for item in sorted(k_edges)],
    }
    omitted = {
        FULL: None,
        NO_COMMON_POINT_CONTROL: "common-point/Berge-triangle rule",
        K_DEGREE_UPPER_CONTROL: "exact K-degree equality",
    }[instance.variant]
    return {
        "schema": "conway99-wave14-n3-48-active-local-candidate-v1",
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty": "UNKNOWN",
        "scope": "active-label auxiliary object only",
        "target_n3": TARGET_N3,
        "profile_id": instance.spec.profile_id,
        "active_order": instance.spec.order,
        "q_values": list(instance.spec.q_values),
        "k_degree_targets": list(instance.spec.k_degrees),
        "branch": branch_description(instance.spec, branch_id),
        "variant": instance.variant,
        "omitted_premise": omitted,
        "encoded_premises": ENCODED_PREMISES,
        "unencoded_premises": UNENCODED_PREMISES,
        "symmetry_boundary": (
            "q labels are sorted canonically; a positive root branch uses only "
            "permutations within equal-q label classes; no completed-graph "
            "automorphism is assumed"
        ),
        "point_sets": [sorted(point) for point in points],
        "K_edges": [list(item) for item in sorted(k_edges)],
        "diagnostics": diagnostics,
        "semantic_core": core,
        "semantic_sha256": sha256_bytes(canonical_json_bytes(core)),
        "formula": formula,
    }


def solve_branch(
    instance: Instance,
    branch_id: str,
    *,
    solver_name: str,
    conflict_budget: int,
    time_limit_seconds: float,
) -> tuple[dict[str, object], list[int] | None]:
    assumptions = branch_assumptions(instance, branch_id)
    formula_hash = materialized_cnf_sha256(instance, assumptions)
    formula = {
        "variable_count": instance.pool.top,
        "base_clause_count": len(instance.cnf.clauses),
        "branch_unit_count": len(assumptions),
        "materialized_clause_count": len(instance.cnf.clauses)
        + len(assumptions),
        "materialized_dimacs_sha256": formula_hash,
        "branch_units_are_solver_assumptions": True,
        "build_seconds": instance.build_seconds,
    }
    timer_fired = threading.Event()
    normalized_solver_name = solver_name.lower()
    # PySAT 1.9.dev7 exposes conflict budgets for CaDiCaL 1.9.5 but its
    # interrupt()/clear_interrupt() methods raise NotImplementedError.  Never
    # describe a wall timer as enforced on those wrappers.
    interrupt_supported = not (
        normalized_solver_name.startswith("cadical")
        or normalized_solver_name.startswith("cd")
    )
    solver_started = time.perf_counter()
    with Solver(
        name=solver_name,
        bootstrap_with=instance.cnf.clauses,
        use_timer=True,
    ) as solver:
        if conflict_budget > 0:
            solver.conf_budget(conflict_budget)

        timer: threading.Timer | None = None
        if time_limit_seconds > 0 and interrupt_supported:
            def interrupt() -> None:
                timer_fired.set()
                solver.interrupt()

            timer = threading.Timer(time_limit_seconds, interrupt)
            timer.daemon = True
            timer.start()
        try:
            result = solver.solve_limited(
                assumptions=list(assumptions),
                expect_interrupt=True,
            )
        finally:
            if timer is not None:
                timer.cancel()
        elapsed = time.perf_counter() - solver_started
        stats = solver.accum_stats()
        model = solver.get_model() if result is True else None
        if timer_fired.is_set() and interrupt_supported:
            solver.clear_interrupt()

    if result is True:
        status = "SAT_CANDIDATE"
    elif result is False:
        status = "UNSAT_UNVERIFIED"
    elif timer_fired.is_set():
        status = "TIMEOUT_UNKNOWN"
    else:
        status = "BUDGET_UNKNOWN"
    record = {
        "profile_id": instance.spec.profile_id,
        "branch": branch_description(instance.spec, branch_id),
        "variant": instance.variant,
        "status": status,
        "evidentiary_status": (
            "positive assignment requires exact validation"
            if status == "SAT_CANDIDATE"
            else "NON_EVIDENTIARY_NO_CHECKED_PROOF_TRACE"
        ),
        "formula": formula,
        "solver": {
            "name": solver_name,
            "conflict_budget": conflict_budget,
            "wall_timeout_seconds_requested": time_limit_seconds,
            "wall_timeout_enforced": (
                time_limit_seconds > 0 and interrupt_supported
            ),
            "timer_fired": timer_fired.is_set(),
            "elapsed_seconds": elapsed,
            "statistics": stats,
            "proof_trace_emitted": False,
            "proof_trace_checked": False,
        },
    }
    return record, model


def write_candidate(path: Path, candidate: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(candidate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def candidate_filename(
    profile_name: str, branch_id: str, variant: str
) -> str:
    return f"n3-48-{profile_name}-{branch_id}-{variant}-candidate.json"


def run_full_scan(args: argparse.Namespace) -> dict[str, object]:
    specs = profile_specs()
    cover = branch_cover()
    results = []
    candidate_paths = []
    current_profile = None
    instance = None
    for branch in cover:
        profile_name = str(branch["profile_id"])
        if profile_name != current_profile:
            instance = build_instance(specs[profile_name], FULL)
            current_profile = profile_name
        if instance is None:
            raise AssertionError("scan instance was not built")
        branch_id = str(branch["branch_id"])
        record, model = solve_branch(
            instance,
            branch_id,
            solver_name=args.solver,
            conflict_budget=args.conflict_budget,
            time_limit_seconds=args.time_limit,
        )
        if model is not None:
            candidate_path = (
                args.candidate_dir
                / candidate_filename(profile_name, branch_id, FULL)
            )
            candidate = candidate_from_model(
                instance,
                branch_id,
                model,
                record["formula"],
            )
            write_candidate(candidate_path, candidate)
            record["candidate_path"] = candidate_path.as_posix()
            record["candidate_semantic_sha256"] = candidate[
                "semantic_sha256"
            ]
            candidate_paths.append(candidate_path.as_posix())
        results.append(record)
        print(
            json.dumps(
                {
                    "profile_id": profile_name,
                    "branch_id": branch_id,
                    "status": record["status"],
                    "variables": record["formula"]["variable_count"],
                    "clauses": record["formula"]["materialized_clause_count"],
                    "elapsed_seconds": record["solver"]["elapsed_seconds"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    semantic_results = [
        {
            "profile_id": record["profile_id"],
            "branch_id": record["branch"]["branch_id"],
            "status": record["status"],
            "formula_sha256": record["formula"][
                "materialized_dimacs_sha256"
            ],
            "candidate_semantic_sha256": record.get(
                "candidate_semantic_sha256"
            ),
        }
        for record in results
    ]
    semantic = {
        "target_n3": TARGET_N3,
        "variant": FULL,
        "coverage": cover,
        "results": semantic_results,
    }
    return {
        "schema": "conway99-wave14-n3-48-active-local-scan-v1",
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty": "UNKNOWN",
        "scope": "complete branch cover of the encoded active-local relaxation",
        "coverage_argument": [
            "the q multiset is canonically sorted, using arbitrary active-label names",
            "an assignment either has no selected size-three point or has at least one",
            "a selected size-three point has one of the enumerated q=3 multiplicities",
            "permutations within equal-q classes act transitively on roots of a fixed composition",
            "no permutation is asserted to extend to an automorphism of a completed graph",
        ],
        "encoded_premises": ENCODED_PREMISES,
        "unencoded_premises": UNENCODED_PREMISES,
        "negative_result_policy": (
            "UNSAT and bounded/timeout solver returns are non-evidentiary "
            "without emitted and independently checked proof traces"
        ),
        "python": sys.version,
        "python_sat": pysat.__version__,
        "platform": platform.platform(),
        "solver_name": args.solver,
        "conflict_budget_per_branch": args.conflict_budget,
        "wall_timeout_seconds_per_branch": args.time_limit,
        "results": results,
        "candidate_paths": candidate_paths,
        "semantic": semantic,
        "semantic_sha256": sha256_bytes(canonical_json_bytes(semantic)),
    }


CONTROL_CASES = (
    (
        "r16-q2x16",
        "root-q3x0",
        NO_COMMON_POINT_CONTROL,
    ),
    (
        "r16-q2x16",
        "no-size3",
        K_DEGREE_UPPER_CONTROL,
    ),
)


def run_controls(args: argparse.Namespace) -> dict[str, object]:
    specs = profile_specs()
    results = []
    for profile_name, branch_id, variant in CONTROL_CASES:
        instance = build_instance(specs[profile_name], variant)
        record, model = solve_branch(
            instance,
            branch_id,
            solver_name=args.solver,
            conflict_budget=args.conflict_budget,
            time_limit_seconds=args.time_limit,
        )
        if model is not None:
            candidate_path = (
                args.candidate_dir
                / candidate_filename(profile_name, branch_id, variant)
            )
            candidate = candidate_from_model(
                instance,
                branch_id,
                model,
                record["formula"],
            )
            write_candidate(candidate_path, candidate)
            record["candidate_path"] = candidate_path.as_posix()
            record["candidate_semantic_sha256"] = candidate[
                "semantic_sha256"
            ]
        results.append(record)
        print(
            json.dumps(
                {
                    "profile_id": profile_name,
                    "branch_id": branch_id,
                    "variant": variant,
                    "status": record["status"],
                    "elapsed_seconds": record["solver"]["elapsed_seconds"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    semantic = {
        "target_n3": TARGET_N3,
        "controls": [
            {
                "profile_id": record["profile_id"],
                "branch_id": record["branch"]["branch_id"],
                "variant": record["variant"],
                "status": record["status"],
                "formula_sha256": record["formula"][
                    "materialized_dimacs_sha256"
                ],
                "candidate_semantic_sha256": record.get(
                    "candidate_semantic_sha256"
                ),
            }
            for record in results
        ],
    }
    return {
        "schema": "conway99-wave14-n3-48-positive-controls-v1",
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty": "UNKNOWN",
        "purpose": (
            "positive weakened assignments must violate exactly the named "
            "omitted premise while retaining the other encoded families"
        ),
        "results": results,
        "semantic": semantic,
        "semantic_sha256": sha256_bytes(canonical_json_bytes(semantic)),
    }


def run_single(args: argparse.Namespace) -> dict[str, object]:
    specs = profile_specs()
    spec = specs[args.profile]
    instance = build_instance(spec, args.variant)
    record, model = solve_branch(
        instance,
        args.branch,
        solver_name=args.solver,
        conflict_budget=args.conflict_budget,
        time_limit_seconds=args.time_limit,
    )
    if model is not None and args.candidate is not None:
        candidate = candidate_from_model(
            instance, args.branch, model, record["formula"]
        )
        write_candidate(args.candidate, candidate)
        record["candidate_path"] = args.candidate.as_posix()
        record["candidate_semantic_sha256"] = candidate[
            "semantic_sha256"
        ]
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scan", action="store_true")
    mode.add_argument("--controls", action="store_true")
    mode.add_argument("--single", action="store_true")
    parser.add_argument(
        "--profile",
        choices=tuple(profile_specs()),
        default="r16-q2x16",
    )
    parser.add_argument("--branch", default="root-q3x0")
    parser.add_argument("--variant", choices=VARIANTS, default=FULL)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--conflict-budget", type=int, default=250_000)
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument(
        "--candidate-dir",
        type=Path,
        default=Path("attempts/wave14-computation"),
    )
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--scan-output", type=Path)
    parser.add_argument("--control-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.scan:
        output = run_full_scan(args)
        path = args.scan_output
    elif args.controls:
        output = run_controls(args)
        path = args.control_output
    else:
        output = run_single(args)
        path = None
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(output, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
