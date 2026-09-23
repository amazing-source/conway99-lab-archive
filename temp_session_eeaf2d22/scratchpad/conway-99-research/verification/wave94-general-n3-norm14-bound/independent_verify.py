#!/usr/bin/env python3
"""Clean-room verifier for the Wave 94 prism-sensitive norm-14 bound.

This module imports no discovery code.  It reconstructs the finite rooted
incidences, the triangular-prism multiplicity, the complementary-Fano seed
map, and all integer arithmetic from definitions.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave94-general-n3-norm14-bound"

V = 99
K = 14
LAMBDA = 1
MU = 2
POSITIVE_RESTRICTED_EIGENVALUE = 3
BASE = tuple(range(14))
MATE_PAIRS = tuple((2 * group, 2 * group + 1) for group in range(7))

EXPECTED_DEPENDENCIES = {
    "verification/wave64-rooted-transition-design/package-manifest.sha256":
        "dd138310fcaa4e3e2d2989281f9c7487b498ad1d15901403b32919d7018bb905",
    "verification/wave71-modular-theta-extension/package-manifest.sha256":
        "0eede2ebc625534360dda3f8e62456e582f5184fd18d3820dd44748de95a5237",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hash_manifest(path: Path) -> dict[str, str]:
    pattern = re.compile(r"^([0-9a-f]{64}) [ *](.+)$")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        match = pattern.fullmatch(line)
        if not match:
            raise AssertionError(f"{path}:{line_number}: malformed manifest line")
        digest, relative = match.groups()
        if relative in entries:
            raise AssertionError(f"{path}:{line_number}: duplicate path {relative}")
        entries[relative] = digest
    return entries


def frozen_inventory() -> tuple[dict[str, str], dict[str, tuple[int, str]]]:
    lines = (HERE / "input-inventory.tsv").read_text(
        encoding="utf-8"
    ).splitlines()
    metadata: dict[str, str] = {}
    files: dict[str, tuple[int, str]] = {}
    in_files = False
    for line in lines:
        if not line:
            continue
        fields = line.split("\t")
        if fields == ["path", "size_bytes", "sha256"]:
            in_files = True
            continue
        if in_files:
            if len(fields) != 3:
                raise AssertionError(f"malformed inventory row: {line!r}")
            relative, size, digest = fields
            if relative in files:
                raise AssertionError(f"duplicate inventory path: {relative}")
            files[relative] = (int(size), digest)
        else:
            if len(fields) != 2:
                raise AssertionError(f"malformed metadata row: {line!r}")
            metadata[fields[0]] = fields[1]
    return metadata, files


def verify_frozen_inputs() -> dict[str, object]:
    metadata, expected_files = frozen_inventory()
    actual_paths = {
        path.relative_to(DISCOVERY).as_posix()
        for path in DISCOVERY.rglob("*")
        if path.is_file()
    }
    failures: list[str] = []
    if actual_paths != set(expected_files):
        failures.append("discovery file inventory changed")
    for relative, (expected_size, expected_hash) in expected_files.items():
        path = DISCOVERY / relative
        if not path.is_file():
            failures.append(f"missing {relative}")
            continue
        if path.stat().st_size != expected_size:
            failures.append(f"size mismatch {relative}")
        if sha256(path) != expected_hash:
            failures.append(f"hash mismatch {relative}")

    manifest_path = DISCOVERY / "package-manifest.sha256"
    manifest = parse_hash_manifest(manifest_path)
    expected_manifest_paths = {
        f"attempts/wave94-general-n3-norm14-bound/{relative}"
        for relative in actual_paths
        if relative != "package-manifest.sha256"
    }
    if set(manifest) != expected_manifest_paths:
        failures.append("discovery manifest coverage mismatch")
    for relative, expected_hash in manifest.items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected_hash:
            failures.append(f"discovery manifest mismatch {relative}")

    dependency_checks = {}
    for relative, expected_hash in EXPECTED_DEPENDENCIES.items():
        path = ROOT / relative
        actual_hash = sha256(path) if path.is_file() else None
        dependency_checks[relative] = {
            "expected_sha256": expected_hash,
            "actual_sha256": actual_hash,
            "passed": actual_hash == expected_hash,
        }
        if actual_hash != expected_hash:
            failures.append(f"dependency manifest mismatch {relative}")

    return {
        "passed": not failures,
        "failures": failures,
        "frozen_utc": metadata["frozen_utc"],
        "frozen_git_commit": metadata["git_commit"],
        "discovery_files": len(expected_files),
        "discovery_manifest_entries": len(manifest),
        "package_manifest_sha256": sha256(manifest_path),
        "dependency_manifests": dependency_checks,
    }


def group(point: int) -> int:
    return point // 2


def mate(point: int) -> int:
    return point ^ 1


def seeds() -> tuple[tuple[int, int, int, int], ...]:
    return tuple(
        seed
        for seed in itertools.combinations(BASE, 4)
        if len({group(point) for point in seed}) == 4
    )


SEEDS = seeds()
SEED_SETS = tuple(frozenset(seed) for seed in SEEDS)


def transition_candidates() -> tuple[tuple[int, int, int], ...]:
    rows = []
    for common in BASE:
        endpoints = [
            point for point in BASE if group(point) != group(common)
        ]
        for left, right in itertools.combinations(endpoints, 2):
            rows.append((common, left, right))
    return tuple(rows)


TRANSITION_CANDIDATES = transition_candidates()


def transition_seed_multiplicity(transition: tuple[int, int, int]) -> int:
    support = frozenset(transition)
    return sum(support <= seed for seed in SEED_SETS)


@lru_cache(maxsize=None)
def perfect_matchings(
    points: tuple[int, ...],
) -> tuple[tuple[tuple[int, int], ...], ...]:
    if not points:
        return ((),)
    first = points[0]
    result = []
    for index in range(1, len(points)):
        second = points[index]
        remaining = points[1:index] + points[index + 1 :]
        pair = (min(first, second), max(first, second))
        for tail in perfect_matchings(remaining):
            result.append((pair,) + tail)
    return tuple(result)


LOCAL_ABSTRACT_POINTS = tuple(range(12))
LOCAL_MATCHINGS = perfect_matchings(LOCAL_ABSTRACT_POINTS)


def forbidden_pairs_in_local_matching(
    matching: tuple[tuple[int, int], ...],
) -> int:
    return sum(mate(left) == right for left, right in matching)


def local_matching_census() -> dict[str, object]:
    census = Counter(
        forbidden_pairs_in_local_matching(matching)
        for matching in LOCAL_MATCHINGS
    )
    local_seed_subsets = tuple(
        subset
        for subset in itertools.combinations(LOCAL_ABSTRACT_POINTS, 3)
        if len({group(point) for point in subset}) == 3
    )
    maximum = 0
    for matching in LOCAL_MATCHINGS:
        pair_sets = tuple(frozenset(pair) for pair in matching)
        for subset in local_seed_subsets:
            subset_set = frozenset(subset)
            maximum = max(
                maximum,
                sum(pair <= subset_set for pair in pair_sets),
            )
    return {
        "perfect_matchings_on_twelve": len(LOCAL_MATCHINGS),
        "forbidden_pair_count_census": {
            str(key): value for key, value in sorted(census.items())
        },
        "three_endpoint_seed_sections": len(local_seed_subsets),
        "maximum_selected_pairs_in_one_local_seed_section": maximum,
        "cap_is_sharp_locally": maximum == 1,
    }


def abstract_to_base_point(common: int, abstract: int) -> int:
    remaining_groups = [
        candidate for candidate in range(7) if candidate != group(common)
    ]
    return 2 * remaining_groups[group(abstract)] + abstract % 2


def first_matching_with_forbidden_count(
    forbidden_count: int,
) -> tuple[tuple[int, int], ...]:
    return next(
        matching
        for matching in LOCAL_MATCHINGS
        if forbidden_pairs_in_local_matching(matching) == forbidden_count
    )


def selection_from_profile(
    profile: Iterable[int],
) -> tuple[tuple[int, int, int], ...]:
    transitions = []
    values = tuple(profile)
    if len(values) != len(BASE):
        raise ValueError("one local forbidden-pair count is required per base")
    for common, forbidden_count in zip(BASE, values):
        local = first_matching_with_forbidden_count(forbidden_count)
        for abstract_left, abstract_right in local:
            left = abstract_to_base_point(common, abstract_left)
            right = abstract_to_base_point(common, abstract_right)
            transitions.append((common, min(left, right), max(left, right)))
    return tuple(transitions)


def validate_selected_transitions(
    transitions: Iterable[tuple[int, int, int]],
) -> tuple[tuple[int, int, int], ...]:
    rows = tuple(transitions)
    if len(rows) != 84 or len(set(rows)) != 84:
        raise ValueError("selected transitions must contain 84 distinct rows")
    for common in BASE:
        local = [row for row in rows if row[0] == common]
        if len(local) != 6:
            raise ValueError("every base point must select six transitions")
        endpoints = [point for _, left, right in local for point in (left, right)]
        expected = [
            point for point in BASE if group(point) != group(common)
        ]
        if sorted(endpoints) != expected:
            raise ValueError("local transitions must perfectly match 12 labels")
    return rows


def analyze_selected_transitions(
    transitions: Iterable[tuple[int, int, int]],
) -> dict[str, object]:
    rows = validate_selected_transitions(transitions)
    forbidden = sum(mate(left) == right for _, left, right in rows)
    multiplicity_sum = sum(
        transition_seed_multiplicity(row) for row in rows
    )
    seed_loads = [
        sum(frozenset(row) <= seed for row in rows)
        for seed in SEED_SETS
    ]
    bad = sum(load > 0 for load in seed_loads)
    free = len(SEEDS) - bad
    return {
        "f": forbidden,
        "transition_seed_incidences": multiplicity_sum,
        "expected_transition_seed_incidences": 8 * (84 - forbidden),
        "maximum_seed_load": max(seed_loads),
        "bad_seeds": bad,
        "transition_free_seeds": free,
        "bad_seed_lower_bound": 168 - 2 * forbidden,
        "transition_free_seed_upper_bound": 392 + 2 * forbidden,
        "passed": (
            multiplicity_sum == 8 * (84 - forbidden)
            and max(seed_loads) <= 4
            and bad >= 168 - 2 * forbidden
            and free <= 392 + 2 * forbidden
        ),
    }


def selection_saturating_seed(
    seed: tuple[int, int, int, int],
) -> tuple[tuple[int, int, int], ...]:
    seed_set = set(seed)
    transitions = []
    for common in BASE:
        endpoints = [
            point for point in BASE if group(point) != group(common)
        ]
        pairs: list[tuple[int, int]] = []
        if common in seed_set:
            inside = sorted(seed_set - {common})
            first_pair = (inside[0], inside[1])
            pairs.append(first_pair)
            remaining = [
                point for point in endpoints if point not in first_pair
            ]
        else:
            remaining = endpoints
        while remaining:
            first = remaining.pop(0)
            second = remaining.pop(0)
            pairs.append((first, second))
        for left, right in pairs:
            transitions.append((common, min(left, right), max(left, right)))
    return validate_selected_transitions(transitions)


def edge(left: int, right: int) -> frozenset[int]:
    return frozenset((left, right))


def two_triangle_graph(cross_edges: int) -> frozenset[frozenset[int]]:
    if not 0 <= cross_edges <= 3:
        raise ValueError("cross_edges must be between zero and three")
    first = (0, 1, 2)
    second = (3, 4, 5)
    edges = {
        edge(left, right)
        for triangle in (first, second)
        for left, right in itertools.combinations(triangle, 2)
    }
    edges.update(edge(index, index + 3) for index in range(cross_edges))
    return frozenset(edges)


def induced_c4_count(edges: frozenset[frozenset[int]]) -> int:
    total = 0
    for vertices in itertools.combinations(range(6), 4):
        degrees = {
            vertex: sum(
                edge(vertex, other) in edges
                for other in vertices
                if other != vertex
            )
            for vertex in vertices
        }
        if set(degrees.values()) == {2}:
            total += 1
    return total


def rooted_prism_transitions() -> dict[int, tuple[int, int, int, int, int]]:
    edges = two_triangle_graph(3)
    partner = {index: index + 3 for index in range(3)}
    partner.update({index + 3: index for index in range(3)})
    triangles = ({0, 1, 2}, {3, 4, 5})
    result = {}
    for root in range(6):
        own = next(triangle for triangle in triangles if root in triangle)
        mate_vertices = sorted(own - {root})
        left, right = mate_vertices
        opposite = partner[root]
        left_residual = partner[left]
        right_residual = partner[right]
        required = {
            edge(root, left),
            edge(root, right),
            edge(left, right),
            edge(opposite, left_residual),
            edge(opposite, right_residual),
            edge(left_residual, right_residual),
            edge(root, opposite),
            edge(left, left_residual),
            edge(right, right_residual),
        }
        if required != set(edges):
            raise AssertionError("rooted prism reconstruction lost an edge")
        result[root] = (
            opposite,
            left,
            right,
            left_residual,
            right_residual,
        )
    return result


def prism_identity() -> dict[str, object]:
    graph_edges = V * K // 2
    graph_nonedges = math.comb(V, 2) - graph_edges
    # Every nonedge has exactly two common neighbors; lambda=1 makes those
    # neighbors nonadjacent.  Each induced C4 has two opposite nonedges.
    induced_c4s = graph_nonedges * math.comb(MU, 2) // 2
    rooted = rooted_prism_transitions()
    shape_counts = {
        str(cross): induced_c4_count(two_triangle_graph(cross))
        for cross in range(4)
    }
    return {
        "P_definition": (
            "number of induced six-vertex triangular prisms: two disjoint "
            "triangles joined by all three matching cross edges"
        ),
        "n3_definition": (
            "number of induced six-vertex configurations consisting of two "
            "disjoint triangles joined by exactly two matching cross edges"
        ),
        "graph_edges": graph_edges,
        "graph_nonedges": graph_nonedges,
        "induced_C4_count": induced_c4s,
        "two_times_induced_C4_count": 2 * induced_c4s,
        "C4_count_by_cross_matching_size": shape_counts,
        "rooted_transitions_in_one_prism": len(rooted),
        "global_identity": "n3+3P=4158",
        "proof_summary": (
            "Each induced C4 has two pairs of opposite edges. Completing "
            "each edge to its unique triangle gives an n3 configuration or "
            "a prism. Conversely an n3 configuration contains one such C4 "
            "and a prism contains three. A prism has six roots and the "
            "rooted opposite vertex is unique, so sum_o f_o=6P."
        ),
        "passed": (
            induced_c4s == 2079
            and shape_counts == {"0": 0, "1": 0, "2": 1, "3": 3}
            and len(rooted) == 6
        ),
    }


def fano_complement_blocks() -> tuple[frozenset[int], ...]:
    points = frozenset(range(1, 8))
    lines = {
        frozenset((left, right, left ^ right))
        for left, right in itertools.combinations(points, 2)
    }
    return tuple(sorted((points - line for line in lines), key=lambda x: tuple(x)))


def norm14_seed_map() -> dict[str, object]:
    blocks = fano_complement_blocks()
    point_degrees = Counter(point for block in blocks for point in block)
    pair_degrees = Counter(
        pair
        for block in blocks
        for pair in itertools.combinations(sorted(block), 2)
    )
    root_block = blocks[0]
    intersections = [
        frozenset(block & root_block)
        for block in blocks
        if block != root_block
    ]
    expected_pairs = {
        frozenset(pair)
        for pair in itertools.combinations(sorted(root_block), 2)
    }

    support_size = 14
    spectral_numerator = (
        POSITIVE_RESTRICTED_EIGENVALUE * support_size * V
        + (K - POSITIVE_RESTRICTED_EIGENVALUE)
        * support_size
        * support_size
    )
    spectral_edge_upper = spectral_numerator // (2 * V)
    pair_capacity = MU * math.comb(7, 2)
    design_pair_incidences = 7 * math.comb(4, 2)
    return {
        "unit_sign_class_sizes": [7, 7],
        "support_edge_formula": "e(P union N)=28+4h",
        "support_spectral_edge_upper": spectral_edge_upper,
        "same_sign_edges_forced": 0,
        "cross_degree": 4,
        "complementary_Fano_blocks": len(blocks),
        "point_degrees": sorted(point_degrees.values()),
        "pair_degrees": sorted(pair_degrees.values()),
        "root_block_size": len(root_block),
        "other_block_intersections_with_root": sorted(
            len(intersection) for intersection in intersections
        ),
        "root_pair_saturation": set(intersections) == expected_pairs,
        "common_neighbor_pair_capacity": pair_capacity,
        "design_pair_incidences": design_pair_incidences,
        "seed_injection": (
            "For positive root o, Q=NcapN(o) is a four-point seed. Each "
            "pair in Q has exactly the common positive vertices o and its "
            "unique rooted residual label, recovering all of P. The 42 "
            "N-to-pairs-of-P incidences saturate the 42 SRG common-neighbor "
            "slots, so every vertex outside N meets P at most once; hence N "
            "is recovered as the vertices with four neighbors in P."
        ),
        "transition_free": (
            "A selected transition supported by three points of Q would "
            "join two recovered positive residual labels, contradicting "
            "the forced independence of P."
        ),
        "passed": (
            len(blocks) == 7
            and set(point_degrees.values()) == {4}
            and set(pair_degrees.values()) == {2}
            and set(intersections) == expected_pairs
            and spectral_edge_upper == 31
            and 28 + 4 > spectral_edge_upper
            and pair_capacity == design_pair_incidences == 42
        ),
    }


def finite_seed_census() -> dict[str, object]:
    mate_rows = [
        row for row in TRANSITION_CANDIDATES if mate(row[1]) == row[2]
    ]
    nonmate_rows = [
        row for row in TRANSITION_CANDIDATES if mate(row[1]) != row[2]
    ]
    mate_multiplicities = {
        transition_seed_multiplicity(row) for row in mate_rows
    }
    nonmate_multiplicities = {
        transition_seed_multiplicity(row) for row in nonmate_rows
    }

    matching = local_matching_census()
    profiles = [
        [forbidden] * 14
        for forbidden in sorted(
            int(value)
            for value in matching["forbidden_pair_count_census"]
        )
    ]
    profiles.append([0, 1, 2, 3, 4, 6, 0, 1, 2, 3, 4, 6, 0, 1])
    profile_checks = [
        analyze_selected_transitions(selection_from_profile(profile))
        for profile in profiles
    ]
    saturated = analyze_selected_transitions(
        selection_saturating_seed(SEEDS[0])
    )
    return {
        "seed_count": len(SEEDS),
        "candidate_transition_count": len(TRANSITION_CANDIDATES),
        "mate_forbidden_candidate_count": len(mate_rows),
        "nonmate_candidate_count": len(nonmate_rows),
        "mate_transition_seed_multiplicities": sorted(mate_multiplicities),
        "nonmate_transition_seed_multiplicities": sorted(
            nonmate_multiplicities
        ),
        "local_matching_exhaustion": matching,
        "selected_transition_profile_checks": profile_checks,
        "global_seed_load_cap": 4,
        "cap_four_is_attained": saturated["maximum_seed_load"] == 4,
        "incidence_argument": (
            "There are 8(84-f_o) transition-seed incidences. A seed has "
            "three incident labels at each of its four base points, and a "
            "local matching selects at most one pair among three, so its "
            "load is at most four. Therefore at least 168-2f_o seeds are "
            "bad and at most 392+2f_o are transition-free."
        ),
        "passed": (
            len(SEEDS) == math.comb(7, 4) * 2**4 == 560
            and len(TRANSITION_CANDIDATES) == 14 * math.comb(12, 2)
            and len(mate_rows) == 84
            and len(nonmate_rows) == 840
            and mate_multiplicities == {0}
            and nonmate_multiplicities == {8}
            and matching[
                "maximum_selected_pairs_in_one_local_seed_section"
            ] == 1
            and all(row["passed"] for row in profile_checks)
            and saturated["maximum_seed_load"] == 4
            and saturated["passed"]
        ),
    }


def bound_from_prisms(prisms: int) -> int:
    if not 0 <= prisms <= 1386:
        raise ValueError("P is outside the nonnegative identity domain")
    return (38808 + 12 * prisms) // 7


def bound_from_n3(n3: int) -> int:
    if not 0 <= n3 <= 4158:
        raise ValueError("n3 is outside the nonnegative identity domain")
    if (4158 - n3) % 3:
        raise ValueError("n3 is incompatible with integral P")
    return (55440 - 4 * n3) // 7


def global_arithmetic() -> dict[str, object]:
    rows = []
    for prisms in range(1387):
        n3 = 4158 - 3 * prisms
        by_prisms = bound_from_prisms(prisms)
        by_n3 = bound_from_n3(n3)
        if by_prisms != by_n3:
            raise AssertionError("P and n3 formulas disagree")
        rows.append((n3, prisms, by_prisms))

    endpoints = {
        str(n3): {
            "P": (4158 - n3) // 3,
            "N14_upper": bound_from_n3(n3),
            "numerator_mod_7": (55440 - 4 * n3) % 7,
        }
        for n3 in (4158, 4155, 708, 0)
    }

    # One unoriented sign-pair consists of two vectors t and -t.  Each has
    # seven positive entries, so its contribution is 14=7*2, not 7 or 28.
    positive_roots_per_oriented_vector = [
        sum(value > 0 for value in vector)
        for vector in (
            (1,) * 7 + (-1,) * 7,
            (-1,) * 7 + (1,) * 7,
        )
    ]
    return {
        "root_bound": "a14(o)<=392+2f_o",
        "rooted_prism_sum": "sum_o f_o=6P",
        "orientation_identity": "sum_o a14(o)=7N14",
        "N14_counts_both_signs": True,
        "positive_roots_in_test_sign_pair": positive_roots_per_oriented_vector,
        "test_sign_pair_total": sum(positive_roots_per_oriented_vector),
        "global_inequality": "7N14<=38808+12P",
        "P_bound": "N14<=floor((38808+12P)/7)",
        "n3_bound": "N14<=floor((55440-4n3)/7)",
        "full_identity_domain_rows_checked": len(rows),
        "endpoint_rows": endpoints,
        "bound_step_sizes_as_P_increases": sorted(
            {right[2] - left[2] for left, right in zip(rows, rows[1:])}
        ),
        "passed": (
            V * 392 == 38808
            and 2 * 6 == 12
            and 38808 + 4 * 4158 == 55440
            and positive_roots_per_oriented_vector == [7, 7]
            and sum(positive_roots_per_oriented_vector) == 7 * 2
            and len(rows) == 1387
            and endpoints["4158"]["N14_upper"] == 5544
            and endpoints["4155"]["N14_upper"] == 5545
            and endpoints["708"]["N14_upper"] == 7515
            and endpoints["0"]["N14_upper"] == 7920
        ),
    }


def compare_discovery(independent: dict[str, object]) -> dict[str, object]:
    discovery = json.loads(
        (DISCOVERY / "exact-results.json").read_text(encoding="utf-8")
    )
    expected_endpoints = [
        {
            "n3": int(n3),
            "P": row["P"],
            "N14_upper_bound": row["N14_upper"],
        }
        for n3, row in independent["components"]["global_arithmetic"][
            "endpoint_rows"
        ].items()
    ]
    expected_endpoints.sort(
        key=lambda row: (4158, 4155, 708, 0).index(row["n3"])
    )
    checks = {
        "seed_count": discovery["finite_census"]["seed_count"] == 560,
        "transition_counts": (
            discovery["finite_census"]["mate_forbidden_candidate_rows"] == 84
            and discovery["finite_census"]["nonmate_candidate_rows"] == 840
        ),
        "multiplicities": (
            discovery["finite_census"][
                "mate_transition_seed_multiplicity"
            ] == 0
            and discovery["finite_census"][
                "nonmate_transition_seed_multiplicity"
            ] == 8
        ),
        "cap": (
            discovery["finite_census"][
                "selected_transitions_per_seed_cap"
            ] == 4
        ),
        "rooted_prism_identity": (
            discovery["prism_multiplicity"]["global_identity"]
            == "sum_o f_o=6P"
        ),
        "bounds": discovery["bound"]
        == {
            "oriented_root_inequality": "a14(o)<=392+2*f_o",
            "global_inequality": "7*N14<=38808+12P",
            "P_form": "N14<=floor((38808+12P)/7)",
            "n3_form": "N14<=floor((55440-4*n3)/7)",
        },
        "endpoints": discovery["boundary_rows"] == expected_endpoints,
        "scope": (
            discovery["scope"]["N14_counts_both_signs"] is True
            and discovery["scope"]["requires_prism_free_endpoint"] is False
            and discovery["scope"]["requires_rank_28"] is False
        ),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "discovery_claim_label": discovery["claim_label"],
        "comparison_scope": (
            "Post-reconstruction comparison only; discovery code was not "
            "imported or used to derive the independent result."
        ),
    }


def build_results() -> dict[str, object]:
    input_integrity = verify_frozen_inputs()
    identity = prism_identity()
    seed_map = norm14_seed_map()
    census = finite_seed_census()
    arithmetic = global_arithmetic()
    components = {
        "input_integrity": input_integrity,
        "prism_and_n3_identity": identity,
        "norm14_seed_map": seed_map,
        "finite_seed_census": census,
        "global_arithmetic": arithmetic,
    }
    passed = all(component["passed"] for component in components.values())
    result: dict[str, object] = {
        "format": "wave94-general-n3-norm14-independent-verifier-v1",
        "role": "verifier",
        "claim_label": "VERIFIED" if passed else "REFUTED",
        "verdict": "VERIFIED" if passed else "REFUTED",
        "conditional_scope": "hypothetical srg(99,14,1,2)",
        "components": components,
        "theorem": (
            "N14 <= floor((38808+12P)/7) "
            "= floor((55440-4*n3)/7)"
        ),
        "assumptions": [
            "N14 counts both t and -t as distinct nonzero eigenvectors.",
            "P counts induced triangular prisms.",
            "n3 counts the two-cross-edge two-triangle configuration.",
            "No prism-free, rank-28, or automorphism hypothesis is imposed.",
        ],
        "limitations": [
            "This bounds the norm-14 shell only.",
            "No upper bound on N16 or N18 follows.",
            "No strict upper bound on n3 or Conway-99 resolution follows.",
            "Literature novelty remains UNKNOWN.",
        ],
        "status": {
            "N16_upper_bound": None,
            "N18_upper_bound": None,
            "strict_n3_upper_bound": None,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }
    comparison = compare_discovery(result)
    result["discovery_comparison"] = comparison
    if not comparison["passed"]:
        result["claim_label"] = "REFUTED"
        result["verdict"] = "REFUTED"
    return result


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    encoded = canonical_bytes(build_results())
    if args.output:
        args.output.write_bytes(encoded)
        print(f"WROTE {args.output} sha256={sha256(args.output)}")
    elif args.verify:
        if args.verify.read_bytes() != encoded:
            raise SystemExit(f"verification mismatch: {args.verify}")
        print(f"VERIFIED {args.verify} sha256={sha256(args.verify)}")
    else:
        print(encoded.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
