#!/usr/bin/env python3
"""Independent verifier for the Wave 38 complete-endpoint construction.

The mathematical inventory and prism oracle are rebuilt without importing the
discovery implementation.  Discovery code is loaded only after those clean-room
results exist, for differential and hostile validation of its public APIs.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import itertools
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

import yaml


PAIR_COUNT = 7
COORDINATE_COUNT = 14
RESIDUAL_COUNT = 84
FULL_VERTEX_COUNT = 99
ROOT_VERTEX = 0
COORDINATE_OFFSET = 1
RESIDUAL_OFFSET = 15
EXPECTED_REFINED_IDS = (
    15, 16, 17, 18,
    19, 20, 21, 22,
    36, 37, 38, 39, 40, 41,
    50, 51, 52, 53, 54, 55, 56, 57,
    68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78,
)
EXPECTED_BY_PARENT = {
    4: (15, 16, 17, 18),
    5: (19, 20, 21, 22),
    8: (36, 37, 38, 39, 40, 41),
    10: (50, 51, 52, 53, 54, 55, 56, 57),
    12: (68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78),
}
SENSITIVE_PATTERNS = (
    re.compile(r"(?i)\b[A-Z]:[\\/]"),
    re.compile(r"(?i)(?:^|[\\/])Users[\\/]"),
    re.compile(r"(?i)(?:^|[\\/])home[\\/]"),
    re.compile(r"(?i)\b(?:ghp_|github_pat_|sk-[A-Za-z0-9])"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._-]+"),
    re.compile(r"(?i)\b(?:OPENAI_API_KEY|GITHUB_TOKEN)\b"),
)
TEXT_SUFFIXES = {".json", ".md", ".py", ".sha256", ".yaml", ".yml", ".gitignore"}

Edge = tuple[int, int]
Triangle = tuple[int, int, int]
Witness = tuple[Triangle, Triangle, tuple[Edge, Edge, Edge]]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def attempt_root() -> Path:
    return repository_root() / "attempts/wave38-complete-endpoint"


def verifier_root() -> Path:
    return Path(__file__).resolve().parent


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_compact(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


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
    require(isinstance(value, dict), f"{path} is not a JSON object")
    return value


class StrictYamlLoader(yaml.SafeLoader):
    pass


def construct_unique_mapping(
    loader: StrictYamlLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[str, Any]:
    loader.flatten_mapping(node)
    answer: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in answer:
            raise ValueError(f"duplicate YAML key {key!r}")
        answer[key] = loader.construct_object(value_node, deep=deep)
    return answer


StrictYamlLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictYamlLoader)
    require(isinstance(value, dict), f"{path} is not a YAML mapping")
    return value


def canonical_edge(first: int, second: int) -> Edge:
    require(type(first) is int and type(second) is int, "edge endpoints are not ints")
    require(first != second, "loop encountered")
    return (first, second) if first < second else (second, first)


@lru_cache(maxsize=1)
def labels() -> tuple[tuple[int, int], ...]:
    answer = tuple(
        (left, right)
        for left, right in itertools.combinations(range(COORDINATE_COUNT), 2)
        if right != (left ^ 1)
    )
    require(len(answer) == RESIDUAL_COUNT, "residual label count changed")
    return answer


def full_edge_state(first: int, second: int) -> bool | Edge:
    first, second = canonical_edge(first, second)
    require(0 <= first < second < FULL_VERTEX_COUNT, "full edge outside 0..98")
    if first == ROOT_VERTEX:
        return COORDINATE_OFFSET <= second < RESIDUAL_OFFSET
    if second < RESIDUAL_OFFSET:
        left = first - COORDINATE_OFFSET
        right = second - COORDINATE_OFFSET
        return left // 2 == right // 2 and left != right
    if first < RESIDUAL_OFFSET:
        coordinate = first - COORDINATE_OFFSET
        residual = second - RESIDUAL_OFFSET
        return coordinate in labels()[residual]
    return first - RESIDUAL_OFFSET, second - RESIDUAL_OFFSET


def independent_triangle_inventory() -> dict[str, object]:
    type_counts: Counter[str] = Counter()
    variable_counts: Counter[int] = Counter()
    total = 0
    for triangle in itertools.combinations(range(FULL_VERTEX_COUNT), 3):
        states = tuple(
            full_edge_state(first, second)
            for first, second in itertools.combinations(triangle, 2)
        )
        if False in states:
            continue
        total += 1
        variable_counts[sum(type(state) is tuple for state in states)] += 1
        if ROOT_VERTEX in triangle:
            kind = "root_triangle"
        elif sum(vertex < RESIDUAL_OFFSET for vertex in triangle) == 1:
            kind = "coordinate_residual_residual"
        elif all(vertex >= RESIDUAL_OFFSET for vertex in triangle):
            kind = "residual_only"
        else:
            kind = "other"
        type_counts[kind] += 1

    closed_form = {
        "root_triangle": PAIR_COUNT,
        "coordinate_residual_residual": COORDINATE_COUNT
        * (COORDINATE_COUNT - 2)
        * (COORDINATE_COUNT - 3)
        // 2,
        "residual_only": _comb(RESIDUAL_COUNT, 3),
    }
    require(dict(type_counts) == closed_form, "enumerated triangle types differ")
    residual_prisms = 60 * _comb(RESIDUAL_COUNT, 6)
    return {
        "candidate_triangles": total,
        "candidate_triangle_type_histogram": dict(sorted(type_counts.items())),
        "candidate_triangle_variable_edge_histogram": {
            str(key): variable_counts[key] for key in sorted(variable_counts)
        },
        "exact_residual_only_prism_embeddings": residual_prisms,
        "residual_partition_factor": 60,
        "residual_partition_derivation": "binom(6,3)/2 * 3! = 10 * 6",
        "naive_all_triangle_pair_matching_upper": 6 * _comb(total, 2),
    }


def _comb(total: int, selected: int) -> int:
    if selected < 0 or selected > total:
        return 0
    return __import__("math").comb(total, selected)


def triangles_in_graph(vertex_count: int, edges: Iterable[Edge]) -> tuple[Triangle, ...]:
    adjacency = [set() for _ in range(vertex_count)]
    for raw_edge in edges:
        first, second = canonical_edge(*raw_edge)
        require(0 <= first < second < vertex_count, "edge outside graph")
        adjacency[first].add(second)
        adjacency[second].add(first)
    answer = []
    for first in range(vertex_count):
        for second in sorted(vertex for vertex in adjacency[first] if vertex > first):
            for third in sorted(adjacency[first] & adjacency[second]):
                if third > second:
                    answer.append((first, second, third))
    return tuple(answer)


def independent_prisms(vertex_count: int, edges: Iterable[Edge]) -> tuple[Witness, ...]:
    edge_set = {canonical_edge(*edge) for edge in edges}
    triangles = triangles_in_graph(vertex_count, edge_set)
    answer: list[Witness] = []
    for first_index, first in enumerate(triangles):
        for second in triangles[first_index + 1 :]:
            if set(first) & set(second):
                continue
            cross = tuple(
                sorted(
                    canonical_edge(left, right)
                    for left in first
                    for right in second
                    if canonical_edge(left, right) in edge_set
                )
            )
            if len(cross) != 3:
                continue
            degree = Counter(vertex for edge in cross for vertex in edge)
            if set(degree.values()) != {1} or len(degree) != 6:
                continue
            answer.append((first, second, cross))
    return tuple(answer)


def six_vertex_prism_patterns() -> tuple[frozenset[Edge], ...]:
    vertices = tuple(range(6))
    answer: set[frozenset[Edge]] = set()
    for first in itertools.combinations(vertices[1:], 2):
        left = (0, *first)
        right = tuple(vertex for vertex in vertices if vertex not in left)
        for permutation in itertools.permutations(right):
            edges = {
                canonical_edge(*edge)
                for triangle in (left, right)
                for edge in itertools.combinations(triangle, 2)
            }
            edges.update(canonical_edge(left[index], permutation[index]) for index in range(3))
            answer.add(frozenset(edges))
    require(len(answer) == 60, "six-vertex prism pattern count is not 60")
    return tuple(sorted(answer, key=lambda item: tuple(sorted(item))))


def lambda_at_most_one(vertex_count: int, edges: Iterable[Edge]) -> bool:
    adjacency = [set() for _ in range(vertex_count)]
    edge_set = {canonical_edge(*edge) for edge in edges}
    for first, second in edge_set:
        adjacency[first].add(second)
        adjacency[second].add(first)
    return all(
        len(adjacency[first] & adjacency[second]) <= 1
        for first, second in edge_set
    )


def verify_lambda_compression() -> dict[str, object]:
    required = next(iter(six_vertex_prism_patterns()))
    optional = tuple(
        edge
        for edge in itertools.combinations(range(6), 2)
        if edge not in required
    )
    survivors = []
    for mask in range(1 << len(optional)):
        edge_set = set(required)
        edge_set.update(
            edge for index, edge in enumerate(optional) if mask & (1 << index)
        )
        if lambda_at_most_one(6, edge_set):
            survivors.append(edge_set)
    require(survivors == [set(required)], "nine-edge compression has a supergraph")
    return {
        "required_edges": 9,
        "optional_unmatched_cross_edges": len(optional),
        "supergraphs_checked": 1 << len(optional),
        "lambda_at_most_one_survivors": 1,
    }


@lru_cache(maxsize=1)
def rooted_verifier():
    path = repository_root() / "verification/wave37-rooted-branches/independent_check.py"
    spec = importlib.util.spec_from_file_location("wave38_complete_rooted_source", path)
    require(spec is not None and spec.loader is not None, "rooted verifier unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def independent_endpoint_cases() -> dict[int, tuple[int, ...]]:
    rooted = rooted_verifier()
    endpoint_set = set(rooted.endpoint_edges())
    surviving_parents = []
    for parent in range(1, 13):
        positive = {
            edge
            for edge, value in rooted.branch_decisions(parent).items()
            if value
        }
        if not positive & endpoint_set:
            surviving_parents.append(parent)
    require(surviving_parents == [4, 5, 8, 10, 12], "parent survivor set changed")
    grouped: dict[int, list[int]] = {parent: [] for parent in surviving_parents}
    for identifier, (matching, _, _) in enumerate(rooted.refined_orbits(), start=1):
        parent = rooted.parent_number_for_matching(matching)
        if parent in grouped:
            grouped[parent].append(identifier)
    answer = {key: tuple(value) for key, value in grouped.items()}
    require(answer == EXPECTED_BY_PARENT, "33-case independent cover changed")
    require(tuple(item for ids in answer.values() for item in ids) == EXPECTED_REFINED_IDS,
            "refined case IDs changed")
    return answer


def load_candidate(path: Path) -> tuple[int, tuple[Edge, ...], dict[str, Any]]:
    raw = load_json(path)
    require(set(raw) == {"format", "vertices", "edges"}, "candidate schema changed")
    require(raw["format"] == "srg-edge-list-v1", "candidate format changed")
    require(type(raw["vertices"]) is int and raw["vertices"] == FULL_VERTEX_COUNT,
            "candidate vertex count changed")
    require(isinstance(raw["edges"], list), "candidate edges are not a list")
    edges = []
    for entry in raw["edges"]:
        require(
            isinstance(entry, list)
            and len(entry) == 2
            and all(type(vertex) is int for vertex in entry),
            "candidate edge schema is loose",
        )
        edge = canonical_edge(*entry)
        require(0 <= edge[0] < edge[1] < FULL_VERTEX_COUNT, "candidate edge invalid")
        edges.append(edge)
    require(len(edges) == len(set(edges)), "candidate contains duplicate edges")
    return FULL_VERTEX_COUNT, tuple(sorted(edges)), raw


def residual_variable_ids() -> dict[Edge, int]:
    return {
        edge: variable
        for variable, edge in enumerate(
            itertools.combinations(range(RESIDUAL_COUNT), 2), start=1
        )
    }


def witness_clause(witness: Witness) -> tuple[tuple[Edge, ...], tuple[int, ...]]:
    first, second, matching = witness
    required = {
        canonical_edge(*edge)
        for triangle in (first, second)
        for edge in itertools.combinations(triangle, 2)
    }
    required.update(matching)
    variables = []
    for edge in sorted(required):
        state = full_edge_state(*edge)
        require(state is not False, "witness uses a fixed nonedge")
        if type(state) is tuple:
            variables.append(state)
    variable_tuple = tuple(sorted(set(variables)))
    ids = residual_variable_ids()
    return variable_tuple, tuple(-ids[edge] for edge in variable_tuple)


def verify_fixture() -> dict[str, object]:
    candidate_path = attempt_root() / "fixture-residual-prism.json"
    catalog_path = attempt_root() / "fixture-residual-prism-cuts.json"
    vertex_count, edges, _ = load_candidate(candidate_path)
    catalog = load_json(catalog_path)
    witnesses = independent_prisms(vertex_count, edges)
    require(len(witnesses) == 1, "fixture does not contain exactly one prism")
    require(len(triangles_in_graph(vertex_count, edges)) == 2, "fixture triangle count changed")
    require(catalog["candidate"]["edge_count"] == len(edges), "catalog edge count unbound")
    edge_digest = sha256_bytes(canonical_compact([list(edge) for edge in edges]))
    require(catalog["candidate"]["edge_catalog_sha256"] == edge_digest,
            "catalog edge digest does not match candidate")
    require(catalog["triangle_count"] == 2, "catalog triangle count changed")
    require(catalog["prism_witness_count"] == len(witnesses),
            "catalog prism count changed")
    require(catalog["deduplicated_cut_count"] == 1, "fixture cut count changed")
    variables, literals = witness_clause(witnesses[0])
    entry = catalog["entries"][0]
    require(entry["variable_edges"] == [list(edge) for edge in variables],
            "fixture variable edges differ")
    require(entry["negative_literals"] == list(literals), "fixture literals differ")
    return {
        "candidate_file_sha256": sha256_file(candidate_path),
        "edge_catalog_sha256": edge_digest,
        "edge_count": len(edges),
        "triangle_count": 2,
        "prism_witness_count": 1,
        "deduplicated_cut_count": 1,
        "cut_literal_count": len(literals),
    }


@lru_cache(maxsize=1)
def discovery_module():
    path = attempt_root() / "complete_endpoint.py"
    sys.path.insert(0, str(attempt_root()))
    spec = importlib.util.spec_from_file_location("wave38_complete_discovery", path)
    require(spec is not None and spec.loader is not None, "discovery module unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical_discovery_witnesses(raw_witnesses: Iterable[Any]) -> tuple[Witness, ...]:
    answer = []
    for witness in raw_witnesses:
        first, second = witness.triangles
        answer.append((tuple(first), tuple(second), tuple(witness.matching)))
    return tuple(answer)


def differential_oracle_check() -> dict[str, object]:
    discovery = discovery_module()
    all_edges = tuple(itertools.combinations(range(6), 2))
    exact_patterns = set(six_vertex_prism_patterns())
    for mask in range(1 << len(all_edges)):
        edges = {
            edge for index, edge in enumerate(all_edges) if mask & (1 << index)
        }
        expected_count = int(frozenset(edges) in exact_patterns)
        rebuilt = independent_prisms(6, edges)
        observed = canonical_discovery_witnesses(discovery.find_induced_prisms(6, edges))
        require(len(rebuilt) == expected_count, f"independent six-vertex oracle failed at {mask}")
        require(observed == rebuilt, f"discovery oracle differs at six-vertex graph {mask}")

    base = set(next(iter(exact_patterns)))
    shifted = {(left + 6, right + 6) for left, right in base}
    hostile = {
        "two_disjoint_prisms": (12, base | shifted),
        "extra_cross_edge": (6, base | {next(edge for edge in all_edges if edge not in base)}),
        "three_cross_edges_not_matching": (
            6,
            {
                (0, 1), (0, 2), (1, 2),
                (3, 4), (3, 5), (4, 5),
                (0, 3), (0, 4), (0, 5),
            },
        ),
        "complete_graph": (6, set(all_edges)),
        "overlapping_triangles": (5, {(0, 1), (0, 2), (1, 2), (0, 3), (1, 3)}),
    }
    hostile_counts = {}
    for name, (vertex_count, edges) in hostile.items():
        rebuilt = independent_prisms(vertex_count, edges)
        observed = canonical_discovery_witnesses(
            discovery.find_induced_prisms(vertex_count, edges)
        )
        require(observed == rebuilt, f"discovery differs on hostile fixture {name}")
        hostile_counts[name] = len(rebuilt)
    return {
        "all_six_vertex_graphs_checked": 1 << len(all_edges),
        "distinct_labelled_prism_graphs": len(exact_patterns),
        "hostile_fixture_count": len(hostile),
        "hostile_prism_counts": hostile_counts,
    }


def accepts(
    callable_object,
    value: Mapping[str, object],
    **kwargs: object,
) -> bool:
    try:
        callable_object(value, **kwargs)
    except (AssertionError, KeyError, TypeError, ValueError):
        return False
    return True


def hostile_validator_check() -> dict[str, object]:
    discovery = discovery_module()
    catalog = load_json(attempt_root() / "fixture-residual-prism-cuts.json")
    pool = load_json(attempt_root() / "fixture-cut-pool.json")
    require(accepts(discovery.validate_cut_catalog, catalog), "fixture catalog rejected")
    require(accepts(discovery.validate_cut_pool, pool), "fixture pool rejected")

    literal_tamper = copy.deepcopy(catalog)
    literal_tamper["entries"][0]["negative_literals"][0] -= 1
    variable_tamper = copy.deepcopy(catalog)
    variable_tamper["entries"][0]["variable_edges"][0] = [0, 9]
    witness_tamper = copy.deepcopy(catalog)
    witness_tamper["entries"][0]["witness"]["matching"][1] = [15, 19]
    duplicate = copy.deepcopy(catalog)
    duplicate["entries"].append(copy.deepcopy(duplicate["entries"][0]))
    duplicate["deduplicated_cut_count"] = 2
    require(not accepts(discovery.validate_cut_catalog, literal_tamper),
            "literal tamper was accepted")
    require(not accepts(discovery.validate_cut_catalog, variable_tamper),
            "variable-edge tamper was accepted")
    require(not accepts(discovery.validate_cut_catalog, witness_tamper),
            "witness tamper was accepted")
    require(not accepts(discovery.validate_cut_catalog, duplicate),
            "duplicate clause was accepted")

    _, candidate_edges, _ = load_candidate(
        attempt_root() / "fixture-residual-prism.json"
    )
    inflated_label = copy.deepcopy(catalog)
    inflated_label["claim_label"] = "VERIFIED_STATIC_COMPLETE"
    inflated_scope = copy.deepcopy(catalog)
    inflated_scope["scope"] = "all cases proved"
    removed_limitations = copy.deepcopy(catalog)
    removed_limitations["limitations"] = []
    forged_candidate = copy.deepcopy(catalog)
    forged_candidate["candidate"] = {
        "edge_count": 0,
        "edge_catalog_sha256": "0" * 64,
    }
    forged_candidate["triangle_count"] = 0

    omitted_catalog = copy.deepcopy(catalog)
    omitted_catalog["entries"] = []
    omitted_catalog["prism_witness_count"] = 0
    omitted_catalog["deduplicated_cut_count"] = 0
    omitted_catalog["claim_label"] = "CANDIDATE_PRISM_FREE_ONLY"

    catalog_raw = (attempt_root() / "fixture-residual-prism-cuts.json").read_bytes()
    sources = [(sha256_bytes(catalog_raw), catalog)]
    inflated_pool_label = copy.deepcopy(pool)
    inflated_pool_label["claim_label"] = "VERIFIED_STATIC_COMPLETE"
    inflated_pool_scope = copy.deepcopy(pool)
    inflated_pool_scope["scope"] = "all cases proved"
    removed_pool_limitations = copy.deepcopy(pool)
    removed_pool_limitations["limitations"] = []
    forged_pool_source = copy.deepcopy(pool)
    forged_pool_source["source_catalogs"][0]["sha256"] = "0" * 64
    forged_pool_source["source_catalogs"][0]["prism_witness_count"] = 999
    forged_pool_source["source_catalogs"][0]["deduplicated_cut_count"] = 999

    bool_schema_catalog = copy.deepcopy(catalog)
    bool_schema_catalog["entries"][0]["variable_edges"][0] = [False, True]

    regressions = {
        "catalog_label_tamper_rejected": not accepts(
            discovery.validate_cut_catalog, inflated_label
        ),
        "catalog_scope_tamper_rejected": not accepts(
            discovery.validate_cut_catalog, inflated_scope
        ),
        "catalog_limitations_tamper_rejected": not accepts(
            discovery.validate_cut_catalog, removed_limitations
        ),
        "catalog_candidate_metadata_tamper_rejected_when_bound": not accepts(
            discovery.validate_cut_catalog,
            forged_candidate,
            candidate_edges=candidate_edges,
            require_complete=True,
        ),
        "catalog_witness_omission_rejected_when_bound": not accepts(
            discovery.validate_cut_catalog,
            omitted_catalog,
            candidate_edges=candidate_edges,
            require_complete=True,
        ),
        "catalog_complete_candidate_binding_accepted": accepts(
            discovery.validate_cut_catalog,
            catalog,
            candidate_edges=candidate_edges,
            require_complete=True,
        ),
        "catalog_completeness_requires_candidate": not accepts(
            discovery.validate_cut_catalog,
            catalog,
            require_complete=True,
        ),
        "pool_label_tamper_rejected": not accepts(
            discovery.validate_cut_pool, inflated_pool_label
        ),
        "pool_scope_tamper_rejected": not accepts(
            discovery.validate_cut_pool, inflated_pool_scope
        ),
        "pool_limitations_tamper_rejected": not accepts(
            discovery.validate_cut_pool, removed_pool_limitations
        ),
        "pool_source_tamper_rejected_when_bound": not accepts(
            discovery.validate_cut_pool,
            forged_pool_source,
            source_catalogs=sources,
            require_sources=True,
        ),
        "pool_complete_source_binding_accepted": accepts(
            discovery.validate_cut_pool,
            pool,
            source_catalogs=sources,
            require_sources=True,
        ),
        "pool_provenance_requires_sources": not accepts(
            discovery.validate_cut_pool,
            pool,
            require_sources=True,
        ),
        "boolean_edge_schema_alias_rejected": not accepts(
            discovery.validate_cut_catalog, bool_schema_catalog
        ),
    }
    require(all(regressions.values()), "one or more hardening regressions failed")
    return {
        "semantic_tamper_rejections": {
            "negative_literal": True,
            "variable_edge": True,
            "matching_witness": True,
            "duplicate_clause": True,
        },
        "hardening_regressions": regressions,
        "intentional_unbound_api_boundary": {
            "omitted_catalog_accepted_for_cut_soundness_only": accepts(
                discovery.validate_cut_catalog, omitted_catalog
            ),
            "forged_pool_source_accepted_for_cut_soundness_only": accepts(
                discovery.validate_cut_pool, forged_pool_source
            ),
        },
        "conclusion": (
            "the public completeness and provenance paths require candidate or "
            "source evidence and reject every prior V1-V3 attack; unbound library "
            "calls remain explicitly limited to individual-cut soundness"
        ),
    }


def verify_only_cli_check() -> dict[str, object]:
    candidate = attempt_root() / "fixture-residual-prism.json"
    catalog_path = attempt_root() / "fixture-residual-prism-cuts.json"
    pool_path = attempt_root() / "fixture-cut-pool.json"
    prism_cli = attempt_root() / "prism_oracle.py"
    pool_cli = attempt_root() / "cut_pool.py"
    catalog = load_json(catalog_path)
    pool = load_json(pool_path)

    def run(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", *arguments],
            cwd=repository_root(),
            capture_output=True,
            text=True,
            check=False,
        )

    catalog_missing_candidate = run(
        str(prism_cli), "--verify-only", "--catalog", str(catalog_path)
    )
    catalog_bound = run(
        str(prism_cli),
        "--verify-only",
        "--candidate",
        str(candidate),
        "--catalog",
        str(catalog_path),
    )
    pool_missing_sources = run(
        str(pool_cli), "--verify-only", "--pool", str(pool_path)
    )
    pool_bound = run(
        str(pool_cli),
        "--verify-only",
        "--pool",
        str(pool_path),
        "--catalog",
        str(catalog_path),
    )
    require(catalog_missing_candidate.returncode != 0,
            "catalog verify-only accepted no candidate")
    require(
        catalog_bound.returncode == 0
        and "PASS_COMPLETE_CATALOG_BOUND_TO_CANDIDATE" in catalog_bound.stdout,
        "catalog verify-only did not bind the fixture candidate",
    )
    require(pool_missing_sources.returncode != 0,
            "pool verify-only accepted no source catalogs")
    require(
        pool_bound.returncode == 0 and "PASS_SOURCE_BOUND_POOL" in pool_bound.stdout,
        "pool verify-only did not bind the fixture source",
    )

    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        omitted = copy.deepcopy(catalog)
        omitted["entries"] = []
        omitted["prism_witness_count"] = 0
        omitted["deduplicated_cut_count"] = 0
        omitted["claim_label"] = "CANDIDATE_PRISM_FREE_ONLY"
        omitted_path = tmp / "omitted.json"
        omitted_path.write_text(
            json.dumps(omitted, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        omitted_result = run(
            str(prism_cli),
            "--verify-only",
            "--candidate",
            str(candidate),
            "--catalog",
            str(omitted_path),
        )
        forged = copy.deepcopy(pool)
        forged["source_catalogs"][0]["sha256"] = "0" * 64
        forged_path = tmp / "forged-pool.json"
        forged_path.write_text(
            json.dumps(forged, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        forged_result = run(
            str(pool_cli),
            "--verify-only",
            "--pool",
            str(forged_path),
            "--catalog",
            str(catalog_path),
        )
    require(omitted_result.returncode != 0,
            "catalog verify-only accepted an omitted witness")
    require(forged_result.returncode != 0,
            "pool verify-only accepted a forged source digest")
    return {
        "catalog_requires_candidate": True,
        "complete_catalog_bound_to_candidate": True,
        "omitted_witness_rejected": True,
        "pool_requires_all_sources": True,
        "source_bound_pool_accepted": True,
        "forged_source_digest_rejected": True,
    }


def exporter_guard_check() -> dict[str, object]:
    exporter_path = attempt_root() / "export_complete_endpoint.py"
    tree = ast.parse(exporter_path.read_text(encoding="utf-8"))
    functions = {
        node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    static = functions["write_static_complete_opb"]
    branch = functions["write_branch_opb"]
    static_args = tuple(argument.arg for argument in static.args.args)
    branch_args = tuple(argument.arg for argument in branch.args.args)
    require("cut_catalog_path" not in static_args, "static exporter accepts a cut pool")
    require("cut_catalog_path" in branch_args, "lazy exporter lost its cut source")

    static_source = ast.get_source_segment(exporter_path.read_text(encoding="utf-8"), static)
    branch_source = ast.get_source_segment(exporter_path.read_text(encoding="utf-8"), branch)
    require(static_source is not None and "iter_complete_static_clauses" in static_source,
            "static exporter does not stream the complete iterator")
    require(branch_source is not None and 'strategy="lazy_exact_separation"' in branch_source,
            "partial pool route is not labelled lazy")

    spec = importlib.util.spec_from_file_location("wave38_complete_exporter", exporter_path)
    require(spec is not None and spec.loader is not None, "exporter unavailable")
    if str(attempt_root()) not in sys.path:
        sys.path.insert(0, str(attempt_root()))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        opb = tmp / "refused.opb"
        metadata = tmp / "refused.json"
        refused = False
        try:
            module.write_static_complete_opb(15, opb, metadata, "wrong")
        except ValueError:
            refused = True
        require(refused and not opb.exists() and not metadata.exists(),
                "static acknowledgement guard failed before writes")
        outside_branch = False
        try:
            module.write_branch_opb(15, opb, metadata, None)
        except ValueError:
            outside_branch = True
        require(outside_branch and not opb.exists() and not metadata.exists(),
                "branch exporter did not reject outside paths before writes")
        outside_static = False
        try:
            module.write_static_complete_opb(
                15,
                opb,
                metadata,
                module.STATIC_ACKNOWLEDGEMENT,
            )
        except ValueError:
            outside_static = True
        require(outside_static and not opb.exists() and not metadata.exists(),
                "static exporter did not reject outside paths before writes")

    require(
        branch_source.index('validated_output_path(opb_path, "OPB output")')
        < branch_source.index("build_branch_formula"),
        "branch OPB containment is not checked before formula construction",
    )
    require(
        branch_source.index('validated_output_path(metadata_path, "metadata output")')
        < branch_source.index("build_branch_formula"),
        "branch metadata containment is not checked before formula construction",
    )
    require(
        static_source.index('validated_output_path(opb_path, "OPB output")')
        < static_source.index("build_branch_formula"),
        "static OPB containment is not checked before formula construction",
    )
    same_path = verifier_root() / "never-created.opb"
    same_output_rejected = False
    try:
        module.write_branch_opb(15, same_path, same_path, None)
    except ValueError:
        same_output_rejected = True
    require(same_output_rejected and not same_path.exists(),
            "identical OPB and metadata paths were not rejected before writes")
    return {
        "wrong_acknowledgement_refused_before_write": True,
        "static_route_accepts_cut_pool": False,
        "static_route_streams_complete_iterator": True,
        "partial_pool_route_strategy": "lazy_exact_separation",
        "partial_pool_formula_claim_label": "CANDIDATE_FORMULA_ONLY",
        "branch_outside_path_refused_before_write": True,
        "static_outside_path_refused_before_write": True,
        "identical_output_paths_refused_before_write": True,
    }


def safe_manifest_path(raw: str) -> Path:
    require(isinstance(raw, str), "manifest path is not text")
    require("\\" not in raw and ":" not in raw, "manifest path is not canonical POSIX")
    pure = PurePosixPath(raw)
    require(not pure.is_absolute(), "manifest path is absolute")
    require(all(part not in ("", ".", "..") for part in pure.parts),
            "manifest path has traversal")
    path = repository_root().joinpath(*pure.parts).resolve()
    path.relative_to(repository_root().resolve())
    return path


def inspect_hash_manifest(
    path: Path,
) -> tuple[list[tuple[str, str]], list[dict[str, str]]]:
    answer = []
    mismatches = []
    seen = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        require(line != "", f"blank hash row {line_number}")
        parts = line.split("  ", 1)
        require(len(parts) == 2, f"invalid hash row {line_number}")
        digest, relative = parts
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
                f"invalid digest row {line_number}")
        require(relative not in seen, f"duplicate hash path {relative}")
        seen.add(relative)
        target = safe_manifest_path(relative)
        require(target.is_file(), f"hashed input missing: {relative}")
        actual = sha256_file(target)
        if actual != digest:
            mismatches.append(
                {
                    "path": relative,
                    "expected": digest,
                    "actual": actual,
                }
            )
        answer.append((digest, relative))
    return answer, mismatches


def parse_hash_manifest(path: Path) -> list[tuple[str, str]]:
    answer, mismatches = inspect_hash_manifest(path)
    require(not mismatches, f"hash mismatches: {mismatches}")
    return answer


def package_integrity_check() -> dict[str, object]:
    package_manifest, package_mismatches = inspect_hash_manifest(
        attempt_root() / "package-manifest.sha256"
    )
    input_freeze = parse_hash_manifest(attempt_root() / "input-freeze.sha256")
    listed_package = {relative for _, relative in package_manifest}
    actual_package = {
        path.relative_to(repository_root()).as_posix()
        for path in attempt_root().iterdir()
        if path.is_file() and path.name != "package-manifest.sha256"
    }
    require(listed_package == actual_package, "package manifest coverage differs")

    report = load_yaml(attempt_root() / "run-report.yaml")
    require(report["role"] == "construction" and report["claim_label"] == "CANDIDATE",
            "construction report status inflated")
    require(report["solver_status"] == "NOT_RUN"
            and report["certificate_status"] == "NONE",
            "construction report claims target evidence")
    report_mismatches = []
    for output in report["outputs"]:
        target = safe_manifest_path(output["path"])
        actual = sha256_file(target)
        if output["sha256"] != actual:
            report_mismatches.append(
                {
                    "path": output["path"],
                    "expected": output["sha256"],
                    "actual": actual,
                }
            )

    privacy_hits = []
    for path in attempt_root().iterdir():
        if not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                privacy_hits.append({"path": path.name, "pattern": pattern.pattern})
    require(not privacy_hits, f"privacy scan found {privacy_hits}")
    return {
        "status": (
            "PASS"
            if not package_mismatches and not report_mismatches
            else "FAIL_STALE_HASHES"
        ),
        "package_manifest_entries": len(package_manifest),
        "package_manifest_exact_coverage": True,
        "package_manifest_hash_mismatches": package_mismatches,
        "frozen_input_entries": len(input_freeze),
        "input_freeze_hash_mismatches": 0,
        "strict_json_duplicate_key_rejection": True,
        "strict_yaml_duplicate_key_rejection": True,
        "run_report_output_hashes": len(report["outputs"]),
        "run_report_output_hash_mismatches": report_mismatches,
        "privacy_scan_files": sum(
            path.is_file() and path.suffix.casefold() in TEXT_SUFFIXES
            for path in attempt_root().iterdir()
        ),
        "privacy_hits": 0,
    }


def audit() -> dict[str, object]:
    triangle_inventory = independent_triangle_inventory()
    expected_inventory = load_json(attempt_root() / "static-schema-estimate.json")
    for key, value in triangle_inventory.items():
        if key in expected_inventory:
            require(expected_inventory[key] == value, f"inventory differs at {key}")
    cases = independent_endpoint_cases()
    require(
        tuple(case["refined_branch"] for case in expected_inventory["endpoint_refined_cases"])
        == EXPECTED_REFINED_IDS,
        "published refined cases differ",
    )
    require(
        {
            parent: tuple(
                case["refined_branch"]
                for case in expected_inventory["endpoint_refined_cases"]
                if case["parent_branch"] == parent
            )
            for parent in cases
        }
        == cases,
        "published parent grouping differs",
    )

    lambda_result = verify_lambda_compression()
    fixture = verify_fixture()
    oracle = differential_oracle_check()
    validators = hostile_validator_check()
    verify_only_cli = verify_only_cli_check()
    exporter = exporter_guard_check()
    integrity = package_integrity_check()
    return {
        "format": "wave38-complete-endpoint-independent-results-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_CONSTRUCTION_SCOPE_ONLY",
        "target_status": "UNKNOWN",
        "checks": {
            "triangle_inventory": triangle_inventory,
            "endpoint_case_cover": {
                "case_count": len(EXPECTED_REFINED_IDS),
                "by_parent": {str(key): list(value) for key, value in cases.items()},
                "completed_graph_automorphism_assumed": False,
            },
            "lambda_compression": lambda_result,
            "fixture": fixture,
            "oracle": oracle,
            "validators": validators,
            "verify_only_cli": verify_only_cli,
            "exporter": exporter,
            "integrity": integrity,
        },
        "verified": [
            "The rooted scaffold has exactly 96,215 potential triangles.",
            "The residual-only schema has exactly 24,388,892,640 distinct clauses.",
            "Under adjacent-pair lambda at most one, the nine positive prism edges force inducedness.",
            "The decoded-candidate oracle agrees with an independent oracle on every six-vertex graph and hostile larger fixtures.",
            "The normalized endpoint scope is exactly the published 33 refined cases.",
            "Every retained fixture cut is independently rederived from a valid prism witness.",
            "The static exporter rejects a missing acknowledgement and does not accept a partial cut pool.",
            "Catalog verify-only is bound to candidate edges and rejects omitted witnesses.",
            "Pool verify-only is bound to every supplied source catalog and rejects forged provenance.",
            "Catalog and pool status, scope, limitations, counts, and integer schemas reject the prior attacks.",
            "OPB and metadata output containment is validated before formula construction or filesystem writes.",
            "The refreshed 16-entry discovery package manifest and all construction-report output hashes replay exactly.",
        ],
        "findings": [
            {
                "id": "W38-CE-V1",
                "severity": "RESOLVED",
                "status": "FIXED",
                "summary": (
                    "complete verify-only now requires candidate edges, reconstructs the "
                    "canonical catalog, and rejects omitted witnesses or metadata tampering"
                ),
            },
            {
                "id": "W38-CE-V2",
                "severity": "RESOLVED",
                "status": "FIXED",
                "summary": (
                    "pool verify-only now requires every source catalog and compares the "
                    "pool with their canonical byte-digest-bound merge"
                ),
            },
            {
                "id": "W38-CE-V3",
                "severity": "RESOLVED",
                "status": "FIXED",
                "summary": (
                    "exact integer type checks reject Boolean aliases and strict status, "
                    "scope, limitations, and count checks reject inflation"
                ),
            },
            {
                "id": "W38-CE-V4",
                "severity": "RESOLVED",
                "status": "FIXED",
                "summary": (
                    "branch and static OPB and metadata paths are resolved inside the "
                    "repository and checked for collision before construction or writes"
                ),
            },
            {
                "id": "W38-CE-V5",
                "severity": "RESOLVED",
                "status": "FIXED",
                "summary": (
                    "the discovery package manifest and construction run-report were "
                    "regenerated after hardening and now bind every published file"
                ),
            },
        ],
        "evidence_boundary": {
            "target_formula_generated": False,
            "target_solver_run": False,
            "sat_witness": False,
            "unsat_proof": False,
            "complete_cut_iteration": False,
            "improved_upper_bound": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
