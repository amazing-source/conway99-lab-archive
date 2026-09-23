"""Independent exact verifier for the Wave 116 C4 Jacobi/theta assessment.

This module does not import or execute discovery code.  It reconstructs the
four-cycle projector, marking scalings, discriminant-sector arithmetic,
Poisson exponents, incidence normalization, and interpolation degree using
only exact integer/rational arithmetic.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def mat_scale(
    matrix: list[list[Fraction]], scalar: Fraction
) -> list[list[Fraction]]:
    return [[scalar * entry for entry in row] for row in matrix]


def mat_vec(
    matrix: list[list[Fraction]], vector: list[Fraction]
) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction())
        for row in matrix
    ]


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction())


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    answer = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column] != 0),
            None,
        )
        require(pivot is not None, "matrix is singular")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            answer *= -1
        value = work[column][column]
        answer *= value
        work[column] = [entry / value for entry in work[column]]
        for row in range(column + 1, len(work)):
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    a - multiplier * b
                    for a, b in zip(work[row], work[column])
                ]
    return answer


def inverse_times(
    matrix: list[list[Fraction]], vector: list[Fraction]
) -> list[Fraction]:
    size = len(matrix)
    work = [row[:] + [value] for row, value in zip(matrix, vector)]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column] != 0),
            None,
        )
        require(pivot is not None, "matrix is singular")
        work[column], work[pivot] = work[pivot], work[column]
        value = work[column][column]
        work[column] = [entry / value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    a - multiplier * b
                    for a, b in zip(work[row], work[column])
                ]
    return [work[row][-1] for row in range(size)]


def rank_mod_prime(matrix: list[list[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    rank = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = pow(work[rank][column], -1, prime)
        work[rank] = [(scale * entry) % prime for entry in work[rank]]
        for row in range(len(work)):
            if row == rank:
                continue
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    (a - multiplier * b) % prime
                    for a, b in zip(work[row], work[rank])
                ]
        rank += 1
    return rank


def frac(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def matrix_text(matrix: list[list[Fraction]]) -> list[list[str]]:
    return [[frac(entry) for entry in row] for row in matrix]


def cycle_projector() -> list[list[Fraction]]:
    adjacency = [
        [Fraction(int((row - column) % 4 in (1, 3))) for column in range(4)]
        for row in range(4)
    ]
    return [
        [
            (
                3 * int(row == column)
                - adjacency[row][column]
                + Fraction(1, 9)
            )
            / 7
            for column in range(4)
        ]
        for row in range(4)
    ]


def lagrange_indicator(target: int) -> list[Fraction]:
    """Coefficients, low to high, for delta_target on {-4,...,4}."""
    polynomial = [Fraction(1)]
    denominator = Fraction(1)
    for root in range(-4, 5):
        if root == target:
            continue
        next_polynomial = [Fraction(0)] * (len(polynomial) + 1)
        for degree, coefficient in enumerate(polynomial):
            next_polynomial[degree] -= root * coefficient
            next_polynomial[degree + 1] += coefficient
        polynomial = next_polynomial
        denominator *= target - root
    return [coefficient / denominator for coefficient in polynomial]


def polynomial_value(coefficients: list[Fraction], value: int) -> Fraction:
    answer = Fraction(0)
    for coefficient in reversed(coefficients):
        answer = answer * value + coefficient
    return answer


def build_results() -> dict[str, object]:
    projector = cycle_projector()
    modes = {
        "constant": ([1, 1, 1, 1], Fraction(13, 63)),
        "alternating": ([1, -1, 1, -1], Fraction(5, 7)),
        "zero_a": ([1, 0, -1, 0], Fraction(3, 7)),
        "zero_b": ([0, 1, 0, -1], Fraction(3, 7)),
    }
    for vector, eigenvalue in modes.values():
        rational_vector = [Fraction(entry) for entry in vector]
        require(
            mat_vec(projector, rational_vector)
            == [eigenvalue * entry for entry in rational_vector],
            "projector eigenpair failed",
        )
    projector_det = determinant(projector)
    require(projector_det == Fraction(65, 2401), "wrong projector determinant")

    gram_a = mat_scale(projector, Fraction(9))
    gram_l = mat_scale(projector, Fraction(63))
    gram_k = mat_scale(projector, Fraction(441))
    require(gram_l == mat_scale(gram_a, Fraction(7)), "wrong a-to-L scaling")
    require(gram_k == mat_scale(gram_l, Fraction(7)), "wrong L-to-K scaling")
    require(determinant(gram_l) == 426465, "wrong L marking determinant")
    require(determinant(gram_k) == 1023942465, "wrong K marking determinant")

    integral_l = [[int(entry) for entry in row] for row in gram_l]
    residue = [[entry % 7 for entry in row] for row in integral_l]
    residue_rank = rank_mod_prime(residue, 7)
    residue_det = int(determinant(gram_l)) % 7
    require(residue_rank == 4 and residue_det == 4, "four classes not independent")

    alternating = [1, -1, 1, -1]
    fourier_pattern = [Fraction(21 * entry) for entry in alternating]
    projected_norm = dot(
        fourier_pattern, inverse_times(gram_k, fourier_pattern)
    )
    require(projected_norm == Fraction(28, 5), "wrong projected Fourier norm")

    poisson_rows: list[dict[str, object]] = []
    for discriminant_length_q in range(2, 17, 2):
        determinant_exponent_k = 44 - discriminant_length_q
        # det(K)^(-1/2) * (7*tau)^22, with i^(-22)=-1.
        raw_exponent = Fraction(44 - determinant_exponent_k, 2)
        slash_exponent = raw_exponent - 11
        solved_scalar_exponent = -slash_exponent
        require(
            raw_exponent == Fraction(discriminant_length_q, 2),
            "wrong raw Poisson exponent",
        )
        poisson_rows.append(
            {
                "q": discriminant_length_q,
                "det_K_exponent": determinant_exponent_k,
                "raw_factor": f"-7^{frac(raw_exponent)}",
                "jacobi_slash_factor": f"-7^{frac(slash_exponent)}",
                "solved_scalar_factor": f"-7^{frac(solved_scalar_exponent)}",
            }
        )

    oriented_vectors = 5868
    cycles_per_vector = 18
    oriented_incidence = oriented_vectors * cycles_per_vector
    require(oriented_incidence == 105624, "wrong Wave 112 incidence import")
    require(oriented_incidence % 2 == 0, "antipodal halving failed")
    antipodal_incidence = oriented_incidence // 2
    cycle_count = 2079
    cap_per_cycle = 25
    cap_total = cycle_count * cap_per_cycle
    require(cap_total == 51975, "wrong cap total")
    require(antipodal_incidence == 52812, "wrong antipodal incidence")
    require(antipodal_incidence - cap_total == 837, "wrong contradiction gap")

    indicator_plus = lagrange_indicator(1)
    indicator_minus = lagrange_indicator(-1)
    domain = list(range(-4, 5))
    require(len(indicator_plus) - 1 == 8, "wrong interpolation degree")
    require(len(indicator_minus) - 1 == 8, "wrong interpolation degree")
    for value in domain:
        require(
            polynomial_value(indicator_plus, value)
            == int(value == 1),
            "plus indicator interpolation failed",
        )
        require(
            polynomial_value(indicator_minus, value)
            == int(value == -1),
            "minus indicator interpolation failed",
        )

    discriminant_margins = {
        str(n): frac(Fraction(2 * n) - projected_norm) for n in (7, 8, 9)
    }
    require(
        all(Fraction(value) > 0 for value in discriminant_margins.values()),
        "ordinary Jacobi support would exclude a target coefficient",
    )

    return {
        "format": "wave116-independent-verifier-v1",
        "claim_label": "VERIFIED",
        "verdict": "VERIFIED_WITH_CLARIFICATIONS",
        "conditional_scope": (
            "C4 coordinate Jacobi/theta strategy for a hypothetical "
            "srg(99,14,1,2), conditional on verified Waves 66, 71, and 112"
        ),
        "projector": {
            "matrix": matrix_text(projector),
            "eigenvalues_by_mode": {
                name: frac(eigenvalue) for name, (_, eigenvalue) in modes.items()
            },
            "determinant": frac(projector_det),
            "positive_definite": True,
        },
        "markings": {
            "naive_p": {
                "definition": "p_i=u_i/sqrt(7)",
                "gram": "E",
                "ordinary_index_justified": False,
                "actual_membership": "p_i not in K*",
                "reason": (
                    "K*=(1/sqrt(7))L, while [u_i]=alpha has order 9 in "
                    "M*/M and L/M=<3alpha>; hence u_i is not in L"
                ),
            },
            "dual_a": {
                "definition": "a_i=3u_i/sqrt(7)",
                "membership": "K*",
                "gram": matrix_text(gram_a),
                "seven_multiple_membership": "7a_i=3sqrt(7)u_i in K",
                "class_order": 7,
            },
            "L_v": {
                "definition": "v_i=3u_i",
                "membership": "L",
                "gram": matrix_text(gram_l),
                "eigenvalues": [13, 45, 27, 27],
                "determinant": int(determinant(gram_l)),
            },
            "K_g": {
                "definition": "g_i=3sqrt(7)u_i",
                "membership": "K",
                "gram": matrix_text(gram_k),
                "eigenvalues": [91, 315, 189, 189],
                "determinant": int(determinant(gram_k)),
                "matrix_index": "G_K/2",
            },
        },
        "discriminant_sector": {
            "pairing_numerator_mod_7": residue,
            "rank_mod_7": residue_rank,
            "determinant_mod_7": residue_det,
            "generated_subgroup": "(Z/7)^4",
            "subgroup_size": 7**4,
            "nondegenerate": True,
            "closure_warning": (
                "The four generated classes form a nondegenerate subgroup, "
                "but this alone does not erase or identify its orthogonal "
                "complement in K*/K; no closed 2401-component scalar system "
                "has been proved"
            ),
        },
        "cycle_sum": {
            "induced_C4_count": cycle_count,
            "common_gram_without_automorphisms": True,
            "dihedral_relabeling_preserves_index": True,
            "constant_coefficient": cycle_count,
            "z_zero_specialization": "2079*Theta_K",
            "index_discriminant_class_count": int(determinant(gram_k)),
        },
        "poisson_fricke": {
            "rank": 44,
            "weight": 22,
            "complex_phase": "i^(-22)=-1",
            "raw_formula": (
                "Phi_K(-1/(7tau),z/(7tau))="
                "-7^(q/2)tau^22 exp(pi*i*z^T G_L z/tau)Phi_L(tau,z)"
            ),
            "slash_formula": "Phi_K||W_7=-7^(q/2-11)Phi_L",
            "scalar_solved_formula": (
                "Theta_L=-7^(11-q/2)(Theta_K|_22 W_7)"
            ),
            "index_change": "G_K/2 to G_L/2=G_K/14",
            "rows": poisson_rows,
        },
        "incidence": {
            "fourier_pattern": [int(entry) for entry in fourier_pattern],
            "coordinate_pattern": alternating,
            "projected_norm": frac(projected_norm),
            "support_discriminant_margins_2n_minus_projected_norm": (
                discriminant_margins
            ),
            "coefficient_sum_counts": "antipodal C4 incidences",
            "oriented_count_factor": 2,
            "oriented_lower": oriented_incidence,
            "antipodal_lower": antipodal_incidence,
            "cap_25_total": cap_total,
            "gap": antipodal_incidence - cap_total,
        },
        "harmonic_interpolation": {
            "coordinate_domain": domain,
            "univariate_degree": 8,
            "four_coordinate_total_degree": 32,
            "indicator_plus_coefficients": [frac(value) for value in indicator_plus],
            "indicator_minus_coefficients": [
                frac(value) for value in indicator_minus
            ],
            "exact_on_norm_at_most_18": True,
            "harmonic_degrees_at_most": 32,
            "coefficientwise_positivity_retained": False,
            "clarification": (
                "The interpolation gives an exact finite weighted-theta "
                "reformulation on the three target shells, not an upper bound; "
                "harmonic components can have signed coefficients"
            ),
        },
        "status_wall": {
            "Jacobi_basis_constructed": False,
            "Sturm_bound_proved": False,
            "upper_dual_certificate_constructed": False,
            "upper_bound_proved": False,
            "rank28_excluded": False,
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
        },
        "clarifications": [
            (
                "The symbol q is overloaded in the discovery prose: it is the "
                "7-primary discriminant length in Poisson powers, while q^n "
                "also denotes the Fourier variable."
            ),
            (
                "The 1,023,942,465 count is the discriminant size of the "
                "four-variable index lattice G_K, not a proved minimal basis "
                "dimension for a useful optimization."
            ),
            (
                "The degree-32 interpolation is exact only after restricting "
                "to the norm-14, norm-16, and norm-18 shells where each "
                "integral coordinate lies in {-4,...,4}."
            ),
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_results()
    if args.verify:
        archived = json.loads(args.verify.read_text(encoding="utf-8"))
        require(result == archived, "archived independent result mismatch")
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()
