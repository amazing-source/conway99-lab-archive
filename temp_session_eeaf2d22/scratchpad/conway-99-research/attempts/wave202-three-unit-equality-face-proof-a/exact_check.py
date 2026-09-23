"""Exact checks for the Wave202 three-unit equality face."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def derive() -> dict[str, object]:
    C = 4158
    V = 99
    Q0 = 7059
    base = 19 * C - 85 * V
    rhs = 10 * Q0 - base
    assert base == 70587
    assert rhs == 3

    weights = {
        "SI": 8,
        "S2": 12,
        "SE2": 2,
        "RA": 7,
        "SL": 3,
        "L": 1,
        "delta": 1,
        "eta": 2,
        "SF": 1,
        "a1": 1,
        "b3": 6,
        "c2": 2,
        "W": 4,
    }
    forced_zero = sorted(name for name, weight in weights.items() if weight > 3)
    assert forced_zero == ["RA", "S2", "SI", "W", "b3"]

    # Replay the coefficient reduction from the 40-scaled Wave198 budget.
    expanded_budget = {
        "SI": 32,
        "S2": 48,
        "SE2": 8,
        "RA": 28,
        "SL": 12,
        "SH": 3,
        "SF": 13,
        "g": 9,
        "delta": 5,
        "eta": 5,
        "epsilon": 1,
        "a1": 4,
        "b3": 24,
        "c2": 8,
        "W": 16,
    }
    weighted_left = {
        "SF": 9,
        "g": 9,
        "SH": 3,
        "delta": 1,
        "epsilon": 1,
        "eta": -3,
    }
    difference = {
        name: expanded_budget.get(name, 0) - weighted_left.get(name, 0)
        for name in set(expanded_budget) | set(weighted_left)
    }
    difference = {name: value for name, value in difference.items() if value}
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
    divided_difference = {
        name: value // 4 for name, value in difference.items()
    }
    assert all(4 * divided_difference[name] == value for name, value in difference.items())

    partition_classes = {
        "A": {
            "SL": 1,
            "E": 0,
            "U": 0,
            "description": "all three units in SL",
        },
        "B": {
            "SL": 0,
            "E": 0,
            "U": 3,
            "description": "unit-weight slacks sum to three",
        },
        "C": {
            "SL": 0,
            "E": 1,
            "U": 1,
            "description": "one even slack and one unit-weight slack",
        },
    }
    for values in partition_classes.values():
        assert 3 * values["SL"] + 2 * values["E"] + values["U"] == 3

    return {
        "certificate": {
            "identity": (
                "10*Q0-(19*C-85*V)=8*SI+12*S2+2*SE2+7*RA+3*SL"
                "+L+delta+2*eta+SF+a1+6*b3+2*c2+4*W"
            ),
            "L": "delta-3*q+epsilon",
            "base": base,
            "Q0": Q0,
            "rhs": rhs,
            "forced_zero": forced_zero,
            "coefficient_replay_after_weighted_row": divided_difference,
        },
        "partitions": {
            "E": "SE2+eta+c2",
            "U": "L+delta+SF+a1",
            "classes": partition_classes,
        },
        "local_slack": {
            "e_P": "rho_P-sum_selected(m_y-1)",
            "deficient": "L_x=3*(12-c_x)+q_x+sum_P e_P",
            "tight": "L_x=q_x-3+sum_P e_P",
            "deficient_zero": "c_x=12,q_x=0,e_P=0 for all P",
            "tight_zero": (
                "e_P=k_P=0 off d_P=5; e_P+k_P=1 on each of three d_P=5"
            ),
            "center_sizes": [12, 13],
            "m1_bound": "r<=L<=3",
        },
        "two_center": {
            "m1_forces_opposite_occupied": True,
            "opposite_may_have_m_at_least_2": True,
            "parity_obstruction": False,
            "baseline_obstruction_found": False,
            "global_realization": "UNKNOWN",
        },
        "claim": {
            "conditional_Q_lower_bound": 7059,
            "Q0_7059_excluded": False,
        },
        "search_scope": (
            "exact certificate and tiny symbolic slack partition only; "
            "no graph, code, cover, SAT, LP, configuration, isomorphism, "
            "or brute-force search"
        ),
        "claim_label": "DERIVED_FACE_CHARACTERIZATION_NO_EXCLUSION",
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
        print("PASS: Wave202 equality-face result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
