#!/usr/bin/env python3
"""Exact pre-SAT invariants for all Wave 60 component triples."""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
CHECK_PATH = HERE / "exact_check.py"
SPEC = importlib.util.spec_from_file_location("wave60_exact_check", CHECK_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import exact checker")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def rank_f2(matrix: Sequence[Sequence[int]]) -> int:
    rows = [
        sum((value & 1) << column for column, value in enumerate(row))
        for row in matrix
    ]
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next(
            (
                index
                for index in range(rank, len(rows))
                if rows[index] >> column & 1
            ),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and rows[index] >> column & 1:
                rows[index] ^= rows[rank]
        rank += 1
    return rank


def matrix_multiply(
    left: Sequence[Sequence[int]],
    right: Sequence[Sequence[int]],
) -> list[list[int]]:
    return [
        [
            sum(
                left[row][middle] * right[middle][column]
                for middle in range(len(right))
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def characteristic_polynomial(
    matrix: Sequence[Sequence[int]],
) -> tuple[int, ...]:
    """Return coefficients of det(xI-A), highest degree first."""

    order = len(matrix)
    power = [list(row) for row in matrix]
    traces = [0]
    for exponent in range(1, order + 1):
        if exponent > 1:
            power = matrix_multiply(power, matrix)
        traces.append(sum(power[index][index] for index in range(order)))
    elementary = [1]
    for degree in range(1, order + 1):
        numerator = sum(
            (-1) ** (power_index - 1)
            * elementary[degree - power_index]
            * traces[power_index]
            for power_index in range(1, degree + 1)
        )
        if numerator % degree:
            raise AssertionError("Newton division is not integral")
        elementary.append(numerator // degree)
    return tuple(
        [1]
        + [(-1) ** degree * elementary[degree] for degree in range(1, order + 1)]
    )


def local_gram(record: dict[str, object]) -> list[list[int]]:
    adjacency = [set() for _ in range(12)]
    for left, right in record["edges"]:
        adjacency[left].add(right)
        adjacency[right].add(left)
    result = [[0] * 12 for _ in range(12)]
    for left in range(12):
        for right in range(12):
            result[left][right] = (
                (12 if left == right else 0)
                - (1 if right in adjacency[left] else 0)
                + 2
                - (1 if left // 4 == right // 4 else 0)
                - len(adjacency[left] & adjacency[right])
            )
    return result


def adjacency_matrix(record: dict[str, object]) -> list[list[int]]:
    result = [[0] * 12 for _ in range(12)]
    for left, right in record["edges"]:
        result[left][right] = result[right][left] = 1
    return result


def fibre_preserving_automorphism_order(record: dict[str, object]) -> int:
    adjacency = [set() for _ in range(12)]
    for left, right in record["edges"]:
        adjacency[left].add(right)
        adjacency[right].add(left)
    original = CHECK.adjacency_code(adjacency)
    total = 0
    for perm0 in CHECK.PERMUTATIONS:
        for perm1 in CHECK.PERMUTATIONS:
            for perm2 in CHECK.PERMUTATIONS:
                relabel = tuple(perm0) + tuple(4 + i for i in perm1) + tuple(
                    8 + i for i in perm2
                )
                if CHECK.adjacency_code(adjacency, relabel) == original:
                    total += 1
    return total


def type_invariants(types: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    records = []
    for record in types:
        adjacency = adjacency_matrix(record)
        gram = local_gram(record)
        offdiagonal = Counter(
            gram[left][right]
            for left in range(12)
            for right in range(left + 1, 12)
        )
        category_support: Counter[str] = Counter()
        for left, right in itertools.combinations(range(12), 2):
            if gram[left][right] <= 0:
                continue
            fibre_left, fibre_right = left // 4, right // 4
            if fibre_left == fibre_right:
                category = f"A{fibre_left}"
            else:
                missing = ({0, 1, 2} - {fibre_left, fibre_right}).pop()
                category = f"B{missing}"
            category_support[category] += 1
        per_vertex = sorted(
            tuple(
                sorted(
                    Counter(
                        gram[vertex][other]
                        for other in range(12)
                        if other != vertex
                    ).items()
                )
            )
            for vertex in range(12)
        )
        records.append(
            {
                "type_index": record["type_index"],
                "C4": record["C4"],
                "adjacency_characteristic_polynomial": list(
                    characteristic_polynomial(adjacency)
                ),
                "local_gram_characteristic_polynomial": list(
                    characteristic_polynomial(gram)
                ),
                "local_gram_rank_F2": rank_f2(gram),
                "local_gram_offdiagonal_distribution": {
                    str(key): offdiagonal[key] for key in sorted(offdiagonal)
                },
                "positive_local_pair_support_by_category": {
                    key: category_support[key]
                    for key in sorted(category_support)
                },
                "local_gram_vertex_row_signatures": [
                    {str(key): value for key, value in signature}
                    for signature in per_vertex
                ],
                "fibre_preserving_automorphism_order": (
                    fibre_preserving_automorphism_order(record)
                ),
            }
        )
    return records


def signature_key(record: dict[str, object]) -> str:
    fields = {
        key: value
        for key, value in record.items()
        if key not in {"type_index"}
    }
    return json.dumps(fields, sort_keys=True, separators=(",", ":"))


def compatible_categories(categories: Sequence[str]) -> bool:
    fibre_totals = [0, 0, 0]
    for category in categories:
        kind = category[0]
        index = int(category[1])
        if kind == "A":
            fibre_totals[index] += 2
        elif kind == "B":
            for fibre in range(3):
                if fibre != index:
                    fibre_totals[fibre] += 1
        else:
            raise AssertionError("unknown category")
    return fibre_totals == [2, 2, 2]


def available_column_count(
    triple: Sequence[int],
    invariants: Sequence[dict[str, object]],
) -> int:
    supports = [
        invariants[index]["positive_local_pair_support_by_category"]
        for index in triple
    ]
    return sum(
        supports[0][category0]
        * supports[1][category1]
        * supports[2][category2]
        for category0 in supports[0]
        for category1 in supports[1]
        for category2 in supports[2]
        if compatible_categories((category0, category1, category2))
    )


def fibre_permutation_actions(
    types: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    code_to_type = {
        int(record["canonical_code_hex"], 16): record["type_index"]
        for record in types
    }
    actions = []
    for fibre_permutation in itertools.permutations(range(3)):
        mapping = []
        for record in types:
            adjacency = [set() for _ in range(12)]
            for left, right in record["edges"]:
                adjacency[left].add(right)
                adjacency[right].add(left)
            relabel = tuple(
                fibre_permutation[vertex // 4] * 4 + vertex % 4
                for vertex in range(12)
            )
            moved = [set() for _ in range(12)]
            for left in range(12):
                for right in adjacency[left]:
                    if left < right:
                        new_left, new_right = relabel[left], relabel[right]
                        moved[new_left].add(new_right)
                        moved[new_right].add(new_left)
            code = CHECK.canonical_component_code(moved)
            mapping.append(code_to_type[code])
        if sorted(mapping) != list(range(len(types))):
            raise AssertionError("fibre permutation does not act on types")
        actions.append(
            {
                "fibre_permutation": list(fibre_permutation),
                "type_mapping": mapping,
            }
        )
    return actions


def scan() -> dict[str, object]:
    CHECK.require_memory()
    census = CHECK.component_census()
    types = census["types"]
    invariants = type_invariants(types)
    groups: dict[str, list[int]] = defaultdict(list)
    for record in invariants:
        groups[signature_key(record)].append(record["type_index"])

    actions = fibre_permutation_actions(types)
    triples = list(itertools.combinations_with_replacement(range(len(types)), 3))
    triple_index = {triple: index for index, triple in enumerate(triples)}
    triple_orbit_representatives: dict[tuple[int, int, int], list[int]] = {}
    for triple in triples:
        orbit = {
            tuple(sorted(action["type_mapping"][index] for index in triple))
            for action in actions
        }
        representative = min(orbit)
        triple_orbit_representatives.setdefault(representative, []).append(
            triple_index[triple]
        )
    rank_distribution: Counter[int] = Counter()
    candidate_count_distribution: Counter[int] = Counter()
    survivors = []
    rejected = []
    for triple_index, triple in enumerate(triples):
        adjacency = CHECK.union_core([types[index] for index in triple])
        gram = CHECK.gram_target(adjacency)
        rank = rank_f2(gram)
        rank_distribution[rank] += 1
        record = {
            "triple_index": triple_index,
            "type_triple": list(triple),
            "C4_total": sum(types[index]["C4"] for index in triple),
            "target_gram_rank_F2": rank,
            "available_distinct_column_count": available_column_count(
                triple, invariants
            ),
        }
        candidate_count_distribution[
            record["available_distinct_column_count"]
        ] += 1
        if rank <= 30 and rank % 2 == 0:
            survivors.append(record)
        else:
            rejected.append(record)
    return {
        "format": "wave60-c3-invariant-scan-v1",
        "claim_label": "DERIVED",
        "component_type_count": len(types),
        "type_invariants": invariants,
        "coarse_signature_groups": [
            {
                "types": values,
                "size": len(values),
            }
            for values in sorted(groups.values())
        ],
        "coarse_signature_group_count": len(groups),
        "simultaneous_fibre_permutation_action": actions,
        "safe_triple_orbit_reduction": {
            "reason": (
                "simultaneously relabel the three vertices of the fixed "
                "triangle and hence the three fibres in every component; "
                "this is coordinate relabeling, not an assumed automorphism"
            ),
            "orbit_count": len(triple_orbit_representatives),
            "representatives": [
                {
                    "type_triple": list(representative),
                    "triple_indices": indices,
                    "orbit_size": len(indices),
                }
                for representative, indices in sorted(
                    triple_orbit_representatives.items()
                )
            ],
        },
        "triple_count": len(triples),
        "F2_necessary_condition": {
            "column_kernel": (
                "three fibre and three component indicators span dimension "
                "five and annihilate every column"
            ),
            "rank_B_upper_bound": 31,
            "alternating_gram": True,
            "target_gram_rank_must_be_even_and_at_most": 30,
        },
        "target_gram_rank_F2_distribution": {
            str(key): rank_distribution[key] for key in sorted(rank_distribution)
        },
        "available_distinct_column_count": {
            "formula": (
                "sum over the 21 compatible component/fibre category "
                "patterns of the product of the three positive local-pair "
                "support counts"
            ),
            "distribution": {
                str(key): candidate_count_distribution[key]
                for key in sorted(candidate_count_distribution)
            },
            "minimum": min(candidate_count_distribution),
            "maximum": max(candidate_count_distribution),
            "zero_candidate_triples": candidate_count_distribution.get(0, 0),
            "aligned_type_4_triple": available_column_count(
                (4, 4, 4), invariants
            ),
        },
        "survivor_count": len(survivors),
        "rejected_count": len(rejected),
        "survivors": survivors,
        "rejected": rejected,
        "free_memory_percent_at_end": CHECK.free_memory_percent(),
    }


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = scan()
    payload = canonical_bytes(result)
    if args.output:
        args.output.write_bytes(payload)
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
