#!/usr/bin/env python3
"""Exploratory exact census for the Wave 14 all-size-two r=16 branch.

Input is intended to be the graph6 output of

    geng -q -td3D3 16 24:24

For every cubic triangle-free point graph F, this program independently
validates the record and applies only the following necessary relaxation:

* K contains F and every pair of F-neighbours (singleton crossing);
* a positive H-support joins disjoint F-edges whose four endpoint cross-pairs
  all avoid that mandatory part of K;
* the fixed-point identity makes the positive-support graph 2-regular on
  E(F); and
* in A = line(F) union support, adjacent pairs have at most one common active
  neighbour and all pairs have at most two.

A survivor is only an abstract active-support countermodel, not a Conway
graph.  A zero census would still depend on the external completeness of
geng and would not be a formal UNSAT certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


ORDER = 16
POINT_COUNT = 24
EXPECTED_RECORDS = 801


def edge(a: int, b: int) -> tuple[int, int]:
    if a == b:
        raise ValueError("loop")
    return (a, b) if a < b else (b, a)


def decode_graph6(record: str) -> tuple[int, frozenset[tuple[int, int]]]:
    if not record or record.startswith(">>graph6<<"):
        raise ValueError("bare short graph6 record required")
    order = ord(record[0]) - 63
    if not 0 <= order <= 62:
        raise ValueError("short graph6 order required")
    bits: list[int] = []
    for character in record[1:]:
        value = ord(character) - 63
        if not 0 <= value <= 63:
            raise ValueError("bad graph6 character")
        bits.extend((value >> bit) & 1 for bit in range(5, -1, -1))
    needed = order * (order - 1) // 2
    if len(bits) < needed:
        raise ValueError("truncated graph6 record")
    edges = set()
    offset = 0
    for right in range(1, order):
        for left in range(right):
            if bits[offset]:
                edges.add((left, right))
            offset += 1
    return order, frozenset(edges)


def adjacency(order: int, edges: frozenset[tuple[int, int]]) -> list[set[int]]:
    output = [set() for _ in range(order)]
    for a, b in edges:
        output[a].add(b)
        output[b].add(a)
    return output


def validate_f(edges: frozenset[tuple[int, int]]) -> None:
    if len(edges) != POINT_COUNT:
        raise AssertionError("wrong edge count")
    adj = adjacency(ORDER, edges)
    if any(len(row) != 3 for row in adj):
        raise AssertionError("not cubic")
    if any(
        b in adj[a] and c in adj[a] and c in adj[b]
        for a in range(ORDER)
        for b in range(a + 1, ORDER)
        for c in range(b + 1, ORDER)
    ):
        raise AssertionError("not triangle-free")


def mandatory_k(
    f_edges: frozenset[tuple[int, int]],
) -> frozenset[tuple[int, int]]:
    adj = adjacency(ORDER, f_edges)
    output = set(f_edges)
    for row in adj:
        output.update(edge(a, b) for a, b in itertools.combinations(row, 2))
    return frozenset(output)


def line_edges(points: tuple[tuple[int, int], ...]) -> frozenset[tuple[int, int]]:
    return frozenset(
        (i, j)
        for i, j in itertools.combinations(range(POINT_COUNT), 2)
        if set(points[i]) & set(points[j])
    )


def compatible_supports(
    points: tuple[tuple[int, int], ...],
    mandatory: frozenset[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    output = []
    for i, j in itertools.combinations(range(POINT_COUNT), 2):
        if set(points[i]) & set(points[j]):
            continue
        cross = {
            edge(a, b)
            for a in points[i]
            for b in points[j]
        }
        if not cross & mandatory:
            output.append((i, j))
    return tuple(output)


def cap_ok(
    forced_line: frozenset[tuple[int, int]],
    selected: set[tuple[int, int]],
) -> bool:
    rows = [0] * POINT_COUNT
    for a, b in forced_line:
        rows[a] |= 1 << b
        rows[b] |= 1 << a
    for a, b in selected:
        rows[a] |= 1 << b
        rows[b] |= 1 << a
    adjacency_edges = forced_line | selected
    for a, b in itertools.combinations(range(POINT_COUNT), 2):
        common = (rows[a] & rows[b]).bit_count()
        if common > 2:
            return False
        if (a, b) in adjacency_edges and common > 1:
            return False
    return True


def factor_search(
    points: tuple[tuple[int, int], ...],
    forced_line: frozenset[tuple[int, int]],
    compatible: tuple[tuple[int, int], ...],
    node_limit: int,
) -> dict[str, object]:
    incident: list[list[tuple[int, int]]] = [[] for _ in range(POINT_COUNT)]
    for pair in compatible:
        incident[pair[0]].append(pair)
        incident[pair[1]].append(pair)
    rectangles = {
        pair: frozenset(
            edge(a, b)
            for a in points[pair[0]]
            for b in points[pair[1]]
        )
        for pair in compatible
    }
    covering: dict[tuple[int, int], list[tuple[int, int]]] = {
        pair: [] for pair in itertools.combinations(range(ORDER), 2)
    }
    for support, rectangle in rectangles.items():
        for label_pair in rectangle:
            covering[label_pair].append(support)
    selected: set[tuple[int, int]] = set()
    excluded: set[tuple[int, int]] = set()
    degree = [0] * POINT_COUNT
    stats: Counter[str] = Counter()
    solution: tuple[tuple[int, int], ...] | None = None
    cutoff = False

    def include(pair: tuple[int, int]) -> bool:
        a, b = pair
        if pair in selected:
            return True
        if pair in excluded or degree[a] >= 2 or degree[b] >= 2:
            return False
        selected.add(pair)
        degree[a] += 1
        degree[b] += 1
        return True

    def snapshot():
        return set(selected), set(excluded), degree[:]

    def restore(state) -> None:
        saved_selected, saved_excluded, saved_degree = state
        selected.clear()
        selected.update(saved_selected)
        excluded.clear()
        excluded.update(saved_excluded)
        degree[:] = saved_degree

    def propagate() -> bool:
        while True:
            changed = False
            for vertex in range(POINT_COUNT):
                available = [
                    pair
                    for pair in incident[vertex]
                    if pair not in selected and pair not in excluded
                ]
                need = 2 - degree[vertex]
                if need < 0 or len(available) < need:
                    stats["degree_rejections"] += 1
                    return False
                if need == 0 and available:
                    excluded.update(available)
                    changed = True
                    break
                if need == len(available) and need:
                    for pair in available:
                        if not include(pair):
                            stats["degree_rejections"] += 1
                            return False
                    if not cap_ok(forced_line, selected):
                        stats["cap_rejections"] += 1
                        return False
                    changed = True
                    break
            if not changed:
                coverage: Counter[tuple[int, int]] = Counter()
                for pair in selected:
                    coverage.update(rectangles[pair])
                if any(value > 2 for value in coverage.values()):
                    stats["coverage_rejections"] += 1
                    return False
                forced_supports = set()
                for label_pair, value in coverage.items():
                    if value != 1:
                        continue
                    available = [
                        pair
                        for pair in covering[label_pair]
                        if pair not in selected
                        and pair not in excluded
                        and degree[pair[0]] < 2
                        and degree[pair[1]] < 2
                    ]
                    if not available:
                        stats["coverage_rejections"] += 1
                        return False
                    if len(available) == 1:
                        forced_supports.add(available[0])
                if forced_supports:
                    for pair in sorted(forced_supports):
                        if not include(pair):
                            stats["coverage_rejections"] += 1
                            return False
                    if not cap_ok(forced_line, selected):
                        stats["cap_rejections"] += 1
                        return False
                    changed = True
            if not changed:
                return True

    def visit() -> None:
        nonlocal solution, cutoff
        if solution is not None or cutoff:
            return
        stats["nodes"] += 1
        if stats["nodes"] > node_limit:
            cutoff = True
            return
        entry = snapshot()
        if not propagate():
            restore(entry)
            return
        if all(value == 2 for value in degree):
            coverage: Counter[tuple[int, int]] = Counter()
            for pair in selected:
                coverage.update(rectangles[pair])
            if any(value not in (0, 2) for value in coverage.values()):
                stats["coverage_rejections"] += 1
                restore(entry)
                return
            if sum(value == 2 for value in coverage.values()) != 48:
                raise AssertionError("coverage handshake changed")
            stats["solutions"] += 1
            solution = tuple(sorted(selected))
            restore(entry)
            return
        choices = []
        for vertex in range(POINT_COUNT):
            if degree[vertex] == 2:
                continue
            available = [
                pair
                for pair in incident[vertex]
                if pair not in selected and pair not in excluded
            ]
            need = 2 - degree[vertex]
            choices.append((len(available) - need, len(available), vertex, available))
        _slack, _count, _vertex, available = min(choices)
        pair = available[0]

        branch = snapshot()
        if include(pair):
            if cap_ok(forced_line, selected):
                visit()
            else:
                stats["cap_rejections"] += 1
        restore(branch)

        excluded.add(pair)
        visit()
        restore(branch)
        restore(entry)

    visit()
    return {
        "status": "CUTOFF" if cutoff else ("SAT" if solution is not None else "UNSAT"),
        "statistics": dict(sorted(stats.items())),
        "solution": [list(pair) for pair in solution] if solution else None,
    }


def run(
    path: Path,
    node_limit: int,
    selected_indices: frozenset[int] | None = None,
) -> dict[str, object]:
    records = [
        line.strip()
        for line in path.read_text(encoding="ascii").splitlines()
        if line.strip()
    ]
    if len(records) != EXPECTED_RECORDS:
        raise AssertionError(f"expected {EXPECTED_RECORDS} records, got {len(records)}")
    if len(records) != len(set(records)):
        raise AssertionError("duplicate graph6 records")

    totals: Counter[str] = Counter()
    survivors = []
    cutoffs = []
    mandatory_hist: Counter[int] = Counter()
    processed = 0
    for index, record in enumerate(records):
        if selected_indices is not None and index not in selected_indices:
            continue
        processed += 1
        order, f_edges = decode_graph6(record)
        if order != ORDER:
            raise AssertionError("wrong order")
        validate_f(f_edges)
        mandatory = mandatory_k(f_edges)
        mandatory_degrees = tuple(len(row) for row in adjacency(ORDER, mandatory))
        if max(mandatory_degrees) > 9:
            raise AssertionError("mandatory K exceeds degree nine")
        mandatory_hist[len(mandatory)] += 1
        points = tuple(sorted(f_edges))
        forced_line = line_edges(points)
        compatible = compatible_supports(points, mandatory)
        search = factor_search(points, forced_line, compatible, node_limit)
        totals[search["status"]] += 1
        item = {
            "catalog_index": index,
            "graph6": record,
            "mandatory_k_edges": len(mandatory),
            "mandatory_k_degree_histogram": dict(
                sorted(Counter(mandatory_degrees).items())
            ),
            "compatible_support_edges": len(compatible),
            "search": search,
        }
        if search["status"] == "SAT":
            survivors.append(item)
        elif search["status"] == "CUTOFF":
            cutoffs.append(item)

    return {
        "scope": "all-size-two r=16 active-support relaxation",
        "catalog": path.as_posix(),
        "catalog_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "catalog_records": len(records),
        "processed_records": processed,
        "selected_indices": (
            sorted(selected_indices) if selected_indices is not None else None
        ),
        "catalog_completeness_external_premise": "nauty_2.9.3_geng_-q_-td3D3_16_24:24",
        "mandatory_k_edge_histogram": dict(sorted(mandatory_hist.items())),
        "search_status_histogram": dict(sorted(totals.items())),
        "survivor_count": len(survivors),
        "cutoff_count": len(cutoffs),
        "survivors": survivors,
        "cutoffs": cutoffs,
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "limitations": [
            "all-active-points-restricted-to-size-two",
            "K-tested-only-through-its-mandatory-subgraph",
            "geng-completeness-is-external",
            "no-formal-proof-trace",
            "not-a-99-vertex-search",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--node-limit", type=int, default=1_000_000)
    parser.add_argument(
        "--indices",
        help="optional comma-separated catalog indices to process",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    selected_indices = (
        frozenset(int(value) for value in args.indices.split(","))
        if args.indices
        else None
    )
    result = run(args.catalog, args.node_limit, selected_indices)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    print(
        "records", result["catalog_records"],
        "statuses", result["search_status_histogram"],
        "survivors", result["survivor_count"],
        "cutoffs", result["cutoff_count"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
