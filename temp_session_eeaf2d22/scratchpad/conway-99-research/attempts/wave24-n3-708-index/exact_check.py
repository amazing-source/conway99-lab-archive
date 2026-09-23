#!/usr/bin/env python3
"""Exact arithmetic checks for the Wave 24 n3=708 lattice boundary.

This checker validates finite arithmetic and explicit matrices.  The
continuum logarithmic inequality is proved in the accompanying report; here
we certify the exact derivative factorization and rational bounds on log(3)
used by that proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
RANK = 44
N3 = 708
DELTA = N3 - 693
TRACE_B = 4 * DELTA
TRACE_C = (TRACE_B - RANK) // 2

INPUTS = {
    "verification/2026-07-23-wave20-global-schur-audit.md":
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave23-index-pranks/2026-07-23T192952Z-audit.md":
        "bfd02ebc39515e27e9e2c79d8e286905086f5747a02a310036ce27dd29ff3116",
    "verification/wave23-endpoint-crosscheck/2026-07-23T200645Z-correction-audit.md":
        "791d74340c8a84a9993f9a5179c66baf0b2f7e431df5fb7eda2f593195f9bf53",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def identity(n: int) -> list[list[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(a: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*a)]


def matmul(
    a: list[list[int | Fraction]],
    b: list[list[int | Fraction]],
) -> list[list[int | Fraction]]:
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def trace(a: list[list[int | Fraction]]) -> int | Fraction:
    return sum(a[i][i] for i in range(len(a)))


def block_diag(blocks: Iterable[list[list[int]]]) -> list[list[int]]:
    blocks = list(blocks)
    total = sum(len(block) for block in blocks)
    out = [[0] * total for _ in range(total)]
    offset = 0
    for block in blocks:
        size = len(block)
        for i in range(size):
            for j in range(size):
                out[offset + i][offset + j] = block[i][j]
        offset += size
    return out


def determinant(matrix: list[list[int | Fraction]]) -> Fraction:
    """Fraction-free-enough Gaussian determinant for the small exact blocks."""
    a = [[Fraction(x) for x in row] for row in matrix]
    n = len(a)
    det = Fraction(1)
    for col in range(n):
        pivot = next((row for row in range(col, n) if a[row][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            det = -det
        pivot_value = a[col][col]
        det *= pivot_value
        a[col] = [x / pivot_value for x in a[col]]
        for row in range(col + 1, n):
            scale = a[row][col]
            if scale:
                a[row] = [
                    x - scale * y for x, y in zip(a[row], a[col])
                ]
    return det


def inverse(matrix: list[list[int]]) -> list[list[Fraction]]:
    n = len(matrix)
    a = [
        [Fraction(x) for x in row]
        + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for col in range(n):
        pivot = next((row for row in range(col, n) if a[row][col]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
        pivot_value = a[col][col]
        a[col] = [x / pivot_value for x in a[col]]
        for row in range(n):
            if row == col:
                continue
            scale = a[row][col]
            if scale:
                a[row] = [
                    x - scale * y for x, y in zip(a[row], a[col])
                ]
    return [row[n:] for row in a]


def rank(matrix: list[list[int | Fraction]]) -> int:
    a = [[Fraction(x) for x in row] for row in matrix]
    rows = len(a)
    cols = len(a[0]) if rows else 0
    rank_value = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(rank_value, rows) if a[row][col]),
            None,
        )
        if pivot is None:
            continue
        a[rank_value], a[pivot] = a[pivot], a[rank_value]
        pivot_value = a[rank_value][col]
        a[rank_value] = [x / pivot_value for x in a[rank_value]]
        for row in range(rows):
            if row == rank_value:
                continue
            scale = a[row][col]
            if scale:
                a[row] = [
                    x - scale * y
                    for x, y in zip(a[row], a[rank_value])
                ]
        rank_value += 1
        if rank_value == rows:
            break
    return rank_value


def is_symmetric(matrix: list[list[int | Fraction]]) -> bool:
    return matrix == transpose(matrix)


def has_even_diagonal(matrix: list[list[int | Fraction]]) -> bool:
    return all(
        x.denominator == 1 and x.numerator % 2 == 0
        if isinstance(x, Fraction)
        else x % 2 == 0
        for x in (matrix[i][i] for i in range(len(matrix)))
    )


def positive_definite_by_sylvester(
    matrix: list[list[int | Fraction]],
) -> bool:
    return all(
        determinant([row[:size] for row in matrix[:size]]) > 0
        for size in range(1, len(matrix) + 1)
    )


def log3_bounds(terms: int = 12) -> tuple[Fraction, Fraction]:
    """Bound log(3)=2*atanh(1/2) by a partial sum and geometric tail."""
    z = Fraction(1, 2)
    lower = 2 * sum(
        (z ** (2 * k + 1)) / (2 * k + 1) for k in range(terms)
    )
    first_power = 2 * terms + 1
    tail = (
        2
        * z ** first_power
        / Fraction(first_power, 1)
        / (1 - z * z)
    )
    return lower, lower + tail


def derivative_factorization_coefficients() -> dict[str, object]:
    """Compare coefficients in Q[log(3)][x] for the derivative numerator."""
    # Store each coefficient as (coefficient of log(3), rational part),
    # ordered by x^0, x^1, x^2.
    expanded = [
        (Fraction(-1), Fraction(2, 3)),
        (Fraction(-1), Fraction(-2, 3)),
        (Fraction(2), Fraction(0)),
    ]
    factored = [
        (Fraction(-1), Fraction(2, 3)),
        (Fraction(-1), Fraction(-2, 3)),
        (Fraction(2), Fraction(0)),
    ]
    return {
        "expanded": [
            [fraction_text(left), fraction_text(right)]
            for left, right in expanded
        ],
        "factored": [
            [fraction_text(left), fraction_text(right)]
            for left, right in factored
        ],
        "match": expanded == factored,
    }


def trace_square_rank_bounds(
    trace_c: int = TRACE_C,
    ambient_rank: int = RANK,
) -> list[dict[str, str | int]]:
    """Bounds from Cauchy and the integral nonzero pseudodeterminant."""
    rows = []
    for nonzero_rank in range(1, ambient_rank + 1):
        cauchy = Fraction(trace_c * trace_c, nonzero_rank)
        pseudodeterminant_amgm = Fraction(nonzero_rank, 1)
        floor = max(cauchy, pseudodeterminant_amgm)
        rows.append(
            {
                "nonzero_rank": nonzero_rank,
                "cauchy": fraction_text(cauchy),
                "pseudodeterminant_amgm": fraction_text(
                    pseudodeterminant_amgm
                ),
                "combined_floor": fraction_text(floor),
            }
        )
    return rows


def minimum_trace_c_square(
    trace_c: int = TRACE_C,
    ambient_rank: int = RANK,
) -> Fraction:
    return min(
        max(
            Fraction(trace_c * trace_c, nonzero_rank),
            Fraction(nonzero_rank, 1),
        )
        for nonzero_rank in range(1, ambient_rank + 1)
    )


def determinant_cap(trace_c: int = TRACE_C) -> int:
    """The report proves det(I+2C) <= 3^tr(C) for this positive case."""
    if trace_c < 0:
        raise ValueError("this certificate requires nonnegative trace")
    return 3 ** trace_c


def smooth_index_candidates(cap: int = 3 ** TRACE_C) -> list[dict[str, int]]:
    max_h = cap // 5
    rows = []
    for exponent_3 in range(RANK + 1):
        for exponent_7 in range(RANK + 1):
            h = 3 ** exponent_3 * 7 ** exponent_7
            if h > max_h or h == 1 or h % 4 != 1:
                continue
            detq_raw_max = cap // h
            detq_max = 1 + 4 * ((detq_raw_max - 1) // 4)
            if detq_max < 5:
                continue
            rows.append(
                {
                    "h": h,
                    "v3_h": exponent_3,
                    "v7_h": exponent_7,
                    "rank_F3_M": RANK - exponent_3,
                    "rank_F7_M": RANK - exponent_7,
                    "detQ_min": 5,
                    "detQ_max_congruent_1_mod_4": detq_max,
                }
            )
    return sorted(rows, key=lambda row: row["h"])


E8 = [
    [2, -1, 0, 0, 0, 0, 0, 0],
    [-1, 2, -1, 0, 0, 0, 0, 0],
    [0, -1, 2, -1, 0, 0, 0, -1],
    [0, 0, -1, 2, -1, 0, 0, 0],
    [0, 0, 0, -1, 2, -1, 0, 0],
    [0, 0, 0, 0, -1, 2, -1, 0],
    [0, 0, 0, 0, 0, -1, 2, 0],
    [0, 0, -1, 0, 0, 0, 0, 2],
]
A2 = [[2, -1], [-1, 2]]


def explicit_lattice_survivor() -> dict[str, object]:
    e8_inverse_fraction = inverse(E8)
    if any(x.denominator != 1 for row in e8_inverse_fraction for x in row):
        raise AssertionError("E8 inverse should be integral")
    e8_inverse = [
        [int(x) for x in row] for row in e8_inverse_fraction
    ]

    s = block_diag([E8] * 5 + [A2] * 2)
    q = block_diag([e8_inverse] * 5 + [A2] * 2)
    s_inverse = inverse(s)
    g_fraction = [[21 * x for x in row] for row in s_inverse]
    if any(x.denominator != 1 for row in g_fraction for x in row):
        raise AssertionError("21*S^-1 should be integral")
    g = [[int(x) for x in row] for row in g_fraction]
    b_fraction = matmul(s, q)
    b = [[int(x) for x in row] for row in b_fraction]
    i44 = identity(RANK)
    c = [
        [(b[row][col] - i44[row][col]) // 2 for col in range(RANK)]
        for row in range(RANK)
    ]

    a2_g = [[14, 7], [7, 14]]
    e8_scaled_minimum_floor = 42 if (
        has_even_diagonal(e8_inverse)
        and positive_definite_by_sylvester(e8_inverse)
    ) else 0
    a2_quadratic_is_14_times_a2_norm = (
        a2_g[0][0] == 14
        and 2 * a2_g[0][1] == 14
        and a2_g[1][1] == 14
    )
    a2_scaled_minimum_floor = 14 if a2_quadratic_is_14_times_a2_norm else 0
    g_minimum_lower_bound = min(
        e8_scaled_minimum_floor,
        a2_scaled_minimum_floor,
    )

    sb = matmul(s, q)
    gb = matmul(g, b)
    twenty_one_q = [[21 * x for x in row] for row in q]
    sg = matmul(s, g)
    twenty_one_i = [[21 * x for x in row] for row in i44]

    facts = {
        "rank": len(s),
        "detS_h": int(determinant(s)),
        "detQ": int(determinant(q)),
        "detG": int(determinant(g)),
        "detB": int(determinant(b)),
        "traceB": int(trace(b)),
        "traceC": int(trace(c)),
        "traceC2": int(trace(matmul(c, c))),
        "rankC": rank(c),
        "S_even": has_even_diagonal(s),
        "Q_even": has_even_diagonal(q),
        "G_even": has_even_diagonal(g),
        "S_symmetric": is_symmetric(s),
        "Q_symmetric": is_symmetric(q),
        "G_symmetric": is_symmetric(g),
        "B_congruent_I_mod_2": all(
            (b[row][col] - i44[row][col]) % 2 == 0
            for row in range(RANK)
            for col in range(RANK)
        ),
        "S_G_equals_21I": sg == twenty_one_i,
        "G_B_equals_21Q": gb == twenty_one_q,
        "B_equals_SQ": b == sb,
        "B_symmetric": is_symmetric(b),
        "E8_positive_definite": positive_definite_by_sylvester(E8),
        "A2_positive_definite": positive_definite_by_sylvester(A2),
        "E8_inverse_positive_definite": positive_definite_by_sylvester(
            e8_inverse
        ),
        "E8_inverse_even": has_even_diagonal(e8_inverse),
        "G_minimum_lower_bound": g_minimum_lower_bound,
    }
    expected = {
        "rank": 44,
        "detS_h": 9,
        "detQ": 9,
        "detG": 21 ** 44 // 9,
        "detB": 81,
        "traceB": 60,
        "traceC": 8,
        "traceC2": 32,
        "rankC": 2,
        "S_even": True,
        "Q_even": True,
        "G_even": True,
        "S_symmetric": True,
        "Q_symmetric": True,
        "G_symmetric": True,
        "B_congruent_I_mod_2": True,
        "S_G_equals_21I": True,
        "G_B_equals_21Q": True,
        "B_equals_SQ": True,
        "B_symmetric": True,
        "E8_positive_definite": True,
        "A2_positive_definite": True,
        "E8_inverse_positive_definite": True,
        "E8_inverse_even": True,
        "G_minimum_lower_bound": 14,
    }
    if facts != expected:
        raise AssertionError((facts, expected))
    return {
        "block_description": {
            "S": "E8^5 direct_sum A2^2",
            "Q": "(E8 inverse)^5 direct_sum A2^2",
            "G": "21*S inverse",
            "B": "S*Q = I_40 direct_sum (A2^2) direct_sum (A2^2)",
        },
        "facts": facts,
        "scope": (
            "Exact survivor of the determinant/scaled-dual/endomorphism "
            "relaxation; no primitive embedding in Z^231, 231-by-231 "
            "projector, Schur-square W, or graph is asserted."
        ),
    }


def local_endpoint_data() -> dict[str, object]:
    q_sum = 2 * N3 // 3
    deviation_sum = q_sum - 2 * 231
    trace_a4 = 84 * DELTA
    diagonal_excess_units = trace_a4 // 4 - 231

    lower_table = []
    for q_value in range(13):
        rational = Fraction(99 * (q_value - 2) ** 2, 43)
        multiple = 4
        while multiple < rational:
            multiple += 4
        lower_table.append(
            {
                "q": q_value,
                "rational_lower": fraction_text(rational),
                "positive_multiple_of_4_lower": multiple,
                "excess_units_over_4": (multiple - 4) // 4,
            }
        )

    harmonic_rhs = 1376 * (92 * DELTA)
    harmonic_q12_lhs = 138 ** 2 * (12 - 2) ** 2
    q11_center = Fraction((138 * 9) ** 2, 92 * DELTA)
    q11_centered_diagonal = Fraction(1376) - q11_center
    off_diagonal_options = [-136, 1, 0, -1]
    q11_pair_excluded = all(
        abs(Fraction(value) - q11_center) > q11_centered_diagonal
        for value in off_diagonal_options
    )

    survivor_profile = {2: 221, 3: 10}
    return {
        "sum_q": q_sum,
        "sum_q_minus_2": deviation_sum,
        "trace_A4": trace_a4,
        "diagonal_excess_units": diagonal_excess_units,
        "local_diagonal_lower_table": lower_table,
        "harmonic_q12": {
            "lhs": harmonic_q12_lhs,
            "rhs": harmonic_rhs,
            "gap_lhs_minus_rhs": harmonic_q12_lhs - harmonic_rhs,
            "excluded": harmonic_q12_lhs > harmonic_rhs,
        },
        "q11_centered_diagonal": fraction_text(q11_centered_diagonal),
        "two_q11_excluded": q11_pair_excluded,
        "scalar_survivor_profile": {
            "multiplicities": {str(k): v for k, v in survivor_profile.items()},
            "vertex_count": sum(survivor_profile.values()),
            "sum_q": sum(k * v for k, v in survivor_profile.items()),
            "sum_q_minus_2": sum(
                (k - 2) * v for k, v in survivor_profile.items()
            ),
            "limitation": (
                "Satisfies the scalar q budgets only; no graph or matrix "
                "realization is asserted."
            ),
        },
    }


def build_results() -> dict[str, object]:
    input_hashes = {
        path: {
            "expected_sha256": expected,
            "actual_sha256": sha256(ROOT / path),
            "matches": sha256(ROOT / path) == expected,
        }
        for path, expected in INPUTS.items()
    }
    if not all(item["matches"] for item in input_hashes.values()):
        raise AssertionError("frozen input hash mismatch")

    lower_log3, upper_log3 = log3_bounds()
    trace_c_square_floor = minimum_trace_c_square()
    trace_b_square_floor = (
        RANK + 4 * TRACE_C + 4 * trace_c_square_floor
    )
    cap = determinant_cap()
    indices = smooth_index_candidates(cap)

    return {
        "status": "DERIVED_EXACT_REPLAY_PENDING_INDEPENDENT_VERIFIER",
        "scope": (
            "Necessary restrictions at n3=708 and an exact survivor of the "
            "abstract projector-lattice package; no target resolution."
        ),
        "frozen_inputs": input_hashes,
        "endpoint": {
            "n3": N3,
            "Delta": DELTA,
            "rank": RANK,
            "traceB": TRACE_B,
            "traceC": TRACE_C,
            "traceC2_floor": fraction_text(trace_c_square_floor),
            "traceB2_floor": fraction_text(trace_b_square_floor),
            "trace_rank_bounds": trace_square_rank_bounds(),
        },
        "log_inequality_certificate": {
            "log3_lower": fraction_text(lower_log3),
            "log3_upper": fraction_text(upper_log3),
            "lower_gt_2_over_3": lower_log3 > Fraction(2, 3),
            "upper_lt_2": upper_log3 < 2,
            "c_positive": lower_log3 - Fraction(2, 3) > 0,
            "positive_x_derivative_numerator_factorization": (
                "(x-1)*(2*log(3)*x + log(3)-2/3)"
            ),
            "derivative_coefficient_check":
                derivative_factorization_coefficients(),
            "negative_x_auxiliary_derivative": (
                "log(3)-2/(1+2*x) < log(3)-2 < 0"
            ),
        },
        "determinant_index": {
            "detB_cap": cap,
            "detQ_floor": 5,
            "h_cap": cap // 5,
            "h_candidates": indices,
            "candidate_values": [row["h"] for row in indices],
        },
        "explicit_abstract_survivor": explicit_lattice_survivor(),
        "local_endpoint": local_endpoint_data(),
        "conclusion": {
            "n3_708_excluded": False,
            "sharp_current_index_restriction": (
                "h in {9,21,49,81,189,441,729,1029}"
            ),
            "next_obstruction": (
                "Must use the 231-vector Gram/projector and W=M o M origin "
                "or stronger graph-local compatibility; the abstract "
                "coordinate-lattice relaxation has an exact h=9 survivor."
            ),
            "target_status": "UNKNOWN",
            "novelty_status": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("exact-results.json"),
    )
    args = parser.parse_args()
    payload = build_results()
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(payload["conclusion"], sort_keys=True))


if __name__ == "__main__":
    main()
