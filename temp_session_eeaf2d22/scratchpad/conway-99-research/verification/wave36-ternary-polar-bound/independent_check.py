#!/usr/bin/env python3
"""Independent verifier for the Wave 36 ternary polar-graph rank bound.

No discovery-side module or result is imported.  The finite checks reconstruct
the F_3 quadratic-space counts, orthogonality-graph parameters, spectrum, and
exact mixing inequality from the frozen endpoint constants.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
import itertools
import json
import math
from pathlib import Path


FIELD = 3
SELECTED_POINTS = 231
SELECTED_DEGREE = 162
RATIONAL_RANK = 44


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def form_diagonal(dimension: int, determinant_class: int) -> tuple[int, ...]:
    require(dimension >= 1, "dimension must be positive")
    require(determinant_class in (1, 2), "determinant class must be 1 or 2")
    return (1,) * (dimension - 1) + (determinant_class,)


def bilinear(
    left: tuple[int, ...],
    right: tuple[int, ...],
    determinant_class: int,
) -> int:
    diagonal = form_diagonal(len(left), determinant_class)
    require(len(left) == len(right), "dimension mismatch")
    return sum(a * x * y for a, x, y in zip(diagonal, left, right)) % FIELD


def quadratic(vector: tuple[int, ...], determinant_class: int) -> int:
    return bilinear(vector, vector, determinant_class)


@lru_cache(maxsize=None)
def projective_norm_two_points(
    dimension: int,
    determinant_class: int,
) -> tuple[tuple[int, ...], ...]:
    """Enumerate one representative per norm-two projective line."""

    points: list[tuple[int, ...]] = []
    for vector in itertools.product(range(FIELD), repeat=dimension):
        try:
            first = next(index for index, value in enumerate(vector) if value)
        except StopIteration:
            continue
        inverse = pow(vector[first], -1, FIELD)
        normalized = tuple((inverse * value) % FIELD for value in vector)
        if normalized == vector and quadratic(vector, determinant_class) == 2:
            points.append(vector)
    return tuple(points)


def add_coordinate(distribution: tuple[int, int, int], coefficient: int) -> tuple[int, int, int]:
    """Convolve a norm-residue distribution with one F_3 coordinate."""

    require(coefficient in (1, 2), "invalid diagonal coefficient")
    result = [0, 0, 0]
    for residue, count in enumerate(distribution):
        result[residue] += count  # coordinate zero
        result[(residue + coefficient) % FIELD] += 2 * count  # coordinate +/-1
    return tuple(result)  # type: ignore[return-value]


@lru_cache(maxsize=None)
def norm_residue_distribution(dimension: int, determinant_class: int) -> tuple[int, int, int]:
    if dimension == 0:
        return (1, 0, 0)
    distribution = (1, 0, 0)
    for coefficient in form_diagonal(dimension, determinant_class):
        distribution = add_coordinate(distribution, coefficient)
    require(sum(distribution) == FIELD**dimension, "residue distribution total mismatch")
    return distribution


@lru_cache(maxsize=None)
def norm_two_projective_count(dimension: int, determinant_class: int) -> int:
    if dimension == 0:
        return 0
    vector_count = norm_residue_distribution(dimension, determinant_class)[2]
    require(vector_count % 2 == 0, "norm-two vectors do not pair under sign")
    return vector_count // 2


def point_count_table(max_dimension: int = 12) -> list[dict[str, int]]:
    return [
        {
            "dimension": dimension,
            "square": norm_two_projective_count(dimension, 1),
            "nonsquare": norm_two_projective_count(dimension, 2),
        }
        for dimension in range(1, max_dimension + 1)
    ]


def exact_srg_parameters(dimension: int, determinant_class: int) -> dict[str, int]:
    """Parameters of the norm-two projective orthogonality graph.

    The nonadjacent common-neighbor count is obtained directly from its
    degenerate two-space:

      span(v,w)^perp = <u> direct_sum K,

    where u is the radical and K is nondegenerate of dimension r-3 and the
    ambient determinant class.  Each norm-two projective point of K has three
    projective lifts, hence mu=3*N_(r-3)^epsilon.
    """

    require(dimension >= 3, "SRG parameter formula requires dimension at least three")
    toggled = 2 if determinant_class == 1 else 1
    vertex_count = norm_two_projective_count(dimension, determinant_class)
    degree = norm_two_projective_count(dimension - 1, toggled)
    lam = norm_two_projective_count(dimension - 2, determinant_class)
    mu = 3 * norm_two_projective_count(dimension - 3, determinant_class)
    require(
        (vertex_count - degree - 1) * mu == degree * (degree - lam - 1),
        "strongly regular two-path identity failed",
    )
    return {
        "v": vertex_count,
        "k": degree,
        "lambda": lam,
        "mu": mu,
    }


@lru_cache(maxsize=None)
def enumerated_graph_parameters(dimension: int, determinant_class: int) -> dict[str, object]:
    """Exhaustively check all pairs in a manageable polar graph."""

    points = projective_norm_two_points(dimension, determinant_class)
    expected = exact_srg_parameters(dimension, determinant_class)
    count = len(points)
    require(count == expected["v"], "enumerated point count mismatch")

    neighbor_masks: list[int] = []
    for left in points:
        mask = 0
        for index, right in enumerate(points):
            if bilinear(left, right, determinant_class) == 0:
                mask |= 1 << index
        neighbor_masks.append(mask)

    degrees = {mask.bit_count() for mask in neighbor_masks}
    require(degrees == {expected["k"]}, "enumerated degrees are not constant")

    adjacent_common: set[int] = set()
    nonadjacent_common: set[int] = set()
    nonadjacent_gram_determinants: set[int] = set()
    for left in range(count):
        for right in range(left + 1, count):
            common = (neighbor_masks[left] & neighbor_masks[right]).bit_count()
            inner = bilinear(points[left], points[right], determinant_class)
            if inner == 0:
                adjacent_common.add(common)
            else:
                nonadjacent_common.add(common)
                gram_det = (2 * 2 - inner * inner) % FIELD
                nonadjacent_gram_determinants.add(gram_det)

    require(adjacent_common == {expected["lambda"]}, "adjacent pair count mismatch")
    require(nonadjacent_common == {expected["mu"]}, "nonadjacent pair count mismatch")
    require(nonadjacent_gram_determinants == {0}, "nonadjacent span is not uniformly degenerate")
    return {
        "dimension": dimension,
        "determinant_class": determinant_class,
        "parameters": expected,
        "all_degrees": sorted(degrees),
        "all_adjacent_common_neighbor_counts": sorted(adjacent_common),
        "all_nonadjacent_common_neighbor_counts": sorted(nonadjacent_common),
        "all_nonadjacent_gram_determinants": sorted(nonadjacent_gram_determinants),
    }


def eigen_data(parameters: dict[str, int]) -> dict[str, int]:
    v = parameters["v"]
    k = parameters["k"]
    lam = parameters["lambda"]
    mu = parameters["mu"]
    linear = lam - mu
    discriminant = linear * linear + 4 * (k - mu)
    root = math.isqrt(discriminant)
    require(root * root == discriminant, "non-square SRG eigenvalue discriminant")
    require((linear + root) % 2 == 0, "nonintegral positive eigenvalue")
    theta = (linear + root) // 2
    tau = (linear - root) // 2
    denominator = theta - tau
    numerator = -k - tau * (v - 1)
    require(numerator % denominator == 0, "nonintegral eigenvalue multiplicity")
    theta_mult = numerator // denominator
    tau_mult = v - 1 - theta_mult
    require(k + theta_mult * theta + tau_mult * tau == 0, "trace equation failed")
    require(
        k * k + theta_mult * theta * theta + tau_mult * tau * tau == v * k,
        "trace-square equation failed",
    )
    require(theta < k, "nonprincipal eigenvalue reached the degree")
    return {
        "theta": theta,
        "tau": tau,
        "theta_multiplicity": theta_mult,
        "tau_multiplicity": tau_mult,
    }


def mixing_upper_average_degree(
    parameters: dict[str, int],
    theta: int,
    selected_points: int = SELECTED_POINTS,
) -> Fraction:
    """Exact upper bound theta+(k-theta)m/v."""

    return Fraction(
        parameters["k"] * selected_points
        + theta * (parameters["v"] - selected_points),
        parameters["v"],
    )


def polar_case(dimension: int, determinant_class: int) -> dict[str, object]:
    parameters = exact_srg_parameters(dimension, determinant_class)
    spectrum = eigen_data(parameters)
    bound = mixing_upper_average_degree(parameters, spectrum["theta"])
    return {
        "dimension": dimension,
        "determinant_class": determinant_class,
        **parameters,
        **spectrum,
        "mixing_bound": {
            "numerator": bound.numerator,
            "denominator": bound.denominator,
            "display": (
                str(bound.numerator)
                if bound.denominator == 1
                else f"{bound.numerator}/{bound.denominator}"
            ),
        },
        "excluded": bound < SELECTED_DEGREE,
    }


def endpoint_distinctness_check() -> dict[str, object]:
    alphabet = (0, 2, -2)
    require(len({value % 3 for value in alphabet}) == 3, "alphabet residues collide")
    require((-13) % 3 == 2, "diagonal residue mismatch")
    false_norm = 2 * (-13 - 2) ** 2
    true_norm = 2 * 441
    require(false_norm == 450 and true_norm == 882, "row norm arithmetic mismatch")
    require(false_norm != true_norm, "proportional row contradiction failed")
    return {
        "projective_points": SELECTED_POINTS,
        "point_norm": 2,
        "forced_equal_row_difference": "-15(e_i-e_j)",
        "forced_antipodal_row_sum": "-15(e_i+e_j)",
        "false_integer_combination_norm_squared": false_norm,
        "orthogonal_row_combination_norm_squared": true_norm,
        "distinct_projective_points": True,
        "orthogonal_selected_neighbors_per_point": SELECTED_DEGREE,
    }


def build_result() -> dict[str, object]:
    # Brute-force counts independently validate the recurrence where direct
    # enumeration remains tiny.
    brute_count_checks = []
    for dimension in range(1, 8):
        for determinant_class in (1, 2):
            brute = len(projective_norm_two_points(dimension, determinant_class))
            recurrence = norm_two_projective_count(dimension, determinant_class)
            require(brute == recurrence, "brute-force/recurrence count mismatch")
            brute_count_checks.append(
                {
                    "dimension": dimension,
                    "determinant_class": determinant_class,
                    "count": brute,
                }
            )

    # Exhaust every pair in both determinant classes from dimension four
    # through seven.  The dimension-three nonsquare graph is complete, so it
    # has no nonadjacent pair on which to test the degenerate-span count.
    enumerated_srg_checks = [
        enumerated_graph_parameters(dimension, determinant_class)
        for dimension in range(4, 8)
        for determinant_class in (1, 2)
    ]

    cases = [
        polar_case(dimension, determinant_class)
        for dimension in range(7, 13)
        for determinant_class in (1, 2)
    ]
    for case in cases:
        bound = Fraction(
            case["mixing_bound"]["numerator"],  # type: ignore[index]
            case["mixing_bound"]["denominator"],  # type: ignore[index]
        )
        require(case["excluded"] == (bound < SELECTED_DEGREE), "exclusion mismatch")

    lower_cases = [case for case in cases if case["dimension"] <= 11]
    require(all(case["excluded"] for case in lower_cases), "a rank <=11 class survives")
    rank_twelve = [case for case in cases if case["dimension"] == 12]
    surviving_rank_twelve = [
        "square" if case["determinant_class"] == 1 else "nonsquare"
        for case in rank_twelve
        if not case["excluded"]
    ]
    require(surviving_rank_twelve == ["square"], "rank-twelve class boundary mismatch")

    higher_cases = [
        polar_case(dimension, determinant_class)
        for dimension in range(13, RATIONAL_RANK + 1)
        for determinant_class in (1, 2)
    ]
    require(
        all(not case["excluded"] for case in higher_cases),
        "a rank from thirteen through forty-four was unexpectedly excluded",
    )
    minimum_higher_case = min(
        higher_cases,
        key=lambda case: Fraction(
            case["mixing_bound"]["numerator"],  # type: ignore[index]
            case["mixing_bound"]["denominator"],  # type: ignore[index]
        ),
    )
    minimum_higher_bound = Fraction(
        minimum_higher_case["mixing_bound"]["numerator"],  # type: ignore[index]
        minimum_higher_case["mixing_bound"]["denominator"],  # type: ignore[index]
    )

    # Hostile check: treating the singular nonadjacent two-space as
    # nondegenerate codimension two gives the adjacent count, not mu.
    hostile = []
    for determinant_class in (1, 2):
        params = exact_srg_parameters(8, determinant_class)
        naive = norm_two_projective_count(6, determinant_class)
        require(naive != params["mu"], "degenerate-span hostile control went inactive")
        hostile.append(
            {
                "determinant_class": determinant_class,
                "incorrect_nondegenerate_codim2_count": naive,
                "correct_degenerate_count": params["mu"],
            }
        )

    return {
        "schema_version": 1,
        "role": "verifier",
        "scope": "conditional n3=4158 ternary polar-graph rank bound",
        "frozen_public_head": "697cc02bcbe16b69aaf08822298e03c66329c64c",
        "endpoint": endpoint_distinctness_check(),
        "factorization_lemma": (
            "For symmetric rank-r A over F_3, A=VHV^T with V full column "
            "rank and H symmetric nondegenerate."
        ),
        "point_count_table": point_count_table(),
        "brute_force_point_count_checks": brute_count_checks,
        "strong_regularity_proof_data": {
            "degree_complement_class": "2*epsilon",
            "adjacent_complement_class": "epsilon",
            "nonadjacent_gram_determinant": 0,
            "nonadjacent_complement_model": "<u> direct_sum K",
            "nonadjacent_K_dimension": "r-3",
            "nonadjacent_K_determinant_class": "epsilon",
            "projective_lifts_per_K_point": 3,
            "mu_formula": "3*N_(r-3)^epsilon",
            "transitivity": (
                "Adjacent pairs have a unique nondegenerate Gram type. "
                "For a nonadjacent pair, signs normalize inner product to 1; "
                "a canonical H_hyp direct-sum <v> direct-sum K decomposition "
                "shows all ordered pairs are isometric."
            ),
            "exhaustive_small_graph_checks": enumerated_srg_checks,
            "hostile_degenerate_span_checks": hostile,
        },
        "polar_cases": cases,
        "ranks_13_through_44_check": {
            "checked_case_count": len(higher_cases),
            "all_survive_mixing_test": True,
            "minimum_bound_case": {
                "dimension": minimum_higher_case["dimension"],
                "determinant_class": minimum_higher_case["determinant_class"],
                "bound": {
                    "numerator": minimum_higher_bound.numerator,
                    "denominator": minimum_higher_bound.denominator,
                },
            },
        },
        "conclusion": {
            "rank_F3_M_lower_bound": 12,
            "rank_twelve_surviving_determinant_classes": surviving_rank_twelve,
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "conway_99": "UNKNOWN",
            "novelty": "NOT_ASSESSED",
        },
        "limitations": [
            "The endpoint C, factor configuration, and graph are hypothetical.",
            "The result is a necessary modular-rank condition, not endpoint exclusion.",
            "The finite checker accompanies the general transitivity and degenerate-span proof.",
            "Rank twelve square class and ranks thirteen through forty-four survive this test.",
        ],
    }


def canonical_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    require(not (args.output and args.verify), "choose only one output mode")
    text = canonical_json(build_result())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8", newline="\n")
    elif args.verify:
        require(args.verify.read_text(encoding="utf-8") == text, "stored result mismatch")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
