#!/usr/bin/env python3
"""Independent Wave 12 catalog and active-support verifier.

This program deliberately does not import the construction-lane code.  It
decodes Meringer's shortcode archive and the repository graph6 catalog from
their documented byte formats, matches them with a small in-file
isomorphism routine, and emits a proof tree for the remaining support-factor
search.

The finite search is a relaxation of the full Conway-99 problem.  It assumes
the already audited all-size-two n3=42 reduction and uses only:

* F is a simple cubic triangle-free graph on fourteen active labels;
* mandatory K edges are F edges and pairs of F-neighbours;
* a support joins disjoint F-edges whose 2-by-2 cross rectangle avoids the
  mandatory K edges;
* every F-edge object has exactly two supports; and
* line_graph(F) plus the supports respects the SRG common-neighbour caps.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, deque
from pathlib import Path
from typing import Iterable, Iterator


N_ACTIVE = 14
F_DEGREE = 3
F_EDGE_COUNT = N_ACTIVE * F_DEGREE // 2


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def edge_tuple(masks: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return tuple(
        (u, v)
        for u in range(len(masks))
        for v in range(u + 1, len(masks))
        if (masks[u] >> v) & 1
    )


def masks_from_edges(n: int, edges: Iterable[tuple[int, int]]) -> tuple[int, ...]:
    masks = [0] * n
    for u, v in edges:
        if not 0 <= u < v < n:
            raise ValueError(f"invalid edge {(u, v)} for order {n}")
        if (masks[u] >> v) & 1:
            raise ValueError(f"duplicate edge {(u, v)}")
        masks[u] |= 1 << v
        masks[v] |= 1 << u
    return tuple(masks)


def graph6_decode(record: str) -> tuple[int, ...]:
    """Decode the small-order graph6 form without a graph library."""

    raw = record.strip().encode("ascii")
    if not raw:
        raise ValueError("empty graph6 record")
    if raw[0] == 126:
        raise ValueError("only the one-byte graph6 order form is expected")
    n = raw[0] - 63
    if not 0 <= n <= 62:
        raise ValueError("invalid graph6 order byte")

    bits: list[int] = []
    for byte in raw[1:]:
        value = byte - 63
        if not 0 <= value < 64:
            raise ValueError("invalid graph6 data byte")
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))

    required = n * (n - 1) // 2
    if len(bits) < required or any(bits[required:]):
        raise ValueError("invalid graph6 length or nonzero padding")

    edges: list[tuple[int, int]] = []
    cursor = 0
    for high in range(1, n):
        for low in range(high):
            if bits[cursor]:
                edges.append((low, high))
            cursor += 1
    return masks_from_edges(n, edges)


def shortcode_records(data: bytes, n: int, degree: int) -> Iterator[list[int]]:
    """Expand GENREG prefix-compressed shortcode records."""

    code_length = n * degree // 2
    cursor = 0
    previous: list[int] = []
    ordinal = 0
    while cursor < len(data):
        common = data[cursor]
        cursor += 1
        if common > code_length:
            raise ValueError(f"record {ordinal}: prefix {common} exceeds code length")
        if ordinal == 0 and common != 0:
            raise ValueError("first shortcode prefix is not zero")
        if ordinal and common > len(previous):
            raise ValueError(f"record {ordinal}: prefix exceeds previous record")
        suffix_length = code_length - common
        if cursor + suffix_length > len(data):
            raise ValueError(f"record {ordinal}: truncated suffix")
        code = previous[:common] + list(data[cursor : cursor + suffix_length])
        cursor += suffix_length
        if len(code) != code_length:
            raise AssertionError("internal shortcode length error")
        yield code
        previous = code
        ordinal += 1

    if cursor != len(data):
        raise ValueError("trailing shortcode bytes")


def shortcode_decode(code: list[int], n: int, degree: int) -> tuple[int, ...]:
    """Recover lower endpoints from regularity and the documented ordering."""

    degrees = [0] * n
    masks = [0] * n
    cursor = 0
    for lower in range(n):
        needed = degree - degrees[lower]
        if needed < 0:
            raise ValueError("shortcode overfills a vertex")
        last_upper = lower
        for _ in range(needed):
            if cursor >= len(code):
                raise ValueError("shortcode ends before all degrees are filled")
            upper = code[cursor] - 1
            cursor += 1
            if not lower < upper < n:
                raise ValueError(f"invalid shortcode endpoint {upper + 1}")
            if upper <= last_upper:
                raise ValueError("shortcode neighbours are not strictly increasing")
            if degrees[upper] >= degree:
                raise ValueError("shortcode overfills an upper endpoint")
            masks[lower] |= 1 << upper
            masks[upper] |= 1 << lower
            degrees[lower] += 1
            degrees[upper] += 1
            last_upper = upper
    if cursor != len(code) or any(value != degree for value in degrees):
        raise ValueError("shortcode does not decode to the promised regular graph")
    return tuple(masks)


def components(graph: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    unseen = set(range(len(graph)))
    result: list[tuple[int, ...]] = []
    while unseen:
        root = min(unseen)
        queue = deque([root])
        unseen.remove(root)
        component: list[int] = []
        while queue:
            vertex = queue.popleft()
            component.append(vertex)
            neighbours = [u for u in range(len(graph)) if (graph[vertex] >> u) & 1]
            for neighbour in neighbours:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    queue.append(neighbour)
        result.append(tuple(sorted(component)))
    return tuple(sorted(result, key=lambda part: (len(part), part)))


def induced(graph: tuple[int, ...], vertices: tuple[int, ...]) -> tuple[int, ...]:
    position = {old: new for new, old in enumerate(vertices)}
    edges = []
    for old_u in vertices:
        for old_v in vertices:
            if old_u < old_v and (graph[old_u] >> old_v) & 1:
                edges.append((position[old_u], position[old_v]))
    return masks_from_edges(len(vertices), edges)


def is_bipartite(graph: tuple[int, ...]) -> bool:
    colour: list[int | None] = [None] * len(graph)
    for root in range(len(graph)):
        if colour[root] is not None:
            continue
        colour[root] = 0
        queue = deque([root])
        while queue:
            vertex = queue.popleft()
            for neighbour in range(len(graph)):
                if not (graph[vertex] >> neighbour) & 1:
                    continue
                if colour[neighbour] is None:
                    colour[neighbour] = 1 - colour[vertex]  # type: ignore[operator]
                    queue.append(neighbour)
                elif colour[neighbour] == colour[vertex]:
                    return False
    return True


def has_triangle(graph: tuple[int, ...]) -> bool:
    for u in range(len(graph)):
        for v in range(u + 1, len(graph)):
            if (graph[u] >> v) & 1 and (graph[u] & graph[v]):
                return True
    return False


def distance_profile(graph: tuple[int, ...], root: int) -> tuple[int, ...]:
    distance = [-1] * len(graph)
    distance[root] = 0
    queue = deque([root])
    while queue:
        vertex = queue.popleft()
        for neighbour in range(len(graph)):
            if (graph[vertex] >> neighbour) & 1 and distance[neighbour] < 0:
                distance[neighbour] = distance[vertex] + 1
                queue.append(neighbour)
    counts = Counter(distance)
    return tuple(counts[level] for level in range(-1, max(distance) + 1))


def joint_colours(
    left: tuple[int, ...], right: tuple[int, ...]
) -> tuple[list[int], list[int]] | None:
    """Joint one-dimensional refinement, used only as an isomorphism filter."""

    raw_left = [
        (left[v].bit_count(), distance_profile(left, v)) for v in range(len(left))
    ]
    raw_right = [
        (right[v].bit_count(), distance_profile(right, v)) for v in range(len(right))
    ]

    def rank(
        values_left: list[object], values_right: list[object]
    ) -> tuple[list[int], list[int]]:
        palette = {value: i for i, value in enumerate(sorted(set(values_left + values_right)))}
        return (
            [palette[value] for value in values_left],
            [palette[value] for value in values_right],
        )

    colours_left, colours_right = rank(raw_left, raw_right)
    while True:
        next_left = [
            (
                colours_left[v],
                tuple(
                    sorted(
                        colours_left[u]
                        for u in range(len(left))
                        if (left[v] >> u) & 1
                    )
                ),
            )
            for v in range(len(left))
        ]
        next_right = [
            (
                colours_right[v],
                tuple(
                    sorted(
                        colours_right[u]
                        for u in range(len(right))
                        if (right[v] >> u) & 1
                    )
                ),
            )
            for v in range(len(right))
        ]
        new_left, new_right = rank(next_left, next_right)
        if Counter(new_left) != Counter(new_right):
            return None
        if new_left == colours_left and new_right == colours_right:
            return new_left, new_right
        colours_left, colours_right = new_left, new_right


def isomorphic(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    """Small exact backtracker independent of nauty and NetworkX."""

    if len(left) != len(right):
        return False
    if len(edge_tuple(left)) != len(edge_tuple(right)):
        return False
    refined = joint_colours(left, right)
    if refined is None:
        return False
    colours_left, colours_right = refined
    n = len(left)
    mapping = [-1] * n
    reverse = [-1] * n

    def candidates(source: int) -> list[int]:
        result = []
        for target in range(n):
            if reverse[target] >= 0 or colours_left[source] != colours_right[target]:
                continue
            consistent = True
            for other_source, other_target in enumerate(mapping):
                if other_target < 0:
                    continue
                if ((left[source] >> other_source) & 1) != (
                    (right[target] >> other_target) & 1
                ):
                    consistent = False
                    break
            if consistent:
                result.append(target)
        return result

    def search(assigned: int) -> bool:
        if assigned == n:
            return True
        choices: list[tuple[int, int, int, list[int]]] = []
        for source in range(n):
            if mapping[source] >= 0:
                continue
            options = candidates(source)
            if not options:
                return False
            mapped_neighbours = sum(
                1
                for other in range(n)
                if mapping[other] >= 0 and (left[source] >> other) & 1
            )
            choices.append((len(options), -mapped_neighbours, source, options))
        _, _, source, options = min(choices)
        for target in options:
            mapping[source] = target
            reverse[target] = source
            if search(assigned + 1):
                return True
            mapping[source] = -1
            reverse[target] = -1
        return False

    return search(0)


def enumerate_small_cubic_triangle_free(n: int) -> tuple[int, list[tuple[int, ...]]]:
    """Enumerate labeled graphs, then quotient with the local isomorphism test."""

    masks = [0] * n
    degrees = [0] * n
    labeled_count = 0
    representatives: list[tuple[int, ...]] = []

    def recurse() -> None:
        nonlocal labeled_count
        try:
            lower = next(vertex for vertex in range(n) if degrees[vertex] < 3)
        except StopIteration:
            graph = tuple(masks)
            if len(components(graph)) != 1 or has_triangle(graph):
                return
            labeled_count += 1
            if not any(isomorphic(graph, rep) for rep in representatives):
                representatives.append(graph)
            return

        need = 3 - degrees[lower]
        eligible = [
            upper
            for upper in range(lower + 1, n)
            if degrees[upper] < 3
            and not ((masks[lower] >> upper) & 1)
            and not (masks[lower] & masks[upper])
        ]
        if len(eligible) < need:
            return
        for chosen in itertools.combinations(eligible, need):
            for upper in chosen:
                masks[lower] |= 1 << upper
                masks[upper] |= 1 << lower
                degrees[lower] += 1
                degrees[upper] += 1
            recurse()
            for upper in chosen:
                masks[lower] &= ~(1 << upper)
                masks[upper] &= ~(1 << lower)
                degrees[lower] -= 1
                degrees[upper] -= 1

    recurse()
    return labeled_count, representatives


def disjoint_union(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    shift = len(left)
    edges = list(edge_tuple(left))
    edges.extend((u + shift, v + shift) for u, v in edge_tuple(right))
    return masks_from_edges(len(left) + len(right), edges)


def catalog_audit(scd_path: Path, graph6_path: Path) -> dict[str, object]:
    scd_codes = list(shortcode_records(scd_path.read_bytes(), N_ACTIVE, F_DEGREE))
    scd_graphs = [
        shortcode_decode(code, N_ACTIVE, F_DEGREE) for code in scd_codes
    ]
    if len(scd_graphs) != 110:
        raise AssertionError(f"official archive decoded to {len(scd_graphs)}, not 110")
    for graph in scd_graphs:
        if len(components(graph)) != 1 or has_triangle(graph):
            raise AssertionError("official archive record violates connected/girth premise")

    graph6_records = [
        line.strip()
        for line in graph6_path.read_text(encoding="ascii").splitlines()
        if line.strip()
    ]
    graph6_graphs = [graph6_decode(record) for record in graph6_records]
    if len(graph6_graphs) != 112 or len(set(graph6_records)) != 112:
        raise AssertionError("repository catalog does not have 112 distinct records")
    for graph in graph6_graphs:
        if (
            len(graph) != N_ACTIVE
            or any(mask.bit_count() != F_DEGREE for mask in graph)
            or has_triangle(graph)
        ):
            raise AssertionError("repository catalog record violates cubic/girth premise")

    connected_indices = [
        index for index, graph in enumerate(graph6_graphs) if len(components(graph)) == 1
    ]
    disconnected_indices = [
        index for index, graph in enumerate(graph6_graphs) if len(components(graph)) > 1
    ]
    if len(connected_indices) != 110 or len(disconnected_indices) != 2:
        raise AssertionError("repository connected/disconnected split is not 110+2")

    crossmatch: list[int] = []
    for ordinal, source in enumerate(scd_graphs):
        matches = [
            index
            for index in connected_indices
            if isomorphic(source, graph6_graphs[index])
        ]
        if len(matches) != 1:
            raise AssertionError(
                f"official record {ordinal} has {len(matches)} repository matches"
            )
        crossmatch.append(matches[0])
    if len(set(crossmatch)) != 110 or set(crossmatch) != set(connected_indices):
        raise AssertionError("official/repository crossmatch is not a bijection")

    labeled6, reps6 = enumerate_small_cubic_triangle_free(6)
    labeled8, reps8 = enumerate_small_cubic_triangle_free(8)
    if len(reps6) != 1 or len(reps8) != 2:
        raise AssertionError(
            f"small independent census produced {len(reps6)} and {len(reps8)} types"
        )
    if not is_bipartite(reps6[0]):
        raise AssertionError("order-six representative is not K3,3")

    disconnected_models = [disjoint_union(reps6[0], graph) for graph in reps8]
    small_matches: list[int] = []
    disconnected_rows: list[dict[str, object]] = []
    for model in disconnected_models:
        matches = [
            index
            for index in disconnected_indices
            if isomorphic(model, graph6_graphs[index])
        ]
        if len(matches) != 1:
            raise AssertionError("independent disconnected model match is not unique")
        index = matches[0]
        small_matches.append(index)
        parts = components(graph6_graphs[index])
        if tuple(map(len, parts)) != (6, 8):
            raise AssertionError("disconnected record does not have component orders 6+8")
        component8 = induced(graph6_graphs[index], parts[1])
        disconnected_rows.append(
            {
                "graph6_index": index,
                "graph6": graph6_records[index],
                "component_orders": [6, 8],
                "order6_type": "K3,3",
                "order8_type": "cube_Q3"
                if is_bipartite(component8)
                else "Wagner_M8",
            }
        )
    if set(small_matches) != set(disconnected_indices):
        raise AssertionError("independent disconnected census is not a bijection")

    return {
        "scd_sha256": sha256(scd_path),
        "scd_bytes": scd_path.stat().st_size,
        "scd_records": len(scd_graphs),
        "graph6_sha256": sha256(graph6_path),
        "graph6_records": len(graph6_graphs),
        "connected_graph6_records": len(connected_indices),
        "official_to_graph6_index": crossmatch,
        "small_labeled_counts": {"order6": labeled6, "order8": labeled8},
        "small_unlabeled_counts": {"order6": len(reps6), "order8": len(reps8)},
        "disconnected": sorted(
            disconnected_rows, key=lambda row: int(row["graph6_index"])
        ),
        "_graph6_records": graph6_records,
        "_graph6_graphs": graph6_graphs,
    }


def mandatory_k(graph: tuple[int, ...]) -> tuple[int, ...]:
    mandatory = list(graph)
    for root in range(len(graph)):
        neighbours = [u for u in range(len(graph)) if (graph[root] >> u) & 1]
        for u, v in itertools.combinations(neighbours, 2):
            mandatory[u] |= 1 << v
            mandatory[v] |= 1 << u
    return tuple(mandatory)


def cap_violation(
    base: tuple[int, ...],
    support_edges: tuple[tuple[int, int], ...],
    selected: int,
) -> dict[str, object] | None:
    active = list(base)
    for edge_index, (u, v) in enumerate(support_edges):
        if (selected >> edge_index) & 1:
            active[u] |= 1 << v
            active[v] |= 1 << u
    for u in range(len(active)):
        for v in range(u + 1, len(active)):
            common_mask = active[u] & active[v]
            common_count = common_mask.bit_count()
            adjacent = bool((active[u] >> v) & 1)
            limit = 1 if adjacent else 2
            if common_count > limit:
                return {
                    "pair": [u, v],
                    "adjacent": adjacent,
                    "common": [
                        w for w in range(len(active)) if (common_mask >> w) & 1
                    ],
                    "limit": limit,
                }
    return None


def adjacent_cap_violation(
    base: tuple[int, ...],
    support_edges: tuple[tuple[int, int], ...],
    selected: int,
) -> dict[str, object] | None:
    """Return only lambda-cap failures, deliberately omitting the mu cap."""

    active = list(base)
    for edge_index, (u, v) in enumerate(support_edges):
        if (selected >> edge_index) & 1:
            active[u] |= 1 << v
            active[v] |= 1 << u
    for u in range(len(active)):
        for v in range(u + 1, len(active)):
            if not ((active[u] >> v) & 1):
                continue
            common_mask = active[u] & active[v]
            if common_mask.bit_count() > 1:
                return {
                    "pair": [u, v],
                    "adjacent": True,
                    "common": [
                        w for w in range(len(active)) if (common_mask >> w) & 1
                    ],
                    "limit": 1,
                }
    return None


def find_lambda_only_factor(problem: dict[str, object]) -> tuple[int, int]:
    """Find one 2-factor obeying lambda<=1, if one exists.

    This is an adversarial strictness check, not part of the rejection proof.
    The full proof tree is checked separately.
    """

    base = problem["base"]
    supports = problem["supports"]
    incident = problem["incident"]
    assert isinstance(base, tuple)
    assert isinstance(supports, tuple)
    assert isinstance(incident, tuple)
    all_edges = (1 << len(supports)) - 1
    nodes = 0

    def recurse(selected: int, excluded: int) -> int | None:
        nonlocal nodes
        nodes += 1
        while True:
            degree = [(selected & mask).bit_count() for mask in incident]
            undecided = all_edges & ~(selected | excluded)
            if any(value > 2 for value in degree):
                return None
            if adjacent_cap_violation(base, supports, selected) is not None:
                return None
            if any(
                degree[v] + (incident[v] & undecided).bit_count() < 2
                for v in range(len(incident))
            ):
                return None

            move: tuple[int, int] | None = None
            for vertex, value in enumerate(degree):
                available = incident[vertex] & undecided
                if value == 2 and available:
                    move = (available & -available, 0)
                    break
            if move is None:
                for vertex, value in enumerate(degree):
                    available = incident[vertex] & undecided
                    if available and value + available.bit_count() == 2:
                        move = (available & -available, 1)
                        break
            if move is None:
                remaining = undecided
                while remaining:
                    bit = remaining & -remaining
                    if adjacent_cap_violation(base, supports, selected | bit):
                        move = (bit, 0)
                        break
                    remaining ^= bit
            if move is None:
                break
            bit, value = move
            if value:
                selected |= bit
            else:
                excluded |= bit

        if all(value == 2 for value in degree):
            return selected
        choices = [
            ((incident[v] & undecided).bit_count(), v, incident[v] & undecided)
            for v, value in enumerate(degree)
            if value < 2 and (incident[v] & undecided)
        ]
        _, _, available = min(choices)
        bit = available & -available
        return recurse(selected | bit, excluded) or recurse(selected, excluded | bit)

    answer = recurse(0, 0)
    if answer is None:
        raise AssertionError("expected catalog index 6 lambda-only diagnostic factor")
    return answer, nodes


def factor_cycles(
    vertex_count: int,
    supports: tuple[tuple[int, int], ...],
    selected: int,
) -> list[list[int]]:
    adjacency = [[] for _ in range(vertex_count)]
    for index, (u, v) in enumerate(supports):
        if (selected >> index) & 1:
            adjacency[u].append(v)
            adjacency[v].append(u)
    if any(len(neighbours) != 2 for neighbours in adjacency):
        raise AssertionError("selected support is not a 2-factor")
    seen: set[int] = set()
    cycles: list[list[int]] = []
    for start in range(vertex_count):
        if start in seen:
            continue
        cycle = [start]
        previous = -1
        current = start
        while True:
            seen.add(current)
            following = next(v for v in sorted(adjacency[current]) if v != previous)
            if following == start:
                break
            cycle.append(following)
            previous, current = current, following
        cycles.append(cycle)
    return cycles


def support_problem(graph: tuple[int, ...]) -> dict[str, object]:
    f_edges = edge_tuple(graph)
    if len(f_edges) != F_EDGE_COUNT:
        raise AssertionError("F edge count mismatch")
    mandatory = mandatory_k(graph)
    base_edges = [
        (i, j)
        for i, first in enumerate(f_edges)
        for j, second in enumerate(f_edges[i + 1 :], i + 1)
        if set(first) & set(second)
    ]
    base = masks_from_edges(len(f_edges), base_edges)
    supports: list[tuple[int, int]] = []
    for i, first in enumerate(f_edges):
        for j, second in enumerate(f_edges[i + 1 :], i + 1):
            if set(first) & set(second):
                continue
            if all(
                not ((mandatory[u] >> v) & 1) for u in first for v in second
            ):
                supports.append((i, j))
    incident = [0] * len(f_edges)
    for index, (u, v) in enumerate(supports):
        incident[u] |= 1 << index
        incident[v] |= 1 << index
    return {
        "f_edges": f_edges,
        "mandatory": mandatory,
        "base": base,
        "supports": tuple(supports),
        "incident": tuple(incident),
    }


def build_rejection_tree(problem: dict[str, object]) -> tuple[dict[str, object], dict[str, int]]:
    base = problem["base"]
    supports = problem["supports"]
    incident = problem["incident"]
    assert isinstance(base, tuple)
    assert isinstance(supports, tuple)
    assert isinstance(incident, tuple)
    support_count = len(supports)
    all_edges = (1 << support_count) - 1
    statistics = {
        "nodes": 0,
        "branches": 0,
        "forced_in": 0,
        "forced_out_degree": 0,
        "forced_out_cap": 0,
        "leaves_degree": 0,
        "leaves_cap": 0,
        "survivors": 0,
    }

    def degrees(selected: int) -> list[int]:
        return [(selected & mask).bit_count() for mask in incident]

    def recurse(selected: int, excluded: int) -> dict[str, object]:
        statistics["nodes"] += 1
        forced: list[dict[str, object]] = []
        while True:
            degree = degrees(selected)
            undecided = all_edges & ~(selected | excluded)

            overflow = next((v for v, value in enumerate(degree) if value > 2), None)
            if overflow is not None:
                statistics["leaves_degree"] += 1
                return {
                    "forced": forced,
                    "leaf": {"kind": "degree_overflow", "vertex": overflow},
                }
            shortage = next(
                (
                    v
                    for v, value in enumerate(degree)
                    if value + (incident[v] & undecided).bit_count() < 2
                ),
                None,
            )
            if shortage is not None:
                statistics["leaves_degree"] += 1
                return {
                    "forced": forced,
                    "leaf": {"kind": "degree_shortage", "vertex": shortage},
                }
            violation = cap_violation(base, supports, selected)
            if violation is not None:
                statistics["leaves_cap"] += 1
                return {
                    "forced": forced,
                    "leaf": {"kind": "common_neighbour_cap", **violation},
                }

            forced_move: tuple[int, int, str, int | None] | None = None
            for vertex, value in enumerate(degree):
                available = incident[vertex] & undecided
                if value == 2 and available:
                    edge_index = (available & -available).bit_length() - 1
                    forced_move = (edge_index, 0, "degree_saturated", vertex)
                    break
            if forced_move is None:
                for vertex, value in enumerate(degree):
                    available = incident[vertex] & undecided
                    if available and value + available.bit_count() == 2:
                        edge_index = (available & -available).bit_length() - 1
                        forced_move = (edge_index, 1, "degree_needed", vertex)
                        break
            if forced_move is None:
                bit = undecided
                while bit:
                    edge_bit = bit & -bit
                    edge_index = edge_bit.bit_length() - 1
                    witness = cap_violation(base, supports, selected | edge_bit)
                    if witness is not None:
                        forced_move = (edge_index, 0, "cap_if_in", None)
                        break
                    bit ^= edge_bit

            if forced_move is None:
                break
            edge_index, value, rule, vertex = forced_move
            entry: dict[str, object] = {
                "edge": edge_index,
                "value": value,
                "rule": rule,
            }
            if vertex is not None:
                entry["vertex"] = vertex
            forced.append(entry)
            if value:
                selected |= 1 << edge_index
                statistics["forced_in"] += 1
            else:
                excluded |= 1 << edge_index
                if rule == "cap_if_in":
                    statistics["forced_out_cap"] += 1
                else:
                    statistics["forced_out_degree"] += 1

        degree = degrees(selected)
        if all(value == 2 for value in degree):
            statistics["survivors"] += 1
            return {
                "forced": forced,
                "leaf": {
                    "kind": "survivor",
                    "selected": [
                        index
                        for index in range(support_count)
                        if (selected >> index) & 1
                    ],
                },
            }

        undecided = all_edges & ~(selected | excluded)
        choices = []
        for vertex, value in enumerate(degree):
            if value >= 2:
                continue
            available = incident[vertex] & undecided
            if available:
                choices.append((available.bit_count(), -(2 - value), vertex, available))
        if not choices:
            raise AssertionError("incomplete state has no branch candidate")
        _, _, _, available = min(choices)
        edge_index = (available & -available).bit_length() - 1
        statistics["branches"] += 1
        return {
            "forced": forced,
            "branch_edge": edge_index,
            "include": recurse(selected | (1 << edge_index), excluded),
            "exclude": recurse(selected, excluded | (1 << edge_index)),
        }

    return recurse(0, 0), statistics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scd", type=Path, required=True)
    parser.add_argument("--graph6", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    catalog = catalog_audit(args.scd, args.graph6)
    graph6_records = catalog.pop("_graph6_records")
    graph6_graphs = catalog.pop("_graph6_graphs")
    assert isinstance(graph6_records, list)
    assert isinstance(graph6_graphs, list)

    degree_histogram: Counter[int] = Counter()
    survivors: list[dict[str, object]] = []
    for index, graph in enumerate(graph6_graphs):
        mandatory = mandatory_k(graph)
        maximum = max(mask.bit_count() for mask in mandatory)
        degree_histogram[maximum] += 1
        if maximum > 7:
            continue
        problem = support_problem(graph)
        tree, statistics = build_rejection_tree(problem)
        supports = problem["supports"]
        mandatory = problem["mandatory"]
        f_edges = problem["f_edges"]
        assert isinstance(supports, tuple)
        assert isinstance(mandatory, tuple)
        assert isinstance(f_edges, tuple)
        survivors.append(
            {
                "graph6_index": index,
                "graph6": graph6_records[index],
                "component_orders": [len(part) for part in components(graph)],
                "mandatory_k_edges": len(edge_tuple(mandatory)),
                "mandatory_k_degrees": [mask.bit_count() for mask in mandatory],
                "f_edges": [list(edge) for edge in f_edges],
                "support_edges": [list(edge) for edge in supports],
                "support_count": len(supports),
                "search_statistics": statistics,
                "rejection_tree": tree,
            }
        )

    if len(survivors) != 4:
        raise AssertionError(f"mandatory-degree filter left {len(survivors)}, not four")

    attack_graph = graph6_graphs[6]
    attack_problem = support_problem(attack_graph)
    attack_selected, attack_nodes = find_lambda_only_factor(attack_problem)
    attack_supports = attack_problem["supports"]
    attack_base = attack_problem["base"]
    assert isinstance(attack_supports, tuple)
    assert isinstance(attack_base, tuple)
    if adjacent_cap_violation(attack_base, attack_supports, attack_selected):
        raise AssertionError("lambda-only attack witness violates lambda cap")
    attack_mu_witness = cap_violation(
        attack_base, attack_supports, attack_selected
    )
    if (
        attack_mu_witness is None
        or attack_mu_witness["adjacent"]
        or len(attack_mu_witness["common"]) != 3
    ):
        raise AssertionError("lambda-only attack does not isolate a mu=2 failure")

    payload = {
        "schema": "conway99-n3-42-support-proof-v1",
        "scope": (
            "conditional all-size-two n3=42 active-support relaxation; "
            "not a 99-vertex existence search"
        ),
        "catalog": catalog,
        "mandatory_max_degree_histogram": {
            str(key): value for key, value in sorted(degree_histogram.items())
        },
        "mandatory_degree_survivors": survivors,
        "mu_cap_attack": {
            "graph6_index": 6,
            "search_nodes": attack_nodes,
            "selected_support_indices": [
                index
                for index in range(len(attack_supports))
                if (attack_selected >> index) & 1
            ],
            "selected_support_pairs": [
                list(attack_supports[index])
                for index in range(len(attack_supports))
                if (attack_selected >> index) & 1
            ],
            "cycles": factor_cycles(
                F_EDGE_COUNT, attack_supports, attack_selected
            ),
            "lambda_cap": "PASS",
            "first_mu_cap_violation": attack_mu_witness,
        },
        "all_support_cap_survivors": sum(
            int(row["search_statistics"]["survivors"])  # type: ignore[index]
            for row in survivors
        ),
        "target_result": "UNKNOWN",
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.output.write_text(encoded, encoding="utf-8", newline="\n")

    print(f"official_shortcode_sha256={catalog['scd_sha256']}")
    print(f"official_connected_records={catalog['scd_records']}")
    print(f"repository_graph6_sha256={catalog['graph6_sha256']}")
    print(f"repository_records={catalog['graph6_records']}")
    print(f"disconnected={json.dumps(catalog['disconnected'], sort_keys=True)}")
    print(f"mandatory_degree_survivors={[row['graph6_index'] for row in survivors]}")
    for row in survivors:
        print(
            "survivor",
            row["graph6_index"],
            row["graph6"],
            "M_edges",
            row["mandatory_k_edges"],
            "supports",
            row["support_count"],
            "search",
            json.dumps(row["search_statistics"], sort_keys=True),
        )
    print(f"all_support_cap_survivors={payload['all_support_cap_survivors']}")
    print(
        "mu_cap_attack="
        + json.dumps(payload["mu_cap_attack"], sort_keys=True)
    )
    print(f"certificate_sha256={sha256(args.output)}")
    print("target_result=UNKNOWN")
    return 0 if payload["all_support_cap_survivors"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
