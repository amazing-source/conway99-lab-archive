#!/usr/bin/env python3
"""Strict discovery-side validation for the Wave 16 ``n3=51`` archive."""

from __future__ import annotations

import argparse
import copy
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

from pysat.solvers import Solver

import wave16_n3_51_active_sat as sat
import wave16_n3_51_profiles as profiles


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = (
    ROOT
    / "attempts"
    / "wave16-n3-51-computation"
    / "n3-51-profile-census.json"
)
SCAN_PATH = (
    ROOT
    / "attempts"
    / "wave16-n3-51-computation"
    / "n3-51-active-local-scan.json"
)
FAILURES_PATH = (
    ROOT
    / "attempts"
    / "wave16-n3-51-computation"
    / "n3-51-run-failures.json"
)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def exact_keys(
    value: dict[str, object],
    expected: set[str],
    context: str,
) -> None:
    observed = set(value)
    if observed != expected:
        raise AssertionError(
            f"{context} keys differ: "
            f"missing={sorted(expected-observed)}, "
            f"extra={sorted(observed-expected)}"
        )


def independent_profiles() -> tuple[tuple[int, ...], ...]:
    answers: list[tuple[int, ...]] = []

    def visit(
        remainder: int,
        lower: int,
        current: tuple[int, ...],
    ) -> None:
        if remainder == 0:
            order = len(current)
            if current and max(3 * q for q in current) <= order - 1:
                answers.append(current)
            return
        for part in range(lower, remainder + 1):
            visit(remainder - part, part, (*current, part))

    visit(34, 2, ())
    return tuple(
        sorted(answers, key=lambda row: (-len(row), row))
    )


def independent_local_state_count(
    order: int,
    root_q: Sequence[int],
) -> int:
    q_values = tuple(root_q)
    k_caps = tuple(order - 1 - 3 * value for value in q_values)
    answer = 0
    for t_values in itertools.product((1, 2, 3), repeat=3):
        if 3 + sum(t_values) > order - 3:
            continue
        u_caps = tuple(
            degree - 3 - t_value
            for degree, t_value in zip(
                k_caps,
                t_values,
                strict=True,
            )
        )
        if min(u_caps) < 0:
            continue
        for zeroes in itertools.product(
            *(range(t_value) for t_value in t_values)
        ):
            lower = tuple(
                sum(
                    3 - t_values[j] + 2 * zeroes[j]
                    for j in range(3)
                    if j != i
                )
                for i in range(3)
            )
            if any(
                lo > hi
                for lo, hi in zip(lower, u_caps, strict=True)
            ):
                continue
            full = sum(
                t_value - 1 - zero
                for t_value, zero in zip(
                    t_values,
                    zeroes,
                    strict=True,
                )
            )
            if 4 * full > 2 * sum(q_values):
                continue
            answer += 1
    return answer


def validate_profile_artifact(path: Path) -> dict[str, object]:
    report = load_json(path)
    exact_keys(
        report,
        {
            "schema",
            "claim_label",
            "target_result",
            "conditional_n3_51_exclusion",
            "novelty",
            "starting_git_commit",
            "source_manifest",
            "encoded_premises",
            "unencoded_premises",
            "method",
            "python",
            "platform",
            "semantic",
            "semantic_sha256",
        },
        "profile report",
    )
    if report["schema"] != (
        "conway99-wave16-n3-51-profile-census-v1"
    ):
        raise AssertionError("profile schema mismatch")
    if report["claim_label"] != "DERIVED_PENDING_AUDIT":
        raise AssertionError("profile claim inflation")
    for key in (
        "target_result",
        "conditional_n3_51_exclusion",
        "novelty",
    ):
        if report[key] != "UNKNOWN":
            raise AssertionError(f"profile {key} inflation")
    if report["starting_git_commit"] != profiles.STARTING_COMMIT:
        raise AssertionError("profile starting commit mismatch")
    if report["source_manifest"] != profiles.source_manifest():
        raise AssertionError("profile source manifest mismatch")
    semantic = report["semantic"]
    if report["semantic_sha256"] != profiles.sha256_bytes(
        profiles.canonical_json_bytes(semantic)
    ):
        raise AssertionError("profile semantic digest mismatch")

    enumerated = independent_profiles()
    archived = tuple(
        tuple(map(int, row["q_values"]))
        for row in semantic["raw_profiles"]
    )
    if archived != enumerated:
        raise AssertionError("independent profile enumeration mismatch")
    survivors = []
    for row in semantic["raw_profiles"]:
        q_values = tuple(map(int, row["q_values"]))
        order = len(q_values)
        degrees = tuple(
            order - 1 - 3 * value for value in q_values
        )
        if list(degrees) != row["k_degrees"]:
            raise AssertionError("profile K-degree mismatch")
        if sum(degrees) % 2:
            raise AssertionError("profile handshake failure")
        if min(degrees) >= 4:
            survivors.append(row["profile_id"])
    if survivors != list(profiles.EXPECTED_SURVIVING_PROFILES):
        raise AssertionError("independent survivor filter mismatch")

    for profile_name, details in semantic[
        "large_point_reductions"
    ].items():
        order = int(profile_name.split("-", 1)[0][1:])
        maximum_degree = int(
            details["maximum_root_k_degree_used"]
        )
        for size_key, obstruction in details[
            "size_obstructions"
        ].items():
            size = int(size_key)
            forced = 2 * size * size
            available = (
                size * maximum_degree - size * (size - 1)
            )
            if obstruction[
                "forced_external_k_incidence"
            ] != forced:
                raise AssertionError("large-point forced count changed")
            if obstruction[
                "available_external_k_incidence"
            ] != available:
                raise AssertionError("large-point capacity changed")
            if not forced > available:
                raise AssertionError("large-point contradiction lost")
        if details["remaining_point_sizes"] != [2, 3]:
            raise AssertionError("point-size reduction changed")

    observed_modes = {}
    for profile_modes in semantic[
        "local_size3_mode_census"
    ]:
        order = int(profile_modes["active_order"])
        for row in profile_modes["root_compositions"]:
            root_q = tuple(map(int, row["root_q_values"]))
            independent = independent_local_state_count(
                order,
                root_q,
            )
            if row["labeled_state_count"] != independent:
                raise AssertionError("local state count mismatch")
            observed_modes[(order, root_q)] = independent
    expected_modes = {
        (17, (2, 2, 2)): 75,
        (16, (2, 2, 2)): 32,
        (16, (2, 2, 3)): 3,
        (16, (2, 3, 3)): 1,
        (15, (2, 2, 2)): 8,
        (15, (2, 2, 3)): 0,
        (15, (2, 3, 3)): 0,
        (15, (3, 3, 3)): 0,
        (14, (2, 2, 2)): 1,
        (14, (2, 2, 3)): 0,
        (14, (2, 3, 3)): 0,
        (14, (3, 3, 3)): 0,
    }
    if observed_modes != expected_modes:
        raise AssertionError("local mode table mismatch")
    post_finite = tuple(
        (row["profile_id"], row["branch_id"])
        for row in semantic["post_finite_surviving_branches"]
    )
    if post_finite != profiles.EXPECTED_SURVIVING_BRANCHES:
        raise AssertionError("seven-branch cover mismatch")
    return {
        "status": "PASS",
        "raw_profile_count": len(archived),
        "surviving_profile_count": len(survivors),
        "post_finite_branch_count": len(post_finite),
        "semantic_sha256": report["semantic_sha256"],
        "file_sha256": profiles.file_sha256(path),
    }


def normalize_point(raw: object, order: int) -> frozenset[int]:
    if (
        not isinstance(raw, list)
        or len(raw) not in (2, 3)
        or not all(type(value) is int for value in raw)
    ):
        raise AssertionError("malformed point")
    if raw != sorted(raw) or len(set(raw)) != len(raw):
        raise AssertionError("point is not a sorted set")
    if not all(0 <= value < order for value in raw):
        raise AssertionError("point label out of range")
    return frozenset(raw)


def normalize_edge(raw: object, order: int) -> tuple[int, int]:
    if (
        not isinstance(raw, list)
        or len(raw) != 2
        or not all(type(value) is int for value in raw)
    ):
        raise AssertionError("malformed K edge")
    left, right = raw
    if not 0 <= left < right < order:
        raise AssertionError("K edge not canonical")
    return (left, right)


def recompute_diagnostics(
    q_values: Sequence[int],
    points: Sequence[frozenset[int]],
    k_edges: frozenset[tuple[int, int]],
) -> dict[str, object]:
    spec = sat.ProfileSpec(
        profile_id=profiles.profile_id(q_values),
        q_values=tuple(q_values),
        k_degrees=profiles.k_degrees(q_values),
    )
    return sat.assignment_diagnostics(spec, points, k_edges)


def validate_candidate_object(
    candidate: dict[str, object],
) -> dict[str, object]:
    exact_keys(
        candidate,
        {
            "schema",
            "claim_label",
            "target_result",
            "conditional_n3_51_exclusion",
            "novelty",
            "scope",
            "target_n3",
            "starting_git_commit",
            "source_provenance",
            "profile_id",
            "active_order",
            "q_values",
            "k_degree_targets",
            "branch",
            "variant",
            "encoded_premises",
            "unencoded_premises",
            "symmetry_boundary",
            "point_sets",
            "K_edges",
            "diagnostics",
            "semantic_core",
            "semantic_sha256",
            "formula",
        },
        "candidate",
    )
    if candidate["schema"] != (
        "conway99-wave16-n3-51-active-local-candidate-v1"
    ):
        raise AssertionError("candidate schema mismatch")
    if candidate["claim_label"] != "CANDIDATE":
        raise AssertionError("candidate claim inflation")
    for key in (
        "target_result",
        "conditional_n3_51_exclusion",
        "novelty",
    ):
        if candidate[key] != "UNKNOWN":
            raise AssertionError(f"candidate {key} inflation")
    if candidate["scope"] != "active-label auxiliary object only":
        raise AssertionError("candidate scope mismatch")
    if candidate["target_n3"] != 51:
        raise AssertionError("candidate target n3 mismatch")
    if candidate["starting_git_commit"] != profiles.STARTING_COMMIT:
        raise AssertionError("candidate starting commit mismatch")
    if candidate["source_provenance"] != sat.source_provenance():
        raise AssertionError("candidate source provenance mismatch")
    if candidate["variant"] != sat.FULL:
        raise AssertionError("candidate variant mismatch")
    if candidate["encoded_premises"] != sat.ENCODED_PREMISES:
        raise AssertionError("candidate encoded premises changed")
    if candidate["unencoded_premises"] != sat.UNENCODED_PREMISES:
        raise AssertionError("candidate unencoded premises changed")
    if candidate["symmetry_boundary"] != (
        "q labels are sorted; a positive root branch uses only "
        "permutations inside equal-q classes; no completed-graph "
        "automorphism is assumed"
    ):
        raise AssertionError("candidate symmetry boundary changed")

    q_values = tuple(map(int, candidate["q_values"]))
    order = len(q_values)
    if candidate["active_order"] != order:
        raise AssertionError("candidate order mismatch")
    if candidate["profile_id"] != profiles.profile_id(q_values):
        raise AssertionError("candidate profile id mismatch")
    if candidate["profile_id"] not in sat.profile_specs():
        raise AssertionError("candidate profile is not a survivor")
    if list(profiles.k_degrees(q_values)) != candidate[
        "k_degree_targets"
    ]:
        raise AssertionError("candidate K targets mismatch")
    points = tuple(
        normalize_point(raw, order)
        for raw in candidate["point_sets"]
    )
    if len(points) != len(set(points)):
        raise AssertionError("duplicate selected point")
    if [sorted(point) for point in points] != candidate["point_sets"]:
        raise AssertionError("point order is not canonical")
    k_edges = tuple(
        normalize_edge(raw, order)
        for raw in candidate["K_edges"]
    )
    if len(k_edges) != len(set(k_edges)):
        raise AssertionError("duplicate K edge")
    if list(k_edges) != sorted(k_edges):
        raise AssertionError("K edge order is not canonical")
    frozen_k = frozenset(k_edges)

    branch_id = str(candidate["branch"]["branch_id"])
    spec = sat.profile_specs()[str(candidate["profile_id"])]
    expected_branch = sat.branch_description(spec, branch_id)
    if candidate["branch"] != expected_branch:
        raise AssertionError("candidate branch metadata mismatch")
    if (
        candidate["profile_id"],
        branch_id,
    ) not in profiles.EXPECTED_SURVIVING_BRANCHES:
        raise AssertionError("candidate branch is outside cover")

    diagnostics = recompute_diagnostics(
        q_values,
        points,
        frozen_k,
    )
    if candidate["diagnostics"] != diagnostics:
        raise AssertionError("candidate diagnostics mismatch")
    if diagnostics["incidence_degrees"] != [3] * order:
        raise AssertionError("candidate incidence failure")
    if diagnostics["linear_pair_owner_violation_count"]:
        raise AssertionError("candidate linearity failure")
    if diagnostics["missing_point_clique_edges"]:
        raise AssertionError("candidate point clique failure")
    if diagnostics["k_degree_sequence"] != candidate[
        "k_degree_targets"
    ]:
        raise AssertionError("candidate K-degree failure")
    if diagnostics["common_point_Berge_triangle_count"]:
        raise AssertionError("candidate common-point failure")
    if diagnostics["meeting_crossing_violation_count"]:
        raise AssertionError("candidate crossing failure")
    if diagnostics["overlap_cap_violation_count"]:
        raise AssertionError("candidate overlap-cap failure")

    core = {
        "starting_git_commit": candidate["starting_git_commit"],
        "source_provenance": candidate["source_provenance"],
        "profile_id": candidate["profile_id"],
        "q_values": candidate["q_values"],
        "branch": candidate["branch"],
        "point_sets": candidate["point_sets"],
        "K_edges": candidate["K_edges"],
        "formula_materialized_dimacs_sha256": candidate[
            "formula"
        ]["materialized_dimacs_sha256"],
        "encoded_premises_sha256": candidate["formula"][
            "encoded_premises_sha256"
        ],
    }
    if candidate["semantic_core"] != core:
        raise AssertionError("candidate semantic core mismatch")
    digest = profiles.sha256_bytes(
        profiles.canonical_json_bytes(core)
    )
    if candidate["semantic_sha256"] != digest:
        raise AssertionError("candidate semantic digest mismatch")
    formula = candidate["formula"]
    if formula["builder_source_sha256"] != profiles.file_sha256(
        ROOT / formula["builder_source"]
    ):
        raise AssertionError("candidate builder hash mismatch")
    if formula["profile_source_sha256"] != profiles.file_sha256(
        ROOT / formula["profile_source"]
    ):
        raise AssertionError("candidate profile source hash mismatch")
    if formula["encoded_premises_sha256"] != (
        profiles.sha256_bytes(
            profiles.canonical_json_bytes(sat.ENCODED_PREMISES)
        )
    ):
        raise AssertionError("candidate premise digest mismatch")
    return {
        "status": "PASS",
        "profile_id": candidate["profile_id"],
        "branch_id": branch_id,
        "point_count": len(points),
        "size2_point_count": diagnostics["size2_point_count"],
        "size3_point_count": diagnostics["size3_point_count"],
        "k_edge_count": len(k_edges),
        "semantic_sha256": digest,
    }


def fixed_candidate_assumptions(
    instance: sat.Instance,
    candidate: dict[str, object],
) -> list[int]:
    chosen_points = {
        frozenset(map(int, raw))
        for raw in candidate["point_sets"]
    }
    chosen_k = {
        tuple(map(int, raw))
        for raw in candidate["K_edges"]
    }
    assumptions = list(
        sat.branch_assumptions(
            instance,
            str(candidate["branch"]["branch_id"]),
        )
    )
    assumptions.extend(
        variable if point in chosen_points else -variable
        for point, variable in instance.selected.items()
    )
    assumptions.extend(
        variable if item in chosen_k else -variable
        for item, variable in instance.k_edge.items()
    )
    return assumptions


def validate_scan(
    path: Path,
    *,
    rebuild_formulas: bool = True,
) -> dict[str, object]:
    scan = load_json(path)
    exact_keys(
        scan,
        {
            "schema",
            "claim_label",
            "target_result",
            "conditional_n3_51_exclusion",
            "novelty",
            "scope",
            "starting_git_commit",
            "source_provenance",
            "coverage_argument",
            "encoded_premises",
            "unencoded_premises",
            "negative_result_policy",
            "python",
            "python_sat",
            "platform",
            "solver_name",
            "conflict_budget_per_branch",
            "wall_timeout_seconds_per_branch",
            "results",
            "candidate_paths",
            "semantic",
            "semantic_sha256",
        },
        "scan",
    )
    if scan["schema"] != (
        "conway99-wave16-n3-51-active-local-scan-v1"
    ):
        raise AssertionError("scan schema mismatch")
    if scan["claim_label"] != "CANDIDATE":
        raise AssertionError("scan claim inflation")
    for key in (
        "target_result",
        "conditional_n3_51_exclusion",
        "novelty",
    ):
        if scan[key] != "UNKNOWN":
            raise AssertionError(f"scan {key} inflation")
    if scan["starting_git_commit"] != profiles.STARTING_COMMIT:
        raise AssertionError("scan starting commit mismatch")
    if scan["source_provenance"] != sat.source_provenance():
        raise AssertionError("scan source provenance mismatch")
    if scan["encoded_premises"] != sat.ENCODED_PREMISES:
        raise AssertionError("scan encoded premises changed")
    if scan["unencoded_premises"] != sat.UNENCODED_PREMISES:
        raise AssertionError("scan unencoded premises changed")
    if scan["negative_result_policy"] != (
        "UNSAT, budget, and timeout returns have no force "
        "without an emitted and independently checked proof trace"
    ):
        raise AssertionError("scan negative policy changed")
    semantic = scan["semantic"]
    if scan["semantic_sha256"] != profiles.sha256_bytes(
        profiles.canonical_json_bytes(semantic)
    ):
        raise AssertionError("scan semantic digest mismatch")

    expected_cover = list(profiles.surviving_branches())
    observed_cover = [
        {
            "profile_id": row["profile_id"],
            "branch_id": row["branch"]["branch_id"],
        }
        for row in scan["results"]
    ]
    if observed_cover != expected_cover:
        raise AssertionError("scan branch cover mismatch")
    if semantic["coverage"] != expected_cover:
        raise AssertionError("scan semantic cover mismatch")

    allowed = {
        "SAT_CANDIDATE",
        "UNSAT_UNVERIFIED",
        "BUDGET_UNKNOWN",
        "TIMEOUT_UNKNOWN",
    }
    validations = []
    archived_paths = []
    specs = sat.profile_specs()
    instances: dict[str, sat.Instance] = {}
    for row in scan["results"]:
        status = row["status"]
        if status not in allowed:
            raise AssertionError("scan status vocabulary changed")
        solver = row["solver"]
        if (
            solver["proof_trace_emitted"] is not False
            or solver["proof_trace_checked"] is not False
        ):
            raise AssertionError("scan forged proof-trace status")
        if status == "SAT_CANDIDATE":
            if row["evidentiary_status"] != (
                "POSITIVE_ASSIGNMENT_REQUIRES_EXACT_VALIDATION"
            ):
                raise AssertionError("positive evidentiary status changed")
            candidate_path = ROOT / row["candidate_path"]
            if profiles.file_sha256(candidate_path) != row[
                "candidate_file_sha256"
            ]:
                raise AssertionError("candidate file hash mismatch")
            candidate = load_json(candidate_path)
            validation = validate_candidate_object(candidate)
            if validation["semantic_sha256"] != row[
                "candidate_semantic_sha256"
            ]:
                raise AssertionError("candidate semantic link mismatch")
            validations.append(validation)
            archived_paths.append(row["candidate_path"])
        else:
            if row["evidentiary_status"] != (
                "NON_EVIDENTIARY_NO_CHECKED_PROOF_TRACE"
            ):
                raise AssertionError("negative evidentiary inflation")
            for key in (
                "candidate_path",
                "candidate_file_sha256",
                "candidate_semantic_sha256",
            ):
                if key in row:
                    raise AssertionError(
                        "negative row has candidate metadata"
                    )

        if rebuild_formulas:
            profile_name = str(row["profile_id"])
            if profile_name not in instances:
                instances[profile_name] = sat.build_instance(
                    specs[profile_name]
                )
            instance = instances[profile_name]
            assumptions = sat.branch_assumptions(
                instance,
                str(row["branch"]["branch_id"]),
            )
            formula = row["formula"]
            if formula["variable_count"] != instance.pool.top:
                raise AssertionError("formula variable count mismatch")
            if formula["base_clause_count"] != len(
                instance.cnf.clauses
            ):
                raise AssertionError("formula base clause mismatch")
            if formula["branch_unit_count"] != len(assumptions):
                raise AssertionError("formula branch units mismatch")
            if formula["materialized_clause_count"] != (
                len(instance.cnf.clauses) + len(assumptions)
            ):
                raise AssertionError(
                    "formula materialized clause mismatch"
                )
            if formula["materialized_dimacs_sha256"] != (
                sat.materialized_cnf_sha256(
                    instance,
                    assumptions,
                )
            ):
                raise AssertionError("formula stream digest mismatch")
            if status == "SAT_CANDIDATE":
                candidate = load_json(ROOT / row["candidate_path"])
                fixed = fixed_candidate_assumptions(
                    instance,
                    candidate,
                )
                with Solver(
                    name="glucose42",
                    bootstrap_with=instance.cnf.clauses,
                ) as solver_instance:
                    if not solver_instance.solve(assumptions=fixed):
                        raise AssertionError(
                            "candidate does not extend to formula"
                        )

    if archived_paths != scan["candidate_paths"]:
        raise AssertionError("scan candidate path list mismatch")
    projection = [
        {
            "profile_id": row["profile_id"],
            "branch_id": row["branch"]["branch_id"],
            "status": row["status"],
            "formula_sha256": row["formula"][
                "materialized_dimacs_sha256"
            ],
            "candidate_file_sha256": row.get(
                "candidate_file_sha256"
            ),
            "candidate_semantic_sha256": row.get(
                "candidate_semantic_sha256"
            ),
        }
        for row in scan["results"]
    ]
    if semantic["results"] != projection:
        raise AssertionError("scan semantic projection mismatch")
    return {
        "status": "PASS",
        "branch_count": len(scan["results"]),
        "status_histogram": dict(
            sorted(
                Counter(
                    row["status"] for row in scan["results"]
                ).items()
            )
        ),
        "validated_candidates": validations,
        "all_formula_streams_rebuilt": rebuild_formulas,
        "negative_results_evidentiary": False,
        "semantic_sha256": scan["semantic_sha256"],
        "file_sha256": profiles.file_sha256(path),
    }


def validate_run_failures(
    path: Path,
    scan_path: Path,
) -> dict[str, object]:
    archive = load_json(path)
    exact_keys(
        archive,
        {
            "schema",
            "claim_label",
            "target_result",
            "conditional_n3_51_exclusion",
            "novelty",
            "starting_git_commit",
            "final_archive",
            "historical_probe_before_final_source_freeze",
        },
        "run failures",
    )
    if archive["schema"] != (
        "conway99-wave16-n3-51-run-failures-v1"
    ):
        raise AssertionError("failure archive schema mismatch")
    if archive["claim_label"] != "CANDIDATE":
        raise AssertionError("failure archive claim inflation")
    for key in (
        "target_result",
        "conditional_n3_51_exclusion",
        "novelty",
    ):
        if archive[key] != "UNKNOWN":
            raise AssertionError(f"failure archive {key} inflation")
    if archive["starting_git_commit"] != profiles.STARTING_COMMIT:
        raise AssertionError("failure archive starting commit mismatch")

    final = archive["final_archive"]
    expected_scan_path = scan_path.relative_to(ROOT).as_posix()
    if final["active_local_scan_path"] != expected_scan_path:
        raise AssertionError("failure archive scan path mismatch")
    if final["active_local_scan_sha256"] != profiles.file_sha256(
        scan_path
    ):
        raise AssertionError("failure archive scan hash mismatch")
    scan = load_json(scan_path)
    negative_histogram = Counter(
        row["status"]
        for row in scan["results"]
        if row["status"] != "SAT_CANDIDATE"
    )
    if final["negative_status_histogram"] != dict(
        sorted(negative_histogram.items())
    ):
        raise AssertionError(
            "failure archive negative histogram mismatch"
        )

    probe = archive[
        "historical_probe_before_final_source_freeze"
    ]
    if probe["status"] != "BUDGET_UNKNOWN":
        raise AssertionError("historical probe status inflation")
    if (
        probe["proof_trace_emitted"] is not False
        or probe["proof_trace_checked"] is not False
    ):
        raise AssertionError("historical probe forged proof status")
    if probe["evidentiary_status"] != (
        "NON_EVIDENTIARY_NO_CHECKED_PROOF_TRACE"
    ):
        raise AssertionError(
            "historical probe evidentiary inflation"
        )
    matching = next(
        row
        for row in scan["results"]
        if row["profile_id"] == probe["profile_id"]
        and row["branch"]["branch_id"] == probe["branch_id"]
    )
    for key in (
        "variable_count",
        "base_clause_count",
        "branch_unit_count",
        "materialized_clause_count",
        "materialized_dimacs_sha256",
    ):
        if probe["formula"][key] != matching["formula"][key]:
            raise AssertionError(
                f"historical probe formula {key} mismatch"
            )
    return {
        "status": "PASS",
        "historical_budget_unknown_count": 1,
        "final_negative_status_histogram": dict(
            sorted(negative_histogram.items())
        ),
        "file_sha256": profiles.file_sha256(path),
    }


def mutation_checks(
    candidate: dict[str, object],
    scan: dict[str, object],
) -> dict[str, object]:
    results = {}

    def reject_candidate(
        name: str,
        mutated: dict[str, object],
    ) -> None:
        try:
            validate_candidate_object(mutated)
        except (
            AssertionError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            results[name] = str(error)
        else:
            raise AssertionError(
                f"candidate mutation {name} was accepted"
            )

    def reject_scan(
        name: str,
        mutated: dict[str, object],
    ) -> None:
        temporary = (
            ROOT
            / "attempts"
            / "wave16-n3-51-computation"
            / ".mutation-scan.json"
        )
        temporary.write_text(
            json.dumps(mutated, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        try:
            validate_scan(temporary, rebuild_formulas=False)
        except (
            AssertionError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            results[name] = str(error)
        else:
            raise AssertionError(f"scan mutation {name} was accepted")
        finally:
            temporary.unlink(missing_ok=True)

    changed = copy.deepcopy(candidate)
    changed["claim_label"] = "VERIFIED"
    reject_candidate("candidate_claim_inflation", changed)

    changed = copy.deepcopy(candidate)
    changed["target_result"] = "NONEXISTENT"
    reject_candidate("candidate_target_inflation", changed)

    changed = copy.deepcopy(candidate)
    changed["conditional_n3_51_exclusion"] = "PROVED"
    reject_candidate("candidate_conditional_inflation", changed)

    changed = copy.deepcopy(candidate)
    changed["novelty"] = "NEW"
    reject_candidate("candidate_novelty_inflation", changed)

    changed = copy.deepcopy(candidate)
    changed["scope"] = "complete Conway graph"
    reject_candidate("candidate_scope_inflation", changed)

    changed = copy.deepcopy(candidate)
    changed["point_sets"].append(
        copy.deepcopy(changed["point_sets"][0])
    )
    reject_candidate("candidate_duplicate_point", changed)

    changed = copy.deepcopy(candidate)
    changed["point_sets"].pop()
    reject_candidate("candidate_deleted_point", changed)

    changed = copy.deepcopy(candidate)
    changed["K_edges"].append(
        copy.deepcopy(changed["K_edges"][0])
    )
    reject_candidate("candidate_duplicate_K_edge", changed)

    changed = copy.deepcopy(candidate)
    changed["K_edges"].pop()
    reject_candidate("candidate_deleted_K_edge", changed)

    changed = copy.deepcopy(candidate)
    changed["q_values"][0] = 3
    reject_candidate("candidate_altered_q", changed)

    changed = copy.deepcopy(candidate)
    changed["branch"]["normalization"] = (
        "assume a completed automorphism"
    )
    reject_candidate("candidate_forged_symmetry", changed)

    changed = copy.deepcopy(candidate)
    changed["encoded_premises"].pop()
    reject_candidate("candidate_premise_deletion", changed)

    changed = copy.deepcopy(candidate)
    changed["diagnostics"]["k_edge_count"] += 1
    reject_candidate("candidate_forged_diagnostic", changed)

    changed = copy.deepcopy(candidate)
    changed["semantic_sha256"] = "0" * 64
    reject_candidate("candidate_forged_semantic_hash", changed)

    changed = copy.deepcopy(candidate)
    changed["formula"]["materialized_dimacs_sha256"] = "0" * 64
    reject_candidate("candidate_forged_formula_hash", changed)

    changed = copy.deepcopy(scan)
    changed["claim_label"] = "VERIFIED"
    reject_scan("scan_claim_inflation", changed)

    changed = copy.deepcopy(scan)
    negative = next(
        row
        for row in changed["results"]
        if row["status"] != "SAT_CANDIDATE"
    )
    negative["status"] = "PROVED_UNSAT"
    changed["semantic"]["results"][0]["status"] = "PROVED_UNSAT"
    changed["semantic_sha256"] = profiles.sha256_bytes(
        profiles.canonical_json_bytes(changed["semantic"])
    )
    reject_scan("scan_negative_promotion", changed)

    changed = copy.deepcopy(scan)
    negative = next(
        row
        for row in changed["results"]
        if row["status"] != "SAT_CANDIDATE"
    )
    negative["solver"]["proof_trace_checked"] = True
    reject_scan("scan_forged_proof_check", changed)

    changed = copy.deepcopy(scan)
    changed["results"].append(copy.deepcopy(changed["results"][0]))
    reject_scan("scan_duplicate_branch", changed)

    changed = copy.deepcopy(scan)
    positive = next(
        row
        for row in changed["results"]
        if row["status"] == "SAT_CANDIDATE"
    )
    positive["candidate_path"] = PROFILE_PATH.relative_to(
        ROOT
    ).as_posix()
    reject_scan("scan_candidate_redirection", changed)

    return {
        "status": "PASS",
        "mutation_count": len(results),
        "mutations": results,
    }


def build_validation(
    profile_path: Path,
    scan_path: Path,
    failures_path: Path,
) -> dict[str, object]:
    profile_validation = validate_profile_artifact(profile_path)
    scan_validation = validate_scan(scan_path)
    failure_validation = validate_run_failures(
        failures_path,
        scan_path,
    )
    scan = load_json(scan_path)
    candidate_path = ROOT / scan["candidate_paths"][0]
    candidate = load_json(candidate_path)
    mutations = mutation_checks(candidate, scan)
    semantic = {
        "profile_semantic_sha256": profile_validation[
            "semantic_sha256"
        ],
        "scan_semantic_sha256": scan_validation[
            "semantic_sha256"
        ],
        "candidate_semantic_sha256": [
            row["semantic_sha256"]
            for row in scan_validation["validated_candidates"]
        ],
        "formula_stream_count": scan_validation["branch_count"],
        "mutation_count": mutations["mutation_count"],
        "failure_archive_sha256": failure_validation[
            "file_sha256"
        ],
    }
    return {
        "schema": (
            "conway99-wave16-n3-51-discovery-validation-v1"
        ),
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "conditional_n3_51_exclusion": "UNKNOWN",
        "novelty": "UNKNOWN",
        "starting_git_commit": profiles.STARTING_COMMIT,
        "profile_validation": profile_validation,
        "scan_validation": scan_validation,
        "failure_validation": failure_validation,
        "mutation_validation": mutations,
        "negative_solver_results_evidentiary": False,
        "semantic": semantic,
        "semantic_sha256": profiles.sha256_bytes(
            profiles.canonical_json_bytes(semantic)
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", type=Path, default=PROFILE_PATH)
    parser.add_argument("--scan", type=Path, default=SCAN_PATH)
    parser.add_argument(
        "--failures",
        type=Path,
        default=FAILURES_PATH,
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = build_validation(
        args.profiles,
        args.scan,
        args.failures,
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(output, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
