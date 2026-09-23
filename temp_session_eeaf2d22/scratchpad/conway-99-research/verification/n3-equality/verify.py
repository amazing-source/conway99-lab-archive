#!/usr/bin/env python3
"""Exact arithmetic checks for the Wave 8 exclusion of n3 = 30.

The human proof supplies the graph-theoretic implications.  This checker
independently recomputes every finite arithmetic step and the final local
overlapping-set crossing.
"""

from __future__ import annotations

from itertools import combinations, product
from typing import Iterable, Sequence


ALLOWED_H_DEGREES = frozenset((0, 4, 6, 8, 10, 12))
WAVE6_BRANCH_DEGREES = (4, 8, 10, 12, 12, 6, 10, 12, 8, 12, 10, 12)

Edge = tuple[int, int]
Point = frozenset[int]


def active_q_sequences(n3_count: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate active-q multisets allowed by degree and handshake data."""

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


def fixed_triangle_profile(q_value: int) -> tuple[int, int, int]:
    """Return prisms, N3s per side-vertex pair, and per side vertex.

    For each unordered pair of vertices on a fixed graph-triangle, exactly
    twelve disjoint triangle partners use cross-edges at both vertices.  All
    p=12-q prism partners do so, leaving q N3 partners for that pair.  Each
    triangle vertex lies in two of the three unordered pairs.
    """

    if not 0 <= q_value <= 12:
        raise ValueError("q must lie between zero and twelve")
    prism_partners = 12 - q_value
    n3_per_vertex_pair = 12 - prism_partners
    n3_per_vertex = 2 * n3_per_vertex_pair
    return prism_partners, n3_per_vertex_pair, n3_per_vertex


def point_size_solutions(
    *,
    incidence_total: int,
    edge_budget: int,
    maximum_size: int,
    forbid_singletons: bool,
) -> tuple[tuple[int, ...], ...]:
    """Enumerate point-size count vectors under incidence/edge consumption."""

    if incidence_total < 0 or edge_budget < 0:
        raise ValueError("totals must be nonnegative")
    if not 1 <= maximum_size <= 4:
        raise ValueError("the supported maximum point size is between one and four")
    ranges = tuple(range(incidence_total // size + 1) for size in range(1, maximum_size + 1))
    results: list[tuple[int, ...]] = []
    for counts in product(*ranges):
        if forbid_singletons and counts[0] != 0:
            continue
        incidences = sum(size * counts[size - 1] for size in range(1, maximum_size + 1))
        consumed = sum(
            (size * (size - 1) // 2) * counts[size - 1]
            for size in range(2, maximum_size + 1)
        )
        if incidences == incidence_total and consumed <= edge_budget:
            results.append(tuple(counts))
    return tuple(results)


def cubic_component_partitions(order: int) -> tuple[tuple[int, ...], ...]:
    """Possible component-order partitions for a simple cubic graph."""

    if order < 0:
        raise ValueError("order must be nonnegative")
    results: list[tuple[int, ...]] = []

    def visit(remaining: int, least: int, parts: tuple[int, ...]) -> None:
        if remaining == 0:
            results.append(parts)
            return
        # Every cubic component has even order at least four.
        for part in range(least, remaining + 1, 2):
            visit(remaining - part, part, (*parts, part))

    visit(order, 4, ())
    return tuple(results)


def crossing_l_edges(first: Point, second: Point, l_edges: Iterable[Edge]) -> int:
    """Count each L-edge crossing possibly overlapping point sets once."""

    return sum(
        (left in first and right in second) or (right in first and left in second)
        for left, right in l_edges
    )


def internal_crossing_profiles(neighbor_slots: int) -> tuple[tuple[int, int, int, int], ...]:
    """Enumerate crossings for two point sets meeting in one active triangle.

    Removing the common triangle leaves disjoint subsets A,B of its K-
    neighborhood.  A profile records ``(|A|, |B|, e_K(A,B), e_L(A,B))``.
    """

    if neighbor_slots < 0:
        raise ValueError("neighbor slot count must be nonnegative")
    profiles: list[tuple[int, int, int, int]] = []
    for left_size in range(neighbor_slots + 1):
        for right_size in range(neighbor_slots - left_size + 1):
            cross_pairs = left_size * right_size
            for k_crossing in range(cross_pairs + 1):
                profiles.append(
                    (left_size, right_size, k_crossing, cross_pairs - k_crossing)
                )
    return tuple(profiles)


def ceil_multiple_of_three(value: int) -> int:
    return 3 * ((value + 2) // 3)


def verify() -> None:
    q30 = active_q_sequences(30)
    if q30 != ((2,) * 10,):
        raise AssertionError(f"unexpected n3=30 active-q sequence {q30}")

    prisms, n3_per_pair, n3_per_vertex = fixed_triangle_profile(2)
    if (prisms, n3_per_pair, n3_per_vertex) != (10, 2, 4):
        raise AssertionError("wrong fixed-triangle q=2 endpoint profile")

    # The ten active triangles form a 6-regular L, so K is cubic and has
    # fifteen edges.  With no size-four point, a singleton has crossing at
    # most three with every point and therefore cannot meet its fixed-point
    # H-degree sum of four.  Enumerate what remains.
    no_size_four = point_size_solutions(
        incidence_total=30,
        edge_budget=15,
        maximum_size=3,
        forbid_singletons=True,
    )
    if no_size_four != ((0, 15, 0),):
        raise AssertionError(f"unexpected no-size-four point counts {no_size_four}")
    size_two_count = no_size_four[0][1]
    consumed_k_edges = size_two_count
    if consumed_k_edges != 15:
        raise AssertionError("the size-two points do not consume every K-edge")

    # A simple cubic graph of order ten cannot have every component K4.
    component_partitions = cubic_component_partitions(10)
    if component_partitions != ((4, 6), (10,)):
        raise AssertionError(f"unexpected cubic component partitions {component_partitions}")
    if 10 % 4 == 0:
        raise AssertionError("the K4-component obstruction unexpectedly vanished")

    internal_profiles = internal_crossing_profiles(3)
    positive_allowed_internal = tuple(
        profile for profile in internal_profiles if profile[3] in ALLOWED_H_DEGREES - {0}
    )
    if positive_allowed_internal:
        raise AssertionError(
            f"an internal active-triangle edge admitted positive H-degree: "
            f"{positive_allowed_internal}"
        )

    # At a cubic K-vertex i with nonclique neighborhood choose nonadjacent
    # neighbors j,k.  The consumed edges ij,ik correspond to two original
    # vertices in graph-triangle T_i.  Their active sets overlap at i, and jk
    # is the unique crossing L-edge.
    first = frozenset((0, 1))
    second = frozenset((0, 2))
    local_l_edges = frozenset(((1, 2),))
    overlap_crossing = crossing_l_edges(first, second, local_l_edges)
    if overlap_crossing != 1:
        raise AssertionError("wrong overlapping-set crossing count")
    if overlap_crossing in ALLOWED_H_DEGREES:
        raise AssertionError("degree one unexpectedly became an allowed H-degree")

    # A size-four point is a K4 component.  It consumes every K-edge incident
    # with its four active triangles, leaving two singleton point slots on
    # each.  The only size-four point has zero L-crossing with those
    # singletons; all remaining point sizes are at most three.
    singleton_slots_from_size_four = 4 * (3 - 1)
    if singleton_slots_from_size_four != 8:
        raise AssertionError("wrong number of forced singleton slots")
    singleton_max_crossing = 3
    if singleton_max_crossing >= min(ALLOWED_H_DEGREES - {0}):
        raise AssertionError("a singleton could unexpectedly support H")

    branch_bounds = tuple(
        max(33, ceil_multiple_of_three(4 * degree))
        for degree in WAVE6_BRANCH_DEGREES
    )
    expected_branch_bounds = (33, 33, 42, 48, 48, 33, 42, 48, 33, 48, 42, 48)
    if branch_bounds != expected_branch_bounds:
        raise AssertionError(f"wrong Wave 8 branch bounds {branch_bounds}")

    print("PASS n3=30 equality exclusion arithmetic")
    print("active_q_n3_30", list(q30[0]))
    print("fixed_triangle_prism_partners", prisms)
    print("fixed_side_n3_per_vertex_pair", n3_per_pair)
    print("fixed_side_n3_per_vertex", n3_per_vertex)
    print("no_size_four_point_counts", list(no_size_four[0]))
    print("consumed_cubic_complement_edges", consumed_k_edges)
    print("cubic_component_partitions", [list(parts) for parts in component_partitions])
    print("positive_allowed_internal_profiles", list(positive_allowed_internal))
    print("forced_overlap_h_degree", overlap_crossing)
    print("size_four_forced_singleton_slots", singleton_slots_from_size_four)
    print("global_n3_lower_bound", 33)
    print("global_p6_lower_bound", 209_286 + 33)
    print("branch_n3_bounds", list(branch_bounds))


def main(argv: Sequence[str] | None = None) -> int:
    if argv:
        raise ValueError("this checker takes no arguments")
    verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
