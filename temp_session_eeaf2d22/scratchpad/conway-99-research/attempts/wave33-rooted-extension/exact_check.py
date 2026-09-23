#!/usr/bin/env python3
"""Exact Wave 33 rooted-extension consequences.

Standard library only.  Starting from the independently verified Wave 32
signed Fano-complement support, this checker derives the full three-cell
partition, the O-Q design constraints, the induced O-graph spectrum, exact
small-cycle counts, and a necessary-and-sufficient binary block-matrix
extension criterion.

It does not find or exclude a full extension.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
FROZEN_INPUTS = {
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "verification/wave33-continuation-protocol.md":
        "b98b6bb8228b54b67cd949ee1bf6eb05ebd6ebe74f1cbc9e49b041a55e2d2fe6",
    "agents/2026-07-24-wave32-rooted-proof.md":
        "04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0",
    "attempts/wave32-rooted-vector/exact-results.json":
        "9fa31703b5c4721476b1b88f217d7455615c0d92c0d6db7f150abadfc069c2a0",
    "verification/wave32-rooted-vector/audit.md":
        "36d83232d82e30205e0aefa30aedff0a517de1edb0adbaa54575ea68d04ce1a5",
    "verification/wave32-rooted-vector/independent-results.json":
        "4ed239e997e4485abdab4e26a2e28e2a981b6fff069c4d926ccff3d2241dbe6f",
}


Matrix = list[list[int]]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True)
        .encode("utf-8")
        + b"\n"
    )


def hash_payload(payload: object) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    observed = {
        relative: sha256_file(ROOT / relative)
        for relative in FROZEN_INPUTS
    }
    if observed != FROZEN_INPUTS:
        raise AssertionError(
            "frozen input mismatch\n"
            f"expected={FROZEN_INPUTS}\n"
            f"observed={observed}"
        )
    return observed


def zeros(rows: int, columns: int) -> Matrix:
    return [[0 for _ in range(columns)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zeros(size, size)
    for index in range(size):
        result[index][index] = 1
    return result


def all_ones(rows: int, columns: int) -> Matrix:
    return [[1 for _ in range(columns)] for _ in range(rows)]


def transpose(matrix: Sequence[Sequence[int]]) -> Matrix:
    if not matrix:
        return []
    return [list(column) for column in zip(*matrix)]


def matmul(
    left: Sequence[Sequence[int]],
    right: Sequence[Sequence[int]],
) -> Matrix:
    if not left or not right:
        raise ValueError("matrix factors must be nonempty")
    right_t = transpose(right)
    if len(left[0]) != len(right):
        raise ValueError("matrix factor dimensions do not match")
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def matadd(*matrices: Sequence[Sequence[int]]) -> Matrix:
    if not matrices:
        raise ValueError("at least one matrix is required")
    rows = len(matrices[0])
    columns = len(matrices[0][0])
    if any(
        len(matrix) != rows
        or any(len(row) != columns for row in matrix)
        for matrix in matrices
    ):
        raise ValueError("matrix dimensions do not match")
    return [
        [sum(matrix[i][j] for matrix in matrices) for j in range(columns)]
        for i in range(rows)
    ]


def matscale(matrix: Sequence[Sequence[int]], scalar: int) -> Matrix:
    return [[scalar * value for value in row] for row in matrix]


def matrix_rank(matrix: Sequence[Sequence[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(pivot_row, rows)
                if work[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                a - factor * b
                for a, b in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def degree_histogram(matrix: Sequence[Sequence[int]]) -> dict[str, int]:
    degrees = [sum(row) for row in matrix]
    return {
        str(degree): degrees.count(degree)
        for degree in sorted(set(degrees))
    }


def fano_complement() -> Matrix:
    """Canonical 2-(7,4,2) incidence from the Wave 32 package."""
    fano_lines = (
        (0, 1, 2),
        (0, 3, 4),
        (0, 5, 6),
        (1, 3, 5),
        (1, 4, 6),
        (2, 3, 6),
        (2, 4, 5),
    )
    return [
        [0 if point in fano_lines[line] else 1 for line in range(7)]
        for point in range(7)
    ]


def build_fixed_support() -> dict[str, object]:
    cross = fano_complement()
    support_adjacency = zeros(14, 14)
    for positive in range(7):
        for negative in range(7):
            if cross[positive][negative]:
                support_adjacency[positive][7 + negative] = 1
                support_adjacency[7 + negative][positive] = 1

    labels: list[tuple[int, int, int, str]] = []
    for positive in range(7):
        for negative in range(7):
            multiplicity = 1 if cross[positive][negative] else 2
            label_type = (
                "support_edge_completion"
                if multiplicity == 1
                else "support_nonedge_completion"
            )
            for copy in range(multiplicity):
                labels.append((positive, negative, copy, label_type))

    support_to_o = zeros(14, len(labels))
    for index, (positive, negative, _copy, _kind) in enumerate(labels):
        support_to_o[positive][index] = 1
        support_to_o[7 + negative][index] = 1

    if len(labels) != 70:
        raise AssertionError("O-label count drifted")
    if degree_histogram(support_adjacency) != {"4": 14}:
        raise AssertionError("support graph is not 4-regular")
    if [sum(row) for row in support_to_o] != [10] * 14:
        raise AssertionError("support-to-O row sums drifted")
    if [sum(column) for column in transpose(support_to_o)] != [2] * 70:
        raise AssertionError("support-to-O column sums drifted")

    return {
        "cross": cross,
        "A_S": support_adjacency,
        "F": support_to_o,
        "labels": labels,
    }


def fixed_support_identities() -> dict[str, object]:
    fixed = build_fixed_support()
    support_adjacency = fixed["A_S"]
    support_to_o = fixed["F"]
    assert isinstance(support_adjacency, list)
    assert isinstance(support_to_o, list)
    left = matadd(
        matmul(support_adjacency, support_adjacency),
        matmul(support_to_o, transpose(support_to_o)),
    )
    right = matadd(
        matscale(identity(14), 12),
        matscale(support_adjacency, -1),
        matscale(all_ones(14, 14), 2),
    )
    if left != right:
        raise AssertionError("fixed S-S block identity failed")

    signed = [[1] for _ in range(7)] + [[-1] for _ in range(7)]
    if matmul(support_adjacency, signed) != matscale(signed, -4):
        raise AssertionError("signed support vector lost eigenvalue -4")
    if matmul(transpose(support_to_o), signed) != zeros(70, 1):
        raise AssertionError("O labels are not sign-balanced")

    gram = matmul(support_to_o, transpose(support_to_o))
    return {
        "fixed_SS_block_identity": True,
        "support_adjacency_sha256": hash_payload(support_adjacency),
        "support_to_O_sha256": hash_payload(support_to_o),
        "O_label_sha256": hash_payload(fixed["labels"]),
        "support_spectrum": {
            "4": 1,
            "-4": 1,
            "sqrt(2)": 6,
            "-sqrt(2)": 6,
        },
        "rank_F": matrix_rank(support_to_o),
        "rank_FFt": matrix_rank(gram),
        "signed_minus_four_vector_in_kernel_Ft": True,
        "O_label_types": {
            "support_edge_completion": sum(
                label[3] == "support_edge_completion"
                for label in fixed["labels"]
            ),
            "support_nonedge_completion": sum(
                label[3] == "support_nonedge_completion"
                for label in fixed["labels"]
            ),
        },
    }


def quotient_characteristic_check(quotient: Matrix) -> None:
    q2 = matmul(quotient, quotient)
    q3 = matmul(q2, quotient)
    polynomial = matadd(
        q3,
        matscale(q2, -13),
        matscale(quotient, -26),
        matscale(identity(3), 168),
    )
    if polynomial != zeros(3, 3):
        raise AssertionError("quotient characteristic polynomial failed")
    if sum(quotient[i][i] for i in range(3)) != 13:
        raise AssertionError("quotient trace drifted")


def equitable_partition() -> dict[str, object]:
    # S has size 14.  O vertices have two S-neighbors; Q vertices have none.
    # Count two-walks from Q and O into S.
    q_to_s_two_walks = 14 * 2
    q_to_o = q_to_s_two_walks // 2
    q_to_q = 14 - q_to_o
    o_to_s_two_walks = 2 * 1 + 12 * 2
    o_to_o = (o_to_s_two_walks - 2 * 4) // 2
    o_to_q = 14 - 2 - o_to_o
    quotient = [
        [4, 10, 0],
        [2, o_to_o, o_to_q],
        [0, q_to_o, q_to_q],
    ]
    quotient_characteristic_check(quotient)

    if quotient != [[4, 10, 0], [2, 9, 3], [0, 14, 0]]:
        raise AssertionError("equitable quotient drifted")
    if 14 * 10 != 70 * 2 or 70 * 3 != 15 * 14:
        raise AssertionError("partition edge balance failed")

    hostile_mu = 3
    hostile_q_to_o = (14 * hostile_mu) // 2
    if hostile_q_to_o <= 14:
        raise AssertionError("mu=3 hostile mutation should exceed degree")

    return {
        "cell_names": ["S_signed_support", "O_support_adjacent", "Q_support_free"],
        "cell_sizes": [14, 70, 15],
        "quotient": quotient,
        "quotient_characteristic_polynomial": "(x-14)(x-3)(x+4)",
        "quotient_spectrum": {"14": 1, "3": 1, "-4": 1},
        "Q_is_independent": True,
        "two_walk_arithmetic": {
            "Q_to_S": {
                "target": q_to_s_two_walks,
                "contribution_per_O_neighbor": 2,
                "degree_into_O": q_to_o,
            },
            "O_to_S": {
                "target": o_to_s_two_walks,
                "support_neighbor_contribution": 8,
                "contribution_per_O_neighbor": 2,
                "degree_into_O": o_to_o,
                "degree_into_Q": o_to_q,
            },
        },
        "hostile_mu_3": {
            "implied_Q_to_O_degree": hostile_q_to_o,
            "available_total_degree": 14,
            "passes": False,
        },
    }


def integer_partitions(
    total: int,
    minimum: int,
    maximum: int | None = None,
) -> Iterable[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    if maximum is None:
        maximum = total
    for first in range(min(maximum, total), minimum - 1, -1):
        for rest in integer_partitions(total - first, minimum, first):
            yield (first,) + rest


def design_consequences() -> dict[str, object]:
    half_cycle_partitions = sorted(integer_partitions(7, 2), reverse=True)
    cycle_types = [
        [2 * part for part in partition]
        for partition in half_cycle_partitions
    ]
    expected = [[14], [10, 4], [8, 6], [6, 4, 4]]
    if cycle_types != expected:
        raise AssertionError(f"2-factor cycle types drifted: {cycle_types}")

    # For a 70 x 15 incidence matrix B:
    # row weight 3, column weight 14, pairwise column intersection 2.
    btb_diagonal = 14
    btb_off_diagonal = 2
    scaled_centered_diagonal = (
        25 * btb_diagonal - 10 * 14 + 70
    )
    scaled_centered_off_diagonal = (
        25 * btb_off_diagonal - 5 * 14 - 5 * 14 + 70
    )
    if (scaled_centered_diagonal, scaled_centered_off_diagonal) != (280, -20):
        raise AssertionError("centered design simplex Gram drifted")

    return {
        "design": "simple 2-(15,3,2) with 70 blocks",
        "matrix_dimensions": [70, 15],
        "row_weight": 3,
        "column_weight": 14,
        "pairwise_column_intersection": 2,
        "B_transpose_B": "12I_15+2J_15",
        "rank_B": 15,
        "simple_block_argument": (
            "two repeated O-neighborhood triples would give the two O "
            "vertices at least three common Q neighbors"
        ),
        "each_Q_neighborhood_label_graph": {
            "vertices": "P union R",
            "degree": 2,
            "simple": True,
            "bipartite": True,
            "cycle_types": cycle_types,
        },
        "scaled_centered_neighborhood_vectors": {
            "definition": "w_q=5*1_{N_O(q)}-1_O",
            "gram_diagonal": scaled_centered_diagonal,
            "gram_off_diagonal": scaled_centered_off_diagonal,
            "gram_matrix": "300I_15-20J_15",
            "span_dimension": 14,
            "conditional_D_action": "D*w_q=-w_q",
        },
    }


def pg_3_2_lines() -> list[tuple[int, int, int]]:
    lines = {
        tuple(sorted((left - 1, right - 1, (left ^ right) - 1)))
        for left, right in itertools.combinations(range(1, 16), 2)
    }
    result = sorted(lines)
    if len(result) != 35:
        raise AssertionError("PG(3,2) line count drifted")
    return result


def hostile_design_only_control() -> dict[str, object]:
    """Build a simple 2-(15,3,2) that deliberately ignores F-label coupling."""
    first = pg_3_2_lines()
    permutation = [7, 4, 9, 10, 1, 14, 8, 6, 5, 12, 11, 2, 13, 0, 3]
    second = sorted(
        tuple(sorted(permutation[point] for point in block))
        for block in first
    )
    blocks = first + second
    if set(first) & set(second):
        raise AssertionError("hostile STS copies are not disjoint")
    if len(set(blocks)) != 70:
        raise AssertionError("hostile design blocks are not simple")

    incidence = zeros(70, 15)
    for row, block in enumerate(blocks):
        for point in block:
            incidence[row][point] = 1
    btb = matmul(transpose(incidence), incidence)
    expected = matadd(
        matscale(identity(15), 12),
        matscale(all_ones(15, 15), 2),
    )
    if btb != expected:
        raise AssertionError("hostile 2-design identity failed")

    fixed = build_fixed_support()
    support_to_o = fixed["F"]
    assert isinstance(support_to_o, list)
    label_coupling = matmul(support_to_o, incidence)
    mismatch_count = sum(
        value != 2
        for row in label_coupling
        for value in row
    )
    histogram = {
        str(value): sum(
            entry == value
            for row in label_coupling
            for entry in row
        )
        for value in sorted({entry for row in label_coupling for entry in row})
    }
    if mismatch_count == 0:
        raise AssertionError("hostile design accidentally satisfied F B=2J")

    return {
        "status": "HOSTILE_DESIGN_ONLY_NOT_AN_EXTENSION",
        "construction": "two disjoint PG(3,2) Steiner triple systems",
        "point_permutation": permutation,
        "block_count": len(blocks),
        "blocks_are_distinct": True,
        "row_weight_histogram": degree_histogram(incidence),
        "column_weight_histogram": degree_histogram(transpose(incidence)),
        "pairwise_column_intersections": sorted({
            btb[i][j]
            for i, j in itertools.combinations(range(15), 2)
        }),
        "B_sha256": hash_payload(incidence),
        "B_transpose_B_passes": True,
        "arbitrary_O_label_order_FB_histogram": histogram,
        "arbitrary_O_label_order_FB_mismatch_count": mismatch_count,
        "F_B_equals_2J": False,
        "limitation": (
            "This proves only that the abstract 2-(15,3,2) design condition "
            "is consistent; it deliberately fails the fixed support-label "
            "coupling and supplies no D."
        ),
    }


def build_forced_support_star_edges() -> Matrix:
    fixed = build_fixed_support()
    labels = fixed["labels"]
    cross = fixed["cross"]
    assert isinstance(labels, list)
    assert isinstance(cross, list)
    index = {
        (positive, negative, copy): position
        for position, (positive, negative, copy, _kind) in enumerate(labels)
    }
    edges: set[tuple[int, int]] = set()

    def add_matching(groups: list[tuple[int, int]]) -> None:
        if len(groups) != 3:
            raise AssertionError("support-star group count drifted")
        (a0, a1), (b0, b1), (c0, c1) = groups
        for left, right in ((a0, b0), (b1, c0), (c1, a1)):
            edge = tuple(sorted((left, right)))
            if edge in edges:
                raise AssertionError("duplicate forced support-star edge")
            edges.add(edge)

    for positive in range(7):
        nonneighbors = [
            negative
            for negative in range(7)
            if not cross[positive][negative]
        ]
        add_matching([
            (
                index[(positive, negative, 0)],
                index[(positive, negative, 1)],
            )
            for negative in nonneighbors
        ])

    for negative in range(7):
        nonneighbors = [
            positive
            for positive in range(7)
            if not cross[positive][negative]
        ]
        add_matching([
            (
                index[(positive, negative, 0)],
                index[(positive, negative, 1)],
            )
            for positive in nonneighbors
        ])

    adjacency = zeros(70, 70)
    for left, right in edges:
        adjacency[left][right] = 1
        adjacency[right][left] = 1
    if len(edges) != 42:
        raise AssertionError("forced support-star edge count drifted")
    if degree_histogram(adjacency) != {"0": 28, "2": 42}:
        raise AssertionError("forced support-star degree histogram drifted")
    return adjacency


def valid_binary_matrix(
    matrix: Sequence[Sequence[int]],
    rows: int,
    columns: int,
) -> bool:
    return (
        len(matrix) == rows
        and all(len(row) == columns for row in matrix)
        and all(value in (0, 1) for row in matrix for value in row)
    )


def assemble_full_adjacency(D: Matrix, B: Matrix) -> Matrix:
    fixed = build_fixed_support()
    support_adjacency = fixed["A_S"]
    support_to_o = fixed["F"]
    assert isinstance(support_adjacency, list)
    assert isinstance(support_to_o, list)
    full = zeros(99, 99)
    for i in range(14):
        for j in range(14):
            full[i][j] = support_adjacency[i][j]
    for i in range(14):
        for j in range(70):
            full[i][14 + j] = support_to_o[i][j]
            full[14 + j][i] = support_to_o[i][j]
    for i in range(70):
        for j in range(70):
            full[14 + i][14 + j] = D[i][j]
    for i in range(70):
        for j in range(15):
            full[14 + i][84 + j] = B[i][j]
            full[84 + j][14 + i] = B[i][j]
    return full


def extension_criterion_diagnostics(D: Matrix, B: Matrix) -> dict[str, object]:
    fixed = build_fixed_support()
    support_adjacency = fixed["A_S"]
    support_to_o = fixed["F"]
    assert isinstance(support_adjacency, list)
    assert isinstance(support_to_o, list)
    if not valid_binary_matrix(D, 70, 70):
        return {"shape_and_binary": False, "all_blocks_pass": False}
    if not valid_binary_matrix(B, 70, 15):
        return {"shape_and_binary": False, "all_blocks_pass": False}

    symmetric_zero_diagonal = (
        D == transpose(D)
        and all(D[index][index] == 0 for index in range(70))
    )
    blocks = {
        "SS_fixed": (
            matadd(
                matmul(support_adjacency, support_adjacency),
                matmul(support_to_o, transpose(support_to_o)),
            )
            == matadd(
                matscale(identity(14), 12),
                matscale(support_adjacency, -1),
                matscale(all_ones(14, 14), 2),
            )
        ),
        "SO": (
            matadd(
                matmul(support_adjacency, support_to_o),
                matmul(support_to_o, D),
            )
            == matadd(
                matscale(all_ones(14, 70), 2),
                matscale(support_to_o, -1),
            )
        ),
        "SQ": (
            matmul(support_to_o, B)
            == matscale(all_ones(14, 15), 2)
        ),
        "OO": (
            matadd(
                matmul(transpose(support_to_o), support_to_o),
                matmul(D, D),
                matmul(B, transpose(B)),
            )
            == matadd(
                matscale(identity(70), 12),
                matscale(D, -1),
                matscale(all_ones(70, 70), 2),
            )
        ),
        "OQ": (
            matmul(D, B)
            == matadd(
                matscale(all_ones(70, 15), 2),
                matscale(B, -1),
            )
        ),
        "QQ": (
            matmul(transpose(B), B)
            == matadd(
                matscale(identity(15), 12),
                matscale(all_ones(15, 15), 2),
            )
        ),
    }
    full = assemble_full_adjacency(D, B)
    global_identity = (
        matmul(full, full)
        == matadd(
            matscale(identity(99), 12),
            matscale(full, -1),
            matscale(all_ones(99, 99), 2),
        )
    )
    all_blocks_pass = symmetric_zero_diagonal and all(blocks.values())
    if global_identity != all_blocks_pass:
        raise AssertionError(
            "block criterion and assembled global identity disagree"
        )
    return {
        "shape_and_binary": True,
        "D_symmetric_zero_diagonal": symmetric_zero_diagonal,
        "block_passes": blocks,
        "all_blocks_pass": all_blocks_pass,
        "assembled_global_identity_passes": global_identity,
    }


def extension_criterion() -> dict[str, object]:
    fixed = build_fixed_support()
    support_to_o = fixed["F"]
    assert isinstance(support_to_o, list)
    hostile_D = build_forced_support_star_edges()
    hostile_B_payload = hostile_design_only_control()

    first = pg_3_2_lines()
    permutation = hostile_B_payload["point_permutation"]
    assert isinstance(permutation, list)
    second = sorted(
        tuple(sorted(permutation[point] for point in block))
        for block in first
    )
    hostile_B = zeros(70, 15)
    for row, block in enumerate(first + second):
        for point in block:
            hostile_B[row][point] = 1

    diagnostics = extension_criterion_diagnostics(hostile_D, hostile_B)
    if diagnostics["all_blocks_pass"]:
        raise AssertionError("hostile partial matrices became an extension")

    return {
        "fixed_matrices": {
            "A_S_dimensions": [14, 14],
            "F_dimensions": [14, 70],
            "F_column_description": (
                "one column per support cross-edge and two columns per "
                "support cross-nonedge"
            ),
        },
        "unknown_binary_matrices": {
            "D": "70x70 symmetric zero-diagonal O adjacency",
            "B": "70x15 O-Q incidence",
        },
        "block_equations": [
            "A_S^2+F F^T=12I-A_S+2J",
            "A_S F+F D=2J-F",
            "F B=2J",
            "F^T F+D^2+B B^T=12I-D+2J",
            "D B=2J-B",
            "B^T B=12I+2J",
        ],
        "necessity": (
            "Every rooted extension necessarily, after relabeling only the "
            "already-forced Fano support and its O labels, supplies D and B "
            "satisfying all six blocks."
        ),
        "sufficiency": (
            "Binary D,B with D symmetric and zero-diagonal satisfying all "
            "six blocks assemble to a simple 99-vertex adjacency matrix with "
            "A^2=12I-A+2J; its diagonal gives degree 14 and its off-diagonal "
            "entries give lambda=1, mu=2."
        ),
        "finite_search_space": {
            "D_binary_upper_triangle_variables": 70 * 69 // 2,
            "B_binary_variables": 70 * 15,
            "total_raw_binary_variables": 70 * 69 // 2 + 70 * 15,
            "automorphism_assumption": "none",
        },
        "hostile_partial_control": {
            "D_degree_histogram": degree_histogram(hostile_D),
            "D_edge_count": sum(sum(row) for row in hostile_D) // 2,
            "B_is_abstract_two_design": True,
            "criterion_diagnostics": diagnostics,
            "status": "REJECTED_BY_COMPLETE_CRITERION",
        },
    }


def quadratic_power(a: int, b: int, exponent: int) -> tuple[int, int]:
    """Return coefficients of (a+b*sqrt(2))**exponent."""
    result_a, result_b = 1, 0
    base_a, base_b = a, b
    power = exponent
    while power:
        if power & 1:
            result_a, result_b = (
                result_a * base_a + 2 * result_b * base_b,
                result_a * base_b + result_b * base_a,
            )
        base_a, base_b = (
            base_a * base_a + 2 * base_b * base_b,
            2 * base_a * base_b,
        )
        power //= 2
    return result_a, result_b


def forced_D_spectral_moment(exponent: int) -> int:
    rational = (
        9 ** exponent
        + 14 * ((-1) ** exponent)
        + 27 * (3 ** exponent)
        + 16 * ((-4) ** exponent)
    )
    plus = quadratic_power(-1, 1, exponent)
    minus = quadratic_power(-1, -1, exponent)
    if plus[1] + minus[1] != 0:
        raise AssertionError("quadratic conjugates did not cancel")
    return rational + 6 * (plus[0] + minus[0])


def forced_D_spectrum() -> dict[str, object]:
    moments = {
        str(exponent): forced_D_spectral_moment(exponent)
        for exponent in range(5)
    }
    expected = {"0": 70, "1": 0, "2": 630, "3": 336, "4": 13062}
    if moments != expected:
        raise AssertionError(f"D spectral moments drifted: {moments}")

    edge_count = moments["2"] // 2
    triangle_count = moments["3"] // 6
    four_cycle_base = (
        2 * edge_count
        + 4 * 70 * (9 * 8 // 2)
    )
    four_cycle_count = (moments["4"] - four_cycle_base) // 8
    if (edge_count, triangle_count, four_cycle_count) != (315, 56, 294):
        raise AssertionError("D small-cycle census drifted")

    return {
        "derivation_decomposition": {
            "constant_O_space": {
                "dimension": 1,
                "D_eigenvalue": "9",
            },
            "centered_Q_neighborhood_space": {
                "dimension": 14,
                "D_eigenvalue": "-1",
            },
            "nonconstant_support_incidence_space": {
                "dimensions": [6, 6],
                "D_eigenvalues": ["-1-sqrt(2)", "-1+sqrt(2)"],
            },
            "joint_kernel_of_F_and_B_transpose": {
                "dimension": 43,
                "polynomial": "D^2+D-12I=0",
                "D_eigenvalue_multiplicities": {"3": 27, "-4": 16},
            },
        },
        "spectrum": {
            "9": 1,
            "-1": 14,
            "-1-sqrt(2)": 6,
            "-1+sqrt(2)": 6,
            "3": 27,
            "-4": 16,
        },
        "characteristic_polynomial": (
            "(x-9)(x+1)^14(x^2+2x-1)^6(x-3)^27(x+4)^16"
        ),
        "spectral_moments": moments,
        "connected": True,
        "edge_count": edge_count,
        "triangle_count": triangle_count,
        "four_cycle_count": four_cycle_count,
        "determinant": "2^32*3^29",
    }


def triangle_and_edge_census() -> dict[str, object]:
    total_graph_edges = 99 * 14 // 2
    total_graph_triangles = total_graph_edges * 1 // 3
    D_edges = 70 * 9 // 2
    support_witnessed_D_edges = 14 * 3
    Q_witnessed_D_edges = 15 * 7
    O_witnessed_D_edges = (
        D_edges - support_witnessed_D_edges - Q_witnessed_D_edges
    )
    D_triangles = O_witnessed_D_edges // 3
    triangle_classes = {
        "two_S_one_O": 28,
        "one_S_two_O": support_witnessed_D_edges,
        "two_O_one_Q": Q_witnessed_D_edges,
        "three_O": D_triangles,
    }
    if sum(triangle_classes.values()) != total_graph_triangles:
        raise AssertionError("global triangle classes do not sum correctly")
    if D_triangles != forced_D_spectrum()["triangle_count"]:
        raise AssertionError("combinatorial and spectral D triangles disagree")

    return {
        "target_graph": {
            "edge_count": total_graph_edges,
            "triangle_count": total_graph_triangles,
        },
        "D_edge_partition_by_unique_common_neighbor_cell": {
            "S": support_witnessed_D_edges,
            "Q": Q_witnessed_D_edges,
            "O": O_witnessed_D_edges,
            "total": D_edges,
        },
        "target_triangle_partition": triangle_classes,
        "explanations": {
            "S_witnessed": (
                "the six nonedge-completion O-neighbors at each support "
                "vertex form a perfect matching"
            ),
            "Q_witnessed": (
                "each of 15 Q-neighborhoods induces a seven-edge matching "
                "in D"
            ),
            "O_witnessed": (
                "the remaining D edges have their unique common neighbor "
                "inside O and partition three-to-one into D triangles"
            ),
        },
    }


def build_results() -> dict[str, object]:
    frozen = verify_frozen_inputs()
    return {
        "schema_version": 1,
        "claim_label": "DERIVED_VERIFICATION_PENDING",
        "scope": (
            "necessary and sufficient finite block-matrix extension criterion, "
            "and necessary partition/design/spectral consequences, conditional "
            "on the verified Wave 32 actual-incidence rooted support"
        ),
        "frozen_inputs": frozen,
        "fixed_support": fixed_support_identities(),
        "equitable_partition": equitable_partition(),
        "O_Q_design": design_consequences(),
        "hostile_design_only_control": hostile_design_only_control(),
        "extension_criterion": extension_criterion(),
        "forced_O_graph_spectrum": forced_D_spectrum(),
        "triangle_and_edge_census": triangle_and_edge_census(),
        "status": {
            "finite_extension_criterion": "DERIVED_VERIFICATION_PENDING",
            "necessary_partition_design_spectrum": "DERIVED_VERIFICATION_PENDING",
            "full_extension_found": False,
            "root_exclusion": "NOT_OBTAINED",
            "rooted_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "No D,B pair satisfying the criterion is constructed.",
            "No complete search or infeasibility certificate is supplied.",
            "The hostile 2-design deliberately fails fixed F-label coupling.",
            "Projector, lattice, tensor, and Schur conditions beyond graph "
            "extension remain additional filters on any passing D,B pair.",
            "No automorphism is assumed beyond relabeling the forced support.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = build_results()
    encoded = canonical_bytes(payload)
    if args.output:
        args.output.write_bytes(encoded)
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
