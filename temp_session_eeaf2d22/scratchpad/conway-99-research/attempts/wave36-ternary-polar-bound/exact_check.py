#!/usr/bin/env python3
"""Exact arithmetic for the Wave 36 ternary polar-graph rank bound.

The mathematics is recorded in
``agents/2026-07-26-wave36-ternary-polar-bound.md``.  This checker does not
construct an endpoint matrix.  It verifies the finite-field point counts,
strongly-regular graph parameters, eigenvalues, and exact spectral-mixing
inequalities used to exclude ranks at most eleven.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any


ORDER = 3
TARGET_POINT_COUNT = 231
TARGET_INTERNAL_DEGREE = 162


def norm_residue_counts(dimension: int, determinant_class: int) -> tuple[int, int, int]:
    """Count vectors of each norm for diag(1,...,1,determinant_class)."""

    if dimension < 1:
        raise ValueError("dimension must be positive")
    if determinant_class not in (1, 2):
        raise ValueError("determinant class must be 1 or 2")

    counts = [1, 0, 0]
    coefficients = [1] * (dimension - 1) + [determinant_class]
    for coefficient in coefficients:
        updated = [0, 0, 0]
        for residue, count in enumerate(counts):
            updated[residue] += count
            # The two nonzero field elements have square one.
            updated[(residue + coefficient) % ORDER] += 2 * count
        counts = updated
    if sum(counts) != ORDER**dimension:
        raise AssertionError("quadratic-form vector count is incomplete")
    return tuple(counts)


def norm_two_projective_points(dimension: int, determinant_class: int) -> int:
    """Number of projective points represented by norm-two vectors."""

    count = norm_residue_counts(dimension, determinant_class)[2]
    if count % 2:
        raise AssertionError("nonzero vectors must occur in antipodal pairs")
    return count // 2


def polar_graph_parameters(dimension: int, determinant_class: int) -> dict[str, int]:
    """Parameters of orthogonality on norm-two projective points over F_3."""

    if dimension < 3:
        raise ValueError("dimension must be at least three")

    vertex_count = norm_two_projective_points(dimension, determinant_class)
    # A norm-two point has an orthogonal complement whose determinant class
    # is toggled because 2^{-1}=2 in F_3.
    degree = norm_two_projective_points(dimension - 1, 3 - determinant_class)
    # Two orthogonal norm-two points span determinant 2*2=1, so their
    # orthogonal complement retains the ambient determinant class.
    adjacent_common = norm_two_projective_points(
        dimension - 2, determinant_class
    )
    denominator = vertex_count - degree - 1
    numerator = degree * (degree - adjacent_common - 1)
    if denominator <= 0 or numerator % denominator:
        raise AssertionError("nonintegral strongly-regular mu parameter")
    nonadjacent_common = numerator // denominator

    discriminant = (
        (adjacent_common - nonadjacent_common) ** 2
        + 4 * (degree - nonadjacent_common)
    )
    square_root = isqrt(discriminant)
    if square_root * square_root != discriminant:
        raise AssertionError("nonintegral restricted eigenvalues")
    positive_eigenvalue = (
        adjacent_common - nonadjacent_common + square_root
    ) // 2
    negative_eigenvalue = (
        adjacent_common - nonadjacent_common - square_root
    ) // 2

    if (
        positive_eigenvalue + negative_eigenvalue
        != adjacent_common - nonadjacent_common
    ):
        raise AssertionError("restricted eigenvalue sum mismatch")
    if (
        positive_eigenvalue * negative_eigenvalue
        != nonadjacent_common - degree
    ):
        raise AssertionError("restricted eigenvalue product mismatch")

    positive_multiplicity_numerator = (
        -degree - (vertex_count - 1) * negative_eigenvalue
    )
    positive_multiplicity_denominator = (
        positive_eigenvalue - negative_eigenvalue
    )
    if (
        positive_multiplicity_numerator
        % positive_multiplicity_denominator
    ):
        raise AssertionError("nonintegral eigenvalue multiplicity")
    positive_multiplicity = (
        positive_multiplicity_numerator
        // positive_multiplicity_denominator
    )
    negative_multiplicity = vertex_count - 1 - positive_multiplicity

    return {
        "dimension": dimension,
        "determinant_class": determinant_class,
        "vertex_count": vertex_count,
        "degree": degree,
        "lambda": adjacent_common,
        "mu": nonadjacent_common,
        "positive_eigenvalue": positive_eigenvalue,
        "positive_multiplicity": positive_multiplicity,
        "negative_eigenvalue": negative_eigenvalue,
        "negative_multiplicity": negative_multiplicity,
    }


def mixing_upper_bound(
    parameters: dict[str, int],
    subset_size: int = TARGET_POINT_COUNT,
) -> Fraction:
    """Upper bound for the average induced degree of a subset."""

    vertex_count = parameters["vertex_count"]
    degree = parameters["degree"]
    theta = parameters["positive_eigenvalue"]
    if subset_size > vertex_count:
        raise ValueError("subset is larger than the ambient graph")
    return Fraction(
        degree * subset_size + theta * (vertex_count - subset_size),
        vertex_count,
    )


def fraction_record(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "display": str(value),
        "decimal_12": f"{float(value):.12f}",
    }


def build_result() -> dict[str, Any]:
    point_count_table = []
    for dimension in range(1, 13):
        point_count_table.append(
            {
                "dimension": dimension,
                "square_determinant": norm_two_projective_points(
                    dimension, 1
                ),
                "nonsquare_determinant": norm_two_projective_points(
                    dimension, 2
                ),
            }
        )

    cases = []
    for dimension in range(7, 13):
        for determinant_class in (1, 2):
            parameters = polar_graph_parameters(
                dimension, determinant_class
            )
            upper = mixing_upper_bound(parameters)
            excluded = upper < TARGET_INTERNAL_DEGREE
            cases.append(
                {
                    **parameters,
                    "mixing_upper_average_induced_degree": fraction_record(
                        upper
                    ),
                    "target_average_induced_degree": TARGET_INTERNAL_DEGREE,
                    "excluded": excluded,
                }
            )

    excluded_through_eleven = all(
        case["excluded"] for case in cases if case["dimension"] <= 11
    )
    rank_twelve = [
        case for case in cases if case["dimension"] == 12
    ]
    if not excluded_through_eleven:
        raise AssertionError("a rank at most eleven survived")
    if [case["excluded"] for case in rank_twelve] != [False, True]:
        raise AssertionError("unexpected rank-twelve determinant outcome")

    return {
        "claim_label": "CANDIDATE_PENDING_INDEPENDENT_VERIFICATION",
        "field_order": ORDER,
        "endpoint_projective_point_count": TARGET_POINT_COUNT,
        "endpoint_orthogonal_companions_per_point": TARGET_INTERNAL_DEGREE,
        "distinctness_norm_check": {
            "congruent_or_antipodal_integer_combination_norm_squared": 450,
            "orthogonal_endpoint_row_combination_norm_squared": 882,
            "distinct_projective_points": True,
        },
        "point_count_table": point_count_table,
        "polar_graph_cases": cases,
        "derived_rank_floor": 12,
        "rank_twelve_surviving_determinant_classes": ["square"],
        "endpoint_excluded": False,
        "global_upper_bound_on_n3": 4158,
        "limitations": [
            "The endpoint matrix and graph are hypothetical; neither is constructed.",
            "The calculation only sharpens a conditional modular-rank constraint.",
            "The argument requires independent adversarial verification before promotion.",
            "The surviving rank-twelve square-determinant case and all ranks 13 through 44 remain feasible under this test.",
        ],
    }


def canonical_bytes(result: dict[str, Any]) -> bytes:
    return (
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    data = canonical_bytes(build_result())
    if args.verify:
        existing = args.verify.read_bytes()
        if existing != data:
            raise SystemExit(
                "verification mismatch: "
                f"expected {sha256_bytes(data)}, got {sha256_bytes(existing)}"
            )
        print(sha256_bytes(data))
        return
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)
        print(sha256_bytes(data))
        return
    print(data.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
