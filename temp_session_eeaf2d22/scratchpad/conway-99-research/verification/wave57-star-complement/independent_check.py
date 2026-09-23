#!/usr/bin/env python3
"""Clean-room exact verifier for the Wave 57 star-complement lane.

This module imports no discovery code.  It verifies the discovery artifact,
derives the stronger cubic-four-cycle bound, and compares the Wave 57
multiplicity box with the already verified Wave 36 spectral transfer.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave57-star-complement" / "exact-results.json"
PRIOR = ROOT / "verification" / "wave36-block-compatibility" / "independent-results.json"
OUTPUT = HERE / "independent-results.json"
MIN_FREE_MEMORY_PERCENT = Fraction(20, 1)
ROOTS = (-3, -2, -1, 0, 1, 2)

EXPECTED_DISCOVERY_RANGES = {
    (18, 8): (0, 89),
    (18, 9): (0, 89),
    (18, 10): (0, 89),
    (18, 11): (7, 89),
    (18, 12): (24, 89),
    (18, 13): (54, 89),
    (19, 8): (4, 89),
    (19, 9): (8, 89),
    (19, 10): (13, 89),
    (19, 11): (21, 89),
    (19, 12): (34, 89),
    (19, 13): (57, 89),
    (20, 8): (41, 89),
    (20, 9): (42, 89),
    (20, 10): (44, 89),
    (20, 11): (47, 89),
    (20, 12): (52, 89),
    (20, 13): (65, 89),
}

EXPECTED_CONTROL_QUADRATICS = {
    (20, 8): (-4, 1, 4, "(x^2-(-4)x+(1))^4"),
    (20, 9): (-5, 5, 4, "(x^2-(-5)x+(5))^4"),
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
    if os.name == "nt":
        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return Fraction(100 * status.ullAvailPhys, status.ullTotalPhys)
    pages = os.sysconf("SC_AVPHYS_PAGES")
    total = os.sysconf("SC_PHYS_PAGES")
    return Fraction(100 * pages, total)


def require_memory_headroom() -> Fraction:
    available = free_memory_percent()
    if available < MIN_FREE_MEMORY_PERCENT:
        raise RuntimeError(
            f"free physical memory {float(available):.2f}% is below 20%"
        )
    return available


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_hash_file(path: Path) -> list[tuple[str, str]]:
    records = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        digest, relative = raw.split(maxsplit=1)
        records.append((digest, relative.strip()))
    return records


def check_hash_file(path: Path) -> None:
    for expected, relative in parse_hash_file(path):
        actual = sha256(ROOT / relative)
        assert actual == expected, (relative, expected, actual)


def det2(a: int, b: int, c: int) -> int:
    return a * c - b * b


def det3_symmetric(matrix: list[list[int]]) -> int:
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
        and det3_symmetric(matrix) >= 0
    )


def mul_srg(
    x: tuple[Fraction, Fraction, Fraction],
    y: tuple[Fraction, Fraction, Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    """Multiply in Q[I,A,J], using A^2=12I-A+2J."""
    xi, xa, xj = x
    yi, ya, yj = y
    return (
        xi * yi + 12 * xa * ya,
        xi * ya + xa * yi - xa * ya,
        xi * yj
        + xj * yi
        + 2 * xa * ya
        + 14 * (xa * yj + xj * ya)
        + 99 * xj * yj,
    )


def quotient_and_sector_checks() -> dict:
    q = ((2, 12, 0), (1, 3, 10), (0, 6, 8))
    trace = sum(q[i][i] for i in range(3))
    principal_two_sum = (
        q[0][0] * q[1][1] - q[0][1] * q[1][0]
        + q[0][0] * q[2][2] - q[0][2] * q[2][0]
        + q[1][1] * q[2][2] - q[1][2] * q[2][1]
    )
    determinant = (
        q[0][0] * (q[1][1] * q[2][2] - q[1][2] * q[2][1])
        - q[0][1] * (q[1][0] * q[2][2] - q[1][2] * q[2][0])
        + q[0][2] * (q[1][0] * q[2][1] - q[1][1] * q[2][0])
    )
    assert (trace, principal_two_sum, determinant) == (13, -26, -168)
    roots = (14, 3, -4)
    for value in roots:
        assert value**3 - 13 * value**2 - 26 * value + 168 == 0

    basis = ((1, -1, 0), (1, 0, -1))
    for eigenvalue in (3, -4):
        assert eigenvalue * (eigenvalue + 1) == 12
        for beta in basis:
            assert sum(beta) == 0
            alpha = tuple(eigenvalue * value for value in beta)
            assert all(
                eigenvalue * alpha[i] == -alpha[i] + 12 * beta[i]
                for i in range(3)
            )
            assert all(eigenvalue * beta[i] == alpha[i] for i in range(3))
            assert 2 * sum(beta) == 0
    return {
        "quotient": [list(row) for row in q],
        "characteristic_polynomial_coefficients": [1, -13, -26, 168],
        "eigenvalues": list(roots),
        "supported_dimension_each": 2,
        "no_automorphism_used": True,
    }


def projector_checks() -> dict:
    e3 = (Fraction(4, 7), Fraction(1, 7), Fraction(-2, 77))
    em4 = (Fraction(3, 7), Fraction(-1, 7), Fraction(1, 63))
    zero = (Fraction(), Fraction(), Fraction())
    assert mul_srg(e3, e3) == e3
    assert mul_srg(em4, em4) == em4
    assert mul_srg(e3, em4) == zero
    assert 99 * (e3[0] + e3[2]) == 54
    assert 99 * (em4[0] + em4[2]) == 44
    # The regular direction is not in either Y-block kernel.
    assert Fraction(8 + 4, 7) - Fraction(2 * 60, 77) == Fraction(12, 77)
    assert Fraction(-8 + 3, 7) + Fraction(60, 63) == Fraction(5, 21)
    return {
        "E3": "(A+4I-(2/11)J)/7",
        "E_minus4": "(-A+3I+(1/9)J)/7",
        "ranks": {"E3": 54, "E_minus4": 44},
        "Y_block_ranks": {
            "E3": "60-b",
            "E_minus4": "60-a",
        },
        "supported_dimensions": {
            "lambda_3": "b-6",
            "lambda_minus4": "a-16",
        },
    }


def remaining_moments(a: int, b: int, c4x: int | None = None) -> list[int]:
    moments = [
        59 - a - b,
        -8 - 3 * a + 4 * b,
        416 - 9 * a - 16 * b,
        -320 - 27 * a + 64 * b,
    ]
    if c4x is not None:
        moments.append(4472 + 8 * c4x - 81 * a - 256 * b)
    return moments


def first_three_feasible(a: int, b: int) -> bool:
    p0, p1, p2, p3 = remaining_moments(a, b)
    if p0 < 0 or not psd2(p0, p1, p2):
        return False
    lower = (p1 + 4 * p0, p2 + 4 * p1, p3 + 4 * p2)
    upper = (3 * p0 - p1, 3 * p1 - p2, 3 * p2 - p3)
    return psd2(*lower) and psd2(*upper)


def fourth_feasible(a: int, b: int, c4x: int) -> bool:
    p0, p1, p2, p3, p4 = remaining_moments(a, b, c4x)
    hankel = [[p0, p1, p2], [p1, p2, p3], [p2, p3, p4]]
    localizer = (
        12 * p0 - p1 - p2,
        12 * p1 - p2 - p3,
        12 * p2 - p3 - p4,
    )
    assert localizer == (300, -192, 840 - 8 * c4x)
    return psd3(hankel) and psd2(*localizer)


def newton_coefficients(power_sums: Iterable[int]) -> list[int]:
    p = [0] + list(power_sums)
    elementary = [1]
    for degree in range(1, len(p)):
        numerator = sum(
            (-1) ** (index - 1)
            * elementary[degree - index]
            * p[index]
            for index in range(1, degree + 1)
        )
        assert numerator % degree == 0
        elementary.append(numerator // degree)
    return elementary[1:]


def quadratic_power_sums(s: int, p: int) -> tuple[int, ...]:
    return (
        2,
        s,
        s * s - 2 * p,
        s**3 - 3 * p * s,
        s**4 - 4 * p * s * s + 2 * p * p,
    )


def exact_quadratic_interval_check(s: int, p: int) -> None:
    discriminant = s * s - 4 * p
    assert discriminant > 0
    assert not any(root * root == discriminant for root in range(discriminant + 1))
    # For the two actual controls these exact inequalities are equivalent to
    # both roots lying strictly in (-4,3).
    assert -8 < s < 6
    assert 16 + 4 * s + p > 0  # f(-4)>0
    assert 9 - 3 * s + p > 0   # f(3)>0
    assert -4 < Fraction(s, 2) < 3


def combinatorial_checks() -> dict:
    triangle_parts = [1, 18, 0, 36, 144, 32]
    assert sum(triangle_parts) == 231
    assert 6 * triangle_parts[-1] == 192
    assert 60 * 8 // 2 == 240

    # The block-overlap ledger.
    for c4x in range(226):
        n0, n1, n2 = 342 + 2 * c4x, 900 - 4 * c4x, 288 + 2 * c4x
        assert n0 + n1 + n2 == 1530
        assert n1 + 2 * n2 == 1476
        assert (n0 // 2) == 171 + c4x
    assert 900 - 4 * 225 == 0

    # Missing in discovery: X is cubic on 36 vertices.  At a vertex there
    # are only C(3,2)=3 pairs of incident edges, and mu=2 allows each such
    # pair to close at most one C4.  Hence 4*C4(X)<=36*3.
    vertex_cycle_incidence_cap = 36 * 3
    corrected_c4_max = vertex_cycle_incidence_cap // 4
    assert corrected_c4_max == 27

    return {
        "triangle_decomposition": {
            "T": 1,
            "TXX": 18,
            "XXX": 0,
            "XXY": 36,
            "XYY": 144,
            "YYY": 32,
        },
        "Y": {
            "order": 60,
            "degree": 8,
            "edges": 240,
            "triangles": 32,
            "moments_0_to_3": [60, 0, 480, 192],
        },
        "ledger": {
            "nonadjacent_Y_pair_counts": [
                "342+2q",
                "900-4q",
                "288+2q",
            ],
            "C4_Y": "171+q",
            "trace_A_Y_fourth": "8568+8q",
        },
        "discovery_overlap_nonnegativity_bound": 225,
        "moment_localizer_bound": 89,
        "correct_cubic_graph_bound": 27,
        "cubic_bound_certificate": "4*C4(X)<=36*C(3,2)=108",
    }


def verify_discovery_ledger(data: dict) -> tuple[list[dict], list[dict]]:
    assert data["claim_label"] == "DERIVED_INCONCLUSIVE"
    assert data["endpoint"]["srg"] == [99, 14, 1, 2]
    assert data["endpoint"]["cell_sizes_T_X_Y"] == [3, 36, 60]
    assert data["endpoint"]["prism_free"] is True
    assert data["quotient_and_supported_sectors"]["quotient_matrix"] == [
        [2, 12, 0], [1, 3, 10], [0, 6, 8]
    ]
    assert data["quotient_and_supported_sectors"]["eigenvalues"] == [14, 3, -4]
    assert (
        data["quotient_and_supported_sectors"]["supported_sector"]["dimension_each"]
        == 2
    )
    assert data["projectors_and_restrictions"]["ranks"] == {
        "E3": 54, "E_minus4": 44
    }
    assert data["projectors_and_restrictions"]["Y_block_ranks"] == {
        "E3": "60-mult_Y(-4)",
        "E_minus4": "60-mult_Y(3)",
    }
    assert data["forced_Y_multiplicities"]["mult_Y_3"] == [18, 20]
    assert data["forced_Y_multiplicities"]["mult_Y_minus4"] == [8, 13]
    assert data["forced_Y_multiplicities"]["supported_kernel_dimensions"] == {
        "lambda_3": "mult_Y(-4)-6",
        "lambda_minus4": "mult_Y(3)-16",
    }
    moments = data["combinatorial_moments"]
    assert moments["Y_order_degree_edges"] == [60, 8, 240]
    assert moments["Y_triangles"] == 32
    assert moments["trace_A_Y_powers_0_to_3"] == [60, 0, 480, 192]
    assert moments["triangle_decomposition"] == {
        "T_itself": 1,
        "T_plus_two_X": 18,
        "three_X": 0,
        "two_X_plus_Y": 36,
        "X_plus_two_Y": 144,
        "three_Y": 32,
    }
    assert moments["four_cycle_parameter"] == {
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
    }
    star = data["star_complement_reduction"]
    assert star["whole_graph_lambda_3"] == {
        "star_set_size": 54,
        "minimum_U_hit": "mult_Y(-4)-6 in [2,7]",
        "minimum_hit_complement_Y_count": "mult_Y(-4) in [8,13]",
        "star_complement_size": 45,
    }
    assert star["whole_graph_lambda_minus4"] == {
        "star_set_size": 44,
        "minimum_U_hit": "mult_Y(3)-16 in [2,4]",
        "minimum_hit_complement_Y_count": "mult_Y(3) in [18,20]",
        "star_complement_size": 55,
    }
    assert star["Y_only_exact_rank_problem"] == {
        "rank_11AY_plus_44I_minus_2J": "60-mult_Y(-4) in [47,52]",
        "rank_minus9AY_plus_27I_plus_J": "60-mult_Y(3) in [39,42]",
        "lambda_3_star_complement_orders": [40, 42],
        "lambda_minus4_star_complement_orders": [47, 52],
    }
    assert (
        star["reconstruction_identity"]
        == "mu I-A_S = B^T (mu I-C)^(-1) B, with mu not in spectrum(C)"
    )
    conclusion = data["conclusion"]
    assert conclusion["endpoint_excluded"] is False
    assert conclusion["endpoint_graph_constructed"] is False
    assert conclusion["conway_99_status"] == "UNKNOWN"

    first_three = [
        (a, b)
        for a in range(18, 60)
        for b in range(8, 60)
        if first_three_feasible(a, b)
    ]
    expected_pairs = list(EXPECTED_DISCOVERY_RANGES)
    assert first_three == expected_pairs

    rows = data["multiplicity_fourth_moment_ledger"]
    actual_rows = {}
    for row in rows:
        pair = (row["a_mult_Y_3"], row["b_mult_Y_minus4"])
        assert pair not in actual_rows
        actual_rows[pair] = row
    assert list(actual_rows) == expected_pairs

    corrected_rows = []
    for pair, expected_range in EXPECTED_DISCOVERY_RANGES.items():
        feasible = [q for q in range(226) if fourth_feasible(*pair, q)]
        assert feasible == list(range(expected_range[0], expected_range[1] + 1))
        row = actual_rows[pair]
        assert (row["C4_X_min"], row["C4_X_max"]) == expected_range
        assert row["feasible_C4_X_count"] == len(feasible)
        corrected = [q for q in feasible if q <= 27]
        if corrected:
            corrected_rows.append({
                "a": pair[0],
                "b": pair[1],
                "C4_X_min": min(corrected),
                "C4_X_max": max(corrected),
                "count": len(corrected),
            })

    assert len(corrected_rows) == 9
    return rows, corrected_rows


def verify_controls(data: dict) -> list[dict]:
    controls = data["scalar_algebraic_integer_controls"]
    assert len(controls) == 18
    seen = set()
    summaries = []
    for row in controls:
        pair = (row["a_mult_Y_3"], row["b_mult_Y_minus4"])
        assert pair in EXPECTED_DISCOVERY_RANGES and pair not in seen
        seen.add(pair)
        counts = [row["linear_root_counts"][str(root)] for root in ROOTS]
        assert all(isinstance(count, int) and count >= 0 for count in counts)
        sums = [sum(counts)]
        sums.extend(
            sum(count * root**power for count, root in zip(counts, ROOTS))
            for power in range(1, 5)
        )
        if pair in EXPECTED_CONTROL_QUADRATICS:
            s, product, multiplicity, text = EXPECTED_CONTROL_QUADRATICS[pair]
            assert row["quadratic_factor"] == text
            exact_quadratic_interval_check(s, product)
            for index, value in enumerate(quadratic_power_sums(s, product)):
                sums[index] += multiplicity * value
        else:
            assert row["quadratic_factor"] is None

        assert sums == row["residual_power_sums_p0_to_p4"]
        assert sums[:4] == remaining_moments(*pair)
        numerator = sums[4] + 81 * pair[0] + 256 * pair[1] - 4472
        assert numerator % 8 == 0
        c4x = numerator // 8
        assert c4x == row["C4_X"]
        assert fourth_feasible(*pair, c4x)
        newton_coefficients(sums[1:])
        assert row["verified"] is True
        assert row["graph_realization_claimed"] is False
        summaries.append({
            "a": pair[0],
            "b": pair[1],
            "C4_X": c4x,
            "within_correct_cubic_bound": c4x <= 27,
        })
    assert seen == set(EXPECTED_DISCOVERY_RANGES)
    assert sum(item["within_correct_cubic_bound"] for item in summaries) == 8
    return summaries


def prior_wave36_checks(prior: dict) -> dict:
    assert prior["claim_label"] == "VERIFIED"
    general = prior["general_checks"]
    partitions = general["component_patterns"]["surviving_partitions"]
    assert partitions == [[4, 4, 4], [4, 8], [6, 6], [12]]
    component_counts = sorted({len(partition) for partition in partitions})
    assert component_counts == [1, 2, 3]
    spectral = general["spectral_general_form"]
    assert spectral["H_triangles"] == 32
    assert spectral["H_four_cycles"] == "171+C4(A_X)"

    exact_pairs = []
    for components in component_counts:
        rank_b = 35 - components
        kernel_dimension = 60 - rank_b
        transferred_trace = -26 + 4 * components
        kernel_trace = -transferred_trace
        # a+b=kernel_dimension; 3a-4b=kernel_trace.
        a_numerator = kernel_trace + 4 * kernel_dimension
        assert a_numerator % 7 == 0
        a = a_numerator // 7
        b = kernel_dimension - a
        assert (a, b) == (18, 7 + components)
        sample = general["spectral_transfer_samples"][str(components)]
        assert sample["gram_rank"] == rank_b
        assert sample["kernel_multiplicities"] == {"3": a, "-4": b}
        exact_pairs.append((a, b))
    return {
        "component_counts": component_counts,
        "rank_B": "35-kappa",
        "mult_Y_3": 18,
        "mult_Y_minus4": "7+kappa",
        "actual_project_pair_set": [list(pair) for pair in exact_pairs],
        "Y_rank_targets": {
            "rank_11AY_plus_44I_minus_2J": [50, 52],
            "rank_minus9AY_plus_27I_plus_J": 42,
        },
        "Y_star_complement_orders": {
            "lambda_3": 42,
            "lambda_minus4": [50, 52],
        },
        "whole_graph_minimum_U_hits": {
            "lambda_3": [2, 4],
            "lambda_minus4": 2,
        },
    }


def run_checks(
    discovery_path: Path = DISCOVERY,
    prior_path: Path = PRIOR,
    write_output: bool = True,
) -> dict:
    start_memory = require_memory_headroom()
    check_hash_file(HERE / "preinspection-freeze.sha256")
    if discovery_path.resolve() == DISCOVERY.resolve():
        check_hash_file(HERE / "discovery-freeze.sha256")

    discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
    prior = json.loads(prior_path.read_text(encoding="utf-8"))

    quotient = quotient_and_sector_checks()
    projectors = projector_checks()
    combinatorics = combinatorial_checks()
    original_rows, cubic_corrected_rows = verify_discovery_ledger(discovery)
    controls = verify_controls(discovery)
    prior_result = prior_wave36_checks(prior)

    actual_pairs = {
        tuple(pair) for pair in prior_result["actual_project_pair_set"]
    }
    assert actual_pairs == {(18, 8), (18, 9), (18, 10)}
    corrected_full_rows = [
        row
        for row in cubic_corrected_rows
        if (row["a"], row["b"]) in actual_pairs
    ]
    assert corrected_full_rows == [
        {"a": 18, "b": 8, "C4_X_min": 0, "C4_X_max": 27, "count": 28},
        {"a": 18, "b": 9, "C4_X_min": 0, "C4_X_max": 27, "count": 28},
        {"a": 18, "b": 10, "C4_X_min": 0, "C4_X_max": 27, "count": 28},
    ]

    result = {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "REFUTED",
        "verdict": "REFUTED_IN_PART",
        "scope": (
            "conditional prism-free endpoint, arbitrary fixed triangle, "
            "Wave57 internal derivation plus project-prior comparison"
        ),
        "independently_reproduced": {
            "quotient_and_supported_sectors": quotient,
            "projectors": projectors,
            "triangle_and_moment_ledger": combinatorics,
            "wave57_moment_relaxation_rows": original_rows,
            "wave57_scalar_control_summaries": controls,
            "star_set_rank_argument": "VERIFIED",
        },
        "corrections": [
            {
                "id": "C1",
                "severity": "material",
                "discovery_statement": "moment-localizer range 0<=C4(X)<=89",
                "correct_statement": "cubic/SRG incidence gives 0<=C4(X)<=27",
                "certificate": "4*C4(X)<=36*C(3,2)=108",
            },
            {
                "id": "C2",
                "severity": "material",
                "discovery_statement": "18 endpoint multiplicity pairs remain",
                "correct_statement": (
                    "18 pairs remain only in the weaker Wave57 moment "
                    "relaxation; prior verified Wave36 transfer leaves "
                    "exactly (18,8),(18,9),(18,10)"
                ),
            },
            {
                "id": "C3",
                "severity": "material",
                "discovery_statement": (
                    "Y-only star-complement orders are 40..42 for lambda=3 "
                    "and 47..52 for lambda=-4"
                ),
                "correct_statement": (
                    "with the prior verified transfer they are exactly 42 "
                    "for lambda=3 and 50..52 for lambda=-4"
                ),
            },
            {
                "id": "C4",
                "severity": "scope",
                "discovery_statement": "all 18 scalar controls support the lane",
                "correct_statement": (
                    "all 18 are valid only for the stated weaker scalar "
                    "moment system; only 8 supplied controls obey C4(X)<=27, "
                    "and Wave36 already supplies the stronger full spectral "
                    "transfer"
                ),
            },
        ],
        "corrected_ledgers": {
            "moment_plus_cubic_rows": cubic_corrected_rows,
            "moment_plus_cubic_row_count": len(cubic_corrected_rows),
            "full_project_prior_rows": corrected_full_rows,
            "full_project_prior_row_count": len(corrected_full_rows),
        },
        "prior_wave36": prior_result,
        "chronology": {
            "wave57_spectral_multiplicity_and_C4_transfer": (
                "REDUNDANT_WEAKER_THAN_VERIFIED_WAVE36"
            ),
            "wave57_additional_packaging": (
                "exact star-set intersection minima and a Y-only "
                "reconstruction framing"
            ),
            "novelty_status": "UNKNOWN",
        },
        "status_boundary": {
            "Y_graph_constructed": False,
            "endpoint_graph_constructed": False,
            "endpoint_excluded": False,
            "conway_99_status": "UNKNOWN",
        },
        "resource_guard": {
            "minimum_free_physical_memory_percent": 20,
            "start_free_physical_memory_percent": round(float(start_memory), 2),
            "finish_free_physical_memory_percent": round(
                float(require_memory_headroom()), 2
            ),
        },
        "limitations": [
            "All conclusions are conditional on the prism-free n3=4158 endpoint.",
            "The corrected C4 upper bound and Wave36 transfer do not construct or exclude the endpoint.",
            "The scalar controls are not graph spectra.",
            "No binary reconstruction matrix or exhaustive star-complement search is supplied.",
            "No completed-graph automorphism is assumed.",
        ],
    }
    if write_output:
        OUTPUT.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return result


def verify_saved(path: Path) -> dict:
    expected = run_checks(write_output=False)
    actual = json.loads(path.read_text(encoding="utf-8"))
    # Memory percentages are observational and may differ on replay.
    expected_copy = copy.deepcopy(expected)
    actual_copy = copy.deepcopy(actual)
    expected_copy["resource_guard"].pop("start_free_physical_memory_percent")
    expected_copy["resource_guard"].pop("finish_free_physical_memory_percent")
    actual_copy["resource_guard"].pop("start_free_physical_memory_percent")
    actual_copy["resource_guard"].pop("finish_free_physical_memory_percent")
    assert actual_copy == expected_copy
    return actual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DISCOVERY)
    parser.add_argument("--prior", type=Path, default=PRIOR)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        result = verify_saved(args.verify)
    else:
        result = run_checks(
            discovery_path=args.input,
            prior_path=args.prior,
            write_output=False,
        )
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "claim_label": result["claim_label"],
        "verdict": result["verdict"],
        "correction_count": len(result["corrections"]),
        "project_prior_pairs":
            result["corrected_ledgers"]["full_project_prior_row_count"],
        "conway_99_status":
            result["status_boundary"]["conway_99_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
