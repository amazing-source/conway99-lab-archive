#!/usr/bin/env python3
"""Independent semantic validator for the Wave 14 active countermodel.

Passing this validator means that the JSON object satisfies the explicitly
listed active/local relaxation.  It emphatically does not validate a
99-vertex strongly regular graph.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


def edge(a: int, b: int) -> tuple[int, int]:
    assert a != b
    return (a, b) if a < b else (b, a)


def edge_set(records) -> set[tuple[int, int]]:
    output = {edge(int(a), int(b)) for a, b in records}
    assert len(output) == len(records)
    return output


def degrees(order: int, edges: set[tuple[int, int]]) -> tuple[int, ...]:
    output = [0] * order
    for a, b in edges:
        assert 0 <= a < b < order
        output[a] += 1
        output[b] += 1
    return tuple(output)


def adjacency(order: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    output = [set() for _ in range(order)]
    for a, b in edges:
        output[a].add(b)
        output[b].add(a)
    return output


def triangles(order: int, edges: set[tuple[int, int]]) -> list[tuple[int, int, int]]:
    return [
        triple
        for triple in itertools.combinations(range(order), 3)
        if all(edge(a, b) in edges for a, b in itertools.combinations(triple, 2))
    ]


def decode_graph6(record: str) -> tuple[int, set[tuple[int, int]]]:
    assert record and not record.startswith(">>graph6<<")
    order = ord(record[0]) - 63
    assert 0 <= order <= 62
    bits = []
    for character in record[1:]:
        value = ord(character) - 63
        assert 0 <= value <= 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    output = set()
    offset = 0
    for right in range(1, order):
        for left in range(right):
            if bits[offset]:
                output.add((left, right))
            offset += 1
    return order, output


def crossing(
    left_point: tuple[int, int],
    right_point: tuple[int, int],
    l_edges: set[tuple[int, int]],
) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    overlap = set(left_point) & set(right_point)
    assert len(overlap) <= 1
    left = [value for value in left_point if value not in overlap]
    right = [value for value in right_point if value not in overlap]
    left_degrees = [
        sum(edge(a, b) in l_edges for b in right)
        for a in left
    ]
    right_degrees = [
        sum(edge(a, b) in l_edges for a in left)
        for b in right
    ]
    return sum(left_degrees), tuple(left_degrees), tuple(right_degrees)


def verify(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema"] == "wave14-all2-active-countermodel-v1"
    assert data["claim_label"] == "CANDIDATE"

    order = data["active_label_order"]
    assert order == 16
    q = tuple(data["q_values"])
    assert q == (2,) * order and sum(q) == 32

    points = tuple(tuple(pair) for pair in data["point_sets"])
    assert len(points) == 24 and len(set(points)) == 24
    assert all(len(pair) == 2 and pair[0] < pair[1] for pair in points)
    point_graph = set(points)
    assert degrees(order, point_graph) == (3,) * order
    assert not triangles(order, point_graph)
    decoded_order, decoded_edges = decode_graph6(data["point_graph_graph6"])
    assert decoded_order == order and decoded_edges == point_graph

    l_edges = edge_set(data["L_edges"])
    k_edges = edge_set(data["K_edges"])
    all_pairs = set(itertools.combinations(range(order), 2))
    assert l_edges.isdisjoint(k_edges)
    assert l_edges | k_edges == all_pairs
    assert len(l_edges) == 48 and degrees(order, l_edges) == (6,) * order
    assert len(k_edges) == 72 and degrees(order, k_edges) == (9,) * order
    assert point_graph <= k_edges

    # Singleton crossing at every active label forces every distance-two pair
    # of the cubic point graph into K.
    point_adjacency = adjacency(order, point_graph)
    mandatory_k = set(point_graph)
    for row in point_adjacency:
        mandatory_k.update(edge(a, b) for a, b in itertools.combinations(row, 2))
    assert mandatory_k <= k_edges

    support = tuple(tuple(pair) for pair in data["positive_support_point_pairs"])
    assert len(support) == 24 and len(set(support)) == 24
    support_set = set(support)
    assert degrees(len(points), support_set) == (2,) * len(points)

    coverage: dict[tuple[int, int], list[int]] = defaultdict(list)
    for support_index, (left_index, right_index) in enumerate(support):
        assert 0 <= left_index < right_index < len(points)
        assert set(points[left_index]).isdisjoint(points[right_index])
        cross_pairs = {
            edge(a, b)
            for a in points[left_index]
            for b in points[right_index]
        }
        assert len(cross_pairs) == 4 and cross_pairs <= l_edges
        for label_pair in cross_pairs:
            coverage[label_pair].append(support_index)
    assert set(coverage) == l_edges
    assert Counter(map(len, coverage.values())) == Counter({2: 48})

    expected_h = {
        edge(indices[0], indices[1])
        for indices in coverage.values()
    }
    h_edges = edge_set(data["H_nonisolated_edges"])
    assert h_edges == expected_h and len(h_edges) == 48
    assert degrees(len(support), h_edges) == (4,) * len(support)
    assert not triangles(len(support), h_edges)

    line_edges = {
        (left, right)
        for left, right in itertools.combinations(range(len(points)), 2)
        if set(points[left]) & set(points[right])
    }
    active_adjacency = edge_set(data["active_original_adjacency"])
    assert line_edges.isdisjoint(support_set)
    assert active_adjacency == line_edges | support_set
    assert degrees(len(points), active_adjacency) == (6,) * len(points)

    # Every selected active graph edge obeys the inherited two-sided labeled
    # crossing rule.  Meeting point pairs have empty crossing; support pairs
    # have a full 2-by-2 crossing.
    h_degree_by_active_edge = {}
    for pair in active_adjacency:
        size, left_degrees, right_degrees = crossing(
            points[pair[0]], points[pair[1]], l_edges
        )
        assert all(value in (0, 2) for value in left_degrees + right_degrees)
        assert size in (0, 4)
        h_degree_by_active_edge[pair] = size
    assert {pair for pair, value in h_degree_by_active_edge.items() if value == 4} == support_set
    assert all(h_degree_by_active_edge[pair] == 0 for pair in line_edges)

    # Fixed-point identity: 2*(q_i+q_j)=8 for every size-two point.
    for point_index, point in enumerate(points):
        total = sum(
            value
            for pair, value in h_degree_by_active_edge.items()
            if point_index in pair
        )
        assert total == 2 * sum(q[label] for label in point) == 8

    # Necessary SRG common-neighbour upper caps in the forced active subgraph.
    active_rows = adjacency(len(points), active_adjacency)
    cap_histogram = Counter()
    for left, right in itertools.combinations(range(len(points)), 2):
        common = len(active_rows[left] & active_rows[right])
        cap_histogram[common] += 1
        assert common <= 2
        if (left, right) in active_adjacency:
            assert common <= 1

    return {
        "status": "PASS active-relaxation countermodel",
        "claim_label": "CANDIDATE",
        "active_labels": order,
        "active_points": len(points),
        "L_edges": len(l_edges),
        "K_edges": len(k_edges),
        "positive_support_edges": len(support),
        "H_edges": len(h_edges),
        "H_triangle_count": 0,
        "active_common_neighbor_histogram": dict(sorted(cap_histogram.items())),
        "target_result": "UNKNOWN",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.certificate), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
