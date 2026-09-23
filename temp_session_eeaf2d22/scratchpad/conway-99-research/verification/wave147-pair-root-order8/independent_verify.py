"""Independent exact verifier for the sealed Wave147 pair-root package.

No Wave147 Python module is imported or executed.  This checker rebuilds the
flag bases and order-eight class stream, replays the complete deletion
artifact, reconstructs representative coefficient matrices, and evaluates
the rook-graph control using standard-library integer arithmetic.
"""

from __future__ import annotations

import ctypes
import gzip
import hashlib
import itertools
import json
from fractions import Fraction
from functools import lru_cache
from math import comb
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave147-alternative-lane"
WAVE45 = (
    ROOT
    / "attempts"
    / "wave45-flag-moment"
    / "checkpoint-v1-moment-coefficients.json"
)
STORED_RESULT = DISCOVERY / "exact-results.json"
COEFFICIENT_GZIP = DISCOVERY / "coefficients.json.gz"
OUTPUT = HERE / "verification-results.json"

EXPECTED_DISCOVERY_MANIFEST = (
    "0c7585f996374246918948eb1537e61e2e165474f815a66eff24bf82e7c8e690"
)
EXPECTED_WAVE45 = (
    "ffcf9f9942446d66c3559d97954217af3ba17c1978ea9417c6e99920d4a45420"
)
EXPECTED_STREAMS = {
    5: (21, "f2717bd1bacb92b0a13010fa93e44b8a77d0958c2bf74a94cde323ace56a1e9e", 2),
    6: (62, "eb49cbaa20bfa2c6a64d56a0500a6ed1525727e9fa639d2b577b2862cb7a197a", 2),
    7: (208, "6d4a9643e0377fabd32f2fad5fb284d48dee9612fc5910f96796ee2dd348f0b6", 3),
    8: (916, "c2cf3604abc76a537eca21f1a8ef041697ca40d8ad41668d25eb412b9cd67337", 4),
}
MIN_FREE_MEMORY_PERCENT = 20.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )


def memory_status() -> dict[str, float]:
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

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))),
        "GlobalMemoryStatusEx failed",
    )
    free_percent = 100.0 * status.ullAvailPhys / status.ullTotalPhys
    require(
        free_percent >= MIN_FREE_MEMORY_PERCENT,
        f"free physical memory {free_percent:.2f}% below verifier floor",
    )
    return {
        "free_percent": free_percent,
        "free_gib": status.ullAvailPhys / (1 << 30),
        "floor_percent": MIN_FREE_MEMORY_PERCENT,
    }


def verify_manifest() -> dict:
    path = DISCOVERY / "package-manifest.sha256"
    actual_manifest = sha256(path)
    rows = []
    failures = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        candidate = (DISCOVERY / relative.strip()).resolve()
        try:
            candidate.relative_to(DISCOVERY.resolve())
        except ValueError:
            failures.append(f"path escape: {relative}")
            continue
        if not candidate.is_file():
            failures.append(f"missing: {relative}")
            continue
        actual = sha256(candidate)
        rows.append(
            {
                "path": relative.strip(),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "pass": actual == expected,
            }
        )
        if actual != expected:
            failures.append(f"hash mismatch: {relative}")
    return {
        "manifest_sha256": actual_manifest,
        "expected_manifest_sha256": EXPECTED_DISCOVERY_MANIFEST,
        "manifest_pass": actual_manifest == EXPECTED_DISCOVERY_MANIFEST,
        "entry_count": len(rows),
        "entries_pass": not failures,
        "failures": failures,
    }


@lru_cache(maxsize=None)
def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    )


@lru_cache(maxsize=None)
def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def adjacency_rows(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for position, (left, right) in enumerate(edges(order)):
        if (mask >> position) & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def mask_from_edges(order: int, graph_edges: Iterable[tuple[int, int]]) -> int:
    positions = edge_positions(order)
    result = 0
    for left, right in graph_edges:
        result |= 1 << positions[tuple(sorted((left, right)))]
    return result


def locally_admissible(mask: int, order: int) -> bool:
    rows = adjacency_rows(mask, order)
    for left in range(order):
        if rows[left].bit_count() > 14:
            return False
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            if (rows[left] >> right) & 1:
                if common > 1:
                    return False
            elif common > 2:
                return False
    return True


def transform_mask(mask: int, order: int, permutation: Sequence[int]) -> int:
    positions = edge_positions(order)
    result = 0
    for position, (left, right) in enumerate(edges(order)):
        if not ((mask >> position) & 1):
            continue
        image = tuple(sorted((permutation[left], permutation[right])))
        result |= 1 << positions[image]
    return result


def canonical_flag(mask: int) -> int:
    return min(
        transform_mask(mask, 5, (0, 1) + free_order)
        for free_order in itertools.permutations((2, 3, 4))
    )


def flag_basis(root_edge: bool) -> tuple[int, ...]:
    representatives = set()
    for mask in range(1 << comb(5, 2)):
        if bool(mask & 1) != root_edge or not locally_admissible(mask, 5):
            continue
        representatives.add(canonical_flag(mask))
    return tuple(sorted(representatives))


@lru_cache(maxsize=None)
def canonical_unrooted(mask: int, order: int) -> int:
    """Canonicalize completely using the isomorphism-invariant degree cells."""
    rows = adjacency_rows(mask, order)
    groups: dict[int, list[int]] = {}
    for vertex, row in enumerate(rows):
        groups.setdefault(row.bit_count(), []).append(vertex)

    starts = 0
    choices = []
    for degree in sorted(groups):
        sources = groups[degree]
        targets = tuple(range(starts, starts + len(sources)))
        starts += len(sources)
        choices.append(
            tuple(
                tuple(zip(sources, target_order))
                for target_order in itertools.permutations(targets)
            )
        )

    best = None
    for selected in itertools.product(*choices):
        permutation = [0] * order
        for cell in selected:
            for source, target in cell:
                permutation[source] = target
        candidate = transform_mask(mask, order, permutation)
        if best is None or candidate < best:
            best = candidate
    require(best is not None, "empty canonicalization")
    return best


def class_stream_hash(classes: Sequence[int], width: int) -> str:
    return hashlib.sha256(
        b"".join(mask.to_bytes(width, "big") for mask in classes)
    ).hexdigest()


def frozen_class_streams() -> dict[int, tuple[int, ...]]:
    require(sha256(WAVE45) == EXPECTED_WAVE45, "Wave45 input drift")
    payload = json.loads(WAVE45.read_text(encoding="utf-8"))
    records = payload["families"]["vertex"]["class_coefficients"]
    streams = {}
    for order in (5, 6, 7):
        stream = tuple(
            sorted(
                {
                    int(record["canonical_mask"])
                    for record in records
                    if int(record["order"]) == order
                }
            )
        )
        expected_count, expected_hash, width = EXPECTED_STREAMS[order]
        require(len(stream) == expected_count, f"order-{order} count drift")
        require(
            class_stream_hash(stream, width) == expected_hash,
            f"order-{order} stream drift",
        )
        require(
            all(locally_admissible(mask, order) for mask in stream),
            f"order-{order} inadmissible class",
        )
        streams[order] = stream
    return streams


def extend_to_order_eight(classes7: Sequence[int]) -> tuple[tuple[int, ...], int]:
    memory_status()
    pos7 = edge_positions(7)
    pos8 = edge_positions(8)
    classes8 = set()
    accepted_labeled = 0
    for index, mask7 in enumerate(classes7):
        base = 0
        for edge, old_position in pos7.items():
            if (mask7 >> old_position) & 1:
                base |= 1 << pos8[edge]
        for neighborhood in range(1 << 7):
            mask8 = base
            for vertex in range(7):
                if (neighborhood >> vertex) & 1:
                    mask8 |= 1 << pos8[(vertex, 7)]
            if not locally_admissible(mask8, 8):
                continue
            accepted_labeled += 1
            classes8.add(canonical_unrooted(mask8, 8))
        if index and index % 32 == 0:
            memory_status()
    result = tuple(sorted(classes8))
    expected_count, expected_hash, width = EXPECTED_STREAMS[8]
    require(len(result) == expected_count, "order-eight count mismatch")
    require(
        class_stream_hash(result, width) == expected_hash,
        "order-eight class stream mismatch",
    )
    memory_status()
    return result, accepted_labeled


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    chosen = tuple(vertex for vertex in range(order) if vertex != deleted)
    positions = edge_positions(order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1 :]:
            if (mask >> positions[(left, right)]) & 1:
                result |= 1 << target_position
            target_position += 1
    return result


def independent_deletion_rows(
    classes7: Sequence[int], classes8: Sequence[int]
) -> list[dict[str, object]]:
    translate = {
        canonical_unrooted(mask, 7): mask for mask in classes7
    }
    require(len(translate) == len(classes7), "order-seven class collision")
    rows: dict[int, dict[int, int]] = {mask: {} for mask in classes7}
    column_totals = {mask: 0 for mask in classes8}
    for mask8 in classes8:
        for deleted in range(8):
            canonical7 = canonical_unrooted(delete_vertex(mask8, 8, deleted), 7)
            require(canonical7 in translate, "deletion left class stream")
            mask7 = translate[canonical7]
            rows[mask7][mask8] = rows[mask7].get(mask8, 0) + 1
            column_totals[mask8] += 1
    require(set(column_totals.values()) == {8}, "deletion column sum mismatch")
    return [
        {
            "order7_mask": mask7,
            "left_multiplier": 99 - 7,
            "terms_order8_mask_multiplicity": [
                [mask8, multiplicity]
                for mask8, multiplicity in sorted(rows[mask7].items())
            ],
        }
        for mask7 in classes7
    ]


def induced_flag(
    mask: int,
    order: int,
    roots: tuple[int, int],
    free: tuple[int, int, int],
) -> int:
    chosen = roots + free
    positions = edge_positions(order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1 :]:
            if (mask >> positions[tuple(sorted((left, right)))]) & 1:
                result |= 1 << target_position
            target_position += 1
    return result


def root_embeddings(
    mask: int, order: int, root_edge: bool
) -> Iterable[tuple[int, int]]:
    rows = adjacency_rows(mask, order)
    for left in range(order):
        for right in range(order):
            if left == right:
                continue
            if bool((rows[left] >> right) & 1) == root_edge:
                yield left, right


def coefficient_matrix(
    mask: int,
    order: int,
    root_edge: bool,
    flags: Sequence[int],
) -> list[list[int]]:
    index = {flag: position for position, flag in enumerate(flags)}
    matrix = [[0] * len(flags) for _ in flags]
    vertices = set(range(order))
    for roots in root_embeddings(mask, order, root_edge):
        remaining = tuple(sorted(vertices.difference(roots)))
        remaining_set = set(remaining)
        triples = tuple(itertools.combinations(remaining, 3))
        flag_by_triple = {
            triple: index[canonical_flag(induced_flag(mask, order, roots, triple))]
            for triple in triples
        }
        for first in triples:
            first_set = set(first)
            for second in triples:
                if first_set.union(second) != remaining_set:
                    continue
                matrix[flag_by_triple[first]][flag_by_triple[second]] += 1
    require(
        matrix == [list(row) for row in zip(*matrix)],
        "coefficient matrix is not symmetric",
    )
    return matrix


def upper_entries(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [row, column, matrix[row][column]]
        for row in range(len(matrix))
        for column in range(row, len(matrix))
        if matrix[row][column]
    ]


def exact_rank(matrix: Sequence[Sequence[int]]) -> int:
    work = [
        [Fraction(value) for value in row]
        for row in matrix
        if any(row)
    ]
    if not work:
        return 0
    rank = 0
    columns = len(work[0])
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        for entry in range(column, columns):
            work[rank][entry] /= pivot_value
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            for entry in range(column, columns):
                work[row][entry] -= factor * work[rank][entry]
        rank += 1
        if rank == len(work):
            break
    return rank


def n3_and_prism_masks() -> tuple[int, int]:
    n3 = mask_from_edges(
        6,
        (
            (0, 1),
            (0, 2),
            (1, 2),
            (3, 4),
            (3, 5),
            (4, 5),
            (0, 3),
            (1, 4),
        ),
    )
    prism = n3 | mask_from_edges(6, ((2, 5),))
    require(locally_admissible(n3, 6), "N3 inadmissible")
    require(locally_admissible(prism, 6), "prism inadmissible")
    return n3, prism


def rook_mask() -> int:
    graph_edges = []
    for left in range(9):
        left_row, left_column = divmod(left, 3)
        for right in range(left + 1, 9):
            right_row, right_column = divmod(right, 3)
            if left_row == right_row or left_column == right_column:
                graph_edges.append((left, right))
    return mask_from_edges(9, graph_edges)


def induced_subgraph(mask: int, order: int, chosen: Sequence[int]) -> int:
    positions = edge_positions(order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1 :]:
            if (mask >> positions[(left, right)]) & 1:
                result |= 1 << target_position
            target_position += 1
    return result


def count_induced(mask: int, order: int, target: int, target_order: int) -> int:
    canonical_target = canonical_unrooted(target, target_order)
    return sum(
        canonical_unrooted(
            induced_subgraph(mask, order, chosen), target_order
        )
        == canonical_target
        for chosen in itertools.combinations(range(order), target_order)
    )


def direct_root_vectors(
    mask: int,
    order: int,
    root_edge: bool,
    flags: Sequence[int],
) -> list[list[int]]:
    index = {flag: position for position, flag in enumerate(flags)}
    vertices = set(range(order))
    vectors = []
    for roots in root_embeddings(mask, order, root_edge):
        counts = [0] * len(flags)
        remaining = tuple(sorted(vertices.difference(roots)))
        for free in itertools.combinations(remaining, 3):
            flag = canonical_flag(induced_flag(mask, order, roots, free))
            counts[index[flag]] += 1
        vectors.append(counts)
    return vectors


def artifact_audit(
    streams: dict[int, tuple[int, ...]],
    classes8: tuple[int, ...],
    flags_by_family: dict[str, tuple[int, ...]],
    deletion_rows: list[dict[str, object]],
) -> tuple[dict, dict]:
    raw_gzip = COEFFICIENT_GZIP.read_bytes()
    uncompressed = gzip.decompress(raw_gzip)
    payload = json.loads(uncompressed.decode("ascii"))
    require(canonical_bytes(payload) == uncompressed, "payload is not canonical JSON")
    stored = json.loads(STORED_RESULT.read_text(encoding="utf-8"))
    summary = stored["full_coefficient_payload"]
    require(sha256(COEFFICIENT_GZIP) == summary["gzip_sha256"], "gzip hash")
    require(len(raw_gzip) == summary["gzip_bytes"], "gzip length")
    require(hashlib.sha256(uncompressed).hexdigest() == summary["sha256"], "payload hash")
    require(
        len(uncompressed) == summary["canonical_uncompressed_bytes"],
        "payload length",
    )
    require(payload["format"] == "wave147-pair-root-order5-full-coefficients-v1", "format")
    require(
        payload["order7_to_order8_deletion_equations"] == deletion_rows,
        "full deletion artifact mismatch",
    )

    expected_keys = [
        (order, mask)
        for order in range(5, 9)
        for mask in (classes8 if order == 8 else streams[order])
    ]
    record_index = {}
    total_entries = 0
    family_records = {}
    for family, flags in flags_by_family.items():
        family_payload = payload["families"][family]
        require(family_payload["matrix_size"] == len(flags), "matrix size")
        records = family_payload["class_coefficients"]
        keys = [
            (int(record["order"]), int(record["canonical_mask"]))
            for record in records
        ]
        require(keys == expected_keys, f"{family} class record stream")
        for record in records:
            key = (
                family,
                int(record["order"]),
                int(record["canonical_mask"]),
            )
            require(key not in record_index, "duplicate class record")
            entries = record["upper_entries"]
            seen = set()
            for entry in entries:
                require(
                    isinstance(entry, list)
                    and len(entry) == 3
                    and all(type(value) is int for value in entry),
                    "malformed coefficient entry",
                )
                row, column, value = entry
                require(
                    0 <= row <= column < len(flags) and value > 0,
                    "invalid upper coefficient",
                )
                require((row, column) not in seen, "duplicate upper entry")
                seen.add((row, column))
            total_entries += len(entries)
            record_index[key] = record
        family_records[family] = len(records)
    require(family_records == {"ordered_edge": 1207, "ordered_nonedge": 1207}, "record counts")
    require(total_entries == 272054, "upper-entry count")
    require(summary["total_class_matrix_records"] == 2414, "stored record total")
    require(summary["total_nonzero_upper_entries"] == total_entries, "stored entry total")
    require(len(deletion_rows) == 208, "deletion row count")
    require(
        sum(len(row["terms_order8_mask_multiplicity"]) for row in deletion_rows)
        == 5333,
        "deletion term count",
    )
    return (
        {
            "canonical_uncompressed_bytes": len(uncompressed),
            "payload_sha256": hashlib.sha256(uncompressed).hexdigest(),
            "gzip_bytes": len(raw_gzip),
            "gzip_sha256": sha256(COEFFICIENT_GZIP),
            "class_matrix_records_per_family": family_records,
            "total_class_matrix_records": sum(family_records.values()),
            "total_nonzero_upper_entries": total_entries,
            "deletion_rows": len(deletion_rows),
            "deletion_nonzero_terms": sum(
                len(row["terms_order8_mask_multiplicity"])
                for row in deletion_rows
            ),
        },
        record_index,
    )


def coefficient_semantics(
    streams: dict[int, tuple[int, ...]],
    classes8: tuple[int, ...],
    flags_by_family: dict[str, tuple[int, ...]],
    record_index: dict,
) -> dict:
    selections = {
        order: tuple(
            dict.fromkeys(
                (
                    (classes8 if order == 8 else streams[order])[0],
                    (classes8 if order == 8 else streams[order])[
                        len(classes8 if order == 8 else streams[order]) // 2
                    ],
                    (classes8 if order == 8 else streams[order])[-1],
                )
            )
        )
        for order in range(5, 9)
    }
    representative_checks = []
    for family, root_edge in (
        ("ordered_edge", True),
        ("ordered_nonedge", False),
    ):
        flags = flags_by_family[family]
        for order, masks in selections.items():
            for mask in masks:
                actual = upper_entries(
                    coefficient_matrix(mask, order, root_edge, flags)
                )
                expected = record_index[(family, order, mask)]["upper_entries"]
                require(actual == expected, f"coefficient mismatch {family}/{order}/{mask}")
                representative_checks.append(
                    {
                        "family": family,
                        "order": order,
                        "canonical_mask": mask,
                        "upper_entry_count": len(actual),
                        "pass": True,
                    }
                )

    n3, prism = n3_and_prism_masks()
    wave45_by_independent_canonical = {
        canonical_unrooted(mask, 6): mask for mask in streams[6]
    }
    require(
        len(wave45_by_independent_canonical) == len(streams[6]),
        "order-six canonical translation collision",
    )
    n3_canonical = canonical_unrooted(n3, 6)
    prism_canonical = canonical_unrooted(prism, 6)
    require(
        n3_canonical in wave45_by_independent_canonical
        and prism_canonical in wave45_by_independent_canonical,
        "target class missing from order-six stream",
    )
    n3_key = wave45_by_independent_canonical[n3_canonical]
    prism_key = wave45_by_independent_canonical[prism_canonical]
    carriers = {}
    requested = {
        "ordered_edge": (185, 199),
        "ordered_nonedge": (186, 206),
    }
    for family, root_edge in (
        ("ordered_edge", True),
        ("ordered_nonedge", False),
    ):
        flags = flags_by_family[family]
        n3_matrix = coefficient_matrix(n3, 6, root_edge, flags)
        prism_matrix = coefficient_matrix(prism, 6, root_edge, flags)
        require(
            upper_entries(n3_matrix)
            == record_index[(family, 6, n3_key)]["upper_entries"],
            f"{family} N3 artifact mismatch",
        )
        require(
            upper_entries(prism_matrix)
            == record_index[(family, 6, prism_key)]["upper_entries"],
            f"{family} prism artifact mismatch",
        )
        row_mask, column_mask = requested[family]
        row = flags.index(row_mask)
        column = flags.index(column_mask)
        require(n3_matrix[row][column] == 4, f"{family} N3 carrier")
        require(prism_matrix[row][column] == 0, f"{family} prism carrier")
        carriers[family] = {
            "row": row,
            "column": column,
            "row_flag_mask": row_mask,
            "column_flag_mask": column_mask,
            "n3_coefficient": n3_matrix[row][column],
            "prism_coefficient": prism_matrix[row][column],
            "n3_sum_all_entries": sum(map(sum, n3_matrix)),
            "prism_sum_all_entries": sum(map(sum, prism_matrix)),
            "n3_rank_over_Q": exact_rank(n3_matrix),
            "prism_rank_over_Q": exact_rank(prism_matrix),
        }
    return {
        "representative_matrix_checks": representative_checks,
        "representative_matrix_check_count": len(representative_checks),
        "n3_independent_canonical_mask": n3_canonical,
        "n3_wave45_mask": n3_key,
        "prism_independent_canonical_mask": prism_canonical,
        "prism_wave45_mask": prism_key,
        "carriers": carriers,
    }


def rook_control(flags_by_family: dict[str, tuple[int, ...]]) -> dict:
    graph = rook_mask()
    rows = adjacency_rows(graph, 9)
    require(all(row.bit_count() == 4 for row in rows), "rook degree")
    for left in range(9):
        for right in range(left + 1, 9):
            common = (rows[left] & rows[right]).bit_count()
            require(
                common == (1 if (rows[left] >> right) & 1 else 2),
                "rook SRG common-neighbor count",
            )
    n3, prism = n3_and_prism_masks()
    controls = {}
    for family, root_edge in (
        ("ordered_edge", True),
        ("ordered_nonedge", False),
    ):
        vectors = direct_root_vectors(
            graph, 9, root_edge, flags_by_family[family]
        )
        require(len(vectors) == 36, "rook root count")
        require(all(sum(vector) == comb(7, 3) for vector in vectors), "rook triple count")
        require(all(vector == vectors[0] for vector in vectors), "rook root vectors differ")
        sum_all = sum(sum(vector) ** 2 for vector in vectors)
        trace = sum(
            sum(value * value for value in vector) for vector in vectors
        )
        require(sum_all == 44100 and trace == 2412, "rook moment totals")
        controls[family] = {
            "root_embeddings": len(vectors),
            "free_triples_per_root": comb(7, 3),
            "all_root_vectors_identical": True,
            "rank_over_Q": 1,
            "trace": trace,
            "sum_all_entries": sum_all,
            "psd_certificate": "sum of 36 explicit integer outer products",
        }
    return {
        "degree": 4,
        "lambda": 1,
        "mu": 2,
        "induced_n3_count": count_induced(graph, 9, n3, 6),
        "induced_triangular_prism_count": count_induced(
            graph, 9, prism, 6
        ),
        "direct_moments": controls,
    }


def build_results() -> dict:
    memory_status()
    manifest = verify_manifest()
    require(manifest["manifest_pass"] and manifest["entries_pass"], "manifest")
    stored = json.loads(STORED_RESULT.read_text(encoding="utf-8"))
    streams = frozen_class_streams()
    classes8, accepted_labeled = extend_to_order_eight(streams[7])
    require(
        list(classes8) == stored["class_streams"]["8"]["canonical_masks"],
        "stored order-eight list mismatch",
    )
    flags_by_family = {
        "ordered_edge": flag_basis(True),
        "ordered_nonedge": flag_basis(False),
    }
    require(
        flags_by_family["ordered_edge"]
        == tuple(stored["families"]["ordered_edge"]["flag_masks"]),
        "edge flag basis mismatch",
    )
    require(
        flags_by_family["ordered_nonedge"]
        == tuple(stored["families"]["ordered_nonedge"]["flag_masks"]),
        "nonedge flag basis mismatch",
    )
    deletion_rows = independent_deletion_rows(streams[7], classes8)
    artifact, record_index = artifact_audit(
        streams,
        classes8,
        flags_by_family,
        deletion_rows,
    )
    semantics = coefficient_semantics(
        streams,
        classes8,
        flags_by_family,
        record_index,
    )
    rook = rook_control(flags_by_family)
    require(
        (rook["induced_n3_count"], rook["induced_triangular_prism_count"])
        == (0, 6),
        "rook induced counts",
    )
    memory_status()
    return {
        "format": "wave147-independent-pair-root-order8-verification-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "flag bases, complete order-eight locally admissible class stream, "
            "artifact integrity/counts, full ordinary deletion layer, "
            "representative coefficient semantics, N3 carriers, and rook control"
        ),
        "sealed_discovery_package": manifest,
        "memory": {
            "free_physical_memory_floor_percent": MIN_FREE_MEMORY_PERCENT,
            "floor_checked_before_during_and_after": True,
        },
        "flag_bases": {
            "ordered_edge": {
                "count": len(flags_by_family["ordered_edge"]),
                "masks": list(flags_by_family["ordered_edge"]),
            },
            "ordered_nonedge": {
                "count": len(flags_by_family["ordered_nonedge"]),
                "masks": list(flags_by_family["ordered_nonedge"]),
            },
        },
        "class_streams": {
            str(order): {
                "count": len(classes8 if order == 8 else streams[order]),
                "sha256": class_stream_hash(
                    classes8 if order == 8 else streams[order],
                    EXPECTED_STREAMS[order][2],
                ),
            }
            for order in range(5, 9)
        }
        | {
            "order8_extension": {
                "seven_class_seeds": len(streams[7]),
                "neighborhoods_per_seed": 1 << 7,
                "locally_admissible_labeled_extensions": accepted_labeled,
                "unlabeled_classes": len(classes8),
                "stored_mask_list_exact_match": True,
            }
        },
        "artifact": artifact,
        "coefficient_semantics": semantics,
        "rook_positive_control": rook,
        "verdict": {
            "flag_bases": "PASS",
            "order8_class_stream": "PASS",
            "full_artifact_integrity_and_counts": "PASS",
            "ordinary_deletion_rows": "PASS",
            "representative_coefficient_semantics": "PASS",
            "n3_carrier_coefficient_4_prism_0": "PASS",
            "rook_positive_control": "PASS",
            "overall": "PASS_WITH_SCOPE",
        },
        "status_wall": {
            "strong_marked_vertex_pair_order8_rows": "NOT_BUILT",
            "numerical_SDP": "NOT_RUN",
            "rational_dual_certificate": "NOT_OBTAINED",
            "strict_n3_upper_bound": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "external_novelty": "UNKNOWN",
        },
    }


def main() -> None:
    payload = build_results()
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("Wave147 independent audit: PASS_WITH_SCOPE")


if __name__ == "__main__":
    main()
