#!/usr/bin/env python3
"""Standalone replay verifier for the conditional n3=33 census certificate.

This file intentionally does not import audit_n3_33.py.  It has a separate
graph6 decoder, an individualize/refine canonical graph normalizer, and an
alternate binary f-factor recursion.  It recomputes the complete family set,
checks every recorded contradiction witness, and performs in-memory mutation
tests against the certificate validator.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import itertools
import json
import platform
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Iterator


ORDER = 11
PROFILES = {
    "A": {2: 12, 3: 3, 4: 0},
    "B": {2: 13, 3: 1, 4: 1},
    "C": {2: 15, 3: 1, 4: 0},
}
ALLOWED = {0, 4, 6, 8, 10, 12}
Edge = tuple[int, int]
Graph = tuple[frozenset[int], ...]
FamilyKey = tuple[int, str, tuple[tuple[int, ...], ...]]


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def digest_raw_gzip(path: Path) -> str:
    with gzip.open(path, "rb") as handle:
        return digest_bytes(handle.read())


def digest_json(value: object) -> str:
    return digest_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def pair(left: int, right: int) -> Edge:
    return (left, right) if left < right else (right, left)


def decode_g6(text: str) -> Graph:
    """Independent bit-string graph6 decoder for short order fields."""

    label = text.strip()
    if not label or ord(label[0]) - 63 != ORDER:
        raise AssertionError("bad short graph6 order")
    bit_string = "".join(f"{ord(character) - 63:06b}" for character in label[1:])
    neighbors = [set() for _ in range(ORDER)]
    cursor = 0
    for high in range(1, ORDER):
        for low in range(high):
            if bit_string[cursor] == "1":
                neighbors[low].add(high)
                neighbors[high].add(low)
            cursor += 1
    return tuple(frozenset(items) for items in neighbors)


def encode_g6(graph: Graph) -> str:
    bit_string = "".join(
        "1" if low in graph[high] else "0"
        for high in range(1, ORDER)
        for low in range(high)
    )
    bit_string += "0" * ((-len(bit_string)) % 6)
    return chr(63 + ORDER) + "".join(
        chr(63 + int(bit_string[index : index + 6], 2))
        for index in range(0, len(bit_string), 6)
    )


def graph_edges(graph: Graph) -> tuple[Edge, ...]:
    return tuple(
        (left, right)
        for left in range(ORDER)
        for right in range(left + 1, ORDER)
        if right in graph[left]
    )


def connected(graph: Graph) -> bool:
    reached = {0}
    pending = [0]
    while pending:
        vertex = pending.pop()
        new = graph[vertex] - reached
        reached.update(new)
        pending.extend(new)
    return len(reached) == ORDER


def validate_quartic(graph: Graph) -> None:
    if len(graph) != ORDER or any(len(items) != 4 for items in graph):
        raise AssertionError("not quartic order 11")
    if any(vertex in graph[vertex] for vertex in range(ORDER)):
        raise AssertionError("loop")
    if any(
        (other in graph[vertex]) != (vertex in graph[other])
        for vertex in range(ORDER)
        for other in range(ORDER)
    ):
        raise AssertionError("asymmetric graph")
    if len(graph_edges(graph)) != 22:
        raise AssertionError("wrong quartic edge count")


def extra_disconnected_graph() -> Graph:
    neighbors = [set() for _ in range(ORDER)]
    for left, right in itertools.combinations(range(5), 2):
        neighbors[left].add(right)
        neighbors[right].add(left)
    absent = {(5, 6), (7, 8), (9, 10)}
    for left, right in itertools.combinations(range(5, ORDER), 2):
        if (left, right) not in absent:
            neighbors[left].add(right)
            neighbors[right].add(left)
    result = tuple(frozenset(items) for items in neighbors)
    validate_quartic(result)
    if connected(result):
        raise AssertionError("extra graph unexpectedly connected")
    return result


def load_graphs(catalog: Path) -> tuple[list[str], list[Graph]]:
    with gzip.open(catalog, "rt", encoding="ascii") as handle:
        labels = [line.strip() for line in handle if line.strip()]
    if len(labels) != 265 or len(set(labels)) != 265:
        raise AssertionError("connected catalog count/label uniqueness failed")
    graphs = [decode_g6(label) for label in labels]
    for label, graph in zip(labels, graphs):
        validate_quartic(graph)
        if not connected(graph) or encode_g6(graph) != label:
            raise AssertionError("connected catalog validation failed")
    extra = extra_disconnected_graph()
    labels.append(encode_g6(extra))
    graphs.append(extra)
    return labels, graphs


def refine_colors(graph: Graph, colors: tuple[int, ...]) -> tuple[int, ...]:
    while True:
        number = max(colors) + 1
        signatures = []
        for vertex in range(ORDER):
            neighbor_counts = tuple(
                sum(colors[other] == color for other in graph[vertex])
                for color in range(number)
            )
            signatures.append((colors[vertex], neighbor_counts))
        rank = {item: index for index, item in enumerate(sorted(set(signatures)))}
        refined = tuple(rank[item] for item in signatures)
        if refined == colors:
            return refined
        colors = refined


def canonical_graph_code(graph: Graph) -> str:
    """Exact individualize/refine canonical adjacency code."""

    def search(colors: tuple[int, ...]) -> str:
        colors = refine_colors(graph, colors)
        cells = [
            tuple(vertex for vertex, color_at_vertex in enumerate(colors) if color_at_vertex == color)
            for color in range(max(colors) + 1)
        ]
        nonsingletons = [cell for cell in cells if len(cell) > 1]
        if not nonsingletons:
            ordering = sorted(range(ORDER), key=colors.__getitem__)
            return "".join(
                "1" if ordering[high] in graph[ordering[low]] else "0"
                for high in range(1, ORDER)
                for low in range(high)
            )
        chosen_cell = min(nonsingletons, key=lambda cell: (len(cell), colors[cell[0]]))
        branches = []
        for vertex in chosen_cell:
            individualized = list(colors)
            individualized[vertex] = max(colors) + 1
            branches.append(search(tuple(individualized)))
        return min(branches)

    return search((0,) * ORDER)


def relabel(graph: Graph, permutation: tuple[int, ...]) -> Graph:
    """permutation[old] is the new label."""

    output = [set() for _ in range(ORDER)]
    for old in range(ORDER):
        for neighbor in graph[old]:
            output[permutation[old]].add(permutation[neighbor])
    return tuple(frozenset(items) for items in output)


def all_cliques(graph: Graph, size: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        vertices
        for vertices in itertools.combinations(range(ORDER), size)
        if all(right in graph[left] for left, right in itertools.combinations(vertices, 2))
    )


def alternate_f_factors(
    available: tuple[Edge, ...], demands: tuple[int, ...]
) -> Iterator[tuple[Edge, ...]]:
    """Binary incident-edge recursion, distinct from the primary enumerator."""

    def visit(edges: tuple[Edge, ...], residual: tuple[int, ...]) -> Iterator[tuple[Edge, ...]]:
        if sum(residual) == 0:
            yield ()
            return
        vertex = next(index for index, value in enumerate(residual) if value)
        choices = tuple(
            item
            for item in edges
            if vertex in item and residual[item[0]] and residual[item[1]]
        )
        need = residual[vertex]
        if len(choices) < need:
            return

        def select(position: int, still_needed: int, selected: tuple[Edge, ...]) -> Iterator[tuple[Edge, ...]]:
            if still_needed == 0:
                yield selected
                return
            if len(choices) - position < still_needed:
                return
            current = choices[position]
            other = current[1] if current[0] == vertex else current[0]
            if residual[other] > 0:
                yield from select(position + 1, still_needed - 1, selected + (current,))
            yield from select(position + 1, still_needed, selected)

        for selected in select(0, need, ()):
            next_demands = list(residual)
            next_demands[vertex] = 0
            feasible = True
            for current in selected:
                other = current[1] if current[0] == vertex else current[0]
                next_demands[other] -= 1
                feasible &= next_demands[other] >= 0
            if not feasible:
                continue
            remaining = tuple(
                item
                for item in edges
                if vertex not in item
                and next_demands[item[0]] > 0
                and next_demands[item[1]] > 0
            )
            remaining_degrees = Counter(endpoint for item in remaining for endpoint in item)
            if any(
                next_demands[index] > remaining_degrees[index]
                for index in range(ORDER)
            ):
                continue
            for suffix in visit(remaining, tuple(next_demands)):
                yield selected + suffix

    yield from visit(available, demands)


def validate_family(graph: Graph, profile: str, points: tuple[tuple[int, ...], ...]) -> bool:
    expected = PROFILES[profile]
    if Counter(map(len, points)) != Counter({size: count for size, count in expected.items() if count}):
        return False
    if any(
        right not in graph[left]
        for point_set in points
        for left, right in itertools.combinations(point_set, 2)
    ):
        return False
    if any(sum(vertex in point_set for point_set in points) != 3 for vertex in range(ORDER)):
        return False

    owner: dict[Edge, int] = {}
    for point_id, point_set in enumerate(points):
        for left, right in itertools.combinations(point_set, 2):
            item = pair(left, right)
            if item in owner:
                return False
            owner[item] = point_id
    for triangle in all_cliques(graph, 3):
        triangle_edges = [pair(*item) for item in itertools.combinations(triangle, 2)]
        if all(item in owner for item in triangle_edges):
            if len({owner[item] for item in triangle_edges}) != 1:
                return False
    return True


def enumerate_families(graph: Graph) -> Iterator[tuple[str, tuple[tuple[int, ...], ...]]]:
    edges = graph_edges(graph)
    triangles = all_cliques(graph, 3)
    fours = all_cliques(graph, 4)
    seen: set[tuple[str, tuple[tuple[int, ...], ...]]] = set()
    for profile in ("A", "B", "C"):
        triangle_needed = PROFILES[profile][3]
        four_needed = PROFILES[profile][4]
        for chosen_triangles in itertools.combinations(triangles, triangle_needed):
            for chosen_fours in itertools.combinations(fours, four_needed):
                central = chosen_triangles + chosen_fours
                consumed: set[Edge] = set()
                valid = True
                loads = [0] * ORDER
                for point_set in central:
                    point_edges = {pair(*item) for item in itertools.combinations(point_set, 2)}
                    if consumed & point_edges:
                        valid = False
                        break
                    consumed.update(point_edges)
                    for vertex in point_set:
                        loads[vertex] += 1
                if not valid or any(value > 3 for value in loads):
                    continue
                demands = tuple(3 - value for value in loads)
                available = tuple(item for item in edges if item not in consumed)
                for factor in alternate_f_factors(available, demands):
                    points = tuple(sorted(central + factor, key=lambda item: (len(item), item)))
                    key = (profile, points)
                    if key in seen:
                        raise AssertionError("alternate enumeration produced a duplicate family")
                    if validate_family(graph, profile, points):
                        seen.add(key)
                        yield key


def forced_data(graph: Graph, points: tuple[tuple[int, ...], ...]) -> dict[str, object]:
    k_edges = set(graph_edges(graph))
    l_edges = tuple(
        (left, right)
        for left in range(ORDER)
        for right in range(left + 1, ORDER)
        if (left, right) not in k_edges
    )
    sets = tuple(set(item) for item in points)
    forced: dict[Edge, int] = {}
    for triangle in range(ORDER):
        ids = [index for index, point_set in enumerate(sets) if triangle in point_set]
        if len(ids) != 3:
            raise AssertionError("bad triangle incidence in replay")
        for left, right in itertools.combinations(ids, 2):
            item = pair(left, right)
            if item in forced:
                raise AssertionError("forced edge repeated")
            forced[item] = triangle
    degree_histogram: Counter[int] = Counter()
    bad = 0
    for (left, right), _triangle in forced.items():
        degree = sum(
            (a in sets[left] and b in sets[right])
            or (b in sets[left] and a in sets[right])
            for a, b in l_edges
        )
        degree_histogram[degree] += 1
        bad += degree not in ALLOWED
    return {
        "l_edges": l_edges,
        "sets": sets,
        "forced": forced,
        "histogram": degree_histogram,
        "bad_count": bad,
    }


def family_key(type_index: int, profile: str, points: object) -> FamilyKey:
    return (
        int(type_index),
        str(profile),
        tuple(tuple(int(vertex) for vertex in point_set) for point_set in points),
    )


def recompute(labels: list[str], graphs: list[Graph]) -> dict[str, object]:
    families: dict[FamilyKey, dict[str, object]] = {}
    counts = Counter()
    type_sets = {profile: set() for profile in PROFILES}
    per_type = []
    bad_counts = Counter()
    bad_degrees = Counter()
    for type_index, (label, graph) in enumerate(zip(labels, graphs), 1):
        local = Counter()
        for profile, points in enumerate_families(graph):
            key = family_key(type_index, profile, points)
            if key in families:
                raise AssertionError("duplicate global family key")
            data = forced_data(graph, points)
            families[key] = data
            counts[profile] += 1
            local[profile] += 1
            type_sets[profile].add(type_index)
            bad_counts[data["bad_count"]] += 1
            for degree, count in data["histogram"].items():
                if degree not in ALLOWED:
                    bad_degrees[degree] += count
        per_type.append(
            {
                "type_index": type_index,
                "graph6": label,
                "connected": connected(graph),
                "family_counts": {profile: local[profile] for profile in PROFILES},
            }
        )
    core = sorted(
        (
            {
                "type_index": key[0],
                "graph6": labels[key[0] - 1],
                "profile": key[1],
                "points": [list(item) for item in key[2]],
            }
            for key in families
        ),
        key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
    )
    return {
        "families": families,
        "counts": {profile: counts[profile] for profile in PROFILES},
        "type_counts": {profile: len(type_sets[profile]) for profile in PROFILES},
        "per_type": per_type,
        "core_digest": digest_json(core),
        "per_type_digest": digest_json(per_type),
        "bad_counts": bad_counts,
        "bad_degrees": bad_degrees,
    }


def validate_certificate(
    certificate: dict[str, object], recomputed: dict[str, object], labels: list[str]
) -> None:
    if certificate.get("schema") != "conditional-n3-33-forced-internal-audit-v1":
        raise AssertionError("schema mismatch")
    enumeration = certificate["enumeration"]
    if enumeration["family_counts_by_profile"] != recomputed["counts"]:
        raise AssertionError("profile counts mismatch")
    if enumeration["types_with_profile"] != recomputed["type_counts"]:
        raise AssertionError("profile type counts mismatch")
    if enumeration["total_families"] != len(recomputed["families"]):
        raise AssertionError("total family count mismatch")
    if enumeration["family_core_sha256"] != recomputed["core_digest"]:
        raise AssertionError("family core digest mismatch")
    if enumeration["per_type_sha256"] != recomputed["per_type_digest"]:
        raise AssertionError("per-type digest mismatch")
    if certificate["per_type"] != recomputed["per_type"]:
        raise AssertionError("per-type records mismatch")
    if {
        int(key): value
        for key, value in enumeration["bad_forced_edges_per_family_histogram"].items()
    } != recomputed["bad_counts"]:
        raise AssertionError("bad-count histogram mismatch")
    if {
        int(key): value
        for key, value in enumeration["aggregate_bad_forced_degree_histogram"].items()
    } != recomputed["bad_degrees"]:
        raise AssertionError("bad-degree histogram mismatch")

    records = certificate["family_failure_records"]
    record_map = {
        family_key(item["type_index"], item["profile"], item["points"]): item
        for item in records
    }
    if len(record_map) != len(records) or set(record_map) != set(recomputed["families"]):
        raise AssertionError("failure-record family coverage mismatch")
    for key, data in recomputed["families"].items():
        record = record_map[key]
        expected_histogram = {
            str(degree): count for degree, count in sorted(data["histogram"].items())
        }
        if record["forced_internal_edge_count"] != 33:
            raise AssertionError("forced edge count mismatch")
        if record["forced_degree_histogram"] != expected_histogram:
            raise AssertionError("forced degree histogram mismatch")
        if record["bad_forced_edge_count"] != data["bad_count"] or data["bad_count"] == 0:
            raise AssertionError("bad forced-edge count mismatch")
        witness = record["witness"]
        left, right = map(int, witness["point_ids"])
        if pair(left, right) not in data["forced"]:
            raise AssertionError("witness is not a forced internal edge")
        if witness["shared_triangle"] != data["forced"][pair(left, right)]:
            raise AssertionError("witness shared triangle mismatch")
        point_sets = data["sets"]
        crossing = [
            list(item)
            for item in data["l_edges"]
            if (item[0] in point_sets[left] and item[1] in point_sets[right])
            or (item[1] in point_sets[left] and item[0] in point_sets[right])
        ]
        if witness["crossing_l_edges"] != crossing:
            raise AssertionError("witness crossing edge list mismatch")
        if witness["d_H"] != len(crossing) or witness["d_H"] in ALLOWED:
            raise AssertionError("witness H-degree mismatch")
        if witness["point_sets"] != [sorted(point_sets[left]), sorted(point_sets[right])]:
            raise AssertionError("witness point sets mismatch")
        if record["graph6"] != labels[key[0] - 1]:
            raise AssertionError("record graph label mismatch")
    conclusion = certificate["conclusion"]
    if conclusion["status"] != "EXHAUSTIVE_CONTRADICTION_UNDER_PREMISES":
        raise AssertionError("conclusion status mismatch")
    if conclusion["support_selection_needed"] is not False:
        raise AssertionError("support-selection flag mismatch")


def expect_rejection(
    name: str,
    certificate: dict[str, object],
    recomputed: dict[str, object],
    labels: list[str],
    mutate,
) -> str:
    altered = copy.deepcopy(certificate)
    mutate(altered)
    try:
        validate_certificate(altered, recomputed, labels)
    except (AssertionError, KeyError, IndexError, TypeError, ValueError):
        return name
    raise AssertionError(f"mutation unexpectedly accepted: {name}")


def run(args: argparse.Namespace) -> dict[str, object]:
    started = time.monotonic()
    catalog = args.catalog.resolve()
    certificate_path = args.certificate.resolve()
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    primary_script = Path(certificate["runtime"]["implementation_path"]).resolve()
    if certificate["runtime"]["implementation_sha256"] != digest_file(primary_script):
        raise AssertionError("primary implementation checksum mismatch")
    if certificate["catalog"]["sha256_compressed"] != digest_file(catalog):
        raise AssertionError("catalog compressed checksum mismatch")
    if certificate["catalog"]["sha256_decompressed"] != digest_raw_gzip(catalog):
        raise AssertionError("catalog raw checksum mismatch")
    labels, graphs = load_graphs(catalog)
    if certificate["catalog"]["disconnected_graph6"] != labels[-1]:
        raise AssertionError("disconnected graph label mismatch")

    canonical_codes = [canonical_graph_code(graph) for graph in graphs]
    if len(set(canonical_codes)) != 266:
        raise AssertionError("catalog contains isomorphic duplicate types")
    reverse = tuple(reversed(range(ORDER)))
    affine = tuple((3 * vertex + 2) % ORDER for vertex in range(ORDER))
    for graph, code in zip(graphs, canonical_codes):
        if canonical_graph_code(relabel(graph, reverse)) != code:
            raise AssertionError("reverse relabeling changed canonical code")
        if canonical_graph_code(relabel(graph, affine)) != code:
            raise AssertionError("affine relabeling changed canonical code")

    recomputed = recompute(labels, graphs)
    validate_certificate(certificate, recomputed, labels)
    mutations = [
        expect_rejection(
            "drop_failure_record",
            certificate,
            recomputed,
            labels,
            lambda item: item["family_failure_records"].pop(),
        ),
        expect_rejection(
            "alter_witness_degree",
            certificate,
            recomputed,
            labels,
            lambda item: item["family_failure_records"][0]["witness"].__setitem__(
                "d_H", item["family_failure_records"][0]["witness"]["d_H"] + 1
            ),
        ),
        expect_rejection(
            "alter_family_digest",
            certificate,
            recomputed,
            labels,
            lambda item: item["enumeration"].__setitem__("family_core_sha256", "0" * 64),
        ),
        expect_rejection(
            "alter_per_type_count",
            certificate,
            recomputed,
            labels,
            lambda item: item["per_type"][0]["family_counts"].__setitem__(
                "C", item["per_type"][0]["family_counts"]["C"] + 1
            ),
        ),
    ]
    result = {
        "status": "PASS independent n3=33 census replay",
        "implementations": {
            "primary_path": str(primary_script),
            "primary_sha256": digest_file(primary_script),
            "verifier_path": str(Path(__file__).resolve()),
            "verifier_sha256": digest_file(Path(__file__).resolve()),
        },
        "certificate": {
            "path": str(certificate_path),
            "sha256": digest_file(certificate_path),
        },
        "catalog": {
            "path": str(catalog),
            "sha256_compressed": digest_file(catalog),
            "sha256_decompressed": digest_raw_gzip(catalog),
            "connected_count": 265,
            "unique_disconnected_count": 1,
            "total_type_count": 266,
            "canonical_type_count": len(set(canonical_codes)),
            "canonical_codes_sha256": digest_json(sorted(canonical_codes)),
            "relabeling_checks_per_type": 2,
        },
        "enumeration": {
            "family_counts_by_profile": recomputed["counts"],
            "types_with_profile": recomputed["type_counts"],
            "total_families": len(recomputed["families"]),
            "family_core_sha256": recomputed["core_digest"],
            "per_type_sha256": recomputed["per_type_digest"],
            "bad_forced_edges_per_family_histogram": {
                str(key): value for key, value in sorted(recomputed["bad_counts"].items())
            },
            "aggregate_bad_forced_degree_histogram": {
                str(key): value for key, value in sorted(recomputed["bad_degrees"].items())
            },
            "surviving_families": recomputed["bad_counts"].get(0, 0),
        },
        "mutation_checks_rejected": mutations,
        "runtime": {
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "standard_library_only": True,
            "elapsed_seconds": time.monotonic() - started,
        },
        "limitations": [
            "connected-catalog completeness relies on the House of Graphs/Meringer genreg source count",
            "mathematical conclusion remains conditional on the committed Wave 6-8 premises",
        ],
    }
    if args.output:
        output = args.output.resolve()
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if json.loads(output.read_text(encoding="utf-8")) != result:
            raise AssertionError("verification report write/read mismatch")
        print(f"wrote {output}")
        print(f"report_sha256 {digest_file(output)}")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    directory = Path(__file__).resolve().parent
    parser.add_argument("--catalog", type=Path, default=directory / "11_4_3.g6.gz")
    parser.add_argument("--certificate", type=Path, default=directory / "n3-33-audit.json")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
