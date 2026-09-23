"""Post-freeze checks for additional Wave202 source claims.

This file does not alter the independently frozen result.  It verifies
the source's center-size and multiplicity-one consequences analytically.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def center_certificate_cost(full_flag_count: int) -> dict[str, int]:
    if not 0 <= full_flag_count <= 13:
        raise ValueError("Wave196 gives 0<=c_x<=13")
    sf_contribution = 13 - full_flag_count
    delta_contribution = max(0, 36 - 3 * full_flag_count)
    return {
        "c_x": full_flag_count,
        "SF_contribution": sf_contribution,
        "delta_contribution": delta_contribution,
        "combined_cost": sf_contribution + delta_contribution,
    }


def m1_margin(
    full_multiplicities: tuple[int, ...],
    selected_multiplicities: dict[int, int],
    *,
    degree_five_baseline: bool,
) -> dict[str, int]:
    if not full_multiplicities or len(full_multiplicities) > 4:
        raise ValueError("one occupied four-point fibre is required")
    if any(value < 1 for value in full_multiplicities):
        raise ValueError("full multiplicities must be positive")
    degree = sum(full_multiplicities)
    if degree > 5:
        raise ValueError("simple pair degree exceeded")
    if degree_five_baseline and degree != 5:
        raise ValueError("baseline requires degree five")
    for index, value in selected_multiplicities.items():
        if not 0 <= index < len(full_multiplicities):
            raise ValueError("selected label absent")
        if not 1 <= value <= full_multiplicities[index]:
            raise ValueError("selected multiplicity exceeds full")

    rho = degree - len(full_multiplicities)
    selected_repeat = sum(
        value - 1 for value in selected_multiplicities.values()
    )
    e = rho - selected_repeat
    if e < 0:
        raise AssertionError("selected repeats cannot exceed full repeats")
    k = len(selected_multiplicities)
    r = sum(value == 1 for value in selected_multiplicities.values())
    h = k - r
    local_term = e + k - int(degree_five_baseline)

    if not degree_five_baseline:
        proof_margin = e + h
    elif h >= 1:
        proof_margin = e + h - 1
    else:
        # With no high-multiplicity selected value, selected repeats are
        # zero.  Degree five in a four-point fibre gives rho=e>=1.
        assert e == rho >= 1
        proof_margin = e - 1
    assert local_term - r == proof_margin >= 0
    return {
        "degree": degree,
        "e": e,
        "selected_values": k,
        "m1_values": r,
        "higher_values": h,
        "baseline": int(degree_five_baseline),
        "local_term": local_term,
        "margin_over_m1": proof_margin,
    }


def derive() -> dict[str, object]:
    center_costs = {
        str(c_x): center_certificate_cost(c_x)
        for c_x in (10, 11, 12, 13)
    }
    assert center_costs["11"]["combined_cost"] == 5
    assert center_costs["12"]["combined_cost"] == 1
    assert center_costs["13"]["combined_cost"] == 0

    profiles = {
        "baseline_m1": m1_margin(
            (1, 2, 1, 1),
            {0: 1},
            degree_five_baseline=True,
        ),
        "baseline_m1_and_m2": m1_margin(
            (1, 2, 1, 1),
            {0: 1, 1: 2},
            degree_five_baseline=True,
        ),
        "baseline_two_m1": m1_margin(
            (1, 1, 2, 1),
            {0: 1, 1: 1},
            degree_five_baseline=True,
        ),
        "nonbaseline_m1": m1_margin(
            (1, 1, 1),
            {0: 1},
            degree_five_baseline=False,
        ),
    }

    return {
        "format": "wave202-post-freeze-source-comparison-v1",
        "center_sizes": {
            "certificate_budget": 3,
            "costs": center_costs,
            "conclusion": "c_x is 12 or 13 at every center",
        },
        "multiplicity_one": {
            "fibre_identity": (
                "local_term-r=e+h off baseline; on a degree-five "
                "baseline it is e+h-1 when h>=1 and e-1 otherwise"
            ),
            "profiles": profiles,
            "global_conclusion": "r<=SM<=3",
        },
        "two_center": {
            "m1_orientation_forces_opposite_occupied": True,
            "opposite_multiplicity_forced_to_one": False,
            "parity_obstruction": False,
            "cross_center_fibre_multiset_coupling_available": False,
        },
        "verdict": "SOURCE_CLAIMS_CORROBORATED_NO_EXCLUSION",
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
        print("PASS: Wave202 source-comparison result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
