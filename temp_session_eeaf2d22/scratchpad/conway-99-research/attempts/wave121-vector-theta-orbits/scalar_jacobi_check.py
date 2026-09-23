#!/usr/bin/env python3
"""Exact one-variable C4 Jacobi reduction for the Wave 121 continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


Q = Fraction
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = Path(__file__).with_name("scalar-jacobi-results.json")

FROZEN_INPUTS = {
    "verification/wave66-spherical-code-shift/package-manifest.sha256":
        "a6051ebcfccab0fc9b3f9698f0024cc3284549f5148c9a12a4c6bbe08c786486",
    "verification/wave71-modular-theta-extension/package-manifest.sha256":
        "0eede2ebc625534360dda3f8e62456e582f5184fd18d3820dd44748de95a5237",
    "verification/wave86-level7-exact/package-manifest.sha256":
        "cbfafc03db11ad7f103e532e0f5e0b2e85ff6b568ad327b947a2d394a1d1dfa2",
    "verification/wave112-c4-short-vector-incidence/package-manifest.sha256":
        "56845bcdf221c16ec46d40c630a8cdb3d63beed1314dd2683e17bf5c929ff024",
    "attempts/wave116-c4-jacobi-theta/package-manifest.sha256":
        "9c474c8fc6c04e382b7fd506997c7ec81cb5ea5fa38453e6f284271eda933d98",
    "verification/wave116-c4-jacobi-theta/package-manifest.sha256":
        "e44afa352f51c192d6c5ac8584ccd6334dd69a3d11856f4ac0254283829bbfb8",
}


def free_memory_percent() -> float:
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_frozen_inputs() -> None:
    for relative, expected in FROZEN_INPUTS.items():
        actual = sha256_file(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"frozen input mismatch for {relative}: {actual} != {expected}"
            )


def matvec(matrix: list[list[Q]], vector: list[int]) -> list[Q]:
    return [
        sum(entry * value for entry, value in zip(row, vector))
        for row in matrix
    ]


def dot(left: list[int] | list[Q], right: list[int] | list[Q]) -> Q:
    return sum(Q(a) * Q(b) for a, b in zip(left, right))


def build_results() -> dict[str, object]:
    check_frozen_inputs()
    if free_memory_percent() < 15.0:
        raise MemoryError("host free-memory budget below 15 percent")

    epsilon = [1, -1, 1, -1]
    gram_u = [
        [Q(28, 9), Q(-8, 9), Q(1, 9), Q(-8, 9)],
        [Q(-8, 9), Q(28, 9), Q(-8, 9), Q(1, 9)],
        [Q(1, 9), Q(-8, 9), Q(28, 9), Q(-8, 9)],
        [Q(-8, 9), Q(1, 9), Q(-8, 9), Q(28, 9)],
    ]
    image = matvec(gram_u, epsilon)
    norm_d = dot(epsilon, image)
    if image != [Q(5), Q(-5), Q(5), Q(-5)] or norm_d != 20:
        raise AssertionError("alternating C4 norm mismatch")

    norm_b = 7 * norm_d
    index_k = norm_b // 2
    index_l = norm_d // 2
    old_norm_h = 9 * norm_b
    if (norm_b, index_k, index_l, old_norm_h) != (140, 70, 10, 1260):
        raise AssertionError("Jacobi scale mismatch")

    # If d=k*e in the even lattice L, then 20/k^2=e^2 is an even integer.
    primitive_obstructions = {
        k: Q(20, k * k)
        for k in range(2, 6)
        if Q(20, k * k).denominator == 1
        and Q(20, k * k).numerator % 2 == 0
    }
    if primitive_obstructions:
        raise AssertionError("unexpected divisibility candidate")

    support = {
        n: 4 * index_k * n - 28**2 for n in (7, 8, 9, 10)
    }
    if any(value < 0 for value in support.values()):
        raise AssertionError("target violates Jacobi support")

    short_scalar_control = {"x7": 5868, "x8": 0, "x9": 0}
    target_antipodal = 52812
    cycle_count = 2079
    row_total_q7 = cycle_count * short_scalar_control["x7"]
    truncated_coefficients = {
        "c(0,0)": cycle_count,
        "c(7,-28)": target_antipodal,
        "c(7,0)": row_total_q7 - 2 * target_antipodal,
        "c(7,28)": target_antipodal,
    }
    if (
        truncated_coefficients["c(7,-28)"]
        + truncated_coefficients["c(7,0)"]
        + truncated_coefficients["c(7,28)"]
        != row_total_q7
    ):
        raise AssertionError("truncated row sum mismatch")
    if min(truncated_coefficients.values()) < 0:
        raise AssertionError("negative truncated coefficient")

    return {
        "format": "wave121-scalar-c4-jacobi-v1",
        "claim_label": "DERIVED",
        "scope": (
            "conditional one-variable C4 Jacobi reduction in the rank-28 "
            "q=16 row; exact arithmetic and a truncated coefficient-cone "
            "null control, not a complete Jacobi basis"
        ),
        "frozen_inputs": FROZEN_INPUTS,
        "alternating_vector": {
            "epsilon": epsilon,
            "definition": "d_C=sum_(i in C) epsilon_i*u_i",
            "membership": (
                "d_C in M because epsilon is integral and has coordinate "
                "sum zero; hence d_C in L"
            ),
            "cycle_gram_u": [
                [str(entry) for entry in row] for row in gram_u
            ],
            "gram_times_epsilon": [str(entry) for entry in image],
            "norm_d": int(norm_d),
            "primitive_in_L": True,
            "primitive_reason": (
                "d_C=k*e in even L would make 20/k^2 an even integer; "
                "no integer k>1 does"
            ),
            "divisibility_in_L": 1,
            "divisibility_reason": (
                "div_L(d_C) divides 20; if it exceeded one, d_C/s would "
                "give nontrivial order prime to 7 in the 7-elementary "
                "group L*/L, or contradict primitivity"
            ),
        },
        "markings": {
            "K": {
                "vector": "b_C=sqrt(7)*d_C in K",
                "membership_reason": "d_C in L subset L* and K=sqrt(7)L*",
                "norm": int(norm_b),
                "ordinary_scalar_Jacobi_index": int(index_k),
                "primitive": True,
                "divisibility": 7,
                "pairing": (
                    "for x=sqrt(7)y in K, <x,b_C>=7*sum epsilon_i*t_i"
                ),
            },
            "L_Fricke_partner": {
                "vector": "d_C in L",
                "norm": int(norm_d),
                "ordinary_scalar_Jacobi_index": int(index_l),
                "primitive": True,
                "divisibility": 1,
            },
            "comparison_to_wave116": {
                "old_vector": "h_C=sum epsilon_i*g_i=3*b_C",
                "old_norm": int(old_norm_h),
                "old_K_index": old_norm_h // 2,
                "old_L_index": (old_norm_h // 7) // 2,
                "index_reduction_factor": 9,
            },
        },
        "Fricke_Poisson": {
            "raw_rank28_formula": (
                "Phi_K(-1/(7tau),z/(7tau)) = "
                "-7^8*tau^22*exp(20*pi*i*z^2/tau)*Phi_L(tau,z)"
            ),
            "normalized_rank28_formula": "Phi_K||W_7=-7^-3*Phi_L",
            "index_change": "70 on K to 10 on L",
            "scalar_specialization": (
                "at z=0 this is the verified q=16 scalar Fricke relation"
            ),
        },
        "incidence_coefficient": {
            "ell": "sum epsilon_i*t_i",
            "short_coordinate_alphabet": "{0,+1,-1} at norms 14,16,18",
            "equivalence": "ell=4 iff t_C=(1,-1,1,-1)",
            "K_Fourier_exponent": 28,
            "target": "[q^7 zeta^28]+[q^8 zeta^28]+[q^9 zeta^28]",
            "counts": "antipodal alternating C4 incidences",
            "rank28_lower": target_antipodal,
            "sufficient_upper_for_contradiction": 51975,
            "gap": 837,
            "q10_warning": (
                "the coefficient at q^10 is a valid Jacobi coefficient, "
                "but ell=4 is not proved to isolate the alternating unit "
                "pattern there under the frozen inputs"
            ),
        },
        "theta_decomposition": {
            "K_naive_residue_count": 2 * index_k,
            "K_pairing_divisibility": 7,
            "K_live_residues": [7 * s for s in range(20)],
            "reduced_component_count": 20,
            "after_z_to_minus_z_symmetry": 11,
            "K_basis_identity": (
                "theta_(70,7s)(tau,z)=theta_(10,s)(7tau,7z)"
            ),
            "L_basis": "theta_(10,t)(tau,z), t mod 20",
            "theta_S_formula": (
                "theta_(10,s)(-1/tau,z/tau)=sqrt(-i*tau/20)"
                "*exp(20*pi*i*z^2/tau)"
                "*sum_t exp(-pi*i*s*t/10)*theta_(10,t)(tau,z)"
            ),
            "component_weight": "43/2",
            "Fricke_component_equation_rank28": (
                "sqrt(-i*tau/20)*sum_s exp(-pi*i*s*t/10)"
                "*H_s(-1/(7tau)) = -7^8*tau^22*G_t(tau)"
            ),
        },
        "support": {
            "condition": "4*70*n-r^2>=0",
            "target_r": 28,
            "margins": {str(n): value for n, value in support.items()},
            "all_q7_through_q10_targets_permitted": True,
        },
        "truncated_coefficient_cone": {
            "constraints_checked": [
                "nonnegative integer coefficients",
                "c(n,r)=c(n,-r)",
                "r is divisible by 7",
                "4*70*n-r^2>=0",
                "sum_r c(n,r)=2079*x_n",
                "x7=5868,x8=x9=0 from the verified scalar formal control",
            ],
            "explicit_control": truncated_coefficients,
            "q7_row_total": row_total_q7,
            "target_coefficient_sum": target_antipodal,
            "exceeds_contradiction_threshold": True,
            "interpretation": (
                "elementary theta-decomposition support and positivity do "
                "not prove the needed upper bound"
            ),
            "not_claimed": (
                "this truncated table is not a Jacobi form, lattice, graph, "
                "or all-orders Fricke-compatible component vector"
            ),
        },
        "basis_LP_assessment": {
            "proof_producing_full_basis_constructed": False,
            "exact_reduction_achieved": (
                "the modular problem is reduced from the Wave116 "
                "four-variable determinant 1023942465 to 20 Fourier "
                "components, or 11 after evenness"
            ),
            "remaining_requirements": [
                "construct the weight-43/2 20-component K/L Fricke module",
                "prove a coefficient truncation or Sturm/valence bound",
                "impose componentwise lattice positivity on both sides",
                "derive an exact dual upper certificate at most 51975",
            ],
            "upper_bound_proved": False,
        },
        "boundary": {
            "rank28_excluded": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "The truncated coefficient control is not a Jacobi form.",
            "No complete half-integral-weight component basis is constructed.",
            "The q10 coefficient has no frozen exact incidence interpretation.",
            "No automorphism is assumed by summing one marking per C4.",
        ],
    }


def verify_results(result: dict[str, object]) -> None:
    if result != build_results():
        raise AssertionError("stored scalar Jacobi result differs from replay")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    result = build_results()
    if args.verify:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        verify_results(stored)
        print("wave121 scalar Jacobi replay: PASS")
        return
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()
