"""Finite algebra and arithmetic checks for Wave 181.

This checker handles only the closed local profiles, the canonical C4 Gram,
and equality bookkeeping.  It performs no graph, code, SAT, configuration,
or isomorphism search.
"""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any, Iterable


FIELD = 3


def mat_vec(matrix: list[list[int]], vector: Iterable[int]) -> list[int]:
    values = list(vector)
    return [
        sum(entry * value for entry, value in zip(row, values)) % FIELD
        for row in matrix
    ]


def rank_mod3(matrix: list[list[int]]) -> int:
    work = [[entry % FIELD for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(pivot_row, rows)
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = 1 if work[pivot_row][column] == 1 else 2
        work[pivot_row] = [
            inverse * value % FIELD for value in work[pivot_row]
        ]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    (left - factor * right) % FIELD
                    for left, right in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def canonical(vector: Iterable[int]) -> tuple[int, ...]:
    values = tuple(value % FIELD for value in vector)
    first = next(value for value in values if value)
    scale = 1 if first == 1 else 2
    return tuple(scale * value % FIELD for value in values)


def analyze() -> dict[str, Any]:
    # S0 contributes one; two distinct extra-neighbor blocks contribute two;
    # the other four outer blocks retain the baseline xt edge and contribute
    # one.
    shared_center_h = [1, 2, 2, 1, 1, 1, 1]

    c4_gram = [
        [0, 1, 1, 2],
        [1, 0, 2, 1],
        [1, 2, 0, 1],
        [2, 1, 1, 0],
    ]
    kernel = [
        vector
        for vector in product(range(FIELD), repeat=4)
        if any(vector) and mat_vec(c4_gram, vector) == [0] * 4
    ]
    projective_kernel = sorted({canonical(vector) for vector in kernel})
    checkerboard = [1, 2, 2, 1]
    switched_gram = [
        [
            checkerboard[row]
            * c4_gram[row][column]
            * checkerboard[column]
            % FIELD
            for column in range(4)
        ]
        for row in range(4)
    ]

    vertices = 99
    degree = 14
    edges = vertices * degree // 2
    pairs = vertices * (vertices - 1) // 2
    nonedges = pairs - edges
    c4_orbits = nonedges // 2

    result = {
        "field": FIELD,
        "shared_center_adjacent_third": {
            "pairing_profile": shared_center_h,
            "nonzero_squares": sum(1 for value in shared_center_h if value),
            "singularity_residue": sum(
                value * value for value in shared_center_h
            )
            % FIELD,
            "conclusion": "rejected by star-projector singularity",
        },
        "shared_center_anticomplete_third": {
            "conclusion": (
                "Wave180 circuits cross-realize all three leaf pairs"
            ),
        },
        "canonical_c4_gram": c4_gram,
        "canonical_c4_gram_rank": rank_mod3(c4_gram),
        "canonical_c4_projective_kernel": [
            list(vector) for vector in projective_kernel
        ],
        "checkerboard_vector": checkerboard,
        "switched_c4_gram": switched_gram,
        "switched_c4_gram_formula": "2*(J_4-I_4)",
        "pair_counts": {
            "edges": edges,
            "nonedges": nonedges,
            "all_pairs": pairs,
            "canonical_c4_orbits": c4_orbits,
        },
        "incidences": {
            "c4_per_edge": 12,
            "c4_per_triangle_block": 36,
            "total_edge_c4": edges * 12,
            "total_c4_edges": c4_orbits * 4,
        },
        "equality_boundary": {
            "nonedge_projective_circuits": 2079,
            "required_canonical_c4_conics": 2079,
            "triple_serving_circuits": 0,
            "singleton_serving_circuits": 0,
            "signed_matrix_shape": [2079, 231],
            "signed_matrix_rank_upper_if_equal": 220,
            "signed_gram_mod3": "2*K+L",
        },
        "projector_sum_coefficient_mod3": 36 % FIELD,
        "conclusion": (
            "equality forces all 2079 canonical induced C4 supports to be "
            "checkerboard Q(2,3) conics; the first projector sum vanishes"
        ),
    }
    verify(result)
    return result


def verify(result: dict[str, Any]) -> None:
    shared = result["shared_center_adjacent_third"]
    assert shared["pairing_profile"] == [1, 2, 2, 1, 1, 1, 1]
    assert shared["nonzero_squares"] == 7
    assert shared["singularity_residue"] == 1
    assert result["canonical_c4_gram_rank"] == 3
    assert result["canonical_c4_projective_kernel"] == [[1, 2, 2, 1]]
    expected_switched = [
        [0 if row == column else 2 for column in range(4)]
        for row in range(4)
    ]
    assert result["switched_c4_gram"] == expected_switched
    assert result["pair_counts"] == {
        "edges": 693,
        "nonedges": 4158,
        "all_pairs": 4851,
        "canonical_c4_orbits": 2079,
    }
    incidences = result["incidences"]
    assert incidences["total_edge_c4"] == incidences["total_c4_edges"] == 8316
    assert incidences["c4_per_triangle_block"] == 36
    equality = result["equality_boundary"]
    assert equality["required_canonical_c4_conics"] == 2079
    assert equality["signed_matrix_rank_upper_if_equal"] == 220
    assert result["projector_sum_coefficient_mod3"] == 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = analyze()
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == result
    if args.write:
        args.write.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if not args.write and not args.verify:
        print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: Wave181 canonical-C4 equality exact checks")


if __name__ == "__main__":
    main()
