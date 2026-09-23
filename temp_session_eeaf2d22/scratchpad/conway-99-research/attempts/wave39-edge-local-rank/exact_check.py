#!/usr/bin/env python3
"""Exact edge-local characteristic-seven rank calculation for Conway-99."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

FORMAT = "wave39-edge-local-rank-v1"
PUBLIC_BASE_COMMIT = "019b78ac9a5170107d105ad4d8fcd27f55dde642"
PRIME = 7
TARGET_VERTICES = 99
TRIANGLE_PROJECTOR_RATIONAL_RANK = 44


def integer_partitions(total: int, minimum: int = 1) -> Iterable[tuple[int, ...]]:
    """Yield nondecreasing positive partitions of ``total``."""

    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for tail in integer_partitions(total - first, first):
            yield (first,) + tail


def add_edge(adjacency: list[list[int]], left: int, right: int) -> None:
    if left == right or adjacency[left][right]:
        raise AssertionError("invalid repeated or loop edge")
    adjacency[left][right] = 1
    adjacency[right][left] = 1


def canonical_edge_local_graph(partition: Sequence[int]) -> list[list[int]]:
    """Build the forced 27-vertex graph for one cycle partition.

    Vertices 0,1,2 are the edge endpoints x,y and their triangle mate z.
    Vertices 3..14 are X and 15..26 are Y.  Each part m creates a cycle of
    length 4m in the union of the X matching, Y matching, and X--Y matching.
    """

    if tuple(partition) not in set(integer_partitions(6)):
        raise ValueError("partition must be a positive nondecreasing partition of six")

    adjacency = [[0] * 27 for _ in range(27)]
    x, y, z = 0, 1, 2
    x_vertices = list(range(3, 15))
    y_vertices = list(range(15, 27))

    add_edge(adjacency, x, y)
    add_edge(adjacency, x, z)
    add_edge(adjacency, y, z)
    for vertex in x_vertices:
        add_edge(adjacency, x, vertex)
    for vertex in y_vertices:
        add_edge(adjacency, y, vertex)

    offset = 0
    for part in partition:
        xs = x_vertices[offset : offset + 2 * part]
        ys = y_vertices[offset : offset + 2 * part]
        for index in range(part):
            x_even = xs[2 * index]
            x_odd = xs[2 * index + 1]
            y_even = ys[2 * index]
            y_odd = ys[2 * index + 1]
            next_x_even = xs[(2 * (index + 1)) % (2 * part)]
            add_edge(adjacency, x_even, x_odd)
            add_edge(adjacency, y_even, y_odd)
            add_edge(adjacency, x_odd, y_odd)
            add_edge(adjacency, y_even, next_x_even)
        offset += 2 * part

    if offset != 12:
        raise AssertionError("cycle parts did not consume all local vertices")
    return adjacency


def connected_component_sizes(
    adjacency: Sequence[Sequence[int]], vertices: Sequence[int]
) -> tuple[int, ...]:
    allowed = set(vertices)
    unseen = set(vertices)
    sizes: list[int] = []
    while unseen:
        start = min(unseen)
        stack = [start]
        size = 0
        while stack:
            vertex = stack.pop()
            if vertex not in unseen:
                continue
            unseen.remove(vertex)
            size += 1
            stack.extend(
                neighbor
                for neighbor in allowed
                if adjacency[vertex][neighbor] and neighbor in unseen
            )
        sizes.append(size)
    return tuple(sorted(sizes))


def local_axioms(adjacency: Sequence[Sequence[int]]) -> dict[str, object]:
    degrees = [sum(row) for row in adjacency]
    x_vertices = range(3, 15)
    y_vertices = range(15, 27)
    cycle_vertices = tuple(range(3, 27))
    x_internal = [sum(adjacency[v][u] for u in x_vertices) for v in x_vertices]
    y_internal = [sum(adjacency[v][u] for u in y_vertices) for v in y_vertices]
    cross_x = [sum(adjacency[v][u] for u in y_vertices) for v in x_vertices]
    cross_y = [sum(adjacency[v][u] for u in x_vertices) for v in y_vertices]
    if degrees[:3] != [14, 14, 2]:
        raise AssertionError("triangle endpoint degrees changed")
    if set(degrees[3:]) != {3}:
        raise AssertionError("X/Y local degrees changed")
    if set(x_internal) != {1} or set(y_internal) != {1}:
        raise AssertionError("fibre matchings changed")
    if set(cross_x) != {1} or set(cross_y) != {1}:
        raise AssertionError("cross matching changed")
    return {
        "vertex_count": len(adjacency),
        "edge_count": sum(degrees) // 2,
        "degree_sequence": sorted(degrees),
        "X_internal_degree_set": sorted(set(x_internal)),
        "Y_internal_degree_set": sorted(set(y_internal)),
        "cross_degree_sets": [sorted(set(cross_x)), sorted(set(cross_y))],
        "cycle_component_sizes": list(
            connected_component_sizes(adjacency, cycle_vertices)
        ),
    }


def incidence_transport_block(
    adjacency: Sequence[Sequence[int]],
) -> list[list[int]]:
    """Return (27 I - 9 A + J) on the local vertex set."""

    order = len(adjacency)
    return [
        [
            27 * int(row == column) - 9 * adjacency[row][column] + 1
            for column in range(order)
        ]
        for row in range(order)
    ]


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    if not work:
        return 0
    row_count = len(work)
    column_count = len(work[0])
    rank = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(rank, row_count) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [(entry * inverse) % prime for entry in work[rank]]
        for row in range(row_count):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (left - factor * right) % prime
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == row_count:
            break
    return rank


def rank_formula(partition: Sequence[int]) -> int:
    """Closed finite-normal-form formula checked by exact elimination."""

    even_parts = sum(part % 2 == 0 for part in partition)
    return 25 - 2 * even_parts


def admissible_endpoint_pairs() -> list[list[int]]:
    """Apply r3>=12, r7>=19, r3,r7<=44, and even r3+r7."""

    return [
        [r3, r7]
        for r3 in range(12, 45)
        for r7 in range(19, 45)
        if (r3 + r7) % 2 == 0
    ]


def exact_record() -> dict[str, object]:
    normal_forms: list[dict[str, object]] = []
    for partition in integer_partitions(6):
        adjacency = canonical_edge_local_graph(partition)
        axioms = local_axioms(adjacency)
        expected_components = sorted(4 * part for part in partition)
        if axioms["cycle_component_sizes"] != expected_components:
            raise AssertionError("cycle component sizes do not match the partition")
        matrix = incidence_transport_block(adjacency)
        rank = rank_mod_prime(matrix, PRIME)
        formula_rank = rank_formula(partition)
        if rank != formula_rank:
            raise AssertionError(
                f"rank formula failed for {partition}: {rank} != {formula_rank}"
            )
        normal_forms.append(
            {
                "partition": list(partition),
                "cycle_lengths": expected_components,
                "even_part_count": sum(part % 2 == 0 for part in partition),
                "contains_local_prism": 1 in partition,
                "rank_F7_local_transport_block": rank,
                "nullity_F7_local_transport_block": 27 - rank,
                "local_axioms": axioms,
            }
        )

    endpoint_forms = [
        form for form in normal_forms if not form["contains_local_prism"]
    ]
    endpoint_partitions = [form["partition"] for form in endpoint_forms]
    expected_endpoint = [[2, 2, 2], [2, 4], [3, 3], [6]]
    if endpoint_partitions != expected_endpoint:
        raise AssertionError("prism-free endpoint partition list changed")

    universal_floor = min(
        int(form["rank_F7_local_transport_block"]) for form in normal_forms
    )
    endpoint_floor = min(
        int(form["rank_F7_local_transport_block"]) for form in endpoint_forms
    )
    if universal_floor != 19 or endpoint_floor != 19:
        raise AssertionError("rank floor changed")

    pairs = admissible_endpoint_pairs()
    r3_twelve = [r7 for r3, r7 in pairs if r3 == 12]
    if r3_twelve != list(range(20, 45, 2)):
        raise AssertionError("r3=12 parity boundary changed")
    if len(pairs) != 429:
        raise AssertionError("endpoint rank-pair count changed")

    return {
        "format": FORMAT,
        "role": "proof_a",
        "claim_label": "CANDIDATE",
        "git_commit": PUBLIC_BASE_COMMIT,
        "scope": (
            "Universal edge-local characteristic-seven rank consequence for "
            "a hypothetical srg(99,14,1,2), with conditional prism-free "
            "endpoint refinements"
        ),
        "transport_identity": {
            "vertex_triangle_incidence": "N",
            "integral_triangle_projector": "M=21E_0",
            "identity": "N M N^T = 27I - 9A + J",
            "modulo_seven_identification": (
                "27I-9A+J is congruent to the Seidel matrix J-I-2A"
            ),
            "rank_transfer_used": (
                "rank_F7(M)=rank_F7(NMN^T), because N is injective on "
                "im(M): N^T N M=(3I+Gamma)M=3M"
            ),
        },
        "edge_local_geometry": {
            "vertices": "L={x,y,z} union X union Y",
            "size": 27,
            "X_size": 12,
            "Y_size": 12,
            "forced_structure": (
                "xyz is a triangle; X and Y each induce a perfect matching; "
                "X--Y is a perfect matching; x sees X and y sees Y"
            ),
            "normal_form_count": len(normal_forms),
            "cycle_partition_total": 6,
            "cycle_lengths": "4m for parts m of a partition of 6",
            "rank_formula": "25 - 2*(number of even parts)",
            "normal_forms": normal_forms,
        },
        "universal_result": {
            "rank_F7_M_lower_bound": universal_floor,
            "previous_verified_lower_bound": 13,
            "rational_rank_upper_bound": TRIANGLE_PROJECTOR_RATIONAL_RANK,
        },
        "endpoint_result": {
            "conditional_on": "n3=4158, equivalently no induced triangular prism",
            "surviving_partitions": endpoint_partitions,
            "r7_lower_bound": endpoint_floor,
            "if_r3_equals_12": {
                "r7_parity": "even",
                "r7_lower_bound": 20,
                "admissible_r7_values": r3_twelve,
            },
            "admissible_rank_pair_count_after_update": len(pairs),
            "previous_admissible_rank_pair_count": 528,
            "low_rank_structural_consequences": {
                "r7_at_most_20": "every edge has local partition 2+2+2",
                "r7_at_most_22": "every edge has local partition 2+2+2 or 2+4",
                "r7_at_most_24": "no edge has local partition 3+3",
            },
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
        },
        "limitations": [
            "Discovery cannot verify itself.",
            "The rank floor is a necessary condition, not a graph construction.",
            "The 429 rank pairs are arithmetic survivors, not matrices or graphs.",
            "No endpoint contradiction, prism forcing theorem, or improved n3 upper bound follows.",
            "Novelty and priority remain UNKNOWN.",
        ],
        "target_status": "UNKNOWN",
    }


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output", type=Path)
    mode.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = canonical_json(exact_record())
    if args.verify:
        if args.verify.read_bytes() != payload:
            raise SystemExit("stored exact result differs from regeneration")
        print(f"PASS: {args.verify} matches exact regeneration")
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    else:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
