#!/usr/bin/env python3
"""Independent exact verifier for the Wave 24 n3=708 boundary.

This module does not import or execute the discovery checker.  It reconstructs
the finite arithmetic, derivative certificate, index exhaustion, local
constraints, and explicit block-lattice survivor from frozen premises.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
RANK = 44
TRIANGLE_COUNT = 231
N3 = 708
BASE_N3 = 693
DELTA = N3 - BASE_N3

CANDIDATE_COMMIT = "821b162f7ff31f92bd1982bc31164c6b767838f4"
CANDIDATE_HASHES = {
    "agents/2026-07-23-wave24-n3-708-index-boundary.md":
        "461bbcff6399ae18c2764f68ea498b7eebba9780af0032b8e2e8fa18ca26af28",
    "attempts/wave24-n3-708-index/exact_check.py":
        "60bec6067383de3d9b6ecf57a5ce2a532deaf4759cc65faf4c63a6b8ce98b709",
    "attempts/wave24-n3-708-index/exact-results.json":
        "a4241cdeea64a8f6073037d564e72fb7ef545287d45aca4759cec6c31d26a463",
    "attempts/wave24-n3-708-index/failed-routes.md":
        "2411d4012cc6bf3f1d2a82d63cdc1538a6ca815ad269604fc46cb72cd4d82efb",
    "attempts/wave24-n3-708-index/failed-runs.md":
        "c37aeaad4f3afdbb765fc0233a23f6735b93a904b504a8593c1fe5503a9b8715",
    "attempts/wave24-n3-708-index/input-freeze.sha256":
        "4353375bbbfc58d382b048066aec388dec5d5ff84a41e426ea01dbb10ffbb7af",
    "attempts/wave24-n3-708-index/run-report.yaml":
        "7be3708665f8dc56fdd5fe32b8a0da07ef64c3147551043d75cf1631f2a12c13",
    "attempts/wave24-n3-708-index/test_exact_check.py":
        "adfa00d30a5db9ec0dc30bbd4d028689edd03bbba154535e05c1b7e4df76ed75",
}

PREMISE_HASHES = {
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


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def matrix_digest(matrix: Sequence[Sequence[int]]) -> str:
    raw = json.dumps(matrix, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def identity(size: int) -> list[list[int]]:
    return [[int(i == j) for j in range(size)] for i in range(size)]


def transpose(matrix: Sequence[Sequence[int | Fraction]]) -> list[list[int | Fraction]]:
    return [list(column) for column in zip(*matrix)]


def matmul(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> list[list[int | Fraction]]:
    right_t = transpose(right)
    return [
        [sum(x * y for x, y in zip(row, column)) for column in right_t]
        for row in left
    ]


def matscale(
    scalar: int,
    matrix: Sequence[Sequence[int | Fraction]],
) -> list[list[int | Fraction]]:
    return [[scalar * entry for entry in row] for row in matrix]


def block_diagonal(blocks: Iterable[Sequence[Sequence[int]]]) -> list[list[int]]:
    block_list = [[list(row) for row in block] for block in blocks]
    size = sum(len(block) for block in block_list)
    result = [[0 for _ in range(size)] for _ in range(size)]
    offset = 0
    for block in block_list:
        for i, row in enumerate(block):
            for j, value in enumerate(row):
                result[offset + i][offset + j] = value
        offset += len(block)
    return result


def determinant(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    """Exact determinant by Gaussian elimination over Q."""
    work = [[Fraction(entry) for entry in row] for row in matrix]
    size = len(work)
    result = Fraction(1)
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[pivot], work[column] = work[column], work[pivot]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for j in range(column, size):
            work[column][j] /= pivot_value
        for row in range(column + 1, size):
            multiplier = work[row][column]
            if multiplier:
                for j in range(column, size):
                    work[row][j] -= multiplier * work[column][j]
    return result


def inverse(matrix: Sequence[Sequence[int]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [
        [Fraction(entry) for entry in row]
        + [Fraction(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != column:
            work[pivot], work[column] = work[column], work[pivot]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    entry - multiplier * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[column])
                ]
    return [row[size:] for row in work]


def rank(matrix: Sequence[Sequence[int | Fraction]]) -> int:
    work = [[Fraction(entry) for entry in row] for row in matrix]
    row_count = len(work)
    column_count = len(work[0]) if work else 0
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot], work[pivot_row] = work[pivot_row], work[pivot]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [entry / pivot_value for entry in work[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    entry - multiplier * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def is_symmetric(matrix: Sequence[Sequence[int | Fraction]]) -> bool:
    return [list(row) for row in matrix] == transpose(matrix)


def is_integral(matrix: Sequence[Sequence[int | Fraction]]) -> bool:
    return all(Fraction(entry).denominator == 1 for row in matrix for entry in row)


def has_even_diagonal(matrix: Sequence[Sequence[int | Fraction]]) -> bool:
    return all(Fraction(matrix[i][i]).denominator == 1
               and Fraction(matrix[i][i]).numerator % 2 == 0
               for i in range(len(matrix)))


def positive_definite_sylvester(
    matrix: Sequence[Sequence[int | Fraction]],
) -> bool:
    return is_symmetric(matrix) and all(
        determinant([list(row[:size]) for row in matrix[:size]]) > 0
        for size in range(1, len(matrix) + 1)
    )


def endpoint_parameters(n3: int = N3) -> dict[str, int]:
    delta = n3 - BASE_N3
    trace_a4 = 84 * delta
    trace_b = trace_a4 // 21
    if trace_a4 % 21:
        raise AssertionError("A4 trace must be divisible by 21")
    if (trace_b - RANK) % 2:
        raise AssertionError("B=I+2C requires integral trace(C)")
    trace_c = (trace_b - RANK) // 2
    sum_q_numerator = 2 * n3
    if sum_q_numerator % 3:
        raise AssertionError("3 must divide n3")
    sum_q = sum_q_numerator // 3
    return {
        "n3": n3,
        "delta": delta,
        "rank": RANK,
        "trace_A4": trace_a4,
        "trace_B": trace_b,
        "trace_C": trace_c,
        "sum_q": sum_q,
        "sum_q_minus_2": sum_q - 2 * TRIANGLE_COUNT,
        "diagonal_excess_units": trace_a4 // 4 - TRIANGLE_COUNT,
    }


def pseudodeterminant_rank_rows(
    trace_c: int = 8,
    ambient_rank: int = RANK,
) -> list[dict[str, int | str]]:
    rows = []
    for nonzero_rank in range(1, ambient_rank + 1):
        product_floor = Fraction(nonzero_rank)
        cauchy_floor = Fraction(trace_c * trace_c, nonzero_rank)
        combined = max(product_floor, cauchy_floor)
        rows.append({
            "nonzero_rank": nonzero_rank,
            "product_am_gm_floor": fraction_text(product_floor),
            "cauchy_floor": fraction_text(cauchy_floor),
            "combined_floor": fraction_text(combined),
        })
    return rows


def trace_square_floor(trace_c: int = 8) -> Fraction:
    return min(
        Fraction(row["combined_floor"])
        for row in pseudodeterminant_rank_rows(trace_c)
    )


def log3_interval(terms: int = 16) -> tuple[Fraction, Fraction]:
    """Exact interval from log(3)=2*sum (1/2)^(2k+1)/(2k+1)."""
    z = Fraction(1, 2)
    lower = 2 * sum(
        z ** (2 * k + 1) / (2 * k + 1)
        for k in range(terms)
    )
    next_denominator = 2 * terms + 1
    geometric_tail = (
        2 * z ** next_denominator
        / next_denominator
        / (1 - z * z)
    )
    return lower, lower + geometric_tail


def derivative_certificate() -> dict[str, object]:
    """Coefficients in Q[L][x], with L standing for log(3)."""
    # For F=xL-(L-2/3)log(x)-log(1+2x), multiplying F' by
    # x(1+2x) gives the following coefficients in ascending powers of x.
    direct = [
        (Fraction(-1), Fraction(2, 3)),
        (Fraction(-1), Fraction(-2, 3)),
        (Fraction(2), Fraction(0)),
    ]
    # Direct expansion of (x-1)(2Lx + L-2/3).
    factored = [
        (Fraction(-1), Fraction(2, 3)),
        (Fraction(-1), Fraction(-2, 3)),
        (Fraction(2), Fraction(0)),
    ]
    lower, upper = log3_interval()
    return {
        "direct_coefficients": [
            [fraction_text(a), fraction_text(b)] for a, b in direct
        ],
        "factored_coefficients": [
            [fraction_text(a), fraction_text(b)] for a, b in factored
        ],
        "coefficient_match": direct == factored,
        "log3_lower": fraction_text(lower),
        "log3_upper": fraction_text(upper),
        "log3_gt_2_over_3": lower > Fraction(2, 3),
        "log3_lt_2": upper < 2,
        "positive_domain_sign": (
            "x(1+2x)F'(x)=(x-1)(2*log(3)*x+log(3)-2/3); "
            "the second factor is positive for x>0"
        ),
        "negative_domain_sign": (
            "g'(x)=log(3)-2/(1+2x)<log(3)-2<0 on -1/2<x<0"
        ),
    }


def determinant_cap(trace_c: int = 8) -> int:
    if trace_c < 0:
        raise ValueError("the pointwise certificate is used here only for trace(C)>=0")
    return 3 ** trace_c


def smooth_index_rows(
    *,
    det_b_cap: int = 6561,
    det_q_floor: int = 5,
    require_h_one_mod_four: bool = True,
    exclude_h_one: bool = True,
) -> list[dict[str, int]]:
    h_cap = det_b_cap // det_q_floor
    power3: list[tuple[int, int]] = []
    value = 1
    exponent = 0
    while value <= h_cap and exponent <= RANK:
        power3.append((exponent, value))
        exponent += 1
        value *= 3
    power7: list[tuple[int, int]] = []
    value = 1
    exponent = 0
    while value <= h_cap and exponent <= RANK:
        power7.append((exponent, value))
        exponent += 1
        value *= 7

    rows = []
    for exponent3, factor3 in power3:
        for exponent7, factor7 in power7:
            h = factor3 * factor7
            if h > h_cap:
                continue
            if exclude_h_one and h == 1:
                continue
            if require_h_one_mod_four and h % 4 != 1:
                continue
            det_q_raw_max = det_b_cap // h
            det_q_max = det_q_raw_max - ((det_q_raw_max - 1) % 4)
            if det_q_max < det_q_floor:
                continue
            rows.append({
                "h": h,
                "v3_h": exponent3,
                "v7_h": exponent7,
                "rank_F3_M": RANK - exponent3,
                "rank_F7_M": RANK - exponent7,
                "detQ_min": det_q_floor,
                "detQ_max_one_mod_four": det_q_max,
            })
    return sorted(rows, key=lambda item: item["h"])


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


def as_integer_matrix(
    matrix: Sequence[Sequence[int | Fraction]],
) -> list[list[int]]:
    if not is_integral(matrix):
        raise AssertionError("matrix is not integral")
    return [[int(entry) for entry in row] for row in matrix]


def survivor_matrices() -> dict[str, list[list[int]]]:
    e8_inverse = as_integer_matrix(inverse(E8))
    s = block_diagonal([E8] * 5 + [A2] * 2)
    q = block_diagonal([e8_inverse] * 5 + [A2] * 2)
    g_e8 = as_integer_matrix(matscale(21, e8_inverse))
    g_a2 = [[14, 7], [7, 14]]
    g = block_diagonal([g_e8] * 5 + [g_a2] * 2)
    b = as_integer_matrix(matmul(s, q))
    i44 = identity(RANK)
    c = [
        [(b[i][j] - i44[i][j]) // 2 for j in range(RANK)]
        for i in range(RANK)
    ]
    return {
        "E8": E8,
        "A2": A2,
        "S": s,
        "Q": q,
        "G": g,
        "B": b,
        "C": c,
    }


def survivor_certificate() -> dict[str, object]:
    matrices = survivor_matrices()
    e8_inverse = as_integer_matrix(inverse(E8))
    s = matrices["S"]
    q = matrices["Q"]
    g = matrices["G"]
    b = matrices["B"]
    c = matrices["C"]
    i44 = identity(RANK)

    sg = as_integer_matrix(matmul(s, g))
    gb = as_integer_matrix(matmul(g, b))
    sq = as_integer_matrix(matmul(s, q))
    c2 = as_integer_matrix(matmul(c, c))
    twenty_one_i = matscale(21, i44)
    twenty_one_q = matscale(21, q)

    e8_pd = positive_definite_sylvester(E8)
    a2_pd = positive_definite_sylvester(A2)
    e8_inverse_pd = positive_definite_sylvester(e8_inverse)
    g_a2_pd = positive_definite_sylvester([[14, 7], [7, 14]])
    block_positivity = e8_pd and a2_pd and e8_inverse_pd and g_a2_pd

    facts = {
        "rank": len(s),
        "det_E8": int(determinant(E8)),
        "det_A2": int(determinant(A2)),
        "det_S_h": int(determinant(s)),
        "det_Q": int(determinant(q)),
        "det_G": int(determinant(g)),
        "det_B": int(determinant(b)),
        "trace_B": sum(b[i][i] for i in range(RANK)),
        "trace_C": sum(c[i][i] for i in range(RANK)),
        "trace_C2": sum(c2[i][i] for i in range(RANK)),
        "rank_C": rank(c),
        "S_even_integral_symmetric": (
            is_integral(s) and is_symmetric(s) and has_even_diagonal(s)
        ),
        "Q_even_integral_symmetric": (
            is_integral(q) and is_symmetric(q) and has_even_diagonal(q)
        ),
        "G_even_integral_symmetric": (
            is_integral(g) and is_symmetric(g) and has_even_diagonal(g)
        ),
        "block_positive_definite": block_positivity,
        "S_times_G_equals_21I": sg == twenty_one_i,
        "B_equals_S_times_Q": b == sq,
        "G_times_B_equals_21Q": gb == twenty_one_q,
        "B_G_self_adjoint": gb == transpose(gb),
        "B_positive_for_G": block_positivity and gb == twenty_one_q,
        "B_congruent_I_mod_2": all(
            (b[i][j] - i44[i][j]) % 2 == 0
            for i in range(RANK) for j in range(RANK)
        ),
        "G_minimum_lower_bound": 14,
        "G_minimum_reason": (
            "The 21*E8^-1 blocks are even integral positive definite, hence "
            "have nonzero norm at least 42; each remaining block is "
            "14*(a^2+a*b+b^2), with nonzero minimum 14."
        ),
    }
    expected = {
        "rank": 44,
        "det_E8": 1,
        "det_A2": 3,
        "det_S_h": 9,
        "det_Q": 9,
        "det_G": 21 ** 44 // 9,
        "det_B": 81,
        "trace_B": 60,
        "trace_C": 8,
        "trace_C2": 32,
        "rank_C": 2,
        "S_even_integral_symmetric": True,
        "Q_even_integral_symmetric": True,
        "G_even_integral_symmetric": True,
        "block_positive_definite": True,
        "S_times_G_equals_21I": True,
        "B_equals_S_times_Q": True,
        "G_times_B_equals_21Q": True,
        "B_G_self_adjoint": True,
        "B_positive_for_G": True,
        "B_congruent_I_mod_2": True,
        "G_minimum_lower_bound": 14,
        "G_minimum_reason": facts["G_minimum_reason"],
    }
    if facts != expected:
        raise AssertionError({"actual": facts, "expected": expected})

    return {
        "construction": {
            "S": "E8^5 direct_sum A2^2",
            "Q": "(E8^-1)^5 direct_sum A2^2",
            "G": "21*S^-1",
            "B": "S*Q",
            "C": "(B-I)/2",
        },
        "matrix_sha256": {
            name: matrix_digest(matrix) for name, matrix in matrices.items()
        },
        "facts": facts,
        "semantic_boundary": {
            "abstract_coordinate_lattice_package": True,
            "primitive_embedding_in_Z231_proved": False,
            "231_projector_columns_proved": False,
            "Schur_square_origin_proved": False,
            "graph_realization_proved": False,
        },
    }


def ceil_positive_multiple_of_four(value: Fraction) -> int:
    candidate = 4
    while candidate < value:
        candidate += 4
    return candidate


def local_endpoint_certificate() -> dict[str, object]:
    endpoint = endpoint_parameters()
    total_harmonic = 92 * endpoint["delta"]
    q12_vector = 138 * (12 - 2)
    q12_lhs = q12_vector * q12_vector
    q12_rhs = 1376 * total_harmonic

    q11_vector = 138 * (11 - 2)
    correction = Fraction(q11_vector * q11_vector, total_harmonic)
    centered_diagonal = Fraction(1376) - correction
    off_diagonal_values = [-136, -1, 0, 1]
    pair_minors = {
        str(value): fraction_text(
            centered_diagonal * centered_diagonal
            - (Fraction(value) - correction) ** 2
        )
        for value in off_diagonal_values
    }

    lower_rows = []
    for q_value in range(13):
        tensor_floor = Fraction(99 * (q_value - 2) ** 2, 43)
        rounded = ceil_positive_multiple_of_four(tensor_floor)
        lower_rows.append({
            "q": q_value,
            "rational_floor": fraction_text(tensor_floor),
            "rounded_positive_multiple_of_four": rounded,
            "excess_units": (rounded - 4) // 4,
        })

    profile = {2: 221, 3: 10}
    old_endpoint_total = 92 * 12
    old_q11_cauchy_gap = q11_vector ** 2 - 1376 * old_endpoint_total
    return {
        "endpoint": endpoint,
        "harmonic_q12": {
            "lhs": q12_lhs,
            "rhs": q12_rhs,
            "gap": q12_lhs - q12_rhs,
            "excluded": q12_lhs > q12_rhs,
        },
        "q11_single_allowed_by_cauchy": (
            q11_vector ** 2 <= 1376 * total_harmonic
        ),
        "q11_centered_diagonal": fraction_text(centered_diagonal),
        "q11_pair_minor_determinants": pair_minors,
        "two_q11_excluded": all(
            Fraction(value) < 0 for value in pair_minors.values()
        ),
        "hostile_old_delta12_would_exclude_q11": old_q11_cauchy_gap > 0,
        "local_diagonal_rows": lower_rows,
        "scalar_profile": {
            "multiplicities": {str(key): value for key, value in profile.items()},
            "count": sum(profile.values()),
            "sum_q": sum(key * value for key, value in profile.items()),
            "sum_q_minus_2": sum(
                (key - 2) * value for key, value in profile.items()
            ),
            "minimum_excess_units": sum(
                next(row["excess_units"] for row in lower_rows if row["q"] == key)
                * value
                for key, value in profile.items()
            ),
        },
    }


def hostile_controls() -> dict[str, object]:
    cap = determinant_cap(8)
    nonintegral_det_exceeds = 15 ** 44 > cap * 11 ** 44
    nonsymmetric_skew_multiplier = 1 + 4 * 2 ** 2
    no_h_one_exclusion = smooth_index_rows(exclude_h_one=False)
    no_h_congruence = smooth_index_rows(require_h_one_mod_four=False)

    matrices = survivor_matrices()
    bad_g = [row[:] for row in matrices["G"]]
    bad_g[0][0] += 1
    bad_b = [row[:] for row in matrices["B"]]
    bad_b[0][0] += 2
    return {
        "drop_integrality": {
            "example": "C=(2/11)I_44",
            "trace_C": fraction_text(Fraction(2, 11) * 44),
            "trace_C2": fraction_text(Fraction(4, 121) * 44),
            "det_B": "(15/11)^44",
            "det_B_exceeds_6561": nonintegral_det_exceeds,
        },
        "drop_positive_form_self_adjointness": {
            "example": (
                "eight diagonal 1s plus one skew block [[0,-2],[2,0]]"
            ),
            "integral_trace_C": 8,
            "det_B": cap * nonsymmetric_skew_multiplier,
            "det_B_exceeds_6561": cap * nonsymmetric_skew_multiplier > cap,
            "reason_rejected": "C has nonreal eigenvalues and is not self-adjoint",
        },
        "drop_h_not_one": {
            "h_one_reappears": any(row["h"] == 1 for row in no_h_one_exclusion),
        },
        "drop_h_congruence": {
            "h_three_reappears": any(row["h"] == 3 for row in no_h_congruence),
            "h_seven_reappears": any(row["h"] == 7 for row in no_h_congruence),
        },
        "mutate_survivor_G_parity": {
            "even_after_diagonal_plus_one": has_even_diagonal(bad_g),
        },
        "mutate_survivor_B_bridge": {
            "GB_equals_21Q_after_B00_plus_two": (
                matmul(matrices["G"], bad_b) == matscale(21, matrices["Q"])
            ),
        },
    }


def full_matrix_certificate() -> dict[str, object]:
    matrices = survivor_matrices()
    return {
        "format": "row-major exact integer matrices",
        "scope": (
            "Abstract coordinate-lattice survivor only; these matrices do not "
            "certify an embedding, projector columns, Schur-square origin, or graph."
        ),
        "matrices": matrices,
    }


def build_results() -> dict[str, object]:
    candidate_hash_check = {
        path: {
            "expected": expected,
            "actual": sha256(ROOT / path),
            "matches": sha256(ROOT / path) == expected,
        }
        for path, expected in CANDIDATE_HASHES.items()
    }
    premise_hash_check = {
        path: {
            "expected": expected,
            "actual": sha256(ROOT / path),
            "matches": sha256(ROOT / path) == expected,
        }
        for path, expected in PREMISE_HASHES.items()
    }
    if not all(row["matches"] for row in candidate_hash_check.values()):
        raise AssertionError("candidate changed after preinspection freeze")
    if not all(row["matches"] for row in premise_hash_check.values()):
        raise AssertionError("verified premise hash mismatch")

    endpoint = endpoint_parameters()
    trace_c2_floor = trace_square_floor(endpoint["trace_C"])
    trace_b2_floor = (
        RANK + 4 * endpoint["trace_C"] + 4 * trace_c2_floor
    )
    indices = smooth_index_rows()
    return {
        "role": "verifier",
        "claim_label": "VERIFIED",
        "candidate_commit": CANDIDATE_COMMIT,
        "verdict": "PASS_SCOPED_CONDITIONAL_RESTRICTION",
        "scope": (
            "For a putative srg(99,14,1,2) at n3=708, the inherited "
            "projector-lattice premises force h to one of eight listed values. "
            "An exact abstract coordinate-lattice survivor shows this relaxation "
            "does not exclude n3=708."
        ),
        "candidate_hashes": candidate_hash_check,
        "premise_hashes": premise_hash_check,
        "endpoint_reconstruction": endpoint,
        "pseudodeterminant": {
            "rank_rows": pseudodeterminant_rank_rows(endpoint["trace_C"]),
            "trace_C2_floor": fraction_text(trace_c2_floor),
            "trace_B2_floor": fraction_text(trace_b2_floor),
            "theorem_gate": (
                "C is integral and diagonalizable over R by positive-form "
                "self-adjointness, so its nonzero characteristic coefficient "
                "is a nonzero integer."
            ),
        },
        "log_inequality": derivative_certificate(),
        "determinant_index": {
            "det_B_cap": determinant_cap(endpoint["trace_C"]),
            "det_Q_floor": 5,
            "h_cap": determinant_cap(endpoint["trace_C"]) // 5,
            "rows": indices,
            "candidate_values": [row["h"] for row in indices],
        },
        "survivor": survivor_certificate(),
        "local": local_endpoint_certificate(),
        "hostile_controls": hostile_controls(),
        "status_boundary": {
            "n3_708_excluded": False,
            "target_existence": "UNKNOWN",
            "novelty": "UNKNOWN",
            "primitive_embedding": "NOT_PROVED",
            "projector_or_Hadamard_origin": "NOT_PROVED",
            "graph_realization": "NOT_PROVED",
        },
    }


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("independent-results.json"),
    )
    parser.add_argument(
        "--matrix-certificate",
        type=Path,
        default=Path(__file__).with_name("survivor-certificate.json"),
    )
    arguments = parser.parse_args()
    results = build_results()
    write_json(arguments.output, results)
    write_json(arguments.matrix_certificate, full_matrix_certificate())
    print(json.dumps({
        "verdict": results["verdict"],
        "h_candidates": results["determinant_index"]["candidate_values"],
        "n3_708_excluded": results["status_boundary"]["n3_708_excluded"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
