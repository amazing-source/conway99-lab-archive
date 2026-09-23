#!/usr/bin/env python3
"""Classify every canonical rank-33 lift at the Wave 42 B-boundary.

This is a discovery checker.  It imports the frozen Wave 41 labelled lift
generator, reconstructs all 264 triangle-free rank-33 masks, and applies only
the exact necessary ``BB^T`` identities used in Wave 42.  It does not assume
an automorphism of a completed graph and does not decide the endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Sequence


FORMAT = "wave43-all-rank33-lifts-v1"
FROZEN_COMMIT = "e28f90464d00b98d37672b0b2b23dba15399a6f2"
SOURCE_CODE = Path("attempts/wave41-allquotient-lifts/exact_check.py")
SOURCE_CODE_SHA256 = (
    "9a94a08dfec20a72c335168714a047f92e1aff09ac05bdd827a78ce2deb45e76"
)
FIBRES = 3
FIBRE_SIZE = 12
X_SIZE = 36


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_wave41(path: Path = SOURCE_CODE) -> ModuleType:
    raw = path.read_bytes()
    require(sha256_bytes(raw) == SOURCE_CODE_SHA256, "Wave 41 source hash changed")
    spec = importlib.util.spec_from_file_location("wave41_allquotient", path)
    require(spec is not None and spec.loader is not None, "cannot load Wave 41 source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def components(adjacency: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    unseen = set(range(X_SIZE))
    result: list[tuple[int, ...]] = []
    while unseen:
        start = min(unseen)
        seen = {start}
        stack = [start]
        while stack:
            vertex = stack.pop()
            for neighbor in adjacency[vertex]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        unseen -= seen
        result.append(tuple(sorted(seen)))
    return tuple(sorted(result, key=lambda item: (len(item), item)))


def adjacency_matrix(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    result = [[0] * X_SIZE for _ in range(X_SIZE)]
    for left, neighbors in enumerate(adjacency):
        for right in neighbors:
            result[left][right] = 1
    require(result == [list(row) for row in zip(*result)], "adjacency not symmetric")
    require(set(map(sum, result)) == {3}, "core is not cubic")
    return result


def matrix_square(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            sum(matrix[left][middle] * matrix[middle][right] for middle in range(X_SIZE))
            for right in range(X_SIZE)
        ]
        for left in range(X_SIZE)
    ]


def forced_gram(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    square = matrix_square(adjacency)
    return [
        [
            (12 if left == right else 0)
            - adjacency[left][right]
            + 2
            - (1 if left // FIBRE_SIZE == right // FIBRE_SIZE else 0)
            - square[left][right]
            for right in range(X_SIZE)
        ]
        for left in range(X_SIZE)
    ]


def four_cycle_count(adjacency: Sequence[Sequence[int]]) -> int:
    opposite_pairs = 0
    for left, right in itertools.combinations(range(X_SIZE), 2):
        common = sum(
            adjacency[left][middle] and adjacency[right][middle]
            for middle in range(X_SIZE)
        )
        opposite_pairs += common * (common - 1) // 2
    require(opposite_pairs % 2 == 0, "four-cycle count parity failed")
    return opposite_pairs // 2


def allowed_pairs(
    fibre: int,
    gram: Sequence[Sequence[int]],
) -> tuple[tuple[int, int], ...]:
    start = fibre * FIBRE_SIZE
    return tuple(
        pair
        for pair in itertools.combinations(range(start, start + FIBRE_SIZE), 2)
        if gram[pair[0]][pair[1]] == 1
    )


def pair_cross_compatible(
    left: Sequence[int],
    right: Sequence[int],
    gram: Sequence[Sequence[int]],
) -> bool:
    return all(gram[u][v] > 0 for u in left for v in right)


def candidate_census(
    adjacency: Sequence[Sequence[int]],
    gram: Sequence[Sequence[int]],
    small_component: frozenset[int],
) -> dict[str, object]:
    pair_sets = tuple(allowed_pairs(fibre, gram) for fibre in range(FIBRES))
    require(tuple(map(len, pair_sets)) == (60, 60, 60), "pair census changed")
    pair_masks = tuple(
        tuple((1 << left) | (1 << right) for left, right in pairs)
        for pairs in pair_sets
    )
    small_counts = tuple(
        tuple(sum(vertex in small_component for vertex in pair) for pair in pairs)
        for pairs in pair_sets
    )
    compatibility_02 = [
        sum(
            1 << k
            for k, right in enumerate(pair_sets[2])
            if pair_cross_compatible(left, right, gram)
        )
        for left in pair_sets[0]
    ]
    compatibility_12 = [
        sum(
            1 << k
            for k, right in enumerate(pair_sets[2])
            if pair_cross_compatible(left, right, gram)
        )
        for left in pair_sets[1]
    ]
    pattern_k = {
        value: sum(
            1 << k for k, count in enumerate(small_counts[2]) if count == value
        )
        for value in (0, 1, 2)
    }
    neighbor_masks = tuple(
        sum(1 << right for right, value in enumerate(row) if value)
        for row in adjacency
    )

    support_legal = 0
    component_legal = 0
    mixed_legal = 0
    mixed_patterns: Counter[tuple[int, int, int]] = Counter()
    for i, pair0 in enumerate(pair_sets[0]):
        for j, pair1 in enumerate(pair_sets[1]):
            if not pair_cross_compatible(pair0, pair1, gram):
                continue
            compatible_k = compatibility_02[i] & compatibility_12[j]
            support_legal += compatible_k.bit_count()
            needed = 2 - small_counts[0][i] - small_counts[1][j]
            if needed not in pattern_k:
                continue
            compatible_k &= pattern_k[needed]
            component_legal += compatible_k.bit_count()
            while compatible_k:
                bit = compatible_k & -compatible_k
                k = bit.bit_length() - 1
                compatible_k ^= bit
                block_mask = pair_masks[0][i] | pair_masks[1][j] | pair_masks[2][k]
                if all(
                    (neighbor_masks[vertex] & block_mask).bit_count()
                    <= (1 if block_mask >> vertex & 1 else 2)
                    for vertex in range(X_SIZE)
                ):
                    mixed_legal += 1
                    mixed_patterns[
                        (
                            small_counts[0][i],
                            small_counts[1][j],
                            small_counts[2][k],
                        )
                    ] += 1
    return {
        "raw_pair_triples": 60**3,
        "gram_support_legal": support_legal,
        "after_forced_component_equality": component_legal,
        "after_mixed_BH_nonnegativity": mixed_legal,
        "mixed_legal_by_component_pattern": {
            str(pattern): count for pattern, count in sorted(mixed_patterns.items())
        },
    }


def component_record(
    component: Sequence[int],
    gram: Sequence[Sequence[int]],
) -> dict[str, object]:
    indicator = [int(vertex in component) for vertex in range(X_SIZE)]
    fibre_balance = [
        sum(vertex // FIBRE_SIZE == fibre for vertex in component)
        for fibre in range(FIBRES)
    ]
    first = 10 * len(component)
    second = sum(
        indicator[left] * gram[left][right] * indicator[right]
        for left in range(X_SIZE)
        for right in range(X_SIZE)
    )
    cauchy_numerator = first * first
    cauchy_floor = (cauchy_numerator + 59) // 60
    equality = second * 60 == cauchy_numerator
    forced_intersection = first // 60 if first % 60 == 0 else None
    return {
        "size": len(component),
        "fibre_balance": fibre_balance,
        "intersection_first_moment": first,
        "intersection_second_moment": second,
        "cauchy_floor": cauchy_floor,
        "cauchy_equality": equality,
        "forced_integer_intersection": forced_intersection,
    }


def enumerate_rank33_masks(wave41: ModuleType) -> tuple[object, tuple[int, ...]]:
    _, rank_eleven, _ = wave41.enumerate_quotients()
    require(len(rank_eleven) == 8, "rank-eleven quotient census changed")
    canonical = rank_eleven[0][1]
    allowed, ranks, _ = wave41.canonical_lift_census(canonical)
    # Wave 41's sparse routine omits the base-triangle quotient direction, so
    # K39 rank 33 is encoded by sparse rank 32.
    masks = [
        mask
        for mask in range(wave41.MASK_COUNT)
        if (allowed >> mask) & 1 and ranks[mask] + 1 == 33
    ]
    require(len(masks) == 264, "rank-33 lift census changed")
    return canonical, tuple(masks)


def build_results() -> dict[str, object]:
    wave41 = load_wave41()
    canonical, masks = enumerate_rank33_masks(wave41)
    signature_counts: Counter[tuple[int, ...]] = Counter()
    fibre_signature_counts: Counter[tuple[tuple[int, ...], ...]] = Counter()
    c4_counts: Counter[int] = Counter()
    gram_min_counts: Counter[int] = Counter()
    gram_entry_distributions: Counter[tuple[tuple[int, int], ...]] = Counter()
    gram_modular_rank_counts: Counter[int] = Counter()
    candidate_census_distribution: Counter[tuple[int, int, int]] = Counter()
    c4_candidate_joint_distribution: Counter[
        tuple[int, tuple[int, int, int]]
    ] = Counter()
    cauchy_equality_failures: list[int] = []
    odd_fibre_component_masks: list[int] = []
    negative_gram_masks: list[int] = []
    mask_records: list[dict[str, object]] = []

    for mask in masks:
        sparse = wave41.lifted_adjacency(canonical, mask)
        adjacency = adjacency_matrix(sparse)
        gram = forced_gram(adjacency)
        require(gram == [list(row) for row in zip(*gram)], "Gram not symmetric")
        core_components = components(sparse)
        small_component = frozenset(core_components[0])
        records = tuple(component_record(component, gram) for component in core_components)
        sizes = tuple(int(record["size"]) for record in records)
        fibre_signature = tuple(
            tuple(map(int, record["fibre_balance"])) for record in records
        )
        signature_counts[sizes] += 1
        fibre_signature_counts[fibre_signature] += 1
        c4 = four_cycle_count(adjacency)
        c4_counts[c4] += 1
        gram_min = min(map(min, gram))
        gram_min_counts[gram_min] += 1
        distribution = tuple(sorted(Counter(itertools.chain.from_iterable(gram)).items()))
        gram_entry_distributions[distribution] += 1
        structural_kernel = (
            tuple(
                int(vertex // FIBRE_SIZE == 0)
                - int(vertex // FIBRE_SIZE == 1)
                for vertex in range(X_SIZE)
            ),
            tuple(
                int(vertex // FIBRE_SIZE == 0)
                - int(vertex // FIBRE_SIZE == 2)
                for vertex in range(X_SIZE)
            ),
            tuple(
                2 if vertex in small_component else -1
                for vertex in range(X_SIZE)
            ),
        )
        require(
            all(
                all(
                    sum(gram[row][column] * vector[column] for column in range(X_SIZE))
                    == 0
                    for row in range(X_SIZE)
                )
                for vector in structural_kernel
            ),
            "structural kernel vector failed",
        )
        require(
            wave41.matrix_rank(structural_kernel, 1_000_003) == 3,
            "structural kernel vectors are dependent",
        )
        gram_modular_rank = wave41.matrix_rank(gram, 1_000_003)
        require(gram_modular_rank == 33, "forced Gram rational-rank certificate changed")
        gram_modular_rank_counts[gram_modular_rank] += 1

        if gram_min < 0:
            negative_gram_masks.append(mask)
        if any(not bool(record["cauchy_equality"]) for record in records):
            cauchy_equality_failures.append(mask)
        if any(
            len(set(record["fibre_balance"])) != 1
            or int(record["fibre_balance"][0]) % 2
            for record in records
        ):
            odd_fibre_component_masks.append(mask)

        census = candidate_census(adjacency, gram, small_component)
        census_key = (
            int(census["gram_support_legal"]),
            int(census["after_forced_component_equality"]),
            int(census["after_mixed_BH_nonnegativity"]),
        )
        candidate_census_distribution[census_key] += 1
        c4_candidate_joint_distribution[(c4, census_key)] += 1
        mask_records.append(
            {
                "mask": mask,
                "component_sizes": list(sizes),
                "component_fibre_balances": [list(item) for item in fibre_signature],
                "component_moments": list(records),
                "four_cycle_count": c4,
                "forced_gram_minimum": gram_min,
                "forced_gram_entry_distribution": {
                    str(value): count for value, count in distribution
                },
                "forced_gram_rank_mod_1000003": gram_modular_rank,
                "structural_kernel_dimension": 3,
                "candidate_census": census,
            }
        )

    return {
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "format": FORMAT,
        "git_commit": FROZEN_COMMIT,
        "scope": (
            "Conditional on n3=4158, r3=12, all edges type 222, and one of "
            "the 264 canonical rank-33 triangle-free lifts: exact BB^T "
            "component and entrywise-positivity necessities. No completed-graph "
            "automorphism is assumed."
        ),
        "input": {
            str(SOURCE_CODE).replace("\\", "/"): SOURCE_CODE_SHA256,
        },
        "rank33_lift_count": len(masks),
        "rank33_masks": list(masks),
        "rank33_masks_sha256": sha256_bytes(canonical_bytes(list(masks))),
        "component_size_partition_distribution": {
            str(signature): count for signature, count in sorted(signature_counts.items())
        },
        "component_fibre_balance_distribution": {
            str(signature): count
            for signature, count in sorted(fibre_signature_counts.items())
        },
        "four_cycle_count_distribution": {
            str(value): count for value, count in sorted(c4_counts.items())
        },
        "forced_gram_minimum_distribution": {
            str(value): count for value, count in sorted(gram_min_counts.items())
        },
        "forced_gram_entry_distribution_classes": [
            {
                "entry_distribution": {
                    str(value): count for value, count in distribution
                },
                "lift_count": count,
            }
            for distribution, count in sorted(gram_entry_distributions.items())
        ],
        "forced_gram_rank_mod_1000003_distribution": {
            str(rank): count for rank, count in sorted(gram_modular_rank_counts.items())
        },
        "forced_gram_kernel_theorem": (
            "For every lift, the two fibre-indicator differences and the "
            "2*small-minus-large component contrast are three independent "
            "integer kernel vectors. Rank 33 modulo 1000003 proves the "
            "rational kernel is exactly their span."
        ),
        "candidate_census_distribution": {
            str(census): count
            for census, count in sorted(candidate_census_distribution.items())
        },
        "four_cycle_candidate_census_joint_distribution": {
            str(key): count
            for key, count in sorted(c4_candidate_joint_distribution.items())
        },
        "necessary_exclusions": {
            "negative_forced_gram_masks": negative_gram_masks,
            "component_cauchy_equality_failure_masks": cauchy_equality_failures,
            "nonuniform_or_odd_fibre_component_masks": odd_fibre_component_masks,
            "excluded_union_count": len(
                set(negative_gram_masks)
                | set(cauchy_equality_failures)
                | set(odd_fibre_component_masks)
            ),
        },
        "per_mask": mask_records,
        "status_wall": {
            "full_B_for_any_surviving_mask": "UNKNOWN",
            "compatible_H": "UNKNOWN",
            "all_triangle_free_lifts": "NOT_CHECKED",
            "endpoint_excluded": False,
            "conway_99_resolved": False,
        },
        "limitations": [
            "The five candidate-census values are numerical classes, not a proof of five isomorphism classes.",
            "Every one of the 264 lifts survives these necessary filters.",
            "No complete 60-column B, compatible H, endpoint exclusion, or graph is supplied.",
            "Discovery cannot promote its own result to VERIFIED.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    rendered = canonical_bytes(build_results())
    if args.verify is not None:
        if args.verify.read_bytes() != rendered:
            raise SystemExit("verification mismatch")
        print("verification: PASS")
    elif args.output is not None:
        args.output.write_bytes(rendered)
    else:
        print(rendered.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
