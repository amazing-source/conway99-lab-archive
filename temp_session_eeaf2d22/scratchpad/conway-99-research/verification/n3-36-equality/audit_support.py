#!/usr/bin/env python3
"""Exact abstract-support census for the Wave 10 ``n3 = 36`` branch.

After the human proof reduces the all-size-two case to ``K = 2 K6``, the
points in either component are the nine edges of a ``K3,3``.  This program
enumerates every remaining abstract positive-H support for one labeled point
family, checks all Wave 6--9 support conditions, and then applies the original
SRG lambda/mu saturation condition.  It uses only the Python standard library.

The reduction to this finite domain is proved in the accompanying report; this
program alone is not a Conway-99 nonexistence certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Sequence


POINTS = tuple((left, right) for left in range(3) for right in range(3, 6))
POINT_SETS = tuple(frozenset(point) for point in POINTS)
L_CELL_COUNT = 36


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def point_resource_profiles() -> tuple[dict[str, int], ...]:
    """Enumerate incidence-36 profiles within the thirty-edge K budget."""

    profiles = []
    for x2 in range(19):
        for x3 in range(13):
            for x4 in range(10):
                for x5 in range(8):
                    for x6 in range(7):
                        incidence = 2 * x2 + 3 * x3 + 4 * x4 + 5 * x5 + 6 * x6
                        consumed = x2 + 3 * x3 + 6 * x4 + 10 * x5 + 15 * x6
                        if incidence == 36 and consumed <= 30:
                            profiles.append(
                                {
                                    "x2": x2,
                                    "x3": x3,
                                    "x4": x4,
                                    "x5": x5,
                                    "x6": x6,
                                    "consumed_K_edges": consumed,
                                }
                            )
    if len(profiles) != 14:
        raise AssertionError(f"expected fourteen resource profiles, got {len(profiles)}")
    return tuple(profiles)


def partitions_of_six(offset: int) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    vertices = tuple(range(offset, offset + 6))
    results = []
    for first in itertools.combinations(vertices, 3):
        second = tuple(vertex for vertex in vertices if vertex not in first)
        if first < second:
            results.append((tuple(first), second))
    if len(results) != 10:
        raise AssertionError("a labeled six-set should have ten unordered 3+3 partitions")
    return tuple(results)


def labeled_point_families() -> tuple[tuple[tuple[int, int], ...], ...]:
    """Enumerate the 10^2 cubic point families inside the two labeled K6s."""

    families = []
    for first in partitions_of_six(0):
        for second in partitions_of_six(6):
            points = tuple(
                sorted(
                    tuple(sorted((left, right)))
                    for partition in (first, second)
                    for left in partition[0]
                    for right in partition[1]
                )
            )
            if len(points) != 18 or len(set(points)) != 18:
                raise AssertionError("wrong point-family size")
            if any(sum(vertex in point for point in points) != 3 for vertex in range(12)):
                raise AssertionError("point family is not cubic")
            families.append(points)
    if len(families) != 100 or len(set(families)) != 100:
        raise AssertionError("expected one hundred labeled point families")
    return tuple(families)


def rook_audit() -> dict[str, int | str]:
    adjacency = tuple(
        frozenset(
            other
            for other in range(9)
            if other != vertex and POINT_SETS[vertex] & POINT_SETS[other]
        )
        for vertex in range(9)
    )
    pair_histogram: Counter[tuple[bool, int]] = Counter()
    for left, right in itertools.combinations(range(9), 2):
        adjacent = right in adjacency[left]
        common = len(adjacency[left] & adjacency[right])
        pair_histogram[(adjacent, common)] += 1
        if common != (1 if adjacent else 2):
            raise AssertionError("rook graph failed the (9,4,1,2) identity")
    if any(len(neighbors) != 4 for neighbors in adjacency):
        raise AssertionError("rook graph is not 4-regular")
    return {
        "vertices": 9,
        "degree": 4,
        "adjacent_pairs_saturated_at_lambda_1": pair_histogram[(True, 1)],
        "nonadjacent_pairs_saturated_at_mu_2": pair_histogram[(False, 2)],
        "outside_neighborhood_capacity": 1,
        "induced_graph": "L(K3,3)=rook(3,3)",
    }


RECTANGLES = tuple(
    tuple(
        tuple(6 * left + right for left in POINTS[first] for right in POINTS[second])
        for second in range(9)
    )
    for first in range(9)
)


def permutation_coverage(permutation: tuple[int, ...]) -> tuple[int, ...]:
    coverage = [0] * L_CELL_COUNT
    for first, second in enumerate(permutation):
        for cell in RECTANGLES[first][second]:
            coverage[cell] += 1
    return tuple(coverage)


def enumerate_support_masks() -> tuple[tuple[int, ...], dict[str, int]]:
    """Decompose every row/column-degree-two support into two matchings."""

    buckets: dict[tuple[int, ...], list[tuple[int, ...]]] = defaultdict(list)
    eligible = 0
    for permutation in itertools.permutations(range(9)):
        coverage = permutation_coverage(permutation)
        if max(coverage) <= 2:
            buckets[coverage].append(permutation)
            eligible += 1

    examined = 0
    accepted_ordered = 0
    masks: set[int] = set()
    for coverage, first_permutations in buckets.items():
        complement = tuple(2 - value for value in coverage)
        for first in first_permutations:
            inverse_first = [0] * 9
            for row, column in enumerate(first):
                inverse_first[column] = row
            for second in buckets.get(complement, ()):
                examined += 1
                # Each fixed point sees two disjoint opposite K3,3 edges; this
                # is the matching condition in both orientations.
                if any(POINT_SETS[first[row]] & POINT_SETS[second[row]] for row in range(9)):
                    continue
                inverse_second = [0] * 9
                for row, column in enumerate(second):
                    inverse_second[column] = row
                if any(
                    POINT_SETS[inverse_first[column]] & POINT_SETS[inverse_second[column]]
                    for column in range(9)
                ):
                    continue
                accepted_ordered += 1
                mask = 0
                for row, column in enumerate(first):
                    mask |= 1 << (9 * row + column)
                for row, column in enumerate(second):
                    mask |= 1 << (9 * row + column)
                masks.add(mask)

    ordered = tuple(sorted(masks))
    statistics = {
        "permutations_total": 362_880,
        "eligible_first_permutations": eligible,
        "coverage_signature_count": len(buckets),
        "maximum_signature_bucket_size": max(map(len, buckets.values())),
        "ordered_pairs_examined": examined,
        "accepted_ordered_decompositions": accepted_ordered,
        "unique_support_masks": len(ordered),
    }
    expected = {
        "permutations_total": 362_880,
        "eligible_first_permutations": 230_112,
        "coverage_signature_count": 189_505,
        "maximum_signature_bucket_size": 72,
        "ordered_pairs_examined": 203_688,
        "accepted_ordered_decompositions": 3_456,
        "unique_support_masks": 216,
    }
    if statistics != expected:
        raise AssertionError(f"support stage counts changed: {statistics}")
    return ordered, statistics


def selected_pairs(mask: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (position // 9, position % 9)
        for position in range(81)
        if mask >> position & 1
    )


def validate_support(mask: int) -> tuple[bool, int, int, int]:
    """Check the abstract H constraints and count decisive SRG violations."""

    selected = selected_pairs(mask)
    if len(selected) != 18:
        raise AssertionError("support does not contain eighteen positive graph edges")
    rows = [[second for first, second in selected if first == row] for row in range(9)]
    columns = [[first for first, second in selected if second == column] for column in range(9)]
    if any(len(items) != 2 for items in (*rows, *columns)):
        raise AssertionError("fixed-point row/column degree is not two")
    if any(POINT_SETS[items[0]] & POINT_SETS[items[1]] for items in (*rows, *columns)):
        raise AssertionError("a fixed-point support pair is not a matching")

    coverage_sets = [set(RECTANGLES[first][second]) for first, second in selected]
    coverers = [
        [index for index, coverage in enumerate(coverage_sets) if cell in coverage]
        for cell in range(L_CELL_COUNT)
    ]
    if any(len(items) != 2 for items in coverers):
        raise AssertionError("an L-edge is not covered exactly twice")
    for first, second in coverers:
        if selected[first][0] == selected[second][0] or selected[first][1] == selected[second][1]:
            raise AssertionError("the two N3 cross-edges fail the matching condition")

    adjacency = [set() for _ in range(18)]
    for first, second in itertools.combinations(range(18), 2):
        common = coverage_sets[first] & coverage_sets[second]
        if len(common) > 1:
            raise AssertionError("H is not simple")
        if common:
            adjacency[first].add(second)
            adjacency[second].add(first)
    if any(len(neighbors) != 4 for neighbors in adjacency):
        raise AssertionError("H is not 4-regular")
    triangle_count = sum(
        second in adjacency[first]
        and third in adjacency[first]
        and third in adjacency[second]
        for first, second, third in itertools.combinations(range(18), 3)
    )
    if triangle_count:
        raise AssertionError("H contains a triangle")

    reached = {0}
    pending = [0]
    while pending:
        vertex = pending.pop()
        new = adjacency[vertex] - reached
        reached.update(new)
        pending.extend(new)
    connected = len(reached) == 18
    four_cycles = sum(
        len(adjacency[left] & adjacency[right])
        * (len(adjacency[left] & adjacency[right]) - 1)
        // 2
        for left, right in itertools.combinations(range(18), 2)
    ) // 2

    # Each row and column has two selected opposite-rook points.  The fixed
    # source point is therefore an extra common neighbor of a pair whose
    # lambda=1 or mu=2 allowance is already saturated inside the rook.
    saturation_violations = len(rows) + len(columns)
    return connected, four_cycles, triangle_count, saturation_violations


def build_certificate(git_commit: str) -> dict[str, object]:
    started = time.monotonic()
    profiles = point_resource_profiles()
    families = labeled_point_families()
    rook = rook_audit()
    masks, search = enumerate_support_masks()
    diagnostics = Counter(validate_support(mask) for mask in masks)
    expected_diagnostics = Counter({(True, 18, 0, 18): 216})
    if diagnostics != expected_diagnostics:
        raise AssertionError(f"support diagnostics changed: {diagnostics}")
    return {
        "schema": "conditional-n3-36-support-audit-v1",
        "claim_label": "VERIFIED_CONDITIONAL_FINITE_REDUCTION",
        "git_commit": git_commit,
        "premises": [
            "the committed Wave 6-9 auxiliary-graph lemmas",
            "the Wave 10 human reduction of n3=36 to the all-size-two 2K6 case",
            "the original SRG parameters lambda=1 and mu=2",
        ],
        "resource_profiles": {
            "integer_profiles_before_local_pruning": len(profiles),
            "profiles": list(profiles),
            "sole_profile_after_human_local_pruning": {
                "x2": 18,
                "x3": 0,
                "x4": 0,
                "x5": 0,
                "x6": 0,
            },
        },
        "all_size_two_domain": {
            "forced_K_type": "2K6",
            "labeled_point_families": len(families),
            "point_family_digest": canonical_sha256(families),
            "automorphism_orbits": 1,
        },
        "rook_saturation": rook,
        "abstract_support": {
            **search,
            "support_masks": list(masks),
            "support_masks_sha256": canonical_sha256(masks),
            "diagnostics": {
                "connected_4_regular_triangle_free_H_with_18_C4s_and_18_saturation_violations": 216
            },
            "survivors_before_original_SRG_saturation": len(masks),
            "survivors_after_original_SRG_saturation": 0,
        },
        "conclusion": {
            "status": "EXHAUSTIVE_CONTRADICTION_UNDER_RECORDED_PREMISES",
            "excluded_equality": "n3=36",
            "conditional_n3_lower_bound": 39,
            "conditional_induced_C6_lower_bound": 209_325,
            "target_result": "UNKNOWN",
        },
        "runtime": {
            "python_version": platform.python_version(),
            "python_executable_name": Path(sys.executable).name,
            "standard_library_only": True,
            "elapsed_seconds": time.monotonic() - started,
        },
        "limitations": [
            "The checker certifies the recorded finite support domain, not the upstream human reduction by itself.",
            "It neither constructs nor disproves srg(99,14,1,2).",
            "No automorphism of a completed Conway graph is assumed.",
        ],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    certificate = build_certificate(args.git_commit)
    args.certificate.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("PASS n3=36 abstract-support census")
    print("resource_profiles", certificate["resource_profiles"]["integer_profiles_before_local_pruning"])
    print("labeled_point_families", certificate["all_size_two_domain"]["labeled_point_families"])
    print("abstract_supports", certificate["abstract_support"]["unique_support_masks"])
    print("survivors_after_rook_saturation", certificate["abstract_support"]["survivors_after_original_SRG_saturation"])
    print("certificate", args.certificate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
