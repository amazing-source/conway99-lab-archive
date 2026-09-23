#!/usr/bin/env python3
"""Exact Wave 71 checks for the level-7 neighbor and theta boundary.

The modular-form implication is conditional on Skoruppa's published
reduction theorem, cited in literature-freeze.md.  Everything performed here
after that import is deterministic standard-library arithmetic over F_7.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


PRIME = 7
RANK = 44
SURVIVING_Q = tuple(range(2, 17, 2))


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


def divisor_power_sum(n: int, power: int) -> int:
    return sum(d**power for d in range(1, n + 1) if n % d == 0)


def eisenstein_series(weight: int, precision: int, modulus: int = PRIME) -> list[int]:
    """Return E_4 or E_6 modulo modulus through q^precision."""
    if weight == 4:
        factor, power = 240, 3
    elif weight == 6:
        factor, power = -504, 5
    else:
        raise ValueError("only E4 and E6 are supported")
    return [1] + [
        factor * divisor_power_sum(n, power) % modulus
        for n in range(1, precision + 1)
    ]


def series_multiply(a: list[int], b: list[int], modulus: int) -> list[int]:
    precision = max(len(a), len(b)) - 1
    out = [0] * (precision + 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if i + j > precision:
                break
            out[i + j] = (out[i + j] + x * y) % modulus
    return out


def series_power(a: list[int], exponent: int, modulus: int) -> list[int]:
    precision = len(a) - 1
    result = [1] + [0] * precision
    base = a[:]
    n = exponent
    while n:
        if n & 1:
            result = series_multiply(result, base, modulus)
        base = series_multiply(base, base, modulus)
        n //= 2
    return result


def level_one_monomials(weight: int, precision: int) -> list[dict[str, object]]:
    """Basis monomials E4^a E6^b of the requested even level-one weight."""
    e4 = eisenstein_series(4, precision)
    e6 = eisenstein_series(6, precision)
    assert e6 == [1] + [0] * precision  # E6 == 1 coefficientwise modulo 7.
    rows: list[dict[str, object]] = []
    for a in range(weight // 4 + 1):
        remainder = weight - 4 * a
        if remainder < 0 or remainder % 6:
            continue
        b = remainder // 6
        series = series_multiply(
            series_power(e4, a, PRIME),
            series_power(e6, b, PRIME),
            PRIME,
        )
        rows.append({"E4_exponent": a, "E6_exponent": b, "series_mod_7": series})
    return rows


def rref_augmented(
    matrix: list[list[int]], rhs: list[int], modulus: int = PRIME
) -> dict[str, object]:
    """Exact reduced row echelon form of [matrix | rhs] over F_modulus."""
    if len(matrix) != len(rhs):
        raise ValueError("row/rhs mismatch")
    columns = len(matrix[0]) if matrix else 0
    augmented = [
        [entry % modulus for entry in row] + [value % modulus]
        for row, value in zip(matrix, rhs)
    ]
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(columns):
        selected = next(
            (
                row
                for row in range(pivot_row, len(augmented))
                if augmented[row][column] % modulus
            ),
            None,
        )
        if selected is None:
            continue
        augmented[pivot_row], augmented[selected] = (
            augmented[selected],
            augmented[pivot_row],
        )
        inverse = pow(augmented[pivot_row][column], -1, modulus)
        augmented[pivot_row] = [
            inverse * entry % modulus for entry in augmented[pivot_row]
        ]
        for row in range(len(augmented)):
            if row == pivot_row or not augmented[row][column]:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                (x - scale * y) % modulus
                for x, y in zip(augmented[row], augmented[pivot_row])
            ]
        pivot_columns.append(column)
        pivot_row += 1

    inconsistent = any(
        all(augmented[row][column] == 0 for column in range(columns))
        and augmented[row][-1] != 0
        for row in range(pivot_row, len(augmented))
    )
    free_columns = [
        column for column in range(columns) if column not in pivot_columns
    ]
    particular: list[int] | None = None
    directions: list[list[int]] = []
    if not inconsistent:
        particular = [0] * columns
        for row, column in enumerate(pivot_columns):
            particular[column] = augmented[row][-1]
        for free in free_columns:
            direction = [0] * columns
            direction[free] = 1
            for row, column in enumerate(pivot_columns):
                direction[column] = -augmented[row][free] % modulus
            directions.append(direction)
    return {
        "rref": augmented,
        "pivot_columns": pivot_columns,
        "free_columns": free_columns,
        "rank": len(pivot_columns),
        "inconsistent": inconsistent,
        "particular": particular,
        "directions": directions,
    }


def theta_gap_system(weight: int, vanish_through: int, precision: int) -> dict[str, object]:
    """Solve constant=1 and q^1..q^vanish_through=0 modulo 7."""
    monomials = level_one_monomials(weight, precision)
    matrix = [
        [int(item["series_mod_7"][n]) for item in monomials]
        for n in range(vanish_through + 1)
    ]
    rhs = [1] + [0] * vanish_through
    solved = rref_augmented(matrix, rhs)
    return {"monomials": monomials, "solution": solved}


def evaluate_coefficient(
    monomials: list[dict[str, object]], vector: list[int], exponent: int
) -> int:
    return sum(
        coefficient * int(item["series_mod_7"][exponent])
        for coefficient, item in zip(vector, monomials)
    ) % PRIME


def elementary_divisor_weight(seven_length: int) -> int:
    """Skoruppa weight e(K)/2 for Smith factors 1^(44-s), 7^s."""
    return (RANK - seven_length + PRIME * seven_length) // 2


def modular_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    precision = 14
    for q in SURVIVING_Q:
        seven_length_k = RANK - q
        weight = elementary_divisor_weight(seven_length_k)
        required_gap = theta_gap_system(weight, 6, precision)
        assert not required_gap["solution"]["inconsistent"]

        maximal_tested_gap = 8 if q == 16 else 13
        extremal = theta_gap_system(weight, maximal_tested_gap, precision)
        assert not extremal["solution"]["inconsistent"]
        particular = extremal["solution"]["particular"]
        assert particular is not None
        assert not extremal["solution"]["free_columns"]
        next_exponent = maximal_tested_gap + 1
        forced_next = evaluate_coefficient(
            extremal["monomials"], particular, next_exponent
        )
        impossible_next = theta_gap_system(weight, next_exponent, precision)
        assert impossible_next["solution"]["inconsistent"]
        rows.append(
            {
                "q_discriminant_length_L": q,
                "q_rank_F7_Seidel": 44 - q,
                "seven_length_K": seven_length_k,
                "skoruppa_level_one_weight": weight,
                "basis_monomials": [
                    [item["E4_exponent"], item["E6_exponent"]]
                    for item in extremal["monomials"]
                ],
                "required_gap_q1_through_q6_feasible_mod_7": True,
                "longest_initial_zero_run_feasible_mod_7": maximal_tested_gap,
                "next_zero_condition_inconsistent": True,
                "forced_next_coefficient_mod_7_under_longest_gap": forced_next,
                "forced_upper_bound_min_K": 2 * next_exponent,
                "forced_upper_bound_min_L_dual": f"{2 * next_exponent}/7",
            }
        )
    return rows


def q16_short_coefficient_relation() -> dict[str, object]:
    """Derive A_18 == 2-A_14-A_16 mod 7 after the known q^1..q^6 gap."""
    weight = 106
    solved = theta_gap_system(weight, 6, 9)
    monomials = solved["monomials"]
    solution = solved["solution"]
    particular = solution["particular"]
    directions = solution["directions"]
    assert particular is not None
    assert len(directions) == 2
    affine = {}
    for exponent in (7, 8, 9):
        affine[str(exponent)] = {
            "constant": evaluate_coefficient(monomials, particular, exponent),
            "direction_coefficients": [
                evaluate_coefficient(monomials, direction, exponent)
                for direction in directions
            ],
        }
    assert affine == {
        "7": {"constant": 2, "direction_coefficients": [6, 6]},
        "8": {"constant": 0, "direction_coefficients": [5, 6]},
        "9": {"constant": 0, "direction_coefficients": [3, 2]},
    }
    # Eliminating the two free parameters gives a9=2-a7-a8.
    return {
        "weight": weight,
        "basis_monomials": [
            [item["E4_exponent"], item["E6_exponent"]] for item in monomials
        ],
        "affine_parameterization_q7_q8_q9": affine,
        "eliminated_relation": "A18 = 2 - A14 - A16 (mod 7)",
        "parity_strengthening": "A14 + A16 + A18 = 2 (mod 14)",
    }


def integer_profiles(norm: int) -> list[dict[str, int]]:
    """Enumerate low-norm signed coordinate profiles with odd support >=8."""
    profiles: list[dict[str, int]] = []
    # Choose counts of magnitudes >=2.  The remaining squared norm is exactly
    # p1+m1, while the zero-sum equation determines p1-m1.  This is a complete
    # enumeration without a large Cartesian product.
    for p4 in range(norm // 16 + 1):
        for m4 in range(norm // 16 + 1):
            used4 = 16 * (p4 + m4)
            if used4 > norm:
                continue
            for p3 in range((norm - used4) // 9 + 1):
                for m3 in range((norm - used4) // 9 + 1):
                    used3 = used4 + 9 * (p3 + m3)
                    if used3 > norm:
                        continue
                    for p2 in range((norm - used3) // 4 + 1):
                        for m2 in range((norm - used3) // 4 + 1):
                            remaining = norm - used3 - 4 * (p2 + m2)
                            difference = -(
                                2 * (p2 - m2)
                                + 3 * (p3 - m3)
                                + 4 * (p4 - m4)
                            )
                            if (remaining + difference) % 2:
                                continue
                            p1 = (remaining + difference) // 2
                            m1 = (remaining - difference) // 2
                            if p1 < 0 or m1 < 0:
                                continue
                            odd_support = p1 + m1 + p3 + m3
                            if odd_support < 8:
                                continue
                            profiles.append(
                                {
                                    "+1": p1,
                                    "-1": m1,
                                    "+2": p2,
                                    "-2": m2,
                                    "+3": p3,
                                    "-3": m3,
                                    "+4": p4,
                                    "-4": m4,
                                    "odd_support": odd_support,
                                }
                            )
    return sorted(
        profiles,
        key=lambda row: tuple(row[key] for key in ("+4", "-4", "+3", "-3", "+2", "-2", "+1", "-1")),
    )


def subset_edge_bound_numerator(size: int) -> tuple[int, int]:
    """Return 3m/2+11m^2/198 in lowest terms."""
    from fractions import Fraction

    value = Fraction(3 * size, 2) + Fraction(11 * size * size, 198)
    return value.numerator, value.denominator


def low_norm_classification() -> dict[str, object]:
    profiles = {str(norm): integer_profiles(norm) for norm in (14, 16, 18)}
    assert [len(profiles[str(n)]) for n in (14, 16, 18)] == [3, 8, 8]
    assert subset_edge_bound_numerator(14) == (287, 9)
    assert subset_edge_bound_numerator(16) == (344, 9)
    assert subset_edge_bound_numerator(18) == (45, 1)
    assert subset_edge_bound_numerator(15) == (35, 1)
    return {
        "raw_profiles": profiles,
        "exact_profile_counts": {"14": 3, "16": 8, "18": 8},
        "post_coordinate_and_weight8_elimination": {
            "14": ["seven +1 and seven -1"],
            "16": ["eight +1 and eight -1"],
            "18": ["nine +1 and nine -1"],
        },
        "signed_support_edge_bounds": {
            "14": {
                "spectral_bound": "287/9",
                "induced_edges": "28+4h",
                "surviving_h": [0],
            },
            "16": {
                "spectral_bound": "344/9",
                "induced_edges": "32+4h",
                "spectral_survivors_h": [0, 1],
                "common_neighbor_count_excludes_h": [1],
                "surviving_h": [0],
            },
            "18": {
                "spectral_bound": "45",
                "induced_edges": "36+4h",
                "surviving_h": [0, 1, 2],
                "h2_requires_disjoint_same_sign_edges": True,
            },
        },
        "norm14_forced_design": {
            "support_graph": "4-regular bipartite graph on 7+7",
            "incidence_design": "symmetric 2-(7,4,2), complement of the Fano plane",
            "outside_partition_sizes": [70, 15],
            "outside_15_independent": True,
            "outside_incidence_design": "2-(15,3,2) on 70 blocks",
        },
        "excluded_norm18_mixed_profile": {
            "profile_up_to_sign": "six +1, eight -1, one +2",
            "forced_induced_edge_lower_bound": 36,
            "spectral_upper_bound_on_15_vertices": 35,
        },
    }


def build_results() -> dict[str, object]:
    rows = modular_rows()
    assert rows[-1]["forced_upper_bound_min_K"] == 18
    assert all(row["forced_upper_bound_min_K"] == 28 for row in rows[:-1])
    return {
        "format": "wave71-modular-theta-extension-v1",
        "claim_label": "DERIVED",
        "scope": "conditional on the Wave66 lattice package and Skoruppa's theorem",
        "neighbor_construction": {
            "marked_class": "alpha=[u_i] in M*/M",
            "marked_class_order": 9,
            "marked_class_quadratic_value": "q(alpha)=14/9=5/9 mod Z",
            "isotropic_subgroup": "H=<3 alpha>, |H|=3",
            "L": "M_H=M+Z(3u_0)",
            "L_index_over_M": 3,
            "L_discriminant_group": "(Z/7)^q",
            "L_determinant": "7^q",
            "K": "sqrt(7) L*",
            "K_even_level": 7,
            "K_discriminant_group": "(Z/7)^(44-q)",
            "K_determinant": "7^(44-q)",
            "minimum_K_lower_bound": 14,
            "marked_vectors_in_L": {
                "count": 99,
                "vectors": "3u_i",
                "norm": 28,
                "adjacent_inner_product": -8,
                "nonadjacent_inner_product": 1,
                "frame_operator": "sum_i (3u_i)(3u_i)^T=63I",
            },
        },
        "modular_reduction": {
            "imported_theorem": "Skoruppa 2008 main theorem",
            "theta_K_initial_shape": "1+0q+...+0q^6+O(q^7)",
            "rows": rows,
            "q16_short_coefficient_relation": q16_short_coefficient_relation(),
        },
        "short_vector_dictionary": {
            "L_dual_fractional_parameter": "a is 0, 33, or 66 modulo 99",
            "nonintegral_energy_lower_bound": "sum_i t_i^2 >= 22",
            "norm_at_most_18_over_7_forces_a_zero": True,
            "bijection": (
                "K vectors of norm n<=18 correspond to integer t with "
                "sum(t)=0, At=-4t, and sum(t_i^2)=n"
            ),
            "classification": low_norm_classification(),
        },
        "endpoint": {
            "q16_row_forces_low_norm_eigenvector": True,
            "q16_allowed_squared_norms": [14, 16, 18],
            "q16_count_congruence": "N14+N16+N18=2 mod 14",
            "all_eight_rows_excluded": False,
            "conway_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Wave71 does not validate Wave66; it is conditional on that package.",
            "Skoruppa's theorem is a cited import, not reproved here.",
            "A scalar theta-series congruence is necessary but not sufficient for a lattice genus.",
            "A lattice genus is necessary but not sufficient for the marked 99-vector frame.",
            "The forced low-norm eigenvector alternatives are not yet excluded.",
        ],
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
        raise SystemExit(f"refusing to run with only {free:.1f}% free physical memory")
    encoded = canonical_bytes(build_results())
    canonical = Path(__file__).with_name("exact-results.json")
    if args.output:
        args.output.write_bytes(encoded)
    elif args.verify:
        if canonical.read_bytes() != encoded:
            raise SystemExit("exact-results.json is stale")
        print("PASS: Wave71 canonical artifact matches exact recomputation")
    else:
        print(encoded.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
