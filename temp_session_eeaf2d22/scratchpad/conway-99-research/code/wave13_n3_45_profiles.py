#!/usr/bin/env python3
"""Exact arithmetic and local finite checks for the Wave 13 ``n3=45`` lane.

The program starts only from the frozen active-triangle premises used in
Waves 9--12.  It enumerates every active-``q`` multiset, applies the
non-singleton degree requirement and the already verified degree-three
obstruction, and then checks local point flowers in the two remaining
profiles.

The final all-``q=2`` order-fifteen frontier is deliberately *not* declared
infeasible.  The output records the exact weakened incidence signatures that
remain after the local checks.  This is discovery code and its results stay
``CANDIDATE`` until replayed independently.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


TARGET_N3 = 45
Q_SUM = 2 * TARGET_N3 // 3
ALLOWED_H_DEGREES = frozenset((0, 4, 6, 8, 10, 12))


def edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise ValueError("loops are not graph edges")
    return (left, right) if left < right else (right, left)


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_sha256() -> str:
    return sha256_bytes(Path(__file__).resolve().read_bytes())


def active_q_profiles(n3_count: int = TARGET_N3) -> tuple[tuple[int, ...], ...]:
    """Enumerate every multiset with ``q>=2`` and ``3q<=r-1``."""

    if n3_count < 0 or (2 * n3_count) % 3:
        raise ValueError("2*n3 must be a nonnegative multiple of three")
    total = 2 * n3_count // 3
    profiles: list[tuple[int, ...]] = []

    def visit(remaining: int, least: int, values: tuple[int, ...]) -> None:
        if remaining == 0:
            order = len(values)
            if values and all(3 * value <= order - 1 for value in values):
                profiles.append(values)
            return
        for value in range(least, min(12, remaining) + 1):
            visit(remaining - value, value, (*values, value))

    visit(total, 2, ())
    return tuple(
        sorted(
            profiles,
            key=lambda profile: (-len(profile), max(profile), profile),
        )
    )


def k_degree_profile(q_values: Sequence[int]) -> tuple[int, ...]:
    order = len(q_values)
    return tuple(order - 1 - 3 * value for value in q_values)


def forced_singleton_lower_bound(k_degrees: Sequence[int]) -> int:
    """Three non-singleton point cliques need three distinct incident edges."""

    return sum(max(0, 3 - value) for value in k_degrees)


def profile_table() -> tuple[dict[str, object], ...]:
    rows = []
    for profile in active_q_profiles():
        degrees = k_degree_profile(profile)
        if min(degrees) < 0 or sum(degrees) % 2:
            raise AssertionError("an active profile has an invalid K checksum")
        degree_filtered = min(degrees) >= 3
        rows.append(
            {
                "active_order": len(profile),
                "q_values": list(profile),
                "q_histogram": dict(sorted(Counter(profile).items())),
                "k_degrees": list(degrees),
                "k_degree_histogram": dict(sorted(Counter(degrees).items())),
                "k_edge_count": sum(degrees) // 2,
                "forced_singleton_lower_bound": forced_singleton_lower_bound(
                    degrees
                ),
                "survives_no_singleton_degree_filter": degree_filtered,
                "survives_degree_three_obstruction": (
                    degree_filtered and min(degrees) >= 4
                ),
            }
        )
    return tuple(rows)


def maximum_point_size(active_order: int) -> int:
    """Return the largest ``s`` satisfying the expansion bound ``2s<=r-s``."""

    if active_order < 2:
        raise ValueError("active order must be at least two")
    return max(
        (
            size
            for size in range(2, active_order + 1)
            if 2 * size <= active_order - size
        ),
        default=1,
    )


def flower_census(
    *,
    active_order: int,
    root_size: int,
    maximum_petal_size: int,
    root_k_degrees: Sequence[int],
) -> dict[str, object]:
    """Exhaust every ordered petal-size word around one point.

    The two petals at each occurrence are grouped consecutively.  External
    petal parts are pairwise disjoint by linearity and the common-point rule.
    A size-two petal has singleton external side, so its endpoint is
    K-adjacent to every root label.  A larger petal additionally contributes
    its own external labels to the K-degree of its base occurrence.
    """

    if len(root_k_degrees) != root_size:
        raise ValueError("one K-degree is required for each root occurrence")
    if not 2 <= root_size <= active_order:
        raise ValueError("invalid root size")
    if maximum_petal_size < 2:
        raise ValueError("petal sizes must be at least two")

    petal_count = 2 * root_size
    outside_capacity = active_order - root_size
    alphabet = tuple(range(2, maximum_petal_size + 1))
    statistics: Counter[str] = Counter()
    singleton_histogram: Counter[int] = Counter()
    maximum_lower_degree_histogram: Counter[int] = Counter()
    first_capacity_survivor: tuple[int, ...] | None = None
    first_degree_survivor: tuple[int, ...] | None = None

    for petals in itertools.product(alphabet, repeat=petal_count):
        statistics["total_words"] += 1
        external_slots = sum(value - 1 for value in petals)
        if external_slots > outside_capacity:
            statistics["capacity_rejections"] += 1
            continue
        statistics["capacity_feasible"] += 1
        if first_capacity_survivor is None:
            first_capacity_survivor = petals
        singleton_count = petals.count(2)
        lower_degrees = []
        for occurrence in range(root_size):
            based_petals = petals[2 * occurrence : 2 * occurrence + 2]
            additional_non_singleton = sum(
                value - 1 for value in based_petals if value > 2
            )
            lower_degrees.append(
                root_size - 1
                + singleton_count
                + additional_non_singleton
            )
        singleton_histogram[singleton_count] += 1
        maximum_lower_degree_histogram[max(lower_degrees)] += 1
        if all(
            lower <= capacity
            for lower, capacity in zip(
                lower_degrees, root_k_degrees, strict=True
            )
        ):
            statistics["k_degree_survivors"] += 1
            if first_degree_survivor is None:
                first_degree_survivor = petals
        else:
            statistics["k_degree_rejections"] += 1

    if statistics["total_words"] != len(alphabet) ** petal_count:
        raise AssertionError("flower word count changed")
    return {
        "active_order": active_order,
        "root_size": root_size,
        "maximum_petal_size": maximum_petal_size,
        "root_k_degrees": list(root_k_degrees),
        "petal_count": petal_count,
        "outside_capacity": outside_capacity,
        "statistics": dict(sorted(statistics.items())),
        "singleton_petal_histogram": dict(sorted(singleton_histogram.items())),
        "maximum_root_degree_lower_bound_histogram": dict(
            sorted(maximum_lower_degree_histogram.items())
        ),
        "first_capacity_survivor": (
            list(first_capacity_survivor)
            if first_capacity_survivor is not None
            else None
        ),
        "first_k_degree_survivor": (
            list(first_degree_survivor)
            if first_degree_survivor is not None
            else None
        ),
    }


def size_three_local_modes(
    active_order: int,
    q_values: Sequence[int],
) -> tuple[dict[str, object], ...]:
    """Enumerate exact rooted size-three modes after local forcing.

    ``t_i`` is the number of size-three points through root label ``i``.
    ``z_i`` is the number of its other size-three petals whose 2-by-2
    crossing with the root point is empty in L (hence full in K).  All other
    size-three petals have a full L crossing and contribute four to the
    fixed-point sum.
    """

    if len(q_values) != 3 or any(value not in (2, 3) for value in q_values):
        raise ValueError("the local root needs three q-values in {2,3}")
    k_degrees = tuple(active_order - 1 - 3 * value for value in q_values)
    fixed_point_total = 2 * sum(q_values)
    output = []
    for t_values in itertools.product((1, 2, 3), repeat=3):
        f_degrees = tuple(3 + value for value in t_values)
        if any(
            used > available
            for used, available in zip(f_degrees, k_degrees, strict=True)
        ):
            continue
        external_slots = 3 + sum(t_values)
        if external_slots > active_order - 3:
            continue
        for zero_modes in itertools.product(
            *(range(value) for value in t_values)
        ):
            u_degrees = tuple(
                degree - f_degree
                for degree, f_degree in zip(
                    k_degrees, f_degrees, strict=True
                )
            )
            forced_u = tuple(
                sum(
                    (3 - t_values[other]) + 2 * zero_modes[other]
                    for other in range(3)
                    if other != index
                )
                for index in range(3)
            )
            if any(
                forced > available
                for forced, available in zip(
                    forced_u, u_degrees, strict=True
                )
            ):
                continue
            full_l_crossings = sum(
                t_values[index] - 1 - zero_modes[index]
                for index in range(3)
            )
            overlap_h_contribution = 4 * full_l_crossings
            if overlap_h_contribution > fixed_point_total:
                continue
            output.append(
                {
                    "q_values": list(q_values),
                    "k_degrees": list(k_degrees),
                    "t_values": list(t_values),
                    "zero_l_crossings_by_occurrence": list(zero_modes),
                    "full_l_crossings": full_l_crossings,
                    "overlap_h_contribution": overlap_h_contribution,
                    "fixed_point_total": fixed_point_total,
                    "remaining_fixed_point_support": (
                        fixed_point_total - overlap_h_contribution
                    ),
                    "u_degrees": list(u_degrees),
                    "forced_u_lower_bounds": list(forced_u),
                    "external_slots": external_slots,
                }
            )
    return tuple(output)


def canonical_mode_histogram(
    modes: Iterable[dict[str, object]],
) -> dict[str, int]:
    histogram: Counter[str] = Counter()
    for mode in modes:
        pairs = sorted(
            zip(
                mode["t_values"],
                mode["zero_l_crossings_by_occurrence"],
                strict=True,
            )
        )
        key = ",".join(f"{t}:{z}" for t, z in pairs)
        histogram[key] += 1
    return dict(sorted(histogram.items()))


def cubic_graphs(order: int) -> tuple[frozenset[tuple[int, int]], ...]:
    """Enumerate labeled cubic graphs at the only small orders needed."""

    if order not in (4, 6):
        raise ValueError("only orders four and six are used")
    possible = tuple(itertools.combinations(range(order), 2))
    answers = []
    for chosen in itertools.combinations(possible, 3 * order // 2):
        degrees = Counter(vertex for item in chosen for vertex in item)
        if all(degrees[vertex] == 3 for vertex in range(order)):
            answers.append(frozenset(chosen))
    return tuple(answers)


def contains_triangle(
    graph_edges: frozenset[tuple[int, int]], order: int
) -> bool:
    return any(
        all(edge(*pair) in graph_edges for pair in itertools.combinations(triple, 2))
        for triple in itertools.combinations(range(order), 3)
    )


def line_graph_open_neighborhoods(
    graph_edges: frozenset[tuple[int, int]],
) -> tuple[frozenset[int], ...]:
    ordered = tuple(sorted(graph_edges))
    return tuple(
        frozenset(
            other_index
            for other_index, other in enumerate(ordered)
            if other_index != index and set(item) & set(other)
        )
        for index, item in enumerate(ordered)
    )


def is_k33(graph_edges: frozenset[tuple[int, int]]) -> bool:
    if len(graph_edges) != 9:
        return False
    for first_side in itertools.combinations(range(6), 3):
        if 0 not in first_side:
            continue
        left = set(first_side)
        right = set(range(6)) - left
        expected = {
            edge(first, second) for first in left for second in right
        }
        if graph_edges == expected:
            return True
    return False


def mixed_order14_reduction() -> dict[str, object]:
    """Replay the finite local reduction of the mixed order-fourteen profile."""

    q2_modes = size_three_local_modes(14, (2, 2, 2))
    q3_assignments = tuple(
        values
        for values in itertools.product((2, 3), repeat=3)
        if 3 in values
    )
    q3_mode_rows = tuple(
        {
            "q_values": list(q_values),
            "mode_count": len(size_three_local_modes(14, q_values)),
            "modes": list(size_three_local_modes(14, q_values)),
        }
        for q_values in q3_assignments
    )
    mixed_modes = tuple(
        mode for row in q3_mode_rows for mode in row["modes"]
    )
    if len(q3_assignments) != 7:
        raise AssertionError("the ordered q3-containing root cover changed")
    if set(q3_assignments) != {
        values
        for values in itertools.product((2, 3), repeat=3)
        if 3 in values
    }:
        raise AssertionError("a q3-containing root assignment is missing")
    if {
        tuple(mode["t_values"]) for mode in q2_modes
    } != {(2, 2, 2)}:
        raise AssertionError("the q2-only size-three mode changed")
    if mixed_modes:
        raise AssertionError("a size-three point containing q=3 survived")

    small_cubic = {}
    for order in (4, 6):
        labeled = cubic_graphs(order)
        triangle_free = tuple(
            graph for graph in labeled if not contains_triangle(graph, order)
        )
        small_cubic[order] = {
            "labeled_cubic": len(labeled),
            "labeled_triangle_free_cubic": len(triangle_free),
            "all_triangle_free_graphs_are_K3,3": (
                all(is_k33(graph) for graph in triangle_free)
                if order == 6
                else not triangle_free
            ),
            "all_line_graphs_open_twin_free": all(
                len(set(line_graph_open_neighborhoods(graph)))
                == len(graph_edges := graph)
                for graph in triangle_free
            ),
        }

    # If m size-three points remain, their intersection graph R is cubic and
    # has e=3m/2 edge labels.  Every such label's third point needs a distinct
    # incidence at a q=2,t=0 label.  There are only 3(12-e) such incidences.
    candidate_orders = []
    for order in range(4, 13, 2):
        edge_count = 3 * order // 2
        if edge_count <= 3 * (12 - edge_count):
            candidate_orders.append(order)
    if candidate_orders != [4, 6]:
        raise AssertionError("mixed-profile cubic order bound changed")

    surviving_graph_type = {
        "order": 6,
        "type": "K3,3",
        "edge_labels": 9,
        "q2_t0_labels": 3,
        "open_twin_injection_possible": False,
    }
    # In an all-size-two branch the point graph is cubic and triangle-free.
    # At a q=3 label x, its three point-mates are K-neighbours.  The six
    # length-two paths from x have endpoints outside that neighbourhood, and
    # one endpoint can receive at most three paths.  Hence at least two
    # distinct distance-two labels are also forced K-neighbours of x.
    length_two_paths = 3 * 2
    maximum_paths_per_endpoint = 3
    minimum_distance_two_labels = (
        length_two_paths + maximum_paths_per_endpoint - 1
    ) // maximum_paths_per_endpoint
    all_size_two_k_degree_lower_bound = 3 + minimum_distance_two_labels
    if all_size_two_k_degree_lower_bound <= 4:
        raise AssertionError("the q=3 all-size-two obstruction disappeared")
    return {
        "q2_only_local_modes": list(q2_modes),
        "q3_containing_assignments_checked": [
            list(values) for values in q3_assignments
        ],
        "q3_containing_assignment_count": len(q3_assignments),
        "q3_containing_mode_census": list(q3_mode_rows),
        "q3_containing_local_modes": list(mixed_modes),
        "candidate_cubic_orders": candidate_orders,
        "small_cubic_census": small_cubic,
        "last_graph_type": surviving_graph_type,
        "size_three_branch_survivors": 0,
        "all_size_two_branch": {
            "length_two_paths_from_q3_label": length_two_paths,
            "maximum_paths_per_distance_two_endpoint": (
                maximum_paths_per_endpoint
            ),
            "minimum_distinct_distance_two_labels": (
                minimum_distance_two_labels
            ),
            "forced_K_degree_lower_bound": (
                all_size_two_k_degree_lower_bound
            ),
            "available_K_degree": 4,
            "contradiction": all_size_two_k_degree_lower_bound > 4,
        },
        "profile_survivors": 0,
    }


def all_q2_incidence_signatures() -> tuple[dict[str, object], ...]:
    """Enumerate exact degree/type-count signatures at order fifteen.

    The four locally surviving size-three types are ``111``, ``122``,
    ``222``, and ``223``.  The final type has exactly one degree-three label,
    so its count is divisible by three when incidences are summed globally.
    """

    signatures = []
    for size3_points in range(1, 16, 2):
        size2_points = (45 - 3 * size3_points) // 2
        for type111 in range(size3_points + 1):
            for type122 in range(size3_points - type111 + 1):
                for type222 in range(
                    size3_points - type111 - type122 + 1
                ):
                    type223 = (
                        size3_points - type111 - type122 - type222
                    )
                    degree1_incidences = 3 * type111 + type122
                    degree2_incidences = (
                        2 * type122 + 3 * type222 + 2 * type223
                    )
                    degree3_incidences = type223
                    if degree2_incidences % 2 or degree3_incidences % 3:
                        continue
                    degree1_labels = degree1_incidences
                    degree2_labels = degree2_incidences // 2
                    degree3_labels = degree3_incidences // 3
                    used_labels = (
                        degree1_labels + degree2_labels + degree3_labels
                    )
                    if used_labels > 15:
                        continue
                    signatures.append(
                        {
                            "size2_points": size2_points,
                            "size3_points": size3_points,
                            "type_counts": {
                                "111": type111,
                                "122": type122,
                                "222": type222,
                                "223": type223,
                            },
                            "t_degree_histogram": {
                                "0": 15 - used_labels,
                                "1": degree1_labels,
                                "2": degree2_labels,
                                "3": degree3_labels,
                            },
                            "point_incidence_checksum": (
                                2 * size2_points + 3 * size3_points
                            ),
                        }
                    )
    return tuple(signatures)


def audit() -> dict[str, object]:
    expected_profiles = (
        (2,) * 15,
        (2,) * 12 + (3, 3),
        (2,) * 13 + (4,),
        (2,) * 9 + (3,) * 4,
        (2,) * 11 + (4, 4),
        (2,) * 10 + (3, 3, 4),
        (2,) * 6 + (3,) * 6,
        (2,) * 3 + (3,) * 8,
        (3,) * 10,
    )
    profiles = active_q_profiles()
    if profiles != expected_profiles:
        raise AssertionError(f"unexpected n3=45 profiles: {profiles}")
    table = profile_table()
    after_degree = tuple(
        row["q_values"]
        for row in table
        if row["survives_no_singleton_degree_filter"]
    )
    after_degree_three = tuple(
        row["q_values"]
        for row in table
        if row["survives_degree_three_obstruction"]
    )
    if len(after_degree) != 3 or len(after_degree_three) != 2:
        raise AssertionError("active-profile filters changed")

    flowers = {
        "order15_size5": flower_census(
            active_order=15,
            root_size=5,
            maximum_petal_size=5,
            root_k_degrees=(8,) * 5,
        ),
        "order15_size4": flower_census(
            active_order=15,
            root_size=4,
            maximum_petal_size=4,
            root_k_degrees=(8,) * 4,
        ),
        "order14_size4": flower_census(
            active_order=14,
            root_size=4,
            maximum_petal_size=4,
            root_k_degrees=(7,) * 4,
        ),
    }
    if any(
        row["statistics"].get("k_degree_survivors", 0)
        for row in flowers.values()
    ):
        raise AssertionError("a size-four or size-five flower survived")

    order15_modes = size_three_local_modes(15, (2, 2, 2))
    canonical_t = {
        tuple(sorted(mode["t_values"])) for mode in order15_modes
    }
    expected_t = {
        (1, 1, 1),
        (1, 2, 2),
        (2, 2, 2),
        (2, 2, 3),
    }
    if canonical_t != expected_t:
        raise AssertionError("order-fifteen size-three modes changed")
    signatures = all_q2_incidence_signatures()
    if len(signatures) != 59:
        raise AssertionError("global incidence-signature count changed")

    result = {
        "schema": "conway99-wave13-n3-45-local-census-v1",
        "builder_source_sha256": source_sha256(),
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty_status": "UNKNOWN",
        "n3": TARGET_N3,
        "q_sum": Q_SUM,
        "raw_active_profiles": len(profiles),
        "profile_table": list(table),
        "profiles_after_no_singleton_degree_filter": list(after_degree),
        "profiles_after_degree_three_obstruction": list(after_degree_three),
        "maximum_point_size_by_active_order": {
            str(order): maximum_point_size(order) for order in (13, 14, 15)
        },
        "flower_censuses": flowers,
        "mixed_order14_reduction": mixed_order14_reduction(),
        "order15_size_three_local_modes": list(order15_modes),
        "order15_size_three_canonical_mode_histogram": (
            canonical_mode_histogram(order15_modes)
        ),
        "order15_incidence_signature_count": len(signatures),
        "order15_incidence_signatures": list(signatures),
        "remaining_frontier": (
            "r=15, q=2^15, K 8-regular, every active point has size 2 or 3"
        ),
        "limitations": [
            "conditional_on_the_frozen_active_triangle_premises",
            "local_and_integer_checks_only",
            "no_completed_99_vertex_graph",
            "no_claim_that_the_remaining_frontier_is_realizable",
            "no_nonexistence_claim_for_n3_45_or_the_target",
        ],
    }
    result["semantic_sha256"] = sha256_bytes(canonical_json_bytes(result))
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args(argv)
    result = audit()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    if arguments.json:
        print(rendered, end="")
    else:
        print("PASS conditional n3=45 active-profile/local census")
        print("raw_active_profiles", result["raw_active_profiles"])
        print(
            "post_degree_three_profiles",
            len(result["profiles_after_degree_three_obstruction"]),
        )
        print(
            "mixed_order14_profile_survivors",
            result["mixed_order14_reduction"]["profile_survivors"],
        )
        print(
            "order15_local_mode_types",
            sorted(
                {
                    tuple(sorted(mode["t_values"]))
                    for mode in result["order15_size_three_local_modes"]
                }
            ),
        )
        print(
            "order15_incidence_signatures",
            result["order15_incidence_signature_count"],
        )
        print("remaining_frontier", result["remaining_frontier"])
        print("claim_label", result["claim_label"])
        print("target_result", result["target_result"])
        print("semantic_sha256", result["semantic_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
