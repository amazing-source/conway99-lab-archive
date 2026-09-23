#!/usr/bin/env python3
"""Exact finite checks for the Wave 9 exclusion of n3 = 33.

The human proof supplies the graph-theoretic implications.  This checker
independently recomputes the active-triangle arithmetic, the finite local
crossing obstructions, the point-size alternatives, the forced K5 closure,
the residual K6-minus-matching obstruction, and the strengthened bounds.
"""

from __future__ import annotations

from itertools import combinations, product
from typing import Iterable, Sequence


ALLOWED_H_DEGREES = frozenset((0, 4, 6, 8, 10, 12))
WAVE6_BRANCH_DEGREES = (4, 8, 10, 12, 12, 6, 10, 12, 8, 12, 10, 12)

Edge = tuple[int, int]


def normalized_edge(left: int, right: int) -> Edge:
    if left == right:
        raise ValueError("loops are not edges")
    return (left, right) if left < right else (right, left)


def active_q_sequences(n3_count: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate active-q multisets allowed by handshake and degree data."""

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
    """Return prism partners, N3s per side pair, and N3s per side point."""

    if not 0 <= q_value <= 12:
        raise ValueError("q must lie between zero and twelve")
    prism_partners = 12 - q_value
    n3_per_side_pair = q_value
    n3_per_side_point = 2 * q_value
    return prism_partners, n3_per_side_pair, n3_per_side_point


def bounded_h_degree_sums(term_count: int, crossing_cap: int) -> frozenset[int]:
    """All sums of allowed H-degrees bounded by a local crossing cap."""

    if term_count < 0 or crossing_cap < 0:
        raise ValueError("term count and crossing cap must be nonnegative")
    choices = ALLOWED_H_DEGREES & frozenset(range(crossing_cap + 1))
    totals = {0}
    for _ in range(term_count):
        totals = {partial + value for partial in totals for value in choices}
    return frozenset(totals)


def singleton_biregular_crossing_counts(maximum_other_size: int) -> frozenset[int]:
    """Enumerate simple crossing graphs with one left vertex and degrees 0/2.

    Wave 7 gives local degree zero or two on both labeled sides.  A shared
    graph-triangle is isolated and can be omitted, so the remaining crossing
    graph is simple and bipartite.  The enumeration checks every possible
    right-side size through ``maximum_other_size``.
    """

    if maximum_other_size < 0:
        raise ValueError("maximum other size must be nonnegative")
    edge_counts: set[int] = set()
    for right_order in range(maximum_other_size + 1):
        for mask in range(1 << right_order):
            left_degree = mask.bit_count()
            right_degrees = tuple((mask >> index) & 1 for index in range(right_order))
            if left_degree in (0, 2) and all(degree in (0, 2) for degree in right_degrees):
                edge_counts.add(left_degree)
    return frozenset(edge_counts)


def point_size_solutions(
    *, incidence_total: int, edge_budget: int
) -> tuple[tuple[int, int], ...]:
    """Enumerate ``(x2,x3)`` after singletons and sizes above three vanish."""

    if incidence_total < 0 or edge_budget < 0:
        raise ValueError("totals must be nonnegative")
    results: list[tuple[int, int]] = []
    for size_two in range(incidence_total // 2 + 1):
        for size_three in range(incidence_total // 3 + 1):
            if 2 * size_two + 3 * size_three != incidence_total:
                continue
            if size_two + 3 * size_three <= edge_budget:
                results.append((size_two, size_three))
    return tuple(results)


def size_three_local_closures() -> tuple[frozenset[Edge], ...]:
    """Enumerate local K-closures compatible with allowed internal H-degrees.

    Vertices 0,1,2 form a size-three point, while ``{0,3}`` and ``{0,4}``
    are the other two point sets on active triangle 0.  The mandatory K-edges
    are the four edges at 0 and edge 1-2.  Five remaining pairs determine the
    three crossings of the actual graph edges inside that triangle.
    """

    mandatory = frozenset(
        normalized_edge(*edge)
        for edge in ((0, 1), (0, 2), (0, 3), (0, 4), (1, 2))
    )
    optional = tuple(
        normalized_edge(*edge)
        for edge in ((1, 3), (2, 3), (1, 4), (2, 4), (3, 4))
    )
    closures: list[frozenset[Edge]] = []
    for bits in product((False, True), repeat=len(optional)):
        k_edges = mandatory | frozenset(
            edge for edge, present in zip(optional, bits, strict=True) if present
        )
        crossing_degrees = (
            sum(normalized_edge(vertex, 3) not in k_edges for vertex in (1, 2)),
            sum(normalized_edge(vertex, 4) not in k_edges for vertex in (1, 2)),
            int(normalized_edge(3, 4) not in k_edges),
        )
        if all(degree in ALLOWED_H_DEGREES for degree in crossing_degrees):
            closures.append(k_edges)
    return tuple(closures)


def perfect_matchings(vertices: Iterable[int]) -> tuple[frozenset[Edge], ...]:
    """Enumerate every perfect matching on an even finite vertex set."""

    remaining = tuple(sorted(vertices))
    if len(set(remaining)) != len(remaining):
        raise ValueError("vertices must be distinct")
    if len(remaining) % 2:
        raise ValueError("a perfect matching needs even order")

    def visit(todo: tuple[int, ...]) -> tuple[frozenset[Edge], ...]:
        if not todo:
            return (frozenset(),)
        first = todo[0]
        results: list[frozenset[Edge]] = []
        for index in range(1, len(todo)):
            second = todo[index]
            rest = todo[1:index] + todo[index + 1 :]
            for matching in visit(rest):
                results.append(matching | {normalized_edge(first, second)})
        return tuple(results)

    return visit(remaining)


def is_clique(vertices: Iterable[int], edges: frozenset[Edge]) -> bool:
    chosen = tuple(vertices)
    return all(normalized_edge(left, right) in edges for left, right in combinations(chosen, 2))


def residual_local_choices() -> tuple[int, int]:
    """Count all local choices in every labeled K6-minus-matching residual."""

    vertices = tuple(range(6))
    complete_edges = frozenset(
        normalized_edge(left, right) for left, right in combinations(vertices, 2)
    )
    total = 0
    valid = 0
    for missing_matching in perfect_matchings(vertices):
        residual_edges = complete_edges - missing_matching
        for vertex in vertices:
            neighbors = tuple(
                other
                for other in vertices
                if other != vertex and normalized_edge(vertex, other) in residual_edges
            )
            if len(neighbors) != 4:
                raise AssertionError("K6 minus a perfect matching is not 4-regular")
            for unused_neighbor in neighbors:
                total += 1
                consumed_neighbors = tuple(
                    neighbor for neighbor in neighbors if neighbor != unused_neighbor
                )
                if is_clique(consumed_neighbors, residual_edges):
                    valid += 1
    return total, valid


def ceil_multiple_of_three(value: int) -> int:
    return 3 * ((value + 2) // 3)


def verify() -> None:
    q33 = active_q_sequences(33)
    expected_q33 = ((2,) * 11, (2,) * 8 + (3, 3))
    if q33 != expected_q33:
        raise AssertionError(f"unexpected n3=33 active-q sequences {q33}")

    if fixed_triangle_profile(2) != (10, 2, 4):
        raise AssertionError("wrong q=2 fixed-side endpoint profile")
    if fixed_triangle_profile(3) != (9, 3, 6):
        raise AssertionError("wrong q=3 fixed-side endpoint profile")

    # In the mixed r=10 case, each q=3 active triangle is isolated in K.
    # Every one of its original points is therefore a singleton.  The other
    # eight K-vertices are cubic, so any crossing has size at most four.
    mixed_singleton_sums = bounded_h_degree_sums(term_count=14, crossing_cap=4)
    if 6 in mixed_singleton_sums:
        raise AssertionError("the mixed q profile unexpectedly met fixed sum six")

    # In the all-q=2 r=11 case, K is 4-regular, hence point cliques have size
    # at most five.  The local H_T degree-0/2 property on both labeled sides
    # makes a singleton crossing graph empty.
    singleton_crossings = singleton_biregular_crossing_counts(5)
    if singleton_crossings != frozenset((0,)):
        raise AssertionError(f"nonempty singleton crossing survived: {singleton_crossings}")

    point_solutions = point_size_solutions(incidence_total=33, edge_budget=22)
    if point_solutions != ((12, 3), (15, 1)):
        raise AssertionError(f"unexpected point-size solutions {point_solutions}")

    closures = size_three_local_closures()
    complete_k5 = frozenset(
        normalized_edge(left, right) for left, right in combinations(range(5), 2)
    )
    if closures != (complete_k5,):
        raise AssertionError(f"a size-three point did not force exactly K5: {closures}")

    # Three vertex-disjoint size-three points would force three distinct K5
    # components.  The one-size-three alternative leaves six vertices.
    if 3 * 5 <= 11:
        raise AssertionError("three K5 components unexpectedly fit on eleven vertices")
    residual_order = 11 - 5
    residual_degree = 4
    if residual_order - 1 - residual_degree != 1:
        raise AssertionError("the residual complement is not a perfect matching")

    matchings = perfect_matchings(range(residual_order))
    if len(matchings) != 15:
        raise AssertionError(f"wrong number of K6 perfect matchings: {len(matchings)}")
    residual_choices, valid_residual_choices = residual_local_choices()
    if residual_choices != 360 or valid_residual_choices != 0:
        raise AssertionError(
            "a residual K6-minus-matching local clique choice survived: "
            f"{valid_residual_choices}/{residual_choices}"
        )

    branch_bounds = tuple(
        max(36, ceil_multiple_of_three(4 * degree))
        for degree in WAVE6_BRANCH_DEGREES
    )
    expected_branch_bounds = (36, 36, 42, 48, 48, 36, 42, 48, 36, 48, 42, 48)
    if branch_bounds != expected_branch_bounds:
        raise AssertionError(f"wrong Wave 9 branch bounds {branch_bounds}")

    print("PASS n3=33 equality exclusion arithmetic")
    print("active_q_n3_33", [list(sequence) for sequence in q33])
    print("mixed_profile_possible_singleton_sums", sorted(mixed_singleton_sums))
    print("all_q2_singleton_crossing_counts", sorted(singleton_crossings))
    print("point_size_solutions_x2_x3", [list(solution) for solution in point_solutions])
    print("size_three_local_closures", len(closures))
    print("residual_perfect_matchings", len(matchings))
    print("residual_local_choices", residual_choices)
    print("valid_residual_local_choices", valid_residual_choices)
    print("global_n3_lower_bound", 36)
    print("global_p6_lower_bound", 209_286 + 36)
    print("branch_n3_bounds", list(branch_bounds))


def main(argv: Sequence[str] | None = None) -> int:
    if argv:
        raise ValueError("this checker takes no arguments")
    verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
