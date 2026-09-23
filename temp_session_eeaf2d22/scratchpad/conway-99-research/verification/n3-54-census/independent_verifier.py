"""Independent verifier for the Wave 17 n3=54 fixed-F census.

The proof engine here is deliberately separate from the discovery engine:

* graphs are adjacency bit masks, not edge-set adjacency rows;
* a support variable is represented by its 180-bit equation syndrome;
* the nullspace is constructed by streaming *columns* through a highest-pivot
  XOR basis, rather than row-reducing the parity matrix; and
* every nonzero connected-case kernel is enumerated exhaustively.

A small row-oriented compatibility routine is retained only to reproduce the
algorithm-specific hashes committed by the discovery certificate.  It is not
used to decide the mathematical obstruction.
"""

from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import platform
import ssl
import sys
from typing import Iterable, Iterator, Sequence
import urllib.parse
import urllib.request


CATALOGS: dict[int, dict[str, object]] = {
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
}

DISCOVERY_FILES = (
    "census.py",
    "build_certificate.py",
    "verify_certificate.py",
    "test_certificate.py",
    "census-results.json",
    "exact-certificate.json",
    "verification-result.json",
)

Pair = tuple[int, int]
Candidate = tuple[int, int, int]
Case = dict[str, object]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def normalized_pair(left: int, right: int) -> Pair:
    if left == right:
        raise ValueError("a pair cannot be a loop")
    return (left, right) if left < right else (right, left)


def iter_set_bits(value: int) -> Iterator[int]:
    while value:
        low = value & -value
        yield low.bit_length() - 1
        value ^= low


def decode_short_graph6(record: bytes) -> tuple[int, ...]:
    """Decode a canonical bare short-form graph6 record into neighbor masks."""

    if not record:
        raise ValueError("empty graph6 record")
    if record.startswith(b">>graph6<<"):
        raise ValueError("graph6 header is not permitted in a catalog record")
    order = record[0] - 63
    if not 0 <= order <= 62:
        raise ValueError("only canonical short-form graph6 is permitted")
    edge_slots = order * (order - 1) // 2
    payload_groups = (edge_slots + 5) // 6
    if len(record) != 1 + payload_groups:
        raise ValueError("graph6 record is truncated or has trailing data")
    payload = []
    for raw in record[1:]:
        value = raw - 63
        if not 0 <= value <= 63:
            raise ValueError("graph6 payload byte is outside 63..126")
        payload.append(value)
    if edge_slots % 6 and payload:
        unused = 6 - edge_slots % 6
        if payload[-1] & ((1 << unused) - 1):
            raise ValueError("graph6 padding bits are nonzero")

    neighbors = [0] * order
    bit_index = 0
    for right in range(1, order):
        for left in range(right):
            group = payload[bit_index // 6]
            present = (group >> (5 - bit_index % 6)) & 1
            if present:
                neighbors[left] |= 1 << right
                neighbors[right] |= 1 << left
            bit_index += 1
    return tuple(neighbors)


def graph_edges(neighbors: Sequence[int]) -> tuple[Pair, ...]:
    return tuple(
        (left, right)
        for left in range(len(neighbors))
        for right in range(left + 1, len(neighbors))
        if neighbors[left] >> right & 1
    )


def graph_from_edges(order: int, edges: Iterable[Pair]) -> tuple[int, ...]:
    rows = [0] * order
    seen: set[Pair] = set()
    for raw_left, raw_right in edges:
        left, right = normalized_pair(raw_left, raw_right)
        if not 0 <= left < right < order:
            raise ValueError("edge endpoint outside graph order")
        if (left, right) in seen:
            raise ValueError("duplicate edge")
        seen.add((left, right))
        rows[left] |= 1 << right
        rows[right] |= 1 << left
    return tuple(rows)


def connected_components(neighbors: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    unseen = (1 << len(neighbors)) - 1
    components = []
    while unseen:
        root_bit = unseen & -unseen
        frontier = root_bit
        component = 0
        while frontier:
            vertex_bit = frontier & -frontier
            frontier ^= vertex_bit
            vertex = vertex_bit.bit_length() - 1
            component |= vertex_bit
            new = neighbors[vertex] & unseen & ~component
            frontier |= new
            unseen &= ~vertex_bit
        vertices = tuple(iter_set_bits(component))
        components.append(vertices)
    return tuple(sorted(components, key=lambda part: (len(part), part)))


def validate_simple_cubic(neighbors: Sequence[int]) -> None:
    order = len(neighbors)
    vertex_mask = (1 << order) - 1
    for vertex, row in enumerate(neighbors):
        if row & ~vertex_mask:
            raise AssertionError("adjacency mask leaves graph order")
        if row >> vertex & 1:
            raise AssertionError("loop in adjacency mask")
        if row.bit_count() != 3:
            raise AssertionError("graph is not cubic")
        for other in iter_set_bits(row):
            if not (neighbors[other] >> vertex & 1):
                raise AssertionError("adjacency mask is asymmetric")
    if len(graph_edges(neighbors)) != 3 * order // 2:
        raise AssertionError("cubic edge count is inconsistent")


def validate_girth_at_least_five(neighbors: Sequence[int]) -> None:
    order = len(neighbors)
    for left in range(order):
        for right in range(left + 1, order):
            common = (neighbors[left] & neighbors[right]).bit_count()
            if neighbors[left] >> right & 1 and common:
                raise AssertionError("triangle detected")
            if common >= 2:
                raise AssertionError("4-cycle detected")


def validate_catalog_graph(neighbors: Sequence[int], expected_order: int) -> None:
    if len(neighbors) != expected_order:
        raise AssertionError("catalog record has the wrong order")
    validate_simple_cubic(neighbors)
    if len(connected_components(neighbors)) != 1:
        raise AssertionError("catalog record is disconnected")
    validate_girth_at_least_five(neighbors)


def validate_catalog_blob(
    order: int, compressed: bytes
) -> tuple[tuple[bytes, ...], bytes]:
    expected = CATALOGS[order]
    if len(compressed) != expected["compressed_bytes"]:
        raise AssertionError(f"order-{order} compressed byte count mismatch")
    if sha256_bytes(compressed) != expected["compressed_sha256"]:
        raise AssertionError(f"order-{order} compressed SHA-256 mismatch")
    try:
        decompressed = gzip.decompress(compressed)
    except (EOFError, OSError) as exc:
        raise AssertionError(f"order-{order} gzip stream is invalid") from exc
    if len(decompressed) != expected["decompressed_bytes"]:
        raise AssertionError(f"order-{order} decompressed byte count mismatch")
    if sha256_bytes(decompressed) != expected["decompressed_sha256"]:
        raise AssertionError(f"order-{order} decompressed SHA-256 mismatch")
    if not decompressed.endswith(b"\n"):
        raise AssertionError(f"order-{order} catalog lacks its terminal newline")
    split = decompressed.split(b"\n")
    if split[-1] != b"" or any(not record for record in split[:-1]):
        raise AssertionError(f"order-{order} catalog contains a blank record")
    records = tuple(split[:-1])
    if len(records) != expected["records"]:
        raise AssertionError(f"order-{order} record count mismatch")
    if len(set(records)) != len(records):
        raise AssertionError(f"order-{order} catalog repeats a raw record")
    for record in records:
        validate_catalog_graph(decode_short_graph6(record), order)
    return records, decompressed


def fetch_catalog(order: int) -> tuple[tuple[bytes, ...], dict[str, object]]:
    expected = CATALOGS[order]
    request = urllib.request.Request(
        str(expected["url"]),
        headers={"User-Agent": "Conway99-Wave17-hostile-verifier/1"},
    )
    with urllib.request.urlopen(request, timeout=30.0) as response:
        status = getattr(response, "status", None)
        final_url = response.geturl()
        compressed = response.read()
        response_headers = {
            key: response.headers.get(key)
            for key in ("Content-Length", "Content-Type", "ETag", "Last-Modified")
        }
    parsed = urllib.parse.urlsplit(final_url)
    if status != 200:
        raise AssertionError(f"order-{order} catalog returned HTTP {status}")
    if parsed.scheme != "https" or parsed.hostname != "houseofgraphs.org":
        raise AssertionError(f"order-{order} catalog redirected off trusted HTTPS host")
    if final_url != expected["url"]:
        raise AssertionError(f"order-{order} catalog URL changed after redirect")
    records, decompressed = validate_catalog_blob(order, compressed)
    sequence = hashlib.sha256()
    for record in records:
        sequence.update(len(record).to_bytes(2, "big"))
        sequence.update(record)
    observed = {
        "url": expected["url"],
        "final_url": final_url,
        "http_status": status,
        "response_headers": response_headers,
        "compressed_bytes": len(compressed),
        "compressed_sha256": sha256_bytes(compressed),
        "decompressed_bytes": len(decompressed),
        "decompressed_sha256": sha256_bytes(decompressed),
        "records": len(records),
        "unique_raw_records": len(set(records)),
        "record_sequence_sha256": sequence.hexdigest(),
    }
    return records, observed


def k33_edges(offset: int = 0) -> tuple[Pair, ...]:
    return tuple(
        (offset + left, offset + right)
        for left in range(3)
        for right in range(3, 6)
    )


def build_cases(
    records12: Sequence[bytes], records18: Sequence[bytes]
) -> list[Case]:
    cases: list[Case] = []
    for index, record in enumerate(records18):
        neighbors = decode_short_graph6(record)
        validate_catalog_graph(neighbors, 18)
        cases.append(
            {
                "case_id": f"connected18-{index:03d}",
                "family": "connected_cubic_girth5_order18",
                "catalog_order": 18,
                "catalog_index": index,
                "record_sha256": sha256_bytes(record),
                "neighbors": neighbors,
                "component_count": 1,
            }
        )
    for index, record in enumerate(records12):
        small = decode_short_graph6(record)
        validate_catalog_graph(small, 12)
        shifted = tuple(
            (left + 6, right + 6) for left, right in graph_edges(small)
        )
        combined = graph_from_edges(18, (*k33_edges(), *shifted))
        validate_simple_cubic(combined)
        components = connected_components(combined)
        if tuple(sorted(map(len, components))) != (6, 12):
            raise AssertionError("mixed case does not have components 6+12")
        for left in range(18):
            for right in range(left + 1, 18):
                if not (combined[left] >> right & 1):
                    if (combined[left] & combined[right]).bit_count() == 2:
                        raise AssertionError("mixed case violates the codegree-2 ban")
                elif combined[left] & combined[right]:
                    raise AssertionError("mixed case contains a triangle")
        cases.append(
            {
                "case_id": f"k33-plus-connected12-{index:03d}",
                "family": "K3,3_plus_connected_cubic_girth5_order12",
                "catalog_order": 12,
                "catalog_index": index,
                "record_sha256": sha256_bytes(record),
                "neighbors": combined,
                "component_count": 2,
            }
        )
    if len(cases) != 457:
        raise AssertionError("residual case count is not 457")
    if Counter(case["component_count"] for case in cases) != {1: 455, 2: 2}:
        raise AssertionError("residual component-family coverage changed")
    return cases


def label_pair_index(order: int) -> dict[Pair, int]:
    return {
        pair: index
        for index, pair in enumerate(itertools.combinations(range(order), 2))
    }


def forced_k_pair_ids(neighbors: Sequence[int]) -> frozenset[int]:
    index = label_pair_index(len(neighbors))
    forced: set[int] = set()
    for pair in graph_edges(neighbors):
        forced.add(index[pair])
    for center in range(len(neighbors)):
        local = tuple(iter_set_bits(neighbors[center]))
        for left, right in itertools.combinations(local, 2):
            forced.add(index[normalized_pair(left, right)])
    return frozenset(forced)


def compatible_supports(neighbors: Sequence[int]) -> tuple[Candidate, ...]:
    """Return (point-left, point-right, rectangle-pair-bitmask) candidates."""

    points = graph_edges(neighbors)
    pair_index = label_pair_index(len(neighbors))
    forced = forced_k_pair_ids(neighbors)
    candidates = []
    for left in range(len(points)):
        point_left = points[left]
        endpoint_mask_left = (1 << point_left[0]) | (1 << point_left[1])
        for right in range(left + 1, len(points)):
            point_right = points[right]
            endpoint_mask_right = (1 << point_right[0]) | (1 << point_right[1])
            if endpoint_mask_left & endpoint_mask_right:
                continue
            rectangle_ids = tuple(
                pair_index[normalized_pair(a, b)]
                for a in point_left
                for b in point_right
            )
            if len(set(rectangle_ids)) != 4:
                raise AssertionError("disjoint point edges did not make a rectangle")
            if any(pair_id in forced for pair_id in rectangle_ids):
                continue
            rectangle_mask = sum(1 << pair_id for pair_id in rectangle_ids)
            candidates.append((left, right, rectangle_mask))
    return tuple(candidates)


def candidate_syndromes(
    candidates: Sequence[Candidate], point_count: int, label_order: int
) -> tuple[int, ...]:
    pair_count = label_order * (label_order - 1) // 2
    result = []
    for left, right, rectangle_mask in candidates:
        if not 0 <= left < right < point_count:
            raise AssertionError("candidate point endpoint is invalid")
        if rectangle_mask >> pair_count:
            raise AssertionError("candidate rectangle leaves label-pair range")
        result.append(
            (1 << left)
            | (1 << right)
            | (rectangle_mask << point_count)
        )
    return tuple(result)


def column_kernel_basis(columns: Sequence[int]) -> tuple[int, tuple[int, ...]]:
    """Stream equation-syndrome columns into a highest-pivot XOR basis.

    Each dependency bit mask returned is a nullspace vector in variable
    coordinates.  The construction is independent of row reduction.
    """

    pivots: dict[int, tuple[int, int]] = {}
    dependencies = []
    for column_index, raw_column in enumerate(columns):
        value = raw_column
        combination = 1 << column_index
        while value:
            pivot = value.bit_length() - 1
            previous = pivots.get(pivot)
            if previous is None:
                pivots[pivot] = (value, combination)
                break
            value ^= previous[0]
            combination ^= previous[1]
        if not value:
            dependencies.append(combination)
    return len(pivots), tuple(dependencies)


def syndrome_of_vector(columns: Sequence[int], vector: int) -> int:
    syndrome = 0
    for index in iter_set_bits(vector):
        if index >= len(columns):
            raise AssertionError("kernel vector leaves variable range")
        syndrome ^= columns[index]
    return syndrome


def assert_kernel_basis(columns: Sequence[int], basis: Sequence[int]) -> None:
    incremental: dict[int, int] = {}
    for vector in basis:
        if not vector:
            raise AssertionError("zero vector included in nullspace basis")
        if syndrome_of_vector(columns, vector):
            raise AssertionError("claimed nullspace vector has nonzero syndrome")
        reduced = vector
        while reduced:
            pivot = reduced.bit_length() - 1
            if pivot not in incremental:
                incremental[pivot] = reduced
                break
            reduced ^= incremental[pivot]
        if not reduced:
            raise AssertionError("nullspace basis is linearly dependent")


def point_variable_masks(
    candidates: Sequence[Candidate], point_count: int
) -> tuple[int, ...]:
    masks = [0] * point_count
    for variable, (left, right, _) in enumerate(candidates):
        masks[left] |= 1 << variable
        masks[right] |= 1 << variable
    return tuple(masks)


def enumerate_kernel_degree_two(
    basis: Sequence[int], point_masks: Sequence[int]
) -> tuple[int, int]:
    """Enumerate every kernel vector; count exact degree-two selections."""

    vector_count = 1 << len(basis)
    passing = 0
    current = 0
    prior_gray = 0
    for counter in range(vector_count):
        gray = counter ^ (counter >> 1)
        if counter:
            changed = gray ^ prior_gray
            current ^= basis[changed.bit_length() - 1]
        prior_gray = gray
        if all((current & mask).bit_count() == 2 for mask in point_masks):
            passing += 1
    return vector_count, passing


def rows_from_columns(columns: Sequence[int], equation_count: int) -> tuple[int, ...]:
    rows = [0] * equation_count
    for variable, column in enumerate(columns):
        for equation in iter_set_bits(column):
            if equation >= equation_count:
                raise AssertionError("column leaves equation range")
            rows[equation] |= 1 << variable
    return tuple(rows)


def low_pivot_row_commitments(
    rows: Iterable[int], variable_count: int
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    """Reproduce discovery's deterministic digest objects, not its proof."""

    work = [row for row in rows if row]
    rank = 0
    pivots = []
    for variable in range(variable_count):
        source = next(
            (
                index
                for index in range(rank, len(work))
                if work[index] >> variable & 1
            ),
            None,
        )
        if source is None:
            continue
        work[rank], work[source] = work[source], work[rank]
        pivot_row = work[rank]
        for index in range(len(work)):
            if index != rank and work[index] >> variable & 1:
                work[index] ^= pivot_row
        pivots.append(variable)
        rank += 1
        if rank == len(work):
            break
    reduced = tuple(work[:rank])
    pivot_set = set(pivots)
    basis = []
    for free in range(variable_count):
        if free in pivot_set:
            continue
        vector = 1 << free
        for row, pivot in zip(reduced, pivots):
            if row >> free & 1:
                vector |= 1 << pivot
        basis.append(vector)
    return reduced, tuple(pivots), tuple(basis)


def packed_sequence_sha256(values: Iterable[int], variable_count: int) -> str:
    byte_width = max(1, (variable_count + 7) // 8)
    digest = hashlib.sha256()
    digest.update(variable_count.to_bytes(2, "big"))
    for value in values:
        digest.update(value.to_bytes(byte_width, "little"))
    return digest.hexdigest()


def connected_case_result(case: Case) -> dict[str, object]:
    neighbors = case["neighbors"]
    assert isinstance(neighbors, tuple)
    candidates = compatible_supports(neighbors)
    columns = candidate_syndromes(candidates, 27, 18)
    independent_rank, independent_basis = column_kernel_basis(columns)
    assert_kernel_basis(columns, independent_basis)
    if independent_rank + len(independent_basis) != len(candidates):
        raise AssertionError("column rank-nullity identity failed")
    examined, passing = enumerate_kernel_degree_two(
        independent_basis, point_variable_masks(candidates, 27)
    )
    if passing:
        raise AssertionError(
            f"{case['case_id']} has a degree-two vector in the parity relaxation"
        )

    parity_rows = rows_from_columns(columns, 180)
    reduced, pivots, digest_basis = low_pivot_row_commitments(
        parity_rows, len(candidates)
    )
    if len(pivots) != independent_rank:
        raise AssertionError("column and row ranks disagree")
    assert_kernel_basis(columns, digest_basis)
    if len(digest_basis) != len(independent_basis):
        raise AssertionError("column and row nullities disagree")
    return {
        "case_id": case["case_id"],
        "catalog_index": case["catalog_index"],
        "record_sha256": case["record_sha256"],
        "compatible_support_count": len(candidates),
        "parity_row_count": 180,
        "parity_matrix_sha256": packed_sequence_sha256(
            parity_rows, len(candidates)
        ),
        "parity_rank": independent_rank,
        "parity_nullity": len(independent_basis),
        "rref_sha256": packed_sequence_sha256(reduced, len(candidates)),
        "nullspace_basis_sha256": packed_sequence_sha256(
            digest_basis, len(candidates)
        ),
        "kernel_vectors_examined": examined,
        "point_degree_two_vectors": passing,
        "rejection": (
            "TRIVIAL_PARITY_KERNEL"
            if not independent_basis
            else "EXHAUSTED_PARITY_KERNEL_NO_POINT_DEGREE_TWO_VECTOR"
        ),
    }


def mixed_partition_counts(
    candidates: Sequence[Candidate],
    first_points: frozenset[int],
    second_points: frozenset[int],
) -> tuple[int, int, int]:
    within_first = 0
    between = 0
    within_second = 0
    for left, right, _ in candidates:
        if left in first_points and right in first_points:
            within_first += 1
        elif left in second_points and right in second_points:
            within_second += 1
        elif (
            left in first_points
            and right in second_points
            or right in first_points
            and left in second_points
        ):
            between += 1
        else:
            raise AssertionError("candidate does not respect point partition")
    return within_first, between, within_second


def mixed_degree_count_obstruction(
    first_point_count: int,
    second_point_count: int,
    within_first_candidates: int,
    within_second_candidates: int,
) -> tuple[bool, int, int]:
    """Return obstruction and forced selected cross/second-internal counts."""

    if within_first_candidates:
        return False, -1, -1
    forced_cross = 2 * first_point_count
    remaining_second_degree = 2 * second_point_count - forced_cross
    if remaining_second_degree < 0 or remaining_second_degree % 2:
        raise AssertionError("mixed degree arithmetic is inconsistent")
    forced_second_internal = remaining_second_degree // 2
    return (
        within_second_candidates < forced_second_internal,
        forced_cross,
        forced_second_internal,
    )


def mixed_case_result(case: Case) -> dict[str, object]:
    neighbors = case["neighbors"]
    assert isinstance(neighbors, tuple)
    points = graph_edges(neighbors)
    if len(points) != 27 or points[:9] != k33_edges():
        raise AssertionError("mixed point ordering does not isolate K3,3 first")
    candidates = compatible_supports(neighbors)
    first = frozenset(range(9))
    second = frozenset(range(9, 27))
    inside_first, between, inside_second = mixed_partition_counts(
        candidates, first, second
    )
    obstructed, forced_cross, forced_second = mixed_degree_count_obstruction(
        9, 18, inside_first, inside_second
    )
    if between != 9 * 18:
        raise AssertionError("not every mixed-component point pair is compatible")
    if not obstructed:
        raise AssertionError("mixed degree count does not obstruct this case")
    return {
        "case_id": case["case_id"],
        "catalog_index": case["catalog_index"],
        "record_sha256": case["record_sha256"],
        "compatible_support_count": len(candidates),
        "K3,3_point_count": 9,
        "order12_point_count": 18,
        "within_K3,3_candidates": inside_first,
        "cross_component_candidates": between,
        "within_order12_candidates": inside_second,
        "forced_cross_R_edges": forced_cross,
        "forced_internal_order12_R_edges": forced_second,
        "rejection": "TOO_FEW_INTERNAL_ORDER12_CANDIDATES",
    }


def exact_equal(actual: object, expected: object, context: str) -> None:
    if actual != expected:
        raise AssertionError(f"{context} differs from independent reconstruction")


def validate_discovery_certificate(
    certificate: dict[str, object],
    connected: list[dict[str, object]],
    mixed: list[dict[str, object]],
) -> dict[str, object]:
    histogram = Counter(str(row["parity_nullity"]) for row in connected)
    rejection_counts = Counter(str(row["rejection"]) for row in connected)
    expected_summary = {
        "parity_nullity_histogram": dict(
            sorted(histogram.items(), key=lambda item: int(item[0]))
        ),
        "connected_rejections": dict(sorted(rejection_counts.items())),
        "mixed_rejections": {"TOO_FEW_INTERNAL_ORDER12_CANDIDATES": 2},
        "maximum_kernel_vectors_examined": max(
            int(row["kernel_vectors_examined"]) for row in connected
        ),
        "total_point_degree_two_vectors": sum(
            int(row["point_degree_two_vectors"]) for row in connected
        ),
    }
    exact_equal(certificate.get("schema_version"), 1, "certificate schema")
    exact_equal(certificate.get("case_count"), 457, "certificate case count")
    exact_equal(
        certificate.get("connected_case_count"), 455, "connected case count"
    )
    exact_equal(
        certificate.get("mixed_component_case_count"), 2, "mixed case count"
    )
    exact_equal(
        certificate.get("connected_cases"), connected, "connected certificate rows"
    )
    exact_equal(
        certificate.get("mixed_component_cases"), mixed, "mixed certificate rows"
    )
    exact_equal(certificate.get("summary"), expected_summary, "certificate summary")
    exact_equal(
        certificate.get("catalogs"),
        {str(order): dict(CATALOGS[order]) for order in sorted(CATALOGS)},
        "certificate catalog metadata",
    )
    exact_equal(
        certificate.get("claim_label"),
        "DERIVED_PENDING_INDEPENDENT_AUDIT",
        "certificate claim label",
    )
    exact_equal(
        certificate.get("conditional_n3_54"),
        "EXCLUDED_DERIVED_PENDING_INDEPENDENT_AUDIT",
        "certificate conditional status",
    )
    exact_equal(certificate.get("conway_99"), "UNKNOWN", "target status")
    exact_equal(certificate.get("novelty"), "UNKNOWN", "novelty status")
    exact_equal(
        certificate.get("prospective_conditional_n3_lower_bound"),
        57,
        "prospective n3 bound",
    )
    exact_equal(
        certificate.get("prospective_conditional_induced_C6_lower_bound"),
        209343,
        "prospective induced-C6 bound",
    )
    if 209286 + 57 != 209343:
        raise AssertionError("prospective induced-C6 arithmetic failed")
    return expected_summary


def validate_raw_census(
    census: dict[str, object],
    cases: Sequence[Case],
    connected: Sequence[dict[str, object]],
    mixed: Sequence[dict[str, object]],
) -> dict[str, int]:
    exact_equal(census.get("schema_version"), 1, "raw census schema")
    exact_equal(census.get("full_case_count"), 457, "raw census full count")
    exact_equal(
        census.get("slice"), {"start": 0, "stop": 457, "count": 457}, "raw slice"
    )
    exact_equal(
        census.get("claim_status"),
        "CANDIDATE_CENSUS_PENDING_INDEPENDENT_VALIDATION",
        "raw census status",
    )
    raw_cases = census.get("cases")
    if not isinstance(raw_cases, list) or len(raw_cases) != 457:
        raise AssertionError("raw census case rows are missing")
    proof_rows = {
        row["case_id"]: row for row in [*connected, *mixed]
    }
    raw_status_counts: Counter[str] = Counter()
    for case, raw in zip(cases, raw_cases):
        if not isinstance(raw, dict):
            raise AssertionError("raw census case is not an object")
        exact_equal(raw.get("case_id"), case["case_id"], "raw case id")
        exact_equal(
            raw.get("catalog_index"), case["catalog_index"], "raw catalog index"
        )
        exact_equal(
            raw.get("record_sha256"), case["record_sha256"], "raw record hash"
        )
        proof = proof_rows[str(case["case_id"])]
        exact_equal(
            raw.get("compatible_support_count"),
            proof["compatible_support_count"],
            "raw compatible-support count",
        )
        stages = raw.get("stages")
        if not isinstance(stages, dict):
            raise AssertionError("raw stages are missing")
        exact_status = stages.get("exact_coverage")
        if not isinstance(exact_status, dict):
            raise AssertionError("raw exact-coverage status is missing")
        status = str(exact_status.get("status"))
        raw_status_counts[status] += 1
        if status != "UNSAT_UNVERIFIED":
            raise AssertionError("unexpected raw solver status")
        for later in (
            "matching",
            "common_neighbor_caps",
            "spectrum",
            "binary_restrictions",
        ):
            stage = stages.get(later)
            if not isinstance(stage, dict) or stage.get("status") != "NOT_REACHED":
                raise AssertionError("raw census unexpectedly reached a later stage")
    return dict(sorted(raw_status_counts.items()))


def validate_discovery_result(
    result: dict[str, object], certificate_path: Path
) -> None:
    exact_equal(result.get("status"), "PASS", "discovery verifier status")
    exact_equal(
        result.get("certificate_sha256"),
        sha256_file(certificate_path),
        "discovery certificate file hash",
    )
    exact_equal(
        result.get("catalog_records_checked"), 457, "discovery catalog count"
    )
    exact_equal(
        result.get("connected_parity_kernels_checked"),
        455,
        "discovery connected count",
    )
    exact_equal(
        result.get("mixed_count_obstructions_checked"),
        2,
        "discovery mixed count",
    )
    exact_equal(
        result.get("maximum_kernel_vectors_examined"),
        262144,
        "discovery maximum kernel enumeration",
    )
    exact_equal(
        result.get("conditional_n3_54"),
        "EXCLUDED_DERIVED_PENDING_INDEPENDENT_AUDIT",
        "discovery conditional status",
    )
    exact_equal(result.get("conway_99"), "UNKNOWN", "discovery target status")
    exact_equal(result.get("novelty"), "UNKNOWN", "discovery novelty status")


def stable_semantic_digest(
    connected: Sequence[dict[str, object]],
    mixed: Sequence[dict[str, object]],
) -> str:
    payload = {
        "connected": [
            {
                key: row[key]
                for key in (
                    "case_id",
                    "record_sha256",
                    "compatible_support_count",
                    "parity_rank",
                    "parity_nullity",
                    "kernel_vectors_examined",
                    "point_degree_two_vectors",
                )
            }
            for row in connected
        ],
        "mixed": list(mixed),
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return sha256_bytes(encoded)


def run(
    attempts_dir: Path,
    structural_report: Path,
    discovery_report: Path,
    freeze_path: Path,
) -> dict[str, object]:
    records12, observed12 = fetch_catalog(12)
    records18, observed18 = fetch_catalog(18)
    cases = build_cases(records12, records18)

    connected_results = []
    mixed_results = []
    for case in cases:
        if case["component_count"] == 1:
            connected_results.append(connected_case_result(case))
        else:
            mixed_results.append(mixed_case_result(case))

    certificate_path = attempts_dir / "exact-certificate.json"
    raw_census_path = attempts_dir / "census-results.json"
    discovery_result_path = attempts_dir / "verification-result.json"
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    raw_census = json.loads(raw_census_path.read_text(encoding="utf-8"))
    discovery_result = json.loads(
        discovery_result_path.read_text(encoding="utf-8")
    )
    summary = validate_discovery_certificate(
        certificate, connected_results, mixed_results
    )
    raw_statuses = validate_raw_census(
        raw_census, cases, connected_results, mixed_results
    )
    validate_discovery_result(discovery_result, certificate_path)

    artifact_hashes = {
        name: sha256_file(attempts_dir / name) for name in DISCOVERY_FILES
    }
    nontrivial = [
        row for row in connected_results if int(row["parity_nullity"]) > 0
    ]
    nullity_histogram = dict(
        sorted(
            Counter(
                str(row["parity_nullity"]) for row in connected_results
            ).items(),
            key=lambda item: int(item[0]),
        )
    )
    return {
        "schema_version": 1,
        "role": "verifier",
        "status": "PASS",
        "claim_label": "VERIFIED",
        "scope": (
            "conditional exclusion of the frozen Wave17 n3=54 F/R residual; "
            "not a resolution of SRG(99,14,1,2)"
        ),
        "preinspection_freeze": {
            "path": freeze_path.as_posix(),
            "sha256": sha256_file(freeze_path),
        },
        "structural_input": {
            "path": structural_report.as_posix(),
            "sha256": sha256_file(structural_report),
            "status_consumed": "DERIVED; audited separately from this census",
        },
        "discovery_report": {
            "path": discovery_report.as_posix(),
            "sha256": sha256_file(discovery_report),
        },
        "catalogs": {"12": observed12, "18": observed18},
        "coverage": {
            "total_cases": 457,
            "connected_order18": 455,
            "mixed_K3,3_plus_order12": 2,
            "excluded_3K3,3_branch_consumed_from_structural_input": True,
            "official_catalog_completeness_and_one_per_isomorphism_class": (
                "EXTERNAL_PREMISE"
            ),
        },
        "connected_parity_obstruction": {
            "cases_checked": len(connected_results),
            "trivial_kernels": sum(
                not int(row["parity_nullity"]) for row in connected_results
            ),
            "nontrivial_kernels_exhausted": len(nontrivial),
            "nullity_histogram": nullity_histogram,
            "maximum_nullity": max(
                int(row["parity_nullity"]) for row in connected_results
            ),
            "maximum_kernel_vectors_examined": max(
                int(row["kernel_vectors_examined"]) for row in connected_results
            ),
            "total_kernel_vectors_examined": sum(
                int(row["kernel_vectors_examined"]) for row in connected_results
            ),
            "degree_two_vectors": sum(
                int(row["point_degree_two_vectors"])
                for row in connected_results
            ),
            "discovery_summary_exact_match": summary,
        },
        "mixed_degree_count_obstruction": {
            "cases_checked": len(mixed_results),
            "cases": mixed_results,
        },
        "raw_sat_boundary": {
            "statuses": raw_statuses,
            "used_as_evidence": False,
        },
        "discovery_artifact_sha256": artifact_hashes,
        "semantic_manifest_sha256": stable_semantic_digest(
            connected_results, mixed_results
        ),
        "certificate_checks": {
            "connected_rows_exactly_matched": len(connected_results),
            "mixed_rows_exactly_matched": len(mixed_results),
            "algorithm_specific_matrix_rref_basis_hashes_matched": True,
            "discovery_result_certificate_hash_matched": True,
        },
        "conditional_n3_54": "EXCLUDED_VERIFIED",
        "prospective_conditional_n3_lower_bound": 57,
        "prospective_conditional_induced_C6_lower_bound": 209343,
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
        "tool_versions": {
            "python": sys.version,
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "openssl": ssl.OPENSSL_VERSION,
            "external_python_packages_used": [],
        },
        "limitations": [
            "conditional on the frozen structural F/R reduction",
            "catalog completeness and isomorphism-class coverage are external premises",
            "catalog bytes were fetched and validated in memory but not redistributed",
            "the original SRG target and novelty remain UNKNOWN",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--attempts-dir",
        type=Path,
        default=Path("attempts/wave17-n3-54-census"),
    )
    parser.add_argument(
        "--structural-report",
        type=Path,
        default=Path("agents/2026-07-23-wave17-n3-54-structural.md"),
    )
    parser.add_argument(
        "--discovery-report",
        type=Path,
        default=Path("agents/2026-07-23-wave17-n3-54-census.md"),
    )
    parser.add_argument(
        "--freeze",
        type=Path,
        default=Path("verification/n3-54-census/00-preinspection-freeze.md"),
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run(
        args.attempts_dir,
        args.structural_report,
        args.discovery_report,
        args.freeze,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
