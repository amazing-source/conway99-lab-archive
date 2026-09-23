"""Exact replay for the Wave201 proof-B hostile audit.

This checker evaluates multiset identities and symbolic coefficients.
It performs no graph, set-family, configuration, or isomorphism search.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def fiber_charge(
    full_multiplicities: tuple[int, ...],
    selected_multiplicities: dict[int, int],
    *,
    subtract_degree_five_baseline: bool,
) -> dict[str, int | bool]:
    """Check the value-by-value weighted charge in one fiber."""
    assert full_multiplicities
    assert len(full_multiplicities) <= 4
    assert all(value >= 1 for value in full_multiplicities)
    degree = sum(full_multiplicities)
    assert degree <= 5

    for index, selected in selected_multiplicities.items():
        assert 0 <= index < len(full_multiplicities)
        assert 1 <= selected <= full_multiplicities[index]

    distinct = len(full_multiplicities)
    rho = degree - distinct
    k = len(selected_multiplicities)
    selected_m_minus_one = sum(
        value - 1 for value in selected_multiplicities.values()
    )
    selected_charge = sum(
        value - 2 for value in selected_multiplicities.values()
    )
    unused_repetition = rho - selected_m_minus_one

    # Exact expansion:
    # unused_repetition =
    #   sum_selected(r_y-m_y) + sum_unselected(r_z-1).
    selected_gap = sum(
        full_multiplicities[index] - selected
        for index, selected in selected_multiplicities.items()
    )
    unselected_gap = sum(
        full - 1
        for index, full in enumerate(full_multiplicities)
        if index not in selected_multiplicities
    )
    assert unused_repetition == selected_gap + unselected_gap
    assert unused_repetition >= 0

    if subtract_degree_five_baseline:
        assert degree == 5
        assert rho >= 1
        available = rho - 1
        if k:
            residual = unused_repetition + (k - 1)
        else:
            residual = available
    else:
        available = rho
        residual = unused_repetition + k

    assert residual == available - selected_charge
    assert residual >= 0
    return {
        "degree": degree,
        "distinct": distinct,
        "rho": rho,
        "selected_values": k,
        "selected_charge": selected_charge,
        "available_after_baseline": available,
        "residual": residual,
        "valid": True,
    }


def add(
    left: dict[str, int], right: dict[str, int], scale: int = 1
) -> dict[str, int]:
    names = set(left) | set(right)
    return {
        name: left.get(name, 0) + scale * right.get(name, 0)
        for name in names
        if left.get(name, 0) + scale * right.get(name, 0)
    }


def derive() -> dict[str, object]:
    examples = {
        "degree5_empty": fiber_charge(
            (2, 1, 1, 1), {}, subtract_degree_five_baseline=True
        ),
        "degree5_single_saturated": fiber_charge(
            (5,), {0: 5}, subtract_degree_five_baseline=True
        ),
        "degree5_multiple_values": fiber_charge(
            (3, 2), {0: 3, 1: 2}, subtract_degree_five_baseline=True
        ),
        "degree4_multiple_values": fiber_charge(
            (2, 2), {0: 2, 1: 2}, subtract_degree_five_baseline=False
        ),
    }

    global_row = {
        "SF": 9,
        "g": 9,
        "SH": 3,
        "delta": 1,
        "epsilon": 1,
        "eta": -3,
    }
    budget = {
        "SI": 32,
        "S2": 48,
        "SE2": 8,
        "RA": 28,
        "SL": 12,
        "S5": 1,
        "SH": 3,
        "SF": 13,
        "a1": 4,
        "b3": 24,
        "c2": 8,
        "g": 9,
        "W": 16,
    }
    s5 = {"delta": 5, "eta": 5, "epsilon": 1}
    expanded_budget = add(budget, {"S5": 1}, scale=-1)
    expanded_budget = add(expanded_budget, s5)
    difference = add(expanded_budget, global_row, scale=-1)
    expected_difference = {
        "SI": 32,
        "S2": 48,
        "SE2": 8,
        "RA": 28,
        "SL": 12,
        "SF": 4,
        "delta": 4,
        "eta": 8,
        "a1": 4,
        "b3": 24,
        "c2": 8,
        "W": 16,
    }
    assert difference == expected_difference
    assert all(coefficient >= 0 for coefficient in difference.values())

    target = Fraction(281457, 40)
    improved = target + Fraction(891, 40)
    assert improved == Fraction(70587, 10)
    integer_bound = (
        improved.numerator + improved.denominator - 1
    ) // improved.denominator
    assert integer_bound == 7059

    return {
        "claim_label": (
            "AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION"
        ),
        "fiber_lemma": {
            "identity": (
                "rho-sum_selected(m_y-1)="
                "sum_selected(r_y-m_y)+sum_unselected(r_z-1)>=0"
            ),
            "nonbaseline_residual": "unused_repetition+k>=0",
            "degree5_nonempty_residual": (
                "unused_repetition+(k-1)>=0"
            ),
            "degree5_empty_residual": "rho-1>=0",
            "examples": examples,
        },
        "local_to_global": {
            "tight_center_degree_five_baselines": 3,
            "deficient_center": (
                "delta_x>=sum_selected_at_x(m_y-2)"
            ),
            "tight_center": (
                "delta_x>=sum_selected_at_x(m_y-2)"
            ),
            "global": "delta>=3*q-epsilon",
        },
        "global_elimination": {
            "q_identity": (
                "4*q=297-3*SF-3*g-SH+epsilon+delta+eta"
            ),
            "derived_row": (
                "9*SF+9*g+3*SH+delta+epsilon-3*eta>=891"
            ),
            "floor": 891,
        },
        "budget_domination": {
            "difference_coefficients": difference,
            "all_nonnegative": True,
            "budget_floor": 891,
        },
        "consequence": {
            "wave198_target": str(target),
            "improved_rational_target": str(improved),
            "conditional_Q_lower_bound": integer_bound,
            "edge_added_projective": integer_bound + 693,
            "scalar_words": 2 * (integer_bound + 693),
        },
        "search_scope": (
            "exact multiset identities and symbolic coefficient algebra "
            "only; no graph, code, cover, SAT, LP, configuration, "
            "enumeration, isomorphism, or brute-force search"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print("PASS: Wave201 proof-B weighted-fiber audit matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
