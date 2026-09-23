#!/usr/bin/env python3
"""Numerical combined moment-SDP scout for the Conway-99 endpoint.

This discovery script combines the exact Wave 44 170-row count system,
nonnegativity, the three sealed Wave 45 finite moment families, and all eight
sealed Wave 47 three-root moment families.  It maximizes a common normalized
minimum-eigenvalue margin.  Floating solver output is always CANDIDATE/UNKNOWN.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import json
import math
import os
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

import clarabel
import cvxpy as cp
import numpy as np
import scipy
import scipy.sparse as sp
import scs


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROW_SYSTEM = ROOT / "attempts/wave44-rooted-flags/row-system.json"
W45_COEFFICIENTS = (
    ROOT
    / "attempts/wave45-flag-moment"
    / "checkpoint-v1-moment-coefficients.json"
)
W45_CODE = (
    ROOT / "attempts/wave45-flag-moment" / "flag_moment-v1.py"
)
W47_HANDOFF = (
    ROOT / "attempts/wave47-three-root-moment/compact-handoff.json"
)
W47_COEFFICIENTS = (
    ROOT / "attempts/wave47-three-root-moment/coefficients.json"
)
EXACT_FACES = HERE / "exact-faces.json"
DEFAULT_OUTPUT = HERE / "combined-sdp-result.json"

EXPECTED_SHA256 = {
    ROW_SYSTEM: "fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722",
    W45_COEFFICIENTS: "ffcf9f9942446d66c3559d97954217af3ba17c1978ea9417c6e99920d4a45420",
    W45_CODE: "21ed58592eeced3433fdff0b98ae4f963b269ed0b39be05322f1dac42ce1be70",
    W47_HANDOFF: "8b74110bc6ae983e288d448cd1a963f81521f178e8280bbbf5864274a1639a47",
    W47_COEFFICIENTS: "07b55f06ff8f7d5f2de53d92a3222366e122a7306028752ecd31c10962a824b3",
    EXACT_FACES: "49d157a2c6025f7a7d1149619959e3f488229d619a5c65a03a79e7a71a93f066",
}
MIN_FREE_MEMORY_PERCENT = 20.0
N = 99
N3 = 4158
SEVEN_TOTAL = math.comb(N, 7)
Y_SCALE = N3


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def free_memory_percent() -> float:
    if os.name == "nt":
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

        state = MEMORYSTATUSEX()
        state.dwLength = ctypes.sizeof(state)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
            raise OSError("GlobalMemoryStatusEx failed")
        return 100.0 * state.ullAvailPhys / state.ullTotalPhys
    available = os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    total = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    return 100.0 * available / total


def memory_guard(stage: str) -> float:
    free = free_memory_percent()
    if free < MIN_FREE_MEMORY_PERCENT:
        raise MemoryError(
            f"{stage}: {free:.2f}% free physical memory is below "
            f"{MIN_FREE_MEMORY_PERCENT:.2f}%"
        )
    return free


def load_frozen_json(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    expected = EXPECTED_SHA256[path]
    if sha256_bytes(payload) != expected:
        raise ValueError(f"{path.name} SHA-256 mismatch")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain an object")
    return data


def load_wave45_module() -> Any:
    payload = W45_CODE.read_bytes()
    if sha256_bytes(payload) != EXPECTED_SHA256[W45_CODE]:
        raise ValueError("Wave45 code SHA-256 mismatch")
    name = "wave48_frozen_wave45"
    spec = importlib.util.spec_from_file_location(name, W45_CODE)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen Wave45 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def exact_lower_counts() -> tuple[dict[int, dict[int, int]], dict[str, Any]]:
    module = load_wave45_module()
    catalogues = module.build_catalogues()
    classes = module.admissible_classes(catalogues)
    counts = module.target_lower_counts(classes)
    record = {
        str(order): {
            "count": len(counts[order]),
            "total": sum(counts[order].values()),
            "sha256": sha256_bytes(
                json.dumps(
                    [
                        [mask, counts[order][mask]]
                        for mask in sorted(counts[order])
                    ],
                    separators=(",", ":"),
                ).encode("ascii")
            ),
        }
        for order in sorted(counts)
    }
    return counts, record


def scaled_linear_system(
    row_system: dict[str, Any],
) -> tuple[sp.csr_matrix, np.ndarray, list[dict[str, Any]]]:
    rows: list[list[int]] = []
    rhs: list[int] = []
    row_names: list[tuple[str, int]] = []
    for family in ("base", "vertex", "edge", "nonedge"):
        block = row_system["families"][family]
        for index, (row, target) in enumerate(
            zip(block["rows"], block["rhs"], strict=True)
        ):
            if len(row) != 209:
                raise ValueError("Wave44 row width changed")
            rows.append(row)
            rhs.append(target)
            row_names.append((family, index))
    if len(rows) != 170:
        raise ValueError("Wave44 row count changed")

    data: list[float] = []
    row_indices: list[int] = []
    column_indices: list[int] = []
    scaled_rhs: list[float] = []
    scaling_records: list[dict[str, Any]] = []
    for row_index, (row, target) in enumerate(zip(rows, rhs, strict=True)):
        scaled_coefficients = [
            coefficient * (SEVEN_TOTAL if column < 208 else Y_SCALE)
            for column, coefficient in enumerate(row)
        ]
        scale = max(
            1,
            abs(target),
            *(abs(value) for value in scaled_coefficients),
        )
        for column, value in enumerate(scaled_coefficients):
            if value:
                row_indices.append(row_index)
                column_indices.append(column)
                data.append(value / scale)
        scaled_rhs.append(target / scale)
        scaling_records.append(
            {
                "family": row_names[row_index][0],
                "family_row": row_names[row_index][1],
                "positive_scale": scale,
            }
        )
    matrix = sp.coo_matrix(
        (data, (row_indices, column_indices)),
        shape=(170, 209),
        dtype=np.float64,
    ).tocsr()
    return matrix, np.asarray(scaled_rhs), scaling_records


def add_upper_entry(
    matrix: np.ndarray,
    row: int,
    column: int,
    value: float,
) -> None:
    matrix[row, column] += value
    if row != column:
        matrix[column, row] += value


def moment_affine_map(
    family_name: str,
    family: dict[str, Any],
    lower_counts: dict[int, dict[int, int]],
    class_index: dict[int, int],
) -> tuple[np.ndarray, sp.csr_matrix, dict[str, Any]]:
    size = int(family["matrix_size"])
    denominator = int(
        family.get(
            "probability_normalization_denominator_at_n99",
            family.get("normalization_denominator_at_n99"),
        )
    )
    constant = np.zeros((size, size), dtype=np.float64)
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[float] = []
    orders: set[int] = set()
    order7_records = 0
    for record in family["class_coefficients"]:
        order = int(record["order"])
        mask = int(record["canonical_mask"])
        orders.add(order)
        if order < 7:
            count = lower_counts[order][mask]
            for row, column, coefficient in record["upper_entries"]:
                add_upper_entry(
                    constant,
                    int(row),
                    int(column),
                    float(int(coefficient) * count),
                )
        elif order == 7:
            order7_records += 1
            variable = class_index[mask]
            for row, column, coefficient in record["upper_entries"]:
                row = int(row)
                column = int(column)
                scaled = float(int(coefficient) * SEVEN_TOTAL / denominator)
                row_indices.append(row * size + column)
                column_indices.append(variable)
                values.append(scaled)
                if row != column:
                    row_indices.append(column * size + row)
                    column_indices.append(variable)
                    values.append(scaled)
        else:
            raise ValueError("moment union order exceeds seven")
    constant /= denominator
    coefficient_map = sp.coo_matrix(
        (values, (row_indices, column_indices)),
        shape=(size * size, 208),
        dtype=np.float64,
    ).tocsr()
    return constant, coefficient_map, {
        "name": family_name,
        "matrix_size": size,
        "normalization_denominator": denominator,
        "union_orders": sorted(orders),
        "order7_class_records": order7_records,
        "coefficient_nonzeros": int(coefficient_map.nnz),
        "constant_frobenius_norm": float(np.linalg.norm(constant)),
    }


def active_support_basis(
    constant: np.ndarray,
    coefficient_map: sp.csr_matrix,
    affine_z_particular: np.ndarray,
    affine_z_nullspace: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    size = constant.shape[0]
    matrices = [
        (
            constant.reshape(size * size)
            + coefficient_map @ affine_z_particular
        ).reshape((size, size))
    ]
    for direction in range(affine_z_nullspace.shape[1]):
        vector = coefficient_map @ affine_z_nullspace[:, direction]
        matrix = np.asarray(vector).reshape((size, size))
        if np.linalg.norm(matrix) > 1e-14:
            matrices.append(matrix)
    support = np.hstack(matrices)
    left, singular_values, _ = np.linalg.svd(
        support,
        full_matrices=False,
    )
    tolerance = (
        max(support.shape)
        * np.finfo(np.float64).eps
        * (float(singular_values[0]) if singular_values.size else 1.0)
    )
    rank = int(np.sum(singular_values > tolerance))
    if rank == 0:
        return np.zeros((size, 0)), {
            "ambient_size": size,
            "active_rank": 0,
            "svd_tolerance": tolerance,
            "largest_singular_value": 0.0,
            "smallest_retained_singular_value": None,
            "largest_discarded_singular_value": 0.0,
        }
    basis = left[:, :rank]
    projector = basis @ basis.T
    maximum_escape = 0.0
    for matrix in matrices:
        maximum_escape = max(
            maximum_escape,
            float(np.linalg.norm((np.eye(size) - projector) @ matrix)),
        )
    return basis, {
        "ambient_size": size,
        "active_rank": rank,
        "svd_tolerance": tolerance,
        "largest_singular_value": float(singular_values[0]),
        "smallest_retained_singular_value": float(singular_values[rank - 1]),
        "largest_discarded_singular_value": (
            0.0
            if rank == len(singular_values)
            else float(singular_values[rank])
        ),
        "maximum_coefficient_column_escape_frobenius": maximum_escape,
        "affine_matrices_used": len(matrices),
    }


def affine_linear_space(
    matrix: sp.csr_matrix,
    rhs: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    dense = matrix.toarray()
    left, singular_values, right_t = np.linalg.svd(
        dense,
        full_matrices=True,
    )
    tolerance = (
        max(dense.shape)
        * np.finfo(np.float64).eps
        * float(singular_values[0])
    )
    rank = int(np.sum(singular_values > tolerance))
    particular, residuals, _, _ = np.linalg.lstsq(
        dense,
        rhs,
        rcond=tolerance / singular_values[0],
    )
    nullspace = right_t[rank:, :].T
    maximum_residual = float(np.max(np.abs(dense @ particular - rhs)))
    maximum_null_residual = float(
        np.max(np.abs(dense @ nullspace))
    )
    if rank != 93:
        raise ValueError(f"numerical Wave44 rank changed: {rank}")
    return particular, nullspace, {
        "rank": rank,
        "nullity": int(nullspace.shape[1]),
        "svd_tolerance": tolerance,
        "largest_singular_value": float(singular_values[0]),
        "smallest_retained_singular_value": float(singular_values[rank - 1]),
        "largest_discarded_singular_value": float(singular_values[rank]),
        "particular_max_abs_residual": maximum_residual,
        "nullspace_max_abs_residual": maximum_null_residual,
        "least_squares_residual_sum": (
            0.0 if not residuals.size else float(residuals[0])
        ),
    }


def build_problem() -> dict[str, Any]:
    memory_guard("build start")
    row_system = load_frozen_json(ROW_SYSTEM)
    w45 = load_frozen_json(W45_COEFFICIENTS)
    w47_handoff = load_frozen_json(W47_HANDOFF)
    w47 = load_frozen_json(W47_COEFFICIENTS)
    exact_faces = load_frozen_json(EXACT_FACES)
    lower_counts, lower_record = exact_lower_counts()

    classes = [int(mask) for mask in row_system["classes"]]
    if len(classes) != 208 or len(set(classes)) != 208:
        raise ValueError("Wave44 class stream changed")
    class_index = {mask: index for index, mask in enumerate(classes)}
    for coefficients in (w45, w47):
        stream = coefficients["class_streams"]["7"]
        if int(stream["count"]) != 208:
            raise ValueError("moment order-seven class census changed")
        seen = {
            int(record["canonical_mask"])
            for family in coefficients["families"].values()
            for record in family["class_coefficients"]
            if int(record["order"]) == 7
        }
        if seen != set(classes):
            raise ValueError("moment order-seven class stream differs from Wave44")

    linear_matrix, linear_rhs, row_scaling = scaled_linear_system(row_system)
    affine_particular, affine_nullspace, affine_record = affine_linear_space(
        linear_matrix,
        linear_rhs,
    )
    affine_coordinate = cp.Variable(
        affine_nullspace.shape[1],
        name="wave44_affine_coordinates",
    )
    affine_vector = affine_particular + affine_nullspace @ affine_coordinate
    z = affine_vector[:208]
    q = affine_vector[208]
    margin = cp.Variable(name="common_normalized_psd_margin")
    nonnegative_constraint = z >= 0
    lower_y_constraint = q >= Fraction(2079, Y_SCALE)
    upper_y_constraint = q <= 1
    constraints: list[Any] = [
        nonnegative_constraint,
        lower_y_constraint,
        upper_y_constraint,
    ]

    moment_records: list[dict[str, Any]] = []
    moment_expressions: list[Any] = []
    face_lookup = {
        (record["source"], record["name"]): record
        for record in exact_faces["families"]
    }
    for source_name, coefficients in (("wave45", w45), ("wave47", w47)):
        for family_name, family in coefficients["families"].items():
            constant, coefficient_map, record = moment_affine_map(
                family_name,
                family,
                lower_counts,
                class_index,
            )
            size = record["matrix_size"]
            expression = cp.reshape(
                coefficient_map @ z + constant.reshape(size * size),
                (size, size),
                order="C",
            )
            expression = (expression + expression.T) / 2
            numerical_support_basis, numerical_support_record = active_support_basis(
                constant,
                coefficient_map,
                affine_particular[:208],
                affine_nullspace[:208, :],
            )
            face = face_lookup[(source_name, family_name)]
            kernel = np.asarray(
                [
                    record["vector"]
                    for record in face["kernel_vectors"]
                ],
                dtype=np.float64,
            )
            if kernel.shape[0]:
                _, _, kernel_right_t = np.linalg.svd(
                    kernel,
                    full_matrices=True,
                )
                support_basis = kernel_right_t[kernel.shape[0] :, :].T
            else:
                support_basis = np.eye(size)
            if support_basis.shape[1] != face[
                "exact_rational_active_rank_certified"
            ]:
                raise ValueError("exact face active rank changed")
            compressed = support_basis.T @ expression @ support_basis
            psd_constraint = compressed >> 0
            constraints.append(psd_constraint)
            if support_basis.shape[1]:
                margin_constraint = (
                    compressed
                    - margin * np.eye(support_basis.shape[1])
                    >> 0
                )
                constraints.append(margin_constraint)
            else:
                margin_constraint = None
            moment_expressions.append(expression)
            record["source"] = source_name
            record["constant"] = constant
            record["coefficient_map"] = coefficient_map
            record["psd_constraint"] = psd_constraint
            record["margin_constraint"] = margin_constraint
            record["support_basis"] = support_basis
            record["compressed_expression"] = compressed
            record["active_support"] = {
                "exact_rational_active_rank": face[
                    "exact_rational_active_rank_certified"
                ],
                "exact_rational_nullity": face[
                    "exact_rational_nullity_certified"
                ],
                "forced_zero_diagonals": face["forced_zero_diagonals"],
                "all_kernel_vectors_exact_affine_identities": face[
                    "all_kernel_vectors_exact_affine_identities"
                ],
                "modular_active_ranks": face["modular_active_ranks"],
                "numerical_diagnostic": numerical_support_record,
                "numerical_rank_agrees": (
                    numerical_support_basis.shape[1]
                    == support_basis.shape[1]
                ),
            }
            moment_records.append(record)
    if len(moment_records) != 11:
        raise ValueError("combined moment family count changed")
    problem = cp.Problem(cp.Maximize(margin), constraints)
    memory_guard("problem built")
    return {
        "problem": problem,
        "z": z,
        "q": q,
        "affine_coordinate": affine_coordinate,
        "margin": margin,
        "linear_constraint": None,
        "nonnegative_constraint": nonnegative_constraint,
        "lower_y_constraint": lower_y_constraint,
        "upper_y_constraint": upper_y_constraint,
        "linear_matrix": linear_matrix,
        "linear_rhs": linear_rhs,
        "row_scaling": row_scaling,
        "affine_record": affine_record,
        "row_system": row_system,
        "lower_counts": lower_counts,
        "lower_record": lower_record,
        "moment_records": moment_records,
        "constraints": constraints,
        "base_constraints": [
            nonnegative_constraint,
            lower_y_constraint,
            upper_y_constraint,
            *[
                record["psd_constraint"] for record in moment_records
            ],
        ],
        "moment_expressions": moment_expressions,
        "w47_handoff_payload_sha256": w47_handoff[
            "payload_sha256_without_this_field"
        ],
    }


def exact_decimal_residuals(
    row_system: dict[str, Any],
    z_values: Sequence[float],
    q_value: float,
) -> dict[str, Any]:
    z_fraction = [
        Fraction(format(float(value), ".17g")) for value in z_values
    ]
    q_fraction = Fraction(format(float(q_value), ".17g"))
    vector = [
        value * SEVEN_TOTAL for value in z_fraction
    ] + [q_fraction * Y_SCALE]
    residuals: list[Fraction] = []
    family_max: dict[str, Fraction] = {}
    for family_name in ("base", "vertex", "edge", "nonedge"):
        family = row_system["families"][family_name]
        values = []
        for row, rhs in zip(family["rows"], family["rhs"], strict=True):
            residual = (
                sum(Fraction(coefficient) * value for coefficient, value in zip(row, vector))
                - rhs
            )
            residuals.append(residual)
            values.append(abs(residual))
        family_max[family_name] = max(values, default=Fraction())
    max_abs = max((abs(value) for value in residuals), default=Fraction())
    return {
        "decimal_rationalization": "each float formatted with .17g and parsed exactly",
        "maximum_absolute_raw_residual": str(max_abs),
        "maximum_absolute_raw_residual_float": float(max_abs),
        "family_maximum_absolute_raw_residual": {
            key: str(value) for key, value in family_max.items()
        },
        "nonzero_exact_residuals": sum(value != 0 for value in residuals),
        "residual_catalog_sha256": sha256_bytes(
            json.dumps(
                [str(value) for value in residuals],
                separators=(",", ":"),
            ).encode("ascii")
        ),
    }


def evaluate_candidate(model: dict[str, Any]) -> dict[str, Any] | None:
    z_value = model["z"].value
    q_value = model["q"].value
    margin_value = model["margin"].value
    if z_value is None or q_value is None or margin_value is None:
        return None
    z_value = np.asarray(z_value, dtype=np.float64)
    q_value = float(q_value)
    matrix_residual = model["linear_matrix"] @ np.r_[z_value, q_value] - model["linear_rhs"]
    families = []
    for record in model["moment_records"]:
        size = record["matrix_size"]
        matrix = (
            record["constant"].reshape(size * size)
            + record["coefficient_map"] @ z_value
        ).reshape((size, size))
        matrix = (matrix + matrix.T) / 2
        eigenvalues = np.linalg.eigvalsh(matrix)
        basis = record["support_basis"]
        active_eigenvalues = (
            np.linalg.eigvalsh(basis.T @ matrix @ basis)
            if basis.shape[1]
            else np.asarray([], dtype=np.float64)
        )
        families.append(
            {
                "source": record["source"],
                "name": record["name"],
                "matrix_size": size,
                "minimum_normalized_eigenvalue": float(eigenvalues[0]),
                "maximum_normalized_eigenvalue": float(eigenvalues[-1]),
                "active_support_rank": int(basis.shape[1]),
                "minimum_active_support_eigenvalue": (
                    None
                    if not active_eigenvalues.size
                    else float(active_eigenvalues[0])
                ),
                "maximum_active_support_eigenvalue": (
                    None
                    if not active_eigenvalues.size
                    else float(active_eigenvalues[-1])
                ),
                "trace": float(np.trace(matrix)),
                "symmetry_max_abs_residual": float(
                    np.max(np.abs(matrix - matrix.T))
                ),
                "matrix_sha256_float64_le": sha256_bytes(
                    np.asarray(matrix, dtype="<f8").tobytes(order="C")
                ),
            }
        )
    return {
        "common_margin": float(margin_value),
        "seven_probability_minimum": float(np.min(z_value)),
        "seven_probability_sum": float(np.sum(z_value)),
        "h11_over_4_scaled": q_value,
        "h11_float": float(4 * Y_SCALE * q_value),
        "scaled_linear_max_abs_residual": float(
            np.max(np.abs(matrix_residual))
        ),
        "scaled_linear_l2_residual": float(np.linalg.norm(matrix_residual)),
        "exact_decimal_linear_residuals": exact_decimal_residuals(
            model["row_system"],
            z_value,
            q_value,
        ),
        "moment_families": families,
        "minimum_family_eigenvalue": min(
            family["minimum_normalized_eigenvalue"] for family in families
        ),
        "minimum_active_support_eigenvalue": min(
            family["minimum_active_support_eigenvalue"]
            for family in families
            if family["minimum_active_support_eigenvalue"] is not None
        ),
        "seven_probabilities": [
            {
                "canonical_mask": int(mask),
                "value": format(float(value), ".17g"),
            }
            for mask, value in zip(
                model["row_system"]["classes"],
                z_value,
                strict=True,
            )
            if abs(float(value)) >= 1e-14
        ],
    }


def dual_summary(model: dict[str, Any]) -> dict[str, Any]:
    equality = (
        None
        if model["linear_constraint"] is None
        else model["linear_constraint"].dual_value
    )
    nonnegative = model["nonnegative_constraint"].dual_value
    psd_records = []
    for record in model["moment_records"]:
        dual = record["psd_constraint"].dual_value
        if dual is None:
            psd_records.append(
                {"source": record["source"], "name": record["name"], "available": False}
            )
            continue
        dual = np.asarray(dual, dtype=np.float64)
        eig = np.linalg.eigvalsh((dual + dual.T) / 2)
        psd_records.append(
            {
                "source": record["source"],
                "name": record["name"],
                "available": True,
                "frobenius_norm": float(np.linalg.norm(dual)),
                "minimum_eigenvalue": float(eig[0]),
                "maximum_eigenvalue": float(eig[-1]),
                "matrix_sha256_float64_le": sha256_bytes(
                    np.asarray(dual, dtype="<f8").tobytes(order="C")
                ),
            }
        )
        margin_dual = (
            None
            if record["margin_constraint"] is None
            else record["margin_constraint"].dual_value
        )
        if margin_dual is not None:
            margin_dual = np.asarray(margin_dual, dtype=np.float64)
            margin_eigenvalues = np.linalg.eigvalsh(
                (margin_dual + margin_dual.T) / 2
            )
            psd_records[-1]["margin_dual"] = {
                "size": int(margin_dual.shape[0]),
                "frobenius_norm": float(np.linalg.norm(margin_dual)),
                "minimum_eigenvalue": float(margin_eigenvalues[0]),
                "maximum_eigenvalue": float(margin_eigenvalues[-1]),
                "matrix_sha256_float64_le": sha256_bytes(
                    np.asarray(margin_dual, dtype="<f8").tobytes(order="C")
                ),
            }
    result: dict[str, Any] = {
        "psd_families": psd_records,
        "lower_y_dual": (
            None
            if model["lower_y_constraint"].dual_value is None
            else float(model["lower_y_constraint"].dual_value)
        ),
        "upper_y_dual": (
            None
            if model["upper_y_constraint"].dual_value is None
            else float(model["upper_y_constraint"].dual_value)
        ),
        "rational_reconstruction": {
            "attempted": False,
            "status": "NOT_ATTEMPTED_UNLESS_NUMERICAL_MARGIN_IS_STRICTLY_NEGATIVE",
            "exact_certificate": None,
        },
    }
    if equality is not None:
        equality = np.asarray(equality, dtype=np.float64)
        result["linear_equality_dual"] = {
            "count": int(equality.size),
            "maximum_absolute_value": float(np.max(np.abs(equality))),
            "l2_norm": float(np.linalg.norm(equality)),
            "sha256_float64_le": sha256_bytes(
                np.asarray(equality, dtype="<f8").tobytes()
            ),
        }
    if nonnegative is not None:
        nonnegative = np.asarray(nonnegative, dtype=np.float64)
        result["nonnegative_dual"] = {
            "count": int(nonnegative.size),
            "minimum": float(np.min(nonnegative)),
            "maximum": float(np.max(nonnegative)),
            "sha256_float64_le": sha256_bytes(
                np.asarray(nonnegative, dtype="<f8").tobytes()
            ),
        }
    return result


def solver_settings(name: str) -> dict[str, Any]:
    if name == "CLARABEL":
        return {
            "max_iter": 500,
            "tol_gap_abs": 1e-8,
            "tol_gap_rel": 1e-8,
            "tol_feas": 1e-8,
            "equilibrate_enable": True,
            "verbose": False,
        }
    if name == "SCS":
        return {
            "max_iters": 100_000,
            "eps": 1e-6,
            "normalize": True,
            "scale": 1.0,
            "acceleration_lookback": 10,
            "verbose": False,
        }
    raise ValueError(name)


def solve_one(model: dict[str, Any], solver: str) -> dict[str, Any]:
    memory_before = memory_guard(f"{solver} before solve")
    settings = solver_settings(solver)
    started = time.perf_counter()
    exception = None
    try:
        objective = model["problem"].solve(
            solver=solver,
            warm_start=False,
            **settings,
        )
    except Exception as error:  # numerical scout retains exact exception text
        objective = None
        exception = f"{type(error).__name__}: {error}"
    elapsed = time.perf_counter() - started
    memory_after = memory_guard(f"{solver} after solve")
    candidate = evaluate_candidate(model)
    record = {
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
        "dual": dual_summary(model),
        "memory_free_percent_before": round(memory_before, 2),
        "memory_free_percent_after": round(memory_after, 2),
        "claim_label": "CANDIDATE_NUMERICAL_ONLY",
        "used_as_exact_evidence": False,
    }
    return record


def public_model_record(model: dict[str, Any]) -> dict[str, Any]:
    moments = []
    for record in model["moment_records"]:
        moments.append(
            {
                key: value
                for key, value in record.items()
                if key
                not in {
                    "constant",
                    "coefficient_map",
                    "psd_constraint",
                    "margin_constraint",
                    "support_basis",
                    "compressed_expression",
                }
            }
        )
    return {
        "scaled_variables": {
            "seven_class_probability": f"x_H / C(99,7), C(99,7)={SEVEN_TOTAL}",
            "h11_over_4_scaled": f"(h11/4) / {Y_SCALE}",
        },
        "linear_rows": 170,
        "linear_matrix_shape": list(model["linear_matrix"].shape),
        "linear_matrix_nonzeros": int(model["linear_matrix"].nnz),
        "row_scaling": model["row_scaling"],
        "linear_affine_space": model["affine_record"],
        "nonnegativity": "all 208 seven-class probabilities",
        "h11_over_4_scaled_bounds": [
            str(Fraction(2079, Y_SCALE)),
            "1",
        ],
        "moment_families": moments,
        "common_margin_definition": (
            "retain every full probability-normalized moment PSD constraint; "
            "maximize t such that each compression to the numerical span of "
            "all frozen coefficient-matrix columns satisfies "
            "U_sigma^T M_sigma U_sigma - t I >= 0"
        ),
        "lower_counts": model["lower_record"],
    }


def run(solvers: Sequence[str]) -> dict[str, Any]:
    memory_start = memory_guard("run start")
    model = build_problem()
    model_record = public_model_record(model)
    solver_records = []
    for solver in solvers:
        solver_records.append(solve_one(model, solver))
    return {
        "format": "wave48-combined-conic-moment-scout-v1",
        "role": "proof_b",
        "claim_label": "CANDIDATE",
        "scope": (
            "numerical real SDP combining the exact Wave44 170-row endpoint "
            "count system, nonnegativity, all three Wave45 finite moment "
            "families, and all eight Wave47 three-root moment families"
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
            "minimum_free_physical_memory_percent": MIN_FREE_MEMORY_PERCENT,
            "free_physical_memory_percent_at_start": round(memory_start, 2),
            "status": "PASS",
        },
        "model": model_record,
        "solvers": solver_records,
        "conclusion": {
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "graph_constructed": False,
            "numerical_status_is_not_certificate": True,
        },
        "limitations": [
            "CVXPY, Clarabel, and SCS results are floating numerical diagnostics.",
            "No infeasibility claim is made without an exact rational dual certificate.",
            "The Wave47 three-root coefficient package is CANDIDATE pending clean-room verification.",
            "A numerically feasible aggregate vector would not construct a graph.",
            "No completed-graph automorphism is assumed.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--solvers",
        nargs="+",
        choices=("CLARABEL", "SCS"),
        default=("CLARABEL", "SCS"),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run(args.solvers)
    payload = canonical_payload(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(
        json.dumps(
            {
                record["solver"]: {
                    "status": record["status"],
                    "objective": record["objective"],
                    "minimum_family_eigenvalue": (
                        None
                        if record["candidate"] is None
                        else record["candidate"]["minimum_family_eigenvalue"]
                    ),
                    "scaled_linear_max_abs_residual": (
                        None
                        if record["candidate"] is None
                        else record["candidate"][
                            "scaled_linear_max_abs_residual"
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
