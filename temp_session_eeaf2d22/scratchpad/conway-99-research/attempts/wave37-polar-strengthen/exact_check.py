#!/usr/bin/env python3
"""Exact Wave 37 finite-polar and ternary-code strengthening checks.

This discovery-side checker starts only from the frozen endpoint reflection
data and the independently verified Wave 36 finite-field factorization.  It
does not construct the endpoint matrix, a point configuration, or a Conway
graph.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


PUBLIC_HEAD = "efbf74e3edf4d11d853d0129634507b01ff7b577"
N = 231
RANK_Q = 44
S_PLUS = 32
S_MINUS = 36
S_ZERO = 162
S_POSITIVE_EIGENVALUE = 17
S_POSITIVE_MULTIPLICITY = 44
S_NEGATIVE_EIGENVALUE = -4
S_NEGATIVE_MULTIPLICITY = 187

INPUT_HASHES = {
    "agents/2026-07-26-wave36-ternary-polar-bound.md":
        "062e8b5478b93195dae4d9a571677688cefcd7397cda75246dbd03503f7c9b85",
    "attempts/wave36-ternary-polar-bound/exact-results.json":
        "7d7c15ad99952ee3ca70582a887e771331156b8ef8e50524d296f1dc15f425a1",
    "verification/wave36-ternary-polar-bound/independent-results.json":
        "38ec002886c2a9b38f8d11824dc79e07147b16386dcc3449064633efb630beeb",
    "attempts/wave35-n3-upper-spectral/exact-results.json":
        "ca1df07bede11642fb1639a2ae554c1a31ce9a58424d5b3e5031c90ad550a194",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_frozen_inputs(root: Path | None = None) -> None:
    base = repository_root() if root is None else root
    actual = {
        relative: sha256_file(base / relative)
        for relative in INPUT_HASHES
    }
    require(actual == INPUT_HASHES, f"frozen input mismatch: {actual!r}")


def fraction_record(value: Fraction) -> dict[str, int | str]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "display": (
            str(value.numerator)
            if value.denominator == 1
            else f"{value.numerator}/{value.denominator}"
        ),
    }


def ternary_code_consequences(rank: int = 12) -> dict[str, object]:
    """Record consequences of C=V H V^T and C^2=C1=0 over F_3."""

    require(rank >= 1, "rank must be positive")
    special_weight = 1 + S_PLUS + S_MINUS
    composition_one = S_MINUS
    composition_two = 1 + S_PLUS
    require(special_weight == 69, "special codeword weight changed")
    require(
        (composition_one, composition_two) == (36, 33),
        "special complete weight changed",
    )
    require(composition_one % 3 == composition_two % 3 == 0,
            "special complete weight lost ternary divisibility")

    symmetric_square_ceiling = rank * (rank + 1) // 2
    return {
        "factorization": "C=V H V^T over F_3, with V full column rank",
        "square_zero_frame": "V^T V=0",
        "zero_sum_frame": "V^T 1=0",
        "code": {
            "definition": "U=col(V) <= F_3^231",
            "parameters": f"[231,{rank}]_3",
            "self_orthogonal": True,
            "all_one_vector_in_dual": True,
            "projective": True,
            "dual_distance_lower_bound": 3,
            "every_word_symbol_one_count_divisible_by_3": True,
            "every_word_symbol_two_count_divisible_by_3": True,
            "reason": (
                "x.x=0 gives n1+n2=0 mod 3 and x.1=0 gives "
                "n1+2n2=0 mod 3"
            ),
        },
        "distinguished_words": {
            "projective_word_count": N,
            "nonzero_word_count_including_negatives": 2 * N,
            "weight": special_weight,
            "composition_n1_n2": [composition_one, composition_two],
            "weight_enumerator_constraint": "A_69>=462",
        },
        "schur_square": {
            "matrix": "C^(o2)=I+B mod 3, B=S^(o2)",
            "rank_ceiling": symmetric_square_ceiling,
            "orthogonality_matrix": "J-I-B",
            "orthogonality_matrix_rank_ceiling": symmetric_square_ceiling + 1,
        },
    }


def krawtchouk(order: int, weight: int, length: int = N, field: int = 3) -> int:
    """q-ary Krawtchouk polynomial K_order(weight), exactly."""

    lower = max(0, order - (length - weight))
    upper = min(order, weight)
    return sum(
        (-1) ** index
        * (field - 1) ** (order - index)
        * math.comb(weight, index)
        * math.comb(length - weight, order - index)
        for index in range(lower, upper + 1)
    )


def ternary_delsarte_relaxation() -> dict[str, object]:
    """Give an exact hostile real relaxation for basic code LP constraints.

    This is deliberately not called a formal or realizable weight enumerator:
    most transformed coefficients are nonintegral.  It only proves that
    nonnegativity of the ordinary MacWilliams transform, even together with
    C <= C^perp, does not reject the boundary data.
    """

    code_size = 3**12
    distribution = {
        0: 1,
        69: 462,
        141: 76965,
        153: 288015,
        162: 165998,
    }
    require(sum(distribution.values()) == code_size, "A-distribution total changed")
    require(all(weight % 3 == 0 for weight in distribution),
            "A-distribution has a forbidden weight")

    transformed_numerators = []
    nonintegral = []
    for order in range(N + 1):
        numerator = sum(
            amount * krawtchouk(order, weight)
            for weight, amount in distribution.items()
        )
        transformed_numerators.append(numerator)
        require(numerator >= 0, f"negative transformed coefficient B_{order}")
        require(
            numerator >= code_size * distribution.get(order, 0),
            f"self-orthogonal relaxation B_{order}>=A_{order} failed",
        )
        if numerator % code_size:
            nonintegral.append(order)

    require(transformed_numerators[1] == transformed_numerators[2] == 0,
            "projective dual-distance moments changed")
    require(nonintegral == list(range(3, N + 1)),
            "hostile relaxation integrality boundary changed")
    return {
        "A_distribution": {
            str(weight): amount
            for weight, amount in sorted(distribution.items())
        },
        "sum_A": code_size,
        "A_69": distribution[69],
        "weights_divisible_by_3": True,
        "B_1": 0,
        "B_2": 0,
        "all_real_B_nonnegative": True,
        "all_real_B_at_least_A": True,
        "nonintegral_B_orders": nonintegral,
        "is_formal_weight_enumerator": False,
        "is_code": False,
        "interpretation": (
            "The basic real Delsarte/MacWilliams inequalities do not exclude "
            "rank twelve. Integrality and realizability remain unproved."
        ),
    }


def ternary_oriented_scheme() -> dict[str, object]:
    """Reconstruct the five-class oriented norm-two scheme in square rank 12."""

    field = 3
    dimension = 12
    diagonal = (1,) * dimension
    x = (0, 0, 1, 1) + (0,) * 8
    representatives = (
        x,
        tuple((-entry) % field for entry in x),
        (0, 0, 1, 2) + (0,) * 8,
        (0, 1, 0, 1) + (0,) * 8,
        (0, 1, 0, 2) + (0,) * 8,
    )

    def inner(left: Sequence[int], right: Sequence[int]) -> int:
        return sum(
            coefficient * a * b
            for coefficient, a, b in zip(diagonal, left, right)
        ) % field

    def negative(vector: Sequence[int]) -> tuple[int, ...]:
        return tuple((-entry) % field for entry in vector)

    def relation(left: Sequence[int], right: Sequence[int]) -> int:
        if tuple(right) == tuple(left):
            return 0
        if tuple(right) == negative(left):
            return 1
        return {0: 2, 1: 3, 2: 4}[inner(left, right)]

    require([relation(x, y) for y in representatives] == list(range(5)),
            "oriented ternary relation representatives changed")

    intersection_matrices = []
    for y in representatives:
        states: dict[tuple[int, int, int], int] = {(0, 0, 0): 1}
        for coefficient, x_coordinate, y_coordinate in zip(diagonal, x, y):
            updated: dict[tuple[int, int, int], int] = defaultdict(int)
            for (norm, x_inner, y_inner), count in states.items():
                for z_coordinate in range(field):
                    updated[
                        (
                            (norm + coefficient * z_coordinate**2) % field,
                            (
                                x_inner
                                + coefficient * x_coordinate * z_coordinate
                            ) % field,
                            (
                                y_inner
                                + coefficient * y_coordinate * z_coordinate
                            ) % field,
                        )
                    ] += count
            states = dict(updated)

        matrix = [[0] * 5 for _ in range(5)]
        generic = {0: 2, 1: 3, 2: 4}
        for (norm, x_inner, y_inner), count in states.items():
            if norm == 2:
                matrix[generic[x_inner]][generic[y_inner]] += count
        for z in {tuple(x), negative(x), tuple(y), negative(y)}:
            old_i = generic[inner(x, z)]
            old_j = generic[inner(z, y)]
            new_i = relation(x, z)
            new_j = relation(z, y)
            matrix[old_i][old_j] -= 1
            matrix[new_i][new_j] += 1
        intersection_matrices.append(matrix)

    valencies = [
        intersection_matrices[0][index][index]
        for index in range(5)
    ]
    require(valencies == [1, 1, 58806, 59048, 59048],
            "ternary oriented valencies changed")

    first_eigenmatrix = [
        [1, 1, 58806, 59048, 59048],
        [1, 1, 486, -244, -244],
        [1, -1, 0, 244, -244],
        [1, 1, -162, 80, 80],
        [1, -1, 0, -242, 242],
    ]
    for character in first_eigenmatrix:
        for left in range(5):
            for right in range(5):
                expected = character[left] * character[right]
                actual = sum(
                    intersection_matrices[relation_index][left][right]
                    * character[relation_index]
                    for relation_index in range(5)
                )
                require(actual == expected, "ternary scheme character failed")

    endpoint_distribution = [1, 0, 162, 36, 32]
    positivity = [
        sum(
            Fraction(amount * eigenvalue, valency)
            for amount, eigenvalue, valency in zip(
                endpoint_distribution, character, valencies
            )
        )
        for character in first_eigenmatrix
    ]
    require(all(value >= 0 for value in positivity),
            "oriented association-scheme positivity failed")
    return {
        "relation_order": [
            "equal",
            "antipodal",
            "inner_0",
            "inner_1_independent",
            "inner_2_independent",
        ],
        "valencies": valencies,
        "intersection_matrices": intersection_matrices,
        "first_eigenmatrix": first_eigenmatrix,
        "endpoint_inner_distribution": endpoint_distribution,
        "delsarte_positivity": [
            fraction_record(value) for value in positivity
        ],
        "excluded": False,
    }


def divisibility_refined_evans() -> dict[str, object]:
    """Use the ternary frame to sharpen the outside-degree integer gap."""

    v = 88452
    k = 29403
    lam = 9882
    mu = 9720
    selected = N
    induced_degree = S_ZERO
    outside_count = v - selected
    first_moment = selected * (k - induced_degree)
    second_moment = (
        (lam - mu) * selected * induced_degree
        + (k - mu) * selected
        + mu * selected**2
        - selected * induced_degree**2
    )
    require(
        (outside_count, first_moment, second_moment)
        == (88221, 6754671, 523215693),
        "outside moments changed",
    )
    require(first_moment % 3 == 0 and second_moment % 9 == 0,
            "outside divisibility moments changed")

    ordinary = min(
        (
            second_moment
            - (2 * root + 1) * first_moment
            + root * (root + 1) * outside_count,
            root,
        )
        for root in range(selected + 1)
    )
    divisible = min(
        (
            second_moment
            - (2 * root + 3) * first_moment
            + root * (root + 3) * outside_count,
            root,
        )
        for root in range(0, selected + 1, 3)
    )
    require(ordinary == (6020322, 76), "ordinary Evans boundary changed")
    require(divisible == (5843880, 75), "divisible Evans boundary changed")
    return {
        "ambient_parameters": {
            "v": v,
            "k": k,
            "lambda": lam,
            "mu": mu,
        },
        "selected_size": selected,
        "selected_degree": induced_degree,
        "outside_count": outside_count,
        "outside_degree_sum": first_moment,
        "outside_degree_square_sum": second_moment,
        "outside_degrees_divisible_by_3": True,
        "ordinary_consecutive_integer_polynomial": {
            "root_pair": [ordinary[1], ordinary[1] + 1],
            "sum": ordinary[0],
        },
        "divisibility_refined_polynomial": {
            "root_pair": [divisible[1], divisible[1] + 3],
            "sum": divisible[0],
        },
        "excluded": divisible[0] < 0,
    }


def polynomial_add(left: list[int], right: list[int]) -> list[int]:
    size = max(len(left), len(right))
    answer = [0] * size
    for index in range(size):
        answer[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        )
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return answer


def polynomial_multiply(left: list[int], right: list[int]) -> list[int]:
    answer = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            answer[i + j] += a * b
    return answer


def permutation_sign(permutation: Sequence[int]) -> int:
    inversions = sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def characteristic_polynomial(matrix: Sequence[Sequence[int]]) -> list[int]:
    """Return det(xI-M), low coefficient first, by the Leibniz formula."""

    size = len(matrix)
    require(all(len(row) == size for row in matrix), "matrix is not square")
    total = [0]
    for permutation in itertools.permutations(range(size)):
        term = [permutation_sign(permutation)]
        for row, column in enumerate(permutation):
            factor = [-matrix[row][column]]
            if row == column:
                factor.append(1)
            term = polynomial_multiply(term, factor)
        total = polynomial_add(total, term)
    return total


def q7_projective_scheme(determinant_class: int) -> dict[str, object]:
    """Build the rank-eleven norm-one projective association scheme over F_7."""

    field = 7
    dimension = 11
    require(determinant_class in (1, 3), "F_7 determinant class must be 1 or 3")
    diagonal = (1,) * (dimension - 1) + (determinant_class,)

    def norm(vector: Sequence[int]) -> int:
        return sum(
            coefficient * entry * entry
            for coefficient, entry in zip(diagonal, vector)
        ) % field

    def inner(left: Sequence[int], right: Sequence[int]) -> int:
        return sum(
            coefficient * a * b
            for coefficient, a, b in zip(diagonal, left, right)
        ) % field

    def negative(vector: Sequence[int]) -> tuple[int, ...]:
        return tuple((-entry) % field for entry in vector)

    square_to_relation = {0: 1, 1: 2, 2: 3, 4: 4}

    def relation(left: Sequence[int], right: Sequence[int]) -> int:
        if tuple(right) in (tuple(left), negative(left)):
            return 0
        return square_to_relation[inner(left, right) ** 2 % field]

    x = (1,) + (0,) * (dimension - 1)
    representatives: dict[int, tuple[int, ...]] = {0: x}
    for short in itertools.product(range(field), repeat=4):
        candidate = short + (0,) * (dimension - 4)
        if norm(candidate) != 1 or candidate in (x, negative(x)):
            continue
        class_index = square_to_relation.get(inner(x, candidate) ** 2 % field)
        if class_index is not None and class_index not in representatives:
            representatives[class_index] = candidate
        if len(representatives) == 5:
            break
    require(set(representatives) == set(range(5)),
            "failed to find all F_7 pair-orbit representatives")

    intersection_matrices = []
    for class_index in range(5):
        y = representatives[class_index]
        states: dict[tuple[int, int, int], int] = {(0, 0, 0): 1}
        for coefficient, x_coordinate, y_coordinate in zip(diagonal, x, y):
            updated: dict[tuple[int, int, int], int] = defaultdict(int)
            for (q_value, x_inner, y_inner), count in states.items():
                for z_coordinate in range(field):
                    updated[
                        (
                            (q_value + coefficient * z_coordinate**2) % field,
                            (
                                x_inner
                                + coefficient * x_coordinate * z_coordinate
                            ) % field,
                            (
                                y_inner
                                + coefficient * y_coordinate * z_coordinate
                            ) % field,
                        )
                    ] += count
            states = dict(updated)

        vector_matrix = [[0] * 5 for _ in range(5)]
        for (q_value, x_inner, y_inner), count in states.items():
            if q_value == 1:
                vector_matrix[
                    square_to_relation[x_inner**2 % field]
                ][
                    square_to_relation[y_inner**2 % field]
                ] += count
        for z in {x, negative(x), y, negative(y)}:
            old_i = square_to_relation[inner(x, z) ** 2 % field]
            old_j = square_to_relation[inner(z, y) ** 2 % field]
            new_i = relation(x, z)
            new_j = relation(z, y)
            vector_matrix[old_i][old_j] -= 1
            vector_matrix[new_i][new_j] += 1

        require(all(value % 2 == 0 for row in vector_matrix for value in row),
                "norm-one vectors did not pair projectively")
        intersection_matrices.append(
            [[value // 2 for value in row] for row in vector_matrix]
        )

    valencies = [
        intersection_matrices[0][index][index]
        for index in range(5)
    ]
    expected_valencies = {
        1: [1, 20178004, 40339200, 40356008, 40356008],
        3: [1, 20175603, 40368012, 40351206, 40351206],
    }[determinant_class]
    require(valencies == expected_valencies, "F_7 projective valencies changed")

    # Multiplication by the orthogonality relation in the Bose--Mesner
    # algebra. Column j contains the coefficients of A_orth A_j.
    orthogonality_multiplication = [
        [
            intersection_matrices[pair_class][1][right_relation]
            for right_relation in range(5)
        ]
        for pair_class in range(5)
    ]
    actual_characteristic = characteristic_polynomial(
        orthogonality_multiplication
    )
    if determinant_class == 1:
        expected_factors = [
            [-valencies[1], 1],
            [4802, 1],
            [-2401, 1],
            [-7**8, -4802, 1],
        ]
        theta = "2401*(1+sqrt(2))"
        theta_lower_bound = 4802
    else:
        expected_factors = [
            [-valencies[1], 1],
            [-4802, 1],
            [2401, 1],
            [-7**8, 4802, 1],
        ]
        theta = "4802"
        theta_lower_bound = 4802
    expected_characteristic = [1]
    for factor in expected_factors:
        expected_characteristic = polynomial_multiply(
            expected_characteristic, factor
        )
    require(actual_characteristic == expected_characteristic,
            "F_7 orthogonality characteristic polynomial changed")

    common_orthogonal_neighbors = [
        intersection_matrices[pair_class][1][1]
        for pair_class in range(5)
    ]
    require(
        len(set(common_orthogonal_neighbors[2:])) > 1,
        "F_7 orthogonality graph unexpectedly became strongly regular",
    )
    require(theta_lower_bound > S_ZERO,
            "F_7 rank-eleven spectral survivor lost its slack")
    return {
        "dimension": dimension,
        "determinant_class": (
            "square" if determinant_class == 1 else "nonsquare"
        ),
        "vertex_count": sum(valencies),
        "relation_order": [
            "equal",
            "orthogonal",
            "nonorthogonal_t_squared_1_degenerate",
            "nonorthogonal_t_squared_2",
            "nonorthogonal_t_squared_4",
        ],
        "valencies": valencies,
        "common_orthogonal_neighbors_by_relation": common_orthogonal_neighbors,
        "is_strongly_regular": False,
        "orthogonality_multiplication_matrix": orthogonality_multiplication,
        "orthogonality_characteristic_polynomial_low_first":
            actual_characteristic,
        "largest_nonprincipal_eigenvalue": theta,
        "largest_nonprincipal_eigenvalue_strictly_above": theta_lower_bound,
        "spectral_mixing_right_side_strictly_above": theta_lower_bound,
        "target_induced_degree": S_ZERO,
        "excluded": False,
    }


def signed_triangle_geometry() -> dict[str, object]:
    """Separate balanced signed triangles from genuinely collinear triples."""

    support_degree = S_PLUS + S_MINUS
    edge_count = N * support_degree // 2
    trace_cube = (
        S_POSITIVE_MULTIPLICITY * S_POSITIVE_EIGENVALUE**3
        + S_NEGATIVE_MULTIPLICITY * S_NEGATIVE_EIGENVALUE**3
    )
    signed_triangle_difference = trace_cube // 6
    require(
        (support_degree, edge_count, trace_cube, signed_triangle_difference)
        == (68, 7854, 204204, 34034),
        "signed triangle data changed",
    )

    # A nonorthogonal pair of norm-two projective points over F_3 lies on a
    # unique projective line, so it is contained in at most one collinear
    # selected triple.
    maximum_collinear_triples = edge_count // 3
    minimum_independent_balanced = (
        signed_triangle_difference - maximum_collinear_triples
    )
    require(
        (maximum_collinear_triples, minimum_independent_balanced)
        == (2618, 31416),
        "collinear/independent triangle boundary changed",
    )

    # A three-space whose restricted Gram form has rank one has a
    # two-dimensional radical. Its norm-two projective points form an affine
    # plane of order three: 9 points, 12 lines, and 84-12=72 independent
    # triples.
    points_per_degenerate_space = 3**2
    affine_lines = 3 * (3 + 1)
    independent_triples_per_space = (
        math.comb(points_per_degenerate_space, 3) - affine_lines
    )
    minimum_degenerate_spaces = math.ceil(
        minimum_independent_balanced / independent_triples_per_space
    )
    require(
        (points_per_degenerate_space, affine_lines,
         independent_triples_per_space, minimum_degenerate_spaces)
        == (9, 12, 72, 437),
        "degenerate-space covering count changed",
    )
    return {
        "support_graph_degree": support_degree,
        "support_graph_edges": edge_count,
        "trace_S_cubed": trace_cube,
        "balanced_minus_unbalanced_triangles": signed_triangle_difference,
        "maximum_collinear_selected_triples": maximum_collinear_triples,
        "minimum_linearly_independent_balanced_triples":
            minimum_independent_balanced,
        "independent_balanced_triple_span": {
            "dimension": 3,
            "restricted_gram_rank": 1,
            "radical_dimension": 2,
        },
        "maximum_norm_two_points_per_such_space":
            points_per_degenerate_space,
        "maximum_independent_triples_per_such_space":
            independent_triples_per_space,
        "minimum_distinct_degenerate_three_spaces":
            minimum_degenerate_spaces,
        "false_inference_refuted": (
            "A singular 3x3 Gram matrix in a nondegenerate ambient space "
            "does not imply the three vectors are linearly dependent."
        ),
    }


def boundary_rank_dichotomy() -> dict[str, object]:
    pairs = [
        (rank3, rank7)
        for rank3 in range(12, RANK_Q + 1)
        for rank7 in range(11, RANK_Q + 1)
        if (rank3 + rank7) % 2 == 0
    ]
    require(len(pairs) == 561, "combined Wave 36 rank-pair count changed")
    require(
        all(rank7 >= 12 and rank7 % 2 == 0 for rank3, rank7 in pairs if rank3 == 12),
        "r3=12 parity boundary changed",
    )
    require(
        all(rank3 >= 13 and rank3 % 2 == 1 for rank3, rank7 in pairs if rank7 == 11),
        "r7=11 parity boundary changed",
    )
    return {
        "surviving_pair_count_after_wave36_bounds_and_parity": len(pairs),
        "if_r3_equals_12": {
            "ternary_determinant_class": "square",
            "r7_minimum": 12,
            "r7_parity": "even",
        },
        "if_r7_equals_11": {
            "r3_minimum": 13,
            "r3_parity": "odd",
        },
    }


def build_results() -> dict[str, object]:
    verify_frozen_inputs()
    ternary = ternary_code_consequences()
    q7_cases = [q7_projective_scheme(value) for value in (1, 3)]
    require(all(not case["excluded"] for case in q7_cases),
            "an F_7 rank-eleven class was unexpectedly excluded")
    return {
        "schema_version": 1,
        "claim_label": "DERIVED_INCONCLUSIVE_PENDING_INDEPENDENT_VERIFICATION",
        "scope": (
            "Conditional n3=4158 ternary code/design strengthening, signed "
            "degenerate-triple count, and characteristic-seven rank-eleven "
            "projective spectral test"
        ),
        "frozen_public_head": PUBLIC_HEAD,
        "ternary_code": ternary,
        "ternary_basic_delsarte_relaxation": ternary_delsarte_relaxation(),
        "ternary_oriented_association_scheme": ternary_oriented_scheme(),
        "ternary_divisibility_refined_evans": divisibility_refined_evans(),
        "signed_triangle_geometry": signed_triangle_geometry(),
        "characteristic_seven_rank_eleven_cases": q7_cases,
        "combined_rank_boundary": boundary_rank_dichotomy(),
        "conclusion": {
            "new_rank_lower_bound": False,
            "new_determinant_class_exclusion": False,
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "strongest_general_upper_bound_on_n3": 4158,
            "target_status": "UNKNOWN",
            "stronger_structural_restrictions": [
                "projective self-orthogonal ternary [231,r3] code with 1 in its dual",
                "A_69>=462 and both nonzero symbol counts divisible by three",
                "rank_F3(I+B)<=r3(r3+1)/2",
                "at least 31416 independent balanced degenerate ternary triples",
                "at least 437 distinct rank-one degenerate three-spaces",
                "231 distinct norm-one F_7 projective points at r7=11 survive both determinant classes",
            ],
        },
        "limitations": [
            "No endpoint reflection, finite-field configuration, or graph is constructed.",
            "The real Delsarte control is not a formal weight enumerator or code.",
            "The F_7 orthogonality graph is not strongly regular, so Evans's SRG polynomial does not apply.",
            "The square r3=12 case and both r7=11 determinant classes survive the tested exact bounds.",
            "The false collinearity inference is explicitly refuted.",
            "No literature novelty or priority claim is made.",
        ],
    }


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    require(not (arguments.output and arguments.verify),
            "choose only one of --output and --verify")
    rendered = canonical_json(build_results())
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    elif arguments.verify is not None:
        require(
            arguments.verify.read_text(encoding="utf-8") == rendered,
            "stored result differs from exact regeneration",
        )
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
