#!/usr/bin/env python3
"""Clean-room checks for the Wave 40 edge-type coupling lane.

This module deliberately does not import, read, or execute the corresponding
discovery package.  It reconstructs only conditional one-triangle and global
cell-complex consequences of a hypothetical prism-free srg(99,14,1,2).

Nothing here constructs the 60 outside blocks, a 99-vertex graph, or an
endpoint contradiction.
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


FIELD_THREE = 3
FIELD_SEVEN = 7
FIBRE_COUNT = 3
PAIRS_PER_FIBRE = 6
QUOTIENT_VERTEX_COUNT = FIBRE_COUNT * PAIRS_PER_FIBRE
X_VERTEX_COUNT = 2 * QUOTIENT_VERTEX_COUNT
GRAPH_EDGE_COUNT = 693
GRAPH_TRIANGLE_COUNT = 231
ENDPOINT_EDGE_COUNT = 4158

Pair = tuple[int, int]
Pairing = tuple[Pair, ...]
Quotient = tuple[tuple[int, ...], ...]


def perfect_matchings(items: tuple[int, ...]) -> Iterable[Pairing]:
    """Generate every perfect matching, with canonical pair/order sorting."""

    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        second = items[index]
        remainder = items[1:index] + items[index + 1 :]
        for matching in perfect_matchings(remainder):
            yield tuple(sorted(((first, second),) + matching))


PAIRINGS: tuple[Pairing, ...] = tuple(
    sorted(set(perfect_matchings(tuple(range(PAIRS_PER_FIBRE)))))
)
BASE_PAIRING: Pairing = ((0, 1), (2, 3), (4, 5))
RELATIVE_REPRESENTATIVES: tuple[tuple[str, Pairing], ...] = (
    ("111", BASE_PAIRING),
    ("12", ((0, 1), (2, 4), (3, 5))),
    ("3", ((0, 2), (1, 4), (3, 5))),
)


def pairing_union_type(left: Pairing, right: Pairing) -> tuple[int, ...]:
    """Return half-cycle lengths in the union of two matchings on six points."""

    adjacency = [set() for _ in range(PAIRS_PER_FIBRE)]
    for first, second in left + right:
        adjacency[first].add(second)
        adjacency[second].add(first)
    unseen = set(range(PAIRS_PER_FIBRE))
    parts: list[int] = []
    while unseen:
        start = min(unseen)
        component = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor not in component:
                    component.add(neighbor)
                    stack.append(neighbor)
        unseen.difference_update(component)
        parts.append(1 if len(component) == 2 else len(component) // 2)
    return tuple(sorted(parts))


def empty_quotient() -> list[set[int]]:
    return [set() for _ in range(QUOTIENT_VERTEX_COUNT)]


def add_three_squares(
    adjacency: list[set[int]],
    left_fibre: int,
    right_fibre: int,
    left_pairing: Pairing,
    right_pairing: Pairing,
    block_permutation: Sequence[int],
) -> None:
    """Add a labelled 3C4 between two six-point quotient fibres."""

    if sorted(block_permutation) != list(range(PAIRS_PER_FIBRE // 2)):
        raise AssertionError("not a permutation of the three paired blocks")
    for block in range(PAIRS_PER_FIBRE // 2):
        right_block = block_permutation[block]
        for left in left_pairing[block]:
            for right in right_pairing[right_block]:
                left_vertex = left_fibre * PAIRS_PER_FIBRE + left
                right_vertex = right_fibre * PAIRS_PER_FIBRE + right
                if right_vertex in adjacency[left_vertex]:
                    raise AssertionError("parallel quotient edge")
                adjacency[left_vertex].add(right_vertex)
                adjacency[right_vertex].add(left_vertex)


def make_quotient(
    relative_type: str,
    fibre2_pairing: Pairing,
    fibre0_pairing: Pairing,
    block_permutation: Sequence[int],
) -> Quotient:
    """Build one representative in the complete 4,050-case normalization."""

    relative = dict(RELATIVE_REPRESENTATIVES)[relative_type]
    adjacency = empty_quotient()
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
    quotient = tuple(tuple(sorted(neighbors)) for neighbors in adjacency)
    if set(map(len, quotient)) != {4}:
        raise AssertionError("quotient is not four-regular")
    return quotient


def adjacency_matrix(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    size = len(adjacency)
    matrix = [[0] * size for _ in range(size)]
    for left, neighbors in enumerate(adjacency):
        for right in neighbors:
            matrix[left][right] = 1
    return matrix


def matrix_rank(matrix: Sequence[Sequence[int]], prime: int) -> int:
    """Exact dense Gaussian rank over a prime field."""

    rows = [[entry % prime for entry in row] for row in matrix]
    if not rows:
        return 0
    rank = 0
    for column in range(len(rows[0])):
        pivot = next(
            (
                row
                for row in range(rank, len(rows))
                if rows[row][column] % prime
            ),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [(inverse * entry) % prime for entry in rows[rank]]
        for row in range(rank + 1, len(rows)):
            factor = rows[row][column] % prime
            if factor:
                rows[row] = [
                    (left - factor * right) % prime
                    for left, right in zip(rows[row], rows[rank])
                ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def quotient_gram_rank(quotient: Quotient) -> int:
    """Rank over F3 of 2I+A_Q, the pair-incidence quotient."""

    matrix = adjacency_matrix(quotient)
    for index in range(len(matrix)):
        matrix[index][index] = 2
    return matrix_rank(matrix, FIELD_THREE)


def enumerate_normalized_quotients() -> tuple[Counter[int], list[dict[str, object]]]:
    """Enumerate the complete normalization and retain rank-eleven records."""

    distribution: Counter[int] = Counter()
    rank_eleven: list[dict[str, object]] = []
    for relative_type, _ in RELATIVE_REPRESENTATIVES:
        for fibre2_pairing in PAIRINGS:
            for fibre0_pairing in PAIRINGS:
                for permutation in itertools.permutations(range(3)):
                    quotient = make_quotient(
                        relative_type,
                        fibre2_pairing,
                        fibre0_pairing,
                        permutation,
                    )
                    rank = quotient_gram_rank(quotient)
                    distribution[rank] += 1
                    if rank == 11:
                        rank_eleven.append(
                            {
                                "relative_type": relative_type,
                                "fibre2_pairing": [list(pair) for pair in fibre2_pairing],
                                "fibre0_pairing": [list(pair) for pair in fibre0_pairing],
                                "block_permutation": list(permutation),
                            }
                        )
    return distribution, rank_eleven


def canonical_rank_eleven_quotient() -> Quotient:
    """The lexicographically first record in the rank-eleven census."""

    relative = "12"
    pairing = ((0, 1), (2, 4), (3, 5))
    return make_quotient(relative, pairing, pairing, (0, 1, 2))


def quotient_edges(quotient: Quotient) -> tuple[Pair, ...]:
    return tuple(
        (left, right)
        for left, neighbors in enumerate(quotient)
        for right in neighbors
        if left < right
    )


def half_edge_assignments(quotient: Quotient) -> dict[Pair, tuple[int, int]]:
    """Return (constant, mask coefficient) for each directed half-edge.

    At every quotient vertex, the two edges to the lower-numbered other
    fibre are assigned canonically to endpoints 0 and 1.  The local mask bit
    records the relative assignment of the two edges to the remaining fibre.
    Endpoint swaps have thereby been quotiented out independently at all
    eighteen pair-vertices.
    """

    assignments: dict[Pair, tuple[int, int]] = {}
    for vertex, neighbors in enumerate(quotient):
        other_fibres = sorted({neighbor // PAIRS_PER_FIBRE for neighbor in neighbors})
        if len(other_fibres) != 2:
            raise AssertionError("quotient vertex does not meet both other fibres")
        for coefficient, fibre in enumerate(other_fibres):
            fibre_neighbors = sorted(
                neighbor
                for neighbor in neighbors
                if neighbor // PAIRS_PER_FIBRE == fibre
            )
            if len(fibre_neighbors) != 2:
                raise AssertionError("quotient bidegree is not two")
            for constant, neighbor in enumerate(fibre_neighbors):
                assignments[(vertex, neighbor)] = (constant, coefficient)
    return assignments


def quotient_triangles(
    quotient: Quotient,
    assignments: dict[Pair, tuple[int, int]],
) -> tuple[tuple[tuple[int, int], ...], ...]:
    """Return the exact forbidden three-bit pattern for each quotient triangle."""

    triangles: list[tuple[tuple[int, int], ...]] = []
    for left, middle, right in itertools.combinations(
        range(QUOTIENT_VERTEX_COUNT), 3
    ):
        if (
            middle not in quotient[left]
            or right not in quotient[left]
            or right not in quotient[middle]
        ):
            continue
        requirements: list[tuple[int, int]] = []
        for vertex, first, second in (
            (left, middle, right),
            (middle, left, right),
            (right, left, middle),
        ):
            first_constant, first_coefficient = assignments[(vertex, first)]
            second_constant, second_coefficient = assignments[(vertex, second)]
            if first_coefficient == second_coefficient:
                raise AssertionError("triangle does not use both other fibres")
            requirements.append((vertex, first_constant ^ second_constant))
        triangles.append(tuple(requirements))
    return tuple(triangles)


def is_triangle_free_mask(
    mask: int,
    forbidden_patterns: Sequence[Sequence[tuple[int, int]]],
) -> bool:
    return all(
        not all(((mask >> vertex) & 1) == value for vertex, value in pattern)
        for pattern in forbidden_patterns
    )


def lifted_x_adjacency(
    quotient: Quotient,
    assignments: dict[Pair, tuple[int, int]],
    mask: int,
) -> list[set[int]]:
    """Lift a quotient using one relative endpoint-pairing bit per pair."""

    adjacency = [set() for _ in range(X_VERTEX_COUNT)]
    for pair_vertex in range(QUOTIENT_VERTEX_COUNT):
        left = 2 * pair_vertex
        right = left + 1
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
        lifted_left = 2 * left + left_endpoint
        lifted_right = 2 * right + right_endpoint
        adjacency[lifted_left].add(lifted_right)
        adjacency[lifted_right].add(lifted_left)
    if set(map(len, adjacency)) != {3}:
        raise AssertionError("lift is not cubic")
    return adjacency


INVERSES_MOD_SEVEN = (0, 1, 4, 5, 2, 3, 6)


def sparse_rank_three_i_minus_adjacency(
    adjacency: Sequence[Sequence[int]],
) -> int:
    """Exact symmetric-congruence rank of 3I-A over F7.

    Sparse one-by-one pivots are used whenever a nonzero diagonal exists.
    If the remaining diagonal vanishes, a nonzero off-diagonal entry gives
    an invertible two-by-two pivot.  These are congruence operations, so the
    accumulated pivot sizes equal the exact matrix rank.
    """

    size = len(adjacency)
    rows: list[dict[int, int]] = [dict() for _ in range(size)]

    def set_symmetric(left: int, right: int, value: int) -> None:
        reduced = value % FIELD_SEVEN
        if reduced:
            rows[left][right] = reduced
            rows[right][left] = reduced
        else:
            rows[left].pop(right, None)
            rows[right].pop(left, None)

    for vertex in range(size):
        rows[vertex][vertex] = 3
    for left, neighbors in enumerate(adjacency):
        for right in neighbors:
            if left < right:
                set_symmetric(left, right, -1)

    active = set(range(size))
    rank = 0
    while active:
        diagonal_pivots = [
            vertex for vertex in active if rows[vertex].get(vertex, 0)
        ]
        if diagonal_pivots:
            pivot = min(
                diagonal_pivots,
                key=lambda vertex: sum(
                    neighbor in active and neighbor != vertex
                    for neighbor in rows[vertex]
                ),
            )
            inverse = INVERSES_MOD_SEVEN[rows[pivot][pivot]]
            neighbors = [
                vertex
                for vertex in rows[pivot]
                if vertex in active and vertex != pivot
            ]
            for left_index, left in enumerate(neighbors):
                left_entry = rows[left][pivot]
                for right in neighbors[left_index:]:
                    value = (
                        rows[left].get(right, 0)
                        - left_entry * inverse * rows[pivot][right]
                    )
                    set_symmetric(left, right, value)
            for neighbor in list(rows[pivot]):
                if neighbor != pivot:
                    rows[neighbor].pop(pivot, None)
            rows[pivot].clear()
            active.remove(pivot)
            rank += 1
            continue

        pivot = min(active)
        partners = [
            vertex
            for vertex in rows[pivot]
            if vertex in active and vertex != pivot
        ]
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
                right_pivot = rows[right].get(pivot, 0)
                right_partner = rows[right].get(partner, 0)
                value = rows[left].get(right, 0) - inverse * (
                    left_pivot * right_partner
                    + left_partner * right_pivot
                )
                set_symmetric(left, right, value)
        for removed in (pivot, partner):
            for neighbor in list(rows[removed]):
                if neighbor != removed:
                    rows[neighbor].pop(removed, None)
            rows[removed].clear()
            active.remove(removed)
        rank += 2
    return rank


def ordinary_triangle_count(adjacency: Sequence[Sequence[int]]) -> int:
    return sum(
        middle in adjacency[left]
        and right in adjacency[left]
        and right in adjacency[middle]
        for left, middle, right in itertools.combinations(
            range(len(adjacency)), 3
        )
    )


def edge_local_parts(
    adjacency: Sequence[Sequence[int]], left_fibre: int, right_fibre: int
) -> tuple[int, ...]:
    """Return Wave 39 half-cycle parts for one base-triangle edge."""

    vertices = [
        vertex
        for fibre in (left_fibre, right_fibre)
        for vertex in range(12 * fibre, 12 * fibre + 12)
    ]
    allowed = set(vertices)
    unseen = set(vertices)
    parts: list[int] = []
    while unseen:
        start = min(unseen)
        component = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor in allowed and neighbor not in component:
                    component.add(neighbor)
                    stack.append(neighbor)
        unseen.difference_update(component)
        if len(component) % 4:
            raise AssertionError("edge-local component is not 4k")
        parts.append(len(component) // 4)
    return tuple(sorted(parts))


def three_i_minus_adjacency(
    adjacency: Sequence[Sequence[int]],
) -> list[list[int]]:
    size = len(adjacency)
    return [
        [
            (
                3
                if left == right
                else (-1 if right in adjacency[left] else 0)
            )
            % FIELD_SEVEN
            for right in range(size)
        ]
        for left in range(size)
    ]


def transported_39_block(
    adjacency_x: Sequence[Sequence[int]],
) -> list[list[int]]:
    """Build (J-I-2A)[T union X] over F7."""

    size = 3 + len(adjacency_x)
    adjacency = [set() for _ in range(size)]
    for left, right in itertools.combinations(range(3), 2):
        adjacency[left].add(right)
        adjacency[right].add(left)
    for fibre in range(3):
        for local in range(12):
            x_vertex = 3 + 12 * fibre + local
            adjacency[fibre].add(x_vertex)
            adjacency[x_vertex].add(fibre)
    for left, neighbors in enumerate(adjacency_x):
        for right in neighbors:
            adjacency[3 + left].add(3 + right)
    return [
        [
            (
                0
                if left == right
                else (6 if right in adjacency[left] else 1)
            )
            for right in range(size)
        ]
        for left in range(size)
    ]


def exhaustive_lift_census(
    quotient: Quotient,
) -> tuple[dict[str, object], dict[str, object]]:
    assignments = half_edge_assignments(quotient)
    forbidden = quotient_triangles(quotient, assignments)
    rank_distribution: Counter[int] = Counter()
    triangle_free_count = 0
    canonical_by_rank: dict[int, tuple[int, list[set[int]]]] = {}
    for mask in range(1 << QUOTIENT_VERTEX_COUNT):
        if not is_triangle_free_mask(mask, forbidden):
            continue
        triangle_free_count += 1
        adjacency = lifted_x_adjacency(quotient, assignments, mask)
        rank = sparse_rank_three_i_minus_adjacency(adjacency)
        rank_distribution[rank] += 1
        canonical_by_rank.setdefault(rank, (mask, adjacency))

    minimum_rank = min(rank_distribution)
    witness_mask, witness_adjacency = canonical_by_rank[minimum_rank]
    dense_rank = matrix_rank(
        three_i_minus_adjacency(witness_adjacency), FIELD_SEVEN
    )
    if dense_rank != minimum_rank:
        raise AssertionError("sparse and dense F7 ranks disagree")
    block_rank = matrix_rank(
        transported_39_block(witness_adjacency), FIELD_SEVEN
    )
    if block_rank != 1 + dense_rank:
        raise AssertionError("39-block identity failed on canonical witness")

    witness_edges = [
        [left, right]
        for left, neighbors in enumerate(witness_adjacency)
        for right in neighbors
        if left < right
    ]
    witness_payload = {
        "mask_integer": witness_mask,
        "mask_bits_vertex_0_first": [
            (witness_mask >> vertex) & 1
            for vertex in range(QUOTIENT_VERTEX_COUNT)
        ],
        "x_edges": witness_edges,
    }
    witness_hash = hashlib.sha256(canonical_bytes(witness_payload)).hexdigest()
    witness = {
        **witness_payload,
        "sha256_of_witness_payload": witness_hash,
        "x_vertex_count": X_VERTEX_COUNT,
        "x_edge_count": len(witness_edges),
        "x_degree_set": sorted(set(map(len, witness_adjacency))),
        "x_triangle_count": ordinary_triangle_count(witness_adjacency),
        "base_edge_types": {
            "01": list(edge_local_parts(witness_adjacency, 0, 1)),
            "12": list(edge_local_parts(witness_adjacency, 1, 2)),
            "20": list(edge_local_parts(witness_adjacency, 2, 0)),
        },
        "rank_F7_3I_minus_A_X": dense_rank,
        "rank_F7_39_block_K": block_rank,
    }
    census = {
        "mask_count": 1 << QUOTIENT_VERTEX_COUNT,
        "quotient_triangle_count": len(forbidden),
        "triangle_free_mask_count": triangle_free_count,
        "rank_F7_3I_minus_A_X_distribution": {
            str(rank): count for rank, count in sorted(rank_distribution.items())
        },
        "rank_F7_39_block_K_distribution": {
            str(rank + 1): count
            for rank, count in sorted(rank_distribution.items())
        },
    }
    return census, witness


def global_complex_identities() -> dict[str, object]:
    """Record the exact variable identities and the valid Euler scope."""

    # Variables a,b,c,d count graph edges of types 222,24,33,6.
    # Every local link has twelve edges and the listed component lengths.
    sample_counts = (100, 200, 300, 93)
    a, b, c, d = sample_counts
    if a + b + c + d != GRAPH_EDGE_COUNT:
        raise AssertionError("hostile sample does not sum to 693")
    f4 = 3 * a + b
    f6 = 2 * c
    f8 = b
    f12 = d
    if 4 * f4 + 6 * f6 + 8 * f8 + 12 * f12 != 2 * ENDPOINT_EDGE_COUNT:
        raise AssertionError("face-edge handshake identity failed")

    return {
        "endpoint_bijection": {
            "J_vertices_are_graph_edges": GRAPH_EDGE_COUNT,
            "L_vertices_are_graph_triangles": GRAPH_TRIANGLE_COUNT,
            "E_J": ENDPOINT_EDGE_COUNT,
            "E_L": ENDPOINT_EDGE_COUNT,
            "map": (
                "A J-edge is the pair of opposite cross-edges of its unique "
                "induced N3; it maps to the L-edge joining the two side triangles."
            ),
            "why_bijective": (
                "At the prism-free endpoint every J-edge is nontriangular; "
                "the audited nontriangular-J-edge/N3 correspondence is bijective."
            ),
        },
        "type_variables": {
            "equation": "t222+t24+t33+t6=693",
            "face_counts": {
                "f4": "3*t222+t24",
                "f6": "2*t33",
                "f8": "t24",
                "f12": "t6",
                "F": "3*t222+2*t24+2*t33+t6",
            },
            "edge_face_handshake": (
                "4*f4+6*f6+8*f8+12*f12=8316=2*4158"
            ),
        },
        "closed_complex": {
            "vertices": 231,
            "edges": 4158,
            "faces": "F=3*t222+2*t24+2*t33+t6",
            "closed_reason": (
                "Each L-edge/N3 has exactly two distinct cross-edges, and each "
                "cross-edge selects one incident local-link face."
            ),
            "unsplit_euler_characteristic": "chi_cell=231-4158+F",
            "unsplit_chi_range": [-3234, -1848],
            "surface_warning": (
                "The unsplit complex is a closed 2-complex, not automatically "
                "a surface: the link H_T of a triangle-vertex can have several cycles."
            ),
        },
        "normalized_surface": {
            "operation": (
                "Split each triangle-vertex once per connected cycle of its link H_T."
            ),
            "vertex_count": "C=sum_T components(H_T)",
            "component_count_bounds": [231, 1386],
            "why_bounds": (
                "Each of 231 links is a 2-factor on 36 vertices with cycle "
                "length divisible by 3 and at least 6, hence has 1 through 6 cycles."
            ),
            "edges": 4158,
            "faces": "F=3*t222+2*t24+2*t33+t6",
            "euler_characteristic": "chi_surface=C-4158+F",
            "coarse_chi_range": [-3234, -693],
            "scope": (
                "Negative Euler characteristic is compatible with closed "
                "orientable or nonorientable surfaces.  Parity constrains "
                "orientability only conditionally and yields no contradiction."
            ),
        },
    }


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def build_results() -> dict[str, object]:
    if len(PAIRINGS) != 15:
        raise AssertionError("six-point pairing census changed")
    relative_distribution = Counter(
        pairing_union_type(BASE_PAIRING, pairing) for pairing in PAIRINGS
    )
    if relative_distribution != Counter(
        {(1, 1, 1): 1, (1, 2): 6, (3,): 8}
    ):
        raise AssertionError("relative pairing orbit census changed")

    rank_distribution, rank_eleven = enumerate_normalized_quotients()
    expected_quotient_ranks = Counter(
        {11: 8, 12: 1, 13: 400, 14: 46, 15: 2616, 16: 979}
    )
    if rank_distribution != expected_quotient_ranks:
        raise AssertionError(
            f"quotient rank distribution changed: {rank_distribution}"
        )

    quotient = canonical_rank_eleven_quotient()
    lift_census, witness = exhaustive_lift_census(quotient)
    expected_core_ranks = {"32": 264, "33": 7348, "34": 29766}
    expected_block_ranks = {"33": 264, "34": 7348, "35": 29766}
    if lift_census["triangle_free_mask_count"] != 37378:
        raise AssertionError("triangle-free mask census changed")
    if (
        lift_census["rank_F7_3I_minus_A_X_distribution"]
        != expected_core_ranks
    ):
        raise AssertionError(
            "core lift rank distribution changed: "
            f"{lift_census['rank_F7_3I_minus_A_X_distribution']}"
        )
    if lift_census["rank_F7_39_block_K_distribution"] != expected_block_ranks:
        raise AssertionError(
            "39-block lift rank distribution changed: "
            f"{lift_census['rank_F7_39_block_K_distribution']}"
        )
    if witness["x_triangle_count"] != 0:
        raise AssertionError("canonical witness is not triangle-free")
    if set(tuple(parts) for parts in witness["base_edge_types"].values()) != {
        (2, 2, 2)
    }:
        raise AssertionError("canonical witness is not all-222 at the base triangle")

    quotient_matrix_edges = [
        list(edge) for edge in quotient_edges(quotient)
    ]
    quotient_payload = {"edges": quotient_matrix_edges}
    quotient_hash = hashlib.sha256(
        canonical_bytes(quotient_payload)
    ).hexdigest()

    return {
        "claim_label": "VERIFIED_SCOPED",
        "format": "wave40-edge-type-coupling-independent-v1",
        "scope": (
            "Conditional global cell-complex identities and exhaustive "
            "all-222 one-triangle quotient/lift controls at n3=4158."
        ),
        "global_complex": global_complex_identities(),
        "normalized_quotient_enumeration": {
            "normalization": (
                "Fix the 01 relation to 3C4; classify the second pairing at "
                "fibre 1 by relative type 111,12,3; fix the 12 relation; "
                "enumerate all 15*15*6 possible 20 relations."
            ),
            "relative_pairing_type_counts_before_normalization": {
                "111": 1,
                "12": 6,
                "3": 8,
            },
            "representative_count": 3 * 15 * 15 * 6,
            "isomorphism_warning": (
                "These are complete normalized representatives, not asserted "
                "to be pairwise nonisomorphic."
            ),
            "matrix": "2I+A_Q over F_3",
            "rank_distribution": {
                str(rank): count
                for rank, count in sorted(rank_distribution.items())
            },
            "rank_eleven_count": len(rank_eleven),
            "rank_eleven_records": rank_eleven,
        },
        "explicit_rank_eleven_quotient": {
            **quotient_payload,
            "sha256_of_quotient_payload": quotient_hash,
            "vertex_count": QUOTIENT_VERTEX_COUNT,
            "edge_count": len(quotient_matrix_edges),
            "degree_set": sorted(set(map(len, quotient))),
            "rank_F3_2I_plus_A_Q": quotient_gram_rank(quotient),
        },
        "endpoint_pairing_lifts": {
            **lift_census,
            "mask_semantics": (
                "One relative endpoint-assignment bit at each of 18 quotient "
                "vertices, after independently quotienting endpoint swaps."
            ),
            "canonical_minimum_rank_witness": witness,
        },
        "rank_39_identity": {
            "statement": (
                "rank_F7((J-I-2A)[T union X])="
                "1+rank_F7(3I-A_X)"
            ),
            "derivation": [
                "The T block is I-J_3 and is invertible over F_7.",
                "Its Schur complement vanishes on the three-dimensional fibre-indicator space U.",
                "On U_perp the Schur complement is 2(3I-A_X).",
                "The restriction of 3I-A_X to U has rank two.",
                "Therefore rank(K_39)=3+(rank(3I-A_X)-2)=1+rank(3I-A_X).",
            ],
            "canonical_witness_check": {
                "rank_F7_3I_minus_A_X": witness[
                    "rank_F7_3I_minus_A_X"
                ],
                "rank_F7_K_39": witness["rank_F7_39_block_K"],
            },
        },
        "positive_control": {
            "status": "VERIFIED_ONE_TRIANGLE_CONTROL",
            "properties": [
                "36 vertices and 54 edges",
                "cubic",
                "triangle-free",
                "three 12-point fibres, each with a perfect matching",
                "each cross-fibre graph is a perfect matching",
                "all three base-triangle edges have type 222",
            ],
            "not_supplied": [
                "the 60 Y vertices or their block-incidence matrix B",
                "a compatible eight-regular graph H on Y",
                "cross-triangle compatibility",
                "a 99-vertex strongly regular graph",
                "an endpoint contradiction or improved upper bound",
            ],
        },
        "status_wall": {
            "endpoint_n3_4158": "UNKNOWN",
            "general_upper_bound_below_4158": "NOT_PROVED",
            "conway_99": "UNKNOWN",
            "graph_or_counterexample": "NONE",
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
