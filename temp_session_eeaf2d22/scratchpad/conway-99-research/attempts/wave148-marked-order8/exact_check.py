#!/usr/bin/env python3
"""Exact marked degree/common-neighbor rows for the Wave147 order-eight lift."""

from __future__ import annotations

import argparse
import functools
import gzip
import hashlib
import importlib.util
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W147_CHECKER = ROOT / "attempts/wave147-alternative-lane/exact_check.py"
W147_RESULTS = ROOT / "attempts/wave147-alternative-lane/exact-results.json"
EXPECTED_W147_CHECKER_SHA256 = (
    "c49a6c5efb38afc0e33d395ebc1e1110f159132a118039170d4da56a728e6fb9"
)
EXPECTED_W147_RESULTS_SHA256 = (
    "8baea3d7fdf69ff6653ff859d30ea975dcbef44330445ace73ae051c7db1373c"
)
EXPECTED_ORDER7_SHA256 = (
    "6d4a9643e0377fabd32f2fad5fb284d48dee9612fc5910f96796ee2dd348f0b6"
)
EXPECTED_ORDER8_SHA256 = (
    "c2cf3604abc76a537eca21f1a8ef041697ca40d8ad41668d25eb412b9cd67337"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


require(
    sha256_file(W147_CHECKER) == EXPECTED_W147_CHECKER_SHA256,
    "Wave147 checker hash drift",
)
require(
    sha256_file(W147_RESULTS) == EXPECTED_W147_RESULTS_SHA256,
    "Wave147 result hash drift",
)
W147 = load_module("wave148_frozen_wave147", W147_CHECKER)


def class_stream_sha256(classes: Sequence[int], width: int) -> str:
    return hashlib.sha256(
        b"".join(mask.to_bytes(width, "big") for mask in classes)
    ).hexdigest()


def load_class_streams() -> tuple[tuple[int, ...], tuple[int, ...]]:
    classes7 = W147.classes_from_wave45()[7]
    payload = json.loads(W147_RESULTS.read_text(encoding="utf-8"))
    classes8 = tuple(
        int(mask) for mask in payload["class_streams"]["8"]["canonical_masks"]
    )
    require(len(classes7) == 208, "order-seven class count")
    require(len(classes8) == 916, "order-eight class count")
    require(
        class_stream_sha256(classes7, 3) == EXPECTED_ORDER7_SHA256,
        "order-seven class hash",
    )
    require(
        class_stream_sha256(classes8, 4) == EXPECTED_ORDER8_SHA256,
        "order-eight class hash",
    )
    require(
        all(W147.locally_admissible(mask, 7) for mask in classes7),
        "order-seven local admissibility",
    )
    require(
        all(W147.locally_admissible(mask, 8) for mask in classes8),
        "order-eight local admissibility",
    )
    return classes7, classes8


@functools.lru_cache(maxsize=None)
def canonical_rooted(mask: int, roots: tuple[int, ...], order: int = 7) -> int:
    """Canonicalize while fixing one or two roots pointwise."""
    require(len(roots) in (1, 2), "root count")
    require(len(set(roots)) == len(roots), "distinct roots")
    rows = W147.adjacency_rows(mask, order)
    free = tuple(vertex for vertex in range(order) if vertex not in roots)
    groups: dict[tuple[int, tuple[int, ...]], list[int]] = {}
    for vertex in free:
        signature = (
            rows[vertex].bit_count(),
            tuple((rows[vertex] >> root) & 1 for root in roots),
        )
        groups.setdefault(signature, []).append(vertex)

    target_start = len(roots)
    cell_maps = []
    for signature in sorted(groups):
        vertices = groups[signature]
        targets = tuple(range(target_start, target_start + len(vertices)))
        target_start += len(vertices)
        cell_maps.append(
            tuple(
                dict(zip(vertices, target_order))
                for target_order in itertools.permutations(targets)
            )
        )

    best: int | None = None
    for choices in itertools.product(*cell_maps):
        permutation = [0] * order
        for root_position, source_root in enumerate(roots):
            permutation[source_root] = root_position
        for mapping in choices:
            for source, target in mapping.items():
                permutation[source] = target
        transformed = W147.transform_mask(mask, order, permutation)
        if best is None or transformed < best:
            best = transformed
    require(best is not None, "empty rooted canonicalization")
    return best


def order7_type_definitions(
    classes7: Sequence[int],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    vertex_rows = []
    pair_rows = []
    for mask7 in classes7:
        rows = W147.adjacency_rows(mask7, 7)
        vertex_types = Counter(
            canonical_rooted(mask7, (vertex,)) for vertex in range(7)
        )
        for rooted_key, multiplicity in sorted(vertex_types.items()):
            rooted_rows = W147.adjacency_rows(rooted_key, 7)
            internal_degree = rooted_rows[0].bit_count()
            outside_count = 14 - internal_degree
            require(outside_count >= 0, "negative outside degree")
            vertex_rows.append(
                {
                    "order7_mask": mask7,
                    "rooted_key": rooted_key,
                    "orbit_multiplicity": multiplicity,
                    "internal_degree": internal_degree,
                    "outside_neighbor_count": outside_count,
                    "lhs_coefficient": multiplicity * outside_count,
                }
            )

        pair_types = Counter(
            canonical_rooted(mask7, (first, second))
            for first in range(7)
            for second in range(7)
            if first != second
        )
        for rooted_key, multiplicity in sorted(pair_types.items()):
            rooted_rows = W147.adjacency_rows(rooted_key, 7)
            adjacent = bool(rooted_rows[0] >> 1 & 1)
            common = (rooted_rows[0] & rooted_rows[1]).bit_count()
            target_common = 1 if adjacent else 2
            outside_count = target_common - common
            require(outside_count >= 0, "negative outside common count")
            pair_rows.append(
                {
                    "order7_mask": mask7,
                    "rooted_key": rooted_key,
                    "orbit_multiplicity": multiplicity,
                    "root_relation": "edge" if adjacent else "nonedge",
                    "internal_common_neighbors": common,
                    "target_common_neighbors": target_common,
                    "outside_common_neighbor_count": outside_count,
                    "lhs_coefficient": multiplicity * outside_count,
                }
            )

        require(sum(vertex_types.values()) == 7, "vertex orbit partition")
        require(sum(pair_types.values()) == 42, "pair orbit partition")
    return vertex_rows, pair_rows


def translate_order7_classes(classes7: Sequence[int]) -> dict[int, int]:
    translation = {
        W147.canonical_unrooted_by_degree(mask, 7): mask for mask in classes7
    }
    require(len(translation) == len(classes7), "order-seven translation collision")
    return translation


def increment(term_map: dict[int, int], mask8: int) -> None:
    term_map[mask8] = term_map.get(mask8, 0) + 1


def add_extension_terms(
    classes7: Sequence[int],
    classes8: Sequence[int],
    vertex_rows: list[dict[str, object]],
    pair_rows: list[dict[str, object]],
) -> dict[str, object]:
    vertex_index = {
        (int(row["order7_mask"]), int(row["rooted_key"])): position
        for position, row in enumerate(vertex_rows)
    }
    pair_index = {
        (int(row["order7_mask"]), int(row["rooted_key"])): position
        for position, row in enumerate(pair_rows)
    }
    require(len(vertex_index) == len(vertex_rows), "duplicate vertex row")
    require(len(pair_index) == len(pair_rows), "duplicate pair row")
    vertex_terms: list[dict[int, int]] = [{} for _ in vertex_rows]
    pair_terms: list[dict[int, int]] = [{} for _ in pair_rows]
    order7_translation = translate_order7_classes(classes7)

    vertex_rhs_total_by_k = {mask: 0 for mask in classes8}
    pair_rhs_total_by_k = {mask: 0 for mask in classes8}
    for class_index, mask8 in enumerate(classes8):
        rows8 = W147.adjacency_rows(mask8, 8)
        for deleted in range(8):
            survivors = tuple(vertex for vertex in range(8) if vertex != deleted)
            mask7 = W147.delete_vertex_mask(mask8, 8, deleted)
            degree_canonical7 = W147.canonical_unrooted_by_degree(mask7, 7)
            require(
                degree_canonical7 in order7_translation,
                "deleted graph outside order-seven stream",
            )
            class7 = order7_translation[degree_canonical7]
            deleted_neighbors = [
                new_index
                for new_index, original in enumerate(survivors)
                if rows8[deleted] >> original & 1
            ]
            for root in deleted_neighbors:
                rooted_key = canonical_rooted(mask7, (root,))
                row_index = vertex_index[(class7, rooted_key)]
                increment(vertex_terms[row_index], mask8)
                vertex_rhs_total_by_k[mask8] += 1
            for first in deleted_neighbors:
                for second in deleted_neighbors:
                    if first == second:
                        continue
                    rooted_key = canonical_rooted(mask7, (first, second))
                    row_index = pair_index[(class7, rooted_key)]
                    increment(pair_terms[row_index], mask8)
                    pair_rhs_total_by_k[mask8] += 1
        expected_vertex_total = sum(row.bit_count() for row in rows8)
        expected_pair_total = sum(
            row.bit_count() * (row.bit_count() - 1) for row in rows8
        )
        require(
            vertex_rhs_total_by_k[mask8] == expected_vertex_total,
            "vertex aggregate coefficient",
        )
        require(
            pair_rhs_total_by_k[mask8] == expected_pair_total,
            "pair aggregate coefficient",
        )
        if class_index % 64 == 0:
            W147.require_memory_floor()

    for row_index, row in enumerate(vertex_rows):
        row["row_id"] = f"V{row_index:04d}"
        row["terms_order8_mask_coefficient"] = [
            [mask, coefficient]
            for mask, coefficient in sorted(vertex_terms[row_index].items())
        ]
    for row_index, row in enumerate(pair_rows):
        row["row_id"] = f"P{row_index:04d}"
        row["terms_order8_mask_coefficient"] = [
            [mask, coefficient]
            for mask, coefficient in sorted(pair_terms[row_index].items())
        ]

    return {
        "vertex_rhs_total_by_order8": vertex_rhs_total_by_k,
        "pair_rhs_total_by_order8": pair_rhs_total_by_k,
    }


def edge_count(mask: int, order: int) -> int:
    return mask.bit_count()


def validate_left_aggregates(
    classes7: Sequence[int],
    vertex_rows: Sequence[dict[str, object]],
    pair_rows: Sequence[dict[str, object]],
) -> None:
    vertex_by_h: dict[int, int] = Counter()
    pair_by_h: dict[int, int] = Counter()
    for row in vertex_rows:
        vertex_by_h[int(row["order7_mask"])] += int(row["lhs_coefficient"])
    for row in pair_rows:
        pair_by_h[int(row["order7_mask"])] += int(row["lhs_coefficient"])

    for mask7 in classes7:
        rows7 = W147.adjacency_rows(mask7, 7)
        expected_vertex = 7 * 14 - 2 * edge_count(mask7, 7)
        expected_pair = 0
        for first in range(7):
            for second in range(7):
                if first == second:
                    continue
                target_common = 1 if rows7[first] >> second & 1 else 2
                internal_common = (rows7[first] & rows7[second]).bit_count()
                expected_pair += target_common - internal_common
        require(vertex_by_h[mask7] == expected_vertex, "vertex left aggregate")
        require(pair_by_h[mask7] == expected_pair, "pair left aggregate")


def row_summary(rows: Sequence[dict[str, object]]) -> dict[str, object]:
    term_counts = [len(row["terms_order8_mask_coefficient"]) for row in rows]
    coefficients = [
        coefficient
        for row in rows
        for _, coefficient in row["terms_order8_mask_coefficient"]
    ]
    return {
        "rows": len(rows),
        "zero_lhs_rows": sum(int(row["lhs_coefficient"]) == 0 for row in rows),
        "zero_rhs_rows": sum(not row["terms_order8_mask_coefficient"] for row in rows),
        "nonzero_terms": sum(term_counts),
        "minimum_terms_per_row": min(term_counts),
        "maximum_terms_per_row": max(term_counts),
        "maximum_term_coefficient": max(coefficients, default=0),
        "lhs_coefficient_sum": sum(int(row["lhs_coefficient"]) for row in rows),
    }


def build_artifacts() -> tuple[dict[str, object], bytes]:
    W147.require_memory_floor()
    classes7, classes8 = load_class_streams()
    vertex_rows, pair_rows = order7_type_definitions(classes7)
    aggregate_controls = add_extension_terms(
        classes7, classes8, vertex_rows, pair_rows
    )
    validate_left_aggregates(classes7, vertex_rows, pair_rows)
    payload = {
        "format": "wave148-marked-order8-rows-v1",
        "semantics": {
            "vertex": (
                "m_tau*(14-d_tau)*x_H7 = sum_K "
                "e_vertex(tau,K)*x_K8"
            ),
            "ordered_pair": (
                "m_tau*(lambda_or_mu-c_tau)*x_H7 = sum_K "
                "e_pair(tau,K)*x_K8"
            ),
            "automorphism_policy": (
                "roots are pointwise labelled and all embeddings are counted; "
                "no graph automorphism is assumed"
            ),
        },
        "class_streams": {
            "7": {"count": len(classes7), "sha256": EXPECTED_ORDER7_SHA256},
            "8": {"count": len(classes8), "sha256": EXPECTED_ORDER8_SHA256},
        },
        "vertex_rows": vertex_rows,
        "ordered_pair_rows": pair_rows,
    }
    payload_bytes = canonical_bytes(payload)
    payload_gzip = gzip.compress(payload_bytes, compresslevel=9, mtime=0)
    result = {
        "format": "wave148-marked-order8-summary-v1",
        "claim_label": "DERIVED",
        "scope": "hypothetical srg(99,14,1,2), no endpoint or automorphism",
        "source_hashes": {
            "wave147_checker": EXPECTED_W147_CHECKER_SHA256,
            "wave147_results": EXPECTED_W147_RESULTS_SHA256,
        },
        "class_streams": payload["class_streams"],
        "vertex_rows": row_summary(vertex_rows),
        "ordered_pair_rows": row_summary(pair_rows),
        "aggregate_controls": {
            "vertex_rhs_columns": len(
                aggregate_controls["vertex_rhs_total_by_order8"]
            ),
            "ordered_pair_rhs_columns": len(
                aggregate_controls["pair_rhs_total_by_order8"]
            ),
            "vertex_identity": "sum_w degree_K(w)=2|E(K)| for every K",
            "ordered_pair_identity": (
                "sum_w degree_K(w)*(degree_K(w)-1) for every K"
            ),
            "left_aggregates_checked": len(classes7),
        },
        "row_artifact": {
            "path": "marked-rows.json.gz",
            "canonical_sha256": hashlib.sha256(payload_bytes).hexdigest(),
            "gzip_sha256": hashlib.sha256(payload_gzip).hexdigest(),
            "canonical_bytes": len(payload_bytes),
            "gzip_bytes": len(payload_gzip),
        },
        "status": {
            "solver_run": "NOT_RUN",
            "numerical_feasibility": "UNKNOWN_NOT_RUN",
            "strict_n3_upper_bound": "UNKNOWN",
            "rational_dual_certificate": "NOT_OBTAINED",
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "Discovery work is not independent verification.",
            "These are necessary count rows, not sufficient graph realizability conditions.",
            "The combined Wave147/Wave148 SDP was not assembled or optimized.",
            "No bound, endpoint exclusion, construction, target resolution, or novelty claim follows.",
        ],
    }
    W147.require_memory_floor()
    return result, payload_gzip


def build_result() -> dict[str, object]:
    return build_artifacts()[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    result, row_gzip = build_artifacts()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        require(result == expected, "stored result mismatch")
        row_path = args.verify.with_name("marked-rows.json.gz")
        require(row_path.is_file(), "missing row artifact")
        require(row_path.read_bytes() == row_gzip, "row artifact mismatch")
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
    row_path = output.with_name("marked-rows.json.gz")
    row_path.write_bytes(row_gzip)
    print(
        json.dumps(
            {
                "status": "WROTE",
                "path": str(output),
                "row_path": str(row_path),
                "sha256": hashlib.sha256(canonical_bytes(result)).hexdigest(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
