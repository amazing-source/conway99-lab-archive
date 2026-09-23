#!/usr/bin/env python3
"""Exact Wave 53 multi-root coherent-lift experiment.

The objects here are forced CSP templates around two distinguished graph
triangles in each nonidentity relation K, B, C, and D.  Unresolved B/C
relations remain Boolean-choice nodes; no completion is selected before WL
refinement.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path
from typing import Iterable, Sequence


RELATION_ORDER = ("K", "B", "C", "D")
COMMON_K_NEIGHBORS = {"K": 5, "B": 2, "C": 1, "D": 0}
MEMORY_FLOOR_PERCENT = 20.0
SECTORS = range(3)
LOCAL_ROOTS = ("R", "S")
ROOT_PAIR = ("R", "S")


class MemoryStatus(ctypes.Structure):
    _fields_ = (
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_physical", ctypes.c_ulonglong),
        ("available_physical", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("available_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("available_virtual", ctypes.c_ulonglong),
        ("available_extended_virtual", ctypes.c_ulonglong),
    )


def free_physical_memory_percent() -> float:
    if sys.platform != "win32":
        return 100.0
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.available_physical / status.total_physical


def enforce_memory_floor() -> float:
    free_percent = free_physical_memory_percent()
    if free_percent < MEMORY_FLOOR_PERCENT:
        raise MemoryError(
            f"free physical memory {free_percent:.2f}% is below "
            f"{MEMORY_FLOOR_PERCENT:.2f}%"
        )
    return free_percent


def pair_key(left: str, right: str) -> tuple[str, str]:
    if left == right:
        raise ValueError("unordered pair requires distinct endpoints")
    return tuple(sorted((left, right)))


def candidate_label(key: tuple[str, str]) -> str:
    return f"v::{key[0]}::{key[1]}"


@dataclass
class Geometry:
    relation: str
    sectors: dict[str, list[list[str]]]
    triangle_nodes: list[str]
    common_petals: list[str]


@dataclass
class Template:
    geometry: Geometry
    nodes: list[str]
    tokens: list[list[str]]
    triangle_relations: dict[tuple[str, str], str]
    candidate_contexts: dict[
        tuple[str, str], list[tuple[str, int, int]]
    ]
    cap_candidates: dict[str, tuple[tuple[str, str], ...]]
    cap_owners: dict[str, str]
    forced_true: set[tuple[str, str]]


def _unique_fill(root: str, sector: int, count: int) -> list[str]:
    return [f"{root.lower()}_{sector}_{index}" for index in range(count)]


def build_geometry(relation: str) -> Geometry:
    """Build the canonical naming of the forced two-root overlap.

    The names choose coordinates on the two root triangles only.  They do not
    assert an automorphism of a completed graph.
    """

    if relation not in RELATION_ORDER:
        raise ValueError(f"unknown root relation {relation!r}")

    sectors = {root: [[] for _ in SECTORS] for root in LOCAL_ROOTS}
    common_count = COMMON_K_NEIGHBORS[relation]
    common_petals = [f"h{index}" for index in range(common_count)]

    if relation == "K":
        sectors["R"][0] = ["S", *common_petals]
        sectors["S"][0] = ["R", *common_petals]
        for root in LOCAL_ROOTS:
            sectors[root][1] = _unique_fill(root, 1, 6)
            sectors[root][2] = _unique_fill(root, 2, 6)
    else:
        placements = []
        if relation in ("C", "B"):
            placements.append((0, "h0"))
        if relation == "B":
            placements.append((1, "h1"))
        for root in LOCAL_ROOTS:
            for sector in SECTORS:
                shared = [name for placed, name in placements if placed == sector]
                sectors[root][sector] = [
                    *shared,
                    *_unique_fill(root, sector, 6 - len(shared)),
                ]

    triangle_nodes = sorted(
        {"R", "S"}
        | {
            node
            for root in LOCAL_ROOTS
            for sector in sectors[root]
            for node in sector
        }
    )
    geometry = Geometry(
        relation=relation,
        sectors=sectors,
        triangle_nodes=triangle_nodes,
        common_petals=common_petals,
    )
    validate_geometry(geometry)
    return geometry


def validate_geometry(geometry: Geometry) -> dict[str, object]:
    relation = geometry.relation
    if relation not in RELATION_ORDER:
        raise AssertionError("invalid relation")
    for root in LOCAL_ROOTS:
        if len(geometry.sectors[root]) != 3:
            raise AssertionError("each root must have three sectors")
        flattened = []
        for sector in geometry.sectors[root]:
            if len(sector) != 6 or len(set(sector)) != 6:
                raise AssertionError("each root sector must contain six triangles")
            flattened.extend(sector)
        if len(set(flattened)) != 18:
            raise AssertionError("a root must have eighteen distinct K-neighbors")
        if root in flattened:
            raise AssertionError("a root cannot be its own K-neighbor")

    r_petals = {
        node for sector in geometry.sectors["R"] for node in sector
    }
    s_petals = {
        node for sector in geometry.sectors["S"] for node in sector
    }
    overlap = sorted(r_petals & s_petals)
    expected_overlap = COMMON_K_NEIGHBORS[relation]
    if len(overlap) != expected_overlap:
        raise AssertionError(
            f"{relation} has {len(overlap)} common K-neighbors, "
            f"expected {expected_overlap}"
        )
    if relation == "K":
        if "S" not in r_petals or "R" not in s_petals:
            raise AssertionError("K-related roots must occur in opposite petal sets")
        if overlap != geometry.common_petals:
            raise AssertionError("bad five-triangle K overlap")
    else:
        if "S" in r_petals or "R" in s_petals:
            raise AssertionError("disjoint roots cannot occur in opposite petal sets")
        if overlap != geometry.common_petals:
            raise AssertionError("bad cross-edge common-neighbor overlap")

    if relation == "B":
        r_locations = {
            node: sector_index
            for sector_index, sector in enumerate(geometry.sectors["R"])
            for node in sector
            if node in geometry.common_petals
        }
        s_locations = {
            node: sector_index
            for sector_index, sector in enumerate(geometry.sectors["S"])
            for node in sector
            if node in geometry.common_petals
        }
        if (
            len(set(r_locations.values())) != 2
            or len(set(s_locations.values())) != 2
        ):
            raise AssertionError("B cross edges must use distinct root vertices")

    expected_orders = {"K": 31, "B": 36, "C": 37, "D": 38}
    if len(geometry.triangle_nodes) != expected_orders[relation]:
        raise AssertionError("unexpected two-root triangle-core order")
    return {
        "triangle_core_order": len(geometry.triangle_nodes),
        "common_K_neighbor_count": len(overlap),
        "each_root_has_3K6": True,
        "B_cross_edges_form_a_matching": relation != "B" or True,
    }


def build_triangle_relations(
    geometry: Geometry,
) -> dict[tuple[str, str], str]:
    relations: dict[tuple[str, str], str] = {}

    def set_relation(left: str, right: str, value: str) -> None:
        key = pair_key(left, right)
        old = relations.get(key)
        if old is not None and old != value:
            raise AssertionError(
                f"inconsistent forced relation for {key}: {old} versus {value}"
            )
        relations[key] = value

    set_relation("R", "S", geometry.relation)
    for root in LOCAL_ROOTS:
        for sector in geometry.sectors[root]:
            for node in sector:
                set_relation(root, node, "K")
            for left, right in combinations(sector, 2):
                set_relation(left, right, "K")
        for left_sector, right_sector in combinations(SECTORS, 2):
            for left in geometry.sectors[root][left_sector]:
                for right in geometry.sectors[root][right_sector]:
                    key = pair_key(left, right)
                    old = relations.get(key)
                    if old is not None and old != "U_BC":
                        raise AssertionError(
                            f"cross-sector pair {key} already forced {old}"
                        )
                    relations[key] = "U_BC"

    if geometry.relation == "B":
        shared_pair = pair_key("h0", "h1")
        if relations.get(shared_pair) != "U_BC":
            raise AssertionError("the two B-root common petals must be cross-sector")
        # T_0 and T_1 already have the two root-triangle edges as cross edges.
        # A third cross edge would be the forbidden prism, so their relation is B.
        relations[shared_pair] = "B"
    return relations


def build_template(relation: str) -> Template:
    geometry = build_geometry(relation)
    triangle_relations = build_triangle_relations(geometry)
    candidate_contexts: dict[
        tuple[str, str], list[tuple[str, int, int]]
    ] = defaultdict(list)
    cap_candidates: dict[str, tuple[tuple[str, str], ...]] = {}
    cap_owners: dict[str, str] = {}

    for root in LOCAL_ROOTS:
        for left_sector, right_sector in combinations(SECTORS, 2):
            for left in geometry.sectors[root][left_sector]:
                for right in geometry.sectors[root][right_sector]:
                    candidate_contexts[pair_key(left, right)].append(
                        (root, left_sector, right_sector)
                    )
        for owner_sector in SECTORS:
            for target_sector in SECTORS:
                if owner_sector == target_sector:
                    continue
                for owner in geometry.sectors[root][owner_sector]:
                    cap_name = (
                        f"cap::{root}::{owner_sector}->{target_sector}::{owner}"
                    )
                    choices = tuple(
                        sorted(
                            pair_key(owner, target)
                            for target in geometry.sectors[root][target_sector]
                        )
                    )
                    cap_candidates[cap_name] = choices
                    cap_owners[cap_name] = owner

    forced_true = (
        {pair_key("h0", "h1")} if relation == "B" else set()
    )
    candidate_nodes = [
        candidate_label(key) for key in sorted(candidate_contexts)
    ]
    cap_nodes = sorted(cap_candidates)
    nodes = [*geometry.triangle_nodes, *candidate_nodes, *cap_nodes]
    node_kinds = {}
    for node in geometry.triangle_nodes:
        node_kinds[node] = (
            "distinguished_root" if node in ROOT_PAIR else "triangle"
        )
    for key in candidate_contexts:
        node_kinds[candidate_label(key)] = (
            "candidate_B_forced_true"
            if key in forced_true
            else "candidate_B_unset"
        )
    for node in cap_nodes:
        node_kinds[node] = "cap_exactly_2"

    candidate_by_label = {
        candidate_label(key): key for key in candidate_contexts
    }
    cap_sets = {
        cap_name: set(keys) for cap_name, keys in cap_candidates.items()
    }

    def base_relation(left: str, right: str) -> str:
        if left == right:
            return "diag"
        if left in geometry.triangle_nodes and right in geometry.triangle_nodes:
            return triangle_relations.get(pair_key(left, right), "U_ALL")
        left_candidate = candidate_by_label.get(left)
        right_candidate = candidate_by_label.get(right)
        if left_candidate is not None and right in left_candidate:
            return "candidate_endpoint"
        if right_candidate is not None and left in right_candidate:
            return "candidate_endpoint"
        if left_candidate is not None and right in cap_sets:
            if left_candidate in cap_sets[right]:
                return "candidate_in_cap"
        if right_candidate is not None and left in cap_sets:
            if right_candidate in cap_sets[left]:
                return "candidate_in_cap"
        if left in cap_owners and cap_owners[left] == right:
            return "cap_owner"
        if right in cap_owners and cap_owners[right] == left:
            return "cap_owner"
        return "none"

    tokens = [
        [
            f"{node_kinds[left]}->{node_kinds[right]}:"
            f"{base_relation(left, right)}"
            for right in nodes
        ]
        for left in nodes
    ]
    template = Template(
        geometry=geometry,
        nodes=nodes,
        tokens=tokens,
        triangle_relations=triangle_relations,
        candidate_contexts=dict(candidate_contexts),
        cap_candidates=cap_candidates,
        cap_owners=cap_owners,
        forced_true=forced_true,
    )
    validate_template(template)
    return template


def validate_template(template: Template) -> dict[str, object]:
    relation = template.geometry.relation
    expected_candidates = {"K": 216, "B": 215, "C": 216, "D": 216}
    expected_orders = {"K": 319, "B": 323, "C": 325, "D": 326}
    if len(template.candidate_contexts) != expected_candidates[relation]:
        raise AssertionError("unexpected unique candidate count")
    if len(template.cap_candidates) != 72:
        raise AssertionError("two roots must contribute 72 exact-two caps")
    if len(template.nodes) != expected_orders[relation]:
        raise AssertionError("unexpected expanded CSP order")
    if any(len(choices) != 6 for choices in template.cap_candidates.values()):
        raise AssertionError("each exact-two cap must contain six candidates")
    if any(key not in template.candidate_contexts for key in template.forced_true):
        raise AssertionError("forced truth is not a candidate variable")

    shared = {
        key: contexts
        for key, contexts in template.candidate_contexts.items()
        if len(contexts) > 1
    }
    if relation == "B":
        if set(shared) != {pair_key("h0", "h1")}:
            raise AssertionError("B must have exactly one shared candidate")
        if set(shared) != template.forced_true:
            raise AssertionError("the shared B candidate must be forced true")
        if len(next(iter(shared.values()))) != 2:
            raise AssertionError("shared B candidate must occur in both roots")
    elif shared:
        raise AssertionError(f"{relation} unexpectedly shares candidate variables")

    node_index = {node: index for index, node in enumerate(template.nodes)}
    for key in template.candidate_contexts:
        label = candidate_label(key)
        row = Counter(
            token.rsplit(":", 1)[-1]
            for token in template.tokens[node_index[label]]
        )
        if row["candidate_endpoint"] != 2:
            raise AssertionError("candidate must have exactly two endpoints")
        expected_cap_degree = 4 if key in shared else 2
        if row["candidate_in_cap"] != expected_cap_degree:
            raise AssertionError("candidate has bad cap-incidence degree")
    for cap_name in template.cap_candidates:
        row = Counter(
            token.rsplit(":", 1)[-1]
            for token in template.tokens[node_index[cap_name]]
        )
        if row["candidate_in_cap"] != 6 or row["cap_owner"] != 1:
            raise AssertionError("bad cap incidence row")

    return {
        "expanded_order": len(template.nodes),
        "triangle_nodes": len(template.geometry.triangle_nodes),
        "unique_candidate_nodes": len(template.candidate_contexts),
        "cap_nodes": len(template.cap_candidates),
        "shared_candidate_nodes": len(shared),
        "forced_true_candidate_nodes": len(template.forced_true),
        "every_cap_has_six_candidates": True,
        "candidate_endpoints_checked": True,
    }


def deterministic_control(template: Template) -> dict[str, object]:
    """Choose a positive cap assignment only after the forced CSP is built.

    These controls prove local feasibility.  They are never fed into WL.
    """

    selected_by_root: dict[str, set[tuple[str, str]]] = {}
    for root in LOCAL_ROOTS:
        selected: set[tuple[str, str]] = set()
        for left_sector, right_sector in combinations(SECTORS, 2):
            left_nodes = template.geometry.sectors[root][left_sector]
            right_nodes = template.geometry.sectors[root][right_sector]
            for index in range(6):
                selected.add(pair_key(left_nodes[index], right_nodes[index]))
                selected.add(
                    pair_key(left_nodes[index], right_nodes[(index + 1) % 6])
                )
        selected_by_root[root] = selected

    selected = set().union(*selected_by_root.values())
    control = {
        "selected_candidate_labels": [
            candidate_label(key) for key in sorted(selected)
        ],
        "selected_unique_count": len(selected),
        "selected_incidence_count_across_two_roots": sum(
            len(values) for values in selected_by_root.values()
        ),
        "assignment_sha256": hashlib.sha256(
            canonical_bytes([candidate_label(key) for key in sorted(selected)])
        ).hexdigest(),
    }
    verify_control(template, control)
    return control


def verify_control(template: Template, control: dict[str, object]) -> None:
    label_to_key = {
        candidate_label(key): key for key in template.candidate_contexts
    }
    labels = control.get("selected_candidate_labels")
    if not isinstance(labels, list) or len(labels) != len(set(labels)):
        raise AssertionError("selected candidate labels must be a unique list")
    try:
        selected = {label_to_key[label] for label in labels}
    except KeyError as error:
        raise AssertionError("control selects a noncandidate") from error
    if not template.forced_true <= selected:
        raise AssertionError("control omits a forced-true B candidate")
    for cap_name, choices in template.cap_candidates.items():
        if len(selected.intersection(choices)) != 2:
            raise AssertionError(f"cap {cap_name} does not have value two")
    if control.get("selected_unique_count") != len(selected):
        raise AssertionError("selected unique count mismatch")
    incidence_count = sum(
        len(selected.intersection(choices))
        for choices in template.cap_candidates.values()
    )
    # Every selected local variable has two cap incidences per root context.
    if incidence_count != 144:
        raise AssertionError("two-root cap incidence total must be 144")
    if control.get("selected_incidence_count_across_two_roots") != 72:
        raise AssertionError("each rooted control must select 36 variables")
    expected_hash = hashlib.sha256(canonical_bytes(sorted(labels))).hexdigest()
    if control.get("assignment_sha256") != expected_hash:
        raise AssertionError("control assignment hash mismatch")


def _canonical_ids(values: Sequence[bytes]) -> list[int]:
    unique = sorted(set(values))
    identifiers = {value: index for index, value in enumerate(unique)}
    return [identifiers[value] for value in values]


def _initial_pair_colors(tokens: Sequence[Sequence[str]]) -> list[int]:
    flat = [token.encode("utf-8") for row in tokens for token in row]
    return _canonical_ids(flat)


def _refine_pair_colors(colors: Sequence[int], order: int) -> list[int]:
    signatures: list[bytes] = []
    pack_current = struct.Struct(">I").pack
    pack_record = struct.Struct(">III").pack
    for left in range(order):
        left_offset = left * order
        for right in range(order):
            multiplicities = Counter(
                (
                    colors[left_offset + middle],
                    colors[middle * order + right],
                )
                for middle in range(order)
            )
            signature = bytearray(pack_current(colors[left_offset + right]))
            for (first, second), count in sorted(multiplicities.items()):
                signature.extend(pack_record(first, second, count))
            signatures.append(bytes(signature))
    return _canonical_ids(signatures)


def same_partition(left: Sequence[int], right: Sequence[int]) -> bool:
    if len(left) != len(right):
        return False
    forward: dict[int, int] = {}
    reverse: dict[int, int] = {}
    for old, new in zip(left, right, strict=True):
        if old in forward and forward[old] != new:
            return False
        if new in reverse and reverse[new] != old:
            return False
        forward[old] = new
        reverse[new] = old
    return True


def wl2(tokens: Sequence[Sequence[str]]) -> dict[str, object]:
    order = len(tokens)
    if order == 0 or any(len(row) != order for row in tokens):
        raise ValueError("2-WL input must be a nonempty square matrix")
    colors = _initial_pair_colors(tokens)
    color_counts = [len(set(colors))]
    proper_rounds = 0
    while True:
        enforce_memory_floor()
        refined = _refine_pair_colors(colors, order)
        refined_count = len(set(refined))
        if refined_count < color_counts[-1]:
            raise AssertionError("2-WL refinement merged colors")
        if refined_count == color_counts[-1]:
            if not same_partition(colors, refined):
                raise AssertionError("equal 2-WL color count changed partition")
            colors = refined
            break
        colors = refined
        color_counts.append(refined_count)
        proper_rounds += 1

    # A hostile stability replay.
    replay = _refine_pair_colors(colors, order)
    if not same_partition(colors, replay):
        raise AssertionError("reported 2-WL partition is not stable")

    class_sizes = Counter(colors)
    representatives: dict[int, tuple[int, int]] = {}
    for index, color in enumerate(colors):
        representatives.setdefault(color, divmod(index, order))
    records = []
    for output_color in range(len(class_sizes)):
        left, right = representatives[output_color]
        multiplicities = Counter(
            (
                colors[left * order + middle],
                colors[middle * order + right],
            )
            for middle in range(order)
        )
        for (first, second), count in sorted(multiplicities.items()):
            records.append([first, second, output_color, count])

    matrix = [
        colors[offset : offset + order]
        for offset in range(0, order * order, order)
    ]
    diagonal_sizes = sorted(
        Counter(colors[index * order + index] for index in range(order)).values()
    )
    sizes = [class_sizes[index] for index in range(len(class_sizes))]
    return {
        "order": order,
        "initial_color_count": color_counts[0],
        "proper_refinement_rounds": proper_rounds,
        "color_counts": color_counts,
        "stable_color_count": len(class_sizes),
        "class_sizes": sizes,
        "diagonal_class_sizes": diagonal_sizes,
        "pair_color_matrix": matrix,
        "intersection_numbers_nonzero": records,
        "intersection_parameter_nonzero_count": len(records),
        "partition_sha256": hashlib.sha256(canonical_bytes(matrix)).hexdigest(),
        "intersection_tensor_sha256": hashlib.sha256(
            canonical_bytes(records)
        ).hexdigest(),
        "all_intersection_numbers_nonnegative_integers": True,
        "stable_replay_passed": True,
    }


def triangle_core_tokens(template: Template) -> list[list[str]]:
    triangle_set = set(template.geometry.triangle_nodes)
    indices = [
        index
        for index, node in enumerate(template.nodes)
        if node in triangle_set
    ]
    return [
        [template.tokens[left][right] for right in indices]
        for left in indices
    ]


def _initial_triple_colors(pair_tokens: Sequence[Sequence[str]]) -> list[int]:
    order = len(pair_tokens)
    pair_colors = _initial_pair_colors(pair_tokens)
    signatures = []
    pack = struct.Struct(">IIIIIIIII").pack
    for first, second, third in product(range(order), repeat=3):
        indices = (first, second, third)
        values = tuple(
            pair_colors[indices[left] * order + indices[right]]
            for left in range(3)
            for right in range(3)
        )
        signatures.append(pack(*values))
    return _canonical_ids(signatures)


def _triple_index(first: int, second: int, third: int, order: int) -> int:
    return (first * order + second) * order + third


def _refine_triple_colors(colors: Sequence[int], order: int) -> list[int]:
    signatures: list[bytes] = []
    pack_current = struct.Struct(">I").pack
    pack_record = struct.Struct(">IIII").pack
    for first, second, third in product(range(order), repeat=3):
        multiplicities = Counter(
            (
                colors[_triple_index(replacement, second, third, order)],
                colors[_triple_index(first, replacement, third, order)],
                colors[_triple_index(first, second, replacement, order)],
            )
            for replacement in range(order)
        )
        signature = bytearray(
            pack_current(colors[_triple_index(first, second, third, order)])
        )
        for color_triple, count in sorted(multiplicities.items()):
            signature.extend(pack_record(*color_triple, count))
        signatures.append(bytes(signature))
    return _canonical_ids(signatures)


def wl3(pair_tokens: Sequence[Sequence[str]]) -> dict[str, object]:
    """Run exact folklore 3-WL on the small two-root triangle core."""

    order = len(pair_tokens)
    if order == 0 or any(len(row) != order for row in pair_tokens):
        raise ValueError("3-WL pair-color input must be nonempty and square")
    colors = _initial_triple_colors(pair_tokens)
    color_counts = [len(set(colors))]
    proper_rounds = 0
    while True:
        enforce_memory_floor()
        refined = _refine_triple_colors(colors, order)
        refined_count = len(set(refined))
        if refined_count < color_counts[-1]:
            raise AssertionError("3-WL refinement merged colors")
        if refined_count == color_counts[-1]:
            if not same_partition(colors, refined):
                raise AssertionError("equal 3-WL color count changed partition")
            colors = refined
            break
        colors = refined
        color_counts.append(refined_count)
        proper_rounds += 1

    replay = _refine_triple_colors(colors, order)
    if not same_partition(colors, replay):
        raise AssertionError("reported 3-WL partition is not stable")
    class_sizes = Counter(colors)
    vertex_orbits = Counter(
        colors[_triple_index(index, index, index, order)]
        for index in range(order)
    )
    return {
        "order": order,
        "tuple_count": order**3,
        "initial_color_count": color_counts[0],
        "proper_refinement_rounds": proper_rounds,
        "color_counts": color_counts,
        "stable_color_count": len(class_sizes),
        "class_sizes": [
            class_sizes[index] for index in range(len(class_sizes))
        ],
        "diagonal_vertex_class_sizes": sorted(vertex_orbits.values()),
        "tuple_partition_sha256": hashlib.sha256(
            canonical_bytes(colors)
        ).hexdigest(),
        "stable_replay_passed": True,
    }


def compact_wl2(closure: dict[str, object]) -> dict[str, object]:
    return {
        key: closure[key]
        for key in (
            "order",
            "initial_color_count",
            "proper_refinement_rounds",
            "color_counts",
            "stable_color_count",
            "diagonal_class_sizes",
            "intersection_parameter_nonzero_count",
            "partition_sha256",
            "intersection_tensor_sha256",
            "all_intersection_numbers_nonnegative_integers",
            "stable_replay_passed",
        )
    }


def build_relation_record(relation: str) -> dict[str, object]:
    enforce_memory_floor()
    template = build_template(relation)
    geometry_checks = validate_geometry(template.geometry)
    template_checks = validate_template(template)
    control = deterministic_control(template)
    closure_2wl = wl2(template.tokens)
    core_tokens = triangle_core_tokens(template)
    closure_3wl = wl3(core_tokens)
    return {
        "relation": relation,
        "free_physical_memory_at_start_at_least_percent": (
            MEMORY_FLOOR_PERCENT
        ),
        "geometry": {
            "sectors": deepcopy(template.geometry.sectors),
            "triangle_nodes": template.geometry.triangle_nodes,
            "common_petals": template.geometry.common_petals,
            "checks": geometry_checks,
        },
        "forced_csp": {
            "nodes": template.nodes,
            "triangle_relation_records": [
                [*key, value]
                for key, value in sorted(template.triangle_relations.items())
            ],
            "candidate_records": [
                {
                    "key": list(key),
                    "label": candidate_label(key),
                    "contexts": [list(context) for context in contexts],
                    "forced_value": (
                        1 if key in template.forced_true else None
                    ),
                }
                for key, contexts in sorted(template.candidate_contexts.items())
            ],
            "cap_records": [
                {
                    "label": cap_name,
                    "owner": template.cap_owners[cap_name],
                    "right_side": 2,
                    "candidate_labels": [
                        candidate_label(key)
                        for key in template.cap_candidates[cap_name]
                    ],
                }
                for cap_name in sorted(template.cap_candidates)
            ],
            "checks": template_checks,
            "positive_integral_control": control,
        },
        "expanded_forced_csp_2wl": {
            "scope": (
                "2-WL on triangle, unresolved candidate, and exact-two cap "
                "incidence nodes; the numerical cap RHS is checked by the "
                "separate positive integral control"
            ),
            "closure": closure_2wl,
        },
        "triangle_core_3wl": {
            "scope": (
                "exact folklore 3-WL on the smallest two-root typed triangle "
                "core, before any candidate completion"
            ),
            "closure": closure_3wl,
        },
        "result": {
            "integral_intersection_number_exclusion": False,
            "positive_local_control_survives": True,
            "forced_truth_assignments": len(template.forced_true),
            "endpoint": "UNKNOWN",
        },
    }


def validate_result(payload: dict[str, object]) -> None:
    if payload.get("format") != "wave53-multi-root-wl-v1":
        raise AssertionError("wrong result format")
    if payload.get("claim_label") != "DERIVED":
        raise AssertionError("discovery result must remain DERIVED")
    records = payload.get("relation_records")
    if not isinstance(records, list):
        raise AssertionError("relation records missing")
    if [record.get("relation") for record in records] != list(RELATION_ORDER):
        raise AssertionError("relation record order mismatch")
    expected_hashes = {
        record["relation"]: hashlib.sha256(canonical_bytes(record)).hexdigest()
        for record in records
    }
    if payload.get("relation_record_sha256s") != expected_hashes:
        raise AssertionError("relation-record hash mismatch")
    for record in records:
        relation = record["relation"]
        template = build_template(relation)
        stored_control = record["forced_csp"]["positive_integral_control"]
        verify_control(template, stored_control)
        closure = record["expanded_forced_csp_2wl"]["closure"]
        if not closure.get("all_intersection_numbers_nonnegative_integers"):
            raise AssertionError("2-WL integrality flag missing")
        if record["result"]["integral_intersection_number_exclusion"]:
            raise AssertionError("a realized finite template cannot claim exclusion")
        if record["result"]["endpoint"] != "UNKNOWN":
            raise AssertionError("endpoint status inflation")
    boundary = payload.get("claim_boundary", {})
    if boundary.get("prism_free_endpoint") != "UNKNOWN":
        raise AssertionError("endpoint status must remain UNKNOWN")
    if boundary.get("conway_99") != "UNKNOWN":
        raise AssertionError("Conway-99 status must remain UNKNOWN")


def assemble_results(records: Sequence[dict[str, object]]) -> dict[str, object]:
    if [record.get("relation") for record in records] != list(RELATION_ORDER):
        raise AssertionError("cannot assemble incomplete or misordered records")
    record_hashes = {
        record["relation"]: hashlib.sha256(canonical_bytes(record)).hexdigest()
        for record in records
    }
    payload = {
        "format": "wave53-multi-root-wl-v1",
        "claim_label": "DERIVED",
        "claim_boundary": {
            "two_root_forced_csp_closures": "EXACT_DERIVED",
            "explicit_local_cap_controls": "CANDIDATE",
            "new_integral_intersection_number_obstruction": False,
            "prism_free_endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "frozen_model": {
            "root_relations": list(RELATION_ORDER),
            "common_K_neighbor_counts": COMMON_K_NEIGHBORS,
            "one_root_sector_structure": "3K6",
            "per_opposite_sector_cap": "exactly two B among six candidates",
            "B_pair_extra_forcing": (
                "the two common K-neighbor triangles form one shared "
                "candidate variable forced to B"
            ),
            "automorphism_policy": (
                "root vertices are coordinatized only to name forced "
                "incidences; no local permutation is assumed to extend to "
                "a completed graph"
            ),
            "completion_policy": (
                "all unresolved B/C pairs remain candidate nodes during WL; "
                "deterministic 2-factor assignments are post-hoc controls only"
            ),
        },
        "relation_records": records,
        "relation_record_sha256s": record_hashes,
        "aggregate_result": {
            "relations_excluded": [],
            "relations_with_positive_local_controls": list(RELATION_ORDER),
            "stronger_than_wave52": (
                "yes: both rooted 3K6 systems, their shared triangle nodes, "
                "their shared candidate variables, and all 72 caps are "
                "retained simultaneously"
            ),
            "disposition": "NULL_RESULT_FOR_THIS_MULTI_ROOT_COHERENT_LIFT",
            "endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
        "checks": {
            "all_arithmetic_exact": True,
            "all_four_nonidentity_root_relations_checked": True,
            "exact_2wl_stability_replayed": True,
            "exact_3wl_stability_replayed": True,
            "positive_cap_controls_checked": True,
            "memory_floor_percent": MEMORY_FLOOR_PERCENT,
        },
        "limitations": [
            "This is discovery-agent work and is not independently verified.",
            "The finite templates retain only two rooted K-neighborhoods, not all 231 graph triangles or 99 graph vertices.",
            "2-WL sees cap incidence but not the numerical right side; exact-two is checked separately by local integral controls.",
            "3-WL is run only on the smaller triangle core and omits cap nodes.",
            "A positive local cap control is not a graph construction and need not extend globally.",
            "Integral intersection numbers of a realized finite incidence template do not certify graph realizability.",
            "No automorphism, transitivity, homogeneous intersection table, or association scheme is assumed.",
            "No endpoint exclusion, construction, or improved n3 upper bound follows.",
        ],
    }
    validate_result(payload)
    return payload


def build_results() -> dict[str, object]:
    enforce_memory_floor()
    records = [build_relation_record(relation) for relation in RELATION_ORDER]
    return assemble_results(records)


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--relation", choices=RELATION_ORDER)
    parser.add_argument("--assemble-from", type=Path)
    parser.add_argument("--envelope-only", action="store_true")
    arguments = parser.parse_args()
    if (arguments.output is None) == (arguments.verify is None):
        parser.error("choose exactly one of --output or --verify")
    if arguments.assemble_from is not None and arguments.output is None:
        parser.error("--assemble-from requires --output")
    if arguments.assemble_from is not None and arguments.relation is not None:
        parser.error("--assemble-from and --relation are mutually exclusive")
    if arguments.envelope_only and arguments.verify is None:
        parser.error("--envelope-only requires --verify")

    if arguments.output is not None and arguments.relation is not None:
        payload = build_relation_record(arguments.relation)
    elif arguments.output is not None and arguments.assemble_from is not None:
        records = [
            json.loads(
                (arguments.assemble_from / f"{relation}.json").read_text(
                    encoding="utf-8"
                )
            )
            for relation in RELATION_ORDER
        ]
        payload = assemble_results(records)
    elif arguments.verify is not None and arguments.envelope_only:
        payload = json.loads(arguments.verify.read_text(encoding="utf-8"))
        validate_result(payload)
        encoded = canonical_bytes(payload)
        if arguments.verify.read_bytes() != encoded:
            print("FAIL_NONCANONICAL_ENVELOPE", file=sys.stderr)
            return 1
        print("PASS_EXACT_ENVELOPE")
        print(f"sha256={hashlib.sha256(encoded).hexdigest()}")
        return 0
    elif arguments.verify is not None and arguments.relation is not None:
        stored_payload = json.loads(arguments.verify.read_text(encoding="utf-8"))
        validate_result(stored_payload)
        stored_record = next(
            record
            for record in stored_payload["relation_records"]
            if record["relation"] == arguments.relation
        )
        rebuilt_record = build_relation_record(arguments.relation)
        stored = canonical_bytes(stored_record)
        encoded = canonical_bytes(rebuilt_record)
        if stored != encoded:
            print(
                f"FAIL_RELATION_REPLAY relation={arguments.relation}",
                file=sys.stderr,
            )
            print(
                f"stored_sha256={hashlib.sha256(stored).hexdigest()}",
                file=sys.stderr,
            )
            print(
                f"rebuilt_sha256={hashlib.sha256(encoded).hexdigest()}",
                file=sys.stderr,
            )
            return 1
        print(f"PASS_RELATION_REPLAY relation={arguments.relation}")
        print(f"sha256={hashlib.sha256(encoded).hexdigest()}")
        return 0
    else:
        payload = build_results()
    encoded = canonical_bytes(payload)
    digest = hashlib.sha256(encoded).hexdigest()
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_bytes(encoded)
        print(f"WROTE {arguments.output}")
        print(f"sha256={digest}")
        return 0

    assert arguments.verify is not None
    stored = arguments.verify.read_bytes()
    if stored != encoded:
        print("FAIL_EXACT_REPLAY", file=sys.stderr)
        print(
            f"stored_sha256={hashlib.sha256(stored).hexdigest()}",
            file=sys.stderr,
        )
        print(f"rebuilt_sha256={digest}", file=sys.stderr)
        return 1
    print("PASS_EXACT_REPLAY")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
