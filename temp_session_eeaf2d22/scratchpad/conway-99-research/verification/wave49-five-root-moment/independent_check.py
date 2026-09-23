#!/usr/bin/env python3
"""Independent exact verifier for Wave49 five-root one-free moments.

No Wave49 discovery implementation or result is imported.  The program
enumerates the finite graph universes, coefficient tensors, root-coordinate
congruences, control Gram matrices, and immutable-support witness matrices
from the frozen upstream inputs.
"""

from __future__ import annotations

import argparse
import ctypes
import functools
import hashlib
import itertools
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
N = 99
LAMBDA = 1
MU = 2
ORDERS = (5, 6, 7)
EXPECTED_LABELLED = {5: 683, 6: 13_174, 7: 394_020}
EXPECTED_UNLABELLED = {5: 21, 6: 62, 7: 208}
EXPECTED_CLASS_HASHES = {
    5: "f9bd6d5818a81c1b026ac46e467609435576a54f933e6d5beac5c13b20259686",
    6: "5cd10b0861dfba894731a89a269255a7c0a495f8ee7420552aebb13bafb8b75f",
    7: "89c646b6cae3018cad44b2f73cd1ef2569f4e108132002f0bcc7653d7229314a",
}
EXPECTED_ROOTS = {
    0: 32, 1: 32, 3: 28, 7: 22, 15: 16, 19: 16, 20: 32,
    21: 26, 23: 16, 28: 28, 29: 21, 31: 13, 54: 18, 58: 24,
    59: 16, 62: 16, 184: 16, 185: 15, 207: 10, 220: 21, 221: 12,
}

INPUT_HASHES = {
    "attempts/wave43-seven-deck-endpoint/exact-results.json":
        "06b498a736a511a7d6f5912bd4686e5d4eb30f4041477e3ee9cbc1704f1757c8",
    "attempts/wave44-rooted-flags/rooted-witness.json":
        "9be153b2487c3e07e20bffeb7ee6c890e69caa6e8d6b6e2936fbc5d8927bd5b9",
    "attempts/wave44-rooted-flags/row-system.json":
        "fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722",
    "attempts/wave45-flag-moment/checkpoint-v1-seed0-17cuts-15witnesses.json":
        "96a50f9add4b12b2c86587da29ade8b9da34f88a7b7617c048ffb7139c12b64b",
    "attempts/wave45-flag-moment/checkpoint-v1-moment-coefficients.json":
        "ffcf9f9942446d66c3559d97954217af3ba17c1978ea9417c6e99920d4a45420",
    "attempts/wave45-flag-moment/flag_moment-v1.py":
        "21ed58592eeced3433fdff0b98ae4f963b269ed0b39be05322f1dac42ce1be70",
    "attempts/wave47-three-root-moment/compact-handoff.json":
        "8b74110bc6ae983e288d448cd1a963f81521f178e8280bbbf5864274a1639a47",
    "attempts/wave47-three-root-moment/coefficients.json":
        "07b55f06ff8f7d5f2de53d92a3222366e122a7306028752ecd31c10962a824b3",
    "verification/wave47-three-root-moment/verification-results.json":
        "1c80d2b70b8e6bef42d4d9df124cc82dc9baf642d36873c61e91e8f2acc99a43",
    "verification/wave47-three-root-moment/package-manifest.sha256":
        "cec96a7cbc967bbbdc95215bc2086d3056d94966c95d7ca1d60fa731f17f58eb",
    "attempts/wave48-conic-moment/combined_sdp.py":
        "670aa656bed216b7207fadf29905a6b160af43dc29e612583156adc1be9e5053",
    "attempts/wave48-conic-moment/exact-faces.json":
        "49d157a2c6025f7a7d1149619959e3f488229d619a5c65a03a79e7a71a93f066",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def compact(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def object_hash(value: object) -> str:
    return hashlib.sha256(compact(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def strict_json(path: Path) -> Any:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def free_memory_percent() -> float:
    if os.name == "nt":
        state = MemoryStatusEx()
        state.dwLength = ctypes.sizeof(state)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
            raise OSError("GlobalMemoryStatusEx failed")
        return 100.0 * state.ullAvailPhys / state.ullTotalPhys
    page = os.sysconf("SC_PAGE_SIZE")
    return 100.0 * os.sysconf("SC_AVPHYS_PAGES") / os.sysconf("SC_PHYS_PAGES")


def memory_guard(stage: str) -> dict[str, object]:
    available = free_memory_percent()
    if available < 20.0:
        raise MemoryError(f"{available:.2f}% free memory at {stage}")
    return {"stage": stage, "free_percent": round(available, 3)}


@functools.lru_cache(maxsize=None)
def edge_pairs(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    )


@functools.lru_cache(maxsize=None)
def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edge_pairs(order))}


def edge_index(left: int, right: int, order: int) -> int:
    if left > right:
        left, right = right, left
    require(0 <= left < right < order, "invalid edge")
    return edge_positions(order)[(left, right)]


def adjacent(mask: int, left: int, right: int, order: int) -> bool:
    return bool((mask >> edge_index(left, right, order)) & 1)


def mask_from_edges(order: int, edges: Iterable[tuple[int, int]]) -> int:
    mask = 0
    for left, right in edges:
        mask |= 1 << edge_index(left, right, order)
    return mask


@functools.lru_cache(maxsize=None)
def permutation_edge_maps(order: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(
            edge_index(permutation[left], permutation[right], order)
            for left, right in edge_pairs(order)
        )
        for permutation in itertools.permutations(range(order))
    )


def edge_map_for_permutation(permutation: Sequence[int]) -> tuple[int, ...]:
    order = len(permutation)
    require(sorted(permutation) == list(range(order)), "not a permutation")
    return tuple(
        edge_index(permutation[left], permutation[right], order)
        for left, right in edge_pairs(order)
    )


def transform_mask(mask: int, edge_map: Sequence[int]) -> int:
    result = 0
    while mask:
        bit = mask & -mask
        source = bit.bit_length() - 1
        result |= 1 << edge_map[source]
        mask ^= bit
    return result


def graph_rows(mask: int, order: int) -> list[int]:
    rows = [0] * order
    for index, (left, right) in enumerate(edge_pairs(order)):
        if (mask >> index) & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return rows


def locally_admissible(mask: int, order: int) -> bool:
    rows = graph_rows(mask, order)
    for left in range(order):
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            cap = LAMBDA if adjacent(mask, left, right, order) else MU
            if common > cap:
                return False
    return True


def induced_mask(mask: int, source_order: int, vertices: Sequence[int]) -> int:
    result = 0
    target_order = len(vertices)
    for bit, (left, right) in enumerate(edge_pairs(target_order)):
        if adjacent(mask, vertices[left], vertices[right], source_order):
            result |= 1 << bit
    return result


def enumerate_classes(order: int) -> tuple[tuple[int, ...], list[int], int]:
    size = 1 << len(edge_pairs(order))
    labelled = {mask for mask in range(size) if locally_admissible(mask, order)}
    remaining = set(labelled)
    lookup = [-1] * size
    classes: list[int] = []
    maps = permutation_edge_maps(order)
    while remaining:
        seed = next(iter(remaining))
        orbit = {transform_mask(seed, edge_map) for edge_map in maps}
        require(orbit <= labelled, "admissibility not invariant")
        representative = min(orbit)
        require(representative in remaining, "partial orbit")
        classes.append(representative)
        for member in orbit:
            lookup[member] = representative
        remaining.difference_update(orbit)
    classes.sort()
    require(sum(value >= 0 for value in lookup) == len(labelled), "lookup incomplete")
    require(all(lookup[item] == item for item in classes), "noncanonical representative")
    return tuple(classes), lookup, len(labelled)


def root_mask(mask: int, order: int, roots: Sequence[int]) -> int:
    require(len(roots) == 5 and len(set(roots)) == 5, "bad root injection")
    return induced_mask(mask, order, roots)


def attachment_mask(
    mask: int, order: int, roots: Sequence[int], free_vertex: int
) -> int:
    result = 0
    for index, root in enumerate(roots):
        result |= int(adjacent(mask, root, free_vertex, order)) << index
    return result


def extension_mask(root: int, attachment: int) -> int:
    edges = [
        edge for index, edge in enumerate(edge_pairs(5)) if (root >> index) & 1
    ]
    edges.extend(
        (index, 5) for index in range(5) if (attachment >> index) & 1
    )
    return mask_from_edges(6, edges)


def attachment_universe(root: int) -> tuple[int, ...]:
    return tuple(
        attachment
        for attachment in range(32)
        if locally_admissible(extension_mask(root, attachment), 6)
    )


def enumerate_tensors(
    classes: dict[int, tuple[int, ...]]
) -> tuple[
    dict[int, list[dict[int, Counter[tuple[int, int]]]]],
    dict[str, object],
]:
    tensors: dict[int, list[dict[int, Counter[tuple[int, int]]]]] = {
        6: [], 7: []
    }
    raw_totals_ok = True
    for order in (6, 7):
        for class_index, mask in enumerate(classes[order]):
            by_root: dict[int, Counter[tuple[int, int]]] = {}
            injection_count = 0
            for roots in itertools.permutations(range(order), 5):
                injection_count += 1
                sigma = root_mask(mask, order, roots)
                nonroots = [vertex for vertex in range(order) if vertex not in roots]
                counter = by_root.setdefault(sigma, Counter())
                if order == 6:
                    attachment = attachment_mask(
                        mask, order, roots, nonroots[0]
                    )
                    counter[(attachment, attachment)] += 1
                else:
                    first = attachment_mask(mask, order, roots, nonroots[0])
                    second = attachment_mask(mask, order, roots, nonroots[1])
                    counter[(first, second)] += 1
                    counter[(second, first)] += 1
            expected = math.perm(order, 5) * (1 if order == 6 else 2)
            raw_total = sum(sum(counter.values()) for counter in by_root.values())
            raw_totals_ok &= injection_count == math.perm(order, 5)
            raw_totals_ok &= raw_total == expected
            tensors[order].append(by_root)
            if (class_index + 1) % 50 == 0:
                memory_guard(f"tensor-order-{order}-class-{class_index + 1}")
        print(f"progress: order-{order} tensors", file=sys.stderr, flush=True)
    labelled_roots = set()
    for by_root in tensors[6]:
        labelled_roots.update(by_root)
    for by_root in tensors[7]:
        labelled_roots.update(by_root)
    require(len(labelled_roots) == 683, "labelled tensor root census changed")
    require(raw_totals_ok, "raw injection totals indicate automorphism division")
    return tensors, {
        "labelled_root_tensor_count": len(labelled_roots),
        "order6_raw_total_per_class": math.perm(6, 5),
        "order7_raw_total_per_class": 2 * math.perm(7, 5),
        "all_class_totals_use_raw_ordered_injections": True,
        "automorphism_division": "none",
    }


def upper_entries(
    counter: Counter[tuple[int, int]],
    attachment_index: dict[int, int],
) -> list[list[int]]:
    result = []
    for (left, right), value in sorted(counter.items()):
        row = attachment_index[left]
        column = attachment_index[right]
        if row <= column and value:
            result.append([row, column, value])
    return result


def coefficient_document(
    classes: dict[int, tuple[int, ...]],
    tensors: dict[int, list[dict[int, Counter[tuple[int, int]]]]],
) -> dict[str, object]:
    families = []
    for sigma in classes[5]:
        attachments = attachment_universe(sigma)
        index = {item: position for position, item in enumerate(attachments)}
        records: dict[str, list[dict[str, object]]] = {"6": [], "7": []}
        for order in (6, 7):
            for class_mask, by_root in zip(classes[order], tensors[order]):
                counter = by_root.get(sigma, Counter())
                entries = upper_entries(counter, index)
                records[str(order)].append(
                    {
                        "canonical_mask": class_mask,
                        "upper_entries": entries,
                        "ordered_contribution_total": sum(counter.values()),
                    }
                )
        family_payload = {
            "root_mask": sigma,
            "attachment_masks": list(attachments),
            "dimension": len(attachments),
            "order6": records["6"],
            "order7": records["7"],
        }
        family_payload["payload_sha256"] = object_hash(family_payload)
        families.append(family_payload)
    document: dict[str, object] = {
        "format": "wave49-five-root-moment-independent-coefficients-v1",
        "edge_bit_order": [list(edge) for edge in edge_pairs(5)],
        "families": families,
    }
    document["payload_sha256_without_this_field"] = object_hash(document)
    return document


def permute_attachment(attachment: int, permutation: Sequence[int]) -> int:
    result = 0
    for source in range(5):
        if (attachment >> source) & 1:
            result |= 1 << permutation[source]
    return result


def verify_relabellings(
    classes: dict[int, tuple[int, ...]],
    tensors: dict[int, list[dict[int, Counter[tuple[int, int]]]]],
) -> dict[str, object]:
    records = []
    permutations = tuple(itertools.permutations(range(5)))
    for sigma in classes[5]:
        source_attachments = attachment_universe(sigma)
        for permutation in permutations:
            edge_map = edge_map_for_permutation(permutation)
            target = transform_mask(sigma, edge_map)
            target_attachments = attachment_universe(target)
            attachment_map = {
                item: permute_attachment(item, permutation)
                for item in source_attachments
            }
            require(
                set(attachment_map.values()) == set(target_attachments)
                and len(attachment_map) == len(target_attachments),
                "attachment relabelling is not bijective",
            )
            totals: dict[str, int] = {}
            for order in (6, 7):
                total = 0
                for by_root in tensors[order]:
                    source = by_root.get(sigma, Counter())
                    transformed = Counter(
                        {
                            (attachment_map[left], attachment_map[right]): value
                            for (left, right), value in source.items()
                        }
                    )
                    target_counter = by_root.get(target, Counter())
                    require(
                        transformed == target_counter,
                        f"order-{order} tensor congruence failed",
                    )
                    total += sum(source.values())
                totals[str(order)] = total
            records.append(
                {
                    "source_root_mask": sigma,
                    "permutation": list(permutation),
                    "target_root_mask": target,
                    "attachment_index_map": [
                        target_attachments.index(attachment_map[item])
                        for item in source_attachments
                    ],
                    "order6_total": totals["6"],
                    "order7_total": totals["7"],
                }
            )
    require(len(records) == 2_520, "S5 mapping count changed")
    return {
        "mapping_count": len(records),
        "nonidentity_mapping_count": sum(
            item["permutation"] != [0, 1, 2, 3, 4] for item in records
        ),
        "all_attachment_maps_bijective": True,
        "all_order6_tensors_congruent": True,
        "all_order7_tensors_congruent": True,
        "interpretation": "root-coordinate relabelling, not a target-graph automorphism",
        "records_sha256": object_hash(records),
        "records": records,
    }


def zero_matrix(size: int) -> list[list[int]]:
    return [[0] * size for _ in range(size)]


def add_counter_matrix(
    matrix: list[list[int]],
    counter: Counter[tuple[int, int]],
    attachment_index: dict[int, int],
    multiplier: int,
) -> None:
    if not multiplier:
        return
    for (left, right), value in counter.items():
        matrix[attachment_index[left]][attachment_index[right]] += multiplier * value


def matrix_sum(matrix: Sequence[Sequence[int]]) -> int:
    return sum(sum(row) for row in matrix)


def quadratic(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> int:
    return sum(
        vector[row] * matrix[row][column] * vector[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def automorphism_count(mask: int, order: int) -> int:
    return sum(
        transform_mask(mask, edge_map) == mask
        for edge_map in permutation_edge_maps(order)
    )


def petersen_graph() -> tuple[int, int]:
    edges: set[tuple[int, int]] = set()
    for vertex in range(5):
        edges.add(tuple(sorted((vertex, (vertex + 1) % 5))))
        edges.add((vertex, 5 + vertex))
        edges.add(tuple(sorted((5 + vertex, 5 + (vertex + 2) % 5))))
    return mask_from_edges(10, edges), 10


def clebsch_graph() -> tuple[int, int]:
    edges: set[tuple[int, int]] = set()
    for vertex in range(16):
        for difference in (1, 2, 4, 8, 15):
            other = vertex ^ difference
            if vertex < other:
                edges.add((vertex, other))
    return mask_from_edges(16, edges), 16


def srg_parameters(mask: int, order: int) -> tuple[int, int, int, int]:
    rows = graph_rows(mask, order)
    degrees = {row.bit_count() for row in rows}
    require(len(degrees) == 1, "control is not regular")
    adjacent_common = set()
    nonadjacent_common = set()
    for left in range(order):
        for right in range(left + 1, order):
            target = adjacent_common if adjacent(mask, left, right, order) else nonadjacent_common
            target.add((rows[left] & rows[right]).bit_count())
    require(len(adjacent_common) == len(nonadjacent_common) == 1, "not SRG")
    return order, next(iter(degrees)), next(iter(adjacent_common)), next(iter(nonadjacent_common))


def induced_class_counts(
    mask: int, graph_order: int, lookups: dict[int, list[int]]
) -> dict[int, Counter[int]]:
    result = {}
    for order in (5, 6, 7):
        counter = Counter()
        for vertices in itertools.combinations(range(graph_order), order):
            item = induced_mask(mask, graph_order, vertices)
            representative = lookups[order][item]
            require(representative >= 0, "control induced inadmissible class")
            counter[representative] += 1
        result[order] = counter
    return result


def direct_control_matrices(
    mask: int,
    order: int,
    canonical_roots: Sequence[int],
) -> tuple[dict[int, list[list[int]]], Counter[int]]:
    attachments = {sigma: attachment_universe(sigma) for sigma in canonical_roots}
    indices = {
        sigma: {item: position for position, item in enumerate(attachments[sigma])}
        for sigma in canonical_roots
    }
    matrices = {sigma: zero_matrix(len(attachments[sigma])) for sigma in canonical_roots}
    embeddings = Counter()
    canonical_set = set(canonical_roots)
    for roots in itertools.permutations(range(order), 5):
        sigma = root_mask(mask, order, roots)
        if sigma not in canonical_set:
            continue
        embeddings[sigma] += 1
        vector = [0] * len(attachments[sigma])
        for vertex in range(order):
            if vertex in roots:
                continue
            item = attachment_mask(mask, order, roots, vertex)
            vector[indices[sigma][item]] += 1
        matrix = matrices[sigma]
        for row, left in enumerate(vector):
            if not left:
                continue
            for column, right in enumerate(vector):
                if right:
                    matrix[row][column] += left * right
    return matrices, embeddings


def expanded_matrix(
    sigma: int,
    counts: dict[int, Counter[int]],
    classes: dict[int, tuple[int, ...]],
    tensors: dict[int, list[dict[int, Counter[tuple[int, int]]]]],
) -> list[list[int]]:
    attachments = attachment_universe(sigma)
    index = {item: position for position, item in enumerate(attachments)}
    matrix = zero_matrix(len(attachments))
    for order in (6, 7):
        for class_mask, by_root in zip(classes[order], tensors[order]):
            add_counter_matrix(
                matrix, by_root.get(sigma, Counter()), index, counts[order][class_mask]
            )
    return matrix


def verify_controls(
    classes: dict[int, tuple[int, ...]],
    lookups: dict[int, list[int]],
    tensors: dict[int, list[dict[int, Counter[tuple[int, int]]]]],
) -> list[dict[str, object]]:
    result = []
    for name, (mask, order), parameters in (
        ("Petersen", petersen_graph(), (10, 3, 0, 1)),
        ("Clebsch", clebsch_graph(), (16, 5, 0, 2)),
    ):
        require(srg_parameters(mask, order) == parameters, f"{name} parameters")
        counts = induced_class_counts(mask, order, lookups)
        direct, embeddings = direct_control_matrices(mask, order, classes[5])
        family_records = []
        for sigma in classes[5]:
            expanded = expanded_matrix(sigma, counts, classes, tensors)
            require(direct[sigma] == expanded, f"{name} root {sigma} expansion")
            expected = embeddings[sigma] * (order - 5) ** 2
            require(matrix_sum(direct[sigma]) == expected, f"{name} normalization")
            family_records.append(
                {
                    "root_mask": sigma,
                    "dimension": len(attachment_universe(sigma)),
                    "root_embeddings": embeddings[sigma],
                    "all_ones_quadratic": expected,
                    "matrix_sha256": object_hash(direct[sigma]),
                    "direct_equals_coefficient_expansion": True,
                    "exact_psd_certificate": "sum of integer attachment-count outer products",
                }
            )
        result.append(
            {
                "name": name,
                "order": order,
                "srg_parameters": list(parameters),
                "induced_subset_totals": {
                    str(suborder): sum(counts[suborder].values())
                    for suborder in (5, 6, 7)
                },
                "families": family_records,
                "family_catalog_sha256": object_hash(family_records),
            }
        )
        print(f"progress: {name} controls", file=sys.stderr, flush=True)
        memory_guard(f"control-{name}")
    return result


def support_counter(
    support: Sequence[dict[str, object]], expected_hash: str, classes7: set[int]
) -> Counter[int]:
    require(object_hash(support) == expected_hash, "support hash mismatch")
    masks = [item["canonical_mask"] for item in support]
    require(masks == sorted(masks) and len(masks) == len(set(masks)), "bad support order")
    result = Counter()
    for item in support:
        mask = item["canonical_mask"]
        count = item["count"]
        require(type(mask) is int and mask in classes7, "noncanonical support mask")
        require(type(count) is int and count > 0, "invalid support count")
        result[mask] = count
    require(sum(result.values()) == math.comb(N, 7), "support total changed")
    return result


def load_supports(classes7: set[int]) -> list[dict[str, object]]:
    wave43_path = ROOT / "attempts/wave43-seven-deck-endpoint/exact-results.json"
    wave44_path = ROOT / "attempts/wave44-rooted-flags/rooted-witness.json"
    checkpoint_path = ROOT / (
        "attempts/wave45-flag-moment/"
        "checkpoint-v1-seed0-17cuts-15witnesses.json"
    )
    wave43 = strict_json(wave43_path)
    wave44 = strict_json(wave44_path)
    checkpoint = strict_json(checkpoint_path)
    raw = [
        (
            "wave43_unrooted",
            wave43["certificate"]["support"],
            wave43["certificate"]["support_sha256"],
            wave43_path,
        ),
        (
            "wave44_rooted",
            wave44["support"],
            wave44["support_sha256"],
            wave44_path,
        ),
    ]
    for item in checkpoint["witnesses"]:
        raw.append(
            (
                f"wave45_iteration_{item['iteration']}",
                item["support"],
                item["support_sha256"],
                checkpoint_path,
            )
        )
    require(len(raw) == 17, "support census changed")
    result = []
    for name, support, support_hash, path in raw:
        counts = support_counter(support, support_hash, classes7)
        result.append(
            {
                "name": name,
                "input_path": path.relative_to(ROOT).as_posix(),
                "input_sha256": sha256_file(path),
                "support": support,
                "support_sha256": support_hash,
                "counts7": counts,
            }
        )
    return result


def lower_deck_tables(
    classes: dict[int, tuple[int, ...]], lookups: dict[int, list[int]]
) -> dict[int, dict[int, Counter[int]]]:
    result: dict[int, dict[int, Counter[int]]] = {5: {}, 6: {}}
    for seven in classes[7]:
        for order in (5, 6):
            deck = Counter()
            for vertices in itertools.combinations(range(7), order):
                submask = induced_mask(seven, 7, vertices)
                representative = lookups[order][submask]
                require(representative >= 0, "lower deck inadmissible")
                deck[representative] += 1
            require(sum(deck.values()) == math.comb(7, order), "deck total")
            result[order][seven] = deck
    return result


def derive_counts(
    counts7: Counter[int],
    classes: dict[int, tuple[int, ...]],
    decks: dict[int, dict[int, Counter[int]]],
) -> dict[int, Counter[int]]:
    result = {7: Counter(counts7)}
    for order in (5, 6):
        numerator = Counter()
        for seven, count in counts7.items():
            for lower, multiplicity in decks[order][seven].items():
                numerator[lower] += count * multiplicity
        divisor = math.comb(N - order, 7 - order)
        counts = Counter()
        for mask in classes[order]:
            value = numerator[mask]
            require(value % divisor == 0, "nonintegral lower deck")
            quotient = value // divisor
            require(quotient >= 0, "negative lower count")
            if quotient:
                counts[mask] = quotient
        require(sum(counts.values()) == math.comb(N, order), "lower total")
        result[order] = counts
    return result


def sparse_count_hash(counts: Counter[int]) -> str:
    return object_hash(
        [
            {"canonical_mask": mask, "count": counts[mask]}
            for mask in sorted(counts)
            if counts[mask]
        ]
    )


def primitive(vector: Sequence[int]) -> list[int]:
    divisor = 0
    for value in vector:
        divisor = math.gcd(divisor, abs(int(value)))
    require(divisor > 0, "zero direction")
    result = [int(value) // divisor for value in vector]
    first = next(value for value in result if value)
    if first < 0:
        result = [-value for value in result]
    return result


def find_negative_direction(matrix: Sequence[Sequence[int]]) -> tuple[list[int], int]:
    """Use floating point only to propose; certify the returned vector exactly."""

    import numpy as np

    array = np.asarray(matrix, dtype=np.float64)
    eigenvalues, eigenvectors = np.linalg.eigh(array)
    order = np.argsort(eigenvalues)
    for eigen_index in order:
        vector = eigenvectors[:, eigen_index]
        for scale in (8, 16, 32, 64, 128, 256, 512, 1024, 4096, 16384):
            candidate = np.rint(vector * scale).astype(object).tolist()
            if not any(candidate):
                continue
            direction = primitive(candidate)
            value = quadratic(matrix, direction)
            if value < 0:
                return direction, value
        if eigenvalues[eigen_index] >= 0:
            break
    # Exact deterministic fallback over sparse two-coordinate directions.
    size = len(matrix)
    for left in range(size):
        for right in range(left + 1, size):
            for sign in (-1, 1):
                direction = [0] * size
                direction[left] = 1
                direction[right] = sign
                value = quadratic(matrix, direction)
                if value < 0:
                    return direction, value
    raise AssertionError("no exact negative integer direction found")


def verify_witnesses(
    supports: list[dict[str, object]],
    classes: dict[int, tuple[int, ...]],
    tensors: dict[int, list[dict[int, Counter[tuple[int, int]]]]],
    decks: dict[int, dict[int, Counter[int]]],
) -> list[dict[str, object]]:
    automorphisms = {
        sigma: automorphism_count(sigma, 5) for sigma in classes[5]
    }
    result = []
    matrix_count = 0
    for support in supports:
        counts = derive_counts(support["counts7"], classes, decks)
        family_records = []
        for sigma in classes[5]:
            matrix = expanded_matrix(sigma, counts, classes, tensors)
            expected = counts[5][sigma] * automorphisms[sigma] * 94**2
            require(matrix_sum(matrix) == expected, "witness all-ones normalization")
            direction, value = find_negative_direction(matrix)
            require(
                len(direction) == len(attachment_universe(sigma))
                and quadratic(matrix, direction) == value < 0,
                "negative direction failed exact replay",
            )
            family_records.append(
                {
                    "root_mask": sigma,
                    "dimension": len(attachment_universe(sigma)),
                    "root_automorphism_count": automorphisms[sigma],
                    "ordered_root_embeddings_at_n99": (
                        counts[5][sigma] * automorphisms[sigma]
                    ),
                    "all_ones_quadratic": expected,
                    "matrix_sha256": object_hash(matrix),
                    "negative_direction": direction,
                    "negative_quadratic": value,
                    "direction_sha256": object_hash(direction),
                }
            )
            matrix_count += 1
        result.append(
            {
                "name": support["name"],
                "input_path": support["input_path"],
                "input_sha256": support["input_sha256"],
                "support_sha256": support["support_sha256"],
                "support_size": len(support["support"]),
                "lower_deck_sha256": {
                    "5": sparse_count_hash(counts[5]),
                    "6": sparse_count_hash(counts[6]),
                },
                "seven_subset_total": sum(counts[7].values()),
                "families": family_records,
                "family_catalog_sha256": object_hash(family_records),
            }
        )
        print(f"progress: witness {support['name']}", file=sys.stderr, flush=True)
        memory_guard(f"witness-{support['name']}")
    require(matrix_count == 357, "witness matrix census changed")
    return result


def verify_input_hashes() -> dict[str, str]:
    result = {}
    for relative, expected in INPUT_HASHES.items():
        actual = sha256_file(ROOT / relative)
        require(actual == expected, f"frozen input changed: {relative}")
        result[relative] = actual
    return result


def compute(coefficient_output: Path) -> dict[str, object]:
    coefficient_output = coefficient_output.resolve()
    samples = [memory_guard("start")]
    inputs = verify_input_hashes()
    classes: dict[int, tuple[int, ...]] = {}
    lookups: dict[int, list[int]] = {}
    labelled_counts = {}
    for order in ORDERS:
        class_list, lookup, labelled = enumerate_classes(order)
        require(labelled == EXPECTED_LABELLED[order], f"labelled order-{order}")
        require(len(class_list) == EXPECTED_UNLABELLED[order], f"classes order-{order}")
        require(object_hash(list(class_list)) == EXPECTED_CLASS_HASHES[order],
                f"class hash order-{order}")
        classes[order] = class_list
        lookups[order] = lookup
        labelled_counts[str(order)] = labelled
        print(f"progress: classes order {order}", file=sys.stderr, flush=True)
        samples.append(memory_guard(f"classes-{order}"))

    root_dimensions = {
        sigma: len(attachment_universe(sigma)) for sigma in classes[5]
    }
    require(root_dimensions == EXPECTED_ROOTS, "root family dimensions changed")
    tensors, tensor_summary = enumerate_tensors(classes)
    samples.append(memory_guard("tensors"))
    coefficients = coefficient_document(classes, tensors)
    coefficient_output.write_bytes(canonical(coefficients))
    relabellings = verify_relabellings(classes, tensors)
    samples.append(memory_guard("relabel"))
    print("progress: S5 congruences", file=sys.stderr, flush=True)
    controls = verify_controls(classes, lookups, tensors)
    supports = load_supports(set(classes[7]))
    decks = lower_deck_tables(classes, lookups)
    witnesses = verify_witnesses(supports, classes, tensors, decks)
    samples.append(memory_guard("complete"))

    return {
        "format": "wave49-five-root-moment-independent-v1",
        "role": "verifier",
        "claim_label": "CANDIDATE_PRECOMPARISON",
        "scope": (
            "exact finite five-root one-free coefficient tensors, all S5 "
            "coordinate congruences, two graph controls, and 17 by 21 "
            "immutable-support witness matrices"
        ),
        "inputs": inputs,
        "classes": {
            "labelled_counts": labelled_counts,
            "unlabelled_counts": {
                str(order): len(classes[order]) for order in ORDERS
            },
            "canonical_masks": {
                str(order): list(classes[order]) for order in ORDERS
            },
            "canonical_stream_sha256": {
                str(order): object_hash(list(classes[order])) for order in ORDERS
            },
        },
        "families": {
            "canonical_root_count": len(classes[5]),
            "labelled_root_count": EXPECTED_LABELLED[5],
            "root_attachment_dimensions": {
                str(sigma): root_dimensions[sigma] for sigma in classes[5]
            },
            "coefficient_path": coefficient_output.relative_to(ROOT.resolve()).as_posix(),
            "coefficient_file_sha256": sha256_file(coefficient_output),
            "coefficient_payload_sha256": coefficients[
                "payload_sha256_without_this_field"
            ],
            "tensor_summary": tensor_summary,
        },
        "root_relabelling": relabellings,
        "controls": controls,
        "witnesses": witnesses,
        "summary": {
            "canonical_families": 21,
            "labelled_root_tensors": 683,
            "s5_mapping_checks": relabellings["mapping_count"],
            "control_matrix_checks": sum(len(item["families"]) for item in controls),
            "witness_supports": len(witnesses),
            "witness_matrix_checks": sum(len(item["families"]) for item in witnesses),
            "exact_negative_directions": sum(
                len(item["families"]) for item in witnesses
            ),
            "all_negative_directions_exact": True,
            "numerical_sdp_used_as_evidence": False,
        },
        "resource_guard": {
            "minimum_free_physical_memory_percent": 20.0,
            "samples": samples,
            "status": "PASS",
        },
        "scope_wall": {
            "endpoint_n3_4158": "UNKNOWN",
            "branch_closure": "UNKNOWN",
            "strict_upper_bound": "UNKNOWN",
            "graph_construction": "NOT_PROVED",
            "novelty": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "Coordinate congruence is not a target-graph automorphism.",
            "No automorphism divisor appears in coefficient totals.",
            "Integer negative directions refute only the 17 supplied aggregate supports.",
            "Numerical SDP status, duals, residuals, and eigenvalues are not evidence.",
            "No endpoint or Conway-99 conclusion follows.",
        ],
    }


def validate(result: dict[str, object]) -> None:
    require(result["format"] == "wave49-five-root-moment-independent-v1", "format")
    summary = result["summary"]
    require(summary["canonical_families"] == 21, "family count")
    require(summary["labelled_root_tensors"] == 683, "labelled roots")
    require(summary["s5_mapping_checks"] == 2_520, "mapping count")
    require(summary["control_matrix_checks"] == 42, "control count")
    require(summary["witness_supports"] == 17, "support count")
    require(summary["witness_matrix_checks"] == 357, "witness matrix count")
    require(summary["exact_negative_directions"] == 357, "direction count")
    require(summary["numerical_sdp_used_as_evidence"] is False, "numeric promotion")
    require(result["scope_wall"]["endpoint_n3_4158"] == "UNKNOWN", "scope wall")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--compute", metavar="OUTPUT")
    group.add_argument("--validate", metavar="INPUT")
    parser.add_argument(
        "--coefficients",
        default=str(HERE / "independent-coefficients.json"),
    )
    args = parser.parse_args()
    if args.compute:
        result = compute(Path(args.coefficients))
        validate(result)
        Path(args.compute).write_bytes(canonical(result))
    else:
        result = strict_json(Path(args.validate))
        validate(result)
    print("PASS: Wave49 clean-room finite reconstruction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
