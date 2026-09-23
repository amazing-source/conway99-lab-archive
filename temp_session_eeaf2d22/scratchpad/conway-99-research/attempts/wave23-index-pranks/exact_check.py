#!/usr/bin/env python3
"""Exact arithmetic checks for the Wave 23 projector-index endpoint attack.

No floating-point number decides a mathematical branch.  In particular, the
38 radical stationary products are bounded above with rational square-root
brackets obtained by integer ``isqrt``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable


RANK = 44
ENDPOINT_TRACE = 48
ENDPOINT_SQUARE_TRACE = 60
SQRT_SCALE = 10**12


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def decimal_floor_text(value: Fraction, places: int = 12) -> str:
    """Return a deterministic decimal truncation, using integer arithmetic."""

    require(value >= 0, "decimal formatter expects a nonnegative fraction")
    scale = 10**places
    scaled = value.numerator * scale // value.denominator
    whole, tail = divmod(scaled, scale)
    return f"{whole}.{tail:0{places}d}"


def sqrt_floor_scaled(value: Fraction, scale: int = SQRT_SCALE) -> int:
    """Return floor(scale*sqrt(value)), certified with integer inequalities."""

    require(value >= 0, "square-root radicand must be nonnegative")
    floor_value = math.isqrt(value.numerator * scale * scale // value.denominator)
    require(
        floor_value * floor_value * value.denominator
        <= value.numerator * scale * scale,
        "lower square-root bracket failed",
    )
    require(
        (floor_value + 1) * (floor_value + 1) * value.denominator
        > value.numerator * scale * scale,
        "upper square-root bracket failed",
    )
    return floor_value


@dataclass(frozen=True)
class StationaryCase:
    high_multiplicity: int
    high_radicand: Fraction
    low_radicand: Fraction
    high_sqrt_floor: int
    low_sqrt_floor: int
    high_upper: Fraction
    low_upper: Fraction
    product_upper: Fraction

    def as_json(self) -> dict[str, object]:
        margin = Fraction(13) - self.product_upper
        require(margin > 0, "stationary product was not certified below 13")
        encoded = (
            f"{self.high_multiplicity}|{self.high_sqrt_floor}|"
            f"{self.low_sqrt_floor}|{self.product_upper.numerator}|"
            f"{self.product_upper.denominator}"
        ).encode("ascii")
        return {
            "high_multiplicity": self.high_multiplicity,
            "high_sqrt_floor_at_scale_1e12": self.high_sqrt_floor,
            "low_sqrt_floor_at_scale_1e12": self.low_sqrt_floor,
            "high_radicand": fraction_text(self.high_radicand),
            "low_radicand": fraction_text(self.low_radicand),
            "high_upper_decimal": decimal_floor_text(self.high_upper),
            "low_upper_decimal": decimal_floor_text(self.low_upper),
            "product_upper_decimal": decimal_floor_text(self.product_upper),
            "product_upper_lt_13": True,
            "positive_margin_numerator_digits": len(str(margin.numerator)),
            "positive_margin_denominator_digits": len(str(margin.denominator)),
            "certificate_sha256": hashlib.sha256(encoded).hexdigest(),
        }


def stationary_cases(
    square_trace: int = ENDPOINT_SQUARE_TRACE,
    *,
    rank: int = RANK,
    trace: int = ENDPOINT_TRACE,
    scale: int = SQRT_SCALE,
) -> list[StationaryCase]:
    """Enumerate all positive two-value stationary spectra.

    The constraints are

        sum x_i = trace,  sum x_i^2 = square_trace.

    ``k`` entries take the larger value and ``rank-k`` the smaller value.
    """

    require(rank > 1 and trace > 0, "invalid moment dimensions")
    variance = Fraction(square_trace, rank) - Fraction(trace, rank) ** 2
    require(variance > 0, "the two moments must have positive variance")
    mean = Fraction(trace, rank)
    cases: list[StationaryCase] = []
    for k in range(1, rank):
        high_rad = variance * Fraction(rank - k, k)
        low_rad = variance * Fraction(k, rank - k)
        high_floor = sqrt_floor_scaled(high_rad, scale)
        low_floor = sqrt_floor_scaled(low_rad, scale)

        # a = mean + sqrt(high_rad); use an upper radical bracket.
        high_upper = mean + Fraction(high_floor + 1, scale)
        # b = mean - sqrt(low_rad); use a lower radical bracket.
        low_upper = mean - Fraction(low_floor, scale)

        # If even the upper bracket is nonpositive, the exact lower value is
        # nonpositive and this multiplicity cannot occur in an interior
        # positive stationary point.
        if low_upper <= 0:
            continue
        exact_low_positive = mean * mean > low_rad
        if not exact_low_positive:
            continue

        product_upper = high_upper**k * low_upper ** (rank - k)
        cases.append(
            StationaryCase(
                high_multiplicity=k,
                high_radicand=high_rad,
                low_radicand=low_rad,
                high_sqrt_floor=high_floor,
                low_sqrt_floor=low_floor,
                high_upper=high_upper,
                low_upper=low_upper,
                product_upper=product_upper,
            )
        )
    return cases


def certify_product_cap(square_trace: int = ENDPOINT_SQUARE_TRACE) -> dict[str, object]:
    cases = stationary_cases(square_trace)
    require(cases, "no positive stationary cases were found")
    all_below = all(case.product_upper < 13 for case in cases)
    maximum = max(cases, key=lambda case: case.product_upper)
    return {
        "rank": RANK,
        "trace": ENDPOINT_TRACE,
        "square_trace": square_trace,
        "positive_stationary_case_count": len(cases),
        "positive_high_multiplicities": [
            case.high_multiplicity for case in cases
        ],
        "all_exact_rational_upper_bounds_lt_13": all_below,
        "largest_certified_upper_case": maximum.high_multiplicity,
        "largest_certified_upper_decimal": decimal_floor_text(
            maximum.product_upper
        ),
        "cases": [case.as_json() for case in cases] if all_below else [],
    }


def trace_square_lower_bound(rank: int = RANK, trace_b: int = 48) -> dict[str, int]:
    """Derive tr(B^2)>=60 from B=I+2C and tr(B)=48."""

    require((trace_b - rank) % 2 == 0, "B-I must have even trace")
    trace_c = (trace_b - rank) // 2
    # For every integral matrix, tr(C^2)=tr(C) modulo two.  Self-adjointness
    # for a positive form makes C diagonalizable over R with real eigenvalues,
    # so trace(C^2)>0 when trace(C)!=0.
    minimum_trace_c_square = 1
    if trace_c % 2 == 0:
        minimum_trace_c_square = 2
    minimum_trace_b_square = (
        rank + 4 * trace_c + 4 * minimum_trace_c_square
    )
    return {
        "rank": rank,
        "trace_B": trace_b,
        "trace_C": trace_c,
        "trace_C2_mod_2": trace_c % 2,
        "minimum_positive_trace_C2": minimum_trace_c_square,
        "minimum_trace_B2": minimum_trace_b_square,
    }


def trace_square_parity(matrix: list[list[int]]) -> tuple[int, int]:
    n = len(matrix)
    require(n > 0 and all(len(row) == n for row in matrix), "matrix not square")
    trace = sum(matrix[i][i] for i in range(n))
    trace_square = sum(
        matrix[i][j] * matrix[j][i] for i in range(n) for j in range(n)
    )
    return trace % 2, trace_square % 2


def endpoint_index_survivors(det_cap: int) -> list[dict[str, int]]:
    """Enumerate h, det(Q), det(B) using only audited endpoint arithmetic."""

    rows: list[dict[str, int]] = []
    hs: set[int] = set()
    for a in range(5):
        for b in range(5):
            h = 3**a * 7**b
            if h <= det_cap:
                hs.add(h)
    for h in sorted(hs):
        for det_q in range(5, det_cap + 1, 4):
            det_b = h * det_q
            if det_b <= det_cap and det_b % 4 == 1:
                rows.append({"h": h, "det_Q": det_q, "det_B": det_b})
    return rows


def smith_rank_data(
    count_1: int, count_3: int, count_7: int, count_21: int
) -> dict[str, int]:
    counts = (count_1, count_3, count_7, count_21)
    require(all(value >= 0 for value in counts), "negative Smith count")
    require(sum(counts) == RANK, "Smith counts must sum to 44")
    h = 3 ** (count_3 + count_21) * 7 ** (count_7 + count_21)
    rank_3 = count_1 + count_7
    rank_7 = count_1 + count_3
    require(3 ** (RANK - rank_3) * 7 ** (RANK - rank_7) == h, "rank formula failed")
    return {
        "h": h,
        "rank_F3_M": rank_3,
        "rank_F7_M": rank_7,
        "v3_h": RANK - rank_3,
        "v7_h": RANK - rank_7,
    }


@dataclass(frozen=True)
class BoseMesnerElement:
    """Element aI+bA+cJ in the target adjacency algebra."""

    i: Fraction
    a: Fraction
    j: Fraction

    def __add__(self, other: "BoseMesnerElement") -> "BoseMesnerElement":
        return BoseMesnerElement(
            self.i + other.i, self.a + other.a, self.j + other.j
        )

    def __mul__(self, other: "BoseMesnerElement") -> "BoseMesnerElement":
        # A^2=12I-A+2J, AJ=JA=14J, J^2=99J.
        i = self.i * other.i + 12 * self.a * other.a
        a = (
            self.i * other.a
            + self.a * other.i
            - self.a * other.a
        )
        j = (
            self.i * other.j
            + self.j * other.i
            + 2 * self.a * other.a
            + 14 * self.a * other.j
            + 14 * self.j * other.a
            + 99 * self.j * other.j
        )
        return BoseMesnerElement(i, a, j)

    def scale(self, scalar: Fraction | int) -> "BoseMesnerElement":
        scalar = Fraction(scalar)
        return BoseMesnerElement(
            scalar * self.i, scalar * self.a, scalar * self.j
        )


def adjacency_algebra_checks() -> dict[str, object]:
    identity = BoseMesnerElement(Fraction(1), Fraction(0), Fraction(0))
    adjacency = BoseMesnerElement(Fraction(0), Fraction(1), Fraction(0))
    all_ones = BoseMesnerElement(Fraction(0), Fraction(0), Fraction(1))
    seidel = identity + adjacency.scale(2) + all_ones.scale(-1)
    seidel_square = seidel * seidel
    require(
        seidel_square == identity.scale(49) + all_ones.scale(49),
        "Seidel square identity failed",
    )

    r_operator = (
        identity.scale(3) + adjacency.scale(-1) + all_ones.scale(Fraction(1, 9))
    )
    require(r_operator * r_operator == r_operator.scale(7), "R^2=7R failed")

    # Over F_7, 5R=S coefficientwise (9 is invertible).
    coeff_5r_mod7 = tuple(
        int(value.numerator * pow(value.denominator, -1, 7) * 5) % 7
        for value in (r_operator.i, r_operator.a, r_operator.j)
    )
    coeff_s_mod7 = tuple(
        int(value.numerator * pow(value.denominator, -1, 7)) % 7
        for value in (seidel.i, seidel.a, seidel.j)
    )
    require(coeff_5r_mod7 == coeff_s_mod7, "5R=S mod 7 failed")
    return {
        "S_coefficients_I_A_J": [
            fraction_text(seidel.i),
            fraction_text(seidel.a),
            fraction_text(seidel.j),
        ],
        "S2_coefficients_I_A_J": [
            fraction_text(seidel_square.i),
            fraction_text(seidel_square.a),
            fraction_text(seidel_square.j),
        ],
        "R_coefficients_I_A_J": [
            fraction_text(r_operator.i),
            fraction_text(r_operator.a),
            fraction_text(r_operator.j),
        ],
        "R2_equals_7R": True,
        "five_R_equals_S_mod_7": True,
    }


def h_one_obstruction(rank: int = RANK, scale: int = 21) -> dict[str, object]:
    require(scale % 2 == 1, "the parity transfer requires odd scale")
    signature_mod_8 = rank % 8
    impossible = signature_mod_8 != 0
    return {
        "premise": "L=21L*",
        "coordinate_consequence": "21G^{-1} is unimodular integral",
        "inverse_consequence": "G/21 is unimodular integral",
        "parity_consequence": "G/21 is even because G is even and 21 is odd",
        "rank": rank,
        "signature_mod_8": signature_mod_8,
        "even_unimodular_positive_definite_possible": not impossible,
        "h_equals_1_excluded": impossible,
    }


def build_results() -> dict[str, object]:
    trace_bound = trace_square_lower_bound()
    require(trace_bound["minimum_trace_B2"] == 60, "wrong square-trace floor")
    cap = certify_product_cap()
    require(
        cap["positive_stationary_case_count"] == 38,
        "wrong number of positive stationary cases",
    )
    require(
        cap["positive_high_multiplicities"] == list(range(1, 39)),
        "wrong stationary multiplicity interval",
    )
    require(
        cap["all_exact_rational_upper_bounds_lt_13"],
        "determinant cap was not certified",
    )
    require(
        cap["largest_certified_upper_case"] == 1,
        "wrong largest certified stationary case",
    )

    old_endpoint = endpoint_index_survivors(45)
    require(sorted({row["h"] for row in old_endpoint}) == [1, 9], "old h-list changed")
    new_endpoint = endpoint_index_survivors(12)
    require(sorted({row["h"] for row in new_endpoint}) == [1], "new h-list changed")
    h_one = h_one_obstruction()
    require(h_one["h_equals_1_excluded"], "h=1 obstruction failed")

    return {
        "status": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "scope": "conditional exclusion of the n3=705 endpoint",
        "smith_index_relations": {
            "nonzero_smith_factors": [1, 3, 7, 21],
            "h_formula": "3^(44-rank_F3(M))*7^(44-rank_F7(M))",
            "h_equals_Delta_44_M": True,
            "endpoint_rank_pairs_before_new_exclusion": {
                "h=1": [44, 44],
                "h=9": [42, 44],
            },
        },
        "modular_reductions": {
            "F7": {
                "rank_N": 99,
                "reason": "rank(A mod 7)=98 with kernel <1>, but N^T1=3*1 !=0",
                "rank_M_equals_rank_Seidel_mod_7": True,
                "seidel_identity": adjacency_algebra_checks(),
                "limitation": "S^2=0 mod 7 alone does not fix rank(S mod 7)",
            },
            "F3": {
                "exact_identity": "NM=3(3I-A)N+J, hence NM=J mod 3",
                "limitation": "this does not determine rank(M mod 3)",
            },
        },
        "near_identity_moment": trace_bound,
        "two_moment_product_certificate": cap,
        "determinant_consequences": {
            "det_B_positive_integer_mod_4": 1,
            "strict_upper_bound": 13,
            "integer_candidates_after_det_Q_ge_5": [5, 9],
            "audited_cap_45_endpoint_rows": old_endpoint,
            "new_cap_12_endpoint_rows": new_endpoint,
        },
        "h_equals_one_obstruction": h_one,
        "endpoint_conclusion": {
            "n3_equals_705": "REFUTED_PENDING_INDEPENDENT_VERIFICATION",
            "conditional_lower_bound_n3": 708,
            "conditional_induced_C6_lower_bound": 209994,
            "target_existence": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    results = build_results()
    if args.output is not None:
        write_json(args.output, results)
    else:
        print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
