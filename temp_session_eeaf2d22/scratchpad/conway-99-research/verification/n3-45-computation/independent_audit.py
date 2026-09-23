#!/usr/bin/env python3
"""Independent arithmetic and witness audit for the frozen Wave 13 artifacts.

This file deliberately does not import either Wave 13 discovery module.  It
reconstructs the finite arithmetic, rooted local modes, branch cover, scan
digest, and positive diagnostic witness from the mathematical definitions.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence


ORDER = 15
K_DEGREE = 8
ROOT = frozenset((0, 1, 2))
MODE_WORDS = ("111", "122", "222", "223")
MODE_MINIMUM_POINTS = {
    mode: 1 + sum(int(value) - 1 for value in mode)
    for mode in MODE_WORDS
}
EXPECTED_BRANCHES = (
    (1, "111"),
    (3, "111"),
    (3, "122"),
    (5, "111"),
    (5, "122"),
    (5, "222"),
    (5, "223"),
    (7, "111"),
    (7, "122"),
    (7, "222"),
    (7, "223"),
    (9, "111"),
    (9, "122"),
    (9, "222"),
    (9, "223"),
    (11, "222"),
    (11, "223"),
)
EXPECTED_INPUT_HASHES = {
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "agents/2026-07-22-wave13-n3-45-computational.md":
        "f1ace31438aa147018cb8210fa92cd940a0a4795e698bc09d34f3537debf8904",
    "code/wave13_n3_45_profiles.py":
        "7685a370166c0caa41460d5cbfab3b3a51d28da52441db63f5befeb396e4cf7c",
    "code/wave13_n3_45_active_sat.py":
        "ad4b0c41e7aeebb3f9b9c5d1253c317e59b96d69f3d782f2ea83de655bf052e7",
    "code/wave13_n3_45_test.py":
        "0d2d4d868618ce714599c014ab0f8ac247c2f240a521848433fe94298bfbd3d3",
    "attempts/wave13-computation/n3-45-local-census.json":
        "f0fcbd3457e5b39f56e68492d2a29ae2f45a5deeff99cc30803178d3f3ee2019",
    "attempts/wave13-computation/n3-45-active-local-sat-scan.json":
        "d526bc59b4000a59ff8cc607be89744072a8845763883c8f60af65075bfdd933",
    "attempts/wave13-computation/n3-45-no-common-point-m5-111.json":
        "e32486506a5da0607c0deddaced42ff77f059b39abc3ba29923cd5d056762bb0",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    rendered = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (rendered + "\n").encode("ascii")


def semantic_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def graph_edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise ValueError("loops are not permitted")
    return (left, right) if left < right else (right, left)


def nondecreasing_partitions(
    total: int,
    length: int,
    minimum: int = 2,
) -> Iterable[tuple[int, ...]]:
    """Generate partitions without using the discovery recursion."""

    def extend(
        remaining: int,
        slots: int,
        least: int,
        prefix: tuple[int, ...],
    ) -> Iterable[tuple[int, ...]]:
        if slots == 0:
            if remaining == 0:
                yield prefix
            return
        largest = remaining // slots
        for value in range(least, largest + 1):
            yield from extend(
                remaining - value,
                slots - 1,
                value,
                (*prefix, value),
            )

    yield from extend(total, length, minimum, ())


def reconstruct_profiles() -> tuple[dict[str, object], ...]:
    profiles = []
    for active_order in range(1, 16):
        for q_values in nondecreasing_partitions(30, active_order):
            if not all(3 * q <= active_order - 1 for q in q_values):
                continue
            k_degrees = tuple(active_order - 1 - 3 * q for q in q_values)
            profiles.append(
                {
                    "active_order": active_order,
                    "q_values": q_values,
                    "k_degrees": k_degrees,
                    "passes_three_distinct_nonsingleton_edges":
                        min(k_degrees) >= 3,
                    "passes_frozen_degree_three_obstruction":
                        min(k_degrees) >= 4,
                }
            )
    profiles.sort(
        key=lambda row: (
            -int(row["active_order"]),
            max(row["q_values"]),
            row["q_values"],
        )
    )
    expected = (
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
    assert tuple(row["q_values"] for row in profiles) == expected
    assert sum(
        bool(row["passes_three_distinct_nonsingleton_edges"])
        for row in profiles
    ) == 3
    assert sum(
        bool(row["passes_frozen_degree_three_obstruction"])
        for row in profiles
    ) == 2
    return tuple(profiles)


def flower_reconstruction(
    active_order: int,
    root_size: int,
    largest_petal: int,
    degree_capacity: int,
) -> dict[str, object]:
    """Enumerate disjoint external petal sizes and forced root degrees."""

    outside = active_order - root_size
    feasible = 0
    degree_survivors = 0
    first_feasible: tuple[int, ...] | None = None
    for petals in itertools.product(
        range(2, largest_petal + 1),
        repeat=2 * root_size,
    ):
        if sum(size - 1 for size in petals) > outside:
            continue
        feasible += 1
        if first_feasible is None:
            first_feasible = petals
        singleton_petals = petals.count(2)
        lower_degrees = []
        for occurrence in range(root_size):
            based = petals[2 * occurrence:2 * occurrence + 2]
            lower_degrees.append(
                root_size - 1
                + singleton_petals
                + sum(size - 1 for size in based if size > 2)
            )
        if all(value <= degree_capacity for value in lower_degrees):
            degree_survivors += 1
    return {
        "active_order": active_order,
        "root_size": root_size,
        "largest_petal": largest_petal,
        "outside_capacity": outside,
        "total_words": (largest_petal - 1) ** (2 * root_size),
        "capacity_feasible": feasible,
        "degree_survivors": degree_survivors,
        "first_capacity_feasible": first_feasible,
    }


def rooted_modes(
    active_order: int,
    q_values: Sequence[int],
) -> tuple[dict[str, object], ...]:
    """Re-enumerate every (t,z) root mode from capacity inequalities."""

    if len(q_values) != 3:
        raise ValueError("a rooted size-three point has three occurrences")
    k_degrees = tuple(active_order - 1 - 3 * q for q in q_values)
    fixed_total = 2 * sum(q_values)
    survivors = []
    for t_values in itertools.product((1, 2, 3), repeat=3):
        f_degrees = tuple(3 + t for t in t_values)
        if any(f > k for f, k in zip(f_degrees, k_degrees, strict=True)):
            continue
        if 3 + sum(t_values) > active_order - 3:
            continue
        u_capacity = tuple(
            k - f for k, f in zip(k_degrees, f_degrees, strict=True)
        )
        for z_values in itertools.product(
            *(range(t) for t in t_values)
        ):
            forced_u = tuple(
                sum(
                    3 - t_values[other] + 2 * z_values[other]
                    for other in range(3)
                    if other != occurrence
                )
                for occurrence in range(3)
            )
            if any(
                forced > capacity
                for forced, capacity in zip(
                    forced_u,
                    u_capacity,
                    strict=True,
                )
            ):
                continue
            full_l = sum(
                t_values[index] - 1 - z_values[index]
                for index in range(3)
            )
            if 4 * full_l > fixed_total:
                continue
            survivors.append(
                {
                    "t": t_values,
                    "z": z_values,
                    "u_capacity": u_capacity,
                    "forced_u": forced_u,
                    "full_L_crossings": full_l,
                    "overlap_contribution": 4 * full_l,
                    "remaining_support": fixed_total - 4 * full_l,
                    "external_slots": 3 + sum(t_values),
                }
            )
    return tuple(survivors)


def reconstruct_rooted_mode_results() -> dict[str, object]:
    order15 = rooted_modes(15, (2, 2, 2))
    canonical = Counter(
        tuple(sorted(zip(row["t"], row["z"], strict=True)))
        for row in order15
    )
    expected = {
        ((1, 0), (1, 0), (1, 0)): 1,
        ((1, 0), (2, 0), (2, 0)): 3,
        ((2, 0), (2, 0), (2, 0)): 1,
        ((2, 0), (2, 0), (3, 1)): 3,
    }
    assert dict(canonical) == expected

    # Check all seven q-combinations containing q=3, not merely the
    # one-q=3 case used by the discovery regression.
    mixed_q_results = {
        "".join(map(str, q_values)): len(rooted_modes(14, q_values))
        for q_values in itertools.product((2, 3), repeat=3)
        if 3 in q_values
    }
    assert set(mixed_q_results.values()) == {0}
    q2_order14 = rooted_modes(14, (2, 2, 2))
    assert {
        tuple(row["t"]) for row in q2_order14
    } == {(2, 2, 2)}
    return {
        "order15_ordered_mode_count": len(order15),
        "order15_canonical_histogram": {
            ",".join(f"{t}:{z}" for t, z in key): value
            for key, value in sorted(canonical.items())
        },
        "order14_q3_containing_mode_counts": mixed_q_results,
        "order14_q2_modes": [
            {"t": list(row["t"]), "z": list(row["z"])}
            for row in q2_order14
        ],
    }


def cubic_graph_census(order: int) -> dict[str, object]:
    possible_edges = tuple(itertools.combinations(range(order), 2))
    cubic = []
    triangle_free = []
    for chosen in itertools.combinations(possible_edges, 3 * order // 2):
        degrees = Counter(vertex for item in chosen for vertex in item)
        if any(degrees[vertex] != 3 for vertex in range(order)):
            continue
        edge_set = frozenset(chosen)
        cubic.append(edge_set)
        has_triangle = any(
            all(
                graph_edge(*item) in edge_set
                for item in itertools.combinations(triple, 2)
            )
            for triple in itertools.combinations(range(order), 3)
        )
        if not has_triangle:
            triangle_free.append(edge_set)

    open_twin_free = True
    for graph in triangle_free:
        ordered = tuple(sorted(graph))
        neighborhoods = []
        for index, item in enumerate(ordered):
            neighborhoods.append(
                frozenset(
                    other_index
                    for other_index, other in enumerate(ordered)
                    if other_index != index and set(item) & set(other)
                )
            )
        open_twin_free &= len(set(neighborhoods)) == len(neighborhoods)
    return {
        "order": order,
        "labeled_cubic": len(cubic),
        "labeled_triangle_free_cubic": len(triangle_free),
        "all_triangle_free_line_graphs_open_twin_free": open_twin_free,
    }


def reconstruct_mixed_profile_reduction() -> dict[str, object]:
    flowers = {
        "r15_s5": flower_reconstruction(15, 5, 5, 8),
        "r15_s4": flower_reconstruction(15, 4, 4, 8),
        "r14_s4": flower_reconstruction(14, 4, 4, 7),
    }
    assert {
        key: row["capacity_feasible"] for key, row in flowers.items()
    } == {"r15_s5": 1, "r15_s4": 157, "r14_s4": 45}
    assert all(row["degree_survivors"] == 0 for row in flowers.values())

    # In the nonempty size-three branch, R is cubic with e=3v/2 and
    # e <= 3(12-e), leaving v=4 or 6.
    possible_orders = [
        vertices
        for vertices in range(4, 13, 2)
        if (edges := 3 * vertices // 2) <= 3 * (12 - edges)
    ]
    assert possible_orders == [4, 6]
    graph_censuses = {
        order: cubic_graph_census(order) for order in possible_orders
    }
    assert graph_censuses[4]["labeled_triangle_free_cubic"] == 0
    assert graph_censuses[6]["labeled_triangle_free_cubic"] == 10
    assert graph_censuses[6][
        "all_triangle_free_line_graphs_open_twin_free"
    ]
    return {
        "flowers": flowers,
        "possible_cubic_orders": possible_orders,
        "cubic_graph_censuses": graph_censuses,
        "K33_edge_labels": 9,
        "available_q2_t0_labels": 3,
        "open_twin_injection_contradiction": 9 > 3,
        "all_size2_distance2_endpoint_lower_bound": (6 + 3 - 1) // 3,
        "all_size2_forced_q3_K_degree": 3 + (6 + 3 - 1) // 3,
        "q3_K_degree_capacity": 4,
    }


def reconstruct_incidence_signatures() -> tuple[dict[str, object], ...]:
    signatures = []
    for m in range(1, 16, 2):
        size2 = (45 - 3 * m) // 2
        for type111 in range(m + 1):
            for type122 in range(m - type111 + 1):
                for type222 in range(m - type111 - type122 + 1):
                    type223 = m - type111 - type122 - type222
                    degree1_occurrences = 3 * type111 + type122
                    degree2_occurrences = (
                        2 * type122 + 3 * type222 + 2 * type223
                    )
                    degree3_occurrences = type223
                    if degree2_occurrences % 2:
                        continue
                    if degree3_occurrences % 3:
                        continue
                    label_counts = (
                        degree1_occurrences,
                        degree2_occurrences // 2,
                        degree3_occurrences // 3,
                    )
                    if sum(label_counts) > ORDER:
                        continue
                    signatures.append(
                        {
                            "m": m,
                            "size2": size2,
                            "type_counts": {
                                "111": type111,
                                "122": type122,
                                "222": type222,
                                "223": type223,
                            },
                            "t_label_counts": {
                                "0": ORDER - sum(label_counts),
                                "1": label_counts[0],
                                "2": label_counts[1],
                                "3": label_counts[2],
                            },
                        }
                    )
    histogram = Counter(row["m"] for row in signatures)
    assert histogram == Counter({1: 2, 3: 7, 5: 16, 7: 21, 9: 12, 11: 1})
    assert len(signatures) == 59
    return tuple(signatures)


def minimum_integral_label_use(m: int) -> dict[str, object]:
    """Minimize used t=1,2,3 labels before imposing the order-15 cap."""

    rows = []
    for type111 in range(m + 1):
        for type122 in range(m - type111 + 1):
            for type222 in range(m - type111 - type122 + 1):
                type223 = m - type111 - type122 - type222
                degree1_occurrences = 3 * type111 + type122
                degree2_occurrences = (
                    2 * type122 + 3 * type222 + 2 * type223
                )
                degree3_occurrences = type223
                if degree2_occurrences % 2 or degree3_occurrences % 3:
                    continue
                label_counts = (
                    degree1_occurrences,
                    degree2_occurrences // 2,
                    degree3_occurrences // 3,
                )
                rows.append(
                    {
                        "used_labels": sum(label_counts),
                        "type_counts": {
                            "111": type111,
                            "122": type122,
                            "222": type222,
                            "223": type223,
                        },
                        "t_label_counts": {
                            "1": label_counts[0],
                            "2": label_counts[1],
                            "3": label_counts[2],
                        },
                    }
                )
    minimum = min(row["used_labels"] for row in rows)
    return {
        "m": m,
        "minimum_used_labels": minimum,
        "minimizers": [
            row for row in rows if row["used_labels"] == minimum
        ],
    }


def reconstruct_branch_cover(
    signatures: Sequence[dict[str, object]],
) -> tuple[tuple[int, str], ...]:
    branches = []
    by_m: dict[int, list[dict[str, object]]] = defaultdict(list)
    for signature in signatures:
        by_m[int(signature["m"])].append(signature)
    for m in sorted(by_m):
        modes_present = {
            mode
            for signature in by_m[m]
            for mode, count in signature["type_counts"].items()
            if count
        }
        for mode in MODE_WORDS:
            if mode in modes_present and m >= MODE_MINIMUM_POINTS[mode]:
                branches.append((m, mode))
    assert tuple(branches) == EXPECTED_BRANCHES
    return tuple(branches)


def inspect_scan(path: Path) -> dict[str, object]:
    scan = json.loads(path.read_text(encoding="utf-8"))
    cover = tuple(tuple(item) for item in scan["branch_cover"])
    assert cover == EXPECTED_BRANCHES
    assert scan["branch_count"] == 17 == len(scan["branches"])
    assert all(
        row["status"] == "UNSAT_UNVERIFIED" for row in scan["branches"]
    )
    formula_hashes = [
        row["statistics"]["cnf_sha256"] for row in scan["branches"]
    ]
    assert len(set(formula_hashes)) == 17
    semantic = {
        "schema": scan["schema"],
        "status": scan["status"],
        "branch_cover": scan["branch_cover"],
        "branches": [
            {
                "size3_point_count": row["size3_point_count"],
                "root_mode": row["root_mode"],
                "status": row["status"],
                "variables": row["statistics"]["variables"],
                "clauses": row["statistics"]["clauses"],
                "cnf_sha256": row["statistics"]["cnf_sha256"],
            }
            for row in scan["branches"]
        ],
        "claim_label": scan["claim_label"],
        "target_result": scan["target_result"],
    }
    digest = semantic_sha256(semantic)
    assert digest == scan["semantic_sha256"]
    return {
        "branch_count": len(scan["branches"]),
        "cover": [list(item) for item in cover],
        "all_statuses": sorted({row["status"] for row in scan["branches"]}),
        "distinct_formula_hashes": len(set(formula_hashes)),
        "minimum_variables": min(
            row["statistics"]["variables"] for row in scan["branches"]
        ),
        "maximum_variables": max(
            row["statistics"]["variables"] for row in scan["branches"]
        ),
        "minimum_clauses": min(
            row["statistics"]["clauses"] for row in scan["branches"]
        ),
        "maximum_clauses": max(
            row["statistics"]["clauses"] for row in scan["branches"]
        ),
        "semantic_sha256": digest,
    }


def point_tuple(raw: object) -> tuple[int, ...]:
    if not isinstance(raw, list):
        raise AssertionError("point must be a JSON list")
    point = tuple(raw)
    if any(type(vertex) is not int for vertex in point):
        raise AssertionError("point labels must be integers")
    if tuple(sorted(point)) != point or len(set(point)) != len(point):
        raise AssertionError("point labels must be sorted and distinct")
    if len(point) not in (2, 3):
        raise AssertionError("point size must be two or three")
    if not all(0 <= vertex < ORDER for vertex in point):
        raise AssertionError("point label is outside 0..14")
    return point


def edge_tuple(raw: object) -> tuple[int, int]:
    if not isinstance(raw, list) or len(raw) != 2:
        raise AssertionError("edge must be a two-entry JSON list")
    left, right = raw
    if type(left) is not int or type(right) is not int:
        raise AssertionError("edge labels must be integers")
    if not 0 <= left < right < ORDER:
        raise AssertionError("edges must be sorted within 0..14")
    return left, right


def witness_core_diagnostics(
    points: Sequence[tuple[int, ...]],
    k_edges: frozenset[tuple[int, int]],
) -> dict[str, object]:
    incidence = Counter(vertex for point in points for vertex in point)
    pair_owners: dict[tuple[int, int], list[int]] = defaultdict(list)
    missing_clique_edges = []
    for point_index, point in enumerate(points):
        for item in itertools.combinations(point, 2):
            pair_owners[item].append(point_index)
            if item not in k_edges:
                missing_clique_edges.append((point_index, item))

    degrees = Counter(vertex for item in k_edges for vertex in item)
    berge_certificates = []
    point_set = set(points)
    for triple in itertools.combinations(range(ORDER), 3):
        pair_items = tuple(itertools.combinations(triple, 2))
        if all(pair_owners[item] for item in pair_items) and triple not in point_set:
            berge_certificates.append(
                {
                    "triple": list(triple),
                    "owner_indices": [
                        pair_owners[item][0] for item in pair_items
                    ],
                    "owners": [
                        list(points[pair_owners[item][0]])
                        for item in pair_items
                    ],
                }
            )

    meeting_crossings = 0
    crossing_violations = []
    full_overlaps = []
    full_overlap_degree = Counter()
    for left_index, left in enumerate(points):
        for right_index in range(left_index + 1, len(points)):
            right = points[right_index]
            common = set(left) & set(right)
            if len(common) != 1:
                continue
            meeting_crossings += 1
            base = next(iter(common))
            left_external = [vertex for vertex in left if vertex != base]
            right_external = [vertex for vertex in right if vertex != base]
            l_matrix = [
                [
                    graph_edge(first, second) not in k_edges
                    for second in right_external
                ]
                for first in left_external
            ]
            row_degrees = [sum(row) for row in l_matrix]
            column_degrees = [
                sum(l_matrix[row][column] for row in range(len(l_matrix)))
                for column in range(len(right_external))
            ]
            if any(
                value not in (0, 2)
                for value in (*row_degrees, *column_degrees)
            ):
                crossing_violations.append([left_index, right_index])
            if (
                len(left) == 3
                and len(right) == 3
                and sum(row_degrees) == 4
            ):
                full_overlaps.append([left_index, right_index])
                full_overlap_degree[left_index] += 1
                full_overlap_degree[right_index] += 1

    t_values = tuple(
        sum(len(point) == 3 and vertex in point for point in points)
        for vertex in range(ORDER)
    )
    local_types = Counter(
        "".join(str(t_values[vertex]) for vertex in point)
        if tuple(t_values[vertex] for vertex in point)
        == tuple(sorted(t_values[vertex] for vertex in point))
        else "".join(
            map(str, sorted(t_values[vertex] for vertex in point))
        )
        for point in points
        if len(point) == 3
    )
    size3_indices = [
        index for index, point in enumerate(points) if len(point) == 3
    ]
    return {
        "incidence_degrees": [
            incidence[vertex] for vertex in range(ORDER)
        ],
        "linear_pair_owner_violations": [
            {
                "edge": list(item),
                "owner_indices": owners,
            }
            for item, owners in sorted(pair_owners.items())
            if len(owners) > 1
        ],
        "missing_point_clique_edges": [
            [index, list(item)] for index, item in missing_clique_edges
        ],
        "K_degree_sequence": [
            degrees[vertex] for vertex in range(ORDER)
        ],
        "berge_certificates": berge_certificates,
        "meeting_crossings_checked": meeting_crossings,
        "meeting_crossing_violations": crossing_violations,
        "full_L_overlaps": full_overlaps,
        "maximum_size3_full_L_overlap_degree": max(
            (full_overlap_degree[index] for index in size3_indices),
            default=0,
        ),
        "size3_points_over_fixed_point_cap": sum(
            full_overlap_degree[index] > 3 for index in size3_indices
        ),
        "t_values": list(t_values),
        "t_degree_histogram": {
            str(key): value
            for key, value in sorted(Counter(t_values).items())
        },
        "size3_local_type_histogram": dict(sorted(local_types.items())),
    }


EXPECTED_RESTRICTIONS = [
    "active_labels_only",
    "point_sizes_restricted_to_2_or_3_after_local_proof",
    "one_size3_point_fixed_by_full_label_relabeling",
    "one_of_four_root_modes_fixed_by_its_label_stabilizer",
    "meeting_crossings_and_overlap_fixed_point_upper_bound_only",
    "remaining_fixed_point_support_not_encoded",
    "inactive_vertices_not_encoded",
    "no_complete_99_vertex_adjacency_matrix",
    "no_global_lambda_mu_equalities",
    "diagnostic_variant_no_common_point",
]


def strict_validate_witness(candidate: dict[str, object]) -> dict[str, object]:
    expected_scalars = {
        "schema": "conway99-wave13-n3-45-active-local-diagnostic-v1",
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "variant": "no_common_point",
        "active_order": ORDER,
        "K_degree": K_DEGREE,
        "size3_point_count": 5,
        "root_mode": "111",
        "omitted_premise": "common-point/Berge-triangle prohibition",
    }
    for key, expected in expected_scalars.items():
        if candidate.get(key) != expected:
            raise AssertionError(f"witness metadata mismatch: {key}")
    if candidate.get("q_values") != [2] * ORDER:
        raise AssertionError("q metadata mismatch")
    if candidate.get("restrictions") != EXPECTED_RESTRICTIONS:
        raise AssertionError("restriction boundary mismatch")
    root_metadata = candidate.get("root_normalization")
    if not isinstance(root_metadata, dict):
        raise AssertionError("missing root normalization")
    if root_metadata.get("point") != [0, 1, 2]:
        raise AssertionError("wrong normalized root")
    if root_metadata.get("local_mode") != "111":
        raise AssertionError("wrong normalized mode")
    if root_metadata.get("completed_graph_automorphism_assumed") is not False:
        raise AssertionError("an undeclared completed-graph symmetry appeared")

    raw_points = candidate.get("point_sets")
    raw_edges = candidate.get("K_edges")
    if not isinstance(raw_points, list) or not isinstance(raw_edges, list):
        raise AssertionError("point_sets and K_edges must be lists")
    points = tuple(point_tuple(raw) for raw in raw_points)
    edge_list = tuple(edge_tuple(raw) for raw in raw_edges)
    if len(set(points)) != len(points):
        raise AssertionError("duplicate point")
    if len(set(edge_list)) != len(edge_list):
        raise AssertionError("duplicate K edge")
    k_edges = frozenset(edge_list)
    if ROOT not in {frozenset(point) for point in points}:
        raise AssertionError("normalized root absent")
    if sum(len(point) == 2 for point in points) != 15:
        raise AssertionError("wrong size-two point count")
    if sum(len(point) == 3 for point in points) != 5:
        raise AssertionError("wrong size-three point count")
    if len(k_edges) != ORDER * K_DEGREE // 2:
        raise AssertionError("wrong K edge count")

    diagnostics = witness_core_diagnostics(points, k_edges)
    if diagnostics["incidence_degrees"] != [3] * ORDER:
        raise AssertionError("point incidence is not exactly three")
    if diagnostics["linear_pair_owner_violations"]:
        raise AssertionError("point hypergraph is not linear")
    if diagnostics["missing_point_clique_edges"]:
        raise AssertionError("selected point is not a K-clique")
    if diagnostics["K_degree_sequence"] != [K_DEGREE] * ORDER:
        raise AssertionError("K is not 8-regular")
    if diagnostics["meeting_crossing_violations"]:
        raise AssertionError("meeting crossing rule fails")
    if diagnostics["size3_points_over_fixed_point_cap"]:
        raise AssertionError("overlap cap fails")
    if len(diagnostics["berge_certificates"]) != 18:
        raise AssertionError("expected exactly 18 common-point violations")
    root_t = [
        diagnostics["t_values"][vertex] for vertex in sorted(ROOT)
    ]
    if root_t != [1, 1, 1]:
        raise AssertionError("root mode is not 111")

    archived_diagnostics = candidate.get("diagnostics")
    independently_projected = {
        "point_count": len(points),
        "size2_point_count": sum(len(point) == 2 for point in points),
        "size3_point_count": sum(len(point) == 3 for point in points),
        "incidence_degrees": diagnostics["incidence_degrees"],
        "linear_pair_owner_violations": len(
            diagnostics["linear_pair_owner_violations"]
        ),
        "missing_point_clique_edges": len(
            diagnostics["missing_point_clique_edges"]
        ),
        "K_degree_sequence": diagnostics["K_degree_sequence"],
        "common_point_Berge_triangle_count": len(
            diagnostics["berge_certificates"]
        ),
        "first_common_point_Berge_triangles": [
            row["triple"] for row in diagnostics["berge_certificates"][:10]
        ],
        "meeting_crossing_violations": len(
            diagnostics["meeting_crossing_violations"]
        ),
        "full_L_overlap_count": len(diagnostics["full_L_overlaps"]),
        "maximum_size3_full_L_overlap_degree":
            diagnostics["maximum_size3_full_L_overlap_degree"],
        "size3_points_over_fixed_point_cap":
            diagnostics["size3_points_over_fixed_point_cap"],
        "t_degree_histogram": diagnostics["t_degree_histogram"],
        "size3_local_type_histogram":
            diagnostics["size3_local_type_histogram"],
    }
    if archived_diagnostics != independently_projected:
        raise AssertionError("archived diagnostics do not recompute")

    semantic = {
        "variant": candidate["variant"],
        "point_sets": [list(point) for point in points],
        "K_edges": [list(item) for item in sorted(k_edges)],
        "diagnostics": independently_projected,
    }
    digest = semantic_sha256(semantic)
    if digest != candidate.get("semantic_sha256"):
        raise AssertionError("witness semantic hash mismatch")
    return {
        "point_count": len(points),
        "size2_point_count": 15,
        "size3_point_count": 5,
        "K_edge_count": len(k_edges),
        "meeting_crossings_checked":
            diagnostics["meeting_crossings_checked"],
        "full_L_overlaps": diagnostics["full_L_overlaps"],
        "maximum_size3_full_L_overlap_degree":
            diagnostics["maximum_size3_full_L_overlap_degree"],
        "t_degree_histogram": diagnostics["t_degree_histogram"],
        "size3_local_type_histogram":
            diagnostics["size3_local_type_histogram"],
        "common_point_Berge_triangle_count": 18,
        "berge_certificates": diagnostics["berge_certificates"],
        "semantic_sha256": digest,
    }


def strict_mutation_results(candidate: dict[str, object]) -> dict[str, bool]:
    mutations: dict[str, dict[str, object]] = {}

    removed_edge = copy.deepcopy(candidate)
    removed_edge["K_edges"].pop()
    mutations["remove_K_edge"] = removed_edge

    duplicate_edge = copy.deepcopy(candidate)
    duplicate_edge["K_edges"].append(copy.deepcopy(duplicate_edge["K_edges"][0]))
    mutations["duplicate_K_edge"] = duplicate_edge

    metadata = copy.deepcopy(candidate)
    metadata["root_mode"] = "223"
    metadata["size3_point_count"] = 11
    metadata["active_order"] = 99
    mutations["forge_unhashed_metadata"] = metadata

    inflated = copy.deepcopy(candidate)
    inflated["claim_label"] = "VERIFIED"
    mutations["inflate_status"] = inflated

    altered_diagnostics = copy.deepcopy(candidate)
    altered_diagnostics["diagnostics"]["common_point_Berge_triangle_count"] = 17
    mutations["alter_diagnostic_count"] = altered_diagnostics

    results = {}
    for name, value in mutations.items():
        try:
            strict_validate_witness(value)
        except (AssertionError, KeyError, TypeError, ValueError):
            results[name] = True
        else:
            results[name] = False
    assert all(results.values())
    return results


def inventory_inputs(repository: Path) -> dict[str, str]:
    observed = {
        relative: sha256_file(repository / Path(relative))
        for relative in EXPECTED_INPUT_HASHES
    }
    assert observed == EXPECTED_INPUT_HASHES
    return observed


def audit(repository: Path) -> dict[str, object]:
    input_hashes = inventory_inputs(repository)
    profiles = reconstruct_profiles()
    local_modes = reconstruct_rooted_mode_results()
    mixed_reduction = reconstruct_mixed_profile_reduction()
    signatures = reconstruct_incidence_signatures()
    branch_cover = reconstruct_branch_cover(signatures)
    scan = inspect_scan(
        repository
        / "attempts"
        / "wave13-computation"
        / "n3-45-active-local-sat-scan.json"
    )
    candidate = json.loads(
        (
            repository
            / "attempts"
            / "wave13-computation"
            / "n3-45-no-common-point-m5-111.json"
        ).read_text(encoding="utf-8")
    )
    witness = strict_validate_witness(candidate)
    mutation_results = strict_mutation_results(candidate)
    large_m_minima = {
        str(m): minimum_integral_label_use(m) for m in (13, 15)
    }
    assert large_m_minima["13"]["minimum_used_labels"] == 18
    assert large_m_minima["15"]["minimum_used_labels"] == 20
    return {
        "input_hashes": input_hashes,
        "profiles": [
            {
                **row,
                "q_values": list(row["q_values"]),
                "k_degrees": list(row["k_degrees"]),
            }
            for row in profiles
        ],
        "profile_count": len(profiles),
        "profiles_after_degree_filter": sum(
            bool(row["passes_three_distinct_nonsingleton_edges"])
            for row in profiles
        ),
        "profiles_after_frozen_degree_three_obstruction": sum(
            bool(row["passes_frozen_degree_three_obstruction"])
            for row in profiles
        ),
        "local_modes": local_modes,
        "mixed_profile_reduction": mixed_reduction,
        "incidence_signature_count": len(signatures),
        "incidence_signature_histogram": {
            str(key): value
            for key, value in sorted(
                Counter(row["m"] for row in signatures).items()
            )
        },
        "m11_signature": [
            row for row in signatures if row["m"] == 11
        ],
        "m13_signature_count": sum(row["m"] == 13 for row in signatures),
        "m15_signature_count": sum(row["m"] == 15 for row in signatures),
        "m13_m15_minimum_integral_label_use": large_m_minima,
        "mode_minimum_points": MODE_MINIMUM_POINTS,
        "branch_cover": [list(item) for item in branch_cover],
        "scan": scan,
        "witness": witness,
        "strict_mutations_rejected": mutation_results,
        "solver_conclusion": "UNSAT_UNVERIFIED",
        "target_result": "UNKNOWN",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    result = audit(arguments.repository.resolve())
    if arguments.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS independent Wave 13 arithmetic/witness reconstruction")
        print("profiles", result["profile_count"])
        print("incidence_signatures", result["incidence_signature_count"])
        print("branches", len(result["branch_cover"]))
        print(
            "berge_violations",
            result["witness"]["common_point_Berge_triangle_count"],
        )
        print("solver_conclusion", result["solver_conclusion"])
        print("target_result", result["target_result"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
