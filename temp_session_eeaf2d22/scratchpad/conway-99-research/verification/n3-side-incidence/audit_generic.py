#!/usr/bin/env python3
"""Generic point-clique audit for the Wave 7 finite incidence cases."""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations


NONZERO_H_DEGREES = frozenset((4, 6, 8, 10, 12))

Edge = tuple[int, int]
Point = tuple[int, ...]


def cycle_edges(parts: tuple[int, ...]) -> tuple[int, tuple[Edge, ...]]:
    edges: set[Edge] = set()
    offset = 0
    for length in parts:
        if length < 3:
            raise ValueError("simple cycle components have length at least three")
        for index in range(length):
            edges.add(tuple(sorted((offset + index, offset + (index + 1) % length))))
        offset += length
    return offset, tuple(sorted(edges))


def matching_edges(vertex_count: int) -> tuple[int, tuple[Edge, ...]]:
    if vertex_count % 2:
        raise ValueError("a perfect matching needs an even vertex count")
    return vertex_count, tuple(
        (2 * index, 2 * index + 1) for index in range(vertex_count // 2)
    )


def nontrivial_cliques(vertex_count: int, k_edges: tuple[Edge, ...]) -> tuple[Point, ...]:
    k_edge_set = set(k_edges)
    cliques: list[Point] = []
    for size in range(2, vertex_count + 1):
        for vertices in combinations(range(vertex_count), size):
            if all(tuple(sorted(edge)) in k_edge_set for edge in combinations(vertices, 2)):
                cliques.append(vertices)
    return tuple(cliques)


def consumed_edges(point: Point) -> frozenset[Edge]:
    return frozenset(tuple(sorted(edge)) for edge in combinations(point, 2))


def point_families(
    vertex_count: int, k_edges: tuple[Edge, ...]
):
    """Enumerate all nontrivial point-clique families, then add singletons."""

    candidates = nontrivial_cliques(vertex_count, k_edges)
    consumptions = tuple(consumed_edges(point) for point in candidates)
    k_edge_set = set(k_edges)
    k_triangles = tuple(
        frozenset(tuple(sorted(edge)) for edge in combinations(triangle, 2))
        for triangle in combinations(range(vertex_count), 3)
        if consumed_edges(triangle) <= k_edge_set
    )

    for mask in range(1 << len(candidates)):
        family: list[Point] = []
        used_edges: set[Edge] = set()
        valid = True
        for index, candidate in enumerate(candidates):
            if not mask & (1 << index):
                continue
            if used_edges.intersection(consumptions[index]):
                valid = False
                break
            family.append(candidate)
            used_edges.update(consumptions[index])
        if not valid:
            continue

        # If all edges of a K3 are consumed, the three graph triangles must
        # meet at the single size-three point that consumes them.  Three
        # different pair-intersection points would force a graph edge into
        # two graph triangles.
        for triangle_edges in k_triangles:
            if not triangle_edges <= used_edges:
                continue
            holders = [
                point
                for point in family
                if triangle_edges <= consumed_edges(point)
            ]
            if len(holders) != 1 or len(holders[0]) != 3:
                valid = False
                break
        if not valid:
            continue

        loads = Counter(vertex for point in family for vertex in point)
        if any(loads[vertex] > 3 for vertex in range(vertex_count)):
            continue

        # Every active graph triangle has three original vertices.  Singleton
        # fillers have crossing count at most three and therefore cannot be a
        # support vertex of H, but including them checks that each abstract
        # family extends to a complete three-points-per-triangle incidence.
        completed = list(family)
        for vertex in range(vertex_count):
            completed.extend([(vertex,)] * (3 - loads[vertex]))
        yield tuple(completed)


def crossing_count(first: Point, second: Point, k_edges: tuple[Edge, ...]) -> int:
    k_edge_set = set(k_edges)
    crossings: set[Edge] = set()
    for left in first:
        for right in second:
            if left == right:
                continue
            edge = tuple(sorted((left, right)))
            if edge not in k_edge_set:
                crossings.add(edge)
    return len(crossings)


def audit_case(
    vertex_count: int, k_edges: tuple[Edge, ...]
) -> dict[int, tuple[int, int, frozenset[int]]]:
    raw = defaultdict(lambda: {"families": 0, "maximum": 0, "degrees": set()})
    for points in point_families(vertex_count, k_edges):
        triple_count = sum(len(point) == 3 for point in points)
        degrees = tuple(
            degree
            for first, second in combinations(points, 2)
            if (degree := crossing_count(first, second, k_edges))
            in NONZERO_H_DEGREES
        )
        row = raw[triple_count]
        row["families"] += 1
        row["maximum"] = max(row["maximum"], len(degrees))
        row["degrees"].update(degrees)
    return {
        triple_count: (
            int(row["families"]),
            int(row["maximum"]),
            frozenset(row["degrees"]),
        )
        for triple_count, row in raw.items()
    }


def minimum_mantel_support(edge_count: int) -> int:
    support = 0
    while support * support // 4 < edge_count:
        support += 1
    return support


def verify() -> None:
    n8, matching = matching_edges(8)
    n9, c9 = cycle_edges((9,))
    _, c4_c5 = cycle_edges((4, 5))
    _, c3_c6 = cycle_edges((3, 6))
    _, three_c3 = cycle_edges((3, 3, 3))

    matching_stats = audit_case(n8, matching)
    c9_stats = audit_case(n9, c9)
    c4_c5_stats = audit_case(n9, c4_c5)
    c3_c6_stats = audit_case(n9, c3_c6)
    three_c3_stats = audit_case(n9, three_c3)

    if matching_stats != {0: (16, 6, frozenset((4,)))}:
        raise AssertionError(f"wrong matching-family audit {matching_stats}")
    if c9_stats[0][0] != 512 or c9_stats[0][2] != {4}:
        raise AssertionError(f"wrong C9 family audit {c9_stats}")
    if c4_c5_stats[0][0] != 512 or c4_c5_stats[0][2] != {4}:
        raise AssertionError(f"wrong C4+C5 family audit {c4_c5_stats}")
    if c3_c6_stats != {
        0: (448, 15, frozenset((4,))),
        1: (64, 9, frozenset((4, 6))),
    }:
        raise AssertionError(f"wrong C3+C6 family audit {c3_c6_stats}")
    if three_c3_stats != {
        0: (343, 12, frozenset((4,))),
        1: (147, 8, frozenset((4, 6))),
        2: (21, 4, frozenset((6,))),
        3: (1, 0, frozenset()),
    }:
        raise AssertionError(f"wrong 3C3 family audit {three_c3_stats}")
    if minimum_mantel_support(24) != 10 or minimum_mantel_support(27) != 11:
        raise AssertionError("wrong Mantel support minimum")

    print("PASS generic N3 point-clique audit")
    print("n3_24_families", matching_stats[0][0])
    print("n3_24_support_maximum", matching_stats[0][1])
    print("n3_27_c3_c6_central_families", c3_c6_stats[1][0])
    print("n3_27_c3_c6_support_maximum", c3_c6_stats[1][1])
    print("n3_27_3c3_central_counts", [147, 21, 1])
    print("n3_27_3c3_support_maxima", [8, 4, 0])
    print("n3_27_mantel_support_minimum", 11)


def main() -> int:
    verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
