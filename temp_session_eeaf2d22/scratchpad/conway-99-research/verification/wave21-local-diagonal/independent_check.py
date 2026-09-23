#!/usr/bin/env python3
"""Independent exact checks for the Wave 21 local-diagonal relaxation.

This file deliberately does not import any submitted Wave 21 module.  It
starts from the audited Wave 20 matrix data

    M >= 0, M^2 = 21 M, M 1 = 0, diag(M) = 4,

and the exact row profile indexed by q.  All non-integral arithmetic uses
fractions.Fraction.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, Tuple


N = 231
DIM = 44
SCALE = 21
M_DIAGONAL = 4
ENDPOINT_N3 = 705
BASE_N3 = 693
DELTA = ENDPOINT_N3 - BASE_N3
SUM_Q = 2 * ENDPOINT_N3 // 3
TRACE_A4 = 84 * DELTA


def ceil_fraction(x: Fraction) -> int:
    return -(-x.numerator // x.denominator)


def row_profile(q: int) -> Dict[int, int]:
    """Counts of disjoint rows having r cross-edges, for a fixed triangle."""
    if not 0 <= q <= 12:
        raise ValueError("q must be in 0..12")
    return {0: 20 + q, 1: 180 - 3 * q, 2: 3 * q, 3: 12 - q}


def m_entry_for_r(r: int) -> int:
    return 1 - r


def row_moment(q: int, power: int) -> int:
    """Full ordered row moment, including the diagonal and zero categories."""
    profile = row_profile(q)
    return M_DIAGONAL**power + sum(
        count * m_entry_for_r(r) ** power for r, count in profile.items()
    )


def traceless_tensor_norm_squared() -> Fraction:
    """||x*x - (||x||^2/DIM) I||_F^2 for ||x||^2=4."""
    radius_squared = Fraction(M_DIAGONAL)
    return radius_squared**2 * Fraction(DIM - 1, DIM)


def tensor_coefficient(q: int) -> int:
    """Inner product of the tensor row with the traceless test tensor."""
    # The tensor row has zero trace because all frame vectors have norm 4
    # and M 1=0, so the identity component drops out.
    return row_moment(q, 3)


def tensor_diagonal_lower(q: int) -> Fraction:
    coefficient = Fraction(tensor_coefficient(q))
    return coefficient**2 / traceless_tensor_norm_squared()


def minimum_diagonal_units(q: int) -> int:
    """Minimum A4_TT/4 from positivity, mod four, and the tensor bound."""
    return max(1, ceil_fraction(tensor_diagonal_lower(q) / 4))


def endpoint_diagonal_cap() -> int:
    """One diagonal after the other 230 positive mod-four diagonals."""
    return TRACE_A4 - 4 * (N - 1)


def endpoint_tensor_allowed_q() -> Tuple[int, ...]:
    cap = endpoint_diagonal_cap()
    return tuple(q for q in range(13) if tensor_diagonal_lower(q) <= cap)


def harmonic_kernel(m: int) -> int:
    """23 times the degree-three harmonic Gram kernel."""
    return 23 * m**3 - 24 * m


def harmonic_constants(q: int, delta: int = DELTA) -> Dict[str, Fraction]:
    # For d=44 and ||x||^2=4, the trace subtraction is
    # 3*||x||^4/(d+2)=48/46=24/23.
    subtraction = Fraction(3 * M_DIAGONAL**2, DIM + 2)
    diagonal = harmonic_kernel(M_DIAGONAL)
    row_sum = 23 * row_moment(q, 3) - 24 * row_moment(q, 1)
    total_sum = 92 * delta
    return {
        "unscaled_trace_subtraction": subtraction,
        "diagonal": Fraction(diagonal),
        "row_sum": Fraction(row_sum),
        "total_sum": Fraction(total_sum),
    }


def centered_harmonic_diagonal(q: int, delta: int = DELTA) -> Fraction:
    constants = harmonic_constants(q, delta)
    total = constants["total_sum"]
    if total <= 0:
        raise ValueError("centering requires a positive all-ones norm")
    return constants["diagonal"] - constants["row_sum"] ** 2 / total


def centered_harmonic_off_diagonal(
    q_left: int, q_right: int, m: int, delta: int = DELTA
) -> Fraction:
    left = harmonic_constants(q_left, delta)
    right = harmonic_constants(q_right, delta)
    total = left["total_sum"]
    return Fraction(harmonic_kernel(m)) - left["row_sum"] * right["row_sum"] / total


def centered_minor_determinant(
    q_left: int, q_right: int, m: int, delta: int = DELTA
) -> Fraction:
    return (
        centered_harmonic_diagonal(q_left, delta)
        * centered_harmonic_diagonal(q_right, delta)
        - centered_harmonic_off_diagonal(q_left, q_right, m, delta) ** 2
    )


def odd_entry_counts_at_endpoint() -> Dict[str, int]:
    # The diagonal of M is even.  Every row has a0+a2=20+4q odd
    # off-diagonal entries.  The row sum counts ordered pairs.
    ordered = N * 20 + 4 * SUM_Q
    assert ordered % 2 == 0
    return {"ordered": ordered, "unordered": ordered // 2}


def trace_square_constants() -> Dict[str, object]:
    # If t=tr(M W M W), cyclicity and M^2=21M give
    # tr((M W M)^2)=21^2 t.
    factor = SCALE**2
    rank_trace_bound = Fraction(TRACE_A4**2, DIM * factor)
    raw_integer_bound = ceil_fraction(rank_trace_bound)

    odd = odd_entry_counts_at_endpoint()
    trace_square_mod_8 = (2 * odd["unordered"]) % 8
    # 441 is 1 modulo 8, so t has the same residue.
    t_mod_8 = trace_square_mod_8
    t_minimum = raw_integer_bound
    while t_minimum % 8 != t_mod_8:
        t_minimum += 1
    return {
        "factor": factor,
        "rank_trace_bound": rank_trace_bound,
        "raw_integer_bound": raw_integer_bound,
        "trace_square_mod_8": trace_square_mod_8,
        "t_mod_8": t_mod_8,
        "t_minimum": t_minimum,
        "trace_square_minimum": factor * t_minimum,
    }


def count_scalar_profiles(allow_q_one: bool = True) -> int:
    """Count aggregate q profiles passing the local diagonal budget.

    At n3=705, relative to 231 rows of q=2, the q-sum excess is 8.
    Only q=0,4,5,6,7,8 consume extra diagonal units.  Enumerating those
    bounded variables first makes this exhaustive count very small.
    """
    extra = {q: minimum_diagonal_units(q) - 1 for q in range(9)}
    total = 0
    for c8 in range(21 // extra[8] + 1):
        b8 = c8 * extra[8]
        for c7 in range((21 - b8) // extra[7] + 1):
            b7 = b8 + c7 * extra[7]
            for c6 in range((21 - b7) // extra[6] + 1):
                b6 = b7 + c6 * extra[6]
                for c5 in range((21 - b6) // extra[5] + 1):
                    b5 = b6 + c5 * extra[5]
                    for c4 in range((21 - b5) // extra[4] + 1):
                        b4 = b5 + c4 * extra[4]
                        for c0 in range((21 - b4) // extra[0] + 1):
                            high_excess = (
                                2 * c4 + 3 * c5 + 4 * c6 + 5 * c7 + 6 * c8
                            )
                            c1_values: Iterable[int]
                            c1_values = range(N + 1) if allow_q_one else (0,)
                            for c1 in c1_values:
                                c3 = 8 + 2 * c0 + c1 - high_excess
                                if c3 < 0:
                                    continue
                                c2 = N - (
                                    c0 + c1 + c3 + c4 + c5 + c6 + c7 + c8
                                )
                                if c2 >= 0:
                                    total += 1
    return total


def scalar_survivor() -> Dict[str, object]:
    """An aggregate witness only; it is not a graph or a matrix certificate."""
    profile = {q: 0 for q in range(9)}
    profile[2] = 223
    profile[3] = 8
    assert sum(profile.values()) == N
    assert sum(q * count for q, count in profile.items()) == SUM_Q

    # Give 21 q=2 rows diagonal 8 and every other row diagonal 4.
    diagonal_multiset = {4: 210, 8: 21}
    diagonal_sum = sum(value * count for value, count in diagonal_multiset.items())
    diagonal_square_sum = sum(
        value * value * count for value, count in diagonal_multiset.items()
    )
    trace_square = trace_square_constants()["trace_square_minimum"]
    off_diagonal_ordered_square_energy = trace_square - diagonal_square_sum

    odd = odd_entry_counts_at_endpoint()
    # After assigning magnitude one to every forced odd ordered position,
    # the remaining energy can be supplied, at aggregate level, by symmetric
    # magnitude-two pairs.  This does not assert compatible row incidences.
    remaining_after_odd = off_diagonal_ordered_square_energy - odd["ordered"]
    even_unordered_magnitude_two_pairs = remaining_after_odd // 8
    assert remaining_after_odd >= 0 and remaining_after_odd % 8 == 0

    return {
        "profile": profile,
        "diagonal_multiset": diagonal_multiset,
        "diagonal_sum": diagonal_sum,
        "diagonal_square_sum": diagonal_square_sum,
        "t": trace_square_constants()["t_minimum"],
        "trace_square": trace_square,
        "off_diagonal_ordered_square_energy": off_diagonal_ordered_square_energy,
        "forced_odd_ordered_positions": odd["ordered"],
        "additional_unordered_magnitude_two_pairs": even_unordered_magnitude_two_pairs,
        "scope": "aggregate scalar relaxation only",
    }


def spectral_moment_witness() -> Dict[str, object]:
    """Verify the submitted two-point spectrum without evaluating radicals.

    There are 22 copies of each of

        252/11 +/- (21/11)*sqrt(21).

    Symmetric sums suffice to check the first two moments exactly.  The
    positivity test also stays rational after squaring.
    """
    multiplicity = 22
    center = Fraction(252, 11)
    radical_coefficient = Fraction(21, 11)
    radical_squared = radical_coefficient**2 * 21
    total = multiplicity * (2 * center)
    square_total = multiplicity * 2 * (center**2 + radical_squared)
    return {
        "multiplicity_each": multiplicity,
        "rank": 2 * multiplicity,
        "center": center,
        "radical_coefficient": radical_coefficient,
        "radicand": 21,
        "smaller_value_positive": center**2 > radical_squared,
        "sum": total,
        "sum_squares": square_total,
        "scope": "nonnegative spectral first-two-moment relaxation only",
    }


def fraction_json(value: object) -> object:
    if isinstance(value, Fraction):
        return (
            value.numerator
            if value.denominator == 1
            else f"{value.numerator}/{value.denominator}"
        )
    if isinstance(value, dict):
        return {str(key): fraction_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [fraction_json(item) for item in value]
    return value


def build_results() -> Dict[str, object]:
    cap = endpoint_diagonal_cap()
    tensor = {
        "traceless_norm_squared": traceless_tensor_norm_squared(),
        "coefficients": {q: tensor_coefficient(q) for q in range(13)},
        "lower_bounds": {q: tensor_diagonal_lower(q) for q in range(13)},
        "minimum_diagonal_units_q0_to_q8": {
            q: minimum_diagonal_units(q) for q in range(9)
        },
        "endpoint_diagonal_cap": cap,
        "endpoint_allowed_q": endpoint_tensor_allowed_q(),
    }

    harmonic = {
        "kernel_values": {m: harmonic_kernel(m) for m in (4, 1, 0, -1, -2)},
        "endpoint_constants": {
            q: harmonic_constants(q) for q in range(13)
        },
        "endpoint_centered_diagonal": {
            q: centered_harmonic_diagonal(q) for q in range(11)
        },
        "q10_minor_determinants": {
            q: {
                m: centered_minor_determinant(10, q, m)
                for m in (1, 0, -1, -2)
            }
            for q in range(11)
        },
    }

    return fraction_json(
        {
            "premises": {
                "triangle_count": N,
                "projector_rank": DIM,
                "projector_scale": SCALE,
                "n3": ENDPOINT_N3,
                "delta": DELTA,
                "sum_q": SUM_Q,
                "trace_A4": TRACE_A4,
            },
            "tensor": tensor,
            "harmonic": harmonic,
            "trace_square": trace_square_constants(),
            "scalar_relaxation": {
                "profile_count_with_q1": count_scalar_profiles(True),
                "hostile_profile_count_if_q1_silently_deleted": count_scalar_profiles(
                    False
                ),
                "survivor": scalar_survivor(),
                "spectral_moment_witness": spectral_moment_witness(),
            },
            "status": {
                "endpoint_excluded": False,
                "target_resolved": False,
                "novelty_assessed": False,
            },
        }
    )


def main() -> None:
    output = Path(__file__).with_name("independent-checks.json")
    output.write_text(
        json.dumps(build_results(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(output)


if __name__ == "__main__":
    main()
