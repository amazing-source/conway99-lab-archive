#!/usr/bin/env python3
"""Independent exact verifier for the Wave54 formal ordinary enumerator.

This implementation intentionally computes q-ary Krawtchouk coefficients from
their defining binomial sum.  It does not import any discovery code.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Iterable


Q = 3
N = 231
K = 11
CODE_SIZE = Q**K
DUAL_SIZE = Q ** (N - K)
MIN_FREE_MEMORY_PERCENT = 15.0
CANDIDATE_SPARSE = {
    0: 1,
    18: 2,
    144: 53_316,
    153: 19_798,
    159: 98_496,
    162: 5_072,
    198: 462,
}
DUAL_LOWER_BOUNDS = {7: 198, 12: 1_386, 13: 1_386, 14: 16_632}

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM_PATHS = (
    "AGENTS.md",
    "verification/2026-07-27-wave39-integration-audit.md",
    "verification/2026-07-27-wave39-orchestrator.md",
    "verification/wave39-edge-local-rank/independent-results.json",
    "verification/wave39-proof-solver/exact-results.json",
    "verification/wave39-edge-local-rank/package-manifest.sha256",
    "verification/wave39-proof-solver/package-manifest.sha256",
    "attempts/wave39-simultaneous-bh/exact-results.json",
    "attempts/wave39-simultaneous-bh/README.md",
    "attempts/wave39-simultaneous-bh/run-report.yaml",
    "attempts/wave39-simultaneous-bh/input-freeze.sha256",
    "attempts/wave39-simultaneous-bh/package-manifest.sha256",
)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def free_memory_percent() -> float:
    """Return currently available physical memory as a percentage."""

    if os.name == "nt":
        class MemoryStatus(ctypes.Structure):
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

        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return 100.0 * status.ullAvailPhys / status.ullTotalPhys

    page_size = os.sysconf("SC_PAGE_SIZE")
    available = os.sysconf("SC_AVPHYS_PAGES") * page_size
    total = os.sysconf("SC_PHYS_PAGES") * page_size
    return 100.0 * available / total


def enforce_memory_floor() -> float:
    percent = free_memory_percent()
    if percent < MIN_FREE_MEMORY_PERCENT:
        raise MemoryError(
            f"free physical memory {percent:.2f}% is below "
            f"{MIN_FREE_MEMORY_PERCENT:.2f}%"
        )
    return percent


def krawtchouk_direct(j: int, i: int, *, q: int = Q, n: int = N) -> int:
    """Direct defining binomial sum for the q-ary Krawtchouk coefficient."""

    if not (0 <= i <= n and 0 <= j <= n):
        raise ValueError("indices must lie in 0..n")
    lower = max(0, j - (n - i))
    upper = min(i, j)
    return sum(
        (-1) ** t
        * (q - 1) ** (j - t)
        * math.comb(i, t)
        * math.comb(n - i, j - t)
        for t in range(lower, upper + 1)
    )


def dense_candidate() -> list[int]:
    values = [0] * (N + 1)
    for weight, count in CANDIDATE_SPARSE.items():
        values[weight] = count
    return values


def macwilliams_direct(a_values: Iterable[int]) -> tuple[list[int], list[int]]:
    """Return exact dual coefficients and pre-division numerators."""

    a = list(a_values)
    if len(a) != N + 1:
        raise ValueError(f"expected {N + 1} primal coefficients")
    numerators = [
        sum(a[i] * krawtchouk_direct(j, i) for i in range(N + 1))
        for j in range(N + 1)
    ]
    if any(value % CODE_SIZE for value in numerators):
        bad = [j for j, value in enumerate(numerators) if value % CODE_SIZE]
        raise ValueError(f"nonintegral MacWilliams coefficients at {bad}")
    return [value // CODE_SIZE for value in numerators], numerators


def condition_failures(
    a_values: Iterable[object],
    b_values: Iterable[object],
    *,
    check_transform: bool = True,
) -> list[str]:
    """List all failed conditions without short-circuiting."""

    a = list(a_values)
    b = list(b_values)
    failures: list[str] = []
    if len(a) != N + 1:
        return ["A length"]
    if len(b) != N + 1:
        return ["B length"]

    a_integral = all(type(value) is int for value in a)
    b_integral = all(type(value) is int for value in b)
    if not a_integral:
        failures.append("A integral")
    if not b_integral:
        failures.append("B integral")
    if not a_integral or not b_integral:
        return failures

    if a[0] != 1:
        failures.append("A0")
    if any(value < 0 for value in a):
        failures.append("A nonnegative")
    if sum(a) != CODE_SIZE:
        failures.append("A size")
    if any(a[i] and i % 3 for i in range(1, N + 1)):
        failures.append("A support divisible by 3")
    if any(a[i] % 2 for i in range(1, N + 1)):
        failures.append("nonzero A even")
    if a[198] < 462:
        failures.append("A198 lower bound")

    if any(value < 0 for value in b):
        failures.append("B nonnegative")
    if b[0] != 1:
        failures.append("B0")
    if b[1] != 0 or b[2] != 0:
        failures.append("projectivity B1=B2=0")
    if any(b[i] < a[i] for i in range(N + 1)):
        failures.append("formal self-orthogonal dominance")
    for weight, lower in DUAL_LOWER_BOUNDS.items():
        if b[weight] < lower:
            failures.append(f"B{weight} lower bound")
    if sum(b) != DUAL_SIZE:
        failures.append("dual size")

    if check_transform:
        numerators = [
            sum(a[i] * krawtchouk_direct(j, i) for i in range(N + 1))
            for j in range(N + 1)
        ]
        if any(value % CODE_SIZE for value in numerators):
            failures.append("MacWilliams integrality")
        elif [value // CODE_SIZE for value in numerators] != b:
            failures.append("MacWilliams equality")
    return failures


def build_result() -> dict[str, object]:
    enforce_memory_floor()
    a = dense_candidate()
    b, numerators = macwilliams_direct(a)
    failures = condition_failures(a, b)
    if failures:
        raise AssertionError(f"candidate failed: {failures}")

    upstream = {
        relative: sha256_path(ROOT / relative) for relative in UPSTREAM_PATHS
    }
    nonzero_b = {str(j): value for j, value in enumerate(b) if value}
    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "Conditional formal ordinary weight-enumerator feasibility for a "
            "centered projective self-orthogonal ternary [231,11] code"
        ),
        "parameters": {
            "q": Q,
            "n": N,
            "dimension": K,
            "primal_size": CODE_SIZE,
            "dual_size": DUAL_SIZE,
        },
        "candidate_A_sparse": {
            str(weight): count for weight, count in CANDIDATE_SPARSE.items()
        },
        "candidate_A": a,
        "macwilliams": {
            "formula": (
                "K_j(i)=sum_t (-1)^t*2^(j-t)*C(i,t)*C(231-i,j-t)"
            ),
            "implementation": "direct finite binomial sum",
            "B": b,
            "nonzero_B": nonzero_b,
            "numerator_remainders_mod_3^11": [
                value % CODE_SIZE for value in numerators
            ],
        },
        "checks": {
            "A0_is_1": a[0] == 1,
            "all_232_A_integral_nonnegative": all(
                type(value) is int and value >= 0 for value in a
            ),
            "A_sum_is_3^11": sum(a) == CODE_SIZE,
            "A_support_divisible_by_3": all(
                not a[i] or i % 3 == 0 for i in range(1, N + 1)
            ),
            "nonzero_A_even": all(a[i] % 2 == 0 for i in range(1, N + 1)),
            "A198_at_least_462": a[198] >= 462,
            "all_232_B_integral": all(
                value % CODE_SIZE == 0 for value in numerators
            ),
            "all_232_B_nonnegative": all(value >= 0 for value in b),
            "B1_B2_zero": b[1] == b[2] == 0,
            "formal_dominance_B_ge_A": all(
                b[i] >= a[i] for i in range(N + 1)
            ),
            "dual_lower_bounds": {
                str(weight): {
                    "actual": b[weight],
                    "required": lower,
                    "pass": b[weight] >= lower,
                }
                for weight, lower in DUAL_LOWER_BOUNDS.items()
            },
            "B_sum_is_3^220": sum(b) == DUAL_SIZE,
            "all_conditions": True,
        },
        "additional_ordinary_conditions_not_in_frozen_target": {
            "nonzero_B_even_from_ternary_scalar_pairing": all(
                value % 2 == 0 for value in b[1:]
            ),
            "nonzero_B_minus_A_even": all(
                (b[i] - a[i]) % 2 == 0 for i in range(1, N + 1)
            ),
            "B231_at_least_2_from_recorded_all_one_dual_word": b[231] >= 2,
            "B231_actual": b[231],
        },
        "resources": {
            "minimum_free_memory_percent": MIN_FREE_MEMORY_PERCENT,
            "free_memory_floor_passed": True,
        },
        "upstream_sha256": upstream,
        "limitations": [
            "This verifies one formal ordinary weight enumerator only.",
            "It does not construct or classify a ternary linear code.",
            "It does not supply a complete weight enumerator or endpoint object.",
            "It does not construct or exclude an srg(99,14,1,2).",
            "The code constraints are conditional on the Wave39 centered boundary.",
            "Novelty and priority are not assessed.",
        ],
    }


def canonical_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()

    result = build_result()
    text = canonical_json(result)
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8", newline="\n")
        print(f"WROTE {args.output}")
        return 0

    expected = args.verify.read_text(encoding="utf-8")
    if expected != text:
        print(f"MISMATCH {args.verify}")
        return 1
    print(f"VERIFIED {args.verify}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
