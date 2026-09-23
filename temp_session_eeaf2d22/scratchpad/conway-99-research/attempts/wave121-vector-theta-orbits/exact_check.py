#!/usr/bin/env python3
"""Exact orbit-aggregate theta feasibility checks for Wave 121.

This is a discovery package.  It uses only full finite-quadratic-space
orbit sums; it never assumes that an abstract discriminant-form
automorphism lifts to a lattice or graph automorphism.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from fractions import Fraction
from pathlib import Path
from types import ModuleType


Q = Fraction
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = Path(__file__).with_name("exact-results.json")
MAX_K_INDEX = 11
MAX_L_INDEX = 7 * MAX_K_INDEX

FROZEN_INPUTS = {
    "verification/wave66-spherical-code-shift/package-manifest.sha256":
        "a6051ebcfccab0fc9b3f9698f0024cc3284549f5148c9a12a4c6bbe08c786486",
    "verification/wave80-f7-overlattice-code/package-manifest.sha256":
        "25129c86f97c8f9513eff04ada641c458b924f8edd583e6e6abc76d114c64077",
    "verification/wave86-level7-exact/package-manifest.sha256":
        "cbfafc03db11ad7f103e532e0f5e0b2e85ff6b568ad327b947a2d394a1d1dfa2",
    "verification/wave97-f7-exterior-matroid/package-manifest.sha256":
        "e7cdd56b40a385ffff42dcdf66f0a0f5b54f60af8472d6a9a9718f7209114992",
    "verification/wave101-all-rank-level7-lp/package-manifest.sha256":
        "79fd0331a936761f2394d58f835df80e41ad855cdf88660a2ccfd5841c5d7aba",
    "attempts/wave86-level7-exact/package-manifest.sha256":
        "c6066fd10258578c15e511f3802217e4ff613ffe3d3b3b8f11e804f0316ac75d",
    "attempts/wave101-all-rank-level7-lp/package-manifest.sha256":
        "54d620a8644d7efe5d2e418869b035331127862c2125ef3da325272417307619",
}

# Variables are z=(x7,...,x13); x14 is eliminated by y0=1.
PREFIX20_WITNESS = (
    Q(389888, 57),
    Q(0),
    Q(0),
    Q(0),
    Q(1495218928, 57),
    Q(2126104904, 57),
    Q(6854397536, 19),
)
PREFIX22_WITNESS = (
    Q(0),
    Q(1219920912, 9307),
    Q(3455785984, 9307),
    Q(0),
    Q(0),
    Q(1013289561144, 9307),
    Q(3477251342208, 9307),
)
MIN_X10_WITNESS = (
    Q(0),
    Q(0),
    Q(0),
    Q(2729216),
    Q(9904496),
    Q(64688008),
    Q(374547488),
)
MIN_X10_X11_WITNESS = (
    Q(0),
    Q(0),
    Q(0),
    Q(4144144),
    Q(0),
    Q(83082072),
    Q(383037056),
)


def free_memory_percent() -> float:
    """Return available physical-memory percentage."""

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


def load_module(name: str, relative: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise ImportError(relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fraction_text(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def evaluate(form: tuple[Q, list[Q]], witness: tuple[Q, ...]) -> Q:
    constant, linear = form
    return constant + sum(a * z for a, z in zip(linear, witness))


def subtract(
    left: tuple[Q, list[Q]], right: tuple[Q, list[Q]]
) -> tuple[Q, list[Q]]:
    return (
        left[0] - right[0],
        [a - b for a, b in zip(left[1], right[1])],
    )


def build_affine_series() -> tuple[
    list[tuple[Q, list[Q]]],
    list[tuple[Q, list[Q]]],
    list[tuple[int, str, int, str]],
]:
    """Extend the frozen 15-dimensional modular pair exactly through y77."""

    if free_memory_percent() < 15.0:
        raise MemoryError("host free-memory budget below 15 percent")

    wave86 = load_module(
        "wave121_wave86",
        "attempts/wave86-level7-exact/exact_check.py",
    )
    wave101 = load_module(
        "wave121_wave101",
        "attempts/wave101-all-rank-level7-lp/exact_lp.py",
    )

    wave86.PRECISION = MAX_L_INDEX
    wave86.SERIES = {
        (weight, orientation): wave86.eisenstein(weight, orientation)
        for weight in range(3, 20, 2)
        for orientation in "AB"
    }
    basis = wave86.independent_basis()
    if len(basis) != 15:
        raise AssertionError("frozen modular basis no longer has rank 15")

    coefficient_matrix = [
        [wave86.product_series(form)[n] for form in basis]
        for n in range(15)
    ]
    inverse = wave86.invert(coefficient_matrix)
    fricke_images = []
    for n in range(15):
        row = []
        for form in basis:
            factor, image = wave86.fricke_image(form)
            row.append(factor * wave86.product_series(image)[n])
        fricke_images.append(row)
    fricke = wave86.matmul(fricke_images, inverse)
    y_prefix, y_prefix_linear, x14_constant, x14_linear = (
        wave101.affine_pair(fricke, 14)
    )

    x_prefix_constants = [Q(0)] * 15
    x_prefix_linear = [[Q(0)] * 7 for _ in range(15)]
    x_prefix_constants[0] = Q(1)
    for j in range(7):
        x_prefix_linear[7 + j][j] = Q(1)
    x_prefix_constants[14] = x14_constant
    x_prefix_linear[14] = x14_linear

    modular_constants = [
        sum(inverse[i][j] * x_prefix_constants[j] for j in range(15))
        for i in range(15)
    ]
    modular_linear = [
        [
            sum(inverse[i][k] * x_prefix_linear[k][j] for k in range(15))
            for j in range(7)
        ]
        for i in range(15)
    ]

    def coefficient(n: int, fricke_side: bool) -> tuple[Q, list[Q]]:
        values = []
        for form in basis:
            if fricke_side:
                factor, image = wave86.fricke_image(form)
                values.append(factor * wave86.product_series(image)[n])
            else:
                values.append(wave86.product_series(form)[n])
        scale = Q(-(7**4)) if fricke_side else Q(1)
        constant = scale * sum(
            values[i] * modular_constants[i] for i in range(15)
        )
        linear = [
            scale
            * sum(values[i] * modular_linear[i][j] for i in range(15))
            for j in range(7)
        ]
        return constant, linear

    x = [coefficient(n, False) for n in range(15)]
    y = [coefficient(n, True) for n in range(MAX_L_INDEX + 1)]
    if x[0] != (Q(1), [Q(0)] * 7):
        raise AssertionError("Theta_K constant term changed")
    if y[0] != (Q(1), [Q(0)] * 7):
        raise AssertionError("Theta_L constant term changed")
    for n in range(15):
        if y[n] != (y_prefix[n], y_prefix_linear[n]):
            raise AssertionError(f"Fricke prefix mismatch at y{n}")
    return x, y, basis


def orbit_counts(dimension: int) -> dict[str, int]:
    """Counts for an even-dimensional minus-type quadratic space over F7."""

    if dimension % 2:
        raise ValueError("dimension must be even")
    field = 7
    half = dimension // 2
    total_isotropic = field ** (dimension - 1) - (
        (field - 1) * field ** (half - 1)
    )
    each_nonzero_value = (
        field ** (dimension - 1) + field ** (half - 1)
    )
    result = {
        "zero": 1,
        "nonzero_isotropic": total_isotropic - 1,
        "each_exact_nonzero_value": each_nonzero_value,
        "all_six_nonzero_values": 6 * each_nonzero_value,
        "total": field**dimension,
    }
    if sum(
        (
            result["zero"],
            result["nonzero_isotropic"],
            result["all_six_nonzero_values"],
        )
    ) != result["total"]:
        raise AssertionError("quadratic orbit counts do not sum")
    return result


def feasibility(
    witness: tuple[Q, ...],
    x: list[tuple[Q, list[Q]]],
    y: list[tuple[Q, list[Q]]],
) -> dict[str, object]:
    x_values = {n: evaluate(x[n], witness) for n in range(7, 15)}
    y_values = {
        n: evaluate(y[n], witness) for n in range(1, MAX_L_INDEX + 1)
    }
    k_discriminant_isotropic = {
        n: y_values[7 * n] - (Q(0) if n < 7 else x_values[n])
        for n in range(1, MAX_K_INDEX + 1)
    }
    l_discriminant_isotropic = {
        m: x_values[7 * m] - y_values[m] for m in (1, 2)
    }
    all_values = (
        list(x_values.values())
        + list(y_values.values())
        + list(k_discriminant_isotropic.values())
        + list(l_discriminant_isotropic.values())
    )
    return {
        "all_extended_coefficients_nonnegative": all(v >= 0 for v in all_values),
        "all_extended_coefficients_integral": all(
            v.denominator == 1 for v in all_values
        ),
        "all_nonconstant_coefficients_even": all(
            v.denominator == 1 and v.numerator % 2 == 0 for v in all_values
        ),
        "x7_to_x14": {
            f"x{n}": fraction_text(x_values[n]) for n in range(7, 15)
        },
        "selected_y": {
            f"y{n}": fraction_text(y_values[n])
            for n in (1, 2, 3, 4, 5, 7, 14, 49, 56, 63, 70, 77)
        },
        "minimum_y1_to_y77": fraction_text(min(y_values.values())),
        "K_discriminant_nonzero_isotropic_y7n_minus_xn": {
            str(n): fraction_text(value)
            for n, value in k_discriminant_isotropic.items()
        },
        "L_discriminant_nonzero_isotropic_x7m_minus_ym": {
            str(m): fraction_text(value)
            for m, value in l_discriminant_isotropic.items()
        },
    }


def restricted_identity(
    target_constant: Q,
    target_linear: list[Q],
    terms: list[tuple[Q, tuple[Q, list[Q]]]],
) -> bool:
    """Check an affine identity after imposing x7=x8=x9=0."""

    rhs_constant = sum(multiplier * form[0] for multiplier, form in terms)
    rhs_linear = [
        sum(multiplier * form[1][j] for multiplier, form in terms)
        for j in range(7)
    ]
    return (
        rhs_constant == target_constant
        and rhs_linear[3:] == target_linear[3:]
    )


def build_results() -> dict[str, object]:
    check_frozen_inputs()
    x, y, basis = build_affine_series()

    prefix20 = feasibility(PREFIX20_WITNESS, x, y)
    prefix22 = feasibility(PREFIX22_WITNESS, x, y)
    min_x10 = feasibility(MIN_X10_WITNESS, x, y)
    min_x10_x11 = feasibility(MIN_X10_X11_WITNESS, x, y)
    for control in (prefix20, prefix22, min_x10, min_x10_x11):
        if not control["all_extended_coefficients_nonnegative"]:
            raise AssertionError("an advertised exact control is infeasible")

    x10_identity = restricted_identity(
        Q(-2729216),
        [Q(0), Q(0), Q(0), Q(1), Q(0), Q(0), Q(0)],
        [
            (Q(440363), y[1]),
            (Q(32536), y[2]),
            (Q(1715), y[3]),
            (Q(49), y[4]),
        ],
    )
    x10_x11_identity = restricted_identity(
        Q(-4144144),
        [Q(0), Q(0), Q(0), Q(1), Q(1), Q(0), Q(0)],
        [
            (Q(6, 7), (Q(0), [Q(0), Q(0), Q(0), Q(0), Q(1), Q(0), Q(0)])),
            (Q(280574), y[1]),
            (Q(13377), y[2]),
            (Q(343), y[3]),
        ],
    )
    if not x10_identity or not x10_x11_identity:
        raise AssertionError("restricted exact forcing identity failed")

    d_l = orbit_counts(14)
    d_k = orbit_counts(30)
    code_fiber = 7**30
    anisotropic_codeword_upper = (
        code_fiber * d_l["each_exact_nonzero_value"]
    )

    return {
        "format": "wave121-vector-theta-orbits-v1",
        "claim_label": "DERIVED",
        "scope": (
            "conditional q=14, rank_F7(S)=30 row of a hypothetical "
            "srg(99,14,1,2); exact orbit-aggregate theta feasibility "
            "through K norm 22 and the dual coefficients needed through y77"
        ),
        "frozen_inputs": FROZEN_INPUTS,
        "quadratic_spaces": {
            "L_discriminant": {
                "group": "(Z/7)^14",
                "orthogonal_type": "O^-(14,7)",
                "orbit_counts": d_l,
            },
            "K_discriminant": {
                "group": "(Z/7)^30",
                "orthogonal_type": "O^-(30,7)",
                "orbit_counts": d_k,
            },
            "justified_reduction": (
                "aggregate by exact quadratic value; zero is kept separate "
                "from nonzero isotropic; no componentwise equality and no "
                "lift of an abstract orthogonal isometry is assumed"
            ),
            "projective_reduction_rejected": (
                "exact quadratic values and the Wave80 coordinate "
                "compositions at norms 14,16,18 are retained"
            ),
        },
        "orbit_theta_dictionary": {
            "L_discriminant_nonzero_isotropic": (
                "[q^(7m)] = x_(7m)-y_m, from K/(sqrt(7)L)"
            ),
            "K_discriminant_nonzero_isotropic": (
                "[q^n] = y_(7n)-x_n, from K*/K"
            ),
            "anisotropic_components": (
                "exact residue dissections of Theta_K or Theta_L(tau/7); "
                "their aggregate nonnegativity is ordinary coefficient "
                "nonnegativity"
            ),
            "new_exact_inequalities_checked": [
                "x7-y1>=0",
                "x14-y2>=0",
                "y_(7n)-x_n>=0 for 1<=n<=11, with x_n=0 for 1<=n<=6",
            ],
        },
        "seven_variable_model": {
            "variables": ["x7", "x8", "x9", "x10", "x11", "x12", "x13"],
            "eliminated": "x14 via y0=1",
            "constraints": [
                "x7,...,x14>=0",
                "y1,...,y77>=0",
                "x7-y1>=0 and x14-y2>=0",
                "y_(7n)-x_n>=0 for 1<=n<=11",
            ],
            "integral_lattice_refinement": (
                "all displayed theta and orbit coefficients are required "
                "to be nonnegative even integers"
            ),
            "modular_basis_dimension": len(basis),
        },
        "prefix_bounds": {
            "through_norm_20": {
                "exact_optimum": "389888/57",
                "even_lattice_lower_bound": 6842,
                "unchanged_from_verified_wave101": True,
                "reason": (
                    "the verified Wave101 dual remains valid and its exact "
                    "primal optimizer satisfies every added orbit constraint"
                ),
                "extended_primal_control": prefix20,
            },
            "through_norm_22": {
                "exact_optimum": "4675706896/9307",
                "even_lattice_lower_bound": 502388,
                "unchanged_from_verified_wave101": True,
                "reason": (
                    "the verified Wave101 dual remains valid and its exact "
                    "primal optimizer satisfies every added orbit constraint"
                ),
                "extended_primal_control": prefix22,
            },
        },
        "conditional_no_norm_14_16_18": {
            "assumption": "x7=x8=x9=0",
            "x10_lower_bound": {
                "value": 2729216,
                "identity": (
                    "x10-2729216 = 440363*y1 + 32536*y2 "
                    "+ 1715*y3 + 49*y4"
                ),
                "identity_exact": x10_identity,
                "attaining_extended_control": min_x10,
            },
            "x10_plus_x11_lower_bound": {
                "value": 4144144,
                "identity": (
                    "x10+x11-4144144 = (6/7)*x11 + 280574*y1 "
                    "+ 13377*y2 + 343*y3"
                ),
                "identity_exact": x10_x11_identity,
                "attaining_extended_rational_control": min_x10_x11,
                "integrality_warning": (
                    "the exact rational optimum has fractional y "
                    "coefficients and is not parity-rounded here"
                ),
            },
            "formal_even_integral_null_control": min_x10,
            "interpretation": (
                "the formal model can move all forced mass beyond norm 18; "
                "it then forces millions of norm-20/22 vectors but remains "
                "exactly feasible"
            ),
        },
        "coordinate_and_code_boundary": {
            "known_frozen_compositions": [
                {
                    "K_norm": 14,
                    "evaluation_symbols": "seven 3, seven 4, eighty-five 0",
                    "code_self_dot_mod7": 0,
                },
                {
                    "K_norm": 16,
                    "evaluation_symbols": "eight 3, eight 4, eighty-three 0",
                    "code_self_dot_mod7": 4,
                },
                {
                    "K_norm": 18,
                    "evaluation_symbols": "nine 3, nine 4, eighty-one 0",
                    "code_self_dot_mod7": 1,
                },
            ],
            "norm20": {
                "code_self_dot_mod7": 5,
                "coordinate_composition": "UNKNOWN_UNDER_FROZEN_INPUTS",
            },
            "norm22": {
                "code_self_dot_mod7": 2,
                "coordinate_composition": "UNKNOWN_UNDER_FROZEN_INPUTS",
            },
            "abstract_anisotropic_codeword_upper_each_exact_value": (
                anisotropic_codeword_upper
            ),
            "upper_bound_formula": (
                "7^30*(7^13+7^6), using radical fibers of C -> C/R"
            ),
            "upper_bound_contradiction": False,
            "warning": (
                "the abstract quotient does not determine Hamming or signed "
                "coordinate composition at norms 20 or 22; those shells "
                "are not merged or interpreted as graph eigenvectors here"
            ),
        },
        "boundary": {
            "formal_even_integral_null_through_norm_22": True,
            "positive_forcing_beyond_norm18": True,
            "new_upper_certificate": False,
            "rank30_excluded": False,
            "graph_or_lattice_constructed": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Discovery cannot verify itself; independent verification is required.",
            "Orbit sums are necessary aggregate data, not individual coset theta series.",
            "No graph automorphism or lattice automorphism is assumed.",
            "The finite model checks y coefficients only through y77.",
            "The even integral control is a formal modular/orbit prefix, not a lattice.",
            "No coordinate classification at norms 20 or 22 is imported or claimed.",
        ],
    }


def verify_results(result: dict[str, object]) -> None:
    fresh = build_results()
    if result != fresh:
        raise AssertionError("stored result differs from exact recomputation")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    result = build_results()
    if args.verify:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        verify_results(stored)
        print("wave121 exact replay: PASS")
        return
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()
