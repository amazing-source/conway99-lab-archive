#!/usr/bin/env python3
"""Test the Wave150 endpoint pseudowitness with four-root order-eight moments.

This is a discovery script, not an independent verifier.  Four root vertices
are fixed pointwise and a flag adds an unordered pair of free vertices.  A
product of two such flags has union order 6, 7, or 8, so the resulting
centered covariance constraints use only the exact counts already present in
the Wave150 endpoint witness.
"""

from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WAVE147 = ROOT / "attempts/wave147-alternative-lane/exact_check.py"
WAVE150_MODEL = ROOT / "attempts/wave150-order8-sdp-scout/endpoint_sdp.py"
WITNESS = ROOT / "attempts/wave150-order8-sdp-scout/exact-rank1-witness.json"
OUTPUT = HERE / "four-root-scout.json"

N = 99
ROOT_MASKS = (0, 1, 3, 7, 11, 12, 13, 15, 30)
COUNT_SCALE = 4
MIN_FREE_MEMORY_PERCENT = 15.0


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_phys", ctypes.c_ulonglong),
        ("avail_phys", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("avail_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("avail_virtual", ctypes.c_ulonglong),
        ("avail_extended_virtual", ctypes.c_ulonglong),
    ]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def memory_record(label: str) -> dict[str, float | str]:
    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    require(bool(ok), "GlobalMemoryStatusEx failed")
    free_percent = 100.0 * status.avail_phys / status.total_phys
    require(
        free_percent >= MIN_FREE_MEMORY_PERCENT,
        f"free physical memory {free_percent:.2f}% is below the 15% floor",
    )
    return {
        "label": label,
        "free_physical_memory_percent": free_percent,
        "available_physical_gib": status.avail_phys / 2**30,
        "total_physical_gib": status.total_phys / 2**30,
    }


def induced_mask(
    graph_mask: int,
    graph_order: int,
    chosen_vertices: Sequence[int],
    edge_positions: Any,
) -> int:
    source_positions = edge_positions(graph_order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen_vertices):
        for right in chosen_vertices[left_index + 1 :]:
            if graph_mask >> source_positions[tuple(sorted((left, right)))] & 1:
                result |= 1 << target_position
            target_position += 1
    return result


def embed_root_mask(root_mask: int, edge_positions: Any) -> int:
    source = edge_positions(4)
    target = edge_positions(6)
    result = 0
    for edge, position in source.items():
        if root_mask >> position & 1:
            result |= 1 << target[edge]
    return result


def canonical_four_root_flag(mask: int, transform_mask: Any) -> int:
    swapped = transform_mask(mask, 6, (0, 1, 2, 3, 5, 4))
    return min(mask, swapped)


def flag_universe(
    root_mask: int,
    edge_positions: Any,
    locally_admissible: Any,
    transform_mask: Any,
) -> tuple[int, ...]:
    base = embed_root_mask(root_mask, edge_positions)
    root_edges = set(edge_positions(4))
    extension_positions = [
        position
        for edge, position in edge_positions(6).items()
        if edge not in root_edges
    ]
    require(len(extension_positions) == 9, "four-root extension width changed")
    flags: set[int] = set()
    for extension in range(1 << len(extension_positions)):
        mask = base
        for bit, position in enumerate(extension_positions):
            if extension >> bit & 1:
                mask |= 1 << position
        if locally_admissible(mask, 6):
            flags.add(canonical_four_root_flag(mask, transform_mask))
    return tuple(sorted(flags))


def automorphism_size(root_mask: int, transform_mask: Any) -> int:
    return sum(
        transform_mask(root_mask, 4, permutation) == root_mask
        for permutation in itertools.permutations(range(4))
    )


def parse_count(value: str | int) -> Fraction:
    return Fraction(str(value))


def count_maps(
    inputs: dict[str, Any], witness: dict[str, Any]
) -> dict[int, dict[int, Fraction]]:
    maps: dict[int, dict[int, Fraction]] = {
        4: {
            int(mask): Fraction(int(count))
            for mask, count in inputs["lower_counts"][4].items()
        },
        6: {
            int(mask): Fraction(int(count))
            for mask, count in inputs["lower_counts"][6].items()
        },
        7: {int(mask): Fraction(0) for mask in inputs["classes"][7]},
        8: {int(mask): Fraction(0) for mask in inputs["classes8"]},
    }
    for record in witness["x7_support"]:
        count_maps_entry = parse_count(record["count"])
        require(count_maps_entry.denominator == 1, "nonintegral order-seven count")
        maps[7][int(record["canonical_mask"])] = count_maps_entry
    for record in witness["x8_support"]:
        count_maps_entry = parse_count(record["count"])
        require(
            COUNT_SCALE % count_maps_entry.denominator == 0,
            "order-eight denominator escaped scale",
        )
        maps[8][int(record["canonical_mask"])] = count_maps_entry
    return maps


def class_for_root(
    root_mask: int, classes4: Iterable[int], canonical_unrooted: Any
) -> int:
    target = canonical_unrooted(root_mask, 4)
    matches = [
        int(mask)
        for mask in classes4
        if canonical_unrooted(int(mask), 4) == target
    ]
    require(len(matches) == 1, f"root class lookup failed for mask {root_mask}")
    return matches[0]


def covering_pair_indices(complement_size: int) -> tuple[tuple[int, int], ...]:
    pairs = tuple(itertools.combinations(range(complement_size), 2))
    return tuple(
        (left, right)
        for left, first in enumerate(pairs)
        for right, second in enumerate(pairs)
        if len(set(first).union(second)) == complement_size
    )


def add_weighted_moments(
    graph_mask: int,
    graph_order: int,
    weight_scaled: int,
    root_mask_to_index: dict[int, int],
    flag_indices: Sequence[dict[int, int]],
    moments_scaled: Sequence[list[list[int]]],
    first_moments: Sequence[list[int]],
    functions: dict[str, Any],
) -> tuple[int, int]:
    vertices = tuple(range(graph_order))
    complement_size = graph_order - 4
    pair_indices = covering_pair_indices(complement_size)
    edge_positions = functions["edge_positions"]
    canonical_flag = functions["canonical_flag"]
    matched_embeddings = 0
    emitted_products = 0
    for roots in itertools.permutations(vertices, 4):
        induced_root = induced_mask(
            graph_mask, graph_order, roots, edge_positions
        )
        root_index = root_mask_to_index.get(induced_root)
        if root_index is None:
            continue
        matched_embeddings += 1
        complement = tuple(vertex for vertex in vertices if vertex not in roots)
        free_pairs = tuple(itertools.combinations(complement, 2))
        flag_by_pair = [
            flag_indices[root_index][
                canonical_flag(
                    induced_mask(
                        graph_mask,
                        graph_order,
                        roots + free_pair,
                        edge_positions,
                    )
                )
            ]
            for free_pair in free_pairs
        ]
        if graph_order == 6:
            require(len(flag_by_pair) == 1, "bad order-six complement")
            first_moments[root_index][flag_by_pair[0]] += weight_scaled
        matrix = moments_scaled[root_index]
        for left, right in pair_indices:
            matrix[flag_by_pair[left]][flag_by_pair[right]] += weight_scaled
            emitted_products += 1
    return matched_embeddings, emitted_products


def exact_two_coordinate_certificate(
    matrix: Sequence[Sequence[int]],
) -> dict[str, Any] | None:
    for index, diagonal in enumerate(matrix):
        if diagonal[index] < 0:
            return {
                "kind": "negative_diagonal",
                "indices": [index],
                "vector": [1],
                "quadratic_value_scaled": str(diagonal[index]),
            }
    for left in range(len(matrix)):
        a = matrix[left][left]
        if a <= 0:
            continue
        for right in range(left + 1, len(matrix)):
            b = matrix[left][right]
            c = matrix[right][right]
            determinant = a * c - b * b
            if determinant < 0:
                # v=(b,-a) gives v^T[[a,b],[b,c]]v = a(ac-b^2).
                value = a * determinant
                require(value < 0, "bad two-coordinate certificate")
                divisor = math.gcd(abs(b), abs(a))
                vector = [b // divisor, -a // divisor]
                reduced_value = value // (divisor * divisor)
                return {
                    "kind": "negative_2x2_principal_minor",
                    "indices": [left, right],
                    "vector": [str(entry) for entry in vector],
                    "principal_entries_scaled": [
                        str(a),
                        str(b),
                        str(c),
                    ],
                    "determinant_scaled_squared": str(determinant),
                    "quadratic_value_scaled": str(reduced_value),
                }
    return None


def exact_eigenvector_certificate(
    matrix: Sequence[Sequence[int]], eigenvector: np.ndarray
) -> dict[str, Any]:
    integer_vector = np.rint(eigenvector * 1_000_000).astype(np.int64)
    require(np.count_nonzero(integer_vector), "rounded eigenvector vanished")

    def quadratic(vector: np.ndarray) -> int:
        support = np.flatnonzero(vector)
        value = 0
        for left in support:
            value += int(vector[left]) * int(vector[left]) * matrix[left][left]
            for right in support:
                if right <= left:
                    continue
                value += (
                    2
                    * int(vector[left])
                    * int(vector[right])
                    * matrix[left][right]
                )
        return value

    value = quadratic(integer_vector)
    require(value < 0, "numeric eigenvector did not yield exact negativity")
    # Greedily sparsify while preserving a strict exact negative value.
    for index in np.argsort(np.abs(integer_vector)):
        if not integer_vector[index]:
            continue
        old = integer_vector[index]
        integer_vector[index] = 0
        candidate = quadratic(integer_vector)
        if candidate < 0:
            value = candidate
        else:
            integer_vector[index] = old
    support = np.flatnonzero(integer_vector)
    divisor = 0
    for index in support:
        divisor = math.gcd(divisor, abs(int(integer_vector[index])))
    integer_vector //= divisor
    value = quadratic(integer_vector)
    require(value < 0, "reduced eigenvector lost negativity")
    return {
        "kind": "integer_vector",
        "indices": [int(index) for index in support],
        "vector": [str(int(integer_vector[index])) for index in support],
        "quadratic_value_scaled": str(value),
    }


def main() -> int:
    start = time.time()
    memory = [memory_record("start")]
    wave147 = load_module("wave152_wave147_frozen", WAVE147)
    wave150 = load_module("wave152_wave150_frozen", WAVE150_MODEL)
    inputs = wave150.load_inputs(False)
    witness = json.loads(WITNESS.read_text(encoding="utf-8"))
    require(
        witness["conclusion"]["finite_relaxation"] == "EXACT_RATIONAL_FEASIBLE",
        "unexpected Wave150 witness status",
    )
    counts = count_maps(inputs, witness)

    flags = [
        flag_universe(
            root_mask,
            wave147.edge_positions,
            wave147.locally_admissible,
            wave147.transform_mask,
        )
        for root_mask in ROOT_MASKS
    ]
    flag_indices = [
        {flag: index for index, flag in enumerate(family)}
        for family in flags
    ]
    root_mask_to_index = {
        root_mask: index for index, root_mask in enumerate(ROOT_MASKS)
    }
    moments_scaled = [
        [[0] * len(family) for _ in family]
        for family in flags
    ]
    first_moments_scaled = [[0] * len(family) for family in flags]

    enumeration: dict[str, dict[str, int]] = {}
    functions = {
        "edge_positions": wave147.edge_positions,
        "canonical_flag": lambda mask: canonical_four_root_flag(
            mask, wave147.transform_mask
        ),
    }
    for order in (6, 7, 8):
        matched = 0
        products = 0
        nonzero_classes = 0
        for class_index, class_mask in enumerate(counts[order]):
            weight = counts[order][class_mask]
            if not weight:
                continue
            nonzero_classes += 1
            weight_scaled = weight * COUNT_SCALE
            require(weight_scaled.denominator == 1, "scaled count is not integral")
            local_matched, local_products = add_weighted_moments(
                class_mask,
                order,
                int(weight_scaled),
                root_mask_to_index,
                flag_indices,
                moments_scaled,
                first_moments_scaled,
                functions,
            )
            matched += local_matched
            products += local_products
            if class_index % 64 == 0:
                memory.append(memory_record(f"order_{order}_class_{class_index}"))
        enumeration[str(order)] = {
            "nonzero_classes": nonzero_classes,
            "matched_root_embeddings_unweighted": matched,
            "emitted_products_unweighted": products,
        }
        memory.append(memory_record(f"order_{order}_complete"))

    root_results = []
    all_exact_psd = True
    any_exact_separation = False
    free_pairs_full = math.comb(N - 4, 2)
    classes4 = tuple(int(mask) for mask in inputs["classes"][4])
    for root_index, root_mask in enumerate(ROOT_MASKS):
        root_class = class_for_root(
            root_mask, classes4, wave147.canonical_unrooted_by_degree
        )
        aut = automorphism_size(root_mask, wave147.transform_mask)
        root_count = aut * int(counts[4][root_class])
        s_scaled = first_moments_scaled[root_index]
        matrix_scaled = moments_scaled[root_index]
        require(
            sum(s_scaled) == COUNT_SCALE * root_count * free_pairs_full,
            f"first-moment total failed for root {root_mask}",
        )
        require(
            sum(map(sum, matrix_scaled))
            == COUNT_SCALE * root_count * free_pairs_full * free_pairs_full,
            f"second-moment total failed for root {root_mask}",
        )
        # B = 4*(R*M-s*s^T).  matrix_scaled=4*M and s_scaled=4*s.
        # Thus B = R*matrix_scaled - (s_scaled*s_scaled)/4.
        centered_scaled = [
            [
                root_count * matrix_scaled[row][column]
                - s_scaled[row] * s_scaled[column] // COUNT_SCALE
                for column in range(len(flags[root_index]))
            ]
            for row in range(len(flags[root_index]))
        ]
        require(
            all(
                s_scaled[row] * s_scaled[column] % COUNT_SCALE == 0
                for row in range(len(flags[root_index]))
                for column in range(len(flags[root_index]))
            ),
            "centered scaling lost integrality",
        )
        require(
            centered_scaled
            == [list(row) for row in zip(*centered_scaled)],
            "centered matrix is not symmetric",
        )
        scale = max(abs(entry) for row in centered_scaled for entry in row)
        numeric = np.asarray(centered_scaled, dtype=np.float64)
        if scale:
            numeric /= float(scale)
        eigenvalues, eigenvectors = np.linalg.eigh(numeric)
        minimum = float(eigenvalues[0])
        certificate = exact_two_coordinate_certificate(centered_scaled)
        if certificate is None and minimum < -1e-9:
            certificate = exact_eigenvector_certificate(
                centered_scaled, eigenvectors[:, 0]
            )
        exact_status = (
            "NOT_PSD" if certificate is not None else "NUMERICALLY_NO_SEPARATION"
        )
        if certificate is not None:
            any_exact_separation = True
            all_exact_psd = False
            certificate["flag_masks"] = [
                flags[root_index][index] for index in certificate["indices"]
            ]
        else:
            # Absence of a found negative vector is not an exact PSD proof.
            all_exact_psd = False
        root_results.append(
            {
                "root_mask": root_mask,
                "root_edges": wave147.edge_list_from_mask(root_mask, 4),
                "root_class_mask": root_class,
                "automorphism_size": aut,
                "root_embedding_count": root_count,
                "flag_count": len(flags[root_index]),
                "flag_masks": list(flags[root_index]),
                "first_moment_total": str(sum(s_scaled) // COUNT_SCALE),
                "second_moment_total": str(
                    sum(map(sum, matrix_scaled)) // COUNT_SCALE
                ),
                "centered_scale": "4*(R*M-s*s^T)",
                "maximum_absolute_scaled_entry": str(scale),
                "minimum_numeric_eigenvalue_after_max_entry_scaling": minimum,
                "exact_status": exact_status,
                "negative_certificate": certificate,
            }
        )

    memory.append(memory_record("complete"))
    payload = {
        "format": "wave152-four-root-order8-scout-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Four pointwise-labeled roots plus two-free-vertex flags, tested "
            "against the exact Wave150 n3=4158 count pseudowitness."
        ),
        "conclusion": {
            "Conway_99": "UNKNOWN",
            "endpoint_n3_4158": "UNKNOWN",
            "wave150_pseudowitness": (
                "EXACTLY_SEPARATED_BY_FOUR_ROOT_COVARIANCE"
                if any_exact_separation
                else "NO_EXACT_SEPARATION_FOUND"
            ),
            "all_blocks_exactly_psd": all_exact_psd,
        },
        "method": {
            "root_order": 4,
            "flag_order": 6,
            "free_vertices_per_flag": 2,
            "union_orders": [6, 7, 8],
            "root_labels": "pointwise fixed",
            "free_pair": "unordered",
            "centered_covariance_identity": "R*M-s*s^T is PSD",
            "count_denominator_scale": COUNT_SCALE,
        },
        "inputs": {
            str(WAVE147.relative_to(ROOT)).replace("\\", "/"): sha256_file(WAVE147),
            str(WAVE150_MODEL.relative_to(ROOT)).replace("\\", "/"): sha256_file(
                WAVE150_MODEL
            ),
            str(WITNESS.relative_to(ROOT)).replace("\\", "/"): sha256_file(WITNESS),
        },
        "enumeration": enumeration,
        "root_blocks": root_results,
        "limitations": [
            "This discovery package cannot verify its own certificate.",
            "A separation refutes only the Wave150 pseudowitness, not every endpoint count vector.",
            "A block without a negative certificate is not promoted to exact PSD.",
            "No graph or strict upper bound is claimed.",
        ],
        "resource_report": {
            "elapsed_seconds": time.time() - start,
            "memory_samples": memory,
            "minimum_free_physical_memory_percent": min(
                float(record["free_physical_memory_percent"]) for record in memory
            ),
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["conclusion"], indent=2))
    for record in root_results:
        print(
            f"root={record['root_mask']:>2} flags={record['flag_count']:>3} "
            f"min={record['minimum_numeric_eigenvalue_after_max_entry_scaling']:.6g} "
            f"status={record['exact_status']}"
        )
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
