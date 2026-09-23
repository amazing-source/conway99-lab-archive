#!/usr/bin/env python3
"""Exact arithmetic checks for the Wave 21 lattice-extension checkpoint.

This script does not instantiate a putative Conway graph.  It checks only the
integer arithmetic consequences of the independently derived lattice lemmas in
agents/2026-07-23-wave21-lattice-extension.md.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


RANK = 44
TRIANGLES = 231
BASELINE_N3 = 693


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def determinant_cap(delta: int) -> int:
    """AM--GM cap for det(B), where rank(B)=44 and tr(B)=4*delta."""
    numerator = (4 * delta) ** RANK
    denominator = RANK**RANK
    return numerator // denominator


def smooth_indices(limit: int) -> list[int]:
    """All positive 3,7-smooth integers at most limit."""
    values: set[int] = set()
    power3 = 1
    while power3 <= limit:
        power7 = 1
        while power3 * power7 <= limit:
            values.add(power3 * power7)
            power7 *= 7
        power3 *= 3
    return sorted(values)


def endpoint_index_options(
    delta: int,
    *,
    even_lattice_determinant_floor: int = 3,
) -> dict[str, object]:
    """Enumerate index/determinant possibilities at one endpoint.

    The exact lattice reduction gives

        det(B) = h * det(Q),

    where h=[L:21L*] is 3,7-smooth, Q is an even positive-definite integral
    rank-44 Gram matrix, det(Q) is odd, and det(B)=1 (mod 4).

    The classical even-unimodular signature obstruction rules out det(Q)=1
    in positive-definite rank 44, so the operative floor is 3.  Passing a
    floor of 1 exposes the weaker arithmetic before that theorem is used.
    """
    require(delta > 0, "delta must be positive")
    require(
        even_lattice_determinant_floor >= 1
        and even_lattice_determinant_floor % 2 == 1,
        "the determinant floor must be a positive odd integer",
    )
    cap = determinant_cap(delta)
    options: list[dict[str, int]] = []
    for h in smooth_indices(cap):
        for det_q in range(even_lattice_determinant_floor, cap // h + 1, 2):
            det_b = h * det_q
            if det_b % 4 == 1:
                options.append({"h": h, "det_q": det_q, "det_b": det_b})
    return {
        "delta": delta,
        "trace_b": 4 * delta,
        "determinant_cap": cap,
        "even_lattice_determinant_floor": even_lattice_determinant_floor,
        "options": options,
        "possible_h": sorted({row["h"] for row in options}),
    }


def harmonic_cubic_data(delta: int) -> dict[str, object]:
    """Check H=23*M^{o3}-24*M and its endpoint Cauchy consequence."""
    values = {
        str(m): 23 * m**3 - 24 * m
        for m in (4, 1, 0, -1, -2)
    }
    require(
        values == {"4": 1376, "1": -1, "0": 0, "-1": 1, "-2": -136},
        "harmonic-kernel entry values changed",
    )
    total_norm = 92 * delta
    allowed_q: list[int] = []
    rejected_q: list[int] = []
    for q in range(13):
        row_sum = 138 * (q - 2)
        if row_sum**2 <= values["4"] * total_norm:
            allowed_q.append(q)
        else:
            rejected_q.append(q)
    return {
        "kernel": "23*M_hadamard_3-24*M",
        "entries": values,
        "row_sum": "138*(q-2)",
        "total_sum": f"92*delta={total_norm}",
        "cauchy_allowed_q": allowed_q,
        "cauchy_rejected_q": rejected_q,
    }


def ceil_multiple_of_four(value: Fraction) -> int:
    return 4 * (
        (value.numerator + 4 * value.denominator - 1)
        // (4 * value.denominator)
    )


def contraction_floor(q: int) -> int:
    """Local floor from traceless contraction plus mod-four positivity."""
    require(0 <= q <= 12, "q outside the audited row-profile range")
    traceless_bound = Fraction(99 * (q - 2) ** 2, 43)
    return max(4, ceil_multiple_of_four(traceless_bound))


def minimum_contraction_trace(
    triangle_count: int,
    q_sum: int,
    *,
    forbid_q_one: bool = True,
) -> int:
    """Exact dynamic program over q profiles; used to document non-improvement."""
    infinity = 10**18
    row = [infinity] * (q_sum + 1)
    row[0] = 0
    for _ in range(triangle_count):
        nxt = [infinity] * (q_sum + 1)
        for partial_sum, partial_cost in enumerate(row):
            if partial_cost == infinity:
                continue
            for q in range(13):
                if forbid_q_one and q == 1:
                    continue
                target = partial_sum + q
                if target <= q_sum:
                    nxt[target] = min(
                        nxt[target],
                        partial_cost + contraction_floor(q),
                    )
        row = nxt
    require(row[q_sum] != infinity, "no q profile reached the requested sum")
    return row[q_sum]


def audit() -> dict[str, object]:
    delta = 12
    n3 = BASELINE_N3 + delta
    require(n3 == 705, "endpoint arithmetic changed")
    require(n3 % 3 == 0, "endpoint lost the audited divisibility")

    weak_options = endpoint_index_options(
        delta, even_lattice_determinant_floor=1
    )
    strong_options = endpoint_index_options(
        delta, even_lattice_determinant_floor=3
    )
    require(
        weak_options["determinant_cap"] == 45,
        "AM--GM determinant cap changed",
    )
    require(
        weak_options["possible_h"] == [1, 3, 7, 9, 21],
        "weak endpoint index list changed",
    )
    require(
        strong_options["possible_h"] == [1, 3, 7, 9],
        "even-lattice endpoint index list changed",
    )

    harmonic = harmonic_cubic_data(delta)
    require(
        harmonic["cauchy_rejected_q"] == [11, 12],
        "harmonic endpoint rejection set changed",
    )

    q_sum = 2 * n3 // 3
    require(q_sum == 470, "endpoint q sum changed")
    local_floors = {str(q): contraction_floor(q) for q in range(13)}
    minimum_trace = minimum_contraction_trace(TRIANGLES, q_sum)
    require(
        minimum_trace == 4 * TRIANGLES == 924,
        "local contraction optimization changed",
    )
    actual_trace = 84 * delta
    require(actual_trace == 1008, "Wave 20 trace identity changed")
    require(
        minimum_trace < actual_trace,
        "the retained local route unexpectedly became a contradiction",
    )

    return {
        "claim_label": "UNKNOWN",
        "scope": "stronger-than-705 conditional lattice obstruction",
        "endpoint": {
            "n3": n3,
            "delta": delta,
            "q_sum": q_sum,
            "trace_A": actual_trace,
            "trace_B": 4 * delta,
        },
        "projection_lattice": {
            "rank": RANK,
            "h_definition": "[L:21L*]=21^44/det(L)",
            "determinant_identity": "det(B)=h*det(Q)",
            "B_mod_2": "identity",
            "det_B_mod_4": 1,
            "Q": "even positive-definite integral rank-44 Gram matrix",
        },
        "endpoint_without_even_unimodular_obstruction": weak_options,
        "endpoint_with_even_unimodular_obstruction": strong_options,
        "conditional_implication": (
            "if h>=21, then n3=705 is impossible; "
            "the audited data do not determine h"
        ),
        "harmonic_cubic": harmonic,
        "traceless_contraction": {
            "local_floors": local_floors,
            "minimum_total_at_q_sum_470": minimum_trace,
            "available_trace": actual_trace,
            "result": "NO_CONTRADICTION",
        },
        "strongest_conclusion": (
            "No unconditional improvement over n3>=705 was obtained."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
