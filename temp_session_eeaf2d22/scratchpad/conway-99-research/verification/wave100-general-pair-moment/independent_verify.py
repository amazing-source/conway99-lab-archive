#!/usr/bin/env python3
"""Clean-room arithmetic verifier for the Wave 100 general pair moment."""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
from typing import Any


V = 99
K = 14
LAMBDA = 1
MU = 2
TRANSITIONS_PER_ROOT = 84
SEEDS_PER_ROOT = 560
OUTPUT = Path(__file__).with_name("independent-results.json")
POINTS = tuple(range(14))
GROUP = {point: point // 2 for point in POINTS}
MATE = {point: point ^ 1 for point in POINTS}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pair(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left < right else (right, left)


@lru_cache(maxsize=None)
def perfect_matchings(
    items: tuple[int, ...],
) -> tuple[tuple[tuple[int, int], ...], ...]:
    if not items:
        return ((),)
    first = items[0]
    rows = []
    for index in range(1, len(items)):
        second = items[index]
        rest = items[1:index] + items[index + 1 :]
        for tail in perfect_matchings(rest):
            rows.append((pair(first, second),) + tail)
    return tuple(rows)


@lru_cache(maxsize=None)
def local_matchings(center: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    endpoints = tuple(
        point for point in POINTS if GROUP[point] != GROUP[center]
    )
    rows = tuple(
        tuple(sorted(matching)) for matching in perfect_matchings(endpoints)
    )
    require(len(rows) == 10_395, "general local matching count changed")
    return rows


@lru_cache(maxsize=1)
def seeds() -> tuple[tuple[int, int, int, int], ...]:
    rows = tuple(
        seed
        for seed in combinations(POINTS, 4)
        if len({GROUP[point] for point in seed}) == 4
    )
    require(len(rows) == 560, "rooted seed count changed")
    return rows


def transition_candidates() -> tuple[tuple[int, int, int], ...]:
    rows = []
    for center in POINTS:
        endpoints = tuple(
            point for point in POINTS if GROUP[point] != GROUP[center]
        )
        rows.extend(
            (center, left, right)
            for left, right in combinations(endpoints, 2)
        )
    require(len(rows) == 924, "general transition-candidate count changed")
    return tuple(rows)


def local_applicability_certificate() -> dict[str, Any]:
    """Check cap 18 when local matchings may contain mate transitions."""

    candidates = transition_candidates()
    mate_forbidden = [
        row for row in candidates if MATE[row[1]] == row[2]
    ]
    seed_eligible = [
        row for row in candidates if GROUP[row[1]] != GROUP[row[2]]
    ]
    seed_sets = tuple(frozenset(seed) for seed in seeds())
    mate_multiplicities = {
        sum(frozenset(row) <= seed for seed in seed_sets)
        for row in mate_forbidden
    }
    eligible_multiplicities = {
        sum(frozenset(row) <= seed for seed in seed_sets)
        for row in seed_eligible
    }
    require(len(mate_forbidden) == 84, "mate transition census changed")
    require(len(seed_eligible) == 840, "eligible transition census changed")
    require(mate_multiplicities == {0}, "mate transition entered a seed")
    require(
        eligible_multiplicities == {8},
        "eligible transition seed multiplicity changed",
    )

    shared, first, second = 0, 2, 4
    extensions = {
        point
        for point in POINTS
        if GROUP[point]
        not in {GROUP[shared], GROUP[first], GROUP[second]}
    }
    require(len(extensions) == 8, "extension-point count changed")

    def original_profiles(center: int, other: int) -> set[tuple[bool, int]]:
        profiles = set()
        for matching in local_matchings(center):
            edges = set(matching)
            identical = pair(shared, other) in edges
            if identical:
                score = 8
            else:
                score = sum(
                    (
                        left in {shared, other} and right in extensions
                    )
                    or (
                        right in {shared, other} and left in extensions
                    )
                    for left, right in matching
                )
                require(score <= 2, "non-identical center exceeded two")
            profiles.add((identical, score))
        return profiles

    first_profiles = original_profiles(first, second)
    second_profiles = original_profiles(second, first)
    require(first_profiles == second_profiles, "profile symmetry failed")
    without_guard = max(
        left[1] + right[1]
        for left in first_profiles
        for right in second_profiles
    )
    with_guard = max(
        left[1] + right[1]
        for left in first_profiles
        for right in second_profiles
        if not (left[0] and right[0])
    )
    require(without_guard == 16, "unguarded cap changed")
    require(with_guard == 10, "lambda-guarded cap changed")

    fourth_maxima = []
    fixed_triple = {shared, first, second}
    for center in sorted(extensions):
        maximum = max(
            sum(
                left in fixed_triple and right in fixed_triple
                for left, right in matching
            )
            for matching in local_matchings(center)
        )
        require(maximum == 1, "fourth center exceeded one")
        fourth_maxima.append(maximum)
    cap = with_guard + sum(fourth_maxima)
    require(cap == 18, "general per-transition cap changed")
    return {
        "seed_count": len(seed_sets),
        "transition_candidate_count": len(candidates),
        "mate_forbidden_candidate_count": len(mate_forbidden),
        "seed_eligible_candidate_count": len(seed_eligible),
        "mate_transition_seed_multiplicities": sorted(mate_multiplicities),
        "eligible_transition_seed_multiplicities": sorted(
            eligible_multiplicities
        ),
        "local_perfect_matching_count": len(local_matchings(0)),
        "original_center_profile_types": [
            [identical, score]
            for identical, score in sorted(first_profiles)
        ],
        "original_center_max_without_lambda_guard": without_guard,
        "original_center_max_with_lambda_guard": with_guard,
        "fourth_center_sum_of_maxima": sum(fourth_maxima),
        "per_transition_coincidence_cap": cap,
        "mate_transition_applicability": (
            "mate transitions lie in zero seeds; every seed-eligible fixed "
            "transition retains cap 18 even when other local matching edges "
            "may be mate transitions"
        ),
    }


def edge(left: int, right: int) -> frozenset[int]:
    return frozenset((left, right))


def two_triangle_graph(cross_edges: int) -> frozenset[frozenset[int]]:
    require(0 <= cross_edges <= 3, "invalid cross-edge count")
    triangles = ((0, 1, 2), (3, 4, 5))
    edges = {
        edge(left, right)
        for triangle in triangles
        for left, right in combinations(triangle, 2)
    }
    edges.update(edge(index, index + 3) for index in range(cross_edges))
    return frozenset(edges)


def induced_c4_count(edges: frozenset[frozenset[int]]) -> int:
    count = 0
    for vertices in combinations(range(6), 4):
        degrees = {
            vertex: sum(
                edge(vertex, other) in edges
                for other in vertices
                if other != vertex
            )
            for vertex in vertices
        }
        count += set(degrees.values()) == {2}
    return count


def prism_identity_certificate() -> dict[str, Any]:
    graph_edges = V * K // 2
    graph_nonedges = math.comb(V, 2) - graph_edges
    induced_c4s = graph_nonedges * math.comb(MU, 2) // 2
    shape_counts = [
        induced_c4_count(two_triangle_graph(cross))
        for cross in range(4)
    ]

    prism_edges = two_triangle_graph(3)
    partner = {
        **{index: index + 3 for index in range(3)},
        **{index + 3: index for index in range(3)},
    }
    triangles = ({0, 1, 2}, {3, 4, 5})
    rooted_certificates = []
    for root in range(6):
        own_triangle = next(row for row in triangles if root in row)
        left, right = sorted(own_triangle - {root})
        opposite = partner[root]
        left_residual = partner[left]
        right_residual = partner[right]
        required = {
            edge(root, left),
            edge(root, right),
            edge(left, right),
            edge(opposite, left_residual),
            edge(opposite, right_residual),
            edge(left_residual, right_residual),
            edge(root, opposite),
            edge(left, left_residual),
            edge(right, right_residual),
        }
        require(required == prism_edges, "rooted prism lost an edge")
        rooted_certificates.append(
            [root, opposite, left, right, left_residual, right_residual]
        )

    require(graph_nonedges == 4158, "nonedge count changed")
    require(induced_c4s == 2079, "induced C4 count changed")
    require(shape_counts == [0, 0, 1, 3], "two-triangle census changed")
    require(len(rooted_certificates) == 6, "prism root multiplicity changed")
    return {
        "graph_nonedges": graph_nonedges,
        "induced_C4_count": induced_c4s,
        "C4_counts_for_cross_matching_sizes_0_to_3": shape_counts,
        "n3_plus_3P": 2 * induced_c4s,
        "rooted_prism_certificates": rooted_certificates,
        "roots_per_prism": len(rooted_certificates),
        "rooted_identity": "sum_o f_o=6P",
    }


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def rooted_row(forbidden_transitions: int) -> dict[str, Any]:
    require(
        0 <= forbidden_transitions <= TRANSITIONS_PER_ROOT,
        "f_o outside its rooted range",
    )
    selected_seed_eligible = TRANSITIONS_PER_ROOT - forbidden_transitions
    first_moment = 8 * selected_seed_eligible
    pair_moment_upper = 9 * selected_seed_eligible
    bad_seed_rational_lower = (
        Fraction(first_moment, 2)
        - Fraction(pair_moment_upper, 6)
    )
    bad_seed_integer_lower = ceil_fraction(bad_seed_rational_lower)
    transition_free_upper = SEEDS_PER_ROOT - bad_seed_integer_lower
    floor_formula = (700 + 5 * forbidden_transitions) // 2
    require(
        bad_seed_rational_lower
        == Fraction(5 * selected_seed_eligible, 2),
        "rooted lower-bound simplification changed",
    )
    require(
        transition_free_upper == floor_formula,
        "rootwise ceiling/floor complement failed",
    )
    return {
        "f_o": forbidden_transitions,
        "seed_eligible_transitions": selected_seed_eligible,
        "first_moment": first_moment,
        "unordered_pair_moment_upper": pair_moment_upper,
        "bad_seed_rational_lower": str(bad_seed_rational_lower),
        "bad_seed_integer_lower": bad_seed_integer_lower,
        "transition_free_seed_upper": transition_free_upper,
        "root_bound_formula": "floor(350+5*f_o/2)",
    }


def even_distribution(total: int) -> list[int]:
    """Witness sharpness of the floor-sum relaxation under only 0<=f<=84."""

    require(total % 2 == 0, "total must be even")
    require(0 <= total <= V * TRANSITIONS_PER_ROOT, "total out of range")
    remaining = total
    values = []
    for _ in range(V):
        value = min(TRANSITIONS_PER_ROOT, remaining)
        require(value % 2 == 0, "greedy even distribution became odd")
        values.append(value)
        remaining -= value
    require(remaining == 0, "distribution capacity was insufficient")
    return values


def floor_sum_certificate(prisms: int) -> dict[str, Any]:
    require(0 <= prisms <= 1386, "P outside compatible identity domain")
    total_f = 6 * prisms
    # floor(350+5f/2) = 350 + (5f-(f mod 2))/2.
    # Since sum f=6P is even, the number of odd f values is even, and
    # the total is at most 99*350+15P.
    global_root_upper = V * 350 + 15 * prisms
    witness = even_distribution(total_f)
    witness_sum = sum((700 + 5 * value) // 2 for value in witness)
    require(sum(witness) == total_f, "floor witness has wrong sum")
    require(witness_sum == global_root_upper, "floor-sum cap not attained")
    return {
        "P": prisms,
        "sum_f_o": total_f,
        "identity": "sum_o floor(350+5*f_o/2)<=34650+15P",
        "parity_defect_formula": (
            "sum_o floor(5*f_o/2)=(5*sum_o f_o-#odd(f_o))/2"
        ),
        "global_rooted_incidence_upper": global_root_upper,
        "scalar_relaxation_sharp_under_box_and_sum_only": True,
    }


def compatible_rows() -> list[dict[str, int]]:
    rows = []
    for prisms in range(1387):
        n3 = 4158 - 3 * prisms
        floor_sum = floor_sum_certificate(prisms)
        numerator_from_prisms = floor_sum["global_rooted_incidence_upper"]
        numerator_from_n3 = 55440 - 5 * n3
        require(
            numerator_from_prisms == numerator_from_n3,
            "substitution to coefficient -5*n3 failed",
        )
        integral_bound = numerator_from_n3 // 7
        even_bound = 2 * (numerator_from_n3 // 14)
        require(even_bound % 2 == 0, "antipodal bound is not even")
        require(
            even_bound <= Fraction(numerator_from_n3, 7),
            "even bound exceeds the rational inequality",
        )
        require(
            even_bound + 2 > Fraction(numerator_from_n3, 7),
            "even bound is not the strongest antipodal rounding",
        )
        require(
            even_bound == integral_bound - (integral_bound % 2),
            "even-floor formulations disagree",
        )
        rows.append(
            {
                "n3": n3,
                "P": prisms,
                "rooted_numerator": numerator_from_n3,
                "integer_floor": integral_bound,
                "even_N14_upper": even_bound,
                "numerator_mod_14": numerator_from_n3 % 14,
            }
        )
    return rows


def row_digest(rows: list[dict[str, int]]) -> str:
    encoded = (
        json.dumps(rows, separators=(",", ":"), sort_keys=True) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def independent_result() -> dict[str, Any]:
    prism = prism_identity_certificate()
    applicability = local_applicability_certificate()
    root_rows = [rooted_row(forbidden) for forbidden in range(85)]
    rows = compatible_rows()
    endpoints = {
        str(n3): next(row for row in rows if row["n3"] == n3)
        for n3 in (4158, 4155, 708, 0)
    }
    parity_tightened = sum(
        row["even_N14_upper"] < row["integer_floor"] for row in rows
    )
    require(len(rows) == 1387, "compatible-row count changed")
    return {
        "format": "wave100-general-pair-moment-independent-v1",
        "role": "verifier",
        "claim_label": "PENDING_DISCOVERY_COMPARISON",
        "scope": {
            "hypothetical_graph": "srg(99,14,1,2)",
            "requires_P0": False,
            "requires_rank_28": False,
            "N14_counts_both_signs": True,
        },
        "prism_identity": prism,
        "local_applicability": applicability,
        "rootwise_moment": {
            "per_transition_coincidence_cap": applicability[
                "per_transition_coincidence_cap"
            ],
            "pair_moment_factor_per_seed_eligible_transition": 9,
            "rows_f_o_0_through_84_checked": len(root_rows),
            "endpoint_rows": {
                str(index): root_rows[index] for index in (0, 1, 2, 83, 84)
            },
            "theorem": "a14(o)<=floor(350+5*f_o/2)",
        },
        "floor_sum": {
            "root_count": V,
            "sum_f_identity": "sum_o f_o=6P",
            "inequality": (
                "sum_o floor(350+5*f_o/2)<=34650+15P"
            ),
            "direction": "UPPER",
            "parity_defect": (
                "the right side loses #odd(f_o)/2 from its maximum"
            ),
        },
        "global_bound": {
            "rooted_incidence_inequality": (
                "7*N14<=34650+15P=55440-5*n3"
            ),
            "P_form": "N14<=2*floor((34650+15P)/14)",
            "n3_form": "N14<=2*floor((55440-5*n3)/14)",
            "coefficient_of_n3": -5,
            "compatible_rows_checked": len(rows),
            "compatible_rows_sha256": row_digest(rows),
            "rows_tightened_by_antipodal_even_rounding": parity_tightened,
            "endpoint_rows": endpoints,
        },
        "precomparison_verdict": {
            "rootwise_ceiling_floor": "INDEPENDENTLY_REPRODUCED",
            "floor_sum_direction": "INDEPENDENTLY_REPRODUCED",
            "six_root_prism_factor": "INDEPENDENTLY_REPRODUCED",
            "coefficient_minus_five": "INDEPENDENTLY_REPRODUCED",
            "all_1387_even_roundings": "INDEPENDENTLY_REPRODUCED",
            "discovery_comparison": "NOT_YET_PERFORMED",
        },
        "status": {
            "general_N14_upper_bound": "DERIVED_PENDING_COMPARISON",
            "strict_n3_upper_bound": "NOT_PROVED",
            "graph_nonexistence": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The theorem bounds N14 as a function of n3; it does not bound n3.",
            "The floor-sum relaxation ignores additional prism-incidence compatibility.",
            "No graph existence or nonexistence conclusion follows.",
            "Novelty and literature priority are not assessed.",
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
        require(arguments.output.is_file(), "independent result is missing")
        require(
            arguments.output.read_text(encoding="utf-8") == rendered,
            "independent result mismatch",
        )
    else:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    print("PASS: Wave100 clean-room reconstruction")


if __name__ == "__main__":
    main()
