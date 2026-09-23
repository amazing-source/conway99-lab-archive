"""Exact fourth-order star-projector calculations for Wave 204.

This checker has two deliberately separated parts.

1. It reduces an adjacent pair of endpoint star projectors to a 6 by 6
   compression and proves that the alternating fourth trace detects exactly
   the Wave176 cycle type ``4+2``.
2. It constructs two abstract rank-11, 231-column, 99-star controls with the
   same pairwise projector trace Gram and different fourth-trace matrices.

The controls are not graphs or endpoint configurations.  Their failed target
premises are reported explicitly in the result.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable


FIELD = 3
ROOT = Path(__file__).resolve().parents[2]
EXPECTED_INPUTS = {
    "verification/wave171-pq-centered-code/verification-report.md":
        "1f2ba5ed92ba6bb1ccc05cd753a8e359f208c3ddc7ca85766f26f8869346414f",
    "verification/wave176-star-projector-circuits/audit.md":
        "f58577409f39e98b06bfbe206221d3d278f0c473bcf5057afc381094d5e65d05",
    "agents/2026-07-29-wave191-global-star-module-proof-b.md":
        "afe7d35627ec14a9599b427bcca0751e86a3f32b71fb7baf4d91e9e2e335f75f",
    "verification/wave203-two-center-incidence-verifier/audit.md":
        "382d8553457557fe2ecbe0fd1733ecb06b01f5c60be879e65cab56c078edc3d7",
}


Matrix = list[list[int]]


def mod(value: int) -> int:
    return value % FIELD


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def identity(size: int) -> Matrix:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def diagonal(entries: Iterable[int]) -> Matrix:
    values = [mod(entry) for entry in entries]
    return [
        [values[row] if row == column else 0 for column in range(len(values))]
        for row in range(len(values))
    ]


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [mod(left[row][column] + right[row][column]) for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def scalar_matrix(scalar: int, matrix: Matrix) -> Matrix:
    return [[mod(scalar * entry) for entry in row] for row in matrix]


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shape mismatch")
    return [
        [
            mod(
                sum(
                    left[row][inner] * right[inner][column]
                    for inner in range(len(right))
                )
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_power(matrix: Matrix, exponent: int) -> Matrix:
    result = identity(len(matrix))
    for _ in range(exponent):
        result = matrix_multiply(result, matrix)
    return result


def matrix_trace(matrix: Matrix) -> int:
    return mod(sum(matrix[index][index] for index in range(len(matrix))))


def flatten(matrix: Matrix) -> list[int]:
    return [entry for row in matrix for entry in row]


def gf3_rref(matrix: Matrix) -> tuple[Matrix, list[int]]:
    if not matrix:
        return [], []
    rows = [[mod(entry) for entry in row] for row in matrix]
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("ragged matrix")
    pivots: list[int] = []
    pivot_row = 0
    for column in range(width):
        source = next(
            (
                row
                for row in range(pivot_row, len(rows))
                if rows[row][column]
            ),
            None,
        )
        if source is None:
            continue
        rows[pivot_row], rows[source] = rows[source], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], -1, FIELD)
        rows[pivot_row] = [mod(inverse * entry) for entry in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            multiplier = rows[row][column]
            rows[row] = [
                mod(rows[row][index] - multiplier * rows[pivot_row][index])
                for index in range(width)
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return rows, pivots


def gf3_rank(matrix: Matrix) -> int:
    return len(gf3_rref(matrix)[1])


def gf3_nullspace(matrix: Matrix) -> list[list[int]]:
    reduced, pivots = gf3_rref(matrix)
    width = len(matrix[0])
    free = [column for column in range(width) if column not in pivots]
    basis: list[list[int]] = []
    for free_column in free:
        vector = [0] * width
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = mod(-reduced[row][free_column])
        basis.append(vector)
    return basis


def gf3_inverse(matrix: Matrix) -> Matrix:
    if len(matrix) != len(matrix[0]):
        raise ValueError("inverse requires a square matrix")
    size = len(matrix)
    augmented = [
        [mod(entry) for entry in matrix[row]] + identity(size)[row]
        for row in range(size)
    ]
    reduced, pivots = gf3_rref(augmented)
    if pivots[:size] != list(range(size)):
        raise ValueError("singular matrix")
    return [row[size:] for row in reduced]


def gf3_determinant(matrix: Matrix) -> int:
    if len(matrix) != len(matrix[0]):
        raise ValueError("determinant requires a square matrix")
    rows = [[mod(entry) for entry in row] for row in matrix]
    determinant = 1
    for column in range(len(rows)):
        source = next(
            (row for row in range(column, len(rows)) if rows[row][column]),
            None,
        )
        if source is None:
            return 0
        if source != column:
            rows[column], rows[source] = rows[source], rows[column]
            determinant = mod(-determinant)
        pivot = rows[column][column]
        determinant = mod(determinant * pivot)
        inverse = pow(pivot, -1, FIELD)
        for row in range(column + 1, len(rows)):
            multiplier = mod(rows[row][column] * inverse)
            rows[row] = [
                mod(rows[row][index] - multiplier * rows[column][index])
                for index in range(len(rows))
            ]
    return determinant


def polynomial_add(left: list[int], right: list[int]) -> list[int]:
    width = max(len(left), len(right))
    return [
        mod(
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        )
        for index in range(width)
    ]


def polynomial_multiply(left: list[int], right: list[int]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] = mod(
                result[left_index + right_index] + left_value * right_value
            )
    return result


def permutation_parity(permutation: tuple[int, ...]) -> int:
    return (
        sum(
            permutation[left] > permutation[right]
            for left in range(len(permutation))
            for right in range(left + 1, len(permutation))
        )
        % 2
    )


def characteristic_polynomial(matrix: Matrix) -> list[int]:
    """Return det(xI-A), with coefficients in low-to-high order."""

    size = len(matrix)
    result = [0] * (size + 1)
    for permutation in itertools.permutations(range(size)):
        term = [1]
        for row, column in enumerate(permutation):
            factor = (
                [mod(-matrix[row][column]), 1]
                if row == column
                else [mod(-matrix[row][column])]
            )
            term = polynomial_multiply(term, factor)
        if permutation_parity(permutation):
            term = [mod(-coefficient) for coefficient in term]
        result = polynomial_add(result, term)
    return result


def minimal_polynomial(matrix: Matrix) -> list[int]:
    """Return the monic minimal polynomial, low-to-high."""

    powers = [identity(len(matrix))]
    for _ in range(1, len(matrix) + 2):
        powers.append(matrix_multiply(powers[-1], matrix))
        coefficient_matrix = transpose([flatten(power) for power in powers])
        for relation in gf3_nullspace(coefficient_matrix):
            if relation[-1]:
                inverse = pow(relation[-1], -1, FIELD)
                return [mod(inverse * entry) for entry in relation]
    raise AssertionError("minimal polynomial not found")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inputs() -> dict[str, str]:
    observed = {
        relative: sha256(ROOT / relative) for relative in EXPECTED_INPUTS
    }
    if observed != EXPECTED_INPUTS:
        raise AssertionError({"expected": EXPECTED_INPUTS, "observed": observed})
    return observed


def cycle_biadjacency(parts: tuple[int, ...]) -> Matrix:
    if sum(parts) != 6 or any(part < 2 for part in parts):
        raise ValueError("parts must partition six into parts at least two")
    matrix = [[0] * 6 for _ in range(6)]
    offset = 0
    for part in parts:
        for index in range(part):
            matrix[offset + index][offset + index] = 1
            matrix[offset + index][offset + ((index + 1) % part)] = 1
        offset += part
    if [sum(row) for row in matrix] != [2] * 6:
        raise AssertionError("row degree changed")
    if [sum(row[column] for row in matrix) for column in range(6)] != [2] * 6:
        raise AssertionError("column degree changed")
    return matrix


def star_basis_gram() -> Matrix:
    return [[0 if row == column else 1 for column in range(6)] for row in range(6)]


def cross_gram(parts: tuple[int, ...]) -> Matrix:
    incidence = cycle_biadjacency(parts)
    return [
        [mod(1 + incidence[row][column]) for column in range(6)]
        for row in range(6)
    ]


def pair_compression(parts: tuple[int, ...]) -> Matrix:
    """Return P_x P_y P_x on the six-space E_x.

    In star bases avoiding the common triangle, both diagonal Gram blocks
    are G=J-I and the cross block is C=J+N.  Direct inversion gives
    G^{-1}C=2N, so the compression is N N^T.
    """

    gram = star_basis_gram()
    inverse = gf3_inverse(gram)
    cross = cross_gram(parts)
    direct = matrix_multiply(
        matrix_multiply(matrix_multiply(inverse, cross), inverse),
        transpose(cross),
    )
    incidence = cycle_biadjacency(parts)
    symbolic = matrix_multiply(incidence, transpose(incidence))
    if direct != symbolic:
        raise AssertionError("G inverse reduction failed")
    return direct


def compound_two_trace(matrix: Matrix) -> int:
    """Return trace of the second compound of a square matrix."""

    total = 0
    for left in range(len(matrix)):
        for right in range(left + 1, len(matrix)):
            total += (
                matrix[left][left] * matrix[right][right]
                - matrix[left][right] * matrix[right][left]
            )
    return mod(total)


def analyze_cycle(parts: tuple[int, ...]) -> dict[str, Any]:
    compression = pair_compression(parts)
    traces = [
        matrix_trace(matrix_power(compression, exponent))
        for exponent in range(1, 7)
    ]
    pair_trace = traces[0]
    fourth_trace = traces[1]
    exterior_trace = mod(
        pow(2, -1, FIELD) * (pair_trace * pair_trace - fourth_trace)
    )
    symmetric_trace = mod(
        pow(2, -1, FIELD) * (pair_trace * pair_trace + fourth_trace)
    )
    if compound_two_trace(compression) != exterior_trace:
        raise AssertionError("second-compound trace formula failed")
    return {
        "cycle_half_lengths": list(parts),
        "compression": compression,
        "compression_rank": gf3_rank(compression),
        "trace_powers_1_through_6": traces,
        "pair_trace": pair_trace,
        "alternating_fourth_trace": fourth_trace,
        "exterior_square_trace": exterior_trace,
        "symmetric_square_trace": symmetric_trace,
        "characteristic_polynomial_low_to_high": characteristic_polynomial(
            compression
        ),
        "minimal_polynomial_low_to_high": minimal_polynomial(compression),
    }


AMBIENT_FORM = diagonal([1] * 10 + [2])
SMALL_P = [
    [1, 0],
    [0, 1],
    [0, 0],
    [0, 0],
    [0, 0],
]
SMALL_Q1 = [
    [1, 2],
    [1, 0],
    [2, 1],
    [2, 0],
    [1, 1],
]
SMALL_Q2 = [
    [1, 1],
    [1, 1],
    [0, 1],
    [1, 2],
    [1, 2],
]
SIMPLEX_COEFFICIENT_COLUMNS = {
    "P": [
        [1, 1, 1, 0, 0, 0],
        [2, 1, 1, 0, 0, 0],
        [0, 2, 2, 1, 0, 0],
        [0, 1, 0, 2, 1, 0],
        [0, 1, 0, 2, 2, 0],
        [0, 0, 1, 2, 0, 1],
    ],
    "Q1": [
        [0, 1, 0, 0, 0, 0],
        [2, 2, 0, 0, 0, 0],
        [2, 0, 1, 0, 0, 0],
        [2, 0, 2, 1, 0, 1],
        [2, 0, 2, 2, 0, 1],
        [2, 0, 2, 0, 1, 2],
    ],
    "Q2": [
        [1, 1, 0, 0, 0, 0],
        [2, 1, 0, 0, 0, 0],
        [0, 2, 1, 0, 0, 0],
        [0, 2, 2, 1, 0, 1],
        [0, 2, 2, 2, 0, 1],
        [0, 2, 2, 0, 1, 2],
    ],
}


def coordinate_vector(index: int) -> list[int]:
    return [int(row == index) for row in range(11)]


def embedded_basis(small: Matrix, kind: str) -> Matrix:
    columns = [
        [small[row][column] if row < 5 else 0 for row in range(11)]
        for column in range(2)
    ]
    columns.extend([coordinate_vector(5), coordinate_vector(6)])
    columns.extend(
        [coordinate_vector(7), coordinate_vector(8)]
        if kind == "P"
        else [coordinate_vector(9), coordinate_vector(10)]
    )
    return transpose(columns)


def gram(basis: Matrix) -> Matrix:
    return matrix_multiply(
        matrix_multiply(transpose(basis), AMBIENT_FORM), basis
    )


def orthogonal_projector(basis: Matrix) -> Matrix:
    return matrix_multiply(
        matrix_multiply(
            matrix_multiply(basis, gf3_inverse(gram(basis))),
            transpose(basis),
        ),
        AMBIENT_FORM,
    )


def star_columns(name: str, basis: Matrix) -> Matrix:
    first_six = matrix_multiply(
        basis, transpose(SIMPLEX_COEFFICIENT_COLUMNS[name])
    )
    seventh = [
        mod(-sum(first_six[row][column] for column in range(6)))
        for row in range(11)
    ]
    return [
        first_six[row] + [seventh[row]]
        for row in range(11)
    ]


def rank_one_operator(vector: list[int]) -> Matrix:
    column = [[entry] for entry in vector]
    return matrix_multiply(
        matrix_multiply(column, transpose(column)), AMBIENT_FORM
    )


def star_frame_operator(columns: Matrix) -> Matrix:
    result = [[0] * 11 for _ in range(11)]
    for column in transpose(columns):
        result = matrix_add(result, rank_one_operator(column))
    return result


def local_control_data() -> tuple[dict[str, Any], dict[str, Matrix], dict[str, Matrix]]:
    bases = {
        "P": embedded_basis(SMALL_P, "P"),
        "Q1": embedded_basis(SMALL_Q1, "Q"),
        "Q2": embedded_basis(SMALL_Q2, "Q"),
    }
    projectors = {
        name: orthogonal_projector(basis) for name, basis in bases.items()
    }
    columns = {
        name: star_columns(name, basis) for name, basis in bases.items()
    }
    target_gram = [[0 if row == column else 1 for column in range(7)] for row in range(7)]
    for name in bases:
        projector = projectors[name]
        if matrix_multiply(projector, projector) != projector:
            raise AssertionError(f"{name} is not idempotent")
        if matrix_multiply(transpose(projector), AMBIENT_FORM) != matrix_multiply(
            AMBIENT_FORM, projector
        ):
            raise AssertionError(f"{name} is not self-adjoint")
        if gf3_rank(projector) != 6 or matrix_trace(projector) != 0:
            raise AssertionError(f"{name} rank/trace changed")
        if gf3_determinant(gram(bases[name])) != 1:
            raise AssertionError(f"{name} star-space discriminant changed")
        if gram(columns[name]) != target_gram:
            raise AssertionError(f"{name} simplex Gram changed")
        if [mod(sum(row)) for row in columns[name]] != [0] * 11:
            raise AssertionError(f"{name} simplex sum changed")
        if star_frame_operator(columns[name]) != scalar_matrix(2, projector):
            raise AssertionError(f"{name} frame/projector identity changed")
    pair_data: dict[str, Any] = {}
    for left, right in (("P", "Q1"), ("P", "Q2"), ("Q1", "Q2")):
        product = matrix_multiply(projectors[left], projectors[right])
        fourth = matrix_trace(matrix_multiply(product, product))
        intersection = (
            12 - gf3_rank([bases[left][row] + bases[right][row] for row in range(11)])
        )
        pair_data[f"{left},{right}"] = {
            "pair_trace": matrix_trace(product),
            "alternating_fourth_trace": fourth,
            "intersection_dimension": intersection,
        }
    if pair_data["P,Q1"]["pair_trace"] != pair_data["P,Q2"]["pair_trace"]:
        raise AssertionError("pair traces no longer match")
    if pair_data["P,Q1"]["intersection_dimension"] != pair_data["P,Q2"]["intersection_dimension"]:
        raise AssertionError("intersection dimensions no longer match")
    if pair_data["P,Q1"]["alternating_fourth_trace"] == pair_data["P,Q2"]["alternating_fourth_trace"]:
        raise AssertionError("fourth-trace separation disappeared")
    joined_columns = [
        bases["P"][row] + bases["Q1"][row] + bases["Q2"][row]
        for row in range(11)
    ]
    if gf3_rank(joined_columns) != 11:
        raise AssertionError("three star spaces no longer span the ambient space")
    return (
        {
            "ambient_dimension": 11,
            "ambient_form_diagonal": [1] * 10 + [2],
            "each_projector": {
                "rank": 6,
                "trace": 0,
                "self_adjoint": True,
                "idempotent": True,
                "star_space_discriminant": 1,
                "seven_singular_columns": True,
                "simplex_gram": "J_7-I_7",
                "column_sum_zero": True,
                "projector_identity": "P=-sum(z tensor z)",
            },
            "pair_data": pair_data,
            "ambient_span_rank_of_P_Q1_Q2": 11,
        },
        projectors,
        columns,
    )


def normalized_projective_direction(vector: list[int]) -> tuple[int, ...]:
    first = next((entry for entry in vector if entry), None)
    if first is None:
        raise AssertionError("zero projective vector")
    inverse = pow(first, -1, FIELD)
    return tuple(mod(inverse * entry) for entry in vector)


def global_control_summary(
    projectors: dict[str, Matrix],
    columns: dict[str, Matrix],
) -> dict[str, Any]:
    """Build the two labelwise controls and compare their moment matrices."""

    assignment_a = ["P"] * 9 + ["Q1"] * 12 + ["Q2"] * 12
    assignment_b = ["P"] * 9 + ["Q2"] * 12 + ["Q1"] * 12
    controls: dict[str, dict[str, Any]] = {}
    moment_matrices: dict[str, tuple[Matrix, Matrix]] = {}
    for label, assignment in (("A", assignment_a), ("B", assignment_b)):
        projector_rows = [
            projectors[name] for name in assignment for _ in range(3)
        ]
        column_vectors = [
            vector
            for name in assignment
            for vector in transpose(columns[name])
        ]
        column_matrix = transpose(column_vectors)
        frame = [[0] * 11 for _ in range(11)]
        for vector in column_vectors:
            frame = matrix_add(frame, rank_one_operator(vector))
        projector_sum = [[0] * 11 for _ in range(11)]
        for projector in projector_rows:
            projector_sum = matrix_add(projector_sum, projector)
        centered_gram = matrix_multiply(
            matrix_multiply(transpose(column_matrix), AMBIENT_FORM),
            column_matrix,
        )
        pair_trace = []
        fourth_trace = []
        for left in projector_rows:
            pair_row = []
            fourth_row = []
            for right in projector_rows:
                product = matrix_multiply(left, right)
                pair_row.append(matrix_trace(product))
                fourth_row.append(matrix_trace(matrix_multiply(product, product)))
            pair_trace.append(pair_row)
            fourth_trace.append(fourth_row)
        if frame != [[0] * 11 for _ in range(11)]:
            raise AssertionError(f"control {label} is not zero-tight")
        if projector_sum != [[0] * 11 for _ in range(11)]:
            raise AssertionError(f"control {label} projector sum changed")
        if gf3_rank(column_matrix) != 11 or gf3_rank(centered_gram) != 11:
            raise AssertionError(f"control {label} rank changed")
        if any(centered_gram[index][index] for index in range(231)):
            raise AssertionError(f"control {label} has nonsingular column")
        controls[label] = {
            "projector_count": len(projector_rows),
            "column_label_count": len(column_vectors),
            "star_group_counts": {
                name: assignment.count(name) for name in ("P", "Q1", "Q2")
            },
            "projectors_per_star_group": 3,
            "columns_per_star_group": 7,
            "column_incidence_degree": 3,
            "ambient_column_span_rank": gf3_rank(column_matrix),
            "centered_gram_rank": gf3_rank(centered_gram),
            "centered_gram_square_zero_via_zero_frame": True,
            "all_columns_singular": True,
            "projector_sum_zero": True,
            "distinct_projective_direction_count": len(
                {normalized_projective_direction(vector) for vector in column_vectors}
            ),
        }
        moment_matrices[label] = (pair_trace, fourth_trace)
    pair_a, fourth_a = moment_matrices["A"]
    pair_b, fourth_b = moment_matrices["B"]
    if pair_a != pair_b:
        raise AssertionError("pairwise trace Grams differ")
    different_fourth_entries = sum(
        fourth_a[row][column] != fourth_b[row][column]
        for row in range(99)
        for column in range(99)
    )
    if not different_fourth_entries:
        raise AssertionError("fourth-trace matrices did not separate")
    pair_distribution = {
        str(value): sum(entry == value for row in pair_a for entry in row)
        for value in range(FIELD)
    }
    fourth_distributions = {
        label: {
            str(value): sum(entry == value for row in matrix for entry in row)
            for value in range(FIELD)
        }
        for label, matrix in (("A", fourth_a), ("B", fourth_b))
    }
    return {
        "controls": controls,
        "same_pairwise_projector_trace_gram": True,
        "pairwise_trace_entry_distribution": pair_distribution,
        "different_fourth_trace_matrices": True,
        "different_ordered_fourth_trace_entries": different_fourth_entries,
        "fourth_trace_entry_distributions": fourth_distributions,
        "satisfied_endpoint_shaped_premises": [
            "nondegenerate ambient dimension 11 over F_3",
            "231 labelled singular columns spanning dimension 11",
            "centered Gram rank 11 and square zero",
            "99 rank-six trace-zero self-adjoint idempotent star projectors",
            "seven simplex columns per star and P=-sum(z tensor z)",
            "each column label belongs to three stars",
            "sum of all 99 projectors is zero",
        ],
        "failed_target_premises": [
            "the 231 labelled columns are not projectively distinct",
            "dual distance at least four fails because vector directions repeat",
            "the 99-by-231 incidence is not the linear point-triangle incidence of a simple graph",
            "three point rows in one group share seven blocks rather than at most one",
            "BB^T is not A+I for srg(99,14,1,2)",
            "the exact 32-regular selected orthogonality graph and block relation profiles are not imposed",
            "the controls are not graphs, codes with the endpoint distance, covers, or endpoint configurations",
        ],
    }


def analyze() -> dict[str, Any]:
    inputs = verify_inputs()
    cycles = {
        "+".join(str(part) for part in parts): analyze_cycle(parts)
        for parts in ((6,), (4, 2), (3, 3), (2, 2, 2))
    }
    local, projectors, columns = local_control_data()
    global_controls = global_control_summary(projectors, columns)
    return {
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "field": FIELD,
        "scope": (
            "conditional prism-free n3=4158 and centered rank-11 endpoint; "
            "adjacent star-pair fourth traces only"
        ),
        "inputs": inputs,
        "adjacent_pair_reduction": {
            "star_basis_gram": "G=J_6-I_6",
            "cross_gram": "C=J_6+N",
            "inverse_identity": "G^-1 C=2N",
            "compression": "A_xy=P_x P_y P_x|E_x=N N^T",
            "full_trace_identity": (
                "tr(A_xy^2)=tr((P_x P_y P_x)^2)="
                "tr(P_x P_y P_x P_y)"
            ),
            "cycle_types": cycles,
            "detector": (
                "for adjacent x,y, tr(P_x P_y P_x P_y)=1 in F_3 "
                "iff the outer cycle type is 4+2; it is 0 for 6, 3+3, "
                "and 2+2+2"
            ),
            "exterior_detector": (
                "tr((wedge^2 P_x)(wedge^2 P_y))="
                "(g_xy^2-h_xy)/2; since g_xy=0 on graph edges, this "
                "equals h_xy and is the same 4+2 detector"
            ),
        },
        "positive_controls": {
            "local": local,
            "global_99_projector_231_column": global_controls,
        },
        "conclusions": {
            "adjacent_4_plus_2_type_detected_by_fourth_trace": True,
            "pairwise_trace_determines_fourth_trace": False,
            "endpoint_excluded": False,
            "strict_n3_improvement": False,
            "conway_99_status": "UNKNOWN",
            "missing_invariant": (
                "graph-specific distribution and compatibility of the "
                "alternating fourth traces, including all nonedge pairs"
            ),
        },
    }


def verify(data: dict[str, Any]) -> None:
    types = data["adjacent_pair_reduction"]["cycle_types"]
    if {name: item["pair_trace"] for name, item in types.items()} != {
        "6": 0,
        "4+2": 0,
        "3+3": 0,
        "2+2+2": 0,
    }:
        raise AssertionError("edge pair traces changed")
    if {
        name: item["alternating_fourth_trace"] for name, item in types.items()
    } != {"6": 0, "4+2": 1, "3+3": 0, "2+2+2": 0}:
        raise AssertionError("fourth-trace detector changed")
    if {
        name: item["characteristic_polynomial_low_to_high"]
        for name, item in types.items()
    } != {
        "6": [0, 0, 0, 2, 0, 0, 1],
        "4+2": [0, 0, 1, 0, 1, 0, 1],
        "3+3": [1, 0, 0, 1, 0, 0, 1],
        "2+2+2": [0, 0, 0, 2, 0, 0, 1],
    }:
        raise AssertionError("characteristic modules changed")
    if {
        name: item["minimal_polynomial_low_to_high"]
        for name, item in types.items()
    } != {
        "6": [0, 0, 1, 1, 1],
        "4+2": [0, 2, 0, 1],
        "3+3": [1, 1, 1],
        "2+2+2": [0, 2, 1],
    }:
        raise AssertionError("minimal modules changed")
    controls = data["positive_controls"]["global_99_projector_231_column"]
    if controls["different_ordered_fourth_trace_entries"] != 3888:
        raise AssertionError("global fourth separation changed")
    if controls["pairwise_trace_entry_distribution"] != {
        "0": 3321,
        "1": 2592,
        "2": 3888,
    }:
        raise AssertionError("global pairwise distribution changed")
    if controls["fourth_trace_entry_distributions"] != {
        "A": {"0": 3321, "1": 1944, "2": 4536},
        "B": {"0": 3321, "1": 1944, "2": 4536},
    }:
        raise AssertionError("global fourth distributions changed")
    if data["conclusions"]["endpoint_excluded"]:
        raise AssertionError("status inflation")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    data = analyze()
    verify(data)
    if args.verify:
        observed = json.loads(args.verify.read_text(encoding="utf-8"))
        if observed != data:
            raise AssertionError("frozen result differs")
    if args.write:
        args.write.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if not args.write and not args.verify:
        print(json.dumps(data, indent=2, sort_keys=True))
    print("PASS: Wave204 fourth-order projector checks")


if __name__ == "__main__":
    main()
