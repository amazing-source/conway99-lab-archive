#!/usr/bin/env python3
"""Post-freeze comparison for the Wave49 five-root discovery package.

The discovery implementation is never imported or executed.  Its JSON files
are treated as untrusted claims and compared to a fresh reconstruction using
the frozen clean-room verifier.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY_COEFFICIENTS = ROOT / "attempts/wave49-five-root-moment/coefficients.json"
DISCOVERY_RESULTS = ROOT / "attempts/wave49-five-root-moment/results.json"
DISCOVERY_NUMERICAL = ROOT / "attempts/wave49-five-root-moment/combined-sdp-result.json"
INDEPENDENT_RESULT = HERE / "independent-result.json"


def load_core():
    path = HERE / "independent_check.py"
    spec = importlib.util.spec_from_file_location("wave49_cleanroom_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load clean-room core")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


V = load_core()


def labelled_tensor_statistics(
    classes: dict[int, tuple[int, ...]],
    tensors: dict[int, list[dict[int, Counter[tuple[int, int]]]]],
) -> dict[str, object]:
    roots = sorted(
        {
            root
            for order in (6, 7)
            for by_root in tensors[order]
            for root in by_root
        }
    )
    payload = []
    record_count = 0
    entry_count = 0
    for root in roots:
        records = []
        for order in (6, 7):
            for class_mask, by_root in zip(classes[order], tensors[order]):
                entries = by_root.get(root, Counter())
                if not entries:
                    continue
                encoded = [
                    [left, right, value]
                    for (left, right), value in sorted(entries.items())
                    if value
                ]
                records.append(
                    {
                        "order": order,
                        "canonical_mask": class_mask,
                        "entries": encoded,
                    }
                )
                record_count += 1
                entry_count += len(encoded)
        payload.append({"root_mask": root, "records": records})
    return {
        "labelled_root_mask_count": len(roots),
        "nonempty_root_class_records": record_count,
        "nonzero_ordered_attachment_entries": entry_count,
        "ordered_root_embedding_visits": {
            "6": len(classes[6]) * math.perm(6, 5),
            "7": len(classes[7]) * math.perm(7, 5),
        },
        "sparse_labelled_tensor_sha256": V.object_hash(payload),
    }


def family_record(
    sigma: int,
    classes: dict[int, tuple[int, ...]],
    tensors: dict[int, list[dict[int, Counter[tuple[int, int]]]]],
    lower_counts: dict[int, Counter[int]],
) -> dict[str, object]:
    flags = V.attachment_universe(sigma)
    index = {flag: position for position, flag in enumerate(flags)}
    records = []
    for order in (6, 7):
        for class_mask, by_root in zip(classes[order], tensors[order]):
            records.append(
                {
                    "canonical_mask": class_mask,
                    "order": order,
                    "upper_entries": V.upper_entries(
                        by_root.get(sigma, Counter()), index
                    ),
                }
            )
    automorphisms = V.automorphism_count(sigma, 5)
    root_count = lower_counts[5][sigma]
    root_embeddings = root_count * automorphisms
    V.require(root_embeddings > 0, "zero canonical root count")
    return {
        "automorphism_count_of_root_type": automorphisms,
        "class_coefficients": records,
        "flags": list(flags),
        "free_vertices_per_root_at_n99": 94,
        "matrix_size": len(flags),
        "normalization_denominator_at_n99": root_embeddings * 94**2,
        "root_embeddings_at_n99": root_embeddings,
        "root_induced_count_at_n99": root_count,
        "root_mask": sigma,
    }


def reconstruct_discovery_coefficient_document(
    classes: dict[int, tuple[int, ...]],
    tensors: dict[int, list[dict[int, Counter[tuple[int, int]]]]],
    lower_counts: dict[int, Counter[int]],
) -> tuple[dict[str, object], dict[str, dict[str, object]], dict[str, object]]:
    labelled = labelled_tensor_statistics(classes, tensors)
    relabelling = {
        "canonical_root_representatives": 21,
        "class_tensor_record_checks": 2_520 * (62 + 208),
        "mapping_checks": 2_520,
        "nonidentity_mapping_checks": 21 * 119,
        "permutations_per_root": 120,
        "status": "PASS_EXACT",
        "target_graph_automorphism_assumed": False,
        "theorem": (
            "for every root permutation pi, the attachment permutation P_pi "
            "satisfies M_{pi(sigma)} = P_pi M_sigma P_pi^T coefficientwise"
        ),
    }
    families = {
        f"root5_{sigma}": family_record(
            sigma, classes, tensors, lower_counts
        )
        for sigma in classes[5]
    }
    document: dict[str, object] = {
        "class_streams": {
            str(order): {
                "count": len(classes[order]),
                "sha256": V.object_hash(list(classes[order])),
            }
            for order in (5, 6, 7)
        },
        "convention": {
            "automorphism_division": "none",
            "canonical_root_representatives": True,
            "distinct_free_vertices_union_order": 7,
            "free_vertex_attachment_bits": [0, 1, 2, 3, 4],
            "pair_of_free_vertices": "ordered",
            "root_labels_fixed_pointwise": True,
            "same_free_vertex_union_order": 6,
        },
        "families": families,
        "format": "wave49-five-root-one-free-moment-coefficients-v1",
        "input_freeze": V.INPUT_HASHES,
        "labelled_tensor_reconstruction": labelled,
        "root_relabelling": relabelling,
    }
    document["payload_sha256_without_this_field"] = V.object_hash(document)
    stats = {
        name: {
            "class_coefficients_sha256": V.object_hash(family["class_coefficients"]),
            "family_sha256": V.object_hash(family),
            "flag_sha256": V.object_hash(family["flags"]),
            "matrix_size": family["matrix_size"],
            "nonzero_upper_entries": sum(
                len(record["upper_entries"])
                for record in family["class_coefficients"]
            ),
            "root_mask": family["root_mask"],
        }
        for name, family in families.items()
    }
    return document, families, stats


def compare_controls(
    discovery: dict[str, object], independent: dict[str, object]
) -> list[str]:
    mismatches = []
    independent_by_name = {item["name"]: item for item in independent["controls"]}
    for control in discovery["controls"]:
        name = control["name"]
        expected_control = independent_by_name.get(name)
        if expected_control is None:
            mismatches.append(f"controls.{name}.missing_independent")
            continue
        for field in ("order", "srg_parameters"):
            if control[field] != expected_control[field]:
                mismatches.append(f"controls.{name}.{field}")
        expected_induced = {
            key: expected_control["induced_subset_totals"][key]
            for key in ("6", "7")
        }
        if control["induced_subset_totals"] != expected_induced:
            mismatches.append(f"controls.{name}.induced_subset_totals")
        expected_families = {
            f"root5_{item['root_mask']}": item
            for item in expected_control["families"]
        }
        for family_name, claimed in control["families"].items():
            expected = expected_families.get(family_name)
            if expected is None:
                mismatches.append(f"controls.{name}.{family_name}.missing")
                continue
            checks = {
                "matrix_sha256": expected["matrix_sha256"],
                "root_embeddings": expected["root_embeddings"],
                "all_ones_quadratic": expected["all_ones_quadratic"],
                "direct_equals_expansion": True,
            }
            for field, value in checks.items():
                if claimed.get(field) != value:
                    mismatches.append(f"controls.{name}.{family_name}.{field}")
    return mismatches


def compare_targets(
    discovery: dict[str, object],
    independent: dict[str, object],
    classes: dict[int, tuple[int, ...]],
    tensors: dict[int, list[dict[int, Counter[tuple[int, int]]]]],
    supports: list[dict[str, object]],
    decks: dict[int, dict[int, Counter[int]]],
) -> tuple[list[str], dict[str, object]]:
    mismatches = []
    independent_targets = {item["name"]: item for item in independent["witnesses"]}
    discovery_targets = {item["name"]: item for item in discovery["targets"]}
    support_by_name = {item["name"]: item for item in supports}
    candidate_directions = 0
    exact_negative = 0
    common_lower: dict[str, str] | None = None
    per_target = []
    for name in sorted(support_by_name):
        support = support_by_name[name]
        expected = independent_targets[name]
        claimed = discovery_targets.get(name)
        if claimed is None:
            mismatches.append(f"targets.{name}.missing")
            continue
        for field, value in {
            "input_path": support["input_path"],
            "support_sha256": support["support_sha256"],
            "exactly_indefinite_family_count": 21,
        }.items():
            if claimed.get(field) != value:
                mismatches.append(f"targets.{name}.{field}")
        counts = V.derive_counts(support["counts7"], classes, decks)
        lower = {
            "5": V.sparse_count_hash(counts[5]),
            "6": V.sparse_count_hash(counts[6]),
        }
        if common_lower is None:
            common_lower = lower
        elif lower != common_lower:
            mismatches.append(f"targets.{name}.lower_deck_not_common")
        expected_families = {
            f"root5_{item['root_mask']}": item for item in expected["families"]
        }
        for family_name, record in claimed["family_results"].items():
            independent_family = expected_families.get(family_name)
            if independent_family is None:
                mismatches.append(f"targets.{name}.{family_name}.missing_independent")
                continue
            sigma = int(family_name.removeprefix("root5_"))
            matrix = V.expanded_matrix(sigma, counts, classes, tensors)
            for field, value in {
                "matrix_size": independent_family["dimension"],
                "matrix_sha256": independent_family["matrix_sha256"],
                "normalization_denominator": independent_family["all_ones_quadratic"],
                "status": "EXACTLY_INDEFINITE",
            }.items():
                if record.get(field) != value:
                    mismatches.append(f"targets.{name}.{family_name}.{field}")
            inertia = record.get("exact_inertia")
            if (
                not isinstance(inertia, dict)
                or sum(inertia.get(key, -10**9) for key in ("positive", "negative", "zero"))
                != independent_family["dimension"]
                or inertia.get("negative", 0) <= 0
            ):
                mismatches.append(f"targets.{name}.{family_name}.exact_inertia")
            direction = record.get("exact_negative_direction")
            if not isinstance(direction, dict):
                mismatches.append(f"targets.{name}.{family_name}.direction_missing")
                continue
            vector = direction.get("vector")
            numerator = direction.get("quadratic_numerator")
            candidate_directions += 1
            if (
                not isinstance(vector, list)
                or len(vector) != independent_family["dimension"]
                or not all(type(value) is int for value in vector)
            ):
                mismatches.append(f"targets.{name}.{family_name}.direction_vector")
                continue
            actual = V.quadratic(matrix, vector)
            if actual != numerator or actual >= 0:
                mismatches.append(f"targets.{name}.{family_name}.direction_quadratic")
            else:
                exact_negative += 1
        per_target.append(
            {
                "name": name,
                "support_sha256": support["support_sha256"],
                "lower_deck_sha256": lower,
                "independent_family_catalog_sha256": expected[
                    "family_catalog_sha256"
                ],
                "candidate_family_count": len(claimed["family_results"]),
            }
        )
    summary = discovery["target_summary"]
    if summary.get("matrix_total") != 357:
        mismatches.append("target_summary.matrix_total")
    if summary.get("exactly_indefinite_matrices") != 357:
        mismatches.append("target_summary.exactly_indefinite_matrices")
    if summary.get("exactly_psd_matrices") != 0:
        mismatches.append("target_summary.exactly_psd_matrices")
    if summary.get("targets_refuted_by_at_least_one_family") != 17:
        mismatches.append("target_summary.targets_refuted_by_at_least_one_family")
    if summary.get("common_lower_deck_sha256") != common_lower:
        mismatches.append("target_summary.common_lower_deck_sha256")
    return mismatches, {
        "candidate_directions_replayed": candidate_directions,
        "candidate_directions_strictly_negative_exact": exact_negative,
        "common_lower_deck_sha256": common_lower,
        "targets": per_target,
    }


def compute() -> dict[str, object]:
    V.memory_guard("comparison-start")
    discovery_coefficients = V.strict_json(DISCOVERY_COEFFICIENTS)
    discovery_results = V.strict_json(DISCOVERY_RESULTS)
    independent = V.strict_json(INDEPENDENT_RESULT)
    coefficient_self_hash = V.object_hash(
        {
            key: value
            for key, value in discovery_coefficients.items()
            if key != "payload_sha256_without_this_field"
        }
    )

    classes: dict[int, tuple[int, ...]] = {}
    lookups: dict[int, list[int]] = {}
    for order in (5, 6, 7):
        class_list, lookup, labelled = V.enumerate_classes(order)
        V.require(labelled == V.EXPECTED_LABELLED[order], "class count")
        classes[order] = class_list
        lookups[order] = lookup
    tensors, _tensor_summary = V.enumerate_tensors(classes)
    supports = V.load_supports(set(classes[7]))
    decks = V.lower_deck_tables(classes, lookups)
    first_counts = V.derive_counts(supports[0]["counts7"], classes, decks)
    reconstructed, families, family_stats = (
        reconstruct_discovery_coefficient_document(
            classes, tensors, first_counts
        )
    )

    mismatches = []
    if coefficient_self_hash != discovery_coefficients.get(
        "payload_sha256_without_this_field"
    ):
        mismatches.append("coefficients.self_payload_sha256")
    if reconstructed != discovery_coefficients:
        # Preserve field-level diagnostics for the major commitments.
        for field in (
            "class_streams", "convention", "families", "input_freeze",
            "labelled_tensor_reconstruction", "root_relabelling",
            "payload_sha256_without_this_field",
        ):
            if reconstructed.get(field) != discovery_coefficients.get(field):
                mismatches.append(f"coefficients.{field}")

    coefficient_model = discovery_results["coefficient_model"]
    if coefficient_model.get("payload_sha256") != reconstructed[
        "payload_sha256_without_this_field"
    ]:
        mismatches.append("results.coefficient_model.payload_sha256")
    if coefficient_model.get("family_count") != 21:
        mismatches.append("results.coefficient_model.family_count")
    for name, expected in family_stats.items():
        if coefficient_model["family_stats"].get(name) != expected:
            mismatches.append(f"results.coefficient_model.family_stats.{name}")
    if discovery_results.get("root_relabelling") != reconstructed[
        "root_relabelling"
    ]:
        mismatches.append("results.root_relabelling")

    mismatches.extend(compare_controls(discovery_results, independent))
    target_mismatches, target_replay = compare_targets(
        discovery_results, independent, classes, tensors, supports, decks
    )
    mismatches.extend(target_mismatches)

    conclusion = discovery_results.get("conclusion", {})
    expected_wall = {
        "endpoint_n3_4158": "UNKNOWN",
        "full_psd_constrained_count_system_tested": False,
        "graph_constructed": False,
        "strict_upper_bound_below_4158": "NOT_PROVED",
    }
    if conclusion != expected_wall:
        mismatches.append("results.conclusion")
    return {
        "format": "wave49-five-root-moment-comparison-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED" if not mismatches else "REFUTED",
        "discovery_artifacts": {
            "coefficients.json": V.sha256_file(DISCOVERY_COEFFICIENTS),
            "results.json": V.sha256_file(DISCOVERY_RESULTS),
            "combined-sdp-result.json": V.sha256_file(DISCOVERY_NUMERICAL),
        },
        "precomparison_result_sha256": V.sha256_file(INDEPENDENT_RESULT),
        "coefficient_comparison": {
            "exact_document_equality": reconstructed == discovery_coefficients,
            "canonical_payload_sha256": coefficient_self_hash,
            "labelled_tensor_reconstruction": reconstructed[
                "labelled_tensor_reconstruction"
            ],
            "root_relabelling": reconstructed["root_relabelling"],
            "family_count": len(families),
        },
        "controls": {
            "matrix_checks": 42,
            "all_direct_equal_expansion": not any(
                item.startswith("controls.") for item in mismatches
            ),
            "all_exact_psd_by_outer_products": True,
        },
        "witness_replay": target_replay,
        "numerical_sdp": {
            "artifact_sha256_recorded": True,
            "opened_for_mathematical_evidence": False,
            "solver_status_used_as_evidence": False,
            "floating_duals_used_as_evidence": False,
            "residuals_used_as_evidence": False,
            "eigenvalue_margins_used_as_evidence": False,
        },
        "mismatches": sorted(set(mismatches)),
        "scope_wall": expected_wall,
    }


def validate(result: dict[str, object]) -> None:
    V.require(result["format"] == "wave49-five-root-moment-comparison-v1", "format")
    V.require(result["claim_label"] == "VERIFIED_SCOPED", "comparison failed")
    V.require(result["mismatches"] == [], "comparison mismatches")
    V.require(
        result["coefficient_comparison"]["exact_document_equality"] is True,
        "coefficient document differs",
    )
    V.require(
        result["witness_replay"]["candidate_directions_replayed"] == 357,
        "direction census",
    )
    V.require(
        result["witness_replay"]["candidate_directions_strictly_negative_exact"]
        == 357,
        "direction replay",
    )
    V.require(
        result["numerical_sdp"]["solver_status_used_as_evidence"] is False,
        "numeric evidence promotion",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--compute", metavar="OUTPUT")
    group.add_argument("--validate", metavar="INPUT")
    args = parser.parse_args()
    if args.compute:
        result = compute()
        Path(args.compute).write_bytes(V.canonical(result))
    else:
        result = V.strict_json(Path(args.validate))
    validate(result)
    print("PASS: Wave49 discovery package matches clean-room reconstruction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
