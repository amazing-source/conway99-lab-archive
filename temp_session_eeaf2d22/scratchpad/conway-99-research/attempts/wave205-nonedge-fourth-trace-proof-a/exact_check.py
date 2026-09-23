"""Exact nonedge fourth-trace controls for Wave 205 proof A.

The checker uses no solver.  It validates three complete 28-vertex local
adjacency certificates, reconstructs their centered two-star Gram matrices,
builds exact coordinates in the fixed nonsquare 11-space over F_3, and
checks every stated projector invariant.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


FIELD = 3
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXPECTED_INPUTS = {
    "attempts/wave205-fourth-trace-globalization/protocol.md":
        "a1d45fc0a82b9944a9e020ded3945e75944e0e00202eacbb20eb05598e30bf4d",
    "verification/wave171-pq-centered-code/verification-report.md":
        "1f2ba5ed92ba6bb1ccc05cd753a8e359f208c3ddc7ca85766f26f8869346414f",
    "verification/wave176-star-projector-circuits/audit.md":
        "f58577409f39e98b06bfbe206221d3d278f0c473bcf5057afc381094d5e65d05",
    "attempts/wave204-projector-fourth-order-proof-b/derivation.md":
        "2b4ddbec109ff7fba31371709be6616f681ca26ce79339d892f5e30729a060d0",
    "verification/wave204-global-compatibility-verifier/audit.md":
        "eadad44ea0e7ac653defb7e5431c13b2ef06ae53eced0bbf6412f82fc3244c65",
}

Matrix = list[list[int]]
Vector = list[int]


def mod(value: int) -> int:
    return value % FIELD


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def identity(size: int) -> Matrix:
    return [[int(i == j) for j in range(size)] for i in range(size)]


def diagonal(values: Iterable[int]) -> Matrix:
    entries = [mod(value) for value in values]
    return [
        [entries[i] if i == j else 0 for j in range(len(entries))]
        for i in range(len(entries))
    ]


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [mod(left[i][j] + right[i][j]) for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def scalar_matrix(scalar: int, matrix: Matrix) -> Matrix:
    return [[mod(scalar * value) for value in row] for row in matrix]


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix shape mismatch")
    return [
        [
            mod(sum(left[i][k] * right[k][j] for k in range(len(right))))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matrix_vector(matrix: Matrix, vector: Vector) -> Vector:
    return [
        mod(sum(matrix[i][j] * vector[j] for j in range(len(vector))))
        for i in range(len(matrix))
    ]


def vector_dot(left: Vector, form: Matrix, right: Vector) -> int:
    return mod(
        sum(
            left[i] * form[i][j] * right[j]
            for i in range(len(left))
            for j in range(len(right))
        )
    )


def trace(matrix: Matrix) -> int:
    return mod(sum(matrix[i][i] for i in range(len(matrix))))


def rref(matrix: Matrix) -> tuple[Matrix, list[int]]:
    if not matrix:
        return [], []
    rows = [[mod(value) for value in row] for row in matrix]
    width = len(rows[0])
    pivots: list[int] = []
    pivot_row = 0
    for column in range(width):
        source = next(
            (
                row
                for row in range(pivot_row, len(rows))
                if rows[row][column]
            ),
            None,
        )
        if source is None:
            continue
        rows[pivot_row], rows[source] = rows[source], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], -1, FIELD)
        rows[pivot_row] = [mod(inverse * value) for value in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            multiplier = rows[row][column]
            rows[row] = [
                mod(rows[row][j] - multiplier * rows[pivot_row][j])
                for j in range(width)
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return rows, pivots


def rank(matrix: Matrix) -> int:
    return len(rref(matrix)[1])


def inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("inverse requires a square matrix")
    augmented = [
        [mod(value) for value in matrix[i]] + identity(size)[i]
        for i in range(size)
    ]
    reduced, pivots = rref(augmented)
    if pivots[:size] != list(range(size)):
        raise ValueError("singular matrix")
    return [row[size:] for row in reduced]


def determinant(matrix: Matrix) -> int:
    size = len(matrix)
    rows = [[mod(value) for value in row] for row in matrix]
    result = 1
    for column in range(size):
        source = next(
            (row for row in range(column, size) if rows[row][column]),
            None,
        )
        if source is None:
            return 0
        if source != column:
            rows[column], rows[source] = rows[source], rows[column]
            result = mod(-result)
        pivot = rows[column][column]
        result = mod(result * pivot)
        inverse_pivot = pow(pivot, -1, FIELD)
        for row in range(column + 1, size):
            multiplier = mod(rows[row][column] * inverse_pivot)
            rows[row] = [
                mod(rows[row][j] - multiplier * rows[column][j])
                for j in range(size)
            ]
    return result


def nullspace(matrix: Matrix) -> list[Vector]:
    reduced, pivots = rref(matrix)
    width = len(matrix[0])
    free = [column for column in range(width) if column not in pivots]
    basis: list[Vector] = []
    for free_column in free:
        vector = [0] * width
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = mod(-reduced[row][free_column])
        basis.append(vector)
    return basis


def minimum_linear_code_weight(basis: list[Vector]) -> int:
    return min(
        sum(value != 0 for value in vector)
        for coefficients in itertools.product(range(FIELD), repeat=len(basis))
        if any(coefficients)
        for vector in [
            [
                mod(
                    sum(
                        coefficients[i] * basis[i][j]
                        for i in range(len(basis))
                    )
                )
                for j in range(len(basis[0]))
            ]
        ]
    )


def independent_basis(vectors: list[Vector], dimension: int) -> list[Vector]:
    selected: list[Vector] = []
    for vector in vectors:
        if rank(selected + [vector]) > len(selected):
            selected.append(vector)
        if len(selected) == dimension:
            break
    if len(selected) != dimension:
        raise AssertionError("independent-basis extraction failed")
    return selected


def congruence_diagonalize(form: Matrix) -> tuple[Matrix, list[int]]:
    """Return T and diag with T^T form T=diag(diag), deterministically."""

    size = len(form)
    remaining = identity(size)
    orthogonal: list[Vector] = []
    while remaining:
        chosen = next(
            (
                vector
                for vector in remaining
                if vector_dot(vector, form, vector)
            ),
            None,
        )
        if chosen is None:
            pair = next(
                (
                    (left, right)
                    for left_index, left in enumerate(remaining)
                    for right in remaining[left_index + 1 :]
                    if vector_dot(left, form, right)
                ),
                None,
            )
            if pair is None:
                raise AssertionError("nondegenerate subspace became radical")
            chosen = [
                mod(pair[0][i] + pair[1][i]) for i in range(size)
            ]
        norm = vector_dot(chosen, form, chosen)
        inverse_norm = pow(norm, -1, FIELD)
        projected: list[Vector] = []
        for vector in remaining:
            coefficient = mod(
                vector_dot(chosen, form, vector) * inverse_norm
            )
            candidate = [
                mod(vector[i] - coefficient * chosen[i])
                for i in range(size)
            ]
            if any(candidate):
                projected.append(candidate)
        orthogonal.append(chosen)
        remaining = independent_basis(projected, len(remaining) - 1)
    transform = transpose(orthogonal)
    transformed = matrix_multiply(
        matrix_multiply(transpose(transform), form), transform
    )
    diagonal_entries = [transformed[i][i] for i in range(size)]
    if transformed != diagonal(diagonal_entries):
        raise AssertionError("congruence diagonalization failed")
    return transform, diagonal_entries


AMBIENT_FORM = diagonal([1] * 10 + [2])


def ambient_orthogonal_basis(norms: list[int]) -> Matrix:
    """Embed a determinant-two form of dimension at most 11 in diag(1^10,2)."""

    two_positions = [i for i, value in enumerate(norms) if value == 2]
    one_positions = [i for i, value in enumerate(norms) if value == 1]
    if len(two_positions) % 2 != 1:
        raise AssertionError("expected determinant-two diagonal form")
    columns: list[Vector | None] = [None] * len(norms)
    next_axis = 0
    for left_position, right_position in zip(
        two_positions[:-1:2], two_positions[1:-1:2]
    ):
        left = [0] * 11
        right = [0] * 11
        left[next_axis] = 1
        left[next_axis + 1] = 1
        right[next_axis] = 1
        right[next_axis + 1] = 2
        columns[left_position] = left
        columns[right_position] = right
        next_axis += 2
    final_two = [0] * 11
    final_two[10] = 1
    columns[two_positions[-1]] = final_two
    for position in one_positions:
        vector = [0] * 11
        vector[next_axis] = 1
        columns[position] = vector
        next_axis += 1
    if next_axis != len(norms) - 1 or any(column is None for column in columns):
        raise AssertionError("ambient coordinate allocation changed")
    result = transpose([column for column in columns if column is not None])
    if matrix_multiply(
        matrix_multiply(transpose(result), AMBIENT_FORM), result
    ) != diagonal(norms):
        raise AssertionError("ambient orthogonal basis has wrong Gram")
    return result


def coordinate_realization(full_gram: Matrix) -> tuple[Matrix, dict[str, Any]]:
    full_rank = rank(full_gram)
    if full_rank not in (10, 11):
        raise AssertionError("sealed controls require nondegenerate rank 10 or 11")
    basis_indices = rref(full_gram)[1]
    if len(basis_indices) != full_rank:
        raise AssertionError("quotient basis extraction failed")
    basis_gram = [
        [full_gram[i][j] for j in basis_indices]
        for i in basis_indices
    ]
    basis_determinant = determinant(basis_gram)
    if basis_determinant != 2:
        raise AssertionError("fixed quotient discriminant changed")
    transform, norms = congruence_diagonalize(basis_gram)
    diagonal_coordinates = ambient_orthogonal_basis(norms)
    basis_coordinates = matrix_multiply(
        diagonal_coordinates, inverse(transform)
    )
    basis_cross_all = [
        [full_gram[i][j] for j in range(14)] for i in basis_indices
    ]
    coordinates = matrix_multiply(
        matrix_multiply(basis_coordinates, inverse(basis_gram)),
        basis_cross_all,
    )
    reconstructed = matrix_multiply(
        matrix_multiply(transpose(coordinates), AMBIENT_FORM), coordinates
    )
    if reconstructed != full_gram:
        raise AssertionError("coordinate realization does not reproduce Gram")
    return coordinates, {
        "principal_basis_indices_zero_based": basis_indices,
        "principal_determinant": basis_determinant,
        "congruence_diagonal_norms": norms,
        "ambient_form_diagonal": [1] * 10 + [2],
        "coordinate_matrix_11_by_14": coordinates,
    }


def rank_one_operator(vector: Vector) -> Matrix:
    column = [[value] for value in vector]
    return matrix_multiply(
        matrix_multiply(column, transpose(column)), AMBIENT_FORM
    )


def star_projector(columns: Matrix) -> Matrix:
    result = [[0] * 11 for _ in range(11)]
    for vector in transpose(columns):
        result = matrix_add(result, scalar_matrix(2, rank_one_operator(vector)))
    return result


def normalized_projective(vector: Vector) -> tuple[int, ...]:
    first = next((value for value in vector if value), None)
    if first is None:
        raise AssertionError("zero projective vector")
    inverse_first = pow(first, -1, FIELD)
    return tuple(mod(inverse_first * value) for value in vector)


def fixed_inputs() -> dict[str, str]:
    observed = {
        relative: sha256(ROOT / relative) for relative in EXPECTED_INPUTS
    }
    if observed != EXPECTED_INPUTS:
        raise AssertionError(
            {"expected_inputs": EXPECTED_INPUTS, "observed_inputs": observed}
        )
    return observed


def parse_controls() -> dict[str, Any]:
    return json.loads((HERE / "controls.json").read_text(encoding="utf-8"))


def edge(left: str, right: str) -> tuple[str, str]:
    if left == right:
        raise AssertionError("loop requested")
    return tuple(sorted((left, right)))


def build_local_edges(
    convention: dict[str, Any], exclusive_cross_edges: list[list[str]]
) -> set[tuple[str, str]]:
    x_blocks = convention["x_blocks_without_center"]
    y_blocks = convention["y_blocks_without_center"]
    edges: set[tuple[str, str]] = set()
    for block in x_blocks:
        edges.add(edge("x", block[0]))
        edges.add(edge("x", block[1]))
        edges.add(edge(block[0], block[1]))
    for block in y_blocks:
        edges.add(edge("y", block[0]))
        edges.add(edge("y", block[1]))
        edges.add(edge(block[0], block[1]))
    for left, right in exclusive_cross_edges:
        edges.add(edge(left, right))
    return edges


def common_neighbors(
    vertices: list[str], edges: set[tuple[str, str]], left: str, right: str
) -> set[str]:
    return {
        vertex
        for vertex in vertices
        if vertex not in (left, right)
        and edge(left, vertex) in edges
        and edge(right, vertex) in edges
    }


def triangle_cross_entry(
    left: list[str], right: list[str], edges: set[tuple[str, str]]
) -> tuple[int, int]:
    integer_count = sum(
        edge(left_vertex, right_vertex) in edges
        for left_vertex in left
        for right_vertex in right
        if left_vertex != right_vertex
    )
    return integer_count, mod(integer_count)


def profile(row: list[int]) -> dict[str, int]:
    return {str(value): row.count(value) for value in range(FIELD)}


def profile_multiset(matrix: Matrix) -> list[dict[str, Any]]:
    counts = Counter(tuple(row.count(value) for value in range(FIELD)) for row in matrix)
    return [
        {
            "counts_0_1_2": list(key),
            "multiplicity": counts[key],
        }
        for key in sorted(counts)
    ]


def full_two_star_gram(cross: Matrix) -> Matrix:
    star = [
        [0 if row == column else 1 for column in range(7)]
        for row in range(7)
    ]
    return (
        [star[row] + cross[row] for row in range(7)]
        + [
            [cross[row][column] for row in range(7)] + star[column]
            for column in range(7)
        ]
    )


def normalized_boundary(
    top_distinct: int, left_distinct: int
) -> tuple[Matrix, Matrix, list[int], list[int]]:
    """Normalize the two special-row and two special-column placements.

    Independent permutations of the five ordinary rows and columns put the
    extra 2 in the first special row/column at ordinary position zero.  The
    second extra 2 is then either aligned at zero or distinct at one.  The
    four Boolean cases are therefore exhaustive up to permitted relabeling.
    """

    top_extra = [0, 1 if top_distinct else 0]
    left_extra = [0, 1 if left_distinct else 0]
    top = [
        [1, 2]
        + [2 if column == top_extra[0] else 1 for column in range(5)],
        [2, 1]
        + [2 if column == top_extra[1] else 1 for column in range(5)],
    ]
    first_two = [
        [
            2 if row == left_extra[0] else 1,
            2 if row == left_extra[1] else 1,
        ]
        for row in range(5)
    ]
    core_row_sums = [6 - sum(row) for row in first_two]
    core_column_sums = [
        6 - top[0][column + 2] - top[1][column + 2]
        for column in range(5)
    ]
    return top, first_two, core_row_sums, core_column_sums


def binary_matrices_with_margins(
    row_sums: list[int], column_sums: list[int]
) -> Iterable[Matrix]:
    row_patterns = [
        [
            list(pattern)
            for pattern in itertools.product((0, 1), repeat=5)
            if sum(pattern) == row_sum
        ]
        for row_sum in row_sums
    ]

    def recurse(
        rows: Matrix, row_index: int, remaining_columns: list[int]
    ) -> Iterable[Matrix]:
        if row_index == 5:
            if remaining_columns == [0] * 5:
                yield rows
            return
        rows_after = 4 - row_index
        for row in row_patterns[row_index]:
            remaining = [
                remaining_columns[column] - row[column]
                for column in range(5)
            ]
            if min(remaining) < 0:
                continue
            if any(value > rows_after for value in remaining):
                continue
            yield from recurse(rows + [row], row_index + 1, remaining)

    yield from recurse([], 0, list(column_sums))


def low_t_core_matrices(
    row_sums: list[int], column_sums: list[int], core_twos: int
) -> Iterable[Matrix]:
    if core_twos == 0:
        yield from binary_matrices_with_margins(row_sums, column_sums)
        return
    if core_twos != 1:
        raise ValueError("the sealed census covers only t=6 and t=7")
    for double_row in range(5):
        for double_column in range(5):
            residual_rows = list(row_sums)
            residual_columns = list(column_sums)
            residual_rows[double_row] -= 2
            residual_columns[double_column] -= 2
            if min(residual_rows) < 0 or min(residual_columns) < 0:
                continue
            for binary in binary_matrices_with_margins(
                residual_rows, residual_columns
            ):
                if binary[double_row][double_column]:
                    continue
                core = [row[:] for row in binary]
                core[double_row][double_column] = 2
                yield core


def normalized_low_t_matrices(t_value: int) -> Iterable[Matrix]:
    """Enumerate all normalized profile matrices with t=6 or t=7.

    The six forced 2-entries consist of the two off-diagonal distinguished
    entries, the two remaining special-row 2s, and the two remaining
    special-column 2s.  Thus the ordinary 5 by 5 core has exactly `t-6`
    entries equal to 2.
    """

    if t_value not in (6, 7):
        raise ValueError("only the exact low-count frontier is enumerated")
    for top_distinct in (0, 1):
        for left_distinct in (0, 1):
            top, first_two, row_sums, column_sums = normalized_boundary(
                top_distinct, left_distinct
            )
            for core in low_t_core_matrices(
                row_sums, column_sums, t_value - 6
            ):
                yield top + [
                    first_two[row] + core[row] for row in range(5)
                ]


def exact_low_t_census() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for t_value in (6, 7):
        histogram: Counter[tuple[int, int, int, int]] = Counter()
        admissible_by_h: Counter[int] = Counter()
        total = 0
        for cross in normalized_low_t_matrices(t_value):
            if sum(value == 2 for row in cross for value in row) != t_value:
                raise AssertionError("low-t enumerator count drift")
            full_gram = full_two_star_gram(cross)
            reduced, pivots = rref(full_gram)
            del reduced
            gram_rank = len(pivots)
            gram_kernel = nullspace(full_gram)
            kernel_distance = minimum_linear_code_weight(gram_kernel)
            discriminant = 0
            if gram_rank <= 11:
                principal = [
                    [full_gram[i][j] for j in pivots] for i in pivots
                ]
                discriminant = determinant(principal)
                if not discriminant:
                    raise AssertionError(
                        "symmetric rank basis gave a singular principal minor"
                    )
            compression = matrix_multiply(cross, transpose(cross))
            fourth_trace = trace(matrix_multiply(compression, compression))
            histogram[
                (gram_rank, discriminant, kernel_distance, fourth_trace)
            ] += 1
            if (
                gram_rank == 11
                and discriminant == 2
                and kernel_distance >= 4
            ):
                # At full ambient rank the Gram kernel is the true relation
                # code.  This implication is intentionally not used below
                # rank 11, where a radical lift may shrink that true kernel.
                admissible_by_h[fourth_trace] += 1
            total += 1
        result[str(t_value)] = {
            "normalized_matrix_count": total,
            "normalization_cases": 4,
            "histogram": [
                {
                    "gram_rank": key[0],
                    "quotient_discriminant_or_zero_if_rank_over_11": key[1],
                    "gram_kernel_minimum_weight": key[2],
                    "fourth_trace": key[3],
                    "count": histogram[key],
                }
                for key in sorted(histogram)
            ],
            "rank11_nonsquare_true_distance_at_least_4_by_h": {
                str(value): admissible_by_h[value] for value in range(3)
            },
        }
    if result["6"]["normalized_matrix_count"] != 646:
        raise AssertionError("t=6 normalized census count changed")
    if result["7"]["normalized_matrix_count"] != 7886:
        raise AssertionError("t=7 normalized census count changed")
    if result["6"]["rank11_nonsquare_true_distance_at_least_4_by_h"] != {
        "0": 0,
        "1": 18,
        "2": 0,
    }:
        raise AssertionError("t=6 admissible census changed")
    if result["7"]["rank11_nonsquare_true_distance_at_least_4_by_h"] != {
        "0": 297,
        "1": 324,
        "2": 144,
    }:
        raise AssertionError("t=7 admissible census changed")
    return result


def analyze_control(
    convention: dict[str, Any], certificate: dict[str, Any]
) -> dict[str, Any]:
    x_blocks_without = convention["x_blocks_without_center"]
    y_blocks_without = convention["y_blocks_without_center"]
    x_blocks = [["x", *block] for block in x_blocks_without]
    y_blocks = [["y", *block] for block in y_blocks_without]
    vertices = sorted(
        {
            vertex
            for block in x_blocks + y_blocks
            for vertex in block
        }
    )
    if len(vertices) != 28:
        raise AssertionError("two-center union does not have 28 vertices")
    edges = build_local_edges(
        convention, certificate["exclusive_cross_edges"]
    )
    neighborhoods = {
        center: {
            vertex
            for vertex in vertices
            if vertex != center and edge(center, vertex) in edges
        }
        for center in ("x", "y")
    }
    if len(neighborhoods["x"]) != 14 or len(neighborhoods["y"]) != 14:
        raise AssertionError("center degree changed")
    if neighborhoods["x"] & neighborhoods["y"] != {"a", "b"}:
        raise AssertionError("common-neighbor pair changed")
    if edge("a", "b") in edges:
        raise AssertionError("the two common neighbors became adjacent")

    expected_cross = [
        [int(value) for value in row]
        for row in certificate["cross_gram_rows"]
    ]
    observed_cross: Matrix = []
    integer_cross_counts: Matrix = []
    for left_index, left_block in enumerate(x_blocks):
        observed_row: list[int] = []
        integer_row: list[int] = []
        for right_index, right_block in enumerate(y_blocks):
            integer_count, residue = triangle_cross_entry(
                left_block, right_block, edges
            )
            integer_row.append(integer_count)
            observed_row.append(residue)
            if set(left_block).isdisjoint(right_block) and integer_count > 2:
                raise AssertionError(
                    f"endpoint cross-edge cap failed at {left_index},{right_index}"
                )
        integer_cross_counts.append(integer_row)
        observed_cross.append(observed_row)
    if observed_cross != expected_cross:
        raise AssertionError(
            {
                "control": certificate["name"],
                "expected_cross": expected_cross,
                "observed_cross": observed_cross,
            }
        )

    adjacent_common_histogram: Counter[int] = Counter()
    nonedge_common_histogram: Counter[int] = Counter()
    for left_index, left in enumerate(vertices):
        for right in vertices[left_index + 1 :]:
            count = len(common_neighbors(vertices, edges, left, right))
            if edge(left, right) in edges:
                if count > 1:
                    raise AssertionError(
                        f"lambda upper bound failed at {left},{right}"
                    )
                adjacent_common_histogram[count] += 1
            else:
                if count > 2:
                    raise AssertionError(
                        f"mu upper bound failed at {left},{right}"
                    )
                nonedge_common_histogram[count] += 1

    for exclusive in sorted(neighborhoods["x"] - {"a", "b"}):
        if len(common_neighbors(vertices, edges, exclusive, "y")) != 2:
            raise AssertionError("exclusive x-neighbor lost mu=2 at y")
    for exclusive in sorted(neighborhoods["y"] - {"a", "b"}):
        if len(common_neighbors(vertices, edges, exclusive, "x")) != 2:
            raise AssertionError("exclusive y-neighbor lost mu=2 at x")

    if observed_cross[:2][:] and [
        row[:2] for row in observed_cross[:2]
    ] != [[1, 2], [2, 1]]:
        raise AssertionError("distinguished 2-by-2 corner changed")
    for row in observed_cross[:2]:
        if profile(row) != {"0": 0, "1": 5, "2": 2}:
            raise AssertionError("special row profile changed")
    for row in transpose(observed_cross)[:2]:
        if profile(row) != {"0": 0, "1": 5, "2": 2}:
            raise AssertionError("special column profile changed")
    ordinary_k_rows: list[int] = []
    ordinary_k_columns: list[int] = []
    for row in observed_cross[2:]:
        if sum(row) != 6:
            raise AssertionError("ordinary row integer sum changed")
        k = row.count(2)
        if profile(row) != {
            "0": 1 + k,
            "1": 6 - 2 * k,
            "2": k,
        }:
            raise AssertionError("ordinary row profile formula failed")
        ordinary_k_rows.append(k)
    for row in transpose(observed_cross)[2:]:
        if sum(row) != 6:
            raise AssertionError("ordinary column integer sum changed")
        k = row.count(2)
        if profile(row) != {
            "0": 1 + k,
            "1": 6 - 2 * k,
            "2": k,
        }:
            raise AssertionError("ordinary column profile formula failed")
        ordinary_k_columns.append(k)
    if matrix_vector(observed_cross, [1] * 7) != [0] * 7:
        raise AssertionError("cross Gram row sums are not zero")
    if matrix_vector(transpose(observed_cross), [1] * 7) != [0] * 7:
        raise AssertionError("cross Gram column sums are not zero")

    compression = matrix_multiply(observed_cross, transpose(observed_cross))
    pair_trace = trace(compression)
    fourth_trace = trace(matrix_multiply(compression, compression))
    t_value = sum(
        value == 2 for row in observed_cross for value in row
    )
    if t_value != certificate["claimed_t"]:
        raise AssertionError("claimed number of D=2 entries changed")
    if fourth_trace != certificate["claimed_h"]:
        raise AssertionError("claimed fourth trace changed")

    full_gram = full_two_star_gram(observed_cross)
    all_blocks = x_blocks + y_blocks
    local_full_gram = [
        [
            triangle_cross_entry(left_block, right_block, edges)[1]
            for right_block in all_blocks
        ]
        for left_block in all_blocks
    ]
    if local_full_gram != full_gram:
        raise AssertionError("local B^T A B does not reproduce the full Gram")
    full_rank = rank(full_gram)
    kernel = nullspace(full_gram)
    kernel_minimum_weight = minimum_linear_code_weight(kernel)
    if full_rank != 11 or len(kernel) != 3 or kernel_minimum_weight < 4:
        raise AssertionError("two-star Gram code invariants changed")
    # A nullspace basis need not contain either star word literally.
    if matrix_vector(full_gram, [1] * 7 + [0] * 7) != [0] * 14:
        raise AssertionError("first star circuit absent")
    if matrix_vector(full_gram, [0] * 7 + [1] * 7) != [0] * 14:
        raise AssertionError("second star circuit absent")

    coordinates, embedding = coordinate_realization(full_gram)
    projective_directions = {
        normalized_projective(vector) for vector in transpose(coordinates)
    }
    if len(projective_directions) != 14:
        raise AssertionError("local projective distinctness failed")
    x_columns = [row[:7] for row in coordinates]
    y_columns = [row[7:] for row in coordinates]
    p_x = star_projector(x_columns)
    p_y = star_projector(y_columns)
    for projector in (p_x, p_y):
        if matrix_multiply(projector, projector) != projector:
            raise AssertionError("star projector is not idempotent")
        if rank(projector) != 6 or trace(projector) != 0:
            raise AssertionError("star projector rank or trace changed")
        if matrix_multiply(transpose(projector), AMBIENT_FORM) != matrix_multiply(
            AMBIENT_FORM, projector
        ):
            raise AssertionError("star projector is not self-adjoint")
    product = matrix_multiply(p_x, p_y)
    coordinate_pair_trace = trace(product)
    coordinate_fourth_trace = trace(matrix_multiply(product, product))
    if (coordinate_pair_trace, coordinate_fourth_trace) != (
        pair_trace,
        fourth_trace,
    ):
        raise AssertionError("coordinate and cross-Gram traces disagree")

    return {
        "name": certificate["name"],
        "claimed_and_recomputed_t": t_value,
        "claimed_and_recomputed_h": fourth_trace,
        "pair_trace": pair_trace,
        "cross_gram": observed_cross,
        "integer_triangle_cross_counts": integer_cross_counts,
        "special_corner": [row[:2] for row in observed_cross[:2]],
        "row_profile_multiset": profile_multiset(observed_cross),
        "column_profile_multiset": profile_multiset(transpose(observed_cross)),
        "ordinary_row_k_values": ordinary_k_rows,
        "ordinary_column_k_values": ordinary_k_columns,
        "local_graph": {
            "vertex_count": len(vertices),
            "edge_count": len(edges),
            "center_degrees": {
                center: len(neighborhoods[center]) for center in ("x", "y")
            },
            "center_common_neighbors": sorted(
                neighborhoods["x"] & neighborhoods["y"]
            ),
            "exclusive_cross_edge_count": len(
                certificate["exclusive_cross_edges"]
            ),
            "adjacent_pair_local_common_neighbor_histogram": {
                str(key): adjacent_common_histogram[key]
                for key in sorted(adjacent_common_histogram)
            },
            "nonedge_pair_local_common_neighbor_histogram": {
                str(key): nonedge_common_histogram[key]
                for key in sorted(nonedge_common_histogram)
            },
            "all_edges_have_at_most_one_local_common_neighbor": True,
            "all_nonedges_have_at_most_two_local_common_neighbors": True,
            "opposite_center_mu_two_for_all_exclusive_neighbors": True,
            "endpoint_cross_edge_cap_on_selected_disjoint_blocks": True,
            "full_local_B_transpose_A_B_reproduces_two_star_gram": True,
        },
        "two_star_gram": {
            "rank": full_rank,
            "kernel_nullity": len(kernel),
            "kernel_minimum_nonzero_weight": kernel_minimum_weight,
            "kernel_is_true_relation_code_because_rank_is_11": True,
            "local_projective_direction_count": len(projective_directions),
            "star_circuit_words_present": True,
            "embedding": embedding,
        },
        "projectors": {
            "ambient_dimension": 11,
            "each_rank": 6,
            "each_trace": 0,
            "each_idempotent": True,
            "each_self_adjoint": True,
            "intersection_dimension": 12 - full_rank,
            "pair_trace": coordinate_pair_trace,
            "fourth_trace": coordinate_fourth_trace,
        },
    }


def analyze() -> dict[str, Any]:
    inputs = fixed_inputs()
    controls = parse_controls()
    convention = controls["vertex_convention"]
    analyzed = [
        analyze_control(convention, certificate)
        for certificate in controls["controls"]
    ]
    by_name = {control["name"]: control for control in analyzed}
    if {
        by_name[name]["claimed_and_recomputed_h"]
        for name in ("t7_h0", "t7_h1", "t7_h2")
    } != {0, 1, 2}:
        raise AssertionError("t=7 controls no longer realize every field value")
    for name in ("t7_h0", "t7_h1", "t7_h2"):
        if by_name[name]["claimed_and_recomputed_t"] != 7:
            raise AssertionError("average-seven control count changed")
        if by_name[name]["pair_trace"] != 2:
            raise AssertionError("average-seven pair trace changed")
        if by_name[name]["projectors"]["intersection_dimension"] != 1:
            raise AssertionError("average-seven intersection changed")
    if by_name["t6_h1"]["two_star_gram"][
        "kernel_minimum_nonzero_weight"
    ] != 6:
        raise AssertionError("t=6 projective control distance changed")
    census = exact_low_t_census()
    return {
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "scope": (
            "conditional n3=4158 rank-11 endpoint; exact necessary two-center "
            "nonedge geometry and target-shaped 28-vertex local controls"
        ),
        "field": FIELD,
        "inputs": inputs,
        "derived_nonedge_geometry": {
            "two_common_neighbors_are_nonadjacent": True,
            "distinguished_cross_gram_corner": [[1, 2], [2, 1]],
            "each_special_row_and_column_profile": {
                "zeros": 0,
                "ones": 5,
                "twos": 2,
            },
            "ordinary_row_and_column_rule": (
                "integer sum 6; for k entries equal to 2 the profile is "
                "0^(1+k) 1^(6-2k) 2^k, with 0<=k<=3"
            ),
            "fourth_trace_formula": "h=tr((C C^T)^2) over F_3",
            "two_entry_count": (
                "t_xy=#(entries C_ij=2)=BLB^T_xy as an integer; "
                "pair trace=2*t_xy in F_3"
            ),
            "derivation_uses": [
                "lambda=1",
                "mu=2",
                "seven edge-triangles at each center",
                "P=0 prohibition on three cross edges between disjoint triangles",
                "D=B^T A B over F_3",
            ],
        },
        "complete_normalized_low_t_census": census,
        "controls": analyzed,
        "strong_separation": {
            "control_names": ["t7_h0", "t7_h1", "t7_h2"],
            "same_two_entry_count": 7,
            "same_pair_trace": 2,
            "same_intersection_dimension": 1,
            "same_full_gram_rank": 11,
            "same_quotient_discriminant": 2,
            "true_relation_minimum_weight_at_least": 4,
            "different_fourth_traces": [0, 1, 2],
        },
        "conclusions": {
            "t_at_least_7_from_local_projectivity": False,
            "exact_t7_determines_h": False,
            "every_F3_fourth_trace_value_has_a_rank11_t7_local_control": True,
            "two_center_profile_data_determines_h": False,
            "pair_trace_plus_intersection_plus_t_determines_h": False,
            "actual_endpoint_nonedge_h_classified": False,
            "rank_11_endpoint_excluded": False,
            "conway_99_status": "UNKNOWN",
            "newly_named_missing_invariant": (
                "the simultaneous 99-center extension law coupling the "
                "unsaturated pairs of overlapping 28-vertex two-center balls; "
                "neither local SRG completion bounds nor the scalar t_xy supplies it"
            ),
        },
        "omitted_target_premises": [
            "completion from 28 to 99 vertices",
            "degree 14 away from the two frozen centers",
            "exact lambda=1 and mu=2 completions for every currently unsaturated local pair",
            "simultaneous compatibility of overlapping two-center balls",
            "all 231 triangle blocks and all 99 point-stars",
            "global projective distinctness and dual distance for 231 columns",
            "global centered-Gram rank 11 and square-zero identity",
            "global sum of 99 star projectors equal to zero",
            "the full endpoint block-relation profiles for every triangle pair",
            "an srg(99,14,1,2), endpoint code, construction, or nonexistence proof",
        ],
    }


def verify(data: dict[str, Any]) -> None:
    if data["conclusions"]["actual_endpoint_nonedge_h_classified"]:
        raise AssertionError("status inflation: actual nonedges are not classified")
    if data["conclusions"]["rank_11_endpoint_excluded"]:
        raise AssertionError("status inflation: endpoint not excluded")
    if data["conclusions"]["conway_99_status"] != "UNKNOWN":
        raise AssertionError("status inflation: Conway-99 must remain UNKNOWN")
    if [
        (
            control["claimed_and_recomputed_t"],
            control["claimed_and_recomputed_h"],
        )
        for control in data["controls"]
    ] != [(6, 1), (7, 0), (7, 1), (7, 2)]:
        raise AssertionError("control order or trace values changed")
    if data["strong_separation"]["different_fourth_traces"] != [0, 1, 2]:
        raise AssertionError("strong separation changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    data = analyze()
    verify(data)
    if args.verify:
        observed = json.loads(args.verify.read_text(encoding="utf-8"))
        if observed != data:
            raise AssertionError("frozen result differs")
    if args.write:
        args.write.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if not args.write and not args.verify:
        print(json.dumps(data, indent=2, sort_keys=True))
    print("PASS: Wave205 proof-A nonedge fourth-trace checks")


if __name__ == "__main__":
    main()
