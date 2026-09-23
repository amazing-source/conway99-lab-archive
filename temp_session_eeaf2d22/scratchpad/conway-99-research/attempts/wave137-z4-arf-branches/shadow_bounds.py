"""Exact Krawtchouk shadow-bound replay on the two K5 witnesses."""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave137_exact_check", HERE / "exact_check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)
BASE = CHECK.BASE
ARF_MAGNITUDE = 1 << 27


def encode(value: Fraction | int) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def audit(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    replay = CHECK.verify(path)
    if not replay["terminal_witness_replayed"]:
        raise AssertionError("input is not an exact replayed witness")
    if replay["max_moment"] != 5:
        raise AssertionError("shadow audit expects a cumulative K5 witness")
    image, _dual = BASE.arrays(payload)
    violations = []
    records = []
    for degree in range(6, BASE.N + 1):
        moment = CHECK.signed_krawtchouk(image, degree)
        bound = ARF_MAGNITUDE * comb(BASE.N, degree)
        record = {
            "degree": degree,
            "M_t": encode(moment),
            "bound": str(bound),
            "satisfied": abs(moment) <= bound,
        }
        records.append(record)
        if abs(moment) > bound:
            violations.append(
                {
                    **record,
                    "excess": encode(abs(moment) - bound),
                    "violated_side": (
                        "upper" if moment > bound else "lower"
                    ),
                }
            )
    return {
        "path": str(path),
        "sign": payload["sign"],
        "bounds_checked": len(records),
        "violated_degrees": [
            violation["degree"] for violation in violations
        ],
        "violations": violations,
        "all_records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "shadow-bound-audit.json",
    )
    args = parser.parse_args()
    result = {
        "format": "wave137-binary-shadow-bound-audit-v1",
        "claim_label": "DERIVED",
        "bound": "|M_t| <= 2^27 * binom(99,t)",
        "audits": [audit(path) for path in args.paths],
        "limitations": [
            "The audit concerns formal rational Wave132 witnesses.",
            "No divisibility or parity condition on M_t/2^27 is imposed.",
        ],
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for audit_result in result["audits"]:
        print(
            audit_result["sign"],
            audit_result["violated_degrees"],
        )


if __name__ == "__main__":
    main()
