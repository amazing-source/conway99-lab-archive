#!/usr/bin/env python3
"""Discover and exactly replay a rational Wave146 endpoint witness.

The numerical solution is obtained only after column-aware combinatorial
scaling.  Every recovered coordinate is reconstructed with denominator at
most four, and the final sparse vector is accepted only if all 8,981 integer
equalities hold exactly over ``fractions.Fraction``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linprog


ROOT = Path(__file__).resolve().parents[2]
FULL_MODEL_PATH = (
    ROOT / "attempts/wave146-six-seven-coupling/full_endpoint_coupling_scout.py"
)
DEFAULT_OUTPUT = ROOT / "attempts/wave146-six-seven-coupling/exact-results.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_full_model() -> Any:
    specification = importlib.util.spec_from_file_location(
        "wave146_exact_full_model",
        FULL_MODEL_PATH,
    )
    require(
        specification is not None and specification.loader is not None,
        "cannot load full endpoint model",
    )
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def combinatorial_column_scales(model: dict[str, Any], variable_count: int) -> np.ndarray:
    endpoint = model["base"]["wave43"]
    scales = np.ones(variable_count, dtype=np.float64)
    for column in range(len(endpoint["classes"])):
        deck_bounds = [
            endpoint["deck_rhs"][row_index] / row[column]
            for row_index, row in enumerate(endpoint["matrix_rows"])
            if row[column] > 0
        ]
        scales[column] = max(1.0, min(deck_bounds)) if deck_bounds else 1.0
    h11_index = len(endpoint["classes"])
    scales[h11_index] = 4158.0

    forms = model["wave21"].six_counts()
    class_marginals = {
        source: int(forms[source].evaluate(4158))
        for source in range(1, 63)
    }
    for (source, _), column in model["b_index"].items():
        scales[column] = max(1.0, float(class_marginals[source]))
    for (source, _, _), column in model["x_index"].items():
        scales[column] = max(1.0, float(93 * class_marginals[source]))
    return scales


def exact_replay(
    model: dict[str, Any],
    matrix: Any,
    targets: np.ndarray,
    values: list[Fraction],
) -> dict[str, Any]:
    require(len(values) == matrix.shape[1], "candidate vector length mismatch")
    require(all(value >= 0 for value in values), "candidate has a negative coordinate")
    h11_index = len(model["base"]["wave43"]["classes"])
    require(
        Fraction(2079) <= values[h11_index] <= Fraction(4158),
        "h11/4 is outside the endpoint interval",
    )
    failures = []
    for row_index in range(matrix.shape[0]):
        row = matrix[row_index:row_index + 1, :]
        actual = sum(
            (
                Fraction(int(coefficient)) * values[int(column)]
                for column, coefficient in zip(row.indices, row.data)
            ),
            Fraction(0),
        )
        expected = Fraction(int(targets[row_index]))
        if actual != expected:
            failures.append(
                {
                    "row_index": row_index,
                    "actual": str(actual),
                    "expected": str(expected),
                }
            )
            if len(failures) == 20:
                break
    require(not failures, f"exact equality replay failed: {failures}")
    denominators = [value.denominator for value in values if value]
    return {
        "verification": "PASS",
        "variables": matrix.shape[1],
        "equalities": matrix.shape[0],
        "matrix_nonzeros": int(matrix.nnz),
        "positive_variables": sum(value > 0 for value in values),
        "maximum_denominator": max(denominators, default=1),
        "h11_over_4": str(values[h11_index]),
        "h11": str(4 * values[h11_index]),
    }


def sparse_candidate(
    labels: list[str],
    values: list[Fraction],
) -> list[dict[str, Any]]:
    return [
        {
            "label": label,
            "numerator": value.numerator,
            "denominator": value.denominator,
        }
        for label, value in zip(labels, values)
        if value
    ]


def discover(time_limit: float) -> dict[str, Any]:
    full = load_full_model()
    model = full.build_model()
    matrix, targets, _ = full.sparse_constraints(model)
    scales = combinatorial_column_scales(model, matrix.shape[1])
    column_scaled = matrix.multiply(scales)
    row_maximum = np.asarray(
        abs(column_scaled).max(axis=1).toarray()
    ).ravel()
    row_scales = 1.0 / np.maximum(
        1.0,
        np.maximum(row_maximum, np.abs(targets)),
    )
    solve_matrix = column_scaled.multiply(row_scales[:, None])
    solve_targets = targets * row_scales
    h11_index = len(model["base"]["wave43"]["classes"])
    bounds = [(0.0, None)] * matrix.shape[1]
    bounds[h11_index] = (2079.0 / 4158.0, 1.0)
    result = linprog(
        c=np.zeros(matrix.shape[1], dtype=np.float64),
        A_eq=solve_matrix,
        b_eq=solve_targets,
        bounds=bounds,
        method="highs",
        options={
            "presolve": True,
            "time_limit": time_limit,
            "primal_feasibility_tolerance": 1e-9,
            "dual_feasibility_tolerance": 1e-9,
        },
    )
    require(result.success and result.x is not None, f"scout failed: {result.message}")
    recovered = result.x * scales
    values = [
        Fraction(0)
        if abs(float(value)) < 1e-4
        else Fraction(float(value)).limit_denominator(4)
        for value in recovered
    ]
    replay = exact_replay(model, matrix, targets, values)
    support = sparse_candidate(model["variable_labels"], values)
    support_bytes = json.dumps(
        support,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return {
        "format": "wave146-full-endpoint-rational-witness-v1",
        "role": "construction",
        "claim_label": "EXACT_RATIONAL_RELAXATION_WITNESS",
        "scope": (
            "all seven-extendable six-class/weight cells, aggregate local "
            "profiles, Wave141 moments, and the complete endpoint order-seven deck"
        ),
        "parameters": {
            "srg": [99, 14, 1, 2],
            "n3": 4158,
            "h11_interval": [8316, 16632],
        },
        "model": replay,
        "discovery_solver": {
            "engine": "scipy.optimize.linprog with bundled HiGHS",
            "status": int(result.status),
            "message": str(result.message),
            "time_limit_seconds": time_limit,
            "column_aware_scaling": True,
            "solver_status_is_not_certificate_authority": True,
        },
        "candidate": {
            "support_sha256": hashlib.sha256(support_bytes).hexdigest(),
            "support": support,
        },
        "conclusion": {
            "one_root_six_to_seven_relaxation": "EXACT_RATIONAL_FEASIBLE",
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "graph_construction": False,
            "conway_99": "UNKNOWN",
        },
        "limitations": [
            "Aggregate X variables need not decompose into local profiles for every individual six-set.",
            "Different rooted seven-set views are not coupled on eight or more vertices.",
            "A rational aggregate witness is not a graph or code realization.",
            "No automorphism of a putative graph is assumed.",
        ],
    }


def verify(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(
        payload.get("format") == "wave146-full-endpoint-rational-witness-v1",
        "unexpected candidate format",
    )
    full = load_full_model()
    model = full.build_model()
    matrix, targets, _ = full.sparse_constraints(model)
    index = {
        label: position
        for position, label in enumerate(model["variable_labels"])
    }
    values = [Fraction(0)] * len(index)
    seen = set()
    support = payload.get("candidate", {}).get("support")
    require(isinstance(support, list), "candidate support missing")
    for record in support:
        require(
            isinstance(record, dict)
            and set(record) == {"label", "numerator", "denominator"},
            "malformed support record",
        )
        label = record["label"]
        numerator = record["numerator"]
        denominator = record["denominator"]
        require(
            isinstance(label, str)
            and type(numerator) is int
            and type(denominator) is int
            and denominator > 0,
            "invalid support scalar",
        )
        require(label in index and label not in seen, "unknown or duplicate label")
        seen.add(label)
        value = Fraction(numerator, denominator)
        require(value > 0, "sparse support values must be positive")
        values[index[label]] = value
    canonical_support = sparse_candidate(model["variable_labels"], values)
    require(canonical_support == support, "support is not in canonical order")
    support_bytes = json.dumps(
        support,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    require(
        hashlib.sha256(support_bytes).hexdigest()
        == payload["candidate"]["support_sha256"],
        "support digest mismatch",
    )
    replay = exact_replay(model, matrix, targets, values)
    require(replay == payload["model"], "stored model summary mismatch")
    return {
        "verification": "PASS",
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        **replay,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    require(1 <= arguments.time_limit <= 1800, "invalid time limit")
    if arguments.verify is not None:
        print(json.dumps(verify(arguments.verify), indent=2, sort_keys=True))
        return 0
    result = discover(arguments.time_limit)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    output = arguments.output or DEFAULT_OUTPUT
    output.write_text(rendered, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": str(output),
                "sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
                "positive_variables": result["model"]["positive_variables"],
                "maximum_denominator": result["model"]["maximum_denominator"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
