#!/usr/bin/env python3
"""Independent exact verifier for the Wave 52 rooted coherent closure.

This checker does not import the discovery implementation.  It rebuilds the
rooted structures from typed vertices and incidences, runs its own ordered-pair
2-WL refinement, and compares only after the frozen inputs have been checked.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from typing import Hashable, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
FREEZE = Path(__file__).with_name("input-freeze.sha256")
DISCOVERY_RESULT = ROOT / "attempts/wave52-coherent-closure/exact-result.json"
MEMORY_FLOOR_PERCENT = 20.0
SECTORS = (0, 1, 2)
PETALS = tuple(range(6))
SECTOR_PAIRS = ((0, 1), (0, 2), (1, 2))
CYCLE_TYPES = ((6,), (4, 2), (3, 3), (2, 2, 2))


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def verify_input_freeze() -> dict[str, str]:
    frozen: dict[str, str] = {}
    for line in FREEZE.read_text(encoding="ascii").splitlines():
        expected, relative = line.split(maxsplit=1)
        relative = relative.lstrip("*")
        path = ROOT / Path(relative)
        actual = sha256_file(path)
        if actual != expected:
            raise AssertionError(
                f"frozen input drift: {relative}: expected {expected}, got {actual}"
            )
        frozen[relative] = actual
    if frozen["attempts/wave52-coherent-closure/exact-result.json"] != (
        "75951c260b3a0dda55c2acc324fc6c60322778a72eabb049445d3a87f982e2e9"
    ):
        raise AssertionError("unexpected discovery result freeze")
    if frozen["attempts/wave52-coherent-closure/package-manifest.sha256"] != (
        "4b25853eca8ed96f5beea74e4e51ef744259a8436510d23c443b8e3f140692b3"
    ):
        raise AssertionError("unexpected discovery package freeze")
    return frozen


def free_memory_percent() -> float:
    if hasattr(ctypes, "windll"):
        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return 100.0 * status.available_physical / status.total_physical
    return 100.0


def require_memory_floor(floor: float = MEMORY_FLOOR_PERCENT) -> float:
    if floor < MEMORY_FLOOR_PERCENT:
        raise AssertionError("verifier memory floor must not be weakened")
    available = free_memory_percent()
    if available < floor:
        raise MemoryError(
            f"free physical memory {available:.2f}% is below {floor:.2f}%"
        )
    return available


Node = tuple[object, ...]


def node_kind(node: Node) -> str:
    return str(node[0])


def root_node() -> Node:
    return ("root",)


def petal_node(sector: int, index: int) -> Node:
    return ("petal", sector, index)


def candidate_node(s: int, t: int, i: int, j: int) -> Node:
    if not s < t:
        raise ValueError("candidate sectors must be sorted")
    return ("candidate_B", s, t, i, j)


def cap_node(owner_sector: int, target_sector: int, owner: int) -> Node:
    if owner_sector == target_sector:
        raise ValueError("cap sectors must differ")
    return ("cap_exactly_2", owner_sector, target_sector, owner)


def rooted_nodes() -> tuple[Node, ...]:
    return (root_node(),) + tuple(
        petal_node(s, i) for s in SECTORS for i in PETALS
    )


def canonicalize(items: Sequence[Sequence[Hashable]]) -> list[list[int]]:
    unique = sorted({entry for row in items for entry in row})
    number = {entry: i for i, entry in enumerate(unique)}
    return [[number[entry] for entry in row] for row in items]


def refine_2wl(initial_tokens: Sequence[Sequence[Hashable]]) -> dict[str, object]:
    """Run directed 2-WL with exact multiset multiplicities."""

    colors = canonicalize(initial_tokens)
    n = len(colors)
    trajectory = [len({c for row in colors for c in row})]
    rounds = 0
    while True:
        signatures: list[list[Hashable]] = []
        for i in range(n):
            row: list[Hashable] = []
            for j in range(n):
                pairs = Counter((colors[i][k], colors[k][j]) for k in range(n))
                row.append((colors[i][j], tuple(sorted(pairs.items()))))
            signatures.append(row)
        refined = canonicalize(signatures)
        refined_count = len({c for row in refined for c in row})
        if refined_count == trajectory[-1]:
            break
        colors = refined
        trajectory.append(refined_count)
        rounds += 1
    certificate = stable_certificate(colors)
    return {
        "colors": colors,
        "trajectory": trajectory,
        "proper_rounds": rounds,
        "stable_color_count": trajectory[-1],
        "diagonal_class_sizes": diagonal_class_sizes(colors),
        "certificate": certificate,
    }


def diagonal_class_sizes(colors: Sequence[Sequence[int]]) -> list[int]:
    counts = Counter(colors[i][i] for i in range(len(colors)))
    return sorted(counts.values())


def stable_certificate(colors: Sequence[Sequence[int]]) -> dict[str, object]:
    n = len(colors)
    color_count = max(max(row) for row in colors) + 1
    pairs_by_color: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for i in range(n):
        for j in range(n):
            pairs_by_color[colors[i][j]].append((i, j))

    nonzero: list[list[int]] = []
    for c in range(color_count):
        reference: tuple[tuple[tuple[int, int], int], ...] | None = None
        for i, j in pairs_by_color[c]:
            counts = Counter((colors[i][k], colors[k][j]) for k in range(n))
            encoded = tuple(sorted(counts.items()))
            if reference is None:
                reference = encoded
            elif encoded != reference:
                raise AssertionError(f"2-WL color {c} has nonconstant intersections")
        if reference is None:
            raise AssertionError(f"empty color {c}")
        for (a, b), value in reference:
            nonzero.append([c, a, b, value])

    payload = {
        "order": n,
        "stable_color_count": color_count,
        "class_sizes": [len(pairs_by_color[c]) for c in range(color_count)],
        "intersection_nonzero": nonzero,
    }
    return {
        **payload,
        "fingerprint_sha256": hashlib.sha256(canonical_bytes(payload)).hexdigest(),
        "nonzero_parameter_count": len(nonzero),
    }


def partial_tokens() -> tuple[tuple[Node, ...], list[list[Hashable]]]:
    nodes = rooted_nodes()

    def relation(left: Node, right: Node) -> str:
        if left == right:
            return "diag"
        if node_kind(left) == "root" or node_kind(right) == "root":
            return "K"
        if left[1] == right[1]:
            return "K"
        return "cross_unselected"

    tokens = [
        [(node_kind(left), node_kind(right), relation(left, right)) for right in nodes]
        for left in nodes
    ]
    return nodes, tokens


def expected_candidate_endpoints(edge: Node) -> frozenset[Node]:
    _, s, t, i, j = edge
    return frozenset((petal_node(int(s), int(i)), petal_node(int(t), int(j))))


def expected_candidate_caps(edge: Node) -> frozenset[Node]:
    _, s, t, i, j = edge
    return frozenset(
        (
            cap_node(int(s), int(t), int(i)),
            cap_node(int(t), int(s), int(j)),
        )
    )


def expected_cap_owner(cap: Node) -> Node:
    _, s, _t, i = cap
    return petal_node(int(s), int(i))


def build_constraint_template() -> dict[str, object]:
    triangles = rooted_nodes()
    candidates = tuple(
        candidate_node(s, t, i, j)
        for s, t in SECTOR_PAIRS
        for i in PETALS
        for j in PETALS
    )
    caps = tuple(
        cap_node(s, t, i)
        for s in SECTORS
        for t in SECTORS
        if s != t
        for i in PETALS
    )
    nodes = triangles + candidates + caps
    endpoints = {edge: expected_candidate_endpoints(edge) for edge in candidates}
    edge_caps = {edge: expected_candidate_caps(edge) for edge in candidates}
    owners = {cap: expected_cap_owner(cap) for cap in caps}
    validate_template(nodes, endpoints, edge_caps, owners)

    def relation(left: Node, right: Node) -> str:
        if left == right:
            return "diag"
        lk, rk = node_kind(left), node_kind(right)
        if {lk, rk} == {"root", "petal"}:
            return "K"
        if lk == rk == "petal":
            return "K" if left[1] == right[1] else "cross_unselected"
        if lk == "candidate_B" and right in endpoints[left]:
            return "candidate_endpoint"
        if rk == "candidate_B" and left in endpoints[right]:
            return "candidate_endpoint"
        if lk == "candidate_B" and right in edge_caps[left]:
            return "candidate_in_cap"
        if rk == "candidate_B" and left in edge_caps[right]:
            return "candidate_in_cap"
        if lk == "cap_exactly_2" and owners[left] == right:
            return "cap_owner"
        if rk == "cap_exactly_2" and owners[right] == left:
            return "cap_owner"
        return "none"

    tokens = [
        [(node_kind(left), node_kind(right), relation(left, right)) for right in nodes]
        for left in nodes
    ]
    return {
        "nodes": nodes,
        "candidates": candidates,
        "caps": caps,
        "endpoints": endpoints,
        "edge_caps": edge_caps,
        "owners": owners,
        "tokens": tokens,
    }


def validate_template(
    nodes: Sequence[Node],
    endpoints: dict[Node, frozenset[Node]],
    edge_caps: dict[Node, frozenset[Node]],
    owners: dict[Node, Node],
) -> None:
    kind_counts = Counter(map(node_kind, nodes))
    expected_counts = {
        "root": 1,
        "petal": 18,
        "candidate_B": 108,
        "cap_exactly_2": 36,
    }
    if dict(kind_counts) != expected_counts:
        raise AssertionError(f"wrong template node counts: {dict(kind_counts)}")
    candidates = [node for node in nodes if node_kind(node) == "candidate_B"]
    caps = [node for node in nodes if node_kind(node) == "cap_exactly_2"]
    for edge in candidates:
        if endpoints.get(edge) != expected_candidate_endpoints(edge):
            raise AssertionError(f"wrong or duplicate candidate endpoint: {edge}")
        if edge_caps.get(edge) != expected_candidate_caps(edge):
            raise AssertionError(f"wrong candidate-cap incidence: {edge}")
    cap_members = Counter(cap for edge in candidates for cap in edge_caps[edge])
    if any(cap_members[cap] != 6 for cap in caps):
        raise AssertionError("a cap does not contain six candidates")
    if any(owners.get(cap) != expected_cap_owner(cap) for cap in caps):
        raise AssertionError("wrong cap owner")


def two_factor(parts: Sequence[int]) -> tuple[tuple[int, int], ...]:
    if tuple(sorted(parts, reverse=True)) not in CYCLE_TYPES:
        raise AssertionError(f"invalid simple bipartite 2-factor type: {parts}")
    edges: list[tuple[int, int]] = []
    offset = 0
    for length in parts:
        block = tuple(range(offset, offset + length))
        for position, left in enumerate(block):
            edges.append((left, block[position]))
            edges.append((left, block[(position + 1) % length]))
        offset += length
    validate_two_factor(edges)
    return tuple(edges)


def validate_two_factor(edges: Iterable[tuple[int, int]]) -> None:
    edge_list = list(edges)
    if len(edge_list) != 12 or len(set(edge_list)) != 12:
        raise AssertionError("factor must have twelve distinct edges")
    left = Counter(a for a, _ in edge_list)
    right = Counter(b for _, b in edge_list)
    if left != Counter({i: 2 for i in PETALS}):
        raise AssertionError("left endpoints are not all degree two")
    if right != Counter({i: 2 for i in PETALS}):
        raise AssertionError("right endpoints are not all degree two")


def completed_tokens(
    profile: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]
) -> tuple[tuple[Node, ...], list[list[Hashable]], frozenset[Node]]:
    selected: set[Node] = set()
    for (s, t), parts in zip(SECTOR_PAIRS, profile, strict=True):
        for i, j in two_factor(parts):
            selected.add(candidate_node(s, t, i, j))
    nodes = rooted_nodes()

    def relation(left: Node, right: Node) -> str:
        if left == right:
            return "diag"
        lk, rk = node_kind(left), node_kind(right)
        if lk == "root" or rk == "root":
            return "K"
        if left[1] == right[1]:
            return "K"
        s, i = int(left[1]), int(left[2])
        t, j = int(right[1]), int(right[2])
        if s > t:
            s, t, i, j = t, s, j, i
        return "B" if candidate_node(s, t, i, j) in selected else "C"

    tokens = [
        [(node_kind(left), node_kind(right), relation(left, right)) for right in nodes]
        for left in nodes
    ]
    return nodes, tokens, frozenset(selected)


def check_selected_caps(selected: frozenset[Node], template: dict[str, object]) -> None:
    edge_caps = template["edge_caps"]
    caps = template["caps"]
    assert isinstance(edge_caps, dict)
    counts = Counter(cap for edge in selected for cap in edge_caps[edge])
    if any(counts[cap] != 2 for cap in caps):
        raise AssertionError("selected completion violates an exact-two cap")


def derive_local_arithmetic() -> dict[str, object]:
    # A vertex neighborhood is a matching of seven edges because k=14 and
    # lambda=1.  One of those seven triangles is the root.
    triangles_through_each_root_vertex = 14 // 2
    petals_per_sector = triangles_through_each_root_vertex - 1
    rooted_petals = 3 * petals_per_sector
    if (triangles_through_each_root_vertex, petals_per_sector, rooted_petals) != (
        7,
        6,
        18,
    ):
        raise AssertionError("root-sector arithmetic failed")

    total_triangles = 99 * 14 // 6
    disjoint_from_root = total_triangles - 1 - rooted_petals
    root_to_outside_edges = 3 * (14 - 2)
    total_cross_edge_incidences = root_to_outside_edges * 6
    cross_edge_pairs = 3 * (14 - 2)

    # At the prism-free endpoint q is 0, 1, or 2.  If d,c,b count these
    # relations, then d+c+b=212, c+2b=216, and b=36.
    b = cross_edge_pairs
    c = total_cross_edge_incidences - 2 * b
    d = disjoint_from_root - b - c
    if (total_triangles, disjoint_from_root, d, c, b) != (231, 212, 32, 144, 36):
        raise AssertionError("global relation valencies failed")

    return {
        "vertex_neighborhood_matching_edges": triangles_through_each_root_vertex,
        "petals_per_root_vertex": petals_per_sector,
        "rooted_petal_partition": [6, 6, 6],
        "rooted_K_graph": "3K6",
        "global_triangle_count": total_triangles,
        "global_relation_valencies_I_K_D_C_B": [1, 18, d, c, b],
        "global_cross_edge_moment": {
            "d_plus_c_plus_b": disjoint_from_root,
            "c_plus_2b": total_cross_edge_incidences,
            "b_at_prism_free_endpoint": cross_edge_pairs,
        },
        "per_petal_per_opposite_sector": {"B": 2, "C": 4, "D": 0},
        "per_petal_across_both_opposite_sectors": {"B": 4, "C": 8, "D": 0},
    }


def hostile_mutations(template: dict[str, object]) -> dict[str, bool]:
    detected: dict[str, bool] = {}

    deleted = list(two_factor((6,)))
    deleted.pop()
    try:
        validate_two_factor(deleted)
    except AssertionError:
        detected["deleted_B_edge"] = True

    duplicated = list(two_factor((6,)))
    duplicated[-1] = duplicated[0]
    try:
        validate_two_factor(duplicated)
    except AssertionError:
        detected["duplicated_B_endpoint_pair"] = True

    nodes = template["nodes"]
    endpoints = dict(template["endpoints"])
    edge_caps = dict(template["edge_caps"])
    owners = dict(template["owners"])
    first_edge = next(iter(edge_caps))
    correct = edge_caps[first_edge]
    wrong = next(cap for cap in template["caps"] if cap not in correct)
    edge_caps[first_edge] = frozenset((next(iter(correct)), wrong))
    try:
        validate_template(nodes, endpoints, edge_caps, owners)
    except AssertionError:
        detected["changed_cap_incidence"] = True

    bad_endpoints = dict(template["endpoints"])
    endpoint = next(iter(bad_endpoints[first_edge]))
    bad_endpoints[first_edge] = frozenset((endpoint,))
    try:
        validate_template(nodes, bad_endpoints, template["edge_caps"], owners)
    except AssertionError:
        detected["duplicated_candidate_endpoint"] = True

    try:
        require_memory_floor(MEMORY_FLOOR_PERCENT - 1.0)
    except AssertionError:
        detected["weakened_memory_floor"] = True

    expected = {
        "deleted_B_edge",
        "duplicated_B_endpoint_pair",
        "changed_cap_incidence",
        "duplicated_candidate_endpoint",
        "weakened_memory_floor",
    }
    if set(detected) != expected or not all(detected.values()):
        raise AssertionError(f"hostile mutation escaped: {expected - set(detected)}")
    return detected


def compare_discovery(
    discovery: dict[str, object],
    partial: dict[str, object],
    template_wl: dict[str, object],
    records: list[dict[str, object]],
    distinct_fingerprints: int,
) -> dict[str, object]:
    if discovery["claim_label"] != "DERIVED":
        raise AssertionError("discovery label changed")
    if discovery["claim_boundary"]["conway_99"] != "UNKNOWN":
        raise AssertionError("discovery status inflation")
    if discovery["claim_boundary"]["prism_free_endpoint"] != "UNKNOWN":
        raise AssertionError("endpoint status inflation")
    if discovery["frozen_relations"]["global_valencies"] != [1, 18, 32, 144, 36]:
        raise AssertionError("discovery global valencies disagree")

    discovery_partial = discovery["partial_19_triangle_closure"]["closure"]
    if discovery_partial["color_counts"] != partial["trajectory"]:
        raise AssertionError("partial 2-WL trajectory mismatch")
    if sorted(discovery["partial_19_triangle_closure"]["diagonal_class_sizes"]) != (
        partial["diagonal_class_sizes"]
    ):
        raise AssertionError("partial diagonal classes mismatch")

    discovery_template = discovery["completion_free_constraint_template"]["closure"]
    if discovery_template["color_counts"] != template_wl["trajectory"]:
        raise AssertionError("constraint-template 2-WL trajectory mismatch")
    if sorted(
        discovery["completion_free_constraint_template"]["diagonal_class_sizes"]
    ) != template_wl["diagonal_class_sizes"]:
        raise AssertionError("constraint-template diagonal classes mismatch")
    if sorted(discovery_template["class_sizes"]) != sorted(
        template_wl["certificate"]["class_sizes"]
    ):
        raise AssertionError("constraint-template color class sizes mismatch")
    if (
        discovery_template["intersection_parameter_nonzero_count"]
        != template_wl["certificate"]["nonzero_parameter_count"]
    ):
        raise AssertionError("constraint-template intersection tensor size mismatch")

    discovered_records = discovery["canonical_completion_diagnostic"]["records"]
    if len(discovered_records) != 64 or len(records) != 64:
        raise AssertionError("wrong canonical profile count")
    by_profile = {
        tuple(tuple(part) for part in record["profile"]): record
        for record in discovered_records
    }
    for record in records:
        profile = tuple(tuple(part) for part in record["profile"])
        observed = by_profile[profile]
        if observed["closure"]["stable_color_count"] != record["stable_color_count"]:
            raise AssertionError(f"completed stable color mismatch: {profile}")
        if observed["closure"]["proper_refinement_rounds"] != record["proper_rounds"]:
            raise AssertionError(f"completed round mismatch: {profile}")

    # Compare the entire equivalence relation on the 64 fingerprints, rather
    # than expecting two independent implementations to assign the same hash.
    ours = [record["fingerprint_sha256"] for record in records]
    theirs = [
        by_profile[tuple(tuple(part) for part in record["profile"])]["closure"][
            "invariant_fingerprint_sha256"
        ]
        for record in records
    ]
    for i in range(64):
        for j in range(64):
            if (ours[i] == ours[j]) != (theirs[i] == theirs[j]):
                raise AssertionError(f"fingerprint partition mismatch at {i},{j}")
    if distinct_fingerprints != 39:
        raise AssertionError("independent fingerprint count is not 39")
    if discovery["canonical_completion_diagnostic"][
        "distinct_invariant_fingerprint_count"
    ] != distinct_fingerprints:
        raise AssertionError("discovery fingerprint count mismatch")
    return {
        "partial_trajectory_match": True,
        "constraint_template_trajectory_match": True,
        "constraint_template_color_class_sizes_match": True,
        "constraint_template_intersection_tensor_size_match": True,
        "all_64_stable_color_counts_and_rounds_match": True,
        "all_4096_fingerprint_equivalences_match": True,
    }


def build_result() -> dict[str, object]:
    memory_at_start = require_memory_floor()
    frozen = verify_input_freeze()
    arithmetic = derive_local_arithmetic()

    partial_nodes, partial_initial = partial_tokens()
    partial = refine_2wl(partial_initial)
    if len(partial_nodes) != 19 or partial["trajectory"] != [6]:
        raise AssertionError("unexpected partial rooted closure")
    if partial["diagonal_class_sizes"] != [1, 18]:
        raise AssertionError("unexpected partial diagonal classes")

    template = build_constraint_template()
    template_wl = refine_2wl(template["tokens"])
    if len(template["nodes"]) != 163:
        raise AssertionError("unexpected constraint-template order")
    if template_wl["trajectory"] != [26, 38, 47]:
        raise AssertionError("unexpected constraint-template trajectory")
    if template_wl["diagonal_class_sizes"] != [1, 18, 36, 108]:
        raise AssertionError("unexpected constraint-template diagonal classes")

    records: list[dict[str, object]] = []
    for profile in product(CYCLE_TYPES, repeat=3):
        _nodes, initial, selected = completed_tokens(profile)
        check_selected_caps(selected, template)
        closure = refine_2wl(initial)
        records.append(
            {
                "profile": [list(part) for part in profile],
                "stable_color_count": closure["stable_color_count"],
                "proper_rounds": closure["proper_rounds"],
                "fingerprint_sha256": closure["certificate"]["fingerprint_sha256"],
                "selected_B_edges": len(selected),
                "all_36_caps_equal_two": True,
            }
        )

    fingerprint_count = len({r["fingerprint_sha256"] for r in records})
    color_counts = [int(r["stable_color_count"]) for r in records]
    profile_map = {
        tuple(tuple(part) for part in record["profile"]): record for record in records
    }
    if fingerprint_count != 39:
        raise AssertionError(f"expected 39 fingerprints, got {fingerprint_count}")
    if (min(color_counts), max(color_counts)) != (8, 361):
        raise AssertionError("unexpected completed color-count range")
    if profile_map[((6,), (6,), (6,))]["stable_color_count"] != 13:
        raise AssertionError("all-6 profile should have 13 stable colors")
    if profile_map[((2, 2, 2),) * 3]["stable_color_count"] != 8:
        raise AssertionError("all-222 profile should have 8 stable colors")

    mutations = hostile_mutations(template)

    # Comparison is deliberately last: every preceding calculation was made
    # from the prose-level typed incidence specification.
    discovery = json.loads(DISCOVERY_RESULT.read_text(encoding="utf-8"))
    comparison = compare_discovery(
        discovery, partial, template_wl, records, fingerprint_count
    )
    memory_at_end = require_memory_floor()

    return {
        "format": "wave52-independent-coherent-closure-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "Independent exact verification of the one-root, prism-free "
            "completion-free coherent-closure experiment only"
        ),
        "input_freeze": frozen,
        "independent_derivation": arithmetic,
        "partial_19_triangle_closure": {
            "order": 19,
            "trajectory": partial["trajectory"],
            "proper_rounds": partial["proper_rounds"],
            "stable_color_count": partial["stable_color_count"],
            "diagonal_class_sizes": partial["diagonal_class_sizes"],
            "class_sizes_sorted": sorted(partial["certificate"]["class_sizes"]),
            "nonzero_intersection_parameters": partial["certificate"][
                "nonzero_parameter_count"
            ],
            "fingerprint_sha256": partial["certificate"]["fingerprint_sha256"],
        },
        "completion_free_constraint_template": {
            "node_counts": dict(Counter(map(node_kind, template["nodes"]))),
            "order": 163,
            "trajectory": template_wl["trajectory"],
            "proper_rounds": template_wl["proper_rounds"],
            "stable_color_count": template_wl["stable_color_count"],
            "diagonal_class_sizes": template_wl["diagonal_class_sizes"],
            "class_sizes_sorted": sorted(template_wl["certificate"]["class_sizes"]),
            "nonzero_intersection_parameters": template_wl["certificate"][
                "nonzero_parameter_count"
            ],
            "fingerprint_sha256": template_wl["certificate"]["fingerprint_sha256"],
        },
        "canonical_completion_diagnostic": {
            "profile_count": len(records),
            "distinct_fingerprint_count": fingerprint_count,
            "stable_color_count_range": [min(color_counts), max(color_counts)],
            "all_6_stable_color_count": profile_map[((6,),) * 3][
                "stable_color_count"
            ],
            "all_222_stable_color_count": profile_map[((2, 2, 2),) * 3][
                "stable_color_count"
            ],
            "positive_integral_cap_completions": True,
            "records": records,
        },
        "hostile_mutations_detected": mutations,
        "comparison": comparison,
        "memory": {
            "enforced_floor_percent": MEMORY_FLOOR_PERCENT,
            "free_at_both_checks_at_least_floor": (
                memory_at_start >= MEMORY_FLOOR_PERCENT
                and memory_at_end >= MEMORY_FLOOR_PERCENT
            ),
        },
        "disposition": {
            "rooted_local_claims": "VERIFIED",
            "completed_closure_depends_on_arbitrary_B_choice": True,
            "new_forced_obstruction": False,
            "global_graph_constructed": False,
            "improved_n3_upper_bound": False,
            "prism_free_endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The verified scope is one root triangle and its 18 K-neighbors.",
            "The 163-node object is an incidence template, not a Boolean CSP solver.",
            "The 64 profile triples are canonical diagnostics, not all labelled joint completions.",
            "An integral local cap completion need not lift to a 99-vertex graph.",
            "No graph automorphism, transitivity, or association scheme is assumed.",
            "No endpoint exclusion, construction, or improved upper bound follows.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if bool(args.output) == bool(args.verify):
        parser.error("choose exactly one of --output or --verify")

    result = build_result()
    encoded = canonical_bytes(result)
    if args.output:
        args.output.write_bytes(encoded)
        print(
            "PASS_INDEPENDENT_WAVE52 "
            f"sha256={hashlib.sha256(encoded).hexdigest()} "
            "endpoint=UNKNOWN"
        )
        return 0
    actual = args.verify.read_bytes()
    if actual != encoded:
        raise AssertionError(
            f"independent result drift: expected {hashlib.sha256(encoded).hexdigest()}, "
            f"got {hashlib.sha256(actual).hexdigest()}"
        )
    print(
        "PASS_INDEPENDENT_WAVE52_REPLAY "
        f"sha256={hashlib.sha256(actual).hexdigest()} endpoint=UNKNOWN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
