#!/usr/bin/env python3
"""Convert Wave152 negative directions into exact linear endpoint cuts.

For a fixed four-root type tau and integer flag direction v, covariance gives

    R_tau * sum_H q_H(v) x_H - (v^T s_tau)^2 >= 0.

Here q_H is the exact coefficient of an induced class H in the raw second
moment, s_tau is fixed by the order-six counts, and H has order 6, 7, or 8.
The resulting inequality is linear in the order-seven and order-eight induced
counts at the frozen n3=4158 endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SCOUT_PATH = HERE / "four_root_scout.py"
SCOUT_RESULT = HERE / "four-root-scout.json"
OUTPUT = HERE / "exact-cuts.json"


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


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def generic_count_maps(
    inputs: dict[str, Any], witness: dict[str, Any]
) -> dict[int, dict[int, Fraction]]:
    maps: dict[int, dict[int, Fraction]] = {
        4: {
            int(mask): Fraction(int(count))
            for mask, count in inputs["lower_counts"][4].items()
        },
        6: {
            int(mask): Fraction(int(count))
            for mask, count in inputs["lower_counts"][6].items()
        },
        7: {int(mask): Fraction(0) for mask in inputs["classes"][7]},
        8: {int(mask): Fraction(0) for mask in inputs["classes8"]},
    }
    for order, key in ((7, "x7_support"), (8, "x8_support")):
        for record in witness[key]:
            maps[order][int(record["canonical_mask"])] = Fraction(
                str(record["count"])
            )
    require(
        all(value.denominator == 1 for value in maps[7].values()),
        "order-seven counts must be integral",
    )
    return maps


def dense_direction(block: dict[str, Any]) -> list[int]:
    direction = [0] * int(block["flag_count"])
    certificate = block["negative_certificate"]
    require(certificate is not None, "missing negative certificate")
    for index, value in zip(
        certificate["indices"], certificate["vector"], strict=True
    ):
        direction[int(index)] = int(value)
    return direction


def class_coefficients(
    graph_mask: int,
    graph_order: int,
    root_mask: int,
    direction: Sequence[int],
    flag_index: dict[int, int],
    scout: Any,
    wave147: Any,
) -> tuple[int, int]:
    """Return (first-moment coefficient, quadratic coefficient)."""
    vertices = tuple(range(graph_order))
    pair_indices = scout.covering_pair_indices(graph_order - 4)
    first = 0
    quadratic = 0
    for roots in itertools.permutations(vertices, 4):
        if (
            scout.induced_mask(
                graph_mask, graph_order, roots, wave147.edge_positions
            )
            != root_mask
        ):
            continue
        complement = tuple(vertex for vertex in vertices if vertex not in roots)
        free_pairs = tuple(itertools.combinations(complement, 2))
        values = [
            direction[
                flag_index[
                    scout.canonical_four_root_flag(
                        scout.induced_mask(
                            graph_mask,
                            graph_order,
                            roots + free_pair,
                            wave147.edge_positions,
                        ),
                        wave147.transform_mask,
                    )
                ]
            ]
            for free_pair in free_pairs
        ]
        if graph_order == 6:
            require(len(values) == 1, "bad order-six complement")
            first += values[0]
        quadratic += sum(values[left] * values[right] for left, right in pair_indices)
    return first, quadratic


def build_cut(
    block: dict[str, Any],
    scout: Any,
    wave147: Any,
    inputs: dict[str, Any],
    count_maps: dict[int, dict[int, Fraction]],
    memory_samples: list[dict[str, Any]],
    stored_count_scale: int,
) -> dict[str, Any]:
    root_mask = int(block["root_mask"])
    root_count = int(block["root_embedding_count"])
    direction = dense_direction(block)
    flags = tuple(int(mask) for mask in block["flag_masks"])
    flag_index = {flag: index for index, flag in enumerate(flags)}

    coefficients: dict[int, dict[int, int]] = {6: {}, 7: {}, 8: {}}
    first_coefficients: dict[int, int] = {}
    for order in (6, 7, 8):
        classes = (
            tuple(int(mask) for mask in inputs["classes"][order])
            if order <= 7
            else tuple(int(mask) for mask in inputs["classes8"])
        )
        for class_index, class_mask in enumerate(classes):
            first, quadratic = class_coefficients(
                class_mask,
                order,
                root_mask,
                direction,
                flag_index,
                scout,
                wave147,
            )
            if order == 6 and first:
                first_coefficients[class_mask] = first
            if quadratic:
                coefficients[order][class_mask] = quadratic
            if class_index % 64 == 0:
                memory_samples.append(
                    scout.memory_record(
                        f"cut_root_{root_mask}_order_{order}_class_{class_index}"
                    )
                )

    projected_first = sum(
        int(count_maps[6][mask]) * coefficient
        for mask, coefficient in first_coefficients.items()
    )
    constant = (
        root_count
        * sum(
            int(count_maps[6][mask]) * coefficient
            for mask, coefficient in coefficients[6].items()
        )
        - projected_first * projected_first
    )
    dense7 = [
        root_count * coefficients[7].get(int(mask), 0)
        for mask in inputs["classes"][7]
    ]
    dense8 = [
        root_count * coefficients[8].get(int(mask), 0)
        for mask in inputs["classes8"]
    ]
    divisor = math.gcd(abs(constant), *map(abs, dense7), *map(abs, dense8))
    require(divisor > 0, "zero covariance cut")
    primitive_constant = constant // divisor
    primitive7 = [value // divisor for value in dense7]
    primitive8 = [value // divisor for value in dense8]

    exact_value = Fraction(constant)
    exact_value += sum(
        coefficient * count_maps[7][int(mask)]
        for coefficient, mask in zip(dense7, inputs["classes"][7], strict=True)
    )
    exact_value += sum(
        coefficient * count_maps[8][int(mask)]
        for coefficient, mask in zip(dense8, inputs["classes8"], strict=True)
    )
    stored_scaled = int(block["negative_certificate"]["quadratic_value_scaled"])
    require(
        stored_count_scale * exact_value == stored_scaled,
        (
            f"cut replay disagrees for root {root_mask}: "
            f"{stored_count_scale * exact_value}"
        ),
    )
    require(exact_value < 0, "stored direction is not an exact cut")

    core = {
        "root_mask": root_mask,
        "root_embedding_count": root_count,
        "flag_count": len(flags),
        "direction": direction,
        "sense": (
            "constant + sum(a7_H*x7_H) + sum(a8_H*x8_H) >= 0"
        ),
        "constant": str(primitive_constant),
        "order7_coefficients": [
            {"canonical_mask": int(mask), "coefficient": str(coefficient)}
            for mask, coefficient in zip(
                inputs["classes"][7], primitive7, strict=True
            )
            if coefficient
        ],
        "order8_coefficients": [
            {"canonical_mask": int(mask), "coefficient": str(coefficient)}
            for mask, coefficient in zip(inputs["classes8"], primitive8, strict=True)
            if coefficient
        ],
        "primitive_divisor": str(divisor),
        "wave150_witness_value": str(exact_value / divisor),
        "wave150_witness_unscaled_value": str(exact_value),
        "projected_first_moment": str(projected_first),
        "order6_quadratic_nonzeros": len(coefficients[6]),
    }
    if stored_count_scale == 4:
        core["stored_four_times_value"] = str(stored_scaled)
    else:
        core["stored_scaled_value"] = str(stored_scaled)
        core["stored_count_scale"] = stored_count_scale
    return {**core, "cut_sha256": canonical_sha256(core)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluation", type=Path, default=SCOUT_RESULT)
    parser.add_argument("--witness", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--max-cuts", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.evaluation = args.evaluation.resolve()
    args.output = args.output.resolve()
    if args.witness is not None:
        args.witness = args.witness.resolve()
    started = time.time()
    scout = load_module("wave152_scout_frozen", SCOUT_PATH)
    wave147 = load_module("wave152_cut_wave147", scout.WAVE147)
    wave150 = load_module("wave152_cut_wave150", scout.WAVE150_MODEL)
    inputs = wave150.load_inputs(False)
    witness_path = scout.WITNESS if args.witness is None else args.witness
    witness = json.loads(witness_path.read_text(encoding="utf-8"))
    count_maps = generic_count_maps(inputs, witness)
    result = json.loads(args.evaluation.read_text(encoding="utf-8"))
    stored_count_scale = int(
        result.get(
            "count_denominator_scale",
            result.get("method", {}).get("count_denominator_scale", 0),
        )
    )
    require(stored_count_scale > 0, "missing stored count scale")
    memory_samples = [scout.memory_record("cut_build_start")]
    negative_blocks = [
        block
        for block in result["root_blocks"]
        if block["negative_certificate"] is not None
    ]
    negative_blocks.sort(
        key=lambda block: float(
            block["minimum_numeric_eigenvalue_after_max_entry_scaling"]
        )
    )
    if args.max_cuts > 0:
        negative_blocks = negative_blocks[: args.max_cuts]
    cuts = [
        build_cut(
            block,
            scout,
            wave147,
            inputs,
            count_maps,
            memory_samples,
            stored_count_scale,
        )
        for block in negative_blocks
    ]
    if args.evaluation.resolve() == SCOUT_RESULT.resolve():
        require([cut["root_mask"] for cut in cuts] == [3, 12], "cut roots changed")
    memory_samples.append(scout.memory_record("cut_build_complete"))
    payload = {
        "format": "wave152-four-root-exact-cuts-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Two exact valid covariance inequalities in the order-seven and "
            "order-eight induced counts at the frozen n3=4158 endpoint."
        ),
        "inputs": {
            str(SCOUT_PATH.relative_to(ROOT)).replace("\\", "/"): scout.sha256_file(
                SCOUT_PATH
            ),
            str(args.evaluation.relative_to(ROOT)).replace(
                "\\", "/"
            ): scout.sha256_file(args.evaluation),
            str(witness_path.relative_to(ROOT)).replace(
                "\\", "/"
            ): scout.sha256_file(witness_path),
        },
        "cuts": cuts,
        "limitations": [
            "The cuts refute the stored Wave150 witness, not the whole endpoint.",
            "This discovery package cannot independently verify itself.",
            "No graph, strict upper bound, or Conway-99 resolution is claimed.",
        ],
        "resource_report": {
            "elapsed_seconds": time.time() - started,
            "minimum_free_physical_memory_percent": min(
                float(record["free_physical_memory_percent"])
                for record in memory_samples
            ),
            "samples": memory_samples,
        },
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            [
                {
                    "root_mask": cut["root_mask"],
                    "cut_sha256": cut["cut_sha256"],
                    "witness_value": cut["wave150_witness_value"],
                    "order7_nonzeros": len(cut["order7_coefficients"]),
                    "order8_nonzeros": len(cut["order8_coefficients"]),
                }
                for cut in cuts
            ],
            indent=2,
        )
    )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
