#!/usr/bin/env python3
"""Numerical scout for the Wave147 two-root order-eight endpoint SDP.

This is reconnaissance only.  Solver status, including numerical
infeasibility, is not a proof.  The script uses normalized induced-count
variables and the exact coefficient artifacts already frozen in the
repository.  A rigorous exclusion would require an independently replayed
exact rational dual certificate.
"""

from __future__ import annotations

import argparse
import ctypes
import gzip
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
from scipy import sparse


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
COEFFICIENTS = ROOT / "attempts/wave147-alternative-lane/coefficients.json.gz"
WAVE147_RESULT = ROOT / "attempts/wave147-alternative-lane/exact-results.json"
ROW_SYSTEM = ROOT / "attempts/wave44-rooted-flags/row-system.json"
WAVE45 = ROOT / "attempts/wave45-flag-moment/flag_moment-v1.py"
MARKED_ROWS = ROOT / "attempts/wave148-marked-order8/marked-rows.json.gz"

N = 99
N3 = 4158
Y_MIN = 2079
Y_MAX = 4158
MIN_FREE_MEMORY_PERCENT = 15.0


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_phys", ctypes.c_ulonglong),
        ("avail_phys", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("avail_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("avail_virtual", ctypes.c_ulonglong),
        ("avail_extended_virtual", ctypes.c_ulonglong),
    ]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def memory_record(label: str) -> dict[str, float | str]:
    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    require(bool(ok), "GlobalMemoryStatusEx failed")
    free_percent = 100.0 * status.avail_phys / status.total_phys
    require(
        free_percent >= MIN_FREE_MEMORY_PERCENT,
        f"free physical memory {free_percent:.2f}% is below the 15% floor",
    )
    return {
        "label": label,
        "free_physical_memory_percent": free_percent,
        "available_physical_gib": status.avail_phys / 2**30,
        "total_physical_gib": status.total_phys / 2**30,
    }


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_inputs(include_marked: bool) -> dict[str, Any]:
    coefficient_payload = json.loads(gzip.decompress(COEFFICIENTS.read_bytes()))
    wave147_result = json.loads(WAVE147_RESULT.read_text(encoding="utf-8"))
    row_system = json.loads(ROW_SYSTEM.read_text(encoding="utf-8"))
    marked_rows = (
        json.loads(gzip.decompress(MARKED_ROWS.read_bytes()))
        if include_marked
        else None
    )

    wave45 = load_module("wave150_wave45_frozen", WAVE45)
    classes = wave45.admissible_classes(wave45.build_catalogues())
    lower_counts = wave45.target_lower_counts(classes)

    require(tuple(classes) == (4, 5, 6, 7), "lower class orders changed")
    require(len(classes[5]) == 21, "order-five class count changed")
    require(len(classes[6]) == 62, "order-six class count changed")
    require(len(classes[7]) == 208, "order-seven class count changed")

    classes8 = tuple(
        int(mask) for mask in wave147_result["class_streams"]["8"]["canonical_masks"]
    )
    require(len(classes8) == 916, "order-eight class count changed")
    require(
        tuple(row_system["classes"]) == tuple(classes[7]),
        "Wave44 and Wave147 order-seven streams disagree",
    )

    for family in coefficient_payload["families"].values():
        by_order: dict[int, list[int]] = {order: [] for order in range(5, 9)}
        for record in family["class_coefficients"]:
            by_order[int(record["order"])].append(int(record["canonical_mask"]))
        require(tuple(by_order[5]) == tuple(classes[5]), "order-five stream drift")
        require(tuple(by_order[6]) == tuple(classes[6]), "order-six stream drift")
        require(tuple(by_order[7]) == tuple(classes[7]), "order-seven stream drift")
        require(tuple(by_order[8]) == classes8, "order-eight stream drift")

    return {
        "coefficient_payload": coefficient_payload,
        "row_system": row_system,
        "classes": classes,
        "classes8": classes8,
        "lower_counts": lower_counts,
        "marked_rows": marked_rows,
    }


def deletion_matrix(
    payload: dict[str, Any],
    classes7: tuple[int, ...],
    classes8: tuple[int, ...],
) -> sparse.csr_array:
    index7 = {mask: index for index, mask in enumerate(classes7)}
    index8 = {mask: index for index, mask in enumerate(classes8)}
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[float] = []
    rows = payload["order7_to_order8_deletion_equations"]
    require(len(rows) == len(classes7), "deletion row count changed")
    for record in rows:
        row = index7[int(record["order7_mask"])]
        require(int(record["left_multiplier"]) == 92, "bad deletion multiplier")
        for mask8, multiplicity in record["terms_order8_mask_multiplicity"]:
            row_indices.append(row)
            column_indices.append(index8[int(mask8)])
            values.append(float(multiplicity) / 8.0)
    matrix = sparse.coo_array(
        (values, (row_indices, column_indices)),
        shape=(len(classes7), len(classes8)),
    ).tocsr()
    require(np.allclose(np.asarray(matrix.sum(axis=0)).ravel(), 1.0), "bad deletion columns")
    return matrix


def normalized_wave44_rows(
    row_system: dict[str, Any],
) -> tuple[sparse.csr_array, np.ndarray, np.ndarray, list[str]]:
    rows: list[list[int]] = []
    rhs: list[int] = []
    labels: list[str] = []
    for family_name in ("base", "vertex", "edge", "nonedge"):
        family = row_system["families"][family_name]
        for local_index, (row, target) in enumerate(
            zip(family["rows"], family["rhs"], strict=True)
        ):
            require(len(row) == 209, "Wave44 row width changed")
            rows.append([int(value) for value in row])
            rhs.append(int(target))
            labels.append(f"{family_name}:{local_index}")

    c7 = math.comb(N, 7)
    matrix7 = np.asarray([row[:-1] for row in rows], dtype=np.float64) * c7
    vector_y = np.asarray([row[-1] for row in rows], dtype=np.float64) * Y_MAX
    targets = np.asarray(rhs, dtype=np.float64)
    scales = np.maximum.reduce(
        [
            np.max(np.abs(matrix7), axis=1),
            np.abs(vector_y),
            np.abs(targets),
            np.ones(len(rows)),
        ]
    )
    return (
        sparse.csr_array(matrix7 / scales[:, None]),
        vector_y / scales,
        targets / scales,
        labels,
    )


def normalized_marked_rows(
    payload: dict[str, Any],
    classes7: tuple[int, ...],
    classes8: tuple[int, ...],
) -> tuple[sparse.csr_array, sparse.csr_array, dict[str, int]]:
    index7 = {mask: index for index, mask in enumerate(classes7)}
    index8 = {mask: index for index, mask in enumerate(classes8)}
    c8_over_c7 = math.comb(N, 8) / math.comb(N, 7)
    require(c8_over_c7 == 11.5, "unexpected binomial ratio")

    rows7: list[int] = []
    columns7: list[int] = []
    values7: list[float] = []
    rows8: list[int] = []
    columns8: list[int] = []
    values8: list[float] = []
    row_scales: list[float] = []
    zero_rows = 0
    records = payload["vertex_rows"] + payload["ordered_pair_rows"]
    for row_index, record in enumerate(records):
        lhs = float(record["lhs_coefficient"])
        terms = [
            (index8[int(mask)], c8_over_c7 * float(coefficient))
            for mask, coefficient in record["terms_order8_mask_coefficient"]
        ]
        scale = max([abs(lhs), *(abs(value) for _, value in terms), 1.0])
        row_scales.append(scale)
        if lhs:
            rows7.append(row_index)
            columns7.append(index7[int(record["order7_mask"])])
            values7.append(lhs / scale)
        for column, value in terms:
            rows8.append(row_index)
            columns8.append(column)
            values8.append(value / scale)
        if not lhs and not terms:
            zero_rows += 1

    matrix7 = sparse.coo_array(
        (values7, (rows7, columns7)),
        shape=(len(records), len(classes7)),
    ).tocsr()
    matrix8 = sparse.coo_array(
        (values8, (rows8, columns8)),
        shape=(len(records), len(classes8)),
    ).tocsr()
    require(zero_rows == 893, "zero-capacity marked-row count changed")
    return matrix7, matrix8, {
        "total_rows": len(records),
        "vertex_rows": len(payload["vertex_rows"]),
        "ordered_pair_rows": len(payload["ordered_pair_rows"]),
        "zero_rows": zero_rows,
        "order7_nonzeros": int(matrix7.nnz),
        "order8_nonzeros": int(matrix8.nnz),
    }


def moment_expression(
    family: dict[str, Any],
    classes7: tuple[int, ...],
    classes8: tuple[int, ...],
    lower_counts: dict[int, dict[int, int]],
    p7: cp.Variable,
    p8: cp.Variable,
    root_count: int,
) -> tuple[cp.Expression, np.ndarray, dict[str, Any]]:
    size = int(family["matrix_size"])
    index7 = {mask: index for index, mask in enumerate(classes7)}
    index8 = {mask: index for index, mask in enumerate(classes8)}
    matrix_scale = root_count * math.comb(N - 2, 3) ** 2

    constant = np.zeros(size * size, dtype=np.float64)
    mean_counts = np.zeros(size, dtype=np.float64)
    rows7: list[int] = []
    columns7: list[int] = []
    values7: list[float] = []
    rows8: list[int] = []
    columns8: list[int] = []
    values8: list[float] = []

    def add_entry(
        target_rows: list[int],
        target_columns: list[int],
        target_values: list[float],
        row: int,
        column: int,
        variable_index: int,
        value: float,
    ) -> None:
        target_rows.append(row * size + column)
        target_columns.append(variable_index)
        target_values.append(value)
        if row != column:
            target_rows.append(column * size + row)
            target_columns.append(variable_index)
            target_values.append(value)

    for record in family["class_coefficients"]:
        order = int(record["order"])
        mask = int(record["canonical_mask"])
        for row, column, integer_value in record["upper_entries"]:
            value = float(integer_value) / matrix_scale
            if order in (5, 6):
                contribution = lower_counts[order][mask] * value
                constant[row * size + column] += contribution
                if row != column:
                    constant[column * size + row] += contribution
                if order == 5:
                    require(row == column, "order-five coefficient is not diagonal")
                    mean_counts[row] += (
                        lower_counts[order][mask] * float(integer_value)
                    )
            elif order == 7:
                add_entry(
                    rows7,
                    columns7,
                    values7,
                    int(row),
                    int(column),
                    index7[mask],
                    math.comb(N, 7) * value,
                )
            elif order == 8:
                add_entry(
                    rows8,
                    columns8,
                    values8,
                    int(row),
                    int(column),
                    index8[mask],
                    math.comb(N, 8) * value,
                )
            else:
                raise AssertionError(f"unexpected class order {order}")

    map7 = sparse.coo_array(
        (values7, (rows7, columns7)),
        shape=(size * size, len(classes7)),
    ).tocsr()
    map8 = sparse.coo_array(
        (values8, (rows8, columns8)),
        shape=(size * size, len(classes8)),
    ).tocsr()
    vector = constant + map7 @ p7 + map8 @ p8
    matrix = cp.reshape(vector, (size, size), order="C")
    free_triples = math.comb(N - 2, 3)
    require(
        abs(float(mean_counts.sum()) - root_count * free_triples) < 0.5,
        "flag first-moment total changed",
    )
    mean_probability = mean_counts / (root_count * free_triples)
    return matrix, mean_probability, {
        "size": size,
        "scale": matrix_scale,
        "mean_probability_sum": float(mean_probability.sum()),
        "mean_probability_nonzeros": int(np.count_nonzero(mean_probability)),
        "constant_nonzeros": int(np.count_nonzero(constant)),
        "order7_nonzeros": int(map7.nnz),
        "order8_nonzeros": int(map8.nnz),
    }


def numeric_summary(
    p7: cp.Variable,
    p8: cp.Variable,
    y_fraction: cp.Variable,
    deletion: sparse.csr_array,
    row_matrix: sparse.csr_array,
    row_y: np.ndarray,
    row_rhs: np.ndarray,
    moments: dict[str, cp.Expression],
    centered_moments: dict[str, cp.Expression],
    marked_matrices: tuple[sparse.csr_array, sparse.csr_array] | None,
) -> dict[str, Any]:
    if p7.value is None or p8.value is None or y_fraction.value is None:
        return {"candidate_available": False}

    values7 = np.asarray(p7.value, dtype=np.float64).ravel()
    values8 = np.asarray(p8.value, dtype=np.float64).ravel()
    y_value = float(np.asarray(y_fraction.value).item())
    row_residual = row_matrix @ values7 + row_y * y_value - row_rhs
    deletion_residual = values7 - deletion @ values8
    marked_residual = (
        None
        if marked_matrices is None
        else marked_matrices[0] @ values7 - marked_matrices[1] @ values8
    )

    moment_records: dict[str, Any] = {}
    for name, expression in moments.items():
        matrix = np.asarray(expression.value, dtype=np.float64)
        matrix = (matrix + matrix.T) / 2.0
        eigenvalues = np.linalg.eigvalsh(matrix)
        centered = np.asarray(centered_moments[name].value, dtype=np.float64)
        centered = (centered + centered.T) / 2.0
        centered_eigenvalues = np.linalg.eigvalsh(centered)
        moment_records[name] = {
            "minimum_eigenvalue": float(eigenvalues[0]),
            "maximum_eigenvalue": float(eigenvalues[-1]),
            "negative_eigenvalues_below_minus_1e_7": int(
                np.count_nonzero(eigenvalues < -1e-7)
            ),
            "numerical_rank_above_1e_8": int(np.count_nonzero(eigenvalues > 1e-8)),
            "centered_minimum_eigenvalue": float(centered_eigenvalues[0]),
            "centered_maximum_eigenvalue": float(centered_eigenvalues[-1]),
            "centered_negative_eigenvalues_below_minus_1e_7": int(
                np.count_nonzero(centered_eigenvalues < -1e-7)
            ),
            "centered_numerical_rank_above_1e_8": int(
                np.count_nonzero(centered_eigenvalues > 1e-8)
            ),
        }

    return {
        "candidate_available": True,
        "y_fraction": y_value,
        "y_approx": Y_MAX * y_value,
        "p7_minimum": float(values7.min()),
        "p8_minimum": float(values8.min()),
        "p7_sum": float(values7.sum()),
        "p8_sum": float(values8.sum()),
        "wave44_max_abs_scaled_residual": float(np.max(np.abs(row_residual))),
        "deletion_max_abs_density_residual": float(
            np.max(np.abs(deletion_residual))
        ),
        "marked_max_abs_scaled_residual": (
            None
            if marked_residual is None
            else float(np.max(np.abs(marked_residual)))
        ),
        "moments": moment_records,
        "p7_density": values7.tolist(),
        "p8_density": values8.tolist(),
    }


def solve(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    memory = [memory_record("before_load")]
    inputs = load_inputs(args.include_marked)
    memory.append(memory_record("after_load"))

    payload = inputs["coefficient_payload"]
    classes7 = tuple(int(mask) for mask in inputs["classes"][7])
    classes8 = tuple(int(mask) for mask in inputs["classes8"])
    lower_counts = inputs["lower_counts"]

    deletion = deletion_matrix(payload, classes7, classes8)
    row_matrix, row_y, row_rhs, row_labels = normalized_wave44_rows(
        inputs["row_system"]
    )
    marked_metadata = None
    marked_matrices = None
    if inputs["marked_rows"] is not None:
        marked7, marked8, marked_metadata = normalized_marked_rows(
            inputs["marked_rows"], classes7, classes8
        )
        marked_matrices = (marked7, marked8)

    p7 = cp.Variable(
        len(classes7), nonneg=not args.explicit_bounds, name="p7"
    )
    p8 = cp.Variable(
        len(classes8), nonneg=not args.explicit_bounds, name="p8"
    )
    y_fraction = cp.Variable(name="y_fraction")
    margin = cp.Variable(name="common_psd_margin")

    constraints: list[cp.Constraint] = []
    constraint_labels: list[str] = []

    def add_constraint(label: str, constraint: cp.Constraint) -> None:
        constraint_labels.append(label)
        constraints.append(constraint)

    add_constraint("sum_p7", cp.sum(p7) == 1)
    add_constraint("sum_p8", cp.sum(p8) == 1)
    if args.explicit_bounds:
        add_constraint("p7_nonnegative", p7 >= 0)
        add_constraint("p8_nonnegative", p8 >= 0)
    add_constraint("deletion", p7 == deletion @ p8)
    add_constraint(
        "wave44",
        row_matrix @ p7 + row_y * y_fraction == row_rhs,
    )
    add_constraint("y_lower", y_fraction >= Y_MIN / Y_MAX)
    add_constraint("y_upper", y_fraction <= 1)
    if marked_matrices is not None:
        add_constraint(
            "marked",
            marked_matrices[0] @ p7 == marked_matrices[1] @ p8,
        )

    moments: dict[str, cp.Expression] = {}
    centered_moments: dict[str, cp.Expression] = {}
    moment_metadata: dict[str, Any] = {}
    family_roots = {
        "ordered_edge": N * 14,
        "ordered_nonedge": N * 84,
    }
    selected_families = (
        tuple(family_roots)
        if args.family == "both"
        else (args.family,)
    )
    for name in selected_families:
        root_count = family_roots[name]
        expression, mean_probability, metadata = moment_expression(
            payload["families"][name],
            classes7,
            classes8,
            lower_counts,
            p7,
            p8,
            root_count,
        )
        moments[name] = expression
        centered = expression - np.outer(mean_probability, mean_probability)
        centered_moments[name] = centered
        moment_metadata[name] = metadata
        if args.force_zero_covariance:
            add_constraint(f"{name}_centered_zero", centered == 0)
        elif args.diagonal_only:
            add_constraint(f"{name}_centered_diagonal", cp.diag(centered) >= 0)
        else:
            constrained_matrix = centered if args.centered else expression
            add_constraint(
                f"{name}_{'centered' if args.centered else 'raw'}_psd",
                constrained_matrix - margin * np.eye(metadata["size"]) >> 0
            )

    linear_mode = args.force_zero_covariance or args.diagonal_only
    objective = cp.Minimize(0) if linear_mode else cp.Maximize(margin)
    problem = cp.Problem(objective, constraints)
    memory.append(memory_record("before_solve"))
    solve_kwargs: dict[str, Any] = {"verbose": args.verbose}
    if args.solver == "SCS":
        solve_kwargs.update(
            {
                "eps": args.eps,
                "max_iters": args.max_iters,
                "time_limit_secs": args.time_limit,
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
    elif args.solver == "HIGHS":
        require(linear_mode, "HIGHS requires a linear-mode option")
        solve_kwargs.update(
            {
                "time_limit": float(args.time_limit),
                "presolve": "off" if args.no_presolve else "on",
                "primal_feasibility_tolerance": max(args.eps, 1e-10),
                "dual_feasibility_tolerance": max(args.eps, 1e-10),
            }
        )
    else:
        raise AssertionError(f"unsupported solver {args.solver}")

    try:
        value = problem.solve(solver=args.solver, **solve_kwargs)
        solver_error = None
    except Exception as exc:  # numerical scout must preserve solver failures
        value = None
        solver_error = f"{type(exc).__name__}: {exc}"
    memory.append(memory_record("after_solve"))

    infeasibility_dual_ray = None
    if problem.status in {"infeasible", "infeasible_inaccurate"}:
        blocks = []
        total_nonzeros = 0
        for label, constraint in zip(constraint_labels, constraints, strict=True):
            dual = constraint.dual_value
            if dual is None:
                blocks.append({"label": label, "available": False})
                continue
            values = np.asarray(dual, dtype=np.float64).ravel()
            support = [
                [int(index), float(value)]
                for index, value in enumerate(values)
                if abs(value) > 1e-12
            ]
            total_nonzeros += len(support)
            blocks.append(
                {
                    "label": label,
                    "available": True,
                    "shape": list(np.asarray(dual).shape),
                    "nonzero_support": support,
                    "minimum": float(values.min()) if values.size else None,
                    "maximum": float(values.max()) if values.size else None,
                }
            )
        infeasibility_dual_ray = {
            "source": "CVXPY mapping of the HiGHS floating dual ray",
            "claim_label": "CANDIDATE",
            "zero_threshold": 1e-12,
            "total_nonzeros": total_nonzeros,
            "blocks": blocks,
        }

    candidate = numeric_summary(
        p7,
        p8,
        y_fraction,
        deletion,
        row_matrix,
        row_y,
        row_rhs,
        moments,
        centered_moments,
        marked_matrices,
    )
    elapsed = time.time() - started
    stats = problem.solver_stats
    result = {
        "format": "wave150-order8-endpoint-sdp-scout-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Numerical common-margin scout for the n3=4158 two-root order-eight "
            "relaxation using Wave44 rows, ordinary 7->8 deletion, nonnegativity, "
            "both Wave147 PSD blocks, and optionally the Wave148 marked rows."
        ),
        "target": {
            "srg": [99, 14, 1, 2],
            "n3": N3,
            "endpoint_equivalence": "n3=4158 iff the induced prism count is zero",
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path)
            for path in (
                COEFFICIENTS,
                WAVE147_RESULT,
                ROW_SYSTEM,
                WAVE45,
                *([MARKED_ROWS] if args.include_marked else []),
            )
        },
        "model": {
            "order7_density_variables": len(classes7),
            "order8_density_variables": len(classes8),
            "wave44_rows": len(row_labels),
            "deletion_rows": deletion.shape[0],
            "deletion_nonzeros": int(deletion.nnz),
            "moment_blocks": moment_metadata,
            "objective": "maximize a common normalized PSD eigenvalue margin",
            "centered_covariance_psd": args.centered,
            "centered_covariance_forced_zero": args.force_zero_covariance,
            "centered_covariance_diagonal_only": args.diagonal_only,
            "selected_moment_families": list(selected_families),
            "marked_order8_rows_included": args.include_marked,
            "marked_rows": marked_metadata,
        },
        "solver": {
            "name": args.solver,
            "status": problem.status,
            "objective_value": (
                None
                if value is None or not math.isfinite(float(value))
                else float(value)
            ),
            "error": solver_error,
            "solve_time_seconds": getattr(stats, "solve_time", None),
            "setup_time_seconds": getattr(stats, "setup_time", None),
            "iterations": getattr(stats, "num_iters", None),
            "elapsed_wall_seconds": elapsed,
            "eps": args.eps,
            "max_iters": args.max_iters,
            "time_limit_seconds": args.time_limit,
            "infeasibility_dual_ray": infeasibility_dual_ray,
        },
        "candidate": candidate,
        "memory": memory,
        "limitations": [
            (
                "Wave148 marked degree/common-neighbor order-eight rows are included."
                if args.include_marked
                else "No marked degree/common-neighbor order-eight rows are included."
            ),
            "A floating solver status or negative common margin is not a proof.",
            "A numerical feasible point is not an exact rational witness and is not a graph.",
            "A strict bound requires an independently replayed exact rational SDP dual certificate.",
        ],
        "conclusion": {
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--solver", choices=("SCS", "CLARABEL", "HIGHS"), default="SCS"
    )
    parser.add_argument("--eps", type=float, default=1e-6)
    parser.add_argument("--max-iters", type=int, default=20_000)
    parser.add_argument("--time-limit", type=int, default=600)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--include-marked", action="store_true")
    parser.add_argument("--centered", action="store_true")
    parser.add_argument("--force-zero-covariance", action="store_true")
    parser.add_argument("--diagonal-only", action="store_true")
    parser.add_argument(
        "--family",
        choices=("both", "ordered_edge", "ordered_nonedge"),
        default="both",
    )
    parser.add_argument("--explicit-bounds", action="store_true")
    parser.add_argument("--no-presolve", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = solve(args)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
        print(
            json.dumps(
                {
                    "output": str(args.output),
                    "status": result["solver"]["status"],
                    "objective_value": result["solver"]["objective_value"],
                    "candidate_available": result["candidate"]["candidate_available"],
                    "elapsed_wall_seconds": result["solver"]["elapsed_wall_seconds"],
                },
                sort_keys=True,
            )
        )
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
