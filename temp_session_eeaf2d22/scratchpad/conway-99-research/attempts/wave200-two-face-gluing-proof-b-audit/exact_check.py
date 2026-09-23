"""Exact arithmetic replay for the Wave200 proof-B hostile audit.

The checker expands integer slack and per-fiber loss formulas only. It
does not search graphs, set families, configurations, or isomorphism
classes.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def tight_center_loss(saturated: int) -> dict[str, int]:
    """Lower-bound loss for a fixed c=13 HM equality template."""
    assert 0 <= saturated <= 3
    saturated_loss = 4 * saturated
    unsaturated_degree_five_loss = 3 - saturated
    occurrence_loss = saturated_loss + unsaturated_degree_five_loss
    delta_lower = 36 - 3 * 13 + occurrence_loss
    assert occurrence_loss == 3 + 3 * saturated
    assert delta_lower == 3 * saturated
    return {
        "saturated": saturated,
        "occurrence_loss_lower": occurrence_loss,
        "delta_lower": delta_lower,
    }


def deficient_center_loss(c: int, saturated: int) -> dict[str, int]:
    """Lower-bound loss below c=13, using disjoint saturated fibers."""
    assert 0 <= c <= 12
    assert 0 <= saturated <= (3 * c) // 5
    occurrence_loss = 4 * saturated
    baseline = 36 - 3 * c
    delta_lower = baseline + occurrence_loss
    assert baseline >= 0
    assert delta_lower >= 4 * saturated
    return {
        "c": c,
        "saturated": saturated,
        "baseline": baseline,
        "occurrence_loss_lower": occurrence_loss,
        "delta_lower": delta_lower,
    }


def derive() -> dict[str, object]:
    c_total = 4158
    vertices = 99
    target = Fraction(76 * c_total - 349 * vertices, 40)
    assert target == Fraction(281457, 40)

    face_rows: dict[str, dict[str, int]] = {}
    for q0 in (7037, 7038):
        budget = int(40 * (Fraction(q0) - target))
        four_s_lower = 297 - 3 * budget
        s_lower = (four_s_lower + 3) // 4
        delta_upper = budget // 5
        s_upper = delta_upper // 3
        face_rows[str(q0)] = {
            "budget": budget,
            "four_s_lower": four_s_lower,
            "s_lower": s_lower,
            "delta_upper": delta_upper,
            "s_upper": s_upper,
        }
        assert s_lower > s_upper

    assert face_rows == {
        "7037": {
            "budget": 23,
            "four_s_lower": 228,
            "s_lower": 57,
            "delta_upper": 4,
            "s_upper": 1,
        },
        "7038": {
            "budget": 63,
            "four_s_lower": 108,
            "s_lower": 27,
            "delta_upper": 12,
            "s_upper": 4,
        },
    }

    tight_rows = [tight_center_loss(s) for s in range(4)]
    deficient_examples = [
        deficient_center_loss(12, s) for s in range(8)
    ]

    next_budget = int(40 * (Fraction(7039) - target))
    assert next_budget == 103
    assert 297 - 3 * next_budget < 0

    return {
        "claim_label": (
            "AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION"
        ),
        "faces": {
            "target": str(target),
            "rows": face_rows,
            "uniform_budget_upper": 63,
            "uniform_s_lower": 27,
            "uniform_delta_upper": 12,
            "uniform_s_upper": 4,
        },
        "fiber_partition": {
            "pair_types": 21,
            "vertices_per_fiber": 4,
            "nonneighbors_partitioned": 84,
            "unique_type_per_leaf": True,
            "one_leaf_per_contained_pair_per_flag": True,
            "identity": "3*c_x-j_x=sum_P(d_P-u_P)",
            "saturated_type": {
                "d_P": 5,
                "u_P": 1,
                "loss": 4,
                "distinct_saturated_labels_have_distinct_types": True,
            },
        },
        "local_loss": {
            "tight_rows": tight_rows,
            "tight_formula": "delta_x>=3*s_x",
            "deficient_c12_rows": deficient_examples,
            "deficient_formula": "delta_x>=4*s_x",
            "global_formula": "3*s<=delta<=S5/5<=B/5",
        },
        "contradictions": {
            "7037": "57<=s<=1",
            "7038": "27<=s<=4",
        },
        "consequence": {
            "conditional_Q_lower_bound": 7039,
            "edge_added_projective": 7039 + 693,
            "scalar_words": 2 * (7039 + 693),
        },
        "stopping_point": {
            "Q0": 7039,
            "budget": next_budget,
            "coarse_four_s_lower": 297 - 3 * next_budget,
            "excluded_by_this_mechanism": False,
        },
        "search_scope": (
            "exact slack and per-fiber incidence arithmetic only; no "
            "graph, code, cover, SAT, LP, configuration, enumeration, "
            "isomorphism, or brute-force search"
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
        print("PASS: Wave200 proof-B two-face audit matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
