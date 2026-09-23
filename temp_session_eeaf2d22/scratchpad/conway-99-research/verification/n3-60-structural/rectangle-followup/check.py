#!/usr/bin/env python3
"""Minimal independent GF(2) check for N A_R N^T = 2 A_L."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[3]
INPUTS = {
    "verification/n3-60-structural/preinspection-freeze.md":
        "983f90c1d150c6e14e5e2bc7a010e1a3809848ddb1e4b825e5fdfac70398d6af",
    "verification/2026-07-23-wave15-global-lift-audit.md":
        "edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036",
    "verification/2026-07-23-wave16-n3-51-structural-audit.md":
        "99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6",
    "agents/2026-07-23-wave19-n3-60-structural.md":
        "b2f90af07f34a6525ea35cdf4d392d95aea10fc319633cd17037d00145690744",
}


def rank_dense(rows: Sequence[Sequence[int]], columns: int) -> int:
    matrix = [[entry & 1 for entry in row] for row in rows]
    rank = 0
    for column in range(columns):
        pivot = next(
            (i for i in range(rank, len(matrix)) if matrix[i][column]), None
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        for i in range(len(matrix)):
            if i != rank and matrix[i][column]:
                matrix[i] = [
                    left ^ right for left, right in zip(matrix[i], matrix[rank])
                ]
        rank += 1
    return rank


def rank_bits(rows: Sequence[Sequence[int]], columns: int) -> int:
    values = [
        sum((entry & 1) << j for j, entry in enumerate(row)) for row in rows
    ]
    rank = 0
    for column in range(columns - 1, -1, -1):
        pivot = next(
            (i for i in range(rank, len(values)) if values[i] >> column & 1),
            None,
        )
        if pivot is None:
            continue
        values[rank], values[pivot] = values[pivot], values[rank]
        for i in range(len(values)):
            if i != rank and values[i] >> column & 1:
                values[i] ^= values[rank]
        rank += 1
    return rank


def rank(rows: Sequence[Sequence[int]], columns: int) -> int:
    first, second = rank_dense(rows, columns), rank_bits(rows, columns)
    assert first == second
    return first


def cycle_partitions(total: int, minimum: int = 3):
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for tail in cycle_partitions(total - first, first):
            yield (first,) + tail


def cycle_matrix(lengths: Sequence[int]) -> list[list[int]]:
    order = sum(lengths)
    matrix = [[0] * order for _ in range(order)]
    offset = 0
    for length in lengths:
        for i in range(length):
            first, second = offset + i, offset + (i + 1) % length
            matrix[first][second] = matrix[second][first] = 1
        offset += length
    return matrix


def cycle_nullity(lengths: Sequence[int]) -> int:
    return sum(1 if length % 2 else 2 for length in lengths)


def incidence(vertex_count: int, edges: Sequence[tuple[int, int]]):
    matrix = [[0] * len(edges) for _ in range(vertex_count)]
    for j, (first, second) in enumerate(edges):
        matrix[first][j] = matrix[second][j] = 1
    return matrix


def in_row_space(vector: Sequence[int], rows: Sequence[Sequence[int]]) -> bool:
    columns = len(vector)
    return rank(rows, columns) == rank(list(rows) + [list(vector)], columns)


def component_count(vertex_count: int, edges: Sequence[tuple[int, int]]) -> int:
    adjacency = [set() for _ in range(vertex_count)]
    for first, second in edges:
        adjacency[first].add(second)
        adjacency[second].add(first)
    unseen, count = set(range(vertex_count)), 0
    while unseen:
        count += 1
        stack = [next(iter(unseen))]
        seen = set()
        while stack:
            vertex = stack.pop()
            if vertex in seen:
                continue
            seen.add(vertex)
            stack.extend(adjacency[vertex] - seen)
        unseen -= seen
    return count


def bipartite(vertex_count: int, edges: Sequence[tuple[int, int]]) -> bool:
    adjacency = [set() for _ in range(vertex_count)]
    for first, second in edges:
        adjacency[first].add(second)
        adjacency[second].add(first)
    colors = {}
    for start in range(vertex_count):
        if start in colors:
            continue
        colors[start], stack = 0, [start]
        while stack:
            vertex = stack.pop()
            for neighbor in adjacency[vertex]:
                if neighbor not in colors:
                    colors[neighbor] = 1 - colors[vertex]
                    stack.append(neighbor)
                elif colors[neighbor] == colors[vertex]:
                    return False
    return True


def controls():
    k33 = tuple((left, right) for left in range(3) for right in range(3, 6))
    petersen = tuple(
        sorted(
            {
                tuple(sorted(edge))
                for i in range(5)
                for edge in (
                    (i, (i + 1) % 5),
                    (i, 5 + i),
                    (5 + i, 5 + (i + 2) % 5),
                )
            }
        )
    )
    rows = []
    for name, vertices, edges, expected_bipartite in (
        ("K3,3", 6, k33, True),
        ("Petersen", 10, petersen, False),
    ):
        n_matrix = incidence(vertices, edges)
        ones = [1] * len(edges)
        cut_membership = in_row_space(ones, n_matrix)
        assert bipartite(vertices, edges) == expected_bipartite
        assert cut_membership == expected_bipartite
        assert rank(n_matrix, len(edges)) == vertices - component_count(vertices, edges)
        rows.append(
            {
                "graph": name,
                "bipartite": expected_bipartite,
                "all_one_edge_vector_in_cut_space": cut_membership,
                "result": "PASS",
            }
        )
    return rows


def build():
    observed = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in INPUTS
    }
    assert observed == INPUTS
    partitions = list(cycle_partitions(30))
    assert len(partitions) == 331
    rows = []
    for lengths in partitions:
        matrix = cycle_matrix(lengths)
        actual = 30 - rank(matrix, 30)
        formula = cycle_nullity(lengths)
        assert actual == formula
        rows.append({"cycles": list(lengths), "nullity": formula})
    counts = {
        str(components): sum(
            row["nullity"] >= 10 - 2 * components for row in rows
        )
        for components in (1, 2, 3)
    }
    nonbip_counts = {
        str(components): sum(
            row["nullity"] >= 12 - 2 * components for row in rows
        )
        for components in (1, 2, 3)
    }
    assert counts == {"1": 147, "2": 263, "3": 323}
    assert nonbip_counts == {"1": 55, "2": 147, "3": 263}
    control_rows = controls()
    return {
        "claim_label": "DERIVED",
        "scope": "GF(2) rank/nullity consequences of N A_R N^T=2A_L",
        "inputs_sha256": observed,
        "derivation": [
            "W=im(N^T) is the binary cut space and dim(W)=20-c(F).",
            "Modulo two, W is totally isotropic for the alternating form A_R.",
            "For z=nullity(A_R) and t=dim(W intersect ker(A_R)), projection to the nondegenerate quotient gives 20-c-t <= (30-z)/2.",
            "Thus t>=5-c+z/2; because t<=z, z>=10-2c.",
            "On C_l, A_R x=0 gives x_(i+2)=x_i, so its nullity is one for odd l and two for even l.",
            "Therefore z=#odd R-cycles+2#even R-cycles.",
            "Every simple triangle-free cubic component has even order at least six, hence c(F)<=3.",
        ],
        "nonbipartite_refinement": {
            "status": "NECESSARY_CONDITION_ONLY",
            "proof": [
                "The all-one edge vector lies in ker(A_R) because every R row has sum two, which is zero in GF(2).",
                "It lies in cut(F)=im(N^T) exactly if N^T x=1 is solvable, equivalently if x gives opposite colors across every F edge, equivalently if every F component is bipartite.",
                "If some F component is nonbipartite, the all-one radical vector is outside W, so t<=z-1.",
                "Combining z-1>=t>=5-c+z/2 yields z>=12-2c.",
            ],
            "cycle_type_counts_by_c": nonbip_counts,
            "hostile_bipartite_nonbipartite_controls": control_rows,
        },
        "cycle_type_census": {
            "all_cycle_types": 331,
            "necessary_counts_by_c": counts,
            "rows": rows,
        },
        "restrictions": [
            "Cycle lengths are unlabeled simple 2-factor cycles of length at least three.",
            "The counts are necessary cycle-type filters, not placement or feasibility certificates.",
            "No graph catalog, automorphism restriction, solver, or prohibited later-wave input is used.",
        ],
        "status_boundary": {
            "rank_nullity_invariant": "DERIVED",
            "m30": "UNKNOWN",
            "conditional_n3_60": "UNKNOWN_FINITE_RESIDUAL",
            "self_promoted_to_VERIFIED": False,
        },
    }


def render():
    return json.dumps(build(), indent=2, sort_keys=True) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    text = render()
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    if args.verify:
        assert args.verify.read_text(encoding="utf-8") == text
    if not args.output and not args.verify:
        result = json.loads(text)
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "counts": result["cycle_type_census"]["necessary_counts_by_c"],
                    "m30": result["status_boundary"]["m30"],
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
