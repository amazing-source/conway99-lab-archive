#!/usr/bin/env python3
"""Exact Wave 36 checks for the one-triangle endpoint reduction.

The checker has two purposes.

1. It audits consequences that hold for every prism-free one-triangle core.
2. It applies the new mixed-block nonnegativity cut to the restricted Wave 35
   core and enumerates the surviving individual block types exactly.

It does not solve the simultaneous 60-block design and does not decide the
Conway-99 target.
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


N = 12
FIBRES = 3
X_SIZE = FIBRES * N
Y_SIZE = 60
WITHIN_FACTOR_INDICES = (1, 2, 3)


def one_factor(round_index: int) -> tuple[tuple[int, int], ...]:
    """Return round ``round_index`` of the standard K_12 one-factorization."""

    if not 0 <= round_index < N - 1:
        raise ValueError(round_index)
    modulus = N - 1
    pairs = [(N - 1, round_index)]
    for offset in range(1, N // 2):
        pairs.append(
            (
                (round_index + offset) % modulus,
                (round_index - offset) % modulus,
            )
        )
    return tuple(sorted(tuple(sorted(pair)) for pair in pairs))


FACTORS = tuple(one_factor(index) for index in range(N - 1))


def partner_map(factor: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    result = [-1] * N
    for left, right in factor:
        result[left] = right
        result[right] = left
    if any(value < 0 for value in result):
        raise AssertionError("not a perfect matching")
    return tuple(result)


SIGMA = partner_map(FACTORS[0])


def add_edge(matrix: list[list[int]], left: int, right: int) -> None:
    if left == right or matrix[left][right]:
        raise AssertionError((left, right))
    matrix[left][right] = 1
    matrix[right][left] = 1


def build_restricted_x_adjacency() -> list[list[int]]:
    """Build the normalized Wave 35 36-vertex cubic core."""

    adjacency = [[0] * X_SIZE for _ in range(X_SIZE)]
    for fibre, factor_index in enumerate(WITHIN_FACTOR_INDICES):
        for left, right in FACTORS[factor_index]:
            add_edge(
                adjacency,
                fibre * N + left,
                fibre * N + right,
            )
    for label in range(N):
        add_edge(adjacency, label, N + label)
        add_edge(adjacency, N + label, 2 * N + label)
        add_edge(adjacency, 2 * N + label, SIGMA[label])
    return adjacency


def matrix_multiply(
    left: list[list[int]],
    right: list[list[int]],
) -> list[list[int]]:
    rows = len(left)
    middle = len(right)
    columns = len(right[0])
    return [
        [
            sum(left[row][index] * right[index][column] for index in range(middle))
            for column in range(columns)
        ]
        for row in range(rows)
    ]


def matrix_square(matrix: list[list[int]]) -> list[list[int]]:
    return matrix_multiply(matrix, matrix)


def matrix_trace(matrix: list[list[int]]) -> int:
    return sum(matrix[index][index] for index in range(len(matrix)))


def matrix_power_trace(matrix: list[list[int]], exponent: int) -> int:
    if exponent < 1:
        raise ValueError(exponent)
    power = [row[:] for row in matrix]
    for _ in range(1, exponent):
        power = matrix_multiply(power, matrix)
    return matrix_trace(power)


def rational_rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    row_count = len(work)
    column_count = len(work[0])
    rank = 0
    for column in range(column_count):
        pivot = next(
            (
                row
                for row in range(rank, row_count)
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(row_count):
            if row == rank or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
    return rank


def connected_component_count(adjacency: list[list[int]]) -> int:
    unseen = set(range(len(adjacency)))
    count = 0
    while unseen:
        count += 1
        stack = [min(unseen)]
        while stack:
            vertex = stack.pop()
            if vertex not in unseen:
                continue
            unseen.remove(vertex)
            stack.extend(
                neighbor
                for neighbor, value in enumerate(adjacency[vertex])
                if value and neighbor in unseen
            )
    return count


def triangle_count(adjacency: list[list[int]]) -> int:
    return sum(
        adjacency[left][middle]
        * adjacency[middle][right]
        * adjacency[right][left]
        for left, middle, right in combinations(range(len(adjacency)), 3)
    )


def four_cycle_count(adjacency: list[list[int]]) -> int:
    squared = matrix_square(adjacency)
    total = 0
    for left, right in combinations(range(len(adjacency)), 2):
        common = squared[left][right]
        total += common * (common - 1) // 2
    if total % 2:
        raise AssertionError("each four-cycle must be counted twice")
    return total // 2


def required_xy_gram(adjacency: list[list[int]]) -> list[list[int]]:
    """Return the forced B B^T in the T|X|Y partition."""

    squared = matrix_square(adjacency)
    gram = [[0] * X_SIZE for _ in range(X_SIZE)]
    for left in range(X_SIZE):
        for right in range(X_SIZE):
            gram[left][right] = (
                (12 if left == right else 0)
                - adjacency[left][right]
                + 2
                - (1 if left // N == right // N else 0)
                - squared[left][right]
            )
    return gram


def allowed_pairs(factor_index: int) -> tuple[tuple[int, int], ...]:
    forbidden = set(FACTORS[factor_index])
    return tuple(
        pair
        for pair in combinations(range(N), 2)
        if pair not in forbidden
    )


def block_vector(
    pairs: tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
) -> tuple[int, ...]:
    selected = {
        fibre * N + point
        for fibre, pair in enumerate(pairs)
        for point in pair
    }
    return tuple(int(point in selected) for point in range(X_SIZE))


def transfer_target(
    adjacency: list[list[int]],
    block: tuple[int, ...],
    neighbors: tuple[tuple[int, ...], ...] | None = None,
) -> tuple[int, ...]:
    """Return d(b)=2*1-(I+A_X)b, forced to equal B h_y."""

    if neighbors is None:
        neighbors = tuple(
            tuple(
                neighbor
                for neighbor, value in enumerate(adjacency[point])
                if value
            )
            for point in range(X_SIZE)
        )
    return tuple(
        2
        - block[point]
        - sum(block[neighbor] for neighbor in neighbors[point])
        for point in range(X_SIZE)
    )


def internal_edge_count(
    adjacency: list[list[int]],
    block: tuple[int, ...],
) -> int:
    return sum(
        adjacency[left][right] * block[left] * block[right]
        for left, right in combinations(range(X_SIZE), 2)
    )


def old_matching_cut(
    adjacency: list[list[int]],
    block: tuple[int, ...],
) -> bool:
    selected = [point for point, value in enumerate(block) if value]
    return all(
        sum(adjacency[point][neighbor] for neighbor in selected) <= 1
        for point in selected
    )


def enumerate_restricted_blocks(
    adjacency: list[list[int]],
) -> dict[str, object]:
    pair_sets = tuple(
        allowed_pairs(factor_index)
        for factor_index in WITHIN_FACTOR_INDICES
    )
    old_total = 0
    new_total = 0
    old_by_edges: Counter[int] = Counter()
    new_by_edges: Counter[int] = Counter()
    target_signatures: Counter[tuple[int, int, int]] = Counter()
    rejected_by_negative_count: Counter[int] = Counter()
    neighbors = tuple(
        tuple(
            neighbor
            for neighbor, value in enumerate(adjacency[point])
            if value
        )
        for point in range(X_SIZE)
    )

    for pairs in product(*pair_sets):
        block = block_vector(pairs)
        degrees = tuple(
            sum(block[neighbor] for neighbor in neighbors[point])
            for point in range(X_SIZE)
        )
        if any(
            degrees[point] > 1
            for point, selected in enumerate(block)
            if selected
        ):
            continue
        old_total += 1
        edges = sum(
            degrees[point]
            for point, selected in enumerate(block)
            if selected
        ) // 2
        old_by_edges[edges] += 1
        target = tuple(
            2 - block[point] - degrees[point]
            for point in range(X_SIZE)
        )
        negative_count = sum(value < 0 for value in target)
        if negative_count:
            rejected_by_negative_count[negative_count] += 1
            continue
        if sum(target) != 48:
            raise AssertionError("eight neighboring six-blocks must total 48")
        if any(value not in (0, 1, 2) for value in target):
            raise AssertionError("unexpected nonnegative transfer value")
        new_total += 1
        new_by_edges[edges] += 1
        target_signatures[
            (
                target.count(0),
                target.count(1),
                target.count(2),
            )
        ] += 1

    return {
        "allowed_pair_count_per_fibre": [len(pairs) for pairs in pair_sets],
        "old_induced_matching_count": old_total,
        "old_by_internal_X_edges": {
            str(key): value
            for key, value in sorted(old_by_edges.items())
        },
        "mixed_equation_survivor_count": new_total,
        "removed_by_mixed_equation": old_total - new_total,
        "survivors_by_internal_X_edges": {
            str(key): value
            for key, value in sorted(new_by_edges.items())
        },
        "transfer_target_signature_n0_n1_n2": {
            ",".join(map(str, key)): value
            for key, value in sorted(target_signatures.items())
        },
        "rejected_by_negative_entry_count": {
            str(key): value
            for key, value in sorted(rejected_by_negative_count.items())
        },
    }


def adjacency_fingerprint(adjacency: list[list[int]]) -> str:
    encoded = "".join(
        str(adjacency[left][right])
        for left in range(X_SIZE)
        for right in range(left + 1, X_SIZE)
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def endpoint_component_partitions() -> tuple[tuple[int, ...], ...]:
    """Return the surviving partitions of 12 fibre labels by X components.

    A component containing ``m`` points of each fibre must have even ``m``.
    The case ``m=2`` would be K_3,3 and violates the global mu=2 equation.
    """

    result: set[tuple[int, ...]] = set()

    def visit(remaining: int, minimum: int, parts: tuple[int, ...]) -> None:
        if not remaining:
            result.add(parts)
            return
        for part in range(minimum, remaining + 1, 2):
            if part < 4:
                continue
            visit(remaining - part, part, parts + (part,))

    visit(12, 4, ())
    return tuple(sorted(result))


def component_pattern_constraints() -> dict[str, object]:
    """Return exact one-component block-pattern moment consequences."""

    return {
        "4": {
            "per_fibre_counts_z0_z1_z2": [24, 32, 4],
            "total_pattern_counts": {
                "permutations_of_2_0_0": 12,
                "permutations_of_1_1_0": 48,
            },
            "orientation_counts": {
                "2_0_0_with_each_double_coordinate": 4,
                "1_1_0_with_each_zero_coordinate": 16,
            },
        },
        "6": {
            "per_fibre_counts_z0_z1_z2": [12, 36, 12],
            "total_pattern_counts": {
                "1_1_1": 24,
                "permutations_of_2_1_0": 36,
            },
            "orientation_constraints": (
                "The 3-by-3 zero-diagonal count matrix indexed by "
                "(double coordinate, zero coordinate) has every row and "
                "column sum 12."
            ),
        },
        "8": {
            "per_fibre_counts_z0_z1_z2": [4, 32, 24],
            "total_pattern_counts": {
                "permutations_of_2_2_0": 12,
                "permutations_of_2_1_1": 48,
            },
            "orientation_counts": {
                "2_2_0_with_each_zero_coordinate": 4,
                "2_1_1_with_each_double_coordinate": 16,
            },
        },
        "12": {
            "per_fibre_counts_z0_z1_z2": [0, 0, 60],
            "total_pattern_counts": {"2_2_2": 60},
        },
    }


def build_results() -> dict[str, object]:
    factor_edges = tuple(edge for factor in FACTORS for edge in factor)
    if len(factor_edges) != 66 or len(set(factor_edges)) != 66:
        raise AssertionError("K_12 one-factorization failed")

    adjacency = build_restricted_x_adjacency()
    degree_set = sorted(set(map(sum, adjacency)))
    if degree_set != [3]:
        raise AssertionError(degree_set)
    triangles = triangle_count(adjacency)
    if triangles:
        raise AssertionError("restricted endpoint core is not triangle-free")
    components = connected_component_count(adjacency)
    cycles4 = four_cycle_count(adjacency)
    gram = required_xy_gram(adjacency)
    gram_rank = rational_rank(gram)

    fibre_difference_vectors = (
        tuple([1] * N + [-1] * N + [0] * N),
        tuple([1] * N + [0] * N + [-1] * N),
    )
    for vector in fibre_difference_vectors:
        if any(
            sum(gram[row][column] * vector[column] for column in range(X_SIZE))
            for row in range(X_SIZE)
        ):
            raise AssertionError("fibre-difference vector left the Gram kernel")
    if any(sum(row) != 60 for row in gram):
        raise AssertionError("Gram row sum is not 60")
    expected_rank = 35 - components
    if gram_rank != expected_rank:
        raise AssertionError((gram_rank, expected_rank))

    trace_a = {
        exponent: matrix_power_trace(adjacency, exponent)
        for exponent in range(1, 5)
    }
    expected_trace_a4 = X_SIZE * 3 * (2 * 3 - 1) + 8 * cycles4
    if trace_a != {
        1: 0,
        2: X_SIZE * 3,
        3: 6 * triangles,
        4: expected_trace_a4,
    }:
        raise AssertionError(trace_a)

    transferred_power_traces = {
        "1": 4 * components - 26,
        "2": 206 - 16 * components,
        "3": 154 + 64 * components,
        "4": 5318 - 256 * components + 8 * cycles4,
    }
    kernel_power_traces = {
        "1": 26 - 4 * components,
        "2": 274 + 16 * components,
        "3": 38 - 64 * components,
        "4": 3250 + 256 * components,
    }
    required_h_power_traces = {
        str(exponent): (
            transferred_power_traces[str(exponent)]
            + kernel_power_traces[str(exponent)]
        )
        for exponent in range(1, 5)
    }
    if required_h_power_traces != {
        "1": 0,
        "2": 480,
        "3": 192,
        "4": 8568 + 8 * cycles4,
    }:
        raise AssertionError(required_h_power_traces)

    block_census = enumerate_restricted_blocks(adjacency)

    return {
        "claim_label": "DERIVED",
        "format": "wave36-block-compatibility-v1",
        "frozen_scope": {
            "endpoint": "n3=4158, equivalently no induced triangular prisms",
            "partition_sizes_T_X_Y": [3, 36, 60],
            "public_input_commit": (
                "697cc02bcbe16b69aaf08822298e03c66329c64c"
            ),
        },
        "general_core_theorem": {
            "hypotheses": [
                "A_X is the cubic triangle-free 36-vertex core induced by a base triangle.",
                "Its three 12-point fibres have quotient matrix J_3.",
                "B is a binary 36-by-60 matrix with two ones per fibre in every column.",
                "H is a simple symmetric 60-by-60 adjacency matrix completing the SRG block equations.",
            ],
            "forced_equations": {
                "xx": "B B^T = 12I - A_X + 2J - R R^T - A_X^2",
                "xy": "B H = 2J - (I + A_X) B = (J/3 - I - A_X) B",
                "yy": "B^T B + H^2 = 12I - H + 2J",
            },
            "per_column_cut": {
                "formula": "d(b)=2*1-(I+A_X)b=B h_y",
                "consequence": "Every coordinate of d(b) is nonnegative.",
                "inside_B": "A_X[B] has maximum degree at most one.",
                "outside_B": "No outside X vertex has three neighbors in B.",
                "sum": 48,
            },
            "spectral_transfer": {
                "component_parameter": "c=number of connected components of A_X",
                "gram_rank": "rank(B B^T)=35-c",
                "row_space_action": (
                    "H on im(B^T) has eigenvalue 8 and eigenvalues "
                    "-1-lambda for every non-quotient, non-component-3 "
                    "eigenvalue lambda of A_X"
                ),
                "kernel_action": "H on ker(B) has spectrum 3^18,(-4)^(7+c)",
                "H_triangle_count": 32,
                "H_four_cycle_count": "171+C4(A_X)",
                "H_connected": (
                    "Yes: the displayed spectrum has exactly one eigenvalue 8."
                ),
                "characteristic_polynomial": (
                    "If chi_X(t)=(t-3)^c t^2 f(t), then "
                    "chi_H(t)=(-1)^(34-c)(t-8)(t-3)^18"
                    "(t+4)^(7+c)f(-1-t)."
                ),
            },
            "component_balance": {
                "component_shape": (
                    "Every X component has m vertices in each fibre and 3m total."
                ),
                "block_moments": (
                    "For z_y=|b_y intersect C|, sum_y z_y=30m and "
                    "sum_y z_y^2=15m^2."
                ),
                "equality_consequence": (
                    "All 60 blocks satisfy z_y=m/2; hence every component "
                    "parameter m is even."
                ),
                "m_equals_2_exclusion": (
                    "A connected cubic triangle-free graph on six vertices "
                    "is K_3,3, whose same-side nonedges have three common "
                    "X-neighbors, contradicting mu=2."
                ),
                "surviving_component_partitions_of_12": [
                    list(parts)
                    for parts in endpoint_component_partitions()
                ],
                "per_fibre_moments": (
                    "For z_iy=|b_y intersect (C cap X_i)|, "
                    "sum_y z_iy=10m, sum_y z_iy^2=m^2+8m, and "
                    "sum_y z_iy z_jy=2m(m-2) for i!=j."
                ),
                "disconnected_pattern_constraints": (
                    component_pattern_constraints()
                ),
                "partition_coupling": {
                    "4+8": (
                        "The m=8 pattern is the coordinatewise complement "
                        "2-z of the m=4 pattern."
                    ),
                    "6+6": (
                        "The two m=6 patterns are coordinatewise complements."
                    ),
                    "4+4+4": (
                        "Per block the only component-pattern combinations "
                        "are balanced AAA, aligned ABB, or balanced BBB, "
                        "where A is a permutation of (2,0,0) and B of (1,1,0)."
                    ),
                },
            },
            "pointwise_triangle_transfer": {
                "definition": "e_y=number of A_X edges induced by block b_y",
                "X-X-y_triangles": "e_y",
                "X-Y-y_triangles": "6-2e_y",
                "Y-Y-y_triangles": "1+e_y",
                "global_sum_e_y": 36,
            },
            "complete_fixed_core_reduction": [
                "Choose two permutations pairing the 60 allowed edges in fibre 0 with those in fibres 1 and 2.",
                "Require the three cross-fibre concurrence matrices to equal the off-diagonal blocks of B B^T.",
                "Require the per-column mixed-equation cut d(b)>=0.",
                "Choose a simple symmetric 8-regular H and enforce the exact xy and yy equations above.",
                "The resulting 3+36+60 block matrix satisfies A^2=12I-A+2J and is a full srg(99,14,1,2) certificate.",
            ],
        },
        "restricted_core": {
            "normalization": {
                "cross_matchings_X0X1_X1X2": "identity",
                "cross_matching_X2X0_factor": 0,
                "within_fibre_factor_indices": list(WITHIN_FACTOR_INDICES),
            },
            "adjacency_sha256_upper_triangle_bits": adjacency_fingerprint(adjacency),
            "vertex_count": X_SIZE,
            "edge_count": sum(map(sum, adjacency)) // 2,
            "degree_set": degree_set,
            "triangle_count": triangles,
            "four_cycle_count": cycles4,
            "connected_component_count": components,
            "gram_rational_rank": gram_rank,
            "transferred_H_power_traces_1_to_4": transferred_power_traces,
            "kernel_H_power_traces_1_to_4": kernel_power_traces,
            "required_H_power_traces_1_to_4": required_h_power_traces,
            "required_H_triangle_count": required_h_power_traces["3"] // 6,
            "required_H_four_cycle_count": (
                required_h_power_traces["4"] - Y_SIZE * 8 * 15
            )
            // 8,
            "individual_block_census": block_census,
        },
        "limitations": [
            "The restricted core fixes one derangement and three within-fibre one-factors.",
            "The 151712 survivors are individual columns, not a simultaneous 60-column design.",
            "No compatible H, full graph, endpoint exclusion, or upper-bound improvement is supplied.",
            "The spectral-transfer theorem is derived here but is not self-promoted to VERIFIED.",
            "Conway-99 and n3=4158 remain UNKNOWN.",
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
