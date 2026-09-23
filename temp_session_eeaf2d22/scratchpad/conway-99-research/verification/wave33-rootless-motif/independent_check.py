#!/usr/bin/env python3
"""Clean-room Wave 33 rootless-motif verifier.

This standard-library checker was written and frozen before inspecting any
Wave 33 rootless discovery artifact.  It uses only the public continuation
protocol and independently verified Wave 20/Wave 32 premises.

It verifies a scoped algebraic/local non-forcing result.  It neither imports
nor executes discovery code, constructs a target graph, nor decides the
global rootless motif question.
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
    "CONJECTURE.md":
        "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "verification/wave33-continuation-protocol.md":
        "b98b6bb8228b54b67cd949ee1bf6eb05ebd6ebe74f1cbc9e49b041a55e2d2fe6",
    "verification/2026-07-23-wave20-global-schur-audit.md":
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "verification/wave32-indecomposable/audit.md":
        "15285e618b3a38c91c5d2e373dcb859720a2062d9ca108cd79cae12506a53f44",
    "verification/wave32-indecomposable/independent-results.json":
        "4b90ef54358a14abc92c925c8e0f94ed9510b4f80857fde5aa4e2abf4ba89e2a",
}

BASIS = ("I", "J", "Gamma", "C")
CATEGORIES = ("D", "Gamma", "R0", "R1", "R2", "R3")
R2_PAIR_ENTRY_VECTOR = (0, 1, 0, 2)


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
            "public input freeze mismatch\n"
            f"expected={FROZEN_INPUTS}\n"
            f"observed={observed}"
        )
    return observed


def determinant(matrix: Sequence[Sequence[int]]) -> int:
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1) ** column
        * matrix[0][column]
        * determinant([
            list(row[:column]) + list(row[column + 1:])
            for row in matrix[1:]
        ])
        for column in range(len(matrix))
    )


def basis_value(coefficients: Sequence[int], eigenvalue: int) -> int:
    if len(coefficients) != 4:
        raise ValueError("basis coefficient vector must have length four")
    I, J, Gamma, C = coefficients
    c_value = eigenvalue * eigenvalue - 5 * eigenvalue - 18
    j_value = 231 if eigenvalue == 18 else 0
    return I + J * j_value + Gamma * eigenvalue + C * c_value


def gamma_multiplication_table() -> dict[str, object]:
    products: dict[tuple[str, str], tuple[int, int, int, int]] = {
        ("I", "I"): (1, 0, 0, 0),
        ("I", "J"): (0, 1, 0, 0),
        ("I", "Gamma"): (0, 0, 1, 0),
        ("I", "C"): (0, 0, 0, 1),
        ("J", "J"): (0, 231, 0, 0),
        ("J", "Gamma"): (0, 18, 0, 0),
        ("J", "C"): (0, 216, 0, 0),
        ("Gamma", "Gamma"): (18, 0, 5, 1),
        ("Gamma", "C"): (-18, 18, -2, -1),
        ("C", "C"): (72, 216, -16, -14),
    }
    for (left, right), coefficients in list(products.items()):
        products[(right, left)] = coefficients

    eigenvalues = [18, 7, 0, -3]
    basis_evaluation = [
        [
            1,
            231 if eigenvalue == 18 else 0,
            eigenvalue,
            eigenvalue * eigenvalue - 5 * eigenvalue - 18,
        ]
        for eigenvalue in eigenvalues
    ]
    independence_determinant = determinant(basis_evaluation)
    if independence_determinant != 48510:
        raise AssertionError("basis evaluation determinant drifted")

    single_basis = {
        name: tuple(int(index == position) for index in range(4))
        for position, name in enumerate(BASIS)
    }
    for left in BASIS:
        for right in BASIS:
            coefficients = products[(left, right)]
            for eigenvalue in eigenvalues:
                observed = basis_value(coefficients, eigenvalue)
                expected = (
                    basis_value(single_basis[left], eigenvalue)
                    * basis_value(single_basis[right], eigenvalue)
                )
                if observed != expected:
                    raise AssertionError(
                        f"product {left}*{right} fails at {eigenvalue}"
                    )

    return {
        "basis": list(BASIS),
        "Gamma_spectrum": {"18": 1, "7": 54, "0": 44, "-3": 132},
        "minimal_polynomial": "x(x-18)(x-7)(x+3)",
        "minimal_polynomial_expanded": "x^4-22x^3+51x^2+378x",
        "basis_evaluation_determinant": independence_determinant,
        "dimension": 4,
        "defining_relations": {
            "C": "Gamma^2-5Gamma-18I",
            "J": "(Gamma^3-4Gamma^2-21Gamma)/18",
        },
        "multiplication": {
            f"{left}*{right}": list(products[(left, right)])
            for left_index, left in enumerate(BASIS)
            for right in BASIS[left_index:]
        },
        "coefficient_order": list(BASIS),
    }


def hostile_wrong_C_coefficient() -> dict[str, object]:
    # If C'=Gamma^2-4Gamma-18I, an intersecting pair has
    # Gamma=1 and Gamma^2=5, hence entry 1 rather than 0.
    intersecting_entry = 5 - 4 - 0
    target_entry = 5 - 5 - 0
    if (intersecting_entry, target_entry) != (1, 0):
        raise AssertionError("hostile C-coefficient arithmetic drifted")
    return {
        "target_Gamma_coefficient": -5,
        "hostile_Gamma_coefficient": -4,
        "target_intersecting_entry": target_entry,
        "hostile_intersecting_entry": intersecting_entry,
        "hostile_still_represents_cross_edge_count": False,
    }


def margins_for_q(q: int) -> list[int]:
    if not 0 <= q <= 12:
        raise ValueError("q must lie in [0,12]")
    return [1, 18, 20 + q, 180 - 3 * q, 3 * q, 12 - q]


def local_tables() -> tuple[list[list[int]], list[list[int]]]:
    table_zero = [
        [0, 0, 0, 0, 1, 0],
        [0, 2, 0, 16, 0, 0],
        [0, 0, 13, 0, 5, 4],
        [0, 16, 0, 152, 0, 6],
        [1, 0, 5, 0, 0, 0],
        [0, 0, 4, 6, 0, 0],
    ]
    table_one = [
        [0, 0, 0, 0, 1, 0],
        [0, 2, 0, 16, 0, 0],
        [0, 0, 9, 4, 5, 4],
        [0, 16, 4, 149, 0, 5],
        [1, 0, 5, 0, 0, 0],
        [0, 0, 4, 5, 0, 1],
    ]
    return table_zero, table_one


def entry_vectors() -> dict[str, tuple[int, ...]]:
    return {
        "I": (1, 0, 0, 0, 0, 0),
        "J": (1, 1, 1, 1, 1, 1),
        "Gamma": (0, 1, 0, 0, 0, 0),
        "C": (0, 0, 0, 1, 2, 3),
    }


def bilinear_contraction(
    left: Sequence[int],
    table: Sequence[Sequence[int]],
    right: Sequence[int],
) -> int:
    return sum(
        left[row] * table[row][column] * right[column]
        for row in range(6)
        for column in range(6)
    )


def table_contraction_matrix(table: Sequence[Sequence[int]]) -> list[list[int]]:
    vectors = entry_vectors()
    return [
        [
            bilinear_contraction(vectors[left], table, vectors[right])
            for right in BASIS
        ]
        for left in BASIS
    ]


def expected_R2_product_matrix() -> list[list[int]]:
    algebra = gamma_multiplication_table()
    raw = algebra["multiplication"]
    assert isinstance(raw, dict)
    result: list[list[int]] = []
    for left_index, left in enumerate(BASIS):
        row = []
        for right_index, right in enumerate(BASIS):
            first, second = (
                (left, right)
                if left_index <= right_index
                else (right, left)
            )
            coefficients = raw[f"{first}*{second}"]
            assert isinstance(coefficients, list)
            row.append(sum(
                coefficient * entry
                for coefficient, entry in zip(
                    coefficients,
                    R2_PAIR_ENTRY_VECTOR,
                )
            ))
        result.append(row)
    return result


def validate_local_table(table: Sequence[Sequence[int]]) -> dict[str, object]:
    if len(table) != 6 or any(len(row) != 6 for row in table):
        raise AssertionError("local table shape is not 6x6")
    if any(value < 0 or int(value) != value for row in table for value in row):
        raise AssertionError("local table is not nonnegative integral")
    if list(map(list, table)) != [list(row) for row in zip(*table)]:
        raise AssertionError("local table is not symmetric")
    margins = [sum(row) for row in table]
    if margins != margins_for_q(2):
        raise AssertionError(f"q=2 margins drifted: {margins}")
    fixed = {
        "D_R2": table[0][4],
        "R2_D": table[4][0],
        "Gamma_Gamma": table[1][1],
    }
    if fixed != {"D_R2": 1, "R2_D": 1, "Gamma_Gamma": 2}:
        raise AssertionError(f"fixed R2-pair cells drifted: {fixed}")
    contractions = table_contraction_matrix(table)
    expected = expected_R2_product_matrix()
    if contractions != expected:
        raise AssertionError(
            f"Q[Gamma] contraction mismatch: {contractions} != {expected}"
        )
    return {
        "margins": margins,
        "fixed_cells": fixed,
        "contractions": contractions,
        "common_R3_count": table[5][5],
        "sha256": hash_payload(table),
    }


def algebraic_local_nonforcing() -> dict[str, object]:
    table_zero, table_one = local_tables()
    zero = validate_local_table(table_zero)
    one = validate_local_table(table_one)
    if zero["common_R3_count"] != 0 or one["common_R3_count"] != 1:
        raise AssertionError("hostile common-R3 values drifted")
    if zero["margins"] != one["margins"]:
        raise AssertionError("hostile table margins differ")
    if zero["contractions"] != one["contractions"]:
        raise AssertionError("hostile Q[Gamma] contractions differ")

    switch = [
        [table_one[i][j] - table_zero[i][j] for j in range(6)]
        for i in range(6)
    ]
    if [sum(row) for row in switch] != [0] * 6:
        raise AssertionError("table switch changes margins")
    vectors = entry_vectors()
    for left in BASIS:
        for right in BASIS:
            if bilinear_contraction(
                vectors[left],
                switch,
                vectors[right],
            ) != 0:
                raise AssertionError("table switch is visible to Q[Gamma]")

    return {
        "pair_scope": {
            "q_T": 2,
            "q_U": 2,
            "relation": "R2",
            "formal_only": True,
            "global_existence_of_such_pair": "NOT_PROVED",
        },
        "category_order": list(CATEGORIES),
        "table_common_R3_zero": table_zero,
        "table_common_R3_one": table_one,
        "shared_margins": zero["margins"],
        "shared_QGamma_contractions": zero["contractions"],
        "basis_order": list(BASIS),
        "switch": switch,
        "switch_row_sums": [sum(row) for row in switch],
        "common_R3_counts": [zero["common_R3_count"], one["common_R3_count"]],
        "trace_contribution_for_unordered_R2_pair": [0, 2],
        "interpretation": (
            "All bilinear contractions from the four-dimensional fused "
            "algebra agree, but the R3-R3 cell changes by one."
        ),
        "limitation": (
            "These are nonnegative integral intersection tables satisfying "
            "the fused constraints; neither is asserted realizable by a "
            "global triangle configuration."
        ),
    }


def poly_multiply(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> list[Fraction]:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def reduce_gamma_polynomial(coefficients: Sequence[Fraction]) -> list[Fraction]:
    work = list(coefficients)
    # x^4=22x^3-51x^2-378x.
    replacement = [
        Fraction(0),
        Fraction(-378),
        Fraction(-51),
        Fraction(22),
    ]
    while len(work) > 4:
        degree = len(work) - 1
        leading = work.pop()
        shift = degree - 4
        for index, value in enumerate(replacement):
            work[shift + index] += leading * value
    while len(work) < 4:
        work.append(Fraction(0))
    return work


def polynomial_to_basis(
    coefficients: Sequence[Fraction],
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    p0, p1, p2, p3 = coefficients
    J = 18 * p3
    C = p2 + 4 * p3
    Gamma = p1 + 5 * p2 + 41 * p3
    I = p0 + 18 * p2 + 72 * p3
    return I, J, Gamma, C


def incidence_transport() -> dict[str, object]:
    # NN^T=7I+A and N^TN=3I+Gamma imply
    # A N=N(Gamma-4I), hence
    # N^T A^k N=(Gamma+3I)(Gamma-4I)^k.
    current = [Fraction(3), Fraction(1)]
    factor = [Fraction(-4), Fraction(1)]
    rows = []
    for exponent in range(9):
        reduced = reduce_gamma_polynomial(current)
        basis_coefficients = polynomial_to_basis(reduced)
        if any(value.denominator != 1 for value in basis_coefficients):
            raise AssertionError("transport basis coefficient is nonintegral")
        for eigenvalue in (18, 7, 0, -3):
            observed = sum(
                reduced[degree] * (eigenvalue ** degree)
                for degree in range(4)
            )
            expected = (eigenvalue + 3) * ((eigenvalue - 4) ** exponent)
            if observed != expected:
                raise AssertionError(
                    f"transport exponent {exponent} fails at {eigenvalue}"
                )
        rows.append({
            "k": exponent,
            "reduced_polynomial_coefficients_ascending": [
                int(value) for value in reduced
            ],
            "basis_coefficients_I_J_Gamma_C": [
                int(value) for value in basis_coefficients
            ],
        })
        current = poly_multiply(current, factor)

    if rows[:3] != [
        {
            "k": 0,
            "reduced_polynomial_coefficients_ascending": [3, 1, 0, 0],
            "basis_coefficients_I_J_Gamma_C": [3, 0, 1, 0],
        },
        {
            "k": 1,
            "reduced_polynomial_coefficients_ascending": [-12, -1, 1, 0],
            "basis_coefficients_I_J_Gamma_C": [6, 0, 4, 1],
        },
        {
            "k": 2,
            "reduced_polynomial_coefficients_ascending": [48, -8, -5, 1],
            "basis_coefficients_I_J_Gamma_C": [30, 18, 8, -1],
        },
    ]:
        raise AssertionError("initial transport rows drifted")

    return {
        "premises": ["N N^T=7I+A", "N^T N=3I+Gamma"],
        "intertwining": "A N=N(Gamma-4I)",
        "all_nonnegative_k": (
            "N^T A^k N=(Gamma+3I)(Gamma-4I)^k in Q[Gamma]"
        ),
        "first_nine_exact_reductions": rows,
        "kernel_scope": (
            "the Gamma=-3 eigenspace is killed by N^T N and contributes zero"
        ),
        "limitation": (
            "This covers vertex-walk contractions mediated by N; it does "
            "not place arbitrary triple-incidence tensors or individual "
            "R2/R3 relation matrices in Q[Gamma]."
        ),
        "hostile_shift_minus_3": {
            "premise_balance": "(7I+A)N=N(3I+Gamma)",
            "correct_shift": -4,
            "hostile_shift": -3,
            "passes": False,
        },
    }


def affine_indicator_possible(values: Sequence[int]) -> bool:
    if len(values) != 4:
        raise ValueError("indicator must give values at r=0,1,2,3")
    intercept = Fraction(values[0])
    slope = Fraction(values[1] - values[0])
    return all(
        intercept + slope * relation == value
        for relation, value in enumerate(values)
    )


def fused_algebra_scope() -> dict[str, object]:
    indicators = {
        "R0": [1, 0, 0, 0],
        "R1": [0, 1, 0, 0],
        "R2": [0, 0, 1, 0],
        "R3": [0, 0, 0, 1],
    }
    possible = {
        name: affine_indicator_possible(values)
        for name, values in indicators.items()
    }
    if any(possible.values()):
        raise AssertionError("an individual R relation became affine in r")
    return {
        "QGamma_entry_form_on_disjoint_pairs": "alpha+beta*r(T,U)",
        "individual_relation_indicators_affine": possible,
        "R3_matrix_in_QGamma": False,
        "R2_matrix_in_QGamma": False,
        "common_R3_statistic": "(A_R3^2)_{T,U}",
        "common_R3_determined_by_QGamma": False,
        "scope_conclusion": (
            "closure of N^T A^k N in Q[Gamma] cannot by itself determine "
            "the forbidden mixed motif"
        ),
    }


def base_six_vertex_graph() -> list[set[int]]:
    adjacency = [set() for _ in range(6)]

    def add_edge(left: int, right: int) -> None:
        adjacency[left].add(right)
        adjacency[right].add(left)

    for left, right in itertools.combinations(range(3), 2):
        add_edge(left, right)
    for left, right in itertools.combinations(range(3, 6), 2):
        add_edge(left, right)
    add_edge(0, 3)
    add_edge(1, 4)
    return adjacency


def multiplicity_board(
    lambda_value: int = 1,
    mu_value: int = 2,
) -> list[list[int]]:
    adjacency = base_six_vertex_graph()
    board = []
    for t_vertex in range(3):
        row = []
        for u_local in range(3):
            u_vertex = 3 + u_local
            adjacent = u_vertex in adjacency[t_vertex]
            target = lambda_value if adjacent else mu_value
            internal_common = len(
                adjacency[t_vertex] & adjacency[u_vertex]
            )
            outside = target - internal_common
            if outside < 0:
                raise AssertionError("negative outside multiplicity")
            row.append(outside)
        board.append(row)
    return board


def board_witnesses(board: Sequence[Sequence[int]]) -> dict[tuple[int, int], list[str]]:
    result: dict[tuple[int, int], list[str]] = {}
    for row in range(3):
        for column in range(3):
            count = board[row][column]
            names = []
            for copy in range(count):
                suffix = "" if count == 1 else chr(ord("a") + copy)
                names.append(f"w{row}{column}{suffix}")
            result[(row, column)] = names
    return result


def transversal_candidates(
    board: Sequence[Sequence[int]],
) -> list[tuple[str, str, str]]:
    witnesses = board_witnesses(board)
    candidates: list[tuple[str, str, str]] = []
    for permutation in itertools.permutations(range(3)):
        choices = [
            witnesses[(row, permutation[row])]
            for row in range(3)
        ]
        if any(not cell for cell in choices):
            continue
        for selected in itertools.product(*choices):
            if len(set(selected)) != 3:
                raise AssertionError("transversal reused an outside witness")
            candidates.append(tuple(selected))
    if len(candidates) != len(set(candidates)):
        raise AssertionError("duplicate transversal candidate")
    return candidates


def actual_incidence_board() -> dict[str, object]:
    board = multiplicity_board()
    expected = [[1, 0, 1], [0, 1, 1], [1, 1, 2]]
    if board != expected:
        raise AssertionError(f"target multiplicity board drifted: {board}")
    candidates = transversal_candidates(board)
    expected_candidates = [
        ("w00", "w11", "w22a"),
        ("w00", "w11", "w22b"),
        ("w00", "w12", "w21"),
        ("w02", "w11", "w20"),
    ]
    if candidates != expected_candidates:
        raise AssertionError(f"transversal candidates drifted: {candidates}")

    hostile_mu_board = multiplicity_board(mu_value=3)
    hostile_candidates = transversal_candidates(hostile_mu_board)
    if len(hostile_candidates) <= len(candidates):
        raise AssertionError("mu=3 mutation did not enlarge candidates")

    return {
        "normalized_R2_cross_edges": [[0, 0], [1, 1]],
        "multiplicity_board": board,
        "board_rows": ["t0", "t1", "t2"],
        "board_columns": ["u0", "u1", "u2"],
        "derivation": (
            "entry=lambda or mu minus common neighbors already lying in "
            "T union U"
        ),
        "transversal_candidates": [list(candidate) for candidate in candidates],
        "transversal_candidate_count": len(candidates),
        "candidate_condition": (
            "one cell in each row and column; the three selected witnesses "
            "must additionally induce a graph triangle"
        ),
        "hostile_mu_3": {
            "multiplicity_board": hostile_mu_board,
            "transversal_candidate_count": len(hostile_candidates),
            "passes_target_count": False,
        },
    }


def build_local_control(add_candidate_triangle: bool) -> dict[str, object]:
    board = multiplicity_board()
    witnesses = board_witnesses(board)
    names = [f"t{i}" for i in range(3)] + [f"u{i}" for i in range(3)]
    names += [
        witness
        for row in range(3)
        for column in range(3)
        for witness in witnesses[(row, column)]
    ]
    adjacency = {name: set() for name in names}

    def add_edge(left: str, right: str) -> None:
        if left == right:
            raise AssertionError("loop in local control")
        adjacency[left].add(right)
        adjacency[right].add(left)

    for left, right in itertools.combinations([f"t{i}" for i in range(3)], 2):
        add_edge(left, right)
    for left, right in itertools.combinations([f"u{i}" for i in range(3)], 2):
        add_edge(left, right)
    add_edge("t0", "u0")
    add_edge("t1", "u1")
    for (row, column), cell_witnesses in witnesses.items():
        for witness in cell_witnesses:
            add_edge(f"t{row}", witness)
            add_edge(f"u{column}", witness)

    chosen_triangle = ("w00", "w12", "w21")
    if add_candidate_triangle:
        for left, right in itertools.combinations(chosen_triangle, 2):
            add_edge(left, right)

    # Audit lambda/mu only for the nine T-U cross pairs.
    common_board = []
    for row in range(3):
        values = []
        for column in range(3):
            left, right = f"t{row}", f"u{column}"
            common = len(adjacency[left] & adjacency[right])
            target = 1 if right in adjacency[left] else 2
            if common != target:
                raise AssertionError(
                    f"cross pair {(left,right)} has {common}, expected {target}"
                )
            values.append(common)
        common_board.append(values)

    candidates = [
        tuple(candidate)
        for candidate in actual_incidence_board()["transversal_candidates"]
    ]

    def is_triangle(vertices: Sequence[str]) -> bool:
        return all(
            right in adjacency[left]
            for left, right in itertools.combinations(vertices, 2)
        )

    realized = [candidate for candidate in candidates if is_triangle(candidate)]
    expected_count = 1 if add_candidate_triangle else 0
    if len(realized) != expected_count:
        raise AssertionError("local control motif count drifted")

    if add_candidate_triangle:
        T = ("t0", "t1", "t2")
        U = ("u0", "u1", "u2")

        def cross_edge_count(
            left_triple: Sequence[str],
            right_triple: Sequence[str],
        ) -> int:
            return sum(
                right in adjacency[left]
                for left in left_triple
                for right in right_triple
            )

        if (
            cross_edge_count(T, chosen_triangle) != 3
            or cross_edge_count(U, chosen_triangle) != 3
        ):
            raise AssertionError("realized triangle is not common R3")

    edge_count = sum(len(neighbors) for neighbors in adjacency.values()) // 2
    degree_histogram = {
        str(degree): sum(
            len(neighbors) == degree
            for neighbors in adjacency.values()
        )
        for degree in sorted({len(neighbors) for neighbors in adjacency.values()})
    }
    return {
        "status": "LOCAL_CROSS_PAIR_CONTROL_NOT_A_TARGET_GRAPH",
        "vertex_count": len(names),
        "edge_count": edge_count,
        "degree_histogram": degree_histogram,
        "cross_pair_common_neighbor_board": common_board,
        "candidate_triangle_added": add_candidate_triangle,
        "realized_transversal_triangles": [list(item) for item in realized],
        "common_R3_count": len(realized),
        "R2_pair_trace_contribution": 2 * len(realized),
        "dropped_premises": [
            "all lambda/mu constraints outside the nine T-U cross pairs",
            "99-vertex size and degree 14",
            "global triangle relation margins",
            "projector, lattice, tensor, and Schur endpoint identities",
        ],
    }


def local_incidence_nonforcing() -> dict[str, object]:
    zero = build_local_control(False)
    one = build_local_control(True)
    if zero["cross_pair_common_neighbor_board"] != one[
        "cross_pair_common_neighbor_board"
    ]:
        raise AssertionError("local controls changed cross-pair counts")
    if [zero["common_R3_count"], one["common_R3_count"]] != [0, 1]:
        raise AssertionError("local controls did not separate motif count")
    return {
        "zero_motif_control": zero,
        "one_motif_control": one,
        "shared_exact_cross_pair_lambda_mu": True,
        "conclusion": (
            "the exact 3x3 board supplies four candidates but does not decide "
            "which candidate triples induce graph triangles"
        ),
        "scope": "local non-forcing only; neither control is globally admissible",
    }


def status_wall() -> dict[str, object]:
    return {
        "QGamma_multiplication": "INDEPENDENTLY_DERIVED",
        "formal_table_nonforcing": "INDEPENDENTLY_DERIVED",
        "incidence_transport": "INDEPENDENTLY_DERIVED_WITH_SCOPE_LIMIT",
        "actual_R2_multiplicity_board": "INDEPENDENTLY_DERIVED",
        "four_transversal_candidates": "INDEPENDENTLY_DERIVED",
        "global_motif_forcing": "UNKNOWN",
        "global_motif_avoidance": "UNKNOWN",
        "rootless_endpoint": "UNKNOWN",
        "n3_708": "UNKNOWN",
        "Conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
    }


def build_results() -> dict[str, object]:
    return {
        "schema_version": 1,
        "role": "clean_room_adversarial_verifier_precomparison",
        "claim_label": "DERIVED_PRECOMPARISON",
        "frozen_public_inputs": verify_frozen_inputs(),
        "gamma_algebra": gamma_multiplication_table(),
        "hostile_wrong_C_coefficient": hostile_wrong_C_coefficient(),
        "algebraic_local_nonforcing": algebraic_local_nonforcing(),
        "incidence_transport": incidence_transport(),
        "fused_algebra_scope": fused_algebra_scope(),
        "actual_incidence_board": actual_incidence_board(),
        "local_incidence_nonforcing": local_incidence_nonforcing(),
        "status": status_wall(),
        "independence": {
            "candidate_files_inspected": False,
            "candidate_code_imported_or_executed": False,
            "candidate_comparison_performed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = canonical_bytes(build_results())
    if args.output:
        args.output.write_bytes(encoded)
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
