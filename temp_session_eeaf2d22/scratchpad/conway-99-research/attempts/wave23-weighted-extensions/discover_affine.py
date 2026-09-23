#!/usr/bin/env python3
"""Discovery-only construction of the affine order-seven count family.

SciPy/HiGHS is used only to locate two adjacent real solutions.  Both are
rounded to integers and checked against every equation with exact Python
integer arithmetic before the affine artifact is written.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import model


Z_MIN = 353
Z_NEXT = 354
Z_MAX = 705


def solve_exactly_roundable(
    matrix: np.ndarray,
    rhs: np.ndarray,
    h11_column: int,
    z: int,
) -> tuple[list[int], dict[str, object]]:
    total = math.comb(model.N, 7)
    bounds: list[tuple[float, float | None]] = [(0.0, None)] * matrix.shape[1]
    fixed = 4 * z / total
    bounds[h11_column] = (fixed, fixed)
    result = linprog(
        np.zeros(matrix.shape[1]),
        A_eq=matrix,
        b_eq=rhs / total,
        bounds=bounds,
        method="highs",
        options={
            "presolve": True,
            "primal_feasibility_tolerance": 1e-9,
            "dual_feasibility_tolerance": 1e-9,
        },
    )
    if result.x is None:
        raise AssertionError(
            f"HiGHS returned no candidate at z={z}: "
            f"status={result.status} {result.message}"
        )
    scaled = result.x * total
    rounded = np.rint(scaled).astype(np.int64)
    maximum_rounding_error = float(np.max(np.abs(scaled - rounded)))
    integer_rhs = rhs.astype(np.int64)
    integer_matrix = matrix.astype(np.int64)
    residual = integer_matrix @ rounded - integer_rhs
    if np.any(residual):
        bad = np.flatnonzero(residual)
        raise AssertionError(
            f"rounded candidate at z={z} fails exact rows "
            f"{bad[:10].tolist()}"
        )
    if int(rounded[h11_column]) != 4 * z:
        raise AssertionError("rounded candidate changed fixed H11")
    if np.any(rounded < 0):
        raise AssertionError("rounded candidate is negative")
    return (
        [int(value) for value in rounded],
        {
            "z": z,
            "solver_status": int(result.status),
            "solver_message": str(result.message),
            "maximum_rounding_error": maximum_rounding_error,
            "exact_equation_residual": 0,
            "support_size": int(np.count_nonzero(rounded)),
        },
    )


def solve_lower_counts() -> tuple[dict[str, object], ...]:
    counts = [model.N]
    records: list[dict[str, object]] = [
        {
            "order": 1,
            "canonical_masks": [0],
            "counts": counts,
        }
    ]
    for order in range(1, 5):
        transition = model.build_transition(order)
        matrix = np.asarray(transition["matrix_rows"], dtype=float)
        integer_rhs = np.asarray(
            model.transition_rhs(transition, counts),
            dtype=np.int64,
        )
        total = math.comb(model.N, order + 1)
        result = linprog(
            np.zeros(len(transition["upper_classes"])),
            A_eq=matrix,
            b_eq=integer_rhs.astype(float) / total,
            bounds=(0, None),
            method="highs",
        )
        if result.x is None:
            raise AssertionError(f"lower transition {order}->{order+1} failed")
        scaled = result.x * total
        rounded = np.rint(scaled).astype(np.int64)
        residual = matrix.astype(np.int64) @ rounded - integer_rhs
        if np.any(residual) or np.any(rounded < 0):
            raise AssertionError(f"lower transition {order}->{order+1} is not exact")
        counts = [int(value) for value in rounded]
        records.append(
            {
                "order": order + 1,
                "canonical_masks": list(transition["upper_classes"]),
                "counts": counts,
                "maximum_rounding_error": float(
                    np.max(np.abs(scaled - rounded))
                ),
            }
        )
    return tuple(records)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("affine-witness.json"),
    )
    arguments = parser.parse_args()

    transition = model.build_transition(6)
    classes = tuple(transition["upper_classes"])
    matrix = np.asarray(transition["matrix_rows"], dtype=float)
    source_counts = dict(zip(model.SOURCE_N_MASKS, model.SIX_COUNTS))
    six_counts = [source_counts[mask] for mask in transition["lower_classes"]]
    rhs = np.asarray(
        model.transition_rhs(transition, six_counts),
        dtype=np.int64,
    )
    h_masks = model.source_h_masks()
    h11_column = classes.index(h_masks[11])

    at_min, run_min = solve_exactly_roundable(
        matrix, rhs, h11_column, Z_MIN
    )
    at_next, run_next = solve_exactly_roundable(
        matrix, rhs, h11_column, Z_NEXT
    )
    delta = [right - left for left, right in zip(at_min, at_next)]
    integer_matrix = matrix.astype(np.int64)
    if np.any(integer_matrix @ np.asarray(delta, dtype=np.int64)):
        raise AssertionError("affine delta is not in the exact integer kernel")

    at_max = [
        base + (Z_MAX - Z_MIN) * step
        for base, step in zip(at_min, delta)
    ]
    if min(at_min) < 0 or min(at_max) < 0:
        raise AssertionError("affine family is negative at an interval endpoint")
    if sum(at_min) != math.comb(model.N, 7) or sum(delta) != 0:
        raise AssertionError("affine family has the wrong total")

    # The other 18 source formulas are comparison targets, not solver inputs.
    h_comparison = []
    for index, (mask, column) in enumerate(
        (mask, classes.index(mask)) for mask in h_masks
    ):
        expected_min = model.published_hamiltonian_counts(
            model.N3, 4 * Z_MIN
        )[index]
        expected_next = model.published_hamiltonian_counts(
            model.N3, 4 * Z_NEXT
        )[index]
        actual_min = at_min[column]
        actual_next = at_next[column]
        if (actual_min, actual_next) != (expected_min, expected_next):
            raise AssertionError(f"published H_{index} affine formula differs")
        h_comparison.append(
            {
                "source_index": index,
                "canonical_mask": mask,
                "count_at_z_min": actual_min,
                "delta_per_z": actual_next - actual_min,
                "used_as_solver_input": index == 11,
            }
        )

    lower_counts = solve_lower_counts()
    transition5 = model.build_transition(5)
    five_counts = lower_counts[-1]["counts"]
    rhs5 = np.asarray(
        model.transition_rhs(transition5, five_counts),
        dtype=np.int64,
    )
    source_six_canonical = np.asarray(
        [source_counts[mask] for mask in transition5["upper_classes"]],
        dtype=np.int64,
    )
    residual5 = (
        np.asarray(transition5["matrix_rows"], dtype=np.int64)
        @ source_six_canonical
        - rhs5
    )
    if np.any(residual5):
        raise AssertionError("published six-count vector fails exact 5->6 gate")

    payload = {
        "schema_version": 1,
        "claim_label": "CANDIDATE_PENDING_INDEPENDENT_VERIFICATION",
        "scope": (
            "All orbit-refined one-vertex extension equations through order "
            "seven for srg(99,14,1,2), at n3=705 and every integer "
            "z=h11/4 in 353,...,705"
        ),
        "parameters": {
            "n": model.N,
            "k": model.K,
            "lambda": model.LAMBDA,
            "mu": model.MU,
            "n3": model.N3,
            "z_min": Z_MIN,
            "z_max": Z_MAX,
            "h11_min": 4 * Z_MIN,
            "h11_max": 4 * Z_MAX,
        },
        "independent_lower_counts": list(lower_counts),
        "source_six_count_gate": {
            "transition": "5->6",
            "rows_checked": len(transition5["matrix_rows"]),
            "exact_maximum_residual": int(np.max(np.abs(residual5))),
        },
        "order_seven_affine_family": {
            "coordinate": "z=h11/4",
            "records": [
                {
                    "canonical_mask": mask,
                    "count_at_z_min": base,
                    "delta_per_z": step,
                }
                for mask, base, step in zip(classes, at_min, delta)
            ],
            "exact_rows_checked": len(transition["matrix_rows"]),
            "minimum_count_at_z_min": min(at_min),
            "minimum_count_at_z_max": min(at_max),
            "support_size_at_z_min": sum(value > 0 for value in at_min),
            "support_size_at_z_max": sum(value > 0 for value in at_max),
            "total_at_every_z": math.comb(model.N, 7),
        },
        "hamiltonian_comparison": {
            "solver_inputs": ["H_11=4z"],
            "not_solver_inputs": [
                f"H_{index}" for index in range(19) if index != 11
            ],
            "records": h_comparison,
            "all_19_source_affine_formulas_match": True,
        },
        "discovery_runs": [run_min, run_next],
        "warnings": [
            "Solver exit codes are not certificates.",
            "The exact affine count family is not a graph construction.",
            "The H-panel-to-mask alignment remains a pinned source interpretation.",
        ],
    }
    arguments.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "output": arguments.output.as_posix(),
        "rows_6_to_7": len(transition["matrix_rows"]),
        "support_at_z_min": sum(value > 0 for value in at_min),
        "support_at_z_max": sum(value > 0 for value in at_max),
        "minimum_at_z_min": min(at_min),
        "minimum_at_z_max": min(at_max),
        "hamiltonian_formulas_matched": 19,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
