#!/usr/bin/env python3
"""Deterministic bounded scout of the fully specified 39-vertex local block.

This is deliberately not an exhaustive result.  It restores the perfect
matching inside the third fibre Z and samples both that matching and the
Y--Z permutation.  The proved rank-25 floor comes from ``exact_check.py`` and
does not depend on this scout.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

import exact_check as exact


FORMAT = "wave40-full-39-block-bounded-scout-v1"
SEED = 20_260_727
SAMPLES_PER_TYPE = 512


def all_matchings() -> tuple[tuple[int, ...], ...]:
    return tuple(
        exact.matching_map(edges)
        for edges in exact.pairings(tuple(range(exact.SIDE_SIZE)))
    )


def core_adjacency(
    pulled_y_matching: tuple[int, ...],
    yz_permutation: tuple[int, ...],
    z_matching: tuple[int, ...],
) -> list[list[int]]:
    """Return the cubic 36-vertex three-fibre core adjacency."""

    adjacency = [[0] * 36 for _ in range(36)]
    for index in range(exact.SIDE_SIZE):
        exact.add_edge(adjacency, index, 12 + index)
        exact.add_edge(adjacency, index, 24 + index)
        exact.add_edge(adjacency, 12 + yz_permutation[index], 24 + index)
    for matching, offset in (
        (exact.STANDARD_MATCHING, 0),
        (pulled_y_matching, 12),
        (z_matching, 24),
    ):
        for left, right in enumerate(matching):
            if left < right:
                exact.add_edge(adjacency, offset + left, offset + right)
    if {sum(row) for row in adjacency} != {3}:
        raise AssertionError("three-fibre core is not cubic")
    return adjacency


def full_block(
    pulled_y_matching: tuple[int, ...],
    yz_permutation: tuple[int, ...],
    z_matching: tuple[int, ...],
) -> list[list[int]]:
    adjacency = [[0] * exact.THREE_FIBRE_SIZE for _ in range(exact.THREE_FIBRE_SIZE)]

    def add(left: int, right: int) -> None:
        exact.add_edge(adjacency, left, right)

    for left, right in ((0, 1), (0, 2), (1, 2)):
        add(left, right)
    for index in range(exact.SIDE_SIZE):
        add(0, 3 + index)
        add(1, 15 + index)
        add(2, 27 + index)
        add(3 + index, 15 + index)
        add(3 + index, 27 + index)
        add(15 + yz_permutation[index], 27 + index)
    for matching, offset in (
        (exact.STANDARD_MATCHING, 3),
        (pulled_y_matching, 15),
        (z_matching, 27),
    ):
        for left, right in enumerate(matching):
            if left < right:
                add(offset + left, offset + right)
    return exact.seidel_matrix(adjacency)


def core_laplacian_rank(core: list[list[int]]) -> int:
    return exact.rank_mod_prime(
        [
            [3 * int(row == column) - core[row][column] for column in range(36)]
            for row in range(36)
        ]
    )


def component_sizes(adjacency: list[list[int]]) -> list[int]:
    unseen = set(range(len(adjacency)))
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
                neighbour
                for neighbour, present in enumerate(adjacency[vertex])
                if present and neighbour in unseen
            )
        sizes.append(size)
    return sorted(sizes)


def quotient_rank_audit() -> dict[str, object]:
    identity = [[int(row == column) for column in range(3)] for row in range(3)]
    ones = [[1] * 3 for _ in range(3)]

    def combination(i_coefficient: int, j_coefficient: int) -> list[list[int]]:
        return [
            [
                (i_coefficient * identity[row][column] + j_coefficient)
                % exact.PRIME
                for column in range(3)
            ]
            for row in range(3)
        ]

    blocks = (
        (combination(1, -1), combination(4, 5)),
        (combination(-2, 1), combination(6, 3)),
    )
    seidel_quotient = [
        [
            blocks[row // 3][column // 3][row % 3][column % 3]
            for column in range(6)
        ]
        for row in range(6)
    ]
    laplacian_quotient = [
        [
            (3 * identity[row][column] - ones[row][column]) % exact.PRIME
            for column in range(3)
        ]
        for row in range(3)
    ]
    seidel_rank = exact.rank_mod_prime(seidel_quotient)
    laplacian_rank = exact.rank_mod_prime(laplacian_quotient)
    if (seidel_rank, laplacian_rank) != (3, 2):
        raise AssertionError("three-fibre quotient rank audit changed")
    return {
        "K39_triangle_plus_fibre_constant_matrix_F7": seidel_quotient,
        "K39_quotient_rank_F7": seidel_rank,
        "core_3I_minus_A_quotient_matrix_F7": laplacian_quotient,
        "core_quotient_rank_F7": laplacian_rank,
    }


def derive() -> dict[str, object]:
    rng = random.Random(SEED)
    matchings = all_matchings()
    catalog = exact.matching_catalog()
    identity_permutation = tuple(range(exact.SIDE_SIZE))
    aligned_core = core_adjacency(
        exact.STANDARD_MATCHING,
        identity_permutation,
        exact.STANDARD_MATCHING,
    )
    aligned_block = full_block(
        exact.STANDARD_MATCHING,
        identity_permutation,
        exact.STANDARD_MATCHING,
    )
    aligned_laplacian_rank = core_laplacian_rank(aligned_core)
    aligned_block_rank = exact.rank_mod_prime(aligned_block)
    if aligned_block_rank != 1 + aligned_laplacian_rank:
        raise AssertionError("aligned control violates the block-rank identity")
    records: list[dict[str, object]] = []
    for partition in sorted(catalog):
        representative = tuple(catalog[partition]["representative"])
        histogram: Counter[int] = Counter()
        minimum = 100
        witness: dict[str, object] | None = None
        for _ in range(SAMPLES_PER_TYPE):
            permutation_list = list(range(exact.SIDE_SIZE))
            rng.shuffle(permutation_list)
            permutation = tuple(permutation_list)
            z_matching = matchings[rng.randrange(len(matchings))]
            core = core_adjacency(representative, permutation, z_matching)
            rank = exact.rank_mod_prime(full_block(representative, permutation, z_matching))
            laplacian_rank = core_laplacian_rank(core)
            if rank != 1 + laplacian_rank:
                raise AssertionError("sample violates rank(K39)=1+rank(3I-A_core)")
            histogram[rank] += 1
            if rank < minimum:
                minimum = rank
                witness = {
                    "Y_Z_permutation": list(permutation),
                    "Z_matching": list(z_matching),
                    "rank_F7": rank,
                }
        if witness is None:
            raise AssertionError("bounded scout generated no sample")
        records.append(
            {
                "partition": list(partition),
                "partition_key": exact.partition_key(partition),
                "sample_count": SAMPLES_PER_TYPE,
                "rank_histogram": {
                    str(rank): histogram[rank] for rank in sorted(histogram)
                },
                "minimum_sampled_rank_F7": minimum,
                "minimum_witness": witness,
            }
        )
    return {
        "format": FORMAT,
        "claim_label": "BOUNDED_SCOUT_NON_EVIDENTIARY",
        "seed": SEED,
        "samples_per_partition_type": SAMPLES_PER_TYPE,
        "partition_type_count": len(records),
        "exact_block_rank_identity": {
            "identity": "rank_F7(K_39)=1+rank_F7(3I_36-A_core)",
            "scope": (
                "every three-fibre block with the forced three equal fibres, "
                "internal matchings, and pairwise perfect matchings"
            ),
            "derivation": (
                "The 36-space splits into the three-dimensional fibre-constant "
                "space and ker(R). The cubic equitable quotient is J_3. On "
                "ker(R), K_39 is 2(3I-A_core); exact reduction on the six "
                "triangle/fibre-constant coordinates has rank 3 while "
                "3I-A_core has quotient rank 2."
            ),
            "quotient_audit": quotient_rank_audit(),
        },
        "aligned_positive_control": {
            "partition": [1, 1, 1, 1, 1, 1],
            "Y_Z_permutation": list(identity_permutation),
            "Z_matching": list(exact.STANDARD_MATCHING),
            "core_component_sizes": component_sizes(aligned_core),
            "core_laplacian_rank_F7": aligned_laplacian_rank,
            "full_39_block_rank_F7": aligned_block_rank,
            "scope": (
                "exact relaxed local control; it contains type-1/prism "
                "structure and is not a prism-free endpoint or full graph"
            ),
        },
        "records": records,
        "interpretation": (
            "Every sample restores the theorem-forced perfect matching inside "
            "Z and uses a bijective Y-Z attachment. The sample is not an "
            "exhaustion, and its minima are not rank lower bounds. The aligned "
            "rank-31 control is exact and lies outside the random sample."
        ),
        "proved_floor_from_exact_census": 25,
        "limitations": [
            "Only 512 of 12!*10395 labelled (permutation,Z-matching) pairs are sampled per type.",
            "No completed-graph automorphism quotient or complete orbit census is claimed.",
            "The 39-vertex controls need not extend to a 99-vertex SRG.",
            "The sampled minima cannot improve the proved rank floor.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path)
    mode.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = exact.canonical_json(derive())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
        print(json.dumps({"output": str(args.output), "sha256": exact.sha256_bytes(payload)}))
        return 0
    if args.verify.read_bytes() != payload:
        raise SystemExit("stored full-block scout differs from deterministic regeneration")
    print("PASS: bounded full-block scout matches deterministic regeneration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
