#!/usr/bin/env python3
"""Replay the Wave136 Arf/Gauss diagnostic on the sealed Wave131 witness."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from math import comb
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WITNESS = (
    ROOT / "attempts" / "wave131-binary-lcd-enumerator" / "rational-witness.json"
)


def frac(text: str | int) -> Fraction:
    return Fraction(str(text))


def signed_even_sum(coefficients: dict[str, str]) -> Fraction:
    return sum(
        (
            (-1 if (weight // 2) % 2 else 1) * frac(value)
            for key, value in coefficients.items()
            if (weight := int(key)) % 2 == 0
        ),
        Fraction(0),
    )


def encode(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def derive(witness_path: Path) -> dict[str, object]:
    witness = json.loads(witness_path.read_text(encoding="utf-8"))
    g_r = signed_even_sum(witness["image_coefficients"])
    g_e = signed_even_sum(witness["dual_coefficients"])
    g_h = sum(
        ((-1 if (weight // 2) % 2 else 1) * comb(99, weight)
         for weight in range(0, 100, 2)),
        0,
    )
    target_r = 1 << 27
    target_e = 1 << 22
    checks = {
        "ambient_gauss_sum_is_minus_2pow49": g_h == -(1 << 49),
        "ordinary_macwilliams_ratio": g_e == -g_r / 32,
        "wave131_witness_violates_arf_magnitude": abs(g_r) != target_r,
        "target_product_for_either_branch": target_r * -target_e == g_h,
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    return {
        "format": "wave136-arf-gauss-diagnostic-v1",
        "claim_label": "DERIVED",
        "scope": "Exact Arf/Gauss branch diagnostic on the sealed Wave131 formal rational witness.",
        "witness": str(witness_path.relative_to(ROOT)).replace("\\", "/"),
        "dimensions": {"ambient_even": 98, "image": 54, "even_dual": 44},
        "forced_branches": {
            "image_gauss_sum": ["-134217728", "134217728"],
            "even_dual_gauss_sum": ["4194304", "-4194304"],
            "sign_coupling": "G_E=-G_R/32",
        },
        "ambient_gauss_sum": str(g_h),
        "witness_values": {
            "G_R": encode(g_r),
            "G_E": encode(g_e),
            "absolute_G_R_over_2pow27": encode(abs(g_r) / target_r),
        },
        "checks": checks,
        "status_wall": {
            "wave131_formal_witness": "REFUTED_BY_ARF_MAGNITUDE",
            "binary_code": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "graph": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--witness", type=Path, default=DEFAULT_WITNESS)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = derive(args.witness.resolve())
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("verification mismatch")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
