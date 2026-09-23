#!/usr/bin/env python3
"""Focused audit of the omitted m=30 rectangle compatibility identity.

For N = (active-label)-by-(size-two-point) incidence and A_R the positive
crossing graph on points, first principles force

    N A_R N^T = 2 A_L.

The hostile construction below satisfies the submitted coarse F/R
descriptions but violates this equation, proving that a cycle partition for R
is not a complete compatibility certificate.  It is not a target search.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "verification/2026-07-23-wave15-algebraic-audit.md":
        "b0541d05d2c1c359152b86223e2ebbdbd002b2ff42deb699f6a0b21d149a5b45",
    "verification/2026-07-23-wave16-n3-51-structural-audit.md":
        "99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6",
    "agents/2026-07-23-wave19-n3-60-structural.md":
        "b2f90af07f34a6525ea35cdf4d392d95aea10fc319633cd17037d00145690744",
    "attempts/wave19-n3-60-structural/residual-certificates.json":
        "3396b3b67b944b86bfd0d51e8beca25dfc9350815269c62cda4fa7c22a7a5c8b",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate() -> dict[str, str]:
    observed = {name: sha256(ROOT / name) for name in INPUTS}
    if observed != INPUTS:
        raise AssertionError("rectangle-probe input mismatch")
    return observed


def generalized_petersen_10_2() -> tuple[tuple[int, int], ...]:
    """Connected cubic triangle-free graph on 20 labels and 30 points."""
    edges: set[tuple[int, int]] = set()
    for index in range(10):
        edges.add(tuple(sorted((index, (index + 1) % 10))))
        edges.add((index, 10 + index))
        edges.add(tuple(sorted((10 + index, 10 + ((index + 2) % 10)))))
    answer = tuple(sorted(edges))
    if len(answer) != 30:
        raise AssertionError("generalized Petersen edge count mismatch")
    return answer


def degree_sequence(
    vertex_count: int, edges: Iterable[tuple[int, int]]
) -> tuple[int, ...]:
    values = [0] * vertex_count
    for left, right in edges:
        if left == right:
            raise ValueError("loop")
        values[left] += 1
        values[right] += 1
    return tuple(values)


def triangle_count(edges: Iterable[tuple[int, int]], vertex_count: int) -> int:
    edge_set = {tuple(sorted(edge)) for edge in edges}
    return sum(
        all(tuple(sorted(pair)) in edge_set for pair in itertools.combinations(triple, 2))
        for triple in itertools.combinations(range(vertex_count), 3)
    )


def disjoint_edge_hamilton_cycle(
    point_edges: tuple[tuple[int, int], ...]
) -> tuple[int, ...]:
    """Find one deterministic R cycle whose consecutive F edges are disjoint."""
    point_count = len(point_edges)
    compatible = tuple(
        tuple(
            other
            for other in range(point_count)
            if other != point
            and set(point_edges[point]).isdisjoint(point_edges[other])
        )
        for point in range(point_count)
    )
    path = [0]
    unused = set(range(1, point_count))

    def extend() -> bool:
        if not unused:
            return 0 in compatible[path[-1]]
        current = path[-1]
        candidates = [point for point in compatible[current] if point in unused]
        # Fail first on the vertices with the fewest currently available exits.
        candidates.sort(key=lambda point: (
            sum(neighbor in unused for neighbor in compatible[point]),
            point,
        ))
        for point in candidates:
            if len(unused) == 1 and 0 not in compatible[point]:
                continue
            unused.remove(point)
            path.append(point)
            if extend():
                return True
            path.pop()
            unused.add(point)
        return False

    if not extend():
        raise AssertionError("no hostile disjoint-edge Hamilton cycle found")
    return tuple(path)


def incidence_matrix(
    label_count: int, point_edges: tuple[tuple[int, int], ...]
) -> list[list[int]]:
    matrix = [[0] * len(point_edges) for _ in range(label_count)]
    for point, (left, right) in enumerate(point_edges):
        matrix[left][point] = 1
        matrix[right][point] = 1
    return matrix


def adjacency_from_cycle(cycle: tuple[int, ...]) -> list[list[int]]:
    count = len(cycle)
    matrix = [[0] * count for _ in range(count)]
    for index, left in enumerate(cycle):
        right = cycle[(index + 1) % count]
        matrix[left][right] = matrix[right][left] = 1
    return matrix


def rectangle_product(
    incidence: list[list[int]], point_adjacency: list[list[int]]
) -> list[list[int]]:
    label_count = len(incidence)
    point_count = len(point_adjacency)
    product = [[0] * label_count for _ in range(label_count)]
    for left_label in range(label_count):
        for right_label in range(label_count):
            product[left_label][right_label] = sum(
                incidence[left_label][left_point]
                * point_adjacency[left_point][right_point]
                * incidence[right_label][right_point]
                for left_point in range(point_count)
                for right_point in range(point_count)
            )
    return product


def cycle_partitions(total: int, minimum_part: int = 3) -> tuple[tuple[int, ...], ...]:
    if total == 0:
        return ((),)
    answers = []
    for first in range(minimum_part, total + 1):
        for rest in cycle_partitions(total - first, first):
            answers.append((first,) + rest)
    return tuple(answers)


def gf2_rank(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    column_count = len(matrix[0])
    rows = [
        sum((value & 1) << column for column, value in enumerate(row))
        for row in matrix
    ]
    rank = 0
    for column in range(column_count):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index] >> column & 1),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and rows[index] >> column & 1:
                rows[index] ^= rows[rank]
        rank += 1
    return rank


def cycle_adjacency(partition: tuple[int, ...]) -> list[list[int]]:
    total = sum(partition)
    matrix = [[0] * total for _ in range(total)]
    offset = 0
    for length in partition:
        for index in range(length):
            left = offset + index
            right = offset + ((index + 1) % length)
            matrix[left][right] = matrix[right][left] = 1
        offset += length
    return matrix


def cycle_nullity(partition: tuple[int, ...]) -> int:
    """GF(2) nullity: one per odd cycle and two per even cycle."""
    return len(partition) + sum(length % 2 == 0 for length in partition)


def mod2_cycle_restriction() -> dict[str, object]:
    partitions = cycle_partitions(30)
    if len(partitions) != 331:
        raise AssertionError("cycle partition census mismatch")
    distribution: dict[int, int] = {}
    for partition in partitions:
        predicted = cycle_nullity(partition)
        direct = 30 - gf2_rank(cycle_adjacency(partition))
        if predicted != direct:
            raise AssertionError(f"cycle nullity mismatch: {partition}")
        distribution[predicted] = distribution.get(predicted, 0) + 1

    # For a cubic triangle-free F on 20 vertices, every component has at least
    # six vertices, hence c(F)<=3.  rank_GF2(N)=20-c and dim ker(N)=10+c.
    # From N A_R N^T=0 mod 2, A_R maps im(N^T) into ker(N), forcing
    # nullity(A_R)>=10-2c.
    thresholds = {
        component_count: 10 - 2 * component_count
        for component_count in (1, 2, 3)
    }
    survivors = {
        component_count: sum(
            cycle_nullity(partition) >= threshold for partition in partitions
        )
        for component_count, threshold in thresholds.items()
    }
    universally_excluded = [
        list(partition) for partition in partitions if cycle_nullity(partition) < 4
    ]
    if universally_excluded != [
        [3, 27], [5, 25], [7, 23], [9, 21],
        [11, 19], [13, 17], [15, 15], [30],
    ]:
        raise AssertionError("universal cycle-type exclusion mismatch")
    return {
        "derivation": (
            "Over GF(2), N A_R N^T=0. For c components of F, "
            "dim im(N^T)=20-c and dim ker(N)=10+c, so A_R maps a "
            "(20-c)-space into a (10+c)-space and nullity(A_R)>=10-2c."
        ),
        "component_bound": "c(F)<=3 because a simple cubic triangle-free component has >=6 vertices",
        "cycle_nullity_formula": "#odd cycles + 2*#even cycles",
        "nullity_distribution_over_331_cycle_partitions": {
            str(key): value for key, value in sorted(distribution.items())
        },
        "required_nullity_by_F_component_count": {
            str(key): value for key, value in thresholds.items()
        },
        "surviving_cycle_partition_count_by_F_component_count": {
            str(key): value for key, value in survivors.items()
        },
        "universally_excluded_cycle_partitions": universally_excluded,
        "connected_F_consequence": (
            "If F is connected, only 147 of the 331 abstract R cycle "
            "partitions survive the necessary nullity>=8 test."
        ),
    }


def build_results() -> dict[str, object]:
    inputs = authenticate()
    point_edges = generalized_petersen_10_2()
    if degree_sequence(20, point_edges) != (3,) * 20:
        raise AssertionError("hostile F is not cubic")
    if triangle_count(point_edges, 20):
        raise AssertionError("hostile F is not triangle-free")

    cycle = disjoint_edge_hamilton_cycle(point_edges)
    r_edges = {
        tuple(sorted((cycle[index], cycle[(index + 1) % 30])))
        for index in range(30)
    }
    if len(r_edges) != 30 or degree_sequence(30, r_edges) != (2,) * 30:
        raise AssertionError("hostile R is not a simple spanning 2-factor")
    if any(
        not set(point_edges[left]).isdisjoint(point_edges[right])
        for left, right in r_edges
    ):
        raise AssertionError("hostile R meets in F")

    incidence = incidence_matrix(20, point_edges)
    point_adjacency = adjacency_from_cycle(cycle)
    product = rectangle_product(incidence, point_adjacency)
    diagonal = [product[index][index] for index in range(20)]
    off_diagonal = [
        product[left][right]
        for left in range(20)
        for right in range(left + 1, 20)
    ]
    value_counts = {
        str(value): off_diagonal.count(value) for value in sorted(set(off_diagonal))
    }
    violating_pair = next(
        (left, right, product[left][right])
        for left in range(20)
        for right in range(left + 1, 20)
        if product[left][right] not in (0, 2)
    )
    if any(diagonal):
        raise AssertionError("disjoint R should give zero diagonal")
    if all(value in (0, 2) for value in off_diagonal):
        raise AssertionError("hostile coarse F/R pair unexpectedly satisfies identity")
    if [sum(row) for row in product] != [12] * 20:
        raise AssertionError("rectangle-product row sum should be 12")

    return {
        "claim_label": "DERIVED",
        "inputs_sha256": inputs,
        "identity": "N A_R N^T = 2 A_L",
        "first_principles_derivation": [
            "N is the 20-by-30 active-label/size-two-point incidence matrix.",
            "An R edge has a positive two-by-two L crossing, hence contributes its full four-entry rectangle to N A_R N^T.",
            "An L edge joins two active graph triangles by exactly two original cross edges (the audited a_2=d_L=3q definition).",
            "Each of those two cross edges has a nonempty size-two crossing containing that L edge, so it is an R edge.",
            "Thus every L entry occurs exactly twice and every non-L entry occurs zero times.",
            "Z edges have zero crossing and therefore do not occur in A_R or in this product.",
        ],
        "submitted_artifact_check": {
            "residual_json_contains_N_A_R_Nt": False,
            "residual_json_instantiates_common_labeled_F_R_L": False,
            "effect": (
                "omitted stronger necessary compatibility; does not falsify the "
                "coarser necessary reduction or close m=30"
            ),
        },
        "mod2_rank_consequence": mod2_cycle_restriction(),
        "hostile_coarse_pair": {
            "restriction": (
                "one explicit F=generalized Petersen G(10,2), Z empty, and one "
                "deterministically found 30-cycle R; this is not a complete search"
            ),
            "F_connected_cubic_triangle_free": True,
            "R_simple_spanning_2factor": True,
            "R_disjoint_from_line_graph_F": True,
            "R_cycle_length_multiset": [30],
            "rectangle_row_sums": [sum(row) for row in product],
            "off_diagonal_value_counts": value_counts,
            "first_violating_label_pair": list(violating_pair),
            "rectangle_identity": "FAIL",
            "mod2_explanation": (
                "F is connected, so nullity(A_R)>=8 is necessary; a single "
                "30-cycle has GF(2) nullity two"
            ),
            "meaning": (
                "the candidate's cycle-partition/coarse F-R fields accept data "
                "that cannot be a positive-crossing system"
            ),
        },
        "status_boundary": {
            "r20_m30": "UNKNOWN_STRONGER_FINITE_RESIDUAL",
            "conditional_n3_60": "UNKNOWN_FINITE_RESIDUAL",
            "conway_99_target": "UNKNOWN",
        },
        "limitations": [
            "No search for an F,R pair satisfying the identity was performed.",
            "Failure of the single hostile coarse pair is not nonexistence evidence.",
            "The identity is a necessary condition, not an SRG extension certificate.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    rendered = json.dumps(build_results(), indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    if arguments.verify:
        if arguments.verify.read_text(encoding="utf-8") != rendered:
            raise AssertionError(f"rectangle result mismatch: {arguments.verify}")
    if not arguments.output and not arguments.verify:
        print(rendered, end="")


if __name__ == "__main__":
    main()
