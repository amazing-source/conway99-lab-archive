"""Exact coefficient model for the level-7 index-10/index-70 Jacobi pair.

The script does not inspect or import Wave 126.  It constructs the proposed
239-dimensional weak-Jacobi module, links its L and K sides by Fricke, and
emits exact rational constraint matrices.  Floating LP calls are diagnostic
only; no infeasibility is promoted without an exact Farkas identity.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import pickle
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Iterable


Q = Fraction
HERE = Path(__file__).resolve().parent
LEVEL = 7
WEIGHT = 22
INDEX_L = 10
INDEX_K = 70
QDISC = 16
MODEL_CACHE_VERSION = "wave127-fricke-eigen-model-v1"
CHARACTER = (0, 1, 1, -1, 1, -1, -1)
Poly = dict[tuple[int, int], Q]
Product = tuple[tuple[int, str], tuple[int, str]]


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0

    class Status(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("available_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("available_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended", ctypes.c_ulonglong),
        ]

    state = Status()
    state.length = ctypes.sizeof(state)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * state.available_phys / state.total_phys


def qtext(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def clean(poly: Poly) -> Poly:
    return {key: value for key, value in poly.items() if value}


def poly_add(left: Poly, right: Poly, scale: Q = Q(1)) -> Poly:
    out: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    out.update(left)
    for key, value in right.items():
        out[key] += scale * value
    return clean(dict(out))


def poly_mul(left: Poly, right: Poly, qmax: int) -> Poly:
    out: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for (n1, r1), c1 in left.items():
        for (n2, r2), c2 in right.items():
            if n1 + n2 <= qmax:
                out[n1 + n2, r1 + r2] += c1 * c2
    return clean(dict(out))


def poly_power(base: Poly, exponent: int, qmax: int) -> Poly:
    out: Poly = {(0, 0): Q(1)}
    factor = base
    while exponent:
        if exponent & 1:
            out = poly_mul(out, factor, qmax)
        exponent >>= 1
        if exponent:
            factor = poly_mul(factor, factor, qmax)
    return out


def phi_minus2(qmax: int) -> Poly:
    out: Poly = {(0, -1): Q(1), (0, 0): Q(-2), (0, 1): Q(1)}
    for n in range(1, qmax + 1):
        scalar = {
            (j * n, 0): Q(math.comb(j + 3, 3))
            for j in range(qmax // n + 1)
        }
        plus = {(0, 0): Q(1), (n, 1): Q(-2), (2 * n, 2): Q(1)}
        minus = {(0, 0): Q(1), (n, -1): Q(-2), (2 * n, -2): Q(1)}
        out = poly_mul(poly_mul(poly_mul(out, scalar, qmax), plus, qmax), minus, qmax)
    return out


def theta_terms(kind: str, q8max: int) -> dict[tuple[int, int], Q]:
    out: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for n in range(-48, 49):
        if kind == "theta2":
            q8, y2, coefficient = (2 * n + 1) ** 2, 2 * n + 1, 1
        elif kind == "theta3":
            q8, y2, coefficient = 4 * n * n, 2 * n, 1
        elif kind == "theta4":
            q8, y2 = 4 * n * n, 2 * n
            coefficient = -1 if n % 2 else 1
        else:
            raise ValueError(kind)
        if q8 <= q8max + 8:
            out[q8, y2] += Q(coefficient)
    return clean(dict(out))


def qy_mul(
    left: dict[tuple[int, int], Q],
    right: dict[tuple[int, int], Q],
    q8max: int,
) -> dict[tuple[int, int], Q]:
    out: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for (q1, y1), c1 in left.items():
        for (q2, y2), c2 in right.items():
            if q1 + q2 <= q8max:
                out[q1 + q2, y1 + y2] += c1 * c2
    return clean(dict(out))


def theta_ratio_q8(kind: str, qmax: int) -> dict[tuple[int, int], Q]:
    q8max = 8 * qmax + 2
    theta = theta_terms(kind, q8max)
    numerator = qy_mul(theta, theta, q8max)
    denominator: defaultdict[int, Q] = defaultdict(Q)
    for (q8, _y2), coefficient in numerator.items():
        denominator[q8] += coefficient
    shift = min(q for q, coefficient in denominator.items() if coefficient)
    numerator = {(q - shift, y): c for (q, y), c in numerator.items()}
    denominator = {q - shift: c for q, c in denominator.items()}
    d0 = denominator[0]
    inverse = {0: Q(1) / d0}
    for n in range(1, 8 * qmax + 1):
        inverse[n] = -sum(
            denominator.get(j, Q(0)) * inverse.get(n - j, Q(0))
            for j in range(1, n + 1)
        ) / d0
    out: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for (q8, y2), coefficient in numerator.items():
        for extra, value in inverse.items():
            if q8 + extra <= 8 * qmax:
                out[q8 + extra, y2] += coefficient * value
    return clean(dict(out))


def phi_zero(qmax: int) -> Poly:
    combined: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for kind in ("theta2", "theta3", "theta4"):
        for key, value in theta_ratio_q8(kind, qmax).items():
            combined[key] += 4 * value
    out: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for (q8, y2), coefficient in combined.items():
        if coefficient:
            if q8 % 8 or y2 % 2:
                raise AssertionError(("fractional exponent", q8, y2))
            out[q8 // 8, y2 // 2] += coefficient
    return clean(dict(out))


def scale_jacobi(poly: Poly, factor: int, qmax: int) -> Poly:
    return {
        (factor * n, factor * r): coefficient
        for (n, r), coefficient in poly.items()
        if factor * n <= qmax
    }


def bernoulli_numbers(limit: int) -> list[Q]:
    values = [Q(0)] * (limit + 1)
    values[0] = Q(1)
    for degree in range(1, limit + 1):
        values[degree] = -sum(
            Q(math.comb(degree + 1, j)) * values[j]
            for j in range(degree)
        ) / Q(degree + 1)
    return values


BERNOULLI = bernoulli_numbers(42)


def chi(n: int) -> int:
    return CHARACTER[n % LEVEL]


def bernoulli_polynomial(degree: int, value: Q) -> Q:
    return sum(
        Q(math.comb(degree, j))
        * BERNOULLI[j]
        * value ** (degree - j)
        for j in range(degree + 1)
    )


def generalized_bernoulli(degree: int) -> Q:
    return Q(LEVEL ** (degree - 1)) * sum(
        Q(chi(a)) * bernoulli_polynomial(degree, Q(a, LEVEL))
        for a in range(1, LEVEL + 1)
    )


def eisenstein(weight: int, orientation: str, qmax: int) -> list[Q]:
    series = [Q(0)] * (qmax + 1)
    if orientation == "C":
        series[0] = -generalized_bernoulli(weight) / Q(2 * weight)
    elif orientation != "T":
        raise ValueError(orientation)
    for divisor in range(1, qmax + 1):
        power = divisor ** (weight - 1)
        for n in range(divisor, qmax + 1, divisor):
            series[n] += (
                Q(chi(divisor)) * power
                if orientation == "C"
                else Q(chi(n // divisor)) * power
            )
    return series


def series_mul(left: list[Q], right: list[Q], qmax: int) -> list[Q]:
    return [
        sum(left[j] * right[n - j] for j in range(n + 1))
        for n in range(qmax + 1)
    ]


def rank(matrix: list[list[Q]]) -> int:
    work = [row[:] for row in matrix]
    if not work:
        return 0
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def inverse(matrix: list[list[Q]]) -> list[list[Q]]:
    size = len(matrix)
    work = [
        row[:] + [Q(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            row for row in range(column, size) if work[row][column]
        )
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[column], strict=True)
            ]
    return [row[size:] for row in work]


def nullspace(matrix: list[list[Q]]) -> list[list[Q]]:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivots = []
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(
                    work[row], work[pivot_row], strict=True
                )
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break
    free = [column for column in range(columns) if column not in pivots]
    basis = []
    for free_column in free:
        vector = [Q(0)] * columns
        vector[free_column] = Q(1)
        for row, pivot_column in enumerate(pivots):
            vector[pivot_column] = -work[row][free_column]
        basis.append(vector)
    return basis


def modular_dimension(weight: int) -> int:
    return 2 * (weight // 3) + 1


def modular_basis(weight: int, qmax: int) -> list[dict[str, object]]:
    # Independence has to be checked through the level-7 Sturm bound even
    # when the requested Jacobi cutoff is smaller.
    sturm = 2 * weight // 3
    basis_qmax = max(qmax, sturm)
    eisenstein_cache = {
        (odd_weight, orientation): eisenstein(
            odd_weight, orientation, basis_qmax
        )
        for odd_weight in range(3, weight - 1, 2)
        for orientation in ("C", "T")
    }
    candidates: list[Product] = []
    for left_weight in range(3, weight - 2, 2):
        right_weight = weight - left_weight
        if right_weight < 3 or right_weight % 2 == 0:
            continue
        for left_type in ("C", "T"):
            for right_type in ("C", "T"):
                candidates.append(
                    ((left_weight, left_type), (right_weight, right_type))
                )
    candidates = sorted(candidates, key=repr, reverse=True)

    def expansion(product: Product) -> list[Q]:
        return series_mul(
            eisenstein_cache[product[0]],
            eisenstein_cache[product[1]],
            basis_qmax,
        )

    expected = modular_dimension(weight)
    selected: list[Product] = []
    old_rank = 0
    for candidate in candidates:
        trial = selected + [candidate]
        matrix = [
            [expansion(product)[n] for product in trial]
            for n in range(sturm + 1)
        ]
        new_rank = rank(matrix)
        if new_rank > old_rank:
            selected = trial
            old_rank = new_rank
        if old_rank == expected:
            break
    if old_rank != expected:
        raise AssertionError(("modular basis rank", weight, old_rank, expected))

    raw_rows = []
    for product in selected:
        mapped = []
        factor = Q(-1)
        for factor_weight, orientation in product:
            exponent = (
                (factor_weight - 1) // 2
                if orientation == "C"
                else (1 - factor_weight) // 2
            )
            factor *= (
                Q(LEVEL**exponent)
                if exponent >= 0
                else Q(1, LEVEL ** (-exponent))
            )
            mapped.append(
                (factor_weight, "T" if orientation == "C" else "C")
            )
        mapped_product = (mapped[0], mapped[1])
        raw_rows.append(
            {
                "product": product,
                "series": expansion(product),
                "fricke_factor": factor,
                "fricke_product": mapped_product,
                "fricke_series": [
                    factor * coefficient
                    for coefficient in expansion(mapped_product)
                ],
            }
        )

    # Replace the raw Eisenstein products by an exact Fourier-echelon basis.
    # This is an invertible rational change of columns, but avoids presenting
    # LP solvers with generalized-Bernoulli constants of wildly different
    # sizes.
    pivot_q = []
    old_rank = 0
    coefficient_rows = [
        [row["series"][n] for row in raw_rows]
        for n in range(sturm + 1)
    ]
    for n, coefficient_row in enumerate(coefficient_rows):
        new_rank = rank(
            [coefficient_rows[index] for index in pivot_q]
            + [coefficient_row]
        )
        if new_rank > old_rank:
            pivot_q.append(n)
            old_rank = new_rank
        if old_rank == expected:
            break
    transform = inverse([coefficient_rows[n] for n in pivot_q])
    rows = []
    for column in range(expected):
        rows.append(
            {
                "combination": [
                    {
                        "coefficient": qtext(transform[row][column]),
                        "product": raw_rows[row]["product"],
                    }
                    for row in range(expected)
                    if transform[row][column]
                ],
                "pivot_q": pivot_q[column],
                "series": [
                    sum(
                        raw_rows[row]["series"][n]
                        * transform[row][column]
                        for row in range(expected)
                    )
                    for n in range(basis_qmax + 1)
                ],
                "fricke_series": [
                    sum(
                        raw_rows[row]["fricke_series"][n]
                        * transform[row][column]
                        for row in range(expected)
                    )
                    for n in range(basis_qmax + 1)
                ],
            }
        )

    # Diagonalize the exact Fricke involution, then echelonize separately in
    # its + and - eigenspaces.  This keeps both cusps numerically visible.
    fricke_matrix = [
        [rows[column]["fricke_series"][n] for column in range(expected)]
        for n in pivot_q
    ]
    square_check = [
        [
            sum(
                fricke_matrix[i][k] * fricke_matrix[k][j]
                for k in range(expected)
            )
            for j in range(expected)
        ]
        for i in range(expected)
    ]
    if square_check != [
        [Q(int(i == j)) for j in range(expected)]
        for i in range(expected)
    ]:
        raise AssertionError(("Fricke involution", weight))

    eigen_rows = []
    for eigenvalue in (1, -1):
        vectors = nullspace(
            [
                [
                    fricke_matrix[i][j]
                    - Q(eigenvalue * int(i == j))
                    for j in range(expected)
                ]
                for i in range(expected)
            ]
        )
        raw_eigen = [
            [
                sum(
                    rows[column]["series"][n] * vector[column]
                    for column in range(expected)
                )
                for n in range(basis_qmax + 1)
            ]
            for vector in vectors
        ]
        eigen_pivots = []
        old_rank = 0
        for n in range(sturm + 1):
            coefficient_row = [
                series[n] for series in raw_eigen
            ]
            new_rank = rank(
                [
                    [series[index] for series in raw_eigen]
                    for index in eigen_pivots
                ]
                + [coefficient_row]
            )
            if new_rank > old_rank:
                eigen_pivots.append(n)
                old_rank = new_rank
            if old_rank == len(vectors):
                break
        eigen_transform = inverse(
            [
                [series[n] for series in raw_eigen]
                for n in eigen_pivots
            ]
        )
        for column in range(len(vectors)):
            series = [
                sum(
                    raw_eigen[row][n] * eigen_transform[row][column]
                    for row in range(len(vectors))
                )
                for n in range(basis_qmax + 1)
            ]
            eigen_rows.append(
                {
                    "combination": "Fricke-eigen Fourier-echelon",
                    "pivot_q": eigen_pivots[column],
                    "fricke_eigenvalue": eigenvalue,
                    "series": series,
                    "fricke_series": [
                        Q(eigenvalue) * value for value in series
                    ],
                }
            )
    if len(eigen_rows) != expected:
        raise AssertionError(("Fricke eigenspace dimensions", weight))
    return eigen_rows


def convolve_modular_jacobi(series: list[Q], jacobi: Poly, qmax: int) -> Poly:
    out: defaultdict[tuple[int, int], Q] = defaultdict(Q)
    for n_mod, coefficient in enumerate(series):
        if not coefficient:
            continue
        for (n_jacobi, r), value in jacobi.items():
            if n_mod + n_jacobi <= qmax:
                out[n_mod + n_jacobi, r] += coefficient * value
    return clean(dict(out))


def build_columns(qmax: int) -> tuple[list[dict[str, object]], dict[str, object]]:
    if free_memory_percent() < 15:
        raise RuntimeError("memory floor")
    aa = phi_minus2(qmax)
    bb = phi_zero(qmax)
    if [bb.get((0, r), 0) for r in (-1, 0, 1)] != [1, 10, 1]:
        raise AssertionError("B normalization")
    aa_powers = [{(0, 0): Q(1)}]
    bb_powers = [{(0, 0): Q(1)}]
    for _ in range(INDEX_L):
        aa_powers.append(poly_mul(aa_powers[-1], aa, qmax))
        bb_powers.append(poly_mul(bb_powers[-1], bb, qmax))
    jacobi = [
        poly_mul(
            aa_powers[c],
            bb_powers[INDEX_L - c],
            qmax,
        )
        for c in range(INDEX_L + 1)
    ]
    jacobi_scaled = [scale_jacobi(poly, LEVEL, qmax) for poly in jacobi]

    columns = []
    dimensions = []
    for c in range(INDEX_L + 1):
        weight = WEIGHT + 2 * c
        basis = modular_basis(weight, qmax)
        dimensions.append(len(basis))
        scale = -Q(1, LEVEL ** (3 + c))
        for index, row in enumerate(basis):
            l_poly = convolve_modular_jacobi(row["series"], jacobi[c], qmax)
            k_poly = convolve_modular_jacobi(
                [scale * value for value in row["fricke_series"]],
                jacobi_scaled[c],
                qmax,
            )
            columns.append(
                {
                    "c": c,
                    "weight": weight,
                    "basis_index": index,
                    "combination": row["combination"],
                    "pivot_q": row["pivot_q"],
                    "fricke_eigenvalue": row["fricke_eigenvalue"],
                    "L": l_poly,
                    "K": k_poly,
                }
            )
    if sum(dimensions) != 239 or len(columns) != 239:
        raise AssertionError(("module dimension", dimensions))
    return columns, {
        "dimensions_by_c": dimensions,
        "total_dimension": len(columns),
        "A_q0": {str(r): qtext(aa.get((0, r), Q(0))) for r in range(-1, 2)},
        "B_q0": {str(r): qtext(bb.get((0, r), Q(0))) for r in range(-1, 2)},
    }


def row_for_key(columns: list[dict[str, object]], side: str, key: tuple[int, int]) -> list[Q]:
    return [column[side].get(key, Q(0)) for column in columns]


def add_equality(
    equalities: list[dict[str, object]],
    label: str,
    row: list[Q],
    right: Q,
) -> None:
    if any(row) or right:
        equalities.append({"label": label, "row": row, "right": right})


def add_inequality(
    inequalities: list[dict[str, object]],
    label: str,
    row: list[Q],
) -> None:
    if any(row):
        inequalities.append({"label": label, "row": row})


def build_constraints(
    columns: list[dict[str, object]],
    cutoff: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    equalities: list[dict[str, object]] = []
    inequalities: list[dict[str, object]] = []

    for side in ("L", "K"):
        add_equality(
            equalities,
            f"{side}:constant",
            row_for_key(columns, side, (0, 0)),
            Q(2079),
        )
        keys = sorted(
            {
                key
                for column in columns
                for key in column[side]
                if key[0] <= cutoff
            }
        )
        index = INDEX_L if side == "L" else INDEX_K
        for n, r in keys:
            row = row_for_key(columns, side, (n, r))
            outside_holomorphic = r * r > 4 * index * n
            k_gap = side == "K" and 1 <= n <= 6
            k_short_forbidden = (
                side == "K" and 7 <= n <= 10 and abs(r) > 28
            )
            if outside_holomorphic or k_gap or k_short_forbidden:
                add_equality(
                    equalities,
                    (
                        f"{side}:zero:n{n}:r{r}:"
                        f"{'hol' if outside_holomorphic else 'graph'}"
                    ),
                    row,
                    Q(0),
                )
            else:
                add_inequality(
                    inequalities,
                    f"{side}:positive:n{n}:r{r}",
                    row,
                )

        for n in range(1, cutoff + 1):
            live_r = sorted(
                {
                    r
                    for column in columns
                    for (nn, r) in column[side]
                    if nn == n
                }
            )
            if not live_r:
                continue
            moment = [Q(0)] * len(columns)
            coefficient = 10 if side == "L" else 70
            for r in live_r:
                row = row_for_key(columns, side, (n, r))
                moment = [
                    left + (11 * r * r - coefficient * n) * right
                    for left, right in zip(moment, row, strict=True)
                ]
            add_equality(
                equalities,
                f"{side}:moment:n{n}",
                moment,
                Q(0),
            )
    return equalities, inequalities


def reduced_constraints_for_solver(
    equalities: list[dict[str, object]],
    inequalities: list[dict[str, object]],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, int],
]:
    from flint import fmpq, fmpq_mat

    variables = len(equalities[0]["row"])

    def fq(value: Q):
        return fmpq(value.numerator, value.denominator)

    augmented_transpose = fmpq_mat(
        variables + 1,
        len(equalities),
        [
            fq(
                equalities[column]["row"][row]
                if row < variables
                else equalities[column]["right"]
            )
            for row in range(variables + 1)
            for column in range(len(equalities))
        ],
    )
    reduced, equality_rank = augmented_transpose.rref()
    equality_pivots = [
        next(
            column
            for column in range(len(equalities))
            if reduced[row, column]
        )
        for row in range(equality_rank)
    ]
    independent_equalities = [
        equalities[index] for index in equality_pivots
    ]

    seen = set()
    deduplicated_inequalities = []
    for constraint in inequalities:
        first = next(value for value in constraint["row"] if value)
        scale = abs(first)
        key = tuple(value / scale for value in constraint["row"])
        if key in seen:
            continue
        seen.add(key)
        deduplicated_inequalities.append(constraint)
    return (
        independent_equalities,
        deduplicated_inequalities,
        {
            "original_equalities": len(equalities),
            "independent_equalities": len(independent_equalities),
            "original_inequalities": len(inequalities),
            "deduplicated_inequalities": len(
                deduplicated_inequalities
            ),
        },
    )


def balanced_float_rows(
    equalities: list[dict[str, object]],
    inequalities: list[dict[str, object]],
) -> tuple[object, object, object, object, dict[str, float]]:
    import numpy as np

    a_eq = np.array(
        [
            [float(value) for value in constraint["row"]]
            for constraint in equalities
        ],
        dtype=float,
    )
    b_eq = np.array(
        [float(constraint["right"]) for constraint in equalities],
        dtype=float,
    )
    g_rows = np.array(
        [
            [float(value) for value in constraint["row"]]
            for constraint in inequalities
        ],
        dtype=float,
    )
    matrix = np.vstack([a_eq, g_rows])
    right = np.concatenate([b_eq, np.zeros(len(inequalities))])
    column_scales = np.ones(matrix.shape[1])
    for _ in range(16):
        row_factors = np.ones(matrix.shape[0])
        for row in range(matrix.shape[0]):
            values = np.abs(matrix[row][np.nonzero(matrix[row])])
            if right[row]:
                values = np.append(values, abs(right[row]))
            if len(values):
                center = (
                    math.log(float(np.min(values)))
                    + math.log(float(np.max(values)))
                ) / 2
                row_factors[row] = math.exp(-center)
        matrix *= row_factors[:, None]
        right *= row_factors

        column_factors = np.ones(matrix.shape[1])
        for column in range(matrix.shape[1]):
            values = np.abs(
                matrix[:, column][np.nonzero(matrix[:, column])]
            )
            if len(values):
                center = (
                    math.log(float(np.min(values)))
                    + math.log(float(np.max(values)))
                ) / 2
                column_factors[column] = math.exp(-center)
        matrix *= column_factors[None, :]
        column_scales *= column_factors

    nonzero = np.abs(matrix[np.nonzero(matrix)])
    stats = {
        "balanced_min_nonzero": float(np.min(nonzero)),
        "balanced_max": float(np.max(np.abs(matrix))),
        "balanced_rhs_min_nonzero": float(
            np.min(np.abs(right[np.nonzero(right)]))
        ),
        "balanced_rhs_max": float(np.max(np.abs(right))),
    }
    split = len(equalities)
    return (
        matrix[:split],
        right[:split],
        matrix[split:],
        column_scales,
        stats,
    )


def float_feasibility(
    equalities: list[dict[str, object]],
    inequalities: list[dict[str, object]],
    variables: int,
    include_solution: bool = False,
) -> dict[str, object]:
    import numpy as np
    from scipy.optimize import linprog

    solver_equalities, solver_inequalities, reduction = (
        reduced_constraints_for_solver(equalities, inequalities)
    )
    a_eq, b_eq, g_rows, column_scales, balancing = balanced_float_rows(
        solver_equalities, solver_inequalities
    )
    a_ub = -g_rows
    result = linprog(
        np.zeros(variables),
        A_ub=np.array(a_ub) if len(a_ub) else None,
        b_ub=np.zeros(len(a_ub)) if len(a_ub) else None,
        A_eq=np.array(a_eq),
        b_eq=np.array(b_eq),
        bounds=[(None, None)] * variables,
        method="highs",
        options={"dual_feasibility_tolerance": 1e-8, "primal_feasibility_tolerance": 1e-8},
    )
    diagnostic = {
        "success": bool(result.success),
        "status": int(result.status),
        "message": str(result.message),
        "classification": (
            "FLOAT_FEASIBLE_DIAGNOSTIC"
            if result.success
            else "FLOAT_INFEASIBLE_DIAGNOSTIC"
        ),
    }
    diagnostic["balancing"] = balancing
    diagnostic["exact_reduction"] = reduction
    if result.success:
        original_solution = column_scales * result.x
        equality_residual = max(
            (
                abs(
                    sum(
                        float(value) * original_solution[index]
                        for index, value in enumerate(constraint["row"])
                    )
                    - float(constraint["right"])
                )
                / max(
                    1.0,
                    abs(float(constraint["right"])),
                    max(abs(float(value)) for value in constraint["row"]),
                )
                for constraint in equalities
            ),
            default=0.0,
        )
        inequality_margin = min(
            (
                sum(
                    float(value) * original_solution[index]
                    for index, value in enumerate(constraint["row"])
                )
                / max(
                    1.0,
                    max(abs(float(value)) for value in constraint["row"]),
                )
                for constraint in inequalities
            ),
            default=0.0,
        )
        diagnostic["max_scaled_equality_residual"] = equality_residual
        diagnostic["min_scaled_inequality_margin"] = inequality_margin
        diagnostic["max_abs_variable"] = float(max(abs(original_solution)))
        if include_solution:
            diagnostic["_solution"] = original_solution.tolist()
    return diagnostic


def recover_exact_vertex(
    equalities: list[dict[str, object]],
    inequalities: list[dict[str, object]],
    variables: int,
) -> dict[str, object]:
    """Try to turn a floating basic feasible point into an exact rational one.

    This is deliberately one-way: failure leaves exact feasibility UNKNOWN.
    Success is checked against every original rational row.
    """

    from flint import fmpq, fmpq_mat

    diagnostic = float_feasibility(
        equalities, inequalities, variables, include_solution=True
    )
    if not diagnostic["success"]:
        return {
            "classification": "NO_EXACT_CANDIDATE_FROM_FLOAT",
            "floating_diagnostic": diagnostic,
        }
    solution = diagnostic.pop("_solution")

    def scaled_value(constraint: dict[str, object]) -> float:
        row = constraint["row"]
        scale = max(1.0, max(abs(float(value)) for value in row))
        return sum(
            float(value) * solution[index]
            for index, value in enumerate(row)
        ) / scale

    active = [
        constraint
        for constraint in inequalities
        if abs(scaled_value(constraint)) <= 2e-7
    ]
    combined = equalities + active

    def fq(value: Q):
        return fmpq(value.numerator, value.denominator)

    transpose = fmpq_mat(
        variables,
        len(combined),
        [
            fq(combined[column]["row"][row])
            for row in range(variables)
            for column in range(len(combined))
        ],
    )
    reduced, exact_rank = transpose.rref()
    pivot_columns = []
    for row in range(exact_rank):
        pivot = next(
            column
            for column in range(len(combined))
            if reduced[row, column]
        )
        pivot_columns.append(pivot)
    if exact_rank != variables:
        return {
            "classification": "ACTIVE_ROWS_DO_NOT_DEFINE_VERTEX",
            "floating_diagnostic": diagnostic,
            "active_inequalities": len(active),
            "exact_active_rank": exact_rank,
        }

    selected = [combined[index] for index in pivot_columns]
    square = fmpq_mat(
        variables,
        variables,
        [
            fq(value)
            for constraint in selected
            for value in constraint["row"]
        ],
    )
    right = fmpq_mat(
        variables,
        1,
        [
            fq(combined[index]["right"])
            if index < len(equalities)
            else fmpq(0)
            for index in pivot_columns
        ],
    )
    exact = square.solve(right, algorithm="dixon")
    candidate = [
        Q(int(exact[row, 0].numerator), int(exact[row, 0].denominator))
        for row in range(variables)
    ]

    failed_equalities = [
        constraint["label"]
        for constraint in equalities
        if sum(
            value * candidate[index]
            for index, value in enumerate(constraint["row"])
        )
        != constraint["right"]
    ]
    failed_inequalities = [
        constraint["label"]
        for constraint in inequalities
        if sum(
            value * candidate[index]
            for index, value in enumerate(constraint["row"])
        )
        < 0
    ]
    tight_inequalities = [
        constraint["label"]
        for constraint in inequalities
        if sum(
            value * candidate[index]
            for index, value in enumerate(constraint["row"])
        )
        == 0
    ]
    verified = not failed_equalities and not failed_inequalities
    return {
        "format": "wave127-exact-rational-candidate-v1",
        "classification": (
            "EXACT_RATIONAL_FEASIBLE"
            if verified
            else "EXACT_VERTEX_RECOVERY_FAILED"
        ),
        "floating_diagnostic": diagnostic,
        "active_inequalities": len(active),
        "selected_row_labels": [
            constraint["label"] for constraint in selected
        ],
        "failed_equalities": failed_equalities,
        "failed_inequalities": failed_inequalities,
        "tight_inequalities": tight_inequalities,
        "solution": [qtext(value) for value in candidate],
    }


def recover_exact_primal_reduced(
    equalities: list[dict[str, object]],
    inequalities: list[dict[str, object]],
    variables: int,
) -> dict[str, object]:
    import numpy as np
    from flint import fmpq, fmpq_mat
    from scipy.optimize import linprog

    solver_equalities, solver_inequalities, reduction = (
        reduced_constraints_for_solver(equalities, inequalities)
    )

    def fq(value: Q):
        return fmpq(value.numerator, value.denominator)

    def solve_affine_nonnegative(
        rows: list[list[Q]],
        constants: list[Q],
        depth: int = 0,
    ) -> tuple[list[Q] | None, list[dict[str, object]]]:
        dimension = len(rows[0]) if rows else 0
        trace: list[dict[str, object]] = []
        if dimension == 0:
            return (
                ([] if all(value >= 0 for value in constants) else None),
                [{"depth": depth, "dimension": 0}],
            )
        column_scales = np.ones(dimension)
        row_scales = np.ones(len(rows))
        for _ in range(12):
            for column in range(dimension):
                values = [
                    abs(float(row[column]))
                    / (row_scales[index] * column_scales[column])
                    for index, row in enumerate(rows)
                    if row[column]
                ]
                if values:
                    column_scales[column] *= math.sqrt(
                        min(values) * max(values)
                    )
            for index, (row, constant) in enumerate(
                zip(rows, constants, strict=True)
            ):
                values = [
                    abs(float(value))
                    / (column_scales[column] * row_scales[index])
                    for column, value in enumerate(row)
                    if value
                ]
                if constant:
                    values.append(
                        abs(float(constant)) / row_scales[index]
                    )
                if values:
                    row_scales[index] *= math.sqrt(
                        min(values) * max(values)
                    )
        scaled_rows = np.array(
            [
                [
                    float(value)
                    / (row_scales[row] * column_scales[column])
                    for column, value in enumerate(source)
                ]
                for row, source in enumerate(rows)
            ]
        )
        scaled_constants = np.array(
            [
                float(value) / row_scales[index]
                for index, value in enumerate(constants)
            ]
        )
        lp = linprog(
            np.zeros(dimension),
            A_ub=-scaled_rows,
            b_ub=scaled_constants,
            bounds=[(None, None)] * dimension,
            method="highs",
            options={
                "dual_feasibility_tolerance": 1e-9,
                "primal_feasibility_tolerance": 1e-9,
            },
        )
        trace.append(
            {
                "depth": depth,
                "dimension": dimension,
                "inequalities": len(rows),
                "float_success": bool(lp.success),
                "float_status": int(lp.status),
            }
        )
        if not lp.success:
            return None, trace
        parameters_float = lp.x / column_scales
        rounded = [
            Q(float(value)).limit_denominator(10**14)
            for value in parameters_float
        ]
        if all(
            constant
            + sum(
                row[column] * rounded[column]
                for column in range(dimension)
            )
            >= 0
            for row, constant in zip(rows, constants, strict=True)
        ):
            trace[-1]["outcome"] = "rational_rounding_verified"
            return rounded, trace
        if depth >= 6:
            trace[-1]["outcome"] = "depth_limit"
            return None, trace

        scaled_slacks = scaled_constants + scaled_rows @ lp.x
        for threshold in (
            1e-12,
            3e-12,
            1e-11,
            3e-11,
            1e-10,
            3e-10,
            1e-9,
            3e-9,
            1e-8,
        ):
            active = [
                index
                for index, value in enumerate(scaled_slacks)
                if abs(value) <= threshold
            ]
            if not active:
                continue
            active_augmented = [
                rows[index][:] + [-constants[index]]
                for index in active
            ]
            active_matrix = fmpq_mat(
                len(active_augmented),
                dimension + 1,
                [
                    fq(value)
                    for source in active_augmented
                    for value in source
                ],
            )
            active_rref, active_rank = active_matrix.rref()
            pivots = []
            inconsistent = False
            for row_index in range(active_rank):
                pivot = next(
                    column
                    for column in range(dimension + 1)
                    if active_rref[row_index, column]
                )
                if pivot == dimension:
                    inconsistent = True
                    break
                pivots.append(pivot)
            if inconsistent or not pivots or len(pivots) >= dimension:
                continue
            free_columns = [
                column
                for column in range(dimension)
                if column not in pivots
            ]
            face_particular = [Q(0)] * dimension
            face_directions = [
                [Q(0)] * len(free_columns) for _ in range(dimension)
            ]
            for index, free_column in enumerate(free_columns):
                face_directions[free_column][index] = Q(1)
            for row_index, pivot in enumerate(pivots):
                face_particular[pivot] = Q(
                    int(active_rref[row_index, dimension].numerator),
                    int(active_rref[row_index, dimension].denominator),
                )
                for index, free_column in enumerate(free_columns):
                    face_directions[pivot][index] = -Q(
                        int(
                            active_rref[row_index, free_column].numerator
                        ),
                        int(
                            active_rref[row_index, free_column].denominator
                        ),
                    )
            face_rows = []
            face_constants = []
            for source, constant in zip(rows, constants, strict=True):
                face_constants.append(
                    constant
                    + sum(
                        source[index] * face_particular[index]
                        for index in range(dimension)
                    )
                )
                face_rows.append(
                    [
                        sum(
                            source[index]
                            * face_directions[index][column]
                            for index in range(dimension)
                        )
                        for column in range(len(free_columns))
                    ]
                )
            trace_index = len(trace) - 1
            subparameters, subtrace = solve_affine_nonnegative(
                face_rows, face_constants, depth + 1
            )
            trace[trace_index].setdefault("faces_tried", []).append(
                {
                    "threshold": threshold,
                    "active": len(active),
                    "rank": len(pivots),
                    "subdimension": len(free_columns),
                    "success": subparameters is not None,
                }
            )
            trace.extend(subtrace)
            if subparameters is None:
                continue
            parameters = [
                face_particular[row]
                + sum(
                    face_directions[row][column]
                    * subparameters[column]
                    for column in range(len(free_columns))
                )
                for row in range(dimension)
            ]
            if all(
                constant
                + sum(
                    source[column] * parameters[column]
                    for column in range(dimension)
                )
                >= 0
                for source, constant in zip(
                    rows, constants, strict=True
                )
            ):
                return parameters, trace
        trace[0]["outcome"] = "no_face_verified"
        return None, trace

    augmented = fmpq_mat(
        len(solver_equalities),
        variables + 1,
        [
            fq(value)
            for constraint in solver_equalities
            for value in constraint["row"] + [constraint["right"]]
        ],
    )
    echelon, exact_rank = augmented.rref()
    pivots = []
    for row in range(exact_rank):
        pivot = next(
            column
            for column in range(variables + 1)
            if echelon[row, column]
        )
        if pivot == variables:
            return {
                "classification": "EXACT_PRIMAL_EQUALITIES_INCONSISTENT",
                "exact_reduction": reduction,
            }
        pivots.append(pivot)
    free = [column for column in range(variables) if column not in pivots]
    particular = [Q(0)] * variables
    directions = [[Q(0)] * len(free) for _ in range(variables)]
    for index, free_column in enumerate(free):
        directions[free_column][index] = Q(1)
    for row, pivot in enumerate(pivots):
        particular[pivot] = Q(
            int(echelon[row, variables].numerator),
            int(echelon[row, variables].denominator),
        )
        for index, free_column in enumerate(free):
            directions[pivot][index] = -Q(
                int(echelon[row, free_column].numerator),
                int(echelon[row, free_column].denominator),
            )

    affine_rows = []
    affine_constants = []
    for constraint in solver_inequalities:
        affine_constants.append(
            sum(
                value * particular[index]
                for index, value in enumerate(constraint["row"])
            )
        )
        affine_rows.append(
            [
                sum(
                    constraint["row"][index]
                    * directions[index][column]
                    for index in range(variables)
                )
                for column in range(len(free))
            ]
        )

    recursive_parameters, recursive_trace = solve_affine_nonnegative(
        affine_rows, affine_constants
    )
    if recursive_parameters is not None:
        candidate = [
            particular[row]
            + sum(
                directions[row][column] * recursive_parameters[column]
                for column in range(len(free))
            )
            for row in range(variables)
        ]
        failed_equalities = [
            constraint["label"]
            for constraint in equalities
            if sum(
                value * candidate[index]
                for index, value in enumerate(constraint["row"])
            )
            != constraint["right"]
        ]
        failed_inequalities = [
            constraint["label"]
            for constraint in inequalities
            if sum(
                value * candidate[index]
                for index, value in enumerate(constraint["row"])
            )
            < 0
        ]
        if not failed_equalities and not failed_inequalities:
            tight = [
                constraint["label"]
                for constraint in inequalities
                if sum(
                    value * candidate[index]
                    for index, value in enumerate(constraint["row"])
                )
                == 0
            ]
            return {
                "format": "wave127-exact-rational-candidate-v1",
                "classification": "EXACT_RATIONAL_FEASIBLE",
                "diagnostic": {
                    "exact_reduction": reduction,
                    "primal_affine_rank": exact_rank,
                    "primal_free_dimension": len(free),
                    "recursive_trace": recursive_trace,
                },
                "failed_equalities": [],
                "failed_inequalities": [],
                "tight_inequalities": tight,
                "solution": [qtext(value) for value in candidate],
            }

    column_scales = np.ones(len(free))
    row_scales = np.ones(len(affine_rows))
    for _ in range(12):
        for column in range(len(free)):
            values = [
                abs(float(row[column]))
                / (row_scales[index] * column_scales[column])
                for index, row in enumerate(affine_rows)
                if row[column]
            ]
            if values:
                column_scales[column] *= math.sqrt(
                    min(values) * max(values)
                )
        for index, (row, constant) in enumerate(
            zip(affine_rows, affine_constants, strict=True)
        ):
            values = [
                abs(float(value))
                / (column_scales[column] * row_scales[index])
                for column, value in enumerate(row)
                if value
            ]
            if constant:
                values.append(
                    abs(float(constant)) / row_scales[index]
                )
            if values:
                row_scales[index] *= math.sqrt(
                    min(values) * max(values)
                )
    scaled_rows = np.array(
        [
            [
                float(value)
                / (row_scales[row] * column_scales[column])
                for column, value in enumerate(source)
            ]
            for row, source in enumerate(affine_rows)
        ]
    )
    scaled_constants = np.array(
        [
            float(value) / row_scales[index]
            for index, value in enumerate(affine_constants)
        ]
    )
    nonzero = np.abs(scaled_rows[np.nonzero(scaled_rows)])
    reduced_lp = linprog(
        np.zeros(len(free)),
        A_ub=-scaled_rows,
        b_ub=scaled_constants,
        bounds=[(None, None)] * len(free),
        method="highs",
        options={
            "dual_feasibility_tolerance": 1e-9,
            "primal_feasibility_tolerance": 1e-9,
        },
    )
    diagnostic = {
        "exact_reduction": reduction,
        "primal_affine_rank": exact_rank,
        "primal_free_dimension": len(free),
        "recursive_trace": recursive_trace,
        "reduced_balanced_min_nonzero": float(np.min(nonzero)),
        "reduced_balanced_max": float(np.max(np.abs(scaled_rows))),
        "reduced_float_success": bool(reduced_lp.success),
        "reduced_float_status": int(reduced_lp.status),
        "reduced_float_message": str(reduced_lp.message),
    }
    if not reduced_lp.success:
        return {
            "classification": "REDUCED_PRIMAL_FLOAT_FAILED",
            "diagnostic": diagnostic,
        }

    reduced_parameters = reduced_lp.x / column_scales
    float_values = np.array(
        [
            float(affine_constants[row])
            + sum(
                float(affine_rows[row][column])
                * reduced_parameters[column]
                for column in range(len(free))
            )
            for row in range(len(affine_rows))
        ]
    )
    original_scales = np.array(
        [
            max(
                [abs(float(value)) for value in row]
                + [abs(float(affine_constants[index])), 1.0]
            )
            for index, row in enumerate(affine_rows)
        ]
    )
    parameter_candidates = [
        [
            Q(float(value)).limit_denominator(10**12)
            for value in reduced_parameters
        ]
    ]
    attempts = []
    for threshold in (1e-6, 1e-7, 1e-8, 1e-9, 1e-10, 1e-11):
        active = [
            index
            for index, value in enumerate(
                float_values / original_scales
            )
            if abs(value) <= threshold
        ]
        if not active:
            continue
        active_augmented = [
            affine_rows[index][:] + [-affine_constants[index]]
            for index in active
        ]
        active_matrix = fmpq_mat(
            len(active_augmented),
            len(free) + 1,
            [
                fq(value)
                for row in active_augmented
                for value in row
            ],
        )
        active_rref, active_rank = active_matrix.rref()
        active_pivots = []
        inconsistent = False
        for row in range(active_rank):
            pivot = next(
                column
                for column in range(len(free) + 1)
                if active_rref[row, column]
            )
            if pivot == len(free):
                inconsistent = True
                break
            active_pivots.append(pivot)
        if inconsistent:
            attempts.append(
                {
                    "threshold": threshold,
                    "active": len(active),
                    "outcome": "active_system_inconsistent",
                }
            )
            continue
        active_free = [
            column
            for column in range(len(free))
            if column not in active_pivots
        ]
        parameters = [
            Q(float(value)).limit_denominator(10**12)
            for value in reduced_parameters
        ]
        for row, pivot in enumerate(active_pivots):
            parameters[pivot] = Q(
                int(active_rref[row, len(free)].numerator),
                int(active_rref[row, len(free)].denominator),
            ) - sum(
                Q(
                    int(active_rref[row, column].numerator),
                    int(active_rref[row, column].denominator),
                )
                * parameters[column]
                for column in active_free
            )
        parameter_candidates.append(parameters)
        attempts.append(
            {
                "threshold": threshold,
                "active": len(active),
                "active_rank": active_rank,
                "outcome": "projected",
            }
        )

    for parameters in parameter_candidates:
        candidate = [
            particular[row]
            + sum(
                directions[row][column] * parameters[column]
                for column in range(len(free))
            )
            for row in range(variables)
        ]
        failed_equalities = [
            constraint["label"]
            for constraint in equalities
            if sum(
                value * candidate[index]
                for index, value in enumerate(constraint["row"])
            )
            != constraint["right"]
        ]
        failed_inequalities = [
            constraint["label"]
            for constraint in inequalities
            if sum(
                value * candidate[index]
                for index, value in enumerate(constraint["row"])
            )
            < 0
        ]
        if failed_equalities or failed_inequalities:
            continue
        tight = [
            constraint["label"]
            for constraint in inequalities
            if sum(
                value * candidate[index]
                for index, value in enumerate(constraint["row"])
            )
            == 0
        ]
        return {
            "format": "wave127-exact-rational-candidate-v1",
            "classification": "EXACT_RATIONAL_FEASIBLE",
            "diagnostic": diagnostic,
            "attempts": attempts,
            "failed_equalities": [],
            "failed_inequalities": [],
            "tight_inequalities": tight,
            "solution": [qtext(value) for value in candidate],
        }
    return {
        "classification": "EXACT_PRIMAL_RECOVERY_FAILED",
        "diagnostic": diagnostic,
        "attempts": attempts,
    }


def recover_exact_farkas_reduced(
    equalities: list[dict[str, object]],
    inequalities: list[dict[str, object]],
    variables: int,
) -> dict[str, object]:
    """Eliminate the Farkas equalities exactly, leaving a small rational LP."""

    import numpy as np
    from flint import fmpq, fmpq_mat
    from scipy.optimize import linprog

    solver_equalities, solver_inequalities, reduction = (
        reduced_constraints_for_solver(equalities, inequalities)
    )

    def fq(value: Q):
        return fmpq(value.numerator, value.denominator)

    constraints = solver_equalities + solver_inequalities
    equality_count = len(solver_equalities)
    multiplier_count = len(constraints)
    equation_count = variables + 1
    augmented = fmpq_mat(
        equation_count,
        multiplier_count + 1,
        [
            fq(
                (
                    constraint["row"][row]
                    if row < variables
                    else (
                        constraint["right"]
                        if column < equality_count
                        else Q(0)
                    )
                )
                if column < multiplier_count
                else Q(int(row == variables))
            )
            for row in range(equation_count)
            for column, constraint in enumerate(
                constraints + [constraints[0]]
            )
        ],
    )
    echelon, exact_rank = augmented.rref()
    pivots = []
    inconsistent = False
    for row in range(exact_rank):
        pivot = next(
            column
            for column in range(multiplier_count + 1)
            if echelon[row, column]
        )
        if pivot == multiplier_count:
            inconsistent = True
            break
        pivots.append(pivot)
    if inconsistent:
        return {
            "classification": "EXACT_DUAL_AFFINE_SYSTEM_INCONSISTENT",
            "exact_reduction": reduction,
        }
    free = [
        column
        for column in range(multiplier_count)
        if column not in pivots
    ]
    if len(pivots) != exact_rank:
        raise AssertionError("unexpected RREF pivot")

    particular = [Q(0)] * multiplier_count
    directions = [
        [Q(0)] * len(free) for _ in range(multiplier_count)
    ]
    for index, free_column in enumerate(free):
        directions[free_column][index] = Q(1)
    for row, pivot in enumerate(pivots):
        particular[pivot] = Q(
            int(echelon[row, multiplier_count].numerator),
            int(echelon[row, multiplier_count].denominator),
        )
        for index, free_column in enumerate(free):
            directions[pivot][index] = -Q(
                int(echelon[row, free_column].numerator),
                int(echelon[row, free_column].denominator),
            )

    z_indices = range(equality_count, multiplier_count)
    nz_exact = [directions[index] for index in z_indices]
    z0_exact = [particular[index] for index in z_indices]
    column_scales = np.ones(len(free))
    row_scales = np.ones(len(solver_inequalities))
    for _ in range(12):
        for column in range(len(free)):
            values = [
                abs(float(row[column]))
                / (row_scales[index] * column_scales[column])
                for index, row in enumerate(nz_exact)
                if row[column]
            ]
            if values:
                column_scales[column] *= math.sqrt(
                    min(values) * max(values)
                )
        for index, (row, constant) in enumerate(
            zip(nz_exact, z0_exact, strict=True)
        ):
            values = [
                abs(float(value))
                / (column_scales[column] * row_scales[index])
                for column, value in enumerate(row)
                if value
            ]
            if constant:
                values.append(
                    abs(float(constant)) / row_scales[index]
                )
            if values:
                row_scales[index] *= math.sqrt(
                    min(values) * max(values)
                )
    nz = np.array(
        [
            [
                float(value)
                / (row_scales[row] * column_scales[column])
                for column, value in enumerate(source)
            ]
            for row, source in enumerate(nz_exact)
        ]
    )
    z0 = np.array(
        [
            float(value) / row_scales[index]
            for index, value in enumerate(z0_exact)
        ]
    )
    nonzero_reduced = np.abs(nz[np.nonzero(nz)])
    reduced_lp = linprog(
        np.zeros(len(free)),
        A_ub=-nz,
        b_ub=z0,
        bounds=[(None, None)] * len(free),
        method="highs",
        options={
            "dual_feasibility_tolerance": 1e-9,
            "primal_feasibility_tolerance": 1e-9,
        },
    )
    diagnostic = {
        "exact_reduction": reduction,
        "dual_multiplier_variables": multiplier_count,
        "dual_affine_rank": exact_rank,
        "dual_free_dimension": len(free),
        "reduced_float_success": bool(reduced_lp.success),
        "reduced_float_status": int(reduced_lp.status),
        "reduced_float_message": str(reduced_lp.message),
        "reduced_balanced_min_nonzero": float(
            np.min(nonzero_reduced)
        ),
        "reduced_balanced_max": float(np.max(np.abs(nz))),
    }
    if not reduced_lp.success:
        return {
            "classification": "REDUCED_DUAL_FLOAT_FAILED",
            "dual_diagnostic": diagnostic,
        }

    def exact_multipliers(parameters: list[Q]) -> list[Q]:
        return [
            particular[row]
            + sum(
                directions[row][column] * parameters[column]
                for column in range(len(free))
            )
            for row in range(multiplier_count)
        ]

    attempts = []
    reduced_parameters = reduced_lp.x / column_scales
    parameter_candidates = [
        [
            Q(float(value)).limit_denominator(10**12)
            for value in reduced_parameters
        ]
    ]
    float_z = np.array(
        [
            float(z0_exact[row])
            + sum(
                float(nz_exact[row][column])
                * reduced_parameters[column]
                for column in range(len(free))
            )
            for row in range(len(z0_exact))
        ]
    )
    original_scales = np.maximum(
        np.array(
            [
                max(
                    [abs(float(value)) for value in row]
                    + [abs(float(z0_exact[index])), 1.0]
                )
                for index, row in enumerate(nz_exact)
            ]
        ),
        1.0,
    )
    for threshold in (1e-6, 1e-7, 1e-8, 1e-9, 1e-10):
        active = [
            index
            for index, value in enumerate(float_z / original_scales)
            if abs(value) <= threshold
        ]
        if not active:
            continue
        active_augmented = [
            directions[equality_count + index][:]
            + [-particular[equality_count + index]]
            for index in active
        ]
        active_matrix = fmpq_mat(
            len(active_augmented),
            len(free) + 1,
            [
                fq(value)
                for row in active_augmented
                for value in row
            ],
        )
        active_rref, active_rank = active_matrix.rref()
        active_pivots = []
        active_inconsistent = False
        for row in range(active_rank):
            pivot = next(
                column
                for column in range(len(free) + 1)
                if active_rref[row, column]
            )
            if pivot == len(free):
                active_inconsistent = True
                break
            active_pivots.append(pivot)
        if active_inconsistent:
            attempts.append(
                {
                    "threshold": threshold,
                    "active": len(active),
                    "outcome": "active_system_inconsistent",
                }
            )
            continue
        active_free = [
            column
            for column in range(len(free))
            if column not in active_pivots
        ]
        parameters = [
            Q(float(value)).limit_denominator(10**12)
            for value in reduced_parameters
        ]
        for row, pivot in enumerate(active_pivots):
            parameters[pivot] = Q(
                int(active_rref[row, len(free)].numerator),
                int(active_rref[row, len(free)].denominator),
            ) - sum(
                Q(
                    int(active_rref[row, column].numerator),
                    int(active_rref[row, column].denominator),
                )
                * parameters[column]
                for column in active_free
            )
        parameter_candidates.append(parameters)
        attempts.append(
            {
                "threshold": threshold,
                "active": len(active),
                "active_rank": active_rank,
                "outcome": "projected",
            }
        )

    for parameters in parameter_candidates:
        multipliers = exact_multipliers(parameters)
        if any(
            multipliers[index] < 0 for index in z_indices
        ):
            continue
        identities = []
        for row in range(equation_count):
            identities.append(
                sum(
                    (
                        constraints[column]["row"][row]
                        if row < variables
                        else (
                            constraints[column]["right"]
                            if column < equality_count
                            else Q(0)
                        )
                    )
                    * multipliers[column]
                    for column in range(multiplier_count)
                )
            )
        if any(identities[:variables]) or identities[-1] != 1:
            continue
        entries = [
            {
                "kind": (
                    "equality"
                    if index < equality_count
                    else "inequality"
                ),
                "label": constraints[index]["label"],
                "multiplier": qtext(multiplier),
            }
            for index, multiplier in enumerate(multipliers)
            if multiplier
        ]
        return {
            "format": "wave127-exact-farkas-v1",
            "classification": "EXACT_FARKAS_VERIFIED",
            "convention": (
                "sum y_i*Aeq_i + sum z_j*G_j = 0, "
                "z_j >= 0, sum y_i*b_i = 1"
            ),
            "dual_diagnostic": diagnostic,
            "attempts": attempts,
            "entries": entries,
            "identity": {
                "variable_coordinates_all_zero": True,
                "right_hand_side": "1",
                "inequality_multipliers_nonnegative": True,
            },
        }
    return {
        "classification": "EXACT_FARKAS_RECOVERY_FAILED",
        "dual_diagnostic": diagnostic,
        "attempts": attempts,
    }


def recover_exact_farkas(
    equalities: list[dict[str, object]],
    inequalities: list[dict[str, object]],
    variables: int,
) -> dict[str, object]:
    return recover_exact_farkas_reduced(
        equalities, inequalities, variables
    )


def build_model(
    cutoff: int,
    run_float: bool = False,
    exact_candidate_path: Path | None = None,
    exact_farkas_path: Path | None = None,
    columns_cache_path: Path | None = None,
) -> dict[str, object]:
    qmax = max(cutoff, 10)
    cached = None
    if columns_cache_path is not None and columns_cache_path.exists():
        with columns_cache_path.open("rb") as stream:
            candidate_cache = pickle.load(stream)
        if (
            candidate_cache.get("version") == MODEL_CACHE_VERSION
            and candidate_cache.get("qmax") == qmax
        ):
            cached = candidate_cache
    if cached is None:
        columns, module = build_columns(qmax)
        if columns_cache_path is not None:
            with columns_cache_path.open("wb") as stream:
                pickle.dump(
                    {
                        "version": MODEL_CACHE_VERSION,
                        "qmax": qmax,
                        "columns": columns,
                        "module": module,
                    },
                    stream,
                    protocol=pickle.HIGHEST_PROTOCOL,
                )
    else:
        columns = cached["columns"]
        module = cached["module"]
    equalities, inequalities = build_constraints(columns, cutoff)
    result = {
        "format": "wave127-exact-jacobi-lp-v1",
        "cutoff": cutoff,
        "module": module,
        "fricke": {
            "L_coefficient_weight_c": "22+2c",
            "K_from_L_block": "h_c=-7^(-3-c)*(f_c|W_7)",
            "general_exponent": "qdisc/2-11-c=-3-c",
            "K_Jacobi_factor": "A(7tau,7z)^c B(7tau,7z)^(10-c)",
        },
        "constraints": {
            "variables": len(columns),
            "equalities": len(equalities),
            "inequalities": len(inequalities),
            "equality_labels": [constraint["label"] for constraint in equalities],
            "inequality_labels": [constraint["label"] for constraint in inequalities],
        },
        "status": {
            "exact_feasibility": "UNKNOWN",
            "exact_Farkas_certificate": None,
            "rank28_excluded": False,
            "Conway_99": "UNKNOWN",
        },
    }
    if run_float:
        result["floating_diagnostic"] = float_feasibility(
            equalities, inequalities, len(columns)
        )
    if exact_candidate_path is not None:
        candidate = recover_exact_primal_reduced(
            equalities, inequalities, len(columns)
        )
        exact_candidate_path.write_text(
            canonical_json(candidate), encoding="utf-8", newline="\n"
        )
        result["exact_candidate"] = {
            "path": str(exact_candidate_path),
            "classification": candidate["classification"],
        }
        if candidate["classification"] == "EXACT_RATIONAL_FEASIBLE":
            result["status"]["exact_feasibility"] = "FEASIBLE_AT_FINITE_CUTOFF"
    if exact_farkas_path is not None:
        farkas = recover_exact_farkas(
            equalities, inequalities, len(columns)
        )
        exact_farkas_path.write_text(
            canonical_json(farkas), encoding="utf-8", newline="\n"
        )
        result["exact_farkas"] = {
            "path": str(exact_farkas_path),
            "classification": farkas["classification"],
        }
        if farkas["classification"] == "EXACT_FARKAS_VERIFIED":
            result["status"]["exact_feasibility"] = "INFEASIBLE_AT_FINITE_CUTOFF"
            result["status"]["exact_Farkas_certificate"] = str(
                exact_farkas_path
            )
    return result


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", type=int, default=12)
    parser.add_argument("--float", action="store_true")
    parser.add_argument("--exact-candidate", type=Path)
    parser.add_argument("--exact-farkas", type=Path)
    parser.add_argument("--columns-cache", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if free_memory_percent() < 15:
        raise SystemExit("free memory below 15%")
    result = build_model(
        args.cutoff,
        args.float,
        args.exact_candidate,
        args.exact_farkas,
        args.columns_cache,
    )
    payload = canonical_json(result)
    if args.write:
        args.write.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
