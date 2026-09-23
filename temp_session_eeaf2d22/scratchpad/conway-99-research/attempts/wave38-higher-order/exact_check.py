#!/usr/bin/env python3
"""Exact Wave 38 higher-order checks at the prism-free endpoint.

This discovery-side checker verifies:

* the signed support triangle and four-cycle imbalances forced by the
  endpoint reflection;
* a characteristic-three centering of the 231 factor rows;
* the exact rank bridge from the 19 triangles meeting a fixed graph
  triangle to an 18-vertex tripartite quotient graph; and
* a frozen connected one-triangle core showing that this local rank bridge
  alone does not eliminate the surviving ternary rank-twelve case.

It neither constructs a 60-column block system nor excludes the endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path


FIELD = 3
TRIANGLE_COUNT = 231
POSITIVE_MULTIPLICITY = 44
NEGATIVE_MULTIPLICITY = 187
SIGNED_POSITIVE_EIGENVALUE = 17
SIGNED_NEGATIVE_EIGENVALUE = -4
SUPPORT_DEGREE = 68
FIBRE_SIZE = 12
CORE_SIZE = 36

# A deterministic positive control found during discovery.  Row i is the
# 36-bit adjacency mask of vertex i.  The test suite checks symmetry and
# every asserted semantic property rather than trusting the encoding.
FROZEN_CORE_ROWS_HEX = (
    "800080002",
    "80001001",
    "1004008",
    "100020004",
    "200002020",
    "2800010",
    "40100080",
    "400010040",
    "4040200",
    "10400100",
    "20200800",
    "8008400",
    "2002002",
    "400001010",
    "200008004",
    "20004800",
    "1020080",
    "800010008",
    "8080100",
    "40040001",
    "80200040",
    "4100400",
    "100800200",
    "10400020",
    "2010004",
    "1001020",
    "8200100",
    "4040800",
    "20800200",
    "10008400",
    "80080040",
    "40100002",
    "200400008",
    "100004010",
    "800002080",
    "400020001",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    """Exact row rank over a prime field."""

    work = [[entry % prime for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(rank, rows)
                if work[row][column] % prime
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [(inverse * entry) % prime for entry in work[rank]]
        for row in range(rows):
            if row == rank:
                continue
            scale = work[row][column] % prime
            if scale:
                work[row] = [
                    (left - scale * right) % prime
                    for left, right in zip(work[row], work[rank])
                ]
        rank += 1
    return rank


def rational_rank(matrix: list[list[int]]) -> int:
    """Exact rational row rank for the 36-by-36 Gram control."""

    work = [[Fraction(entry) for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [entry / pivot_value for entry in work[rank]]
        for row in range(rows):
            if row == rank or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
    return rank


def signed_cycle_counts() -> dict[str, int]:
    """Return exact signed triangle and four-cycle imbalances."""

    trace_three = (
        POSITIVE_MULTIPLICITY * SIGNED_POSITIVE_EIGENVALUE**3
        + NEGATIVE_MULTIPLICITY * SIGNED_NEGATIVE_EIGENVALUE**3
    )
    trace_four = (
        POSITIVE_MULTIPLICITY * SIGNED_POSITIVE_EIGENVALUE**4
        + NEGATIVE_MULTIPLICITY * SIGNED_NEGATIVE_EIGENVALUE**4
    )
    triangle_difference = trace_three // 6
    nonsimple_closed_four_walks = (
        TRIANGLE_COUNT
        * SUPPORT_DEGREE
        * (2 * SUPPORT_DEGREE - 1)
    )
    require(trace_three % 6 == 0, "signed triangle trace lost integrality")
    require(
        (trace_four - nonsimple_closed_four_walks) % 8 == 0,
        "signed four-cycle trace lost integrality",
    )
    four_cycle_difference = (
        trace_four - nonsimple_closed_four_walks
    ) // 8
    require(trace_three == 204_204, "trace(S^3) changed")
    require(triangle_difference == 34_034, "triangle imbalance changed")
    require(trace_four == 3_722_796, "trace(S^4) changed")
    require(
        nonsimple_closed_four_walks == 2_120_580,
        "nonsimple length-four walk count changed",
    )
    require(four_cycle_difference == 200_277, "four-cycle imbalance changed")
    return {
        "trace_S_cubed": trace_three,
        "balanced_minus_unbalanced_support_triangles": triangle_difference,
        "trace_S_fourth": trace_four,
        "nonsimple_closed_signed_walks_length_four": (
            nonsimple_closed_four_walks
        ),
        "balanced_minus_unbalanced_support_four_cycles": (
            four_cycle_difference
        ),
    }


def ternary_centering() -> dict[str, object]:
    """Record the exact characteristic-three clique-sum centering lemma."""

    # These scalar checks audit the three possible entries of M N^T:
    # 4 on a triangle, -2 at a vertex adjacent to it, and 1 otherwise.
    reduced_values = {
        str(value): (2 * value) % FIELD
        for value in (4, -2, 1)
    }
    require(
        set(reduced_values.values()) == {2},
        "vertex-clique sums are not constant modulo three",
    )

    # A seven-triangle vertex clique consists of mutually C-orthogonal
    # norm-two rows.
    common_sum_norm = (7 * 2) % FIELD
    require(common_sum_norm == 2, "common clique sum lost norm two")

    clique_gram = [
        [0 if left == right else 1 for right in range(7)]
        for left in range(7)
    ]
    require(
        rank_mod(clique_gram, FIELD) == 6,
        "centered seven-clique Gram rank changed",
    )
    ones = [1] * 7
    require(
        all(
            sum(clique_gram[row][column] * ones[column]
                for column in range(7)) % FIELD == 0
            for row in range(7)
        ),
        "seven-clique all-one relation changed",
    )
    return {
        "factorization": "C=V H V^T over F_3",
        "vertex_clique_sum": (
            "w_x=sum_{T contains x} v_T is independent of x"
        ),
        "common_vector_norm": 2,
        "common_inner_product_with_every_v_T": 2,
        "centered_rows": "z_T=v_T-w",
        "centered_row_norm": 0,
        "centered_rows_orthogonal_to_w": True,
        "centered_gram": "D=C+J over F_3",
        "centered_gram_rank": "rank_F3(D)=r3-1",
        "vertex_clique_relation": (
            "sum_{T contains x} z_T=0 for every graph vertex x"
        ),
        "seven_clique_gram_rank": 6,
        "reduced_MNt_values": reduced_values,
    }


def core_adjacency() -> list[list[int]]:
    masks = [int(encoded, 16) for encoded in FROZEN_CORE_ROWS_HEX]
    require(len(masks) == CORE_SIZE, "frozen core row count changed")
    adjacency = [
        [
            (masks[left] >> right) & 1
            for right in range(CORE_SIZE)
        ]
        for left in range(CORE_SIZE)
    ]
    for left in range(CORE_SIZE):
        require(adjacency[left][left] == 0, "core acquired a loop")
        for right in range(CORE_SIZE):
            require(
                adjacency[left][right] == adjacency[right][left],
                "frozen core is not symmetric",
            )
    return adjacency


def neighbors(adjacency: list[list[int]], vertex: int) -> tuple[int, ...]:
    return tuple(
        neighbor
        for neighbor, entry in enumerate(adjacency[vertex])
        if entry
    )


def connected_components(adjacency: list[list[int]]) -> list[list[int]]:
    unseen = set(range(len(adjacency)))
    components: list[list[int]] = []
    while unseen:
        stack = [min(unseen)]
        component: list[int] = []
        while stack:
            vertex = stack.pop()
            if vertex not in unseen:
                continue
            unseen.remove(vertex)
            component.append(vertex)
            stack.extend(
                neighbor
                for neighbor in neighbors(adjacency, vertex)
                if neighbor in unseen
            )
        components.append(sorted(component))
    return components


def fibre_matchings(
    adjacency: list[list[int]],
) -> tuple[tuple[tuple[int, int], ...], ...]:
    matchings = []
    for fibre in range(3):
        start = fibre * FIBRE_SIZE
        pairs = tuple(
            (left - start, right - start)
            for left in range(start, start + FIBRE_SIZE)
            for right in range(left + 1, start + FIBRE_SIZE)
            if adjacency[left][right]
        )
        require(len(pairs) == 6, "within-fibre matching size changed")
        require(
            sorted(point for pair in pairs for point in pair)
            == list(range(FIBRE_SIZE)),
            "within-fibre edges are not a perfect matching",
        )
        matchings.append(pairs)
    return tuple(matchings)


def local_quotient(
    adjacency: list[list[int]],
) -> list[list[int]]:
    """Contract each within-fibre matching edge to obtain P on 18 labels."""

    matchings = fibre_matchings(adjacency)
    label_of: list[dict[int, int]] = []
    for matching in matchings:
        mapping = {
            point: label
            for label, pair in enumerate(matching)
            for point in pair
        }
        label_of.append(mapping)

    quotient = [[0] * 18 for _ in range(18)]
    for first_fibre, second_fibre in ((0, 1), (1, 2), (2, 0)):
        first_start = first_fibre * FIBRE_SIZE
        second_start = second_fibre * FIBRE_SIZE
        for first_point in range(FIBRE_SIZE):
            for second_point in range(FIBRE_SIZE):
                if not adjacency[
                    first_start + first_point
                ][
                    second_start + second_point
                ]:
                    continue
                first_label = 6 * first_fibre + label_of[first_fibre][
                    first_point
                ]
                second_label = 6 * second_fibre + label_of[second_fibre][
                    second_point
                ]
                quotient[first_label][second_label] += 1
                quotient[second_label][first_label] += 1

    require(
        all(entry in (0, 1) for row in quotient for entry in row),
        "quotient has a doubled edge, which would close a prism",
    )
    require(
        set(map(sum, quotient)) == {4},
        "quotient is not four-regular",
    )
    for first_fibre, second_fibre in ((0, 1), (1, 2), (2, 0)):
        for label in range(6):
            first_row = 6 * first_fibre + label
            require(
                sum(
                    quotient[first_row][6 * second_fibre + other]
                    for other in range(6)
                ) == 2,
                "quotient bipartite block is not two-regular",
            )
    return quotient


def local_centered_gram(quotient: list[list[int]]) -> list[list[int]]:
    """Return the 19-triangle centered Gram block over F_3."""

    gram = [[0] * 19 for _ in range(19)]
    for label in range(18):
        gram[0][1 + label] = 1
        gram[1 + label][0] = 1
    for left in range(18):
        for right in range(18):
            same_group = left // 6 == right // 6
            if left == right:
                value = 0
            elif same_group:
                value = 1
            else:
                value = 1 + quotient[left][right]
            gram[1 + left][1 + right] = value % FIELD
    return gram


def required_block_gram(
    adjacency: list[list[int]],
) -> list[list[int]]:
    adjacency_squared = [
        [
            sum(
                adjacency[left][middle] * adjacency[middle][right]
                for middle in range(CORE_SIZE)
            )
            for right in range(CORE_SIZE)
        ]
        for left in range(CORE_SIZE)
    ]
    return [
        [
            (
                (12 if left == right else 0)
                - adjacency[left][right]
                + 2
                - int(left // FIBRE_SIZE == right // FIBRE_SIZE)
                - adjacency_squared[left][right]
            )
            for right in range(CORE_SIZE)
        ]
        for left in range(CORE_SIZE)
    ]


def enumerate_individual_blocks(
    adjacency: list[list[int]],
) -> dict[str, object]:
    matching_edges = [
        set(fibre_matching)
        for fibre_matching in fibre_matchings(adjacency)
    ]
    allowed_pairs = [
        tuple(
            pair
            for pair in combinations(range(FIBRE_SIZE), 2)
            if pair not in matching_edges[fibre]
        )
        for fibre in range(3)
    ]
    require(
        [len(pairs) for pairs in allowed_pairs] == [60, 60, 60],
        "allowed pair counts changed",
    )
    neighbor_masks = [
        sum(1 << neighbor for neighbor in neighbors(adjacency, vertex))
        for vertex in range(CORE_SIZE)
    ]
    old_count = 0
    mixed_count = 0
    mixed_by_internal_edges: Counter[int] = Counter()
    for triple in product(*allowed_pairs):
        mask = 0
        for fibre, pair in enumerate(triple):
            for point in pair:
                mask |= 1 << (fibre * FIBRE_SIZE + point)

        internal_degree_sum = 0
        admissible = True
        for vertex in range(CORE_SIZE):
            if not (mask >> vertex) & 1:
                continue
            selected_degree = (
                neighbor_masks[vertex] & mask
            ).bit_count()
            if selected_degree > 1:
                admissible = False
                break
            internal_degree_sum += selected_degree
        if not admissible:
            continue
        old_count += 1
        internal_edges = internal_degree_sum // 2

        transfer = [
            2
            - ((mask >> vertex) & 1)
            - (neighbor_masks[vertex] & mask).bit_count()
            for vertex in range(CORE_SIZE)
        ]
        if min(transfer) < 0:
            continue
        require(sum(transfer) == 48, "mixed transfer sum changed")
        mixed_count += 1
        mixed_by_internal_edges[internal_edges] += 1

    require(old_count == 183_596, "old individual-block count changed")
    require(mixed_count == 152_399, "mixed-cut block count changed")
    require(
        mixed_by_internal_edges
        == Counter({0: 52_517, 1: 76_540, 2: 22_610, 3: 732}),
        "mixed-cut internal-edge histogram changed",
    )
    return {
        "allowed_pairs_per_fibre": [60, 60, 60],
        "induced_matching_survivors": old_count,
        "mixed_equation_survivors": mixed_count,
        "mixed_survivors_by_internal_X_edges": {
            str(key): value
            for key, value in sorted(mixed_by_internal_edges.items())
        },
    }


def frozen_core_control() -> dict[str, object]:
    adjacency = core_adjacency()
    require(set(map(sum, adjacency)) == {3}, "core is not cubic")
    require(
        connected_components(adjacency) == [list(range(CORE_SIZE))],
        "core is not connected",
    )
    require(
        all(
            sum(
                adjacency[left][middle] * adjacency[middle][right]
                for middle in range(CORE_SIZE)
            ) == 0
            for left in range(CORE_SIZE)
            for right in range(left + 1, CORE_SIZE)
            if adjacency[left][right]
        ),
        "core is not triangle-free",
    )

    pair_codegree_histogram: Counter[tuple[str, int]] = Counter()
    for left in range(CORE_SIZE):
        for right in range(left + 1, CORE_SIZE):
            codegree = sum(
                adjacency[left][middle] * adjacency[middle][right]
                for middle in range(CORE_SIZE)
            )
            same_fibre = left // FIBRE_SIZE == right // FIBRE_SIZE
            relation = (
                "edge"
                if adjacency[left][right]
                else "same_fibre_nonedge"
                if same_fibre
                else "cross_fibre_nonedge"
            )
            pair_codegree_histogram[(relation, codegree)] += 1
            if adjacency[left][right]:
                require(codegree == 0, "triangle-free edge has a common neighbor")
            elif same_fibre:
                require(
                    codegree <= 1,
                    "same-fibre pair makes the required B Gram negative",
                )
            else:
                require(
                    codegree <= 2,
                    "cross-fibre pair exceeds the target mu cap",
                )

    # Each pair of fibres must be joined by a perfect matching.
    for first, second in ((0, 1), (1, 2), (2, 0)):
        block_row_sums = [
            sum(
                adjacency[first * FIBRE_SIZE + point][
                    second * FIBRE_SIZE + other
                ]
                for other in range(FIBRE_SIZE)
            )
            for point in range(FIBRE_SIZE)
        ]
        block_column_sums = [
            sum(
                adjacency[first * FIBRE_SIZE + point][
                    second * FIBRE_SIZE + other
                ]
                for point in range(FIBRE_SIZE)
            )
            for other in range(FIBRE_SIZE)
        ]
        require(
            set(block_row_sums) == set(block_column_sums) == {1},
            "cross-fibre block is not a perfect matching",
        )

    quotient = local_quotient(adjacency)
    shifted_quotient = [
        [
            (quotient[left][right] - int(left == right)) % FIELD
            for right in range(18)
        ]
        for left in range(18)
    ]
    local_gram = local_centered_gram(quotient)
    quotient_rank = rank_mod(shifted_quotient, FIELD)
    local_gram_rank = rank_mod(local_gram, FIELD)
    require(quotient_rank == 10, "frozen quotient rank changed")
    require(
        local_gram_rank == quotient_rank,
        "19-triangle rank bridge failed",
    )

    gram = required_block_gram(adjacency)
    require(
        min(entry for row in gram for entry in row) >= 0,
        "required B Gram has a negative entry",
    )
    require(
        set(gram[index][index] for index in range(CORE_SIZE)) == {10},
        "required B Gram diagonal changed",
    )
    gram_rank = rational_rank(gram)
    require(gram_rank == 34, "required B Gram rational rank changed")
    require(
        all(sum(row) == 60 for row in gram),
        "required B Gram row sum changed",
    )

    upper_triangle_bits = "".join(
        str(adjacency[left][right])
        for left in range(CORE_SIZE)
        for right in range(left + 1, CORE_SIZE)
    ).encode("ascii")
    return {
        "adjacency_sha256_upper_triangle_bits": hashlib.sha256(
            upper_triangle_bits
        ).hexdigest(),
        "adjacency_rows_hex": list(FROZEN_CORE_ROWS_HEX),
        "vertices": CORE_SIZE,
        "edges": sum(map(sum, adjacency)) // 2,
        "degree": 3,
        "connected": True,
        "triangle_free": True,
        "component_partition_in_fibre_units": [12],
        "within_fibre_matchings": [
            [list(pair) for pair in matching]
            for matching in fibre_matchings(adjacency)
        ],
        "pair_codegree_histogram": {
            f"{relation}:{codegree}": count
            for (relation, codegree), count
            in sorted(pair_codegree_histogram.items())
        },
        "required_BBt_entry_minimum": 0,
        "required_BBt_rational_rank": gram_rank,
        "quotient_P_degree": 4,
        "quotient_bipartite_block_degree": 2,
        "quotient_P_minus_I_rank_F3": quotient_rank,
        "local_19_triangle_centered_gram_rank_F3": local_gram_rank,
        "individual_block_census": enumerate_individual_blocks(adjacency),
    }


def build_results() -> dict[str, object]:
    return {
        "claim_label": "DERIVED",
        "format": "wave38-higher-order-v1",
        "scope": (
            "Conditional prism-free endpoint n3=4158; exact signed "
            "four-cycle count and characteristic-three vertex-clique/local "
            "rank consequences"
        ),
        "frozen_commit": "3014f3b1c010cdde1687b8878d4ec58d2bb90f03",
        "signed_higher_order_counts": signed_cycle_counts(),
        "ternary_vertex_clique_centering": ternary_centering(),
        "fixed_triangle_rank_bridge": {
            "local_triangle_set_size": 19,
            "quotient_vertices": 18,
            "quotient_partition": [6, 6, 6],
            "quotient_degree": 4,
            "each_cross_block_degree": 2,
            "matrix": "P-I over F_3",
            "identity": (
                "rank_F3((C+J)[triangles meeting T])=rank_F3(P-I)"
            ),
            "global_ceiling": (
                "rank_F3(P-I)<=rank_F3(C+J)=r3-1"
            ),
            "conditional_closing_lemma": (
                "If every full endpoint forced some base triangle with "
                "rank_F3(P_T-I)>=12, then r3>=13 and the surviving "
                "rank-twelve ternary boundary would be excluded."
            ),
        },
        "frozen_local_positive_control": frozen_core_control(),
        "conclusion": {
            "new_exact_four_cycle_imbalance": 200_277,
            "new_ternary_centered_clique_structure": True,
            "local_rank_bridge_raises_verified_r3_floor": False,
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "target_status": "UNKNOWN",
            "smallest_missing_lemma": (
                "Use simultaneous 60-block B/H completion or cross-base-"
                "triangle compatibility to force rank_F3(P_T-I)>=12 for "
                "at least one base triangle; the one-triangle core axioms "
                "alone allow rank 10."
            ),
        },
        "limitations": [
            "The signed four-cycle imbalance is a necessary count, not an endpoint contradiction.",
            "The ternary centering and local rank bridge are discovery-side derivations pending independent verification.",
            "The frozen 36-vertex core is not a 60-column B, compatible H, 99-vertex graph, or endpoint construction.",
            "The individual block census does not impose simultaneous column compatibility.",
            "No endpoint exclusion or upper-bound improvement is claimed.",
        ],
    }


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    encoded = canonical_bytes(build_results())
    if arguments.verify is not None:
        if arguments.verify.read_bytes() != encoded:
            print(f"FAIL: {arguments.verify} differs", file=sys.stderr)
            return 1
        print(f"PASS: {arguments.verify} matches exact regeneration")
        return 0
    if arguments.output is not None:
        arguments.output.write_bytes(encoded)
        print(arguments.output)
        return 0
    sys.stdout.buffer.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
