#!/usr/bin/env python3
"""Exact finite checks for the Wave 7 triangle-side incidence argument."""

from __future__ import annotations

from itertools import combinations, combinations_with_replacement, product
from typing import Iterator, NamedTuple, Sequence


NONZERO_H_DEGREES = frozenset((4, 6, 8, 10, 12))
WAVE6_BRANCH_DEGREES = (4, 8, 10, 12, 12, 6, 10, 12, 8, 12, 10, 12)

Edge = tuple[int, int]
Point = frozenset[int]


class PointPattern(NamedTuple):
    """Non-singleton active-triangle sets belonging to graph vertices."""

    points: tuple[Point, ...]
    triple_points: int


def partner_counts(q_value: int) -> tuple[int, int, int, int]:
    """Solve the three fixed-triangle cross-edge count equations."""

    if not 0 <= q_value <= 12:
        raise ValueError("q must lie between zero and twelve")
    prism_partners = 12 - q_value
    count_two = 36 - 3 * prism_partners
    count_one = 216 - 2 * count_two - 3 * prism_partners
    count_zero = 212 - count_one - count_two - prism_partners
    counts = (count_zero, count_one, count_two, prism_partners)
    if any(value < 0 for value in counts):
        raise AssertionError("the cross-edge count equations gave a negative count")
    return counts


def active_q_sequences(n3_count: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate active q-multisets allowed by degree and handshake data."""

    if n3_count < 0 or (2 * n3_count) % 3:
        raise ValueError("2*n3 must be a nonnegative multiple of three")
    q_sum = 2 * n3_count // 3
    results: list[tuple[int, ...]] = []
    for active_count in range(1, q_sum // 2 + 1):
        for values in combinations_with_replacement(range(2, 13), active_count):
            if sum(values) != q_sum:
                continue
            if all(3 * value <= active_count - 1 for value in values):
                results.append(values)
    return tuple(results)


def cycle_partitions(total: int, minimum: int = 3) -> tuple[tuple[int, ...], ...]:
    """Integer partitions describing simple 2-regular graphs."""

    def visit(remaining: int, least: int) -> Iterator[tuple[int, ...]]:
        if remaining == 0:
            yield ()
            return
        for part in range(least, remaining + 1):
            for tail in visit(remaining - part, part):
                yield (part, *tail)

    return tuple(visit(total, minimum))


def cycle_edges(offset: int, length: int) -> tuple[Edge, ...]:
    return tuple(
        tuple(sorted((offset + index, offset + (index + 1) % length)))
        for index in range(length)
    )


def component_patterns(offset: int, length: int) -> tuple[PointPattern, ...]:
    """Enumerate an upper cover of intersection-point patterns on one cycle."""

    edges = cycle_edges(offset, length)
    patterns: list[PointPattern] = []
    if length == 3:
        # Three pairwise-intersecting graph triangles have one common graph
        # vertex.  Otherwise at most two of the three complement edges can be
        # realized as distinct pair-intersection points.
        patterns.append(
            PointPattern((frozenset(range(offset, offset + length)),), 1)
        )
        for count in range(3):
            for selected in combinations(edges, count):
                patterns.append(
                    PointPattern(tuple(frozenset(edge) for edge in selected), 0)
                )
    else:
        # A clique in a cycle of length at least four has size at most two.
        # Treat every subset of cycle edges as realizable; this can only make
        # the resulting support bound weaker and hence safe.
        for mask in range(1 << length):
            points = tuple(
                frozenset(edges[index])
                for index in range(length)
                if mask & (1 << index)
            )
            patterns.append(PointPattern(points, 0))
    return tuple(patterns)


def cycle_point_patterns(parts: tuple[int, ...]) -> Iterator[PointPattern]:
    offsets: list[int] = []
    offset = 0
    for length in parts:
        offsets.append(offset)
        offset += length
    component_options = tuple(
        component_patterns(start, length)
        for start, length in zip(offsets, parts)
    )
    for selected in product(*component_options):
        yield PointPattern(
            tuple(point for state in selected for point in state.points),
            sum(state.triple_points for state in selected),
        )


def complement_cycle_graph(parts: tuple[int, ...]) -> tuple[int, frozenset[Edge]]:
    complement_edges: set[Edge] = set()
    offset = 0
    for length in parts:
        complement_edges.update(cycle_edges(offset, length))
        offset += length
    complete_edges = set(combinations(range(offset), 2))
    return offset, frozenset(complete_edges - complement_edges)


def crossing_l_edges(left: Point, right: Point, l_edges: frozenset[Edge]) -> int:
    """Count each L-edge crossing two possibly overlapping sets exactly once."""

    return sum(
        (first in left and second in right)
        or (second in left and first in right)
        for first, second in l_edges
    )


def support_profile(
    pattern: PointPattern, l_edges: frozenset[Edge]
) -> tuple[int, tuple[int, ...]]:
    degrees: list[int] = []
    for left, right in combinations(pattern.points, 2):
        degree = crossing_l_edges(left, right, l_edges)
        if degree in NONZERO_H_DEGREES:
            degrees.append(degree)
    return len(degrees), tuple(sorted(degrees))


def matching_support_maximum(edge_count: int) -> tuple[int, frozenset[int]]:
    """Maximum support bound when the complement is a perfect matching."""

    vertex_count = 2 * edge_count
    matching = tuple((2 * index, 2 * index + 1) for index in range(edge_count))
    l_edges = frozenset(set(combinations(range(vertex_count), 2)) - set(matching))
    maximum = 0
    degrees: set[int] = set()
    for mask in range(1 << edge_count):
        pattern = PointPattern(
            tuple(
                frozenset(matching[index])
                for index in range(edge_count)
                if mask & (1 << index)
            ),
            0,
        )
        support, found_degrees = support_profile(pattern, l_edges)
        maximum = max(maximum, support)
        degrees.update(found_degrees)
    return maximum, frozenset(degrees)


def cycle_support_maximum(
    parts: tuple[int, ...], *, require_triple: bool
) -> tuple[int, frozenset[int], int]:
    """Exhaust all point patterns and return a safe support upper bound."""

    _, l_edges = complement_cycle_graph(parts)
    maximum = 0
    degrees: set[int] = set()
    tested = 0
    for pattern in cycle_point_patterns(parts):
        if require_triple and pattern.triple_points == 0:
            continue
        tested += 1
        support, found_degrees = support_profile(pattern, l_edges)
        maximum = max(maximum, support)
        degrees.update(found_degrees)
    return maximum, frozenset(degrees), tested


def minimum_mantel_support(edge_count: int) -> int:
    support = 0
    while support * support // 4 < edge_count:
        support += 1
    return support


def ceil_multiple_of_three(value: int) -> int:
    return 3 * ((value + 2) // 3)


def verify() -> None:
    expected_counts = tuple(
        (20 + q_value, 180 - 3 * q_value, 3 * q_value, 12 - q_value)
        for q_value in range(13)
    )
    actual_counts = tuple(partner_counts(q_value) for q_value in range(13))
    if actual_counts != expected_counts:
        raise AssertionError("wrong solution of the cross-edge count equations")
    for counts in actual_counts:
        if sum(counts) != 212:
            raise AssertionError("wrong number of disjoint triangle partners")
        if sum(index * value for index, value in enumerate(counts)) != 216:
            raise AssertionError("wrong cross-edge first moment")
        if counts[2] + 3 * counts[3] != 36:
            raise AssertionError("wrong cross-edge second binomial moment")

    q24 = active_q_sequences(24)
    q27 = active_q_sequences(27)
    if q24 != ((2,) * 8,) or q27 != ((2,) * 9,):
        raise AssertionError("unexpected active-q extremal sequence")

    matching_maximum, matching_degrees = matching_support_maximum(4)
    if matching_maximum != 6 or matching_degrees != {4}:
        raise AssertionError("wrong n3=24 matching support bound")
    required_support_24 = 2 * 24 // 4
    if not matching_maximum < required_support_24:
        raise AssertionError("the n3=24 support contradiction did not close")

    partitions = cycle_partitions(9)
    expected_partitions = ((3, 3, 3), (3, 6), (4, 5), (9,))
    if partitions != expected_partitions:
        raise AssertionError(f"unexpected 2-regular cycle types {partitions}")

    no_triangle_results = {
        parts: cycle_support_maximum(parts, require_triple=False)
        for parts in ((4, 5), (9,))
    }
    if any(degrees != {4} for _, degrees, _ in no_triangle_results.values()):
        raise AssertionError("a no-triangle complement admitted a non-four degree")
    if (2 * 27) % 4 == 0:
        raise AssertionError("the n3=27 four-regular handshake obstruction vanished")

    with_triangle_results = {
        parts: cycle_support_maximum(parts, require_triple=True)
        for parts in ((3, 6), (3, 3, 3))
    }
    expected_maxima = {(3, 6): 9, (3, 3, 3): 8}
    actual_maxima = {
        parts: result[0] for parts, result in with_triangle_results.items()
    }
    if actual_maxima != expected_maxima:
        raise AssertionError(f"wrong n3=27 support maxima {actual_maxima}")
    if any(result[1] != {4, 6} for result in with_triangle_results.values()):
        raise AssertionError("unexpected eligible degree in a triangle component case")

    mantel_support = minimum_mantel_support(27)
    if mantel_support != 11:
        raise AssertionError("wrong Mantel support threshold")
    if not all(maximum < mantel_support for maximum in actual_maxima.values()):
        raise AssertionError("an n3=27 support case survived Mantel")

    branch_bounds = tuple(
        max(30, ceil_multiple_of_three(4 * degree))
        for degree in WAVE6_BRANCH_DEGREES
    )
    expected_branch_bounds = (30, 33, 42, 48, 48, 30, 42, 48, 33, 48, 42, 48)
    if branch_bounds != expected_branch_bounds:
        raise AssertionError("wrong strengthened branch bounds")

    print("PASS N3 side-incidence exact checks")
    print("partner_counts_q0", list(actual_counts[0]))
    print("partner_counts_q12", list(actual_counts[12]))
    print("active_q_n3_24", list(q24[0]))
    print("active_q_n3_27", list(q27[0]))
    print("n3_24_support_maximum", matching_maximum)
    print("n3_24_support_required", required_support_24)
    print("n3_27_cycle_types", [list(parts) for parts in partitions])
    print("n3_27_c3_c6_support_maximum", actual_maxima[(3, 6)])
    print("n3_27_3c3_support_maximum", actual_maxima[(3, 3, 3)])
    print("n3_27_mantel_support_minimum", mantel_support)
    print("global_n3_lower_bound", 30)
    print("global_p6_lower_bound", 209_286 + 30)
    print("branch_n3_bounds", list(branch_bounds))


def main(argv: Sequence[str] | None = None) -> int:
    if argv:
        raise ValueError("this checker takes no arguments")
    verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
