#!/usr/bin/env python3
"""Numerical Wave48 + Wave49 endpoint SDP scout.

The exact Wave49 coefficient package supplies 21 additional normalized moment
matrices.  This program appends their full PSD constraints to the frozen
Wave48 normalized real SDP and maximizes the same common active-support
eigenvalue margin.  Every solver result remains numerical CANDIDATE evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import sys
import time
from functools import reduce
from pathlib import Path
from typing import Any, Sequence

import clarabel
import cvxpy as cp
import numpy as np
import scipy
import scs


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE48_CODE = ROOT / "attempts/wave48-conic-moment/combined_sdp.py"
WAVE49_COEFFICIENTS = HERE / "coefficients.json"
DEFAULT_OUTPUT = HERE / "combined-sdp-result.json"
EXPECTED_SHA256 = {
    WAVE48_CODE: "670aa656bed216b7207fadf29905a6b160af43dc29e612583156adc1be9e5053",
    WAVE49_COEFFICIENTS: "66aeb26175643030770c8060a0550d202c56b6a9636e245ef19866a4a9cf308d",
}
EXPECTED_WAVE49_PAYLOAD_SHA256 = (
    "940ed2820a3501e1b5017a5a3dafce55789ce189a754ef94af01954f28a79511"
)
EXPECTED_ROOT_SIZES = {
    0: 32,
    1: 32,
    3: 28,
    7: 22,
    15: 16,
    19: 16,
    20: 32,
    21: 26,
    23: 16,
    28: 28,
    29: 21,
    31: 13,
    54: 18,
    58: 24,
    59: 16,
    62: 16,
    184: 16,
    185: 15,
    207: 10,
    220: 21,
    221: 12,
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_wave48() -> Any:
    payload = WAVE48_CODE.read_bytes()
    if sha256_bytes(payload) != EXPECTED_SHA256[WAVE48_CODE]:
        raise ValueError("frozen Wave48 code SHA-256 mismatch")
    name = "wave49_frozen_wave48"
    spec = importlib.util.spec_from_file_location(name, WAVE48_CODE)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import frozen Wave48 scout")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_coefficients() -> dict[str, Any]:
    payload = WAVE49_COEFFICIENTS.read_bytes()
    if sha256_bytes(payload) != EXPECTED_SHA256[WAVE49_COEFFICIENTS]:
        raise ValueError("Wave49 coefficient file SHA-256 mismatch")
    coefficients = json.loads(payload)
    if (
        coefficients["payload_sha256_without_this_field"]
        != EXPECTED_WAVE49_PAYLOAD_SHA256
    ):
        raise ValueError("Wave49 internal payload SHA-256 mismatch")
    actual = {
        int(family["root_mask"]): int(family["matrix_size"])
        for family in coefficients["families"].values()
    }
    if actual != EXPECTED_ROOT_SIZES:
        raise ValueError("Wave49 root-family census changed")
    return coefficients


def primitive_integer_vector(vector: np.ndarray, scale: int = 1_000_000) -> list[int]:
    rounded = np.rint(vector * scale).astype(object)
    values = [int(value) for value in rounded]
    divisor = reduce(math.gcd, (abs(value) for value in values), 0)
    if divisor:
        values = [value // divisor for value in values]
    first = next((value for value in values if value), 0)
    if first < 0:
        values = [-value for value in values]
    if not any(values):
        raise ValueError("rounded eigenvector vanished")
    return values


def exact_cut(
    family: dict[str, Any],
    vector: list[int],
    lower_counts: dict[int, dict[int, int]],
) -> dict[str, Any]:
    constant = 0
    order7: dict[int, int] = {}
    for record in family["class_coefficients"]:
        quadratic = 0
        for row, column, coefficient in record["upper_entries"]:
            multiplier = 1 if int(row) == int(column) else 2
            quadratic += (
                multiplier
                * int(coefficient)
                * vector[int(row)]
                * vector[int(column)]
            )
        order = int(record["order"])
        mask = int(record["canonical_mask"])
        if order < 7:
            constant += quadratic * int(lower_counts[order][mask])
        elif quadratic:
            order7[mask] = quadratic
    catalog = [[mask, order7[mask]] for mask in sorted(order7)]
    record = {
        "meaning": (
            "(constant_raw_numerator + sum coefficient_H*x_H) / "
            "normalization_denominator >= 0"
        ),
        "primitive_integer_vector": vector,
        "constant_raw_numerator": constant,
        "normalization_denominator": int(
            family["normalization_denominator_at_n99"]
        ),
        "order7_count_coefficients": catalog,
    }
    record["payload_sha256_without_this_field"] = sha256_bytes(
        canonical_payload(record)
    )
    return record


def build_model(wave48: Any, coefficients: dict[str, Any]) -> dict[str, Any]:
    base = wave48.build_problem()
    classes = [int(mask) for mask in base["row_system"]["classes"]]
    class_index = {mask: index for index, mask in enumerate(classes)}
    affine_particular = (
        base["affine_nullspace"] if "affine_nullspace" in base else None
    )
    # Wave48 exposes the affine diagnostics but not its bases. Recompute the
    # identical numerical affine space solely to diagnose Wave49 support.
    particular, nullspace, affine_record = wave48.affine_linear_space(
        base["linear_matrix"], base["linear_rhs"]
    )
    records: list[dict[str, Any]] = []
    constraints = list(base["constraints"])
    for name, family in coefficients["families"].items():
        constant, coefficient_map, public = wave48.moment_affine_map(
            name,
            family,
            base["lower_counts"],
            class_index,
        )
        size = int(public["matrix_size"])
        expression = cp.reshape(
            coefficient_map @ base["z"] + constant.reshape(size * size),
            (size, size),
            order="C",
        )
        expression = (expression + expression.T) / 2
        support_basis, support_record = wave48.active_support_basis(
            constant,
            coefficient_map,
            particular[:208],
            nullspace[:208, :],
        )
        full_psd_constraint = expression >> 0
        constraints.append(full_psd_constraint)
        compressed = support_basis.T @ expression @ support_basis
        if support_basis.shape[1]:
            margin_constraint = (
                compressed
                - base["margin"] * np.eye(support_basis.shape[1])
                >> 0
            )
            constraints.append(margin_constraint)
        else:
            margin_constraint = None
        public.update(
            {
                "source": "wave49",
                "root_mask": int(family["root_mask"]),
                "active_support": {
                    **support_record,
                    "basis_status": "NUMERICAL_DIAGNOSTIC_ONLY",
                },
            }
        )
        records.append(
            {
                "public": public,
                "family": family,
                "constant": constant,
                "coefficient_map": coefficient_map,
                "expression": expression,
                "support_basis": support_basis,
                "compressed": compressed,
                "full_psd_constraint": full_psd_constraint,
                "margin_constraint": margin_constraint,
            }
        )
    if len(records) != 21:
        raise ValueError("Wave49 moment family count changed")
    problem = cp.Problem(cp.Maximize(base["margin"]), constraints)
    wave48.memory_guard("Wave49 problem built")
    return {
        "base": base,
        "problem": problem,
        "records": records,
        "constraints": constraints,
        "affine_recomputation": affine_record,
    }


def matrix_summary(matrix: np.ndarray) -> dict[str, Any]:
    symmetric = (matrix + matrix.T) / 2
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    return {
        "minimum_eigenvalue": float(eigenvalues[0]),
        "maximum_eigenvalue": float(eigenvalues[-1]),
        "trace": float(np.trace(symmetric)),
        "matrix_sha256_float64_le": sha256_bytes(
            np.asarray(symmetric, dtype="<f8").tobytes(order="C")
        ),
        "_minimum_eigenvector": eigenvectors[:, 0],
    }


def evaluate_candidate(wave48: Any, model: dict[str, Any]) -> dict[str, Any] | None:
    base = model["base"]
    if (
        base["z"].value is None
        or base["q"].value is None
        or base["margin"].value is None
    ):
        return None
    z = np.asarray(base["z"].value, dtype=np.float64)
    q = float(base["q"].value)
    existing = wave48.evaluate_candidate(base)
    families = []
    for record in model["records"]:
        size = int(record["public"]["matrix_size"])
        matrix = (
            record["constant"].reshape(size * size)
            + record["coefficient_map"] @ z
        ).reshape((size, size))
        summary = matrix_summary(matrix)
        eigenvector = summary.pop("_minimum_eigenvector")
        primitive = primitive_integer_vector(eigenvector)
        cut = exact_cut(record["family"], primitive, base["lower_counts"])
        raw_value = float(cut["constant_raw_numerator"])
        coefficient_lookup = dict(cut["order7_count_coefficients"])
        for mask, probability in zip(
            base["row_system"]["classes"], z, strict=True
        ):
            raw_value += (
                coefficient_lookup.get(int(mask), 0)
                * float(probability)
                * wave48.SEVEN_TOTAL
            )
        denominator = float(cut["normalization_denominator"])
        basis = record["support_basis"]
        active = (
            np.linalg.eigvalsh(basis.T @ matrix @ basis)
            if basis.shape[1]
            else np.asarray([], dtype=np.float64)
        )
        families.append(
            {
                **record["public"],
                **summary,
                "minimum_active_support_eigenvalue": (
                    None if not active.size else float(active[0])
                ),
                "maximum_active_support_eigenvalue": (
                    None if not active.size else float(active[-1])
                ),
                "candidate_minimum_direction_exact_cut": cut,
                "candidate_cut_value_float": raw_value / denominator,
            }
        )
    residual = (
        base["linear_matrix"] @ np.r_[z, q] - base["linear_rhs"]
    )
    all_probabilities = [
        {
            "canonical_mask": int(mask),
            "value": format(float(value), ".17g"),
        }
        for mask, value in zip(
            base["row_system"]["classes"], z, strict=True
        )
    ]
    return {
        "common_margin": float(base["margin"].value),
        "h11_over_4_scaled": format(q, ".17g"),
        "h11_float": format(4 * wave48.Y_SCALE * q, ".17g"),
        "seven_probability_minimum": float(np.min(z)),
        "seven_probability_sum": float(np.sum(z)),
        "scaled_linear_max_abs_residual": float(np.max(np.abs(residual))),
        "scaled_linear_l2_residual": float(np.linalg.norm(residual)),
        "exact_decimal_linear_residuals": wave48.exact_decimal_residuals(
            base["row_system"], z, q
        ),
        "wave45_wave47": existing,
        "wave49_families": families,
        "minimum_wave49_eigenvalue": min(
            item["minimum_eigenvalue"] for item in families
        ),
        "minimum_wave49_active_support_eigenvalue": min(
            item["minimum_active_support_eigenvalue"]
            for item in families
            if item["minimum_active_support_eigenvalue"] is not None
        ),
        "seven_probabilities_all_208": all_probabilities,
        "seven_probability_vector_sha256_float64_le": sha256_bytes(
            np.asarray(z, dtype="<f8").tobytes()
        ),
    }


def dual_matrix_summary(value: Any) -> dict[str, Any]:
    if value is None:
        return {"available": False}
    matrix = np.asarray(value, dtype=np.float64)
    matrix = (matrix + matrix.T) / 2
    eigenvalues = np.linalg.eigvalsh(matrix)
    return {
        "available": True,
        "shape": list(matrix.shape),
        "frobenius_norm": float(np.linalg.norm(matrix)),
        "minimum_eigenvalue": float(eigenvalues[0]),
        "maximum_eigenvalue": float(eigenvalues[-1]),
        "matrix_sha256_float64_le": sha256_bytes(
            np.asarray(matrix, dtype="<f8").tobytes(order="C")
        ),
        "matrix_float17": [
            [format(float(value), ".17g") for value in row]
            for row in matrix
        ],
    }


def candidate_dual(wave48: Any, model: dict[str, Any]) -> dict[str, Any]:
    records = []
    for record in model["records"]:
        records.append(
            {
                "name": record["public"]["name"],
                "root_mask": record["public"]["root_mask"],
                "full_psd": dual_matrix_summary(
                    record["full_psd_constraint"].dual_value
                ),
                "margin": (
                    {"available": False}
                    if record["margin_constraint"] is None
                    else dual_matrix_summary(
                        record["margin_constraint"].dual_value
                    )
                ),
            }
        )
    return {
        "status": "FLOATING_CANDIDATE_ONLY",
        "wave45_wave47": wave48.dual_summary(model["base"]),
        "wave49": records,
        "exact_rational_certificate_extracted": False,
        "used_as_proof": False,
    }


def classify(record: dict[str, Any]) -> str:
    if record["status"] in {"infeasible", "infeasible_inaccurate"}:
        return "NUMERICAL_INFEASIBILITY_SIGNAL"
    candidate = record["candidate"]
    if candidate is None:
        return "NO_NUMERICAL_CANDIDATE"
    margin = float(candidate["common_margin"])
    residual = float(candidate["scaled_linear_max_abs_residual"])
    minimum = min(
        float(candidate["minimum_wave49_eigenvalue"]),
        float(candidate["wave45_wave47"]["minimum_family_eigenvalue"]),
        float(candidate["seven_probability_minimum"]),
    )
    if margin > 1e-6 and residual <= 1e-7 and minimum >= -1e-7:
        return "NUMERICAL_STRICT_INTERIOR_AGGREGATE_SIGNAL"
    if margin < -1e-6 and residual <= 1e-7:
        return "NUMERICAL_NEGATIVE_MARGIN_SIGNAL"
    return "NUMERICAL_NEAR_BOUNDARY_OR_UNRESOLVED"


def solver_settings(name: str) -> dict[str, Any]:
    if name == "CLARABEL":
        return {
            "max_iter": 750,
            "tol_gap_abs": 1e-8,
            "tol_gap_rel": 1e-8,
            "tol_feas": 1e-8,
            "equilibrate_enable": True,
            "verbose": False,
        }
    if name == "SCS":
        return {
            "max_iters": 150_000,
            "eps": 1e-6,
            "normalize": True,
            "scale": 1.0,
            "acceleration_lookback": 10,
            "verbose": False,
        }
    raise ValueError(name)


def solve_one(wave48: Any, model: dict[str, Any], solver: str) -> dict[str, Any]:
    before = wave48.memory_guard(f"{solver} before Wave49 solve")
    settings = solver_settings(solver)
    started = time.perf_counter()
    exception = None
    objective = None
    try:
        objective = model["problem"].solve(
            solver=solver,
            warm_start=False,
            **settings,
        )
    except Exception as error:
        exception = f"{type(error).__name__}: {error}"
    elapsed = time.perf_counter() - started
    after = wave48.memory_guard(f"{solver} after Wave49 solve")
    candidate = evaluate_candidate(wave48, model)
    result = {
        "solver": solver,
        "settings": settings,
        "status": model["problem"].status,
        "objective": None if objective is None else float(objective),
        "solve_time_seconds_wall": elapsed,
        "solver_stats": {
            "solve_time": model["problem"].solver_stats.solve_time,
            "setup_time": model["problem"].solver_stats.setup_time,
            "num_iters": model["problem"].solver_stats.num_iters,
            "extra_stats_text": repr(model["problem"].solver_stats.extra_stats),
        },
        "exception": exception,
        "candidate": candidate,
        "candidate_dual": candidate_dual(wave48, model),
        "memory_free_percent_before": round(before, 2),
        "memory_free_percent_after": round(after, 2),
        "claim_label": "CANDIDATE_NUMERICAL_ONLY",
        "used_as_exact_evidence": False,
    }
    result["interpretation"] = classify(result)
    return result


def public_model(model: dict[str, Any]) -> dict[str, Any]:
    base = model["base"]
    return {
        "linear_rows": 170,
        "seven_probability_variables": 208,
        "wave45_wave47_moment_families": len(base["moment_records"]),
        "wave49_moment_families": len(model["records"]),
        "total_moment_families": len(base["moment_records"])
        + len(model["records"]),
        "common_margin_definition": (
            "all exact full PSD constraints retained; maximize one common "
            "margin on each coefficient-span compression; Wave45/Wave47 "
            "compressions use their sealed exact faces and Wave49 uses only "
            "a numerical SVD support diagnostic"
        ),
        "wave49_families": [
            record["public"] for record in model["records"]
        ],
        "wave49_affine_support_recomputation": model[
            "affine_recomputation"
        ],
        "normalization": {
            "seven_class_variables": (
                f"x_H / C(99,7), C(99,7)={math.comb(99, 7)}"
            ),
            "h11_over_4": "q=(h11/4)/4158",
        },
    }


def run(solvers: Sequence[str]) -> dict[str, Any]:
    wave48 = load_wave48()
    coefficients = load_coefficients()
    memory_start = wave48.memory_guard("Wave49 SDP start")
    model = build_model(wave48, coefficients)
    solver_results = [
        solve_one(wave48, model, solver) for solver in solvers
    ]
    return {
        "format": "wave49-five-root-combined-sdp-scout-v1",
        "role": "construction",
        "claim_label": "CANDIDATE",
        "scope": (
            "floating normalized real SDP combining Wave48 with all 21 exact "
            "Wave49 five-root one-free attachment moment families"
        ),
        "sources": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": expected,
            }
            for path, expected in EXPECTED_SHA256.items()
        ],
        "software": {
            "python": platform.python_version(),
            "cvxpy": cp.__version__,
            "clarabel": clarabel.__version__,
            "scs": scs.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "installed_cvxpy_solvers": cp.installed_solvers(),
        },
        "resource_guard": {
            "minimum_free_physical_memory_percent": 20.0,
            "free_physical_memory_percent_at_start": round(memory_start, 2),
            "status": "PASS",
        },
        "model": public_model(model),
        "solvers": solver_results,
        "conclusion": {
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "graph_constructed": False,
            "numerical_status_is_not_certificate": True,
            "exact_rational_dual_certificate": "NOT_EXTRACTED",
        },
        "limitations": [
            "All CVXPY, Clarabel, SCS, SVD, and eigenvector results are floating diagnostics.",
            "No solver status is an exact feasibility or infeasibility certificate.",
            "Wave49 active-support bases are numerical diagnostics, while full PSD constraints are retained.",
            "The integer-vector cuts are exact valid PSD inequalities, but their values at a floating candidate are not exact certificates.",
            "An aggregate feasible vector would not construct a graph.",
            "No target-graph automorphism is assumed.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--solvers",
        nargs="+",
        choices=("CLARABEL", "SCS"),
        default=("CLARABEL",),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run(args.solvers)
    payload = canonical_payload(result)
    args.output.write_bytes(payload)
    print(
        json.dumps(
            {
                record["solver"]: {
                    "status": record["status"],
                    "objective": record["objective"],
                    "interpretation": record["interpretation"],
                    "scaled_linear_max_abs_residual": (
                        None
                        if record["candidate"] is None
                        else record["candidate"][
                            "scaled_linear_max_abs_residual"
                        ]
                    ),
                    "minimum_wave49_eigenvalue": (
                        None
                        if record["candidate"] is None
                        else record["candidate"][
                            "minimum_wave49_eigenvalue"
                        ]
                    ),
                }
                for record in result["solvers"]
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"result_sha256={sha256_bytes(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
