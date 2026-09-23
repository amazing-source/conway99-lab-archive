#!/usr/bin/env python3
"""Independent replay of the sealed Wave 47 three-root moment package.

This verifier is self-contained.  It reads the sealed JSON data artifacts but
does not import or execute any discovery implementation.  In particular, it
independently:

* enumerates all locally admissible unlabelled graphs of orders 5, 6, and 7;
* constructs every pointwise-labelled three-root, two-free-vertex flag;
* counts every ordered pair of flags by its exact induced union;
* compares direct and expanded Gram matrices on Petersen and Clebsch controls;
* reconstructs the order-5 and order-6 decks of all 17 immutable witnesses;
* evaluates all 2,664 supplied integer negative directions; and
* rebuilds and compares all 2,657 primitive, deduplicated cuts.

No endpoint, upper-bound, graph-existence, or Conway-99 conclusion is within
the scope of this finite replay.
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
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATTEMPT = ROOT / "attempts" / "wave47-three-root-moment"

N = 99
K = 14
LAMBDA = 1
MU = 2
MIN_FREE_MEMORY_PERCENT = 20.0
FAMILIES = tuple(f"root_{pattern:03b}" for pattern in range(8))
UNION_ORDERS = (5, 6, 7)
EXPECTED_HANDOFF_SHA256 = (
    "8b74110bc6ae983e288d448cd1a963f81521f178e8280bbbf5864274a1639a47"
)
EXPECTED_MANIFEST_SHA256 = (
    "3fee6bf5ec42c5b70138f508ba3fbff6b44b56870601ea25111cd7da93473737"
)
EXPECTED_FULL_ARTIFACTS = {
    "coefficients.json": (
        4_868_254,
        "07b55f06ff8f7d5f2de53d92a3222366e122a7306028752ecd31c10962a824b3",
    ),
    "results.json": (
        3_159_944,
        "a58d04b56ed66094536ffc158b32085e3e940e5c3e42a3983a471e95e99daf37",
    ),
    "cuts.json": (
        42_757_624,
        "d2ea38ed74a1b9098c9cc8eae52f8d65723c2631335b0acedba647dc16aa313e",
    ),
}


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
        success = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
        require(bool(success), "GlobalMemoryStatusEx failed")
        return int(status.ullTotalPhys), int(status.ullAvailPhys)
    page_size = os.sysconf("SC_PAGE_SIZE")
    total = page_size * os.sysconf("SC_PHYS_PAGES")
    available = page_size * os.sysconf("SC_AVPHYS_PAGES")
    return int(total), int(available)


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
        f"[memory] {label}: {sample['free_percent']:.2f}% free "
        f"({available:,}/{total:,} bytes)",
        flush=True,
    )
    require(
        percent >= MIN_FREE_MEMORY_PERCENT,
        f"physical-memory floor violated at {label}: {percent:.2f}% free",
    )
    return sample


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


@functools.lru_cache(maxsize=None)
def permutation_edge_maps(order: int) -> tuple[tuple[int, ...], ...]:
    maps: list[tuple[int, ...]] = []
    for permutation in itertools.permutations(range(order)):
        maps.append(
            tuple(
                edge_index(permutation[left], permutation[right], order)
                for left, right in edge_pairs(order)
            )
        )
    return tuple(maps)


def edge_map_from_vertex_map(
    order: int, vertex_map: Sequence[int]
) -> tuple[int, ...]:
    require(sorted(vertex_map) == list(range(order)), "vertex map is not a permutation")
    return tuple(
        edge_index(vertex_map[left], vertex_map[right], order)
        for left, right in edge_pairs(order)
    )


def transform_mask(mask: int, edge_map: Sequence[int]) -> int:
    transformed = 0
    remaining = mask
    while remaining:
        low_bit = remaining & -remaining
        source_index = low_bit.bit_length() - 1
        transformed |= 1 << edge_map[source_index]
        remaining ^= low_bit
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
    labelled_count = len(labelled)
    remaining = set(labelled)
    lookup = [-1] * (1 << len(edge_pairs(order)))
    classes: list[int] = []
    maps = permutation_edge_maps(order)
    while remaining:
        seed = next(iter(remaining))
        orbit = {transform_mask(seed, edge_map) for edge_map in maps}
        require(orbit.issubset(labelled), "admissibility changed under relabelling")
        canonical = min(orbit)
        require(canonical in remaining, "partial unrooted orbit encountered")
        classes.append(canonical)
        for member in orbit:
            lookup[member] = canonical
        remaining.difference_update(orbit)
    classes.sort()
    for canonical in classes:
        require(lookup[canonical] == canonical, "class representative is not canonical")
    require(
        sum(1 for value in lookup if value >= 0) == labelled_count,
        "canonical lookup does not cover exactly the admissible labelled masks",
    )
    return tuple(classes), lookup, labelled_count


def root_pattern(mask: int, order: int, roots: Sequence[int]) -> int:
    require(len(roots) == 3 and len(set(roots)) == 3, "roots must be distinct")
    return (
        int(adjacent(mask, roots[0], roots[1], order))
        | (int(adjacent(mask, roots[0], roots[2], order)) << 1)
        | (int(adjacent(mask, roots[1], roots[2], order)) << 2)
    )


FREE_SWAP_EDGE_MAP = edge_map_from_vertex_map(5, (0, 1, 2, 4, 3))


@functools.lru_cache(maxsize=None)
def canonical_flag(mask: int) -> int:
    return min(mask, transform_mask(mask, FREE_SWAP_EDGE_MAP))


def flag_universe(pattern: int) -> tuple[int, ...]:
    flags = {
        canonical_flag(mask)
        for mask in range(1 << len(edge_pairs(5)))
        if locally_admissible(mask, 5)
        and root_pattern(mask, 5, (0, 1, 2)) == pattern
    }
    return tuple(sorted(flags))


def flag_from_selection(
    mask: int,
    order: int,
    roots: Sequence[int],
    selection: Sequence[int],
) -> int:
    require(len(selection) == 2, "flag requires an unordered pair of free vertices")
    rooted = induced_mask(mask, order, tuple(roots) + tuple(sorted(selection)))
    return canonical_flag(rooted)


def root_embeddings(
    mask: int, order: int, pattern: int
) -> Iterable[tuple[int, int, int]]:
    for roots in itertools.permutations(range(order), 3):
        if root_pattern(mask, order, roots) == pattern:
            yield roots


def zero_matrix(size: int) -> list[list[int]]:
    return [[0] * size for _ in range(size)]


def class_coefficient_matrix(
    mask: int,
    order: int,
    pattern: int,
    flags: Sequence[int],
) -> tuple[list[list[int]], int]:
    flag_index = {flag: index for index, flag in enumerate(flags)}
    matrix = zero_matrix(len(flags))
    embedding_count = 0
    for roots in root_embeddings(mask, order, pattern):
        embedding_count += 1
        nonroots = tuple(vertex for vertex in range(order) if vertex not in roots)
        all_nonroots = frozenset(nonroots)
        selections = tuple(itertools.combinations(nonroots, 2))
        for first_selection in selections:
            first = flag_from_selection(mask, order, roots, first_selection)
            require(first in flag_index, "first flag left admissible universe")
            first_index = flag_index[first]
            for second_selection in selections:
                if frozenset(first_selection).union(second_selection) != all_nonroots:
                    continue
                second = flag_from_selection(mask, order, roots, second_selection)
                require(second in flag_index, "second flag left admissible universe")
                matrix[first_index][flag_index[second]] += 1
    require(
        all(
            matrix[row][column] == matrix[column][row]
            for row in range(len(flags))
            for column in range(len(flags))
        ),
        "ordered-pair coefficient matrix is not symmetric",
    )
    union_pair_count = {5: 1, 6: 6, 7: 6}[order]
    require(
        sum(map(sum, matrix)) == embedding_count * union_pair_count,
        "all-ones class coefficient lost roots or ordered free-pair overlaps",
    )
    return matrix, embedding_count


def upper_entries(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [row, column, matrix[row][column]]
        for row in range(len(matrix))
        for column in range(row, len(matrix))
        if matrix[row][column]
    ]


def expand_upper(
    size: int, entries: Sequence[Sequence[int]], multiplier: int = 1
) -> list[list[int]]:
    matrix = zero_matrix(size)
    for row, column, value in entries:
        matrix[row][column] += multiplier * value
        if row != column:
            matrix[column][row] += multiplier * value
    return matrix


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


def matrix_sum(matrix: Sequence[Sequence[int]]) -> int:
    return sum(map(sum, matrix))


def quadratic(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> int:
    require(len(matrix) == len(vector), "quadratic dimension mismatch")
    return sum(
        vector[row] * matrix[row][column] * vector[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def quadratic_upper(
    entries: Sequence[Sequence[int]], vector: Sequence[int], double: bool = True
) -> int:
    total = 0
    for row, column, value in entries:
        factor = 2 if double and row != column else 1
        total += factor * value * vector[row] * vector[column]
    return total


def root_embeddings_at_n99(pattern: int) -> int:
    edge_count = pattern.bit_count()
    if edge_count == 0:
        return N * (N - 1 - K) * (N - 2 - (2 * K - MU))
    if edge_count == 1:
        return N * K * (
            N - 2 - (2 * (K - 1) - LAMBDA)
        )
    if edge_count == 2:
        return N * K * (K - 1 - LAMBDA)
    require(edge_count == 3, "unknown root pattern")
    return N * K * LAMBDA


def family_metadata(pattern: int, flags: Sequence[int]) -> dict[str, Any]:
    roots = root_embeddings_at_n99(pattern)
    free_pairs = math.comb(N - 3, 2)
    return {
        "class_coefficients": [],
        "flags": list(flags),
        "free_subsets_per_root_at_n99": free_pairs,
        "matrix_size": len(flags),
        "normalization_denominator_at_n99": roots * free_pairs**2,
        "root_embeddings_at_n99": roots,
        "root_pattern": pattern,
        "root_pattern_binary": f"{pattern:03b}",
    }


def reconstruct_coefficients(
    class_sets: dict[int, tuple[int, ...]],
    frozen_inputs: dict[str, str],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    flag_sets = {pattern: flag_universe(pattern) for pattern in range(8)}
    expected_dimensions = (64, 56, 56, 42, 56, 42, 42, 20)
    require(
        tuple(len(flag_sets[p]) for p in range(8)) == expected_dimensions,
        "three-root flag census changed",
    )
    families: dict[str, dict[str, Any]] = {}
    coefficient_stats: dict[str, Any] = {}
    for pattern in range(8):
        name = FAMILIES[pattern]
        flags = flag_sets[pattern]
        record = family_metadata(pattern, flags)
        class_records: list[dict[str, Any]] = []
        embedding_partition: dict[str, int] = {}
        for order in UNION_ORDERS:
            total_embeddings = 0
            for mask in class_sets[order]:
                matrix, embeddings = class_coefficient_matrix(
                    mask, order, pattern, flags
                )
                total_embeddings += embeddings
                class_records.append(
                    {
                        "canonical_mask": mask,
                        "order": order,
                        "upper_entries": upper_entries(matrix),
                    }
                )
            embedding_partition[str(order)] = total_embeddings
        record["class_coefficients"] = class_records
        families[name] = record
        coefficient_stats[name] = {
            "flag_count": len(flags),
            "flags_sha256": sha256_compact(list(flags)),
            "class_record_count": len(class_records),
            "nonzero_upper_entries": sum(
                len(item["upper_entries"]) for item in class_records
            ),
            "class_coefficients_sha256": sha256_compact(class_records),
            "family_sha256": sha256_compact(record),
            "root_embedding_partition_over_unlabelled_classes": embedding_partition,
        }
        print(
            f"[coefficients] {name}: {len(flags)} flags, "
            f"{coefficient_stats[name]['nonzero_upper_entries']:,} "
            "nonzero upper entries",
            flush=True,
        )
        memory_guard(f"after-coefficients-{name}")
    class_streams = {
        str(order): {
            "count": len(class_sets[order]),
            "sha256": sha256_compact(list(class_sets[order])),
        }
        for order in UNION_ORDERS
    }
    document: dict[str, Any] = {
        "class_streams": class_streams,
        "convention": {
            "automorphism_division": "none",
            "free_vertices": "unordered pair",
            "pair_of_flags": "ordered",
            "root_labels": [0, 1, 2],
            "root_labels_fixed_pointwise": True,
            "root_pattern_bits": ["01", "02", "12"],
            "union_orders": [5, 6, 7],
        },
        "families": families,
        "format": "wave47-three-root-five-vertex-flag-coefficients-v1",
        "input_freeze": frozen_inputs,
    }
    document["payload_sha256_without_this_field"] = sha256_compact(document)
    return document, families, coefficient_stats


def sparse_upper_map(record: dict[str, Any]) -> dict[tuple[int, int], int]:
    return {
        (row, column): value
        for row, column, value in record["upper_entries"]
    }


def verify_root_relabellings(
    families: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    checks = 0
    nonidentity_checks = 0
    for permutation in itertools.permutations(range(3)):
        vertex_map = tuple(permutation) + (3, 4)
        edge_map = edge_map_from_vertex_map(5, vertex_map)
        for source_pattern in range(8):
            source_name = FAMILIES[source_pattern]
            source = families[source_name]
            transformed_root_mask = transform_mask(source["flags"][0], edge_map)
            target_pattern = root_pattern(
                transformed_root_mask, 5, (0, 1, 2)
            )
            target_name = FAMILIES[target_pattern]
            target = families[target_name]
            target_index = {
                flag: index for index, flag in enumerate(target["flags"])
            }
            index_map = []
            for flag in source["flags"]:
                transformed = canonical_flag(transform_mask(flag, edge_map))
                require(
                    transformed in target_index,
                    "root relabelling left target flag universe",
                )
                index_map.append(target_index[transformed])
            require(
                len(set(index_map)) == len(index_map) == len(target["flags"]),
                "root relabelling is not a flag bijection",
            )
            for source_record, target_record in zip(
                source["class_coefficients"], target["class_coefficients"]
            ):
                require(
                    (
                        source_record["order"],
                        source_record["canonical_mask"],
                    )
                    == (
                        target_record["order"],
                        target_record["canonical_mask"],
                    ),
                    "family class streams are misaligned",
                )
                mapped: dict[tuple[int, int], int] = {}
                for row, column, value in source_record["upper_entries"]:
                    new_row, new_column = index_map[row], index_map[column]
                    key = (
                        min(new_row, new_column),
                        max(new_row, new_column),
                    )
                    require(key not in mapped, "root relabelling merged entries")
                    mapped[key] = value
                require(
                    mapped == sparse_upper_map(target_record),
                    "root-order permutation changed coefficient tensor",
                )
            checks += 1
            if permutation != (0, 1, 2):
                nonidentity_checks += 1
    return {
        "all_s3_permutations_all_families": "PASS",
        "mapping_checks": checks,
        "nonidentity_mapping_checks": nonidentity_checks,
        "interpretation": (
            "root labels are pointwise fixed within a family; S3 is used only "
            "as an external cross-family consistency attack"
        ),
    }


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
    require(len(degrees) == 1, "control is not regular")
    lambdas: set[int] = set()
    mus: set[int] = set()
    for left in range(order):
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            (lambdas if adjacent(mask, left, right, order) else mus).add(common)
    require(len(lambdas) == len(mus) == 1, "control is not strongly regular")
    return order, next(iter(degrees)), next(iter(lambdas)), next(iter(mus))


def induced_class_counts(
    mask: int,
    graph_order: int,
    class_lookup: dict[int, list[int]],
) -> dict[int, Counter[int]]:
    counts: dict[int, Counter[int]] = {}
    for order in UNION_ORDERS:
        counter: Counter[int] = Counter()
        for vertices in itertools.combinations(range(graph_order), order):
            submask = induced_mask(mask, graph_order, vertices)
            canonical = class_lookup[order][submask]
            require(canonical >= 0, "control induced an inadmissible class")
            counter[canonical] += 1
        counts[order] = counter
    return counts


def direct_outer_product(
    mask: int,
    graph_order: int,
    pattern: int,
    flags: Sequence[int],
) -> tuple[list[list[int]], int]:
    flag_index = {flag: index for index, flag in enumerate(flags)}
    matrix = zero_matrix(len(flags))
    embeddings = 0
    for roots in root_embeddings(mask, graph_order, pattern):
        embeddings += 1
        nonroots = tuple(vertex for vertex in range(graph_order) if vertex not in roots)
        vector = [0] * len(flags)
        for selection in itertools.combinations(nonroots, 2):
            flag = flag_from_selection(mask, graph_order, roots, selection)
            require(flag in flag_index, "control flag left universe")
            vector[flag_index[flag]] += 1
        for row, left in enumerate(vector):
            if not left:
                continue
            for column, right in enumerate(vector):
                if right:
                    matrix[row][column] += left * right
    return matrix, embeddings


def expanded_matrix(
    family: dict[str, Any],
    class_counts: dict[int, Counter[int]],
) -> list[list[int]]:
    matrix = zero_matrix(family["matrix_size"])
    for record in family["class_coefficients"]:
        multiplier = class_counts[record["order"]][record["canonical_mask"]]
        if multiplier:
            add_scaled_upper(matrix, record["upper_entries"], multiplier)
    return matrix


def verify_controls(
    families: dict[str, dict[str, Any]],
    class_lookup: dict[int, list[int]],
    handoff: dict[str, Any],
    sealed_results: dict[str, Any],
) -> list[dict[str, Any]]:
    handoff_controls = {item["name"]: item for item in handoff["controls"]}
    result_controls = {item["name"]: item for item in sealed_results["controls"]}
    output: list[dict[str, Any]] = []
    for name, graph_data, expected_parameters in (
        ("Petersen", petersen_graph(), (10, 3, 0, 1)),
        ("Clebsch", clebsch_graph(), (16, 5, 0, 2)),
    ):
        mask, graph_order = graph_data
        require(
            srg_parameters(mask, graph_order) == expected_parameters,
            f"{name} control parameters changed",
        )
        counts = induced_class_counts(mask, graph_order, class_lookup)
        induced_totals = {
            str(order): sum(counts[order].values()) for order in UNION_ORDERS
        }
        require(
            induced_totals
            == {str(order): math.comb(graph_order, order) for order in UNION_ORDERS},
            f"{name} induced-subset totals failed",
        )
        family_output: dict[str, Any] = {}
        embedding_partition = 0
        for pattern, family_name in enumerate(FAMILIES):
            family = families[family_name]
            direct, embeddings = direct_outer_product(
                mask, graph_order, pattern, family["flags"]
            )
            expanded = expanded_matrix(family, counts)
            require(direct == expanded, f"{name} {family_name} expansion mismatch")
            expected_ones = embeddings * math.comb(graph_order - 3, 2) ** 2
            require(
                matrix_sum(direct) == expected_ones,
                f"{name} {family_name} all-ones normalization failed",
            )
            matrix_hash = sha256_compact(direct)
            require(
                matrix_hash
                == handoff_controls[name]["family_matrix_sha256"][family_name],
                f"{name} {family_name} handoff matrix hash mismatch",
            )
            sealed_family = result_controls[name]["families"][family_name]
            require(
                matrix_hash == sealed_family["matrix_sha256"]
                and embeddings == sealed_family["root_embeddings"]
                and expected_ones == sealed_family["all_ones_quadratic"],
                f"{name} {family_name} results control metadata mismatch",
            )
            embedding_partition += embeddings
            family_output[family_name] = {
                "matrix_sha256": matrix_hash,
                "root_embeddings": embeddings,
                "all_ones_quadratic": expected_ones,
                "direct_equals_expansion": True,
                "psd_certificate": "explicit sum of integer outer products",
            }
        require(
            embedding_partition == graph_order * (graph_order - 1) * (graph_order - 2),
            f"{name} ordered-root partition failed",
        )
        require(
            induced_totals == handoff_controls[name]["induced_subset_totals"],
            f"{name} handoff induced totals mismatch",
        )
        output.append(
            {
                "name": name,
                "order": graph_order,
                "srg_parameters": list(expected_parameters),
                "induced_subset_totals": induced_totals,
                "ordered_root_partition": embedding_partition,
                "families": family_output,
            }
        )
        print(f"[control] {name}: all eight exact direct expansions match", flush=True)
        memory_guard(f"after-control-{name}")
    return output


def parse_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    pattern = re.compile(r"^([0-9a-f]{64})  (.+)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.fullmatch(line)
        require(match is not None, f"malformed manifest line: {line!r}")
        digest, relative = match.groups()
        require(relative not in entries, f"duplicate manifest path: {relative}")
        entries[relative] = digest
    return entries


def verify_sealed_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    handoff_path = ATTEMPT / "compact-handoff.json"
    manifest_path = ATTEMPT / "package-manifest.sha256"
    require(
        sha256_file(handoff_path) == EXPECTED_HANDOFF_SHA256,
        "compact handoff SHA-256 mismatch",
    )
    require(
        sha256_file(manifest_path) == EXPECTED_MANIFEST_SHA256,
        "package manifest SHA-256 mismatch",
    )
    manifest_entries = parse_manifest(manifest_path)
    for relative, expected in manifest_entries.items():
        path = ROOT / Path(relative)
        require(path.is_file(), f"manifest path missing: {relative}")
        require(
            sha256_file(path) == expected,
            f"manifest member hash mismatch: {relative}",
        )
    handoff = read_json(handoff_path)
    handoff_payload = {
        key: value
        for key, value in handoff.items()
        if key != "payload_sha256_without_this_field"
    }
    require(
        sha256_compact(handoff_payload)
        == handoff["payload_sha256_without_this_field"],
        "compact handoff canonical payload hash mismatch",
    )
    require(
        handoff["payload_sha256_without_this_field"]
        == "e6d1991c20c8c30c4e393a081cf3fa3c4264b6ee5dacae279d5b6ab726766867",
        "unexpected compact handoff payload hash",
    )
    for relative, expected in handoff["input_freeze"].items():
        path = ROOT / Path(relative)
        require(path.is_file(), f"frozen input missing: {relative}")
        require(
            sha256_file(path) == expected,
            f"frozen input changed: {relative}",
        )
    full_documents: dict[str, Any] = {}
    for filename, (expected_bytes, expected_hash) in EXPECTED_FULL_ARTIFACTS.items():
        path = ATTEMPT / filename
        require(path.stat().st_size == expected_bytes, f"{filename} byte size changed")
        require(sha256_file(path) == expected_hash, f"{filename} hash changed")
        handoff_record = handoff["full_reconstruction"][filename.removesuffix(".json")]
        require(
            handoff_record["bytes"] == expected_bytes
            and handoff_record["sha256"] == expected_hash,
            f"{filename} handoff reconstruction metadata changed",
        )
        full_documents[filename] = read_json(path)
    coefficients = full_documents["coefficients.json"]
    coefficient_payload = {
        key: value
        for key, value in coefficients.items()
        if key != "payload_sha256_without_this_field"
    }
    require(
        sha256_compact(coefficient_payload)
        == coefficients["payload_sha256_without_this_field"]
        == handoff["coefficient_payload_sha256"],
        "coefficient canonical payload hash mismatch",
    )
    require(
        full_documents["results.json"]["conclusion"]
        == handoff["conclusion"],
        "results and handoff scope walls differ",
    )
    require(
        full_documents["cuts.json"]["scope_wall"]["endpoint_n3_4158"]
        == "UNKNOWN",
        "sealed cuts improperly promote endpoint status",
    )
    return (
        handoff,
        coefficients,
        full_documents["results.json"],
        full_documents["cuts.json"],
    )


def support_counter(
    support: Sequence[dict[str, Any]],
    expected_hash: str,
    class_set: set[int],
    label: str,
) -> Counter[int]:
    require(sha256_compact(support) == expected_hash, f"{label} support hash mismatch")
    masks = [item["canonical_mask"] for item in support]
    require(masks == sorted(masks), f"{label} support is not sorted")
    require(len(masks) == len(set(masks)), f"{label} support repeats a class")
    counter: Counter[int] = Counter()
    for item in support:
        mask, count = item["canonical_mask"], item["count"]
        require(mask in class_set, f"{label} uses a noncanonical seven-class")
        require(type(count) is int and count > 0, f"{label} has nonpositive count")
        counter[mask] = count
    require(
        sum(counter.values()) == math.comb(N, 7),
        f"{label} seven-subset total changed",
    )
    return counter


def load_witnesses(
    handoff: dict[str, Any],
    sealed_results: dict[str, Any],
    classes7: set[int],
) -> list[dict[str, Any]]:
    wave43_path = ROOT / "attempts/wave43-seven-deck-endpoint/exact-results.json"
    wave44_path = ROOT / "attempts/wave44-rooted-flags/rooted-witness.json"
    checkpoint_path = (
        ROOT
        / "attempts/wave45-flag-moment/checkpoint-v1-seed0-17cuts-15witnesses.json"
    )
    wave43 = read_json(wave43_path)
    wave44 = read_json(wave44_path)
    checkpoint = read_json(checkpoint_path)
    source_records = [
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
        source_records.append(
            (
                f"wave45_iteration_{item['iteration']}",
                item["support"],
                item["support_sha256"],
                checkpoint_path,
            )
        )
    require(len(source_records) == 17, "immutable witness census changed")
    sealed_targets = {target["name"]: target for target in sealed_results["targets"]}
    handoff_targets = {target["name"]: target for target in handoff["targets"]}
    witnesses: list[dict[str, Any]] = []
    for name, support, support_hash, input_path in source_records:
        require(name in sealed_targets and name in handoff_targets, f"missing target {name}")
        target = sealed_targets[name]
        require(
            target["support_sha256"] == support_hash
            == handoff_targets[name]["support_sha256"],
            f"{name} support hash routing mismatch",
        )
        relative = input_path.relative_to(ROOT).as_posix()
        require(
            target["input_path"] == relative
            and target["input_sha256"] == sha256_file(input_path),
            f"{name} source routing mismatch",
        )
        counts7 = support_counter(support, support_hash, classes7, name)
        witnesses.append(
            {
                "name": name,
                "support": support,
                "support_sha256": support_hash,
                "counts7": counts7,
                "sealed_target": target,
                "handoff_target": handoff_targets[name],
            }
        )
    return witnesses


def lower_deck_tables(
    class_sets: dict[int, tuple[int, ...]],
    class_lookup: dict[int, list[int]],
) -> dict[int, dict[int, Counter[int]]]:
    tables: dict[int, dict[int, Counter[int]]] = {5: {}, 6: {}}
    for seven_mask in class_sets[7]:
        for order in (5, 6):
            counter: Counter[int] = Counter()
            for vertices in itertools.combinations(range(7), order):
                submask = induced_mask(seven_mask, 7, vertices)
                canonical = class_lookup[order][submask]
                require(canonical >= 0, "admissible seven-class had bad lower deck")
                counter[canonical] += 1
            require(
                sum(counter.values()) == math.comb(7, order),
                "lower-deck table total failed",
            )
            tables[order][seven_mask] = counter
    return tables


def derive_counts(
    counts7: Counter[int],
    class_sets: dict[int, tuple[int, ...]],
    tables: dict[int, dict[int, Counter[int]]],
) -> dict[int, Counter[int]]:
    result: dict[int, Counter[int]] = {7: Counter(counts7)}
    for order in (5, 6):
        numerator: Counter[int] = Counter()
        for seven_mask, count in counts7.items():
            for lower_mask, multiplicity in tables[order][seven_mask].items():
                numerator[lower_mask] += count * multiplicity
        divisor = math.comb(N - order, 7 - order)
        counts: Counter[int] = Counter()
        for mask in class_sets[order]:
            value = numerator[mask]
            require(value % divisor == 0, "lower deck is nonintegral")
            quotient = value // divisor
            require(quotient >= 0, "lower deck is negative")
            if quotient:
                counts[mask] = quotient
        require(
            sum(counts.values()) == math.comb(N, order),
            f"order-{order} deck total changed",
        )
        result[order] = counts
    return result


def sparse_count_hash(counts: Counter[int]) -> str:
    return sha256_compact(
        [
            {"canonical_mask": mask, "count": counts[mask]}
            for mask in sorted(counts)
            if counts[mask]
        ]
    )


def matrix_from_counts(
    family: dict[str, Any], counts: dict[int, Counter[int]]
) -> list[list[int]]:
    return expanded_matrix(family, counts)


def family_cut_coefficients(
    family: dict[str, Any], vector: Sequence[int]
) -> dict[int, dict[int, int]]:
    by_order: dict[int, dict[int, int]] = {5: {}, 6: {}, 7: {}}
    for record in family["class_coefficients"]:
        value = quadratic_upper(record["upper_entries"], vector, double=True)
        if value:
            by_order[record["order"]][record["canonical_mask"]] = value
    return by_order


def primitive_cut(
    family_name: str,
    family: dict[str, Any],
    vector: Sequence[int],
    counts: dict[int, Counter[int]],
    source: str,
    source_direction_index: int,
    support_hash: str,
) -> tuple[dict[str, Any], int, int, bool]:
    coefficients = family_cut_coefficients(family, vector)
    constant_raw = sum(
        value * counts[order][mask]
        for order in (5, 6)
        for mask, value in coefficients[order].items()
    )
    seven_raw = coefficients[7]
    divisor = 0
    for value in itertools.chain((constant_raw,), seven_raw.values()):
        divisor = math.gcd(divisor, abs(value))
    require(divisor > 0, "zero cut cannot be primitive")
    constant = constant_raw // divisor
    sparse7 = [
        {"canonical_mask": mask, "coefficient": value // divisor}
        for mask, value in sorted(seven_raw.items())
    ]
    source_value = constant + sum(
        item["coefficient"] * counts[7][item["canonical_mask"]]
        for item in sparse7
    )
    pattern = int(family_name.removeprefix("root_"), 2)
    payload = {
        "coefficients": sparse7,
        "constant": constant,
        "family": family_name,
        "primitive_divisor": divisor,
        "root_pattern": pattern,
        "vector": list(vector),
    }
    cut_hash = sha256_compact(payload)
    record = {
        "coefficients": sparse7,
        "constant": constant,
        "cut_sha256": cut_hash,
        "family": family_name,
        "primitive_divisor": divisor,
        "root_pattern": pattern,
        "source": source,
        "source_cut_value": source_value,
        "source_direction_index": source_direction_index,
        "source_support_sha256": support_hash,
        "vector": list(vector),
    }
    undoubled_differs = any(
        quadratic_upper(item["upper_entries"], vector, double=False)
        != quadratic_upper(item["upper_entries"], vector, double=True)
        for item in family["class_coefficients"]
    )
    raw_value = (
        constant_raw
        + sum(value * counts[7][mask] for mask, value in seven_raw.items())
    )
    return record, raw_value, divisor, undoubled_differs


def compare_float(actual: float, expected: float, label: str) -> float:
    error = abs(actual - expected)
    tolerance = 1e-6 * max(1.0, abs(expected))
    require(error <= tolerance, f"{label} float diagnostic differs by {error}")
    return error


def replay_witnesses_and_cuts(
    witnesses: list[dict[str, Any]],
    families: dict[str, dict[str, Any]],
    class_sets: dict[int, tuple[int, ...]],
    lower_tables: dict[int, dict[int, Counter[int]]],
    handoff: dict[str, Any],
    sealed_cuts: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    all_generated: list[dict[str, Any]] = []
    unique_generated: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    witness_output: list[dict[str, Any]] = []
    common_lower_hashes: dict[str, str] | None = None
    offdiagonal_attack_count = 0
    maximum_minimum_eigenvalue_error = 0.0
    maximum_normalized_eigenvalue_error = 0.0
    robust_vs_reported_count_differences = 0
    total_directions = 0
    matrix_count = 0
    for witness in witnesses:
        name = witness["name"]
        counts = derive_counts(witness["counts7"], class_sets, lower_tables)
        witness["counts"] = counts
        lower_hashes = {
            str(order): sparse_count_hash(counts[order]) for order in (5, 6)
        }
        if common_lower_hashes is None:
            common_lower_hashes = lower_hashes
        require(
            lower_hashes == common_lower_hashes,
            f"{name} does not have the common frozen lower deck",
        )
        target = witness["sealed_target"]
        family_output: dict[str, Any] = {}
        indefinite_families = 0
        witness_direction_count = 0
        for pattern, family_name in enumerate(FAMILIES):
            family = families[family_name]
            sealed_family = target["family_results"][family_name]
            matrix = matrix_from_counts(family, counts)
            matrix_hash = sha256_compact(matrix)
            require(
                matrix_hash == sealed_family["matrix_sha256"],
                f"{name} {family_name} matrix hash mismatch",
            )
            denominator = family["normalization_denominator_at_n99"]
            require(
                sealed_family["normalization_denominator"] == denominator,
                f"{name} {family_name} normalization metadata mismatch",
            )
            require(
                matrix_sum(matrix) == denominator,
                f"{name} {family_name} all-ones normalization failed",
            )
            eigenvalues = np.linalg.eigvalsh(np.asarray(matrix, dtype=np.float64))
            spectral_scale = max(
                1.0, abs(float(eigenvalues[0])), abs(float(eigenvalues[-1]))
            )
            spectral_backward_tolerance = max(
                1e-5,
                128
                * np.finfo(np.float64).eps
                * len(matrix)
                * spectral_scale,
            )
            robust_negative_count = int(
                np.count_nonzero(eigenvalues < -spectral_backward_tolerance)
            )
            reporting_threshold = 1e-8 * spectral_scale
            reported_negative_count = int(
                np.count_nonzero(eigenvalues < -reporting_threshold)
            )
            require(
                reported_negative_count
                == sealed_family["numerical_negative_eigenvalue_count"],
                (
                    f"{name} {family_name} reported numerical negative count "
                    f"mismatch (actual={reported_negative_count}, "
                    f"expected={sealed_family['numerical_negative_eigenvalue_count']}, "
                    f"threshold={reporting_threshold}, "
                    f"boundary={eigenvalues[max(0, sealed_family['numerical_negative_eigenvalue_count'] - 3):sealed_family['numerical_negative_eigenvalue_count'] + 3].tolist()})"
                ),
            )
            robust_vs_reported_count_differences += int(
                robust_negative_count != reported_negative_count
            )
            minimum_raw = float(eigenvalues[0])
            minimum_normalized = minimum_raw / denominator
            maximum_minimum_eigenvalue_error = max(
                maximum_minimum_eigenvalue_error,
                compare_float(
                    minimum_raw,
                    sealed_family["minimum_raw_eigenvalue_float"],
                    f"{name} {family_name} minimum raw eigenvalue",
                ),
            )
            maximum_normalized_eigenvalue_error = max(
                maximum_normalized_eigenvalue_error,
                compare_float(
                    minimum_normalized,
                    sealed_family["minimum_normalized_eigenvalue_float"],
                    f"{name} {family_name} minimum normalized eigenvalue",
                ),
            )
            directions = sealed_family["exact_negative_directions"]
            require(
                len(directions)
                == sealed_family["exact_negative_direction_count"]
                == reported_negative_count,
                f"{name} {family_name} direction census mismatch",
            )
            require(directions, f"{name} {family_name} has no exact negative direction")
            indefinite_families += 1
            for expected_index, direction in enumerate(directions):
                vector = direction["vector"]
                require(
                    direction["eigenvalue_index"] == expected_index,
                    f"{name} {family_name} direction ordering changed",
                )
                require(
                    len(vector) == family["matrix_size"],
                    f"{name} {family_name} direction dimension mismatch",
                )
                vector_gcd = 0
                for value in vector:
                    vector_gcd = math.gcd(vector_gcd, abs(value))
                require(vector_gcd == 1, f"{name} {family_name} direction not primitive")
                raw_quadratic = quadratic(matrix, vector)
                require(
                    raw_quadratic == direction["quadratic_numerator"] < 0,
                    f"{name} {family_name} negative direction replay failed",
                )
                cut_record, cut_raw, divisor, undoubled_differs = primitive_cut(
                    family_name,
                    family,
                    vector,
                    counts,
                    name,
                    direction["eigenvalue_index"],
                    witness["support_sha256"],
                )
                require(
                    cut_raw == raw_quadratic,
                    f"{name} {family_name} cut linearization mismatch",
                )
                require(
                    cut_record["source_cut_value"] * divisor == raw_quadratic,
                    f"{name} {family_name} primitive cut scaling mismatch",
                )
                require(
                    cut_record["source_cut_value"] < 0,
                    f"{name} {family_name} cut did not reject source",
                )
                offdiagonal_attack_count += int(undoubled_differs)
                all_generated.append(cut_record)
                if cut_record["cut_sha256"] not in seen_hashes:
                    seen_hashes.add(cut_record["cut_sha256"])
                    unique_generated.append(cut_record)
            witness_direction_count += len(directions)
            matrix_count += 1
            family_output[family_name] = {
                "matrix_sha256": matrix_hash,
                "matrix_size": family["matrix_size"],
                "normalization_denominator": denominator,
                "all_ones_quadratic": matrix_sum(matrix),
                "reported_negative_eigenvalue_count": reported_negative_count,
                "reporting_threshold_raw": reporting_threshold,
                "backward_robust_negative_eigenvalue_count": robust_negative_count,
                "spectral_backward_tolerance": spectral_backward_tolerance,
                "exact_negative_directions_replayed": len(directions),
                "all_direction_values_strictly_negative": True,
            }
        require(
            indefinite_families
            == target["exactly_indefinite_family_count"]
            == witness["handoff_target"]["exactly_indefinite_family_count"]
            == 8,
            f"{name} family indefiniteness census mismatch",
        )
        require(
            witness_direction_count
            == witness["handoff_target"]["total_exact_negative_directions"],
            f"{name} direction total differs from handoff",
        )
        total_directions += witness_direction_count
        witness_output.append(
            {
                "name": name,
                "support_sha256": witness["support_sha256"],
                "support_size": len(witness["support"]),
                "seven_subset_total": sum(counts[7].values()),
                "lower_deck_sha256": lower_hashes,
                "exactly_indefinite_family_count": indefinite_families,
                "exact_negative_directions_replayed": witness_direction_count,
                "families": family_output,
            }
        )
        print(
            f"[witness] {name}: eight indefinite families, "
            f"{witness_direction_count} exact negative directions",
            flush=True,
        )
        memory_guard(f"after-witness-{name}")
    require(total_directions == 2664 == len(all_generated), "raw direction total changed")
    require(
        len(unique_generated) == len(seen_hashes) == 2657,
        "primitive cut deduplication total changed",
    )
    require(
        unique_generated == sealed_cuts["cuts"],
        "independent complete cut ledger differs from sealed cuts.json",
    )
    require(
        len({item["cut_sha256"] for item in unique_generated}) == 2657,
        "sealed cut hashes are not unique",
    )
    require(
        offdiagonal_attack_count > 0,
        "off-diagonal-doubling attack never distinguished the wrong convention",
    )
    representative_by_hash = {
        item["cut_sha256"]: item for item in unique_generated
    }
    for representative in handoff["representative_cuts"]:
        cut_hash = representative["cut_sha256"]
        require(cut_hash in representative_by_hash, "representative cut not in ledger")
        require(
            representative == representative_by_hash[cut_hash],
            "representative cut record differs from complete replay",
        )
    require(
        len(handoff["representative_cuts"]) == 17,
        "representative cut census changed",
    )
    duplicate_count = len(all_generated) - len(unique_generated)
    duplicate_sources: list[dict[str, Any]] = []
    first_by_hash: dict[str, dict[str, Any]] = {}
    for item in all_generated:
        cut_hash = item["cut_sha256"]
        if cut_hash in first_by_hash:
            duplicate_sources.append(
                {
                    "cut_sha256": cut_hash,
                    "first": {
                        "source": first_by_hash[cut_hash]["source"],
                        "family": first_by_hash[cut_hash]["family"],
                        "direction_index": first_by_hash[cut_hash][
                            "source_direction_index"
                        ],
                    },
                    "duplicate": {
                        "source": item["source"],
                        "family": item["family"],
                        "direction_index": item["source_direction_index"],
                    },
                }
            )
        else:
            first_by_hash[cut_hash] = item
    require(
        duplicate_count == len(duplicate_sources) == 7,
        "expected exactly seven repeated primitive inequalities",
    )
    cut_summary = {
        "generated_before_deduplication": len(all_generated),
        "unique_primitive_cuts": len(unique_generated),
        "duplicate_primitive_cuts": duplicate_count,
        "complete_ledger_exactly_equal_to_sealed": True,
        "all_2664_raw_quadratics_exactly_replayed": True,
        "all_2657_source_cut_values_strictly_negative": True,
        "representative_cuts_exactly_replayed": 17,
        "offdiagonal_doubling_distinguished_from_wrong_formula_on_direction_class_pairs": (
            offdiagonal_attack_count
        ),
        "duplicate_sources": duplicate_sources,
        "common_lower_deck_sha256": common_lower_hashes,
        "matrix_count": matrix_count,
        "maximum_minimum_raw_eigenvalue_absolute_error": (
            maximum_minimum_eigenvalue_error
        ),
        "maximum_minimum_normalized_eigenvalue_absolute_error": (
            maximum_normalized_eigenvalue_error
        ),
        "matrices_where_backward_robust_and_reported_counts_differ": (
            robust_vs_reported_count_differences
        ),
    }
    return witness_output, cut_summary


def rehash_sealed_inputs(
    handoff: dict[str, Any],
) -> dict[str, Any]:
    require(
        sha256_file(ATTEMPT / "compact-handoff.json") == EXPECTED_HANDOFF_SHA256,
        "compact handoff changed during replay",
    )
    require(
        sha256_file(ATTEMPT / "package-manifest.sha256")
        == EXPECTED_MANIFEST_SHA256,
        "package manifest changed during replay",
    )
    for relative, expected in handoff["input_freeze"].items():
        require(
            sha256_file(ROOT / Path(relative)) == expected,
            f"frozen input changed during replay: {relative}",
        )
    for filename, (_, expected_hash) in EXPECTED_FULL_ARTIFACTS.items():
        require(
            sha256_file(ATTEMPT / filename) == expected_hash,
            f"{filename} changed during replay",
        )
    return {
        "sealed_inputs_unchanged_during_replay": True,
        "compact_handoff_sha256": EXPECTED_HANDOFF_SHA256,
        "package_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "full_reconstruction_sha256": {
            filename: digest
            for filename, (_, digest) in EXPECTED_FULL_ARTIFACTS.items()
        },
    }


def self_tests() -> dict[str, Any]:
    require(edge_pairs(5)[0] == (0, 1), "edge ordering starts incorrectly")
    require(edge_index(0, 2, 5) == 1, "edge 02 index changed")
    require(edge_index(1, 2, 5) == 4, "edge 12 index changed")
    require(root_pattern(1, 5, (0, 1, 2)) == 1, "root bit 01 changed")
    require(root_pattern(2, 5, (0, 1, 2)) == 2, "root bit 02 changed")
    require(root_pattern(16, 5, (0, 1, 2)) == 4, "root bit 12 changed")
    k4 = mask_from_edges(4, itertools.combinations(range(4), 2))
    require(not locally_admissible(k4, 4), "K4 incorrectly locally admissible")
    c5 = mask_from_edges(5, ((0, 1), (1, 2), (2, 3), (3, 4), (4, 0)))
    require(locally_admissible(c5, 5), "C5 incorrectly locally inadmissible")
    swapped = transform_mask(c5, FREE_SWAP_EDGE_MAP)
    require(canonical_flag(c5) == canonical_flag(swapped), "free swap not quotiented")
    return {
        "edge_order_root_bits": "PASS",
        "local_cap_hostile_examples": "PASS",
        "free_vertex_swap_canonicalization": "PASS",
    }


def compute() -> dict[str, Any]:
    memory_guard("start")
    tests = self_tests()
    handoff, sealed_coefficients, sealed_results, sealed_cuts = verify_sealed_inputs()
    print("[seal] compact handoff, manifest, frozen inputs, and full artifacts match", flush=True)
    memory_guard("after-sealed-inputs")

    class_sets: dict[int, tuple[int, ...]] = {}
    class_lookup: dict[int, list[int]] = {}
    labelled_counts: dict[str, int] = {}
    for order in UNION_ORDERS:
        classes, lookup, labelled_count = enumerate_unrooted_classes(order)
        class_sets[order] = classes
        class_lookup[order] = lookup
        labelled_counts[str(order)] = labelled_count
        expected_count = {5: 21, 6: 62, 7: 208}[order]
        require(len(classes) == expected_count, f"order-{order} class count changed")
        require(
            sha256_compact(list(classes))
            == handoff["class_streams"][str(order)]["sha256"],
            f"order-{order} class stream hash mismatch",
        )
        print(
            f"[classes] order {order}: {labelled_count:,} admissible labelled "
            f"masks -> {len(classes)} unlabelled classes",
            flush=True,
        )
        memory_guard(f"after-class-enumeration-{order}")

    independent_coefficients, families, coefficient_stats = reconstruct_coefficients(
        class_sets, handoff["input_freeze"]
    )
    require(
        independent_coefficients == sealed_coefficients,
        "independent coefficient document differs from sealed coefficients.json",
    )
    require(
        independent_coefficients["payload_sha256_without_this_field"]
        == handoff["coefficient_payload_sha256"],
        "independent coefficient payload hash differs from handoff",
    )
    root_counts = {
        family: families[family]["root_embeddings_at_n99"] for family in FAMILIES
    }
    require(
        sum(root_counts.values()) == N * (N - 1) * (N - 2),
        "all eight ordered root patterns do not partition ordered triples",
    )
    require(
        all(
            families[family]["free_subsets_per_root_at_n99"] == math.comb(96, 2)
            for family in FAMILIES
        ),
        "free-pair census at n=99 changed",
    )
    relabelling = verify_root_relabellings(families)
    print("[root-order] all S3 cross-family tensor mappings match", flush=True)
    memory_guard("after-root-relabel-attacks")

    controls = verify_controls(
        families, class_lookup, handoff, sealed_results
    )
    witnesses = load_witnesses(
        handoff, sealed_results, set(class_sets[7])
    )
    lower_tables = lower_deck_tables(class_sets, class_lookup)
    witness_output, cut_summary = replay_witnesses_and_cuts(
        witnesses,
        families,
        class_sets,
        lower_tables,
        handoff,
        sealed_cuts,
    )
    require(
        cut_summary["generated_before_deduplication"]
        == handoff["full_cut_ledger"]["generated_cut_count_before_deduplication"]
        and cut_summary["unique_primitive_cuts"]
        == handoff["full_cut_ledger"]["unique_cut_count"],
        "cut summary differs from compact handoff",
    )
    require(
        handoff["conclusion"]["endpoint_n3_4158"] == "UNKNOWN"
        and handoff["conclusion"]["strict_upper_bound_below_4158"] == "NOT_PROVED"
        and not handoff["conclusion"]["full_psd_constrained_count_system_tested"]
        and not handoff["conclusion"]["graph_constructed"],
        "scope wall was not preserved",
    )
    final_hashes = rehash_sealed_inputs(handoff)
    memory_guard("finish")
    return {
        "format": "wave47-three-root-moment-independent-verification-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED",
        "scope": (
            "Independent exact reconstruction of all eight three-labelled-root "
            "flag families, orders 5-7 coefficient tensors, two direct Gram "
            "controls, 17 immutable witness matrices, 2664 supplied negative "
            "directions, and 2657 deduplicated primitive cuts."
        ),
        "sealed_inputs": final_hashes,
        "self_tests": tests,
        "class_enumeration": {
            "method": (
                "all labelled simple masks filtered by edge/nonedge common-neighbor "
                "caps, then complete S_n orbit removal"
            ),
            "labelled_admissible_counts": labelled_counts,
            "unlabelled_counts": {
                str(order): len(class_sets[order]) for order in UNION_ORDERS
            },
            "class_stream_sha256": {
                str(order): sha256_compact(list(class_sets[order]))
                for order in UNION_ORDERS
            },
        },
        "families": {
            "ordered_root_patterns": list(FAMILIES),
            "root_pattern_bit_order": ["01", "02", "12"],
            "root_embeddings_at_n99": root_counts,
            "ordered_root_partition_at_n99": sum(root_counts.values()),
            "free_pairs_per_root_at_n99": math.comb(96, 2),
            "coefficient_payload_sha256": independent_coefficients[
                "payload_sha256_without_this_field"
            ],
            "coefficient_stats": coefficient_stats,
            "root_relabelling_attacks": relabelling,
            "automorphism_division": "none",
        },
        "controls": controls,
        "witnesses": witness_output,
        "cuts": cut_summary,
        "attacks": {
            "normalization": (
                "all 136 witness all-ones quadratics and all 16 control "
                "all-ones quadratics equal the exact raw denominators"
            ),
            "root_ordering": relabelling,
            "automorphisms": (
                "coefficients count all ordered root embeddings and ordered "
                "free-pair products; no automorphism divisor is present"
            ),
            "offdiagonal_doubling": (
                "every quadratic uses diagonal plus twice each off-diagonal "
                "upper entry; an undoubled hostile formula is explicitly "
                "distinguished"
            ),
            "class_canonical_mappings": (
                "complete labelled admissible spaces map to unique minimum "
                "representatives under every vertex permutation"
            ),
            "hashes": (
                "sealed hashes checked before and after replay; independent "
                "coefficient payload and complete cut ledger match exactly"
            ),
        },
        "conclusion": {
            "finite_wave47_replay": "VERIFIED_SCOPED",
            "all_17_immutable_witnesses_refuted_by_supplied_directions": True,
            "full_psd_constrained_count_system_tested": False,
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "The 2657 inequalities reject only their recorded aggregate sources.",
            "No complete search of the PSD-constrained integer count region was run.",
            "A surviving aggregate moment vector would not construct a graph.",
            "Floating eigenvalues are diagnostic; exact certification comes from integer quadratics.",
            "No novelty, priority, endpoint exclusion, strict upper bound, or Conway-99 claim is made.",
        ],
        "resource_guard": {
            "minimum_free_physical_memory_percent": MIN_FREE_MEMORY_PERCENT,
            "samples": MEMORY_SAMPLES,
            "minimum_observed_free_percent": min(
                item["free_percent"] for item in MEMORY_SAMPLES
            ),
        },
    }


def validate_summary(record: dict[str, Any]) -> None:
    require(record["claim_label"] == "VERIFIED_SCOPED", "wrong scoped verdict")
    require(
        record["class_enumeration"]["unlabelled_counts"]
        == {"5": 21, "6": 62, "7": 208},
        "class census failed",
    )
    require(
        [record["families"]["coefficient_stats"][name]["flag_count"] for name in FAMILIES]
        == [64, 56, 56, 42, 56, 42, 42, 20],
        "flag census failed",
    )
    require(len(record["witnesses"]) == 17, "witness census failed")
    require(
        record["cuts"]["generated_before_deduplication"] == 2664
        and record["cuts"]["unique_primitive_cuts"] == 2657,
        "cut census failed",
    )
    require(
        record["resource_guard"]["minimum_observed_free_percent"]
        >= MIN_FREE_MEMORY_PERCENT,
        "recorded memory floor failed",
    )
    require(
        record["conclusion"]["endpoint_n3_4158"] == "UNKNOWN"
        and record["conclusion"]["Conway_99"] == "UNKNOWN",
        "scope wall failed",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "verification-results.json",
        help="path for the compact independent verification record",
    )
    parser.add_argument(
        "--validate",
        type=Path,
        help="validate an existing verification record without recomputation",
    )
    parser.add_argument(
        "--self-test-only",
        action="store_true",
        help="run only fast implementation self-tests",
    )
    args = parser.parse_args()
    if args.self_test_only:
        print(json.dumps(self_tests(), sort_keys=True))
        return 0
    if args.validate:
        record = read_json(args.validate)
        validate_summary(record)
        print(
            f"validated {args.validate} sha256={sha256_file(args.validate)}",
            flush=True,
        )
        return 0
    record = compute()
    validate_summary(record)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(record))
    print(
        f"[done] wrote {args.output} sha256={sha256_file(args.output)} "
        "claim_label=VERIFIED_SCOPED",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
