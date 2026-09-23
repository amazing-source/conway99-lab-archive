"""Exact rational scout for the Wave134 symmetrized Z4 enumerator.

The codeword type is (n0, nodd, n2).  Translation by the full-support
order-two word identifies (n0, nodd, n2) with (n2, nodd, n0).  Both residue
codes are even, so only even ``nodd`` shells need to be represented.

The script uses exact Z3 rational arithmetic.  It never materializes the
5,050 by 5,050 transform: after the two forced symmetries there are 1,119
primal orbit variables, and each transform row is generated from two
univariate Krawtchouk factors.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb
from pathlib import Path

from z3 import Real, Solver, Sum, sat


N = 99
LOG2_C_ORDER = 109
LOG2_D_ORDER = 89
ORBIT_TOTAL = 1 << (LOG2_C_ORDER - 1)
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "rational-witness.json"


def encode(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def decode(value) -> Fraction:
    return Fraction(value.numerator_as_long(), value.denominator_as_long())


@lru_cache(maxsize=None)
def kraw(degree: int, negative: int, length: int) -> int:
    """Coefficient of t^degree in (1+t)^(length-negative)(1-t)^negative."""
    if degree < 0 or degree > length:
        return 0
    return sum(
        (-1) ** overlap
        * comb(negative, overlap)
        * comb(length - negative, degree - overlap)
        for overlap in range(
            max(0, degree - (length - negative)),
            min(negative, degree) + 1,
        )
    )


def representative(state: tuple[int, int, int]) -> tuple[int, int, int]:
    a, b, c = state
    return (max(a, c), b, min(a, c))


def primal_residue_weights() -> list[int]:
    return [0] + list(range(8, 94, 2))


def dual_residue_weights() -> list[int]:
    return [0] + list(range(8, 92, 2))


def primal_orbit_states() -> list[tuple[int, int, int]]:
    result = []
    for b in primal_residue_weights():
        remaining = N - b
        for c in range((remaining + 1) // 2):
            a = remaining - c
            if b == 0 and 1 <= c <= 6:
                # Tor(C)=R+<1>.  The verified R bound wt<=92 excludes
                # torsion weights 1..6, while weight 7 remains possible.
                continue
            result.append((a, b, c))
    return result


def dual_orbit_states() -> list[tuple[int, int, int]]:
    result = []
    for b in dual_residue_weights():
        remaining = N - b
        for c in range((remaining + 1) // 2):
            a = remaining - c
            if b == 0 and 1 <= c <= 7:
                # Tor(Cperp)=Rperp has verified minimum distance eight
                # and complement symmetry.
                continue
            result.append((a, b, c))
    return result


def forbidden_dual_states() -> list[tuple[int, int, int]]:
    result = []
    for b in (2, 4, 6, 92, 94, 96, 98):
        remaining = N - b
        for c in range((remaining + 1) // 2):
            result.append((remaining - c, b, c))
    for c in range(1, 8):
        result.append((N - c, 0, c))
    return result


def add_symmetric(
    table: dict[tuple[int, int, int], int],
    state: tuple[int, int, int],
    count: int,
) -> None:
    rep = representative(state)
    table[rep] += count


TRIPLE_TYPES = (
    (70686, 0, 0, (2, 2, 2)),
    (27720, 0, 1, (2, 2, 2)),
    (41580, 1, 0, (1, 2, 2)),
    (8316, 1, 1, (1, 2, 2)),
    (8316, 2, 0, (1, 1, 2)),
    (231, 3, 0, (1, 1, 1)),
)


def membership_counts(
    weights: tuple[int, ...],
    pair_intersections: tuple[int, ...] = (),
    triple_intersection: int = 0,
) -> dict[int, int]:
    """Counts of coordinate membership masks for up to three rows."""
    size = len(weights)
    if size == 0:
        return {0: N}
    if size == 1:
        return {0: N - weights[0], 1: weights[0]}
    if size == 2:
        common = pair_intersections[0]
        return {
            0: N - weights[0] - weights[1] + common,
            1: weights[0] - common,
            2: weights[1] - common,
            3: common,
        }
    p12, p13, p23 = pair_intersections
    common = triple_intersection
    result = {
        7: common,
        3: p12 - common,
        5: p13 - common,
        6: p23 - common,
        1: weights[0] - p12 - p13 + common,
        2: weights[1] - p12 - p23 + common,
        4: weights[2] - p13 - p23 + common,
    }
    result[0] = N - sum(result.values())
    return result


def composition(
    masks: dict[int, int],
    coefficients: tuple[int, ...],
) -> tuple[int, int, int]:
    symbols = [0, 0, 0, 0]
    for mask, count in masks.items():
        symbol = sum(
            coefficient
            for index, coefficient in enumerate(coefficients)
            if mask & (1 << index)
        ) % 4
        symbols[symbol] += count
    return symbols[0], symbols[1] + symbols[3], symbols[2]


def forced_primal() -> dict[tuple[int, int, int], int]:
    """All nonzero Z4 coefficient patterns on row supports through size 3."""
    result: dict[tuple[int, int, int], int] = defaultdict(int)
    add_symmetric(result, (99, 0, 0), 1)
    one_masks = membership_counts((14,))
    for coefficients in product((1, 2, 3), repeat=1):
        add_symmetric(
            result,
            composition(one_masks, coefficients),
            99,
        )
    for support_count, intersection in ((693, 1), (4158, 2)):
        masks = membership_counts((14, 14), (intersection,))
        for coefficients in product((1, 2, 3), repeat=2):
            add_symmetric(
                result,
                composition(masks, coefficients),
                support_count,
            )
    for support_count, _edges, common, intersections in TRIPLE_TYPES:
        masks = membership_counts((14, 14, 14), intersections, common)
        for coefficients in product((1, 2, 3), repeat=3):
            add_symmetric(
                result,
                composition(masks, coefficients),
                support_count,
            )
    return dict(result)


def forced_dual() -> dict[tuple[int, int, int], int]:
    """All even-sum coefficient patterns on closed-row supports <=3."""
    result: dict[tuple[int, int, int], int] = defaultdict(int)
    add_symmetric(result, (99, 0, 0), 1)
    one_masks = membership_counts((15,))
    for coefficients in product((1, 2, 3), repeat=1):
        if sum(coefficients) % 2 == 0:
            add_symmetric(
                result,
                composition(one_masks, coefficients),
                99,
            )
    for support_count, intersection in ((693, 3), (4158, 2)):
        masks = membership_counts((15, 15), (intersection,))
        for coefficients in product((1, 2, 3), repeat=2):
            if sum(coefficients) % 2 == 0:
                add_symmetric(
                    result,
                    composition(masks, coefficients),
                    support_count,
                )
    internal_universal = {0: 0, 1: 0, 2: 1, 3: 3}
    for support_count, edges, common, intersections in TRIPLE_TYPES:
        closed_pairs = tuple(3 if value == 1 else 2 for value in intersections)
        closed_triple = common + internal_universal[edges]
        masks = membership_counts(
            (15, 15, 15),
            closed_pairs,
            closed_triple,
        )
        for coefficients in product((1, 2, 3), repeat=3):
            if sum(coefficients) % 2 == 0:
                add_symmetric(
                    result,
                    composition(masks, coefficients),
                    support_count,
                )
    return dict(result)


def transform_coefficient(
    source: tuple[int, int, int],
    target: tuple[int, int, int],
) -> int:
    """Coefficient for one source state before dividing by |C|.

    For source (a,b,c), the transformed monomial is

      (x+2y+z)^a (x-z)^b (x-2y+z)^c.

    The coefficient factors into a ``y`` Krawtchouk coefficient and an
    ``x,z`` Krawtchouk coefficient.
    """
    source_a, source_b, source_c = source
    _, target_b, target_c = target
    odd_factor = kraw(
        target_b,
        source_c,
        source_a + source_c,
    )
    xz_factor = kraw(
        target_c,
        source_b,
        N - target_b,
    )
    return (1 << target_b) * odd_factor * xz_factor


def discover(timeout_ms: int) -> dict:
    primal_states = primal_orbit_states()
    dual_states = dual_orbit_states()
    primal_lower = forced_primal()
    dual_lower = forced_dual()
    if not set(primal_lower).issubset(primal_states):
        raise AssertionError("a forced primal state was excluded")
    if not set(dual_lower).issubset(dual_states):
        raise AssertionError("a forced dual state was excluded")

    variables = {
        state: Real(f"A_{state[0]}_{state[1]}_{state[2]}")
        for state in primal_states
    }
    solver = Solver()
    solver.set(timeout=timeout_ms)
    for state in primal_states:
        solver.add(variables[state] >= primal_lower.get(state, 0))
    solver.add(variables[(99, 0, 0)] == 1)
    solver.add(
        Sum([variables[state] for state in primal_states]) == ORBIT_TOTAL
    )

    print(
        f"building exact system: variables={len(primal_states)} "
        f"allowed_dual_rows={len(dual_states)} "
        f"forbidden_dual_rows={len(forbidden_dual_states())}",
        flush=True,
    )
    transform_rows: dict[tuple[int, int, int], list[int]] = {}
    for target in dual_states:
        coefficients = [
            transform_coefficient(source, target)
            for source in primal_states
        ]
        transform_rows[target] = coefficients
        expression = Sum(
            [
                coefficient * variables[source]
                for source, coefficient in zip(
                    primal_states, coefficients
                )
                if coefficient
            ]
        )
        solver.add(
            expression
            >= dual_lower.get(target, 0) * ORBIT_TOTAL
        )

    for target in forbidden_dual_states():
        coefficients = [
            transform_coefficient(source, target)
            for source in primal_states
        ]
        expression = Sum(
            [
                coefficient * variables[source]
                for source, coefficient in zip(
                    primal_states, coefficients
                )
                if coefficient
            ]
        )
        solver.add(expression == 0)

    print("starting exact rational solve", flush=True)
    status = solver.check()
    if status != sat:
        raise SystemExit(f"Wave134 rational scout returned {status}")
    model = solver.model()
    primal = {
        state: decode(model.eval(variables[state], model_completion=True))
        for state in primal_states
    }
    dual = {}
    for target, coefficients in transform_rows.items():
        numerator = sum(
            Fraction(coefficient) * primal[source]
            for source, coefficient in zip(
                primal_states, coefficients
            )
        )
        dual[target] = numerator / ORBIT_TOTAL

    if any(value < 0 for value in primal.values()):
        raise AssertionError("negative primal coefficient")
    if any(value < 0 for value in dual.values()):
        raise AssertionError("negative dual coefficient")

    return {
        "format": "wave134-z4-symmetrized-rational-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Full three-variable symmetrized Z4 MacWilliams relaxation "
            "with exact graph-forced words through triples."
        ),
        "parameters": {
            "length": N,
            "C_type": "4^54 2^1",
            "C_order": str(1 << LOG2_C_ORDER),
            "Cperp_type": "4^44 2^1",
            "Cperp_order": str(1 << LOG2_D_ORDER),
            "raw_state_count": comb(N + 2, 2),
            "primal_orbit_variable_count": len(primal_states),
            "allowed_dual_orbit_count": len(dual_states),
            "forbidden_dual_orbit_count": len(forbidden_dual_states()),
        },
        "primal_orbits": {
            f"{a},{b},{c}": encode(value)
            for (a, b, c), value in primal.items()
            if value
        },
        "dual_orbits": {
            f"{a},{b},{c}": encode(value)
            for (a, b, c), value in dual.items()
            if value
        },
        "forced_primal_lower": {
            f"{a},{b},{c}": str(value)
            for (a, b, c), value in sorted(primal_lower.items())
        },
        "forced_dual_lower": {
            f"{a},{b},{c}": str(value)
            for (a, b, c), value in sorted(dual_lower.items())
        },
        "limitations": [
            "The witness is a formal exact rational symmetrized enumerator.",
            "It does not realize a Z4 code, adjacency matrix, or graph.",
            "It does not retain labelled-word compatibility beyond the forced aggregate counts.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout-ms", type=int, default=300000)
    args = parser.parse_args()
    result = discover(args.timeout_ms)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
