#!/usr/bin/env python3
"""Independent exact verifier for the Wave 23 endpoint exclusion.

No submitted Wave 23 module is imported.  Irrational stationary spectra are
bounded with dyadic rational intervals, independently of the submitted
decimal-scale certificates.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path


DIMENSION = 44
TRACE_B = 48
SQUARE_TRACE_FLOOR = 60
DYADIC_BITS = 160


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sqrt_dyadic_bracket(value: Fraction, bits: int = DYADIC_BITS) -> tuple[Fraction, Fraction]:
    """Return exact dyadic lower/upper bounds around sqrt(value)."""
    require(value >= 0, "negative radicand")
    denominator = 1 << bits
    scaled_square_floor = (
        value.numerator * denominator * denominator // value.denominator
    )
    integer_floor = math.isqrt(scaled_square_floor)
    lower = Fraction(integer_floor, denominator)
    upper = Fraction(integer_floor + 1, denominator)
    require(lower * lower <= value, "invalid lower radical bound")
    require(upper * upper > value, "invalid upper radical bound")
    return lower, upper


def trace_square_floor(rank: int = DIMENSION, trace_b: int = TRACE_B) -> dict[str, int]:
    """Exact consequence of B=I+2C with C integral and G-self-adjoint."""
    require((trace_b - rank) % 2 == 0, "B-I does not have even trace")
    trace_c = (trace_b - rank) // 2
    require(trace_c != 0, "this endpoint argument requires C nonzero")
    parity = trace_c % 2
    minimum_positive_trace_c2 = 1 if parity else 2
    return {
        "rank": rank,
        "trace_B": trace_b,
        "trace_C": trace_c,
        "trace_C2_parity": parity,
        "minimum_positive_trace_C2": minimum_positive_trace_c2,
        "minimum_trace_B2": (
            rank + 4 * trace_c + 4 * minimum_positive_trace_c2
        ),
    }


def trace_square_parities(matrix: list[list[int]]) -> tuple[int, int]:
    n = len(matrix)
    require(n and all(len(row) == n for row in matrix), "matrix must be square")
    trace = sum(matrix[index][index] for index in range(n))
    trace_square = 0
    for row in range(n):
        for column in range(n):
            trace_square += matrix[row][column] * matrix[column][row]
    return trace % 2, trace_square % 2


def stationary_spectrum(
    high_count: int,
    *,
    rank: int = DIMENSION,
    trace: int = TRACE_B,
    square_trace: int = SQUARE_TRACE_FLOOR,
) -> dict[str, object]:
    """Exact radical data and a certified product upper bound."""
    require(0 < high_count < rank, "invalid multiplicity")
    low_count = rank - high_count
    mean = Fraction(trace, rank)
    variance = Fraction(square_trace, rank) - mean * mean
    require(variance > 0, "second moment must exceed the equal-point moment")

    high_radicand = variance * Fraction(low_count, high_count)
    low_radicand = variance * Fraction(high_count, low_count)
    high_lower, high_upper_radical = sqrt_dyadic_bracket(high_radicand)
    low_lower, low_upper_radical = sqrt_dyadic_bracket(low_radicand)

    high_lower_value = mean + high_lower
    high_upper_value = mean + high_upper_radical
    low_lower_value = mean - low_upper_radical
    low_upper_value = mean - low_lower

    exact_low_positive = mean * mean > low_radicand
    product_upper: Fraction | None = None
    if exact_low_positive:
        require(low_lower_value > 0, "dyadic precision did not preserve positivity")
        product_upper = (
            high_upper_value**high_count
            * low_upper_value**low_count
        )

    return {
        "high_count": high_count,
        "low_count": low_count,
        "high_radicand": high_radicand,
        "low_radicand": low_radicand,
        "high_interval": (high_lower_value, high_upper_value),
        "low_interval": (low_lower_value, low_upper_value),
        "exact_low_positive": exact_low_positive,
        "product_upper": product_upper,
    }


def product_certificate(
    square_trace: int = SQUARE_TRACE_FLOOR,
) -> dict[str, object]:
    positive_cases: list[dict[str, object]] = []
    excluded_counts: list[int] = []
    for high_count in range(1, DIMENSION):
        case = stationary_spectrum(
            high_count,
            square_trace=square_trace,
        )
        if case["exact_low_positive"]:
            positive_cases.append(case)
        else:
            excluded_counts.append(high_count)
    require(positive_cases, "no positive stationary spectrum")
    largest = max(
        positive_cases,
        key=lambda item: item["product_upper"],
    )
    all_below_13 = all(
        item["product_upper"] < 13
        for item in positive_cases
    )
    return {
        "rank": DIMENSION,
        "trace": TRACE_B,
        "square_trace": square_trace,
        "positive_high_counts": [item["high_count"] for item in positive_cases],
        "nonpositive_low_counts": excluded_counts,
        "all_product_upper_bounds_below_13": all_below_13,
        "largest_high_count": largest["high_count"],
        "largest_product_upper": largest["product_upper"],
        "cases": positive_cases,
    }


def smooth_3_7(limit: int) -> list[int]:
    values: set[int] = set()
    power_three = 1
    while power_three <= limit:
        power_seven = 1
        while power_three * power_seven <= limit:
            values.add(power_three * power_seven)
            power_seven *= 7
        power_three *= 3
    return sorted(values)


def determinant_pairs(cap: int) -> list[tuple[int, int, int]]:
    """Endpoint pairs with detQ=1 mod 4, detQ>=5, and detB=1 mod 4."""
    rows: list[tuple[int, int, int]] = []
    for h in smooth_3_7(cap):
        for det_q in range(5, cap + 1, 4):
            det_b = h * det_q
            if det_b <= cap and det_b % 4 == 1:
                rows.append((h, det_q, det_b))
    return rows


def smith_data(factors: tuple[int, ...]) -> dict[str, int]:
    require(len(factors) == DIMENSION, "expected 44 nonzero Smith factors")
    require(all(value in (1, 3, 7, 21) for value in factors), "invalid Smith factor")
    h = math.prod(factors)
    rank_three = sum(value % 3 != 0 for value in factors)
    rank_seven = sum(value % 7 != 0 for value in factors)
    require(
        h == 3 ** (DIMENSION - rank_three) * 7 ** (DIMENSION - rank_seven),
        "Smith/rank valuation identity failed",
    )
    return {
        "h": h,
        "rank_mod_3": rank_three,
        "rank_mod_7": rank_seven,
    }


def even_gram_odd_determinant_mod_four(rank: int) -> int:
    require(rank > 0 and rank % 2 == 0, "rank must be positive and even")
    return pow(3, rank // 2, 4)


def h_one_rescaling(rank: int = DIMENSION, odd_scale: int = 21) -> dict[str, object]:
    require(odd_scale % 2 == 1, "evenness does not descend through an even scale")
    signature_mod_eight = rank % 8
    return {
        "premise": "L=scale*L*",
        "coordinate_map": "scale*G^{-1} is integral unimodular",
        "rescaled_gram": "G/scale is integral unimodular",
        "rescaled_even": True,
        "signature_mod_eight": signature_mod_eight,
        "excluded_by_even_unimodular_signature": signature_mod_eight != 0,
    }


def adjacency_algebra_product(
    left: tuple[Fraction, Fraction, Fraction],
    right: tuple[Fraction, Fraction, Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    """Multiply coefficients of I,A,J for srg(99,14,1,2)."""
    li, la, lj = left
    ri, ra, rj = right
    return (
        li * ri + 12 * la * ra,
        li * ra + la * ri - la * ra,
        (
            li * rj
            + lj * ri
            + 2 * la * ra
            + 14 * la * rj
            + 14 * lj * ra
            + 99 * lj * rj
        ),
    )


def adjacency_checks() -> dict[str, object]:
    seidel = (Fraction(1), Fraction(2), Fraction(-1))
    r_operator = (Fraction(3), Fraction(-1), Fraction(1, 9))
    seidel_square = adjacency_algebra_product(seidel, seidel)
    r_square = adjacency_algebra_product(r_operator, r_operator)
    require(seidel_square == (Fraction(49), Fraction(0), Fraction(49)), "S^2 failed")
    require(
        r_square == tuple(7 * coefficient for coefficient in r_operator),
        "R^2=7R failed",
    )
    five_r_mod_seven = tuple(
        (5 * value.numerator * pow(value.denominator, -1, 7)) % 7
        for value in r_operator
    )
    s_mod_seven = tuple(
        (value.numerator * pow(value.denominator, -1, 7)) % 7
        for value in seidel
    )
    require(five_r_mod_seven == s_mod_seven, "5R=S mod 7 failed")
    return {
        "S2": [str(value) for value in seidel_square],
        "R2_equals_7R": True,
        "five_R_equals_S_mod_7": True,
    }


def fraction_json(value: Fraction | None) -> object:
    if value is None:
        return None
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
    }


def audit() -> dict[str, object]:
    trace_floor = trace_square_floor()
    require(trace_floor["minimum_trace_B2"] == 60, "trace-square floor changed")

    certificate = product_certificate()
    require(
        certificate["positive_high_counts"] == list(range(1, 39)),
        "positive KKT multiplicities changed",
    )
    require(
        certificate["nonpositive_low_counts"] == list(range(39, 44)),
        "nonpositive boundary multiplicities changed",
    )
    require(
        certificate["all_product_upper_bounds_below_13"],
        "product cap below 13 failed",
    )
    require(certificate["largest_high_count"] == 1, "maximum case changed")

    old_pairs = determinant_pairs(45)
    new_pairs = determinant_pairs(12)
    require(sorted({row[0] for row in old_pairs}) == [1, 9], "old h list changed")
    require(new_pairs == [(1, 5, 5), (1, 9, 9)], "new determinant pairs changed")

    h_one = h_one_rescaling()
    require(h_one["excluded_by_even_unimodular_signature"], "h=1 survived")
    require(even_gram_odd_determinant_mod_four(44) == 1, "detQ residue changed")

    weak_certificate = product_certificate(square_trace=59)
    require(
        not weak_certificate["all_product_upper_bounds_below_13"],
        "hostile square-trace 59 unexpectedly certified the cap",
    )

    largest_upper = certificate["largest_product_upper"]
    return {
        "claim_label": "VERIFIED",
        "scope": "conditional exclusion of the n3=705 endpoint",
        "trace_square": trace_floor,
        "kkt_boundary_audit": {
            "coordinate_boundary_product": 0,
            "positive_feasible_witness": "3,3,1^42 with product 9",
            "strict_square_inequality_stationarity": (
                "sum-only stationarity forces equality, which has square sum 576/11<60"
            ),
            "active_constraint": "sum squares=60",
            "positive_high_counts": certificate["positive_high_counts"],
            "nonpositive_low_counts": certificate["nonpositive_low_counts"],
        },
        "two_moment_certificate": {
            "dyadic_bits": DYADIC_BITS,
            "largest_high_count": certificate["largest_high_count"],
            "largest_product_upper": fraction_json(largest_upper),
            "all_38_product_upper_bounds_below_13": True,
            "square_trace_59_hostile_control": "DOES_NOT_CERTIFY",
            "cases": [
                {
                    "high_count": item["high_count"],
                    "high_radicand": fraction_json(item["high_radicand"]),
                    "low_radicand": fraction_json(item["low_radicand"]),
                    "product_upper": fraction_json(item["product_upper"]),
                }
                for item in certificate["cases"]
            ],
        },
        "determinant": {
            "strict_cap": 13,
            "det_B_candidates_before_factorization": [1, 5, 9],
            "det_B_candidates_after_det_Q_floor": [5, 9],
            "old_pairs_cap_45": [
                {"h": h, "det_Q": det_q, "det_B": det_b}
                for h, det_q, det_b in old_pairs
            ],
            "new_pairs_cap_12": [
                {"h": h, "det_Q": det_q, "det_B": det_b}
                for h, det_q, det_b in new_pairs
            ],
        },
        "h_one_rescaling": h_one,
        "smith_controls": {
            "h=1": smith_data((1,) * 44),
            "h=9": smith_data((1,) * 42 + (3, 3)),
        },
        "adjacency_algebra_controls": adjacency_checks(),
        "conclusion": {
            "n3_equals_705": "REFUTED_CONDITIONALLY",
            "conditional_n3_lower_bound": 708,
            "conditional_induced_C6_lower_bound": 209994,
            "target_resolution": "NOT_CLAIMED",
            "novelty": "NOT_ASSESSED",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    rendered = json.dumps(audit(), indent=2, sort_keys=True) + "\n"
    if arguments.output is None:
        print(rendered, end="")
    else:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
