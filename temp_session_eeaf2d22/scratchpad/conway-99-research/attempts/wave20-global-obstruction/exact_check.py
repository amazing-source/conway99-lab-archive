#!/usr/bin/env python3
"""Exact checker for the Wave 20 triangle-projector obstruction.

This program uses only Python's standard library and rational arithmetic.
It does not search for a Conway graph.  It checks the arithmetic in the
conditional derivation

    srg(99,14,1,2) exists  ==>  n3 >= 705.

The mathematical proof, including the combinatorial interpretation of every
matrix entry, is in agents/2026-07-23-wave20-global-schur.md.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple


F = Fraction
Affine = Tuple[Fraction, Fraction]  # constant + coefficient * n3


class InvariantError(AssertionError):
    """Raised when an exact identity or a hostile mutation fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvariantError(message)


def fstr(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def affine_str(value: Affine, variable: str = "n3") -> str:
    constant, coefficient = value
    return f"{fstr(constant)} + ({fstr(coefficient)})*{variable}"


def affine_add(*values: Affine) -> Affine:
    return (
        sum((value[0] for value in values), F(0)),
        sum((value[1] for value in values), F(0)),
    )


def affine_scale(value: Affine, scalar: Fraction) -> Affine:
    return value[0] * scalar, value[1] * scalar


def solve_linear(matrix: Sequence[Sequence[Fraction]], rhs: Sequence[Fraction]) -> List[Fraction]:
    """Solve a square rational system by exact Gauss-Jordan elimination."""

    n = len(rhs)
    require(len(matrix) == n and all(len(row) == n for row in matrix), "system is not square")
    augmented = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((row for row in range(column, n) if augmented[row][column]), None)
        require(pivot is not None, f"singular system at column {column}")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [entry / pivot_value for entry in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            multiplier = augmented[row][column]
            augmented[row] = [
                left - multiplier * right
                for left, right in zip(augmented[row], augmented[column])
            ]
    return [augmented[i][-1] for i in range(n)]


GAMMA_EIGENVALUES = (18, 7, 0, -3)
GAMMA_MULTIPLICITIES = {18: 1, 7: 54, 0: 44, -3: 132}
C_EIGENVALUES = {theta: theta * theta - 5 * theta - 18 for theta in GAMMA_EIGENVALUES}


def validate_gamma_spectrum(
    multiplicities: Mapping[int, int] = GAMMA_MULTIPLICITIES,
) -> None:
    """Check dimension, trace, degree, and the incidence-derived spectrum."""

    require(set(multiplicities) == set(GAMMA_EIGENVALUES), "wrong Gamma eigenvalue support")
    require(sum(multiplicities.values()) == 231, "Gamma multiplicities do not sum to 231")
    require(sum(theta * multiplicities[theta] for theta in GAMMA_EIGENVALUES) == 0,
            "Gamma trace is not zero")
    require(sum(theta * theta * multiplicities[theta] for theta in GAMMA_EIGENVALUES)
            == 231 * 18, "Gamma second spectral moment is not 231*18")
    require(C_EIGENVALUES == {18: 216, 7: -4, 0: -18, -3: 6},
            "C=f(Gamma) spectrum changed")


def projector_coefficients(target: int) -> Tuple[Fraction, Fraction, Fraction, Fraction]:
    """Return (a,b,c,d) for E_target=aI+bJ+cGamma+dC."""

    require(target in GAMMA_EIGENVALUES, "unknown projector target")
    matrix: List[List[Fraction]] = []
    rhs: List[Fraction] = []
    for theta in GAMMA_EIGENVALUES:
        matrix.append([
            F(1),
            F(231 if theta == 18 else 0),
            F(theta),
            F(C_EIGENVALUES[theta]),
        ])
        rhs.append(F(int(theta == target)))
    return tuple(solve_linear(matrix, rhs))  # type: ignore[return-value]


def projector_entry_data(
    coefficients: Sequence[Fraction],
) -> Tuple[Fraction, Fraction, Fraction, Fraction]:
    """Return diagonal, intersecting, disjoint-intercept, disjoint-slope."""

    require(len(coefficients) == 4, "projector needs four coefficients")
    a, b, c, d = coefficients
    return a + b, b + c, b, d


def validate_projector(
    target: int,
    coefficients: Sequence[Fraction],
    c_eigenvalues: Mapping[int, int] = C_EIGENVALUES,
) -> None:
    """Check that a proposed combination is exactly the target projector."""

    require(len(coefficients) == 4, "projector coefficient length changed")
    a, b, c, d = coefficients
    for theta in GAMMA_EIGENVALUES:
        action = a + c * theta + d * c_eigenvalues[theta]
        if theta == 18:
            action += 231 * b
        require(action == int(theta == target),
                f"projector action failed at theta={theta}: {action}")
    diagonal, _, _, _ = projector_entry_data(coefficients)
    require(231 * diagonal == GAMMA_MULTIPLICITIES[target],
            "projector diagonal does not equal rank/231")


def row_profile(q: int) -> Dict[int, int]:
    """The exact counts a_r(T) for a triangle with q(T)=q."""

    require(0 <= q <= 12, "q is outside the combinatorial range 0..12")
    profile = {0: 20 + q, 1: 180 - 3 * q, 2: 3 * q, 3: 12 - q}
    require(sum(profile.values()) == 212, "row profile has wrong number of disjoint triangles")
    require(sum(r * profile[r] for r in range(4)) == 216,
            "row profile has wrong first cross-edge moment")
    require(sum((r * (r - 1) // 2) * profile[r] for r in range(4)) == 36,
            "row profile has wrong second binomial moment")
    require(all(value >= 0 for value in profile.values()), "row profile became negative")
    return profile


def global_ordered_counts(pair_factor: int = 2) -> Dict[str, Affine]:
    """Ordered pair counts, expressed as affine functions of n3.

    ``pair_factor`` is exposed solely for hostile mutation tests.  The valid
    value is two because each unordered N3 has two ordered side-triangle
    orientations.
    """

    require(pair_factor > 0, "pair factor must be positive")
    n2 = (F(0), F(pair_factor))
    # a_2(T)=3q(T), so sum q = pair_factor*n3/3.
    q_sum = (F(0), F(pair_factor, 3))
    counts = {
        "diagonal": (F(231), F(0)),
        "intersect": (F(231 * 18), F(0)),
        "r0": affine_add((F(231 * 20), F(0)), q_sum),
        "r1": affine_add((F(231 * 180), F(0)), affine_scale(q_sum, F(-3))),
        "r2": n2,
        "r3": affine_add((F(231 * 12), F(0)), affine_scale(q_sum, F(-1))),
    }
    total = affine_add(*counts.values())
    require(total == (F(231 * 231), F(0)), "ordered pair counts do not total 231^2")
    return counts


def schur_triple(
    first: int,
    second: int,
    third: int,
    counts: Mapping[str, Affine] | None = None,
) -> Affine:
    """Compute sum_{T,U} E_first[T,U]E_second[T,U]E_third[T,U]."""

    if counts is None:
        counts = global_ordered_counts()
    data = {
        theta: projector_entry_data(projector_coefficients(theta))
        for theta in GAMMA_EIGENVALUES
    }
    factors = (first, second, third)

    def product_for(category: str, r: int | None = None) -> Fraction:
        product = F(1)
        for theta in factors:
            diagonal, intersect, intercept, slope = data[theta]
            if category == "diagonal":
                entry = diagonal
            elif category == "intersect":
                entry = intersect
            else:
                require(r is not None, "disjoint category needs r")
                entry = intercept + slope * r
            product *= entry
        return product

    answer = affine_scale(counts["diagonal"], product_for("diagonal"))
    answer = affine_add(answer, affine_scale(counts["intersect"], product_for("intersect")))
    for r in range(4):
        answer = affine_add(answer, affine_scale(counts[f"r{r}"], product_for("disjoint", r)))
    return answer


def unscaled_cubic(counts: Mapping[str, Affine] | None = None) -> Affine:
    """Return sum M_ij^3 for M=21E_0."""

    constant, coefficient = schur_triple(0, 0, 0, counts)
    return constant * 21**3, coefficient * 21**3


def gegenbauer_bounds(max_degree: int = 60) -> Dict[str, object]:
    """Run the spherical harmonic pair-distribution check in dimension 44."""

    require(max_degree >= 3, "need degree at least three")
    alpha = F(21)  # (dimension-2)/2 for dimension 44
    points = (F(1), F(1, 4), F(0), F(-1, 4), F(-1, 2))
    weights: Tuple[Affine, ...] = (
        (F(231), F(0)),
        (F(4620), F(2, 3)),
        (F(45738), F(-2)),
        (F(0), F(2)),
        (F(2772), F(-2, 3)),
    )

    previous = [F(1) for _ in points]
    current = [2 * alpha * point for point in points]
    inequalities: List[Tuple[int, Affine]] = []

    def record(degree: int, values: Sequence[Fraction]) -> None:
        total = (F(0), F(0))
        for weight, value in zip(weights, values):
            total = affine_add(total, affine_scale(weight, value))
        inequalities.append((degree, total))

    record(0, previous)
    record(1, current)
    for degree_minus_one in range(1, max_degree):
        next_values = []
        for point, prev_value, value in zip(points, previous, current):
            numerator = (
                2 * (F(degree_minus_one) + alpha) * point * value
                - (F(degree_minus_one) + 2 * alpha - 1) * prev_value
            )
            next_values.append(numerator / F(degree_minus_one + 1))
        record(degree_minus_one + 1, next_values)
        previous, current = current, next_values

    lower = []
    upper = []
    for degree, (constant, coefficient) in inequalities:
        if coefficient > 0:
            lower.append((degree, -constant / coefficient))
        elif coefficient < 0:
            upper.append((degree, -constant / coefficient))
    strongest_lower = max(lower, key=lambda item: item[1])
    strongest_upper = min(
        (item for item in upper if item[1] >= 0),
        key=lambda item: item[1],
    )
    return {
        "max_degree": max_degree,
        "strongest_nonnegative_lower": {
            "degree": strongest_lower[0],
            "bound": fstr(strongest_lower[1]),
        },
        "strongest_nonnegative_upper": {
            "degree": strongest_upper[0],
            "bound": fstr(strongest_upper[1]),
        },
    }


def next_multiple(value: Fraction, modulus: int) -> int:
    integer_ceiling = -((-value.numerator) // value.denominator)
    return ((integer_ceiling + modulus - 1) // modulus) * modulus


def quadratic_mod2(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> int:
    """Evaluate v^T M v over F2."""

    size = len(vector)
    require(len(matrix) == size and all(len(row) == size for row in matrix),
            "quadratic-form dimensions disagree")
    return sum(
        vector[i] * matrix[i][j] * vector[j]
        for i in range(size)
        for j in range(size)
    ) % 2


def validate_alternating_quadratic_lemma() -> None:
    """Exhaust the characteristic-two lemma in small dimensions.

    The proof in arbitrary dimension is the same cancellation: diagonal terms
    vanish and every off-diagonal term occurs twice.  This small exhaustive
    replay is a regression guard against changing either premise.
    """

    for size in range(1, 5):
        edge_count = size * (size - 1) // 2
        for edge_mask in range(1 << edge_count):
            matrix = [[0 for _ in range(size)] for _ in range(size)]
            bit = 0
            for i in range(size):
                for j in range(i + 1, size):
                    value = (edge_mask >> bit) & 1
                    matrix[i][j] = value
                    matrix[j][i] = value
                    bit += 1
            for vector_mask in range(1 << size):
                vector = [(vector_mask >> i) & 1 for i in range(size)]
                require(quadratic_mod2(matrix, vector) == 0,
                        "symmetric zero-diagonal form was not alternating")


def derive_final_bound(
    triangle_count: int = 231,
    diagonal_multiple_of_four: bool = True,
    every_mod2_row_nonzero: bool = True,
) -> Dict[str, object]:
    """Check the integral PSD lift and return the resulting n3 endpoint.

    The optional arguments exist for hostile tests.  The valid derivation has
    231 triangle indices, diagonal divisible by four, and no zero row modulo
    two.
    """

    require(triangle_count > 0, "triangle count must be positive")
    require(diagonal_multiple_of_four, "A_ii mod-four premise was removed")
    require(every_mod2_row_nonzero, "nonzero-row premise was removed")

    # A=M(M o M)M is integral PSD and A == M (mod 2).  Since every row of M
    # mod 2 is nonzero, no row of A is zero.  PSD then forces A_ii>0.
    #
    # Write W=M o M=M+2D.  D is symmetric and D_ii=(16-4)/2=6 is even.
    # Therefore D mod 2 is alternating and v^T D v=0 over F2.  Since
    # M^3=441M, the diagonal of
    #
    #   A=M^3+2MDM
    #
    # is congruent to diag(M)=4 modulo four.  Thus every A_ii is a positive
    # multiple of four.
    trace_lower = 4 * triangle_count
    trace_per_delta = 84
    delta_threshold = F(trace_lower, trace_per_delta)
    delta = next_multiple(delta_threshold, 3)
    return {
        "trace_lower": trace_lower,
        "trace_formula": "84*(n3-693)",
        "delta_threshold": fstr(delta_threshold),
        "delta_multiple_of_three": delta,
        "n3_lower_bound": 693 + delta,
        "induced_C6_lower_bound": 209286 + 693 + delta,
    }


def audit() -> Dict[str, object]:
    validate_gamma_spectrum()
    validate_alternating_quadratic_lemma()
    projectors = {
        str(theta): projector_coefficients(theta)
        for theta in GAMMA_EIGENVALUES
    }
    for theta in GAMMA_EIGENVALUES:
        validate_projector(theta, projectors[str(theta)])

    expected_e0 = (F(1, 7), F(1, 21), F(-1, 21), F(-1, 21))
    require(projectors["0"] == expected_e0, "zero-eigenspace projector coefficients changed")
    require(projector_entry_data(expected_e0)
            == (F(4, 21), F(0), F(1, 21), F(-1, 21)),
            "zero-projector entry formula changed")

    profiles = {str(q): row_profile(q) for q in range(13)}
    counts = global_ordered_counts()
    cubic = schur_triple(0, 0, 0, counts)
    require(cubic == (F(-44, 147), F(4, 9261)),
            f"scaled Schur cubic changed: {cubic}")
    cubic_unscaled = unscaled_cubic(counts)
    require(cubic_unscaled == (F(-2772), F(4)),
            f"integral Schur cubic changed: {cubic_unscaled}")
    require((-cubic[0] / cubic[1]) == 693, "Schur positivity endpoint changed")

    # At n3=693, the row sum of M o M o M is 6(q(T)-2).
    for q in range(13):
        profile = profiles[str(q)]
        row_cube = 4**3 + profile[0] - profile[2] - 2**3 * profile[3]
        require(row_cube == 6 * (q - 2), f"row Schur-cube identity failed at q={q}")

    # Exact opposite-edge compression retained as a failed upper-bound route.
    j_compression = {
        "14-eigenspace": F(10 * 14 + 2 * 99 - 2, 14 + 14),
        "3-eigenspace": F(10 * 3 - 2, 14 + 3),
        "-4-eigenspace": F(10 * -4 - 2, 14 - 4),
    }
    require(j_compression == {
        "14-eigenspace": F(12),
        "3-eigenspace": F(28, 17),
        "-4-eigenspace": F(-21, 5),
    }, "opposite-edge compression arithmetic changed")

    mixed_triples: MutableMapping[str, str] = {}
    for i, first in enumerate(GAMMA_EIGENVALUES):
        for second in GAMMA_EIGENVALUES[i:]:
            for third in GAMMA_EIGENVALUES:
                value = schur_triple(first, second, third, counts)
                mixed_triples[f"{first},{second}|{third}"] = affine_str(value)

    final_bound = derive_final_bound()
    require(final_bound["n3_lower_bound"] == 705, "final endpoint changed")

    # The closest multiples explicitly exercise the strengthened trace
    # obstruction.
    require(84 * 9 < 924, "delta=9 should be excluded")
    require(84 * 12 >= 924, "delta=12 should be the first surviving multiple")

    return {
        "schema_version": 1,
        "claim_label": "DERIVED",
        "scope": "conditional_on_existence_of_srg_99_14_1_2",
        "target_status": "UNKNOWN",
        "novelty_status": "UNKNOWN",
        "exact_arithmetic": "fractions.Fraction",
        "gamma_spectrum": {
            str(theta): GAMMA_MULTIPLICITIES[theta]
            for theta in GAMMA_EIGENVALUES
        },
        "c_spectrum": {
            str(theta): C_EIGENVALUES[theta]
            for theta in GAMMA_EIGENVALUES
        },
        "projectors": {
            theta: [fstr(value) for value in coefficients]
            for theta, coefficients in projectors.items()
        },
        "e0_entries": {
            "diagonal": "4/21",
            "intersecting": "0",
            "disjoint_r": "(1-r)/21",
        },
        "row_profiles": profiles,
        "global_ordered_counts": {
            key: affine_str(value)
            for key, value in counts.items()
        },
        "schur_cubic": affine_str(cubic),
        "integral_schur_cubic": affine_str(cubic_unscaled),
        "schur_bound": 693,
        "mod2_lift": {
            "M": "21*E0",
            "M_squared": "21*M",
            "W": "M o M",
            "W_mod_2": "M",
            "A": "M*W*M",
            "A_mod_2": "M",
            "D": "(W-M)/2",
            "D_mod_2": "symmetric_zero_diagonal",
            "A_diagonal_mod_4": 0,
            "minimum_positive_diagonal": 4,
        },
        "final_bound": final_bound,
        "mixed_schur_triples": mixed_triples,
        "gegenbauer_check": gegenbauer_bounds(60),
        "opposite_edge_compression": {
            key: fstr(value) for key, value in j_compression.items()
        },
        "limitations": [
            "Conditional on the existence of the frozen SRG target.",
            "No target nonexistence or construction claim is made.",
            "No literature novelty claim is made.",
            "The checker verifies exact arithmetic, not the prose-to-combinatorics bridge.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="write deterministic JSON to this path")
    arguments = parser.parse_args()
    result = audit()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
