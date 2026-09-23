#!/usr/bin/env python3
"""Exact replay of the Wave151 partial binary incidence factor.

The certificate realizes the first two 12-row groups of the Wave149 Gram
matrix.  It does not contain a third group or the residual adjacency block,
so the full finite subproblem remains UNKNOWN.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE149_RESULT = ROOT / "attempts/wave149-terwilliger-triple/exact-results.json"
WAVE149_MANIFEST = ROOT / "attempts/wave149-terwilliger-triple/package-manifest.sha256"
EXPECTED_WAVE149_RESULT_SHA256 = (
    "6fed4da32fbeefce54d1802136dc8c9a328f112bb0f295a86230f0e6175f5ee6"
)
EXPECTED_WAVE149_MANIFEST_SHA256 = (
    "84bea47182b6a59b69f5df29d4f7a8cdf71bff63cfbc47947b1e65013d09d70f"
)

Q1 = [
    39, 54, 27, 45, 46, 32, 28, 55, 6, 22, 58, 47, 48, 24, 33,
    20, 18, 51, 29, 37, 41, 4, 19, 43, 13, 50, 0, 52, 5, 56,
    38, 59, 36, 3, 14, 11, 17, 34, 23, 1, 49, 16, 30, 10, 8,
    15, 53, 35, 57, 21, 26, 2, 9, 40, 44, 7, 31, 42, 12, 25,
]

# Best retained discovery point for the third group with Q1 fixed.  It is not
# a certificate: its exact squared residual is 80.
NEAR_Q2 = [
    43, 28, 23, 48, 11, 59, 54, 21, 39, 6, 50, 33, 46, 51, 41,
    10, 38, 52, 3, 25, 4, 45, 56, 37, 9, 55, 18, 12, 57, 5,
    44, 8, 36, 14, 27, 15, 17, 7, 35, 20, 31, 22, 26, 29, 0,
    58, 16, 30, 13, 40, 49, 32, 34, 19, 24, 47, 42, 53, 1, 2,
]


def demand(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def zero(rows: int, columns: int) -> list[list[int]]:
    return [[0] * columns for _ in range(rows)]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*matrix)]


def multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def subtract(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [left[i][j] - right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def squared_norm(matrix: list[list[int]]) -> int:
    return sum(value * value for row in matrix for value in row)


def edge_universe() -> list[tuple[int, int]]:
    matching = {
        tuple(sorted((vertex, vertex ^ 1))) for vertex in range(12)
    }
    return [
        edge for edge in itertools.combinations(range(12), 2)
        if edge not in matching
    ]


def incidence(edges: list[tuple[int, int]]) -> list[list[int]]:
    result = zero(12, len(edges))
    for column, edge in enumerate(edges):
        for vertex in edge:
            result[vertex][column] = 1
    return result


def permute_columns(
    matrix: list[list[int]],
    permutation: list[int],
) -> list[list[int]]:
    return [[row[column] for column in permutation] for row in matrix]


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def build_result() -> dict[str, Any]:
    demand(hashlib.sha256(WAVE149_RESULT.read_bytes()).hexdigest()
           == EXPECTED_WAVE149_RESULT_SHA256, "Wave149 result drift")
    demand(hashlib.sha256(WAVE149_MANIFEST.read_bytes()).hexdigest()
           == EXPECTED_WAVE149_MANIFEST_SHA256, "Wave149 manifest drift")
    parent = json.loads(WAVE149_RESULT.read_text(encoding="utf-8"))
    gram = parent["minimal_surviving_witness"]["gram_rows"]
    target_00 = [row[:12] for row in gram[:12]]
    target_01 = [row[12:24] for row in gram[:12]]
    target_02 = [row[24:36] for row in gram[:12]]
    target_11 = [row[12:24] for row in gram[12:24]]
    target_12 = [row[24:36] for row in gram[12:24]]
    target_22 = [row[24:36] for row in gram[24:36]]
    demand(target_00 == target_11 == target_22,
           "diagonal Gram blocks differ")
    demand(target_01 == target_02, "first two cross targets differ")

    edges = edge_universe()
    demand(len(edges) == 60, "nonmatching edge universe is not 60")
    c0 = incidence(edges)
    demand(sorted(Q1) == list(range(60)), "Q1 is not a permutation")
    c1 = permute_columns(c0, Q1)
    demand(multiply(c0, transpose(c0)) == target_00, "C0 Gram failure")
    demand(multiply(c1, transpose(c1)) == target_11, "C1 Gram failure")
    demand(multiply(c0, transpose(c1)) == target_01, "C0/C1 cross failure")
    for block in (c0, c1):
        demand(all(sum(row) == 10 for row in block), "row weight is not 10")
        demand(all(sum(block[row][column] for row in range(12)) == 2
                   for column in range(60)), "column group weight is not 2")

    demand(sorted(NEAR_Q2) == list(range(60)), "near Q2 is not a permutation")
    c2_near = permute_columns(c0, NEAR_Q2)
    near_residual_02 = subtract(
        multiply(c0, transpose(c2_near)), target_02
    )
    near_residual_12 = subtract(
        multiply(c1, transpose(c2_near)), target_12
    )
    near_score = squared_norm(near_residual_02) + squared_norm(near_residual_12)
    demand(near_score == 80, "retained near-Q2 residual differs")

    partial = c0 + c1
    return {
        "format": "wave151-triangle-root-binary-factor-v1",
        "role": "proof_b",
        "claim_label": "VERIFIED_PARTIAL_CONSTRUCTION_UNKNOWN_FULL",
        "scope": (
            "binary factorization of the fixed Wave149 prism-free 36x36 Gram "
            "matrix, followed conditionally by the residual 60-vertex block"
        ),
        "frozen_inputs_sha256": {
            "attempts/wave149-terwilliger-triple/package-manifest.sha256":
                EXPECTED_WAVE149_MANIFEST_SHA256,
            "attempts/wave149-terwilliger-triple/exact-results.json":
                EXPECTED_WAVE149_RESULT_SHA256,
        },
        "finite_problem": {
            "C_shape": [36, 60],
            "C_row_sum": 10,
            "C_column_ones_per_12_row_group": 2,
            "target_gram_sha256":
                parent["minimal_surviving_witness"]["gram_sha256"],
            "D_shape": [60, 60],
            "D_symmetric_zero_diagonal": True,
            "D_degree": 8,
        },
        "exact_partial_factor": {
            "groups_constructed": 2,
            "shape": [24, 60],
            "edge_columns": [list(edge) for edge in edges],
            "Q1": Q1,
            "binary_matrix_sha256": canonical_digest(partial),
            "all_row_sums_10": True,
            "all_group_column_sums_2": True,
            "diagonal_and_G01_blocks_replayed": True,
        },
        "third_group_search": {
            "status": "UNKNOWN",
            "fixed_Q1_exact_z3_status": "UNSAT_WITHOUT_EXPORTED_PROOF",
            "fixed_Q1_status_is_not_global": True,
            "fixed_Q1_status_used_as_certificate": False,
            "best_retained_Q2_permutation": NEAR_Q2,
            "best_exact_squared_residual": near_score,
            "unrestricted_joint_best_squared_residual": 108,
        },
        "residual_D_layer": {
            "status": "NOT_REACHED",
            "reason": "no complete 36x60 C certificate",
            "mixed_identity": (
                "C_i D=2J-C_i-M_iC_i-F_ijC_j-F_ikC_k"
            ),
            "quadratic_identity": (
                "D^2=12I-D+2J-sum_i C_i^T C_i"
            ),
        },
        "conclusion": {
            "complete_C_factor": "UNKNOWN",
            "complete_D_factor": "NOT_REACHED",
            "forces_a_prism": False,
            "strict_n3_upper_bound": "NOT_IMPROVED",
            "graph_realization": False,
            "conway_99": "UNKNOWN",
        },
        "limitations": [
            "A 24x60 partial factor does not imply a 36x60 factor.",
            "The Z3 UNSAT status concerns only the displayed Q1 and has no exported proof.",
            "No solver-negative result is promoted.",
            "No automorphism of a putative graph is assumed.",
        ],
    }


def verify_payload(payload: dict[str, Any]) -> None:
    demand(payload == build_result(), "stored Wave151 result differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    if arguments.verify:
        verify_payload(json.loads(arguments.verify.read_text(encoding="utf-8")))
        print(json.dumps({"verification": "PASS", "path": str(arguments.verify)}))
        return 0
    result = build_result()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
