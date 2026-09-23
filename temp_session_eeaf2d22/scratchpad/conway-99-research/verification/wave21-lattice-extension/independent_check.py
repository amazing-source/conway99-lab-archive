#!/usr/bin/env python3
"""Independent exact checks for the Wave 21 lattice-extension audit.

This module imports no submitted Wave 21 code.  It checks the finite
arithmetic consequences separately and includes an elementary sharpening:
an even integral Gram matrix of rank 44 and odd determinant has determinant
1 modulo 4.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


RANK = 44
TRIANGLES = 231
ENDPOINT_DELTA = 12
ENDPOINT_N3 = 705


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil_to_four(value: Fraction) -> int:
    return 4 * (
        (value.numerator + 4 * value.denominator - 1)
        // (4 * value.denominator)
    )


def smooth_3_7(limit: int) -> list[int]:
    values: set[int] = set()
    a = 1
    while a <= limit:
        b = 1
        while a * b <= limit:
            values.add(a * b)
            b *= 7
        a *= 3
    return sorted(values)


def determinant_cap(delta: int) -> tuple[Fraction, int]:
    exact = Fraction(4 * delta, RANK) ** RANK
    return exact, floor_fraction(exact)


def endpoint_pairs(*, use_even_determinant_congruence: bool) -> list[tuple[int, int, int]]:
    _, cap = determinant_cap(ENDPOINT_DELTA)
    rows: list[tuple[int, int, int]] = []
    for h in smooth_3_7(cap):
        for det_q in range(3, cap // h + 1, 2):
            det_b = h * det_q
            if det_b % 4 != 1:
                continue
            if use_even_determinant_congruence and det_q % 4 != 1:
                continue
            rows.append((h, det_q, det_b))
    return rows


def even_odd_determinant_residue(rank: int) -> int:
    """Modulo-four determinant of an even Gram matrix with odd determinant.

    A nonsingular alternating matrix over F_2 admits an integral congruence
    reduction, modulo 4, to rank/2 blocks with odd off-diagonal entry.
    Each block has determinant 3 modulo 4.  Therefore the residue is
    (-1)^(rank/2) modulo 4.
    """
    require(rank > 0 and rank % 2 == 0, "rank must be positive and even")
    return pow(3, rank // 2, 4)


def determinant(matrix: list[list[int]]) -> int:
    """Bareiss exact determinant, used only by independent hostile tests."""
    n = len(matrix)
    require(n > 0 and all(len(row) == n for row in matrix), "matrix must be square")
    work = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for pivot_index in range(n - 1):
        if work[pivot_index][pivot_index] == 0:
            swap = next(
                (
                    row_index
                    for row_index in range(pivot_index + 1, n)
                    if work[row_index][pivot_index] != 0
                ),
                None,
            )
            if swap is None:
                return 0
            work[pivot_index], work[swap] = work[swap], work[pivot_index]
            sign *= -1
        pivot = work[pivot_index][pivot_index]
        for row_index in range(pivot_index + 1, n):
            for column_index in range(pivot_index + 1, n):
                numerator = (
                    work[row_index][column_index] * pivot
                    - work[row_index][pivot_index]
                    * work[pivot_index][column_index]
                )
                require(
                    numerator % previous == 0,
                    "Bareiss exact division failed",
                )
                work[row_index][column_index] = numerator // previous
        previous = pivot
    return sign * work[-1][-1]


def rank_one_projection_index(vector: tuple[int, ...], scale: int) -> dict[str, int]:
    """Check the index direction for a primitive rational line.

    For L=Z*v with primitive v and d=<v,v>, E Z^n=L*=(1/d)Z*v.
    If d divides scale, then scale*E is integral and
    [L:scale*L*]=scale/d.
    """
    from math import gcd

    coordinate_gcd = 0
    for coordinate in vector:
        coordinate_gcd = gcd(coordinate_gcd, abs(coordinate))
    require(coordinate_gcd == 1, "vector must be primitive")
    gram_determinant = sum(coordinate * coordinate for coordinate in vector)
    require(scale % gram_determinant == 0, "scale must be divisible by the norm")
    index = scale // gram_determinant
    return {
        "rank": 1,
        "gram_determinant": gram_determinant,
        "scale": scale,
        "index_direct": index,
        "index_formula": scale // gram_determinant,
    }


def harmonic_entries() -> dict[int, int]:
    return {m: 23 * m**3 - 24 * m for m in (4, 1, 0, -1, -2)}


def row_counts(q: int) -> tuple[int, int, int, int]:
    require(0 <= q <= 12, "q outside the audited range")
    return (20 + q, 180 - 3 * q, 3 * q, 12 - q)


def harmonic_row_sum(q: int) -> int:
    a0, _, a2, a3 = row_counts(q)
    values = harmonic_entries()
    return values[4] + a0 * values[1] + a2 * values[-1] + a3 * values[-2]


def harmonic_endpoint() -> dict[str, object]:
    total = 92 * ENDPOINT_DELTA
    diagonal = harmonic_entries()[4]
    allowed: list[int] = []
    rejected: list[int] = []
    for q in range(13):
        destination = allowed if harmonic_row_sum(q) ** 2 <= diagonal * total else rejected
        destination.append(q)
    return {
        "entries": {str(key): value for key, value in harmonic_entries().items()},
        "total_sum": total,
        "allowed_q": allowed,
        "rejected_q": rejected,
    }


def contraction_bound(q: int) -> Fraction:
    require(0 <= q <= 12, "q outside the audited range")
    return Fraction(99 * (q - 2) ** 2, 43)


def contraction_floor(q: int) -> int:
    return max(4, ceil_to_four(contraction_bound(q)))


def minimum_profile_cost(
    triangle_count: int,
    q_sum: int,
    *,
    forbid_q_one: bool,
) -> tuple[int, dict[int, int]]:
    """Independent DP returning both minimum cost and one witness profile."""
    infinity = 10**30
    prior: dict[int, tuple[int, dict[int, int]]] = {0: (0, {})}
    for _ in range(triangle_count):
        current: dict[int, tuple[int, dict[int, int]]] = {}
        for partial_sum, (partial_cost, profile) in prior.items():
            for q in range(13):
                if forbid_q_one and q == 1:
                    continue
                target = partial_sum + q
                if target > q_sum:
                    continue
                cost = partial_cost + contraction_floor(q)
                incumbent = current.get(target, (infinity, {}))[0]
                if cost < incumbent:
                    next_profile = dict(profile)
                    next_profile[q] = next_profile.get(q, 0) + 1
                    current[target] = (cost, next_profile)
        prior = current
    require(q_sum in prior, "requested q sum is unreachable")
    return prior[q_sum]


def audit() -> dict[str, object]:
    exact_cap, integer_cap = determinant_cap(ENDPOINT_DELTA)
    require(Fraction(45) < exact_cap < Fraction(46), "endpoint AM-GM interval changed")
    require(integer_cap == 45, "endpoint determinant cap changed")

    submitted_pairs = endpoint_pairs(use_even_determinant_congruence=False)
    submitted_h = sorted({h for h, _, _ in submitted_pairs})
    require(submitted_h == [1, 3, 7, 9], "submitted-constraint h list changed")

    strengthened_pairs = endpoint_pairs(use_even_determinant_congruence=True)
    strengthened_h = sorted({h for h, _, _ in strengthened_pairs})
    require(
        even_odd_determinant_residue(RANK) == 1,
        "rank-44 even determinant residue changed",
    )
    require(strengthened_h == [1, 9], "strengthened h list changed")

    harmonic = harmonic_endpoint()
    require(harmonic["rejected_q"] == [11, 12], "harmonic rejection changed")
    for q in range(13):
        require(harmonic_row_sum(q) == 138 * (q - 2), "harmonic row formula changed")

    q_sum = 2 * ENDPOINT_N3 // 3
    minimum, profile = minimum_profile_cost(
        TRIANGLES,
        q_sum,
        forbid_q_one=True,
    )
    minimum_with_q_one, _ = minimum_profile_cost(
        TRIANGLES,
        q_sum,
        forbid_q_one=False,
    )
    require(minimum == 924, "contraction DP minimum changed")
    require(minimum_with_q_one == 924, "q=1 hostile mutation changed the minimum")
    require(sum(profile.values()) == TRIANGLES, "profile cardinality changed")
    require(sum(q * count for q, count in profile.items()) == q_sum, "profile sum changed")

    projection_sanity = [
        rank_one_projection_index((1, 1), 2),
        rank_one_projection_index((1, 2), 10),
    ]
    require(
        [row["index_direct"] for row in projection_sanity] == [1, 2],
        "projection-lattice index direction changed",
    )

    return {
        "audit_label": "VERIFIED_SCOPED_WITH_NONBLOCKING_STRENGTHENING",
        "scope": "Wave 21 lattice-extension arithmetic and finite endpoint claims",
        "endpoint": {
            "n3": ENDPOINT_N3,
            "delta": ENDPOINT_DELTA,
            "trace_B": 48,
            "am_gm_exact": {
                "numerator": exact_cap.numerator,
                "denominator": exact_cap.denominator,
            },
            "determinant_cap": integer_cap,
        },
        "projection_index_sanity": projection_sanity,
        "submitted_constraints": {
            "possible_h": submitted_h,
            "pairs": [
                {"h": h, "det_Q": det_q, "det_B": det_b}
                for h, det_q, det_b in submitted_pairs
            ],
        },
        "additional_even_determinant_congruence": {
            "rank": RANK,
            "det_Q_mod_4": even_odd_determinant_residue(RANK),
            "possible_h": strengthened_h,
            "pairs": [
                {"h": h, "det_Q": det_q, "det_B": det_b}
                for h, det_q, det_b in strengthened_pairs
            ],
            "consequence": "n3=705 forces h in {1,9}; h remains undetermined",
        },
        "harmonic_cubic": harmonic,
        "traceless_contraction": {
            "floors": {str(q): contraction_floor(q) for q in range(13)},
            "q_sum": q_sum,
            "minimum": minimum,
            "witness_profile": {str(q): count for q, count in sorted(profile.items())},
            "minimum_if_q_one_allowed": minimum_with_q_one,
            "available_trace": 84 * ENDPOINT_DELTA,
            "result": "NO_CONTRADICTION",
        },
        "boundary": {
            "unconditional_improvement": False,
            "index_h_determined": False,
            "target_status": "NOT_ASSESSED",
            "novelty_status": "NOT_ASSESSED",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    rendered = json.dumps(audit(), indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
