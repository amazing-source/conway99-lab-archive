"""Exact checks for the Wave 195 fixed-center packet bound.

Only fixed F_3 coefficient identities and exact rational arithmetic are
used.  There is no graph, code, cover, SAT, LP, configuration,
enumeration, or isomorphism search.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


VARIABLES = (
    "C K n1 n2 n3 p2 p3 a1 a2 a3 b1 b3 c1 c2 "
    "r1 r2 h y g W"
).split()


def basis(name: str) -> dict[str, Fraction]:
    return {variable: Fraction(variable == name) for variable in VARIABLES}


def add(*vectors: dict[str, Fraction]) -> dict[str, Fraction]:
    return {
        variable: sum((vector[variable] for vector in vectors), Fraction())
        for variable in VARIABLES
    }


def scale(
    multiplier: Fraction | int,
    vector: dict[str, Fraction],
) -> dict[str, Fraction]:
    return {
        variable: Fraction(multiplier) * vector[variable]
        for variable in VARIABLES
    }


def add_mod3(*vectors: list[int]) -> list[int]:
    return [
        sum(vector[index] for vector in vectors) % 3
        for index in range(len(vectors[0]))
    ]


def scale_mod3(multiplier: int, vector: list[int]) -> list[int]:
    return [(multiplier * value) % 3 for value in vector]


def support(vector: list[int]) -> list[int]:
    return [index for index, value in enumerate(vector) if value]


def local_coefficient_checks() -> dict[str, object]:
    # Coordinates 0..6 are the seven x-star blocks.  Coordinates 7 and 8
    # are two distinct leaf triangles T,T'.
    star = [1] * 7 + [0, 0]
    c4_a = [2, 2, 2, 0, 0, 0, 0, 1, 0]
    c4_same_a = [2, 2, 2, 0, 0, 0, 0, 0, 1]
    c4_disjoint_a = [0, 0, 0, 2, 2, 2, 0, 0, 1]

    equal_a_difference = add_mod3(
        c4_a,
        scale_mod3(2, c4_same_a),
    )
    disjoint_a_sum = add_mod3(c4_a, c4_disjoint_a, star)

    assert support(equal_a_difference) == [7, 8]
    assert support(disjoint_a_sum) == [6, 7, 8]

    return {
        "coordinate_order": "seven center-star blocks, T, T_prime",
        "equal_A_difference": equal_a_difference,
        "equal_A_difference_weight": len(support(equal_a_difference)),
        "disjoint_A_plus_star": disjoint_a_sum,
        "disjoint_A_plus_star_weight": len(support(disjoint_a_sum)),
        "consequences_at_dual_distance_at_least_4": {
            "leaf_to_A_injective": True,
            "A_family_pairwise_intersecting": True,
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
        "SG": add(
            v["K"],
            scale(-1, v["C"]),
            v["n1"],
            scale(2, v["n2"]),
            scale(-1, v["a3"]),
            scale(-1, v["b3"]),
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
    terms = [
        ("SI", Fraction(2, 3), slacks["SI"]),
        ("S2", Fraction(4, 3), slacks["S2"]),
        ("SE2", Fraction(1, 6), slacks["SE2"]),
        ("RA", Fraction(2, 3), slacks["RA"]),
        ("SL", Fraction(1, 3), slacks["SL"]),
        ("SG", Fraction(1, 6), slacks["SG"]),
        ("a1", Fraction(1, 6), v["a1"]),
        ("b3", Fraction(1, 2), v["b3"]),
        ("c2", Fraction(1, 6), v["c2"]),
        ("W", Fraction(1, 3), v["W"]),
    ]
    right = add(*(scale(coefficient, vector) for _, coefficient, vector in terms))
    difference = add(
        q0,
        scale(Fraction(-11, 6), v["C"]),
        scale(Fraction(1, 6), v["K"]),
        scale(-1, right),
    )

    substitutions = {
        "n1": {"a1": Fraction(1), "a2": Fraction(1), "a3": Fraction(1)},
        "p2": {"b1": Fraction(1, 2), "b3": Fraction(1, 2)},
        "p3": {"c1": Fraction(1), "c2": Fraction(1)},
        "r1": {"a1": Fraction(1), "b1": Fraction(1), "c1": Fraction(1)},
    }
    reduced = {
        name: coefficient
        for name, coefficient in difference.items()
        if name not in substitutions
    }
    for name, replacement in substitutions.items():
        for target, multiplier in replacement.items():
            reduced[target] = (
                reduced.get(target, Fraction())
                + difference[name] * multiplier
            )
    reduced = {
        name: str(coefficient)
        for name, coefficient in reduced.items()
        if coefficient
    }
    assert reduced == {}

    c = 4158
    k = 99 * 39
    rational_target = Fraction(11 * c - k, 6)
    integer_bound = (rational_target.numerator + rational_target.denominator - 1) // (
        rational_target.denominator
    )

    null_row = {name: Fraction() for name in VARIABLES}
    null_row.update(
        {
            "C": Fraction(c),
            "K": Fraction(k),
            "n1": Fraction(99),
            "a2": Fraction(99),
            "n2": Fraction(99),
            "p2": Fraction(99),
            "b1": Fraction(198),
            "n3": Fraction(1386),
            "p3": Fraction(3663),
            "c1": Fraction(3663),
            "r1": Fraction(3861),
            "r2": Fraction(99, 2),
            "y": Fraction(99),
        }
    )

    def evaluate(vector: dict[str, Fraction]) -> Fraction:
        return sum(
            vector[name] * null_row[name]
            for name in VARIABLES
        )

    null_slacks = {name: evaluate(vector) for name, vector in slacks.items()}
    assert all(value == 0 for value in null_slacks.values())
    assert evaluate(q0) == rational_target
    assert (
        null_row["n1"]
        == null_row["a1"] + null_row["a2"] + null_row["a3"]
    )
    assert 2 * null_row["p2"] == null_row["b1"] + null_row["b3"]
    assert null_row["p3"] == null_row["c1"] + null_row["c2"]
    assert (
        null_row["r1"]
        == null_row["a1"] + null_row["b1"] + null_row["c1"]
    )

    return {
        "identity": (
            "Q0-(11*C-K)/6=(2/3)SI+(4/3)S2+(1/6)SE2+"
            "(2/3)RA+(1/3)SL+(1/6)SG+a1/6+b3/2+c2/6+W/3"
        ),
        "multipliers": {
            name: str(coefficient)
            for name, coefficient, _ in terms
        },
        "reduced_difference": reduced,
        "C": c,
        "K": k,
        "rational_Q_target": str(rational_target),
        "integer_Q_lower_bound": integer_bound,
        "edge_added_projective": integer_bound + 693,
        "circuit_scalar_words": 2 * (integer_bound + 693),
        "rational_null": {
            "n3": "1386",
            "n2=p2": "99",
            "b1": "198",
            "p3=c1": "3663",
            "r1": "3861",
            "n1=a2": "99",
            "r2": "99/2",
            "y": "99",
            "all_other_variables": "0",
            "all_six_slacks_zero": True,
            "asserted_object": False,
        },
    }


def derive() -> dict[str, object]:
    hm_nontrivial_cap = 15 - 3 + 1
    ekr_trivial_cap = 15
    trivial_neighbor_base = 14 - 2
    label_cap_per_center = 39
    k = 99 * label_cap_per_center

    assert hm_nontrivial_cap == 13
    assert ekr_trivial_cap == 15
    assert trivial_neighbor_base == 12
    assert k == 3861

    result = {
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "conditional_scope": (
            "prism-free rank-11 endpoint and the verified Wave194 "
            "pool/slack system"
        ),
        "local_coefficients": local_coefficient_checks(),
        "fixed_center_theorem": {
            "ground_set_size": 7,
            "subset_size": 3,
            "leaf_to_A_injective": True,
            "A_family_pairwise_intersecting": True,
            "hilton_milner_nontrivial_cap": hm_nontrivial_cap,
            "erdos_ko_rado_trivial_cap": ekr_trivial_cap,
            "trivial_common_block_neighbor_base": trivial_neighbor_base,
            "universal_oriented_label_cap": "j_x<=39",
        },
        "global_row": {
            "definition": (
                "SG=K-C+n1+2*n2-a3-b3>=0"
            ),
            "K": k,
            "upper": "J<=K",
            "lower": "J>=C-n1-2*n2+a3+b3",
        },
        "certificate": certificate(),
        "search_scope": (
            "fixed F3 coefficient identities and exact rational "
            "extremal-set arithmetic only; no graph, code, cover, SAT, "
            "LP, configuration, enumeration, or isomorphism search"
        ),
    }
    assert result["certificate"]["integer_Q_lower_bound"] == 6980
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
        print("PASS: Wave195 fixed-center packet bound matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
