"""Exact arithmetic checks for Wave199 near-face gluing."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def ceil_fraction(value: Fraction) -> int:
    return (value.numerator + value.denominator - 1) // value.denominator


def derive() -> dict[str, object]:
    C = 4158
    V = 99
    target = Fraction(76 * C - 349 * V, 40)
    assert target == Fraction(281457, 40)

    assumed_q0 = 7037
    budget = 40 * (Fraction(assumed_q0) - target)
    assert budget == 23

    weights = {
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
    maxima = {
        name: int(budget) // weight for name, weight in weights.items()
    }
    assert maxima["SF"] == 1
    assert maxima["g"] == 2
    assert maxima["SH"] == 7
    assert maxima["S5"] == 23

    delta_max = maxima["S5"] // 5
    epsilon_max = maxima["S5"]
    assert delta_max == 4
    assert epsilon_max == 23

    # From 4q=297-3SF-3g-SH+epsilon+delta+eta.
    q_numerator_lower = (
        297
        - 3 * maxima["SF"]
        - 3 * maxima["g"]
        - maxima["SH"]
    )
    q_lower = ceil_fraction(Fraction(q_numerator_lower, 4))
    saturated_lower = q_lower - epsilon_max
    assert q_numerator_lower == 281
    assert q_lower == 71
    assert saturated_lower == 48

    # With SF<=1, at most one center has c_x<=12.
    # If that center is saturated it consumes all delta and contributes <=7.
    # Otherwise one tight c_x=13 center consumes at least 3 delta and
    # contributes at most 3 saturated orientations.
    deficient_saturated_upper = 7
    tight_center_deficit_min = 3
    tight_upper = 3 * (delta_max // tight_center_deficit_min)
    saturated_upper = max(deficient_saturated_upper, tight_upper)
    assert tight_upper == 3
    assert saturated_upper == 7
    assert saturated_lower > saturated_upper

    improved_q = assumed_q0 + 1
    return {
        "claim": {
            "excluded_face": "Q0=7037",
            "conditional_Q_lower_bound": improved_q,
            "edge_added_projective": improved_q + 693,
            "scalar_words": 2 * (improved_q + 693),
        },
        "budget": {
            "target": str(target),
            "multiplier": 40,
            "value": int(budget),
            "weights": weights,
            "maxima_used": {
                "SF": maxima["SF"],
                "g": maxima["g"],
                "SH": maxima["SH"],
                "S5": maxima["S5"],
            },
        },
        "orientation_deficits": {
            "decomposition": "S5=5*delta+5*eta+epsilon",
            "delta_max": delta_max,
            "epsilon_max": epsilon_max,
            "q_identity": (
                "4*q=297-3*SF-3*g-SH+epsilon+delta+eta"
            ),
            "q_lower": q_lower,
            "saturated_lower": saturated_lower,
        },
        "local_cap": {
            "tight_center_pair_cap": 3,
            "tight_center_deficit_min": tight_center_deficit_min,
            "deficient_center_pair_cap": 7,
            "deficient_center_count_max": 1,
            "total_delta_max": delta_max,
            "saturated_upper": saturated_upper,
        },
        "contradiction": "48<=s<=7",
        "search_scope": (
            "exact slack arithmetic and local extremal set geometry only; "
            "no graph, code, cover, SAT, LP, configuration, enumeration, "
            "isomorphism, or brute-force search"
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
        print("PASS: Wave199 near-face result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
