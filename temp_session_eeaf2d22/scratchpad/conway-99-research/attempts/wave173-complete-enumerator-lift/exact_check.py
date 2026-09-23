"""Exact Wave 173 complete-enumerator lift obstruction.

The script uses only Python's standard library and never searches for a graph
or code.  It also reconstructs the relevant multivariate Krawtchouk
coefficients directly in Z[omega]/(omega^2+omega+1).
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Iterable

N = 231
CODE_SIZE = 3**11
PAIR_COUNTS = {
    18: 1,
    144: 26_658,
    153: 9_899,
    159: 49_248,
    162: 2_536,
    198: 231,
}
GENERAL_CONTROL = {
    (0, 3): Fraction(9_303_802_338, 154_676_717),
    (36, 162): Fraction(231),
    (54, 162): Fraction(3_304_353_488, 11_898_209),
    (63, 93): Fraction(61_600_137_243, 11_898_209),
    (72, 78): Fraction(585_275_248_956, 11_898_209),
    (78, 81): Fraction(5_202_810_114_945, 154_676_717),
}

Eisenstein = tuple[int, int]
ONE: Eisenstein = (1, 0)
OMEGA: Eisenstein = (0, 1)
OMEGA2: Eisenstein = (-1, -1)


def eadd(left: Eisenstein, right: Eisenstein) -> Eisenstein:
    return left[0] + right[0], left[1] + right[1]


def emul(left: Eisenstein, right: Eisenstein) -> Eisenstein:
    p, q = left
    r, s = right
    return p * r - q * s, p * s + q * r - q * s


def epow(value: Eisenstein, exponent: int) -> Eisenstein:
    result = ONE
    for _ in range(exponent):
        result = emul(result, value)
    return result


def group_term(
    count: int,
    ones: int,
    twos: int,
    one_phase: Eisenstein,
    two_phase: Eisenstein,
) -> Eisenstein:
    coefficient = comb(count, ones) * comb(count - ones, twos)
    phase = emul(epow(one_phase, ones), epow(two_phase, twos))
    return coefficient * phase[0], coefficient * phase[1]


def complete_krawtchouk(
    symbol_ones: int,
    symbol_twos: int,
    dual_ones: int,
    dual_twos: int,
) -> Eisenstein:
    """Coefficient for one word in the complete MacWilliams transform."""

    groups = (
        (N - symbol_ones - symbol_twos, ONE, ONE),
        (symbol_ones, OMEGA, OMEGA2),
        (symbol_twos, OMEGA2, OMEGA),
    )
    result: Eisenstein = (0, 0)
    for r0 in range(dual_ones + 1):
        for r1 in range(dual_ones - r0 + 1):
            r = (r0, r1, dual_ones - r0 - r1)
            for s0 in range(dual_twos + 1):
                for s1 in range(dual_twos - s0 + 1):
                    s = (s0, s1, dual_twos - s0 - s1)
                    if any(
                        r[index] + s[index] > groups[index][0]
                        for index in range(3)
                    ):
                        continue
                    term = ONE
                    for index, (count, one_phase, two_phase) in enumerate(
                        groups
                    ):
                        term = emul(
                            term,
                            group_term(
                                count,
                                r[index],
                                s[index],
                                one_phase,
                                two_phase,
                            ),
                        )
                    result = eadd(result, term)
    return result


def x_value(weight: int) -> Fraction:
    return Fraction(2 * N - 3 * weight, 2)


def paired_k20(weight: int, difference: int) -> Fraction:
    x = x_value(weight)
    return x * x - x - Fraction(3, 4) * difference * difference


def paired_k30(weight: int, difference: int) -> Fraction:
    x = x_value(weight)
    return (
        x**3 / 3
        - x**2
        + Fraction(2 * N, 3)
        - Fraction(3, 4) * (x + 1) * difference * difference
    )


def paired_k10(weight: int) -> Fraction:
    return 2 * x_value(weight)


def paired_k11(weight: int, difference: int) -> Fraction:
    x = x_value(weight)
    return 2 * x**2 + Fraction(3, 2) * difference**2 - 2 * N


def paired_k21(weight: int, difference: int) -> Fraction:
    x = x_value(weight)
    return (
        x**3
        - x**2
        - 2 * (N - 1) * x
        + Fraction(3, 4) * (x + 1) * difference**2
    )


def allowed_compositions(weight: int) -> Iterable[tuple[int, int]]:
    for symbol_ones in range(0, weight + 1, 3):
        symbol_twos = weight - symbol_ones
        if symbol_twos % 3 == 0:
            yield symbol_ones, symbol_twos


def formula_cross_check() -> bool:
    for weight in PAIR_COUNTS:
        for symbol_ones, symbol_twos in allowed_compositions(weight):
            difference = symbol_ones - symbol_twos
            for dual, formula in (
                ((2, 0), paired_k20(weight, difference)),
                ((3, 0), paired_k30(weight, difference)),
            ):
                direct = eadd(
                    complete_krawtchouk(
                        symbol_ones, symbol_twos, dual[0], dual[1]
                    ),
                    complete_krawtchouk(
                        symbol_twos, symbol_ones, dual[0], dual[1]
                    ),
                )
                if direct[1] != 0 or Fraction(direct[0]) != formula:
                    return False
    return True


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def general_control_check() -> dict[str, object]:
    def total(function: object) -> Fraction:
        return sum(
            multiplicity
            * function(
                symbol_ones + symbol_twos,
                symbol_ones - symbol_twos,
            )
            for (symbol_ones, symbol_twos), multiplicity in GENERAL_CONTROL.items()
        )

    pair_total = sum(GENERAL_CONTROL.values())
    b10_numerator = Fraction(N) + total(
        lambda weight, difference: paired_k10(weight)
    )
    b20_numerator = Fraction(comb(N, 2)) + total(paired_k20)
    b11_numerator = Fraction(N * (N - 1)) + total(paired_k11)
    b21_numerator = Fraction(3 * comb(N, 3)) + total(paired_k21)
    b30_numerator = Fraction(comb(N, 3)) + total(paired_k30)
    b30 = b30_numerator / CODE_SIZE

    checks = {
        "nonnegative_cells": all(value >= 0 for value in GENERAL_CONTROL.values()),
        "pair_total": pair_total == Fraction(CODE_SIZE - 1, 2),
        "B10_zero": b10_numerator == 0,
        "B20_zero": b20_numerator == 0,
        "B11_zero": b11_numerator == 0,
        "B21_zero": b21_numerator == 0,
        "distinguished_pairs": GENERAL_CONTROL[(36, 162)] == 231,
        "B30_positive": b30 == Fraction(2_948_614_938_535, 963_754_929),
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    return {
        "cells": {
            f"{left},{right}": fraction_text(value)
            for (left, right), value in GENERAL_CONTROL.items()
        },
        "B30": fraction_text(b30),
        "checks": checks,
        "scope": "rational degree-three complete-moment control only",
    }


def derive() -> dict[str, object]:
    base20 = sum(
        count * (x_value(weight) ** 2 - x_value(weight))
        for weight, count in PAIR_COUNTS.items()
    )
    q_total = Fraction(4, 3) * (comb(N, 2) + base20)

    base30 = sum(
        count
        * (
            x_value(weight) ** 3 / 3
            - x_value(weight) ** 2
            + Fraction(2 * N, 3)
        )
        for weight, count in PAIR_COUNTS.items()
    )
    b30 = 60
    t_total = Fraction(-4, 3) * (
        b30 * CODE_SIZE - comb(N, 3) - base30
    )

    fixed_difference = 162 - 36
    q_fixed = PAIR_COUNTS[198] * fixed_difference**2
    t_fixed = (x_value(198) + 1) * q_fixed
    q_remaining = q_total - q_fixed
    t_remaining = t_total - t_fixed

    weight18_cap = 18**2
    next_coefficient = max(
        x_value(weight) + 1
        for weight in PAIR_COUNTS
        if weight not in (18, 198)
    )
    upper_bound = (
        (x_value(18) + 1) * weight18_cap
        + next_coefficient * (q_remaining - weight18_cap)
    )
    gap = t_remaining - upper_bound

    coefficients = {
        str(weight): fraction_text(x_value(weight) + 1)
        for weight in PAIR_COUNTS
    }
    checks = {
        "pair_count": sum(PAIR_COUNTS.values())
        == (CODE_SIZE - 1) // 2,
        "complete_formula_cross_check": formula_cross_check(),
        "wave172_forces_B30": b30 == 120 // 2,
        "Q_total": q_total == 13_640_319,
        "T_total": t_total == Fraction(-7_617_321, 2),
        "Q_fixed": q_fixed == 3_667_356,
        "T_fixed": t_fixed == -238_378_140,
        "Q_remaining": q_remaining == 9_972_963,
        "T_remaining": t_remaining == Fraction(469_138_959, 2),
        "upper_bound": upper_bound == 159_628_644,
        "strict_contradiction": gap == Fraction(149_881_671, 2) and gap > 0,
    }
    if not all(checks.values()):
        raise AssertionError(checks)

    return {
        "format": "wave173-complete-enumerator-lift-v1",
        "claim_label": "DERIVED",
        "scope": (
            "nonexistence of a complete-enumerator lift of the Wave54 "
            "ordinary formal distribution under the distinguished endpoint "
            "weight-198 compositions and Wave172 mixed-weight-3 zero "
            "constraints"
        ),
        "pair_counts": {str(key): value for key, value in PAIR_COUNTS.items()},
        "x_plus_one_by_weight": coefficients,
        "moments": {
            "Q_total": fraction_text(q_total),
            "T_total": fraction_text(t_total),
            "Q_fixed_weight198": fraction_text(Fraction(q_fixed)),
            "T_fixed_weight198": fraction_text(t_fixed),
            "Q_remaining": fraction_text(q_remaining),
            "T_remaining": fraction_text(t_remaining),
            "T_remaining_upper_bound": fraction_text(upper_bound),
            "contradiction_gap": fraction_text(gap),
        },
        "checks": checks,
        "general_rational_control": general_control_check(),
        "disposition": {
            "wave54_complete_lift": "REFUTED",
            "general_degree3_rational_relaxation": "FEASIBLE",
            "all_ordinary_enumerators": "NOT_CLASSIFIED",
            "endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("stored result differs from exact reconstruction")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
