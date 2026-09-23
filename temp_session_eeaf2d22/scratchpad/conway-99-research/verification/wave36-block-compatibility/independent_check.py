#!/usr/bin/env python3
"""Independent checks for the Wave 36 one-triangle block claims.

This file deliberately does not import either Wave 35 or Wave 36 discovery
code.  It reconstructs the published restricted core from the frozen
normalization and independently enumerates its candidate columns.

The general arguments are conditional on the one-triangle endpoint premises:

* A_X is a cubic triangle-free graph on three fibres of size 12;
* every vertex has one A_X-neighbour in each fibre (including its own);
* B is 36 by 60, with row sum 10 and two ones per fibre in every column;
* H is a simple symmetric 8-regular graph; and
* the full adjacency matrix obeys A^2 = 12I - A + 2J.

No simultaneous B or H is constructed or excluded here.
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


FIBRE_SIZE = 12
FIBRE_COUNT = 3
X_SIZE = FIBRE_SIZE * FIBRE_COUNT
Y_SIZE = 60
WITHIN_ROUNDS = (1, 2, 3)

# Frozen Wave 35 X0-X1 edge bijection.  It is data, not a discovery claim:
# entry i maps the lexicographic i-th allowed X0 pair to this X1-pair index.
FROZEN_PAIR_01 = (
    38, 47, 19, 12, 59, 57, 7, 28, 14, 48,
    43, 3, 10, 25, 36, 54, 33, 5, 50, 11,
    52, 27, 0, 29, 22, 55, 56, 45, 49, 58,
    24, 1, 53, 32, 35, 9, 44, 46, 13, 39,
    31, 30, 37, 15, 26, 4, 16, 8, 20, 34,
    21, 18, 2, 17, 41, 6, 40, 42, 23, 51,
)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def circle_matching(round_number: int) -> tuple[tuple[int, int], ...]:
    """One round of the circle construction for a K_12 one-factorization."""

    if round_number not in range(11):
        raise ValueError(round_number)
    fixed = 11
    pairs = [(fixed, round_number)]
    for distance in range(1, 6):
        pairs.append(
            (
                (round_number - distance) % 11,
                (round_number + distance) % 11,
            )
        )
    return tuple(sorted(tuple(sorted(edge)) for edge in pairs))


FACTORS = tuple(circle_matching(round_number) for round_number in range(11))


def matching_involution(edges: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    image = [-1] * FIBRE_SIZE
    for left, right in edges:
        image[left] = right
        image[right] = left
    if sorted(image) != list(range(FIBRE_SIZE)):
        raise AssertionError("not a fixed-point-free involution")
    return tuple(image)


def restricted_core() -> tuple[int, ...]:
    """Return adjacency rows as bitsets for the frozen Wave 35 core."""

    rows = [0] * X_SIZE

    def join(left: int, right: int) -> None:
        if left == right or rows[left] & (1 << right):
            raise AssertionError((left, right))
        rows[left] |= 1 << right
        rows[right] |= 1 << left

    for fibre, round_number in enumerate(WITHIN_ROUNDS):
        for left, right in FACTORS[round_number]:
            join(fibre * FIBRE_SIZE + left, fibre * FIBRE_SIZE + right)

    sigma = matching_involution(FACTORS[0])
    for label in range(FIBRE_SIZE):
        join(label, FIBRE_SIZE + label)
        join(FIBRE_SIZE + label, 2 * FIBRE_SIZE + label)
        join(2 * FIBRE_SIZE + label, sigma[label])

    return tuple(rows)


def adjacency_matrix(rows: tuple[int, ...]) -> list[list[int]]:
    return [
        [(rows[left] >> right) & 1 for right in range(len(rows))]
        for left in range(len(rows))
    ]


def matmul(
    left: list[list[int]],
    right: list[list[int]],
) -> list[list[int]]:
    return [
        [
            sum(x * y for x, y in zip(left_row, right_column))
            for right_column in zip(*right)
        ]
        for left_row in left
    ]


def matrix_square(matrix: list[list[int]]) -> list[list[int]]:
    return matmul(matrix, matrix)


def trace_power(matrix: list[list[int]], exponent: int) -> int:
    if exponent < 1:
        raise ValueError(exponent)
    power = [row[:] for row in matrix]
    for _ in range(exponent - 1):
        power = matmul(power, matrix)
    return sum(power[index][index] for index in range(len(matrix)))


def rational_rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(entry) for entry in row] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (
                row
                for row in range(pivot_row, len(work))
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [entry / divisor for entry in work[pivot_row]]
        for row in range(pivot_row + 1, len(work)):
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    entry - multiplier * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
    return pivot_row


def component_count(rows: tuple[int, ...]) -> int:
    unseen = set(range(len(rows)))
    count = 0
    while unseen:
        count += 1
        stack = [next(iter(unseen))]
        while stack:
            vertex = stack.pop()
            if vertex not in unseen:
                continue
            unseen.remove(vertex)
            stack.extend(
                neighbor
                for neighbor in unseen
                if rows[vertex] & (1 << neighbor)
            )
    return count


def triangle_count(rows: tuple[int, ...]) -> int:
    total = 0
    for left in range(len(rows)):
        for middle in range(left + 1, len(rows)):
            if not rows[left] & (1 << middle):
                continue
            common = rows[left] & rows[middle]
            total += sum(
                1
                for right in range(middle + 1, len(rows))
                if common & (1 << right)
            )
    return total


def four_cycle_count(rows: tuple[int, ...]) -> int:
    doubled = 0
    for left, right in combinations(range(len(rows)), 2):
        common = (rows[left] & rows[right]).bit_count()
        doubled += common * (common - 1) // 2
    if doubled % 2:
        raise AssertionError("four-cycle double count is odd")
    return doubled // 2


def forced_gram(rows: tuple[int, ...]) -> list[list[int]]:
    """Compute 12I-A_X+2J-RR^T-A_X^2 from the reconstructed core."""

    matrix = adjacency_matrix(rows)
    squared = matrix_square(matrix)
    return [
        [
            (12 if left == right else 0)
            - matrix[left][right]
            + 2
            - int(left // FIBRE_SIZE == right // FIBRE_SIZE)
            - squared[left][right]
            for right in range(X_SIZE)
        ]
        for left in range(X_SIZE)
    ]


def allowed_pairs(round_number: int) -> tuple[tuple[int, int], ...]:
    forbidden = set(FACTORS[round_number])
    return tuple(
        edge
        for edge in combinations(range(FIBRE_SIZE), 2)
        if edge not in forbidden
    )


def selection_mask(edges: tuple[tuple[int, int], ...]) -> int:
    mask = 0
    for fibre, edge in enumerate(edges):
        for point in edge:
            mask |= 1 << (fibre * FIBRE_SIZE + point)
    if mask.bit_count() != 6:
        raise AssertionError("block is not of shape (2,2,2)")
    return mask


def block_statistics(
    rows: tuple[int, ...],
    mask: int,
) -> tuple[bool, bool, int, int]:
    """Return old-cut, new-cut, internal-edge count, negative-entry count."""

    selected_degrees = [
        (rows[point] & mask).bit_count()
        for point in range(X_SIZE)
        if mask & (1 << point)
    ]
    old_cut = max(selected_degrees) <= 1
    internal_edges = sum(selected_degrees) // 2
    transfer = [
        2 - int(bool(mask & (1 << point))) - (rows[point] & mask).bit_count()
        for point in range(X_SIZE)
    ]
    negative_count = sum(entry < 0 for entry in transfer)
    return old_cut, old_cut and negative_count == 0, internal_edges, negative_count


def exhaustive_column_census(rows: tuple[int, ...]) -> dict[str, object]:
    pair_sets = tuple(allowed_pairs(round_number) for round_number in WITHIN_ROUNDS)
    old_by_edges: Counter[int] = Counter()
    new_by_edges: Counter[int] = Counter()
    rejected_by_negative_entries: Counter[int] = Counter()
    transfer_signatures: Counter[tuple[int, int, int]] = Counter()

    for edges in product(*pair_sets):
        mask = selection_mask(edges)
        old_cut, new_cut, internal_edges, negative_count = block_statistics(
            rows, mask
        )
        if not old_cut:
            continue
        old_by_edges[internal_edges] += 1
        if not new_cut:
            rejected_by_negative_entries[negative_count] += 1
            continue
        new_by_edges[internal_edges] += 1
        transfer = [
            2
            - int(bool(mask & (1 << point)))
            - (rows[point] & mask).bit_count()
            for point in range(X_SIZE)
        ]
        transfer_signatures[
            (transfer.count(0), transfer.count(1), transfer.count(2))
        ] += 1

    return {
        "raw_triples": len(pair_sets[0]) * len(pair_sets[1]) * len(pair_sets[2]),
        "allowed_pairs_per_fibre": [len(pairs) for pairs in pair_sets],
        "old_count": sum(old_by_edges.values()),
        "old_by_internal_edges": dict(sorted(old_by_edges.items())),
        "new_count": sum(new_by_edges.values()),
        "new_by_internal_edges": dict(sorted(new_by_edges.items())),
        "removed": sum(rejected_by_negative_entries.values()),
        "rejected_by_negative_entry_count": dict(
            sorted(rejected_by_negative_entries.items())
        ),
        "transfer_target_signatures": {
            ",".join(map(str, signature)): count
            for signature, count in sorted(transfer_signatures.items())
        },
    }


def fixed_pair_residual_census(
    rows: tuple[int, ...],
    gram: list[list[int]],
) -> dict[str, int | bool]:
    pair_sets = tuple(allowed_pairs(round_number) for round_number in WITHIN_ROUNDS)
    if sorted(FROZEN_PAIR_01) != list(range(60)):
        raise AssertionError("frozen pair data are not a permutation")

    concurrence = [[0] * FIBRE_SIZE for _ in range(FIBRE_SIZE)]
    for pair0_index, pair1_index in enumerate(FROZEN_PAIR_01):
        for point0 in pair_sets[0][pair0_index]:
            for point1 in pair_sets[1][pair1_index]:
                concurrence[point0][point1] += 1
    required = [
        row[FIBRE_SIZE : 2 * FIBRE_SIZE]
        for row in gram[:FIBRE_SIZE]
    ]

    raw = old = new = 0
    for pair0_index, pair1_index in enumerate(FROZEN_PAIR_01):
        pair0 = pair_sets[0][pair0_index]
        pair1 = pair_sets[1][pair1_index]
        for pair2 in pair_sets[2]:
            raw += 1
            old_cut, new_cut, _, _ = block_statistics(
                rows,
                selection_mask((pair0, pair1, pair2)),
            )
            old += int(old_cut)
            new += int(new_cut)
    return {
        "pair_certificate_realizes_forced_X0_X1_gram": concurrence == required,
        "raw_choices": raw,
        "old_cut_choices": old,
        "mixed_cut_choices": new,
    }


def integer_partitions(
    total: int,
    minimum: int,
    *,
    floor: int | None = None,
) -> tuple[tuple[int, ...], ...]:
    lower = minimum if floor is None else floor
    partitions: list[tuple[int, ...]] = []
    for first in range(lower, total + 1, 2):
        remainder = total - first
        if remainder == 0:
            partitions.append((first,))
        elif remainder >= first:
            for tail in integer_partitions(remainder, minimum, floor=first):
                partitions.append((first,) + tail)
    return tuple(partitions)


def component_patterns(m: int) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        triple
        for triple in product(range(3), repeat=3)
        if sum(triple) == m // 2
    )


def per_fibre_value_counts(m: int) -> tuple[int, int, int]:
    """Solve counts n_0,n_1,n_2 from 60, first moment, second moment."""

    count2 = (m * m - 2 * m) // 2
    count1 = 10 * m - 2 * count2
    count0 = Y_SIZE - count1 - count2
    if (
        count1 + 2 * count2 != 10 * m
        or count1 + 4 * count2 != m * m + 8 * m
    ):
        raise AssertionError(m)
    return count0, count1, count2


def component_pattern_audit() -> dict[str, object]:
    shapes: dict[str, object] = {}
    for m in (4, 6, 8, 12):
        patterns = component_patterns(m)
        orbit_counts = Counter(tuple(sorted(pattern)) for pattern in patterns)
        shapes[str(m)] = {
            "possible_oriented_patterns": [list(pattern) for pattern in patterns],
            "shape_orientation_counts": {
                ",".join(map(str, shape)): count
                for shape, count in sorted(orbit_counts.items())
            },
            "per_fibre_counts_z0_z1_z2": list(per_fibre_value_counts(m)),
        }

    coupling: dict[str, object] = {}
    for partition in ((4, 8), (6, 6), (4, 4, 4)):
        compatible = [
            choice
            for choice in product(*(component_patterns(m) for m in partition))
            if all(sum(pattern[i] for pattern in choice) == 2 for i in range(3))
        ]
        key = "+".join(map(str, partition))
        coupling[key] = {
            "compatible_oriented_tuples": len(compatible),
            "all_are_coordinatewise_complements": (
                all(
                    all(left[i] + right[i] == 2 for i in range(3))
                    for left, right in compatible
                )
                if len(partition) == 2
                else None
            ),
        }
        if partition == (4, 4, 4):
            kinds: Counter[str] = Counter()
            for choice in compatible:
                a_count = sum(sorted(pattern) == [0, 0, 2] for pattern in choice)
                if a_count == 3:
                    kinds["balanced_AAA"] += 1
                elif a_count == 1:
                    kinds["aligned_ABB"] += 1
                elif a_count == 0:
                    kinds["balanced_BBB"] += 1
                else:
                    kinds["unexpected"] += 1
            coupling[key]["kind_counts"] = dict(sorted(kinds.items()))

    return {
        "surviving_partitions": [
            list(partition) for partition in integer_partitions(12, 4)
        ],
        "single_component_patterns": shapes,
        "partition_coupling": coupling,
    }


def six_vertex_control() -> dict[str, int]:
    """Exhaust all labelled cubic triangle-free graphs on six vertices."""

    all_edges = tuple(combinations(range(6), 2))
    survivors = 0
    minimum_max_common_for_a_nonedge = 6
    for chosen in combinations(all_edges, 9):
        rows = [0] * 6
        for left, right in chosen:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
        if set(row.bit_count() for row in rows) != {3}:
            continue
        if triangle_count(tuple(rows)):
            continue
        survivors += 1
        maximum_common = max(
            (rows[left] & rows[right]).bit_count()
            for left, right in all_edges
            if not rows[left] & (1 << right)
        )
        minimum_max_common_for_a_nonedge = min(
            minimum_max_common_for_a_nonedge, maximum_common
        )
    return {
        "labelled_cubic_triangle_free_graphs": survivors,
        "minimum_over_graphs_of_max_common_neighbors_for_a_nonedge": (
            minimum_max_common_for_a_nonedge
        ),
    }


def spectral_arithmetic(component_number: int, x_four_cycles: int) -> dict[str, object]:
    """Check the trace arithmetic implied by the spectral transfer."""

    c = component_number
    q = x_four_cycles
    f_dimension = 34 - c
    f_power_sums = {
        0: f_dimension,
        1: -3 * c,
        2: 108 - 9 * c,
        3: -27 * c,
        4: 540 + 8 * q - 81 * c,
    }

    def transferred_power(exponent: int) -> int:
        # 8^p plus sum_lambda (-1-lambda)^p, expanded binomially.
        total = 8**exponent
        for power in range(exponent + 1):
            total += (
                (-1) ** exponent
                * _binomial(exponent, power)
                * f_power_sums[power]
            )
        return total

    kernel_mult_3 = 18
    kernel_mult_minus_4 = 7 + c
    transferred = {
        exponent: transferred_power(exponent) for exponent in range(1, 5)
    }
    kernel = {
        exponent: (
            kernel_mult_3 * 3**exponent
            + kernel_mult_minus_4 * (-4) ** exponent
        )
        for exponent in range(1, 5)
    }
    total = {
        exponent: transferred[exponent] + kernel[exponent]
        for exponent in range(1, 5)
    }
    return {
        "component_count": c,
        "f_degree": f_dimension,
        "gram_rank": 35 - c,
        "kernel_dimension": 25 + c,
        "kernel_multiplicities": {"3": kernel_mult_3, "-4": kernel_mult_minus_4},
        "transferred_traces_1_to_4": transferred,
        "kernel_traces_1_to_4": kernel,
        "H_traces_1_to_4": total,
        "H_triangles": total[3] // 6,
        "H_four_cycles": (total[4] - Y_SIZE * 8 * 15) // 8,
        "characteristic_polynomial_degree": (
            1 + kernel_mult_3 + kernel_mult_minus_4 + f_dimension
        ),
        "transformed_factor_sign_exponent": f_dimension,
    }


def _binomial(n: int, k: int) -> int:
    numerator = denominator = 1
    for value in range(1, k + 1):
        numerator *= n - value + 1
        denominator *= value
    return numerator // denominator


def upper_triangle_hash(rows: tuple[int, ...]) -> str:
    payload = "".join(
        str((rows[left] >> right) & 1)
        for left in range(len(rows))
        for right in range(left + 1, len(rows))
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def build_results() -> dict[str, object]:
    factor_edges = [edge for factor in FACTORS for edge in factor]
    if len(factor_edges) != 66 or len(set(factor_edges)) != 66:
        raise AssertionError("circle construction did not partition K_12")

    rows = restricted_core()
    matrix = adjacency_matrix(rows)
    gram = forced_gram(rows)
    census = exhaustive_column_census(rows)
    residual = fixed_pair_residual_census(rows, gram)
    components = component_count(rows)
    x_four_cycles = four_cycle_count(rows)

    if set(row.bit_count() for row in rows) != {3}:
        raise AssertionError("restricted core is not cubic")
    if triangle_count(rows):
        raise AssertionError("restricted core has a triangle")
    if census["old_count"] != 183980 or census["new_count"] != 151712:
        raise AssertionError(census)
    if residual != {
        "pair_certificate_realizes_forced_X0_X1_gram": True,
        "raw_choices": 3600,
        "old_cut_choices": 3266,
        "mixed_cut_choices": 2939,
    }:
        raise AssertionError(residual)

    spectral_samples = {
        str(c): spectral_arithmetic(c, x_four_cycles)
        for c in (1, 2, 3)
    }
    for sample in spectral_samples.values():
        if sample["H_traces_1_to_4"] != {
            1: 0,
            2: 480,
            3: 192,
            4: 8568 + 8 * x_four_cycles,
        }:
            raise AssertionError(sample)
        if sample["characteristic_polynomial_degree"] != 60:
            raise AssertionError(sample)

    return {
        "claim_label": "VERIFIED",
        "format": "wave36-block-compatibility-independent-v1",
        "scope": (
            "Conditional endpoint one-triangle consequences and one frozen "
            "restricted-core census; no simultaneous 60-column object"
        ),
        "general_checks": {
            "block_equations": {
                "xx": "BB^T=12I-A_X+2J-RR^T-A_X^2",
                "xy": "BH=2J-(I+A_X)B=(J/3-I-A_X)B",
                "yy": "B^TB+H^2=12I-H+2J",
                "column_transfer": "d(b)=2*1-(I+A_X)b=Bh_y>=0",
                "column_transfer_sum": 48,
            },
            "component_moments": {
                "component_total": "sum_y z_y=30m",
                "component_second": "sum_y z_y^2=15m^2",
                "equality": "z_y=m/2 for all 60 y",
                "per_fibre_total": "sum_y z_iy=10m",
                "per_fibre_second": "sum_y z_iy^2=m^2+8m",
                "cross_fibre": "sum_y z_iy*z_jy=2m(m-2)",
            },
            "component_patterns": component_pattern_audit(),
            "m_equals_2_exhaustive_control": six_vertex_control(),
            "spectral_transfer_samples": spectral_samples,
            "spectral_general_form": {
                "charpoly": (
                    "chi_H(t)=(-1)^(34-c)(t-8)(t-3)^18"
                    "(t+4)^(7+c)f(-1-t)"
                ),
                "H_connected": True,
                "H_triangles": 32,
                "H_four_cycles": "171+C4(A_X)",
            },
        },
        "restricted_core": {
            "upper_triangle_sha256": upper_triangle_hash(rows),
            "vertices": X_SIZE,
            "edges": sum(row.bit_count() for row in rows) // 2,
            "degree_set": sorted(set(row.bit_count() for row in rows)),
            "components": components,
            "triangles": triangle_count(rows),
            "four_cycles": x_four_cycles,
            "adjacency_traces_1_to_4": {
                exponent: trace_power(matrix, exponent)
                for exponent in range(1, 5)
            },
            "forced_gram_rank_over_Q": rational_rank(gram),
            "column_census": census,
            "fixed_pair_residual_census": residual,
        },
        "solver_scope_audit": {
            "status": "UNKNOWN",
            "verified_scope": (
                "The fixed-pair search concerns one frozen X0-X1 certificate "
                "and at most the 2939 independently reproduced mixed-cut choices."
            ),
            "execution_reproducibility": (
                "Not independently verified: the target directory retains no "
                "solver program, CNF/MPS instance, raw log, or solver certificate."
            ),
            "logical_effect": (
                "A timeout or budget exhaustion proves neither feasibility nor "
                "infeasibility, even within the restricted fixed-pair scope."
            ),
        },
        "limitations": [
            "All general conclusions are conditional on the frozen endpoint premises.",
            "The 151712 count is an individual-column census for one normalized core.",
            "The 2939 count is a residual census for one fixed X0-X1 certificate.",
            "No simultaneous B, compatible H, endpoint exclusion, or improved n3 bound is proved.",
            "The historical solver execution metadata cannot be reproduced from retained files.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = canonical_bytes(build_results())
    if arguments.output is not None:
        arguments.output.write_bytes(payload)
        print(arguments.output)
        return 0
    if arguments.verify is not None:
        if arguments.verify.read_bytes() != payload:
            print(f"FAIL: {arguments.verify} differs", file=sys.stderr)
            return 1
        print(f"PASS: {arguments.verify} matches independent regeneration")
        return 0
    sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
