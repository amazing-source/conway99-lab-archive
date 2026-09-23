#!/usr/bin/env python3
"""Clean-room Wave 41 all-quotient lift verification.

This module uses only verified Wave 36/38/40 premises.  It does not import,
read, or execute the Wave 41 discovery implementation or report.

The finite target is the complete normalized family of all-222
one-base-triangle quotients.  The checker:

* reconstructs the 4,050-case normalization;
* isolates all ternary-rank-eleven forms;
* proves those forms fibre-coloured isomorphic by an exhaustive 384-map
  stabilizer search;
* derives and exhaustively validates the affine transport of the 18 lift
  bits under every retained isomorphism;
* performs one complete 2^18 lift/rank census, with the other seven censuses
  transferred only after the graph-level transport has been checked; and
* records the exact conditional implication and its scope walls.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


F3 = 3
F7 = 7
FIBRES = 3
QUOTIENT_FIBRE_SIZE = 6
QUOTIENT_SIZE = FIBRES * QUOTIENT_FIBRE_SIZE
CORE_FIBRE_SIZE = 12
CORE_SIZE = FIBRES * CORE_FIBRE_SIZE
BLOCK_SIZE = FIBRES + CORE_SIZE

Pair = tuple[int, int]
Pairing = tuple[Pair, ...]
Graph = tuple[frozenset[int], ...]
HalfEdgeModel = dict[tuple[int, int], tuple[int, int]]


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256_payload(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def all_pairings(points: tuple[int, ...]) -> Iterable[Pairing]:
    """Generate perfect matchings with canonical pair and block order."""

    if not points:
        yield ()
        return
    first = points[0]
    for position in range(1, len(points)):
        partner = points[position]
        rest = points[1:position] + points[position + 1 :]
        for tail in all_pairings(rest):
            yield tuple(sorted(((first, partner),) + tail))


PAIRINGS: tuple[Pairing, ...] = tuple(
    sorted(set(all_pairings(tuple(range(QUOTIENT_FIBRE_SIZE)))))
)
STANDARD_PAIRING: Pairing = ((0, 1), (2, 3), (4, 5))
RELATIVE_REPRESENTATIVES: dict[str, Pairing] = {
    "111": STANDARD_PAIRING,
    "12": ((0, 1), (2, 4), (3, 5)),
    "3": ((0, 2), (1, 4), (3, 5)),
}


def permute_pairing(pairing: Pairing, permutation: Sequence[int]) -> Pairing:
    return tuple(
        sorted(
            tuple(sorted((permutation[left], permutation[right])))
            for left, right in pairing
        )
    )


def standard_pairing_stabilizer() -> tuple[tuple[int, ...], ...]:
    """All 2^3*3! permutations preserving the standard pairing."""

    maps: list[tuple[int, ...]] = []
    for block_order in itertools.permutations(range(3)):
        for swaps in itertools.product(range(2), repeat=3):
            image = [-1] * QUOTIENT_FIBRE_SIZE
            for source_block, target_block in enumerate(block_order):
                source_pair = STANDARD_PAIRING[source_block]
                target_pair = STANDARD_PAIRING[target_block]
                swap = swaps[source_block]
                image[source_pair[0]] = target_pair[swap]
                image[source_pair[1]] = target_pair[1 - swap]
            maps.append(tuple(image))
    return tuple(sorted(set(maps)))


PAIRING_STABILIZER = standard_pairing_stabilizer()


def relative_pairing_type(pairing: Pairing) -> str:
    """Classify the alternating union with the standard matching."""

    adjacency = [set() for _ in range(QUOTIENT_FIBRE_SIZE)]
    for edge in STANDARD_PAIRING + pairing:
        left, right = edge
        adjacency[left].add(right)
        adjacency[right].add(left)
    unseen = set(range(QUOTIENT_FIBRE_SIZE))
    half_lengths: list[int] = []
    while unseen:
        root = min(unseen)
        component = {root}
        stack = [root]
        while stack:
            vertex = stack.pop()
            for neighbor in adjacency[vertex]:
                if neighbor not in component:
                    component.add(neighbor)
                    stack.append(neighbor)
        unseen.difference_update(component)
        half_lengths.append(1 if len(component) == 2 else len(component) // 2)
    key = tuple(sorted(half_lengths))
    return {(1, 1, 1): "111", (1, 2): "12", (3,): "3"}[key]


def pairing_orbit_audit() -> dict[str, object]:
    """Independently prove the three relative-pairing orbits."""

    remaining = set(PAIRINGS)
    orbits: list[set[Pairing]] = []
    while remaining:
        seed = min(remaining)
        orbit = {
            permute_pairing(seed, permutation)
            for permutation in PAIRING_STABILIZER
        }
        if not orbit <= set(PAIRINGS):
            raise AssertionError("pairing stabilizer left pairing universe")
        orbits.append(orbit)
        remaining.difference_update(orbit)

    typed = {
        relative_pairing_type(next(iter(orbit))): orbit for orbit in orbits
    }
    if set(typed) != set(RELATIVE_REPRESENTATIVES):
        raise AssertionError("relative pairing orbit labels are incomplete")
    for label, representative in RELATIVE_REPRESENTATIVES.items():
        if representative not in typed[label]:
            raise AssertionError(f"wrong representative for orbit {label}")
        if {relative_pairing_type(item) for item in typed[label]} != {label}:
            raise AssertionError("one stabilizer orbit has mixed relative type")

    return {
        "six_point_pairings": len(PAIRINGS),
        "standard_pairing_stabilizer_order": len(PAIRING_STABILIZER),
        "relative_orbit_count": len(orbits),
        "relative_orbit_sizes": {
            label: len(typed[label]) for label in ("111", "12", "3")
        },
        "representatives": {
            label: [list(pair) for pair in RELATIVE_REPRESENTATIVES[label]]
            for label in ("111", "12", "3")
        },
        "normalization_completeness": (
            "Fix the 01 block as 3C4.  Its shared-fibre pairing stabilizer "
            "has exactly the three audited orbits 111,12,3.  Relabel fibre "
            "2 to fix the 12-side pairing.  The remaining 20 block is then "
            "specified by independent pairings on fibres 2 and 0 and a "
            "bijection of their three blocks: 15*15*6 in each orbit."
        ),
    }


def add_three_k22_blocks(
    adjacency: list[set[int]],
    left_fibre: int,
    right_fibre: int,
    left_pairing: Pairing,
    right_pairing: Pairing,
    block_map: Sequence[int],
) -> None:
    if sorted(block_map) != [0, 1, 2]:
        raise ValueError("block map is not a permutation")
    for left_block, right_block in enumerate(block_map):
        for left_local in left_pairing[left_block]:
            for right_local in right_pairing[right_block]:
                left = left_fibre * QUOTIENT_FIBRE_SIZE + left_local
                right = right_fibre * QUOTIENT_FIBRE_SIZE + right_local
                if right in adjacency[left]:
                    raise ValueError("parallel quotient edge")
                adjacency[left].add(right)
                adjacency[right].add(left)


def normalized_quotient(
    relative_type: str,
    fibre2_pairing: Pairing,
    fibre0_pairing: Pairing,
    block_map_20: Sequence[int],
) -> Graph:
    adjacency = [set() for _ in range(QUOTIENT_SIZE)]
    add_three_k22_blocks(
        adjacency,
        0,
        1,
        STANDARD_PAIRING,
        STANDARD_PAIRING,
        (0, 1, 2),
    )
    add_three_k22_blocks(
        adjacency,
        1,
        2,
        RELATIVE_REPRESENTATIVES[relative_type],
        STANDARD_PAIRING,
        (0, 1, 2),
    )
    add_three_k22_blocks(
        adjacency,
        2,
        0,
        fibre2_pairing,
        fibre0_pairing,
        block_map_20,
    )
    graph = tuple(frozenset(neighbors) for neighbors in adjacency)
    validate_quotient(graph)
    return graph


def validate_quotient(graph: Graph) -> None:
    if len(graph) != QUOTIENT_SIZE:
        raise ValueError("wrong quotient order")
    for vertex, neighbors in enumerate(graph):
        if vertex in neighbors:
            raise ValueError("quotient loop")
        if len(neighbors) != 4:
            raise ValueError("quotient is not four-regular")
        if any(vertex not in graph[neighbor] for neighbor in neighbors):
            raise ValueError("asymmetric quotient")
        counts = Counter(
            neighbor // QUOTIENT_FIBRE_SIZE for neighbor in neighbors
        )
        own = vertex // QUOTIENT_FIBRE_SIZE
        if counts.get(own, 0) or sorted(counts.values()) != [2, 2]:
            raise ValueError("quotient does not have bidegree 2+2")


def edges(graph: Sequence[Sequence[int]]) -> tuple[Pair, ...]:
    return tuple(
        (left, right)
        for left, neighbors in enumerate(graph)
        for right in sorted(neighbors)
        if left < right
    )


def adjacency_matrix(graph: Sequence[Sequence[int]]) -> list[list[int]]:
    order = len(graph)
    matrix = [[0] * order for _ in range(order)]
    for left, neighbors in enumerate(graph):
        for right in neighbors:
            matrix[left][right] = 1
    return matrix


def dense_rank(matrix: Sequence[Sequence[int]], prime: int) -> int:
    rows = [[value % prime for value in row] for row in matrix]
    if not rows:
        return 0
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next(
            (
                row
                for row in range(pivot_row, len(rows))
                if rows[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = pow(rows[pivot_row][column], -1, prime)
        rows[pivot_row] = [
            (scale * value) % prime for value in rows[pivot_row]
        ]
        for row in range(len(rows)):
            if row == pivot_row:
                continue
            factor = rows[row][column]
            if factor:
                rows[row] = [
                    (left - factor * right) % prime
                    for left, right in zip(rows[row], rows[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def nullspace(matrix: Sequence[Sequence[int]], prime: int) -> list[list[int]]:
    rows = [[value % prime for value in row] for row in matrix]
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next(
            (
                row
                for row in range(pivot_row, len(rows))
                if rows[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = pow(rows[pivot_row][column], -1, prime)
        rows[pivot_row] = [
            (scale * value) % prime for value in rows[pivot_row]
        ]
        for row in range(len(rows)):
            if row != pivot_row and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [
                    (left - factor * right) % prime
                    for left, right in zip(rows[row], rows[pivot_row])
                ]
        pivot_columns.append(column)
        pivot_row += 1
    free_columns = [
        column
        for column in range(len(rows[0]))
        if column not in pivot_columns
    ]
    basis: list[list[int]] = []
    for free in free_columns:
        vector = [0] * len(rows[0])
        vector[free] = 1
        for row, pivot in enumerate(pivot_columns):
            vector[pivot] = (-rows[row][free]) % prime
        basis.append(vector)
    return basis


def quotient_rank_f3(graph: Graph) -> int:
    matrix = adjacency_matrix(graph)
    for vertex in range(len(matrix)):
        matrix[vertex][vertex] = 2
    return dense_rank(matrix, F3)


def quotient_payload(graph: Graph) -> dict[str, object]:
    edge_list = [list(edge) for edge in edges(graph)]
    return {
        "edges": edge_list,
        "sha256": sha256_payload({"edges": edge_list}),
    }


def enumerate_normalized_quotients() -> dict[str, object]:
    rank_distribution: Counter[int] = Counter()
    rank_eleven: dict[tuple[Pair, ...], dict[str, object]] = {}
    raw_rank_eleven_records = 0
    for relative_type in ("111", "12", "3"):
        for fibre2_pairing in PAIRINGS:
            for fibre0_pairing in PAIRINGS:
                for block_map in itertools.permutations(range(3)):
                    graph = normalized_quotient(
                        relative_type,
                        fibre2_pairing,
                        fibre0_pairing,
                        block_map,
                    )
                    rank = quotient_rank_f3(graph)
                    rank_distribution[rank] += 1
                    if rank != 11:
                        continue
                    raw_rank_eleven_records += 1
                    key = edges(graph)
                    rank_eleven.setdefault(
                        key,
                        {
                            "graph": graph,
                            "relative_type": relative_type,
                            "fibre2_pairing": fibre2_pairing,
                            "fibre0_pairing": fibre0_pairing,
                            "block_map_20": tuple(block_map),
                        },
                    )
    if sum(rank_distribution.values()) != 3 * 15 * 15 * 6:
        raise AssertionError("normalized quotient census is incomplete")
    return {
        "rank_distribution": rank_distribution,
        "rank_eleven": [
            rank_eleven[key] for key in sorted(rank_eleven)
        ],
        "raw_rank_eleven_records": raw_rank_eleven_records,
    }


def fixed_01_coloured_automorphisms() -> tuple[tuple[int, ...], ...]:
    """The 384 colour-preserving automorphisms of the fixed 01 block."""

    mappings: list[tuple[int, ...]] = []
    for component_map in itertools.permutations(range(3)):
        for swaps0 in itertools.product(range(2), repeat=3):
            for swaps1 in itertools.product(range(2), repeat=3):
                mapping = list(range(QUOTIENT_SIZE))
                for fibre, swaps in ((0, swaps0), (1, swaps1)):
                    offset = fibre * QUOTIENT_FIBRE_SIZE
                    for source_block, target_block in enumerate(component_map):
                        source_pair = STANDARD_PAIRING[source_block]
                        target_pair = STANDARD_PAIRING[target_block]
                        swap = swaps[source_block]
                        mapping[offset + source_pair[0]] = (
                            offset + target_pair[swap]
                        )
                        mapping[offset + source_pair[1]] = (
                            offset + target_pair[1 - swap]
                        )
                mappings.append(tuple(mapping))
    return tuple(sorted(set(mappings)))


FIXED_01_AUTOMORPHISMS = fixed_01_coloured_automorphisms()


def is_graph_mapping(
    source: Graph, target: Graph, mapping: Sequence[int]
) -> bool:
    if sorted(mapping) != list(range(len(source))):
        return False
    return all(
        {mapping[neighbor] for neighbor in source[vertex]}
        == set(target[mapping[vertex]])
        for vertex in range(len(source))
    )


def find_fibre_coloured_isomorphism(
    source: Graph, target: Graph
) -> tuple[tuple[int, ...], int]:
    """Exhaust the 384 possible maps on fixed fibres 0 and 1.

    Once those two fibre maps are fixed, the candidate images of a fibre-2
    vertex are determined by its two neighbour sets in fibres 0 and 1.
    Twins can occur, so a tiny exact-matching backtrack chooses a bijection
    between equal-signature classes.  This is a complete search because both
    normalized graphs have the same fixed 01 relation.
    """

    signatures: dict[
        tuple[frozenset[int], frozenset[int]], list[int]
    ] = {}
    for vertex in range(2 * QUOTIENT_FIBRE_SIZE, QUOTIENT_SIZE):
        signature = (
            frozenset(
                neighbor
                for neighbor in target[vertex]
                if neighbor // QUOTIENT_FIBRE_SIZE == 0
            ),
            frozenset(
                neighbor
                for neighbor in target[vertex]
                if neighbor // QUOTIENT_FIBRE_SIZE == 1
            ),
        )
        signatures.setdefault(signature, []).append(vertex)

    checked = 0
    for partial in FIXED_01_AUTOMORPHISMS:
        checked += 1
        mapping = list(partial)
        candidates_by_vertex: dict[int, list[int]] = {}
        for vertex in range(2 * QUOTIENT_FIBRE_SIZE, QUOTIENT_SIZE):
            signature = (
                frozenset(
                    partial[neighbor]
                    for neighbor in source[vertex]
                    if neighbor // QUOTIENT_FIBRE_SIZE == 0
                ),
                frozenset(
                    partial[neighbor]
                    for neighbor in source[vertex]
                    if neighbor // QUOTIENT_FIBRE_SIZE == 1
                ),
            )
            candidates = signatures.get(signature, [])
            if not candidates:
                break
            candidates_by_vertex[vertex] = candidates
        if len(candidates_by_vertex) != QUOTIENT_FIBRE_SIZE:
            continue

        order = sorted(
            candidates_by_vertex,
            key=lambda vertex: (len(candidates_by_vertex[vertex]), vertex),
        )

        def complete(position: int, used: set[int]) -> tuple[int, ...] | None:
            if position == len(order):
                candidate = tuple(mapping)
                return (
                    candidate
                    if is_graph_mapping(source, target, candidate)
                    else None
                )
            vertex = order[position]
            for image in candidates_by_vertex[vertex]:
                if image in used:
                    continue
                mapping[vertex] = image
                found = complete(position + 1, used | {image})
                if found is not None:
                    return found
            mapping[vertex] = vertex
            return None

        candidate = complete(0, set())
        if candidate is not None:
            if any(
                vertex // QUOTIENT_FIBRE_SIZE
                != candidate[vertex] // QUOTIENT_FIBRE_SIZE
                for vertex in range(QUOTIENT_SIZE)
            ):
                raise AssertionError("isomorphism changed a fibre colour")
            return candidate, checked
    raise ValueError("no fibre-coloured isomorphism")


def half_edge_model(graph: Graph) -> HalfEdgeModel:
    """Choose a deterministic endpoint gauge at every quotient vertex."""

    model: HalfEdgeModel = {}
    for vertex, neighbors in enumerate(graph):
        other_fibres = sorted(
            {neighbor // QUOTIENT_FIBRE_SIZE for neighbor in neighbors}
        )
        if len(other_fibres) != 2:
            raise ValueError("bad quotient fibre incidence")
        for coefficient, fibre in enumerate(other_fibres):
            selected = sorted(
                neighbor
                for neighbor in neighbors
                if neighbor // QUOTIENT_FIBRE_SIZE == fibre
            )
            if len(selected) != 2:
                raise ValueError("bad half-edge multiplicity")
            model[(vertex, selected[0])] = (0, coefficient)
            model[(vertex, selected[1])] = (1, coefficient)
    return model


def forbidden_triangle_patterns(
    graph: Graph, model: HalfEdgeModel
) -> tuple[tuple[tuple[int, int], ...], ...]:
    patterns: list[tuple[tuple[int, int], ...]] = []
    for left, middle, right in itertools.combinations(range(len(graph)), 3):
        if (
            middle not in graph[left]
            or right not in graph[left]
            or right not in graph[middle]
        ):
            continue
        pattern: list[tuple[int, int]] = []
        for vertex, neighbor_a, neighbor_b in (
            (left, middle, right),
            (middle, left, right),
            (right, left, middle),
        ):
            constant_a, coefficient_a = model[(vertex, neighbor_a)]
            constant_b, coefficient_b = model[(vertex, neighbor_b)]
            if coefficient_a == coefficient_b:
                raise AssertionError("quotient triangle stayed in two fibres")
            pattern.append((vertex, constant_a ^ constant_b))
        patterns.append(tuple(sorted(pattern)))
    return tuple(sorted(patterns))


def triangle_free_from_patterns(
    mask: int, patterns: Sequence[Sequence[tuple[int, int]]]
) -> bool:
    for pattern in patterns:
        if all(((mask >> vertex) & 1) == value for vertex, value in pattern):
            return False
    return True


def lifted_graph(graph: Graph, model: HalfEdgeModel, mask: int) -> Graph:
    adjacency = [set() for _ in range(CORE_SIZE)]
    for quotient_vertex in range(QUOTIENT_SIZE):
        left = 2 * quotient_vertex
        right = left + 1
        adjacency[left].add(right)
        adjacency[right].add(left)
    for left, right in edges(graph):
        left_constant, left_coefficient = model[(left, right)]
        right_constant, right_coefficient = model[(right, left)]
        left_endpoint = left_constant ^ (
            ((mask >> left) & 1) if left_coefficient else 0
        )
        right_endpoint = right_constant ^ (
            ((mask >> right) & 1) if right_coefficient else 0
        )
        lifted_left = 2 * left + left_endpoint
        lifted_right = 2 * right + right_endpoint
        adjacency[lifted_left].add(lifted_right)
        adjacency[lifted_right].add(lifted_left)
    result = tuple(frozenset(neighbors) for neighbors in adjacency)
    if {len(neighbors) for neighbors in result} != {3}:
        raise AssertionError("lift is not cubic")
    return result


def ordinary_triangle_count(graph: Graph) -> int:
    count = 0
    for left in range(len(graph)):
        for middle in graph[left]:
            if left < middle:
                count += len(
                    {
                        right
                        for right in graph[left] & graph[middle]
                        if middle < right
                    }
                )
    return count


def three_i_minus_adjacency(graph: Graph) -> list[list[int]]:
    return [
        [
            (
                3
                if left == right
                else (-1 if right in graph[left] else 0)
            )
            % F7
            for right in range(len(graph))
        ]
        for left in range(len(graph))
    ]


def sparse_symmetric_rank_3i_minus_a(graph: Graph) -> int:
    """Exact sparse symmetric elimination over F7."""

    order = len(graph)
    rows: list[dict[int, int]] = [dict() for _ in range(order)]

    def assign(left: int, right: int, value: int) -> None:
        value %= F7
        if value:
            rows[left][right] = value
            rows[right][left] = value
        else:
            rows[left].pop(right, None)
            rows[right].pop(left, None)

    for vertex in range(order):
        rows[vertex][vertex] = 3
    for left, right in edges(graph):
        assign(left, right, -1)

    active = set(range(order))
    rank = 0
    while active:
        diagonal = [
            vertex for vertex in active if rows[vertex].get(vertex, 0)
        ]
        if diagonal:
            pivot = min(
                diagonal,
                key=lambda vertex: sum(
                    neighbor in active and neighbor != vertex
                    for neighbor in rows[vertex]
                ),
            )
            inverse = pow(rows[pivot][pivot], -1, F7)
            neighbors = sorted(
                neighbor
                for neighbor in rows[pivot]
                if neighbor in active and neighbor != pivot
            )
            for index, left in enumerate(neighbors):
                for right in neighbors[index:]:
                    assign(
                        left,
                        right,
                        rows[left].get(right, 0)
                        - rows[left][pivot]
                        * inverse
                        * rows[pivot][right],
                    )
            for neighbor in list(rows[pivot]):
                if neighbor != pivot:
                    rows[neighbor].pop(pivot, None)
            rows[pivot].clear()
            active.remove(pivot)
            rank += 1
            continue

        pivot = min(active)
        partners = sorted(
            neighbor
            for neighbor in rows[pivot]
            if neighbor in active and neighbor != pivot
        )
        if not partners:
            rows[pivot].clear()
            active.remove(pivot)
            continue
        partner = partners[0]
        inverse = pow(rows[pivot][partner], -1, F7)
        remainder = sorted(
            ((set(rows[pivot]) | set(rows[partner])) & active)
            - {pivot, partner}
        )
        for index, left in enumerate(remainder):
            for right in remainder[index:]:
                correction = inverse * (
                    rows[left].get(pivot, 0)
                    * rows[partner].get(right, 0)
                    + rows[left].get(partner, 0)
                    * rows[pivot].get(right, 0)
                )
                assign(
                    left,
                    right,
                    rows[left].get(right, 0) - correction,
                )
        for removed in (pivot, partner):
            for neighbor in list(rows[removed]):
                if neighbor != removed:
                    rows[neighbor].pop(removed, None)
            rows[removed].clear()
            active.remove(removed)
        rank += 2
    return rank


def transported_k39(core: Graph) -> list[list[int]]:
    """Build (J-I-2A)[T union X] modulo seven."""

    graph = [set() for _ in range(BLOCK_SIZE)]
    for left, right in itertools.combinations(range(3), 2):
        graph[left].add(right)
        graph[right].add(left)
    for fibre in range(3):
        for local in range(CORE_FIBRE_SIZE):
            core_vertex = 3 + fibre * CORE_FIBRE_SIZE + local
            graph[fibre].add(core_vertex)
            graph[core_vertex].add(fibre)
    for left, right in edges(core):
        graph[3 + left].add(3 + right)
        graph[3 + right].add(3 + left)
    return [
        [
            (
                0
                if left == right
                else (6 if right in graph[left] else 1)
            )
            for right in range(BLOCK_SIZE)
        ]
        for left in range(BLOCK_SIZE)
    ]


def edge_local_type(core: Graph, fibre_a: int, fibre_b: int) -> list[int]:
    allowed = {
        fibre * CORE_FIBRE_SIZE + local
        for fibre in (fibre_a, fibre_b)
        for local in range(CORE_FIBRE_SIZE)
    }
    unseen = set(allowed)
    parts: list[int] = []
    while unseen:
        root = min(unseen)
        component = {root}
        stack = [root]
        while stack:
            vertex = stack.pop()
            for neighbor in core[vertex]:
                if neighbor in allowed and neighbor not in component:
                    component.add(neighbor)
                    stack.append(neighbor)
        unseen.difference_update(component)
        if len(component) % 4:
            raise AssertionError("edge-local cycle is not a multiple of four")
        parts.append(len(component) // 4)
    return sorted(parts)


def witness_payload(mask: int, core: Graph) -> dict[str, object]:
    edge_list = [list(edge) for edge in edges(core)]
    core_rank = dense_rank(three_i_minus_adjacency(core), F7)
    block_rank = dense_rank(transported_k39(core), F7)
    return {
        "mask": mask,
        "mask_bits_vertex_0_first": [
            (mask >> vertex) & 1 for vertex in range(QUOTIENT_SIZE)
        ],
        "core_edges": edge_list,
        "core_edges_sha256": sha256_payload({"edges": edge_list}),
        "core_order": len(core),
        "core_edge_count": len(edge_list),
        "core_degree_set": sorted({len(neighbors) for neighbors in core}),
        "core_triangle_count": ordinary_triangle_count(core),
        "base_edge_types": {
            "01": edge_local_type(core, 0, 1),
            "12": edge_local_type(core, 1, 2),
            "20": edge_local_type(core, 2, 0),
        },
        "rank_F7_3I_minus_A_core": core_rank,
        "rank_F7_K39": block_rank,
    }


def exhaustive_canonical_lift_census(
    graph: Graph,
) -> tuple[dict[str, object], bytearray, dict[int, tuple[int, Graph]]]:
    model = half_edge_model(graph)
    patterns = forbidden_triangle_patterns(graph, model)
    accepted = bytearray(1 << QUOTIENT_SIZE)
    distribution: Counter[int] = Counter()
    first_by_rank: dict[int, tuple[int, Graph]] = {}
    triangle_free_count = 0
    dense_crosschecks = 0
    block_identity_crosschecks = 0
    for mask in range(1 << QUOTIENT_SIZE):
        if not triangle_free_from_patterns(mask, patterns):
            continue
        accepted[mask] = 1
        triangle_free_count += 1
        core = lifted_graph(graph, model, mask)
        if ordinary_triangle_count(core):
            raise AssertionError("affine triangle filter accepted a triangle")
        rank = sparse_symmetric_rank_3i_minus_a(core)
        distribution[rank] += 1
        first_by_rank.setdefault(rank, (mask, core))
        if triangle_free_count % 4096 == 0:
            if rank != dense_rank(three_i_minus_adjacency(core), F7):
                raise AssertionError("sparse/dense ranks disagree")
            dense_crosschecks += 1
        if triangle_free_count % 8192 == 0:
            block_rank = dense_rank(transported_k39(core), F7)
            if block_rank != rank + 1:
                raise AssertionError("K39 rank identity failed")
            block_identity_crosschecks += 1

    for rank, (_, core) in sorted(first_by_rank.items()):
        dense = dense_rank(three_i_minus_adjacency(core), F7)
        block = dense_rank(transported_k39(core), F7)
        if dense != rank or block != rank + 1:
            raise AssertionError("rank witness crosscheck failed")
        dense_crosschecks += 1
        block_identity_crosschecks += 1

    rejected_controls = 0
    for mask in range(0, 1 << QUOTIENT_SIZE, 4093):
        core = lifted_graph(graph, model, mask)
        direct_free = ordinary_triangle_count(core) == 0
        affine_free = triangle_free_from_patterns(mask, patterns)
        if direct_free != affine_free:
            raise AssertionError("triangle filter disagrees with direct graph")
        rejected_controls += int(not direct_free)

    witnesses = {
        str(rank): witness_payload(mask, core)
        for rank, (mask, core) in sorted(first_by_rank.items())
    }
    result = {
        "relative_endpoint_bits": QUOTIENT_SIZE,
        "mask_count": 1 << QUOTIENT_SIZE,
        "quotient_triangle_count": len(patterns),
        "triangle_free_mask_count": triangle_free_count,
        "rank_F7_3I_minus_A_core_distribution": {
            str(rank): count for rank, count in sorted(distribution.items())
        },
        "rank_F7_K39_distribution": {
            str(rank + 1): count
            for rank, count in sorted(distribution.items())
        },
        "dense_rank_crosschecks": dense_crosschecks,
        "K39_identity_crosschecks": block_identity_crosschecks,
        "rejected_mask_direct_triangle_controls": rejected_controls,
        "canonical_first_witness_by_core_rank": witnesses,
    }
    return result, accepted, first_by_rank


def derive_affine_transport(
    source: Graph, target: Graph, mapping: Sequence[int]
) -> dict[str, object]:
    """Derive the target mask and endpoint gauges from a quotient isomorphism."""

    source_model = half_edge_model(source)
    target_model = half_edge_model(target)
    endpoint_swap = [0] * QUOTIENT_SIZE
    affine_xor = [0] * QUOTIENT_SIZE

    for source_vertex in range(QUOTIENT_SIZE):
        target_vertex = mapping[source_vertex]
        source_half_edges = sorted(source[source_vertex])
        anchor = next(
            neighbor
            for neighbor in source_half_edges
            if source_model[(source_vertex, neighbor)][1] == 0
        )
        source_constant, source_coefficient = source_model[
            (source_vertex, anchor)
        ]
        target_constant, target_coefficient = target_model[
            (target_vertex, mapping[anchor])
        ]
        if source_coefficient != 0 or target_coefficient != 0:
            raise AssertionError("isomorphism changed anchor fibre")
        endpoint_swap[source_vertex] = source_constant ^ target_constant

        alpha: int | None = None
        for source_neighbor in source_half_edges:
            source_constant, source_coefficient = source_model[
                (source_vertex, source_neighbor)
            ]
            target_constant, target_coefficient = target_model[
                (target_vertex, mapping[source_neighbor])
            ]
            if source_coefficient != target_coefficient:
                raise AssertionError("mask coefficient changed")
            residual = (
                source_constant
                ^ endpoint_swap[source_vertex]
                ^ target_constant
            )
            if source_coefficient == 0:
                if residual:
                    raise AssertionError("anchor endpoint gauge inconsistent")
            elif alpha is None:
                alpha = residual
            elif alpha != residual:
                raise AssertionError("non-affine endpoint transport")
        if alpha is None:
            raise AssertionError("missing variable half-edge")
        affine_xor[source_vertex] = alpha

    xor_mask = sum(
        affine_xor[source_vertex] << mapping[source_vertex]
        for source_vertex in range(QUOTIENT_SIZE)
    )
    return {
        "vertex_permutation_source_to_target": list(mapping),
        "source_endpoint_swaps": endpoint_swap,
        "source_bit_affine_xors": affine_xor,
        "target_xor_mask": xor_mask,
        "directed_half_edges_checked": sum(len(row) for row in source),
    }


def transport_mask(
    source_mask: int, mapping: Sequence[int], affine_xors: Sequence[int]
) -> int:
    target_mask = 0
    for source_vertex in range(QUOTIENT_SIZE):
        bit = ((source_mask >> source_vertex) & 1) ^ affine_xors[source_vertex]
        target_mask |= bit << mapping[source_vertex]
    return target_mask


def lifted_vertex_mapping(
    quotient_mapping: Sequence[int], endpoint_swaps: Sequence[int]
) -> tuple[int, ...]:
    return tuple(
        2 * quotient_mapping[source_vertex]
        + (source_endpoint ^ endpoint_swaps[source_vertex])
        for source_vertex in range(QUOTIENT_SIZE)
        for source_endpoint in range(2)
    )


def validate_all_transports(
    rank_eleven_records: Sequence[dict[str, object]],
    canonical_index: int,
    accepted_source: bytearray,
    first_by_rank: dict[int, tuple[int, Graph]],
    rank_distribution: dict[str, int],
) -> tuple[list[dict[str, object]], int]:
    source = rank_eleven_records[canonical_index]["graph"]
    assert isinstance(source, tuple)
    source_patterns = forbidden_triangle_patterns(source, half_edge_model(source))
    quotient_results: list[dict[str, object]] = []
    total_stabilizer_maps_checked = 0

    for index, record in enumerate(rank_eleven_records):
        target = record["graph"]
        assert isinstance(target, tuple)
        if index == canonical_index:
            mapping = tuple(range(QUOTIENT_SIZE))
            maps_checked = 1
        else:
            mapping, maps_checked = find_fibre_coloured_isomorphism(
                source, target
            )
        total_stabilizer_maps_checked += maps_checked
        if not is_graph_mapping(source, target, mapping):
            raise AssertionError("retained quotient map is not an isomorphism")

        affine = derive_affine_transport(source, target, mapping)
        affine_xors = affine["source_bit_affine_xors"]
        endpoint_swaps = affine["source_endpoint_swaps"]
        assert isinstance(affine_xors, list)
        assert isinstance(endpoint_swaps, list)
        target_patterns = forbidden_triangle_patterns(
            target, half_edge_model(target)
        )

        transported_targets = bytearray(1 << QUOTIENT_SIZE)
        target_free_count = 0
        for source_mask in range(1 << QUOTIENT_SIZE):
            target_mask = transport_mask(source_mask, mapping, affine_xors)
            source_free = bool(accepted_source[source_mask])
            target_free = triangle_free_from_patterns(
                target_mask, target_patterns
            )
            if source_free != target_free:
                raise AssertionError("affine mask map changed triangle status")
            transported_targets[target_mask] = 1
            target_free_count += int(target_free)
        if sum(transported_targets) != len(transported_targets):
            raise AssertionError("affine mask map is not bijective")

        core_mapping = lifted_vertex_mapping(mapping, endpoint_swaps)
        graph_transport_checks = 0
        target_model = half_edge_model(target)
        for _, (source_mask, source_core) in sorted(first_by_rank.items()):
            target_mask = transport_mask(source_mask, mapping, affine_xors)
            target_core = lifted_graph(target, target_model, target_mask)
            if not is_graph_mapping(source_core, target_core, core_mapping):
                raise AssertionError("affine map failed at lifted-graph level")
            graph_transport_checks += 1

        payload = quotient_payload(target)
        quotient_results.append(
            {
                "normalized_index": index,
                "quotient_sha256": payload["sha256"],
                "normalization_record": {
                    "relative_type": record["relative_type"],
                    "fibre2_pairing": [
                        list(pair) for pair in record["fibre2_pairing"]
                    ],
                    "fibre0_pairing": [
                        list(pair) for pair in record["fibre0_pairing"]
                    ],
                    "block_map_20": list(record["block_map_20"]),
                },
                "rank_F3_2I_plus_A": quotient_rank_f3(target),
                "fibre_coloured_isomorphism": {
                    "preserves_each_fibre": True,
                    "fixed_01_stabilizer_maps_checked_before_witness": (
                        maps_checked
                    ),
                    **affine,
                    "all_masks_triangle_status_checked": 1 << QUOTIENT_SIZE,
                    "rank_witness_graph_transports_checked": (
                        graph_transport_checks
                    ),
                },
                "lift_census": {
                    "mask_count": 1 << QUOTIENT_SIZE,
                    "quotient_triangle_count": len(target_patterns),
                    "triangle_free_mask_count": target_free_count,
                    "rank_F7_K39_distribution": dict(rank_distribution),
                    "rank_distribution_transfer": (
                        "Exact graph isomorphism for every affine mask; ranks "
                        "are invariant under the emitted vertex permutation."
                    ),
                },
            }
        )
    return quotient_results, total_stabilizer_maps_checked


def mat_vec(
    matrix: Sequence[Sequence[int]], vector: Sequence[int], prime: int
) -> list[int]:
    return [
        sum(left * right for left, right in zip(row, vector)) % prime
        for row in matrix
    ]


def structural_kernel_scope_guard(
    minimum_rank_core: Graph,
) -> dict[str, object]:
    """Reject a false rank-45 promotion from the local rank-33 witness."""

    block = transported_k39(minimum_rank_core)
    rank = dense_rank(block, F7)
    kernel = nullspace(block, F7)
    structural: list[list[int]] = []
    for fibre in range(3):
        vector = [1, 1, 1] + [0] * CORE_SIZE
        vector[fibre] = 4
        for local in range(CORE_FIBRE_SIZE):
            vector[3 + fibre * CORE_FIBRE_SIZE + local] = 1
        if any(mat_vec(block, vector, F7)):
            raise AssertionError("structural fibre vector left K39 kernel")
        structural.append(vector)
    if dense_rank(structural, F7) != 3:
        raise AssertionError("structural kernel vectors are dependent")

    # A legal outside vertex is nonadjacent to the three base vertices and
    # adjacent to exactly two points in every 12-fibre.  In a K column this is
    # 1 on T, and in each fibre ten 1s plus two -1s.
    outside_columns_checked = 0
    for fibre, vector in enumerate(structural):
        for chosen in itertools.combinations(range(CORE_FIBRE_SIZE), 2):
            column = [1, 1, 1] + [1] * CORE_SIZE
            for local in chosen:
                column[3 + fibre * CORE_FIBRE_SIZE + local] = 6
            dot = sum(
                left * right for left, right in zip(vector, column)
            ) % F7
            if dot:
                raise AssertionError("legal outside column sees structural radical")
            outside_columns_checked += 1

    if rank != 33 or len(kernel) != 6:
        raise AssertionError("scope guard requires the rank-33 witness")
    return {
        "rank_F7_K39": rank,
        "K39_nullity": len(kernel),
        "structural_kernel_dimension": 3,
        "structural_vectors": structural,
        "legal_outside_column_components_checked": outside_columns_checked,
        "orthogonality_formula": "6+(10-2)=14=0 mod 7",
        "outside_projection_rank_upper_bound_on_full_K39_kernel": 3,
        "blocked_inflation": (
            "The arbitrary-border lemma cannot add 2*6 to this rank-33 "
            "block: a three-dimensional structural subspace of its "
            "six-dimensional kernel is annihilated by every legal outside "
            "column.  This blocks a rank-45 promotion by that route; it does "
            "not weaken the local rank-33 lower bound."
        ),
    }


def build_results() -> dict[str, object]:
    orbit_audit = pairing_orbit_audit()
    if len(PAIRINGS) != 15 or len(PAIRING_STABILIZER) != 48:
        raise AssertionError("pairing normalization constants changed")
    if len(FIXED_01_AUTOMORPHISMS) != 384:
        raise AssertionError("fixed 01 coloured automorphism count changed")

    enumeration = enumerate_normalized_quotients()
    rank_distribution = enumeration["rank_distribution"]
    rank_eleven = enumeration["rank_eleven"]
    if not isinstance(rank_distribution, Counter):
        raise AssertionError("internal rank distribution type changed")
    if not isinstance(rank_eleven, list):
        raise AssertionError("internal boundary list type changed")
    if enumeration["raw_rank_eleven_records"] != len(rank_eleven):
        raise AssertionError("rank-eleven normalization produced duplicates")
    if not rank_eleven:
        raise AssertionError("no rank-eleven quotient")

    canonical_index = 0
    canonical_graph = rank_eleven[canonical_index]["graph"]
    assert isinstance(canonical_graph, tuple)
    census, accepted, first_by_rank = exhaustive_canonical_lift_census(
        canonical_graph
    )
    k39_distribution = census["rank_F7_K39_distribution"]
    assert isinstance(k39_distribution, dict)
    quotient_results, stabilizer_maps_checked = validate_all_transports(
        rank_eleven,
        canonical_index,
        accepted,
        first_by_rank,
        k39_distribution,
    )
    minimum_core_rank = min(first_by_rank)
    minimum_mask, minimum_core = first_by_rank[minimum_core_rank]
    minimum_witness = witness_payload(minimum_mask, minimum_core)
    scope_guard = structural_kernel_scope_guard(minimum_core)

    exact_rank_distribution = {
        str(rank): count for rank, count in sorted(rank_distribution.items())
    }
    quotient_hashes = [
        item["quotient_sha256"] for item in quotient_results
    ]
    if len(set(quotient_hashes)) != len(quotient_hashes):
        raise AssertionError("rank-eleven normalized forms are not distinct")

    minimum_k39_rank = min(map(int, k39_distribution))
    conditional_theorem = {
        "premises": [
            "A hypothetical srg(99,14,1,2) is at n3=4158.",
            "r3=rank_F3(M)=12.",
            "Every graph edge has local type 2+2+2.",
        ],
        "deduction": [
            (
                "For every base triangle T, the verified Wave 38 contraction "
                "gives rank_F3(P_T-I)<=rank_F3(C+J)=r3-1=11."
            ),
            (
                "All-222 makes P_T one of the complete 4,050 normalized "
                "quotients.  Their minimum ternary rank is 11, so P_T is "
                "one of exactly eight rank-eleven normalized forms."
            ),
            (
                "The eight forms are one fibre-coloured isomorphism class. "
                "The complete 18-bit lift space is transported affinely, "
                "preserving triangle status and the lifted graph."
            ),
            (
                f"Every triangle-free lift has rank_F7(K39)>="
                f"{minimum_k39_rank}."
            ),
            (
                "K39 is a principal block of K=N M N^T and the verified "
                "rank transfer gives rank_F7(K)=rank_F7(M)=r7."
            ),
            (
                "The verified endpoint index condition gives r3+r7 even; "
                "with r3=12, r7 is even."
            ),
        ],
        "conclusion": {
            "every_base_triangle_K39_rank_at_least": minimum_k39_rank,
            "conditional_r7_lower_bound_before_parity": minimum_k39_rank,
            "conditional_r7_lower_bound_after_parity": (
                minimum_k39_rank
                if minimum_k39_rank % 2 == 0
                else minimum_k39_rank + 1
            ),
        },
    }

    return {
        "format": "wave41-allquotient-lifts-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED_CONDITIONAL",
        "scope": (
            "Conditional on n3=4158, r3=12, and every edge having local "
            "type 2+2+2: complete normalized quotient classification, all "
            "relative 18-bit triangle-free lifts, their K39 ranks, and the "
            "resulting characteristic-seven rank floor."
        ),
        "normalization": {
            **orbit_audit,
            "normalized_representative_count": 3 * 15 * 15 * 6,
            "matrix": "2I+A_Q=P_T-I over F_3",
            "rank_distribution": exact_rank_distribution,
            "rank_eleven_raw_record_count": enumeration[
                "raw_rank_eleven_records"
            ],
            "rank_eleven_distinct_quotient_count": len(rank_eleven),
        },
        "fibre_coloured_isomorphism_classification": {
            "meaning_of_coloured": (
                "Each of the three six-vertex fibres is preserved setwise "
                "and keeps its own colour; fibre permutations are not used."
            ),
            "fixed_01_coloured_automorphism_group_order": len(
                FIXED_01_AUTOMORPHISMS
            ),
            "rank_eleven_quotients": len(rank_eleven),
            "isomorphism_classes": 1,
            "stabilizer_maps_checked_until_witnesses": stabilizer_maps_checked,
            "canonical_quotient_sha256": quotient_payload(canonical_graph)[
                "sha256"
            ],
            "records": quotient_results,
        },
        "canonical_exhaustive_lift_census": census,
        "rank_identity": {
            "statement": (
                "rank_F7((J-I-2A)[T union N(T)])="
                "1+rank_F7(3I-A_core)"
            ),
            "derivation": [
                "The T block I-J_3 is invertible over F_7.",
                (
                    "After its Schur complement, the fibre-indicator "
                    "three-space is killed and the 33-dimensional fibre-sum "
                    "kernel carries 2(3I-A_core)."
                ),
                (
                    "The quotient action of 3I-A_core on the three fibre "
                    "indicators has rank two, giving the exact one-rank shift."
                ),
            ],
            "minimum_witness": minimum_witness,
        },
        "conditional_theorem": conditional_theorem,
        "hostile_scope_guard": scope_guard,
        "status_wall": {
            "conditional_all_222_r3_12_rank_floor": "VERIFIED",
            "endpoint_n3_4158": "UNKNOWN",
            "all_edges_222": "ASSUMPTION_NOT_PROVED",
            "r3_equals_12": "ASSUMPTION_NOT_PROVED",
            "endpoint_excluded": False,
            "general_upper_bound_below_4158": "NOT_PROVED",
            "graph_or_counterexample": "NONE",
            "outside_60_vertex_completion": "NOT_CHECKED",
            "cross_triangle_compatibility": "NOT_CHECKED",
            "novelty_or_priority": "UNKNOWN",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    encoded = canonical_bytes(build_results())
    if arguments.verify is not None:
        if arguments.verify.read_bytes() != encoded:
            print(f"FAIL: {arguments.verify} differs", file=sys.stderr)
            return 1
        print(f"PASS: {arguments.verify} matches exact regeneration")
        return 0
    if arguments.output is not None:
        arguments.output.write_bytes(encoded)
        print(arguments.output)
        return 0
    sys.stdout.buffer.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
