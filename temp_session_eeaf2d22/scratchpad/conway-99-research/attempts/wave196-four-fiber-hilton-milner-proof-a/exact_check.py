"""Exact symbolic checks for Wave196 proof A.

This checks the two fixed Hilton--Milner equality templates, four-fiber
arithmetic, the Q>=7029 rational certificate, and its integer arithmetic
null row. It performs no graph, code, cover, SAT, LP, configuration,
enumeration, or isomorphism search.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction
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


def pair_degrees(family: set[frozenset[int]]) -> Counter[frozenset[int]]:
    degrees: Counter[frozenset[int]] = Counter()
    for triple in family:
        for pair in itertools.combinations(sorted(triple), 2):
            degrees[frozenset(pair)] += 1
    return degrees


def hilton_milner_templates() -> dict[str, object]:
    ground = set(range(7))

    special = frozenset({1, 2, 3})
    hm = {special}
    for pair in itertools.combinations(sorted(ground - {0}), 2):
        if set(pair) & set(special):
            hm.add(frozenset({0, *pair}))

    core = {0, 1, 2}
    triangle = {
        frozenset(triple)
        for triple in itertools.combinations(sorted(ground), 3)
        if len(set(triple) & core) >= 2
    }

    result: dict[str, object] = {}
    for name, family in (("H", hm), ("K", triangle)):
        degrees = pair_degrees(family)
        degree_five = sorted(
            [sorted(pair) for pair, degree in degrees.items() if degree == 5]
        )
        assert len(family) == 13
        assert len(degree_five) == 3
        assert max(degrees.values()) == 5
        assert sum(degrees.values()) == 39
        fiber_capacity = 4
        forced_repeats = sum(
            max(0, degree - fiber_capacity) for degree in degrees.values()
        )
        assert forced_repeats >= 3
        assert 3 * len(family) - forced_repeats <= 36
        result[name] = {
            "members": len(family),
            "pair_degree_five": degree_five,
            "number_pair_degree_five": len(degree_five),
            "total_pair_incidences": sum(degrees.values()),
            "forced_fiber_repeats": forced_repeats,
            "leaf_union_cap": 3 * len(family) - forced_repeats,
        }
    return result


def local_geometry() -> dict[str, object]:
    star_blocks = 7
    block_pairs = star_blocks * (star_blocks - 1) // 2
    endpoints_per_block = 2
    fiber_size = endpoints_per_block**2
    nonneighbors = block_pairs * fiber_size
    common_star_flags = 14 - 2
    local_leaf_cap = 3 * common_star_flags
    global_flag_cap = 99 * 13
    global_leaf_cap = 99 * local_leaf_cap

    assert block_pairs == 21
    assert fiber_size == 4
    assert nonneighbors == 84
    assert common_star_flags == 12
    assert local_leaf_cap == 36
    assert global_flag_cap == 1287
    assert global_leaf_cap == 3564

    return {
        "star_blocks": star_blocks,
        "two_block_types": block_pairs,
        "fiber_size": fiber_size,
        "partitioned_nonneighbors": nonneighbors,
        "common_star_flag_cap": common_star_flags,
        "universal_local_flag_cap": 13,
        "global_flag_cap": global_flag_cap,
        "universal_local_oriented_label_cap": local_leaf_cap,
        "global_oriented_label_cap_H": global_leaf_cap,
        "new_slack": "S36=H-C+n1+2*n2-a3-b3>=0",
        "hilton_milner_equality_templates": hilton_milner_templates(),
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
        "S36": vector(H=1, C=-1, n1=1, n2=2, a3=-1, b3=-1),
    }
    weights = {
        "SI": Fraction(2, 3),
        "S2": Fraction(4, 3),
        "SE2": Fraction(1, 6),
        "RA": Fraction(2, 3),
        "SL": Fraction(1, 3),
        "S36": Fraction(1, 6),
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
        "S36": (
            row["H"]
            - row["C"]
            + row["n1"]
            + 2 * row["n2"]
            - row["a3"]
            - row["b3"]
        ),
    }


def integer_null_row() -> dict[str, object]:
    row = vector(
        H=3564,
        C=4158,
        n2=297,
        n3=1287,
        p2=297,
        p3=3564,
        b1=594,
        c1=3564,
        r1=4158,
    )
    evaluation = evaluate_row(row)
    assert row["a1"] + row["a2"] + row["a3"] == row["n1"]
    assert row["b1"] + row["b3"] == 2 * row["p2"]
    assert row["c1"] + row["c2"] == row["p3"]
    assert row["a1"] + row["b1"] + row["c1"] == row["r1"]
    assert all(
        evaluation[name] == 0
        for name in ("SI", "S2", "SE2", "RA", "SL", "S36")
    )
    target = Fraction(11 * row["C"] - row["H"], 6)
    assert evaluation["Q0"] == target == 7029
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
    geometry = local_geometry()
    remainder = certificate_remainder()
    expected_remainder = vector(
        a1=Fraction(1, 6),
        b3=Fraction(1, 2),
        c2=Fraction(1, 6),
        W=Fraction(1, 3),
    )
    assert remainder == expected_remainder

    c = 4158
    h_constant = int(geometry["global_oriented_label_cap_H"])
    target = Fraction(11 * c - h_constant, 6)
    assert h_constant == 3564
    assert target == 7029
    edge_added = int(target) + 693
    scalar_words = 2 * edge_added
    assert edge_added == 7722
    assert scalar_words == 15444

    return {
        "local_geometry": geometry,
        "certificate": {
            "identity_target": "(11*C-H)/6",
            "slack_weights": {
                "SI": "2/3",
                "S2": "4/3",
                "SE2": "1/6",
                "RA": "2/3",
                "SL": "1/3",
                "S36": "1/6",
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
            "H": h_constant,
            "projective_nonedge_Q": int(target),
            "edge_added_projective": edge_added,
            "circuit_scalar_words": scalar_words,
        },
        "integer_null_control": integer_null_row(),
        "claim": {
            "local": "j_x<=36",
            "global": "J<=3564",
            "new_slack": "3564-C+n1+2*n2-a3-b3>=0",
            "bound": "Q>=7029",
        },
        "search_scope": (
            "two fixed Hilton-Milner equality templates, exact incidence "
            "identities, and rational coefficient algebra only; no graph, "
            "code, cover, SAT, LP, configuration, enumeration, or "
            "isomorphism search"
        ),
        "claim_label": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive()
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
        print("PASS: Wave196 proof-A exact result matches")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
