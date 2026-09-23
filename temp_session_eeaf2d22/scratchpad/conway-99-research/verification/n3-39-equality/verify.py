#!/usr/bin/env python3
"""Exact finite checks for the Wave 11 exclusion of ``n3 = 39``.

The human proof supplies the reduction from a putative ``srg(99,14,1,2)``
to thirteen active graph-triangles.  On those triangles ``L`` is the side
graph and ``K`` is explicitly the simple complement of ``L``.  This compact,
standard-library checker replays the finite arithmetic and every local branch
of the repaired point-incidence proof.

It is a regression companion to a conditional proof, not a standalone
nonexistence certificate for the Conway graph.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from typing import Iterable, Sequence


ACTIVE_ORDER = 13
K_DEGREE = 6
K_EDGE_COUNT = ACTIVE_ORDER * K_DEGREE // 2
WAVE6_BRANCH_DEGREES = (4, 8, 10, 12, 12, 6, 10, 12, 8, 12, 10, 12)
COMPLEMENT_PREMISE = "K_is_simple_complement_of_L_on_distinct_active_triangles"
POINT_CLIQUE_PREMISE = "every_active_point_set_is_a_clique_in_K"
LINEARITY_PREMISE = "point_hypergraph_is_linear"
COMMON_POINT_PREMISE = "common_point_Berge_triangle_is_forbidden"
CROSSING_PREMISE = "every_labeled_crossing_degree_is_zero_or_two"
PROOF_PREMISES = frozenset(
    (
        COMPLEMENT_PREMISE,
        POINT_CLIQUE_PREMISE,
        LINEARITY_PREMISE,
        COMMON_POINT_PREMISE,
        CROSSING_PREMISE,
    )
)


def active_q_sequences(n3_count: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate active-q multisets from the Wave 7 handshake constraints."""

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


def forced_singletons_at_triangle(k_degree: int) -> int:
    """Three nonempty point cliques compete for distinct incident K-edges."""

    if k_degree < 0:
        raise ValueError("K-degree must be nonnegative")
    return max(0, 3 - k_degree)


def crossing_masks(left_order: int, right_order: int) -> tuple[int, ...]:
    """Enumerate simple bipartite masks with every degree in ``{0,2}``."""

    if left_order < 0 or right_order < 0:
        raise ValueError("crossing orders must be nonnegative")
    bit_count = left_order * right_order
    if bit_count > 20:
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


def local_point_types(k_degree: int = K_DEGREE) -> tuple[tuple[int, int, int], ...]:
    """Enumerate sorted sizes of the three point sets through one triangle."""

    if k_degree < 3:
        raise ValueError("three non-singleton point sets need degree at least three")
    return tuple(
        sizes
        for sizes in combinations_with_replacement(range(2, k_degree + 2), 3)
        if sum(size - 1 for size in sizes) <= k_degree
    )


def forbidden_common_point_triple(point_sets: Sequence[frozenset[int]]) -> bool:
    """Detect a Berge triangle of three distinct linear point sets."""

    if len(point_sets) != 3 or len(set(point_sets)) != 3:
        raise ValueError("three distinct point sets are required")
    intersections = [
        point_sets[left] & point_sets[right]
        for left, right in combinations(range(3), 2)
    ]
    return all(len(item) == 1 for item in intersections) and len(set().union(*intersections)) == 3


def require_premises(premises: Iterable[str], required: Iterable[str]) -> None:
    """Reject a local witness when a proof bridge it uses is absent."""

    available = frozenset(premises)
    missing = frozenset(required) - available
    if missing:
        raise ValueError(f"missing proof premises: {sorted(missing)}")


def edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise ValueError("loops are not edges")
    return (left, right) if left < right else (right, left)


def clique_edges(vertices: Iterable[int]) -> frozenset[tuple[int, int]]:
    return frozenset(edge(left, right) for left, right in combinations(sorted(vertices), 2))


def type_233_u_witness(
    premises: Iterable[str] = PROOF_PREMISES,
) -> dict[str, object]:
    """Build the exact four-edge U-degree witness at a 233 occurrence."""

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
    if crossing_masks(2, 1) != (0,) or crossing_masks(1, 2) != (0,):
        raise AssertionError("a singleton-side type-233 crossing was nonempty")
    root = frozenset((0, 1, 2))
    size_two = frozenset((0, 3))
    size_three = frozenset((0, 4, 5))
    attempted = (
        (root, size_two, 1, 3),
        (root, size_two, 2, 3),
        (size_two, size_three, 3, 4),
        (size_two, size_three, 3, 5),
    )
    forced_k_edges = frozenset(edge(left, right) for _p, _q, left, right in attempted)
    forbidden_f_owners = frozenset(
        edge(left, right)
        for point_left, point_right, left, right in attempted
        if forbidden_common_point_triple(
            (point_left, point_right, frozenset((left, right)))
        )
    )
    if forbidden_f_owners != forced_k_edges:
        raise AssertionError("a forced type-233 edge acquired an F-owner")
    endpoint_degree = sum(3 in item for item in forced_k_edges)
    if endpoint_degree != 4:
        raise AssertionError("the type-233 four-edge witness changed")
    return {
        "forced_k_edges": forced_k_edges,
        "forbidden_f_owners": forbidden_f_owners,
        "forced_u_edges": forced_k_edges,
        "size_two_endpoint": 3,
        "size_two_endpoint_u_degree": endpoint_degree,
        "maximum_available_u_degree": 3,
    }


def two_224_root_degree_witness(
    premises: Iterable[str] = PROOF_PREMISES,
    *,
    use_complement: bool = True,
) -> dict[str, object]:
    """Build two 224 occurrences and list every forced K-neighbor."""

    required = (POINT_CLIQUE_PREMISE, LINEARITY_PREMISE, COMMON_POINT_PREMISE)
    if use_complement:
        required = (*required, COMPLEMENT_PREMISE, CROSSING_PREMISE)
    require_premises(premises, required)
    if use_complement and crossing_masks(3, 1) != (0,):
        raise AssertionError("a singleton-side 224 crossing was nonempty")
    root = frozenset((0, 1, 2, 3))
    based_endpoints = {0: frozenset((4, 5)), 1: frozenset((6, 7))}
    endpoints = frozenset().union(*based_endpoints.values())
    point_clique_endpoint_edges = frozenset(
        edge(base, endpoint)
        for base, values in based_endpoints.items()
        for endpoint in values
    )
    complement_edges = frozenset()
    if use_complement:
        complement_edges = frozenset(
            edge(root_vertex, endpoint)
            for base, values in based_endpoints.items()
            for endpoint in values
            for root_vertex in root - {base}
        )
    forced_edges = clique_edges(root) | point_clique_endpoint_edges | complement_edges
    neighbors = {
        vertex: frozenset(
            right if left == vertex else left
            for left, right in forced_edges
            if vertex in (left, right)
        )
        for vertex in root
    }
    return {
        "root": root,
        "endpoints": endpoints,
        "point_clique_endpoint_edges": point_clique_endpoint_edges,
        "complement_inferred_endpoint_edges": complement_edges,
        "neighbors": neighbors,
        "degrees": tuple(len(neighbors[vertex]) for vertex in sorted(root)),
    }


def homogeneous_root3_u_witness(
    pairs: Sequence[tuple[int, int]],
    premises: Iterable[str] = PROOF_PREMISES,
) -> dict[str, object]:
    """Construct exact forced-U endpoint sets for a no-233 flower."""

    if len(pairs) != 3 or any(pair not in ((2, 2), (3, 3)) for pair in pairs):
        raise ValueError("three homogeneous 223/333 occurrence pairs are required")
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
    if crossing_masks(2, 1) != (0,):
        raise AssertionError("a singleton-side root/petal crossing was nonempty")
    root_point = frozenset((0, 1, 2))
    endpoints = {
        root: frozenset((3 + 2 * root, 4 + 2 * root))
        for root, pair in enumerate(pairs)
        if pair == (2, 2)
    }
    petal_points = {
        base: tuple(frozenset((base, endpoint)) for endpoint in sorted(values))
        for base, values in endpoints.items()
    }
    forced_edge_sets: dict[int, frozenset[tuple[int, int]]] = {}
    owner_veto_sets: dict[int, frozenset[tuple[int, int]]] = {}
    for root_vertex in range(3):
        forced = frozenset(
            edge(root_vertex, endpoint)
            for base, values in endpoints.items()
            if base != root_vertex
            for endpoint in values
        )
        vetoes = frozenset(
            edge(root_vertex, endpoint)
            for base, points in petal_points.items()
            if base != root_vertex
            for point in points
            for endpoint in point - {base}
            if forbidden_common_point_triple(
                (root_point, point, frozenset((root_vertex, endpoint)))
            )
        )
        if vetoes != forced:
            raise AssertionError("a forced propagation edge acquired an F-owner")
        forced_edge_sets[root_vertex] = forced
        owner_veto_sets[root_vertex] = vetoes
    capacities = tuple(2 - pair.count(3) for pair in pairs)
    forced = tuple(len(forced_edge_sets[root]) for root in range(3))
    return {
        "capacities": capacities,
        "endpoint_sets": endpoints,
        "forced_u_edges": forced_edge_sets,
        "forbidden_f_owners": owner_veto_sets,
        "forced_u_cardinalities": forced,
        "violating_roots": tuple(
            root for root in range(3) if forced[root] > capacities[root]
        ),
    }


def expansion_bound(point_size: int) -> tuple[int, int, bool]:
    """Return available vertices, required external representatives, feasibility."""

    if not 2 <= point_size <= ACTIVE_ORDER:
        raise ValueError("active point size must lie between two and thirteen")
    available = ACTIVE_ORDER - point_size
    required = 2 * point_size
    return available, required, required <= available


def point_resource_profiles() -> tuple[tuple[int, int, int], ...]:
    """Enumerate size-2/3/4 incidence profiles before local elimination."""

    profiles = []
    for x4 in range(10):
        for x3 in range(14):
            for x2 in range(20):
                if 2 * x2 + 3 * x3 + 4 * x4 != 3 * ACTIVE_ORDER:
                    continue
                consumed = x2 + 3 * x3 + 6 * x4
                if consumed <= K_EDGE_COUNT:
                    profiles.append((x2, x3, x4))
    return tuple(profiles)


def flower_crossing_extensions(root_size: int, petals: Sequence[int]) -> int:
    """Count all local degree-{0,2} crossing choices for an ordered flower."""

    if len(petals) % 2:
        raise ValueError("petals must occur in pairs")
    root_external = root_size - 1
    count = 1
    for offset in range(0, len(petals), 2):
        left_external = petals[offset] - 1
        right_external = petals[offset + 1] - 1
        count *= len(crossing_masks(root_external, left_external))
        count *= len(crossing_masks(root_external, right_external))
        count *= len(crossing_masks(left_external, right_external))
    return count


def size_four_flower_statistics() -> dict[str, int]:
    """Exhaust all ordered petal-size profiles around a size-four point."""

    total = 0
    capacity_rejections = 0
    feasible = 0
    minimum_224 = 4
    crossing_extensions = 0
    minimum_root_degree = ACTIVE_ORDER
    type_224_histogram = Counter()
    witness = two_224_root_degree_witness()
    if witness["degrees"] != (7, 7, 7, 7):
        raise AssertionError("the explicit two-224 complement witness changed")
    for petals in product((2, 3, 4), repeat=8):
        total += 1
        external_slots = sum(size - 1 for size in petals)
        if external_slots > ACTIVE_ORDER - 4:
            capacity_rejections += 1
            continue
        feasible += 1
        type_224 = sum(
            petals[offset] == petals[offset + 1] == 2
            for offset in range(0, 8, 2)
        )
        type_224_histogram[type_224] += 1
        minimum_224 = min(minimum_224, type_224)
        extensions = flower_crossing_extensions(4, petals)
        crossing_extensions += extensions
        # Any two 224 occurrences instantiate the exact seven-neighbor witness.
        root_degree_lower = min(witness["degrees"])
        minimum_root_degree = min(minimum_root_degree, root_degree_lower)
        if type_224 < 3 or root_degree_lower <= K_DEGREE:
            raise AssertionError("a size-four flower escaped its degree contradiction")
    return {
        "total_profiles": total,
        "capacity_rejections": capacity_rejections,
        "feasible_profiles": feasible,
        "minimum_type_224_occurrences": minimum_224,
        "crossing_extensions": crossing_extensions,
        "minimum_root_degree_lower": minimum_root_degree,
        "type_224_histogram": dict(sorted(type_224_histogram.items())),
    }


def u_degree(size_three_points: int) -> int:
    """Degree in ``U=K-F`` after point-clique edges are removed."""

    if not 0 <= size_three_points <= 3:
        raise ValueError("a triangle has between zero and three size-three points")
    return K_DEGREE - (3 + size_three_points)


def size_three_flower_statistics() -> dict[str, int]:
    """Exhaust all ordered size-2/3 petals around a size-three point."""

    classifications = Counter()
    overlap = Counter()
    extension_totals = Counter()
    homogeneous_223_histogram = Counter()
    total = 0
    for petals in product((2, 3), repeat=6):
        total += 1
        external_slots = sum(size - 1 for size in petals)
        pairs = tuple((petals[offset], petals[offset + 1]) for offset in range(0, 6, 2))
        extensions = flower_crossing_extensions(3, petals)
        over_capacity = external_slots > ACTIVE_ORDER - 3
        if any(left != right for left, right in pairs):
            classifications["has_233"] += 1
            overlap[("has_233", over_capacity)] += 1
            witness = type_233_u_witness()
            if witness["size_two_endpoint_u_degree"] <= witness["maximum_available_u_degree"]:
                raise AssertionError("the type-233 U-degree contradiction disappeared")
            extension_totals["type_233_raw"] += extensions
            extension_totals[
                "type_233_over_capacity" if over_capacity else "type_233_capacity_feasible"
            ] += extensions
            continue

        type_223 = sum(pair == (2, 2) for pair in pairs)
        type_333 = 3 - type_223
        if type_333 == 3:
            classifications["all_333"] += 1
            overlap[("all_333", over_capacity)] += 1
            extension_totals["all_333_raw"] += extensions
            if not over_capacity or external_slots != 12:
                raise AssertionError("the unique all-333 capacity witness changed")
            continue

        classifications["has_223_no_233"] += 1
        overlap[("has_223_no_233", over_capacity)] += 1
        homogeneous_223_histogram[type_223] += 1
        witness = homogeneous_root3_u_witness(pairs)
        if not witness["violating_roots"]:
            raise AssertionError(
                f"a 223/333 root pattern survived: petals={petals}, types={(type_223, type_333)}"
            )
        extension_totals["root_223_333"] += extensions

    return {
        "total_profiles": total,
        "profiles_with_type_233": classifications["has_233"],
        "all_333_profiles": classifications["all_333"],
        "profiles_with_223_no_233": classifications["has_223_no_233"],
        "type_233_capacity_feasible_profiles": overlap[("has_233", False)],
        "type_233_over_capacity_profiles": overlap[("has_233", True)],
        "all_333_over_capacity_profiles": overlap[("all_333", True)],
        "homogeneous_223_over_capacity_profiles": overlap[("has_223_no_233", True)],
        "profiles_by_type_223_count": dict(sorted(homogeneous_223_histogram.items())),
        "type_233_raw_crossing_extensions": extension_totals["type_233_raw"],
        "type_233_capacity_feasible_crossing_extensions": extension_totals[
            "type_233_capacity_feasible"
        ],
        "type_233_over_capacity_crossing_extensions": extension_totals[
            "type_233_over_capacity"
        ],
        "all_333_raw_crossing_extensions": extension_totals["all_333_raw"],
        "root_223_333_crossing_extensions": extension_totals["root_223_333"],
        "all_raw_crossing_extensions": sum(
            extension_totals[key]
            for key in ("type_233_raw", "all_333_raw", "root_223_333")
        ),
    }


def ceil_multiple_of_three(value: int) -> int:
    return 3 * ((value + 2) // 3)


def verify() -> None:
    q39 = active_q_sequences(39)
    expected_q39 = (
        (2,) * 13,
        (2,) * 10 + (3, 3),
        (2,) * 7 + (3,) * 4,
        (2,) * 4 + (3,) * 6,
    )
    if q39 != expected_q39:
        raise AssertionError(f"unexpected n3=39 active profiles: {q39}")

    degree_profiles = tuple(k_degree_profile(profile) for profile in q39)
    expected_histograms = (
        Counter({6: 13}),
        Counter({5: 10, 2: 2}),
        Counter({4: 7, 1: 4}),
        Counter({3: 4, 0: 6}),
    )
    if tuple(Counter(profile) for profile in degree_profiles) != expected_histograms:
        raise AssertionError("wrong K-degree profiles")
    mixed_forced_singletons = tuple(
        sum(forced_singletons_at_triangle(degree) for degree in profile if degree < 3)
        for profile in degree_profiles[1:]
    )
    if mixed_forced_singletons != (2, 8, 18):
        raise AssertionError("mixed-profile singleton count changed")

    point_types = local_point_types()
    expected_types = (
        (2, 2, 2),
        (2, 2, 3),
        (2, 2, 4),
        (2, 2, 5),
        (2, 3, 3),
        (2, 3, 4),
        (3, 3, 3),
    )
    if point_types != expected_types:
        raise AssertionError(f"wrong local point types: {point_types}")
    singleton_crossings = {
        right: crossing_edge_counts(1, right)
        for right in range(1, 5)
    }
    if singleton_crossings != {right: frozenset((0,)) for right in range(1, 5)}:
        raise AssertionError("a singleton-side crossing survived")

    bounds = tuple(expansion_bound(size) for size in range(2, ACTIVE_ORDER + 1))
    if tuple(size for size, bound in zip(range(2, ACTIVE_ORDER + 1), bounds, strict=True) if bound[2]) != (2, 3, 4):
        raise AssertionError("the expansion bound changed")

    resource_profiles = point_resource_profiles()
    if len(resource_profiles) != 20 or not all(profile[1] % 2 for profile in resource_profiles):
        raise AssertionError("point resource profiles changed")

    size4 = size_four_flower_statistics()
    expected_size4 = {
        "total_profiles": 6_561,
        "capacity_rejections": 6_552,
        "feasible_profiles": 9,
        "minimum_type_224_occurrences": 3,
        "crossing_extensions": 33,
        "minimum_root_degree_lower": 7,
        "type_224_histogram": {3: 8, 4: 1},
    }
    if size4 != expected_size4:
        raise AssertionError(f"size-four flower census changed: {size4}")

    if tuple(u_degree(value) for value in range(4)) != (3, 2, 1, 0):
        raise AssertionError("F/U degree table changed")
    size3 = size_three_flower_statistics()
    expected_size3 = {
        "total_profiles": 64,
        "profiles_with_type_233": 56,
        "all_333_profiles": 1,
        "profiles_with_223_no_233": 7,
        "type_233_capacity_feasible_profiles": 50,
        "type_233_over_capacity_profiles": 6,
        "all_333_over_capacity_profiles": 1,
        "homogeneous_223_over_capacity_profiles": 0,
        "profiles_by_type_223_count": {1: 3, 2: 3, 3: 1},
        "type_233_raw_crossing_extensions": 1_468,
        "type_233_capacity_feasible_crossing_extensions": 700,
        "type_233_over_capacity_crossing_extensions": 768,
        "all_333_raw_crossing_extensions": 512,
        "root_223_333_crossing_extensions": 217,
        "all_raw_crossing_extensions": 2_197,
    }
    if size3 != expected_size3:
        raise AssertionError(f"size-three flower census changed: {size3}")

    if (ACTIVE_ORDER * 3) % 2 != 1:
        raise AssertionError("the all-size-two parity contradiction disappeared")

    branch_bounds = tuple(
        max(42, ceil_multiple_of_three(4 * degree))
        for degree in WAVE6_BRANCH_DEGREES
    )
    expected_branch_bounds = (42, 42, 42, 48, 48, 42, 42, 48, 42, 48, 42, 48)
    if branch_bounds != expected_branch_bounds:
        raise AssertionError(f"wrong Wave 11 branch bounds: {branch_bounds}")

    print("PASS n3=39 equality exclusion arithmetic")
    print("active_q_n3_39", [list(profile) for profile in q39])
    print("K_degree_histograms", [dict(sorted(item.items())) for item in expected_histograms])
    print("mixed_forced_singletons", list(mixed_forced_singletons))
    print("local_point_types", [list(profile) for profile in point_types])
    print("point_resource_profiles", len(resource_profiles))
    print("size4_flower_statistics", size4)
    print("size3_flower_statistics", size3)
    print("global_n3_lower_bound", 42)
    print("global_induced_C6_lower_bound", 209_286 + 42)
    print("branch_n3_bounds", list(branch_bounds))
    print("target_result", "UNKNOWN")


def main(argv: Sequence[str] | None = None) -> int:
    if argv:
        raise ValueError("this checker takes no arguments")
    verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
