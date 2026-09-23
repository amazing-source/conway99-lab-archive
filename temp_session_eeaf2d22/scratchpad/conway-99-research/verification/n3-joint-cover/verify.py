#!/usr/bin/env python3
"""Independent exact verifier for the 12-branch N3 joint matching cover."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations, permutations
from pathlib import Path
from typing import Iterator, Sequence


ROOT = Path(__file__).resolve().parent
DEFAULT_CERTIFICATE = ROOT / "n3-joint-cover.json"
Matching = tuple[tuple[int, int], ...]

UNIT = {frozenset((0, 2)), frozenset((2, 4))}
FIXED_EDGE = (0, 4)
SHARED_FIBER_ENDPOINTS = (0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
REMAINING_ENDPOINTS = (1, 5, 6, 7, 8, 9, 10, 11, 12, 13)
LEGACY_FIBER_ENDPOINTS = tuple(range(2, 14))


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant {value!r}")


def exact_integer(value: object, field: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{field} must be an integer")
    return value


def exact_integer_list(value: object, field: str) -> list[int]:
    if not isinstance(value, list) or any(type(item) is not int for item in value):
        raise ValueError(f"{field} must be a list of integers")
    return value


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


def act_matching(matching: Matching, permutation: Sequence[int]) -> Matching:
    return tuple(
        sorted(
            tuple(sorted((permutation[left], permutation[right])))
            for left, right in matching
        )
    )


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(left[right[index]] for index in range(14))


def stabilizer_generators() -> tuple[tuple[int, ...], ...]:
    identity = tuple(range(14))
    generators: list[tuple[int, ...]] = []

    special = list(identity)
    special[0], special[4] = 4, 0
    special[1], special[5] = 5, 1
    generators.append(tuple(special))

    for first in (6, 8, 10, 12):
        flip = list(identity)
        flip[first], flip[first + 1] = first + 1, first
        generators.append(tuple(flip))

    for first, second in ((6, 8), (8, 10), (10, 12)):
        swap = list(identity)
        swap[first], swap[second] = second, first
        swap[first + 1], swap[second + 1] = second + 1, first + 1
        generators.append(tuple(swap))

    return tuple(generators)


def generated_group(
    generators: Sequence[Sequence[int]],
) -> set[tuple[int, ...]]:
    identity = tuple(range(14))
    group = {identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            image = compose(generator, current)
            if image not in group:
                group.add(image)
                frontier.append(image)
    return group


def image_unit(permutation: Sequence[int]) -> set[frozenset[int]]:
    return {
        frozenset(permutation[coordinate] for coordinate in label) for label in UNIT
    }


def filtered_full_wreath_stabilizer() -> set[tuple[int, ...]]:
    result: set[tuple[int, ...]] = set()
    for pair_image in permutations(range(7)):
        for flip_mask in range(1 << 7):
            permutation = [0] * 14
            for source_pair in range(7):
                flip = (flip_mask >> source_pair) & 1
                target_pair = pair_image[source_pair]
                for endpoint in (0, 1):
                    permutation[2 * source_pair + endpoint] = (
                        2 * target_pair + (endpoint ^ flip)
                    )
            frozen = tuple(permutation)
            if image_unit(frozen) == UNIT:
                result.add(frozen)
    return result


def orbit(
    representative: Matching, generators: Sequence[Sequence[int]]
) -> set[Matching]:
    result = {representative}
    frontier = [representative]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            image = act_matching(current, generator)
            if image not in result:
                result.add(image)
                frontier.append(image)
    return result


def normalize_representative(raw: object) -> Matching:
    if not isinstance(raw, list):
        raise ValueError("representative must be a list")
    edges: list[tuple[int, int]] = []
    for edge in raw:
        if (
            not isinstance(edge, list)
            or len(edge) != 2
            or any(type(endpoint) is not int for endpoint in edge)
        ):
            raise ValueError("representative edge must contain two integers")
        left, right = edge
        if left >= right:
            raise ValueError("representative edges must be ordered")
        edges.append((left, right))
    matching = tuple(edges)
    if matching != tuple(sorted(matching)):
        raise ValueError("representative must be lexicographically ordered")
    flattened = sorted(endpoint for edge in matching for endpoint in edge)
    if flattened != list(SHARED_FIBER_ENDPOINTS):
        raise ValueError("representative is not a perfect matching on S_2")
    if FIXED_EDGE not in matching:
        raise ValueError("representative omits the N3 edge")
    return matching


def positive_edge_literals(matching: Matching) -> list[int]:
    labels = tuple(
        (left, right)
        for left, right in combinations(range(14), 2)
        if right != (left ^ 1)
    )
    label_index = {label: index for index, label in enumerate(labels)}
    edge_variable = {
        edge: variable
        for variable, edge in enumerate(combinations(range(len(labels)), 2), start=1)
    }
    result: list[int] = []
    for left, right in matching:
        first = label_index[tuple(sorted((2, left)))]
        second = label_index[tuple(sorted((2, right)))]
        result.append(edge_variable[tuple(sorted((first, second)))])
    return sorted(result)


def verify(certificate_path: Path = DEFAULT_CERTIFICATE) -> None:
    raw_bytes = certificate_path.read_bytes()
    certificate = json.loads(
        raw_bytes,
        object_pairs_hook=unique_object,
        parse_constant=reject_json_constant,
    )
    if not isinstance(certificate, dict):
        raise ValueError("certificate must be a JSON object")
    expected_top_keys = {
        "format",
        "pair_count",
        "branch_coordinate",
        "fixed_endpoint_edge",
        "stabilizer_order",
        "matching_count",
        "burnside_fixed_sum",
        "legacy_fiber_orbit_count",
        "branches",
    }
    if set(certificate) != expected_top_keys:
        raise ValueError("unexpected certificate keys")
    if certificate["format"] != "n3-joint-fiber-matching-orbits-v1":
        raise ValueError("unexpected certificate format")
    pair_count = exact_integer(certificate["pair_count"], "pair_count")
    branch_coordinate = exact_integer(
        certificate["branch_coordinate"], "branch_coordinate"
    )
    if pair_count != 7 or branch_coordinate != 2:
        raise ValueError("certificate uses the wrong target scaffold or fiber")
    fixed_endpoint_edge = exact_integer_list(
        certificate["fixed_endpoint_edge"], "fixed_endpoint_edge"
    )
    if fixed_endpoint_edge != [0, 4]:
        raise ValueError("certificate uses the wrong N3 matching edge")
    stabilizer_order = exact_integer(
        certificate["stabilizer_order"], "stabilizer_order"
    )
    matching_count = exact_integer(certificate["matching_count"], "matching_count")
    burnside_fixed_sum = exact_integer(
        certificate["burnside_fixed_sum"], "burnside_fixed_sum"
    )
    legacy_fiber_orbit_count = exact_integer(
        certificate["legacy_fiber_orbit_count"], "legacy_fiber_orbit_count"
    )

    generators = stabilizer_generators()
    generated = generated_group(generators)
    filtered = filtered_full_wreath_stabilizer()
    if generated != filtered or len(generated) != stabilizer_order:
        raise AssertionError("generators do not give the exact N3-unit stabilizer")

    states = set(perfect_matchings(REMAINING_ENDPOINTS))
    if len(states) != matching_count:
        raise AssertionError("wrong fixed-edge matching count")

    raw_branches = certificate["branches"]
    if not isinstance(raw_branches, list) or len(raw_branches) != 12:
        raise ValueError("certificate must contain 12 branches")
    covered: set[Matching] = set()
    for expected_branch, raw_branch in enumerate(raw_branches, start=1):
        if not isinstance(raw_branch, dict):
            raise ValueError("branch must be an object")
        if set(raw_branch) != {
            "branch",
            "orbit_size",
            "stabilizer_size",
            "representative",
            "positive_edge_literals",
        }:
            raise ValueError("unexpected branch keys")
        branch_number = exact_integer(raw_branch["branch"], "branch")
        orbit_size = exact_integer(raw_branch["orbit_size"], "orbit_size")
        recorded_stabilizer_size = exact_integer(
            raw_branch["stabilizer_size"], "stabilizer_size"
        )
        recorded_literals = exact_integer_list(
            raw_branch["positive_edge_literals"], "positive_edge_literals"
        )
        if branch_number != expected_branch:
            raise ValueError("branches are not sequential")
        representative = normalize_representative(raw_branch["representative"])
        remaining = tuple(edge for edge in representative if edge != FIXED_EDGE)
        branch_orbit = orbit(remaining, generators)
        if remaining != min(branch_orbit):
            raise AssertionError("branch representative is not canonical")
        if len(branch_orbit) != orbit_size:
            raise AssertionError("incorrect branch orbit size")
        if covered.intersection(branch_orbit):
            raise AssertionError("branch orbits overlap")
        covered.update(branch_orbit)
        stabilizer_size = sum(
            act_matching(remaining, permutation) == remaining
            for permutation in generated
        )
        if stabilizer_size != recorded_stabilizer_size:
            raise AssertionError("incorrect branch stabilizer size")
        if stabilizer_size * len(branch_orbit) != len(generated):
            raise AssertionError("orbit-stabilizer checksum failed")
        if positive_edge_literals(representative) != recorded_literals:
            raise AssertionError("positive SAT literals do not match the branch")
    if covered != states:
        raise AssertionError("the 12 branches do not cover all fixed-edge matchings")

    burnside_sum = sum(
        act_matching(matching, permutation) == matching
        for permutation in generated
        for matching in states
    )
    if burnside_sum != burnside_fixed_sum:
        raise AssertionError("Burnside checksum failed")
    if burnside_sum // len(generated) != len(raw_branches):
        raise AssertionError("Burnside orbit count is not 12")

    legacy_group = {permutation for permutation in generated if permutation[0] == 0}
    if len(legacy_group) != 384:
        raise AssertionError("wrong N3 stabilizer subgroup for legacy S_0")
    legacy_unseen = set(perfect_matchings(LEGACY_FIBER_ENDPOINTS))
    legacy_orbit_count = 0
    while legacy_unseen:
        representative = min(legacy_unseen)
        branch_orbit = {
            act_matching(representative, permutation) for permutation in legacy_group
        }
        legacy_unseen.difference_update(branch_orbit)
        legacy_orbit_count += 1
    if legacy_orbit_count != legacy_fiber_orbit_count:
        raise AssertionError("legacy S_0 orbit count is not 78")

    print("PASS N3 joint 12-branch cover")
    print("certificate_sha256", hashlib.sha256(raw_bytes).hexdigest())
    print("stabilizer_order", len(generated))
    print("matching_count", len(states))
    print("orbit_sizes", [branch["orbit_size"] for branch in raw_branches])
    print("burnside_fixed_sum", burnside_sum)
    print("legacy_fiber_orbits", legacy_orbit_count)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "certificate",
        nargs="?",
        type=Path,
        default=DEFAULT_CERTIFICATE,
        help="certificate to verify (default: the sibling committed JSON file)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    verify(args.certificate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
