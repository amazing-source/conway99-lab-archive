#!/usr/bin/env python3
"""Canonical perfect-matching branches for one rooted endpoint fiber.

For the Conway model, a fiber S_u has 12 residual vertices naturally grouped
by six fixed scaffold pairs. Perfect matchings on S_u have exactly 11 orbits
under C2 wreath S6, indexed by integer partitions of 6.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Any, Iterator, Sequence

from root_model import RootModel


Matching = tuple[tuple[int, int], ...]
RefinedN3State = tuple[Matching, int]

N3_SHARED_COORDINATE = 2
N3_FIXED_ENDPOINT_EDGE = (0, 4)
N3_REMAINING_ENDPOINTS = (1, 5, 6, 7, 8, 9, 10, 11, 12, 13)
N3_REFINED_CANDIDATE_ENDPOINTS = (0, 1, 3, 6, 7, 8, 9, 10, 11, 12, 13)


def integer_partitions(total: int, maximum: int | None = None) -> Iterator[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    if maximum is None or maximum > total:
        maximum = total
    for first in range(maximum, 0, -1):
        for rest in integer_partitions(total - first, first):
            yield (first,) + rest


def perfect_matchings(vertices: tuple[int, ...]) -> Iterator[Matching]:
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        remainder = vertices[1:index] + vertices[index + 1 :]
        for rest in perfect_matchings(remainder):
            yield ((first, second),) + rest


def canonical_matching(partition: Sequence[int]) -> Matching:
    """Build a representative whose union with fixed pairs has this cycle type."""

    if not partition or any(type(part) is not int or part < 1 for part in partition):
        raise ValueError("partition must contain positive integers")
    if tuple(partition) != tuple(sorted(partition, reverse=True)):
        raise ValueError("partition must be in nonincreasing order")

    matching: list[tuple[int, int]] = []
    pair_offset = 0
    for part in partition:
        if part == 1:
            matching.append((2 * pair_offset, 2 * pair_offset + 1))
        else:
            component_pairs = list(range(pair_offset, pair_offset + part))
            for index, pair in enumerate(component_pairs):
                next_pair = component_pairs[(index + 1) % part]
                matching.append((2 * pair + 1, 2 * next_pair))
        pair_offset += part

    return tuple(sorted(tuple(sorted(edge)) for edge in matching))


def matching_type(matching: Sequence[tuple[int, int]], pair_count: int) -> tuple[int, ...]:
    """Return component sizes after contracting the fixed matching pairs."""

    vertices = set(range(2 * pair_count))
    used: set[int] = set()
    pair_graph = [set() for _ in range(pair_count)]
    loops: set[int] = set()

    for raw_left, raw_right in matching:
        left, right = sorted((raw_left, raw_right))
        if left not in vertices or right not in vertices or left == right:
            raise ValueError("matching contains an invalid endpoint")
        if left in used or right in used:
            raise ValueError("matching reuses an endpoint")
        used.update((left, right))
        first_pair, second_pair = left // 2, right // 2
        if first_pair == second_pair:
            loops.add(first_pair)
        else:
            pair_graph[first_pair].add(second_pair)
            pair_graph[second_pair].add(first_pair)

    if used != vertices:
        raise ValueError("matching does not cover every endpoint")

    components: list[int] = []
    seen: set[int] = set()
    for start in range(pair_count):
        if start in seen:
            continue
        if start in loops:
            if pair_graph[start]:
                raise ValueError("invalid matching component mixes a loop and other edges")
            seen.add(start)
            components.append(1)
            continue
        stack = [start]
        size = 0
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            size += 1
            stack.extend(pair_graph[current] - seen)
        components.append(size)

    return tuple(sorted(components, reverse=True))


def orbit_type_counts(pair_count: int = 6) -> Counter[tuple[int, ...]]:
    counts: Counter[tuple[int, ...]] = Counter()
    for matching in perfect_matchings(tuple(range(2 * pair_count))):
        counts[matching_type(matching, pair_count)] += 1
    return counts


def endpoint_generators(pair_count: int) -> tuple[tuple[int, ...], ...]:
    """Generators for the automorphism group of the fixed endpoint matching."""

    identity = tuple(range(2 * pair_count))
    generators: list[tuple[int, ...]] = []
    for pair in range(pair_count):
        permutation = list(identity)
        permutation[2 * pair], permutation[2 * pair + 1] = (
            permutation[2 * pair + 1],
            permutation[2 * pair],
        )
        generators.append(tuple(permutation))
    for pair in range(pair_count - 1):
        permutation = list(identity)
        left = 2 * pair
        right = left + 2
        permutation[left], permutation[right] = permutation[right], permutation[left]
        permutation[left + 1], permutation[right + 1] = (
            permutation[right + 1],
            permutation[left + 1],
        )
        generators.append(tuple(permutation))
    return tuple(generators)


def permute_matching(matching: Matching, permutation: Sequence[int]) -> Matching:
    return tuple(
        sorted(
            tuple(sorted((permutation[left], permutation[right])))
            for left, right in matching
        )
    )


def n3_unit_stabilizer_generators() -> tuple[tuple[int, ...], ...]:
    """Generators for the target N3-unit stabilizer inside C2 wreath S7.

    The normalized unit joins labels (0,2) and (2,4).  Its unique shared
    coordinate 2 and mate 3 are fixed.  The coordinate pairs (0,1) and (4,5)
    may be exchanged, while the other four scaffold pairs retain their full
    wreath-product action.
    """

    identity = tuple(range(14))
    generators: list[tuple[int, ...]] = []

    permutation = list(identity)
    permutation[0], permutation[4] = 4, 0
    permutation[1], permutation[5] = 5, 1
    generators.append(tuple(permutation))

    for left in (6, 8, 10, 12):
        permutation = list(identity)
        permutation[left], permutation[left + 1] = left + 1, left
        generators.append(tuple(permutation))

    for first, second in ((6, 8), (8, 10), (10, 12)):
        permutation = list(identity)
        permutation[first], permutation[second] = second, first
        permutation[first + 1], permutation[second + 1] = second + 1, first + 1
        generators.append(tuple(permutation))

    return tuple(generators)


def n3_oriented_stabilizer_generators() -> tuple[tuple[int, ...], ...]:
    """Generators for the N3-unit stabilizer fixing coordinate 0.

    Fixing coordinate 0 also fixes its normalized witness partner 4 and their
    mates 1 and 5.  The remaining action is exactly C2 wreath S4, of order
    384.  This subgroup preserves the oriented common-neighbor refinement.
    """

    return n3_unit_stabilizer_generators()[1:]


@lru_cache(maxsize=1)
def n3_joint_matching_orbits() -> tuple[tuple[Matching, int], ...]:
    """Return the 12 matching orbits on the invariant shared fiber S_2.

    The N3 unit already fixes endpoint edge (0,4), leaving ten endpoints and
    9!!=945 perfect matchings.  Representatives are the lexicographic minima
    under the exact N3-unit stabilizer generators.
    """

    unseen = set(perfect_matchings(N3_REMAINING_ENDPOINTS))
    generators = n3_unit_stabilizer_generators()
    orbits: list[tuple[Matching, int]] = []

    while unseen:
        remaining_representative = min(unseen)
        orbit = {remaining_representative}
        frontier = [remaining_representative]
        while frontier:
            current = frontier.pop()
            for generator in generators:
                image = permute_matching(current, generator)
                if image not in orbit:
                    orbit.add(image)
                    frontier.append(image)
        if not orbit <= unseen:
            raise AssertionError("N3 matching orbits overlap")
        unseen.difference_update(orbit)
        full_representative = tuple(
            sorted((N3_FIXED_ENDPOINT_EDGE, *remaining_representative))
        )
        orbits.append((full_representative, len(orbit)))

    return tuple(orbits)


@lru_cache(maxsize=1)
def n3_refined_orbits() -> tuple[tuple[Matching, int, int], ...]:
    """Return the 78 oriented N3 common-neighbor refinement orbits.

    A state consists of an S_2 matching containing endpoint edge (0,4) and
    the endpoint h of the unique additional common neighbor label (4,h) for
    label (0,2) and root-neighbor coordinate 4.  There are 945*11=10,395
    states.  The orientation-preserving stabilizer has exactly 78 orbits.
    """

    matchings = {
        tuple(sorted((N3_FIXED_ENDPOINT_EDGE, *remaining)))
        for remaining in perfect_matchings(N3_REMAINING_ENDPOINTS)
    }
    unseen: set[RefinedN3State] = {
        (matching, endpoint)
        for matching in matchings
        for endpoint in N3_REFINED_CANDIDATE_ENDPOINTS
    }
    generators = n3_oriented_stabilizer_generators()
    orbits: list[tuple[Matching, int, int]] = []

    while unseen:
        representative = min(unseen)
        orbit = {representative}
        frontier = [representative]
        while frontier:
            matching, endpoint = frontier.pop()
            for generator in generators:
                image = (
                    permute_matching(matching, generator),
                    generator[endpoint],
                )
                if image not in orbit:
                    orbit.add(image)
                    frontier.append(image)
        if not orbit <= unseen:
            raise AssertionError("refined N3 orbits overlap")
        unseen.difference_update(orbit)
        orbits.append((representative[0], representative[1], len(orbit)))

    return tuple(orbits)


def n3_joint_branch_decisions(
    root: RootModel, branch_number: int
) -> dict[tuple[int, int], bool]:
    """Fix one branch of the complete N3-stabilized matching cover on S_2."""

    if root.pair_count != 7:
        raise ValueError("the N3 joint cover applies only to pair_count 7")
    if type(branch_number) is not int:
        raise ValueError("N3 joint branch number must be an integer")
    orbits = n3_joint_matching_orbits()
    if not 1 <= branch_number <= len(orbits):
        raise ValueError(f"N3 joint branch number must be in 1..{len(orbits)}")

    representative, _ = orbits[branch_number - 1]
    fiber = root.containing(N3_SHARED_COORDINATE)
    endpoint_to_label: dict[int, int] = {}
    for label_index in fiber:
        left, right = root.labels[label_index]
        other = right if left == N3_SHARED_COORDINATE else left
        endpoint_to_label[other] = label_index
    if set(endpoint_to_label) != {
        0,
        1,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
    }:
        raise AssertionError("unexpected N3 shared-fiber endpoints")

    true_edges = {
        tuple(sorted((endpoint_to_label[left], endpoint_to_label[right])))
        for left, right in representative
    }
    if len(true_edges) != 6:
        raise AssertionError("N3 joint representative is not a perfect matching")
    return {
        tuple(sorted((first, second))): tuple(sorted((first, second))) in true_edges
        for first, second in combinations(fiber, 2)
    }


def n3_refined_branch_specification(
    root: RootModel, branch_number: int
) -> tuple[dict[tuple[int, int], bool], tuple[int, int], int]:
    """Return matching decisions, the refinement edge, and first branch."""

    if root.pair_count != 7:
        raise ValueError("the refined N3 cover applies only to pair_count 7")
    if type(branch_number) is not int:
        raise ValueError("refined N3 branch number must be an integer")
    orbits = n3_refined_orbits()
    if not 1 <= branch_number <= len(orbits):
        raise ValueError(f"refined N3 branch number must be in 1..{len(orbits)}")

    representative, endpoint, _ = orbits[branch_number - 1]
    first_branches = n3_joint_matching_orbits()
    try:
        first_branch = next(
            branch
            for branch, (matching, _) in enumerate(first_branches, start=1)
            if matching == representative
        )
    except StopIteration as exc:
        raise AssertionError("refined representative is not joint-canonical") from exc

    decisions = n3_joint_branch_decisions(root, first_branch)
    indices = root.label_index()
    first_label = indices[(0, 2)]
    second_label = indices[tuple(sorted((4, endpoint)))]
    refinement_edge = tuple(sorted((first_label, second_label)))
    if refinement_edge in decisions:
        raise AssertionError("refinement edge unexpectedly lies inside S_2")
    return decisions, refinement_edge, first_branch


def n3_joint_summary() -> dict[str, Any]:
    orbits = n3_joint_matching_orbits()
    if sum(size for _, size in orbits) != 945:
        raise AssertionError("N3 joint orbits do not cover all 945 matchings")
    return {
        "format": "n3-joint-fiber-matching-orbits-v1",
        "pair_count": 7,
        "branch_coordinate": N3_SHARED_COORDINATE,
        "fixed_endpoint_edge": list(N3_FIXED_ENDPOINT_EDGE),
        "stabilizer": "C2 x (C2 wreath S4)",
        "stabilizer_order": 768,
        "matching_count": 945,
        "orbit_count": len(orbits),
        "orbits": [
            {
                "branch": branch,
                "orbit_size": size,
                "stabilizer_size": 768 // size,
                "representative": [list(edge) for edge in representative],
            }
            for branch, (representative, size) in enumerate(orbits, start=1)
        ],
    }


def n3_refined_summary() -> dict[str, Any]:
    orbits = n3_refined_orbits()
    if sum(size for _, _, size in orbits) != 10_395:
        raise AssertionError("refined N3 orbits do not cover all 10,395 states")
    first_branches = {
        matching: branch
        for branch, (matching, _) in enumerate(n3_joint_matching_orbits(), start=1)
    }
    root = RootModel.build(7)
    indices = root.label_index()
    edge_variables = {
        edge: variable
        for variable, edge in enumerate(
            combinations(range(root.residual_count), 2), start=1
        )
    }

    def positive_literals(matching: Matching, endpoint: int) -> list[int]:
        literals = []
        for left, right in matching:
            first = indices[tuple(sorted((N3_SHARED_COORDINATE, left)))]
            second = indices[tuple(sorted((N3_SHARED_COORDINATE, right)))]
            literals.append(edge_variables[tuple(sorted((first, second)))])
        first = indices[(0, 2)]
        second = indices[tuple(sorted((4, endpoint)))]
        literals.append(edge_variables[tuple(sorted((first, second)))])
        return sorted(literals)

    return {
        "format": "n3-oriented-common-neighbor-orbits-v1",
        "pair_count": 7,
        "matching_coordinate": N3_SHARED_COORDINATE,
        "fixed_endpoint_edge": list(N3_FIXED_ENDPOINT_EDGE),
        "oriented_coordinate": 0,
        "common_neighbor_coordinate": 4,
        "stabilizer": "C2 wreath S4",
        "stabilizer_order": 384,
        "matching_count": 945,
        "candidate_count": len(N3_REFINED_CANDIDATE_ENDPOINTS),
        "candidate_endpoints": list(N3_REFINED_CANDIDATE_ENDPOINTS),
        "coordinate_profile_target": 2,
        "state_count": 10_395,
        "orbit_count": len(orbits),
        "burnside_fixed_sum": 29_952,
        "orbits": [
            {
                "branch": branch,
                "first_matching_branch": first_branches[matching],
                "candidate_endpoint": endpoint,
                "orbit_size": size,
                "stabilizer_size": 384 // size,
                "representative": [list(edge) for edge in matching],
                "positive_edge_literals": positive_literals(matching, endpoint),
            }
            for branch, (matching, endpoint, size) in enumerate(orbits, start=1)
        ],
    }


def orbit_sizes_via_generators(pair_count: int = 6) -> dict[tuple[int, ...], int]:
    """Exhaustively compute matching orbits under C2 wreath S_pair_count."""

    unseen = set(perfect_matchings(tuple(range(2 * pair_count))))
    generators = endpoint_generators(pair_count)
    sizes: dict[tuple[int, ...], int] = {}

    while unseen:
        representative = min(unseen)
        orbit = {representative}
        frontier = [representative]
        while frontier:
            current = frontier.pop()
            for generator in generators:
                image = permute_matching(current, generator)
                if image not in orbit:
                    orbit.add(image)
                    frontier.append(image)
        unseen.difference_update(orbit)
        orbit_type = matching_type(representative, pair_count)
        if orbit_type in sizes:
            raise AssertionError(f"matching type {orbit_type} splits into multiple orbits")
        sizes[orbit_type] = len(orbit)

    return sizes


def parse_partition(text: str, expected_sum: int) -> tuple[int, ...]:
    try:
        parts = tuple(int(part) for part in text.replace(",", "+").split("+") if part)
    except ValueError as exc:
        raise ValueError(f"invalid partition {text!r}") from exc
    if not parts or sum(parts) != expected_sum:
        raise ValueError(f"partition must sum to {expected_sum}")
    parts = tuple(sorted(parts, reverse=True))
    return parts


def canonical_branch_decisions(
    root: RootModel, coordinate: int, partition: Sequence[int]
) -> dict[tuple[int, int], bool]:
    """Fix all edges inside S_coordinate to one canonical matching."""

    expected_sum = root.pair_count - 1
    if sum(partition) != expected_sum:
        raise ValueError(f"partition must sum to {expected_sum}")
    fiber = root.containing(coordinate)
    if len(fiber) != 2 * expected_sum:
        raise AssertionError("unexpected endpoint-fiber size")

    # Order fiber vertices by their other endpoint. This places scaffold mates
    # consecutively, so positions (0,1), (2,3), ... form the fixed matching.
    other_endpoint_and_label: list[tuple[int, int]] = []
    for label_index in fiber:
        label = root.labels[label_index]
        other = label[1] if label[0] == coordinate else label[0]
        other_endpoint_and_label.append((other, label_index))
    ordered_fiber = [
        label_index for _, label_index in sorted(other_endpoint_and_label)
    ]

    representative = canonical_matching(tuple(sorted(partition, reverse=True)))
    true_edges = {
        tuple(sorted((ordered_fiber[left], ordered_fiber[right])))
        for left, right in representative
    }
    return {
        tuple(sorted((first, second))): tuple(sorted((first, second))) in true_edges
        for first, second in combinations(ordered_fiber, 2)
    }


def summary(pair_count: int = 6) -> dict[str, Any]:
    counts = orbit_type_counts(pair_count)
    generator_orbits = orbit_sizes_via_generators(pair_count)
    if dict(counts) != generator_orbits:
        raise AssertionError("matching types do not agree with generated group orbits")
    return {
        "format": "fiber-matching-orbits-v1",
        "pair_count": pair_count,
        "matching_count": sum(counts.values()),
        "orbit_count": len(counts),
        "orbits": [
            {
                "partition": list(partition),
                "labeled_matchings": counts[partition],
                "generated_orbit_size": generator_orbits[partition],
                "representative": [list(edge) for edge in canonical_matching(partition)],
            }
            for partition in sorted(counts, reverse=True)
        ],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair-count", type=int)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--n3-joint",
        action="store_true",
        help="emit the target-specific 12-branch N3-stabilized cover",
    )
    group.add_argument(
        "--n3-refined",
        action="store_true",
        help="emit the 78-branch oriented common-neighbor refinement",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.n3_joint or args.n3_refined:
        if args.pair_count not in (None, 7):
            flag = "--n3-joint" if args.n3_joint else "--n3-refined"
            raise SystemExit(f"{flag} applies only to --pair-count 7")
        report = n3_joint_summary() if args.n3_joint else n3_refined_summary()
    else:
        report = summary(args.pair_count if args.pair_count is not None else 6)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
