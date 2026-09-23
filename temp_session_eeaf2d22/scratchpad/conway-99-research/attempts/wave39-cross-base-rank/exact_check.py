#!/usr/bin/env python3
"""Exact Wave 39 cross-base ternary-rank checks.

The checker works conditionally at the prism-free endpoint n3=4158 and,
inside that endpoint, at the surviving boundary rank_F3(M)=12 with square
factor-form determinant.  It verifies:

* the determinant classes of the centered eleven-space, a six-dimensional
  vertex-star space, and its five-dimensional orthogonal complement;
* the exact projection profile of the 84 graph triangles adjacent to a
  fixed original vertex;
* the finite-field pigeonhole consequence forcing at least twelve pairs of
  equal projected vectors and hence short factor-row dependencies;
* explicit rank-ten and determinant-compatible rank-eleven tripartite
  quotient controls, refuting a purely local rank-twelve shortcut; and
* a finite quadratic-space positive control showing that the projection
  and collision constraints alone are consistent.

No 231-row endpoint configuration or 99-vertex graph is constructed, and
the endpoint is not excluded.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path


FIELD = 3
TRIANGLES = 231
VERTICES = 99
TRIANGLES_PER_VERTEX = 7
NEIGHBORS_PER_VERTEX = 14
ADJACENT_TRIANGLES_PER_NEIGHBOR = 6
ADJACENT_TRIANGLES = (
    NEIGHBORS_PER_VERTEX * ADJACENT_TRIANGLES_PER_NEIGHBOR
)

ROOT = Path(__file__).resolve().parents[2]
FROZEN_INPUTS = {
    "verification/wave36-ternary-polar-bound/independent-results.json":
        "38ec002886c2a9b38f8d11824dc79e07147b16386dcc3449064633efb630beeb",
    "verification/wave38-higher-order/independent-results.json":
        "c0d56150980fe874ce1fa60eab9423da037400b7dcc17b5593380b2f03b5a0cb",
    "verification/wave38-higher-order/audit.md":
        "d52b331a966339a4102f69c04572ca65eaaffb3dd46570980fedeceb161ddce2",
}

# Each tuple encodes one bipartite block I+P_sigma of a simple
# four-regular tripartite quotient P on parts 6+6+6.
RANK_TEN_QUOTIENT = (
    (5, 0, 1, 2, 3, 4),
    (5, 4, 0, 1, 2, 3),
    (3, 4, 5, 0, 2, 1),
)
RANK_ELEVEN_NONSQUARE_QUOTIENT = (
    (3, 4, 5, 1, 0, 2),
    (1, 0, 5, 4, 3, 2),
    (4, 3, 5, 0, 1, 2),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_inputs() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in FROZEN_INPUTS.items():
        digest = file_sha256(ROOT / relative)
        require(digest == expected, f"frozen input changed: {relative}")
        observed[relative] = digest
    return observed


def dot(left: list[int], right: list[int], gram: list[list[int]]) -> int:
    return sum(
        left[i] * gram[i][j] * right[j]
        for i in range(len(left))
        for j in range(len(right))
    ) % FIELD


def matmul(
    left: list[list[int]], right: list[list[int]]
) -> list[list[int]]:
    if not left:
        return []
    require(right, "right matrix is empty")
    require(len(left[0]) == len(right), "matrix dimensions do not match")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right))) % FIELD
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def rank_mod(matrix: list[list[int]], prime: int = FIELD) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(rank, rows)
                if work[row][column] % prime
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [
            inverse * entry % prime for entry in work[rank]
        ]
        for row in range(rows):
            if row == rank:
                continue
            scale = work[row][column] % prime
            if scale:
                work[row] = [
                    (left - scale * right) % prime
                    for left, right in zip(work[row], work[rank])
                ]
        rank += 1
    return rank


def determinant_mod(
    matrix: list[list[int]], prime: int = FIELD
) -> int:
    require(
        all(len(row) == len(matrix) for row in matrix),
        "determinant requires a square matrix",
    )
    work = [[entry % prime for entry in row] for row in matrix]
    size = len(work)
    determinant = 1
    for column in range(size):
        pivot = next(
            (
                row
                for row in range(column, size)
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        pivot_value = work[column][column] % prime
        determinant = determinant * pivot_value % prime
        inverse = pow(pivot_value, -1, prime)
        for row in range(column + 1, size):
            scale = work[row][column] * inverse % prime
            if scale:
                work[row] = [
                    (left - scale * right) % prime
                    for left, right in zip(work[row], work[column])
                ]
    return determinant % prime


def nonsingular_principal_minor(
    matrix: list[list[int]], rank: int
) -> tuple[int, tuple[int, ...]]:
    """Return determinant and indices of the first nonsingular rank minor."""

    for indices in itertools.combinations(range(len(matrix)), rank):
        principal = [
            [matrix[left][right] for right in indices]
            for left in indices
        ]
        determinant = determinant_mod(principal)
        if determinant:
            return determinant, indices
    raise AssertionError("symmetric matrix has no nonsingular rank minor")


def block_diagonal(*blocks: list[list[int]]) -> list[list[int]]:
    total = sum(len(block) for block in blocks)
    result = [[0] * total for _ in range(total)]
    offset = 0
    for block in blocks:
        for row in range(len(block)):
            for column in range(len(block)):
                result[offset + row][offset + column] = (
                    block[row][column] % FIELD
                )
        offset += len(block)
    return result


def determinant_and_projection_spaces() -> dict[str, object]:
    """Audit the three determinant classes used by the projection theorem."""

    # At r3=12 the independently verified polar argument leaves only a
    # square determinant class.  The common star-sum w has norm two.
    full_dimension = 12
    full_determinant = 1
    common_vector_norm = 2
    centered_dimension = full_dimension - 1
    centered_determinant = (
        full_determinant * pow(common_vector_norm, -1, FIELD)
    ) % FIELD
    require(centered_determinant == 2, "centered determinant class changed")

    star_basis_gram = [
        [0 if row == column else 1 for column in range(6)]
        for row in range(6)
    ]
    star_determinant = determinant_mod(star_basis_gram)
    require(star_determinant == 1, "vertex-star determinant is not square")
    require(rank_mod(star_basis_gram) == 6, "vertex-star rank changed")

    complement_dimension = centered_dimension - 6
    complement_determinant = (
        centered_determinant * pow(star_determinant, -1, FIELD)
    ) % FIELD
    require(complement_dimension == 5, "complement dimension changed")
    require(
        complement_determinant == 2,
        "five-space complement is not nonsquare",
    )
    return {
        "full_factor_space": {
            "dimension": full_dimension,
            "determinant_class": "square",
            "determinant_representative": full_determinant,
        },
        "common_vector": {"norm": common_vector_norm},
        "centered_space": {
            "dimension": centered_dimension,
            "determinant_class": "nonsquare",
            "determinant_representative": centered_determinant,
        },
        "vertex_star_space": {
            "dimension": 6,
            "basis_gram": star_basis_gram,
            "determinant_class": "square",
            "determinant_representative": star_determinant,
        },
        "orthogonal_complement": {
            "dimension": complement_dimension,
            "determinant_class": "nonsquare",
            "determinant_representative": complement_determinant,
        },
    }


def quadratic_vector_counts() -> dict[str, object]:
    """Enumerate the five-dimensional nonsquare form diag(1,1,1,1,2)."""

    diagonal = [1, 1, 1, 1, 2]
    vectors_by_norm: dict[int, list[tuple[int, ...]]] = {
        0: [],
        1: [],
        2: [],
    }
    for vector in itertools.product(range(FIELD), repeat=5):
        norm = sum(
            diagonal[index] * value * value
            for index, value in enumerate(vector)
        ) % FIELD
        vectors_by_norm[norm].append(vector)
    counts = {norm: len(vectors) for norm, vectors in vectors_by_norm.items()}
    require(counts == {0: 81, 1: 72, 2: 90}, "quadratic counts changed")
    projective = {
        0: (counts[0] - 1) // 2,
        1: counts[1] // 2,
        2: counts[2] // 2,
    }
    require(projective == {0: 40, 1: 36, 2: 45}, "projective counts changed")
    return {
        "diagonal": diagonal,
        "vector_counts_by_norm": {str(key): value for key, value in counts.items()},
        "projective_point_counts_by_norm": {
            str(key): value for key, value in projective.items()
        },
        "norm_one_vectors": [list(vector) for vector in vectors_by_norm[1]],
    }


def adjacent_triangle_profile() -> dict[str, object]:
    """Return the exact fixed-vertex profile for an adjacent triangle."""

    require(ADJACENT_TRIANGLES == 84, "adjacent-triangle count changed")

    # For U adjacent to x, the common edge triangle contributes M=0.
    # Each of the other six star triangles has one or two cross edges,
    # hence M=0 or -1.  Their M-sum is (M N^T)[U,x]=-2.
    m_values = [0] * 5 + [-1] * 2
    require(sum(m_values) == -2, "M-star sum changed")
    d_values = [(2 * value + 1) % FIELD for value in m_values]
    require(Counter(d_values) == Counter({1: 5, 2: 2}), "D profile changed")
    projected_norm = sum(value * value for value in d_values) % FIELD
    require(projected_norm == 1, "projected norm changed")

    patterns = [list(pair) for pair in itertools.combinations(range(7), 2)]
    require(len(patterns) == 21, "two-position pattern count changed")
    return {
        "triangles_adjacent_to_fixed_vertex": ADJACENT_TRIANGLES,
        "count_derivation": "14 neighbors times 6 other triangles",
        "M_star_profile": {"0": 5, "-1": 2},
        "D_star_profile": {"1": 5, "2": 2},
        "two_positions": patterns,
        "projected_vector_norm": projected_norm,
    }


def collision_lower_bound(objects: int, bins: int) -> int:
    require(objects >= bins >= 1, "pigeonhole inputs are out of scope")
    # For occupancies n_i, C(n_i,2)>=n_i-1 when n_i>0.
    return objects - bins


def projection_collision_theorem() -> dict[str, object]:
    adjacent = adjacent_triangle_profile()
    counts = quadratic_vector_counts()
    available = counts["vector_counts_by_norm"]["1"]
    forced_pairs = collision_lower_bound(ADJACENT_TRIANGLES, available)
    require(forced_pairs == 12, "collision lower bound changed")
    return {
        "projected_objects": ADJACENT_TRIANGLES,
        "available_oriented_norm_one_vectors": available,
        "forced_equal_projection_pairs_lower_bound": forced_pairs,
        "dependency": (
            "q_U=q_V implies z_U-z_V+sum_i(d_Ui-d_Vi)z_Ti=0"
        ),
        "factor_row_dependency": (
            "The coefficient sum is zero, so the same relation holds "
            "after replacing every z by v=z+w."
        ),
        "support_sizes": [4, 6],
        "pair_classification": {
            "two-position_sets_intersect_in_one": {
                "dependency_support": 4,
                "required_centered_inner_product_D_UV": 1,
            },
            "two-position_sets_are_disjoint": {
                "dependency_support": 6,
                "required_centered_inner_product_D_UV": 2,
            },
            "two-position_sets_equal": {
                "distinct_equal_projections": False,
                "reason": "equal d and equal q determine equal z",
            },
        },
        "adjacent_profile": adjacent,
    }


def build_quotient(
    permutations: tuple[tuple[int, ...], ...]
) -> list[list[int]]:
    require(len(permutations) == 3, "three quotient blocks are required")
    quotient = [[0] * 18 for _ in range(18)]
    for (first, second), permutation in zip(
        ((0, 1), (1, 2), (2, 0)), permutations
    ):
        require(
            sorted(permutation) == list(range(6)),
            "quotient control is not a permutation",
        )
        require(
            all(permutation[index] != index for index in range(6)),
            "quotient permutation is not a derangement",
        )
        for left in range(6):
            for right in (left, permutation[left]):
                a = 6 * first + left
                b = 6 * second + right
                require(quotient[a][b] == 0, "quotient block doubled an edge")
                quotient[a][b] = quotient[b][a] = 1
    require(set(map(sum, quotient)) == {4}, "quotient is not four-regular")
    for first, second in ((0, 1), (1, 2), (2, 0)):
        for row in range(6):
            require(
                sum(
                    quotient[6 * first + row][6 * second + column]
                    for column in range(6)
                ) == 2,
                "quotient block is not two-regular",
            )
    return quotient


def quotient_control(
    name: str,
    permutations: tuple[tuple[int, ...], ...],
    expected_rank: int,
    expected_discriminant: int,
) -> dict[str, object]:
    quotient = build_quotient(permutations)
    shifted = [
        [
            (quotient[row][column] - int(row == column)) % FIELD
            for column in range(18)
        ]
        for row in range(18)
    ]
    rank = rank_mod(shifted)
    require(rank == expected_rank, f"{name} rank changed")
    determinant, indices = nonsingular_principal_minor(shifted, rank)
    require(
        determinant == expected_discriminant,
        f"{name} discriminant changed",
    )
    return {
        "name": name,
        "permutations": [list(permutation) for permutation in permutations],
        "rank_F3_P_minus_I": rank,
        "discriminant_representative": determinant,
        "discriminant_class": (
            "square" if determinant == 1 else "nonsquare"
        ),
        "witness_principal_indices": list(indices),
        "vertices": 18,
        "parts": [6, 6, 6],
        "degree": 4,
        "bipartite_block_degree": 2,
        "simple": True,
    }


def local_rank_controls() -> dict[str, object]:
    rank_ten = quotient_control(
        "rank-ten-local-control",
        RANK_TEN_QUOTIENT,
        expected_rank=10,
        expected_discriminant=2,
    )
    rank_eleven = quotient_control(
        "rank-eleven-nonsquare-local-control",
        RANK_ELEVEN_NONSQUARE_QUOTIENT,
        expected_rank=11,
        expected_discriminant=2,
    )
    return {
        "controls": [rank_ten, rank_eleven],
        "refuted_local_claim": (
            "Every simple tripartite four-regular P with two-regular "
            "bipartite blocks has rank_F3(P-I)>=12."
        ),
        "determinant_compatible_rank_eleven_exists": True,
        "scope": (
            "These are quotient matrices only, not 36-vertex cores, "
            "simultaneous B/H completions, endpoint matrices, or graphs."
        ),
    }


def star_vectors() -> tuple[list[list[int]], list[list[int]]]:
    star_gram = [
        [0 if row == column else 1 for column in range(6)]
        for row in range(6)
    ]
    vectors = [
        [int(row == column) for column in range(6)]
        for row in range(6)
    ]
    vectors.append([2] * 6)
    require(
        all(
            dot(vectors[left], vectors[right], star_gram)
            == (0 if left == right else 1)
            for left in range(7)
            for right in range(7)
        ),
        "seven-vector simplex Gram changed",
    )
    require(
        all(sum(vector[column] for vector in vectors) % FIELD == 0
            for column in range(6)),
        "seven-vector simplex lost its sum relation",
    )
    return star_gram, vectors


def projection_positive_control() -> dict[str, object]:
    """Build a finite model of the projection and collision constraints."""

    star_gram, stars = star_vectors()
    k_gram = [
        [0] * row + [value] + [0] * (4 - row)
        for row, value in enumerate([1, 1, 1, 1, 2])
    ]
    w_gram = block_diagonal(star_gram, k_gram)
    require(determinant_mod(w_gram) == 2, "control W determinant changed")

    norm_one = [
        list(vector)
        for vector in itertools.product(range(FIELD), repeat=5)
        if dot(list(vector), list(vector), k_gram) == 1
    ]
    require(len(norm_one) == 72, "control norm-one list changed")
    patterns = list(itertools.combinations(range(7), 2))

    assignments: list[tuple[list[int], tuple[int, int]]] = []
    for index, q_vector in enumerate(norm_one):
        assignments.append((q_vector, patterns[index % len(patterns)]))
    for index in range(12):
        original_pattern = patterns[index % len(patterns)]
        shifted_pattern = patterns[(index + 1) % len(patterns)]
        require(shifted_pattern != original_pattern, "pattern shift failed")
        assignments.append((norm_one[index], shifted_pattern))
    require(len(assignments) == 84, "control assignment count changed")

    adjacent_vectors: list[list[int]] = []
    d_vectors: list[list[int]] = []
    q_vectors: list[list[int]] = []
    for q_vector, pattern in assignments:
        d_vector = [1] * 7
        for index in pattern:
            d_vector[index] = 2
        projection = [
            -sum(
                d_vector[index] * stars[index][coordinate]
                for index in range(7)
            ) % FIELD
            for coordinate in range(6)
        ]
        z_vector = projection + q_vector
        require(dot(projection, projection, star_gram) == 2,
                "projection norm changed")
        require(dot(q_vector, q_vector, k_gram) == 1,
                "complement norm changed")
        require(dot(z_vector, z_vector, w_gram) == 0,
                "adjacent z vector is not isotropic")
        observed_d = [
            dot(star + [0] * 5, z_vector, w_gram)
            for star in stars
        ]
        require(observed_d == d_vector, "star inner profile changed")
        adjacent_vectors.append(z_vector)
        d_vectors.append(d_vector)
        q_vectors.append(q_vector)

    require(
        len({tuple(vector) for vector in adjacent_vectors}) == 84,
        "positive-control adjacent vectors are not distinct",
    )
    q_occupancy = Counter(map(tuple, q_vectors))
    collision_pairs = sum(
        multiplicity * (multiplicity - 1) // 2
        for multiplicity in q_occupancy.values()
    )
    require(collision_pairs == 12, "positive-control collision count changed")
    require(max(q_occupancy.values()) == 2, "unexpected q multiplicity")

    relation_support_histogram: Counter[int] = Counter()
    relation_type_histogram: Counter[str] = Counter()
    for first in range(72):
        second = 72 + first
        if first >= 12:
            break
        require(q_vectors[first] == q_vectors[second], "frozen q pair changed")
        coefficients = [0] * (2 + 7)
        coefficients[0] = 1
        coefficients[1] = 2
        for index in range(7):
            coefficients[2 + index] = (
                d_vectors[first][index] - d_vectors[second][index]
            ) % FIELD
        relation_vectors = [
            adjacent_vectors[first],
            adjacent_vectors[second],
            *[star + [0] * 5 for star in stars],
        ]
        relation = [
            sum(
                coefficients[index] * relation_vectors[index][coordinate]
                for index in range(len(relation_vectors))
            ) % FIELD
            for coordinate in range(11)
        ]
        require(relation == [0] * 11, "short dependency failed")
        support = sum(coefficient != 0 for coefficient in coefficients)
        require(support in (4, 6), "dependency support changed")
        relation_support_histogram[support] += 1

        first_pattern = {
            index for index, value in enumerate(d_vectors[first]) if value == 2
        }
        second_pattern = {
            index for index, value in enumerate(d_vectors[second]) if value == 2
        }
        overlap = len(first_pattern & second_pattern)
        q_inner = dot(q_vectors[first], q_vectors[second], k_gram)
        p_inner = (
            dot(
                adjacent_vectors[first][:6],
                adjacent_vectors[second][:6],
                star_gram,
            )
        )
        d_inner = sum(
            left * right
            for left, right in zip(d_vectors[first], d_vectors[second])
        ) % FIELD
        require(p_inner == (-d_inner) % FIELD, "projection inner product changed")
        d_uv = dot(
            adjacent_vectors[first],
            adjacent_vectors[second],
            w_gram,
        )
        require((d_uv + d_inner) % FIELD == q_inner == 1,
                "collision pair identity changed")
        expected = 1 if overlap == 1 else 2
        require(d_uv == expected, "collision pair D-class changed")
        relation_type_histogram[
            "overlap-one" if overlap == 1 else "disjoint"
        ] += 1

    combined = [star + [0] * 5 for star in stars] + adjacent_vectors
    require(rank_mod(combined) == 11, "positive control does not span W")
    combined_gram = matmul(matmul(combined, w_gram), transpose(combined))
    require(rank_mod(combined_gram) == 11, "positive-control Gram rank changed")
    return {
        "ambient_centered_space": {
            "dimension": 11,
            "determinant_representative": 2,
        },
        "vertex_star_vectors": 7,
        "adjacent_isotropic_vectors": 84,
        "distinct_adjacent_vectors": 84,
        "norm_one_projection_values_available": 72,
        "distinct_projection_values_used": 72,
        "equal_projection_pair_count": collision_pairs,
        "maximum_projection_multiplicity": max(q_occupancy.values()),
        "short_dependency_support_histogram": {
            str(key): value
            for key, value in sorted(relation_support_histogram.items())
        },
        "collision_pattern_histogram": dict(sorted(relation_type_histogram.items())),
        "combined_vector_rank": rank_mod(combined),
        "combined_gram_rank": rank_mod(combined_gram),
        "interpretation": (
            "Finite quadratic-space control for the projection theorem only; "
            "it omits the remaining 140 triangles, V^T V=0, the full D "
            "alphabet/incidence equations, every simultaneous base, and a graph."
        ),
    }


def build_results() -> dict[str, object]:
    return {
        "format": "wave39-cross-base-rank-v1",
        "claim_label": "DERIVED_INCONCLUSIVE",
        "frozen_public_head": "019b78ac9a5170107d105ad4d8fcd27f55dde642",
        "scope": (
            "Conditional prism-free endpoint n3=4158 and the surviving "
            "rank_F3(M)=12 square determinant boundary"
        ),
        "inputs": audit_inputs(),
        "space_determinants": determinant_and_projection_spaces(),
        "projection_collision_theorem": projection_collision_theorem(),
        "local_rank_controls": local_rank_controls(),
        "projection_positive_control": projection_positive_control(),
        "conclusion": {
            "new_exact_cross_base_restriction": (
                "For every original vertex x, the 84 adjacent graph "
                "triangles force at least 12 equal-projection pairs and "
                "therefore at least 12 explicit support-4-or-6 factor-row "
                "dependencies of the displayed star form."
            ),
            "universal_local_rank_twelve_claim": "REFUTED_BY_QUOTIENT_CONTROLS",
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "strongest_general_upper_bound_on_n3": 4158,
            "target_status": "UNKNOWN",
            "next_exact_target": (
                "Classify the forced support-4/6 dependencies against the "
                "full triangle-incidence relations, or prove that their "
                "required multiplicity across all 99 vertex stars is impossible."
            ),
        },
        "limitations": [
            "All statements are conditional on the endpoint and r3=12 boundary.",
            "The collision theorem is a necessary condition, not a contradiction.",
            "Collision pairs counted at different vertex stars may overlap.",
            "The quotient controls are not full one-triangle cores or graphs.",
            "The projection positive control omits the global frame and incidence equations.",
            "No endpoint matrix, Conway graph, upper-bound improvement, or novelty claim is supplied.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    encoded = canonical_bytes(build_results())
    if arguments.verify is not None:
        if arguments.verify.read_bytes() != encoded:
            print(f"FAIL: {arguments.verify} differs", file=sys.stderr)
            return 1
        print(f"PASS: {arguments.verify} matches exact regeneration")
        return 0
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_bytes(encoded)
        print(arguments.output)
        return 0
    sys.stdout.buffer.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
