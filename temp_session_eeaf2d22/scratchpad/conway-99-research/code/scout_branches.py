#!/usr/bin/env python3
"""Run a bounded, non-evidentiary scouting pass across all canonical branches.

The base CNF is built once. Branch decisions are supplied as assumptions to one
incremental solver, so learned clauses may carry between branches. This is safe
for candidate scouting but not the archival proof workflow.
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence

import pysat
from pysat.solvers import Solver

from matching_orbits import canonical_branch_decisions, integer_partitions
from sat_model import EncodedRootModel


def difference(after: dict[str, int], before: dict[str, int]) -> dict[str, int]:
    return {key: after.get(key, 0) - before.get(key, 0) for key in after}


def run_scout(
    pair_count: int,
    coordinate: int,
    conflict_budget: int,
    solver_name: str,
    candidate_directory: Path | None,
    cardinality_backend: str = "cnf",
    reuse_solver: bool = True,
) -> dict[str, Any]:
    if cardinality_backend == "native" and solver_name != "minicard":
        raise ValueError("native cardinality is supported only with solver 'minicard'")
    build_start = time.perf_counter()
    encoded = EncodedRootModel.build(
        pair_count,
        "compact",
        cardinality_backend,
    )
    build_seconds = time.perf_counter() - build_start
    partitions = list(integer_partitions(pair_count - 1))
    branch_reports: list[dict[str, Any]] = []
    bootstrap = (
        encoded.cnf
        if encoded.cardinality_backend == "native"
        else encoded.cnf.clauses
    )

    def run_partition(
        solver: Solver,
        partition: tuple[int, ...],
        previous_stats: dict[str, int],
    ) -> tuple[dict[str, Any], dict[str, int], bool | None]:
        decisions = canonical_branch_decisions(encoded.root, coordinate, partition)
        assumptions = [
            encoded.edge_variables[edge] if present else -encoded.edge_variables[edge]
            for edge, present in sorted(decisions.items())
        ]
        solver.conf_budget(conflict_budget)
        branch_start = time.perf_counter()
        status = solver.solve_limited(assumptions=assumptions)
        branch_seconds = time.perf_counter() - branch_start
        current_stats = solver.accum_stats()
        delta = difference(current_stats, previous_stats)

        branch: dict[str, Any] = {
            "partition": list(partition),
            "result": (
                "SAT_MODEL"
                if status is True
                else "UNSAT_UNVERIFIED"
                if status is False
                else "UNKNOWN"
            ),
            "wall_seconds": branch_seconds,
            "solver_stats_delta": delta,
        }
        if status is True:
            model = solver.get_model()
            if model is None:
                raise RuntimeError("solver returned SAT without a model")
            certificate = encoded.full_certificate(model)
            if candidate_directory:
                candidate_directory.mkdir(parents=True, exist_ok=True)
                name = "-".join(str(part) for part in partition)
                candidate_path = candidate_directory / f"scout-branch-{name}.srg.json"
                candidate_path.write_text(
                    json.dumps(certificate, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                branch["candidate"] = str(candidate_path)
        return branch, current_stats, status

    solve_start = time.perf_counter()
    if reuse_solver:
        with Solver(
            name=solver_name,
            bootstrap_with=bootstrap,
            use_timer=True,
        ) as solver:
            previous_stats = solver.accum_stats()
            for partition in partitions:
                branch, previous_stats, status = run_partition(
                    solver,
                    partition,
                    previous_stats,
                )
                branch_reports.append(branch)
                if status is True:
                    break
    else:
        for partition in partitions:
            partition_text = "+".join(str(part) for part in partition)
            command = [
                sys.executable,
                str(Path(__file__).with_name("sat_model.py")),
                "--pair-count",
                str(pair_count),
                "--variant",
                "compact",
                "--cardinality",
                cardinality_backend,
                "--branch",
                partition_text,
                "--branch-coordinate",
                str(coordinate),
                "--solve",
                "--solver",
                solver_name,
                "--conflict-budget",
                str(conflict_budget),
            ]
            candidate_path = None
            if candidate_directory:
                candidate_directory.mkdir(parents=True, exist_ok=True)
                candidate_path = (
                    candidate_directory / f"scout-branch-{partition_text}.srg.json"
                )
                command.extend(("--candidate", str(candidate_path)))

            branch_start = time.perf_counter()
            completed = subprocess.run(
                command,
                capture_output=True,
                check=False,
                text=True,
            )
            branch_seconds = time.perf_counter() - branch_start
            if completed.returncode != 0:
                raise RuntimeError(
                    f"fresh branch process failed for {partition_text}: "
                    f"{completed.stderr.strip()}"
                )
            child_report = json.loads(completed.stdout)
            result = child_report.get("result")
            if result not in ("SAT_MODEL", "UNSAT_UNVERIFIED", "UNKNOWN"):
                raise RuntimeError(
                    f"fresh branch process returned invalid result {result!r}"
                )
            branch = {
                "partition": list(partition),
                "result": result,
                "wall_seconds": branch_seconds,
                "solver_stats_delta": child_report["solver"][
                    "accumulated_stats"
                ],
            }
            if result == "SAT_MODEL" and candidate_path:
                branch["candidate"] = str(candidate_path)
            branch_reports.append(branch)
            if result == "SAT_MODEL":
                break

    return {
        "format": "conway-branch-scout-v1",
        "evidence_status": "NON_EVIDENTIARY_SCOUT",
        "warning": "UNKNOWN/timeouts are not evidence; UNSAT requires rerun with branch units and a checked proof.",
        "environment": {
            "python": sys.version.split()[0],
            "python_sat": pysat.__version__,
            "platform": platform.platform(),
        },
        "configuration": {
            "pair_count": pair_count,
            "coordinate": coordinate,
            "conflict_budget_per_branch": conflict_budget,
            "solver": solver_name,
            "cardinality_backend": cardinality_backend,
            "incremental_learned_clauses": reuse_solver,
        },
        "encoding": encoded.statistics(),
        "build_seconds": build_seconds,
        "solve_wall_seconds": time.perf_counter() - solve_start,
        "branches_planned": len(partitions),
        "branches_run": len(branch_reports),
        "branches": branch_reports,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair-count", type=int, default=7)
    parser.add_argument("--coordinate", type=int, default=0)
    parser.add_argument("--conflict-budget", type=int, default=100)
    parser.add_argument("--solver")
    parser.add_argument(
        "--cardinality",
        choices=("cnf", "native"),
        default="cnf",
    )
    parser.add_argument(
        "--fresh-solvers",
        action="store_true",
        help="rebuild the solver for each branch instead of sharing learned clauses",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--candidate-directory", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.conflict_budget < 1:
        raise SystemExit("--conflict-budget must be positive")
    solver_name = args.solver or (
        "minicard" if args.cardinality == "native" else "cadical300"
    )
    report = run_scout(
        args.pair_count,
        args.coordinate,
        args.conflict_budget,
        solver_name,
        args.candidate_directory,
        args.cardinality,
        not args.fresh_solvers,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
