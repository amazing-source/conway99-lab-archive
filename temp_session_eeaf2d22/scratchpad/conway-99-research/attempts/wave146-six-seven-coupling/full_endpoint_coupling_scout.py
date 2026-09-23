#!/usr/bin/env python3
"""Full endpoint LP coupling six-set code weights to the order-seven deck.

This frees the Wave144 class/weight table.  Variables are:

* all seven-extendable six-class/output-weight counts B_(H,w);
* aggregate rooted neighborhood-pattern counts X_(H,w,P);
* all 208 order-seven class counts and h11/4.

The model imposes exact six-class marginals at n3=4158, Wave141 reciprocity
moments t=0..3 and S6, every aggregate local z_P equation, every rooted
six-to-seven extension identity, and the complete Wave43 deletion/Hamiltonian
system.  It is still an aggregate relaxation, not a graph model.

Numerical status is scouting evidence only.  Infeasibility requires an exact
Farkas certificate; feasibility requires an exact replay before promotion.
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
AGGREGATE_PATH = (
    ROOT / "attempts/wave146-six-seven-coupling/aggregate_coupling_scout.py"
)


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


def build_model() -> dict[str, Any]:
    aggregate = load_module("wave146_full_aggregate", AGGREGATE_PATH)
    fixed = load_module("wave146_full_fixed", aggregate.FIXED_SCOUT_PATH)
    support = load_module("wave146_full_support", aggregate.SUPPORT_PATH)
    wave144 = support.load_wave144()
    wave21 = wave144.load_wave21()
    base = fixed.build_model()
    require(not base["missing_keys"], "seven-class root key universe is incomplete")
    masks = fixed.source_masks(wave21)
    support_result = support.build_result()
    supports = {
        int(record["source_class"]): tuple(
            map(int, record["seven_extendable_attainable_weights"])
        )
        for record in support_result["class_profiles"]
    }
    require(set(supports) == set(range(1, 63)), "support table incomplete")

    variable_labels = [
        f"seven:{mask}" for mask in base["wave43"]["classes"]
    ] + ["h11_over_4"]
    b_index: dict[tuple[int, int], int] = {}
    x_index: dict[tuple[int, int, int], int] = {}
    possible_by_source: dict[int, tuple[int, ...]] = {}
    orbit_by_source_pattern: dict[tuple[int, int], int] = {}
    for source in range(1, 63):
        mask = masks[source - 1]
        patterns = tuple(
            pattern
            for pattern in range(64)
            if aggregate.possible_pattern(support, wave144, mask, pattern)
        )
        require(patterns, f"source {source} has no possible patterns")
        possible_by_source[source] = patterns
        for pattern in patterns:
            orbit_by_source_pattern[(source, pattern)] = (
                fixed.canonical_profile_pattern(
                    base["wave43"]["wave22"],
                    mask,
                    pattern,
                )
            )
        for weight in supports[source]:
            b_index[(source, weight)] = len(variable_labels)
            variable_labels.append(f"b:{source}:{weight}")
            for pattern in patterns:
                x_index[(source, weight, pattern)] = len(variable_labels)
                variable_labels.append(f"x:{source}:{weight}:{pattern}")

    return {
        "aggregate": aggregate,
        "fixed": fixed,
        "support": support,
        "wave144": wave144,
        "wave21": wave21,
        "base": base,
        "masks": masks,
        "supports": supports,
        "possible_by_source": possible_by_source,
        "orbit_by_source_pattern": orbit_by_source_pattern,
        "b_index": b_index,
        "x_index": x_index,
        "variable_labels": variable_labels,
    }


def sparse_constraints(
    model: dict[str, Any],
) -> tuple[Any, np.ndarray, list[str]]:
    base = model["base"]
    endpoint = base["wave43"]
    wave144 = model["wave144"]
    wave21 = model["wave21"]
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

    forms = wave21.six_counts()
    for source in range(1, 63):
        marginal = forms[source].evaluate(4158)
        require(marginal.denominator == 1, "nonintegral endpoint marginal")
        append_row(
            (
                (model["b_index"][(source, weight)], 1)
                for weight in model["supports"][source]
            ),
            int(marginal),
            f"class-marginal:{source}",
        )

    _, moment_rhs = wave144.low_rows_and_moments()
    for degree in range(4):
        append_row(
            (
                (
                    model["b_index"][(source, weight)],
                    wave144.krawtchouk(degree, weight),
                )
                for source in range(1, 63)
                for weight in model["supports"][source]
            ),
            int(moment_rhs[degree]),
            f"reciprocity:{degree}",
        )
    append_row(
        (
            (
                model["b_index"][(source, weight)],
                (-1) ** (weight // 2),
            )
            for source in range(1, 63)
            for weight in model["supports"][source]
        ),
        2734116,
        "signed-S6",
    )

    root_x_columns: dict[tuple[int, int], list[int]] = defaultdict(list)
    for source in range(1, 63):
        mask = model["masks"][source - 1]
        params = wave144.local_parameters(mask)
        patterns = model["possible_by_source"][source]
        for weight in model["supports"][source]:
            b_column = model["b_index"][(source, weight)]

            def x_entries(coefficient) -> Iterable[tuple[int, int]]:
                for pattern in patterns:
                    value = coefficient(pattern)
                    if value:
                        yield model["x_index"][(source, weight, pattern)], value

            append_row(
                list(x_entries(lambda pattern: 1)) + [(b_column, -93)],
                0,
                f"cell-total:{source}:{weight}",
            )
            for vertex in range(6):
                append_row(
                    list(
                        x_entries(lambda pattern, v=vertex: (pattern >> v) & 1)
                    )
                    + [(b_column, -params["degree_rhs"][vertex])],
                    0,
                    f"cell-degree:{source}:{weight}:{vertex}",
                )
            for pair_index, (left, right) in enumerate(wave144.edges()):
                append_row(
                    list(
                        x_entries(
                            lambda pattern, a=left, b=right: (
                                (pattern >> a & 1) and (pattern >> b & 1)
                            )
                        )
                    )
                    + [(b_column, -params["pair_rhs"][pair_index])],
                    0,
                    f"cell-pair:{source}:{weight}:{left}:{right}",
                )
            append_row(
                list(x_entries(lambda pattern: pattern.bit_count() & 1))
                + [(b_column, -(weight - params["inside_odd_weight"]))],
                0,
                f"cell-odd:{source}:{weight}",
            )
            for pattern in patterns:
                orbit = model["orbit_by_source_pattern"][(source, pattern)]
                root_x_columns[(source, orbit)].append(
                    model["x_index"][(source, weight, pattern)]
                )

    for key in base["keys"]:
        entries = [(column, 1) for column in root_x_columns.get(key, [])]
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

    solve_matrix = matrix
    solve_targets = targets
    column_scales = np.ones(variable_count, dtype=np.float64)
    row_scales = np.ones(matrix.shape[0], dtype=np.float64)
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
        endpoint = model["base"]["wave43"]
        for column in range(len(endpoint["classes"])):
            deck_bounds = [
                endpoint["deck_rhs"][row_index] / row[column]
                for row_index, row in enumerate(endpoint["matrix_rows"])
                if row[column] > 0
            ]
            column_scales[column] = (
                max(1.0, min(deck_bounds)) if deck_bounds else 1.0
            )
        column_scales[h11_index] = 4158.0
        forms = model["wave21"].six_counts()
        class_marginals = {
            source: int(forms[source].evaluate(4158))
            for source in range(1, 63)
        }
        for (source, _), column in model["b_index"].items():
            column_scales[column] = max(
                1.0,
                float(class_marginals[source]),
            )
        for (source, _, _), column in model["x_index"].items():
            column_scales[column] = max(
                1.0,
                float(93 * class_marginals[source]),
            )
        column_scaled = matrix.multiply(column_scales)
        row_maximum = np.asarray(
            abs(column_scaled).max(axis=1).toarray()
        ).ravel()
        row_scales = 1.0 / np.maximum(
            1.0,
            np.maximum(row_maximum, np.abs(targets)),
        )
        solve_matrix = column_scaled.multiply(row_scales[:, None])
        solve_targets = targets * row_scales
        scaled_lower = lower / column_scales
        scaled_upper = upper / column_scales
        result = linprog(
            c=np.zeros(variable_count, dtype=np.float64),
            A_eq=solve_matrix,
            b_eq=solve_targets,
            bounds=list(zip(scaled_lower, scaled_upper)),
            method="highs",
            options={
                "presolve": True,
                "time_limit": time_limit,
                "primal_feasibility_tolerance": 1e-9,
                "dual_feasibility_tolerance": 1e-9,
            },
        )

    maximum_residual = None
    maximum_scaled_residual = None
    maximum_relative_residual = None
    minimum_value = None
    positive_variables = None
    if result.x is not None:
        recovered = result.x if integer else result.x * column_scales
        residual = matrix @ recovered - targets
        maximum_residual = float(np.max(np.abs(residual)))
        maximum_scaled_residual = float(
            np.max(np.abs(solve_matrix @ result.x - solve_targets))
        )
        maximum_relative_residual = float(
            np.max(np.abs(residual) / np.maximum(1.0, np.abs(targets)))
        )
        minimum_value = float(np.min(recovered))
        positive_variables = int(np.count_nonzero(recovered > 1e-7))
    return {
        "format": "wave146-full-endpoint-six-seven-coupling-scout-v1",
        "scope": (
            "all seven-extendable six-class/weight cells, local rooted "
            "profiles, Wave141 moments, and complete endpoint order-seven deck"
        ),
        "model": {
            "variables": variable_count,
            "equalities": int(matrix.shape[0]),
            "nonzeros": int(matrix.nnz),
            "six_weight_cells": len(model["b_index"]),
            "root_extension_types": len(model["base"]["keys"]),
        },
        "solver": {
            "domain": "NONNEGATIVE_INTEGERS" if integer else "NONNEGATIVE_REALS",
            "status": int(result.status),
            "message": str(result.message),
            "success": bool(result.success),
            "time_limit_seconds": time_limit,
            "maximum_equality_residual": maximum_residual,
            "maximum_scaled_equality_residual": maximum_scaled_residual,
            "maximum_relative_equality_residual": maximum_relative_residual,
            "minimum_variable": minimum_value,
            "positive_variables": positive_variables,
            "column_aware_scaling": not integer,
            "solver_status_is_not_a_certificate": True,
        },
        "conclusion": (
            "NUMERICAL_FEASIBLE_CANDIDATE"
            if result.x is not None and result.success
            else "UNKNOWN"
        ),
        "limitations": [
            "Aggregate profile equations need not decompose into profiles for individual six-sets.",
            "Overlaps beyond one rooted seventh vertex are not retained.",
            "Numerical feasibility is not an exact rational certificate.",
            "Numerical infeasibility is not negative evidence without an exact Farkas certificate.",
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
