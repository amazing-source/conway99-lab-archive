#!/usr/bin/env python3
"""Clean-room exact verifier for the Wave 33 rooted extension synopsis.

This module does not import or execute discovery code.  It reconstructs:

* the canonical 14-vertex Fano-complement support and its 14x70
  support-to-outside incidence D;
* the forced 14+70+15 equitable quotient;
* the simple 2-(15,3,2) O-Q incidence design;
* all six block equations equivalent to A^2=12I-A+2J;
* the conditional exact spectrum of the induced 70-vertex graph H; and
* necessity and sufficiency of an explicit finite binary (D,B,H) criterion.

No solution of that criterion is claimed or searched for here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "independent-results.json"

FROZEN_INPUTS = {
    "verification/wave33-continuation-protocol.md":
        "b98b6bb8228b54b67cd949ee1bf6eb05ebd6ebe74f1cbc9e49b041a55e2d2fe6",
    "agents/2026-07-24-wave32-rooted-proof.md":
        "04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0",
    "verification/wave32-rooted-vector/audit.md":
        "36d83232d82e30205e0aefa30aedff0a517de1edb0adbaa54575ea68d04ce1a5",
    "verification/wave32-rooted-vector/independent-results.json":
        "4ed239e997e4485abdab4e26a2e28e2a981b6fff069c4d926ccff3d2241dbe6f",
}

S_SIZE = 14
O_SIZE = 70
Q_SIZE = 15
TOTAL_SIZE = 99
DEGREE = 14
LAMBDA = 1
MU = 2


Matrix = list[list[int]]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_inputs() -> dict[str, str]:
    actual: dict[str, str] = {}
    for relative, expected in FROZEN_INPUTS.items():
        digest = sha256_file(REPO_ROOT / relative)
        if digest != expected:
            raise AssertionError(
                f"frozen input changed: {relative}: {digest} != {expected}"
            )
        actual[relative] = digest
    return actual


def zeros(rows: int, columns: int) -> Matrix:
    return [[0 for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zeros(size, size)
    for index in range(size):
        result[index][index] = 1
    return result


def ones(rows: int, columns: int) -> Matrix:
    return [[1 for _ in range(columns)] for _ in range(rows)]


def transpose(matrix: Sequence[Sequence[int]]) -> Matrix:
    if not matrix:
        return []
    return [
        [matrix[i][j] for i in range(len(matrix))]
        for j in range(len(matrix[0]))
    ]


def matmul(
    left: Sequence[Sequence[int]],
    right: Sequence[Sequence[int]],
) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise AssertionError("matrix multiplication shape mismatch")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matrix_add(*matrices: Sequence[Sequence[int]]) -> Matrix:
    if not matrices:
        raise AssertionError("no matrices supplied")
    rows = len(matrices[0])
    columns = len(matrices[0][0])
    if any(len(matrix) != rows or any(len(row) != columns for row in matrix)
           for matrix in matrices):
        raise AssertionError("matrix addition shape mismatch")
    return [
        [sum(matrix[i][j] for matrix in matrices) for j in range(columns)]
        for i in range(rows)
    ]


def matrix_scale(matrix: Sequence[Sequence[int]], scalar: int) -> Matrix:
    return [[scalar * value for value in row] for row in matrix]


def matrix_subtract(
    left: Sequence[Sequence[int]],
    right: Sequence[Sequence[int]],
) -> Matrix:
    return matrix_add(left, matrix_scale(right, -1))


def row_sums(matrix: Sequence[Sequence[int]]) -> list[int]:
    return [sum(row) for row in matrix]


def column_sums(matrix: Sequence[Sequence[int]]) -> list[int]:
    return row_sums(transpose(matrix))


def is_zero_matrix(matrix: Sequence[Sequence[int]]) -> bool:
    return all(value == 0 for row in matrix for value in row)


def trace(matrix: Sequence[Sequence[int]]) -> int:
    if any(len(row) != len(matrix) for row in matrix):
        raise AssertionError("trace requires a square matrix")
    return sum(matrix[i][i] for i in range(len(matrix)))


def fraction_rank(matrix: Sequence[Sequence[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if work else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows)
             if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                work[row][j] - factor * work[pivot_row][j]
                for j in range(columns)
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def canonical_fano_lines() -> list[tuple[int, int, int]]:
    """Lines of PG(2,2), with points represented by nonzero F2^3 vectors."""

    lines = {
        tuple(sorted((left, right, left ^ right)))
        for left in range(1, 8)
        for right in range(left + 1, 8)
        if left ^ right not in (left, right)
    }
    ordered = sorted(lines)
    if len(ordered) != 7 or any(len(line) != 3 for line in ordered):
        raise AssertionError("Fano line construction failed")
    pair_counts = {
        pair: sum(set(pair).issubset(line) for line in ordered)
        for pair in combinations(range(1, 8), 2)
    }
    if set(pair_counts.values()) != {1}:
        raise AssertionError("Fano pair incidence failed")
    return ordered


def support_matrix() -> dict[str, Any]:
    """Return the bipartite complement of Fano point-line incidence."""

    lines = canonical_fano_lines()
    cross = [
        [0 if point in lines[line_index] else 1 for line_index in range(7)]
        for point in range(1, 8)
    ]
    if row_sums(cross) != [4] * 7 or column_sums(cross) != [4] * 7:
        raise AssertionError("support cross matrix is not 4-regular")
    cross_gram = matmul(cross, transpose(cross))
    expected_cross_gram = matrix_add(
        matrix_scale(identity(7), 2),
        matrix_scale(ones(7, 7), 2),
    )
    if cross_gram != expected_cross_gram:
        raise AssertionError("Fano-complement design identity failed")

    support = zeros(14, 14)
    for point in range(7):
        for line in range(7):
            support[point][7 + line] = cross[point][line]
            support[7 + line][point] = cross[point][line]
    if row_sums(support) != [4] * 14:
        raise AssertionError("support graph is not 4-regular")
    if support != transpose(support) or any(support[i][i] for i in range(14)):
        raise AssertionError("support graph is not simple")

    # Exact annihilating polynomial records eigenvalues
    # 4,-4,+sqrt(2),-sqrt(2).
    support_squared = matmul(support, support)
    polynomial = matmul(
        matrix_subtract(support_squared, matrix_scale(identity(14), 2)),
        matrix_subtract(support_squared, matrix_scale(identity(14), 16)),
    )
    if not is_zero_matrix(polynomial):
        raise AssertionError("support spectrum polynomial failed")
    if trace(support) != 0 or trace(support_squared) != 14 * 4:
        raise AssertionError("support spectral moments failed")

    return {
        "fano_lines": [list(line) for line in lines],
        "cross_matrix": cross,
        "support_adjacency": support,
        "cross_identity": "C*C^T=2I+2J",
        "support_spectrum": {
            "4": 1,
            "-4": 1,
            "+sqrt(2)": 6,
            "-sqrt(2)": 6,
        },
        "uses_catalog": False,
        "uses_automorphism": False,
    }


def canonical_support_outside_incidence(
    support: Sequence[Sequence[int]],
) -> dict[str, Any]:
    """Build D from one copy per support edge and two per cross nonedge."""

    columns: list[list[int]] = []
    metadata: list[dict[str, Any]] = []
    for point in range(7):
        for line in range(7):
            left = point
            right = 7 + line
            copies = 1 if support[left][right] else 2
            kind = "support_edge_completion" if copies == 1 else \
                "support_cross_nonedge_completion"
            for copy in range(copies):
                column = [0] * 14
                column[left] = 1
                column[right] = 1
                columns.append(column)
                metadata.append({
                    "point_index": point,
                    "line_index": line,
                    "copy": copy,
                    "kind": kind,
                })
    if len(columns) != 70:
        raise AssertionError("D does not have 70 columns")
    d_matrix = transpose(columns)
    if row_sums(d_matrix) != [10] * 14:
        raise AssertionError("D row degrees are not ten")
    if column_sums(d_matrix) != [2] * 70:
        raise AssertionError("D column degrees are not two")

    d_gram = matmul(d_matrix, transpose(d_matrix))
    support_squared = matmul(support, support)
    expected = matrix_add(
        matrix_scale(identity(14), 12),
        matrix_scale(support, -1),
        matrix_scale(ones(14, 14), 2),
        matrix_scale(support_squared, -1),
    )
    if d_gram != expected:
        raise AssertionError("S-S block identity failed")

    signed_support = [1] * 7 + [-1] * 7
    if [
        sum(d_matrix[i][column] * signed_support[i] for i in range(14))
        for column in range(70)
    ] != [0] * 70:
        raise AssertionError("D^T does not kill the signed support vector")
    if fraction_rank(d_matrix) != 13:
        raise AssertionError("rank(D) is not 13")

    type_counts = {
        kind: sum(item["kind"] == kind for item in metadata)
        for kind in (
            "support_edge_completion",
            "support_cross_nonedge_completion",
        )
    }
    if type_counts != {
        "support_edge_completion": 28,
        "support_cross_nonedge_completion": 42,
    }:
        raise AssertionError("D completion-type census failed")

    return {
        "D": d_matrix,
        "column_metadata": metadata,
        "shape": [14, 70],
        "row_sums": row_sums(d_matrix),
        "column_sums": column_sums(d_matrix),
        "type_counts": type_counts,
        "rank": fraction_rank(d_matrix),
        "kernel_of_D_transpose": "span((+1)^7,(-1)^7)",
        "SS_block_identity": "F^2+D*D^T=12I-F+2J",
    }


def quotient_derivation() -> dict[str, Any]:
    """Derive all quotient entries without assuming equitability."""

    # For o in O: it is adjacent to two S vertices and nonadjacent to twelve.
    s_o_common_total = 2 * LAMBDA + 12 * MU
    contribution_from_s_neighbours = 2 * 4
    o_to_o = (
        s_o_common_total - contribution_from_s_neighbours
    ) // 2
    if contribution_from_s_neighbours + 2 * o_to_o != s_o_common_total:
        raise AssertionError("O common-neighbour double count is not integral")
    o_to_q = DEGREE - 2 - o_to_o

    # For q in Q: all fourteen S vertices are nonneighbors.  Every O
    # neighbour contributes its two support neighbours; a Q neighbour
    # contributes none.
    s_q_common_total = S_SIZE * MU
    q_to_o = s_q_common_total // 2
    if 2 * q_to_o != s_q_common_total:
        raise AssertionError("Q common-neighbour double count is not integral")
    q_to_q = DEGREE - q_to_o

    quotient = [
        [4, 10, 0],
        [2, o_to_o, o_to_q],
        [0, q_to_o, q_to_q],
    ]
    expected = [[4, 10, 0], [2, 9, 3], [0, 14, 0]]
    if quotient != expected:
        raise AssertionError("quotient derivation changed")
    if any(sum(row) != DEGREE for row in quotient):
        raise AssertionError("quotient row sum is not fourteen")
    balance = [
        S_SIZE * quotient[0][1] == O_SIZE * quotient[1][0],
        O_SIZE * quotient[1][2] == Q_SIZE * quotient[2][1],
        S_SIZE * quotient[0][2] == Q_SIZE * quotient[2][0],
    ]
    if not all(balance):
        raise AssertionError("equitable quotient balance failed")

    eigenvectors = {
        "14": [1, 1, 1],
        "3": [-30, 3, 14],
        "-4": [-5, 4, -14],
    }
    for eigenvalue_text, vector in eigenvectors.items():
        eigenvalue = int(eigenvalue_text)
        image = [
            sum(quotient[i][j] * vector[j] for j in range(3))
            for i in range(3)
        ]
        if image != [eigenvalue * value for value in vector]:
            raise AssertionError("quotient eigensystem failed")

    return {
        "cell_order": ["S", "O", "Q"],
        "cell_sizes": [S_SIZE, O_SIZE, Q_SIZE],
        "common_neighbour_double_counts": {
            "for_o_in_O": {
                "sum_over_s_in_S": s_o_common_total,
                "contribution_from_two_S_neighbours": 8,
                "two_per_O_neighbour": True,
                "derived_O_neighbours": o_to_o,
                "derived_Q_neighbours": o_to_q,
            },
            "for_q_in_Q": {
                "sum_over_s_in_S": s_q_common_total,
                "two_per_O_neighbour": True,
                "derived_O_neighbours": q_to_o,
                "derived_Q_neighbours": q_to_q,
            },
        },
        "quotient": quotient,
        "quotient_spectrum": {"14": 1, "3": 1, "-4": 1},
        "Q_independent": True,
        "equitability_assumed": False,
    }


def design_derivation() -> dict[str, Any]:
    """Derive the O-Q incidence parameters and simplicity."""

    row_weight = 3
    column_weight = 14
    pair_intersection = MU
    block_count = O_SIZE
    point_count = Q_SIZE
    pair_count_from_blocks = block_count * (row_weight * (row_weight - 1) // 2)
    pair_count_from_lambda = (
        pair_intersection * point_count * (point_count - 1) // 2
    )
    if pair_count_from_blocks != pair_count_from_lambda:
        raise AssertionError("2-design pair count failed")
    if block_count * row_weight != point_count * column_weight:
        raise AssertionError("2-design incidence count failed")

    return {
        "B_shape": [70, 15],
        "B_row_weight": row_weight,
        "B_column_weight": column_weight,
        "B_transpose_B": "12I_15+2J_15",
        "design": "simple 2-(15,3,2)",
        "block_count": block_count,
        "replication_number": column_weight,
        "pair_lambda": pair_intersection,
        "simplicity_argument": (
            "Duplicate B rows would give two distinct O vertices at least "
            "three common Q neighbours, exceeding both lambda=1 and mu=2."
        ),
        "simplicity_uses_automorphism": False,
    }


def rhs_srg(adjacency: Sequence[Sequence[int]]) -> Matrix:
    size = len(adjacency)
    return matrix_add(
        matrix_scale(identity(size), 12),
        matrix_scale(adjacency, -1),
        matrix_scale(ones(size, size), 2),
    )


def assemble_adjacency(
    support: Sequence[Sequence[int]],
    d_matrix: Sequence[Sequence[int]],
    b_matrix: Sequence[Sequence[int]],
    h_matrix: Sequence[Sequence[int]],
) -> Matrix:
    if len(support) != 14 or len(support[0]) != 14:
        raise AssertionError("F shape mismatch")
    if len(d_matrix) != 14 or len(d_matrix[0]) != 70:
        raise AssertionError("D shape mismatch")
    if len(b_matrix) != 70 or len(b_matrix[0]) != 15:
        raise AssertionError("B shape mismatch")
    if len(h_matrix) != 70 or len(h_matrix[0]) != 70:
        raise AssertionError("H shape mismatch")
    result = zeros(99, 99)
    for i in range(14):
        for j in range(14):
            result[i][j] = support[i][j]
    for i in range(14):
        for j in range(70):
            result[i][14 + j] = d_matrix[i][j]
            result[14 + j][i] = d_matrix[i][j]
    for i in range(70):
        for j in range(70):
            result[14 + i][14 + j] = h_matrix[i][j]
    for i in range(70):
        for j in range(15):
            result[14 + i][84 + j] = b_matrix[i][j]
            result[84 + j][14 + i] = b_matrix[i][j]
    return result


def block_residuals(
    support: Sequence[Sequence[int]],
    d_matrix: Sequence[Sequence[int]],
    b_matrix: Sequence[Sequence[int]],
    h_matrix: Sequence[Sequence[int]],
) -> dict[str, Matrix]:
    f_squared = matmul(support, support)
    dd_t = matmul(d_matrix, transpose(d_matrix))
    fd = matmul(support, d_matrix)
    dh = matmul(d_matrix, h_matrix)
    db = matmul(d_matrix, b_matrix)
    d_t_d = matmul(transpose(d_matrix), d_matrix)
    h_squared = matmul(h_matrix, h_matrix)
    bb_t = matmul(b_matrix, transpose(b_matrix))
    hb = matmul(h_matrix, b_matrix)
    b_t_b = matmul(transpose(b_matrix), b_matrix)
    return {
        "SS": matrix_subtract(
            matrix_add(f_squared, dd_t),
            matrix_add(
                matrix_scale(identity(14), 12),
                matrix_scale(support, -1),
                matrix_scale(ones(14, 14), 2),
            ),
        ),
        "SO": matrix_subtract(
            matrix_add(fd, dh),
            matrix_add(
                matrix_scale(ones(14, 70), 2),
                matrix_scale(d_matrix, -1),
            ),
        ),
        "SQ": matrix_subtract(db, matrix_scale(ones(14, 15), 2)),
        "OO": matrix_subtract(
            matrix_add(d_t_d, h_squared, bb_t),
            matrix_add(
                matrix_scale(identity(70), 12),
                matrix_scale(h_matrix, -1),
                matrix_scale(ones(70, 70), 2),
            ),
        ),
        "OQ": matrix_subtract(
            hb,
            matrix_add(
                matrix_scale(ones(70, 15), 2),
                matrix_scale(b_matrix, -1),
            ),
        ),
        "QQ": matrix_subtract(
            b_t_b,
            matrix_add(
                matrix_scale(identity(15), 12),
                matrix_scale(ones(15, 15), 2),
            ),
        ),
    }


def extract_block(
    matrix: Sequence[Sequence[int]],
    row_start: int,
    row_end: int,
    column_start: int,
    column_end: int,
) -> Matrix:
    return [
        list(row[column_start:column_end])
        for row in matrix[row_start:row_end]
    ]


def deterministic_hostile_matrices() -> tuple[Matrix, Matrix]:
    """Arbitrary binary matrices used only to test block/full equivalence."""

    b_matrix = [
        [1 if (7 * row + 3 * column + row * column) % 19 < 4 else 0
         for column in range(15)]
        for row in range(70)
    ]
    h_matrix = zeros(70, 70)
    for left in range(70):
        for right in range(left + 1, 70):
            value = 1 if (
                (left * left + 3 * right + left * right + 5) % 23 < 5
            ) else 0
            h_matrix[left][right] = value
            h_matrix[right][left] = value
    return b_matrix, h_matrix


def is_binary_matrix(matrix: Sequence[Sequence[int]]) -> bool:
    return all(value in (0, 1) for row in matrix for value in row)


def evaluate_binary_criterion(
    support: Sequence[Sequence[int]],
    d_matrix: Sequence[Sequence[int]],
    b_matrix: Sequence[Sequence[int]],
    h_matrix: Sequence[Sequence[int]],
) -> dict[str, Any]:
    """Fail-closed audit of a proposed finite binary criterion witness."""

    shape_b = (
        len(b_matrix) == 70
        and all(len(row) == 15 for row in b_matrix)
    )
    shape_h = (
        len(h_matrix) == 70
        and all(len(row) == 70 for row in h_matrix)
    )
    gates: dict[str, bool] = {
        "B_shape": shape_b,
        "H_shape": shape_h,
    }
    if not shape_b or not shape_h:
        return {
            "gates": gates,
            "block_residual_nonzero_entries": {},
            "passes": False,
        }

    gates.update({
        "B_binary": is_binary_matrix(b_matrix),
        "B_row_sums_3": row_sums(b_matrix) == [3] * 70,
        "B_column_sums_14": column_sums(b_matrix) == [14] * 15,
        "B_rows_distinct": len({tuple(row) for row in b_matrix}) == 70,
        "H_binary": is_binary_matrix(h_matrix),
        "H_symmetric": list(map(list, h_matrix)) == transpose(h_matrix),
        "H_zero_diagonal": all(h_matrix[i][i] == 0 for i in range(70)),
        "H_row_sums_9": row_sums(h_matrix) == [9] * 70,
    })
    residuals = block_residuals(support, d_matrix, b_matrix, h_matrix)
    residual_counts = {
        name: sum(value != 0 for row in residual for value in row)
        for name, residual in residuals.items()
    }
    gates.update({
        f"{name}_equation": count == 0
        for name, count in residual_counts.items()
    })
    return {
        "gates": gates,
        "block_residual_nonzero_entries": residual_counts,
        "passes": all(gates.values()),
    }


def criterion_derivation(
    support: Sequence[Sequence[int]],
    d_matrix: Sequence[Sequence[int]],
) -> dict[str, Any]:
    """Audit exact equivalence between six block equations and the SRG identity."""

    b_hostile, h_hostile = deterministic_hostile_matrices()
    adjacency = assemble_adjacency(support, d_matrix, b_hostile, h_hostile)
    full_residual = matrix_subtract(matmul(adjacency, adjacency), rhs_srg(adjacency))
    residuals = block_residuals(support, d_matrix, b_hostile, h_hostile)
    block_ranges = {
        "SS": (0, 14, 0, 14),
        "SO": (0, 14, 14, 84),
        "SQ": (0, 14, 84, 99),
        "OO": (14, 84, 14, 84),
        "OQ": (14, 84, 84, 99),
        "QQ": (84, 99, 84, 99),
    }
    for name, bounds in block_ranges.items():
        if extract_block(full_residual, *bounds) != residuals[name]:
            raise AssertionError(f"{name} residual is not the full SRG block")

    # The frozen F,D already satisfy SS exactly.
    if not is_zero_matrix(residuals["SS"]):
        raise AssertionError("canonical F,D fail the SS block")
    if all(is_zero_matrix(value) for value in residuals.values()):
        raise AssertionError("hostile matrices accidentally solve the criterion")
    hostile_evaluation = evaluate_binary_criterion(
        support, d_matrix, b_hostile, h_hostile
    )
    if hostile_evaluation["passes"]:
        raise AssertionError("hostile matrices passed the finite criterion")

    return {
        "fixed_data": {
            "F": "canonical 14-vertex bipartite Fano-incidence complement",
            "D": (
                "canonical 14x70 binary incidence: one column per support "
                "edge and two per support cross-nonedge"
            ),
            "S_Q_block": "zero",
            "Q_Q_block": "zero",
        },
        "unknown_binary_data": {
            "B": {
                "shape": [70, 15],
                "entries": "0 or 1",
                "row_sums": 3,
                "column_sums": 14,
                "rows_distinct": True,
            },
            "H": {
                "shape": [70, 70],
                "entries": "0 or 1",
                "symmetric": True,
                "diagonal": 0,
                "row_sums": 9,
            },
        },
        "block_equations": {
            "SS": "F^2+D*D^T=12I_14-F+2J_14",
            "SO": "F*D+D*H=2J_(14x70)-D",
            "SQ": "D*B=2J_(14x15)",
            "OO": "D^T*D+H^2+B*B^T=12I_70-H+2J_70",
            "OQ": "H*B=2J_(70x15)-B",
            "QQ": "B^T*B=12I_15+2J_15",
        },
        "necessity": (
            "Each equation is the corresponding block of "
            "A^2=12I-A+2J for a target extension."
        ),
        "sufficiency": (
            "Conversely, binary B and symmetric zero-diagonal binary H "
            "with the displayed degree conditions and all six equations "
            "assemble with F,D and zero S-Q,Q-Q blocks into a simple "
            "99-vertex adjacency matrix satisfying A^2=12I-A+2J."
        ),
        "degree_recovery": (
            "The diagonal of the assembled identity gives degree 14; the "
            "off-diagonal entries give lambda=1 on edges and mu=2 on nonedges."
        ),
        "direct_full_block_reconstruction_test": "PASS",
        "hostile_B_H_evaluation": hostile_evaluation,
        "finite_search_space": (
            "All variables are the finitely many binary entries of B and H; "
            "no automorphism restriction is imposed."
        ),
    }


def h_spectrum_derivation(
    support: Sequence[Sequence[int]],
    d_matrix: Sequence[Sequence[int]],
) -> dict[str, Any]:
    """Derive the spectrum forced on H by the criterion."""

    d_rank = fraction_rank(d_matrix)
    if d_rank != 13:
        raise AssertionError("D rank changed")
    centered_d_dimension = d_rank - 1
    b_rank = 15  # From B^T B=12I+2J, which is positive definite.
    centered_b_dimension = b_rank - 1
    residual_dimension = 70 - 1 - centered_d_dimension - centered_b_dimension
    if residual_dimension != 43:
        raise AssertionError("residual H-space dimension changed")

    # Known H eigenvalues on 27 dimensions:
    # 1_O: 9
    # im(B|1^perp): -1, dimension 14
    # im(D^T) from F eigen +/-sqrt(2):
    #   -(1+sqrt(2)), -(1-sqrt(2)), each dimension 6.
    known_trace = 9 - 14 - 6 - 6
    if known_trace != -17:
        raise AssertionError("known H trace changed")
    residual_trace = -known_trace  # diag(H)=0.
    m3_numerator = residual_trace + 4 * residual_dimension
    if m3_numerator % 7:
        raise AssertionError("residual multiplicities are not integral")
    multiplicity_3 = m3_numerator // 7
    multiplicity_minus4 = residual_dimension - multiplicity_3
    if (multiplicity_3, multiplicity_minus4) != (27, 16):
        raise AssertionError("residual H multiplicities changed")

    trace_squared = (
        9 ** 2
        + 14 * (-1) ** 2
        + 6 * 6  # Sum of squares of -1 +/- sqrt(2), times multiplicity 6.
        + multiplicity_3 * 3 ** 2
        + multiplicity_minus4 * (-4) ** 2
    )
    if trace_squared != 70 * 9:
        raise AssertionError("H trace-square disagrees with 9-regularity")
    trace_cubed = (
        9 ** 3
        + 14 * (-1) ** 3
        + 6 * (-14)  # Sum of cubes of -1 +/- sqrt(2).
        + multiplicity_3 * 3 ** 3
        + multiplicity_minus4 * (-4) ** 3
    )
    if trace_cubed != 336 or trace_cubed % 6:
        raise AssertionError("H triangle trace changed")

    return {
        "orthogonal_invariant_subspaces": [
            {
                "space": "span(1_O)",
                "dimension": 1,
                "H_eigenvalue": "9",
            },
            {
                "space": "B(1_Q^perp)",
                "dimension": centered_b_dimension,
                "H_eigenvalue": "-1",
                "source_equation": "H*B=2J-B",
            },
            {
                "space": "D^T(F-eigenspace +sqrt(2))",
                "dimension": 6,
                "H_eigenvalue": "-1-sqrt(2)",
            },
            {
                "space": "D^T(F-eigenspace -sqrt(2))",
                "dimension": 6,
                "H_eigenvalue": "-1+sqrt(2)",
            },
            {
                "space": "ker(D) intersect ker(B^T) intersect 1_O^perp",
                "dimension": residual_dimension,
                "H_polynomial": "x^2+x-12=(x-3)(x+4)",
            },
        ],
        "orthogonality_bridge": (
            "D*B=2J makes D^T(1_S^perp) orthogonal to B(1_Q^perp)."
        ),
        "rank_D": d_rank,
        "rank_B": b_rank,
        "spectrum": [
            {"eigenvalue": "9", "multiplicity": 1},
            {"eigenvalue": "-1", "multiplicity": 14},
            {"eigenvalue": "-1+sqrt(2)", "multiplicity": 6},
            {"eigenvalue": "-1-sqrt(2)", "multiplicity": 6},
            {"eigenvalue": "3", "multiplicity": multiplicity_3},
            {"eigenvalue": "-4", "multiplicity": multiplicity_minus4},
        ],
        "characteristic_polynomial_factorization": (
            "(x-9)(x+1)^14((x+1)^2-2)^6(x-3)^27(x+4)^16"
        ),
        "trace": 0,
        "trace_H_squared": trace_squared,
        "edge_count": trace_squared // 2,
        "trace_H_cubed": trace_cubed,
        "triangle_count": trace_cubed // 6,
    }


def hostile_premise_checks() -> dict[str, Any]:
    return {
        "drop_Q_independence": (
            "Then the Q-Q block is B^T B+K^2=12I-K+2J, not the displayed "
            "2-design identity; the synopsis criterion no longer follows."
        ),
        "drop_binary_B": (
            "The matrix equations alone would describe weighted incidence, "
            "not a simple graph or a block design."
        ),
        "drop_H_symmetry_or_zero_diagonal": (
            "The assembled matrix would not be a simple undirected adjacency "
            "matrix; the trace argument fixing residual multiplicities fails."
        ),
        "keep_only_quotient_and_design": (
            "These do not imply the SO, OO, or OQ common-neighbour equations "
            "and are not sufficient for an SRG extension."
        ),
        "duplicate_B_rows": (
            "Two O vertices would have at least three common Q neighbours, "
            "contradicting both possible SRG pair counts."
        ),
        "assume_support_automorphism_extends": (
            "Forbidden and unnecessary. Canonical F,D are chosen only after "
            "relabeling the forced support and its 70 completion vertices; "
            "B,H remain unrestricted binary variables."
        ),
    }


def build_result() -> dict[str, Any]:
    inputs = validate_inputs()
    support = support_matrix()
    d_data = canonical_support_outside_incidence(
        support["support_adjacency"]
    )
    quotient = quotient_derivation()
    design = design_derivation()
    criterion = criterion_derivation(
        support["support_adjacency"], d_data["D"]
    )
    spectrum = h_spectrum_derivation(
        support["support_adjacency"], d_data["D"]
    )
    return {
        "scope": (
            "Precomparison clean-room verification of the frozen Wave 33 "
            "rooted structural synopsis; no candidate inspection and no "
            "finite criterion solution or target extension."
        ),
        "inputs": inputs,
        "comparison_status": "NOT_RELEASED",
        "support": support,
        "support_outside_incidence": d_data,
        "quotient": quotient,
        "O_Q_design": design,
        "finite_binary_criterion": criterion,
        "H_spectrum": spectrum,
        "hostile_premise_checks": hostile_premise_checks(),
        "status": {
            "cell_sizes_and_quotient": "DERIVED",
            "Q_independent": "DERIVED",
            "simple_2_15_3_2_design": "DERIVED",
            "block_criterion_necessity": "DERIVED",
            "block_criterion_sufficiency": "DERIVED",
            "conditional_H_spectrum": "DERIVED",
            "criterion_has_binary_solution": "UNKNOWN",
            "rooted_endpoint_extension_or_exclusion": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "uses_automorphism_restriction": False,
        "imports_or_executes_candidate_code": False,
    }


def render(value: Any) -> str:
    return json.dumps(
        value, indent=2, sort_keys=True, ensure_ascii=True
    ) + "\n"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(value), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--stdout", action="store_true")
    arguments = parser.parse_args()
    result = build_result()
    if arguments.stdout:
        print(render(result), end="")
    else:
        write_json(arguments.output, result)
        print(json.dumps({
            "output": str(arguments.output),
            "sha256": hashlib.sha256(
                render(result).encode("utf-8")
            ).hexdigest(),
            "status": result["status"],
        }, sort_keys=True))


if __name__ == "__main__":
    main()
