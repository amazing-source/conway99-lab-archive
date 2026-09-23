"""Regenerate and exactly verify a Wave127 rational primal candidate."""

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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", type=int, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--columns-cache", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.candidate.read_text(encoding="utf-8"))
    qmax = max(args.cutoff, 10)
    if args.columns_cache and args.columns_cache.exists():
        import pickle

        with args.columns_cache.open("rb") as stream:
            cached = pickle.load(stream)
        if (
            cached.get("version") != MODEL.MODEL_CACHE_VERSION
            or cached.get("qmax") != qmax
        ):
            raise SystemExit("incompatible columns cache")
        columns = cached["columns"]
    else:
        columns, _module = MODEL.build_columns(qmax)
    equalities, inequalities = MODEL.build_constraints(columns, args.cutoff)
    solution = [Fraction(value) for value in payload.get("solution", [])]

    failed_equalities = []
    for constraint in equalities:
        value = sum(
            coefficient * solution[index]
            for index, coefficient in enumerate(constraint["row"])
        )
        if value != constraint["right"]:
            failed_equalities.append(
                {
                    "label": constraint["label"],
                    "value": MODEL.qtext(value),
                    "expected": MODEL.qtext(constraint["right"]),
                }
            )
    failed_inequalities = []
    tight = []
    for constraint in inequalities:
        value = sum(
            coefficient * solution[index]
            for index, coefficient in enumerate(constraint["row"])
        )
        if value < 0:
            failed_inequalities.append(
                {
                    "label": constraint["label"],
                    "value": MODEL.qtext(value),
                }
            )
        elif value == 0:
            tight.append(constraint["label"])

    verified = (
        payload.get("classification") == "EXACT_RATIONAL_FEASIBLE"
        and len(solution) == len(columns)
        and not failed_equalities
        and not failed_inequalities
    )
    result = {
        "format": "wave127-primal-verification-v1",
        "candidate": str(args.candidate),
        "cutoff": args.cutoff,
        "variables": len(columns),
        "equalities": len(equalities),
        "inequalities": len(inequalities),
        "failed_equalities": failed_equalities,
        "failed_inequalities": failed_inequalities,
        "tight_inequalities": len(tight),
        "classification": (
            "VERIFIED_EXACT_RATIONAL_FEASIBLE"
            if verified
            else "REFUTED_OR_UNVERIFIED"
        ),
    }
    text = MODEL.canonical_json(result)
    if args.write:
        args.write.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
