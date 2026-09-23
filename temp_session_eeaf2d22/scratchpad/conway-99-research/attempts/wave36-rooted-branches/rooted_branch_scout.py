#!/usr/bin/env python3
"""Exact Wave 36 scouts for the five prism-free rooted branches.

The Wave 35 endpoint reduction fixes 84 residual nonedges and leaves normalized
N3 joint branches 4, 5, 8, 10, and 12.  Each surviving branch fixes six
triangles through coordinate 2.  If ``n3=4158``, then the graph contains no
induced triangular prism.  This program adds the corresponding clauses
forbidding a second triangle joined by a perfect matching to any of those six
fixed triangles.

The clauses use no additional automorphism assumption.  They are logical
consequences of ``P=0`` and the SRG equations: two disjoint triangles joined
by a perfect matching are automatically an induced triangular prism because
an extra cross edge would give an adjacent pair two common neighbors.

All embedded solver outcomes are discovery-only.  A SAT result is decoded to a
complete edge list and must pass an independent SRG checker.  An UNSAT result
does not count without a retained formula, proof, and independent replay.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path
from typing import Iterable, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CODE_ROOT = REPOSITORY_ROOT / "code"
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from matching_orbits import n3_joint_branch_decisions  # noqa: E402
from pysat.solvers import Solver  # noqa: E402
from sat_model import EncodedRootModel  # noqa: E402
from wave35_n3_endpoint_root_scout import (  # noqa: E402
    SURVIVING_BRANCHES,
    endpoint_edge_sha256,
    endpoint_edges,
)


FROZEN_COMMIT = "697cc02bcbe16b69aaf08822298e03c66329c64c"
ROOT_VERTEX = 0
COORDINATE_OFFSET = 1
RESIDUAL_OFFSET = 15
FULL_VERTEX_COUNT = 99

EdgeState = bool | int


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def full_edge_state(
    encoded: EncodedRootModel, first: int, second: int
) -> EdgeState:
    """Return a fixed truth value or a positive residual-edge literal."""

    if first == second:
        return False
    if first > second:
        first, second = second, first

    if first == ROOT_VERTEX:
        return COORDINATE_OFFSET <= second < RESIDUAL_OFFSET

    first_is_coordinate = first < RESIDUAL_OFFSET
    second_is_coordinate = second < RESIDUAL_OFFSET
    if first_is_coordinate and second_is_coordinate:
        first_coordinate = first - COORDINATE_OFFSET
        second_coordinate = second - COORDINATE_OFFSET
        return (
            first_coordinate // 2 == second_coordinate // 2
            and first_coordinate != second_coordinate
        )

    if first_is_coordinate:
        coordinate = first - COORDINATE_OFFSET
        label_index = second - RESIDUAL_OFFSET
        return coordinate in encoded.root.labels[label_index]

    first_label = first - RESIDUAL_OFFSET
    second_label = second - RESIDUAL_OFFSET
    return encoded.edge_literal(first_label, second_label)


def possible_neighbors(
    encoded: EncodedRootModel, vertex: int, excluded: frozenset[int]
) -> tuple[int, ...]:
    return tuple(
        other
        for other in range(FULL_VERTEX_COUNT)
        if other not in excluded
        and other != vertex
        and full_edge_state(encoded, vertex, other) is not False
    )


def branch_coordinate_triangles(
    encoded: EncodedRootModel, branch: int
) -> tuple[tuple[int, int, int], ...]:
    """Return the six branch-fixed triangles through coordinate 2."""

    decisions = n3_joint_branch_decisions(encoded.root, branch)
    fiber = set(encoded.root.containing(2))
    positive = tuple(
        sorted(
            edge
            for edge, present in decisions.items()
            if present and edge[0] in fiber and edge[1] in fiber
        )
    )
    if len(positive) != 6:
        raise AssertionError("joint branch did not fix six fiber-matching edges")
    triangles = tuple(
        (
            COORDINATE_OFFSET + 2,
            RESIDUAL_OFFSET + first,
            RESIDUAL_OFFSET + second,
        )
        for first, second in positive
    )
    for triangle in triangles:
        if any(
            full_edge_state(encoded, first, second) is False
            for first, second in itertools.combinations(triangle, 2)
        ):
            raise AssertionError("a declared coordinate triangle has a fixed nonedge")
    return triangles


def required_positive_variables(
    encoded: EncodedRootModel, edges: Iterable[tuple[int, int]]
) -> tuple[int, ...] | None:
    variables: set[int] = set()
    for first, second in edges:
        state = full_edge_state(encoded, first, second)
        if state is False:
            return None
        if state is not True:
            variables.add(int(state))
    return tuple(sorted(variables))


def fixed_triangle_prism_clauses(
    encoded: EncodedRootModel, triangle: Sequence[int]
) -> tuple[tuple[int, ...], ...]:
    """Forbid every prism whose first triangle is fixed.

    The three vertices of a prospective second triangle are assigned to the
    three fixed-triangle vertices according to their matching cross edges.
    Thus iterating the three neighbor lists covers all six possible matchings
    for every unordered second triangle without assuming graph symmetry.
    """

    frozen = tuple(triangle)
    if len(frozen) != 3 or len(set(frozen)) != 3:
        raise ValueError("triangle must contain three distinct vertices")
    excluded = frozenset(frozen)
    neighbor_lists = tuple(
        possible_neighbors(encoded, vertex, excluded) for vertex in frozen
    )
    clauses: set[tuple[int, ...]] = set()

    for matched in itertools.product(*neighbor_lists):
        if len(set(matched)) != 3:
            continue
        required_edges = (
            (frozen[0], matched[0]),
            (frozen[1], matched[1]),
            (frozen[2], matched[2]),
            (matched[0], matched[1]),
            (matched[0], matched[2]),
            (matched[1], matched[2]),
        )
        variables = required_positive_variables(encoded, required_edges)
        if variables is None:
            continue
        if not variables:
            raise AssertionError("the fixed scaffold already contains a prism")
        clauses.add(tuple(-variable for variable in variables))

    return tuple(sorted(clauses))


def endpoint_fixed_assignments(
    encoded: EncodedRootModel, branch: int
) -> dict[int, bool]:
    assignments = {
        encoded.edge_variables[edge]: False for edge in endpoint_edges(encoded.root)
    }
    indices = encoded.root.label_index()
    normalized_edge = tuple(
        sorted((indices[(0, 2)], indices[(2, 4)]))
    )
    assignments[encoded.edge_variables[normalized_edge]] = True
    for edge, present in n3_joint_branch_decisions(encoded.root, branch).items():
        literal = encoded.edge_variables[edge]
        prior = assignments.get(literal)
        if prior is not None and prior != present:
            raise AssertionError("surviving branch clashes with endpoint units")
        assignments[literal] = present
    return assignments


def clause_is_satisfied(
    clause: Sequence[int], assignments: dict[int, bool]
) -> bool:
    return any(
        assignments.get(abs(literal)) == (literal > 0)
        for literal in clause
        if abs(literal) in assignments
    )


def add_endpoint_and_branch(encoded: EncodedRootModel, branch: int) -> None:
    for edge in endpoint_edges(encoded.root):
        encoded.cnf.append([-encoded.edge_variables[edge]])
    encoded.add_n3_normalization()
    encoded.add_n3_joint_branch(branch)


def add_fixed_triangle_prism_constraints(
    encoded: EncodedRootModel, branch: int
) -> dict[str, object]:
    assignments = endpoint_fixed_assignments(encoded, branch)
    per_triangle: list[dict[str, object]] = []
    all_clauses: set[tuple[int, ...]] = set()
    for triangle in branch_coordinate_triangles(encoded, branch):
        clauses = fixed_triangle_prism_clauses(encoded, triangle)
        active = tuple(
            clause
            for clause in clauses
            if not clause_is_satisfied(clause, assignments)
        )
        all_clauses.update(active)
        per_triangle.append(
            {
                "triangle": list(triangle),
                "raw_clause_count": len(clauses),
                "active_after_fixed_units": len(active),
            }
        )
    for clause in sorted(all_clauses):
        encoded.cnf.append(list(clause))
    clause_lengths: dict[str, int] = {}
    for clause in all_clauses:
        key = str(len(clause))
        clause_lengths[key] = clause_lengths.get(key, 0) + 1
    return {
        "fixed_triangle_count": 6,
        "per_triangle": per_triangle,
        "deduplicated_active_clause_count": len(all_clauses),
        "clause_length_histogram": dict(
            sorted(clause_lengths.items(), key=lambda item: int(item[0]))
        ),
        "clause_catalog_sha256": sha256_text(
            canonical_json([list(clause) for clause in sorted(all_clauses)])
        ),
    }


def merge_model_with_fixed_assignments(
    model: Sequence[int], assignments: dict[int, bool]
) -> list[int]:
    merged = {abs(literal): literal > 0 for literal in model}
    for variable, value in assignments.items():
        prior = merged.get(variable)
        if prior is not None and prior != value:
            raise AssertionError("solver model contradicts a fixed assignment")
        merged[variable] = value
    return [
        variable if value else -variable
        for variable, value in sorted(merged.items())
    ]


def solve_native_model(
    encoded: EncodedRootModel, solver_name: str, conflict_budget: int
) -> tuple[bool | None, list[int] | None, dict[str, object]]:
    started = time.monotonic()
    with Solver(
        name=solver_name,
        bootstrap_with=encoded.cnf,
        use_timer=True,
    ) as solver:
        solver.conf_budget(conflict_budget)
        result = solver.solve_limited()
        model = solver.get_model() if result is True else None
        statistics: dict[str, object] = {
            "solver": solver_name,
            "conflict_budget": conflict_budget,
            "wall_seconds": time.monotonic() - started,
            "solver_seconds": solver.time_accum(),
            "accumulated_stats": solver.accum_stats(),
        }
    return result, model, statistics


def parse_branches(text: str) -> tuple[int, ...]:
    try:
        branches = tuple(int(part) for part in text.split(",") if part)
    except ValueError as error:
        raise argparse.ArgumentTypeError("branches must be comma-separated integers") from error
    if not branches or any(branch not in SURVIVING_BRANCHES for branch in branches):
        raise argparse.ArgumentTypeError(
            "branches must be selected from 4,5,8,10,12"
        )
    if len(branches) != len(set(branches)):
        raise argparse.ArgumentTypeError("branches must not repeat")
    return branches


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--branches",
        type=parse_branches,
        default=SURVIVING_BRANCHES,
        help="comma-separated subset of 4,5,8,10,12",
    )
    parser.add_argument(
        "--mode",
        choices=("baseline", "fixed-triangle-prisms"),
        default="fixed-triangle-prisms",
    )
    parser.add_argument("--conflict-budget", type=int, default=100_000)
    parser.add_argument(
        "--solver",
        default="gluecard4",
        choices=("minicard", "gluecard3", "gluecard4"),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--candidate-dir", type=Path)
    parser.add_argument(
        "--derive-only",
        action="store_true",
        help="build and hash every exact constraint family without calling a solver",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.conflict_budget < 1:
        raise SystemExit("--conflict-budget must be positive")
    started = time.monotonic()
    records: list[dict[str, object]] = []

    for branch in args.branches:
        branch_started = time.monotonic()
        encoded = EncodedRootModel.build(
            7, variant="compact", cardinality_backend="native"
        )
        add_endpoint_and_branch(encoded, branch)
        strengthening = None
        if args.mode == "fixed-triangle-prisms":
            strengthening = add_fixed_triangle_prism_constraints(encoded, branch)

        result = None
        model = None
        solver_record = None
        if args.derive_only:
            status = "NOT_RUN"
        else:
            result, model, solver_record = solve_native_model(
                encoded, args.solver, conflict_budget=args.conflict_budget
            )
            status = (
                "SAT_CANDIDATE"
                if result is True
                else "UNSAT_UNVERIFIED"
                if result is False
                else "BUDGET_UNKNOWN"
            )
        candidate_path = None
        candidate_sha256 = None
        if result is True and model is not None:
            merged_model = merge_model_with_fixed_assignments(
                model, endpoint_fixed_assignments(encoded, branch)
            )
            candidate = encoded.full_certificate(merged_model)
            candidate_text = json.dumps(candidate, indent=2, sort_keys=True) + "\n"
            candidate_sha256 = sha256_text(candidate_text)
            if args.candidate_dir:
                args.candidate_dir.mkdir(parents=True, exist_ok=True)
                candidate_path = args.candidate_dir / f"branch-{branch}.srg.json"
                candidate_path.write_text(
                    candidate_text, encoding="utf-8", newline="\n"
                )

        records.append(
            {
                "branch": branch,
                "status": status,
                "mode": args.mode,
                "encoding": encoded.statistics(),
                "strengthening": strengthening,
                "solver": solver_record,
                "wall_seconds": time.monotonic() - branch_started,
                "candidate_path": (
                    str(candidate_path.relative_to(REPOSITORY_ROOT))
                    if candidate_path is not None
                    else None
                ),
                "candidate_sha256": candidate_sha256,
            }
        )

    payload = {
        "format": "wave36-prism-free-rooted-branch-scout-v1",
        "role": "construction",
        "claim_label": "UNKNOWN",
        "git_commit": FROZEN_COMMIT,
        "scope": (
            "five exact normalized rooted branches under n3=4158 (P=0), "
            "with no completed-graph automorphism assumption"
        ),
        "mode": args.mode,
        "derive_only": args.derive_only,
        "conflict_budget_per_branch": args.conflict_budget,
        "endpoint_unit_count": 84,
        "endpoint_edge_catalog_sha256": endpoint_edge_sha256(
            endpoint_edges(EncodedRootModel.build(7).root)
        ),
        "branches": list(args.branches),
        "records": records,
        "wall_seconds": time.monotonic() - started,
        "limitations": [
            "BUDGET_UNKNOWN has no mathematical evidentiary value.",
            "UNSAT_UNVERIFIED needs a retained formula and independently checked proof.",
            "SAT_CANDIDATE needs independent complete-SRG and prism-free validation.",
            "The six fixed-triangle clause families are consequences of P=0 but do not encode every possible prism.",
        ],
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
