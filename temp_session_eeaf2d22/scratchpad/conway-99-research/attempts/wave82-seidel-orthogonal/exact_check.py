#!/usr/bin/env python3
"""Exact Wave 82 checker using only the Python standard library."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
from typing import Any


ORDER = 99
SURVIVING_RANKS = [28, 30, 32, 34, 36, 38, 40, 42]
INPUTS = {
    "verification/wave66-spherical-code-shift/independent-results.json":
        "3d6689b292fa5605e012da55f94e299926c1762c6ec77b8ef06007c62a65b61f",
    "verification/wave51-seidel-smith/independent-result.json":
        "1dda847b1180ac881f2ccce80285a2a50d9cab1f0f910f7dbdf9a6087d53d793",
}


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
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def enforce_memory_floor(floor: float = 20.0) -> None:
    if os.name != "nt":
        return
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    free = 100.0 * status.ullAvailPhys / status.ullTotalPhys
    if free < floor:
        raise MemoryError(
            f"available physical memory {free:.2f}% is below {floor:.2f}%"
        )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def multiply_algebra(
    left: tuple[int, int, int], right: tuple[int, int, int]
) -> tuple[int, int, int]:
    """Multiply aI+bJ+cS using J^2=99J, S^2=49(I+J), SJ=-70J."""
    a, b, c = left
    d, e, f = right
    return (
        a * d + 49 * c * f,
        a * e + b * d + 99 * b * e + 49 * c * f
        - 70 * (b * f + c * e),
        a * f + c * d,
    )


def load_imports(repo_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    for relative, expected in INPUTS.items():
        path = repo_root / relative
        actual = sha256(path)
        if actual != expected:
            raise AssertionError(
                f"input hash mismatch for {relative}: {actual} != {expected}"
            )
        payloads[relative] = json.loads(path.read_text(encoding="utf-8"))
    return (
        payloads[
            "verification/wave51-seidel-smith/independent-result.json"
        ],
        payloads[
            "verification/wave66-spherical-code-shift/independent-results.json"
        ],
    )


def validate_imports(
    seidel: dict[str, Any], wave66: dict[str, Any]
) -> None:
    if seidel["seidel_identity"]["formula"] != "S^2 = 49(I+J)":
        raise AssertionError("unexpected Seidel identity")
    if seidel["rational_spectra"]["seidel"] != {
        "-70": 1, "-7": 44, "7": 54
    }:
        raise AssertionError("unexpected corrected Seidel spectrum")
    if (
        seidel["smith_logic"]["closed_form"]
        != "diag(1^r,7^(99-2r),49^(r-1),490)"
    ):
        raise AssertionError("unexpected imported Seidel Smith form")
    ranks = wave66["gauss_and_milgram"]["surviving_ranks"]
    if ranks != SURVIVING_RANKS:
        raise AssertionError(f"unexpected Wave 66 ranks: {ranks}")


def smith_factors(r: int) -> list[int]:
    if r not in SURVIVING_RANKS:
        raise ValueError(f"rank {r} is outside the frozen survivor set")
    return (
        [1]
        + [9] * (r - 1)
        + [63] * (ORDER - 2 * r)
        + [441] * (r - 1)
        + [3969]
    )


def factor_profile(r: int) -> dict[str, Any]:
    factors = smith_factors(r)
    if len(factors) != ORDER:
        raise AssertionError("wrong Smith factor count")
    if any(b % a for a, b in zip(factors, factors[1:])):
        raise AssertionError("Smith divisibility chain failed")
    product = 1
    for factor in factors:
        product *= factor
    if product != 63 ** ORDER:
        raise AssertionError("Smith determinant failed")
    reciprocal = all(
        factors[i] * factors[ORDER - 1 - i] == 3969
        for i in range(ORDER)
    )
    if not reciprocal:
        raise AssertionError("Smith reciprocity failed")
    return {
        "factor_count": ORDER,
        "invariant_factor_counts": {
            "1": 1,
            "9": r - 1,
            "63": ORDER - 2 * r,
            "441": r - 1,
            "3969": 1,
        },
        "product": "63^99",
        "rank_f7": r,
        "reciprocal_pairs_product": 3969,
    }


def build_result(
    seidel: dict[str, Any], wave66: dict[str, Any]
) -> dict[str, Any]:
    validate_imports(seidel, wave66)
    t = (0, 7, 9)
    if multiply_algebra(t, t) != (3969, 0, 0):
        raise AssertionError("symbolic T^2 identity failed")
    if 7 + 9 != 16 or 7 - 9 != -2:
        raise AssertionError("entry alphabet failed")
    if 99 * 7 - 70 * 9 != 63:
        raise AssertionError("row sum failed")
    if (7 + 2 - 9, 16 + 2, -2 + 2) != (0, 18, 0):
        raise AssertionError("adjacency recovery failed")

    return {
        "claim_label": "DERIVED_DISCOVERY_ONLY",
        "conditional_scope": "hypothetical srg(99,14,1,2)",
        "equivalent_integral_orthogonal_matrix": {
            "adjacency_recovery": "A=(T+2J-9I)/18",
            "definition": "T=9S+7J=18A-2J+9I",
            "determinant": "63^99",
            "diagonal": 7,
            "off_diagonal_alphabet": [-2, 16],
            "order": 99,
            "row_sum": 63,
            "spectrum": {"-63": 44, "63": 55},
            "square": "T^2=3969I",
        },
        "smith_form": {
            "closed_form":
                "diag(1,9^(r-1),63^(99-2r),441^(r-1),3969)",
            "profiles": [factor_profile(r) for r in SURVIVING_RANKS],
            "seven_primary_exponents": "0^r,1^(99-2r),2^r",
            "three_primary_exponents": "0^1,2^97,4^1",
        },
        "status": {
            "contradiction_found": False,
            "matrix_constructed": False,
            "novelty": "UNKNOWN",
            "rank_rows_excluded": 0,
            "resolution": "UNKNOWN",
            "surviving_ranks": SURVIVING_RANKS,
        },
    }


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--print", action="store_true", dest="print_result")
    args = parser.parse_args()
    enforce_memory_floor()
    repo_root = Path(__file__).resolve().parents[2]
    seidel, wave66 = load_imports(repo_root)
    result = build_result(seidel, wave66)
    rendered = canonical_json(result)
    if args.verify:
        expected = args.verify
        if not expected.is_absolute():
            expected = repo_root / expected
        if expected.read_text(encoding="utf-8") != rendered:
            raise AssertionError(f"artifact mismatch: {expected}")
    if args.print_result or not args.verify:
        print(rendered, end="")
    print("PASS_WAVE82_SEIDEL_ORTHOGONAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
