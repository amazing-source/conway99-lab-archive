#!/usr/bin/env python3
"""Independent exact audit of the abstract n3=30 side-incidence case.

This is a scratch verifier, deliberately outside the research repository.  It
uses only the Python standard library.  The computation has three layers:

1. Generate every labeled simple cubic graph K on vertices 0,...,9 with the
   harmless normalization N_K(0)={1,2,3}, and quotient by an exact adjacency-
   preserving isomorphism search.
2. For every K type, enumerate every admissible family of point-cliques S_u:
   K-edge consumption is disjoint, K3 intersections obey the common-point
   rule, unused K-edges are allowed, loads are at most three, and distinct
   singleton fillers complete every active triangle to three points.
3. Apply the allowed H-degree set and fixed-side H_T local degree 0/2 rule.
   Cases with fewer than eleven candidate support vertices fail Mantel.  In
   all remaining cases, exhaust every subset of candidate support vertices
   and require every L-edge to be covered exactly twice.  Later matching,
   H-simplicity, H-triangle-freeness, and graph-degree-capacity filters are
   retained as separate audit layers, although no exact-two cover survives.

Candidate support pairs are only an upper cover: the program never calls one
an actual graph edge until it is selected in an exact-two cover.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from itertools import combinations, permutations
from pathlib import Path
from typing import Iterator, Sequence


N = 10
NONZERO_H_DEGREES = frozenset((4, 6, 8, 10, 12))
MANTEL_SUPPORT_MINIMUM = 11

Edge = tuple[int, int]
Graph = tuple[int, ...]
Point = tuple[int, ...]
Candidate = tuple[int, int, int, int]  # point ids, L-edge mask, H-degree


def graph_features(graph: Graph):
    component = [-1] * N
    component_sizes: list[int] = []
    for start in range(N):
        if component[start] >= 0:
            continue
        queue = [start]
        component[start] = len(component_sizes)
        for vertex in queue:
            unseen = graph[vertex]
            while unseen:
                bit = unseen & -unseen
                other = bit.bit_length() - 1
                unseen -= bit
                if component[other] < 0:
                    component[other] = component[start]
                    queue.append(other)
        component_sizes.append(len(queue))

    vertex_features = []
    for vertex in range(N):
        neighbors = [other for other in range(N) if graph[vertex] >> other & 1]
        triangle_count = sum(
            bool(graph[first] >> second & 1)
            for first, second in combinations(neighbors, 2)
        )
        distance = [-1] * N
        distance[vertex] = 0
        queue = [vertex]
        for current in queue:
            unseen = graph[current]
            while unseen:
                bit = unseen & -unseen
                other = bit.bit_length() - 1
                unseen -= bit
                if distance[other] < 0:
                    distance[other] = distance[current] + 1
                    queue.append(other)
        distance_histogram = tuple(
            Counter(distance).get(value, 0) for value in range(1, 6)
        )
        common_neighbors = tuple(
            sorted(
                (graph[vertex] & graph[other]).bit_count()
                for other in range(N)
                if other != vertex
            )
        )
        vertex_features.append(
            (
                component_sizes[component[vertex]],
                triangle_count,
                distance_histogram,
                common_neighbors,
            )
        )
    global_features = (
        tuple(sorted(component_sizes)),
        tuple(sorted(vertex_features)),
    )
    return tuple(vertex_features), global_features


def exact_isomorphism_count(
    first: Graph,
    first_features,
    second: Graph,
    second_features,
    *,
    count_all: bool,
) -> int | bool:
    """Exact adjacency-preserving backtracking, optionally counting all maps."""

    first_vertex, first_global = first_features
    second_vertex, second_global = second_features
    if first_global != second_global:
        return 0 if count_all else False

    first_to_second = [-1] * N
    second_to_first = [-1] * N
    second_classes: dict[object, list[int]] = defaultdict(list)
    for vertex, feature in enumerate(second_vertex):
        second_classes[feature].append(vertex)
    first_root_neighbors = [
        vertex for vertex in range(N) if first[0] >> vertex & 1
    ]
    total = 0

    def extend(mapped_count: int) -> bool:
        nonlocal total
        if mapped_count == N:
            total += 1
            return not count_all

        best_vertex = -1
        best_images: list[int] | None = None
        best_key = None
        for vertex in range(N):
            if first_to_second[vertex] >= 0:
                continue
            images = []
            for image in second_classes[first_vertex[vertex]]:
                if second_to_first[image] >= 0:
                    continue
                if all(
                    bool(first[vertex] >> mapped & 1)
                    == bool(second[image] >> first_to_second[mapped] & 1)
                    for mapped in range(N)
                    if first_to_second[mapped] >= 0
                ):
                    images.append(image)
            if not images:
                return False
            mapped_neighbors = sum(
                first_to_second[other] >= 0
                for other in range(N)
                if first[vertex] >> other & 1
            )
            key = (-mapped_neighbors, len(images))
            if best_key is None or key < best_key:
                best_key = key
                best_vertex = vertex
                best_images = images

        assert best_images is not None
        for image in best_images:
            first_to_second[best_vertex] = image
            second_to_first[image] = best_vertex
            if extend(mapped_count + 1) and not count_all:
                return True
            first_to_second[best_vertex] = -1
            second_to_first[image] = -1
        return False

    for second_root in second_classes[first_vertex[0]]:
        first_to_second[0] = second_root
        second_to_first[second_root] = 0
        second_neighbors = [
            vertex for vertex in range(N) if second[second_root] >> vertex & 1
        ]
        for ordered_images in permutations(second_neighbors):
            if any(
                second_vertex[ordered_images[index]]
                != first_vertex[first_root_neighbors[index]]
                for index in range(3)
            ):
                continue
            for vertex, image in zip(first_root_neighbors, ordered_images):
                first_to_second[vertex] = image
                second_to_first[image] = vertex
            if extend(4) and not count_all:
                return True
            for vertex, image in zip(first_root_neighbors, ordered_images):
                first_to_second[vertex] = -1
                second_to_first[image] = -1
        first_to_second[0] = -1
        second_to_first[second_root] = -1
    return total if count_all else False


def graph6(graph: Graph) -> str:
    bits = [
        (graph[first] >> second) & 1
        for second in range(1, N)
        for first in range(second)
    ]
    bits.extend([0] * (-len(bits) % 6))
    return chr(63 + N) + "".join(
        chr(
            63
            + sum(
                bits[offset + index] << (5 - index)
                for index in range(6)
            )
        )
        for offset in range(0, len(bits), 6)
    )


def decode_graph6(encoded: str) -> Graph:
    if ord(encoded[0]) - 63 != N:
        raise ValueError("this checker expects graph6 order ten")
    bits = []
    for character in encoded[1:]:
        value = ord(character) - 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    graph = [0] * N
    offset = 0
    for second in range(1, N):
        for first in range(second):
            if bits[offset]:
                graph[first] |= 1 << second
                graph[second] |= 1 << first
            offset += 1
    return tuple(graph)


def graph_edges(graph: Graph) -> tuple[Edge, ...]:
    return tuple(
        (first, second)
        for first, second in combinations(range(N), 2)
        if graph[first] >> second & 1
    )


def component_sizes(graph: Graph) -> tuple[int, ...]:
    return graph_features(graph)[1][0]


def triangle_count(graph: Graph) -> int:
    return sum(
        all(graph[first] >> second & 1 for first, second in combinations(triple, 2))
        for triple in combinations(range(N), 3)
    )


def k4_count(graph: Graph) -> int:
    return sum(
        all(graph[first] >> second & 1 for first, second in combinations(quad, 2))
        for quad in combinations(range(N), 4)
    )


def every_neighborhood_is_a_clique(graph: Graph) -> bool:
    for vertex in range(N):
        neighbors = [other for other in range(N) if graph[vertex] >> other & 1]
        if not all(
            graph[first] >> second & 1
            for first, second in combinations(neighbors, 2)
        ):
            return False
    return True


def enumerate_cubic_types():
    """Complete normalized labeled generation plus exact isomorphism quotient."""

    representatives: list[Graph] = []
    features = []
    class_counts: list[int] = []
    buckets: dict[object, list[int]] = defaultdict(list)
    generated_count = 0

    graph = [0] * N
    for neighbor in (1, 2, 3):
        graph[0] |= 1 << neighbor
        graph[neighbor] |= 1
    remaining = [0, 2, 2, 2, 3, 3, 3, 3, 3, 3]

    def accept() -> None:
        nonlocal generated_count
        generated_count += 1
        candidate = tuple(graph)
        candidate_features = graph_features(candidate)
        for index in buckets[candidate_features[1]]:
            if exact_isomorphism_count(
                candidate,
                candidate_features,
                representatives[index],
                features[index],
                count_all=False,
            ):
                class_counts[index] += 1
                return
        index = len(representatives)
        representatives.append(candidate)
        features.append(candidate_features)
        class_counts.append(1)
        buckets[candidate_features[1]].append(index)

    def visit(start: int = 1) -> None:
        vertex = next(
            (index for index in range(start, N) if remaining[index]),
            None,
        )
        if vertex is None:
            accept()
            return
        needed = remaining[vertex]
        candidates = [
            other
            for other in range(vertex + 1, N)
            if remaining[other] > 0
        ]
        if len(candidates) < needed:
            return
        for chosen in combinations(candidates, needed):
            for other in chosen:
                remaining[other] -= 1
                graph[vertex] |= 1 << other
                graph[other] |= 1 << vertex
            remaining[vertex] = 0
            active = [
                index
                for index in range(vertex + 1, N)
                if remaining[index]
            ]
            feasible = sum(remaining) % 2 == 0 and all(
                remaining[index] <= len(active) - 1 for index in active
            )
            if feasible:
                visit(vertex + 1)
            remaining[vertex] = needed
            for other in chosen:
                remaining[other] += 1
                graph[vertex] &= ~(1 << other)
                graph[other] &= ~(1 << vertex)

    visit()
    if generated_count != 133_105:
        raise AssertionError(f"wrong normalized labeled count {generated_count}")
    if len(representatives) != 21:
        raise AssertionError(f"wrong cubic type count {len(representatives)}")

    records = []
    for index, (representative, representative_features, observed) in enumerate(
        zip(representatives, features, class_counts), start=1
    ):
        automorphisms = int(
            exact_isomorphism_count(
                representative,
                representative_features,
                representative,
                representative_features,
                count_all=True,
            )
        )
        expected = math.factorial(N) // (automorphisms * math.comb(N - 1, 3))
        if observed != expected:
            raise AssertionError(
                f"type {index} has {observed} normalized labels, expected {expected}"
            )
        encoded = graph6(representative)
        if decode_graph6(encoded) != representative:
            raise AssertionError("graph6 round trip failed")
        records.append(
            {
                "type": index,
                "graph6": encoded,
                "edges": [list(edge) for edge in graph_edges(representative)],
                "component_sizes": list(component_sizes(representative)),
                "connected": component_sizes(representative) == (N,),
                "triangle_count": triangle_count(representative),
                "k4_count": k4_count(representative),
                "automorphism_order": automorphisms,
                "normalized_labeled_count": observed,
                "expected_count_43200_over_aut": expected,
            }
        )
    if sum(record["connected"] for record in records) != 19:
        raise AssertionError("wrong connected cubic type count")
    if sum(record["normalized_labeled_count"] for record in records) != 133_105:
        raise AssertionError("cubic class counts do not sum to the generator count")
    return representatives, records


def edge_disjoint_central_sets(cliques):
    answer = []
    selected = []

    def visit(index: int, used_edges: int) -> None:
        if index == len(cliques):
            answer.append((tuple(selected), used_edges))
            return
        visit(index + 1, used_edges)
        point, edge_mask = cliques[index]
        if not used_edges & edge_mask:
            selected.append(point)
            visit(index + 1, used_edges | edge_mask)
            selected.pop()

    visit(0, 0)
    return tuple(answer)


def point_patterns(graph: Graph) -> Iterator[tuple[tuple[Point, ...], tuple[Point, ...]]]:
    """All admissible nontrivial point-cliques plus singleton completion."""

    k_edges = list(graph_edges(graph))
    edge_index = {edge: index for index, edge in enumerate(k_edges)}
    triangles = []
    central_cliques = []
    for point in combinations(range(N), 3):
        edges = tuple(combinations(point, 2))
        if all(edge in edge_index for edge in edges):
            edge_mask = sum(1 << edge_index[edge] for edge in edges)
            triangles.append((point, edge_mask))
            central_cliques.append((point, edge_mask))
    for point in combinations(range(N), 4):
        edges = tuple(combinations(point, 2))
        if all(edge in edge_index for edge in edges):
            central_cliques.append(
                (point, sum(1 << edge_index[edge] for edge in edges))
            )

    all_edges = (1 << 15) - 1
    for central_points, central_mask in edge_disjoint_central_sets(central_cliques):
        available = all_edges ^ central_mask
        selected_edges = available
        while True:
            used_edges = central_mask | selected_edges
            valid = all(
                used_edges & triangle_mask != triangle_mask
                or any(set(triangle) <= set(point) for point in central_points)
                for triangle, triangle_mask in triangles
            )
            if valid:
                nontrivial = list(central_points) + [
                    k_edges[index]
                    for index in range(15)
                    if selected_edges >> index & 1
                ]
                load = [
                    sum(vertex in point for point in nontrivial)
                    for vertex in range(N)
                ]
                if max(load) <= 3:
                    completed = list(nontrivial)
                    for vertex in range(N):
                        completed.extend([(vertex,)] * (3 - load[vertex]))
                    yield tuple(nontrivial), tuple(completed)
            if selected_edges == 0:
                break
            selected_edges = (selected_edges - 1) & available


def build_incidence_instance(graph: Graph, points: tuple[Point, ...]):
    l_edges = [
        edge for edge in combinations(range(N), 2) if edge not in set(graph_edges(graph))
    ]
    if len(l_edges) != 30:
        raise AssertionError("the complement of a cubic order-ten graph needs 30 edges")
    star_masks = [
        sum(1 << index for index, edge in enumerate(l_edges) if vertex in edge)
        for vertex in range(N)
    ]
    point_masks = [sum(1 << vertex for vertex in point) for point in points]
    crossing_cache: dict[tuple[int, int], int] = {}

    def crossing(first: int, second: int) -> int:
        key = tuple(sorted((point_masks[first], point_masks[second])))
        if key not in crossing_cache:
            crossing_cache[key] = sum(
                1 << index
                for index, (left, right) in enumerate(l_edges)
                if (
                    point_masks[first] >> left & 1
                    and point_masks[second] >> right & 1
                )
                or (
                    point_masks[first] >> right & 1
                    and point_masks[second] >> left & 1
                )
            )
        return crossing_cache[key]

    points_at_triangle = [
        [
            point_id
            for point_id, point_mask in enumerate(point_masks)
            if point_mask >> triangle & 1
        ]
        for triangle in range(N)
    ]
    if any(len(point_ids) != 3 for point_ids in points_at_triangle):
        raise AssertionError("singleton completion did not give three points per triangle")

    required: set[tuple[int, int]] = set()
    for point_ids in points_at_triangle:
        for first, second in combinations(point_ids, 2):
            edge_mask = crossing(first, second)
            degree = edge_mask.bit_count()
            # These are forced graph edges because the two points lie in the
            # same active graph-triangle; hence the standard H-degree rule
            # applies to them exactly as to every other graph edge.
            if degree not in NONZERO_H_DEGREES | {0}:
                return None
            if degree:
                if any(
                    (edge_mask & star).bit_count() not in (0, 2)
                    for star in star_masks
                ):
                    return None
                required.add(tuple(sorted((first, second))))

    candidates: list[Candidate] = []
    for first, second in combinations(range(len(points)), 2):
        edge_mask = crossing(first, second)
        degree = edge_mask.bit_count()
        if degree in NONZERO_H_DEGREES and all(
            (edge_mask & star).bit_count() in (0, 2) for star in star_masks
        ):
            candidates.append((first, second, edge_mask, degree))
    return point_masks, tuple(candidates), frozenset(required)


def exhaust_candidate_subsets(instance) -> tuple[int, int, int, int, int]:
    """Exact subset audit through five increasingly strong constraint layers."""

    point_masks, candidates, required = instance
    candidate_count = len(candidates)
    if candidate_count < MANTEL_SUPPORT_MINIMUM:
        return (0, 0, 0, 0, 0)
    candidate_index = {
        (first, second): index
        for index, (first, second, _, _) in enumerate(candidates)
    }
    if any(pair not in candidate_index for pair in required):
        return (0, 0, 0, 0, 0)
    required_mask = sum(1 << candidate_index[pair] for pair in required)
    coverers = [
        sum(
            1 << index
            for index, candidate in enumerate(candidates)
            if candidate[2] >> edge & 1
        )
        for edge in range(30)
    ]
    if any(mask.bit_count() < 2 for mask in coverers):
        return (0, 0, 0, 0, 0)

    matching_forbidden = []
    simplicity_forbidden = []
    adjacency = [0] * candidate_count
    for first, second in combinations(range(candidate_count), 2):
        shared_l_edges = candidates[first][2] & candidates[second][2]
        pair_mask = (1 << first) | (1 << second)
        if shared_l_edges and (
            {candidates[first][0], candidates[first][1]}
            & {candidates[second][0], candidates[second][1]}
        ):
            matching_forbidden.append(pair_mask)
        if shared_l_edges.bit_count() > 1:
            simplicity_forbidden.append(pair_mask)
        if shared_l_edges.bit_count() == 1:
            adjacency[first] |= 1 << second
            adjacency[second] |= 1 << first
    triangle_forbidden = [
        (1 << first) | (1 << second) | (1 << third)
        for first, second, third in combinations(range(candidate_count), 3)
        if adjacency[first] >> second & 1
        and adjacency[first] >> third & 1
        and adjacency[second] >> third & 1
    ]
    incident_candidates = [
        sum(
            1 << index
            for index, candidate in enumerate(candidates)
            if point_id in candidate[:2]
        )
        for point_id in range(len(point_masks))
    ]
    degree_capacity = [14 - 2 * point_mask.bit_count() for point_mask in point_masks]

    degree_sums = [0] * (1 << candidate_count)
    stage_counts = [0] * 5
    for selected in range(1 << candidate_count):
        if selected:
            bit = selected & -selected
            index = bit.bit_length() - 1
            degree_sums[selected] = (
                degree_sums[selected ^ bit] + candidates[index][3]
            )
        if selected & required_mask != required_mask:
            continue
        if degree_sums[selected] != 60:
            continue
        if any((selected & coverer).bit_count() != 2 for coverer in coverers):
            continue
        stage_counts[0] += 1
        if any(selected & forbidden == forbidden for forbidden in matching_forbidden):
            continue
        stage_counts[1] += 1
        if any(selected & forbidden == forbidden for forbidden in simplicity_forbidden):
            continue
        stage_counts[2] += 1
        if any(selected & forbidden == forbidden for forbidden in triangle_forbidden):
            continue
        stage_counts[3] += 1
        if any(
            (selected & incident_candidates[point_id]).bit_count()
            > degree_capacity[point_id]
            for point_id in range(len(point_masks))
        ):
            continue
        stage_counts[4] += 1
    return tuple(stage_counts)


def audit_incidence_type(graph: Graph):
    family_count = 0
    internal_fixed_side_valid = 0
    support_maximum = 0
    candidate_at_least_mantel = 0
    forced_positive_internal_maximum = 0
    exact_stage_solution_counts = [0] * 5
    exact_stage_pattern_counts = [0] * 5

    for _, completed_points in point_patterns(graph):
        family_count += 1
        instance = build_incidence_instance(graph, completed_points)
        if instance is None:
            continue
        internal_fixed_side_valid += 1
        _, candidates, required = instance
        support_maximum = max(support_maximum, len(candidates))
        forced_positive_internal_maximum = max(
            forced_positive_internal_maximum, len(required)
        )
        if len(candidates) < MANTEL_SUPPORT_MINIMUM:
            continue
        candidate_at_least_mantel += 1
        stage_counts = exhaust_candidate_subsets(instance)
        for stage, count in enumerate(stage_counts):
            exact_stage_solution_counts[stage] += count
            exact_stage_pattern_counts[stage] += count > 0

    return {
        "point_family_count": family_count,
        "internal_and_fixed_side_valid_count": internal_fixed_side_valid,
        "locally_admissible_support_maximum": support_maximum,
        "candidate_support_at_least_11_count": candidate_at_least_mantel,
        "forced_positive_internal_edge_maximum": forced_positive_internal_maximum,
        "solution_subsets_by_stage": exact_stage_solution_counts,
        "patterns_with_solution_by_stage": exact_stage_pattern_counts,
    }


def verify_short_proof(records):
    # If x4=0, the fixed-point identity excludes x1.  Enumerate the remaining
    # incidence and K-edge resource equations instead of solving them by hand.
    no_size_four_solutions = []
    for x2 in range(16):
        for x3 in range(11):
            if 2 * x2 + 3 * x3 == 30 and x2 + 3 * x3 <= 15:
                no_size_four_solutions.append((x2, x3))
    if no_size_four_solutions != [(15, 0)]:
        raise AssertionError("unexpected no-size-four point count")

    neighborhood_clique_types = [
        record["type"]
        for record in records
        if every_neighborhood_is_a_clique(decode_graph6(record["graph6"]))
    ]
    if neighborhood_clique_types:
        raise AssertionError("an order-ten cubic graph had every neighborhood a clique")

    k4_types = [record["type"] for record in records if record["k4_count"]]
    if len(k4_types) != 2:
        raise AssertionError("expected the two K4-plus-six-vertex cubic types")
    for type_number in k4_types:
        graph = decode_graph6(records[type_number - 1]["graph6"])
        if component_sizes(graph) not in ((4, 6),):
            raise AssertionError("a cubic K4 was not an isolated component")
        if k4_count(graph) != 1:
            raise AssertionError("unexpected second K4 component")

    return {
        "fixed_point_identity": "sum_{v adjacent u} d_H(uv) = 4 |S_u|",
        "forced_internal_bound": "d_H(uv)=e_L(S_u,S_v)<=2, hence 0",
        "no_size_four_integer_solutions_x2_x3": [
            list(solution) for solution in no_size_four_solutions
        ],
        "cubic_types_with_every_neighborhood_a_clique": neighborhood_clique_types,
        "cubic_types_with_one_K4_component": k4_types,
        "cubic_types_with_two_K4_components": [],
        "verdict": "PASS: the classification-free short contradiction closes n3=30",
    }


def build_certificate(script_hash: str):
    representatives, records = enumerate_cubic_types()
    print(
        "cubic_generation",
        133_105,
        "types",
        len(records),
        "connected",
        sum(record["connected"] for record in records),
        flush=True,
    )

    total_families = 0
    total_valid = 0
    total_mantel_candidates = 0
    for representative, record in zip(representatives, records):
        incidence = audit_incidence_type(representative)
        record.update(incidence)
        total_families += incidence["point_family_count"]
        total_valid += incidence["internal_and_fixed_side_valid_count"]
        total_mantel_candidates += incidence["candidate_support_at_least_11_count"]
        print(
            "type",
            record["type"],
            record["graph6"],
            "families",
            incidence["point_family_count"],
            "valid",
            incidence["internal_and_fixed_side_valid_count"],
            "max_support",
            incidence["locally_admissible_support_maximum"],
            "candidate_ge_11",
            incidence["candidate_support_at_least_11_count"],
            "exact_two",
            incidence["solution_subsets_by_stage"][0],
            flush=True,
        )

    if total_mantel_candidates != 267:
        raise AssertionError(f"wrong qualifying pattern count {total_mantel_candidates}")
    if any(
        any(record["solution_subsets_by_stage"])
        for record in records
    ):
        raise AssertionError("an n3=30 exact-two cover survived")
    if any(record["forced_positive_internal_edge_maximum"] for record in records):
        raise AssertionError("a forced internal active-triangle edge had positive H-degree")

    short_proof = verify_short_proof(records)
    certificate = {
        "format": "conway-n3-30-abstract-incidence-audit-v1",
        "script_sha256": script_hash,
        "scope": "necessary abstract incidence constraints conditional on a putative srg(99,14,1,2)",
        "candidate_support_warning": "candidate pairs are upper-bound possibilities, not actual graph edges; actual selection begins only in the exact-two-cover layer",
        "assumptions": [
            "n3=30 forces ten active q=2 graph-triangles",
            "K is the simple cubic complement of the six-regular active L graph",
            "point sets S_u are K-cliques with edge-disjoint K-edge consumption",
            "every K3 whose three edges are consumed has one common point",
            "each active triangle contains exactly three original graph vertices",
            "d_H(e) is in {0,4,6,8,10,12}",
            "each nonisolated fixed-side H_T vertex has degree two",
            "every L-edge is an N3 and therefore has exactly two cross graph-edges",
            "H is simple and triangle-free",
        ],
        "cubic_generation": {
            "normalization": "N_K(0)={1,2,3}",
            "normalized_labeled_graph_count": 133_105,
            "isomorphism_type_count": 21,
            "connected_type_count": 19,
            "disconnected_type_count": 2,
            "class_count_checksum": "each normalized class count equals 43200/|Aut(K)|",
        },
        "incidence_totals": {
            "point_family_count": total_families,
            "internal_and_fixed_side_valid_count": total_valid,
            "candidate_support_at_least_11_count": total_mantel_candidates,
            "exact_two_cover_solution_count": 0,
            "surviving_type_count": 0,
            "surviving_pattern_count": 0,
        },
        "constraint_stages": [
            "every L-edge covered exactly twice",
            "the two cross edges at each L-edge form a matching",
            "H is simple",
            "H is triangle-free",
            "original graph degree capacity is at most 14",
        ],
        "short_proof_cross_check": short_proof,
        "types": records,
        "verdict": "VERIFIED ABSTRACT CONTRADICTION FOR n3=30; conditional bound advances to n3>=33",
        "limitations": "This is not a Conway-99 existence or nonexistence certificate; it verifies a conditional necessary count bound.",
    }
    return certificate


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", type=Path)
    group.add_argument("--check", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    certificate = build_certificate(script_hash)
    rendered = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print("certificate", args.output)
    elif args.check is not None:
        if args.check.read_bytes() != rendered.encode("utf-8"):
            raise AssertionError("certificate differs from exact regeneration")
        print("certificate_replay PASS")
    else:
        print(rendered, end="")
    print("script_sha256", script_hash)
    print("certificate_sha256", hashlib.sha256(rendered.encode("utf-8")).hexdigest())
    print("PASS n3=30 abstract incidence exclusion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
