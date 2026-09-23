"""Independent standard-library verifier for the Wave 17 F/R certificate.

This module imports neither the SAT scout nor the certificate builder.  It
fetches and validates both official catalogs in memory, independently parses
and checks every graph, reconstructs all 457 residual cases, reproduces the
GF(2) kernel census and mixed-component counts, and compares every certificate
field exactly.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable
import urllib.request


CATALOGS = {
    18: {
        "url": "https://houseofgraphs.org/data/cubics/cub18-gir5.g6.gz",
        "compressed_bytes": 2470,
        "compressed_sha256": (
            "95ff5ca833f3a1361d652e8f585d8aed21af61d73d135abf366570dcbddfcf7e"
        ),
        "decompressed_bytes": 12740,
        "decompressed_sha256": (
            "39fb8633418927da9f5e3bd9fe81c83070a05ff65bfc532719618471a267f7fd"
        ),
        "records": 455,
    },
    12: {
        "url": "https://houseofgraphs.org/data/cubics/cub12-gir5.g6.gz",
        "compressed_bytes": 55,
        "compressed_sha256": (
            "c63e83c1b6c27af375c1f44f4dedfb5aa3f4f2abf01b6e68ba131942f72a6226"
        ),
        "decompressed_bytes": 26,
        "decompressed_sha256": (
            "ddf1582755db62e06d8072b7dfffb48357b56c677c11890eb14d9aeeb1ba55d4"
        ),
        "records": 2,
    },
}


Edge = tuple[int, int]


def edge(left: int, right: int) -> Edge:
    if left == right:
        raise ValueError("loop")
    return (left, right) if left < right else (right, left)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_records(order: int) -> tuple[bytes, ...]:
    metadata = CATALOGS[order]
    request = urllib.request.Request(
        str(metadata["url"]),
        headers={"User-Agent": "Conway99-Wave17-independent-verifier/1"},
    )
    with urllib.request.urlopen(request, timeout=30.0) as response:
        compressed = response.read()
    observed_compressed = (len(compressed), sha256_bytes(compressed))
    expected_compressed = (
        metadata["compressed_bytes"],
        metadata["compressed_sha256"],
    )
    if observed_compressed != expected_compressed:
        raise AssertionError(
            f"order-{order} compressed catalog validation failed"
        )
    decompressed = gzip.decompress(compressed)
    observed_decompressed = (len(decompressed), sha256_bytes(decompressed))
    expected_decompressed = (
        metadata["decompressed_bytes"],
        metadata["decompressed_sha256"],
    )
    if observed_decompressed != expected_decompressed:
        raise AssertionError(
            f"order-{order} decompressed catalog validation failed"
        )
    records = tuple(line for line in decompressed.splitlines() if line)
    if len(records) != metadata["records"] or len(records) != len(set(records)):
        raise AssertionError(f"order-{order} record validation failed")
    return records


def parse_graph6(record: bytes) -> tuple[int, frozenset[Edge]]:
    if not record or record.startswith(b">>graph6<<"):
        raise ValueError("bare short graph6 required")
    order = record[0] - 63
    if not 0 <= order <= 62:
        raise ValueError("short graph6 order required")
    bit_stream = []
    for raw in record[1:]:
        value = raw - 63
        if not 0 <= value <= 63:
            raise ValueError("invalid graph6 byte")
        bit_stream.extend(
            (value >> shift) & 1 for shift in range(5, -1, -1)
        )
    required = order * (order - 1) // 2
    if len(bit_stream) < required:
        raise ValueError("truncated graph6")
    result = set()
    cursor = 0
    for right in range(1, order):
        for left in range(right):
            if bit_stream[cursor]:
                result.add((left, right))
            cursor += 1
    return order, frozenset(result)


def graph_rows(order: int, edges: Iterable[Edge]) -> tuple[frozenset[int], ...]:
    rows = [set() for _ in range(order)]
    for left, right in edges:
        if not 0 <= left < right < order:
            raise AssertionError("invalid edge")
        rows[left].add(right)
        rows[right].add(left)
    return tuple(frozenset(row) for row in rows)


def check_catalog_graph(order: int, edges: frozenset[Edge]) -> None:
    rows = graph_rows(order, edges)
    if len(edges) != 3 * order // 2 or any(len(row) != 3 for row in rows):
        raise AssertionError("catalog graph is not cubic")
    seen = {0}
    queue = [0]
    while queue:
        current = queue.pop()
        for neighbor in rows[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    if len(seen) != order:
        raise AssertionError("catalog graph is disconnected")
    for left, right in edges:
        if rows[left] & rows[right]:
            raise AssertionError("catalog graph has a triangle")
    for left, right in itertools.combinations(range(order), 2):
        if len(rows[left] & rows[right]) >= 2:
            raise AssertionError("catalog graph has a 4-cycle")


def three_by_three_edges() -> frozenset[Edge]:
    return frozenset(
        (left, right) for left in range(3) for right in range(3, 6)
    )


def make_cases() -> tuple[list[dict[str, object]], dict[str, object]]:
    cases = []
    for index, record in enumerate(fetch_records(18)):
        order, edges = parse_graph6(record)
        if order != 18:
            raise AssertionError("wrong order-18 record")
        check_catalog_graph(order, edges)
        cases.append(
            {
                "case_id": f"connected18-{index:03d}",
                "catalog_index": index,
                "record_sha256": sha256_bytes(record),
                "F_edges": edges,
                "components": 1,
            }
        )
    for index, record in enumerate(fetch_records(12)):
        order, edges12 = parse_graph6(record)
        if order != 12:
            raise AssertionError("wrong order-12 record")
        check_catalog_graph(order, edges12)
        shifted = frozenset(
            (left + 6, right + 6) for left, right in edges12
        )
        cases.append(
            {
                "case_id": f"k33-plus-connected12-{index:03d}",
                "catalog_index": index,
                "record_sha256": sha256_bytes(record),
                "F_edges": three_by_three_edges() | shifted,
                "components": 2,
            }
        )
    metadata = {
        str(order): {key: value for key, value in CATALOGS[order].items()}
        for order in sorted(CATALOGS)
    }
    return cases, metadata


def forced_k_pairs(f_edges: frozenset[Edge]) -> frozenset[Edge]:
    rows = graph_rows(18, f_edges)
    result = set(f_edges)
    for neighbors in rows:
        result.update(
            edge(left, right)
            for left, right in itertools.combinations(neighbors, 2)
        )
    return frozenset(result)


def support_candidates(
    f_edges: frozenset[Edge],
) -> tuple[tuple[int, int, tuple[Edge, ...]], ...]:
    points = tuple(sorted(f_edges))
    forbidden = forced_k_pairs(f_edges)
    candidates = []
    for left, right in itertools.combinations(range(27), 2):
        if set(points[left]) & set(points[right]):
            continue
        rectangle = tuple(
            sorted(
                edge(a, b)
                for a in points[left]
                for b in points[right]
            )
        )
        if set(rectangle) & forbidden:
            continue
        candidates.append((left, right, rectangle))
    return tuple(candidates)


def make_parity_rows(
    candidates: tuple[tuple[int, int, tuple[Edge, ...]], ...]
) -> tuple[int, ...]:
    result = []
    for point in range(27):
        mask = 0
        for index, (left, right, _) in enumerate(candidates):
            if point in (left, right):
                mask ^= 1 << index
        result.append(mask)
    for label_pair in itertools.combinations(range(18), 2):
        mask = 0
        for index, (_, _, rectangle) in enumerate(candidates):
            if label_pair in rectangle:
                mask ^= 1 << index
        result.append(mask)
    return tuple(result)


def reduced_kernel(
    input_rows: Iterable[int], variable_count: int
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    rows = [row for row in input_rows if row]
    pivot_count = 0
    pivot_columns = []
    for column in range(variable_count):
        source = None
        for index in range(pivot_count, len(rows)):
            if rows[index] & (1 << column):
                source = index
                break
        if source is None:
            continue
        rows[pivot_count], rows[source] = rows[source], rows[pivot_count]
        for index in range(len(rows)):
            if index != pivot_count and rows[index] & (1 << column):
                rows[index] ^= rows[pivot_count]
        pivot_columns.append(column)
        pivot_count += 1
        if pivot_count == len(rows):
            break
    reduced = tuple(rows[:pivot_count])
    pivot_set = set(pivot_columns)
    basis = []
    for free in range(variable_count):
        if free in pivot_set:
            continue
        vector = 1 << free
        for row, pivot in zip(reduced, pivot_columns):
            if row & (1 << free):
                vector |= 1 << pivot
        basis.append(vector)
    return reduced, tuple(pivot_columns), tuple(basis)


def vector_sequence_hash(values: Iterable[int], variable_count: int) -> str:
    byte_width = max(1, (variable_count + 7) // 8)
    digest = hashlib.sha256()
    digest.update(variable_count.to_bytes(2, "big"))
    for value in values:
        digest.update(value.to_bytes(byte_width, "little"))
    return digest.hexdigest()


def point_masks(
    candidates: tuple[tuple[int, int, tuple[Edge, ...]], ...]
) -> tuple[int, ...]:
    result = []
    for point in range(27):
        mask = 0
        for index, (left, right, _) in enumerate(candidates):
            if point == left or point == right:
                mask |= 1 << index
        result.append(mask)
    return tuple(result)


def enumerate_kernel(
    basis: tuple[int, ...], masks: tuple[int, ...]
) -> tuple[int, int]:
    total = 1 << len(basis)
    passing = 0
    vector = 0
    last_gray = 0
    for index in range(total):
        gray = index ^ (index >> 1)
        if index:
            difference = gray ^ last_gray
            vector ^= basis[difference.bit_length() - 1]
        last_gray = gray
        if all((vector & mask).bit_count() == 2 for mask in masks):
            passing += 1
    return total, passing


def expected_connected(case: dict[str, object]) -> dict[str, object]:
    candidates = support_candidates(case["F_edges"])
    parity = make_parity_rows(candidates)
    reduced, pivots, basis = reduced_kernel(parity, len(candidates))
    examined, passing = enumerate_kernel(basis, point_masks(candidates))
    if passing:
        raise AssertionError("parity kernel contains an admissible vector")
    return {
        "case_id": case["case_id"],
        "catalog_index": case["catalog_index"],
        "record_sha256": case["record_sha256"],
        "compatible_support_count": len(candidates),
        "parity_row_count": len(parity),
        "parity_matrix_sha256": vector_sequence_hash(
            parity, len(candidates)
        ),
        "parity_rank": len(pivots),
        "parity_nullity": len(basis),
        "rref_sha256": vector_sequence_hash(reduced, len(candidates)),
        "nullspace_basis_sha256": vector_sequence_hash(
            basis, len(candidates)
        ),
        "kernel_vectors_examined": examined,
        "point_degree_two_vectors": passing,
        "rejection": (
            "TRIVIAL_PARITY_KERNEL"
            if not basis
            else "EXHAUSTED_PARITY_KERNEL_NO_POINT_DEGREE_TWO_VECTOR"
        ),
    }


def expected_mixed(case: dict[str, object]) -> dict[str, object]:
    candidates = support_candidates(case["F_edges"])
    group_a = set(range(9))
    group_b = set(range(9, 27))
    inside_a = sum(
        left in group_a and right in group_a
        for left, right, _ in candidates
    )
    between = sum(
        (left in group_a and right in group_b)
        or (right in group_a and left in group_b)
        for left, right, _ in candidates
    )
    inside_b = sum(
        left in group_b and right in group_b
        for left, right, _ in candidates
    )
    forced_between = 18
    forced_inside_b = 9
    if inside_a != 0 or between != 162 or inside_b >= forced_inside_b:
        raise AssertionError("mixed count does not reject")
    return {
        "case_id": case["case_id"],
        "catalog_index": case["catalog_index"],
        "record_sha256": case["record_sha256"],
        "compatible_support_count": len(candidates),
        "K3,3_point_count": 9,
        "order12_point_count": 18,
        "within_K3,3_candidates": inside_a,
        "cross_component_candidates": between,
        "within_order12_candidates": inside_b,
        "forced_cross_R_edges": forced_between,
        "forced_internal_order12_R_edges": forced_inside_b,
        "rejection": "TOO_FEW_INTERNAL_ORDER12_CANDIDATES",
    }


def build_expected() -> dict[str, object]:
    cases, metadata = make_cases()
    connected = [
        expected_connected(case) for case in cases if case["components"] == 1
    ]
    mixed = [
        expected_mixed(case) for case in cases if case["components"] == 2
    ]
    histogram: dict[str, int] = {}
    rejection_counts: dict[str, int] = {}
    for row in connected:
        nullity = str(row["parity_nullity"])
        histogram[nullity] = histogram.get(nullity, 0) + 1
        rejection = str(row["rejection"])
        rejection_counts[rejection] = rejection_counts.get(rejection, 0) + 1
    return {
        "schema_version": 1,
        "scope": (
            "complete fixed-F exact-coverage obstruction for the frozen "
            "Wave17 n3=54 structural residual"
        ),
        "catalogs": metadata,
        "catalog_redistributed": False,
        "case_count": len(cases),
        "connected_case_count": len(connected),
        "mixed_component_case_count": len(mixed),
        "certificate_method": {
            "connected": (
                "GF(2) point-degree and rectangle-coverage parity kernel, "
                "followed by exhaustive kernel enumeration"
            ),
            "mixed": "direct compatible-support count forced by 2-regularity",
        },
        "summary": {
            "parity_nullity_histogram": dict(
                sorted(histogram.items(), key=lambda item: int(item[0]))
            ),
            "connected_rejections": dict(sorted(rejection_counts.items())),
            "mixed_rejections": {
                "TOO_FEW_INTERNAL_ORDER12_CANDIDATES": len(mixed)
            },
            "maximum_kernel_vectors_examined": max(
                row["kernel_vectors_examined"] for row in connected
            ),
            "total_point_degree_two_vectors": sum(
                row["point_degree_two_vectors"] for row in connected
            ),
        },
        "connected_cases": connected,
        "mixed_component_cases": mixed,
        "claim_label": "DERIVED_PENDING_INDEPENDENT_AUDIT",
        "conditional_n3_54": "EXCLUDED_DERIVED_PENDING_INDEPENDENT_AUDIT",
        "prospective_conditional_n3_lower_bound": 57,
        "prospective_conditional_induced_C6_lower_bound": 209343,
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
        "limitations": [
            "conditional on the frozen Wave17 F/R structural reduction",
            "discovery lane cannot verify its own certificate",
            "official catalog completeness and nonisomorphism are external premises",
            "no target existence or nonexistence result",
        ],
    }


def exact_compare(actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError("certificate differs from independent reconstruction")


def verify(path: Path) -> dict[str, object]:
    actual = json.loads(path.read_text(encoding="utf-8"))
    expected = build_expected()
    exact_compare(actual, expected)
    return {
        "status": "PASS",
        "certificate": path.as_posix(),
        "certificate_sha256": sha256_bytes(path.read_bytes()),
        "catalog_records_checked": 457,
        "connected_parity_kernels_checked": 455,
        "mixed_count_obstructions_checked": 2,
        "maximum_kernel_vectors_examined": expected["summary"][
            "maximum_kernel_vectors_examined"
        ],
        "conditional_n3_54": "EXCLUDED_DERIVED_PENDING_INDEPENDENT_AUDIT",
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.certificate)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
