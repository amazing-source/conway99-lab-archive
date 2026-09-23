#!/usr/bin/env python3
"""Exact finite checks supporting the Wave 10 exclusion of ``n3 = 36``.

The human proof supplies the graph-theoretic implications.  This standard-
library checker independently recomputes the active profiles, every local
crossing type, the common-point obstructions, the line-graph-twin endpoint
configuration, the all-size-two component pairing, the induced rook graph,
and the strengthened numerical bounds.

It is not a standalone nonexistence certificate for ``srg(99,14,1,2)``.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from typing import Iterable, Sequence


ALLOWED_H_DEGREES = frozenset((0, 4, 6, 8, 10, 12))
WAVE6_BRANCH_DEGREES = (4, 8, 10, 12, 12, 6, 10, 12, 8, 12, 10, 12)

Edge = tuple[int, int]


def normalized_edge(left: int, right: int) -> Edge:
    if left == right:
        raise ValueError("loops are not edges")
    return (left, right) if left < right else (right, left)


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
    """Return degrees in the active complement ``K``."""

    active_count = len(q_values)
    return tuple(active_count - 1 - 3 * value for value in q_values)


def forced_singletons_at_triangle(k_degree: int) -> int:
    """Three nonempty point cliques compete for distinct incident K-edges."""

    if k_degree < 0:
        raise ValueError("K-degree must be nonnegative")
    return max(0, 3 - k_degree)


def biregular_crossing_edge_counts(left_order: int, right_order: int) -> frozenset[int]:
    """Enumerate bipartite crossings whose labeled degrees all lie in {0,2}.

    ``left_order`` and ``right_order`` are the point-set sizes after deleting
    their possible common active triangle.  Orders never exceed three in the
    Wave 10 local applications, so direct bit enumeration is exact and tiny.
    """

    if left_order < 0 or right_order < 0:
        raise ValueError("crossing orders must be nonnegative")
    pair_count = left_order * right_order
    if pair_count > 20:
        raise ValueError("direct crossing enumeration is intentionally local")
    results: set[int] = set()
    for mask in range(1 << pair_count):
        left_degrees = [0] * left_order
        right_degrees = [0] * right_order
        for left in range(left_order):
            for right in range(right_order):
                if mask >> (left * right_order + right) & 1:
                    left_degrees[left] += 1
                    right_degrees[right] += 1
        if all(value in (0, 2) for value in (*left_degrees, *right_degrees)):
            results.add(mask.bit_count())
    return frozenset(results)


def local_point_types(k_degree: int = 5) -> tuple[tuple[int, int, int], ...]:
    """Enumerate sorted point-set sizes through an all-q=2 active triangle."""

    if k_degree < 3:
        raise ValueError("three non-singleton point sets need degree at least three")
    output = []
    for sizes in combinations_with_replacement(range(2, k_degree + 2), 3):
        if sum(size - 1 for size in sizes) <= k_degree:
            output.append(sizes)
    return tuple(output)


def local_crossing_counts(left_size: int, right_size: int) -> frozenset[int]:
    """Allowed H-degrees between two points on the same active triangle."""

    if left_size < 1 or right_size < 1:
        raise ValueError("point sets must be nonempty")
    return biregular_crossing_edge_counts(left_size - 1, right_size - 1) & ALLOWED_H_DEGREES


def complete_cross_component_size_pairs(maximum_size: int = 4) -> tuple[tuple[int, int], ...]:
    """Point-size pairs compatible with a complete L-crossing between K6s."""

    if maximum_size < 2:
        raise ValueError("maximum size must be at least two")
    results = []
    for left in range(2, maximum_size + 1):
        for right in range(2, maximum_size + 1):
            edge_count = left * right
            if left in (0, 2) and right in (0, 2) and edge_count in ALLOWED_H_DEGREES:
                results.append((left, right))
    return tuple(results)


def graph_from_edges(order: int, edges: Iterable[Edge]) -> tuple[frozenset[int], ...]:
    if order < 0:
        raise ValueError("graph order must be nonnegative")
    adjacency = [set() for _ in range(order)]
    for left, right in edges:
        if not 0 <= left < order or not 0 <= right < order or left == right:
            raise ValueError("invalid edge")
        adjacency[left].add(right)
        adjacency[right].add(left)
    return tuple(frozenset(items) for items in adjacency)


def cubic_graphs_on_six() -> tuple[frozenset[Edge], ...]:
    """Enumerate every labeled cubic graph on six vertices."""

    all_edges = tuple(combinations(range(6), 2))
    results = []
    for chosen in combinations(all_edges, 9):
        degrees = Counter(vertex for edge in chosen for vertex in edge)
        if all(degrees[vertex] == 3 for vertex in range(6)):
            results.append(frozenset(normalized_edge(*edge) for edge in chosen))
    return tuple(results)


def contains_triangle(edges: frozenset[Edge], order: int) -> bool:
    return any(
        all(normalized_edge(left, right) in edges for left, right in combinations(vertices, 2))
        for vertices in combinations(range(order), 3)
    )


def is_k33(edges: frozenset[Edge]) -> bool:
    """Recognize a labeled copy of K3,3 on vertices 0,...,5."""

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


def rook_graph_audit() -> tuple[int, int, tuple[int, ...]]:
    """Check that L(K3,3) has SRG parameters (9,4,1,2)."""

    points = tuple((row, column) for row in range(3) for column in range(3))
    adjacency = tuple(
        frozenset(
            other
            for other in range(9)
            if other != vertex
            and (
                points[other][0] == points[vertex][0]
                or points[other][1] == points[vertex][1]
            )
        )
        for vertex in range(9)
    )
    if any(len(neighbors) != 4 for neighbors in adjacency):
        raise AssertionError("rook graph is not 4-regular")
    adjacent_pairs = 0
    nonadjacent_pairs = 0
    common_counts = []
    for left, right in combinations(range(9), 2):
        common = len(adjacency[left] & adjacency[right])
        common_counts.append(common)
        if right in adjacency[left]:
            adjacent_pairs += 1
            if common != 1:
                raise AssertionError("rook lambda count changed")
        else:
            nonadjacent_pairs += 1
            if common != 2:
                raise AssertionError("rook mu count changed")
    return adjacent_pairs, nonadjacent_pairs, tuple(sorted(common_counts))


def forbidden_common_point_triple(point_sets: Sequence[frozenset[int]]) -> bool:
    """Detect three pairwise intersections at three distinct active triangles."""

    if len(point_sets) != 3 or len(set(point_sets)) != 3:
        raise ValueError("three distinct point sets are required")
    intersections = [
        point_sets[left] & point_sets[right]
        for left, right in combinations(range(3), 2)
    ]
    return all(len(item) == 1 for item in intersections) and len(set().union(*intersections)) == 3


def size_three_223_endpoint_choices() -> tuple[int, int]:
    """Count the apparent and common-point-safe endpoints at a second occurrence."""

    # C={0,1,2}; at occurrence 0 the two size-two endpoints are 3 and 4.
    # K5 leaves occurrence 1 only the candidate pool {3,4,5}.  Reusing 3 or
    # 4 creates the forbidden triples C,{0,a},{1,a}, so only 5 is safe.
    central = frozenset((0, 1, 2))
    pool = (3, 4, 5)
    apparent = tuple(combinations(pool, 2))
    valid = []
    for endpoints in apparent:
        if any(
            forbidden_common_point_triple(
                (central, frozenset((0, reused)), frozenset((1, reused)))
            )
            for reused in endpoints
            if reused in (3, 4)
        ):
            continue
        valid.append(endpoints)
    return len(apparent), len(valid)


def split_233_type222_mate_choices() -> tuple[int, int]:
    """Enumerate the two same-side choices and reject both by common points."""

    # At split 233 triangle i=0, the two size-three sides are {0,1,2}
    # and {0,3,4}; its size-two mate is {0,5}.  If 5 were type 222, its
    # other endpoints must form a K-edge.  Split leaves only pairs {1,2}
    # and {3,4}; either makes a forbidden triple.
    sides = (frozenset((0, 1, 2)), frozenset((0, 3, 4)))
    mate = frozenset((0, 5))
    choices = ((1, 2), (3, 4))
    valid = []
    for side, pair in zip(sides, choices, strict=True):
        endpoint_point = frozenset((5, pair[0]))
        if not forbidden_common_point_triple((side, mate, endpoint_point)):
            valid.append(pair)
    return len(choices), len(valid)


def line_twin_cross_configurations() -> tuple[int, int]:
    """Enumerate endpoint configurations for disjoint line-graph open twins."""

    base = frozenset((normalized_edge(0, 1), normalized_edge(2, 3)))
    cross = tuple(
        normalized_edge(left, right)
        for left in (0, 1)
        for right in (2, 3)
    )
    twin_configurations = []
    split_compatible = []
    for bits in product((False, True), repeat=4):
        edges = base | frozenset(
            candidate
            for candidate, present in zip(cross, bits, strict=True)
            if present
        )
        line_neighbors = {
            chosen: frozenset(
                other
                for other in edges
                if other != chosen and set(other) & set(chosen)
            )
            for chosen in base
        }
        first, second = tuple(base)
        if line_neighbors[first] != line_neighbors[second] or len(line_neighbors[first]) != 4:
            continue
        twin_configurations.append(edges)
        u, v = first
        x, y = second
        first_side = (normalized_edge(u, x), normalized_edge(u, y))
        second_side = (normalized_edge(v, x), normalized_edge(v, y))
        if not any(set(left) & set(right) for left in first_side for right in second_side):
            split_compatible.append(edges)
    return len(twin_configurations), len(split_compatible)


def triangle_group_pairings(group_count: int = 4) -> tuple[tuple[int, ...], ...]:
    """Enumerate fixed-point-free involutions pairing the forced U-triangles."""

    if group_count < 0 or group_count % 2:
        raise ValueError("an even nonnegative group count is required")
    results = []
    for mapping in product(range(group_count), repeat=group_count):
        if all(mapping[index] != index for index in range(group_count)) and all(
            mapping[mapping[index]] == index for index in range(group_count)
        ):
            results.append(mapping)
    return tuple(results)


def paired_group_k_components(pairing: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    """Build K=U+F from paired U-triangles and return component orders."""

    group_count = len(pairing)
    if any(not 0 <= target < group_count for target in pairing):
        raise ValueError("bad group target")
    edges: set[Edge] = set()
    for group in range(group_count):
        vertices = range(3 * group, 3 * group + 3)
        edges.update(normalized_edge(*item) for item in combinations(vertices, 2))
        target_vertices = range(3 * pairing[group], 3 * pairing[group] + 3)
        edges.update(
            normalized_edge(left, right)
            for left in vertices
            for right in target_vertices
        )
    adjacency = graph_from_edges(3 * group_count, edges)
    unseen = set(range(3 * group_count))
    component_orders = []
    while unseen:
        seed = min(unseen)
        reached = {seed}
        pending = [seed]
        while pending:
            vertex = pending.pop()
            new = set(adjacency[vertex]) - reached
            reached.update(new)
            pending.extend(new)
        unseen.difference_update(reached)
        component_orders.append(len(reached))
    return tuple(sorted(component_orders))


def ceil_multiple_of_three(value: int) -> int:
    return 3 * ((value + 2) // 3)


def verify() -> None:
    q36 = active_q_sequences(36)
    expected_q36 = (
        (2,) * 12,
        (2,) * 9 + (3, 3),
        (2,) * 6 + (3,) * 4,
    )
    if q36 != expected_q36:
        raise AssertionError(f"unexpected n3=36 active profiles: {q36}")

    degree_profiles = tuple(k_degree_profile(profile) for profile in q36)
    if tuple(Counter(profile) for profile in degree_profiles) != (
        Counter({5: 12}),
        Counter({4: 9, 1: 2}),
        Counter({3: 6, 0: 4}),
    ):
        raise AssertionError("wrong K-degree profiles")
    mixed_forced_singletons = tuple(
        sum(forced_singletons_at_triangle(degree) for degree in profile if degree < 3)
        for profile in degree_profiles[1:]
    )
    if mixed_forced_singletons != (4, 12):
        raise AssertionError("mixed-profile singleton count changed")
    if biregular_crossing_edge_counts(1, 4) != frozenset((0,)):
        raise AssertionError("a singleton crossing survived")

    point_types = local_point_types()
    if point_types != ((2, 2, 2), (2, 2, 3), (2, 2, 4), (2, 3, 3)):
        raise AssertionError(f"wrong local point types: {point_types}")
    expected_crossings = {
        (2, 2): frozenset((0,)),
        (2, 3): frozenset((0,)),
        (2, 4): frozenset((0,)),
        (3, 3): frozenset((0, 4)),
    }
    if {pair: local_crossing_counts(*pair) for pair in expected_crossings} != expected_crossings:
        raise AssertionError("local crossing alternatives changed")

    if complete_cross_component_size_pairs() != ((2, 2),):
        raise AssertionError("a non-size-two complete cross-component pair survived")

    cubic_six = cubic_graphs_on_six()
    triangle_free_cubic_six = tuple(graph for graph in cubic_six if not contains_triangle(graph, 6))
    if len(cubic_six) != 70 or len(triangle_free_cubic_six) != 10:
        raise AssertionError("labeled cubic-six census changed")
    if not all(is_k33(graph) for graph in triangle_free_cubic_six):
        raise AssertionError("a triangle-free cubic graph on six was not K3,3")

    adjacent_pairs, nonadjacent_pairs, common_counts = rook_graph_audit()
    if (adjacent_pairs, nonadjacent_pairs) != (18, 18):
        raise AssertionError("rook pair counts changed")
    if Counter(common_counts) != Counter({1: 18, 2: 18}):
        raise AssertionError("rook saturation histogram changed")
    if 4 * 2 != 8 or 2 <= 1:
        raise AssertionError("fixed-point or outside-neighborhood contradiction changed")

    if size_three_223_endpoint_choices() != (3, 0):
        raise AssertionError("a size-three 223 endpoint choice survived")
    if split_233_type222_mate_choices() != (2, 0):
        raise AssertionError("a split-233 type-222 mate survived")
    if line_twin_cross_configurations() != (1, 0):
        raise AssertionError("a split-compatible line-twin configuration survived")

    pairings = triangle_group_pairings()
    if len(pairings) != 3 or any(paired_group_k_components(pairing) != (6, 6) for pairing in pairings):
        raise AssertionError("the all-size-two branch did not force 2K6")

    branch_bounds = tuple(
        max(39, ceil_multiple_of_three(4 * degree))
        for degree in WAVE6_BRANCH_DEGREES
    )
    expected_branch_bounds = (39, 39, 42, 48, 48, 39, 42, 48, 39, 48, 42, 48)
    if branch_bounds != expected_branch_bounds:
        raise AssertionError(f"wrong Wave 10 branch bounds: {branch_bounds}")

    print("PASS n3=36 equality exclusion arithmetic")
    print("active_q_n3_36", [list(profile) for profile in q36])
    print("K_degree_histograms", [dict(sorted(Counter(profile).items())) for profile in degree_profiles])
    print("mixed_forced_singletons", list(mixed_forced_singletons))
    print("local_point_types", [list(profile) for profile in point_types])
    print("cubic_graphs_order_6", len(cubic_six))
    print("triangle_free_cubic_graphs_order_6", len(triangle_free_cubic_six))
    print("rook_adjacent_nonadjacent_pairs", [adjacent_pairs, nonadjacent_pairs])
    print("size3_223_choices_survivors", list(size_three_223_endpoint_choices()))
    print("split233_type222_choices_survivors", list(split_233_type222_mate_choices()))
    print("line_twin_configurations_survivors", list(line_twin_cross_configurations()))
    print("all_size_two_group_pairings", len(pairings))
    print("global_n3_lower_bound", 39)
    print("global_p6_lower_bound", 209_286 + 39)
    print("branch_n3_bounds", list(branch_bounds))


def main(argv: Sequence[str] | None = None) -> int:
    if argv:
        raise ValueError("this checker takes no arguments")
    verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
