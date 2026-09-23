"""Source-blind exact verifier for Wave201 multiplicity-weighted loss.

The local proof treats arbitrary selected multiplicities inside one
four-point pair fibre.  The global proof uses exact rational coefficient
algebra.  No Wave201 source is imported, and no graph, configuration,
family, cover, SAT, LP, isomorphism, or brute-force search is performed.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


VARIABLES = (
    "C V n1 n2 n3 p2 p3 a1 a2 a3 b1 b3 c1 c2 "
    "r1 r2 h y g W"
).split()


def basis(name: str) -> dict[str, Fraction]:
    return {variable: Fraction(variable == name) for variable in VARIABLES}


def add(
    *vectors: dict[str, Fraction],
) -> dict[str, Fraction]:
    return {
        variable: sum(
            (vector[variable] for vector in vectors),
            Fraction(),
        )
        for variable in VARIABLES
    }


def scale(
    multiplier: int | Fraction,
    vector: dict[str, Fraction],
) -> dict[str, Fraction]:
    return {
        variable: Fraction(multiplier) * vector[variable]
        for variable in VARIABLES
    }


def substitute_raw_identities(
    expression: dict[str, Fraction],
) -> dict[str, Fraction]:
    substitutions = {
        "n1": {"a1": Fraction(1), "a2": Fraction(1), "a3": Fraction(1)},
        "p2": {"b1": Fraction(1, 2), "b3": Fraction(1, 2)},
        "p3": {"c1": Fraction(1), "c2": Fraction(1)},
        "r1": {"a1": Fraction(1), "b1": Fraction(1), "c1": Fraction(1)},
    }
    result = {variable: Fraction() for variable in VARIABLES}
    for variable, coefficient in expression.items():
        if variable in substitutions:
            for target, scalar in substitutions[variable].items():
                result[target] += coefficient * scalar
        else:
            result[variable] += coefficient
    return result


def nonzero_strings(
    vector: dict[str, Fraction],
) -> dict[str, str]:
    return {
        variable: str(value)
        for variable, value in vector.items()
        if value
    }


def fibre_profile(
    full: dict[str, int],
    selected: dict[str, int],
) -> dict[str, int]:
    if not full:
        if selected:
            raise ValueError("selected labels require full-pool labels")
        return {
            "d": 0,
            "u": 0,
            "r": 0,
            "loss": 0,
            "weighted": 0,
            "decomposition": 0,
        }
    if len(full) > 4:
        raise ValueError("a pair fibre has only four labels")
    if any(value < 1 for value in full.values()):
        raise ValueError("full multiplicities must be positive")
    if sum(full.values()) > 5:
        raise ValueError("a simple triple family has pair degree at most five")
    for label, multiplicity in selected.items():
        if label not in full:
            raise ValueError("selected label absent from full pool")
        if not 1 <= multiplicity <= full[label]:
            raise ValueError("selected multiplicity exceeds full multiplicity")

    d = sum(full.values())
    u = len(full)
    r = len(selected)
    loss = d - u
    weighted = sum(value - 2 for value in selected.values())
    decomposition = (
        sum(
            full[label] - multiplicity + 1
            for label, multiplicity in selected.items()
        )
        + sum(
            multiplicity - 1
            for label, multiplicity in full.items()
            if label not in selected
        )
    )
    assert loss - weighted == decomposition
    assert decomposition >= r
    return {
        "d": d,
        "u": u,
        "r": r,
        "loss": loss,
        "weighted": weighted,
        "decomposition": decomposition,
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

    result: dict[str, object] = {}
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
        assert sum(degrees.values()) == 39
        result[name] = {
            "members": len(family),
            "pair_occurrences": sum(degrees.values()),
            "maximum_pair_degree": max(degrees.values()),
            "degree_five_pairs": degree_five,
            "number_degree_five_pairs": len(degree_five),
        }
    return result


def local_theorem() -> dict[str, object]:
    examples = {
        "multiplicity_one": fibre_profile(
            {"a": 1},
            {"a": 1},
        ),
        "two_selected_labels_same_fibre": fibre_profile(
            {"a": 3, "b": 2},
            {"a": 3, "b": 2},
        ),
        "multiplicity_one_plus_four": fibre_profile(
            {"a": 1, "b": 4},
            {"a": 1, "b": 4},
        ),
        "selected_strictly_below_full": fibre_profile(
            {"a": 4, "b": 1},
            {"a": 2},
        ),
        "four_distinct_full_labels": fibre_profile(
            {"a": 2, "b": 1, "c": 1, "d": 1},
            {"a": 1, "b": 1},
        ),
    }
    assert examples["multiplicity_one"]["weighted"] == -1
    assert examples["two_selected_labels_same_fibre"]["r"] == 2
    assert examples["multiplicity_one_plus_four"]["weighted"] == 1

    return {
        "fibre_identity": (
            "(d-u)-sum_selected(m-2)="
            "sum_selected(n-m+1)+sum_unselected(n-1)"
        ),
        "fibre_consequence": (
            "d-u>=sum_selected(m-2)+r>=sum_selected(m-2)"
        ),
        "hostile_profiles": examples,
        "deficient_center": {
            "scope": "c_x<=12",
            "identity": (
                "delta_x=36-3*c_x+sum_P(d_P-u_P)"
            ),
            "conclusion": (
                "delta_x>=sum_nonprivate_y(m_x(y)-2)"
            ),
        },
        "tight_center": {
            "scope": "c_x=13",
            "hilton_milner_templates": hilton_milner_templates(),
            "baseline": (
                "exactly three d_P=5 fibres, each with d_P-u_P>=1"
            ),
            "degree_five_selected_case": (
                "if r_P>=1 then d_P-u_P>=weighted_P+r_P"
                ">=weighted_P+1"
            ),
            "degree_five_unselected_case": (
                "if r_P=0 then weighted_P=0 and d_P-u_P>=1"
            ),
            "conclusion": (
                "delta_x=sum_P(d_P-u_P)-3"
                ">=sum_nonprivate_y(m_x(y)-2)"
            ),
        },
        "selected_vs_full_guard": (
            "each selected occurrence is a full-pool occurrence of the "
            "same oriented label, so m_y<=n_y; unselected full labels "
            "remain in u_P and in the exact loss decomposition"
        ),
        "global": {
            "weighted_identity": (
                "sum_nonprivate(m-2)=3*q-epsilon"
            ),
            "new_slack": "SM=delta-3*q+epsilon>=0",
        },
    }


def certificate() -> dict[str, object]:
    v = {name: basis(name) for name in VARIABLES}
    incidence = add(
        scale(2, v["n1"]),
        scale(2, v["n2"]),
        scale(3, v["n3"]),
        v["p2"],
        v["p3"],
    )
    slacks = {
        "SI": add(incidence, scale(-2, v["C"])),
        "S2": add(v["p2"], scale(-1, v["n2"])),
        "SE2": add(
            scale(2, v["r2"]),
            scale(-1, v["a2"]),
            scale(-1, v["c2"]),
        ),
        "RA": add(
            scale(3, v["h"]),
            v["y"],
            scale(3, v["g"]),
            scale(-1, v["a2"]),
            scale(-1, v["a3"]),
            scale(-2, v["b3"]),
            scale(-1, v["c2"]),
        ),
        "SL": add(
            v["n1"],
            scale(2, v["n2"]),
            v["c1"],
            scale(2, v["r2"]),
            v["y"],
            scale(2, v["W"]),
            scale(-1, v["C"]),
        ),
        "SF": add(
            scale(13, v["V"]),
            scale(-1, v["n3"]),
            scale(-1, v["h"]),
            scale(-1, v["g"]),
        ),
    }
    q0 = add(
        v["n1"],
        v["n2"],
        scale(2, v["n3"]),
        v["r1"],
        v["r2"],
        scale(2, v["h"]),
        v["y"],
        scale(2, v["g"]),
        v["W"],
    )

    # After delta=36V-J, eta=J-T-a3-b3, T=p3+q,
    # epsilon=p3+5q-3n3, and SM=delta-3q+epsilon:
    # delta+2eta+SM+SF
    #   =85V-p3-2a3-2b3-4n3-h-g.
    weighted_local_bundle = add(
        scale(85, v["V"]),
        scale(-1, v["p3"]),
        scale(-2, v["a3"]),
        scale(-2, v["b3"]),
        scale(-4, v["n3"]),
        scale(-1, v["h"]),
        scale(-1, v["g"]),
    )

    terms = [
        ("SI", Fraction(4, 5), slacks["SI"]),
        ("S2", Fraction(6, 5), slacks["S2"]),
        ("SE2", Fraction(1, 5), slacks["SE2"]),
        ("RA", Fraction(7, 10), slacks["RA"]),
        ("SL", Fraction(3, 10), slacks["SL"]),
        (
            "delta+2eta+SM+SF",
            Fraction(1, 10),
            weighted_local_bundle,
        ),
        ("a1", Fraction(1, 10), v["a1"]),
        ("b3", Fraction(3, 5), v["b3"]),
        ("c2", Fraction(1, 5), v["c2"]),
        ("W", Fraction(2, 5), v["W"]),
    ]
    right = add(*(scale(weight, vector) for _, weight, vector in terms))
    left = add(
        q0,
        scale(Fraction(-19, 10), v["C"]),
        scale(Fraction(85, 10), v["V"]),
    )
    reduced_difference = substitute_raw_identities(add(left, scale(-1, right)))
    assert nonzero_strings(reduced_difference) == {}

    c = 4158
    vertices = 99
    target = Fraction(19 * c - 85 * vertices, 10)
    assert target == Fraction(70587, 10)
    assert -((-target.numerator) // target.denominator) == 7059

    return {
        "weighted_local_bundle_derivation": (
            "delta+2*eta+SM+SF="
            "85*V-p3-2*a3-2*b3-4*n3-h-g"
        ),
        "identity": (
            "Q0-(19*C-85*V)/10="
            "4*SI/5+6*S2/5+SE2/5+7*RA/10+3*SL/10+"
            "delta/10+eta/5+SM/10+SF/10+"
            "a1/10+3*b3/5+c2/5+2*W/5"
        ),
        "reduced_difference": nonzero_strings(reduced_difference),
        "target": str(target),
        "integer_Q_lower": 7059,
        "edge_isolated_projective": 693,
        "all_projective_short_circuits": 7059 + 693,
        "nonzero_scalar_short_circuit_words": 2 * (7059 + 693),
    }


def evaluate_row(
    row: dict[str, Fraction],
    hidden: dict[str, Fraction],
) -> dict[str, Fraction]:
    incidence = (
        2 * row["n1"]
        + 2 * row["n2"]
        + 3 * row["n3"]
        + row["p2"]
        + row["p3"]
    )
    q0 = (
        row["n1"]
        + row["n2"]
        + 2 * row["n3"]
        + row["r1"]
        + row["r2"]
        + 2 * row["h"]
        + row["y"]
        + 2 * row["g"]
        + row["W"]
    )
    return {
        "Q0": q0,
        "SI": incidence - 2 * row["C"],
        "S2": row["p2"] - row["n2"],
        "SE2": 2 * row["r2"] - row["a2"] - row["c2"],
        "RA": (
            3 * row["h"]
            + row["y"]
            + 3 * row["g"]
            - row["a2"]
            - row["a3"]
            - 2 * row["b3"]
            - row["c2"]
        ),
        "SL": (
            row["n1"]
            + 2 * row["n2"]
            + row["c1"]
            + 2 * row["r2"]
            + row["y"]
            + 2 * row["W"]
            - row["C"]
        ),
        "SF": 13 * row["V"] - row["n3"] - row["h"] - row["g"],
        "SH": 3 * row["h"] - row["a3"] - row["b3"],
        "delta": hidden["delta"],
        "eta": hidden["eta"],
        "epsilon": hidden["epsilon"],
        "SM": (
            hidden["delta"] - 3 * hidden["q"] + hidden["epsilon"]
        ),
        "selected_nonprivate_incidence": 5 * hidden["q"] - hidden["epsilon"],
    }


def make_row(**entries: int | Fraction) -> dict[str, Fraction]:
    return {
        variable: Fraction(entries.get(variable, 0))
        for variable in VARIABLES
    }


def accounting_controls() -> dict[str, object]:
    integer_row = make_row(
        C=4158,
        V=99,
        n1=261,
        n2=357,
        n3=1200,
        p2=357,
        p3=3123,
        a2=60,
        a3=201,
        b1=714,
        c1=3123,
        r1=3837,
        r2=30,
        h=67,
        g=20,
    )
    integer_hidden = {
        "delta": Fraction(3),
        "J": Fraction(3561),
        "eta": Fraction(0),
        "T": Fraction(3360),
        "q": Fraction(237),
        "epsilon": Fraction(708),
    }
    integer_eval = evaluate_row(integer_row, integer_hidden)
    integer_profile = {1: 1, 2: 232, 3: 4}
    profile_q = sum(integer_profile.values())
    profile_incidence = sum(
        multiplicity * count
        for multiplicity, count in integer_profile.items()
    )
    profile_epsilon = sum(
        (5 - multiplicity) * count
        for multiplicity, count in integer_profile.items()
    )
    profile_weighted = sum(
        (multiplicity - 2) * count
        for multiplicity, count in integer_profile.items()
    )

    assert integer_row["n1"] == (
        integer_row["a1"] + integer_row["a2"] + integer_row["a3"]
    )
    assert 2 * integer_row["p2"] == integer_row["b1"] + integer_row["b3"]
    assert integer_row["p3"] == integer_row["c1"] + integer_row["c2"]
    assert integer_row["r1"] == (
        integer_row["a1"] + integer_row["b1"] + integer_row["c1"]
    )
    assert integer_hidden["J"] == 36 * integer_row["V"] - 3
    assert integer_hidden["T"] == (
        integer_hidden["J"] - integer_row["a3"] - integer_row["b3"]
    )
    assert integer_hidden["q"] == integer_hidden["T"] - integer_row["p3"]
    assert profile_q == integer_hidden["q"]
    assert profile_incidence == 3 * integer_row["n3"] - integer_row["p3"]
    assert profile_epsilon == integer_hidden["epsilon"]
    assert profile_weighted == integer_hidden["delta"]
    assert integer_eval["Q0"] == 7059
    assert all(
        integer_eval[name] == 0
        for name in ("SI", "S2", "SE2", "RA", "SL", "SF", "SH", "eta", "SM")
    )
    assert integer_eval["delta"] == 3

    rational_row = make_row(
        C=4158,
        V=99,
        n1=261,
        n2=Fraction(1782, 5),
        n3=1200,
        p2=Fraction(1782, 5),
        p3=Fraction(15624, 5),
        a2=Fraction(297, 5),
        a3=Fraction(1008, 5),
        b1=Fraction(3564, 5),
        c1=Fraction(15624, 5),
        r1=Fraction(19188, 5),
        r2=Fraction(297, 10),
        h=Fraction(336, 5),
        g=Fraction(99, 5),
    )
    rational_hidden = {
        "delta": Fraction(0),
        "J": Fraction(3564),
        "eta": Fraction(0),
        "T": Fraction(16812, 5),
        "q": Fraction(1188, 5),
        "epsilon": Fraction(3564, 5),
    }
    rational_eval = evaluate_row(rational_row, rational_hidden)
    assert rational_row["n1"] == (
        rational_row["a1"] + rational_row["a2"] + rational_row["a3"]
    )
    assert 2 * rational_row["p2"] == rational_row["b1"]
    assert rational_row["p3"] == rational_row["c1"]
    assert rational_row["r1"] == rational_row["b1"] + rational_row["c1"]
    assert rational_hidden["T"] == rational_hidden["J"] - rational_row["a3"]
    assert rational_hidden["q"] == rational_hidden["T"] - rational_row["p3"]
    assert rational_eval["Q0"] == Fraction(70587, 10)
    assert all(
        rational_eval[name] == 0
        for name in (
            "SI",
            "S2",
            "SE2",
            "RA",
            "SL",
            "SF",
            "SH",
            "delta",
            "eta",
            "SM",
        )
    )

    def nonzero_row(row: dict[str, Fraction]) -> dict[str, str]:
        return {
            name: str(value)
            for name, value in row.items()
            if value
        }

    def evaluation_strings(
        evaluation: dict[str, Fraction],
    ) -> dict[str, str]:
        return {
            name: str(value)
            for name, value in evaluation.items()
        }

    return {
        "integer_near_equality": {
            "row": nonzero_row(integer_row),
            "hidden": {
                name: str(value)
                for name, value in integer_hidden.items()
            },
            "evaluation": evaluation_strings(integer_eval),
            "multiplicity_profile": {
                str(multiplicity): count
                for multiplicity, count in integer_profile.items()
            },
            "profile_q": profile_q,
            "profile_incidence": profile_incidence,
            "profile_epsilon": profile_epsilon,
            "profile_weighted_loss": profile_weighted,
            "scaled_certificate_budget": 3,
            "only_positive_certificate_term": "delta=3",
            "asserted_object": False,
        },
        "rational_equality": {
            "row": nonzero_row(rational_row),
            "hidden": {
                name: str(value)
                for name, value in rational_hidden.items()
            },
            "evaluation": evaluation_strings(rational_eval),
            "asserted_object": False,
        },
    }


def derive() -> dict[str, object]:
    return {
        "format": "wave201-multiplicity-weighted-independent-v1",
        "verdict": "INDEPENDENTLY_DERIVED_PRE_SOURCE",
        "conditional_setting": (
            "prism-free rank-11 endpoint n3=4158, P=0"
        ),
        "local_theorem": local_theorem(),
        "certificate": certificate(),
        "accounting_controls": accounting_controls(),
        "boundary": {
            "graph_constructed": False,
            "flag_family_constructed": False,
            "code_or_cover_constructed": False,
            "endpoint_excluded": False,
            "rank_11_excluded": False,
            "strict_original_n3_improvement": False,
            "external_novelty": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
        "search_scope": (
            "symbolic fibre decomposition, two fixed Hilton-Milner "
            "formulas, exact rational coefficient algebra, and explicit "
            "accounting rows only; no graph, configuration, family, cover, "
            "SAT, LP, enumeration, isomorphism, or brute-force search"
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
        print("PASS: source-blind Wave201 result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
