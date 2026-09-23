#!/usr/bin/env python3
"""Exact arithmetic checks for the Wave 66 spherical/lattice shift.

This is a deterministic parameter-level checker.  It does not construct an
SRG or independently verify the mathematical derivation.
"""

from __future__ import annotations

import argparse
import json
import os
import math
from fractions import Fraction
from pathlib import Path
from typing import Dict, Tuple


V = 99
K = 14
R = 3
S_EIG = -4
M_R = 54
M_S = 44


def free_memory_percent() -> float:
    """Return free physical-memory percentage on Windows, or 100 elsewhere."""
    if os.name != "nt":
        return 100.0
    import ctypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.ullAvailPhys / status.ullTotalPhys


# Triples represent a*I+b*A+c*J in the SRG Bose-Mesner algebra.
Triple = Tuple[int, int, int]


def multiply(x: Triple, y: Triple) -> Triple:
    a, b, c = x
    d, e, f = y
    # A^2=12I-A+2J, AJ=JA=14J, J^2=99J.
    return (
        a * d + 12 * b * e,
        a * e + b * d - b * e,
        a * f
        + c * d
        + 2 * b * e
        + 14 * b * f
        + 14 * c * e
        + 99 * c * f,
    )


def add(x: Triple, y: Triple) -> Triple:
    return tuple(a + b for a, b in zip(x, y))  # type: ignore[return-value]


def scale(c: int, x: Triple) -> Triple:
    return tuple(c * a for a in x)  # type: ignore[return-value]


def eval_on_eigenvalue(x: Triple, eigenvalue: int, principal: bool = False) -> int:
    a, b, c = x
    return a + b * eigenvalue + (V * c if principal else 0)


def spectral_subset_edge_ceiling(size: int) -> int:
    return int(exact_subset_bound(size))


def exact_subset_bound(size: int) -> Fraction:
    return Fraction(R * size, 2) + Fraction((K - R) * size * size, 2 * V)


def fractional_energy(a: int) -> Fraction:
    return Fraction(a * (V - a), V)


def z9_gauss_cyclotomic_quotient(a: int) -> Dict[str, object]:
    """Exact proof that the normalized Z/9 Gauss phase is +1.

    If zeta is a primitive ninth root, Phi_9=1+x^3+x^6.  For every unit a,
    sum_x zeta^(a*x^2)-3 is either 2*x*Phi_9 or 2*x^2*Phi_9.
    """
    if a % 3 == 0:
        raise ValueError("a must be a unit modulo 9")
    counts = [0] * 9
    for x in range(9):
        counts[(a * x * x) % 9] += 1
    expected_one = [3, 2, 0, 0, 2, 0, 0, 2, 0]
    expected_two = [3, 0, 2, 0, 0, 2, 0, 0, 2]
    if counts == expected_one:
        quotient = "2*x"
    elif counts == expected_two:
        quotient = "2*x^2"
    else:
        raise AssertionError("unexpected Z/9 quadratic-residue count")
    return {
        "coefficient_counts": counts,
        "sum_minus_3_quotient_by_Phi9": quotient,
        "normalized_phase": "+1",
    }


def build_results() -> Dict[str, object]:
    # Convention S=2A-J+I; B=7I-S=6I-2A+J.
    seidel: Triple = (1, 2, -1)
    gram_b: Triple = (6, -2, 1)
    centered_twice: Triple = (6, -2, 0)

    assert add(seidel, gram_b) == (7, 0, 0)
    assert multiply(seidel, seidel) == (49, 0, 49)
    assert multiply(gram_b, gram_b) == add(scale(14, gram_b), (0, 0, 49))

    spectrum_b = {
        "principal": eval_on_eigenvalue(gram_b, K, principal=True),
        "eigenvalue_3_space": eval_on_eigenvalue(gram_b, R),
        "eigenvalue_minus4_space": eval_on_eigenvalue(gram_b, S_EIG),
    }
    assert spectrum_b == {
        "principal": 77,
        "eigenvalue_3_space": 0,
        "eigenvalue_minus4_space": 14,
    }
    spectrum_s = {
        "principal": eval_on_eigenvalue(seidel, K, principal=True),
        "eigenvalue_3_space": eval_on_eigenvalue(seidel, R),
        "eigenvalue_minus4_space": eval_on_eigenvalue(seidel, S_EIG),
    }
    assert spectrum_s == {
        "principal": -70,
        "eigenvalue_3_space": 7,
        "eigenvalue_minus4_space": -7,
    }

    # C=3I-A+J/9 is the centered rank-44 Gram matrix.
    centered_spectrum = {
        "principal": Fraction(3 - K, 1) + Fraction(V, 9),
        "eigenvalue_3_space": Fraction(3 - R, 1),
        "eigenvalue_minus4_space": Fraction(3 - S_EIG, 1),
    }
    assert centered_spectrum == {
        "principal": Fraction(0, 1),
        "eigenvalue_3_space": Fraction(0, 1),
        "eigenvalue_minus4_space": Fraction(7, 1),
    }

    subset_bounds = {
        str(size): {
            "exact_edge_upper_bound": str(exact_subset_bound(size)),
            "integer_edge_ceiling": int(exact_subset_bound(size)),
        }
        for size in (10, 12)
    }
    assert subset_bounds["10"]["integer_edge_ceiling"] == 20
    assert subset_bounds["12"]["integer_edge_ceiling"] == 26

    fractional = {
        str(a): str(fractional_energy(a)) for a in range(11, 99, 11)
    }
    assert fractional["11"] == "88/9"
    assert fractional["22"] == "154/9"
    assert fractional["88"] == "88/9"

    determinant_rows = []
    for rank7 in range(28, 45):
        exponent = 44 - rank7
        determinant_rows.append(
            {
                "rank_F7_Seidel": rank7,
                "seven_exponent": exponent,
                "determinant": 9 * (7**exponent),
                "milgram_phase_possible": exponent > 0 and exponent % 2 == 0,
                "required_seven_determinant_sign": (
                    None if exponent == 0 or exponent % 2 else (-1) ** (exponent // 2 + 1)
                ),
                "discriminant_group": (
                    "Z/9"
                    if exponent == 0
                    else f"Z/9 direct_sum (Z/7)^{exponent}"
                ),
            }
        )
    surviving_rows = [
        row for row in determinant_rows if row["milgram_phase_possible"]
    ]
    assert [row["rank_F7_Seidel"] for row in surviving_rows] == list(
        range(28, 43, 2)
    )

    # Blichfeldt: gamma_44 <= (2/pi)*Gamma(24)^(1/22), hence
    # det(M) <= 23!^2/pi^44.  Rational bounds 157/50 < pi < 22/7
    # prove r<=17 impossible while r=18 is not deleted by this inequality.
    factorial_square = math.factorial(23) ** 2
    rank17_det = 9 * 7**27
    rank18_det = 9 * 7**26
    rank17_excluded_exact = (
        rank17_det * 157**44 > factorial_square * 50**44
    )
    rank18_survives_exact = (
        rank18_det * 22**44 <= factorial_square * 7**44
    )
    assert rank17_excluded_exact
    assert rank18_survives_exact

    z9_gauss = {
        str(a): z9_gauss_cyclotomic_quotient(a)
        for a in (1, 2, 4, 5, 7, 8)
    }
    milgram_phase_table = []
    for exponent in range(17):
        possible = exponent > 0 and exponent % 2 == 0
        milgram_phase_table.append(
            {
                "seven_dimension": exponent,
                "possible_phase_types": (
                    ["+1"] if exponent == 0
                    else (["+i", "-i"] if exponent % 2 else ["+1", "-1"])
                ),
                "can_match_signature_phase_minus_one": possible,
            }
        )

    # The two embedding inner products and constant-coordinate lift.
    emb3_adj = Fraction(3, 14)
    emb3_non = Fraction(-1, 21)
    embm4_adj = Fraction(-2, 7)
    embm4_non = Fraction(1, 28)
    lift_constant_square = Fraction(1, 8)
    lift_scale = Fraction(1, 1) / (1 + lift_constant_square)
    lifted_adj = (embm4_adj + lift_constant_square) * lift_scale
    lifted_non = (embm4_non + lift_constant_square) * lift_scale
    assert lifted_adj == Fraction(-1, 7)
    assert lifted_non == Fraction(1, 7)

    return {
        "format": "wave66-spherical-code-shift-v1",
        "claim_label": "CANDIDATE",
        "scope": "conditional consequences of a hypothetical srg(99,14,1,2)",
        "srg_parameters": {
            "v": V,
            "k": K,
            "lambda": 1,
            "mu": 2,
            "restricted_eigenvalues": {
                "3": M_R,
                "-4": M_S,
            },
        },
        "spherical_embeddings": {
            "rank_54": {
                "adjacent_inner_product": str(emb3_adj),
                "nonadjacent_inner_product": str(emb3_non),
            },
            "rank_44": {
                "adjacent_inner_product": str(embm4_adj),
                "nonadjacent_inner_product": str(embm4_non),
            },
            "equiangular_lift": {
                "dimension": 45,
                "common_absolute_inner_product": "1/7",
                "adjacent": str(lifted_adj),
                "nonadjacent": str(lifted_non),
            },
        },
        "integral_gram": {
            "seidel_sign_convention": (
                "S=2A-J+I; adjacent +1, nonadjacent -1, diagonal 0"
            ),
            "seidel_spectrum": spectrum_s,
            "B": "6I + J - 2A = 7I - S",
            "diagonal": 7,
            "off_diagonal": [-1, 1],
            "row_sum": 77,
            "spectrum": spectrum_b,
            "nonzero_pseudodeterminant": 77 * (14**44),
            "two_adic_valuation": 44,
            "identity": "B^2 = 14B + 49J",
        },
        "centering": {
            "centered_gram": "C=3I-A+J/9",
            "spectrum": {
                key: str(value) for key, value in centered_spectrum.items()
            },
            "rank": 44,
            "all_ones_direction_removed": True,
            "difference_norms_after_halving": {
                "adjacent_to_reference": 8,
                "nonadjacent_to_reference": 6,
            },
        },
        "difference_lattice": {
            "rank": 44,
            "even": True,
            "frame_operator": "sum_i u_i u_i^T = 7I",
            "dual_denominator": "63 M* subset M",
            "determinant_formula": "9*7^(44-r)",
            "discriminant_group_formula": "Z/9 direct_sum (Z/7)^(44-r)",
            "rank_parameter": "r=rank_F7(S)",
            "rank_mod_3": 43,
            "rank_mod_7": "r",
            "dual_minimum_lower_bound": "2",
            "milgram_congruence": "r is even and r<=42",
        },
        "milgram": {
            "signature": 44,
            "required_normalized_gauss_phase": "-1",
            "Z9_normalized_gauss_phase": "+1",
            "seven_primary_phase": "delta*i^(44-r), delta in {+1,-1}",
            "necessary_and_sufficient_phase_condition_at_group_level": (
                "44-r is positive and even"
            ),
            "required_seven_determinant_sign": "(-1)^((44-r)/2+1)",
            "exact_discriminant_form_level_for_survivors": 63,
            "z9_exact_cyclotomic_checks": z9_gauss,
            "seven_dimension_phase_table": milgram_phase_table,
            "surviving_ranks_in_imported_interval": list(range(28, 43, 2)),
        },
        "blichfeldt_cross_check": {
            "bound": "det(M) <= 23!^2/pi^44",
            "r_at_least": 18,
            "rank_17_excluded_using_pi_gt_157_over_50": rank17_excluded_exact,
            "rank_18_survives_using_pi_lt_22_over_7": rank18_survives_exact,
            "weaker_than_imported_r_at_least_28": True,
        },
        "dual_minimum_checks": {
            "allowed_fractional_numerators_mod_99": list(range(0, 99, 11)),
            "unconstrained_fractional_energy_minima": fractional,
            "a11_integer_norm_15_equality_profile": {
                "positive_ones": 2,
                "negative_ones": 13,
                "excluded_by_coordinate_equations": True,
            },
            "integral_norms_below_14_excluded": [8, 10, 12],
            "subset_edge_bounds": subset_bounds,
            "ten_support_forced_model": "4-regular bipartite on 5+5; violates mu=2",
            "twelve_support_forced_model": (
                "4-regular bipartite on 6+6; 36 same-side common-neighbor "
                "incidences exceed 30"
            ),
        },
        "endpoint": {
            "imported_verified_rank_interval": [28, 44],
            "all_determinant_rows_before_milgram": determinant_rows,
            "surviving_rows": surviving_rows,
            "survivor_count": len(surviving_rows),
            "contradiction_found": False,
            "graph_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "This package is discovery work and is not independent verification.",
            "No graph, equiangular configuration, or lattice is constructed.",
            "A discriminant-group profile is not a lattice realization.",
            "All 17 imported rank rows survive.",
        ],
    }


def canonical_bytes(payload: Dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run with only {free:.1f}% free physical memory")

    payload = build_results()
    encoded = canonical_bytes(payload)
    canonical_path = Path(__file__).with_name("exact-results.json")

    if args.output:
        args.output.write_bytes(encoded)
    elif args.verify:
        if canonical_path.read_bytes() != encoded:
            raise SystemExit("exact-results.json is stale")
        print("PASS: canonical artifact matches exact recomputation")
    else:
        canonical_path.write_bytes(encoded)
        print(f"wrote {canonical_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
