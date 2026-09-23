#!/usr/bin/env python3
"""Reconstruct an exact rational witness on the zero-covariance face.

The input is a floating HiGHS scout.  It is used only to select a support and
round the order-seven counts.  Every promoted value is then solved and checked
with exact integer/rational arithmetic.  A successful witness certifies only
feasibility of this finite relaxation; it is not a graph.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from flint import fmpq, fmpz_mat


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "endpoint_sdp.py"
DEFAULT_CANDIDATE = HERE / "marked-rank1-both-highs-explicit.json"
MARKED_PATH = ROOT / "attempts/wave148-marked-order8/marked-rows.json.gz"
COEFFICIENTS_PATH = (
    ROOT / "attempts/wave147-alternative-lane/coefficients.json.gz"
)
ROW_SYSTEM_PATH = ROOT / "attempts/wave44-rooted-flags/row-system.json"

N = 99
C7 = math.comb(N, 7)
C8 = math.comb(N, 8)
Y = 2079
MODULUS = 1_000_003


@dataclass(frozen=True)
class ExactRow:
    label: str
    coefficients: dict[int, int]
    rhs: int


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def add_row(
    rows: list[ExactRow],
    label: str,
    coefficients: dict[int, int],
    rhs: int,
) -> None:
    cleaned = {column: value for column, value in coefficients.items() if value}
    if not cleaned:
        require(rhs == 0, f"constant contradiction in {label}: {rhs}")
        return
    rows.append(ExactRow(label, cleaned, int(rhs)))


def rounded_order7(
    candidate: dict[str, Any],
    row_system: dict[str, Any],
) -> tuple[list[int], dict[str, Any]]:
    density = np.asarray(candidate["candidate"]["p7_density"], dtype=np.float64)
    raw = density * C7
    rounded = np.rint(raw).astype(np.int64)
    require(float(np.max(np.abs(raw - rounded))) < 0.01, "x7 rounding unsafe")
    require(int(rounded.min()) >= 0, "negative rounded x7")
    require(int(rounded.sum()) == C7, "rounded x7 total changed")
    require(abs(float(candidate["candidate"]["y_approx"]) - Y) < 0.01, "y changed")

    errors: list[tuple[str, int, int]] = []
    for family_name in ("base", "vertex", "edge", "nonedge"):
        family = row_system["families"][family_name]
        for index, (row, rhs) in enumerate(
            zip(family["rows"], family["rhs"], strict=True)
        ):
            value = (
                sum(int(a) * int(b) for a, b in zip(row[:-1], rounded, strict=True))
                + int(row[-1]) * Y
                - int(rhs)
            )
            if value:
                errors.append((family_name, index, value))
    require(not errors, f"rounded x7 fails Wave44: {errors[:3]}")
    return rounded.tolist(), {
        "sum": int(rounded.sum()),
        "support": int(np.count_nonzero(rounded)),
        "maximum_rounding_error": float(np.max(np.abs(raw - rounded))),
        "y": Y,
        "wave44_rows_passed": sum(
            len(row_system["families"][name]["rows"])
            for name in ("base", "vertex", "edge", "nonedge")
        ),
    }


def build_rows(
    inputs: dict[str, Any],
    x7: list[int],
) -> tuple[list[ExactRow], dict[str, Any]]:
    coefficients = inputs["coefficient_payload"]
    marked = json.loads(gzip.decompress(MARKED_PATH.read_bytes()))
    classes7 = tuple(int(mask) for mask in inputs["classes"][7])
    classes8 = tuple(int(mask) for mask in inputs["classes8"])
    lower = inputs["lower_counts"]
    index7 = {mask: index for index, mask in enumerate(classes7)}
    index8 = {mask: index for index, mask in enumerate(classes8)}
    rows: list[ExactRow] = []

    add_row(rows, "sum_x8", {column: 1 for column in range(len(classes8))}, C8)

    deletion_count = 0
    for record in coefficients["order7_to_order8_deletion_equations"]:
        mask7 = int(record["order7_mask"])
        terms = {
            index8[int(mask8)]: int(multiplicity)
            for mask8, multiplicity in record["terms_order8_mask_multiplicity"]
        }
        add_row(
            rows,
            f"D:{mask7}",
            terms,
            int(record["left_multiplier"]) * x7[index7[mask7]],
        )
        deletion_count += 1

    marked_count = 0
    for family_name in ("vertex_rows", "ordered_pair_rows"):
        for record in marked[family_name]:
            mask7 = int(record["order7_mask"])
            terms = {
                index8[int(mask8)]: int(value)
                for mask8, value in record["terms_order8_mask_coefficient"]
            }
            add_row(
                rows,
                str(record["row_id"]),
                terms,
                int(record["lhs_coefficient"]) * x7[index7[mask7]],
            )
            marked_count += 1

    moment_counts: dict[str, int] = {}
    for family_name, root_count in (
        ("ordered_edge", N * 14),
        ("ordered_nonedge", N * 84),
    ):
        family = coefficients["families"][family_name]
        size = int(family["matrix_size"])
        mean = [0] * size
        fixed: dict[tuple[int, int], int] = {}
        order8: dict[tuple[int, int], dict[int, int]] = {}

        for record in family["class_coefficients"]:
            order = int(record["order"])
            mask = int(record["canonical_mask"])
            if order in (5, 6):
                count = int(lower[order][mask])
            elif order == 7:
                count = int(x7[index7[mask]])
            else:
                count = 0
            for row, column, value in record["upper_entries"]:
                key = (int(row), int(column))
                integer_value = int(value)
                if order <= 7:
                    fixed[key] = fixed.get(key, 0) + count * integer_value
                    if order == 5:
                        require(row == column, "order-five matrix is not diagonal")
                        mean[int(row)] += count * integer_value
                else:
                    bucket = order8.setdefault(key, {})
                    bucket[index8[mask]] = integer_value

        require(
            sum(mean) == root_count * math.comb(N - 2, 3),
            f"{family_name} first-moment total changed",
        )
        emitted = 0
        for row in range(size):
            for column in range(row, size):
                key = (row, column)
                terms = {
                    variable: root_count * value
                    for variable, value in order8.get(key, {}).items()
                }
                rhs = mean[row] * mean[column] - root_count * fixed.get(key, 0)
                add_row(rows, f"M:{family_name}:{row}:{column}", terms, rhs)
                emitted += 1
        moment_counts[family_name] = emitted

    return rows, {
        "rows_after_trivial_removal": len(rows),
        "deletion_rows": deletion_count,
        "marked_rows_seen": marked_count,
        "moment_upper_entries": moment_counts,
    }


def candidate_support(
    candidate: dict[str, Any],
) -> tuple[list[int], dict[str, Any]]:
    raw = np.asarray(candidate["candidate"]["p8_density"], dtype=np.float64) * C8
    support = [index for index, value in enumerate(raw) if value > 1.0]
    outside = [abs(float(raw[index])) for index in range(len(raw)) if index not in support]
    require(len(support) == 874, f"candidate support changed: {len(support)}")
    require(max(outside, default=0.0) < 0.1, "excluded candidate coordinate too large")
    return support, {
        "support_size": len(support),
        "excluded_maximum_absolute_raw_count": max(outside, default=0.0),
        "minimum_included_raw_count": min(float(raw[index]) for index in support),
    }


def restrict_rows(
    rows: list[ExactRow],
    support: list[int],
) -> tuple[list[ExactRow], dict[int, int]]:
    local = {global_index: index for index, global_index in enumerate(support)}
    restricted: list[ExactRow] = []
    for row in rows:
        coefficients = {
            local[column]: value
            for column, value in row.coefficients.items()
            if column in local
        }
        if not coefficients:
            require(row.rhs == 0, f"support contradicts {row.label}")
            continue
        restricted.append(ExactRow(row.label, coefficients, row.rhs))
    return restricted, local


def modular_independent_rows(
    rows: list[ExactRow],
    variable_count: int,
) -> tuple[list[int], dict[str, Any]]:
    pivots: dict[int, dict[int, int]] = {}
    selected: list[int] = []
    for row_index, row in enumerate(rows):
        vector = {
            column: value % MODULUS
            for column, value in row.coefficients.items()
            if value % MODULUS
        }
        while vector:
            pivot = min(vector)
            if pivot not in pivots:
                inverse = pow(vector[pivot], -1, MODULUS)
                vector = {
                    column: (value * inverse) % MODULUS
                    for column, value in vector.items()
                    if (value * inverse) % MODULUS
                }
                pivots[pivot] = vector
                selected.append(row_index)
                break
            factor = vector[pivot]
            pivot_row = pivots[pivot]
            for column, value in pivot_row.items():
                updated = (vector.get(column, 0) - factor * value) % MODULUS
                if updated:
                    vector[column] = updated
                else:
                    vector.pop(column, None)
        if len(selected) == variable_count:
            break
    return selected, {
        "modulus": MODULUS,
        "rank": len(selected),
        "variables": variable_count,
        "full_column_rank": len(selected) == variable_count,
        "rows_scanned": (
            selected[-1] + 1 if len(selected) == variable_count else len(rows)
        ),
    }


def exact_solve_and_verify(
    rows: list[ExactRow],
    selected: list[int],
    variable_count: int,
) -> tuple[list[fmpq], dict[str, Any]]:
    require(len(selected) == variable_count, "selected system is not square")
    flat = [0] * (variable_count * variable_count)
    rhs = [0] * variable_count
    for matrix_row, row_index in enumerate(selected):
        row = rows[row_index]
        offset = matrix_row * variable_count
        for column, value in row.coefficients.items():
            flat[offset + column] = value
        rhs[matrix_row] = row.rhs
    matrix = fmpz_mat(variable_count, variable_count, flat)
    target = fmpz_mat(variable_count, 1, rhs)
    solution_matrix = matrix.solve(target)
    solution = [solution_matrix[index, 0] for index in range(variable_count)]

    failures = []
    for row_index, row in enumerate(rows):
        value = sum(
            (fmpq(coefficient) * solution[column]
            for column, coefficient in row.coefficients.items()),
            fmpq(0),
        )
        if value != row.rhs:
            failures.append((row_index, row.label, str(value), str(row.rhs)))
            if len(failures) >= 10:
                break
    require(not failures, f"exact row replay failed: {failures}")
    require(all(value >= 0 for value in solution), "exact solution is negative")
    denominators = [int(value.q) for value in solution]
    numerators = [int(value.p) for value in solution]
    return solution, {
        "all_rows_passed": len(rows),
        "minimum_numerator": min(numerators),
        "maximum_numerator": max(numerators),
        "maximum_denominator": max(denominators),
        "distinct_denominators": len(set(denominators)),
        "integer_coordinates": sum(denominator == 1 for denominator in denominators),
    }


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--selection-output", type=Path)
    parser.add_argument("--selection", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--select-only", action="store_true")
    args = parser.parse_args()

    started = time.time()
    model = load_module("wave150_endpoint_model", MODEL_PATH)
    inputs = model.load_inputs(True)
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    row_system = json.loads(ROW_SYSTEM_PATH.read_text(encoding="utf-8"))
    x7, x7_record = rounded_order7(candidate, row_system)
    rows, row_record = build_rows(inputs, x7)
    support, support_record = candidate_support(candidate)
    restricted, _ = restrict_rows(rows, support)

    if args.selection:
        selection_payload = json.loads(args.selection.read_text(encoding="utf-8"))
        selected = [int(index) for index in selection_payload["selected_row_indices"]]
        modular_record = selection_payload["modular_rank"]
    else:
        selected, modular_record = modular_independent_rows(
            restricted, len(support)
        )

    selection_result = {
        "format": "wave150-rank1-selection-v1",
        "candidate_sha256": sha256_file(args.candidate),
        "support": support,
        "support_record": support_record,
        "x7_record": x7_record,
        "row_record": row_record,
        "restricted_rows": len(restricted),
        "modular_rank": modular_record,
        "selected_row_indices": selected,
        "selected_row_labels": [restricted[index].label for index in selected],
        "elapsed_seconds": time.time() - started,
    }
    if args.selection_output:
        args.selection_output.write_bytes(canonical_json_bytes(selection_result))
    if args.select_only:
        print(
            json.dumps(
                {
                    "rank": modular_record["rank"],
                    "variables": len(support),
                    "rows": len(restricted),
                    "selection_output": (
                        None if args.selection_output is None else str(args.selection_output)
                    ),
                    "elapsed_seconds": time.time() - started,
                },
                sort_keys=True,
            )
        )
        return 0

    solution, solve_record = exact_solve_and_verify(
        restricted, selected, len(support)
    )
    full_solution = [fmpq(0)] * len(inputs["classes8"])
    for global_index, value in zip(support, solution, strict=True):
        full_solution[global_index] = value
    full_failures = []
    for row_index, row in enumerate(rows):
        value = sum(
            (
                fmpq(coefficient) * full_solution[column]
                for column, coefficient in row.coefficients.items()
            ),
            fmpq(0),
        )
        if value != row.rhs:
            full_failures.append((row_index, row.label, str(value), str(row.rhs)))
            if len(full_failures) >= 10:
                break
    require(not full_failures, f"full exact row replay failed: {full_failures}")
    solve_record["restricted_rows_passed"] = solve_record.pop("all_rows_passed")
    solve_record["all_rows_passed"] = len(rows)
    classes7 = tuple(int(mask) for mask in inputs["classes"][7])
    classes8 = tuple(int(mask) for mask in inputs["classes8"])
    witness = {
        "format": "wave150-exact-rank1-endpoint-witness-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Exact rational feasibility of the n3=4158 Wave44+Wave147+Wave148 "
            "count system on the zero-centered-covariance face."
        ),
        "target": {"srg": [99, 14, 1, 2], "n3": 4158, "h11": 4 * Y},
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path)
            for path in (
                args.candidate,
                MODEL_PATH,
                MARKED_PATH,
                COEFFICIENTS_PATH,
                ROW_SYSTEM_PATH,
            )
        },
        "selection": selection_result,
        "exact_solve": solve_record,
        "x7_support": [
            {"canonical_mask": mask, "count": count}
            for mask, count in zip(classes7, x7, strict=True)
            if count
        ],
        "x8_support": [
            {
                "canonical_mask": classes8[global_index],
                "count": str(value),
            }
            for global_index, value in zip(support, solution, strict=True)
            if value
        ],
        "conclusion": {
            "finite_relaxation": "EXACT_RATIONAL_FEASIBLE",
            "graph_constructed": False,
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "This exact count vector is not a graph.",
            "The discovery package cannot verify itself.",
            "Higher-order overlap consistency is not represented.",
        ],
        "elapsed_seconds": time.time() - started,
    }
    require(args.output is not None, "--output is required for a full solve")
    args.output.write_bytes(canonical_json_bytes(witness))
    print(
        json.dumps(
            {
                "output": str(args.output),
                "support7": len(witness["x7_support"]),
                "support8": len(witness["x8_support"]),
                "maximum_denominator": solve_record["maximum_denominator"],
                "rows_passed": solve_record["all_rows_passed"],
                "elapsed_seconds": witness["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
