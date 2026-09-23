#!/usr/bin/env python3
"""Independent exact checks for the Wave 31 sign-commutant obstruction.

This module does not import or execute the discovery implementation.  It
reconstructs the numerical and finite algebraic consequences from the frozen
SRG, incidence, projector-frame, and rootless block hypotheses.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import platform
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


V = 99
K_DEGREE = 14
LAMBDA = 1
MU = 2
TRIANGLE_SIZE = 3
TRIANGLES_PER_VERTEX = 7
TRIANGLES = 231
FRAME_RANK = 44
PROJECTOR_SCALE = 21
FRAME_NORM = 4

ESSENTIAL_PREMISES = (
    "target_srg_99_14_1_2",
    "actual_vertex_triangle_incidence",
    "zero_eigenspace_projector",
    "integral_full_rank_frame",
    "minimum_four_scaled_dual_form",
    "integral_orthogonal_decomposition",
    "coordinate_block_sign_involution",
    "symmetric_incidence_transport",
    "shared_triangle_edge_sign",
    "target_connectedness",
)


class PremiseError(ValueError):
    """Raised when an essential premise is absent."""


Matrix = tuple[tuple[Fraction, ...], ...]


def q(value: int, denominator: int = 1) -> Fraction:
    return Fraction(value, denominator)


def matrix(rows: Sequence[Sequence[int | Fraction]]) -> Matrix:
    return tuple(tuple(Fraction(value) for value in row) for row in rows)


def identity(size: int) -> Matrix:
    return tuple(
        tuple(q(int(row == column)) for column in range(size))
        for row in range(size)
    )


def transpose(left: Matrix) -> Matrix:
    return tuple(tuple(left[row][column] for row in range(len(left))) for column in range(len(left[0])))


def matmul(left: Matrix, right: Matrix) -> Matrix:
    assert len(left[0]) == len(right)
    right_t = transpose(right)
    return tuple(
        tuple(sum((a * b for a, b in zip(row, column)), q(0)) for column in right_t)
        for row in left
    )


def matsub(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(a - b for a, b in zip(left_row, right_row))
        for left_row, right_row in zip(left, right)
    )


def matscale(scale: Fraction, left: Matrix) -> Matrix:
    return tuple(tuple(scale * value for value in row) for row in left)


def matadd(*matrices: Matrix) -> Matrix:
    return tuple(
        tuple(sum((item[row][column] for item in matrices), q(0)) for column in range(len(matrices[0][0])))
        for row in range(len(matrices[0]))
    )


def matvec(left: Matrix, vector: Sequence[int | Fraction]) -> tuple[Fraction, ...]:
    return tuple(
        sum((value * Fraction(coordinate) for value, coordinate in zip(row, vector)), q(0))
        for row in left
    )


def target_spectrum() -> dict[str, object]:
    """Derive the nontrivial SRG spectrum and multiplicities exactly."""

    # For an srg(v,k,lambda,mu), a nonprincipal eigenvalue t satisfies
    # t^2-(lambda-mu)t-(k-mu)=0.  Here this is t^2+t-12.
    roots = [
        candidate
        for candidate in range(-K_DEGREE, K_DEGREE + 1)
        if candidate * candidate
        - (LAMBDA - MU) * candidate
        - (K_DEGREE - MU)
        == 0
    ]
    assert roots == [-4, 3]
    negative, positive = roots

    multiplicities = []
    for positive_multiplicity in range(V):
        negative_multiplicity = V - 1 - positive_multiplicity
        if (
            K_DEGREE
            + positive * positive_multiplicity
            + negative * negative_multiplicity
            == 0
        ):
            multiplicities.append((positive_multiplicity, negative_multiplicity))
    assert multiplicities == [(54, 44)]
    positive_multiplicity, negative_multiplicity = multiplicities[0]

    edges = V * K_DEGREE // 2
    triangles_from_edges = edges // TRIANGLE_SIZE
    assert edges == 693
    assert triangles_from_edges == TRIANGLES
    assert V * TRIANGLES_PER_VERTEX == TRIANGLES * TRIANGLE_SIZE

    return {
        "adjacency_minimal_relation_nonprincipal": "t^2+t-12=0",
        "adjacency_eigenvalues": [K_DEGREE, positive, negative],
        "adjacency_multiplicities": [1, positive_multiplicity, negative_multiplicity],
        "edges": edges,
        "triangles": triangles_from_edges,
        "triangles_per_vertex": TRIANGLES_PER_VERTEX,
        "gamma_eigenvalues": [18, 7, 0, -3],
        "gamma_multiplicities": [1, positive_multiplicity, negative_multiplicity, TRIANGLES - V],
    }


def projector_coefficients() -> dict[str, object]:
    """Solve P=alpha I+beta A+gamma J for the A=-4 projector."""

    # alpha+3 beta=0 and alpha-4 beta=1.
    beta = q(-1, 7)
    alpha = q(3, 7)
    gamma = -(alpha + K_DEGREE * beta) / V
    assert gamma == q(1, 63)

    eigenspace_values = {
        "14": alpha + K_DEGREE * beta + V * gamma,
        "3": alpha + 3 * beta,
        "-4": alpha - 4 * beta,
    }
    assert eigenspace_values == {"14": q(0), "3": q(0), "-4": q(1)}

    return {
        "alpha_I": str(alpha),
        "beta_A": str(beta),
        "gamma_J": str(gamma),
        "integer_formula": "(27I-9A+J)/63",
        "eigenspace_values": {key: int(value) for key, value in eigenspace_values.items()},
    }


def incidence_transport() -> dict[str, object]:
    """Check the exact scale and dimension argument for N:im(E)->V_-4."""

    spectrum = target_spectrum()
    gamma_zero_dimension = spectrum["adjacency_multiplicities"][2]
    minus_four_dimension = spectrum["adjacency_multiplicities"][2]
    assert gamma_zero_dimension == FRAME_RANK
    assert minus_four_dimension == FRAME_RANK

    # On Gamma u=0, N^T N u=(3I+Gamma)u=3u.  Thus the squared
    # norm scale is three and the map is injective.  NN^T=7I+A then
    # yields (7I+A)Nu=3Nu, or A(Nu)=-4Nu.
    norm_square_scale = TRIANGLE_SIZE
    transported_adjacency_eigenvalue = norm_square_scale - TRIANGLES_PER_VERTEX
    assert transported_adjacency_eigenvalue == -4

    return {
        "domain": "im(E)=ker(Gamma)",
        "domain_dimension": gamma_zero_dimension,
        "norm_square_scale": norm_square_scale,
        "injective": norm_square_scale > 0,
        "transported_adjacency_eigenvalue": transported_adjacency_eigenvalue,
        "target_dimension": minus_four_dimension,
        "onto_minus_four_eigenspace": gamma_zero_dimension == minus_four_dimension,
    }


def rootless_support_patterns(block_count: int) -> list[list[int]]:
    """Enumerate all component-norm patterns relevant to a norm-four row."""

    # Minimum at least four makes every nonzero lattice-block component have
    # norm at least four. Evenness is not needed. Values above four cannot
    # occur in a sum equal to four, so {0,4,5} is a complete illustrative
    # truncated domain for this implication.
    patterns = [
        list(values)
        for values in itertools.product((0, 4, 5), repeat=block_count)
        if sum(values) == FRAME_NORM
    ]
    assert all(pattern.count(FRAME_NORM) == 1 for pattern in patterns)
    assert all(sum(value != 0 for value in pattern) == 1 for pattern in patterns)
    return patterns


def block_support() -> dict[str, object]:
    patterns_by_block_count = {
        str(block_count): rootless_support_patterns(block_count)
        for block_count in range(2, 6)
    }
    rooted_counterpattern = [2, 2]
    assert sum(rooted_counterpattern) == FRAME_NORM

    return {
        "rootless_component_rule": "each nonzero lattice-block component has norm at least 4",
        "evenness_role": "inherited endpoint hypothesis but unnecessary for one-block row support",
        "norm_four_patterns": patterns_by_block_count,
        "consequence": "each frame row is supported in exactly one lattice block",
        "matrix_consequence": "M=XSX^T and E=M/21 are coordinate-block diagonal",
        "rooted_counterpattern": rooted_counterpattern,
        "rooted_consequence": "a 2+2 split can destroy coordinate block diagonality",
    }


def commutation_controls() -> dict[str, object]:
    """Exact 2x2 controls for the preservation/symmetry implications."""

    rank_one_projector = matrix([[1, 0], [0, 0]])
    nonsymmetric_preserver = matrix([[1, 1], [0, 2]])
    assert matvec(nonsymmetric_preserver, [1, 0]) == (q(1), q(0))
    nonsymmetric_commutator = matsub(
        matmul(nonsymmetric_preserver, rank_one_projector),
        matmul(rank_one_projector, nonsymmetric_preserver),
    )
    assert nonsymmetric_commutator != matrix([[0, 0], [0, 0]])

    oblique_coordinate_projector = matscale(q(1, 2), matrix([[1, 1], [1, 1]]))
    coordinate_sign = matrix([[1, 0], [0, -1]])
    de_minus_ed = matsub(
        matmul(coordinate_sign, oblique_coordinate_projector),
        matmul(oblique_coordinate_projector, coordinate_sign),
    )
    assert de_minus_ed != matrix([[0, 0], [0, 0]])
    assert matvec(coordinate_sign, [1, 1]) == (q(1), q(-1))
    assert matvec(oblique_coordinate_projector, [1, -1]) == (q(0), q(0))

    # For a symmetric [[a,b],[b,c]], preservation of span(e1) forces b=0,
    # and the resulting diagonal matrix commutes with diag(1,0).
    symmetric_examples_checked = 0
    for a, b, c in itertools.product(range(-2, 3), repeat=3):
        candidate = matrix([[a, b], [b, c]])
        if matvec(candidate, [1, 0])[1] == 0:
            symmetric_examples_checked += 1
            assert (
                matsub(
                    matmul(candidate, rank_one_projector),
                    matmul(rank_one_projector, candidate),
                )
                == matrix([[0, 0], [0, 0]])
            )

    return {
        "symmetric_preserver_examples_checked": symmetric_examples_checked,
        "symmetric_preserver_commutes": True,
        "nonsymmetric_preserver": {
            "preserves_V": True,
            "commutes_with_P": False,
            "commutator": [[int(value) for value in row] for row in nonsymmetric_commutator],
        },
        "drop_DE_equals_ED": {
            "E": "projector onto span((1,1))",
            "D": "diag(1,-1)",
            "commutes": False,
            "D_preserves_imE": False,
        },
    }


def commutator_coefficients() -> dict[str, object]:
    """Check the sign and every scalar in the projector commutator."""

    # Use generic exact 2x2 matrices to verify
    # [K,(27I-9A+J)/63]=0 iff -9(KA-AK)+(KJ-JK)=0.
    K_matrix = matrix([[2, -1], [3, 4]])
    A_matrix = matrix([[0, 1], [1, 0]])
    J_matrix = matrix([[1, 1], [1, 1]])
    P_numerator = matadd(
        matscale(q(27), identity(2)),
        matscale(q(-9), A_matrix),
        J_matrix,
    )
    P_matrix = matscale(q(1, 63), P_numerator)
    kp_minus_pk = matsub(matmul(K_matrix, P_matrix), matmul(P_matrix, K_matrix))
    ka_minus_ak = matsub(matmul(K_matrix, A_matrix), matmul(A_matrix, K_matrix))
    kj_minus_jk = matsub(matmul(K_matrix, J_matrix), matmul(J_matrix, K_matrix))
    reconstructed = matscale(
        q(1, 63),
        matadd(matscale(q(-9), ka_minus_ak), kj_minus_jk),
    )
    assert kp_minus_pk == reconstructed

    # K1=NDN^T1=3ND1=3d.  Substitution into the preceding identity
    # divides both sides by three.
    k_one_coefficient = TRIANGLE_SIZE
    projector_a_coefficient = 9
    reduced_coefficient = projector_a_coefficient // k_one_coefficient
    assert projector_a_coefficient == reduced_coefficient * k_one_coefficient

    return {
        "projector_commutator": "9(KA-AK)=KJ-JK",
        "K_one": "K1=3d",
        "symmetric_K_gives_one_transpose_K": "1^T K=3d^T",
        "reduced_identity": "3(KA-AK)=d1^T-1d^T",
        "coefficients": {
            "projector_A": projector_a_coefficient,
            "K_one": k_one_coefficient,
            "reduced": reduced_coefficient,
        },
        "generic_matrix_sign_check": True,
    }


def adjacent_local_sum(first_sign: int = 1, second_sign: int = 1) -> dict[str, object]:
    """Audit all 99 summands of (ZA-AZ)_xy by SRG relation class."""

    categories = [
        {
            "vertices": ["x"],
            "count": 1,
            "ZA_factor": "Z_xx A_xy",
            "ZA_each": 0,
            "AZ_factor": "A_xx Z_xy",
            "AZ_each": 0,
        },
        {
            "vertices": ["y"],
            "count": 1,
            "ZA_factor": "Z_xy A_yy",
            "ZA_each": 0,
            "AZ_factor": "A_xy Z_yy",
            "AZ_each": 0,
        },
        {
            "vertices": ["z"],
            "count": LAMBDA,
            "ZA_factor": "Z_xz A_zy",
            "ZA_each": first_sign,
            "AZ_factor": "A_xz Z_zy",
            "AZ_each": second_sign,
        },
        {
            "vertices": ["N(x) minus {y,z}"],
            "count": K_DEGREE - 2,
            "ZA_factor": "Z_xw A_wy",
            "ZA_each": 0,
            "AZ_factor": "A_xw Z_wy",
            "AZ_each": 0,
        },
        {
            "vertices": ["N(y) minus {x,z}"],
            "count": K_DEGREE - 2,
            "ZA_factor": "Z_xw A_wy",
            "ZA_each": 0,
            "AZ_factor": "A_xw Z_wy",
            "AZ_each": 0,
        },
        {
            "vertices": ["neither endpoint nor a neighbor of both"],
            "count": V - (2 + LAMBDA + 2 * (K_DEGREE - 2)),
            "ZA_factor": "Z_xw A_wy",
            "ZA_each": 0,
            "AZ_factor": "A_xw Z_wy",
            "AZ_each": 0,
        },
    ]
    assert sum(item["count"] for item in categories) == V
    za = sum(item["count"] * item["ZA_each"] for item in categories)
    az = sum(item["count"] * item["AZ_each"] for item in categories)
    return {
        "categories": categories,
        "summands_checked": V,
        "ZA_xy": za,
        "AZ_xy": az,
        "ZA_minus_AZ_xy": za - az,
        "cancels": za == az,
    }


def local_commutator() -> dict[str, object]:
    shared = adjacent_local_sum(1, 1)
    mutated = adjacent_local_sum(1, -1)
    assert shared["ZA_minus_AZ_xy"] == 0
    assert mutated["ZA_minus_AZ_xy"] == 2

    # With delta=d_x-d_y, 3(delta+c)=delta.
    mutation_delta = Fraction(-3 * mutated["ZA_minus_AZ_xy"], 2)
    assert mutation_delta == -3

    return {
        "shared_triangle_sign": shared,
        "mutated_edge_signs": mutated,
        "adjacent_equation_shared": "3(d_x-d_y)=d_x-d_y",
        "shared_consequence": "d_x=d_y",
        "mutation_permitted_difference": int(mutation_delta),
    }


def connectedness() -> dict[str, object]:
    assert MU > 0
    return {
        "adjacent_pair_distance": 1,
        "nonadjacent_common_neighbors": MU,
        "nonadjacent_pair_distance_at_most": 2,
        "connected": True,
        "diameter_at_most": 2,
    }


def signed_block_sizes() -> list[dict[str, int]]:
    rows = []
    for signed_degree in range(-TRIANGLES_PER_VERTEX, TRIANGLES_PER_VERTEX + 1, 2):
        numerator = V * signed_degree + TRIANGLES * TRIANGLE_SIZE
        assert numerator % (2 * TRIANGLE_SIZE) == 0
        block_size = numerator // (2 * TRIANGLE_SIZE)
        assert V * signed_degree == TRIANGLE_SIZE * (2 * block_size - TRIANGLES)
        rows.append(
            {
                "constant_signed_degree": signed_degree,
                "block_size": block_size,
                "block_size_mod_33": block_size % 33,
            }
        )
    assert [item["block_size"] for item in rows] == list(range(0, TRIANGLES + 1, 33))
    return rows


def block_rank_census() -> list[dict[str, object]]:
    rows = []
    for rank in range(1, FRAME_RANK):
        integral_row_count = (PROJECTOR_SCALE * rank) % FRAME_NORM == 0
        if integral_row_count:
            block_rows = PROJECTOR_SCALE * rank // FRAME_NORM
            rows.append(
                {
                    "rank": rank,
                    "rows": block_rows,
                    "rows_mod_21": block_rows % 21,
                    "rows_mod_33": block_rows % 33,
                    "excluded": block_rows % 33 != 0,
                }
            )
    assert [item["rank"] for item in rows] == list(range(4, FRAME_RANK, 4))
    assert all(item["excluded"] for item in rows)
    return rows


def divisibility_and_trace() -> dict[str, object]:
    signed_sizes = signed_block_sizes()
    rank_census = block_rank_census()
    lcm = math.lcm(21, 33)
    assert lcm == TRIANGLES
    assert math.gcd(21, 33) == 3

    # There is a shorter projector-only route once coordinate block
    # diagonality has already been obtained.  E_I is an idempotent symmetric
    # principal block and diag(E_I)=4/21, hence
    # rank(E_I)=tr(E_I)=4b/21 is an integer.  This directly gives 21|b.
    coordinate_block_ranks = []
    for block_rows in range(TRIANGLES + 1):
        trace = Fraction(FRAME_NORM * block_rows, PROJECTOR_SCALE)
        if trace.denominator == 1:
            coordinate_block_ranks.append(
                {"block_rows": block_rows, "projector_block_rank": int(trace)}
            )
    assert [item["block_rows"] for item in coordinate_block_ranks] == list(
        range(0, TRIANGLES + 1, 21)
    )

    return {
        "double_count": "99d=3(2b-231)",
        "reduced_double_count": "33d=2b-231",
        "signed_size_consequence": "33 divides b",
        "constant_degree_size_census": signed_sizes,
        "coordinate_projector_trace": "rank(E_I)=tr(E_I)=4b/21",
        "coordinate_projector_trace_consequence": "21 divides b",
        "coordinate_projector_rank_census": coordinate_block_ranks,
        "frame_trace": "4b=21r",
        "frame_trace_consequences": ["4 divides r", "21 divides b"],
        "combined_row_divisibility": f"lcm(21,33)={lcm} divides b",
        "proper_block_range": f"0<b<{TRIANGLES}",
        "proper_rank_census": rank_census,
        "wave30_rows": {
            "rank20": PROJECTOR_SCALE * 20 // FRAME_NORM,
            "rank24": PROJECTOR_SCALE * 24 // FRAME_NORM,
        },
        "wave30_rows_mod_33": {
            "rank20": (PROJECTOR_SCALE * 20 // FRAME_NORM) % 33,
            "rank24": (PROJECTOR_SCALE * 24 // FRAME_NORM) % 33,
        },
    }


def hostile_controls() -> dict[str, object]:
    return {
        "drop_rootlessness": {
            "counterpattern": [2, 2],
            "effect": "a norm-four frame row can meet two blocks",
        },
        "drop_nonzero_component_norm_floor": {
            "counterpattern": [1, 3],
            "effect": "component support no longer follows without the minimum-four lattice-vector floor, for example after dropping integrality/evenness together",
        },
        "drop_evenness_alone": {
            "effect": "no failure; minimum at least four still forces one-block row support",
        },
        "drop_DE_equals_ED": commutation_controls()["drop_DE_equals_ED"],
        "drop_K_symmetry": commutation_controls()["nonsymmetric_preserver"],
        "drop_shared_triangle_sign": {
            "ZA_minus_AZ_xy": adjacent_local_sum(1, -1)["ZA_minus_AZ_xy"],
            "permitted_d_x_minus_d_y": -3,
        },
        "drop_connectedness": {
            "effect": "edgewise constancy only forces one value on each connected component",
        },
        "multiple_of_33_only": {
            "effect": "necessary row-count arithmetic constructs no D, E, frame, or graph",
        },
    }


def derive(enabled_premises: Iterable[str] | None = None) -> dict[str, object]:
    enabled = set(ESSENTIAL_PREMISES if enabled_premises is None else enabled_premises)
    missing = [premise for premise in ESSENTIAL_PREMISES if premise not in enabled]
    if missing:
        raise PremiseError("missing essential premises: " + ", ".join(missing))

    return {
        "schema": "wave31-sign-commutant-independent-verifier-v1",
        "frozen_candidate_commit": "a8b0c34040f6857b3c5ebcc44f108e03a4159088",
        "target": target_spectrum(),
        "projector": projector_coefficients(),
        "incidence_transport": incidence_transport(),
        "rootless_block_support": block_support(),
        "transport_commutation": commutation_controls(),
        "commutator": commutator_coefficients(),
        "adjacent_local_audit": local_commutator(),
        "connectedness": connectedness(),
        "divisibility_and_trace": divisibility_and_trace(),
        "hostile_controls": hostile_controls(),
        "scope": {
            "verified_scoped_conclusion": (
                "No nontrivial rootless integral orthogonal decomposition of "
                "the rank-44 scaled-dual endpoint S-form can satisfy the "
                "actual target-graph incidence/projector package."
            ),
            "rootless_decomposable_endpoint_forms": "REFUTED_VERIFIED_SCOPED",
            "wave30_rank20_plus_rank24_decomposable_boundary": "REFUTED_VERIFIED_SCOPED",
            "rootless_indecomposable_endpoint_forms": "UNKNOWN",
            "rooted_endpoint_forms": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "runtime": {
            "implementation": platform.python_implementation(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "verdict": "PASS_SCOPED",
    }


def write_json(path: Path, result: dict[str, object]) -> None:
    payload = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_text(payload, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.output:
        write_json(args.output, result)
    else:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
