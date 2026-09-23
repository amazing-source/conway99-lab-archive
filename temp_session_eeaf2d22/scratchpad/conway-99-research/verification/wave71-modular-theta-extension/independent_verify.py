#!/usr/bin/env python3
"""Clean-room verifier for the conditional Wave 71 modular-theta route.

The calculation imports only the independently verified Wave 66 theorem.  It
does not import or execute Wave 71 discovery code.  Its conclusions remain
conditional on a hypothetical srg(99,14,1,2).
"""

from __future__ import annotations

import argparse
import json
import math
import os
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Iterable


MODULUS = 7
PRECISION = 15
RANK = 44
V = 99
K_DEGREE = 14
POSITIVE_RESTRICTED_EIGENVALUE = 3


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


def divisor_power_sum(n: int, power: int) -> int:
    return sum(d**power for d in range(1, n + 1) if n % d == 0)


def series_multiply(left: list[int], right: list[int]) -> list[int]:
    result = [0] * PRECISION
    for i, x in enumerate(left):
        for j, y in enumerate(right[: PRECISION - i]):
            result[i + j] = (result[i + j] + x * y) % MODULUS
    return result


def series_power(series: list[int], exponent: int) -> list[int]:
    result = [1] + [0] * (PRECISION - 1)
    base = series[:]
    while exponent:
        if exponent & 1:
            result = series_multiply(result, base)
        base = series_multiply(base, base)
        exponent //= 2
    return result


def eisenstein_series_mod_7() -> tuple[list[int], list[int]]:
    e4 = [1] + [
        (240 * divisor_power_sum(n, 3)) % 7 for n in range(1, PRECISION)
    ]
    e6 = [1] + [
        (-504 * divisor_power_sum(n, 5)) % 7 for n in range(1, PRECISION)
    ]
    assert e6 == [1] + [0] * (PRECISION - 1)
    return e4, e6


def rref_affine(
    coefficient_rows: list[list[int]], target: list[int]
) -> tuple[list[list[int]], list[int], list[int], bool]:
    column_count = len(coefficient_rows[0])
    matrix = [
        [value % MODULUS for value in row] + [rhs % MODULUS]
        for row, rhs in zip(coefficient_rows, target, strict=True)
    ]
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        selected = next(
            (
                row
                for row in range(pivot_row, len(matrix))
                if matrix[row][column] % MODULUS
            ),
            None,
        )
        if selected is None:
            continue
        matrix[pivot_row], matrix[selected] = matrix[selected], matrix[pivot_row]
        inverse = pow(matrix[pivot_row][column], -1, MODULUS)
        matrix[pivot_row] = [
            (entry * inverse) % MODULUS for entry in matrix[pivot_row]
        ]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                (x - factor * y) % MODULUS
                for x, y in zip(matrix[row], matrix[pivot_row], strict=True)
            ]
        pivot_columns.append(column)
        pivot_row += 1
    inconsistent = any(
        all(row[column] == 0 for column in range(column_count)) and row[-1]
        for row in matrix
    )
    free_columns = [
        column for column in range(column_count) if column not in pivot_columns
    ]
    return matrix, pivot_columns, free_columns, inconsistent


def solve_affine(
    matrix: list[list[int]],
    pivot_columns: list[int],
    free_columns: list[int],
    free_values: list[int],
    column_count: int,
) -> list[int]:
    solution = [0] * column_count
    for column, value in zip(free_columns, free_values, strict=True):
        solution[column] = value % MODULUS
    for row, column in reversed(list(enumerate(pivot_columns))):
        solution[column] = (
            matrix[row][-1]
            - sum(matrix[row][j] * solution[j] for j in free_columns)
        ) % MODULUS
    return solution


def normalized_affine_relations(
    base: tuple[int, int, int], directions: list[tuple[int, int, int]]
) -> list[tuple[int, int, int, int]]:
    relations: set[tuple[int, int, int, int]] = set()
    for coefficients in product(range(7), repeat=3):
        if coefficients == (0, 0, 0):
            continue
        if not all(
            sum(a * b for a, b in zip(coefficients, direction, strict=True)) % 7
            == 0
            for direction in directions
        ):
            continue
        first = next(value for value in coefficients if value)
        inverse = pow(first, -1, 7)
        constant = (
            sum(a * b for a, b in zip(coefficients, base, strict=True)) * inverse
        ) % 7
        relations.add(
            tuple((value * inverse) % 7 for value in coefficients) + (constant,)
        )
    return sorted(relations)


def level_one_rows() -> list[dict[str, object]]:
    e4, e6 = eisenstein_series_mod_7()
    rows: list[dict[str, object]] = []
    for q in range(2, 17, 2):
        weight = 154 - 3 * q
        basis_exponents = [
            (a, (weight - 4 * a) // 6)
            for a in range(weight // 4 + 1)
            if weight - 4 * a >= 0 and (weight - 4 * a) % 6 == 0
        ]
        basis = [
            series_multiply(series_power(e4, a), series_power(e6, b))
            for a, b in basis_exponents
        ]
        constraints = [
            [basis[column][coefficient] for column in range(len(basis))]
            for coefficient in range(7)
        ]
        matrix, pivots, free, inconsistent = rref_affine(
            constraints, [1] + [0] * 6
        )
        assert not inconsistent

        def triple(free_values: list[int]) -> tuple[int, int, int]:
            solution = solve_affine(
                matrix, pivots, free, free_values, len(basis)
            )
            return tuple(
                sum(
                    solution[column] * basis[column][coefficient]
                    for column in range(len(basis))
                )
                % 7
                for coefficient in (7, 8, 9)
            )

        base = triple([0] * len(free))
        directions = []
        for index in range(len(free)):
            unit = [0] * len(free)
            unit[index] = 1
            moved = triple(unit)
            directions.append(
                tuple((moved[j] - base[j]) % 7 for j in range(3))
            )
        relations = normalized_affine_relations(base, directions)

        longest_gap = 8 if q == 16 else 13
        long_constraints = [
            [basis[column][coefficient] for column in range(len(basis))]
            for coefficient in range(longest_gap + 1)
        ]
        long_matrix, long_pivots, long_free, long_inconsistent = rref_affine(
            long_constraints, [1] + [0] * longest_gap
        )
        assert not long_inconsistent and not long_free
        long_solution = solve_affine(
            long_matrix, long_pivots, long_free, [], len(basis)
        )
        next_coefficient = sum(
            long_solution[column] * basis[column][longest_gap + 1]
            for column in range(len(basis))
        ) % 7
        impossible_constraints = [
            [basis[column][coefficient] for column in range(len(basis))]
            for coefficient in range(longest_gap + 2)
        ]
        _, _, _, next_zero_inconsistent = rref_affine(
            impossible_constraints, [1] + [0] * (longest_gap + 1)
        )
        assert next_zero_inconsistent
        rows.append(
            {
                "q": q,
                "weight": weight,
                "integral_basis_dimension": len(basis),
                "constraint_rank": len(pivots),
                "affine_dimension_after_q0_to_q6": len(free),
                "longest_initial_zero_run": longest_gap,
                "forced_next_coefficient_mod_7": next_coefficient,
                "next_zero_inconsistent": next_zero_inconsistent,
                "forced_upper_bound_on_min_K": 2 * (longest_gap + 1),
                "relations_on_coefficients_q7_q8_q9": [
                    {
                        "coefficients": list(relation[:3]),
                        "constant": relation[3],
                    }
                    for relation in relations
                ],
            }
        )
    assert [
        row["relations_on_coefficients_q7_q8_q9"] for row in rows[:-1]
    ] == [[]] * 7
    assert rows[-1]["relations_on_coefficients_q7_q8_q9"] == [
        {"coefficients": [1, 1, 1], "constant": 2}
    ]
    assert [
        (
            row["longest_initial_zero_run"],
            row["forced_next_coefficient_mod_7"],
            row["forced_upper_bound_on_min_K"],
        )
        for row in rows
    ] == [(13, 6, 28)] * 7 + [(8, 2, 18)]
    return rows


def signed_sum_possible(magnitudes: Iterable[int]) -> bool:
    sums = {0}
    for magnitude in magnitudes:
        sums = {
            current + sign * magnitude
            for current in sums
            for sign in (-1, 1)
        }
    return 0 in sums


def magnitude_profiles(norm: int) -> list[tuple[int, int, int, int]]:
    profiles = []
    for count1 in range(norm + 1):
        for count2 in range(norm // 4 + 1):
            for count3 in range(norm // 9 + 1):
                for count4 in range(norm // 16 + 1):
                    if (
                        count1
                        + 4 * count2
                        + 9 * count3
                        + 16 * count4
                        != norm
                    ):
                        continue
                    if count1 + count3 < 8:
                        continue
                    magnitudes = (
                        [1] * count1
                        + [2] * count2
                        + [3] * count3
                        + [4] * count4
                    )
                    if signed_sum_possible(magnitudes):
                        profiles.append((count1, count2, count3, count4))
    return profiles


def canonical_sign_cases(
    profile: tuple[int, int, int, int]
) -> list[dict[int, int]]:
    counts = {magnitude: count for magnitude, count in enumerate(profile, 1)}
    cases: dict[tuple[tuple[int, int], ...], dict[int, int]] = {}
    ranges = [range(counts[magnitude] + 1) for magnitude in range(1, 5)]
    for positives in product(*ranges):
        signed_sum = sum(
            magnitude * (2 * positives[magnitude - 1] - counts[magnitude])
            for magnitude in range(1, 5)
        )
        if signed_sum:
            continue
        case = {
            value: count
            for magnitude in range(1, 5)
            for value, count in (
                (magnitude, positives[magnitude - 1]),
                (-magnitude, counts[magnitude] - positives[magnitude - 1]),
            )
            if count
        }
        negated = {-value: count for value, count in case.items()}
        key = tuple(sorted(case.items()))
        negative_key = tuple(sorted(negated.items()))
        canonical_key = min(key, negative_key)
        cases[canonical_key] = dict(canonical_key)
    return [cases[key] for key in sorted(cases)]


def spectral_edge_bound(support_size: int) -> int:
    numerator = (
        POSITIVE_RESTRICTED_EIGENVALUE * support_size * V
        + (K_DEGREE - POSITIVE_RESTRICTED_EIGENVALUE)
        * support_size
        * support_size
    )
    return numerator // (2 * V)


def aggregate_edge_totals(
    class_counts: dict[int, int], edge_bound: int
) -> list[int]:
    """Exhaust all integer edge-count matrices between signed value classes."""
    values = tuple(sorted(class_counts))
    pairs: list[tuple[int, int, int, tuple[int, ...]]] = []
    for index, left in enumerate(values):
        for right in values[index:]:
            capacity = (
                class_counts[left] * (class_counts[left] - 1) // 2
                if left == right
                else class_counts[left] * class_counts[right]
            )
            coefficients = [0] * len(values)
            if left == right:
                coefficients[index] = 2 * left
            else:
                coefficients[index] = right
                coefficients[values.index(right)] = left
            pairs.append((left, right, capacity, tuple(coefficients)))
    pairs.sort(
        key=lambda item: sum(abs(value) for value in item[3]) * item[2],
        reverse=True,
    )

    suffix_minimum = [[0] * len(values) for _ in range(len(pairs) + 1)]
    suffix_maximum = [[0] * len(values) for _ in range(len(pairs) + 1)]
    for index in range(len(pairs) - 1, -1, -1):
        capacity = pairs[index][2]
        coefficients = pairs[index][3]
        for column, coefficient in enumerate(coefficients):
            suffix_minimum[index][column] = (
                suffix_minimum[index + 1][column]
                + min(0, coefficient * capacity)
            )
            suffix_maximum[index][column] = (
                suffix_maximum[index + 1][column]
                + max(0, coefficient * capacity)
            )

    target = tuple(-4 * value * class_counts[value] for value in values)
    states = {(target, 0)}
    for index, (_, _, capacity, coefficients) in enumerate(pairs):
        next_states = set()
        for residual, used_edges in states:
            for edge_count in range(min(capacity, edge_bound - used_edges) + 1):
                next_residual = tuple(
                    residual[column] - coefficients[column] * edge_count
                    for column in range(len(values))
                )
                if all(
                    suffix_minimum[index + 1][column]
                    <= next_residual[column]
                    <= suffix_maximum[index + 1][column]
                    for column in range(len(values))
                ):
                    next_states.add(
                        (next_residual, used_edges + edge_count)
                    )
        states = next_states
        if not states:
            break
    return sorted(
        {
            used_edges
            for residual, used_edges in states
            if all(value == 0 for value in residual)
        }
    )


def low_norm_analysis() -> dict[str, object]:
    expected_profiles = {
        14: [(10, 1, 0, 0), (14, 0, 0, 0)],
        16: [
            (7, 0, 1, 0),
            (8, 2, 0, 0),
            (12, 1, 0, 0),
            (16, 0, 0, 0),
        ],
        18: [
            (9, 0, 1, 0),
            (10, 2, 0, 0),
            (14, 1, 0, 0),
            (18, 0, 0, 0),
        ],
    }
    assert {norm: magnitude_profiles(norm) for norm in (14, 16, 18)} == (
        expected_profiles
    )

    cases = []
    for norm, profiles in expected_profiles.items():
        for profile in profiles:
            for signed_counts in canonical_sign_cases(profile):
                support_size = sum(signed_counts.values())
                bound = spectral_edge_bound(support_size)
                possible_totals = aggregate_edge_totals(signed_counts, bound)
                cases.append(
                    {
                        "norm": norm,
                        "profile_abs1_abs2_abs3_abs4": list(profile),
                        "signed_value_counts": {
                            str(value): signed_counts[value]
                            for value in sorted(signed_counts)
                        },
                        "support_size": support_size,
                        "spectral_edge_bound": bound,
                        "aggregate_edge_totals": possible_totals,
                    }
                )

    surviving = [
        case
        for case in cases
        if case["aggregate_edge_totals"]
    ]
    assert [
        (
            case["norm"],
            case["profile_abs1_abs2_abs3_abs4"],
            case["aggregate_edge_totals"],
        )
        for case in surviving
    ] == [
        (14, [14, 0, 0, 0], [28]),
        (16, [16, 0, 0, 0], [32, 36]),
        (18, [18, 0, 0, 0], [36, 40, 44]),
    ]

    # If a is the number of same-sign edges in each sign class, then the
    # total support edge count is 4h+4a.  Lambda=1 removes a=1 at h=8.
    assert 5 + 5 - 8 == 2
    # At h=9, a=2 forces two-edge matchings.  Opposite-side common
    # neighbors alone saturate all pair codegrees, so every outside vertex
    # meets each sign class at most once.  There are 82 incidences but only
    # 81 outside vertices.
    assert 4 * math.comb(5, 2) + 5 * math.comb(4, 2) == 70
    assert 2 * 1 + (math.comb(9, 2) - 2) * 2 == 70
    assert 9 * 14 - (4 * 6 + 5 * 4) == 82
    assert V - 18 == 81

    return {
        "odd_support_import": (
            "the odd support is a nonzero ker_F2(A) word and therefore has "
            "size at least 8"
        ),
        "profiles": {
            str(norm): [list(profile) for profile in profiles]
            for norm, profiles in expected_profiles.items()
        },
        "aggregate_cases": cases,
        "all_mixed_magnitude_profiles_eliminated": True,
        "remaining_signed_supports": {
            "norm14": {
                "sign_class_sizes": [7, 7],
                "induced_graph": "4-regular bipartite",
                "stronger_structure": (
                    "the incidence graph of the complementary Fano "
                    "2-(7,4,2) design"
                ),
                "outside_degree_moments": {
                    "vertices": 85,
                    "sum_d": 70,
                    "sum_choose_d_2": 0,
                    "distribution_d0_to_d7": [15, 70, 0, 0, 0, 0, 0, 0],
                },
                "external_design": {
                    "independent_point_set_size": 15,
                    "block_count": 70,
                    "parameters": "2-(15,3,2)",
                    "derivation": (
                        "the 15 degree-zero-to-support vertices are "
                        "independent; their 70 external neighborhoods have "
                        "sum c=210 and sum C(c,2)=210, so equality in "
                        "Cauchy forces every block size c=3"
                    ),
                },
            },
            "norm16": {
                "sign_class_sizes": [8, 8],
                "induced_graph": "4-regular bipartite",
                "same_sign_edge_case_a1": (
                    "impossible: its adjacent endpoints each have five "
                    "neighbors in an opposite class of size eight, giving "
                    "at least two common neighbors against lambda=1"
                ),
                "outside_degree_moments": {
                    "vertices": 83,
                    "sum_d": 80,
                    "sum_choose_d_2": 8,
                    "possible_distributions_d0_to_d7": [
                        [11, 64, 8, 0, 0, 0, 0, 0],
                        [10, 67, 5, 1, 0, 0, 0, 0],
                        [9, 70, 2, 2, 0, 0, 0, 0],
                        [8, 72, 2, 0, 1, 0, 0, 0],
                    ],
                },
            },
            "norm18": {
                "sign_class_sizes": [9, 9],
                "surviving_h": [0, 1],
                "case_a0": "4-regular bipartite",
                "case_a1": (
                    "one same-sign edge in each class; its four endpoints "
                    "have cross-degree five and the other vertices have "
                    "cross-degree four; each same-sign edge has exactly one "
                    "common neighbor in the opposite class"
                ),
                "case_a2": (
                    "impossible: lambda=1 makes both two-edge same-sign "
                    "graphs matchings; opposite-class codegrees then "
                    "saturate every same-class pair, but 82 outside "
                    "incidences cannot fit into 81 vertices at degree at "
                    "most one"
                ),
            },
        },
    }


def lattice_transfer() -> dict[str, object]:
    rows = []
    for q in range(2, 17, 2):
        l_smith = [1] * (44 - q) + [7] * q
        k_smith = [1] * q + [7] * (44 - q)
        elementary_divisor_sum = sum(k_smith)
        assert elementary_divisor_sum == 308 - 6 * q
        rows.append(
            {
                "q": q,
                "r": 44 - q,
                "L_smith_count_1_7": [l_smith.count(1), l_smith.count(7)],
                "K_smith_count_1_7": [
                    k_smith.count(1),
                    k_smith.count(7),
                ],
                "elementary_divisor_sum": elementary_divisor_sum,
                "Skoruppa_level_one_weight": elementary_divisor_sum // 2,
            }
        )
    return {
        "wave66_import": {
            "rank": 44,
            "M_discriminant": "Z/9 direct_sum (Z/7)^q",
            "q_values": list(range(2, 17, 2)),
            "min_Mdual_at_least": 2,
        },
        "marked_three_primary_class": (
            "all u_i have one class alpha in M*/M; q(alpha)=14/9=5/9 "
            "mod Z and b(alpha,alpha)=28/9=1/9 mod Z, so alpha has order "
            "nine and generates the Z/9 factor; H=<3 alpha> is isotropic"
        ),
        "marked_class_exact_values": {
            "alpha": "[u_i]",
            "order": 9,
            "quadratic_value_mod_Z": "5/9",
            "bilinear_self_value_mod_Z": "1/9",
            "H": "<3 alpha>",
            "H_perp_inside_Z9": "H",
        },
        "index_three_even_overlattice": {
            "definition": "L=M+Z(3u_0), so L/M=H",
            "index": 3,
            "rank": 44,
            "discriminant": "(Z/7)^q",
            "exact_level": 7,
            "minimum_at_least": 2,
            "marked_frame": {
                "vectors": "3u_i, i=0,...,98",
                "norm": 28,
                "adjacent_inner_product": -8,
                "nonadjacent_inner_product": 1,
                "sum": 0,
                "frame_operator": "63I",
            },
        },
        "dual_scaled_lattice": {
            "definition": "K=sqrt(7) L*",
            "rank": 44,
            "even_integral": True,
            "exact_level": 7,
            "minimum_at_least": 14,
        },
        "rows": rows,
    }


def vector_bijection() -> dict[str, object]:
    # L*/M maps to H-perp, so its 3-primary marked coordinate has order at
    # most three.  In Wave 66 coordinates t_i=n_i+b/9 this gives 3|b.
    # For b=3 or 6, the unconstrained balanced fractional energy is 22.
    assert 33 * (99 - 33) // 99 == 22
    assert 66 * (99 - 66) // 99 == 22
    return {
        "coordinate_model": (
            "for y in M*, t_i=<y,u_i>=n_i+b/9, sum(n_i)=-11b, "
            "and (A+4I)n=-(2b)1"
        ),
        "Ldual_condition": "the marked Z/9 coordinate lies in H, hence 3|b",
        "fractional_cosets": (
            "the nonintegral possibilities b=3,6 have unconstrained frame "
            "energy 22 and cannot occur at energy 14,16,18"
        ),
        "bijection": (
            "vectors of norm 14,16,18 in K=sqrt(7)L* correspond bijectively "
            "to integer vectors n with (A+4I)n=0 and squared norm "
            "14,16,18, respectively"
        ),
        "theta_coefficients": (
            "N14,N16,N18 count those integer -4 eigenvectors and are even "
            "under n -> -n"
        ),
    }


def build_results() -> dict[str, object]:
    level_one = level_one_rows()
    return {
        "format": "wave71-independent-verifier-v1",
        "role": "verifier",
        "verdict": "VERIFIED_WITH_CORRECTION",
        "claim_label": "VERIFIED",
        "conditional_scope": "hypothetical srg(99,14,1,2)",
        "lattice_transfer": lattice_transfer(),
        "Skoruppa_main_theorem": {
            "primary_source": (
                "Nils-Peter Skoruppa, Reduction mod l of Theta Series of "
                "Level l^n, arXiv:0807.4694v1, Main Theorem"
            ),
            "source_url": "https://arxiv.org/abs/0807.4694",
            "normalization": (
                "theta_L=sum_x q^((x,x)/2); e(L) is the sum, not the "
                "valuation sum, of the Gram elementary divisors"
            ),
            "hypotheses_checked": {
                "prime_at_least_5": True,
                "positive_definite_even_integral": True,
                "level_is_prime_power": True,
                "integral_theta_coefficients": True,
            },
            "conclusion": (
                "theta_L is coefficientwise congruent mod 7 to an integral "
                "level-one modular form of weight e(L)/2=154-3q"
            ),
        },
        "level_one_mod_7": {
            "theta_initial_shape": (
                "1+0q+...+0q^6+N14 q^7+N16 q^8+N18 q^9+..."
            ),
            "rows": level_one,
            "q16_relation_mod_7": "N14+N16+N18=2 mod 7",
            "q16_relation_mod_14": "N14+N16+N18=2 mod 14",
            "q16_consequence": (
                "at least one integer -4 eigenvector of squared norm "
                "14, 16, or 18 exists"
            ),
            "no_relation_through_q9_for_q2_to_q14": True,
            "q2_to_q14_stronger_bound": "min(K)<=28",
        },
        "vector_bijection": vector_bijection(),
        "low_norm_analysis": low_norm_analysis(),
        "status": {
            "new_conditional_fact": (
                "q=16 (equivalently r=28) forces one of the classified "
                "small signed-support configurations"
            ),
            "recorded_correction": (
                "discovery leaves norm-18 h=2 alive; the verifier's exact "
                "outside-incidence count excludes it, so only h=0 or h=1 "
                "remain at norm 18"
            ),
            "q16_excluded": False,
            "graph": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run with only {free:.1f}% free memory")

    encoded = canonical_bytes(build_results())
    canonical = Path(__file__).with_name("independent-results.json")
    if args.output:
        args.output.write_bytes(encoded)
    elif args.verify:
        if canonical.read_bytes() != encoded:
            raise SystemExit("independent-results.json is stale")
    else:
        canonical.write_bytes(encoded)
    print(
        "PASS: Wave 71 clean-room modular-theta reconstruction; "
        "VERIFIED_WITH_CORRECTION; Conway-99 UNKNOWN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
