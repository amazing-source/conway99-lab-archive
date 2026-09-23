#!/usr/bin/env python3
"""Exact Wave 52 rooted coherent-closure experiment.

This file studies only the finite structure forced around one triangle at the
prism-free endpoint.  It does not assume that any automorphism of this local
template extends to a completed Conway graph.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import sys
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Iterable, Sequence


SECTORS = range(3)
PETALS = range(6)
SECTOR_PAIRS = ((0, 1), (0, 2), (1, 2))
CYCLE_PARTITIONS = ((6,), (4, 2), (3, 3), (2, 2, 2))
MEMORY_FLOOR_PERCENT = 20.0


class MemoryStatus(ctypes.Structure):
    _fields_ = (
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_physical", ctypes.c_ulonglong),
        ("available_physical", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("available_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("available_virtual", ctypes.c_ulonglong),
        ("available_extended_virtual", ctypes.c_ulonglong),
    )


def free_physical_memory_percent() -> float:
    if sys.platform != "win32":
        return 100.0
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.available_physical / status.total_physical


def enforce_memory_floor() -> float:
    free_percent = free_physical_memory_percent()
    if free_percent < MEMORY_FLOOR_PERCENT:
        raise MemoryError(
            f"free physical memory {free_percent:.2f}% is below "
            f"{MEMORY_FLOOR_PERCENT:.2f}%"
        )
    return free_percent


def petal(sector: int, index: int) -> str:
    return f"p{sector}_{index}"


def candidate(left_sector: int, right_sector: int, left: int, right: int) -> str:
    return f"e{left_sector}{right_sector}_{left}_{right}"


def cap(owner_sector: int, target_sector: int, owner: int) -> str:
    return f"c{owner_sector}{target_sector}_{owner}"


def triangle_labels() -> tuple[str, ...]:
    return ("root",) + tuple(
        petal(sector, index) for sector in SECTORS for index in PETALS
    )


def parse_petal(label: str) -> tuple[int, int]:
    if not label.startswith("p"):
        raise ValueError(f"not a petal label: {label}")
    sector, index = label[1:].split("_")
    return int(sector), int(index)


def canonicalize_tokens(tokens: Sequence[Sequence[object]]) -> list[list[int]]:
    unique = sorted({token for row in tokens for token in row})
    ids = {token: index for index, token in enumerate(unique)}
    return [[ids[token] for token in row] for row in tokens]


def partial_triangle_structure() -> tuple[tuple[str, ...], list[list[str]]]:
    """The completion-free root plus its 18 K-neighbors.

    Cross-sector petal pairs are deliberately left in the single color U.
    """

    labels = triangle_labels()
    colors: list[list[str]] = []
    for left in labels:
        row = []
        for right in labels:
            if left == right:
                row.append("diag_root" if left == "root" else "diag_petal")
            elif left == "root":
                row.append("K_root_to_petal")
            elif right == "root":
                row.append("K_petal_to_root")
            else:
                left_sector, _ = parse_petal(left)
                right_sector, _ = parse_petal(right)
                row.append("K_same_sector" if left_sector == right_sector else "U")
        colors.append(row)
    return labels, colors


def constraint_template_structure() -> tuple[tuple[str, ...], list[list[str]]]:
    """Incidence encoding of every allowed cross-sector B choice and cap.

    There are 108 Boolean-choice nodes, one for each cross-sector petal pair,
    and 36 cap nodes.  A cap says that one petal must choose exactly two of the
    six candidate B-neighbors in a specified opposite sector.  The numerical
    right side two is metadata of the cap-node type; 2-WL sees the exact
    incidence pattern, while a separate exact checker enforces the right side.
    """

    triangles = triangle_labels()
    candidates = tuple(
        candidate(left_sector, right_sector, left, right)
        for left_sector, right_sector in SECTOR_PAIRS
        for left in PETALS
        for right in PETALS
    )
    caps = tuple(
        cap(owner_sector, target_sector, owner)
        for owner_sector in SECTORS
        for target_sector in SECTORS
        if owner_sector != target_sector
        for owner in PETALS
    )
    labels = triangles + candidates + caps

    kinds = {}
    for label in labels:
        if label == "root":
            kinds[label] = "root"
        elif label.startswith("p"):
            kinds[label] = "petal"
        elif label.startswith("e"):
            kinds[label] = "candidate_B"
        else:
            kinds[label] = "cap_exactly_2"

    candidate_endpoints: dict[str, frozenset[str]] = {}
    candidate_caps: dict[str, frozenset[str]] = {}
    for left_sector, right_sector in SECTOR_PAIRS:
        for left in PETALS:
            for right in PETALS:
                edge = candidate(left_sector, right_sector, left, right)
                candidate_endpoints[edge] = frozenset(
                    (petal(left_sector, left), petal(right_sector, right))
                )
                candidate_caps[edge] = frozenset(
                    (
                        cap(left_sector, right_sector, left),
                        cap(right_sector, left_sector, right),
                    )
                )

    cap_owner = {}
    for owner_sector in SECTORS:
        for target_sector in SECTORS:
            if owner_sector == target_sector:
                continue
            for owner in PETALS:
                cap_owner[cap(owner_sector, target_sector, owner)] = petal(
                    owner_sector, owner
                )

    def relation(left: str, right: str) -> str:
        if left == right:
            return "diag"
        if left == "root" and right.startswith("p"):
            return "K"
        if right == "root" and left.startswith("p"):
            return "K"
        if left.startswith("p") and right.startswith("p"):
            left_sector, _ = parse_petal(left)
            right_sector, _ = parse_petal(right)
            return "K" if left_sector == right_sector else "cross_unselected"
        if left.startswith("e") and right in candidate_endpoints.get(left, ()):
            return "candidate_endpoint"
        if right.startswith("e") and left in candidate_endpoints.get(right, ()):
            return "candidate_endpoint"
        if left.startswith("e") and right in candidate_caps.get(left, ()):
            return "candidate_in_cap"
        if right.startswith("e") and left in candidate_caps.get(right, ()):
            return "candidate_in_cap"
        if left.startswith("c") and cap_owner.get(left) == right:
            return "cap_owner"
        if right.startswith("c") and cap_owner.get(right) == left:
            return "cap_owner"
        return "none"

    tokens = [
        [
            f"{kinds[left]}->{kinds[right]}:{relation(left, right)}"
            for right in labels
        ]
        for left in labels
    ]
    return labels, tokens


def validate_cycle_partition(parts: Sequence[int]) -> tuple[int, ...]:
    normalized = tuple(parts)
    if tuple(sorted(normalized, reverse=True)) != normalized:
        raise ValueError("cycle partition must be nonincreasing")
    if any(part < 2 for part in normalized):
        raise ValueError("a simple bipartite 2-factor has half-cycle size >=2")
    if sum(normalized) != 6:
        raise ValueError("cycle partition must sum to six")
    if normalized not in CYCLE_PARTITIONS:
        raise ValueError(f"unexpected cycle partition: {normalized}")
    return normalized


def bipartite_two_factor(parts: Sequence[int]) -> frozenset[tuple[int, int]]:
    """Return a canonical 6-by-6 simple 2-factor of the requested cycle type."""

    partition = validate_cycle_partition(parts)
    edges: set[tuple[int, int]] = set()
    offset = 0
    for size in partition:
        component = range(offset, offset + size)
        for local, left in enumerate(component):
            edges.add((left, offset + local))
            edges.add((left, offset + (local + 1) % size))
        offset += size
    verify_two_factor(edges)
    return frozenset(edges)


def verify_two_factor(edges: Iterable[tuple[int, int]]) -> None:
    edge_set = set(edges)
    if len(edge_set) != 12:
        raise AssertionError(f"B relation has {len(edge_set)} edges, expected 12")
    if any(left not in PETALS or right not in PETALS for left, right in edge_set):
        raise AssertionError("B relation endpoint outside the six petals")
    left_degrees = Counter(left for left, _ in edge_set)
    right_degrees = Counter(right for _, right in edge_set)
    if tuple(left_degrees[index] for index in PETALS) != (2,) * 6:
        raise AssertionError("left B degrees are not all two")
    if tuple(right_degrees[index] for index in PETALS) != (2,) * 6:
        raise AssertionError("right B degrees are not all two")


def completion_from_profile(
    profile: Sequence[Sequence[int]],
) -> dict[tuple[int, int], frozenset[tuple[int, int]]]:
    if len(profile) != 3:
        raise ValueError("one cycle partition is required for each sector pair")
    completion = {}
    for sector_pair, partition in zip(SECTOR_PAIRS, profile, strict=True):
        completion[sector_pair] = bipartite_two_factor(partition)
    verify_completion(completion)
    return completion


def verify_completion(
    completion: dict[tuple[int, int], frozenset[tuple[int, int]]],
) -> None:
    if set(completion) != set(SECTOR_PAIRS):
        raise AssertionError("completion does not cover the three sector pairs")
    for edge_set in completion.values():
        verify_two_factor(edge_set)


def completed_triangle_structure(
    completion: dict[tuple[int, int], frozenset[tuple[int, int]]],
) -> tuple[tuple[str, ...], list[list[str]]]:
    verify_completion(completion)
    labels = triangle_labels()
    colors: list[list[str]] = []
    for left in labels:
        row = []
        for right in labels:
            if left == right:
                row.append("diag_root" if left == "root" else "diag_petal")
            elif left == "root":
                row.append("K_root_to_petal")
            elif right == "root":
                row.append("K_petal_to_root")
            else:
                left_sector, left_index = parse_petal(left)
                right_sector, right_index = parse_petal(right)
                if left_sector == right_sector:
                    row.append("K_same_sector")
                else:
                    if left_sector < right_sector:
                        sector_pair = (left_sector, right_sector)
                        pair = (left_index, right_index)
                    else:
                        sector_pair = (right_sector, left_sector)
                        pair = (right_index, left_index)
                    row.append("B" if pair in completion[sector_pair] else "C")
        colors.append(row)
    verify_completed_triangle_relations(labels, colors)
    return labels, colors


def verify_completed_triangle_relations(
    labels: Sequence[str], colors: Sequence[Sequence[str]]
) -> None:
    if tuple(labels) != triangle_labels():
        raise AssertionError("unexpected triangle-label universe")
    root_index = labels.index("root")
    root_row = Counter(colors[root_index])
    if root_row != Counter({"K_root_to_petal": 18, "diag_root": 1}):
        raise AssertionError("root does not have exactly 18 K-neighbors")
    for row_index, label in enumerate(labels):
        if label == "root":
            continue
        counts = Counter(colors[row_index])
        expected = Counter(
            {
                "diag_petal": 1,
                "K_petal_to_root": 1,
                "K_same_sector": 5,
                "B": 4,
                "C": 8,
            }
        )
        if counts != expected:
            raise AssertionError(f"bad rooted relation caps at {label}: {counts}")


def wl2(tokens: Sequence[Sequence[object]]) -> dict[str, object]:
    """Run exact two-dimensional Weisfeiler-Leman refinement."""

    order = len(tokens)
    if order == 0 or any(len(row) != order for row in tokens):
        raise ValueError("2-WL input must be a nonempty square matrix")
    colors = canonicalize_tokens(tokens)
    initial_color_count = len({color for row in colors for color in row})
    rounds = 0
    color_counts = [initial_color_count]
    while True:
        signatures = []
        for left in range(order):
            row = []
            for right in range(order):
                multiplicities = Counter(
                    (colors[left][middle], colors[middle][right])
                    for middle in range(order)
                )
                row.append(
                    (
                        colors[left][right],
                        tuple(sorted(multiplicities.items())),
                    )
                )
            signatures.append(row)
        refined = canonicalize_tokens(signatures)
        refined_count = len({color for row in refined for color in row})
        if refined_count < color_counts[-1]:
            raise AssertionError("2-WL refinement merged colors")
        if refined_count == color_counts[-1]:
            colors = refined
            break
        colors = refined
        rounds += 1
        color_counts.append(refined_count)

    certificate = coherent_certificate(colors)
    return {
        "order": order,
        "initial_color_count": initial_color_count,
        "proper_refinement_rounds": rounds,
        "color_counts": color_counts,
        "stable_color_count": certificate["stable_color_count"],
        "class_sizes": certificate["class_sizes"],
        "pair_color_matrix": colors,
        "intersection_numbers_nonzero": certificate[
            "intersection_numbers_nonzero"
        ],
        "intersection_parameter_nonzero_count": certificate[
            "intersection_parameter_nonzero_count"
        ],
        "partition_sha256": certificate["partition_sha256"],
        "intersection_tensor_sha256": certificate["intersection_tensor_sha256"],
        "invariant_fingerprint_sha256": certificate[
            "invariant_fingerprint_sha256"
        ],
    }


def coherent_certificate(colors: Sequence[Sequence[int]]) -> dict[str, object]:
    order = len(colors)
    classes: dict[int, list[tuple[int, int]]] = {}
    for left, right in product(range(order), repeat=2):
        classes.setdefault(colors[left][right], []).append((left, right))
    stable_color_count = len(classes)
    if set(classes) != set(range(stable_color_count)):
        raise AssertionError("stable colors are not contiguous")

    records = []
    for output_color in range(stable_color_count):
        representative = classes[output_color][0]
        reference = Counter(
            (
                colors[representative[0]][middle],
                colors[middle][representative[1]],
            )
            for middle in range(order)
        )
        for left, right in classes[output_color][1:]:
            current = Counter(
                (colors[left][middle], colors[middle][right])
                for middle in range(order)
            )
            if current != reference:
                raise AssertionError(
                    f"intersection numbers vary in color {output_color}"
                )
        for (left_color, right_color), value in sorted(reference.items()):
            if value:
                records.append(
                    [left_color, right_color, output_color, value]
                )

    class_sizes = [len(classes[color]) for color in range(stable_color_count)]
    partition_bytes = canonical_bytes(colors)
    intersection_bytes = canonical_bytes(records)
    invariant_payload = {
        "class_sizes": class_sizes,
        "intersection_numbers_nonzero": records,
        "order": order,
    }
    return {
        "stable_color_count": stable_color_count,
        "class_sizes": class_sizes,
        "intersection_numbers_nonzero": records,
        "intersection_parameter_nonzero_count": len(records),
        "partition_sha256": hashlib.sha256(partition_bytes).hexdigest(),
        "intersection_tensor_sha256": hashlib.sha256(
            intersection_bytes
        ).hexdigest(),
        "invariant_fingerprint_sha256": hashlib.sha256(
            canonical_bytes(invariant_payload)
        ).hexdigest(),
    }


def compact_closure(result: dict[str, object]) -> dict[str, object]:
    return {
        key: result[key]
        for key in (
            "order",
            "initial_color_count",
            "proper_refinement_rounds",
            "color_counts",
            "stable_color_count",
            "class_sizes",
            "intersection_parameter_nonzero_count",
            "partition_sha256",
            "intersection_tensor_sha256",
            "invariant_fingerprint_sha256",
        )
    }


def diagonal_class_sizes(closure: dict[str, object]) -> list[int]:
    matrix = closure["pair_color_matrix"]
    return sorted(Counter(matrix[index][index] for index in range(len(matrix))).values())


def all_canonical_completion_profiles() -> list[dict[str, object]]:
    records = []
    for profile in product(CYCLE_PARTITIONS, repeat=3):
        completion = completion_from_profile(profile)
        _, tokens = completed_triangle_structure(completion)
        closure = wl2(tokens)
        records.append(
            {
                "profile": [list(partition) for partition in profile],
                "closure": compact_closure(closure),
            }
        )
    return records


def validate_constraint_template(
    labels: Sequence[str], tokens: Sequence[Sequence[str]]
) -> dict[str, object]:
    counts = Counter(
        "root"
        if label == "root"
        else "petal"
        if label.startswith("p")
        else "candidate_B"
        if label.startswith("e")
        else "cap_exactly_2"
        for label in labels
    )
    expected = Counter(
        {"root": 1, "petal": 18, "candidate_B": 108, "cap_exactly_2": 36}
    )
    if counts != expected:
        raise AssertionError(f"bad constraint-template node counts: {counts}")

    for index, label in enumerate(labels):
        row = Counter(token.rsplit(":", 1)[-1] for token in tokens[index])
        if label.startswith("e"):
            if row["candidate_endpoint"] != 2 or row["candidate_in_cap"] != 2:
                raise AssertionError(f"bad candidate incidences at {label}: {row}")
        if label.startswith("c"):
            if row["cap_owner"] != 1 or row["candidate_in_cap"] != 6:
                raise AssertionError(f"bad cap incidences at {label}: {row}")
    return {
        "node_counts": dict(sorted(counts.items())),
        "each_candidate_B_node_has_two_endpoints": True,
        "each_candidate_B_node_lies_in_two_caps": True,
        "each_exactly_2_cap_has_six_candidates": True,
        "each_exactly_2_cap_has_one_owner_petal": True,
    }


def build_results() -> dict[str, object]:
    enforce_memory_floor()

    partial_labels, partial_tokens = partial_triangle_structure()
    partial_closure = wl2(partial_tokens)

    template_labels, template_tokens = constraint_template_structure()
    template_checks = validate_constraint_template(template_labels, template_tokens)
    template_closure = wl2(template_tokens)

    completion_records = all_canonical_completion_profiles()
    fingerprint_counts = Counter(
        record["closure"]["invariant_fingerprint_sha256"]
        for record in completion_records
    )
    stable_color_counts = sorted(
        {record["closure"]["stable_color_count"] for record in completion_records}
    )
    first_profile = (CYCLE_PARTITIONS[0],) * 3
    second_profile = (CYCLE_PARTITIONS[-1],) * 3
    diagnostic_examples = []
    for profile in (first_profile, second_profile):
        completion = completion_from_profile(profile)
        labels, tokens = completed_triangle_structure(completion)
        closure = wl2(tokens)
        diagnostic_examples.append(
            {
                "profile": [list(partition) for partition in profile],
                "relation_caps_checked": True,
                "labels": list(labels),
                "closure": closure,
            }
        )
    if (
        diagnostic_examples[0]["closure"]["invariant_fingerprint_sha256"]
        == diagnostic_examples[1]["closure"]["invariant_fingerprint_sha256"]
    ):
        raise AssertionError("chosen completion diagnostics did not separate")

    return {
        "format": "wave52-rooted-coherent-closure-v1",
        "claim_label": "DERIVED",
        "claim_boundary": {
            "completion_free_constraint_template_closure": "EXACT_DERIVED",
            "new_intersection_number_or_integrality_obstruction": False,
            "completed_relation_closure": "COMPLETION_DEPENDENT",
            "prism_free_endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "frozen_relations": {
            "order": ["I", "K", "D", "C", "B"],
            "meaning": {
                "I": "equal graph triangles",
                "K": "share one graph vertex",
                "D": "disjoint with zero cross edges",
                "C": "disjoint with one cross edge",
                "B": "disjoint with two cross edges",
            },
            "global_valencies": [1, 18, 32, 144, 36],
            "rooted_forced_structure": {
                "root_triangle_count": 1,
                "K_neighbor_count": 18,
                "K_neighbor_partition": "3K6",
                "cross_sector_relations": ["B", "C"],
                "per_petal_per_opposite_sector_B_degree": 2,
                "per_petal_per_opposite_sector_C_degree": 4,
                "D_degree_inside_rooted_19_triangle_structure": 0,
            },
        },
        "derivation_scope": {
            "automorphism_policy": (
                "No local symmetry is assumed to extend to a completed graph; "
                "no transitivity or association-scheme constants are imposed."
            ),
            "completion_policy": (
                "The forced closure uses a CSP incidence template containing "
                "all 108 allowed B choices and all 36 exactly-two caps. "
                "Completed B/C examples are diagnostics only."
            ),
            "right_side_semantics": (
                "2-WL refines the binary incidence structure. Exact-two cap "
                "right sides are checked separately by integral completions."
            ),
        },
        "partial_19_triangle_closure": {
            "labels": list(partial_labels),
            "diagonal_class_sizes": diagonal_class_sizes(partial_closure),
            "closure": partial_closure,
        },
        "completion_free_constraint_template": {
            "labels": list(template_labels),
            "checks": template_checks,
            "diagonal_class_sizes": diagonal_class_sizes(template_closure),
            "closure": template_closure,
        },
        "canonical_completion_diagnostic": {
            "scope": (
                "64 canonical cycle-profile triples only; not an exhaustive "
                "classification of joint labelled completions."
            ),
            "cycle_partitions_per_sector_pair": [
                list(partition) for partition in CYCLE_PARTITIONS
            ],
            "profile_count": len(completion_records),
            "distinct_invariant_fingerprint_count": len(fingerprint_counts),
            "stable_color_counts_observed": stable_color_counts,
            "fingerprint_multiplicities": dict(sorted(fingerprint_counts.items())),
            "records": completion_records,
            "two_full_certificate_examples": diagnostic_examples,
        },
        "result": {
            "exact_contradiction": False,
            "positive_local_cap_completions": True,
            "new_forced_color_obstruction": False,
            "completed_closure_depends_on_arbitrary_B_completion": True,
            "disposition": "NULL_RESULT_FOR_THIS_COHERENT_CLOSURE",
        },
        "checks": {
            "free_physical_memory_at_start_at_least_percent": (
                MEMORY_FLOOR_PERCENT
            ),
            "memory_floor_percent": MEMORY_FLOOR_PERCENT,
            "all_arithmetic_exact": True,
            "partial_closure_intersection_numbers_constant": True,
            "constraint_template_intersection_numbers_constant": True,
            "canonical_completion_profiles_checked": len(completion_records),
            "all_completed_petal_rows_have_K5_B4_C8_plus_root": True,
        },
        "limitations": [
            "This is discovery-agent work and is not independently verified.",
            "The exact coherent closure is only for one root triangle and its 18 K-neighbors.",
            "2-WL does not enforce the full 231-triangle adjacency algebra or the 99-vertex SRG equations.",
            "The exactly-two cap value is checked by explicit integral completions, not inferred by 2-WL.",
            "The 64 completed examples fix arbitrary canonical B two-factors and are diagnostic, not exhaustive.",
            "A local cap completion need not lift to a Conway graph.",
            "No global graph automorphism, transitivity, or association scheme is assumed.",
            "No endpoint exclusion, graph construction, or improved n3 upper bound follows.",
        ],
    }


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()

    encoded = canonical_bytes(build_results())
    digest = hashlib.sha256(encoded).hexdigest()
    if arguments.verify is not None:
        if arguments.verify.read_bytes() != encoded:
            print(f"FAIL: {arguments.verify} differs", file=sys.stderr)
            return 1
        print("PASS_EXACT_REPLAY")
        print(f"sha256={digest}")
        return 0
    if arguments.output is not None:
        arguments.output.write_bytes(encoded)
        print(arguments.output)
        print(f"sha256={digest}")
        return 0
    sys.stdout.buffer.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
