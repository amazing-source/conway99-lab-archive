"""Exact arithmetic for the Wave 124 one-variable C4 Jacobi reduction.

This script intentionally separates two claims.

* The lattice/C4 calculation is conditional on frozen verified inputs.
* The basis calculation constructs the full-level subspace
  J_{22,10}(SL_2(Z)) inside J_{22,10}(Gamma_0(7)); it is not advertised as
  a basis of the whole level-seven space.

All q-y expansions use q=exp(2*pi*i*tau), y=exp(2*pi*i*z), and exact
fractions.  No discovery artifact is imported by an eventual verifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WEIGHT = 22
INDEX_L = 10
INDEX_K = 70
QMAX = 10

FROZEN_INPUTS = {
    "verification/wave71-modular-theta-extension/package-manifest.sha256":
        "0eede2ebc625534360dda3f8e62456e582f5184fd18d3820dd44748de95a5237",
    "verification/wave96-norm16-norm18-upper/package-manifest.sha256":
        "8b3f9f90de931dc152ccf1b9e0705409492a6c5eb5246643ddce55aad8afe6e9",
    "verification/wave112-c4-short-vector-incidence/package-manifest.sha256":
        "56845bcdf221c16ec46d40c630a8cdb3d63beed1314dd2683e17bf5c929ff024",
    "verification/wave116-c4-jacobi-theta/package-manifest.sha256":
        "e44afa352f51c192d6c5ac8584ccd6334dd69a3d11856f4ac0254283829bbfb8",
}

Poly = dict[tuple[int, int], Fraction]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_frozen_inputs() -> None:
    for rel, expected in FROZEN_INPUTS.items():
        actual = sha256(ROOT / rel)
        if actual != expected:
            raise ValueError(f"frozen input mismatch: {rel}: {actual} != {expected}")


def clean(poly: Poly) -> Poly:
    return {key: value for key, value in poly.items() if value}


def add(left: Poly, right: Poly, scale: Fraction = Fraction(1)) -> Poly:
    out: defaultdict[tuple[int, int], Fraction] = defaultdict(Fraction)
    out.update(left)
    for key, value in right.items():
        out[key] += scale * value
    return clean(dict(out))


def mul(left: Poly, right: Poly, qmax: int = QMAX) -> Poly:
    out: defaultdict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for (n1, r1), c1 in left.items():
        for (n2, r2), c2 in right.items():
            if n1 + n2 <= qmax:
                out[n1 + n2, r1 + r2] += c1 * c2
    return clean(dict(out))


def power(base: Poly, exponent: int, qmax: int = QMAX) -> Poly:
    out: Poly = {(0, 0): Fraction(1)}
    factor = base
    e = exponent
    while e:
        if e & 1:
            out = mul(out, factor, qmax)
        e >>= 1
        if e:
            factor = mul(factor, factor, qmax)
    return out


def sigma(n: int, exponent: int) -> int:
    return sum(d**exponent for d in range(1, n + 1) if n % d == 0)


def eisenstein(weight: int, qmax: int = QMAX) -> Poly:
    if weight == 4:
        multiplier, exponent = 240, 3
    elif weight == 6:
        multiplier, exponent = -504, 5
    else:
        raise ValueError(weight)
    out: Poly = {(0, 0): Fraction(1)}
    for n in range(1, qmax + 1):
        out[n, 0] = Fraction(multiplier * sigma(n, exponent))
    return out


def phi_minus2(qmax: int = QMAX) -> Poly:
    """Product expansion of phi_{-2,1}=-theta_1^2/eta^6."""

    out: Poly = {
        (0, -1): Fraction(1),
        (0, 0): Fraction(-2),
        (0, 1): Fraction(1),
    }
    for n in range(1, qmax + 1):
        scalar: Poly = {
            (j * n, 0): Fraction(math.comb(j + 3, 3))
            for j in range(qmax // n + 1)
        }
        plus: Poly = {
            (0, 0): Fraction(1),
            (n, 1): Fraction(-2),
            (2 * n, 2): Fraction(1),
        }
        minus: Poly = {
            (0, 0): Fraction(1),
            (n, -1): Fraction(-2),
            (2 * n, -2): Fraction(1),
        }
        out = mul(mul(mul(out, scalar, qmax), plus, qmax), minus, qmax)
    return out


def _theta_terms(kind: str, q8max: int) -> dict[tuple[int, int], Fraction]:
    """Return theta terms in Q=q^(1/8), Y=y^(1/2)."""

    out: defaultdict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for n in range(-32, 33):
        if kind == "theta2":
            q8 = (2 * n + 1) ** 2
            y2 = 2 * n + 1
            coeff = 1
        elif kind == "theta3":
            q8 = 4 * n * n
            y2 = 2 * n
            coeff = 1
        elif kind == "theta4":
            q8 = 4 * n * n
            y2 = 2 * n
            coeff = -1 if n % 2 else 1
        else:
            raise ValueError(kind)
        if q8 <= q8max + 8:
            out[q8, y2] += Fraction(coeff)
    return clean(dict(out))


def _qy_mul(
    left: dict[tuple[int, int], Fraction],
    right: dict[tuple[int, int], Fraction],
    q8max: int,
) -> dict[tuple[int, int], Fraction]:
    out: defaultdict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for (q1, y1), c1 in left.items():
        for (q2, y2), c2 in right.items():
            if q1 + q2 <= q8max:
                out[q1 + q2, y1 + y2] += c1 * c2
    return clean(dict(out))


def _theta_ratio_q8(kind: str, qmax: int) -> dict[tuple[int, int], Fraction]:
    q8max = 8 * qmax + 2
    theta = _theta_terms(kind, q8max)
    numerator = _qy_mul(theta, theta, q8max)
    denominator: defaultdict[int, Fraction] = defaultdict(Fraction)
    for (q8, _y2), coeff in numerator.items():
        denominator[q8] += coeff

    shift = min(q for q, coeff in denominator.items() if coeff)
    numerator = {(q - shift, y): c for (q, y), c in numerator.items()}
    denominator = {q - shift: c for q, c in denominator.items()}
    d0 = denominator[0]
    inverse: dict[int, Fraction] = {0: Fraction(1, 1) / d0}
    for n in range(1, 8 * qmax + 1):
        total = sum(
            denominator.get(j, Fraction(0)) * inverse.get(n - j, Fraction(0))
            for j in range(1, n + 1)
        )
        inverse[n] = -total / d0

    ratio_q8: defaultdict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for (q8, y2), coeff in numerator.items():
        for extra, inv in inverse.items():
            if q8 + extra <= 8 * qmax:
                ratio_q8[q8 + extra, y2] += coeff * inv

    return clean(dict(ratio_q8))


def phi_zero(qmax: int = QMAX) -> Poly:
    combined: defaultdict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for kind in ("theta2", "theta3", "theta4"):
        for key, value in _theta_ratio_q8(kind, qmax).items():
            combined[key] += 4 * value
    out: defaultdict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for (q8, y2), coeff in combined.items():
        if coeff:
            if q8 % 8 or y2 % 2:
                raise AssertionError(
                    f"fractional exponent survived in phi_0,1: {(q8, y2)}"
                )
            out[q8 // 8, y2 // 2] += coeff
    return clean(dict(out))


def weak_monomials() -> list[tuple[int, int, int, int]]:
    """Tuples (a,b,c,d) for E4^a E6^b A^c B^d."""

    rows: list[tuple[int, int, int, int]] = []
    for c in range(INDEX_L + 1):
        d = INDEX_L - c
        modular_weight = WEIGHT + 2 * c
        for a in range(modular_weight // 4 + 1):
            remainder = modular_weight - 4 * a
            if remainder >= 0 and remainder % 6 == 0:
                rows.append((a, remainder // 6, c, d))
    return rows


def monomial_expansions(qmax: int = QMAX) -> tuple[list[tuple[int, int, int, int]], list[Poly]]:
    e4 = eisenstein(4, qmax)
    e6 = eisenstein(6, qmax)
    aa = phi_minus2(qmax)
    bb = phi_zero(qmax)
    monomials = weak_monomials()
    expansions: list[Poly] = []
    for a, b, c, d in monomials:
        value: Poly = {(0, 0): Fraction(1)}
        for factor, exponent in ((e4, a), (e6, b), (aa, c), (bb, d)):
            value = mul(value, power(factor, exponent, qmax), qmax)
        expansions.append(value)
    return monomials, expansions


def nullspace(rows: Iterable[Iterable[Fraction]], columns: int) -> list[list[Fraction]]:
    """Deterministic rational nullspace in free-column order."""

    matrix = [list(row) for row in rows]
    if not matrix:
        return [
            [Fraction(int(i == j)) for i in range(columns)]
            for j in range(columns)
        ]
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(columns):
        selected = next(
            (row for row in range(pivot_row, len(matrix)) if matrix[row][column]),
            None,
        )
        if selected is None:
            continue
        matrix[pivot_row], matrix[selected] = matrix[selected], matrix[pivot_row]
        scale = matrix[pivot_row][column]
        matrix[pivot_row] = [value / scale for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            multiple = matrix[row][column]
            matrix[row] = [
                left - multiple * right
                for left, right in zip(matrix[row], matrix[pivot_row], strict=True)
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    free_columns = [column for column in range(columns) if column not in pivot_columns]
    basis: list[list[Fraction]] = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(columns)]
        vector[free] = Fraction(1)
        for row, pivot in enumerate(pivot_columns):
            vector[pivot] = -matrix[row][free]
        basis.append(vector)
    return basis


def constraint_keys(expansions: list[Poly], cusp: bool) -> list[tuple[int, int]]:
    keys = set().union(*(expansion.keys() for expansion in expansions))
    if cusp:
        return sorted((n, r) for n, r in keys if 4 * INDEX_L * n - r * r <= 0)
    return sorted((n, r) for n, r in keys if 4 * INDEX_L * n - r * r < 0)


def kernel_basis(
    expansions: list[Poly],
    columns: list[int],
    cusp: bool,
) -> tuple[list[tuple[int, int]], list[list[Fraction]]]:
    selected = [expansions[index] for index in columns]
    keys = constraint_keys(selected, cusp)
    rows = [
        [expansion.get(key, Fraction(0)) for expansion in selected]
        for key in keys
    ]
    return keys, nullspace(rows, len(selected))


def linear_combination(
    expansions: list[Poly],
    columns: list[int],
    coefficients: list[Fraction],
    qmax: int = QMAX,
) -> Poly:
    out: Poly = {}
    for index, coefficient in zip(columns, coefficients, strict=True):
        out = add(out, expansions[index], coefficient)
    return {key: value for key, value in out.items() if key[0] <= qmax and value}


def primitive_integer_vector(vector: list[Fraction]) -> list[int]:
    common_denominator = math.lcm(*(value.denominator for value in vector))
    integers = [value.numerator * (common_denominator // value.denominator) for value in vector]
    divisor = math.gcd(*(abs(value) for value in integers if value))
    integers = [value // divisor for value in integers]
    first = next(value for value in integers if value)
    if first < 0:
        integers = [-value for value in integers]
    return integers


def first_target_direction(
    monomials: list[tuple[int, int, int, int]],
    expansions: list[Poly],
    minimum_a_power: int = 1,
    include_terms: bool = True,
) -> dict[str, object]:
    columns = [
        index
        for index, (_a, _b, c, _d) in enumerate(monomials)
        if c >= minimum_a_power
    ]
    polar_keys, basis = kernel_basis(expansions, columns, cusp=True)
    target = (1, 4)
    chosen: list[Fraction] | None = None
    target_value = Fraction(0)
    for vector in basis:
        form = linear_combination(expansions, columns, vector)
        if form.get(target, Fraction(0)):
            chosen = vector
            target_value = form[target]
            break
    if chosen is None:
        return {
            "exists": False,
            "a_divisible_cusp_dimension": len(basis),
            "minimum_A_power": minimum_a_power,
            "target": [1, 4],
        }

    integral = primitive_integer_vector(chosen)
    form = linear_combination(
        expansions,
        columns,
        [Fraction(value) for value in integral],
    )
    target_integral = form[target]
    if target_integral < 0:
        integral = [-value for value in integral]
        form = {key: -value for key, value in form.items()}
        target_integral = -target_integral

    terms = []
    for column, coefficient in zip(columns, integral, strict=True):
        if coefficient and include_terms:
            terms.append(
                {
                    "coefficient": coefficient,
                    "monomial_E4_E6_A_B": list(monomials[column]),
                }
            )
    nonzero_q1 = [
        {"r": r, "coefficient": str(value)}
        for (n, r), value in sorted(form.items())
        if n == 1 and value
    ]
    return {
        "exists": True,
        "a_divisible_cusp_dimension": len(basis),
        "minimum_A_power": minimum_a_power,
        "vanishing_order_at_z_zero_at_least": 2 * minimum_a_power,
        "polar_or_boundary_constraints": len(polar_keys),
        "target": [1, 4],
        "target_coefficient": str(target_integral),
        "monomial_terms": terms,
        "q1_coefficients": nonzero_q1,
        "z_zero_identically": True,
        "cusp": True,
        "oldform_lift": {
            "L_direction": "psi(tau,z)",
            "K_direction": "-7^(qdisc/2)*psi(7tau,7z)",
            "K_target": [7, 28],
            "changes_only_K_q_exponents_divisible_by_7": True,
            "preserves_both_constant_terms": True,
            "preserves_both_z_zero_scalar_specializations": True,
        },
    }


def even_indicator_coefficients() -> list[str]:
    """Coefficients low-to-high of prod_{j=0}^3 (X^2-j^2)/(16-j^2)."""

    poly = [Fraction(1)]
    denominator = Fraction(1)
    for j in range(4):
        next_poly = [Fraction(0) for _ in range(len(poly) + 2)]
        for degree, coefficient in enumerate(poly):
            next_poly[degree] -= j * j * coefficient
            next_poly[degree + 2] += coefficient
        poly = next_poly
        denominator *= 16 - j * j
    return [str(coefficient / denominator) for coefficient in poly]


def coefficient_selection_rows() -> list[dict[str, object]]:
    rows = []
    profiles = {
        14: (7, 7),
        16: (8, 8),
        18: (9, 9),
        20: (10, 10),
    }
    c4_minima = {14: 21, 16: 20, 18: 18, 20: 15}
    for norm, signs in profiles.items():
        q_exponent = norm // 2
        rows.append(
            {
                "norm": norm,
                "q_exponent": q_exponent,
                "verified_unit_profile": {"plus_one": signs[0], "minus_one": signs[1]},
                "K_fourier_exponent": 28,
                "dot_epsilon_coordinate_sum": 4,
                "exact_pattern_selected": [1, -1, 1, -1],
                "minimum_alternating_C4_per_antipodal_support": c4_minima[norm],
            }
        )
    return rows


def build_results() -> dict[str, object]:
    verify_frozen_inputs()
    monomials, expansions = monomial_expansions()

    polar_keys, holomorphic_basis = kernel_basis(
        expansions, list(range(len(expansions))), cusp=False
    )
    boundary_keys, cusp_basis = kernel_basis(
        expansions, list(range(len(expansions))), cusp=True
    )
    directions = [
        first_target_direction(
            monomials,
            expansions,
            minimum_a_power=minimum,
            include_terms=(minimum == 1),
        )
        for minimum in range(1, 6)
    ]

    # Independent normalizations internal to this script.
    aa = phi_minus2(2)
    bb = phi_zero(2)
    if [aa.get((0, r), 0) for r in (-1, 0, 1)] != [1, -2, 1]:
        raise AssertionError("phi_-2,1 q^0 normalization")
    if [bb.get((0, r), 0) for r in (-1, 0, 1)] != [1, 10, 1]:
        raise AssertionError("phi_0,1 q^0 normalization")

    # C4 norm: epsilon^T(3I-H+J/9)epsilon = 20.
    epsilon = [1, -1, 1, -1]
    h = [
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 0],
    ]
    gram_d = [
        [
            Fraction(3 * int(i == j) - h[i][j]) + Fraction(1, 9)
            for j in range(4)
        ]
        for i in range(4)
    ]
    norm_d_fraction = sum(
        Fraction(epsilon[i]) * gram_d[i][j] * epsilon[j]
        for i in range(4)
        for j in range(4)
    )
    norm_d = int(norm_d_fraction)
    if norm_d != 20:
        raise AssertionError(norm_d)

    return {
        "format": "wave124-c4-index70-jacobi-v1",
        "claim_label": "DERIVED_AND_NULL_BOUNDARY",
        "scope": (
            "Conditional one-variable C4 Jacobi reduction for a hypothetical "
            "srg(99,14,1,2), plus an exact full-level old-subspace audit."
        ),
        "frozen_inputs": FROZEN_INPUTS,
        "c4_marking": {
            "epsilon": [1, -1, 1, -1],
            "definition": "d=sum_i epsilon_i u_i",
            "sum_epsilon": 0,
            "membership": "d in M subset L",
            "norm_d": norm_d,
            "primitive_in_L": True,
            "primitivity_reason": (
                "If d=k*l with k>=2 and l in the even lattice L, then "
                "20=k^2*(an even positive integer), impossible."
            ),
            "K_marking": "b=sqrt(7)*d in K",
            "norm_b": 7 * norm_d,
            "K_index": INDEX_K,
            "divisibility_in_K": 7,
            "divisibility_reason": (
                "<sqrt(7)y,b>=7<y,d> for y in L*; primitivity of d makes "
                "the gcd of <y,d> equal to one."
            ),
            "L_partner_index": INDEX_L,
            "evaluation": "<sqrt(7)y,b>=7*sum_i epsilon_i*t_i",
        },
        "coefficient_selection": {
            "rows": coefficient_selection_rows(),
            "conclusion": (
                "For q exponents 7,8,9,10, coefficient r=28 exactly counts "
                "antipodal incidences with the chosen alternating C4 pattern."
            ),
            "why_exact": (
                "The verified profiles on norms 14,16,18,20 have only "
                "coordinates 0,+1,-1. The sum of four epsilon_i*t_i reaches "
                "four iff all four coordinates equal epsilon_i."
            ),
            "oriented_count_factor": 2,
            "rank28_lower_through_q9": 52812,
            "rank28_cap25_upper_target": 51975,
            "rank28_gap": 837,
            "rank30_lower_through_q10": 51315,
            "rank30_cap24_upper_target": 49896,
            "rank30_gap": 1419,
            "degree8_even_indicator": {
                "formula": "prod_{j=0}^3 (ell^2-j^2)/(16-j^2)",
                "coefficients_low_to_high": even_indicator_coefficients(),
                "domain": "ell in {-4,-3,...,4} on the verified unit shells",
                "value": "1 exactly when |ell|=4, otherwise 0",
                "theta_moment_weights": [22, 24, 26, 28, 30],
            },
        },
        "tight_frame": {
            "cycle_sign_matrix": "S=83I-13A+J",
            "entry_counts": {
                "diagonal_C4s_through_vertex": 84,
                "adjacent_C4s_through_edge_with_negative_sign": -12,
                "nonadjacent_unique_C4_with_positive_sign": 1,
            },
            "eigenvalue_on_minus4_space": 135,
            "u_frame_operator": "sum_i u_i*u_i^T=7I",
            "d_frame_operator": "sum_C d_C*d_C^T=945I",
            "coordinate_identity": "sum_C ell_C(t)^2=135*sum_i t_i^2",
            "K_second_moment": (
                "sum_r r^2*c_K(n,r)=13230*n*a_K(n), "
                "where a_K(n) counts norm-2n K vectors"
            ),
            "L_second_moment": (
                "sum_r r^2*c_L(n,r)=1890*n*a_L(n), "
                "where a_L(n) counts norm-2n L vectors"
            ),
            "forced_L_boundary_coefficient": {
                "coefficient": [10, 20],
                "value": 2079,
                "reason": (
                    "For fixed C, norm(x)=norm(d_C)=20 and <x,d_C>=20 "
                    "force x=d_C by Cauchy equality; equivalently this is "
                    "the elliptic translate of c_L(0,0)=2079."
                ),
            },
        },
        "fricke_pair": {
            "weight": WEIGHT,
            "character": "trivial (the discriminants 7^q and 7^(44-q) are squares)",
            "raw_formula": (
                "Psi_K(-1/(7*tau),z/(7*tau))="
                "-7^(qdisc/2)*tau^22*exp(20*pi*i*z^2/tau)*Psi_L(tau,z)"
            ),
            "K_index": INDEX_K,
            "L_index": INDEX_L,
            "not_fixed_index": True,
            "K_r_divisibility": 7,
            "compressed_elliptic_relation": (
                "Writing r=7s, s changes by 20*lambda and n changes by "
                "7*(s*lambda+10*lambda^2), so n mod 7 is preserved."
            ),
            "residue_sector_warning": (
                "The q^7 target is in the old residue-zero sector, whereas "
                "q^8,q^9,q^10 lie in three genuinely different sectors."
            ),
        },
        "full_level_basis_audit": {
            "space": "J_22,10(SL2Z), embedded in J_22,10(Gamma0(7))",
            "whole_level7_basis_constructed": False,
            "weak_ring_generators": [
                "E4",
                "E6",
                "A=phi_-2,1",
                "B=phi_0,1",
            ],
            "weak_monomial_count": len(monomials),
            "weak_monomials_E4_E6_A_B": [list(row) for row in monomials],
            "polar_constraint_count_in_expansion": len(polar_keys),
            "boundary_constraint_count_in_expansion": len(boundary_keys),
            "holomorphic_dimension": len(holomorphic_basis),
            "cusp_dimension": len(cusp_basis),
            "holomorphic_basis_monomial_coordinates": [
                primitive_integer_vector(vector) for vector in holomorphic_basis
            ],
            "cusp_basis_monomial_coordinates": [
                primitive_integer_vector(vector) for vector in cusp_basis
            ],
            "q_expansion_precision": QMAX,
            "polar_completeness_reason": (
                "For index 10, elliptic reduction takes r to |r|<=10. "
                "Negative discriminant then has n<r^2/40<=5/2, so q^10 "
                "contains every reduced polar orbit."
            ),
            "scalar_invisible_fricke_directions_by_A_power": directions,
        },
        "optimization_boundary": {
            "modularity_fricke_constants_and_scalar_specializations_bounded": False,
            "reason": (
                "The explicit A-divisible full-level Jacobi cusp direction "
                "and its Fricke old lift preserve constants and z=0 scalar "
                "theta specializations while changing c_K(7,28)."
            ),
            "second_moment_alone_bounded": False,
            "second_moment_reason": (
                "An A^2-divisible cusp direction, if recorded as existing "
                "above, vanishes through z^2 and still changes the old "
                "q^7,r=28 coefficient."
            ),
            "positivity_bounded": "UNKNOWN",
            "why_no_upper_certificate": (
                "The oldform direction has signed Fourier coefficients. "
                "It also introduces Fourier patterns forbidden by the graph's "
                "unit-shell coordinate support. Coefficientwise nonnegativity "
                "on both K and L, integrality, all forced support zeros, and "
                "the nonzero residue sectors have not been solved."
            ),
            "smallest_next_model": (
                "Use the five even Taylor moments through z^8 (weights "
                "22,24,26,28,30), the exact frame second moment, all "
                "unit-shell support zeros, and the K/L Fricke pairing. Only "
                "if that quotient remains feasible should one construct the "
                "full J_22,10(Gamma0(7)) theta-decomposition basis split by "
                "the four relevant K n mod 7 sectors."
            ),
        },
        "status": {
            "new_upper_bound": None,
            "rank28_excluded": False,
            "rank30_excluded": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    results = build_results()
    payload = canonical_json(results)
    if args.verify is not None:
        if args.verify.read_text(encoding="utf-8") != payload:
            raise SystemExit("verification mismatch")
    elif args.write is not None:
        args.write.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
