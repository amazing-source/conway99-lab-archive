"""Independent exact verifier for the sealed Wave 101 discovery package.

The implementation does not import or execute Wave 101 code.  It rebuilds
M_22(Gamma0(7)), its Fricke involution, the rank-dependent Poisson transfer,
and exact primal/dual certificates for the scalar theta linear programs.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from fractions import Fraction
from pathlib import Path


Q = Fraction
LEVEL = 7
WEIGHT = 22
RANK = 44
STURM = 14
PRECISION = 14
CHARACTER = (0, 1, 1, -1, 1, -1, -1)
HERE = Path(__file__).resolve().parent
CANONICAL = HERE / "independent-results.json"


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0
    import ctypes

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


def chi(n: int) -> int:
    return CHARACTER[n % LEVEL]


def bernoulli_numbers(limit: int) -> list[Q]:
    values = [Q(0)] * (limit + 1)
    values[0] = Q(1)
    for degree in range(1, limit + 1):
        values[degree] = -sum(
            Q(math.comb(degree + 1, j)) * values[j]
            for j in range(degree)
        ) / Q(degree + 1)
    return values


BERNOULLI = bernoulli_numbers(WEIGHT)


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


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def eisenstein(weight: int, orientation: str) -> list[Q]:
    """Return E_k(chi,1) for C and E_k(1,chi) for T."""

    series = [Q(0)] * (PRECISION + 1)
    if orientation == "C":
        series[0] = -generalized_bernoulli(weight) / Q(2 * weight)
    elif orientation != "T":
        raise ValueError(orientation)
    for n in range(1, PRECISION + 1):
        series[n] = sum(
            Q(chi(d) if orientation == "C" else chi(n // d))
            * d ** (weight - 1)
            for d in divisors(n)
        )
    return series


EISENSTEIN = {
    (weight, orientation): eisenstein(weight, orientation)
    for weight in range(3, 20, 2)
    for orientation in ("C", "T")
}

Factor = tuple[int, str]
Product = tuple[Factor, Factor]
AffineForm = tuple[str, Q, list[Q]]


def multiply_series(left: list[Q], right: list[Q]) -> list[Q]:
    return [
        sum(left[j] * right[n - j] for j in range(n + 1))
        for n in range(PRECISION + 1)
    ]


def product_series(product: Product) -> list[Q]:
    return multiply_series(EISENSTEIN[product[0]], EISENSTEIN[product[1]])


def rank(matrix: list[list[Q]]) -> int:
    work = [row[:] for row in matrix]
    if not work:
        return 0
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (r for r in range(pivot_row, len(work)) if work[r][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for r in range(len(work)):
            if r == pivot_row or not work[r][column]:
                continue
            scale = work[r][column]
            work[r] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(
                    work[r], work[pivot_row], strict=True
                )
            ]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def inverse(matrix: list[list[Q]]) -> list[list[Q]]:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("square matrix required")
    work = [
        row[:] + [Q(r == c) for c in range(size)]
        for r, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (r for r in range(column, size) if work[r][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for r in range(size):
            if r == column or not work[r][column]:
                continue
            scale = work[r][column]
            work[r] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(
                    work[r], work[column], strict=True
                )
            ]
    return [row[size:] for row in work]


def matrix_product(left: list[list[Q]], right: list[list[Q]]) -> list[list[Q]]:
    return [
        [
            sum(left[r][k] * right[k][c] for k in range(len(right)))
            for c in range(len(right[0]))
        ]
        for r in range(len(left))
    ]


def solve(matrix: list[list[Q]], right: list[Q]) -> list[Q]:
    inv = inverse(matrix)
    return [
        sum(inv[r][c] * right[c] for c in range(len(right)))
        for r in range(len(inv))
    ]


def basis_candidates() -> list[Product]:
    candidates: list[Product] = []
    for left_weight in range(3, 12, 2):
        right_weight = WEIGHT - left_weight
        for left_type in ("C", "T"):
            for right_type in ("C", "T"):
                candidates.append(
                    ((left_weight, left_type), (right_weight, right_type))
                )
    return sorted(candidates, key=repr, reverse=True)


def coefficient_matrix(products: list[Product]) -> list[list[Q]]:
    return [
        [product_series(product)[n] for product in products]
        for n in range(STURM + 1)
    ]


def select_basis() -> list[Product]:
    selected: list[Product] = []
    old_rank = 0
    for candidate in basis_candidates():
        trial = selected + [candidate]
        new_rank = rank(coefficient_matrix(trial))
        if new_rank > old_rank:
            selected = trial
            old_rank = new_rank
        if old_rank == 15:
            break
    if old_rank != 15:
        raise AssertionError(old_rank)
    return selected


def fricke_product(product: Product) -> tuple[Q, Product]:
    """Use the corrected q-normalized Fricke formulas.

    Both odd-character Eisenstein factors contribute phase -i.  The product
    phase is therefore -1.
    """

    mapped: list[Factor] = []
    factor = Q(-1)
    for weight, orientation in product:
        exponent = (
            (weight - 1) // 2
            if orientation == "C"
            else (1 - weight) // 2
        )
        factor *= (
            Q(LEVEL**exponent)
            if exponent >= 0
            else Q(1, LEVEL ** (-exponent))
        )
        mapped.append(
            (weight, "T" if orientation == "C" else "C")
        )
    return factor, (mapped[0], mapped[1])


def fricke_matrix(basis: list[Product]) -> list[list[Q]]:
    prefix_to_coordinates = inverse(coefficient_matrix(basis))
    transformed = []
    for n in range(STURM + 1):
        transformed.append(
            [
                fricke_product(product)[0]
                * product_series(fricke_product(product)[1])[n]
                for product in basis
            ]
        )
    return matrix_product(transformed, prefix_to_coordinates)


def modular_invariants() -> dict[str, int]:
    index = 8
    cusps = 2
    e2 = 0
    e3 = 2
    genus = Q(1) + Q(index, 12) - Q(e2, 4) - Q(e3, 3) - Q(cusps, 2)
    cusp_dimension = (
        (WEIGHT - 1) * (genus - 1)
        + (Q(WEIGHT, 2) - 1) * cusps
        + (WEIGHT // 4) * e2
        + (WEIGHT // 3) * e3
    )
    return {
        "index": index,
        "cusps": cusps,
        "elliptic_order_2": e2,
        "elliptic_order_3": e3,
        "genus": int(genus),
        "cusp_dimension": int(cusp_dimension),
        "eisenstein_dimension": cusps,
        "dimension": int(cusp_dimension + cusps),
        "sturm_bound": WEIGHT * index // 12,
    }


def transfer_factor(q_value: int) -> Q:
    """Theta_L = factor * (Theta_K |_22 W_7)."""

    if q_value not in range(2, 15, 2):
        raise ValueError(q_value)
    # det(K)=7^(44-q); Poisson gives
    # Theta_K|W_7 = -7^(q/2-11) Theta_L.
    return -Q(LEVEL ** (11 - q_value // 2))


def affine_system(q_value: int, fricke: list[list[Q]]) -> dict[str, object]:
    factor = transfer_factor(q_value)
    raw_constants = [factor * fricke[n][0] for n in range(15)]
    raw_rows = [
        [factor * fricke[n][j] for j in range(7, 15)]
        for n in range(15)
    ]
    pivot = raw_rows[0][7]
    x14_constant = (Q(1) - raw_constants[0]) / pivot
    x14_row = [-raw_rows[0][j] / pivot for j in range(7)]
    y_constants = [
        raw_constants[n] + raw_rows[n][7] * x14_constant
        for n in range(15)
    ]
    y_rows = [
        [
            raw_rows[n][j] + raw_rows[n][7] * x14_row[j]
            for j in range(7)
        ]
        for n in range(15)
    ]
    if y_constants[0] != 1 or any(y_rows[0]):
        raise AssertionError("constant-term elimination failed")
    forms: list[AffineForm] = [
        (
            f"x{7 + j}",
            Q(0),
            [Q(k == j) for k in range(7)],
        )
        for j in range(7)
    ]
    forms.append(("x14", x14_constant, x14_row))
    forms.extend(
        (f"y{n}", y_constants[n], y_rows[n])
        for n in range(1, 15)
    )
    return {
        "factor": factor,
        "x14_constant": x14_constant,
        "x14_row": x14_row,
        "y_constants": y_constants,
        "y_rows": y_rows,
        "forms": forms,
    }


def objective_prefix(end: int, system: dict[str, object]) -> tuple[Q, list[Q]]:
    if end not in range(7, 15):
        raise ValueError(end)
    constant = Q(0)
    row = [Q(0)] * 7
    for n in range(7, min(end, 13) + 1):
        row[n - 7] += 1
    if end == 14:
        constant += system["x14_constant"]
        row = [
            row[j] + system["x14_row"][j]
            for j in range(7)
        ]
    return constant, row


def objective_triangular(system: dict[str, object]) -> tuple[Q, list[Q]]:
    # 8*x7+7*x8+...+x14.
    constant = system["x14_constant"]
    return constant, [
        Q(8 - j) + system["x14_row"][j]
        for j in range(7)
    ]


NONZERO_ACTIVE: dict[int, dict[str, list[str]]] = {
    2: {
        "prefix13": ["x7", "x8", "x10", "x11", "x12", "x13", "y1"],
        "prefix14": ["x8", "x10", "x11", "x12", "x13", "x14", "y1"],
    },
    4: {
        "prefix12": ["x8", "x9", "x10", "x11", "x12", "y1", "y2"],
        "prefix13": ["x7", "x8", "x10", "x11", "x12", "x13", "y1"],
        "prefix14": ["x8", "x10", "x11", "x12", "x13", "x14", "y1"],
    },
    6: {
        "prefix12": ["x8", "x9", "x10", "x11", "x12", "y1", "y2"],
        "prefix13": ["x7", "x8", "x10", "x11", "x12", "x13", "y1"],
        "prefix14": ["x8", "x10", "x11", "x12", "x13", "x14", "y1"],
    },
    8: {
        "prefix12": ["x8", "x9", "x10", "x11", "x12", "y1", "y2"],
        "prefix13": ["x7", "x8", "x10", "x11", "x12", "x13", "y1"],
        "prefix14": ["x8", "x10", "x11", "x12", "x13", "x14", "y1"],
    },
    10: {
        "prefix11": ["x8", "x9", "x10", "x11", "y1", "y2", "y3"],
        "prefix12": ["x8", "x9", "x10", "x11", "x12", "y1", "y2"],
        "prefix13": ["x8", "x10", "x11", "x12", "x13", "y1", "y4"],
        "prefix14": ["x8", "x10", "x11", "x12", "x13", "x14", "y1"],
    },
    12: {
        "prefix11": ["x8", "x9", "x10", "x11", "y1", "y2", "y3"],
        "prefix12": ["x9", "x10", "x11", "x12", "y1", "y2", "y5"],
        "prefix13": ["x8", "x10", "x11", "x12", "x13", "y1", "y4"],
        "prefix14": ["x8", "x10", "x11", "x12", "x13", "y1", "y5"],
    },
    14: {
        "prefix10": ["x8", "x9", "x10", "y1", "y2", "y3", "y4"],
        "prefix11": ["x7", "x10", "x11", "y1", "y2", "y3", "y5"],
        "prefix12": ["x8", "x11", "x12", "y1", "y2", "y4", "y5"],
        "prefix13": ["x8", "x10", "x12", "y1", "y2", "y4", "y5"],
        "prefix14": ["x8", "x11", "x12", "y1", "y2", "y4", "y5"],
    },
}

TRIANGULAR_ACTIVE = {
    2: NONZERO_ACTIVE[2]["prefix14"],
    4: NONZERO_ACTIVE[4]["prefix14"],
    6: NONZERO_ACTIVE[6]["prefix14"],
    8: NONZERO_ACTIVE[8]["prefix14"],
    10: NONZERO_ACTIVE[10]["prefix14"],
    12: NONZERO_ACTIVE[12]["prefix14"],
    14: NONZERO_ACTIVE[14]["prefix14"],
}

ZERO_CONTROL_ACTIVE = {
    2: ["x7", "x8", "x9", "x10", "x11", "x12", "y1"],
    4: ["x7", "x8", "x9", "x10", "x11", "y1", "y2"],
    6: ["x7", "x8", "x9", "x10", "x11", "y1", "y2"],
    8: ["x7", "x8", "x9", "x10", "x11", "y1", "y2"],
    10: ["x7", "x8", "x9", "x10", "y1", "y2", "y3"],
    12: ["x7", "x8", "x9", "x10", "x12", "y1", "y2"],
    14: ["x7", "x8", "x9", "y1", "y2", "y3", "y4"],
}


def evaluate(form: AffineForm, point: list[Q]) -> Q:
    return form[1] + sum(
        coefficient * value
        for coefficient, value in zip(form[2], point, strict=True)
    )


def exact_certificate(
    objective: tuple[Q, list[Q]],
    system: dict[str, object],
    active_labels: list[str],
) -> dict[str, object]:
    forms: list[AffineForm] = system["forms"]
    by_label = {form[0]: form for form in forms}
    active = [by_label[label] for label in active_labels]
    point = solve(
        [form[2] for form in active],
        [-form[1] for form in active],
    )
    values = {form[0]: evaluate(form, point) for form in forms}
    if not all(value >= 0 for value in values.values()):
        bad = {key: value for key, value in values.items() if value < 0}
        raise AssertionError(("infeasible primal", bad))

    objective_constant, objective_row = objective
    # objective_row = sum multiplier_i * active_row_i.
    transpose = [
        [active[column][2][row] for column in range(7)]
        for row in range(7)
    ]
    multipliers = solve(transpose, objective_row)
    if not all(value >= 0 for value in multipliers):
        raise AssertionError(("negative dual", active_labels, multipliers))
    bound = objective_constant - sum(
        multiplier * form[1]
        for multiplier, form in zip(multipliers, active, strict=True)
    )
    primal_value = objective_constant + sum(
        coefficient * value
        for coefficient, value in zip(objective_row, point, strict=True)
    )
    if primal_value != bound:
        raise AssertionError(("duality gap", primal_value, bound))
    return {
        "bound": format_q(bound),
        "parity_rounded_bound": next_even_at_least(bound),
        "active_constraints": active_labels,
        "primal_x7_to_x13": [format_q(value) for value in point],
        "primal_x14": format_q(values["x14"]),
        "primal_y1_to_y14": [
            format_q(values[f"y{n}"]) for n in range(1, 15)
        ],
        "dual_multipliers": {
            label: format_q(value)
            for label, value in zip(active_labels, multipliers, strict=True)
            if value
        },
        "all_primal_forms_nonnegative": True,
        "all_dual_multipliers_nonnegative": True,
        "exact_strong_duality": True,
    }


def zero_prefix_certificates(
    q_value: int,
    system: dict[str, object],
    maximum_zero_end: int,
) -> dict[str, object]:
    forms: list[AffineForm] = system["forms"]
    by_label = {form[0]: form for form in forms}
    active = [by_label[label] for label in ZERO_CONTROL_ACTIVE[q_value]]
    point = solve(
        [form[2] for form in active],
        [-form[1] for form in active],
    )
    values = {form[0]: evaluate(form, point) for form in forms}
    if not all(value >= 0 for value in values.values()):
        raise AssertionError("zero-prefix control is infeasible")
    if any(values[f"x{n}"] for n in range(7, maximum_zero_end + 1)):
        raise AssertionError("zero-prefix control misses a forced zero")
    return {
        "maximum_zero_prefix_end": maximum_zero_end,
        "active_constraints": ZERO_CONTROL_ACTIVE[q_value],
        "x7_to_x14": [
            format_q(values[f"x{n}"]) for n in range(7, 15)
        ],
        "y1_to_y14": [
            format_q(values[f"y{n}"]) for n in range(1, 15)
        ],
        "all_22_coordinates_nonnegative": True,
        "x7_x8_x9_are_zero": all(
            values[f"x{n}"] == 0 for n in (7, 8, 9)
        ),
    }


def format_q(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def next_even_at_least(value: Q) -> int:
    integer = (value.numerator + value.denominator - 1) // value.denominator
    return integer + integer % 2


def mod7_rank_and_relations() -> dict[str, object]:
    """Reconstruct the absence of a q7-q9 relation for q <= 14."""

    modulus = 7

    def sigma(n: int, power: int) -> int:
        return sum(d**power for d in divisors(n))

    e4 = [1] + [
        240 * sigma(n, 3) % modulus for n in range(1, 15)
    ]
    e6 = [1] + [
        -504 * sigma(n, 5) % modulus for n in range(1, 15)
    ]
    if e6 != [1] + [0] * 14:
        raise AssertionError("E6 is not 1 modulo seven")

    def convolution(left: list[int], right: list[int]) -> list[int]:
        return [
            sum(left[j] * right[n - j] for j in range(n + 1)) % modulus
            for n in range(15)
        ]

    def power(series: list[int], exponent: int) -> list[int]:
        result = [1] + [0] * 14
        for _ in range(exponent):
            result = convolution(result, series)
        return result

    rows = []
    for q_value in range(2, 15, 2):
        weight = 154 - 3 * q_value
        exponents = [
            (a, (weight - 4 * a) // 6)
            for a in range(weight // 4 + 1)
            if weight >= 4 * a and (weight - 4 * a) % 6 == 0
        ]
        basis = [
            convolution(power(e4, a), power(e6, b))
            for a, b in exponents
        ]
        matrix = [
            [basis[column][n] for column in range(len(basis))]
            for n in range(7)
        ]
        augmented = [
            row[:] + [int(i == 0)]
            for i, row in enumerate(matrix)
        ]
        pivot_row = 0
        pivots = []
        for column in range(len(basis)):
            pivot = next(
                (
                    r
                    for r in range(pivot_row, 7)
                    if augmented[r][column] % modulus
                ),
                None,
            )
            if pivot is None:
                continue
            augmented[pivot_row], augmented[pivot] = (
                augmented[pivot],
                augmented[pivot_row],
            )
            scale = pow(augmented[pivot_row][column], -1, modulus)
            augmented[pivot_row] = [
                value * scale % modulus
                for value in augmented[pivot_row]
            ]
            for r in range(7):
                if r == pivot_row:
                    continue
                scale = augmented[r][column] % modulus
                if scale:
                    augmented[r] = [
                        (left - scale * right) % modulus
                        for left, right in zip(
                            augmented[r], augmented[pivot_row], strict=True
                        )
                    ]
            pivots.append(column)
            pivot_row += 1
        free = [
            column for column in range(len(basis))
            if column not in pivots
        ]

        def coefficient_vector(free_values: list[int]) -> tuple[int, ...]:
            solution = [0] * len(basis)
            for column, value in zip(free, free_values, strict=True):
                solution[column] = value
            for r, column in reversed(list(enumerate(pivots))):
                solution[column] = (
                    augmented[r][-1]
                    - sum(
                        augmented[r][j] * solution[j]
                        for j in free
                    )
                ) % modulus
            return tuple(
                sum(
                    solution[column] * basis[column][n]
                    for column in range(len(basis))
                ) % modulus
                for n in range(7, 15)
            )

        base = coefficient_vector([0] * len(free))
        directions_full = []
        for i in range(len(free)):
            unit = [0] * len(free)
            unit[i] = 1
            moved = coefficient_vector(unit)
            directions_full.append(
                tuple((moved[j] - base[j]) % modulus for j in range(8))
            )
        directions = [direction[:3] for direction in directions_full]
        direction_rank = 0
        span = []
        for vector in directions:
            trial = span + [list(vector)]
            new_rank = rank_mod7(trial)
            if new_rank > direction_rank:
                span = trial
                direction_rank = new_rank
        objective_rows = {}
        objective_weights = {
            **{
                f"prefix{end}": [
                    int(n <= end) for n in range(7, 15)
                ]
                for end in range(7, 15)
            },
            "triangular": list(range(8, 0, -1)),
        }
        for label, weights in objective_weights.items():
            base_residue = sum(
                weight_value * coefficient
                for weight_value, coefficient in zip(
                    weights, base, strict=True
                )
            ) % modulus
            direction_residues = [
                sum(
                    weight_value * coefficient
                    for weight_value, coefficient in zip(
                        weights, direction, strict=True
                    )
                ) % modulus
                for direction in directions_full
            ]
            objective_rows[label] = {
                "particular_residue_mod_7": base_residue,
                "direction_residues_mod_7": direction_residues,
                "fixed_residue": not any(direction_residues),
            }
        if any(
            objective["fixed_residue"]
            for objective in objective_rows.values()
        ):
            raise AssertionError(("unexpected fixed objective", q_value))
        rows.append(
            {
                "q": q_value,
                "weight": weight,
                "affine_direction_rank_on_x7_x8_x9": direction_rank,
                "no_affine_relation_on_x7_x8_x9": direction_rank == 3,
                "objectives": objective_rows,
            }
        )
    if not all(row["no_affine_relation_on_x7_x8_x9"] for row in rows):
        raise AssertionError(rows)
    return {
        "rows": rows,
        "scope": (
            "For q=2,4,...,14 the level-one mod-7 congruence forces no "
            "affine relation among x7,x8,x9, and every tested prefix or "
            "triangular objective varies in an affine direction. Only "
            "antipodal evenness is used to round the rational LP bounds."
        ),
    }


def rank_mod7(matrix: list[list[int]]) -> int:
    work = [[value % 7 for value in row] for row in matrix]
    pivot_row = 0
    if not work:
        return 0
    for column in range(len(work[0])):
        pivot = next(
            (r for r in range(pivot_row, len(work)) if work[r][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = pow(work[pivot_row][column], -1, 7)
        work[pivot_row] = [
            value * scale % 7 for value in work[pivot_row]
        ]
        for r in range(len(work)):
            if r == pivot_row:
                continue
            scale = work[r][column]
            if scale:
                work[r] = [
                    (left - scale * right) % 7
                    for left, right in zip(
                        work[r], work[pivot_row], strict=True
                    )
                ]
        pivot_row += 1
    return pivot_row


def mod2_lattice_comparisons() -> dict[str, object]:
    cosets = 2**RANK - 1
    return {
        "nonzero_cosets_of_2K": cosets,
        "prefix_x7_to_x13_upper": 2 * cosets,
        "prefix_x7_to_x14_upper": 2 * RANK * cosets,
        "triangular_weighted_upper": 2 * RANK * cosets,
        "proof": (
            "If u and v are non-antipodal representatives of one class "
            "modulo 2K, then (u+v)/2 and (u-v)/2 are nonzero lattice "
            "vectors and the parallelogram law forces ||u||^2+||v||^2 "
            "at least 4*min(K)=56. Thus below norm 28 each nonzero class "
            "has at most one antipodal pair. At norm 28, equality forces "
            "same-class representatives to be pairwise orthogonal, hence "
            "at most rank(K)=44 antipodal pairs. The same 44-pair cap "
            "bounds both the unweighted and weights-8-through-1 sums "
            "per nonzero mod-2 class."
        ),
        "assessment": (
            "These universal rank-44 lattice upper bounds are many orders "
            "of magnitude above the verified scalar LP lower bounds."
        ),
    }


def build_results() -> dict[str, object]:
    space = modular_invariants()
    if space["dimension"] != 15 or space["sturm_bound"] != 14:
        raise AssertionError(space)
    basis = select_basis()
    basis_matrix = coefficient_matrix(basis)
    fricke = fricke_matrix(basis)
    identity = [
        [Q(r == c) for c in range(15)] for r in range(15)
    ]
    if matrix_product(fricke, fricke) != identity:
        raise AssertionError("Fricke square is not identity")

    maximum_zero = {2: 12, 4: 11, 6: 11, 8: 11, 10: 10, 12: 10, 14: 9}
    rows = []
    for q_value in range(2, 15, 2):
        system = affine_system(q_value, fricke)
        prefixes: dict[str, object] = {}
        for end in range(7, 15):
            label = f"prefix{end}"
            if end <= maximum_zero[q_value]:
                prefixes[label] = {
                    "bound": "0",
                    "parity_rounded_bound": 0,
                    "dual_multipliers": {
                        f"x{n}": "1" for n in range(7, end + 1)
                    },
                    "certificate_type": (
                        "direct nonnegative-coordinate lower bound, with "
                        "the row zero control as a feasible primal witness"
                    ),
                }
            else:
                prefixes[label] = exact_certificate(
                    objective_prefix(end, system),
                    system,
                    NONZERO_ACTIVE[q_value][label],
                )
        rows.append(
            {
                "q": q_value,
                "r": RANK - q_value,
                "poisson_factor": format_q(system["factor"]),
                "prefix_bounds": prefixes,
                "triangular_weighted_bound": exact_certificate(
                    objective_triangular(system),
                    system,
                    TRIANGULAR_ACTIVE[q_value],
                ),
                "zero_prefix_control": zero_prefix_certificates(
                    q_value, system, maximum_zero[q_value]
                ),
            }
        )

    return {
        "format": "wave101-independent-verifier-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "verdict": "VERIFIED_SCOPED",
        "conditional_scope": (
            "scalar theta cones attached to the Wave 71 level-7 lattice "
            "rows q=2,4,...,14 for a hypothetical srg(99,14,1,2)"
        ),
        "discovery_manifest_sha256": (
            "54d620a8644d7efe5d2e418869b035331127862c2125ef3da325272417307619"
        ),
        "modular_space": {
            **space,
            "basis_rank_through_q14": rank(basis_matrix),
            "fricke_square_is_identity": True,
            "basis_products": [
                [[weight, side] for weight, side in product]
                for product in basis
            ],
        },
        "normalizations": {
            "theta_series": "Theta=sum_v q^((v,v)/2)",
            "x": "Theta_K, with x_n counting vectors of norm 2n",
            "y": "Theta_L",
            "poisson_formula": (
                "Theta_L=-7^(11-q/2)*(Theta_K|_22 W_7)"
            ),
            "fricke_formulas": {
                "E_k(chi,1)": (
                    "-i*7^((k-1)/2)*E_k(1,chi)"
                ),
                "E_k(1,chi)": (
                    "-i*7^((1-k)/2)*E_k(chi,1)"
                ),
            },
        },
        "rows": rows,
        "mod7_scope": mod7_rank_and_relations(),
        "mod2_lattice_upper_comparisons": mod2_lattice_comparisons(),
        "dictionary_scope": {
            "certified": {
                "x7": "N14, norm-14 integer -4 eigenvectors",
                "x8": "N16, norm-16 integer -4 eigenvectors",
                "x9": "N18, norm-18 integer -4 eigenvectors",
            },
            "not_certified": (
                "No signed-unit-support or integer-eigenvector dictionary "
                "is asserted for x10,x11,x12,x13,x14."
            ),
        },
        "boundary": {
            "all_rank_row_excluded": False,
            "graph_constructed": False,
            "lattice_realized": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
            "crucial_scalar_null": (
                "Every q=2,4,...,14 row has an exact feasible first-15-"
                "coefficient scalar control with x7=x8=x9=0."
            ),
        },
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run at {free:.1f}% free memory")
    encoded = canonical_bytes(build_results())
    if args.output:
        args.output.write_bytes(encoded)
    elif args.verify:
        if not CANONICAL.exists() or CANONICAL.read_bytes() != encoded:
            raise SystemExit("independent-results.json is missing or stale")
    else:
        CANONICAL.write_bytes(encoded)
    print(
        "PASS: Wave 101 independent all-rank exact LP verifier; "
        f"free memory {free:.1f}%"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
