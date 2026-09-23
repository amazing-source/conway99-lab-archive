#!/usr/bin/env python3
"""Independent exact audit of the simpler Wave 23 endpoint cross-check.

This module imports no candidate code and does not use the earlier KKT
optimization.  The needed Maclaurin case is proved by AM--GM on all pair
products.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


RANK = 44
TRACE_B = 48
PROJECTOR_SCALE = 21


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def exact_determinant(matrix: list[list[int]]) -> int:
    """Fraction-free Bareiss determinant for finite hostile checks."""
    n = len(matrix)
    require(all(len(row) == n for row in matrix), "matrix must be square")
    if n == 0:
        return 1
    work = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for pivot_index in range(n - 1):
        pivot_row = next(
            (
                row
                for row in range(pivot_index, n)
                if work[row][pivot_index] != 0
            ),
            None,
        )
        if pivot_row is None:
            return 0
        if pivot_row != pivot_index:
            work[pivot_index], work[pivot_row] = (
                work[pivot_row],
                work[pivot_index],
            )
            sign *= -1
        pivot = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, n):
            for column in range(pivot_index + 1, n):
                numerator = (
                    work[row][column] * pivot
                    - work[row][pivot_index] * work[pivot_index][column]
                )
                require(numerator % previous == 0, "Bareiss division failed")
                work[row][column] = numerator // previous
        previous = pivot
    return sign * work[-1][-1]


def even_gram_odd_determinant_residue(rank: int) -> int:
    require(rank > 0 and rank % 2 == 0, "rank must be positive and even")
    return pow(3, rank // 2, 4)


def scaled_dual_facts(
    *,
    rank: int = RANK,
    scale: int = PROJECTOR_SCALE,
) -> dict[str, object]:
    require(rank == 44, "frozen lattice rank changed")
    require(scale == 21 and scale % 2 == 1, "frozen odd scale changed")
    residue = even_gram_odd_determinant_residue(rank)
    return {
        "matrix": "S=21*G^{-1}",
        "integral_from_inclusion": "21L* subset L",
        "symmetric_positive_definite": True,
        "determinant": "21^44/det(G)=h",
        "even_diagonal": (
            "odd principal cofactors of even G vanish modulo 2"
        ),
        "determinant_mod_4": residue,
        "h_one_excluded": rank % 8 != 0,
    }


def first_integer_with_residue_at_least(
    lower: Fraction,
    *,
    residue: int,
    modulus: int,
) -> int:
    candidate = (lower.numerator + lower.denominator - 1) // lower.denominator
    while candidate % modulus != residue % modulus:
        candidate += 1
    return candidate


def trace_square_floor(
    *,
    rank: int = RANK,
    trace_b: int = TRACE_B,
) -> dict[str, object]:
    require((trace_b - rank) % 2 == 0, "B-I must have even trace")
    trace_c = (trace_b - rank) // 2
    trace_c2_parity = trace_c % 2
    trace_b2_mod_8 = (
        rank + 4 * trace_c + 4 * trace_c2_parity
    ) % 8
    cauchy = Fraction(trace_b * trace_b, rank)
    minimum = first_integer_with_residue_at_least(
        cauchy,
        residue=trace_b2_mod_8,
        modulus=8,
    )
    return {
        "rank": rank,
        "trace_B": trace_b,
        "trace_C": trace_c,
        "trace_C2_mod_2": trace_c2_parity,
        "trace_B2_mod_8": trace_b2_mod_8,
        "cauchy_lower": cauchy,
        "minimum_trace_B2": minimum,
        "minimum_trace_A4_squared": PROJECTOR_SCALE**2 * minimum,
    }


def pair_product_maclaurin(
    trace_square_lower: int,
    *,
    rank: int = RANK,
    trace_b: int = TRACE_B,
) -> dict[str, object]:
    """Exact k=2 Maclaurin bound via AM--GM on pair products.

    For positive eigenvalues lambda_i, the arithmetic mean of the
    C(rank,2) numbers lambda_i*lambda_j is e2/C(rank,2).  Their geometric
    mean is det(B)^(2/rank).
    """
    require(rank > 0 and rank % 2 == 0, "rank must be positive and even")
    e2_upper = Fraction(trace_b * trace_b - trace_square_lower, 2)
    pair_count = math.comb(rank, 2)
    normalized = e2_upper / pair_count
    determinant_bound = normalized ** (rank // 2)
    integer_cap = determinant_bound.numerator // determinant_bound.denominator
    return {
        "newton_e2_upper": e2_upper,
        "pair_count": pair_count,
        "normalized_pair_mean": normalized,
        "am_gm_exponent": Fraction(2, rank),
        "determinant_bound": determinant_bound,
        "integer_cap": integer_cap,
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


def factor_pairs(
    cap: int,
    *,
    det_q_minimum: int = 5,
    require_h_residue: bool = True,
    exclude_h_one: bool = True,
    require_smooth: bool = True,
    require_det_q_residue: bool = True,
    require_det_b_residue: bool = True,
) -> list[tuple[int, int, int]]:
    h_limit = cap // det_q_minimum
    h_values = smooth_3_7(h_limit) if require_smooth else list(range(1, h_limit + 1))
    if require_h_residue:
        h_values = [h for h in h_values if h % 4 == 1]
    if exclude_h_one:
        h_values = [h for h in h_values if h != 1]
    rows: list[tuple[int, int, int]] = []
    for h in h_values:
        for det_q in range(det_q_minimum, cap // h + 1):
            if require_det_q_residue and det_q % 4 != 1:
                continue
            det_b = h * det_q
            if require_det_b_residue and det_b % 4 != 1:
                continue
            rows.append((h, det_q, det_b))
    return rows


def odd_alternating_principal_checks() -> dict[str, object]:
    """Finite controls for the cofactor parity used to show S is even."""
    checked = 0
    for size in (1, 3):
        positions = list(itertools.combinations(range(size), 2))
        for bits in itertools.product((0, 1), repeat=len(positions)):
            matrix = [[0] * size for _ in range(size)]
            for (left, right), bit in zip(positions, bits):
                matrix[left][right] = bit
                matrix[right][left] = bit
            require(exact_determinant(matrix) % 2 == 0, "odd alternating determinant")
            checked += 1
    return {
        "finite_cases_checked": checked,
        "general_reason": "alternating forms have even rank",
    }


def audit() -> dict[str, object]:
    scaled_dual = scaled_dual_facts()
    require(scaled_dual["determinant_mod_4"] == 1, "h residue changed")
    require(scaled_dual["h_one_excluded"], "h=1 signature obstruction changed")

    trace_data = trace_square_floor()
    require(trace_data["trace_C"] == 2, "trace C changed")
    require(trace_data["trace_B2_mod_8"] == 4, "trace-square residue changed")
    require(trace_data["minimum_trace_B2"] == 60, "trace-square floor changed")

    maclaurin = pair_product_maclaurin(60)
    require(maclaurin["newton_e2_upper"] == 1122, "e2 bound changed")
    require(maclaurin["pair_count"] == 946, "pair count changed")
    require(
        maclaurin["normalized_pair_mean"] == Fraction(51, 43),
        "normalized pair mean changed",
    )
    left = 51**22
    right = 43**23
    require(left < right, "exact power comparison failed")
    require(maclaurin["determinant_bound"] < 43, "strict determinant bound failed")
    require(maclaurin["integer_cap"] == 42, "integer determinant cap changed")

    h_upper = 42 // 5
    require(smooth_3_7(h_upper) == [1, 3, 7], "smooth list changed")
    residue_survivors = [h for h in smooth_3_7(h_upper) if h % 4 == 1]
    require(residue_survivors == [1], "h residue survivors changed")
    require(factor_pairs(42) == [], "endpoint factor survived")

    weak = pair_product_maclaurin(54)
    require(weak["integer_cap"] == 45, "hostile weak cap changed")
    weak_pairs = factor_pairs(45)
    require((9, 5, 45) in weak_pairs, "hostile h=9 pair vanished")

    no_smooth = factor_pairs(42, require_smooth=False)
    require((5, 5, 25) in no_smooth, "hostile nonsmooth pair vanished")

    h_one_pairs = factor_pairs(42, exclude_h_one=False)
    require(any(h == 1 for h, _, _ in h_one_pairs), "hostile h=1 pairs vanished")

    # The candidate's claimed (9,3,27) hostile survivor does not survive if
    # the independent frozen consequence det(B)=1 mod 4 is retained.
    det_q_residue_omitted = factor_pairs(
        42,
        det_q_minimum=3,
        require_det_q_residue=False,
    )
    require(
        (9, 3, 27) not in det_q_residue_omitted,
        "detB modulo four failed to reject the candidate hostile pair",
    )
    # It does appear if det(B)=1 mod 4 is silently omitted as well.
    double_omission = factor_pairs(
        42,
        det_q_minimum=3,
        require_det_q_residue=False,
        require_det_b_residue=False,
    )
    require(
        (9, 3, 27) in double_omission,
        "double-omission control did not reproduce the candidate pair",
    )

    return {
        "claim_label": "VERIFIED",
        "scope": "conditional exclusion of n3=705 from frozen Wave20/Wave21 premises",
        "scaled_dual": scaled_dual,
        "cofactor_parity_controls": odd_alternating_principal_checks(),
        "trace_square": {
            key: (
                {"numerator": value.numerator, "denominator": value.denominator}
                if isinstance(value, Fraction)
                else value
            )
            for key, value in trace_data.items()
        },
        "pair_product_maclaurin": {
            "e2_upper": 1122,
            "pair_count": 946,
            "normalized": "51/43",
            "derivation": "AM-GM on all 946 pair products",
            "left_51_pow_22": left,
            "right_43_pow_23": right,
            "gap": right - left,
            "strict_det_B_upper": 43,
            "integer_det_B_cap": 42,
        },
        "determinant_index": {
            "det_B_factorization": "h*det(Q)",
            "det_Q_mod_4": 1,
            "det_Q_minimum": 5,
            "h_upper": h_upper,
            "smooth_h_at_most_8": smooth_3_7(h_upper),
            "h_mod_4_survivors": residue_survivors,
            "h_one_excluded": True,
            "final_pairs": [],
        },
        "hostile_controls": {
            "trace_square_54": {
                "det_B_cap": weak["integer_cap"],
                "survivor": [9, 5, 45],
            },
            "omit_smoothness": [5, 5, 25],
            "omit_h_one_obstruction_count": sum(
                h == 1 for h, _, _ in h_one_pairs
            ),
            "admit_det_Q_three_with_det_B_mod_4_retained": {
                "candidate_pair": [9, 3, 27],
                "status": "REJECTED_BY_det_B_mod_4",
            },
            "omit_det_Q_and_det_B_residues": {
                "survivor": [9, 3, 27],
            },
        },
        "conclusion": {
            "n3_705": "EXCLUDED_CONDITIONALLY",
            "conditional_n3_lower_bound": 708,
            "conditional_induced_C6_lower_bound": 209994,
            "target_status": "UNKNOWN",
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
