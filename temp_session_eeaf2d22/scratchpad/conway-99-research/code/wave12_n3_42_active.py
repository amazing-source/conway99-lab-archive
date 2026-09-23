#!/usr/bin/env python3
"""Independent finite checks for the Wave 12 ``n3 = 42`` active domain.

This file does not import any earlier equality checker.  It reconstructs the
active-q arithmetic, exhausts the size-four rooted-flower capacity check,
exhausts the surviving mixed profile's degree-three star, and validates a
machine-readable candidate for a deliberately restricted all-size-two local
subproblem.

The candidate validator checks necessary active-incidence constraints only.
It does not check, construct, or claim an ``srg(99,14,1,2)``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


TARGET_N3 = 42
Q_SUM = 2 * TARGET_N3 // 3
EXPECTED_RAW_PROFILES = (
    (2,) * 14,
    (2,) * 11 + (3, 3),
    (2,) * 12 + (4,),
    (2,) * 8 + (3,) * 4,
    (2,) * 5 + (3,) * 6,
    (2,) * 2 + (3,) * 8,
)
EXPECTED_SURVIVING_PROFILES = (
    (2,) * 14,
    (2,) * 11 + (3, 3),
)


def edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise ValueError("loops are not edges")
    return (left, right) if left < right else (right, left)


def all_edges(order: int) -> frozenset[tuple[int, int]]:
    return frozenset(itertools.combinations(range(order), 2))


def parse_edges(
    values: Iterable[Sequence[int]], order: int, *, name: str
) -> frozenset[tuple[int, int]]:
    parsed: list[tuple[int, int]] = []
    for value in values:
        if len(value) != 2:
            raise AssertionError(f"{name} contains a non-edge record")
        left, right = map(int, value)
        if not (0 <= left < order and 0 <= right < order):
            raise AssertionError(f"{name} endpoint out of range")
        parsed.append(edge(left, right))
    if len(parsed) != len(set(parsed)):
        raise AssertionError(f"{name} contains a duplicate edge")
    return frozenset(parsed)


def degrees(order: int, edges: Iterable[tuple[int, int]]) -> tuple[int, ...]:
    output = [0] * order
    for left, right in edges:
        output[left] += 1
        output[right] += 1
    return tuple(output)


def active_q_profiles(n3_count: int = TARGET_N3) -> tuple[tuple[int, ...], ...]:
    """Enumerate all active-q multisets from scratch.

    The only inputs are ``q >= 2``, ``sum(q)=2*n3/3``, and
    ``3*q(T) <= r-1`` on ``r`` active triangles.
    """

    if n3_count < 0 or (2 * n3_count) % 3:
        raise ValueError("2*n3 must be a nonnegative multiple of three")
    total = 2 * n3_count // 3
    profiles: set[tuple[int, ...]] = set()

    def visit(remaining: int, least: int, values: tuple[int, ...]) -> None:
        if remaining == 0:
            order = len(values)
            if values and all(3 * value <= order - 1 for value in values):
                profiles.add(values)
            return
        for value in range(least, min(12, remaining) + 1):
            visit(remaining - value, value, (*values, value))

    visit(total, 2, ())
    return tuple(
        sorted(
            profiles,
            key=lambda profile: (
                -len(profile),
                max(profile),
                profile,
            ),
        )
    )


def k_degree_profile(q_values: Sequence[int]) -> tuple[int, ...]:
    order = len(q_values)
    return tuple(order - 1 - 3 * value for value in q_values)


def forced_singleton_lower_bound(k_degrees: Sequence[int]) -> int:
    """Count point incidences forced singleton by an incident K-edge deficit."""

    return sum(max(0, 3 - degree) for degree in k_degrees)


def profile_table() -> tuple[dict[str, object], ...]:
    output = []
    for profile in active_q_profiles():
        k_degrees = k_degree_profile(profile)
        if min(k_degrees) < 0 or sum(k_degrees) % 2:
            raise AssertionError("active profile has a nongraphical degree checksum")
        output.append(
            {
                "active_order": len(profile),
                "q_histogram": dict(sorted(Counter(profile).items())),
                "k_degree_histogram": dict(sorted(Counter(k_degrees).items())),
                "k_edge_count": sum(k_degrees) // 2,
                "forced_singleton_lower_bound": forced_singleton_lower_bound(
                    k_degrees
                ),
                "survives_no_singleton_premise": min(k_degrees) >= 3,
            }
        )
    return tuple(output)


def expansion_bound(order: int, point_size: int) -> tuple[int, int, bool]:
    """Two external representatives per occurrence must be distinct."""

    if not 2 <= point_size <= order:
        raise ValueError("point size outside the active domain")
    available = order - point_size
    required = 2 * point_size
    return available, required, required <= available


def size_four_flower_census(
    active_order: int, maximum_k_degree: int
) -> dict[str, object]:
    """Exhaust all petal sizes after the expansion bound gives sizes 2--4.

    A size-two petal has singleton external side.  Its crossing with the
    size-four root is empty in L, so its endpoint is K-adjacent to all four
    root vertices.  All eight external petal parts are disjoint.
    """

    if active_order not in (13, 14):
        raise ValueError("the Wave 12 surviving orders are 13 and 14")
    feasible = 0
    capacity_rejected = 0
    size_two_histogram: Counter[int] = Counter()
    degree_histogram: Counter[int] = Counter()
    survivors = 0
    for petals in itertools.product((2, 3, 4), repeat=8):
        external_slots = sum(size - 1 for size in petals)
        if external_slots > active_order - 4:
            capacity_rejected += 1
            continue
        feasible += 1
        size_two_petals = petals.count(2)
        root_degree_lower = 3 + size_two_petals
        size_two_histogram[size_two_petals] += 1
        degree_histogram[root_degree_lower] += 1
        survivors += root_degree_lower <= maximum_k_degree
    if feasible + capacity_rejected != 3**8:
        raise AssertionError("size-four word count changed")
    return {
        "active_order": active_order,
        "maximum_k_degree": maximum_k_degree,
        "total_profiles": 3**8,
        "capacity_rejections": capacity_rejected,
        "capacity_feasible": feasible,
        "size_two_petal_histogram": dict(sorted(size_two_histogram.items())),
        "root_degree_lower_histogram": dict(sorted(degree_histogram.items())),
        "survivors": survivors,
    }


def common_point_forbids_pair_owner(
    first: frozenset[int],
    second: frozenset[int],
    proposed_owner: frozenset[int],
) -> bool:
    intersections = (
        first & second,
        first & proposed_owner,
        second & proposed_owner,
    )
    return (
        all(len(value) == 1 for value in intersections)
        and len(frozenset().union(*intersections)) == 3
    )


def mixed_degree_three_star_census() -> dict[str, object]:
    """Exhaust the local closure around one q=3 triangle in the mixed profile.

    Labels are ``b=0`` and its three K-neighbors ``x=1,y=2,z=3``.  Degree
    three and three non-singleton point cliques force the point sets
    ``bx,by,bz``.  Singleton crossings at ``b`` force ``xyz`` to be a K3,
    and the common-point rule forbids those three cross edges from acquiring
    point owners.

    At occurrence ``x`` of point ``bx``, the other two point sets have
    disjoint nonempty external parts.  Singleton crossing with ``b`` confines
    both parts to ``{y,z}``; this finite routine enumerates every assignment.
    """

    b, x, y, z = 0, 1, 2, 3
    neighbors = frozenset((x, y, z))
    point_bx = frozenset((b, x))
    point_by = frozenset((b, y))
    point_bz = frozenset((b, z))
    forced_k = frozenset(
        (
            edge(b, x),
            edge(b, y),
            edge(b, z),
            edge(x, y),
            edge(x, z),
            edge(y, z),
        )
    )
    forbidden_f = frozenset(
        candidate
        for candidate, first, second in (
            (edge(x, y), point_bx, point_by),
            (edge(x, z), point_bx, point_bz),
            (edge(y, z), point_by, point_bz),
        )
        if common_point_forbids_pair_owner(
            first, second, frozenset(candidate)
        )
    )
    if forbidden_f != frozenset((edge(x, y), edge(x, z), edge(y, z))):
        raise AssertionError("mixed-star common-point veto changed")

    available = tuple(sorted(neighbors - {x}))
    nonempty_subsets = tuple(
        frozenset(value)
        for size in range(1, len(available) + 1)
        for value in itertools.combinations(available, size)
    )
    records = []
    for left_external in nonempty_subsets:
        for right_external in nonempty_subsets:
            if left_external & right_external:
                continue
            owned_edges = frozenset(
                edge(x, endpoint)
                for endpoint in left_external | right_external
            )
            conflicts = owned_edges & forbidden_f
            records.append(
                {
                    "left_external": sorted(left_external),
                    "right_external": sorted(right_external),
                    "owned_edges": [list(value) for value in sorted(owned_edges)],
                    "common_point_conflicts": [
                        list(value) for value in sorted(conflicts)
                    ],
                    "survives": not conflicts,
                }
            )
    if len(records) != 2 or any(record["survives"] for record in records):
        raise AssertionError("mixed degree-three star acquired a survivor")
    return {
        "forced_k_edges": [list(value) for value in sorted(forced_k)],
        "forbidden_f_cross_edges": [
            list(value) for value in sorted(forbidden_f)
        ],
        "assignments": records,
        "assignment_count": len(records),
        "survivors": 0,
    }


def candidate_digest(value: object) -> str:
    payload = (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_size2_candidate(certificate: dict[str, object]) -> dict[str, object]:
    """Validate the restricted all-size-two active-local certificate."""

    if certificate.get("schema") != "wave12-n3-42-all-size2-active-local-v1":
        raise AssertionError("wrong candidate schema")
    if certificate.get("claim_label") != "CANDIDATE":
        raise AssertionError("candidate status inflation")
    if certificate.get("target_result") != "UNKNOWN":
        raise AssertionError("target status inflation")
    order = int(certificate.get("active_order", -1))
    if order != 14:
        raise AssertionError("wrong active order")
    q_values = tuple(map(int, certificate.get("q_values", ())))
    if q_values != (2,) * order:
        raise AssertionError("candidate is not the all-q=2 profile")

    point_edges = parse_edges(
        certificate.get("point_sets", ()), order, name="point_sets"
    )
    k_edges = parse_edges(certificate.get("K_edges", ()), order, name="K_edges")
    l_edges = parse_edges(certificate.get("L_edges", ()), order, name="L_edges")
    if len(point_edges) != 21 or degrees(order, point_edges) != (3,) * order:
        raise AssertionError("point incidence is not a cubic size-two system")
    for triangle in itertools.combinations(range(order), 3):
        if all(edge(*pair) in point_edges for pair in itertools.combinations(triangle, 2)):
            raise AssertionError("point system contains a forbidden Berge triangle")
    if len(k_edges) != 49 or degrees(order, k_edges) != (7,) * order:
        raise AssertionError("K is not 7-regular")
    if not point_edges <= k_edges:
        raise AssertionError("a size-two point is not a K-clique")
    if l_edges != all_edges(order) - k_edges:
        raise AssertionError("L is not the simple complement of K")

    local_crossings = 0
    for root in range(order):
        mates = tuple(
            right if left == root else left
            for left, right in point_edges
            if root in (left, right)
        )
        if len(mates) != 3:
            raise AssertionError("wrong number of points through an active triangle")
        for left, right in itertools.combinations(mates, 2):
            local_crossings += 1
            if edge(left, right) not in k_edges:
                raise AssertionError("a singleton local L-crossing is nonempty")

    cycle = tuple(map(int, certificate.get("support_opportunity_cycle", ())))
    if len(cycle) != len(point_edges) or set(cycle) != set(range(len(point_edges))):
        raise AssertionError("support opportunity cycle is not Hamiltonian")
    ordered_points = tuple(sorted(point_edges))
    support_sums = [0] * len(ordered_points)
    support_edges: set[tuple[int, int]] = set()
    for left_index, right_index in zip(cycle, (*cycle[1:], cycle[0]), strict=True):
        support_edges.add(edge(left_index, right_index))
        left_point = ordered_points[left_index]
        right_point = ordered_points[right_index]
        if set(left_point) & set(right_point):
            raise AssertionError("a support opportunity joins meeting point sets")
        cross_pairs = frozenset(
            edge(left, right)
            for left in left_point
            for right in right_point
        )
        if cross_pairs & k_edges:
            raise AssertionError("a support opportunity is not a full L K2,2")
        if not cross_pairs <= l_edges or len(cross_pairs) != 4:
            raise AssertionError("wrong support opportunity crossing size")
        support_sums[left_index] += 4
        support_sums[right_index] += 4
    if support_sums != [8] * len(ordered_points):
        raise AssertionError("support opportunities do not meet the 4|S| checksum")

    line_edges = {
        (left, right)
        for left, right in itertools.combinations(range(len(ordered_points)), 2)
        if set(ordered_points[left]) & set(ordered_points[right])
    }
    partial_edges = line_edges | support_edges
    partial_adjacency = [set() for _ in ordered_points]
    for left, right in partial_edges:
        partial_adjacency[left].add(right)
        partial_adjacency[right].add(left)
    adjacent_cap_violations = 0
    universal_two_cap_violations = 0
    for left, right in itertools.combinations(range(len(ordered_points)), 2):
        common = len(partial_adjacency[left] & partial_adjacency[right])
        if (left, right) in partial_edges and common > 1:
            adjacent_cap_violations += 1
        if common > 2:
            universal_two_cap_violations += 1
    if adjacent_cap_violations == 0 or universal_two_cap_violations == 0:
        raise AssertionError("the retained diagnostic unexpectedly passed SRG caps")

    restrictions = tuple(certificate.get("restrictions", ()))
    required_restrictions = (
        "all_active_point_sets_have_size_2",
        "active_local_constraints_only",
        "no_99_vertex_adjacency_matrix",
        "no_global_lambda_mu_completion",
        "support_cycle_records_opportunities_not_asserted_graph_edges",
    )
    if restrictions != required_restrictions:
        raise AssertionError("candidate restriction boundary changed")

    return {
        "status": "PASS restricted n3=42 active-local candidate",
        "active_order": order,
        "point_sets": len(point_edges),
        "K_edges": len(k_edges),
        "L_edges": len(l_edges),
        "local_singleton_crossings_checked": local_crossings,
        "support_opportunity_cycle_length": len(cycle),
        "support_sum_per_point": 8,
        "diagnostic_adjacent_cap_violations": adjacent_cap_violations,
        "diagnostic_universal_two_cap_violations": universal_two_cap_violations,
        "candidate_sha256": candidate_digest(certificate),
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
    }


def verify(certificate_path: Path | None = None) -> dict[str, object]:
    profiles = active_q_profiles()
    if profiles != EXPECTED_RAW_PROFILES:
        raise AssertionError(f"unexpected n3=42 profiles: {profiles}")
    table = profile_table()
    surviving = tuple(
        profile
        for profile, row in zip(profiles, table, strict=True)
        if row["survives_no_singleton_premise"]
    )
    if surviving != EXPECTED_SURVIVING_PROFILES:
        raise AssertionError(f"wrong no-singleton survivors: {surviving}")
    if tuple(row["forced_singleton_lower_bound"] for row in table) != (
        0,
        0,
        3,
        4,
        12,
        24,
    ):
        raise AssertionError("forced-singleton totals changed")

    expansion = {
        order: tuple(
            size
            for size in range(2, order + 1)
            if expansion_bound(order, size)[2]
        )
        for order in (13, 14)
    }
    if expansion != {13: (2, 3, 4), 14: (2, 3, 4)}:
        raise AssertionError("Wave 12 expansion bound changed")

    size4 = {
        13: size_four_flower_census(13, 6),
        14: size_four_flower_census(14, 7),
    }
    if size4[13]["survivors"] or size4[14]["survivors"]:
        raise AssertionError("a size-four local flower survived")
    if (
        size4[13]["capacity_feasible"],
        size4[14]["capacity_feasible"],
    ) != (9, 45):
        raise AssertionError("size-four capacity census changed")

    mixed = mixed_degree_three_star_census()
    result: dict[str, object] = {
        "status": "PASS n3=42 active-profile and local-subproblem census",
        "q_sum": Q_SUM,
        "raw_profile_count": len(profiles),
        "profile_table": table,
        "surviving_profile_count_after_singletons": len(surviving),
        "surviving_profiles": [list(profile) for profile in surviving],
        "expansion_surviving_sizes": expansion,
        "size_four_census": size4,
        "mixed_degree_three_star": mixed,
        "mixed_profile_local_survivors": 0,
        "remaining_unrestricted_active_profile": list((2,) * 14),
        "target_result": "UNKNOWN",
    }
    if certificate_path is not None:
        certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
        result["restricted_candidate"] = validate_size2_candidate(certificate)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    result = verify(arguments.certificate)
    if arguments.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
        print("raw_profiles", result["raw_profile_count"])
        print(
            "surviving_profiles",
            result["surviving_profiles"],
        )
        print(
            "mixed_profile_local_survivors",
            result["mixed_profile_local_survivors"],
        )
        if "restricted_candidate" in result:
            print(
                "restricted_candidate",
                result["restricted_candidate"]["status"],
            )
            print(
                "candidate_sha256",
                result["restricted_candidate"]["candidate_sha256"],
            )
        print("target_result", result["target_result"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
