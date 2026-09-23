#!/usr/bin/env python3
"""Exact Wave57 star-complement and spectral-compression checks.

Only the Python standard library is used.  The output is a necessary-condition
ledger and a collection of scalar controls, not a graph construction.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "exact-results.json"
MIN_FREE_MEMORY_PERCENT = Fraction(15, 1)

FROZEN_INPUTS = {
    "attempts/wave35-n3-4158-combinatorial/exact-results.json":
        "07e1469e7690bd630385e734d387fa13a1eb537f0c578bf31270c3b7b8824b67",
    "attempts/wave35-n3-upper-spectral/exact-results.json":
        "ca1df07bede11642fb1639a2ae554c1a31ce9a58424d5b3e5031c90ad550a194",
    "verification/wave35-n3-upper-spectral/independent-results.json":
        "c704d8fce8f1d5975204b9a06ada0098c66fbdb9e0de8016a1ff89d86e691305",
    "verification/wave35-n3-upper-spectral/audit.md":
        "5300d965a23846e2549196e9a5c207047ee268579f60e5d3c5133c092d1a287b",
}

ROOTS = (-3, -2, -1, 0, 1, 2)

# Counts are in ROOTS order.  These are scalar spectra only.
INTEGER_CONTROLS = {
    (18, 8): (11, 2, 4, 7, 7, 2),
    (18, 9): (7, 7, 4, 2, 11, 1),
    (18, 10): (3, 13, 0, 3, 11, 1),
    (18, 11): (0, 15, 2, 0, 12, 1),
    (18, 12): (0, 8, 10, 3, 4, 4),
    (18, 13): (0, 0, 22, 0, 0, 6),
    (19, 8): (12, 0, 3, 11, 6, 0),
    (19, 9): (9, 2, 5, 8, 7, 0),
    (19, 10): (5, 8, 1, 9, 7, 0),
    (19, 11): (2, 10, 3, 6, 8, 0),
    (19, 12): (0, 9, 7, 5, 6, 1),
    (19, 13): (0, 1, 19, 2, 2, 3),
    (20, 10): (8, 0, 4, 17, 0, 0),
    (20, 11): (4, 6, 0, 18, 0, 0),
    (20, 12): (1, 8, 2, 15, 1, 0),
    (20, 13): (0, 2, 16, 4, 4, 0),
}

# A monic quadratic x^2 - s*x + p contributes its two conjugate roots.
QUADRATIC_CONTROLS = {
    (20, 8): {
        "linear_counts": (4, 4, 0, 15, 0, 0),
        "quadratic": {"s": -4, "p": 1, "multiplicity": 4},
    },
    (20, 9): {
        "linear_counts": (3, 0, 4, 14, 1, 0),
        "quadratic": {"s": -5, "p": 5, "multiplicity": 4},
    },
}


class MemoryStatusEx(ctypes.Structure):
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


def free_memory_percent() -> Fraction:
    """Return physical-memory availability as an exact percentage."""
    if os.name == "nt":
        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return Fraction(100 * status.ullAvailPhys, status.ullTotalPhys)
    if hasattr(os, "sysconf"):
        pages = os.sysconf("SC_AVPHYS_PAGES")
        total = os.sysconf("SC_PHYS_PAGES")
        return Fraction(100 * pages, total)
    raise RuntimeError("No standard-library memory query for this platform")


def require_memory_headroom() -> None:
    available = free_memory_percent()
    if available < MIN_FREE_MEMORY_PERCENT:
        raise RuntimeError(
            f"free physical memory {float(available):.2f}% is below 15%"
        )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_frozen_inputs() -> None:
    for relative, expected in FROZEN_INPUTS.items():
        actual = sha256(ROOT / relative)
        assert actual == expected, (relative, expected, actual)


def det2(a: int, b: int, c: int) -> int:
    return a * c - b * b


def det3(matrix: list[list[int]]) -> int:
    a, b, c = matrix[0]
    _, d, e = matrix[1]
    _, _, f = matrix[2]
    return a * (d * f - e * e) - b * (b * f - c * e) + c * (b * e - c * d)


def psd2(a: int, b: int, c: int) -> bool:
    return a >= 0 and c >= 0 and det2(a, b, c) >= 0


def psd3(matrix: list[list[int]]) -> bool:
    a, b, c = matrix[0]
    _, d, e = matrix[1]
    _, _, f = matrix[2]
    return (
        min(a, d, f) >= 0
        and det2(a, b, d) >= 0
        and det2(a, c, f) >= 0
        and det2(d, e, f) >= 0
        and det3(matrix) >= 0
    )


def mul_srg(x: tuple[Fraction, Fraction, Fraction],
            y: tuple[Fraction, Fraction, Fraction]
            ) -> tuple[Fraction, Fraction, Fraction]:
    """Multiply in Q[I,A,J], with A^2=12I-A+2J, AJ=14J, J^2=99J."""
    xi, xa, xj = x
    yi, ya, yj = y
    out_i = xi * yi + 12 * xa * ya
    out_a = xi * ya + xa * yi - xa * ya
    out_j = (
        xi * yj + xj * yi + 2 * xa * ya
        + 14 * (xa * yj + xj * ya) + 99 * xj * yj
    )
    return out_i, out_a, out_j


def projector_checks() -> dict:
    e3 = (Fraction(4, 7), Fraction(1, 7), Fraction(-2, 77))
    em4 = (Fraction(3, 7), Fraction(-1, 7), Fraction(1, 63))
    zero = (Fraction(0), Fraction(0), Fraction(0))
    assert mul_srg(e3, e3) == e3
    assert mul_srg(em4, em4) == em4
    assert mul_srg(e3, em4) == zero
    trace_e3 = 99 * (e3[0] + e3[2])
    trace_em4 = 99 * (em4[0] + em4[2])
    assert (trace_e3, trace_em4) == (54, 44)
    return {
        "E3": "(A+4I-(2/11)J)/7",
        "E_minus4": "(-A+3I+(1/9)J)/7",
        "idempotence_and_orthogonality": True,
        "ranks": {"E3": 54, "E_minus4": 44},
        "Y_block_ranks": {
            "E3": "60-mult_Y(-4)",
            "E_minus4": "60-mult_Y(3)",
        },
    }


def quotient_and_supported_sector_checks() -> dict:
    quotient = ((2, 12, 0), (1, 3, 10), (0, 6, 8))
    # det(xI-Q) = x^3 - 13x^2 - 26x + 168.
    roots = (14, 3, -4)
    for value in roots:
        assert value**3 - 13 * value**2 - 26 * value + 168 == 0
    beta_basis = ((1, -1, 0), (1, 0, -1))
    for value in (3, -4):
        assert value * (value + 1) == 12
        for beta in beta_basis:
            assert sum(beta) == 0
            alpha = tuple(value * item for item in beta)
            # T equation: lambda*alpha_i = -alpha_i + 12 beta_i.
            assert all(value * alpha[i] == -alpha[i] + 12 * beta[i]
                       for i in range(3))
            # X equation after beta_0+beta_1+beta_2=0: lambda*beta_i=alpha_i.
            assert all(value * beta[i] == alpha[i] for i in range(3))
            # Every y has two neighbours in each Xi.
            assert 2 * sum(beta) == 0
    return {
        "quotient_matrix": quotient,
        "characteristic_polynomial": "x^3-13x^2-26x+168",
        "eigenvalues": roots,
        "supported_sector": {
            "support": "U=T union X",
            "beta_condition": "beta0+beta1+beta2=0",
            "alpha_i": "lambda*beta_i",
            "equation": "lambda(lambda+1)=12",
            "eigenvalues": [3, -4],
            "dimension_each": 2,
        },
    }


def remaining_moments(a: int, b: int, c4x: int | None = None) -> list[int]:
    """Power sums p0,... for nontrivial roots other than 3 and -4."""
    result = [
        59 - a - b,
        -8 - 3 * a + 4 * b,
        416 - 9 * a - 16 * b,
        -320 - 27 * a + 64 * b,
    ]
    if c4x is not None:
        result.append(4472 + 8 * c4x - 81 * a - 256 * b)
    return result


def first_three_moment_feasible(a: int, b: int) -> bool:
    r, p1, p2, p3 = remaining_moments(a, b)
    if r < 0 or not psd2(r, p1, p2):
        return False
    # Localizers for x+4 and 3-x on the residual support (-4,3).
    plus = (p1 + 4 * r, p2 + 4 * p1, p3 + 4 * p2)
    minus = (3 * r - p1, 3 * p1 - p2, 3 * p2 - p3)
    return psd2(*plus) and psd2(*minus)


def fourth_moment_feasible(a: int, b: int, c4x: int) -> bool:
    r, p1, p2, p3, p4 = remaining_moments(a, b, c4x)
    hankel = [[r, p1, p2], [p1, p2, p3], [p2, p3, p4]]
    # g(x)=(x+4)(3-x)=12-x-x^2.
    q0 = 12 * r - p1 - p2
    q1 = 12 * p1 - p2 - p3
    q2 = 12 * p2 - p3 - p4
    assert (q0, q1, q2) == (300, -192, 840 - 8 * c4x)
    return psd3(hankel) and psd2(q0, q1, q2)


def newton_coefficients(power_sums: Iterable[int]) -> list[int]:
    p = [0] + list(power_sums)
    e = [1]
    for degree in range(1, len(p)):
        numerator = sum(
            (-1) ** (i - 1) * e[degree - i] * p[i]
            for i in range(1, degree + 1)
        )
        assert numerator % degree == 0
        e.append(numerator // degree)
    return e[1:]


def quadratic_power_sums(s: int, p: int) -> tuple[int, int, int, int, int]:
    return (
        2,
        s,
        s * s - 2 * p,
        s**3 - 3 * p * s,
        s**4 - 4 * p * s * s + 2 * p * p,
    )


def verify_scalar_control(a: int, b: int, control: dict) -> dict:
    counts = tuple(control["linear_counts"])
    sums = [sum(counts)]
    sums.extend(
        sum(count * root**power for count, root in zip(counts, ROOTS))
        for power in range(1, 5)
    )
    factor = control.get("quadratic")
    factor_text = None
    if factor:
        s, p, multiplicity = (
            factor["s"], factor["p"], factor["multiplicity"]
        )
        discriminant = s * s - 4 * p
        root_low = (s - discriminant**0.5) / 2
        root_high = (s + discriminant**0.5) / 2
        assert discriminant > 0
        assert int(discriminant**0.5) ** 2 != discriminant
        assert -4 < root_low < root_high < 3
        for index, value in enumerate(quadratic_power_sums(s, p)):
            sums[index] += multiplicity * value
        factor_text = f"(x^2-({s})x+({p}))^{multiplicity}"
    r, p1, p2, p3 = remaining_moments(a, b)
    assert sums[:4] == [r, p1, p2, p3]
    c_numerator = sums[4] + 81 * a + 256 * b - 4472
    assert c_numerator % 8 == 0
    c4x = c_numerator // 8
    assert fourth_moment_feasible(a, b, c4x)
    newton_coefficients(sums[1:])
    return {
        "a_mult_Y_3": a,
        "b_mult_Y_minus4": b,
        "linear_root_counts": dict(zip(map(str, ROOTS), counts)),
        "quadratic_factor": factor_text,
        "residual_power_sums_p0_to_p4": sums,
        "C4_X": c4x,
        "verified": True,
        "graph_realization_claimed": False,
    }


def multiplicity_and_moment_checks() -> tuple[list[dict], list[dict]]:
    # Explicit supported sectors and restriction-map ranks give a>=18,b>=8.
    candidates = []
    for a in range(18, 60):
        for b in range(8, 60):
            if first_three_moment_feasible(a, b):
                candidates.append((a, b))
    expected = [(a, b) for a in range(18, 21) for b in range(8, 14)]
    assert candidates == expected

    ledger = []
    controls = []
    for a, b in candidates:
        feasible_c = [
            c for c in range(226) if fourth_moment_feasible(a, b, c)
        ]
        assert feasible_c == list(range(min(feasible_c), max(feasible_c) + 1))
        for c in (min(feasible_c), max(feasible_c)):
            newton_coefficients(remaining_moments(a, b, c)[1:])
        ledger.append({
            "a_mult_Y_3": a,
            "b_mult_Y_minus4": b,
            "residual_degree": 59 - a - b,
            "C4_X_min": min(feasible_c),
            "C4_X_max": max(feasible_c),
            "feasible_C4_X_count": len(feasible_c),
            "minimum_U_hit_star_set_lambda3": b - 6,
            "minimum_U_hit_star_set_lambda_minus4": a - 16,
        })
        if (a, b) in INTEGER_CONTROLS:
            control = {
                "linear_counts": INTEGER_CONTROLS[(a, b)],
            }
        else:
            control = QUADRATIC_CONTROLS[(a, b)]
        controls.append(verify_scalar_control(a, b, control))
    return ledger, controls


def combinatorial_moment_checks() -> dict:
    # Triangles classified by their counts in X and Y, after fixing T.
    triangle_parts = {
        "T_itself": 1,
        "T_plus_two_X": 18,
        "three_X": 0,
        "two_X_plus_Y": 36,
        "X_plus_two_Y": 144,
        "three_Y": 32,
    }
    assert sum(triangle_parts.values()) == 231
    assert 6 * triangle_parts["three_Y"] == 192
    # Let c=C4(X).  Pair counts for nonadjacent vertices of Y by block overlap.
    for c in (0, 89, 225):
        n0, n1, n2 = 342 + 2 * c, 900 - 4 * c, 288 + 2 * c
        assert n0 + n1 + n2 == 1530
        assert n1 + 2 * n2 == 1476
        assert n0 >= 0 and n2 >= 0
        if c <= 225:
            assert n1 >= 0
        assert 171 + c == n0 // 2
        trace_a4_y = 2 * 240 + 4 * 60 * 28 + 8 * (171 + c)
        assert trace_a4_y == 8568 + 8 * c
    return {
        "Y_order_degree_edges": [60, 8, 240],
        "triangle_decomposition": triangle_parts,
        "Y_triangles": 32,
        "trace_A_Y_powers_0_to_3": [60, 0, 480, 192],
        "four_cycle_parameter": {
            "c": "C4(X)",
            "combinatorial_range": [0, 225],
            "nonadjacent_Y_pairs_by_block_overlap": {
                "0": "342+2c",
                "1": "900-4c",
                "2": "288+2c",
            },
            "C4_Y": "171+c",
            "trace_A_Y_fourth": "8568+8c",
            "moment_localizer_range": [0, 89],
        },
    }


def run_checks(write_output: bool = True) -> dict:
    require_memory_headroom()
    check_frozen_inputs()
    quotient = quotient_and_supported_sector_checks()
    projectors = projector_checks()
    combinatorics = combinatorial_moment_checks()
    ledger, controls = multiplicity_and_moment_checks()
    result = {
        "schema_version": 1,
        "role": "proof_a",
        "claim_label": "DERIVED_INCONCLUSIVE",
        "scope": (
            "conditional n3=4158 endpoint; arbitrary fixed triangle; "
            "no automorphism assumption"
        ),
        "endpoint": {
            "srg": [99, 14, 1, 2],
            "spectrum": {"14": 1, "3": 54, "-4": 44},
            "cell_sizes_T_X_Y": [3, 36, 60],
            "prism_free": True,
        },
        "quotient_and_supported_sectors": quotient,
        "projectors_and_restrictions": projectors,
        "forced_Y_multiplicities": {
            "mult_Y_3": [18, 20],
            "mult_Y_minus4": [8, 13],
            "supported_kernel_dimensions": {
                "lambda_3": "mult_Y(-4)-6",
                "lambda_minus4": "mult_Y(3)-16",
            },
            "candidate_pair_count": len(ledger),
        },
        "combinatorial_moments": combinatorics,
        "multiplicity_fourth_moment_ledger": ledger,
        "scalar_algebraic_integer_controls": controls,
        "star_complement_reduction": {
            "whole_graph_lambda_3": {
                "star_set_size": 54,
                "minimum_U_hit": "mult_Y(-4)-6 in [2,7]",
                "minimum_hit_complement_Y_count": "mult_Y(-4) in [8,13]",
                "star_complement_size": 45,
            },
            "whole_graph_lambda_minus4": {
                "star_set_size": 44,
                "minimum_U_hit": "mult_Y(3)-16 in [2,4]",
                "minimum_hit_complement_Y_count": "mult_Y(3) in [18,20]",
                "star_complement_size": 55,
            },
            "Y_only_exact_rank_problem": {
                "rank_11AY_plus_44I_minus_2J": "60-mult_Y(-4) in [47,52]",
                "rank_minus9AY_plus_27I_plus_J": "60-mult_Y(3) in [39,42]",
                "lambda_3_star_complement_orders": [40, 42],
                "lambda_minus4_star_complement_orders": [47, 52],
            },
            "reconstruction_identity": (
                "mu I-A_S = B^T (mu I-C)^(-1) B, "
                "with mu not in spectrum(C)"
            ),
        },
        "resource_guard": {
            "minimum_free_physical_memory_percent": 15,
            "checked_at_start_and_finish": True,
        },
        "conclusion": {
            "endpoint_excluded": False,
            "endpoint_graph_constructed": False,
            "smaller_exact_problem_identified": True,
            "all_18_scalar_moment_cases_have_controls": True,
            "conway_99_status": "UNKNOWN",
        },
        "limitations": [
            "The controls are algebraic-integer scalar multisets, not certified graph spectra.",
            "Truncated moment positivity is necessary, not sufficient.",
            "No binary star-complement incidence matrix is constructed.",
            "No 60-vertex Y graph or 99-vertex endpoint graph is constructed.",
            "No endpoint contradiction is obtained.",
        ],
    }
    require_memory_headroom()
    if write_output:
        OUTPUT.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return result


if __name__ == "__main__":
    checked = run_checks(write_output=True)
    print(json.dumps({
        "claim_label": checked["claim_label"],
        "candidate_pairs":
            checked["forced_Y_multiplicities"]["candidate_pair_count"],
        "controls":
            len(checked["scalar_algebraic_integer_controls"]),
        "endpoint_excluded": checked["conclusion"]["endpoint_excluded"],
        "output": str(OUTPUT),
    }, sort_keys=True))
