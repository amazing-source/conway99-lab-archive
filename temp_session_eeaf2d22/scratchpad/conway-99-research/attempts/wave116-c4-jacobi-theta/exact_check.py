"""Exact arithmetic for the Wave 116 C4/Jacobi strategy assessment."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def mat_scale(matrix: list[list[Fraction]], scalar: Fraction) -> list[list[Fraction]]:
    return [[scalar * entry for entry in row] for row in matrix]


def mat_vec(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction())
        for row in matrix
    ]


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction())


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column]),
            None,
        )
        require(pivot is not None, "singular matrix")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result *= -1
        value = work[column][column]
        result *= value
        work[column] = [entry / value for entry in work[column]]
        for row in range(column + 1, len(work)):
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    a - multiplier * b
                    for a, b in zip(work[row], work[column])
                ]
    return result


def solve(matrix: list[list[Fraction]], vector: list[Fraction]) -> list[Fraction]:
    size = len(matrix)
    work = [row[:] + [value] for row, value in zip(matrix, vector)]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        require(pivot is not None, "singular matrix")
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


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def matrix_text(matrix: list[list[Fraction]]) -> list[list[str]]:
    return [[fraction_text(entry) for entry in row] for row in matrix]


def cycle_adjacency() -> list[list[Fraction]]:
    return [
        [Fraction(int((i - j) % 4 in (1, 3))) for j in range(4)]
        for i in range(4)
    ]


def restricted_projector() -> list[list[Fraction]]:
    adjacency = cycle_adjacency()
    return [
        [
            (
                3 * int(i == j)
                - adjacency[i][j]
                + Fraction(1, 9)
            )
            / 7
            for j in range(4)
        ]
        for i in range(4)
    ]


def verify_eigenpair(
    matrix: list[list[Fraction]],
    vector: list[int],
    eigenvalue: Fraction,
) -> None:
    rational_vector = [Fraction(value) for value in vector]
    require(
        mat_vec(matrix, rational_vector)
        == [eigenvalue * value for value in rational_vector],
        f"failed eigenpair at {eigenvalue}",
    )


def build_results() -> dict[str, object]:
    projector = restricted_projector()
    one = [1, 1, 1, 1]
    alternating = [1, -1, 1, -1]
    zero_a = [1, 0, -1, 0]
    zero_b = [0, 1, 0, -1]
    projector_eigenvalues = [
        Fraction(13, 63),
        Fraction(5, 7),
        Fraction(3, 7),
        Fraction(3, 7),
    ]
    for vector, eigenvalue in zip(
        (one, alternating, zero_a, zero_b),
        projector_eigenvalues,
    ):
        verify_eigenpair(projector, vector, eigenvalue)
    require(determinant(projector) == Fraction(65, 2401), "wrong E determinant")

    dual_evaluation_gram = mat_scale(projector, Fraction(9))
    l_marking_gram = mat_scale(projector, Fraction(63))
    k_marking_gram = mat_scale(projector, Fraction(441))
    require(
        k_marking_gram == mat_scale(l_marking_gram, Fraction(7)),
        "Fricke marking scales do not match",
    )
    require(determinant(l_marking_gram) == 426465, "wrong L marking determinant")
    require(
        determinant(k_marking_gram) == 1023942465,
        "wrong K marking determinant",
    )

    expected_l = [
        [28, -8, 1, -8],
        [-8, 28, -8, 1],
        [1, -8, 28, -8],
        [-8, 1, -8, 28],
    ]
    require(
        l_marking_gram
        == [[Fraction(entry) for entry in row] for row in expected_l],
        "wrong L marking matrix",
    )

    residue_matrix = [
        [int(entry) % 7 for entry in row]
        for row in l_marking_gram
    ]
    require(int(determinant(l_marking_gram)) % 7 == 4, "residue Gram is singular")

    r_pattern = [Fraction(21 * value) for value in alternating]
    projected_norm = dot(r_pattern, solve(k_marking_gram, r_pattern))
    require(projected_norm == Fraction(28, 5), "wrong projected pattern norm")

    oriented_lower = 105624
    require(oriented_lower % 2 == 0, "antipodal lower bound is not integral")
    antipodal_lower = oriented_lower // 2
    c4_count = 2079
    local_cap = 25
    cap_total = c4_count * local_cap
    require(cap_total < antipodal_lower, "Wave 112 target does not close")

    return {
        "format": "wave116-c4-jacobi-theta-v1",
        "claim_label": "DERIVED",
        "scope": (
            "Conditional exact C4 evaluation-lattice and Jacobi strategy "
            "assessment; no graph, rank, or novelty result."
        ),
        "restricted_projector": {
            "formula": "E_-4[C]=(3I-H_C+J/9)/7",
            "matrix": matrix_text(projector),
            "eigenvectors": {
                "constant": one,
                "alternating": alternating,
                "zero_mode_a": zero_a,
                "zero_mode_b": zero_b,
            },
            "eigenvalues": [fraction_text(value) for value in projector_eigenvalues],
            "determinant": "65/2401",
            "positive_definite": True,
        },
        "evaluation_lattices": {
            "coordinate_vector": {
                "name": "p_i=u_i/sqrt(7)",
                "gram": "E_-4[C]",
                "warning": (
                    "p_i is not proved to lie in K*; E/2 is not a justified "
                    "ordinary Jacobi index."
                ),
            },
            "dual_evaluation_vector": {
                "name": "a_i=3u_i/sqrt(7)",
                "membership": "a_i in K*",
                "seven_multiple": "7a_i=3sqrt(7)u_i in K",
                "gram": matrix_text(dual_evaluation_gram),
                "four_classes_in_K_dual_mod_K": "(Z/7)^4",
                "residue_pairing_times_7_mod_7": residue_matrix,
                "residue_determinant_mod_7": 4,
                "short_vector_coordinate": "<x,a_i>=3t_i",
            },
            "ordinary_K_Jacobi_marking": {
                "name": "g_i=7a_i=3sqrt(7)u_i",
                "membership": "g_i in K",
                "gram": matrix_text(k_marking_gram),
                "eigenvalues": [91, 315, 189, 189],
                "determinant": 1023942465,
                "matrix_index": "G_K/2",
                "short_vector_coordinate": "<x,g_i>=21t_i",
            },
            "Fricke_L_marking": {
                "name": "v_i=3u_i",
                "membership": "v_i in L",
                "gram": matrix_text(l_marking_gram),
                "eigenvalues": [13, 45, 27, 27],
                "determinant": 426465,
                "relation": "G_K=7G_L and g_i/sqrt(7)=v_i",
            },
        },
        "cycle_sum": {
            "induced_C4_count": c4_count,
            "cyclic_labeling": (
                "Choose any cyclic labeling per C4; dihedral relabeling "
                "preserves the common index."
            ),
            "automorphism_assumption": False,
            "ordinary_Jacobi_object": (
                "Phi_K=sum_C sum_xinK q^((x,x)/2) "
                "exp(2pi*i*sum_j z_j<x,g_Cj>)"
            ),
            "weight": 22,
            "level": 7,
            "index": "G_K/2",
            "constant_coefficient": c4_count,
            "z_zero_specialization": "Phi_K(tau,0)=2079*Theta_K(tau)",
        },
        "Fricke_Poisson": {
            "raw_formula": (
                "Phi_K(-1/(7tau),z/(7tau))="
                "-7^(q/2)*tau^22*exp(pi*i*z^T*G_L*z/tau)*Phi_L(tau,z)"
            ),
            "normalized_formula": (
                "Phi_K||W_7=-7^(q/2-11)*Phi_L"
            ),
            "scalar_control": (
                "At z=0 this is equivalent to "
                "Theta_L=-7^(11-q/2)*(Theta_K|W_7)."
            ),
            "warning": (
                "Fricke couples the K index G_K/2 to the L index G_L/2; "
                "it is not a self-map of one fixed index."
            ),
        },
        "incidence_coefficient": {
            "alternating_t_pattern": alternating,
            "K_Fourier_pattern": [int(value) for value in r_pattern],
            "projected_norm": "28/5",
            "q_exponents": [7, 8, 9],
            "interpretation": (
                "For each C4 incidence exactly one vector in an antipodal "
                "pair has the chosen alternating pattern."
            ),
            "coefficient_sum_is_antipodal_incidence": True,
            "oriented_incidence_is_twice_coefficient_sum": True,
            "rank28_coefficient_sum_lower": antipodal_lower,
            "rank28_oriented_incidence_lower": oriented_lower,
            "sufficient_coefficient_sum_upper_for_contradiction": cap_total,
            "gap": antipodal_lower - cap_total,
        },
        "finite_dimensional_routes": {
            "matrix_index_theta_decomposition_component_count": 1023942465,
            "unscaled_four_class_subgroup_size": 2401,
            "unscaled_modular_closure_warning": (
                "The four classes give a nondegenerate (Z/7)^4 sector, but "
                "modular transformations still retain the orthogonal "
                "discriminant complement unless additional orbit data are proved."
            ),
            "exact_LP_blueprint": [
                "construct an exact basis through a proved Jacobi Sturm bound",
                "fix both constant terms at 2079 and impose the Fricke relation",
                "impose nonnegative integral Fourier coefficients for both theta sums",
                "maximize c(7,21a)+c(8,21a)+c(9,21a)",
                "accept an upper bound only with an exact dual certificate",
            ],
            "harmonic_alternative": {
                "short_coordinate_range": "t_i in {-4,-3,...,4}",
                "indicator_interpolation_degree_per_coordinate": 8,
                "total_degree": 32,
                "description": (
                    "On norms at most 18, a degree-32 polynomial in four "
                    "evaluations exactly isolates the alternating pattern; "
                    "harmonic decomposition replaces the huge matrix index by "
                    "weighted theta series, but loses coefficient positivity."
                ),
            },
        },
        "current_boundary": {
            "new_Jacobi_upper_bound": None,
            "reason": (
                "No exact Jacobi basis, Sturm truncation, Fricke-positive cone, "
                "or dual upper certificate has been constructed."
            ),
            "rank28_excluded": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
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
        require(result == archived, "archived result mismatch")
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")


if __name__ == "__main__":
    main()
