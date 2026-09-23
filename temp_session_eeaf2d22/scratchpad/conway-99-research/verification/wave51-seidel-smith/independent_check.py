#!/usr/bin/env python3
"""Independent exact reconstruction for the Wave 51 Seidel/Smith claims."""

from __future__ import annotations

import argparse
import ctypes
import json
from math import comb
from pathlib import Path

N = 99
P = 7
RESULT_PATH = Path(__file__).with_name("independent-result.json")


def available_memory_fraction() -> float | None:
    if not hasattr(ctypes, "windll"):
        return None

    class MemoryStatusEx(ctypes.Structure):
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

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(MemoryStatusEx)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None
    return status.ullAvailPhys / status.ullTotalPhys


def enforce_memory_floor(floor: float = 0.15) -> None:
    fraction = available_memory_fraction()
    if fraction is not None and fraction < floor:
        raise RuntimeError(
            f"available physical memory {fraction:.3%} is below {floor:.1%}"
        )


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    rank = 0
    for column in range(cols):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [(inverse * value) % prime for value in work[rank]]
        for row in range(rows):
            if row == rank or work[row][column] == 0:
                continue
            scale = work[row][column]
            work[row] = [
                (left - scale * right) % prime
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
    return rank


def identity_plus_j(size: int) -> list[list[int]]:
    return [[1 + (row == column) for column in range(size)] for row in range(size)]


def j_minus_identity(size: int) -> list[list[int]]:
    return [[int(row != column) for column in range(size)] for row in range(size)]


def seidel_square_coefficients() -> dict[str, int]:
    """Expand (2A-J+I)^2 using the frozen SRG relations."""

    return {
        "I": 4 * 12 + 1,
        "A": 4 * (-1) + 4,
        "J": 4 * 2 + 99 - 2 * 14 - 2 * 14 - 2,
    }


def rational_spectra() -> dict[str, object]:
    """Derive multiplicities from dimensions and trace, not discovery data."""

    # On 1-perp, A obeys x^2+x-12=(x-3)(x+4).
    dimension = 98
    multiplicity_a3 = (4 * dimension - 14) // 7
    multiplicity_a_minus4 = dimension - multiplicity_a3
    adjacency = {14: 1, 3: multiplicity_a3, -4: multiplicity_a_minus4}
    seidel = {
        -70: 1,
        7: multiplicity_a3,
        -7: multiplicity_a_minus4,
    }
    trace = sum(value * multiplicity for value, multiplicity in seidel.items())
    determinant_abs = 1
    for value, multiplicity in seidel.items():
        determinant_abs *= abs(value) ** multiplicity
    return {
        "adjacency": {str(key): value for key, value in adjacency.items()},
        "seidel": {str(key): value for key, value in seidel.items()},
        "seidel_trace": trace,
        "absolute_determinant": str(determinant_abs),
    }


def seven_exponent_candidates(rank: int) -> list[list[int]]:
    """Enumerate sorted 7-exponent profiles obeying the reciprocal pairing."""

    if not 1 <= rank <= 49:
        raise ValueError("rank must lie in 1..49")
    candidates: list[list[int]] = []
    for count_one in range(N - rank + 1):
        count_two = N - rank - count_one
        exponents = [0] * rank + [1] * count_one + [2] * count_two
        if all(
            exponents[index] + exponents[-1 - index] == 2
            for index in range(N)
        ):
            candidates.append(exponents)
    return candidates


def seven_exponents(rank: int) -> list[int]:
    candidates = seven_exponent_candidates(rank)
    if len(candidates) != 1:
        raise AssertionError(f"expected unique 7-profile, got {len(candidates)}")
    return candidates[0]


def assemble_invariant_factors(rank: int) -> list[int]:
    """Align sorted local exponents, as required for invariant factors."""

    seven = seven_exponents(rank)
    two = [0] * 98 + [1]
    five = [0] * 98 + [1]
    return [
        (2**a2) * (5**a5) * (7**a7)
        for a2, a5, a7 in zip(two, five, seven)
    ]


def valuation(value: int, prime: int) -> int:
    exponent = 0
    while value % prime == 0:
        exponent += 1
        value //= prime
    return exponent


def modular_rank(factors: list[int], prime: int) -> int:
    return sum(factor % prime != 0 for factor in factors)


def profile(rank: int) -> dict[str, object]:
    factors = assemble_invariant_factors(rank)
    product = 1
    for factor in factors:
        product *= factor
    expected = [1] * rank
    expected += [7] * (99 - 2 * rank)
    expected += [49] * (rank - 1)
    expected += [490]
    return {
        "rank_f7": rank,
        "factor_count": len(factors),
        "matches_closed_form": factors == expected,
        "divisibility_chain": all(
            right % left == 0 for left, right in zip(factors, factors[1:])
        ),
        "absolute_product": str(product),
        "rank_mod_2": modular_rank(factors, 2),
        "rank_mod_5": modular_rank(factors, 5),
        "rank_mod_7": modular_rank(factors, 7),
        "seven_counts": {
            str(exponent): sum(
                valuation(factor, 7) == exponent for factor in factors
            )
            for exponent in range(3)
        },
    }


def rank_and_determinant_only_counterexample(rank: int = 28) -> dict[str, object]:
    """Exhibit why modular ranks plus determinant do not force the 7-profile."""

    canonical = [0] * rank + [1] * (N - 2 * rank) + [2] * rank
    # Replace two exponent-2 terms by one exponent-1 and one exponent-3.
    alternative = (
        [0] * rank
        + [1] * (N - 2 * rank + 1)
        + [2] * (rank - 2)
        + [3]
    )
    return {
        "rank": rank,
        "canonical_counts": {
            str(e): canonical.count(e) for e in sorted(set(canonical))
        },
        "alternative_counts": {
            str(e): alternative.count(e) for e in sorted(set(alternative))
        },
        "same_factor_count": len(canonical) == len(alternative) == N,
        "same_rank_mod_7": canonical.count(0) == alternative.count(0) == rank,
        "same_determinant_valuation": sum(canonical) == sum(alternative) == N,
        "alternative_violates_reciprocal_pairing": not all(
            alternative[index] + alternative[-1 - index] == 2
            for index in range(N)
        ),
    }


def jordan_profile(rank: int) -> dict[str, int]:
    if not 0 <= rank <= 49:
        raise ValueError("square-zero rank must lie in 0..49")
    return {"J2_zero": rank, "J1_zero": N - 2 * rank}


def symmetric_square_floor(required: int) -> int:
    rank = 0
    while comb(rank + 1, 2) < required:
        rank += 1
    return rank


def build_result() -> dict[str, object]:
    enforce_memory_floor()
    spectra = rational_spectra()
    profiles = [profile(rank) for rank in range(1, 50)]
    endpoint = profiles[27:44]
    gram_rank = rank_mod(j_minus_identity(N), P)
    unit_mod_7 = 100 % 7 != 0
    return {
        "claim_label": "VERIFIED",
        "scope": (
            "corrected conditional Seidel identity, Smith form, Jordan type, "
            "and symmetric-square consequence"
        ),
        "seidel_identity": {
            "square_coefficients": seidel_square_coefficients(),
            "formula": "S^2 = 49(I+J)",
        },
        "rational_spectra": spectra,
        "discovery_correction": {
            "claim_label": "REFUTED",
            "discovery_claim": "-70^1, +7^44, -7^54",
            "correct_spectrum": "-70^1, +7^54, -7^44",
            "reason": "the discovery multiplicities give trace -140, not trace(S)=0",
            "downstream_effect": (
                "none on the absolute determinant, local Smith calculation, "
                "Jordan type, or symmetric-square bound"
            ),
        },
        "smith_logic": {
            "det_I_plus_J": 100,
            "I_plus_J_is_unit_over_Z7": unit_mod_7,
            "reciprocal_equation": "49 S^-1 = (I+J)^-1 S over Z_7",
            "paired_exponents": "a_i + a_(100-i) = 2",
            "unique_profiles_for_r_1_through_49": all(
                len(seven_exponent_candidates(rank)) == 1
                for rank in range(1, 50)
            ),
            "profiles": profiles,
            "closed_form": "diag(1^r,7^(99-2r),49^(r-1),490)",
            "rank_information_alone_warning": rank_and_determinant_only_counterexample(),
        },
        "mod_7_jordan": {
            "formula": "J2(0)^r direct_sum J1(0)^(99-2r)",
            "profiles": [jordan_profile(rank) for rank in range(50)],
        },
        "symmetric_square": {
            "pure_square_gram": "J-I",
            "gram_rank_mod_7": gram_rank,
            "ambient_dimension": "r(r+1)/2",
            "derived_floor": symmetric_square_floor(gram_rank),
            "rank_13_dimension": comb(14, 2),
            "rank_14_dimension": comb(15, 2),
        },
        "endpoint": {
            "claim_label": "UNKNOWN",
            "imported_interval": [28, 44],
            "surviving_ranks": [entry["rank_f7"] for entry in endpoint],
            "survivor_count": len(endpoint),
            "contradiction_found": False,
        },
        "limitations": [
            "The argument is conditional on a hypothetical SRG and constructs no matrix.",
            "The Smith profiles are necessary, not sufficient, for realizability.",
            "Ranks modulo 2, 5, and 7 do not alone determine the Smith form.",
            "The reciprocal 7-adic identity and determinant are essential inputs.",
            "No rank in the imported endpoint interval 28..44 is excluded.",
        ],
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    parser.add_argument("--verify", action="store_true")
    arguments = parser.parse_args()
    encoded = canonical_bytes(build_result())
    if arguments.verify:
        if arguments.output.read_bytes() != encoded:
            raise SystemExit("independent artifact differs from exact reconstruction")
        print(f"verified {arguments.output}")
        return 0
    arguments.output.write_bytes(encoded)
    print(f"wrote {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

