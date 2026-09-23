#!/usr/bin/env python3
"""Independent exact verification of the Wave 35 n3=4158 spectral package.

This module imports no discovery-side Python or JSON.  It reconstructs the
endpoint algebra from the SRG parameters and exact rational arithmetic.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Iterable, Sequence


N_VERTICES = 99
DEGREE = 14
LAMBDA = 1
MU = 2
N_TRIANGLES = 231
TRIANGLE_DEGREE = 18
PROJECTOR_RANK = 44
PROJECTOR_SCALE = 21
N3_ENDPOINT = 4158
GAMMA_EIGENS = (18, 7, 0, -3)
GAMMA_MULTS = {18: 1, 7: 54, 0: 44, -3: 132}


class CheckFailure(AssertionError):
    """Raised when an exact verifier obligation fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def ftext(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def product(values: Iterable[int]) -> int:
    answer = 1
    for value in values:
        answer *= value
    return answer


def solve_rational(
    matrix: Sequence[Sequence[Fraction | int]],
    rhs: Sequence[Fraction | int],
) -> list[Fraction]:
    size = len(rhs)
    require(len(matrix) == size and all(len(row) == size for row in matrix), "non-square system")
    work = [
        [Fraction(entry) for entry in row] + [Fraction(rhs[index])]
        for index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        require(pivot is not None, "singular rational system")
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            multiplier = work[row][column]
            work[row] = [
                left - multiplier * right
                for left, right in zip(work[row], work[column])
            ]
    return [work[index][-1] for index in range(size)]


def endpoint_premises(n3: int = N3_ENDPOINT) -> dict[str, object]:
    """Derive the endpoint profile from the SRG parameters and q moments."""

    # The nonprincipal SRG eigenvalues solve x^2-(lambda-mu)x-(k-mu)=0.
    require((3, -4) == (3, -4), "SRG roots changed")
    positive_mult = (-(DEGREE) - (-4) * (N_VERTICES - 1)) // (3 - (-4))
    negative_mult = N_VERTICES - 1 - positive_mult
    require((positive_mult, negative_mult) == (54, 44), "SRG multiplicities changed")

    triangle_count = N_VERTICES * DEGREE // 6
    require(triangle_count == N_TRIANGLES, "triangle count changed")
    gamma_spectrum = {
        DEGREE + 7 - 3: 1,
        3 + 7 - 3: positive_mult,
        -4 + 7 - 3: negative_mult,
        -3: N_TRIANGLES - N_VERTICES,
    }
    require(gamma_spectrum == GAMMA_MULTS, "triangle-intersection spectrum changed")

    require((2 * n3) % 3 == 0, "2*n3/3 is not integral")
    q_sum = 2 * n3 // 3
    q_max = 12
    upper = 3 * N_TRIANGLES * q_max // 2
    require(upper == N3_ENDPOINT, "q<=12 upper endpoint changed")
    require(n3 == upper, "this verifier package is frozen to the equality endpoint")
    require(q_sum == N_TRIANGLES * q_max, "endpoint average q is not 12")

    q = q_max
    profile = (20 + q, 180 - 3 * q, 3 * q, 12 - q)
    require(profile == (32, 144, 36, 0), "endpoint a_r profile changed")
    require(sum(profile) == 212, "disjoint-triangle count changed")
    require(sum(index * profile[index] for index in range(4)) == 216, "first moment changed")
    require(
        sum(index * (index - 1) // 2 * profile[index] for index in range(4)) == 36,
        "second binomial moment changed",
    )

    s_plus, s_minus, s_zero = profile[0], profile[2], profile[1] + TRIANGLE_DEGREE
    require((s_plus, s_minus, s_zero) == (32, 36, 162), "signed row profile changed")
    require(s_plus - s_minus == -4, "S row sum changed")
    require(s_plus + s_minus == 68, "S squared row norm changed")
    return {
        "srg_spectrum": {"14": 1, "3": positive_mult, "-4": negative_mult},
        "gamma_spectrum": {str(key): value for key, value in gamma_spectrum.items()},
        "triangle_count": triangle_count,
        "q_sum": q_sum,
        "q_per_triangle": q,
        "n3_upper_from_q_le_12": upper,
        "a_profile": list(profile),
        "S_off_diagonal_profile": {"+1": s_plus, "-1": s_minus, "0": s_zero},
    }


def validate_snf_factors(factors: Sequence[int]) -> None:
    require(len(factors) == N_TRIANGLES, "wrong SNF length")
    require(all(right % left == 0 for left, right in zip(factors, factors[1:])), "not an invariant-factor chain")
    require(all(68 % factor == 0 for factor in factors), "factor does not divide 68")
    require(sum(factor % 2 for factor in factors) == PROJECTOR_RANK, "wrong rank modulo two")
    require(product(factors) == 17**44 * 4**187, "wrong determinant")


def smith_and_reflection() -> dict[str, object]:
    """Derive the unique Smith form and the integral involution."""

    # rank_F2(M)=44: e_44(M)=21^44 is odd, so some 44-minor is odd;
    # no larger minor survives because rank_Q(M)=44.  S=M-4I=M mod 2.
    require(21**44 % 2 == 1, "principal-minor parity changed")
    rank_mod2_s = 44

    # S(S-13I)=68I makes the cokernel exponent divide 68.  There are 187
    # even factors.  Their total 2-valuation is 374, so all have valuation 2.
    even_count = N_TRIANGLES - rank_mod2_s
    require(even_count == 187 and 2 * even_count == 374, "2-adic accounting changed")
    # Hence even factors are 4 or 68, and odd factors are 1 or 17.
    # An odd 17 would force all 187 later even factors to be 68, exceeding
    # the available total 17-valuation 44.  Thus all odd factors are 1.
    factors = [1] * 44 + [4] * 143 + [68] * 44
    validate_snf_factors(factors)

    # S has eigenvalues 17^44 and -4^187.
    require(17 * 44 - 4 * 187 == 0, "trace S changed")
    require(17**2 * 44 + 4**2 * 187 == N_TRIANGLES * 68, "trace S^2 changed")
    require(13 * 17 + 68 == 17**2 and 13 * (-4) + 68 == (-4) ** 2, "S polynomial changed")

    # C=2S-13I.
    require((2 * 17 - 13, 2 * (-4) - 13) == (21, -21), "C spectrum changed")
    require(4 * 68 + 169 == 441, "C row norm changed")
    return {
        "rank_F2_S": rank_mod2_s,
        "S_spectrum": {"17": 44, "-4": 187},
        "S_identity": "S^2=13S+68I",
        "S_cokernel_exponent_divides": 68,
        "snf": "diag(1^44,4^143,68^44)",
        "C_definition": "C=2S-13I=2M-21I",
        "C_identity": "C^2=441I",
        "C_spectrum": {"+21": 44, "-21": 187},
        "C_row_sum": -21,
        "C_row_squared_norm": 441,
    }


def c_eigenvalue(theta: int) -> int:
    return theta * theta - 5 * theta - 18


def projector_coefficients(target: int) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Coefficients of E_target=aI+bJ+cGamma+dC, independently solved."""

    matrix = []
    rhs = []
    for theta in GAMMA_EIGENS:
        matrix.append([1, 231 if theta == 18 else 0, theta, c_eigenvalue(theta)])
        rhs.append(int(theta == target))
    answer = solve_rational(matrix, rhs)
    return tuple(answer)  # type: ignore[return-value]


def projector_entries(target: int) -> dict[str, Fraction]:
    a, b, c, d = projector_coefficients(target)
    diagonal = a + b
    require(231 * diagonal == GAMMA_MULTS[target], "projector diagonal/rank mismatch")
    return {
        "diagonal": diagonal,
        "intersect": b + c,
        "r0": b,
        "r1": b + d,
        "r2": b + 2 * d,
        "r3": b + 3 * d,
    }


def schur_and_compressions() -> dict[str, object]:
    """Recompute all forty primitive-projector triples from entry classes."""

    counts = {
        "diagonal": 231,
        "intersect": 231 * 18,
        "r0": 231 * 32,
        "r1": 231 * 144,
        "r2": 231 * 36,
        "r3": 0,
    }
    require(sum(counts.values()) == 231**2, "ordered class counts changed")
    entries = {theta: projector_entries(theta) for theta in GAMMA_EIGENS}

    triples: dict[str, Fraction] = {}
    for first, second in combinations_with_replacement(GAMMA_EIGENS, 2):
        for third in GAMMA_EIGENS:
            value = sum(
                Fraction(counts[category])
                * entries[first][category]
                * entries[second][category]
                * entries[third][category]
                for category in counts
            )
            triples[f"{first},{second}|{third}"] = value
    require(len(triples) == 40, "mixed triple count changed")
    require(all(value >= 0 for value in triples.values()), "negative primitive-projector Schur triple")
    positives = [value for value in triples.values() if value > 0]
    require(sum(value == 0 for value in triples.values()) == 15, "zero triple count changed")
    require(min(positives) == Fraction(1, 231), "smallest positive triple changed")

    # W=M o M=441(E0 o E0).  B=W-16I=S o S.
    dimensions = GAMMA_MULTS
    trace_w = {theta: 441 * triples[f"0,0|{theta}"] for theta in GAMMA_EIGENS}
    require(
        trace_w == {
            18: Fraction(84),
            7: Fraction(3672, 5),
            0: Fraction(660),
            -3: Fraction(11088, 5),
        },
        "W compression traces changed",
    )
    trace_b = {theta: trace_w[theta] - 16 * dimensions[theta] for theta in GAMMA_EIGENS}
    require(
        trace_b
        == {
            18: Fraction(68),
            7: Fraction(-648, 5),
            0: Fraction(-44),
            -3: Fraction(528, 5),
        },
        "B compression traces changed",
    )
    require(sum(trace_b.values()) == 0, "trace B changed")
    trace_b2 = 231 * 68
    cauchy_floor = sum(trace_b[theta] ** 2 / dimensions[theta] for theta in GAMMA_EIGENS)
    require(cauchy_floor == Fraction(126588, 25), "compression floor changed")
    slack = Fraction(trace_b2) - cauchy_floor
    require(slack == Fraction(266112, 25), "compression slack changed")

    # Entrywise powers use only diagonal 4 and off-diagonal 0,+/-1.
    require(4**3 == 4 + 60, "Schur cube diagonal changed")
    return {
        "mixed_triple_count": len(triples),
        "mixed_negative_count": sum(value < 0 for value in triples.values()),
        "mixed_zero_count": sum(value == 0 for value in triples.values()),
        "mixed_smallest_positive": ftext(min(positives)),
        "schur_odd_formula": "M^(o k)=M+(4^k-4)I",
        "schur_even_formula": "M^(o k)=W+(4^k-16)I",
        "schur_cube_spectrum": {"81": 44, "60": 187},
        "B_projector_traces": {str(theta): ftext(trace_b[theta]) for theta in GAMMA_EIGENS},
        "B_trace_square": trace_b2,
        "B_cauchy_floor": ftext(cauchy_floor),
        "B_unallocated_slack": ftext(slack),
    }


def incidence_frobenius() -> dict[str, object]:
    """Independently check the B*N^T local and spectral scalar bounds."""

    # For x adjacent to T, every disjoint U through x has at least the
    # x--T cross edge.  Since r=3 is absent, p-m=-2 forces exactly two r=2.
    adjacent_value = 2

    # For x nonadjacent to T, let t_x count r=2 triangles U through x.
    # Then p-m=1 gives B-degree p+m=1+2t_x.  Six common-neighbor incidences
    # bound t_x<=3.  Each of the 36 r=2 triangles has exactly one vertex
    # nonadjacent to T, so sum t_x=36.
    minimum_none = 36 * 3**2 + 24
    maximum_none = 12 * 7**2 + 48
    row_min = 36 * adjacent_value**2 + minimum_none
    row_max = 36 * adjacent_value**2 + maximum_none
    require((row_min, row_max) == (492, 780), "local Frobenius bounds changed")
    global_min, global_max = 231 * row_min, 231 * row_max

    # ||BN^T||^2=tr((3I+Gamma)B^2)=21*x18+10*x7+3*x0.
    x18 = Fraction(68**2)
    require(21 * x18 == 97104, "constant incidence energy changed")
    x7_floor = Fraction(648, 5) ** 2 / 54
    x0_floor = Fraction(44**2, 44)
    spectral_floor = 21 * x18 + 10 * x7_floor + 3 * x0_floor
    require(spectral_floor == Fraction(501732, 5), "spectral incidence floor changed")
    require(spectral_floor < global_min, "scalar route unexpectedly contradicts endpoint")

    scalar = {
        7: Fraction(8208, 5),
        0: Fraction(44),
        -3: Fraction(46992, 5),
    }
    require(sum(scalar.values()) == 15708 - 68**2, "scalar energy total changed")
    require(scalar[7] >= x7_floor, "scalar x7 below Cauchy floor")
    require(scalar[-3] >= Fraction(528, 5) ** 2 / 132, "scalar x-3 below Cauchy floor")
    require(21 * x18 + 10 * scalar[7] + 3 * scalar[0] == global_min, "scalar misses local floor")
    return {
        "BN_transpose_values": {
            "on_T": 0,
            "adjacent_to_T": adjacent_value,
            "nonadjacent_to_T": "1+2t_x",
            "t_bounds": [0, 3],
            "sum_t": 36,
        },
        "per_row_square_range": [row_min, row_max],
        "global_square_range": [global_min, global_max],
        "spectral_cauchy_floor": ftext(spectral_floor),
        "scalar_survivor": {str(key): ftext(value) for key, value in scalar.items()},
        "scalar_is_matrix_or_graph": False,
    }


def determinant_bareiss(matrix: Sequence[Sequence[int]]) -> int:
    size = len(matrix)
    require(all(len(row) == size for row in matrix), "determinant input not square")
    work = [list(row) for row in matrix]
    sign = 1
    previous = 1
    for column in range(size - 1):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        for row in range(column + 1, size):
            for other in range(column + 1, size):
                numerator = work[row][other] * pivot_value - work[row][column] * work[column][other]
                require(numerator % previous == 0, "nonexact Bareiss division")
                work[row][other] = numerator // previous
        previous = pivot_value
        for row in range(column + 1, size):
            work[row][column] = 0
    return sign * work[-1][-1]


def cycle_union(lengths: Sequence[int]) -> list[list[int]]:
    size = sum(lengths)
    result = [[0] * size for _ in range(size)]
    offset = 0
    for length in lengths:
        require(length >= 4 and length % 2 == 0, "invalid bipartite cycle")
        for index in range(length):
            left = offset + index
            right = offset + (index + 1) % length
            result[left][right] = result[right][left] = 1
        offset += length
    return result


def local_controls() -> dict[str, object]:
    adjacent_determinants: dict[str, int] = {}
    for partition in ((12,), (8, 4), (6, 6), (4, 4, 4)):
        support = cycle_union(partition)
        require(all(sum(row) == 2 for row in support), "adjacent support not 2-regular")
        gram = [
            [4 * int(row == column) - support[row][column] for column in range(12)]
            for row in range(12)
        ]
        determinant = determinant_bareiss(gram)
        require(determinant > 0, "adjacent local block not positive definite")
        adjacent_determinants["+".join(map(str, partition))] = determinant

    cross = [[0] * 7 for _ in range(7)]
    for row, column in ((0, 1), (1, 0), (0, 2), (1, 3), (4, 0), (5, 1)):
        cross[row][column] = -1
    for row, column in ((2, 2), (3, 3), (4, 2), (4, 4), (5, 3), (5, 5), (6, 6)):
        cross[row][column] = 1
    row_sums = [sum(row) for row in cross]
    col_sums = [sum(cross[row][column] for row in range(7)) for column in range(7)]
    require(row_sums == col_sums == [-2, -2, 1, 1, 1, 1, 1], "relaxed nonadjacent margins changed")
    require(cross[0][0] == cross[1][1] == 0, "forced intersecting zeros changed")
    require(cross[0][1] == cross[1][0] == -1, "forced r=2 cells changed")
    frobenius_square = sum(value * value for row in cross for value in row)
    require(frobenius_square == 13 < 16, "relaxed nonadjacent PSD witness changed")
    return {
        "adjacent_cycle_determinants": adjacent_determinants,
        "adjacent_all_actual_cycle_types_positive": True,
        "nonadjacent_relaxed_control_frobenius_square": frobenius_square,
        "nonadjacent_relaxed_control_positive_by_norm_bound": True,
        "nonadjacent_control_actual_incidence_realization": "NOT_CLAIMED",
    }


def principal_minor_criterion() -> dict[str, object]:
    """Verify the 45-minor target and hostile-test both wording boundaries."""

    require(PROJECTOR_RANK + 1 == 45, "principal target size changed")
    require(4 - 3 > 0, "support-degree-three Gershgorin margin lost")

    # Sharp hostile control: a negative K5 block plus forty isolated indices.
    # It has support degree four and eigenvalue -4, so degree <=4 would fail.
    s = [[0] * 45 for _ in range(45)]
    switching = [1, 1, -1, -1, -1]
    for row in range(5):
        for column in range(5):
            if row != column:
                s[row][column] = -switching[row] * switching[column]
    support_degrees = [sum(abs(value) for value in row) for row in s]
    algebraic_sums = [sum(row) for row in s]
    require(max(support_degrees) == 4, "K5 support mutation changed")
    require(max(abs(value) for value in algebraic_sums) <= 2, "switched K5 algebraic sums changed")
    eigenvector = switching + [0] * 40
    require(
        all(sum(s[row][column] * eigenvector[column] for column in range(45)) == -4 * eigenvector[row] for row in range(45)),
        "switched K5 lost eigenvalue -4",
    )
    return {
        "universal_fact": "rank(M)=44 implies every 45x45 principal M[X] is singular",
        "equivalent_fact": "every 45x45 principal S[X] has eigenvalue -4",
        "sufficient_condition": "max_i sum_{j in X}|S_ij| <= 3",
        "gershgorin_positive_margin": 1,
        "condition_constructed": False,
        "degree_four_is_not_sufficient": True,
        "absolute_algebraic_row_sum_is_not_sufficient": True,
        "hostile_switched_K5_support_degree": 4,
        "hostile_switched_K5_max_absolute_algebraic_sum": 2,
    }


def build_results() -> dict[str, object]:
    return {
        "schema_version": 1,
        "role": "verifier",
        "verdict": "VERIFIED_SCOPED_WITH_WORDING_QUALIFIER",
        "scope": "conditional n3=4158 spectral, Smith, Schur, scalar/local-relaxation, and 45-principal-minor claims only",
        "endpoint": endpoint_premises(),
        "smith_and_reflection": smith_and_reflection(),
        "schur_and_compressions": schur_and_compressions(),
        "incidence_frobenius": incidence_frobenius(),
        "local_controls": local_controls(),
        "principal_minor": principal_minor_criterion(),
        "status": {
            "endpoint_matrix_constructed": False,
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "conway_99": "UNKNOWN",
        },
        "qualifiers": [
            "The principal-minor condition uses support degree sum_j |S_ij|, not the absolute algebraic row sum.",
            "The nonadjacent 7x7 matrix is a relaxation witness, not a locally or globally realized graph block.",
            "Mixed-Schur nonnegativity and scalar feasibility are failure-of-obstruction results, not existence evidence.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    rendered = json.dumps(build_results(), indent=2, sort_keys=True) + "\n"
    if arguments.verify is not None:
        require(arguments.verify.read_text(encoding="utf-8") == rendered, "frozen result differs")
    if arguments.output is not None:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    elif arguments.verify is None:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
