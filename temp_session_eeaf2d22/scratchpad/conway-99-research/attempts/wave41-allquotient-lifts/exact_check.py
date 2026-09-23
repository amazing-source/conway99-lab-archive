#!/usr/bin/env python3
"""Exact Wave 41 census of the rank-eleven all-222 quotient lifts.

This is a finite one-triangle relaxation.  It does not construct the sixty
outside vertices, a simultaneous block design, or an srg(99,14,1,2).
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

FORMAT = "wave41-allquotient-lifts-v1"
FROZEN_COMMIT = "4f1754a28723a8e0e4ea3025312cd264b1b117d2"
FIELD_THREE = 3
FIELD_SEVEN = 7
FIBRES = 3
LABELS = 6
QUOTIENT_VERTICES = FIBRES * LABELS
LIFT_VERTICES = 2 * QUOTIENT_VERTICES
MASK_COUNT = 1 << QUOTIENT_VERTICES

Pair = tuple[int, int]
Pairing = tuple[Pair, ...]
Quotient = tuple[tuple[int, ...], ...]

BASE_PAIRING: Pairing = ((0, 1), (2, 3), (4, 5))
RELATIVE_REPRESENTATIVES: tuple[tuple[str, Pairing], ...] = (
    ("aligned_222", BASE_PAIRING),
    ("share_one_24", ((0, 1), (2, 4), (3, 5))),
    ("six_cycle_6", ((0, 2), (1, 4), (3, 5))),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def perfect_matchings(items: tuple[int, ...]) -> Iterable[Pairing]:
    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        second = items[index]
        rest = items[1:index] + items[index + 1 :]
        for tail in perfect_matchings(rest):
            yield tuple(sorted(((first, second),) + tail))


PAIRINGS: tuple[Pairing, ...] = tuple(
    sorted(set(perfect_matchings(tuple(range(LABELS)))))
)
PERMUTATIONS: tuple[tuple[int, ...], ...] = tuple(
    itertools.permutations(range(LABELS))
)


def empty_adjacency(size: int) -> list[set[int]]:
    return [set() for _ in range(size)]


def add_three_squares(
    adjacency: list[set[int]],
    left_fibre: int,
    right_fibre: int,
    left_pairing: Pairing,
    right_pairing: Pairing,
    block_permutation: Sequence[int],
) -> None:
    require(sorted(block_permutation) == [0, 1, 2], "bad block permutation")
    for left_block, right_block in enumerate(block_permutation):
        for left in left_pairing[left_block]:
            for right in right_pairing[right_block]:
                u = LABELS * left_fibre + left
                v = LABELS * right_fibre + right
                require(v not in adjacency[u], "parallel quotient edge")
                adjacency[u].add(v)
                adjacency[v].add(u)


def make_quotient(
    relative_orbit: str,
    fibre2_pairing: Pairing,
    fibre0_pairing: Pairing,
    block_permutation: Sequence[int],
) -> Quotient:
    relative = dict(RELATIVE_REPRESENTATIVES)[relative_orbit]
    adjacency = empty_adjacency(QUOTIENT_VERTICES)
    add_three_squares(
        adjacency, 0, 1, BASE_PAIRING, BASE_PAIRING, (0, 1, 2)
    )
    add_three_squares(
        adjacency, 1, 2, relative, BASE_PAIRING, (0, 1, 2)
    )
    add_three_squares(
        adjacency,
        2,
        0,
        fibre2_pairing,
        fibre0_pairing,
        block_permutation,
    )
    require(set(map(len, adjacency)) == {4}, "quotient is not four-regular")
    return tuple(tuple(sorted(neighbors)) for neighbors in adjacency)


def adjacency_matrix(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    matrix = [[0] * len(adjacency) for _ in adjacency]
    for left, neighbors in enumerate(adjacency):
        for right in neighbors:
            matrix[left][right] = 1
    return matrix


def matrix_rank(matrix: Sequence[Sequence[int]], prime: int) -> int:
    rows = [[entry % prime for entry in row] for row in matrix]
    if not rows:
        return 0
    rank = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [(inverse * entry) % prime for entry in rows[rank]]
        for row in range(rank + 1, len(rows)):
            factor = rows[row][column]
            if factor:
                rows[row] = [
                    (left - factor * right) % prime
                    for left, right in zip(rows[row], rows[rank])
                ]
        rank += 1
    return rank


def quotient_rank(quotient: Quotient) -> int:
    matrix = adjacency_matrix(quotient)
    for index in range(len(matrix)):
        matrix[index][index] = 2
    return matrix_rank(matrix, FIELD_THREE)


def quotient_edges(quotient: Quotient) -> tuple[Pair, ...]:
    return tuple(
        (left, right)
        for left, neighbors in enumerate(quotient)
        for right in neighbors
        if left < right
    )


def half_edge_assignments(
    quotient: Quotient,
) -> dict[Pair, tuple[int, int]]:
    """Encode the endpoint convention by (constant, mask coefficient)."""

    assignments: dict[Pair, tuple[int, int]] = {}
    for vertex, neighbors in enumerate(quotient):
        other_fibres = sorted({neighbor // LABELS for neighbor in neighbors})
        require(len(other_fibres) == 2, "bad quotient fibre incidence")
        for coefficient, fibre in enumerate(other_fibres):
            fibre_neighbors = sorted(
                neighbor for neighbor in neighbors if neighbor // LABELS == fibre
            )
            require(len(fibre_neighbors) == 2, "quotient bidegree is not two")
            for constant, neighbor in enumerate(fibre_neighbors):
                assignments[(vertex, neighbor)] = (constant, coefficient)
    return assignments


def triangle_clauses(
    quotient: Quotient,
) -> tuple[tuple[tuple[int, int], ...], ...]:
    """Return the forbidden three-bit assignment for each quotient triangle."""

    assignments = half_edge_assignments(quotient)
    clauses: list[tuple[tuple[int, int], ...]] = []
    for vertices in itertools.combinations(range(QUOTIENT_VERTICES), 3):
        left, middle, right = vertices
        if not (
            middle in quotient[left]
            and right in quotient[left]
            and right in quotient[middle]
        ):
            continue
        requirements: list[tuple[int, int]] = []
        for vertex, first, second in (
            (left, middle, right),
            (middle, left, right),
            (right, left, middle),
        ):
            c1, a1 = assignments[(vertex, first)]
            c2, a2 = assignments[(vertex, second)]
            require(a1 != a2, "triangle failed to use both other fibres")
            requirements.append((vertex, c1 ^ c2))
        clauses.append(tuple(requirements))
    return tuple(clauses)


def variable_value_bitsets() -> tuple[tuple[int, int], ...]:
    """Bitset masks for all 2^18 Boolean assignments."""

    all_assignments = (1 << MASK_COUNT) - 1
    result: list[tuple[int, int]] = []
    byte_count = MASK_COUNT // 8
    for variable in range(QUOTIENT_VERTICES):
        one_bytes = bytearray(byte_count)
        for assignment in range(MASK_COUNT):
            if (assignment >> variable) & 1:
                one_bytes[assignment >> 3] |= 1 << (assignment & 7)
        ones = int.from_bytes(one_bytes, "little")
        result.append((all_assignments ^ ones, ones))
    return tuple(result)


VARIABLE_VALUE_BITS = variable_value_bitsets()
ALL_ASSIGNMENTS = (1 << MASK_COUNT) - 1


def allowed_assignment_bitset(
    clauses: Sequence[Sequence[tuple[int, int]]],
) -> int:
    allowed = ALL_ASSIGNMENTS
    for clause in clauses:
        forbidden = ALL_ASSIGNMENTS
        for variable, value in clause:
            forbidden &= VARIABLE_VALUE_BITS[variable][value]
        allowed &= ALL_ASSIGNMENTS ^ forbidden
    return allowed


def lifted_adjacency(
    quotient: Quotient,
    mask: int,
) -> list[set[int]]:
    assignments = half_edge_assignments(quotient)
    adjacency = empty_adjacency(LIFT_VERTICES)
    for pair_vertex in range(QUOTIENT_VERTICES):
        left, right = 2 * pair_vertex, 2 * pair_vertex + 1
        adjacency[left].add(right)
        adjacency[right].add(left)
    for left, right in quotient_edges(quotient):
        left_constant, left_coefficient = assignments[(left, right)]
        right_constant, right_coefficient = assignments[(right, left)]
        left_endpoint = left_constant ^ (
            ((mask >> left) & 1) if left_coefficient else 0
        )
        right_endpoint = right_constant ^ (
            ((mask >> right) & 1) if right_coefficient else 0
        )
        u = 2 * left + left_endpoint
        v = 2 * right + right_endpoint
        require(v not in adjacency[u], "parallel lifted edge")
        adjacency[u].add(v)
        adjacency[v].add(u)
    require(set(map(len, adjacency)) == {3}, "lift is not cubic")
    return adjacency


INVERSES_MOD_SEVEN = (0, 1, 4, 5, 2, 3, 6)


def sparse_laplacian_rank(adjacency: Sequence[Sequence[int]]) -> int:
    """Exact symmetric-congruence rank of 3I-A over F7."""

    rows: list[dict[int, int]] = [dict() for _ in adjacency]

    def set_symmetric(left: int, right: int, value: int) -> None:
        reduced = value % FIELD_SEVEN
        if reduced:
            rows[left][right] = reduced
            rows[right][left] = reduced
        else:
            rows[left].pop(right, None)
            rows[right].pop(left, None)

    for vertex in range(len(adjacency)):
        rows[vertex][vertex] = 3
    for left, neighbors in enumerate(adjacency):
        for right in neighbors:
            if left < right:
                set_symmetric(left, right, -1)

    active = set(range(len(adjacency)))
    rank = 0
    while active:
        diagonal = [v for v in active if rows[v].get(v, 0)]
        if diagonal:
            pivot = min(
                diagonal,
                key=lambda v: sum(u in active and u != v for u in rows[v]),
            )
            inverse = INVERSES_MOD_SEVEN[rows[pivot][pivot]]
            neighbors = [v for v in rows[pivot] if v in active and v != pivot]
            for left_index, left in enumerate(neighbors):
                left_entry = rows[left][pivot]
                for right in neighbors[left_index:]:
                    set_symmetric(
                        left,
                        right,
                        rows[left].get(right, 0)
                        - left_entry * inverse * rows[pivot][right],
                    )
            for neighbor in list(rows[pivot]):
                if neighbor != pivot:
                    rows[neighbor].pop(pivot, None)
            rows[pivot].clear()
            active.remove(pivot)
            rank += 1
            continue

        pivot = min(active)
        partners = [v for v in rows[pivot] if v in active and v != pivot]
        if not partners:
            rows[pivot].clear()
            active.remove(pivot)
            continue
        partner = min(partners)
        inverse = INVERSES_MOD_SEVEN[rows[pivot][partner]]
        remainder = sorted(
            ((set(rows[pivot]) | set(rows[partner])) & active)
            - {pivot, partner}
        )
        for left_index, left in enumerate(remainder):
            left_pivot = rows[left].get(pivot, 0)
            left_partner = rows[left].get(partner, 0)
            for right in remainder[left_index:]:
                set_symmetric(
                    left,
                    right,
                    rows[left].get(right, 0)
                    - inverse
                    * (
                        left_pivot * rows[right].get(partner, 0)
                        + left_partner * rows[right].get(pivot, 0)
                    ),
                )
        for removed in (pivot, partner):
            for neighbor in list(rows[removed]):
                if neighbor != removed:
                    rows[neighbor].pop(removed, None)
            rows[removed].clear()
            active.remove(removed)
        rank += 2
    return rank


def dense_laplacian_rank(adjacency: Sequence[Sequence[int]]) -> int:
    return matrix_rank(
        [
            [
                3 if left == right else (-1 if right in adjacency[left] else 0)
                for right in range(len(adjacency))
            ]
            for left in range(len(adjacency))
        ],
        FIELD_SEVEN,
    )


def transported_k39(
    adjacency_x: Sequence[Sequence[int]],
) -> list[list[int]]:
    """Return (J-I-2A)[T union X] over F7."""

    adjacency = empty_adjacency(3 + len(adjacency_x))
    for left, right in itertools.combinations(range(3), 2):
        adjacency[left].add(right)
        adjacency[right].add(left)
    for fibre in range(3):
        for local in range(12):
            vertex = 3 + 12 * fibre + local
            adjacency[fibre].add(vertex)
            adjacency[vertex].add(fibre)
    for left, neighbors in enumerate(adjacency_x):
        adjacency[3 + left].update(3 + right for right in neighbors)
    return [
        [
            0 if left == right else (6 if right in adjacency[left] else 1)
            for right in range(len(adjacency))
        ]
        for left in range(len(adjacency))
    ]


def structural_fibre_star_vectors() -> tuple[tuple[int, ...], ...]:
    """Three universal K39-kernel vectors, one for each twelve-fibre."""

    vectors: list[tuple[int, ...]] = []
    for fibre in range(3):
        vector = [0] * 39
        vector[:3] = [1, 1, 1]
        vector[fibre] = 4
        for local in range(12):
            vector[3 + 12 * fibre + local] = 1
        vectors.append(tuple(vector))
    return tuple(vectors)


def matrix_vector_product(
    matrix: Sequence[Sequence[int]],
    vector: Sequence[int],
    prime: int,
) -> tuple[int, ...]:
    return tuple(
        sum(entry * value for entry, value in zip(row, vector)) % prime
        for row in matrix
    )


def triangle_count(adjacency: Sequence[Sequence[int]]) -> int:
    return sum(
        middle in adjacency[left]
        and right in adjacency[left]
        and right in adjacency[middle]
        for left, middle, right in itertools.combinations(
            range(len(adjacency)), 3
        )
    )


def quotient_payload(quotient: Quotient) -> dict[str, object]:
    edges = [list(edge) for edge in quotient_edges(quotient)]
    payload = {"edges": edges}
    return {
        **payload,
        "sha256": sha256_bytes(canonical_bytes(payload)),
        "rank_F3_2I_plus_A": quotient_rank(quotient),
        "triangle_count": len(triangle_clauses(quotient)),
    }


def block_rows(quotient: Quotient, left: int, right: int) -> tuple[int, ...]:
    return tuple(
        sum(
            1 << (neighbor % LABELS)
            for neighbor in quotient[LABELS * left + label]
            if neighbor // LABELS == right
        )
        for label in range(LABELS)
    )


PERMUTED_MASKS: dict[tuple[int, ...], tuple[int, ...]] = {
    permutation: tuple(
        sum(1 << permutation[index] for index in range(LABELS) if mask >> index & 1)
        for mask in range(1 << LABELS)
    )
    for permutation in PERMUTATIONS
}


def block_mapping_ok(
    source_rows: Sequence[int],
    target_rows: Sequence[int],
    left_map: Sequence[int],
    right_map: Sequence[int],
) -> bool:
    permuted = PERMUTED_MASKS[tuple(right_map)]
    return all(
        permuted[source_rows[label]] == target_rows[left_map[label]]
        for label in range(LABELS)
    )


def coloured_quotient_isomorphism(
    source: Quotient,
    target: Quotient,
) -> tuple[int, ...]:
    """Find a fibre-preserving source-to-target quotient isomorphism."""

    source_blocks = {
        (left, right): block_rows(source, left, right)
        for left, right in ((0, 1), (1, 2), (2, 0))
    }
    target_blocks = {
        (left, right): block_rows(target, left, right)
        for left, right in ((0, 1), (1, 2), (2, 0))
    }
    for map0 in PERMUTATIONS:
        for map1 in PERMUTATIONS:
            if not block_mapping_ok(
                source_blocks[(0, 1)],
                target_blocks[(0, 1)],
                map0,
                map1,
            ):
                continue
            for map2 in PERMUTATIONS:
                if not block_mapping_ok(
                    source_blocks[(1, 2)],
                    target_blocks[(1, 2)],
                    map1,
                    map2,
                ):
                    continue
                if not block_mapping_ok(
                    source_blocks[(2, 0)],
                    target_blocks[(2, 0)],
                    map2,
                    map0,
                ):
                    continue
                mapping = tuple(
                    LABELS * fibre + (map0, map1, map2)[fibre][label]
                    for fibre in range(FIBRES)
                    for label in range(LABELS)
                )
                require(
                    all(
                        {mapping[v] for v in source[u]}
                        == set(target[mapping[u]])
                        for u in range(QUOTIENT_VERTICES)
                    ),
                    "constructed quotient map failed",
                )
                return mapping
    raise AssertionError("rank-eleven quotient is not colour-isomorphic")


def relabel_lift(
    adjacency: Sequence[Sequence[int]],
    quotient_mapping: Sequence[int],
) -> list[set[int]]:
    relabelled = empty_adjacency(LIFT_VERTICES)
    for source_pair in range(QUOTIENT_VERTICES):
        for source_endpoint in (0, 1):
            source_vertex = 2 * source_pair + source_endpoint
            target_vertex = 2 * quotient_mapping[source_pair] + source_endpoint
            relabelled[target_vertex] = {
                2 * quotient_mapping[neighbor // 2] + neighbor % 2
                for neighbor in adjacency[source_vertex]
            }
    return relabelled


def endpoint_for_quotient_neighbor(
    adjacency: Sequence[Sequence[int]],
    pair_vertex: int,
    neighbor_pair: int,
) -> int:
    found = [
        endpoint
        for endpoint in (0, 1)
        if any(
            2 * neighbor_pair + neighbor_endpoint
            in adjacency[2 * pair_vertex + endpoint]
            for neighbor_endpoint in (0, 1)
        )
    ]
    require(len(found) == 1, "lift does not cover quotient edge once")
    return found[0]


def canonical_mask_from_lift(
    quotient: Quotient,
    adjacency: Sequence[Sequence[int]],
) -> int:
    mask = 0
    for vertex in range(QUOTIENT_VERTICES):
        other_fibres = sorted(
            {neighbor // LABELS for neighbor in quotient[vertex]}
        )
        first_neighbors = [
            neighbor
            for neighbor in quotient[vertex]
            if neighbor // LABELS == other_fibres[0]
        ]
        second_neighbors = [
            neighbor
            for neighbor in quotient[vertex]
            if neighbor // LABELS == other_fibres[1]
        ]
        first = min(first_neighbors)
        second = min(second_neighbors)
        bit = endpoint_for_quotient_neighbor(adjacency, vertex, first) ^ (
            endpoint_for_quotient_neighbor(adjacency, vertex, second)
        )
        mask |= bit << vertex
    return mask


def affine_mask_transport(
    source: Quotient,
    target: Quotient,
    quotient_mapping: Sequence[int],
) -> tuple[int, tuple[int, ...]]:
    def transport(mask: int) -> int:
        adjacency = lifted_adjacency(source, mask)
        relabelled = relabel_lift(adjacency, quotient_mapping)
        return canonical_mask_from_lift(target, relabelled)

    constant = transport(0)
    destinations: list[int] = []
    for variable in range(QUOTIENT_VERTICES):
        delta = transport(1 << variable) ^ constant
        require(delta and delta & (delta - 1) == 0, "transport is not affine")
        destinations.append(delta.bit_length() - 1)
    require(
        sorted(destinations) == list(range(QUOTIENT_VERTICES)),
        "affine transport is not bijective",
    )
    return constant, tuple(destinations)


def transform_mask(
    mask: int,
    constant: int,
    destinations: Sequence[int],
) -> int:
    target = constant
    for source, destination in enumerate(destinations):
        target ^= ((mask >> source) & 1) << destination
    return target


def witness_record(
    quotient: Quotient,
    mask: int,
) -> dict[str, object]:
    adjacency = lifted_adjacency(quotient, mask)
    sparse_rank = sparse_laplacian_rank(adjacency)
    dense_rank = dense_laplacian_rank(adjacency)
    require(sparse_rank == dense_rank, "sparse/dense rank mismatch")
    require(triangle_count(adjacency) == 0, "witness is not triangle-free")
    k39 = transported_k39(adjacency)
    k39_rank = matrix_rank(k39, FIELD_SEVEN)
    require(k39_rank == dense_rank + 1, "K39 rank identity failed")
    structural = structural_fibre_star_vectors()
    require(
        all(
            matrix_vector_product(k39, vector, FIELD_SEVEN) == (0,) * 39
            for vector in structural
        ),
        "structural fibre-star vector left the K39 kernel",
    )
    require(
        matrix_rank(structural, FIELD_SEVEN) == 3,
        "structural fibre-star vectors lost independence",
    )
    edges = [
        [left, right]
        for left, neighbors in enumerate(adjacency)
        for right in neighbors
        if left < right
    ]
    payload = {"mask": mask, "edges": edges}
    return {
        **payload,
        "sha256": sha256_bytes(canonical_bytes(payload)),
        "rank_F7_3I_minus_A": dense_rank,
        "rank_F7_K39": k39_rank,
        "structural_fibre_star_kernel_dimension": 3,
        "degree_set": sorted(set(map(len, adjacency))),
        "triangle_count": 0,
    }


def canonical_lift_census(
    quotient: Quotient,
) -> tuple[int, list[int], dict[str, object]]:
    clauses = triangle_clauses(quotient)
    allowed = allowed_assignment_bitset(clauses)
    ranks = [0] * MASK_COUNT
    distribution: Counter[int] = Counter()
    first_by_rank: dict[int, int] = {}
    for mask in range(MASK_COUNT):
        if not (allowed >> mask) & 1:
            continue
        rank = sparse_laplacian_rank(lifted_adjacency(quotient, mask))
        ranks[mask] = rank
        distribution[rank] += 1
        first_by_rank.setdefault(rank, mask)
    minimum = min(distribution)
    return allowed, ranks, {
        "mask_count": MASK_COUNT,
        "triangle_free_mask_count": allowed.bit_count(),
        "rank_F7_3I_minus_A_distribution": {
            str(rank): count for rank, count in sorted(distribution.items())
        },
        "rank_F7_K39_distribution": {
            str(rank + 1): count
            for rank, count in sorted(distribution.items())
        },
        "minimum_rank_F7_3I_minus_A": minimum,
        "minimum_rank_F7_K39": minimum + 1,
        "canonical_minimum_witness": witness_record(
            quotient, first_by_rank[minimum]
        ),
    }


def enumerate_quotients() -> tuple[
    Counter[int],
    list[tuple[dict[str, object], Quotient]],
    list[dict[str, object]],
]:
    rank_distribution: Counter[int] = Counter()
    rank_eleven: list[tuple[dict[str, object], Quotient]] = []
    extended: list[dict[str, object]] = []
    index = 0
    for relative_orbit, _ in RELATIVE_REPRESENTATIVES:
        for fibre2_pairing in PAIRINGS:
            for fibre0_pairing in PAIRINGS:
                for permutation in itertools.permutations(range(3)):
                    quotient = make_quotient(
                        relative_orbit,
                        fibre2_pairing,
                        fibre0_pairing,
                        permutation,
                    )
                    rank = quotient_rank(quotient)
                    clauses = triangle_clauses(quotient)
                    allowed_count = allowed_assignment_bitset(clauses).bit_count()
                    rank_distribution[rank] += 1
                    extended.append(
                        {
                            "rank": rank,
                            "triangles": len(clauses),
                            "triangle_free_masks": allowed_count,
                            "relative_orbit": relative_orbit,
                        }
                    )
                    if rank == 11:
                        rank_eleven.append(
                            (
                                {
                                    "normalized_index": index,
                                    "relative_orbit": relative_orbit,
                                    "fibre2_pairing": [
                                        list(pair) for pair in fibre2_pairing
                                    ],
                                    "fibre0_pairing": [
                                        list(pair) for pair in fibre0_pairing
                                    ],
                                    "block_permutation": list(permutation),
                                },
                                quotient,
                            )
                        )
                    index += 1
    require(index == 4050, "normalization case count changed")
    return rank_distribution, rank_eleven, extended


def extended_summary(records: Sequence[dict[str, object]]) -> dict[str, object]:
    joint = Counter(
        (
            record["rank"],
            record["triangles"],
            record["triangle_free_masks"],
        )
        for record in records
    )
    by_rank: dict[str, dict[str, object]] = {}
    for rank in sorted({int(record["rank"]) for record in records}):
        selected = [record for record in records if record["rank"] == rank]
        counts = Counter(int(record["triangle_free_masks"]) for record in selected)
        by_rank[str(rank)] = {
            "forms": len(selected),
            "triangle_count_range": [
                min(int(record["triangles"]) for record in selected),
                max(int(record["triangles"]) for record in selected),
            ],
            "triangle_free_mask_count_range": [min(counts), max(counts)],
            "triangle_free_mask_count_distribution": {
                str(value): count for value, count in sorted(counts.items())
            },
        }
    return {
        "joint_distribution": [
            {
                "rank_F3_2I_plus_A": rank,
                "quotient_triangle_count": triangles,
                "triangle_free_mask_count": masks,
                "normalized_forms": count,
            }
            for (rank, triangles, masks), count in sorted(joint.items())
        ],
        "by_quotient_rank": by_rank,
    }


def exact_record() -> dict[str, object]:
    rank_distribution, rank_eleven, extended = enumerate_quotients()
    require(
        rank_distribution
        == Counter({11: 8, 12: 1, 13: 400, 14: 46, 15: 2616, 16: 979}),
        "Wave 40 quotient rank census changed",
    )
    require(len(rank_eleven) == 8, "rank-eleven case count changed")

    canonical_meta, canonical = rank_eleven[0]
    canonical_allowed, canonical_ranks, canonical_census = (
        canonical_lift_census(canonical)
    )
    per_quotient: list[dict[str, object]] = []
    for case_number, (metadata, quotient) in enumerate(rank_eleven):
        mapping = coloured_quotient_isomorphism(quotient, canonical)
        constant, destinations = affine_mask_transport(
            quotient, canonical, mapping
        )
        source_allowed = allowed_assignment_bitset(triangle_clauses(quotient))
        distribution: Counter[int] = Counter()
        first_by_rank: dict[int, int] = {}
        transported_allowed = 0
        for source_mask in range(MASK_COUNT):
            target_mask = transform_mask(source_mask, constant, destinations)
            source_is_allowed = (source_allowed >> source_mask) & 1
            target_is_allowed = (canonical_allowed >> target_mask) & 1
            require(
                source_is_allowed == target_is_allowed,
                "affine transport changed triangle-freeness",
            )
            if source_is_allowed:
                transported_allowed += 1
                rank = canonical_ranks[target_mask]
                require(rank > 0, "transported allowed mask has no rank")
                distribution[rank] += 1
                first_by_rank.setdefault(rank, source_mask)
        minimum = min(distribution)
        witness = witness_record(quotient, first_by_rank[minimum])
        require(witness["rank_F7_3I_minus_A"] == minimum, "witness rank drift")
        per_quotient.append(
            {
                "case_number": case_number,
                **metadata,
                "quotient": quotient_payload(quotient),
                "fibre_preserving_isomorphism_to_case_0": list(mapping),
                "affine_mask_transport_to_case_0": {
                    "constant_mask": constant,
                    "source_variable_to_target_variable": list(destinations),
                },
                "mask_count": MASK_COUNT,
                "triangle_free_mask_count": transported_allowed,
                "rank_F7_3I_minus_A_distribution": {
                    str(rank): count
                    for rank, count in sorted(distribution.items())
                },
                "rank_F7_K39_distribution": {
                    str(rank + 1): count
                    for rank, count in sorted(distribution.items())
                },
                "minimum_rank_F7_3I_minus_A": minimum,
                "minimum_rank_F7_K39": minimum + 1,
                "canonical_minimum_witness": witness,
            }
        )

    common_distributions = {
        canonical_bytes(
            {
                "triangle_free_mask_count": case["triangle_free_mask_count"],
                "rank_F7_K39_distribution": case["rank_F7_K39_distribution"],
            }
        )
        for case in per_quotient
    }
    require(len(common_distributions) == 1, "rank-eleven lift censuses differ")

    return {
        "format": FORMAT,
        "git_commit": FROZEN_COMMIT,
        "role": "construction",
        "claim_label": "CANDIDATE",
        "scope": (
            "All 4,050 normalized all-222 one-triangle quotients, with a "
            "complete endpoint-pairing lift census for all eight rank-eleven "
            "forms under the conditional prism-free local model."
        ),
        "normalized_all_222_quotients": {
            "case_count": 4050,
            "rank_F3_2I_plus_A_distribution": {
                str(rank): count
                for rank, count in sorted(rank_distribution.items())
            },
            "extended_triangle_free_lift_count_census": extended_summary(
                extended
            ),
        },
        "rank_eleven_boundary": {
            "normalized_case_count": 8,
            "fibre_coloured_isomorphism_class_count": 1,
            "canonical_case_metadata": canonical_meta,
            "canonical_lift_census": canonical_census,
            "all_cases": per_quotient,
            "common_exact_conclusion": {
                "quotient_triangle_count": 16,
                "triangle_free_masks_per_case": 37378,
                "rank_F7_K39_distribution_per_case": {
                    "33": 264,
                    "34": 7348,
                    "35": 29766,
                },
                "minimum_rank_F7_K39": 33,
            },
        },
        "conditional_candidate_theorem": {
            "assumptions": [
                "n3=4158 (no triangular prism)",
                "r3=rank_F3(M)=12",
                "all 693 graph edges have local type 2+2+2",
            ],
            "statement": (
                "For every base graph triangle T, the 39-vertex principal "
                "block K[T union N(T)] has F7-rank at least 33. Therefore "
                "r7=rank_F7(M)>=33, and the existing parity condition sharpens "
                "this joint branch to even r7>=34."
            ),
            "derivation": [
                "The verified quotient bridge gives rank_F3(2I+A_P)<=r3-1=11.",
                "The complete all-222 quotient census has exactly eight rank-11 cases.",
                "Those eight cases are one fibre-coloured isomorphism class.",
                "Every triangle-free endpoint-pairing lift has rank_F7(K39)>=33.",
                "A principal-block rank is at most the rank of the full matrix.",
            ],
            "status": "CANDIDATE_PENDING_INDEPENDENT_VERIFICATION",
        },
        "invariant_search": {
            "successes": [
                "The eight normalized rank-eleven records collapse to one exact fibre-coloured quotient isomorphism class.",
                "The omitted 18 pairing bits never lower the local K39 rank below 33 in that class.",
                "The complete 4,050-case census now records exact triangle-free pairing-mask counts, not only quotient ranks.",
            ],
            "failed_to_force_a_prism": [
                "All eight rank-eleven quotient cases have 37,378 triangle-free lifts.",
                "Each case has 264 lifts attaining K39 rank 33.",
                "A one-triangle quotient/lift relaxation does not enforce simultaneous 60-column B or 99-vertex compatibility.",
            ],
        },
        "rank33_border_roadblock": {
            "structural_kernel_vectors": (
                "For each fibre i, take T-coordinates (4,1,1) with 4 at "
                "the corresponding base vertex, put 1 on all twelve "
                "vertices of fibre i, and 0 on the other two fibres."
            ),
            "kernel_dimension_supplied": 3,
            "independence": "The three fibre-star vectors are F7-independent.",
            "outside_column_balance": (
                "Every outside vertex is nonadjacent to all three vertices "
                "of T and adjacent to exactly two vertices in each 12-fibre."
            ),
            "automatic_orthogonality": (
                "For its matching fibre-star vector, an outside K-column "
                "has dot product (4+1+1)+(10-2)=14=0 mod 7."
            ),
            "consequence_at_local_rank_33": (
                "The K39 kernel has dimension six, while three independent "
                "kernel vectors already annihilate every outside column. "
                "Therefore rank(H^T U)<=3 automatically for any balanced "
                "outside border U. The full-rank-at-most-44 requirement "
                "rank(H^T U)<=5 is vacuous and cannot force rank at least 45."
            ),
            "status": "FAILED_ROUTE",
        },
        "status_wall": {
            "endpoint_n3_4158": "UNKNOWN",
            "general_upper_bound_below_4158": "NOT_PROVED",
            "conway_99": "UNKNOWN",
            "graph_or_counterexample": "NONE",
            "novelty_or_priority": "UNKNOWN",
        },
        "limitations": [
            "Discovery cannot verify its own candidate theorem.",
            "The 4,050 quotient normalization is complete only for three all-222 sides around one graph triangle.",
            "The all-eight lift census is exact, but each lift is only a 36-vertex local core.",
            "No simultaneous B, outside graph H, global triangle-star compatibility, or 99-vertex graph is constructed.",
            "No endpoint exclusion, improved n3 upper bound, solution, or novelty claim is made.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    encoded = canonical_bytes(exact_record())
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
