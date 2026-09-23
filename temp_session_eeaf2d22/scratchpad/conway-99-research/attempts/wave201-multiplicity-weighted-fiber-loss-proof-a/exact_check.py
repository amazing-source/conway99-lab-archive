"""Exact symbolic checks for Wave201 multiplicity-weighted fiber loss."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def add_coefficients(
    left: dict[str, int], right: dict[str, int], scale: int = 1
) -> dict[str, int]:
    names = set(left) | set(right)
    return {
        name: left.get(name, 0) + scale * right.get(name, 0)
        for name in names
        if left.get(name, 0) + scale * right.get(name, 0)
    }


def derive() -> dict[str, object]:
    # Generic same-fiber algebra. For k selected leaf values in a
    # degree-five fiber, subtracting one baseline leaves k-1 spare units.
    same_fiber = {
        "full_repeat": "rho=sum_z(r_z-1)",
        "selected_charge": "sum_y(m_y-1)",
        "degree5_after_baseline": (
            "rho-1-sum_y(m_y-2)>=k-1>=0 for k>=1"
        ),
        "degree5_empty_case": "rho-1>=0",
    }

    # Eliminate q from delta>=3q-epsilon and the Wave198 q identity.
    # The resulting left side is L>=891.
    global_left = {
        "SF": 9,
        "g": 9,
        "SH": 3,
        "delta": 1,
        "epsilon": 1,
        "eta": -3,
    }
    global_floor = 891

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
    expanded_budget = add_coefficients(budget, {"S5": 1}, scale=-1)
    expanded_budget = add_coefficients(expanded_budget, s5)
    difference = add_coefficients(expanded_budget, global_left, scale=-1)
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
    assert all(value >= 0 for value in difference.values())

    C = 4158
    V = 99
    wave198_target = Fraction(76 * C - 349 * V, 40)
    improved_target = wave198_target + Fraction(global_floor, 40)
    assert wave198_target == Fraction(281457, 40)
    assert improved_target == Fraction(282348, 40)
    assert improved_target == Fraction(352935, 50)
    integer_q = (
        improved_target.numerator + improved_target.denominator - 1
    ) // improved_target.denominator
    assert integer_q == 7059

    return {
        "local_lemma": {
            "same_fiber": same_fiber,
            "deficient_center": (
                "delta_x=36-3*c_x+sum_P rho_P>=sum_y(m_y-2)"
            ),
            "tight_center_baselines": 3,
            "tight_center": (
                "delta_x=sum_d5(rho_P-1)+sum_other rho_P"
                ">=sum_y(m_y-2)"
            ),
            "global": "delta>=sum_nonprivate(m_y-2)=3*q-epsilon",
        },
        "global_elimination": {
            "q_identity": (
                "4*q=297-3*SF-3*g-SH+epsilon+delta+eta"
            ),
            "derived_row": (
                "9*SF+9*g+3*SH+delta+epsilon-3*eta>=891"
            ),
            "floor": global_floor,
        },
        "budget_domination": {
            "B": "40*Q0-(76*C-349*V)",
            "difference_coefficients": difference,
            "all_difference_coefficients_nonnegative": True,
            "floor": global_floor,
        },
        "claim": {
            "wave198_target": str(wave198_target),
            "improved_rational_target": str(improved_target),
            "conditional_Q_lower_bound": integer_q,
            "edge_added_projective": integer_q + 693,
            "scalar_words": 2 * (integer_q + 693),
        },
        "search_scope": (
            "exact multiset repetition and symbolic coefficient algebra "
            "only; no graph, code, cover, SAT, LP, configuration, "
            "enumeration, isomorphism, or brute-force search"
        ),
        "claim_label": "DERIVED_PENDING_HOSTILE_AUDIT",
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
        print("PASS: Wave201 weighted-fiber result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
