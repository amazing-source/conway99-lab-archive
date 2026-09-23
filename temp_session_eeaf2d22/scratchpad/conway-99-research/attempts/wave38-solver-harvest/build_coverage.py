#!/usr/bin/env python3
"""Build the deterministic Wave 38 endpoint-case coverage plan.

This script does not construct a SAT/PB formula and does not invoke a solver.
It filters the independently verified 78-orbit refinement certificate by the
five parent branches that survived the endpoint-unit propagation audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ATTEMPT_ROOT = Path(__file__).resolve().parent
REFINED_CERTIFICATE = (
    REPOSITORY_ROOT / "verification" / "n3-refined-cover" / "n3-refined-cover.json"
)
ENDPOINT_REDUCTION = (
    REPOSITORY_ROOT
    / "attempts"
    / "wave35-n3-upper-triple-overlap"
    / "root-endpoint-reduction.json"
)
BRANCH15_METADATA = (
    REPOSITORY_ROOT
    / "attempts"
    / "wave37-proof-producing-endpoint"
    / "branch-15-formula.json"
)
BRANCH15_GZIP = (
    REPOSITORY_ROOT
    / "attempts"
    / "wave37-proof-producing-endpoint"
    / "branch-15.opb.gz"
)
CALIBRATION = (
    REPOSITORY_ROOT / "verification" / "2026-07-22-veripb-calibration.md"
)
PUBLIC_COMMIT = "3014f3b1c010cdde1687b8878d4ec58d2bb90f03"


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_bytes(),
        object_pairs_hook=strict_object,
        parse_constant=reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refinement_literal(candidate_endpoint: int) -> tuple[list[int], int]:
    labels = tuple(
        (left, right)
        for left, right in combinations(range(14), 2)
        if right != (left ^ 1)
    )
    label_index = {label: index for index, label in enumerate(labels)}
    edge_variable = {
        edge: variable
        for variable, edge in enumerate(combinations(range(len(labels)), 2), start=1)
    }
    first_label = label_index[(0, 2)]
    second_label = label_index[tuple(sorted((4, candidate_endpoint)))]
    edge = tuple(sorted((first_label, second_label)))
    return list(edge), edge_variable[edge]


def build() -> dict[str, Any]:
    refined = load_json(REFINED_CERTIFICATE)
    endpoint = load_json(ENDPOINT_REDUCTION)
    branch15 = load_json(BRANCH15_METADATA)

    if refined.get("format") != "n3-oriented-common-neighbor-orbits-v1":
        raise ValueError("wrong refined-cover format")
    if refined.get("orbit_count") != 78 or refined.get("state_count") != 10_395:
        raise ValueError("wrong refined-cover size")
    if endpoint.get("format") != "wave35-n3-endpoint-root-scout-v1":
        raise ValueError("wrong endpoint-reduction format")

    surviving = endpoint["endpoint"]["solver_branches"]
    if surviving != [4, 5, 8, 10, 12]:
        raise ValueError("unexpected endpoint-compatible parent branches")

    cases: list[dict[str, Any]] = []
    for raw in refined["orbits"]:
        parent = raw["first_matching_branch"]
        if parent not in surviving:
            continue
        branch = raw["branch"]
        edge, literal = refinement_literal(raw["candidate_endpoint"])
        if literal not in raw["positive_edge_literals"]:
            raise AssertionError("refinement literal missing from certified positive literals")
        stem = f"logs/local/wave38-endpoint-33/case-{branch:02d}"
        cases.append(
            {
                "refined_branch": branch,
                "parent_branch": parent,
                "candidate_endpoint": raw["candidate_endpoint"],
                "orbit_size": raw["orbit_size"],
                "refinement_edge": edge,
                "refinement_literal": literal,
                "formula_scope": (
                    "complete compact rooted SRG model plus endpoint units, "
                    "N3 normalization, this refined representative, and the "
                    "parent's six fixed-triangle prism clause families"
                ),
                "planned_artifacts": {
                    "opb": f"{stem}.opb",
                    "formula_metadata": f"{stem}.formula.json",
                    "raw_proof": f"{stem}.pbp",
                    "kernel_proof": f"{stem}.kernel.pbp",
                    "solver_transcript": f"{stem}.solver.txt",
                    "checker_transcript": f"{stem}.checkers.txt",
                    "terminal_result": f"{stem}.result.json",
                },
                "formula_status": (
                    "PUBLISHED_COMPRESSED_FORMULA_ONLY"
                    if branch == 15
                    else "NOT_EXPORTED"
                ),
                "terminal_result_status": "UNKNOWN",
                "proof_status": "MISSING",
            }
        )

    expected_ids = [
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        36,
        37,
        38,
        39,
        40,
        41,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
    ]
    if [case["refined_branch"] for case in cases] != expected_ids:
        raise AssertionError("endpoint-compatible refined-case list changed")

    by_parent: list[dict[str, Any]] = []
    for parent in surviving:
        selected = [case for case in cases if case["parent_branch"] == parent]
        by_parent.append(
            {
                "parent_branch": parent,
                "case_count": len(selected),
                "refined_branches": [
                    case["refined_branch"] for case in selected
                ],
                "refined_state_orbit_weight": sum(
                    case["orbit_size"] for case in selected
                ),
            }
        )

    payload = {
        "format": "wave38-proof-producing-endpoint-coverage-v1",
        "role": "construction",
        "claim_label": "UNKNOWN",
        "git_commit": PUBLIC_COMMIT,
        "scope": (
            "exact proof-producing work queue for all 33 endpoint-compatible "
            "refined cases, conditional on n3=4158"
        ),
        "inputs": {
            REFINED_CERTIFICATE.relative_to(REPOSITORY_ROOT).as_posix(): sha256(
                REFINED_CERTIFICATE
            ),
            ENDPOINT_REDUCTION.relative_to(REPOSITORY_ROOT).as_posix(): sha256(
                ENDPOINT_REDUCTION
            ),
            BRANCH15_METADATA.relative_to(REPOSITORY_ROOT).as_posix(): sha256(
                BRANCH15_METADATA
            ),
            BRANCH15_GZIP.relative_to(REPOSITORY_ROOT).as_posix(): sha256(
                BRANCH15_GZIP
            ),
            CALIBRATION.relative_to(REPOSITORY_ROOT).as_posix(): sha256(
                CALIBRATION
            ),
        },
        "normalization": {
            "completed_graph_automorphism_assumed": False,
            "total_refined_orbit_count": 78,
            "total_refined_state_count": 10_395,
            "endpoint_compatible_parent_branches": surviving,
            "endpoint_compatible_orbit_count": len(cases),
            "endpoint_compatible_state_orbit_weight": sum(
                case["orbit_size"] for case in cases
            ),
            "endpoint_incompatible_state_orbit_weight": (
                refined["state_count"] - sum(case["orbit_size"] for case in cases)
            ),
        },
        "coverage_by_parent": by_parent,
        "cases": cases,
        "published_seed_formula": {
            "refined_branch": branch15["refined_branch"],
            "parent_branch": branch15["parent_branch"],
            "metadata_path": BRANCH15_METADATA.relative_to(REPOSITORY_ROOT).as_posix(),
            "metadata_sha256": sha256(BRANCH15_METADATA),
            "gzip_path": BRANCH15_GZIP.relative_to(REPOSITORY_ROOT).as_posix(),
            "gzip_sha256": sha256(BRANCH15_GZIP),
            "raw_opb_sha256": branch15["opb"]["sha256"],
            "status": "CANDIDATE_FORMULA_ONLY",
        },
        "proof_tool_lock": {
            "calibration": CALIBRATION.relative_to(REPOSITORY_ROOT).as_posix(),
            "Exact_sha256": (
                "842ac70b4e938d24f537a56513ff64ea845206c714ce34da467ce146c5c5c928"
            ),
            "VeriPB_sha256": (
                "635b6f2fbd7a7fb98bf7a1f7af038355a1e58438cfdc1ee4e2649979017ace36"
            ),
            "CakePB_sha256": (
                "5920919642b1c498c2654a849fcd894ea18e7736ebf32919a9a8915861033e46"
            ),
        },
        "atomic_case_workflow": [
            "Export exactly one canonical OPB and metadata file for the case.",
            "Audit the OPB structure, hash it, and require pinned Exact --onlyparse.",
            "Run pinned Exact with --proof-assumptions=0 and a case-owned proof log.",
            "If the run stops without SAT or UNSAT, journal NO_CONCLUSION; eliminate nothing.",
            "For UNSAT, require strict raw VeriPB replay, elaboration, strict kernel replay, and CakePB VERIFIED UNSATISFIABLE.",
            "For SAT, retain and independently decode the assignment; check all SRG(99,14,1,2) axioms and global prism-freeness.",
            "Write the terminal result atomically only after every required checker succeeds.",
        ],
        "promotion_gate": {
            "endpoint_excluded_only_if": (
                "all 33 cases have independently checked UNSAT certificates"
            ),
            "endpoint_constructed_only_if": (
                "at least one SAT assignment decodes to a complete "
                "SRG(99,14,1,2) with global P=0"
            ),
            "timeouts_or_budget_stops": "ZERO_EVIDENCE",
            "partial_proof_logs": "ZERO_ENDPOINT_COVERAGE",
        },
        "current_result_counts": {
            "checked_unsat": 0,
            "independently_checked_endpoint_graph": 0,
            "unknown": 33,
        },
        "limitations": [
            "The six fixed-triangle prism clause families do not encode every prism.",
            "UNSAT of a case formula is sufficient to exclude that case because the formula contains only necessary endpoint constraints.",
            "SAT of a case formula is not sufficient for the endpoint unless the decoded graph is independently checked to be globally prism-free.",
            "No formula result, proof certificate, graph, endpoint exclusion, or improved upper bound is supplied.",
        ],
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ATTEMPT_ROOT / "coverage-plan.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build()
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(f"wrote {args.output} ({len(payload['cases'])} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
