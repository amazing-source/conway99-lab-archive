#!/usr/bin/env python3
"""Validate and seal the Wave 60 discovery checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UPSTREAM = {
    "verification/wave36-block-compatibility/independent-results.json":
        "b92ee5cde6a63ba3cce09bc2eae1518979aea09c4f5db39789b65f117b0768c4",
    "attempts/wave58-cross-incidence-rank/exact-results.json":
        "ec03c32fc72ec75222049a49b194b10bcae6bf1122ac82d9d9943e5b2f63181a",
}
ARTIFACTS = (
    "component-census.json",
    "invariant-results.json",
    "triple-0580-enumeration.json",
    "triple-0580-glucose-10k.json",
    "triple-444-local-search.json",
    "triple-444-x6-local-search.json",
    "triple-444-x12-local-search.json",
    "triple-000-x0-local-search.json",
    "triple-000-x6-local-search.json",
    "triple-000-x12-local-search.json",
)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict[str, object]:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def validate() -> dict[str, object]:
    for relative, expected in UPSTREAM.items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"upstream changed: {relative}: {actual} != {expected}"
            )
    census = load("component-census.json")
    component = census["component_census"]
    if (
        component["raw_coordinate_normalized_count"],
        component["accepted_labelled_count"],
        component["fibre_preserving_type_count"],
    ) != (216, 50, 18):
        raise AssertionError("component census changed")
    if component["accepted_labelled_C4_distribution"] != {
        "2": 6,
        "4": 30,
        "6": 14,
    }:
        raise AssertionError("C4 distribution changed")

    invariant = load("invariant-results.json")
    if invariant["triple_count"] != 1140:
        raise AssertionError("triple count changed")
    if invariant["safe_triple_orbit_reduction"]["orbit_count"] != 275:
        raise AssertionError("safe orbit count changed")
    if invariant["target_gram_rank_F2_distribution"] != {
        "14": 67,
        "16": 415,
        "18": 412,
        "20": 185,
        "22": 51,
        "24": 10,
    }:
        raise AssertionError("F2 rank distribution changed")
    if invariant["rejected_count"] != 0:
        raise AssertionError("F2 scan unexpectedly rejects a triple")
    availability = invariant["available_distinct_column_count"]
    if (
        availability["minimum"],
        availability["maximum"],
        availability["zero_candidate_triples"],
        availability["aligned_type_4_triple"],
    ) != (15936, 27200, 0, 20928):
        raise AssertionError("candidate availability summary changed")

    enumeration = load("triple-0580-enumeration.json")
    if enumeration["selected_type_triple"] != [4, 4, 4]:
        raise AssertionError("aligned triple changed")
    if enumeration["candidate_enumeration"]["candidate_count"] != 20928:
        raise AssertionError("aligned candidate count changed")
    if enumeration["candidate_enumeration"]["component_pattern_count"] != 21:
        raise AssertionError("formal pattern count changed")

    sat = load("triple-0580-glucose-10k.json")
    if sat["selection"]["status"] != "UNKNOWN":
        raise AssertionError("bounded SAT status changed")
    if sat["selection"]["proof_certificate_supplied"]:
        raise AssertionError("bounded run unexpectedly claims a proof")

    local_search = {}
    for name in ARTIFACTS[4:]:
        result = load(name)
        if result["status"] != "UNKNOWN":
            raise AssertionError(f"local search status changed: {name}")
        local_search[name] = {
            "type_triple": result["type_triple"],
            "x_AAA": result["slot_pattern_parameter_x_AAA"],
            "best_squared_error": result["best_squared_error"],
            "best_duplicate_columns": result["best_duplicate_columns"],
        }

    return {
        "format": "wave60-c3-incidence-design-checkpoint-v1",
        "claim_label": "DERIVED",
        "endpoint_status": "UNKNOWN",
        "scope": (
            "conditional kappa=3 component classification, exact invariant "
            "scan, aligned candidate enumeration, and bounded construction "
            "telemetry; no full incidence design or exclusion"
        ),
        "upstream_inputs": UPSTREAM,
        "component_classification": {
            "coordinate_normalized": 216,
            "accepted_labelled": 50,
            "fibre_preserving_types": 18,
            "labelled_C4_distribution": {"2": 6, "4": 30, "6": 14},
        },
        "triple_reduction": {
            "fibre_preserving_multisets": 1140,
            "safe_simultaneous_fibre_relabel_orbits": 275,
            "coarse_invariant_signature_groups": (
                invariant["coarse_signature_group_count"]
            ),
        },
        "F2_rank_filter": {
            "necessary_upper_bound": 30,
            "observed_distribution": (
                invariant["target_gram_rank_F2_distribution"]
            ),
            "rejected_triples": 0,
            "conclusion": "REDUNDANT",
        },
        "individual_column_support": {
            "minimum_over_triples": availability["minimum"],
            "maximum_over_triples": availability["maximum"],
            "zero_support_triples": availability["zero_candidate_triples"],
            "aligned_type_4_candidate_count": 20928,
            "formal_pattern_count": 21,
        },
        "aligned_bounded_sat": {
            "status": "UNKNOWN",
            "solver": sat["selection"]["solver"],
            "conflict_budget_observed": (
                sat["selection"]["solver_statistics"]["conflicts"]
            ),
            "candidate_variables": (
                sat["selection"]["candidate_variable_count"]
            ),
            "cnf_variables": sat["selection"]["cnf_variable_count"],
            "cnf_clauses": sat["selection"]["cnf_clause_count"],
            "proof_certificate_supplied": False,
        },
        "exact_marginal_local_search": local_search,
        "artifact_sha256": {
            name: sha256(HERE / name) for name in ARTIFACTS
        },
        "limitations": [
            "The 275 safe coordinate orbits are not exhausted.",
            "No SAT model or full 36 x 60 binary B is supplied.",
            "No UNSAT proof or exhaustive nonexistence certificate is supplied.",
            "Heuristic positive-error searches are not nonexistence evidence.",
            "No compatible Y graph or full SRG is constructed.",
            "Discovery does not verify itself.",
        ],
    }


def write_manifest(paths: list[str]) -> None:
    lines = []
    for relative in paths:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        lines.append(f"{sha256(path)}  {relative}")
    (HERE / "package-manifest.sha256").write_text(
        "\n".join(lines) + "\n", encoding="ascii", newline="\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", action="store_true")
    args = parser.parse_args()
    result = validate()
    (HERE / "exact-results.json").write_bytes(canonical_bytes(result))
    (HERE / "input-freeze.sha256").write_text(
        "\n".join(
            f"{digest}  {relative}"
            for relative, digest in UPSTREAM.items()
        )
        + "\n",
        encoding="ascii",
        newline="\n",
    )
    if args.manifest:
        write_manifest(
            [
                "agents/2026-07-27-wave60-c3-incidence-design.md",
                "attempts/wave60-c3-incidence-design/.gitattributes",
                "attempts/wave60-c3-incidence-design/README.md",
                "attempts/wave60-c3-incidence-design/constructive_search.py",
                "attempts/wave60-c3-incidence-design/exact-results.json",
                "attempts/wave60-c3-incidence-design/exact_check.py",
                "attempts/wave60-c3-incidence-design/failed-routes.md",
                "attempts/wave60-c3-incidence-design/input-freeze.sha256",
                "attempts/wave60-c3-incidence-design/invariant_scan.py",
                "attempts/wave60-c3-incidence-design/protocol.md",
                "attempts/wave60-c3-incidence-design/run-report.yaml",
                "attempts/wave60-c3-incidence-design/seal_checkpoint.py",
                "attempts/wave60-c3-incidence-design/test_exact_check.py",
                *[
                    f"attempts/wave60-c3-incidence-design/{name}"
                    for name in ARTIFACTS
                ],
            ]
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
