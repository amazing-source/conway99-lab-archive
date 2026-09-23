#!/usr/bin/env python3
"""Discovery-side prism-free rank-27 equality obstruction.

This checker starts from the independently verified Wave 42 decomposition

    rank(K39) = (25 - 2e) + 2 rank(F) + rank(D),
    rank(F) >= e,

for an edge-local partition with ``e`` even parts.  At the prism-free
endpoint only the four types 222, 24, 33, and 6 are possible, and the third
cross-fibre permutation is a derangement.

The complete target of this file is deliberately narrower than universal
rank 28.  It checks all rank-27 mechanisms for the three even endpoint types:

* rank(F)=e and rank(D)=2;
* rank(F)=e+1 and rank(D)=0.

For type 6, the first mechanism is a direct 288 by 10,395 exact enumeration.
The second is an exact pivot/mate CSP over all labelled derangements.  For
types 222 and 24 a complete labelled subspace cover proves that every
derangement has rank(F) at least e+2, so neither mechanism can occur.

The all-odd endpoint type 33 is not covered.  Consequently this package does
not by itself prove a prism-free rank-28 theorem.  Discovery cannot verify
its own conclusions.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import numpy as np


PRIME = 7
SIDE = 12
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WAVE41 = ROOT / "verification/wave41-rank26-secondary/secondary_check.py"
WAVE42_RESULT = ROOT / "verification/wave42-rank27/independent-results.json"
ENDPOINT_EVEN_PARTITIONS = ((2, 2, 2), (4, 2), (6,))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def load_wave41():
    spec = importlib.util.spec_from_file_location("wave41_frozen", WAVE41)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen Wave 41 verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.audit_frozen_inputs()
    return module


def is_derangement(permutation: Sequence[int]) -> bool:
    return all(left != right for left, right in enumerate(permutation))


def determinant_three(values: np.ndarray) -> np.ndarray:
    """Vectorized 3-by-3 determinant over F_7."""

    return (
        values[:, 0, 0]
        * (
            values[:, 1, 1] * values[:, 2, 2]
            - values[:, 1, 2] * values[:, 2, 1]
        )
        - values[:, 0, 1]
        * (
            values[:, 1, 0] * values[:, 2, 2]
            - values[:, 1, 2] * values[:, 2, 0]
        )
        + values[:, 0, 2]
        * (
            values[:, 1, 0] * values[:, 2, 1]
            - values[:, 1, 1] * values[:, 2, 0]
        )
    ) % PRIME


def rank_at_most_two_mask(values: np.ndarray) -> np.ndarray:
    """Return the exact rank-at-most-two mask using every 3-by-3 minor."""

    if values.ndim != 3 or values.shape[1] != values.shape[2]:
        raise ValueError("expected a batch of square matrices")
    dimension = values.shape[1]
    triples = tuple(itertools.combinations(range(dimension), 3))
    survivors = np.ones(values.shape[0], dtype=bool)
    for rows in triples:
        for columns in triples:
            indices = np.flatnonzero(survivors)
            if not indices.size:
                return survivors
            submatrices = values[indices][:, rows, :][:, :, columns]
            rejected = determinant_three(submatrices) != 0
            survivors[indices[rejected]] = False
    return survivors


def projected_matching_forms(
    z: Sequence[Sequence[int]],
    edges: Sequence[tuple[int, int]],
    pairing_indices: Sequence[Sequence[int]],
) -> np.ndarray:
    """Return every Z^T W_R Z in the frozen labelled matching order."""

    z_array = np.asarray(z, dtype=np.int16)
    sums = z_array.sum(axis=0, dtype=np.int16)
    base = np.outer(sums, sums) - z_array.T @ z_array
    contributions = np.asarray(
        [
            -2
            * (
                np.outer(z_array[left], z_array[right])
                + np.outer(z_array[right], z_array[left])
            )
            for left, right in edges
        ],
        dtype=np.int16,
    )
    indices = np.asarray(pairing_indices, dtype=np.int16)
    return np.asarray(
        (base[None, :, :] + contributions[indices].sum(axis=1)) % PRIME,
        dtype=np.int8,
    )


def maximum_support_matching(
    allowed_by_left: Sequence[Sequence[int]],
) -> tuple[int, tuple[int, ...] | None]:
    """Maximum bipartite matching, with a perfect matching if one exists."""

    owner = [-1] * SIDE

    def augment(left: int, seen: int) -> bool:
        for right in allowed_by_left[left]:
            bit = 1 << right
            if seen & bit:
                continue
            previous = owner[right]
            if previous < 0 or augment(previous, seen | bit):
                owner[right] = left
                return True
        return False

    cardinality = sum(augment(left, 0) for left in range(SIDE))
    if cardinality != SIDE:
        return cardinality, None
    permutation = [-1] * SIDE
    for right, left in enumerate(owner):
        permutation[left] = right
    return cardinality, tuple(permutation)


def packed_basis(space: Sequence[Sequence[int]]) -> bytes:
    return bytes(value % PRIME for row in space for value in row)


def generated_spaces_stream(
    lines: Sequence[tuple[int, ...]],
    dimension: int,
    wave41,
) -> Iterator[tuple[tuple[int, ...], ...]]:
    """Deduplicate generated subspaces without materializing combinations."""

    seen: set[bytes] = set()
    for generators in itertools.combinations(lines, dimension):
        space = wave41.canonical_span(generators)
        if len(space) != dimension:
            continue
        key = packed_basis(space)
        if key in seen:
            continue
        seen.add(key)
        yield space


def derangement_rank_cover(
    partition: tuple[int, ...],
    target_rank: int,
    wave41,
) -> tuple[dict[str, object], tuple[tuple[int, ...], ...]]:
    """Cover every F with rank at most target_rank by generated subspaces."""

    signatures = wave41.signature_table(partition)
    lines = sorted(
        {
            wave41.projective(vector)
            for vector in signatures.values()
            if any(vector)
        }
    )
    candidate_generator_sets = 0
    distinct_spaces = 0
    spaces_with_perfect_support = 0
    maximum_derangement_support = 0
    derangement_permutations: set[tuple[int, ...]] = set()

    # Any rank-r assignment has its nonzero column lines in an r-space
    # generated by at most r observed lines.  Zero columns belong to every
    # space.  Therefore this stream covers every permutation of rank <= r.
    for space in generated_spaces_stream(lines, target_rank, wave41):
        distinct_spaces += 1
        allowed = [
            tuple(
                right
                for right in range(SIDE)
                if left != right
                and wave41.belongs(signatures[(left, right)], space)
            )
            for left in range(SIDE)
        ]
        cardinality, witness = maximum_support_matching(allowed)
        maximum_derangement_support = max(maximum_derangement_support, cardinality)
        if witness is not None:
            spaces_with_perfect_support += 1
            allowed_edges = {
                (left, right)
                for left, rights in enumerate(allowed)
                for right in rights
            }
            for permutation in wave41.permutations_in_support(allowed_edges):
                actual_rank = wave41.rank(
                    [
                        signatures[(left, right)]
                        for left, right in enumerate(permutation)
                    ]
                )
                if actual_rank <= target_rank:
                    derangement_permutations.add(permutation)

    # The number is recorded independently of the streaming/dedup logic.
    candidate_generator_sets = math.comb(len(lines), target_rank)
    ordered_permutations = tuple(sorted(derangement_permutations))
    permutation_stream = hashlib.sha256()
    rank_histogram: Counter[int] = Counter()
    for permutation in ordered_permutations:
        permutation_stream.update(bytes(permutation))
        rank_histogram[
            wave41.rank(
                [
                    signatures[(left, right)]
                    for left, right in enumerate(permutation)
                ]
            )
        ] += 1
    record = {
        "partition": list(partition),
        "target_F_rank_at_most": target_rank,
        "observed_projective_lines": len(lines),
        "candidate_generator_sets": candidate_generator_sets,
        "distinct_generated_subspaces": distinct_spaces,
        "spaces_with_derangement_perfect_support": spaces_with_perfect_support,
        "maximum_derangement_support_size": maximum_derangement_support,
        "low_F_derangement_permutation_count": len(ordered_permutations),
        "low_F_derangement_rank_histogram": {
            str(rank): count for rank, count in sorted(rank_histogram.items())
        },
        "low_F_derangement_permutation_stream_sha256":
            permutation_stream.hexdigest(),
        "low_F_derangements_first_20": [
            list(value) for value in ordered_permutations[:20]
        ],
        "coverage": (
            "Every permutation whose projected F columns span dimension at "
            "most the target lies in a target-dimensional subspace generated "
            "by observed projective lines. Every such distinct subspace is "
            "enumerated, diagonal assignments are removed, and exact "
            "bipartite matching tests derangement support."
        ),
    }
    return record, ordered_permutations


def zero_residual_explicit(
    partition: tuple[int, ...],
    permutations: Sequence[tuple[int, ...]],
    target_F_rank: int,
    wave41,
) -> dict[str, object]:
    """Test every labelled R for an explicit low-F permutation stream."""

    context = wave41.partition_context(partition)
    edges, pairing_indices, _ = wave41.pairing_index_data()
    pairings = tuple(wave41.all_pairings())
    tested_pairs = 0
    zero_residual_pairs = 0
    witnesses: list[dict[str, object]] = []
    solution_stream = hashlib.sha256()
    for permutation in permutations:
        data = wave41.fast_quotient_data(context, permutation)
        require(data["F_rank"] == target_F_rank, "wrong explicit F rank")
        forms = projected_matching_forms(data["Z"], edges, pairing_indices)
        target = np.asarray(data["target"], dtype=np.int8)
        hits = np.flatnonzero(np.all(forms == target[None, :, :], axis=(1, 2)))
        tested_pairs += len(pairing_indices)
        zero_residual_pairs += int(hits.size)
        for matching_index in hits:
            matching = pairings[int(matching_index)]
            full_rank = wave41.rank(
                wave41.full_block(partition, permutation, matching)
            )
            require(full_rank == 27, "zero residual did not lift to rank 27")
            solution_stream.update(
                bytes(permutation)
                + int(matching_index).to_bytes(2, "big")
            )
            if len(witnesses) < 20:
                witnesses.append(
                    {
                        "permutation": list(permutation),
                        "matching_index": int(matching_index),
                        "matching": [list(edge) for edge in matching],
                        "full_K39_rank_F7": full_rank,
                    }
                )
    return {
        "partition": list(partition),
        "target_F_rank": target_F_rank,
        "explicit_derangement_permutations": len(permutations),
        "labelled_R_per_permutation": len(pairing_indices),
        "tested_derangement_R_pairs": tested_pairs,
        "zero_residual_pairs": zero_residual_pairs,
        "rank27_witnesses_first_20": witnesses,
        "solution_stream_sha256": solution_stream.hexdigest(),
        "completeness": (
            "The preceding generated-subspace cover emits every labelled "
            "derangement of the target F rank. Every one of the 10,395 "
            "labelled perfect matchings is tested by exact projected-form "
            "equality for every emitted permutation."
        ),
    }


def type6_minimum_rank_two_residual(wave41) -> dict[str, object]:
    """Check all prism-free rank(F)=1 pairs for residual rank at most two."""

    partition = (6,)
    even_parts, permutations, census = wave41.minimum_f_permutations(partition)
    require(even_parts == 1, "type 6 even-part count changed")
    derangements = tuple(value for value in permutations if is_derangement(value))
    require(len(derangements) == 288, "type 6 minimum derangement count changed")
    context = wave41.partition_context(partition)
    edges, pairing_indices, _ = wave41.pairing_index_data()
    pairings = tuple(wave41.all_pairings())
    pairing_stream = hashlib.sha256()
    for pairing in pairings:
        pairing_stream.update(bytes(value for edge in pairing for value in edge))

    tested_pairs = 0
    rank_at_most_two_pairs = 0
    rank_exactly_two_pairs = 0
    witnesses: list[dict[str, object]] = []
    permutation_stream = hashlib.sha256()
    candidate_stream = hashlib.sha256()

    for permutation in derangements:
        permutation_stream.update(bytes(permutation))
        data = wave41.fast_quotient_data(context, permutation)
        require(data["F_rank"] == 1, "minimum stream changed rank")
        forms = projected_matching_forms(data["Z"], edges, pairing_indices)
        residuals = (
            forms.astype(np.int16)
            - np.asarray(data["target"], dtype=np.int16)[None, :, :]
        ) % PRIME
        mask = rank_at_most_two_mask(residuals)
        locations = np.flatnonzero(mask)
        tested_pairs += len(pairing_indices)
        rank_at_most_two_pairs += int(locations.size)
        for matching_index in locations:
            residual = residuals[int(matching_index)].astype(int).tolist()
            residual_rank = wave41.rank(residual)
            require(residual_rank <= 2, "minor predicate emitted rank above two")
            if residual_rank == 2:
                rank_exactly_two_pairs += 1
            candidate_stream.update(
                bytes(permutation)
                + int(matching_index).to_bytes(2, "big")
                + bytes(value for row in residual for value in row)
            )
            if len(witnesses) < 20:
                matching = pairings[int(matching_index)]
                full_rank = wave41.rank(
                    wave41.full_block(partition, permutation, matching)
                )
                witnesses.append(
                    {
                        "permutation": list(permutation),
                        "matching_index": int(matching_index),
                        "matching": [list(edge) for edge in matching],
                        "residual_rank_F7": residual_rank,
                        "residual": residual,
                        "full_K39_rank_F7": full_rank,
                    }
                )

    return {
        "partition": [6],
        "minimum_F_rank": 1,
        "minimum_F_permutations_all": len(permutations),
        "minimum_F_derangements": len(derangements),
        "minimum_F_subspace_census": census,
        "labelled_R_matchings": len(pairing_indices),
        "tested_minimum_F_derangement_R_pairs": tested_pairs,
        "rank_at_most_two_residual_pairs": rank_at_most_two_pairs,
        "rank_exactly_two_residual_pairs": rank_exactly_two_pairs,
        "rank27_witnesses_first_20": witnesses,
        "permutation_stream_sha256": permutation_stream.hexdigest(),
        "pairing_stream_sha256": pairing_stream.hexdigest(),
        "candidate_stream_sha256": candidate_stream.hexdigest(),
        "completeness": (
            "All 288 labelled minimum-F derangements and all 10,395 labelled "
            "third-fibre matchings are explicit. Every 3-by-3 minor of each "
            "residual is tested; rank at most two is equivalent to their "
            "simultaneous vanishing."
        ),
    }


def projective_line(vector: Sequence[int], wave41) -> tuple[int, ...]:
    return wave41.projective(vector)


def solve_two_coefficients(
    vector: Sequence[int],
    first: Sequence[int],
    second: Sequence[int],
) -> tuple[int, int]:
    for left in range(PRIME):
        for right in range(PRIME):
            if all(
                (left * a + right * b - c) % PRIME == 0
                for a, b, c in zip(first, second, vector)
            ):
                return left, right
    raise ValueError("vector is outside the pivot span")


def type6_rank_two_zero_residual_csp(wave41) -> dict[str, object]:
    """Exhaust all type-6 rank(F)=2 derangements with residual zero.

    Coordinate 0 is the first F pivot.  Coordinate q is canonically the first
    later coordinate on a different projective line.  Branching on the mates
    of 0 and q fixes every pivot/free matching entry.  The zero-residual
    diagonal equations give unary assignment constraints, while the
    off-diagonal equations determine whether each free pair must or must not
    be an R edge.  Exact all-different backtracking then covers every labelled
    permutation and every labelled R matching without materializing 12!.
    """

    partition = (6,)
    context = wave41.partition_context(partition)
    signatures = context["signatures"]
    interaction = context["interaction"]
    inverse_two = pow(2, -1, PRIME)

    def signature(left: int, right: int) -> tuple[int, ...]:
        return tuple(signatures[12 * left + right])

    def sym_interaction(
        left: int, right: int, other_left: int, other_right: int
    ) -> int:
        first = 12 * left + right
        second = 12 * other_left + other_right
        return (
            inverse_two
            * (interaction[first][second] + interaction[second][first])
        ) % PRIME

    pivot_assignment_branches = 0
    mate_branches = 0
    unary_viable_branches = 0
    backtrack_nodes = 0
    complete_permutations = 0
    residual_zero_pairs = 0
    solution_stream = hashlib.sha256()
    witnesses: list[dict[str, object]] = []

    pivot = 0
    for pivot_image in range(1, SIDE):  # endpoint derangement
        first_vector = signature(pivot, pivot_image)
        first_line = projective_line(first_vector, wave41)
        for second_pivot in range(1, SIDE):
            for second_image in range(SIDE):
                if second_image in (pivot_image, second_pivot):
                    continue
                second_vector = signature(second_pivot, second_image)
                if projective_line(second_vector, wave41) == first_line:
                    continue
                pivot_assignment_branches += 1
                free = tuple(
                    value
                    for value in range(SIDE)
                    if value not in (pivot, second_pivot)
                )

                mate_cases: list[tuple[int, int]] = [(second_pivot, pivot)]
                mate_cases.extend(
                    (mate_pivot, mate_second)
                    for mate_pivot in free
                    for mate_second in free
                    if mate_second != mate_pivot
                )

                for mate_pivot, mate_second in mate_cases:
                    mate_branches += 1
                    paired_pivots = mate_pivot == second_pivot
                    require(
                        paired_pivots == (mate_second == pivot),
                        "asymmetric pivot mate branch",
                    )
                    pivot_cross = PRIME - 1 if paired_pivots else 1

                    def pivot_w(left: int, which: int) -> int:
                        if which == pivot:
                            return PRIME - 1 if left == mate_pivot else 1
                        if which == second_pivot:
                            return PRIME - 1 if left == mate_second else 1
                        raise ValueError("unknown pivot")

                    candidates: dict[
                        int, list[tuple[int, int, int]]
                    ] = {}
                    viable = True
                    for left in free:
                        values: list[tuple[int, int, int]] = []
                        for right in range(SIDE):
                            if right in (pivot_image, second_image) or right == left:
                                continue
                            vector = signature(left, right)
                            line = projective_line(vector, wave41)
                            if left < second_pivot and line != first_line:
                                continue
                            coefficient_first, coefficient_second = (
                                solve_two_coefficients(
                                    vector, first_vector, second_vector
                                )
                            )
                            a = coefficient_first
                            b = coefficient_second
                            t_ii = sym_interaction(left, right, left, right)
                            t_ip = sym_interaction(
                                left, right, pivot, pivot_image
                            )
                            t_iq = sym_interaction(
                                left, right, second_pivot, second_image
                            )
                            t_pp = sym_interaction(
                                pivot, pivot_image, pivot, pivot_image
                            )
                            t_qq = sym_interaction(
                                second_pivot,
                                second_image,
                                second_pivot,
                                second_image,
                            )
                            t_pq = sym_interaction(
                                pivot,
                                pivot_image,
                                second_pivot,
                                second_image,
                            )
                            target_diagonal = (
                                t_ii
                                - 2 * a * t_ip
                                - 2 * b * t_iq
                                + a * a * t_pp
                                + b * b * t_qq
                                + 2 * a * b * t_pq
                            ) % PRIME
                            matching_diagonal = (
                                -2 * a * pivot_w(left, pivot)
                                - 2 * b * pivot_w(left, second_pivot)
                                + 2 * a * b * pivot_cross
                            ) % PRIME
                            if target_diagonal == matching_diagonal:
                                values.append((right, a, b))
                        if not values:
                            viable = False
                            break
                        candidates[left] = values
                    if not viable:
                        continue
                    unary_viable_branches += 1
                    order = tuple(
                        sorted(free, key=lambda left: (len(candidates[left]), left))
                    )
                    assignment: dict[int, tuple[int, int, int]] = {
                        pivot: (pivot_image, 1, 0),
                        second_pivot: (second_image, 0, 1),
                    }
                    forced_mate: dict[int, int] = {}

                    def is_prepivot_matched(left: int) -> bool:
                        return (
                            (not paired_pivots)
                            and left in (mate_pivot, mate_second)
                        )

                    def required_free_w(
                        left: int,
                        left_data: tuple[int, int, int],
                        other: int,
                        other_data: tuple[int, int, int],
                    ) -> int:
                        left_right, a, b = left_data
                        other_right, c, d = other_data
                        t_ij = sym_interaction(
                            left, left_right, other, other_right
                        )
                        t_ip = sym_interaction(
                            left, left_right, pivot, pivot_image
                        )
                        t_iq = sym_interaction(
                            left,
                            left_right,
                            second_pivot,
                            second_image,
                        )
                        t_pj = sym_interaction(
                            pivot, pivot_image, other, other_right
                        )
                        t_qj = sym_interaction(
                            second_pivot,
                            second_image,
                            other,
                            other_right,
                        )
                        t_pp = sym_interaction(
                            pivot, pivot_image, pivot, pivot_image
                        )
                        t_qq = sym_interaction(
                            second_pivot,
                            second_image,
                            second_pivot,
                            second_image,
                        )
                        t_pq = sym_interaction(
                            pivot,
                            pivot_image,
                            second_pivot,
                            second_image,
                        )
                        target = (
                            t_ij
                            - c * t_ip
                            - d * t_iq
                            - a * t_pj
                            - b * t_qj
                            + a * c * t_pp
                            + (a * d + b * c) * t_pq
                            + b * d * t_qq
                        ) % PRIME
                        return (
                            target
                            + c * pivot_w(left, pivot)
                            + d * pivot_w(left, second_pivot)
                            + a * pivot_w(other, pivot)
                            + b * pivot_w(other, second_pivot)
                            - (a * d + b * c) * pivot_cross
                        ) % PRIME

                    def visit(depth: int, used: int) -> None:
                        nonlocal backtrack_nodes
                        nonlocal complete_permutations
                        nonlocal residual_zero_pairs
                        backtrack_nodes += 1
                        if depth == len(order):
                            for left in free:
                                if is_prepivot_matched(left):
                                    if left in forced_mate:
                                        return
                                elif left not in forced_mate:
                                    return
                            permutation = tuple(
                                assignment[left][0] for left in range(SIDE)
                            )
                            require(is_derangement(permutation), "CSP lost endpoint")
                            data = wave41.fast_quotient_data(context, permutation)
                            require(data["F_rank"] == 2, "CSP lost rank-two F")
                            mate = [-1] * SIDE
                            mate[pivot] = mate_pivot
                            mate[mate_pivot] = pivot
                            mate[second_pivot] = mate_second
                            mate[mate_second] = second_pivot
                            for left, right in forced_mate.items():
                                mate[left] = right
                            require(
                                all(value >= 0 for value in mate),
                                "CSP emitted incomplete R matching",
                            )
                            matching = tuple(
                                (left, mate[left])
                                for left in range(SIDE)
                                if left < mate[left]
                            )
                            residual = wave41.schur_residual(
                                partition, permutation, matching
                            )
                            require(
                                wave41.rank(residual) == 0,
                                "CSP emitted nonzero residual",
                            )
                            full_rank = wave41.rank(
                                wave41.full_block(
                                    partition, permutation, matching
                                )
                            )
                            require(full_rank == 27, "CSP lift is not rank 27")
                            complete_permutations += 1
                            residual_zero_pairs += 1
                            solution_stream.update(
                                bytes(permutation)
                                + bytes(value for edge in matching for value in edge)
                            )
                            if len(witnesses) < 20:
                                witnesses.append(
                                    {
                                        "permutation": list(permutation),
                                        "matching": [
                                            list(edge) for edge in matching
                                        ],
                                        "full_K39_rank_F7": full_rank,
                                    }
                                )
                            return

                        left = order[depth]
                        for candidate in candidates[left]:
                            right = candidate[0]
                            bit = 1 << right
                            if used & bit:
                                continue
                            updates: list[tuple[int, int]] = []
                            compatible = True
                            for other in assignment:
                                if other in (pivot, second_pivot):
                                    continue
                                value = required_free_w(
                                    left, candidate, other, assignment[other]
                                )
                                if value not in (1, PRIME - 1):
                                    compatible = False
                                    break
                                if value == PRIME - 1:
                                    if (
                                        is_prepivot_matched(left)
                                        or is_prepivot_matched(other)
                                        or (
                                            left in forced_mate
                                            and forced_mate[left] != other
                                        )
                                        or (
                                            other in forced_mate
                                            and forced_mate[other] != left
                                        )
                                    ):
                                        compatible = False
                                        break
                                    if left not in forced_mate:
                                        forced_mate[left] = other
                                        updates.append((left, other))
                                    if other not in forced_mate:
                                        forced_mate[other] = left
                                        updates.append((other, left))
                                elif (
                                    forced_mate.get(left) == other
                                    or forced_mate.get(other) == left
                                ):
                                    compatible = False
                                    break
                            if compatible:
                                assignment[left] = candidate
                                visit(depth + 1, used | bit)
                                del assignment[left]
                            for key, value in reversed(updates):
                                require(
                                    forced_mate.get(key) == value,
                                    "mate rollback mismatch",
                                )
                                del forced_mate[key]

                    visit(
                        0,
                        (1 << pivot_image) | (1 << second_image),
                    )

    return {
        "partition": [6],
        "target_F_rank": 2,
        "target_residual_rank": 0,
        "endpoint_derangement": True,
        "canonical_first_pivot": 0,
        "pivot_assignment_branches": pivot_assignment_branches,
        "pivot_mate_branches": mate_branches,
        "unary_viable_branches": unary_viable_branches,
        "backtrack_nodes": backtrack_nodes,
        "complete_permutations": complete_permutations,
        "residual_zero_pairs": residual_zero_pairs,
        "rank27_witnesses_first_20": witnesses,
        "solution_stream_sha256": solution_stream.hexdigest(),
        "completeness": (
            "Every type-6 derangement of F-rank two has coordinate 0 as a "
            "pivot and a unique first later coordinate on a different "
            "projective signature line. Their images are enumerated. Every "
            "perfect matching R is in exactly one branch determined by the "
            "mates of the two pivot coordinates. Exact diagonal equations "
            "give unary domains; exact off-diagonal kernel-form equations "
            "give pairwise mate/nonmate constraints; all-different "
            "backtracking covers every remaining labelled permutation."
        ),
    }


def compute() -> dict[str, object]:
    wave41 = load_wave41()
    wave42 = json.loads(WAVE42_RESULT.read_text(encoding="utf-8"))
    require(
        wave42["status_wall"]["universal_rank_F7_M_lower_bound"] == 27,
        "Wave 42 verified rank floor changed",
    )

    cover_222, permutations_222 = derangement_rank_cover(
        (2, 2, 2), 4, wave41
    )
    cover_42, permutations_42 = derangement_rank_cover((4, 2), 3, wave41)
    covers = {"2+2+2": cover_222, "4+2": cover_42}
    higher_F_zero = {
        "2+2+2": zero_residual_explicit(
            (2, 2, 2), permutations_222, 4, wave41
        ),
        "4+2": zero_residual_explicit((4, 2), permutations_42, 3, wave41),
    }
    minimum = type6_minimum_rank_two_residual(wave41)
    next_boundary = type6_rank_two_zero_residual_csp(wave41)

    even_endpoint_rank27_exists = (
        any(record["zero_residual_pairs"] for record in higher_F_zero.values())
        or bool(minimum["rank_at_most_two_residual_pairs"])
        or bool(next_boundary["residual_zero_pairs"])
    )
    return {
        "format": "wave43-rank28-motif-v1",
        "role": "proof_a",
        "claim_label": "DERIVED",
        "git_commit": "e28f90464d00b98d37672b0b2b23dba15399a6f2",
        "scope": (
            "Complete rank-27 equality exclusion for the three even "
            "edge-local partition types allowed by the conditional "
            "prism-free endpoint."
        ),
        "inputs": {
            "verification/wave41-rank26-secondary/secondary_check.py":
                sha256_file(WAVE41),
            "verification/wave42-rank27/independent-results.json":
                sha256_file(WAVE42_RESULT),
        },
        "premises": {
            "verified_wave42_formula": (
                "rank(K39)=(25-2e)+2 rank(F)+rank(D), rank(F)>=e"
            ),
            "rank27_dichotomy": (
                "rank 27 iff [rank(F)=e and rank(D)=2] or "
                "[rank(F)=e+1 and rank(D)=0]"
            ),
            "conditional_endpoint": (
                "n3=4158, equivalently no induced triangular prism"
            ),
            "endpoint_local_types": ["2+2+2", "4+2", "3+3", "6"],
            "endpoint_cross_permutation": "derangement",
            "automorphism_restriction": "none",
        },
        "low_F_derangement_covers": covers,
        "higher_F_zero_residual_explicit": higher_F_zero,
        "type6_minimum_F_rank2_residual": minimum,
        "type6_next_F_zero_residual": next_boundary,
        "conclusion": {
            "even_endpoint_rank27_exists": even_endpoint_rank27_exists,
            "derived_scoped_theorem": (
                "Conditional on n3=4158, if a base edge has type 222, 24, "
                "or 6, then its 39-point triangle block has F7-rank at least "
                "28."
            ),
            "unresolved_endpoint_type": "3+3",
            "prism_free_rank28_universal": "NOT_PROVED",
            "universal_rank28": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "The all-odd endpoint type 3+3 is not covered.",
            "The theorem is conditional on the prism-free endpoint n3=4158.",
            "A local relaxation is not a completed 99-vertex graph.",
            "No endpoint exclusion, strict general n3 upper bound, novelty, "
            "or priority claim is made.",
        ],
    }


def validate(result: dict[str, object]) -> None:
    require(result["format"] == "wave43-rank28-motif-v1", "format changed")
    require(result["claim_label"] == "DERIVED", "status inflation")
    require(
        set(result["low_F_derangement_covers"]) == {"2+2+2", "4+2"},
        "cover scope changed",
    )
    for record in result["low_F_derangement_covers"].values():
        require(
            record["low_F_derangement_permutation_count"] > 0,
            "expected low-F derangement stream disappeared",
        )
    for record in result["higher_F_zero_residual_explicit"].values():
        require(record["explicit_derangement_permutations"] > 0, "empty cover")
        require(
            record["tested_derangement_R_pairs"]
            == record["explicit_derangement_permutations"] * 10_395,
            "explicit zero-residual pair coverage changed",
        )
        require(record["zero_residual_pairs"] == 0, "zero residual appeared")
    minimum = result["type6_minimum_F_rank2_residual"]
    require(minimum["minimum_F_derangements"] == 288, "derangement census")
    require(
        minimum["tested_minimum_F_derangement_R_pairs"] == 288 * 10_395,
        "explicit pair coverage changed",
    )
    require(
        minimum["rank_at_most_two_residual_pairs"] == 0,
        "rank-two residual appeared",
    )
    require(
        result["type6_next_F_zero_residual"]["residual_zero_pairs"] == 0,
        "zero residual appeared",
    )
    require(
        not result["conclusion"]["even_endpoint_rank27_exists"],
        "scoped conclusion changed",
    )
    require(
        result["conclusion"]["unresolved_endpoint_type"] == "3+3",
        "scope wall lost",
    )
    require(
        result["conclusion"]["prism_free_rank28_universal"] == "NOT_PROVED",
        "universal claim inflated",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = compute()
    validate(result)
    payload = canonical_json(result)
    if args.verify:
        require(args.verify.read_bytes() == payload, "stored result differs")
        print(
            f"PASS {args.verify} "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
        print(
            f"WROTE {args.output} "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
