"""Lightweight non-certifying coefficient-max scout for Wave139."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import gf4_model as model


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "numeric-scout.json"


def normalized_basis_matrix():
    states = model.states()
    partitions = model.partitions3()
    matrix = np.empty((len(states), len(partitions)), dtype=np.float64)
    evaluations = [model.basis_evaluation(partition) for partition in partitions]
    for column, (partition, evaluation) in enumerate(
        zip(partitions, evaluations)
    ):
        matrix[:, column] = [
            model.basis_coefficient(partition, state) / evaluation
            for state in states
        ]
    return states, partitions, matrix


def scaled_row(row: np.ndarray, rhs: float):
    scale = float(np.max(np.abs(row)))
    if not np.isfinite(scale) or scale == 0:
        raise AssertionError("zero or nonfinite model row")
    return row / scale, rhs / scale


def scout(
    time_limit: float,
    method: str = "highs",
    objective: str = "maximize-target",
) -> dict:
    started = time.monotonic()
    states, partitions, matrix = normalized_basis_matrix()
    state_index = {state: index for index, state in enumerate(states)}
    lower = model.lower_bounds()

    row_scales = np.max(np.abs(matrix), axis=1)
    if np.any(row_scales == 0):
        raise AssertionError("basis has a zero state row")
    a_ub = -(matrix / row_scales[:, None])
    b_ub = np.asarray(
        [
            -lower.get(state, 0) / model.ORDER / row_scales[index]
            for index, state in enumerate(states)
        ]
    )

    a_eq = [np.ones(len(partitions))]
    b_eq = [1.0]
    equality_labels = ["normalization"]

    zero_row, zero_rhs = scaled_row(
        matrix[state_index[(99, 0, 0)]], 1 / model.ORDER
    )
    a_eq.append(zero_row)
    b_eq.append(zero_rhs)
    equality_labels.append("A0")

    pure_y_indices = [
        index for index, state in enumerate(states) if state[2] == 0
    ]
    pure_y_row = np.sum(matrix[pure_y_indices, :], axis=0)
    pure_y_row, pure_y_rhs = scaled_row(
        pure_y_row, (1 << 54) / model.ORDER
    )
    a_eq.append(pure_y_row)
    b_eq.append(pure_y_rhs)
    equality_labels.append("pure_Y_size")

    for weight in sorted(model.PURE_Y_ZERO_WEIGHTS):
        row = matrix[state_index[(model.N - weight, weight, 0)]]
        row, rhs = scaled_row(row, 0.0)
        a_eq.append(row)
        b_eq.append(rhs)
        equality_labels.append(f"pure_Y_zero_{weight}")

    target_index = state_index[model.TARGET_STATE]
    target_row = matrix[target_index]
    target_scale = float(np.max(np.abs(target_row)))
    objective_row = (
        -(target_row / target_scale)
        if objective == "maximize-target"
        else np.zeros(len(partitions))
    )
    result = linprog(
        objective_row,
        A_ub=a_ub,
        b_ub=b_ub,
        A_eq=np.asarray(a_eq),
        b_eq=np.asarray(b_eq),
        bounds=[(None, None)] * len(partitions),
        method=method,
        options={
            "time_limit": time_limit,
            "primal_feasibility_tolerance": 1e-9,
            "dual_feasibility_tolerance": 1e-9,
        },
    )
    payload = {
        "format": "wave139-gf4-n3-numeric-scout-v1",
        "claim_label": "CANDIDATE",
        "scipy_status": int(result.status),
        "scipy_message": result.message,
        "success": bool(result.success),
        "method": method,
        "objective": objective,
        "elapsed_seconds": time.monotonic() - started,
        "dimensions": {
            "raw_states": 5050,
            "allowed_state_inequalities": len(states),
            "invariant_basis_variables": len(partitions),
            "equalities_after_invariant_reduction": len(a_eq),
        },
        "state_order": ["nI", "nY", "nR"],
        "target_state": list(model.TARGET_STATE),
        "limitations": [
            "Floating-point support scout only.",
            "No numerical objective or dual vector is an exact upper bound.",
            "A strict bound requires exact rational dual replay.",
        ],
    }
    if result.x is not None:
        q = np.asarray(result.x)
        state_probabilities = matrix @ q
        target_probability = float(state_probabilities[target_index])
        equality_residuals = np.asarray(a_eq) @ q - np.asarray(b_eq)
        state_slacks = state_probabilities - np.asarray(
            [lower.get(state, 0) / model.ORDER for state in states]
        )
        payload["numerical_solution"] = {
            "target_probability": target_probability,
            "target_coefficient": target_probability * model.ORDER,
            "target_over_4158": (
                target_probability * model.ORDER / 4158
            ),
            "min_unscaled_state_slack": float(np.min(state_slacks)),
            "max_scaled_equality_residual": float(
                np.max(np.abs(equality_residuals))
            ),
            "active_state_indices_at_1e-9_scaled": [
                index
                for index, slack in enumerate(
                    state_slacks / row_scales
                )
                if slack <= 1e-9
            ],
            "basis_support_at_1e-10": int(np.sum(np.abs(q) > 1e-10)),
            "equality_labels": equality_labels,
        }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time-limit", type=float, default=60)
    parser.add_argument(
        "--method",
        choices=("highs", "highs-ds", "highs-ipm"),
        default="highs",
    )
    parser.add_argument(
        "--objective",
        choices=("maximize-target", "feasibility"),
        default="maximize-target",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = scout(args.time_limit, args.method, args.objective)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(payload["scipy_status"], payload["success"])
    if "numerical_solution" in payload:
        print(payload["numerical_solution"]["target_coefficient"])


if __name__ == "__main__":
    main()
