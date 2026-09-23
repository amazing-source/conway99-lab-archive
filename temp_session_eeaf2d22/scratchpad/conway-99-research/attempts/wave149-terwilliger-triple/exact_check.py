#!/usr/bin/env python3
"""Exact triangle-root Terwilliger/Gram projection for Conway-99.

This checker uses only the Python standard library.  It constructs a
prism-free local permutation system around one triangle and proves that the
resulting 36x36 Gram matrix passes entrywise nonnegativity, exact PSD, and
rank constraints.  It therefore certifies a null result for this projection,
not a graph or endpoint witness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE21_RESULT = ROOT / "attempts/wave21-six-vertex-lp/exact-results.json"
EXPECTED_WAVE21_SHA256 = (
    "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b"
)
ORDER = 12


def demand(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def zero_matrix(rows: int, columns: int) -> list[list[int]]:
    return [[0 for _ in range(columns)] for _ in range(rows)]


def identity(order: int) -> list[list[int]]:
    result = zero_matrix(order, order)
    for i in range(order):
        result[i][i] = 1
    return result


def all_ones(order: int) -> list[list[int]]:
    return [[1] * order for _ in range(order)]


def permutation_matrix(permutation: list[int]) -> list[list[int]]:
    result = zero_matrix(len(permutation), len(permutation))
    for row, column in enumerate(permutation):
        result[row][column] = 1
    return result


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*matrix)]


def add(*matrices: list[list[int]]) -> list[list[int]]:
    return [
        [sum(matrix[i][j] for matrix in matrices) for j in range(len(matrices[0][0]))]
        for i in range(len(matrices[0]))
    ]


def scale(coefficient: int, matrix: list[list[int]]) -> list[list[int]]:
    return [[coefficient * value for value in row] for row in matrix]


def multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def block_matrix(blocks: list[list[list[list[int]]]]) -> list[list[int]]:
    result = []
    for block_row in blocks:
        for local_row in range(len(block_row[0])):
            result.append(
                sum((block[local_row] for block in block_row), [])
            )
    return result


def canonical_digest(value: Any) -> str:
    rendered = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(rendered).hexdigest()


def character_certificate() -> list[dict[str, int]]:
    """Exact simultaneous-character PSD certificate.

    M and P are commuting involutions.  On a joint character with eigenvalues
    m,p and J-eigenvalue j, the 3x3 group-index matrix is

        [[d,a,a],[a,d,b],[a,b,d]].

    It splits into scalar d-b and a 2x2 block with determinant shown below.
    """

    records = []
    cases = [
        (1, 1, 12, 1),
        (1, 1, 0, 2),
        (1, -1, 0, 3),
        (-1, 1, 0, 3),
        (-1, -1, 0, 3),
    ]
    for m_value, p_value, j_value, multiplicity in cases:
        d_value = 9 - m_value + j_value
        a_value = 2 * j_value - 1 - 2 * m_value - p_value
        b_value = 2 * j_value - 1 - p_value - 2 * m_value * p_value
        antisymmetric = d_value - b_value
        determinant = d_value * (d_value + b_value) - 2 * a_value**2
        demand(d_value >= 0 and d_value + b_value >= 0,
               "negative 2x2 diagonal")
        demand(antisymmetric >= 0 and determinant >= 0,
               "PSD character condition failed")
        symmetric_rank = 2 if determinant > 0 else int(
            d_value != 0 or a_value != 0 or d_value + b_value != 0
        )
        records.append(
            {
                "m": m_value,
                "p": p_value,
                "j": j_value,
                "multiplicity": multiplicity,
                "d": d_value,
                "a": a_value,
                "b": b_value,
                "antisymmetric_eigenvalue": antisymmetric,
                "symmetric_2x2_determinant": determinant,
                "rank_contribution_per_character": (
                    int(antisymmetric > 0) + symmetric_rank
                ),
            }
        )
    demand(sum(record["multiplicity"] for record in records) == ORDER,
           "character multiplicities do not sum to 12")
    return records


def build_result() -> dict[str, Any]:
    demand(hashlib.sha256(WAVE21_RESULT.read_bytes()).hexdigest()
           == EXPECTED_WAVE21_SHA256, "Wave21 input drift")
    wave21 = json.loads(WAVE21_RESULT.read_text(encoding="utf-8"))
    prism_formula = wave21["formula_tables"]["six"]["1"]
    demand(
        prism_formula == {
            "constant": "1386",
            "n3_coefficient": "-1/3",
            "h11_coefficient": "0",
        },
        "prism-count formula drift",
    )

    i_matrix = identity(ORDER)
    j_matrix = all_ones(ORDER)
    matching_permutation = [
        value
        for pair in range(0, ORDER, 2)
        for value in (pair + 1, pair)
    ]
    shift_permutation = [(value + 6) % ORDER for value in range(ORDER)]
    m_matrix = permutation_matrix(matching_permutation)
    p_matrix = permutation_matrix(shift_permutation)
    demand(multiply(m_matrix, m_matrix) == i_matrix, "M is not an involution")
    demand(multiply(p_matrix, p_matrix) == i_matrix, "P is not an involution")
    demand(multiply(m_matrix, p_matrix) == multiply(p_matrix, m_matrix),
           "M and P do not commute")
    demand(sum(p_matrix[i][i] for i in range(ORDER)) == 0,
           "rooted prism count is not zero")

    diagonal = add(scale(9, i_matrix), scale(-1, m_matrix), j_matrix)
    cross_01 = add(
        scale(2, j_matrix),
        scale(-1, i_matrix),
        scale(-2, m_matrix),
        scale(-1, p_matrix),
    )
    cross_02 = [row[:] for row in cross_01]
    cross_12 = add(
        scale(2, j_matrix),
        scale(-1, i_matrix),
        scale(-1, p_matrix),
        scale(-2, multiply(m_matrix, p_matrix)),
    )
    gram = block_matrix(
        [
            [diagonal, cross_01, cross_02],
            [transpose(cross_01), diagonal, cross_12],
            [transpose(cross_02), transpose(cross_12), diagonal],
        ]
    )
    demand(gram == transpose(gram), "Gram matrix is not symmetric")
    demand(min(map(min, gram)) >= 0, "negative triple-intersection entry")
    demand(max(map(max, gram)) <= 10, "unexpected Gram entry")
    demand(all(gram[i][i] == 10 for i in range(36)),
           "incidence row size is not 10")
    demand(all(sum(row) == 60 for row in gram),
           "Gram row sums are not 60")

    characters = character_certificate()
    rank = sum(
        record["multiplicity"]
        * record["rank_contribution_per_character"]
        for record in characters
    )
    demand(rank == 32 and rank <= 60, "exact rank certificate failed")
    demand(sum(
        3 * record["d"] * record["multiplicity"]
        for record in characters
    ) == sum(gram[i][i] for i in range(36)), "character trace mismatch")

    return {
        "format": "wave149-triangle-root-terwilliger-v1",
        "role": "proof_b",
        "claim_label": "VERIFIED_NULL_PROJECTION",
        "scope": (
            "triangle-root permutation and first 36x36 Terwilliger Gram "
            "projection at the prism-free n3=4158 endpoint"
        ),
        "parameters": {
            "srg": [99, 14, 1, 2],
            "root_triangle_count": 231,
            "root_partition_sizes": [12, 12, 12, 60],
            "n3_endpoint": 4158,
            "prism_count_formula": "N1=1386-n3/3",
            "endpoint_prism_count": 0,
        },
        "derived_block_structure": {
            "Ai_internal": "perfect matching M_i",
            "Ai_Aj": "perfect matching F_ij",
            "Ai_B": "12x60 binary, row sum 10, column contribution 2 per Ai",
            "B_internal": "8-regular simple graph",
            "gram_diagonal": "C_i C_i^T = 9I - M_i + J",
            "gram_cross": (
                "C_i C_j^T = 2J-F_ij-M_iF_ij-F_ijM_j-F_ikF_kj"
            ),
            "rooted_prisms": "trace(F_01 F_12 F_20)",
        },
        "minimal_surviving_witness": {
            "M0_M1_M2_permutation": matching_permutation,
            "F01_permutation": list(range(ORDER)),
            "F02_permutation": list(range(ORDER)),
            "F12_permutation": shift_permutation,
            "rooted_prism_fixed_points": 0,
            "gram_order": 36,
            "gram_minimum_entry": min(map(min, gram)),
            "gram_maximum_entry": max(map(max, gram)),
            "gram_rank": rank,
            "available_factor_dimension": 60,
            "gram_sha256": canonical_digest(gram),
            "gram_rows": gram,
            "exact_psd_character_certificate": characters,
        },
        "conclusion": {
            "forces_a_prism": False,
            "strict_n3_upper_bound": "NOT_IMPROVED",
            "first_terwilliger_psd_projection": "EXACTLY_FEASIBLE",
            "binary_incidence_factor": "UNKNOWN",
            "graph_realization": False,
            "conway_99": "UNKNOWN",
        },
        "next_missing_compatibility": [
            (
                "Factor the displayed integer Gram matrix as C C^T with C "
                "binary 36x60, each row sum 10, and each column containing "
                "exactly two ones in each 12-row group."
            ),
            (
                "Find a symmetric zero-diagonal 8-regular 60x60 matrix D "
                "satisfying C_i D = 2J-C_i-M_iC_i-F_ijC_j-F_ikC_k."
            ),
            (
                "Enforce D^2 = 12I-D+2J-sum_i C_i^T C_i and then compatibility "
                "between different root triangles."
            ),
        ],
        "limitations": [
            "The Gram witness is not a binary incidence factor.",
            "It is local to one abstract root triangle.",
            "PSD feasibility does not imply a graph exists.",
            "No automorphism of a putative graph is assumed.",
        ],
        "frozen_inputs_sha256": {
            "attempts/wave21-six-vertex-lp/exact-results.json":
                EXPECTED_WAVE21_SHA256,
        },
    }


def verify_payload(payload: dict[str, Any]) -> None:
    rebuilt = build_result()
    demand(payload == rebuilt, "stored exact result differs from reconstruction")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    if arguments.verify is not None:
        payload = json.loads(arguments.verify.read_text(encoding="utf-8"))
        verify_payload(payload)
        print(json.dumps({"verification": "PASS", "path": str(arguments.verify)}))
        return 0
    result = build_result()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output is not None:
        arguments.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
