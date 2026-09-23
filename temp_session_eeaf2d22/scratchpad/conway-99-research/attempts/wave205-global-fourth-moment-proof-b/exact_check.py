"""Exact Wave 205 proof-B calculations.

The package separates three issues:

1. the correct tensor/operator coordinate dimensions for fourth traces;
2. the exact point-star pair-feature factorization H = U K_D U^T; and
3. a scoped rank-11 projector control showing that sum(P_x)=0 does not
   imply H*1=0 or vanishing quadratic projector moment.

The control is not a graph or endpoint realization.  Its failed premises
are emitted explicitly.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


FIELD = 3
AMBIENT_DIMENSION = 11
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
    "verification/wave204-global-compatibility-verifier/package-manifest.sha256":
        "48cd018c7f7cebe7f2bc93a6dbd9440422f8dc843bc6c0fa96b29968e440f9c2",
    "verification/2026-07-29-wave204-orchestrator.md":
        "7760a4c5a4b6a501262bbb3b061828725cd23c6837fd724fada84d94a3124edd",
}


Matrix = list[list[int]]


def mod(value: int) -> int:
    return value % FIELD


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inputs() -> dict[str, str]:
    observed = {
        relative: sha256(ROOT / relative) for relative in EXPECTED_INPUTS
    }
    if observed != EXPECTED_INPUTS:
        raise AssertionError({"expected": EXPECTED_INPUTS, "observed": observed})
    return observed


def identity(size: int) -> Matrix:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def diagonal(entries: Iterable[int]) -> Matrix:
    values = [mod(value) for value in entries]
    return [
        [values[row] if row == column else 0 for column in range(len(values))]
        for row in range(len(values))
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


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


def matrix_trace(matrix: Matrix) -> int:
    return mod(sum(matrix[index][index] for index in range(len(matrix))))


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


def point_triangle_incidence(
    point_count: int, blocks: list[tuple[int, ...]]
) -> Matrix:
    incidence = [[0] * len(blocks) for _ in range(point_count)]
    for block_index, block in enumerate(blocks):
        for point in block:
            incidence[point][block_index] = 1
    return incidence


def cyclic_resolvable_control() -> tuple[list[tuple[int, int]], list[tuple[int, ...]]]:
    """A deterministic 99-point, 231-block linear 3-uniform control.

    Points are (a,i) in Z_3 x Z_33.  For seven slopes s, the blocks are
    {(0,i),(1,i+s),(2,i+2s)}.  This has the exact incidence counts needed
    to test the star-pair feature theorem but is not the target SRG.
    """

    points = [(layer, value) for layer in range(3) for value in range(33)]
    point_index = {point: index for index, point in enumerate(points)}
    blocks = []
    for slope in range(7):
        for intercept in range(33):
            blocks.append(
                tuple(
                    point_index[(layer, (intercept + layer * slope) % 33)]
                    for layer in range(3)
                )
            )
    return points, blocks


def common_neighbor_distributions(
    point_count: int, blocks: list[tuple[int, ...]]
) -> tuple[dict[int, int], dict[int, int], list[int]]:
    adjacency = [set() for _ in range(point_count)]
    for block in blocks:
        for point in block:
            adjacency[point].update(set(block) - {point})
    adjacent_counts: Counter[int] = Counter()
    nonadjacent_counts: Counter[int] = Counter()
    for left in range(point_count):
        for right in range(left + 1, point_count):
            common = len(adjacency[left] & adjacency[right])
            target = adjacent_counts if right in adjacency[left] else nonadjacent_counts
            target[common] += 1
    return dict(sorted(adjacent_counts.items())), dict(sorted(nonadjacent_counts.items())), [
        len(neighbors) for neighbors in adjacency
    ]


def star_pair_feature_summary() -> dict[str, Any]:
    points, blocks = cyclic_resolvable_control()
    incidence = point_triangle_incidence(len(points), blocks)
    point_blocks = [
        [block for block, value in enumerate(row) if value] for row in incidence
    ]
    if [len(items) for items in point_blocks] != [7] * 99:
        raise AssertionError("point degree changed")
    block_sets = [set(block) for block in blocks]
    if any(
        len(block_sets[left] & block_sets[right]) > 1
        for left in range(len(blocks))
        for right in range(left + 1, len(blocks))
    ):
        raise AssertionError("linearity failed")

    # For every point choose one ordered pair of distinct incident blocks.
    # The corresponding U-column is exactly that point's unit vector.
    witnesses = []
    for point, incident in enumerate(point_blocks):
        left, right = incident[:2]
        supporting_points = [
            candidate
            for candidate, row in enumerate(incidence)
            if row[left] and row[right]
        ]
        if supporting_points != [point]:
            raise AssertionError("star-pair witness is not a unit column")
        witnesses.append((left, right))
    witness_matrix = identity(99)

    adjacent_distribution, nonadjacent_distribution, degrees = (
        common_neighbor_distributions(99, blocks)
    )
    return {
        "points": 99,
        "triangle_blocks": 231,
        "block_size": 3,
        "blocks_per_point": 7,
        "linear_triple_system": True,
        "ordered_distinct_star_pair_coordinates": 99 * 7 * 6,
        "unordered_distinct_star_pair_coordinates": 99 * 7 * 6 // 2,
        "unit_witness_columns": len(witnesses),
        "unit_witness_matrix_rank": gf3_rank(witness_matrix),
        "star_pair_feature_rank": 99,
        "sum_feature_on_diagonal_pair": 0,
        "sum_feature_on_distinct_intersecting_pair": 1,
        "sum_feature_identity": "sum_x u_x=vec(Q), Q=B^T B over F_3",
        "control_point_degrees": distribution(degrees),
        "control_adjacent_common_neighbor_distribution": {
            str(value): count
            for value, count in adjacent_distribution.items()
        },
        "control_nonadjacent_common_neighbor_distribution": {
            str(value): count
            for value, count in nonadjacent_distribution.items()
        },
        "control_is_srg_99_14_1_2": False,
    }


def fano_blocks() -> list[tuple[int, int, int]]:
    return [
        (0, 1, 3),
        (0, 2, 5),
        (0, 4, 6),
        (1, 2, 6),
        (1, 4, 5),
        (2, 3, 4),
        (3, 5, 6),
    ]


def toy_gram() -> Matrix:
    size = 7
    return [
        [
            0
            if row == column
            else mod(row * row + row * column + column * column + row + column)
            for column in range(size)
        ]
        for row in range(size)
    ]


def direct_fourth_trace(
    star_left: list[int], star_right: list[int], gram: Matrix
) -> int:
    total = 0
    for first, third in itertools.product(star_left, repeat=2):
        for second, fourth in itertools.product(star_right, repeat=2):
            total += (
                gram[first][second]
                * gram[second][third]
                * gram[third][fourth]
                * gram[fourth][first]
            )
    return mod(total)


def ordered_pair_feature(incidence: Matrix) -> Matrix:
    block_count = len(incidence[0])
    return [
        [
            row[first] * row[second]
            for first in range(block_count)
            for second in range(block_count)
        ]
        for row in incidence
    ]


def crossing_kernel(gram: Matrix) -> Matrix:
    size = len(gram)
    pairs = [(first, second) for first in range(size) for second in range(size)]
    return [
        [
            mod(
                gram[first][middle_left]
                * gram[middle_left][second]
                * gram[second][middle_right]
                * gram[middle_right][first]
            )
            for middle_left, middle_right in pairs
        ]
        for first, second in pairs
    ]


def hadamard(left: Matrix, right: Matrix) -> Matrix:
    return [
        [mod(left[row][column] * right[row][column]) for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def toy_factorization_summary() -> dict[str, Any]:
    blocks = fano_blocks()
    incidence = point_triangle_incidence(7, blocks)
    gram = toy_gram()
    stars = [
        [index for index, value in enumerate(row) if value] for row in incidence
    ]
    direct = [
        [direct_fourth_trace(stars[left], stars[right], gram) for right in range(7)]
        for left in range(7)
    ]
    feature = ordered_pair_feature(incidence)
    kernel = crossing_kernel(gram)
    factored = matrix_multiply(matrix_multiply(feature, kernel), transpose(feature))
    if direct != factored:
        raise AssertionError("H=U K_D U^T factorization failed")

    q_matrix = matrix_multiply(transpose(incidence), incidence)
    q_vector = [entry for row in q_matrix for entry in row]
    feature_sum = [
        mod(sum(feature[point][coordinate] for point in range(7)))
        for coordinate in range(49)
    ]
    if feature_sum != q_vector:
        raise AssertionError("sum_x u_x=vec(Q) failed")
    row_sum_factored = matrix_multiply(
        feature, matrix_multiply(kernel, [[value] for value in q_vector])
    )
    row_sums = [mod(sum(row)) for row in direct]
    if [row[0] for row in row_sum_factored] != row_sums:
        raise AssertionError("factorized row sums failed")

    localizer_row_sums = []
    for point in range(7):
        selector = diagonal(incidence[point])
        moment = matrix_multiply(matrix_multiply(gram, selector), gram)
        localizer = hadamard(q_matrix, moment)
        localizer_row_sums.append(
            matrix_trace(matrix_multiply(localizer, moment))
        )
    if localizer_row_sums != row_sums:
        raise AssertionError("Hadamard localizer row-sum identity failed")

    kernel_q = [
        row[0]
        for row in matrix_multiply(kernel, [[value] for value in q_vector])
    ]
    line_norms = []
    for first in range(7):
        for second in range(7):
            hadamard_rows = [
                mod(gram[first][block] * gram[second][block])
                for block in range(7)
            ]
            line_vector = [
                mod(
                    sum(
                        incidence[point][block] * hadamard_rows[block]
                        for block in range(7)
                    )
                )
                for point in range(7)
            ]
            line_norms.append(mod(sum(value * value for value in line_vector)))
    if line_norms != kernel_q:
        raise AssertionError("line-vector norm contraction failed")
    return {
        "toy_points": 7,
        "toy_blocks": 7,
        "direct_equals_U_K_U_transpose": True,
        "sum_feature_equals_vec_Q": True,
        "row_sums": row_sums,
        "row_sum_factorization": "H*1=U K_D vec(Q)",
        "localizer_identity": (
            "(H*1)_x=tr((Q o (D S_x D))(D S_x D)), Q=B^T B"
        ),
        "line_vector_norm_identity": True,
    }


AMBIENT_FORM = diagonal([1] * 10 + [2])
BASE_SUPPORTS = [
    (1, 2, 4, 5, 6, 8),
    (1, 2, 3, 5, 6, 8),
    (1, 2, 5, 7, 8, 9),
    (0, 1, 3, 5, 6, 7),
    (0, 1, 4, 5, 7, 9),
    (0, 1, 3, 4, 5, 9),
]
SIMPLEX_COLUMNS = transpose(
    [
        [0, 0, 0, 1, 1, 1],
        [0, 0, 0, 1, 1, 2],
        [0, 0, 1, 2, 2, 0],
        [0, 1, 2, 0, 1, 0],
        [0, 2, 2, 0, 1, 0],
        [1, 0, 2, 1, 0, 0],
        [2, 0, 2, 1, 0, 0],
    ]
)


def coordinate_basis(support: tuple[int, ...]) -> Matrix:
    return [
        [int(row == coordinate) for coordinate in support]
        for row in range(AMBIENT_DIMENSION)
    ]


def orthogonal_reflection() -> Matrix:
    vector = [int(index < 4) for index in range(AMBIENT_DIMENSION)]
    rank_one = [
        [mod(vector[row] * vector[column]) for column in range(AMBIENT_DIMENSION)]
        for row in range(AMBIENT_DIMENSION)
    ]
    reflection = matrix_add(identity(AMBIENT_DIMENSION), rank_one)
    if matrix_multiply(
        matrix_multiply(transpose(reflection), AMBIENT_FORM), reflection
    ) != AMBIENT_FORM:
        raise AssertionError("reflection lost orthogonality")
    return reflection


def projector_from_orthonormal_basis(basis: Matrix) -> Matrix:
    return matrix_multiply(
        matrix_multiply(basis, transpose(basis)), AMBIENT_FORM
    )


def rank_one_operator(vector: list[int]) -> Matrix:
    column = [[value] for value in vector]
    return matrix_multiply(
        matrix_multiply(column, transpose(column)), AMBIENT_FORM
    )


def star_columns(basis: Matrix) -> Matrix:
    return matrix_multiply(basis, SIMPLEX_COLUMNS)


def gram(columns: Matrix) -> Matrix:
    return matrix_multiply(
        matrix_multiply(transpose(columns), AMBIENT_FORM), columns
    )


def flatten(matrix: Matrix) -> tuple[int, ...]:
    return tuple(entry for row in matrix for entry in row)


def pair_trace(left: Matrix, right: Matrix) -> int:
    return matrix_trace(matrix_multiply(left, right))


def fourth_trace(left: Matrix, right: Matrix) -> int:
    product = matrix_multiply(left, right)
    return matrix_trace(matrix_multiply(product, product))


def quadratic_moment_nonzero_coordinates(projectors: list[Matrix]) -> int:
    coordinates = [0] * (AMBIENT_DIMENSION ** 4)
    for projector in projectors:
        for row_left in range(AMBIENT_DIMENSION):
            for column_left in range(AMBIENT_DIMENSION):
                left = projector[row_left][column_left]
                if not left:
                    continue
                prefix = (
                    (row_left * AMBIENT_DIMENSION + column_left)
                    * AMBIENT_DIMENSION
                    * AMBIENT_DIMENSION
                )
                for row_right in range(AMBIENT_DIMENSION):
                    for column_right in range(AMBIENT_DIMENSION):
                        index = (
                            prefix
                            + row_right * AMBIENT_DIMENSION
                            + column_right
                        )
                        coordinates[index] = mod(
                            coordinates[index]
                            + left * projector[row_right][column_right]
                        )
    return sum(value != 0 for value in coordinates)


def distribution(values: Iterable[int]) -> dict[str, int]:
    return {
        str(value): count
        for value, count in sorted(Counter(values).items())
    }


def projector_control_summary() -> dict[str, Any]:
    first_bases = [coordinate_basis(support) for support in BASE_SUPPORTS]
    reflection = orthogonal_reflection()
    second_bases = [
        matrix_multiply(reflection, basis) for basis in first_bases
    ]
    bases = first_bases + second_bases
    projectors = [projector_from_orthonormal_basis(basis) for basis in bases]
    expected_simplex_gram = [
        [0 if row == column else 1 for column in range(7)]
        for row in range(7)
    ]
    zero_operator = [[0] * AMBIENT_DIMENSION for _ in range(AMBIENT_DIMENSION)]
    for index, (basis, projector) in enumerate(zip(bases, projectors)):
        if matrix_multiply(
            matrix_multiply(transpose(basis), AMBIENT_FORM), basis
        ) != identity(6):
            raise AssertionError(f"basis {index} is not orthonormal")
        if matrix_multiply(projector, projector) != projector:
            raise AssertionError(f"projector {index} is not idempotent")
        if matrix_multiply(transpose(projector), AMBIENT_FORM) != (
            matrix_multiply(AMBIENT_FORM, projector)
        ):
            raise AssertionError(f"projector {index} is not self-adjoint")
        if gf3_rank(projector) != 6 or matrix_trace(projector) != 0:
            raise AssertionError(f"projector {index} rank/trace changed")
        columns = star_columns(basis)
        if gram(columns) != expected_simplex_gram:
            raise AssertionError(f"projector {index} simplex Gram changed")
        if [mod(sum(row)) for row in columns] != [0] * AMBIENT_DIMENSION:
            raise AssertionError(f"projector {index} simplex sum changed")
        frame = [[0] * AMBIENT_DIMENSION for _ in range(AMBIENT_DIMENSION)]
        for vector in transpose(columns):
            frame = matrix_add(frame, rank_one_operator(vector))
        if projector != scalar_matrix(2, frame):
            raise AssertionError(f"projector {index} frame identity changed")

    if len({flatten(projector) for projector in projectors}) != 12:
        raise AssertionError("base projectors are no longer distinct")
    base_sum = zero_operator
    for projector in projectors:
        base_sum = matrix_add(base_sum, projector)
    if base_sum != zero_operator:
        raise AssertionError("base projector sum changed")

    # Add 29 triples of the first projector: 12+87=99 labels and the added
    # contribution vanishes both in the first and quadratic moments.
    label_types = list(range(12)) + [0] * 87
    all_projectors = [projectors[index] for index in label_types]
    full_sum = zero_operator
    for projector in all_projectors:
        full_sum = matrix_add(full_sum, projector)
    if full_sum != zero_operator:
        raise AssertionError("99-projector sum changed")

    small_pair = [
        [pair_trace(left, right) for right in projectors] for left in projectors
    ]
    small_fourth = [
        [fourth_trace(left, right) for right in projectors] for left in projectors
    ]
    pair_matrix = [
        [small_pair[left][right] for right in label_types] for left in label_types
    ]
    fourth_matrix = [
        [small_fourth[left][right] for right in label_types] for left in label_types
    ]
    pair_row_sums = [mod(sum(row)) for row in pair_matrix]
    fourth_row_sums = [mod(sum(row)) for row in fourth_matrix]
    if pair_row_sums != [0] * 99:
        raise AssertionError("linear trace-Gram contraction changed")
    if fourth_row_sums == [0] * 99:
        raise AssertionError("fourth row-sum separation disappeared")
    quadratic_nonzero = quadratic_moment_nonzero_coordinates(projectors)
    if quadratic_nonzero == 0:
        raise AssertionError("quadratic moment unexpectedly vanished")

    return {
        "ambient_dimension": 11,
        "ambient_form_diagonal": [1] * 10 + [2],
        "ambient_form_discriminant": 2,
        "base_distinct_projectors": 12,
        "projector_labels": 99,
        "each_projector": {
            "rank": 6,
            "trace": 0,
            "idempotent": True,
            "self_adjoint": True,
            "star_space_discriminant": 1,
            "seven_singular_simplex_columns": True,
            "simplex_gram": "J_7-I_7",
            "simplex_sum_zero": True,
            "projector_identity": "P=-sum(z tensor z)",
        },
        "sum_projectors_zero": True,
        "pair_trace_matrix_rank": gf3_rank(pair_matrix),
        "pair_trace_row_sum_distribution": distribution(pair_row_sums),
        "fourth_trace_matrix_rank": gf3_rank(fourth_matrix),
        "fourth_trace_diagonal_zero": all(
            fourth_matrix[index][index] == 0 for index in range(99)
        ),
        "fourth_trace_row_sum_distribution": distribution(fourth_row_sums),
        "ordered_entries_where_pair_and_fourth_trace_differ": sum(
            pair_matrix[left][right] != fourth_matrix[left][right]
            for left in range(99)
            for right in range(99)
        ),
        "quadratic_projector_moment_nonzero_coordinates": quadratic_nonzero,
        "conclusion": (
            "sum_x P_x=0 forces the pair-trace Gram row sums to vanish, "
            "but does not force sum_x(P_x symmetric-tensor P_x)=0 or H*1=0"
        ),
        "satisfied_endpoint_shaped_premises": [
            "nondegenerate nonsquare 11-space over F_3",
            "99 rank-six trace-zero self-adjoint idempotents",
            "every star space has discriminant one",
            "every projector has a seven-singular-column simplex J_7-I_7",
            "P=-sum(z tensor z) for every local simplex",
            "sum of all 99 projectors is zero",
        ],
        "failed_target_premises": [
            "only 12 projector labels are distinct; 87 labels repeat one projector",
            "the local simplex columns are not glued into 231 projectively distinct global columns",
            "there is no 99-by-231 linear point-triangle incidence with column degree three",
            "there is no centered 231-column rank-11 square-zero Gram realization",
            "the endpoint dual-distance, orthogonality graph, and circuit-cover conditions are absent",
            "the control is not an srg(99,14,1,2), graph code, or endpoint realization",
        ],
    }


def dimension_ledger() -> dict[str, Any]:
    n = AMBIENT_DIMENSION
    symmetric_v = n * (n + 1) // 2
    trace_zero = symmetric_v - 1
    wedge_v = n * (n - 1) // 2
    return {
        "V_dimension": n,
        "self_adjoint_End_V_dimension": symmetric_v,
        "trace_zero_self_adjoint_End_V_dimension": trace_zero,
        "quadratic_feature_Sym2_of_trace_zero_dimension":
            trace_zero * (trace_zero + 1) // 2,
        "wedge2_V_dimension": wedge_v,
        "self_adjoint_End_wedge2_V_dimension":
            wedge_v * (wedge_v + 1) // 2,
        "trace_zero_self_adjoint_End_wedge2_V_dimension":
            wedge_v * (wedge_v + 1) // 2 - 1,
        "Sym2_V_dimension": symmetric_v,
        "self_adjoint_End_Sym2_V_dimension":
            symmetric_v * (symmetric_v + 1) // 2,
        "trace_zero_self_adjoint_End_Sym2_V_dimension":
            symmetric_v * (symmetric_v + 1) // 2 - 1,
        "trace_wedge2_projector": mod(6 * 5 // 2),
        "trace_Sym2_projector": mod(6 * 7 // 2),
        "rank_consequence": (
            "all correct operator-coordinate spaces exceed 99; they yield "
            "no nontrivial rank bound for a 99-by-99 matrix"
        ),
    }


def analyze() -> dict[str, Any]:
    return {
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "field": 3,
        "scope": (
            "conditional prism-free n3=4158 centered rank-11 endpoint; "
            "global fourth-trace factorization and obstruction boundary"
        ),
        "inputs": verify_inputs(),
        "dimension_ledger": dimension_ledger(),
        "actual_incidence_factorization": {
            "star_selector": "S_x=diag(B_x)",
            "pair_feature": "u_x[(T,U)]=B[x,T] B[x,U] on ordered block pairs",
            "crossing_kernel": (
                "K_D[(T,U),(R,S)]=D[T,R]D[R,U]D[U,S]D[S,T]"
            ),
            "full_matrix_identity": "H=U K_D U^T",
            "feature_sum_identity": "sum_x u_x=vec(Q), Q=B^T B over F_3",
            "feature_rank_theorem": (
                "rank_F3(U)=99 because for each x any two distinct x-star "
                "blocks give a U-column equal to the unit vector e_x"
            ),
            "quadratic_projector_moment": (
                "Omega=sum_x(P_x symmetric-tensor P_x); sum_x P_x=0 "
                "does not imply Omega=0"
            ),
            "row_sum_identity": (
                "H*1 is the crossing pairing of P_x symmetric-tensor P_x "
                "with Omega"
            ),
            "hadamard_localizer": (
                "M_x=D S_x D; (H*1)_x=tr((Q o M_x)M_x)"
            ),
            "line_vector_refinement": (
                "for w_TU=B(D_T o D_U), "
                "(K_D vec(Q))[(T,U)]=w_TU^T w_TU"
            ),
            "star_pair_feature_control": star_pair_feature_summary(),
            "toy_exact_replay": toy_factorization_summary(),
        },
        "positive_control": projector_control_summary(),
        "conclusions": {
            "new_full_matrix_identity": "H=U K_D U^T",
            "star_pair_incidence_alone_forces_rank_drop": False,
            "sum_projectors_zero_forces_H_row_sums_zero": False,
            "naive_wedge_or_symmetric_square_rank_bound_below_99": False,
            "endpoint_excluded": False,
            "rank_11_excluded": False,
            "strict_n3_improvement": False,
            "conway_99_status": "UNKNOWN",
            "newly_named_missing_invariant": (
                "the restriction of the crossing four-Gram kernel K_D to "
                "the full-rank 99-dimensional star-pair feature subspace; "
                "equivalently the Hadamard localizers "
                "Q o (D S_x D), or the norms of "
                "w_TU=B(D_T o D_U)"
            ),
        },
    }


def verify(data: dict[str, Any]) -> None:
    dimensions = data["dimension_ledger"]
    if dimensions != {
        "V_dimension": 11,
        "self_adjoint_End_V_dimension": 66,
        "trace_zero_self_adjoint_End_V_dimension": 65,
        "quadratic_feature_Sym2_of_trace_zero_dimension": 2145,
        "wedge2_V_dimension": 55,
        "self_adjoint_End_wedge2_V_dimension": 1540,
        "trace_zero_self_adjoint_End_wedge2_V_dimension": 1539,
        "Sym2_V_dimension": 66,
        "self_adjoint_End_Sym2_V_dimension": 2211,
        "trace_zero_self_adjoint_End_Sym2_V_dimension": 2210,
        "trace_wedge2_projector": 0,
        "trace_Sym2_projector": 0,
        "rank_consequence": (
            "all correct operator-coordinate spaces exceed 99; they yield "
            "no nontrivial rank bound for a 99-by-99 matrix"
        ),
    }:
        raise AssertionError("dimension ledger changed")
    feature = data["actual_incidence_factorization"][
        "star_pair_feature_control"
    ]
    if feature["star_pair_feature_rank"] != 99:
        raise AssertionError("star-pair feature rank changed")
    if feature["ordered_distinct_star_pair_coordinates"] != 4158:
        raise AssertionError("ordered star-pair count changed")
    if feature["control_is_srg_99_14_1_2"]:
        raise AssertionError("relaxed incidence control became target-shaped")
    control = data["positive_control"]
    if control["pair_trace_matrix_rank"] != 8:
        raise AssertionError("pair-trace control rank changed")
    if control["fourth_trace_matrix_rank"] != 9:
        raise AssertionError("fourth-trace control rank changed")
    if control["pair_trace_row_sum_distribution"] != {"0": 99}:
        raise AssertionError("linear contraction control changed")
    if control["fourth_trace_row_sum_distribution"] != {
        "0": 6,
        "1": 91,
        "2": 2,
    }:
        raise AssertionError("fourth row-sum control changed")
    if control["ordered_entries_where_pair_and_fourth_trace_differ"] != 740:
        raise AssertionError("pair/fourth separation changed")
    if control["quadratic_projector_moment_nonzero_coordinates"] != 302:
        raise AssertionError("quadratic projector moment changed")
    if data["conclusions"]["endpoint_excluded"]:
        raise AssertionError("status inflation")
    if data["conclusions"]["rank_11_excluded"]:
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
    print("PASS: Wave205 global fourth-moment proof-B checks")


if __name__ == "__main__":
    main()
