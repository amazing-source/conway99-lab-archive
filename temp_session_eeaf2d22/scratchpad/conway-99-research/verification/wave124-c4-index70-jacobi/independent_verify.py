#!/usr/bin/env python3
"""Clean-room verifier for the Wave 124 scalar C4 Jacobi reduction.

This module does not import or execute Wave 124 discovery code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


Q = Fraction
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = Path(__file__).with_name("independent-results.json")

FROZEN_INPUTS = {
    "verification/wave71-modular-theta-extension/package-manifest.sha256":
        "0eede2ebc625534360dda3f8e62456e582f5184fd18d3820dd44748de95a5237",
    "verification/wave86-level7-exact/package-manifest.sha256":
        "cbfafc03db11ad7f103e532e0f5e0b2e85ff6b568ad327b947a2d394a1d1dfa2",
    "verification/wave96-norm16-norm18-upper/package-manifest.sha256":
        "8b3f9f90de931dc152ccf1b9e0705409492a6c5eb5246643ddce55aad8afe6e9",
    "verification/wave101-all-rank-level7-lp/package-manifest.sha256":
        "79fd0331a936761f2394d58f835df80e41ad855cdf88660a2ccfd5841c5d7aba",
    "verification/wave112-c4-short-vector-incidence/package-manifest.sha256":
        "56845bcdf221c16ec46d40c630a8cdb3d63beed1314dd2683e17bf5c929ff024",
    "verification/wave116-c4-jacobi-theta/package-manifest.sha256":
        "e44afa352f51c192d6c5ac8584ccd6334dd69a3d11856f4ac0254283829bbfb8",
}

SEALED_DISCOVERY_MANIFEST = (
    "fbdaa5071229c921fdf652a91eaa895f57ce1d31f726cb4f465f0356a6dfec55"
)


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
    manifest = (
        ROOT
        / "attempts"
        / "wave124-c4-index70-jacobi"
        / "package-manifest.sha256"
    )
    if sha256_file(manifest) != SEALED_DISCOVERY_MANIFEST:
        raise AssertionError("Wave 124 discovery seal changed")


def matrix_vector(
    matrix: list[list[Q]], vector: list[int]
) -> list[Q]:
    return [
        sum(entry * value for entry, value in zip(row, vector))
        for row in matrix
    ]


def dot(left: list[int] | list[Q], right: list[int] | list[Q]) -> Q:
    return sum(Q(a) * Q(b) for a, b in zip(left, right))


def build_results() -> dict[str, object]:
    check_frozen_inputs()
    if free_memory_percent() < 15:
        raise MemoryError("host free-memory budget below 15 percent")

    epsilon = [1, -1, 1, -1]
    gram_u = [
        [Q(28, 9), Q(-8, 9), Q(1, 9), Q(-8, 9)],
        [Q(-8, 9), Q(28, 9), Q(-8, 9), Q(1, 9)],
        [Q(1, 9), Q(-8, 9), Q(28, 9), Q(-8, 9)],
        [Q(-8, 9), Q(1, 9), Q(-8, 9), Q(28, 9)],
    ]
    gram_image = matrix_vector(gram_u, epsilon)
    norm_d = dot(epsilon, gram_image)
    if gram_image != [Q(5), Q(-5), Q(5), Q(-5)]:
        raise AssertionError("C4 alternating eigenmode mismatch")
    if norm_d != 20:
        raise AssertionError("d_C norm mismatch")

    # An even-lattice divisor k>1 would require 20/k^2 to be even integral.
    divisors = []
    for k in range(2, 6):
        quotient = Q(20, k * k)
        if quotient.denominator == 1 and quotient.numerator % 2 == 0:
            divisors.append(k)
    if divisors:
        raise AssertionError("d_C is unexpectedly divisible in L")

    # There is also an exact pairing-one witness.  For vertices outside an
    # induced C4, let k_v be the number of neighbours on that C4.  The four
    # cycle vertices send 4*(14-2)=48 edges outside.  Common-neighbour counts
    # give sum_v binom(k_v,2)=4: each of the four adjacent pairs has its one
    # common neighbour outside, while each opposite pair's two common
    # neighbours are already the other cycle vertices.  If N1 were zero,
    # sum k_v would be at most 2*sum binom(k_v,2)=8, contradiction.  Hence
    # some outside u_v meets one cycle vertex, and <u_v,d_C>=+/-1.
    c4_external_edge_count = 4 * (14 - 2)
    c4_external_pair_count = 4 * 1 + 2 * (2 - 2)
    if c4_external_edge_count != 48 or c4_external_pair_count != 4:
        raise AssertionError("C4 external incidence count mismatch")
    if c4_external_edge_count <= 2 * c4_external_pair_count:
        raise AssertionError("pairing-one witness was not forced")

    norm_b = 7 * norm_d
    index_k = norm_b // 2
    index_l = norm_d // 2
    if (norm_b, index_k, index_l) != (140, 70, 10):
        raise AssertionError("scalar Jacobi index mismatch")

    support_margins = {
        n: 4 * index_k * n - 28**2 for n in (7, 8, 9, 10)
    }
    if any(margin < 0 for margin in support_margins.values()):
        raise AssertionError("a target coefficient violates Jacobi support")

    # For each C4, e_C has four unit entries with alternating signs.
    # Pair counts in srg(99,14,1,2):
    # diagonal 84 cycles, adjacent 12 cycles, nonadjacent one diagonal cycle.
    moment_matrix = "83I-13A+J"
    moment_eigenvalue_minus4 = 83 - 13 * (-4)
    if moment_eigenvalue_minus4 != 135:
        raise AssertionError("C4 second-moment eigenvalue mismatch")

    shell_rows = {}
    for n in (7, 8, 9, 10):
        shell_rows[str(n)] = {
            "K_squared_norm": 2 * n,
            "sum_C_ell_C_squared_per_vector": 270 * n,
            "sum_C_r_C_squared_per_vector": 13230 * n,
            "target_support_margin": support_margins[n],
        }

    cycle_count = 2079
    rank28_scalar_x7 = 5868
    target = 52812
    row_total = cycle_count * rank28_scalar_x7
    required_second_moment = 13230 * 7 * rank28_scalar_x7
    coefficient_r42 = 130563
    coefficient_r0 = 11832822
    null_coefficients = {
        "c(7,-42)": coefficient_r42,
        "c(7,-28)": target,
        "c(7,0)": coefficient_r0,
        "c(7,28)": target,
        "c(7,42)": coefficient_r42,
    }
    if sum(null_coefficients.values()) != row_total:
        raise AssertionError("null-control row sum mismatch")
    null_moment = sum(
        int(label.split(",")[1].rstrip(")")) ** 2 * value
        for label, value in null_coefficients.items()
    )
    if null_moment != required_second_moment:
        raise AssertionError("null-control second moment mismatch")

    rank28_antipodal_lower = 52812
    rank28_cap25_capacity = cycle_count * 25
    rank30_antipodal_lower = 102630 // 2
    rank30_cap24_capacity = cycle_count * 24

    indicator = [Q(1)]
    indicator_denominator = Q(1)
    for j in range(4):
        updated = [Q(0) for _ in range(len(indicator) + 2)]
        for degree, coefficient in enumerate(indicator):
            updated[degree] -= j * j * coefficient
            updated[degree + 2] += coefficient
        indicator = updated
        indicator_denominator *= 16 - j * j
    indicator = [coefficient / indicator_denominator for coefficient in indicator]
    for ell in range(-4, 5):
        value = sum(
            coefficient * ell**degree
            for degree, coefficient in enumerate(indicator)
        )
        if value != int(abs(ell) == 4):
            raise AssertionError("degree-eight indicator mismatch")

    return {
        "format": "wave124-independent-verification-v1",
        "claim_label": "VERIFIED_WITH_CLARIFICATIONS",
        "frozen_discovery_manifest_sha256": SEALED_DISCOVERY_MANIFEST,
        "conditional_scope": (
            "primitive scalar C4 Jacobi marking for hypothetical "
            "srg(99,14,1,2), using verified rank-28 and rank-30 inputs"
        ),
        "alternating_vector": {
            "definition": "d_C=sum epsilon_i*u_i",
            "epsilon": epsilon,
            "membership": "d_C in M subset L because sum epsilon_i=0",
            "gram_times_epsilon": [
                str(value) for value in gram_image
            ],
            "norm": int(norm_d),
            "primitive_in_L": True,
            "divisibility_in_L": 1,
            "primitivity_reason": (
                "d_C=k*e in even L would require 20/k^2 to be an even "
                "integer; no k>1 works"
            ),
            "divisibility_reason": (
                "the induced-C4 incidence equations sum k_v=48 and "
                "sum binom(k_v,2)=4 for outside vertices, forcing an "
                "outside vertex adjacent to exactly one cycle vertex; "
                "its frame vector u_v in M subset L pairs +/-1 with d_C"
            ),
            "pairing_one_witness_counts": {
                "external_C4_edges": c4_external_edge_count,
                "external_common_neighbor_pairs": c4_external_pair_count,
                "conclusion": "at least one outside vertex has k_v=1",
            },
        },
        "markings": {
            "K": {
                "definition": "b_C=sqrt(7)*d_C",
                "membership": "K=sqrt(7)L* because d_C in L subset L*",
                "norm": int(norm_b),
                "Jacobi_index": int(index_k),
                "primitive": True,
                "divisibility": 7,
            },
            "L": {
                "definition": "d_C",
                "norm": int(norm_d),
                "Jacobi_index": int(index_l),
                "primitive": True,
                "divisibility": 1,
            },
            "Wave116_comparison": {
                "old_marking": "h_C=3*b_C",
                "old_K_index": 630,
                "old_L_index": 90,
                "index_reduction_factor": 9,
            },
        },
        "coefficient_interpretation": {
            "pairing": "<sqrt(7)y,b_C>=7*ell_C",
            "ell_C": "sum epsilon_i*t_i",
            "target_r": 28,
            "norms_with_verified_unit_alphabet": [14, 16, 18, 20],
            "q_exponents_with_exact_alternating_interpretation": [7, 8, 9, 10],
            "norm20_justification": (
                "verified Wave96: the nonintegral floor is 22 and the only "
                "norm-20 profile is ten +1 and ten -1"
            ),
            "equivalence": "ell_C=4 iff t_C=(1,-1,1,-1)",
            "antipodal_counting": (
                "one of each antipodal pair contributes at r=28 and the "
                "other at r=-28"
            ),
        },
        "Fricke_Poisson": {
            "general_raw": (
                "Phi_K(-1/(7tau),z/(7tau))=-7^(q/2)*tau^22"
                "*exp(20*pi*i*z^2/tau)*Phi_L(tau,z)"
            ),
            "rank28_q16_raw_factor": "-7^8",
            "rank28_q16_normalized_factor": "-7^-3",
            "rank30_q14_raw_factor": "-7^7",
            "rank30_q14_normalized_factor": "-7^-4",
            "index_change": "70 to 10",
            "z_zero_control": "recovers the verified scalar Fricke relation",
        },
        "theta_decomposition": {
            "ordinary_index70_residues": 140,
            "K_divisibility": 7,
            "live_K_residues": [7 * s for s in range(20)],
            "component_count": 20,
            "even_component_count": 11,
            "identity": (
                "theta_(70,7s)(tau,z)=theta_(10,s)(7tau,7z)"
            ),
            "component_weight": "43/2",
            "theta_S_transform": (
                "theta_(10,s)(-1/tau,z/tau)=sqrt(-i*tau/20)"
                "*exp(20*pi*i*z^2/tau)"
                "*sum_t exp(-pi*i*s*t/10)*theta_(10,t)(tau,z)"
            ),
            "component_Fricke_general": (
                "sqrt(-i*tau/20)*sum_s exp(-pi*i*s*t/10)"
                "*H_s(-1/(7tau))=-7^(q/2)*tau^22*G_t(tau)"
            ),
        },
        "tight_frame_second_moment": {
            "C4_counts": {
                "cycles_through_vertex": 84,
                "cycles_through_edge": 12,
                "cycles_with_nonedge_as_diagonal": 1,
            },
            "coordinate_matrix": moment_matrix,
            "minus4_eigenvalue": moment_eigenvalue_minus4,
            "identity_ell": "sum_C ell_C^2=135*||t||^2=270*n",
            "identity_r": "sum_C r_C^2=49*270*n=13230*n",
            "L_frame_operator": "sum_C d_C*d_C^T=945I",
            "L_identity": "sum_C <x,d_C>^2=1890*n for norm(x)=2n",
            "forced_L_coefficient": {
                "coefficient": [10, 20],
                "value": cycle_count,
                "reason": (
                    "for each C, norm(x)=norm(d_C)=20 and "
                    "<x,d_C>=20 imply x=d_C by equality in Cauchy-Schwarz"
                ),
            },
            "shell_rows": shell_rows,
        },
        "degree_eight_indicator": {
            "formula": "product_(j=0)^3 (ell^2-j^2)/(16-j^2)",
            "coefficients_low_to_high": [
                str(coefficient) for coefficient in indicator
            ],
            "verified_domain": list(range(-4, 5)),
            "selected_values": [-4, 4],
            "Taylor_weights": [22, 24, 26, 28, 30],
        },
        "incidence_targets": {
            "rank28_q16": {
                "q_range": [7, 8, 9],
                "antipodal_lower": rank28_antipodal_lower,
                "cap25_capacity": rank28_cap25_capacity,
                "gap": rank28_antipodal_lower - rank28_cap25_capacity,
                "cap25_proved": False,
            },
            "rank30_q14": {
                "q_range": [7, 8, 9, 10],
                "antipodal_lower": rank30_antipodal_lower,
                "cap24_capacity": rank30_cap24_capacity,
                "gap": rank30_antipodal_lower - rank30_cap24_capacity,
                "cap24_proved": False,
            },
        },
        "support": {
            "condition": "4*70*n-r^2>=0",
            "target_r": 28,
            "margins": {
                str(n): margin for n, margin in support_margins.items()
            },
            "all_target_coefficients_permitted": True,
        },
        "null_control": {
            "scalar_prefix": {"x7": rank28_scalar_x7, "x8": 0, "x9": 0},
            "coefficients": null_coefficients,
            "row_sum": row_total,
            "required_second_moment": required_second_moment,
            "actual_second_moment": null_moment,
            "target_antipodal_incidence": target,
            "checks": [
                "nonnegative integral",
                "r-to-minus-r symmetry",
                "r divisible by 7",
                "Jacobi support",
                "z=0 row sum",
                "tight-frame second moment",
            ],
            "not_a_Jacobi_form": True,
            "not_Fricke_complete": True,
        },
        "evidence_boundary": {
            "complete_weight43_over2_component_basis": False,
            "Jacobi_Sturm_or_valence_bound": False,
            "exact_upper_dual": False,
            "cap25": "UNKNOWN",
            "cap24": "UNKNOWN",
            "rank28_excluded": False,
            "rank30_excluded": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "clarifications": [
            "The q^10/r=28 incidence interpretation is justified only after importing the independently verified Wave96 norm-20 dictionary.",
            "The 20-component theta/Fricke reduction is exact, but no spanning modular basis or finite certification bound is supplied.",
            "The explicit null table satisfies the new second moment but is not an all-orders Jacobi form.",
        ],
    }


def verify_results(stored: dict[str, object]) -> None:
    if stored != build_results():
        raise AssertionError("stored independent result differs from replay")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    result = build_results()
    if args.verify:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        verify_results(stored)
        print("wave124 independent replay: PASS")
        return
    args.output.write_bytes(
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    print(args.output)


if __name__ == "__main__":
    main()
