"""Exact affine-face rank computation for corrected Wave134.

The 161 forbidden dual orbit rows are transformed into integer character
rows on the 1,119 primal orbit variables.  FLINT computes exact rational
RREFs; an independent finite-field elimination supplies compact nonzero-minor
certificates for the two full-row-rank claims.
"""

from __future__ import annotations

import argparse
import ctypes
import importlib.util
import json
import math
from pathlib import Path

from flint import fmpq_mat


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE134 = ROOT / "attempts" / "wave134-z4-symmetrized-enumerator"
SPEC = importlib.util.spec_from_file_location(
    "wave134_exact_check", WAVE134 / "exact_check.py"
)
MODEL = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODEL)
DEFAULT_OUTPUT = HERE / "face-rank.json"
PRIME = 2_147_483_647


class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_phys", ctypes.c_ulonglong),
        ("avail_phys", ctypes.c_ulonglong),
        ("total_page", ctypes.c_ulonglong),
        ("avail_page", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("avail_virtual", ctypes.c_ulonglong),
        ("avail_extended_virtual", ctypes.c_ulonglong),
    ]


def free_memory_percent() -> float:
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.avail_phys / status.total_phys


def character_rows() -> tuple[list[tuple[int, int, int]], list[list[int]]]:
    sources = MODEL.primal_states()
    targets = MODEL.forbidden_dual_states()
    rows = [
        [
            MODEL.transform_coefficient(source, target)
            for source in sources
        ]
        for target in targets
    ]
    return sources, rows


def pivot_columns_from_rref(matrix, rank: int) -> list[int]:
    pivots = []
    for row in range(rank):
        pivot = next(
            column for column in range(matrix.ncols()) if matrix[row, column]
        )
        pivots.append(pivot)
    return pivots


def modular_rank_and_pivots(
    rows: list[list[int]], prime: int
) -> tuple[int, list[int]]:
    work = [[value % prime for value in row] for row in rows]
    row_count = len(work)
    column_count = len(work[0]) if work else 0
    pivot_row = 0
    pivots = []
    for column in range(column_count):
        selected = next(
            (
                row
                for row in range(pivot_row, row_count)
                if work[row][column]
            ),
            None,
        )
        if selected is None:
            continue
        work[pivot_row], work[selected] = work[selected], work[pivot_row]
        inverse = pow(work[pivot_row][column], prime - 2, prime)
        work[pivot_row] = [
            value * inverse % prime for value in work[pivot_row]
        ]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    (left - factor * right) % prime
                    for left, right in zip(work[row], work[pivot_row])
                ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row, pivots


def modular_independent_row_indices(
    rows: list[list[int]], prime: int
) -> list[int]:
    """Return a greedy independent original-row basis modulo ``prime``."""
    basis: dict[int, list[int]] = {}
    selected = []
    for index, original in enumerate(rows):
        row = [value % prime for value in original]
        for pivot in sorted(basis):
            factor = row[pivot]
            if factor:
                row = [
                    (left - factor * right) % prime
                    for left, right in zip(row, basis[pivot])
                ]
        pivot = next((column for column, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        inverse = pow(row[pivot], prime - 2, prime)
        row = [value * inverse % prime for value in row]
        basis[pivot] = row
        selected.append(index)
    return selected


def encode_rational(value) -> str:
    numerator = int(value.numerator)
    denominator = int(value.denominator)
    if denominator == 1:
        return str(numerator)
    return f"{numerator}/{denominator}"


def primitive_relation(values) -> list[int]:
    denominators = [int(value.denominator) for value in values]
    common = 1
    for denominator in denominators:
        common = math.lcm(common, denominator)
    integers = [
        int(value.numerator) * (common // int(value.denominator))
        for value in values
    ]
    divisor = 0
    for value in integers:
        divisor = math.gcd(divisor, abs(value))
    if divisor:
        integers = [value // divisor for value in integers]
    first = next((value for value in integers if value), 1)
    if first < 0:
        integers = [-value for value in integers]
    return integers


def left_dependency_basis(matrix, rank: int) -> list[list[int]]:
    """Compute a primitive integer basis of ker(matrix^T) exactly."""
    echelon, transpose_rank = matrix.transpose().rref()
    if transpose_rank != rank:
        raise AssertionError("transpose rank disagrees")
    pivots = pivot_columns_from_rref(echelon, transpose_rank)
    pivot_set = set(pivots)
    free = [
        column for column in range(matrix.nrows()) if column not in pivot_set
    ]
    relations = []
    for free_column in free:
        vector = [0] * matrix.nrows()
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -echelon[row, free_column]
        relations.append(primitive_relation(vector))
    return relations


def compute() -> dict:
    before = free_memory_percent()
    if before < 15:
        raise RuntimeError("free physical memory below 15%")
    sources, zero_rows = character_rows()
    targets = MODEL.forbidden_dual_states()
    if (len(sources), len(zero_rows)) != (1119, 161):
        raise AssertionError("corrected Wave134 dimensions changed")

    zero_matrix = fmpq_mat(
        len(zero_rows),
        len(sources),
        [value for row in zero_rows for value in row],
    )
    zero_echelon, zero_rank = zero_matrix.rref()
    zero_pivots = pivot_columns_from_rref(zero_echelon, zero_rank)
    dependency_basis = left_dependency_basis(zero_matrix, zero_rank)
    modular_zero_rank, modular_zero_pivots = modular_rank_and_pivots(
        zero_rows, PRIME
    )
    independent_row_indices = modular_independent_row_indices(
        zero_rows, PRIME
    )
    del zero_matrix, zero_echelon

    combined_rows = list(zero_rows)
    combined_rows.append([1] * len(sources))
    zero_index = sources.index((99, 0, 0))
    unit = [0] * len(sources)
    unit[zero_index] = 1
    combined_rows.append(unit)
    combined_matrix = fmpq_mat(
        len(combined_rows),
        len(sources),
        [value for row in combined_rows for value in row],
    )
    combined_echelon, combined_rank = combined_matrix.rref()
    combined_pivots = pivot_columns_from_rref(
        combined_echelon, combined_rank
    )
    modular_combined_rank, modular_combined_pivots = (
        modular_rank_and_pivots(combined_rows, PRIME)
    )

    right_hand_side = [0] * len(zero_rows) + [1 << 108, 1]
    augmented_rows = [
        row + [right]
        for row, right in zip(combined_rows, right_hand_side)
    ]
    augmented_matrix = fmpq_mat(
        len(augmented_rows),
        len(sources) + 1,
        [value for row in augmented_rows for value in row],
    )
    _augmented_echelon, augmented_rank = augmented_matrix.rref()
    modular_augmented_rank, modular_augmented_pivots = (
        modular_rank_and_pivots(augmented_rows, PRIME)
    )

    torsion_shell = [
        1 if state[1] == 0 else 0 for state in sources
    ]
    extended_rows = combined_rows + [torsion_shell]
    extended_right_hand_side = right_hand_side + [1 << 54]
    extended_matrix = fmpq_mat(
        len(extended_rows),
        len(sources),
        [value for row in extended_rows for value in row],
    )
    extended_echelon, extended_rank = extended_matrix.rref()
    extended_pivots = pivot_columns_from_rref(
        extended_echelon, extended_rank
    )
    modular_extended_rank, modular_extended_pivots = (
        modular_rank_and_pivots(extended_rows, PRIME)
    )
    extended_augmented_rows = [
        row + [right]
        for row, right in zip(
            extended_rows, extended_right_hand_side
        )
    ]
    extended_augmented_matrix = fmpq_mat(
        len(extended_augmented_rows),
        len(sources) + 1,
        [
            value
            for row in extended_augmented_rows
            for value in row
        ],
    )
    _extended_augmented_echelon, extended_augmented_rank = (
        extended_augmented_matrix.rref()
    )
    (
        modular_extended_augmented_rank,
        modular_extended_augmented_pivots,
    ) = modular_rank_and_pivots(extended_augmented_rows, PRIME)

    if zero_rank != 143 or modular_zero_rank != 143:
        raise AssertionError("unexpected exact zero-face rank")
    if len(independent_row_indices) != 143:
        raise AssertionError("unexpected independent row-basis size")
    if len(dependency_basis) != 18:
        raise AssertionError("unexpected dependency nullity")
    if combined_rank != 145 or modular_combined_rank != 145:
        raise AssertionError("unexpected exact affine coefficient rank")
    if augmented_rank != combined_rank:
        raise AssertionError("exact affine system is inconsistent")
    if extended_rank != 146 or modular_extended_rank != 146:
        raise AssertionError("unexpected torsion-extended affine rank")
    if extended_augmented_rank != extended_rank:
        raise AssertionError("torsion-extended affine system is inconsistent")

    return {
        "format": "wave135-z4-exact-face-rank-v1",
        "claim_label": "DERIVED",
        "scope": (
            "Exact rational affine-face rank for the corrected Wave134 "
            "symmetrized Z4 enumerator."
        ),
        "dimensions": {
            "primal_orbit_variables": len(sources),
            "zero_dual_rows": len(zero_rows),
            "zero_face_rank_Q": zero_rank,
            "zero_face_nullity_Q": len(sources) - zero_rank,
            "affine_rows_with_normalization_and_A0": len(combined_rows),
            "affine_rank_before_torsion_shell_Q": combined_rank,
            "affine_dimension_before_torsion_shell_Q": (
                len(sources) - combined_rank
            ),
            "affine_rows_with_torsion_shell": len(extended_rows),
            "affine_coefficient_rank_Q": extended_rank,
            "affine_dimension_Q": len(sources) - extended_rank,
        },
        "affine_consistency": {
            "classification": "CONSISTENT",
            "reason": (
                "The exact coefficient and augmented matrices both have "
                "rank 146 after adding the torsion-shell equality, so "
                "the prescribed right-hand side is consistent."
            ),
        },
        "torsion_shell_equality": {
            "equation": (
                "sum of primal orbit coefficients with odd-symbol "
                "count b=0 equals 2^54"
            ),
            "independent_of_prior_affine_rows": True,
            "rank_increment": 1,
        },
        "flint_rref": {
            "zero_pivot_columns": zero_pivots,
            "combined_pivot_columns": combined_pivots,
            "torsion_extended_pivot_columns": extended_pivots,
        },
        "forbidden_row_basis": {
            "selection_method": (
                "Greedy row elimination modulo the certificate prime; "
                "because its size equals the exact Q-rank, these original "
                "rows form an exact Q-basis."
            ),
            "independent_row_indices": independent_row_indices,
            "independent_targets": [
                list(targets[index]) for index in independent_row_indices
            ],
        },
        "forbidden_row_dependencies": {
            "dimension": len(dependency_basis),
            "basis": [
                {
                    "support": [
                        {
                            "row_index": index,
                            "target": list(targets[index]),
                            "coefficient": str(value),
                        }
                        for index, value in enumerate(relation)
                        if value
                    ]
                }
                for relation in dependency_basis
            ],
            "verification": (
                "Each displayed primitive integer coefficient vector "
                "multiplies the 161 by 1119 forbidden character matrix "
                "to the zero row exactly."
            ),
        },
        "modular_minor_certificate": {
            "prime": PRIME,
            "zero_rank_mod_prime": modular_zero_rank,
            "zero_pivot_columns": modular_zero_pivots,
            "combined_rank_mod_prime": modular_combined_rank,
            "combined_pivot_columns": modular_combined_pivots,
            "augmented_rank_mod_prime": modular_augmented_rank,
            "augmented_pivot_columns": modular_augmented_pivots,
            "torsion_extended_rank_mod_prime": modular_extended_rank,
            "torsion_extended_pivot_columns": modular_extended_pivots,
            "torsion_extended_augmented_rank_mod_prime": (
                modular_extended_augmented_rank
            ),
            "torsion_extended_augmented_pivot_columns": (
                modular_extended_augmented_pivots
            ),
            "logic": (
                "Full row rank modulo a prime exhibits a nonzero maximal "
                "minor modulo that prime, hence the same integer minor is "
                "nonzero over Q."
            ),
        },
        "memory": {
            "free_percent_before": before,
            "free_percent_after": free_memory_percent(),
        },
        "limitations": [
            "Affine consistency ignores coefficient nonnegativity.",
            "Rational and integral enumerator feasibility remain UNKNOWN.",
            "No code, adjacency matrix, or graph is constructed.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = compute()
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "rank/nullity:",
        result["dimensions"]["zero_face_rank_Q"],
        result["dimensions"]["zero_face_nullity_Q"],
    )
    print(
        "affine rank/dimension:",
        result["dimensions"]["affine_coefficient_rank_Q"],
        result["dimensions"]["affine_dimension_Q"],
    )


if __name__ == "__main__":
    main()
