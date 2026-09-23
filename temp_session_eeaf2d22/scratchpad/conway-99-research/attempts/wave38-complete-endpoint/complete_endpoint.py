#!/usr/bin/env python3
"""Exact all-prism primitives for the Wave 38 endpoint construction.

The rooted model has 99 full vertices:

* vertex 0 is the normalized root;
* vertices 1..14 are its coordinate neighbors; and
* vertices 15..98 are the 84 residual vertices labelled by non-mate
  coordinate pairs.

This module does not solve the Conway problem.  It supplies two exact ways to
enforce the conditional endpoint ``P=0``:

1. a static streaming schema that emits a blocking clause for every labelled
   triangular-prism embedding compatible with the rooted scaffold; and
2. an exhaustive candidate oracle that finds every induced triangular prism
   in a decoded graph and emits independently checkable lazy cuts.

The static schema is complete but enormous.  The lazy route is a complete
finite solve-cut-check procedure only when iteration continues until a checked
prism-free SAT witness or a checked UNSAT proof is obtained.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CODE_ROOT = REPOSITORY_ROOT / "code"
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from matching_orbits import (  # noqa: E402
    n3_refined_branch_specification,
    n3_refined_orbits,
)
from root_model import RootModel  # noqa: E402


ROOT_VERTEX = 0
COORDINATE_OFFSET = 1
RESIDUAL_OFFSET = 15
FULL_VERTEX_COUNT = 99
RESIDUAL_VERTEX_COUNT = 84
SURVIVING_PARENTS = (4, 5, 8, 10, 12)
MATCHING_PERMUTATIONS = tuple(itertools.permutations(range(3)))
FORMAT = "wave38-complete-endpoint-schema-v1"
CATALOG_SCOPE = "all induced triangular prisms in one decoded 99-vertex candidate"
CATALOG_LIMITATIONS = (
    "A zero-prism candidate still requires independent SRG verification.",
    "Cuts describe one candidate iteration, not a terminal search.",
    "UNSAT counts only with a retained independently checked proof.",
)
POOL_SCOPE = "cumulative exact prism cuts from decoded endpoint candidates"
POOL_LIMITATIONS = (
    "The pool is not a complete formula unless a terminal check is reached.",
    "UNSAT requires a retained independently checked proof.",
    "A zero-prism SAT candidate requires independent full-SRG verification.",
)

VariableEdge = tuple[int, int]
FullEdge = tuple[int, int]
EdgeState = bool | VariableEdge


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_edge(first: int, second: int) -> FullEdge:
    if type(first) is not int or type(second) is not int:
        raise TypeError("edge endpoints must be integers")
    if first == second:
        raise ValueError("loops are not graph edges")
    return (first, second) if first < second else (second, first)


def rooted_edge_state(root: RootModel, first: int, second: int) -> EdgeState:
    """Return fixed truth or the residual-variable key of a full edge."""

    first, second = canonical_edge(first, second)
    if not 0 <= first < second < FULL_VERTEX_COUNT:
        raise ValueError("full edge endpoint is outside 0..98")

    if first == ROOT_VERTEX:
        return COORDINATE_OFFSET <= second < RESIDUAL_OFFSET

    if first < RESIDUAL_OFFSET and second < RESIDUAL_OFFSET:
        first_coordinate = first - COORDINATE_OFFSET
        second_coordinate = second - COORDINATE_OFFSET
        return (
            first_coordinate // 2 == second_coordinate // 2
            and first_coordinate != second_coordinate
        )

    if first < RESIDUAL_OFFSET:
        coordinate = first - COORDINATE_OFFSET
        label_index = second - RESIDUAL_OFFSET
        return coordinate in root.labels[label_index]

    return (
        first - RESIDUAL_OFFSET,
        second - RESIDUAL_OFFSET,
    )


def residual_variable_ids() -> dict[VariableEdge, int]:
    """Reproduce the first IDPool block in ``EncodedRootModel.build``."""

    return {
        edge: variable
        for variable, edge in enumerate(
            itertools.combinations(range(RESIDUAL_VERTEX_COUNT), 2),
            start=1,
        )
    }


def possible_triangle(root: RootModel, vertices: Sequence[int]) -> bool:
    if len(vertices) != 3 or len(set(vertices)) != 3:
        raise ValueError("a triangle needs three distinct vertices")
    return all(
        rooted_edge_state(root, first, second) is not False
        for first, second in itertools.combinations(sorted(vertices), 2)
    )


def potential_triangles(root: RootModel) -> tuple[tuple[int, int, int], ...]:
    """List every full-vertex triple not killed by a fixed scaffold nonedge."""

    return tuple(
        triangle
        for triangle in itertools.combinations(range(FULL_VERTEX_COUNT), 3)
        if possible_triangle(root, triangle)
    )


def prism_required_edges(
    first_triangle: Sequence[int],
    second_triangle: Sequence[int],
    matching_permutation: Sequence[int],
) -> tuple[FullEdge, ...]:
    """Return the nine positive edges of one labelled prism orientation."""

    first = tuple(sorted(first_triangle))
    second = tuple(sorted(second_triangle))
    permutation = tuple(matching_permutation)
    if len(first) != 3 or len(set(first)) != 3:
        raise ValueError("first triangle must contain three distinct vertices")
    if len(second) != 3 or len(set(second)) != 3:
        raise ValueError("second triangle must contain three distinct vertices")
    if set(first).intersection(second):
        raise ValueError("the two prism triangles must be disjoint")
    if sorted(permutation) != [0, 1, 2]:
        raise ValueError("matching permutation must permute 0,1,2")

    edges = {
        canonical_edge(*edge)
        for edge in itertools.combinations(first, 2)
    }
    edges.update(
        canonical_edge(*edge)
        for edge in itertools.combinations(second, 2)
    )
    edges.update(
        canonical_edge(first[index], second[permutation[index]])
        for index in range(3)
    )
    if len(edges) != 9:
        raise AssertionError("a prism pattern must have nine distinct edges")
    return tuple(sorted(edges))


def prism_variable_keys(
    root: RootModel,
    first_triangle: Sequence[int],
    second_triangle: Sequence[int],
    matching_permutation: Sequence[int],
) -> tuple[VariableEdge, ...] | None:
    """Return the variable part of a prism clause, or ``None`` if impossible."""

    variables: set[VariableEdge] = set()
    for edge in prism_required_edges(
        first_triangle, second_triangle, matching_permutation
    ):
        state = rooted_edge_state(root, *edge)
        if state is False:
            return None
        if state is not True:
            variables.add(state)
    if not variables:
        raise AssertionError("the fixed rooted scaffold already contains a prism")
    return tuple(sorted(variables))


def simplify_negative_clause(
    variable_keys: Sequence[VariableEdge],
    variable_ids: Mapping[VariableEdge, int],
    fixed_assignments: Mapping[int, bool],
) -> tuple[int, ...] | None:
    """Simplify ``OR(not x_e)`` under fixed assignments.

    ``None`` means that a fixed-false variable already satisfies the clause.
    The empty tuple means that every variable was fixed true and the branch is
    immediately contradictory.
    """

    active: list[int] = []
    for key in variable_keys:
        variable = variable_ids[key]
        assignment = fixed_assignments.get(variable)
        if assignment is False:
            return None
        if assignment is None:
            active.append(-variable)
    return tuple(sorted(set(active), key=abs))


def iter_complete_static_clauses(
    root: RootModel,
    fixed_assignments: Mapping[int, bool] | None = None,
) -> Iterator[tuple[int, ...]]:
    """Stream a complete all-prism CNF family.

    Triangle pairs are unordered and each of their six perfect matchings is
    visited exactly once.  A yielded clause is a disjunction of negative
    residual-edge literals.  Duplicate simplified clauses are intentionally
    permitted; removing them would require unbounded catalog memory and is not
    needed for soundness or completeness.
    """

    assignments = fixed_assignments or {}
    variables = residual_variable_ids()
    triangles = potential_triangles(root)
    for first_index, first_triangle in enumerate(triangles):
        first_vertices = frozenset(first_triangle)
        for second_triangle in triangles[first_index + 1 :]:
            if first_vertices.intersection(second_triangle):
                continue
            for permutation in MATCHING_PERMUTATIONS:
                keys = prism_variable_keys(
                    root,
                    first_triangle,
                    second_triangle,
                    permutation,
                )
                if keys is None:
                    continue
                clause = simplify_negative_clause(keys, variables, assignments)
                if clause is not None:
                    yield clause


def endpoint_refined_cases(root: RootModel | None = None) -> tuple[dict[str, int], ...]:
    """Return the exact 33 endpoint-compatible refined cases."""

    actual_root = root or RootModel.build(7)
    cases: list[dict[str, int]] = []
    for branch in range(1, len(n3_refined_orbits()) + 1):
        _, _, parent = n3_refined_branch_specification(actual_root, branch)
        if parent in SURVIVING_PARENTS:
            cases.append({"refined_branch": branch, "parent_branch": parent})
    if len(cases) != 33:
        raise AssertionError(f"expected 33 endpoint cases, found {len(cases)}")
    return tuple(cases)


def static_size_inventory(root: RootModel | None = None) -> dict[str, object]:
    """Return exact cheap counts and honest lower/upper static-size bounds."""

    actual_root = root or RootModel.build(7)
    triangles = potential_triangles(actual_root)
    variable_edge_histogram: dict[int, int] = {}
    vertex_type_histogram: dict[str, int] = {}
    for triangle in triangles:
        variable_count = sum(
            rooted_edge_state(actual_root, *edge) is not True
            for edge in itertools.combinations(triangle, 2)
        )
        variable_edge_histogram[variable_count] = (
            variable_edge_histogram.get(variable_count, 0) + 1
        )
        if ROOT_VERTEX in triangle:
            kind = "root_triangle"
        elif sum(vertex < RESIDUAL_OFFSET for vertex in triangle) == 1:
            kind = "coordinate_residual_residual"
        elif all(vertex >= RESIDUAL_OFFSET for vertex in triangle):
            kind = "residual_only"
        else:
            kind = "other"
        vertex_type_histogram[kind] = vertex_type_histogram.get(kind, 0) + 1

    residual_only_prism_embeddings = 60 * _comb(RESIDUAL_VERTEX_COUNT, 6)
    naive_pair_matching_upper = 6 * _comb(len(triangles), 2)
    cases = endpoint_refined_cases(actual_root)
    return {
        "format": "wave38-complete-endpoint-static-size-v1",
        "claim_label": "DERIVED_SIZE_BOUND_ONLY",
        "full_vertices": FULL_VERTEX_COUNT,
        "residual_vertices": RESIDUAL_VERTEX_COUNT,
        "candidate_triangles": len(triangles),
        "candidate_triangle_variable_edge_histogram": {
            str(key): variable_edge_histogram[key]
            for key in sorted(variable_edge_histogram)
        },
        "candidate_triangle_type_histogram": dict(
            sorted(vertex_type_histogram.items())
        ),
        "exact_residual_only_prism_embeddings": residual_only_prism_embeddings,
        "naive_all_triangle_pair_matching_upper": naive_pair_matching_upper,
        "endpoint_refined_case_count": len(cases),
        "endpoint_refined_cases": list(cases),
        "interpretation": [
            (
                "The residual-only count is an exact subset of the static "
                "labelled prism schema, before branch simplification."
            ),
            (
                "The all-pair value is an upper bound because it includes "
                "intersecting triangle pairs and scaffold-incompatible matchings."
            ),
            (
                "These counts explain why the complete static formula must be "
                "streamed and why lazy exact separation is the practical route."
            ),
        ],
    }


def _comb(total: int, selected: int) -> int:
    if selected < 0 or selected > total:
        return 0
    numerator = 1
    denominator = 1
    for offset in range(selected):
        numerator *= total - offset
        denominator *= offset + 1
    return numerator // denominator


@dataclass(frozen=True)
class PrismWitness:
    triangles: tuple[tuple[int, int, int], tuple[int, int, int]]
    matching: tuple[FullEdge, FullEdge, FullEdge]

    def __post_init__(self) -> None:
        first, second = self.triangles
        if (
            len(first) != 3
            or len(set(first)) != 3
            or len(second) != 3
            or len(set(second)) != 3
            or set(first).intersection(second)
        ):
            raise ValueError("a prism witness needs two disjoint triples")
        if tuple(sorted(first)) != first or tuple(sorted(second)) != second:
            raise ValueError("witness triangles must be sorted")
        if tuple(sorted(self.matching)) != self.matching:
            raise ValueError("witness matching edges must be sorted")
        first_set = set(first)
        second_set = set(second)
        degrees = {vertex: 0 for vertex in (*first, *second)}
        for edge in self.matching:
            left, right = canonical_edge(*edge)
            if not (
                (left in first_set and right in second_set)
                or (left in second_set and right in first_set)
            ):
                raise ValueError("every matching edge must cross the triangles")
            degrees[left] += 1
            degrees[right] += 1
        if set(degrees.values()) != {1}:
            raise ValueError("witness cross edges are not a perfect matching")

    @property
    def vertices(self) -> tuple[int, ...]:
        return tuple(sorted((*self.triangles[0], *self.triangles[1])))

    @property
    def required_edges(self) -> tuple[FullEdge, ...]:
        edges = {
            canonical_edge(*edge)
            for triangle in self.triangles
            for edge in itertools.combinations(triangle, 2)
        }
        edges.update(self.matching)
        if len(edges) != 9:
            raise AssertionError("prism witness does not contain nine edges")
        return tuple(sorted(edges))

    def as_json(self) -> dict[str, object]:
        return {
            "triangles": [
                list(self.triangles[0]),
                list(self.triangles[1]),
            ],
            "matching": [list(edge) for edge in self.matching],
            "vertices": list(self.vertices),
        }


def triangles_in_graph(
    vertex_count: int, edges: Iterable[FullEdge]
) -> tuple[tuple[int, int, int], ...]:
    adjacency = [set() for _ in range(vertex_count)]
    for raw_first, raw_second in edges:
        first, second = canonical_edge(raw_first, raw_second)
        if not 0 <= first < second < vertex_count:
            raise ValueError("edge endpoint outside certificate vertex range")
        adjacency[first].add(second)
        adjacency[second].add(first)

    triangles: list[tuple[int, int, int]] = []
    for first in range(vertex_count):
        for second in sorted(vertex for vertex in adjacency[first] if vertex > first):
            for third in sorted(
                vertex
                for vertex in adjacency[first].intersection(adjacency[second])
                if vertex > second
            ):
                triangles.append((first, second, third))
    return tuple(triangles)


def find_induced_prisms(
    vertex_count: int, edges: Iterable[FullEdge]
) -> tuple[PrismWitness, ...]:
    """Exhaustively find induced triangular prisms in an edge-list graph."""

    edge_set = {canonical_edge(*edge) for edge in edges}
    triangles = triangles_in_graph(vertex_count, edge_set)
    witnesses: list[PrismWitness] = []

    for first_index, first in enumerate(triangles):
        first_set = frozenset(first)
        for second in triangles[first_index + 1 :]:
            if first_set.intersection(second):
                continue
            cross = tuple(
                sorted(
                    edge
                    for edge in (
                        canonical_edge(left, right)
                        for left in first
                        for right in second
                    )
                    if edge in edge_set
                )
            )
            if len(cross) != 3:
                continue
            cross_degrees = {vertex: 0 for vertex in (*first, *second)}
            for left, right in cross:
                cross_degrees[left] += 1
                cross_degrees[right] += 1
            if set(cross_degrees.values()) != {1}:
                continue
            witnesses.append(
                PrismWitness(
                    triangles=(tuple(first), tuple(second)),
                    matching=cross,
                )
            )

    return tuple(witnesses)


def witness_variable_keys(
    root: RootModel, witness: PrismWitness
) -> tuple[VariableEdge, ...]:
    variables: set[VariableEdge] = set()
    for edge in witness.required_edges:
        state = rooted_edge_state(root, *edge)
        if state is False:
            raise ValueError("witness uses a fixed scaffold nonedge")
        if state is not True:
            variables.add(state)
    if not variables:
        raise ValueError("witness unexpectedly lies entirely in fixed edges")
    return tuple(sorted(variables))


def cut_catalog(
    vertex_count: int,
    edges: Iterable[FullEdge],
    root: RootModel | None = None,
) -> dict[str, object]:
    """Build a deterministic independently checkable catalog of all prism cuts."""

    if vertex_count != FULL_VERTEX_COUNT:
        raise ValueError("the endpoint cut catalog requires exactly 99 vertices")
    actual_root = root or RootModel.build(7)
    edge_list = tuple(sorted({canonical_edge(*edge) for edge in edges}))
    witnesses = find_induced_prisms(vertex_count, edge_list)
    variable_ids = residual_variable_ids()
    entries_by_clause: dict[tuple[int, ...], dict[str, object]] = {}

    for witness in witnesses:
        keys = witness_variable_keys(actual_root, witness)
        literals = tuple(-variable_ids[key] for key in keys)
        entries_by_clause.setdefault(
            literals,
            {
                "negative_literals": list(literals),
                "variable_edges": [list(edge) for edge in keys],
                "witness": witness.as_json(),
            },
        )

    entries = [entries_by_clause[key] for key in sorted(entries_by_clause)]
    return {
        "format": "wave38-prism-cut-catalog-v1",
        "claim_label": (
            "CANDIDATE_PRISM_FREE_ONLY" if not witnesses else "CANDIDATE_CUTS"
        ),
        "scope": CATALOG_SCOPE,
        "candidate": {
            "edge_count": len(edge_list),
            "edge_catalog_sha256": sha256_bytes(
                canonical_json([list(edge) for edge in edge_list]).encode("utf-8")
            ),
        },
        "triangle_count": len(triangles_in_graph(vertex_count, edge_list)),
        "prism_witness_count": len(witnesses),
        "deduplicated_cut_count": len(entries),
        "entries": entries,
        "limitations": list(CATALOG_LIMITATIONS),
    }


def validate_cut_catalog(
    catalog: Mapping[str, object],
    root: RootModel | None = None,
    *,
    candidate_edges: Iterable[FullEdge] | None = None,
    require_complete: bool = False,
) -> tuple[tuple[int, ...], ...]:
    """Validate retained cuts and optionally bind the complete candidate catalog.

    Without ``candidate_edges`` this proves only the soundness of every listed
    cut.  A completeness claim requires the frozen candidate edge set and a
    byte-for-byte-equivalent reconstruction of the canonical catalog.
    """

    required = {
        "format",
        "claim_label",
        "scope",
        "candidate",
        "triangle_count",
        "prism_witness_count",
        "deduplicated_cut_count",
        "entries",
        "limitations",
    }
    if set(catalog) != required:
        raise ValueError("cut catalog has missing or unknown top-level keys")
    if catalog["format"] != "wave38-prism-cut-catalog-v1":
        raise ValueError("unsupported cut catalog format")
    for key in (
        "triangle_count",
        "prism_witness_count",
        "deduplicated_cut_count",
    ):
        if type(catalog[key]) is not int or catalog[key] < 0:
            raise ValueError(f"cut catalog {key} must be a nonnegative integer")
    expected_claim = (
        "CANDIDATE_PRISM_FREE_ONLY"
        if catalog["prism_witness_count"] == 0
        else "CANDIDATE_CUTS"
    )
    if catalog["claim_label"] != expected_claim:
        raise ValueError("cut catalog has an invalid claim label")
    if catalog["scope"] != CATALOG_SCOPE:
        raise ValueError("cut catalog has an invalid scope")
    if catalog["limitations"] != list(CATALOG_LIMITATIONS):
        raise ValueError("cut catalog has invalid limitations")
    candidate = catalog["candidate"]
    if not isinstance(candidate, dict) or set(candidate) != {
        "edge_count",
        "edge_catalog_sha256",
    }:
        raise ValueError("cut catalog candidate has an invalid schema")
    if type(candidate["edge_count"]) is not int or candidate["edge_count"] < 0:
        raise ValueError("cut catalog candidate edge_count is invalid")
    candidate_digest = candidate["edge_catalog_sha256"]
    if (
        not isinstance(candidate_digest, str)
        or len(candidate_digest) != 64
        or any(character not in "0123456789abcdef" for character in candidate_digest)
    ):
        raise ValueError("cut catalog candidate SHA-256 is invalid")
    entries = catalog["entries"]
    if not isinstance(entries, list):
        raise ValueError("cut catalog entries must be a list")

    actual_root = root or RootModel.build(7)
    variable_ids = residual_variable_ids()
    cuts: list[tuple[int, ...]] = []
    for index, raw_entry in enumerate(entries):
        if not isinstance(raw_entry, dict) or set(raw_entry) != {
            "negative_literals",
            "variable_edges",
            "witness",
        }:
            raise ValueError(f"cut entry {index} has an invalid schema")
        raw_witness = raw_entry["witness"]
        if not isinstance(raw_witness, dict) or set(raw_witness) != {
            "triangles",
            "matching",
            "vertices",
        }:
            raise ValueError(f"cut entry {index} witness has an invalid schema")
        raw_triangles = raw_witness["triangles"]
        raw_matching = raw_witness["matching"]
        if (
            not isinstance(raw_triangles, list)
            or len(raw_triangles) != 2
            or any(
                not isinstance(triangle, list)
                or len(triangle) != 3
                or any(type(vertex) is not int for vertex in triangle)
                for triangle in raw_triangles
            )
            or not isinstance(raw_matching, list)
            or len(raw_matching) != 3
            or any(
                not isinstance(edge, list)
                or len(edge) != 2
                or any(type(vertex) is not int for vertex in edge)
                for edge in raw_matching
            )
        ):
            raise ValueError(f"cut entry {index} witness dimensions are invalid")
        raw_vertices = raw_witness["vertices"]
        if (
            not isinstance(raw_vertices, list)
            or len(raw_vertices) != 6
            or any(type(vertex) is not int for vertex in raw_vertices)
        ):
            raise ValueError(f"cut entry {index} witness vertices are invalid")
        raw_variable_edges = raw_entry["variable_edges"]
        if (
            not isinstance(raw_variable_edges, list)
            or any(
                not isinstance(edge, list)
                or len(edge) != 2
                or any(type(vertex) is not int for vertex in edge)
                for edge in raw_variable_edges
            )
        ):
            raise ValueError(f"cut entry {index} variable edges are invalid")
        raw_literals = raw_entry["negative_literals"]
        if (
            not isinstance(raw_literals, list)
            or any(type(literal) is not int for literal in raw_literals)
        ):
            raise ValueError(f"cut entry {index} literals are invalid")
        triangles = tuple(tuple(vertex for vertex in tri) for tri in raw_triangles)
        matching = tuple(canonical_edge(*edge) for edge in raw_matching)
        try:
            witness = PrismWitness(
                triangles=(
                    tuple(sorted(triangles[0])),
                    tuple(sorted(triangles[1])),
                ),
                matching=tuple(sorted(matching)),
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"cut entry {index} has an invalid prism witness"
            ) from error
        if list(witness.vertices) != raw_vertices:
            raise ValueError(f"cut entry {index} has a wrong vertex catalog")
        keys = witness_variable_keys(actual_root, witness)
        if [list(edge) for edge in keys] != raw_variable_edges:
            raise ValueError(f"cut entry {index} has wrong variable edges")
        literals = tuple(-variable_ids[key] for key in keys)
        if list(literals) != raw_literals:
            raise ValueError(f"cut entry {index} has wrong literals")
        cuts.append(literals)

    if len(cuts) != len(set(cuts)):
        raise ValueError("cut catalog contains duplicate clauses")
    if cuts != sorted(cuts):
        raise ValueError("cut catalog clauses are not in canonical order")
    if len(cuts) != catalog["deduplicated_cut_count"]:
        raise ValueError("cut count does not match catalog metadata")
    if catalog["prism_witness_count"] < len(cuts):
        raise ValueError("a deduplicated cut cannot outnumber prism witnesses")
    if candidate_edges is not None:
        expected = cut_catalog(FULL_VERTEX_COUNT, candidate_edges, actual_root)
        if dict(catalog) != expected:
            raise ValueError(
                "cut catalog is not the complete canonical catalog for the candidate"
            )
    elif require_complete:
        raise ValueError(
            "candidate edges are required to verify cut catalog completeness"
        )
    return tuple(cuts)


def build_cut_pool(
    catalogs: Sequence[tuple[str, Mapping[str, object]]],
    root: RootModel | None = None,
) -> dict[str, object]:
    """Merge per-candidate catalogs into a deterministic cumulative cut pool.

    ``catalogs`` pairs each catalog's SHA-256 with its parsed content.  Sorting
    by digest makes the pool independent of command-line input order.
    """

    actual_root = root or RootModel.build(7)
    entries_by_clause: dict[tuple[int, ...], dict[str, object]] = {}
    sources: list[dict[str, object]] = []
    for digest, catalog in sorted(catalogs, key=lambda item: item[0]):
        cuts = validate_cut_catalog(catalog, actual_root)
        entries = catalog["entries"]
        if not isinstance(entries, list):
            raise AssertionError("validated catalog entries changed type")
        for cut, entry in zip(cuts, entries, strict=True):
            entries_by_clause.setdefault(cut, entry)
        sources.append(
            {
                "sha256": digest,
                "prism_witness_count": catalog["prism_witness_count"],
                "deduplicated_cut_count": len(cuts),
            }
        )

    ordered_cuts = sorted(entries_by_clause)
    return {
        "format": "wave38-prism-cut-pool-v1",
        "claim_label": "CANDIDATE_CUT_POOL_ONLY",
        "scope": POOL_SCOPE,
        "source_catalogs": sources,
        "deduplicated_cut_count": len(ordered_cuts),
        "entries": [entries_by_clause[cut] for cut in ordered_cuts],
        "limitations": list(POOL_LIMITATIONS),
    }


def validate_cut_pool(
    pool: Mapping[str, object],
    root: RootModel | None = None,
    *,
    source_catalogs: Sequence[tuple[str, Mapping[str, object]]] | None = None,
    require_sources: bool = False,
) -> tuple[tuple[int, ...], ...]:
    required = {
        "format",
        "claim_label",
        "scope",
        "source_catalogs",
        "deduplicated_cut_count",
        "entries",
        "limitations",
    }
    if set(pool) != required:
        raise ValueError("cut pool has missing or unknown top-level keys")
    if pool["format"] != "wave38-prism-cut-pool-v1":
        raise ValueError("unsupported cut pool format")
    if pool["claim_label"] != "CANDIDATE_CUT_POOL_ONLY":
        raise ValueError("cut pool has an invalid claim label")
    if pool["scope"] != POOL_SCOPE:
        raise ValueError("cut pool has an invalid scope")
    if pool["limitations"] != list(POOL_LIMITATIONS):
        raise ValueError("cut pool has invalid limitations")
    if (
        type(pool["deduplicated_cut_count"]) is not int
        or pool["deduplicated_cut_count"] < 0
    ):
        raise ValueError("cut pool deduplicated_cut_count is invalid")
    if not isinstance(pool["entries"], list):
        raise ValueError("cut pool entries must be a list")
    pool_sources = pool["source_catalogs"]
    if not isinstance(pool_sources, list):
        raise ValueError("cut pool source_catalogs must be a list")
    digests: list[str] = []
    for index, source in enumerate(pool_sources):
        if not isinstance(source, dict) or set(source) != {
            "sha256",
            "prism_witness_count",
            "deduplicated_cut_count",
        }:
            raise ValueError(f"cut pool source {index} has invalid schema")
        digest = source["sha256"]
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise ValueError(f"cut pool source {index} has invalid SHA-256")
        for key in ("prism_witness_count", "deduplicated_cut_count"):
            if type(source[key]) is not int or source[key] < 0:
                raise ValueError(f"cut pool source {index} has invalid {key}")
        digests.append(digest)
    if digests != sorted(digests) or len(digests) != len(set(digests)):
        raise ValueError("cut pool source hashes must be unique and sorted")

    pseudo_catalog = {
        "format": "wave38-prism-cut-catalog-v1",
        "claim_label": (
            "CANDIDATE_PRISM_FREE_ONLY"
            if not pool["entries"]
            else "CANDIDATE_CUTS"
        ),
        "scope": CATALOG_SCOPE,
        "candidate": {
            "edge_count": 0,
            "edge_catalog_sha256": "0" * 64,
        },
        "triangle_count": 0,
        "prism_witness_count": len(pool["entries"]),
        "deduplicated_cut_count": pool["deduplicated_cut_count"],
        "entries": pool["entries"],
        "limitations": list(CATALOG_LIMITATIONS),
    }
    cuts = validate_cut_catalog(pseudo_catalog, root)
    if source_catalogs is not None:
        expected = build_cut_pool(source_catalogs, root)
        if dict(pool) != expected:
            raise ValueError(
                "cut pool is not the canonical merge of the supplied source catalogs"
            )
    elif require_sources:
        raise ValueError("source catalogs are required to verify cut pool provenance")
    return cuts


def adjacent_pair_lambda_at_most_one(
    vertex_count: int, edges: Iterable[FullEdge]
) -> bool:
    """Check the only SRG fact used to drop induced nonedge literals."""

    edge_set = {canonical_edge(*edge) for edge in edges}
    adjacency = [set() for _ in range(vertex_count)]
    for first, second in edge_set:
        adjacency[first].add(second)
        adjacency[second].add(first)
    return all(
        len(adjacency[first].intersection(adjacency[second])) <= 1
        for first, second in edge_set
    )
