#!/usr/bin/env python3
"""Replay the independent n3=42 support-cap rejection certificate.

This checker does not import the certificate builder or the construction-lane
program.  It uses set-valued graphs, re-derives every support opportunity,
and validates that the proof tree partitions all support assignments using
only sound degree or monotone common-neighbour implications.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any


EXPECTED_SCD_SHA256 = "6f3e9cf2b7e0d85c5df59c1638ab9d2fddbfc9905c49b35da01cc892f847e9a0"
EXPECTED_GRAPH6_SHA256 = "24bfd4964cc4e86554f721ff0f988c5e0bb8fc992b6113f142f09737d3ac90fd"

VertexGraph = tuple[frozenset[int], ...]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def graph_from_edges(n: int, edges: list[tuple[int, int]]) -> VertexGraph:
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        if u == v or not (0 <= u < n and 0 <= v < n):
            raise AssertionError(f"bad edge {(u, v)}")
        if v in adjacency[u]:
            raise AssertionError(f"duplicate edge {(u, v)}")
        adjacency[u].add(v)
        adjacency[v].add(u)
    return tuple(frozenset(neighbours) for neighbours in adjacency)


def edges(graph: VertexGraph) -> list[tuple[int, int]]:
    return [
        (u, v)
        for u in range(len(graph))
        for v in sorted(graph[u])
        if u < v
    ]


def decode_graph6(text: str) -> VertexGraph:
    data = text.strip().encode("ascii")
    if not data or data[0] == ord("~"):
        raise AssertionError("expected small-order graph6")
    n = data[0] - 63
    bitstream = "".join(f"{byte - 63:06b}" for byte in data[1:])
    required = n * (n - 1) // 2
    if len(bitstream) < required or "1" in bitstream[required:]:
        raise AssertionError("invalid graph6 data length/padding")
    result = []
    offset = 0
    for right in range(1, n):
        for left in range(right):
            if bitstream[offset] == "1":
                result.append((left, right))
            offset += 1
    return graph_from_edges(n, result)


def decode_shortcode_archive(data: bytes, n: int = 14, degree: int = 3) -> list[VertexGraph]:
    code_size = n * degree // 2
    previous: list[int] = []
    cursor = 0
    result: list[VertexGraph] = []
    while cursor < len(data):
        prefix = data[cursor]
        cursor += 1
        if prefix > code_size or (not result and prefix != 0):
            raise AssertionError("invalid shortcode prefix")
        suffix = code_size - prefix
        if cursor + suffix > len(data):
            raise AssertionError("truncated shortcode record")
        code = previous[:prefix] + list(data[cursor : cursor + suffix])
        cursor += suffix

        adjacency = [set() for _ in range(n)]
        position = 0
        for lower in range(n):
            needed = degree - len(adjacency[lower])
            previous_upper = lower
            for _ in range(needed):
                upper = code[position] - 1
                position += 1
                if not lower < upper < n or upper <= previous_upper:
                    raise AssertionError("invalid shortcode endpoint ordering")
                adjacency[lower].add(upper)
                adjacency[upper].add(lower)
                previous_upper = upper
        graph = tuple(frozenset(neighbours) for neighbours in adjacency)
        if position != code_size or any(len(neighbours) != degree for neighbours in graph):
            raise AssertionError("shortcode regularity failure")
        result.append(graph)
        previous = code
    if cursor != len(data):
        raise AssertionError("shortcode trailing data")
    return result


def component_sets(graph: VertexGraph) -> list[frozenset[int]]:
    remaining = set(range(len(graph)))
    answer = []
    while remaining:
        root = min(remaining)
        seen = {root}
        queue = deque([root])
        while queue:
            vertex = queue.popleft()
            for neighbour in graph[vertex]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    queue.append(neighbour)
        remaining -= seen
        answer.append(frozenset(seen))
    return sorted(answer, key=lambda part: (len(part), min(part)))


def bipartite_on(graph: VertexGraph, vertices: frozenset[int]) -> bool:
    colour: dict[int, int] = {}
    for root in vertices:
        if root in colour:
            continue
        colour[root] = 0
        queue = deque([root])
        while queue:
            vertex = queue.popleft()
            for neighbour in graph[vertex] & vertices:
                if neighbour not in colour:
                    colour[neighbour] = 1 - colour[vertex]
                    queue.append(neighbour)
                elif colour[neighbour] == colour[vertex]:
                    return False
    return True


def vertex_signature(graph: VertexGraph, root: int) -> tuple[int, ...]:
    distance = {root: 0}
    queue = deque([root])
    while queue:
        vertex = queue.popleft()
        for neighbour in graph[vertex]:
            if neighbour not in distance:
                distance[neighbour] = distance[vertex] + 1
                queue.append(neighbour)
    histogram = Counter(distance.values())
    return (len(graph[root]),) + tuple(
        histogram[level] for level in range(max(histogram) + 1)
    )


def isomorphic(source: VertexGraph, target: VertexGraph) -> bool:
    """A second, mapping-first isomorphism backtracker for claimed pairs."""

    if len(source) != len(target) or len(edges(source)) != len(edges(target)):
        return False
    n = len(source)
    source_signatures = [vertex_signature(source, v) for v in range(n)]
    target_signatures = [vertex_signature(target, v) for v in range(n)]
    if Counter(source_signatures) != Counter(target_signatures):
        return False
    forward: dict[int, int] = {}
    used: set[int] = set()

    def options(vertex: int) -> list[int]:
        choices = []
        for image in range(n):
            if image in used or source_signatures[vertex] != target_signatures[image]:
                continue
            if all(
                ((other in source[vertex]) == (mapped in target[image]))
                for other, mapped in forward.items()
            ):
                choices.append(image)
        return choices

    def recurse() -> bool:
        if len(forward) == n:
            return True
        candidates = []
        for vertex in range(n):
            if vertex in forward:
                continue
            available = options(vertex)
            if not available:
                return False
            mapped_neighbours = sum(neighbour in forward for neighbour in source[vertex])
            candidates.append((len(available), -mapped_neighbours, vertex, available))
        _, _, vertex, available = min(candidates)
        for image in available:
            forward[vertex] = image
            used.add(image)
            if recurse():
                return True
            used.remove(image)
            del forward[vertex]
        return False

    return recurse()


def mandatory_edges(graph: VertexGraph) -> set[tuple[int, int]]:
    mandatory = set(edges(graph))
    for root in range(len(graph)):
        for left, right in itertools.combinations(sorted(graph[root]), 2):
            mandatory.add(pair(left, right))
    return mandatory


def support_model(
    graph: VertexGraph,
) -> tuple[
    list[tuple[int, int]],
    set[tuple[int, int]],
    list[tuple[int, int]],
    list[set[int]],
]:
    point_objects = edges(graph)
    mandatory = mandatory_edges(graph)
    line_graph: set[tuple[int, int]] = set()
    support_edges: list[tuple[int, int]] = []
    for left in range(len(point_objects)):
        for right in range(left + 1, len(point_objects)):
            first = set(point_objects[left])
            second = set(point_objects[right])
            if first & second:
                line_graph.add((left, right))
            elif all(pair(u, v) not in mandatory for u in first for v in second):
                support_edges.append((left, right))
    incidence = [set() for _ in point_objects]
    for edge_index, (left, right) in enumerate(support_edges):
        incidence[left].add(edge_index)
        incidence[right].add(edge_index)
    return point_objects, line_graph, support_edges, incidence


def active_adjacency(
    line_graph: set[tuple[int, int]],
    support_edges: list[tuple[int, int]],
    selected: set[int],
) -> set[tuple[int, int]]:
    return line_graph | {support_edges[index] for index in selected}


def first_cap_violation(
    vertex_count: int,
    adjacency: set[tuple[int, int]],
) -> dict[str, Any] | None:
    neighbourhoods = [set() for _ in range(vertex_count)]
    for left, right in adjacency:
        neighbourhoods[left].add(right)
        neighbourhoods[right].add(left)
    for left in range(vertex_count):
        for right in range(left + 1, vertex_count):
            common = sorted(neighbourhoods[left] & neighbourhoods[right])
            adjacent = (left, right) in adjacency
            limit = 1 if adjacent else 2
            if len(common) > limit:
                return {
                    "pair": [left, right],
                    "adjacent": adjacent,
                    "common": common,
                    "limit": limit,
                }
    return None


def first_adjacent_cap_violation(
    vertex_count: int,
    adjacency: set[tuple[int, int]],
) -> dict[str, Any] | None:
    neighbourhoods = [set() for _ in range(vertex_count)]
    for left, right in adjacency:
        neighbourhoods[left].add(right)
        neighbourhoods[right].add(left)
    for left, right in sorted(adjacency):
        common = sorted(neighbourhoods[left] & neighbourhoods[right])
        if len(common) > 1:
            return {
                "pair": [left, right],
                "adjacent": True,
                "common": common,
                "limit": 1,
            }
    return None


def selected_cycles(
    vertex_count: int,
    support_edges: list[tuple[int, int]],
    selected: set[int],
) -> list[list[int]]:
    adjacency = [[] for _ in range(vertex_count)]
    for index in selected:
        left, right = support_edges[index]
        adjacency[left].append(right)
        adjacency[right].append(left)
    if any(len(neighbours) != 2 for neighbours in adjacency):
        raise AssertionError("mu-attack witness is not a 2-factor")
    seen = set()
    answer = []
    for start in range(vertex_count):
        if start in seen:
            continue
        cycle = [start]
        previous = -1
        current = start
        while True:
            seen.add(current)
            following = next(
                vertex for vertex in sorted(adjacency[current]) if vertex != previous
            )
            if following == start:
                break
            cycle.append(following)
            previous, current = current, following
        answer.append(cycle)
    return answer


def replay_tree(
    tree: dict[str, Any],
    line_graph: set[tuple[int, int]],
    support_edges: list[tuple[int, int]],
    incidence: list[set[int]],
) -> dict[str, int]:
    statistics = {
        "nodes": 0,
        "branches": 0,
        "forced_in": 0,
        "forced_out_cap": 0,
        "forced_out_degree": 0,
        "leaves_cap": 0,
        "leaves_degree": 0,
        "survivors": 0,
    }
    universe = set(range(len(support_edges)))

    def degree(vertex: int, selected: set[int]) -> int:
        return len(incidence[vertex] & selected)

    def walk(node: dict[str, Any], selected: set[int], excluded: set[int]) -> None:
        statistics["nodes"] += 1
        if selected & excluded:
            raise AssertionError("proof state selects and excludes one support")

        for move in node.get("forced", []):
            edge_index = move["edge"]
            value = move["value"]
            rule = move["rule"]
            if edge_index in selected or edge_index in excluded:
                raise AssertionError("forced move does not target an undecided support")
            if not 0 <= edge_index < len(support_edges):
                raise AssertionError("forced support index out of range")

            if rule == "degree_saturated":
                vertex = move["vertex"]
                if edge_index not in incidence[vertex] or degree(vertex, selected) != 2:
                    raise AssertionError("invalid degree-saturated forcing")
                if value != 0:
                    raise AssertionError("degree-saturated move must exclude")
                excluded.add(edge_index)
                statistics["forced_out_degree"] += 1
            elif rule == "degree_needed":
                vertex = move["vertex"]
                undecided_at_vertex = incidence[vertex] - selected - excluded
                if (
                    edge_index not in undecided_at_vertex
                    or degree(vertex, selected) + len(undecided_at_vertex) != 2
                ):
                    raise AssertionError("invalid degree-needed forcing")
                if value != 1:
                    raise AssertionError("degree-needed move must select")
                selected.add(edge_index)
                statistics["forced_in"] += 1
            elif rule == "cap_if_in":
                if value != 0:
                    raise AssertionError("cap-if-in move must exclude")
                trial = active_adjacency(
                    line_graph, support_edges, selected | {edge_index}
                )
                if first_cap_violation(len(incidence), trial) is None:
                    raise AssertionError("cap-if-in exclusion has no cap witness")
                excluded.add(edge_index)
                statistics["forced_out_cap"] += 1
            else:
                raise AssertionError(f"unknown forcing rule {rule}")

        if "leaf" in node:
            leaf = node["leaf"]
            kind = leaf["kind"]
            if kind == "degree_overflow":
                vertex = leaf["vertex"]
                if degree(vertex, selected) <= 2:
                    raise AssertionError("false degree-overflow leaf")
                statistics["leaves_degree"] += 1
            elif kind == "degree_shortage":
                vertex = leaf["vertex"]
                undecided = incidence[vertex] - selected - excluded
                if degree(vertex, selected) + len(undecided) >= 2:
                    raise AssertionError("false degree-shortage leaf")
                statistics["leaves_degree"] += 1
            elif kind == "common_neighbour_cap":
                violation = first_cap_violation(
                    len(incidence),
                    active_adjacency(line_graph, support_edges, selected),
                )
                if violation is None:
                    raise AssertionError("false common-neighbour-cap leaf")
                stated = {
                    "pair": leaf["pair"],
                    "adjacent": leaf["adjacent"],
                    "common": leaf["common"],
                    "limit": leaf["limit"],
                }
                if stated != violation:
                    raise AssertionError("cap leaf witness does not match recomputation")
                statistics["leaves_cap"] += 1
            elif kind == "survivor":
                if any(degree(vertex, selected) != 2 for vertex in range(len(incidence))):
                    raise AssertionError("reported survivor is not 2-regular")
                if first_cap_violation(
                    len(incidence),
                    active_adjacency(line_graph, support_edges, selected),
                ):
                    raise AssertionError("reported survivor violates a cap")
                if sorted(selected) != leaf["selected"]:
                    raise AssertionError("survivor selected set mismatch")
                statistics["survivors"] += 1
            else:
                raise AssertionError(f"unknown leaf kind {kind}")
            return

        edge_index = node["branch_edge"]
        if edge_index not in universe - selected - excluded:
            raise AssertionError("branch support is not undecided")
        statistics["branches"] += 1
        walk(
            node["include"],
            selected | {edge_index},
            set(excluded),
        )
        walk(
            node["exclude"],
            set(selected),
            excluded | {edge_index},
        )

    walk(tree, set(), set())
    return statistics


def mutate_first(
    tree: dict[str, Any],
    predicate: Any,
    mutation: Any,
) -> bool:
    for move in tree.get("forced", []):
        if predicate("forced", move):
            mutation("forced", move)
            return True
    if "leaf" in tree and predicate("leaf", tree["leaf"]):
        mutation("leaf", tree["leaf"])
        return True
    for key in ("include", "exclude"):
        if key in tree and mutate_first(tree[key], predicate, mutation):
            return True
    return False


def mutation_checks(
    tree: dict[str, Any],
    line_graph: set[tuple[int, int]],
    support_edges: list[tuple[int, int]],
    incidence: list[set[int]],
) -> int:
    variants: list[dict[str, Any]] = []

    bad_branch = copy.deepcopy(tree)
    bad_branch["branch_edge"] = len(support_edges)
    variants.append(bad_branch)

    bad_cap_force = copy.deepcopy(tree)
    if not mutate_first(
        bad_cap_force,
        lambda kind, item: kind == "forced" and item["rule"] == "cap_if_in",
        lambda _kind, item: item.__setitem__("value", 1),
    ):
        raise AssertionError("mutation fixture has no cap-if-in forcing")
    variants.append(bad_cap_force)

    bad_degree_force = copy.deepcopy(tree)
    if not mutate_first(
        bad_degree_force,
        lambda kind, item: kind == "forced" and item["rule"] == "degree_needed",
        lambda _kind, item: item.__setitem__("value", 0),
    ):
        raise AssertionError("mutation fixture has no degree-needed forcing")
    variants.append(bad_degree_force)

    bad_leaf_witness = copy.deepcopy(tree)
    if not mutate_first(
        bad_leaf_witness,
        lambda kind, item: kind == "leaf"
        and item["kind"] == "common_neighbour_cap",
        lambda _kind, item: item.__setitem__("common", []),
    ):
        raise AssertionError("mutation fixture has no cap leaf")
    variants.append(bad_leaf_witness)

    false_survivor = copy.deepcopy(tree)

    def turn_into_false_survivor(_kind: str, item: dict[str, Any]) -> None:
        item.clear()
        item.update({"kind": "survivor", "selected": []})

    if not mutate_first(
        false_survivor,
        lambda kind, item: kind == "leaf"
        and item["kind"] == "common_neighbour_cap",
        turn_into_false_survivor,
    ):
        raise AssertionError("mutation fixture has no replaceable leaf")
    variants.append(false_survivor)

    rejected = 0
    for variant in variants:
        try:
            replay_tree(variant, line_graph, support_edges, incidence)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("mutated proof tree was incorrectly accepted")
    return rejected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--scd", type=Path, required=True)
    parser.add_argument("--graph6", type=Path, required=True)
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()

    if file_hash(args.scd) != EXPECTED_SCD_SHA256:
        raise AssertionError("official shortcode SHA-256 mismatch")
    if file_hash(args.graph6) != EXPECTED_GRAPH6_SHA256:
        raise AssertionError("repository graph6 SHA-256 mismatch")

    certificate = json.loads(args.certificate.read_text(encoding="utf-8"))
    if certificate["schema"] != "conway99-n3-42-support-proof-v1":
        raise AssertionError("certificate schema mismatch")
    catalog = certificate["catalog"]
    if (
        catalog["scd_sha256"] != EXPECTED_SCD_SHA256
        or catalog["graph6_sha256"] != EXPECTED_GRAPH6_SHA256
    ):
        raise AssertionError("certificate source hashes mismatch")

    shortcode_graphs = decode_shortcode_archive(args.scd.read_bytes())
    graph6_records = [
        line.strip()
        for line in args.graph6.read_text(encoding="ascii").splitlines()
        if line.strip()
    ]
    graph6_graphs = [decode_graph6(record) for record in graph6_records]
    if len(shortcode_graphs) != 110 or len(graph6_graphs) != 112:
        raise AssertionError("catalog record counts mismatch")

    connected = {
        index
        for index, graph in enumerate(graph6_graphs)
        if len(component_sets(graph)) == 1
    }
    mapping = catalog["official_to_graph6_index"]
    if len(mapping) != 110 or set(mapping) != connected:
        raise AssertionError("crossmatch indices do not cover connected catalog")
    for ordinal, graph6_index in enumerate(mapping):
        if not isomorphic(shortcode_graphs[ordinal], graph6_graphs[graph6_index]):
            raise AssertionError(
                f"claimed shortcode/graph6 match fails at official record {ordinal}"
            )

    disconnected = sorted(set(range(112)) - connected)
    if len(disconnected) != 2:
        raise AssertionError("expected exactly two disconnected records")
    disconnected_rows = {
        row["graph6_index"]: row for row in catalog["disconnected"]
    }
    if set(disconnected_rows) != set(disconnected):
        raise AssertionError("disconnected certificate indices mismatch")
    observed_types = set()
    for index in disconnected:
        parts = component_sets(graph6_graphs[index])
        if [len(part) for part in parts] != [6, 8]:
            raise AssertionError("disconnected component orders are not 6+8")
        order6, order8 = parts
        if not bipartite_on(graph6_graphs[index], order6):
            raise AssertionError("order-six component is not the certified K3,3")
        order8_type = "cube_Q3" if bipartite_on(graph6_graphs[index], order8) else "Wagner_M8"
        row = disconnected_rows[index]
        if (
            row["graph6"] != graph6_records[index]
            or row["order6_type"] != "K3,3"
            or row["order8_type"] != order8_type
        ):
            raise AssertionError("disconnected type certificate mismatch")
        observed_types.add(order8_type)
    if observed_types != {"cube_Q3", "Wagner_M8"}:
        raise AssertionError("disconnected order-eight types are incomplete")

    mandatory_histogram: Counter[int] = Counter()
    survivor_indices = []
    for index, graph in enumerate(graph6_graphs):
        mandatory = mandatory_edges(graph)
        maximum = max(
            sum(pair(vertex, other) in mandatory for other in range(14) if other != vertex)
            for vertex in range(14)
        )
        mandatory_histogram[maximum] += 1
        if maximum <= 7:
            survivor_indices.append(index)
    expected_histogram = {
        int(key): value
        for key, value in certificate["mandatory_max_degree_histogram"].items()
    }
    if mandatory_histogram != Counter(expected_histogram):
        raise AssertionError("mandatory-degree histogram mismatch")

    rows = certificate["mandatory_degree_survivors"]
    if [row["graph6_index"] for row in rows] != survivor_indices:
        raise AssertionError("mandatory-degree survivor list mismatch")

    total_survivors = 0
    models_by_index: dict[
        int,
        tuple[
            list[tuple[int, int]],
            set[tuple[int, int]],
            list[tuple[int, int]],
            list[set[int]],
        ],
    ] = {}
    for row in rows:
        index = row["graph6_index"]
        graph = graph6_graphs[index]
        point_objects, line_graph, support_edges, incidence = support_model(graph)
        models_by_index[index] = (
            point_objects,
            line_graph,
            support_edges,
            incidence,
        )
        mandatory = mandatory_edges(graph)
        mandatory_degrees = [
            sum(pair(vertex, other) in mandatory for other in range(14) if other != vertex)
            for vertex in range(14)
        ]
        if row["graph6"] != graph6_records[index]:
            raise AssertionError("survivor graph6 record mismatch")
        if row["f_edges"] != [list(edge) for edge in point_objects]:
            raise AssertionError("point-object edge list mismatch")
        if row["support_edges"] != [list(edge) for edge in support_edges]:
            raise AssertionError("support opportunity list mismatch")
        if row["support_count"] != len(support_edges):
            raise AssertionError("support opportunity count mismatch")
        if row["mandatory_k_edges"] != len(mandatory):
            raise AssertionError("mandatory K edge count mismatch")
        if row["mandatory_k_degrees"] != mandatory_degrees:
            raise AssertionError("mandatory K degree list mismatch")

        statistics = replay_tree(
            row["rejection_tree"], line_graph, support_edges, incidence
        )
        if statistics != row["search_statistics"]:
            raise AssertionError(
                f"proof-tree statistics mismatch for catalog index {index}"
            )
        total_survivors += statistics["survivors"]
        print(
            f"index={index} supports={len(support_edges)} "
            f"nodes={statistics['nodes']} leaves_cap={statistics['leaves_cap']} "
            f"survivors={statistics['survivors']} PASS"
        )

    attack = certificate["mu_cap_attack"]
    attack_index = attack["graph6_index"]
    if attack_index != 6 or attack_index not in models_by_index:
        raise AssertionError("mu-cap attack is not bound to survivor index 6")
    _, attack_line_graph, attack_support_edges, attack_incidence = models_by_index[
        attack_index
    ]
    attack_selected = set(attack["selected_support_indices"])
    if attack["selected_support_pairs"] != [
        list(attack_support_edges[index]) for index in sorted(attack_selected)
    ]:
        raise AssertionError("mu-cap attack support-pair list mismatch")
    if any(
        len(attack_incidence[vertex] & attack_selected) != 2
        for vertex in range(len(attack_incidence))
    ):
        raise AssertionError("mu-cap attack does not have support degree two")
    attack_adjacency = active_adjacency(
        attack_line_graph, attack_support_edges, attack_selected
    )
    if first_adjacent_cap_violation(len(attack_incidence), attack_adjacency):
        raise AssertionError("mu-cap attack violates lambda<=1")
    observed_mu_failure = first_cap_violation(
        len(attack_incidence), attack_adjacency
    )
    if observed_mu_failure != attack["first_mu_cap_violation"]:
        raise AssertionError("mu-cap attack witness mismatch")
    if (
        observed_mu_failure is None
        or observed_mu_failure["adjacent"]
        or len(observed_mu_failure["common"]) != 3
    ):
        raise AssertionError("mu-cap attack does not isolate universal mu<=2")
    if selected_cycles(
        len(attack_incidence), attack_support_edges, attack_selected
    ) != attack["cycles"]:
        raise AssertionError("mu-cap attack cycle decomposition mismatch")

    rejected_mutations = 0
    if args.mutations:
        mutation_row = next(row for row in rows if row["graph6_index"] == 0)
        _, mutation_line, mutation_supports, mutation_incidence = models_by_index[0]
        rejected_mutations = mutation_checks(
            mutation_row["rejection_tree"],
            mutation_line,
            mutation_supports,
            mutation_incidence,
        )

    if total_survivors != certificate["all_support_cap_survivors"]:
        raise AssertionError("total support-cap survivor count mismatch")
    if total_survivors:
        print(f"all_support_cap_survivors={total_survivors} CANDIDATE")
        print("target_result=UNKNOWN")
        return 2

    print("official_crossmatch=110_of_110 PASS")
    print("disconnected_classification=K3,3+Q3,K3,3+M8 PASS")
    print("mandatory_degree_survivors=4 PASS")
    print("support_cap_rejection_trees=4_of_4 PASS")
    print(
        "mu_cap_attack=index_6_lambda_only_3C7_PASS_"
        f"mu_witness_{observed_mu_failure['pair']}_with_3_common"
    )
    if args.mutations:
        print(f"mutation_checks={rejected_mutations}_of_5_rejected PASS")
    print("all_support_cap_survivors=0")
    print(f"certificate_sha256={file_hash(args.certificate)}")
    print("conditional_n3_42_all_size_two_branch=EXCLUDED")
    print("target_result=UNKNOWN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
