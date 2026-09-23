#!/usr/bin/env python3
"""Numerically feed the exact Wave152 cuts back into the endpoint system.

Two modes are available:

* ``zero`` keeps both Wave147 centered covariance blocks identically zero and
  solves the resulting LP with HiGHS.
* ``pair-psd`` imposes the full two-root centered PSD constraints and maximizes
  their common numerical margin.

Numerical solver statuses are reconnaissance only.  An infeasibility claim
requires an independently replayed exact certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import cvxpy as cp
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "attempts/wave150-order8-sdp-scout/endpoint_sdp.py"
CUTS_PATH = HERE / "exact-cuts.json"
N = 99


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dense_cut(
    cut: dict[str, Any],
    classes7: tuple[int, ...],
    classes8: tuple[int, ...],
) -> tuple[int, np.ndarray, np.ndarray]:
    index7 = {mask: index for index, mask in enumerate(classes7)}
    index8 = {mask: index for index, mask in enumerate(classes8)}
    row7 = np.zeros(len(classes7), dtype=np.float64)
    row8 = np.zeros(len(classes8), dtype=np.float64)
    for record in cut["order7_coefficients"]:
        row7[index7[int(record["canonical_mask"])]] = float(record["coefficient"])
    for record in cut["order8_coefficients"]:
        row8[index8[int(record["canonical_mask"])]] = float(record["coefficient"])
    return int(cut["constant"]), row7, row8


def solve(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    model = load_module("wave152_cut_feasibility_model", MODEL_PATH)
    memory = [model.memory_record("start")]
    inputs = model.load_inputs(True)
    cut_paths = [path.resolve() for path in args.cuts]
    cuts = []
    for path in cut_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        cuts.extend(payload["cuts"] if "cuts" in payload else [payload["cut"]])
    require(cuts, "no Wave152 cuts supplied")
    require(
        len({cut["cut_sha256"] for cut in cuts}) == len(cuts),
        "duplicate Wave152 cut",
    )

    classes7 = tuple(int(mask) for mask in inputs["classes"][7])
    classes8 = tuple(int(mask) for mask in inputs["classes8"])
    deletion = model.deletion_matrix(
        inputs["coefficient_payload"], classes7, classes8
    )
    row_matrix, row_y, row_rhs, _ = model.normalized_wave44_rows(
        inputs["row_system"]
    )
    marked7, marked8, marked_metadata = model.normalized_marked_rows(
        inputs["marked_rows"], classes7, classes8
    )

    p7 = cp.Variable(len(classes7), name="p7")
    p8 = cp.Variable(len(classes8), name="p8")
    constraints: list[cp.Constraint] = [
        p7 >= 0,
        p8 >= 0,
        cp.sum(p7) == 1,
        cp.sum(p8) == 1,
        p7 == deletion @ p8,
        row_matrix @ p7 + row_y == row_rhs,
        marked7 @ p7 == marked8 @ p8,
    ]
    cut_expressions: list[cp.Expression] = []
    cut_metadata = []
    c7 = math.comb(N, 7)
    c8 = math.comb(N, 8)
    for cut in cuts:
        constant, dense7, dense8 = dense_cut(cut, classes7, classes8)
        scaled7 = dense7 * c7
        scaled8 = dense8 * c8
        scale = max(
            abs(float(constant)),
            float(np.max(np.abs(scaled7))),
            float(np.max(np.abs(scaled8))),
            1.0,
        )
        expression = (
            float(constant) / scale
            + (scaled7 / scale) @ p7
            + (scaled8 / scale) @ p8
        )
        constraints.append(expression >= 0)
        cut_expressions.append(expression)
        cut_metadata.append(
            {
                "root_mask": int(cut["root_mask"]),
                "cut_sha256": cut["cut_sha256"],
                "normalization_scale": scale,
            }
        )

    moments = {}
    centered_moments = {}
    moment_metadata = {}
    margin = cp.Variable(name="pair_root_common_margin")
    for family_name, root_count in (
        ("ordered_edge", N * 14),
        ("ordered_nonedge", N * 84),
    ):
        expression, mean, metadata = model.moment_expression(
            inputs["coefficient_payload"]["families"][family_name],
            classes7,
            classes8,
            inputs["lower_counts"],
            p7,
            p8,
            root_count,
        )
        centered = expression - np.outer(mean, mean)
        moments[family_name] = expression
        centered_moments[family_name] = centered
        moment_metadata[family_name] = metadata
        if args.mode == "zero":
            constraints.append(centered == 0)
        else:
            constraints.append(
                centered - margin * np.eye(int(metadata["size"])) >> 0
            )

    objective = (
        cp.Minimize(0) if args.mode == "zero" else cp.Maximize(margin)
    )
    problem = cp.Problem(objective, constraints)
    memory.append(model.memory_record("before_solve"))
    solve_kwargs: dict[str, Any] = {"verbose": args.verbose}
    if args.solver == "HIGHS":
        require(args.mode == "zero", "HiGHS is only valid in zero mode")
        solve_kwargs.update(
            {
                "time_limit": float(args.time_limit),
                "presolve": "off",
                "primal_feasibility_tolerance": max(args.eps, 1e-10),
                "dual_feasibility_tolerance": max(args.eps, 1e-10),
            }
        )
    elif args.solver == "SCS":
        solve_kwargs.update(
            {
                "eps": args.eps,
                "max_iters": args.max_iters,
                "time_limit_secs": float(args.time_limit),
                "normalize": True,
            }
        )
    elif args.solver == "CLARABEL":
        solve_kwargs.update(
            {
                "max_iter": args.max_iters,
                "time_limit": float(args.time_limit),
                "tol_gap_abs": args.eps,
                "tol_feas": args.eps,
            }
        )
    else:
        raise AssertionError(f"unsupported solver {args.solver}")

    try:
        value = problem.solve(solver=args.solver, **solve_kwargs)
        solver_error = None
    except Exception as exc:
        value = None
        solver_error = f"{type(exc).__name__}: {exc}"
    memory.append(model.memory_record("after_solve"))

    candidate: dict[str, Any] = {"available": p7.value is not None and p8.value is not None}
    if candidate["available"]:
        values7 = np.asarray(p7.value, dtype=np.float64).ravel()
        values8 = np.asarray(p8.value, dtype=np.float64).ravel()
        candidate.update(
            {
                "p7_density": values7.tolist(),
                "p8_density": values8.tolist(),
                "p7_minimum": float(values7.min()),
                "p8_minimum": float(values8.min()),
                "p7_sum": float(values7.sum()),
                "p8_sum": float(values8.sum()),
                "deletion_max_abs_residual": float(
                    np.max(np.abs(values7 - deletion @ values8))
                ),
                "wave44_max_abs_scaled_residual": float(
                    np.max(np.abs(row_matrix @ values7 + row_y - row_rhs))
                ),
                "marked_max_abs_scaled_residual": float(
                    np.max(np.abs(marked7 @ values7 - marked8 @ values8))
                ),
                "normalized_cut_values": [
                    float(np.asarray(expression.value).item())
                    for expression in cut_expressions
                ],
                "pair_root_blocks": {},
            }
        )
        for family_name in moments:
            centered = np.asarray(
                centered_moments[family_name].value, dtype=np.float64
            )
            centered = (centered + centered.T) / 2
            eigenvalues = np.linalg.eigvalsh(centered)
            candidate["pair_root_blocks"][family_name] = {
                "minimum_centered_eigenvalue": float(eigenvalues[0]),
                "maximum_centered_eigenvalue": float(eigenvalues[-1]),
                "maximum_absolute_centered_entry": float(
                    np.max(np.abs(centered))
                ),
            }
        raw7 = values7 * c7
        candidate["x7_maximum_rounding_error"] = float(
            np.max(np.abs(raw7 - np.rint(raw7)))
        )
        candidate["x7_rounded_sum"] = int(np.rint(raw7).sum())

    stats = problem.solver_stats
    return {
        "format": "wave152-cut-feasibility-scout-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Numerical endpoint feasibility after adding two exact Wave152 "
            "four-root covariance directions to Wave44, Wave148 marked rows, "
            f"and the Wave147 pair-root {args.mode} constraints, on the "
            "h11=16632 endpoint slice."
        ),
        "mode": args.mode,
        "target": {
            "n3": 4158,
            "h11": 16632,
            "wave44_y": 4158,
            "y_fraction": 1.0,
        },
        "inputs": {
            str(MODEL_PATH.relative_to(ROOT)).replace("\\", "/"): sha256_file(
                MODEL_PATH
            ),
            **{
                str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path)
                for path in cut_paths
            },
        },
        "marked_metadata": marked_metadata,
        "moment_metadata": moment_metadata,
        "cut_metadata": cut_metadata,
        "solver": {
            "name": args.solver,
            "status": problem.status,
            "objective_value": None if value is None else float(value),
            "error": solver_error,
            "solve_time": getattr(stats, "solve_time", None),
            "num_iters": getattr(stats, "num_iters", None),
            "numerical_status_is_not_a_certificate": True,
        },
        "candidate": candidate,
        "conclusion": {
            "Conway_99": "UNKNOWN",
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "exact_feasibility_after_cuts": "UNKNOWN",
        },
        "limitations": [
            "A numerical feasible point requires exact reconstruction.",
            "A numerical infeasible status requires an exact dual certificate.",
            f"Only {len(cuts)} four-root directions are imposed, not the full nine PSD blocks.",
        ],
        "resource_report": {
            "elapsed_seconds": time.time() - started,
            "minimum_free_physical_memory_percent": min(
                float(record["free_physical_memory_percent"]) for record in memory
            ),
            "samples": memory,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("zero", "pair-psd"), default="zero")
    parser.add_argument("--solver", choices=("HIGHS", "SCS", "CLARABEL"), default="HIGHS")
    parser.add_argument("--time-limit", type=float, default=120.0)
    parser.add_argument("--max-iters", type=int, default=100_000)
    parser.add_argument("--eps", type=float, default=1e-8)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--cuts", type=Path, nargs="+", default=[CUTS_PATH])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "pair-psd":
        require(args.solver != "HIGHS", "pair-psd requires an SDP solver")
    return args


def main() -> int:
    args = parse_args()
    payload = solve(args)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["solver"], indent=2))
    if payload["candidate"]["available"]:
        print(
            json.dumps(
                {
                    key: value
                    for key, value in payload["candidate"].items()
                    if key
                    in {
                        "p7_minimum",
                        "p8_minimum",
                        "normalized_cut_values",
                        "x7_maximum_rounding_error",
                    }
                },
                indent=2,
            )
        )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
