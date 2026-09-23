#!/usr/bin/env python3
"""Exact verifier for a full order-seven deletion-deck witness.

The target is the necessary induced-subgraph count system for a hypothetical
``srg(99,14,1,2)`` at ``n3=705``.  This program deliberately uses only the
Python standard library.  It does not search for a witness.  Instead, it:

* independently enumerates every labeled and unlabeled locally admissible
  graph on seven vertices;
* independently canonicalizes the 208 isomorphism classes;
* reconstructs every six-vertex deletion deck;
* checks all 62 exact integer deck equations;
* checks the total number of seven-subsets;
* aligns the 19 published Hamiltonian types with canonical masks from the
  pinned source figure transcription and checks all 19 published counts.

Canonical graph masks use lexicographic edge order
``(0,1),(0,2),...,(n-2,n-1)``.  The canonical representative is the least
mask over all vertex permutations.

Passing this checker certifies only feasibility of these necessary count
equations.  A count vector is not a graph construction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from functools import lru_cache
from itertools import combinations, permutations
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ORDER = 7
N = 99
K = 14
LAMBDA = 1
MU = 2
N3 = 705

# This is a feasible published-Hamiltonian parameter value.  The formulas
# require h11 == 0 (mod 4) and 2*n3 <= h11 <= 4*n3.
H11 = 2820

EXPECTED_LABELED_SEVEN = 394_020
EXPECTED_UNLABELED_SEVEN = 208
EXPECTED_TOTAL_SEVEN = math.comb(N, 7)

# N_i -> canonical six-vertex mask.  This source-index alignment was frozen
# only after the independently checked Wave-21 reconstruction of the corrected
# M-to-N deletion table.  The present checker independently enumerates the
# canonical six-vertex universe and requires these 62 masks to be a bijection.
SOURCE_N_MASKS = (
    7100,
    1883,
    5941,
    1916,
    5907,
    1749,
    926,
    1881,
    1884,
    956,
    922,
    1880,
    920,
    5905,
    671,
    761,
    701,
    762,
    63,
    123,
    691,
    663,
    694,
    633,
    760,
    126,
    693,
    246,
    700,
    31,
    61,
    121,
    659,
    122,
    692,
    0,
    1,
    3,
    36,
    7,
    44,
    37,
    35,
    15,
    102,
    45,
    39,
    106,
    616,
    110,
    107,
    47,
    684,
    655,
    685,
    617,
    656,
    657,
    60,
    662,
    120,
    632,
)

# Exact values of n_1,...,n_62 at (n,k,n3)=(99,14,705), evaluated from
# Reimbayev's order-six formula table as independently transcribed and checked
# in Wave 21.
SIX_COUNTS = (
    1151,
    8316,
    705,
    1410,
    20085,
    90066,
    41580,
    164910,
    40875,
    81750,
    668100,
    209991,
    363120,
    2545,
    20790,
    83160,
    166320,
    163500,
    110880,
    831600,
    305390,
    748440,
    1499700,
    334050,
    584940,
    332640,
    749850,
    334050,
    1334790,
    66528,
    1995840,
    1704075,
    6981210,
    6314520,
    6479430,
    101286343,
    275382225,
    187696350,
    145263960,
    30351990,
    95998350,
    103443990,
    5072290,
    2328480,
    2287605,
    36097080,
    8816370,
    37016070,
    2454630,
    3573060,
    3823950,
    1704780,
    1462206,
    83160,
    334050,
    3573060,
    8283875,
    17011860,
    4991010,
    1370730,
    7612665,
    372810,
)

# The pinned Hamiltonian figure displays a perimeter C7 and labels panels
# 1,...,18.  Vertices here are read clockwise, with 0 at the top.  H_0 is the
# omitted bare C7.  Each tuple records only the extra chords visible in the
# corresponding panel.  Exact canonicalization below makes orientation and
# reflection irrelevant.
SOURCE_H_CHORDS: dict[int, tuple[tuple[int, int], ...]] = {
    0: (),
    1: ((6, 1),),
    2: ((5, 2),),
    3: ((0, 5), (0, 2)),
    4: ((0, 5), (0, 3)),
    5: ((0, 4), (0, 3)),
    6: ((6, 4), (1, 3)),
    7: ((6, 1), (5, 2)),
    8: ((6, 1), (0, 4)),
    9: ((6, 3), (1, 4)),
    10: ((6, 1), (6, 4), (1, 3)),
    11: ((0, 2), (0, 5), (1, 4)),
    12: ((0, 4), (0, 3), (6, 1)),
    13: ((0, 4), (0, 3), (5, 2)),
    14: ((0, 5), (0, 3), (4, 2)),
    15: ((6, 4), (1, 3), (5, 2)),
    16: ((6, 1), (5, 2), (0, 3)),
    17: ((6, 1), (5, 2), (6, 4), (1, 3)),
    18: ((6, 1), (5, 2), (0, 4), (0, 3)),
}

SOURCE_FREEZE = {
    "six_formula_artifact": {
        "path": "attempts/wave21-six-vertex-lp/exact-results.json",
        "sha256": "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b",
    },
    "hamiltonian_archive": {
        "url": "https://export.arxiv.org/e-print/2511.06572v1",
        "sha256": "10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a",
    },
    "hamiltonian_tex": {
        "archive_path": "Hamiltonian_Subgraphs_of_Order_Seven.tex",
        "sha256": "0b06fdc1c2951a344592c6af23abd133c4a8a68d717f199e7a0e2d7ceb909d0a",
        "formula_lines": "177-195",
    },
    "hamiltonian_figure": {
        "archive_path": "hamiltonian_7.jpg",
        "sha256": "e37f794e7765c947d3ea76104e9c4c61a00517b649d8b7bea9eb67644fe08a2e",
        "panels": "1-18; H_0 is the omitted bare C7",
    },
}


def edge_data(order: int) -> tuple[tuple[tuple[int, int], ...], dict[tuple[int, int], int]]:
    edges = tuple(combinations(range(order), 2))
    return edges, {edge: index for index, edge in enumerate(edges)}


@lru_cache(maxsize=None)
def permutation_bit_maps(order: int) -> tuple[tuple[int, ...], ...]:
    edges, positions = edge_data(order)
    return tuple(
        tuple(
            1 << positions[tuple(sorted((permutation[left], permutation[right])))]
            for left, right in edges
        )
        for permutation in permutations(range(order))
    )


def transform_mask(mask: int, bit_map: Sequence[int]) -> int:
    transformed = 0
    remaining = mask
    while remaining:
        bit = remaining & -remaining
        transformed |= bit_map[bit.bit_length() - 1]
        remaining -= bit
    return transformed


def canonical_mask(mask: int, order: int) -> int:
    return min(transform_mask(mask, bit_map) for bit_map in permutation_bit_maps(order))


def adjacency_rows(mask: int, order: int) -> tuple[int, ...]:
    edges, _ = edge_data(order)
    rows = [0] * order
    for index, (left, right) in enumerate(edges):
        if mask >> index & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def locally_admissible(mask: int, order: int) -> bool:
    """Necessary induced-subgraph condition for lambda=1 and mu=2."""

    edges, positions = edge_data(order)
    adjacency = adjacency_rows(mask, order)
    for left, right in edges:
        common = (adjacency[left] & adjacency[right]).bit_count()
        if mask >> positions[(left, right)] & 1:
            if common > LAMBDA:
                return False
        elif common > MU:
            return False
    return True


@lru_cache(maxsize=None)
def admissible_labeled_masks(order: int) -> tuple[int, ...]:
    edges, _ = edge_data(order)
    return tuple(
        mask
        for mask in range(1 << len(edges))
        if locally_admissible(mask, order)
    )


@lru_cache(maxsize=None)
def locally_admissible_classes(order: int) -> tuple[int, ...]:
    remaining = set(admissible_labeled_masks(order))
    classes: list[int] = []
    maps = permutation_bit_maps(order)
    while remaining:
        representative = next(iter(remaining))
        orbit = {transform_mask(representative, bit_map) for bit_map in maps}
        canonical = min(orbit)
        if canonical not in remaining:
            raise AssertionError("An isomorphism orbit was only partially removed")
        classes.append(canonical)
        remaining.difference_update(orbit)
    return tuple(sorted(classes))


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    old_edges, _ = edge_data(order)
    _, new_positions = edge_data(order - 1)
    remaining = [vertex for vertex in range(order) if vertex != deleted]
    relabel = {old: new for new, old in enumerate(remaining)}
    result = 0
    for edge_index, (left, right) in enumerate(old_edges):
        if left == deleted or right == deleted or not (mask >> edge_index & 1):
            continue
        edge = tuple(sorted((relabel[left], relabel[right])))
        result |= 1 << new_positions[edge]
    return result


def deck_vector(
    mask: int,
    order: int,
    lower_index: Mapping[int, int],
) -> tuple[int, ...]:
    result = [0] * len(lower_index)
    for deleted in range(order):
        card = canonical_mask(delete_vertex(mask, order, deleted), order - 1)
        result[lower_index[card]] += 1
    return tuple(result)


def c7_mask(chords: Iterable[tuple[int, int]]) -> int:
    _, positions = edge_data(7)
    edges = {
        tuple(sorted((vertex, (vertex + 1) % 7)))
        for vertex in range(7)
    }
    edges.update(tuple(sorted(edge)) for edge in chords)
    return sum(1 << positions[edge] for edge in edges)


@lru_cache(maxsize=None)
def source_h_masks() -> tuple[int, ...]:
    if set(SOURCE_H_CHORDS) != set(range(19)):
        raise AssertionError("Hamiltonian source transcription is incomplete")
    return tuple(
        canonical_mask(c7_mask(SOURCE_H_CHORDS[index]), 7)
        for index in range(19)
    )


@lru_cache(maxsize=None)
def independently_enumerated_hamiltonian_classes() -> tuple[int, ...]:
    """Enumerate through a fixed labeled C7 plus every subset of 14 chords."""

    edges, positions = edge_data(7)
    cycle_edges = {
        tuple(sorted((vertex, (vertex + 1) % 7)))
        for vertex in range(7)
    }
    cycle = sum(1 << positions[edge] for edge in cycle_edges)
    chord_positions = tuple(
        index for index, edge in enumerate(edges) if edge not in cycle_edges
    )
    classes = set()
    for subset in range(1 << len(chord_positions)):
        mask = cycle
        for offset, edge_index in enumerate(chord_positions):
            if subset >> offset & 1:
                mask |= 1 << edge_index
        if locally_admissible(mask, 7):
            classes.add(canonical_mask(mask, 7))
    return tuple(sorted(classes))


def published_hamiltonian_counts(n3: int, h11: int) -> tuple[int, ...]:
    """Evaluate the 19 formulas in arXiv:2511.06572v1 exactly."""

    if h11 % 4:
        raise ValueError("h11 must be divisible by four")
    common = N * K * (K - 2)
    b = common * (K - 4)
    numerators_over_four = (
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        common - 4 * n3 + h11,
        2 * h11,
        None,
        None,
        None,
        None,
        4 * n3 - h11,
    )
    for index in (12, 13, 18):
        assert numerators_over_four[index] is not None
        if numerators_over_four[index] % 4:
            raise ValueError(f"h_{index} is nonintegral")
    values = (
        b * (2 * K**2 - 30 * K + 133) // 14 - 10 * n3 - h11,
        common * (2 * K**2 - 25 * K + 68) // 2 + 16 * n3 + 3 * h11 // 2,
        b * (K - 8) + 12 * n3 + 5 * h11 // 2,
        b - 2 * n3 - h11 // 2,
        b - 4 * n3,
        b // 2 - h11 // 2,
        b - 8 * n3,
        b // 2 - 3 * h11 // 2,
        2 * b - 8 * n3 - 2 * h11,
        b - 2 * n3 - 3 * h11 // 2,
        2 * n3,
        h11,
        numerators_over_four[12] // 4,
        numerators_over_four[13] // 4,
        4 * n3,
        2 * n3,
        h11 - 2 * n3,
        common // 4 - n3,
        numerators_over_four[18] // 4,
    )
    if any(value < 0 for value in values):
        raise ValueError("published Hamiltonian counts are negative")
    return values


def rank_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    """Exact Gaussian rank over F_prime."""

    rows = [[value % prime for value in row] for row in matrix]
    row_count = len(rows)
    column_count = len(rows[0]) if rows else 0
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], -1, prime)
        rows[pivot_row] = [(value * inverse) % prime for value in rows[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or rows[row][column] == 0:
                continue
            factor = rows[row][column]
            rows[row] = [
                (value - factor * pivot_value) % prime
                for value, pivot_value in zip(rows[row], rows[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=1)
def build_model() -> dict[str, object]:
    classes6 = locally_admissible_classes(6)
    if len(classes6) != 62:
        raise AssertionError(f"Expected 62 six-vertex classes, got {len(classes6)}")
    if len(SOURCE_N_MASKS) != 62 or len(set(SOURCE_N_MASKS)) != 62:
        raise AssertionError("Source N-mask alignment is not bijective")
    if set(SOURCE_N_MASKS) != set(classes6):
        raise AssertionError("Source N masks do not cover the six-vertex census")

    classes7 = locally_admissible_classes(7)
    labeled7 = admissible_labeled_masks(7)
    if len(labeled7) != EXPECTED_LABELED_SEVEN:
        raise AssertionError(
            f"Expected {EXPECTED_LABELED_SEVEN} labeled masks, got {len(labeled7)}"
        )
    if len(classes7) != EXPECTED_UNLABELED_SEVEN:
        raise AssertionError(
            f"Expected {EXPECTED_UNLABELED_SEVEN} classes, got {len(classes7)}"
        )

    source_row = {mask: index for index, mask in enumerate(SOURCE_N_MASKS)}
    matrix_columns = tuple(deck_vector(mask, 7, source_row) for mask in classes7)
    if any(sum(column) != 7 for column in matrix_columns):
        raise AssertionError("A seven-vertex deletion deck does not have seven cards")
    matrix_rows = tuple(
        tuple(column[row] for column in matrix_columns)
        for row in range(62)
    )
    rhs = tuple(count * (N - 6) for count in SIX_COUNTS)
    if sum(rhs) != 7 * EXPECTED_TOTAL_SEVEN:
        raise AssertionError("Six-count total is inconsistent with seven-subset total")

    h_masks = source_h_masks()
    if len(set(h_masks)) != 19:
        raise AssertionError("Source Hamiltonian transcription has duplicate classes")
    independent_h = independently_enumerated_hamiltonian_classes()
    if len(independent_h) != 19 or set(h_masks) != set(independent_h):
        raise AssertionError(
            "Source Hamiltonian transcription does not cover the independent census"
        )
    if not set(h_masks).issubset(classes7):
        raise AssertionError("A source Hamiltonian type is outside the full census")

    ranks = {
        str(prime): rank_mod(matrix_rows, prime)
        for prime in (2, 3, 5, 7, 11)
    }
    if ranks != {"2": 48, "3": 57, "5": 61, "7": 61, "11": 62}:
        raise AssertionError(f"Unexpected finite-field ranks: {ranks}")

    return {
        "classes6": classes6,
        "classes7": classes7,
        "matrix_columns": matrix_columns,
        "matrix_rows": matrix_rows,
        "rhs": rhs,
        "h_masks": h_masks,
        "h_counts": published_hamiltonian_counts(N3, H11),
        "ranks": ranks,
    }


def validate_witness(payload: Mapping[str, object], model: Mapping[str, object]) -> dict[str, object]:
    if payload.get("schema_version") != 1:
        raise AssertionError("Unsupported witness schema")
    parameters = payload.get("parameters")
    expected_parameters = {
        "n": N,
        "k": K,
        "lambda": LAMBDA,
        "mu": MU,
        "n3": N3,
        "h11": H11,
    }
    if parameters != expected_parameters:
        raise AssertionError(f"Witness parameters differ: {parameters!r}")

    records = payload.get("classes")
    if not isinstance(records, list) or len(records) != EXPECTED_UNLABELED_SEVEN:
        raise AssertionError("Witness must contain exactly 208 class records")
    masks: list[int] = []
    counts: list[int] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or set(record) != {"canonical_mask", "count"}:
            raise AssertionError(f"Malformed class record {index}")
        mask = record["canonical_mask"]
        count = record["count"]
        if type(mask) is not int or type(count) is not int:
            raise AssertionError(f"Class record {index} does not contain integers")
        if count < 0:
            raise AssertionError(f"Class record {index} has a negative count")
        masks.append(mask)
        counts.append(count)

    classes7 = list(model["classes7"])
    if masks != classes7:
        raise AssertionError("Witness masks are not the complete ordered canonical census")

    matrix_rows = model["matrix_rows"]
    rhs = model["rhs"]
    row_sums = tuple(
        sum(coefficient * count for coefficient, count in zip(row, counts))
        for row in matrix_rows
    )
    bad_rows = [
        index + 1
        for index, (actual, expected) in enumerate(zip(row_sums, rhs))
        if actual != expected
    ]
    if bad_rows:
        raise AssertionError(f"Deletion-deck equations fail for N rows {bad_rows}")

    total = sum(counts)
    if total != EXPECTED_TOTAL_SEVEN:
        raise AssertionError(f"Seven-subset total is {total}, expected {EXPECTED_TOTAL_SEVEN}")

    count_by_mask = dict(zip(masks, counts))
    h_masks = model["h_masks"]
    h_counts = model["h_counts"]
    bad_h = [
        index
        for index, (mask, expected) in enumerate(zip(h_masks, h_counts))
        if count_by_mask[mask] != expected
    ]
    if bad_h:
        raise AssertionError(f"Published Hamiltonian counts fail for H indices {bad_h}")

    support = [
        {"canonical_mask": mask, "count": count}
        for mask, count in zip(masks, counts)
        if count
    ]
    return {
        "support_size": len(support),
        "zero_count_class_count": len(counts) - len(support),
        "total_count": total,
        "minimum_positive_count": min(record["count"] for record in support),
        "maximum_count": max(counts),
        "deck_rows_passed": len(rhs),
        "hamiltonian_types_passed": len(h_counts),
        "support_sha256": hashlib.sha256(
            json.dumps(support, sort_keys=True, separators=(",", ":")).encode("ascii")
        ).hexdigest(),
    }


def build_results(witness_path: Path) -> dict[str, object]:
    model = build_model()
    with witness_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    witness_checks = validate_witness(payload, model)
    h_masks = model["h_masks"]
    h_counts = model["h_counts"]
    try:
        witness_display_path = witness_path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        witness_display_path = witness_path.name
    return {
        "schema_version": 1,
        "claim_label": "DERIVED_INCONCLUSIVE",
        "scope": (
            "Feasibility at n3=705,h11=2820 of all 62 order-7 "
            "vertex-deletion deck equations and all 19 pinned published "
            "Hamiltonian-type counts"
        ),
        "parameters": {
            "n": N,
            "k": K,
            "lambda": LAMBDA,
            "mu": MU,
            "n3": N3,
            "h11": H11,
        },
        "source_freeze": SOURCE_FREEZE,
        "independent_census": {
            "order_6_unlabeled_classes": len(model["classes6"]),
            "order_7_labeled_masks": len(admissible_labeled_masks(7)),
            "order_7_unlabeled_classes": len(model["classes7"]),
            "criterion": (
                "inside common-neighbor count <=1 for each edge and <=2 "
                "for each nonedge"
            ),
            "canonicalization": "least mask over all vertex permutations",
            "hamiltonian_classes": len(independently_enumerated_hamiltonian_classes()),
        },
        "deletion_matrix": {
            "shape": [62, 208],
            "column_sum": 7,
            "finite_field_ranks": model["ranks"],
            "real_rank": 62,
            "real_rank_reason": "rank over F_11 is 62, the number of rows",
        },
        "hamiltonian_alignment": {
            "coordinate_convention": (
                "figure perimeter vertices 0,...,6 clockwise with 0 at top; "
                "listed edges are extra chords beyond the perimeter C7"
            ),
            "source_H_records": [
                {
                    "source_index": index,
                    "figure_panel": "omitted bare C7" if index == 0 else index,
                    "extra_chords": [list(edge) for edge in SOURCE_H_CHORDS[index]],
                    "canonical_mask": mask,
                    "published_count": count,
                }
                for index, (mask, count) in enumerate(zip(h_masks, h_counts))
            ],
            "source_H_to_canonical_mask": {
                str(index): mask for index, mask in enumerate(h_masks)
            },
            "source_H_counts": {
                str(index): count for index, count in enumerate(h_counts)
            },
            "figure_transcription_covers_independent_hamiltonian_census": True,
        },
        "witness": {
            "path": witness_display_path,
            "sha256": sha256_file(witness_path),
            **witness_checks,
        },
        "exact_checks": {
            "all_62_deletion_equations": "PASS",
            "seven_subset_total": EXPECTED_TOTAL_SEVEN,
            "all_19_published_hamiltonian_counts": "PASS",
            "nonnegative_integer_counts": "PASS",
        },
        "conclusion": {
            "deck_system_at_n3_705": "FEASIBLE",
            "published_hamiltonian_formulas_at_h11_2820": "COMPATIBLE_WITH_WITNESS",
            "new_lower_bound_beyond_n3_705": None,
            "graph_construction": False,
            "conway_99_status": "UNKNOWN",
            "warning": (
                "An integer subgraph-count witness for necessary equations is "
                "not an adjacency matrix and is not evidence that the target "
                "strongly regular graph exists."
            ),
        },
    }


def canonical_json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    default_witness = Path(__file__).with_name("witness.json")
    parser.add_argument("--witness", type=Path, default=default_witness)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args(argv)
    try:
        results = build_results(arguments.witness)
    except (AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    output = canonical_json_bytes(results)
    if arguments.output:
        arguments.output.write_bytes(output)
    else:
        sys.stdout.buffer.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
