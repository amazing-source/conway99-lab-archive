#!/usr/bin/env python3
"""Exact Wave 33 proof-B checks for the rootless mixed-motif boundary.

The checker proves two scoped statements.

1.  For a q=2 pair in the r=2 / M=-1 relation, two explicit nonnegative
    local third-triangle tables have identical contractions against every
    pair of matrices in Q[Gamma], but their number of common r=3 / M=-2
    neighbours is respectively zero and one.  Fully contracted two-leg
    vertex-incidence expressions also reduce to Q[Gamma].

2.  Actual SRG incidence around any r=2 pair gives an exact eight-vertex
    double-neighbour board with four pair-indexed transversal candidates.
    Closing one of those candidates is exactly the forbidden
    {-2,-2,-1} motif.

Neither hostile table is a global matrix, frame, graph, or completion.
The partial 99-vertex incidence controls deliberately leave most
outside-outside adjacencies unspecified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path
from typing import Any, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "exact-results.json"

FROZEN_INPUTS = {
    "agents/2026-07-24-wave32-indecomposable-proof.md":
        "5e0e0ce6e33cd8f943d8026c2b9b01b74d9668234d4c9b2c46da6c0c9921b8ef",
    "attempts/wave32-indecomposable/exact_check.py":
        "52bb6a1f9972c981779e9aa9269bd82bb89866cde68a911498e00a4c679dbdae",
    "attempts/wave32-indecomposable/exact-results.json":
        "bccde9635d973e030e004800abc08c37089e036faca1edc2bb85ed70ee731472",
    "verification/wave32-indecomposable/audit.md":
        "15285e618b3a38c91c5d2e373dcb859720a2062d9ca108cd79cae12506a53f44",
    "verification/wave32-indecomposable/independent-results.json":
        "4b90ef54358a14abc92c925c8e0f94ed9510b4f80857fde5aa4e2abf4ba89e2a",
    "agents/2026-07-24-wave31-survivor-proof.md":
        "075566744e2622a4dfa402a125d394aef16dfcb3fc53b172176dce88bd951aaa",
    "verification/wave31-sign-commutant/audit.md":
        "f6145a3c4f4e787b23440a6ea071d606477821abab0ab8e7e5fe52042d6528a0",
    "verification/wave33-continuation-protocol.md":
        "b98b6bb8228b54b67cd949ee1bf6eb05ebd6ebe74f1cbc9e49b041a55e2d2fe6",
    "agents/2026-07-23-wave20-global-schur.md":
        "64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632",
    "verification/2026-07-23-wave20-global-schur-audit.md":
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "agents/2026-07-24-wave32-rooted-proof.md":
        "04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0",
    "verification/wave32-rooted-vector/audit.md":
        "36d83232d82e30205e0aefa30aedff0a517de1edb0adbaa54575ea68d04ce1a5",
}

RELATIONS = ("D", "G", "R0", "R1", "R2", "R3")
OFF_DIAGONAL_RELATIONS = RELATIONS[1:]

# Entry values in the basis I,J,Gamma,C and in M=3I+J-Gamma-C.
FEATURES = {
    "D":  {"I": 1, "J": 1, "Gamma": 0, "C": 0, "M": 4},
    "G":  {"I": 0, "J": 1, "Gamma": 1, "C": 0, "M": 0},
    "R0": {"I": 0, "J": 1, "Gamma": 0, "C": 0, "M": 1},
    "R1": {"I": 0, "J": 1, "Gamma": 0, "C": 1, "M": 0},
    "R2": {"I": 0, "J": 1, "Gamma": 0, "C": 2, "M": -1},
    "R3": {"I": 0, "J": 1, "Gamma": 0, "C": 3, "M": -2},
}

# Tables on the five off-diagonal types G,R0,R1,R2,R3.  The two omitted
# diagonal third-index cases are added by full_local_table().
MOTIF_ZERO_TABLE = (
    (2, 9,   2, 1, 4),
    (9, 7,   0, 0, 6),
    (2, 0, 172, 0, 0),
    (1, 0,   0, 4, 0),
    (4, 6,   0, 0, 0),
)

MOTIF_ONE_TABLE = (
    (2, 10,   0, 2, 4),
    (10, 3,   3, 1, 5),
    (0,  3, 171, 0, 0),
    (2,  1,   0, 2, 0),
    (4,  5,   0, 0, 1),
)

BASIS = ("I", "J", "Gamma", "C")
EXPECTED_R2_CONTRACTION = (
    (0, 1,   0,   2),
    (1, 231, 18, 216),
    (0, 18,  2,  16),
    (2, 216, 16, 188),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_inputs() -> dict[str, str]:
    actual: dict[str, str] = {}
    for relative, expected in FROZEN_INPUTS.items():
        digest = sha256_file(REPO_ROOT / relative)
        if digest != expected:
            raise AssertionError(
                f"frozen input changed: {relative}: {digest} != {expected}"
            )
        actual[relative] = digest
    return actual


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    if len(left) != len(right):
        raise AssertionError("dot-product dimensions differ")
    return sum(a * b for a, b in zip(left, right))


def matrix_subtract(
    left: Sequence[Sequence[int]],
    right: Sequence[Sequence[int]],
) -> list[list[int]]:
    if len(left) != len(right):
        raise AssertionError("matrix row dimensions differ")
    return [
        [a - b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def row_sums(matrix: Sequence[Sequence[int]]) -> list[int]:
    return [sum(row) for row in matrix]


def column_sums(matrix: Sequence[Sequence[int]]) -> list[int]:
    return [
        sum(matrix[i][j] for i in range(len(matrix)))
        for j in range(len(matrix[0]))
    ]


def full_local_table(
    off_diagonal: Sequence[Sequence[int]],
) -> list[list[int]]:
    """Add k=T and k=U to an R2-pair third-index table."""

    if len(off_diagonal) != 5 or any(len(row) != 5 for row in off_diagonal):
        raise AssertionError("off-diagonal table must be 5 by 5")
    table = [[0 for _ in RELATIONS] for _ in RELATIONS]
    table[RELATIONS.index("D")][RELATIONS.index("R2")] = 1
    table[RELATIONS.index("R2")][RELATIONS.index("D")] = 1
    for i, row in enumerate(off_diagonal, start=1):
        for j, value in enumerate(row, start=1):
            table[i][j] = value
    return table


def contraction(
    table: Sequence[Sequence[int]],
    left_feature: str,
    right_feature: str,
) -> int:
    return sum(
        table[i][j]
        * FEATURES[left_relation][left_feature]
        * FEATURES[right_relation][right_feature]
        for i, left_relation in enumerate(RELATIONS)
        for j, right_relation in enumerate(RELATIONS)
    )


def contraction_matrix(
    table: Sequence[Sequence[int]],
    basis: Sequence[str] = BASIS,
) -> list[list[int]]:
    return [
        [contraction(table, left, right) for right in basis]
        for left in basis
    ]


def spectral_algebra() -> dict[str, Any]:
    gamma_eigenvalues = (18, 7, 0, -3)
    multiplicities = (1, 54, 44, 132)
    c_eigenvalues = tuple(
        value * value - 5 * value - 18
        for value in gamma_eigenvalues
    )
    if c_eigenvalues != (216, -4, -18, 6):
        raise AssertionError("C spectrum changed")

    identities = {
        "Gamma_squared": (18, 0, 5, 1),
        "Gamma_times_C": (-18, 18, -2, -1),
        "C_squared": (72, 216, -16, -14),
    }

    def evaluate(coefficients: Sequence[int], index: int) -> int:
        i_value = 1
        j_value = 231 if index == 0 else 0
        gamma_value = gamma_eigenvalues[index]
        c_value = c_eigenvalues[index]
        return dot(coefficients, (i_value, j_value, gamma_value, c_value))

    expected_products = {
        "Gamma_squared": tuple(v * v for v in gamma_eigenvalues),
        "Gamma_times_C": tuple(
            gamma_eigenvalues[i] * c_eigenvalues[i] for i in range(4)
        ),
        "C_squared": tuple(v * v for v in c_eigenvalues),
    }
    for name, coefficients in identities.items():
        actual = tuple(evaluate(coefficients, index) for index in range(4))
        if actual != expected_products[name]:
            raise AssertionError(f"{name} multiplication identity failed")

    m_coefficients = (3, 1, -1, -1)
    m_eigenvalues = tuple(evaluate(m_coefficients, index) for index in range(4))
    if m_eigenvalues != (0, 0, 21, 0):
        raise AssertionError("M is not the scaled zero-projector")

    # For any k>=0,
    # N^T A^k N=(3I+Gamma)(Gamma-4I)^k.  The right side is a polynomial
    # in Gamma and hence lies in the same four-dimensional algebra.
    incidence_spectral_values: dict[str, list[int]] = {}
    for exponent in range(6):
        values = [
            (3 + gamma) * (gamma - 4) ** exponent
            for gamma in gamma_eigenvalues
        ]
        incidence_spectral_values[str(exponent)] = values
        if values[-1] != 0:
            raise AssertionError("incidence contraction did not kill ker(N)")

    return {
        "Gamma_spectrum": [
            {"eigenvalue": value, "multiplicity": multiplicity}
            for value, multiplicity in zip(gamma_eigenvalues, multiplicities)
        ],
        "C_definition": "C=Gamma^2-5*Gamma-18*I",
        "C_spectrum": list(c_eigenvalues),
        "basis": ["I", "J", "Gamma", "C"],
        "multiplication_identities": {
            "Gamma^2": "18*I+5*Gamma+C",
            "Gamma*C": "-18*I+18*J-2*Gamma-C",
            "C^2": "72*I+216*J-16*Gamma-14*C",
        },
        "M_definition": "M=3*I+J-Gamma-C",
        "M_spectrum": list(m_eigenvalues),
        "incidence_reduction": {
            "identity": "N^T*A^k*N=(3I+Gamma)*(Gamma-4I)^k",
            "checked_exponents": list(range(6)),
            "spectral_values": incidence_spectral_values,
            "conclusion": (
                "Every fully contracted two-leg expression obtained from "
                "N, N^T, and a polynomial in A lies in Q[Gamma]."
            ),
            "does_not_cover": (
                "uncontracted vertex labels or genuine three-leg and "
                "higher incidence compatibility"
            ),
        },
    }


def validate_local_table(
    name: str,
    table: Sequence[Sequence[int]],
) -> dict[str, Any]:
    expected_margins = [1, 18, 22, 174, 6, 10]
    if any(value < 0 or not isinstance(value, int)
           for row in table for value in row):
        raise AssertionError(f"{name} is not nonnegative integral")
    if any(table[i][j] != table[j][i]
           for i in range(6) for j in range(6)):
        raise AssertionError(f"{name} is not symmetric")
    if row_sums(table) != expected_margins:
        raise AssertionError(f"{name} row margins failed")
    if column_sums(table) != expected_margins:
        raise AssertionError(f"{name} column margins failed")

    actual_contraction = contraction_matrix(table)
    expected_contraction = [list(row) for row in EXPECTED_R2_CONTRACTION]
    if actual_contraction != expected_contraction:
        raise AssertionError(f"{name} adjacency-algebra contractions failed")

    m_squared_entry = contraction(table, "M", "M")
    if m_squared_entry != -21:
        raise AssertionError(f"{name} does not satisfy (M^2)_TU=-21")

    return {
        "relation_order": list(RELATIONS),
        "table": [list(row) for row in table],
        "row_and_column_margins": dict(zip(RELATIONS, expected_margins)),
        "q_endpoint_values": [2, 2],
        "base_pair_relation": "R2 / C=2 / M=-1",
        "basis_order": list(BASIS),
        "basis_contraction_matrix": actual_contraction,
        "projector_contraction_M_squared": m_squared_entry,
        "common_R3_neighbours": table[5][5],
    }


def local_moment_controls() -> dict[str, Any]:
    zero_table = full_local_table(MOTIF_ZERO_TABLE)
    one_table = full_local_table(MOTIF_ONE_TABLE)
    zero_result = validate_local_table("motif-zero table", zero_table)
    one_result = validate_local_table("motif-one table", one_table)

    delta = matrix_subtract(one_table, zero_table)
    if row_sums(delta) != [0] * 6 or column_sums(delta) != [0] * 6:
        raise AssertionError("null trade changed relation margins")
    if contraction_matrix(delta) != [[0] * 4 for _ in range(4)]:
        raise AssertionError("null trade is visible to Q[Gamma]")
    if contraction(delta, "M", "M") != 0:
        raise AssertionError("null trade changed the projector contraction")
    if delta[5][5] != 1:
        raise AssertionError("null trade did not change the decisive count")

    return {
        "interpretation": (
            "For a fixed ordered R2 pair (T,U), entry (a,b) counts third "
            "triangles V with relation a from T and relation b to U."
        ),
        "motif_zero": zero_result,
        "motif_one": one_result,
        "null_trade_one_minus_zero": [list(row) for row in delta],
        "null_trade_checks": {
            "all_relation_margins_zero": True,
            "all_Q_Gamma_bilinear_contractions_zero": True,
            "M_squared_contraction_zero": True,
            "change_in_common_R3_count": 1,
        },
        "universal_blindness": (
            "Bilinearity implies that both tables give the same "
            "(FG)[T,U] for every F,G in Q[Gamma]."
        ),
        "scope": (
            "Exact local moment controls only. They are not globally "
            "compatible relation tensors, 231-by-231 matrices, projectors, "
            "frames, incidence structures, or graphs."
        ),
    }


def edge_key(left: str, right: str) -> tuple[str, str]:
    if left == right:
        raise AssertionError("loops are not allowed")
    return tuple(sorted((left, right)))


def add_edge(edges: set[tuple[str, str]], left: str, right: str) -> None:
    edges.add(edge_key(left, right))


def adjacent(edges: set[tuple[str, str]], left: str, right: str) -> bool:
    return left != right and edge_key(left, right) in edges


def common_neighbour_count(
    vertices: Sequence[str],
    edges: set[tuple[str, str]],
    left: str,
    right: str,
) -> int:
    return sum(
        adjacent(edges, left, vertex) and adjacent(edges, right, vertex)
        for vertex in vertices
        if vertex not in (left, right)
    )


def base_n3_configuration() -> tuple[list[str], set[tuple[str, str]]]:
    t_vertices = ["t0", "t1", "t2"]
    u_vertices = ["u0", "u1", "u2"]
    vertices = t_vertices + u_vertices
    edges: set[tuple[str, str]] = set()
    for triangle in (t_vertices, u_vertices):
        for left, right in combinations(triangle, 2):
            add_edge(edges, left, right)
    add_edge(edges, "t0", "u0")
    add_edge(edges, "t1", "u1")
    return vertices, edges


def double_neighbour_board() -> dict[str, Any]:
    base_vertices, base_edges = base_n3_configuration()
    t_vertices = base_vertices[:3]
    u_vertices = base_vertices[3:]

    cell_counts: list[list[int]] = []
    for left in t_vertices:
        row: list[int] = []
        for right in u_vertices:
            target = 1 if adjacent(base_edges, left, right) else 2
            already_inside = common_neighbour_count(
                base_vertices, base_edges, left, right
            )
            remainder = target - already_inside
            if remainder < 0:
                raise AssertionError("base N3 already violates SRG parameters")
            row.append(remainder)
        cell_counts.append(row)
    expected_cells = [[1, 0, 1], [0, 1, 1], [1, 1, 2]]
    if cell_counts != expected_cells:
        raise AssertionError("eight-vertex board changed")
    if sum(sum(row) for row in cell_counts) != 8:
        raise AssertionError("double-neighbour board does not have eight vertices")

    cross_degrees_t = [1, 1, 0]
    cross_degrees_u = [1, 1, 0]
    row_only = [
        14 - 2 - cross_degrees_t[i] - sum(cell_counts[i])
        for i in range(3)
    ]
    column_only = [
        14 - 2 - cross_degrees_u[j]
        - sum(cell_counts[i][j] for i in range(3))
        for j in range(3)
    ]
    if row_only != [9, 9, 8] or column_only != [9, 9, 8]:
        raise AssertionError("single-side outside census changed")
    neither = 93 - sum(row_only) - sum(column_only) - 8
    if neither != 33:
        raise AssertionError("neither-side outside census changed")

    board_vertices: list[dict[str, Any]] = []
    for i, j in product(range(3), repeat=2):
        for copy in range(cell_counts[i][j]):
            board_vertices.append({
                "name": f"b{i}{j}_{copy}",
                "t_index": i,
                "u_index": j,
                "copy": copy,
            })

    transversal_candidates: list[list[str]] = []
    for triple in combinations(board_vertices, 3):
        if len({item["t_index"] for item in triple}) != 3:
            continue
        if len({item["u_index"] for item in triple}) != 3:
            continue
        transversal_candidates.append(sorted(item["name"] for item in triple))
    transversal_candidates.sort()
    if len(transversal_candidates) != 4:
        raise AssertionError("transversal candidate count is not four")

    return {
        "base_pair": {
            "triangles": [t_vertices, u_vertices],
            "cross_edges": [["t0", "u0"], ["t1", "u1"]],
            "relation": "R2 / exactly two independent cross edges",
        },
        "cell_rows": t_vertices,
        "cell_columns": u_vertices,
        "both_side_common_neighbour_counts": cell_counts,
        "board_vertices": board_vertices,
        "board_size": len(board_vertices),
        "row_only_counts": row_only,
        "column_only_counts": column_only,
        "neither_side_count": neither,
        "outside_vertex_total": 93,
        "transversal_candidates": transversal_candidates,
        "transversal_candidate_count_per_R2_pair": 4,
        "pair_indexed_candidates_at_n3_708": 4 * 708,
        "equivalence": (
            "A triangle on one board vertex from every row and every column "
            "is exactly a triangle V that is R3 from both base triangles."
        ),
    }


def partial_incidence_control(close_one_candidate: bool) -> dict[str, Any]:
    board = double_neighbour_board()
    base_vertices, edges = base_n3_configuration()
    t_vertices = base_vertices[:3]
    u_vertices = base_vertices[3:]

    outside: list[dict[str, Any]] = []
    for item in board["board_vertices"]:
        outside.append({
            "name": item["name"],
            "t_index": item["t_index"],
            "u_index": item["u_index"],
        })
    for i, count in enumerate(board["row_only_counts"]):
        for copy in range(count):
            outside.append({
                "name": f"rt{i}_{copy}",
                "t_index": i,
                "u_index": None,
            })
    for j, count in enumerate(board["column_only_counts"]):
        for copy in range(count):
            outside.append({
                "name": f"cu{j}_{copy}",
                "t_index": None,
                "u_index": j,
            })
    for copy in range(board["neither_side_count"]):
        outside.append({
            "name": f"n_{copy}",
            "t_index": None,
            "u_index": None,
        })
    if len(outside) != 93 or len({item["name"] for item in outside}) != 93:
        raise AssertionError("partial control does not have 93 outside vertices")

    for item in outside:
        if item["t_index"] is not None:
            add_edge(edges, item["name"], t_vertices[item["t_index"]])
        if item["u_index"] is not None:
            add_edge(edges, item["name"], u_vertices[item["u_index"]])

    closed_candidates: list[list[str]] = []
    if close_one_candidate:
        selected = ["b00_0", "b11_0", "b22_0"]
        for left, right in combinations(selected, 2):
            add_edge(edges, left, right)
        closed_candidates.append(selected)

    vertices = base_vertices + [item["name"] for item in outside]
    if len(vertices) != 99:
        raise AssertionError("partial control does not have 99 vertices")

    degrees = {
        vertex: sum(adjacent(edges, vertex, other) for other in vertices)
        for vertex in vertices
    }
    if any(degrees[vertex] != 14 for vertex in base_vertices):
        raise AssertionError("a base vertex does not have its exact degree")
    if max(degrees.values()) > 14:
        raise AssertionError("a partial degree already exceeds 14")

    cap_violations: list[dict[str, Any]] = []
    for left, right in combinations(vertices, 2):
        is_edge = adjacent(edges, left, right)
        common = common_neighbour_count(vertices, edges, left, right)
        cap = 1 if is_edge else 2
        if common > cap:
            cap_violations.append({
                "left": left,
                "right": right,
                "edge": is_edge,
                "common_neighbours_already_present": common,
                "cap": cap,
            })
    if cap_violations:
        raise AssertionError("partial control already violates lambda/mu caps")

    for left, right in combinations(base_vertices, 2):
        target = 1 if adjacent(edges, left, right) else 2
        actual = common_neighbour_count(vertices, edges, left, right)
        if actual != target:
            raise AssertionError("base-pair lambda/mu equation is incomplete")

    actual_closed: list[list[str]] = []
    for candidate in board["transversal_candidates"]:
        if all(adjacent(edges, left, right)
               for left, right in combinations(candidate, 2)):
            actual_closed.append(candidate)
    if actual_closed != closed_candidates:
        raise AssertionError("partial control has an unexpected closed candidate")

    board_names = [item["name"] for item in board["board_vertices"]]
    fixed_absent_board_edges = [
        list(edge_key(left, right))
        for left, right in combinations(board_names, 2)
        if not adjacent(edges, left, right)
    ]

    return {
        "mode": "one_closed_transversal" if close_one_candidate else "motif_free",
        "vertex_count": len(vertices),
        "fixed_present_edge_count": len(edges),
        "base_vertex_degrees": {
            vertex: degrees[vertex] for vertex in base_vertices
        },
        "maximum_current_outside_degree": max(
            degrees[vertex] for vertex in vertices if vertex not in base_vertices
        ),
        "all_present_pair_common_neighbour_caps_pass": True,
        "all_base_pair_lambda_mu_counts_exact": True,
        "fixed_absent_board_edges": fixed_absent_board_edges,
        "closed_transversal_candidates": actual_closed,
        "closed_transversal_count": len(actual_closed),
        "scope": (
            "A partial 99-vertex edge assignment only. Most "
            "outside-outside adjacencies and all missing outside degrees and "
            "lambda/mu completions remain unspecified. This is not an SRG "
            "extension or a graph construction."
        ),
    }


def actual_incidence_reduction() -> dict[str, Any]:
    board = double_neighbour_board()
    motif_free = partial_incidence_control(False)
    motif_one = partial_incidence_control(True)
    if motif_free["closed_transversal_count"] != 0:
        raise AssertionError("motif-free partial control is not motif-free")
    if motif_one["closed_transversal_count"] != 1:
        raise AssertionError("positive partial control did not close one motif")
    return {
        "board": board,
        "partial_controls": {
            "motif_free": motif_free,
            "motif_one": motif_one,
        },
        "rootless_clause": (
            "For each of the 708 unordered R2 pairs, all four pair-indexed "
            "transversal candidates must fail to be graph triangles."
        ),
        "remaining_obligation": (
            "Prove that the full SRG and projector/Schur compatibility "
            "cannot keep all 2832 pair-indexed candidates open, or construct "
            "a complete endpoint satisfying them."
        ),
    }


def mixed_trace_identity() -> dict[str, Any]:
    # A three-vertex relation pattern with one R2 edge and two R3 edges is
    # counted from each orientation of its R2 edge.
    relation_edges = ("R2", "R3", "R3")
    r2_edge_choices = sum(value == "R2" for value in relation_edges)
    ordered_orientations = 2 * r2_edge_choices
    if ordered_orientations != 2:
        raise AssertionError("mixed-trace normalization changed")
    return {
        "identity": (
            "tr(A_R2*A_R3^2)=sum_(ordered R2 pairs T,U) "
            "#{V: T R3 V and V R3 U}"
        ),
        "unordered_motif_multiplier": ordered_orientations,
        "rootless_required_value": 0,
        "actual_incidence_forces_positive_value": "UNKNOWN",
    }


def strongest_self_objection() -> dict[str, Any]:
    return {
        "objection": (
            "The null trade is local and the 99-vertex controls are partial. "
            "They do not prove that either table extends simultaneously "
            "across all triangle pairs, satisfies uncontracted three-leg "
            "incidence, realizes M^2=21M as a global matrix, or comes from "
            "an srg(99,14,1,2). A global compatibility theorem could still "
            "force the mixed trace positive."
        ),
        "disposition": "VALID_AND_BLOCKING",
        "effect": (
            "The controls delimit failed moment routes but do not exclude "
            "the rootless endpoint or change any global status."
        ),
    }


def build_result() -> dict[str, Any]:
    return {
        "scope": (
            "Exact tensor/adjacency-algebra and actual local-incidence "
            "reductions for the Wave 33 rootless mixed-motif branch."
        ),
        "inputs": validate_inputs(),
        "spectral_and_incidence_algebra": spectral_algebra(),
        "local_moment_controls": local_moment_controls(),
        "actual_incidence_board": actual_incidence_reduction(),
        "mixed_trace": mixed_trace_identity(),
        "strongest_self_objection": strongest_self_objection(),
        "status": {
            "Q_Gamma_two_leg_local_blindness": "DERIVED",
            "fully_contracted_two_leg_incidence_local_blindness": "DERIVED",
            "eight_vertex_board_and_four_candidates_per_R2_pair": "DERIVED",
            "actual_incidence_forces_positive_mixed_trace": "UNKNOWN",
            "rootless_indecomposable_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "uses_automorphism": False,
        "constructs_global_graph_or_endpoint": False,
    }


def render(value: Any) -> str:
    return json.dumps(
        value, indent=2, sort_keys=True, ensure_ascii=True
    ) + "\n"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(value), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--stdout", action="store_true")
    arguments = parser.parse_args()
    result = build_result()
    if arguments.stdout:
        print(render(result), end="")
    else:
        write_json(arguments.output, result)
        print(json.dumps({
            "output": str(arguments.output),
            "sha256": hashlib.sha256(
                render(result).encode("utf-8")
            ).hexdigest(),
            "status": result["status"],
        }, sort_keys=True))


if __name__ == "__main__":
    main()
