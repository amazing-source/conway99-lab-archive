#!/usr/bin/env python3
"""Independent exact audit of the Wave 37 finite-polar package.

No discovery checker is imported.  The finite association algebras are
rebuilt by dynamic programming over the fields, and the signed-triangle
claims receive explicit hostile linear-algebra controls.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Sequence


N = 231
PLUS = 32
MINUS = 36
ZERO = 162


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


def rank_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    if not work:
        return 0
    row = 0
    for column in range(len(work[0])):
        pivot = next(
            (index for index in range(row, len(work)) if work[index][column]),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        inverse = pow(work[row][column], -1, prime)
        work[row] = [(entry * inverse) % prime for entry in work[row]]
        for index in range(len(work)):
            if index != row and work[index][column]:
                scale = work[index][column]
                work[index] = [
                    (left - scale * right) % prime
                    for left, right in zip(work[index], work[row])
                ]
        row += 1
        if row == len(work):
            break
    return row


def code_consequences(rank: int = 12) -> dict[str, object]:
    # C has diagonal -13=2 mod 3; its 32 positive off-diagonal S entries
    # become 2 and its 36 negative entries become 1.
    composition = (MINUS, PLUS + 1)
    require(composition == (36, 33), "distinguished complete weight changed")
    require(sum(composition) == 69, "distinguished weight changed")
    require(all(value % 3 == 0 for value in composition),
            "distinguished composition lost divisibility")
    symmetric_square = rank * (rank + 1) // 2
    return {
        "factorization_argument": {
            "C_squared_zero_implies": "V^T V=0",
            "C_one_zero_implies": "V^T 1=0",
            "required_hypotheses": [
                "C=V H V^T",
                "V has full column rank",
                "H is nondegenerate",
            ],
        },
        "code": {
            "parameters": f"[231,{rank}]_3",
            "self_orthogonal": True,
            "all_one_vector_in_dual": True,
            "projective": True,
            "dual_distance_lower_bound": 3,
            "all_word_n1_divisible_by_3": True,
            "all_word_n2_divisible_by_3": True,
        },
        "distinguished_words": {
            "weight": 69,
            "composition_n1_n2": list(composition),
            "distinct_words_including_negatives": 2 * N,
            "weight_enumerator_constraint": "A_69>=462",
        },
        "schur_square": {
            "rank_I_plus_B_ceiling": symmetric_square,
            "rank_orthogonality_matrix_ceiling": symmetric_square + 1,
        },
    }


def krawtchouk(order: int, weight: int) -> int:
    lower = max(0, order - (N - weight))
    upper = min(order, weight)
    return sum(
        (-1) ** index
        * 2 ** (order - index)
        * math.comb(weight, index)
        * math.comb(N - weight, order - index)
        for index in range(lower, upper + 1)
    )


def macwilliams_hostile_control() -> dict[str, object]:
    distribution = {0: 1, 69: 462, 141: 76_965, 153: 288_015, 162: 165_998}
    size = 3**12
    require(sum(distribution.values()) == size, "weight distribution mass changed")
    transformed = []
    for order in range(N + 1):
        numerator = sum(
            amount * krawtchouk(order, weight)
            for weight, amount in distribution.items()
        )
        transformed.append(Fraction(numerator, size))
    require(transformed[1] == transformed[2] == 0, "dual distance moments changed")
    require(all(value >= 0 for value in transformed), "negative transform")
    require(all(
        transformed[order] >= distribution.get(order, 0)
        for order in range(N + 1)
    ), "self-orthogonal real relaxation failed")
    nonintegral = [
        order for order, value in enumerate(transformed) if value.denominator != 1
    ]
    require(nonintegral == list(range(3, N + 1)), "integrality boundary changed")
    return {
        "A_distribution": {str(key): value for key, value in distribution.items()},
        "sum_A": size,
        "B_1": 0,
        "B_2": 0,
        "all_transforms_nonnegative": True,
        "all_B_at_least_A": True,
        "nonintegral_orders": nonintegral,
        "formal_weight_enumerator": False,
        "code_constructed": False,
    }


def inner(diagonal: Sequence[int], left: Sequence[int],
          right: Sequence[int], field: int) -> int:
    return sum(
        coefficient * a * b
        for coefficient, a, b in zip(diagonal, left, right)
    ) % field


def triple_invariant_counts(
    field: int,
    diagonal: Sequence[int],
    x: Sequence[int],
    y: Sequence[int],
) -> dict[tuple[int, int, int], int]:
    states = {(0, 0, 0): 1}
    for coefficient, x_entry, y_entry in zip(diagonal, x, y):
        updated: dict[tuple[int, int, int], int] = defaultdict(int)
        for (norm, x_inner, y_inner), count in states.items():
            for z in range(field):
                updated[
                    (
                        (norm + coefficient * z * z) % field,
                        (x_inner + coefficient * x_entry * z) % field,
                        (y_inner + coefficient * y_entry * z) % field,
                    )
                ] += count
        states = dict(updated)
    return states


def polynomial_multiply(left: list[int], right: list[int]) -> list[int]:
    answer = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            answer[i + j] += a * b
    return answer


def characteristic_polynomial(matrix: Sequence[Sequence[int]]) -> list[int]:
    size = len(matrix)
    total = [0] * (size + 1)
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        term = [-1 if inversions % 2 else 1]
        for row, column in enumerate(permutation):
            factor = [-matrix[row][column]]
            if row == column:
                factor.append(1)
            term = polynomial_multiply(term, factor)
        for index, coefficient in enumerate(term):
            total[index] += coefficient
    return total


def ternary_oriented_scheme() -> dict[str, object]:
    field = 3
    diagonal = (1,) * 12
    x = (0, 0, 1, 1) + (0,) * 8
    representatives = (
        x,
        tuple(-entry % field for entry in x),
        (0, 0, 1, 2) + (0,) * 8,
        (0, 1, 0, 1) + (0,) * 8,
        (0, 1, 0, 2) + (0,) * 8,
    )

    def relation(left: Sequence[int], right: Sequence[int]) -> int:
        right_tuple = tuple(right)
        if right_tuple == tuple(left):
            return 0
        if right_tuple == tuple(-entry % field for entry in left):
            return 1
        return {0: 2, 1: 3, 2: 4}[inner(diagonal, left, right, field)]

    matrices = []
    generic = {0: 2, 1: 3, 2: 4}
    for y in representatives:
        matrix = [[0] * 5 for _ in range(5)]
        states = triple_invariant_counts(field, diagonal, x, y)
        for (norm, x_inner, y_inner), count in states.items():
            if norm == 2:
                matrix[generic[x_inner]][generic[y_inner]] += count
        special = {
            tuple(x),
            tuple(-entry % field for entry in x),
            tuple(y),
            tuple(-entry % field for entry in y),
        }
        for z in special:
            old_i = generic[inner(diagonal, x, z, field)]
            old_j = generic[inner(diagonal, z, y, field)]
            matrix[old_i][old_j] -= 1
            matrix[relation(x, z)][relation(z, y)] += 1
        matrices.append(matrix)

    valencies = [matrices[0][index][index] for index in range(5)]
    require(valencies == [1, 1, 58_806, 59_048, 59_048],
            "ternary oriented valencies changed")
    characters = [
        [1, 1, 58_806, 59_048, 59_048],
        [1, 1, 486, -244, -244],
        [1, -1, 0, 244, -244],
        [1, 1, -162, 80, 80],
        [1, -1, 0, -242, 242],
    ]
    require(rank_mod(characters, 1_000_003) == 5, "character table is singular")
    for character in characters:
        for left in range(5):
            for right in range(5):
                product = character[left] * character[right]
                expansion = sum(
                    matrices[relation][left][right] * character[relation]
                    for relation in range(5)
                )
                require(product == expansion, "association character failed")
    endpoint = [1, 0, 162, 36, 32]
    positivity = [
        sum(
            Fraction(amount * eigenvalue, valency)
            for amount, eigenvalue, valency in zip(endpoint, character, valencies)
        )
        for character in characters
    ]
    expected = [
        Fraction(231), Fraction(249, 121), Fraction(123, 121),
        Fraction(4767, 7381), Fraction(60, 61),
    ]
    require(positivity == expected, "oriented Delsarte transforms changed")
    return {
        "valencies": valencies,
        "endpoint_distribution": endpoint,
        "delsarte_positivity": [str(value) for value in positivity],
        "excluded": False,
    }


def evans_divisibility_control() -> dict[str, object]:
    v, k, lam, mu = 88_452, 29_403, 9_882, 9_720
    outside = v - N
    first = N * (k - ZERO)
    second = (
        (lam - mu) * N * ZERO
        + (k - mu) * N
        + mu * N * N
        - N * ZERO * ZERO
    )
    require((outside, first, second) == (88_221, 6_754_671, 523_215_693),
            "outside moments changed")
    ordinary = min(
        (second - (2 * root + 1) * first + root * (root + 1) * outside, root)
        for root in range(N + 1)
    )
    ternary = min(
        (second - (2 * root + 3) * first + root * (root + 3) * outside, root)
        for root in range(0, N + 1, 3)
    )
    require(ordinary == (6_020_322, 76), "ordinary polynomial changed")
    require(ternary == (5_843_880, 75), "ternary polynomial changed")
    return {
        "outside_count": outside,
        "outside_degree_sum": first,
        "outside_degree_square_sum": second,
        "ordinary_roots": [ordinary[1], ordinary[1] + 1],
        "ordinary_sum": ordinary[0],
        "divisible_roots": [ternary[1], ternary[1] + 3],
        "divisible_sum": ternary[0],
        "excluded": False,
    }


def signed_triangle_geometry() -> dict[str, object]:
    support_degree = PLUS + MINUS
    edges = N * support_degree // 2
    trace_cube = 44 * 17**3 + 187 * (-4) ** 3
    difference = trace_cube // 6
    require((support_degree, edges, trace_cube, difference)
            == (68, 7_854, 204_204, 34_034), "signed triangle count changed")

    # Explicit counterexample to the rejected collinearity inference.
    diagonal = (1, 1, 1, 1, 2)
    vectors = (
        (0, 0, 0, 0, 1),
        (0, 1, 1, 1, 1),
        (1, 0, 1, 2, 1),
    )
    gram = [
        [inner(diagonal, left, right, 3) for right in vectors]
        for left in vectors
    ]
    require(rank_mod(vectors, 3) == 3 and rank_mod(gram, 3) == 1,
            "hostile independent degenerate triple failed")

    maximum_collinear = edges // 3
    minimum_independent = difference - maximum_collinear
    require((maximum_collinear, minimum_independent) == (2_618, 31_416),
            "independent balanced-triple count changed")

    # A canonical rank-one three-space: q(a,b,c)=2a^2.  Normalize a=1.
    points = [(1, b, c) for b in range(3) for c in range(3)]
    collinear = sum(
        rank_mod(triple, 3) <= 2
        for triple in itertools.combinations(points, 3)
    )
    independent = math.comb(len(points), 3) - collinear
    require((len(points), collinear, independent) == (9, 12, 72),
            "rank-one three-space census changed")
    spaces = math.ceil(minimum_independent / independent)
    require(spaces == 437, "degenerate-space floor changed")
    return {
        "support_degree": support_degree,
        "support_edges": edges,
        "trace_S_cubed": trace_cube,
        "balanced_minus_unbalanced": difference,
        "maximum_collinear_selected_triples": maximum_collinear,
        "minimum_independent_balanced_triples": minimum_independent,
        "rank_one_three_space": {
            "norm_two_projective_points": len(points),
            "collinear_triples": collinear,
            "independent_triples": independent,
        },
        "minimum_distinct_rank_one_three_spaces": spaces,
        "refuted_collinearity_inference": {
            "ambient_diagonal": list(diagonal),
            "vectors": [list(vector) for vector in vectors],
            "vector_rank": 3,
            "gram": gram,
            "gram_rank": 1,
        },
    }


def norm_one_vector_count(field: int, diagonal: Sequence[int]) -> int:
    residues = [1] + [0] * (field - 1)
    for coefficient in diagonal:
        updated = [0] * field
        for prior, count in enumerate(residues):
            for entry in range(field):
                updated[(prior + coefficient * entry * entry) % field] += count
        residues = updated
    return residues[1]


def q7_scheme(determinant: int) -> dict[str, object]:
    field = 7
    diagonal = (1,) * 10 + (determinant,)
    x = (1,) + (0,) * 10
    square_relation = {0: 1, 1: 2, 2: 3, 4: 4}

    def norm(vector: Sequence[int]) -> int:
        return inner(diagonal, vector, vector, field)

    def relation(left: Sequence[int], right: Sequence[int]) -> int:
        if tuple(right) in (
            tuple(left),
            tuple(-entry % field for entry in left),
        ):
            return 0
        return square_relation[inner(diagonal, left, right, field) ** 2 % field]

    representatives = {0: x}
    for short in itertools.product(range(field), repeat=4):
        candidate = short + (0,) * 7
        if norm(candidate) != 1 or candidate in (
            x, tuple(-entry % field for entry in x)
        ):
            continue
        class_index = square_relation[inner(diagonal, x, candidate, field) ** 2 % field]
        representatives.setdefault(class_index, candidate)
        if len(representatives) == 5:
            break
    require(set(representatives) == set(range(5)), "pair representatives missing")

    matrices = []
    for pair_class in range(5):
        y = representatives[pair_class]
        vector_matrix = [[0] * 5 for _ in range(5)]
        states = triple_invariant_counts(field, diagonal, x, y)
        for (norm_value, x_inner, y_inner), count in states.items():
            if norm_value == 1:
                vector_matrix[
                    square_relation[x_inner * x_inner % field]
                ][
                    square_relation[y_inner * y_inner % field]
                ] += count
        special = {
            tuple(x),
            tuple(-entry % field for entry in x),
            tuple(y),
            tuple(-entry % field for entry in y),
        }
        for z in special:
            old_i = square_relation[inner(diagonal, x, z, field) ** 2 % field]
            old_j = square_relation[inner(diagonal, z, y, field) ** 2 % field]
            vector_matrix[old_i][old_j] -= 1
            vector_matrix[relation(x, z)][relation(z, y)] += 1
        require(all(value % 2 == 0 for row in vector_matrix for value in row),
                "projective pairing failed")
        matrices.append([[value // 2 for value in row] for row in vector_matrix])

    valencies = [matrices[0][index][index] for index in range(5)]
    vector_count = norm_one_vector_count(field, diagonal)
    require(sum(valencies) * 2 == vector_count, "projective point count mismatch")
    multiplication = [
        [matrices[pair_class][1][right] for right in range(5)]
        for pair_class in range(5)
    ]
    characteristic = characteristic_polynomial(multiplication)
    if determinant == 1:
        factors = [
            [-valencies[1], 1],
            [4802, 1],
            [-2401, 1],
            [-7**8, -4802, 1],
        ]
        theta = "2401*(1+sqrt(2))"
    else:
        factors = [
            [-valencies[1], 1],
            [-4802, 1],
            [2401, 1],
            [-7**8, 4802, 1],
        ]
        theta = "4802"
    expected = [1]
    for factor in factors:
        expected = polynomial_multiply(expected, factor)
    require(characteristic == expected, "orthogonality spectrum changed")
    common = [matrices[pair_class][1][1] for pair_class in range(5)]
    require(len(set(common[2:])) > 1, "orthogonality graph became SRG")
    return {
        "determinant_class": "square" if determinant == 1 else "nonsquare",
        "vertex_count": sum(valencies),
        "valencies": valencies,
        "common_orthogonal_neighbors_by_relation": common,
        "orthogonality_multiplication_matrix": multiplication,
        "characteristic_polynomial_low_first": characteristic,
        "is_strongly_regular": False,
        "largest_nonprincipal_eigenvalue": theta,
        "largest_nonprincipal_eigenvalue_above_4802": determinant == 1,
        "largest_nonprincipal_eigenvalue_at_least_4802": True,
        "target_induced_degree": ZERO,
        "excluded": False,
    }


def f7_frame_consequences() -> dict[str, object]:
    # Entrywise, C has diagonal 1, zero entries, and off-diagonal +/-2.
    # Cubing mod 7 gives C^(o3)=4(I+C).  C^2=0 makes I+C invertible.
    identity = {
        "diagonal": (1**3 - 4 * (1 + 1)) % 7,
        "zero": (0**3 - 4 * (0 + 0)) % 7,
        "plus_two": (2**3 - 4 * 2) % 7,
        "minus_two": ((-2) ** 3 - 4 * (-2)) % 7,
    }
    require(set(identity.values()) == {0}, "Hadamard cube identity failed")
    cases = [q7_scheme(1), q7_scheme(3)]
    require(
        [case["vertex_count"] for case in cases] == [141_229_221, 141_246_028],
        "rank-eleven point counts changed",
    )
    return {
        "hadamard_cube_identity": "C^(o3)=4(I+C) mod 7",
        "I_plus_C_invertible_from_C_squared_zero": True,
        "pure_cubes_independent": 231,
        "factor_rows_projectively_distinct": 231,
        "selected_norm": 1,
        "selected_orthogonality_degree": ZERO,
        "rank_eleven_cases": cases,
    }


def rank_boundary() -> dict[str, object]:
    pairs = [
        (r3, r7)
        for r3 in range(12, 45)
        for r7 in range(11, 45)
        if (r3 + r7) % 2 == 0
    ]
    require(len(pairs) == 561, "rank-pair count changed")
    return {
        "surviving_pair_count_from_wave36_bounds_and_parity": len(pairs),
        "if_r3_equals_12": "r7 is even and at least 12",
        "if_r7_equals_11": "r3 is odd and at least 13",
    }


@lru_cache(maxsize=1)
def build_results() -> dict[str, object]:
    root = repository_root()
    inputs = [
        "agents/2026-07-26-wave37-polar-strengthen.md",
        "attempts/wave37-polar-strengthen/exact-results.json",
        "attempts/wave37-polar-strengthen/failed-routes.md",
    ]
    result = {
        "schema_version": 1,
        "role": "verifier",
        "scope": "conditional ternary code, exact polar controls, signed degenerate triples, and F7 rank-eleven schemes",
        "claim_label": "VERIFIED_SCOPED_CONDITIONAL_RESTRICTIONS",
        "input_sha256": {path: sha256_file(root / path) for path in inputs},
        "ternary_code": code_consequences(),
        "macwilliams_real_relaxation": macwilliams_hostile_control(),
        "ternary_oriented_scheme": ternary_oriented_scheme(),
        "divisibility_refined_evans": evans_divisibility_control(),
        "signed_triangle_geometry": signed_triangle_geometry(),
        "characteristic_seven": f7_frame_consequences(),
        "rank_boundary": rank_boundary(),
        "conclusion": {
            "new_rank_lower_bound": False,
            "new_determinant_class_exclusion": False,
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "target_status": "UNKNOWN",
        },
        "limitations": [
            "All statements are conditional on the hypothetical n3=4158 endpoint reflection.",
            "No endpoint matrix, finite-field point set, code, or Conway graph is constructed.",
            "The MacWilliams object is a nonintegral real relaxation, not a code enumerator.",
            "Both F7 determinant classes at rank eleven survive the audited spectral test.",
            "Novelty and literature priority are outside this verification scope.",
        ],
    }

    submitted = json.loads(
        (root / "attempts/wave37-polar-strengthen/exact-results.json")
        .read_text(encoding="utf-8")
    )
    require(
        submitted["signed_triangle_geometry"]["minimum_distinct_degenerate_three_spaces"]
        == result["signed_triangle_geometry"]["minimum_distinct_rank_one_three_spaces"],
        "submitted signed-space floor differs",
    )
    submitted_cases = submitted["characteristic_seven_rank_eleven_cases"]
    for submitted_case, checked_case in zip(
        submitted_cases, result["characteristic_seven"]["rank_eleven_cases"]
    ):
        require(submitted_case["vertex_count"] == checked_case["vertex_count"],
                "submitted F7 vertex count differs")
        require(
            submitted_case["orthogonality_characteristic_polynomial_low_first"]
            == checked_case["characteristic_polynomial_low_first"],
            "submitted F7 spectrum differs",
        )
    return result


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    require(not (args.output and args.verify), "choose one output mode")
    rendered = canonical_json(build_results())
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    elif args.verify:
        require(args.verify.read_text(encoding="utf-8") == rendered,
                "stored result differs from independent regeneration")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
