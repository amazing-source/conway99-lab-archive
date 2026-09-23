#!/usr/bin/env python3
"""Exact checks for the Wave 25 strict n3=708 determinant refinement.

The new mathematical step is a lattice-theoretic exclusion of equality in
the Wave 24 trace-square and logarithmic determinant bounds.  This checker
certifies the finite arithmetic, the integral-splitting bookkeeping, the
complete h/det(Q) enumeration, the frozen inputs, and explicit hostile
controls.  The van der Blij signature theorem is applied in the accompanying
report, not proved by this program.
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
N3 = 708
DELTA = N3 - 693
TRACE_B = 4 * DELTA
TRACE_C = (TRACE_B - RANK) // 2
EQUALITY_IMAGE_RANK = 8
EQUALITY_KERNEL_RANK = RANK - EQUALITY_IMAGE_RANK
OLD_DETERMINANT_CAP = 3**TRACE_C

INPUTS = {
    "verification/wave21-lattice-extension/"
    "2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave23-index-pranks/"
    "2026-07-23T192952Z-audit.md":
        "bfd02ebc39515e27e9e2c79d8e286905086f5747a02a310036ce27dd29ff3116",
    "verification/wave23-endpoint-crosscheck/"
    "2026-07-23T200645Z-correction-audit.md":
        "791d74340c8a84a9993f9a5179c66baf0b2f7e431df5fb7eda2f593195f9bf53",
    "verification/wave24-n3-708-index/"
    "2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
    "verification/wave24-n3-708-index/independent-results.json":
        "726807402388c02909171a689f3a7fe2d8d1b74307c24e322ae013d0a9cd486a",
    "verification/wave24-n3-708-index/survivor-certificate.json":
        "a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2",
    "verification/wave24-n3-708-index/theorem-applicability.md":
        "bea67ef5cac84c34ed7ed336ee947532a25a27b05dda653a50693af52cc4b2d1",
}


Number = int | Fraction
Matrix = list[list[Number]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def identity(size: int) -> Matrix:
    return [[int(row == col) for col in range(size)] for row in range(size)]


def diagonal_matrix(values: Sequence[Number]) -> Matrix:
    return [
        [values[row] if row == col else 0 for col in range(len(values))]
        for row in range(len(values))
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    columns = list(zip(*right))
    return [
        [sum(x * y for x, y in zip(row, column)) for column in columns]
        for row in left
    ]


def trace(matrix: Matrix) -> Number:
    return sum(matrix[index][index] for index in range(len(matrix)))


def block_diag(blocks: Iterable[Matrix]) -> Matrix:
    blocks = list(blocks)
    size = sum(len(block) for block in blocks)
    result: Matrix = [[0] * size for _ in range(size)]
    offset = 0
    for block in blocks:
        for row in range(len(block)):
            for col in range(len(block)):
                result[offset + row][offset + col] = block[row][col]
        offset += len(block)
    return result


def determinant(matrix: Matrix) -> Fraction:
    """Exact determinant by rational Gaussian elimination."""
    work = [[Fraction(value) for value in row] for row in matrix]
    size = len(work)
    result = Fraction(1)
    for col in range(size):
        pivot = next(
            (row for row in range(col, size) if work[row][col]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            result = -result
        pivot_value = work[col][col]
        result *= pivot_value
        work[col] = [value / pivot_value for value in work[col]]
        for row in range(col + 1, size):
            scale = work[row][col]
            if scale:
                work[row] = [
                    value - scale * pivot_entry
                    for value, pivot_entry in zip(work[row], work[col])
                ]
    return result


def is_integral_matrix(matrix: Matrix) -> bool:
    return all(Fraction(value).denominator == 1 for row in matrix for value in row)


def is_symmetric(matrix: Matrix) -> bool:
    return matrix == transpose(matrix)


def is_even_integral_form(matrix: Matrix) -> bool:
    return (
        is_integral_matrix(matrix)
        and is_symmetric(matrix)
        and all(Fraction(matrix[i][i]).numerator % 2 == 0 for i in range(len(matrix)))
    )


def positive_definite_by_sylvester(matrix: Matrix) -> bool:
    return all(
        determinant([row[:size] for row in matrix[:size]]) > 0
        for size in range(1, len(matrix) + 1)
    )


def equality_rank_rows() -> list[dict[str, str | int]]:
    """Wave 24 rank-by-rank floor from Cauchy and pseudodeterminant AM-GM."""
    rows: list[dict[str, str | int]] = []
    for nonzero_rank in range(1, RANK + 1):
        cauchy = Fraction(TRACE_C**2, nonzero_rank)
        product_floor = Fraction(nonzero_rank)
        rows.append(
            {
                "nonzero_rank": nonzero_rank,
                "cauchy_floor": fraction_text(cauchy),
                "pseudodeterminant_floor": fraction_text(product_floor),
                "combined_floor": fraction_text(max(cauchy, product_floor)),
            }
        )
    return rows


def trace_square_parity_certificate() -> dict[str, object]:
    """Certify tr(C^2)=tr(C) mod 2 and exhaust the 2x2 residue control."""
    checked = 0
    for a00 in range(2):
        for a01 in range(2):
            for a10 in range(2):
                for a11 in range(2):
                    matrix = [[a00, a01], [a10, a11]]
                    if int(trace(matmul(matrix, matrix))) % 2 != int(trace(matrix)) % 2:
                        raise AssertionError("trace-square parity residue failure")
                    checked += 1
    return {
        "identity": (
            "tr(C^2)=sum_i C_ii^2+2*sum_{i<j} C_ij*C_ji "
            "=tr(C) (mod 2)"
        ),
        "traceC_mod_2": TRACE_C % 2,
        "traceC2_mod_2": TRACE_C % 2,
        "two_by_two_residue_matrices_checked": checked,
    }


def equality_split_certificate() -> dict[str, object]:
    """Bookkeeping for the excluded equality case tr(C^2)=8."""
    rows = equality_rank_rows()
    minimizers = [
        int(row["nonzero_rank"])
        for row in rows
        if Fraction(str(row["combined_floor"])) == 8
    ]
    if minimizers != [EQUALITY_IMAGE_RANK]:
        raise AssertionError("unexpected equality rank")

    canonical_c = diagonal_matrix(
        [1] * EQUALITY_IMAGE_RANK + [0] * EQUALITY_KERNEL_RANK
    )
    canonical_i = identity(RANK)
    canonical_complement = [
        [canonical_i[row][col] - canonical_c[row][col] for col in range(RANK)]
        for row in range(RANK)
    ]
    if matmul(canonical_c, canonical_c) != canonical_c:
        raise AssertionError("canonical equality matrix is not idempotent")
    if matmul(canonical_c, canonical_complement) != [[0] * RANK for _ in range(RANK)]:
        raise AssertionError("canonical equality projections do not split")

    return {
        "old_traceC2_floor": 8,
        "unique_equality_nonzero_rank": minimizers[0],
        "equality_nonzero_eigenvalues": [1] * EQUALITY_IMAGE_RANK,
        "reason": (
            "Equality in Cauchy at rank 8 and trace 8 makes all eight "
            "nonzero real eigenvalues equal to 1; self-adjointness makes C "
            "diagonalizable, hence C^2=C."
        ),
        "integral_split": {
            "identity": "L=im(C) direct_sum ker(C)",
            "integrality_gate": (
                "C and I-C are integral endomorphisms, so both summands and "
                "the decomposition of every lattice vector are integral."
            ),
            "image_rank": EQUALITY_IMAGE_RANK,
            "kernel_rank": EQUALITY_KERNEL_RANK,
            "orthogonality_gate": (
                "Orthogonality: <Cx,y>=<x,Cy>=0 for x arbitrary and "
                "y in ker(C)."
            ),
            "canonical_idempotent_check": True,
        },
        "scaled_dual_forms": {
            "S_definition": "S=21*G^-1",
            "S_integrality": (
                "21L* subset L makes the coordinate matrix 21*G^-1 integral."
            ),
            "S_evenness": (
                "The norm of the i-th 21-dual basis vector is 21*S_ii; "
                "L is even and 21 is odd, so every S_ii is even."
            ),
            "Q_definition": "Q=G*B/21",
            "Q_evenness": "Inherited from Q=X^T*(M o M)*X.",
            "global_product": "S*Q=B",
            "kernel_product": "S_K*Q_K=I_36 because B restricted to ker(C) is I.",
            "kernel_forms": (
                "S_K and Q_K are positive-definite even integral inverse "
                "matrices, hence each has determinant 1."
            ),
        },
        "signature_obstruction": {
            "kernel_rank": EQUALITY_KERNEL_RANK,
            "kernel_rank_mod_8": EQUALITY_KERNEL_RANK % 8,
            "positive_even_unimodular_required": True,
            "van_der_blij_contradiction": signature_obstructs_even_unimodular(
                EQUALITY_KERNEL_RANK,
                even=True,
                integral=True,
                unimodular=True,
                positive_definite=True,
            ),
        },
    }


def signature_obstructs_even_unimodular(
    rank: int,
    *,
    even: bool,
    integral: bool,
    unimodular: bool,
    positive_definite: bool,
) -> bool:
    """Applicability/result of the classical signature-divisibility theorem."""
    hypotheses = even and integral and unimodular and positive_definite
    return hypotheses and rank % 8 != 0


def refined_trace_data() -> dict[str, object]:
    equality = equality_split_certificate()
    if not equality["signature_obstruction"]["van_der_blij_contradiction"]:
        raise AssertionError("equality case was not excluded")
    parity = trace_square_parity_certificate()
    trace_c2_floor = 10
    trace_b2_floor = RANK + 4 * TRACE_C + 4 * trace_c2_floor
    return {
        "traceC": TRACE_C,
        "old_traceC2_floor": 8,
        "equality_excluded": True,
        "traceC2_integral": True,
        "traceC2_parity": parity["traceC2_mod_2"],
        "refined_traceC2_floor": trace_c2_floor,
        "refined_traceB2_floor": trace_b2_floor,
        "traceB2_identity": "tr(B^2)=44+4*tr(C)+4*tr(C^2)",
    }


def determinant_mod_four() -> int:
    """det(I+2C)=1+2 tr(C) modulo four."""
    return (1 + 2 * TRACE_C) % 4


def powers(base: int, maximum: int) -> list[tuple[int, int]]:
    rows: list[tuple[int, int]] = []
    value = 1
    exponent = 0
    while value <= maximum:
        rows.append((exponent, value))
        exponent += 1
        value *= base
    return rows


def enumerate_factor_pairs(
    *,
    limit_exclusive: int = OLD_DETERMINANT_CAP,
    detq_minimum: int = 5,
    require_h_one_mod_four: bool = True,
    require_h_not_one: bool = True,
    detq_filter: str = "one_mod_four",
    require_product_one_mod_four: bool = False,
) -> list[dict[str, int]]:
    """Complete finite enumeration of h=3^a*7^b and det(Q)."""
    if limit_exclusive <= 1:
        return []
    if detq_filter not in {"one_mod_four", "odd", "any"}:
        raise ValueError("unknown det(Q) filter")
    maximum_h = (limit_exclusive - 1) // detq_minimum
    pairs: list[dict[str, int]] = []
    for exponent_3, power_3 in powers(3, maximum_h):
        for exponent_7, power_7 in powers(7, maximum_h // power_3):
            h = power_3 * power_7
            if require_h_not_one and h == 1:
                continue
            if require_h_one_mod_four and h % 4 != 1:
                continue
            maximum_detq = (limit_exclusive - 1) // h
            for detq in range(detq_minimum, maximum_detq + 1):
                if detq_filter == "one_mod_four" and detq % 4 != 1:
                    continue
                if detq_filter == "odd" and detq % 2 != 1:
                    continue
                detb = h * detq
                if require_product_one_mod_four and detb % 4 != 1:
                    continue
                pairs.append(
                    {
                        "h": h,
                        "v3_h": exponent_3,
                        "v7_h": exponent_7,
                        "rank_F3_M": RANK - exponent_3,
                        "rank_F7_M": RANK - exponent_7,
                        "detQ": detq,
                        "detB": detb,
                    }
                )
    return sorted(pairs, key=lambda row: (row["h"], row["detQ"]))


def factor_pair_summary() -> dict[str, object]:
    pairs = enumerate_factor_pairs()
    h_values = sorted({row["h"] for row in pairs})
    rows: list[dict[str, object]] = []
    for h in h_values:
        group = [row for row in pairs if row["h"] == h]
        first = group[0]
        detq_values = [row["detQ"] for row in group]
        rows.append(
            {
                "h": h,
                "v3_h": first["v3_h"],
                "v7_h": first["v7_h"],
                "rank_F3_M": first["rank_F3_M"],
                "rank_F7_M": first["rank_F7_M"],
                "detQ_values": detq_values,
                "detQ_count": len(detq_values),
                "detQ_min": min(detq_values),
                "detQ_max": max(detq_values),
                "detB_max": h * max(detq_values),
            }
        )
    maximum_pair = max(pairs, key=lambda row: row["detB"])
    return {
        "strict_limit": OLD_DETERMINANT_CAP,
        "conditions": [
            "h=3^a*7^b",
            "h=1 mod 4",
            "h!=1",
            "det(Q)=1 mod 4",
            "det(Q)>=5",
            "h*det(Q)<6561",
        ],
        "complete_pair_count": len(pairs),
        "h_values": h_values,
        "rows": rows,
        "combined_best_pair": maximum_pair,
        "combined_detB_cap": maximum_pair["detB"],
    }


def congruence_and_cap_controls() -> dict[str, object]:
    valid = enumerate_factor_pairs()
    omit_detq_mod_four = enumerate_factor_pairs(detq_filter="odd")
    omit_all_detq_parity = enumerate_factor_pairs(detq_filter="any")
    omit_h_mod_four = enumerate_factor_pairs(
        require_h_one_mod_four=False,
        detq_filter="one_mod_four",
    )
    omit_h_mod_four_but_keep_product = enumerate_factor_pairs(
        require_h_one_mod_four=False,
        detq_filter="odd",
        require_product_one_mod_four=True,
    )
    wrong_nonstrict = enumerate_factor_pairs(limit_exclusive=OLD_DETERMINANT_CAP + 1)

    def maximum_row(rows: list[dict[str, int]]) -> dict[str, int]:
        return max(rows, key=lambda row: row["detB"])

    wrong_equality_pairs = [
        row for row in wrong_nonstrict if row["detB"] == OLD_DETERMINANT_CAP
    ]
    return {
        "valid": {
            "pair_count": len(valid),
            "maximum": maximum_row(valid),
        },
        "omit_detQ_one_mod_four_but_keep_odd": {
            "pair_count": len(omit_detq_mod_four),
            "maximum": maximum_row(omit_detq_mod_four),
        },
        "omit_all_detQ_parity_and_congruence": {
            "pair_count": len(omit_all_detq_parity),
            "maximum": maximum_row(omit_all_detq_parity),
        },
        "omit_h_one_mod_four": {
            "pair_count": len(omit_h_mod_four),
            "maximum": maximum_row(omit_h_mod_four),
            "extra_h_values": sorted(
                {row["h"] for row in omit_h_mod_four}
                - {row["h"] for row in valid}
            ),
        },
        "omit_h_one_mod_four_but_keep_detB_one_mod_four": {
            "pair_count": len(omit_h_mod_four_but_keep_product),
            "maximum": maximum_row(omit_h_mod_four_but_keep_product),
        },
        "wrongly_allow_analytic_equality": {
            "pair_count": len(wrong_nonstrict),
            "maximum": maximum_row(wrong_nonstrict),
            "spurious_detB_6561_pairs": wrong_equality_pairs,
        },
    }


def determinant_refinement() -> dict[str, object]:
    pairs = factor_pair_summary()
    direct_mod_four_cap = max(
        value
        for value in range(1, OLD_DETERMINANT_CAP)
        if value % 4 == determinant_mod_four()
    )
    return {
        "wave24_analytic_cap": OLD_DETERMINANT_CAP,
        "equality_characterization": (
            "Equality forces every nonzero eigenvalue of C to be 1, hence "
            "the excluded integral idempotent equality case."
        ),
        "strict_analytic_result": "det(B)<6561",
        "largest_integer_below_6561": OLD_DETERMINANT_CAP - 1,
        "detB_mod_4": determinant_mod_four(),
        "direct_mod_four_cap": direct_mod_four_cap,
        "factorized_congruence_cap": pairs["combined_detB_cap"],
        "factorized_maximizer": pairs["combined_best_pair"],
    }


def frozen_survivor_control() -> dict[str, object]:
    prior = load_json(
        ROOT / "verification/wave24-n3-708-index/independent-results.json"
    )
    certificate = load_json(
        ROOT / "verification/wave24-n3-708-index/survivor-certificate.json"
    )
    matrices = certificate["matrices"]
    s = matrices["S"]
    q = matrices["Q"]
    b = matrices["B"]
    product = matmul(s, q)
    i44 = identity(RANK)
    facts = prior["survivor"]["facts"]
    if product != b:
        raise AssertionError("frozen survivor no longer satisfies S*Q=B")
    if product == i44:
        raise AssertionError("hostile global inverse control unexpectedly failed")
    required = {
        "det_S_h": 9,
        "det_Q": 9,
        "det_B": 81,
        "trace_B": 60,
        "trace_C": 8,
        "trace_C2": 32,
    }
    for key, expected in required.items():
        if facts[key] != expected:
            raise AssertionError(f"frozen survivor mismatch for {key}")
    return {
        "source_status": prior["claim_label"],
        "h": facts["det_S_h"],
        "detQ": facts["det_Q"],
        "detB": facts["det_B"],
        "traceB": facts["trace_B"],
        "traceC": facts["trace_C"],
        "traceC2": facts["trace_C2"],
        "S_times_Q_equals_B": product == b,
        "S_times_Q_equals_identity": product == i44,
        "false_global_statement_rejected": product != i44,
        "correct_scope": (
            "S*Q=B globally; S_K*Q_K=I only on the hypothetical equality "
            "kernel where B_K=I."
        ),
        "semantic_boundary": prior["survivor"]["semantic_boundary"],
    }


def omitted_evenness_control() -> dict[str, object]:
    """Equality package surviving after the even-form hypotheses are dropped."""
    c = diagonal_matrix([1] * EQUALITY_IMAGE_RANK + [0] * EQUALITY_KERNEL_RANK)
    b = diagonal_matrix([3] * EQUALITY_IMAGE_RANK + [1] * EQUALITY_KERNEL_RANK)
    s = identity(RANK)
    g = diagonal_matrix([21] * RANK)
    q = b
    twenty_one_i = diagonal_matrix([21] * RANK)
    twenty_one_q = [[21 * value for value in row] for row in q]
    return {
        "description": (
            "G=21I, S=I, Q=B=diag(3^8,1^36), "
            "C=diag(1^8,0^36)"
        ),
        "C_integral_idempotent": (
            is_integral_matrix(c) and matmul(c, c) == c
        ),
        "traceC": int(trace(c)),
        "traceC2": int(trace(matmul(c, c))),
        "detB": 3**EQUALITY_IMAGE_RANK,
        "S_times_G_equals_21I": matmul(s, g) == twenty_one_i,
        "G_times_B_equals_21Q": matmul(g, b) == twenty_one_q,
        "S_times_Q_equals_B": matmul(s, q) == b,
        "G_even": is_even_integral_form(g),
        "S_even": is_even_integral_form(s),
        "Q_even": is_even_integral_form(q),
        "signature_obstruction_available_from_S": signature_obstructs_even_unimodular(
            EQUALITY_KERNEL_RANK,
            even=is_even_integral_form(s),
            integral=True,
            unimodular=True,
            positive_definite=True,
        ),
        "limitation": (
            "This is a hostile relaxation only: it violates the inherited "
            "evenness of L, S, and Q. It shows why the evenness derivation "
            "cannot be omitted."
        ),
    }


def nonintegral_idempotent_control() -> dict[str, object]:
    """A rational orthogonal projector whose real split is not a Z-split."""
    half = Fraction(1, 2)
    projector = [[half, half], [half, half]]
    c = block_diag([projector] * EQUALITY_IMAGE_RANK + [[[0]]] * 28)
    integral_split_basis = block_diag(
        [[[1, 1], [1, -1]]] * EQUALITY_IMAGE_RANK
        + [[[1]]] * 28
    )
    split_index = abs(determinant(integral_split_basis))
    return {
        "description": (
            "Eight copies of (1/2)[[1,1],[1,1]] plus 28 zero coordinates."
        ),
        "symmetric": is_symmetric(c),
        "idempotent": matmul(c, c) == c,
        "integral_endomorphism": is_integral_matrix(c),
        "traceC": fraction_text(Fraction(trace(c))),
        "traceC2": fraction_text(Fraction(trace(matmul(c, c)))),
        "image_rank": EQUALITY_IMAGE_RANK,
        "kernel_rank": EQUALITY_KERNEL_RANK,
        "index_of_integral_image_plus_kernel": int(split_index),
        "integral_direct_sum": split_index == 1,
        "limitation": (
            "Real orthogonal idempotence alone does not split Z^44; "
            "integrality of C is an active premise."
        ),
    }


def divisible_rank_control() -> dict[str, object]:
    """An explicit even unimodular rank-32 mutation using E8^4."""
    certificate = load_json(
        ROOT / "verification/wave24-n3-708-index/survivor-certificate.json"
    )
    e8 = certificate["matrices"]["E8"]
    witness = block_diag([e8] * 4)
    witness_det = determinant(witness)
    return {
        "mutated_ambient_rank": 40,
        "equality_image_rank": 8,
        "mutated_kernel_rank": 32,
        "mutated_kernel_rank_mod_8": 0,
        "signature_obstruction": signature_obstructs_even_unimodular(
            32,
            even=True,
            integral=True,
            unimodular=True,
            positive_definite=True,
        ),
        "E8_power": 4,
        "witness_rank": len(witness),
        "witness_even_integral": is_even_integral_form(witness),
        "witness_positive_definite": positive_definite_by_sylvester(witness),
        "witness_determinant": int(witness_det),
        "limitation": (
            "The contradiction is rank-sensitive: a 32-dimensional kernel "
            "is compatible with an even positive-definite unimodular form."
        ),
    }


def build_results() -> dict[str, object]:
    frozen_inputs = {
        path: {
            "expected_sha256": expected,
            "actual_sha256": sha256(ROOT / path),
            "matches": sha256(ROOT / path) == expected,
        }
        for path, expected in INPUTS.items()
    }
    if not all(row["matches"] for row in frozen_inputs.values()):
        raise AssertionError("frozen input hash mismatch")

    prior = load_json(
        ROOT / "verification/wave24-n3-708-index/independent-results.json"
    )
    if prior["claim_label"] != "VERIFIED":
        raise AssertionError("Wave 24 premise is not verified")
    if prior["status_boundary"]["target_existence"] != "UNKNOWN":
        raise AssertionError("unexpected target status mutation")

    equality = equality_split_certificate()
    trace_data = refined_trace_data()
    factor_summary = factor_pair_summary()
    determinant_data = determinant_refinement()
    survivor = frozen_survivor_control()
    controls = {
        "false_global_S_equals_Q_inverse": {
            "rejected": survivor["false_global_statement_rejected"],
            "correct_scope": survivor["correct_scope"],
        },
        "omitted_evenness": omitted_evenness_control(),
        "nonintegral_C_idempotent_split": nonintegral_idempotent_control(),
        "rank_divisible_by_8_mutation": divisible_rank_control(),
        "congruence_and_cap_omissions": congruence_and_cap_controls(),
    }

    return {
        "status": "DERIVED_EXACT_REPLAY_PENDING_INDEPENDENT_VERIFIER",
        "scope": (
            "Conditional strict trace and determinant refinement at n3=708 "
            "under the verified projector-lattice premises; no endpoint or "
            "target resolution."
        ),
        "frozen_inputs": frozen_inputs,
        "endpoint": {
            "n3": N3,
            "Delta": DELTA,
            "rank": RANK,
            "traceB": TRACE_B,
            "traceC": TRACE_C,
        },
        "equality_obstruction": equality,
        "trace_refinement": trace_data,
        "determinant_refinement": determinant_data,
        "factor_enumeration": factor_summary,
        "retained_wave24_abstract_survivor": survivor,
        "hostile_controls": controls,
        "conclusion": {
            "conditional_traceC2_floor": 10,
            "conditional_traceB2_floor": 116,
            "conditional_strict_determinant_bound": "det(B)<6561",
            "conditional_combined_detB_cap": 6525,
            "h_candidates": factor_summary["h_values"],
            "n3_708_excluded": False,
            "abstract_h9_detB81_survivor_retained": True,
            "graph_realization": "NOT_PROVED",
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
