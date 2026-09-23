"""Independent exact replay for the Wave199 near-face contradiction.

This checker uses only integer slack arithmetic and the two classified
Hilton--Milner templates through their proved degree-five consequences.
It performs no graph, code, cover, SAT, LP, configuration, enumeration,
isomorphism, or brute-force search.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


BUDGET_WEIGHTS = {
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


def symbolic_add(*vectors: dict[str, int]) -> dict[str, int]:
    names = set().union(*(vector.keys() for vector in vectors))
    return {
        name: sum(vector.get(name, 0) for vector in vectors)
        for name in names
        if sum(vector.get(name, 0) for vector in vectors)
    }


def symbolic_scale(k: int, vector: dict[str, int]) -> dict[str, int]:
    return {name: k * value for name, value in vector.items() if k * value}


def identity_checks() -> dict[str, object]:
    # Definitions:
    # H=J+delta, J=T+a+eta, T=p3+q,
    # 3n3=p3+5q-epsilon.
    h = {"J": 1, "delta": 1}
    j = {"T": 1, "a": 1, "eta": 1}
    t = {"p3": 1, "q": 1}
    three_n3 = {"p3": 1, "q": 5, "epsilon": -1}

    s5 = symbolic_add(
        symbolic_scale(5, h),
        symbolic_scale(-1, three_n3),
        {"p3": -4, "a": -5},
    )
    for source, replacement in (("J", j), ("T", t)):
        coefficient = s5.pop(source, 0)
        s5 = symbolic_add(s5, symbolic_scale(coefficient, replacement))
    assert s5 == {"delta": 5, "eta": 5, "epsilon": 1}

    # From 5q=3n3-p3+epsilon and
    # H=p3+q+a+eta+delta:
    # 4q=3n3-H+a+epsilon+eta+delta.
    four_q_right = {
        "three_n3": 1,
        "H": -1,
        "a": 1,
        "epsilon": 1,
        "eta": 1,
        "delta": 1,
    }
    # n3+h=13V-SF-g, a=3h-SH, and 3*13V-H=3861-3564=297.
    reduced_q_right = {
        "constant": 297,
        "SF": -3,
        "g": -3,
        "SH": -1,
        "epsilon": 1,
        "delta": 1,
        "eta": 1,
    }
    return {
        "S5_identity": "S5=5*delta+5*eta+epsilon",
        "S5_reduced_vector": s5,
        "q_intermediate": (
            "4*q=3*n3-H+a+epsilon+delta+eta"
        ),
        "q_intermediate_vector": four_q_right,
        "q_identity": (
            "4*q=297-3*SF-3*g-SH+epsilon+delta+eta"
        ),
        "q_reduced_vector": reduced_q_right,
    }


def derive() -> dict[str, object]:
    c = 4158
    vertices = 99
    h_cap = 36 * vertices
    target_numerator = 76 * c - 349 * vertices
    target_denominator = 40
    target_floor = target_numerator // target_denominator
    assert (target_numerator, target_denominator) == (281457, 40)
    assert target_floor == 7036

    candidate_q = 7037
    scaled_budget = (
        target_denominator * candidate_q - target_numerator
    )
    assert scaled_budget == 23

    sf_max = scaled_budget // BUDGET_WEIGHTS["SF"]
    g_max = scaled_budget // BUDGET_WEIGHTS["g"]
    sh_max = scaled_budget // BUDGET_WEIGHTS["SH"]
    s5_max = scaled_budget // BUDGET_WEIGHTS["S5"]
    assert (sf_max, g_max, sh_max, s5_max) == (1, 2, 7, 23)

    delta_eta_max = s5_max // 5
    epsilon_max = s5_max
    q_numerator_min = (
        297 - 3 * sf_max - 3 * g_max - sh_max
    )
    q_min = (q_numerator_min + 3) // 4
    saturated_min = q_min - epsilon_max
    assert delta_eta_max == 4
    assert q_numerator_min == 281
    assert q_min == 71
    assert saturated_min == 48

    # Full-pool deficit SF<=1: all centers have c=13, except possibly
    # one center with c=12.
    c13_degree_five_pairs = 3
    c13_saturation_deficit = 3
    c13_saturated_centers = delta_eta_max // c13_saturation_deficit
    c13_saturated_orientations = (
        c13_saturated_centers * c13_degree_five_pairs
    )

    c12_pair_incidences = 3 * 12
    c12_saturated_cap = c12_pair_incidences // 5
    c12_saturation_deficit = 4
    assert c13_saturated_orientations == 3
    assert c12_saturated_cap == 7

    # If the exceptional c=12 center saturates, it consumes all delta<=4
    # and no c=13 center can saturate.  Otherwise use the c=13 bound.
    saturated_max = max(c13_saturated_orientations, c12_saturated_cap)
    assert saturated_max == 7
    assert saturated_min > saturated_max

    return {
        "claim_label": "AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "wave198_face": {
            "target": "281457/40",
            "excluded_integer_value": candidate_q,
            "scaled_budget": scaled_budget,
            "budget_identity": (
                "32SI+48S2+8SE2+28RA+12SL+S5+3SH+13SF+"
                "4a1+24b3+8c2+9g+16W=23"
            ),
            "budget_weights": BUDGET_WEIGHTS,
            "immediate_caps": {
                "SF": sf_max,
                "g": g_max,
                "SH": sh_max,
                "S5": s5_max,
            },
        },
        "global_multiplicity": {
            **identity_checks(),
            "delta_plus_eta_max": delta_eta_max,
            "epsilon_max": epsilon_max,
            "q_numerator_min": q_numerator_min,
            "q_min": q_min,
            "multiplicity_five_orientations_min": saturated_min,
        },
        "local_gluing": {
            "full_flag_deficit_max": sf_max,
            "c13_centers": "all 99, except possibly one c=12 center",
            "c13_degree_five_pair_cap": c13_degree_five_pairs,
            "c13_deficit_per_saturated_center": c13_saturation_deficit,
            "c13_global_saturated_cap": c13_saturated_orientations,
            "c12_pair_incidence_total": c12_pair_incidences,
            "c12_deficit_if_saturated": c12_saturation_deficit,
            "c12_saturated_orientation_cap": c12_saturated_cap,
            "global_saturated_orientation_cap": saturated_max,
            "proof_a_looser_cap": 12,
        },
        "contradiction": {
            "required_saturated_orientations": saturated_min,
            "maximum_saturated_orientations": saturated_max,
            "status": "CONTRADICTION",
        },
        "consequence": {
            "conditional_Q_lower_bound": 7038,
            "edge_added_projective": 7038 + 693,
            "circuit_scalar_words": 2 * (7038 + 693),
        },
        "search_scope": (
            "exact integer slack and incidence arithmetic only; no graph, "
            "code, cover, SAT, LP, configuration, enumeration, isomorphism, "
            "or brute-force search"
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
        print("PASS: Wave199 proof-B near-face audit matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
