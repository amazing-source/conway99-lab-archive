"""Exact exploratory level-7 modular-form calculations for Wave 86.

Discovery only. Conditional on the verified Wave 66/71 lattice transfer.
"""

from __future__ import annotations

import argparse
import json
import os
from fractions import Fraction
from math import comb
from pathlib import Path


Q = Fraction
PRECISION = 50
STURM = 14
CHI7 = (0, 1, 1, -1, 1, -1, -1)
DEFAULT_OUTPUT = Path(__file__).with_name("exact-results.json")


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0
    import ctypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.ullAvailPhys / status.ullTotalPhys


def chi7(n: int) -> int:
    return 0 if n % 7 == 0 else CHI7[n % 7]


def bernoulli_numbers(nmax: int) -> list[Q]:
    values = [Q(0)] * (nmax + 1)
    values[0] = Q(1)
    if nmax:
        values[1] = Q(-1, 2)
    for n in range(2, nmax + 1):
        values[n] = -sum(Q(comb(n + 1, j)) * values[j] for j in range(n)) / Q(n + 1)
    return values


BERNOULLI = bernoulli_numbers(30)


def bernoulli_polynomial(k: int, x: Q) -> Q:
    return sum(Q(comb(k, j)) * BERNOULLI[j] * x ** (k - j) for j in range(k + 1))


def generalized_bernoulli(k: int) -> Q:
    return Q(7 ** (k - 1)) * sum(
        Q(chi7(a)) * bernoulli_polynomial(k, Q(a, 7)) for a in range(1, 8)
    )


def eisenstein(k: int, orientation: str) -> list[Q]:
    """Return E_k(chi,1) for A and E_k(1,chi) for B."""

    result = [Q(0)] * (PRECISION + 1)
    if orientation == "A":
        result[0] = -generalized_bernoulli(k) / Q(2 * k)
    for n in range(1, PRECISION + 1):
        result[n] = sum(
            Q(chi7(d) if orientation == "A" else chi7(n // d)) * d ** (k - 1)
            for d in range(1, n + 1)
            if n % d == 0
        )
    return result


def multiply(left: list[Q], right: list[Q]) -> list[Q]:
    return [
        sum(left[j] * right[n - j] for j in range(n + 1))
        for n in range(PRECISION + 1)
    ]


SERIES = {
    (k, orientation): eisenstein(k, orientation)
    for k in range(3, 20, 2)
    for orientation in "AB"
}


Form = tuple[int, str, int, str]


def product_series(form: Form) -> list[Q]:
    a, oa, b, ob = form
    return multiply(SERIES[a, oa], SERIES[b, ob])


def candidate_products() -> list[Form]:
    forms = []
    for a in range(3, 12, 2):
        b = 22 - a
        for oa in "AB":
            for ob in "AB":
                if a == b and oa > ob:
                    continue
                forms.append((a, oa, b, ob))
    return forms


def independent_basis() -> list[Form]:
    echelon: list[tuple[int, list[Q]]] = []
    basis = []
    for form in candidate_products():
        row = product_series(form)[: STURM + 1]
        for pivot, existing in echelon:
            if row[pivot]:
                scale = row[pivot] / existing[pivot]
                row = [x - scale * y for x, y in zip(row, existing)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            echelon.append((pivot, row))
            basis.append(form)
    return basis


def invert(matrix: list[list[Q]]) -> list[list[Q]]:
    n = len(matrix)
    work = [
        row[:] + [Q(i == j) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next(row for row in range(column, n) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [x / scale for x in work[column]]
        for row in range(n):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                x - scale * y for x, y in zip(work[row], work[column])
            ]
    return [row[n:] for row in work]


def matmul(left: list[list[Q]], right: list[list[Q]]) -> list[list[Q]]:
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def fricke_image(form: Form) -> tuple[Q, Form]:
    """Use the normalized-Eisenstein Fricke exchange.

    For chi=chi_{-7}, g(chi)=i*sqrt(7).  In the normalization used by the
    q-series above,

      A_k=E_k(chi,1) -> -i*7^((k-1)/2) B_k,
      B_k=E_k(1,chi) -> -i*7^((1-k)/2) A_k.

    The two imaginary factors cancel in a weight-22 product.
    """

    a, oa, b, ob = form
    mapped = (
        a,
        "B" if oa == "A" else "A",
        b,
        "B" if ob == "A" else "A",
    )
    sign = -1
    numerator = (a - 1 if oa == "A" else 1 - a) + (
        b - 1 if ob == "A" else 1 - b
    )
    assert numerator % 2 == 0
    exponent = numerator // 2
    factor = Q(sign * 7**exponent) if exponent >= 0 else Q(sign, 7 ** (-exponent))
    return factor, mapped


def fricke_matrix() -> tuple[list[Form], list[list[Q]]]:
    basis = independent_basis()
    assert len(basis) == 15
    coefficient_matrix = [
        [product_series(form)[n] for form in basis]
        for n in range(STURM + 1)
    ]
    inverse = invert(coefficient_matrix)
    image_matrix = []
    for n in range(STURM + 1):
        row = []
        for form in basis:
            factor, image = fricke_image(form)
            row.append(factor * product_series(image)[n])
        image_matrix.append(row)
    return basis, matmul(image_matrix, inverse)


def fraction_text(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def q16_affine_pair(
    fricke: list[list[Q]],
) -> tuple[list[Q], list[list[Q]], Q, list[Q]]:
    """Eliminate x_14 using y_0=1.

    The remaining variables are x_7,...,x_13 and
    y=-7^3(Theta_K|W_7).
    """

    raw_constant = [-Q(7**3) * fricke[n][0] for n in range(15)]
    raw_matrix = [
        [-Q(7**3) * fricke[n][j] for j in range(7, 15)]
        for n in range(15)
    ]
    pivot = raw_matrix[0][7]
    assert pivot
    x14_constant = (Q(1) - raw_constant[0]) / pivot
    x14_coefficients = [-raw_matrix[0][j] / pivot for j in range(7)]
    constants = [
        raw_constant[n] + raw_matrix[n][7] * x14_constant
        for n in range(15)
    ]
    matrix = [
        [
            raw_matrix[n][j] + raw_matrix[n][7] * x14_coefficients[j]
            for j in range(7)
        ]
        for n in range(15)
    ]
    assert constants[0] == 1 and not any(matrix[0])
    return constants, matrix, x14_constant, x14_coefficients


def exact_result() -> dict:
    basis, fricke = fricke_matrix()
    assert len(basis) == 15
    square = matmul(fricke, fricke)
    assert all(
        square[i][j] == Q(i == j)
        for i in range(15)
        for j in range(15)
    )

    constants, affine, x14_constant, x14_coefficients = q16_affine_pair(fricke)
    # In variables z=(x7,...,x13), the exact dual certificate is
    #
    # S-B = l8*x8+l9*x9+l11*x11+l1*y1+...+l4*y4.
    bound = Q(1997236, 341)
    multipliers = {
        "x8": Q(180, 217),
        "x9": Q(2344, 2387),
        "x11": Q(1, 2387),
        "y1": Q(1118523, 341),
        "y2": Q(134113, 341),
        "y3": Q(9604, 341),
        "y4": Q(343, 341),
    }
    rhs_constant = (
        multipliers["y1"] * constants[1]
        + multipliers["y2"] * constants[2]
        + multipliers["y3"] * constants[3]
        + multipliers["y4"] * constants[4]
    )
    assert rhs_constant == -bound
    target = [Q(1), Q(1), Q(1), Q(0), Q(0), Q(0), Q(0)]
    rhs_linear = [Q(0)] * 7
    rhs_linear[1] += multipliers["x8"]
    rhs_linear[2] += multipliers["x9"]
    rhs_linear[4] += multipliers["x11"]
    for n in range(1, 5):
        for j in range(7):
            rhs_linear[j] += multipliers[f"y{n}"] * affine[n][j]
    assert rhs_linear == target

    # This exact formal modular pair attains the rounded scalar lower bound.
    # It is a modular-form feasibility control, not a lattice realization.
    extremal_x = [
        Q(1),
        *([Q(0)] * 6),
        Q(5868),
        Q(0),
        Q(0),
        Q(28852082),
        Q(26264),
        Q(582557668),
        Q(2681235704),
        Q(12272379984),
    ]
    extremal_y = [
        sum(-Q(7**3) * fricke[n][j] * extremal_x[j] for j in range(15))
        for n in range(15)
    ]
    assert extremal_y == [
        Q(1),
        Q(0),
        Q(0),
        Q(0),
        Q(0),
        Q(358916),
        Q(34393854),
        Q(600737200),
        Q(11946196274),
        Q(132636715536),
        Q(1237054839912),
        Q(9122211909000),
        Q(56682577580992),
        Q(304577760235536),
        Q(1443860798777424),
    ]
    assert all(value.denominator == 1 and value >= 0 for value in extremal_x)
    assert all(value.denominator == 1 and value >= 0 for value in extremal_y)
    assert all(value % 2 == 0 for value in extremal_x[1:])
    assert all(value % 2 == 0 for value in extremal_y[1:])
    assert extremal_x[7] + extremal_x[8] + extremal_x[9] == 5868
    assert 5868 % 14 == 2
    assert Q(5854) < bound < Q(5868)

    # Reconstruct the unique modular pair and inspect a longer prefix as a
    # hostile control against a first-15-coefficient transcription accident.
    coefficient_matrix = [
        [product_series(form)[n] for form in basis]
        for n in range(15)
    ]
    inverse = invert(coefficient_matrix)
    coordinates = [
        sum(inverse[i][j] * extremal_x[j] for j in range(15))
        for i in range(15)
    ]
    long_x = [
        sum(coordinates[i] * product_series(basis[i])[n] for i in range(15))
        for n in range(PRECISION + 1)
    ]
    long_y = []
    for n in range(PRECISION + 1):
        transformed = sum(
            coordinates[i]
            * fricke_image(basis[i])[0]
            * product_series(fricke_image(basis[i])[1])[n]
            for i in range(15)
        )
        long_y.append(-Q(7**3) * transformed)
    assert long_x[:15] == extremal_x
    assert long_y[:15] == extremal_y
    assert all(value.denominator == 1 and value >= 0 for value in long_x)
    assert all(value.denominator == 1 and value >= 0 for value in long_y)
    assert all(value % 2 == 0 for value in long_x[1:])
    assert all(value % 2 == 0 for value in long_y[1:])

    return {
        "format": "wave86-level7-exact-v1",
        "claim_label": "DERIVED",
        "scope": "conditional q=16 row of a hypothetical srg(99,14,1,2)",
        "modular_space": {
            "space": "M_22(Gamma0(7)) with trivial character",
            "dimension": 15,
            "sturm_bound": 14,
            "basis_products": [list(form) for form in basis],
            "fricke_involution_exact": True,
            "fricke_matrix_max_denominator": max(
                value.denominator for row in fricke for value in row
            ),
        },
        "theta_transfer": {
            "normalization": "Theta=sum_x q^((x,x)/2)",
            "relation": "Theta_L=-7^3*(Theta_K|W_7)",
            "x_initial_gap": "x1=...=x6=0",
            "x14_elimination": {
                "constant": fraction_text(x14_constant),
                "coefficients_on_x7_to_x13": [
                    fraction_text(value) for value in x14_coefficients
                ],
            },
        },
        "coefficient_identity": {
            "left": "x7+x8+x9-1997236/341",
            "right_terms": {
                key: fraction_text(value) for key, value in multipliers.items()
            },
            "all_right_terms_nonnegative_for_theta_series": True,
            "rational_lower_bound": fraction_text(bound),
            "wave71_congruence": "x7+x8+x9=2 mod 14",
            "forced_integer_lower_bound": 5868,
        },
        "formal_scalar_control": {
            "not_a_lattice_or_graph": True,
            "x0_to_x14": [int(value) for value in extremal_x],
            "y0_to_y14": [int(value) for value in extremal_y],
            "attains_short_sum": 5868,
            "checked_through_q": PRECISION,
            "integral_even_nonnegative_through_checked_prefix": True,
        },
        "status": {
            "new_conditional_fact": "N14+N16+N18>=5868 in the q=16 row",
            "q16_excluded": False,
            "graph": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Conditional on the independently verified Wave66 and Wave71 lattice transfer.",
            "The exact formal modular pair is not a lattice or marked-frame realization.",
            "Scalar theta coefficients do not encode the classified signed supports.",
            "No q=16 exclusion or Conway-99 resolution follows in this package.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run with only {free:.1f}% free physical memory")
    result = exact_result()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != encoded:
            raise SystemExit("canonical exact-results.json mismatch")
        print(f"PASS: canonical result verified; free physical memory {free:.1f}%")
        return
    args.output.write_text(encoded, encoding="utf-8")
    print(f"wrote {args.output}; free physical memory {free:.1f}%")


if __name__ == "__main__":
    main()
