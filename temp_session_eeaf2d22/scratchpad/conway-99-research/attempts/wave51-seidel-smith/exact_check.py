#!/usr/bin/env python3
"""Exact arithmetic checks for the Wave 51 Seidel-Smith candidate."""

from __future__ import annotations

import argparse
import ctypes
import json
from math import comb
from pathlib import Path
from typing import Iterable

N = 99
PRIME = 7
ENDPOINT_MIN = 28
ENDPOINT_MAX = 44
DET_ABS = 10 * (PRIME**N)
RESULT_PATH = Path(__file__).with_name("exact-results.json")


def available_memory_fraction() -> float | None:
    """Return the Windows physical-memory availability fraction, if available."""

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
    available = available_memory_fraction()
    if available is not None and available < floor:
        raise RuntimeError(
            f"available physical memory {available:.3%} is below floor {floor:.1%}"
        )


def valuation(value: int, prime: int) -> int:
    if value <= 0:
        raise ValueError("valuation expects a positive integer")
    exponent = 0
    while value % prime == 0:
        value //= prime
        exponent += 1
    return exponent


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    """Exact Gaussian elimination over F_prime."""

    work = [[entry % prime for entry in row] for row in matrix]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    rank = 0
    for col in range(cols):
        pivot = next((i for i in range(rank, rows) if work[i][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][col], -1, prime)
        work[rank] = [(inverse * entry) % prime for entry in work[rank]]
        for i in range(rows):
            if i == rank or work[i][col] == 0:
                continue
            scale = work[i][col]
            work[i] = [
                (left - scale * right) % prime
                for left, right in zip(work[i], work[rank])
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def j_minus_i(n: int) -> list[list[int]]:
    return [[0 if i == j else 1 for j in range(n)] for i in range(n)]


def jordan_profile_mod_7(rank: int) -> dict[str, int]:
    if not 0 <= rank <= N // 2:
        raise ValueError("a square-zero 99 by 99 matrix has rank at most 49")
    return {"J2_zero_blocks": rank, "J1_zero_blocks": N - 2 * rank}


def smith_factors(rank: int) -> list[int]:
    """Conditional Smith factors for 1 <= rank_F7(S) <= 49."""

    if not 1 <= rank <= N // 2:
        raise ValueError("rank must lie from 1 through 49")
    return (
        [1] * rank
        + [7] * (N - 2 * rank)
        + [49] * (rank - 1)
        + [490]
    )


def modular_rank_from_smith(factors: Iterable[int], prime: int) -> int:
    return sum(value % prime != 0 for value in factors)


def validate_smith_profile(rank: int) -> dict[str, object]:
    factors = smith_factors(rank)
    divisibility = all(right % left == 0 for left, right in zip(factors, factors[1:]))
    product = 1
    for factor in factors:
        product *= factor
    seven_exponents = [valuation(factor, 7) for factor in factors]
    paired = all(
        seven_exponents[i] + seven_exponents[-1 - i] == 2
        for i in range(N)
    )
    result = {
        "rank": rank,
        "factor_count": len(factors),
        "divisibility_chain": divisibility,
        "determinant_matches": product == DET_ABS,
        "rank_mod_2": modular_rank_from_smith(factors, 2),
        "rank_mod_5": modular_rank_from_smith(factors, 5),
        "rank_mod_7": modular_rank_from_smith(factors, 7),
        "seven_valuation_counts": {
            str(exponent): seven_exponents.count(exponent) for exponent in range(3)
        },
        "seven_valuations_pair_to_two": paired,
    }
    result["all_checks_pass"] = (
        result["factor_count"] == N
        and result["divisibility_chain"]
        and result["determinant_matches"]
        and result["rank_mod_2"] == 98
        and result["rank_mod_5"] == 98
        and result["rank_mod_7"] == rank
        and result["seven_valuation_counts"]
        == {"0": rank, "1": N - 2 * rank, "2": rank}
        and result["seven_valuations_pair_to_two"]
    )
    return result


def symmetric_square_floor(required_rank: int = 98) -> int:
    rank = 0
    while comb(rank + 1, 2) < required_rank:
        rank += 1
    return rank


def build_results() -> dict[str, object]:
    enforce_memory_floor()
    all_profiles = [validate_smith_profile(rank) for rank in range(1, 50)]
    endpoint_profiles = [
        profile
        for profile in all_profiles
        if ENDPOINT_MIN <= profile["rank"] <= ENDPOINT_MAX
    ]
    gram_rank = rank_mod(j_minus_i(N), PRIME)
    square_floor = symmetric_square_floor(gram_rank)
    return {
        "claim_label": "CANDIDATE",
        "scope": "conditional consequences for a hypothetical srg(99,14,1,2)",
        "fixed_identities": {
            "seidel_definition": "S = 2A - J + I",
            "seidel_square": "S^2 = 49(I + J)",
            "seidel_spectrum": {"-70": 1, "-7": 54, "7": 44},
            "absolute_determinant": str(DET_ABS),
        },
        "modular_jordan_form": {
            "parameter": "r = rank_F7(S)",
            "formula": "J2(0)^r direct_sum J1(0)^(99-2r)",
            "reason": "S^2=0 over F7",
        },
        "smith_normal_form": {
            "formula": "diag(1^r, 7^(99-2r), 49^(r-1), 490)",
            "range_checked": [1, 49],
            "all_profiles_pass": all(
                profile["all_checks_pass"] for profile in all_profiles
            ),
            "profiles": all_profiles,
            "cokernel_formula": (
                "(Z/7)^(99-2r) direct_sum (Z/49)^(r-1) direct_sum Z/490"
            ),
        },
        "symmetric_square": {
            "pure_square_gram": "S mod 7 Hadamard-square = J-I",
            "gram_rank_mod_7": gram_rank,
            "ambient_dimension": "r(r+1)/2",
            "derived_floor": square_floor,
            "previous_rank_fails": comb(square_floor, 2) < gram_rank,
            "floor_rank_passes": comb(square_floor + 1, 2) >= gram_rank,
            "pure_square_span_rank": 98,
            "relation": "sum_i (v_i symmetric_tensor v_i) = 0",
        },
        "endpoint": {
            "imported_verified_interval": [ENDPOINT_MIN, ENDPOINT_MAX],
            "surviving_integer_ranks": [
                profile["rank"] for profile in endpoint_profiles
            ],
            "survivor_count": len(endpoint_profiles),
            "contradiction_found": False,
            "comparison": (
                "the derived symmetric-square floor r>=14 is weaker than "
                "the imported verified floor r>=28"
            ),
        },
        "limitations": [
            "No graph or Seidel matrix was constructed.",
            "Smith-profile compatibility is not matrix or graph realizability.",
            "No endpoint rank in 28..44 is excluded.",
            "This discovery package is not independent verification.",
        ],
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="compare recomputed canonical bytes with --output",
    )
    args = parser.parse_args()
    payload = build_results()
    encoded = canonical_bytes(payload)
    if args.verify:
        if not args.output.exists():
            raise SystemExit(f"missing artifact: {args.output}")
        if args.output.read_bytes() != encoded:
            raise SystemExit("artifact differs from exact recomputation")
        print(f"verified {args.output}")
        return 0
    args.output.write_bytes(encoded)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

