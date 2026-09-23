#!/usr/bin/env python3
"""Discover and exactly check affine structural kernels for Wave48 moments."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMBINED = HERE / "combined_sdp.py"
DEFAULT_OUTPUT = HERE / "exact-faces.json"
PRIMES = (1_000_003, 1_000_033, 1_000_037)


def load_combined() -> Any:
    name = "wave48_combined_for_faces"
    spec = importlib.util.spec_from_file_location(name, COMBINED)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load combined_sdp.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def numeric_rref(rows: np.ndarray, tolerance: float = 1e-8) -> np.ndarray:
    matrix = rows.copy()
    pivot_row = 0
    for column in range(matrix.shape[1]):
        if pivot_row == matrix.shape[0]:
            break
        candidate = max(
            range(pivot_row, matrix.shape[0]),
            key=lambda row: abs(matrix[row, column]),
        )
        if abs(matrix[candidate, column]) < tolerance:
            continue
        matrix[[pivot_row, candidate]] = matrix[[candidate, pivot_row]]
        matrix[pivot_row] /= matrix[pivot_row, column]
        for row in range(matrix.shape[0]):
            if row != pivot_row and abs(matrix[row, column]) >= tolerance:
                matrix[row] -= matrix[row, column] * matrix[pivot_row]
        pivot_row += 1
    matrix[np.abs(matrix) < tolerance] = 0.0
    return matrix[:pivot_row]


def primitive_integer_vector(
    values: Sequence[float],
    max_denominator: int = 10_000,
) -> tuple[int, ...]:
    fractions = [
        Fraction(float(value)).limit_denominator(max_denominator)
        for value in values
    ]
    denominator = math.lcm(*(value.denominator for value in fractions))
    integers = [
        value.numerator * (denominator // value.denominator)
        for value in fractions
    ]
    gcd = math.gcd(*(abs(value) for value in integers if value))
    integers = [value // gcd for value in integers]
    first = next(value for value in integers if value)
    if first < 0:
        integers = [-value for value in integers]
    return tuple(integers)


class ExactRowSpan:
    """Sparse exact echelon basis for homogeneous affine equations."""

    def __init__(self, rows: Iterable[dict[int, Fraction]]) -> None:
        self.pivots: dict[int, dict[int, Fraction]] = {}
        for row in rows:
            reduced = self.reduce(dict(row))
            if not reduced:
                continue
            pivot = min(reduced)
            factor = reduced[pivot]
            reduced = {
                column: value / factor
                for column, value in reduced.items()
                if value
            }
            self.pivots[pivot] = reduced

    def reduce(self, row: dict[int, Fraction]) -> dict[int, Fraction]:
        while row:
            pivot = min(row)
            basis = self.pivots.get(pivot)
            if basis is None:
                break
            factor = row[pivot]
            for column, value in basis.items():
                updated = row.get(column, Fraction()) - factor * value
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
        return row

    def contains(self, row: dict[int, Fraction]) -> bool:
        return not self.reduce(dict(row))


def exact_affine_row_span(row_system: dict[str, Any]) -> ExactRowSpan:
    rows = []
    for family_name in ("base", "vertex", "edge", "nonedge"):
        family = row_system["families"][family_name]
        for coefficients, rhs in zip(
            family["rows"],
            family["rhs"],
            strict=True,
        ):
            row = {
                column: Fraction(value)
                for column, value in enumerate(coefficients)
                if value
            }
            if rhs:
                row[209] = Fraction(-rhs)
            rows.append(row)
    span = ExactRowSpan(rows)
    if len(span.pivots) != 93:
        raise ValueError(f"exact Wave44 affine rank changed: {len(span.pivots)}")
    return span


def family_functionals(
    family: dict[str, Any],
    lower_counts: dict[int, dict[int, int]],
    class_index: dict[int, int],
    vector: Sequence[int],
) -> list[dict[int, Fraction]]:
    size = int(family["matrix_size"])
    if len(vector) != size:
        raise ValueError("kernel vector length changed")
    rows: list[dict[int, Fraction]] = [dict() for _ in range(size)]
    for record in family["class_coefficients"]:
        order = int(record["order"])
        mask = int(record["canonical_mask"])
        variable = None if order < 7 else class_index[mask]
        count = None if order == 7 else lower_counts[order][mask]
        for raw_row, raw_column, raw_coefficient in record["upper_entries"]:
            row = int(raw_row)
            column = int(raw_column)
            coefficient = int(raw_coefficient)
            contributions = [(row, coefficient * vector[column])]
            if row != column:
                contributions.append((column, coefficient * vector[row]))
            for output_row, value in contributions:
                if not value:
                    continue
                target_column = 209 if variable is None else variable
                scalar = value * (count if count is not None else 1)
                updated = rows[output_row].get(
                    target_column,
                    Fraction(),
                ) + scalar
                if updated:
                    rows[output_row][target_column] = Fraction(updated)
                else:
                    rows[output_row].pop(target_column, None)
    return rows


def diagonal_functional(
    family: dict[str, Any],
    lower_counts: dict[int, dict[int, int]],
    class_index: dict[int, int],
    diagonal: int,
) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for record in family["class_coefficients"]:
        order = int(record["order"])
        mask = int(record["canonical_mask"])
        for row, column, coefficient in record["upper_entries"]:
            if int(row) != diagonal or int(column) != diagonal:
                continue
            target_column = (
                class_index[mask] if order == 7 else 209
            )
            scalar = int(coefficient)
            if order < 7:
                scalar *= lower_counts[order][mask]
            result[target_column] = result.get(
                target_column,
                Fraction(),
            ) + scalar
    return {column: value for column, value in result.items() if value}


def modular_rref(
    rows: Sequence[Sequence[int]],
    rhs: Sequence[int],
    prime: int,
) -> tuple[list[list[int]], list[int]]:
    matrix = [
        [value % prime for value in row]
        + [target % prime]
        for row, target in zip(rows, rhs, strict=True)
    ]
    pivots: list[int] = []
    pivot_row = 0
    columns = len(rows[0])
    for column in range(columns):
        candidate = next(
            (
                row
                for row in range(pivot_row, len(matrix))
                if matrix[row][column]
            ),
            None,
        )
        if candidate is None:
            continue
        matrix[pivot_row], matrix[candidate] = (
            matrix[candidate],
            matrix[pivot_row],
        )
        inverse = pow(matrix[pivot_row][column], prime - 2, prime)
        matrix[pivot_row] = [
            value * inverse % prime for value in matrix[pivot_row]
        ]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                (left - factor * right) % prime
                for left, right in zip(
                    matrix[row],
                    matrix[pivot_row],
                    strict=True,
                )
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return matrix[:pivot_row], pivots


def modular_affine_basis(
    rows: Sequence[Sequence[int]],
    rhs: Sequence[int],
    prime: int,
) -> tuple[list[int], list[list[int]], int]:
    rref, pivots = modular_rref(rows, rhs, prime)
    pivot_set = set(pivots)
    free = [column for column in range(len(rows[0])) if column not in pivot_set]
    particular = [0] * len(rows[0])
    for row, pivot in zip(rref, pivots, strict=True):
        particular[pivot] = row[-1]
    nullspace: list[list[int]] = []
    for free_column in free:
        vector = [0] * len(rows[0])
        vector[free_column] = 1
        for row, pivot in zip(rref, pivots, strict=True):
            vector[pivot] = -row[free_column] % prime
        nullspace.append(vector)
    return particular, nullspace, len(pivots)


def exact_family_matrices(
    family: dict[str, Any],
    lower_counts: dict[int, dict[int, int]],
    class_index: dict[int, int],
) -> tuple[list[list[int]], list[list[list[int]]]]:
    size = int(family["matrix_size"])
    constant = [[0] * size for _ in range(size)]
    coefficients = [
        [[0] * size for _ in range(size)] for _ in range(208)
    ]
    for record in family["class_coefficients"]:
        order = int(record["order"])
        mask = int(record["canonical_mask"])
        target = constant if order < 7 else coefficients[class_index[mask]]
        scalar = lower_counts[order][mask] if order < 7 else 1
        for row, column, value in record["upper_entries"]:
            row = int(row)
            column = int(column)
            value = int(value) * scalar
            target[row][column] += value
            if row != column:
                target[column][row] += value
    return constant, coefficients


def matrix_linear_combination_mod(
    constant: Sequence[Sequence[int]],
    coefficients: Sequence[Sequence[Sequence[int]]],
    point: Sequence[int],
    prime: int,
    *,
    include_constant: bool,
) -> list[list[int]]:
    size = len(constant)
    result = [
        [constant[row][column] % prime if include_constant else 0 for column in range(size)]
        for row in range(size)
    ]
    for variable, scalar in enumerate(point[:208]):
        scalar %= prime
        if not scalar:
            continue
        matrix = coefficients[variable]
        for row in range(size):
            for column in range(size):
                if matrix[row][column]:
                    result[row][column] = (
                        result[row][column]
                        + scalar * matrix[row][column]
                    ) % prime
    return result


def rank_mod(rows: list[list[int]], prime: int) -> int:
    if not rows:
        return 0
    matrix = [[value % prime for value in row] for row in rows]
    rank = 0
    columns = len(matrix[0])
    for column in range(columns):
        candidate = next(
            (
                row
                for row in range(rank, len(matrix))
                if matrix[row][column]
            ),
            None,
        )
        if candidate is None:
            continue
        matrix[rank], matrix[candidate] = matrix[candidate], matrix[rank]
        inverse = pow(matrix[rank][column], prime - 2, prime)
        matrix[rank] = [
            value * inverse % prime for value in matrix[rank]
        ]
        for row in range(rank + 1, len(matrix)):
            if not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                (left - factor * right) % prime
                for left, right in zip(
                    matrix[row],
                    matrix[rank],
                    strict=True,
                )
            ]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def modular_active_rank(
    family: dict[str, Any],
    lower_counts: dict[int, dict[int, int]],
    class_index: dict[int, int],
    row_system: dict[str, Any],
    prime: int,
) -> int:
    rows = []
    rhs = []
    for family_name in ("base", "vertex", "edge", "nonedge"):
        block = row_system["families"][family_name]
        rows.extend(block["rows"])
        rhs.extend(block["rhs"])
    particular, nullspace, rank = modular_affine_basis(rows, rhs, prime)
    if rank != 93 or len(nullspace) != 116:
        raise ValueError("modular Wave44 rank/nullity changed")
    constant, coefficients = exact_family_matrices(
        family,
        lower_counts,
        class_index,
    )
    affine_matrices = [
        matrix_linear_combination_mod(
            constant,
            coefficients,
            particular,
            prime,
            include_constant=True,
        )
    ]
    affine_matrices.extend(
        matrix_linear_combination_mod(
            constant,
            coefficients,
            direction,
            prime,
            include_constant=False,
        )
        for direction in nullspace
    )
    stacked = [
        row
        for matrix in affine_matrices
        for row in matrix
    ]
    return rank_mod(stacked, prime)


def run() -> dict[str, Any]:
    combined = load_combined()
    combined.memory_guard("exact faces start")
    model = combined.build_problem()
    row_system = model["row_system"]
    exact_span = exact_affine_row_span(row_system)
    lower_counts = model["lower_counts"]
    class_index = {
        int(mask): index for index, mask in enumerate(row_system["classes"])
    }
    w45 = combined.load_frozen_json(combined.W45_COEFFICIENTS)
    w47 = combined.load_frozen_json(combined.W47_COEFFICIENTS)
    family_payloads = {
        ("wave45", name): family
        for name, family in w45["families"].items()
    }
    family_payloads.update(
        {
            ("wave47", name): family
            for name, family in w47["families"].items()
        }
    )

    records = []
    for model_record in model["moment_records"]:
        source = model_record["source"]
        name = model_record["name"]
        family = family_payloads[(source, name)]
        basis = model_record["support_basis"]
        ambient = basis.shape[0]
        active = basis.shape[1]
        if active == ambient:
            candidate_vectors: list[tuple[int, ...]] = []
        else:
            _, _, right_t = np.linalg.svd(
                basis.T,
                full_matrices=True,
            )
            numeric_kernel = right_t[active:, :]
            canonical_numeric = numeric_rref(numeric_kernel)
            candidate_vectors = [
                primitive_integer_vector(row) for row in canonical_numeric
            ]
        exact_checks = []
        for vector in candidate_vectors:
            functionals = family_functionals(
                family,
                lower_counts,
                class_index,
                vector,
            )
            residuals = [
                exact_span.reduce(dict(functional))
                for functional in functionals
            ]
            exact = all(not residual for residual in residuals)
            exact_checks.append(
                {
                    "vector": list(vector),
                    "support": [
                        [index, value]
                        for index, value in enumerate(vector)
                        if value
                    ],
                    "primitive": math.gcd(
                        *(abs(value) for value in vector if value)
                    )
                    == 1,
                    "exact_affine_kernel_identity": exact,
                    "nonzero_reduced_rows": sum(bool(row) for row in residuals),
                    "vector_sha256": sha256_bytes(
                        json.dumps(list(vector), separators=(",", ":")).encode("ascii")
                    ),
                }
            )
        forced_zero_diagonals = []
        for diagonal in range(ambient):
            functional = diagonal_functional(
                family,
                lower_counts,
                class_index,
                diagonal,
            )
            if exact_span.contains(functional):
                forced_zero_diagonals.append(diagonal)
        modular_ranks = {
            str(prime): modular_active_rank(
                family,
                lower_counts,
                class_index,
                row_system,
                prime,
            )
            for prime in PRIMES
        }
        all_exact = all(
            item["exact_affine_kernel_identity"] for item in exact_checks
        )
        candidate_nullity = len(candidate_vectors)
        modular_complete = all(
            rank == ambient - candidate_nullity
            for rank in modular_ranks.values()
        )
        records.append(
            {
                "source": source,
                "name": name,
                "ambient_size": ambient,
                "candidate_active_rank": active,
                "candidate_nullity": candidate_nullity,
                "kernel_vectors": exact_checks,
                "all_kernel_vectors_exact_affine_identities": all_exact,
                "forced_zero_diagonals": forced_zero_diagonals,
                "modular_active_ranks": modular_ranks,
                "exact_rational_active_rank_certified": (
                    ambient - candidate_nullity
                    if all_exact and modular_complete
                    else None
                ),
                "exact_rational_nullity_certified": (
                    candidate_nullity
                    if all_exact and modular_complete
                    else None
                ),
            }
        )
        combined.memory_guard(f"exact faces {source}/{name}")

    all_sealed = all(
        record["exact_rational_nullity_certified"] is not None
        for record in records
    )
    return {
        "format": "wave48-exact-affine-moment-faces-v1",
        "role": "proof_b",
        "claim_label": "DERIVED" if all_sealed else "CANDIDATE",
        "scope": (
            "exact universal kernels of the Wave45 and Wave47 moment "
            "families on the rational affine space defined by all 170 "
            "Wave44 equations"
        ),
        "wave44_exact_affine_rank": len(exact_span.pivots),
        "wave44_exact_affine_nullity": 209 - len(exact_span.pivots),
        "modular_primes": list(PRIMES),
        "families": records,
        "all_families_exactly_sealed": all_sealed,
        "limitations": [
            "These are affine structural faces, not a feasible SDP witness.",
            "Positive-semidefinite feasibility after facial reduction remains numerical.",
            "The Wave47 coefficient package is CANDIDATE pending independent verification.",
            "No endpoint exclusion or graph construction follows.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run()
    payload = canonical_payload(result)
    if args.verify:
        if args.output.read_bytes() != payload:
            raise ValueError("stored exact-face result differs")
        print(
            "PASS_EXACT_FACE_REPLAY "
            f"sha256={sha256_bytes(payload)} "
            f"families={len(result['families'])}"
        )
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(
        json.dumps(
            {
                "all_families_exactly_sealed": result[
                    "all_families_exactly_sealed"
                ],
                "families": [
                    {
                        "name": f"{record['source']}/{record['name']}",
                        "rank": record[
                            "exact_rational_active_rank_certified"
                        ],
                        "nullity": record[
                            "exact_rational_nullity_certified"
                        ],
                    }
                    for record in result["families"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"result_sha256={sha256_bytes(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
