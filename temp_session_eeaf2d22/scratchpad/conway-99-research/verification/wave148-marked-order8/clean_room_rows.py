"""Clean-room derivation of marked order-eight extension-row invariants.

This module reads only published Wave147 artifacts.  It does not inspect,
import, or execute any Wave148 discovery artifact.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE147_GZIP = (
    ROOT / "attempts" / "wave147-alternative-lane" / "coefficients.json.gz"
)
WAVE147_RESULT = (
    ROOT / "attempts" / "wave147-alternative-lane" / "exact-results.json"
)
OUTPUT = HERE / "expected-invariants.json"

EXPECTED_GZIP_SHA256 = (
    "a46d8a8b6fd3ae339cdf7c9b633a661d917e3481bed762ae6aa70f1b4886cf1e"
)
EXPECTED_PAYLOAD_SHA256 = (
    "a7402e77048090ea492c435190aadc1d32bd1df99276e612f6d199aec9e14b08"
)
EXPECTED_ORDER8_SHA256 = (
    "c2cf3604abc76a537eca21f1a8ef041697ca40d8ad41668d25eb412b9cd67337"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def transform_mask(mask: int, order: int, permutation: Sequence[int]) -> int:
    positions = edge_positions(order)
    result = 0
    for position, (left, right) in enumerate(edges(order)):
        if not ((mask >> position) & 1):
            continue
        image = tuple(sorted((permutation[left], permutation[right])))
        result |= 1 << positions[image]
    return result


@lru_cache(maxsize=None)
def canonical_unrooted(mask: int, order: int) -> int:
    rows = adjacency_rows(mask, order)
    groups: dict[int, list[int]] = {}
    for vertex, row in enumerate(rows):
        groups.setdefault(row.bit_count(), []).append(vertex)
    start = 0
    cell_choices = []
    for degree in sorted(groups):
        sources = groups[degree]
        targets = tuple(range(start, start + len(sources)))
        start += len(sources)
        cell_choices.append(
            tuple(
                tuple(zip(sources, image))
                for image in itertools.permutations(targets)
            )
        )
    best = None
    for selected in itertools.product(*cell_choices):
        permutation = [0] * order
        for cell in selected:
            for source, target in cell:
                permutation[source] = target
        candidate = transform_mask(mask, order, permutation)
        if best is None or candidate < best:
            best = candidate
    require(best is not None, "empty unrooted canonicalization")
    return best


@lru_cache(maxsize=None)
def canonical_rooted(
    mask: int, order: int, roots: tuple[int, ...]
) -> int:
    """Canonicalize while sending ordered roots pointwise to 0,1,..."""
    require(len(set(roots)) == len(roots), "duplicate roots")
    rows = adjacency_rows(mask, order)
    root_set = set(roots)
    groups: dict[tuple[int, ...], list[int]] = {}
    for vertex in range(order):
        if vertex in root_set:
            continue
        signature = (
            rows[vertex].bit_count(),
            *(int(bool((rows[vertex] >> root) & 1)) for root in roots),
        )
        groups.setdefault(signature, []).append(vertex)

    start = len(roots)
    cell_choices = []
    for signature in sorted(groups):
        sources = groups[signature]
        targets = tuple(range(start, start + len(sources)))
        start += len(sources)
        cell_choices.append(
            tuple(
                tuple(zip(sources, image))
                for image in itertools.permutations(targets)
            )
        )
    best = None
    for selected in itertools.product(*cell_choices):
        permutation = [0] * order
        for target, root in enumerate(roots):
            permutation[root] = target
        for cell in selected:
            for source, target in cell:
                permutation[source] = target
        candidate = transform_mask(mask, order, permutation)
        if best is None or candidate < best:
            best = candidate
    require(best is not None, "empty rooted canonicalization")
    return best


def delete_vertex(
    mask: int, order: int, deleted: int
) -> tuple[int, dict[int, int]]:
    chosen = [vertex for vertex in range(order) if vertex != deleted]
    relabel = {old: new for new, old in enumerate(chosen)}
    positions = edge_positions(order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1 :]:
            if (mask >> positions[(left, right)]) & 1:
                result |= 1 << target_position
            target_position += 1
    return result, relabel


def published_streams() -> tuple[tuple[int, ...], tuple[int, ...], dict]:
    gzip_bytes = WAVE147_GZIP.read_bytes()
    require(sha256_bytes(gzip_bytes) == EXPECTED_GZIP_SHA256, "Wave147 gzip drift")
    payload_bytes = gzip.decompress(gzip_bytes)
    require(
        sha256_bytes(payload_bytes) == EXPECTED_PAYLOAD_SHA256,
        "Wave147 payload drift",
    )
    payload = json.loads(payload_bytes.decode("ascii"))
    classes7 = tuple(
        int(row["order7_mask"])
        for row in payload["order7_to_order8_deletion_equations"]
    )
    stored = json.loads(WAVE147_RESULT.read_text(encoding="utf-8"))
    classes8 = tuple(
        int(mask) for mask in stored["class_streams"]["8"]["canonical_masks"]
    )
    require(len(classes7) == 208 and len(classes8) == 916, "class count drift")
    require(
        sha256_bytes(b"".join(mask.to_bytes(4, "big") for mask in classes8))
        == EXPECTED_ORDER8_SHA256,
        "order-eight stream drift",
    )
    return classes7, classes8, payload


def rooted_type_tables(classes7: Sequence[int]) -> tuple[dict, dict]:
    vertex_types = {}
    pair_types = {}
    for source_mask in classes7:
        rows = adjacency_rows(source_mask, 7)
        local_vertex = {}
        local_pair = {}
        for vertex in range(7):
            key = canonical_rooted(source_mask, 7, (vertex,))
            local_vertex[key] = local_vertex.get(key, 0) + 1
        for left in range(7):
            for right in range(7):
                if left == right:
                    continue
                key = canonical_rooted(source_mask, 7, (left, right))
                local_pair[key] = local_pair.get(key, 0) + 1
        require(sum(local_vertex.values()) == 7, "vertex multiplicity")
        require(sum(local_pair.values()) == 42, "pair multiplicity")

        for key, multiplicity in local_vertex.items():
            canonical_rows = adjacency_rows(key, 7)
            record = {
                "source_mask": source_mask,
                "multiplicity": multiplicity,
                "degree": canonical_rows[0].bit_count(),
            }
            require(key not in vertex_types, "vertex type collision")
            vertex_types[key] = record
        for key, multiplicity in local_pair.items():
            canonical_rows = adjacency_rows(key, 7)
            adjacent = bool(canonical_rows[0] & (1 << 1))
            common_inside = (
                canonical_rows[0] & canonical_rows[1]
            ).bit_count()
            record = {
                "source_mask": source_mask,
                "multiplicity": multiplicity,
                "adjacent": adjacent,
                "common_inside": common_inside,
            }
            require(key not in pair_types, "pair type collision")
            pair_types[key] = record
    return vertex_types, pair_types


def coefficient_rows(
    classes8: Sequence[int],
    vertex_types: dict,
    pair_types: dict,
) -> tuple[dict, dict, dict]:
    vertex_coefficients = {key: {} for key in vertex_types}
    pair_coefficients = {key: {} for key in pair_types}
    column_checks = {}
    for mask8 in classes8:
        rows8 = adjacency_rows(mask8, 8)
        vertex_total = 0
        pair_total = 0
        for deleted in range(8):
            mask7, relabel = delete_vertex(mask8, 8, deleted)
            neighbors = [
                vertex
                for vertex in range(8)
                if vertex != deleted and ((rows8[deleted] >> vertex) & 1)
            ]
            for vertex in neighbors:
                key = canonical_rooted(mask7, 7, (relabel[vertex],))
                require(key in vertex_coefficients, "unknown vertex type")
                row = vertex_coefficients[key]
                row[mask8] = row.get(mask8, 0) + 1
                vertex_total += 1
            for left in neighbors:
                for right in neighbors:
                    if left == right:
                        continue
                    key = canonical_rooted(
                        mask7, 7, (relabel[left], relabel[right])
                    )
                    require(key in pair_coefficients, "unknown pair type")
                    row = pair_coefficients[key]
                    row[mask8] = row.get(mask8, 0) + 1
                    pair_total += 1
        edge_count = mask8.bit_count()
        expected_pair = sum(
            row.bit_count() * (row.bit_count() - 1) for row in rows8
        )
        require(vertex_total == 2 * edge_count, "vertex column identity")
        require(pair_total == expected_pair, "pair column identity")
        column_checks[mask8] = {
            "vertex_total": vertex_total,
            "expected_vertex_total": 2 * edge_count,
            "pair_total": pair_total,
            "expected_pair_total": expected_pair,
        }
    return vertex_coefficients, pair_coefficients, column_checks


def row_residual(record: dict, k: int, lam: int, mu: int) -> int:
    if "degree" in record:
        return k - int(record["degree"])
    target = lam if record["adjacent"] else mu
    return target - int(record["common_inside"])


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


def rook_mask() -> int:
    graph_edges = []
    for left in range(9):
        left_row, left_column = divmod(left, 3)
        for right in range(left + 1, 9):
            right_row, right_column = divmod(right, 3)
            if left_row == right_row or left_column == right_column:
                graph_edges.append((left, right))
    return mask_from_edges(9, graph_edges)


def induced_counts(
    graph: int,
    graph_order: int,
    subset_order: int,
    translation: dict[int, int],
) -> dict[int, int]:
    counts = {}
    for chosen in itertools.combinations(range(graph_order), subset_order):
        mask = induced_subgraph(graph, graph_order, chosen)
        canonical = canonical_unrooted(mask, subset_order)
        require(canonical in translation, "control left class stream")
        stored = translation[canonical]
        counts[stored] = counts.get(stored, 0) + 1
    return counts


def evaluate_rows(
    types: dict,
    coefficients: dict,
    counts7: dict[int, int],
    counts8: dict[int, int],
    k: int,
    lam: int,
    mu: int,
) -> tuple[list[dict], int]:
    failures = []
    zero_residual_rows = 0
    for key, record in types.items():
        residual = row_residual(record, k, lam, mu)
        source_count = counts7.get(int(record["source_mask"]), 0)
        if source_count:
            require(residual >= 0, "negative residual on a realized control type")
        left = (
            residual
            * int(record["multiplicity"])
            * source_count
        )
        right = sum(
            coefficient * counts8.get(mask8, 0)
            for mask8, coefficient in coefficients[key].items()
        )
        if residual == 0 and source_count:
            zero_residual_rows += 1
        if left != right:
            failures.append(
                {
                    "rooted_key": key,
                    "left": left,
                    "right": right,
                    "residual": residual,
                }
            )
    return failures, zero_residual_rows


def micro_controls(
    classes7: Sequence[int],
    classes8: Sequence[int],
    vertex_types: dict,
    pair_types: dict,
    vertex_coefficients: dict,
    pair_coefficients: dict,
) -> dict:
    by7 = {canonical_unrooted(mask, 7): mask for mask in classes7}
    by8 = {canonical_unrooted(mask, 8): mask for mask in classes8}
    require(len(by7) == len(classes7) and len(by8) == len(classes8), "translation")

    empty7 = by7[canonical_unrooted(0, 7)]
    one_edge7_raw = mask_from_edges(7, ((0, 1),))
    one_edge7 = by7[canonical_unrooted(one_edge7_raw, 7)]
    one_edge8_raw = mask_from_edges(8, ((0, 1),))
    path8_raw = mask_from_edges(8, ((0, 1), (0, 2)))
    triangle8_raw = mask_from_edges(8, ((0, 1), (0, 2), (1, 2)))
    one_edge8 = by8[canonical_unrooted(one_edge8_raw, 8)]
    path8 = by8[canonical_unrooted(path8_raw, 8)]
    triangle8 = by8[canonical_unrooted(triangle8_raw, 8)]

    vertex_empty_key = canonical_rooted(0, 7, (0,))
    pair_empty_key = canonical_rooted(0, 7, (0, 1))
    pair_edge_key = canonical_rooted(one_edge7_raw, 7, (0, 1))
    require(vertex_types[vertex_empty_key]["source_mask"] == empty7, "empty vertex source")
    require(pair_types[pair_empty_key]["source_mask"] == empty7, "empty pair source")
    require(pair_types[pair_edge_key]["source_mask"] == one_edge7, "edge pair source")
    controls = {
        "degree_empty7_to_one_edge8": {
            "source_mask7": empty7,
            "target_mask8": one_edge8,
            "coefficient": vertex_coefficients[vertex_empty_key].get(one_edge8, 0),
            "expected": 2,
        },
        "nonedge_CN_empty7_to_path8": {
            "source_mask7": empty7,
            "target_mask8": path8,
            "coefficient": pair_coefficients[pair_empty_key].get(path8, 0),
            "expected": 2,
        },
        "edge_CN_one_edge7_to_triangle8": {
            "source_mask7": one_edge7,
            "target_mask8": triangle8,
            "coefficient": pair_coefficients[pair_edge_key].get(triangle8, 0),
            "expected": 6,
        },
    }
    require(
        all(row["coefficient"] == row["expected"] for row in controls.values()),
        "micro coefficient control",
    )
    return controls


def build_expected_invariants() -> dict:
    classes7, classes8, _ = published_streams()
    vertex_types, pair_types = rooted_type_tables(classes7)
    vertex_coefficients, pair_coefficients, column_checks = coefficient_rows(
        classes8, vertex_types, pair_types
    )
    target_vertex_residuals = [
        row_residual(record, 14, 1, 2) for record in vertex_types.values()
    ]
    target_pair_residuals = [
        row_residual(record, 14, 1, 2) for record in pair_types.values()
    ]
    require(min(target_vertex_residuals) >= 0, "target vertex residual")
    require(min(target_pair_residuals) >= 0, "target pair residual")
    require(
        all(
            residual or not pair_coefficients[key]
            for (key, record), residual in zip(
                pair_types.items(), target_pair_residuals
            )
        ),
        "zero target residual has a positive coefficient",
    )

    translate7 = {canonical_unrooted(mask, 7): mask for mask in classes7}
    translate8 = {canonical_unrooted(mask, 8): mask for mask in classes8}
    rook = rook_mask()
    rook_rows = adjacency_rows(rook, 9)
    require(all(row.bit_count() == 4 for row in rook_rows), "rook degree")
    for left in range(9):
        for right in range(left + 1, 9):
            expected = 1 if (rook_rows[left] >> right) & 1 else 2
            require(
                (rook_rows[left] & rook_rows[right]).bit_count() == expected,
                "rook common-neighbor parameter",
            )
    counts7 = induced_counts(rook, 9, 7, translate7)
    counts8 = induced_counts(rook, 9, 8, translate8)
    vertex_failures, vertex_zero = evaluate_rows(
        vertex_types,
        vertex_coefficients,
        counts7,
        counts8,
        4,
        1,
        2,
    )
    pair_failures, pair_zero = evaluate_rows(
        pair_types,
        pair_coefficients,
        counts7,
        counts8,
        4,
        1,
        2,
    )
    require(not vertex_failures and not pair_failures, "rook row replay")
    controls = micro_controls(
        classes7,
        classes8,
        vertex_types,
        pair_types,
        vertex_coefficients,
        pair_coefficients,
    )
    return {
        "format": "wave148-clean-room-marked-order8-expected-invariants-v1",
        "claim_label": "DERIVED_PROTOCOL_NOT_DISCOVERY_VERIFICATION",
        "scope": (
            "first-principles meanings and expected invariants for marked "
            "degree/common-neighbor order-seven-to-eight rows"
        ),
        "inputs": {
            "wave147_coefficient_gzip_sha256": EXPECTED_GZIP_SHA256,
            "wave147_payload_sha256": EXPECTED_PAYLOAD_SHA256,
            "wave147_order8_stream_sha256": EXPECTED_ORDER8_SHA256,
        },
        "conventions": {
            "vertex_roots": 1,
            "pair_roots": 2,
            "pair_ordered": True,
            "marks_fixed_pointwise": True,
            "automorphism_division": False,
            "target_parameters": [99, 14, 1, 2],
        },
        "dimensions": {
            "order7_classes": len(classes7),
            "order8_classes": len(classes8),
            "vertex_rooted_types": len(vertex_types),
            "ordered_pair_rooted_types": len(pair_types),
            "active_target_pair_rows": sum(
                residual > 0 for residual in target_pair_residuals
            ),
            "zero_target_pair_rows": sum(
                residual == 0 for residual in target_pair_residuals
            ),
            "vertex_coefficient_nonzero_terms": sum(
                len(row) for row in vertex_coefficients.values()
            ),
            "pair_coefficient_nonzero_terms": sum(
                len(row) for row in pair_coefficients.values()
            ),
            "vertex_source_multiplicity_total": sum(
                int(record["multiplicity"])
                for record in vertex_types.values()
            ),
            "pair_source_multiplicity_total": sum(
                int(record["multiplicity"])
                for record in pair_types.values()
            ),
        },
        "target_residual_ranges": {
            "vertex_min": min(target_vertex_residuals),
            "vertex_max": max(target_vertex_residuals),
            "pair_min": min(target_pair_residuals),
            "pair_max": max(target_pair_residuals),
            "zero_pair_rows_have_zero_coefficient_support": True,
        },
        "column_identities": {
            "classes_checked": len(column_checks),
            "vertex_identity": "sum_tau a(tau,K)=2*edges(K)",
            "pair_identity": (
                "sum_tau b(tau,K)=sum_x deg_K(x)*(deg_K(x)-1)"
            ),
            "all_pass": True,
        },
        "micro_controls": controls,
        "rook_positive_control": {
            "parameters": [9, 4, 1, 2],
            "order7_subset_total": sum(counts7.values()),
            "order8_subset_total": sum(counts8.values()),
            "order7_nonzero_classes": len(counts7),
            "order8_nonzero_classes": len(counts8),
            "vertex_row_failures": vertex_failures,
            "pair_row_failures": pair_failures,
            "vertex_zero_residual_rows": vertex_zero,
            "pair_zero_residual_rows": pair_zero,
            "all_marked_rows_pass": True,
        },
        "status": {
            "clean_room_protocol": "FROZEN",
            "wave148_manifest": "NOT_RECEIVED",
            "wave148_artifacts_verified": False,
            "strict_n3_upper_bound": "UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
    }


def main() -> None:
    payload = build_expected_invariants()
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload["dimensions"], sort_keys=True))


if __name__ == "__main__":
    main()
