#!/usr/bin/env python3
"""Independent replay of the Wave 10 ``n3 = 36`` support certificate.

This implementation does not import ``audit_support.py``.  It constructs the
second matching recursively instead of pairing coverage-signature buckets,
then recomputes the finite domain, support masks, rook saturation, and several
mutation rejections using only the Python standard library.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Sequence


POINTS = tuple((left, right) for left in range(3) for right in range(3, 6))
POINT_SETS = tuple(frozenset(point) for point in POINTS)
RECTANGLES = tuple(
    tuple(
        tuple(6 * left + right for left in POINTS[first] for right in POINTS[second])
        for second in range(9)
    )
    for first in range(9)
)


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def resource_profiles() -> tuple[dict[str, int], ...]:
    answer = []
    for values in itertools.product(*(range(bound) for bound in (19, 13, 10, 8, 7))):
        x2, x3, x4, x5, x6 = values
        if 2 * x2 + 3 * x3 + 4 * x4 + 5 * x5 + 6 * x6 != 36:
            continue
        consumed = x2 + 3 * x3 + 6 * x4 + 10 * x5 + 15 * x6
        if consumed <= 30:
            answer.append(
                {
                    "x2": x2,
                    "x3": x3,
                    "x4": x4,
                    "x5": x5,
                    "x6": x6,
                    "consumed_K_edges": consumed,
                }
            )
    if len(answer) != 14:
        raise AssertionError("resource-profile count changed")
    return tuple(answer)


def partitions_of_six(offset: int) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    vertices = tuple(range(offset, offset + 6))
    result = []
    for first in itertools.combinations(vertices, 3):
        second = tuple(vertex for vertex in vertices if vertex not in first)
        if first < second:
            result.append((tuple(first), second))
    if len(result) != 10:
        raise AssertionError("partition count changed")
    return tuple(result)


def point_families() -> tuple[tuple[tuple[int, int], ...], ...]:
    records = []
    for first in partitions_of_six(0):
        for second in partitions_of_six(6):
            family = tuple(
                sorted(
                    tuple(sorted((left, right)))
                    for partition in (first, second)
                    for left in partition[0]
                    for right in partition[1]
                )
            )
            if any(sum(vertex in point for point in family) != 3 for vertex in range(12)):
                raise AssertionError("noncubic point family")
            records.append(family)
    if len(records) != 100 or len(set(records)) != 100:
        raise AssertionError("point-family count changed")
    return tuple(records)


def first_coverage(permutation: tuple[int, ...]) -> list[int]:
    coverage = [0] * 36
    for row, column in enumerate(permutation):
        for cell in RECTANGLES[row][column]:
            coverage[cell] += 1
    return coverage


def enumerate_supports_recursive() -> tuple[tuple[int, ...], dict[str, int]]:
    """Choose one matching, then recursively construct its exact complement."""

    masks: set[int] = set()
    eligible = 0
    recursive_ordered_completions = 0
    for first in itertools.permutations(range(9)):
        coverage = first_coverage(first)
        if max(coverage) > 2:
            continue
        eligible += 1
        inverse_first = [0] * 9
        for row, column in enumerate(first):
            inverse_first[column] = row
        residual = [2 - value for value in coverage]
        domains = []
        feasible = True
        for row in range(9):
            choices = tuple(
                column
                for column in range(9)
                if not (POINT_SETS[column] & POINT_SETS[first[row]])
                and not (POINT_SETS[row] & POINT_SETS[inverse_first[column]])
                and all(residual[cell] > 0 for cell in RECTANGLES[row][column])
            )
            if not choices:
                feasible = False
                break
            domains.append(choices)
        if not feasible:
            continue

        chosen = [-1] * 9

        def complete(done: int, used_columns: int) -> None:
            nonlocal recursive_ordered_completions
            if done == 9:
                if any(residual):
                    return
                recursive_ordered_completions += 1
                mask = 0
                for row, column in enumerate(first):
                    mask |= 1 << (9 * row + column)
                for row, column in enumerate(chosen):
                    mask |= 1 << (9 * row + column)
                masks.add(mask)
                return

            candidates = []
            for row in range(9):
                if chosen[row] >= 0:
                    continue
                choices = [
                    column
                    for column in domains[row]
                    if not (used_columns >> column & 1)
                    and all(residual[cell] > 0 for cell in RECTANGLES[row][column])
                ]
                if not choices:
                    return
                candidates.append((len(choices), row, choices))
            _, row, choices = min(candidates)
            for column in choices:
                chosen[row] = column
                for cell in RECTANGLES[row][column]:
                    residual[cell] -= 1
                complete(done + 1, used_columns | (1 << column))
                for cell in RECTANGLES[row][column]:
                    residual[cell] += 1
                chosen[row] = -1

        complete(0, 0)

    ordered = tuple(sorted(masks))
    statistics = {
        "eligible_first_permutations": eligible,
        "recursive_ordered_completions": recursive_ordered_completions,
        "unique_support_masks": len(ordered),
    }
    if statistics != {
        "eligible_first_permutations": 230_112,
        "recursive_ordered_completions": 3_456,
        "unique_support_masks": 216,
    }:
        raise AssertionError(f"independent support counts changed: {statistics}")
    return ordered, statistics


def support_diagnostic(mask: int) -> tuple[int, int]:
    rook_adjacency = tuple(
        frozenset(
            other
            for other in range(9)
            if other != vertex and POINT_SETS[vertex] & POINT_SETS[other]
        )
        for vertex in range(9)
    )
    for left, right in itertools.combinations(range(9), 2):
        expected = 1 if right in rook_adjacency[left] else 2
        if len(rook_adjacency[left] & rook_adjacency[right]) != expected:
            raise AssertionError("rook lambda/mu identity changed")

    selected = tuple(
        (position // 9, position % 9)
        for position in range(81)
        if mask >> position & 1
    )
    if len(selected) != 18:
        raise AssertionError("support size changed")
    rows = [[column for row, column in selected if row == fixed] for fixed in range(9)]
    columns = [[row for row, column in selected if column == fixed] for fixed in range(9)]
    if any(len(items) != 2 for items in (*rows, *columns)):
        raise AssertionError("fixed-point degree changed")
    if any(POINT_SETS[items[0]] & POINT_SETS[items[1]] for items in (*rows, *columns)):
        raise AssertionError("support matching condition changed")

    covers = [set(RECTANGLES[row][column]) for row, column in selected]
    cell_coverers = [
        [index for index, coverage in enumerate(covers) if cell in coverage]
        for cell in range(36)
    ]
    if any(len(items) != 2 for items in cell_coverers):
        raise AssertionError("exact-two cell coverage changed")
    adjacency = [set() for _ in range(18)]
    for left, right in itertools.combinations(range(18), 2):
        common = covers[left] & covers[right]
        if len(common) > 1:
            raise AssertionError("H simplicity changed")
        if common:
            adjacency[left].add(right)
            adjacency[right].add(left)
    if any(len(neighbors) != 4 for neighbors in adjacency):
        raise AssertionError("H degree changed")
    triangles = sum(
        right in adjacency[left]
        and third in adjacency[left]
        and third in adjacency[right]
        for left, right, third in itertools.combinations(range(18), 3)
    )
    if triangles:
        raise AssertionError("H triangle found")
    return len(rows) + len(columns), triangles


def validate_certificate(
    certificate: dict[str, object],
    profiles: tuple[dict[str, int], ...],
    families: tuple[tuple[tuple[int, int], ...], ...],
    masks: tuple[int, ...],
) -> None:
    if certificate.get("schema") != "conditional-n3-36-support-audit-v1":
        raise AssertionError("certificate schema changed")
    resource = certificate["resource_profiles"]
    if resource["profiles"] != list(profiles):
        raise AssertionError("resource profiles changed")
    domain = certificate["all_size_two_domain"]
    if domain["labeled_point_families"] != 100:
        raise AssertionError("point-family count changed")
    if domain["point_family_digest"] != canonical_sha256(families):
        raise AssertionError("point-family digest changed")
    support = certificate["abstract_support"]
    if support["support_masks"] != list(masks):
        raise AssertionError("support masks changed")
    if support["support_masks_sha256"] != canonical_sha256(masks):
        raise AssertionError("support-mask digest changed")
    if support["survivors_after_original_SRG_saturation"] != 0:
        raise AssertionError("a false final survivor was recorded")
    rook = certificate["rook_saturation"]
    if rook["adjacent_pairs_saturated_at_lambda_1"] != 18:
        raise AssertionError("rook lambda count changed")
    if rook["nonadjacent_pairs_saturated_at_mu_2"] != 18:
        raise AssertionError("rook mu count changed")
    conclusion = certificate["conclusion"]
    if conclusion["conditional_n3_lower_bound"] != 39:
        raise AssertionError("conditional n3 bound changed")
    if conclusion["target_result"] != "UNKNOWN":
        raise AssertionError("target status was inflated")


def mutation_rejections(
    certificate: dict[str, object],
    context: tuple[
        tuple[dict[str, int], ...],
        tuple[tuple[tuple[int, int], ...], ...],
        tuple[int, ...],
    ],
) -> tuple[str, ...]:
    mutations = (
        ("drop_support", lambda item: item["abstract_support"]["support_masks"].pop()),
        (
            "alter_support_digest",
            lambda item: item["abstract_support"].__setitem__("support_masks_sha256", "0" * 64),
        ),
        (
            "restore_false_survivor",
            lambda item: item["abstract_support"].__setitem__(
                "survivors_after_original_SRG_saturation", 1
            ),
        ),
        (
            "alter_rook_mu",
            lambda item: item["rook_saturation"].__setitem__(
                "nonadjacent_pairs_saturated_at_mu_2", 17
            ),
        ),
        (
            "inflate_target_status",
            lambda item: item["conclusion"].__setitem__("target_result", "NONEXISTENT"),
        ),
    )
    rejected = []
    for name, mutation in mutations:
        altered = copy.deepcopy(certificate)
        mutation(altered)
        try:
            validate_certificate(altered, *context)
        except (AssertionError, KeyError, IndexError, TypeError, ValueError):
            rejected.append(name)
        else:
            raise AssertionError(f"mutation was accepted: {name}")
    return tuple(rejected)


def replay(certificate_path: Path) -> dict[str, object]:
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    profiles = resource_profiles()
    families = point_families()
    masks, statistics = enumerate_supports_recursive()
    diagnostics = Counter(support_diagnostic(mask) for mask in masks)
    if diagnostics != Counter({(18, 0): 216}):
        raise AssertionError(f"independent support diagnostics changed: {diagnostics}")
    context = (profiles, families, masks)
    validate_certificate(certificate, *context)
    rejected = mutation_rejections(certificate, context)
    return {
        "status": "PASS independent n3=36 support replay",
        "resource_profiles": len(profiles),
        "labeled_point_families": len(families),
        "support_search": statistics,
        "support_masks_sha256": canonical_sha256(masks),
        "diagnostics": {"18_rook_saturation_violations_and_zero_H_triangles": 216},
        "final_survivors": 0,
        "mutations_rejected": list(rejected),
        "target_result": "UNKNOWN",
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = replay(args.certificate)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
