"""Independent exact verifier for the sealed Wave 86 discovery package.

This module never imports or executes discovery code.  It reconstructs the
weight-22 level-seven modular space, Fricke action, Poisson theta transfer,
positive coefficient certificate, and the finite scalar control over Q.
"""

from __future__ import annotations

import json
import math
import os
from fractions import Fraction
from pathlib import Path


QQ = Fraction
LEVEL = 7
WEIGHT = 22
STURM_BOUND = 14
CHECK_PRECISION = 50
CHI_MINUS_SEVEN = (0, 1, 1, -1, 1, -1, -1)
HERE = Path(__file__).resolve().parent
CANONICAL_RESULT = HERE / "independent-results.json"


def free_physical_memory_percent() -> float:
    if os.name != "nt":
        return 100.0
    import ctypes

    class MemoryStatus(ctypes.Structure):
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

    state = MemoryStatus()
    state.length = ctypes.sizeof(state)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * state.available_phys / state.total_phys


def chi(n: int) -> int:
    return CHI_MINUS_SEVEN[n % LEVEL]


def ordinary_bernoulli(up_to: int) -> list[QQ]:
    """Compute B_0,...,B_up_to from the defining triangular recurrence."""

    values = [QQ(0) for _ in range(up_to + 1)]
    values[0] = QQ(1)
    for m in range(1, up_to + 1):
        subtotal = sum(
            QQ(math.comb(m + 1, j)) * values[j] for j in range(m)
        )
        values[m] = -subtotal / QQ(m + 1)
    return values


BERNOULLI = ordinary_bernoulli(WEIGHT)


def bernoulli_polynomial_value(degree: int, x: QQ) -> QQ:
    return sum(
        QQ(math.comb(degree, j)) * BERNOULLI[j] * x ** (degree - j)
        for j in range(degree + 1)
    )


def generalized_bernoulli(degree: int) -> QQ:
    return QQ(LEVEL ** (degree - 1)) * sum(
        QQ(chi(a)) * bernoulli_polynomial_value(degree, QQ(a, LEVEL))
        for a in range(1, LEVEL + 1)
    )


def divisors(n: int) -> list[int]:
    small: list[int] = []
    large: list[int] = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            small.append(d)
            if d * d != n:
                large.append(n // d)
        d += 1
    return small + list(reversed(large))


def twisted_eisenstein(weight: int, side: str) -> list[QQ]:
    """q-expansion of E_k(chi,1) (side C) or E_k(1,chi) (side T).

    The letters intentionally differ from the discovery implementation.
    """

    if side not in {"C", "T"}:
        raise ValueError(side)
    coefficients = [QQ(0) for _ in range(CHECK_PRECISION + 1)]
    if side == "C":
        # L(chi,1-k)/2 = -B_{k,chi}/(2k).
        coefficients[0] = -generalized_bernoulli(weight) / QQ(2 * weight)
    for n in range(1, CHECK_PRECISION + 1):
        coefficients[n] = sum(
            QQ(chi(d) if side == "C" else chi(n // d)) * d ** (weight - 1)
            for d in divisors(n)
        )
    return coefficients


def convolve(left: list[QQ], right: list[QQ]) -> list[QQ]:
    return [
        sum(left[j] * right[n - j] for j in range(n + 1))
        for n in range(CHECK_PRECISION + 1)
    ]


EISENSTEIN = {
    (weight, side): twisted_eisenstein(weight, side)
    for weight in range(3, 20, 2)
    for side in ("C", "T")
}

Factor = tuple[int, str]
Product = tuple[Factor, Factor]


def product_qexp(product: Product) -> list[QQ]:
    return convolve(EISENSTEIN[product[0]], EISENSTEIN[product[1]])


def product_candidates() -> list[Product]:
    candidates: list[Product] = []
    for left_weight in range(3, 12, 2):
        right_weight = WEIGHT - left_weight
        for left_side in ("C", "T"):
            for right_side in ("C", "T"):
                if left_weight == right_weight and left_side > right_side:
                    continue
                candidates.append(
                    ((left_weight, left_side), (right_weight, right_side))
                )
    # A deliberately different ordering from discovery makes the chosen basis
    # and elimination path independent.
    return sorted(candidates, key=repr, reverse=True)


def matrix_rank(rows: list[list[QQ]]) -> int:
    work = [row[:] for row in rows]
    if not work:
        return 0
    row_count = len(work)
    column_count = len(work[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (r for r in range(pivot_row, row_count) if work[r][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for r in range(row_count):
            if r == pivot_row or not work[r][column]:
                continue
            scale = work[r][column]
            work[r] = [
                value - scale * pivot_value
                for value, pivot_value in zip(work[r], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def coefficient_rows(products: list[Product], stop: int = STURM_BOUND) -> list[list[QQ]]:
    return [
        [product_qexp(product)[n] for product in products]
        for n in range(stop + 1)
    ]


def select_full_basis() -> list[Product]:
    selected: list[Product] = []
    rank = 0
    for product in product_candidates():
        trial = selected + [product]
        trial_rank = matrix_rank(coefficient_rows(trial))
        if trial_rank > rank:
            selected = trial
            rank = trial_rank
        if rank == 15:
            break
    if rank != 15:
        raise AssertionError(f"product span has rank {rank}, expected 15")
    return selected


def inverse(matrix: list[list[QQ]]) -> list[list[QQ]]:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("inverse requires a nonempty square matrix")
    augmented = [
        row[:] + [QQ(r == c) for c in range(size)]
        for r, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (r for r in range(column, size) if augmented[r][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for r in range(size):
            if r == column:
                continue
            multiplier = augmented[r][column]
            if multiplier:
                augmented[r] = [
                    value - multiplier * pivot_value
                    for value, pivot_value in zip(
                        augmented[r], augmented[column]
                    )
                ]
    return [row[size:] for row in augmented]


def matrix_product(left: list[list[QQ]], right: list[list[QQ]]) -> list[list[QQ]]:
    return [
        [
            sum(left[r][k] * right[k][c] for k in range(len(right)))
            for c in range(len(right[0]))
        ]
        for r in range(len(left))
    ]


def matrix_vector(matrix: list[list[QQ]], vector: list[QQ]) -> list[QQ]:
    return [
        sum(value * vector[c] for c, value in enumerate(row))
        for row in matrix
    ]


def solve(square: list[list[QQ]], right: list[QQ]) -> list[QQ]:
    return matrix_vector(inverse(square), right)


def single_fricke_multiplier(weight: int, side: str) -> tuple[str, QQ]:
    """Return the common phase label and rational 7-power.

    With tau(chi_{-7})=i*sqrt(7), both orientations carry phase -i:

      E_k(chi,1)|W_7 = -i 7^((k-1)/2) E_k(1,chi)
      E_k(1,chi)|W_7 = -i 7^((1-k)/2) E_k(chi,1).

    We keep -i symbolic; products of two factors have phase (-i)^2=-1.
    """

    exponent = (weight - 1) // 2 if side == "C" else (1 - weight) // 2
    power = QQ(LEVEL**exponent) if exponent >= 0 else QQ(1, LEVEL ** (-exponent))
    return "-i", power


def product_fricke(product: Product, omit_gauss_phase: bool = False) -> tuple[QQ, Product]:
    mapped: list[Factor] = []
    power = QQ(1)
    for weight, side in product:
        _, contribution = single_fricke_multiplier(weight, side)
        power *= contribution
        mapped.append((weight, "T" if side == "C" else "C"))
    phase_product = QQ(1) if omit_gauss_phase else QQ(-1)
    return phase_product * power, (mapped[0], mapped[1])


def fricke_prefix_operator(
    basis: list[Product], omit_gauss_phase: bool = False
) -> list[list[QQ]]:
    coordinates_to_prefix = coefficient_rows(basis)
    prefix_to_coordinates = inverse(coordinates_to_prefix)
    transformed_prefix = []
    for n in range(STURM_BOUND + 1):
        row: list[QQ] = []
        for product in basis:
            factor, image = product_fricke(product, omit_gauss_phase)
            row.append(factor * product_qexp(image)[n])
        transformed_prefix.append(row)
    return matrix_product(transformed_prefix, prefix_to_coordinates)


def modular_space_invariants() -> dict:
    index = LEVEL + 1
    cusps = 2
    elliptic_two = 0
    elliptic_three = 2
    genus = (
        QQ(1)
        + QQ(index, 12)
        - QQ(elliptic_two, 4)
        - QQ(elliptic_three, 3)
        - QQ(cusps, 2)
    )
    cusp_dimension = (
        (WEIGHT - 1) * (genus - 1)
        + (QQ(WEIGHT, 2) - 1) * cusps
        + (WEIGHT // 4) * elliptic_two
        + (WEIGHT // 3) * elliptic_three
    )
    dimension = cusp_dimension + cusps
    sturm = (WEIGHT * index) // 12
    return {
        "index": index,
        "cusps": cusps,
        "elliptic_order_2": elliptic_two,
        "elliptic_order_3": elliptic_three,
        "genus": int(genus),
        "cusp_dimension": int(cusp_dimension),
        "eisenstein_dimension": cusps,
        "dimension": int(dimension),
        "sturm_bound": sturm,
    }


def theta_transfer_constant() -> QQ:
    """Poisson transfer for rank 44, det(L)=7^16.

    Standard determinant-normalized W_7 contributes
    7^(weight/2) * i^(-weight) / sqrt(det(L)).
    """

    level_power = LEVEL ** (WEIGHT // 2)
    square_root_determinant = LEVEL**8
    phase_i_minus_weight = -1  # i^(-22)
    return QQ(phase_i_minus_weight * level_power, square_root_determinant)


def affine_theta_pair(
    fricke: list[list[QQ]],
) -> tuple[list[QQ], list[list[QQ]], QQ, list[QQ]]:
    """Impose x0=1, x1=...=x6=0 and y0=1, eliminating x14.

    Remaining variables are z=(x7,...,x13), and
    y=theta_transfer_constant() * (Theta_K | W_7).
    """

    transfer = theta_transfer_constant()
    raw_constants = [transfer * fricke[n][0] for n in range(15)]
    raw_rows = [
        [transfer * fricke[n][j] for j in range(7, 15)]
        for n in range(15)
    ]
    pivot = raw_rows[0][7]
    if not pivot:
        raise AssertionError("x14 does not control the y0 equation")
    x14_constant = (QQ(1) - raw_constants[0]) / pivot
    x14_linear = [-raw_rows[0][j] / pivot for j in range(7)]
    constants = [
        raw_constants[n] + raw_rows[n][7] * x14_constant for n in range(15)
    ]
    rows = [
        [
            raw_rows[n][j] + raw_rows[n][7] * x14_linear[j]
            for j in range(7)
        ]
        for n in range(15)
    ]
    if constants[0] != 1 or any(rows[0]):
        raise AssertionError("y0 elimination failed")
    return constants, rows, x14_constant, x14_linear


def derive_positive_identity(
    constants: list[QQ], affine_rows: list[list[QQ]]
) -> tuple[QQ, dict[str, QQ]]:
    """Derive, rather than import, the seven-multiplier certificate."""

    unit_rows = [[QQ(r == c) for c in range(7)] for r in range(7)]
    labels = ("x8", "x9", "x11", "y1", "y2", "y3", "y4")
    forms = (
        unit_rows[1],
        unit_rows[2],
        unit_rows[4],
        affine_rows[1],
        affine_rows[2],
        affine_rows[3],
        affine_rows[4],
    )
    columns = [[forms[c][r] for c in range(7)] for r in range(7)]
    target = [QQ(1), QQ(1), QQ(1), QQ(0), QQ(0), QQ(0), QQ(0)]
    values = solve(columns, target)
    multipliers = dict(zip(labels, values))
    rhs_constant = sum(
        multipliers[f"y{n}"] * constants[n] for n in range(1, 5)
    )
    bound = -rhs_constant
    return bound, multipliers


def derive_scalar_equality_control(
    basis: list[Product],
    fricke: list[list[QQ]],
    constants: list[QQ],
    affine_rows: list[list[QQ]],
    x14_constant: QQ,
    x14_linear: list[QQ],
) -> tuple[list[QQ], list[QQ], list[QQ], list[QQ]]:
    """Derive the first congruence-compatible scalar control and continue to q50.

    Impose x7=5868, x8=x9=0 and y1=...=y4=0.  These seven exact
    conditions determine the remaining Sturm variables.  This does not attain
    equality in the rational inequality: its positive x11 term supplies the
    necessary slack.
    """

    unit_rows = [[QQ(r == c) for c in range(7)] for r in range(7)]
    constraint_rows = [
        unit_rows[0],
        unit_rows[1],
        unit_rows[2],
        affine_rows[1],
        affine_rows[2],
        affine_rows[3],
        affine_rows[4],
    ]
    constraint_constants = [
        -QQ(5868),
        QQ(0),
        QQ(0),
        constants[1],
        constants[2],
        constants[3],
        constants[4],
    ]
    z = solve(constraint_rows, [-value for value in constraint_constants])
    x14 = x14_constant + sum(
        coefficient * value for coefficient, value in zip(x14_linear, z)
    )
    x_prefix = [QQ(1), *([QQ(0)] * 6), *z, x14]
    y_prefix = [
        theta_transfer_constant()
        * sum(fricke[n][j] * x_prefix[j] for j in range(15))
        for n in range(15)
    ]

    prefix_matrix = coefficient_rows(basis)
    modular_coordinates = solve(prefix_matrix, x_prefix)
    long_x = [
        sum(
            modular_coordinates[j] * product_qexp(basis[j])[n]
            for j in range(15)
        )
        for n in range(CHECK_PRECISION + 1)
    ]
    long_y: list[QQ] = []
    for n in range(CHECK_PRECISION + 1):
        transformed = QQ(0)
        for j, product in enumerate(basis):
            factor, image = product_fricke(product)
            transformed += (
                modular_coordinates[j] * factor * product_qexp(image)[n]
            )
        long_y.append(theta_transfer_constant() * transformed)
    return x_prefix, y_prefix, long_x, long_y


def format_fraction(value: QQ) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def first_congruent_integer_at_least(bound: QQ, residue: int, modulus: int) -> int:
    candidate = (bound.numerator + bound.denominator - 1) // bound.denominator
    return candidate + ((residue - candidate) % modulus)


def verify_exact() -> dict:
    space = modular_space_invariants()
    if space["dimension"] != 15 or space["sturm_bound"] != STURM_BOUND:
        raise AssertionError(space)

    basis = select_full_basis()
    basis_rank = matrix_rank(coefficient_rows(basis))
    truncated_rank = matrix_rank(coefficient_rows(basis[:-1]))
    if basis_rank != 15 or truncated_rank != 14:
        raise AssertionError((basis_rank, truncated_rank))

    fricke = fricke_prefix_operator(basis)
    fricke_square = matrix_product(fricke, fricke)
    identity = [
        [QQ(r == c) for c in range(15)]
        for r in range(15)
    ]
    if fricke_square != identity:
        raise AssertionError("Fricke operator is not an involution")

    # Exact individual and product phase checks.
    phase_c3, power_c3 = single_fricke_multiplier(3, "C")
    phase_t3, power_t3 = single_fricke_multiplier(3, "T")
    if (phase_c3, power_c3, phase_t3, power_t3) != (
        "-i",
        QQ(7),
        "-i",
        QQ(1, 7),
    ):
        raise AssertionError("Gauss phase or 7-power normalization failed")
    sample_factor, _ = product_fricke(((3, "C"), (19, "C")))
    wrong_phase_factor, _ = product_fricke(
        ((3, "C"), (19, "C")), omit_gauss_phase=True
    )
    if sample_factor != -QQ(7**10) or wrong_phase_factor != QQ(7**10):
        raise AssertionError("hostile Gauss-phase control failed")

    transfer = theta_transfer_constant()
    if transfer != -QQ(7**3):
        raise AssertionError(transfer)
    constants, affine, x14_constant, x14_linear = affine_theta_pair(fricke)
    bound, multipliers = derive_positive_identity(constants, affine)
    if not all(value > 0 for value in multipliers.values()):
        raise AssertionError("certificate is not coefficientwise positive")

    target = [QQ(1), QQ(1), QQ(1), QQ(0), QQ(0), QQ(0), QQ(0)]
    reconstructed = [QQ(0) for _ in range(7)]
    reconstructed[1] += multipliers["x8"]
    reconstructed[2] += multipliers["x9"]
    reconstructed[4] += multipliers["x11"]
    for n in range(1, 5):
        for j in range(7):
            reconstructed[j] += multipliers[f"y{n}"] * affine[n][j]
    if reconstructed != target:
        raise AssertionError("positive identity linear part failed")
    if (
        sum(multipliers[f"y{n}"] * constants[n] for n in range(1, 5))
        != -bound
    ):
        raise AssertionError("positive identity constant failed")

    forced = first_congruent_integer_at_least(bound, 2, 14)
    if forced != 5868 or not (QQ(5854) < bound < QQ(5868)):
        raise AssertionError((bound, forced))

    x_prefix, y_prefix, long_x, long_y = derive_scalar_equality_control(
        basis,
        fricke,
        constants,
        affine,
        x14_constant,
        x14_linear,
    )
    if x_prefix[7] + x_prefix[8] + x_prefix[9] != forced:
        raise AssertionError("scalar congruence-boundary control misses 5868")
    if long_x[:15] != x_prefix or long_y[:15] != y_prefix:
        raise AssertionError("long continuation does not reproduce Sturm prefix")
    for name, series in (("K", long_x), ("L", long_y)):
        if not all(value.denominator == 1 and value >= 0 for value in series):
            raise AssertionError(f"{name} scalar control is not integral/nonnegative")
        if not all(value.numerator % 2 == 0 for value in series[1:]):
            raise AssertionError(f"{name} scalar control has an odd nonconstant term")

    # Hostile transfer controls use the already-derived correct modular prefix.
    wrong_sign_y0 = QQ(7**3) * sum(
        fricke[0][j] * x_prefix[j] for j in range(15)
    )
    wrong_power_y0 = -QQ(7**2) * sum(
        fricke[0][j] * x_prefix[j] for j in range(15)
    )
    if wrong_sign_y0 != -1 or wrong_power_y0 != QQ(1, 7):
        raise AssertionError("wrong-sign/power controls did not fail as expected")

    expected_multipliers = {
        "x8": QQ(180, 217),
        "x9": QQ(2344, 2387),
        "x11": QQ(1, 2387),
        "y1": QQ(1118523, 341),
        "y2": QQ(134113, 341),
        "y3": QQ(9604, 341),
        "y4": QQ(343, 341),
    }
    if bound != QQ(1997236, 341) or multipliers != expected_multipliers:
        raise AssertionError("independent certificate differs from sealed claim")

    return {
        "format": "wave86-level7-independent-verifier-v1",
        "claim_label": "VERIFIED",
        "verdict": "VERIFIED_WITH_LITERATURE_CORRECTION",
        "conditional_scope": (
            "Wave 71 q=16 row for a hypothetical srg(99,14,1,2)"
        ),
        "discovery_manifest_sha256": (
            "c6066fd10258578c15e511f3802217e4ff613ffe3d3b3b8f11e804f0316ac75d"
        ),
        "modular_space": {
            **space,
            "basis_rank_through_q14": basis_rank,
            "rank_after_omitting_one_basis_product": truncated_rank,
            "basis_products": [
                [[weight, side] for weight, side in product] for product in basis
            ],
            "fricke_square_is_identity": True,
        },
        "normalizations": {
            "character": "chi=(-7/.) modulo 7",
            "gauss_sum": "tau(chi)=i*sqrt(7)",
            "individual_fricke": {
                "E_k(chi,1)": "-i*7^((k-1)/2)*E_k(1,chi)",
                "E_k(1,chi)": "-i*7^((1-k)/2)*E_k(chi,1)",
            },
            "individual_W7_square": "chi(-1)=-1",
            "weight_22_product_W7_square": 1,
            "theta_series": "Theta=sum_v q^((v,v)/2)",
            "poisson_transfer": "Theta_L=-7^3*(Theta_K|W7)",
            "source_correction": (
                "Printed arXiv Eq.(2.8) omits the normalization ratio; "
                "the stated factors follow from Eqs.(2.5) and (2.7)."
            ),
            "norm_indexing": {
                "q7": "norm 14, hence N14",
                "q8": "norm 16, hence N16",
                "q9": "norm 18, hence N18",
            },
        },
        "positive_identity": {
            "left": "x7+x8+x9-1997236/341",
            "multipliers": {
                key: format_fraction(value)
                for key, value in multipliers.items()
            },
            "all_multipliers_positive": True,
            "rational_lower_bound": format_fraction(bound),
            "only_external_arithmetic_input": "Wave71: S=2 mod 14",
            "forced_integer_lower_bound": forced,
            "short_vector_conclusion": "N14+N16+N18>=5868",
        },
        "scalar_control": {
            "classification": "finite formal scalar null only",
            "not_a_lattice_or_graph": True,
            "checked_through_q": CHECK_PRECISION,
            "integral_even_nonnegative": True,
            "x0_to_x14": [int(value) for value in x_prefix],
            "y0_to_y14": [int(value) for value in y_prefix],
        },
        "hostile_controls": {
            "wrong_gauss_phase_sample": {
                "correct_A3_A19_factor": format_fraction(sample_factor),
                "omitted_phase_factor": format_fraction(wrong_phase_factor),
            },
            "wrong_theta_sign_y0": format_fraction(wrong_sign_y0),
            "wrong_theta_power_7_squared_y0": format_fraction(wrong_power_y0),
            "incomplete_basis_rank": truncated_rank,
        },
        "status": {
            "q16_excluded": False,
            "lattice_realized": False,
            "graph": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    free = free_physical_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run with only {free:.1f}% free physical memory")
    result = verify_exact()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--print" in os.sys.argv:
        print(encoded, end="")
        return
    if not CANONICAL_RESULT.exists():
        raise SystemExit("canonical independent-results.json is missing")
    if CANONICAL_RESULT.read_text(encoding="utf-8") != encoded:
        raise SystemExit("canonical independent-results.json mismatch")
    print(
        "PASS: independent exact verifier; "
        f"free physical memory {free:.1f}%"
    )


if __name__ == "__main__":
    main()
