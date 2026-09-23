#!/usr/bin/env python3
"""Exact Wave 49 five-root, one-free-vertex finite moments.

This construction is independent of the Wave 47 discovery implementation.
It exhausts the local graph class streams, builds coefficient tensors for all
683 labelled admissible five-root masks in one grouped pass, retains the 21
canonical representatives, proves all S5 relabelling congruences exactly,
checks Petersen/Clebsch direct outer-product controls, and evaluates the 17
immutable Wave45-v1 witnesses with exact integer arithmetic.
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
import re
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT_FREEZE = HERE / "input-freeze.sha256"
COEFFICIENT_OUTPUT = HERE / "coefficients.json"
RESULT_OUTPUT = HERE / "results.json"

N = 99
K = 14
LAMBDA = 1
MU = 2
MIN_FREE_MEMORY_PERCENT = 20.0
UNION_ORDERS = (6, 7)
ROOT_MASKS_AND_SIZES = (
    (0, 32),
    (1, 32),
    (3, 28),
    (7, 22),
    (15, 16),
    (19, 16),
    (20, 32),
    (21, 26),
    (23, 16),
    (28, 28),
    (29, 21),
    (31, 13),
    (54, 18),
    (58, 24),
    (59, 16),
    (62, 16),
    (184, 16),
    (185, 15),
    (207, 10),
    (220, 21),
    (221, 12),
)
ROOT_MASKS = tuple(mask for mask, _ in ROOT_MASKS_AND_SIZES)
EXPECTED_SIZES = dict(ROOT_MASKS_AND_SIZES)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def compact_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"
    ).encode("utf-8")


def sha256_compact(value: object) -> str:
    return hashlib.sha256(compact_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


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


MEMORY_SAMPLES: list[dict[str, Any]] = []


def physical_memory() -> tuple[int, int]:
    if os.name == "nt":
        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        require(
            bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))),
            "GlobalMemoryStatusEx failed",
        )
        return int(status.ullTotalPhys), int(status.ullAvailPhys)
    page_size = os.sysconf("SC_PAGE_SIZE")
    return (
        int(page_size * os.sysconf("SC_PHYS_PAGES")),
        int(page_size * os.sysconf("SC_AVPHYS_PAGES")),
    )


def memory_guard(label: str) -> dict[str, Any]:
    total, available = physical_memory()
    percent = 100.0 * available / total
    sample = {
        "label": label,
        "total_bytes": total,
        "available_bytes": available,
        "free_percent": round(percent, 2),
    }
    MEMORY_SAMPLES.append(sample)
    print(
        f"[memory] {label}: {percent:.2f}% free "
        f"({available:,}/{total:,} bytes)",
        flush=True,
    )
    require(
        percent >= MIN_FREE_MEMORY_PERCENT,
        f"{label}: free physical memory {percent:.2f}% below floor",
    )
    return sample


def parse_input_freeze() -> dict[str, str]:
    pattern = re.compile(r"^([0-9a-f]{64})  (.+)$")
    frozen: dict[str, str] = {}
    for line in INPUT_FREEZE.read_text(encoding="utf-8").splitlines():
        match = pattern.fullmatch(line)
        require(match is not None, f"malformed input-freeze line: {line!r}")
        digest, relative = match.groups()
        require(relative not in frozen, f"duplicate frozen path: {relative}")
        path = ROOT / Path(relative)
        require(path.is_file(), f"frozen input missing: {relative}")
        require(sha256_file(path) == digest, f"frozen input hash changed: {relative}")
        frozen[relative] = digest
    return frozen


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
    return bool(mask >> edge_index(left, right, order) & 1)


def mask_from_edges(order: int, edges: Iterable[tuple[int, int]]) -> int:
    mask = 0
    for left, right in edges:
        mask |= 1 << edge_index(left, right, order)
    return mask


def edge_map_from_vertex_map(
    order: int, vertex_map: Sequence[int]
) -> tuple[int, ...]:
    require(sorted(vertex_map) == list(range(order)), "not a vertex permutation")
    return tuple(
        edge_index(vertex_map[left], vertex_map[right], order)
        for left, right in edge_pairs(order)
    )


@functools.lru_cache(maxsize=None)
def permutation_edge_maps(order: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        edge_map_from_vertex_map(order, permutation)
        for permutation in itertools.permutations(range(order))
    )


def transform_mask(mask: int, edge_map: Sequence[int]) -> int:
    transformed = 0
    remaining = mask
    while remaining:
        low = remaining & -remaining
        source = low.bit_length() - 1
        transformed |= 1 << edge_map[source]
        remaining ^= low
    return transformed


def locally_admissible(mask: int, order: int) -> bool:
    rows = [0] * order
    for index, (left, right) in enumerate(edge_pairs(order)):
        if mask >> index & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    for left in range(order):
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            cap = LAMBDA if adjacent(mask, left, right, order) else MU
            if common > cap:
                return False
    return True


def induced_mask(
    mask: int, source_order: int, vertices: Sequence[int]
) -> int:
    return mask_from_edges(
        len(vertices),
        (
            (left_index, right_index)
            for left_index, left in enumerate(vertices)
            for right_index, right in enumerate(vertices)
            if left_index < right_index
            and adjacent(mask, left, right, source_order)
        ),
    )


def enumerate_unrooted_classes(
    order: int,
) -> tuple[tuple[int, ...], list[int], int]:
    labelled = {
        mask
        for mask in range(1 << len(edge_pairs(order)))
        if locally_admissible(mask, order)
    }
    remaining = set(labelled)
    lookup = [-1] * (1 << len(edge_pairs(order)))
    classes: list[int] = []
    maps = permutation_edge_maps(order)
    while remaining:
        seed = next(iter(remaining))
        orbit = {transform_mask(seed, edge_map) for edge_map in maps}
        require(orbit.issubset(labelled), "local cap changed under relabelling")
        canonical = min(orbit)
        require(canonical in remaining, "partial graph orbit encountered")
        classes.append(canonical)
        for member in orbit:
            lookup[member] = canonical
        remaining.difference_update(orbit)
    classes.sort()
    require(
        sum(value >= 0 for value in lookup) == len(labelled),
        "canonical lookup coverage mismatch",
    )
    return tuple(classes), lookup, len(labelled)


@functools.lru_cache(maxsize=None)
def extend_root(root_mask: int, attachment: int) -> int:
    edges = [
        (left, right)
        for index, (left, right) in enumerate(edge_pairs(5))
        if root_mask >> index & 1
    ]
    edges.extend((root, 5) for root in range(5) if attachment >> root & 1)
    return mask_from_edges(6, edges)


@functools.lru_cache(maxsize=None)
def attachment_universe(root_mask: int) -> tuple[int, ...]:
    return tuple(
        attachment
        for attachment in range(32)
        if locally_admissible(extend_root(root_mask, attachment), 6)
    )


def attachment_mask(
    graph_mask: int,
    graph_order: int,
    roots: Sequence[int],
    free_vertex: int,
) -> int:
    result = 0
    for root_label, root_vertex in enumerate(roots):
        if adjacent(graph_mask, root_vertex, free_vertex, graph_order):
            result |= 1 << root_label
    return result


def transform_attachment(attachment: int, permutation: Sequence[int]) -> int:
    transformed = 0
    for old_label, new_label in enumerate(permutation):
        if attachment >> old_label & 1:
            transformed |= 1 << new_label
    return transformed


def automorphism_count(mask: int, order: int) -> int:
    return sum(
        transform_mask(mask, edge_map) == mask
        for edge_map in permutation_edge_maps(order)
    )


TensorCounter = Counter[tuple[int, int]]
LabelledTensors = dict[int, dict[tuple[int, int], TensorCounter]]


def build_all_labelled_tensors(
    class_sets: dict[int, tuple[int, ...]],
) -> tuple[LabelledTensors, dict[str, Any]]:
    tensors: defaultdict[
        int, defaultdict[tuple[int, int], TensorCounter]
    ] = defaultdict(lambda: defaultdict(Counter))
    root_embedding_totals: Counter[tuple[int, int, int]] = Counter()
    visits = {"6": 0, "7": 0}
    for order in UNION_ORDERS:
        for class_mask in class_sets[order]:
            for roots in itertools.permutations(range(order), 5):
                visits[str(order)] += 1
                root_mask = induced_mask(class_mask, order, roots)
                nonroots = tuple(
                    vertex for vertex in range(order) if vertex not in roots
                )
                key = (order, class_mask)
                root_embedding_totals[(root_mask, order, class_mask)] += 1
                if order == 6:
                    require(len(nonroots) == 1, "bad order-six complement")
                    attachment = attachment_mask(
                        class_mask, order, roots, nonroots[0]
                    )
                    require(
                        attachment in attachment_universe(root_mask),
                        "order-six attachment left its admissible universe",
                    )
                    tensors[root_mask][key][(attachment, attachment)] += 1
                else:
                    require(len(nonroots) == 2, "bad order-seven complement")
                    left = attachment_mask(class_mask, order, roots, nonroots[0])
                    right = attachment_mask(class_mask, order, roots, nonroots[1])
                    universe = attachment_universe(root_mask)
                    require(
                        left in universe and right in universe,
                        "order-seven attachment left its admissible universe",
                    )
                    tensors[root_mask][key][(left, right)] += 1
                    tensors[root_mask][key][(right, left)] += 1
            memory_guard(f"tensors-order{order}-class{class_mask}")
        print(f"[tensors] completed order {order}", flush=True)
    labelled_root_masks = tuple(sorted(tensors))
    require(len(labelled_root_masks) == 683, "labelled five-root census changed")
    for root_mask in labelled_root_masks:
        for (order, class_mask), entries in tensors[root_mask].items():
            require(
                all(
                    entries[(left, right)] == entries[(right, left)]
                    for left, right in entries
                ),
                "labelled coefficient matrix is not symmetric",
            )
            expected = root_embedding_totals[(root_mask, order, class_mask)]
            factor = 1 if order == 6 else 2
            require(
                sum(entries.values()) == factor * expected,
                "labelled coefficient all-ones total failed",
            )
    sparse_payload = [
        {
            "root_mask": root_mask,
            "records": [
                {
                    "order": order,
                    "canonical_mask": class_mask,
                    "entries": [
                        [left, right, value]
                        for (left, right), value in sorted(entries.items())
                        if value
                    ],
                }
                for (order, class_mask), entries in sorted(tensors[root_mask].items())
                if entries
            ],
        }
        for root_mask in labelled_root_masks
    ]
    stats = {
        "labelled_root_mask_count": len(labelled_root_masks),
        "ordered_root_embedding_visits": visits,
        "nonempty_root_class_records": sum(
            len(records) for records in tensors.values()
        ),
        "nonzero_ordered_attachment_entries": sum(
            len(entries)
            for records in tensors.values()
            for entries in records.values()
        ),
        "sparse_labelled_tensor_sha256": sha256_compact(sparse_payload),
    }
    return {root: dict(records) for root, records in tensors.items()}, stats


def verify_relabelling_congruence(
    tensors: LabelledTensors,
    class_sets: dict[int, tuple[int, ...]],
) -> dict[str, Any]:
    permutations = tuple(itertools.permutations(range(5)))
    mapping_checks = 0
    record_checks = 0
    nonidentity_checks = 0
    for source_root in ROOT_MASKS:
        source_flags = attachment_universe(source_root)
        for permutation in permutations:
            target_root = transform_mask(
                source_root, edge_map_from_vertex_map(5, permutation)
            )
            target_flags = attachment_universe(target_root)
            mapped_flags = tuple(
                transform_attachment(flag, permutation) for flag in source_flags
            )
            require(
                set(mapped_flags) == set(target_flags)
                and len(mapped_flags) == len(set(mapped_flags)),
                "root relabelling is not an attachment bijection",
            )
            for order in UNION_ORDERS:
                for class_mask in class_sets[order]:
                    source_entries = tensors[source_root].get(
                        (order, class_mask), Counter()
                    )
                    target_entries = tensors[target_root].get(
                        (order, class_mask), Counter()
                    )
                    mapped: TensorCounter = Counter()
                    for (left, right), value in source_entries.items():
                        mapped[
                            (
                                transform_attachment(left, permutation),
                                transform_attachment(right, permutation),
                            )
                        ] += value
                    require(
                        mapped == target_entries,
                        "S5 root relabelling changed a class coefficient tensor",
                    )
                    record_checks += 1
            mapping_checks += 1
            if permutation != tuple(range(5)):
                nonidentity_checks += 1
    require(mapping_checks == 21 * math.factorial(5), "S5 check census changed")
    return {
        "status": "PASS_EXACT",
        "canonical_root_representatives": len(ROOT_MASKS),
        "permutations_per_root": math.factorial(5),
        "mapping_checks": mapping_checks,
        "nonidentity_mapping_checks": nonidentity_checks,
        "class_tensor_record_checks": record_checks,
        "theorem": (
            "for every root permutation pi, the attachment permutation P_pi "
            "satisfies M_{pi(sigma)} = P_pi M_sigma P_pi^T coefficientwise"
        ),
        "target_graph_automorphism_assumed": False,
    }


def support_counter(
    support: Sequence[dict[str, Any]],
    expected_hash: str,
    classes7: set[int],
    label: str,
) -> Counter[int]:
    require(sha256_compact(support) == expected_hash, f"{label} support hash mismatch")
    masks = [item["canonical_mask"] for item in support]
    require(masks == sorted(masks), f"{label} support not sorted")
    require(len(masks) == len(set(masks)), f"{label} repeated support mask")
    counter: Counter[int] = Counter()
    for item in support:
        mask, count = item["canonical_mask"], item["count"]
        require(mask in classes7, f"{label} noncanonical seven-class")
        require(type(count) is int and count > 0, f"{label} bad count")
        counter[mask] = count
    require(sum(counter.values()) == math.comb(N, 7), f"{label} total changed")
    return counter


def load_witnesses(classes7: set[int]) -> list[dict[str, Any]]:
    wave43_path = ROOT / "attempts/wave43-seven-deck-endpoint/exact-results.json"
    wave44_path = ROOT / "attempts/wave44-rooted-flags/rooted-witness.json"
    checkpoint_path = (
        ROOT
        / "attempts/wave45-flag-moment/checkpoint-v1-seed0-17cuts-15witnesses.json"
    )
    wave43 = read_json(wave43_path)
    wave44 = read_json(wave44_path)
    checkpoint = read_json(checkpoint_path)
    records = [
        (
            "wave43_unrooted",
            wave43["certificate"]["support"],
            wave43["certificate"]["support_sha256"],
            wave43_path.relative_to(ROOT).as_posix(),
        ),
        (
            "wave44_rooted",
            wave44["support"],
            wave44["support_sha256"],
            wave44_path.relative_to(ROOT).as_posix(),
        ),
    ]
    records.extend(
        (
            f"wave45_iteration_{item['iteration']}",
            item["support"],
            item["support_sha256"],
            checkpoint_path.relative_to(ROOT).as_posix(),
        )
        for item in checkpoint["witnesses"]
    )
    require(len(records) == 17, "witness census changed")
    return [
        {
            "name": name,
            "support": support,
            "support_sha256": support_hash,
            "input_path": path,
            "counts7": support_counter(support, support_hash, classes7, name),
        }
        for name, support, support_hash, path in records
    ]


def lower_deck_tables(
    class_sets: dict[int, tuple[int, ...]],
    class_lookup: dict[int, list[int]],
) -> dict[int, dict[int, Counter[int]]]:
    tables: dict[int, dict[int, Counter[int]]] = {5: {}, 6: {}}
    for seven_mask in class_sets[7]:
        for order in (5, 6):
            counter: Counter[int] = Counter()
            for vertices in itertools.combinations(range(7), order):
                lower = induced_mask(seven_mask, 7, vertices)
                canonical = class_lookup[order][lower]
                require(canonical >= 0, "bad lower class")
                counter[canonical] += 1
            require(sum(counter.values()) == math.comb(7, order), "deck table total")
            tables[order][seven_mask] = counter
    return tables


def derive_counts(
    counts7: Counter[int],
    class_sets: dict[int, tuple[int, ...]],
    tables: dict[int, dict[int, Counter[int]]],
) -> dict[int, Counter[int]]:
    result = {7: Counter(counts7)}
    for order in (5, 6):
        numerator: Counter[int] = Counter()
        for seven_mask, count in counts7.items():
            for lower_mask, multiplicity in tables[order][seven_mask].items():
                numerator[lower_mask] += count * multiplicity
        divisor = math.comb(N - order, 7 - order)
        derived: Counter[int] = Counter()
        for mask in class_sets[order]:
            require(numerator[mask] % divisor == 0, "nonintegral lower deck")
            value = numerator[mask] // divisor
            require(value >= 0, "negative lower count")
            if value:
                derived[mask] = value
        require(
            sum(derived.values()) == math.comb(N, order),
            f"order-{order} lower total changed",
        )
        result[order] = derived
    return result


def sparse_count_hash(counts: Counter[int]) -> str:
    return sha256_compact(
        [
            {"canonical_mask": mask, "count": count}
            for mask, count in sorted(counts.items())
            if count
        ]
    )


def canonical_family_record(
    root_mask: int,
    tensors: LabelledTensors,
    class_sets: dict[int, tuple[int, ...]],
    lower_counts: dict[int, Counter[int]],
) -> dict[str, Any]:
    flags = attachment_universe(root_mask)
    require(len(flags) == EXPECTED_SIZES[root_mask], "attachment size changed")
    index = {flag: position for position, flag in enumerate(flags)}
    records: list[dict[str, Any]] = []
    for order in UNION_ORDERS:
        for class_mask in class_sets[order]:
            raw = tensors[root_mask].get((order, class_mask), Counter())
            upper = []
            for (left, right), value in sorted(raw.items()):
                left_index, right_index = index[left], index[right]
                if left_index <= right_index and value:
                    upper.append([left_index, right_index, value])
            records.append(
                {
                    "canonical_mask": class_mask,
                    "order": order,
                    "upper_entries": upper,
                }
            )
    aut = automorphism_count(root_mask, 5)
    root_count = lower_counts[5][root_mask]
    root_embeddings = root_count * aut
    require(root_embeddings > 0, f"root {root_mask} has zero frozen embeddings")
    return {
        "automorphism_count_of_root_type": aut,
        "class_coefficients": records,
        "flags": list(flags),
        "free_vertices_per_root_at_n99": N - 5,
        "matrix_size": len(flags),
        "normalization_denominator_at_n99": root_embeddings * (N - 5) ** 2,
        "root_embeddings_at_n99": root_embeddings,
        "root_induced_count_at_n99": root_count,
        "root_mask": root_mask,
    }


def reconstruct_coefficient_document(
    tensors: LabelledTensors,
    class_sets: dict[int, tuple[int, ...]],
    lower_counts: dict[int, Counter[int]],
    frozen_inputs: dict[str, str],
    labelled_stats: dict[str, Any],
    relabelling: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    families = {
        f"root5_{mask}": canonical_family_record(
            mask, tensors, class_sets, lower_counts
        )
        for mask in ROOT_MASKS
    }
    stats = {
        name: {
            "root_mask": family["root_mask"],
            "matrix_size": family["matrix_size"],
            "flag_sha256": sha256_compact(family["flags"]),
            "nonzero_upper_entries": sum(
                len(record["upper_entries"])
                for record in family["class_coefficients"]
            ),
            "class_coefficients_sha256": sha256_compact(
                family["class_coefficients"]
            ),
            "family_sha256": sha256_compact(family),
        }
        for name, family in families.items()
    }
    document: dict[str, Any] = {
        "class_streams": {
            str(order): {
                "count": len(class_sets[order]),
                "sha256": sha256_compact(list(class_sets[order])),
            }
            for order in (5, 6, 7)
        },
        "convention": {
            "automorphism_division": "none",
            "canonical_root_representatives": True,
            "free_vertex_attachment_bits": [0, 1, 2, 3, 4],
            "pair_of_free_vertices": "ordered",
            "root_labels_fixed_pointwise": True,
            "same_free_vertex_union_order": 6,
            "distinct_free_vertices_union_order": 7,
        },
        "families": families,
        "format": "wave49-five-root-one-free-moment-coefficients-v1",
        "input_freeze": frozen_inputs,
        "labelled_tensor_reconstruction": labelled_stats,
        "root_relabelling": relabelling,
    }
    document["payload_sha256_without_this_field"] = sha256_compact(document)
    return document, families, stats


def zero_matrix(size: int) -> list[list[int]]:
    return [[0] * size for _ in range(size)]


def add_scaled_upper(
    matrix: list[list[int]],
    entries: Sequence[Sequence[int]],
    multiplier: int,
) -> None:
    for row, column, value in entries:
        increment = multiplier * value
        matrix[row][column] += increment
        if row != column:
            matrix[column][row] += increment


def expanded_matrix(
    family: dict[str, Any], counts: dict[int, Counter[int]]
) -> list[list[int]]:
    matrix = zero_matrix(family["matrix_size"])
    for record in family["class_coefficients"]:
        multiplier = counts[record["order"]][record["canonical_mask"]]
        if multiplier:
            add_scaled_upper(matrix, record["upper_entries"], multiplier)
    return matrix


def matrix_sum(matrix: Sequence[Sequence[int]]) -> int:
    return sum(map(sum, matrix))


def quadratic(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> int:
    return sum(
        vector[row] * matrix[row][column] * vector[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def exact_inertia(matrix: Sequence[Sequence[int]]) -> tuple[int, int, int]:
    """Return exact inertia by rational symmetric congruence elimination."""

    active = [
        [Fraction(value) for value in row] for row in matrix
    ]
    positive = negative = zero = 0
    while active:
        size = len(active)
        diagonal = next(
            (index for index in range(size) if active[index][index]),
            None,
        )
        if diagonal is not None:
            if diagonal:
                active[0], active[diagonal] = active[diagonal], active[0]
                for row in active:
                    row[0], row[diagonal] = row[diagonal], row[0]
            pivot = active[0][0]
            if pivot > 0:
                positive += 1
            else:
                negative += 1
            tail = [
                [
                    active[row][column]
                    - active[row][0] * active[column][0] / pivot
                    for column in range(1, size)
                ]
                for row in range(1, size)
            ]
            active = tail
            continue
        offdiagonal = next(
            (
                (row, column)
                for row in range(size)
                for column in range(row + 1, size)
                if active[row][column]
            ),
            None,
        )
        if offdiagonal is None:
            zero += size
            break
        first, second = offdiagonal
        permutation = [first, second] + [
            index for index in range(size) if index not in (first, second)
        ]
        active = [
            [active[row][column] for column in permutation]
            for row in permutation
        ]
        pivot = active[0][1]
        positive += 1
        negative += 1
        tail = [
            [
                active[row][column]
                - (
                    active[row][0] * active[column][1]
                    + active[row][1] * active[column][0]
                )
                / pivot
                for column in range(2, size)
            ]
            for row in range(2, size)
        ]
        active = tail
    require(
        positive + negative + zero == len(matrix),
        "exact inertia dimension mismatch",
    )
    return positive, negative, zero


def primitive_vector(values: Sequence[int]) -> list[int]:
    gcd = 0
    for value in values:
        gcd = math.gcd(gcd, abs(value))
    require(gcd > 0, "zero vector")
    result = [value // gcd for value in values]
    first = next(value for value in result if value)
    if first < 0:
        result = [-value for value in result]
    return result


def exact_negative_direction(
    matrix: Sequence[Sequence[int]],
    eigenvector: Sequence[float],
) -> dict[str, Any]:
    scale_value = max(abs(float(value)) for value in eigenvector)
    require(scale_value > 0, "zero numerical eigenvector")
    for scale in (10, 20, 50, 100, 200, 500, 1_000, 2_000, 5_000, 10_000):
        candidate = [
            int(round(float(value) * scale / scale_value))
            for value in eigenvector
        ]
        if not any(candidate):
            continue
        vector = primitive_vector(candidate)
        value = quadratic(matrix, vector)
        if value < 0:
            return {
                "quadratic_numerator": value,
                "rounding_scale": scale,
                "vector": vector,
            }
    raise AssertionError("failed to rationalize an exact negative direction")


def petersen_graph() -> tuple[int, int]:
    edges: set[tuple[int, int]] = set()
    for vertex in range(5):
        edges.add((vertex, (vertex + 1) % 5))
        edges.add((vertex, 5 + vertex))
        edges.add((5 + vertex, 5 + (vertex + 2) % 5))
    return mask_from_edges(10, edges), 10


def clebsch_graph() -> tuple[int, int]:
    edges: set[tuple[int, int]] = set()
    for vertex in range(16):
        for step in (1, 2, 4, 8, 15):
            edges.add((vertex, vertex ^ step))
    return mask_from_edges(16, edges), 16


def graph_rows(mask: int, order: int) -> list[int]:
    rows = [0] * order
    for index, (left, right) in enumerate(edge_pairs(order)):
        if mask >> index & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return rows


def srg_parameters(mask: int, order: int) -> tuple[int, int, int, int]:
    rows = graph_rows(mask, order)
    degrees = {row.bit_count() for row in rows}
    require(len(degrees) == 1, "control graph not regular")
    lambdas: set[int] = set()
    mus: set[int] = set()
    for left in range(order):
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            (lambdas if adjacent(mask, left, right, order) else mus).add(common)
    require(len(lambdas) == len(mus) == 1, "control graph not strongly regular")
    return order, next(iter(degrees)), next(iter(lambdas)), next(iter(mus))


def induced_class_counts(
    mask: int,
    graph_order: int,
    class_lookup: dict[int, list[int]],
) -> dict[int, Counter[int]]:
    result: dict[int, Counter[int]] = {}
    for order in (6, 7):
        counts: Counter[int] = Counter()
        for vertices in itertools.combinations(range(graph_order), order):
            submask = induced_mask(mask, graph_order, vertices)
            canonical = class_lookup[order][submask]
            require(canonical >= 0, "control induced inadmissible class")
            counts[canonical] += 1
        result[order] = counts
    return result


def direct_outer_product(
    graph_mask: int,
    graph_order: int,
    root_mask: int,
    flags: Sequence[int],
) -> tuple[list[list[int]], int]:
    index = {flag: position for position, flag in enumerate(flags)}
    matrix = zero_matrix(len(flags))
    embeddings = 0
    for roots in itertools.permutations(range(graph_order), 5):
        if induced_mask(graph_mask, graph_order, roots) != root_mask:
            continue
        embeddings += 1
        vector = [0] * len(flags)
        for free in range(graph_order):
            if free in roots:
                continue
            attachment = attachment_mask(graph_mask, graph_order, roots, free)
            require(attachment in index, "control attachment left universe")
            vector[index[attachment]] += 1
        for row, left in enumerate(vector):
            if not left:
                continue
            for column, right in enumerate(vector):
                if right:
                    matrix[row][column] += left * right
    return matrix, embeddings


def verify_controls(
    families: dict[str, dict[str, Any]],
    class_lookup: dict[int, list[int]],
) -> list[dict[str, Any]]:
    output = []
    for name, graph_data, expected in (
        ("Petersen", petersen_graph(), (10, 3, 0, 1)),
        ("Clebsch", clebsch_graph(), (16, 5, 0, 2)),
    ):
        graph_mask, graph_order = graph_data
        require(srg_parameters(graph_mask, graph_order) == expected, "bad control")
        counts = induced_class_counts(graph_mask, graph_order, class_lookup)
        family_records = {}
        for root_mask in ROOT_MASKS:
            family_name = f"root5_{root_mask}"
            family = families[family_name]
            direct, embeddings = direct_outer_product(
                graph_mask, graph_order, root_mask, family["flags"]
            )
            expanded = expanded_matrix(family, counts)
            require(direct == expanded, f"{name} {family_name} control mismatch")
            all_ones = embeddings * (graph_order - 5) ** 2
            require(matrix_sum(direct) == all_ones, "control all-ones mismatch")
            family_records[family_name] = {
                "all_ones_quadratic": all_ones,
                "direct_equals_expansion": True,
                "exact_psd_reason": "direct sum of integer outer products",
                "matrix_sha256": sha256_compact(direct),
                "root_embeddings": embeddings,
            }
        output.append(
            {
                "families": family_records,
                "induced_subset_totals": {
                    str(order): sum(counts[order].values())
                    for order in UNION_ORDERS
                },
                "name": name,
                "order": graph_order,
                "srg_parameters": list(expected),
            }
        )
        print(f"[control] {name}: all 21 families match", flush=True)
        memory_guard(f"after-control-{name}")
    return output


def evaluate_witnesses(
    witnesses: list[dict[str, Any]],
    families: dict[str, dict[str, Any]],
    class_sets: dict[int, tuple[int, ...]],
    tables: dict[int, dict[int, Counter[int]]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    output = []
    common_lower_hashes: dict[str, str] | None = None
    total_indefinite = 0
    total_psd = 0
    targets_refuted = 0
    for witness in witnesses:
        counts = derive_counts(witness["counts7"], class_sets, tables)
        lower_hashes = {
            str(order): sparse_count_hash(counts[order]) for order in (5, 6)
        }
        if common_lower_hashes is None:
            common_lower_hashes = lower_hashes
        require(lower_hashes == common_lower_hashes, "lower decks differ")
        family_records = {}
        indefinite = 0
        for root_mask in ROOT_MASKS:
            family_name = f"root5_{root_mask}"
            family = families[family_name]
            matrix = expanded_matrix(family, counts)
            denominator = family["normalization_denominator_at_n99"]
            require(
                matrix_sum(matrix) == denominator,
                f"{witness['name']} {family_name} normalization failed",
            )
            inertia = exact_inertia(matrix)
            eigenvalues, eigenvectors = np.linalg.eigh(
                np.asarray(matrix, dtype=np.float64)
            )
            record: dict[str, Any] = {
                "exact_inertia": {
                    "positive": inertia[0],
                    "negative": inertia[1],
                    "zero": inertia[2],
                },
                "matrix_sha256": sha256_compact(matrix),
                "matrix_size": family["matrix_size"],
                "minimum_normalized_eigenvalue_float": float(
                    eigenvalues[0] / denominator
                ),
                "minimum_raw_eigenvalue_float": float(eigenvalues[0]),
                "normalization_denominator": denominator,
            }
            if inertia[1]:
                direction = exact_negative_direction(matrix, eigenvectors[:, 0])
                require(
                    direction["quadratic_numerator"] < 0,
                    "negative direction is not exact",
                )
                record["status"] = "EXACTLY_INDEFINITE"
                record["exact_negative_direction"] = direction
                indefinite += 1
                total_indefinite += 1
            else:
                record["status"] = "EXACTLY_PSD"
                record["exact_psd_reason"] = (
                    "rational symmetric congruence inertia has no negative pivot"
                )
                total_psd += 1
            family_records[family_name] = record
        if indefinite:
            targets_refuted += 1
        output.append(
            {
                "exactly_indefinite_family_count": indefinite,
                "family_results": family_records,
                "input_path": witness["input_path"],
                "name": witness["name"],
                "support_sha256": witness["support_sha256"],
            }
        )
        print(
            f"[witness] {witness['name']}: {indefinite}/21 indefinite",
            flush=True,
        )
        memory_guard(f"after-witness-{witness['name']}")
    require(len(output) == 17, "witness output census changed")
    return output, {
        "common_lower_deck_sha256": common_lower_hashes,
        "exactly_indefinite_matrices": total_indefinite,
        "exactly_psd_matrices": total_psd,
        "matrix_total": total_indefinite + total_psd,
        "targets_refuted_by_at_least_one_family": targets_refuted,
    }


def self_tests() -> dict[str, Any]:
    require(len(ROOT_MASKS) == 21 and len(set(ROOT_MASKS)) == 21, "root list")
    k4 = mask_from_edges(4, itertools.combinations(range(4), 2))
    require(not locally_admissible(k4, 4), "K4 should fail local cap")
    c5 = mask_from_edges(5, ((0, 1), (1, 2), (2, 3), (3, 4), (4, 0)))
    require(locally_admissible(c5, 5), "C5 should pass local cap")
    require(
        transform_attachment(0b00101, (4, 3, 2, 1, 0)) == 0b10100,
        "attachment permutation orientation changed",
    )
    return {
        "hostile_local_cap_examples": "PASS",
        "root_census": "PASS",
        "attachment_permutation_orientation": "PASS",
    }


def compute() -> tuple[dict[str, Any], dict[str, Any]]:
    memory_guard("start")
    tests = self_tests()
    frozen_inputs = parse_input_freeze()
    class_sets: dict[int, tuple[int, ...]] = {}
    class_lookup: dict[int, list[int]] = {}
    labelled_counts: dict[str, int] = {}
    for order in (5, 6, 7):
        classes, lookup, labelled_count = enumerate_unrooted_classes(order)
        class_sets[order] = classes
        class_lookup[order] = lookup
        labelled_counts[str(order)] = labelled_count
        require(
            len(classes) == {5: 21, 6: 62, 7: 208}[order],
            f"order-{order} class count changed",
        )
        print(
            f"[classes] order {order}: {labelled_count:,} labelled -> "
            f"{len(classes)} canonical",
            flush=True,
        )
        memory_guard(f"after-classes-{order}")
    require(class_sets[5] == ROOT_MASKS, "canonical root mask stream changed")
    require(
        {mask: len(attachment_universe(mask)) for mask in ROOT_MASKS}
        == EXPECTED_SIZES,
        "attachment family census changed",
    )

    witnesses = load_witnesses(set(class_sets[7]))
    tables = lower_deck_tables(class_sets, class_lookup)
    for witness in witnesses:
        witness["counts"] = derive_counts(witness["counts7"], class_sets, tables)
    common_counts = witnesses[0]["counts"]
    require(
        all(
            witness["counts"][order] == common_counts[order]
            for witness in witnesses
            for order in (5, 6)
        ),
        "frozen witnesses have different lower decks",
    )

    tensors, labelled_stats = build_all_labelled_tensors(class_sets)
    memory_guard("after-all-labelled-tensors")
    relabelling = verify_relabelling_congruence(tensors, class_sets)
    print(
        f"[relabel] {relabelling['mapping_checks']} S5 family mappings pass",
        flush=True,
    )
    memory_guard("after-relabel-proof")

    coefficients, families, coefficient_stats = reconstruct_coefficient_document(
        tensors,
        class_sets,
        common_counts,
        frozen_inputs,
        labelled_stats,
        relabelling,
    )
    controls = verify_controls(families, class_lookup)
    targets, target_summary = evaluate_witnesses(
        witnesses, families, class_sets, tables
    )
    require(
        parse_input_freeze() == frozen_inputs,
        "frozen inputs changed during construction",
    )
    memory_guard("finish")
    results = {
        "claim_label": "CANDIDATE",
        "coefficient_model": {
            "family_count": len(families),
            "file": COEFFICIENT_OUTPUT.relative_to(ROOT).as_posix(),
            "family_stats": coefficient_stats,
            "payload_sha256": coefficients["payload_sha256_without_this_field"],
        },
        "conclusion": {
            "endpoint_n3_4158": "UNKNOWN",
            "full_psd_constrained_count_system_tested": False,
            "graph_constructed": False,
            "strict_upper_bound_below_4158": "NOT_PROVED",
        },
        "controls": controls,
        "format": "wave49-five-root-one-free-moment-results-v1",
        "limitations": [
            "Discovery cannot certify its own coefficient construction.",
            "A negative matrix direction refutes only its recorded aggregate witness.",
            "Exact matrix PSD on recorded witnesses does not prove global feasibility.",
            "The combined real SDP is a separate floating numerical scout.",
            "No target-graph automorphism is assumed.",
        ],
        "parameters": {
            "k": K,
            "lambda": LAMBDA,
            "mu": MU,
            "n": N,
            "n3": 4158,
        },
        "resource_guard": {
            "minimum_free_memory_percent": MIN_FREE_MEMORY_PERCENT,
            "minimum_observed_free_percent": min(
                sample["free_percent"] for sample in MEMORY_SAMPLES
            ),
            "samples": MEMORY_SAMPLES,
        },
        "role": "construction",
        "root_relabelling": relabelling,
        "scope": (
            "Exact candidate finite Gram matrices for all 21 canonical "
            "five-vertex root types with one-free-vertex attachment flags, "
            "evaluated on the 17 immutable endpoint count witnesses."
        ),
        "self_tests": tests,
        "target_summary": target_summary,
        "targets": targets,
    }
    return coefficients, results


def validate_outputs(
    coefficients: dict[str, Any], results: dict[str, Any]
) -> None:
    require(coefficients["class_streams"]["5"]["count"] == 21, "class5")
    require(coefficients["class_streams"]["6"]["count"] == 62, "class6")
    require(coefficients["class_streams"]["7"]["count"] == 208, "class7")
    require(len(coefficients["families"]) == 21, "family count")
    require(
        [family["matrix_size"] for family in coefficients["families"].values()]
        == [size for _, size in ROOT_MASKS_AND_SIZES],
        "family sizes",
    )
    require(results["target_summary"]["matrix_total"] == 17 * 21, "matrices")
    require(results["conclusion"]["endpoint_n3_4158"] == "UNKNOWN", "scope")


def replay_comparison_result(results: dict[str, Any]) -> dict[str, Any]:
    """Drop only host-state observations before deterministic replay comparison."""
    normalized = json.loads(json.dumps(results))
    normalized["resource_guard"]["minimum_observed_free_percent"] = None
    normalized["resource_guard"]["samples"] = []
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    coefficients, results = compute()
    validate_outputs(coefficients, results)
    coefficient_payload = canonical_bytes(coefficients)
    result_payload = canonical_bytes(results)
    if args.verify:
        require(
            COEFFICIENT_OUTPUT.read_bytes() == coefficient_payload,
            "stored coefficients differ from replay",
        )
        require(
            replay_comparison_result(json.loads(RESULT_OUTPUT.read_text()))
            == replay_comparison_result(results),
            "stored results differ from replay",
        )
        print(
            "PASS_EXACT_REPLAY "
            f"coefficients_sha256={hashlib.sha256(coefficient_payload).hexdigest()} "
            f"results_sha256={hashlib.sha256(result_payload).hexdigest()}"
        )
        return 0
    COEFFICIENT_OUTPUT.write_bytes(coefficient_payload)
    RESULT_OUTPUT.write_bytes(result_payload)
    print(
        f"coefficients_sha256={hashlib.sha256(coefficient_payload).hexdigest()}"
    )
    print(f"results_sha256={hashlib.sha256(result_payload).hexdigest()}")
    print(
        json.dumps(
            {
                "families": len(coefficients["families"]),
                "labelled_root_masks": coefficients[
                    "labelled_tensor_reconstruction"
                ]["labelled_root_mask_count"],
                "indefinite_matrices": results["target_summary"][
                    "exactly_indefinite_matrices"
                ],
                "psd_matrices": results["target_summary"][
                    "exactly_psd_matrices"
                ],
                "targets_refuted": results["target_summary"][
                    "targets_refuted_by_at_least_one_family"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
