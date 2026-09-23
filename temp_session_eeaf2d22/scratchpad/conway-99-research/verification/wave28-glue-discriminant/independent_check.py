#!/usr/bin/env python3
"""Independent exact checks for the frozen Wave 28 glue/discriminant lane.

This file is a clean-room implementation.  It imports no discovery code and
does not read the discovery JSON.  All arithmetic is integer or Fraction
arithmetic from the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Iterable


RANK = 44
FRAME_ROWS = 231
H_VALUES = (9, 21, 49, 81, 189, 441, 729, 1029)
NONSQUARE = {3: 2, 7: 3}


def valuation(number: int, prime: int) -> int:
    """Return v_prime(number) for a positive integer."""
    if number <= 0 or prime <= 1:
        raise ValueError("valuation expects a positive integer and a prime")
    value = 0
    while number % prime == 0:
        number //= prime
        value += 1
    return value


def legendre(value: int, prime: int) -> int:
    """Return the Legendre symbol for a unit modulo an odd prime."""
    residue = value % prime
    if residue == 0:
        raise ValueError("Legendre symbol input must be a unit")
    result = pow(residue, (prime - 1) // 2, prime)
    if result == 1:
        return 1
    if result == prime - 1:
        return -1
    raise AssertionError("Euler criterion returned an impossible value")


def signs_for_dimension(dimension: int) -> tuple[int, ...]:
    """The empty form has sign +1; a nonzero odd-primary form has two signs."""
    return (1,) if dimension == 0 else (1, -1)


def exact_level(u: int, v: int) -> int:
    """Exact level of a nonzero elementary 3,7 quadratic module."""
    level = 1
    if u:
        level *= 3
    if v:
        level *= 7
    return level


def invariant_factors(u: int, v: int) -> list[int]:
    """Invariant-factor notation for (Z/3)^u plus (Z/7)^v.

    Mixed primary factors pair as Z/3 plus Z/7 = Z/21.  This is the
    adversarial control for the frozen prose error that incorrectly excluded
    cyclic order-21 factors.
    """
    paired = min(u, v)
    if u >= v:
        return [3] * (u - v) + [21] * paired
    return [7] * (v - u) + [21] * paired


def canonical_coefficients(prime: int, dimension: int, delta: int) -> list[int]:
    """Canonical coefficients a_i for direct sums of <2 a_i / p>."""
    if dimension == 0:
        if delta != 1:
            raise ValueError("the empty component has determinant sign +1")
        return []
    if delta not in (-1, 1):
        raise ValueError("delta must be +/-1")
    coefficients = [1] * dimension
    if delta == -1:
        coefficients[-1] = NONSQUARE[prime]
    product = math.prod(coefficients)
    if legendre(product, prime) != delta:
        raise AssertionError("canonical coefficient sign mismatch")
    return coefficients


def gauss_phase_exponent(dimension: int, delta: int) -> int:
    """Power of i in i^dimension * delta, represented modulo four."""
    if delta not in (-1, 1):
        raise ValueError("delta must be +/-1")
    return (dimension + (2 if delta == -1 else 0)) % 4


def gauss_residue_counts(prime: int, coefficient: int) -> list[int]:
    """Coefficient counts for sum_x zeta_p^(coefficient*x^2)."""
    counts = [0] * prime
    for x in range(prime):
        counts[(coefficient * x * x) % prime] += 1
    return counts


def cyclotomic_zero_for_prime(coefficient_vector: Iterable[int]) -> bool:
    """Test P(zeta_p)=0 when deg(P)<p, using Phi_p=1+...+x^(p-1)."""
    values = tuple(coefficient_vector)
    return bool(values) and all(value == values[0] for value in values)


def local_gauss_controls() -> dict[str, object]:
    """Exact residue-polynomial checks behind the two local sign choices."""
    controls: dict[str, object] = {}
    for prime in (3, 7):
        square = gauss_residue_counts(prime, 1)
        nonsquare = gauss_residue_counts(prime, NONSQUARE[prime])
        conjugate_square = [square[(-index) % prime] for index in range(prime)]
        controls[str(prime)] = {
            "square_counts": square,
            "nonsquare_counts": nonsquare,
            "nonsquare_is_negative_square_at_zeta": cyclotomic_zero_for_prime(
                a + b for a, b in zip(square, nonsquare, strict=True)
            ),
            "square_gauss_sum_is_pure_imaginary": cyclotomic_zero_for_prime(
                a + b for a, b in zip(square, conjugate_square, strict=True)
            ),
            "legendre_nonsquare": legendre(NONSQUARE[prime], prime),
        }
    return controls


def discriminant_candidates_for_h(h: int) -> dict[str, object]:
    """Enumerate every local sign pair satisfying the signature-44 phase."""
    if h not in H_VALUES:
        raise ValueError("h is not in the frozen determinant list")
    u = valuation(h, 3)
    v = valuation(h, 7)
    if h != (3**u) * (7**v):
        raise AssertionError("unexpected prime factor in h")

    candidates: list[dict[str, object]] = []
    for delta_3 in signs_for_dimension(u):
        for delta_7 in signs_for_dimension(v):
            phase = (
                gauss_phase_exponent(u, delta_3)
                + gauss_phase_exponent(v, delta_7)
            ) % 4
            if phase == 2:  # i^2=-1=exp(2*pi*i*44/8)
                candidates.append(
                    {
                        "delta_3": delta_3,
                        "delta_7": delta_7,
                        "coefficients_3": canonical_coefficients(3, u, delta_3),
                        "coefficients_7": canonical_coefficients(7, v, delta_7),
                        "phase_i_exponent": phase,
                    }
                )

    return {
        "h": h,
        "u": u,
        "v": v,
        "group": f"(Z/3)^{u} + (Z/7)^{v}",
        "invariant_factors": invariant_factors(u, v),
        "group_exponent": exact_level(u, v),
        "exact_level": exact_level(u, v),
        "g_primary_dimensions": {"3": RANK - u, "7": RANK - v},
        "candidates": candidates,
    }


def scaled_dual_sign_ratio(h: int, prime: int) -> int:
    """Compute delta_p(G)/delta_p(S) from local Jordan determinants.

    If m=v_p(h), ell=21/p, and n=44, the ratio is

      (2/p)^n (ell/p)^(n-m) (h/p^m / p).
    """
    if prime not in (3, 7):
        raise ValueError("only the frozen primes 3 and 7 are supported")
    m = valuation(h, prime)
    ell = 21 // prime
    unit_part = h // (prime**m)
    return (
        legendre(2, prime) ** RANK
        * legendre(ell, prime) ** (RANK - m)
        * legendre(unit_part, prime)
    )


def complement_rows() -> list[dict[str, int]]:
    """Arithmetic consequences for the complement of a norm-two root."""
    return [
        {
            "h": h,
            "index": 2,
            "determinant_complement": 2 * h,
            "two_primary_order": 2,
        }
        for h in H_VALUES
    ]


def vector_norm(vector: tuple[int, ...], gram: tuple[tuple[int, ...], ...]) -> int:
    return sum(
        vector[i] * gram[i][j] * vector[j]
        for i in range(len(vector))
        for j in range(len(vector))
    )


def vector_pair(
    left: tuple[int, ...],
    right: tuple[int, ...],
    gram: tuple[tuple[int, ...], ...],
) -> int:
    return sum(
        left[i] * gram[i][j] * right[j]
        for i in range(len(left))
        for j in range(len(right))
    )


def a2_root_control() -> dict[str, object]:
    """Hostile exact example showing primitive does not mean orthogonal split."""
    gram = ((2, -1), (-1, 2))
    root = (1, 0)
    complement_generator = (1, 2)
    determinant_l = gram[0][0] * gram[1][1] - gram[0][1] * gram[1][0]
    determinant_direct_sum = vector_norm(root, gram) * vector_norm(
        complement_generator, gram
    )
    index_squared = determinant_direct_sum // determinant_l
    return {
        "lattice": "A2",
        "gram": [list(row) for row in gram],
        "determinant_l": determinant_l,
        "root": list(root),
        "root_norm": vector_norm(root, gram),
        "root_divisibility": math.gcd(*(abs(entry) for entry in gram[0])),
        "complement_generator": list(complement_generator),
        "complement_norm_and_determinant": vector_norm(complement_generator, gram),
        "orthogonality": vector_pair(root, complement_generator, gram),
        "direct_sum_determinant": determinant_direct_sum,
        "index": math.isqrt(index_squared),
        "two_primary_complement_value": {
            "representative": "k/2",
            "q": str(Fraction(vector_norm(complement_generator, gram), 4)),
            "mod_2": "-1/2",
        },
    }


def pattern_census() -> tuple[list[dict[str, int]], list[dict[str, int]]]:
    """Enumerate count patterns from the solved moment equations."""
    second_moment: list[dict[str, int]] = []
    cubic_filtered: list[dict[str, int]] = []
    for a in range(0, 22):
        for e in range(0, 22):
            b = 21 - 3 * a - e
            d = 21 - a - 3 * e
            z = 189 + 3 * (a + e)
            if min(a, b, z, d, e) < 0:
                continue
            record = {
                "a_plus_2": a,
                "b_plus_1": b,
                "z_zero": z,
                "d_minus_1": d,
                "e_minus_2": e,
                "sum": 2 * a + b - d - 2 * e,
                "squared_norm": 4 * a + b + d + 4 * e,
                "cubic_sum": 8 * a + b - d - 8 * e,
            }
            if sum((a, b, z, d, e)) != FRAME_ROWS:
                raise AssertionError("pattern has the wrong number of coordinates")
            if record["sum"] != 0 or record["squared_norm"] != 42:
                raise AssertionError("solved pattern does not satisfy its moments")
            second_moment.append(record)
            energy = Fraction(record["cubic_sum"] ** 2, 8)
            if energy <= 60:
                cubic_filtered.append(record)
    return second_moment, cubic_filtered


def pattern_from_counts(a: int, b: int, z: int, d: int, e: int) -> dict[str, object]:
    cubic_sum = 8 * a + b - d - 8 * e
    energy = Fraction(cubic_sum**2, 8)
    return {
        "counts": [a, b, z, d, e],
        "coordinate_count": a + b + z + d + e,
        "sum": 2 * a + b - d - 2 * e,
        "squared_norm": 4 * a + b + d + 4 * e,
        "cubic_sum": cubic_sum,
        "cubic_energy": {"numerator": energy.numerator, "denominator": energy.denominator},
        "passes_energy_at_most_60": energy <= 60,
    }


def cancellation_order_implication(a_order: int, b_order: int, h_order: int) -> bool:
    """Order-only implication used after injectivity of both glue projections."""
    hypotheses = (
        a_order > 0
        and b_order > 0
        and h_order > 0
        and h_order * h_order == a_order * b_order
        and h_order <= a_order
        and h_order <= b_order
    )
    return (not hypotheses) or (a_order == b_order == h_order)


def root_closure_hypothesis_controls() -> dict[str, object]:
    """Small exact controls showing why the theorem's hypotheses are needed."""
    return {
        "all_roots_required": {
            "lattice": "A1 orthogonal_sum A1",
            "chosen_sublattice": "first A1 only",
            "chosen_complement": "second A1",
            "complement_minimum": 2,
            "conclusion": (
                "An arbitrary root sublattice can have a rooted complement; "
                "rootlessness uses that R contains every root of L."
            ),
        },
        "primitivity_required_for_projection_injectivity": {
            "lattice": "A1=<2> generated by e",
            "nonprimitive_sublattice": "Z(2e)=<8>",
            "complement": "0",
            "overlattice_quotient_order": 2,
            "projection_to_complement_order": 1,
            "conclusion": (
                "Without primitivity, a glue projection can have nontrivial "
                "kernel; Rbar and K are primitive by construction in the theorem."
            ),
        },
        "both_injections_required_for_full_cancellation": {
            "self_dual_order_example": {"A_order": 2, "B_order": 8, "H_order": 4},
            "identity": "4^2=2*8",
            "failed_hypothesis": "H cannot inject into the order-two factor",
        },
    }


def build_results() -> dict[str, object]:
    rows = [discriminant_candidates_for_h(h) for h in H_VALUES]
    total_candidates = sum(len(row["candidates"]) for row in rows)
    second_moment, cubic_filtered = pattern_census()
    hostile = pattern_from_counts(0, 21, 189, 21, 0)
    mutation = pattern_from_counts(4, 9, 201, 17, 0)

    expected_levels = {9: 3, 21: 21, 49: 7, 81: 3, 189: 21, 441: 21, 729: 3, 1029: 21}
    if {row["h"]: row["exact_level"] for row in rows} != expected_levels:
        raise AssertionError("exact-level table mismatch")
    if total_candidates != 12 or total_candidates == 11:
        raise AssertionError("formal discriminant-form count must be exactly twelve")
    if any(
        scaled_dual_sign_ratio(h, p) != 1 for h in H_VALUES for p in (3, 7)
    ):
        raise AssertionError("a scaled-dual local determinant sign changed")
    if len(second_moment) != 46 or len(cubic_filtered) != 32:
        raise AssertionError("one-root count census mismatch")
    if hostile["passes_energy_at_most_60"] is not True:
        raise AssertionError("the hostile scalar-moment control must survive")
    if mutation["passes_energy_at_most_60"] is not False:
        raise AssertionError("the active cubic mutation must be rejected")

    a2 = a2_root_control()
    if (
        a2["determinant_l"] != 3
        or a2["root_divisibility"] != 1
        or a2["index"] != 2
        or a2["complement_norm_and_determinant"] != 6
        or a2["orthogonality"] != 0
    ):
        raise AssertionError("A2 hostile root control failed")

    return {
        "schema_version": 1,
        "implementation": {
            "language": "Python standard library only",
            "discovery_code_imported": False,
            "discovery_json_read": False,
            "arithmetic": "integers and fractions; no floating point",
        },
        "frozen": {
            "rank": RANK,
            "frame_rows": FRAME_ROWS,
            "determinants": list(H_VALUES),
            "signature_phase_i_exponent": 2,
        },
        "local_gauss_controls": local_gauss_controls(),
        "discriminant_rows": rows,
        "formal_candidate_count": total_candidates,
        "hostile_stale_count_11_accepted": total_candidates == 11,
        "scaled_dual": {
            "formula": "(2/p)^44 * ((21/p)/p)^(44-v_p(h)) * ((h/p^v_p(h))/p)",
            "rows": [
                {
                    "h": h,
                    "ratio_delta_g_over_delta_s_at_3": scaled_dual_sign_ratio(h, 3),
                    "ratio_delta_g_over_delta_s_at_7": scaled_dual_sign_ratio(h, 7),
                }
                for h in H_VALUES
            ],
        },
        "single_root": {
            "general_complement_rows": complement_rows(),
            "two_primary_form": "<-1/2>",
            "odd_primary_form": "unchanged from L",
            "a2_hostile_control": a2,
        },
        "projector_patterns": {
            "second_moment_count": len(second_moment),
            "second_moment_patterns": second_moment,
            "cubic_filtered_count": len(cubic_filtered),
            "cubic_filtered_patterns": cubic_filtered,
            "hostile_survivor": hostile,
            "active_rejected_mutation": mutation,
        },
        "primitive_root_closure": {
            "hypotheses": [
                "L is positive-definite, even, and integral",
                "R is generated by every norm-two vector of L",
                "Rbar=(R tensor Q) intersect L",
                "K=Rbar_perp intersect L",
                "H0=Rbar/R and H1=L/(Rbar direct_sum K)",
            ],
            "checked_consequences": [
                "R is an ADE root lattice",
                "Rbar and K are primitive in L",
                "nonzero H0 cosets have minimum at least four",
                "K is rootless",
                "H1 is an isotropic graph with injective projections",
                "q_L is H1_perp/H1",
                "det(L)=det(R)det(K)/(|H0|^2|H1|^2)",
                "away from 3 and 7, both projections are surjective and q_K=-q_Rbar",
            ],
            "hostile_hypothesis_controls": root_closure_hypothesis_controls(),
            "scope": "theorem audited in audit.md; not a finite classification or realization",
        },
        "frozen_discovery_defects": [
            {
                "location": "agents/2026-07-24-wave28-glue-discriminant.md section 2",
                "severity": "wording; nonfatal to downstream mathematics",
                "frozen_text": "There can be no cyclic factor of order 9, 49, or 21",
                "verdict": "FALSE for order 21",
                "reason": "Z/21 is killed by 21 and is isomorphic to Z/3 plus Z/7",
                "impact": (
                    "The primary decomposition, exact levels, twelve-form census, "
                    "and downstream calculations remain valid."
                ),
                "recommended_replacement": (
                    "No p-primary cyclic factor has order p^2 or higher. "
                    "Invariant factors divide 21 and may have order 21."
                ),
            }
        ],
        "verdict": {
            "scoped_claims": "PASS_WITH_CORRECTION",
            "excluded_h_rows": [],
            "lattice_realization": "UNKNOWN",
            "projector_or_schur_realization": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    write_json(arguments.output, build_results())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
