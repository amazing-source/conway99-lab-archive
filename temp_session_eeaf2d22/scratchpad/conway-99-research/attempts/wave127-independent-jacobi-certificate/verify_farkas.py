"""Independent exact-row check for a Wave127 Farkas certificate."""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave127_jacobi_lp", HERE / "jacobi_lp.py")
MODEL = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODEL)


def parse_rational(text: str) -> Fraction:
    return Fraction(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", type=int, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()

    certificate = json.loads(args.certificate.read_text(encoding="utf-8"))
    columns, _module = MODEL.build_columns(max(args.cutoff, 10))
    equalities, inequalities = MODEL.build_constraints(columns, args.cutoff)
    by_key = {
        ("equality", constraint["label"]): constraint
        for constraint in equalities
    }
    by_key.update(
        {
            ("inequality", constraint["label"]): constraint
            for constraint in inequalities
        }
    )

    row_sum = [Fraction(0)] * len(columns)
    right_sum = Fraction(0)
    missing = []
    negative = []
    for entry in certificate.get("entries", []):
        key = (entry["kind"], entry["label"])
        constraint = by_key.get(key)
        if constraint is None:
            missing.append(f"{key[0]}:{key[1]}")
            continue
        multiplier = parse_rational(entry["multiplier"])
        if entry["kind"] == "inequality" and multiplier < 0:
            negative.append(entry["label"])
        row_sum = [
            left + multiplier * right
            for left, right in zip(
                row_sum, constraint["row"], strict=True
            )
        ]
        if entry["kind"] == "equality":
            right_sum += multiplier * constraint["right"]

    verified = (
        certificate.get("classification") == "EXACT_FARKAS_VERIFIED"
        and not missing
        and not negative
        and not any(row_sum)
        and right_sum == 1
    )
    result = {
        "format": "wave127-farkas-verification-v1",
        "certificate": str(args.certificate),
        "cutoff": args.cutoff,
        "variables": len(columns),
        "equalities": len(equalities),
        "inequalities": len(inequalities),
        "entries": len(certificate.get("entries", [])),
        "missing_labels": missing,
        "negative_inequality_multipliers": negative,
        "nonzero_identity_coordinates": sum(bool(value) for value in row_sum),
        "right_hand_side": MODEL.qtext(right_sum),
        "classification": (
            "VERIFIED_EXACT_FARKAS"
            if verified
            else "REFUTED_OR_UNVERIFIED"
        ),
    }
    payload = MODEL.canonical_json(result)
    if args.write:
        args.write.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
