#!/usr/bin/env python3
"""Independent semantic and mutation audit of the Wave 14 all-size-two object.

This does not import or invoke any discovery-lane module.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter, defaultdict, deque
from pathlib import Path


def pair(a: int, b: int) -> tuple[int, int]:
    if a == b:
        raise AssertionError("loop")
    return (a, b) if a < b else (b, a)


def pairs(records) -> set[tuple[int, int]]:
    result = {pair(int(a), int(b)) for a, b in records}
    assert len(result) == len(records), "duplicate edge"
    return result


def rows(n: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    result = [set() for _ in range(n)]
    for a, b in edges:
        assert 0 <= a < b < n
        result[a].add(b)
        result[b].add(a)
    return result


def components(n: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    adj = rows(n, edges)
    unseen = set(range(n))
    result = []
    while unseen:
        root = min(unseen)
        component = {root}
        queue = deque([root])
        unseen.remove(root)
        while queue:
            v = queue.popleft()
            for w in adj[v]:
                if w in unseen:
                    unseen.remove(w)
                    component.add(w)
                    queue.append(w)
        result.append(component)
    return result


def triangle_count(n: int, edges: set[tuple[int, int]]) -> int:
    adj = rows(n, edges)
    return sum(
        len(adj[a] & adj[b])
        for a, b in edges
    ) // 3


def bipartition(component: set[int], adj: list[set[int]]) -> tuple[set[int], set[int]]:
    color: dict[int, int] = {}
    for root in component:
        if root in color:
            continue
        color[root] = 0
        queue = deque([root])
        while queue:
            v = queue.popleft()
            for w in adj[v]:
                if w not in color:
                    color[w] = 1 - color[v]
                    queue.append(w)
                else:
                    assert color[w] != color[v], "component is not bipartite"
    return (
        {v for v in component if color[v] == 0},
        {v for v in component if color[v] == 1},
    )


def decode_graph6(record: str) -> tuple[int, set[tuple[int, int]]]:
    assert record and not record.startswith(">>graph6<<")
    n = ord(record[0]) - 63
    assert 0 <= n <= 62
    bits = []
    for char in record[1:]:
        value = ord(char) - 63
        assert 0 <= value < 64
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    result = set()
    offset = 0
    for b in range(1, n):
        for a in range(b):
            if bits[offset]:
                result.add((a, b))
            offset += 1
    return n, result


def crossing(
    left: tuple[int, ...],
    right: tuple[int, ...],
    l_edges: set[tuple[int, int]],
) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    overlap = set(left) & set(right)
    assert len(overlap) <= 1
    left_only = tuple(v for v in left if v not in overlap)
    right_only = tuple(v for v in right if v not in overlap)
    left_degree = tuple(
        sum(pair(a, b) in l_edges for b in right_only)
        for a in left_only
    )
    right_degree = tuple(
        sum(pair(a, b) in l_edges for a in left_only)
        for b in right_only
    )
    return sum(left_degree), left_degree, right_degree


def verify_data(data: dict) -> dict:
    n = int(data["active_label_order"])
    assert n == 16
    q = tuple(map(int, data["q_values"]))
    assert q == (2,) * 16 and sum(q) == 32

    point_list = tuple(tuple(map(int, p)) for p in data["point_sets"])
    assert len(point_list) == 24
    assert all(len(p) == 2 and p[0] < p[1] for p in point_list)
    f_edges = set(point_list)
    assert len(f_edges) == 24
    f_rows = rows(n, f_edges)
    assert {len(row) for row in f_rows} == {3}
    assert triangle_count(n, f_edges) == 0
    g6_n, g6_edges = decode_graph6(data["point_graph_graph6"])
    assert (g6_n, g6_edges) == (n, f_edges)

    f_components = components(n, f_edges)
    assert sorted(map(len, f_components)) == [8, 8]
    for component in f_components:
        left, right = bipartition(component, f_rows)
        assert len(left) == len(right) == 4
        # A connected cubic bipartite graph on 4+4 vertices is K4,4 minus a
        # perfect matching, hence Q3.
        assert all(len(f_rows[v] & right) == 3 for v in left)
        assert all(len(f_rows[v] & left) == 3 for v in right)

    k_edges = pairs(data["K_edges"])
    l_edges = pairs(data["L_edges"])
    universe = set(itertools.combinations(range(n), 2))
    assert k_edges.isdisjoint(l_edges)
    assert k_edges | l_edges == universe
    assert len(k_edges) == 72 and {len(r) for r in rows(n, k_edges)} == {9}
    assert len(l_edges) == 48 and {len(r) for r in rows(n, l_edges)} == {6}
    assert f_edges <= k_edges
    for center in range(n):
        for a, b in itertools.combinations(f_rows[center], 2):
            assert pair(a, b) in k_edges, "missing singleton-crossing K edge"

    label_points = [[] for _ in range(n)]
    for p_index, p in enumerate(point_list):
        for label in p:
            label_points[label].append(p_index)
    assert all(len(indices) == 3 for indices in label_points)

    support_edges = pairs(data["positive_support_point_pairs"])
    assert len(support_edges) == 24
    support_rows = rows(len(point_list), support_edges)
    assert {len(row) for row in support_rows} == {2}
    support_components = components(len(point_list), support_edges)
    assert sorted(map(len, support_components)) == [4] * 6
    assert all(
        sum(pair(a, b) in support_edges for a, b in itertools.combinations(c, 2)) == 4
        for c in support_components
    )

    support_order = tuple(tuple(map(int, e)) for e in data["positive_support_point_pairs"])
    coverage: dict[tuple[int, int], list[int]] = defaultdict(list)
    for support_index, (p_index, q_index) in enumerate(support_order):
        p = point_list[p_index]
        q_point = point_list[q_index]
        assert set(p).isdisjoint(q_point)
        rectangle = {pair(a, b) for a in p for b in q_point}
        assert len(rectangle) == 4 and rectangle <= l_edges
        for label_edge in rectangle:
            coverage[label_edge].append(support_index)
    assert set(coverage) == l_edges
    assert all(len(indices) == 2 for indices in coverage.values())

    line_edges = {
        pair(p, q_point)
        for p, q_point in itertools.combinations(range(len(point_list)), 2)
        if set(point_list[p]) & set(point_list[q_point])
    }
    active_edges = pairs(data["active_original_adjacency"])
    assert active_edges == line_edges | support_edges
    assert line_edges.isdisjoint(support_edges)
    active_rows = rows(len(point_list), active_edges)

    # Check each L-edge as a literal induced N3 on its two active point
    # triangles. This directly checks that the two selected cross graph
    # edges are independent, rather than relying on the lambda cap to imply it.
    for i, j in l_edges:
        left = label_points[i]
        right = label_points[j]
        assert set(left).isdisjoint(right)
        assert all(pair(a, b) in active_edges for a, b in itertools.combinations(left, 2))
        assert all(pair(a, b) in active_edges for a, b in itertools.combinations(right, 2))
        cross = {
            pair(a, b)
            for a in left
            for b in right
            if pair(a, b) in active_edges
        }
        assert len(cross) == 2
        endpoints = [v for e in cross for v in e]
        assert len(set(endpoints)) == 4, "N3 cross edges are not independent"
        assert set(coverage[(i, j)]) == {
            support_order.index(e) if e in support_order else support_order.index((e[1], e[0]))
            for e in cross
        }

    h_edges = pairs(data["H_nonisolated_edges"])
    expected_h = {
        pair(indices[0], indices[1])
        for indices in coverage.values()
    }
    assert h_edges == expected_h
    assert len(h_edges) == 48
    h_rows = rows(len(support_order), h_edges)
    assert {len(row) for row in h_rows} == {4}
    assert triangle_count(len(support_order), h_edges) == 0
    assert len(components(len(support_order), h_edges)) == 1

    crossing_degree = {}
    for p_index, q_index in active_edges:
        size, left_degree, right_degree = crossing(
            point_list[p_index], point_list[q_index], l_edges
        )
        assert all(d in (0, 2) for d in left_degree + right_degree)
        assert size in (0, 4)
        crossing_degree[(p_index, q_index)] = size
    assert {e for e, d in crossing_degree.items() if d == 4} == support_edges
    assert all(crossing_degree[e] == 0 for e in line_edges)
    for p_index, p in enumerate(point_list):
        total = sum(d for e, d in crossing_degree.items() if p_index in e)
        assert total == 2 * sum(q[label] for label in p) == 8

    histogram = Counter()
    for p, q_point in itertools.combinations(range(len(point_list)), 2):
        common = len(active_rows[p] & active_rows[q_point])
        histogram[common] += 1
        assert common <= 2
        if pair(p, q_point) in active_edges:
            assert common <= 1

    return {
        "status": "PASS",
        "F_components": [len(c) for c in f_components],
        "support_components": [len(c) for c in support_components],
        "L_edges": len(l_edges),
        "support_edges": len(support_edges),
        "H_edges": len(h_edges),
        "H_connected": True,
        "H_triangle_count": 0,
        "active_common_neighbor_histogram": dict(sorted(histogram.items())),
        "direct_N3_matching_checks": len(l_edges),
    }


def mutation_audit(data: dict) -> dict[str, str]:
    mutations = {}

    q_bad = copy.deepcopy(data)
    q_bad["q_values"][0] = 3
    mutations["q_value"] = q_bad

    complement_bad = copy.deepcopy(data)
    complement_bad["L_edges"][0] = list(complement_bad["K_edges"][0])
    mutations["K_L_complement"] = complement_bad

    support_bad = copy.deepcopy(data)
    support_bad["positive_support_point_pairs"][0] = [0, 1]
    mutations["support_rectangle"] = support_bad

    h_bad = copy.deepcopy(data)
    h_bad["H_nonisolated_edges"][0] = [0, 1]
    mutations["H_reconstruction"] = h_bad

    active_bad = copy.deepcopy(data)
    active_bad["active_original_adjacency"][0] = [0, 4]
    mutations["actual_edge_crossing"] = active_bad

    results = {}
    for name, mutant in mutations.items():
        try:
            verify_data(mutant)
        except (AssertionError, ValueError):
            results[name] = "REJECTED"
        else:
            results[name] = "SURVIVED"
    assert set(results.values()) == {"REJECTED"}
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    raw = args.certificate.read_bytes()
    data = json.loads(raw)
    result = verify_data(data)
    result["certificate_sha256"] = hashlib.sha256(raw).hexdigest()
    result["mutations"] = mutation_audit(data)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
