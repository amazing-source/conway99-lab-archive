"""Exact symbolic and arithmetic checks for Wave195 proof A.

The human proof supplies the Hilton--Milner flag-diversity row. This checker
verifies its local constants, the ternary cancellations, the exact rational
dual certificate, the integral bound, and a fractional null control.

No graph, code, cover, SAT, LP, configuration, enumeration, or isomorphism
search is performed.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from math import comb
from pathlib import Path


VARIABLES = (
    "H",
    "C",
    "n1",
    "n2",
    "n3",
    "p2",
    "p3",
    "a1",
    "a2",
    "a3",
    "b1",
    "b3",
    "c1",
    "c2",
    "r1",
    "r2",
    "h",
    "y",
    "g",
    "W",
)


def vector(**entries: int | Fraction) -> dict[str, Fraction]:
    return {name: Fraction(entries.get(name, 0)) for name in VARIABLES}


def add(
    left: dict[str, Fraction],
    right: dict[str, Fraction],
    scalar: Fraction = Fraction(1),
) -> dict[str, Fraction]:
    return {name: left[name] + scalar * right[name] for name in VARIABLES}


def substitute_raw_identities(
    expression: dict[str, Fraction],
) -> dict[str, Fraction]:
    substitutions = {
        "n1": {"a1": Fraction(1), "a2": Fraction(1), "a3": Fraction(1)},
        "p2": {"b1": Fraction(1, 2), "b3": Fraction(1, 2)},
        "p3": {"c1": Fraction(1), "c2": Fraction(1)},
        "r1": {"a1": Fraction(1), "b1": Fraction(1), "c1": Fraction(1)},
    }
    result = vector()
    for name, coefficient in expression.items():
        if name in substitutions:
            for target, scalar in substitutions[name].items():
                result[target] += coefficient * scalar
        else:
            result[name] += coefficient
    return result


def add_mod3(*vectors: list[int]) -> list[int]:
    return [sum(entries) % 3 for entries in zip(*vectors)]


def sub_mod3(left: list[int], right: list[int]) -> list[int]:
    return [(a - b) % 3 for a, b in zip(left, right)]


def weight(vector_value: list[int]) -> int:
    return sum(entry != 0 for entry in vector_value)


def ternary_cancellations() -> dict[str, object]:
    """Check the injectivity and intersecting-family cancellation words."""

    # Coordinates 0..6 are the seven center-star blocks. Coordinates 7,8
    # are two distinct leaf triangles.
    star = [1] * 7 + [0, 0]
    c4_a = [2, 2, 2, 0, 0, 0, 0, 1, 0]
    c4_aprime = [0, 0, 0, 2, 2, 2, 0, 0, 1]
    disjoint_sum = add_mod3(c4_a, c4_aprime, star)
    assert disjoint_sum == [0, 0, 0, 0, 0, 0, 1, 1, 1]

    c4_same_a_second_leaf = [2, 2, 2, 0, 0, 0, 0, 0, 1]
    equal_a_difference = sub_mod3(c4_a, c4_same_a_second_leaf)
    assert equal_a_difference == [0, 0, 0, 0, 0, 0, 0, 1, 2]

    return {
        "coordinate_order": "7 center-star blocks, leaf T, leaf T-prime",
        "disjoint_A_cancellation": disjoint_sum,
        "disjoint_A_cancellation_weight": weight(disjoint_sum),
        "equal_A_cancellation": equal_a_difference,
        "equal_A_cancellation_weight": weight(equal_a_difference),
        "dual_distance_input": 4,
        "consequences": [
            "T maps injectively to A_x(T)",
            "the A_x(T) family is pairwise intersecting",
        ],
    }


def local_set_system() -> dict[str, object]:
    n = 7
    k = 3
    graph_degree = 14
    common_star_neighbor_cap = graph_degree - 2
    hm_first = comb(n - 1, k - 1)
    hm_subtracted = comb(n - k - 1, k - 1)
    hm_cap = hm_first - hm_subtracted + 1
    vertices = 99
    hm_global_capacity = vertices * hm_cap
    affine_constant = vertices * 39

    assert n > 2 * k
    assert common_star_neighbor_cap == 12
    assert hm_first == 15
    assert hm_subtracted == 3
    assert hm_cap == 13
    assert hm_global_capacity == 1287
    assert affine_constant == 3861

    return {
        "ground_set_size": n,
        "uniformity": k,
        "graph_degree": graph_degree,
        "lambda": 1,
        "common_star_distinct_neighbor_cap": common_star_neighbor_cap,
        "common_star_local_row": "j_x<=12+12+c_x<=39",
        "unified_local_row": "j_x<=39",
        "hilton_milner": {
            "hypothesis": "n>2k, pairwise intersecting, empty total intersection",
            "formula": "C(n-1,k-1)-C(n-k-1,k-1)+1",
            "first_term": hm_first,
            "subtracted_term": hm_subtracted,
            "nontrivial_cap": hm_cap,
            "reference_doi": "10.1093/qmath/18.1.369",
        },
        "vertices": vertices,
        "hm_global_center_capacity": hm_global_capacity,
        "affine_constant_H": affine_constant,
        "global_oriented_label_row": "J<=H",
        "cover_lower_row": "J>=C-n1-2*n2+a3+b3",
        "new_slack": "SG=H-C+n1+2*n2-a3-b3>=0",
    }


def certificate_remainder() -> dict[str, Fraction]:
    objective = vector(
        H=Fraction(1, 6),
        C=Fraction(-11, 6),
        n1=1,
        n2=1,
        n3=2,
        r1=1,
        r2=1,
        h=2,
        y=1,
        g=2,
        W=1,
    )
    slacks = {
        "SI": vector(C=-2, n1=2, n2=2, n3=3, p2=1, p3=1),
        "S2": vector(p2=1, n2=-1),
        "SE2": vector(r2=2, a2=-1, c2=-1),
        "RA": vector(
            h=3,
            y=1,
            g=3,
            a2=-1,
            a3=-1,
            b3=-2,
            c2=-1,
        ),
        "SL": vector(C=-1, n1=1, n2=2, c1=1, r2=2, y=1, W=2),
        "SG": vector(
            H=1,
            C=-1,
            n1=1,
            n2=2,
            a3=-1,
            b3=-1,
        ),
    }
    weights = {
        "SI": Fraction(2, 3),
        "S2": Fraction(4, 3),
        "SE2": Fraction(1, 6),
        "RA": Fraction(2, 3),
        "SL": Fraction(1, 3),
        "SG": Fraction(1, 6),
    }
    remainder = objective
    for name, slack in slacks.items():
        remainder = add(remainder, slack, -weights[name])
    return substitute_raw_identities(remainder)


def evaluate_row(row: dict[str, Fraction]) -> dict[str, Fraction]:
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
        "I": incidence,
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
        "SG": (
            row["H"]
            - row["C"]
            + row["n1"]
            + 2 * row["n2"]
            - row["a3"]
            - row["b3"]
        ),
    }


def rational_null_row() -> dict[str, object]:
    row = vector(
        H=3861,
        C=4158,
        n2=Fraction(297, 2),
        n3=Fraction(2673, 2),
        p2=Fraction(297, 2),
        p3=3861,
        b1=297,
        c1=3861,
        r1=4158,
    )
    evaluation = evaluate_row(row)
    assert row["a1"] + row["a2"] + row["a3"] == row["n1"]
    assert row["b1"] + row["b3"] == 2 * row["p2"]
    assert row["c1"] + row["c2"] == row["p3"]
    assert row["a1"] + row["b1"] + row["c1"] == row["r1"]
    assert all(evaluation[name] == 0 for name in ("SI", "S2", "SE2", "RA", "SL", "SG"))
    target = Fraction(11 * row["C"] - row["H"], 6)
    assert evaluation["Q0"] == target == Fraction(13959, 2)
    return {
        "row": {
            name: str(value)
            for name, value in row.items()
            if value
        },
        "evaluation": {
            name: str(value)
            for name, value in evaluation.items()
        },
        "target": str(target),
        "is_object": False,
    }


def derive() -> dict[str, object]:
    local = local_set_system()
    remainder = certificate_remainder()
    expected_remainder = vector(
        a1=Fraction(1, 6),
        b3=Fraction(1, 2),
        c2=Fraction(1, 6),
        W=Fraction(1, 3),
    )
    assert remainder == expected_remainder

    c = 4158
    hm_capacity = int(local["hm_global_center_capacity"])
    affine_constant = int(local["affine_constant_H"])
    target = Fraction(11 * c - affine_constant, 6)
    integer_q = (target.numerator + target.denominator - 1) // target.denominator
    assert target == Fraction(13959, 2)
    assert integer_q == 6980
    all_projective = integer_q + 693
    scalar_words = 2 * all_projective
    assert all_projective == 7673
    assert scalar_words == 15346

    result = {
        "ternary_cancellations": ternary_cancellations(),
        "local_set_system": local,
        "certificate": {
            "target": "(11*C-H)/6",
            "slack_weights": {
                "SI": "2/3",
                "S2": "4/3",
                "SE2": "1/6",
                "RA": "2/3",
                "SL": "1/3",
                "SG": "1/6",
            },
            "remainder_coefficients": {
                name: str(value)
                for name, value in remainder.items()
                if value
            },
            "all_remainder_coefficients_nonnegative": all(
                value >= 0 for value in remainder.values()
            ),
        },
        "bound": {
            "C": c,
            "H": affine_constant,
            "rational_Q0": str(target),
            "integral_Q": integer_q,
            "edge_added_projective": all_projective,
            "circuit_scalar_words": scalar_words,
        },
        "rational_null_control": rational_null_row(),
        "old_equality_face": {
            "packets": c // 3,
            "global_center_capacity": hm_capacity,
            "capacity_deficit": c // 3 - hm_capacity,
            "SG": affine_constant - c,
            "refuted_Q": 5 * c // 3,
        },
        "claim": {
            "new_slack": "H-C+n1+2*n2-a3-b3>=0",
            "rational_bound": "Q>=(11*C-H)/6",
            "integral_bound": "Q>=6980",
        },
        "search_scope": (
            "fixed ternary cancellations, binomial coefficients, exact "
            "rational coefficient algebra, and symbolic counting only; no "
            "graph, code, cover, SAT, LP, configuration, enumeration, or "
            "isomorphism search"
        ),
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
    }
    assert result["old_equality_face"]["packets"] == 1386
    assert result["old_equality_face"]["capacity_deficit"] == 99
    assert result["old_equality_face"]["SG"] == -297
    assert result["old_equality_face"]["refuted_Q"] == 6930
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print("PASS: Wave195 proof-A exact result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
