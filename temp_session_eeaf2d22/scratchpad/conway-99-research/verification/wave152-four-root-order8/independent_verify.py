#!/usr/bin/env python3
"""Clean-room exact verifier for the Wave152 four-root certificates.

The discovery program is hashed but never imported or executed.  Lower-order
counts are independently derived from the stored Wave150 x7 support by exact
vertex-deletion identities.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY_CODE = ROOT / "attempts/wave152-four-root-order8/four_root_scout.py"
DISCOVERY_RESULT = ROOT / "attempts/wave152-four-root-order8/four-root-scout.json"
WAVE150_WITNESS = (
    ROOT / "attempts/wave150-order8-sdp-scout/exact-rank1-witness.json"
)

EXPECTED_DISCOVERY_CODE_SHA256 = (
    "84866de40a2c06b826da40cef7f2f212aca3a0fdfb56d38b7df8a0ec2cd4f766"
)
EXPECTED_DISCOVERY_RESULT_SHA256 = (
    "c3633fe3337c1910774e13c9a0841b17bb3f55df1d9800c673979016e877ce95"
)
EXPECTED_WAVE150_WITNESS_SHA256 = (
    "e63afbe9ca36b4b1571b3dde75309d0cce45f3bc862d6e8c08bfe62f78dc130d"
)

N = 99
COUNT_SCALE = 4
MIN_FREE_MEMORY_PERCENT = 15.0
ROOT_MASKS = (0, 1, 3, 7, 11, 12, 13, 15, 30)


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


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def value_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


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
        f"free physical memory {free_percent:.2f}% below 15% floor",
    )
    return {
        "label": label,
        "free_physical_memory_percent": free_percent,
        "available_physical_gib": status.avail_phys / 2**30,
        "total_physical_gib": status.total_phys / 2**30,
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
        if mask >> position & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def locally_admissible(mask: int, order: int) -> bool:
    """Necessary induced conditions for srg parameters lambda=1 and mu=2."""
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
    positions = edge_positions(order)
    result = 0
    for old_position, (left, right) in enumerate(edges(order)):
        if not (mask >> old_position & 1):
            continue
        new_edge = tuple(sorted((permutation[left], permutation[right])))
        result |= 1 << positions[new_edge]
    return result


@lru_cache(maxsize=None)
def canonical_unrooted(mask: int, order: int) -> int:
    return min(
        transform_mask(mask, order, permutation)
        for permutation in itertools.permutations(range(order))
    )


def induced_mask(
    graph_mask: int, graph_order: int, chosen_vertices: Sequence[int]
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


def embed_root_mask(root_mask: int) -> int:
    source = edge_positions(4)
    target = edge_positions(6)
    result = 0
    for edge, position in source.items():
        if root_mask >> position & 1:
            result |= 1 << target[edge]
    return result


def canonical_four_root_flag(mask: int) -> int:
    swapped = transform_mask(mask, 6, (0, 1, 2, 3, 5, 4))
    return min(mask, swapped)


def admissible_root_types() -> tuple[int, ...]:
    return tuple(
        sorted(
            {
                canonical_unrooted(mask, 4)
                for mask in range(1 << len(edges(4)))
                if locally_admissible(mask, 4)
            }
        )
    )


def flag_universe(root_mask: int) -> tuple[int, ...]:
    base = embed_root_mask(root_mask)
    root_edges = set(edges(4))
    extension_positions = tuple(
        position
        for edge, position in edge_positions(6).items()
        if edge not in root_edges
    )
    require(len(extension_positions) == 9, "extension width")
    flags = set()
    for extension in range(1 << 9):
        mask = base
        for bit, position in enumerate(extension_positions):
            if extension >> bit & 1:
                mask |= 1 << position
        if locally_admissible(mask, 6):
            flags.add(canonical_four_root_flag(mask))
    return tuple(sorted(flags))


def automorphism_size(mask: int, order: int) -> int:
    return sum(
        transform_mask(mask, order, permutation) == mask
        for permutation in itertools.permutations(range(order))
    )


def parse_count(value: str | int) -> Fraction:
    return Fraction(str(value))


def derive_lower_counts(
    x7: dict[int, Fraction],
) -> dict[int, dict[int, Fraction]]:
    """Derive x6,x5,x4 using exact one-vertex deletion identities."""
    by_order: dict[int, dict[int, Fraction]] = {7: dict(x7)}
    current = dict(x7)
    for order in (7, 6, 5):
        accumulated: Counter[int] = Counter()
        for mask, count in current.items():
            for deleted in range(order):
                chosen = tuple(vertex for vertex in range(order) if vertex != deleted)
                child = induced_mask(mask, order, chosen)
                accumulated[canonical_unrooted(child, order - 1)] += count
        extension_count = N - (order - 1)
        next_counts = {
            mask: total / extension_count
            for mask, total in accumulated.items()
        }
        require(
            all(count.denominator == 1 for count in next_counts.values()),
            f"nonintegral x{order - 1} deletion count",
        )
        require(
            sum(next_counts.values()) == math.comb(N, order - 1),
            f"x{order - 1} total",
        )
        by_order[order - 1] = next_counts
        current = next_counts
    return by_order


def covering_pair_indices(complement_size: int) -> tuple[tuple[int, int], ...]:
    pairs = tuple(itertools.combinations(range(complement_size), 2))
    return tuple(
        (left, right)
        for left, first in enumerate(pairs)
        for right, second in enumerate(pairs)
        if len(set(first).union(second)) == complement_size
    )


@lru_cache(maxsize=None)
def rooted_embeddings(order: int) -> tuple[
    tuple[tuple[int, ...], tuple[tuple[int, int], ...]], ...
]:
    records = []
    vertices = tuple(range(order))
    covering = covering_pair_indices(order - 4)
    for roots in itertools.permutations(vertices, 4):
        complement = tuple(vertex for vertex in vertices if vertex not in roots)
        free_pairs = tuple(itertools.combinations(complement, 2))
        records.append((roots, free_pairs))
    require(bool(covering), f"no covering pair indices for order {order}")
    return tuple(records)


def add_weighted_moments(
    graph_mask: int,
    graph_order: int,
    weight_scaled: int,
    root_to_index: dict[int, int],
    flag_indices: Sequence[dict[int, int]],
    moments: Sequence[list[list[int]]],
    first_moments: Sequence[list[int]],
) -> tuple[int, int]:
    covering = covering_pair_indices(graph_order - 4)
    matched = 0
    emitted = 0
    for roots, free_pairs in rooted_embeddings(graph_order):
        root_mask = induced_mask(graph_mask, graph_order, roots)
        root_index = root_to_index.get(root_mask)
        if root_index is None:
            continue
        matched += 1
        flag_by_pair = []
        for free_pair in free_pairs:
            flag = induced_mask(graph_mask, graph_order, roots + free_pair)
            canonical_flag = canonical_four_root_flag(flag)
            require(
                canonical_flag in flag_indices[root_index],
                "emitted flag outside independently built universe",
            )
            flag_by_pair.append(flag_indices[root_index][canonical_flag])
        if graph_order == 6:
            require(len(flag_by_pair) == 1, "order-six free-pair count")
            first_moments[root_index][flag_by_pair[0]] += weight_scaled
        matrix = moments[root_index]
        for left, right in covering:
            matrix[flag_by_pair[left]][flag_by_pair[right]] += weight_scaled
            emitted += 1
    return matched, emitted


def certificate_quadratic(
    root_count: int,
    first_scaled: Sequence[int],
    matrix_scaled: Sequence[Sequence[int]],
    indices: Sequence[int],
    vector: Sequence[int],
) -> int:
    require(len(indices) == len(vector), "certificate support length")
    linear = sum(
        vector[position] * first_scaled[index]
        for position, index in enumerate(indices)
    )
    require(linear * linear % COUNT_SCALE == 0, "certificate scaling")
    matrix_quadratic = sum(
        vector[left_position]
        * vector[right_position]
        * matrix_scaled[left_index][right_index]
        for left_position, left_index in enumerate(indices)
        for right_position, right_index in enumerate(indices)
    )
    return root_count * matrix_quadratic - linear * linear // COUNT_SCALE


def verify_flag_semantics(root_mask: int, flags: Sequence[int]) -> None:
    require(tuple(flags) == tuple(sorted(set(flags))), "flag order or duplicate")
    for flag in flags:
        require(locally_admissible(flag, 6), "inadmissible flag")
        require(canonical_four_root_flag(flag) == flag, "free pair not canonical")
        induced_root = induced_mask(flag, 6, (0, 1, 2, 3))
        require(induced_root == root_mask, "pointwise root mismatch")


def verify_certificate_flag_semantics(
    family: Sequence[int],
    indices: Sequence[int],
    certificate_flags: Sequence[int],
) -> None:
    require(
        tuple(family[index] for index in indices) == tuple(certificate_flags),
        "certificate index/flag semantics",
    )


def build_result() -> dict[str, object]:
    memory = [memory_record("start")]
    require(
        sha256_file(DISCOVERY_CODE) == EXPECTED_DISCOVERY_CODE_SHA256,
        "discovery code hash drift",
    )
    require(
        sha256_file(DISCOVERY_RESULT) == EXPECTED_DISCOVERY_RESULT_SHA256,
        "discovery result hash drift",
    )
    require(
        sha256_file(WAVE150_WITNESS) == EXPECTED_WAVE150_WITNESS_SHA256,
        "Wave150 witness hash drift",
    )
    stored = json.loads(DISCOVERY_RESULT.read_text(encoding="utf-8"))
    witness = json.loads(WAVE150_WITNESS.read_text(encoding="utf-8"))
    require(stored["claim_label"] == "CANDIDATE", "unexpected discovery status")
    require(
        witness["conclusion"]["finite_relaxation"] == "EXACT_RATIONAL_FEASIBLE",
        "unexpected Wave150 witness status",
    )

    generated_root_types = admissible_root_types()
    require(generated_root_types == ROOT_MASKS, "four-root type census")
    flags = tuple(flag_universe(root_mask) for root_mask in ROOT_MASKS)
    for root_mask, family in zip(ROOT_MASKS, flags):
        verify_flag_semantics(root_mask, family)
    flag_indices = tuple(
        {flag: index for index, flag in enumerate(family)}
        for family in flags
    )

    x7 = {
        int(record["canonical_mask"]): parse_count(record["count"])
        for record in witness["x7_support"]
    }
    x8 = {
        int(record["canonical_mask"]): parse_count(record["count"])
        for record in witness["x8_support"]
    }
    require(all(count > 0 for count in x7.values()), "nonpositive x7 support")
    require(all(count > 0 for count in x8.values()), "nonpositive x8 support")
    require(all(count.denominator == 1 for count in x7.values()), "fractional x7")
    require(
        all(COUNT_SCALE % count.denominator == 0 for count in x8.values()),
        "x8 denominator exceeds scale",
    )
    lower = derive_lower_counts(x7)
    x6 = lower[6]
    x4 = lower[4]
    require(len(x6) == 61, "x6 nonzero support size")
    require(len(x4) == 9, "x4 support size")

    count_maps = {6: x6, 7: x7, 8: x8}
    root_to_index = {root_mask: index for index, root_mask in enumerate(ROOT_MASKS)}
    moments = tuple(
        [[0] * len(family) for _ in family]
        for family in flags
    )
    first_moments = tuple([0] * len(family) for family in flags)
    enumeration = {}
    for order in (6, 7, 8):
        matched = 0
        emitted = 0
        for graph_mask, weight in count_maps[order].items():
            scaled = weight * COUNT_SCALE
            require(scaled.denominator == 1, f"fractional scaled x{order}")
            local_matched, local_emitted = add_weighted_moments(
                graph_mask,
                order,
                int(scaled),
                root_to_index,
                flag_indices,
                moments,
                first_moments,
            )
            matched += local_matched
            emitted += local_emitted
        enumeration[str(order)] = {
            "nonzero_classes": len(count_maps[order]),
            "matched_root_embeddings_unweighted": matched,
            "emitted_products_unweighted": emitted,
        }
        memory.append(memory_record(f"order_{order}_complete"))

    stored_by_root = {
        int(record["root_mask"]): record for record in stored["root_blocks"]
    }
    require(set(stored_by_root) == set(ROOT_MASKS), "stored root blocks")
    free_pairs_full = math.comb(N - 4, 2)
    root_results = []
    for root_index, root_mask in enumerate(ROOT_MASKS):
        family = flags[root_index]
        root_count_fraction = (
            automorphism_size(root_mask, 4)
            * x4[canonical_unrooted(root_mask, 4)]
        )
        require(root_count_fraction.denominator == 1, "fractional root count")
        root_count = int(root_count_fraction)
        first_scaled = first_moments[root_index]
        matrix_scaled = moments[root_index]
        first_total_scaled = sum(first_scaled)
        second_total_scaled = sum(map(sum, matrix_scaled))
        require(
            first_total_scaled
            == COUNT_SCALE * root_count * free_pairs_full,
            f"first total root {root_mask}",
        )
        require(
            second_total_scaled
            == COUNT_SCALE * root_count * free_pairs_full * free_pairs_full,
            f"second total root {root_mask}",
        )
        require(
            all(
                first_scaled[row] * first_scaled[column] % COUNT_SCALE == 0
                for row in range(len(family))
                for column in range(len(family))
            ),
            f"center scaling root {root_mask}",
        )
        centered = [
            [
                root_count * matrix_scaled[row][column]
                - first_scaled[row] * first_scaled[column] // COUNT_SCALE
                for column in range(len(family))
            ]
            for row in range(len(family))
        ]
        require(
            centered == [list(row) for row in zip(*centered)],
            f"nonsymmetric centered block root {root_mask}",
        )
        maximum_absolute = max(abs(value) for row in centered for value in row)
        stored_root = stored_by_root[root_mask]
        require(list(family) == stored_root["flag_masks"], "stored flag universe")
        require(len(family) == int(stored_root["flag_count"]), "stored flag count")
        require(root_count == int(stored_root["root_embedding_count"]), "root count")
        require(
            first_total_scaled // COUNT_SCALE
            == int(stored_root["first_moment_total"]),
            "stored first total",
        )
        require(
            second_total_scaled // COUNT_SCALE
            == int(stored_root["second_moment_total"]),
            "stored second total",
        )
        require(
            maximum_absolute
            == int(stored_root["maximum_absolute_scaled_entry"]),
            "stored centered maximum",
        )

        certificate_result = None
        stored_certificate = stored_root["negative_certificate"]
        if stored_certificate is not None:
            indices = tuple(int(index) for index in stored_certificate["indices"])
            vector = tuple(int(value) for value in stored_certificate["vector"])
            certificate_flags = tuple(
                int(mask) for mask in stored_certificate["flag_masks"]
            )
            verify_certificate_flag_semantics(
                family,
                indices,
                certificate_flags,
            )
            quadratic = certificate_quadratic(
                root_count,
                first_scaled,
                matrix_scaled,
                indices,
                vector,
            )
            direct_quadratic = sum(
                vector[left_position]
                * vector[right_position]
                * centered[left_index][right_index]
                for left_position, left_index in enumerate(indices)
                for right_position, right_index in enumerate(indices)
            )
            require(quadratic == direct_quadratic, "quadratic replay disagreement")
            require(
                quadratic == int(stored_certificate["quadratic_value_scaled"]),
                "stored quadratic value",
            )
            require(quadratic < 0, "certificate is not negative")
            hostile_vector = list(vector)
            hostile_vector[0] += 1
            hostile_value = certificate_quadratic(
                root_count,
                first_scaled,
                matrix_scaled,
                indices,
                hostile_vector,
            )
            require(hostile_value != quadratic, "hostile vector mutation survived")
            certificate_result = {
                "kind": "integer_vector",
                "support_size": len(indices),
                "indices": list(indices),
                "flag_masks": list(certificate_flags),
                "vector": list(vector),
                "quadratic_value_scaled": str(quadratic),
                "strictly_negative": True,
                "proves_centered_block_not_psd": True,
                "hostile_first_coordinate_plus_one_value_scaled": str(hostile_value),
                "hostile_mutation_rejected": True,
            }

        root_results.append(
            {
                "root_mask": root_mask,
                "automorphism_size": automorphism_size(root_mask, 4),
                "root_embedding_count": root_count,
                "flag_count": len(family),
                "flag_masks": list(family),
                "flag_masks_sha256": value_sha256(list(family)),
                "first_moment_total": first_total_scaled // COUNT_SCALE,
                "first_moment_scaled_sha256": value_sha256(first_scaled),
                "second_moment_total": second_total_scaled // COUNT_SCALE,
                "second_moment_scaled_sha256": value_sha256(matrix_scaled),
                "centered_scale": "4*(R*M-s*s^T)",
                "centered_scaled_sha256": value_sha256(centered),
                "maximum_absolute_scaled_entry": maximum_absolute,
                "negative_certificate": certificate_result,
                "exact_status": (
                    "NOT_PSD"
                    if certificate_result is not None
                    else (
                        "EXACTLY_PSD_ZERO"
                        if maximum_absolute == 0
                        else "UNKNOWN_NO_NEGATIVE_CERTIFICATE"
                    )
                ),
            }
        )
        del centered

    require(enumeration == stored["enumeration"], "stored enumeration mismatch")
    negative_masks = tuple(
        record["root_mask"]
        for record in root_results
        if record["exact_status"] == "NOT_PSD"
    )
    require(negative_masks == (3, 12), "negative root-mask census")
    memory.append(memory_record("complete"))
    return {
        "format": "wave152-independent-four-root-order8-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "Exact rejection of the Wave150 x6/x7/x8 pseudowitness by "
            "four-root covariance blocks; not endpoint rejection"
        ),
        "inputs": {
            str(DISCOVERY_CODE.relative_to(ROOT)).replace("\\", "/"):
                EXPECTED_DISCOVERY_CODE_SHA256,
            str(DISCOVERY_RESULT.relative_to(ROOT)).replace("\\", "/"):
                EXPECTED_DISCOVERY_RESULT_SHA256,
            str(WAVE150_WITNESS.relative_to(ROOT)).replace("\\", "/"):
                EXPECTED_WAVE150_WITNESS_SHA256,
            "discovery_code_imported_or_executed": False,
        },
        "semantics": {
            "root_order": 4,
            "root_labels": "pointwise fixed",
            "root_masks": list(ROOT_MASKS),
            "free_vertices_per_flag": 2,
            "free_pair": "unordered modulo only the swap of vertices 4 and 5",
            "flag_order": 6,
            "union_orders": [6, 7, 8],
            "local_admissibility": (
                "adjacent codegree at most lambda=1; nonadjacent codegree "
                "at most mu=2"
            ),
            "moment_pairing": (
                "ordered pairs of unordered free pairs, partitioned by "
                "union order 6, 7, or 8"
            ),
        },
        "count_reconstruction": {
            "route": (
                "x6,x5,x4 derived from exact x7 support by one-vertex "
                "deletion identities; no discovery/model code executed"
            ),
            "support_sizes": {
                "x4": len(x4),
                "x5": len(lower[5]),
                "x6": len(x6),
                "x7": len(x7),
                "x8": len(x8),
            },
            "x4_sha256": value_sha256(
                [[mask, str(count)] for mask, count in sorted(x4.items())]
            ),
            "x6_sha256": value_sha256(
                [[mask, str(count)] for mask, count in sorted(x6.items())]
            ),
            "x7_sha256": value_sha256(
                [[mask, str(count)] for mask, count in sorted(x7.items())]
            ),
            "x8_sha256": value_sha256(
                [[mask, str(count)] for mask, count in sorted(x8.items())]
            ),
            "count_denominator_scale": COUNT_SCALE,
        },
        "enumeration": enumeration,
        "root_blocks": root_results,
        "verdict": {
            "root_mask_3_centered_block": "VERIFIED_NOT_PSD",
            "root_mask_12_centered_block": "VERIFIED_NOT_PSD",
            "wave150_pseudowitness": "REFUTED",
            "endpoint_n3_4158": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "strict_upper_bound": "NOT_PROVED",
        },
        "proof_rule": (
            "A real symmetric PSD matrix has v^T B v >= 0 for every real v; "
            "each replayed integer vector has an exact negative value."
        ),
        "limitations": [
            "Only the single Wave150 pseudowitness is separated.",
            "No universal endpoint infeasibility certificate is supplied.",
            "Blocks lacking a negative vector are not certified PSD.",
            "No graph result, strict bound, endpoint resolution, or novelty claim follows.",
        ],
        "resource_report": {
            "memory_samples": memory,
            "minimum_free_physical_memory_percent": min(
                float(record["free_physical_memory_percent"])
                for record in memory
            ),
            "required_floor_percent": MIN_FREE_MEMORY_PERCENT,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = build_result()
    if args.verify is not None:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        # Memory samples are observational and intentionally excluded from replay.
        result_without_memory = dict(result)
        stored_without_memory = dict(stored)
        result_without_memory.pop("resource_report")
        stored_without_memory.pop("resource_report")
        require(result_without_memory == stored_without_memory, "stored result mismatch")
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "semantic_sha256": value_sha256(result_without_memory),
                },
                sort_keys=True,
            )
        )
        return
    output = args.output or HERE / "independent-results.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "WROTE",
                "path": str(output),
                "semantic_sha256": value_sha256(
                    {key: value for key, value in result.items() if key != "resource_report"}
                ),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
