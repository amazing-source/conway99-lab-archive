"""Source-blind Wave202 equality-face verifier.

This checker characterizes the exact three-unit Wave201 certificate
face, derives the raw-variable formulas by symbolic affine algebra, and
tests the local weighted-slack equality structure.  It performs no
graph, configuration, family, cover, SAT, LP, enumeration, isomorphism,
or brute-force search.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


Linear = dict[str, Fraction]


def constant(value: int | Fraction) -> Linear:
    return {"_": Fraction(value)} if value else {}


def variable(name: str) -> Linear:
    return {name: Fraction(1)}


def add(*expressions: Linear) -> Linear:
    names = set().union(*(expression.keys() for expression in expressions))
    return {
        name: sum(
            (expression.get(name, Fraction()) for expression in expressions),
            Fraction(),
        )
        for name in names
        if sum(
            (expression.get(name, Fraction()) for expression in expressions),
            Fraction(),
        )
    }


def scale(multiplier: int | Fraction, expression: Linear) -> Linear:
    return {
        name: Fraction(multiplier) * coefficient
        for name, coefficient in expression.items()
        if Fraction(multiplier) * coefficient
    }


def evaluate(expression: Linear, values: dict[str, int]) -> Fraction:
    return sum(
        coefficient * (1 if name == "_" else values[name])
        for name, coefficient in expression.items()
    )


def symbolic_face() -> dict[str, object]:
    # Low-weight certificate slacks.  The budget equation eliminates
    # delta, leaving no case or object enumeration.
    e = variable("SE2")
    ell = variable("SL")
    eta = variable("eta")
    sm = variable("SM")
    sf = variable("SF")
    a1 = variable("a1")
    c2 = variable("c2")
    a3 = variable("a3")
    n3 = variable("n3")
    g = variable("g")

    delta = add(
        constant(3),
        scale(-2, e),
        scale(-3, ell),
        scale(-2, eta),
        scale(-1, sm),
        scale(-1, sf),
        scale(-1, a1),
        scale(-2, c2),
    )
    budget = add(
        scale(2, e),
        scale(3, ell),
        delta,
        scale(2, eta),
        sm,
        sf,
        a1,
        scale(2, c2),
    )
    assert budget == constant(3)

    # Formulas obtained from the raw identities after
    # SI=S2=RA=b3=W=0 and the three-unit budget.
    a2 = add(constant(60), scale(-1, e), scale(-1, c2), scale(-2, sf))
    r2 = add(constant(30), scale(-1, sf))
    n2 = add(constant(357), scale(-1, a1), scale(-1, ell), sf)
    y = add(
        a3,
        scale(3, n3),
        constant(-3801),
        scale(-1, e),
        sf,
    )
    h = add(constant(1287), scale(-1, n3), scale(-1, sf), scale(-1, g))
    q = add(
        scale(3, n3),
        a3,
        eta,
        sm,
        constant(-3564),
    )
    p3 = add(
        constant(7128),
        scale(-1, delta),
        scale(-2, a3),
        scale(-2, eta),
        scale(-1, sm),
        scale(-3, n3),
    )
    c1 = add(p3, scale(-1, c2))
    n1 = add(a1, a2, a3)
    p2 = n2
    b1 = scale(2, n2)
    r1 = add(a1, b1, c1)
    j_union = add(constant(3564), scale(-1, delta))
    t_union = add(j_union, scale(-1, a3), scale(-1, eta))
    epsilon = add(sm, scale(-1, delta), scale(3, q))

    # Reconstruct every defining row symbolically.
    incidence = add(
        scale(2, n1),
        scale(2, n2),
        scale(3, n3),
        p2,
        p3,
    )
    si = add(incidence, constant(-8316))
    s2 = add(p2, scale(-1, n2))
    se2 = add(scale(2, r2), scale(-1, a2), scale(-1, c2))
    ra = add(
        scale(3, h),
        y,
        scale(3, g),
        scale(-1, a2),
        scale(-1, a3),
        scale(-1, c2),
    )
    sl = add(
        n1,
        scale(2, n2),
        c1,
        scale(2, r2),
        y,
        constant(-4158),
    )
    reconstructed_sf = add(
        constant(1287),
        scale(-1, n3),
        scale(-1, h),
        scale(-1, g),
    )
    reconstructed_eta = add(
        j_union,
        scale(-1, t_union),
        scale(-1, a3),
    )
    t_minus_p3_q = add(t_union, scale(-1, p3), scale(-1, q))
    selected_incidence = add(scale(3, n3), scale(-1, p3))
    capacity_incidence = add(scale(5, q), scale(-1, epsilon))
    reconstructed_sm = add(delta, scale(-3, q), epsilon)
    q0 = add(
        n1,
        n2,
        scale(2, n3),
        r1,
        r2,
        scale(2, h),
        y,
        scale(2, g),
    )

    assert si == {}
    assert s2 == {}
    assert se2 == e
    assert ra == {}
    assert sl == ell
    assert reconstructed_sf == sf
    assert reconstructed_eta == eta
    assert t_minus_p3_q == {}
    assert selected_incidence == capacity_incidence
    assert reconstructed_sm == sm
    assert q0 == constant(7059)

    return {
        "certificate_face": (
            "3=8*SI+12*S2+2*SE2+7*RA+3*SL+delta+2*eta+"
            "SM+SF+a1+6*b3+2*c2+4*W"
        ),
        "forced_zero": ["SI", "S2", "RA", "b3", "W"],
        "reduced_budget": (
            "2*SE2+3*SL+delta+2*eta+SM+SF+a1+2*c2=3"
        ),
        "analytic_partition": {
            "SL_one": (
                "SL=1 and SE2=delta=eta=SM=SF=a1=c2=0"
            ),
            "SL_zero_even_zero": (
                "SL=0, SE2+eta+c2=0, delta+SM+SF+a1=3"
            ),
            "SL_zero_even_one": (
                "SL=0, SE2+eta+c2=1, delta+SM+SF+a1=1"
            ),
            "complete": True,
        },
        "raw_formulas": {
            "delta": (
                "3-2*SE2-3*SL-2*eta-SM-SF-a1-2*c2"
            ),
            "a2": "60-SE2-c2-2*SF",
            "r2": "30-SF",
            "n2": "357-a1-SL+SF",
            "y": "a3+3*n3-3801-SE2+SF",
            "h": "1287-n3-SF-g",
            "q": "3*n3+a3+eta+SM-3564",
            "p3": "7128-delta-2*a3-2*eta-SM-3*n3",
            "c1": "p3-c2",
            "n1": "a1+a2+a3",
            "p2": "n2",
            "b1": "2*n2",
            "r1": "a1+b1+c1",
            "J": "3564-delta",
            "T": "J-a3-eta",
            "epsilon": "SM-delta+3*q",
        },
        "symbolic_replay": {
            "SI": "0",
            "S2": "0",
            "SE2": "SE2",
            "RA": "0",
            "SL": "SL",
            "SF": "SF",
            "eta": "eta",
            "SM": "SM",
            "T-p3-q": "0",
            "3*n3-p3-(5*q-epsilon)": "0",
            "Q0": "7059",
        },
        "integrality": (
            "all displayed raw variables are integral for integral free "
            "counts and slacks; no hidden half-integrality remains"
        ),
        "nonnegativity_conditions": [
            "SE2+c2+2*SF<=60",
            "SF<=30",
            "a1+SL<=357+SF",
            "a3+3*n3+SF-SE2>=3801",
            "a3+3*n3+eta+SM>=3564",
            "p3>=c2",
            "0<=g<=1287-n3-SF",
            "0<=epsilon<=4*q",
            "delta,eta,SM,SF,SE2,SL,a1,c2>=0",
        ],
    }


def fibre_term(
    full_multiplicities: tuple[int, ...],
    selected_multiplicities: dict[int, int],
    *,
    baseline: bool,
) -> dict[str, int]:
    if not full_multiplicities:
        raise ValueError("occupied pair type required")
    if len(full_multiplicities) > 4:
        raise ValueError("four-point fibre exceeded")
    if any(value < 1 for value in full_multiplicities):
        raise ValueError("full multiplicities must be positive")
    degree = sum(full_multiplicities)
    if degree > 5:
        raise ValueError("simple pair degree exceeded")
    if baseline and degree != 5:
        raise ValueError("baseline is permitted only at degree five")
    for index, selected in selected_multiplicities.items():
        if not 0 <= index < len(full_multiplicities):
            raise ValueError("selected label absent")
        if not 1 <= selected <= full_multiplicities[index]:
            raise ValueError("selected multiplicity exceeds full")

    loss = degree - len(full_multiplicities)
    weighted = sum(value - 2 for value in selected_multiplicities.values())
    selected_gap = sum(
        full_multiplicities[index] - value
        for index, value in selected_multiplicities.items()
    )
    unselected_repetition = sum(
        full - 1
        for index, full in enumerate(full_multiplicities)
        if index not in selected_multiplicities
    )
    r = len(selected_multiplicities)
    gap = selected_gap + unselected_repetition
    term = gap + r - int(baseline)
    assert term == loss - int(baseline) - weighted
    assert term >= 0
    return {
        "degree": degree,
        "distinct_full_labels": len(full_multiplicities),
        "selected_labels": r,
        "loss": loss,
        "weighted": weighted,
        "selected_gap": selected_gap,
        "unselected_repetition": unselected_repetition,
        "baseline": int(baseline),
        "local_term": term,
    }


def local_equality_analysis() -> dict[str, object]:
    examples = {
        "tight_selected_m2": fibre_term(
            (2, 1, 1, 1),
            {0: 2},
            baseline=True,
        ),
        "tight_selected_m3": fibre_term(
            (3, 1, 1),
            {0: 3},
            baseline=True,
        ),
        "tight_empty_baseline": fibre_term(
            (2, 1, 1, 1),
            {},
            baseline=True,
        ),
        "tight_selected_m1": fibre_term(
            (1, 2, 1, 1),
            {0: 1},
            baseline=True,
        ),
        "nonbaseline_distinct": fibre_term(
            (1, 1, 1),
            {},
            baseline=False,
        ),
    }
    assert examples["tight_selected_m2"]["local_term"] == 0
    assert examples["tight_selected_m3"]["local_term"] == 0
    assert examples["tight_empty_baseline"]["local_term"] == 0
    assert examples["tight_selected_m1"]["local_term"] == 1
    assert examples["nonbaseline_distinct"]["local_term"] == 0

    return {
        "fibre_formula": (
            "local_term=sum_selected(n-m)+sum_unselected(n-1)+"
            "r-baseline"
        ),
        "deficient_center": (
            "sigma_x=36-3*c_x+sum_P[gap_P+r_P]"
        ),
        "tight_center": (
            "sigma_x=sum_P[gap_P+r_P-b_P], with b_P=1 on exactly "
            "the three degree-five Hilton-Milner pair types"
        ),
        "global": "SM=sum_x sigma_x",
        "slack_at_most_three": [
            "no center can have c_x<=10",
            "a c_x=11 center consumes at least three units",
            "each selected nonprivate label at a c_x=12 center consumes at least one unit",
            "at a tight center, zero local slack permits selected labels only in degree-five baseline fibres",
        ],
        "tight_zero_slack": {
            "nonbaseline": (
                "no selected nonprivate label and no repeated full label"
            ),
            "baseline_empty": (
                "exactly one unavoidable repeat among four full labels"
            ),
            "baseline_selected": (
                "exactly one selected label, full multiplicity equals "
                "selected multiplicity m in {2,3,4,5}, and every "
                "unselected full label has multiplicity one"
            ),
            "multiplicity_one": (
                "impossible at zero local slack; it costs at least one"
            ),
        },
        "examples": examples,
    }


def null_control() -> dict[str, object]:
    # The integer Wave201 face row, now paired with a locally compatible
    # zero-SM profile.  It is still not a graph or flag-family object.
    raw = {
        "C": 4158,
        "V": 99,
        "a1": 0,
        "a2": 60,
        "a3": 201,
        "b1": 714,
        "b3": 0,
        "c1": 3123,
        "c2": 0,
        "n1": 261,
        "n2": 357,
        "n3": 1200,
        "p2": 357,
        "p3": 3123,
        "r1": 3837,
        "r2": 30,
        "h": 67,
        "y": 0,
        "g": 20,
        "W": 0,
    }
    hidden = {
        "SE2": 0,
        "SL": 0,
        "delta": 3,
        "eta": 0,
        "SM": 0,
        "SF": 0,
        "J": 3561,
        "T": 3360,
        "q": 237,
        "epsilon": 708,
    }
    compatible_profile = {2: 234, 3: 3}
    q = sum(compatible_profile.values())
    incidence = sum(
        multiplicity * count
        for multiplicity, count in compatible_profile.items()
    )
    epsilon = sum(
        (5 - multiplicity) * count
        for multiplicity, count in compatible_profile.items()
    )
    weighted = sum(
        (multiplicity - 2) * count
        for multiplicity, count in compatible_profile.items()
    )
    q0 = (
        raw["n1"]
        + raw["n2"]
        + 2 * raw["n3"]
        + raw["r1"]
        + raw["r2"]
        + 2 * raw["h"]
        + raw["y"]
        + 2 * raw["g"]
    )
    assert q == hidden["q"] == 237
    assert incidence == 3 * raw["n3"] - raw["p3"] == 477
    assert epsilon == hidden["epsilon"] == 708
    assert weighted == hidden["delta"] == 3
    assert hidden["SM"] == hidden["delta"] - weighted == 0
    assert q0 == 7059
    assert 79 * 3 == q

    # The earlier arithmetic m=1 profile has the same aggregate values
    # but cannot realize local zero slack at a tight center.
    m1_profile = {1: 1, 2: 232, 3: 4}
    assert sum(m1_profile.values()) == q
    assert sum(k * v for k, v in m1_profile.items()) == incidence
    assert sum((5 - k) * v for k, v in m1_profile.items()) == epsilon

    return {
        "raw_row": {key: value for key, value in raw.items() if value},
        "hidden": hidden,
        "certificate_partition": "delta=3 and every other term zero",
        "locally_compatible_multiplicity_profile": {
            str(key): value for key, value in compatible_profile.items()
        },
        "local_distribution": (
            "79 tight centers use their three degree-five baseline "
            "fibres; 234 selected labels have m=2 and three have m=3; "
            "the other 20 tight centers carry no selected nonprivate label"
        ),
        "local_multiset_rules": (
            "selected m=2 uses full counts (2,1,1,1); selected m=3 "
            "uses (3,1,1); empty baselines use (2,1,1,1); "
            "nonbaseline full labels are distinct"
        ),
        "aggregate": {
            "q": q,
            "selected_incidence": incidence,
            "epsilon": epsilon,
            "weighted_loss": weighted,
            "Q0": q0,
        },
        "earlier_m1_accounting_profile": {
            "profile": {str(key): value for key, value in m1_profile.items()},
            "locally_zero_slack": False,
            "reason": (
                "a selected m=1 label in a tight degree-five fibre costs "
                "at least one local SM unit"
            ),
        },
        "asserted_graph_or_flag_family": False,
        "consequence": (
            "current one-center fibre inequalities do not exclude Q0=7059"
        ),
    }


def derive() -> dict[str, object]:
    return {
        "format": "wave202-three-unit-face-independent-v1",
        "verdict": "INDEPENDENTLY_DERIVED_PRE_SOURCE",
        "conditional_setting": (
            "prism-free rank-11 endpoint n3=4158, P=0"
        ),
        "face": symbolic_face(),
        "local_equality": local_equality_analysis(),
        "null_control": null_control(),
        "bound": {
            "Q0_face_excluded": False,
            "conditional_Q_lower": 7059,
            "conditional_Q_lower_improved": False,
            "all_projective_short_circuits": 7752,
            "nonzero_scalar_short_circuit_words": 15504,
        },
        "boundary": {
            "graph_constructed": False,
            "flag_family_constructed": False,
            "endpoint_excluded": False,
            "rank_11_excluded": False,
            "strict_original_n3_improvement": False,
            "external_novelty": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
        "stopping_point": (
            "the three-unit face is compatible with every current "
            "one-center fibre and aggregate identity; exclusion would "
            "require a cross-center gluing theorem not presently proved"
        ),
        "search_scope": (
            "symbolic affine elimination, exact fibre identities, and "
            "explicit non-object accounting controls only; no graph, "
            "configuration, family, cover, SAT, LP, enumeration, "
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
        print("PASS: source-blind Wave202 equality-face result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
