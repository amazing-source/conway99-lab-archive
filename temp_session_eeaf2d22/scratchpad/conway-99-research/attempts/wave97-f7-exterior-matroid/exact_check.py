#!/usr/bin/env python3
"""Exact arithmetic for the Wave 97 exterior/matroid shift.

No graph is constructed.  Every result is conditional on the verified
Wave 51 and Wave 80 imports listed in ``input-freeze.sha256``.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


FIELD = 7
ORDER = 99
CODE_DIMENSION = 44
ENDPOINT_RANK = 28
ENDPOINT_QUOTIENT = 16
RANK_ROWS = tuple(range(28, 43, 2))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rank_mod(matrix: list[list[int]], prime: int = FIELD) -> int:
    """Return the exact row rank over F_prime."""

    if not matrix:
        return 0
    work = [[entry % prime for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0])
    rank = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(rank, rows)
                if work[row][column] % prime
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [
            entry * inverse % prime for entry in work[rank]
        ]
        for row in range(rows):
            if row == rank or work[row][column] == 0:
                continue
            multiple = work[row][column]
            work[row] = [
                (left - multiple * right) % prime
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
    return rank


def schur_hilbert_profile(rank: int = ENDPOINT_RANK) -> dict[str, Any]:
    """Derive the exact Schur powers of the Seidel hull R."""

    require(ORDER % FIELD == 1, "J-I does not have the required kernel")
    j_minus_i = [
        [0 if row == column else 1 for column in range(ORDER)]
        for row in range(ORDER)
    ]
    square_rank = rank_mod(j_minus_i)
    require(square_rank == ORDER - 1, "rank(J-I) changed")

    symmetric_square_dimension = math.comb(rank + 1, 2)
    symmetric_cube_dimension = math.comb(rank + 2, 3)
    require(
        symmetric_square_dimension >= square_rank,
        "symmetric square is too small",
    )
    require(
        symmetric_cube_dimension >= ORDER,
        "symmetric cube is too small",
    )

    hilbert = [1, rank, square_rank, ORDER]
    h_vector = [
        hilbert[0],
        hilbert[1] - hilbert[0],
        hilbert[2] - hilbert[1],
        hilbert[3] - hilbert[2],
    ]
    require(sum(h_vector) == ORDER, "Hilbert h-vector sum changed")

    return {
        "rank_R": rank,
        "schur_square": {
            "identity": (
                "R*R=1_perp because row_i*row_i=1-e_i and "
                "R is self-orthogonal"
            ),
            "dimension": square_rank,
            "ambient_hyperplane": "coordinate-sum-zero hyperplane",
            "symmetric_square_domain_dimension": symmetric_square_dimension,
            "multiplication_kernel_dimension": (
                symmetric_square_dimension - square_rank
            ),
        },
        "schur_cube": {
            "identity": (
                "R*R*R=F7^99: for i!=j, "
                "row_j*(e_i-e_j)=S[j,i]e_i"
            ),
            "dimension": ORDER,
            "symmetric_cube_domain_dimension": symmetric_cube_dimension,
            "evaluation_kernel_dimension": (
                symmetric_cube_dimension - ORDER
            ),
        },
        "evaluation_algebra": {
            "hilbert_function_degrees_0_to_3": hilbert,
            "h_vector": h_vector,
            "regularity_upper_bound": 3,
        },
        "quadratic_veronese": {
            "number_of_points": ORDER,
            "span_dimension": square_rank,
            "unique_relation": (
                "sum_i nu_2(p_i)=0, with all 99 coefficients nonzero"
            ),
            "every_98_images_independent": True,
            "cayley_bacharach_degree_2": True,
        },
        "evaluation_code_C": {
            "dimension": CODE_DIMENSION,
            "schur_square_dimension": ORDER,
            "reason": (
                "R*R=1_perp and the nondegenerate quotient C/R has "
                "a product with nonzero coordinate sum"
            ),
        },
    }


def exterior_smith_row(rank: int) -> dict[str, Any]:
    """Smith and modular ranks of the second compound C_2(S)."""

    require(rank in RANK_ROWS, "rank is outside the verified Wave 80 rows")
    middle = ORDER - 2 * rank
    length = math.comb(ORDER, 2)
    exterior_rank = math.comb(rank, 2)

    valuation_counts = {
        0: math.comb(rank, 2),
        1: rank * middle,
        2: rank * rank + math.comb(middle, 2),
        3: rank * middle,
        4: math.comb(rank, 2),
    }
    require(
        sum(valuation_counts.values()) == length,
        "exterior valuation multiplicities do not sum to the length",
    )
    require(
        sum(exponent * count for exponent, count in valuation_counts.items())
        == 98 * 99,
        "7-adic determinant valuation changed",
    )
    require(
        valuation_counts[4] >= 98,
        "not enough terminal factors for the 2- and 5-parts",
    )

    smith = [
        {"factor": 1, "multiplicity": valuation_counts[0]},
        {"factor": 7, "multiplicity": valuation_counts[1]},
        {"factor": 49, "multiplicity": valuation_counts[2]},
        {"factor": 343, "multiplicity": valuation_counts[3]},
        {
            "factor": 2401,
            "multiplicity": valuation_counts[4] - 98,
        },
        {"factor": 24010, "multiplicity": 98},
    ]
    require(
        sum(item["multiplicity"] for item in smith) == length,
        "Smith multiplicities do not sum to the compound order",
    )
    for left, right in zip(smith, smith[1:]):
        require(
            right["factor"] % left["factor"] == 0,
            "displayed Smith factors are not a divisibility chain",
        )

    return {
        "rank_F7_S": rank,
        "middle_7_primary_multiplicity": middle,
        "order": length,
        "rank_F7_C2S": exterior_rank,
        "nullity_F7_C2S": length - exterior_rank,
        "7_adic_valuation_counts": {
            str(exponent): count
            for exponent, count in valuation_counts.items()
        },
        "smith_normal_form": smith,
        "determinant_valuations": {"2": 98, "5": 98, "7": 9702},
    }


def exterior_row_geometry() -> dict[str, Any]:
    """Compute one row's support in C_2(S) from SRG intersections."""

    other_vertices = ORDER - 2
    overlapping_pair_columns = 2 * other_vertices
    disjoint_pair_columns = math.comb(other_vertices, 2)

    adjacent_ratio_classes = {
        "same": 1 + 72,
        "different": 12 + 12,
    }
    nonadjacent_ratio_classes = {
        "same": 2 + 71,
        "different": 12 + 12,
    }
    require(
        adjacent_ratio_classes == nonadjacent_ratio_classes,
        "pair relation unexpectedly changes the ratio-class sizes",
    )
    same = adjacent_ratio_classes["same"]
    different = adjacent_ratio_classes["different"]
    require(same + different == other_vertices, "ratio classes drift")

    nonzero_disjoint = same * different
    zero_disjoint = disjoint_pair_columns - nonzero_disjoint
    row_weight = 1 + overlapping_pair_columns + nonzero_disjoint
    integral_square_norm = (
        1 + overlapping_pair_columns + 4 * nonzero_disjoint
    )
    require(row_weight == 1947, "exterior distinguished weight changed")
    require(
        integral_square_norm == 3 * 2401,
        "exterior row square norm changed",
    )

    return {
        "compound_entries": {
            "diagonal": -1,
            "overlapping_pairs": "plus_or_minus_1",
            "disjoint_pairs": "0_or_plus_or_minus_2",
        },
        "pair_relation_tables": {
            "adjacent_original_pair": {
                "both_neighbors": 1,
                "one_sided_each": [12, 12],
                "neither_neighbor": 72,
                "same_ratio": same,
                "different_ratio": different,
            },
            "nonadjacent_original_pair": {
                "both_neighbors": 2,
                "one_sided_each": [12, 12],
                "neither_neighbor": 71,
                "same_ratio": same,
                "different_ratio": different,
            },
        },
        "column_counts": {
            "diagonal": 1,
            "overlapping_nonzero": overlapping_pair_columns,
            "disjoint_nonzero": nonzero_disjoint,
            "disjoint_zero": zero_disjoint,
        },
        "distinguished_row_weight": row_weight,
        "integral_row_square_norm": integral_square_norm,
        "row_square_norm_mod_7": integral_square_norm % FIELD,
        "projective_distinguished_rows": math.comb(ORDER, 2),
        "forced_scalar_closed_weight_1947_words": (
            (FIELD - 1) * math.comb(ORDER, 2)
        ),
        "projectivity_reason": (
            "proportional two-column wedges would make at most four "
            "columns of S dependent, contradicting d(row(S)^perp)>=6"
        ),
    }


def exterior_spectrum() -> dict[str, Any]:
    """Rational spectrum of C_2(S), obtained from pairwise products."""

    spectrum = [
        {"eigenvalue": 490, "multiplicity": 44},
        {"eigenvalue": -490, "multiplicity": 54},
        {"eigenvalue": 49, "multiplicity": 2377},
        {"eigenvalue": -49, "multiplicity": 2376},
    ]
    require(
        sum(item["multiplicity"] for item in spectrum)
        == math.comb(ORDER, 2),
        "exterior spectrum multiplicities drift",
    )
    trace = sum(
        item["eigenvalue"] * item["multiplicity"] for item in spectrum
    )
    require(trace == -math.comb(ORDER, 2), "exterior trace changed")
    determinant_2 = sum(
        item["multiplicity"]
        for item in spectrum
        if item["eigenvalue"] % 2 == 0
    )
    require(determinant_2 == 98, "2-adic determinant valuation changed")

    return {
        "spectrum": spectrum,
        "trace": trace,
        "integer_square_identity": (
            "C2(S)^2=2401*C2(I+J) by Cauchy-Binet"
        ),
        "snf_C2_I_plus_J": "diag(1^4753,100^98)",
        "mod_7_square_zero": True,
    }


def orthogonal_group_order(sign: str, half_dimension: int) -> int:
    """Order of O^sign(2m,7), for odd field order."""

    require(sign in {"plus", "minus"}, "unknown orthogonal sign")
    terminal = (
        FIELD**half_dimension - 1
        if sign == "plus"
        else FIELD**half_dimension + 1
    )
    product = math.prod(
        FIELD ** (2 * index) - 1
        for index in range(1, half_dimension)
    )
    return (
        2
        * FIELD ** (half_dimension * (half_dimension - 1))
        * terminal
        * product
    )


def orthogonal_orbit_profile() -> dict[str, Any]:
    """Exact q=16 orbit counts inside O^-(42,7)."""

    ambient_order = orthogonal_group_order("minus", 21)
    subspace_order = orthogonal_group_order("minus", 8)
    complement_order = orthogonal_group_order("plus", 13)
    denominator = subspace_order * complement_order
    require(
        ambient_order % denominator == 0,
        "orthogonal embedding orbit ratio is not integral",
    )
    embedding_count = ambient_order // denominator

    nonzero_isotropic_vectors = (
        (FIELD**7 - 1) * (FIELD**8 + 1)
    )
    vectors_per_nonzero_norm = FIELD**15 + FIELD**7
    isotropic_points = nonzero_isotropic_vectors // (FIELD - 1)
    square_anisotropic_points = vectors_per_nonzero_norm // 2
    nonsquare_anisotropic_points = vectors_per_nonzero_norm // 2
    projective_total = (FIELD**16 - 1) // (FIELD - 1)
    require(
        isotropic_points
        + square_anisotropic_points
        + nonsquare_anisotropic_points
        == projective_total,
        "orthogonal projective orbits do not partition the points",
    )

    return {
        "ambient": "O^-(42,7)",
        "subspace": "O^-(16,7)",
        "orthogonal_complement": "O^+(26,7)",
        "single_ambient_orthogonal_group_orbit": True,
        "number_of_embedded_subspaces": embedding_count,
        "number_of_embedded_subspaces_decimal_digits": len(
            str(embedding_count)
        ),
        "projective_point_orbits_in_O_minus_16_7": {
            "isotropic": isotropic_points,
            "square_anisotropic": square_anisotropic_points,
            "nonsquare_anisotropic": nonsquare_anisotropic_points,
            "total": projective_total,
        },
        "short_vector_orbit_reduction": {
            "norm_14_code_self_dot_0": (
                "zero quotient class or nonzero isotropic orbit"
            ),
            "norm_16_code_self_dot_4": "square-anisotropic orbit",
            "norm_18_code_self_dot_1": "square-anisotropic orbit",
            "norm_16_and_18_same_projective_orthogonal_orbit": True,
        },
    }


def generalized_weight_boundary() -> dict[str, Any]:
    """Matroid consequences of d(R^perp)>=6."""

    rows = []
    dual_dimension = ORDER - ENDPOINT_RANK
    for index in range(1, dual_dimension + 1):
        rows.append(
            {
                "j": index,
                "lower_from_five_column_independence": index + 5,
                "generalized_singleton_upper": (
                    ORDER - dual_dimension + index
                ),
            }
        )
    require(rows[-1]["generalized_singleton_upper"] == ORDER, "upper drift")

    return {
        "column_matroid_rank": ENDPOINT_RANK,
        "number_of_elements": ORDER,
        "girth_lower_bound": 6,
        "dual_code_parameters": "[99,71]_7",
        "generalized_weight_rows": rows,
        "first_weight_boundary_after_forced_short_vector": "6<=d1<=18",
        "contradiction": False,
    }


def build_results() -> dict[str, Any]:
    profiles = [exterior_smith_row(rank) for rank in RANK_ROWS]
    endpoint = next(
        row for row in profiles if row["rank_F7_S"] == ENDPOINT_RANK
    )
    require(
        endpoint["rank_F7_C2S"] == 378,
        "endpoint exterior rank changed",
    )
    return {
        "format": "wave97-f7-exterior-matroid-v1",
        "claim_label": "DERIVED",
        "scope": (
            "unrestricted conditional consequences of a hypothetical "
            "srg(99,14,1,2), with no graph automorphism assumption"
        ),
        "schur_hilbert": schur_hilbert_profile(),
        "exterior_square": {
            "definition": (
                "E=C2(S), indexed by unordered pairs, "
                "E[I,J]=det(S[I,J])"
            ),
            "all_rank_rows": profiles,
            "endpoint_rank_28": endpoint,
            "row_geometry": exterior_row_geometry(),
            "rational_and_integral_structure": exterior_spectrum(),
            "mod_7_code": {
                "parameters": "[4851,378]_7",
                "self_orthogonal": True,
                "dual_distance_lower_bound": 3,
                "distinguished_weight": 1947,
                "distinguished_projective_lines": 4851,
            },
        },
        "generalized_hamming_weights": generalized_weight_boundary(),
        "orthogonal_orbits": orthogonal_orbit_profile(),
        "boundary": {
            "new_exact_reformulations": [
                "R*R=1_perp and R*R*R=F7^99",
                "quadratic Veronese images form a 99-element circuit",
                "complete conditional Smith form of C2(S)",
                "one exact O^-(16,7) embedding orbit in O^-(42,7)",
            ],
            "rank_28_excluded": False,
            "strict_n3_upper_bound_below_4158": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Wave 97 is discovery and cannot verify itself.",
            "No graph, code, or 4851 by 4851 compound matrix is constructed.",
            "The exterior Smith profile is functorial necessary data.",
            "Abstract orthogonal transitivity forgets all coordinate weights.",
            "Generalized-weight bounds do not determine a realizable matroid.",
        ],
    }


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()

    rendered = canonical_json(build_results())
    if arguments.verify is not None:
        require(
            arguments.verify.read_text(encoding="utf-8") == rendered,
            "sealed exact results differ from a fresh derivation",
        )
    if arguments.output is not None:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    if arguments.output is None and arguments.verify is None:
        print(rendered, end="")


if __name__ == "__main__":
    main()
