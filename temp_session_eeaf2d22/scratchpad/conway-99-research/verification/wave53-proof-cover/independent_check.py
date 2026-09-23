#!/usr/bin/env python3
"""Independent verifier for the Wave 53 endpoint proof-cover package.

This file imports no Wave 53 discovery implementation.  It reconstructs the
local scaffold stabilizers, matching/refinement orbits, SAT variable order,
endpoint filter, and branch units directly from their finite definitions.
It also checks the branch-15 shard byte-for-byte and can run fresh bounded
Exact, VeriPB, and CakePB checks while enforcing a physical-memory reserve.
"""

from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import itertools
import json
import os
import re
import subprocess
import tempfile
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[2]
VERIFY_ROOT = Path(__file__).resolve().parent
DISCOVERY_ROOT = ROOT / "attempts/wave53-proof-cover"

JOINT = ROOT / "verification/n3-joint-cover/n3-joint-cover.json"
REFINED = ROOT / "verification/n3-refined-cover/n3-refined-cover.json"
ENDPOINT = ROOT / "attempts/wave35-n3-upper-triple-overlap/root-endpoint-reduction.json"
PRIOR_ROOTED_CHECKER = ROOT / "verification/wave37-rooted-branches/independent_check.py"
WAVE38_PLAN = ROOT / "attempts/wave38-solver-harvest/coverage-plan.json"
WAVE38_RESULTS = ROOT / "verification/wave38-solver-harvest/independent-results.json"
SOURCE_METADATA = ROOT / "attempts/wave37-proof-producing-endpoint/branch-15-formula.json"
SOURCE_GZIP = ROOT / "attempts/wave37-proof-producing-endpoint/branch-15.opb.gz"
WAVE39_RESULTS = ROOT / "verification/wave39-proof-solver/exact-results.json"

COVERAGE_CERTIFICATE = DISCOVERY_ROOT / "coverage-certificate.json"
SHARD_METADATA = DISCOVERY_ROOT / "branch-15-x187-zero-formula.json"
SHARD_RAW = DISCOVERY_ROOT / "branch-15-x187-zero.opb"
SHARD_GZIP = DISCOVERY_ROOT / "branch-15-x187-zero.opb.gz"
RAW_PROOF = DISCOVERY_ROOT / "branch-15-x187-zero.raw.pbp"
KERNEL_PROOF = DISCOVERY_ROOT / "branch-15-x187-zero.kernel.pbp"
SOLVER_TRANSCRIPT = DISCOVERY_ROOT / "branch-15-x187-zero.solver.txt"
VERIPB_RAW_TRANSCRIPT = DISCOVERY_ROOT / "branch-15-x187-zero.veripb-raw.txt"
VERIPB_ELABORATE_TRANSCRIPT = (
    DISCOVERY_ROOT / "branch-15-x187-zero.veripb-elaborate.txt"
)
VERIPB_KERNEL_TRANSCRIPT = DISCOVERY_ROOT / "branch-15-x187-zero.veripb-kernel.txt"
CAKEPB_TRANSCRIPT = DISCOVERY_ROOT / "branch-15-x187-zero.cakepb.txt"
BOUNDED_RUN = DISCOVERY_ROOT / "bounded-run.json"
INPUT_FREEZE = DISCOVERY_ROOT / "input-freeze.sha256"
DISCOVERY_MANIFEST = DISCOVERY_ROOT / "package-manifest.sha256"
DISCOVERY_REPORT = DISCOVERY_ROOT / "run-report.yaml"
DISCOVERY_README = DISCOVERY_ROOT / "README.md"
CORRECTION_LEDGER = DISCOVERY_ROOT / "correction-ledger.md"
DISCOVERY_AGENT_REPORT = ROOT / "agents/2026-07-27-wave53-proof-cover.md"

INPUT_HASHES = {
    "verification/n3-joint-cover/n3-joint-cover.json":
        "58c4994ff0eef9c5e1702840f791d1400c3da71b445e3c217e3704c5e70de172",
    "verification/n3-refined-cover/n3-refined-cover.json":
        "fd9a14193365bf40d3d7bcbe53d56c6f1ffa8a93ca63d5b68506c3354f3b9f8a",
    "attempts/wave35-n3-upper-triple-overlap/root-endpoint-reduction.json":
        "7551c7b9d956705e41f9feb42d76d3bb5ab60dab0b46416fa9c0e58e5346a46a",
    "verification/wave37-rooted-branches/independent_check.py":
        "2039681ef17eafea7ace392682317d1baf250585d35474fe7dafa35a3cbca3f3",
    "attempts/wave38-solver-harvest/coverage-plan.json":
        "2de85c3f73d4b12a579b281c10171a47c12e26a323ecdf9617c1a842a81d8bf2",
    "verification/wave38-solver-harvest/independent-results.json":
        "2aa691682aa434d1166a98bf4af820652187ffe664911b8aa112104831fe8f6c",
    "attempts/wave37-proof-producing-endpoint/branch-15-formula.json":
        "3a6d4181445a2bdd7859faa0b493376891b4498eb0987989dcdcdc4b8ffe97d6",
    "attempts/wave37-proof-producing-endpoint/branch-15.opb.gz":
        "7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e",
    "verification/wave39-proof-solver/exact-results.json":
        "3afc665de9d8d0e5a5a4dab6b600db1e5b726ef1dfba685eeba92c80da1df5e4",
}

SOURCE_RAW_SHA256 = "4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5"
SHARD_RAW_SHA256 = "b1681416ee2860c4b40ce854fb533062af8e1c7a9dc0c423ba0c5f0545677d08"
SHARD_GZIP_SHA256 = "5d026ebdd3f4e05c46a494ba357fbcaa7e994f7c518a89b8c7f5dc956ac8ee9c"
RAW_PROOF_SHA256 = "ca94b003b5506bbf7164223db415f5df677381a0a1ec99ccc816508b81d36861"
KERNEL_PROOF_SHA256 = "251cc6158e9afba4db8e49eb0dcf02ec564bcfaf03de16151b1bbab0c0d968b9"

EXACT = "/home/researcher/.cache/conway-tools/exact/build-wave3/Exact"
VERIPB = "/home/researcher/.cache/conway-tools/veripb-install/bin/veripb"
CAKEPB = "/home/researcher/.cache/conway-tools/cakepb/cake_pb"
TOOL_HASHES = {
    EXACT: "842ac70b4e938d24f537a56513ff64ea845206c714ce34da467ce146c5c5c928",
    VERIPB: "635b6f2fbd7a7fb98bf7a1f7af038355a1e58438cfdc1ee4e2649979017ace36",
    CAKEPB: "5920919642b1c498c2654a849fcd894ea18e7736ebf32919a9a8915861033e46",
}

PAIR_COUNT = 7
COORDINATE_COUNT = 14
FIXED_EDGE = (0, 4)
REMAINING_ENDPOINTS = (1, 5, 6, 7, 8, 9, 10, 11, 12, 13)
CANDIDATE_ENDPOINTS = (0, 1, 3, 6, 7, 8, 9, 10, 11, 12, 13)
N3_UNIT = {frozenset((0, 2)), frozenset((2, 4))}
SOURCE_HEADER = b"* #variable= 289338 #constraint= 574615"
SHARD_HEADER = b"* #variable= 289338 #constraint= 574616"
ZERO_UNIT = b"+1 ~x187 >= 1 ;\n"
MINIMUM_FREE_MEMORY_PERCENT = 15.0

Matching = tuple[tuple[int, int], ...]
State = tuple[Matching, int]
Permutation = tuple[int, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def read_process_text(path: Path) -> str:
    payload = path.read_bytes()
    text = payload.decode("utf-16") if payload.startswith(b"\xff\xfe") else payload.decode("utf-8")
    return text.replace("\r\n", "\n")


def perfect_matchings(vertices: tuple[int, ...]) -> Iterator[Matching]:
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        remainder = vertices[1:index] + vertices[index + 1 :]
        for suffix in perfect_matchings(remainder):
            yield ((first, second),) + suffix


def compose(left: Sequence[int], right: Sequence[int]) -> Permutation:
    return tuple(left[right[index]] for index in range(COORDINATE_COUNT))


def generated_group(generators: Sequence[Permutation]) -> frozenset[Permutation]:
    identity = tuple(range(COORDINATE_COUNT))
    group = {identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            image = compose(generator, current)
            if image not in group:
                group.add(image)
                frontier.append(image)
    return frozenset(group)


def unit_image(permutation: Sequence[int]) -> set[frozenset[int]]:
    return {
        frozenset(permutation[coordinate] for coordinate in edge)
        for edge in N3_UNIT
    }


def parent_generators() -> tuple[Permutation, ...]:
    identity = tuple(range(COORDINATE_COUNT))
    generators: list[Permutation] = []
    end_swap = list(identity)
    end_swap[0], end_swap[4] = 4, 0
    end_swap[1], end_swap[5] = 5, 1
    generators.append(tuple(end_swap))
    for first in (6, 8, 10, 12):
        flip = list(identity)
        flip[first], flip[first + 1] = first + 1, first
        generators.append(tuple(flip))
    for first, second in ((6, 8), (8, 10), (10, 12)):
        swap = list(identity)
        swap[first], swap[second] = second, first
        swap[first + 1], swap[second + 1] = second + 1, first + 1
        generators.append(tuple(swap))
    return tuple(generators)


@lru_cache(maxsize=1)
def exact_stabilizers() -> tuple[frozenset[Permutation], frozenset[Permutation]]:
    """Compare generated groups to exhaustive filters of C2 wreath S7."""
    generated_parent = generated_group(parent_generators())
    generated_oriented = generated_group(parent_generators()[1:])
    filtered_parent: set[Permutation] = set()
    filtered_oriented: set[Permutation] = set()
    full_wreath_count = 0
    for pair_image in itertools.permutations(range(PAIR_COUNT)):
        for flip_mask in range(1 << PAIR_COUNT):
            full_wreath_count += 1
            permutation = [0] * COORDINATE_COUNT
            for source_pair in range(PAIR_COUNT):
                target_pair = pair_image[source_pair]
                flip = (flip_mask >> source_pair) & 1
                for endpoint in (0, 1):
                    permutation[2 * source_pair + endpoint] = (
                        2 * target_pair + (endpoint ^ flip)
                    )
            frozen = tuple(permutation)
            if unit_image(frozen) == N3_UNIT:
                filtered_parent.add(frozen)
                if frozen[0] == 0:
                    filtered_oriented.add(frozen)
    require(full_wreath_count == 645_120, "full scaffold wreath count changed")
    require(generated_parent == filtered_parent, "parent stabilizer is not exact")
    require(generated_oriented == filtered_oriented, "oriented stabilizer is not exact")
    require(len(generated_parent) == 768, "parent stabilizer order changed")
    require(len(generated_oriented) == 384, "oriented stabilizer order changed")
    return generated_parent, generated_oriented


def act_matching(matching: Matching, permutation: Sequence[int]) -> Matching:
    return tuple(
        sorted(
            tuple(sorted((permutation[left], permutation[right])))
            for left, right in matching
        )
    )


def act_state(state: State, permutation: Sequence[int]) -> State:
    matching, endpoint = state
    return act_matching(matching, permutation), permutation[endpoint]


def exact_orbits(
    states: Iterable[Any], group: Iterable[Permutation], action
) -> tuple[tuple[Any, frozenset[Any]], ...]:
    unseen = set(states)
    answer: list[tuple[Any, frozenset[Any]]] = []
    frozen_group = tuple(group)
    while unseen:
        representative = min(unseen)
        orbit = frozenset(action(representative, permutation) for permutation in frozen_group)
        require(orbit <= unseen, "reconstructed orbits overlap")
        unseen.difference_update(orbit)
        answer.append((representative, orbit))
    return tuple(answer)


@lru_cache(maxsize=1)
def matchings() -> frozenset[Matching]:
    result = {
        tuple(sorted((FIXED_EDGE, *remaining)))
        for remaining in perfect_matchings(REMAINING_ENDPOINTS)
    }
    require(len(result) == 945, "fixed-edge matching count changed")
    return frozenset(result)


@lru_cache(maxsize=1)
def parent_orbits() -> tuple[tuple[Matching, frozenset[Matching]], ...]:
    parent_group, _ = exact_stabilizers()
    result = exact_orbits(matchings(), parent_group, act_matching)
    require(len(result) == 12, "parent orbit count changed")
    require(sum(len(orbit) for _, orbit in result) == 945, "parent orbit mass changed")
    return result


@lru_cache(maxsize=1)
def refined_orbits() -> tuple[tuple[State, frozenset[State]], ...]:
    _, oriented_group = exact_stabilizers()
    states = {
        (matching, endpoint)
        for matching in matchings()
        for endpoint in CANDIDATE_ENDPOINTS
    }
    require(len(states) == 10_395, "refined state count changed")
    result = exact_orbits(states, oriented_group, act_state)
    require(len(result) == 78, "refined orbit count changed")
    require(sum(len(orbit) for _, orbit in result) == 10_395, "refined mass changed")
    return result


@lru_cache(maxsize=1)
def labels() -> tuple[tuple[int, int], ...]:
    result = tuple(
        (left, right)
        for left, right in itertools.combinations(range(COORDINATE_COUNT), 2)
        if right != (left ^ 1)
    )
    require(len(result) == 84, "residual-label count changed")
    return result


@lru_cache(maxsize=1)
def label_index() -> dict[tuple[int, int], int]:
    return {label: index for index, label in enumerate(labels())}


@lru_cache(maxsize=1)
def edge_variables() -> dict[tuple[int, int], int]:
    return {
        edge: variable
        for variable, edge in enumerate(
            itertools.combinations(range(len(labels())), 2), start=1
        )
    }


def containing(coordinate: int) -> tuple[int, ...]:
    return tuple(index for index, label in enumerate(labels()) if coordinate in label)


@lru_cache(maxsize=1)
def endpoint_edges() -> tuple[tuple[int, int], ...]:
    indices = label_index()
    answer = set()
    for pair in range(PAIR_COUNT):
        left = 2 * pair
        right = left + 1
        for other in range(COORDINATE_COUNT):
            if other in (left, right):
                continue
            first = indices[tuple(sorted((left, other)))]
            second = indices[tuple(sorted((right, other)))]
            answer.add(tuple(sorted((first, second))))
    result = tuple(sorted(answer))
    require(len(result) == 84, "endpoint edge-unit count changed")
    return result


def assignment(edge: tuple[int, int], value: bool) -> dict[str, Any]:
    return {
        "residual_edge": list(edge),
        "literal": edge_variables()[edge],
        "value": int(value),
    }


def branch_decisions(matching: Matching) -> dict[tuple[int, int], bool]:
    endpoint_to_label: dict[int, int] = {}
    for index in containing(2):
        left, right = labels()[index]
        endpoint_to_label[right if left == 2 else left] = index
    require(len(endpoint_to_label) == 12, "coordinate-2 fiber changed")
    positives = {
        tuple(sorted((endpoint_to_label[left], endpoint_to_label[right])))
        for left, right in matching
    }
    return {
        edge: edge in positives
        for edge in itertools.combinations(containing(2), 2)
    }


def matching_literals(matching: Matching) -> list[int]:
    return sorted(
        edge_variables()[edge]
        for edge, value in branch_decisions(matching).items()
        if value
    )


def refinement_edge(endpoint: int) -> tuple[int, int]:
    first = label_index()[(0, 2)]
    second = label_index()[tuple(sorted((4, endpoint)))]
    return tuple(sorted((first, second)))


def refined_literals(state: State) -> list[int]:
    matching, endpoint = state
    return sorted((*matching_literals(matching), edge_variables()[refinement_edge(endpoint)]))


def exact_parent_number(matching: Matching) -> int:
    for number, (representative, _) in enumerate(parent_orbits(), start=1):
        if representative == matching:
            return number
    raise AssertionError("refined representative lacks canonical parent")


def verify_prior_certificates() -> dict[str, Any]:
    parent_group, oriented_group = exact_stabilizers()
    joint = load_json(JOINT)
    require(joint["format"] == "n3-joint-fiber-matching-orbits-v1", "joint format")
    require(joint["stabilizer_order"] == len(parent_group), "joint stabilizer order")
    require(joint["matching_count"] == len(matchings()), "joint matching count")
    require(len(joint["branches"]) == len(parent_orbits()), "joint branch count")
    parent_burnside = sum(
        act_matching(matching, permutation) == matching
        for permutation in parent_group
        for matching in matchings()
    )
    require(parent_burnside == 9_216 == joint["burnside_fixed_sum"], "parent Burnside")
    for number, (record, (representative, orbit)) in enumerate(
        zip(joint["branches"], parent_orbits()), start=1
    ):
        stabilizer = sum(
            act_matching(representative, permutation) == representative
            for permutation in parent_group
        )
        require(record["branch"] == number, "joint branch numbering")
        require(record["representative"] == [list(edge) for edge in representative],
                "joint representative")
        require(record["orbit_size"] == len(orbit), "joint orbit size")
        require(record["stabilizer_size"] == stabilizer, "joint stabilizer size")
        require(record["positive_edge_literals"] == matching_literals(representative),
                "joint literal catalog")
        require(stabilizer * len(orbit) == len(parent_group), "joint orbit-stabilizer")

    refined = load_json(REFINED)
    require(refined["format"] == "n3-oriented-common-neighbor-orbits-v1",
            "refined format")
    require(refined["stabilizer_order"] == len(oriented_group), "refined group order")
    require(refined["state_count"] == 10_395, "refined recorded state count")
    require(refined["orbit_count"] == 78, "refined recorded orbit count")
    refined_burnside = 0
    for permutation in oriented_group:
        fixed_matchings = sum(
            act_matching(matching, permutation) == matching for matching in matchings()
        )
        fixed_candidates = sum(
            permutation[endpoint] == endpoint for endpoint in CANDIDATE_ENDPOINTS
        )
        refined_burnside += fixed_matchings * fixed_candidates
    require(refined_burnside == 29_952 == refined["burnside_fixed_sum"],
            "refined Burnside")
    for number, (record, (state, orbit)) in enumerate(
        zip(refined["orbits"], refined_orbits()), start=1
    ):
        matching, endpoint = state
        stabilizer = sum(
            act_state(state, permutation) == state for permutation in oriented_group
        )
        require(record["branch"] == number, "refined branch numbering")
        require(record["representative"] == [list(edge) for edge in matching],
                "refined representative")
        require(record["candidate_endpoint"] == endpoint, "refined endpoint")
        require(record["first_matching_branch"] == exact_parent_number(matching),
                "refined parent mapping")
        require(record["orbit_size"] == len(orbit), "refined orbit size")
        require(record["stabilizer_size"] == stabilizer, "refined stabilizer")
        require(record["positive_edge_literals"] == refined_literals(state),
                "refined literal catalog")
        require(stabilizer * len(orbit) == len(oriented_group),
                "refined orbit-stabilizer")
    return {
        "full_scaffold_automorphism_group": "C2 wreath S7",
        "full_scaffold_automorphism_order": 645_120,
        "n3_unit_stabilizer_order": len(parent_group),
        "oriented_stabilizer_order": len(oriented_group),
        "generated_groups_equal_exhaustive_full_wreath_filters": True,
        "parent_matching_count": 945,
        "parent_orbit_count": 12,
        "parent_burnside_fixed_sum": parent_burnside,
        "refined_state_count": 10_395,
        "refined_orbit_count": 78,
        "refined_burnside_fixed_sum": refined_burnside,
        "completed_graph_automorphism_assumed": False,
        "symmetry_interpretation": (
            "canonical relabelling by automorphisms of the frozen local scaffold; "
            "no automorphism of a completed graph is required"
        ),
    }


def reconstruct_coverage() -> tuple[dict[str, Any], dict[str, Any]]:
    endpoint_set = set(endpoint_edges())
    endpoint_units = [assignment(edge, False) for edge in endpoint_edges()]
    parent_records: list[dict[str, Any]] = []
    survivors: list[int] = []
    eliminated: list[int] = []
    for number, (matching, orbit) in enumerate(parent_orbits(), start=1):
        decisions = branch_decisions(matching)
        units = [assignment(edge, value) for edge, value in sorted(decisions.items())]
        conflicts = [
            unit
            for unit in units
            if unit["value"] == 1 and tuple(unit["residual_edge"]) in endpoint_set
        ]
        compatible = not conflicts
        stabilizer = 768 // len(orbit)
        parent_records.append({
            "parent_branch": number,
            "matching_representative": [list(edge) for edge in matching],
            "matching_orbit_size": len(orbit),
            "matching_stabilizer_size": stabilizer,
            "parent_units": units,
            "endpoint_conflict_literals": conflicts,
            "endpoint_compatible": compatible,
        })
        (survivors if compatible else eliminated).append(number)
    require(survivors == [4, 5, 8, 10, 12], "endpoint parent survivors changed")
    require(eliminated == [1, 2, 3, 6, 7, 9, 11], "eliminated parents changed")

    all_refined: list[dict[str, Any]] = []
    cases: list[dict[str, Any]] = []
    for number, (state, orbit) in enumerate(refined_orbits(), start=1):
        matching, endpoint = state
        parent = exact_parent_number(matching)
        record = {
            "refined_branch": number,
            "parent_branch": parent,
            "candidate_endpoint": endpoint,
            "state_orbit_size": len(orbit),
            "matching_representative": [list(edge) for edge in matching],
            "refinement_unit": assignment(refinement_edge(endpoint), True),
            "endpoint_compatible": parent in survivors,
        }
        all_refined.append(record)
        if parent in survivors:
            case = dict(record)
            case["complete_case_status"] = "UNKNOWN"
            case["checked_unsat_certificate"] = None
            cases.append(case)

    compatible_weight = sum(case["state_orbit_size"] for case in cases)
    incompatible = [record for record in all_refined if not record["endpoint_compatible"]]
    incompatible_weight = sum(record["state_orbit_size"] for record in incompatible)
    require(len(cases) == 33 and compatible_weight == 6_644, "compatible cover changed")
    require(len(incompatible) == 45 and incompatible_weight == 3_751,
            "incompatible cover changed")
    require(compatible_weight + incompatible_weight == 10_395, "weight partition")

    by_parent: dict[int, dict[str, int]] = defaultdict(
        lambda: {"case_count": 0, "state_orbit_weight": 0}
    )
    for case in cases:
        parent = case["parent_branch"]
        by_parent[parent]["case_count"] += 1
        by_parent[parent]["state_orbit_weight"] += case["state_orbit_size"]
    summary = {
        str(parent): record for parent, record in sorted(by_parent.items())
    }
    require(summary == {
        "4": {"case_count": 4, "state_orbit_weight": 132},
        "5": {"case_count": 4, "state_orbit_weight": 528},
        "8": {"case_count": 6, "state_orbit_weight": 704},
        "10": {"case_count": 8, "state_orbit_weight": 1_056},
        "12": {"case_count": 11, "state_orbit_weight": 4_224},
    }, "parent weight summary changed")
    expected = {
        "endpoint_units": endpoint_units,
        "parent_definitions": parent_records,
        "case_definitions": cases,
    }
    result = {
        "endpoint_unit_count": len(endpoint_units),
        "parent_definition_count": len(parent_records),
        "units_per_parent": sorted({len(record["parent_units"]) for record in parent_records}),
        "all_parent_unit_count": sum(len(record["parent_units"]) for record in parent_records),
        "all_refined_orbit_count": len(all_refined),
        "normalized_state_count": sum(record["state_orbit_size"] for record in all_refined),
        "endpoint_compatible_parent_branches": survivors,
        "endpoint_incompatible_parent_branches": eliminated,
        "endpoint_compatible_refined_orbit_count": len(cases),
        "endpoint_compatible_state_orbit_weight": compatible_weight,
        "endpoint_incompatible_refined_orbit_count": len(incompatible),
        "endpoint_incompatible_state_orbit_weight": incompatible_weight,
        "case_ids": [case["refined_branch"] for case in cases],
        "by_parent": summary,
        "every_recorded_endpoint_parent_and_refinement_unit_checked": True,
        "every_recorded_orbit_weight_checked": True,
    }
    return expected, result


def verify_discovery_coverage(certificate: dict[str, Any] | None = None) -> dict[str, Any]:
    if certificate is None:
        certificate = load_json(COVERAGE_CERTIFICATE)
    prior = verify_prior_certificates()
    expected, coverage = reconstruct_coverage()
    require(
        certificate["endpoint_assumptions"]["endpoint_nonedge_units"]
        == expected["endpoint_units"],
        "discovery endpoint units differ",
    )
    require(certificate["parent_definitions"] == expected["parent_definitions"],
            "discovery parent definitions differ")
    require(certificate["case_definitions"] == expected["case_definitions"],
            "discovery case definitions differ")
    recorded = certificate["coverage"]
    for key in (
        "normalized_state_count",
        "all_refined_orbit_count",
        "endpoint_incompatible_parent_branches",
        "endpoint_incompatible_refined_orbit_count",
        "endpoint_incompatible_state_orbit_weight",
        "endpoint_compatible_parent_branches",
        "endpoint_compatible_refined_orbit_count",
        "endpoint_compatible_state_orbit_weight",
        "case_ids",
    ):
        require(recorded[key] == coverage[key], f"discovery coverage field {key}")
    require(recorded["branch_cover_exhaustive_under_endpoint_assumptions"] is True,
            "discovery cover not marked exhaustive")
    require(
        certificate["endpoint_assumptions"]["completed_graph_automorphism_assumed"]
        is False,
        "completed-graph automorphism claim changed",
    )

    plan = load_json(WAVE38_PLAN)
    require(len(plan["cases"]) == len(expected["case_definitions"]), "Wave 38 case count")
    for frozen, queued in zip(expected["case_definitions"], plan["cases"]):
        require(frozen["refined_branch"] == queued["refined_branch"], "queue branch")
        require(frozen["parent_branch"] == queued["parent_branch"], "queue parent")
        require(frozen["candidate_endpoint"] == queued["candidate_endpoint"],
                "queue endpoint")
        require(frozen["state_orbit_size"] == queued["orbit_size"], "queue weight")
        require(frozen["refinement_unit"]["literal"] == queued["refinement_literal"],
                "queue literal")
    wave38 = load_json(WAVE38_RESULTS)
    require(wave38["conclusion"]["queue_mapping_verified"] is True, "Wave 38 queue")
    require(wave38["conclusion"]["proof_coverage"] == "0/33", "Wave 38 proof status")

    proof = certificate["proof_status"]
    wave39 = load_json(WAVE39_RESULTS)
    require(wave39["claim_label"] == "VERIFIED", "Wave 39 status")
    require(wave39["scope"] == "branch15 AND x187=1 only", "Wave 39 scope")
    require(wave39["closed_shards"] == 1, "Wave 39 shard count")
    require(wave39["closed_endpoint_cases"] == 0, "Wave 39 complete cases")
    require(proof["complete_cases_checked_unsat"] == 0, "proof numerator inflated")
    require(proof["complete_case_proof_coverage"] == "0/33", "proof coverage inflated")
    require(proof["endpoint_status"] == "UNKNOWN", "endpoint status inflated")
    require(proof["endpoint_excluded"] is False, "endpoint exclusion inflated")
    require(
        all(case["complete_case_status"] == "UNKNOWN"
            and case["checked_unsat_certificate"] is None
            for case in certificate["case_definitions"]),
        "a complete case was promoted",
    )
    return {"stabilizers_and_prior_certificates": prior, "coverage": coverage}


def parse_sha256_manifest(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for number, line in enumerate(path.read_text("utf-8").splitlines(), start=1):
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)", line)
        if match is None:
            raise ValueError(f"malformed manifest line {number}: {path}")
        digest, name = match.groups()
        if name in result:
            raise ValueError(f"duplicate manifest path {name}")
        result[name] = digest
    return result


def verify_input_and_package_hashes() -> dict[str, Any]:
    for name, digest in INPUT_HASHES.items():
        require(sha256_file(ROOT / name) == digest, f"frozen input hash changed: {name}")
    require(parse_sha256_manifest(INPUT_FREEZE) == INPUT_HASHES,
            "discovery input-freeze differs from protocol")
    certificate = load_json(COVERAGE_CERTIFICATE)
    require(certificate["inputs"] == INPUT_HASHES, "certificate input map differs")

    manifest = parse_sha256_manifest(DISCOVERY_MANIFEST)
    mismatches = {
        name: {"recorded": digest, "actual": sha256_file(ROOT / name)}
        for name, digest in manifest.items()
        if not (ROOT / name).is_file() or sha256_file(ROOT / name) != digest
    }
    require(not mismatches, "discovery package manifest has stale records")
    raw_relative = relative(SHARD_RAW)
    ignored = subprocess.run(
        ["git", "check-ignore", "--quiet", "--", raw_relative],
        cwd=ROOT,
        check=False,
    ).returncode == 0
    report_text = DISCOVERY_REPORT.read_text("utf-8")
    readme_text = DISCOVERY_README.read_text("utf-8")
    ledger_text = CORRECTION_LEDGER.read_text("utf-8")
    agent_text = DISCOVERY_AGENT_REPORT.read_text("utf-8")
    bounded_hash_match = re.search(
        rf"path:\s*{re.escape(relative(BOUNDED_RUN))}\s*\n"
        rf"\s*sha256:\s*([0-9a-f]{{64}})",
        report_text,
    )
    require(bounded_hash_match is not None, "run report omits bounded-run output hash")
    bounded_hash_current = bounded_hash_match.group(1) == sha256_file(BOUNDED_RUN)
    required_ledger_ids = (
        "W53-PC-C001",
        "W53-PC-C002",
        "W53-PC-C003",
        "W53-PC-C004",
    )
    ledger_ids_present = all(identifier in ledger_text for identifier in required_ledger_ids)
    manifest_has_resolution_files = all(
        path in manifest
        for path in (
            "attempts/wave53-proof-cover/.gitignore",
            "attempts/wave53-proof-cover/correction-ledger.md",
        )
    )
    source_metadata_listed = "branch-15-formula.json" in report_text
    strict_wall_wording_absent = "three-second wall" not in agent_text
    require(raw_relative not in manifest, "regenerable raw OPB should not be manifested")
    require(ignored, "regenerable raw OPB is not ignored")
    require(manifest_has_resolution_files, "resolution files absent from manifest")
    require(source_metadata_listed, "run report still omits source metadata")
    require(bounded_hash_current, "run report bounded-run output hash is stale")
    require(ledger_ids_present, "correction ledger is incomplete")
    require(strict_wall_wording_absent, "agent report retains strict-wall wording")
    return {
        "frozen_input_count": len(INPUT_HASHES),
        "all_frozen_input_hashes_match": True,
        "coverage_certificate_input_map_exact": True,
        "discovery_manifest_entry_count": len(manifest),
        "all_listed_discovery_manifest_hashes_match": True,
        "raw_opb_present": SHARD_RAW.is_file(),
        "raw_opb_listed_in_discovery_manifest": raw_relative in manifest,
        "raw_opb_git_ignored": ignored,
        "readme_calls_raw_opb_ignored": "ignored raw OPB" in readme_text,
        "run_report_lists_branch15_source_metadata": source_metadata_listed,
        "run_report_bounded_run_output_hash_current": bounded_hash_current,
        "correction_ledger_ids": list(required_ledger_ids),
        "correction_ledger_complete": ledger_ids_present,
        "resolution_files_listed_in_manifest": manifest_has_resolution_files,
        "agent_report_strict_three_second_wall_wording_absent":
            strict_wall_wording_absent,
        "resolved_corrections": [
            "W53-PC-C001: package-local ignore rule now matches the regenerated raw OPB.",
            "W53-PC-C002: run-report input list now includes branch-15-formula.json.",
            (
                "W53-PC-C003: historical RAM telemetry is labeled self-reported "
                "and --timeout=3 is not described as a strict process wall."
            ),
            "W53-PC-C004: run-report bounded-run output hash matches corrected bytes.",
        ],
        "corrections_required": [],
    }


def parse_no_conclusion(text: str, tool: str) -> str:
    if "s VERIFIED NO CONCLUSION" not in text:
        raise ValueError(f"{tool} transcript lacks VERIFIED NO CONCLUSION")
    if "s VERIFIED UNSATISFIABLE" in text or "s VERIFIED SATISFIABLE" in text:
        raise ValueError(f"{tool} transcript contains a terminal result")
    return "VERIFIED_NO_CONCLUSION"


def verify_formula_and_retained_transcripts() -> dict[str, Any]:
    source_compressed = SOURCE_GZIP.read_bytes()
    require(sha256_bytes(source_compressed) == INPUT_HASHES[relative(SOURCE_GZIP)],
            "source gzip hash changed")
    source_raw = gzip.decompress(source_compressed)
    require(sha256_bytes(source_raw) == SOURCE_RAW_SHA256, "source raw hash changed")
    source_header, source_body = source_raw.split(b"\n", 1)
    require(source_header == SOURCE_HEADER, "source header changed")
    require(source_body.count(b"\n") == 574_615, "source constraint line count")

    expected = SHARD_HEADER + b"\n" + source_body + ZERO_UNIT
    require(len(expected) == 29_827_720, "expected shard size changed")
    require(sha256_bytes(expected) == SHARD_RAW_SHA256, "expected shard hash changed")
    raw = SHARD_RAW.read_bytes()
    compressed = SHARD_GZIP.read_bytes()
    require(raw == expected, "raw shard is not the exact append-unit transform")
    require(sha256_bytes(raw) == SHARD_RAW_SHA256, "raw shard digest mismatch")
    require(sha256_bytes(compressed) == SHARD_GZIP_SHA256, "shard gzip digest mismatch")
    require(gzip.decompress(compressed) == raw, "raw and gzip shard bytes differ")
    require(raw.endswith(ZERO_UNIT), "x187=0 unit is not last")
    require(raw.splitlines()[-1] == ZERO_UNIT.rstrip(b"\n"), "last constraint changed")
    require(raw.count(ZERO_UNIT) >= 1, "x187 zero unit missing")

    metadata = load_json(SHARD_METADATA)
    require(metadata["source"]["gzip_sha256"] == INPUT_HASHES[relative(SOURCE_GZIP)],
            "metadata source gzip")
    require(metadata["source"]["raw_sha256"] == SOURCE_RAW_SHA256,
            "metadata source raw")
    require(metadata["source"]["constraints"] == 574_615, "metadata source count")
    require(metadata["transformation"] == {
        "kind": "append_unit_constraint",
        "assumption": "x187=0",
        "constraint": "+1 ~x187 >= 1 ;",
    }, "metadata transform semantics")
    require(metadata["opb"]["raw_sha256"] == SHARD_RAW_SHA256, "metadata raw hash")
    require(metadata["opb"]["gzip_sha256"] == SHARD_GZIP_SHA256, "metadata gzip hash")
    require(metadata["opb"]["constraints"] == 574_616, "metadata constraint count")
    require(metadata["status"] == "CANDIDATE_FORMULA_ONLY", "formula status inflated")

    require(sha256_file(RAW_PROOF) == RAW_PROOF_SHA256, "raw proof hash")
    require(sha256_file(KERNEL_PROOF) == KERNEL_PROOF_SHA256, "kernel proof hash")
    solver = read_process_text(SOLVER_TRANSCRIPT)
    require(re.search(r"^s UNKNOWN$", solver, re.M) is not None, "retained Exact status")
    require("s SATISFIABLE" not in solver and "s UNSATISFIABLE" not in solver,
            "retained Exact transcript is terminal")
    retained_statuses = {
        "veripb_raw": parse_no_conclusion(
            read_process_text(VERIPB_RAW_TRANSCRIPT), "retained VeriPB raw"
        ),
        "veripb_elaborate": parse_no_conclusion(
            read_process_text(VERIPB_ELABORATE_TRANSCRIPT),
            "retained VeriPB elaboration",
        ),
        "veripb_kernel": parse_no_conclusion(
            read_process_text(VERIPB_KERNEL_TRANSCRIPT), "retained VeriPB kernel"
        ),
        "cakepb_kernel": parse_no_conclusion(
            read_process_text(CAKEPB_TRANSCRIPT), "retained CakePB kernel"
        ),
    }
    bounded = load_json(BOUNDED_RUN)
    require(bounded["exact"]["result"] == "UNKNOWN", "bounded result inflated")
    require(set(bounded["proof_replay"].values()) == {"VERIFIED_NO_CONCLUSION"},
            "bounded replay status changed")
    require(bounded["conclusion"]["proof_coverage"] == "0/33", "bounded proof coverage")
    require(bounded["conclusion"]["mathematical_evidence"] == "NONE",
            "bounded evidentiary value")
    require(bounded["conclusion"]["complete_endpoint_cases_closed"] == 0,
            "bounded complete cases")
    resource = bounded["resource_guard"]
    require(
        resource["historical_guard_status"]
        == "SELF_REPORTED_NOT_INDEPENDENTLY_REPLAYABLE",
        "historical resource status is not fail-closed",
    )
    require(resource["raw_monitor_transcript_retained"] is False,
            "historical monitor evidence boundary changed")
    return {
        "source_gzip_sha256": sha256_bytes(source_compressed),
        "source_raw_sha256": sha256_bytes(source_raw),
        "source_declared_constraints": 574_615,
        "source_constraint_lines": source_body.count(b"\n"),
        "shard_raw_sha256": sha256_bytes(raw),
        "shard_gzip_sha256": sha256_bytes(compressed),
        "shard_raw_bytes": len(raw),
        "shard_declared_constraints": 574_616,
        "raw_equals_gzip_decompression": True,
        "exact_transformation": "header +1 and append +1 ~x187 >= 1 ;",
        "opb_semantics": "~x187 is true exactly when x187=0",
        "retained_exact": "UNKNOWN",
        "retained_proof_statuses": retained_statuses,
        "retained_no_conclusion_case_coverage_contribution": 0,
        "historical_discovery_resource_telemetry":
            "SELF_REPORTED_NOT_INDEPENDENTLY_REPLAYABLE",
        "historical_raw_monitor_transcript_retained": False,
    }


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def free_physical_memory_percent() -> float:
    if os.name != "nt":
        with Path("/proc/meminfo").open("r", encoding="ascii") as stream:
            values = {}
            for line in stream:
                key, raw = line.split(":", 1)
                values[key] = int(raw.strip().split()[0])
        return 100.0 * values["MemAvailable"] / values["MemTotal"]
    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.ullAvailPhys / status.ullTotalPhys


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    return f"/mnt/{drive}/" + "/".join(resolved.parts[1:])


def run_wsl_tool(
    label: str,
    arguments: list[str],
    transcript_dir: Path,
    expected_status: str,
    timeout_seconds: int = 180,
) -> dict[str, Any]:
    before = free_physical_memory_percent()
    require(before >= MINIMUM_FREE_MEMORY_PERCENT,
            f"{label}: free memory {before:.2f}% is below reserve")
    completed = subprocess.run(
        ["wsl.exe", "-e", *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    after = free_physical_memory_percent()
    output = completed.stdout + completed.stderr
    transcript_dir.mkdir(parents=True, exist_ok=True)
    (transcript_dir / f"fresh-{label}.txt").write_text(
        output, encoding="utf-8", newline="\n"
    )
    require(completed.returncode == 0, f"{label} exited {completed.returncode}")
    require(expected_status in output, f"{label} lacks status {expected_status!r}")
    require(after >= MINIMUM_FREE_MEMORY_PERCENT,
            f"{label}: free memory {after:.2f}% is below reserve")
    return {
        "returncode": completed.returncode,
        "status_line": expected_status,
        "free_memory_percent_before": round(before, 2),
        "free_memory_percent_after": round(after, 2),
        "transcript_path": relative(transcript_dir / f"fresh-{label}.txt"),
        "transcript_sha256": sha256_file(transcript_dir / f"fresh-{label}.txt"),
    }


def verify_wsl_tool_hashes() -> dict[str, str]:
    result: dict[str, str] = {}
    for path, expected in TOOL_HASHES.items():
        completed = subprocess.run(
            ["wsl.exe", "-e", "sha256sum", path],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        require(completed.returncode == 0, f"cannot hash tool {path}")
        actual = completed.stdout.split()[0]
        require(actual == expected, f"tool hash changed: {path}")
        result[Path(path).name] = actual
    return result


def run_fresh_proof_tools(transcript_dir: Path) -> dict[str, Any]:
    transcript_dir = transcript_dir.resolve()
    hashes = verify_wsl_tool_hashes()
    opb = wsl_path(SHARD_RAW)
    raw_proof = wsl_path(RAW_PROOF)
    kernel_proof = wsl_path(KERNEL_PROOF)
    with tempfile.TemporaryDirectory(prefix="wave53-proof-cover-") as temporary:
        temp = Path(temporary)
        exact_proof = temp / "fresh-exact.raw.pbp"
        fresh_kernel = temp / "fresh-elaborated.kernel.pbp"
        records = {
            "exact": run_wsl_tool(
                "exact",
                [
                    EXACT,
                    "--timeout=3",
                    "--proof-assumptions=0",
                    f"--proof-log={wsl_path(exact_proof)}",
                    opb,
                ],
                transcript_dir,
                "s UNKNOWN",
            ),
            "veripb_raw": run_wsl_tool(
                "veripb-raw",
                [VERIPB, "--force-checked-deletion", opb, raw_proof],
                transcript_dir,
                "s VERIFIED NO CONCLUSION",
            ),
            "veripb_elaborate": run_wsl_tool(
                "veripb-elaborate",
                [
                    VERIPB,
                    "--force-checked-deletion",
                    "--elaborate",
                    wsl_path(fresh_kernel),
                    opb,
                    raw_proof,
                ],
                transcript_dir,
                "s VERIFIED NO CONCLUSION",
            ),
            "veripb_kernel": run_wsl_tool(
                "veripb-kernel",
                [VERIPB, "--force-checked-deletion", opb, kernel_proof],
                transcript_dir,
                "s VERIFIED NO CONCLUSION",
            ),
            "cakepb_kernel": run_wsl_tool(
                "cakepb-kernel",
                [CAKEPB, opb, kernel_proof],
                transcript_dir,
                "s VERIFIED NO CONCLUSION",
            ),
        }
        require(exact_proof.is_file() and exact_proof.stat().st_size > 0,
                "fresh Exact emitted no proof")
        require(fresh_kernel.is_file(), "fresh elaboration emitted no kernel proof")
        records["exact"]["temporary_proof_bytes"] = exact_proof.stat().st_size
        records["exact"]["temporary_proof_sha256"] = sha256_file(exact_proof)
        records["veripb_elaborate"]["fresh_kernel_sha256"] = sha256_file(fresh_kernel)
        records["veripb_elaborate"]["matches_retained_kernel"] = (
            sha256_file(fresh_kernel) == KERNEL_PROOF_SHA256
        )
    minimum_observed = min(
        value
        for record in records.values()
        for key, value in record.items()
        if key.startswith("free_memory_percent_")
    )
    require(minimum_observed >= MINIMUM_FREE_MEMORY_PERCENT, "memory reserve violated")
    return {
        "tool_hashes": hashes,
        "minimum_required_free_memory_percent": MINIMUM_FREE_MEMORY_PERCENT,
        "minimum_observed_free_memory_percent": minimum_observed,
        "reserve_passed": True,
        "runs": records,
        "mathematical_evidence": "NONE",
        "case_coverage_contribution": 0,
    }


def build_results(
    run_tools: bool = False,
    transcript_dir: Path = VERIFY_ROOT,
) -> dict[str, Any]:
    coverage = verify_discovery_coverage()
    formula = verify_formula_and_retained_transcripts()
    hashes = verify_input_and_package_hashes()
    fresh = (
        run_fresh_proof_tools(transcript_dir)
        if run_tools
        else {
            "status": "NOT_RUN_BY_THIS_INVOCATION",
            "minimum_required_free_memory_percent": MINIMUM_FREE_MEMORY_PERCENT,
        }
    )
    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED_COVER_AND_NO_CONCLUSION",
        "scope": (
            "exact conditional 33-case endpoint cover, branch-15 x187=0 "
            "append-unit formula, and nonterminal proof status"
        ),
        "inputs": {
            **INPUT_HASHES,
            relative(COVERAGE_CERTIFICATE): sha256_file(COVERAGE_CERTIFICATE),
            relative(SHARD_METADATA): sha256_file(SHARD_METADATA),
            relative(SHARD_GZIP): sha256_file(SHARD_GZIP),
            relative(RAW_PROOF): sha256_file(RAW_PROOF),
            relative(KERNEL_PROOF): sha256_file(KERNEL_PROOF),
            relative(BOUNDED_RUN): sha256_file(BOUNDED_RUN),
            relative(DISCOVERY_MANIFEST): sha256_file(DISCOVERY_MANIFEST),
            relative(DISCOVERY_REPORT): sha256_file(DISCOVERY_REPORT),
            relative(DISCOVERY_README): sha256_file(DISCOVERY_README),
            relative(CORRECTION_LEDGER): sha256_file(CORRECTION_LEDGER),
            "attempts/wave53-proof-cover/.gitignore":
                sha256_file(DISCOVERY_ROOT / ".gitignore"),
            relative(DISCOVERY_AGENT_REPORT): sha256_file(DISCOVERY_AGENT_REPORT),
        },
        "automorphism_and_prior_certificate_audit":
            coverage["stabilizers_and_prior_certificates"],
        "coverage": coverage["coverage"],
        "formula_and_retained_proof_audit": formula,
        "hash_and_manifest_audit": hashes,
        "fresh_tool_replay": fresh,
        "proof_boundary": {
            "conditional_case_coverage": "33/33",
            "complete_cases_checked_unsat": 0,
            "complete_cases_total": 33,
            "complete_case_unsat_coverage": "0/33",
            "verified_no_conclusion_unsat_coverage_contribution": 0,
            "branch15_status": "UNKNOWN",
            "endpoint_status": "UNKNOWN",
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "conway_99_status": "UNKNOWN",
        },
        "conclusion": {
            "exact_conditional_branch_cover_verified": True,
            "branch15_x187_zero_export_verified": True,
            "retained_no_conclusion_transcripts_verified": True,
            "complete_endpoint_case_closed": False,
            "mathematical_conclusion_from_bounded_run": "NONE",
            "target_status": "UNKNOWN",
            "publication_status": "VERIFIED NO CONCLUSION",
        },
        "correction_resolution": {
            "resolved": hashes["resolved_corrections"],
            "remaining": hashes["corrections_required"],
        },
        "corrections_required": hashes["corrections_required"],
        "limitations": [
            "The cover is conditional on the previously audited normalized n3=4158 endpoint.",
            "Orbit reduction uses local-scaffold relabelling, not completed-graph automorphisms.",
            "The branch formulas encode necessary endpoint conditions and partial prism families.",
            "No complete case has a checked terminal proof.",
            "No endpoint exclusion, graph, strict upper-bound improvement, or novelty claim follows.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--run-proof-tools", action="store_true")
    parser.add_argument("--transcript-dir", type=Path, default=VERIFY_ROOT)
    arguments = parser.parse_args()
    require(not (arguments.output and arguments.verify), "choose output or verify")
    result = build_results(arguments.run_proof_tools, arguments.transcript_dir)
    rendered = canonical_json(result)
    if arguments.output:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    elif arguments.verify:
        require(arguments.verify.read_text("utf-8") == rendered,
                "stored independent results differ")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
