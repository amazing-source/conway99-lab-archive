#!/usr/bin/env python3
"""Independent audit of the Wave 36 fixed-triangle prism package.

This checker intentionally imports no project discovery module.  It rebuilds
the rooted labels, named edge-variable order, stabilizer orbits, endpoint
units, branch assignments, and all five prism-clause catalogs directly from
the frozen combinatorial definitions.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator, Sequence


PAIR_COUNT = 7
COORDINATE_COUNT = 14
RESIDUAL_COUNT = 84
FULL_VERTEX_COUNT = 99
ROOT_VERTEX = 0
COORDINATE_OFFSET = 1
RESIDUAL_OFFSET = 15
SHARED_COORDINATE = 2
FIXED_MATCHING_EDGE = (0, 4)
REMAINING_ENDPOINTS = (1, 5, 6, 7, 8, 9, 10, 11, 12, 13)
REFINEMENT_ENDPOINTS = (0, 1, 3, 6, 7, 8, 9, 10, 11, 12, 13)
EXPECTED_SURVIVORS = (4, 5, 8, 10, 12)
EXPECTED_REFINED_IDS = {
    4: list(range(15, 19)),
    5: list(range(19, 23)),
    8: list(range(36, 42)),
    10: list(range(50, 58)),
    12: list(range(68, 79)),
}
EXPECTED_CATALOG_HASHES = {
    4: "f675391a81dd817fe45f805a9bc9309dba02910988b42988238b66e6c2f5ae2e",
    5: "1215e64d0b8ebd5c898278acdd828cb657d8f1a1485fba4893e34316d94edaf5",
    8: "bb9aac4e06e0d5f9b885aa0705b31d576d8cca7221075cfab938ce70f5716a53",
    10: "eedd27d0322694661a4142a54fca80c95e416b09b2d59d6b21cf74beb4ef2af5",
    12: "ac1aea55f24f3fd23045daa2195cadbd8c2a799b3a27f4755e1ad99290f238d7",
}

Matching = tuple[tuple[int, int], ...]
RefinedState = tuple[Matching, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


@lru_cache(maxsize=1)
def labels() -> tuple[tuple[int, int], ...]:
    answer = tuple(
        (left, right)
        for left, right in itertools.combinations(range(COORDINATE_COUNT), 2)
        if right != (left ^ 1)
    )
    require(len(answer) == RESIDUAL_COUNT, "residual-label count changed")
    return answer


@lru_cache(maxsize=1)
def label_index() -> dict[tuple[int, int], int]:
    return {label: index for index, label in enumerate(labels())}


@lru_cache(maxsize=1)
def edge_variables() -> dict[tuple[int, int], int]:
    return {
        edge: variable
        for variable, edge in enumerate(
            itertools.combinations(range(RESIDUAL_COUNT), 2), start=1
        )
    }


def containing(coordinate: int) -> tuple[int, ...]:
    return tuple(
        index for index, label in enumerate(labels()) if coordinate in label
    )


def perfect_matchings(vertices: tuple[int, ...]) -> Iterator[Matching]:
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        remaining = vertices[1:index] + vertices[index + 1 :]
        for suffix in perfect_matchings(remaining):
            yield ((first, second),) + suffix


def permute_matching(matching: Matching, permutation: Sequence[int]) -> Matching:
    return tuple(
        sorted(
            tuple(sorted((permutation[left], permutation[right])))
            for left, right in matching
        )
    )


def parent_generators() -> tuple[tuple[int, ...], ...]:
    identity = tuple(range(COORDINATE_COUNT))
    generators: list[tuple[int, ...]] = []
    swap_end_pairs = list(identity)
    swap_end_pairs[0], swap_end_pairs[4] = 4, 0
    swap_end_pairs[1], swap_end_pairs[5] = 5, 1
    generators.append(tuple(swap_end_pairs))
    for left in (6, 8, 10, 12):
        permutation = list(identity)
        permutation[left], permutation[left + 1] = left + 1, left
        generators.append(tuple(permutation))
    for left, right in ((6, 8), (8, 10), (10, 12)):
        permutation = list(identity)
        permutation[left], permutation[right] = right, left
        permutation[left + 1], permutation[right + 1] = right + 1, left + 1
        generators.append(tuple(permutation))
    return tuple(generators)


def orbit(seed, generators, action) -> set:
    reached = {seed}
    frontier = [seed]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            image = action(current, generator)
            if image not in reached:
                reached.add(image)
                frontier.append(image)
    return reached


@lru_cache(maxsize=1)
def parent_orbits() -> tuple[tuple[Matching, int], ...]:
    unseen = set(perfect_matchings(REMAINING_ENDPOINTS))
    answer: list[tuple[Matching, int]] = []
    for seed in sorted(tuple(unseen)):
        if seed not in unseen:
            continue
        reached = orbit(seed, parent_generators(), permute_matching)
        require(reached <= unseen, "parent matching orbits overlap")
        unseen.difference_update(reached)
        representative = tuple(sorted((FIXED_MATCHING_EDGE, *seed)))
        answer.append((representative, len(reached)))
    require(not unseen and len(answer) == 12, "parent orbit cover is incomplete")
    require(sum(size for _, size in answer) == 945, "parent orbit mass changed")
    return tuple(answer)


def refined_action(state: RefinedState, permutation: Sequence[int]) -> RefinedState:
    matching, endpoint = state
    return permute_matching(matching, permutation), permutation[endpoint]


@lru_cache(maxsize=1)
def refined_orbits() -> tuple[tuple[Matching, int, int], ...]:
    all_matchings = {
        tuple(sorted((FIXED_MATCHING_EDGE, *remaining)))
        for remaining in perfect_matchings(REMAINING_ENDPOINTS)
    }
    unseen: set[RefinedState] = {
        (matching, endpoint)
        for matching in all_matchings
        for endpoint in REFINEMENT_ENDPOINTS
    }
    generators = parent_generators()[1:]
    answer: list[tuple[Matching, int, int]] = []
    for seed in sorted(tuple(unseen)):
        if seed not in unseen:
            continue
        reached = orbit(seed, generators, refined_action)
        require(reached <= unseen, "refined orbits overlap")
        unseen.difference_update(reached)
        answer.append((seed[0], seed[1], len(reached)))
    require(not unseen and len(answer) == 78, "refined orbit cover is incomplete")
    require(sum(size for _, _, size in answer) == 10_395, "refined mass changed")
    return tuple(answer)


def parent_number_for_matching(matching: Matching) -> int:
    for number, (representative, _) in enumerate(parent_orbits(), start=1):
        if representative == matching:
            return number
    raise AssertionError("refined representative lacks a parent")


def branch_decisions(branch: int) -> dict[tuple[int, int], bool]:
    representative = parent_orbits()[branch - 1][0]
    endpoint_to_label = {}
    for index in containing(SHARED_COORDINATE):
        left, right = labels()[index]
        endpoint_to_label[right if left == SHARED_COORDINATE else left] = index
    require(len(endpoint_to_label) == 12, "shared fiber endpoint map changed")
    positive = {
        tuple(sorted((endpoint_to_label[left], endpoint_to_label[right])))
        for left, right in representative
    }
    fiber = containing(SHARED_COORDINATE)
    return {
        edge: edge in positive for edge in itertools.combinations(fiber, 2)
    }


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
    require(len(result) == 84, "endpoint unit count changed")
    return result


def endpoint_hash() -> str:
    payload = json.dumps([list(edge) for edge in endpoint_edges()], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def full_edge_state(first: int, second: int) -> bool | int:
    if first == second:
        return False
    if first > second:
        first, second = second, first
    if first == ROOT_VERTEX:
        return COORDINATE_OFFSET <= second < RESIDUAL_OFFSET
    first_coordinate = first < RESIDUAL_OFFSET
    second_coordinate = second < RESIDUAL_OFFSET
    if first_coordinate and second_coordinate:
        a = first - COORDINATE_OFFSET
        b = second - COORDINATE_OFFSET
        return a // 2 == b // 2 and a != b
    if first_coordinate:
        coordinate = first - COORDINATE_OFFSET
        residual = second - RESIDUAL_OFFSET
        return coordinate in labels()[residual]
    residual_edge = (first - RESIDUAL_OFFSET, second - RESIDUAL_OFFSET)
    return edge_variables()[residual_edge]


def possible_neighbors(vertex: int, excluded: frozenset[int]) -> tuple[int, ...]:
    return tuple(
        other
        for other in range(FULL_VERTEX_COUNT)
        if other not in excluded
        and other != vertex
        and full_edge_state(vertex, other) is not False
    )


def branch_triangles(branch: int) -> tuple[tuple[int, int, int], ...]:
    fiber = set(containing(SHARED_COORDINATE))
    positive = sorted(
        edge
        for edge, present in branch_decisions(branch).items()
        if present and edge[0] in fiber and edge[1] in fiber
    )
    require(len(positive) == 6, "branch does not fix a perfect matching")
    return tuple(
        (COORDINATE_OFFSET + SHARED_COORDINATE,
         RESIDUAL_OFFSET + left, RESIDUAL_OFFSET + right)
        for left, right in positive
    )


def positive_variables(edges: Iterable[tuple[int, int]]) -> tuple[int, ...] | None:
    variables = set()
    for edge in edges:
        state = full_edge_state(*edge)
        if state is False:
            return None
        if state is not True:
            variables.add(int(state))
    return tuple(sorted(variables))


def triangle_catalog(triangle: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    fixed = tuple(triangle)
    excluded = frozenset(fixed)
    neighbor_lists = tuple(possible_neighbors(vertex, excluded) for vertex in fixed)
    clauses: set[tuple[int, ...]] = set()
    for matched in itertools.product(*neighbor_lists):
        if len(set(matched)) != 3:
            continue
        required = (
            (fixed[0], matched[0]),
            (fixed[1], matched[1]),
            (fixed[2], matched[2]),
            (matched[0], matched[1]),
            (matched[0], matched[2]),
            (matched[1], matched[2]),
        )
        variables = positive_variables(required)
        if variables is None:
            continue
        require(bool(variables), "fixed scaffold contains a prism")
        clauses.add(tuple(-variable for variable in variables))
    return tuple(sorted(clauses))


def fixed_assignments(branch: int) -> dict[int, bool]:
    variables = edge_variables()
    answer = {variables[edge]: False for edge in endpoint_edges()}
    indices = label_index()
    normalization = tuple(sorted((indices[(0, 2)], indices[(2, 4)])))
    answer[variables[normalization]] = True
    for edge, present in branch_decisions(branch).items():
        variable = variables[edge]
        require(variable not in answer or answer[variable] == present,
                "endpoint-compatible branch has a unit conflict")
        answer[variable] = present
    return answer


@lru_cache(maxsize=None)
def catalog_record(branch: int) -> tuple[dict[str, object], tuple[tuple[int, ...], ...]]:
    assignments = fixed_assignments(branch)
    all_active: set[tuple[int, ...]] = set()
    per_triangle = []
    for triangle in branch_triangles(branch):
        raw = triangle_catalog(triangle)
        active = tuple(
            clause
            for clause in raw
            if not any(
                assignments.get(abs(literal)) == (literal > 0)
                for literal in clause
                if abs(literal) in assignments
            )
        )
        all_active.update(active)
        per_triangle.append({
            "triangle": list(triangle),
            "raw_clause_count": len(raw),
            "active_after_fixed_units": len(active),
        })
    ordered = tuple(sorted(all_active))
    histogram = Counter(map(len, ordered))
    digest = hashlib.sha256(
        canonical_compact_json([list(clause) for clause in ordered]).encode("utf-8")
    ).hexdigest()
    record = {
        "fixed_triangle_count": len(per_triangle),
        "per_triangle": per_triangle,
        "deduplicated_active_clause_count": len(ordered),
        "clause_length_histogram": {
            str(length): histogram[length] for length in sorted(histogram)
        },
        "clause_catalog_sha256": digest,
    }
    return record, ordered


def check_lambda_one_lemma() -> dict[str, object]:
    # Name t0,t1,t2 as 0,1,2 and their matched u0,u1,u2 as 3,4,5.
    triangle_edges = {(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5)}
    matching_edges = {(0, 3), (1, 4), (2, 5)}
    required = triangle_edges | matching_edges
    off_matching = {(0, 4), (0, 5), (1, 3), (1, 5), (2, 3), (2, 4)}
    hostile_failures = []
    for edge in sorted(off_matching):
        graph = required | {edge}
        for left, right in triangle_edges:
            common = {
                vertex
                for vertex in range(6)
                if tuple(sorted((left, vertex))) in graph
                and tuple(sorted((right, vertex))) in graph
            }
            if len(common) > 1:
                break
        else:
            hostile_failures.append(edge)
    require(not hostile_failures, "an off-matching cross edge escaped lambda=1")
    return {
        "required_six_edge_pattern_forces_induced_prism": True,
        "off_matching_cross_edges_checked": len(off_matching),
        "lambda_one_violations_detected": len(off_matching),
    }


@lru_cache(maxsize=1)
def build_results() -> dict[str, object]:
    root = repository_root()
    discovery = json.loads(
        (root / "attempts/wave36-rooted-branches/derived-clause-catalog.json")
        .read_text(encoding="utf-8")
    )
    submitted_records = {record["branch"]: record for record in discovery["records"]}

    survivor_profile = {}
    endpoint_set = set(endpoint_edges())
    for branch in range(1, 13):
        positive = {
            edge for edge, present in branch_decisions(branch).items() if present
        }
        survivor_profile[branch] = len(positive & endpoint_set)
    survivors = tuple(
        branch for branch, clashes in survivor_profile.items() if clashes == 0
    )
    require(survivors == EXPECTED_SURVIVORS, "endpoint parent survivors changed")

    refined_by_parent: dict[int, list[int]] = {}
    for identifier, (matching, _, _) in enumerate(refined_orbits(), start=1):
        refined_by_parent.setdefault(parent_number_for_matching(matching), []).append(identifier)
    endpoint_refined = {parent: refined_by_parent[parent] for parent in survivors}
    require(endpoint_refined == EXPECTED_REFINED_IDS, "endpoint refined IDs changed")

    catalog_results = {}
    for branch in survivors:
        record, _ = catalog_record(branch)
        require(record == submitted_records[branch]["strengthening"],
                f"branch {branch} catalog metadata differs")
        require(record["clause_catalog_sha256"] == EXPECTED_CATALOG_HASHES[branch],
                f"branch {branch} catalog hash changed")
        catalog_results[str(branch)] = record

    budget = json.loads(
        (root / "attempts/wave36-rooted-branches/branch-04-prism-100k.json")
        .read_text(encoding="utf-8")
    )
    budget_record = budget["records"][0]
    solver = budget_record["solver"]
    require(budget_record["status"] == "BUDGET_UNKNOWN", "budget status inflated")
    require(solver["conflict_budget"] == solver["accumulated_stats"]["conflicts"] == 100_000,
            "budget boundary does not bind")
    require(budget_record["candidate_path"] is None
            and budget_record["candidate_sha256"] is None,
            "budget result unexpectedly contains a candidate")

    inputs = [
        "agents/2026-07-27-wave36-rooted-branches.md",
        "attempts/wave36-rooted-branches/derived-clause-catalog.json",
        "attempts/wave36-rooted-branches/branch-04-prism-100k.json",
        "attempts/wave36-rooted-branches/run-report.yaml",
    ]
    return {
        "schema_version": 1,
        "role": "verifier",
        "scope": "fixed-triangle prism lemma, five catalogs, exact rooted branch scope, and bounded-solver status",
        "claim_label": "VERIFIED_SCOPED_CONDITIONAL_CLAUSES",
        "input_sha256": {path: sha256_file(root / path) for path in inputs},
        "lambda_one_prism_lemma": check_lambda_one_lemma(),
        "endpoint": {
            "unit_count": len(endpoint_edges()),
            "unit_catalog_sha256": endpoint_hash(),
            "parent_branch_clash_counts": {
                str(branch): survivor_profile[branch] for branch in survivor_profile
            },
            "surviving_parent_branches": list(survivors),
        },
        "branch_cover": {
            "parent_orbit_count": len(parent_orbits()),
            "parent_state_count": sum(size for _, size in parent_orbits()),
            "refined_orbit_count": len(refined_orbits()),
            "refined_state_count": sum(size for _, _, size in refined_orbits()),
            "endpoint_refined_case_count": sum(map(len, endpoint_refined.values())),
            "endpoint_refined_ids_by_parent": {
                str(parent): identifiers
                for parent, identifiers in endpoint_refined.items()
            },
            "completed_graph_automorphism_assumed": False,
        },
        "catalogs": catalog_results,
        "bounded_solver_artifact": {
            "branch": budget_record["branch"],
            "status": budget_record["status"],
            "conflict_budget": solver["conflict_budget"],
            "conflicts": solver["accumulated_stats"]["conflicts"],
            "candidate_present": False,
            "mathematical_evidentiary_value": "NONE",
        },
        "conclusion": {
            "conditional_clause_family_verified": True,
            "all_prisms_encoded": False,
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "target_status": "UNKNOWN",
        },
        "limitations": [
            "The clause catalogs cover only prisms meeting one of six fixed triangles per parent.",
            "The branch cover is conditional on the already audited N3 normalization.",
            "No SAT model, UNSAT proof, endpoint exclusion, or improved upper bound is present.",
            "The nonterminal 33-case run is not an artifact and was not audited.",
        ],
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    require(not (args.output and args.verify), "choose one output mode")
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
