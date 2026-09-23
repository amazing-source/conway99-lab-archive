"""Build the compact exact certificate for the Wave 17 n3=54 F/R census.

The connected cases are rejected by complete enumeration of a GF(2) parity
kernel.  The two K3,3-plus-order-12 cases are rejected by a direct candidate
count.  Official catalog bytes are fetched and validated in memory only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave17_n3_54_census", HERE / "census.py"
)
assert SPEC is not None and SPEC.loader is not None
CENSUS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CENSUS)


def parity_rows(
    candidates: tuple[tuple[int, int, tuple[tuple[int, int], ...]], ...]
) -> tuple[int, ...]:
    rows = []
    for point in range(27):
        rows.append(
            sum(
                1 << index
                for index, (left, right, _) in enumerate(candidates)
                if point in (left, right)
            )
        )
    for label_pair in itertools.combinations(range(18), 2):
        rows.append(
            sum(
                1 << index
                for index, (_, _, rectangle) in enumerate(candidates)
                if label_pair in rectangle
            )
        )
    return tuple(rows)


def rref_and_nullspace(
    rows: Iterable[int], variable_count: int
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    work = [value for value in rows if value]
    rank = 0
    pivots: list[int] = []
    for column in range(variable_count):
        pivot = next(
            (
                index
                for index in range(rank, len(work))
                if work[index] >> column & 1
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for index in range(len(work)):
            if index != rank and work[index] >> column & 1:
                work[index] ^= work[rank]
        pivots.append(column)
        rank += 1
        if rank == len(work):
            break
    reduced = tuple(work[:rank])
    pivot_set = set(pivots)
    free = [column for column in range(variable_count) if column not in pivot_set]
    basis = []
    for free_column in free:
        vector = 1 << free_column
        for row, pivot_column in zip(reduced, pivots):
            if row >> free_column & 1:
                vector |= 1 << pivot_column
        basis.append(vector)
    return reduced, tuple(pivots), tuple(basis)


def packed_hash(values: Iterable[int], variable_count: int) -> str:
    width = max(1, (variable_count + 7) // 8)
    digest = hashlib.sha256()
    digest.update(variable_count.to_bytes(2, "big"))
    for value in values:
        digest.update(value.to_bytes(width, "little"))
    return digest.hexdigest()


def point_incidence_masks(
    candidates: tuple[tuple[int, int, tuple[tuple[int, int], ...]], ...]
) -> tuple[int, ...]:
    return tuple(
        sum(
            1 << index
            for index, (left, right, _) in enumerate(candidates)
            if point in (left, right)
        )
        for point in range(27)
    )


def kernel_point_degree_census(
    basis: tuple[int, ...], point_masks: tuple[int, ...]
) -> dict[str, int]:
    vector_count = 1 << len(basis)
    point_degree_two = 0
    current = 0
    previous_gray = 0
    for index in range(vector_count):
        gray = index ^ (index >> 1)
        if index:
            changed = gray ^ previous_gray
            current ^= basis[changed.bit_length() - 1]
        previous_gray = gray
        if all((current & mask).bit_count() == 2 for mask in point_masks):
            point_degree_two += 1
    return {
        "kernel_vectors_examined": vector_count,
        "point_degree_two_vectors": point_degree_two,
    }


def connected_certificate(case: dict[str, object]) -> dict[str, object]:
    f_edges = case["F_edges"]
    points = tuple(sorted(f_edges))
    candidates = CENSUS.compatible_supports(
        points, CENSUS.mandatory_k(18, f_edges)
    )
    rows = parity_rows(candidates)
    reduced, pivots, basis = rref_and_nullspace(rows, len(candidates))
    census = kernel_point_degree_census(
        basis, point_incidence_masks(candidates)
    )
    if census["point_degree_two_vectors"] != 0:
        raise AssertionError("connected case has an unrejected parity vector")
    return {
        "case_id": case["case_id"],
        "catalog_index": case["catalog_index"],
        "record_sha256": case["record_sha256"],
        "compatible_support_count": len(candidates),
        "parity_row_count": len(rows),
        "parity_matrix_sha256": packed_hash(rows, len(candidates)),
        "parity_rank": len(pivots),
        "parity_nullity": len(basis),
        "rref_sha256": packed_hash(reduced, len(candidates)),
        "nullspace_basis_sha256": packed_hash(basis, len(candidates)),
        **census,
        "rejection": (
            "TRIVIAL_PARITY_KERNEL"
            if not basis
            else "EXHAUSTED_PARITY_KERNEL_NO_POINT_DEGREE_TWO_VECTOR"
        ),
    }


def mixed_certificate(case: dict[str, object]) -> dict[str, object]:
    f_edges = case["F_edges"]
    points = tuple(sorted(f_edges))
    candidates = CENSUS.compatible_supports(
        points, CENSUS.mandatory_k(18, f_edges)
    )
    first = set(range(9))
    second = set(range(9, 27))
    within_first = sum(
        left in first and right in first for left, right, _ in candidates
    )
    cross = sum(
        (left in first and right in second)
        or (right in first and left in second)
        for left, right, _ in candidates
    )
    within_second = sum(
        left in second and right in second for left, right, _ in candidates
    )
    required_cross = 9 * 2
    required_internal_second = (18 * 2 - required_cross) // 2
    if within_first != 0 or cross != 9 * 18:
        raise AssertionError("mixed-component compatibility count changed")
    if within_second >= required_internal_second:
        raise AssertionError("mixed-component count no longer rejects")
    return {
        "case_id": case["case_id"],
        "catalog_index": case["catalog_index"],
        "record_sha256": case["record_sha256"],
        "compatible_support_count": len(candidates),
        "K3,3_point_count": 9,
        "order12_point_count": 18,
        "within_K3,3_candidates": within_first,
        "cross_component_candidates": cross,
        "within_order12_candidates": within_second,
        "forced_cross_R_edges": required_cross,
        "forced_internal_order12_R_edges": required_internal_second,
        "rejection": "TOO_FEW_INTERNAL_ORDER12_CANDIDATES",
    }


def build_certificate() -> dict[str, object]:
    cases, catalog_metadata = CENSUS.build_cases()
    connected = [
        connected_certificate(case)
        for case in cases
        if case["F_component_count"] == 1
    ]
    mixed = [
        mixed_certificate(case)
        for case in cases
        if case["F_component_count"] == 2
    ]
    nullity_histogram = {}
    for row in connected:
        key = str(row["parity_nullity"])
        nullity_histogram[key] = nullity_histogram.get(key, 0) + 1
    connected_rejections = {}
    for row in connected:
        key = row["rejection"]
        connected_rejections[key] = connected_rejections.get(key, 0) + 1
    return {
        "schema_version": 1,
        "scope": (
            "complete fixed-F exact-coverage obstruction for the frozen "
            "Wave17 n3=54 structural residual"
        ),
        "catalogs": catalog_metadata,
        "catalog_redistributed": False,
        "case_count": len(cases),
        "connected_case_count": len(connected),
        "mixed_component_case_count": len(mixed),
        "certificate_method": {
            "connected": (
                "GF(2) point-degree and rectangle-coverage parity kernel, "
                "followed by exhaustive kernel enumeration"
            ),
            "mixed": (
                "direct compatible-support count forced by 2-regularity"
            ),
        },
        "summary": {
            "parity_nullity_histogram": dict(
                sorted(nullity_histogram.items(), key=lambda item: int(item[0]))
            ),
            "connected_rejections": dict(sorted(connected_rejections.items())),
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
