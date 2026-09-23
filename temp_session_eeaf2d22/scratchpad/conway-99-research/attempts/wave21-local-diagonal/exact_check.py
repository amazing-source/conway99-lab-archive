#!/usr/bin/env python3
"""Exact checks for the Wave 21 local-diagonal endpoint analysis.

This is a standard-library, exact-arithmetic checker.  It does not construct
an SRG and does not claim that the scalar relaxation witnesses below extend
to matrices.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


F = Fraction
TRIANGLES = 231
ENDPOINT_N3 = 705
SCHUR_ENDPOINT = 693
DELTA = ENDPOINT_N3 - SCHUR_ENDPOINT
M_VALUES = (-2, -1, 0, 1)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def ceiling(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def next_multiple(value: Fraction, modulus: int) -> int:
    return ((ceiling(value) + modulus - 1) // modulus) * modulus


def row_profile(q: int) -> dict[int, int]:
    require(0 <= q <= 12, "q outside 0..12")
    profile = {0: 20 + q, 1: 180 - 3 * q, 2: 3 * q, 3: 12 - q}
    require(sum(profile.values()) == 212, "wrong disjoint-row total")
    require(sum(r * profile[r] for r in range(4)) == 216, "wrong first moment")
    require(
        sum((r * (r - 1) // 2) * profile[r] for r in range(4)) == 36,
        "wrong second binomial moment",
    )
    return profile


def schur_cube_row_sum(q: int) -> int:
    profile = row_profile(q)
    return 4**3 + profile[0] - profile[2] - 2**3 * profile[3]


def harmonic_value(m: int) -> int:
    require(m in M_VALUES, "not an off-diagonal M value")
    return 23 * m**3 - 24 * m


def local_a4_rational_lower(q: int) -> Fraction:
    """Cauchy lower bound from the traceless anchored quadratic tensor."""

    require(0 <= q <= 12, "q outside 0..12")
    return F(99, 43) * (q - 2) ** 2


def local_a4_integral_lower(q: int) -> int:
    """Positive multiple-of-four refinement of local_a4_rational_lower."""

    rational_lower = local_a4_rational_lower(q)
    return max(4, next_multiple(rational_lower, 4))


def endpoint_scalar_profiles() -> list[dict[str, int]]:
    """Enumerate aggregate q-profiles surviving the scalar local inequalities.

    q>=9 is omitted by the endpoint local-diagonal budget.  q=2 fills all
    unused indices.  In particular, this enumeration does not import the
    separate q!=1 result from earlier waves.
    """

    costs = {
        q: (local_a4_integral_lower(q) - 4) // 4
        for q in (0, 3, 4, 5, 6, 7, 8)
    }
    profiles: list[dict[str, int]] = []
    for b0 in range(11):
        for b1 in range(TRIANGLES + 1):
            for b8 in range(2):
                for b7 in range(2):
                    for b6 in range(3):
                        for b5 in range(5):
                            for b4 in range(11):
                                high = {0: b0, 4: b4, 5: b5, 6: b6, 7: b7, 8: b8}
                                used_cost = sum(costs[q] * count for q, count in high.items())
                                if used_cost > 21:
                                    continue
                                positive_without_q3 = sum(
                                    (q - 2) * count
                                    for q, count in high.items()
                                    if q >= 4
                                )
                                b3 = 8 + 2 * b0 + b1 - positive_without_q3
                                if b3 < 0:
                                    continue
                                counts = {
                                    0: b0, 1: b1, 3: b3, 4: b4, 5: b5,
                                    6: b6, 7: b7, 8: b8,
                                }
                                non_q2 = sum(counts.values())
                                if non_q2 > TRIANGLES:
                                    continue
                                counts[2] = TRIANGLES - non_q2
                                require(sum(q * count for q, count in counts.items()) == 470,
                                        "endpoint q-sum changed")
                                minimum_excess = sum(
                                    ((local_a4_integral_lower(q) - 4) // 4) * count
                                    for q, count in counts.items()
                                )
                                if minimum_excess <= 21:
                                    rendered = {
                                        f"b{q}": counts.get(q, 0)
                                        for q in (0, 1, 2, 3, 4, 5, 6, 7, 8)
                                    }
                                    rendered["minimum_excess_units"] = minimum_excess
                                    profiles.append(rendered)
    return profiles


def endpoint_audit() -> dict[str, object]:
    require(DELTA == 12, "endpoint delta changed")
    require(F(2 * ENDPOINT_N3, 3) == 470, "endpoint q-sum changed")

    # K=M^{o3}: Schur positivity, diagonal 64, row sum 6(q-2),
    # and total all-ones mass 4*Delta.
    k_total = 4 * DELTA
    k_max_abs_deviation_squared = F(64 * k_total, 6**2)
    k_max_q = 2 + int(k_max_abs_deviation_squared**F(1, 2)) if False else 11
    require(9**2 <= k_max_abs_deviation_squared, "q=11 should survive K Cauchy")
    require(10**2 > k_max_abs_deviation_squared, "q=12 should fail K Cauchy")

    # Harmonic cubic tensors in dimension 44 and squared radius 4 have
    # kernel t^3-(24/23)t.  H=23*K-24*M is therefore PSD.
    harmonic_coefficient = F(3 * 4**2, 44 + 2)
    require(harmonic_coefficient == F(24, 23), "harmonic coefficient changed")
    h_diagonal = 23 * 4**3 - 24 * 4
    h_total = 23 * k_total
    require(h_diagonal == 1376, "harmonic diagonal changed")
    require(h_total == 92 * DELTA == 1104, "harmonic total changed")
    h_max_abs_deviation_squared = F(h_diagonal * h_total, 138**2)
    require(8**2 <= h_max_abs_deviation_squared, "q=10 should survive H Cauchy")
    require(9**2 > h_max_abs_deviation_squared, "q=11 should fail H Cauchy")

    # Center H by its all-ones direction.  For q=10 the residual diagonal is
    # 272, while every possible off-diagonal residual between two q=10
    # indices has absolute value at least 1103.
    q10_row_sum = 138 * 8
    q10_residual_diagonal = F(h_diagonal) - F(q10_row_sum**2, h_total)
    require(q10_residual_diagonal == 272, "q=10 centered diagonal changed")
    q10_residual_off_diagonals = {
        str(m): F(harmonic_value(m)) - F(q10_row_sum**2, h_total)
        for m in M_VALUES
    }
    require(
        min(abs(value) for value in q10_residual_off_diagonals.values()) == 1103,
        "q=10 residual off-diagonal gap changed",
    )
    require(
        all(value * value > q10_residual_diagonal**2
            for value in q10_residual_off_diagonals.values()),
        "two q=10 indices should violate every centered 2x2 minor",
    )

    # A4=M(M o M)M is the Gram matrix of
    # S_i=sum_j M_ij (u_j u_j^T).  S_i is traceless and
    # <S_i,u_i u_i^T-I/11>=6(q_i-2).  The anchored traceless tensor has
    # squared norm 16-16/44=172/11.
    anchored_traceless_norm = F(16) - F(16, 44)
    require(anchored_traceless_norm == F(172, 11), "traceless norm changed")
    local_table = []
    for q in range(13):
        require(schur_cube_row_sum(q) == 6 * (q - 2), "row cube changed")
        local_table.append({
            "q": q,
            "cube_row_sum": schur_cube_row_sum(q),
            "a4_rational_lower": str(local_a4_rational_lower(q)),
            "a4_integral_lower": local_a4_integral_lower(q),
            "excess_units_over_4": (local_a4_integral_lower(q) - 4) // 4,
        })

    trace_a4 = 84 * DELTA
    require(trace_a4 == 1008, "A4 endpoint trace changed")
    max_one_diagonal = trace_a4 - 4 * (TRIANGLES - 1)
    require(max_one_diagonal == 88, "single-diagonal budget changed")
    q_endpoint_max = max(
        q for q in range(13)
        if local_a4_rational_lower(q) <= max_one_diagonal
    )
    require(q_endpoint_max == 8, "combined local endpoint q bound changed")

    profiles = endpoint_scalar_profiles()
    require(profiles, "scalar endpoint relaxation became empty")
    simple_profile = {
        "b0": 0,
        "b1": 0,
        "b2": 223,
        "b3": 8,
        "b4": 0,
        "b5": 0,
        "b6": 0,
        "b7": 0,
        "b8": 0,
        "minimum_excess_units": 0,
    }
    require(simple_profile in profiles, "eight-q3 scalar survivor disappeared")

    # Frobenius arithmetic at the endpoint.
    odd_ordered_off_diagonals = (4620 + 470) + 2 * ENDPOINT_N3
    require(odd_ordered_off_diagonals == 6500, "odd-entry count changed")
    odd_unordered_off_diagonals = odd_ordered_off_diagonals // 2
    require(odd_unordered_off_diagonals == 3250, "unordered odd count changed")
    continuous_t_lower = F(trace_a4**2, 44 * 441)
    require(continuous_t_lower == F(576, 11), "rank trace-square bound changed")
    t_min = next(
        t for t in range(ceiling(continuous_t_lower), 100)
        if t % 8 == 4
    )
    require(t_min == 60, "Frobenius congruence endpoint changed")
    require(441 * t_min == 26460, "Frobenius lower bound changed")

    return {
        "schema_version": 1,
        "claim_label": "DERIVED",
        "scope": "conditional_endpoint_n3_705_local_relaxation",
        "target_status": "UNKNOWN",
        "novelty_status": "UNKNOWN",
        "endpoint": {
            "n3": ENDPOINT_N3,
            "delta": DELTA,
            "sum_q": 470,
            "trace_A4": trace_a4,
            "A4_diagonal_excess_units": 21,
        },
        "schur_cube_kernel": {
            "diagonal": 64,
            "row_sum": "6*(q-2)",
            "all_ones_mass": k_total,
            "cauchy_q_max": k_max_q,
        },
        "harmonic_cubic_kernel": {
            "formula": "H=23*(M hadamard-cubed)-24*M",
            "diagonal": h_diagonal,
            "row_sum": "138*(q-2)",
            "all_ones_mass": h_total,
            "cauchy_q_max": 10,
            "centered_q10_diagonal": str(q10_residual_diagonal),
            "centered_q10_off_diagonals": {
                key: str(value) for key, value in q10_residual_off_diagonals.items()
            },
            "q10_multiplicity_max": 1,
        },
        "local_A4": {
            "gram_tensor": "S_i=sum_j M_ij*(u_j tensor u_j)",
            "traceless_anchor_norm_squared": str(anchored_traceless_norm),
            "rational_lower": "(99/43)*(q-2)^2",
            "positive_diagonal_modulus": 4,
            "endpoint_max_single_diagonal": max_one_diagonal,
            "endpoint_q_max": q_endpoint_max,
            "table": local_table,
        },
        "scalar_relaxation": {
            "aggregate_profile_count": len(profiles),
            "simple_survivor": simple_profile,
            "simple_diagonal_distribution": {
                "diagonal_4_count": 210,
                "diagonal_8_count": 21,
                "trace": 1008,
            },
            "warning": "These are scalar witnesses, not matrix or graph constructions.",
        },
        "frobenius": {
            "odd_unordered_off_diagonal_count": odd_unordered_off_diagonals,
            "trace_A4_squared_is_441_t": True,
            "t_mod_8": 4,
            "rank_lower_for_t": str(continuous_t_lower),
            "minimum_t": t_min,
            "trace_A4_squared_lower": 441 * t_min,
            "spectral_relaxation_eigenvalues": "22 copies each of (252+21*sqrt(21))/11 and (252-21*sqrt(21))/11",
        },
        "conclusion": "INCONCLUSIVE_ENDPOINT_SURVIVES",
        "limitations": [
            "No matrix A4 realizing a scalar witness is constructed.",
            "No association scheme, automorphism, or triangle-graph catalog is assumed.",
            "The target and literature novelty remain UNKNOWN.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    rendered = json.dumps(endpoint_audit(), indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
