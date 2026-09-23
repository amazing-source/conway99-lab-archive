#!/usr/bin/env python3
"""Exact replay of the Wave154 triangle-factor portfolio.

The checker validates a second exact Q1 representative, proves it lies
outside the explicit 384-element symmetry orbit of Wave151's Q1, and rebuilds
the joint exact-cover universe.  No complete three-group factor is claimed.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE151_RESULT = ROOT / "attempts/wave151-triangle-root-factor/exact-results.json"
WAVE151_MANIFEST = ROOT / "attempts/wave151-triangle-root-factor/package-manifest.sha256"
EXPECTED_WAVE151_RESULT = (
    "74bc48e2dd0434f3e36a183d724a1ae4a52d7ec9a1e109c92b14f64985da37a4"
)
EXPECTED_WAVE151_MANIFEST = (
    "0e9ea04bad3fb41fda4224684663d828d3d19baea02387303775dd599d34d490"
)

Q1_NEW = [
    55, 50, 34, 6, 39, 45, 38, 23, 21, 35, 58, 19, 22, 29, 20,
    59, 42, 40, 32, 52, 15, 4, 46, 44, 41, 7, 36, 10, 2, 17,
    56, 28, 43, 47, 5, 48, 16, 57, 9, 30, 53, 25, 27, 31, 54,
    18, 24, 49, 11, 51, 33, 3, 26, 0, 8, 12, 14, 1, 13, 37,
]


def demand(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def zero(rows: int, columns: int) -> list[list[int]]:
    return [[0] * columns for _ in range(rows)]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*matrix)]


def multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def edge_universe() -> list[tuple[int, int]]:
    return [
        edge for edge in itertools.combinations(range(12), 2)
        if edge[1] != (edge[0] ^ 1)
    ]


def incidence(edges: list[tuple[int, int]]) -> list[list[int]]:
    matrix = zero(12, len(edges))
    for column, edge in enumerate(edges):
        for vertex in edge:
            matrix[vertex][column] = 1
    return matrix


def permute_columns(matrix: list[list[int]], permutation: list[int]) -> list[list[int]]:
    return [[row[column] for column in permutation] for row in matrix]


def targets() -> tuple[list[list[int]], list[list[int]]]:
    matching = zero(12, 12)
    shift = zero(12, 12)
    for vertex in range(12):
        matching[vertex][vertex ^ 1] = 1
        shift[vertex][(vertex + 6) % 12] = 1
    cross_01 = [
        [
            2 - int(i == j) - 2 * matching[i][j] - shift[i][j]
            for j in range(12)
        ]
        for i in range(12)
    ]
    cross_12 = [
        [
            2
            - int(i == j)
            - shift[i][j]
            - 2 * int(j == ((i ^ 1) + 6) % 12)
            for j in range(12)
        ]
        for i in range(12)
    ]
    return cross_01, cross_12


def centralizer_edge_maps(edges: list[tuple[int, int]]) -> tuple[tuple[int, ...], ...]:
    edge_index = {edge: index for index, edge in enumerate(edges)}
    vertex_orbits = (
        (0, 1, 6, 7),
        (2, 3, 8, 9),
        (4, 5, 10, 11),
    )
    maps = set()
    for orbit_permutation in itertools.permutations(range(3)):
        for translations in itertools.product(range(4), repeat=3):
            vertex_map = [0] * 12
            for source_orbit in range(3):
                target_orbit = orbit_permutation[source_orbit]
                for bits, vertex in enumerate(vertex_orbits[source_orbit]):
                    vertex_map[vertex] = vertex_orbits[target_orbit][
                        bits ^ translations[source_orbit]
                    ]
            maps.add(tuple(
                edge_index[tuple(sorted((vertex_map[u], vertex_map[v])))]
                for u, v in edges
            ))
    demand(len(maps) == 384, "centralizer edge action is not size 384")
    return tuple(sorted(maps))


def conjugate(permutation: list[int], edge_map: tuple[int, ...]) -> tuple[int, ...]:
    inverse = [0] * 60
    for old, new in enumerate(edge_map):
        inverse[new] = old
    return tuple(
        edge_map[permutation[inverse[new_domain]]]
        for new_domain in range(60)
    )


def allowed_triples(
    edges: list[tuple[int, int]],
    cross_01: list[list[int]],
    cross_12: list[list[int]],
) -> set[tuple[int, int, int]]:
    compatible_01 = [
        [
            all(cross_01[i][j] > 0 for i in left for j in right)
            for right in edges
        ]
        for left in edges
    ]
    compatible_12 = [
        [
            all(cross_12[i][j] > 0 for i in left for j in right)
            for right in edges
        ]
        for left in edges
    ]
    return {
        (a, b, c)
        for a in range(60)
        for b in range(60)
        if compatible_01[a][b]
        for c in range(60)
        if compatible_01[a][c] and compatible_12[b][c]
    }


def orbit_count(
    triples: set[tuple[int, int, int]],
    edge_maps: tuple[tuple[int, ...], ...],
) -> int:
    remaining = set(triples)
    count = 0
    while remaining:
        seed = min(remaining)
        orbit = {
            (mapping[seed[0]], mapping[seed[1]], mapping[seed[2]])
            for mapping in edge_maps
        }
        remaining.difference_update(orbit)
        count += 1
    return count


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def build_result() -> dict[str, Any]:
    demand(hashlib.sha256(WAVE151_RESULT.read_bytes()).hexdigest()
           == EXPECTED_WAVE151_RESULT, "Wave151 result drift")
    demand(hashlib.sha256(WAVE151_MANIFEST.read_bytes()).hexdigest()
           == EXPECTED_WAVE151_MANIFEST, "Wave151 manifest drift")
    parent = json.loads(WAVE151_RESULT.read_text(encoding="utf-8"))
    q1_old = list(map(int, parent["exact_partial_factor"]["Q1"]))
    edges = edge_universe()
    c0 = incidence(edges)
    cross_01, cross_12 = targets()
    diagonal = multiply(c0, transpose(c0))
    demand(sorted(Q1_NEW) == list(range(60)), "new Q1 is not a permutation")
    c1_new = permute_columns(c0, Q1_NEW)
    demand(multiply(c1_new, transpose(c1_new)) == diagonal,
           "new Q1 diagonal Gram failure")
    demand(multiply(c0, transpose(c1_new)) == cross_01,
           "new Q1 cross Gram failure")

    edge_maps = centralizer_edge_maps(edges)
    old_orbit = {conjugate(q1_old, mapping) for mapping in edge_maps}
    demand(len(old_orbit) == 384, "old Q1 orbit unexpectedly has stabilizer")
    demand(tuple(Q1_NEW) not in old_orbit,
           "new Q1 is symmetry-equivalent to old Q1")
    new_orbit = {conjugate(Q1_NEW, mapping) for mapping in edge_maps}
    demand(old_orbit.isdisjoint(new_orbit), "Q1 orbits intersect")

    triples = allowed_triples(edges, cross_01, cross_12)
    demand(len(triples) == 69270, "joint exact-cover variable count differs")
    triple_orbits = orbit_count(triples, edge_maps)
    demand(triple_orbits == 292, "joint triple orbit count differs")

    partial_new = c0 + c1_new
    return {
        "format": "wave154-triangle-factor-portfolio-v1",
        "role": "proof_b",
        "claim_label": "VERIFIED_PORTFOLIO_NULL",
        "scope": (
            "symmetry-diverse Q1 representatives and joint exact-cover search "
            "for the fixed Wave149/Wave151 prism-free 36x60 factor"
        ),
        "frozen_inputs_sha256": {
            "attempts/wave151-triangle-root-factor/package-manifest.sha256":
                EXPECTED_WAVE151_MANIFEST,
            "attempts/wave151-triangle-root-factor/exact-results.json":
                EXPECTED_WAVE151_RESULT,
        },
        "symmetry": {
            "explicit_group": "centralizer of M and P on 12 coordinates",
            "group_order": len(edge_maps),
            "old_Q1_orbit_size": len(old_orbit),
            "new_Q1_orbit_size": len(new_orbit),
            "orbits_disjoint": True,
            "no_graph_automorphism_assumed": True,
        },
        "second_exact_Q1_representative": {
            "Q1": Q1_NEW,
            "binary_24x60_sha256": canonical_digest(partial_new),
            "diagonal_blocks_replayed": True,
            "G01_replayed": True,
            "outside_Wave151_Q1_centralizer_orbit": True,
        },
        "joint_exact_cover": {
            "primary_triple_variables": len(triples),
            "triple_orbits_under_explicit_group": triple_orbits,
            "selected_columns_required": 60,
            "edge_capacity_rows": 180,
            "cross_gram_capacity_rows": 432,
            "integer_matrix_nonzeros": 1039050,
            "complete_factor_status": "UNKNOWN",
        },
        "portfolio": [
            {
                "branch": "Wave151 Q1 orbit representative",
                "Q2_status": "UNSAT_WITHOUT_EXPORTED_PROOF",
                "seconds": 40.46,
                "certificate_authority": False,
            },
            {
                "branch": "new disjoint Q1 orbit representative",
                "Q2_z3_status": "UNSAT_WITHOUT_EXPORTED_PROOF",
                "Q2_z3_seconds": 57.59,
                "Q2_gluecard4_status": "INTERRUPTED_UNKNOWN",
                "Q2_gluecard4_seconds": 180.03,
                "certificate_authority": False,
            },
            {
                "branch": "unfixed joint 3D native-cardinality SAT",
                "engine": "Gluecard4",
                "status": "INTERRUPTED_UNKNOWN",
                "seconds": 67.66,
                "certificate_authority": False,
            },
            {
                "branch": "unfixed joint 3D MILP",
                "engine": "HiGHS",
                "status": "TIME_LIMIT_NO_INCUMBENT",
                "seconds": 300.68,
                "certificate_authority": False,
            },
            {
                "branch": "fixed-Q1 CNF proof export",
                "engine": "CaDiCaL195 through PySAT",
                "status": "TIME_LIMIT_NO_PROOF",
                "seconds": 180,
                "certificate_authority": False,
            },
        ],
        "residual_D": {
            "status": "NOT_REACHED",
            "reason": "no complete 36x60 C certificate",
        },
        "conclusion": {
            "complete_C_factor": "UNKNOWN",
            "checkable_UNSAT_proof": False,
            "complete_D_factor": "NOT_REACHED",
            "forces_a_prism": False,
            "strict_n3_upper_bound": "NOT_IMPROVED",
            "graph_realization": False,
            "conway_99": "UNKNOWN",
        },
        "limitations": [
            "Two Q1 symmetry orbits do not exhaust all Q1 factors.",
            "No negative solver status is promoted.",
            "No complete C or D witness was found.",
            "The 384-element group is an explicit local-witness symmetry, not a graph automorphism assumption.",
        ],
    }


def verify_payload(payload: dict[str, Any]) -> None:
    demand(payload == build_result(), "stored Wave154 result differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    if arguments.verify:
        verify_payload(json.loads(arguments.verify.read_text(encoding="utf-8")))
        print(json.dumps({"verification": "PASS", "path": str(arguments.verify)}))
        return 0
    result = build_result()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
