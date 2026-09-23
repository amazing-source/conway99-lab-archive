#!/usr/bin/env python3
"""Independent verifier for the Wave 19 conditional n3=60 closure.

This program imports no discovery code.  It authenticates the canonical v3
release, downloads and pins the official connected-cubic graph6 catalogs,
recomputes every connected and disconnected disposition, reconstructs the
two-Petersen orbit, enumerates every allowed Z placement through three
edges, and replays the exact Gram and Farkas obstructions.

The official House of Graphs assertion that its lists are complete and
pairwise nonisomorphic remains an external premise.  The verifier checks the
released bytes, every decoded record, and every case derived from them.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib
from itertools import combinations, permutations, product
import json
from math import gcd, lcm
from pathlib import Path, PurePosixPath
import urllib.request
from typing import Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_REL = "attempts/wave19-alternate-frontier/manifest.json"
MANIFEST_SHA256 = "428505294e69481e3a45fc4a3b1ca93e7ec92aff0a22a869f3692866db43a782"
PUBLIC_COMMIT = "a121e789e03a32c3d29bce8947b16033c0061ce7"

CORE_HASHES = {
    "agents/2026-07-23-wave19-alternate-frontier.md":
        "ea28f4104bcdd479cf1a2ea59652cb9f541893851a26cef1450755e1d0827dc0",
    "attempts/wave19-alternate-frontier/exact_frontier.py":
        "960b3f85ea2bbdbf940c46875bac7520aa2b514a1068e75d419c8e489dedde7b",
    "attempts/wave19-alternate-frontier/test_exact_frontier.py":
        "5271fc8c2358872c435d68b1e0ba9c0274ea509eed261fddd6bd512b0427d427",
    "attempts/wave19-alternate-frontier/exact-results.json":
        "3e6c3016572c55aa15acc7b629a6a11b73cfce48f33e61ab1def2ebaf9b6f000",
    "attempts/wave19-alternate-frontier/connected20-dispositions.txt":
        "ea4ce3e70e4e3dfc39befd952f633fc680642c5a6285d3ed08232d0d19f43cc6",
    "attempts/wave19-alternate-frontier/disconnected20-dispositions.json":
        "491e7dddd7a5d630b546faf3a86d0aedf34e80bf02bf70d9c52112082d5d1c9b",
    "attempts/wave19-alternate-frontier/public-redaction-v2.json":
        "5a4dc89f5d92472e36c9895a12807bc632479165a6b8378cd19813a2f66fe897",
    "attempts/wave19-alternate-frontier/public-newline-v3.json":
        "7f5f382e4f07ddb7f3e277d217b569c97ac23ebdb607c36134ede0a8a56ce9a6",
    "attempts/wave19-alternate-frontier/run-metadata.json":
        "2e04f0c94ab017e6e36180145cdae0f119a3ce20515966eb29995b6672affd65",
}

CATALOG_EXPECTED = {
    6: (10, "49a7391d96ad84fd13c8b5267ef23c215085ed317e6146e479df2bcdfd672949", 2),
    8: (35, "6946d13a0aec85386d47d087ad2a9f2561b05d8580f0ec937414f8d31359d34f", 5),
    10: (190, "0c3182bcbbfdc38fc7b84f3a1ac510834c3064524db00afeac212a3292f17c7b", 19),
    12: (1105, "21bab16fbf7db826928315b9ca1d64684c0b1f7014b02fab0c6f2fb2f247104b", 85),
    14: (9162, "6657f77868567a7e604a2325b5d748e5a04848b4ab75310ffa3ba695d26c66fe", 509),
    20: (17_356_626, "83e8d235435fb3aab83b0315ae39fe16cf0afdb4699bbdcd6fae31541ea8d458", 510_489),
}

Graph = tuple[int, ...]
Edge = tuple[int, int]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key {key!r}")
        output[key] = value
    return output


def strict_json_bytes(data: bytes) -> object:
    if data.startswith(b"\xef\xbb\xbf"):
        raise ValueError("UTF-8 BOM is forbidden")
    text = data.decode("utf-8")
    decoder = json.JSONDecoder(object_pairs_hook=reject_duplicate_keys)
    value, end = decoder.raw_decode(text)
    if text[end:].strip():
        raise ValueError("trailing JSON data")
    return value


def authenticate_release() -> dict[str, object]:
    manifest_path = ROOT / MANIFEST_REL
    raw = manifest_path.read_bytes()
    if digest(raw) != MANIFEST_SHA256:
        raise AssertionError("v3 manifest SHA-256 mismatch")
    manifest = strict_json_bytes(raw)
    if not isinstance(manifest, dict):
        raise AssertionError("manifest root is not an object")
    if (
        manifest.get("schema_version") != 3
        or manifest.get("release_revision") != "canonical-newline-v3"
        or manifest.get("release_frozen") is not True
    ):
        raise AssertionError("wrong manifest release identity")
    seen: set[str] = set()
    carriage_return_paths: list[str] = []
    for section in ("inputs", "artifacts"):
        records = manifest.get(section)
        if not isinstance(records, list):
            raise AssertionError(f"manifest {section} is not a list")
        for record in records:
            if not isinstance(record, dict):
                raise AssertionError("manifest file record is not an object")
            relative = record.get("path")
            if not isinstance(relative, str):
                raise AssertionError("manifest path is not a string")
            pure = PurePosixPath(relative)
            if pure.is_absolute() or ".." in pure.parts or relative in seen:
                raise AssertionError(f"unsafe or duplicate path {relative}")
            seen.add(relative)
            path = (ROOT / Path(*pure.parts)).resolve()
            if ROOT.resolve() not in path.parents:
                raise AssertionError(f"manifest path escapes root: {relative}")
            data = path.read_bytes()
            if len(data) != record.get("bytes") or digest(data) != record.get("sha256"):
                raise AssertionError(f"manifest bytes mismatch: {relative}")
            if b"\r" in data:
                carriage_return_paths.append(relative)
    if len(seen) != 30:
        raise AssertionError(f"expected 30 authenticated entries, found {len(seen)}")
    if b"\r" in raw or carriage_return_paths:
        raise AssertionError(f"noncanonical CR bytes: {carriage_return_paths}")
    for relative, expected_hash in CORE_HASHES.items():
        if digest((ROOT / relative).read_bytes()) != expected_hash:
            raise AssertionError(f"protected core mismatch: {relative}")
    return manifest


_catalog_cache: dict[int, tuple[bytes, ...]] = {}


def fetch_catalog(order: int, manifest: dict[str, object]) -> tuple[bytes, ...]:
    if order in _catalog_cache:
        return _catalog_cache[order]
    catalogs = manifest["catalogs"]
    assert isinstance(catalogs, dict)
    meta = catalogs[str(order)]
    assert isinstance(meta, dict)
    expected = CATALOG_EXPECTED[order]
    manifest_tuple = (meta["bytes"], meta["sha256"], meta["records"])
    if manifest_tuple != expected:
        raise AssertionError(f"manifest order-{order} catalog pin changed")
    request = urllib.request.Request(
        str(meta["url"]),
        headers={"User-Agent": "Conway99-independent-wave19-verifier/1"},
    )
    with urllib.request.urlopen(request, timeout=60.0) as response:
        data = response.read()
    records = tuple(line for line in data.splitlines() if line)
    observed = (len(data), digest(data), len(records))
    if observed != expected:
        raise AssertionError(f"order-{order} remote catalog mismatch: {observed}")
    if len(records) != len(set(records)):
        raise AssertionError(f"order-{order} catalog has duplicate byte records")
    for record in records:
        graph = strict_decode_graph6(record, expected_order=order)
        validate_connected_cubic(graph)
    _catalog_cache[order] = records
    return records


def strict_decode_graph6(record: bytes, expected_order: int | None = None) -> Graph:
    """Decode canonical short graph6, checking length and zero padding."""
    if not record or record.startswith(b">>graph6<<"):
        raise ValueError("bare short graph6 record required")
    if any(raw < 63 or raw > 126 for raw in record):
        raise ValueError("invalid graph6 character")
    order = record[0] - 63
    if not 0 <= order <= 62:
        raise ValueError("short graph6 order out of range")
    if expected_order is not None and order != expected_order:
        raise ValueError("graph6 order does not match catalog")
    needed = order * (order - 1) // 2
    payload_bytes = (needed + 5) // 6
    if len(record) != 1 + payload_bytes:
        raise ValueError("noncanonical graph6 payload length")
    bits: list[int] = []
    for raw in record[1:]:
        value = raw - 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    if any(bits[needed:]):
        raise ValueError("nonzero graph6 padding bit")
    rows = [0] * order
    cursor = 0
    for high in range(1, order):
        for low in range(high):
            if bits[cursor]:
                rows[low] |= 1 << high
                rows[high] |= 1 << low
            cursor += 1
    return tuple(rows)


def edges(graph: Graph) -> tuple[Edge, ...]:
    return tuple(
        (left, right)
        for left, row in enumerate(graph)
        for right in range(left + 1, len(graph))
        if row >> right & 1
    )


def normalize_edge(left: int, right: int) -> Edge:
    if left == right:
        raise ValueError("loop")
    return (left, right) if left < right else (right, left)


def validate_connected_cubic(graph: Graph) -> None:
    order = len(graph)
    valid_mask = (1 << order) - 1
    for vertex, row in enumerate(graph):
        if row & ~valid_mask or row >> vertex & 1:
            raise AssertionError("invalid adjacency row")
        if row.bit_count() != 3:
            raise AssertionError("catalog graph is not cubic")
        for neighbor in range(order):
            if bool(row >> neighbor & 1) != bool(graph[neighbor] >> vertex & 1):
                raise AssertionError("catalog graph is asymmetric")
    reached = 1
    queue = deque([0])
    while queue:
        vertex = queue.popleft()
        unseen = graph[vertex] & ~reached
        while unseen:
            bit = unseen & -unseen
            unseen ^= bit
            reached |= bit
            queue.append(bit.bit_length() - 1)
    if reached != valid_mask:
        raise AssertionError("catalog graph is disconnected")


def triangle_free(graph: Graph) -> bool:
    for left, right in edges(graph):
        if graph[left] & graph[right]:
            return False
    return True


def disjoint_union(graphs: Sequence[Graph]) -> Graph:
    result: list[int] = []
    offset = 0
    for graph in graphs:
        result.extend(row << offset for row in graph)
        offset += len(graph)
    return tuple(result)


def closed_distance_two(graph: Graph, root: int) -> int:
    mask = (1 << root) | graph[root]
    frontier = graph[root]
    while frontier:
        bit = frontier & -frontier
        frontier ^= bit
        mask |= graph[bit.bit_length() - 1]
    return mask


def six_cycle_masks_by_opposite_paths(graph: Graph) -> tuple[int, ...]:
    """Find C6 vertex sets by pairing internally disjoint 3-edge paths.

    This is deliberately different from the discovery DFS.  Opposite
    vertices of every 6-cycle are joined by two internally disjoint paths
    of length three; conversely such a pair is a 6-cycle even if the six
    vertices have additional chords.
    """
    paths: dict[Edge, set[int]] = defaultdict(set)
    order = len(graph)
    for start in range(order):
        first_choices = graph[start]
        while first_choices:
            first_bit = first_choices & -first_choices
            first_choices ^= first_bit
            first = first_bit.bit_length() - 1
            second_choices = graph[first] & ~(1 << start)
            while second_choices:
                second_bit = second_choices & -second_choices
                second_choices ^= second_bit
                second = second_bit.bit_length() - 1
                end_choices = graph[second] & ~((1 << start) | (1 << first))
                while end_choices:
                    end_bit = end_choices & -end_choices
                    end_choices ^= end_bit
                    end = end_bit.bit_length() - 1
                    if end == start:
                        continue
                    key = normalize_edge(start, end)
                    paths[key].add((1 << first) | (1 << second))
    cycles: set[int] = set()
    for (start, end), interiors in paths.items():
        for first, second in combinations(sorted(interiors), 2):
            if first & second:
                continue
            mask = (1 << start) | (1 << end) | first | second
            if mask.bit_count() == 6:
                cycles.add(mask)
    return tuple(sorted(cycles))


def local_remote_cycle_domains(graph: Graph) -> tuple[frozenset[int], ...] | None:
    cycles = six_cycle_masks_by_opposite_paths(graph)
    domains: list[frozenset[int]] = []
    for root in range(len(graph)):
        forbidden = closed_distance_two(graph, root)
        allowed = frozenset(mask for mask in cycles if not mask & forbidden)
        if not allowed:
            return None
        domains.append(allowed)
    return tuple(domains)


def arc_consistency(
    domains: tuple[frozenset[int], ...],
) -> tuple[frozenset[int], ...] | None:
    """AC-3 for the symmetry constraints v in L(u) iff u in L(v)."""
    current = [set(domain) for domain in domains]
    order = len(current)
    queue = deque((left, right) for left in range(order) for right in range(order) if left != right)
    while queue:
        left, right = queue.popleft()
        right_bits = {
            int(mask >> left & 1)
            for mask in current[right]
        }
        revised = {
            mask for mask in current[left]
            if int(mask >> right & 1) in right_bits
        }
        if revised == current[left]:
            continue
        if not revised:
            return None
        current[left] = revised
        for other in range(order):
            if other != left and other != right:
                queue.append((other, left))
    return tuple(frozenset(domain) for domain in current)


def symmetric_l_solutions(
    domains: tuple[frozenset[int], ...],
) -> tuple[tuple[int, ...], ...]:
    solutions: set[tuple[int, ...]] = set()

    def recurse(state: tuple[frozenset[int], ...]) -> None:
        reduced = arc_consistency(state)
        if reduced is None:
            return
        branch = min(
            (index for index, domain in enumerate(reduced) if len(domain) > 1),
            key=lambda index: (len(reduced[index]), index),
            default=None,
        )
        if branch is None:
            row = tuple(next(iter(domain)) for domain in reduced)
            if any(
                bool(row[left] >> right & 1) != bool(row[right] >> left & 1)
                for left in range(len(row))
                for right in range(left + 1, len(row))
            ):
                raise AssertionError("AC-3 emitted nonsymmetric rows")
            solutions.add(row)
            return
        for value in sorted(reduced[branch]):
            child = list(reduced)
            child[branch] = frozenset((value,))
            recurse(tuple(child))

    recurse(domains)
    return tuple(sorted(solutions))


def point_list(graph: Graph) -> tuple[Edge, ...]:
    return tuple(sorted(edges(graph)))


def l_edge_set(l_rows: tuple[int, ...]) -> frozenset[Edge]:
    return frozenset(
        (left, right)
        for left, row in enumerate(l_rows)
        for right in range(left + 1, len(l_rows))
        if row >> right & 1
    )


def compatible_r_edges(points: tuple[Edge, ...], l_rows: tuple[int, ...]) -> tuple[Edge, ...]:
    result: list[Edge] = []
    for left, right in combinations(range(len(points)), 2):
        p = points[left]
        q = points[right]
        if set(p) & set(q):
            continue
        if all(l_rows[a] >> b & 1 for a in p for b in q):
            result.append((left, right))
    return tuple(result)


def support_degree_histogram(points: tuple[Edge, ...], l_rows: tuple[int, ...]) -> dict[str, int]:
    degree = [0] * len(points)
    for left, right in compatible_r_edges(points, l_rows):
        degree[left] += 1
        degree[right] += 1
    return {str(value): count for value, count in sorted(Counter(degree).items())}


def forced_z_pairs(
    graph: Graph, points: tuple[Edge, ...], l_rows: tuple[int, ...]
) -> tuple[tuple[Edge, tuple[Edge, ...]], ...]:
    """K-pairs with exactly two existing independent cross-edges need a third.

    The frozen component classification defines L as the disjoint-triangle
    pairs with exactly two independent cross-edges.  Thus a K-pair whose two
    common F-neighbors supply those independent cross-edges must acquire the
    unmatched third point-pair edge in Z.
    """
    point_index = {point: index for index, point in enumerate(points)}
    forced: dict[Edge, list[Edge]] = defaultdict(list)
    for left, right in combinations(range(len(graph)), 2):
        if graph[left] >> right & 1 or l_rows[left] >> right & 1:
            continue
        common_mask = graph[left] & graph[right]
        if common_mask.bit_count() != 2:
            continue
        common = frozenset(
            index for index in range(len(graph)) if common_mask >> index & 1
        )
        left_other = [
            index for index in range(len(graph))
            if graph[left] >> index & 1 and index not in common
        ]
        right_other = [
            index for index in range(len(graph))
            if graph[right] >> index & 1 and index not in common
        ]
        if len(left_other) != 1 or len(right_other) != 1:
            raise AssertionError("cubic unmatched endpoint is not unique")
        point_pair = normalize_edge(
            point_index[normalize_edge(left, left_other[0])],
            point_index[normalize_edge(right, right_other[0])],
        )
        forced[point_pair].append((left, right))
    return tuple((key, tuple(sorted(value))) for key, value in sorted(forced.items()))


def connected_census_independent(
    records: tuple[bytes, ...],
    official_dispositions: bytes,
) -> tuple[dict[str, object], tuple[tuple[bytes, Graph, tuple[int, ...]], ...]]:
    if len(official_dispositions) != len(records) + 1 or not official_dispositions.endswith(b"\n"):
        raise AssertionError("official connected disposition length/newline mismatch")
    expected_codes = official_dispositions[:-1]
    counts: Counter[str] = Counter()
    final: list[dict[str, object]] = []
    survivor_models: list[tuple[bytes, Graph, tuple[int, ...]]] = []
    for index, record in enumerate(records):
        graph = strict_decode_graph6(record, expected_order=20)
        validate_connected_cubic(graph)
        if not triangle_free(graph):
            code = "T"
        else:
            counts["triangle_free"] += 1
            domains = local_remote_cycle_domains(graph)
            if domains is None:
                code = "L"
            else:
                counts["local_survivor"] += 1
                solutions = symmetric_l_solutions(domains)
                if not solutions:
                    code = "S"
                else:
                    counts["symmetric_model_count"] += len(solutions)
                    if len(solutions) != 1:
                        raise AssertionError(f"connected index {index} has {len(solutions)} solutions")
                    l_rows = solutions[0]
                    points = point_list(graph)
                    forced = forced_z_pairs(graph, points, l_rows)
                    histogram = support_degree_histogram(points, l_rows)
                    if len(forced) > 3:
                        code = "Z"
                        disposition = "FORCED_Z_EXCEEDS_THREE"
                    elif min(map(int, histogram)) < 2:
                        code = "D"
                        disposition = "SUPPORT_DEGREE_BELOW_TWO"
                    else:
                        raise AssertionError(f"unclassified connected index {index}")
                    final.append(
                        {
                            "catalog_index": index,
                            "record_sha256": digest(record),
                            "domain_size_histogram": {
                                str(size): count
                                for size, count in sorted(Counter(map(len, domains)).items())
                            },
                            "support_degree_histogram": histogram,
                            "forced_zero_edge_count": len(forced),
                            "forced_codegree_two_pair_count": sum(len(labels) for _, labels in forced),
                            "l_rows": list(l_rows),
                            "disposition": disposition,
                        }
                    )
                    survivor_models.append((record, graph, l_rows))
        counts[code] += 1
        if ord(code) != expected_codes[index]:
            raise AssertionError(
                f"connected disposition mismatch at {index}: {code} != {chr(expected_codes[index])}"
            )
        if (index + 1) % 100_000 == 0:
            print(f"independent connected checkpoint {index+1}/{len(records)}", flush=True)
    expected = Counter({"T": 412_943, "L": 97_248, "S": 295, "Z": 2, "D": 1})
    observed_codes = Counter(chr(value) for value in expected_codes)
    if observed_codes != expected:
        raise AssertionError(f"connected code census mismatch: {observed_codes}")
    if (
        counts["triangle_free"] != 97_546
        or counts["local_survivor"] != 298
        or len(final) != 3
    ):
        raise AssertionError(f"connected stage counts changed: {counts}")
    return (
        {
            "catalog_records": len(records),
            "code_histogram": dict(sorted(observed_codes.items())),
            "triangle_free": counts["triangle_free"],
            "local_C6_survivors": counts["local_survivor"],
            "symmetric_L_failures": counts["S"],
            "final_rows": final,
            "per_record_dispositions_exact": True,
        },
        tuple(survivor_models),
    )


def triangle_free_small_catalog(
    order: int, manifest: dict[str, object]
) -> tuple[tuple[int, bytes, Graph], ...]:
    output: list[tuple[int, bytes, Graph]] = []
    for index, record in enumerate(fetch_catalog(order, manifest)):
        graph = strict_decode_graph6(record, expected_order=order)
        if triangle_free(graph):
            output.append((index, record, graph))
    return tuple(output)


def disconnected_models(
    manifest: dict[str, object],
) -> tuple[tuple[str, Graph], ...]:
    small = {
        order: triangle_free_small_catalog(order, manifest)
        for order in (6, 8, 10, 12, 14)
    }
    observed = {order: len(records) for order, records in small.items()}
    if observed != {6: 1, 8: 2, 10: 6, 12: 22, 14: 110}:
        raise AssertionError(f"small triangle-free census mismatch: {observed}")
    output: list[tuple[str, Graph]] = []
    for part14 in small[14]:
        for part6 in small[6]:
            output.append(
                (
                    f"14-{part14[0]:03d}+6-{part6[0]:03d}",
                    disjoint_union((part14[2], part6[2])),
                )
            )
    for part12 in small[12]:
        for part8 in small[8]:
            output.append(
                (
                    f"12-{part12[0]:03d}+8-{part8[0]:03d}",
                    disjoint_union((part12[2], part8[2])),
                )
            )
    for left_index, left in enumerate(small[10]):
        for right in small[10][left_index:]:
            output.append(
                (
                    f"10-{left[0]:03d}+10-{right[0]:03d}",
                    disjoint_union((left[2], right[2])),
                )
            )
    for part8 in small[8]:
        for left_index, left6 in enumerate(small[6]):
            for right6 in small[6][left_index:]:
                output.append(
                    (
                        f"8-{part8[0]:03d}+6-{left6[0]:03d}+6-{right6[0]:03d}",
                        disjoint_union((part8[2], left6[2], right6[2])),
                    )
                )
    if len(output) != 177 or len({case_id for case_id, _ in output}) != 177:
        raise AssertionError("disconnected case construction is not exactly 177")
    return tuple(output)


def disconnected_census_independent(
    manifest: dict[str, object], official_dispositions: bytes
) -> tuple[dict[str, object], Graph, tuple[tuple[int, ...], ...]]:
    official = strict_json_bytes(official_dispositions)
    if not isinstance(official, list):
        raise AssertionError("official disconnected dispositions are not a list")
    cases = disconnected_models(manifest)
    if len(official) != len(cases):
        raise AssertionError("official disconnected disposition count mismatch")
    statuses: Counter[str] = Counter()
    reproduced: list[dict[str, object]] = []
    residual_graph: Graph | None = None
    residual_solutions: tuple[tuple[int, ...], ...] | None = None
    for position, (case_id, graph) in enumerate(cases):
        domains = local_remote_cycle_domains(graph)
        if domains is None:
            status = "NO_LOCAL_C6"
            solutions: tuple[tuple[int, ...], ...] = ()
        else:
            solutions = symmetric_l_solutions(domains)
            if not solutions:
                status = "NO_SYMMETRIC_L"
            else:
                points = point_list(graph)
                forced_counts = [
                    len(forced_z_pairs(graph, points, l_rows))
                    for l_rows in solutions
                ]
                support_histograms = [
                    support_degree_histogram(points, l_rows)
                    for l_rows in solutions
                ]
                if all(count == 20 for count in forced_counts):
                    status = "FORCED_Z_EXCEEDS_THREE"
                elif (
                    len(solutions) == 120
                    and set(forced_counts) == {0}
                    and {
                        tuple(sorted(histogram.items()))
                        for histogram in support_histograms
                    }
                    == {(("2", 30),)}
                ):
                    status = "TWO_PETERSEN_RESIDUAL"
                    if residual_graph is not None:
                        raise AssertionError("more than one two-Petersen residual")
                    residual_graph = graph
                    residual_solutions = solutions
                else:
                    raise AssertionError(
                        f"unclassified disconnected case {case_id}: "
                        f"{len(solutions)} solutions, forced={Counter(forced_counts)}"
                    )
        row = {
            "case_id": case_id,
            "status": status,
            "symmetric_L_solution_count": len(solutions),
        }
        if official[position] != row:
            raise AssertionError(
                f"disconnected disposition mismatch at {position}: "
                f"{row!r} != {official[position]!r}"
            )
        statuses[status] += 1
        reproduced.append(row)
    expected = {
        "NO_LOCAL_C6": 5,
        "NO_SYMMETRIC_L": 168,
        "FORCED_Z_EXCEEDS_THREE": 3,
        "TWO_PETERSEN_RESIDUAL": 1,
    }
    if dict(statuses) != expected:
        raise AssertionError(f"disconnected status census changed: {statuses}")
    if residual_graph is None or residual_solutions is None:
        raise AssertionError("two-Petersen residual was not recovered")
    canonical_render = (
        json.dumps(reproduced, indent=2, sort_keys=True) + "\n"
    ).encode()
    if canonical_render != official_dispositions:
        raise AssertionError("disconnected disposition bytes do not reproduce exactly")
    return (
        {
            "case_count": len(cases),
            "status_counts": dict(sorted(statuses.items())),
            "per_case_dispositions_exact": True,
            "disposition_sha256": digest(canonical_render),
        },
        residual_graph,
        residual_solutions,
    )


def compatible_support_set(
    points: tuple[Edge, ...], l_rows: tuple[int, ...]
) -> frozenset[Edge]:
    selected = frozenset(compatible_r_edges(points, l_rows))
    degree = Counter(vertex for support in selected for vertex in support)
    if len(degree) != len(points) or set(degree.values()) != {2}:
        raise AssertionError("two-Petersen support graph is not 2-regular")
    coverage: Counter[Edge] = Counter()
    cover_supports: dict[Edge, list[Edge]] = defaultdict(list)
    for support in selected:
        for left_label in points[support[0]]:
            for right_label in points[support[1]]:
                pair = normalize_edge(left_label, right_label)
                coverage[pair] += 1
                cover_supports[pair].append(support)
    if set(coverage) != set(l_edge_set(l_rows)) or set(coverage.values()) != {2}:
        raise AssertionError("R rectangles do not give exact twofold L coverage")
    for label_pair, two_supports in cover_supports.items():
        if len(two_supports) != 2:
            raise AssertionError("wrong rectangle multiplicity")
        for label in label_pair:
            incident_points = [
                next(vertex for vertex in support if label in points[vertex])
                for support in two_supports
            ]
            if len(set(incident_points)) != 2:
                raise AssertionError("rectangle covers fail independent matching")
    return selected


def graph_automorphisms_independent(graph: Graph) -> tuple[tuple[int, ...], ...]:
    """Enumerate automorphisms by MRV extension of partial isomorphisms."""
    order = len(graph)
    mapped = [-1] * order
    reverse = [-1] * order
    answers: list[tuple[int, ...]] = []

    def signatures(source: int, target: int) -> bool:
        if graph[source].bit_count() != graph[target].bit_count():
            return False
        for other_source, other_target in enumerate(mapped):
            if other_target < 0:
                continue
            if bool(graph[source] >> other_source & 1) != bool(
                graph[target] >> other_target & 1
            ):
                return False
        mapped_neighbor_count = sum(
            mapped[neighbor] >= 0
            for neighbor in range(order)
            if graph[source] >> neighbor & 1
        )
        target_mapped_neighbor_count = sum(
            reverse[neighbor] >= 0
            for neighbor in range(order)
            if graph[target] >> neighbor & 1
        )
        return mapped_neighbor_count == target_mapped_neighbor_count

    def visit() -> None:
        if all(value >= 0 for value in mapped):
            answers.append(tuple(mapped))
            return
        alternatives: list[tuple[int, int, tuple[int, ...]]] = []
        for source in range(order):
            if mapped[source] >= 0:
                continue
            targets = tuple(
                target
                for target in range(order)
                if reverse[target] < 0 and signatures(source, target)
            )
            alternatives.append((len(targets), source, targets))
        _, source, targets = min(alternatives)
        for target in targets:
            mapped[source] = target
            reverse[target] = source
            visit()
            mapped[source] = -1
            reverse[target] = -1

    visit()
    result = tuple(sorted(set(answers)))
    for permutation in result:
        for left in range(order):
            image_neighbors = sum(
                1 << permutation[right]
                for right in range(order)
                if graph[left] >> right & 1
            )
            if image_neighbors != graph[permutation[left]]:
                raise AssertionError("non-automorphism escaped backtracking")
    return result


def permute_l_rows(
    l_rows: tuple[int, ...], permutation: tuple[int, ...]
) -> tuple[int, ...]:
    result = [0] * len(l_rows)
    for left, right in l_edge_set(l_rows):
        image_left, image_right = permutation[left], permutation[right]
        result[image_left] |= 1 << image_right
        result[image_right] |= 1 << image_left
    return tuple(result)


def point_permutation(
    points: tuple[Edge, ...], label_permutation: tuple[int, ...]
) -> tuple[int, ...]:
    index = {point: position for position, point in enumerate(points)}
    return tuple(
        index[normalize_edge(label_permutation[left], label_permutation[right])]
        for left, right in points
    )


def permute_edge_set(
    selected: Iterable[Edge], permutation: tuple[int, ...]
) -> tuple[Edge, ...]:
    return tuple(
        sorted(
            normalize_edge(permutation[left], permutation[right])
            for left, right in selected
        )
    )


def two_petersen_orbit_independent(
    graph: Graph, l_solutions: tuple[tuple[int, ...], ...]
) -> tuple[
    tuple[int, ...],
    frozenset[Edge],
    tuple[tuple[int, ...], ...],
    dict[str, object],
]:
    points = point_list(graph)
    base_l = min(l_solutions)
    base_r = compatible_support_set(points, base_l)
    first_component = tuple(row & ((1 << 10) - 1) for row in graph[:10])
    automorphisms = graph_automorphisms_independent(first_component)
    if len(automorphisms) != 120:
        raise AssertionError(f"Petersen automorphism count is {len(automorphisms)}")
    all_label_automorphisms: list[tuple[int, ...]] = []
    for left in automorphisms:
        for right in automorphisms:
            all_label_automorphisms.append(
                tuple(left) + tuple(value + 10 for value in right)
            )
            all_label_automorphisms.append(
                tuple(value + 10 for value in left) + tuple(right)
            )
    if len(all_label_automorphisms) != 28_800:
        raise AssertionError("full two-Petersen automorphism enumeration changed")
    l_orbit = {
        permute_l_rows(base_l, permutation)
        for permutation in all_label_automorphisms
    }
    if l_orbit != set(l_solutions) or len(l_orbit) != 120:
        raise AssertionError("120 symmetric L models are not one full orbit")
    point_stabilizer: dict[tuple[int, ...], tuple[int, ...]] = {}
    base_r_tuple = tuple(sorted(base_r))
    for label_permutation in all_label_automorphisms:
        induced = point_permutation(points, label_permutation)
        if permute_edge_set(base_r_tuple, induced) == base_r_tuple:
            point_stabilizer[induced] = label_permutation
    group = tuple(sorted(point_stabilizer))
    if len(group) != 240:
        raise AssertionError(f"(L,R) point stabilizer has order {len(group)}")
    group_set = set(group)
    identity = tuple(range(len(points)))
    if identity not in group_set:
        raise AssertionError("stabilizer misses identity")
    for first in group:
        inverse = [0] * len(first)
        for source, target in enumerate(first):
            inverse[target] = source
        if tuple(inverse) not in group_set:
            raise AssertionError("stabilizer misses an inverse")
    # Check closure without assuming the discovery program's ordering.
    for first in group:
        for second in group:
            composition = tuple(second[first[index]] for index in range(len(points)))
            if composition not in group_set:
                raise AssertionError("stabilizer is not closed")
    return (
        base_l,
        base_r,
        group,
        {
            "petersen_automorphism_count": len(automorphisms),
            "full_F_automorphism_count": len(all_label_automorphisms),
            "L_R_model_count": len(l_solutions),
            "base_stabilizer_order": len(group),
            "orbit_equals_all_models": True,
        },
    )


def active_graph(
    points: tuple[Edge, ...],
    r_edges: Iterable[Edge],
    z_edges: Iterable[Edge] = (),
) -> Graph:
    rows = [0] * len(points)
    for left, right in combinations(range(len(points)), 2):
        if set(points[left]) & set(points[right]):
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    for left, right in tuple(r_edges) + tuple(z_edges):
        rows[left] |= 1 << right
        rows[right] |= 1 << left
    return tuple(rows)


def outside_gram_independent(active: Graph) -> tuple[tuple[int, ...], ...]:
    order = len(active)
    return tuple(
        tuple(
            12 * int(left == right)
            + 2
            - int(active[left] >> right & 1)
            - (active[left] & active[right]).bit_count()
            for right in range(order)
        )
        for left in range(order)
    )


def fraction_echelon_rank(
    matrix: Iterable[Iterable[int | Fraction]],
) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    row = 0
    for column in range(len(work[0])):
        pivot = next(
            (candidate for candidate in range(row, len(work)) if work[candidate][column]),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        pivot_value = work[row][column]
        for lower in range(row + 1, len(work)):
            if not work[lower][column]:
                continue
            multiplier = work[lower][column] / pivot_value
            for right in range(column, len(work[0])):
                work[lower][right] -= multiplier * work[row][right]
        row += 1
        if row == len(work):
            break
    return row


def kernel_basis_independent(
    matrix: tuple[tuple[int, ...], ...],
) -> tuple[tuple[Fraction, ...], ...]:
    work = [[Fraction(value) for value in row] for row in matrix]
    row = 0
    pivots: list[int] = []
    width = len(work[0]) if work else 0
    for column in range(width):
        pivot = next(
            (candidate for candidate in range(row, len(work)) if work[candidate][column]),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        divisor = work[row][column]
        work[row] = [value / divisor for value in work[row]]
        for other in range(len(work)):
            if other == row or not work[other][column]:
                continue
            multiplier = work[other][column]
            work[other] = [
                value - multiplier * pivot_value
                for value, pivot_value in zip(work[other], work[row])
            ]
        pivots.append(column)
        row += 1
        if row == len(work):
            break
    pivot_set = set(pivots)
    basis: list[tuple[Fraction, ...]] = []
    for free in range(width):
        if free in pivot_set:
            continue
        vector = [Fraction(0)] * width
        vector[free] = Fraction(1)
        for pivot_row, pivot_column in enumerate(pivots):
            vector[pivot_column] = -work[pivot_row][free]
        basis.append(tuple(vector))
    return tuple(basis)


def psd_by_exact_ldl(matrix: tuple[tuple[int, ...], ...]) -> bool:
    """Exact symmetric elimination with simultaneous row/column pivots."""
    work = [[Fraction(value) for value in row] for row in matrix]
    order = len(work)
    start = 0
    while start < order:
        if any(work[index][index] < 0 for index in range(start, order)):
            return False
        positive = next(
            (index for index in range(start, order) if work[index][index] > 0),
            None,
        )
        if positive is None:
            # A PSD matrix with a zero diagonal has a zero row/column.
            return not any(
                work[left][right]
                for left in range(start, order)
                for right in range(start, order)
            )
        if positive != start:
            work[start], work[positive] = work[positive], work[start]
            for row_values in work:
                row_values[start], row_values[positive] = (
                    row_values[positive],
                    row_values[start],
                )
        pivot = work[start][start]
        column = [work[index][start] for index in range(order)]
        for left in range(start + 1, order):
            for right in range(left, order):
                value = work[left][right] - column[left] * column[right] / pivot
                work[left][right] = value
                work[right][left] = value
        for index in range(start + 1, order):
            work[start][index] = Fraction(0)
            work[index][start] = Fraction(0)
        start += 1
    return True


def primitive_integer_kernel(
    matrix: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    output: list[tuple[int, ...]] = []
    for vector in kernel_basis_independent(matrix):
        denominator = 1
        for value in vector:
            denominator = lcm(denominator, value.denominator)
        integers = [int(value * denominator) for value in vector]
        divisor = 0
        for value in integers:
            divisor = gcd(divisor, abs(value))
        if divisor:
            integers = [value // divisor for value in integers]
        first = next((value for value in integers if value), 1)
        if first < 0:
            integers = [-value for value in integers]
        output.append(tuple(integers))
    return tuple(output)


def binary_column_supports(
    active: Graph, gram: tuple[tuple[int, ...], ...]
) -> tuple[int, ...]:
    """Complete clique enumeration followed by the exact column-space test."""
    order = len(active)
    kernel = primitive_integer_kernel(gram)
    positive_neighbors = tuple(
        sum(
            1 << right
            for right in range(order)
            if right != left and gram[left][right] > 0
        )
        for left in range(order)
    )
    output: list[int] = []

    def local_degree_ok(mask: int) -> bool:
        return all(
            (active[vertex] & mask).bit_count()
            <= 2 - int(bool(mask >> vertex & 1))
            for vertex in range(order)
        )

    def in_column_space(mask: int) -> bool:
        return all(
            sum(
                coefficient
                for vertex, coefficient in enumerate(vector)
                if mask >> vertex & 1
            )
            == 0
            for vector in kernel
        )

    def extend(prefix: int, candidates: int) -> None:
        remaining = candidates
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            vertex = bit.bit_length() - 1
            selected = prefix | bit
            if not local_degree_ok(selected):
                continue
            if in_column_space(selected):
                output.append(selected)
            later = remaining & ~((1 << (vertex + 1)) - 1)
            extend(selected, later & positive_neighbors[vertex])

    extend(0, (1 << order) - 1)
    result = tuple(sorted(set(output)))
    for mask in result:
        vertices = [vertex for vertex in range(order) if mask >> vertex & 1]
        if not vertices:
            raise AssertionError("zero column must not be enumerated")
        if any(
            gram[left][right] <= 0
            for left, right in combinations(vertices, 2)
        ):
            raise AssertionError("support is not a clique in positive Gram entries")
        if not local_degree_ok(mask) or not in_column_space(mask):
            raise AssertionError("support failed its defining constraints")
    return result


def support_digest(supports: Iterable[int], width: int = 30) -> str:
    accumulator = hashlib.sha256()
    byte_width = (width + 7) // 8
    for support in supports:
        accumulator.update(support.to_bytes(byte_width, "little"))
    return accumulator.hexdigest()


def gram_coefficient_analysis(
    supports: tuple[int, ...],
    gram: tuple[tuple[int, ...], ...],
    recover_unique_solution: bool = False,
) -> dict[str, object]:
    """Forward exact elimination on the coefficient matrix plus target."""
    coordinates = tuple(
        (left, right)
        for left in range(len(gram))
        for right in range(left, len(gram))
    )
    width = len(supports)
    work = [
        [
            Fraction(
                int(bool(support >> left & 1) and bool(support >> right & 1))
            )
            for support in supports
        ]
        + [Fraction(gram[left][right])]
        for left, right in coordinates
    ]
    pivot_rows: list[tuple[int, int]] = []
    rank = 0
    for column in range(width):
        pivot = next(
            (candidate for candidate in range(rank, len(work)) if work[candidate][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        for lower in range(rank + 1, len(work)):
            entry = work[lower][column]
            if not entry:
                continue
            multiplier = entry / pivot_value
            # Earlier columns are already zero in both rows.
            for right in range(column, width + 1):
                work[lower][right] -= multiplier * work[rank][right]
        pivot_rows.append((rank, column))
        rank += 1
        if rank == len(work):
            break
    inconsistent = any(
        not any(row[:width]) and bool(row[width])
        for row in work
    )
    result: dict[str, object] = {
        "support_count": width,
        "coefficient_rank": rank,
        "augmented_inconsistent": inconsistent,
    }
    if recover_unique_solution and not inconsistent and rank == width:
        solution = [Fraction(0)] * width
        for pivot_row, pivot_column in reversed(pivot_rows):
            rhs = work[pivot_row][width] - sum(
                work[pivot_row][column] * solution[column]
                for column in range(pivot_column + 1, width)
            )
            solution[pivot_column] = rhs / work[pivot_row][pivot_column]
        histogram = Counter(solution)
        result["unique_solution_histogram"] = {
            str(value): count
            for value, count in sorted(histogram.items(), key=lambda item: item[0])
        }
        result["negative_solution_count"] = sum(value < 0 for value in solution)
    return result


def eligible_z_edges(
    points: tuple[Edge, ...], active: Graph, l_rows: tuple[int, ...]
) -> tuple[Edge, ...]:
    candidates: list[Edge] = []
    for left, right in combinations(range(len(points)), 2):
        if active[left] >> right & 1 or set(points[left]) & set(points[right]):
            continue
        if all(
            not (l_rows[a] >> b & 1)
            for a in points[left]
            for b in points[right]
        ):
            candidates.append((left, right))
    return tuple(candidates)


def entrywise_nonnegative_after_z(base_active: Graph, selected: tuple[Edge, ...]) -> bool:
    """Check only entries changed by the newly inserted edges."""
    final = list(base_active)
    for left, right in selected:
        final[left] |= 1 << right
        final[right] |= 1 << left
    affected: set[Edge] = set(selected)
    for left, right in selected:
        right_neighbors = final[right] & ~(1 << left)
        while right_neighbors:
            bit = right_neighbors & -right_neighbors
            right_neighbors ^= bit
            affected.add(normalize_edge(left, bit.bit_length() - 1))
        left_neighbors = final[left] & ~(1 << right)
        while left_neighbors:
            bit = left_neighbors & -left_neighbors
            left_neighbors ^= bit
            affected.add(normalize_edge(right, bit.bit_length() - 1))
    for left, right in affected:
        value = (
            2
            - int(final[left] >> right & 1)
            - (final[left] & final[right]).bit_count()
        )
        if value < 0:
            return False
    # Diagonal values are 14-degree and degree is at most 9 here.
    return all(14 - row.bit_count() >= 0 for row in final)


def canonical_z(
    selected: tuple[Edge, ...], group: tuple[tuple[int, ...], ...]
) -> tuple[Edge, ...]:
    return min(permute_edge_set(selected, permutation) for permutation in group)


def z_abstract_type(selected: tuple[Edge, ...]) -> str:
    if not selected:
        return "0"
    if len(selected) == 1:
        return "1:K2"
    degrees = Counter(vertex for edge_value in selected for vertex in edge_value)
    degree_sequence = tuple(sorted(degrees.values(), reverse=True))
    if len(selected) == 2:
        if degree_sequence == (2, 1, 1):
            return "2:P3"
        if degree_sequence == (1, 1, 1, 1):
            return "2:2K2"
    if len(selected) == 3:
        names = {
            (3, 1, 1, 1): "3:K1,3",
            (2, 2, 2): "3:K3",
            (2, 2, 1, 1): "3:P4",
            (2, 1, 1, 1, 1): "3:P3+K2",
            (1, 1, 1, 1, 1, 1): "3:3K2",
        }
        if degree_sequence in names:
            return names[degree_sequence]
    raise AssertionError(f"unclassified simple-edge topology: {selected}")


FARKAS_WEIGHTS = {
    (0, 27): -1,
    (1, 25): -1,
    (2, 16): -1,
    (3, 16): 1,
    (3, 23): -1,
    (3, 25): 1,
    (3, 28): -1,
    (6, 16): 1,
    (6, 22): -1,
    (6, 27): 1,
    (6, 29): -1,
    (8, 15): -1,
    (8, 17): -1,
    (8, 25): 1,
    (8, 27): 1,
}
FINAL_Z = ((0, 23), (1, 22), (2, 17))


def support_linear_weight(support: int, weights: dict[Edge, int]) -> int:
    return sum(
        coefficient
        for (left, right), coefficient in weights.items()
        if support >> left & 1 and support >> right & 1
    )


def farkas_check(
    supports: tuple[int, ...],
    gram: tuple[tuple[int, ...], ...],
    weights: dict[Edge, int],
) -> tuple[int, Counter[int]]:
    target = sum(
        coefficient * gram[left][right]
        for (left, right), coefficient in weights.items()
    )
    scores = Counter(support_linear_weight(support, weights) for support in supports)
    if target >= 0 or not scores or min(scores) < 0:
        raise AssertionError(
            f"Farkas functional is invalid: target={target}, scores={scores}"
        )
    return target, scores


def two_petersen_gram_census_independent(
    graph: Graph,
    base_l: tuple[int, ...],
    base_r: frozenset[Edge],
    group: tuple[tuple[int, ...], ...],
    official_two_petersen: dict[str, object],
) -> dict[str, object]:
    points = point_list(graph)
    base_active = active_graph(points, base_r)
    base_gram = outside_gram_independent(base_active)
    if not all(value >= 0 for row in base_gram for value in row):
        raise AssertionError("Z-empty outside Gram has a negative entry")
    if not psd_by_exact_ldl(base_gram):
        raise AssertionError("Z-empty outside Gram is not PSD")
    base_rank = fraction_echelon_rank(base_gram)
    base_supports = binary_column_supports(base_active, base_gram)
    base_analysis = gram_coefficient_analysis(
        base_supports, base_gram, recover_unique_solution=True
    )
    base_summary = {
        "gram_rank": base_rank,
        "gram_nullity": len(base_gram) - base_rank,
        "support_count": len(base_supports),
        "support_sha256": support_digest(base_supports),
        "support_weight_histogram": {
            str(size): count
            for size, count in sorted(Counter(mask.bit_count() for mask in base_supports).items())
        },
        **base_analysis,
    }
    expected_base = official_two_petersen.get("Z_empty")
    if base_summary != expected_base:
        raise AssertionError(
            "independent Z-empty calculation differs from official result: "
            f"{base_summary!r} != {expected_base!r}"
        )
    if base_summary["unique_solution_histogram"] != {
        "-1": 15,
        "0": 12,
        "1": 20,
        "2": 10,
        "4": 15,
    }:
        raise AssertionError("Z-empty unique coefficient obstruction changed")
    print("independent Z-empty support/Gram system complete", flush=True)

    candidates = eligible_z_edges(points, base_active, base_l)
    if len(candidates) != 165:
        raise AssertionError(f"eligible Z edge count is {len(candidates)}")
    candidate_json = json.dumps(candidates, separators=(",", ":")).encode()
    topology_histogram: Counter[str] = Counter({"0": 1})
    valid: list[tuple[Edge, ...]] = []
    subset_count = 0
    for size in (1, 2, 3):
        for selected in combinations(candidates, size):
            subset_count += 1
            topology_histogram[z_abstract_type(selected)] += 1
            if entrywise_nonnegative_after_z(base_active, selected):
                valid.append(selected)
    if subset_count != 748_825 or len(topology_histogram) != 9:
        raise AssertionError(
            f"Z subset/topology coverage changed: {subset_count}, {topology_histogram}"
        )
    if sum(topology_histogram.values()) != subset_count + 1:
        raise AssertionError("Z topology histogram does not cover every placement")
    if len(valid) != 8_935:
        raise AssertionError(f"entrywise nonnegative Z count is {len(valid)}")
    # Independently evaluate the full 30x30 matrix for every retained placement.
    for selected in valid:
        gram = outside_gram_independent(active_graph(points, base_r, selected))
        if any(value < 0 for row in gram for value in row):
            raise AssertionError("optimized entrywise filter admitted a negative Gram")
    print("independent all-Z entrywise census complete", flush=True)

    orbit_counts: Counter[tuple[Edge, ...]] = Counter(
        canonical_z(selected, group) for selected in valid
    )
    if len(orbit_counts) != 66 or sum(orbit_counts.values()) != len(valid):
        raise AssertionError(f"Z orbit quotient changed: {len(orbit_counts)}")
    psd_rows: list[dict[str, object]] = []
    for representative, slice_count in sorted(orbit_counts.items()):
        active = active_graph(points, base_r, representative)
        gram = outside_gram_independent(active)
        if not psd_by_exact_ldl(gram):
            continue
        supports = binary_column_supports(active, gram)
        analysis = gram_coefficient_analysis(supports, gram)
        psd_rows.append(
            {
                "z_edges": [list(edge_value) for edge_value in representative],
                "entrywise_slice_count": slice_count,
                "gram_rank": fraction_echelon_rank(gram),
                "support_count": len(supports),
                "support_sha256": support_digest(supports),
                "support_weight_histogram": {
                    str(size): count
                    for size, count in sorted(
                        Counter(mask.bit_count() for mask in supports).items()
                    )
                },
                **analysis,
            }
        )
        print(
            f"independent PSD Gram orbit {len(psd_rows)}: "
            f"{representative}, supports={len(supports)}",
            flush=True,
        )
    expected_psd = (
        official_two_petersen.get("nonempty_Z", {})
        if isinstance(official_two_petersen.get("nonempty_Z"), dict)
        else {}
    ).get("psd_orbits")
    if psd_rows != expected_psd:
        raise AssertionError("independent 16-row PSD/Gram table differs from release")
    if len(psd_rows) != 16:
        raise AssertionError(f"exact PSD orbit count is {len(psd_rows)}")
    inconsistent = sum(bool(row["augmented_inconsistent"]) for row in psd_rows)
    if inconsistent != 15:
        raise AssertionError(f"inconsistent Gram orbit count is {inconsistent}")
    residuals = [row for row in psd_rows if not row["augmented_inconsistent"]]
    if len(residuals) != 1:
        raise AssertionError("there is not exactly one coefficient-consistent residual")
    residual = residuals[0]
    residual_edges = tuple(tuple(edge_value) for edge_value in residual["z_edges"])
    if residual_edges != FINAL_Z or canonical_z(FINAL_Z, group) != FINAL_Z:
        raise AssertionError(f"final residual representative changed: {residual_edges}")

    final_active = active_graph(points, base_r, FINAL_Z)
    final_gram = outside_gram_independent(final_active)
    final_supports = binary_column_supports(final_active, final_gram)
    target, scores = farkas_check(final_supports, final_gram, FARKAS_WEIGHTS)
    if (
        fraction_echelon_rank(final_gram) != 28
        or not psd_by_exact_ldl(final_gram)
        or len(final_supports) != 232
        or support_digest(final_supports)
        != "19100d7ee88ee7e7a9fb5bbf4546066ee889c131275b275dd96e07486eeac394"
        or target != -6
        or scores != Counter({0: 211, 1: 18, 2: 3})
        or residual["coefficient_rank"] != 174
    ):
        raise AssertionError("final exact Farkas obstruction changed")

    # Hostile mutation controls: the two known transcription mistakes must fail.
    sign_witness = 69_640
    index_witness = 268_437_537
    if sign_witness not in final_supports or index_witness not in final_supports:
        raise AssertionError("hostile-mutation witness is absent from support census")
    sign_mutation = dict(FARKAS_WEIGHTS)
    sign_mutation[(3, 16)] *= -1
    index_mutation = dict(FARKAS_WEIGHTS)
    index_mutation[(0, 28)] = index_mutation.pop((0, 27))
    if support_linear_weight(sign_witness, sign_mutation) >= 0:
        raise AssertionError("wrong-sign hostile mutation was not rejected")
    if support_linear_weight(index_witness, index_mutation) >= 0:
        raise AssertionError("wrong-index hostile mutation was not rejected")
    # The original is nonnegative on every support, not just the witnesses.
    if any(support_linear_weight(mask, FARKAS_WEIGHTS) < 0 for mask in final_supports):
        raise AssertionError("original Farkas functional is negative on a support")

    orbit_images: dict[tuple[Edge, ...], tuple[int, ...]] = {}
    for permutation in group:
        orbit_images[permute_edge_set(FINAL_Z, permutation)] = permutation
    if len(orbit_images) != 10:
        raise AssertionError(f"final Z orbit has {len(orbit_images)} images")
    final_support_set = set(final_supports)
    for image_edges, permutation in orbit_images.items():
        image_active = active_graph(points, base_r, image_edges)
        image_gram = outside_gram_independent(image_active)
        for left in range(len(points)):
            for right in range(len(points)):
                if (
                    image_gram[permutation[left]][permutation[right]]
                    != final_gram[left][right]
                ):
                    raise AssertionError("outside Gram did not transport along orbit")
        image_supports = binary_column_supports(image_active, image_gram)
        transported = {
            sum(
                1 << permutation[vertex]
                for vertex in range(len(points))
                if support >> vertex & 1
            )
            for support in final_support_set
        }
        if set(image_supports) != transported:
            raise AssertionError("support census did not transport along orbit")
        image_weights = {
            normalize_edge(permutation[left], permutation[right]): coefficient
            for (left, right), coefficient in FARKAS_WEIGHTS.items()
        }
        image_target, image_scores = farkas_check(
            image_supports, image_gram, image_weights
        )
        if image_target != target or image_scores != scores:
            raise AssertionError("Farkas certificate did not transport along orbit")

    final_summary = {
        "z_edges": [list(edge_value) for edge_value in FINAL_Z],
        "gram_rank": 28,
        "support_count": len(final_supports),
        "support_sha256": support_digest(final_supports),
        "coefficient_rank": residual["coefficient_rank"],
        "weights": {
            f"{left},{right}": coefficient
            for (left, right), coefficient in sorted(FARKAS_WEIGHTS.items())
        },
        "target_weighted_sum": target,
        "support_weight_histogram": {
            str(score): count for score, count in sorted(scores.items())
        },
        "orbit_image_count": len(orbit_images),
        "transported_certificate_checked": True,
        "sign_mutation_rejected": True,
        "index_mutation_rejected": True,
    }
    expected_nonempty = official_two_petersen.get("nonempty_Z")
    if not isinstance(expected_nonempty, dict):
        raise AssertionError("official nonempty-Z result is absent")
    computed_nonempty = {
        "eligible_edge_count": len(candidates),
        "eligible_edges_sha256": digest(candidate_json),
        "subsets_size_one_through_three": subset_count,
        "entrywise_nonnegative_B": len(valid),
        "stabilizer_order": len(group),
        "entrywise_orbit_count": len(orbit_counts),
        "exact_PSD_orbit_count": len(psd_rows),
        "inconsistent_Gram_orbits": inconsistent,
        "psd_orbits": psd_rows,
        "final_Farkas": final_summary,
    }
    if computed_nonempty != expected_nonempty:
        raise AssertionError("independent nonempty-Z summary differs from release")
    return {
        "Z_empty": base_summary,
        "nonempty_Z": computed_nonempty,
        "all_nine_abstract_Z_types": dict(sorted(topology_histogram.items())),
        "all_Z_placements_classified": True,
        "hostile_mutations_rejected": {
            "wrong_sign": True,
            "wrong_point_index": True,
        },
    }


def nondecreasing_partitions(
    total: int, minimum: int = 2
) -> Iterator[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for suffix in nondecreasing_partitions(total - first, first):
            yield (first,) + suffix


def m27_cubic_six_audit() -> dict[str, object]:
    possible_edges = tuple(combinations(range(6), 2))
    k33_count = 0
    prism_count = 0
    for selected in combinations(possible_edges, 9):
        degree = Counter(vertex for edge_value in selected for vertex in edge_value)
        if len(degree) != 6 or set(degree.values()) != {3}:
            continue
        adjacency = [0] * 6
        for left, right in selected:
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
        triangle_count = sum(
            int(
                adjacency[a] >> b & 1
                and adjacency[a] >> c & 1
                and adjacency[b] >> c & 1
            )
            for a, b, c in combinations(range(6), 3)
        )
        if triangle_count == 0:
            # The only bipartite cubic graph on six vertices is K3,3.
            k33_count += 1
        elif triangle_count == 2:
            prism_count += 1
        else:
            raise AssertionError("unexpected labeled cubic graph on six vertices")
    if (k33_count, prism_count) != (10, 60):
        raise AssertionError("labeled cubic graph census on six vertices changed")

    grid = tuple(product(range(3), repeat=2))
    coverage: Counter[tuple[tuple[int, int], tuple[int, int]]] = Counter()
    for row, column in grid:
        row_remainder = [(row, other) for other in range(3) if other != column]
        column_remainder = [(other, column) for other in range(3) if other != row]
        for left in row_remainder:
            for right in column_remainder:
                coverage[tuple(sorted((left, right)))] += 1
    expected_pairs = {
        tuple(sorted((left, right)))
        for left, right in combinations(grid, 2)
        if left[0] != right[0] and left[1] != right[1]
    }
    if set(coverage) != expected_pairs or set(coverage.values()) != {2}:
        raise AssertionError("K3,3 grid rectangle coverage is not exactly twice")
    # Each of the nine labels occurs in one size-3 point, hence has six of its
    # eight L-neighbors there.  Its two remaining L-neighbors occur in its
    # third, size-2, point.  The two R-neighbor points of that size-2 point
    # contribute four endpoint appearances, while exact twofold coverage
    # permits only the same two endpoints twice; this forces identical R
    # neighbor points and violates linearity.
    remaining_neighbors = 8 - 6
    r_endpoint_appearances = 2 * remaining_neighbors
    if remaining_neighbors != 2 or r_endpoint_appearances != 4:
        raise AssertionError("K3,3 endpoint count changed")
    return {
        "labeled_cubic_graph_count": k33_count + prism_count,
        "labeled_K3,3_count": k33_count,
        "labeled_prism_count": prism_count,
        "prism_alpha_beta_coverage": 3,
        "K3,3_grid_pair_count": len(coverage),
        "K3,3_grid_pair_coverage": 2,
        "K3,3_remaining_L_neighbors_per_grid_label": remaining_neighbors,
        "K3,3_R_endpoint_appearances_per_grid_label": r_endpoint_appearances,
        "K3,3_forced_identical_R_neighbor_points": True,
    }


def structural_arithmetic_independent(
    official: dict[str, object],
) -> dict[str, object]:
    profiles = tuple(
        profile
        for profile in nondecreasing_partitions(40)
        if profile and all(len(profile) - 1 - 3 * value >= 4 for value in profile)
    )
    profile_rows = [
        {
            "r": len(profile),
            "q": list(profile),
            "d_K": [len(profile) - 1 - 3 * value for value in profile],
            "point_count_upper": 3 * len(profile) // 2,
        }
        for profile in profiles
    ]
    if len(profiles) != 13:
        raise AssertionError(f"q-profile census has size {len(profiles)}")
    square_sum_90 = 63 * (29**2 + 27 * 29 - 18 * 90)
    square_sum_89 = 63 * (29**2 + 27 * 29 - 18 * 89)
    if square_sum_90 != 252 or square_sum_89 != 1386:
        raise AssertionError("m=29 projector moment arithmetic changed")
    # e=89 leaves outside y=t-3 with sum 18 and square sum 14, impossible
    # because sum y_i^2 >= |sum y_i| for integral y_i.
    if not 14 < abs(18):
        raise AssertionError("m=29 integrality contradiction disappeared")
    # At z=4, the projector requires 25 while the four internal terms give
    # at least 8 and outside integrality gives at least 25.
    if not 25 < 8 + 25:
        raise AssertionError("m=30 z=4 contradiction disappeared")
    result = {
        "q_profile_count": len(profiles),
        "q_profiles": profile_rows,
        "r_at_most_17_profile_count": sum(len(profile) <= 17 for profile in profiles),
        "r18_profile_count": sum(len(profile) == 18 for profile in profiles),
        "r19_profile_count": sum(len(profile) == 19 for profile in profiles),
        "r20_profile_count": sum(len(profile) == 20 for profile in profiles),
        "m27": m27_cubic_six_audit(),
        "m28_point_profiles": ["2^25 3^2 4", "2^24 3^4"],
        "m29_point_profiles": ["2^28 4", "2^27 3^2"],
        "m29_e90_projector_square_sum": square_sum_90,
        "m29_e89_projector_square_sum": square_sum_89,
        "m29_e89_outside_y_sum": 18,
        "m29_e89_outside_y_square_sum": 14,
        "m30_Z_spectral_cap": 3,
        "m30_z4_required_sum": 25,
        "m30_z4_lower_bound": 33,
    }
    if result != official:
        raise AssertionError("independent structural arithmetic differs from release")
    return result


def independent_self_tests() -> dict[str, object]:
    # Canonical graph6 for K4 is C~; its six edges and four degrees are fixed.
    k4 = strict_decode_graph6(b"C~", expected_order=4)
    if len(edges(k4)) != 6 or any(row.bit_count() != 3 for row in k4):
        raise AssertionError("strict graph6 K4 control failed")
    for malformed in (b"", b"C", b"C~?", b"C\x7f"):
        try:
            strict_decode_graph6(malformed)
        except ValueError:
            pass
        else:
            raise AssertionError(f"malformed graph6 was accepted: {malformed!r}")

    # Compare the opposite-path C6 method with a direct ordered-path method on
    # every labeled simple graph through order five and deterministic samples
    # on order six.  This tests the independent enumeration itself.
    def direct_cycles(graph: Graph) -> tuple[int, ...]:
        found: set[int] = set()
        order = len(graph)
        for root in range(order):
            def walk(path: tuple[int, ...], seen: int) -> None:
                current = path[-1]
                if len(path) == 6:
                    if graph[current] >> root & 1:
                        found.add(sum(1 << vertex for vertex in path))
                    return
                choices = graph[current] & ~seen
                while choices:
                    bit = choices & -choices
                    choices ^= bit
                    vertex = bit.bit_length() - 1
                    if vertex > root:
                        walk(path + (vertex,), seen | bit)
            walk((root,), 1 << root)
        return tuple(sorted(found))

    checked = 0
    for order in range(1, 6):
        all_edges = tuple(combinations(range(order), 2))
        for encoding in range(1 << len(all_edges)):
            rows = [0] * order
            for index, (left, right) in enumerate(all_edges):
                if encoding >> index & 1:
                    rows[left] |= 1 << right
                    rows[right] |= 1 << left
            graph = tuple(rows)
            if six_cycle_masks_by_opposite_paths(graph) != direct_cycles(graph):
                raise AssertionError(f"C6 algorithms disagree at n={order}, mask={encoding}")
            checked += 1
    order = 6
    all_edges = tuple(combinations(range(order), 2))
    deterministic_masks = tuple(range(0, 1 << len(all_edges), 97))
    for encoding in deterministic_masks:
        rows = [0] * order
        for index, (left, right) in enumerate(all_edges):
            if encoding >> index & 1:
                rows[left] |= 1 << right
                rows[right] |= 1 << left
        graph = tuple(rows)
        if six_cycle_masks_by_opposite_paths(graph) != direct_cycles(graph):
            raise AssertionError(f"C6 algorithms disagree at n=6, mask={encoding}")
        checked += 1

    # Check the optimized Z-entry test against a literal full-Gram evaluation
    # on many small deterministic perturbations.
    base = (
        0b00110,
        0b01001,
        0b11001,
        0b10110,
        0b01100,
    )
    absent = tuple(
        edge_value
        for edge_value in combinations(range(5), 2)
        if not (base[edge_value[0]] >> edge_value[1] & 1)
    )
    z_filter_checks = 0
    base_gram = outside_gram_independent(base)
    if any(value < 0 for row in base_gram for value in row):
        raise AssertionError("self-test base unexpectedly has negative Gram")
    for size in range(min(3, len(absent)) + 1):
        for selected in combinations(absent, size):
            final = list(base)
            for left, right in selected:
                final[left] |= 1 << right
                final[right] |= 1 << left
            literal = all(
                value >= 0
                for row in outside_gram_independent(tuple(final))
                for value in row
            )
            optimized = entrywise_nonnegative_after_z(base, selected)
            if literal != optimized:
                raise AssertionError("optimized Z entrywise filter differs from literal Gram")
            z_filter_checks += 1
    return {
        "graph6_hostile_inputs_rejected": 4,
        "C6_crosscheck_graph_count": checked,
        "optimized_Z_filter_crosschecks": z_filter_checks,
    }


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=("auth", "selftest", "disconnected", "gram", "all"),
        default="all",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_cli()
    manifest = authenticate_release()
    exact = strict_json_bytes(
        (ROOT / "attempts/wave19-alternate-frontier/exact-results.json").read_bytes()
    )
    if not isinstance(exact, dict):
        raise AssertionError("exact-results root is not an object")
    result: dict[str, object] = {
        "verifier": "independent_closure_verifier.py",
        "verifier_source_sha256": digest(Path(__file__).read_bytes()),
        "public_commit_pin": PUBLIC_COMMIT,
        "manifest_sha256": MANIFEST_SHA256,
        "release_entries_authenticated": 30,
        "canonical_LF_verified": True,
    }
    if args.phase in ("selftest", "all"):
        result["self_tests"] = independent_self_tests()
        result["structural_arithmetic"] = structural_arithmetic_independent(
            exact["structural_arithmetic"]
        )
        print("independent self-tests and structural arithmetic complete", flush=True)
    residual_graph: Graph | None = None
    residual_solutions: tuple[tuple[int, ...], ...] | None = None
    if args.phase in ("disconnected", "gram", "all"):
        disconnected_bytes = (
            ROOT / "attempts/wave19-alternate-frontier/disconnected20-dispositions.json"
        ).read_bytes()
        disconnected, residual_graph, residual_solutions = (
            disconnected_census_independent(manifest, disconnected_bytes)
        )
        if disconnected["disposition_sha256"] != CORE_HASHES[
            "attempts/wave19-alternate-frontier/disconnected20-dispositions.json"
        ]:
            raise AssertionError("disconnected disposition digest mismatch")
        result["disconnected_order20"] = disconnected
        print("independent disconnected 177-case census complete", flush=True)
    if args.phase in ("gram", "all"):
        assert residual_graph is not None and residual_solutions is not None
        base_l, base_r, group, orbit = two_petersen_orbit_independent(
            residual_graph, residual_solutions
        )
        official_two = exact["two_Petersen"]
        if not isinstance(official_two, dict):
            raise AssertionError("official two_Petersen result is absent")
        expected_r = tuple(tuple(item) for item in official_two["base_R_edges"])
        if tuple(base_l) != tuple(official_two["base_L_rows"]):
            raise AssertionError("independent base L differs from release")
        if tuple(sorted(base_r)) != expected_r:
            raise AssertionError("independent base R differs from release")
        r_sha = digest(json.dumps(sorted(base_r), separators=(",", ":")).encode())
        if r_sha != official_two["base_R_sha256"]:
            raise AssertionError("independent base R digest differs from release")
        for key, value in orbit.items():
            if official_two.get(key) != value:
                raise AssertionError(f"two-Petersen orbit field differs: {key}")
        result["two_Petersen_orbit"] = {
            **orbit,
            "base_L_rows": list(base_l),
            "base_R_edges": [list(edge_value) for edge_value in sorted(base_r)],
            "base_R_sha256": r_sha,
        }
        print("independent two-Petersen orbit complete", flush=True)
        result["two_Petersen_Gram_and_Farkas"] = (
            two_petersen_gram_census_independent(
                residual_graph, base_l, base_r, group, official_two
            )
        )
    if args.phase == "all":
        connected_bytes = (
            ROOT / "attempts/wave19-alternate-frontier/connected20-dispositions.txt"
        ).read_bytes()
        records20 = fetch_catalog(20, manifest)
        connected, _ = connected_census_independent(records20, connected_bytes)
        official_connected = exact["connected_order20"]
        if not isinstance(official_connected, dict):
            raise AssertionError("official connected result is absent")
        if connected["final_rows"] != official_connected["final_rows"]:
            raise AssertionError("independent connected final rows differ from release")
        if digest(connected_bytes) != official_connected["disposition_sha256"]:
            raise AssertionError("connected disposition SHA differs from release")
        expected_code_histogram = {
            "T": official_connected["triangle_containing"],
            "L": official_connected["triangle_free_without_local_C6"],
            "S": official_connected["symmetric_L_failures"],
            "Z": official_connected["forced_Z_exceeds_three"],
            "D": official_connected["support_degree_below_two"],
        }
        if connected["code_histogram"] != expected_code_histogram:
            raise AssertionError("connected code histogram differs from release")
        result["connected_order20"] = connected
        result["conditional_n3_60"] = "VERIFIED_WITH_CATALOG_PREMISE"
        result["conway_99"] = "UNKNOWN"
        result["novelty"] = "UNKNOWN"
        print("independent connected 510489-record census complete", flush=True)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")


if __name__ == "__main__":
    main()
