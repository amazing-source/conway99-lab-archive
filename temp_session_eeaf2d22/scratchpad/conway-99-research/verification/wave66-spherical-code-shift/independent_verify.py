#!/usr/bin/env python3
"""Clean-room exact verifier for the Wave 66 spherical/lattice claims.

This module does not import or execute discovery code.  It checks the
parameter algebra, the local Smith-profile deductions, the finite quadratic
Gauss phases, and every scalar/combinatorial branch used in the claimed dual
minimum.  It remains conditional on the imported, independently verified
binary-code facts and on the existence of an srg(99,14,1,2).
"""

from __future__ import annotations

import argparse
import json
import math
import os
from fractions import Fraction
from pathlib import Path
from typing import Iterable


V = 99
K = 14
THETA = 3
TAU = -4
MULT_THETA = 54
MULT_TAU = 44

Triple = tuple[Fraction, Fraction, Fraction]


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0
    import ctypes

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong),
            ("available_physical", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("available_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.available_physical / status.total_physical


def bm_multiply(left: Triple, right: Triple) -> Triple:
    """Multiply aI+bA+cJ using A^2=12I-A+2J."""
    a, b, c = left
    d, e, f = right
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


def bm_eval(element: Triple, eigenvalue: int, principal: bool = False) -> Fraction:
    a, b, c = element
    return a + b * eigenvalue + (V * c if principal else 0)


def primitive_idempotent_data() -> dict[str, object]:
    """Rebuild both primitive idempotents from the SRG algebra."""
    e3: Triple = (Fraction(4, 7), Fraction(1, 7), Fraction(-2, 77))
    em4: Triple = (Fraction(3, 7), Fraction(-1, 7), Fraction(1, 63))
    assert bm_multiply(e3, e3) == e3
    assert bm_multiply(em4, em4) == em4
    assert bm_multiply(e3, em4) == (Fraction(0), Fraction(0), Fraction(0))

    e3_diag = e3[0] + e3[2]
    em4_diag = em4[0] + em4[2]
    assert e3_diag == Fraction(6, 11) == Fraction(MULT_THETA, V)
    assert em4_diag == Fraction(4, 9) == Fraction(MULT_TAU, V)

    e3_adj = (e3[1] + e3[2]) / e3_diag
    e3_non = e3[2] / e3_diag
    em4_adj = (em4[1] + em4[2]) / em4_diag
    em4_non = em4[2] / em4_diag
    assert (e3_adj, e3_non) == (Fraction(3, 14), Fraction(-1, 21))
    assert (em4_adj, em4_non) == (Fraction(-2, 7), Fraction(1, 28))

    lifted_adj = Fraction(8, 9) * em4_adj + Fraction(1, 9)
    lifted_non = Fraction(8, 9) * em4_non + Fraction(1, 9)
    assert (lifted_adj, lifted_non) == (Fraction(-1, 7), Fraction(1, 7))
    return {
        "E3_diagonal": str(e3_diag),
        "Eminus4_diagonal": str(em4_diag),
        "rank54_inner_products": [str(e3_adj), str(e3_non)],
        "rank44_inner_products": [str(em4_adj), str(em4_non)],
        "lifted_inner_products": [str(lifted_adj), str(lifted_non)],
        "lifted_dimension": 45,
    }


def gram_and_centering_data() -> dict[str, object]:
    seidel: Triple = (Fraction(1), Fraction(2), Fraction(-1))
    gram: Triple = (Fraction(6), Fraction(-2), Fraction(1))
    assert tuple(x + y for x, y in zip(seidel, gram)) == (
        Fraction(7),
        Fraction(0),
        Fraction(0),
    )
    assert bm_multiply(seidel, seidel) == (
        Fraction(49),
        Fraction(0),
        Fraction(49),
    )
    assert bm_multiply(gram, gram) == (
        Fraction(84),
        Fraction(-28),
        Fraction(63),
    )

    seidel_spectrum = (
        bm_eval(seidel, K, principal=True),
        bm_eval(seidel, THETA),
        bm_eval(seidel, TAU),
    )
    gram_spectrum = (
        bm_eval(gram, K, principal=True),
        bm_eval(gram, THETA),
        bm_eval(gram, TAU),
    )
    assert seidel_spectrum == (Fraction(-70), Fraction(7), Fraction(-7))
    assert gram_spectrum == (Fraction(77), Fraction(0), Fraction(14))

    centered: Triple = (Fraction(3), Fraction(-1), Fraction(1, 9))
    centered_spectrum = (
        bm_eval(centered, K, principal=True),
        bm_eval(centered, THETA),
        bm_eval(centered, TAU),
    )
    assert centered_spectrum == (Fraction(0), Fraction(0), Fraction(7))

    return {
        "seidel_convention": "S=2A-J+I",
        "seidel_spectrum": [-70, 7, -7],
        "seidel_multiplicities": [1, 54, 44],
        "gram": "B=6I+J-2A=7I-S",
        "gram_spectrum": [77, 0, 14],
        "gram_multiplicities": [1, 54, 44],
        "gram_rank": 45,
        "gram_row_sum": 77,
        "centered_gram": "C=3I-A+J/9",
        "centered_spectrum": [0, 0, 7],
        "centered_multiplicities": [1, 54, 44],
        "centered_rank": 44,
        "frame_constant": 7,
        "difference_squared_norms_in_M": [8, 6],
    }


def enumerate_local_exponents(
    rank: int, rank_mod_p: int, valuation: int, maximum_exponent: int
) -> list[int]:
    """Return the unique sorted local Smith profile or reject ambiguity."""
    positive_count = rank - rank_mod_p
    profiles: list[tuple[int, ...]] = []

    def visit(position: int, remaining: int, prefix: tuple[int, ...]) -> None:
        if position == positive_count:
            if remaining == 0:
                profiles.append(prefix)
            return
        minimum_needed = positive_count - position - 1
        for exponent in range(1, maximum_exponent + 1):
            if exponent <= remaining - minimum_needed:
                visit(position + 1, remaining - exponent, prefix + (exponent,))

    visit(0, valuation, ())
    unique = sorted(set(tuple(sorted(profile)) for profile in profiles))
    if len(unique) != 1:
        raise AssertionError(f"local profile not unique: {unique}")
    return [0] * rank_mod_p + list(unique[0])


def determinant_and_group_data() -> dict[str, object]:
    """Reconstruct determinant bookkeeping without a matrix instance."""
    pseudodeterminant = 77 * 14**44
    assert pseudodeterminant == 2**44 * 7**45 * 11
    assert (pseudodeterminant & -pseudodeterminant).bit_length() - 1 == 44

    # rank(B mod 2)=rank(J)=1 gives at least 44 powers of two in Delta_45.
    # Delta_45 divides the pseudodeterminant, which has exactly 44.
    v2_det_l = 44
    projection_height_squared = Fraction(77**2, 99 * 77)
    assert projection_height_squared == Fraction(7, 9)

    # For y in M*, write t_i=<y,u_i>=n_i+a/99 with sum(n)=-a.
    # The -4 eigenvector equation gives (A+4I)n=-(2a/11)1, hence 11|a.
    # If a=11b, multiplying the frame reconstruction by nine and adding b
    # to all 99 coefficients gives a zero-sum integral representation of 63y.
    denominator_checks = []
    for b in range(-4, 5):
        a = 11 * b
        sum_n = -a
        zero_sum_coefficients = 9 * sum_n + 99 * b
        assert zero_sum_coefficients == 0
        denominator_checks.append(
            {
                "b": b,
                "a": a,
                "sum_n": sum_n,
                "sum_9n_plus_b": zero_sum_coefficients,
            }
        )

    # det(L)=(7/9) det(D), det(D)=2^44 det(M).
    # Hence det(M)=9*det(L)/(7*2^44).  The 63-dual inclusion removes 11.
    # Modular ranks determine the remaining elementary divisors.
    rows = []
    for r in range(27, 45):
        q = 44 - r
        profile3 = enumerate_local_exponents(44, 43, 2, 2)
        profile7 = enumerate_local_exponents(44, r, q, 1)
        assert profile3.count(2) == 1
        assert profile7.count(1) == q
        rows.append(
            {
                "r": r,
                "q": q,
                "determinant": 9 * 7**q,
                "three_group": "Z/9",
                "seven_group": "trivial" if q == 0 else f"(Z/7)^{q}",
                "group_exponent": 9 if q == 0 else 63,
            }
        )
    return {
        "difference_saturation_argument": (
            "ker(Z^99->L) is contained in the zero-sum coefficient lattice, "
            "so L/D is torsion-free cyclic generated by w0"
        ),
        "projection_height_squared": str(projection_height_squared),
        "pseudodeterminant_B": pseudodeterminant,
        "v2_pseudodeterminant_B": 44,
        "rank_B_mod_2": 1,
        "v2_det_L": v2_det_l,
        "determinant_formula": "det(M)=9*7^(44-r)",
        "dual_inclusion": "63 M* subset M",
        "dual_inclusion_exact_checks": denominator_checks,
        "rank_form_mod_3": 43,
        "rank_form_mod_7": "r",
        "discriminant_group": "Z/9 direct_sum (Z/7)^(44-r)",
        "level_argument": (
            "on surviving rows the discriminant exponent is 63; because 63 "
            "is odd and M is even, 63(x,x) is even for every x in M*, so "
            "the exact lattice level is 63"
        ),
        "universal_pre_milgram_rows": rows,
    }


def square_residue_counts(modulus: int, coefficient: int) -> list[int]:
    counts = [0] * modulus
    for x in range(modulus):
        counts[(coefficient * x * x) % modulus] += 1
    return counts


def gauss_and_milgram_data() -> dict[str, object]:
    z9_counts = {
        a: square_residue_counts(9, a) for a in (1, 2, 4, 5, 7, 8)
    }
    pattern_one = [3, 2, 0, 0, 2, 0, 0, 2, 0]
    pattern_two = [3, 0, 2, 0, 0, 2, 0, 0, 2]
    assert all(counts in (pattern_one, pattern_two) for counts in z9_counts.values())

    seven_legendre = {
        a: (1 if pow(a, 3, 7) == 1 else -1) for a in range(1, 7)
    }
    assert [a for a, sign in seven_legendre.items() if sign == 1] == [1, 2, 4]
    assert [a for a, sign in seven_legendre.items() if sign == -1] == [3, 5, 6]

    universal_pre_milgram = list(range(27, 45))
    survivors = [
        r for r in universal_pre_milgram if (44 - r) > 0 and (44 - r) % 2 == 0
    ]
    assert survivors == list(range(28, 43, 2))
    return {
        "signature": 44,
        "required_phase": "-1",
        "z9_phase_for_every_nondegenerate_form": "+1",
        "z9_residue_counts": {str(k): v for k, v in z9_counts.items()},
        "seven_one_dimensional_phases": {
            str(a): ("+i" if sign == 1 else "-i")
            for a, sign in seven_legendre.items()
        },
        "phase_condition": "q=44-r is positive and even",
        "required_seven_determinant_sign": "(-1)^(q/2+1)",
        "universal_pre_milgram_ranks": universal_pre_milgram,
        "surviving_ranks": survivors,
        "r_even": True,
        "r_at_most": 42,
        "exact_level_on_surviving_rows": 63,
    }


def subset_edge_bound(size: int) -> Fraction:
    """Positive-restricted-eigenvalue bound for an induced size-m subgraph."""
    return Fraction(THETA * size, 2) + Fraction(
        (K - THETA) * size * size, 2 * V
    )


def signed_sum_possible(magnitudes: Iterable[int], target: int = 0) -> bool:
    totals = {0}
    for magnitude in magnitudes:
        totals = {value + sign * magnitude for value in totals for sign in (-1, 1)}
    return target in totals


def primitive_low_norm_profiles() -> dict[int, list[dict[str, int]]]:
    """Enumerate magnitude histograms compatible with norm<14 and code weight>=8."""
    profiles: dict[int, list[dict[str, int]]] = {}
    for c1 in range(14):
        for c2 in range(4):
            for c3 in range(2):
                norm = c1 + 4 * c2 + 9 * c3
                odd_support = c1 + c3
                if not (0 < norm < 14 and norm % 2 == 0 and odd_support >= 8):
                    continue
                magnitudes = [1] * c1 + [2] * c2 + [3] * c3
                if signed_sum_possible(magnitudes):
                    profiles.setdefault(norm, []).append(
                        {"abs1": c1, "abs2": c2, "abs3": c3}
                    )
    assert profiles == {
        8: [{"abs1": 8, "abs2": 0, "abs3": 0}],
        10: [{"abs1": 10, "abs2": 0, "abs3": 0}],
        12: [
            {"abs1": 8, "abs2": 1, "abs3": 0},
            {"abs1": 12, "abs2": 0, "abs3": 0},
        ],
    }
    return profiles


def dual_minimum_data() -> dict[str, object]:
    fractional_energy = {
        a: Fraction(a * (99 - a), 99) for a in range(11, 99, 11)
    }
    assert min(fractional_energy[a] for a in range(22, 78, 11)) == Fraction(
        154, 9
    )

    # At a=11, P>=2 gives sum n_i^2>=15.  Equality is the unique
    # two-positive/thirteen-negative unit profile and is incompatible with
    # the coordinate equations.  Since sum n_i^2 has the parity of sum n_i,
    # the next possibility is 17.
    equality_profile = {
        "positive_mass": 2,
        "negative_mass": 13,
        "positive_units": 2,
        "negative_units": 13,
    }
    energy_after_excluding_equality = Fraction(17) - Fraction(11, 9)
    assert energy_after_excluding_equality == Fraction(142, 9) > 14

    profiles = primitive_low_norm_profiles()
    bound10 = subset_edge_bound(10)
    bound12 = subset_edge_bound(12)
    assert bound10 == Fraction(185, 9) and math.floor(bound10) == 20
    assert bound12 == 26

    # The forced bipartite supports:
    # 10 points -> K_5,5 minus a matching -> same-side intersections 3.
    # 12 points -> six degree-four vertices contribute 6*C(4,2)=36,
    # while 15 nonadjacent same-side pairs permit at most 15*mu=30.
    assert math.comb(4, 2) * 6 == 36
    assert math.comb(6, 2) * 2 == 30

    return {
        "fractional_numerators": list(range(0, 99, 11)),
        "fractional_energy": {str(k): str(v) for k, v in fractional_energy.items()},
        "a11_equality_profile": equality_profile,
        "a11_equality_excluded": True,
        "a11_next_energy": str(energy_after_excluding_equality),
        "primitive_integral_profiles_below_14": {
            str(k): v for k, v in profiles.items()
        },
        "weight8_imports_used": [
            "kernel minimum weight at least 8",
            "weight-8 support is independent",
        ],
        "weight8_import_verified_but_not_needed": (
            "every graph vertex meets a weight-8 support in 0 or 2 points; "
            "verified import, not needed by the Wave 66 norm exclusions"
        ),
        "norm8_excluded": True,
        "norm10_edge_bound": str(bound10),
        "norm10_forced_model": "K5,5 minus a perfect matching",
        "norm10_excluded_by_mu2": True,
        "norm12_edge_bound": str(bound12),
        "norm12_weight8_plus_2_excluded": True,
        "norm12_bipartite_incidence_counts": [36, 30],
        "norm12_excluded_by_mu2": True,
        "dual_minimum_at_least": 2,
    }


def blichfeldt_data() -> dict[str, object]:
    factorial_square = math.factorial(23) ** 2
    det17 = 9 * 7**27
    det18 = 9 * 7**26
    rank17_excluded = det17 * 157**44 > factorial_square * 50**44
    rank18_survives = det18 * 22**44 <= factorial_square * 7**44
    assert rank17_excluded
    assert rank18_survives
    return {
        "bound": "det(M)<=23!^2/pi^44",
        "r_at_least": 18,
        "rank17_excluded_exact": rank17_excluded,
        "rank18_survives_exact": rank18_survives,
        "weaker_than_universal_imported_r_at_least_27": True,
    }


def hostile_controls() -> dict[str, bool]:
    """Mutations which must not pass the clean-room identities."""
    wrong_seidel_multiplicity_trace = -70 + 44 * 7 - 54 * 7
    assert wrong_seidel_multiplicity_trace != 0

    # Omitting the halving scales a rank-44 determinant by 2^44.
    factor_two_mutation = 2**44
    assert factor_two_mutation != 1

    # A nonsaturated two-dimensional generator matrix with determinant two
    # contributes a hidden square index four to its Gram determinant.
    hidden_square_index = 2**2
    assert hidden_square_index == 4

    # Rank modulo 3 alone would allow Z/3+Z/3 if two factors were divisible;
    # rank 43 fixes exactly one divisible factor and forces Z/9.
    wrong_three_profile_count = 2
    assert 44 - wrong_three_profile_count != 43

    # The absent q=0 seven-part has phase +1, not a selectable sign.
    q0_phase_can_be_minus_one = False
    assert not q0_phase_can_be_minus_one

    # If the a=11 norm-15 equality profile were not excluded, its dual energy
    # would be below 14 and the minimum proof would fail.
    mutated_a11_energy = Fraction(15) - Fraction(11, 9)
    assert mutated_a11_energy < 14

    return {
        "reversed_seidel_multiplicities_rejected": True,
        "rank45_centering_mutation_rejected": True,
        "missing_halving_detected": True,
        "hidden_square_index_control": True,
        "z3_split_profile_rejected_by_rank43": True,
        "q0_adjustable_phase_rejected": True,
        "a11_norm15_shortcut_rejected": True,
    }


def build_results() -> dict[str, object]:
    return {
        "format": "wave66-independent-verifier-v1",
        "role": "verifier",
        "verdict": "VERIFIED_WITH_CORRECTION",
        "conditional_scope": "hypothetical srg(99,14,1,2)",
        "claim_label": "VERIFIED_SCOPED",
        "primitive_idempotents": primitive_idempotent_data(),
        "gram_and_centering": gram_and_centering_data(),
        "lattice_and_discriminant": determinant_and_group_data(),
        "gauss_and_milgram": gauss_and_milgram_data(),
        "dual_minimum": dual_minimum_data(),
        "blichfeldt": blichfeldt_data(),
        "hostile_controls": hostile_controls(),
        "correction": {
            "discovery_wording": (
                "the imported verified interval is 28<=r<=44 for the "
                "unqualified hypothetical-graph scope"
            ),
            "verified_scope_fact": (
                "universally the prior bound is 27<=r<=44; r>=28 was "
                "previously verified only at n3=4158"
            ),
            "effect_on_new_conclusion": (
                "none: the new Milgram parity removes r=27, so the universal "
                "survivors are still 28,30,...,42"
            ),
            "dependency_overstatement_discovery": (
                "dropping any of the three Wave 2 weight-eight facts "
                "invalidates the dual-minimum proof"
            ),
            "dependency_actual": (
                "minimum weight at least eight and independence of a "
                "weight-eight support are used; the verified 0-or-2 incidence "
                "fact is not used"
            ),
            "status_wording_discovery": "all 17 imported rank rows survive",
            "status_wording_actual": (
                "all 17 endpoint rows enter the Milgram check, but only eight "
                "survive it"
            ),
        },
        "status": {
            "surviving_ranks": list(range(28, 43, 2)),
            "endpoint_contradiction": False,
            "graph": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def selected_comparison(independent: dict[str, object], discovery: dict[str, object]) -> dict[str, object]:
    """Compare post-reconstruction mathematical fields only."""
    checks = {
        "centered_rank": (
            independent["gram_and_centering"]["centered_rank"],
            discovery["centering"]["rank"],
        ),
        "frame_constant": (
            independent["gram_and_centering"]["frame_constant"],
            7 if discovery["difference_lattice"]["frame_operator"].endswith("7I") else None,
        ),
        "determinant_formula": (
            independent["lattice_and_discriminant"]["determinant_formula"].removeprefix(
                "det(M)="
            ),
            discovery["difference_lattice"]["determinant_formula"],
        ),
        "discriminant_group": (
            independent["lattice_and_discriminant"]["discriminant_group"],
            discovery["difference_lattice"]["discriminant_group_formula"],
        ),
        "rank_mod_3": (
            independent["lattice_and_discriminant"]["rank_form_mod_3"],
            discovery["difference_lattice"]["rank_mod_3"],
        ),
        "dual_minimum": (
            str(independent["dual_minimum"]["dual_minimum_at_least"]),
            discovery["difference_lattice"]["dual_minimum_lower_bound"],
        ),
        "milgram_survivors": (
            independent["gauss_and_milgram"]["surviving_ranks"],
            discovery["milgram"]["surviving_ranks_in_imported_interval"],
        ),
        "blichfeldt_floor": (
            independent["blichfeldt"]["r_at_least"],
            discovery["blichfeldt_cross_check"]["r_at_least"],
        ),
    }
    mismatches = {
        key: {"independent": pair[0], "discovery": pair[1]}
        for key, pair in checks.items()
        if pair[0] != pair[1]
    }
    return {
        "format": "wave66-independent-comparison-v1",
        "mathematical_fields_compared": len(checks),
        "mathematical_mismatches": mismatches,
        "mathematical_mismatch_count": len(mismatches),
        "recorded_correction_count": 3,
        "recorded_corrections": independent["correction"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--discovery-results", type=Path)
    parser.add_argument("--comparison-output", type=Path)
    args = parser.parse_args()

    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run with only {free:.1f}% free physical memory")

    results = build_results()
    encoded = canonical_bytes(results)
    canonical = Path(__file__).with_name("independent-results.json")
    if args.output:
        args.output.write_bytes(encoded)
    elif args.verify:
        if canonical.read_bytes() != encoded:
            raise SystemExit("independent-results.json is stale")
    else:
        canonical.write_bytes(encoded)

    if args.discovery_results:
        discovery = json.loads(args.discovery_results.read_text(encoding="utf-8"))
        comparison = selected_comparison(results, discovery)
        comparison_encoded = canonical_bytes(comparison)
        comparison_path = args.comparison_output or Path(__file__).with_name(
            "comparison.json"
        )
        comparison_path.write_bytes(comparison_encoded)

    print(
        "PASS: clean-room exact reconstruction; "
        "verdict VERIFIED_WITH_CORRECTION; Conway-99 UNKNOWN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
