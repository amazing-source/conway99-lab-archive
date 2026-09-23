#!/usr/bin/env python3
"""Independent finite audit for the conditional n3=33 equality case.

The script deliberately uses only the Python standard library.  It reads the
House of Graphs connected quartic order-11 graph6 catalog, adds the unique
disconnected quartic graph of order 11, enumerates all admissible point-clique
families for the three resource profiles, and then tests the exact support
constraints from Waves 6--8.

No solver exit code is used as a certificate: the support layer is a direct
backtracking enumeration with independently rechecked terminal states.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import itertools
import json
import platform
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


N = 11
K_EDGE_COUNT = 22
L_EDGE_COUNT = 33
ALLOWED_NONZERO_H_DEGREES = frozenset((4, 6, 8, 10, 12))
MANTEL_SUPPORT_MINIMUM = 12

Edge = tuple[int, int]
Clique = tuple[int, ...]
Graph = tuple[int, ...]  # adjacency bit masks


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_gzip_payload(path: Path) -> str:
    digest = hashlib.sha256()
    with gzip.open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def edge(a: int, b: int) -> Edge:
    return (a, b) if a < b else (b, a)


def edges_of(graph: Graph) -> tuple[Edge, ...]:
    return tuple(
        (left, right)
        for right in range(N)
        for left in range(right)
        if graph[left] >> right & 1
    )


def decode_graph6(line: str) -> Graph:
    """Decode an ordinary graph6 string of order at most 62."""

    data = line.strip()
    if data.startswith(">>graph6<<"):
        data = data[len(">>graph6<<") :]
    if not data or data[0] == "~":
        raise ValueError("only short graph6 headers are supported")
    order = ord(data[0]) - 63
    if order != N:
        raise ValueError(f"expected graph order {N}, got {order}")
    bits: list[int] = []
    for char in data[1:]:
        value = ord(char) - 63
        if not 0 <= value < 64:
            raise ValueError("invalid graph6 character")
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    needed = order * (order - 1) // 2
    if len(bits) < needed:
        raise ValueError("truncated graph6 string")
    adjacency = [0] * order
    position = 0
    for right in range(1, order):
        for left in range(right):
            if bits[position]:
                adjacency[left] |= 1 << right
                adjacency[right] |= 1 << left
            position += 1
    return tuple(adjacency)


def encode_graph6(graph: Graph) -> str:
    bits = [
        (graph[left] >> right) & 1
        for right in range(1, N)
        for left in range(right)
    ]
    bits.extend([0] * ((-len(bits)) % 6))
    payload = "".join(
        chr(63 + sum(bits[start + offset] << (5 - offset) for offset in range(6)))
        for start in range(0, len(bits), 6)
    )
    return chr(63 + N) + payload


def is_connected(graph: Graph) -> bool:
    seen = 1
    frontier = 1
    while frontier:
        vertex_bit = frontier & -frontier
        frontier ^= vertex_bit
        vertex = vertex_bit.bit_length() - 1
        new = graph[vertex] & ~seen
        seen |= new
        frontier |= new
    return seen == (1 << N) - 1


def validate_quartic(graph: Graph) -> None:
    if len(graph) != N:
        raise AssertionError("wrong graph order")
    if any(mask >> N for mask in graph):
        raise AssertionError("adjacency outside vertex range")
    for vertex, mask in enumerate(graph):
        if mask >> vertex & 1:
            raise AssertionError("loop")
        if mask.bit_count() != 4:
            raise AssertionError("not 4-regular")
        for other in range(N):
            if ((mask >> other) & 1) != ((graph[other] >> vertex) & 1):
                raise AssertionError("asymmetric adjacency")
    if len(edges_of(graph)) != K_EDGE_COUNT:
        raise AssertionError("wrong edge count")


def disconnected_quartic() -> Graph:
    """K5 disjoint union the unique quartic graph on six vertices (K6-M)."""

    adjacency = [0] * N
    for left in range(5):
        for right in range(left + 1, 5):
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    missing = {edge(5, 6), edge(7, 8), edge(9, 10)}
    for left in range(5, N):
        for right in range(left + 1, N):
            if (left, right) not in missing:
                adjacency[left] |= 1 << right
                adjacency[right] |= 1 << left
    result = tuple(adjacency)
    validate_quartic(result)
    if is_connected(result):
        raise AssertionError("disconnected graph construction failed")
    return result


def read_catalog(path: Path) -> tuple[list[str], list[Graph]]:
    with gzip.open(path, "rt", encoding="ascii") as handle:
        labels = [line.strip() for line in handle if line.strip()]
    if len(labels) != 265 or len(set(labels)) != 265:
        raise AssertionError(f"expected 265 unique connected labels, got {len(labels)}")
    graphs = [decode_graph6(label) for label in labels]
    for label, graph in zip(labels, graphs):
        validate_quartic(graph)
        if not is_connected(graph):
            raise AssertionError("catalog contains a disconnected graph")
        if encode_graph6(graph) != label:
            # This check only catches decoder/encoder disagreement; graph6
            # labels need not be canonical for arbitrary inputs.
            raise AssertionError("graph6 round trip failed")
    extra = disconnected_quartic()
    labels.append(encode_graph6(extra))
    graphs.append(extra)
    return labels, graphs


def clique_mask(clique: Clique, edge_index: dict[Edge, int]) -> int:
    return sum(1 << edge_index[edge(*pair)] for pair in itertools.combinations(clique, 2))


def graph_cliques(graph: Graph, size: int) -> tuple[Clique, ...]:
    return tuple(
        vertices
        for vertices in itertools.combinations(range(N), size)
        if all(graph[left] >> right & 1 for left, right in itertools.combinations(vertices, 2))
    )


def enumerate_f_factors(
    available_edges: tuple[Edge, ...], demands: tuple[int, ...]
) -> Iterator[tuple[Edge, ...]]:
    """Enumerate every edge subset meeting the exact vertex demands once."""

    def recurse(edges: tuple[Edge, ...], residual: tuple[int, ...]) -> Iterator[tuple[Edge, ...]]:
        if not any(residual):
            yield ()
            return

        incident: list[list[int]] = [[] for _ in range(N)]
        for index, (left, right) in enumerate(edges):
            if residual[left] and residual[right]:
                incident[left].append(index)
                incident[right].append(index)
        positive = [vertex for vertex in range(N) if residual[vertex]]
        if any(len(incident[vertex]) < residual[vertex] for vertex in positive):
            return
        # Processing every edge incident with one residual vertex gives a
        # duplicate-free exact recursion.  Most-constrained first is faster.
        vertex = min(positive, key=lambda item: (len(incident[item]) - residual[item], len(incident[item]), item))
        needed = residual[vertex]
        for chosen_indices in itertools.combinations(incident[vertex], needed):
            chosen_set = set(chosen_indices)
            chosen_edges = tuple(edges[index] for index in chosen_indices)
            new_residual = list(residual)
            new_residual[vertex] = 0
            valid = True
            for left, right in chosen_edges:
                other = right if left == vertex else left
                new_residual[other] -= 1
                if new_residual[other] < 0:
                    valid = False
                    break
            if not valid:
                continue
            remaining = tuple(
                current
                for index, current in enumerate(edges)
                if vertex not in current
                and index not in chosen_set
                and new_residual[current[0]]
                and new_residual[current[1]]
            )
            available_degree = [0] * N
            for left, right in remaining:
                available_degree[left] += 1
                available_degree[right] += 1
            if any(new_residual[item] > available_degree[item] for item in range(N)):
                continue
            for suffix in recurse(remaining, tuple(new_residual)):
                yield chosen_edges + suffix

    yield from recurse(available_edges, demands)


@dataclass(frozen=True)
class PointFamily:
    profile: str
    points: tuple[Clique, ...]


def enumerate_point_families(graph: Graph) -> Iterator[PointFamily]:
    k_edges = edges_of(graph)
    edge_index = {item: index for index, item in enumerate(k_edges)}
    triangles = graph_cliques(graph, 3)
    four_cliques = graph_cliques(graph, 4)
    triangle_masks = {item: clique_mask(item, edge_index) for item in triangles}
    four_masks = {item: clique_mask(item, edge_index) for item in four_cliques}

    # (profile label, number of central K3 points, number of central K4 points)
    profiles = (("A", 3, 0), ("B", 1, 1), ("C", 1, 0))
    for profile, triangle_count, four_count in profiles:
        for selected_triangles in itertools.combinations(triangles, triangle_count):
            used = 0
            triangles_disjoint = True
            for item in selected_triangles:
                mask = triangle_masks[item]
                if used & mask:
                    triangles_disjoint = False
                    break
                used |= mask
            if not triangles_disjoint:
                continue
            for selected_fours in itertools.combinations(four_cliques, four_count):
                central = selected_triangles + selected_fours
                central_used = used
                valid = True
                for item in selected_fours:
                    mask = four_masks[item]
                    if central_used & mask:
                        valid = False
                        break
                    central_used |= mask
                if not valid:
                    continue

                loads = [0] * N
                for item in central:
                    for vertex in item:
                        loads[vertex] += 1
                demands = tuple(3 - load for load in loads)
                if any(value < 0 for value in demands) or sum(demands) % 2:
                    continue
                available = tuple(
                    item for index, item in enumerate(k_edges) if not (central_used >> index & 1)
                )
                for factor in enumerate_f_factors(available, demands):
                    factor_mask = sum(1 << edge_index[item] for item in factor)
                    all_used = central_used | factor_mask
                    # A fully realized K-triangle must be a common-point
                    # triangle contained in one of the selected central points.
                    if any(
                        all_used & triangle_masks[item] == triangle_masks[item]
                        and not any(set(item) <= set(center) for center in central)
                        for item in triangles
                    ):
                        continue
                    points = tuple(sorted(central + tuple(factor), key=lambda item: (len(item), item)))
                    yield PointFamily(profile, points)


@dataclass(frozen=True)
class Candidate:
    first: int
    second: int
    coverage: int
    degree: int
    internal: bool


@dataclass
class SupportInstance:
    family: PointFamily
    l_edges: tuple[Edge, ...]
    candidates: tuple[Candidate, ...]
    required_mask: int
    coverers: tuple[int, ...]
    conflicts: tuple[int, ...]
    triangle_forbidden: tuple[int, ...]
    incident: tuple[int, ...]
    external_incident: tuple[int, ...]
    targets: tuple[int, ...]
    capacities: tuple[int, ...]


def make_support_instance(graph: Graph, family: PointFamily) -> tuple[SupportInstance | None, str]:
    k_edge_set = set(edges_of(graph))
    l_edges = tuple(
        (left, right)
        for right in range(N)
        for left in range(right)
        if (left, right) not in k_edge_set
    )
    if len(l_edges) != L_EDGE_COUNT:
        raise AssertionError("wrong L edge count")
    l_index = {item: index for index, item in enumerate(l_edges)}
    points = family.points
    point_sets = tuple(frozenset(item) for item in points)

    at_triangle = [
        tuple(index for index, point in enumerate(point_sets) if triangle in point)
        for triangle in range(N)
    ]
    if any(len(items) != 3 for items in at_triangle):
        raise AssertionError("each active triangle must have exactly three points")
    if any(len(point_sets[first] & point_sets[second]) > 1 for first, second in itertools.combinations(range(len(points)), 2)):
        raise AssertionError("two points share more than one active triangle")

    forced_pairs = {
        edge(first, second)
        for items in at_triangle
        for first, second in itertools.combinations(items, 2)
    }
    if len(forced_pairs) != N * 3:
        raise AssertionError("internal graph-edge count is not 33")

    def coverage(first: int, second: int) -> int:
        left = point_sets[first]
        right = point_sets[second]
        return sum(
            1 << index
            for index, (a, b) in enumerate(l_edges)
            if (a in left and b in right) or (b in left and a in right)
        )

    pair_data: dict[Edge, tuple[int, int, bool]] = {}
    for first, second in itertools.combinations(range(len(points)), 2):
        mask = coverage(first, second)
        degree = mask.bit_count()
        internal = bool(point_sets[first] & point_sets[second])
        pair_data[(first, second)] = (mask, degree, internal)
        if (first, second) in forced_pairs:
            if degree not in ALLOWED_NONZERO_H_DEGREES | {0}:
                return None, "forced_internal_bad_degree"
            if degree and any(
                sum(1 for l_edge_index in range(L_EDGE_COUNT) if mask >> l_edge_index & 1 and triangle in l_edges[l_edge_index]) not in (0, 2)
                for triangle in range(N)
            ):
                return None, "forced_internal_bad_fixed_side"

    candidates: list[Candidate] = []
    for (first, second), (mask, degree, internal) in pair_data.items():
        if degree in ALLOWED_NONZERO_H_DEGREES and all(
            sum(1 for index, item in enumerate(l_edges) if mask >> index & 1 and triangle in item) in (0, 2)
            for triangle in range(N)
        ):
            candidates.append(Candidate(first, second, mask, degree, internal))

    candidate_index = {(item.first, item.second): index for index, item in enumerate(candidates)}
    required_positive = {
        pair for pair in forced_pairs if pair_data[pair][1]
    }
    if any(pair not in candidate_index for pair in required_positive):
        return None, "required_pair_not_candidate"
    required_mask = sum(1 << candidate_index[pair] for pair in required_positive)

    if len(candidates) < MANTEL_SUPPORT_MINIMUM:
        return None, "candidate_pool_below_mantel"
    coverers = tuple(
        sum(1 << index for index, item in enumerate(candidates) if item.coverage >> l_index & 1)
        for l_index in range(L_EDGE_COUNT)
    )
    if any(mask.bit_count() < 2 for mask in coverers):
        return None, "l_edge_has_fewer_than_two_coverers"

    conflicts = [0] * len(candidates)
    adjacency = [0] * len(candidates)
    for first, second in itertools.combinations(range(len(candidates)), 2):
        left = candidates[first]
        right = candidates[second]
        shared = left.coverage & right.coverage
        same_endpoint = bool({left.first, left.second} & {right.first, right.second})
        if (shared and same_endpoint) or shared.bit_count() > 1:
            conflicts[first] |= 1 << second
            conflicts[second] |= 1 << first
        if shared.bit_count() == 1:
            adjacency[first] |= 1 << second
            adjacency[second] |= 1 << first
    triangle_forbidden = tuple(
        (1 << first) | (1 << second) | (1 << third)
        for first, second, third in itertools.combinations(range(len(candidates)), 3)
        if adjacency[first] >> second & 1
        and adjacency[first] >> third & 1
        and adjacency[second] >> third & 1
    )
    incident = tuple(
        sum(1 << index for index, item in enumerate(candidates) if point in (item.first, item.second))
        for point in range(len(points))
    )
    external_incident = tuple(
        sum(
            1 << index
            for index, item in enumerate(candidates)
            if point in (item.first, item.second) and not item.internal
        )
        for point in range(len(points))
    )
    targets = tuple(4 * len(item) for item in points)
    capacities = tuple(14 - 2 * len(item) for item in points)
    return (
        SupportInstance(
            family=family,
            l_edges=l_edges,
            candidates=tuple(candidates),
            required_mask=required_mask,
            coverers=coverers,
            conflicts=tuple(conflicts),
            triangle_forbidden=triangle_forbidden,
            incident=incident,
            external_incident=external_incident,
            targets=targets,
            capacities=capacities,
        ),
        "ok",
    )


def forced_internal_audit(graph: Graph, family: PointFamily) -> dict[str, object]:
    """Return an independently checkable bad forced-edge witness for a family."""

    k_edges = set(edges_of(graph))
    l_edges = tuple(
        (left, right)
        for right in range(N)
        for left in range(right)
        if (left, right) not in k_edges
    )
    point_sets = tuple(frozenset(item) for item in family.points)
    pair_to_triangle: dict[Edge, int] = {}
    for triangle in range(N):
        point_ids = tuple(
            point_id for point_id, point in enumerate(point_sets) if triangle in point
        )
        if len(point_ids) != 3:
            raise AssertionError("triangle incidence is not three")
        for first, second in itertools.combinations(point_ids, 2):
            pair = edge(first, second)
            if pair in pair_to_triangle:
                raise AssertionError("an internal graph edge lies in two active triangles")
            pair_to_triangle[pair] = triangle
    if len(pair_to_triangle) != 33:
        raise AssertionError("expected 33 forced internal graph edges")

    degree_histogram: Counter[int] = Counter()
    bad: list[dict[str, object]] = []
    for (first, second), shared_triangle in sorted(pair_to_triangle.items()):
        crossing = tuple(
            item
            for item in l_edges
            if (item[0] in point_sets[first] and item[1] in point_sets[second])
            or (item[1] in point_sets[first] and item[0] in point_sets[second])
        )
        degree = len(crossing)
        degree_histogram[degree] += 1
        if degree not in ALLOWED_NONZERO_H_DEGREES | {0}:
            bad.append(
                {
                    "point_ids": [first, second],
                    "point_sets": [sorted(point_sets[first]), sorted(point_sets[second])],
                    "shared_triangle": shared_triangle,
                    "crossing_l_edges": [list(item) for item in crossing],
                    "d_H": degree,
                }
            )
    return {
        "forced_internal_edge_count": len(pair_to_triangle),
        "forced_degree_histogram": {
            str(key): value for key, value in sorted(degree_histogram.items())
        },
        "bad_forced_edge_count": len(bad),
        "witness": bad[0] if bad else None,
    }


def audit(args: argparse.Namespace) -> dict[str, object]:
    catalog_path = args.catalog.resolve()
    labels, graphs = read_catalog(catalog_path)
    family_counts = Counter()
    type_counts = Counter()
    bad_count_histogram = Counter()
    bad_degree_histogram = Counter()
    records: list[dict[str, object]] = []
    per_type: list[dict[str, object]] = []
    total_families = 0
    start = time.monotonic()

    for type_index, (label, graph) in enumerate(zip(labels, graphs), 1):
        type_profiles = set()
        local_counts = Counter()
        for family_index, family in enumerate(enumerate_point_families(graph), 1):
            total_families += 1
            family_counts[family.profile] += 1
            local_counts[family.profile] += 1
            type_profiles.add(family.profile)
            forced = forced_internal_audit(graph, family)
            bad_count = int(forced["bad_forced_edge_count"])
            bad_count_histogram[bad_count] += 1
            for degree_text, count in forced["forced_degree_histogram"].items():
                degree = int(degree_text)
                if degree not in ALLOWED_NONZERO_H_DEGREES | {0}:
                    bad_degree_histogram[degree] += int(count)
            records.append(
                {
                    "global_family_index": total_families,
                    "type_index": type_index,
                    "graph6": label,
                    "family_index_within_type": family_index,
                    "profile": family.profile,
                    "points": [list(item) for item in family.points],
                    **forced,
                }
            )
        for profile in type_profiles:
            type_counts[profile] += 1
        per_type.append(
            {
                "type_index": type_index,
                "graph6": label,
                "connected": is_connected(graph),
                "family_counts": {
                    profile: local_counts[profile] for profile in ("A", "B", "C")
                },
            }
        )

    elapsed = time.monotonic() - start
    counts_by_profile = {profile: family_counts[profile] for profile in ("A", "B", "C")}
    types_by_profile = {profile: type_counts[profile] for profile in ("A", "B", "C")}
    if counts_by_profile != {"A": 15, "B": 0, "C": 595}:
        raise AssertionError(f"unexpected family counts {counts_by_profile}")
    if types_by_profile != {"A": 11, "B": 0, "C": 119}:
        raise AssertionError(f"unexpected type counts {types_by_profile}")
    if total_families != 610 or bad_count_histogram.get(0, 0):
        raise AssertionError("family census or contradiction count failed")
    if bad_degree_histogram != Counter({1: 14488, 2: 3840}):
        raise AssertionError(f"unexpected bad-degree histogram {bad_degree_histogram}")

    family_core = sorted(
        (
            {
                "type_index": item["type_index"],
                "graph6": item["graph6"],
                "profile": item["profile"],
                "points": item["points"],
            }
            for item in records
        ),
        key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
    )
    result: dict[str, object] = {
        "schema": "conditional-n3-33-forced-internal-audit-v1",
        "run_report": {
            "role": "verifier",
            "date_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "git_commit": args.git_commit,
            "claim_label": "DERIVED",
            "scope": "conditional n3=33, eleven active q=2 triangles, K any simple quartic graph on 11 vertices",
            "method": "complete quartic-type and point-clique census followed by a forced internal-edge H-degree check",
            "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
            "limitations": [
                "conditional on the committed Wave 6-8 identities and graph properties",
                "the connected quartic completeness count is sourced from House of Graphs / Meringer genreg",
                "this does not resolve the global Conway 99 problem",
            ],
        },
        "runtime": {
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "elapsed_seconds": elapsed,
            "standard_library_only": True,
            "implementation_path": str(Path(__file__).resolve()),
            "implementation_sha256": sha256_path(Path(__file__).resolve()),
        },
        "premises_used": [
            "n3=33 forces either the ten-active profile (q=3,q=3,q=2^8) or eleven active triangles all q=2; the ten-active profile is separately excluded by the singleton fixed-side argument",
            "in the eleven-active profile, K=complement(L) is simple 4-regular on 11 vertices",
            "each active triangle belongs to exactly three original graph vertices and every point set S_u is a K-clique",
            "a K-edge is consumed by at most one point; a fully consumed K3 must be contained in a common point",
            "singleton point sets are excluded by the fixed-point identity and fixed-side degree 0/2 rule",
            "for every actual graph edge uv, d_H(uv)=e_L(S_u,S_v) and d_H(uv) is in {0,4,6,8,10,12}",
        ],
        "profiles": {
            "A": {"x2": 12, "x3": 3, "x4": 0, "x5": 0, "consumed_K_edges": 21},
            "B": {"x2": 13, "x3": 1, "x4": 1, "x5": 0, "consumed_K_edges": 22},
            "C": {"x2": 15, "x3": 1, "x4": 0, "x5": 0, "consumed_K_edges": 18},
        },
        "catalog": {
            "path": str(catalog_path),
            "source_page": "https://houseofgraphs.org/meta-directory/quartic",
            "source_data": "https://houseofgraphs.org/data/quartics/11_4_3.g6.gz",
            "sha256_compressed": sha256_path(catalog_path),
            "sha256_decompressed": sha256_gzip_payload(catalog_path),
            "connected_graph6_count": 265,
            "disconnected_graph6": labels[-1],
            "disconnected_type": "K5 disjoint union (K6 minus a perfect matching)",
            "total_quartic_types": len(graphs),
        },
        "enumeration": {
            "family_counts_by_profile": counts_by_profile,
            "types_with_profile": types_by_profile,
            "total_families": total_families,
            "family_core_sha256": canonical_json_sha256(family_core),
            "per_type_sha256": canonical_json_sha256(per_type),
            "bad_forced_edges_per_family_histogram": {
                str(key): value for key, value in sorted(bad_count_histogram.items())
            },
            "aggregate_bad_forced_degree_histogram": {
                str(key): value for key, value in sorted(bad_degree_histogram.items())
            },
            "minimum_bad_forced_edges_in_any_family": min(bad_count_histogram),
            "maximum_bad_forced_edges_in_any_family": max(bad_count_histogram),
            "surviving_families": 0,
        },
        "per_type": per_type,
        "family_failure_records": records,
        "conclusion": {
            "status": "EXHAUSTIVE_CONTRADICTION_UNDER_PREMISES",
            "reason": "every admissible point-clique family has a forced actual graph edge inside an active triangle with d_H equal to 1 or 2",
            "support_selection_needed": False,
        },
    }
    if args.certificate:
        output_path = args.certificate.resolve()
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        replay = json.loads(output_path.read_text(encoding="utf-8"))
        if replay != result:
            raise AssertionError("certificate write/read checksum failed")
        print(f"wrote {output_path}")
        print(f"certificate_sha256 {sha256_path(output_path)}")
    elif args.summary_only:
        summary = {
            "catalog": result["catalog"],
            "enumeration": result["enumeration"],
            "conclusion": result["conclusion"],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path(__file__).with_name("11_4_3.g6.gz"),
    )
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--git-commit", default="UNKNOWN")
    parser.add_argument("--summary-only", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    audit(parse_args())
