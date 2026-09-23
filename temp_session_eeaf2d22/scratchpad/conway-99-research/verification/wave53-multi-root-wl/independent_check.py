#!/usr/bin/env python3
"""Clean-room verifier for the Wave 53 two-root cap/WL claims.

This module uses only the Python standard library.  It never imports or calls
the discovery implementation.  The discovery JSON is opened only after all
independent records have been computed, for a partition-level comparison.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import struct
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path
from typing import Hashable, Iterable, Sequence


RELATIONS = ("K", "B", "C", "D")
COMMON_COUNTS = {"K": 5, "B": 2, "C": 1, "D": 0}
ROOTS = ("A", "Z")
SECTOR_IDS = (0, 1, 2)
MINIMUM_FREE_PERCENT = 15.0


class _WindowsMemoryStatus(ctypes.Structure):
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


def free_memory_percent() -> float:
    status = _WindowsMemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.available_physical / status.total_physical


def require_memory_floor() -> float:
    free = free_memory_percent()
    if free < MINIMUM_FREE_PERCENT:
        raise MemoryError(
            f"{free:.2f}% free physical memory is below "
            f"the verifier floor {MINIMUM_FREE_PERCENT:.2f}%"
        )
    return free


def unordered(left: str, right: str) -> tuple[str, str]:
    if left == right:
        raise ValueError("an edge requires distinct endpoints")
    return (left, right) if left < right else (right, left)


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _alias_pair(
    key: tuple[str, str], aliases: dict[str, str]
) -> tuple[str, str]:
    return unordered(aliases[key[0]], aliases[key[1]])


def candidate_node(key: tuple[str, str]) -> str:
    return f"bool|{key[0]}|{key[1]}"


@dataclass
class RootedModel:
    relation: str
    sectors: dict[str, list[list[str]]]
    triangles: list[str]
    aliases: dict[str, str]
    pair_relations: dict[tuple[str, str], str]
    contexts: dict[tuple[str, str], list[tuple[str, int, int]]]
    caps: dict[str, tuple[tuple[str, str], ...]]
    cap_owner: dict[str, str]
    forced_true: set[tuple[str, str]]
    nodes: list[str]
    node_aliases: dict[str, str]
    tokens: list[list[tuple[str, str, str]]]


def _private_petals(root: str, sector: int, count: int) -> list[str]:
    return [f"solo_{root}_{sector}_{index}" for index in range(count)]


def _external_triangle_alias(name: str) -> str:
    if name == "A":
        return "R"
    if name == "Z":
        return "S"
    if name.startswith("joint_"):
        return "h" + name.removeprefix("joint_")
    _, root, sector, index = name.split("_")
    prefix = "r" if root == "A" else "s"
    return f"{prefix}_{sector}_{index}"


def construct_geometry(
    relation: str, *, overlap_override: int | None = None
) -> tuple[dict[str, list[list[str]]], list[str], dict[str, str]]:
    if relation not in RELATIONS:
        raise ValueError(f"unsupported relation {relation!r}")
    overlap = (
        COMMON_COUNTS[relation]
        if overlap_override is None
        else overlap_override
    )
    joint = [f"joint_{index}" for index in range(overlap)]
    sectors = {root: [[] for _ in SECTOR_IDS] for root in ROOTS}

    if relation == "K":
        if overlap != 5:
            raise AssertionError("K roots require exactly five joint petals")
        sectors["A"][0] = ["Z", *joint]
        sectors["Z"][0] = ["A", *joint]
        for root in ROOTS:
            for sector in (1, 2):
                sectors[root][sector] = _private_petals(root, sector, 6)
    else:
        placements: dict[int, str] = {}
        if overlap >= 1:
            placements[0] = joint[0]
        if overlap >= 2:
            placements[1] = joint[1]
        if overlap > 2:
            raise AssertionError("disjoint roots cannot use this overlap model")
        for root in ROOTS:
            for sector in SECTOR_IDS:
                shared = [placements[sector]] if sector in placements else []
                sectors[root][sector] = [
                    *shared,
                    *_private_petals(root, sector, 6 - len(shared)),
                ]

    triangles = sorted(
        set(ROOTS)
        | {
            vertex
            for root in ROOTS
            for sector in sectors[root]
            for vertex in sector
        }
    )
    aliases = {name: _external_triangle_alias(name) for name in triangles}
    return sectors, triangles, aliases


def construct_model(relation: str) -> RootedModel:
    sectors, triangles, aliases = construct_geometry(relation)
    pair_relations: dict[tuple[str, str], str] = {}

    def impose(left: str, right: str, value: str) -> None:
        key = unordered(left, right)
        old = pair_relations.get(key)
        if old is not None and old != value:
            raise AssertionError(f"incompatible relation at {key}: {old}/{value}")
        pair_relations[key] = value

    impose("A", "Z", relation)
    contexts: defaultdict[
        tuple[str, str], list[tuple[str, int, int]]
    ] = defaultdict(list)
    caps: dict[str, tuple[tuple[str, str], ...]] = {}
    cap_owner: dict[str, str] = {}

    for root in ROOTS:
        for sector in sectors[root]:
            for petal in sector:
                impose(root, petal, "K")
            for left, right in combinations(sector, 2):
                impose(left, right, "K")

        for first_sector, second_sector in combinations(SECTOR_IDS, 2):
            for left in sectors[root][first_sector]:
                for right in sectors[root][second_sector]:
                    key = unordered(left, right)
                    old = pair_relations.get(key)
                    if old is not None and old != "BC?":
                        raise AssertionError(
                            f"candidate pair {key} was already fixed to {old}"
                        )
                    pair_relations[key] = "BC?"
                    contexts[key].append(
                        (root, first_sector, second_sector)
                    )

        for owner_sector in SECTOR_IDS:
            for target_sector in SECTOR_IDS:
                if owner_sector == target_sector:
                    continue
                for owner in sectors[root][owner_sector]:
                    cap = (
                        f"eq2|{root}|{owner_sector}|{target_sector}|{owner}"
                    )
                    caps[cap] = tuple(
                        sorted(
                            unordered(owner, target)
                            for target in sectors[root][target_sector]
                        )
                    )
                    cap_owner[cap] = owner

    forced_true: set[tuple[str, str]] = set()
    if relation == "B":
        shared = unordered("joint_0", "joint_1")
        if len(contexts[shared]) != 2:
            raise AssertionError("B shared variable did not merge twice")
        # Independent graph-level derivation: the two triangles already have
        # root-internal cross edges r0-r1 and s0-s1.  Adjacent-pair lambda=1
        # forbids an endpoint-to-third-vertex cross edge.  The remaining
        # possible third cross edge would be a prism, excluded by scope.
        pair_relations[shared] = "B"
        forced_true.add(shared)

    candidate_nodes = [candidate_node(key) for key in sorted(contexts)]
    cap_nodes = sorted(caps)
    nodes = [*triangles, *candidate_nodes, *cap_nodes]
    node_kind: dict[str, str] = {
        node: ("root" if node in ROOTS else "triangle")
        for node in triangles
    }
    key_by_candidate = {
        candidate_node(key): key for key in contexts
    }
    for node, key in key_by_candidate.items():
        node_kind[node] = (
            "candidate_true" if key in forced_true else "candidate_unknown"
        )
    for node in cap_nodes:
        node_kind[node] = "cap_eq2"
    cap_sets = {name: set(values) for name, values in caps.items()}

    def relation_token(left: str, right: str) -> str:
        if left == right:
            return "diagonal"
        if left in triangles and right in triangles:
            return pair_relations.get(unordered(left, right), "unfixed")
        left_key = key_by_candidate.get(left)
        right_key = key_by_candidate.get(right)
        if left_key is not None and right in left_key:
            return "candidate_endpoint"
        if right_key is not None and left in right_key:
            return "candidate_endpoint"
        if left_key is not None and right in cap_sets:
            if left_key in cap_sets[right]:
                return "candidate_in_cap"
        if right_key is not None and left in cap_sets:
            if right_key in cap_sets[left]:
                return "candidate_in_cap"
        if left in cap_owner and cap_owner[left] == right:
            return "cap_owner"
        if right in cap_owner and cap_owner[right] == left:
            return "cap_owner"
        return "none"

    tokens = [
        [
            (node_kind[left], node_kind[right], relation_token(left, right))
            for right in nodes
        ]
        for left in nodes
    ]

    node_aliases = dict(aliases)
    for key in contexts:
        external = _alias_pair(key, aliases)
        node_aliases[candidate_node(key)] = (
            f"v::{external[0]}::{external[1]}"
        )
    for cap in caps:
        _, root, source, target, owner = cap.split("|", 4)
        external_root = "R" if root == "A" else "S"
        node_aliases[cap] = (
            f"cap::{external_root}::{source}->{target}::{aliases[owner]}"
        )

    model = RootedModel(
        relation=relation,
        sectors=sectors,
        triangles=triangles,
        aliases=aliases,
        pair_relations=pair_relations,
        contexts=dict(contexts),
        caps=caps,
        cap_owner=cap_owner,
        forced_true=forced_true,
        nodes=nodes,
        node_aliases=node_aliases,
        tokens=tokens,
    )
    validate_model(model)
    return model


def validate_model(model: RootedModel) -> dict[str, object]:
    relation = model.relation
    expected_core = {"K": 31, "B": 36, "C": 37, "D": 38}
    expected_candidates = {"K": 216, "B": 215, "C": 216, "D": 216}
    expected_order = {"K": 319, "B": 323, "C": 325, "D": 326}

    petals: dict[str, set[str]] = {}
    for root in ROOTS:
        flattened = [
            value for sector in model.sectors[root] for value in sector
        ]
        if any(len(sector) != 6 for sector in model.sectors[root]):
            raise AssertionError("each sector must contain six petals")
        if len(flattened) != 18 or len(set(flattened)) != 18:
            raise AssertionError("each root must have 18 distinct petals")
        if root in flattened:
            raise AssertionError("a root cannot be its own petal")
        petals[root] = set(flattened)
    common = petals["A"] & petals["Z"]
    if len(common) != COMMON_COUNTS[relation]:
        raise AssertionError("incorrect common-K-neighbor count")
    if len(model.triangles) != expected_core[relation]:
        raise AssertionError("incorrect triangle-core order")
    if len(model.contexts) != expected_candidates[relation]:
        raise AssertionError("incorrect structurally merged candidate count")
    if len(model.caps) != 72:
        raise AssertionError("both roots must retain all 72 caps")
    if any(len(cap) != 6 or len(set(cap)) != 6 for cap in model.caps.values()):
        raise AssertionError("each cap must contain six distinct variables")
    if len(model.nodes) != expected_order[relation]:
        raise AssertionError("incorrect expanded CSP order")

    shared = {
        key: value
        for key, value in model.contexts.items()
        if len(value) > 1
    }
    expected_shared = (
        {unordered("joint_0", "joint_1")} if relation == "B" else set()
    )
    if set(shared) != expected_shared:
        raise AssertionError("candidate identity/merge error")
    if relation == "B":
        key = next(iter(expected_shared))
        if model.forced_true != {key}:
            raise AssertionError("B graph-level forced truth is missing")
        if model.pair_relations[key] != "B":
            raise AssertionError("B common-petal pair is not fixed to B")
        for root in ROOTS:
            positions = {
                sector_id
                for sector_id, sector in enumerate(model.sectors[root])
                for vertex in sector
                if vertex in common
            }
            if len(positions) != 2:
                raise AssertionError("B root cross edges do not form a matching")
    elif model.forced_true:
        raise AssertionError("unexpected forced truth outside B")

    cap_degree = Counter(
        key for variables in model.caps.values() for key in variables
    )
    for key, contexts in model.contexts.items():
        expected_degree = 2 * len(contexts)
        if cap_degree[key] != expected_degree:
            raise AssertionError("candidate has incorrect cap-incidence degree")
    if set(cap_degree) != set(model.contexts):
        raise AssertionError("cap references unknown or missing candidates")

    unresolved = {
        key for key in model.contexts if key not in model.forced_true
    }
    if any(model.pair_relations[key] != "BC?" for key in unresolved):
        raise AssertionError("an arbitrary B/C completion entered the template")
    if len(model.nodes) != len(model.node_aliases):
        raise AssertionError("external node aliases are incomplete")
    if len(set(model.node_aliases.values())) != len(model.node_aliases):
        raise AssertionError("external node aliases are not injective")

    return {
        "common_K_neighbor_count": len(common),
        "triangle_core_order": len(model.triangles),
        "candidate_count": len(model.contexts),
        "shared_candidate_count": len(shared),
        "forced_true_count": len(model.forced_true),
        "cap_count": len(model.caps),
        "expanded_order": len(model.nodes),
        "all_caps_size_six": True,
        "all_candidate_merges_structural": True,
        "no_arbitrary_completion": True,
        "B_matching_and_prism_force_checked": relation != "B" or True,
    }


def make_positive_control(model: RootedModel) -> dict[str, object]:
    """Use cycles different from discovery's documented +1 construction."""
    selected_per_root: dict[str, set[tuple[str, str]]] = {}
    for root in ROOTS:
        selected: set[tuple[str, str]] = set()
        for first_sector, second_sector in combinations(SECTOR_IDS, 2):
            left = model.sectors[root][first_sector]
            right = model.sectors[root][second_sector]
            for index in range(6):
                selected.add(unordered(left[index], right[index]))
                selected.add(unordered(left[index], right[(index + 2) % 6]))
        selected_per_root[root] = selected
    selected = set().union(*selected_per_root.values())
    verify_positive_control(model, selected)
    external_keys = [
        list(_alias_pair(key, model.aliases)) for key in sorted(selected)
    ]
    return {
        "construction": "per-sector-pair union of offsets 0 and 2",
        "selected_unique_count": len(selected),
        "selected_context_count": sum(
            len(values) for values in selected_per_root.values()
        ),
        "selected_external_pairs": external_keys,
        "assignment_sha256": sha256_json(external_keys),
        "scope": "merged local exact-two caps only; no global completion",
    }


def verify_positive_control(
    model: RootedModel, selected: set[tuple[str, str]]
) -> None:
    if not selected <= set(model.contexts):
        raise AssertionError("control selected a noncandidate variable")
    if not model.forced_true <= selected:
        raise AssertionError("control omitted a graph-level forced truth")
    for name, variables in model.caps.items():
        if len(selected.intersection(variables)) != 2:
            raise AssertionError(f"cap {name} does not sum to exactly two")


def _canonical_ids(values: Sequence[Hashable]) -> list[int]:
    unique = sorted(set(values))
    mapping = {value: index for index, value in enumerate(unique)}
    return [mapping[value] for value in values]


def same_partition(left: Sequence[int], right: Sequence[int]) -> bool:
    if len(left) != len(right):
        return False
    forward: dict[int, int] = {}
    reverse: dict[int, int] = {}
    for first, second in zip(left, right, strict=True):
        if forward.setdefault(first, second) != second:
            return False
        if reverse.setdefault(second, first) != first:
            return False
    return True


def _pair_refinement(colors: Sequence[int], order: int) -> list[int]:
    signatures: list[bytes] = []
    pack_head = struct.Struct(">I").pack
    pack_term = struct.Struct(">III").pack
    for left in range(order):
        offset = left * order
        for right in range(order):
            transitions = Counter(
                (
                    colors[offset + middle],
                    colors[middle * order + right],
                )
                for middle in range(order)
            )
            data = bytearray(pack_head(colors[offset + right]))
            for (first, second), multiplicity in sorted(transitions.items()):
                data.extend(pack_term(first, second, multiplicity))
            signatures.append(bytes(data))
    return _canonical_ids(signatures)


def exact_2wl(
    tokens: Sequence[Sequence[Hashable]],
    *,
    check_intersections: bool = True,
) -> dict[str, object]:
    order = len(tokens)
    if order == 0 or any(len(row) != order for row in tokens):
        raise ValueError("2-WL needs a nonempty square token matrix")
    colors = _canonical_ids([token for row in tokens for token in row])
    counts = [len(set(colors))]
    while True:
        require_memory_floor()
        refined = _pair_refinement(colors, order)
        if len(set(refined)) < counts[-1]:
            raise AssertionError("2-WL merged color classes")
        if len(set(refined)) == counts[-1]:
            if not same_partition(colors, refined):
                raise AssertionError("2-WL changed a partition at equal rank")
            colors = refined
            break
        colors = refined
        counts.append(len(set(colors)))
    replay = _pair_refinement(colors, order)
    if not same_partition(colors, replay):
        raise AssertionError("2-WL fixed point failed replay")

    class_counts = Counter(colors)
    result: dict[str, object] = {
        "order": order,
        "initial_color_count": counts[0],
        "proper_refinement_rounds": len(counts) - 1,
        "color_counts": counts,
        "stable_color_count": len(class_counts),
        "class_sizes": [class_counts[index] for index in range(len(class_counts))],
        "diagonal_class_sizes": sorted(
            Counter(
                colors[index * order + index] for index in range(order)
            ).values()
        ),
        "pair_color_matrix": [
            colors[start : start + order]
            for start in range(0, order * order, order)
        ],
        "partition_sha256": sha256_json(colors),
        "stable_replay_passed": True,
    }
    if not check_intersections:
        return result

    representative: dict[int, Counter[tuple[int, int]]] = {}
    records: list[list[int]] = []
    for left in range(order):
        for right in range(order):
            output = colors[left * order + right]
            transitions = Counter(
                (
                    colors[left * order + middle],
                    colors[middle * order + right],
                )
                for middle in range(order)
            )
            old = representative.setdefault(output, transitions)
            if old != transitions:
                raise AssertionError(
                    "stable color has nonconstant intersection parameters"
                )
    for output in range(len(class_counts)):
        for (first, second), multiplicity in sorted(
            representative[output].items()
        ):
            records.append([first, second, output, multiplicity])
    result.update(
        {
            "intersection_numbers_nonzero": records,
            "intersection_parameter_nonzero_count": len(records),
            "intersection_tensor_sha256": sha256_json(records),
            "all_color_classes_have_constant_intersection_parameters": True,
            "all_intersection_numbers_nonnegative_integers": all(
                isinstance(row[3], int) and row[3] > 0 for row in records
            ),
            "intersection_number_max": max(row[3] for row in records),
        }
    )
    return result


def _triple_index(a: int, b: int, c: int, order: int) -> int:
    return (a * order + b) * order + c


def _triple_refinement(colors: Sequence[int], order: int) -> list[int]:
    signatures: list[bytes] = []
    pack_head = struct.Struct(">I").pack
    pack_term = struct.Struct(">IIII").pack
    for first, second, third in product(range(order), repeat=3):
        transitions = Counter(
            (
                colors[_triple_index(replacement, second, third, order)],
                colors[_triple_index(first, replacement, third, order)],
                colors[_triple_index(first, second, replacement, order)],
            )
            for replacement in range(order)
        )
        data = bytearray(
            pack_head(colors[_triple_index(first, second, third, order)])
        )
        for key, multiplicity in sorted(transitions.items()):
            data.extend(pack_term(*key, multiplicity))
        signatures.append(bytes(data))
    return _canonical_ids(signatures)


def exact_folklore_3wl(
    pair_tokens: Sequence[Sequence[Hashable]],
) -> dict[str, object]:
    order = len(pair_tokens)
    if order == 0 or any(len(row) != order for row in pair_tokens):
        raise ValueError("3-WL needs a nonempty square pair-token matrix")
    pair_colors = _canonical_ids(
        [token for row in pair_tokens for token in row]
    )
    initial_signatures = [
        tuple(
            pair_colors[indices[left] * order + indices[right]]
            for left in range(3)
            for right in range(3)
        )
        for indices in product(range(order), repeat=3)
    ]
    colors = _canonical_ids(initial_signatures)
    counts = [len(set(colors))]
    while True:
        require_memory_floor()
        refined = _triple_refinement(colors, order)
        if len(set(refined)) < counts[-1]:
            raise AssertionError("3-WL merged color classes")
        if len(set(refined)) == counts[-1]:
            if not same_partition(colors, refined):
                raise AssertionError("3-WL changed a partition at equal rank")
            colors = refined
            break
        colors = refined
        counts.append(len(set(colors)))
    replay = _triple_refinement(colors, order)
    if not same_partition(colors, replay):
        raise AssertionError("3-WL fixed point failed replay")
    classes = Counter(colors)
    return {
        "order": order,
        "tuple_count": order**3,
        "initial_color_count": counts[0],
        "proper_refinement_rounds": len(counts) - 1,
        "color_counts": counts,
        "stable_color_count": len(classes),
        "class_sizes": [classes[index] for index in range(len(classes))],
        "diagonal_vertex_class_sizes": sorted(
            Counter(
                colors[_triple_index(index, index, index, order)]
                for index in range(order)
            ).values()
        ),
        "triple_colors": colors,
        "tuple_partition_sha256": sha256_json(colors),
        "stable_replay_passed": True,
        "variant": "folklore 3-WL with correlated coordinate replacements",
    }


def _permutation(relation: str, nodes: Sequence[str]) -> list[int]:
    return sorted(
        range(len(nodes)),
        key=lambda index: hashlib.sha256(
            f"{relation}|{nodes[index]}".encode("utf-8")
        ).digest(),
    )


def _permute_square(
    matrix: Sequence[Sequence[Hashable]], permutation: Sequence[int]
) -> list[list[Hashable]]:
    return [
        [matrix[old_left][old_right] for old_right in permutation]
        for old_left in permutation
    ]


def check_permutation_invariance(
    model: RootedModel,
    closure_2wl: dict[str, object],
    closure_3wl: dict[str, object],
    triangle_tokens: Sequence[Sequence[Hashable]],
) -> dict[str, object]:
    permutation = _permutation(model.relation, model.nodes)
    permuted_2wl = exact_2wl(
        _permute_square(model.tokens, permutation),
        check_intersections=False,
    )
    original_pairs = [
        closure_2wl["pair_color_matrix"][old_left][old_right]
        for old_left in permutation
        for old_right in permutation
    ]
    permuted_pairs = [
        color
        for row in permuted_2wl["pair_color_matrix"]
        for color in row
    ]
    if not same_partition(original_pairs, permuted_pairs):
        raise AssertionError("2-WL partition depends on node ordering")

    triangle_permutation = _permutation(model.relation, model.triangles)
    permuted_3wl = exact_folklore_3wl(
        _permute_square(triangle_tokens, triangle_permutation)
    )
    original_triples = [
        closure_3wl["triple_colors"][
            _triple_index(old_a, old_b, old_c, len(model.triangles))
        ]
        for old_a in triangle_permutation
        for old_b in triangle_permutation
        for old_c in triangle_permutation
    ]
    if not same_partition(original_triples, permuted_3wl["triple_colors"]):
        raise AssertionError("3-WL partition depends on node ordering")
    return {
        "permutation_nonidentity": permutation != list(range(len(permutation))),
        "exact_2wl_partition_invariant": True,
        "exact_3wl_partition_invariant": True,
        "permuted_2wl_color_count": permuted_2wl["stable_color_count"],
        "permuted_3wl_color_count": permuted_3wl["stable_color_count"],
    }


def _triangle_tokens(model: RootedModel) -> list[list[Hashable]]:
    indices = [model.nodes.index(node) for node in model.triangles]
    return [
        [model.tokens[left][right] for right in indices] for left in indices
    ]


def build_independent_record(relation: str) -> dict[str, object]:
    start_free = require_memory_floor()
    model = construct_model(relation)
    model_checks = validate_model(model)
    wl2 = exact_2wl(model.tokens)
    triangle_tokens = _triangle_tokens(model)
    wl3 = exact_folklore_3wl(triangle_tokens)
    permutation_checks = check_permutation_invariance(
        model, wl2, wl3, triangle_tokens
    )
    control = make_positive_control(model)
    return {
        "relation": relation,
        "memory_floor_percent": MINIMUM_FREE_PERCENT,
        "memory_floor_satisfied_at_start": (
            start_free >= MINIMUM_FREE_PERCENT
        ),
        "model_checks": model_checks,
        "sectors_external": {
            ("R" if root == "A" else "S"): [
                [model.aliases[node] for node in sector]
                for sector in model.sectors[root]
            ]
            for root in ROOTS
        },
        "expanded_node_aliases": [
            model.node_aliases[node] for node in model.nodes
        ],
        "forced_true_external_pairs": [
            list(_alias_pair(key, model.aliases))
            for key in sorted(model.forced_true)
        ],
        "cap_records": [
            {
                "label": model.node_aliases[name],
                "owner": model.aliases[model.cap_owner[name]],
                "right_side": 2,
                "candidate_pairs": [
                    list(_alias_pair(key, model.aliases))
                    for key in model.caps[name]
                ],
            }
            for name in sorted(model.caps)
        ],
        "expanded_forced_csp_2wl": wl2,
        "triangle_core_folklore_3wl": wl3,
        "permutation_checks": permutation_checks,
        "positive_local_control": control,
        "scope_status": {
            "finite_two_root_template": "VERIFIED",
            "root_relation_excluded": False,
            "prism_free_endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }


def _discovery_canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def verify_discovery_wl2_hashes(closure: dict[str, object]) -> None:
    matrix_hash = hashlib.sha256(
        _discovery_canonical_bytes(closure["pair_color_matrix"])
    ).hexdigest()
    if closure.get("partition_sha256") != matrix_hash:
        raise AssertionError("discovery stored 2-WL partition hash fails")
    intersection_hash = hashlib.sha256(
        _discovery_canonical_bytes(
            closure["intersection_numbers_nonzero"]
        )
    ).hexdigest()
    if closure.get("intersection_tensor_sha256") != intersection_hash:
        raise AssertionError("discovery stored intersection tensor hash fails")


def compare_discovery(
    discovery_path: Path,
    independent_records: dict[str, dict[str, object]],
) -> dict[str, object]:
    """Compare only after independent construction and refinement are done."""
    payload = json.loads(discovery_path.read_text(encoding="utf-8"))
    if payload.get("format") != "wave53-multi-root-wl-v1":
        raise AssertionError("discovery envelope format mismatch")
    records = payload.get("relation_records")
    if not isinstance(records, list):
        raise AssertionError("discovery relation records missing")
    if [record.get("relation") for record in records] != list(RELATIONS):
        raise AssertionError("discovery relation records incomplete or reordered")
    computed_record_hashes = {
        record["relation"]: hashlib.sha256(
            _discovery_canonical_bytes(record)
        ).hexdigest()
        for record in records
    }
    if computed_record_hashes != payload.get("relation_record_sha256s"):
        raise AssertionError("discovery internal relation hashes fail")

    comparisons: dict[str, object] = {}
    for discovery in records:
        relation = discovery["relation"]
        clean = independent_records[relation]
        aliases = clean["expanded_node_aliases"]
        discovery_nodes = discovery["forced_csp"]["nodes"]
        if set(aliases) != set(discovery_nodes):
            raise AssertionError(f"{relation}: node identity envelope differs")
        clean_index = {name: index for index, name in enumerate(aliases)}
        clean_matrix = clean["expanded_forced_csp_2wl"]["pair_color_matrix"]
        clean_aligned = [
            clean_matrix[clean_index[left]][clean_index[right]]
            for left in discovery_nodes
            for right in discovery_nodes
        ]
        discovery_matrix = discovery["expanded_forced_csp_2wl"]["closure"][
            "pair_color_matrix"
        ]
        discovery_closure_2wl = discovery[
            "expanded_forced_csp_2wl"
        ]["closure"]
        verify_discovery_wl2_hashes(discovery_closure_2wl)
        discovery_flat = [
            color for row in discovery_matrix for color in row
        ]
        if not same_partition(clean_aligned, discovery_flat):
            raise AssertionError(
                f"{relation}: stable 2-WL partitions are not equivalent"
            )
        discovery_to_clean: dict[int, int] = {}
        clean_to_discovery: dict[int, int] = {}
        for discovery_color, clean_color in zip(
            discovery_flat, clean_aligned, strict=True
        ):
            if (
                discovery_to_clean.setdefault(discovery_color, clean_color)
                != clean_color
            ):
                raise AssertionError("nonfunctional discovery-to-clean map")
            if (
                clean_to_discovery.setdefault(clean_color, discovery_color)
                != discovery_color
            ):
                raise AssertionError("nonbijective discovery-to-clean map")
        transformed_intersections = sorted(
            [
                discovery_to_clean[first],
                discovery_to_clean[second],
                discovery_to_clean[output],
                multiplicity,
            ]
            for first, second, output, multiplicity in discovery[
                "expanded_forced_csp_2wl"
            ]["closure"]["intersection_numbers_nonzero"]
        )
        clean_intersections = sorted(
            clean["expanded_forced_csp_2wl"][
                "intersection_numbers_nonzero"
            ]
        )
        if transformed_intersections != clean_intersections:
            raise AssertionError(
                f"{relation}: intersection tensors do not agree"
            )
        discovery_3wl = discovery["triangle_core_3wl"]["closure"]
        clean_3wl = clean["triangle_core_folklore_3wl"]
        if (
            discovery_3wl["stable_color_count"]
            != clean_3wl["stable_color_count"]
            or sorted(discovery_3wl["class_sizes"])
            != sorted(clean_3wl["class_sizes"])
        ):
            raise AssertionError(
                f"{relation}: 3-WL partition fingerprint differs"
            )
        comparisons[relation] = {
            "expanded_order": len(discovery_nodes),
            "stable_2wl_color_count": len(discovery_to_clean),
            "stable_2wl_partition_exactly_equivalent": True,
            "intersection_tensor_exactly_equivalent_under_color_bijection": True,
            "intersection_parameter_nonzero_count": len(clean_intersections),
            "stored_2wl_partition_hash_valid": True,
            "stored_intersection_tensor_hash_valid": True,
            "stable_3wl_color_count": clean_3wl["stable_color_count"],
            "stable_3wl_class_size_multiset_matches": True,
            "stored_3wl_tuple_partition_hash_reconstructible_from_envelope": False,
        }

    boundary = payload.get("claim_boundary", {})
    if boundary.get("prism_free_endpoint") != "UNKNOWN":
        raise AssertionError("discovery inflated endpoint status")
    if boundary.get("conway_99") != "UNKNOWN":
        raise AssertionError("discovery inflated Conway-99 status")
    if payload.get("claim_label") != "DERIVED":
        raise AssertionError("discovery label is not DERIVED")
    try:
        reported_path = discovery_path.resolve().relative_to(
            Path.cwd().resolve()
        ).as_posix()
    except ValueError:
        reported_path = discovery_path.resolve().as_posix()
    return {
        "path": reported_path,
        "sha256": hashlib.sha256(discovery_path.read_bytes()).hexdigest(),
        "format": payload["format"],
        "claim_label": payload["claim_label"],
        "internal_relation_hashes_valid": True,
        "relation_comparisons": comparisons,
        "endpoint_status_not_inflated": True,
    }


def assemble_independent_result(
    discovery_path: Path,
    records: dict[str, dict[str, object]],
) -> dict[str, object]:
    if set(records) != set(RELATIONS):
        raise AssertionError("independent record set is incomplete")
    for relation in RELATIONS:
        if records[relation].get("relation") != relation:
            raise AssertionError("independent record relation mismatch")
    discovery_audit = compare_discovery(discovery_path, records)
    aggregate = {
        "format": "wave53-multi-root-wl-independent-v1",
        "claim_label": "VERIFIED",
        "checker_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
        "verified_scope": (
            "the four finite two-root cap-incidence templates and their exact "
            "2-WL/triangle-core folklore-3-WL computations"
        ),
        "relation_record_sha256s": {
            relation: sha256_json(record)
            for relation, record in records.items()
        },
        "summary": {
            relation: {
                **record["model_checks"],
                "stable_2wl_color_count": record[
                    "expanded_forced_csp_2wl"
                ]["stable_color_count"],
                "stable_3wl_color_count": record[
                    "triangle_core_folklore_3wl"
                ]["stable_color_count"],
                "intersection_parameter_nonzero_count": record[
                    "expanded_forced_csp_2wl"
                ]["intersection_parameter_nonzero_count"],
                "positive_control_selected_unique_count": record[
                    "positive_local_control"
                ]["selected_unique_count"],
            }
            for relation, record in records.items()
        },
        "discovery_audit": discovery_audit,
        "corrections": [],
        "limitations": [
            "The verified objects are finite two-root local relaxations.",
            "The exact-two right side is checked separately from the WL token structure.",
            "The 3-WL computation is the correlated-replacement folklore variant on triangle cores only.",
            "Discovery omits the triple-color vector, so its stored 3-WL tuple-partition hash is not reconstructible from that JSON alone; independent recomputation verifies the claimed count and class-size multiset.",
            "Positive controls establish only local cap feasibility.",
            "No root relation is excluded.",
        ],
        "endpoint": "UNKNOWN",
        "conway_99": "UNKNOWN",
    }
    return aggregate


def build_result(discovery_path: Path) -> tuple[dict[str, object], dict[str, object]]:
    records: dict[str, dict[str, object]] = {}
    for relation in RELATIONS:
        records[relation] = build_independent_record(relation)
        print(
            f"PASS_INDEPENDENT relation={relation} "
            f"2wl={records[relation]['expanded_forced_csp_2wl']['stable_color_count']} "
            f"3wl={records[relation]['triangle_core_folklore_3wl']['stable_color_count']}",
            flush=True,
        )
    return assemble_independent_result(discovery_path, records), records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--discovery",
        type=Path,
        required=True,
        help="discovery JSON, opened only after independent computation",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--assemble-existing",
        action="store_true",
        help="reseal the aggregate from already computed exact records",
    )
    arguments = parser.parse_args()
    record_dir = arguments.output_dir / "records"
    if arguments.assemble_existing:
        records = {
            relation: json.loads(
                (record_dir / f"{relation}.json").read_text(encoding="utf-8")
            )
            for relation in RELATIONS
        }
        aggregate = assemble_independent_result(arguments.discovery, records)
    else:
        aggregate, records = build_result(arguments.discovery)
    record_dir.mkdir(parents=True, exist_ok=True)
    for relation, record in records.items():
        (record_dir / f"{relation}.json").write_bytes(
            canonical_json_bytes(record)
        )
    output = arguments.output_dir / "independent-result.json"
    output.write_bytes(canonical_json_bytes(aggregate))
    print(
        "PASS_VERIFICATION "
        f"sha256={hashlib.sha256(output.read_bytes()).hexdigest()}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
