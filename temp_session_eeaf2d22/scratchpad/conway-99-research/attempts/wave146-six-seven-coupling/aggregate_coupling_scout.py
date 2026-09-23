#!/usr/bin/env python3
"""Couple the fixed Wave144 endpoint table to the full order-seven deck.

Unlike ``fixed_witness_scout.py``, the local z_P distributions are variables.
For every positive (six-class, output-weight) cell in the Wave144 endpoint
table, this model imposes the aggregate total, degree, pair, and odd-pattern
equations after forbidding rooted order-seven types that violate lambda/mu.
Aut(H)-orbit sums are then identified with the rooted deletion multiplicities
of the complete 208-class order-seven deck.

This is a continuous or integer numerical scout.  Solver infeasibility is not
negative evidence without an independently replayed exact Farkas certificate.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp
from scipy.sparse import coo_array


ROOT = Path(__file__).resolve().parents[2]
FIXED_SCOUT_PATH = (
    ROOT / "attempts/wave146-six-seven-coupling/fixed_witness_scout.py"
)
SUPPORT_PATH = (
    ROOT / "attempts/wave146-six-seven-coupling/seven_extendable_support.py"
)
WAVE144_RESULT = ROOT / "attempts/wave144-sixset-odd-profile/exact-results.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    require(
        specification is not None and specification.loader is not None,
        f"cannot load {path}",
    )
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def possible_pattern(support: Any, wave144: Any, mask: int, pattern: int) -> bool:
    if not support.root_pattern_allowed(wave144, mask, pattern):
        return False
    params = wave144.local_parameters(mask)
    for pair_index, (left, right) in enumerate(wave144.edges()):
        if (
            pattern >> left & 1
            and pattern >> right & 1
            and params["pair_rhs"][pair_index] == 0
        ):
            return False
    return True


def build_model() -> dict[str, Any]:
    fixed = load_module("wave146_aggregate_fixed", FIXED_SCOUT_PATH)
    support = load_module("wave146_aggregate_support", SUPPORT_PATH)
    wave144 = support.load_wave144()
    base = fixed.build_model()
    require(not base["missing_keys"], "seven-class root key universe is incomplete")
    masks = fixed.source_masks(wave144.load_wave21())
    endpoint_payload = json.loads(WAVE144_RESULT.read_text(encoding="utf-8"))
    cells = tuple(
        (
            int(record["source_class"]),
            int(record["output_weight"]),
            int(record["count"]),
        )
        for record in endpoint_payload["aggregate_endpoint_certificate"]["nonzero_cells"]
    )

    variable_labels = [
        f"seven:{mask}" for mask in base["wave43"]["classes"]
    ] + ["h11_over_4"]
    x_index: dict[tuple[int, int, int], int] = {}
    possible_by_cell: dict[tuple[int, int], tuple[int, ...]] = {}
    orbit_by_source_pattern: dict[tuple[int, int], int] = {}
    for source, weight, _ in cells:
        mask = masks[source - 1]
        patterns = tuple(
            pattern
            for pattern in range(64)
            if possible_pattern(support, wave144, mask, pattern)
        )
        require(patterns, f"source {source} has no possible root patterns")
        possible_by_cell[(source, weight)] = patterns
        for pattern in patterns:
            key = (source, weight, pattern)
            x_index[key] = len(variable_labels)
            variable_labels.append(f"x:{source}:{weight}:{pattern}")
            orbit_by_source_pattern[(source, pattern)] = (
                fixed.canonical_profile_pattern(
                    base["wave43"]["wave22"],
                    mask,
                    pattern,
                )
            )

    return {
        "fixed": fixed,
        "support": support,
        "wave144": wave144,
        "base": base,
        "masks": masks,
        "cells": cells,
        "possible_by_cell": possible_by_cell,
        "orbit_by_source_pattern": orbit_by_source_pattern,
        "x_index": x_index,
        "variable_labels": variable_labels,
    }


def sparse_constraints(
    model: dict[str, Any],
) -> tuple[Any, np.ndarray, list[str]]:
    base = model["base"]
    endpoint = base["wave43"]
    wave144 = model["wave144"]
    row_indices: list[int] = []
    column_indices: list[int] = []
    values: list[float] = []
    targets: list[float] = []
    labels: list[str] = []

    def append_row(
        entries: Iterable[tuple[int, int]],
        target: int,
        label: str,
    ) -> None:
        row = len(targets)
        for column, coefficient in entries:
            if coefficient:
                row_indices.append(row)
                column_indices.append(column)
                values.append(float(coefficient))
        targets.append(float(target))
        labels.append(label)

    for index, (coefficients, target) in enumerate(
        zip(endpoint["matrix_rows"], endpoint["deck_rhs"])
    ):
        append_row(
            ((column, coefficient) for column, coefficient in enumerate(coefficients)),
            int(target),
            f"deck:{index + 1}",
        )
    h11_index = len(endpoint["classes"])
    for equation in endpoint["h_equations"]:
        entries = [(int(equation["class_index"]), 1)]
        if equation["y_coefficient"]:
            entries.append((h11_index, -int(equation["y_coefficient"])))
        append_row(
            entries,
            int(equation["constant"]),
            f"hamiltonian:{equation['source_index']}",
        )

    root_x_columns: dict[tuple[int, int], list[int]] = defaultdict(list)
    for source, weight, count in model["cells"]:
        mask = model["masks"][source - 1]
        params = wave144.local_parameters(mask)
        patterns = model["possible_by_cell"][(source, weight)]

        def x_entries(coefficient) -> Iterable[tuple[int, int]]:
            for pattern in patterns:
                value = coefficient(pattern)
                if value:
                    yield model["x_index"][(source, weight, pattern)], value

        append_row(
            x_entries(lambda pattern: 1),
            93 * count,
            f"cell-total:{source}:{weight}",
        )
        for vertex in range(6):
            append_row(
                x_entries(lambda pattern, v=vertex: (pattern >> v) & 1),
                params["degree_rhs"][vertex] * count,
                f"cell-degree:{source}:{weight}:{vertex}",
            )
        for pair_index, (left, right) in enumerate(wave144.edges()):
            append_row(
                x_entries(
                    lambda pattern, a=left, b=right: (
                        (pattern >> a & 1) and (pattern >> b & 1)
                    )
                ),
                params["pair_rhs"][pair_index] * count,
                f"cell-pair:{source}:{weight}:{left}:{right}",
            )
        append_row(
            x_entries(lambda pattern: pattern.bit_count() & 1),
            (weight - params["inside_odd_weight"]) * count,
            f"cell-odd:{source}:{weight}",
        )
        for pattern in patterns:
            orbit = model["orbit_by_source_pattern"][(source, pattern)]
            root_x_columns[(source, orbit)].append(
                model["x_index"][(source, weight, pattern)]
            )

    for key in base["keys"]:
        entries = [
            (column, 1)
            for column in root_x_columns.get(key, [])
        ]
        entries.extend(
            (column, -vector.get(key, 0))
            for column, vector in enumerate(base["vectors"])
            if vector.get(key, 0)
        )
        append_row(entries, 0, f"root-link:{key[0]}:{key[1]}")

    matrix = coo_array(
        (
            np.asarray(values, dtype=np.float64),
            (
                np.asarray(row_indices, dtype=np.int32),
                np.asarray(column_indices, dtype=np.int32),
            ),
        ),
        shape=(len(targets), len(model["variable_labels"])),
    ).tocsr()
    return matrix, np.asarray(targets, dtype=np.float64), labels


def run(time_limit: float, integer: bool) -> dict[str, Any]:
    model = build_model()
    matrix, targets, labels = sparse_constraints(model)
    variable_count = matrix.shape[1]
    lower = np.zeros(variable_count, dtype=np.float64)
    upper = np.full(variable_count, np.inf, dtype=np.float64)
    h11_index = len(model["base"]["wave43"]["classes"])
    lower[h11_index] = math.ceil(2 * 4158 / 4)
    upper[h11_index] = 4158

    if integer:
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
    else:
        result = linprog(
            c=np.zeros(variable_count, dtype=np.float64),
            A_eq=matrix,
            b_eq=targets,
            bounds=list(zip(lower, upper)),
            method="highs",
            options={"presolve": True, "time_limit": time_limit},
        )

    maximum_residual = None
    minimum_value = None
    if result.x is not None:
        maximum_residual = float(np.max(np.abs(matrix @ result.x - targets)))
        minimum_value = float(np.min(result.x))
    return {
        "format": "wave146-aggregate-six-seven-coupling-scout-v1",
        "scope": (
            "fixed Wave144 endpoint class/weight table, variable aggregate "
            "seven-extendable local profiles, and complete order-seven deck"
        ),
        "model": {
            "variables": variable_count,
            "equalities": int(matrix.shape[0]),
            "nonzeros": int(matrix.nnz),
            "positive_six_weight_cells": len(model["cells"]),
            "root_extension_types": len(model["base"]["keys"]),
        },
        "solver": {
            "domain": "NONNEGATIVE_INTEGERS" if integer else "NONNEGATIVE_REALS",
            "status": int(result.status),
            "message": str(result.message),
            "success": bool(result.success),
            "time_limit_seconds": time_limit,
            "maximum_equality_residual": maximum_residual,
            "minimum_variable": minimum_value,
            "solver_status_is_not_a_certificate": True,
        },
        "conclusion": (
            "NUMERICAL_FEASIBLE_CANDIDATE"
            if result.x is not None and result.success
            else "UNKNOWN"
        ),
        "limitations": [
            "The Wave144 endpoint class/weight table is fixed rather than optimized.",
            "Aggregate profile equations need not decompose into profiles for every individual six-set.",
            "Overlaps beyond one rooted seventh vertex are not retained.",
            "Numerical infeasibility is not negative evidence without an exact certificate.",
            "No automorphism of a putative graph is assumed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--integer", action="store_true")
    arguments = parser.parse_args()
    require(1 <= arguments.time_limit <= 1800, "invalid time limit")
    print(
        json.dumps(
            run(arguments.time_limit, arguments.integer),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
