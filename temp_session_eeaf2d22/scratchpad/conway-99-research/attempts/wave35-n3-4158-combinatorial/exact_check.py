#!/usr/bin/env python3
"""Exact checks for the prism-free n3=4158 triangle-fibre reduction.

The global target remains unknown.  This checker proves only the displayed
one-triangle incidence identities and audits one restricted, normalized local
core.  The restricted core is not asserted to extend to 99 vertices.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations, product
from pathlib import Path


N = 12
TRIANGLE_COUNT = 231
N3_ENDPOINT = 4158
WITHIN_FACTOR_INDICES = (1, 2, 3)

# Exact pairwise edge-bijection certificate for the restricted core below.
# Row r is the lexicographically ordered r-th edge of K12 minus factor 1;
# the value is the paired edge index in K12 minus factor 2.
PAIR_01_CERTIFICATE = (
    38, 47, 19, 12, 59, 57, 7, 28, 14, 48,
    43, 3, 10, 25, 36, 54, 33, 5, 50, 11,
    52, 27, 0, 29, 22, 55, 56, 45, 49, 58,
    24, 1, 53, 32, 35, 9, 44, 46, 13, 39,
    31, 30, 37, 15, 26, 4, 16, 8, 20, 34,
    21, 18, 2, 17, 41, 6, 40, 42, 23, 51,
)


def one_factor(round_index: int) -> tuple[tuple[int, int], ...]:
    if not 0 <= round_index < N - 1:
        raise ValueError(round_index)
    modulus = N - 1
    pairs = [(N - 1, round_index)]
    for offset in range(1, N // 2):
        pairs.append(
            (
                (round_index + offset) % modulus,
                (round_index - offset) % modulus,
            )
        )
    return tuple(sorted(tuple(sorted(pair)) for pair in pairs))


FACTORS = tuple(one_factor(index) for index in range(N - 1))


def partner_map(factor: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    result = [-1] * N
    for left, right in factor:
        result[left] = right
        result[right] = left
    if any(value < 0 for value in result):
        raise AssertionError("factor is not perfect")
    return tuple(result)


SIGMA = partner_map(FACTORS[0])


def add_edge(matrix: list[list[int]], left: int, right: int) -> None:
    if left == right or matrix[left][right]:
        raise AssertionError((left, right))
    matrix[left][right] = 1
    matrix[right][left] = 1


def build_restricted_x_adjacency() -> list[list[int]]:
    """Return the normalized 36-vertex cubic fibre core.

    Cross matchings X0-X1 and X1-X2 are the identity.  The X2-X0
    matching is SIGMA, a product of six transpositions.  The three
    within-fibre matchings are factors 1, 2, and 3.
    """

    size = 3 * N
    adjacency = [[0] * size for _ in range(size)]
    for fibre, factor_index in enumerate(WITHIN_FACTOR_INDICES):
        for left, right in FACTORS[factor_index]:
            add_edge(adjacency, fibre * N + left, fibre * N + right)
    for label in range(N):
        add_edge(adjacency, label, N + label)
        add_edge(adjacency, N + label, 2 * N + label)
        add_edge(adjacency, 2 * N + label, SIGMA[label])
    return adjacency


def build_cross_two_factor() -> list[list[int]]:
    size = 3 * N
    adjacency = [[0] * size for _ in range(size)]
    for label in range(N):
        add_edge(adjacency, label, N + label)
        add_edge(adjacency, N + label, 2 * N + label)
        add_edge(adjacency, 2 * N + label, SIGMA[label])
    return adjacency


def cycle_lengths(adjacency: list[list[int]]) -> tuple[int, ...]:
    if any(sum(row) != 2 for row in adjacency):
        raise AssertionError("not a two-factor")
    unseen = set(range(len(adjacency)))
    lengths: list[int] = []
    while unseen:
        start = min(unseen)
        previous = -1
        current = start
        length = 0
        while True:
            unseen.discard(current)
            length += 1
            neighbors = [index for index, value in enumerate(adjacency[current]) if value]
            nxt = neighbors[0] if neighbors[0] != previous else neighbors[1]
            previous, current = current, nxt
            if current == start:
                break
        lengths.append(length)
    return tuple(sorted(lengths))


def square(matrix: list[list[int]]) -> list[list[int]]:
    size = len(matrix)
    return [
        [
            sum(matrix[left][middle] * matrix[middle][right] for middle in range(size))
            for right in range(size)
        ]
        for left in range(size)
    ]


def required_xy_gram(adjacency: list[list[int]]) -> list[list[int]]:
    """Return B B^T forced by the SRG equations in the T|X|Y partition."""

    adjacency_squared = square(adjacency)
    size = len(adjacency)
    gram = [[0] * size for _ in range(size)]
    for left in range(size):
        for right in range(size):
            gram[left][right] = (
                (12 if left == right else 0)
                - adjacency[left][right]
                + 2
                - (1 if left // N == right // N else 0)
                - adjacency_squared[left][right]
            )
    return gram


def allowed_pairs(factor_index: int) -> tuple[tuple[int, int], ...]:
    forbidden = set(FACTORS[factor_index])
    return tuple(
        pair
        for pair in combinations(range(N), 2)
        if pair not in forbidden
    )


def pair_concurrence(
    left_pairs: tuple[tuple[int, int], ...],
    right_pairs: tuple[tuple[int, int], ...],
    permutation: tuple[int, ...],
) -> list[list[int]]:
    if sorted(permutation) != list(range(len(right_pairs))):
        raise AssertionError("certificate is not a permutation")
    result = [[0] * N for _ in range(N)]
    for row, left_pair in enumerate(left_pairs):
        right_pair = right_pairs[permutation[row]]
        for left in left_pair:
            for right in right_pair:
                result[left][right] += 1
    return result


def gf2_rank(matrix: list[list[int]]) -> int:
    rows = [
        sum((value & 1) << column for column, value in enumerate(row))
        for row in matrix
    ]
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next(
            (
                index
                for index in range(rank, len(rows))
                if (rows[index] >> column) & 1
            ),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and ((rows[index] >> column) & 1):
                rows[index] ^= rows[rank]
        rank += 1
    return rank


def triangle_count(adjacency: list[list[int]]) -> int:
    return sum(
        adjacency[left][middle]
        * adjacency[middle][right]
        * adjacency[right][left]
        for left, middle, right in combinations(range(len(adjacency)), 3)
    )


def valid_block_type_census(
    adjacency: list[list[int]],
    pair_sets: tuple[tuple[tuple[int, int], ...], ...],
) -> tuple[int, dict[int, int]]:
    """Count restricted triples whose induced X graph is a matching."""

    total = 0
    by_internal_edge_count: dict[int, int] = {}
    for edges in product(*pair_sets):
        vertices = tuple(
            fibre * N + vertex
            for fibre, pair in enumerate(edges)
            for vertex in pair
        )
        internal_degrees = tuple(
            sum(adjacency[left][right] for right in vertices)
            for left in vertices
        )
        if max(internal_degrees) > 1:
            continue
        internal_edges = sum(internal_degrees) // 2
        total += 1
        by_internal_edge_count[internal_edges] = (
            by_internal_edge_count.get(internal_edges, 0) + 1
        )
    return total, dict(sorted(by_internal_edge_count.items()))


def distribution(values: list[int]) -> dict[int, int]:
    result: dict[int, int] = {}
    for value in values:
        result[value] = result.get(value, 0) + 1
    return dict(sorted(result.items()))


def build_results() -> dict[str, object]:
    all_factor_edges = tuple(edge for factor in FACTORS for edge in factor)
    if len(all_factor_edges) != 66 or len(set(all_factor_edges)) != 66:
        raise AssertionError("K12 factorization failed")

    adjacency = build_restricted_x_adjacency()
    cross_two_factor = build_cross_two_factor()
    gram = required_xy_gram(adjacency)
    pair_sets = tuple(
        allowed_pairs(factor_index)
        for factor_index in WITHIN_FACTOR_INDICES
    )
    valid_total, valid_by_edges = valid_block_type_census(adjacency, pair_sets)

    cross_distributions = {}
    for left_fibre, right_fibre in ((0, 1), (0, 2), (1, 2)):
        values = [
            gram[left_fibre * N + left][right_fibre * N + right]
            for left in range(N)
            for right in range(N)
        ]
        cross_distributions[f"{left_fibre}{right_fibre}"] = {
            str(key): value
            for key, value in distribution(values).items()
        }

    pair_01 = pair_concurrence(
        pair_sets[0],
        pair_sets[1],
        PAIR_01_CERTIFICATE,
    )
    required_01 = [
        row[N : 2 * N]
        for row in gram[:N]
    ]
    if pair_01 != required_01:
        raise AssertionError("pairwise certificate does not realize K01")

    endpoint_prisms = (4158 - N3_ENDPOINT) // 3
    endpoint_q_sum = 2 * N3_ENDPOINT // 3
    endpoint_q = endpoint_q_sum // TRIANGLE_COUNT

    return {
        "claim_label": "UNKNOWN",
        "endpoint": {
            "n3": N3_ENDPOINT,
            "triangular_prisms": endpoint_prisms,
            "q_sum": endpoint_q_sum,
            "q_per_triangle": endpoint_q,
            "disjoint_triangle_profile_a0_a1_a2_a3": [32, 144, 36, 0],
        },
        "format": "wave35-n3-4158-combinatorial-v1",
        "general_triangle_fibre_lemmas": {
            "cell_sizes_T_X_Y": [3, 36, 60],
            "degrees_from_X_into_T_X_Y": [1, 3, 10],
            "degrees_from_Y_into_T_X_Y": [0, 6, 8],
            "X_to_Y_biregular_degrees": [10, 6],
            "same_fibre_Y_block_rule": (
                "matching pairs occur zero times; every other pair occurs once"
            ),
            "xy_gram_formula": "B B^T = 12I - A_X + 2J - R R^T - A_X^2",
            "endpoint_cross_two_factor": (
                "all cycles have length divisible by 3 and at least 6"
            ),
        },
        "restricted_core": {
            "normalization": {
                "cross_matchings_X0X1_X1X2": "identity",
                "cross_matching_X2X0_factor": 0,
                "within_fibre_factor_indices": list(WITHIN_FACTOR_INDICES),
            },
            "sigma_cycle_lengths": list(cycle_lengths(cross_two_factor)),
            "x_vertex_count": len(adjacency),
            "x_edge_count": sum(map(sum, adjacency)) // 2,
            "x_degree_set": sorted(set(map(sum, adjacency))),
            "x_triangle_count": triangle_count(adjacency),
            "required_gram_entry_distribution": {
                str(key): value
                for key, value in distribution(
                    [value for row in gram for value in row]
                ).items()
            },
            "required_gram_row_sum_set": sorted(set(map(sum, gram))),
            "required_gram_gf2_rank": gf2_rank(gram),
            "x_adjacency_gf2_rank": gf2_rank(adjacency),
            "allowed_pair_count_per_fibre": [len(pairs) for pairs in pair_sets],
            "valid_single_block_type_count": valid_total,
            "valid_single_block_types_by_internal_X_edges": {
                str(key): value
                for key, value in valid_by_edges.items()
            },
            "cross_gram_entry_distributions": cross_distributions,
        },
        "pairwise_control": {
            "scope": "X0-X1 pair system only",
            "certificate": list(PAIR_01_CERTIFICATE),
            "certificate_is_permutation": True,
            "certificate_realizes_required_cross_gram": True,
        },
        "limitations": [
            "The normalized factor choices are restricted and not exhaustive.",
            "The 183980 objects are individual block types, not a 60-block design.",
            "The pairwise certificate does not realize all three fibres simultaneously.",
            "No 60-block system, 99-vertex graph, or nonexistence proof is supplied.",
            "Conway-99 and the n3=4158 endpoint remain UNKNOWN.",
        ],
    }


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


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
