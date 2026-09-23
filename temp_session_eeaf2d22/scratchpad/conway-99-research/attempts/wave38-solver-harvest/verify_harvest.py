#!/usr/bin/env python3
"""Fail-closed checker for the Wave 38 solver-harvest artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import build_coverage


ATTEMPT_ROOT = Path(__file__).resolve().parent
DEFAULT_COVERAGE = ATTEMPT_ROOT / "coverage-plan.json"
DEFAULT_SNAPSHOT = ATTEMPT_ROOT / "process-snapshot.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_bytes(),
        object_pairs_hook=build_coverage.strict_object,
        parse_constant=build_coverage.reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def canonical(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def verify_coverage(path: Path) -> dict[str, Any]:
    observed = load_json(path)
    expected = build_coverage.build()
    if canonical(observed) != canonical(expected):
        raise AssertionError("coverage plan is not the deterministic reconstruction")

    cases = observed["cases"]
    if len(cases) != 33:
        raise AssertionError("coverage must contain exactly 33 cases")
    if any(case["terminal_result_status"] != "UNKNOWN" for case in cases):
        raise AssertionError("an uncertified case was promoted")
    if any(case["proof_status"] != "MISSING" for case in cases):
        raise AssertionError("a missing proof was promoted")
    paths = [
        artifact
        for case in cases
        for artifact in case["planned_artifacts"].values()
    ]
    if len(paths) != len(set(paths)):
        raise AssertionError("case-owned artifact paths overlap")
    counts = observed["current_result_counts"]
    if counts != {
        "checked_unsat": 0,
        "independently_checked_endpoint_graph": 0,
        "unknown": 33,
    }:
        raise AssertionError("current result counts inflate the evidence")
    return observed


def verify_snapshot(path: Path, coverage: dict[str, Any]) -> dict[str, Any]:
    snapshot = load_json(path)
    if snapshot.get("format") != "wave38-live-solver-process-snapshot-v1":
        raise ValueError("wrong process-snapshot format")
    if snapshot.get("claim_label") != "UNKNOWN":
        raise AssertionError("process snapshot must remain UNKNOWN")
    if snapshot.get("evidentiary_value") != "NONE":
        raise AssertionError("live or bounded solver activity has no evidentiary value")
    if snapshot.get("terminal_results") != []:
        raise AssertionError("snapshot claims a terminal solver result")

    source = snapshot["runtime"]["source"]
    source_path = build_coverage.REPOSITORY_ROOT / source["path"]
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != source["sha256"]:
        raise AssertionError("live scout source hash mismatch")
    python = snapshot["runtime"]["python"]
    python_path = build_coverage.REPOSITORY_ROOT / python["executable_path"]
    if hashlib.sha256(python_path.read_bytes()).hexdigest() != python["executable_sha256"]:
        raise AssertionError("Python executable hash mismatch")
    pysat = snapshot["runtime"]["pysat"]
    extension_path = (
        build_coverage.REPOSITORY_ROOT / pysat["native_extension_path"]
    )
    if (
        hashlib.sha256(extension_path.read_bytes()).hexdigest()
        != pysat["native_extension_sha256"]
    ):
        raise AssertionError("PySAT native extension hash mismatch")

    runs = snapshot["runs"]
    if len(runs) != 2:
        raise AssertionError("expected exactly two observed live runs")
    by_id = {run["run_id"]: run for run in runs}
    if set(by_id) != {"full-33-gluecard4", "parent4-minicard"}:
        raise AssertionError("unexpected live-run identities")

    expected_all = [
        case["refined_branch"] for case in coverage["cases"]
    ]
    expected_parent4 = [
        case["refined_branch"]
        for case in coverage["cases"]
        if case["parent_branch"] == 4
    ]
    expected_scope = {
        "full-33-gluecard4": {
            "solver": "gluecard4",
            "parents": [4, 5, 8, 10, 12],
            "cases": expected_all,
            "output": "attempts/wave36-rooted-branches/refined-100k.json",
            "ignored": True,
        },
        "parent4-minicard": {
            "solver": "minicard",
            "parents": [4],
            "cases": expected_parent4,
            "output": (
                "attempts/wave36-rooted-branches/"
                "refined-100k-minicard-parent4.json"
            ),
            "ignored": False,
        },
    }
    for run_id, expected in expected_scope.items():
        run = by_id[run_id]
        if run["status"] != "LIVE_NONTERMINAL_NO_OUTPUT":
            raise AssertionError(f"{run_id} was promoted beyond the snapshot")
        if run["terminal_result"] is not None:
            raise AssertionError(f"{run_id} has an uncertified terminal result")
        if run["configuration"]["solver"] != expected["solver"]:
            raise AssertionError(f"{run_id} solver mismatch")
        if run["configuration"]["conflict_budget_per_case"] != 100_000:
            raise AssertionError(f"{run_id} budget mismatch")
        if run["configuration"]["parents"] != expected["parents"]:
            raise AssertionError(f"{run_id} parent scope mismatch")
        if run["configuration"]["refined_branches"] != expected["cases"]:
            raise AssertionError(f"{run_id} refined-case scope mismatch")
        output = run["output"]
        if output["path"] != expected["output"]:
            raise AssertionError(f"{run_id} output path mismatch")
        if output["exists_at_capture"] is not False:
            raise AssertionError(f"{run_id} had an output at capture")
        if output["git_ignored_at_capture"] is not expected["ignored"]:
            raise AssertionError(f"{run_id} ignore status mismatch")
        if run["activity_sample"]["worker_cpu_delta_seconds"] <= 0:
            raise AssertionError(f"{run_id} lacked positive worker activity")
        if run["candidate_paths"] or run["proof_paths"]:
            raise AssertionError(f"{run_id} claims candidate/proof artifacts")
    return snapshot


def verify(
    coverage_path: Path = DEFAULT_COVERAGE,
    snapshot_path: Path = DEFAULT_SNAPSHOT,
) -> dict[str, Any]:
    coverage = verify_coverage(coverage_path)
    snapshot = verify_snapshot(snapshot_path, coverage)
    return {
        "coverage_sha256": hashlib.sha256(coverage_path.read_bytes()).hexdigest(),
        "snapshot_sha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
        "case_count": len(coverage["cases"]),
        "live_run_count": len(snapshot["runs"]),
        "terminal_result_count": len(snapshot["terminal_results"]),
        "result": "PASS",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = verify(args.coverage, args.snapshot)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
