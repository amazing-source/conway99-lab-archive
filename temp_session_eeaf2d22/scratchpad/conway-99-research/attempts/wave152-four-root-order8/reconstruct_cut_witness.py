#!/usr/bin/env python3
"""Reconstruct an exact endpoint pseudowitness after the first Wave152 cuts.

The numerical HiGHS point is used only to choose a support and identify the
root-mask-12 cut as active.  Order-seven counts are rounded and checked
exactly.  An exact rational order-eight vector is then solved from the frozen
Wave150 equalities plus that active cut and replayed against both Wave152
inequalities.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WAVE150_PATH = ROOT / "attempts/wave150-order8-sdp-scout/exact_rank1_witness.py"
MODEL_PATH = ROOT / "attempts/wave150-order8-sdp-scout/endpoint_sdp.py"
ROW_SYSTEM = ROOT / "attempts/wave44-rooted-flags/row-system.json"
CANDIDATE_PATH = HERE / "zero-face-two-cuts-highs.json"
CUTS_PATH = HERE / "exact-cuts.json"
OUTPUT = HERE / "exact-witness-after-two-cuts.json"

N = 99
C7 = math.comb(N, 7)
C8 = math.comb(N, 8)
ACTIVE_ROOTS = (12,)
Y_VALUE = 4158


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cut_dense(
    cut: dict[str, Any],
    classes7: tuple[int, ...],
    classes8: tuple[int, ...],
) -> tuple[int, list[int], list[int]]:
    index7 = {mask: index for index, mask in enumerate(classes7)}
    index8 = {mask: index for index, mask in enumerate(classes8)}
    dense7 = [0] * len(classes7)
    dense8 = [0] * len(classes8)
    for record in cut["order7_coefficients"]:
        dense7[index7[int(record["canonical_mask"])]] = int(record["coefficient"])
    for record in cut["order8_coefficients"]:
        dense8[index8[int(record["canonical_mask"])]] = int(record["coefficient"])
    return int(cut["constant"]), dense7, dense8


def rounded_order7(
    candidate: dict[str, Any],
    row_system: dict[str, Any],
    rounding_tolerance: float,
) -> tuple[list[int], dict[str, Any]]:
    density = np.asarray(candidate["candidate"]["p7_density"], dtype=np.float64)
    raw = density * C7
    rounded = np.rint(raw).astype(np.int64)
    maximum_error = float(np.max(np.abs(raw - rounded)))
    require(maximum_error < rounding_tolerance, "order-seven rounding unsafe")
    require(int(rounded.min()) >= 0, "negative rounded order-seven count")
    require(int(rounded.sum()) == C7, "rounded order-seven total changed")
    errors = []
    rows_passed = 0
    for family_name in ("base", "vertex", "edge", "nonedge"):
        family = row_system["families"][family_name]
        for index, (row, rhs) in enumerate(
            zip(family["rows"], family["rhs"], strict=True)
        ):
            value = (
                sum(
                    int(coefficient) * int(count)
                    for coefficient, count in zip(
                        row[:-1], rounded, strict=True
                    )
                )
                + int(row[-1]) * Y_VALUE
                - int(rhs)
            )
            if value:
                errors.append((family_name, index, value))
            rows_passed += 1
    require(not errors, f"rounded x7 fails Wave44: {errors[:3]}")
    return rounded.tolist(), {
        "sum": int(rounded.sum()),
        "support": int(np.count_nonzero(rounded)),
        "maximum_rounding_error": maximum_error,
        "y": Y_VALUE,
        "h11": 4 * Y_VALUE,
        "wave44_rows_passed": rows_passed,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, default=CANDIDATE_PATH)
    parser.add_argument("--cuts", type=Path, nargs="+", default=[CUTS_PATH])
    parser.add_argument("--active-cut-sha", action="append", default=[])
    parser.add_argument("--rounding-tolerance", type=float, default=0.01)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidate_path = args.candidate.resolve()
    cut_paths = [path.resolve() for path in args.cuts]
    output_path = args.output.resolve()
    started = time.time()
    wave150 = load_module("wave152_exact_wave150", WAVE150_PATH)
    model = load_module("wave152_exact_model", MODEL_PATH)
    inputs = model.load_inputs(True)
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    row_system = json.loads(ROW_SYSTEM.read_text(encoding="utf-8"))
    x7, x7_record = rounded_order7(
        candidate, row_system, args.rounding_tolerance
    )
    rows, row_record = wave150.build_rows(inputs, x7)
    classes7 = tuple(int(mask) for mask in inputs["classes"][7])
    classes8 = tuple(int(mask) for mask in inputs["classes8"])

    cuts = []
    for path in cut_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        cuts.extend(payload["cuts"] if "cuts" in payload else [payload["cut"]])
    require(
        len({cut["cut_sha256"] for cut in cuts}) == len(cuts),
        "duplicate cuts",
    )
    active_hashes = set(args.active_cut_sha)
    if not active_hashes:
        active_hashes = {
            cut["cut_sha256"] for cut in cuts if int(cut["root_mask"]) in ACTIVE_ROOTS
        }
    require(
        active_hashes.issubset({cut["cut_sha256"] for cut in cuts}),
        "active cut hash was not supplied",
    )
    cut_records = {}
    for cut in cuts:
        root_mask = int(cut["root_mask"])
        cut_hash = str(cut["cut_sha256"])
        constant, dense7, dense8 = cut_dense(cut, classes7, classes8)
        fixed = constant + sum(
            coefficient * count
            for coefficient, count in zip(dense7, x7, strict=True)
        )
        cut_records[cut_hash] = {
            "cut": cut,
            "root_mask": root_mask,
            "constant": constant,
            "dense7": dense7,
            "dense8": dense8,
            "fixed_part_through_order7": fixed,
        }
        if cut_hash in active_hashes:
            wave150.add_row(
                rows,
                f"wave152_active_cut_{cut_hash}",
                {
                    column: coefficient
                    for column, coefficient in enumerate(dense8)
                    if coefficient
                },
                -fixed,
            )

    raw8 = [
        float(value) * C8 for value in candidate["candidate"]["p8_density"]
    ]
    support = [index for index, value in enumerate(raw8) if value > 1.0]
    outside = [
        abs(value) for index, value in enumerate(raw8) if index not in support
    ]
    require(max(outside, default=0.0) < 0.1, "excluded coordinate too large")
    restricted, _ = wave150.restrict_rows(rows, support)
    selected, modular = wave150.modular_independent_rows(
        restricted, len(support)
    )
    require(modular["full_column_rank"], f"support not fixed: {modular}")
    solution, solve_record = wave150.exact_solve_and_verify(
        restricted, selected, len(support)
    )
    full_solution = [wave150.fmpq(0)] * len(classes8)
    for global_index, value in zip(support, solution, strict=True):
        full_solution[global_index] = value

    cut_values = {}
    for cut_hash, record in cut_records.items():
        root_mask = int(record["root_mask"])
        value = wave150.fmpq(record["fixed_part_through_order7"])
        value += sum(
            (
                wave150.fmpq(coefficient) * full_solution[index]
                for index, coefficient in enumerate(record["dense8"])
                if coefficient
            ),
            wave150.fmpq(0),
        )
        require(value >= 0, f"exact witness violates root-{root_mask} cut: {value}")
        if cut_hash in active_hashes:
            require(value == 0, f"active cut {cut_hash} not exact")
        cut_values[cut_hash] = {
            "root_mask": root_mask,
            "value": str(value),
            "active": cut_hash in active_hashes,
        }

    solve_record["restricted_rows_passed"] = solve_record.pop("all_rows_passed")
    solve_record["all_rows_passed"] = len(rows)
    payload = {
        "format": "wave152-exact-endpoint-witness-after-two-cuts-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Exact rational feasibility of the Wave150 zero-covariance "
            "endpoint system after both Wave152 four-root cuts, with the "
            "root-mask-12 inequality active and h11=16632."
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path)
            for path in (
                WAVE150_PATH,
                MODEL_PATH,
                ROW_SYSTEM,
                candidate_path,
                *cut_paths,
            )
        },
        "selection": {
            "support_size": len(support),
            "support": support,
            "excluded_maximum_absolute_raw_count": max(outside, default=0.0),
            "modular_rank": modular,
            "selected_row_indices": selected,
            "selected_row_labels": [restricted[index].label for index in selected],
        },
        "x7_record": x7_record,
        "row_record": row_record,
        "exact_solve": solve_record,
        "active_cut_hashes": sorted(active_hashes),
        "exact_cut_values": cut_values,
        "x7_support": [
            {"canonical_mask": mask, "count": count}
            for mask, count in zip(classes7, x7, strict=True)
            if count
        ],
        "x8_support": [
            {"canonical_mask": classes8[index], "count": str(value)}
            for index, value in enumerate(full_solution)
            if value
        ],
        "conclusion": {
            "finite_relaxation_after_two_cuts": "EXACT_RATIONAL_FEASIBLE",
            "graph_constructed": False,
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "This exact count vector is not a graph.",
            "It has not yet been tested against every four-root covariance block.",
            "The discovery package cannot verify itself.",
        ],
        "elapsed_seconds": time.time() - started,
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(output_path),
                "support7": len(payload["x7_support"]),
                "support8": len(payload["x8_support"]),
                "maximum_denominator": solve_record["maximum_denominator"],
                "all_rows_passed": solve_record["all_rows_passed"],
                "cut_values": cut_values,
                "elapsed_seconds": payload["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
