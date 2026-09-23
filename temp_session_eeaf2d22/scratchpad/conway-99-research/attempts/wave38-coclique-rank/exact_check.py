#!/usr/bin/env python3
"""Exact checks for the 13-coclique characteristic-seven rank bound.

This is discovery code.  It verifies two elementary ingredients:

1. every putative srg(99,14,1,2) contains a 13-vertex coclique; and
2. for the integral triangle-projector matrix M, a coclique I satisfies

       N_I M N_I^T = 27 I_|I| + J_|I|.

For |I|=13 this matrix is nonsingular over F_7, so rank_F7(M) >= 13.
The computation is a conditional necessary result, not a graph construction
or an exclusion of the prism-free endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from typing import Iterable, Sequence


FORMAT = "wave38-coclique-rank-v1"
COCLIQUE_SIZE = 13
PRIME = 7


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def integer_partitions(total: int, minimum: int = 1) -> Iterable[tuple[int, ...]]:
    """Yield nondecreasing positive partitions of ``total``."""

    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for tail in integer_partitions(total - first, first):
            yield (first, *tail)


def local_cycle_graph(partition: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    """Return the normalized 2-regular graph on X_0..X_11,Y_0..Y_11.

    The X matching is fixed.  Contracting the X_i--Y_i matching turns the
    other two matchings into a union of alternating cycles.  ``partition``
    records the half-lengths of those cycles and therefore runs over the
    eleven partitions of six.
    """

    normalized = tuple(partition)
    if sum(normalized) != 6 or any(part < 1 for part in normalized):
        raise ValueError("partition must have positive parts summing to six")
    adjacency = [set() for _ in range(24)]

    def add_edge(left: int, right: int) -> None:
        if left == right or right in adjacency[left]:
            raise AssertionError((left, right))
        adjacency[left].add(right)
        adjacency[right].add(left)

    # The common-neighbor bijection between the two 12-point fibres.
    for point in range(12):
        add_edge(point, 12 + point)

    # The six triangles through the first endpoint.
    for point in range(0, 12, 2):
        add_edge(point, point + 1)

    # A representative of every orbit of the second endpoint matching.
    offset = 0
    for part in normalized:
        pairs = [
            (2 * (offset + index), 2 * (offset + index) + 1)
            for index in range(part)
        ]
        for index, (_, right) in enumerate(pairs):
            next_left = pairs[(index + 1) % part][0]
            add_edge(12 + right, 12 + next_left)
        offset += part

    result = tuple(tuple(sorted(neighbors)) for neighbors in adjacency)
    if any(len(neighbors) != 2 for neighbors in result):
        raise AssertionError("local graph is not 2-regular")
    return result


def bipartition(adjacency: Sequence[Sequence[int]]) -> tuple[int, ...]:
    """Return one color class of an even-cycle graph."""

    colors: list[int | None] = [None] * len(adjacency)
    for start in range(len(adjacency)):
        if colors[start] is not None:
            continue
        colors[start] = 0
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            assert colors[vertex] is not None
            for neighbor in adjacency[vertex]:
                wanted = 1 - int(colors[vertex])
                if colors[neighbor] is None:
                    colors[neighbor] = wanted
                    queue.append(neighbor)
                elif colors[neighbor] != wanted:
                    raise AssertionError("matching union contains an odd cycle")
    chosen = tuple(index for index, color in enumerate(colors) if color == 0)
    if len(chosen) != 12:
        raise AssertionError("local color class does not have size twelve")
    if any(
        right in adjacency[left]
        for position, left in enumerate(chosen)
        for right in chosen[position + 1 :]
    ):
        raise AssertionError("reported color class is not independent")
    return chosen


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    row_count = len(work)
    column_count = len(work[0]) if work else 0
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
        work[rank] = [(value * inverse) % prime for value in work[rank]]
        for row in range(row_count):
            if row == rank or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                (left - scale * right) % prime
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
    return rank


def coclique_gram(size: int) -> list[list[int]]:
    """Return 27I+J, including diagonal entries 28."""

    return [
        [28 if row == column else 1 for column in range(size)]
        for row in range(size)
    ]


def exact_record() -> dict[str, object]:
    partitions = tuple(integer_partitions(6))
    controls = []
    for partition in partitions:
        adjacency = local_cycle_graph(partition)
        chosen = bipartition(adjacency)
        controls.append(
            {
                "partition": list(partition),
                "component_sizes": sorted(
                    _component_sizes(adjacency)
                ),
                "local_independent_set_size": len(chosen),
            }
        )

    gram = coclique_gram(COCLIQUE_SIZE)
    determinant = 27 ** (COCLIQUE_SIZE - 1) * (27 + COCLIQUE_SIZE)
    residue = determinant % PRIME
    rank = rank_mod_prime(gram, PRIME)
    if residue == 0 or rank != COCLIQUE_SIZE:
        raise AssertionError("the coclique Gram block is not invertible modulo seven")

    record: dict[str, object] = {
        "format": FORMAT,
        "role": "proof_a",
        "claim_label": "CANDIDATE",
        "scope": (
            "necessary characteristic-seven rank condition for every "
            "hypothetical srg(99,14,1,2)"
        ),
        "coclique": {
            "guaranteed_size": COCLIQUE_SIZE,
            "construction": (
                "choose an edge xy with triangle mate z; the remaining "
                "12 neighbors of x and 12 neighbors of y form an even-cycle "
                "2-regular graph from the two local matchings and the "
                "cross matching; take one bipartition class and add z"
            ),
            "matching_union_partition_count": len(partitions),
            "normal_form_controls": controls,
        },
        "triangle_projector": {
            "definition": "M=21E_0 on the 231 graph triangles",
            "incidence_identity": "N M N^T = 27I - 9A + J",
            "coclique_gram": "N_I M N_I^T = 27I_13 + J_13",
            "determinant_formula": "27^12*(27+13)",
            "determinant": determinant,
            "determinant_mod_7": residue,
            "rank_mod_7": rank,
        },
        "result": {
            "rank_F7_M_lower_bound": COCLIQUE_SIZE,
            "previous_project_lower_bound": 11,
            "endpoint_rank_F7_C_lower_bound": COCLIQUE_SIZE,
            "endpoint_reason": "C=2M-21I is congruent to 2M modulo 7",
            "if_rank_F3_M_is_12_then_rank_F7_M_lower_bound": 14,
            "parity_reason": "rank_F3(M)+rank_F7(M) is even",
        },
        "limitations": [
            "The statement is conditional on existence of the target graph.",
            "It does not construct M, C, or a Conway graph.",
            "It does not exclude n3=4158 or improve n3<=4158.",
            "The 13-coclique construction is prior public mathematics; no novelty is claimed.",
            "The rank argument requires independent adversarial verification.",
        ],
    }
    return record


def _component_sizes(adjacency: Sequence[Sequence[int]]) -> tuple[int, ...]:
    unseen = set(range(len(adjacency)))
    sizes = []
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
            stack.extend(neighbor for neighbor in adjacency[vertex] if neighbor in unseen)
        sizes.append(size)
    return tuple(sorted(sizes))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output", type=Path)
    group.add_argument("--verify", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = canonical_json(exact_record())
    if args.verify:
        if args.verify.read_bytes() != payload:
            raise SystemExit("verification mismatch")
        print(f"verified {args.verify}")
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
