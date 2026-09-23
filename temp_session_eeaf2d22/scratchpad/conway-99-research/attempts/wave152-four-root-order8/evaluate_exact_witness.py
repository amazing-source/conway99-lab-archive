#!/usr/bin/env python3
"""Evaluate any exact order-8 endpoint pseudowitness in all four-root blocks."""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SCOUT_PATH = HERE / "four_root_scout.py"


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


def exact_count_maps(
    inputs: dict[str, Any], witness: dict[str, Any]
) -> tuple[dict[int, dict[int, Fraction]], int]:
    maps = {
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
        "order-seven counts are not integral",
    )
    denominator_scale = math.lcm(
        *(value.denominator for value in maps[8].values())
    )
    return maps, denominator_scale


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    scout = load_module("wave152_general_evaluator", SCOUT_PATH)
    wave147 = load_module("wave152_general_wave147", scout.WAVE147)
    wave150 = load_module("wave152_general_wave150", scout.WAVE150_MODEL)
    inputs = wave150.load_inputs(False)
    witness = json.loads(args.witness.read_text(encoding="utf-8"))
    counts, count_scale = exact_count_maps(inputs, witness)
    memory = [scout.memory_record("general_evaluation_start")]

    flags = [
        scout.flag_universe(
            root_mask,
            wave147.edge_positions,
            wave147.locally_admissible,
            wave147.transform_mask,
        )
        for root_mask in scout.ROOT_MASKS
    ]
    flag_indices = [
        {flag: index for index, flag in enumerate(family)}
        for family in flags
    ]
    moments_scaled = [
        [[0] * len(family) for _ in family] for family in flags
    ]
    first_moments_scaled = [[0] * len(family) for family in flags]
    root_mask_to_index = {
        root_mask: index for index, root_mask in enumerate(scout.ROOT_MASKS)
    }
    functions = {
        "edge_positions": wave147.edge_positions,
        "canonical_flag": lambda mask: scout.canonical_four_root_flag(
            mask, wave147.transform_mask
        ),
    }
    enumeration = {}
    for order in (6, 7, 8):
        matched = 0
        products = 0
        nonzero = 0
        for class_index, (class_mask, weight) in enumerate(counts[order].items()):
            if not weight:
                continue
            nonzero += 1
            scaled = weight * count_scale
            require(scaled.denominator == 1, "count scaling failed")
            local_matched, local_products = scout.add_weighted_moments(
                class_mask,
                order,
                int(scaled),
                root_mask_to_index,
                flag_indices,
                moments_scaled,
                first_moments_scaled,
                functions,
            )
            matched += local_matched
            products += local_products
            if class_index % 64 == 0:
                memory.append(
                    scout.memory_record(
                        f"general_order_{order}_class_{class_index}"
                    )
                )
        enumeration[str(order)] = {
            "nonzero_classes": nonzero,
            "matched_root_embeddings_unweighted": matched,
            "emitted_products_unweighted": products,
        }

    classes4 = tuple(int(mask) for mask in inputs["classes"][4])
    free_pairs_full = math.comb(scout.N - 4, 2)
    blocks = []
    for root_index, root_mask in enumerate(scout.ROOT_MASKS):
        root_class = scout.class_for_root(
            root_mask, classes4, wave147.canonical_unrooted_by_degree
        )
        root_count = (
            scout.automorphism_size(root_mask, wave147.transform_mask)
            * int(counts[4][root_class])
        )
        s_scaled = first_moments_scaled[root_index]
        matrix_scaled = moments_scaled[root_index]
        require(
            sum(s_scaled) == count_scale * root_count * free_pairs_full,
            "first total failed",
        )
        require(
            sum(map(sum, matrix_scaled))
            == count_scale * root_count * free_pairs_full**2,
            "second total failed",
        )
        # count_scale*(R*M-s*s^T)
        centered_scaled = [
            [
                root_count * matrix_scaled[row][column]
                - s_scaled[row] * s_scaled[column] // count_scale
                for column in range(len(flags[root_index]))
            ]
            for row in range(len(flags[root_index]))
        ]
        require(
            all(
                s_scaled[row] * s_scaled[column] % count_scale == 0
                for row in range(len(flags[root_index]))
                for column in range(len(flags[root_index]))
            ),
            "centered scaling is not integral",
        )
        maximum = max(abs(value) for row in centered_scaled for value in row)
        numeric = np.asarray(centered_scaled, dtype=np.float64)
        if maximum:
            numeric /= float(maximum)
        eigenvalues, eigenvectors = np.linalg.eigh(numeric)
        minimum = float(eigenvalues[0])
        certificate = scout.exact_two_coordinate_certificate(centered_scaled)
        if certificate is None and minimum < -1e-9:
            certificate = scout.exact_eigenvector_certificate(
                centered_scaled, eigenvectors[:, 0]
            )
        if certificate is not None:
            certificate["flag_masks"] = [
                flags[root_index][index] for index in certificate["indices"]
            ]
        blocks.append(
            {
                "root_mask": root_mask,
                "root_embedding_count": root_count,
                "flag_count": len(flags[root_index]),
                "flag_masks": list(flags[root_index]),
                "centered_scale": (
                    f"{count_scale}*(R*M-s*s^T)"
                ),
                "maximum_absolute_scaled_entry": str(maximum),
                "minimum_numeric_eigenvalue_after_max_entry_scaling": minimum,
                "exact_status": (
                    "NOT_PSD"
                    if certificate is not None
                    else "NUMERICALLY_NO_SEPARATION"
                ),
                "negative_certificate": certificate,
            }
        )
    memory.append(scout.memory_record("general_evaluation_complete"))
    return {
        "format": "wave152-general-four-root-witness-evaluation-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "All nine four-root/two-free centered covariance blocks evaluated "
            "on one exact rational endpoint count pseudowitness."
        ),
        "input_witness": {
            "path": str(args.witness.relative_to(ROOT)).replace("\\", "/"),
            "sha256": scout.sha256_file(args.witness),
        },
        "count_denominator_scale": count_scale,
        "enumeration": enumeration,
        "root_blocks": blocks,
        "conclusion": {
            "exact_negative_blocks": [
                int(block["root_mask"])
                for block in blocks
                if block["negative_certificate"] is not None
            ],
            "witness_satisfies_all_four_root_blocks": (
                False
                if any(block["negative_certificate"] is not None for block in blocks)
                else "UNKNOWN_WITHOUT_EXACT_PSD"
            ),
            "endpoint_n3_4158": "UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "This discovery evaluator cannot independently verify itself.",
            "No negative block would not constitute an exact PSD proof.",
            "Refuting a count pseudowitness does not refute the endpoint.",
        ],
        "resource_report": {
            "elapsed_seconds": time.time() - started,
            "minimum_free_physical_memory_percent": min(
                float(record["free_physical_memory_percent"]) for record in memory
            ),
            "samples": memory,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--witness", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = evaluate(args)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["conclusion"], indent=2))
    for block in payload["root_blocks"]:
        print(
            f"root={block['root_mask']:>2} flags={block['flag_count']:>3} "
            f"min={block['minimum_numeric_eigenvalue_after_max_entry_scaling']:.6g} "
            f"status={block['exact_status']}"
        )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
