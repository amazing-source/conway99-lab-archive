#!/usr/bin/env python3
"""Exact Wave 39 checks for simultaneous B/H endpoint consequences.

This discovery-side checker has two independent parts.

1. It strengthens the characteristic-three equality case ``r3=12`` by
   centering the 231 triangle rows.  The centered rows are shown to be 231
   distinct isotropic projective points in a nonsquare 11-space.  The full
   five-relation oriented polar scheme is reconstructed exactly.
2. It derives overlap and triangle-decomposition consequences that require
   a *simultaneous* 60-column B and compatible 60-vertex H, not merely the
   individual-column cut used in Wave 38.

Neither part excludes the endpoint.  In particular, all Delsarte transforms
of the centered endpoint distribution are nonnegative.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Sequence


FIELD = 3
TRIANGLE_COUNT = 231
ORIGINAL_VERTICES = 99
ORIGINAL_DEGREE = 14
ENDPOINT_PLUS = 32
ENDPOINT_MINUS = 36
ENDPOINT_ZERO = 162
REFLECTION_ROW_NORM = 441
REFLECTION_ROW_SUM = -21
CORE_SIZE = 36
FIBRE_SIZE = 12
Y_SIZE = 60

FROZEN_COMMIT = "019b78ac9a5170107d105ad4d8fcd27f55dde642"

INPUT_HASHES = {
    "attempts/wave38-higher-order/exact-results.json":
        "7d3229234e5eda3f432ff88eb07670a18611b37a64ef3a7949f4a505f274c782",
    "verification/wave38-higher-order/independent-results.json":
        "c0d56150980fe874ce1fa60eab9423da037400b7dcc17b5593380b2f03b5a0cb",
    "attempts/wave36-block-compatibility/exact-results.json":
        "adab814da773e5a4ce2b98b4b8aa20027dbec9d93d446d3e1e85adaa899339a9",
    "verification/wave36-block-compatibility/independent-results.json":
        "b92ee5cde6a63ba3cce09bc2eae1518979aea09c4f5db39789b65f117b0768c4",
}

# The independently checked Wave 38 rank-ten local control.  It is used only
# as a finite positive control for the B/H counting formulas.
FROZEN_CORE_ROWS_HEX = (
    "800080002",
    "80001001",
    "1004008",
    "100020004",
    "200002020",
    "2800010",
    "40100080",
    "400010040",
    "4040200",
    "10400100",
    "20200800",
    "8008400",
    "2002002",
    "400001010",
    "200008004",
    "20004800",
    "1020080",
    "800010008",
    "8080100",
    "40040001",
    "80200040",
    "4100400",
    "100800200",
    "10400020",
    "2010004",
    "1001020",
    "8200100",
    "4040800",
    "20800200",
    "10008400",
    "80080040",
    "40100002",
    "200400008",
    "100004010",
    "800002080",
    "400020001",
)


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


def rank_mod(matrix: Sequence[Sequence[int]], prime: int = FIELD) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(rank, rows)
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [
            inverse * entry % prime
            for entry in work[rank]
        ]
        for row in range(rows):
            if row == rank or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                (left - scale * right) % prime
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
    return rank


def centered_projective_boundary() -> dict[str, object]:
    """Audit projective distinctness and determinant class at r3=12."""

    require(
        1 + ENDPOINT_PLUS + ENDPOINT_MINUS + ENDPOINT_ZERO
        == TRIANGLE_COUNT,
        "endpoint row profile changed",
    )

    # If z_i=z_j, then D_i=D_j modulo three.  The distinct off-diagonal
    # alphabet residues make C_i-C_j exactly -15(e_i-e_j), of norm 450.
    equal_candidate_norm = 2 * 15**2
    true_sum_or_difference_norm = 2 * REFLECTION_ROW_NORM
    require(
        equal_candidate_norm == 450
        and true_sum_or_difference_norm == 882,
        "equal-row norm audit changed",
    )
    require(
        equal_candidate_norm != true_sum_or_difference_norm,
        "equal centered rows were not rejected",
    )

    # If z_i=-z_j, then D_i=-D_j.  First C_ij=+2.  At each of the other
    # 229 coordinates the pair of C entries is either (+2,+2) or one
    # (-2,0) in either order.  The combined row sum forces 73 coordinates
    # of the first kind.
    other_coordinates = TRIANGLE_COUNT - 2
    antipodal_double_plus = (
        2 * REFLECTION_ROW_SUM
        - 2 * (-13 + 2)
        + 2 * other_coordinates
    ) // 6
    require(
        antipodal_double_plus == 73,
        "antipodal double-plus count changed",
    )
    antipodal_mixed = other_coordinates - antipodal_double_plus
    forced_antipodal_norm = (
        2 * (-13 + 2) ** 2
        + antipodal_double_plus * (2 + 2) ** 2
        + antipodal_mixed * (-2) ** 2
    )
    require(
        forced_antipodal_norm == 2_034,
        "antipodal direct norm changed",
    )
    require(
        forced_antipodal_norm != true_sum_or_difference_norm,
        "antipodal centered rows were not rejected",
    )

    # A zero centered row would require all 230 off-diagonal C entries to
    # equal +2 modulo three, contradicting the exact count 32.
    require(
        ENDPOINT_PLUS < TRIANGLE_COUNT - 1,
        "zero centered row was not rejected",
    )

    # The ambient rank-12 form has square determinant and the common vector
    # w has norm two.  Orthogonal direct sum gives
    # det(w-perp)=det(H)/2, hence the 11-space is nonsquare over F_3.
    return {
        "conditional_boundary": "rank_F3(C)=12 with square determinant class",
        "centered_gram": "D=C+J over F_3",
        "centered_rank": 11,
        "centered_rows": 231,
        "centered_row_norm": 0,
        "centered_rows_nonzero": True,
        "centered_projective_points_distinct": True,
        "ambient_dimension": 11,
        "ambient_determinant_class": "nonsquare",
        "equal_centered_rows_rejection": {
            "forced_integer_difference_norm_squared": equal_candidate_norm,
            "reflection_difference_norm_squared": true_sum_or_difference_norm,
        },
        "antipodal_centered_rows_rejection": {
            "forced_pair_relation": "C_ij=+2",
            "other_coordinate_types": [
                "(+2,+2)",
                "(-2,0) in either order",
            ],
            "double_plus_coordinates": antipodal_double_plus,
            "mixed_coordinates": antipodal_mixed,
            "forced_integer_sum_norm_squared": forced_antipodal_norm,
            "reflection_sum_norm_squared": true_sum_or_difference_norm,
        },
        "oriented_inner_distribution": {
            "equal": 1,
            "antipodal": 0,
            "inner_0": ENDPOINT_PLUS,
            "inner_1": ENDPOINT_ZERO,
            "inner_2": ENDPOINT_MINUS,
        },
    }


def centered_oriented_scheme() -> dict[str, object]:
    """Reconstruct the oriented isotropic scheme in a nonsquare 11-space."""

    diagonal = (1,) * 10 + (2,)
    x = (0,) * 9 + (1, 1)
    representatives = (
        x,
        (0,) * 9 + (2, 2),
        (0,) * 6 + (1, 1, 1, 0, 0),
        (0,) * 9 + (2, 1),
        (0,) * 9 + (1, 2),
    )

    def inner(left: Sequence[int], right: Sequence[int]) -> int:
        return sum(
            coefficient * a * b
            for coefficient, a, b in zip(diagonal, left, right)
        ) % FIELD

    def negative(vector: Sequence[int]) -> tuple[int, ...]:
        return tuple((-entry) % FIELD for entry in vector)

    def relation(left: Sequence[int], right: Sequence[int]) -> int:
        if tuple(right) == tuple(left):
            return 0
        if tuple(right) == negative(left):
            return 1
        return {0: 2, 1: 3, 2: 4}[inner(left, right)]

    require(inner(x, x) == 0, "base vector is not isotropic")
    require(
        [relation(x, y) for y in representatives] == list(range(5)),
        "oriented isotropic representatives changed",
    )

    intersection_matrices: list[list[list[int]]] = []
    generic = {0: 2, 1: 3, 2: 4}
    for y in representatives:
        states: dict[tuple[int, int, int], int] = {(0, 0, 0): 1}
        for coefficient, x_coordinate, y_coordinate in zip(
            diagonal, x, y
        ):
            updated: dict[tuple[int, int, int], int] = defaultdict(int)
            for (norm, x_inner, y_inner), count in states.items():
                for z_coordinate in range(FIELD):
                    updated[
                        (
                            (
                                norm
                                + coefficient * z_coordinate**2
                            ) % FIELD,
                            (
                                x_inner
                                + coefficient
                                * x_coordinate
                                * z_coordinate
                            ) % FIELD,
                            (
                                y_inner
                                + coefficient
                                * y_coordinate
                                * z_coordinate
                            ) % FIELD,
                        )
                    ] += count
            states = dict(updated)

        matrix = [[0] * 5 for _ in range(5)]
        for (norm, x_inner, y_inner), count in states.items():
            if norm == 0:
                matrix[generic[x_inner]][generic[y_inner]] += count

        # The dynamic program includes the zero vector, which is not an
        # oriented projective representative.
        matrix[2][2] -= 1

        # Move x,-x,y,-y from their generic inner-product buckets into the
        # equality or antipodal relations when appropriate.
        for z in {tuple(x), negative(x), tuple(y), negative(y)}:
            old_left = generic[inner(x, z)]
            old_right = generic[inner(z, y)]
            new_left = relation(x, z)
            new_right = relation(z, y)
            matrix[old_left][old_right] -= 1
            matrix[new_left][new_right] += 1
        intersection_matrices.append(matrix)

    valencies = [
        intersection_matrices[0][index][index]
        for index in range(5)
    ]
    require(
        valencies == [1, 1, 19_680, 19_683, 19_683],
        "oriented isotropic valencies changed",
    )

    first_eigenmatrix = [
        [1, 1, 19_680, 19_683, 19_683],
        [1, 1, -164, 81, 81],
        [1, -1, 0, -81, 81],
        [1, 1, 160, -81, -81],
        [1, -1, 0, 243, -243],
    ]
    for character in first_eigenmatrix:
        for left in range(5):
            for right in range(5):
                expected = character[left] * character[right]
                actual = sum(
                    intersection_matrices[relation][left][right]
                    * character[relation]
                    for relation in range(5)
                )
                require(
                    actual == expected,
                    "oriented isotropic scheme character failed",
                )

    endpoint_distribution = [
        1,
        0,
        ENDPOINT_PLUS,
        ENDPOINT_ZERO,
        ENDPOINT_MINUS,
    ]
    positivity = [
        sum(
            Fraction(amount * eigenvalue, valency)
            for amount, eigenvalue, valency in zip(
                endpoint_distribution, character, valencies
            )
        )
        for character in first_eigenmatrix
    ]
    require(
        positivity
        == [
            Fraction(231),
            Fraction(209, 135),
            Fraction(13, 27),
            Fraction(493, 1107),
            Fraction(23, 9),
        ],
        "centered Delsarte transforms changed",
    )
    require(
        all(value >= 0 for value in positivity),
        "centered endpoint distribution was unexpectedly excluded",
    )
    return {
        "field": 3,
        "dimension": 11,
        "determinant_class": "nonsquare",
        "relation_order": [
            "equal",
            "antipodal",
            "inner_0_independent",
            "inner_1",
            "inner_2",
        ],
        "valencies": valencies,
        "intersection_matrices": intersection_matrices,
        "first_eigenmatrix": first_eigenmatrix,
        "endpoint_inner_distribution": endpoint_distribution,
        "delsarte_transforms": [
            fraction_record(value) for value in positivity
        ],
        "excluded": False,
    }


def centered_code_constraints() -> dict[str, object]:
    """Record exact code and low-weight dual constraints."""

    edge_count = ORIGINAL_VERTICES * ORIGINAL_DEGREE // 2
    nonedge_count = (
        ORIGINAL_VERTICES * (ORIGINAL_VERTICES - 1) // 2
        - edge_count
    )
    require((edge_count, nonedge_count) == (693, 4_158),
            "original pair counts changed")

    # Each of the 99 vertex-star incidence rows has weight seven.  Adjacent
    # stars meet in one triangle; nonadjacent stars are disjoint.
    dual_lower_bounds = {
        "7": 2 * ORIGINAL_VERTICES,
        "12": 2 * edge_count,
        "13": 2 * edge_count,
        "14": 4 * nonedge_count,
    }
    require(
        dual_lower_bounds
        == {"7": 198, "12": 1_386, "13": 1_386, "14": 16_632},
        "centered dual low-weight bounds changed",
    )
    return {
        "code": {
            "definition": "W=col(Z) <= F_3^231",
            "parameters": "[231,11]_3",
            "projective": True,
            "self_orthogonal": True,
            "all_one_vector_in_dual": True,
            "frame_identities": [
                "Z^T Z=0",
                "Z^T 1=0",
                "N Z=0",
            ],
        },
        "distinguished_primal_words": {
            "weight": ENDPOINT_ZERO + ENDPOINT_MINUS,
            "composition_n1_n2": [
                ENDPOINT_ZERO,
                ENDPOINT_MINUS,
            ],
            "projective_words": TRIANGLE_COUNT,
            "including_negatives": 2 * TRIANGLE_COUNT,
            "weight_enumerator_constraint": "A_198>=462",
        },
        "dual_low_weight_lower_bounds": dual_lower_bounds,
        "dual_word_sources": {
            "weight_7": "the 99 vertex-star rows and their negatives",
            "weight_12": "differences of adjacent vertex-star rows",
            "weight_13": "sums of adjacent vertex-star rows",
            "weight_14": (
                "sums and differences of nonadjacent vertex-star rows"
            ),
        },
        "collision_control": (
            "The symbol supports recover the one or two original star "
            "centers, so the displayed words are distinct up to the "
            "explicit sign pairing."
        ),
    }


def core_adjacency() -> list[list[int]]:
    masks = [int(encoded, 16) for encoded in FROZEN_CORE_ROWS_HEX]
    require(len(masks) == CORE_SIZE, "frozen core size changed")
    adjacency = [
        [
            (masks[left] >> right) & 1
            for right in range(CORE_SIZE)
        ]
        for left in range(CORE_SIZE)
    ]
    for left in range(CORE_SIZE):
        require(adjacency[left][left] == 0, "frozen core acquired a loop")
        require(sum(adjacency[left]) == 3, "frozen core is not cubic")
        for right in range(CORE_SIZE):
            require(
                adjacency[left][right] == adjacency[right][left],
                "frozen core is not symmetric",
            )
    return adjacency


def square_matrix(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    size = len(matrix)
    return [
        [
            sum(
                matrix[left][middle] * matrix[middle][right]
                for middle in range(size)
            )
            for right in range(size)
        ]
        for left in range(size)
    ]


def four_cycle_count(adjacency: Sequence[Sequence[int]]) -> int:
    squared = square_matrix(adjacency)
    opposite_pair_choices = sum(
        squared[left][right] * (squared[left][right] - 1) // 2
        for left, right in combinations(range(len(adjacency)), 2)
    )
    require(
        opposite_pair_choices % 2 == 0,
        "four-cycle opposite-pair count lost parity",
    )
    return opposite_pair_choices // 2


def required_bbt(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    squared = square_matrix(adjacency)
    return [
        [
            12 * int(left == right)
            - adjacency[left][right]
            + 2
            - int(left // FIBRE_SIZE == right // FIBRE_SIZE)
            - squared[left][right]
            for right in range(CORE_SIZE)
        ]
        for left in range(CORE_SIZE)
    ]


def simultaneous_bh_constraints() -> dict[str, object]:
    """Derive exact overlap and edge decompositions for a full B/H pair."""

    # General formulas in terms of c4=C4(A_X).
    # Row-pair concurrence values in G=BB^T are only 0,1,2 off diagonal.
    # There are 18 forced zeroes from within-fibre matching edges and two
    # more zeroes per core four-cycle (its opposite pairs).
    formula = {
        "row_pair_concurrence_counts": {
            "0": "18+2*c4",
            "1": "324-4*c4",
            "2": "288+2*c4",
        },
        "block_pair_overlap_counts": {
            "0": "438+2*c4",
            "1": "1044-4*c4",
            "2": "288+2*c4",
        },
    }

    # Compatible H has 240 edges.  The mixed equation and
    # sum_y e_y=36 force 144 edges of overlap one and 96 of overlap zero.
    h_edge_overlap = {"0": 96, "1": 144, "2": 0}
    require(sum(h_edge_overlap.values()) == Y_SIZE * 8 // 2,
            "H edge count changed")

    adjacency = core_adjacency()
    core_c4 = four_cycle_count(adjacency)
    require(core_c4 == 4, "frozen rank-ten core four-cycle count changed")
    gram = required_bbt(adjacency)
    gram_histogram = Counter(
        gram[left][right]
        for left, right in combinations(range(CORE_SIZE), 2)
    )
    require(
        gram_histogram == Counter({1: 308, 2: 296, 0: 26}),
        "frozen required BB^T pair histogram changed",
    )

    block_overlap = {
        0: 438 + 2 * core_c4,
        1: 1_044 - 4 * core_c4,
        2: 288 + 2 * core_c4,
    }
    require(
        block_overlap == {0: 446, 1: 1_028, 2: 296},
        "frozen block-overlap census changed",
    )
    require(sum(block_overlap.values()) == 1_770,
            "block-pair total changed")
    require(
        block_overlap[1] + 2 * block_overlap[2]
        == CORE_SIZE * (10 * 9 // 2),
        "block overlap first moment changed",
    )

    nonedge_overlap = {
        overlap: block_overlap[overlap] - h_edge_overlap.get(
            str(overlap), 0
        )
        for overlap in (0, 1, 2)
    }
    require(
        nonedge_overlap == {0: 350, 1: 884, 2: 296},
        "frozen H nonedge overlap census changed",
    )

    # The YY equation gives c_H(y,z)=1-s on an H edge and 2-s on a
    # nonedge, where s=|b_y intersect b_z|.  Thus all 96 overlap-zero
    # edges lie in one H triangle, all 144 overlap-one edges lie in none,
    # and the 32 H triangles are edge-disjoint.
    h_triangles = h_edge_overlap["0"] // 3
    h_four_cycles = nonedge_overlap[0] // 2
    require(
        (h_triangles, h_four_cycles)
        == (32, 171 + core_c4),
        "H triangle/four-cycle reconstruction changed",
    )

    return {
        "full_block_equations": {
            "xx": "BB^T=12I-A_X+2J-RR^T-A_X^2",
            "xy": "BH=(J/3-I-A_X)B",
            "yy": "B^TB+H^2=12I-H+2J",
        },
        "general_overlap_formulas": formula,
        "simultaneous_H_edge_overlap_counts": h_edge_overlap,
        "simultaneous_H_decomposition": {
            "overlap_zero_edges": (
                "96 edges, exactly the edge-disjoint union of 32 H triangles"
            ),
            "overlap_one_edges": (
                "144 edges, none lying in an H triangle"
            ),
            "point_labeled_matchings": (
                "For each x in X, the ten blocks containing x induce a "
                "four-edge matching in H; these 36 matchings partition "
                "the 144 overlap-one edges."
            ),
            "per_block": (
                "If e_y is the number of A_X edges inside b_y, then y lies "
                "in 1+e_y H-triangles, has 2+2e_y overlap-zero neighbors, "
                "and 6-2e_y overlap-one neighbors."
            ),
        },
        "frozen_rank_ten_core_control": {
            "scope": (
                "36-vertex local relaxation only; no simultaneous B or H"
            ),
            "core_four_cycles": core_c4,
            "required_BBt_unordered_off_diagonal_histogram": {
                str(key): value
                for key, value in sorted(gram_histogram.items())
            },
            "forced_block_pair_overlap_counts_if_B_exists": {
                str(key): value
                for key, value in sorted(block_overlap.items())
            },
            "forced_H_edge_overlap_counts_if_completion_exists": (
                h_edge_overlap
            ),
            "forced_H_nonedge_overlap_counts_if_completion_exists": {
                str(key): value
                for key, value in sorted(nonedge_overlap.items())
            },
            "forced_H_triangles_if_completion_exists": h_triangles,
            "forced_H_four_cycles_if_completion_exists": h_four_cycles,
            "completion_found": False,
            "completion_excluded": False,
        },
    }


def build_results() -> dict[str, object]:
    verify_frozen_inputs()
    return {
        "schema_version": 1,
        "claim_label": "DERIVED_INCONCLUSIVE",
        "scope": (
            "Conditional prism-free endpoint n3=4158: simultaneous B/H "
            "overlap decomposition and the centered rank-twelve ternary "
            "equality case"
        ),
        "frozen_commit": FROZEN_COMMIT,
        "centered_projective_boundary": centered_projective_boundary(),
        "centered_oriented_isotropic_scheme": centered_oriented_scheme(),
        "centered_code_constraints": centered_code_constraints(),
        "simultaneous_BH_constraints": simultaneous_bh_constraints(),
        "conclusion": {
            "new_centered_projective_distinctness": True,
            "new_centered_code_constraints": True,
            "new_simultaneous_BH_edge_decomposition": True,
            "rank_twelve_boundary_excluded": False,
            "simultaneous_60_column_B_found": False,
            "simultaneous_60_column_B_excluded": False,
            "compatible_H_found": False,
            "compatible_H_excluded": False,
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "target_status": "UNKNOWN",
        },
        "limitations": [
            "All general conclusions are conditional on the hypothetical prism-free endpoint.",
            "The oriented isotropic Delsarte transforms are all nonnegative, so they do not exclude rank twelve.",
            "The low-weight dual-code lower bounds are necessary conditions, not a code classification.",
            "The overlap and edge decompositions assume a full simultaneous B and compatible H.",
            "The frozen rank-ten core is a local relaxation, not a graph or completion.",
            "No endpoint exclusion, improved n3 bound, construction, or novelty claim is made.",
        ],
    }


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


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
        arguments.output.write_bytes(encoded)
        print(arguments.output)
        return 0
    sys.stdout.buffer.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
