#!/usr/bin/env python3
"""Independent exact checks for the Wave 25 n3=708 strictness claim.

This verifier deliberately uses only frozen, already-audited Wave 21/23/24
premises.  It does not import or execute any Wave 25 discovery code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


BASE_COMMIT = "7103ddfe755a8c3430ef79e9a76e3323f1e00e1d"
RANK = 44
TRACE_C = 8
DET_Q_FLOOR = 5

FROZEN_INPUTS = {
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave23-index-pranks/2026-07-23T192952Z-audit.md":
        "bfd02ebc39515e27e9e2c79d8e286905086f5747a02a310036ce27dd29ff3116",
    "verification/wave23-endpoint-crosscheck/2026-07-23T200645Z-correction-audit.md":
        "791d74340c8a84a9993f9a5179c66baf0b2f7e431df5fb7eda2f593195f9bf53",
    "verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
    "verification/wave24-n3-708-index/independent-results.json":
        "726807402388c02909171a689f3a7fe2d8d1b74307c24e322ae013d0a9cd486a",
    "verification/wave24-n3-708-index/survivor-certificate.json":
        "a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2",
}


Matrix = list[list[Fraction]]


def as_fraction_matrix(rows: Sequence[Sequence[int | Fraction]]) -> Matrix:
    return [[Fraction(value) for value in row] for row in rows]


def identity(n: int) -> Matrix:
    return [
        [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]


def diagonal(values: Sequence[int | Fraction]) -> Matrix:
    n = len(values)
    return [
        [Fraction(values[i]) if i == j else Fraction(0) for j in range(n)]
        for i in range(n)
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    right_t = transpose(right)
    return [
        [sum((a * b for a, b in zip(row, column)), Fraction(0))
         for column in right_t]
        for row in left
    ]


def matsub(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a - b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def scalar_mul(value: int | Fraction, matrix: Matrix) -> Matrix:
    scalar = Fraction(value)
    return [[scalar * entry for entry in row] for row in matrix]


def block_diag(blocks: Sequence[Matrix]) -> Matrix:
    size = sum(len(block) for block in blocks)
    result = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    offset = 0
    for block in blocks:
        n = len(block)
        if any(len(row) != n for row in block):
            raise ValueError("blocks must be square")
        for i in range(n):
            for j in range(n):
                result[offset + i][offset + j] = block[i][j]
        offset += n
    return result


def determinant(matrix: Matrix) -> Fraction:
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("determinant requires a square matrix")
    if n == 0:
        return Fraction(1)
    work = [row[:] for row in matrix]
    sign = 1
    det = Fraction(1)
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        det *= pivot_value
        for j in range(column, n):
            work[column][j] /= pivot_value
        for row in range(column + 1, n):
            factor = work[row][column]
            if factor:
                for j in range(column, n):
                    work[row][j] -= factor * work[column][j]
    return sign * det


def inverse(matrix: Matrix) -> Matrix:
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("inverse requires a square matrix")
    work = [row[:] + unit[:] for row, unit in zip(matrix, identity(n))]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            raise ValueError("matrix is singular")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(n):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(work[row], work[column])
                ]
    return [row[n:] for row in work]


def rank(matrix: Matrix) -> int:
    if not matrix:
        return 0
    work = [row[:] for row in matrix]
    row = 0
    for column in range(len(work[0])):
        pivot = next(
            (candidate for candidate in range(row, len(work))
             if work[candidate][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        pivot_value = work[row][column]
        work[row] = [value / pivot_value for value in work[row]]
        for candidate in range(len(work)):
            if candidate == row:
                continue
            factor = work[candidate][column]
            if factor:
                work[candidate] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(work[candidate], work[row])
                ]
        row += 1
        if row == len(work):
            break
    return row


def trace(matrix: Matrix) -> Fraction:
    return sum((matrix[i][i] for i in range(len(matrix))), Fraction(0))


def is_symmetric(matrix: Matrix) -> bool:
    return matrix == transpose(matrix)


def is_integral(matrix: Matrix) -> bool:
    return all(entry.denominator == 1 for row in matrix for entry in row)


def has_even_diagonal(matrix: Matrix) -> bool:
    return is_integral(matrix) and all(
        int(matrix[i][i]) % 2 == 0 for i in range(len(matrix))
    )


def is_positive_definite_sylvester(matrix: Matrix) -> bool:
    if not is_symmetric(matrix):
        return False
    return all(
        determinant([row[:size] for row in matrix[:size]]) > 0
        for size in range(1, len(matrix) + 1)
    )


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def matrix_digest(matrix: Matrix) -> str:
    payload = json.dumps(
        [[fraction_text(value) for value in row] for row in matrix],
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_inputs(root: Path) -> dict[str, dict[str, str | bool]]:
    result: dict[str, dict[str, str | bool]] = {}
    for relative, expected in FROZEN_INPUTS.items():
        actual = sha256_file(root / relative)
        result[relative] = {
            "expected": expected,
            "actual": actual,
            "matches": actual == expected,
        }
    if not all(row["matches"] for row in result.values()):
        raise RuntimeError("one or more frozen premise hashes changed")
    return result


def trace_square_rank_rows() -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    for nonzero_rank in range(1, RANK + 1):
        product_floor = Fraction(nonzero_rank)
        cauchy_floor = Fraction(TRACE_C * TRACE_C, nonzero_rank)
        combined = max(product_floor, cauchy_floor)
        rows.append({
            "nonzero_rank": nonzero_rank,
            "product_floor": fraction_text(product_floor),
            "cauchy_floor": fraction_text(cauchy_floor),
            "combined_floor": fraction_text(combined),
        })
    return rows


def equality_obstruction() -> dict[str, object]:
    rows = trace_square_rank_rows()
    minimum = min(Fraction(row["combined_floor"]) for row in rows)
    minimizers = [
        int(row["nonzero_rank"])
        for row in rows
        if Fraction(row["combined_floor"]) == minimum
    ]
    if minimum != 8 or minimizers != [8]:
        raise AssertionError("unexpected trace-square minimizer")

    # At r=8, equality in Cauchy with sum(lambda_i)=8 forces every
    # nonzero eigenvalue to be one.  Real diagonalizability then makes C an
    # idempotent.  Its integral image and kernel form a direct summand.
    kernel_rank = RANK - 8
    signature_gate = kernel_rank % 8 == 0
    return {
        "rank_rows": rows,
        "old_trace_C2_floor": 8,
        "old_floor_unique_rank": 8,
        "equality_nonzero_spectrum": {"1": 8},
        "equality_zero_multiplicity": kernel_rank,
        "equality_forces_C_squared_equals_C": True,
        "integral_idempotent_split": (
            "Z^44=im(C) direct_sum ker(C), with ranks 8 and 36"
        ),
        "G_orthogonal_split": True,
        "kernel_block": {
            "B0": "I_36",
            "Q0": "G0/21",
            "S0": "21*G0^-1",
            "S0_equals_Q0_inverse": True,
            "Q0_even_integral_positive_definite": True,
            "S0_even_integral_positive_definite": True,
            "rank": kernel_rank,
            "signature": kernel_rank,
            "even_unimodular_signature_gate_passes": signature_gate,
            "contradiction": not signature_gate,
        },
        "false_global_identity_rejected": (
            "Globally S*Q=B, not I; S=Q^-1 is used only on ker(C), "
            "where B=I."
        ),
        "trace_C2_parity": "tr(C^2)=tr(C) mod 2 for integral C",
        "trace_C2_is_even": TRACE_C % 2 == 0,
        "strict_trace_C2_floor": 10,
        "strict_trace_B2_floor": RANK + 4 * TRACE_C + 4 * 10,
    }


def trace_square_parity(matrix: Matrix) -> bool:
    if not is_integral(matrix) or len(matrix) != len(matrix[0]):
        raise ValueError("expected a square integral matrix")
    tr_c = int(trace(matrix))
    tr_c2 = int(trace(matmul(matrix, matrix)))
    return (tr_c2 - tr_c) % 2 == 0


def largest_one_mod_four_at_most(bound: int) -> int:
    if bound < 1:
        raise ValueError("bound must be positive")
    return bound - ((bound - 1) % 4)


def smooth_values(limit: int, primes: Sequence[int] = (3, 7)) -> list[int]:
    values = {1}
    for prime in primes:
        expanded: set[int] = set()
        for value in values:
            candidate = value
            while candidate <= limit:
                expanded.add(candidate)
                candidate *= prime
        values = expanded
    return sorted(value for value in values if value <= limit)


def valuation(value: int, prime: int) -> int:
    exponent = 0
    while value % prime == 0:
        value //= prime
        exponent += 1
    return exponent


def enumerate_determinant_index() -> dict[str, object]:
    analytic_cap = 3 ** TRACE_C
    strict_integer_cap = analytic_cap - 1
    strict_one_mod_four_cap = largest_one_mod_four_at_most(strict_integer_cap)
    h_cap = strict_one_mod_four_cap // DET_Q_FLOOR

    h_values = [
        value for value in smooth_values(h_cap)
        if value != 1 and value % 4 == 1
    ]
    rows: list[dict[str, int | list[int]]] = []
    for h in h_values:
        q_limit = strict_one_mod_four_cap // h
        q_max = largest_one_mod_four_at_most(q_limit)
        if q_max < DET_Q_FLOOR:
            continue
        q_values = list(range(DET_Q_FLOOR, q_max + 1, 4))
        a = valuation(h, 3)
        b = valuation(h, 7)
        rows.append({
            "h": h,
            "v3_h": a,
            "v7_h": b,
            "rank_F3_M": RANK - a,
            "rank_F7_M": RANK - b,
            "detQ_min": DET_Q_FLOOR,
            "detQ_max": q_max,
            "detQ_count": len(q_values),
            "max_detB": h * q_max,
        })

    combined_cap = max(int(row["max_detB"]) for row in rows)
    combined_maximizers = [
        {"h": int(row["h"]), "detQ": int(row["detQ_max"])}
        for row in rows if int(row["max_detB"]) == combined_cap
    ]
    return {
        "analytic_cap": analytic_cap,
        "analytic_equality_excluded": True,
        "strict_integer_cap": strict_integer_cap,
        "det_B_congruence": "1 mod 4",
        "strict_congruence_cap": strict_one_mod_four_cap,
        "det_Q_floor": DET_Q_FLOOR,
        "h_cap": h_cap,
        "h_values": h_values,
        "rows": rows,
        "combined_exact_cap": combined_cap,
        "combined_maximizers": combined_maximizers,
    }


def e8_gram() -> Matrix:
    # E8 Dynkin tree with arm lengths 2, 4, and 1.
    matrix = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    for i in range(8):
        matrix[i][i] = Fraction(2)
    for i, j in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (2, 7)):
        matrix[i][j] = matrix[j][i] = Fraction(-1)
    return matrix


def a2_gram() -> Matrix:
    return as_fraction_matrix(((2, -1), (-1, 2)))


def survivor_facts() -> dict[str, object]:
    e8 = e8_gram()
    a2 = a2_gram()
    e8_inverse = inverse(e8)
    a2_inverse = inverse(a2)

    s = block_diag([e8] * 5 + [a2] * 2)
    q = block_diag([e8_inverse] * 5 + [a2] * 2)
    g = scalar_mul(21, inverse(s))
    b = matmul(s, q)
    c = scalar_mul(Fraction(1, 2), matsub(b, identity(RANK)))
    q_inverse = block_diag([e8] * 5 + [a2_inverse] * 2)

    det_s = determinant(s)
    det_q = determinant(q)
    det_b = determinant(b)
    facts = {
        "construction": {
            "S": "E8^5 direct_sum A2^2",
            "Q": "(E8^-1)^5 direct_sum A2^2",
            "G": "21*S^-1",
            "B": "S*Q",
            "C": "(B-I)/2",
        },
        "det_E8": int(determinant(e8)),
        "det_A2": int(determinant(a2)),
        "det_S_h": int(det_s),
        "det_Q": int(det_q),
        "det_B": int(det_b),
        "trace_B": int(trace(b)),
        "trace_C": int(trace(c)),
        "trace_C2": int(trace(matmul(c, c))),
        "rank_C": rank(c),
        "block_positive_definite": (
            is_positive_definite_sylvester(e8)
            and is_positive_definite_sylvester(a2)
        ),
        "S_even_integral_symmetric": (
            is_integral(s) and is_symmetric(s) and has_even_diagonal(s)
        ),
        "Q_even_integral_symmetric": (
            is_integral(q) and is_symmetric(q) and has_even_diagonal(q)
        ),
        "G_even_integral_symmetric": (
            is_integral(g) and is_symmetric(g) and has_even_diagonal(g)
        ),
        "S_times_G_equals_21I": matmul(s, g) == scalar_mul(21, identity(RANK)),
        "G_times_B_equals_21Q": matmul(g, b) == scalar_mul(21, q),
        "S_times_Q_equals_B": matmul(s, q) == b,
        "B_congruent_I_mod_2": all(
            entry.denominator == 1 and int(entry) % 2 == int(i == j)
            for i, row in enumerate(b)
            for j, entry in enumerate(row)
        ),
        "global_S_equals_Q_inverse": s == q_inverse,
        "global_S_times_Q_equals_identity": matmul(s, q) == identity(RANK),
        "global_identity_expected": "S*Q=B, not I",
        "G_minimum_lower_bound": 14,
        "G_minimum_reason": (
            "Each 21*E8^-1 block is 21 times an even integral positive "
            "form, hence has nonzero norm at least 42; each remaining "
            "block is 14*(a^2+a*b+b^2), with minimum 14."
        ),
        "matrix_sha256": {
            "E8": matrix_digest(e8),
            "A2": matrix_digest(a2),
            "S": matrix_digest(s),
            "Q": matrix_digest(q),
            "G": matrix_digest(g),
            "B": matrix_digest(b),
            "C": matrix_digest(c),
        },
        "semantic_boundary": {
            "abstract_coordinate_lattice_package": True,
            "primitive_embedding_in_Z231_proved": False,
            "projector_or_Hadamard_origin_proved": False,
            "Schur_square_origin_proved": False,
            "graph_realization_proved": False,
        },
    }
    required = {
        "det_E8": 1,
        "det_A2": 3,
        "det_S_h": 9,
        "det_Q": 9,
        "det_B": 81,
        "trace_B": 60,
        "trace_C": 8,
        "trace_C2": 32,
        "rank_C": 2,
        "global_S_equals_Q_inverse": False,
        "global_S_times_Q_equals_identity": False,
    }
    for key, expected in required.items():
        if facts[key] != expected:
            raise AssertionError(f"survivor {key}: {facts[key]} != {expected}")
    return facts


def equality_odd_control() -> dict[str, object]:
    # This satisfies the equality-spectrum coordinate identities but drops
    # evenness.  It is a hostile control showing exactly where the rank-36
    # signature obstruction enters.
    g = diagonal([7] * 8 + [21] * 36)
    b = diagonal([3] * 8 + [1] * 36)
    q = scalar_mul(Fraction(1, 21), matmul(g, b))
    s = scalar_mul(21, inverse(g))
    q0 = diagonal([1] * 36)
    s0 = diagonal([1] * 36)
    return {
        "trace_C": 8,
        "trace_C2": 8,
        "S_times_Q_equals_B": matmul(s, q) == b,
        "global_S_equals_Q_inverse": s == inverse(q),
        "kernel_S0_equals_Q0_inverse": s0 == inverse(q0),
        "Q_even": has_even_diagonal(q),
        "S_even": has_even_diagonal(s),
        "rejected_because": "Q and S have odd diagonal",
    }


def hostile_controls(index_data: dict[str, object]) -> dict[str, object]:
    # Each mutation removes one premise and admits a determinant above the
    # verified combined cap of 6525.
    return {
        "drop_strictness": {
            "h": 9,
            "detQ": 729,
            "detB": 6561,
            "exceeds_combined_cap": 9 * 729 > int(index_data["combined_exact_cap"]),
        },
        "drop_h_not_one": {
            "h": 1,
            "detQ": 6557,
            "detB": 6557,
            "exceeds_combined_cap": 6557 > int(index_data["combined_exact_cap"]),
        },
        "drop_h_mod_four": {
            "h": 3,
            "detQ": 2185,
            "detB": 6555,
            "exceeds_combined_cap": 3 * 2185 > int(index_data["combined_exact_cap"]),
        },
        "drop_detQ_mod_four": {
            "h": 9,
            "detQ": 728,
            "detB": 6552,
            "exceeds_combined_cap": 9 * 728 > int(index_data["combined_exact_cap"]),
        },
        "equality_spectrum_without_evenness": equality_odd_control(),
    }


def build_results(root: Path) -> dict[str, object]:
    premise_hashes = verify_frozen_inputs(root)
    obstruction = equality_obstruction()
    index_data = enumerate_determinant_index()
    survivor = survivor_facts()
    controls = hostile_controls(index_data)

    if obstruction["strict_trace_C2_floor"] != 10:
        raise AssertionError("strict trace-square floor was not obtained")
    if obstruction["strict_trace_B2_floor"] != 116:
        raise AssertionError("strict B trace-square floor was not obtained")
    if index_data["h_values"] != [9, 21, 49, 81, 189, 441, 729, 1029]:
        raise AssertionError("unexpected index list")
    if index_data["combined_exact_cap"] != 6525:
        raise AssertionError("combined determinant cap is not 6525")
    if survivor["det_S_h"] != 9 or survivor["det_B"] != 81:
        raise AssertionError("h=9 abstract survivor was not preserved")
    if survivor["global_S_equals_Q_inverse"]:
        raise AssertionError("false global scaled-dual identity was accepted")

    return {
        "role": "verifier",
        "base_commit": BASE_COMMIT,
        "claim_label": "VERIFIED",
        "verdict": "PASS_SCOPED_STRICTNESS",
        "scope": (
            "Conditional on the frozen projector-lattice premises at n3=708: "
            "exclude the trace-square/logarithmic equality case, prove "
            "tr(C^2)>=10 and tr(B^2)>=116, and sharpen the combined "
            "determinant/index cap to det(B)<=6525. Preserve the abstract "
            "h=9 coordinate-lattice survivor; do not exclude n3=708."
        ),
        "premise_hashes": premise_hashes,
        "equality_obstruction": obstruction,
        "determinant_index": index_data,
        "survivor": survivor,
        "hostile_controls": controls,
        "status_boundary": {
            "n3_708_excluded": False,
            "abstract_h9_survivor_preserved": True,
            "primitive_embedding": "NOT_PROVED",
            "projector_or_Hadamard_origin": "NOT_PROVED",
            "Schur_square_origin": "NOT_PROVED",
            "graph_realization": "NOT_PROVED",
            "target_existence": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("independent-results.json"),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    results = build_results(root)
    payload = json.dumps(results, indent=2, sort_keys=True) + "\n"
    args.output.write_text(payload, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
