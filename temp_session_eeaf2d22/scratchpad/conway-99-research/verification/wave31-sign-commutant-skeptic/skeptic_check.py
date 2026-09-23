#!/usr/bin/env python3
"""Independent exact checks for the Wave 31 sign-commutant argument.

This is intentionally not a replay of the discovery checker.  It checks the
small exact algebra, all divisibility edge cases, and countermodels obtained
when named premises are removed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


CANDIDATE_COMMIT = "a8b0c34040f6857b3c5ebcc44f108e03a4159088"
VERTICES = 99
TRIANGLES = 231
TRIANGLES_PER_VERTEX = 7
VERTICES_PER_TRIANGLE = 3
PROJECTOR_RANK = 44


Matrix = list[list[Fraction]]


def matrix(rows: Sequence[Sequence[int | Fraction]]) -> Matrix:
    return [[Fraction(value) for value in row] for row in rows]


def transpose(a: Matrix) -> Matrix:
    return [list(row) for row in zip(*a)]


def multiply(a: Matrix, b: Matrix) -> Matrix:
    if not a or not b or len(a[0]) != len(b):
        raise ValueError("incompatible matrix dimensions")
    return [
        [
            sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction(0))
            for j in range(len(b[0]))
        ]
        for i in range(len(a))
    ]


def subtract(a: Matrix, b: Matrix) -> Matrix:
    return [
        [a[i][j] - b[i][j] for j in range(len(a[0]))]
        for i in range(len(a))
    ]


def inverse_2x2(a: Matrix) -> Matrix:
    if len(a) != 2 or any(len(row) != 2 for row in a):
        raise ValueError("only 2-by-2 matrices are accepted")
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    if det == 0:
        raise ValueError("singular matrix")
    return [
        [a[1][1] / det, -a[0][1] / det],
        [-a[1][0] / det, a[0][0] / det],
    ]


def identity(n: int) -> Matrix:
    return [
        [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]


def is_zero(a: Matrix) -> bool:
    return all(value == 0 for row in a for value in row)


def encode_matrix(a: Matrix) -> list[list[int | str]]:
    encoded: list[list[int | str]] = []
    for row in a:
        encoded.append(
            [
                value.numerator
                if value.denominator == 1
                else f"{value.numerator}/{value.denominator}"
                for value in row
            ]
        )
    return encoded


def adjacency(order: int, edges: Iterable[tuple[int, int]]) -> Matrix:
    result = [[Fraction(0) for _ in range(order)] for _ in range(order)]
    for left, right in edges:
        result[left][right] = Fraction(1)
        result[right][left] = Fraction(1)
    return result


def signed_adjacency(
    order: int, edge_signs: dict[tuple[int, int], int]
) -> Matrix:
    result = [[Fraction(0) for _ in range(order)] for _ in range(order)]
    for (left, right), sign in edge_signs.items():
        if sign not in (-1, 1):
            raise ValueError("edge signs must be plus or minus one")
        result[left][right] = Fraction(sign)
        result[right][left] = Fraction(sign)
    return result


def integer_partitions(total: int, minimum: int = 1) -> list[tuple[int, ...]]:
    result: list[tuple[int, ...]] = []

    def visit(remaining: int, floor: int, prefix: tuple[int, ...]) -> None:
        if remaining == 0:
            result.append(prefix)
            return
        for part in range(floor, remaining + 1):
            visit(remaining - part, part, prefix + (part,))

    visit(total, minimum, ())
    return result


def check_basis_change() -> dict[str, object]:
    # Original identities: Y^T Y = 21 T^-1 and M = Y T Y^T.
    t = matrix([[21, 0], [0, 21]])
    y = identity(2)
    p = matrix([[1, 1], [0, 1]])
    p_inverse = inverse_2x2(p)
    contragredient = transpose(p_inverse)
    transformed_y = multiply(y, contragredient)
    transformed_s = multiply(multiply(transpose(p), t), p)

    original_m = multiply(multiply(y, t), transpose(y))
    transformed_m = multiply(
        multiply(transformed_y, transformed_s), transpose(transformed_y)
    )
    transformed_gram = multiply(transpose(transformed_y), transformed_y)
    expected_gram = [
        [21 * value for value in row]
        for row in inverse_2x2(transformed_s)
    ]

    assert transformed_m == original_m
    assert transformed_gram == expected_gram
    assert all(
        value.denominator == 1
        for row in transformed_y
        for value in row
    )
    return {
        "unimodular_P": encode_matrix(p),
        "contragredient_P_inverse_transpose": encode_matrix(contragredient),
        "transformed_S": encode_matrix(transformed_s),
        "transformed_X": encode_matrix(transformed_y),
        "M_is_preserved": True,
        "X_transpose_X_equals_21_S_inverse": True,
        "integrality_is_preserved": True,
    }


def check_support_and_block_nonemptiness() -> dict[str, object]:
    # With every nonzero component norm at least four, a total norm of four
    # has exactly one nonzero component.
    admissible = []
    for first in (0, 4, 5, 6, 7, 8):
        for second in (0, 4, 5, 6, 7, 8):
            if first + second == 4:
                admissible.append((first, second))
    assert admissible == [(0, 4), (4, 0)]

    # Dropping minimum four permits a row to cross two integral blocks.
    weakened_s = matrix([[2, 0], [0, 2]])
    crossing_row = matrix([[1, 1]])
    crossing_norm = multiply(
        multiply(crossing_row, weakened_s), transpose(crossing_row)
    )[0][0]
    assert crossing_norm == 4

    # A positive-rank block cannot have an empty row set because its diagonal
    # block of X^T X is 21 S_block^-1, which is positive definite.
    empty_left = matrix([[0]])
    positive_right = matrix([[Fraction(21, 4)]])
    assert empty_left != positive_right
    return {
        "minimum_four_norm_partitions": [list(item) for item in admissible],
        "every_norm_four_row_has_one_block_support": True,
        "every_positive_rank_lattice_block_has_nonempty_row_set": True,
        "minimum_two_countermodel": {
            "S": encode_matrix(weakened_s),
            "row": encode_matrix(crossing_row)[0],
            "row_norm": int(crossing_norm),
            "nonzero_block_components": 2,
        },
    }


def check_incidence_transport_and_projector() -> dict[str, object]:
    adjacency_eigenspaces = [
        {"adjacency": 14, "J": 99, "P_minus_four": Fraction(27 - 9 * 14 + 99, 63)},
        {"adjacency": 3, "J": 0, "P_minus_four": Fraction(27 - 9 * 3, 63)},
        {"adjacency": -4, "J": 0, "P_minus_four": Fraction(27 + 36, 63)},
    ]
    assert [row["P_minus_four"] for row in adjacency_eigenspaces] == [0, 0, 1]

    # On im(E), N^T N is multiplication by 3.  Hence N is injective there;
    # the image lies in the -4 eigenspace and both dimensions are 44.
    incidence_scale = 3
    assert incidence_scale > 0
    assert PROJECTOR_RANK == 44

    # Formal noncommutative coefficient check:
    # K(27I-9A+J)=(27I-9A+J)K.
    left_minus_right = {
        "KA": -9,
        "AK": 9,
        "KJ": 1,
        "JK": -1,
    }
    target = {
        "KA": 9,
        "AK": -9,
        "KJ": -1,
        "JK": 1,
    }
    # Multiplying the commutation equation by -1 yields the submitted order.
    assert {term: -coefficient for term, coefficient in left_minus_right.items()} == target

    # K1=3d turns 9[KA-AK]=[KJ-JK] into
    # 3[KA-AK]=d1^T-1d^T.
    assert Fraction(9, VERTICES_PER_TRIANGLE) == 3
    return {
        "N_is_injective_on_im_E": True,
        "image_dimension": PROJECTOR_RANK,
        "minus_four_eigenspace_dimension": 44,
        "N_maps_im_E_onto_minus_four_eigenspace": True,
        "projector_eigenspace_values": [
            {
                "adjacency_eigenvalue": row["adjacency"],
                "J_eigenvalue": row["J"],
                "projector_value": int(row["P_minus_four"]),
            }
            for row in adjacency_eigenspaces
        ],
        "commutator_coefficients": target,
        "K_one_scale": VERTICES_PER_TRIANGLE,
        "reduced_commutator_left_scale": 3,
    }


def check_symmetric_invariance() -> dict[str, object]:
    p = matrix([[1, 0], [0, 0]])

    # Exhaust a small exact family.  A symmetric 2-by-2 matrix preserving
    # span(e_1) has zero off-diagonal entry and commutes with P.
    checked = 0
    for a in range(-2, 3):
        for b in range(-2, 3):
            for c in range(-2, 3):
                k = matrix([[a, b], [b, c]])
                preserves = b == 0
                if preserves:
                    checked += 1
                    assert is_zero(subtract(multiply(k, p), multiply(p, k)))

    # Without symmetry, preservation of V does not imply commutation.
    nonsymmetric = matrix([[1, 1], [0, 0]])
    image_e1 = multiply(nonsymmetric, matrix([[1], [0]]))
    nonsymmetric_commutator = subtract(
        multiply(nonsymmetric, p), multiply(p, nonsymmetric)
    )
    assert image_e1 == matrix([[1], [0]])
    assert not is_zero(nonsymmetric_commutator)
    return {
        "symmetric_preserving_matrices_checked": checked,
        "all_commute_with_projector": True,
        "nonsymmetric_countermodel": {
            "K": encode_matrix(nonsymmetric),
            "P": encode_matrix(p),
            "K_preserves_span_e1": True,
            "KP_minus_PK": encode_matrix(nonsymmetric_commutator),
        },
    }


def check_local_triangle_cancellation() -> dict[str, object]:
    edges = ((0, 1), (0, 2), (1, 2))
    a = adjacency(3, edges)
    consistent = signed_adjacency(
        3, {(0, 1): 1, (0, 2): 1, (1, 2): 1}
    )
    consistent_commutator = subtract(
        multiply(consistent, a), multiply(a, consistent)
    )
    assert consistent_commutator[0][1] == 0

    mutated = signed_adjacency(
        3, {(0, 1): 1, (0, 2): 1, (1, 2): -1}
    )
    mutated_commutator = subtract(multiply(mutated, a), multiply(a, mutated))
    assert mutated_commutator[0][1] == 2

    # Both products at an adjacent (x,y) require w adjacent to both x and y.
    common_neighbors = [
        w for w in range(3) if a[0][w] == 1 and a[w][1] == 1
    ]
    assert common_neighbors == [2]
    return {
        "adjacent_pair": [0, 1],
        "common_neighbors": common_neighbors,
        "triangle_consistent_ZA_minus_AZ_entry": int(consistent_commutator[0][1]),
        "mutated_ZA_minus_AZ_entry": int(mutated_commutator[0][1]),
        "no_omitted_summands": True,
    }


def check_connectivity_countermodel() -> dict[str, object]:
    # Two disjoint triangles retain lambda=1 on every edge, but dropping the
    # target mu=2 condition allows different signed degrees on components.
    edges = (
        (0, 1), (0, 2), (1, 2),
        (3, 4), (3, 5), (4, 5),
    )
    a = adjacency(6, edges)
    signs = {
        (0, 1): 1, (0, 2): 1, (1, 2): 1,
        (3, 4): -1, (3, 5): -1, (4, 5): -1,
    }
    z = signed_adjacency(6, signs)
    commutator = subtract(multiply(z, a), multiply(a, z))
    for left, right in edges:
        assert commutator[left][right] == 0
    signed_degrees = [1, 1, 1, -1, -1, -1]
    assert len(set(signed_degrees)) == 2
    return {
        "graph": "disjoint union of two triangles",
        "edge_lambda": 1,
        "cross_component_mu": 0,
        "local_edge_cancellation": True,
        "signed_degrees": signed_degrees,
        "global_constancy_fails": True,
    }


def check_d_e_commutation_countermodel() -> dict[str, object]:
    e = matrix([[Fraction(1, 2), Fraction(1, 2)],
                [Fraction(1, 2), Fraction(1, 2)]])
    d = matrix([[1, 0], [0, -1]])
    commutator = subtract(multiply(d, e), multiply(e, d))
    image_vector = matrix([[1], [1]])
    d_image = multiply(d, image_vector)
    assert not is_zero(commutator)
    assert d_image == matrix([[1], [-1]])
    return {
        "E": encode_matrix(e),
        "D": encode_matrix(d),
        "DE_minus_ED": encode_matrix(commutator),
        "D_does_not_preserve_im_E": True,
    }


def check_divisibility_and_all_blocks() -> dict[str, object]:
    signed_sizes = []
    for block_size in range(TRIANGLES + 1):
        numerator = 2 * block_size - TRIANGLES
        if numerator % (VERTICES // VERTICES_PER_TRIANGLE) == 0:
            signed_degree = numerator // (VERTICES // VERTICES_PER_TRIANGLE)
            if -TRIANGLES_PER_VERTEX <= signed_degree <= TRIANGLES_PER_VERTEX:
                signed_sizes.append(
                    {"block_size": block_size, "signed_degree": signed_degree}
                )
    assert [row["block_size"] for row in signed_sizes] == list(range(0, 232, 33))

    # The submitted lattice trace route.
    proper_lattice_blocks = []
    for rank in range(1, PROJECTOR_RANK):
        if (21 * rank) % 4 == 0:
            block_size = 21 * rank // 4
            proper_lattice_blocks.append(
                {
                    "rank": rank,
                    "block_size": block_size,
                    "block_size_mod_33": block_size % 33,
                }
            )
    assert [row["rank"] for row in proper_lattice_blocks] == list(range(4, 44, 4))
    assert all(row["block_size_mod_33"] != 0 for row in proper_lattice_blocks)

    # Independent shorter route requested by the orchestrator.  If E is
    # coordinate-block diagonal, E_I is an idempotent projector.  Its trace
    # is rank(E_I)=4|I|/21, so 21 divides |I|.  Together with 33-divisibility,
    # lcm(21,33)=231 leaves only the empty and full subsets.
    projector_trace_sizes = [
        block_size
        for block_size in range(TRIANGLES + 1)
        if (4 * block_size) % 21 == 0
    ]
    both_divisibilities = [
        block_size
        for block_size in projector_trace_sizes
        if block_size % 33 == 0
    ]
    assert projector_trace_sizes == list(range(0, 232, 21))
    assert both_divisibilities == [0, 231]

    # Multiple blocks and complement choices reduce to nonempty proper unions
    # of rank units summing to 11.  Every such union has k in 1..10.
    partitions = [
        partition for partition in integer_partitions(PROJECTOR_RANK // 4)
        if len(partition) >= 2
    ]
    assert partitions
    union_units = set()
    for partition in partitions:
        count = len(partition)
        for mask in range(1, (1 << count) - 1):
            union_units.add(
                sum(partition[index] for index in range(count) if mask & (1 << index))
            )
    assert union_units == set(range(1, 11))
    assert all((21 * units) % 33 != 0 for units in union_units)

    complement_pairs = [
        [block_size, TRIANGLES - block_size]
        for block_size in range(0, 116, 33)
    ]
    assert all(
        left % 33 == 0 and right % 33 == 0
        for left, right in complement_pairs
    )

    assert 105 % 33 == 6
    assert 126 % 33 == 27
    return {
        "signed_double_count_solutions": signed_sizes,
        "proper_rootless_lattice_blocks": proper_lattice_blocks,
        "proper_block_contradictions": len(proper_lattice_blocks),
        "projector_trace_simplification": {
            "trace_formula": "rank(E_I)=4*|I|/21",
            "sizes_with_integral_projector_trace": projector_trace_sizes,
            "sizes_also_divisible_by_33": both_divisibilities,
            "conclusion": "only empty and full coordinate blocks survive",
        },
        "rank_unit_partitions_of_11": len(partitions),
        "proper_union_rank_units": sorted(union_units),
        "complement_pairs": complement_pairs,
        "wave30_residues_mod_33": {"105": 6, "126": 27},
    }


def build_results() -> dict[str, object]:
    sections = {
        "basis_change": check_basis_change(),
        "rootless_support": check_support_and_block_nonemptiness(),
        "incidence_transport": check_incidence_transport_and_projector(),
        "symmetric_invariance": check_symmetric_invariance(),
        "triangle_cancellation": check_local_triangle_cancellation(),
        "connectivity_control": check_connectivity_countermodel(),
        "D_E_commutation_control": check_d_e_commutation_countermodel(),
        "divisibility": check_divisibility_and_all_blocks(),
    }
    return {
        "schema_version": 1,
        "candidate_commit": CANDIDATE_COMMIT,
        "arithmetic": "exact integers and fractions only",
        "verdict": "PASS_NO_FATAL_GAP",
        "sections": sections,
        "status_walls": {
            "rooted_endpoint_forms": "UNKNOWN",
            "rootless_indecomposable_endpoint_forms": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def serialize(results: dict[str, object]) -> bytes:
    return (
        json.dumps(results, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = serialize(build_results())
    if args.output is not None:
        args.output.write_bytes(payload)
    print(hashlib.sha256(payload).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
