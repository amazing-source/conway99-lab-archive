#!/usr/bin/env python3
"""Replace the Wave152 mask-12 eigenvector cut by the exact (1,-1) direction."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUILDER_PATH = HERE / "build_exact_cuts.py"
EVALUATION = HERE / "four-root-evaluation-after-five-cuts.json"
WITNESS = HERE / "exact-witness-after-five-cuts.json"
OUTPUT = HERE / "simplified-mask12-cut.json"


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluation", type=Path, default=EVALUATION)
    parser.add_argument("--witness", type=Path, default=WITNESS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evaluation_path = args.evaluation.resolve()
    witness_path = args.witness.resolve()
    output_path = args.output.resolve()
    builder = load_module("wave152_simplified_builder", BUILDER_PATH)
    scout = load_module("wave152_simplified_scout", builder.SCOUT_PATH)
    wave147 = load_module("wave152_simplified_wave147", scout.WAVE147)
    wave150 = load_module("wave152_simplified_wave150", scout.WAVE150_MODEL)
    inputs = wave150.load_inputs(False)
    witness = json.loads(witness_path.read_text(encoding="utf-8"))
    counts = builder.generic_count_maps(inputs, witness)
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    original = next(
        block for block in evaluation["root_blocks"] if int(block["root_mask"]) == 12
    )
    certificate = original["negative_certificate"]
    require(
        certificate["kind"] == "negative_2x2_principal_minor",
        "mask-12 certificate is no longer two-dimensional",
    )
    a, b, c = map(int, certificate["principal_entries_scaled"])
    require(a == c and b > a, "mask-12 block lost equal-diagonal obstruction")
    simplified = dict(original)
    simplified["negative_certificate"] = {
        "kind": "manual_equal_diagonal_direction",
        "indices": list(certificate["indices"]),
        "vector": ["1", "-1"],
        "quadratic_value_scaled": str(2 * (a - b)),
        "flag_masks": list(certificate["flag_masks"]),
    }
    memory = [scout.memory_record("simplified_mask12_cut_start")]
    cut = builder.build_cut(
        simplified,
        scout,
        wave147,
        inputs,
        counts,
        memory,
        int(evaluation["count_denominator_scale"]),
    )
    memory.append(scout.memory_record("simplified_mask12_cut_complete"))
    payload = {
        "format": "wave152-simplified-mask12-cut-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Primitive exact covariance cut from the equal-diagonal mask-12 "
            "principal submatrix on flags 5428 and 6324."
        ),
        "derivation": {
            "principal_indices": list(certificate["indices"]),
            "flag_masks": list(certificate["flag_masks"]),
            "scaled_diagonal": str(a),
            "scaled_off_diagonal": str(b),
            "direction": [1, -1],
            "scaled_quadratic_value": str(2 * (a - b)),
        },
        "cut": cut,
        "limitations": [
            "This direction is valid universally, but its discovery package cannot verify itself.",
            "It separates one rational pseudowitness and does not exclude the endpoint.",
        ],
        "minimum_free_physical_memory_percent": min(
            float(record["free_physical_memory_percent"]) for record in memory
        ),
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "cut_sha256": cut["cut_sha256"],
                "constant": cut["constant"],
                "order7_nonzeros": len(cut["order7_coefficients"]),
                "order8_nonzeros": len(cut["order8_coefficients"]),
                "witness_value": cut["wave150_witness_value"],
            },
            indent=2,
        )
    )
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
