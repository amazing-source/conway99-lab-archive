#!/usr/bin/env python3
"""Exact two-triangle overlap scout for the Conway-99 endpoint.

This is deliberately a bounded relaxation.  It glues two copies of the
canonical Wave 41 rank-33 one-triangle block across the 19 vertices forced
when the second base triangle uses an internal matching edge of the first
triangle's first fibre.  It then exhausts the individually admissible
cross-exclusive neighbour choices and computes their characteristic-seven
kernel signatures.

The program does not enumerate simultaneous 60-column designs, a compatible
outside graph, all rank-33 lifts, or all two-triangle overlap isomorphism
classes.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Sequence


FORMAT = "wave41-overlap-compatibility-v1"
PRIME = 7
LOCAL_ORDER = 39
CORE_ORDER = 36
FIBRE_SIZE = 12
UNION_ORDER = 59
ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "attempts/wave41-allquotient-lifts/exact-results.json"
INPUT_SHA256 = "da8098c5048c9b45ca3625131a98eb5473d29f864ea0c78a3e26d3b091b38e6d"
GIT_COMMIT = "4f1754a28723a8e0e4ea3025312cd264b1b117d2"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rank_mod_prime(
    matrix: Sequence[Sequence[int]], prime: int = PRIME
) -> int:
    return len(rref(matrix, prime)[1])


def rref(
    matrix: Sequence[Sequence[int]], prime: int = PRIME
) -> tuple[list[list[int]], tuple[int, ...]]:
    if not matrix:
        return [], ()
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "ragged matrix")
    work = [[entry % prime for entry in row] for row in matrix]
    rank = 0
    pivots: list[int] = []
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(rank, len(work))
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [
            entry * inverse % prime for entry in work[rank]
        ]
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (left - factor * right) % prime
                for left, right in zip(work[row], work[rank])
            ]
        pivots.append(column)
        rank += 1
        if rank == len(work):
            break
    return work, tuple(pivots)


def kernel_basis(
    matrix: Sequence[Sequence[int]], prime: int = PRIME
) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = rref(matrix, prime)
    width = len(matrix[0])
    basis: list[tuple[int, ...]] = []
    for free in range(width):
        if free in pivots:
            continue
        vector = [0] * width
        vector[free] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free] % prime
        require(
            all(
                sum(matrix[row][column] * vector[column]
                    for column in range(width)) % prime == 0
                for row in range(len(matrix))
            ),
            "kernel reconstruction failed",
        )
        basis.append(tuple(vector))
    return tuple(basis)


def add_edge(adjacency: list[list[int]], left: int, right: int) -> None:
    require(left != right, "loop requested")
    adjacency[left][right] = adjacency[right][left] = 1


def input_witness() -> dict[str, object]:
    require(file_sha256(INPUT) == INPUT_SHA256, "Wave 41 input changed")
    result = json.loads(INPUT.read_text(encoding="utf-8"))
    witness = result["rank_eleven_boundary"]["all_cases"][0][
        "canonical_minimum_witness"
    ]
    require(witness["rank_F7_K39"] == 33, "input witness rank changed")
    require(witness["triangle_count"] == 0, "input witness gained a triangle")
    return witness


def canonical_core() -> list[list[int]]:
    witness = input_witness()
    adjacency = [[0] * CORE_ORDER for _ in range(CORE_ORDER)]
    for left, right in witness["edges"]:
        add_edge(adjacency, int(left), int(right))
    require(set(map(sum, adjacency)) == {3}, "core is not cubic")
    require(
        triangle_count(adjacency) == 0,
        "canonical core is not triangle-free",
    )
    return adjacency


def local_block(core: Sequence[Sequence[int]]) -> list[list[int]]:
    adjacency = [[0] * LOCAL_ORDER for _ in range(LOCAL_ORDER)]
    for left, right in ((0, 1), (0, 2), (1, 2)):
        add_edge(adjacency, left, right)
    for fibre in range(3):
        for point in range(FIBRE_SIZE):
            add_edge(adjacency, fibre, 3 + fibre * FIBRE_SIZE + point)
    for left in range(CORE_ORDER):
        for right in range(left + 1, CORE_ORDER):
            if core[left][right]:
                add_edge(adjacency, 3 + left, 3 + right)
    return adjacency


def triangle_count(adjacency: Sequence[Sequence[int]]) -> int:
    return sum(
        adjacency[first][second]
        and adjacency[first][third]
        and adjacency[second][third]
        for first in range(len(adjacency))
        for second in range(first + 1, len(adjacency))
        for third in range(second + 1, len(adjacency))
    )


def seidel(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            0 if row == column else -1 if adjacency[row][column] else 1
            for column in range(len(adjacency))
        ]
        for row in range(len(adjacency))
    ]


def internal_matching(
    core: Sequence[Sequence[int]], fibre: int
) -> tuple[tuple[int, int], ...]:
    offset = fibre * FIBRE_SIZE
    edges = tuple(
        (left, right)
        for left in range(FIBRE_SIZE)
        for right in range(left + 1, FIBRE_SIZE)
        if core[offset + left][offset + right]
    )
    require(len(edges) == 6, "fibre matching size changed")
    require(
        sorted(point for edge in edges for point in edge)
        == list(range(FIBRE_SIZE)),
        "fibre matching does not cover its fibre",
    )
    return edges


def matching_map(edges: Iterable[tuple[int, int]]) -> tuple[int, ...]:
    result = [-1] * FIBRE_SIZE
    for left, right in edges:
        require(result[left] == result[right] == -1, "matching repeats a point")
        result[left] = right
        result[right] = left
    require(-1 not in result, "matching is incomplete")
    return tuple(result)


def cycle_partition(
    first: Sequence[int], second: Sequence[int]
) -> tuple[int, ...]:
    unseen = set(range(FIBRE_SIZE))
    parts: list[int] = []
    while unseen:
        start = min(unseen)
        vertex = start
        relation = 0
        size = 0
        while vertex in unseen:
            unseen.remove(vertex)
            size += 1
            vertex = (first if relation == 0 else second)[vertex]
            relation ^= 1
        require(size % 2 == 0, "alternating component has odd order")
        parts.append(size // 2)
    return tuple(sorted(parts))


def three_side_types(
    core: Sequence[Sequence[int]],
) -> dict[str, list[int]]:
    matchings = [
        matching_map(internal_matching(core, fibre))
        for fibre in range(3)
    ]
    result: dict[str, list[int]] = {}
    for left_fibre, right_fibre in ((0, 1), (1, 2), (2, 0)):
        cross: dict[int, int] = {}
        for left in range(FIBRE_SIZE):
            neighbors = [
                right
                for right in range(FIBRE_SIZE)
                if core[left_fibre * FIBRE_SIZE + left][
                    right_fibre * FIBRE_SIZE + right
                ]
            ]
            require(len(neighbors) == 1, "cross block is not a matching")
            cross[left] = neighbors[0]
        require(len(set(cross.values())) == FIBRE_SIZE, "cross map is not bijective")
        pulled = [0] * FIBRE_SIZE
        inverse = {right: left for left, right in cross.items()}
        for left in range(FIBRE_SIZE):
            right = cross[left]
            pulled[left] = inverse[matchings[right_fibre][right]]
        partition = cycle_partition(matchings[left_fibre], pulled)
        result[f"{left_fibre}-{right_fibre}"] = list(partition)
    return result


def fixed_gluing() -> tuple[
    list[list[int]], dict[int, int], tuple[int, ...], tuple[int, ...], tuple[int, ...]
]:
    """Glue two canonical blocks along one exact 19-vertex overlap.

    In the first block, the second base triangle is ``(0,3,4)``.  The map
    below sends the base, the complete first fibre, and the four already
    visible cross-fibre neighbors of 3 and 4 to the corresponding vertices
    of the second block.  The remaining twenty vertices are new.
    """

    core = canonical_core()
    first = local_block(core)
    second = local_block(core)

    # Actual first-block vertex -> target second-core fibre-0 point.
    fibre_zero_map = {
        1: 0,
        2: 1,
        5: 2,
        6: 3,
        7: 4,
        8: 5,
        9: 6,
        10: 7,
        11: 8,
        12: 9,
        13: 10,
        14: 11,
    }
    target_to_union: dict[int, int] = {0: 0, 1: 3, 2: 4}
    for actual, target_point in fibre_zero_map.items():
        target_to_union[3 + target_point] = actual

    # The four visible cross-fibre neighbors in the first block.
    target_to_union.update({15: 15, 17: 29, 29: 17, 27: 27})
    next_vertex = LOCAL_ORDER
    for target in range(LOCAL_ORDER):
        if target not in target_to_union:
            target_to_union[target] = next_vertex
            next_vertex += 1
    require(next_vertex == UNION_ORDER, "glued union order changed")
    require(
        len(set(target_to_union.values())) == LOCAL_ORDER,
        "second block map is not injective",
    )

    union = [[0] * UNION_ORDER for _ in range(UNION_ORDER)]
    for left in range(LOCAL_ORDER):
        for right in range(left + 1, LOCAL_ORDER):
            if first[left][right]:
                add_edge(union, left, right)
    for left in range(LOCAL_ORDER):
        for right in range(left + 1, LOCAL_ORDER):
            image_left = target_to_union[left]
            image_right = target_to_union[right]
            if image_left < LOCAL_ORDER and image_right < LOCAL_ORDER:
                require(
                    union[image_left][image_right] == second[left][right],
                    "the two local blocks disagree on their overlap",
                )
            if second[left][right]:
                add_edge(union, image_left, image_right)

    first_vertices = set(range(LOCAL_ORDER))
    second_vertices = set(target_to_union.values())
    overlap = tuple(sorted(first_vertices & second_vertices))
    first_exclusive = tuple(sorted(first_vertices - second_vertices))
    second_exclusive = tuple(sorted(second_vertices - first_vertices))
    require(
        (len(overlap), len(first_exclusive), len(second_exclusive))
        == (19, 20, 20),
        "overlap profile changed",
    )
    return (
        union,
        target_to_union,
        overlap,
        first_exclusive,
        second_exclusive,
    )


def canonical_subspace(
    vectors: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    if not vectors:
        return ()
    reduced, pivots = rref(vectors)
    return tuple(tuple(reduced[row]) for row in range(len(pivots)))


def support_options_and_signatures() -> dict[str, object]:
    union, mapping, overlap, first_exclusive, second_exclusive = fixed_gluing()
    first = [row[:LOCAL_ORDER] for row in union[:LOCAL_ORDER]]
    first_k = seidel(first)
    kernel = kernel_basis(first_k)
    require(
        (rank_mod_prime(first_k), len(kernel)) == (33, 6),
        "first local rank/nullity changed",
    )

    neighbor_masks = [
        sum(1 << neighbor for neighbor in range(LOCAL_ORDER)
            if first[vertex][neighbor])
        for vertex in range(LOCAL_ORDER)
    ]
    signature_sets: list[set[tuple[int, ...]]] = []
    option_counts: list[int] = []
    witnesses: list[dict[tuple[int, ...], tuple[int, ...]]] = []

    for vertex in second_exclusive:
        fixed = {
            point for point in overlap if union[vertex][point]
        }
        fixed_counts = [
            sum(
                3 + fibre * FIBRE_SIZE
                <= point
                < 3 + (fibre + 1) * FIBRE_SIZE
                for point in fixed
            )
            for fibre in range(3)
        ]
        require(fixed_counts[0] == 2, "new vertex lost its two fibre-0 neighbors")
        pools = [
            tuple(
                point
                for point in first_exclusive
                if 3 + fibre * FIBRE_SIZE
                <= point
                < 3 + (fibre + 1) * FIBRE_SIZE
            )
            for fibre in range(3)
        ]
        signatures: set[tuple[int, ...]] = set()
        signature_witnesses: dict[tuple[int, ...], tuple[int, ...]] = {}
        count = 0
        for fibre_one in itertools.combinations(
            pools[1], 2 - fixed_counts[1]
        ):
            for fibre_two in itertools.combinations(
                pools[2], 2 - fixed_counts[2]
            ):
                chosen = tuple(sorted(fibre_one + fibre_two))
                support = fixed | set(chosen)
                support_mask = sum(1 << point for point in support)

                # Necessary SRG support cap.  A selected core point can have
                # at most one selected core neighbor; an unselected core
                # point can have at most two.
                if any(
                    (neighbor_masks[point] & support_mask).bit_count()
                    > (1 if point in support else 2)
                    for point in range(LOCAL_ORDER)
                ):
                    continue

                column = tuple(
                    -1 if point in support else 1
                    for point in range(LOCAL_ORDER)
                )
                signature = tuple(
                    sum(
                        kernel_vector[point] * column[point]
                        for point in range(LOCAL_ORDER)
                    ) % PRIME
                    for kernel_vector in kernel
                )
                signatures.add(signature)
                previous = signature_witnesses.get(signature)
                if previous is None or chosen < previous:
                    signature_witnesses[signature] = chosen
                count += 1
        require(count > 0 and signatures, "a new vertex has no individual support")
        option_counts.append(count)
        signature_sets.append(signatures)
        witnesses.append(signature_witnesses)

    states: set[tuple[tuple[int, ...], ...]] = {()}
    state_counts = []
    for signatures in signature_sets:
        states = {
            canonical_subspace(tuple(state) + (signature,))
            for state in states
            for signature in signatures
        }
        state_counts.append(len(states))
    minimum_signature_rank = min(map(len, states))
    require(minimum_signature_rank == 1, "minimum signature span changed")
    rank_distribution = {
        str(dimension): sum(len(state) == dimension for state in states)
        for dimension in sorted({len(state) for state in states})
    }
    require(
        rank_distribution == {"1": 13, "2": 56, "3": 1},
        "terminal signature-subspace distribution changed",
    )

    target_line = min(state for state in states if len(state) == 1)
    zero = (0,) * len(kernel)
    selected_supports: list[tuple[int, ...]] = []
    selected_signatures: list[tuple[int, ...]] = []
    for signatures, signature_witnesses in zip(
        signature_sets, witnesses, strict=True
    ):
        compatible = sorted(
            signature
            for signature in signatures
            if signature == zero
            or canonical_subspace((signature,)) == target_line
        )
        require(compatible, "target one-space lacks a per-vertex choice")
        signature = compatible[0]
        selected_signatures.append(signature)
        selected_supports.append(signature_witnesses[signature])
    require(
        rank_mod_prime(selected_signatures) == 1,
        "explicit signature witness does not span one dimension",
    )

    # Complete only the twenty-by-twenty cross-exclusive graph block using
    # the selected individual supports.  This is an explicit relaxation
    # control, not a completed SRG.
    completed = [row[:] for row in union]
    for vertex, support in zip(
        second_exclusive, selected_supports, strict=True
    ):
        for point in support:
            add_edge(completed, vertex, point)
    completed_rank = rank_mod_prime(seidel(completed))

    return {
        "first_local_rank_F7": 33,
        "first_local_kernel_dimension": 6,
        "second_exclusive_vertices": list(second_exclusive),
        "individual_support_option_counts": option_counts,
        "signature_set_sizes": [len(signatures) for signatures in signature_sets],
        "terminal_signature_subspace_count": len(states),
        "terminal_signature_subspace_rank_distribution": rank_distribution,
        "minimum_joint_signature_span": minimum_signature_rank,
        "border_congruence_floor": 33 + 2 * minimum_signature_rank,
        "explicit_one_space": [list(row) for row in target_line],
        "explicit_cross_exclusive_supports": [
            list(support) for support in selected_supports
        ],
        "explicit_relaxation_union_rank_F7": completed_rank,
        "scope": (
            "Individual balanced/support-cap columns only; no simultaneous "
            "BB^T design, outside H, pairwise column compatibility, or SRG."
        ),
    }


def build_results() -> dict[str, object]:
    core = canonical_core()
    local = local_block(core)
    local_k_rank = rank_mod_prime(seidel(local))
    require(local_k_rank == 33, "canonical local K rank changed")
    side_types = three_side_types(core)
    require(
        set(tuple(value) for value in side_types.values()) == {(2, 2, 2)},
        "canonical core is not all-222",
    )
    union, mapping, overlap, first_exclusive, second_exclusive = fixed_gluing()
    second_vertices = sorted(mapping.values())
    require(
        rank_mod_prime(
            [[seidel(union)[left][right] for right in second_vertices]
             for left in second_vertices]
        )
        == 33,
        "second local K rank changed",
    )
    return {
        "format": FORMAT,
        "git_commit": GIT_COMMIT,
        "claim_label": "CANDIDATE",
        "hypotheses": [
            "n3=4158 (prism-free endpoint)",
            "rank_F3(M)=12",
            "all 693 graph edges have local type 2+2+2",
            "both selected one-triangle blocks use the canonical rank-33 Wave 41 lift",
        ],
        "input": {
            str(INPUT.relative_to(ROOT)).replace("\\", "/"): INPUT_SHA256
        },
        "canonical_local_block": {
            "vertices": LOCAL_ORDER,
            "core_vertices": CORE_ORDER,
            "core_cubic": set(map(sum, core)) == {3},
            "core_triangle_count": triangle_count(core),
            "three_base_edge_types": side_types,
            "rank_F7_K39": local_k_rank,
            "nullity_F7_K39": LOCAL_ORDER - local_k_rank,
        },
        "two_triangle_overlap": {
            "first_base_triangle": [0, 1, 2],
            "second_base_triangle": [0, 3, 4],
            "overlap_vertices": list(overlap),
            "overlap_size": len(overlap),
            "first_exclusive_size": len(first_exclusive),
            "second_exclusive_size": len(second_exclusive),
            "second_local_to_union_map": {
                str(key): value for key, value in sorted(mapping.items())
            },
            "induced_overlap_agreement": True,
            "both_local_K39_ranks_F7": [33, 33],
        },
        "balanced_border_census": support_options_and_signatures(),
        "conclusion": {
            "exact_positive_control": (
                "Two copies of the canonical rank-33 all-222 block agree "
                "exactly on the forced 19-vertex overlap."
            ),
            "first_order_border_result": (
                "After every new vertex is required to have two neighbors "
                "in each old fibre and pass the individual common-neighbor "
                "support cap, the twenty kernel signatures can still span "
                "one dimension.  The raw congruence floor is only 35."
            ),
            "endpoint_excluded": False,
            "upper_bound_improved": False,
            "target_status": "UNKNOWN",
        },
        "limitations": [
            "This is one fixed self-overlap of one canonical rank-33 lift, not all 264 masks or all overlap classes.",
            "The per-column choices do not realize the simultaneous forced BB^T Gram matrix.",
            "No compatible 60-vertex outside graph H is constructed.",
            "The explicit 59-vertex relaxation is not regular and is not an SRG.",
            "The rank-35 border floor is weaker than the global closing threshold.",
            "Discovery cannot verify its own candidate package.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = build_results()
    payload = canonical_bytes(result)
    if args.verify is not None:
        require(args.verify.read_bytes() == payload, "stored result differs")
    if args.output is not None:
        args.output.write_bytes(payload)
    if args.output is None and args.verify is None:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
