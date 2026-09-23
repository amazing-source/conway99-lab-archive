#!/usr/bin/env python3
"""Deterministic bounded SAT exploration for conditional ``n3=51``.

Only the inherited active-label relaxation is encoded.  Positive assignments
are finite ``CANDIDATE`` objects.  Negative solver returns are explicitly
non-evidentiary because no proof trace is emitted or checked.
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

from wave16_n3_51_profiles import (
    STARTING_COMMIT,
    TARGET_N3,
    canonical_json_bytes,
    file_sha256,
    k_degrees,
    sha256_bytes,
    surviving_branches,
    surviving_profile_rows,
)


FULL = "full"
SOURCE_PATH = Path("code/wave16_n3_51_active_sat.py")
PROFILE_SOURCE_PATH = Path("code/wave16_n3_51_profiles.py")
PROFILE_ARTIFACT_PATH = Path(
    "attempts/wave16-n3-51-computation/n3-51-profile-census.json"
)

ENCODED_PREMISES = [
    (
        "exactly three selected non-singleton point sets pass "
        "through each active label"
    ),
    "all selected point sizes are two or three",
    "the selected point family is linear",
    "F is exactly the union of selected point-clique edges",
    "every selected point is a clique in K",
    "every F-triangle is its selected size-three point",
    (
        "meeting crossings have two-sided L-degrees in {0,2}: "
        "singleton-side crossings are L-empty and 2-by-2 "
        "crossings are L-empty or L-complete"
    ),
    (
        "full 2-by-2 L-overlap counts obey the inherited "
        "fixed-point upper cap at each selected triple"
    ),
    "every active label has its exact profile-specific K-degree",
]

UNENCODED_PREMISES = [
    "inactive point sets and inactive graph vertices",
    "which disjoint selected points are adjacent original vertices",
    "fixed support contributed by disjoint point sets",
    "equality completion of every fixed-point support sum",
    "the 693-vertex H graph",
    "a 99-vertex adjacency matrix",
    "global SRG lambda/mu equations",
]


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
    specs = {}
    for row in surviving_profile_rows():
        q_values = tuple(map(int, row["q_values"]))
        spec = ProfileSpec(
            profile_id=str(row["profile_id"]),
            q_values=q_values,
            k_degrees=k_degrees(q_values),
        )
        specs[spec.profile_id] = spec
    return specs


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


def build_instance(spec: ProfileSpec) -> Instance:
    started = time.perf_counter()
    points = all_points(spec.order)
    edges = all_edges(spec.order)
    pool = IDPool()
    selected = {
        point: pool.id(("point", tuple(sorted(point))))
        for point in points
    }
    k_edge = {
        item: pool.id(("K", item)) for item in edges
    }
    f_edge = {
        item: pool.id(("F", item)) for item in edges
    }
    full_overlap: dict[
        tuple[frozenset[int], frozenset[int]], int
    ] = {}
    cnf = CNF()

    for vertex in range(spec.order):
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

    for item in edges:
        owners = [
            selected[point]
            for point in points
            if set(item) <= point
        ]
        add_at_most(cnf, pool, owners, 1)
        for owner in owners:
            cnf.append([-owner, f_edge[item]])
        cnf.append([-f_edge[item], *owners])

    for point in points:
        for item in itertools.combinations(sorted(point), 2):
            cnf.append([-selected[point], k_edge[item]])

    for triple in itertools.combinations(range(spec.order), 3):
        ab, ac, bc = itertools.combinations(triple, 2)
        cnf.append(
            [
                -f_edge[ab],
                -f_edge[ac],
                -f_edge[bc],
                selected[frozenset(triple)],
            ]
        )

    triples = tuple(
        point for point in points if len(point) == 3
    )
    overlaps_by_point: dict[frozenset[int], list[int]] = {
        point: [] for point in triples
    }
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
            if (
                len(left_external) == 1
                or len(right_external) == 1
            ):
                for literal in crossing:
                    cnf.append([*guard, literal])
                continue

            first = crossing[0]
            for literal in crossing[1:]:
                cnf.append([*guard, -first, literal])
                cnf.append([*guard, first, -literal])

            witness = pool.id(
                (
                    "full_L_overlap",
                    tuple(sorted(left)),
                    tuple(sorted(right)),
                )
            )
            full_overlap[(left, right)] = witness
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

    for point in triples:
        cap = (
            sum(spec.q_values[vertex] for vertex in point)
            // 2
        )
        add_at_most(
            cnf,
            pool,
            overlaps_by_point[point],
            cap,
        )

    for vertex, degree in enumerate(spec.k_degrees):
        add_equals(
            cnf,
            pool,
            (
                k_edge[edge(vertex, other)]
                for other in range(spec.order)
                if other != vertex
            ),
            degree,
        )

    return Instance(
        spec=spec,
        cnf=cnf,
        pool=pool,
        points=points,
        selected=selected,
        k_edge=k_edge,
        f_edge=f_edge,
        full_overlap=full_overlap,
        build_seconds=time.perf_counter() - started,
    )


def canonical_root(
    spec: ProfileSpec,
    root_q3_count: int,
) -> frozenset[int]:
    if not 0 <= root_q3_count <= min(3, spec.q3_count):
        raise ValueError("invalid q=3 root multiplicity")
    q2_needed = 3 - root_q3_count
    if q2_needed > spec.q2_count:
        raise ValueError("not enough q=2 labels")
    root = frozenset(
        (
            *range(q2_needed),
            *range(
                spec.q2_count,
                spec.q2_count + root_q3_count,
            ),
        )
    )
    if len(root) != 3:
        raise AssertionError("canonical root has wrong size")
    return root


def branch_assumptions(
    instance: Instance,
    branch_id: str,
) -> tuple[int, ...]:
    triples = tuple(
        point for point in instance.points if len(point) == 3
    )
    if branch_id == "no-size3":
        return tuple(
            -instance.selected[point] for point in triples
        )
    prefix = "root-q3x"
    if not branch_id.startswith(prefix):
        raise ValueError(f"unknown branch {branch_id!r}")
    root = canonical_root(
        instance.spec,
        int(branch_id.removeprefix(prefix)),
    )
    return (instance.selected[root],)


def branch_description(
    spec: ProfileSpec,
    branch_id: str,
) -> dict[str, object]:
    if branch_id == "no-size3":
        return {
            "branch_id": branch_id,
            "root_q3_count": None,
            "root_point": None,
            "root_q_values": None,
            "normalization": (
                "all selected size-three points are absent"
            ),
        }
    count = int(branch_id.removeprefix("root-q3x"))
    root = canonical_root(spec, count)
    return {
        "branch_id": branch_id,
        "root_q3_count": count,
        "root_point": sorted(root),
        "root_q_values": sorted(
            spec.q_values[vertex] for vertex in root
        ),
        "normalization": (
            "one selected triple is named using only permutations "
            "within the equal-q label classes; no completed-graph "
            "automorphism is assumed"
        ),
    }


def materialized_cnf_sha256(
    instance: Instance,
    assumptions: Sequence[int],
) -> str:
    digest = hashlib.sha256()
    clause_count = len(instance.cnf.clauses) + len(assumptions)
    digest.update(
        (
            f"p cnf {instance.pool.top} {clause_count}\n"
        ).encode("ascii")
    )
    for clause in instance.cnf.clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    for literal in assumptions:
        digest.update(f"{literal} 0\n".encode("ascii"))
    return digest.hexdigest()


def vertex_degrees(
    order: int,
    graph_edges: Iterable[tuple[int, int]],
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
    incidence = Counter(
        vertex for point in points for vertex in point
    )
    owners: dict[tuple[int, int], list[int]] = {
        item: [] for item in all_edges(spec.order)
    }
    missing_clique_edges = []
    for index, point in enumerate(points):
        for item in itertools.combinations(sorted(point), 2):
            owners[item].append(index)
            if item not in k_edges:
                missing_clique_edges.append(item)

    point_set = set(points)
    berge_triangles = []
    for triple in itertools.combinations(range(spec.order), 3):
        pair_items = tuple(itertools.combinations(triple, 2))
        if all(owners[item] for item in pair_items):
            if frozenset(triple) not in point_set:
                berge_triangles.append(list(triple))

    meeting_count = 0
    crossing_violations = []
    full_overlaps: list[list[list[int]]] = []
    overlap_degree: Counter[frozenset[int]] = Counter()
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
                overlap_degree[left] += 1
                overlap_degree[right] += 1
                full_overlaps.append(
                    [sorted(left), sorted(right)]
                )

    overlap_cap_violations = []
    for point in points:
        if len(point) != 3:
            continue
        cap = (
            sum(spec.q_values[vertex] for vertex in point)
            // 2
        )
        observed = overlap_degree[point]
        if observed > cap:
            overlap_cap_violations.append(
                {
                    "point": sorted(point),
                    "observed": observed,
                    "cap": cap,
                }
            )

    return {
        "point_count": len(points),
        "size2_point_count": sum(
            len(point) == 2 for point in points
        ),
        "size3_point_count": sum(
            len(point) == 3 for point in points
        ),
        "incidence_degrees": [
            incidence[vertex] for vertex in range(spec.order)
        ],
        "linear_pair_owner_violation_count": sum(
            len(indices) > 1 for indices in owners.values()
        ),
        "missing_point_clique_edges": [
            list(item)
            for item in sorted(set(missing_clique_edges))
        ],
        "k_edge_count": len(k_edges),
        "k_degree_sequence": list(
            vertex_degrees(spec.order, k_edges)
        ),
        "common_point_Berge_triangle_count": len(
            berge_triangles
        ),
        "common_point_Berge_triangles": berge_triangles,
        "meeting_crossings_checked": meeting_count,
        "meeting_crossing_violation_count": len(
            crossing_violations
        ),
        "meeting_crossing_violations": crossing_violations,
        "full_L_overlap_count": len(full_overlaps),
        "full_L_overlaps": full_overlaps,
        "overlap_cap_violation_count": len(
            overlap_cap_violations
        ),
        "overlap_cap_violations": overlap_cap_violations,
    }


def source_provenance() -> dict[str, str]:
    paths = (
        SOURCE_PATH,
        PROFILE_SOURCE_PATH,
        PROFILE_ARTIFACT_PATH,
    )
    return {
        path.as_posix(): file_sha256(path) for path in paths
    }


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
    branch = branch_description(instance.spec, branch_id)
    core = {
        "starting_git_commit": STARTING_COMMIT,
        "source_provenance": source_provenance(),
        "profile_id": instance.spec.profile_id,
        "q_values": list(instance.spec.q_values),
        "branch": branch,
        "point_sets": [sorted(point) for point in points],
        "K_edges": [list(item) for item in sorted(k_edges)],
        "formula_materialized_dimacs_sha256": formula[
            "materialized_dimacs_sha256"
        ],
        "encoded_premises_sha256": formula[
            "encoded_premises_sha256"
        ],
    }
    return {
        "schema": (
            "conway99-wave16-n3-51-active-local-candidate-v1"
        ),
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "conditional_n3_51_exclusion": "UNKNOWN",
        "novelty": "UNKNOWN",
        "scope": "active-label auxiliary object only",
        "target_n3": TARGET_N3,
        "starting_git_commit": STARTING_COMMIT,
        "source_provenance": source_provenance(),
        "profile_id": instance.spec.profile_id,
        "active_order": instance.spec.order,
        "q_values": list(instance.spec.q_values),
        "k_degree_targets": list(instance.spec.k_degrees),
        "branch": branch,
        "variant": FULL,
        "encoded_premises": ENCODED_PREMISES,
        "unencoded_premises": UNENCODED_PREMISES,
        "symmetry_boundary": (
            "q labels are sorted; a positive root branch uses only "
            "permutations inside equal-q classes; no completed-graph "
            "automorphism is assumed"
        ),
        "point_sets": [sorted(point) for point in points],
        "K_edges": [list(item) for item in sorted(k_edges)],
        "diagnostics": assignment_diagnostics(
            instance.spec,
            points,
            k_edges,
        ),
        "semantic_core": core,
        "semantic_sha256": sha256_bytes(
            canonical_json_bytes(core)
        ),
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
    formula = {
        "builder_source": SOURCE_PATH.as_posix(),
        "builder_source_sha256": file_sha256(SOURCE_PATH),
        "profile_source": PROFILE_SOURCE_PATH.as_posix(),
        "profile_source_sha256": file_sha256(
            PROFILE_SOURCE_PATH
        ),
        "encoded_premises_sha256": sha256_bytes(
            canonical_json_bytes(ENCODED_PREMISES)
        ),
        "variable_count": instance.pool.top,
        "base_clause_count": len(instance.cnf.clauses),
        "branch_unit_count": len(assumptions),
        "materialized_clause_count": (
            len(instance.cnf.clauses) + len(assumptions)
        ),
        "materialized_dimacs_sha256": (
            materialized_cnf_sha256(instance, assumptions)
        ),
        "branch_units_are_solver_assumptions": True,
        "build_seconds": instance.build_seconds,
    }
    timer_fired = threading.Event()
    normalized = solver_name.lower()
    interrupt_supported = not (
        normalized.startswith("cadical")
        or normalized.startswith("cd")
    )
    started = time.perf_counter()
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

            timer = threading.Timer(
                time_limit_seconds,
                interrupt,
            )
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
        elapsed = time.perf_counter() - started
        statistics = solver.accum_stats()
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
    return (
        {
            "profile_id": instance.spec.profile_id,
            "branch": branch_description(
                instance.spec,
                branch_id,
            ),
            "variant": FULL,
            "status": status,
            "evidentiary_status": (
                "POSITIVE_ASSIGNMENT_REQUIRES_EXACT_VALIDATION"
                if status == "SAT_CANDIDATE"
                else "NON_EVIDENTIARY_NO_CHECKED_PROOF_TRACE"
            ),
            "formula": formula,
            "solver": {
                "name": solver_name,
                "conflict_budget": conflict_budget,
                "wall_timeout_seconds_requested": (
                    time_limit_seconds
                ),
                "wall_timeout_enforced": (
                    time_limit_seconds > 0
                    and interrupt_supported
                ),
                "timer_fired": timer_fired.is_set(),
                "elapsed_seconds": elapsed,
                "statistics": statistics,
                "proof_trace_emitted": False,
                "proof_trace_checked": False,
            },
        },
        model,
    )


def candidate_filename(
    profile_name: str,
    branch_id: str,
) -> str:
    return (
        f"n3-51-{profile_name}-{branch_id}-"
        "active-local-candidate.json"
    )


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def run_scan(args: argparse.Namespace) -> dict[str, object]:
    specs = profile_specs()
    cover = surviving_branches()
    results = []
    candidate_paths = []
    current_profile: str | None = None
    instance: Instance | None = None
    for branch in cover:
        profile_name = str(branch["profile_id"])
        branch_id = str(branch["branch_id"])
        if current_profile != profile_name:
            instance = build_instance(specs[profile_name])
            current_profile = profile_name
        if instance is None:
            raise AssertionError("instance was not built")
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
                / candidate_filename(profile_name, branch_id)
            )
            candidate = candidate_from_model(
                instance,
                branch_id,
                model,
                record["formula"],
            )
            write_json(candidate_path, candidate)
            record["candidate_path"] = (
                candidate_path.as_posix()
            )
            record["candidate_file_sha256"] = file_sha256(
                candidate_path
            )
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
                    "variables": record["formula"][
                        "variable_count"
                    ],
                    "clauses": record["formula"][
                        "materialized_clause_count"
                    ],
                    "elapsed_seconds": record["solver"][
                        "elapsed_seconds"
                    ],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    projection = [
        {
            "profile_id": row["profile_id"],
            "branch_id": row["branch"]["branch_id"],
            "status": row["status"],
            "formula_sha256": row["formula"][
                "materialized_dimacs_sha256"
            ],
            "candidate_file_sha256": row.get(
                "candidate_file_sha256"
            ),
            "candidate_semantic_sha256": row.get(
                "candidate_semantic_sha256"
            ),
        }
        for row in results
    ]
    semantic = {
        "target_n3": TARGET_N3,
        "variant": FULL,
        "coverage": list(cover),
        "results": projection,
    }
    return {
        "schema": (
            "conway99-wave16-n3-51-active-local-scan-v1"
        ),
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "conditional_n3_51_exclusion": "UNKNOWN",
        "novelty": "UNKNOWN",
        "scope": (
            "complete seven-branch cover of the encoded active-local "
            "relaxation after the pending-audit finite reductions"
        ),
        "starting_git_commit": STARTING_COMMIT,
        "source_provenance": source_provenance(),
        "coverage_argument": [
            (
                "the independently enumerated q-multiset is sorted "
                "using arbitrary active-label names"
            ),
            (
                "the exact finite reductions leave the seven listed "
                "branches"
            ),
            (
                "an assignment either has no selected triple or has "
                "a selected triple of an enumerated q-composition"
            ),
            (
                "equal-q class permutations name one such triple "
                "without assuming a completed-graph automorphism"
            ),
        ],
        "encoded_premises": ENCODED_PREMISES,
        "unencoded_premises": UNENCODED_PREMISES,
        "negative_result_policy": (
            "UNSAT, budget, and timeout returns have no force "
            "without an emitted and independently checked proof trace"
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
        "semantic_sha256": sha256_bytes(
            canonical_json_bytes(semantic)
        ),
    }


def run_single(args: argparse.Namespace) -> dict[str, object]:
    spec = profile_specs()[args.profile]
    instance = build_instance(spec)
    record, model = solve_branch(
        instance,
        args.branch,
        solver_name=args.solver,
        conflict_budget=args.conflict_budget,
        time_limit_seconds=args.time_limit,
    )
    if model is not None and args.candidate is not None:
        candidate = candidate_from_model(
            instance,
            args.branch,
            model,
            record["formula"],
        )
        write_json(args.candidate, candidate)
        record["candidate_path"] = args.candidate.as_posix()
        record["candidate_file_sha256"] = file_sha256(
            args.candidate
        )
        record["candidate_semantic_sha256"] = candidate[
            "semantic_sha256"
        ]
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scan", action="store_true")
    mode.add_argument("--single", action="store_true")
    parser.add_argument(
        "--profile",
        choices=tuple(profile_specs()),
        default="r17-q2x17",
    )
    parser.add_argument("--branch", default="root-q3x0")
    parser.add_argument("--solver", default="glucose42")
    parser.add_argument(
        "--conflict-budget",
        type=int,
        default=50_000,
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=10.0,
    )
    parser.add_argument(
        "--candidate-dir",
        type=Path,
        default=Path("attempts/wave16-n3-51-computation"),
    )
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--scan-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = run_scan(args) if args.scan else run_single(args)
    if args.scan and args.scan_output is not None:
        write_json(args.scan_output, output)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
