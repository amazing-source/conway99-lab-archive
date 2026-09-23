"""Exact arithmetic companion for the conditional n3=54 equality analysis.

The checker reconstructs the finite q-profile census, the equality-chain
arithmetic, the surface counts, the SRG triangle-type moments, and the binary
rank restrictions stated in the accompanying report.  It does not prove the
human semantic bridges that produce F, R, L, or the equitable cut.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import itertools
import json
from typing import Iterator


TOTAL_Q = 36


def nondecreasing_parts(
    total: int, length: int, minimum: int, maximum: int
) -> Iterator[tuple[int, ...]]:
    def visit(
        remaining: int,
        slots: int,
        lower: int,
        prefix: tuple[int, ...],
    ) -> Iterator[tuple[int, ...]]:
        if slots == 0:
            if remaining == 0:
                yield prefix
            return
        upper = min(maximum, remaining // slots)
        for value in range(lower, upper + 1):
            remainder = remaining - value
            if remainder < value * (slots - 1):
                continue
            if remainder > maximum * (slots - 1):
                continue
            yield from visit(
                remainder, slots - 1, value, prefix + (value,)
            )

    yield from visit(total, length, minimum, ())


def raw_profiles() -> list[tuple[int, tuple[int, ...]]]:
    result = []
    for order in range(1, TOTAL_Q // 2 + 1):
        maximum_q = (order - 1) // 3
        if maximum_q < 2:
            continue
        for profile in nondecreasing_parts(
            TOTAL_Q, order, 2, maximum_q
        ):
            result.append((order, profile))
    return result


def k_degrees(
    order: int, profile: tuple[int, ...]
) -> tuple[int, ...]:
    return tuple(order - 1 - 3 * value for value in profile)


def surviving_profiles() -> list[tuple[int, tuple[int, ...]]]:
    return [
        (order, profile)
        for order, profile in raw_profiles()
        if min(k_degrees(order, profile)) >= 4
    ]


def compressed(values: tuple[int, ...]) -> dict[str, int]:
    return {
        str(value): multiplicity
        for value, multiplicity in sorted(Counter(values).items())
    }


def size_two_type(left_q: int, right_q: int) -> dict[str, object]:
    fixed_sum = 2 * (left_q + right_q)
    compatible = fixed_sum % 4 == 0
    result: dict[str, object] = {
        "q_pair": [left_q, right_q],
        "fixed_sum": fixed_sum,
        "compatible_with_0_or_4_crossings": compatible,
    }
    if compatible:
        result["positive_support_neighbors"] = fixed_sum // 4
        result["active_degree_lower_bound"] = 4 + fixed_sum // 4
    return result


def spectral_average_upper(order: int) -> Fraction:
    return Fraction(3, 1) + Fraction(order, 9)


def triangle_types(c3_components_of_r: int) -> dict[str, int]:
    c = c3_components_of_r
    return {
        "X_vertices_0": 105 - c,
        "X_vertices_1": 81 + 3 * c,
        "X_vertices_2": 27 - 3 * c,
        "X_vertices_3": 18 + c,
        "active_X_vertices_3": 18,
        "inactive_X_vertices_3": c,
    }


def inactive_triangle_meeting_moments(
    c3_components_of_r: int,
) -> dict[str, int]:
    types = triangle_types(c3_components_of_r)
    inactive_counts = {
        0: types["X_vertices_0"],
        1: types["X_vertices_1"],
        2: types["X_vertices_2"],
        3: types["inactive_X_vertices_3"],
    }
    return {
        "inactive_triangle_count": sum(inactive_counts.values()),
        "sum_active_meeting_triangles": sum(
            count * (2 * x_count)
            for x_count, count in inactive_counts.items()
        ),
        "sum_squares_active_meeting_triangles": sum(
            count * (2 * x_count) ** 2
            for x_count, count in inactive_counts.items()
        ),
    }


def cycle_adjacency_nullity_mod2(length: int) -> int:
    # Solve A(C_length)x=0 by exact Gaussian elimination over F_2.
    rows = []
    for vertex in range(length):
        bits = (1 << ((vertex - 1) % length)) | (
            1 << ((vertex + 1) % length)
        )
        rows.append(bits)
    rank = 0
    for column in range(length):
        pivot = next(
            (index for index in range(rank, length) if rows[index] >> column & 1),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(length):
            if index != rank and rows[index] >> column & 1:
                rows[index] ^= rows[rank]
        rank += 1
    return length - rank


def build_result() -> dict[str, object]:
    raw = raw_profiles()
    survivors = surviving_profiles()
    survivor_rows = []
    for order, profile in survivors:
        active_order_upper = 3 * order // 2
        survivor_rows.append(
            {
                "r": order,
                "q_counts": compressed(profile),
                "K_degree_counts": compressed(k_degrees(order, profile)),
                "X_order_upper": active_order_upper,
                "spectral_average_degree_upper": str(
                    spectral_average_upper(active_order_upper)
                ),
                "r_below_boundary_is_excluded": (
                    order < 18
                    and spectral_average_upper(active_order_upper) < 6
                ),
            }
        )

    moments = {
        str(c): {
            "triangle_types": triangle_types(c),
            "inactive_meeting_moments": inactive_triangle_meeting_moments(c),
            "outside_triples_with_one_R_edge": 27 - 3 * c,
            "outside_triples_independent_in_GX": 45 + 3 * c,
        }
        for c in range(10)
    }

    nullities = {
        str(length): cycle_adjacency_nullity_mod2(length)
        for length in range(3, 28)
    }

    return {
        "case": "conditional n3=54 for srg(99,14,1,2)",
        "sum_q": TOTAL_Q,
        "raw_profile_count": len(raw),
        "raw_profile_order_histogram": {
            str(order): sum(
                candidate_order == order
                for candidate_order, _ in raw
            )
            for order in sorted({candidate_order for candidate_order, _ in raw})
        },
        "surviving_profile_count": len(survivors),
        "surviving_profiles": survivor_rows,
        "size_two_types": [
            size_two_type(left, right)
            for left, right in itertools.combinations_with_replacement(
                (2, 3, 4), 2
            )
        ],
        "dense_subset_threshold": 27,
        "boundary_equalities": {
            "r": 18,
            "X_order": 27,
            "point_count": 27,
            "point_sizes": "all 2",
            "q_values": "all 2",
            "GX_degree": 6,
            "GX_edges": 81,
            "cut_degrees_X_to_outside": 8,
            "cut_degrees_outside_to_X": 3,
            "outside_order": 72,
            "quotient_matrix": [[6, 8], [3, 11]],
        },
        "residual_counts": {
            "F_order": 18,
            "F_edges": 27,
            "F_degree": 3,
            "R_order": 27,
            "R_edges": 27,
            "R_degree": 2,
            "L_order": 18,
            "L_edges": 54,
            "L_degree": 6,
            "auxiliary_H_order": 27,
            "auxiliary_H_edges": 54,
            "auxiliary_H_degree": 4,
            "hexagonal_faces": 18,
            "surface_euler_characteristic": 27 - 54 + 18,
            "surface_consequence": "at least one nonorientable component",
        },
        "triangle_type_rows_by_R_C3_count": moments,
        "binary_rank_consequences": {
            "rank_N_over_F2": "18-c_F",
            "rank_R_incidence_over_F2": "27-c_R",
            "self_orthogonal_rank_upper": 13,
            "derived_component_bound": "c_F+c_R>=5",
            "cycle_adjacency_nullity_over_F2": nullities,
            "derived_nullity_bound": (
                "odd_R_cycles+2*even_R_cycles>=9-2*c_F"
            ),
        },
        "point_graph_component_reduction": {
            "pre_parity_options": [
                "connected order-18 cubic graph of girth at least 5",
                "K3,3 plus connected order-12 cubic graph of girth at least 5",
                "three disjoint K3,3 components",
            ],
            "three_K3,3_components": "excluded by exact-coverage parity",
            "surviving_options": [
                "connected order-18 cubic graph of girth at least 5",
                "K3,3 plus connected order-12 cubic graph of girth at least 5",
            ],
        },
        "matrix_identities": {
            "rectangle_coverage": "N A_R N^T = 2 A_L",
            "active_graph": "A_X = N^T N - 2 I + A_R",
            "outside_gram": (
                "C C^T = 12 I - A_X - A_X^2 + 2 J"
            ),
            "equitable_cross": "A_X C + C A_Y = -C + 2 J",
        },
        "claim_status": "DERIVED_RESIDUAL_NOT_EXCLUSION",
        "conditional_n3_54": "UNKNOWN",
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
    }


def main() -> None:
    result = build_result()
    assert result["raw_profile_count"] == 23
    assert result["surviving_profile_count"] == 6
    assert all(
        row["r_below_boundary_is_excluded"]
        for row in result["surviving_profiles"][:-1]
    )
    assert result["residual_counts"]["surface_euler_characteristic"] == -9
    assert all(
        row["inactive_meeting_moments"]
        == {
            "inactive_triangle_count": 213,
            "sum_active_meeting_triangles": 270,
            "sum_squares_active_meeting_triangles": 756,
        }
        for row in result["triangle_type_rows_by_R_C3_count"].values()
    )
    assert all(
        nullity == (1 if int(length) % 2 else 2)
        for length, nullity in result["binary_rank_consequences"][
            "cycle_adjacency_nullity_over_F2"
        ].items()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
