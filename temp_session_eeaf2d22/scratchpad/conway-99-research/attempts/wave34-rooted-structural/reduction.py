"""Exact structural reduction for the Wave 34 rooted six-block criterion.

This module is standard-library only.  Its canonical signed-Fano coordinates
are used only to check permutation-invariant fixed-side facts.  No quotient by
an automorphism is taken: the theorem in the accompanying report applies to
the frozen labeled matrices after the same formulas are evaluated in their
given order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from typing import Iterable, Sequence


Q = Fraction
Matrix = list[list[Fraction]]


def zeros(rows: int, cols: int) -> Matrix:
    return [[Q(0) for _ in range(cols)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    out = zeros(size, size)
    for i in range(size):
        out[i][i] = Q(1)
    return out


def transpose(a: Sequence[Sequence[Fraction]]) -> Matrix:
    return [list(row) for row in zip(*a)]


def multiply(
    a: Sequence[Sequence[Fraction]], b: Sequence[Sequence[Fraction]]
) -> Matrix:
    bt = transpose(b)
    return [
        [sum((x * y for x, y in zip(row, col)), Q(0)) for col in bt]
        for row in a
    ]


def add(
    a: Sequence[Sequence[Fraction]],
    b: Sequence[Sequence[Fraction]],
    scale_a: Fraction = Q(1),
    scale_b: Fraction = Q(1),
) -> Matrix:
    return [
        [scale_a * a[i][j] + scale_b * b[i][j] for j in range(len(a[0]))]
        for i in range(len(a))
    ]


def matrix_trace(a: Sequence[Sequence[Fraction]]) -> Fraction:
    return sum((a[i][i] for i in range(len(a))), Q(0))


def inverse(a: Sequence[Sequence[Fraction]]) -> Matrix:
    size = len(a)
    work = [
        [Q(x) for x in row] + [Q(i == j) for j in range(size)]
        for i, row in enumerate(a)
    ]
    for col in range(size):
        pivot = next(
            (row for row in range(col, size) if work[row][col] != 0), None
        )
        if pivot is None:
            raise ValueError("matrix is singular")
        work[col], work[pivot] = work[pivot], work[col]
        pivot_value = work[col][col]
        work[col] = [x / pivot_value for x in work[col]]
        for row in range(size):
            if row == col or work[row][col] == 0:
                continue
            factor = work[row][col]
            work[row] = [
                work[row][j] - factor * work[col][j] for j in range(2 * size)
            ]
    return [row[size:] for row in work]


def determinant(a: Sequence[Sequence[Fraction]]) -> Fraction:
    size = len(a)
    work = [[Q(x) for x in row] for row in a]
    answer = Q(1)
    sign = 1
    for col in range(size):
        pivot = next(
            (row for row in range(col, size) if work[row][col] != 0), None
        )
        if pivot is None:
            return Q(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            sign *= -1
        pivot_value = work[col][col]
        answer *= pivot_value
        for row in range(col + 1, size):
            if work[row][col] == 0:
                continue
            factor = work[row][col] / pivot_value
            for j in range(col, size):
                work[row][j] -= factor * work[col][j]
    return answer * sign


def rank(a: Sequence[Sequence[Fraction]]) -> int:
    if not a:
        return 0
    work = [[Q(x) for x in row] for row in a]
    rows = len(work)
    cols = len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][col] != 0),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][col]
        work[pivot_row] = [x / pivot_value for x in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][col] == 0:
                continue
            factor = work[row][col]
            work[row] = [
                work[row][j] - factor * work[pivot_row][j] for j in range(cols)
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def rank_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[int(x) % prime for x in row] for row in matrix]
    rows = len(work)
    cols = len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][col]), None
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inv = pow(work[pivot_row][col], -1, prime)
        work[pivot_row] = [(x * inv) % prime for x in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][col] == 0:
                continue
            factor = work[row][col]
            work[row] = [
                (work[row][j] - factor * work[pivot_row][j]) % prime
                for j in range(cols)
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def integer_matrix(a: Sequence[Sequence[Fraction]]) -> list[list[int]]:
    out: list[list[int]] = []
    for row in a:
        converted: list[int] = []
        for value in row:
            if value.denominator != 1:
                raise ValueError(f"nonintegral entry {value}")
            converted.append(value.numerator)
        out.append(converted)
    return out


def canonical_json_sha256(value: object) -> str:
    raw = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def matrix_payload(a: Sequence[Sequence[Fraction]]) -> list[list[object]]:
    out: list[list[object]] = []
    for row in a:
        encoded: list[object] = []
        for value in row:
            if value.denominator == 1:
                encoded.append(value.numerator)
            else:
                encoded.append([value.numerator, value.denominator])
        out.append(encoded)
    return out


def fano_lines() -> list[set[int]]:
    """Cyclic labeling of the seven Fano lines."""

    return [{i, (i + 1) % 7, (i + 3) % 7} for i in range(7)]


def build_fixed_data() -> tuple[Matrix, Matrix, list[dict[str, object]]]:
    """Return support adjacency A, support-to-O incidence P, and O labels.

    Support vertices 0..6 are Fano points and 7..13 are Fano lines.
    A joins a point to the four lines not containing it.  An incidence
    point-line pair has two labeled O copies; a nonincidence pair has one.
    """

    lines = fano_lines()
    support = zeros(14, 14)
    for point in range(7):
        for line in range(7):
            if point not in lines[line]:
                support[point][7 + line] = Q(1)
                support[7 + line][point] = Q(1)

    labels: list[dict[str, object]] = []
    for point in range(7):
        for line in range(7):
            incident = point in lines[line]
            for copy in range(2 if incident else 1):
                labels.append(
                    {
                        "point": point,
                        "line": line,
                        "copy": copy,
                        "incident": incident,
                    }
                )
    if len(labels) != 70:
        raise AssertionError("expected 70 O labels")

    support_to_o = zeros(14, 70)
    for edge, label in enumerate(labels):
        point = int(label["point"])
        line = int(label["line"])
        support_to_o[point][edge] = Q(1)
        support_to_o[7 + line][edge] = Q(1)
    return support, support_to_o, labels


def fixed_operators() -> dict[str, object]:
    """Construct every fixed rational operator in the reduction."""

    support, support_to_o, labels = build_fixed_data()
    support_squared = multiply(support, support)
    gram = multiply(support_to_o, transpose(support_to_o))
    signed = [Q(1)] * 7 + [Q(-1)] * 7
    lifted = [
        [gram[i][j] + signed[i] * signed[j] for j in range(14)]
        for i in range(14)
    ]
    lifted_inverse = inverse(lifted)
    gram_plus = [
        [
            lifted_inverse[i][j] - signed[i] * signed[j] / Q(196)
            for j in range(14)
        ]
        for i in range(14)
    ]
    r_projector = multiply(
        multiply(transpose(support_to_o), gram_plus), support_to_o
    )
    support_times_p = multiply(support, support_to_o)
    c_so = [
        [
            Q(2) - support_to_o[i][edge] - support_times_p[i][edge]
            for edge in range(70)
        ]
        for i in range(14)
    ]
    h_r = multiply(multiply(transpose(c_so), gram_plus), support_to_o)

    fixed_c_rational = zeros(70, 70)
    for i in range(70):
        for j in range(70):
            fixed_c_rational[i][j] = (
                Q(21)
                * (h_r[i][j] + Q(3) * Q(i == j) - Q(3) * r_projector[i][j])
                + Q(21, 5)
            )
    fixed_c = integer_matrix(fixed_c_rational)

    return {
        "support": support,
        "support_to_o": support_to_o,
        "labels": labels,
        "support_squared": support_squared,
        "gram": gram,
        "gram_plus": gram_plus,
        "r_projector": r_projector,
        "c_so": c_so,
        "h_r": h_r,
        "fixed_c": fixed_c,
        "signed_kernel": signed,
    }


def spanning_tree_minor(
    support_to_o: Sequence[Sequence[Fraction]],
    labels: Sequence[dict[str, object]],
) -> dict[str, object]:
    """Produce a unit 13-minor witnessing SNF(P)=diag(1^13,0)."""

    pair_to_first_edge: dict[tuple[int, int], int] = {}
    for edge, label in enumerate(labels):
        pair = (int(label["point"]), int(label["line"]))
        pair_to_first_edge.setdefault(pair, edge)

    # Star from point 0 to all line vertices, then from line 0 to points 1..6.
    columns = [pair_to_first_edge[(0, line)] for line in range(7)]
    columns.extend(pair_to_first_edge[(point, 0)] for point in range(1, 7))
    signed_incidence = [
        [
            support_to_o[row][col] * (Q(1) if row < 7 else Q(-1))
            for col in columns
        ]
        for row in range(14)
    ]
    deleted_row = 13
    minor = [
        row[:] for row_index, row in enumerate(signed_incidence)
        if row_index != deleted_row
    ]
    det = determinant(minor)
    return {
        "columns": columns,
        "deleted_row": deleted_row,
        "determinant": det.numerator if det.denominator == 1 else str(det),
        "o_labels": [labels[col] for col in columns],
    }


def two_factor_dp() -> dict[str, int]:
    """Count every labeled binary column b with P b = 2*1 exactly.

    An underlying multiplicity-one use of an incidence edge has two choices
    between its two labeled O copies.  The weighted count therefore counts
    frozen labeled binary vectors, not unlabelled multigraphs.
    """

    lines = fano_lines()
    incident = [
        [point in lines[line] for line in range(7)] for point in range(7)
    ]
    options: list[list[tuple[tuple[int, ...], int]]] = []
    for point in range(7):
        row_options: list[tuple[tuple[int, ...], int]] = []
        for line in range(7):
            if incident[point][line]:
                row = [0] * 7
                row[line] = 2
                row_options.append((tuple(row), 1))
        for first, second in combinations(range(7), 2):
            row = [0] * 7
            row[first] = 1
            row[second] = 1
            weight = (2 if incident[point][first] else 1) * (
                2 if incident[point][second] else 1
            )
            row_options.append((tuple(row), weight))
        options.append(row_options)

    @lru_cache(maxsize=None)
    def recurse(point: int, remaining: tuple[int, ...]) -> tuple[int, int]:
        if point == 7:
            accepted = int(all(value == 0 for value in remaining))
            return accepted, accepted
        underlying = 0
        labeled = 0
        for row, weight in options[point]:
            if any(row[line] > remaining[line] for line in range(7)):
                continue
            next_remaining = tuple(
                remaining[line] - row[line] for line in range(7)
            )
            child_underlying, child_labeled = recurse(
                point + 1, next_remaining
            )
            underlying += child_underlying
            labeled += weight * child_labeled
        return underlying, labeled

    underlying, labeled = recurse(0, (2,) * 7)
    return {
        "underlying_capacity_bounded_multigraphs": underlying,
        "labeled_binary_columns": labeled,
        "dp_states": recurse.cache_info().currsize,
    }


def full_cycle_census() -> dict[str, int]:
    """Exhaustively classify all labeled two-factor columns by half-cycle type."""

    lines = fano_lines()
    incident = [
        [point in lines[line] for line in range(7)] for point in range(7)
    ]
    options: list[list[tuple[tuple[int, int], int]]] = []
    for point in range(7):
        row_options: list[tuple[tuple[int, int], int]] = []
        for line in range(7):
            if incident[point][line]:
                row_options.append(((line, line), 1))
        for first, second in combinations(range(7), 2):
            weight = (2 if incident[point][first] else 1) * (
                2 if incident[point][second] else 1
            )
            row_options.append(((first, second), weight))
        options.append(row_options)

    remaining = [2] * 7
    chosen: list[tuple[int, int] | None] = [None] * 7
    census: Counter[tuple[int, ...]] = Counter()

    def cycle_type() -> tuple[int, ...]:
        adjacency: list[list[int]] = [[] for _ in range(14)]
        for point, selected in enumerate(chosen):
            if selected is None:
                raise AssertionError("incomplete factor")
            first, second = selected
            adjacency[point].append(7 + first)
            adjacency[7 + first].append(point)
            adjacency[point].append(7 + second)
            adjacency[7 + second].append(point)
        seen = [False] * 14
        point_counts: list[int] = []
        for point in range(7):
            if seen[point]:
                continue
            stack = [point]
            seen[point] = True
            component_points = 0
            while stack:
                vertex = stack.pop()
                if vertex < 7:
                    component_points += 1
                for neighbor in adjacency[vertex]:
                    if not seen[neighbor]:
                        seen[neighbor] = True
                        stack.append(neighbor)
            point_counts.append(component_points)
        return tuple(sorted(point_counts, reverse=True))

    def recurse(point: int, weight: int) -> None:
        if point == 7:
            if all(value == 0 for value in remaining):
                census[cycle_type()] += weight
            return
        for (first, second), option_weight in options[point]:
            if first == second:
                if remaining[first] < 2:
                    continue
                remaining[first] -= 2
                chosen[point] = (first, second)
                recurse(point + 1, weight * option_weight)
                remaining[first] += 2
            else:
                if remaining[first] == 0 or remaining[second] == 0:
                    continue
                remaining[first] -= 1
                remaining[second] -= 1
                chosen[point] = (first, second)
                recurse(point + 1, weight * option_weight)
                remaining[first] += 1
                remaining[second] += 1
        chosen[point] = None

    recurse(0, 1)
    return {
        "+".join(str(part) for part in cycle_type): census[cycle_type]
        for cycle_type in sorted(census, reverse=True)
    }


def square_mod(
    matrix: Sequence[Sequence[int]], prime: int
) -> list[list[int]]:
    size = len(matrix)
    return [
        [
            sum(matrix[i][k] * matrix[k][j] for k in range(size)) % prime
            for j in range(size)
        ]
        for i in range(size)
    ]


def analyze(include_full_census: bool = False) -> dict[str, object]:
    fixed = fixed_operators()
    support = fixed["support"]
    support_to_o = fixed["support_to_o"]
    labels = fixed["labels"]
    support_squared = fixed["support_squared"]
    gram = fixed["gram"]
    gram_plus = fixed["gram_plus"]
    r_projector = fixed["r_projector"]
    c_so = fixed["c_so"]
    h_r = fixed["h_r"]
    fixed_c = fixed["fixed_c"]
    signed = fixed["signed_kernel"]
    assert isinstance(support, list)
    assert isinstance(support_to_o, list)
    assert isinstance(labels, list)
    assert isinstance(support_squared, list)
    assert isinstance(gram, list)
    assert isinstance(gram_plus, list)
    assert isinstance(r_projector, list)
    assert isinstance(c_so, list)
    assert isinstance(h_r, list)
    assert isinstance(fixed_c, list)
    assert isinstance(signed, list)

    # The fixed SS block.
    expected_gram = zeros(14, 14)
    for i in range(14):
        for j in range(14):
            expected_gram[i][j] = (
                Q(12) * Q(i == j)
                - support[i][j]
                + Q(2)
                - support_squared[i][j]
            )
    if gram != expected_gram:
        raise AssertionError("fixed SS block failed")

    # Moore-Penrose and projector identities.
    if multiply(multiply(gram, gram_plus), gram) != gram:
        raise AssertionError("G G+ G != G")
    if multiply(r_projector, r_projector) != r_projector:
        raise AssertionError("R is not idempotent")
    if r_projector != transpose(r_projector):
        raise AssertionError("R is not symmetric")
    if h_r != transpose(h_r):
        raise AssertionError("H_R is not symmetric")
    if multiply(h_r, r_projector) != h_r:
        raise AssertionError("H_R is not supported on R")
    if multiply(support_to_o, h_r) != c_so:
        raise AssertionError("fixed SO action failed")

    signed_column = [[value] for value in signed]
    if multiply(transpose(signed_column), support_to_o) != [([Q(0)] * 70)]:
        raise AssertionError("signed vector is not the left kernel")

    support_degrees = [int(sum(row)) for row in support]
    p_row_degrees = [int(sum(row)) for row in support_to_o]
    p_col_degrees = [
        int(sum(support_to_o[row][col] for row in range(14)))
        for col in range(70)
    ]
    minor = spanning_tree_minor(support_to_o, labels)
    if abs(int(minor["determinant"])) != 1:
        raise AssertionError("SNF unit minor failed")

    diagonal_c = Counter(fixed_c[i][i] for i in range(70))
    off_diagonal_c = Counter(
        fixed_c[i][j] for i in range(70) for j in range(i + 1, 70)
    )
    fixed_mod7 = [[value % 7 for value in row] for row in fixed_c]
    fixed_mod7_square = square_mod(fixed_mod7, 7)
    if any(value for row in fixed_mod7_square for value in row):
        raise AssertionError("fixed C mod 7 is not square-zero")

    two_factors = two_factor_dp()
    result: dict[str, object] = {
        "schema_version": 1,
        "claim_label": "DERIVED",
        "python": platform.python_version(),
        "domain": {
            "support_vertices": 14,
            "O_vertices": 70,
            "Q_vertices": 15,
            "automorphism_quotient": False,
            "fixed_O_Q_design": False,
            "raw_weight_14_columns": math.comb(70, 14),
            "two_factor_columns": two_factors,
        },
        "fixed_support": {
            "support_degree_set": sorted(set(support_degrees)),
            "support_to_O_row_degree_set": sorted(set(p_row_degrees)),
            "support_to_O_column_degree_set": sorted(set(p_col_degrees)),
            "support_adjacency_sha256": canonical_json_sha256(
                matrix_payload(support)
            ),
            "support_to_O_sha256": canonical_json_sha256(
                matrix_payload(support_to_o)
            ),
            "O_labels_sha256": canonical_json_sha256(labels),
            "SS_block_identity": True,
        },
        "kernel_snf": {
            "rank_P_over_Q": rank(support_to_o),
            "kernel_dimension_P": 70 - rank(support_to_o),
            "left_kernel_vector": [int(value) for value in signed],
            "snf_nonzero_invariant_factors": [1] * 13,
            "snf_zero_count": 1,
            "unit_minor_witness": minor,
        },
        "projector_reduction": {
            "rank_R": int(matrix_trace(r_projector)),
            "trace_H_R": int(matrix_trace(h_r)),
            "rank_W_for_every_admissible_B": 14,
            "rank_U_for_every_admissible_B": 43,
            "residual_projector_rank": 16,
            "residual_positive_eigenvalue_multiplicity": 27,
            "residual_negative_eigenvalue_multiplicity": 16,
            "continuous_symmetric_K_block_before_B": 57 * 58 // 2,
            "continuous_symmetric_U_block_after_B": 43 * 44 // 2,
            "rank_16_projector_grassmann_dimension": 16 * 27,
        },
        "integral_projector_numerator": {
            "definition": "L=C-7*B*B^T-21*H=147*E",
            "fixed_C_sha256": canonical_json_sha256(fixed_c),
            "fixed_C_diagonal_distribution": {
                str(key): diagonal_c[key] for key in sorted(diagonal_c)
            },
            "fixed_C_off_diagonal_distribution": {
                str(key): off_diagonal_c[key]
                for key in sorted(off_diagonal_c)
            },
            "solution_L_diagonal_distribution": {"30": 28, "36": 42},
            "trace_L": 147 * 16,
            "equation": "L^2=147L",
            "annihilators": ["P*L=0", "B^T*L=0"],
            "mod_7": {
                "L_equals_fixed_C": True,
                "fixed_rank": rank_mod(fixed_mod7, 7),
                "square_zero": True,
            },
            "mod_3": "L=-B*B^T",
            "binary_recovery": "H=(C-7*B*B^T-L)/21 is symmetric hollow binary",
        },
        "status_wall": {
            "complete_binary_solution": "UNKNOWN",
            "complete_exclusion": "UNKNOWN",
            "rooted_graph_extension": "UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
    }
    if include_full_census:
        cycle_census = full_cycle_census()
        if sum(cycle_census.values()) != two_factors["labeled_binary_columns"]:
            raise AssertionError("cycle census total mismatch")
        result["domain"]["two_factor_cycle_census"] = cycle_census
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full-census",
        action="store_true",
        help="enumerate all 4,946,952 underlying two-factors by cycle type",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            analyze(include_full_census=args.full_census),
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
