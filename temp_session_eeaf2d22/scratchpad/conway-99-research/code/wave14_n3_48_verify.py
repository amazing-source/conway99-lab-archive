#!/usr/bin/env python3
"""Independent standard-library validation for Wave 14 positive artifacts.

This checker deliberately does not import the profile or SAT discovery
modules.  It validates finite positive active-local objects and integrity
metadata.  It does not turn any negative solver return into evidence.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


TARGET_N3 = 48
PROFILE_Q_VALUES = {
    "r16-q2x16": (2,) * 16,
    "r15-q2x13-q3x2": (2,) * 13 + (3,) * 2,
    "r14-q2x10-q3x4": (2,) * 10 + (3,) * 4,
}
FULL = "full"
NO_COMMON_POINT_CONTROL = "no_common_point_control"
K_DEGREE_UPPER_CONTROL = "k_degree_upper_control"
VARIANTS = (FULL, NO_COMMON_POINT_CONTROL, K_DEGREE_UPPER_CONTROL)

ENCODED_PREMISES = [
    "exactly three selected non-singleton point sets through each active label",
    "point sizes are two or three after the finite flower reductions",
    "point-family linearity",
    "F is the exact union of selected point-clique edges",
    "every selected point is a clique in K",
    "common-point/Berge-triangle rule unless named as the omitted control premise",
    "exact two-sided degree-{0,2} crossing for every pair of meeting selected points",
    "fixed-point upper cap on full-L overlaps at every selected size-three point",
    "profile-specific K degrees, or only upper bounds in the named control",
]

UNENCODED_PREMISES = [
    "inactive point sets and inactive graph vertices",
    "which disjoint active point sets represent adjacent original vertices",
    "fixed support contributed by disjoint point sets",
    "equality completion of every fixed-point support sum",
    "the 693-vertex H graph",
    "a 99-vertex adjacency matrix",
    "global SRG lambda/mu equations",
]


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def edge(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise AssertionError("loop in edge list")
    return (left, right) if left < right else (right, left)


def all_edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


def vertex_degrees(
    order: int, graph_edges: Iterable[tuple[int, int]]
) -> tuple[int, ...]:
    output = [0] * order
    for left, right in graph_edges:
        output[left] += 1
        output[right] += 1
    return tuple(output)


def expected_branch(
    q_values: Sequence[int], branch_id: str
) -> dict[str, object]:
    q_values = tuple(q_values)
    q2_count = q_values.count(2)
    q3_count = q_values.count(3)
    if branch_id == "no-size3":
        return {
            "branch_id": branch_id,
            "root_q3_count": None,
            "root_point": None,
            "normalization": (
                "no label symmetry is fixed; every size-three point is absent"
            ),
        }
    if not branch_id.startswith("root-q3x"):
        raise AssertionError("unknown branch id")
    special_count = int(branch_id.removeprefix("root-q3x"))
    if not 0 <= special_count <= min(3, q3_count):
        raise AssertionError("root special multiplicity is out of range")
    ordinary_count = 3 - special_count
    root = tuple(
        (*range(ordinary_count), *range(q2_count, q2_count + special_count))
    )
    return {
        "branch_id": branch_id,
        "root_q3_count": special_count,
        "root_point": list(root),
        "root_q_values": sorted(q_values[vertex] for vertex in root),
        "normalization": (
            "choose one selected triple with this q-composition and map it "
            "to the displayed labels using only permutations within equal-q classes"
        ),
    }


def independent_diagnostics(
    q_values: Sequence[int],
    points: Sequence[frozenset[int]],
    k_edges: frozenset[tuple[int, int]],
) -> dict[str, object]:
    q_values = tuple(q_values)
    order = len(q_values)
    incidence = [0] * order
    pair_owners: dict[tuple[int, int], list[int]] = {
        item: [] for item in all_edges(order)
    }
    missing_clique_edges = []
    for index, point in enumerate(points):
        for vertex in point:
            incidence[vertex] += 1
        for item in itertools.combinations(sorted(point), 2):
            pair_owners[item].append(index)
            if item not in k_edges:
                missing_clique_edges.append(item)

    point_set = set(points)
    berge_triangles = []
    for triple in itertools.combinations(range(order), 3):
        pairs = tuple(itertools.combinations(triple, 2))
        if all(pair_owners[item] for item in pairs):
            if frozenset(triple) not in point_set:
                berge_triangles.append(list(triple))

    crossing_violations = []
    full_overlaps = []
    full_overlap_degrees: Counter[frozenset[int]] = Counter()
    meeting_count = 0
    for left_index, left in enumerate(points):
        for right in points[left_index + 1 :]:
            intersection = left & right
            if len(intersection) != 1:
                continue
            meeting_count += 1
            common = next(iter(intersection))
            left_external = tuple(sorted(left - {common}))
            right_external = tuple(sorted(right - {common}))
            matrix = tuple(
                tuple(
                    edge(first, second) not in k_edges
                    for second in right_external
                )
                for first in left_external
            )
            row_degrees = [sum(row) for row in matrix]
            column_degrees = [
                sum(
                    matrix[row][column]
                    for row in range(len(left_external))
                )
                for column in range(len(right_external))
            ]
            if any(
                value not in (0, 2)
                for value in (*row_degrees, *column_degrees)
            ):
                crossing_violations.append(
                    {
                        "left": sorted(left),
                        "right": sorted(right),
                        "row_degrees": row_degrees,
                        "column_degrees": column_degrees,
                    }
                )
            if (
                len(left) == len(right) == 3
                and sum(row_degrees) == 4
            ):
                full_overlap_degrees[left] += 1
                full_overlap_degrees[right] += 1
                full_overlaps.append([sorted(left), sorted(right)])

    overlap_cap_violations = []
    for point in points:
        if len(point) != 3:
            continue
        cap = sum(q_values[vertex] for vertex in point) // 2
        observed = full_overlap_degrees[point]
        if observed > cap:
            overlap_cap_violations.append(
                {
                    "point": sorted(point),
                    "observed": observed,
                    "cap": cap,
                }
            )

    t_values = tuple(
        sum(len(point) == 3 and vertex in point for point in points)
        for vertex in range(order)
    )
    local_types = Counter(
        (
            tuple(sorted(q_values[vertex] for vertex in point)),
            tuple(sorted(t_values[vertex] for vertex in point)),
        )
        for point in points
        if len(point) == 3
    )
    f_edges = tuple(
        item for item, owners in pair_owners.items() if owners
    )
    return {
        "point_count": len(points),
        "size2_point_count": sum(len(point) == 2 for point in points),
        "size3_point_count": sum(len(point) == 3 for point in points),
        "incidence_degrees": incidence,
        "linear_pair_owner_violations": sum(
            len(owners) > 1 for owners in pair_owners.values()
        ),
        "f_edge_count": len(f_edges),
        "missing_point_clique_edges": [
            list(item) for item in sorted(set(missing_clique_edges))
        ],
        "k_edge_count": len(k_edges),
        "k_degree_sequence": list(vertex_degrees(order, k_edges)),
        "common_point_Berge_triangle_count": len(berge_triangles),
        "common_point_Berge_triangles": berge_triangles,
        "meeting_crossings_checked": meeting_count,
        "meeting_crossing_violation_count": len(crossing_violations),
        "meeting_crossing_violations": crossing_violations,
        "full_L_overlap_count": len(full_overlaps),
        "full_L_overlaps": full_overlaps,
        "overlap_cap_violation_count": len(overlap_cap_violations),
        "overlap_cap_violations": overlap_cap_violations,
        "t_values": list(t_values),
        "size3_local_q_t_histogram": {
            (
                "q"
                + "".join(map(str, q_type))
                + "-t"
                + "".join(map(str, t_type))
            ): multiplicity
            for (q_type, t_type), multiplicity in sorted(local_types.items())
        },
        "point_index_checksum": sha256_bytes(
            canonical_json_bytes(
                [[index, sorted(point)] for index, point in enumerate(points)]
            )
        ),
    }


def validate_candidate_object(candidate: dict[str, object]) -> dict[str, object]:
    if candidate.get("schema") != (
        "conway99-wave14-n3-48-active-local-candidate-v1"
    ):
        raise AssertionError("candidate schema mismatch")
    if candidate.get("claim_label") != "CANDIDATE":
        raise AssertionError("candidate claim status inflation")
    if candidate.get("target_result") != "UNKNOWN":
        raise AssertionError("candidate target status inflation")
    if candidate.get("novelty") != "UNKNOWN":
        raise AssertionError("candidate novelty status inflation")
    if candidate.get("target_n3") != TARGET_N3:
        raise AssertionError("wrong conditional n3 boundary")
    if candidate.get("scope") != "active-label auxiliary object only":
        raise AssertionError("candidate scope changed")
    if candidate.get("encoded_premises") != ENCODED_PREMISES:
        raise AssertionError("encoded premise list changed")
    if candidate.get("unencoded_premises") != UNENCODED_PREMISES:
        raise AssertionError("unencoded premise list changed")

    profile_name = candidate.get("profile_id")
    if profile_name not in PROFILE_Q_VALUES:
        raise AssertionError("unknown profile")
    q_values = PROFILE_Q_VALUES[str(profile_name)]
    order = len(q_values)
    degree_targets = tuple(order - 1 - 3 * q for q in q_values)
    if candidate.get("active_order") != order:
        raise AssertionError("active order mismatch")
    if candidate.get("q_values") != list(q_values):
        raise AssertionError("q profile mismatch")
    if candidate.get("k_degree_targets") != list(degree_targets):
        raise AssertionError("K-degree targets mismatch")

    variant = candidate.get("variant")
    if variant not in VARIANTS:
        raise AssertionError("unknown variant")
    expected_omitted = {
        FULL: None,
        NO_COMMON_POINT_CONTROL: "common-point/Berge-triangle rule",
        K_DEGREE_UPPER_CONTROL: "exact K-degree equality",
    }[str(variant)]
    if candidate.get("omitted_premise") != expected_omitted:
        raise AssertionError("omitted premise metadata mismatch")

    raw_points = candidate.get("point_sets")
    if not isinstance(raw_points, list):
        raise AssertionError("point_sets must be a list")
    if any(
        not isinstance(raw, list)
        or raw != sorted(raw)
        or len(raw) not in (2, 3)
        for raw in raw_points
    ):
        raise AssertionError("point record is not canonical")
    if raw_points != sorted(raw_points, key=lambda item: (len(item), item)):
        raise AssertionError("point list order is not canonical")
    points = tuple(frozenset(map(int, raw)) for raw in raw_points)
    if len(points) != len(set(points)):
        raise AssertionError("duplicate selected point")
    if any(
        not point <= frozenset(range(order)) for point in points
    ):
        raise AssertionError("point label out of range")

    raw_k_edges = candidate.get("K_edges")
    if not isinstance(raw_k_edges, list):
        raise AssertionError("K_edges must be a list")
    if any(
        not isinstance(raw, list)
        or len(raw) != 2
        or raw != sorted(raw)
        for raw in raw_k_edges
    ):
        raise AssertionError("K-edge record is not canonical")
    if raw_k_edges != sorted(raw_k_edges):
        raise AssertionError("K-edge list order is not canonical")
    k_edge_records = tuple(edge(*map(int, raw)) for raw in raw_k_edges)
    if len(k_edge_records) != len(set(k_edge_records)):
        raise AssertionError("duplicate K edge")
    if any(
        not 0 <= left < right < order for left, right in k_edge_records
    ):
        raise AssertionError("K-edge label out of range")
    k_edges = frozenset(k_edge_records)

    branch = candidate.get("branch")
    if not isinstance(branch, dict):
        raise AssertionError("branch metadata missing")
    branch_id = branch.get("branch_id")
    expected = expected_branch(q_values, str(branch_id))
    if branch != expected:
        raise AssertionError("branch normalization metadata mismatch")
    if branch_id == "no-size3":
        if any(len(point) == 3 for point in points):
            raise AssertionError("no-size3 branch contains a triple")
    else:
        root = frozenset(map(int, expected["root_point"]))
        if root not in points:
            raise AssertionError("normalized root is not selected")

    observed = independent_diagnostics(q_values, points, k_edges)
    if observed != candidate.get("diagnostics"):
        raise AssertionError("diagnostic replay mismatch")
    if observed["incidence_degrees"] != [3] * order:
        raise AssertionError("point incidence is not three")
    if observed["linear_pair_owner_violations"]:
        raise AssertionError("point family is not linear")
    if observed["missing_point_clique_edges"]:
        raise AssertionError("selected point is not a K-clique")
    if observed["meeting_crossing_violation_count"]:
        raise AssertionError("meeting crossing rule fails")
    if observed["overlap_cap_violation_count"]:
        raise AssertionError("fixed-point overlap cap fails")

    degrees = observed["k_degree_sequence"]
    if variant in (FULL, NO_COMMON_POINT_CONTROL):
        if degrees != list(degree_targets):
            raise AssertionError("K-degree equality fails")
    else:
        if any(
            observed_degree > target
            for observed_degree, target in zip(
                degrees, degree_targets, strict=True
            )
        ):
            raise AssertionError("K upper-degree control exceeds a target")
        if degrees[0] >= degree_targets[0]:
            raise AssertionError("K upper-degree control did not violate equality")

    berge_count = observed["common_point_Berge_triangle_count"]
    if variant == NO_COMMON_POINT_CONTROL:
        if berge_count < 1:
            raise AssertionError("common-point control has no real violation")
    elif berge_count:
        raise AssertionError("common-point rule fails")

    core = {
        "profile_id": profile_name,
        "q_values": list(q_values),
        "branch": expected,
        "variant": variant,
        "point_sets": raw_points,
        "K_edges": raw_k_edges,
    }
    if candidate.get("semantic_core") != core:
        raise AssertionError("semantic core mismatch")
    digest = sha256_bytes(canonical_json_bytes(core))
    if candidate.get("semantic_sha256") != digest:
        raise AssertionError("semantic digest mismatch")
    formula = candidate.get("formula")
    if not isinstance(formula, dict):
        raise AssertionError("formula metadata missing")
    cnf_hash = formula.get("materialized_dimacs_sha256")
    if not isinstance(cnf_hash, str) or len(cnf_hash) != 64:
        raise AssertionError("formula hash malformed")
    return {
        "status": "PASS",
        "profile_id": profile_name,
        "branch_id": branch_id,
        "variant": variant,
        "point_count": len(points),
        "size3_point_count": observed["size3_point_count"],
        "k_edge_count": len(k_edges),
        "common_point_Berge_triangle_count": berge_count,
        "semantic_sha256": digest,
        "formula_sha256": cnf_hash,
        "target_result": "UNKNOWN",
    }


def active_profiles_independent() -> tuple[tuple[int, ...], ...]:
    output = []

    def visit(remaining: int, least: int, values: tuple[int, ...]) -> None:
        if remaining == 0:
            order = len(values)
            if values and all(3 * value <= order - 1 for value in values):
                output.append(values)
            return
        for value in range(least, remaining + 1):
            visit(remaining - value, value, (*values, value))

    visit(32, 2, ())
    return tuple(sorted(output, key=lambda row: (-len(row), row)))


def independent_flower_count(
    active_order: int,
    root_size: int,
    maximum_petal_size: int,
    root_degree: int,
) -> tuple[int, int]:
    capacity_count = 0
    degree_count = 0
    for word in itertools.product(
        range(2, maximum_petal_size + 1), repeat=2 * root_size
    ):
        if sum(value - 1 for value in word) > active_order - root_size:
            continue
        capacity_count += 1
        singletons = word.count(2)
        lower = tuple(
            root_size
            - 1
            + singletons
            + sum(
                value - 1
                for value in word[2 * root : 2 * root + 2]
                if value > 2
            )
            for root in range(root_size)
        )
        if max(lower) <= root_degree:
            degree_count += 1
    return capacity_count, degree_count


def independent_local_state_count(
    active_order: int, root_q_values: Sequence[int]
) -> int:
    degrees = tuple(
        active_order - 1 - 3 * value for value in root_q_values
    )
    count = 0
    for t_values in itertools.product((1, 2, 3), repeat=3):
        if 3 + sum(t_values) > active_order - 3:
            continue
        u_capacities = tuple(
            degree - 3 - t
            for degree, t in zip(degrees, t_values, strict=True)
        )
        if min(u_capacities) < 0:
            continue
        for empty_counts in itertools.product(
            *(range(t) for t in t_values)
        ):
            forced = tuple(
                sum(
                    3 - t_values[j] + 2 * empty_counts[j]
                    for j in range(3)
                    if j != i
                )
                for i in range(3)
            )
            full = sum(
                t - 1 - empty
                for t, empty in zip(
                    t_values, empty_counts, strict=True
                )
            )
            if all(
                forced[i] <= u_capacities[i] for i in range(3)
            ) and 4 * full <= 2 * sum(root_q_values):
                count += 1
    return count


def validate_profile_census(path: Path) -> dict[str, object]:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema") != "conway99-wave14-n3-48-profile-census-v1":
        raise AssertionError("profile schema mismatch")
    if report.get("claim_label") != "CANDIDATE":
        raise AssertionError("profile claim status inflation")
    if report.get("target_result") != "UNKNOWN":
        raise AssertionError("profile target status inflation")
    if report.get("novelty") != "UNKNOWN":
        raise AssertionError("profile novelty status inflation")
    semantic = report.get("semantic")
    if report.get("semantic_sha256") != sha256_bytes(
        canonical_json_bytes(semantic)
    ):
        raise AssertionError("profile semantic digest mismatch")
    profiles = active_profiles_independent()
    raw_rows = semantic["raw_profiles"]
    if [tuple(row["q_values"]) for row in raw_rows] != list(profiles):
        raise AssertionError("raw profile census mismatch")
    for row in raw_rows:
        q_values = tuple(row["q_values"])
        degrees = tuple(len(q_values) - 1 - 3 * q for q in q_values)
        if row["k_degrees"] != list(degrees):
            raise AssertionError("profile degree conversion mismatch")
        if row["survives_three_non_singleton_points"] != (
            min(degrees) >= 3
        ):
            raise AssertionError("non-singleton degree filter mismatch")
        if row["survives_verified_degree_three_obstruction"] != (
            min(degrees) >= 4
        ):
            raise AssertionError("degree-three filter mismatch")
    if semantic["surviving_profiles"] != list(PROFILE_Q_VALUES):
        raise AssertionError("surviving profile order mismatch")

    independent_flower_results = {
        "r16-size5": independent_flower_count(16, 5, 5, 9),
        "r16-size4": independent_flower_count(16, 4, 4, 9),
        "r15-size5": independent_flower_count(15, 5, 5, 8),
        "r15-size4": independent_flower_count(15, 4, 4, 8),
        "r14-size4": independent_flower_count(14, 4, 4, 7),
    }
    expected_degree_survivors = {
        "r16-size5": 0,
        "r16-size4": 16,
        "r15-size5": 0,
        "r15-size4": 0,
        "r14-size4": 0,
    }
    for key, (_, survivors) in independent_flower_results.items():
        if survivors != expected_degree_survivors[key]:
            raise AssertionError(f"independent flower count changed for {key}")
    reductions = semantic["point_size_reductions"]
    if reductions["r16-q2x16"]["size4_crossing_check"][
        "two_sided_crossing_rejections"
    ] != 16:
        raise AssertionError("order-16 crossing rejection count mismatch")
    if not reductions["r16-q2x16"]["size4_crossing_check"][
        "all_rejected"
    ]:
        raise AssertionError("order-16 size-four words not all rejected")

    local_expected = {
        (16, (2, 2, 2)): 32,
        (15, (2, 2, 2)): 8,
        (15, (2, 2, 3)): 0,
        (15, (2, 3, 3)): 0,
        (14, (2, 2, 2)): 1,
        (14, (2, 2, 3)): 0,
        (14, (2, 3, 3)): 0,
        (14, (3, 3, 3)): 0,
    }
    observed_local = {}
    for profile_modes in semantic["local_size3_mode_census"]:
        order = profile_modes["active_order"]
        for row in profile_modes["root_compositions"]:
            root = tuple(row["root_q_values"])
            independent = independent_local_state_count(order, root)
            if row["labeled_state_count"] != independent:
                raise AssertionError("local state census mismatch")
            observed_local[(order, root)] = independent
    if observed_local != local_expected:
        raise AssertionError("local state table changed")
    if len(semantic["sat_branch_cover"]) != 11:
        raise AssertionError("branch cover size mismatch")
    reduced = [
        (row["profile_id"], row["branch_id"])
        for row in semantic["finite_branch_reduction"]
        if row["survives_finite_reductions"]
    ]
    expected_reduced = [
        ("r16-q2x16", "no-size3"),
        ("r16-q2x16", "root-q3x0"),
        ("r15-q2x13-q3x2", "root-q3x0"),
        ("r14-q2x10-q3x4", "root-q3x0"),
    ]
    if reduced != expected_reduced:
        raise AssertionError("post-finite branch cover mismatch")
    if [
        (row["profile_id"], row["branch_id"])
        for row in semantic["post_finite_surviving_branches"]
    ] != expected_reduced:
        raise AssertionError("post-finite branch summary mismatch")
    return {
        "status": "PASS",
        "raw_profile_count": len(profiles),
        "surviving_profile_count": len(PROFILE_Q_VALUES),
        "post_finite_branch_count": len(reduced),
        "independent_flower_results": {
            key: list(value)
            for key, value in independent_flower_results.items()
        },
        "independent_local_state_counts": {
            f"r{key[0]}-q{''.join(map(str, key[1]))}": value
            for key, value in sorted(local_expected.items())
        },
        "semantic_sha256": report["semantic_sha256"],
        "file_sha256": file_sha256(path),
        "target_result": "UNKNOWN",
    }


def expected_raw_cover() -> list[tuple[str, str]]:
    return [
        ("r16-q2x16", "no-size3"),
        ("r16-q2x16", "root-q3x0"),
        ("r15-q2x13-q3x2", "no-size3"),
        ("r15-q2x13-q3x2", "root-q3x0"),
        ("r15-q2x13-q3x2", "root-q3x1"),
        ("r15-q2x13-q3x2", "root-q3x2"),
        ("r14-q2x10-q3x4", "no-size3"),
        ("r14-q2x10-q3x4", "root-q3x0"),
        ("r14-q2x10-q3x4", "root-q3x1"),
        ("r14-q2x10-q3x4", "root-q3x2"),
        ("r14-q2x10-q3x4", "root-q3x3"),
    ]


def validate_scan(path: Path) -> dict[str, object]:
    scan = json.loads(path.read_text(encoding="utf-8"))
    if scan.get("schema") != (
        "conway99-wave14-n3-48-active-local-scan-v1"
    ):
        raise AssertionError("scan schema mismatch")
    if scan.get("claim_label") != "CANDIDATE":
        raise AssertionError("scan claim status inflation")
    if scan.get("target_result") != "UNKNOWN":
        raise AssertionError("scan target status inflation")
    if scan.get("novelty") != "UNKNOWN":
        raise AssertionError("scan novelty status inflation")
    if scan.get("encoded_premises") != ENCODED_PREMISES:
        raise AssertionError("scan encoded premises changed")
    if scan.get("unencoded_premises") != UNENCODED_PREMISES:
        raise AssertionError("scan unencoded premises changed")
    semantic = scan.get("semantic")
    if scan.get("semantic_sha256") != sha256_bytes(
        canonical_json_bytes(semantic)
    ):
        raise AssertionError("scan semantic digest mismatch")
    results = scan.get("results")
    observed_cover = [
        (row["profile_id"], row["branch"]["branch_id"]) for row in results
    ]
    if observed_cover != expected_raw_cover():
        raise AssertionError("scan branch cover mismatch")
    allowed_statuses = {
        "SAT_CANDIDATE",
        "UNSAT_UNVERIFIED",
        "BUDGET_UNKNOWN",
        "TIMEOUT_UNKNOWN",
    }
    validated_candidates = []
    for row in results:
        if row.get("status") not in allowed_statuses:
            raise AssertionError("scan status vocabulary changed")
        solver = row.get("solver", {})
        if solver.get("proof_trace_emitted") is not False:
            raise AssertionError("scan unexpectedly claims a proof trace")
        if solver.get("proof_trace_checked") is not False:
            raise AssertionError("scan unexpectedly claims proof checking")
        if row["status"] != "SAT_CANDIDATE":
            if row.get("evidentiary_status") != (
                "NON_EVIDENTIARY_NO_CHECKED_PROOF_TRACE"
            ):
                raise AssertionError("negative status was inflated")
        else:
            candidate_path = Path(row["candidate_path"])
            candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
            validation = validate_candidate_object(candidate)
            if (
                validation["semantic_sha256"]
                != row["candidate_semantic_sha256"]
            ):
                raise AssertionError("scan/candidate digest mismatch")
            validated_candidates.append(validation)
    semantic_projection = [
        {
            "profile_id": row["profile_id"],
            "branch_id": row["branch"]["branch_id"],
            "status": row["status"],
            "formula_sha256": row["formula"][
                "materialized_dimacs_sha256"
            ],
            "candidate_semantic_sha256": row.get(
                "candidate_semantic_sha256"
            ),
        }
        for row in results
    ]
    if semantic["results"] != semantic_projection:
        raise AssertionError("scan semantic projection mismatch")
    return {
        "status": "PASS",
        "branch_count": len(results),
        "status_histogram": dict(
            sorted(Counter(row["status"] for row in results).items())
        ),
        "validated_positive_candidates": validated_candidates,
        "semantic_sha256": scan["semantic_sha256"],
        "file_sha256": file_sha256(path),
        "negative_results_evidentiary": False,
        "target_result": "UNKNOWN",
    }


def validate_controls(path: Path) -> dict[str, object]:
    controls = json.loads(path.read_text(encoding="utf-8"))
    if controls.get("schema") != (
        "conway99-wave14-n3-48-positive-controls-v1"
    ):
        raise AssertionError("control schema mismatch")
    if controls.get("claim_label") != "CANDIDATE":
        raise AssertionError("control claim status inflation")
    if controls.get("target_result") != "UNKNOWN":
        raise AssertionError("control target status inflation")
    semantic = controls.get("semantic")
    if controls.get("semantic_sha256") != sha256_bytes(
        canonical_json_bytes(semantic)
    ):
        raise AssertionError("control semantic digest mismatch")
    validations = []
    for row in controls.get("results", []):
        if row.get("status") != "SAT_CANDIDATE":
            raise AssertionError("positive control did not produce a model")
        candidate_path = Path(row["candidate_path"])
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        validation = validate_candidate_object(candidate)
        if validation["variant"] == FULL:
            raise AssertionError("control candidate is not weakened")
        validations.append(validation)
    if {row["variant"] for row in validations} != {
        NO_COMMON_POINT_CONTROL,
        K_DEGREE_UPPER_CONTROL,
    }:
        raise AssertionError("both named positive controls are required")
    return {
        "status": "PASS",
        "control_count": len(validations),
        "validated_controls": validations,
        "semantic_sha256": controls["semantic_sha256"],
        "file_sha256": file_sha256(path),
        "target_result": "UNKNOWN",
    }


def mutation_checks(candidate: dict[str, object]) -> dict[str, object]:
    mutations = {}

    def must_reject(name: str, mutated: dict[str, object]) -> None:
        try:
            validate_candidate_object(mutated)
        except (AssertionError, KeyError, TypeError, ValueError) as error:
            mutations[name] = {
                "result": "REJECTED",
                "reason": str(error),
            }
        else:
            raise AssertionError(f"hostile mutation {name} was accepted")

    changed = copy.deepcopy(candidate)
    changed["claim_label"] = "VERIFIED"
    must_reject("claim_status_inflation", changed)

    changed = copy.deepcopy(candidate)
    changed["target_result"] = "NONEXISTENT"
    must_reject("target_status_inflation", changed)

    changed = copy.deepcopy(candidate)
    changed["K_edges"].append(copy.deepcopy(changed["K_edges"][0]))
    must_reject("duplicate_K_edge", changed)

    changed = copy.deepcopy(candidate)
    changed["K_edges"].pop()
    must_reject("deleted_K_edge", changed)

    changed = copy.deepcopy(candidate)
    changed["point_sets"].append(copy.deepcopy(changed["point_sets"][0]))
    must_reject("duplicate_point", changed)

    changed = copy.deepcopy(candidate)
    changed["branch"]["normalization"] = "assume a completed automorphism"
    must_reject("forged_normalization", changed)

    changed = copy.deepcopy(candidate)
    changed["diagnostics"]["k_edge_count"] += 1
    must_reject("forged_diagnostic", changed)

    changed = copy.deepcopy(candidate)
    changed["q_values"][0] = 3
    must_reject("altered_q_profile", changed)

    changed = copy.deepcopy(candidate)
    changed["semantic_sha256"] = "0" * 64
    must_reject("forged_semantic_digest", changed)
    return {
        "status": "PASS",
        "mutation_count": len(mutations),
        "mutations": mutations,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profiles",
        type=Path,
        default=Path(
            "attempts/wave14-computation/n3-48-profile-census.json"
        ),
    )
    parser.add_argument(
        "--scan",
        type=Path,
        default=Path(
            "attempts/wave14-computation/n3-48-active-local-scan.json"
        ),
    )
    parser.add_argument(
        "--controls",
        type=Path,
        default=Path(
            "attempts/wave14-computation/n3-48-positive-controls.json"
        ),
    )
    parser.add_argument(
        "--mutation-candidate",
        type=Path,
        default=Path(
            "attempts/wave14-computation/"
            "n3-48-r16-q2x16-no-size3-full-candidate.json"
        ),
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile_validation = validate_profile_census(args.profiles)
    scan_validation = validate_scan(args.scan)
    control_validation = validate_controls(args.controls)
    mutation_candidate = json.loads(
        args.mutation_candidate.read_text(encoding="utf-8")
    )
    mutations = mutation_checks(mutation_candidate)
    semantic = {
        "profile_semantic_sha256": profile_validation["semantic_sha256"],
        "scan_semantic_sha256": scan_validation["semantic_sha256"],
        "control_semantic_sha256": control_validation["semantic_sha256"],
        "validated_candidate_semantic_sha256": [
            row["semantic_sha256"]
            for row in scan_validation["validated_positive_candidates"]
        ],
        "validated_control_semantic_sha256": [
            row["semantic_sha256"]
            for row in control_validation["validated_controls"]
        ],
        "mutation_count": mutations["mutation_count"],
    }
    output = {
        "schema": "conway99-wave14-n3-48-independent-validation-v1",
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty": "UNKNOWN",
        "profile_validation": profile_validation,
        "scan_validation": scan_validation,
        "control_validation": control_validation,
        "mutation_validation": mutations,
        "negative_solver_results_evidentiary": False,
        "semantic": semantic,
        "semantic_sha256": sha256_bytes(canonical_json_bytes(semantic)),
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(output, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
