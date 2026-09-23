#!/usr/bin/env python3
"""Seal a compact deterministic handoff from the full Wave 47 reconstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
FULL_FILES = {
    "coefficients": HERE / "coefficients.json",
    "results": HERE / "results.json",
    "cuts": HERE / "cuts.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def build() -> dict[str, object]:
    coefficients = json.loads(FULL_FILES["coefficients"].read_text(encoding="utf-8"))
    results = json.loads(FULL_FILES["results"].read_text(encoding="utf-8"))
    cuts_payload = json.loads(FULL_FILES["cuts"].read_text(encoding="utf-8"))
    cuts = cuts_payload["cuts"]
    by_source_family_direction = {
        (
            cut["source"],
            cut["family"],
            int(cut["source_direction_index"]),
        ): cut
        for cut in cuts
    }

    representatives = []
    target_summaries = []
    for target in results["targets"]:
        source = target["name"]
        exact_families = [
            (family_name, family_record)
            for family_name, family_record in target["family_results"].items()
            if family_record["exact_negative_direction_count"] > 0
        ]
        require(exact_families, f"{source} has no exact negative direction")
        strongest_family, strongest_record = min(
            exact_families,
            key=lambda item: (
                item[1]["minimum_normalized_eigenvalue_float"],
                item[0],
            ),
        )
        key = (source, strongest_family, 0)
        require(key in by_source_family_direction, f"missing representative cut {key}")
        cut = by_source_family_direction[key]
        require(int(cut["source_cut_value"]) < 0, f"{source} cut is not separating")
        representatives.append(cut)
        target_summaries.append(
            {
                "name": source,
                "support_sha256": target["support_sha256"],
                "exactly_indefinite_family_count": target[
                    "exactly_indefinite_family_count"
                ],
                "total_exact_negative_directions": sum(
                    family["exact_negative_direction_count"]
                    for family in target["family_results"].values()
                ),
                "representative_family": strongest_family,
                "representative_minimum_normalized_eigenvalue_float": strongest_record[
                    "minimum_normalized_eigenvalue_float"
                ],
                "representative_cut_sha256": cut["cut_sha256"],
                "representative_cut_value": cut["source_cut_value"],
            }
        )

    require(len(representatives) == 17, "representative cut count changed")
    require(
        len({cut["source"] for cut in representatives}) == 17,
        "representatives do not cover every source",
    )

    controls = []
    for control in results["controls"]:
        controls.append(
            {
                "name": control["name"],
                "order": control["order"],
                "induced_subset_totals": control["induced_subset_totals"],
                "all_eight_direct_equal_expansion": all(
                    family["direct_equals_unrooted_expansion"]
                    for family in control["families"].values()
                ),
                "family_matrix_sha256": {
                    name: family["matrix_sha256"]
                    for name, family in control["families"].items()
                },
            }
        )

    handoff: dict[str, object] = {
        "format": "wave47-three-root-moment-compact-handoff-v1",
        "role": "construction",
        "claim_label": "CANDIDATE",
        "scope": (
            "Compact discovery-side handoff for exact three-labelled-root "
            "five-vertex flag moments on 17 immutable endpoint count witnesses."
        ),
        "input_freeze": coefficients["input_freeze"],
        "full_reconstruction": {
            name: {
                "path": f"attempts/wave47-three-root-moment/{path.name}",
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for name, path in FULL_FILES.items()
        },
        "coefficient_payload_sha256": coefficients[
            "payload_sha256_without_this_field"
        ],
        "families": {
            name: {
                key: record[key]
                for key in (
                    "root_pattern",
                    "root_pattern_binary",
                    "root_embeddings_at_n99",
                    "free_subsets_per_root_at_n99",
                    "normalization_denominator_at_n99",
                    "matrix_size",
                )
            }
            for name, record in coefficients["families"].items()
        },
        "class_streams": coefficients["class_streams"],
        "controls": controls,
        "targets": target_summaries,
        "representative_cuts": representatives,
        "full_cut_ledger": results["cut_ledger"],
        "conclusion": results["conclusion"],
        "limitations": results["limitations"],
        "memory_samples": results["memory_samples"],
    }
    handoff["payload_sha256_without_this_field"] = canonical_sha256(handoff)
    return handoff


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "compact-handoff.json")
    arguments = parser.parse_args()
    handoff = build()
    arguments.output.write_text(
        json.dumps(handoff, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "claim_label": handoff["claim_label"],
                "representative_cuts": len(handoff["representative_cuts"]),
                "full_unique_cuts": handoff["full_cut_ledger"]["unique_cut_count"],
                "all_17_refuted": handoff["conclusion"][
                    "all_17_immutable_witnesses_refuted_by_three_root_layer"
                ],
                "endpoint_n3_4158": handoff["conclusion"]["endpoint_n3_4158"],
                "payload_sha256": handoff["payload_sha256_without_this_field"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
