#!/usr/bin/env python3
"""Clean-room verification of the Wave 81 norm-16 labelled reduction.

The discovery module is never imported.  This verifier independently
enumerates the finite objects from the frozen mathematical specification.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from math import comb
from pathlib import Path


N = 8
ANCHOR = 0x0F
WEIGHT_FOUR = tuple(x for x in range(256) if x.bit_count() == 4)
EXPECTED_MANIFEST_SHA256 = (
    "6c05ff8ef0f97b1c9af0a1fbe1106ec07f826e819869660262fe92b9478033bd"
)


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0
    import ctypes

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("avail_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("avail_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("avail_virtual", ctypes.c_ulonglong),
            ("avail_extended", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.avail_phys / status.total_phys


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def columns(rows: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        sum(((rows[i] >> j) & 1) << i for i in range(N))
        for j in range(N)
    )


def same_side_codegrees_ok(blocks: tuple[int, ...]) -> bool:
    return all(
        (blocks[i] & blocks[j]).bit_count() <= 2
        for i, j in itertools.combinations(range(N), 2)
    )


def enumerate_anchored_supports() -> list[tuple[int, ...]]:
    """Enumerate row-unlabelled supports after one row is sent to 0x0f."""

    choices = tuple(
        row
        for row in WEIGHT_FOUR
        if row > ANCHOR and (row & ANCHOR).bit_count() <= 2
    )
    answers: list[tuple[int, ...]] = []

    def search(
        selected: tuple[int, ...],
        first_choice: int,
        col_degrees: tuple[int, ...],
    ) -> None:
        rows_left = N - len(selected)
        if any(d > 4 or d + rows_left < 4 for d in col_degrees):
            return
        if rows_left == 0:
            if col_degrees == (4,) * N and same_side_codegrees_ok(columns(selected)):
                answers.append(selected)
            return

        for index in range(first_choice, len(choices)):
            candidate = choices[index]
            if any((candidate & old).bit_count() > 2 for old in selected):
                continue
            degrees = tuple(
                col_degrees[j] + ((candidate >> j) & 1) for j in range(N)
            )
            search(selected + (candidate,), index + 1, degrees)

    search((ANCHOR,), 0, (1, 1, 1, 1, 0, 0, 0, 0))
    return answers


def permute_mask(mask: int, old_at_new: tuple[int, ...]) -> int:
    out = 0
    for new, old in enumerate(old_at_new):
        out |= ((mask >> old) & 1) << new
    return out


def support_orbit(rows: tuple[int, ...]) -> set[tuple[int, ...]]:
    """Generate the complete S8 column orbit; sorting removes row labels."""

    return {
        tuple(sorted(permute_mask(row, permutation) for row in rows))
        for permutation in itertools.permutations(range(N))
    }


def support_census() -> tuple[list[tuple[int, ...]], int]:
    anchored = enumerate_anchored_supports()
    covered: set[tuple[int, ...]] = set()
    representatives: list[tuple[int, ...]] = []
    for rows in anchored:
        if rows in covered:
            continue
        orbit = support_orbit(rows)
        representatives.append(min(orbit))
        covered.update(orbit)
    return sorted(representatives), len(anchored)


def deficiencies(blocks: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    result: list[tuple[int, int]] = []
    for i, j in itertools.combinations(range(N), 2):
        multiplicity = 2 - (blocks[i] & blocks[j]).bit_count()
        if multiplicity < 0:
            raise AssertionError("same-side codegree exceeds two")
        result.extend([(i, j)] * multiplicity)
    degrees = Counter(v for pair in result for v in pair)
    if len(result) != 8 or degrees != Counter({i: 2 for i in range(N)}):
        raise AssertionError("deficiency multigraph is not 2-regular of size eight")
    return tuple(sorted(result))


def derive_wave78_histogram(
    representatives: list[tuple[int, ...]],
) -> dict[str, int]:
    """Recover (n0,n1,n2) from support degrees and pair deficiencies."""

    deficiency_counts = {
        len(deficiencies(rows)) for rows in representatives
    } | {
        len(deficiencies(columns(rows))) for rows in representatives
    }
    if deficiency_counts != {8}:
        raise AssertionError("support representatives disagree on n2")
    n2 = deficiency_counts.pop()
    # Sixteen support vertices have 14-4=10 outside neighbors.  An X_d
    # vertex contributes 2d support incidences.
    n1 = (16 * 10) // 2 - 2 * n2
    n0 = 83 - n1 - n2
    if (n0, n1, n2) != (11, 64, 8):
        raise AssertionError("Wave78 histogram reconstruction failed")
    return {"X0": n0, "X1": n1, "X2": n2}


def rectangle_matching(
    rows: tuple[int, ...],
    p_pair: tuple[int, int],
    n_pair: tuple[int, int],
) -> bool:
    for p in p_pair:
        if sum((rows[p] >> n) & 1 for n in n_pair) > 1:
            return False
    for n in n_pair:
        if sum((rows[p] >> n) & 1 for p in p_pair) > 1:
            return False
    return True


def bounded_table_exists(
    capacities: tuple[tuple[int, ...], ...],
    row_sums: tuple[int, ...],
    col_sums: tuple[int, ...],
) -> bool:
    """Exact DP for a bounded nonnegative integral contingency table."""

    if min(row_sums + col_sums) < 0 or sum(row_sums) != sum(col_sums):
        return False

    @functools.lru_cache(maxsize=None)
    def fill(row: int, remaining_cols: tuple[int, ...]) -> bool:
        if row == N:
            return not any(remaining_cols)
        demand = row_sums[row]
        allocation = [0] * N

        def allocate(col: int, left: int) -> bool:
            if col == N:
                if left:
                    return False
                next_cols = tuple(
                    remaining_cols[j] - allocation[j] for j in range(N)
                )
                return fill(row + 1, next_cols)
            upper = min(capacities[row][col], remaining_cols[col], left)
            for value in range(upper + 1):
                allocation[col] = value
                if allocate(col + 1, left - value):
                    return True
            allocation[col] = 0
            return False

        return allocate(0, demand)

    return fill(0, col_sums)


def local_x2_flow(
    rows: tuple[int, ...],
    coupling: tuple[tuple[tuple[int, int], tuple[int, int]], ...],
    rectangle_use: tuple[tuple[int, ...], ...],
) -> tuple[bool, dict[str, object] | None]:
    singleton = tuple(
        tuple(2 - ((rows[i] >> j) & 1) - rectangle_use[i][j] for j in range(N))
        for i in range(N)
    )
    if min(value for row in singleton for value in row) < 0:
        raise AssertionError("negative singleton capacity")

    first_instance: dict[str, object] | None = None
    for p_pair, n_pair in coupling:
        p_set, n_set = set(p_pair), set(n_pair)
        row_sums = tuple(
            (1 if i in p_set else 2)
            - sum((rows[i] >> j) & 1 for j in n_pair)
            for i in range(N)
        )
        col_sums = tuple(
            (1 if j in n_set else 2)
            - sum((rows[i] >> j) & 1 for i in p_pair)
            for j in range(N)
        )
        capacities = tuple(
            tuple(
                0 if i in p_set and j in n_set else singleton[i][j]
                for j in range(N)
            )
            for i in range(N)
        )
        if sum(row_sums) != 6 or sum(col_sums) != 6:
            raise AssertionError("X2 marginal totals are not six")
        if not bounded_table_exists(capacities, row_sums, col_sums):
            return False, None
        if first_instance is None:
            first_instance = {
                "capacities": [list(row) for row in capacities],
                "row_sums": list(row_sums),
                "col_sums": list(col_sums),
            }
    return True, first_instance


def coupling_count(rows: tuple[int, ...]) -> dict[str, object]:
    p_occurrences = deficiencies(rows)
    n_counter = Counter(deficiencies(columns(rows)))
    n_types = tuple(sorted(n_counter))
    remaining = [n_counter[pair] for pair in n_types]
    rectangle_use = [[0] * N for _ in range(N)]
    selected: list[tuple[tuple[int, int], tuple[int, int]]] = []
    count = 0
    flow_count = 0
    first_flow: dict[str, object] | None = None

    def backtrack(position: int, lower_n_type: int) -> None:
        nonlocal count, flow_count, first_flow
        if position == len(p_occurrences):
            count += 1
            frozen_use = tuple(tuple(row) for row in rectangle_use)
            feasible, flow_instance = local_x2_flow(
                rows, tuple(selected), frozen_use
            )
            if feasible:
                flow_count += 1
                if first_flow is None:
                    first_flow = flow_instance
            return

        p_pair = p_occurrences[position]
        start = (
            lower_n_type
            if position and p_pair == p_occurrences[position - 1]
            else 0
        )
        for n_index in range(start, len(n_types)):
            if remaining[n_index] == 0:
                continue
            n_pair = n_types[n_index]
            if not rectangle_matching(rows, p_pair, n_pair):
                continue
            if any(
                len(set(p_pair).intersection(old_p))
                + len(set(n_pair).intersection(old_n))
                > 2
                for old_p, old_n in selected
            ):
                continue
            cells = tuple(itertools.product(p_pair, n_pair))
            if any(
                rectangle_use[i][j] + 1 > 2 - ((rows[i] >> j) & 1)
                for i, j in cells
            ):
                continue
            remaining[n_index] -= 1
            for i, j in cells:
                rectangle_use[i][j] += 1
            selected.append((p_pair, n_pair))
            backtrack(position + 1, n_index)
            selected.pop()
            for i, j in cells:
                rectangle_use[i][j] -= 1
            remaining[n_index] += 1

    backtrack(0, 0)
    return {
        "coupling_count": count,
        "local_flow_count": flow_count,
        "first_flow": first_flow,
    }


def compositions_with_sum(
    count: int, values: tuple[int, ...], weighted_sum: int
) -> list[tuple[int, ...]]:
    answers: list[tuple[int, ...]] = []

    def rec(
        index: int, number_left: int, sum_left: int, prefix: tuple[int, ...]
    ) -> None:
        value = values[index]
        if index == len(values) - 1:
            if number_left * value == sum_left:
                answers.append(prefix + (number_left,))
            return
        for multiplicity in range(number_left + 1):
            used = multiplicity * value
            if used > sum_left:
                break
            rec(
                index + 1,
                number_left - multiplicity,
                sum_left - used,
                prefix + (multiplicity,),
            )

    rec(0, count, weighted_sum, ())
    return answers


def expand(histogram: tuple[int, ...], values: tuple[int, ...]) -> list[int]:
    return [
        value
        for value, multiplicity in zip(values, histogram)
        for _ in range(multiplicity)
    ]


def simple_graphical(degrees: list[int]) -> bool:
    degrees = sorted(degrees, reverse=True)
    if sum(degrees) % 2:
        return False
    while degrees and degrees[0]:
        top = degrees.pop(0)
        if top > len(degrees):
            return False
        for i in range(top):
            degrees[i] -= 1
            if degrees[i] < 0:
                return False
        degrees.sort(reverse=True)
    return True


def bipartite_graphical(left: list[int], right: list[int]) -> bool:
    """Gale-Ryser criterion."""

    left = sorted(left, reverse=True)
    right = sorted(right, reverse=True)
    if min(left + right, default=0) < 0 or sum(left) != sum(right):
        return False
    return all(
        sum(left[:k]) <= sum(min(k, value) for value in right)
        for k in range(1, len(left) + 1)
    )


def six_moments(
    histogram: tuple[int, ...], values: tuple[int, ...], vertex_type: int
) -> tuple[int, ...]:
    totals = [0] * 6
    for a, multiplicity in zip(values, histogram):
        b = 16 - 5 * vertex_type - 2 * a
        c = a + 3 * vertex_type - 2
        terms = (
            comb(c, 2),
            c * b,
            c * a,
            comb(b, 2),
            comb(a, 2),
            a * b,
        )
        for i, value in enumerate(terms):
            totals[i] += multiplicity * value
    return tuple(totals)


def histogram_census() -> dict[str, object]:
    values = ((2, 3, 4, 5, 6, 7, 8), (0, 1, 2, 3, 4, 5), (0, 1, 2, 3))
    counts: dict[str, int] = {}
    fully_graphical_counts: dict[str, int] = {}
    survivors: dict[str, list[dict[str, list[int]]]] = {}
    extra_graphical_rejections: list[dict[str, object]] = []

    for t in range(13):
        families = (
            compositions_with_sum(11, values[0], 32 + 2 * t),
            compositions_with_sum(64, values[1], 48 - 4 * t),
            compositions_with_sum(8, values[2], 2 * t),
        )
        indexed_third: dict[tuple[int, ...], list[tuple[int, ...]]] = defaultdict(list)
        for h2 in families[2]:
            if simple_graphical(expand(h2, values[2])):
                indexed_third[six_moments(h2, values[2], 2)].append(h2)

        target = (
            105 - t,
            1296 + 4 * t,
            144 - 2 * t,
            3280 - 4 * t,
            40 - t,
            720 + 4 * t,
        )
        rows: list[dict[str, list[int]]] = []
        fully_graphical_count = 0
        for h0 in families[0]:
            m0 = six_moments(h0, values[0], 0)
            for h1 in families[1]:
                m1 = six_moments(h1, values[1], 1)
                needed = tuple(target[i] - m0[i] - m1[i] for i in range(6))
                for h2 in indexed_third.get(needed, ()):
                    a0 = expand(h0, values[0])
                    a1 = expand(h1, values[1])
                    a2 = expand(h2, values[2])
                    graphical_checks = {
                        "X0_induced": simple_graphical([a - 2 for a in a0]),
                        "X1_induced": simple_graphical([11 - 2 * a for a in a1]),
                        "X0_X1": bipartite_graphical(
                            [16 - 2 * a for a in a0], [a + 1 for a in a1]
                        ),
                        "X0_X2": bipartite_graphical(a0, [a + 4 for a in a2]),
                        "X1_X2": bipartite_graphical(a1, [6 - 2 * a for a in a2]),
                    }
                    row = {"X0": list(h0), "X1": list(h1), "X2": list(h2)}
                    if all(graphical_checks.values()):
                        fully_graphical_count += 1
                    else:
                        extra_graphical_rejections.append(
                            {
                                "t": t,
                                "histograms": row,
                                "failed_checks": [
                                    name
                                    for name, passed in graphical_checks.items()
                                    if not passed
                                ],
                                "X0_induced_degrees": sorted(
                                    [a - 2 for a in a0], reverse=True
                                ),
                            }
                        )
                    rows.append(row)
        counts[str(t)] = len(rows)
        fully_graphical_counts[str(t)] = fully_graphical_count
        if rows:
            survivors[str(t)] = rows

    return {
        "counts_by_t": counts,
        "counts_after_all_type_graphical_tests": fully_graphical_counts,
        "survivors": survivors,
        "additional_type_graphical_rejections": extra_graphical_rejections,
    }


def multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    size = len(left)
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(size))
            for j in range(size)
        ]
        for i in range(size)
    ]


def power_traces(matrix: list[list[int]], maximum: int) -> list[int]:
    size = len(matrix)
    power = [[int(i == j) for j in range(size)] for i in range(size)]
    traces = [size]
    for _ in range(maximum):
        power = multiply(power, matrix)
        traces.append(sum(power[i][i] for i in range(size)))
    return traces


def charpoly_from_traces(traces: list[int]) -> list[int]:
    degree = len(traces) - 1
    coefficients = [1]
    for k in range(1, degree + 1):
        numerator = -sum(
            coefficients[k - i] * traces[i] for i in range(1, k + 1)
        )
        if numerator % k:
            raise AssertionError("nonintegral Newton coefficient")
        coefficients.append(numerator // k)
    return coefficients


def divide_x_plus_five(coefficients: list[int]) -> list[int]:
    quotient = [coefficients[0]]
    for coefficient in coefficients[1:-1]:
        quotient.append(coefficient - 5 * quotient[-1])
    if coefficients[-1] - 5 * quotient[-1]:
        raise AssertionError("x+5 is not an exact factor")
    return quotient


def support_matrix(rows: tuple[int, ...]) -> list[list[int]]:
    matrix = [[0] * 16 for _ in range(16)]
    for i in range(8):
        for j in range(8):
            edge = (rows[i] >> j) & 1
            matrix[i][8 + j] = edge
            matrix[8 + j][i] = edge
    return matrix


def quadratic_trace(power: int) -> int:
    if power == 0:
        return 2
    if power == 1:
        return 9
    old, current = 2, 9
    for _ in range(2, power + 1):
        old, current = current, 9 * current + 38 * old
    return current


def spectrum_record(rows: tuple[int, ...]) -> dict[str, object]:
    support = support_matrix(rows)
    residual_matrix = [
        [-(int(i == j) + support[i][j]) for j in range(16)]
        for i in range(16)
    ]
    traces = power_traces(residual_matrix, 16)
    q = divide_x_plus_five(charpoly_from_traces(traces))
    outside_traces = [
        38 * 3**power
        + 28 * (-4) ** power
        + quadratic_trace(power)
        + traces[power]
        - (-5) ** power
        for power in range(1, 5)
    ]
    four_cycles = (outside_traces[3] - 23342) // 8
    if outside_traces[:3] != [0, 1002, 906]:
        raise AssertionError("incorrect outside trace")
    if outside_traces[3] < 23342 or (outside_traces[3] - 23342) % 8:
        raise AssertionError("nonintegral four-cycle count")
    return {
        "q_coefficients_descending": q,
        "traces_1_to_4": outside_traces,
        "four_cycles": four_cycles,
        "determinant": 38 * 3**38 * 4**28 * q[-1],
    }


def exponent_control(rows: tuple[int, ...]) -> dict[str, int]:
    support = support_matrix(rows)
    residual_matrix = [
        [-(int(i == j) + support[i][j]) for j in range(16)]
        for i in range(16)
    ]
    residual_trace = sum(residual_matrix[i][i] for i in range(16)) - (-5)
    correct = 38 * 3 + 28 * (-4) + 9 + residual_trace
    swapped = 28 * 3 + 38 * (-4) + 9 + residual_trace
    return {"correct_trace": correct, "swapped_trace": swapped}


def compare_discovery(
    discovery: dict[str, object],
    representatives: list[tuple[int, ...]],
    coupling_records: list[dict[str, object]],
    histograms: dict[str, object],
    spectra: list[dict[str, object]],
) -> None:
    found_rows = [[f"{row:02x}" for row in rows] for rows in representatives]
    records = discovery["support_records"]
    assert isinstance(records, list)
    expected_rows = [record["rows_hex"] for record in records]
    if found_rows != expected_rows:
        raise AssertionError("support representative mismatch")
    if [r["coupling_count"] for r in coupling_records] != [
        record["coupling_multiset_count"] for record in records
    ]:
        raise AssertionError("coupling count mismatch")
    if [r["local_flow_count"] for r in coupling_records] != [
        record["locally_closed_coupling_count"] for record in records
    ]:
        raise AssertionError("local-flow count mismatch")
    expected_hist = discovery["outside_type_degree_closure"]
    if histograms["counts_by_t"] != expected_hist["histogram_counts_by_t"]:
        raise AssertionError("histogram count mismatch")
    discovery_rows = expected_hist["surviving_histograms"]
    for t, rows in histograms["survivors"].items():
        normalized_ours = {
            (
                tuple(row["X0"]),
                tuple(row["X1"]),
                tuple(row["X2"]),
            )
            for row in rows
        }
        normalized_discovery = {
            (
                tuple(row["X0_a_histogram_for_a_2_through_8"]),
                tuple(row["X1_a_histogram_for_a_0_through_5"]),
                tuple(row["X2_a_histogram_for_a_0_through_3"]),
            )
            for row in discovery_rows[t]
        }
        if normalized_ours != normalized_discovery:
            raise AssertionError(f"histogram rows differ for t={t}")
    if [record["q_coefficients_descending"] for record in spectra] != [
        record["outside_spectrum"]["q_H_coefficients_descending"]
        for record in records
    ]:
        raise AssertionError("residual characteristic polynomial mismatch")
    if [record["traces_1_to_4"] for record in spectra] != [
        record["outside_spectrum"]["trace_powers_1_through_4"]
        for record in records
    ]:
        raise AssertionError("spectral trace mismatch")
    if [record["four_cycles"] for record in spectra] != [
        record["outside_spectrum"]["outside_four_cycles"] for record in records
    ]:
        raise AssertionError("four-cycle mismatch")
    if [record["determinant"] for record in spectra] != [
        record["outside_spectrum"]["determinant"] for record in records
    ]:
        raise AssertionError("outside determinant mismatch")


@functools.lru_cache(maxsize=1)
def build_results() -> dict[str, object]:
    repo = Path(__file__).resolve().parents[2]
    discovery_dir = repo / "attempts" / "wave81-norm16-labeled-design"
    manifest = discovery_dir / "package-manifest.sha256"
    if sha256(manifest) != EXPECTED_MANIFEST_SHA256:
        raise AssertionError("discovery package manifest changed")

    representatives, anchored_count = support_census()
    coupling_records = [coupling_count(rows) for rows in representatives]
    histograms = histogram_census()
    spectra = [spectrum_record(rows) for rows in representatives]
    discovery = json.loads((discovery_dir / "exact-results.json").read_text())
    compare_discovery(
        discovery, representatives, coupling_records, histograms, spectra
    )

    first_flow = next(
        record["first_flow"] for record in coupling_records if record["first_flow"]
    )
    capacities = tuple(tuple(row) for row in first_flow["capacities"])
    row_sums = tuple(first_flow["row_sums"])
    col_sums = tuple(first_flow["col_sums"])
    sabotage_row = next(i for i, value in enumerate(row_sums) if value)
    sabotaged = tuple(
        (0,) * N if i == sabotage_row else capacities[i] for i in range(N)
    )
    null_control_rejected = not bounded_table_exists(
        sabotaged, row_sums, col_sums
    )

    expected_counts = {"0": 43, "1": 7}
    expected_counts.update({str(t): 0 for t in range(2, 13)})
    if histograms["counts_by_t"] != expected_counts:
        raise AssertionError("unexpected histogram endpoint")
    if not null_control_rejected:
        raise AssertionError("marginal-flow null control unexpectedly survived")
    stronger_counts = histograms["counts_after_all_type_graphical_tests"]
    if stronger_counts != {
        "0": 40,
        "1": 7,
        **{str(t): 0 for t in range(2, 13)},
    }:
        raise AssertionError("unexpected strengthened graphical endpoint")

    total_couplings = sum(r["coupling_count"] for r in coupling_records)
    total_flows = sum(r["local_flow_count"] for r in coupling_records)
    return {
        "format": "wave81-independent-verification-v1",
        "claim_label": "VERIFIED",
        "conditional_scope": (
            "Wave78 norm-16 signed support branch; no upstream lattice theorem"
        ),
        "discovery_manifest_sha256": sha256(manifest),
        "support": {
            "anchored_supports": anchored_count,
            "S8xS8_orbits": len(representatives),
            "representatives_hex": [
                [f"{row:02x}" for row in rows] for rows in representatives
            ],
            "automorphism_assumed": False,
        },
        "wave78_histogram": {
            **derive_wave78_histogram(representatives),
            "derivation": [
                "n0+n1+n2=83",
                "n1+2*n2=80 from 160 support-outside incidences",
                "n2=8 from the eight deficiency-pair occurrences per side",
            ],
        },
        "couplings": {
            "per_orbit": [r["coupling_count"] for r in coupling_records],
            "total": total_couplings,
            "per_orbit_passing_local_flow": [
                r["local_flow_count"] for r in coupling_records
            ],
            "total_passing_local_flow": total_flows,
            "marginal_flow_null_control_rejected": null_control_rejected,
        },
        "outside_histograms": {
            "counts_by_t": histograms["counts_by_t"],
            "surviving_t": [0, 1],
            "local_type_equations": {
                "b": "16-5*d-2*a",
                "c": "a+3*d-2",
            },
            "type_edge_formulas": {
                "e00": "5+t",
                "e01": "112-4*t",
                "e02": "32+2*t",
                "e11": "304+4*t",
                "e12": "48-4*t",
                "e22": "t",
            },
            "six_pair_moments": [
                "sum C(c,2)=105-t",
                "sum c*b=1296+4*t",
                "sum c*a=144-2*t",
                "sum C(b,2)=3280-4*t",
                "sum C(a,2)=40-t",
                "sum a*b=720+4*t",
            ],
            "verifier_derived_strengthening": {
                "claim_label": "DERIVED",
                "counts_after_all_type_graphical_tests": stronger_counts,
                "rejections": histograms[
                    "additional_type_graphical_rejections"
                ],
                "note": (
                    "Three t=0 moment rows have nongraphical X0-induced "
                    "degree sequences; independent verification is required "
                    "before promotion."
                ),
            },
        },
        "spectrum": {
            "full_SRG_multiplicities": {"3": 54, "-4": 44},
            "principal_factor_exponents": {"3": 38, "-4": 28},
            "exponent_control": exponent_control(representatives[0]),
            "q_coefficients_descending_per_orbit": [
                record["q_coefficients_descending"] for record in spectra
            ],
            "traces_1_to_4_per_orbit": [
                record["traces_1_to_4"] for record in spectra
            ],
            "four_cycles_per_orbit": [
                record["four_cycles"] for record in spectra
            ],
            "determinants_per_orbit": [
                record["determinant"] for record in spectra
            ],
            "orbits_eliminated": 0,
        },
        "endpoint": {
            "norm16_excluded": False,
            "conway_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Conditional on the frozen Wave78 signed-support input.",
            "Couplings and histograms are necessary data, not outside graphs.",
            "Per-X2 marginal flows are local and not simultaneous.",
            "No automorphism of the hypothetical graph is assumed.",
        ],
    }


def canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run below memory floor ({free:.1f}% free)")
    encoded = canonical_json(build_results())
    if args.output:
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    elif args.verify:
        if args.verify.read_text(encoding="utf-8") != encoded:
            raise SystemExit("independent result mismatch")
        print("PASS")
    elif args.json:
        print(encoded, end="")
    else:
        result = build_results()
        print(
            "PASS "
            f"supports={result['support']['anchored_supports']}/"
            f"{result['support']['S8xS8_orbits']} "
            f"couplings={result['couplings']['total']} "
            "histograms=43+7"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
