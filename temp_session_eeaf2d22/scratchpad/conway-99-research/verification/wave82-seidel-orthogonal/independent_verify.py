#!/usr/bin/env python3
"""Clean-room verifier for the Wave 82 integral-orthogonal reduction.

This module deliberately does not import discovery-side Python.  It checks the
matrix equivalence, the p-primary Smith arithmetic, all surviving rank rows,
and several matrices/exponent profiles that satisfy only tempting subsets of
the required conditions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Sequence


N = 99
SCALAR = 3969
RANKS = (28, 30, 32, 34, 36, 38, 40, 42)
EXPECTED_DISCOVERY_MANIFEST = (
    "bc53c1a8f1425e4cbc4c2f78cee036b0e11f364d429cd9adabc55be6956dfaca"
)
EXPECTED_IMPORTS = {
    "verification/wave51-seidel-smith/independent-result.json":
        "1dda847b1180ac881f2ccce80285a2a50d9cab1f0f910f7dbdf9a6087d53d793",
    "verification/wave66-spherical-code-shift/independent-results.json":
        "3d6689b292fa5605e012da55f94e299926c1762c6ec77b8ef06007c62a65b61f",
}


class CheckError(AssertionError):
    """A claimed necessary condition failed."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_frozen_inputs(root: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    discovery_manifest = (
        root / "attempts/wave82-seidel-orthogonal/package-manifest.sha256"
    )
    found[str(discovery_manifest.relative_to(root)).replace("\\", "/")] = sha256(
        discovery_manifest
    )
    if sha256(discovery_manifest) != EXPECTED_DISCOVERY_MANIFEST:
        raise CheckError("Wave 82 discovery manifest changed after freeze")

    for relative, expected in EXPECTED_IMPORTS.items():
        actual = sha256(root / relative)
        found[relative] = actual
        if actual != expected:
            raise CheckError(f"verified import changed: {relative}")
    return found


def zeros(n: int) -> list[list[int]]:
    return [[0 for _ in range(n)] for _ in range(n)]


def multiply(left: Sequence[Sequence[int]],
             right: Sequence[Sequence[int]]) -> list[list[int]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    rows, inner, cols = len(left), len(right), len(right[0])
    out = zeros(rows)
    for i in range(rows):
        if len(left[i]) != inner:
            raise ValueError("ragged left matrix")
        for k, value in enumerate(left[i]):
            if value:
                if len(right[k]) != cols:
                    raise ValueError("ragged right matrix")
                for j, other in enumerate(right[k]):
                    out[i][j] += value * other
    return out


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    rank = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(rank, rows) if work[row][col]), None
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][col], -1, prime)
        work[rank] = [(inverse * value) % prime for value in work[rank]]
        for row in range(rows):
            if row != rank and work[row][col]:
                coefficient = work[row][col]
                work[row] = [
                    (a - coefficient * b) % prime
                    for a, b in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == rows:
            break
    return rank


def validate_adjacency(adjacency: Sequence[Sequence[int]]) -> None:
    if len(adjacency) != N or any(len(row) != N for row in adjacency):
        raise CheckError("adjacency must have order 99")
    for i, row in enumerate(adjacency):
        if row[i] != 0:
            raise CheckError("adjacency diagonal is not hollow")
        if sum(row) != 14:
            raise CheckError("adjacency is not 14-regular")
        for j, value in enumerate(row):
            if value not in (0, 1):
                raise CheckError("adjacency is not binary")
            if value != adjacency[j][i]:
                raise CheckError("adjacency is not symmetric")
    square = multiply(adjacency, adjacency)
    for i in range(N):
        for j in range(N):
            expected = 12 * (i == j) - adjacency[i][j] + 2
            if square[i][j] != expected:
                raise CheckError("adjacency fails A^2=12I-A+2J")


def t_from_adjacency(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            18 * adjacency[i][j] - 2 + 9 * (i == j)
            for j in range(N)
        ]
        for i in range(N)
    ]


def adjacency_from_t(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    if len(matrix) != N or any(len(row) != N for row in matrix):
        raise CheckError("T must have order 99")
    for i, row in enumerate(matrix):
        if row[i] != 7:
            raise CheckError("T diagonal must be 7")
        if sum(row) != 63:
            raise CheckError("T row sum must be 63")
        for j, value in enumerate(row):
            if value != matrix[j][i]:
                raise CheckError("T must be symmetric")
            if i != j and value not in (-2, 16):
                raise CheckError("T has an invalid off-diagonal entry")
    square = multiply(matrix, matrix)
    for i in range(N):
        for j in range(N):
            expected = SCALAR if i == j else 0
            if square[i][j] != expected:
                raise CheckError("T fails T^2=3969I")

    adjacency = [
        [
            (matrix[i][j] + 2 - 9 * (i == j)) // 18
            for j in range(N)
        ]
        for i in range(N)
    ]
    validate_adjacency(adjacency)
    return adjacency


def circulant_degree_fourteen() -> list[list[int]]:
    adjacency = zeros(N)
    offsets = set(range(1, 8)) | set(range(N - 7, N))
    for i in range(N):
        for offset in offsets:
            adjacency[i][(i + offset) % N] = 1
    return adjacency


def valuation(number: int, prime: int) -> int:
    if number == 0:
        raise ValueError("valuation of zero is not used here")
    exponent = 0
    while number % prime == 0:
        exponent += 1
        number //= prime
    return exponent


def validate_reciprocal_exponents(
    exponents: Sequence[int],
    scalar_valuation: int,
) -> None:
    if list(exponents) != sorted(exponents):
        raise CheckError("Smith exponents are not nondecreasing")
    if any(
        exponents[i] + exponents[-1 - i] != scalar_valuation
        for i in range(len(exponents))
    ):
        raise CheckError("Smith reciprocity fails")


def derive_three_primary_exponents() -> list[int]:
    # T = 7J (mod 9), so rank_F3(T)=1 and every 2-minor has v3 >= 2.
    # Thus e_1=0 and e_2>=2.  Reciprocity for T^2=3^4*7^2 I
    # gives e_i+e_(100-i)=4.  It gives e_98<=2, so monotonicity forces
    # all exponents e_2,...,e_98 to equal 2.
    exponents = [0] + [2] * 97 + [4]
    validate_reciprocal_exponents(exponents, 4)
    if sum(value == 0 for value in exponents) != 1:
        raise CheckError("wrong mod-3 rank")
    if exponents[0] + exponents[1] < 2:
        raise CheckError("2-minor valuation is too small")
    return exponents


def seven_primary_exponents(rank: int) -> list[int]:
    if not 0 <= rank <= N // 2:
        raise ValueError("invalid 7-rank")
    exponents = [0] * rank + [1] * (N - 2 * rank) + [2] * rank
    validate_reciprocal_exponents(exponents, 2)
    return exponents


def invariant_factors(rank: int) -> list[int]:
    threes = derive_three_primary_exponents()
    sevens = seven_primary_exponents(rank)
    return [3**a * 7**b for a, b in zip(threes, sevens)]


def validate_invariant_factors(rank: int) -> dict[str, object]:
    factors = invariant_factors(rank)
    if len(factors) != N:
        raise CheckError("wrong invariant-factor count")
    if any(right % left for left, right in zip(factors, factors[1:])):
        raise CheckError("global invariant factors do not divide successively")
    if math.prod(factors) != 63**N:
        raise CheckError("invariant-factor product is not det(T)")
    if any(factors[i] * factors[-1 - i] != SCALAR for i in range(N)):
        raise CheckError("global invariant-factor reciprocity fails")
    if sum(factor % 3 != 0 for factor in factors) != 1:
        raise CheckError("Smith form gives the wrong F3 rank")
    if sum(factor % 7 != 0 for factor in factors) != rank:
        raise CheckError("Smith form gives the wrong F7 rank")
    return {
        "rank_f7": rank,
        "factor_count": len(factors),
        "counts": {
            "1": factors.count(1),
            "9": factors.count(9),
            "63": factors.count(63),
            "441": factors.count(441),
            "3969": factors.count(3969),
        },
        "determinant": "63^99",
        "rank_f3": 1,
        "reciprocal_pair_product": SCALAR,
    }


def expect_rejected(callback, phrase: str) -> str:
    try:
        callback()
    except CheckError as error:
        if phrase not in str(error):
            raise CheckError(
                f"hostile control failed for an unexpected reason: {error}"
            ) from error
        return str(error)
    raise CheckError("hostile control was unexpectedly accepted")


def hostile_controls() -> dict[str, object]:
    cyclic = circulant_degree_fourteen()
    cyclic_t = t_from_adjacency(cyclic)
    # This graph gives exactly the required alphabet and row sums, and T is
    # still rank one mod 3, but it is not strongly regular.
    cyclic_failure = expect_rejected(
        lambda: adjacency_from_t(cyclic_t), "T^2=3969I"
    )
    if rank_mod_prime(cyclic_t, 3) != 1:
        raise CheckError("cyclic hostile control lost rank one mod 3")
    if any(
        cyclic_t[i][j] % 9 != 7
        for i in range(N)
        for j in range(N)
    ):
        raise CheckError("cyclic hostile control lost T=7J mod 9")

    scalar = zeros(N)
    for i in range(N):
        scalar[i][i] = 63
    scalar_failure = expect_rejected(
        lambda: adjacency_from_t(scalar), "diagonal must be 7"
    )

    all_nonedge = [[-2 for _ in range(N)] for _ in range(N)]
    for i in range(N):
        all_nonedge[i][i] = 7
    row_failure = expect_rejected(
        lambda: adjacency_from_t(all_nonedge), "row sum must be 63"
    )

    asymmetric = [row[:] for row in cyclic_t]
    asymmetric[0][1] = -2
    asymmetric[0][8] = 16
    asymmetric_failure = expect_rejected(
        lambda: adjacency_from_t(asymmetric), "symmetric"
    )

    split_three = [0] + [2] * 96 + [3, 3]
    if sum(split_three) != 198 or sum(x == 0 for x in split_three) != 1:
        raise CheckError("bad hostile 3-primary setup")
    split_failure = expect_rejected(
        lambda: validate_reciprocal_exponents(split_three, 4),
        "reciprocity",
    )

    threes = derive_three_primary_exponents()
    reversed_sevens = list(reversed(seven_primary_exponents(28)))
    misaligned = [3**a * 7**b for a, b in zip(threes, reversed_sevens)]
    if math.prod(misaligned) != 63**N:
        raise CheckError("misalignment control should retain determinant")
    alignment_rejected = any(
        right % left for left, right in zip(misaligned, misaligned[1:])
    )
    if not alignment_rejected:
        raise CheckError("misaligned primary factors unexpectedly form an SNF")

    return {
        "cyclic_14_regular_near_miss": {
            "required_entry_alphabet": True,
            "required_row_sum": True,
            "rank_f3": 1,
            "congruence_mod_9": "T=7J",
            "rejected_by": cyclic_failure,
        },
        "scalar_square_matrix_rejected_by": scalar_failure,
        "all_nonedge_matrix_rejected_by": row_failure,
        "asymmetric_matrix_rejected_by": asymmetric_failure,
        "same_determinant_rank_and_minor_floor_three_profile_rejected_by":
            split_failure,
        "misaligned_primary_parts": {
            "same_determinant": True,
            "rejected_by_divisibility_chain": alignment_rejected,
        },
    }


def equivalence_audit() -> dict[str, object]:
    # Forward square in the algebra generated by I,J,S:
    # (9S+7J)^2 = 81*49(I+J)+126*(-70J)+49*99J.
    j_coefficient = 81 * 49 - 126 * 70 + 49 * 99
    if j_coefficient != 0:
        raise CheckError("forward T-square J coefficient did not cancel")
    if 81 * 49 != SCALAR:
        raise CheckError("forward T-square I coefficient is wrong")
    if 9 * (-70) + 7 * 99 != 63:
        raise CheckError("forward row sum is wrong")

    # Converse expansion after row sums give AJ=JA=14J:
    # T^2 = 324A^2 + 324A + 81I - 648J.
    if (SCALAR - 81) // 324 != 12 or 648 // 324 != 2:
        raise CheckError("converse coefficient division failed")
    diagonal, edge, nonedge = (
        (7 + 2 - 9) // 18,
        (16 + 2) // 18,
        (-2 + 2) // 18,
    )
    if (diagonal, edge, nonedge) != (0, 1, 0):
        raise CheckError("entry recovery failed")
    recovered_degree = (63 + 2 * N - 9) // 18
    if recovered_degree != 14:
        raise CheckError("degree recovery failed")

    # Trace(T)=99*7=11*63; T is symmetric and T^2=63^2 I.
    plus = (N + 11) // 2
    minus = N - plus
    if (plus, minus) != (55, 44):
        raise CheckError("T multiplicities are wrong")
    return {
        "forward": {
            "definition": "T=9S+7J=18A-2J+9I",
            "entry_values": {"diagonal": 7, "edge": 16, "nonedge": -2},
            "row_sum": 63,
            "square": "3969I",
        },
        "converse": {
            "entry_map": "A=(T+2J-9I)/18",
            "binary_hollow_symmetric": True,
            "degree": recovered_degree,
            "direct_expansion":
                "T^2-3969I=324(A^2+A-12I-2J)",
            "srg_identity": "A^2=12I-A+2J",
        },
        "spectrum": {"+63": plus, "-63": minus},
        "determinant": "63^99",
    }


def seven_adic_audit() -> dict[str, object]:
    # T=S*U with U=9I-J/10.  The eigenvalues of U are 9 (multiplicity 98)
    # and -9/10 on 1.  Its determinant is -9^99/10, a 7-adic unit.
    determinant_numerator = -(9**N)
    determinant_denominator = 10
    if valuation(abs(determinant_numerator), 7) != 0:
        raise CheckError("U numerator is not a 7-adic unit")
    if valuation(determinant_denominator, 7) != 0:
        raise CheckError("U denominator is not a 7-adic unit")
    # Check the factorization coefficient using SJ=-70J:
    # S(9I-J/10)=9S+7J.
    j_coefficient_numerator = -(-70)
    if j_coefficient_numerator / 10 != 7:
        raise CheckError("7-adic transfer factorization failed")
    return {
        "factorization": "T=S(9I-J/10)",
        "factor_eigenvalues": {"one_perp": "9", "one_line": "-9/10"},
        "factor_determinant": "-9^99/10",
        "factor_is_in_GL_99_Z7": True,
        "conclusion": "T and S have identical 7-primary Smith exponents",
    }


def build_result(root: Path) -> dict[str, object]:
    frozen = check_frozen_inputs(root)
    profiles = [validate_invariant_factors(rank) for rank in RANKS]
    return {
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": "unrestricted hypothetical srg(99,14,1,2)",
        "frozen_inputs": frozen,
        "equivalence": equivalence_audit(),
        "three_primary": {
            "reciprocity": "e_i+e_(100-i)=4",
            "rank_f3": 1,
            "two_minor_floor": 2,
            "exponent_counts": {"0": 1, "2": 97, "4": 1},
        },
        "seven_primary": seven_adic_audit(),
        "smith_form": {
            "formula":
                "diag(1,9^(r-1),63^(99-2r),441^(r-1),3969)",
            "profiles": profiles,
        },
        "hostile_controls": hostile_controls(),
        "status": {
            "surviving_ranks": list(RANKS),
            "rank_rows_excluded": 0,
            "all_eight_survive": True,
            "matrix_constructed": False,
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The result is conditional on a hypothetical graph and the "
            "verified imported 7-primary Smith profile of S.",
            "A valid abstract Smith profile is necessary, not sufficient.",
            "No matrix or graph is constructed and no rank row is removed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--print", action="store_true", dest="print_result")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    result = build_result(root)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    if args.verify:
        if args.verify.read_text(encoding="utf-8") != rendered:
            raise CheckError(f"artifact differs: {args.verify}")
    if args.print_result or (not args.output and not args.verify):
        print(rendered, end="")
    print("PASS_WAVE82_INDEPENDENT_VERIFY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
