"""Bounded, non-evidentiary floating scout for the Wave141 relaxation.

The scout uses 2,500 input-complement representatives and conditional
input-row coordinates

    p[i,j] = B[i,j] / binomial(99,i).

It row-generates transform equations, so it never materializes the full dense
2,500 by 2,500 block unless every row is eventually activated.  Solver status
and approximate residuals are telemetry only.  Transform residuals are audited
after converting to orthonormal q-coordinates.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import time
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, vstack


N = 99
IMAGE_DIMENSION = 54
KERNEL_DIMENSION = 45
HERE = Path(__file__).resolve().parent
INPUTS = tuple(range(50))
OUTPUTS = tuple(range(0, 100, 2))
PAIRS = tuple((i, j) for i in INPUTS for j in OUTPUTS)
INDEX = {pair: position for position, pair in enumerate(PAIRS)}
NVAR = len(PAIRS)
IMAGE_LOWER = {
    14: 99,
    24: 4158,
    26: 693,
    30: 70686,
    32: 41580,
    34: 36036,
    36: 8547,
}
DUAL_BASE_LOWER = {
    15: 99,
    24: 693,
    26: 4158,
    31: 41580,
    33: 79002,
    35: 8316,
    37: 27720,
    39: 231,
}
SIGNED_ROWS = [1, -99, 3465, -56595, 462924, -1821204]


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.ullAvailPhys / status.ullTotalPhys


def exact_krawtchouk() -> list[list[int]]:
    table = [[0] * (N + 1) for _ in range(N + 1)]
    for weight in range(N + 1):
        table[0][weight] = 1
        table[1][weight] = N - 2 * weight
        for degree in range(1, N):
            numerator = (
                (N - 2 * weight) * table[degree][weight]
                - (N - degree + 1) * table[degree - 1][weight]
            )
            if numerator % (degree + 1):
                raise AssertionError("Krawtchouk recurrence lost integrality")
            table[degree + 1][weight] = numerator // (degree + 1)
    return table


def normalized_krawtchouk(
    combinations: np.ndarray,
    exact: list[list[int]],
) -> np.ndarray:
    raw = np.asarray(exact, dtype=np.float64)
    matrix = (
        (2.0 ** (-N / 2))
        * raw
        * np.sqrt(combinations[None, :] / combinations[:, None])
    )
    orthogonality_error = float(
        np.max(np.abs(matrix @ matrix.T - np.eye(N + 1)))
    )
    if orthogonality_error > 2e-12:
        raise AssertionError(
            f"normalized Krawtchouk orthogonality drift: {orthogonality_error}"
        )
    return matrix


def transform_row(
    target_i: int,
    target_j: int,
    normalized: np.ndarray,
    combinations: np.ndarray,
) -> np.ndarray:
    input_factor = np.array(
        [
            normalized[target_j, source_i]
            + normalized[target_j, N - source_i]
            for source_i in INPUTS
        ],
        dtype=np.float64,
    )
    output_factor = normalized[target_i, list(OUTPUTS)]
    source_input_scale = np.sqrt(
        combinations[target_j]
        * combinations[list(INPUTS)]
        / combinations[target_i]
    )
    source_output_scale = 1.0 / np.sqrt(combinations[list(OUTPUTS)])
    row = -np.outer(
        input_factor * source_input_scale,
        output_factor * source_output_scale,
    ).reshape(NVAR)
    row[INDEX[(target_i, target_j)]] += 1.0
    scale = max(1.0, float(np.max(np.abs(row))))
    return row / scale


def reconstruct_q(
    solution: np.ndarray,
    combinations: np.ndarray,
) -> np.ndarray:
    reduced = solution.reshape((len(INPUTS), len(OUTPUTS)))
    q_reduced = reduced * np.sqrt(
        combinations[list(INPUTS), None]
        / combinations[None, list(OUTPUTS)]
    )
    full = np.zeros((N + 1, N + 1), dtype=np.float64)
    full[:50, list(OUTPUTS)] = q_reduced
    full[50:, list(OUTPUTS)] = q_reduced[::-1, :]
    return full


def transform_residual(
    solution: np.ndarray,
    normalized: np.ndarray,
    combinations: np.ndarray,
) -> np.ndarray:
    q = reconstruct_q(solution, combinations)
    transformed = normalized @ q.T @ normalized.T
    return q[:50, list(OUTPUTS)] - transformed[:50, list(OUTPUTS)]


def p_value(count: int, i: int, combinations: np.ndarray) -> float:
    return count / combinations[i]


def coefficient_for_output_function(
    combinations: np.ndarray,
    values_by_output: np.ndarray,
    denominator: float,
) -> np.ndarray:
    result = np.empty(NVAR, dtype=np.float64)
    for position, (i, j) in enumerate(PAIRS):
        result[position] = (
            2.0
            * combinations[i]
            * values_by_output[j]
            / denominator
        )
    return result


def base_model(
    arf_sign: int,
    combinations: np.ndarray,
    exact_kraw: list[list[int]],
) -> tuple[
    list[np.ndarray],
    list[float],
    list[np.ndarray],
    list[float],
    list[tuple[float, float | None]],
    np.ndarray,
]:
    equalities: list[np.ndarray] = []
    equality_rhs: list[float] = []
    inequalities: list[np.ndarray] = []
    inequality_rhs: list[float] = []
    bounds: list[tuple[float, float | None]] = [(0.0, None)] * NVAR

    def add_equality(row: np.ndarray, rhs: float) -> None:
        scale = max(1.0, float(np.max(np.abs(row))), abs(rhs))
        equalities.append(row / scale)
        equality_rhs.append(rhs / scale)

    def add_upper(row: np.ndarray, rhs: float) -> None:
        scale = max(1.0, float(np.max(np.abs(row))), abs(rhs))
        inequalities.append(row / scale)
        inequality_rhs.append(rhs / scale)

    def fix(i: int, j: int, count: int) -> None:
        value = p_value(count, i, combinations)
        bounds[INDEX[(i, j)]] = (value, value)

    # Exact input marginals.
    for i in INPUTS:
        row = np.zeros(NVAR, dtype=np.float64)
        for j in OUTPUTS:
            row[INDEX[(i, j)]] = 1.0
        add_equality(row, 1.0)

    # Exact low input rows 0,...,3.
    low = {
        0: {0: 1},
        1: {14: 99},
        2: {24: 4158, 26: 693},
        3: {30: 70686, 32: 41580, 34: 36036, 36: 8547},
    }
    for i, row in low.items():
        for j in OUTPUTS:
            fix(i, j, row.get(j, 0))

    # Exact image zero columns and the kernel minimum-distance part of column 0.
    for j in (2, 4, 6, 8, 10, 12, 94, 96, 98):
        for i in INPUTS:
            fix(i, j, 0)
    for i in range(1, 15):
        fix(i, 0, 0)

    # Signed input rows S0,...,S5.  S0,...,S3 are redundant hostile checks.
    for i, signed_value in enumerate(SIGNED_ROWS):
        row = np.zeros(NVAR, dtype=np.float64)
        for j in OUTPUTS:
            row[INDEX[(i, j)]] = (
                (-1.0) ** (j // 2)
            )
        add_equality(row, signed_value / combinations[i])

    two_to_n = float(1 << N)
    # The output marginal at zero is exactly 2^45.
    zero_values = np.zeros(N + 1, dtype=np.float64)
    zero_values[0] = 1.0
    add_equality(
        coefficient_for_output_function(
            combinations,
            zero_values,
            two_to_n,
        ),
        2.0 ** (-IMAGE_DIMENSION),
    )

    # Exact Arf/Krawtchouk identities through degree five, one sign per run.
    for degree, signed_input in enumerate(SIGNED_ROWS):
        values = np.zeros(N + 1, dtype=np.float64)
        divisor = combinations[degree]
        for j in OUTPUTS:
            values[j] = (
                (-1.0) ** (j // 2)
                * exact_kraw[degree][j]
                / divisor
            )
        add_equality(
            coefficient_for_output_function(
                combinations,
                values,
                two_to_n,
            ),
            arf_sign
            * signed_input
            / (float(1 << 27) * divisor),
        )

    # All approved Wave137 shadow inequalities for degrees 6,...,99.
    for degree in range(6, N + 1):
        values = np.zeros(N + 1, dtype=np.float64)
        divisor = combinations[degree]
        for j in OUTPUTS:
            values[j] = (
                (-1.0) ** (j // 2)
                * exact_kraw[degree][j]
                / divisor
            )
        row = coefficient_for_output_function(
            combinations,
            values,
            two_to_n,
        )
        add_upper(row, 2.0 ** (-27))
        add_upper(-row, 2.0 ** (-27))

    # Ordinary MacWilliams image-to-kernel constraints.  Coefficients below
    # equal D_t/binom(99,t), where D is the kernel weight enumerator.
    dual_rows = []
    for degree in range(N + 1):
        values = np.zeros(N + 1, dtype=np.float64)
        divisor = combinations[degree]
        for j in OUTPUTS:
            values[j] = exact_kraw[degree][j] / divisor
        dual_rows.append(
            coefficient_for_output_function(
                combinations,
                values,
                two_to_n,
            )
        )
    add_equality(dual_rows[0], 1.0)
    for degree in range(1, 15):
        add_equality(dual_rows[degree], 0.0)
    add_equality(dual_rows[99], 1.0)
    # Complement symmetry supplies the other half.  Adding both floating
    # copies creates avoidable near-zero contradictory rows at high degrees.
    for degree in range(15, 50):
        add_upper(-dual_rows[degree], 0.0)
    for degree in range(50):
        add_equality(dual_rows[degree] - dual_rows[N - degree], 0.0)

    # Known image and kernel lower bounds.
    for j, lower in IMAGE_LOWER.items():
        values = np.zeros(N + 1, dtype=np.float64)
        values[j] = 1.0
        row = coefficient_for_output_function(
            combinations,
            values,
            two_to_n,
        )
        add_upper(-row, -lower * 2.0 ** (-IMAGE_DIMENSION))

    dual_lower = dict(DUAL_BASE_LOWER)
    for degree, lower in list(dual_lower.items()):
        dual_lower[N - degree] = max(dual_lower.get(N - degree, 0), lower)
    for degree, lower in dual_lower.items():
        add_upper(
            -dual_rows[degree],
            -lower / combinations[degree],
        )

    # Maximize the normalized sixth signed row.  The actual objective is
    # S6=binom(99,6)*normalized_objective.
    objective = np.zeros(NVAR, dtype=np.float64)
    for j in OUTPUTS:
        objective[INDEX[(6, j)]] = (
            (-1.0) ** (j // 2)
        )
    return (
        equalities,
        equality_rhs,
        inequalities,
        inequality_rhs,
        bounds,
        objective,
    )


def run_branch(
    arf_sign: int,
    sense: str,
    rounds: int,
    add_per_round: int,
    time_limit: float,
    solver_method: str,
    initial_input_rows: int,
) -> dict:
    started = time.time()
    free_before = free_memory_percent()
    if free_before < 20.0:
        return {
            "arf_sign": arf_sign,
            "sense": sense,
            "status": "SKIPPED_MEMORY_GUARD",
            "free_memory_percent_before": free_before,
        }

    combinations = np.asarray(
        [math.comb(N, degree) for degree in range(N + 1)],
        dtype=np.float64,
    )
    exact = exact_krawtchouk()
    normalized = normalized_krawtchouk(combinations, exact)
    (
        base_eq,
        base_rhs,
        inequalities,
        inequality_rhs,
        bounds,
        objective,
    ) = base_model(arf_sign, combinations, exact)

    active: set[tuple[int, int]] = {
        (i, j)
        for i in range(initial_input_rows)
        for j in OUTPUTS
    }
    transform_rows = [
        transform_row(i, j, normalized, combinations)
        for i, j in sorted(active)
    ]
    round_records = []
    final_solution = None
    final_result = None
    signed_objective = -objective if sense == "max" else objective

    for round_index in range(rounds):
        if free_memory_percent() < 18.0:
            round_records.append({"status": "STOPPED_MEMORY_GUARD"})
            break
        eq_matrix = vstack(
            [
                csr_matrix(np.asarray(base_eq)),
                csr_matrix(np.asarray(transform_rows)),
            ],
            format="csr",
        )
        eq_rhs = np.asarray(base_rhs + [0.0] * len(transform_rows))
        ub_matrix = csr_matrix(np.asarray(inequalities))
        ub_rhs = np.asarray(inequality_rhs)
        result = linprog(
            signed_objective,
            A_ub=ub_matrix,
            b_ub=ub_rhs,
            A_eq=eq_matrix,
            b_eq=eq_rhs,
            bounds=bounds,
            method=solver_method,
            options={
                "time_limit": time_limit,
                "presolve": True,
                "dual_feasibility_tolerance": 1e-8,
                "primal_feasibility_tolerance": 1e-8,
                "ipm_optimality_tolerance": 1e-9,
            },
        )
        final_result = result
        record = {
            "round": round_index,
            "active_transform_rows": len(transform_rows),
            "status_code": int(result.status),
            "status_text": str(result.message),
            "success": bool(result.success),
        }
        if result.x is None:
            round_records.append(record)
            break
        final_solution = result.x
        residual = transform_residual(result.x, normalized, combinations)
        flat = [
            (abs(float(residual[i, j_index])), i, j)
            for i in INPUTS
            for j_index, j in enumerate(OUTPUTS)
            if (i, j) not in active
        ]
        flat.sort(reverse=True)
        record.update(
            {
                "max_inactive_transform_residual": (
                    flat[0][0] if flat else 0.0
                ),
                "max_active_transform_residual": max(
                    abs(float(residual[i, OUTPUTS.index(j)]))
                    for i, j in active
                ),
                "normalized_signed_S6": float(objective @ result.x),
            }
        )
        round_records.append(record)
        additions = [
            (i, j)
            for violation, i, j in flat[:add_per_round]
            if violation > 2e-8
        ]
        if not additions:
            break
        for target in additions:
            active.add(target)
            transform_rows.append(
                transform_row(*target, normalized, combinations)
            )

    output: dict[str, object] = {
        "arf_sign": arf_sign,
        "sense": sense,
        "solver_method": solver_method,
        "initial_input_rows": initial_input_rows,
        "status": "NUMERICAL_TELEMETRY_ONLY",
        "free_memory_percent_before": free_before,
        "free_memory_percent_after": free_memory_percent(),
        "elapsed_seconds": round(time.time() - started, 3),
        "base_equality_rows": len(base_eq),
        "base_inequality_rows": len(inequalities),
        "rounds": round_records,
        "limitations": [
            "Rows are generated; inactive transform equations may still be violated.",
            "Floating solver status is not an exact primal or dual certificate.",
            "Very small boundary q-coordinates make this model ill-conditioned.",
        ],
    }
    if final_solution is not None:
        normalized_s6 = float(objective @ final_solution)
        signed_s6 = math.comb(N, 6) * normalized_s6
        n3 = (3.0 / 512.0) * (signed_s6 - 2024484.0)
        residual = transform_residual(
            final_solution,
            normalized,
            combinations,
        )
        output["last_point"] = {
            "normalized_signed_S6": normalized_s6,
            "signed_S6": signed_s6,
            "implied_n3": n3,
            "max_all_transform_residual_q": float(np.max(np.abs(residual))),
            "min_p": float(np.min(final_solution)),
            "max_p": float(np.max(final_solution)),
        }
    if final_result is not None:
        output["last_solver"] = {
            "status_code": int(final_result.status),
            "status_text": str(final_result.message),
            "success": bool(final_result.success),
        }
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--add-per-round", type=int, default=100)
    parser.add_argument("--time-limit", type=float, default=20.0)
    parser.add_argument(
        "--solver-method",
        choices=["highs", "highs-ds", "highs-ipm"],
        default="highs-ds",
    )
    parser.add_argument("--initial-input-rows", type=int, default=1)
    parser.add_argument(
        "--branches",
        nargs="+",
        default=["plus-max", "minus-max", "plus-min", "minus-min"],
    )
    parser.add_argument("--output", type=Path, default=HERE / "numeric-scout.json")
    args = parser.parse_args()

    results = []
    for branch in args.branches:
        sign_text, sense = branch.split("-", 1)
        sign = 1 if sign_text == "plus" else -1
        results.append(
            run_branch(
                sign,
                sense,
                args.rounds,
                args.add_per_round,
                args.time_limit,
                args.solver_method,
                args.initial_input_rows,
            )
        )
    payload = {
        "format": "wave141-bivariate-numeric-scout-v1",
        "claim_label": "UNKNOWN_NUMERICAL",
        "variable_count": NVAR,
        "working_coordinates": "p[i,j]=B[i,j]/C(99,i)",
        "results": results,
        "negative_inference_allowed": False,
    }
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
