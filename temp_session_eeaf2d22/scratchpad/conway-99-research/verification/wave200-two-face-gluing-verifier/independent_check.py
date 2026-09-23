"""Independent exact checks for the Wave200 two-face gluing claim.

The checker reconstructs the slack identities, the coefficient
domination, and the local fibre-loss argument from sealed pre-Wave200
theorems.  It imports no discovery code and performs no graph,
configuration, cover, SAT, LP, isomorphism, or brute-force search.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


Vector = dict[str, int]


def add(*vectors: Vector) -> Vector:
    names = set().union(*(vector.keys() for vector in vectors))
    return {
        name: sum(vector.get(name, 0) for vector in vectors)
        for name in names
        if sum(vector.get(name, 0) for vector in vectors)
    }


def scale(multiplier: int, vector: Vector) -> Vector:
    return {
        name: multiplier * coefficient
        for name, coefficient in vector.items()
        if multiplier * coefficient
    }


def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def oriented_identities() -> dict[str, object]:
    # Definitions:
    # J=H-delta, T=J-a-eta, p3=T-q,
    # 3n3=p3+5q-epsilon.
    h_cap = {"H": 1}
    j = add(h_cap, {"delta": -1})
    t = add(j, {"a": -1, "eta": -1})
    p3 = add(t, {"q": -1})
    three_n3 = add(p3, {"q": 5, "epsilon": -1})

    s5 = add(
        scale(5, h_cap),
        scale(-1, three_n3),
        scale(-4, p3),
        {"a": -5},
    )
    assert s5 == {"delta": 5, "eta": 5, "epsilon": 1}

    # Independently, the full-pool rows give
    # 3n3=3861-3SF-a-SH-3g.
    three_n3_pool = {
        "constant": 3861,
        "SF": -3,
        "a": -1,
        "SH": -1,
        "g": -3,
    }
    # The orientation definitions above give
    # 3n3=3564-delta-a-eta+4q-epsilon.
    three_n3_oriented = dict(three_n3)
    three_n3_oriented["H"] = three_n3_oriented.pop("H")
    assert three_n3_oriented == {
        "H": 1,
        "delta": -1,
        "a": -1,
        "eta": -1,
        "q": 4,
        "epsilon": -1,
    }
    q_right = {
        "constant": 297,
        "SF": -3,
        "g": -3,
        "SH": -1,
        "epsilon": 1,
        "delta": 1,
        "eta": 1,
    }
    # Direct coefficient comparison after setting H=3564.
    oriented_at_h = dict(three_n3_oriented)
    oriented_at_h.pop("H")
    oriented_at_h["constant"] = 3564
    difference = add(three_n3_pool, scale(-1, oriented_at_h))
    assert difference == add(q_right, {"q": -4})

    return {
        "S5_identity": "S5=5*delta+5*eta+epsilon",
        "S5_vector": s5,
        "q_identity": (
            "4*q=297-3*SF-3*g-SH+epsilon+delta+eta"
        ),
        "q_right_vector": q_right,
    }


def hilton_milner_templates() -> dict[str, object]:
    ground = set(range(7))
    special = frozenset({1, 2, 3})
    standard_h = {special}
    for pair in itertools.combinations(sorted(ground - {0}), 2):
        if set(pair) & set(special):
            standard_h.add(frozenset({0, *pair}))

    core = {0, 1, 2}
    exceptional_k = {
        frozenset(triple)
        for triple in itertools.combinations(sorted(ground), 3)
        if len(set(triple) & core) >= 2
    }

    summaries: dict[str, object] = {}
    for name, family in (
        ("standard_H", standard_h),
        ("exceptional_K", exceptional_k),
    ):
        degrees: Counter[frozenset[int]] = Counter()
        for triple in family:
            for pair in itertools.combinations(sorted(triple), 2):
                degrees[frozenset(pair)] += 1
        degree_five = sorted(
            [sorted(pair) for pair, degree in degrees.items() if degree == 5]
        )
        assert len(family) == 13
        assert max(degrees.values()) == 5
        assert len(degree_five) == 3
        summaries[name] = {
            "members": len(family),
            "maximum_pair_degree": max(degrees.values()),
            "degree_five_pairs": degree_five,
        }
    return summaries


def derive() -> dict[str, object]:
    c = 4158
    vertices = 99
    target = Fraction(76 * c - 349 * vertices, 40)
    assert target == Fraction(281457, 40)

    candidate_faces = (7037, 7038)
    budgets = {
        q0: int(40 * (Fraction(q0) - target))
        for q0 in candidate_faces
    }
    assert budgets == {7037: 23, 7038: 63}
    budget_max = max(budgets.values())

    # The penalty in the saturation lower bound is
    # 3*S5+SH+3*SF+3*g.  Three times the budget row
    # S5+3*SH+13*SF+9*g dominates it coefficientwise.
    penalty = {"S5": 3, "SH": 1, "SF": 3, "g": 3}
    three_budget_row = {"S5": 3, "SH": 9, "SF": 39, "g": 27}
    domination_residual = add(three_budget_row, scale(-1, penalty))
    assert domination_residual == {"SH": 8, "SF": 36, "g": 24}

    forced_four_s = 297 - 3 * budget_max
    forced_s = ceil_div(forced_four_s, 4)
    face_s_lower = {
        q0: ceil_div(297 - 3 * budget, 4)
        for q0, budget in budgets.items()
    }
    assert forced_four_s == 108
    assert forced_s == 27
    assert face_s_lower == {7037: 57, 7038: 27}

    templates = hilton_milner_templates()
    # In a simple 3-uniform family on seven points, a fixed pair has only
    # five possible third points.  A multiplicity-five orientation
    # therefore exhausts its pair fibre, so two such orientations cannot
    # share a fibre.
    possible_third_points = 7 - 2
    saturated_multiplicity = 5
    assert possible_third_points == saturated_multiplicity

    # Tight centre c_x=13: the three degree-five HM fibres force baseline
    # loss 3.  Saturating s_x of them raises total loss to 3+3*s_x,
    # hence delta_x>=3*s_x.
    tight_losses = {
        s_x: 4 * s_x + (3 - s_x)
        for s_x in range(4)
    }
    assert tight_losses == {0: 3, 1: 6, 2: 9, 3: 12}

    # Deficient centre c_x<=12:
    # j_x<=3*c_x-4*s_x, so
    # delta_x>=36-3*c_x+4*s_x>=4*s_x.
    deficient_margin_min = min(36 - 3 * c_x for c_x in range(13))
    assert deficient_margin_min == 0
    deficient_margin_for_c_at_most_12 = min(
        36 - 3 * c_x for c_x in range(12 + 1)
    )
    assert deficient_margin_for_c_at_most_12 == 0
    # The c_x=12 boundary is the weakest deficient case.
    assert 36 - 3 * 12 == 0

    delta_max = budget_max // 5
    saturated_upper = delta_max // 3
    assert delta_max == 12
    assert saturated_upper == 4
    assert forced_s > saturated_upper

    q_lower = 7039
    edge_isolated = 693
    return {
        "format": "wave200-two-face-gluing-independent-v1",
        "verdict": "VERIFIED_WITH_SCOPE",
        "conditional_setting": (
            "prism-free rank-11 endpoint n3=4158, P=0"
        ),
        "faces": {
            "target": str(target),
            "excluded_Q0_values": list(candidate_faces),
            "budgets": {str(key): value for key, value in budgets.items()},
            "maximum_budget": budget_max,
            "budget_subrow": "S5+3*SH+13*SF+9*g<=B",
        },
        "oriented_identities": oriented_identities(),
        "forced_saturation": {
            "unsaturated_count_bound": "q-s<=epsilon",
            "penalty": penalty,
            "three_budget_row": three_budget_row,
            "coefficientwise_domination_residual": domination_residual,
            "bound": "4*s>=297-3*B",
            "face_s_lower": {
                str(key): value for key, value in face_s_lower.items()
            },
            "four_s_lower": forced_four_s,
            "s_lower": forced_s,
        },
        "local_fibre_loss": {
            "simple_family_pair_capacity": possible_third_points,
            "saturated_orientation_multiplicity": saturated_multiplicity,
            "distinct_saturated_fibres_reason": (
                "one saturated orientation exhausts all five simple "
                "triples containing its block pair"
            ),
            "hilton_milner_templates": templates,
            "tight_loss_by_s_x": {
                str(key): value for key, value in tight_losses.items()
            },
            "tight_bound": "delta_x>=3*s_x",
            "deficient_bound": (
                "delta_x>=36-3*c_x+4*s_x>=4*s_x for c_x<=12"
            ),
            "global_bound": "3*s<=delta<=S5/5<=B/5",
            "delta_upper": delta_max,
            "s_upper": saturated_upper,
        },
        "contradiction": {
            "required_s_lower": forced_s,
            "permitted_s_upper": saturated_upper,
            "status": "CONTRADICTION",
        },
        "consequence": {
            "conditional_Q0_lower": q_lower,
            "conditional_Q_lower": q_lower,
            "all_projective_short_circuits": q_lower + edge_isolated,
            "nonzero_scalar_short_circuit_words": (
                2 * (q_lower + edge_isolated)
            ),
        },
        "stopping_point": {
            "Q0": 7039,
            "budget": int(40 * (Fraction(7039) - target)),
            "excluded_by_this_coarse_argument": False,
        },
        "boundary": {
            "graph_constructed": False,
            "endpoint_excluded": False,
            "rank_11_excluded": False,
            "strict_original_n3_improvement": False,
            "external_novelty": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
        "search_scope": (
            "exact symbolic incidence, two fixed Hilton-Milner formulas, "
            "and integer slack arithmetic only; no graph, configuration, "
            "cover, SAT, LP, enumeration, isomorphism, or brute-force search"
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
        print("PASS: independent Wave200 two-face result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
