#!/usr/bin/env python3
"""Post-freeze clean-room comparison for the Wave 33 rooted package.

This file was added only after ``precomparison-freeze.sha256`` had been
published to the orchestrator.  It never imports or executes discovery code.
It reads frozen candidate bytes, normalizes the explicit O-Q certificate into
the precomparison checker's schema, independently reconstructs the assignment
MILP rows, and optionally reimplements the seeded hostile-object search.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

import independent_check as pre


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ATTEMPT = REPO / "attempts" / "wave33-rooted-construction"
CANDIDATE_FREEZE = (
    REPO / "verification" / "wave33-rooted-construction-candidate-freeze.sha256"
)

EXPECTED_PRECOMPARISON_MANIFEST_SHA256 = (
    "4ccbbad9c01eab764d9aa6fb207114e43f8c5a36bec3ec5bf0d161708ce0360d"
)
EXPECTED_CANDIDATE_FREEZE_SHA256 = (
    "441465c157f28e658afde31e6ca0cff49ccb5841a001150bd3e3af616c5bf63a"
)
EXPECTED_CERTIFICATE_SHA256 = (
    "340e5df716ad63bceba25c745ab04c22ea1a3dca01e939072f09775a5fc5f634"
)
EXPECTED_RESULTS_SHA256 = (
    "ba6640eacd041bc8349024a1d3f13e3d74bd67cdad64d2d78c9a94927319c496"
)

ACTIVE_PATTERN = re.compile(r"^(E|N)_(\d)_(\d)(?:_(\d))?$")
ZERO_PATTERN = re.compile(r"^Z(0|[1-9]|1[0-4])$")

RESTRICTIONS = [
    (
        "The active-to-Z triples are restricted to one explicit simple "
        "2-(15,3,2) design; this is not without loss of generality."
    ),
    "Only the active-to-Z layer is supplied; no active-active edges are supplied.",
]
LIMITATIONS = [
    "Support-group balance may fail and is measured rather than assumed.",
    "The support-active block and active-active SRG block are absent.",
    "The projector/lattice/tensor/Schur rooted endpoint layer is absent.",
    "This is not a graph-extension certificate.",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise pre.VerificationError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_candidate_json(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8")
        + b"\n"
    )


def parse_manifest(
    path: Path, base: Path, *, containment: Path | None = None
) -> dict[str, str]:
    entries: dict[str, str] = {}
    containment_resolved = (containment or base).resolve()
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, f"{path}: malformed line {line_number}")
        expected, relative = match.groups()
        require(relative not in entries, f"{path}: duplicate path {relative}")
        target = (base / relative).resolve()
        require(
            target == containment_resolved or containment_resolved in target.parents,
            f"{path}: path escapes base: {relative}",
        )
        require(target.is_file(), f"{path}: missing file: {relative}")
        actual = pre.sha256_path(target)
        require(actual == expected, f"{path}: hash mismatch: {relative}")
        entries[relative] = expected
    return entries


def verify_manifests() -> dict[str, Any]:
    pre_manifest = HERE / "precomparison-freeze.sha256"
    require(
        pre.sha256_path(pre_manifest) == EXPECTED_PRECOMPARISON_MANIFEST_SHA256,
        "precomparison manifest drift",
    )
    pre_entries = parse_manifest(pre_manifest, HERE)
    require(len(pre_entries) == 5, "precomparison manifest must have five entries")
    pre_input_entries = parse_manifest(
        HERE / "input-freeze.sha256", HERE, containment=REPO
    )
    require(
        len(pre_input_entries) == 5,
        "precomparison public-input manifest must have five entries",
    )

    require(
        pre.sha256_path(CANDIDATE_FREEZE) == EXPECTED_CANDIDATE_FREEZE_SHA256,
        "candidate freeze drift",
    )
    candidate_entries = parse_manifest(CANDIDATE_FREEZE, REPO)
    require(len(candidate_entries) == 17, "candidate freeze must have 17 entries")

    artifact_path = ATTEMPT / "artifact-manifest.sha256"
    artifact_entries = parse_manifest(artifact_path, REPO)
    require(len(artifact_entries) == 16, "artifact manifest must have 16 entries")
    expected_nested = dict(candidate_entries)
    removed = expected_nested.pop(
        "attempts/wave33-rooted-construction/artifact-manifest.sha256"
    )
    require(
        removed == pre.sha256_path(artifact_path),
        "candidate freeze does not bind artifact manifest",
    )
    require(
        artifact_entries == expected_nested,
        "candidate freeze and nested artifact manifest disagree",
    )

    input_entries = parse_manifest(ATTEMPT / "input-freeze.sha256", REPO)
    addendum_entries = parse_manifest(ATTEMPT / "input-addendum.sha256", REPO)
    require(len(input_entries) == 7, "input freeze must have seven entries")
    require(
        addendum_entries
        == {
            "verification/wave33-continuation-protocol.md":
                "b98b6bb8228b54b67cd949ee1bf6eb05ebd6ebe74f1cbc9e49b041a55e2d2fe6"
        },
        "input addendum mismatch",
    )
    return {
        "precomparison_manifest_sha256": EXPECTED_PRECOMPARISON_MANIFEST_SHA256,
        "precomparison_entry_count": len(pre_entries),
        "precomparison_input_manifest_sha256": pre.sha256_path(
            HERE / "input-freeze.sha256"
        ),
        "precomparison_input_entry_count": len(pre_input_entries),
        "candidate_freeze_sha256": EXPECTED_CANDIDATE_FREEZE_SHA256,
        "candidate_entry_count": len(candidate_entries),
        "artifact_manifest_sha256": pre.sha256_path(artifact_path),
        "artifact_entry_count": len(artifact_entries),
        "input_freeze_sha256": pre.sha256_path(ATTEMPT / "input-freeze.sha256"),
        "input_entry_count": len(input_entries),
        "input_addendum_sha256": pre.sha256_path(
            ATTEMPT / "input-addendum.sha256"
        ),
        "input_addendum_entry_count": len(addendum_entries),
        "status": "PASS",
    }


def expected_active_labels() -> list[tuple[str, int, int, int]]:
    cross = pre.canonical_cross_incidence()
    labels: list[tuple[str, int, int, int]] = []
    for positive in range(7):
        for negative in range(7):
            if cross[positive][negative]:
                labels.append((f"E_{positive}_{negative}", positive, negative, 0))
    for positive in range(7):
        for negative in range(7):
            if not cross[positive][negative]:
                for copy_index in range(2):
                    labels.append(
                        (
                            f"N_{positive}_{negative}_{copy_index}",
                            positive,
                            negative,
                            copy_index,
                        )
                    )
    require(len(labels) == 70, "internal active-label census failed")
    return labels


def parse_active_label(name: Any) -> tuple[int, int, int]:
    require(isinstance(name, str), "active label must be text")
    match = ACTIVE_PATTERN.fullmatch(name)
    require(match is not None, f"malformed active label: {name}")
    kind, raw_positive, raw_negative, raw_copy = match.groups()
    positive = int(raw_positive)
    negative = int(raw_negative)
    require(
        0 <= positive < 7 and 0 <= negative < 7,
        f"active label outside support domain: {name}",
    )
    cross = pre.canonical_cross_incidence()[positive][negative]
    if kind == "E":
        require(cross == 1 and raw_copy is None, f"invalid E label: {name}")
        copy_index = 0
    else:
        require(cross == 0 and raw_copy in ("0", "1"), f"invalid N label: {name}")
        copy_index = int(raw_copy)
    return positive, negative, copy_index


def parse_zero_label(name: Any) -> int:
    require(isinstance(name, str), "Z label must be text")
    match = ZERO_PATTERN.fullmatch(name)
    require(match is not None, f"invalid Z label: {name}")
    return int(match.group(1))


def cyclic_sts_from_bases(
    bases: Sequence[Sequence[int]],
) -> list[tuple[int, int, int]]:
    normalized = [tuple(block) for block in bases]
    require(
        normalized == [(0, 1, 4), (0, 2, 8), (0, 5, 10)],
        "first STS base list drift",
    )
    blocks = {
        tuple(sorted((point + shift) % 15 for point in base))
        for base in normalized
        for shift in range(15)
    }
    require(len(blocks) == 35, "first STS block count failed")
    pair_counts = Counter(
        pair for block in blocks for pair in itertools.combinations(block, 2)
    )
    require(
        len(pair_counts) == 105 and set(pair_counts.values()) == {1},
        "first STS pair census failed",
    )
    return sorted(blocks)


def reconstruct_fixed_design(construction: Any) -> list[tuple[int, int, int]]:
    require(isinstance(construction, dict), "design_construction must be an object")
    require(
        set(construction)
        == {"first_sts_bases_mod_15", "second_sts_point_permutation"},
        "design_construction keys drift",
    )
    first = cyclic_sts_from_bases(construction["first_sts_bases_mod_15"])
    permutation = construction["second_sts_point_permutation"]
    require(
        isinstance(permutation, list)
        and all(pre.is_exact_int(value) for value in permutation)
        and sorted(permutation) == list(range(15)),
        "second STS point permutation is invalid",
    )
    require(
        permutation == [5, 4, 0, 9, 12, 3, 13, 6, 1, 2, 14, 7, 8, 10, 11],
        "second STS point permutation drift",
    )
    second = sorted(
        tuple(sorted(permutation[point] for point in block)) for block in first
    )
    require(set(first).isdisjoint(second), "two STS copies are not disjoint")
    design = sorted(first + second)
    pre.design_metrics(design)
    return design


def parse_certificate(certificate: Any) -> dict[str, Any]:
    require(isinstance(certificate, dict), "certificate must be an object")
    require(
        set(certificate)
        == {
            "active_to_zero_triples",
            "claim_label",
            "design_construction",
            "discovery",
            "evidence_kind",
            "limitations",
            "restrictions",
            "schema_version",
            "scope",
        },
        "certificate top-level keys drift",
    )
    require(certificate["schema_version"] == 1, "certificate schema drift")
    require(certificate["claim_label"] == "CANDIDATE", "certificate claim drift")
    require(
        certificate["evidence_kind"] == "EXPLICIT_HOSTILE_PARTIAL_OBJECT",
        "certificate evidence kind drift",
    )
    require(
        certificate["scope"]
        == "LABELED_ACTIVE_TO_Z_LAYER_WITH_EXACT_DEGREES_AND_Z_ZERO_BLOCK",
        "certificate scope drift",
    )
    require(certificate["restrictions"] == RESTRICTIONS, "restriction text drift")
    require(certificate["limitations"] == LIMITATIONS, "limitation text drift")

    expected_labels = expected_active_labels()
    expected_names = [row[0] for row in expected_labels]
    records = certificate["active_to_zero_triples"]
    require(isinstance(records, list) and len(records) == 70, "record census failed")
    by_name: dict[str, tuple[int, int, int]] = {}
    for record in records:
        require(
            isinstance(record, dict) and set(record) == {"active", "zeros"},
            "malformed active-to-zero record",
        )
        name = record["active"]
        parse_active_label(name)
        require(name not in by_name, f"duplicate active label: {name}")
        raw_zeros = record["zeros"]
        require(
            isinstance(raw_zeros, list) and len(raw_zeros) == 3,
            f"invalid triple for {name}",
        )
        points = tuple(sorted(parse_zero_label(zero) for zero in raw_zeros))
        require(len(set(points)) == 3, f"repeated Z point for {name}")
        by_name[name] = points
    require(set(by_name) == set(expected_names), "active-label domain is incomplete")

    design = reconstruct_fixed_design(certificate["design_construction"])
    blocks_by_active = [by_name[name] for name in expected_names]
    require(sorted(blocks_by_active) == design, "certificate fixed-design set drift")
    return {
        "active_labels": expected_labels,
        "blocks_by_active": blocks_by_active,
        "fixed_design": design,
        "discovery": certificate["discovery"],
    }


def normalized_payload(
    parsed: dict[str, Any], bounded: dict[str, Any]
) -> dict[str, Any]:
    labels = [
        {
            "id": name,
            "positive": positive,
            "negative": negative,
            "copy": copy_index,
        }
        for name, positive, negative, copy_index in parsed["active_labels"]
    ]
    assignment_phase = bounded["reproducible_milp_run"]["assignment_phase"]
    run = bounded["reproducible_milp_run"]
    return {
        "schema_version": 1,
        "public_base_commit": pre.PUBLIC_BASE_COMMIT,
        "claim_label": "UNKNOWN",
        "global_status": {
            "Conway_99": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "rooted_endpoint": "UNKNOWN",
            "fixed_design_search": "UNKNOWN_TIMEOUT_NO_PRIMAL",
            "root_exclusion": "NOT_OBTAINED",
            "full_graph_construction": "NOT_OBTAINED",
        },
        "support_cross_incidence": pre.canonical_cross_incidence(),
        "o_labels": labels,
        "search_report": {
            "scope": pre.SEARCH_SCOPE,
            "fixed_design_count": 1,
            "o_label_count": 70,
            "block_count": 70,
            "assignment_binary_count": assignment_phase["binary_variables"],
            "o_bijection_equalities": assignment_phase[
                "vertex_assignment_equalities"
            ],
            "block_bijection_equalities": assignment_phase[
                "block_use_equalities"
            ],
            "support_point_equalities": assignment_phase[
                "support_group_point_equalities"
            ],
            "total_equalities": (
                assignment_phase["vertex_assignment_equalities"]
                + assignment_phase["block_use_equalities"]
                + assignment_phase["support_group_point_equalities"]
            ),
            "solver_family": "SciPy/HiGHS",
            "objective": "ZERO",
            "time_limit_seconds": run["time_limit_seconds_per_phase"],
            "termination": "TIME_LIMIT",
            "scipy_status": assignment_phase["solver_status"],
            "primal_found": assignment_phase["primal_point_returned"],
            "active_graph_phase_entered": run["active_graph_phase"]["entered"],
            "claimed_exclusion": False,
            "claimed_construction": False,
            "conclusion": "UNKNOWN",
        },
        "hostile_partial": {
            "status": pre.PARTIAL_STATUS,
            "o_o_layer_scope": "UNSUPPLIED_IN_CERTIFICATE_EMPTY_CONTROL_ONLY",
            "claimed_full_graph": False,
            "claimed_exclusion": False,
            "fixed_design_blocks": [
                list(block) for block in parsed["blocks_by_active"]
            ],
            "assignment": list(range(70)),
            "empty_d_control_edges": [],
            "expected": {
                "row_degree": 3,
                "column_degree": 14,
                "q_pair_intersection": 2,
                "q_pair_count": 105,
                "bf_equation_count": 210,
                "bf_violation_count": 10,
                "bf_squared_defect": 10,
                "empty_d_control_edge_count": 0,
            },
        },
    }


def direct_bf_metrics(parsed: dict[str, Any]) -> dict[str, Any]:
    raw_labels = [
        {
            "id": name,
            "positive": positive,
            "negative": negative,
            "copy": copy_index,
        }
        for name, positive, negative, copy_index in parsed["active_labels"]
    ]
    labels = pre.normalize_o_labels(raw_labels, pre.canonical_cross_incidence())
    support_o = pre.support_o_matrix(labels)
    incidence = pre.incidence_from_blocks(parsed["blocks_by_active"])
    product = pre.matrix_product(support_o, incidence)
    values = [product[support][point] for support in range(14) for point in range(15)]
    violations = [
        {
            "support": support,
            "point": point,
            "actual": product[support][point],
            "defect": product[support][point] - 2,
        }
        for support in range(14)
        for point in range(15)
        if product[support][point] != 2
    ]
    squared = sum(row["defect"] ** 2 for row in violations)
    exact_groups = sum(row == [2] * 15 for row in product)
    require(len(violations) == 10, "candidate must have exactly ten BF violations")
    require(squared == 10, "candidate BF squared defect must be ten")
    require(
        Counter(row["defect"] for row in violations) == Counter({-1: 5, 1: 5}),
        "candidate BF defect signs must be five minus and five plus",
    )
    require(exact_groups == 9, "candidate must balance exactly nine support groups")
    return {
        "equation_count": 210,
        "count_histogram": pre.histogram(values),
        "violation_count": len(violations),
        "squared_defect": squared,
        "defect_histogram": pre.histogram(row["defect"] for row in violations),
        "exact_support_group_count": exact_groups,
        "violations": violations,
        "violations_sha256": sha256_bytes(pre.canonical_json_bytes(violations)),
    }


def independent_assignment_encoding(
    parsed: dict[str, Any],
) -> dict[str, Any]:
    size = 70
    fixed_design = parsed["fixed_design"]
    support_groups: list[list[int]] = [[] for _ in range(14)]
    for vertex, (_name, positive, negative, _copy) in enumerate(
        parsed["active_labels"]
    ):
        support_groups[positive].append(vertex)
        support_groups[7 + negative].append(vertex)
    require([len(group) for group in support_groups] == [10] * 14, "group census")

    rows: list[dict[str, Any]] = []
    for vertex in range(size):
        rows.append(
            {
                "rhs": 1,
                "columns": [vertex * size + block for block in range(size)],
            }
        )
    for block in range(size):
        rows.append(
            {
                "rhs": 1,
                "columns": [vertex * size + block for vertex in range(size)],
            }
        )
    for group in support_groups:
        for point in range(15):
            rows.append(
                {
                    "rhs": 2,
                    "columns": [
                        vertex * size + block_index
                        for vertex in group
                        for block_index, block in enumerate(fixed_design)
                        if point in block
                    ],
                }
            )
    require(len(rows) == 350, "independent encoding row count failed")
    require(
        Counter(len(row["columns"]) for row in rows)
        == Counter({70: 140, 140: 210}),
        "independent encoding row-width census failed",
    )
    require(
        all(len(set(row["columns"])) == len(row["columns"]) for row in rows),
        "independent encoding contains duplicate coefficients",
    )
    return {
        "binary_variable_count": 4900,
        "bounds": "0<=x<=1",
        "integrality": "all variables integer",
        "zero_objective": True,
        "vertex_equalities": 70,
        "block_equalities": 70,
        "support_point_equalities": 210,
        "total_equalities": len(rows),
        "row_width_histogram": pre.histogram(len(row["columns"]) for row in rows),
        "nonzero_coefficient_count": sum(len(row["columns"]) for row in rows),
        "row_system_sha256": sha256_bytes(pre.canonical_json_bytes(rows)),
        "unbalanced_bijection_domain_size": str(math.factorial(70)),
        "semantics": (
            "the first 140 binary equalities encode every permutation of the "
            "one fixed 70-block design; the remaining 210 equalities impose BF=2J"
        ),
        "scope_exclusion": "no other nonisomorphic simple 2-(15,3,2) design",
    }


def verify_bounded_manifest(
    bounded: Any, encoding: dict[str, Any]
) -> dict[str, Any]:
    require(isinstance(bounded, dict), "bounded-search manifest must be an object")
    require(bounded["schema_version"] == 1, "bounded schema drift")
    require(bounded["claim_label"] == "UNKNOWN", "bounded claim must be UNKNOWN")
    require(
        bounded["base_commit"] == pre.PUBLIC_BASE_COMMIT,
        "bounded base commit mismatch",
    )
    graph_domain = bounded["complete_graph_extension_domain"]
    require(graph_domain["graph_automorphism_assumed"] is False, "automorphism gate")
    require(graph_domain["status"] == "NOT_DECIDED", "graph status gate")
    require(graph_domain["unsat_certificate"] is None, "unexpected UNSAT certificate")
    require(graph_domain["witness"] is None, "unexpected graph witness")
    require(
        graph_domain["complete_for_full_rooted_n3_708_endpoint"] is False,
        "full endpoint scope inflated",
    )

    run = bounded["reproducible_milp_run"]
    phase = run["assignment_phase"]
    require(phase["binary_variables"] == encoding["binary_variable_count"], "4900 gate")
    require(phase["vertex_assignment_equalities"] == 70, "vertex equality gate")
    require(phase["block_use_equalities"] == 70, "block equality gate")
    require(
        phase["support_group_point_equalities"] == 210,
        "support-point equality gate",
    )
    require("70!" in phase["completeness_of_encoding"], "bijection scope missing")
    require(phase["encoded_graph_automorphism"] is False, "hidden automorphism")
    require(phase["objective"] == "identically zero feasibility objective", "objective")
    require(phase["primal_point_returned"] is False, "unexpected primal")
    require(phase["solver_status"] == 1, "solver status drift")
    require(
        "Time limit reached" in phase["solver_message"]
        and "primal_status is None" in phase["solver_message"],
        "solver message drift",
    )
    for key in ("solver_objective_value", "solver_mip_node_count", "solver_mip_gap"):
        require(phase[key] is None, f"{key} must be null")
    require(run["time_limit_seconds_per_phase"] == 25, "time limit drift")
    require(run["exit_code"] == 1, "recorded exit code drift")
    require(run["output_created"] is False, "output-created gate")
    require(
        run["interpretation"] == "INCOMPLETE_NONHIT_WITH_NO_MATHEMATICAL_STATUS",
        "timeout interpretation drift",
    )
    require(run["active_graph_phase"]["entered"] is False, "active phase entered")
    require(
        run["active_graph_phase"]["reason"]
        == "phase 1 returned no primal point before its time limit",
        "active-phase reason drift",
    )
    encoded_if = run["active_graph_phase"]["encoded_if_reached"]
    require(
        encoded_if
        == {
            "active_edge_binary_variables": 2415,
            "active_degree_equalities": 70,
            "active_support_equalities": 980,
            "active_zero_equalities_with_requested_flag": 1050,
            "completeness": (
                "all active graphs for the phase-1 assignment satisfying "
                "the named linear equalities"
            ),
        },
        "unreached active-phase census drift",
    )
    require(
        not (ATTEMPT / "bounded-relaxation-certificate.json").exists(),
        "bounded output unexpectedly exists",
    )

    restrictions = bounded["restrictions_of_milp_domain"]
    require(len(restrictions) == 3, "restricted-domain list drift")
    require("one explicit simple" in restrictions[0], "one-design restriction missing")
    require("not without loss of generality" in restrictions[0], "WLOG inflation")
    require("quadratic SRG block would remain omitted" in restrictions[2], "omission")

    wall = bounded["search_status_wall"]
    require(
        wall
        == {
            "complete_domain_unsat_certificate": "NONE",
            "complete_graph_extension": "UNKNOWN",
            "full_rooted_endpoint": "UNKNOWN",
            "milp_timeout_is_negative_evidence": False,
            "n3_708": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "bounded status wall drift",
    )
    return {
        "engine": run["engine"],
        "command": run["command"],
        "time_limit_seconds": 25,
        "solver_status": 1,
        "solver_message": phase["solver_message"],
        "primal_point_returned": False,
        "objective_value": None,
        "mip_node_count": None,
        "mip_gap": None,
        "output_created": False,
        "active_graph_phase_entered": False,
        "interpretation": "UNKNOWN_NO_EVIDENCE",
        "scope": "one fixed simple design only",
    }


def verify_recorded_results(
    exact_results: Any,
    base_results: Any,
    bf: dict[str, Any],
) -> dict[str, Any]:
    require(exact_results["schema_version"] == 1, "exact result schema drift")
    require(exact_results["claim_label"] == "CANDIDATE", "exact claim drift")
    partial = exact_results["hostile_partial_object"]
    require(
        partial["classification"] == "EXACT_HOSTILE_PARTIAL_OBJECT_NOT_A_GRAPH",
        "partial classification drift",
    )
    require(
        partial["claim_label"] == "FINITE_COMPUTATIONAL_EVIDENCE",
        "partial claim-label drift",
    )
    require(partial["active_count"] == 70 and partial["zero_count"] == 15, "counts")
    require(partial["active_zero_degrees"] == {"3": 70}, "row degrees")
    require(partial["zero_degrees"] == {"14": 15}, "column degrees")
    require(partial["active_zero_edge_count"] == 210, "edge count")
    require(partial["zero_zero_pair_count"] == 105, "Q-pair count")
    require(
        partial["zero_zero_common_neighbor_histogram"] == {"2": 105},
        "Q-pair intersections",
    )
    require(
        partial["support_group_zero_count_histogram"] == bf["count_histogram"],
        "BF count histogram mismatch",
    )
    require(
        partial["support_group_balance_violation_count"] == bf["violation_count"],
        "BF violation mismatch",
    )
    require(
        partial["support_group_balance_squared_defect"] == bf["squared_defect"],
        "BF squared-defect mismatch",
    )
    require(
        partial["support_group_balance_exact_group_count"]
        == bf["exact_support_group_count"],
        "BF exact-group mismatch",
    )
    require(partial["support_group_balance_pass"] is False, "BF pass inflation")
    require(partial["restrictions"] == RESTRICTIONS, "result restrictions drift")
    require(partial["limitations"] == LIMITATIONS, "result limitations drift")

    expected_wall = {
        "Conway_99": "UNKNOWN",
        "complete_domain_UNSAT_certificate": "NONE",
        "complete_graph_extension": "UNKNOWN",
        "full_rooted_endpoint": "UNKNOWN",
        "n3_708": "UNKNOWN",
        "novelty": "UNKNOWN",
    }
    require(exact_results["status_wall"] == expected_wall, "exact status wall drift")
    require(base_results["status_wall"] == expected_wall, "base status wall drift")
    require(base_results["claim_label"] == "UNKNOWN", "base claim drift")
    require(
        exact_results["linear_consequences"] == base_results["linear_consequences"],
        "linear-consequence drift",
    )
    linear = exact_results["linear_consequences"]
    require(
        {
            "active_active_degree": linear["active_active_degree"],
            "active_zero_degree": linear["active_zero_degree"],
            "zero_degree": linear["zero_degree"],
            "zero_zero_edges": linear["zero_zero_edges"],
            "active_graph_edge_count": linear["active_graph_edge_count"],
            "active_zero_edge_count": linear["active_zero_edge_count"],
            "full_graph_edge_count": linear["full_graph_edge_count"],
        }
        == {
            "active_active_degree": 9,
            "active_zero_degree": 3,
            "zero_degree": 14,
            "zero_zero_edges": 0,
            "active_graph_edge_count": 315,
            "active_zero_edge_count": 210,
            "full_graph_edge_count": 693,
        },
        "linear consequence values drift",
    )
    return {
        "base_results_sha256": pre.sha256_path(ATTEMPT / "base-results.json"),
        "exact_results_sha256": pre.sha256_path(ATTEMPT / "exact-results.json"),
        "recorded_partial_metrics_match": True,
        "recorded_status_wall_match": True,
        "status": "PASS",
    }


def static_source_audit() -> dict[str, Any]:
    search_path = ATTEMPT / "search_relaxation.py"
    source = search_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"eval", "exec", "compile", "__import__"}
    ]
    require(not forbidden_calls, "dynamic execution found in search source")
    required_snippets = [
        "objective = np.zeros(variable_count, dtype=float)",
        "bounds = Bounds(np.zeros(variable_count), np.ones(variable_count))",
        "integrality=np.ones(variable_count, dtype=np.uint8)",
        "return vertex * size + block",
        "for vertex in range(size):",
        "for block in range(size):",
        "for support_group in model[\"support_groups\"]:",
        "rhs.append(2)",
        "if result.x is None:",
    ]
    for snippet in required_snippets:
        require(snippet in source, f"missing static encoding snippet: {snippet}")

    exact_path = ATTEMPT / "exact_check.py"
    exact_tree = ast.parse(exact_path.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(exact_tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
    require(
        imported_roots
        == {
            "__future__",
            "argparse",
            "hashlib",
            "json",
            "collections",
            "itertools",
            "pathlib",
            "typing",
        },
        "exact checker is not standard-library-only",
    )
    return {
        "search_source_sha256": pre.sha256_path(search_path),
        "assignment_encoding_inspected_lines": ["24-68", "92-139"],
        "active_phase_inspected_lines": ["142-230", "303-333"],
        "assignment_encoding_semantics": "MATCH_INDEPENDENT_ROWS",
        "solver_seed_note": (
            "the seed parameter is accepted but not passed to scipy.optimize.milp; "
            "this does not alter the frozen timeout's non-evidentiary status"
        ),
        "exact_checker_sha256": pre.sha256_path(exact_path),
        "exact_checker_imports": sorted(imported_roots),
        "exact_checker_standard_library_only": True,
        "discovery_checker_scope_metadata_gate": (
            "ABSENT_NONBLOCKING_FOR_FROZEN_BYTES; clean-room comparison checks "
            "scope, restrictions, limitations, and evidence kind exactly"
        ),
        "discovery_checker_duplicate_json_key_gate": (
            "ABSENT_NONBLOCKING_FOR_FROZEN_BYTES; clean-room strict loader passes"
        ),
    }


def verify_solver_environment_hashes() -> dict[str, Any]:
    expected = {
        ".venv/Lib/site-packages/pysat/card.py":
            "adabf7fedfe60b36cbc3c48075770e87e3cd6c5b5a013552009ce96f282a890e",
        ".venv/Lib/site-packages/pysat/solvers.py":
            "253654d8efabae650a0d136ad2f2e6d30b57206b1fb70846c714197468a28f7e",
        ".venv/Lib/site-packages/pysolvers.cp313-win_amd64.pyd":
            "1019bacdbb9400cc54fa89aa39294fefe1c63d5a67fdab35f473364529ec72dd",
        ".venv/Lib/site-packages/scipy/optimize/_milp.py":
            "803785ebcc365d1c04967a267650953da01ed285ee8be1c7a66a9fe3dbf75c3c",
        ".venv/Lib/site-packages/scipy/optimize/_highspy/_core.cp313-win_amd64.pyd":
            "92d47727b06333f871f57427a6d9800481e3e9feeabd59d31320ded8028c5357",
        ".venv/Lib/site-packages/scipy/optimize/_highspy/_highs_options.cp313-win_amd64.pyd":
            "df51a5cdf24f3ff1f06f36ef25c88b0ea41c496f8f7e12bfd40ca840f56d30a5",
    }
    observed: dict[str, str] = {}
    for relative, expected_hash in expected.items():
        path = REPO / relative
        require(path.is_file(), f"solver environment file missing: {relative}")
        actual = pre.sha256_path(path)
        require(actual == expected_hash, f"solver environment hash drift: {relative}")
        observed[relative] = actual
    return {
        "entry_count": len(observed),
        "hashes": observed,
        "status": "PASS",
        "use": "solver provenance only; no solver result is treated as a certificate",
    }


def parallel_classes(blocks: Sequence[tuple[int, int, int]]) -> list[tuple[int, ...]]:
    result: list[tuple[int, ...]] = []
    for candidate in itertools.combinations(range(35), 5):
        covered = {
            point for block_index in candidate for point in blocks[block_index]
        }
        if len(covered) == 15:
            result.append(candidate)
    require(len(result) == 56, "clean-room parallel-class census failed")
    return result


def resolutions(classes: Sequence[tuple[int, ...]]) -> list[tuple[int, ...]]:
    by_block = {block: [] for block in range(35)}
    class_sets = [set(candidate) for candidate in classes]
    for class_index, candidate in enumerate(classes):
        for block in candidate:
            by_block[block].append(class_index)
    found: list[tuple[int, ...]] = []

    def visit(unused: set[int], chosen: list[int]) -> None:
        if not unused:
            found.append(tuple(chosen))
            return
        pivot = min(
            unused,
            key=lambda block: sum(
                class_sets[index] <= unused for index in by_block[block]
            ),
        )
        for class_index in by_block[pivot]:
            candidate = class_sets[class_index]
            if candidate <= unused:
                visit(unused - candidate, chosen + [class_index])

    visit(set(range(35)), [])
    require(len(found) == 240, "clean-room resolution census failed")
    return found


def reproduce_hostile_search(parsed: dict[str, Any]) -> dict[str, Any]:
    """Independent reimplementation; does not import discovery modules."""

    first = cyclic_sts_from_bases([(0, 1, 4), (0, 2, 8), (0, 5, 10)])
    permutation = (5, 4, 0, 9, 12, 3, 13, 6, 1, 2, 14, 7, 8, 10, 11)
    second = sorted(
        tuple(sorted(permutation[point] for point in block)) for block in first
    )
    first_classes = parallel_classes(first)
    second_classes = parallel_classes(second)
    first_resolutions = resolutions(first_classes)
    second_resolutions = resolutions(second_classes)
    design = sorted(first + second)
    design_index = {block: index for index, block in enumerate(design)}

    p_groups = [[] for _ in range(7)]
    r_of_active: list[int] = []
    for vertex, (_name, positive, negative, _copy) in enumerate(
        parsed["active_labels"]
    ):
        p_groups[positive].append(vertex)
        r_of_active.append(negative)
    require([len(group) for group in p_groups] == [10] * 7, "P-group census")

    rng = random.Random(3301)
    best_energy: int | None = None
    best_assignment: list[int] | None = None
    best_restart = -1
    best_step = -1
    completed_restarts = 0
    restarts = 9
    steps = 200_000

    for restart in range(restarts):
        first_resolution = list(
            first_resolutions[rng.randrange(len(first_resolutions))]
        )
        second_resolution = list(
            second_resolutions[rng.randrange(len(second_resolutions))]
        )
        rng.shuffle(first_resolution)
        rng.shuffle(second_resolution)
        packets: list[list[int]] = []
        for positive in range(7):
            packet = [
                design_index[first[index]]
                for index in first_classes[first_resolution[positive]]
            ] + [
                design_index[second[index]]
                for index in second_classes[second_resolution[positive]]
            ]
            rng.shuffle(packet)
            packets.append(packet)

        chosen: list[int | None] = [None] * 70
        for positive in range(7):
            positions = list(p_groups[positive])
            rng.shuffle(positions)
            for vertex, block_index in zip(positions, packets[positive]):
                chosen[vertex] = block_index
        require(all(value is not None for value in chosen), "initial assignment")
        assignment = [int(value) for value in chosen if value is not None]

        counts = [[0] * 15 for _ in range(7)]
        for vertex, block_index in enumerate(assignment):
            negative = r_of_active[vertex]
            for point in design[block_index]:
                counts[negative][point] += 1
        energy = sum((count - 2) ** 2 for row in counts for count in row)
        if best_energy is None or energy < best_energy:
            best_energy = energy
            best_assignment = list(assignment)
            best_restart = restart
            best_step = -1

        for step in range(steps):
            positive = rng.randrange(7)
            left, right = rng.sample(p_groups[positive], 2)
            left_negative = r_of_active[left]
            right_negative = r_of_active[right]
            if left_negative == right_negative:
                continue
            left_block = design[assignment[left]]
            right_block = design[assignment[right]]
            old_local = sum(
                (counts[negative][point] - 2) ** 2
                for negative in (left_negative, right_negative)
                for point in range(15)
            )
            for point in left_block:
                counts[left_negative][point] -= 1
                counts[right_negative][point] += 1
            for point in right_block:
                counts[right_negative][point] -= 1
                counts[left_negative][point] += 1
            new_local = sum(
                (counts[negative][point] - 2) ** 2
                for negative in (left_negative, right_negative)
                for point in range(15)
            )
            delta = new_local - old_local
            temperature = max(0.02, 5.0 * (1.0 - step / steps))
            if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                assignment[left], assignment[right] = (
                    assignment[right],
                    assignment[left],
                )
                energy += delta
            else:
                for point in right_block:
                    counts[left_negative][point] -= 1
                    counts[right_negative][point] += 1
                for point in left_block:
                    counts[right_negative][point] -= 1
                    counts[left_negative][point] += 1
            if best_energy is None or energy < best_energy:
                best_energy = energy
                best_assignment = list(assignment)
                best_restart = restart
                best_step = step
            if energy == 0:
                completed_restarts = restart + 1
                break
        else:
            completed_restarts = restart + 1
            continue
        break

    require(best_assignment is not None and best_energy is not None, "no replay result")
    metadata = {
        "method": (
            "fixed-budget seeded annealing within P-balanced parallel-class packets"
        ),
        "seed": 3301,
        "requested_restarts": restarts,
        "completed_restarts": completed_restarts,
        "steps_per_restart": steps,
        "best_r_side_squared_defect": best_energy,
        "best_restart_zero_based": best_restart,
        "best_step_zero_based": best_step,
        "complete_search": False,
        "nonhit_has_negative_status": False,
        "status_is_certificate": False,
    }
    require(metadata == parsed["discovery"], "search metadata replay drift")
    replay_blocks = [design[index] for index in best_assignment]
    require(
        replay_blocks == parsed["blocks_by_active"],
        "clean-room search assignment differs from certificate",
    )
    expected_certificate = {
        "schema_version": 1,
        "claim_label": "CANDIDATE",
        "evidence_kind": "EXPLICIT_HOSTILE_PARTIAL_OBJECT",
        "scope": "LABELED_ACTIVE_TO_Z_LAYER_WITH_EXACT_DEGREES_AND_Z_ZERO_BLOCK",
        "active_to_zero_triples": [
            {
                "active": row[0],
                "zeros": [f"Z{point}" for point in replay_blocks[index]],
            }
            for index, row in enumerate(parsed["active_labels"])
        ],
        "design_construction": {
            "first_sts_bases_mod_15": [[0, 1, 4], [0, 2, 8], [0, 5, 10]],
            "second_sts_point_permutation": list(permutation),
        },
        "restrictions": RESTRICTIONS,
        "limitations": LIMITATIONS,
        "discovery": metadata,
    }
    encoded = canonical_candidate_json(expected_certificate)
    actual = (ATTEMPT / "partial-design-certificate.json").read_bytes()
    require(encoded == actual, "clean-room search replay is not byte-identical")
    require(sha256_bytes(encoded) == EXPECTED_CERTIFICATE_SHA256, "replay hash drift")
    return {
        "method": "independent standard-library reimplementation",
        "discovery_code_imported_or_executed": False,
        "parallel_class_count_per_STS": 56,
        "resolution_count_per_STS": 240,
        "completed_restarts": completed_restarts,
        "steps_per_restart": steps,
        "best_squared_defect": best_energy,
        "best_restart_zero_based": best_restart,
        "best_step_zero_based": best_step,
        "certificate_sha256": sha256_bytes(encoded),
        "byte_identical": True,
        "status": "PASS",
    }


def static_scope_documents() -> dict[str, Any]:
    correction = (ATTEMPT / "correction-ledger.md").read_text(encoding="utf-8")
    require(
        "complete for extending the already-forced labeled support" in correction,
        "correction ledger graph scope missing",
    )
    require(
        "finite relaxation of the full frozen rooted `n3=708` endpoint" in correction,
        "correction ledger endpoint scope missing",
    )
    require(
        "Any proper relaxation of the graph equations proves neither." in correction,
        "correction ledger relaxation wall missing",
    )
    agent_report = (
        REPO / "agents" / "2026-07-24-wave33-rooted-construction.md"
    ).read_text(encoding="utf-8")
    agent_flat = " ".join(agent_report.split())
    for phrase in (
        "No complete graph extension or UNSAT certificate is claimed.",
        "No outside orbit, stabilizer, lexicographic representative, or graph automorphism",
        "The timeout has no mathematical status.",
        "Conway-99: UNKNOWN",
    ):
        require(phrase in agent_flat, f"agent report missing status phrase: {phrase}")
    run_report = (ATTEMPT / "run-report.yaml").read_text(encoding="utf-8")
    run_flat = " ".join(run_report.split())
    for phrase in (
        "No active-active edge set is supplied.",
        "No timeout, nonhit, solver status, or hostile partial object is evidence",
        "Conway-99, and",
        "novelty all remain UNKNOWN.",
    ):
        require(phrase in run_flat, f"run report missing status phrase: {phrase}")
    return {
        "correction_ledger_sha256": pre.sha256_path(
            ATTEMPT / "correction-ledger.md"
        ),
        "correction_scope": (
            "graph equations complete for labeled SRG extension only; finite "
            "relaxation of the full rooted endpoint"
        ),
        "agent_report_sha256": pre.sha256_path(
            REPO / "agents" / "2026-07-24-wave33-rooted-construction.md"
        ),
        "run_report_sha256": pre.sha256_path(ATTEMPT / "run-report.yaml"),
        "status_language": "PASS",
    }


def compare(*, reproduce_search: bool) -> dict[str, Any]:
    manifests = verify_manifests()
    certificate_path = ATTEMPT / "partial-design-certificate.json"
    require(
        pre.sha256_path(certificate_path) == EXPECTED_CERTIFICATE_SHA256,
        "certificate hash mismatch",
    )
    certificate = pre.load_json(certificate_path)
    parsed = parse_certificate(certificate)
    bounded = pre.load_json(ATTEMPT / "bounded-search-manifest.json")
    normalized = normalized_payload(parsed, bounded)
    frozen_check = pre.verify_payload(
        normalized, input_sha256=pre.sha256_path(certificate_path)
    )
    bf = direct_bf_metrics(parsed)
    encoding = independent_assignment_encoding(parsed)
    milp = verify_bounded_manifest(bounded, encoding)
    exact_results = pre.load_json(ATTEMPT / "exact-results.json")
    base_results = pre.load_json(ATTEMPT / "base-results.json")
    require(
        pre.sha256_path(ATTEMPT / "exact-results.json") == EXPECTED_RESULTS_SHA256,
        "exact-results hash mismatch",
    )
    recorded = verify_recorded_results(exact_results, base_results, bf)
    source = static_source_audit()
    solver_environment = verify_solver_environment_hashes()
    documents = static_scope_documents()
    search_replay = (
        reproduce_hostile_search(parsed)
        if reproduce_search
        else {"status": "NOT_RUN"}
    )
    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "frozen candidate bytes, one fixed-design MILP encoding, timeout "
            "metadata, and exact hostile O-Q partial-object properties only"
        ),
        "manifests": manifests,
        "fixed_design": {
            **pre.design_metrics(parsed["fixed_design"]),
            "construction": "two block-disjoint STS(15) copies",
            "restriction": "one fixed simple design; not without loss of generality",
        },
        "assignment_encoding": encoding,
        "milp_run": milp,
        "hostile_partial": {
            "certificate_sha256": pre.sha256_path(certificate_path),
            "row_degree_histogram": {"3": 70},
            "column_degree_histogram": {"14": 15},
            "Q_pair_intersection_histogram": {"2": 105},
            "BF": bf,
            "O_O_layer_certificate_status": "UNSUPPLIED",
            "empty_D_control": frozen_check["hostile_partial"][
                "empty_D_control_full_graph_check"
            ],
            "empty_D_is_search_restriction": False,
            "classification": "EXACT_HOSTILE_PARTIAL_OBJECT_NOT_A_GRAPH",
            "claim_label": "VERIFIED_SCOPED_FACTS",
        },
        "recorded_results": recorded,
        "static_source_audit": source,
        "solver_environment": solver_environment,
        "scope_documents": documents,
        "deterministic_hostile_search_reproduction": search_replay,
        "objections": [
            (
                "The MILP ranges over one fixed simple design only; it does not "
                "cover other nonisomorphic 2-(15,3,2) designs."
            ),
            (
                "A status-1 time limit with no primal, output, or active phase "
                "is no feasibility or infeasibility evidence."
            ),
            (
                "The O-Q certificate fails ten BF=2J equations and supplies no "
                "O-O layer; the empty-D matrix is a verifier control only."
            ),
            (
                "The discovery checker does not bind prose scope metadata or "
                "reject duplicate JSON keys; frozen bytes are correctly scoped "
                "and the clean-room verifier adds those nonblocking gates."
            ),
        ],
        "status_wall": {
            "complete_graph_extension": "UNKNOWN",
            "complete_domain_UNSAT_certificate": "NONE",
            "full_rooted_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
            "timeout_negative_evidence": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reproduce-search", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = compare(reproduce_search=args.reproduce_search)
    except (OSError, pre.VerificationError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
