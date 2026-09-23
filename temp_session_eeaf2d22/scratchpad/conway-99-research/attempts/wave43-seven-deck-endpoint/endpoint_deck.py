#!/usr/bin/env python3
"""Exact order-seven deck scout at the prism-free n3=4158 endpoint.

The search uses HiGHS only to discover a nonnegative integer count vector.
Any incumbent is then checked with standard-library integer arithmetic.
An infeasibility status is not accepted as a proof certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array


ROOT = Path(__file__).resolve().parents[2]
WAVE21_PATH = ROOT / "attempts" / "wave21-six-vertex-lp" / "exact_check.py"
WAVE22_PATH = ROOT / "attempts" / "wave22-full-seven-deck" / "exact_check.py"
N3 = 4158
Y_MIN = math.ceil(2 * N3 / 4)
Y_MAX = N3


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def integer_value(value: Any, label: str) -> int:
    if value.denominator != 1:
        raise ValueError(f"{label} is not integral: {value}")
    return int(value.numerator)


def build_endpoint_model() -> dict[str, Any]:
    wave21 = load_module("wave43_endpoint_wave21", WAVE21_PATH)
    wave22 = load_module("wave43_endpoint_wave22", WAVE22_PATH)
    base = wave22.build_model()
    classes = tuple(int(mask) for mask in base["classes7"])
    class_index = {mask: index for index, mask in enumerate(classes)}
    h_masks = tuple(int(mask) for mask in base["h_masks"])

    six_forms = wave21.six_counts()
    six_counts = tuple(
        integer_value(six_forms[index].evaluate(N3), f"N_{index}")
        for index in range(1, 63)
    )
    if min(six_counts) < 0 or six_counts[0] != 0:
        raise ValueError("endpoint six-count table or prism count changed")
    deck_rhs = tuple(count * (wave22.N - 6) for count in six_counts)

    seven_forms = wave21.seven_counts()
    h_equations: list[dict[str, int]] = []
    for source_index, mask in enumerate(h_masks):
        form = seven_forms[source_index]
        constant = integer_value(
            form.c + form.x * N3,
            f"H_{source_index} constant",
        )
        y_coefficient = integer_value(
            4 * form.y,
            f"H_{source_index} y coefficient",
        )
        h_equations.append(
            {
                "source_index": source_index,
                "canonical_mask": mask,
                "class_index": class_index[mask],
                "constant": constant,
                "y_coefficient": y_coefficient,
            }
        )

    return {
        "wave21": wave21,
        "wave22": wave22,
        "classes": classes,
        "matrix_rows": tuple(tuple(map(int, row)) for row in base["matrix_rows"]),
        "six_counts": six_counts,
        "deck_rhs": deck_rhs,
        "h_equations": tuple(h_equations),
    }


def sparse_constraints(model: dict[str, Any]) -> tuple[coo_array, np.ndarray]:
    classes = model["classes"]
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[float] = []
    targets: list[float] = []

    for row_index, (row, target) in enumerate(
        zip(model["matrix_rows"], model["deck_rhs"])
    ):
        for column_index, coefficient in enumerate(row):
            if coefficient:
                row_indices.append(row_index)
                column_indices.append(column_index)
                values.append(float(coefficient))
        targets.append(float(target))

    offset = len(targets)
    y_index = len(classes)
    for local_row, equation in enumerate(model["h_equations"]):
        row_index = offset + local_row
        row_indices.append(row_index)
        column_indices.append(equation["class_index"])
        values.append(1.0)
        if equation["y_coefficient"]:
            row_indices.append(row_index)
            column_indices.append(y_index)
            values.append(float(-equation["y_coefficient"]))
        targets.append(float(equation["constant"]))

    matrix = coo_array(
        (
            np.asarray(values, dtype=np.float64),
            (
                np.asarray(row_indices, dtype=np.int32),
                np.asarray(column_indices, dtype=np.int32),
            ),
        ),
        shape=(len(targets), len(classes) + 1),
    ).tocsr()
    return matrix, np.asarray(targets, dtype=np.float64)


def validate_candidate(
    model: dict[str, Any],
    counts: list[int],
    y_value: int,
) -> dict[str, Any]:
    if len(counts) != 208 or min(counts) < 0:
        raise ValueError("candidate is not a nonnegative 208-class vector")
    if not Y_MIN <= y_value <= Y_MAX:
        raise ValueError("h11/4 is outside the exact endpoint interval")

    for row_index, (row, target) in enumerate(
        zip(model["matrix_rows"], model["deck_rhs"])
    ):
        actual = sum(coefficient * count for coefficient, count in zip(row, counts))
        if actual != target:
            raise ValueError(f"deletion row {row_index + 1} failed")

    for equation in model["h_equations"]:
        expected = (
            equation["constant"] + equation["y_coefficient"] * y_value
        )
        if counts[equation["class_index"]] != expected:
            raise ValueError(
                f"H_{equation['source_index']} exact count failed"
            )

    total = sum(counts)
    expected_total = math.comb(99, 7)
    if total != expected_total:
        raise ValueError(f"seven-subset total {total} != {expected_total}")

    classes = model["classes"]
    support = [
        {"canonical_mask": mask, "count": count}
        for mask, count in zip(classes, counts)
        if count
    ]
    prism_row = model["matrix_rows"][0]
    forbidden = [
        classes[index]
        for index, coefficient in enumerate(prism_row)
        if coefficient
    ]
    forbidden_positive = [
        mask
        for mask in forbidden
        if counts[classes.index(mask)] != 0
    ]
    if forbidden_positive:
        raise ValueError("a seven-class containing a prism has positive count")

    canonical_support = json.dumps(
        support, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return {
        "h11": 4 * y_value,
        "support_size": len(support),
        "zero_count_classes": len(classes) - len(support),
        "seven_subset_total": total,
        "prism_containing_class_count": len(forbidden),
        "all_prism_containing_classes_zero": True,
        "support_sha256": hashlib.sha256(canonical_support).hexdigest(),
        "support": support,
    }


def solve_endpoint(time_limit: float) -> dict[str, Any]:
    model = build_endpoint_model()
    matrix, targets = sparse_constraints(model)
    variable_count = len(model["classes"]) + 1
    lower = np.zeros(variable_count, dtype=np.float64)
    upper = np.full(variable_count, np.inf, dtype=np.float64)
    lower[-1] = Y_MIN
    upper[-1] = Y_MAX
    result = milp(
        c=np.zeros(variable_count, dtype=np.float64),
        integrality=np.ones(variable_count, dtype=np.uint8),
        bounds=Bounds(lower, upper),
        constraints=LinearConstraint(matrix, targets, targets),
        options={
            "disp": False,
            "presolve": True,
            "time_limit": time_limit,
            "mip_rel_gap": 0.0,
        },
    )

    certificate = None
    maximum_rounding_error = None
    if result.x is not None:
        rounded = [int(round(float(value))) for value in result.x]
        maximum_rounding_error = max(
            abs(float(value) - integer)
            for value, integer in zip(result.x, rounded)
        )
        certificate = validate_candidate(model, rounded[:-1], rounded[-1])

    return {
        "format": "wave43-seven-deck-endpoint-v1",
        "role": "construction",
        "claim_label": (
            "EXACTLY_VALIDATED_NECESSARY_COUNT_WITNESS"
            if certificate is not None
            else "UNKNOWN"
        ),
        "scope": (
            "Complete 208-class order-seven deletion deck and all 19 "
            "published Hamiltonian counts at n3=4158, with h11/4 variable."
        ),
        "parameters": {
            "n": 99,
            "k": 14,
            "lambda": 1,
            "mu": 2,
            "n3": N3,
            "h11_interval": [4 * Y_MIN, 4 * Y_MAX],
            "h11_multiple": 4,
        },
        "model": {
            "seven_vertex_classes": len(model["classes"]),
            "deletion_equations": 62,
            "hamiltonian_equations": 19,
            "integer_variables_including_h11_over_4": variable_count,
            "sparse_nonzeros": int(matrix.nnz),
        },
        "solver": {
            "engine": "scipy.optimize.milp with bundled HiGHS",
            "status": int(result.status),
            "message": str(result.message),
            "success": bool(result.success),
            "time_limit_seconds": time_limit,
            "maximum_rounding_error": maximum_rounding_error,
            "solver_exit_code_is_not_a_negative_certificate": True,
        },
        "certificate": certificate,
        "conclusion": {
            "order_seven_count_system": (
                "FEASIBLE" if certificate is not None else "UNKNOWN"
            ),
            "endpoint_n3_4158": "UNKNOWN",
            "upper_bound_below_4158": "NOT_PROVED",
            "graph_construction": False,
            "conway_99": "UNKNOWN",
        },
        "limitations": [
            "Aggregate induced-subgraph counts do not enforce overlapping-subset consistency.",
            "A feasible count vector is not a graph or evidence that a graph exists.",
            "A solver infeasibility status would require an independent exact certificate.",
            "No automorphism of a putative graph is assumed.",
        ],
    }


def verify_record(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("format") != "wave43-seven-deck-endpoint-v1":
        raise ValueError("unexpected endpoint-deck record format")
    certificate = payload.get("certificate")
    if not isinstance(certificate, dict):
        raise ValueError("record has no candidate certificate")
    support = certificate.get("support")
    if not isinstance(support, list):
        raise ValueError("record support is absent")

    model = build_endpoint_model()
    index = {mask: position for position, mask in enumerate(model["classes"])}
    counts = [0] * len(model["classes"])
    seen: set[int] = set()
    for record in support:
        if not isinstance(record, dict) or set(record) != {
            "canonical_mask",
            "count",
        }:
            raise ValueError("malformed support record")
        mask = record["canonical_mask"]
        count = record["count"]
        if type(mask) is not int or type(count) is not int or count <= 0:
            raise ValueError("support entries must be positive integers")
        if mask not in index or mask in seen:
            raise ValueError("unknown or duplicate support mask")
        seen.add(mask)
        counts[index[mask]] = count

    h11 = certificate.get("h11")
    if type(h11) is not int or h11 % 4:
        raise ValueError("certificate h11 is not a multiple of four")
    reconstructed = validate_candidate(model, counts, h11 // 4)
    if reconstructed != certificate:
        raise ValueError("stored certificate differs from exact reconstruction")
    return {
        "verification": "PASS",
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "support_size": reconstructed["support_size"],
        "h11": reconstructed["h11"],
        "all_prism_containing_classes_zero": True,
    }


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    if arguments.verify is not None:
        print(json.dumps(verify_record(arguments.verify), sort_keys=True))
        return
    if not 1 <= arguments.time_limit <= 1800:
        raise SystemExit("time limit must be between 1 and 1800 seconds")
    result = solve_endpoint(arguments.time_limit)
    rendered = canonical_bytes(result)
    if arguments.output is None:
        print(rendered.decode("utf-8"), end="")
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_bytes(rendered)
        print(
            json.dumps(
                {
                    "output": str(arguments.output),
                    "sha256": hashlib.sha256(rendered).hexdigest(),
                    "claim_label": result["claim_label"],
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
