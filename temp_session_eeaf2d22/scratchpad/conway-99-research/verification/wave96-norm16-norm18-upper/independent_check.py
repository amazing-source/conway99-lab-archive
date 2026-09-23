"""Independent exact verifier for the sealed Wave 96 package.

This module does not import discovery code.  It checks the finite arithmetic
and the local SRG deductions only.  In particular, it does not prove either
of the proposed fixed-C4 extension caps.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations, product
from math import ceil, comb
from pathlib import Path


Q = Fraction
DEFAULT_OUTPUT = Path(__file__).with_name("independent-results.json")


def fraction_text(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def inverse(matrix: list[list[Q]]) -> list[list[Q]]:
    size = len(matrix)
    work = [
        row[:] + [Q(row_index == column) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            row for row in range(column, size) if work[row][column] != 0
        )
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            multiplier = work[row][column]
            if multiplier == 0:
                continue
            work[row] = [
                left - multiplier * right
                for left, right in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def matmul(
    left: list[list[Q]], right: list[list[Q]]
) -> list[list[Q]]:
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def quadratic(vector: list[Q], matrix: list[list[Q]]) -> Q:
    return sum(
        vector[i] * matrix[i][j] * vector[j]
        for i in range(len(vector))
        for j in range(len(vector))
    )


def projector_check() -> dict:
    # The restricted eigenvalues of srg(99,14,1,2) are 3 and -4.
    projector_values = {
        eigenvalue: Q(27 - 9 * eigenvalue, 63)
        for eigenvalue in (3, -4)
    }
    # J acts by 99 on the all-one line.
    projector_values[14] = Q(27 - 9 * 14 + 99, 63)
    assert projector_values == {3: 0, -4: 1, 14: 0}

    cycle_edges = {
        (0, 1),
        (1, 2),
        (2, 3),
        (0, 3),
    }
    gram = []
    for i in range(4):
        row = []
        for j in range(4):
            edge = (min(i, j), max(i, j)) in cycle_edges
            row.append(Q(27 * (i == j) - 9 * edge + 1, 63))
        gram.append(row)

    gram_inverse = inverse(gram)
    identity = matmul(gram, gram_inverse)
    assert identity == [
        [Q(i == j) for j in range(4)] for i in range(4)
    ]
    alternating = [Q(1), Q(-1), Q(1), Q(-1)]
    interpolant_norm = quadratic(alternating, gram_inverse)
    assert interpolant_norm == Q(28, 5)

    residual_radius = Q(16) - interpolant_norm
    residual_dimension = 44 - 4
    assert residual_dimension == 40

    # The Gram model for the residual cross-polytope is
    # <+e_i,+e_j>=R delta_ij and <-e_i,+e_j>=-R delta_ij.
    signed_axes = [(axis, sign) for axis in range(40) for sign in (-1, 1)]
    distances = []
    for (axis_a, sign_a), (axis_b, sign_b) in combinations(
        signed_axes, 2
    ):
        inner = (
            residual_radius * sign_a * sign_b
            if axis_a == axis_b
            else Q(0)
        )
        distances.append(2 * residual_radius - 2 * inner)
    minimum_distance = min(distances)
    assert len(signed_axes) == 80
    assert minimum_distance == Q(104, 5) > 14

    return {
        "projector_polynomial_values": {
            str(key): fraction_text(value)
            for key, value in projector_values.items()
        },
        "principal_gram": [
            [fraction_text(value) for value in row] for row in gram
        ],
        "principal_inverse": [
            [fraction_text(value) for value in row] for row in gram_inverse
        ],
        "minimum_interpolant_squared_norm": fraction_text(
            interpolant_norm
        ),
        "residual_dimension": residual_dimension,
        "norm16_residual_squared_radius": fraction_text(residual_radius),
        "norm18_residual_squared_radius": fraction_text(
            Q(18) - interpolant_norm
        ),
        "cross_polytope_size": len(signed_axes),
        "cross_polytope_minimum_squared_distance": fraction_text(
            minimum_distance
        ),
        "metric_relaxation_proves_cap25": False,
    }


def fixed_cycle_partition() -> dict:
    # Each diagonal already has its two common neighbours in the cycle.
    # The four cycle edges each have one distinct outside common neighbour.
    type11 = 4
    outside_anchor_incidences = 4 * (14 - 2)
    type1 = outside_anchor_incidences - 2 * type11
    p_only = type1 // 2
    n_only = type1 // 2
    type00 = 95 - type11 - p_only - n_only
    assert (type00, p_only, n_only, type11) == (51, 20, 20, 4)
    selections = comb(10, 2) ** 4 * comb(51, 2) * comb(49, 2)
    return {
        "outside_partition": [type00, p_only, n_only, type11],
        "norm16_type_compatible_selections": selections,
        "graph_compatible_count_established": False,
    }


def degree_square_minimum(vertices: int, edge_count: int) -> int:
    edges = list(combinations(range(vertices), 2))
    best: int | None = None
    for chosen in combinations(edges, edge_count):
        degrees = [0] * vertices
        for left, right in chosen:
            degrees[left] += 1
            degrees[right] += 1
        score = sum(value * value for value in degrees)
        if best is None or score < best:
            best = score
    assert best is not None
    return best


def alternating_c4_lower(sign_size: int, same_edges: int) -> dict:
    square_minimum = degree_square_minimum(sign_size, same_edges)
    pair_incidences = (
        6 * sign_size + 7 * same_edges + square_minimum // 2
    )
    pair_count = comb(sign_size, 2)
    return {
        "sign_size": sign_size,
        "same_edges": same_edges,
        "minimum_degree_square_sum": square_minimum,
        "minimum_cross_pair_incidences": pair_incidences,
        "minimum_alternating_C4": pair_incidences - pair_count,
    }


def weighted_rank28_check() -> dict:
    c4_count = ((comb(99, 2) - 99 * 14 // 2) // 2)
    assert c4_count == 2079

    shell_rows = {
        "norm16_h0": alternating_c4_lower(8, 0),
        "norm18_h0": alternating_c4_lower(9, 0),
        "norm18_h1": alternating_c4_lower(9, 1),
    }
    shell_minima = {
        key: row["minimum_alternating_C4"]
        for key, row in shell_rows.items()
    }
    assert shell_minima == {
        "norm16_h0": 20,
        "norm18_h0": 18,
        "norm18_h1": 26,
    }

    weighted_lower = 13_980_652 - 2387 * 4950
    assert weighted_lower == 2_165_002
    ratios = {
        "norm16_h0": Q(2 * 407, shell_minima["norm16_h0"]),
        "norm18_h0": Q(2 * 43, shell_minima["norm18_h0"]),
        "norm18_h1": Q(2 * 43, shell_minima["norm18_h1"]),
    }
    maximum_ratio = max(ratios.values())
    assert maximum_ratio == Q(407, 10)

    cap25_upper = maximum_ratio * c4_count * 25
    cap25_even_upper = cap25_upper.numerator // cap25_upper.denominator
    cap25_even_upper -= cap25_even_upper % 2
    cap26_upper = maximum_ratio * c4_count * 26
    cap26_even_upper = cap26_upper.numerator // cap26_upper.denominator
    cap26_even_upper -= cap26_even_upper % 2
    assert cap25_even_upper == 2_115_382 < weighted_lower
    assert cap26_even_upper == 2_199_996 > weighted_lower

    incidence_lower = ceil(Q(weighted_lower, 1) / maximum_ratio)
    per_cycle = ceil(Q(incidence_lower, c4_count))
    assert incidence_lower == 53_195
    assert per_cycle == 26
    return {
        "induced_C4_count": c4_count,
        "shell_rows": shell_rows,
        "weighted_lower": weighted_lower,
        "objective_per_incidence_ratios": {
            key: fraction_text(value) for key, value in ratios.items()
        },
        "maximum_ratio": fraction_text(maximum_ratio),
        "cap25_rational_upper": fraction_text(cap25_upper),
        "cap25_even_upper": cap25_even_upper,
        "cap25_contradicts": True,
        "cap26_even_upper": cap26_even_upper,
        "cap26_contradicts": False,
        "forced_total_incidence": incidence_lower,
        "forced_one_cycle_antipodal_extensions": per_cycle,
        "cap25_proved": False,
    }


def norm20_profiles() -> list[dict[str, int]]:
    profiles: set[tuple[int, int, int, int]] = set()
    for plus_two, minus_two, plus_one, minus_one in product(
        range(6), range(6), range(21), range(21)
    ):
        if 4 * (plus_two + minus_two) + plus_one + minus_one != 20:
            continue
        if 2 * (plus_two - minus_two) + plus_one - minus_one != 0:
            continue
        odd_weight = plus_one + minus_one
        if odd_weight != 0 and odd_weight < 8:
            continue
        row = (plus_two, minus_two, plus_one, minus_one)
        opposite = (minus_two, plus_two, minus_one, plus_one)
        profiles.add(min(row, opposite))
    return [
        {
            "plus_two": row[0],
            "minus_two": row[1],
            "plus_one": row[2],
            "minus_one": row[3],
        }
        for row in sorted(
            profiles,
            key=lambda item: (
                item[0] + item[1],
                item[0],
                item[1],
                item[2],
                item[3],
            ),
        )
    ]


def nonzero_neighbor_patterns(
    profile: dict[int, int],
    focal: int,
    forced: dict[int, int] | None = None,
) -> list[dict[int, int]]:
    available = dict(profile)
    available[focal] -= 1
    values = (-2, -1, 1, 2)
    rows = []
    for counts in product(
        *(range(available[value] + 1) for value in values)
    ):
        row = dict(zip(values, counts))
        if forced and any(row[value] != count for value, count in forced.items()):
            continue
        if sum(counts) > 14:
            continue
        if sum(value * row[value] for value in values) != -4 * focal:
            continue
        rows.append(row)
    return rows


def norm20_profile_exclusions() -> dict:
    # Orient every mixed profile so that a +2 is present.
    oriented = {
        "m1": {-2: 0, -1: 9, 1: 7, 2: 1},
        "m2_same": {-2: 0, -1: 8, 1: 4, 2: 2},
        "m2_mixed": {-2: 1, -1: 6, 1: 6, 2: 1},
        "m3_same": {-2: 0, -1: 7, 1: 1, 2: 3},
        "m3_mixed": {-2: 1, -1: 5, 1: 3, 2: 2},
    }
    plus_two_patterns = {
        key: nonzero_neighbor_patterns(profile, 2)
        for key, profile in oriented.items()
    }
    assert not plus_two_patterns["m3_same"]
    assert not plus_two_patterns["m3_mixed"]

    same_rows = plus_two_patterns["m2_same"]
    assert len(same_rows) == 1
    assert same_rows[0] == {-2: 0, -1: 8, 1: 0, 2: 0}

    mixed_rows = plus_two_patterns["m2_mixed"]
    assert len(mixed_rows) == 1
    assert mixed_rows[0] == {-2: 1, -1: 6, 1: 0, 2: 0}
    mixed_unit_rows = nonzero_neighbor_patterns(
        oriented["m2_mixed"], 1, forced={2: 0}
    )
    mixed_common_minimum = min(
        row[-2] + row[-1] for row in mixed_unit_rows
    )
    assert mixed_common_minimum == 3

    m1_plus_two_rows = plus_two_patterns["m1"]
    m1_negative_minimum = min(row[-1] for row in m1_plus_two_rows)
    m1_unit_rows = nonzero_neighbor_patterns(oriented["m1"], 1)
    m1_unit_negative_minimum = min(row[-1] for row in m1_unit_rows)
    m1_intersection_minimum = (
        m1_negative_minimum + m1_unit_negative_minimum - 9
    )
    assert (m1_negative_minimum, m1_unit_negative_minimum) == (8, 4)
    assert m1_intersection_minimum == 3

    return {
        "m3_neighbor_equation_feasible": False,
        "m2_same_forced_shared_neighbors": 8,
        "m2_same_pair_is_nonadjacent": True,
        "m2_mixed_plus2_unit_minimum_common_neighbors": (
            mixed_common_minimum
        ),
        "m1_plus2_negative_neighbors_minimum": m1_negative_minimum,
        "m1_unit_negative_neighbors_minimum": m1_unit_negative_minimum,
        "m1_negative_neighborhood_intersection_minimum": (
            m1_intersection_minimum
        ),
        "srg_limits": {"adjacent": 1, "nonadjacent": 2},
        "all_mixed_profiles_excluded": True,
    }


def norm20_check() -> dict:
    profiles = norm20_profiles()
    expected = [
        (0, 0, 10, 10),
        (0, 1, 9, 7),
        (0, 2, 8, 4),
        (1, 1, 6, 6),
        (0, 3, 7, 1),
        (1, 2, 5, 3),
    ]
    observed = [
        (
            row["plus_two"],
            row["minus_two"],
            row["plus_one"],
            row["minus_one"],
        )
        for row in profiles
    ]
    assert observed == expected

    edge_bound = Q(14 * 20 * 20, 2 * 99) + Q(
        3 * 20 * (99 - 20), 2 * 99
    )
    assert edge_bound == Q(5170, 99)
    assert 40 + 4 * 3 <= edge_bound < 40 + 4 * 4

    c4_rows = [alternating_c4_lower(10, h) for h in range(4)]
    assert [row["minimum_alternating_C4"] for row in c4_rows] == [
        15,
        23,
        31,
        39,
    ]

    return {
        "nonintegral_class_energy_floor": 22,
        "target_norm": 20,
        "integer_transfer_valid_below_floor": True,
        "coordinate_magnitude_upper": 2,
        "profiles_after_parity_and_zero_sum": profiles,
        "exclusions": norm20_profile_exclusions(),
        "surviving_profile": {
            "plus_one": 10,
            "minus_one": 10,
            "other": 0,
        },
        "restricted_edge_bound": fraction_text(edge_bound),
        "same_edges_per_side_upper": 3,
        "alternating_C4_rows": c4_rows,
        "universal_alternating_C4_lower": 15,
    }


def rank30_check(c4_count: int) -> dict:
    prefix = 6842
    incidence = 15 * prefix
    oriented_ceiling = ceil(Q(incidence, c4_count))
    assert incidence == 102_630
    assert oriented_ceiling == 50
    assert c4_count * (2 * 24) < incidence
    return {
        "q14_prefix_lower": prefix,
        "oriented_incidence_lower": incidence,
        "forced_one_cycle_oriented_extensions": oriented_ceiling,
        "forced_one_cycle_antipodal_extensions": oriented_ceiling // 2,
        "cap24_global_oriented_capacity": c4_count * 48,
        "cap24_would_contradict": True,
        "cap24_proved": False,
    }


def exact_result() -> dict:
    weighted = weighted_rank28_check()
    return {
        "format": "wave96-independent-verification-v1",
        "claim_label": "VERIFIED_WITH_CLARIFICATION",
        "frozen_discovery_manifest_sha256": (
            "1d1e7d01edfbfcd2871683390b56e16dc36a18cfc899f301f15a0fce3b246a73"
        ),
        "weighted_rank28": weighted,
        "fixed_C4": fixed_cycle_partition(),
        "projector_relaxation": projector_check(),
        "norm20_dictionary": norm20_check(),
        "rank30_q14": rank30_check(weighted["induced_C4_count"]),
        "jacobi_continuation": {
            "common_index_principal_gram_checked": True,
            "degree8_harmonic_weights_for_rank44": [22, 24, 26, 28, 30],
            "coefficient_interpretation": (
                "At q^8 and q^9, summing both alternating Laurent "
                "monomials over all C4s counts the oriented norm16/norm18 "
                "support-C4 incidences."
            ),
            "transformation_law_established": False,
            "signed_coefficient_control_established": False,
            "route_status": "UNKNOWN",
        },
        "clarification": (
            "In the mixed m=2 exclusion, a positive unit not adjacent to "
            "the -2 vertex already shares at least four negative-unit "
            "neighbors with the +2 vertex and violates mu=2. Only after "
            "that subcase is rejected may adjacency to -2 be called forced."
        ),
        "status": {
            "finite_arithmetic": "VERIFIED",
            "norm20_profile_theorem": "VERIFIED_CONDITIONAL_ON_FROZEN_INPUTS",
            "cap25": "UNKNOWN",
            "cap24": "UNKNOWN",
            "rank28_excluded": False,
            "rank30_excluded": False,
            "N16_upper_bound": None,
            "N18_upper_bound": None,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = exact_result()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify is not None:
        if not args.verify.exists():
            raise SystemExit(f"missing expected result: {args.verify}")
        if args.verify.read_text(encoding="utf-8") != encoded:
            raise SystemExit("independent result mismatch")
        print("PASS: Wave 96 independent result reproduced")
        return
    args.output.write_text(encoded, encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
