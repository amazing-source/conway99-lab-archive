#!/usr/bin/env python3
"""Independent exact checks for the Wave 6 N3-count consequences."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
from typing import Iterator, Sequence


ROOT = Path(__file__).resolve().parent
DEFAULT_JOINT_CERTIFICATE = (
    ROOT.parent / "n3-joint-cover" / "n3-joint-cover.json"
)

Matching = tuple[tuple[int, int], ...]
ENDPOINTS = (0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
MATE_MATCHING = frozenset(
    tuple(sorted((endpoint, endpoint ^ 1)))
    for endpoint in ENDPOINTS
    if endpoint < (endpoint ^ 1)
)
NONZERO_DEGREES = (4, 6, 8, 10, 12)


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant {value!r}")


def perfect_matchings(vertices: tuple[int, ...]) -> Iterator[Matching]:
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        remainder = vertices[1:index] + vertices[index + 1 :]
        for rest in perfect_matchings(remainder):
            yield tuple(sorted(((first, second), *rest)))


def normalize_matching(raw: object) -> Matching:
    if not isinstance(raw, list) or len(raw) != 6:
        raise ValueError("representative must contain six edges")
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
            raise ValueError("representative edge is not ordered")
        edges.append((left, right))
    matching = tuple(edges)
    if matching != tuple(sorted(matching)):
        raise ValueError("representative is not ordered")
    if sorted(endpoint for edge in matching for endpoint in edge) != list(ENDPOINTS):
        raise ValueError("representative is not a matching on the expected fiber")
    return matching


def alternating_signature(matching: Matching) -> tuple[int, ...]:
    active_edges = set(matching).symmetric_difference(MATE_MATCHING)
    adjacency: dict[int, set[int]] = {}
    for left, right in active_edges:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    if any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise AssertionError("active matching union is not a disjoint cycle union")

    unseen = set(adjacency)
    sizes: list[int] = []
    while unseen:
        start = min(unseen)
        component = {start}
        frontier = [start]
        while frontier:
            vertex = frontier.pop()
            for neighbor in adjacency[vertex]:
                if neighbor not in component:
                    component.add(neighbor)
                    frontier.append(neighbor)
        unseen.difference_update(component)
        sizes.append(len(component))
    return tuple(sorted(sizes))


def ceil_multiple_of_three(value: int) -> int:
    return 3 * ((value + 2) // 3)


def abstract_small_edge_candidates() -> list[tuple[int, tuple[int, ...]]]:
    """Degree sequences not eliminated by handshake, Mantel, and m>=4 Delta."""

    candidates: list[tuple[int, tuple[int, ...]]] = []
    for edges in range(3, 24, 3):
        for vertices in range(1, edges // 2 + 1):
            if edges > vertices * vertices // 4:
                continue
            for degrees in combinations_with_replacement(NONZERO_DEGREES, vertices):
                if sum(degrees) != 2 * edges:
                    continue
                if edges < 4 * max(degrees):
                    continue
                candidates.append((edges, degrees))
    return candidates


def enumerate_m18_local_models() -> int:
    """Count possible local models for a 4-regular triangle-free graph on 9."""

    # Fix v.  Its four neighbors A are independent, and the remaining set B
    # has four vertices.  Each A-row has exactly three B-neighbors; B has two
    # internal edges.  Test all 4^4 * C(6,2) forced local possibilities.
    b_pairs = tuple(combinations(range(4), 2))
    survivors = 0
    for missing_by_a in product(range(4), repeat=4):
        a_to_b = {
            (a, b)
            for a, missing in enumerate(missing_by_a)
            for b in range(4)
            if b != missing
        }
        for b_edges in combinations(b_pairs, 2):
            b_degree = Counter(endpoint for edge in b_edges for endpoint in edge)
            if any(
                sum((a, b) in a_to_b for a in range(4)) + b_degree[b] != 4
                for b in range(4)
            ):
                continue
            if any(
                any((a, left) in a_to_b and (a, right) in a_to_b for a in range(4))
                for left, right in b_edges
            ):
                continue
            survivors += 1
    return survivors


def verify_boundary_profile() -> None:
    names = ("x", "u", "v", "a", "b", "c")
    present = {
        frozenset(edge)
        for edge in (
            ("x", "u"),
            ("x", "v"),
            ("u", "v"),
            ("a", "b"),
            ("a", "c"),
            ("b", "c"),
            ("x", "a"),
            ("u", "b"),
        )
    }
    deficits: dict[tuple[str, str], int] = {}
    for left, right in combinations(names, 2):
        pair = frozenset((left, right))
        required = 1 if pair in present else 2
        internal = sum(
            frozenset((left, other)) in present
            and frozenset((right, other)) in present
            for other in names
            if other not in (left, right)
        )
        deficit = required - internal
        if deficit < 0:
            raise AssertionError("the N3 already exceeds an SRG common-neighbor target")
        if deficit:
            deficits[(left, right)] = deficit

    expected = {
        ("x", "a"): 1,
        ("u", "b"): 1,
        ("x", "c"): 1,
        ("u", "c"): 1,
        ("v", "a"): 1,
        ("v", "b"): 1,
        ("v", "c"): 2,
    }
    if deficits != expected:
        raise AssertionError(f"unexpected N3 boundary deficits {deficits}")

    allowed = {frozenset(pair) for pair in deficits}
    if any(
        all(frozenset(pair) in allowed for pair in combinations(triple, 2))
        for triple in combinations(names, 3)
    ):
        raise AssertionError("the allowed boundary-pair graph has a triangle")

    internal_degrees = {
        vertex: sum(vertex in edge for edge in present) for vertex in names
    }
    pair_incidence = Counter()
    for pair, multiplicity in deficits.items():
        for vertex in pair:
            pair_incidence[vertex] += multiplicity
    singletons = tuple(
        14 - internal_degrees[vertex] - pair_incidence[vertex] for vertex in names
    )
    pair_vertices = sum(deficits.values())
    zero_vertices = 99 - len(names) - pair_vertices - sum(singletons)
    if singletons != (9, 9, 8, 9, 9, 8) or zero_vertices != 33:
        raise AssertionError("unexpected singleton or zero-neighbor boundary counts")

    seed = {"x", "b"}
    wave_one = {
        vertex
        for vertex in names
        if vertex not in seed
        and sum(frozenset((vertex, infected)) in present for infected in seed) >= 2
    }
    if wave_one != {"u", "a"}:
        raise AssertionError("unexpected first synchronous percolation wave")
    infected_after_one = seed | wave_one
    wave_two_internal = {
        vertex
        for vertex in names
        if vertex not in infected_after_one
        and sum(
            frozenset((vertex, infected)) in present
            for infected in infected_after_one
        )
        >= 2
    }
    wave_two_pairs = {
        pair for pair in deficits if set(pair) <= infected_after_one
    }
    if wave_two_internal != {"v", "c"} or wave_two_pairs != {
        ("x", "a"),
        ("u", "b"),
    }:
        raise AssertionError("unexpected second synchronous percolation wave")


def verify(joint_certificate: Path = DEFAULT_JOINT_CERTIFICATE) -> None:
    certificate = json.loads(
        joint_certificate.read_text(encoding="utf-8"),
        object_pairs_hook=unique_object,
        parse_constant=reject_json_constant,
    )
    if not isinstance(certificate, dict) or not isinstance(
        certificate.get("branches"), list
    ):
        raise ValueError("invalid joint-cover certificate")
    branches = certificate["branches"]
    if len(branches) != 12:
        raise ValueError("joint certificate must contain twelve branches")

    expected_t = (4, 2, 1, 0, 0, 3, 1, 0, 2, 0, 1, 0)
    expected_signatures = (
        (4,),
        (4, 4),
        (4, 6),
        (4, 4, 4),
        (4, 8),
        (6,),
        (4, 6),
        (6, 6),
        (8,),
        (4, 8),
        (10,),
        (12,),
    )
    expected_bounds = (24, 33, 42, 48, 48, 24, 42, 48, 33, 48, 42, 48)
    actual_t: list[int] = []
    actual_signatures: list[tuple[int, ...]] = []
    actual_bounds: list[int] = []
    for index, branch in enumerate(branches, start=1):
        if not isinstance(branch, dict) or type(branch.get("branch")) is not int:
            raise ValueError("invalid branch object")
        if branch["branch"] != index:
            raise ValueError("branches are not canonically numbered")
        matching = normalize_matching(branch.get("representative"))
        common = len(set(matching).intersection(MATE_MATCHING))
        degree = 12 - 2 * common
        bound = max(24, ceil_multiple_of_three(4 * degree))
        actual_t.append(common)
        actual_signatures.append(alternating_signature(matching))
        actual_bounds.append(bound)
    if tuple(actual_t) != expected_t:
        raise AssertionError("wrong branch mate-edge counts")
    if tuple(actual_signatures) != expected_signatures:
        raise AssertionError("wrong alternating-cycle signatures")
    if tuple(actual_bounds) != expected_bounds:
        raise AssertionError("wrong branch N3 lower bounds")

    distribution = Counter(
        sum(edge not in MATE_MATCHING for edge in matching)
        for matching in perfect_matchings(ENDPOINTS)
    )
    if distribution != {0: 1, 2: 30, 3: 160, 4: 900, 5: 3264, 6: 6040}:
        raise AssertionError("wrong exhaustive matching distribution")

    candidates = abstract_small_edge_candidates()
    if candidates != [(18, (4,) * 9)]:
        raise AssertionError(f"unexpected abstract sub-24 cases {candidates}")
    if enumerate_m18_local_models() != 0:
        raise AssertionError("a forbidden 18-edge local model survived")

    verify_boundary_profile()

    print("PASS N3 count-bound exact checks")
    print("j_edges", 693 * 12 // 2)
    print("global_n3_lower_bound", 24)
    print("global_p6_lower_bound", 209_286 + 24)
    print("branch_t", actual_t)
    print("branch_degrees", [12 - 2 * value for value in actual_t])
    print("branch_n3_bounds", actual_bounds)
    print("matching_distribution", dict(sorted(distribution.items())))
    print("m18_local_survivors", 0)
    print("boundary_pair_vertices", 8)
    print("boundary_singletons", [9, 9, 8, 9, 9, 8])
    print("boundary_zero_vertices", 33)
    print("percolation_wave_1", ["u", "a"])
    print("percolation_wave_2", ["v", "c", "P_xa", "P_ub"])


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "joint_certificate",
        nargs="?",
        type=Path,
        default=DEFAULT_JOINT_CERTIFICATE,
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    verify(args.joint_certificate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
