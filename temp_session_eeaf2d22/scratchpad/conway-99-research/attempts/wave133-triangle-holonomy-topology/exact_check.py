#!/usr/bin/env python3
"""Exact Wave 133 triangle-holonomy and topological-twist controls.

This package is conditional on the prism-free endpoint of a hypothetical
srg(99,14,1,2).  It proves the local holonomy identities algebraically and
constructs two finite controls:

* two 39-vertex triangle-star partial graphs with opposite holonomy signs;
* an endpoint-scale abstract all-222 surface incidence system.

Neither control is a 99-vertex graph or an SRG extension certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Iterable, Sequence


N = 12
GRAPH_TRIANGLES = 231
RELATION_EDGES = 4158
ALL_222_FACES = 2079
SHEETS = 693

# Three oriented quadrilateral faces have side occurrences 0..11.
# Pairings glue each side occurrence to exactly one other occurrence.
BASE_EDGE_PAIRS = (
    (0, 4),
    (1, 5),
    (2, 8),
    (3, 10),
    (6, 9),
    (7, 11),
)
BASE_TWIST_BITS = (0, 0, 0, 1, 0, 1)

# Permutation voltages in (C7 semidirect C3) x C33.  In the first factor,
# b acts on a by multiplication by 2^b modulo 7.
BASE_VOLTAGES = (
    (6, 0, 25),
    (1, 2, 26),
    (0, 2, 11),
    (0, 2, 4),
    (5, 1, 22),
    (3, 1, 29),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_json(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def one_factor(round_index: int) -> tuple[tuple[int, int], ...]:
    """Return round `round_index` of the standard one-factorization of K12."""

    require(0 <= round_index < N - 1, "bad one-factor index")
    pairs = [(N - 1, round_index)]
    for offset in range(1, N // 2):
        pairs.append(
            (
                (round_index + offset) % (N - 1),
                (round_index - offset) % (N - 1),
            )
        )
    return tuple(sorted(tuple(sorted(pair)) for pair in pairs))


FACTORS = tuple(one_factor(index) for index in range(N - 1))


def partner_map(factor: Sequence[tuple[int, int]]) -> tuple[int, ...]:
    result = [-1] * N
    for left, right in factor:
        require(left != right, "loop in perfect matching")
        require(result[left] < 0 and result[right] < 0, "matching collision")
        result[left] = right
        result[right] = left
    require(all(value >= 0 for value in result), "matching is not perfect")
    return tuple(result)


FACTOR_MAPS = tuple(partner_map(factor) for factor in FACTORS)
POSITIVE_HOLONOMY = FACTOR_MAPS[0]
NEGATIVE_HOLONOMY = tuple(range(1, N)) + (0,)
WITHIN_FACTORS = (1, 2, 3)


def permutation_cycles(permutation: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    require(sorted(permutation) == list(range(len(permutation))), "not a permutation")
    unseen = set(range(len(permutation)))
    cycles: list[tuple[int, ...]] = []
    while unseen:
        start = min(unseen)
        current = start
        cycle = []
        while current in unseen:
            unseen.remove(current)
            cycle.append(current)
            current = permutation[current]
        require(current == start, "permutation orbit did not close")
        cycles.append(tuple(cycle))
    return tuple(cycles)


def permutation_sign(permutation: Sequence[int]) -> int:
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def add_edge(adjacency: list[set[int]], left: int, right: int) -> None:
    require(left != right, "loop")
    require(right not in adjacency[left], "parallel edge")
    adjacency[left].add(right)
    adjacency[right].add(left)


def build_triangle_star(
    holonomy: Sequence[int],
) -> tuple[list[set[int]], list[set[int]]]:
    """Build the 36-vertex core and its 39-vertex rooted triangle star."""

    core = [set() for _ in range(3 * N)]
    for fibre, factor_index in enumerate(WITHIN_FACTORS):
        for left, right in FACTORS[factor_index]:
            add_edge(core, fibre * N + left, fibre * N + right)
    for label in range(N):
        add_edge(core, label, N + label)
        add_edge(core, N + label, 2 * N + label)
        add_edge(core, 2 * N + label, holonomy[label])

    star = [set() for _ in range(3 + 3 * N)]
    add_edge(star, 0, 1)
    add_edge(star, 1, 2)
    add_edge(star, 2, 0)
    for fibre in range(3):
        for label in range(N):
            add_edge(star, fibre, 3 + fibre * N + label)
    for left in range(3 * N):
        for right in core[left]:
            if left < right:
                add_edge(star, 3 + left, 3 + right)
    return core, star


def triangle_count(adjacency: Sequence[set[int]]) -> int:
    return sum(
        right in adjacency[middle]
        for left in range(len(adjacency))
        for middle in adjacency[left]
        if left < middle
        for right in adjacency[left] & adjacency[middle]
        if middle < right
    )


def common_neighbor_histogram(
    adjacency: Sequence[set[int]],
) -> tuple[Counter[tuple[int, int]], int, int]:
    histogram: Counter[tuple[int, int]] = Counter()
    maximum_adjacent = 0
    maximum_nonadjacent = 0
    for left in range(len(adjacency)):
        for right in range(left + 1, len(adjacency)):
            common = len(adjacency[left] & adjacency[right])
            adjacent = int(right in adjacency[left])
            histogram[(adjacent, common)] += 1
            if adjacent:
                maximum_adjacent = max(maximum_adjacent, common)
            else:
                maximum_nonadjacent = max(maximum_nonadjacent, common)
    return histogram, maximum_adjacent, maximum_nonadjacent


def forced_gram(core: Sequence[set[int]]) -> list[list[int]]:
    """Return 12I-A+2J-RR^T-A^2 for a normalized 36-vertex core."""

    result = [[0] * (3 * N) for _ in range(3 * N)]
    for left in range(3 * N):
        for right in range(3 * N):
            result[left][right] = (
                (12 if left == right else 0)
                - (1 if right in core[left] else 0)
                + 2
                - (1 if left // N == right // N else 0)
                - len(core[left] & core[right])
            )
    return result


def local_control_record(name: str, holonomy: Sequence[int]) -> dict[str, object]:
    core, star = build_triangle_star(holonomy)
    cycles = permutation_cycles(holonomy)
    histogram, adjacent_cap, nonadjacent_cap = common_neighbor_histogram(star)
    gram = forced_gram(core)
    require(all(len(neighbors) == 3 for neighbors in core), "core is not cubic")
    require(triangle_count(core) == 0, "core has a triangle")
    require([len(star[index]) for index in range(3)] == [14, 14, 14], "base degree")
    require(
        all(len(star[index]) == 4 for index in range(3, 39)),
        "outside partial-star degree",
    )
    require(adjacent_cap <= 1 and nonadjacent_cap <= 2, "SRG codegree cap failed")
    require(min(map(min, gram)) >= 0, "forced Gram has negative entry")
    fixed_points = sum(holonomy[index] == index for index in range(N))
    require(fixed_points == 0, "control holonomy is not a derangement")
    require(
        permutation_sign(holonomy) == (-1) ** len(cycles),
        "even-degree sign/cycle identity failed",
    )
    return {
        "name": name,
        "holonomy": list(holonomy),
        "holonomy_cycle_type": sorted(len(cycle) for cycle in cycles),
        "holonomy_cycle_count": len(cycles),
        "holonomy_fixed_points": fixed_points,
        "holonomy_sign": permutation_sign(holonomy),
        "cross_two_factor_cycle_type": sorted(3 * len(cycle) for cycle in cycles),
        "within_fibre_factor_indices": list(WITHIN_FACTORS),
        "core_vertices": len(core),
        "core_degree": 3,
        "core_edges": sum(map(len, core)) // 2,
        "core_triangle_count": triangle_count(core),
        "partial_star_vertices": len(star),
        "partial_star_degree_sequence": sorted(map(len, star)),
        "partial_star_common_neighbor_cap_adjacent": adjacent_cap,
        "partial_star_common_neighbor_cap_nonadjacent": nonadjacent_cap,
        "partial_star_common_neighbor_histogram": {
            f"adjacent_{adjacent}_common_{common}": count
            for (adjacent, common), count in sorted(histogram.items())
        },
        "forced_gram_entry_range": [
            min(min(row) for row in gram),
            max(max(row) for row in gram),
        ],
        "certificate_sha256": sha256_json(
            {
                "holonomy": list(holonomy),
                "core": [sorted(neighbors) for neighbors in core],
            }
        ),
    }


GroupElement = tuple[int, int, int]
IDENTITY: GroupElement = (0, 0, 0)


def group_mul(left: GroupElement, right: GroupElement) -> GroupElement:
    a, b, c = left
    d, e, f = right
    return (
        (a + pow(2, b, 7) * d) % 7,
        (b + e) % 3,
        (c + f) % 33,
    )


def group_inverse(value: GroupElement) -> GroupElement:
    a, b, c = value
    inverse_b = (-b) % 3
    return (
        (-pow(2, inverse_b, 7) * a) % 7,
        inverse_b,
        (-c) % 33,
    )


GROUP_ELEMENTS = tuple(
    (a, b, c) for a in range(7) for b in range(3) for c in range(33)
)
GROUP_INDEX = {value: index for index, value in enumerate(GROUP_ELEMENTS)}


def base_complex() -> dict[str, object]:
    """Build the two-vertex, six-edge, three-square base surface."""

    link_adjacency = [set() for _ in range(24)]
    for face in range(3):
        for position in range(4):
            side = 4 * face + position
            previous = 4 * face + (position - 1) % 4
            add_edge(link_adjacency, 2 * side, 2 * previous + 1)

    occurrence: dict[int, tuple[int, int]] = {}
    for edge, ((left, right), twist) in enumerate(
        zip(BASE_EDGE_PAIRS, BASE_TWIST_BITS)
    ):
        occurrence[left] = (edge, 1)
        occurrence[right] = (edge, 1 if twist else -1)
        endpoint_pairs = (
            ((0, 0), (1, 1)) if twist else ((0, 1), (1, 0))
        )
        for left_endpoint, right_endpoint in endpoint_pairs:
            add_edge(
                link_adjacency,
                2 * left + left_endpoint,
                2 * right + right_endpoint,
            )

    component = [-1] * 24
    components: list[list[int]] = []
    for start in range(24):
        if component[start] >= 0:
            continue
        label = len(components)
        stack = [start]
        nodes = []
        while stack:
            current = stack.pop()
            if component[current] >= 0:
                continue
            component[current] = label
            nodes.append(current)
            stack.extend(link_adjacency[current])
        components.append(sorted(nodes))
    require(sorted(len(nodes) // 2 for nodes in components) == [6, 6], "base links")
    require(all(len(neighbors) == 2 for neighbors in link_adjacency), "base link degree")

    face_words: list[list[tuple[int, int]]] = []
    for face in range(3):
        face_words.append(
            [occurrence[4 * face + position] for position in range(4)]
        )

    for word in face_words:
        product = IDENTITY
        for edge, sign in word:
            voltage = BASE_VOLTAGES[edge]
            product = group_mul(
                product, voltage if sign == 1 else group_inverse(voltage)
            )
        require(product == IDENTITY, "face voltage did not close")

    reference_orientations = []
    for left, _right in BASE_EDGE_PAIRS:
        reference_orientations.append((component[2 * left], component[2 * left + 1]))
    require(all(left != right for left, right in reference_orientations), "base loop")
    normalized_a_to_b = tuple(
        voltage if orientation == (0, 1) else group_inverse(voltage)
        for voltage, orientation in zip(BASE_VOLTAGES, reference_orientations)
    )
    require(len(set(normalized_a_to_b)) == 6, "parallel lifted matchings")

    return {
        "component": component,
        "components": components,
        "occurrence": occurrence,
        "face_words": face_words,
        "reference_orientations": reference_orientations,
        "normalized_a_to_b": normalized_a_to_b,
    }


def generated_subgroup(generators: Iterable[GroupElement]) -> set[GroupElement]:
    moves = tuple(generators)
    moves += tuple(group_inverse(value) for value in moves)
    seen = {IDENTITY}
    queue = deque([IDENTITY])
    while queue:
        current = queue.popleft()
        for move in moves:
            nxt = group_mul(current, move)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def surface_cover() -> dict[str, object]:
    """Lift the base surface to a connected 693-sheet regular cover."""

    base = base_complex()
    normalized = base["normalized_a_to_b"]
    require(isinstance(normalized, tuple), "normalized voltage type")
    differences = tuple(
        group_mul(group_inverse(normalized[0]), value) for value in normalized[1:]
    )
    require(len(generated_subgroup(differences)) == SHEETS, "cover disconnected")

    # Edge order is sheet-major, then normalized matching.  This fixed order is
    # also the input to the deterministic balanced quotient construction.
    edges: list[tuple[int, int]] = []
    for sheet_index, sheet in enumerate(GROUP_ELEMENTS):
        for voltage in normalized:
            target = GROUP_INDEX[group_mul(sheet, voltage)]
            edges.append((sheet_index, SHEETS + target))
    require(len(edges) == RELATION_EDGES, "cover edge count")
    require(len(set(edges)) == RELATION_EDGES, "cover is not simple")

    edge_index = {tuple(sorted(edge)): index for index, edge in enumerate(edges)}
    require(len(edge_index) == RELATION_EDGES, "edge index collision")

    faces: list[tuple[int, int, int, int]] = []
    component = base["component"]
    occurrence = base["occurrence"]
    require(isinstance(component, list) and isinstance(occurrence, dict), "base types")
    for face in range(3):
        first_side = 4 * face
        start_base_vertex = component[2 * first_side]
        for initial_sheet in GROUP_ELEMENTS:
            sheet = initial_sheet
            vertices = []
            for position in range(4):
                side = 4 * face + position
                current_base_vertex = component[2 * side]
                require(current_base_vertex == component[2 * side], "base vertex")
                vertices.append(
                    current_base_vertex * SHEETS + GROUP_INDEX[sheet]
                )
                edge, sign = occurrence[side]
                voltage = BASE_VOLTAGES[edge]
                sheet = group_mul(
                    sheet, voltage if sign == 1 else group_inverse(voltage)
                )
            require(sheet == initial_sheet, "lifted face did not close")
            require(
                component[2 * first_side] == start_base_vertex,
                "face basepoint changed",
            )
            require(len(set(vertices)) == 4, "lifted face is not a four-cycle")
            faces.append(tuple(vertices))
    require(len(faces) == ALL_222_FACES, "cover face count")

    face_edge_ids: list[tuple[int, int, int, int]] = []
    edge_multiplicity = [0] * len(edges)
    for vertices in faces:
        boundary = []
        for position in range(4):
            pair = tuple(sorted((vertices[position], vertices[(position + 1) % 4])))
            require(pair in edge_index, "face boundary is not a cover edge")
            edge = edge_index[pair]
            boundary.append(edge)
            edge_multiplicity[edge] += 1
        require(len(set(boundary)) == 4, "face repeats an edge")
        face_edge_ids.append(tuple(boundary))
    require(set(edge_multiplicity) == {2}, "surface edge is not in two faces")

    adjacency = [set() for _ in range(2 * SHEETS)]
    for left, right in edges:
        add_edge(adjacency, left, right)
    require(all(len(neighbors) == 6 for neighbors in adjacency), "cover degree")
    seen = {0}
    queue = deque([0])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    require(len(seen) == 2 * SHEETS, "cover graph disconnected")

    incident_edges = [set() for _ in range(2 * SHEETS)]
    link_adjacency: list[dict[int, set[int]]] = [
        defaultdict(set) for _ in range(2 * SHEETS)
    ]
    for edge, (left, right) in enumerate(edges):
        incident_edges[left].add(edge)
        incident_edges[right].add(edge)
    for vertices, boundary in zip(faces, face_edge_ids):
        for position, vertex in enumerate(vertices):
            previous_edge = boundary[(position - 1) % 4]
            next_edge = boundary[position]
            link_adjacency[vertex][previous_edge].add(next_edge)
            link_adjacency[vertex][next_edge].add(previous_edge)
    for vertex in range(2 * SHEETS):
        require(
            set(link_adjacency[vertex]) == incident_edges[vertex],
            "link misses an incident edge",
        )
        require(
            all(len(neighbors) == 2 for neighbors in link_adjacency[vertex].values()),
            "link is not two-regular",
        )
        start = min(incident_edges[vertex])
        link_seen = {start}
        link_queue = [start]
        while link_queue:
            current = link_queue.pop()
            for neighbor in link_adjacency[vertex][current]:
                if neighbor not in link_seen:
                    link_seen.add(neighbor)
                    link_queue.append(neighbor)
        require(len(link_seen) == 6, "cover vertex link is not one six-cycle")

    return {
        "edges": edges,
        "faces": faces,
        "face_edge_ids": face_edge_ids,
        "normalized_a_to_b": normalized,
        "base": base,
    }


def quotient_pair(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left <= right else (right, left)


def collision_cost(pair: tuple[int, int], multiplicity: int) -> int:
    if pair[0] == pair[1]:
        return multiplicity
    return max(0, multiplicity - 1)


def deterministic_six_vertex_partition(
    edges: Sequence[tuple[int, int]],
) -> tuple[list[int], int]:
    """Find a balanced partition with no loop or repeated quotient edge.

    This is a construction algorithm, not a nonexistence search.  Its output
    is checked from scratch below.  The seed and all ordering choices are
    frozen, so verification is deterministic.
    """

    vertex_count = 2 * SHEETS
    rng = random.Random(133)
    labels = [group for group in range(GRAPH_TRIANGLES) for _ in range(6)]
    rng.shuffle(labels)
    incident = [[] for _ in range(vertex_count)]
    for edge, (left, right) in enumerate(edges):
        incident[left].append(edge)
        incident[right].append(edge)

    multiplicities: Counter[tuple[int, int]] = Counter()
    buckets: defaultdict[tuple[int, int], set[int]] = defaultdict(set)
    for edge, (left, right) in enumerate(edges):
        pair = quotient_pair(labels[left], labels[right])
        multiplicities[pair] += 1
        buckets[pair].add(edge)
    cost = sum(
        collision_cost(pair, count) for pair, count in multiplicities.items()
    )
    bad = {
        pair
        for pair, count in multiplicities.items()
        if collision_cost(pair, count)
    }

    for iteration in range(100_000):
        if cost == 0:
            return labels, iteration
        bad_pair = rng.choice(sorted(bad))
        edge = rng.choice(sorted(buckets[bad_pair]))
        left, right = edges[edge]
        first = rng.choice((left, right))
        second = rng.randrange(vertex_count)
        if labels[first] == labels[second]:
            continue

        affected = set(incident[first]) | set(incident[second])
        old_pairs = {
            item: quotient_pair(labels[edges[item][0]], labels[edges[item][1]])
            for item in affected
        }
        old_first, old_second = labels[first], labels[second]
        labels[first], labels[second] = old_second, old_first
        new_pairs = {
            item: quotient_pair(labels[edges[item][0]], labels[edges[item][1]])
            for item in affected
        }
        touched = set(old_pairs.values()) | set(new_pairs.values())
        old_counts = {pair: multiplicities.get(pair, 0) for pair in touched}
        for item in affected:
            old_pair, new_pair = old_pairs[item], new_pairs[item]
            if old_pair == new_pair:
                continue
            multiplicities[old_pair] -= 1
            buckets[old_pair].remove(item)
            multiplicities[new_pair] += 1
            buckets[new_pair].add(item)
        delta = sum(
            collision_cost(pair, multiplicities[pair])
            - collision_cost(pair, old_counts[pair])
            for pair in touched
        )
        temperature = max(0.01, 0.8 * (1 - iteration / 5_000_000))
        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            cost += delta
            for pair in touched:
                if collision_cost(pair, multiplicities[pair]):
                    bad.add(pair)
                else:
                    bad.discard(pair)
        else:
            labels[first], labels[second] = old_first, old_second
            for item in affected:
                old_pair, new_pair = old_pairs[item], new_pairs[item]
                if old_pair == new_pair:
                    continue
                multiplicities[new_pair] -= 1
                buckets[new_pair].remove(item)
                multiplicities[old_pair] += 1
                buckets[old_pair].add(item)
    raise AssertionError("frozen constructive partition run did not finish")


def quotient_record(cover: dict[str, object]) -> dict[str, object]:
    edges = cover["edges"]
    faces = cover["faces"]
    require(isinstance(edges, list) and isinstance(faces, list), "cover record type")
    labels, iterations = deterministic_six_vertex_partition(edges)
    counts = Counter(labels)
    require(
        counts == Counter({label: 6 for label in range(GRAPH_TRIANGLES)}),
        "partition is not 6-balanced",
    )

    quotient_edges = [
        quotient_pair(labels[left], labels[right]) for left, right in edges
    ]
    require(all(left != right for left, right in quotient_edges), "quotient loop")
    require(len(set(quotient_edges)) == RELATION_EDGES, "quotient parallel edge")
    quotient_adjacency = [set() for _ in range(GRAPH_TRIANGLES)]
    for left, right in quotient_edges:
        add_edge(quotient_adjacency, left, right)
    require(
        all(len(neighbors) == 36 for neighbors in quotient_adjacency),
        "quotient is not 36-regular",
    )

    quotient_faces = []
    for face in faces:
        boundary = tuple(labels[vertex] for vertex in face)
        require(len(set(boundary)) == 4, "quotient face is not a four-cycle")
        quotient_faces.append(boundary)
    require(len(set(quotient_faces)) == len(quotient_faces), "duplicate face tuple")

    quotient_edge_index = {
        pair: index for index, pair in enumerate(sorted(set(quotient_edges)))
    }
    edge_face_multiplicity = [0] * RELATION_EDGES
    link_adjacency: list[dict[int, set[int]]] = [
        defaultdict(set) for _ in range(GRAPH_TRIANGLES)
    ]
    for boundary in quotient_faces:
        edge_ids = []
        for position in range(4):
            pair = quotient_pair(boundary[position], boundary[(position + 1) % 4])
            edge = quotient_edge_index[pair]
            edge_ids.append(edge)
            edge_face_multiplicity[edge] += 1
        for position, vertex in enumerate(boundary):
            previous_edge = edge_ids[(position - 1) % 4]
            next_edge = edge_ids[position]
            link_adjacency[vertex][previous_edge].add(next_edge)
            link_adjacency[vertex][next_edge].add(previous_edge)
    require(set(edge_face_multiplicity) == {2}, "quotient edge/face multiplicity")

    link_cycle_types = []
    for vertex in range(GRAPH_TRIANGLES):
        link = link_adjacency[vertex]
        require(len(link) == 36, "quotient link order")
        require(all(len(neighbors) == 2 for neighbors in link.values()), "link degree")
        unseen = set(link)
        lengths = []
        while unseen:
            start = min(unseen)
            stack = [start]
            component = set()
            while stack:
                current = stack.pop()
                if current in component:
                    continue
                component.add(current)
                stack.extend(link[current])
            unseen -= component
            lengths.append(len(component))
        require(sorted(lengths) == [6] * 6, "quotient link is not six C6s")
        link_cycle_types.append(sorted(lengths))

    h_total = sum(len(cycles) for cycles in link_cycle_types)
    euler = h_total - RELATION_EDGES + ALL_222_FACES
    require(h_total == 1386 and euler == -693, "Euler data changed")
    require(euler % 2, "control no longer forces nonorientability")
    product_sign = 1
    for cycles in link_cycle_types:
        product_sign *= (-1) ** len(cycles)
    require(product_sign == 1, "global holonomy sign product changed")
    require(
        product_sign == (-1) ** (euler + RELATION_EDGES - ALL_222_FACES),
        "surface sign identity failed",
    )
    return {
        "partition_seed": 133,
        "partition_acceptance_iteration": iterations,
        "partition_sha256": sha256_json(labels),
        "split_surface_vertices": 2 * SHEETS,
        "quotient_vertices": GRAPH_TRIANGLES,
        "quotient_edges": len(quotient_edges),
        "quotient_degree": 36,
        "quotient_simple": True,
        "quadrilateral_faces": len(quotient_faces),
        "edge_face_multiplicity": 2,
        "link_cycle_type_at_every_quotient_vertex": [6, 6, 6, 6, 6, 6],
        "link_component_total_H": h_total,
        "implied_holonomy_cycle_type_at_every_triangle": [2, 2, 2, 2, 2, 2],
        "implied_holonomy_sign_at_every_triangle": 1,
        "global_holonomy_sign_product": product_sign,
        "euler_characteristic": euler,
        "orientability": "NONORIENTABLE_FORCED_BY_CONNECTED_ODD_EULER_CHARACTERISTIC",
        "quotient_certificate_sha256": sha256_json(
            {
                "labels": labels,
                "edges": quotient_edges,
                "faces": quotient_faces,
            }
        ),
    }


def build_record() -> dict[str, object]:
    positive = local_control_record("positive_six_transpositions", POSITIVE_HOLONOMY)
    negative = local_control_record("negative_twelve_cycle", NEGATIVE_HOLONOMY)
    require(
        {positive["holonomy_sign"], negative["holonomy_sign"]} == {-1, 1},
        "local controls do not realize both signs",
    )

    base = base_complex()
    cover = surface_cover()
    quotient = quotient_record(cover)
    base_components = base["components"]
    require(isinstance(base_components, list), "base components type")
    return {
        "format": "wave133-triangle-holonomy-topology-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Conditional prism-free endpoint: exact rooted-triangle holonomy "
            "identities and finite local/topological controls. No SRG construction."
        ),
        "frozen_parameters": {
            "hypothetical_graph": "srg(99,14,1,2)",
            "endpoint_n3": 4158,
            "endpoint_triangular_prisms": 0,
            "graph_triangles": GRAPH_TRIANGLES,
            "relation_edges": RELATION_EDGES,
            "all_222_faces": ALL_222_FACES,
        },
        "derived_holonomy": {
            "fibres": "X=N(a)-{b,c}, Y=N(b)-{a,c}, Z=N(c)-{a,b}",
            "fibre_sizes": [N, N, N],
            "internal_graph_in_each_fibre": "6K2",
            "cross_graph_between_each_fibre_pair": "perfect_matching",
            "normalized_composition": "h_T=m_ZX o m_YZ o m_XY on X",
            "gauge_rule": "Fibre relabelling conjugates h_T; reversal inverts it.",
            "prism_identity": "induced_prisms_based_at_T = fixed_points(h_T)",
            "endpoint_condition": "h_T is a derangement for every graph triangle T",
            "cross_two_factor_rule": (
                "A holonomy cycle of length k is a cross-fibre cycle of length 3k."
            ),
            "link_component_identity": "h(T)=number_of_cycles(h_T)",
            "sign_identity_per_triangle": "sign(h_T)=(-1)^h(T), since |X|=12",
            "global_surface_sign_identity": (
                "product_T sign(h_T)=(-1)^H="
                "(-1)^(chi+E-F)"
            ),
            "all_222_orientable_implication": (
                "If every normalized surface component were orientable, chi "
                "would be even and product_T sign(h_T) would equal -1."
            ),
        },
        "local_opposite_sign_controls": [positive, negative],
        "topological_twist_control": {
            "base_surface": {
                "vertices": len(base_components),
                "edges": len(BASE_EDGE_PAIRS),
                "faces": 3,
                "link_cycle_lengths": sorted(
                    len(component) // 2 for component in base_components
                ),
                "euler_characteristic": len(base_components) - 6 + 3,
                "side_pairings": [list(pair) for pair in BASE_EDGE_PAIRS],
                "twist_bits": list(BASE_TWIST_BITS),
                "voltages": [list(value) for value in BASE_VOLTAGES],
            },
            "regular_cover": {
                "group": "(C7 semidirect_2 C3) x C33",
                "sheets": SHEETS,
                "connected": True,
                "vertices": 2 * SHEETS,
                "edges": RELATION_EDGES,
                "faces": ALL_222_FACES,
                "simple_six_regular_bipartite_one_skeleton": True,
                "one_six_cycle_link_at_every_split_vertex": True,
            },
            "balanced_quotient": quotient,
        },
        "conclusion": {
            "stronger_exact_necessary_condition": (
                "The global holonomy-sign product is controlled by the Euler "
                "characteristic and face parity, not by derangement alone."
            ),
            "precise_null": (
                "Even after imposing endpoint-scale E/F counts, a simple "
                "36-regular 231-vertex relation quotient, two faces per edge, "
                "and six C6 link components at every triangle, an exact "
                "nonorientable control realizes product sign +1. Therefore a "
                "sign/parity contradiction requires a new theorem forcing "
                "orientability or otherwise constraining the edge-twist class."
            ),
            "endpoint_excluded": False,
            "upper_bound_improved": False,
            "target_status": "UNKNOWN",
        },
        "limitations": [
            "The 39-vertex controls are partial induced-star controls only.",
            "The surface control is an abstract incidence system, not a graph.",
            "The balanced quotient is not asserted to satisfy every intersection parameter forced on the true N3 relation.",
            "No 60-block B system, outside graph H, or 99-vertex adjacency matrix is constructed.",
            "No automorphism or transitivity assumption is used.",
            "The constructive finite controls prove survival of stated relaxations only, not endpoint existence.",
            "Independent verification is required before promotion.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    record = build_record()
    rendered = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        require(record == expected, "stored exact-results.json differs from replay")
        print(f"verified {args.verify}")
    elif args.output is not None:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
