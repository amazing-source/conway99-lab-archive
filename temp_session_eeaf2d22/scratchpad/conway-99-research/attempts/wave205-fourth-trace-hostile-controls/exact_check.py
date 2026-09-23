"""Exact hostile controls for Wave 205 fourth-trace globalization.

This file is intentionally self-contained.  It reconstructs three rank-six
orthogonal projectors over F_3, their seven-column singular simplices, a
99-point/231-block linear triple system, and two labelwise realizations.

The two realizations have the same full pairwise projector-trace matrix.  They
also agree on every edge of the 14-regular point graph, while their alternating
fourth traces differ on 3,888 ordered nonedge pairs.

This is a relaxed control, not an srg(99,14,1,2) or endpoint configuration.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any, Iterable


FIELD = 3
ROOT = Path(__file__).resolve().parents[2]
EXPECTED_INPUTS = {
    "attempts/wave205-fourth-trace-globalization/protocol.md":
        "a1d45fc0a82b9944a9e020ded3945e75944e0e00202eacbb20eb05598e30bf4d",
    "verification/wave204-global-compatibility-verifier/package-manifest.sha256":
        "48cd018c7f7cebe7f2bc93a6dbd9440422f8dc843bc6c0fa96b29968e440f9c2",
    "verification/2026-07-29-wave204-orchestrator.md":
        "7760a4c5a4b6a501262bbb3b061828725cd23c6837fd724fada84d94a3124edd",
    "attempts/wave204-projector-fourth-order-proof-b/exact_check.py":
        "2aa6e2560e0e03c41ea202f2c2550bb3c6aa35436a27a0ccaa27becee297dfff",
    "attempts/wave204-projector-fourth-order-proof-b/exact-results.json":
        "008b098012807fa98a3874df641575c49e7030e120e4417c8eada153c792b151",
}

Matrix = list[list[int]]


def mod(value: int) -> int:
    return value % FIELD


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def identity(size: int) -> Matrix:
    return [[int(row == column) for column in range(size)] for row in range(size)]


def diagonal(entries: Iterable[int]) -> Matrix:
    values = [mod(entry) for entry in entries]
    return [
        [values[row] if row == column else 0 for column in range(len(values))]
        for row in range(len(values))
    ]


def zero_matrix(height: int, width: int) -> Matrix:
    return [[0] * width for _ in range(height)]


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [mod(left[row][column] + right[row][column]) for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def scalar_matrix(scalar: int, matrix: Matrix) -> Matrix:
    return [[mod(scalar * entry) for entry in row] for row in matrix]


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shape mismatch")
    return [
        [
            mod(
                sum(
                    left[row][inner] * right[inner][column]
                    for inner in range(len(right))
                )
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_trace(matrix: Matrix) -> int:
    return mod(sum(matrix[index][index] for index in range(len(matrix))))


def flatten(matrix: Matrix) -> list[int]:
    return [entry for row in matrix for entry in row]


def gf3_rref(matrix: Matrix) -> tuple[Matrix, list[int]]:
    if not matrix:
        return [], []
    rows = [[mod(entry) for entry in row] for row in matrix]
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("ragged matrix")
    pivots: list[int] = []
    pivot_row = 0
    for column in range(width):
        source = next(
            (row for row in range(pivot_row, len(rows)) if rows[row][column]),
            None,
        )
        if source is None:
            continue
        rows[pivot_row], rows[source] = rows[source], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], -1, FIELD)
        rows[pivot_row] = [mod(inverse * entry) for entry in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            multiplier = rows[row][column]
            rows[row] = [
                mod(rows[row][index] - multiplier * rows[pivot_row][index])
                for index in range(width)
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return rows, pivots


def gf3_rank(matrix: Matrix) -> int:
    return len(gf3_rref(matrix)[1])


def gf3_inverse(matrix: Matrix) -> Matrix:
    if len(matrix) != len(matrix[0]):
        raise ValueError("inverse requires square matrix")
    size = len(matrix)
    augmented = [
        [mod(entry) for entry in matrix[row]] + identity(size)[row]
        for row in range(size)
    ]
    reduced, pivots = gf3_rref(augmented)
    if pivots[:size] != list(range(size)):
        raise ValueError("singular matrix")
    return [row[size:] for row in reduced]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inputs() -> dict[str, str]:
    observed = {relative: sha256(ROOT / relative) for relative in EXPECTED_INPUTS}
    if observed != EXPECTED_INPUTS:
        raise AssertionError({"expected": EXPECTED_INPUTS, "observed": observed})
    return observed


AMBIENT_FORM = diagonal([1] * 10 + [2])
SMALL_BASES = {
    "P": [
        [1, 0],
        [0, 1],
        [0, 0],
        [0, 0],
        [0, 0],
    ],
    "Q1": [
        [1, 2],
        [1, 0],
        [2, 1],
        [2, 0],
        [1, 1],
    ],
    "Q2": [
        [1, 1],
        [1, 1],
        [0, 1],
        [1, 2],
        [1, 2],
    ],
}
SIMPLEX_COEFFICIENT_ROWS = {
    "P": [
        [1, 1, 1, 0, 0, 0],
        [2, 1, 1, 0, 0, 0],
        [0, 2, 2, 1, 0, 0],
        [0, 1, 0, 2, 1, 0],
        [0, 1, 0, 2, 2, 0],
        [0, 0, 1, 2, 0, 1],
    ],
    "Q1": [
        [0, 1, 0, 0, 0, 0],
        [2, 2, 0, 0, 0, 0],
        [2, 0, 1, 0, 0, 0],
        [2, 0, 2, 1, 0, 1],
        [2, 0, 2, 2, 0, 1],
        [2, 0, 2, 0, 1, 2],
    ],
    "Q2": [
        [1, 1, 0, 0, 0, 0],
        [2, 1, 0, 0, 0, 0],
        [0, 2, 1, 0, 0, 0],
        [0, 2, 2, 1, 0, 1],
        [0, 2, 2, 2, 0, 1],
        [0, 2, 2, 0, 1, 2],
    ],
}


def coordinate_vector(index: int) -> list[int]:
    return [int(row == index) for row in range(11)]


def embedded_basis(name: str) -> Matrix:
    small = SMALL_BASES[name]
    columns = [
        [small[row][column] if row < 5 else 0 for row in range(11)]
        for column in range(2)
    ]
    columns.extend([coordinate_vector(5), coordinate_vector(6)])
    columns.extend(
        [coordinate_vector(7), coordinate_vector(8)]
        if name == "P"
        else [coordinate_vector(9), coordinate_vector(10)]
    )
    return transpose(columns)


def gram(columns: Matrix) -> Matrix:
    return matrix_multiply(matrix_multiply(transpose(columns), AMBIENT_FORM), columns)


def orthogonal_projector(basis: Matrix) -> Matrix:
    return matrix_multiply(
        matrix_multiply(
            matrix_multiply(basis, gf3_inverse(gram(basis))),
            transpose(basis),
        ),
        AMBIENT_FORM,
    )


def simplex_columns(name: str, basis: Matrix) -> Matrix:
    first_six = matrix_multiply(
        basis, transpose(SIMPLEX_COEFFICIENT_ROWS[name])
    )
    seventh = [
        mod(-sum(first_six[row][column] for column in range(6)))
        for row in range(11)
    ]
    return [first_six[row] + [seventh[row]] for row in range(11)]


def rank_one_operator(vector: list[int]) -> Matrix:
    column = [[entry] for entry in vector]
    return matrix_multiply(
        matrix_multiply(column, transpose(column)),
        AMBIENT_FORM,
    )


def frame_operator(column_vectors: list[list[int]]) -> Matrix:
    result = zero_matrix(11, 11)
    for vector in column_vectors:
        result = matrix_add(result, rank_one_operator(vector))
    return result


def normalized_direction(vector: list[int]) -> tuple[int, ...]:
    first = next((entry for entry in vector if entry), None)
    if first is None:
        raise AssertionError("zero vector")
    inverse = pow(first, -1, FIELD)
    return tuple(mod(inverse * entry) for entry in vector)


def local_objects() -> tuple[dict[str, Matrix], dict[str, Matrix], dict[str, Matrix]]:
    bases = {name: embedded_basis(name) for name in SMALL_BASES}
    projectors = {name: orthogonal_projector(basis) for name, basis in bases.items()}
    simplices = {
        name: simplex_columns(name, basis) for name, basis in bases.items()
    }
    simplex_gram = [[0 if row == column else 1 for column in range(7)] for row in range(7)]
    for name in bases:
        projector = projectors[name]
        columns = simplices[name]
        if matrix_multiply(projector, projector) != projector:
            raise AssertionError(f"{name}: not idempotent")
        if matrix_multiply(transpose(projector), AMBIENT_FORM) != matrix_multiply(
            AMBIENT_FORM, projector
        ):
            raise AssertionError(f"{name}: not self-adjoint")
        if gf3_rank(projector) != 6 or matrix_trace(projector) != 0:
            raise AssertionError(f"{name}: rank or trace changed")
        if gram(columns) != simplex_gram:
            raise AssertionError(f"{name}: simplex Gram changed")
        vectors = transpose(columns)
        if [mod(sum(row)) for row in columns] != [0] * 11:
            raise AssertionError(f"{name}: simplex sum changed")
        if frame_operator(vectors) != scalar_matrix(2, projector):
            raise AssertionError(f"{name}: P=-sum(z tensor z) changed")
    joined = [
        bases["P"][row] + bases["Q1"][row] + bases["Q2"][row]
        for row in range(11)
    ]
    if gf3_rank(joined) != 11:
        raise AssertionError("local spaces do not span dimension 11")
    return bases, projectors, simplices


COMPONENTS = (
    {"name": "C27", "offset": 0, "size": 27, "type_a": "P", "type_b": "P"},
    {"name": "C36a", "offset": 27, "size": 36, "type_a": "Q1", "type_b": "Q2"},
    {"name": "C36b", "offset": 63, "size": 36, "type_a": "Q2", "type_b": "Q1"},
)


def component_blocks(component: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a 7-factorized linear triple system on one cyclic component."""

    offset = component["offset"]
    size = component["size"]
    blocks: list[dict[str, Any]] = []
    for index in range(size // 3):
        vertices = [index, index + size // 3, index + 2 * size // 3]
        blocks.append(
            {
                "component": component["name"],
                "color": 0,
                "vertices": [offset + vertex for vertex in vertices],
                "source": {"kind": "short_orbit", "translate": index},
            }
        )
    for base, first_color in (((0, 1, 5), 1), ((0, 2, 10), 4)):
        for translate in range(size):
            vertices = sorted({(translate + entry) % size for entry in base})
            if len(vertices) != 3:
                raise AssertionError("degenerate cyclic block")
            blocks.append(
                {
                    "component": component["name"],
                    "color": first_color + translate % 3,
                    "vertices": [offset + vertex for vertex in vertices],
                    "source": {
                        "kind": "full_orbit",
                        "base": list(base),
                        "translate": translate,
                    },
                }
            )
    return blocks


def build_blocks() -> list[dict[str, Any]]:
    blocks = [
        block
        for component in COMPONENTS
        for block in component_blocks(component)
    ]
    for block_id, block in enumerate(blocks):
        block["id"] = block_id
    if len(blocks) != 231:
        raise AssertionError("block count changed")
    return blocks


def incidence_and_graph(
    blocks: list[dict[str, Any]],
) -> tuple[Matrix, Matrix, dict[str, Any]]:
    incidence = zero_matrix(99, 231)
    for block in blocks:
        for vertex in block["vertices"]:
            incidence[vertex][block["id"]] = 1
    row_degrees = [sum(row) for row in incidence]
    column_degrees = [sum(incidence[row][column] for row in range(99)) for column in range(231)]
    if row_degrees != [7] * 99 or column_degrees != [3] * 231:
        raise AssertionError("incidence degrees changed")

    integer_bbt = [
        [
            sum(incidence[row][column] * incidence[other][column] for column in range(231))
            for other in range(99)
        ]
        for row in range(99)
    ]
    if any(integer_bbt[row][other] > 1 for row in range(99) for other in range(99) if row != other):
        raise AssertionError("triple system is not linear")
    adjacency = [
        [int(row != other and integer_bbt[row][other] == 1) for other in range(99)]
        for row in range(99)
    ]
    if [sum(row) for row in adjacency] != [14] * 99:
        raise AssertionError("point graph degree changed")
    for row in range(99):
        for other in range(99):
            expected = adjacency[row][other] + (7 if row == other else 0)
            if integer_bbt[row][other] != expected:
                raise AssertionError("integer BB^T identity changed")
            if mod(integer_bbt[row][other]) != mod(
                adjacency[row][other] + int(row == other)
            ):
                raise AssertionError("ternary BB^T identity changed")

    graph_edges = [
        (left, right)
        for left in range(99)
        for right in range(left + 1, 99)
        if adjacency[left][right]
    ]
    triangles = [
        (left, middle, right)
        for left in range(99)
        for middle in range(left + 1, 99)
        for right in range(middle + 1, 99)
        if adjacency[left][middle]
        and adjacency[left][right]
        and adjacency[middle][right]
    ]
    designated = {tuple(sorted(block["vertices"])) for block in blocks}
    extra_triangles = sorted(set(triangles) - designated)
    edge_lambda = Counter(
        sum(adjacency[left][vertex] * adjacency[right][vertex] for vertex in range(99))
        for left, right in graph_edges
    )
    nonedge_mu = Counter(
        sum(adjacency[left][vertex] * adjacency[right][vertex] for vertex in range(99))
        for left in range(99)
        for right in range(left + 1, 99)
        if not adjacency[left][right]
    )

    unseen = set(range(99))
    component_sizes: list[int] = []
    while unseen:
        start = min(unseen)
        queue: deque[int] = deque([start])
        seen = {start}
        unseen.remove(start)
        while queue:
            vertex = queue.popleft()
            for neighbor, is_edge in enumerate(adjacency[vertex]):
                if is_edge and neighbor not in seen:
                    seen.add(neighbor)
                    unseen.remove(neighbor)
                    queue.append(neighbor)
        component_sizes.append(len(seen))

    return incidence, adjacency, {
        "point_count": 99,
        "block_count": 231,
        "row_degree": 7,
        "column_degree": 3,
        "linear_triple_system": True,
        "point_graph_degree": 14,
        "point_graph_edge_count": len(graph_edges),
        "edge_partitioned_by_designated_blocks": True,
        "integer_bbt_identity": "BB^T=A+7I",
        "ternary_bbt_identity": "BB^T=A+I over F_3",
        "parallel_class_count": 7,
        "each_vertex_sees_each_color_once": all(
            sorted(block["color"] for block in blocks if vertex in block["vertices"])
            == list(range(7))
            for vertex in range(99)
        ),
        "connected_component_sizes": sorted(component_sizes),
        "all_graph_triangle_count": len(triangles),
        "designated_block_triangle_count": len(designated),
        "extra_graph_triangle_count": len(extra_triangles),
        "edge_common_neighbor_distribution": {
            str(key): edge_lambda[key] for key in sorted(edge_lambda)
        },
        "nonedge_common_neighbor_distribution": {
            str(key): nonedge_mu[key] for key in sorted(nonedge_mu)
        },
    }


def assigned_type(vertex: int, realization: str) -> str:
    key = "type_a" if realization == "A" else "type_b"
    for component in COMPONENTS:
        if component["offset"] <= vertex < component["offset"] + component["size"]:
            return component[key]
    raise AssertionError("vertex outside components")


def component_type(component_name: str, realization: str) -> str:
    key = "type_a" if realization == "A" else "type_b"
    return next(component[key] for component in COMPONENTS if component["name"] == component_name)


def realization_data(
    realization: str,
    blocks: list[dict[str, Any]],
    projectors: dict[str, Matrix],
    simplices: dict[str, Matrix],
) -> tuple[dict[str, Any], list[Matrix], list[list[int]], Matrix, Matrix]:
    projector_rows = [
        projectors[assigned_type(vertex, realization)] for vertex in range(99)
    ]
    block_vectors = [
        transpose(simplices[component_type(block["component"], realization)])[block["color"]]
        for block in blocks
    ]
    for vertex in range(99):
        incident = [
            block_vectors[block["id"]]
            for block in blocks
            if vertex in block["vertices"]
        ]
        if frame_operator(incident) != scalar_matrix(2, projector_rows[vertex]):
            raise AssertionError(f"{realization}: vertex {vertex} star coupling changed")

    projector_sum = zero_matrix(11, 11)
    for projector in projector_rows:
        projector_sum = matrix_add(projector_sum, projector)
    if projector_sum != zero_matrix(11, 11):
        raise AssertionError(f"{realization}: projector sum changed")
    if frame_operator(block_vectors) != zero_matrix(11, 11):
        raise AssertionError(f"{realization}: global column frame is not zero")

    column_matrix = transpose(block_vectors)
    centered_gram = gram(column_matrix)
    if gf3_rank(column_matrix) != 11 or gf3_rank(centered_gram) != 11:
        raise AssertionError(f"{realization}: column or Gram rank changed")
    if matrix_multiply(centered_gram, centered_gram) != zero_matrix(231, 231):
        raise AssertionError(f"{realization}: centered Gram is not square-zero")
    if any(centered_gram[index][index] for index in range(231)):
        raise AssertionError(f"{realization}: nonsingular block column")

    pair_trace: Matrix = []
    fourth_trace: Matrix = []
    for left in projector_rows:
        pair_row: list[int] = []
        fourth_row: list[int] = []
        for right in projector_rows:
            product = matrix_multiply(left, right)
            pair_row.append(matrix_trace(product))
            fourth_row.append(matrix_trace(matrix_multiply(product, product)))
        pair_trace.append(pair_row)
        fourth_trace.append(fourth_row)

    directions = Counter(normalized_direction(vector) for vector in block_vectors)
    return (
        {
            "projector_count": len(projector_rows),
            "block_column_count": len(block_vectors),
            "ambient_column_span_rank": gf3_rank(column_matrix),
            "centered_gram_rank": gf3_rank(centered_gram),
            "centered_gram_square_zero": True,
            "all_block_columns_singular": True,
            "projector_sum_zero": True,
            "global_column_frame_zero": True,
            "distinct_projective_direction_count": len(directions),
            "projective_direction_multiplicity_distribution": {
                str(key): value
                for key, value in sorted(Counter(directions.values()).items())
            },
            "type_counts": dict(
                sorted(Counter(assigned_type(vertex, realization) for vertex in range(99)).items())
            ),
        },
        projector_rows,
        block_vectors,
        pair_trace,
        fourth_trace,
    )


def distribution(matrix: Matrix) -> dict[str, int]:
    return {
        str(value): sum(entry == value for row in matrix for entry in row)
        for value in range(FIELD)
    }


def analyze() -> tuple[dict[str, Any], dict[str, Any]]:
    inputs = verify_inputs()
    bases, projectors, simplices = local_objects()
    blocks = build_blocks()
    incidence, adjacency, incidence_summary = incidence_and_graph(blocks)
    a_summary, a_projectors, a_vectors, pair_a, fourth_a = realization_data(
        "A", blocks, projectors, simplices
    )
    b_summary, b_projectors, b_vectors, pair_b, fourth_b = realization_data(
        "B", blocks, projectors, simplices
    )
    if pair_a != pair_b:
        raise AssertionError("pairwise trace matrices differ")
    differing = [
        (row, column)
        for row in range(99)
        for column in range(99)
        if fourth_a[row][column] != fourth_b[row][column]
    ]
    edge_differences = [
        (row, column)
        for row, column in differing
        if adjacency[row][column]
    ]
    nonedge_differences = [
        (row, column)
        for row, column in differing
        if row != column and not adjacency[row][column]
    ]
    edge_fourth_values = {
        "A": Counter(
            fourth_a[row][column]
            for row in range(99)
            for column in range(row + 1, 99)
            if adjacency[row][column]
        ),
        "B": Counter(
            fourth_b[row][column]
            for row in range(99)
            for column in range(row + 1, 99)
            if adjacency[row][column]
        ),
    }
    projector_coordinate_rank = {
        realization: gf3_rank([flatten(projector) for projector in rows])
        for realization, rows in (("A", a_projectors), ("B", b_projectors))
    }
    fourth_matrix_rank = {
        "A": gf3_rank(fourth_a),
        "B": gf3_rank(fourth_b),
    }

    result = {
        "claim_label": "CANDIDATE_RELAXED_CONTROL",
        "scope": (
            "exact F_3 controls with endpoint-shaped projector, column, "
            "incidence, and edge premises; not an SRG or endpoint"
        ),
        "field": FIELD,
        "inputs": inputs,
        "local_objects": {
            "ambient_dimension": 11,
            "ambient_form_diagonal": [1] * 10 + [2],
            "projector_types": ["P", "Q1", "Q2"],
            "each_projector": {
                "rank": 6,
                "trace": 0,
                "self_adjoint": True,
                "idempotent": True,
                "seven_singular_simplex_columns": True,
                "simplex_gram": "J_7-I_7",
                "projector_identity": "P=-sum(z tensor z)",
            },
            "three_star_space_span_rank": gf3_rank(
                [
                    bases["P"][row] + bases["Q1"][row] + bases["Q2"][row]
                    for row in range(11)
                ]
            ),
        },
        "incidence_control": incidence_summary,
        "realizations": {"A": a_summary, "B": b_summary},
        "comparison": {
            "same_full_pairwise_projector_trace_matrix": True,
            "pairwise_trace_entry_distribution": distribution(pair_a),
            "different_fourth_trace_matrices": True,
            "different_ordered_fourth_trace_entries": len(differing),
            "different_ordered_edge_fourth_trace_entries": len(edge_differences),
            "different_ordered_nonedge_fourth_trace_entries": len(nonedge_differences),
            "all_differences_are_nonedges": not edge_differences
            and len(differing) == len(nonedge_differences),
            "edge_fourth_trace_distributions_unordered": {
                label: {str(key): value for key, value in sorted(counter.items())}
                for label, counter in edge_fourth_values.items()
            },
            "fourth_trace_entry_distributions": {
                "A": distribution(fourth_a),
                "B": distribution(fourth_b),
            },
            "fourth_trace_matrix_rank_over_F3": fourth_matrix_rank,
            "projector_coordinate_rank_over_F3": projector_coordinate_rank,
        },
        "correct_universal_rank_ledger": {
            "self_adjoint_endomorphism_dimension": 66,
            "trace_zero_self_adjoint_dimension": 65,
            "quadratic_lift_symmetric_square_dimension": 2145,
            "universal_H_rank_bound": "rank(H)<=min(99,2145)=99",
            "bound_is_vacuous_at_99_points": True,
            "wedge2_underlying_space_dimension": 55,
            "wedge2_operator_coordinate_dimension": 3025,
            "warning": (
                "wedge^2(P_x) is an endomorphism of a 55-dimensional space, "
                "not a vector with only 55 operator coordinates"
            ),
        },
        "progressive_premise_ladder": [
            {
                "level": 0,
                "satisfied": (
                    "actual rank-six self-adjoint idempotents in a "
                    "nondegenerate 11-space have equal g and separated h"
                ),
            },
            {
                "level": 1,
                "satisfied": (
                    "99 labelled projectors, 231 labelled singular columns, "
                    "rank-11 square-zero centered Gram, sum P_x=0, and exact "
                    "seven-column star coupling"
                ),
            },
            {
                "level": 2,
                "satisfied": (
                    "99x231 binary linear triple incidence with row degree 7, "
                    "column degree 3, a 14-regular simple point graph, "
                    "BB^T=A+7I over Z and A+I over F_3"
                ),
            },
            {
                "level": 3,
                "satisfied": (
                    "the two controls agree on every point-graph edge and "
                    "separate h only on nonedges"
                ),
            },
        ],
        "failed_target_premises": [
            (
                "the 231 labelled singular columns use only 21 projective "
                "directions, so projective distinctness and dual distance at "
                "least four fail"
            ),
            (
                "the point graph is disconnected with components 27,36,36 "
                "and is not srg(99,14,1,2)"
            ),
            (
                "the designated 231 blocks partition the graph edges into "
                "triangles, but the graph has extra triangles; edge common-"
                "neighbor counts are not lambda=1"
            ),
            (
                "nonedge common-neighbor counts are not uniformly mu=2; "
                "cross-component nonedges have zero common neighbors"
            ),
            (
                "the exact 32-regular selected orthogonality graph and "
                "endpoint block-relation profiles are not imposed"
            ),
            (
                "outer-cycle types, prism-freeness, n3=4158 as an SRG "
                "four-vertex statistic, code endpoint distance, and cover "
                "constraints are not imposed"
            ),
            (
                "the controls are not graphs satisfying the Conway target, "
                "codes with the endpoint distance, covers, or endpoint "
                "configurations"
            ),
        ],
        "conclusions": {
            "construction_level_compatibility_blueprint": True,
            "pairwise_and_edge_fourth_data_force_nonedge_fourth_data": False,
            "srg_excluded": False,
            "rank_11_endpoint_excluded": False,
            "n3_4158_endpoint_excluded": False,
            "conway_99_status": "UNKNOWN",
        },
    }

    certificate = {
        "field": FIELD,
        "ambient_form": AMBIENT_FORM,
        "projectors": projectors,
        "simplices_as_11_by_7_matrices": simplices,
        "components": list(COMPONENTS),
        "blocks": blocks,
        "incidence_matrix": incidence,
        "realization_A": {
            "vertex_types": [assigned_type(vertex, "A") for vertex in range(99)],
            "block_vectors": a_vectors,
        },
        "realization_B": {
            "vertex_types": [assigned_type(vertex, "B") for vertex in range(99)],
            "block_vectors": b_vectors,
        },
    }
    return result, certificate


def verify(result: dict[str, Any], certificate: dict[str, Any]) -> None:
    incidence = result["incidence_control"]
    comparison = result["comparison"]
    if incidence["point_graph_edge_count"] != 693:
        raise AssertionError("edge count changed")
    if incidence["connected_component_sizes"] != [27, 36, 36]:
        raise AssertionError("components changed")
    if incidence["all_graph_triangle_count"] != 1329:
        raise AssertionError("triangle count changed")
    if incidence["extra_graph_triangle_count"] != 1098:
        raise AssertionError("extra triangle count changed")
    if incidence["edge_common_neighbor_distribution"] != {
        "4": 144,
        "5": 243,
        "6": 27,
        "7": 225,
        "8": 27,
        "9": 27,
    }:
        raise AssertionError("edge common-neighbor distribution changed")
    if incidence["nonedge_common_neighbor_distribution"] != {
        "0": 3240,
        "2": 144,
        "4": 180,
        "5": 27,
        "6": 315,
        "7": 27,
        "8": 225,
    }:
        raise AssertionError("nonedge common-neighbor distribution changed")
    if comparison["different_ordered_fourth_trace_entries"] != 3888:
        raise AssertionError("fourth separation changed")
    if comparison["different_ordered_edge_fourth_trace_entries"] != 0:
        raise AssertionError("edge fourth traces separated")
    if comparison["different_ordered_nonedge_fourth_trace_entries"] != 3888:
        raise AssertionError("nonedge fourth separation changed")
    if comparison["pairwise_trace_entry_distribution"] != {
        "0": 3321,
        "1": 2592,
        "2": 3888,
    }:
        raise AssertionError("pair distribution changed")
    if comparison["fourth_trace_entry_distributions"] != {
        "A": {"0": 3321, "1": 1944, "2": 4536},
        "B": {"0": 3321, "1": 1944, "2": 4536},
    }:
        raise AssertionError("fourth distributions changed")
    if comparison["edge_fourth_trace_distributions_unordered"] != {
        "A": {"0": 693},
        "B": {"0": 693},
    }:
        raise AssertionError("edge fourth values changed")
    if len(certificate["blocks"]) != 231:
        raise AssertionError("certificate block count changed")
    if result["conclusions"]["srg_excluded"]:
        raise AssertionError("status inflation")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-results", type=Path)
    parser.add_argument("--write-certificate", type=Path)
    parser.add_argument("--verify-results", type=Path)
    parser.add_argument("--verify-certificate", type=Path)
    args = parser.parse_args()
    result, certificate = analyze()
    verify(result, certificate)
    if args.verify_results:
        observed = json.loads(args.verify_results.read_text(encoding="utf-8"))
        if observed != result:
            raise AssertionError("frozen results differ")
    if args.verify_certificate:
        observed = json.loads(args.verify_certificate.read_text(encoding="utf-8"))
        if observed != certificate:
            raise AssertionError("frozen certificate differs")
    if args.write_results:
        write_json(args.write_results, result)
    if args.write_certificate:
        write_json(args.write_certificate, certificate)
    if not any(
        (
            args.write_results,
            args.write_certificate,
            args.verify_results,
            args.verify_certificate,
        )
    ):
        print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS: Wave205 hostile fourth-trace controls")


if __name__ == "__main__":
    main()
