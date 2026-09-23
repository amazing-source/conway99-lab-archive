#!/usr/bin/env python3
"""Build the Wave 53 exact endpoint branch-coverage certificate.

The certificate freezes case definitions and separates an exhaustive branch
cover from checked UNSAT coverage.  It consumes previously verified orbit and
rooted-branch artifacts; it does not solve a target formula.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ATTEMPT_ROOT = Path(__file__).resolve().parent
JOINT_CERTIFICATE = REPOSITORY_ROOT / "verification/n3-joint-cover/n3-joint-cover.json"
REFINED_CERTIFICATE = REPOSITORY_ROOT / "verification/n3-refined-cover/n3-refined-cover.json"
ENDPOINT_REDUCTION = (
    REPOSITORY_ROOT
    / "attempts/wave35-n3-upper-triple-overlap/root-endpoint-reduction.json"
)
ROOTED_VERIFIER = (
    REPOSITORY_ROOT / "verification/wave37-rooted-branches/independent_check.py"
)
WAVE38_COVER = REPOSITORY_ROOT / "attempts/wave38-solver-harvest/coverage-plan.json"
WAVE38_CHECK = (
    REPOSITORY_ROOT / "verification/wave38-solver-harvest/independent-results.json"
)
BRANCH15_METADATA = (
    REPOSITORY_ROOT
    / "attempts/wave37-proof-producing-endpoint/branch-15-formula.json"
)
BRANCH15_GZIP = (
    REPOSITORY_ROOT / "attempts/wave37-proof-producing-endpoint/branch-15.opb.gz"
)
WAVE39_SHARD_RESULT = (
    REPOSITORY_ROOT / "verification/wave39-proof-solver/exact-results.json"
)

EXPECTED_CASE_IDS = [
    15, 16, 17, 18,
    19, 20, 21, 22,
    36, 37, 38, 39, 40, 41,
    50, 51, 52, 53, 54, 55, 56, 57,
    68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78,
]
EXPECTED_SURVIVING_PARENTS = [4, 5, 8, 10, 12]
SOURCE_COMMIT = "a4a61658356253fb95cf68252c972a4f79df38fe"


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    answer: dict[str, Any] = {}
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
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(REPOSITORY_ROOT).as_posix()


def load_rooted_verifier():
    specification = importlib.util.spec_from_file_location(
        "wave53_frozen_rooted_verifier", ROOTED_VERIFIER
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load frozen rooted verifier")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def literal_assignment(edge: tuple[int, int], value: bool, variables) -> dict[str, Any]:
    return {
        "residual_edge": list(edge),
        "literal": int(variables[edge]),
        "value": int(value),
    }


def build() -> dict[str, Any]:
    rooted = load_rooted_verifier()
    joint = load_json(JOINT_CERTIFICATE)
    refined = load_json(REFINED_CERTIFICATE)
    endpoint = load_json(ENDPOINT_REDUCTION)
    wave38_cover = load_json(WAVE38_COVER)
    wave38_check = load_json(WAVE38_CHECK)
    branch15 = load_json(BRANCH15_METADATA)
    wave39 = load_json(WAVE39_SHARD_RESULT)

    if joint["format"] != "n3-joint-fiber-matching-orbits-v1":
        raise ValueError("wrong joint-cover format")
    if refined["format"] != "n3-oriented-common-neighbor-orbits-v1":
        raise ValueError("wrong refined-cover format")
    if endpoint["format"] != "wave35-n3-endpoint-root-scout-v1":
        raise ValueError("wrong endpoint-reduction format")
    if wave38_check["conclusion"]["queue_mapping_verified"] is not True:
        raise ValueError("Wave 38 queue was not independently accepted")
    if wave38_check["conclusion"]["proof_coverage"] != "0/33":
        raise ValueError("Wave 38 proof coverage changed")
    if endpoint["endpoint"]["solver_branches"] != EXPECTED_SURVIVING_PARENTS:
        raise ValueError("endpoint-compatible parent list changed")
    if wave39["closed_shards"] != 1 or wave39["closed_endpoint_cases"] != 0:
        raise ValueError("Wave 39 shard boundary changed")

    variables = rooted.edge_variables()
    endpoint_edges = tuple(sorted(rooted.endpoint_edges()))
    endpoint_units = [
        literal_assignment(edge, False, variables) for edge in endpoint_edges
    ]
    if len(endpoint_units) != 84:
        raise AssertionError("endpoint unit count changed")

    joint_by_parent = {raw["branch"]: raw for raw in joint["branches"]}
    parent_definitions = []
    surviving_parents = []
    eliminated_parents = []
    for parent in range(1, 13):
        raw = joint_by_parent[parent]
        decisions = rooted.branch_decisions(parent)
        assignments = [
            literal_assignment(edge, value, variables)
            for edge, value in sorted(decisions.items())
        ]
        conflicting = [
            assignment
            for assignment in assignments
            if assignment["value"] == 1
            and tuple(assignment["residual_edge"]) in set(endpoint_edges)
        ]
        compatible = not conflicting
        record = {
            "parent_branch": parent,
            "matching_representative": raw["representative"],
            "matching_orbit_size": raw["orbit_size"],
            "matching_stabilizer_size": raw["stabilizer_size"],
            "parent_units": assignments,
            "endpoint_conflict_literals": conflicting,
            "endpoint_compatible": compatible,
        }
        parent_definitions.append(record)
        (surviving_parents if compatible else eliminated_parents).append(parent)
    if surviving_parents != EXPECTED_SURVIVING_PARENTS:
        raise AssertionError("independent endpoint parent filter changed")
    if eliminated_parents != [1, 2, 3, 6, 7, 9, 11]:
        raise AssertionError("independent eliminated parent list changed")

    cases = []
    all_refined = []
    for identifier, (matching, candidate, orbit_size) in enumerate(
        rooted.refined_orbits(), start=1
    ):
        parent = rooted.parent_number_for_matching(matching)
        indices = rooted.label_index()
        first = indices[(0, 2)]
        second = indices[tuple(sorted((4, candidate)))]
        refinement_edge = tuple(sorted((first, second)))
        raw = {
            "refined_branch": identifier,
            "parent_branch": parent,
            "candidate_endpoint": candidate,
            "state_orbit_size": orbit_size,
            "matching_representative": [list(edge) for edge in matching],
            "refinement_unit": literal_assignment(
                refinement_edge, True, variables
            ),
            "endpoint_compatible": parent in surviving_parents,
        }
        all_refined.append(raw)
        if parent in surviving_parents:
            raw["complete_case_status"] = "UNKNOWN"
            raw["checked_unsat_certificate"] = None
            cases.append(raw)

    if [case["refined_branch"] for case in cases] != EXPECTED_CASE_IDS:
        raise AssertionError("33-case identifier list changed")
    if len(all_refined) != 78 or sum(x["state_orbit_size"] for x in all_refined) != 10_395:
        raise AssertionError("full refined cover size changed")
    if sum(case["state_orbit_size"] for case in cases) != 6_644:
        raise AssertionError("endpoint-compatible orbit weight changed")
    incompatible = [case for case in all_refined if not case["endpoint_compatible"]]
    if len(incompatible) != 45 or sum(x["state_orbit_size"] for x in incompatible) != 3_751:
        raise AssertionError("endpoint-incompatible orbit weight changed")

    prior_cases = wave38_cover["cases"]
    if [case["refined_branch"] for case in prior_cases] != EXPECTED_CASE_IDS:
        raise AssertionError("Wave 38 queue differs")
    for frozen, prior in zip(cases, prior_cases):
        for new_key, old_key in (
            ("refined_branch", "refined_branch"),
            ("parent_branch", "parent_branch"),
            ("candidate_endpoint", "candidate_endpoint"),
            ("state_orbit_size", "orbit_size"),
        ):
            if frozen[new_key] != prior[old_key]:
                raise AssertionError(f"Wave 38 case mismatch at {frozen['refined_branch']}")
        if frozen["refinement_unit"]["literal"] != prior["refinement_literal"]:
            raise AssertionError("Wave 38 refinement literal differs")

    frozen_inputs = [
        JOINT_CERTIFICATE,
        REFINED_CERTIFICATE,
        ENDPOINT_REDUCTION,
        ROOTED_VERIFIER,
        WAVE38_COVER,
        WAVE38_CHECK,
        BRANCH15_METADATA,
        BRANCH15_GZIP,
        WAVE39_SHARD_RESULT,
    ]
    return {
        "format": "wave53-endpoint-proof-cover-v1",
        "role": "proof_a",
        "claim_label": "DERIVED",
        "git_commit": SOURCE_COMMIT,
        "scope": (
            "exact normalized 33-case cover conditional on the n3=4158 "
            "prism-free endpoint; branch coverage only, not case UNSAT"
        ),
        "inputs": {relative(path): sha256_file(path) for path in frozen_inputs},
        "endpoint_assumptions": {
            "graph_parameters": [99, 14, 1, 2],
            "n3": 4158,
            "prism_count": 0,
            "normalization": (
                "one N3 occurrence is fixed in the audited seven-pair rooted "
                "coordinate system"
            ),
            "completed_graph_automorphism_assumed": False,
            "endpoint_nonedge_units": endpoint_units,
        },
        "parent_definitions": parent_definitions,
        "case_definitions": cases,
        "coverage": {
            "normalized_state_count": 10_395,
            "all_refined_orbit_count": 78,
            "endpoint_incompatible_parent_branches": eliminated_parents,
            "endpoint_incompatible_refined_orbit_count": 45,
            "endpoint_incompatible_state_orbit_weight": 3_751,
            "endpoint_compatible_parent_branches": surviving_parents,
            "endpoint_compatible_refined_orbit_count": 33,
            "endpoint_compatible_state_orbit_weight": 6_644,
            "case_ids": EXPECTED_CASE_IDS,
            "branch_cover_exhaustive_under_endpoint_assumptions": True,
        },
        "proof_status": {
            "complete_cases_checked_unsat": 0,
            "complete_cases_total": 33,
            "complete_case_proof_coverage": "0/33",
            "verified_partial_shards": [
                {
                    "refined_branch": 15,
                    "assumption": "x187=1",
                    "result": "VERIFIED_UNSAT",
                    "complete_case_closed": False,
                    "source": relative(WAVE39_SHARD_RESULT),
                    "source_sha256": sha256_file(WAVE39_SHARD_RESULT),
                }
            ],
            "next_open_shard": {
                "refined_branch": 15,
                "assumption": "x187=0",
                "reason": (
                    "the complementary polarity is the exact remainder of the "
                    "only exported endpoint case"
                ),
                "status": "UNKNOWN",
            },
            "endpoint_excluded": False,
            "endpoint_status": "UNKNOWN",
        },
        "smallest_missing_ingredient": {
            "statement": (
                "A checked terminal certificate is missing for every complete "
                "case; the smallest ready target is branch15 AND x187=0."
            ),
            "why_not_a_coverage_gap": (
                "The 33 case definitions exhaust all 6,644 endpoint-compatible "
                "normalized states; zero of those complete cases is closed."
            ),
            "promotion_gate": (
                "Exclude n3=4158 only after all 33 complete cases have "
                "independently replayed UNSAT certificates, or accept a "
                "decoded full SRG only after an exhaustive zero-prism check."
            ),
        },
        "limitations": [
            "The n3=4158 endpoint and its normalization are upstream conditional inputs.",
            "Branch exhaustiveness is not satisfiability or nonexistence.",
            "The one verified branch-15 polarity shard closes no complete case.",
            "No endpoint exclusion, improved upper bound, graph, or novelty claim follows.",
        ],
    }


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ATTEMPT_ROOT / "coverage-certificate.json",
    )
    arguments = parser.parse_args()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_bytes(canonical_json(build()))
    print(f"wrote {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
