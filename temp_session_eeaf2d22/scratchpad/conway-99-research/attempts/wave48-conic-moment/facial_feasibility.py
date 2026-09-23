#!/usr/bin/env python3
"""Feasibility and analytic-center scouts after exact affine facial reduction."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any

import cvxpy as cp
import numpy as np


HERE = Path(__file__).resolve().parent
COMBINED = HERE / "combined_sdp.py"
DEFAULT_OUTPUT = HERE / "facial-feasibility-result.json"


def load_combined() -> Any:
    name = "wave48_combined_for_feasibility"
    spec = importlib.util.spec_from_file_location(name, COMBINED)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load combined_sdp.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def solve_problem(
    combined: Any,
    model: dict[str, Any],
    problem: cp.Problem,
    *,
    solver: str,
    phase: str,
    settings: dict[str, Any],
) -> dict[str, Any]:
    memory_before = combined.memory_guard(f"{phase}/{solver} before")
    started = time.perf_counter()
    exception = None
    try:
        objective = problem.solve(
            solver=solver,
            warm_start=False,
            **settings,
        )
    except Exception as error:
        objective = None
        exception = f"{type(error).__name__}: {error}"
    elapsed = time.perf_counter() - started
    memory_after = combined.memory_guard(f"{phase}/{solver} after")
    model["margin"].value = 0.0
    candidate = combined.evaluate_candidate(model)
    return {
        "phase": phase,
        "solver": solver,
        "settings": settings,
        "status": problem.status,
        "objective": None if objective is None else float(objective),
        "exception": exception,
        "wall_seconds": elapsed,
        "solver_stats": {
            "solve_time": problem.solver_stats.solve_time,
            "setup_time": problem.solver_stats.setup_time,
            "num_iters": problem.solver_stats.num_iters,
            "extra_stats_text": repr(problem.solver_stats.extra_stats),
        },
        "candidate": candidate,
        "memory_free_percent_before": round(memory_before, 2),
        "memory_free_percent_after": round(memory_after, 2),
        "claim_label": "CANDIDATE_NUMERICAL_ONLY",
        "used_as_exact_evidence": False,
    }


def run(*, include_analytic: bool) -> dict[str, Any]:
    combined = load_combined()
    combined.memory_guard("facial feasibility start")
    records = []

    for solver in ("CLARABEL", "SCS"):
        model = combined.build_problem()
        feasibility = cp.Problem(
            cp.Minimize(0),
            model["base_constraints"],
        )
        records.append(
            solve_problem(
                combined,
                model,
                feasibility,
                solver=solver,
                phase="facial_feasibility_margin_zero",
                settings=combined.solver_settings(solver),
            )
        )

    if include_analytic:
        model = combined.build_problem()
        epsilon = 1e-9
        log_determinants = [
            cp.log_det(
                record["compressed_expression"]
                + epsilon * np.eye(
                    record["compressed_expression"].shape[0]
                )
            )
            for record in model["moment_records"]
        ]
        probability_barrier = 1e-5 * cp.sum(cp.log(model["z"] + epsilon))
        q_barrier = 1e-5 * (
            cp.log(model["q"] - 0.5 + epsilon)
            + cp.log(1.0 - model["q"] + epsilon)
        )
        analytic = cp.Problem(
            cp.Maximize(
                sum(log_determinants) + probability_barrier + q_barrier
            ),
            model["base_constraints"],
        )
        analytic_settings = combined.solver_settings("CLARABEL")
        analytic_settings["max_iter"] = 750
        analytic_settings["time_limit"] = 60.0
        records.append(
            solve_problem(
                combined,
                model,
                analytic,
                solver="CLARABEL",
                phase="facial_logdet_analytic_center",
                settings=analytic_settings,
            )
        )

    return {
        "format": "wave48-exact-face-feasibility-scout-v1",
        "role": "proof_b",
        "claim_label": "CANDIDATE",
        "scope": (
            "margin-zero feasibility and log-det analytic-center numerical "
            "scouts after exact Wave48 affine facial reduction"
        ),
        "facial_reduction": {
            "path": "attempts/wave48-conic-moment/exact-faces.json",
            "sha256": combined.EXPECTED_SHA256[combined.EXACT_FACES],
            "all_families_exactly_sealed": True,
        },
        "analytic_center": {
            "matrix_objective": "sum log_det(C_sigma + 1e-9 I)",
            "probability_barrier_weight": 1e-5,
            "probability_shift": 1e-9,
            "h11_scaled_interval": ["1/2", "1"],
        },
        "runs": records,
        "conclusion": {
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "graph_constructed": False,
            "numerical_status_is_not_certificate": True,
        },
        "limitations": [
            "All feasibility and analytic-center statuses are floating diagnostics.",
            "Tiny negative probabilities or eigenvalues are retained as numerical residuals.",
            "No exact feasible real witness or exact infeasibility dual is claimed.",
            "Aggregate moment feasibility would not construct a graph.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-analytic", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run(include_analytic=not args.skip_analytic)
    payload = canonical_payload(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    for record in result["runs"]:
        candidate = record["candidate"]
        print(
            json.dumps(
                {
                    "phase": record["phase"],
                    "solver": record["solver"],
                    "status": record["status"],
                    "objective": record["objective"],
                    "minimum_active_eigenvalue": (
                        None
                        if candidate is None
                        else candidate[
                            "minimum_active_support_eigenvalue"
                        ]
                    ),
                    "minimum_probability": (
                        None
                        if candidate is None
                        else candidate["seven_probability_minimum"]
                    ),
                    "scaled_linear_max_abs_residual": (
                        None
                        if candidate is None
                        else candidate[
                            "scaled_linear_max_abs_residual"
                        ]
                    ),
                },
                sort_keys=True,
            )
        )
    print(f"result_sha256={sha256_bytes(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
