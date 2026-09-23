#!/usr/bin/env python3
"""Exact Wave 40 edge-type coupling checks for Conway-99.

The checker has two deliberately separate scopes.

1. It checks the integer bookkeeping of the global two-complex obtained by
   gluing the Wave 39 edge-local cycle systems through the opposite-edge
   graph J and the N3 triangle graph L.
2. It exhausts a normalized set of all-222 three-side quotients around one
   graph triangle and records the exact rank_F3(P-I) distribution.

Neither scope is a completed-graph search.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

FORMAT = "wave40-edge-type-coupling-v1"
FROZEN_COMMIT = "6b28af70c67f062d687251494a047debe70a246f"

GRAPH_VERTICES = 99
GRAPH_DEGREE = 14
GRAPH_EDGES = GRAPH_VERTICES * GRAPH_DEGREE // 2
GRAPH_TRIANGLES = GRAPH_EDGES // 3
GRAPH_NONEDGES = GRAPH_VERTICES * (GRAPH_VERTICES - 1) // 2 - GRAPH_EDGES
GRAPH_FOUR_CYCLES = GRAPH_NONEDGES // 2
J_EDGES = GRAPH_EDGES * 12 // 2
SURFACE_DARTS = 2 * J_EDGES

EDGE_TYPES = ("222", "24", "33", "6")
EDGE_TYPE_PARTITIONS = {
    "222": (2, 2, 2),
    "24": (2, 4),
    "33": (3, 3),
    "6": (6,),
}

FIXED_PAIRING = ((0, 1), (2, 3), (4, 5))
SHARE_ONE_PAIRING = ((0, 1), (2, 4), (3, 5))
SIX_CYCLE_PAIRING = ((0, 2), (1, 4), (3, 5))
RELATIVE_PAIRING_ORBITS = (
    ("aligned_222", FIXED_PAIRING),
    ("share_one_24", SHARE_ONE_PAIRING),
    ("six_cycle_6", SIX_CYCLE_PAIRING),
)

POSITIVE_LIFT_BITS = "000111010110110111110101010010011100"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def pairings(items: Sequence[int]) -> Iterable[tuple[tuple[int, int], ...]]:
    """Yield all perfect matchings of an even labelled set."""

    items = tuple(items)
    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        second = items[index]
        rest = items[1:index] + items[index + 1 :]
        for tail in pairings(rest):
            yield tuple(sorted(((first, second),) + tail))


def type222_block(
    left_pairing: Sequence[Sequence[int]],
    right_pairing: Sequence[Sequence[int]],
    pair_permutation: Sequence[int],
) -> list[list[int]]:
    """Return a 6 by 6 incidence matrix consisting of three K_2,2 blocks."""

    require(sorted(pair_permutation) == [0, 1, 2], "invalid pair permutation")
    matrix = [[0] * 6 for _ in range(6)]
    for left_index, right_index in enumerate(pair_permutation):
        for left in left_pairing[left_index]:
            for right in right_pairing[right_index]:
                matrix[left][right] = 1
    require(set(map(sum, matrix)) == {2}, "left degree changed")
    require(
        set(sum(matrix[left][right] for left in range(6)) for right in range(6))
        == {2},
        "right degree changed",
    )
    return matrix


def assemble_tripartite_quotient(
    block_01: Sequence[Sequence[int]],
    block_12: Sequence[Sequence[int]],
    block_20: Sequence[Sequence[int]],
) -> list[list[int]]:
    """Assemble the 18-vertex 6+6+6 quotient P."""

    quotient = [[0] * 18 for _ in range(18)]
    for left in range(6):
        for right in range(6):
            quotient[left][6 + right] = quotient[6 + right][left] = block_01[
                left
            ][right]
            quotient[6 + left][12 + right] = quotient[12 + right][6 + left] = (
                block_12[left][right]
            )
            quotient[12 + left][right] = quotient[right][12 + left] = block_20[
                left
            ][right]
    require(set(map(sum, quotient)) == {4}, "quotient degree changed")
    return quotient


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    if not work:
        return 0
    row_count = len(work)
    column_count = len(work[0])
    rank = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(rank, row_count) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [(entry * inverse) % prime for entry in work[rank]]
        for row in range(row_count):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (left - factor * right) % prime
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
    return rank


def rank_over_rationals(matrix: Sequence[Sequence[int]]) -> int:
    work = [[Fraction(entry) for entry in row] for row in matrix]
    if not work:
        return 0
    rank = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = 1 / work[rank][column]
        work[rank] = [entry * inverse for entry in work[rank]]
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
    return rank


def component_profiles(
    adjacency: Sequence[Sequence[int]], part_size: int
) -> tuple[tuple[int, ...], ...]:
    unseen = set(range(len(adjacency)))
    profiles: list[tuple[int, ...]] = []
    part_count = len(adjacency) // part_size
    while unseen:
        stack = [min(unseen)]
        component: list[int] = []
        while stack:
            vertex = stack.pop()
            if vertex not in unseen:
                continue
            unseen.remove(vertex)
            component.append(vertex)
            stack.extend(
                neighbor
                for neighbor in unseen
                if adjacency[vertex][neighbor]
            )
        profiles.append(
            tuple(
                sum(
                    part * part_size <= vertex < (part + 1) * part_size
                    for vertex in component
                )
                for part in range(part_count)
            )
        )
    return tuple(sorted(profiles))


def triangle_count(adjacency: Sequence[Sequence[int]]) -> int:
    order = len(adjacency)
    return sum(
        adjacency[first][second]
        and adjacency[first][third]
        and adjacency[second][third]
        for first in range(order)
        for second in range(first + 1, order)
        for third in range(second + 1, order)
    )


def bipartite_component_sizes(
    quotient: Sequence[Sequence[int]], first_part: int, second_part: int
) -> tuple[int, ...]:
    vertices = set(
        range(6 * first_part, 6 * first_part + 6)
    ) | set(range(6 * second_part, 6 * second_part + 6))
    unseen = set(vertices)
    sizes: list[int] = []
    while unseen:
        stack = [min(unseen)]
        size = 0
        while stack:
            vertex = stack.pop()
            if vertex not in unseen:
                continue
            unseen.remove(vertex)
            size += 1
            stack.extend(
                neighbor
                for neighbor in unseen
                if quotient[vertex][neighbor]
            )
        sizes.append(size)
    return tuple(sorted(sizes))


def shifted_quotient_rank(quotient: Sequence[Sequence[int]]) -> int:
    shifted = [
        [
            quotient[row][column] - int(row == column)
            for column in range(18)
        ]
        for row in range(18)
    ]
    return rank_mod_prime(shifted, 3)


def all_222_quotients() -> Iterable[
    tuple[str, tuple[tuple[int, int], ...], tuple[tuple[int, int], ...], tuple[int, ...], list[list[int]]]
]:
    """Yield a complete normalized labelled family of all-222 quotients.

    Fix the 0--1 block.  The pair partition induced on part 1 by the 1--2
    block has exactly three orbits under the stabilizer of the fixed block:
    it shares three, one, or zero pairs with the fixed partition.  Relabel
    part 2 to normalize that block.  The remaining 2--0 block is arbitrary:
    15 pairings on each side and 3! pair bijections.
    """

    block_01 = type222_block(FIXED_PAIRING, FIXED_PAIRING, (0, 1, 2))
    all_pairings = tuple(pairings(tuple(range(6))))
    require(len(all_pairings) == 15, "perfect-matching count changed")
    for orbit_name, part1_pairing in RELATIVE_PAIRING_ORBITS:
        block_12 = type222_block(part1_pairing, FIXED_PAIRING, (0, 1, 2))
        for part0_pairing in all_pairings:
            for part2_pairing in all_pairings:
                for pair_permutation in itertools.permutations(range(3)):
                    block_20 = type222_block(
                        part2_pairing,
                        part0_pairing,
                        pair_permutation,
                    )
                    quotient = assemble_tripartite_quotient(
                        block_01, block_12, block_20
                    )
                    yield (
                        orbit_name,
                        part0_pairing,
                        part2_pairing,
                        pair_permutation,
                        quotient,
                    )


@functools.lru_cache(maxsize=1)
def all_222_census() -> dict[str, object]:
    rank_distribution: dict[int, int] = {}
    orbit_rank_distributions: dict[str, dict[int, int]] = {}
    low_cases: list[dict[str, object]] = []
    total = 0
    for (
        orbit_name,
        part0_pairing,
        part2_pairing,
        pair_permutation,
        quotient,
    ) in all_222_quotients():
        total += 1
        for first, second in ((0, 1), (1, 2), (2, 0)):
            require(
                bipartite_component_sizes(quotient, first, second) == (4, 4, 4),
                "an all-222 block changed type",
            )
        rank = shifted_quotient_rank(quotient)
        rank_distribution[rank] = rank_distribution.get(rank, 0) + 1
        orbit_distribution = orbit_rank_distributions.setdefault(orbit_name, {})
        orbit_distribution[rank] = orbit_distribution.get(rank, 0) + 1
        if rank <= 11:
            low_cases.append(
                {
                    "relative_pairing_orbit": orbit_name,
                    "part0_pairing": [list(pair) for pair in part0_pairing],
                    "part2_pairing": [list(pair) for pair in part2_pairing],
                    "pair_permutation": list(pair_permutation),
                    "rank_F3_P_minus_I": rank,
                    "triangle_count_P": triangle_count(quotient),
                    "component_profiles": [
                        list(profile)
                        for profile in component_profiles(quotient, 6)
                    ],
                }
            )

    require(total == 3 * 15 * 15 * 6 == 4050, "normalized census size changed")
    require(
        rank_distribution == {11: 8, 12: 1, 13: 400, 14: 46, 15: 2616, 16: 979},
        "all-222 quotient rank distribution changed",
    )
    require(
        orbit_rank_distributions
        == {
            "aligned_222": {12: 1, 13: 88, 14: 43, 15: 672, 16: 546},
            "share_one_24": {11: 8, 13: 184, 14: 2, 15: 960, 16: 196},
            "six_cycle_6": {13: 128, 14: 1, 15: 984, 16: 237},
        },
        "relative-orbit rank distribution changed",
    )
    require(len(low_cases) == 8, "rank-at-most-eleven case count changed")
    require(
        {case["triangle_count_P"] for case in low_cases} == {16},
        "low-case triangle count changed",
    )
    require(
        {
            tuple(tuple(profile) for profile in case["component_profiles"])
            for case in low_cases
        }
        == {((2, 2, 2), (4, 4, 4))},
        "low-case component profile changed",
    )
    return {
        "normalization_proof": (
            "Fix block 01.  The part-1 pair partition of block 12 has "
            "three stabilizer orbits (shared-pair signatures 222, 24, 6); "
            "part 2 then normalizes block 12.  Block 20 has 15 choices of "
            "pair partition on each side and 3! pair bijections."
        ),
        "normalized_labelled_case_count": total,
        "rank_F3_P_minus_I_distribution": {
            str(rank): rank_distribution[rank] for rank in sorted(rank_distribution)
        },
        "distribution_by_relative_pairing_orbit": {
            orbit: {
                str(rank): distribution[rank]
                for rank in sorted(distribution)
            }
            for orbit, distribution in orbit_rank_distributions.items()
        },
        "rank_at_most_11_normalized_case_count": len(low_cases),
        "rank_at_most_11_common_triangle_count_P": 16,
        "rank_at_most_11_common_component_profiles": [[2, 2, 2], [4, 4, 4]],
        "rank_at_most_11_cases": low_cases,
    }


def add_edge(adjacency: list[list[int]], left: int, right: int) -> None:
    require(left != right and not adjacency[left][right], "invalid lift edge")
    adjacency[left][right] = adjacency[right][left] = 1


def positive_quotient() -> list[list[int]]:
    block_01 = type222_block(FIXED_PAIRING, FIXED_PAIRING, (0, 1, 2))
    block_12 = type222_block(SHARE_ONE_PAIRING, FIXED_PAIRING, (0, 1, 2))
    block_20 = type222_block(
        SHARE_ONE_PAIRING, SHARE_ONE_PAIRING, (0, 1, 2)
    )
    quotient = assemble_tripartite_quotient(block_01, block_12, block_20)
    require(shifted_quotient_rank(quotient) == 11, "positive quotient rank changed")
    return quotient


def lift_quotient(
    quotient: Sequence[Sequence[int]], orientation_bits: str
) -> list[list[int]]:
    """Lift a simple quotient to the 36-vertex one-triangle graph A_X."""

    require(
        len(orientation_bits) == 36 and set(orientation_bits) <= {"0", "1"},
        "invalid orientation bits",
    )
    bits = [int(bit) for bit in orientation_bits]
    adjacency = [[0] * 36 for _ in range(36)]
    for part in range(3):
        for label in range(6):
            add_edge(
                adjacency,
                part * 12 + 2 * label,
                part * 12 + 2 * label + 1,
            )

    offset = 0
    for first_part, second_part in ((0, 1), (1, 2), (2, 0)):
        first_bits = bits[offset : offset + 6]
        second_bits = bits[offset + 6 : offset + 12]
        offset += 12
        for first_label in range(6):
            neighbors = sorted(
                second_label
                for second_label in range(6)
                if quotient[6 * first_part + first_label][
                    6 * second_part + second_label
                ]
            )
            require(len(neighbors) == 2, "quotient block degree changed")
            for neighbor_index, second_label in enumerate(neighbors):
                reverse_neighbors = sorted(
                    label
                    for label in range(6)
                    if quotient[6 * second_part + second_label][
                        6 * first_part + label
                    ]
                )
                reverse_index = reverse_neighbors.index(first_label)
                first_endpoint = neighbor_index ^ first_bits[first_label]
                second_endpoint = reverse_index ^ second_bits[second_label]
                add_edge(
                    adjacency,
                    first_part * 12 + 2 * first_label + first_endpoint,
                    second_part * 12 + 2 * second_label + second_endpoint,
                )
    require(offset == 36, "orientation bits were not consumed")
    return adjacency


def contract_lift(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    quotient = [[0] * 18 for _ in range(18)]
    for first_part, second_part in ((0, 1), (1, 2), (2, 0)):
        for first_label in range(6):
            for second_label in range(6):
                count = sum(
                    adjacency[first_part * 12 + 2 * first_label + left_endpoint][
                        second_part * 12 + 2 * second_label + right_endpoint
                    ]
                    for left_endpoint in (0, 1)
                    for right_endpoint in (0, 1)
                )
                require(count in (0, 1), "lift produced a doubled quotient edge")
                quotient[6 * first_part + first_label][
                    6 * second_part + second_label
                ] = count
                quotient[6 * second_part + second_label][
                    6 * first_part + first_label
                ] = count
    return quotient


def square(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    order = len(matrix)
    return [
        [
            sum(matrix[row][middle] * matrix[middle][column] for middle in range(order))
            for column in range(order)
        ]
        for row in range(order)
    ]


def required_block_gram(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    adjacency_squared = square(adjacency)
    gram = [[0] * 36 for _ in range(36)]
    for left in range(36):
        for right in range(36):
            same_fibre = left // 12 == right // 12
            gram[left][right] = (
                12 * int(left == right)
                - adjacency[left][right]
                + 2
                - int(same_fibre)
                - adjacency_squared[left][right]
            )
    return gram


def adjacency_rows_hex(adjacency: Sequence[Sequence[int]]) -> list[str]:
    return [
        format(
            sum(entry << column for column, entry in enumerate(row)),
            "09x",
        )
        for row in adjacency
    ]


def positive_local_lift() -> dict[str, object]:
    quotient = positive_quotient()
    adjacency = lift_quotient(quotient, POSITIVE_LIFT_BITS)
    require(contract_lift(adjacency) == quotient, "lift contraction changed")
    require(set(map(sum, adjacency)) == {3}, "lift is not cubic")
    require(triangle_count(adjacency) == 0, "lift is not triangle-free")
    components = component_profiles(adjacency, 12)
    require(components == ((4, 4, 4), (8, 8, 8)), "lift components changed")

    codegree_histogram: dict[str, int] = {}
    adjacency_squared = square(adjacency)
    for left in range(36):
        for right in range(left + 1, 36):
            if adjacency[left][right]:
                relation = "edge"
            elif left // 12 == right // 12:
                relation = "same_fibre_nonedge"
            else:
                relation = "cross_fibre_nonedge"
            key = f"{relation}:{adjacency_squared[left][right]}"
            codegree_histogram[key] = codegree_histogram.get(key, 0) + 1
    require(
        max(
            codegree
            for key in codegree_histogram
            if key.startswith("cross_fibre_nonedge:")
            for codegree in [int(key.rsplit(":", 1)[1])]
        )
        <= 2,
        "cross-fibre codegree cap failed",
    )

    gram = required_block_gram(adjacency)
    require(min(min(row) for row in gram) == 0, "required Gram has negative entry")
    require(set(map(sum, gram)) == {60}, "required Gram row sum changed")
    gram_rank = rank_over_rationals(gram)
    require(gram_rank == 33, "required Gram rational rank changed")

    rows = adjacency_rows_hex(adjacency)
    rows_digest = hashlib.sha256(("\n".join(rows) + "\n").encode("ascii")).hexdigest()
    return {
        "purpose": (
            "Positive control for the one-triangle relaxation only; it is "
            "not a 60-column B, compatible H, 99-vertex graph, or endpoint witness."
        ),
        "orientation_bits": POSITIVE_LIFT_BITS,
        "adjacency_rows_hex": rows,
        "adjacency_rows_sha256": rows_digest,
        "vertices": 36,
        "degree": 3,
        "triangle_count": 0,
        "component_profiles": [list(profile) for profile in components],
        "quotient_side_types": ["222", "222", "222"],
        "quotient_rank_F3_P_minus_I": shifted_quotient_rank(quotient),
        "quotient_triangle_count": triangle_count(quotient),
        "quotient_component_profiles": [
            list(profile) for profile in component_profiles(quotient, 6)
        ],
        "pair_codegree_histogram": dict(sorted(codegree_histogram.items())),
        "required_BBt_minimum_entry": min(min(row) for row in gram),
        "required_BBt_row_sum": 60,
        "required_BBt_rational_rank": gram_rank,
    }


def canonical_pairing_lift(
    quotient: Sequence[Sequence[int]], pairing_mask: int
) -> list[list[int]]:
    """Return one representative for an 18-bit endpoint-pairing mask.

    At a contracted matching edge, the two quotient edges to either other
    fibre must use its two endpoints once each.  Swapping those endpoints is
    an isomorphism of the unlabelled lift.  Fix the sorted-neighbor assignment
    for the first other fibre; one bit records whether the assignment to the
    second other fibre is parallel or crossed.  Thus the 18 bits are complete
    representatives of the information omitted by P.
    """

    require(0 <= pairing_mask < 2**18, "pairing mask is out of range")
    adjacency = [[0] * 36 for _ in range(36)]
    for part in range(3):
        for label in range(6):
            add_edge(
                adjacency,
                part * 12 + 2 * label,
                part * 12 + 2 * label + 1,
            )

    other_parts = {
        part: sorted(set(range(3)) - {part}) for part in range(3)
    }

    def endpoint(
        quotient_vertex: int, neighbor_part: int, neighbor_index: int
    ) -> int:
        bit = (pairing_mask >> quotient_vertex) & 1
        is_second_part = int(
            neighbor_part == other_parts[quotient_vertex // 6][1]
        )
        return neighbor_index ^ (bit * is_second_part)

    for first_part, second_part in ((0, 1), (1, 2), (2, 0)):
        for first_label in range(6):
            first_vertex = 6 * first_part + first_label
            neighbors = sorted(
                second_label
                for second_label in range(6)
                if quotient[first_vertex][6 * second_part + second_label]
            )
            require(len(neighbors) == 2, "quotient block degree changed")
            for first_index, second_label in enumerate(neighbors):
                second_vertex = 6 * second_part + second_label
                reverse_neighbors = sorted(
                    label
                    for label in range(6)
                    if quotient[second_vertex][6 * first_part + label]
                )
                second_index = reverse_neighbors.index(first_label)
                first_endpoint = endpoint(
                    first_vertex, second_part, first_index
                )
                second_endpoint = endpoint(
                    second_vertex, first_part, second_index
                )
                add_edge(
                    adjacency,
                    first_part * 12 + 2 * first_label + first_endpoint,
                    second_part * 12 + 2 * second_label + second_endpoint,
                )
    return adjacency


def quotient_triangle_forbidden_assignments(
    quotient: Sequence[Sequence[int]],
) -> tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...]:
    """Return the unique local bit assignment lifting each P-triangle."""

    other_parts = {
        part: sorted(set(range(3)) - {part}) for part in range(3)
    }

    def endpoint(
        quotient_vertex: int,
        neighbor_part: int,
        neighbor_index: int,
        bit: int,
    ) -> int:
        is_second_part = int(
            neighbor_part == other_parts[quotient_vertex // 6][1]
        )
        return neighbor_index ^ (bit * is_second_part)

    forbidden: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = []
    for first in range(6):
        for second in range(6, 12):
            if not quotient[first][second]:
                continue
            for third in range(12, 18):
                if not (quotient[first][third] and quotient[second][third]):
                    continue
                vertices = (first, second, third)
                required_bits: list[int] = []
                for vertex in vertices:
                    other_vertices = [
                        other for other in vertices if other != vertex
                    ]
                    valid_bits: list[int] = []
                    for bit in (0, 1):
                        used_endpoints: list[int] = []
                        for other in other_vertices:
                            neighbor_part = other // 6
                            neighbors = sorted(
                                label
                                for label in range(6)
                                if quotient[vertex][
                                    6 * neighbor_part + label
                                ]
                            )
                            neighbor_index = neighbors.index(other % 6)
                            used_endpoints.append(
                                endpoint(
                                    vertex,
                                    neighbor_part,
                                    neighbor_index,
                                    bit,
                                )
                            )
                        if used_endpoints[0] == used_endpoints[1]:
                            valid_bits.append(bit)
                    require(
                        len(valid_bits) == 1,
                        "a quotient triangle lost its unique lift assignment",
                    )
                    required_bits.append(valid_bits[0])
                forbidden.append((vertices, tuple(required_bits)))
    return tuple(forbidden)


def pairing_mask_is_triangle_free(
    pairing_mask: int,
    forbidden: Sequence[
        tuple[tuple[int, int, int], tuple[int, int, int]]
    ],
) -> bool:
    return not any(
        all(
            ((pairing_mask >> vertex) & 1) == bit
            for vertex, bit in zip(vertices, required_bits)
        )
        for vertices, required_bits in forbidden
    )


def laplacian(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            3 * int(row == column) - adjacency[row][column]
            for column in range(len(adjacency))
        ]
        for row in range(len(adjacency))
    ]


def triangle_neighbor_transport_block(
    adjacency_x: Sequence[Sequence[int]],
) -> list[list[int]]:
    """Return K=J-I-2A on T union N(T), of order 39."""

    require(len(adjacency_x) == 36, "neighbor core order changed")
    adjacency = [[0] * 39 for _ in range(39)]
    for first, second in ((0, 1), (1, 2), (2, 0)):
        add_edge(adjacency, first, second)
    for part in range(3):
        for point in range(12):
            add_edge(adjacency, part, 3 + 12 * part + point)
    for first in range(36):
        for second in range(first + 1, 36):
            if adjacency_x[first][second]:
                add_edge(adjacency, 3 + first, 3 + second)
    return [
        [
            1 - int(row == column) - 2 * adjacency[row][column]
            for column in range(39)
        ]
        for row in range(39)
    ]


def triangle_neighbor_rank_identity(
    adjacency_x: Sequence[Sequence[int]],
) -> dict[str, int]:
    """Check rank(K_39)=1+rank(3I-A_X) over F_7."""

    laplacian_rank = rank_mod_prime(laplacian(adjacency_x), 7)
    transport_rank = rank_mod_prime(
        triangle_neighbor_transport_block(adjacency_x), 7
    )
    require(
        transport_rank == 1 + laplacian_rank,
        "triangle-neighbor rank identity failed",
    )
    return {
        "laplacian_rank_F7": laplacian_rank,
        "transport_block_rank_F7": transport_rank,
    }


@functools.lru_cache(maxsize=1)
def positive_quotient_lift_census() -> dict[str, object]:
    """Exhaust the 18 omitted pairing bits for the rank-11 control quotient."""

    quotient = positive_quotient()
    forbidden = quotient_triangle_forbidden_assignments(quotient)
    require(len(forbidden) == 16, "positive quotient triangle count changed")
    triangle_free_masks = [
        mask
        for mask in range(2**18)
        if pairing_mask_is_triangle_free(mask, forbidden)
    ]
    require(
        len(triangle_free_masks) == 37_378,
        "triangle-free pairing-mask count changed",
    )

    rank_distribution: dict[int, int] = {}
    witnesses: dict[int, int] = {}
    for mask in triangle_free_masks:
        adjacency = canonical_pairing_lift(quotient, mask)
        transport_rank = 1 + rank_mod_prime(laplacian(adjacency), 7)
        rank_distribution[transport_rank] = (
            rank_distribution.get(transport_rank, 0) + 1
        )
        witnesses.setdefault(transport_rank, mask)
    require(
        rank_distribution == {33: 264, 34: 7_348, 35: 29_766},
        "positive-quotient 39-block rank distribution changed",
    )
    require(witnesses[33] == 51_739, "canonical rank-33 witness changed")

    witness_adjacency = canonical_pairing_lift(quotient, witnesses[33])
    require(triangle_count(witness_adjacency) == 0, "rank-33 witness has a triangle")
    witness_identity = triangle_neighbor_rank_identity(witness_adjacency)
    witness_rows = adjacency_rows_hex(witness_adjacency)
    witness_digest = hashlib.sha256(
        ("\n".join(witness_rows) + "\n").encode("ascii")
    ).hexdigest()
    return {
        "scope": (
            "All endpoint-pairing lifts of one rank-11 all-222 quotient; "
            "not all 4,050 quotients and not all endpoint cores."
        ),
        "omitted_pairing_bit_count": 18,
        "all_pairing_masks": 2**18,
        "quotient_triangle_count": len(forbidden),
        "triangle_free_pairing_masks": len(triangle_free_masks),
        "transport_rank_F7_distribution": {
            str(rank): rank_distribution[rank]
            for rank in sorted(rank_distribution)
        },
        "minimum_transport_rank_F7": min(rank_distribution),
        "canonical_minimum_witness": {
            "pairing_mask_decimal": witnesses[33],
            "pairing_mask_bits_low_to_high": [
                (witnesses[33] >> bit) & 1 for bit in range(18)
            ],
            "adjacency_rows_hex": witness_rows,
            "adjacency_rows_sha256": witness_digest,
            "component_profiles": [
                list(profile)
                for profile in component_profiles(witness_adjacency, 12)
            ],
            **witness_identity,
        },
    }


def face_counts(type_counts: dict[str, int]) -> dict[str, int]:
    require(set(type_counts) == set(EDGE_TYPES), "edge type keys changed")
    require(all(value >= 0 for value in type_counts.values()), "negative type count")
    require(sum(type_counts.values()) == GRAPH_EDGES, "edge type total changed")
    count_222 = type_counts["222"]
    count_24 = type_counts["24"]
    count_33 = type_counts["33"]
    count_6 = type_counts["6"]
    faces = {
        "length_4": 3 * count_222 + count_24,
        "length_6": 2 * count_33,
        "length_8": count_24,
        "length_12": count_6,
    }
    total_faces = sum(faces.values())
    boundary_sum = sum(
        int(length.rsplit("_", 1)[1]) * count for length, count in faces.items()
    )
    require(boundary_sum == SURFACE_DARTS, "face-boundary identity changed")
    faces["total"] = total_faces
    faces["boundary_sum"] = boundary_sum
    return faces


def surface_record() -> dict[str, object]:
    all_222 = face_counts({"222": 693, "24": 0, "33": 0, "6": 0})
    require(all_222["length_4"] == 2079, "all-222 square count changed")
    require(all_222["total"] == 2079, "all-222 face count changed")
    link_component_min = GRAPH_TRIANGLES
    link_component_max = 6 * GRAPH_TRIANGLES
    euler_min = link_component_min - J_EDGES + all_222["total"]
    euler_max = link_component_max - J_EDGES + all_222["total"]
    require((euler_min, euler_max) == (-1848, -693), "Euler interval changed")
    return {
        "opposite_edge_graph_J": {
            "vertices_graph_edges": GRAPH_EDGES,
            "degree": 12,
            "edges": J_EDGES,
            "graph_four_cycles": GRAPH_FOUR_CYCLES,
            "J_edges_per_graph_four_cycle": 2,
        },
        "triangle_relation_graph_L": {
            "vertices_graph_triangles": GRAPH_TRIANGLES,
            "degree_at_prism_free_endpoint": 36,
            "edges": J_EDGES,
        },
        "edge_bijection": (
            "At the prism-free endpoint, a J edge gives its unique N3 side-"
            "triangle pair, hence an L edge; conversely an L edge has two "
            "cross edges, which are opposite in its induced four-cycle."
        ),
        "star_to_face_rule": (
            "For each graph edge e, the twelve J edges incident with e map "
            "to a simple 2-regular bipartite K_e on the six nonbase "
            "triangles through each endpoint.  Its cycle components are faces."
        ),
        "edge_multiplicity": (
            "Every L edge lies on exactly two face boundaries, one for each "
            "of the two cross graph edges in its N3."
        ),
        "face_formula_for_type_counts_a_b_c_d": {
            "type_order": ["222", "24", "33", "6"],
            "F4": "3a+b",
            "F6": "2c",
            "F8": "b",
            "F12": "d",
            "F_total": "3a+2b+2c+d",
            "boundary_identity": "4F4+6F6+8F8+12F12=8316=2|E(L)|",
        },
        "local_cycle_incidence_in_G": {
            "induced_C8_with_base_edge": "3a+b",
            "induced_C12_with_base_edge": "2c",
            "induced_C16_with_base_edge": "b",
            "induced_C24_with_base_edge": "d",
            "scope_warning": (
                "These count pairs (base edge, induced cycle), not necessarily "
                "distinct induced cycles of G."
            ),
        },
        "triangle_links": {
            "link_vertices_per_graph_triangle": 36,
            "link_degree": 2,
            "identification": (
                "The link is the line graph of the 36-vertex cross-fibre "
                "two-factor in G[N(T)-T]."
            ),
            "cycle_lengths": "multiples of 3 and at least 6",
            "component_count_per_triangle": [1, 6],
        },
        "normalized_surface": {
            "vertices": "H=sum_T h(T), where h(T) is the triangle-link component count",
            "edges": J_EDGES,
            "faces": "3a+2b+2c+d",
            "euler_characteristic": "H-4158+(3a+2b+2c+d)",
        },
        "all_222_specialization": {
            "type_counts": {"222": 693, "24": 0, "33": 0, "6": 0},
            "face_counts": all_222,
            "quadrangulation": True,
            "link_component_total_range": [
                link_component_min,
                link_component_max,
            ],
            "euler_characteristic_range": [euler_min, euler_max],
            "euler_route_is_contradictory": False,
            "reason": (
                "Closed surfaces may have arbitrarily negative Euler "
                "characteristic; orientability is not assumed or derived."
            ),
        },
    }


@functools.lru_cache(maxsize=1)
def exact_record() -> dict[str, object]:
    census = all_222_census()
    positive = positive_local_lift()
    positive_rank_identity = triangle_neighbor_rank_identity(
        lift_quotient(positive_quotient(), POSITIVE_LIFT_BITS)
    )
    lift_census = positive_quotient_lift_census()
    return {
        "format": FORMAT,
        "role": "proof_b",
        "claim_label": "CANDIDATE",
        "git_commit": FROZEN_COMMIT,
        "scope": (
            "Conditional prism-free endpoint n3=4158: global edge-type "
            "surface identities and an exhaustive normalized all-222 "
            "one-triangle quotient census"
        ),
        "frozen_parameters": {
            "srg": [99, 14, 1, 2],
            "graph_edges": GRAPH_EDGES,
            "graph_triangles": GRAPH_TRIANGLES,
            "graph_four_cycles": GRAPH_FOUR_CYCLES,
            "J_edges": J_EDGES,
        },
        "global_edge_type_complex": surface_record(),
        "all_222_three_side_quotient_census": census,
        "joint_low_rank_consequence": {
            "conditional_on": [
                "n3=4158 (no triangular prism)",
                "every graph edge has Wave39 type 222",
                "rank_F3(M)=12",
            ],
            "rank_ceiling_used": (
                "rank_F3(P_T-I)<=rank_F3(C+J)=r3-1=11 for every graph triangle T"
            ),
            "conclusion": (
                "For every T, P_T has component profiles (2,2,2)+(4,4,4), "
                "has exactly 16 triangles, and belongs to one of the eight "
                "normalized labelled rank-11 cases."
            ),
            "lift_component_partition_in_fibre_units": [4, 8],
            "endpoint_excluded": False,
        },
        "one_triangle_positive_control": positive,
        "triangle_neighbor_characteristic_seven_rank": {
            "block": "K[T union N(T),T union N(T)] over F_7",
            "neighbor_core": "A_X=G[N(T)-T], a cubic graph on 36 vertices",
            "identity": (
                "rank_F7(K[T union N(T)])=1+rank_F7(3I-A_X)"
            ),
            "derivation": (
                "The 3 by 3 base-triangle block I-J is invertible.  Its "
                "Schur complement vanishes on the three fibre constants "
                "and equals -I-2A_X=-2(A_X-3I) on their 33-dimensional "
                "orthogonal complement; A_X-3I has rank two on the fibre-"
                "constant space."
            ),
            "quotient_scope_guard": (
                "P_T omits one endpoint-pairing bit at each of its 18 "
                "vertices, and the 39-block rank can change when those "
                "bits change.  A quotient census alone is not a rank proof."
            ),
            "original_positive_lift": positive_rank_identity,
            "one_quotient_complete_pairing_census": lift_census,
            "universal_rank_floor_from_this_lane": None,
        },
        "conclusion": {
            "new_general_upper_bound_on_n3": False,
            "strongest_general_upper_bound_on_n3": 4158,
            "all_222_excluded": False,
            "joint_r3_12_all_222_excluded": False,
            "universal_39_block_rank_at_least_33_proved": False,
            "endpoint_excluded": False,
            "target_status": "UNKNOWN",
            "smallest_exposed_global_target": (
                "Exclude the rank-11 (4+8)-component quotient at even one "
                "base triangle under a full simultaneous B/H completion, "
                "or prove that the resulting 2+4 selections cannot be "
                "compatible across all seven triangle-stars at every vertex."
            ),
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "The surface is a repackaging of necessary endpoint incidences, not a graph construction.",
            "The 4,050-case census is exhaustive only for one normalized all-222 triangle quotient.",
            "The 39-block pairing census is exhaustive for only one of those quotients.",
            "The positive lift is a 36-vertex one-triangle relaxation, not a simultaneous 60-block design.",
            "No automorphism or transitivity of a completed 99-vertex graph is assumed.",
            "No endpoint exclusion, improved n3 upper bound, Conway-99 resolution, or novelty claim is made.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output", type=Path)
    mode.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = canonical_json(exact_record())
    if args.verify:
        if args.verify.read_bytes() != payload:
            raise SystemExit("stored exact result differs from regeneration")
        print(f"PASS: {args.verify} matches exact regeneration")
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    else:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
