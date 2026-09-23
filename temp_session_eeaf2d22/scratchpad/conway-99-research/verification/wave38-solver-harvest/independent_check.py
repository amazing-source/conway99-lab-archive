#!/usr/bin/env python3
"""Independent fail-closed audit of the Wave 38 solver-harvest package.

The discovery builder and checker are never imported.  The exact 33-case
mapping is regenerated from the mathematical orbit definitions in the prior
independent rooted verifier.  Live-process records remain observations only:
proof coverage can increase only through artifacts checked by their required
certificate validators.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


EXPECTED_IDS = [
    15, 16, 17, 18,
    19, 20, 21, 22,
    36, 37, 38, 39, 40, 41,
    50, 51, 52, 53, 54, 55, 56, 57,
    68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78,
]
EXPECTED_PARENT_SUMMARY = {
    4: {"ids": list(range(15, 19)), "weight": 132},
    5: {"ids": list(range(19, 23)), "weight": 528},
    8: {"ids": list(range(36, 42)), "weight": 704},
    10: {"ids": list(range(50, 58)), "weight": 1056},
    12: {"ids": list(range(68, 79)), "weight": 4224},
}
CASE_ARTIFACT_KEYS = {
    "opb",
    "formula_metadata",
    "raw_proof",
    "kernel_proof",
    "solver_transcript",
    "checker_transcript",
    "terminal_result",
}
WINDOWS_RESERVED = {
    "con", "prn", "aux", "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}
SENSITIVE_PATTERNS = [
    re.compile(r"(?i)\b[A-Z]:[\\/]"),
    re.compile(r"(?i)(?:^|[\\/])Users[\\/]"),
    re.compile(r"(?i)(?:^|[\\/])home[\\/]"),
    re.compile(r"(?i)\b(?:ghp_|github_pat_|sk-[A-Za-z0-9])"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._-]+"),
    re.compile(r"(?i)\b(?:OPENAI_API_KEY|GITHUB_TOKEN)\b"),
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def attempt_root() -> Path:
    return repository_root() / "attempts/wave38-solver-harvest"


def verifier_root() -> Path:
    return Path(__file__).resolve().parent


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    answer = {}
    for key, value in pairs:
        if key in answer:
            raise ValueError(f"duplicate JSON key {key!r}")
        answer[key] = value
    return answer


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_bytes(),
        object_pairs_hook=strict_object,
        parse_constant=reject_constant,
    )
    require(isinstance(value, dict), f"{path} is not an object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=1)
def rooted():
    path = repository_root() / "verification/wave37-rooted-branches/independent_check.py"
    spec = importlib.util.spec_from_file_location(
        "wave38_frozen_independent_orbit_source", path
    )
    require(spec is not None and spec.loader is not None,
            "independent orbit source unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def independent_cases() -> tuple[dict[str, int | list[int]], ...]:
    endpoint_set = set(rooted().endpoint_edges())
    survivors = []
    for parent in range(1, 13):
        positive = {
            edge
            for edge, present in rooted().branch_decisions(parent).items()
            if present
        }
        if not positive.intersection(endpoint_set):
            survivors.append(parent)
    require(survivors == [4, 5, 8, 10, 12],
            "independent endpoint survivors changed")

    indices = rooted().label_index()
    variables = rooted().edge_variables()
    answer = []
    for identifier, (matching, endpoint, orbit_size) in enumerate(
        rooted().refined_orbits(), start=1
    ):
        parent = rooted().parent_number_for_matching(matching)
        if parent not in survivors:
            continue
        first_label = indices[(0, 2)]
        second_label = indices[tuple(sorted((4, endpoint)))]
        edge = tuple(sorted((first_label, second_label)))
        answer.append({
            "refined_branch": identifier,
            "parent_branch": parent,
            "candidate_endpoint": endpoint,
            "orbit_size": orbit_size,
            "refinement_edge": list(edge),
            "refinement_literal": variables[edge],
        })
    require([case["refined_branch"] for case in answer] == EXPECTED_IDS,
            "independent 33-case IDs changed")
    return tuple(answer)


def require_exact_keys(value: dict[str, Any], expected: set[str], name: str) -> None:
    require(set(value) == expected,
            f"{name} keys differ: {sorted(set(value) ^ expected)}")


def validate_case_path(raw: str, branch: int, artifact: str) -> str:
    require(isinstance(raw, str), "artifact path is not text")
    require("\\" not in raw and ":" not in raw, "artifact path is not canonical POSIX")
    path = PurePosixPath(raw)
    require(not path.is_absolute(), "artifact path is absolute")
    require(path.parts[:3] == ("logs", "local", "wave38-endpoint-33"),
            "artifact path escaped its owned directory")
    require(all(part not in ("", ".", "..") for part in path.parts),
            "artifact path has traversal or empty components")
    for part in path.parts:
        require(part.rstrip(" .") == part, "Windows-ambiguous path component")
        require(part.split(".")[0].casefold() not in WINDOWS_RESERVED,
                "Windows reserved path component")
    suffixes = {
        "opb": ".opb",
        "formula_metadata": ".formula.json",
        "raw_proof": ".pbp",
        "kernel_proof": ".kernel.pbp",
        "solver_transcript": ".solver.txt",
        "checker_transcript": ".checkers.txt",
        "terminal_result": ".result.json",
    }
    expected = f"logs/local/wave38-endpoint-33/case-{branch:02d}{suffixes[artifact]}"
    require(raw == expected, f"case {branch} {artifact} path changed")
    return raw.casefold()


def verify_coverage(coverage: dict[str, Any]) -> dict[str, object]:
    require_exact_keys(coverage, {
        "format", "role", "claim_label", "git_commit", "scope", "inputs",
        "normalization", "coverage_by_parent", "cases", "published_seed_formula",
        "proof_tool_lock", "atomic_case_workflow", "promotion_gate",
        "current_result_counts", "limitations",
    }, "coverage")
    require(coverage["format"] == "wave38-proof-producing-endpoint-coverage-v1",
            "wrong coverage format")
    require(coverage["role"] == "construction"
            and coverage["claim_label"] == "UNKNOWN",
            "coverage status inflated")

    submitted = coverage["cases"]
    expected = independent_cases()
    require(len(submitted) == len(expected) == 33, "case count is not 33")
    all_paths = []
    parent_weights = {}
    parent_ids = {}
    for observed, rebuilt in zip(submitted, expected):
        require_exact_keys(observed, {
            "refined_branch", "parent_branch", "candidate_endpoint", "orbit_size",
            "refinement_edge", "refinement_literal", "formula_scope",
            "planned_artifacts", "formula_status", "terminal_result_status",
            "proof_status",
        }, f"case {rebuilt['refined_branch']}")
        for key, value in rebuilt.items():
            require(observed[key] == value,
                    f"case {rebuilt['refined_branch']} {key} mismatch")
        branch = int(observed["refined_branch"])
        require(observed["terminal_result_status"] == "UNKNOWN",
                f"case {branch} terminal result promoted")
        require(observed["proof_status"] == "MISSING",
                f"case {branch} proof promoted")
        expected_formula_status = (
            "PUBLISHED_COMPRESSED_FORMULA_ONLY"
            if branch == 15 else "NOT_EXPORTED"
        )
        require(observed["formula_status"] == expected_formula_status,
                f"case {branch} formula status mismatch")
        artifacts = observed["planned_artifacts"]
        require_exact_keys(artifacts, CASE_ARTIFACT_KEYS, f"case {branch} artifacts")
        for artifact, path in artifacts.items():
            all_paths.append(validate_case_path(path, branch, artifact))
        parent = int(observed["parent_branch"])
        parent_ids.setdefault(parent, []).append(branch)
        parent_weights[parent] = parent_weights.get(parent, 0) + int(
            observed["orbit_size"]
        )
    require(len(all_paths) == 231 and len(set(all_paths)) == 231,
            "artifact paths collide under Windows case folding")
    for parent, summary in EXPECTED_PARENT_SUMMARY.items():
        require(parent_ids[parent] == summary["ids"], f"parent {parent} IDs changed")
        require(parent_weights[parent] == summary["weight"],
                f"parent {parent} orbit weight changed")
    total_weight = sum(parent_weights.values())
    require(total_weight == 6644, "endpoint-compatible orbit weight changed")

    normalization = coverage["normalization"]
    require(normalization == {
        "completed_graph_automorphism_assumed": False,
        "total_refined_orbit_count": 78,
        "total_refined_state_count": 10_395,
        "endpoint_compatible_parent_branches": [4, 5, 8, 10, 12],
        "endpoint_compatible_orbit_count": 33,
        "endpoint_compatible_state_orbit_weight": 6644,
        "endpoint_incompatible_state_orbit_weight": 3751,
    }, "normalization summary differs")
    require(coverage["current_result_counts"] == {
        "checked_unsat": 0,
        "independently_checked_endpoint_graph": 0,
        "unknown": 33,
    }, "coverage counts are inflated")

    by_parent = coverage["coverage_by_parent"]
    require(len(by_parent) == 5, "parent summary count changed")
    for record in by_parent:
        parent = record["parent_branch"]
        summary = EXPECTED_PARENT_SUMMARY[parent]
        require(record == {
            "parent_branch": parent,
            "case_count": len(summary["ids"]),
            "refined_branches": summary["ids"],
            "refined_state_orbit_weight": summary["weight"],
        }, f"parent {parent} submitted summary differs")

    seed = coverage["published_seed_formula"]
    require(seed["refined_branch"] == 15 and seed["parent_branch"] == 4,
            "published seed identity changed")
    require(seed["status"] == "CANDIDATE_FORMULA_ONLY",
            "published seed status inflated")
    for path_key, hash_key in (
        ("metadata_path", "metadata_sha256"),
        ("gzip_path", "gzip_sha256"),
    ):
        path = repository_root() / seed[path_key]
        require(path.is_file() and sha256_file(path) == seed[hash_key],
                f"published seed {path_key} hash mismatch")
    metadata = load_json(repository_root() / seed["metadata_path"])
    require(metadata["opb"]["sha256"] == seed["raw_opb_sha256"],
            "seed raw OPB hash not bound to metadata")

    for relative, expected_hash in coverage["inputs"].items():
        path = repository_root() / relative
        require(path.is_file() and sha256_file(path) == expected_hash,
                f"coverage input hash mismatch: {relative}")
    calibration_text = (
        repository_root() / coverage["proof_tool_lock"]["calibration"]
    ).read_text(encoding="utf-8")
    for key in ("Exact_sha256", "VeriPB_sha256", "CakePB_sha256"):
        require(coverage["proof_tool_lock"][key] in calibration_text,
                f"{key} is not pinned by calibration")

    return {
        "parent_case_counts": {
            str(parent): len(parent_ids[parent]) for parent in parent_ids
        },
        "parent_orbit_weights": {
            str(parent): parent_weights[parent] for parent in parent_weights
        },
        "case_count": len(submitted),
        "artifact_path_count": len(all_paths),
        "endpoint_compatible_orbit_weight": total_weight,
        "endpoint_incompatible_orbit_weight": 10_395 - total_weight,
        "case_mapping_matches_independent_orbit_reconstruction": True,
        "casefold_path_collisions": 0,
    }


def verify_snapshot(snapshot: dict[str, Any], live: dict[str, Any],
                    expected_ids: list[int]) -> dict[str, object]:
    require_exact_keys(snapshot, {
        "format", "claim_label", "git_commit", "scope", "captured_utc",
        "capture_method", "runtime", "runs", "terminal_results",
        "evidentiary_value", "limitations",
    }, "process snapshot")
    require(snapshot["format"] == "wave38-live-solver-process-snapshot-v1",
            "wrong process snapshot format")
    require(snapshot["claim_label"] == "UNKNOWN"
            and snapshot["evidentiary_value"] == "NONE",
            "process activity was promoted")
    require(snapshot["terminal_results"] == [], "snapshot has terminal results")
    require(len(snapshot["runs"]) == 2, "snapshot run count changed")
    expected_scopes = {
        "full-33-gluecard4": {
            "solver": "gluecard4",
            "parents": [4, 5, 8, 10, 12],
            "branches": expected_ids,
            "output": "attempts/wave36-rooted-branches/refined-100k.json",
        },
        "parent4-minicard": {
            "solver": "minicard",
            "parents": [4],
            "branches": [15, 16, 17, 18],
            "output": (
                "attempts/wave36-rooted-branches/"
                "refined-100k-minicard-parent4.json"
            ),
        },
    }
    for run in snapshot["runs"]:
        expected = expected_scopes[run["run_id"]]
        require(run["status"] == "LIVE_NONTERMINAL_NO_OUTPUT"
                and run["terminal_result"] is None,
                f"{run['run_id']} snapshot status inflated")
        require(not run["candidate_paths"] and not run["proof_paths"],
                f"{run['run_id']} claims result artifacts")
        configuration = run["configuration"]
        require(configuration["solver"] == expected["solver"]
                and configuration["parents"] == expected["parents"]
                and configuration["refined_branches"] == expected["branches"]
                and configuration["conflict_budget_per_case"] == 100_000,
                f"{run['run_id']} configuration mismatch")
        require(run["output"]["path"] == expected["output"]
                and run["output"]["exists_at_capture"] is False,
                f"{run['run_id']} output boundary changed")
        require(run["activity_sample"]["worker_cpu_delta_seconds"] > 0,
                f"{run['run_id']} historical activity sample is nonpositive")

    require(live["format"] == "wave38-independent-live-observation-v1"
            and live["claim_label"] == "UNKNOWN"
            and live["evidentiary_value"] == "NONE",
            "independent live observation status inflated")
    require(set(live["outputs"].values()) == {False},
            "independent live observation found a terminal output")
    require({worker["run_id"] for worker in live["workers"]}
            == set(expected_scopes), "independent worker identities changed")
    require(all(worker["command_scope_matches_snapshot"] is True
                and worker["cpu_delta_seconds"] > 0
                for worker in live["workers"]),
            "independent live sample did not confirm activity")
    return {
        "historical_run_count": len(snapshot["runs"]),
        "historical_terminal_result_count": len(snapshot["terminal_results"]),
        "independent_live_worker_count": len(live["workers"]),
        "independent_live_outputs_present": sum(live["outputs"].values()),
        "historical_snapshot_replayable": False,
        "activity_evidentiary_value": "NONE",
    }


def verify_hash_manifests() -> dict[str, object]:
    freeze_path = attempt_root() / "input-freeze.sha256"
    entries = {}
    for line in freeze_path.read_text(encoding="utf-8").splitlines():
        require(re.fullmatch(r"[0-9a-f]{64}  [^\r\n]+", line) is not None,
                "malformed discovery input-freeze line")
        digest, relative = line.split("  ", 1)
        require(relative not in entries, "duplicate discovery input-freeze path")
        entries[relative] = digest
        path = repository_root() / relative
        require(path.is_file() and sha256_file(path) == digest,
                f"discovery input-freeze mismatch: {relative}")

    report = yaml.safe_load((attempt_root() / "run-report.yaml").read_text(encoding="utf-8"))
    require(report["role"] == "construction"
            and report["claim_label"] == "UNKNOWN",
            "discovery run report status inflated")
    for section in ("inputs", "outputs"):
        for relative, digest in report[section].items():
            if relative == "tests":
                continue
            path = repository_root() / relative
            require(path.is_file() and sha256_file(path) == digest,
                    f"run-report {section} hash mismatch: {relative}")
    return {
        "discovery_input_freeze_entries": len(entries),
        "run_report_input_hashes": len(report["inputs"]),
        "run_report_output_hashes": len(report["outputs"]),
        "all_hashes_match": True,
    }


def verify_privacy(paths: list[Path]) -> dict[str, object]:
    inspected = 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for pattern in SENSITIVE_PATTERNS:
            require(pattern.search(text) is None,
                    f"privacy-sensitive pattern in {path.name}: {pattern.pattern}")
        inspected += 1
    return {
        "text_files_inspected": inspected,
        "absolute_user_paths_found": 0,
        "credential_patterns_found": 0,
        "sanitized": True,
    }


def proof_artifact_boundary(coverage: dict[str, Any],
                            snapshot: dict[str, Any]) -> dict[str, object]:
    planned = [
        repository_root() / path
        for case in coverage["cases"]
        for path in case["planned_artifacts"].values()
    ]
    existing_planned = [path for path in planned if path.exists()]
    require(not existing_planned, "a planned local artifact now exists and needs audit")
    attempt_proofs = list(attempt_root().rglob("*.pbp"))
    attempt_candidates = list(attempt_root().rglob("*.srg.json"))
    require(not attempt_proofs and not attempt_candidates,
            "Wave 38 package contains an unchecked proof or graph")
    require(snapshot["terminal_results"] == [], "snapshot terminal result exists")
    return {
        "planned_artifact_count": len(planned),
        "planned_artifacts_present": 0,
        "package_proof_files_present": 0,
        "package_candidate_graphs_present": 0,
        "independently_checked_unsat_cases": 0,
        "independently_checked_endpoint_graphs": 0,
        "proof_coverage_numerator": 0,
        "proof_coverage_denominator": 33,
    }


@lru_cache(maxsize=1)
def build_results() -> dict[str, object]:
    coverage_path = attempt_root() / "coverage-plan.json"
    snapshot_path = attempt_root() / "process-snapshot.json"
    live_path = verifier_root() / "live-observation.json"
    coverage = load_json(coverage_path)
    snapshot = load_json(snapshot_path)
    live = load_json(live_path)

    coverage_result = verify_coverage(coverage)
    snapshot_result = verify_snapshot(snapshot, live, EXPECTED_IDS)
    hash_result = verify_hash_manifests()
    boundary = proof_artifact_boundary(coverage, snapshot)
    privacy_paths = sorted(
        path for path in attempt_root().iterdir()
        if path.is_file()
    ) + [live_path]
    privacy = verify_privacy(privacy_paths)
    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED_QUEUE_AND_NULL_HARVEST_ONLY",
        "scope": "independent 33-case queue reconstruction, historical/live absence boundary, path safety, schema, hashes, privacy, and proof coverage",
        "inputs": {
            "attempts/wave38-solver-harvest/coverage-plan.json":
                sha256_file(coverage_path),
            "attempts/wave38-solver-harvest/process-snapshot.json":
                sha256_file(snapshot_path),
            "attempts/wave38-solver-harvest/input-freeze.sha256":
                sha256_file(attempt_root() / "input-freeze.sha256"),
            "attempts/wave38-solver-harvest/run-report.yaml":
                sha256_file(attempt_root() / "run-report.yaml"),
            "verification/wave37-rooted-branches/independent_check.py":
                sha256_file(
                    repository_root()
                    / "verification/wave37-rooted-branches/independent_check.py"
                ),
            "verification/wave38-solver-harvest/live-observation.json":
                sha256_file(live_path),
        },
        "coverage": coverage_result,
        "process_observability": snapshot_result,
        "hashes_and_schema": hash_result,
        "path_plan": {
            "owned_root": "logs/local/wave38-endpoint-33",
            "case_owned_artifact_count": coverage_result["artifact_path_count"],
            "casefold_collisions": coverage_result["casefold_path_collisions"],
            "traversal_or_absolute_paths": 0,
            "windows_ambiguous_paths": 0,
            "published_seed_collision": False,
        },
        "privacy": privacy,
        "proof_boundary": boundary,
        "conclusion": {
            "queue_mapping_verified": True,
            "live_solver_result_verified": False,
            "proof_coverage": "0/33",
            "endpoint_excluded": False,
            "endpoint_constructed": False,
            "upper_bound_improved_below_4158": False,
            "target_status": "UNKNOWN",
        },
        "limitations": [
            "The process snapshot is historical and its original CPU sample cannot be replayed.",
            "Current live-process activity and missing outputs reveal no completed case prefix.",
            "No proof, terminal result, assignment, or graph exists in the audited scope.",
            "Branch 15 has only a formula artifact; formula existence contributes zero proof coverage.",
            "The 33-case queue is conditional on the normalized n3=4158 endpoint setup.",
        ],
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    require(not (args.output and args.verify), "choose only one output mode")
    rendered = canonical_json(build_results())
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    elif args.verify:
        require(args.verify.read_text(encoding="utf-8") == rendered,
                "stored independent result differs")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
