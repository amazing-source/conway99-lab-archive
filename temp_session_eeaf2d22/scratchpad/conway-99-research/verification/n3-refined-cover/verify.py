#!/usr/bin/env python3
"""Independent exact verifier for the 78-case refined N3 cover."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations, permutations
from pathlib import Path
from typing import Iterator, Sequence


ROOT = Path(__file__).resolve().parent
DEFAULT_CERTIFICATE = ROOT / "n3-refined-cover.json"
Matching = tuple[tuple[int, int], ...]
State = tuple[Matching, int]

UNIT = {frozenset((0, 2)), frozenset((2, 4))}
FIXED_EDGE = (0, 4)
MATCHING_ENDPOINTS = (0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
REMAINING_ENDPOINTS = (1, 5, 6, 7, 8, 9, 10, 11, 12, 13)
COMMON_NEIGHBOR_COORDINATE = 4
COMMON_NEIGHBOR_MATE = 5
FIXED_NEIGHBOR_ENDPOINT = 2
FIBER_ENDPOINTS = tuple(
    endpoint
    for endpoint in range(14)
    if endpoint not in (COMMON_NEIGHBOR_COORDINATE, COMMON_NEIGHBOR_MATE)
)
CANDIDATE_ENDPOINTS = tuple(
    endpoint for endpoint in FIBER_ENDPOINTS if endpoint != FIXED_NEIGHBOR_ENDPOINT
)


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


def act_state(state: State, permutation: Sequence[int]) -> State:
    matching, endpoint = state
    return act_matching(matching, permutation), permutation[endpoint]


def compose(left: Sequence[int], right: Sequence[int]) -> tuple[int, ...]:
    return tuple(left[right[index]] for index in range(14))


def oriented_generators() -> tuple[tuple[int, ...], ...]:
    identity = tuple(range(14))
    generators: list[tuple[int, ...]] = []

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


def unit_swap_generator() -> tuple[int, ...]:
    permutation = list(range(14))
    permutation[0], permutation[4] = 4, 0
    permutation[1], permutation[5] = 5, 1
    return tuple(permutation)


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


def filtered_full_wreath_stabilizers(
) -> tuple[set[tuple[int, ...]], set[tuple[int, ...]]]:
    unit_stabilizer: set[tuple[int, ...]] = set()
    oriented_stabilizer: set[tuple[int, ...]] = set()
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
                unit_stabilizer.add(frozen)
                if frozen[0] == 0:
                    oriented_stabilizer.add(frozen)
    return unit_stabilizer, oriented_stabilizer


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
    if flattened != list(MATCHING_ENDPOINTS):
        raise ValueError("representative is not a perfect matching on S_2")
    if FIXED_EDGE not in matching:
        raise ValueError("representative omits the normalized N3 edge")
    return matching


def positive_edge_literals(matching: Matching, endpoint: int) -> list[int]:
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
    first = label_index[(0, 2)]
    second = label_index[tuple(sorted((4, endpoint)))]
    result.append(edge_variable[tuple(sorted((first, second)))])
    return sorted(result)


def exact_group_orbits(
    states: set[State], group: set[tuple[int, ...]]
) -> list[tuple[State, set[State]]]:
    unseen = set(states)
    result: list[tuple[State, set[State]]] = []
    while unseen:
        representative = min(unseen)
        orbit = {act_state(representative, permutation) for permutation in group}
        if not orbit <= unseen:
            raise AssertionError("independently reconstructed orbits overlap")
        unseen.difference_update(orbit)
        result.append((representative, orbit))
    return result


def exact_matching_orbits(
    matchings: set[Matching], group: set[tuple[int, ...]]
) -> list[tuple[Matching, set[Matching]]]:
    unseen = set(matchings)
    result: list[tuple[Matching, set[Matching]]] = []
    while unseen:
        representative = min(unseen)
        orbit = {
            act_matching(representative, permutation) for permutation in group
        }
        if not orbit <= unseen:
            raise AssertionError("independently reconstructed matching orbits overlap")
        unseen.difference_update(orbit)
        result.append((representative, orbit))
    return result


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
        "matching_coordinate",
        "fixed_endpoint_edge",
        "oriented_coordinate",
        "common_neighbor_coordinate",
        "stabilizer",
        "stabilizer_order",
        "matching_count",
        "candidate_count",
        "candidate_endpoints",
        "coordinate_profile_target",
        "state_count",
        "orbit_count",
        "burnside_fixed_sum",
        "orbits",
    }
    if set(certificate) != expected_top_keys:
        raise ValueError("unexpected certificate keys")
    if certificate["format"] != "n3-oriented-common-neighbor-orbits-v1":
        raise ValueError("unexpected certificate format")
    if exact_integer(certificate["pair_count"], "pair_count") != 7:
        raise ValueError("certificate uses the wrong target scaffold")
    if exact_integer(certificate["matching_coordinate"], "matching_coordinate") != 2:
        raise ValueError("certificate uses the wrong matching coordinate")
    if exact_integer(certificate["oriented_coordinate"], "oriented_coordinate") != 0:
        raise ValueError("certificate uses the wrong orientation")
    if (
        exact_integer(
            certificate["common_neighbor_coordinate"],
            "common_neighbor_coordinate",
        )
        != 4
    ):
        raise ValueError("certificate uses the wrong common-neighbor coordinate")
    fixed_edge = exact_integer_list(
        certificate["fixed_endpoint_edge"], "fixed_endpoint_edge"
    )
    if fixed_edge != [0, 4]:
        raise ValueError("certificate uses the wrong fixed matching edge")
    candidate_endpoints = exact_integer_list(
        certificate["candidate_endpoints"], "candidate_endpoints"
    )
    if candidate_endpoints != list(CANDIDATE_ENDPOINTS):
        raise ValueError("certificate uses the wrong candidate endpoints")
    if certificate["stabilizer"] != "C2 wreath S4":
        raise ValueError("certificate names the wrong stabilizer")
    stabilizer_order = exact_integer(
        certificate["stabilizer_order"], "stabilizer_order"
    )
    matching_count = exact_integer(certificate["matching_count"], "matching_count")
    candidate_count = exact_integer(
        certificate["candidate_count"], "candidate_count"
    )
    profile_target = exact_integer(
        certificate["coordinate_profile_target"], "coordinate_profile_target"
    )
    state_count = exact_integer(certificate["state_count"], "state_count")
    orbit_count = exact_integer(certificate["orbit_count"], "orbit_count")
    burnside_fixed_sum = exact_integer(
        certificate["burnside_fixed_sum"], "burnside_fixed_sum"
    )
    if profile_target != 2:
        raise ValueError("coordinate profile target must be two")

    generators = oriented_generators()
    generated = generated_group(generators)
    unit_generated = generated_group((unit_swap_generator(), *generators))
    unit_filtered, filtered = filtered_full_wreath_stabilizers()
    if generated != filtered or len(generated) != stabilizer_order:
        raise AssertionError("generators do not give the exact oriented stabilizer")
    if unit_generated != unit_filtered or len(unit_generated) != 768:
        raise AssertionError("the parent N3-unit stabilizer was not reproduced")

    matchings = {
        tuple(sorted((FIXED_EDGE, *remaining)))
        for remaining in perfect_matchings(REMAINING_ENDPOINTS)
    }
    if len(matchings) != matching_count:
        raise AssertionError("wrong fixed-edge matching count")
    if len(CANDIDATE_ENDPOINTS) != candidate_count:
        raise AssertionError("wrong common-neighbor candidate count")

    # Reconstruct the exact coordinate-4 profile.  The N3 unit already gives
    # p=(0,2) one neighbor q=(2,4) in F_4, so its target of two leaves exactly
    # one choice among the other eleven allowed labels (4,h).
    first_label = frozenset((0, 2))
    fixed_neighbor_label = frozenset(
        (FIXED_NEIGHBOR_ENDPOINT, COMMON_NEIGHBOR_COORDINATE)
    )
    derived_profile_target = (
        2
        - int(COMMON_NEIGHBOR_COORDINATE in first_label)
        - int(COMMON_NEIGHBOR_MATE in first_label)
    )
    if {first_label, fixed_neighbor_label} != UNIT:
        raise AssertionError("the normalized N3 unit was not reconstructed")
    if derived_profile_target != profile_target:
        raise AssertionError("the forced common-neighbor profile was not reproduced")
    if fixed_neighbor_label not in {
        frozenset((COMMON_NEIGHBOR_COORDINATE, endpoint))
        for endpoint in FIBER_ENDPOINTS
    }:
        raise AssertionError("the normalized neighbor is not in the coordinate-4 fiber")
    if derived_profile_target - 1 != 1 or len(CANDIDATE_ENDPOINTS) != 11:
        raise AssertionError("the unique additional-neighbor choice was not derived")

    states = {
        (matching, endpoint)
        for matching in matchings
        for endpoint in CANDIDATE_ENDPOINTS
    }
    if len(states) != state_count:
        raise AssertionError("wrong refined state count")
    reconstructed = exact_group_orbits(states, generated)
    if len(reconstructed) != orbit_count:
        raise AssertionError("wrong independently reconstructed orbit count")

    matching_orbits = exact_matching_orbits(matchings, unit_generated)
    if len(matching_orbits) != 12 or sum(
        len(orbit) for _, orbit in matching_orbits
    ) != matching_count:
        raise AssertionError("the parent 12-branch matching cover was not reproduced")
    first_branch = {
        representative: branch
        for branch, (representative, _) in enumerate(matching_orbits, start=1)
    }

    raw_branches = certificate["orbits"]
    if not isinstance(raw_branches, list) or len(raw_branches) != orbit_count:
        raise ValueError("certificate has the wrong number of orbits")
    covered: set[State] = set()
    for branch, (raw_branch, reconstructed_entry) in enumerate(
        zip(raw_branches, reconstructed), start=1
    ):
        if not isinstance(raw_branch, dict):
            raise ValueError("orbit must be an object")
        if set(raw_branch) != {
            "branch",
            "first_matching_branch",
            "candidate_endpoint",
            "orbit_size",
            "stabilizer_size",
            "representative",
            "positive_edge_literals",
        }:
            raise ValueError("unexpected orbit keys")
        recorded_branch = exact_integer(raw_branch["branch"], "branch")
        recorded_first_branch = exact_integer(
            raw_branch["first_matching_branch"], "first_matching_branch"
        )
        endpoint = exact_integer(
            raw_branch["candidate_endpoint"], "candidate_endpoint"
        )
        orbit_size = exact_integer(raw_branch["orbit_size"], "orbit_size")
        recorded_stabilizer = exact_integer(
            raw_branch["stabilizer_size"], "stabilizer_size"
        )
        literals = exact_integer_list(
            raw_branch["positive_edge_literals"], "positive_edge_literals"
        )
        matching = normalize_representative(raw_branch["representative"])
        state = (matching, endpoint)
        expected_state, expected_orbit = reconstructed_entry
        if recorded_branch != branch or state != expected_state:
            raise AssertionError("orbit representative or numbering is not canonical")
        if endpoint not in CANDIDATE_ENDPOINTS:
            raise ValueError("candidate endpoint is outside the forced choice set")
        if recorded_first_branch != first_branch[matching]:
            raise AssertionError("incorrect first matching branch")
        if len(expected_orbit) != orbit_size:
            raise AssertionError("incorrect refined orbit size")
        stabilizer_size = sum(
            act_state(state, permutation) == state for permutation in generated
        )
        if stabilizer_size != recorded_stabilizer:
            raise AssertionError("incorrect refined stabilizer size")
        if stabilizer_size * orbit_size != len(generated):
            raise AssertionError("refined orbit-stabilizer checksum failed")
        if positive_edge_literals(matching, endpoint) != literals:
            raise AssertionError("positive SAT literals do not match the state")
        if covered.intersection(expected_orbit):
            raise AssertionError("certificate orbits overlap")
        covered.update(expected_orbit)
    if covered != states:
        raise AssertionError("certificate does not cover every refined state")

    burnside_sum = 0
    for permutation in generated:
        fixed_matchings = sum(
            act_matching(matching, permutation) == matching for matching in matchings
        )
        fixed_endpoints = sum(
            permutation[endpoint] == endpoint for endpoint in CANDIDATE_ENDPOINTS
        )
        burnside_sum += fixed_matchings * fixed_endpoints
    if burnside_sum != burnside_fixed_sum:
        raise AssertionError("refined Burnside checksum failed")
    if burnside_sum != orbit_count * len(generated):
        raise AssertionError("Burnside orbit count is not 78")

    print("PASS refined N3 78-branch cover")
    print("certificate_sha256", hashlib.sha256(raw_bytes).hexdigest())
    print("stabilizer_order", len(generated))
    print("parent_stabilizer_order", len(unit_generated))
    print("matching_count", len(matchings))
    print("parent_matching_orbit_count", len(matching_orbits))
    print("candidate_count", len(CANDIDATE_ENDPOINTS))
    print("state_count", len(states))
    print("orbit_count", len(reconstructed))
    print("burnside_fixed_sum", burnside_sum)


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
