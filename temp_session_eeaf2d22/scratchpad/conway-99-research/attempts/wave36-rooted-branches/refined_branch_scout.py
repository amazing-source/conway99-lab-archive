#!/usr/bin/env python3
"""Bounded exact scout of the 33 endpoint-compatible refined N3 cases.

The previously verified oriented-common-neighbor cover refines the five
surviving joint branches into 33 cases.  This is a complete split conditional
on the published cover, the universal N3 occurrence, and ``n3=4158``.  Each
solver is fresh, and each case is imposed as an assumption on its exact parent
formula.  Learned clauses are not shared across cases.

Embedded Gluecard/MiniCard returns remain discovery-only: budget stops are
``UNKNOWN``; an ``UNSAT`` return needs a retained proof-producing formula and
independent proof replay; a SAT assignment needs independent graph checking.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CODE_ROOT = REPOSITORY_ROOT / "code"
ATTEMPT_ROOT = Path(__file__).resolve().parent
for import_root in (CODE_ROOT, ATTEMPT_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from pysat.solvers import Solver

from matching_orbits import (
    n3_refined_branch_specification,
    n3_refined_orbits,
)
from rooted_branch_scout import (
    FROZEN_COMMIT,
    SURVIVING_BRANCHES,
    add_endpoint_and_branch,
    add_fixed_triangle_prism_constraints,
    endpoint_edge_sha256,
    endpoint_edges,
    endpoint_fixed_assignments,
    merge_model_with_fixed_assignments,
    sha256_text,
)
from sat_model import EncodedRootModel


def refined_cases(
    encoded: EncodedRootModel, parent: int
) -> tuple[tuple[int, int, int], ...]:
    cases = []
    orbits = n3_refined_orbits()
    for refined_branch in range(1, len(orbits) + 1):
        _, refinement_edge, first_branch = n3_refined_branch_specification(
            encoded.root, refined_branch
        )
        if first_branch != parent:
            continue
        literal = encoded.edge_variables[refinement_edge]
        orbit_size = orbits[refined_branch - 1][2]
        cases.append((refined_branch, literal, orbit_size))
    return tuple(cases)


def parse_parents(text: str) -> tuple[int, ...]:
    try:
        parents = tuple(int(part) for part in text.split(",") if part)
    except ValueError as error:
        raise argparse.ArgumentTypeError("parents must be comma-separated integers") from error
    if not parents or any(parent not in SURVIVING_BRANCHES for parent in parents):
        raise argparse.ArgumentTypeError("parents must be selected from 4,5,8,10,12")
    if len(parents) != len(set(parents)):
        raise argparse.ArgumentTypeError("parents must not repeat")
    return parents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--parents",
        type=parse_parents,
        default=SURVIVING_BRANCHES,
        help="comma-separated subset of 4,5,8,10,12",
    )
    parser.add_argument("--conflict-budget", type=int, default=100_000)
    parser.add_argument(
        "--solver",
        default="gluecard4",
        choices=("minicard", "gluecard3", "gluecard4"),
    )
    parser.add_argument(
        "--without-fixed-triangle-prisms",
        action="store_true",
        help="omit the Wave 36 P=0 clause strengthening",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--candidate-dir", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.conflict_budget < 1:
        raise SystemExit("--conflict-budget must be positive")
    run_started = time.monotonic()
    parent_records: list[dict[str, object]] = []

    for parent in args.parents:
        encoded = EncodedRootModel.build(
            7, variant="compact", cardinality_backend="native"
        )
        add_endpoint_and_branch(encoded, parent)
        strengthening = (
            None
            if args.without_fixed_triangle_prisms
            else add_fixed_triangle_prism_constraints(encoded, parent)
        )
        cases = refined_cases(encoded, parent)
        fixed_assignments = endpoint_fixed_assignments(encoded, parent)
        case_records: list[dict[str, object]] = []

        for refined_branch, literal, orbit_size in cases:
            case_started = time.monotonic()
            with Solver(
                name=args.solver,
                bootstrap_with=encoded.cnf,
                use_timer=True,
            ) as solver:
                solver.conf_budget(args.conflict_budget)
                result = solver.solve_limited(assumptions=[literal])
                model = solver.get_model() if result is True else None
                solver_record = {
                    "solver": args.solver,
                    "conflict_budget": args.conflict_budget,
                    "solver_seconds": solver.time_accum(),
                    "accumulated_stats": solver.accum_stats(),
                }

            status = (
                "SAT_CANDIDATE"
                if result is True
                else "UNSAT_UNVERIFIED"
                if result is False
                else "BUDGET_UNKNOWN"
            )
            candidate_path = None
            candidate_sha256 = None
            if model is not None:
                case_assignments = dict(fixed_assignments)
                case_assignments[literal] = True
                merged_model = merge_model_with_fixed_assignments(
                    model, case_assignments
                )
                candidate = encoded.full_certificate(merged_model)
                candidate_text = (
                    json.dumps(candidate, indent=2, sort_keys=True) + "\n"
                )
                candidate_sha256 = sha256_text(candidate_text)
                if args.candidate_dir:
                    args.candidate_dir.mkdir(parents=True, exist_ok=True)
                    candidate_path = (
                        args.candidate_dir
                        / f"parent-{parent}-refined-{refined_branch}.srg.json"
                    )
                    candidate_path.write_text(
                        candidate_text, encoding="utf-8", newline="\n"
                    )

            case_records.append(
                {
                    "parent_branch": parent,
                    "refined_branch": refined_branch,
                    "refinement_literal": literal,
                    "refined_orbit_size": orbit_size,
                    "status": status,
                    "solver": solver_record,
                    "wall_seconds": time.monotonic() - case_started,
                    "candidate_path": (
                        str(candidate_path.relative_to(REPOSITORY_ROOT))
                        if candidate_path is not None
                        else None
                    ),
                    "candidate_sha256": candidate_sha256,
                }
            )

        parent_records.append(
            {
                "parent_branch": parent,
                "refined_case_count": len(cases),
                "refined_branch_ids": [case[0] for case in cases],
                "encoding": encoded.statistics(),
                "strengthening": strengthening,
                "cases": case_records,
            }
        )

    payload = {
        "format": "wave36-prism-free-refined-n3-scout-v1",
        "role": "construction",
        "claim_label": "UNKNOWN",
        "git_commit": FROZEN_COMMIT,
        "scope": (
            "complete 33-case oriented-common-neighbor refinement of the five "
            "endpoint-compatible normalized rooted branches under n3=4158"
        ),
        "completed_graph_automorphism_assumed": False,
        "verified_cover_imported": (
            "verification/n3-refined-cover/refined-orbit-certificate.json"
        ),
        "parents": list(args.parents),
        "conflict_budget_per_case": args.conflict_budget,
        "solver": args.solver,
        "fixed_triangle_prism_strengthening": (
            not args.without_fixed_triangle_prisms
        ),
        "endpoint_unit_count": 84,
        "endpoint_edge_catalog_sha256": endpoint_edge_sha256(
            endpoint_edges(EncodedRootModel.build(7).root)
        ),
        "parent_records": parent_records,
        "total_refined_cases": sum(
            int(record["refined_case_count"]) for record in parent_records
        ),
        "wall_seconds": time.monotonic() - run_started,
        "limitations": [
            "Every BUDGET_UNKNOWN case has zero mathematical evidentiary value.",
            "An embedded UNSAT needs exact formula retention and independent proof replay.",
            "A SAT assignment needs independent complete-SRG and P=0 verification.",
            "The imported refined cover was not re-proved by this discovery script.",
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
