#!/usr/bin/env python3
"""Exact coefficient audit for a pair-rooted order-five flag lift.

The target application is a putative srg(99,14,1,2).  A flag has two
ordered roots and three unordered free vertices.  Products of two such
flags have union order five through eight.  This checker constructs the
locally admissible flag bases and the exact order-six coefficient matrices
of the induced N3 graph and the triangular prism.

Only standard-library integer arithmetic is used.  This is a derivation
checker, not an SDP solver and not a graph nonexistence certificate.
"""

from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE45_COEFFICIENTS = (
    ROOT
    / "attempts"
    / "wave45-flag-moment"
    / "checkpoint-v1-moment-coefficients.json"
)
MIN_FREE_MEMORY_PERCENT = 15.0
EXPECTED_WAVE45_SHA256 = (
    "ffcf9f9942446d66c3559d97954217af3ba17c1978ea9417c6e99920d4a45420"
)
EXPECTED_ORDER7_CLASS_SHA256 = (
    "6d4a9643e0377fabd32f2fad5fb284d48dee9612fc5910f96796ee2dd348f0b6"
)
EXPECTED_CLASS_STREAMS = {
    5: (21, "f2717bd1bacb92b0a13010fa93e44b8a77d0958c2bf74a94cde323ace56a1e9e", 2),
    6: (62, "eb49cbaa20bfa2c6a64d56a0500a6ed1525727e9fa639d2b577b2862cb7a197a", 2),
    7: (208, EXPECTED_ORDER7_CLASS_SHA256, 3),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_memory_floor() -> None:
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
        f"free physical memory {free_percent:.2f}% below floor",
    )


def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    )


def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def adjacency_rows(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for position, (left, right) in enumerate(edges(order)):
        if mask >> position & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def mask_from_edges(
    order: int, graph_edges: Iterable[tuple[int, int]]
) -> int:
    positions = edge_positions(order)
    mask = 0
    for left, right in graph_edges:
        mask |= 1 << positions[tuple(sorted((left, right)))]
    return mask


def edge_list_from_mask(mask: int, order: int) -> list[list[int]]:
    return [
        [left, right]
        for position, (left, right) in enumerate(edges(order))
        if mask >> position & 1
    ]


def locally_admissible(mask: int, order: int) -> bool:
    """Necessary induced-subgraph conditions for lambda=1 and mu=2."""
    rows = adjacency_rows(mask, order)
    for left in range(order):
        if rows[left].bit_count() > 14:
            return False
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            adjacent = bool(rows[left] >> right & 1)
            if adjacent and common > 1:
                return False
            if not adjacent and common > 2:
                return False
    return True


def transform_mask(mask: int, order: int, permutation: Sequence[int]) -> int:
    """Relabel old vertex i as new vertex permutation[i]."""
    old_positions = edge_positions(order)
    new_positions = edge_positions(order)
    result = 0
    for old_edge, old_position in old_positions.items():
        if not (mask >> old_position & 1):
            continue
        new_edge = tuple(sorted((permutation[old_edge[0]], permutation[old_edge[1]])))
        result |= 1 << new_positions[new_edge]
    return result


def canonical_flag(mask: int) -> int:
    """Canonicalize an order-five flag while fixing ordered roots 0,1."""
    values = []
    for free_permutation in itertools.permutations((2, 3, 4)):
        permutation = (0, 1) + free_permutation
        values.append(transform_mask(mask, 5, permutation))
    return min(values)


def canonical_unrooted_by_degree(mask: int, order: int) -> int:
    """Canonicalize a small graph using the invariant degree partition.

    Every isomorphism preserves degree.  Put equal-degree vertices in fixed
    consecutive target positions and enumerate only permutations within
    degree cells.  This is a complete canonicalization, not a hash heuristic.
    """
    rows = adjacency_rows(mask, order)
    groups: dict[int, list[int]] = {}
    for vertex, row in enumerate(rows):
        groups.setdefault(row.bit_count(), []).append(vertex)

    target_start = 0
    cell_maps = []
    for degree in sorted(groups):
        vertices = groups[degree]
        targets = tuple(range(target_start, target_start + len(vertices)))
        target_start += len(vertices)
        cell_maps.append(
            tuple(dict(zip(vertices, target_order)) for target_order in itertools.permutations(targets))
        )

    best: int | None = None
    for choices in itertools.product(*cell_maps):
        permutation = [0] * order
        for mapping in choices:
            for source, target in mapping.items():
                permutation[source] = target
        transformed = transform_mask(mask, order, permutation)
        if best is None or transformed < best:
            best = transformed
    require(best is not None, "empty canonicalization")
    return best


def flag_universe(root_edge: bool) -> tuple[int, ...]:
    classes = set()
    for mask in range(1 << math.comb(5, 2)):
        if bool(mask & 1) != root_edge:
            continue
        if locally_admissible(mask, 5):
            classes.add(canonical_flag(mask))
    return tuple(sorted(classes))


def induced_flag_mask(
    mask: int,
    order: int,
    roots: tuple[int, int],
    free_vertices: tuple[int, int, int],
) -> int:
    chosen = roots + free_vertices
    source_positions = edge_positions(order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1 :]:
            if mask >> source_positions[tuple(sorted((left, right)))] & 1:
                result |= 1 << target_position
            target_position += 1
    return result


def root_embeddings(
    mask: int, order: int, root_edge: bool
) -> Iterable[tuple[int, int]]:
    rows = adjacency_rows(mask, order)
    for first in range(order):
        for second in range(order):
            if first == second:
                continue
            if bool(rows[first] >> second & 1) == root_edge:
                yield first, second


def coefficient_matrix_for_class(
    mask: int,
    order: int,
    root_edge: bool,
    flags: Sequence[int],
) -> list[list[int]]:
    """Return one unrooted-class coefficient in the raw pair-root moment."""
    require(5 <= order <= 8, "coefficient order outside five through eight")
    require(locally_admissible(mask, order), "graph not locally admissible")
    index = {flag: position for position, flag in enumerate(flags)}
    matrix = [[0] * len(flags) for _ in flags]
    vertices = set(range(order))
    for roots in root_embeddings(mask, order, root_edge):
        remaining = tuple(sorted(vertices.difference(roots)))
        require(3 <= len(remaining) <= 6, "bad root complement")
        remaining_set = set(remaining)
        free_triples = tuple(itertools.combinations(remaining, 3))
        flag_by_free = {
            free: index[
                canonical_flag(induced_flag_mask(mask, order, roots, free))
            ]
            for free in free_triples
        }
        for first_free in free_triples:
            first_set = set(first_free)
            for second_free in free_triples:
                if first_set.union(second_free) != remaining_set:
                    continue
                matrix[flag_by_free[first_free]][flag_by_free[second_free]] += 1
    require(matrix == [list(row) for row in zip(*matrix)], "matrix not symmetric")
    return matrix


def exact_rank(matrix: Sequence[Sequence[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [value / pivot_value for value in work[rank]]
        for row in range(rows):
            if row == rank or not work[row][column]:
                continue
            multiplier = work[row][column]
            work[row] = [
                value - multiplier * pivot_entry
                for value, pivot_entry in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def matrix_summary(
    matrix: Sequence[Sequence[int]], flags: Sequence[int]
) -> dict[str, object]:
    nonzero_upper = []
    diagonal_sum = 0
    for row in range(len(matrix)):
        diagonal_sum += matrix[row][row]
        for column in range(row, len(matrix)):
            value = matrix[row][column]
            if value:
                nonzero_upper.append(
                    {
                        "row": row,
                        "column": column,
                        "value": value,
                        "row_flag_mask": flags[row],
                        "column_flag_mask": flags[column],
                    }
                )
    return {
        "size": len(matrix),
        "rank_over_Q": exact_rank(matrix),
        "sum_all_entries": sum(sum(row) for row in matrix),
        "trace": diagonal_sum,
        "nonzero_upper_count": len(nonzero_upper),
        "nonzero_upper_entries": nonzero_upper,
    }


def direct_moment(
    graph_mask: int,
    order: int,
    root_edge: bool,
    flags: Sequence[int],
) -> list[list[int]]:
    """Direct finite Gram matrix on a concrete graph."""
    require(locally_admissible(graph_mask, order), "control graph inadmissible")
    index = {flag: position for position, flag in enumerate(flags)}
    matrix = [[0] * len(flags) for _ in flags]
    all_vertices = set(range(order))
    for roots in root_embeddings(graph_mask, order, root_edge):
        counts = [0] * len(flags)
        remaining = tuple(sorted(all_vertices.difference(roots)))
        for free in itertools.combinations(remaining, 3):
            flag = canonical_flag(
                induced_flag_mask(graph_mask, order, roots, free)
            )
            counts[index[flag]] += 1
        for row, left in enumerate(counts):
            if not left:
                continue
            for column, right in enumerate(counts):
                if right:
                    matrix[row][column] += left * right
    return matrix


def rook_3_by_3_mask() -> int:
    graph_edges = []
    for left in range(9):
        left_row, left_column = divmod(left, 3)
        for right in range(left + 1, 9):
            right_row, right_column = divmod(right, 3)
            if left_row == right_row or left_column == right_column:
                graph_edges.append((left, right))
    return mask_from_edges(9, graph_edges)


def count_induced_class(
    graph_mask: int, order: int, class_mask: int, class_order: int
) -> int:
    target = canonical_unrooted_by_degree(class_mask, class_order)
    source_positions = edge_positions(order)
    count = 0
    for chosen in itertools.combinations(range(order), class_order):
        induced = 0
        target_position = 0
        for left_index, left in enumerate(chosen):
            for right in chosen[left_index + 1 :]:
                if graph_mask >> source_positions[(left, right)] & 1:
                    induced |= 1 << target_position
                target_position += 1
        if canonical_unrooted_by_degree(induced, class_order) == target:
            count += 1
    return count


def separating_entries(
    first: Sequence[Sequence[int]],
    second: Sequence[Sequence[int]],
    flags: Sequence[int],
) -> list[dict[str, int]]:
    records = []
    for row in range(len(first)):
        for column in range(row, len(first)):
            if first[row][column] and not second[row][column]:
                records.append(
                    {
                        "row": row,
                        "column": column,
                        "n3_coefficient": first[row][column],
                        "row_flag_mask": flags[row],
                        "column_flag_mask": flags[column],
                    }
                )
    return records


def class_stream_sha256(classes: Sequence[int], width: int) -> str:
    return hashlib.sha256(
        b"".join(mask.to_bytes(width, "big") for mask in classes)
    ).hexdigest()


def classes_from_wave45() -> dict[int, tuple[int, ...]]:
    require(WAVE45_COEFFICIENTS.is_file(), "missing frozen Wave45 coefficients")
    digest = hashlib.sha256(WAVE45_COEFFICIENTS.read_bytes()).hexdigest()
    require(digest == EXPECTED_WAVE45_SHA256, "Wave45 coefficient hash drift")
    payload = json.loads(WAVE45_COEFFICIENTS.read_text(encoding="utf-8"))
    result = {}
    for order, (expected_count, expected_hash, width) in EXPECTED_CLASS_STREAMS.items():
        classes = tuple(
            sorted(
                {
                    int(record["canonical_mask"])
                    for record in payload["families"]["vertex"]["class_coefficients"]
                    if int(record["order"]) == order
                }
            )
        )
        require(len(classes) == expected_count, f"order-{order} class count drift")
        require(
            class_stream_sha256(classes, width) == expected_hash,
            f"order-{order} class stream hash drift",
        )
        require(
            all(locally_admissible(mask, order) for mask in classes),
            f"bad order-{order} class",
        )
        result[order] = classes
    return result


def enumerate_order_eight_classes(classes7: Sequence[int]) -> tuple[int, ...]:
    """Complete locally admissible order-eight stream by vertex extension."""
    require_memory_floor()
    positions7 = edge_positions(7)
    positions8 = edge_positions(8)
    classes8 = set()
    for class_index, mask7 in enumerate(classes7):
        base = 0
        for edge, position7 in positions7.items():
            if mask7 >> position7 & 1:
                base |= 1 << positions8[edge]
        for neighborhood in range(1 << 7):
            mask8 = base
            for vertex in range(7):
                if neighborhood >> vertex & 1:
                    mask8 |= 1 << positions8[(vertex, 7)]
            if locally_admissible(mask8, 8):
                classes8.add(canonical_unrooted_by_degree(mask8, 8))
        if class_index % 32 == 0:
            require_memory_floor()
    result = tuple(sorted(classes8))
    require(len(result) == 916, "order-eight class count drift")
    require(all(locally_admissible(mask, 8) for mask in result), "bad order-eight class")
    require_memory_floor()
    return result


def delete_vertex_mask(mask: int, order: int, deleted: int) -> int:
    chosen = tuple(vertex for vertex in range(order) if vertex != deleted)
    source_positions = edge_positions(order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1 :]:
            if mask >> source_positions[(left, right)] & 1:
                result |= 1 << target_position
            target_position += 1
    return result


def deletion_extension_equations(
    classes7: Sequence[int], classes8: Sequence[int]
) -> list[dict[str, object]]:
    """Build 92*x_H7 = sum_K d(H,K)*x_K for every order-seven H."""
    degree_canonical_to_wave45 = {
        canonical_unrooted_by_degree(mask, 7): mask for mask in classes7
    }
    require(
        len(degree_canonical_to_wave45) == len(classes7),
        "order-seven canonical translation collision",
    )
    terms_by_class7: dict[int, dict[int, int]] = {
        mask: {} for mask in classes7
    }
    for mask8 in classes8:
        total_deletions = 0
        for deleted in range(8):
            degree_canonical7 = canonical_unrooted_by_degree(
                delete_vertex_mask(mask8, 8, deleted), 7
            )
            require(
                degree_canonical7 in degree_canonical_to_wave45,
                "order-eight deletion left class stream",
            )
            mask7 = degree_canonical_to_wave45[degree_canonical7]
            terms = terms_by_class7[mask7]
            terms[mask8] = terms.get(mask8, 0) + 1
            total_deletions += 1
        require(total_deletions == 8, "order-eight deletion multiplicity")

    equations = []
    column_totals = {mask: 0 for mask in classes8}
    for mask7 in classes7:
        terms = [
            [mask8, multiplicity]
            for mask8, multiplicity in sorted(terms_by_class7[mask7].items())
        ]
        for mask8, multiplicity in terms:
            column_totals[mask8] += multiplicity
        equations.append(
            {
                "order7_mask": mask7,
                "left_multiplier": 92,
                "terms_order8_mask_multiplicity": terms,
            }
        )
    require(set(column_totals.values()) == {8}, "deletion column sums")
    return equations


def upper_entries(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [row, column, matrix[row][column]]
        for row in range(len(matrix))
        for column in range(row, len(matrix))
        if matrix[row][column]
    ]


def build_artifacts() -> tuple[dict[str, object], bytes]:
    classes_by_order = classes_from_wave45()
    classes8 = enumerate_order_eight_classes(classes_by_order[7])
    classes_by_order[8] = classes8
    deletion_equations = deletion_extension_equations(
        classes_by_order[7], classes8
    )
    # N3: two disjoint triangles with exactly two independent cross edges.
    n3_mask = mask_from_edges(
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
    prism_mask = n3_mask | mask_from_edges(6, ((2, 5),))
    require(locally_admissible(n3_mask, 6), "N3 local admissibility")
    require(locally_admissible(prism_mask, 6), "prism local admissibility")

    families = {}
    all_coefficients = {}
    for name, root_edge in (("ordered_edge", True), ("ordered_nonedge", False)):
        flags = flag_universe(root_edge)
        n3_matrix = coefficient_matrix_for_class(
            n3_mask, 6, root_edge, flags
        )
        prism_matrix = coefficient_matrix_for_class(
            prism_mask, 6, root_edge, flags
        )
        expected_n3_total = (
            (16 if root_edge else 14) * 12
        )  # ordered roots times ordered omitted-vertex pairs
        expected_prism_total = (
            (18 if root_edge else 12) * 12
        )
        require(
            sum(sum(row) for row in n3_matrix) == expected_n3_total,
            f"{name} N3 embedding total",
        )
        require(
            sum(sum(row) for row in prism_matrix) == expected_prism_total,
            f"{name} prism embedding total",
        )
        separated = separating_entries(n3_matrix, prism_matrix, flags)
        require(separated, f"{name} has no N3-versus-prism separating entry")
        selected = dict(separated[0])
        selected["row_flag_edges"] = edge_list_from_mask(
            selected["row_flag_mask"], 5
        )
        selected["column_flag_edges"] = edge_list_from_mask(
            selected["column_flag_mask"], 5
        )
        selected["prism_coefficient"] = 0
        selected["interpretation"] = (
            f"the raw ({selected['row']},{selected['column']}) moment entry "
            f"receives {selected['n3_coefficient']}*n3 from induced N3 "
            "copies and zero from triangular prisms, in addition to "
            "coefficients of other order-six and order-five-to-eight classes"
        )
        families[name] = {
            "root_relation": "edge" if root_edge else "nonedge",
            "flag_order": 5,
            "root_count": 2,
            "free_count": 3,
            "flag_count": len(flags),
            "flag_masks": list(flags),
            "union_orders": [5, 6, 7, 8],
            "n3_order_six_coefficient": matrix_summary(n3_matrix, flags),
            "prism_order_six_coefficient": matrix_summary(prism_matrix, flags),
            "n3_positive_prism_zero_entries": separated,
            "selected_n3_carrier": selected,
        }
        class_records = []
        for order in range(5, 9):
            for class_mask in classes_by_order[order]:
                matrix = coefficient_matrix_for_class(
                    class_mask, order, root_edge, flags
                )
                class_records.append(
                    {
                        "order": order,
                        "canonical_mask": class_mask,
                        "upper_entries": upper_entries(matrix),
                    }
                )
        all_coefficients[name] = {
            "matrix_size": len(flags),
            "class_coefficients": class_records,
        }

    rook_mask = rook_3_by_3_mask()
    require(
        all(row.bit_count() == 4 for row in adjacency_rows(rook_mask, 9)),
        "rook control degree",
    )
    rook_n3 = count_induced_class(rook_mask, 9, n3_mask, 6)
    rook_prisms = count_induced_class(rook_mask, 9, prism_mask, 6)
    require((rook_n3, rook_prisms) == (0, 6), "rook six-class counts")
    rook_controls = {}
    for name, root_edge in (("ordered_edge", True), ("ordered_nonedge", False)):
        flags = tuple(families[name]["flag_masks"])
        matrix = direct_moment(rook_mask, 9, root_edge, flags)
        expected_roots = 36
        expected_sum = expected_roots * math.comb(7, 3) ** 2
        require(sum(sum(row) for row in matrix) == expected_sum, "rook moment total")
        rook_controls[name] = {
            "matrix_size": len(matrix),
            "rank_over_Q": exact_rank(matrix),
            "trace": sum(matrix[index][index] for index in range(len(matrix))),
            "sum_all_entries": sum(sum(row) for row in matrix),
            "root_embeddings": expected_roots,
            "free_triples_per_root": math.comb(7, 3),
            "psd_certificate": "explicit sum of 36 integer outer products",
        }

    coefficient_payload = {
        "format": "wave147-pair-root-order5-full-coefficients-v1",
        "families": all_coefficients,
        "order7_to_order8_deletion_equations": deletion_equations,
    }
    coefficient_payload_sha256 = hashlib.sha256(
        canonical_bytes(coefficient_payload)
    ).hexdigest()
    coefficient_payload_bytes = canonical_bytes(coefficient_payload)
    coefficient_payload_gzip = gzip.compress(
        coefficient_payload_bytes, compresslevel=9, mtime=0
    )

    result = {
        "format": "wave147-pair-root-order5-coefficients-v1",
        "claim_label": "DERIVED",
        "target": "srg(99,14,1,2)",
        "model": (
            "For each ordered edge or ordered nonedge root theta, count "
            "locally admissible induced flags on the roots plus three "
            "unordered free vertices. Sum c(theta)c(theta)^T over roots."
        ),
        "moment_expansion": (
            "M_sigma=sum_{h=5}^8 sum_{H in H_h} x_H C_H^sigma, "
            "where every C_H^sigma is an explicit integer embedding matrix."
        ),
        "target_coefficient": (
            "The induced N3 count n3 multiplies the displayed order-six "
            "matrix C_N3^sigma. The triangular-prism count P multiplies the "
            "separate C_prism^sigma matrix."
        ),
        "class_streams": {
            "5": {
                "count": len(classes_by_order[5]),
                "sha256": class_stream_sha256(classes_by_order[5], 2),
                "source": "frozen Wave45 exact coefficient package",
            },
            "6": {
                "count": len(classes_by_order[6]),
                "sha256": class_stream_sha256(classes_by_order[6], 2),
                "source": "frozen Wave45 exact coefficient package",
            },
            "7": {
                "count": len(classes_by_order[7]),
                "sha256": class_stream_sha256(classes_by_order[7], 3),
                "source": "frozen Wave45 exact coefficient package",
            },
            "8": {
                "count": len(classes8),
                "sha256": class_stream_sha256(classes8, 4),
                "canonical_masks": list(classes8),
                "construction": (
                    "extend every one of the 208 admissible order-seven "
                    "classes by every neighborhood of a new vertex, filter "
                    "lambda/mu local caps, and canonically quotient by all "
                    "degree-preserving permutations"
                ),
            },
        },
        "full_coefficient_payload": {
            "sha256": coefficient_payload_sha256,
            "artifact": "coefficients.json.gz",
            "canonical_uncompressed_bytes": len(coefficient_payload_bytes),
            "gzip_bytes": len(coefficient_payload_gzip),
            "gzip_sha256": hashlib.sha256(coefficient_payload_gzip).hexdigest(),
            "class_matrix_records_per_family": sum(
                len(classes_by_order[order]) for order in range(5, 9)
            ),
            "total_class_matrix_records": 2
            * sum(len(classes_by_order[order]) for order in range(5, 9)),
            "total_nonzero_upper_entries": sum(
                len(record["upper_entries"])
                for family in all_coefficients.values()
                for record in family["class_coefficients"]
            ),
            "deletion_equations": {
                "rows": len(deletion_equations),
                "left_multiplier": 92,
                "nonzero_terms": sum(
                    len(row["terms_order8_mask_multiplicity"])
                    for row in deletion_equations
                ),
                "identity": (
                    "92*x_H7=sum_K d(H7,K8)*x_K8 for each of the 208 "
                    "order-seven classes"
                ),
            },
        },
        "families": families,
        "positive_control": {
            "graph": "3 by 3 rook graph, srg(9,4,1,2)",
            "induced_n3_count": rook_n3,
            "induced_triangular_prism_count": rook_prisms,
            "direct_moments": rook_controls,
        },
        "status": {
            "strict_n3_upper_bound": "UNKNOWN",
            "numerical_sdp_run": "NOT_RUN",
            "rational_certificate_extraction": (
                "POSSIBLE_IN_PRINCIPLE: a dual solution can be rationalized "
                "to exact PSD Gram blocks plus exact linear count identities; "
                "no such dual certificate is produced here."
            ),
        },
        "limitations": [
            "This package computes the complete class streams, coefficient matrices, and ordinary order-seven-to-eight deletion equations, but not the stronger degree/common-neighbor extension rows or an SDP optimum.",
            "Local admissibility is necessary but not sufficient for extension to the 99-vertex target.",
            "A negative numerical SDP status would not be evidence without an exact rational dual certificate.",
            "No graph, strict upper bound, endpoint exclusion, or novelty claim is made.",
        ],
    }
    return result, coefficient_payload_gzip


def build_result() -> dict[str, object]:
    return build_artifacts()[0]


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    result, coefficient_payload_gzip = build_artifacts()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        require(result == expected, "stored result mismatch")
        coefficient_path = args.verify.with_name("coefficients.json.gz")
        require(coefficient_path.is_file(), "missing compressed coefficient artifact")
        require(
            coefficient_path.read_bytes() == coefficient_payload_gzip,
            "compressed coefficient artifact mismatch",
        )
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "sha256": hashlib.sha256(canonical_bytes(result)).hexdigest(),
                },
                sort_keys=True,
            )
        )
        return

    output = args.output or HERE / "exact-results.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    coefficient_output = output.with_name("coefficients.json.gz")
    coefficient_output.write_bytes(coefficient_payload_gzip)
    print(
        json.dumps(
            {
                "status": "WROTE",
                "path": str(output),
                "coefficient_path": str(coefficient_output),
                "sha256": hashlib.sha256(canonical_bytes(result)).hexdigest(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
