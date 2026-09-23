"""Non-certifying floating feasibility scouts for the two exact Arf slices."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE134 = ROOT / "attempts" / "wave134-z4-symmetrized-enumerator"
WAVE135 = ROOT / "attempts" / "wave135-z4-exact-face"
SPEC = importlib.util.spec_from_file_location(
    "wave134_exact_check", WAVE134 / "exact_check.py"
)
MODEL = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODEL)
ORBIT_TOTAL = 1 << 108
ARF_TOTAL = 1 << 81
TORSION_TOTAL = 1 << 54


def scaled_row(values) -> tuple[np.ndarray, float]:
    row = np.asarray(values, dtype=np.float64)
    scale = float(np.max(np.abs(row)))
    if not np.isfinite(scale) or scale == 0:
        raise AssertionError("invalid scaling row")
    return row / scale, scale


def build(sign: int):
    sources = MODEL.primal_states()
    forbidden = MODEL.forbidden_dual_states()
    allowed = MODEL.dual_states()
    basis_payload = json.loads(
        (WAVE135 / "face-rank.json").read_text(encoding="utf-8")
    )
    basis_indices = basis_payload["forbidden_row_basis"][
        "independent_row_indices"
    ]

    def transform_row(target):
        return [
            MODEL.transform_coefficient(source, target)
            for source in sources
        ]

    equality_rows = []
    equality_rhs = []
    equality_labels = []
    for index in basis_indices:
        row, scale = scaled_row(transform_row(forbidden[index]))
        equality_rows.append(row)
        equality_rhs.append(0.0)
        equality_labels.append(f"forbidden:{index}")
    equality_rows.append(np.ones(len(sources)))
    equality_rhs.append(1.0)
    equality_labels.append("normalization")
    zero = np.zeros(len(sources))
    zero[sources.index((99, 0, 0))] = 1.0
    equality_rows.append(zero)
    equality_rhs.append(1.0 / ORBIT_TOTAL)
    equality_labels.append("A0")
    torsion = np.asarray(
        [1.0 if state[1] == 0 else 0.0 for state in sources]
    )
    equality_rows.append(torsion)
    equality_rhs.append(TORSION_TOTAL / ORBIT_TOTAL)
    equality_labels.append("torsion_shell")
    arf = np.asarray(
        [
            1.0 if (state[1] // 2) % 2 == 0 else -1.0
            for state in sources
        ]
    )
    equality_rows.append(arf)
    equality_rhs.append(sign * ARF_TOTAL / ORBIT_TOTAL)
    equality_labels.append("arf_gauss")

    inequality_rows = []
    inequality_rhs = []
    inequality_scales = []
    for target in allowed:
        row, scale = scaled_row(transform_row(target))
        inequality_rows.append(-row)
        inequality_rhs.append(-MODEL.forced_dual().get(target, 0) / scale)
        inequality_scales.append(scale)

    lower = [
        MODEL.forced_primal().get(state, 0) / ORBIT_TOTAL
        for state in sources
    ]
    return {
        "sources": sources,
        "allowed": allowed,
        "A_eq": np.asarray(equality_rows),
        "b_eq": np.asarray(equality_rhs),
        "eq_labels": equality_labels,
        "A_ub": np.asarray(inequality_rows),
        "b_ub": np.asarray(inequality_rhs),
        "ineq_scales": inequality_scales,
        "bounds": [(value, None) for value in lower],
    }


def scout(
    sign: int,
    time_limit: float,
    method: str = "highs",
    presolve: bool = True,
) -> dict:
    built = build(sign)
    started = time.monotonic()
    result = linprog(
        np.zeros(len(built["sources"])),
        A_ub=built["A_ub"],
        b_ub=built["b_ub"],
        A_eq=built["A_eq"],
        b_eq=built["b_eq"],
        bounds=built["bounds"],
        method=method,
        options={
            "time_limit": time_limit,
            "presolve": presolve,
            "primal_feasibility_tolerance": 1e-10,
            "dual_feasibility_tolerance": 1e-10,
            "ipm_optimality_tolerance": 1e-12,
        },
    )
    payload = {
        "format": "wave137-z4-arf-float-scout-v1",
        "claim_label": "CANDIDATE",
        "sign": sign,
        "method": method,
        "presolve": presolve,
        "scipy_status": int(result.status),
        "scipy_message": result.message,
        "success": bool(result.success),
        "elapsed_seconds": time.monotonic() - started,
        "dimensions": {
            "variables": len(built["sources"]),
            "equalities": built["A_eq"].shape[0],
            "allowed_dual_inequalities": built["A_ub"].shape[0],
        },
        "limitations": [
            "Floating-point scout only; no feasibility or infeasibility claim.",
            "Tiny exact A0, torsion, and forced-count scales may lie below practical numerical resolution.",
            "A numerical infeasibility status is not a Farkas certificate.",
        ],
    }
    if result.x is not None:
        x = np.asarray(result.x)
        equality_residual = built["A_eq"] @ x - built["b_eq"]
        slacks = built["b_ub"] - built["A_ub"] @ x
        active_dual = [
            index
            for index, slack in enumerate(slacks)
            if slack <= 1e-9
        ]
        near_zero_primal = [
            index for index, value in enumerate(x) if value <= 1e-12
        ]
        payload["numerical_replay"] = {
            "max_scaled_equality_residual": float(
                np.max(np.abs(equality_residual))
            ),
            "min_scaled_dual_slack": float(np.min(slacks)),
            "normalization": float(np.sum(x)),
            "torsion_shell_sum": float(
                sum(
                    value
                    for state, value in zip(built["sources"], x)
                    if state[1] == 0
                )
            ),
            "arf_weighted_sum": float(
                sum(
                    (
                        1.0 if (state[1] // 2) % 2 == 0 else -1.0
                    )
                    * value
                    for state, value in zip(built["sources"], x)
                )
            ),
            "active_dual_row_indices_at_1e-9": active_dual,
            "near_zero_primal_indices_at_1e-12": near_zero_primal,
            "positive_primal_support_at_1e-12": (
                len(x) - len(near_zero_primal)
            ),
        }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sign", type=int, choices=(-1, 1), required=True)
    parser.add_argument("--time-limit", type=float, default=60)
    parser.add_argument(
        "--method",
        choices=("highs", "highs-ds", "highs-ipm"),
        default="highs",
    )
    parser.add_argument("--no-presolve", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or (
        HERE
        / (
            "float-scout-plus.json"
            if args.sign > 0
            else "float-scout-minus.json"
        )
    )
    payload = scout(
        args.sign,
        args.time_limit,
        method=args.method,
        presolve=not args.no_presolve,
    )
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(payload["sign"], payload["scipy_status"], payload["success"])


if __name__ == "__main__":
    main()
