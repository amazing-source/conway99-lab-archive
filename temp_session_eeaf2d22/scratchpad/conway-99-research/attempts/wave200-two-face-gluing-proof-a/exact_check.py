"""Exact arithmetic checks for Wave200 two-face gluing."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def derive() -> dict[str, object]:
    C = 4158
    V = 99
    target = Fraction(76 * C - 349 * V, 40)
    assert target == Fraction(281457, 40)

    budgets = {
        q0: 40 * (Fraction(q0) - target) for q0 in (7037, 7038)
    }
    assert budgets == {7037: Fraction(23), 7038: Fraction(63)}
    budget_max = int(max(budgets.values()))
    assert budget_max == 63

    # From 4s >= 297-(3SF+3g+SH+3S5), while
    # 3SF+3g+SH+3S5 <= 3B.
    forced_four_s = 297 - 3 * budget_max
    forced_s = (forced_four_s + 3) // 4
    assert forced_four_s == 108
    assert forced_s == 27

    delta_max = budget_max // 5
    local_s_max = delta_max // 3
    assert delta_max == 12
    assert local_s_max == 4
    assert forced_s > local_s_max

    improved_q = 7039
    next_budget = 40 * (Fraction(improved_q) - target)
    assert next_budget == 103

    return {
        "faces": {
            "target": str(target),
            "budgets": {str(q0): int(value) for q0, value in budgets.items()},
            "budget_max": budget_max,
            "relevant_subrow": "S5+3*SH+13*SF+9*g<=B",
        },
        "forced_saturation": {
            "q_identity": (
                "4*q=297-3*SF-3*g-SH+epsilon+delta+eta"
            ),
            "s_bound": (
                "4*s>=297-(3*SF+3*g+SH+3*S5)>=297-3*B"
            ),
            "four_s_lower": forced_four_s,
            "s_lower": forced_s,
        },
        "local_loss": {
            "tight_center": "delta_x>=3*s_x",
            "deficient_center": "delta_x>=4*s_x",
            "global": "3*s<=delta<=S5/5<=B/5",
            "delta_max": delta_max,
            "s_upper": local_s_max,
        },
        "contradiction": "27<=s<=4",
        "claim": {
            "conditional_Q_lower_bound": improved_q,
            "edge_added_projective": improved_q + 693,
            "scalar_words": 2 * (improved_q + 693),
        },
        "stopping_point": {
            "Q0": improved_q,
            "budget": int(next_budget),
            "coarse_argument_excludes": False,
        },
        "search_scope": (
            "exact slack arithmetic and additive local fiber loss only; "
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
        print("PASS: Wave200 two-face result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
