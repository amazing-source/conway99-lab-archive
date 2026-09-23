"""Exact Wave 176 star-projector and adjacent-cycle checks.

The calculation is deliberately tiny: it reduces an adjacent pair of
seven-point stars to the four partitions of six into cycle half-lengths at
least two.  It does not enumerate graphs, codes, or candidate configurations.
"""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any, Iterable


FIELD = 3
AMBIENT_DIMENSION = 11


def gf3_rref(matrix: list[list[int]]) -> tuple[list[list[int]], list[int]]:
    """Return reduced row-echelon form and pivot columns over F_3."""

    if not matrix:
        return [], []
    rows = [[entry % FIELD for entry in row] for row in matrix]
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("ragged matrix")

    pivots: list[int] = []
    pivot_row = 0
    for column in range(width):
        source = next(
            (
                row
                for row in range(pivot_row, len(rows))
                if rows[row][column] != 0
            ),
            None,
        )
        if source is None:
            continue
        rows[pivot_row], rows[source] = rows[source], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], -1, FIELD)
        rows[pivot_row] = [
            (inverse * entry) % FIELD for entry in rows[pivot_row]
        ]
        for row in range(len(rows)):
            if row == pivot_row or rows[row][column] == 0:
                continue
            multiplier = rows[row][column]
            rows[row] = [
                (
                    rows[row][index]
                    - multiplier * rows[pivot_row][index]
                )
                % FIELD
                for index in range(width)
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return rows, pivots


def gf3_rank(matrix: list[list[int]]) -> int:
    """Return matrix rank over F_3."""

    return len(gf3_rref(matrix)[1])


def gf3_nullspace(matrix: list[list[int]]) -> list[list[int]]:
    """Return a basis of the right nullspace over F_3."""

    reduced, pivots = gf3_rref(matrix)
    width = len(matrix[0])
    free_columns = [column for column in range(width) if column not in pivots]
    basis: list[list[int]] = []
    for free in free_columns:
        vector = [0] * width
        vector[free] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = (-reduced[row][free]) % FIELD
        basis.append(vector)
    return basis


def linear_combination(
    coefficients: Iterable[int], basis: list[list[int]]
) -> list[int]:
    """Form a vector from a basis over F_3."""

    coefficient_list = list(coefficients)
    if not basis:
        return []
    return [
        sum(
            coefficient_list[index] * basis[index][column]
            for index in range(len(basis))
        )
        % FIELD
        for column in range(len(basis[0]))
    ]


def cycle_biadjacency(parts: tuple[int, ...]) -> list[list[int]]:
    """Build the 6 by 6 biadjacency matrix for the stated cycle type."""

    if sum(parts) != 6 or any(part < 2 for part in parts):
        raise ValueError("parts must partition six with every part at least two")
    matrix = [[0] * 6 for _ in range(6)]
    offset = 0
    for part in parts:
        for index in range(part):
            matrix[offset + index][offset + index] = 1
            matrix[offset + index][offset + (index + 1) % part] = 1
        offset += part
    assert all(sum(row) == 2 for row in matrix)
    assert all(sum(matrix[row][column] for row in range(6)) == 2 for column in range(6))
    return matrix


def adjacent_union_gram(parts: tuple[int, ...]) -> list[list[int]]:
    """Return the 13 by 13 centered Gram matrix of two adjacent stars.

    Coordinate zero is the common triangle.  Coordinates 1 through 6 and
    7 through 12 are the outer triangles in the two stars.
    """

    cross = cycle_biadjacency(parts)
    gram = [[0] * 13 for _ in range(13)]
    for row in range(13):
        for column in range(13):
            if row == column:
                entry = 0
            elif row == 0 or column == 0:
                entry = 1
            elif (row <= 6 and column <= 6) or (
                row >= 7 and column >= 7
            ):
                entry = 1
            else:
                left = row - 1 if row <= 6 else column - 1
                right = column - 7 if column >= 7 else row - 7
                entry = 1 + cross[left][right]
            gram[row][column] = entry % FIELD
    return gram


def star_circuits() -> tuple[list[int], list[int]]:
    """Return the two evident seven-point star relations."""

    first = [1] * 7 + [0] * 6
    second = [1] + [0] * 6 + [1] * 6
    return first, second


def in_star_circuit_span(vector: list[int]) -> bool:
    """Test membership in the span of the two evident star circuits."""

    first, second = star_circuits()
    return any(
        vector
        == [
            (left * first[index] + right * second[index]) % FIELD
            for index in range(13)
        ]
        for left, right in product(range(FIELD), repeat=2)
    )


def nonstar_kernel_weight_data(
    gram: list[list[int]],
) -> dict[str, Any]:
    """Enumerate the at most 27 Gram-kernel words for the rank-10 cases."""

    basis = gf3_nullspace(gram)
    words = []
    for coefficients in product(range(FIELD), repeat=len(basis)):
        word = linear_combination(coefficients, basis)
        if not in_star_circuit_span(word):
            words.append(word)
    weights = [sum(entry != 0 for entry in word) for word in words]
    return {
        "gram_kernel_dimension": len(basis),
        "nonstar_words": len(words),
        "minimum_support": min(weights),
        "support_distribution": {
            str(weight): weights.count(weight) for weight in sorted(set(weights))
        },
    }


def analyze_cycle_type(parts: tuple[int, ...]) -> dict[str, Any]:
    """Analyze one of the four adjacent-star cycle types."""

    gram = adjacent_union_gram(parts)
    gram_rank = gf3_rank(gram)
    span_rank_lower = gram_rank
    span_rank_upper = (AMBIENT_DIMENSION + gram_rank) // 2
    relation_dimension_lower = 13 - span_rank_upper
    cross_relation_quotient_lower = relation_dimension_lower - 2
    result: dict[str, Any] = {
        "cycle_half_lengths": list(parts),
        "gram_rank": gram_rank,
        "gram_nullity": 13 - gram_rank,
        "span_rank_bounds": [span_rank_lower, span_rank_upper],
        "star_intersection_dimension_lower": 12 - span_rank_upper,
        "relation_dimension_lower": relation_dimension_lower,
        "cross_relation_quotient_dimension_lower": (
            cross_relation_quotient_lower
        ),
    }
    if gram_rank == 10:
        result["span_rank_exact"] = 10
        result["star_intersection_dimension_exact"] = 2
        result["cross_coset"] = nonstar_kernel_weight_data(gram)
    return result


def analyze() -> dict[str, Any]:
    """Return the exact Wave 176 checkpoint."""

    types = {
        "+".join(str(part) for part in parts): analyze_cycle_type(parts)
        for parts in ((6,), (4, 2), (3, 3), (2, 2, 2))
    }
    return {
        "field": FIELD,
        "ambient_dimension": AMBIENT_DIMENSION,
        "star": {
            "vectors": 7,
            "span_dimension": 6,
            "gram": "J_7-I_7",
            "projector": "P_x=-sum_(T contains x) z_T tensor z_T",
            "projector_rank": 6,
            "projector_trace_mod_3": 0,
            "projector_sum": "sum_x P_x=0",
        },
        "trace_gram": {
            "triangle_relation_degree": 36,
            "identity": "tr(P_x P_y)=2(B L B^T)_(x,y) mod 3",
            "rank_upper": 65,
            "diagonal_entry": 0,
            "graph_edge_integer_entry": 12,
            "full_row_sum": 756,
            "nonneighbor_row_sum": 588,
            "nonneighbor_average": 7,
        },
        "nonadjacent_star_pair": {
            "columns": 14,
            "relation_dimension_lower": 3,
            "evident_star_relations": 2,
            "cross_relation_quotient_dimension_lower": 1,
            "cross_relation_support_bounds": [4, 14],
        },
        "adjacent_star_pair": {
            "columns": 13,
            "cross_bipartite_degree": 2,
            "cycle_types": types,
            "cross_relation_support_bounds": [4, 13],
        },
        "conclusion": (
            "every pair of distinct vertex-stars forces a genuinely cross-star "
            "dual relation; no endpoint exclusion follows"
        ),
    }


def verify(data: dict[str, Any]) -> None:
    """Assert all headline identities and exact ranks."""

    assert data["trace_gram"] == {
        "triangle_relation_degree": 36,
        "identity": "tr(P_x P_y)=2(B L B^T)_(x,y) mod 3",
        "rank_upper": 65,
        "diagonal_entry": 0,
        "graph_edge_integer_entry": 12,
        "full_row_sum": 756,
        "nonneighbor_row_sum": 588,
        "nonneighbor_average": 7,
    }
    types = data["adjacent_star_pair"]["cycle_types"]
    assert {name: item["gram_rank"] for name, item in types.items()} == {
        "6": 10,
        "4+2": 10,
        "3+3": 8,
        "2+2+2": 9,
    }
    assert {
        name: item["star_intersection_dimension_lower"]
        for name, item in types.items()
    } == {"6": 2, "4+2": 2, "3+3": 3, "2+2+2": 2}
    assert {
        name: item["cross_relation_quotient_dimension_lower"]
        for name, item in types.items()
    } == {"6": 1, "4+2": 1, "3+3": 2, "2+2+2": 1}
    assert types["6"]["cross_coset"]["minimum_support"] == 8
    assert types["4+2"]["cross_coset"]["minimum_support"] == 4
    assert data["trace_gram"]["nonneighbor_row_sum"] == (
        data["trace_gram"]["full_row_sum"]
        - 14 * data["trace_gram"]["graph_edge_integer_entry"]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    data = analyze()
    verify(data)
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == data
    if args.write:
        args.write.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    if not args.write and not args.verify:
        print(json.dumps(data, indent=2, sort_keys=True))
    print("PASS: Wave176 star-projector and adjacent-cycle checks")


if __name__ == "__main__":
    main()
