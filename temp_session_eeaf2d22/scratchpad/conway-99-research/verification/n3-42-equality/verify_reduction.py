#!/usr/bin/env python3
"""Structured checker for the proof-side Wave 12 ``n3 = 42`` reduction.

This standard-library program replays only the human finite reduction:

* all six active-``q`` profiles;
* the degree-at-least-three filter and degree-three obstruction;
* the size-four petal counts at active orders 13 and 14;
* the size-three ``t`` inequalities and ``(2,3,3)`` contradiction;
* the cubic point-intersection graph and open-twin obstruction; and
* the resulting all-size-two frontier.

The separate exact-support census that excludes the all-size-two frontier is
not imported or reproduced here.  The strengthened bound ``n3 >= 45`` is
reported only after a named external-exclusion premise is supplied.

This is a regression companion to a conditional proof.  It is not a
standalone certificate for nonexistence of ``srg(99,14,1,2)``.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from typing import Iterable, NamedTuple, Sequence


N3_EQUALITY = 42
ACTIVE_ORDER = 14
K_DEGREE = 7
U_BASE_DEGREE = 4
FIXED_POINT_COEFFICIENT = 4
INDUCED_C6_OFFSET = 209_286
WAVE6_BRANCH_DEGREES = (4, 8, 10, 12, 12, 6, 10, 12, 8, 12, 10, 12)

COMPLEMENT_PREMISE = "K_is_simple_complement_of_L_on_distinct_active_triangles"
POINT_CLIQUE_PREMISE = "every_active_point_set_is_a_clique_in_K"
LINEARITY_PREMISE = "point_hypergraph_is_linear"
COMMON_POINT_PREMISE = "common_point_Berge_triangle_is_forbidden"
CROSSING_PREMISE = "every_labeled_crossing_degree_is_zero_or_two"
FIXED_POINT_PREMISE = "fixed_point_H_degree_sum_is_four_times_point_size"
PROOF_PREMISES = frozenset(
    (
        COMPLEMENT_PREMISE,
        POINT_CLIQUE_PREMISE,
        LINEARITY_PREMISE,
        COMMON_POINT_PREMISE,
        CROSSING_PREMISE,
        FIXED_POINT_PREMISE,
    )
)

PRIOR_BOUND_PREMISE = "previous_verified_conditional_n3_lower_bound_is_42"
DIVISIBILITY_PREMISE = "n3_is_divisible_by_three"
EXTERNAL_SUPPORT_EXCLUSION_PREMISE = (
    "independent_exact_support_verifier_excludes_the_all_size_two_n3_42_frontier"
)
INDUCED_C6_PREMISE = "induced_C6_count_equals_209286_plus_n3"
INTEGRATION_PREMISES = PROOF_PREMISES | frozenset(
    (
        PRIOR_BOUND_PREMISE,
        DIVISIBILITY_PREMISE,
        EXTERNAL_SUPPORT_EXCLUSION_PREMISE,
        INDUCED_C6_PREMISE,
    )
)


class ReductionConfig(NamedTuple):
    """Constants exposed so mutation tests can attack proof coefficients."""

    active_order: int = ACTIVE_ORDER
    k_degree: int = K_DEGREE
    u_base_degree: int = U_BASE_DEGREE
    fixed_point_coefficient: int = FIXED_POINT_COEFFICIENT


DEFAULT_CONFIG = ReductionConfig()


def require_premises(premises: Iterable[str], required: Iterable[str]) -> None:
    """Reject a witness when a proof bridge that it uses is absent."""

    available = frozenset(premises)
    missing = frozenset(required) - available
    if missing:
        raise ValueError(f"missing proof premises: {sorted(missing)}")


def normalized_edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise ValueError("loops are not graph edges")
    return (left, right) if left < right else (right, left)


def active_q_sequences(n3_count: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate the Wave 7 active-``q`` multisets exactly."""

    if n3_count < 0 or (2 * n3_count) % 3:
        raise ValueError("2*n3 must be a nonnegative multiple of three")
    q_sum = 2 * n3_count // 3
    results: list[tuple[int, ...]] = []

    def visit(remaining: int, least: int, values: tuple[int, ...]) -> None:
        if remaining == 0:
            active_count = len(values)
            if values and all(3 * value <= active_count - 1 for value in values):
                results.append(values)
            return
        for value in range(least, min(12, remaining) + 1):
            visit(remaining - value, value, (*values, value))

    visit(q_sum, 2, ())
    return tuple(results)


def k_degree_profile(q_values: Sequence[int]) -> tuple[int, ...]:
    """Return degrees in ``K = complement(L[active])``."""

    active_count = len(q_values)
    return tuple(active_count - 1 - 3 * value for value in q_values)


def degree_filtered_profiles(
    profiles: Iterable[Sequence[int]],
    minimum_degree: int = 3,
) -> tuple[tuple[int, ...], ...]:
    """Keep profiles where three non-singleton point cliques can fit."""

    if minimum_degree < 0:
        raise ValueError("minimum degree must be nonnegative")
    return tuple(
        tuple(profile)
        for profile in profiles
        if min(k_degree_profile(profile), default=-1) >= minimum_degree
    )


def crossing_masks(left_order: int, right_order: int) -> tuple[int, ...]:
    """Enumerate simple bipartite masks whose degrees all lie in ``{0,2}``."""

    if left_order < 0 or right_order < 0:
        raise ValueError("crossing orders must be nonnegative")
    bit_count = left_order * right_order
    if bit_count > 16:
        raise ValueError("direct crossing enumeration is intentionally local")
    accepted = []
    for mask in range(1 << bit_count):
        left_degrees = [0] * left_order
        right_degrees = [0] * right_order
        for left in range(left_order):
            for right in range(right_order):
                if mask >> (left * right_order + right) & 1:
                    left_degrees[left] += 1
                    right_degrees[right] += 1
        if all(value in (0, 2) for value in (*left_degrees, *right_degrees)):
            accepted.append(mask)
    return tuple(accepted)


def crossing_edge_counts(left_order: int, right_order: int) -> frozenset[int]:
    return frozenset(mask.bit_count() for mask in crossing_masks(left_order, right_order))


def forbidden_common_point_triple(point_sets: Sequence[frozenset[int]]) -> bool:
    """Detect a Berge triangle of three distinct linear point sets."""

    if len(point_sets) != 3 or len(set(point_sets)) != 3:
        raise ValueError("three distinct point sets are required")
    intersections = [
        point_sets[left] & point_sets[right]
        for left, right in combinations(range(3), 2)
    ]
    return (
        all(len(intersection) == 1 for intersection in intersections)
        and len(set().union(*intersections)) == 3
    )


def degree_three_obstruction_witness(
    premises: Iterable[str] = PROOF_PREMISES,
) -> dict[str, object]:
    """Build the exact Berge-triangle witness at an active K-degree-three root."""

    require_premises(
        premises,
        (
            COMPLEMENT_PREMISE,
            POINT_CLIQUE_PREMISE,
            LINEARITY_PREMISE,
            COMMON_POINT_PREMISE,
            CROSSING_PREMISE,
        ),
    )
    if any(crossing_masks(1, order) != (0,) for order in (1, 2, 3)):
        raise AssertionError("a singleton-side crossing was nonempty")

    root = 0
    neighbors = (1, 2, 3)
    root_points = tuple(frozenset((root, vertex)) for vertex in neighbors)
    forced_neighbor_points = (
        frozenset((1, 2)),
        frozenset((1, 3)),
        frozenset((2, 3)),
    )
    if not forbidden_common_point_triple(forced_neighbor_points):
        raise AssertionError("the forced neighbor point sets lost their Berge triangle")
    return {
        "root": root,
        "k_degree": len(neighbors),
        "root_points": root_points,
        "available_external_neighbors_at_each_neighbor": 2,
        "forced_neighbor_points": forced_neighbor_points,
        "common_point_contradiction": True,
    }


def maximum_point_size(active_order: int) -> int:
    """Largest ``s`` satisfying the expansion inequality ``2s <= n-s``."""

    if active_order < 2:
        raise ValueError("active order must be at least two")
    feasible = [
        size
        for size in range(2, active_order + 1)
        if 2 * size <= active_order - size
    ]
    return max(feasible, default=1)


def size_four_flower_statistics(
    active_order: int,
    premises: Iterable[str] = PROOF_PREMISES,
) -> dict[str, object]:
    """Exhaust the ``3^8`` petal-size words around a size-four point."""

    require_premises(
        premises,
        (
            COMPLEMENT_PREMISE,
            POINT_CLIQUE_PREMISE,
            LINEARITY_PREMISE,
            COMMON_POINT_PREMISE,
            CROSSING_PREMISE,
        ),
    )
    if active_order < 12:
        raise ValueError("this flower audit is intended for active orders at least twelve")
    if crossing_masks(1, 3) != (0,) or crossing_masks(3, 1) != (0,):
        raise AssertionError("a singleton-size-four crossing was nonempty")

    total = 0
    feasible = 0
    singleton_histogram: Counter[int] = Counter()
    type_224_histogram: Counter[int] = Counter()
    minimum_singleton_petals = 8
    minimum_type_224 = 4
    minimum_root_degree = active_order
    outside_capacity = active_order - 4

    for petals in product((2, 3, 4), repeat=8):
        total += 1
        if sum(size - 1 for size in petals) > outside_capacity:
            continue
        feasible += 1
        singleton_petals = petals.count(2)
        type_224 = sum(
            petals[offset] == petals[offset + 1] == 2
            for offset in range(0, 8, 2)
        )
        root_degree = 3 + singleton_petals
        singleton_histogram[singleton_petals] += 1
        type_224_histogram[type_224] += 1
        minimum_singleton_petals = min(minimum_singleton_petals, singleton_petals)
        minimum_type_224 = min(minimum_type_224, type_224)
        minimum_root_degree = min(minimum_root_degree, root_degree)

    return {
        "active_order": active_order,
        "total_profiles": total,
        "capacity_rejections": total - feasible,
        "feasible_profiles": feasible,
        "outside_capacity": outside_capacity,
        "singleton_petal_histogram": dict(sorted(singleton_histogram.items())),
        "type_224_histogram": dict(sorted(type_224_histogram.items())),
        "minimum_singleton_petals": minimum_singleton_petals,
        "minimum_type_224_occurrences": minimum_type_224,
        "minimum_root_degree": minimum_root_degree,
    }


def t_triple_satisfies_u_inequalities(
    t_values: Sequence[int],
    u_base_degree: int = U_BASE_DEGREE,
) -> bool:
    """Check ``u_base-t_i >= (3-t_j)+(3-t_k)`` cyclically."""

    if len(t_values) != 3 or any(value not in (1, 2, 3) for value in t_values):
        raise ValueError("a t-triple has three entries in {1,2,3}")
    if u_base_degree < 0:
        raise ValueError("U base degree must be nonnegative")
    return all(
        u_base_degree - t_values[index]
        >= sum(3 - t_values[other] for other in range(3) if other != index)
        for index in range(3)
    )


def admissible_size_three_t_triples(
    active_order: int = ACTIVE_ORDER,
    u_base_degree: int = U_BASE_DEGREE,
) -> tuple[tuple[int, int, int], ...]:
    """Enumerate sorted t-triples after petal capacity and U-degree forcing."""

    if active_order < 6:
        raise ValueError("active order is too small for this reduction")
    accepted = []
    for values in combinations_with_replacement((1, 2, 3), 3):
        external_slots = 3 + sum(values)
        if external_slots > active_order - 3:
            continue
        if t_triple_satisfies_u_inequalities(values, u_base_degree):
            accepted.append(values)
    return tuple(accepted)


def t_profile_233_exclusion_witness(
    fixed_point_coefficient: int = FIXED_POINT_COEFFICIENT,
    premises: Iterable[str] = PROOF_PREMISES,
) -> dict[str, object]:
    """Replay the fixed-point contradiction for t-profile ``(2,3,3)``."""

    require_premises(
        premises,
        (
            COMPLEMENT_PREMISE,
            LINEARITY_PREMISE,
            COMMON_POINT_PREMISE,
            CROSSING_PREMISE,
            FIXED_POINT_PREMISE,
        ),
    )
    if fixed_point_coefficient <= 0:
        raise ValueError("fixed-point coefficient must be positive")
    if crossing_edge_counts(2, 2) != frozenset((0, 4)):
        raise AssertionError("the 2-by-2 crossing dichotomy changed")

    t_profile = (2, 3, 3)
    u_degrees = tuple(U_BASE_DEGREE - value for value in t_profile)
    co_points_by_occurrence = tuple(value - 1 for value in t_profile)
    distinct_co_points = sum(co_points_by_occurrence)
    h_degree_per_forced_crossing = 4
    forced_h_contribution = distinct_co_points * h_degree_per_forced_crossing
    fixed_point_total = fixed_point_coefficient * 3
    return {
        "t_profile": t_profile,
        "u_degrees": u_degrees,
        "saturated_t3_roots": 2,
        "co_points_by_occurrence": co_points_by_occurrence,
        "distinct_co_points": distinct_co_points,
        "h_degree_per_forced_crossing": h_degree_per_forced_crossing,
        "forced_h_contribution": forced_h_contribution,
        "fixed_point_total": fixed_point_total,
        "contradiction": forced_h_contribution > fixed_point_total,
    }


def candidate_cubic_r_orders(active_order: int = ACTIVE_ORDER) -> tuple[int, ...]:
    """Orders allowed by ``e=3m/2`` and ``e <= 3(active_order-e)``."""

    if active_order < 4:
        raise ValueError("active order must be at least four")
    candidates = []
    for order in range(4, active_order + 1, 2):
        edge_count = 3 * order // 2
        if edge_count <= 3 * (active_order - edge_count):
            candidates.append(order)
    return tuple(candidates)


def cubic_graphs(order: int) -> tuple[frozenset[tuple[int, int]], ...]:
    """Enumerate labeled simple cubic graphs at the only needed small orders."""

    if order not in (4, 6):
        raise ValueError("the proof-side cubic census only needs orders four and six")
    all_edges = tuple(combinations(range(order), 2))
    edge_count = 3 * order // 2
    results = []
    for chosen in combinations(all_edges, edge_count):
        degrees = Counter(vertex for edge in chosen for vertex in edge)
        if all(degrees[vertex] == 3 for vertex in range(order)):
            results.append(frozenset(normalized_edge(*edge) for edge in chosen))
    return tuple(results)


def contains_triangle(edges: frozenset[tuple[int, int]], order: int) -> bool:
    return any(
        all(normalized_edge(*edge) in edges for edge in combinations(vertices, 2))
        for vertices in combinations(range(order), 3)
    )


def is_k33(edges: frozenset[tuple[int, int]]) -> bool:
    """Recognize a labeled copy of ``K3,3`` on six vertices."""

    if len(edges) != 9:
        return False
    for first_side in combinations(range(6), 3):
        if 0 not in first_side:
            continue
        first = set(first_side)
        second = set(range(6)) - first
        expected = {
            normalized_edge(left, right)
            for left in first
            for right in second
        }
        if edges == expected:
            return True
    return False


def line_graph_open_neighborhoods(
    edges: frozenset[tuple[int, int]],
) -> tuple[frozenset[int], ...]:
    """Return open neighborhoods in the line graph of ``edges``."""

    ordered = tuple(sorted(edges))
    return tuple(
        frozenset(
            other_index
            for other_index, other in enumerate(ordered)
            if other_index != index and set(edge) & set(other)
        )
        for index, edge in enumerate(ordered)
    )


def has_open_twins(neighborhoods: Sequence[frozenset[int]]) -> bool:
    """Whether two distinct vertices have the same open neighborhood."""

    return len(set(neighborhoods)) != len(neighborhoods)


def cubic_r_statistics(active_order: int = ACTIVE_ORDER) -> dict[str, object]:
    """Check the order-four/order-six classification and the twin injection."""

    candidates = candidate_cubic_r_orders(active_order)
    cubic_four = cubic_graphs(4)
    triangle_free_four = tuple(
        graph for graph in cubic_four if not contains_triangle(graph, 4)
    )
    cubic_six = cubic_graphs(6)
    triangle_free_six = tuple(
        graph for graph in cubic_six if not contains_triangle(graph, 6)
    )
    all_k33 = all(is_k33(graph) for graph in triangle_free_six)
    twin_free = all(
        not has_open_twins(line_graph_open_neighborhoods(graph))
        for graph in triangle_free_six
    )
    edge_labels = 9
    t0_labels = active_order - edge_labels
    return {
        "candidate_orders": candidates,
        "labeled_cubic_order_4": len(cubic_four),
        "triangle_free_cubic_order_4": len(triangle_free_four),
        "labeled_cubic_order_6": len(cubic_six),
        "triangle_free_cubic_order_6": len(triangle_free_six),
        "all_triangle_free_order_6_are_k33": all_k33,
        "all_k33_line_graphs_open_twin_free": twin_free,
        "k33_edge_labels": edge_labels,
        "available_t0_labels": t0_labels,
        "injection_possible": edge_labels <= t0_labels,
    }


def all_size_two_frontier() -> dict[str, object]:
    """Return the exact endpoint of this proof-side checker."""

    incidence_count = 3 * ACTIVE_ORDER
    if incidence_count % 2:
        raise AssertionError("the all-size-two incidence count became odd")
    point_count = incidence_count // 2
    return {
        "active_order": ACTIVE_ORDER,
        "point_count": point_count,
        "F_degree": 3,
        "F_edge_count": point_count,
        "F_triangle_free": True,
        "K_degree": K_DEGREE,
        "U_degree": K_DEGREE - 3,
        "L_degree": ACTIVE_ORDER - 1 - K_DEGREE,
        "terminal_state": "all_size_two_exact_H_support_frontier",
        "excluded_by_this_checker": False,
    }


def ceil_multiple_of_three(value: int) -> int:
    if value < 0:
        raise ValueError("value must be nonnegative")
    return 3 * ((value + 2) // 3)


def strengthened_bounds(
    premises: Iterable[str] = INTEGRATION_PREMISES,
) -> dict[str, object]:
    """Integrate the external equality exclusion with prior global bounds."""

    require_premises(
        premises,
        PROOF_PREMISES
        | frozenset(
            (
                PRIOR_BOUND_PREMISE,
                DIVISIBILITY_PREMISE,
                EXTERNAL_SUPPORT_EXCLUSION_PREMISE,
                INDUCED_C6_PREMISE,
            )
        ),
    )
    if N3_EQUALITY % 3:
        raise AssertionError("the equality value is no longer divisible by three")
    global_bound = N3_EQUALITY + 3
    branch_bounds = tuple(
        max(global_bound, ceil_multiple_of_three(4 * degree))
        for degree in WAVE6_BRANCH_DEGREES
    )
    return {
        "conditional": True,
        "external_support_exclusion_checked_here": False,
        "external_support_exclusion_premise": EXTERNAL_SUPPORT_EXCLUSION_PREMISE,
        "global_n3_lower_bound": global_bound,
        "global_induced_C6_lower_bound": INDUCED_C6_OFFSET + global_bound,
        "branch_n3_bounds": branch_bounds,
        "claim_label": "DERIVED",
        "target_result": "UNKNOWN",
    }


def audit_reduction(
    config: ReductionConfig = DEFAULT_CONFIG,
    integration_premises: Iterable[str] = INTEGRATION_PREMISES,
) -> dict[str, object]:
    """Run all strict proof-side assertions and return structured results."""

    q42 = active_q_sequences(N3_EQUALITY)
    expected_q42 = (
        (2,) * 14,
        (2,) * 12 + (4,),
        (2,) * 11 + (3, 3),
        (2,) * 8 + (3,) * 4,
        (2,) * 5 + (3,) * 6,
        (2,) * 2 + (3,) * 8,
    )
    if q42 != expected_q42:
        raise AssertionError(f"unexpected n3=42 active profiles: {q42}")

    degree_histograms = tuple(Counter(k_degree_profile(profile)) for profile in q42)
    expected_histograms = (
        Counter({7: 14}),
        Counter({6: 12, 0: 1}),
        Counter({6: 11, 3: 2}),
        Counter({5: 8, 2: 4}),
        Counter({4: 5, 1: 6}),
        Counter({3: 2, 0: 8}),
    )
    if degree_histograms != expected_histograms:
        raise AssertionError("the six K-degree profiles changed")

    filtered = degree_filtered_profiles(q42)
    expected_filtered = ((2,) * 14, (2,) * 11 + (3, 3))
    if filtered != expected_filtered:
        raise AssertionError(f"wrong degree-filter survivors: {filtered}")
    degree_three = degree_three_obstruction_witness()
    if not degree_three["common_point_contradiction"]:
        raise AssertionError("the degree-three profile survived")

    if config.active_order != ACTIVE_ORDER or config.k_degree != K_DEGREE:
        raise AssertionError("the active-order/K-degree constants were mutated")
    if maximum_point_size(13) != 4 or maximum_point_size(config.active_order) != 4:
        raise AssertionError("the expansion point-size bound changed")

    flower13 = size_four_flower_statistics(13)
    flower14 = size_four_flower_statistics(config.active_order)
    expected_flower13 = {
        "feasible_profiles": 9,
        "capacity_rejections": 6552,
        "singleton_petal_histogram": {7: 8, 8: 1},
        "type_224_histogram": {3: 8, 4: 1},
        "minimum_singleton_petals": 7,
        "minimum_type_224_occurrences": 3,
        "minimum_root_degree": 10,
    }
    expected_flower14 = {
        "feasible_profiles": 45,
        "capacity_rejections": 6516,
        "singleton_petal_histogram": {6: 28, 7: 16, 8: 1},
        "type_224_histogram": {2: 24, 3: 20, 4: 1},
        "minimum_singleton_petals": 6,
        "minimum_type_224_occurrences": 2,
        "minimum_root_degree": 9,
    }
    for key, value in expected_flower13.items():
        if flower13[key] != value:
            raise AssertionError(f"order-13 size-four statistic changed: {key}")
    for key, value in expected_flower14.items():
        if flower14[key] != value:
            raise AssertionError(f"order-14 size-four statistic changed: {key}")
    if flower14["minimum_root_degree"] <= config.k_degree:
        raise AssertionError("a size-four flower escaped the K-degree contradiction")

    t_triples = admissible_size_three_t_triples(
        config.active_order,
        config.u_base_degree,
    )
    if t_triples != ((2, 2, 2), (2, 3, 3)):
        raise AssertionError(f"the admissible t-triples changed: {t_triples}")
    t233 = t_profile_233_exclusion_witness(config.fixed_point_coefficient)
    if t233["fixed_point_total"] != 12 or not t233["contradiction"]:
        raise AssertionError("the (2,3,3) fixed-point contradiction changed")

    cubic = cubic_r_statistics(config.active_order)
    expected_cubic = {
        "candidate_orders": (4, 6),
        "labeled_cubic_order_4": 1,
        "triangle_free_cubic_order_4": 0,
        "labeled_cubic_order_6": 70,
        "triangle_free_cubic_order_6": 10,
        "all_triangle_free_order_6_are_k33": True,
        "all_k33_line_graphs_open_twin_free": True,
        "k33_edge_labels": 9,
        "available_t0_labels": 5,
        "injection_possible": False,
    }
    if cubic != expected_cubic:
        raise AssertionError(f"the cubic-R obstruction changed: {cubic}")

    frontier = all_size_two_frontier()
    if frontier["point_count"] != 21 or frontier["excluded_by_this_checker"]:
        raise AssertionError("the proof-side terminal frontier changed")

    bounds = strengthened_bounds(integration_premises)
    expected_branch_bounds = (
        45,
        45,
        45,
        48,
        48,
        45,
        45,
        48,
        45,
        48,
        45,
        48,
    )
    if bounds["global_n3_lower_bound"] != 45:
        raise AssertionError("the integrated global n3 bound changed")
    if bounds["global_induced_C6_lower_bound"] != 209_331:
        raise AssertionError("the integrated induced-C6 bound changed")
    if bounds["branch_n3_bounds"] != expected_branch_bounds:
        raise AssertionError("the integrated branch bounds changed")
    if bounds["target_result"] != "UNKNOWN":
        raise AssertionError("target status inflation detected")

    return {
        "raw_q_profiles": q42,
        "k_degree_histograms": degree_histograms,
        "degree_filter_survivors": filtered,
        "degree_three_witness": degree_three,
        "size_four_order_13": flower13,
        "size_four_order_14": flower14,
        "admissible_size_three_t_triples": t_triples,
        "t_profile_233_witness": t233,
        "cubic_r": cubic,
        "proof_side_frontier": frontier,
        "integrated_bounds": bounds,
    }


def verify() -> dict[str, object]:
    """Run the checker and print a stable, human-readable summary."""

    result = audit_reduction()
    bounds = result["integrated_bounds"]
    frontier = result["proof_side_frontier"]
    print("PASS conditional n3=42 proof-side reduction")
    print("claim_label", bounds["claim_label"])
    print("conditional", str(bounds["conditional"]).lower())
    print("raw_q_profile_count", len(result["raw_q_profiles"]))
    print(
        "degree_filter_active_orders",
        [len(profile) for profile in result["degree_filter_survivors"]],
    )
    print(
        "size_four_feasible_profiles_order_13_14",
        [
            result["size_four_order_13"]["feasible_profiles"],
            result["size_four_order_14"]["feasible_profiles"],
        ],
    )
    print(
        "admissible_size_three_t_triples",
        [list(values) for values in result["admissible_size_three_t_triples"]],
    )
    print("proof_side_terminal_state", frontier["terminal_state"])
    print(
        "external_support_exclusion_checked_here",
        str(bounds["external_support_exclusion_checked_here"]).lower(),
    )
    print(
        "external_support_exclusion_premise",
        bounds["external_support_exclusion_premise"],
    )
    print("conditional_global_n3_lower_bound", bounds["global_n3_lower_bound"])
    print(
        "conditional_global_induced_C6_lower_bound",
        bounds["global_induced_C6_lower_bound"],
    )
    print("conditional_branch_n3_bounds", list(bounds["branch_n3_bounds"]))
    print("target_result", bounds["target_result"])
    return result


def main(argv: Sequence[str] | None = None) -> int:
    if argv:
        raise ValueError("this checker takes no arguments")
    verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
