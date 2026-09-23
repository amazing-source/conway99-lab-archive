"""Exact Wave 96 weighted-C4 and norm-20 calculations.

Discovery only.  This module proves finite arithmetic reductions and
records an explicit relaxation witness; it does not prove a graph or a
local extension cap.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
from fractions import Fraction
from math import ceil, comb
from pathlib import Path


Q = Fraction
DEFAULT_OUTPUT = Path(__file__).with_name("exact-results.json")


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0

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


def fraction_text(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def invert(matrix: list[list[Q]]) -> list[list[Q]]:
    n = len(matrix)
    work = [
        row[:] + [Q(i == j) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next(row for row in range(column, n) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(n):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[column])
            ]
    return [row[n:] for row in work]


def quadratic(vector: list[Q], matrix: list[list[Q]]) -> Q:
    return sum(
        vector[i] * matrix[i][j] * vector[j]
        for i in range(len(vector))
        for j in range(len(vector))
    )


def even_floor(value: Q) -> int:
    floor = value.numerator // value.denominator
    return floor if floor % 2 == 0 else floor - 1


def c4_projector() -> tuple[list[list[Q]], list[list[Q]], Q]:
    # Cycle order 0-1-2-3-0; signs alternate.
    edges = {(0, 1), (1, 2), (2, 3), (0, 3)}
    gram = []
    for i in range(4):
        row = []
        for j in range(4):
            adjacency = int((min(i, j), max(i, j)) in edges)
            row.append((Q(3 * (i == j) - adjacency) + Q(1, 9)) / 7)
        gram.append(row)
    inverse = invert(gram)
    sign = [Q(1), Q(-1), Q(1), Q(-1)]
    minimum = quadratic(sign, inverse)
    return gram, inverse, minimum


def zero_sum_profiles_norm20() -> list[dict[str, int]]:
    profiles = []
    for magnitude_two in range(4):
        units = 20 - 4 * magnitude_two
        for plus_two in range(magnitude_two + 1):
            minus_two = magnitude_two - plus_two
            for plus_one in range(units + 1):
                minus_one = units - plus_one
                if 2 * (plus_two - minus_two) + plus_one - minus_one:
                    continue
                row = (plus_two, minus_two, plus_one, minus_one)
                opposite = (minus_two, plus_two, minus_one, plus_one)
                if row > opposite:
                    continue
                profiles.append(
                    {
                        "magnitude_two": magnitude_two,
                        "plus_two": plus_two,
                        "minus_two": minus_two,
                        "plus_one": plus_one,
                        "minus_one": minus_one,
                    }
                )
    return profiles


def norm20_c4_rows() -> list[dict[str, int]]:
    rows = []
    for h in range(4):
        # Minimum sum r_i^2 is attained by an h-edge matching for h<=3.
        degree_square_minimum = 2 * h
        cross_pair_codegree = 60 + 7 * h + degree_square_minimum // 2
        rows.append(
            {
                "same_edges_per_side": h,
                "minimum_degree_square_sum": degree_square_minimum,
                "minimum_cross_pair_codegree_sum": cross_pair_codegree,
                "minimum_alternating_C4": cross_pair_codegree - 45,
            }
        )
    return rows


def exact_result() -> dict:
    c4_total = (comb(99, 2) - 99 * 14 // 2) // 2
    assert c4_total == 2079

    modular_constant = 1_997_236 * 7
    n14_cap = 4950
    weighted_lower = modular_constant - 2387 * n14_cap
    assert weighted_lower == 2_165_002

    shell_c4 = {
        "norm16_h0": 20,
        "norm18_h0": 18,
        "norm18_h1": 26,
    }
    ratios = {
        "norm16_h0": Q(2 * 407, shell_c4["norm16_h0"]),
        "norm18_h0": Q(2 * 43, shell_c4["norm18_h0"]),
        "norm18_h1": Q(2 * 43, shell_c4["norm18_h1"]),
    }
    maximum_ratio = max(ratios.values())
    assert maximum_ratio == Q(407, 10)

    cap25_rational = maximum_ratio * c4_total * 25
    cap26_rational = maximum_ratio * c4_total * 26
    cap25_even = even_floor(cap25_rational)
    assert cap25_even == 2_115_382 < weighted_lower < cap26_rational
    forced_incidence = ceil(Q(weighted_lower, 1) / maximum_ratio)
    assert forced_incidence == 53_195
    forced_cycle_extensions = ceil(Q(forced_incidence, c4_total))
    assert forced_cycle_extensions == 26

    type_selections = (
        comb(10, 2) ** 4 * comb(51, 2) * comb(49, 2)
    )
    assert type_selections == 6_148_477_125_000

    gram, inverse, interpolation_norm = c4_projector()
    assert interpolation_norm == Q(28, 5)
    residual16 = Q(16) - interpolation_norm
    residual18 = Q(18) - interpolation_norm
    assert residual16 == Q(52, 5) and residual18 == Q(62, 5)
    cross_polytope_points = 2 * 40
    cross_polytope_min_distance = 2 * residual16
    assert cross_polytope_min_distance == Q(104, 5) > 14

    profiles = zero_sum_profiles_norm20()
    expected_profiles = [
        (0, 0, 0, 10, 10),
        (1, 0, 1, 9, 7),
        (2, 0, 2, 8, 4),
        (2, 1, 1, 6, 6),
        (3, 0, 3, 7, 1),
        (3, 1, 2, 5, 3),
    ]
    observed_profiles = [
        (
            row["magnitude_two"],
            row["plus_two"],
            row["minus_two"],
            row["plus_one"],
            row["minus_one"],
        )
        for row in profiles
    ]
    assert observed_profiles == expected_profiles

    norm20_rows = norm20_c4_rows()
    assert [row["minimum_alternating_C4"] for row in norm20_rows] == [
        15,
        23,
        31,
        39,
    ]
    norm20_edge_upper = Q(3 * 20, 2) + Q(11 * 20 * 20, 198)
    assert norm20_edge_upper == Q(5170, 99)
    assert 40 + 4 * 3 <= norm20_edge_upper < 40 + 4 * 4

    q14_prefix_lower = 6842
    q14_incidence_lower = 15 * q14_prefix_lower
    q14_forced_oriented = ceil(Q(q14_incidence_lower, c4_total))
    if q14_forced_oriented % 2:
        q14_forced_oriented += 1
    assert q14_forced_oriented == 50

    return {
        "format": "wave96-norm16-norm18-upper-v1",
        "claim_label": "DERIVED_AND_NULL_BOUNDARY",
        "scope": {
            "target": "hypothetical srg(99,14,1,2)",
            "prism_free_endpoint_required_for_weighted_rank28": True,
            "rank28_q16_only_for_weighted_target": True,
            "rank30_target_does_not_require_prism_free_endpoint": True,
            "automorphism_assumed": False,
            "counts_include_both_signs": True,
        },
        "weighted_rank28": {
            "wave86_integer_identity": (
                "2387*N14+407*N16+43*N18>=13980652"
            ),
            "wave99_N14_upper": n14_cap,
            "forced_weighted_lower": (
                "407*N16+43*N18>=2165002"
            ),
            "weighted_lower_value": weighted_lower,
            "induced_C4_count": c4_total,
            "C4_per_antipodal_support_lower": shell_c4,
            "objective_per_C4_incidence_ratios": {
                key: fraction_text(value) for key, value in ratios.items()
            },
            "maximum_ratio": fraction_text(maximum_ratio),
            "forced_support_C4_incidence_lower": forced_incidence,
            "forced_some_C4_antipodal_extensions": forced_cycle_extensions,
            "cap25_rational_weighted_upper": fraction_text(cap25_rational),
            "cap25_even_integer_weighted_upper": cap25_even,
            "cap25_would_contradict": True,
            "cap26_rational_weighted_upper": fraction_text(cap26_rational),
            "cap26_would_contradict": False,
            "local_cap25_proved": False,
        },
        "fixed_C4": {
            "outside_partition": {
                "type00": 51,
                "P_only": 20,
                "N_only": 20,
                "type11": 4,
            },
            "anchor_only_fiber_sizes": [10, 10, 10, 10],
            "norm16_remaining_per_sign": {
                "two_from_each_opposite_anchor_fiber": 4,
                "from_type00": 2,
            },
            "type_only_selection_count": type_selections,
            "type_only_count_is_not_graph_compatible_count": True,
        },
        "projector_relaxation": {
            "projector_formula": "E=(27I-9A+J)/63",
            "C4_principal_gram": [
                [fraction_text(value) for value in row] for row in gram
            ],
            "C4_principal_inverse": [
                [fraction_text(value) for value in row] for row in inverse
            ],
            "alternating_pattern": [1, -1, 1, -1],
            "minimum_interpolant_squared_norm": fraction_text(
                interpolation_norm
            ),
            "residual_dimension": 40,
            "norm16_residual_squared_radius": fraction_text(residual16),
            "norm18_residual_squared_radius": fraction_text(residual18),
            "cross_polytope_points_norm16": cross_polytope_points,
            "cross_polytope_minimum_squared_distance": fraction_text(
                cross_polytope_min_distance
            ),
            "required_lattice_minimum_squared_distance": 14,
            "cap25_follows_from_projector_and_distance": False,
            "cross_polytope_is_not_lattice_or_graph": True,
        },
        "norm20_dictionary": {
            "nonintegral_energy_threshold": 22,
            "coordinate_magnitude_upper": 2,
            "odd_support_minimum_weight": 8,
            "magnitude_two_upper": 3,
            "zero_sum_profiles_up_to_global_sign": profiles,
            "profile_exclusions": {
                "m3": "opposite signed mass is at most 7 at a magnitude-2 coordinate",
                "m2_same_sign": "two magnitude-2 coordinates would share 8 neighbors",
                "m2_mixed": "a magnitude-2 coordinate and a same-sign unit share at least 3 neighbors",
                "m1": "negative-unit neighborhood intersection is at least 8+4-9=3",
            },
            "surviving_profile": {
                "plus_one": 10,
                "minus_one": 10,
                "other": 0,
            },
            "mixed_profiles_excluded": True,
            "same_edges_per_side_upper": 3,
            "C4_rows": norm20_rows,
            "universal_alternating_C4_lower": 15,
        },
        "rank30_q14": {
            "wave101_prefix": "x7+x8+x9+x10>=6842",
            "dictionary_extension": "x10=N20",
            "oriented_support_C4_incidence_lower": q14_incidence_lower,
            "forced_some_C4_oriented_extensions": q14_forced_oriented,
            "forced_some_C4_antipodal_extensions": q14_forced_oriented // 2,
            "sufficient_universal_antipodal_cap": 24,
            "local_cap24_proved": False,
        },
        "continuation": {
            "primary": (
                "aggregate four-variable fixed-C4 Jacobi theta LP with "
                "common index matrix"
            ),
            "equivalent_polynomial": (
                "F(t)=sum_C4 product_{v in C4} t_v^2"
            ),
            "harmonic_weights": [22, 24, 26, 28, 30],
            "missing_input": (
                "exact rational-characteristic coset transformation and "
                "signed harmonic coefficient control"
            ),
        },
        "status": {
            "rank28_excluded": False,
            "rank30_excluded": False,
            "N16_upper_bound": None,
            "N18_upper_bound": None,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The cap of 25 antipodal norm16/norm18 extensions is not proved.",
            "The cap of 24 antipodal extensions through norm20 is not proved.",
            "The cross-polytope is only a relaxation witness.",
            "No graph, lattice, or short-vector support is constructed.",
            "Discovery requires independent verification.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_positional", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.output is not None and args.output_positional is not None:
        parser.error("choose either positional output or --output, not both")
    output = args.output or args.output_positional or DEFAULT_OUTPUT
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(
            f"refusing to run with only {free:.1f}% free physical memory"
        )
    result = exact_result()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify:
        if (
            not output.exists()
            or output.read_text(encoding="utf-8") != encoded
        ):
            raise SystemExit("canonical exact-results.json mismatch")
        print(
            "PASS: canonical Wave96 result verified; "
            f"free physical memory {free:.1f}%"
        )
        return
    output.write_text(encoded, encoding="utf-8")
    print(f"wrote {output}; free physical memory {free:.1f}%")


if __name__ == "__main__":
    main()
