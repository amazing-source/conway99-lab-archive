#!/usr/bin/env python3
"""Exact labelled-incidence checks for the Wave 81 norm-16 branch.

This module uses only the Python standard library.  It enumerates support
matrices up to independent relabelling of their two eight-point sides; this
is a quotient by coordinate names, not an automorphism assumption.
"""

from __future__ import annotations

import argparse
import functools
import itertools
import json
import os
from collections import Counter
from math import comb
from pathlib import Path


SIDE = 8
ROW_WEIGHT = 4
ANCHOR_ROW = (1 << ROW_WEIGHT) - 1
ALL_ROWS = tuple(mask for mask in range(1 << SIDE) if mask.bit_count() == ROW_WEIGHT)
PERMUTATIONS_4 = tuple(itertools.permutations(range(4)))
ANCHOR_STABILIZER_MAPS = tuple(
    left + tuple(4 + i for i in right)
    for left in PERMUTATIONS_4
    for right in PERMUTATIONS_4
)


def relabel_mask(mask: int, old_at_new: tuple[int, ...]) -> int:
    """Relabel one eight-bit mask."""

    return sum(
        1 << new_column
        for new_column, old_column in enumerate(old_at_new)
        if mask >> old_column & 1
    )


ANCHOR_STABILIZER_TABLES = tuple(
    tuple(relabel_mask(mask, mapping) for mask in range(1 << SIDE))
    for mapping in ANCHOR_STABILIZER_MAPS
)


def free_memory_percent() -> float:
    """Return available physical memory as a percentage on Windows."""

    if os.name != "nt":
        return 100.0
    import ctypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.ullAvailPhys / status.ullTotalPhys


def transform_rows(rows: tuple[int, ...], old_at_new: tuple[int, ...]) -> tuple[int, ...]:
    """Relabel columns, then forget row names by sorting the row masks."""

    return tuple(sorted(relabel_mask(row, old_at_new) for row in rows))


def anchor_stabilizer_key(rows: tuple[int, ...]) -> tuple[int, ...]:
    """Canonicalize an anchored matrix under S_4 wr S_2 column names."""

    return min(
        tuple(sorted(table[row] for row in rows))
        for table in ANCHOR_STABILIZER_TABLES
    )


@functools.lru_cache(maxsize=None)
def canonical_support(rows: tuple[int, ...]) -> tuple[int, ...]:
    """Canonical key under all S_8 x S_8 side relabellings.

    Row relabellings are removed by sorting.  For the columns, every
    permutation is represented exactly once after choosing which row is sent
    to 00001111, permuting its four columns into positions 0..3, and
    permuting the complementary four columns into positions 4..7.
    """

    best: tuple[int, ...] | None = None
    for anchor in rows:
        ones = tuple(i for i in range(SIDE) if anchor >> i & 1)
        zeros = tuple(i for i in range(SIDE) if not (anchor >> i & 1))
        for left_order in PERMUTATIONS_4:
            left = tuple(ones[i] for i in left_order)
            for right_order in PERMUTATIONS_4:
                old_at_new = left + tuple(zeros[i] for i in right_order)
                candidate = transform_rows(rows, old_at_new)
                if best is None or candidate < best:
                    best = candidate
    assert best is not None and best[0] == ANCHOR_ROW
    return best


def normalized_supports() -> tuple[list[tuple[int, ...]], int]:
    """Enumerate every support orbit and return (canonical reps, anchored count).

    Coverage proof: take any 8x8 support matrix and relabel columns so one
    chosen row becomes 00001111; then sort its rows.  The DFS enumerates that
    anchored matrix.  `canonical_support` subsequently quotients all choices
    of anchor and all column/row relabellings.
    """

    candidates = tuple(
        row
        for row in ALL_ROWS
        if row > ANCHOR_ROW and (row & ANCHOR_ROW).bit_count() <= 2
    )
    representatives: set[tuple[int, ...]] = set()
    anchored_count = 0

    def visit(
        chosen: tuple[int, ...],
        start: int,
        column_counts: tuple[int, ...],
    ) -> None:
        nonlocal anchored_count
        remaining = SIDE - len(chosen)
        if any(count > ROW_WEIGHT or count + remaining < ROW_WEIGHT for count in column_counts):
            return
        if not remaining:
            if column_counts != (ROW_WEIGHT,) * SIDE:
                return
            columns = columns_of(chosen)
            if any(
                (columns[i] & columns[j]).bit_count() > 2
                for i, j in itertools.combinations(range(SIDE), 2)
            ):
                return
            anchored_count += 1
            if anchor_stabilizer_key(chosen) != chosen:
                return
            representatives.add(canonical_support(chosen))
            return

        for position in range(start, len(candidates)):
            row = candidates[position]
            if any((row & old).bit_count() > 2 for old in chosen):
                continue
            updated = tuple(
                count + ((row >> column) & 1)
                for column, count in enumerate(column_counts)
            )
            if any(count > ROW_WEIGHT for count in updated):
                continue
            visit(chosen + (row,), position + 1, updated)

    visit((ANCHOR_ROW,), 0, (1, 1, 1, 1, 0, 0, 0, 0))
    return sorted(representatives), anchored_count


def columns_of(rows: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        sum(((rows[i] >> j) & 1) << i for i in range(SIDE))
        for j in range(SIDE)
    )


def deficiency_pairs(blocks: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    """Expand pair {i,j} with multiplicity 2-codegree(i,j)."""

    pairs: list[tuple[int, int]] = []
    for i, j in itertools.combinations(range(SIDE), 2):
        codegree = (blocks[i] & blocks[j]).bit_count()
        if codegree > 2:
            raise ValueError("pair codegree exceeds two")
        pairs.extend([(i, j)] * (2 - codegree))
    if len(pairs) != 8:
        raise AssertionError(f"expected eight pair deficiencies, got {len(pairs)}")
    degrees = Counter(vertex for pair in pairs for vertex in pair)
    if degrees != Counter({vertex: 2 for vertex in range(SIDE)}):
        raise AssertionError(f"deficiency multigraph is not 2-regular: {degrees}")
    return tuple(sorted(pairs))


def rectangle_is_locally_admissible(
    rows: tuple[int, ...],
    p_pair: tuple[int, int],
    n_pair: tuple[int, int],
) -> bool:
    """Check the edge-lambda rule inside one degree-two outside rectangle."""

    a, b = p_pair
    c, d = n_pair
    return (
        ((rows[a] >> c) & 1) + ((rows[a] >> d) & 1) <= 1
        and ((rows[b] >> c) & 1) + ((rows[b] >> d) & 1) <= 1
        and ((rows[a] >> c) & 1) + ((rows[b] >> c) & 1) <= 1
        and ((rows[a] >> d) & 1) + ((rows[b] >> d) & 1) <= 1
    )


def contingency_feasible(
    capacities: list[list[int]],
    row_demands: list[int],
    column_demands: list[int],
) -> bool:
    """Integral max-flow test for a bounded 8x8 contingency table."""

    if sum(row_demands) != sum(column_demands):
        return False
    source = 0
    row_offset = 1
    column_offset = row_offset + SIDE
    sink = column_offset + SIDE
    order = sink + 1
    residual = [[0] * order for _ in range(order)]

    def add_edge(left: int, right: int, capacity: int) -> None:
        residual[left][right] += capacity

    for i, demand in enumerate(row_demands):
        add_edge(source, row_offset + i, demand)
    for i in range(SIDE):
        for j in range(SIDE):
            add_edge(row_offset + i, column_offset + j, capacities[i][j])
    for j, demand in enumerate(column_demands):
        add_edge(column_offset + j, sink, demand)

    flow = 0
    while True:
        parent = [-1] * order
        parent[source] = source
        queue = [source]
        for vertex in queue:
            for neighbor, capacity in enumerate(residual[vertex]):
                if capacity and parent[neighbor] < 0:
                    parent[neighbor] = vertex
                    queue.append(neighbor)
                    if neighbor == sink:
                        break
            if parent[sink] >= 0:
                break
        if parent[sink] < 0:
            break
        increment = 10**9
        vertex = sink
        while vertex != source:
            increment = min(increment, residual[parent[vertex]][vertex])
            vertex = parent[vertex]
        vertex = sink
        while vertex != source:
            previous = parent[vertex]
            residual[previous][vertex] -= increment
            residual[vertex][previous] += increment
            vertex = previous
        flow += increment
    return flow == sum(row_demands)


def d2_local_common_neighbor_feasible(
    rows: tuple[int, ...],
    coupling: list[tuple[tuple[int, int], tuple[int, int]]],
    singleton_counts: list[list[int]],
) -> bool:
    """Test the support-vs-X2 common-neighbor equations with X2 independent.

    Taking no X2-X2 edges is always allowed by type counts.  Then each X2
    vertex needs six X1 neighbors.  Their singleton cells must realize exact
    row and column marginals; a singleton lying inside the X2 rectangle is
    forbidden because the two outside vertices already share two support
    neighbors.
    """

    for p_pair, n_pair in coupling:
        p_set = set(p_pair)
        n_set = set(n_pair)
        row_demands = [
            (1 if i in p_set else 2)
            - sum((rows[i] >> j) & 1 for j in n_pair)
            for i in range(SIDE)
        ]
        column_demands = [
            (1 if j in n_set else 2)
            - sum((rows[i] >> j) & 1 for i in p_pair)
            for j in range(SIDE)
        ]
        if min(row_demands + column_demands) < 0:
            return False
        if sum(row_demands) != 6 or sum(column_demands) != 6:
            raise AssertionError("unexpected X2-to-X1 marginal sum")
        capacities = [
            [
                0 if i in p_set and j in n_set else singleton_counts[i][j]
                for j in range(SIDE)
            ]
            for i in range(SIDE)
        ]
        if not contingency_feasible(capacities, row_demands, column_demands):
            return False
    return True


def coupling_census(rows: tuple[int, ...]) -> dict[str, object]:
    """Enumerate all exact pair-deficiency couplings for one support matrix.

    Equal pair occurrences are indistinguishable.  Consequently the output
    counts coupling multisets, not permutations of the eight outside labels.
    """

    p_pairs = deficiency_pairs(rows)
    n_pairs = deficiency_pairs(columns_of(rows))
    n_types = tuple(sorted(Counter(n_pairs)))
    remaining = [Counter(n_pairs)[pair] for pair in n_types]
    rectangle_counts = [[0] * SIDE for _ in range(SIDE)]
    chosen: list[tuple[tuple[int, int], tuple[int, int]]] = []
    count = 0
    locally_closed_count = 0
    d2_eligible_edge_histogram: Counter[int] = Counter()
    d1_cell_multiplicity_histogram: Counter[tuple[int, ...]] = Counter()
    first_example: list[list[list[int]]] | None = None

    def visit(index: int, previous_n_type: int) -> None:
        nonlocal count, locally_closed_count, first_example
        if index == len(p_pairs):
            count += 1
            eligible_d2_edges = 0
            for left, right in itertools.combinations(chosen, 2):
                support_overlap = len(set(left[0]) & set(right[0])) + len(
                    set(left[1]) & set(right[1])
                )
                if support_overlap <= 1:
                    eligible_d2_edges += 1
            d2_eligible_edge_histogram[eligible_d2_edges] += 1

            multiplicities = []
            singleton_counts = [[0] * SIDE for _ in range(SIDE)]
            for i in range(SIDE):
                for j in range(SIDE):
                    target = 2 - ((rows[i] >> j) & 1)
                    residual = target - rectangle_counts[i][j]
                    if residual < 0:
                        raise AssertionError("negative singleton residual")
                    singleton_counts[i][j] = residual
                    multiplicities.append(residual)
            d1_cell_multiplicity_histogram[tuple(sorted(Counter(multiplicities).items()))] += 1
            locally_closed = d2_local_common_neighbor_feasible(
                rows, chosen, singleton_counts
            )
            if locally_closed:
                locally_closed_count += 1
            if locally_closed and first_example is None:
                first_example = [
                    [list(p_pair), list(n_pair)] for p_pair, n_pair in chosen
                ]
            return

        p_pair = p_pairs[index]
        if index and p_pair == p_pairs[index - 1]:
            start = previous_n_type
        else:
            start = 0

        for n_index in range(start, len(n_types)):
            if not remaining[n_index]:
                continue
            n_pair = n_types[n_index]
            if not rectangle_is_locally_admissible(rows, p_pair, n_pair):
                continue
            if any(
                len(set(p_pair) & set(old_p)) + len(set(n_pair) & set(old_n)) > 2
                for old_p, old_n in chosen
            ):
                continue

            cells = tuple((i, j) for i in p_pair for j in n_pair)
            if any(
                rectangle_counts[i][j] + 1 > 2 - ((rows[i] >> j) & 1)
                for i, j in cells
            ):
                continue

            remaining[n_index] -= 1
            for i, j in cells:
                rectangle_counts[i][j] += 1
            chosen.append((p_pair, n_pair))
            visit(index + 1, n_index)
            chosen.pop()
            for i, j in cells:
                rectangle_counts[i][j] -= 1
            remaining[n_index] += 1

    visit(0, 0)
    return {
        "coupling_multiset_count": count,
        "has_coupling": bool(count),
        "locally_closed_coupling_count": locally_closed_count,
        "has_locally_closed_coupling": bool(locally_closed_count),
        "d2_eligible_edge_count_histogram": {
            str(key): value for key, value in sorted(d2_eligible_edge_histogram.items())
        },
        "d1_cell_multiplicity_profile_histogram": {
            json.dumps(list(profile), separators=(",", ":")): value
            for profile, value in sorted(d1_cell_multiplicity_histogram.items())
        },
        "first_coupling": first_example,
    }


def support_record(rows: tuple[int, ...]) -> dict[str, object]:
    coupling = coupling_census(rows)
    p_pairs = deficiency_pairs(rows)
    n_pairs = deficiency_pairs(columns_of(rows))
    return {
        "rows_hex": [f"{row:02x}" for row in rows],
        "p_deficiency_pairs": [list(pair) for pair in p_pairs],
        "n_deficiency_pairs": [list(pair) for pair in n_pairs],
        "outside_spectrum": outside_spectral_record(rows),
        **coupling,
    }


def matrix_multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    size = len(left)
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(size))
            for j in range(size)
        ]
        for i in range(size)
    ]


def trace(matrix: list[list[int]]) -> int:
    return sum(matrix[i][i] for i in range(len(matrix)))


def trace_powers(matrix: list[list[int]], maximum: int) -> list[int]:
    size = len(matrix)
    power = [[int(i == j) for j in range(size)] for i in range(size)]
    answers = [size]
    for _ in range(maximum):
        power = matrix_multiply(power, matrix)
        answers.append(trace(power))
    return answers


def characteristic_coefficients(matrix: list[list[int]]) -> list[int]:
    """Return det(xI-M), descending, via exact Newton identities."""

    size = len(matrix)
    power_traces = trace_powers(matrix, size)
    coefficients = [1]
    for k in range(1, size + 1):
        numerator = -sum(
            coefficients[k - i] * power_traces[i]
            for i in range(1, k + 1)
        )
        if numerator % k:
            raise AssertionError("Newton division was not exact")
        coefficients.append(numerator // k)
    return coefficients


def shift_polynomial(coefficients: list[int], shift: int) -> list[int]:
    """Return descending coefficients of p(x+shift)."""

    degree = len(coefficients) - 1
    ascending = [0] * (degree + 1)
    for index, coefficient in enumerate(coefficients):
        power = degree - index
        for new_power in range(power + 1):
            ascending[new_power] += (
                coefficient
                * comb(power, new_power)
                * shift ** (power - new_power)
            )
    return list(reversed(ascending))


def divide_by_x_plus(coefficients: list[int], constant: int) -> list[int]:
    """Exactly divide a descending monic polynomial by x+constant."""

    quotient = [coefficients[0]]
    for coefficient in coefficients[1:-1]:
        quotient.append(coefficient - constant * quotient[-1])
    remainder = coefficients[-1] - constant * quotient[-1]
    if remainder:
        raise AssertionError(f"nonzero polynomial remainder {remainder}")
    return quotient


def support_adjacency(rows: tuple[int, ...]) -> list[list[int]]:
    matrix = [[0] * (2 * SIDE) for _ in range(2 * SIDE)]
    for i in range(SIDE):
        for j in range(SIDE):
            value = (rows[i] >> j) & 1
            matrix[i][SIDE + j] = value
            matrix[SIDE + j][i] = value
    return matrix


def quadratic_root_power_sum(power: int) -> int:
    """Power sum for the roots of x^2-9x-38."""

    if power == 0:
        return 2
    if power == 1:
        return 9
    previous_previous, previous = 2, 9
    for _ in range(2, power + 1):
        previous_previous, previous = previous, 9 * previous + 38 * previous_previous
    return previous


def outside_spectral_record(rows: tuple[int, ...]) -> dict[str, object]:
    """Jacobi principal-minor characteristic factor and exact moments."""

    support = support_adjacency(rows)
    negative_support = [[-entry for entry in row] for row in support]
    shifted = shift_polynomial(characteristic_coefficients(negative_support), 1)
    residual_factor = divide_by_x_plus(shifted, 5)

    negative_identity_minus_support = [
        [-(int(i == j) + support[i][j]) for j in range(2 * SIDE)]
        for i in range(2 * SIDE)
    ]
    residual_power_sums = trace_powers(negative_identity_minus_support, 4)
    outside_traces = {}
    for power in range(1, 5):
        outside_traces[str(power)] = (
            38 * 3**power
            + 28 * (-4) ** power
            + quadratic_root_power_sum(power)
            + residual_power_sums[power]
            - (-5) ** power
        )
    if outside_traces["1"] != 0 or outside_traces["2"] != 1002:
        raise AssertionError(f"invalid outside low moments: {outside_traces}")
    if outside_traces["3"] != 906:
        raise AssertionError(f"outside triangle trace mismatch: {outside_traces}")
    four_cycles_numerator = outside_traces["4"] - 23342
    if four_cycles_numerator < 0 or four_cycles_numerator % 8:
        raise AssertionError("outside four-cycle count is not nonnegative integral")

    # For an 83x83 matrix, det(D) is minus the constant coefficient of
    # det(xI-D).  Evaluating the displayed factorization at x=0 gives this.
    determinant = 38 * 3**38 * 4**28 * residual_factor[-1]
    return {
        "characteristic_factorization": (
            "(x-3)^38 (x+4)^28 (x^2-9x-38) q_H(x)"
        ),
        "q_H_definition": "det((x+1)I+H)/(x+5)",
        "q_H_coefficients_descending": residual_factor,
        "trace_powers_1_through_4": [
            outside_traces[str(power)] for power in range(1, 5)
        ],
        "outside_edges": outside_traces["2"] // 2,
        "outside_triangles": outside_traces["3"] // 6,
        "outside_four_cycles": four_cycles_numerator // 8,
        "determinant": determinant,
    }


def histogram_candidates(
    count: int,
    incidence_to_x2: int,
    minimum_a: int,
    maximum_a: int,
    vertex_type: int,
) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Enumerate type-degree histograms and their six pair moments."""

    answers: list[tuple[tuple[int, ...], tuple[int, ...]]] = []

    def visit(
        a: int,
        remaining_count: int,
        remaining_sum: int,
        prefix: tuple[int, ...],
    ) -> None:
        if a == maximum_a:
            number = remaining_count
            if a * number != remaining_sum:
                return
            histogram = prefix + (number,)
            moments = [0] * 6
            for offset, multiplicity in enumerate(histogram):
                value_a = minimum_a + offset
                value_b = 16 - 5 * vertex_type - 2 * value_a
                value_c = value_a + 3 * vertex_type - 2
                terms = (
                    comb(value_c, 2),
                    value_c * value_b,
                    value_c * value_a,
                    comb(value_b, 2),
                    comb(value_a, 2),
                    value_a * value_b,
                )
                for index, term in enumerate(terms):
                    moments[index] += multiplicity * term
            answers.append((tuple(moments), histogram))
            return
        for number in range(remaining_count + 1):
            used = a * number
            if used > remaining_sum:
                break
            visit(
                a + 1,
                remaining_count - number,
                remaining_sum - used,
                prefix + (number,),
            )

    visit(minimum_a, count, incidence_to_x2, ())
    return answers


def is_graphical(degrees: list[int]) -> bool:
    """Havel-Hakimi test for a simple graph degree sequence."""

    work = sorted(degrees, reverse=True)
    while work and work[0]:
        degree = work.pop(0)
        if degree > len(work):
            return False
        for index in range(degree):
            work[index] -= 1
            if work[index] < 0:
                return False
        work.sort(reverse=True)
    return True


def type_degree_closure() -> dict[str, object]:
    """Apply all six aggregate outside pair common-neighbor equations."""

    edge_formulas = {
        "e00": "5+t",
        "e01": "112-4t",
        "e02": "32+2t",
        "e11": "304+4t",
        "e12": "48-4t",
        "e22": "t",
    }
    surviving: dict[str, list[dict[str, list[int]]]] = {}
    counts_by_t: dict[str, int] = {}
    for t in range(13):
        families = (
            histogram_candidates(11, 32 + 2 * t, 2, 8, 0),
            histogram_candidates(64, 48 - 4 * t, 0, 5, 1),
            histogram_candidates(8, 2 * t, 0, 3, 2),
        )
        target = (
            105 - t,
            1296 + 4 * t,
            144 - 2 * t,
            3280 - 4 * t,
            40 - t,
            720 + 4 * t,
        )
        third_by_moment: dict[tuple[int, ...], list[tuple[int, ...]]] = {}
        for moments, histogram in families[2]:
            degrees = [
                degree
                for degree, multiplicity in enumerate(histogram)
                for _ in range(multiplicity)
            ]
            if is_graphical(degrees):
                third_by_moment.setdefault(moments, []).append(histogram)

        rows = []
        for moments0, histogram0 in families[0]:
            for moments1, histogram1 in families[1]:
                needed = tuple(
                    target[index] - moments0[index] - moments1[index]
                    for index in range(6)
                )
                for histogram2 in third_by_moment.get(needed, ()):
                    rows.append(
                        {
                            "X0_a_histogram_for_a_2_through_8": list(histogram0),
                            "X1_a_histogram_for_a_0_through_5": list(histogram1),
                            "X2_a_histogram_for_a_0_through_3": list(histogram2),
                        }
                    )
        counts_by_t[str(t)] = len(rows)
        if rows:
            surviving[str(t)] = rows

    if counts_by_t != {
        "0": 43,
        "1": 7,
        **{str(t): 0 for t in range(2, 13)},
    }:
        raise AssertionError(f"unexpected type-degree closure: {counts_by_t}")
    return {
        "local_equations": {
            "a": "number of X2 neighbors",
            "b": "number of X1 neighbors = 16-5d-2a",
            "c": "number of X0 neighbors = a+3d-2",
            "ranges": {
                "X0": "2<=a<=8",
                "X1": "0<=a<=5",
                "X2": "0<=a<=3",
            },
        },
        "type_edge_formulas": edge_formulas,
        "outside_pair_moment_order": [
            "sum C(c,2) = 105-t",
            "sum c*b = 1296+4t",
            "sum c*a = 144-2t",
            "sum C(b,2) = 3280-4t",
            "sum C(a,2) = 40-t",
            "sum a*b = 720+4t",
        ],
        "histogram_counts_by_t": counts_by_t,
        "surviving_t": [0, 1],
        "surviving_histograms": surviving,
    }


@functools.lru_cache(maxsize=1)
def build_results() -> dict[str, object]:
    supports, anchored_count = normalized_supports()
    records = [support_record(rows) for rows in supports]
    basic_survivors = [record for record in records if record["has_coupling"]]
    survivors = [
        record for record in records if record["has_locally_closed_coupling"]
    ]
    total_couplings = sum(int(record["coupling_multiset_count"]) for record in records)
    total_locally_closed = sum(
        int(record["locally_closed_coupling_count"]) for record in records
    )
    return {
        "format": "wave81-norm16-labeled-design-v1",
        "claim_label": "DERIVED",
        "scope": (
            "conditional on the verified Wave78 norm-16 histogram and its "
            "imported Wave71/Wave74 hypotheses"
        ),
        "support_enumeration": {
            "anchored_row_sorted_matrix_count": anchored_count,
            "isomorphism_orbit_count_under_independent_side_relabelling": len(supports),
            "coverage_uses_target_automorphism": False,
        },
        "deficiency_couplings": {
            "support_orbits_with_at_least_one_coupling": len(basic_survivors),
            "support_orbits_without_a_coupling": len(records) - len(basic_survivors),
            "support_orbits_with_locally_closed_coupling": len(survivors),
            "support_orbits_without_locally_closed_coupling": (
                len(records) - len(survivors)
            ),
            "coupling_multiset_count_across_orbit_representatives": total_couplings,
            "locally_closed_coupling_count_across_orbit_representatives": (
                total_locally_closed
            ),
        },
        "outside_type_degree_closure": type_degree_closure(),
        "support_records": records,
        "endpoint": {
            "norm16_excluded": not survivors,
            "conway_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "The result is conditional on the imported short-vector support branch.",
            "Coupling counts are taken once per support isomorphism representative.",
            "Surviving labelled incidences do not construct the 83-vertex outside graph.",
            "No solver nonhit is interpreted as nonexistence.",
        ],
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run with only {free:.1f}% free physical memory")
    encoded = canonical_bytes(build_results())
    if args.output:
        args.output.write_bytes(encoded)
    elif args.verify:
        if args.verify.read_bytes() != encoded:
            raise SystemExit("verification mismatch")
        print("PASS")
    else:
        print(encoded.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
