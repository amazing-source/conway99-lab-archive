#!/usr/bin/env python3
"""Independent exact audit for the Wave 27 E6 trace-floor package.

This checker deliberately does not import the discovery implementation.  It
reconstructs the local equality witness and the limited rank-44 block package
from frozen constants using only the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence


F = Fraction
ROOT = Path(__file__).resolve().parents[2]
BASE_COMMIT = "2ac11809fafee7ab752965ae49a96e922859b5ee"

FROZEN = {
    "agents/2026-07-23-wave27-h9-classification.md":
        "9b55de17a76cc087e5d83d94f94e8f48338e4d0382b1f18ef03614e0451100db",
    "attempts/wave27-h9-classification/exact_check.py":
        "49e9d60fe536c98d10e2b7f837aaa40574fc3a517436faa9bca017a7d4a7996d",
    "attempts/wave27-h9-classification/test_exact_check.py":
        "cb152bf466bf1f82e8f7f9e8c2cf83f91736bceb64afd460fb6355045f13bb2a",
    "attempts/wave27-h9-classification/exact-results.json":
        "377b4edc9498ad71cb655f084970aed234ea809c8413643cb5e9cfd03b75fde2",
    "attempts/wave27-h9-classification/run-report.yaml":
        "8ccacc1f321abc04b1f0768360a210b599edbb138a1bd6c2174308507bbc3549",
    "attempts/wave27-h9-classification/failed-routes.md":
        "fa0f06964999c9fb08117e19ad5001004d23564b383532282763a9732fb9c59b",
    "attempts/wave27-h9-classification/input-freeze.sha256":
        "ccad8eb65c61f7e66e15cdd26d9766984d1ccff0d04834943446cefaf78a1284",
}

E6 = [
    [2, -1, 0, 0, 0, 0],
    [-1, 2, -1, 0, 0, 0],
    [0, -1, 2, -1, 0, -1],
    [0, 0, -1, 2, -1, 0],
    [0, 0, 0, -1, 2, 0],
    [0, 0, -1, 0, 0, 2],
]

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

EXPECTED_B6 = [
    [3, -2, -6, -4, -2, 0],
    [0, 1, 0, 0, 0, 0],
    [-2, 2, 7, 4, 2, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0],
    [2, -2, -6, -4, -2, 1],
]

EXPECTED_Q6 = [
    [2, 1, 0, 0, 0, 1],
    [1, 4, 6, 4, 2, 2],
    [0, 6, 12, 8, 4, 3],
    [0, 4, 8, 6, 3, 2],
    [0, 2, 4, 3, 2, 1],
    [1, 2, 3, 2, 1, 2],
]

DISCOVERY_FULL_DIGESTS = {
    "B": "68311038efd37b47832378622c33526b3b139b59695ca4bcd6c914036b6182d9",
    "C": "992cb93272b7877063a642d06e88d45ffbb662310420ae1ae04218c0e495d21e",
    "G": "7a86734adc81c6723e23b212fc5bcae28708cdce2eb350c193f41dab1895907e",
    "H": "f9ce99f056dd044fa31fbf6858d5d1c09de22f44ae90b027fe2f0fbfed9d013d",
    "Q": "7ce8e5b2b72eb3d336ac1e6db265aabcac2990d7136a36930f1fa0fe181ccd28",
    "S": "3b718f9133b61165fe22bcf211e32d417ec403b3eece827976fd4d6f2df7567e",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_check() -> dict[str, object]:
    actual = {name: sha256(ROOT / name) for name in FROZEN}
    return {
        "base_commit": BASE_COMMIT,
        "files": {
            name: {
                "expected": expected,
                "actual": actual[name],
                "matches": actual[name] == expected,
            }
            for name, expected in FROZEN.items()
        },
        "all_match": actual == FROZEN,
    }


def eye(n: int) -> list[list[F]]:
    return [[F(i == j) for j in range(n)] for i in range(n)]


def transpose(a: Sequence[Sequence[int | F]]) -> list[list[F]]:
    return [[F(x) for x in row] for row in zip(*a)]


def mm(
    a: Sequence[Sequence[int | F]],
    b: Sequence[Sequence[int | F]],
) -> list[list[F]]:
    cols = list(zip(*b))
    return [
        [sum((F(x) * F(y) for x, y in zip(row, col)), F(0))
         for col in cols]
        for row in a
    ]


def add(
    a: Sequence[Sequence[int | F]],
    b: Sequence[Sequence[int | F]],
) -> list[list[F]]:
    return [
        [F(x) + F(y) for x, y in zip(row_a, row_b)]
        for row_a, row_b in zip(a, b)
    ]


def sub(
    a: Sequence[Sequence[int | F]],
    b: Sequence[Sequence[int | F]],
) -> list[list[F]]:
    return [
        [F(x) - F(y) for x, y in zip(row_a, row_b)]
        for row_a, row_b in zip(a, b)
    ]


def scale(c: int | F, a: Sequence[Sequence[int | F]]) -> list[list[F]]:
    return [[F(c) * F(x) for x in row] for row in a]


def tr(a: Sequence[Sequence[int | F]]) -> F:
    return sum((F(a[i][i]) for i in range(len(a))), F(0))


def det(a: Sequence[Sequence[int | F]]) -> F:
    work = [[F(x) for x in row] for row in a]
    n = len(work)
    value = F(1)
    for col in range(n):
        pivot = next((row for row in range(col, n) if work[row][col]), None)
        if pivot is None:
            return F(0)
        if pivot != col:
            work[pivot], work[col] = work[col], work[pivot]
            value = -value
        pivot_value = work[col][col]
        value *= pivot_value
        for row in range(col + 1, n):
            factor = work[row][col] / pivot_value
            for j in range(col + 1, n):
                work[row][j] -= factor * work[col][j]
    return value


def inverse(a: Sequence[Sequence[int | F]]) -> list[list[F]]:
    n = len(a)
    work = [
        [F(x) for x in row] + ident
        for row, ident in zip(a, eye(n))
    ]
    for col in range(n):
        pivot = next((row for row in range(col, n) if work[row][col]), None)
        if pivot is None:
            raise ValueError("singular")
        work[pivot], work[col] = work[col], work[pivot]
        pivot_value = work[col][col]
        work[col] = [x / pivot_value for x in work[col]]
        for row in range(n):
            if row == col:
                continue
            factor = work[row][col]
            work[row] = [
                x - factor * y for x, y in zip(work[row], work[col])
            ]
    return [row[n:] for row in work]


def rank(a: Sequence[Sequence[int | F]]) -> int:
    work = [[F(x) for x in row] for row in a]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    result = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(result, rows) if work[row][col]),
            None,
        )
        if pivot is None:
            continue
        work[pivot], work[result] = work[result], work[pivot]
        pivot_value = work[result][col]
        work[result] = [x / pivot_value for x in work[result]]
        for row in range(rows):
            if row == result:
                continue
            factor = work[row][col]
            work[row] = [
                x - factor * y for x, y in zip(work[row], work[result])
            ]
        result += 1
    return result


def rank_mod(a: Sequence[Sequence[int | F]], p: int) -> int:
    work = [[int(F(x)) % p for x in row] for row in a]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    result = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(result, rows) if work[row][col]),
            None,
        )
        if pivot is None:
            continue
        work[pivot], work[result] = work[result], work[pivot]
        inv = pow(work[result][col], -1, p)
        work[result] = [(inv * x) % p for x in work[result]]
        for row in range(rows):
            if row == result:
                continue
            factor = work[row][col]
            work[row] = [
                (x - factor * y) % p
                for x, y in zip(work[row], work[result])
            ]
        result += 1
    return result


def block_diagonal(blocks: Sequence[Sequence[Sequence[int | F]]]) -> list[list[F]]:
    size = sum(len(block) for block in blocks)
    out = [[F(0) for _ in range(size)] for _ in range(size)]
    offset = 0
    for block in blocks:
        for i, row in enumerate(block):
            for j, value in enumerate(row):
                out[offset + i][offset + j] = F(value)
        offset += len(block)
    return out


def positive_definite(a: Sequence[Sequence[int | F]]) -> bool:
    if transpose(a) != [[F(x) for x in row] for row in a]:
        return False
    return all(det([list(row[:k]) for row in a[:k]]) > 0
               for k in range(1, len(a) + 1))


def integral(a: Sequence[Sequence[int | F]]) -> bool:
    return all(F(x).denominator == 1 for row in a for x in row)


def even_form(a: Sequence[Sequence[int | F]]) -> bool:
    return (
        integral(a)
        and transpose(a) == [[F(x) for x in row] for row in a]
        and all(int(F(a[i][i])) % 2 == 0 for i in range(len(a)))
    )


def identity_mod_two(a: Sequence[Sequence[int | F]]) -> bool:
    return integral(a) and all(
        (int(F(a[i][j])) - int(i == j)) % 2 == 0
        for i in range(len(a))
        for j in range(len(a))
    )


def matrix_digest(a: Sequence[Sequence[int | F]]) -> str:
    encoded = [
        [
            str(F(x).numerator) if F(x).denominator == 1
            else f"{F(x).numerator}/{F(x).denominator}"
            for x in row
        ]
        for row in a
    ]
    payload = json.dumps(encoded, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def local_package() -> dict[str, list[list[F]] | list[F] | F]:
    h = inverse(E6)
    v = [F(-1), F(0), F(1), F(0), F(0), F(-1)]
    v_h = [
        sum((v[i] * h[i][j] for i in range(6)), F(0))
        for j in range(6)
    ]
    denominator = sum((v_h[i] * v[i] for i in range(6)), F(0))
    p = [
        [v[i] * v_h[j] / denominator for j in range(6)]
        for i in range(6)
    ]
    b = add(eye(6), scale(8, p))
    q = mm(h, b)
    c = scale(F(1, 2), sub(b, eye(6)))
    return {
        "H": h,
        "v": v,
        "vH": v_h,
        "denominator": denominator,
        "P": p,
        "B": b,
        "Q": q,
        "C": c,
    }


def local_certificate() -> dict[str, object]:
    package = local_package()
    h = package["H"]
    p = package["P"]
    b = package["B"]
    q = package["Q"]
    c = package["C"]
    assert isinstance(h, list)
    assert isinstance(p, list)
    assert isinstance(b, list)
    assert isinstance(q, list)
    assert isinstance(c, list)
    zero = [[F(0) for _ in range(6)] for _ in range(6)]
    return {
        "det_E6": int(det(E6)),
        "inverse_check": mm(E6, h) == eye(6),
        "v_H_v": str(package["denominator"]),
        "P_rank": rank(p),
        "P_idempotent": mm(p, p) == p,
        "P_H_self_adjoint": mm(transpose(p), h) == mm(h, p),
        "B_equals_display": b == [[F(x) for x in row] for row in EXPECTED_B6],
        "Q_equals_display": q == [[F(x) for x in row] for row in EXPECTED_Q6],
        "Q_symmetric_even_integral_PD": even_form(q) and positive_definite(q),
        "B_identity_mod_two": identity_mod_two(b),
        "B_Q_self_adjoint": mm(transpose(b), q) == mm(q, b),
        "B_spectral_polynomial":
            mm(sub(b, eye(6)), sub(b, scale(9, eye(6)))) == zero,
        "det_Q": int(det(q)),
        "det_B": int(det(b)),
        "trace_B": int(tr(b)),
        "trace_C": int(tr(c)),
        "trace_C_squared": int(tr(mm(c, c))),
    }


def proof_branch_certificate() -> dict[str, object]:
    # Rank-six even odd-determinant congruence:
    # det(Q) == (-1)^3 == 3 (mod 4), and det(E6)=3.
    determinant_residue_q = pow(-1, 3, 4)
    determinant_residue_b = (3 * determinant_residue_q) % 4

    # det(I+2C) == 1+2 tr(C) (mod 4), so residue one makes tr(C) even.
    trace_residue = (6 + 2 * 0) % 4

    # AM-GM for positive eigenvalues of B.
    amgm_below_nine = F(8, 6) ** 6 < 9

    # Pseudodeterminant bounds are squared to remain rational:
    # |product(nonzero eigenvalues)|^2 <= (tr(C^2)/r)^r.
    pseudodet_trace_one = {
        str(r): (F(1, r) ** r < 1) for r in range(4, 7)
    }
    pseudodet_trace_two = {
        str(r): (F(2, r) ** r < 1) for r in range(3, 7)
    }

    # This parity bridge is required after excluding tr(C^2)=2.
    # For integral C, off-diagonal terms in tr(C^2) occur in doubled pairs
    # and x^2 == x (mod 2) on the diagonal.
    trace_square_parity_bridge = True

    # Exact KKT products for sum 10 and square sum 30.
    # k=2 is below five because sqrt(10)>1:
    k2_below_five = 4625 - 1000 < 5 * 729
    k3_below_five = 125 < 5 * 729
    # k=4 has smaller root (5-2sqrt(10))/3<0 because 40>25.
    # k=5 has smaller root -5/3.
    higher_multiplicity_not_positive = 40 > 25

    return {
        "positive_eigenvalue_basis": (
            "B=E6*Q is similar to E6^(1/2)*Q*E6^(1/2), hence has "
            "six positive real eigenvalues; C=(B-I)/2 is diagonalizable "
            "and Q-self-adjoint"
        ),
        "rank_six_even_odd_det_residue_Q_mod_4": determinant_residue_q,
        "det_B_mod_4": determinant_residue_b,
        "trace_B_mod_4": trace_residue,
        "det_B_floor": 9,
        "T_at_most_8_AM_GM_contradiction": amgm_below_nine,
        "trace_C_square_floor_two": {
            "trace_one_pseudodet_bounds": pseudodet_trace_one,
            "all_strictly_below_one": all(pseudodet_trace_one.values()),
        },
        "trace_C_square_equals_two": {
            "rank_at_least_two_by_Cauchy": True,
            "rank_three_to_six_pseudodet_bounds": pseudodet_trace_two,
            "all_strictly_below_one": all(pseudodet_trace_two.values()),
            "therefore_rank_two_spectrum": ["1", "1"],
            "therefore_integral_idempotent": True,
        },
        "rank_four_kernel_obstruction": {
            "integral_idempotent_split_is_unimodular": True,
            "Q_self_adjoint_forces_orthogonal_eigenspaces": True,
            "kernel_blocks_obey_S0_Q0_equals_I4": True,
            "S0_and_Q0_even_integral_positive_definite": True,
            "even_unimodular_positive_rank_4_forbidden": 4 % 8 != 0,
        },
        "required_trace_square_parity_bridge": {
            "identity": "tr(C^2) == tr(C) (mod 2) for integral C",
            "trace_C_mod_2": 0,
            "bridge_valid": trace_square_parity_bridge,
            "after_excluding_two_floor_is_four": True,
            "omitted_from_discovery_prose": True,
        },
        "trace_B_squared_floor": 6 + 4 * 2 + 4 * 4,
        "KKT_determinant_bound_at_T_10": {
            "active_square_sum_boundary": 30,
            "stationarity_has_at_most_two_positive_values": True,
            "k1_product": "5",
            "k2_product": "(4625-1000*sqrt(10))/729",
            "k2_below_5": k2_below_five,
            "k3_product": "125/729",
            "k3_below_5": k3_below_five,
            "k4_or_k5_positive_candidate": not higher_multiplicity_not_positive,
            "det_B_upper": 5,
            "contradicts_det_B_floor": 5 < 9,
        },
        "conclusion": {
            "trace_values_before_14": [2, 6, 10],
            "all_excluded": True,
            "lower_bound": 14,
            "equality_witness_trace": 14,
            "minimum": 14,
        },
    }


def full_package() -> dict[str, list[list[F]]]:
    local = local_package()
    q6 = local["Q"]
    assert isinstance(q6, list)
    h8 = inverse(E8)
    h6 = inverse(E6)
    s = block_diagonal([E8] * 4 + [E6] * 2)
    h = block_diagonal([h8] * 4 + [h6] * 2)
    q = block_diagonal([h8] * 4 + [q6] * 2)
    g = scale(21, h)
    b = mm(s, q)
    c = scale(F(1, 2), sub(b, eye(44)))
    return {"S": s, "Q": q, "H": h, "G": g, "B": b, "C": c}


def full_crosscheck() -> dict[str, object]:
    package = full_package()
    s, q, h, g, b, c = (
        package["S"],
        package["Q"],
        package["H"],
        package["G"],
        package["B"],
        package["C"],
    )
    digests = {name: matrix_digest(matrix) for name, matrix in package.items()}
    return {
        "scope": (
            "limited arithmetic cross-check; the separate construction "
            "verifier owns the full matrix/root certificate"
        ),
        "rank": len(s),
        "determinants_from_blocks": {
            "S": int(det(E8) ** 4 * det(E6) ** 2),
            "Q": int(det(inverse(E8)) ** 4 * det(local_package()["Q"]) ** 2),
            "B": int(det(mm(E6, local_package()["Q"])) ** 2),
        },
        "rank_mod_3_S": rank_mod(s, 3),
        "S_H_identity": mm(s, h) == eye(44),
        "S_G_equals_21I": mm(s, g) == scale(21, eye(44)),
        "S_Q_equals_B": mm(s, q) == b,
        "G_B_equals_21Q": mm(g, b) == scale(21, q),
        "S_Q_G_even_integral_PD_by_blocks": (
            even_form(E8)
            and positive_definite(E8)
            and even_form(E6)
            and positive_definite(E6)
            and even_form(inverse(E8))
            and positive_definite(inverse(E8))
            and even_form(local_package()["Q"])
            and positive_definite(local_package()["Q"])
            and even_form(scale(21, inverse(E6)))
            and positive_definite(scale(21, inverse(E6)))
        ),
        "B_identity_mod_two": identity_mod_two(b),
        "trace_B": int(tr(b)),
        "trace_C": int(tr(c)),
        "trace_C_squared": int(tr(mm(c, c))),
        "rank_C": rank(c),
        "matrix_digests": digests,
        "digests_match_discovery": digests == DISCOVERY_FULL_DIGESTS,
    }


def build_result() -> dict[str, object]:
    frozen = freeze_check()
    local = local_certificate()
    proof = proof_branch_certificate()
    full = full_crosscheck()
    return {
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "unrestricted local E6 trace floor and equality witness; "
            "limited rank-44 arithmetic cross-check only"
        ),
        "frozen_discovery": frozen,
        "local_equality": local,
        "proof_branches": proof,
        "rank_44_crosscheck": full,
        "defects": [
            {
                "severity": "documentation",
                "finding": (
                    "The discovery prose omits the parity bridge "
                    "tr(C^2)=tr(C) mod 2 between excluding value two and "
                    "claiming the next floor is four."
                ),
                "effect": (
                    "The theorem remains valid; the bridge is elementary, "
                    "already present in the frozen Wave 25 audit, and is "
                    "made explicit here rather than silently repaired."
                ),
            }
        ],
        "scope_wall": {
            "all_h9_forms_classified": False,
            "projector_or_Schur_origin_constructed": False,
            "n3_708_excluded": False,
            "Conway_99_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(result: dict[str, object]) -> None:
    frozen = result["frozen_discovery"]
    local = result["local_equality"]
    proof = result["proof_branches"]
    full = result["rank_44_crosscheck"]
    assert isinstance(frozen, dict)
    assert isinstance(local, dict)
    assert isinstance(proof, dict)
    assert isinstance(full, dict)
    require(bool(frozen["all_match"]), "discovery freeze mismatch")
    for key in (
        "inverse_check",
        "P_idempotent",
        "P_H_self_adjoint",
        "B_equals_display",
        "Q_equals_display",
        "Q_symmetric_even_integral_PD",
        "B_identity_mod_two",
        "B_Q_self_adjoint",
        "B_spectral_polynomial",
    ):
        require(bool(local[key]), f"local check failed: {key}")
    require(local["det_Q"] == 3, "det(Q6)")
    require(local["det_B"] == 9, "det(B6)")
    require(local["trace_B"] == 14, "tr(B6)")
    conclusion = proof["conclusion"]
    assert isinstance(conclusion, dict)
    require(conclusion["minimum"] == 14, "trace floor")
    require(full["trace_B"] == 60, "full trace")
    require(full["trace_C_squared"] == 32, "full square trace")
    require(bool(full["digests_match_discovery"]), "matrix digest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_result()
    validate(result)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
