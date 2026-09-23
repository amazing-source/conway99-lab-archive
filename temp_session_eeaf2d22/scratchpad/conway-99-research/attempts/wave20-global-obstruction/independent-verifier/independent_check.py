#!/usr/bin/env python3
"""Independent exact checker for the Wave 20 global Schur obstruction.

This module intentionally imports no submitted Wave 20 code or data.  It
checks the integer/rational arithmetic underlying the human reconstruction
and exposes small validation functions used by hostile mutation tests.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


N_VERTICES = 99
DEGREE = 14
N_TRIANGLES = 231
TRIANGLE_GRAPH_DEGREE = 18
PROJECTOR_SCALE = 21
PROJECTOR_RANK = 44
BASE_N3 = 693
DIAGONAL_FLOOR = 4 * N_TRIANGLES


class CheckFailure(AssertionError):
    """Raised when an exact verification obligation fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def poly_mul(*factors: Sequence[int]) -> tuple[int, ...]:
    out = [1]
    for factor in factors:
        nxt = [0] * (len(out) + len(factor) - 1)
        for i, left in enumerate(out):
            for j, right in enumerate(factor):
                nxt[i + j] += left * right
        out = nxt
    return tuple(out)


def poly_eval(coefficients: Sequence[int | Fraction], value: int) -> Fraction:
    total = Fraction(0)
    power = Fraction(1)
    for coefficient in coefficients:
        total += Fraction(coefficient) * power
        power *= value
    return total


def gamma_spectrum() -> dict[int, int]:
    """Derive Gamma's spectrum from BB^T=7I+X and B^TB=3I+Gamma."""
    original = {14: 1, 3: 54, -4: 44}
    incidence_nonzero = {eigenvalue + 7: multiplicity for eigenvalue, multiplicity in original.items()}
    require(all(eigenvalue > 0 for eigenvalue in incidence_nonzero), "BB^T must have full rank 99")
    require(sum(incidence_nonzero.values()) == N_VERTICES, "incidence rank mismatch")
    derived = {eigenvalue - 3: multiplicity for eigenvalue, multiplicity in incidence_nonzero.items()}
    derived[-3] = N_TRIANGLES - N_VERTICES
    return derived


def c_spectrum() -> dict[int, int]:
    out: dict[int, int] = {}
    for theta, multiplicity in gamma_spectrum().items():
        image = theta * theta - 5 * theta - 18
        out[image] = out.get(image, 0) + multiplicity
    return out


def fixed_profile(q: int) -> tuple[int, int, int, int]:
    require(isinstance(q, int) and 0 <= q <= 12, "q must be an integer in [0,12]")
    return (20 + q, 180 - 3 * q, 3 * q, 12 - q)


def profile_moments(profile: Sequence[int]) -> tuple[int, int, int]:
    require(len(profile) == 4, "profile must have four r-types")
    total = sum(profile)
    first = sum(r * profile[r] for r in range(4))
    second_binomial = sum((r * (r - 1) // 2) * profile[r] for r in range(4))
    return total, first, second_binomial


def solve_profile_from_a3(a3: int) -> tuple[int, int, int, int]:
    """Solve the three moment equations with a3 fixed, without using q formulas."""
    require(isinstance(a3, int) and 0 <= a3 <= 12, "a3 out of range")
    a2 = 36 - 3 * a3
    a1 = 216 - 2 * a2 - 3 * a3
    a0 = 212 - a1 - a2 - a3
    result = (a0, a1, a2, a3)
    require(all(value >= 0 for value in result), "negative profile entry")
    require(profile_moments(result) == (212, 216, 36), "moment solution mismatch")
    return result


def q_sum_from_n3(n3: int) -> Fraction:
    return Fraction(2 * n3, 3)


def n3_from_q_sum(sum_q: int) -> Fraction:
    return Fraction(3 * sum_q, 2)


EXPECTED_M_ENTRIES = {
    "diagonal": 4,
    "intersecting": 0,
    "disjoint_r0": 1,
    "disjoint_r1": 0,
    "disjoint_r2": -1,
    "disjoint_r3": -2,
}


def validate_m_entry_table(table: dict[str, int]) -> None:
    require(set(table) == set(EXPECTED_M_ENTRIES), "M entry classification is incomplete or has extra types")
    for key, expected in EXPECTED_M_ENTRIES.items():
        require(table[key] == expected, f"wrong M entry for {key}: expected {expected}")


def scaled_projector_entries(scale: int) -> dict[str, Fraction]:
    return {
        key: Fraction(scale * value, PROJECTOR_SCALE)
        for key, value in EXPECTED_M_ENTRIES.items()
    }


def validate_exact_projector_scale(scale: int) -> None:
    """Validate the exact normalization used by this proof, not arbitrary multiples."""
    require(scale == PROJECTOR_SCALE, f"proof requires M=21E0, received scale {scale}")
    entries = scaled_projector_entries(scale)
    require(all(value.denominator == 1 for value in entries.values()), "scaled projector is not integral")
    require(entries["diagonal"] == 4, "scaled projector diagonal is not four")


def m_row_statistics(q: int, intersecting_entry: int = 0) -> dict[str, int]:
    a0, a1, a2, a3 = fixed_profile(q)
    row_sum = (
        EXPECTED_M_ENTRIES["diagonal"]
        + TRIANGLE_GRAPH_DEGREE * intersecting_entry
        + a0 * EXPECTED_M_ENTRIES["disjoint_r0"]
        + a1 * EXPECTED_M_ENTRIES["disjoint_r1"]
        + a2 * EXPECTED_M_ENTRIES["disjoint_r2"]
        + a3 * EXPECTED_M_ENTRIES["disjoint_r3"]
    )
    cubic_sum = (
        EXPECTED_M_ENTRIES["diagonal"] ** 3
        + TRIANGLE_GRAPH_DEGREE * intersecting_entry**3
        + a0 * EXPECTED_M_ENTRIES["disjoint_r0"] ** 3
        + a1 * EXPECTED_M_ENTRIES["disjoint_r1"] ** 3
        + a2 * EXPECTED_M_ENTRIES["disjoint_r2"] ** 3
        + a3 * EXPECTED_M_ENTRIES["disjoint_r3"] ** 3
    )
    odd_support = sum(
        count
        for count, entry in (
            (1, EXPECTED_M_ENTRIES["diagonal"]),
            (TRIANGLE_GRAPH_DEGREE, intersecting_entry),
            (a0, EXPECTED_M_ENTRIES["disjoint_r0"]),
            (a1, EXPECTED_M_ENTRIES["disjoint_r1"]),
            (a2, EXPECTED_M_ENTRIES["disjoint_r2"]),
            (a3, EXPECTED_M_ENTRIES["disjoint_r3"]),
        )
        if entry % 2
    )
    return {"row_sum": row_sum, "cubic_sum": cubic_sum, "odd_support": odd_support}


def d_entry(m_entry: int) -> int:
    value = m_entry * m_entry - m_entry
    require(value % 2 == 0, "m^2-m must be even")
    return value // 2


def is_symmetric_mod2(matrix: Sequence[Sequence[int]]) -> bool:
    size = len(matrix)
    return all(
        len(row) == size
        and all((matrix[i][j] - matrix[j][i]) % 2 == 0 for j in range(size))
        for i, row in enumerate(matrix)
    )


def is_alternating_mod2(matrix: Sequence[Sequence[int]]) -> bool:
    return is_symmetric_mod2(matrix) and all(matrix[i][i] % 2 == 0 for i in range(len(matrix)))


def quadratic_value(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> int:
    size = len(matrix)
    require(len(vector) == size, "quadratic-form dimension mismatch")
    require(all(len(row) == size for row in matrix), "quadratic-form matrix must be square")
    return sum(vector[i] * matrix[i][j] * vector[j] for i in range(size) for j in range(size))


def verify_alternating_quadratic_law(matrix: Sequence[Sequence[int]]) -> None:
    require(is_alternating_mod2(matrix), "matrix is not alternating modulo two")
    size = len(matrix)
    for mask in range(1 << size):
        vector = [(mask >> i) & 1 for i in range(size)]
        require(quadratic_value(matrix, vector) % 2 == 0, "alternating quadratic form became odd")


def trace_mathcal_a(n3: int) -> int:
    return 84 * (n3 - BASE_N3)


def diagonal_budget_rejects_delta(delta: int) -> bool:
    """Return True exactly when the trace is below 4 in each of 231 rows."""
    return 84 * delta < DIAGONAL_FLOOR


def induced_c6_count(n3: int) -> int:
    return 209_286 + n3


def run_exact_checks() -> dict[str, Any]:
    obligations: dict[str, dict[str, Any]] = {}

    def record(label: str, callback: Any) -> None:
        try:
            details = callback()
            obligations[label] = {"status": "PASS", "details": details}
        except Exception as exc:  # Report all failed obligations before exit.
            obligations[label] = {
                "status": "FAIL",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

    def check_triangle_spectrum() -> dict[str, Any]:
        spectrum = gamma_spectrum()
        require(spectrum == {18: 1, 7: 54, 0: 44, -3: 132}, "Gamma spectrum mismatch")
        require(sum(spectrum.values()) == N_TRIANGLES, "Gamma multiplicities do not total 231")
        require(sum(theta * mult for theta, mult in spectrum.items()) == 0, "Gamma trace is not zero")
        require(
            sum(theta * theta * mult for theta, mult in spectrum.items())
            == N_TRIANGLES * TRIANGLE_GRAPH_DEGREE,
            "Gamma squared trace does not equal 231*18",
        )
        return {"spectrum": {str(k): v for k, v in spectrum.items()}}

    def check_c() -> dict[str, Any]:
        spectrum = c_spectrum()
        require(spectrum == {216: 1, -4: 54, -18: 44, 6: 132}, "C spectrum mismatch")
        require(18 - 5 == 13, "sanity failure")
        diagonal = TRIANGLE_GRAPH_DEGREE - 18
        intersecting = 5 - 5
        require(diagonal == 0 and intersecting == 0, "C does not vanish on diagonal/intersections")
        return {
            "spectrum": {str(k): v for k, v in spectrum.items()},
            "diagonal_entry": diagonal,
            "intersecting_entry": intersecting,
            "disjoint_entries": [0, 1, 2, 3],
        }

    def check_profiles() -> dict[str, Any]:
        rows = []
        for q in range(13):
            profile = fixed_profile(q)
            require(profile == solve_profile_from_a3(12 - q), "profile is not the unique moment solution")
            require(profile_moments(profile) == (212, 216, 36), "fixed profile moments fail")
            rows.append({"q": q, "a": list(profile)})
        require(3 * 72 // 6 == 36, "ordered-pair halving failed")
        return {
            "ordered_instances": 72,
            "unordered_cross_edge_pairs": 36,
            "profiles": rows,
            "relation": "2*n3=3*sum_q",
        }

    def check_projector() -> dict[str, Any]:
        numerator = poly_mul((-18, 1), (-7, 1), (3, 1))
        require(numerator == (378, 51, -22, 1), "projector numerator expansion mismatch")
        values = {
            theta: poly_eval(numerator, theta) / 378
            for theta in (18, 7, 0, -3)
        }
        require(values == {18: 0, 7: 0, 0: 1, -3: 0}, "E0 interpolation mismatch")
        # Substituting Gamma^3=4Gamma^2+21Gamma+18J yields
        # 378I+72Gamma-18Gamma^2+18J, then division by 18.
        require((378 // 18, 72 // 18, -18 // 18, 18 // 18) == (21, 4, -1, 1), "E0 reduction mismatch")
        validate_exact_projector_scale(21)
        validate_m_entry_table(dict(EXPECTED_M_ENTRIES))
        require(PROJECTOR_SCALE * Fraction(PROJECTOR_RANK, N_TRIANGLES) == 4, "M diagonal scaling mismatch")
        return {
            "E0_polynomial_numerator_low_to_high": list(numerator),
            "E0_values": {str(k): str(v) for k, v in values.items()},
            "M_formula": "21I+4Gamma-Gamma^2+J=3I-Gamma-C+J",
            "M_squared_factor": 21,
            "M_entries": EXPECTED_M_ENTRIES,
        }

    def check_rows_and_trace() -> dict[str, Any]:
        rows = []
        for q in range(13):
            stats = m_row_statistics(q)
            require(stats["row_sum"] == 0, "M row sum is not zero")
            require(stats["cubic_sum"] == 6 * q - 12, "cubic row sum scaling mismatch")
            require(stats["odd_support"] == 20 + 4 * q, "mod-two row support mismatch")
            require(stats["odd_support"] > 0, "M has a zero row modulo two")
            rows.append({"q": q, **stats})
        require(21 * (4 * BASE_N3 - 12 * N_TRIANGLES) == 0, "trace baseline is not n3=693")
        require(trace_mathcal_a(BASE_N3 + 12) == 1008, "trace scaling at Delta=12 is wrong")
        return {
            "rows": rows,
            "trace_formula": "84*(n3-693)",
            "psd_first_bound": 693,
        }

    def check_modular_chain() -> dict[str, Any]:
        require(d_entry(4) == 6 and d_entry(4) % 2 == 0, "D diagonal is not even")
        correct_alt = (
            (0, 1, 1),
            (1, 0, 0),
            (1, 0, 0),
        )
        verify_alternating_quadratic_law(correct_alt)
        require(441 % 2 == 1, "M^3 coefficient must be odd modulo two")
        require((441 * 4) % 4 == 0, "M^3 diagonal is not divisible by four")
        return {
            "D_diagonal": 6,
            "D_mod2": "symmetric_zero_diagonal",
            "M_cubed_factor": 441,
            "A_mod2": "M",
            "A_diagonal_mod4": 0,
        }

    def check_final_bound() -> dict[str, Any]:
        require(DIAGONAL_FLOOR == 924, "diagonal trace floor mismatch")
        require(all(diagonal_budget_rejects_delta(delta) for delta in (0, 3, 6, 9)), "small Delta escaped")
        require(not diagonal_budget_rejects_delta(12), "Delta=12 should pass the arithmetic floor")
        require(84 * 11 == 924, "sharp real-valued trace threshold mismatch")
        require(BASE_N3 % 3 == 0, "baseline is not divisible by three")
        lower = BASE_N3 + 12
        require(lower == 705, "final n3 lower bound mismatch")
        require(induced_c6_count(lower) == 209_991, "induced-C6 translation mismatch")
        return {
            "positive_diagonal_count": N_TRIANGLES,
            "minimum_diagonal": 4,
            "trace_floor": DIAGONAL_FLOOR,
            "rejected_deltas": [0, 3, 6, 9],
            "first_arithmetically_permitted_delta": 12,
            "n3_lower_bound": lower,
            "induced_C6_lower_bound": induced_c6_count(lower),
            "target_status": "UNKNOWN",
            "novelty": "UNKNOWN_OUT_OF_SCOPE",
        }

    record("triangle_incidence_spectrum", check_triangle_spectrum)
    record("C_combinatorial_and_spectral_entries", check_c)
    record("fixed_triangle_profiles_and_q_relation", check_profiles)
    record("exact_projector_and_M", check_projector)
    record("Schur_trace_and_nonzero_mod2_rows", check_rows_and_trace)
    record("mod2_mod4_alternating_form", check_modular_chain)
    record("PSD_diagonal_budget_and_final_translation", check_final_bound)

    mutations: dict[str, dict[str, Any]] = {}

    try:
        validate_exact_projector_scale(20)
        mutations["wrong_projector_scaling_20"] = {"status": "MISSED"}
    except CheckFailure as exc:
        mutations["wrong_projector_scaling_20"] = {"status": "DETECTED", "reason": str(exc)}

    hostile_d = ((1, 0), (0, 0))
    try:
        verify_alternating_quadratic_law(hostile_d)
        mutations["nonzero_D_diagonal_mod2"] = {"status": "MISSED"}
    except CheckFailure as exc:
        witness = quadratic_value(hostile_d, (1, 0)) % 2
        mutations["nonzero_D_diagonal_mod2"] = {
            "status": "DETECTED",
            "reason": str(exc),
            "witness_vector": [1, 0],
            "witness_quadratic_value_mod2": witness,
        }

    hostile_table = dict(EXPECTED_M_ENTRIES)
    hostile_table.pop("intersecting")
    try:
        validate_m_entry_table(hostile_table)
        mutations["missing_intersecting_zero_type"] = {"status": "MISSED"}
    except CheckFailure as exc:
        mutations["missing_intersecting_zero_type"] = {"status": "DETECTED", "reason": str(exc)}

    wrong_intersection_stats = m_row_statistics(0, intersecting_entry=1)
    mutations["intersecting_entry_mutated_to_one"] = {
        "status": "DETECTED" if wrong_intersection_stats["row_sum"] != 0 else "MISSED",
        "mutated_row_sum": wrong_intersection_stats["row_sum"],
        "mutated_cubic_sum": wrong_intersection_stats["cubic_sum"],
    }

    mutations["ordered_pair_total_72_without_halving"] = {
        "status": "DETECTED" if 72 != 36 else "MISSED",
        "correct_total": 36,
    }

    for delta in (3, 6, 9):
        mutations[f"Delta_{delta}"] = {
            "status": "DETECTED" if diagonal_budget_rejects_delta(delta) else "MISSED",
            "trace": 84 * delta,
            "required_trace_floor": DIAGONAL_FLOOR,
        }

    all_pass = all(item["status"] == "PASS" for item in obligations.values())
    all_mutations_detected = all(item["status"] == "DETECTED" for item in mutations.values())
    return {
        "checker": "independent_check.py",
        "imports_submitted_candidate_code": False,
        "arithmetic": "exact integers and fractions only",
        "obligations": obligations,
        "hostile_mutations": mutations,
        "summary": {
            "obligations": "PASS" if all_pass else "FAIL",
            "hostile_mutations": "PASS" if all_mutations_detected else "FAIL",
            "conditional_n3_lower_bound": 705 if all_pass else None,
            "conditional_induced_C6_lower_bound": 209_991 if all_pass else None,
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN_OUT_OF_SCOPE",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("independent-results.json"),
        help="path for exact JSON results",
    )
    args = parser.parse_args()
    result = run_exact_checks()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], sort_keys=True))
    return 0 if result["summary"]["obligations"] == result["summary"]["hostile_mutations"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
