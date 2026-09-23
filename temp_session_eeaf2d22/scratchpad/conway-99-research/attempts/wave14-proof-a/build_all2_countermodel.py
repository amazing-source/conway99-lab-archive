#!/usr/bin/env python3
"""Build the explicit r=16 all-size-two active-relaxation countermodel.

The object was discovered in catalog record 12 by ``all2_census.py``.  This
builder expands the compact graph6/support description into a complete JSON
record.  It is a countermodel only to the listed active/local constraints,
not a partial or complete Conway graph.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


GRAPH6 = "O????B_sD_M?B_BO@W?M?"
SUPPORT_INDEX_PAIRS = (
    (0, 12),
    (0, 23),
    (1, 13),
    (1, 20),
    (2, 18),
    (2, 21),
    (3, 15),
    (3, 22),
    (4, 16),
    (4, 19),
    (5, 18),
    (5, 21),
    (6, 14),
    (6, 17),
    (7, 16),
    (7, 19),
    (8, 13),
    (8, 20),
    (9, 14),
    (9, 17),
    (10, 15),
    (10, 22),
    (11, 12),
    (11, 23),
)


def edge(a: int, b: int) -> tuple[int, int]:
    if a == b:
        raise ValueError("loop")
    return (a, b) if a < b else (b, a)


def decode_graph6(record: str) -> tuple[int, tuple[tuple[int, int], ...]]:
    order = ord(record[0]) - 63
    bits = []
    for character in record[1:]:
        value = ord(character) - 63
        bits.extend((value >> bit) & 1 for bit in range(5, -1, -1))
    output = []
    offset = 0
    for right in range(1, order):
        for left in range(right):
            if bits[offset]:
                output.append((left, right))
            offset += 1
    return order, tuple(sorted(output))


def cycles(order: int, edges: set[tuple[int, int]]) -> list[list[int]]:
    adjacency = [set() for _ in range(order)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    output = []
    seen = set()
    for start in range(order):
        if start in seen:
            continue
        cycle = []
        previous = None
        current = start
        while current not in seen:
            seen.add(current)
            cycle.append(current)
            following = min(adjacency[current] - ({previous} if previous is not None else set()))
            previous, current = current, following
        output.append(cycle)
    return output


def build() -> dict[str, object]:
    order, points = decode_graph6(GRAPH6)
    if order != 16 or len(points) != 24:
        raise AssertionError("frozen point graph changed")
    support = tuple(sorted(SUPPORT_INDEX_PAIRS))

    coverage: dict[tuple[int, int], list[int]] = defaultdict(list)
    for support_index, (left, right) in enumerate(support):
        for a in points[left]:
            for b in points[right]:
                coverage[edge(a, b)].append(support_index)
    if set(map(len, coverage.values())) != {2}:
        raise AssertionError("coverage is not exact two")

    l_edges = tuple(sorted(coverage))
    all_label_pairs = set(itertools.combinations(range(order), 2))
    k_edges = tuple(sorted(all_label_pairs - set(l_edges)))
    h_edges = tuple(
        sorted(edge(indices[0], indices[1]) for indices in coverage.values())
    )
    line = tuple(
        (left, right)
        for left, right in itertools.combinations(range(len(points)), 2)
        if set(points[left]) & set(points[right])
    )
    active_adjacency = tuple(sorted(set(line) | set(support)))

    return {
        "schema": "wave14-all2-active-countermodel-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "countermodel to the enumerated r=16 all-size-two active/local "
            "relaxation; not a Conway-99 graph or partial completion"
        ),
        "active_label_order": order,
        "q_values": [2] * order,
        "point_graph_graph6": GRAPH6,
        "point_sets": [list(pair) for pair in points],
        "positive_support_point_pairs": [list(pair) for pair in support],
        "L_edges": [list(pair) for pair in l_edges],
        "K_edges": [list(pair) for pair in k_edges],
        "H_nonisolated_edges": [list(pair) for pair in h_edges],
        "active_original_adjacency": [list(pair) for pair in active_adjacency],
        "derived": {
            "point_graph_components": [
                [0, 1, 2, 3, 8, 9, 10, 11],
                [4, 5, 6, 7, 12, 13, 14, 15],
            ],
            "positive_support_cycles": cycles(24, set(support)),
            "point_count": len(points),
            "L_edge_count": len(l_edges),
            "K_edge_count": len(k_edges),
            "H_edge_count": len(h_edges),
            "active_adjacency_edge_count": len(active_adjacency),
            "coverage_histogram": dict(sorted(Counter(map(len, coverage.values())).items())),
        },
        "limitations": [
            "only-active-label-and-active-point-constraints-are-modeled",
            "75-other-original-vertices-and-the-rest-of-G-are-absent",
            "not-a-positive-certificate",
            "not-a-negative-certificate",
            "does-not-show-full-graph-extendability",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(
        json.dumps(build(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
