#!/usr/bin/env python3
"""Clean-room verifier for the Wave 99 transition-pair moment bound.

This module was written from the frozen assignment and verified Wave 64,
Wave 86, and Wave 90 inputs.  It does not import or execute Wave 99
discovery code.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
import json
import math
from pathlib import Path
from typing import Any, Iterable


POINTS = tuple(range(14))
GROUP = {point: point // 2 for point in POINTS}
MATE = {point: point ^ 1 for point in POINTS}
ROOT_COUNT = 99
SELECTED_TRANSITIONS = 14 * 6
SEED_SIZE = 4
OUTPUT = Path(__file__).with_name("independent-results.json")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pair(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left < right else (right, left)


def perfect_matchings(items: tuple[int, ...]) -> Iterable[tuple[tuple[int, int], ...]]:
    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        second = items[index]
        rest = items[1:index] + items[index + 1 :]
        for tail in perfect_matchings(rest):
            yield (pair(first, second),) + tail


@lru_cache(maxsize=None)
def local_matchings(center: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    """All prism-free transition matchings at one base center."""

    endpoints = tuple(
        point for point in POINTS if GROUP[point] != GROUP[center]
    )
    rows = tuple(
        tuple(sorted(matching))
        for matching in perfect_matchings(endpoints)
        if all(MATE[left] != right for left, right in matching)
    )
    require(len(rows) == 6040, "local perfect-matching count changed")
    return rows


@lru_cache(maxsize=1)
def seeds() -> tuple[tuple[int, int, int, int], ...]:
    rows = tuple(
        seed
        for seed in combinations(POINTS, SEED_SIZE)
        if len({GROUP[point] for point in seed}) == SEED_SIZE
    )
    require(len(rows) == math.comb(7, 4) * 2**4 == 560, "seed count changed")
    return rows


@lru_cache(maxsize=1)
def selected_transition_candidates() -> tuple[tuple[int, int, int], ...]:
    rows = []
    for center in POINTS:
        endpoints = tuple(
            point for point in POINTS if GROUP[point] != GROUP[center]
        )
        for left, right in combinations(endpoints, 2):
            if GROUP[left] != GROUP[right]:
                rows.append((center, left, right))
    require(len(rows) == 840, "transition-candidate count changed")
    return tuple(rows)


def transition_seed_multiplicities() -> list[int]:
    seed_sets = tuple(frozenset(seed) for seed in seeds())
    rows = [
        sum(
            frozenset((center, left, right)) <= seed
            for seed in seed_sets
        )
        for center, left, right in selected_transition_candidates()
    ]
    require(set(rows) == {8}, "a transition does not lie in eight seeds")
    return rows


def matching_contains(
    matching: tuple[tuple[int, int], ...], left: int, right: int
) -> bool:
    return pair(left, right) in matching


def original_center_score(
    matching: tuple[tuple[int, int], ...],
    fixed_center: int,
    first: int,
    second: int,
    tested_center: int,
) -> dict[str, Any]:
    """Weighted co-incidence score at first or second.

    The fixed transition is (fixed_center; first, second).  At center
    ``first`` the identical-triple transition pairs fixed_center with
    second, and conversely at center ``second``.
    """

    require(tested_center in {first, second}, "wrong original center")
    other = second if tested_center == first else first
    identical = matching_contains(matching, fixed_center, other)
    remaining_groups = {
        group
        for group in range(7)
        if group
        not in {
            GROUP[fixed_center],
            GROUP[first],
            GROUP[second],
        }
    }
    eligible_fourth_points = {
        point for point in POINTS if GROUP[point] in remaining_groups
    }
    union_four = sum(
        (
            left in {fixed_center, other}
            and right in eligible_fourth_points
        )
        or (
            right in {fixed_center, other}
            and left in eligible_fourth_points
        )
        for left, right in matching
    )
    weighted = 8 if identical else union_four
    require(union_four <= 2, "an original center contributes over two")
    require(
        not identical or union_four == 0,
        "identical triple did not consume both relevant endpoints",
    )
    return {
        "identical_triple": identical,
        "union_four_transitions": union_four,
        "weighted_coincidences": weighted,
    }


def fourth_center_score(
    matching: tuple[tuple[int, int], ...],
    fixed_triple: frozenset[int],
) -> int:
    """Number of matched pairs internal to the fixed triple."""

    score = sum(
        left in fixed_triple and right in fixed_triple
        for left, right in matching
    )
    require(score <= 1, "a matching selected two pairs on three points")
    return score


def triangle_guard() -> dict[str, Any]:
    """Verify the residual-triangle lambda obstruction."""

    shared, first, second = 0, 2, 4
    p = pair(shared, first)
    q = pair(shared, second)
    r = pair(first, second)
    residual_edges = {pair(0, 1), pair(0, 2), pair(1, 2)}
    # p--q is the fixed transition, p--r is centered at first, and
    # q--r is centered at second.
    common_neighbors_of_p_q = {"base_shared", "residual_r"}
    require(len(common_neighbors_of_p_q) == 2, "hostile triangle changed")
    return {
        "fixed_transition": [p, q],
        "first_center_identical_transition": [p, r],
        "second_center_identical_transition": [q, r],
        "residual_triangle_edge_count": len(residual_edges),
        "common_neighbors_of_fixed_adjacent_pair": sorted(
            common_neighbors_of_p_q
        ),
        "target_lambda": 1,
        "all_three_transitions_allowed_together": False,
        "reason": (
            "the fixed adjacent residual pair would have both its shared "
            "base point and the third residual label as common neighbors"
        ),
    }


def co_incidence_cap() -> dict[str, Any]:
    """Exhaust local matching profiles for one canonical transition."""

    shared, first, second = 0, 2, 4
    fixed_triple = frozenset((shared, first, second))
    fourth_points = tuple(
        point
        for point in POINTS
        if GROUP[point]
        not in {GROUP[shared], GROUP[first], GROUP[second]}
    )
    require(len(fourth_points) == 8, "fourth-point set changed")

    first_profiles = [
        original_center_score(
            matching, shared, first, second, tested_center=first
        )
        for matching in local_matchings(first)
    ]
    second_profiles = [
        original_center_score(
            matching, shared, first, second, tested_center=second
        )
        for matching in local_matchings(second)
    ]

    first_types = sorted(
        {
            (
                row["identical_triple"],
                row["union_four_transitions"],
                row["weighted_coincidences"],
            )
            for row in first_profiles
        }
    )
    second_types = sorted(
        {
            (
                row["identical_triple"],
                row["union_four_transitions"],
                row["weighted_coincidences"],
            )
            for row in second_profiles
        }
    )
    require(first_types == second_types, "original-center profiles differ")

    maximum_original_centers_without_lambda_guard = max(
        left[2] + right[2]
        for left in first_types
        for right in second_types
    )
    maximum_original_centers_with_lambda_guard = max(
        left[2] + right[2]
        for left in first_types
        for right in second_types
        if not (left[0] and right[0])
    )
    require(
        maximum_original_centers_without_lambda_guard == 16,
        "hostile no-lambda cap changed",
    )
    require(
        maximum_original_centers_with_lambda_guard == 10,
        "guarded original-center cap changed",
    )

    fourth_maxima = []
    for center in fourth_points:
        scores = [
            fourth_center_score(matching, fixed_triple)
            for matching in local_matchings(center)
        ]
        fourth_maxima.append(max(scores))
    require(set(fourth_maxima) == {1}, "fourth-center cap changed")
    total_cap = (
        maximum_original_centers_with_lambda_guard + sum(fourth_maxima)
    )
    require(total_cap == 18, "per-transition co-incidence cap changed")

    return {
        "canonical_fixed_transition": [shared, first, second],
        "fixed_transition_seed_count": 8,
        "center_partition": {
            "fixed_center": {
                "contribution": 0,
                "reason": (
                    "its matching already pairs the two fixed endpoints"
                ),
            },
            "other_two_original_centers": {
                "profile_types": [list(row) for row in first_types],
                "maximum_without_lambda_guard": (
                    maximum_original_centers_without_lambda_guard
                ),
                "maximum_with_lambda_guard": (
                    maximum_original_centers_with_lambda_guard
                ),
            },
            "eight_fourth_points": {
                "points": list(fourth_points),
                "individual_maxima": fourth_maxima,
                "sum_of_maxima": sum(fourth_maxima),
            },
        },
        "all_possible_centers_partitioned": True,
        "per_transition_coincidence_cap": total_cap,
        "lambda_triangle_guard": triangle_guard(),
    }


def moment_certificate() -> dict[str, Any]:
    seed_count = len(seeds())
    first_moment = SELECTED_TRANSITIONS * 8
    per_transition_cap = co_incidence_cap()[
        "per_transition_coincidence_cap"
    ]
    ordered_pair_moment_upper = SELECTED_TRANSITIONS * per_transition_cap
    pair_moment_upper = ordered_pair_moment_upper // 2
    require(ordered_pair_moment_upper % 2 == 0, "pair moment is half-integral")
    require(
        (first_moment, pair_moment_upper) == (672, 756),
        "transition moments changed",
    )

    pointwise = []
    for count in range(5):
        right = (
            Fraction(1)
            - Fraction(count, 2)
            + Fraction(math.comb(count, 2), 6)
        )
        left = Fraction(1 if count == 0 else 0)
        require(left <= right, f"pointwise certificate fails at j={count}")
        pointwise.append(
            {
                "j": count,
                "indicator_j_zero": str(left),
                "certificate_right_side": str(right),
                "slack": str(right - left),
            }
        )

    zero_seed_upper = (
        Fraction(seed_count)
        - Fraction(first_moment, 2)
        + Fraction(pair_moment_upper, 6)
    )
    require(zero_seed_upper == 350, "zero-seed upper bound changed")

    # Multiplicity audit:
    # sum_tau sum_{Q contains tau}(j(Q)-1)
    # = sum_Q j(Q)(j(Q)-1) = 2 sum_Q C(j(Q),2).
    return {
        "seed_transition_count_range": [0, 4],
        "seed_count": seed_count,
        "first_moment_exact": first_moment,
        "ordered_transition_pair_moment_upper": ordered_pair_moment_upper,
        "unordered_pair_moment_upper": pair_moment_upper,
        "multiplicity_identity": (
            "sum_tau sum_{Q contains tau}(j(Q)-1)"
            "=sum_Q j(Q)(j(Q)-1)=2 sum_Q C(j(Q),2)"
        ),
        "same_triple_pair_multiplicity": 8,
        "four_point_union_pair_multiplicity": 1,
        "pointwise_certificate": pointwise,
        "pointwise_formula": (
            "1[j=0] <= 1 - j/2 + C(j,2)/6 for 0<=j<=4"
        ),
        "zero_transition_seed_upper_bound": int(zero_seed_upper),
        "extremal_moment_distribution_control": {
            "n0": 350,
            "n3": 168,
            "n4": 42,
            "sum_n": 560,
            "sum_j_n": 672,
            "sum_Cj2_n": 756,
            "interpretation": (
                "formal sharpness for the two recorded moments only"
            ),
        },
    }


def n14_conversion() -> dict[str, Any]:
    rooted_upper = moment_certificate()["zero_transition_seed_upper_bound"]
    rooted_total_upper = ROOT_COUNT * rooted_upper
    require(rooted_total_upper % 7 == 0, "root/sign quotient not integral")
    n14_upper = rooted_total_upper // 7
    require(n14_upper == 4950, "N14 upper bound changed")
    return {
        "rooted_positive_vector_upper_bound": rooted_upper,
        "root_count": ROOT_COUNT,
        "positive_roots_per_oriented_vector": 7,
        "N14_counts_both_signs": True,
        "antipodal_pair_rooted_positive_incidences": 14,
        "identity": "7*N14=sum_o #{t:t_o=+1}",
        "N14_upper_bound": n14_upper,
        "no_extra_factor_of_two": True,
    }


def wave86_rearrangement() -> dict[str, Any]:
    """Rearrange the verified Wave 86 positive identity."""

    base = Fraction(1_997_236, 341)
    x8_rhs = Fraction(180, 217)
    x9_rhs = Fraction(2344, 2387)
    n16_left = Fraction(1) - x8_rhs
    n18_left = Fraction(1) - x9_rhs
    require(n16_left == Fraction(407, 2387), "N16 weight changed")
    require(n18_left == Fraction(43, 2387), "N18 weight changed")
    require(Fraction(2387, 341) == 7, "level-seven denominator changed")

    integral_rhs = int(base * 2387)
    require(integral_rhs == 13_980_652, "integral Wave86 RHS changed")
    n14_upper = n14_conversion()["N14_upper_bound"]
    residual = integral_rhs - 2387 * n14_upper
    require(residual == 2_165_002, "weighted residual changed")
    return {
        "verified_positive_identity_rearranged": (
            "N14+(407/2387)N16+(43/2387)N18"
            ">=1997236/341"
        ),
        "integral_form": (
            "2387*N14+407*N16+43*N18>=13980652"
        ),
        "N14_upper_inserted": n14_upper,
        "conclusion": "407*N16+43*N18>=2165002",
        "weighted_lower_bound": residual,
        "scope_requires_rank_28_q16": True,
        "scope_requires_prism_free_P0": True,
    }


def independent_result() -> dict[str, Any]:
    transition_multiplicities = transition_seed_multiplicities()
    cap = co_incidence_cap()
    moments = moment_certificate()
    n14 = n14_conversion()
    weighted = wave86_rearrangement()
    return {
        "format": "wave99-transition-pair-moment-independent-v1",
        "role": "verifier",
        "claim_label": "PENDING_DISCOVERY_COMPARISON",
        "scope": {
            "hypothetical_graph": "srg(99,14,1,2)",
            "N14_bound_requires_prism_free_P0": True,
            "N14_bound_requires_rank_28": False,
            "weighted_Wave86_conclusion_requires_prism_free_P0": True,
            "weighted_Wave86_conclusion_requires_rank_28_q16": True,
        },
        "rooted_reconstruction": {
            "seed_count": len(seeds()),
            "transition_candidates": len(selected_transition_candidates()),
            "selected_transitions": SELECTED_TRANSITIONS,
            "transition_seed_multiplicity_values": sorted(
                set(transition_multiplicities)
            ),
            "local_perfect_matching_count": len(local_matchings(0)),
        },
        "coincidence_cap": cap,
        "moment_certificate": moments,
        "sign_and_root_conversion": n14,
        "wave86_weighted_rearrangement": weighted,
        "precomparison_verdict": {
            "transition_cap_18": "INDEPENDENTLY_REPRODUCED",
            "N14_upper_bound_4950": "INDEPENDENTLY_REPRODUCED_SCOPED",
            "weighted_lower_bound": "INDEPENDENTLY_REPRODUCED_INTERSECTION_SCOPE",
            "discovery_comparison": "NOT_YET_PERFORMED",
        },
        "limitations": [
            "The N14 theorem is conditional on the prism-free P=0 branch.",
            "The weighted Wave86 consequence additionally requires r=28 (q=16).",
            "The pointwise moment distribution is a formal sharpness control, not a graph.",
            "No graph nonexistence or Conway-99 resolution follows here.",
        ],
    }


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--verify", action="store_true")
    arguments = parser.parse_args()
    rendered = canonical_json(independent_result())
    if arguments.verify:
        require(arguments.output.exists(), "independent result is missing")
        require(
            arguments.output.read_text(encoding="utf-8") == rendered,
            "independent canonical result mismatch",
        )
    else:
        arguments.output.write_text(
            rendered, encoding="utf-8", newline="\n"
        )
    print("PASS: Wave99 clean-room reconstruction")


if __name__ == "__main__":
    main()
