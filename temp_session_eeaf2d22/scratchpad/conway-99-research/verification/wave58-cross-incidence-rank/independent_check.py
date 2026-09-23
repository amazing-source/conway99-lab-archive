#!/usr/bin/env python3
"""Clean-room verifier for Wave 58 cross-incidence rank synthesis.

No Wave 58 discovery code is imported.  The checker independently enumerates
the normalized m=4 and m=6 component spaces and the restricted Wave 40 lift.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
import hashlib
import itertools
import json
import os
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave58-cross-incidence-rank" / "exact-results.json"
WAVE36 = ROOT / "verification" / "wave36-block-compatibility" / "independent-results.json"
WAVE40 = ROOT / "verification" / "wave40-edge-type-coupling" / "independent-results.json"
OUTPUT = HERE / "independent-results.json"
MIN_FREE_MEMORY_PERCENT = Fraction(20, 1)

EXPECTED_M4_DISTRIBUTION = {2: 6, 4: 30, 6: 14}
EXPECTED_M6_DISTRIBUTION = {
    0: 288,
    1: 576,
    2: 3744,
    3: 6744,
    4: 11520,
    5: 7128,
    6: 3648,
    7: 936,
    9: 56,
}
EXPECTED_WAVE40_DISTRIBUTION = {
    4: 1944,
    5: 4320,
    6: 7560,
    7: 7008,
    8: 8172,
    9: 3504,
    10: 3696,
    11: 480,
    12: 658,
    14: 36,
}


class MemoryStatusEx(ctypes.Structure):
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


def free_memory_percent() -> Fraction:
    if os.name == "nt":
        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return Fraction(100 * status.ullAvailPhys, status.ullTotalPhys)
    pages = os.sysconf("SC_AVPHYS_PAGES")
    total = os.sysconf("SC_PHYS_PAGES")
    return Fraction(100 * pages, total)


def require_memory_headroom() -> Fraction:
    available = free_memory_percent()
    if available < MIN_FREE_MEMORY_PERCENT:
        raise RuntimeError(
            f"free physical memory {float(available):.2f}% is below 20%"
        )
    return available


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_hash_file(path: Path) -> None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        expected, relative = raw.split(maxsplit=1)
        actual = sha256(ROOT / relative.strip())
        assert actual == expected, (relative, expected, actual)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def perfect_matchings(items: tuple[int, ...]) -> Iterable[tuple[tuple[int, int], ...]]:
    if not items:
        yield ()
        return
    first = items[0]
    for position in range(1, len(items)):
        partner = items[position]
        remainder = items[1:position] + items[position + 1:]
        for tail in perfect_matchings(remainder):
            yield ((first, partner),) + tail


def add_edge(rows: list[int], left: int, right: int) -> None:
    assert left != right
    rows[left] |= 1 << right
    rows[right] |= 1 << left


def component_core(
    m: int,
    fibre_matchings: Sequence[Sequence[tuple[int, int]]],
    cross_12: Sequence[int],
) -> tuple[int, ...]:
    rows = [0] * (3 * m)
    for fibre, matching in enumerate(fibre_matchings):
        for left, right in matching:
            add_edge(rows, fibre * m + left, fibre * m + right)
    for index in range(m):
        add_edge(rows, index, m + index)
        add_edge(rows, index, 2 * m + index)
        add_edge(rows, m + index, 2 * m + cross_12[index])
    assert {row.bit_count() for row in rows} == {3}
    return tuple(rows)


def component_sizes(rows: Sequence[int]) -> tuple[int, ...]:
    unseen = (1 << len(rows)) - 1
    sizes = []
    while unseen:
        start_bit = unseen & -unseen
        frontier = start_bit
        unseen ^= start_bit
        size = 0
        while frontier:
            bit = frontier & -frontier
            frontier ^= bit
            vertex = bit.bit_length() - 1
            size += 1
            new = rows[vertex] & unseen
            unseen ^= new
            frontier |= new
        sizes.append(size)
    return tuple(sorted(sizes))


def triangle_count(rows: Sequence[int]) -> int:
    total = 0
    for left, neighbors in enumerate(rows):
        later = neighbors & ~((1 << (left + 1)) - 1)
        while later:
            bit = later & -later
            later ^= bit
            middle = bit.bit_length() - 1
            total += (
                rows[left]
                & rows[middle]
                & ~((1 << (middle + 1)) - 1)
            ).bit_count()
    return total


def maximum_nonedge_codegree(rows: Sequence[int]) -> int:
    maximum = 0
    for left in range(len(rows)):
        for right in range(left + 1, len(rows)):
            if rows[left] & (1 << right):
                continue
            maximum = max(maximum, (rows[left] & rows[right]).bit_count())
    return maximum


def four_cycle_count(rows: Sequence[int]) -> int:
    opposite_pairs = 0
    for left in range(len(rows)):
        for right in range(left + 1, len(rows)):
            common = (rows[left] & rows[right]).bit_count()
            opposite_pairs += common * (common - 1) // 2
    assert opposite_pairs % 2 == 0
    return opposite_pairs // 2


def edge_list(rows: Sequence[int]) -> list[list[int]]:
    return [
        [left, right]
        for left in range(len(rows))
        for right in range(left + 1, len(rows))
        if rows[left] & (1 << right)
    ]


def matching_is_valid(matching: Sequence[Sequence[int]], m: int) -> bool:
    flattened = [vertex for edge in matching for vertex in edge]
    return (
        all(len(edge) == 2 and edge[0] != edge[1] for edge in matching)
        and sorted(flattened) == list(range(m))
    )


@lru_cache(maxsize=None)
def normalized_component_census(m: int) -> dict:
    assert m in (4, 6)
    require_memory_headroom()
    matchings = tuple(perfect_matchings(tuple(range(m))))
    base = matchings[0]
    distribution: Counter[int] = Counter()
    witnesses: dict[int, dict] = {}
    raw = 0
    accepted = 0
    for matching_1 in matchings:
        for matching_2 in matchings:
            for permutation in itertools.permutations(range(m)):
                raw += 1
                if raw % 8192 == 0:
                    require_memory_headroom()
                rows = component_core(
                    m, (base, matching_1, matching_2), permutation
                )
                if component_sizes(rows) != (3 * m,):
                    continue
                if triangle_count(rows):
                    continue
                if maximum_nonedge_codegree(rows) > 2:
                    continue
                accepted += 1
                cycles = four_cycle_count(rows)
                distribution[cycles] += 1
                witnesses.setdefault(
                    cycles,
                    {
                        "second_fibre_matching": [list(edge) for edge in matching_1],
                        "third_fibre_matching": [list(edge) for edge in matching_2],
                        "cross_12_permutation": list(permutation),
                    },
                )
    return {
        "m": m,
        "raw": raw,
        "accepted": accepted,
        "distribution": dict(sorted(distribution.items())),
        "witnesses": witnesses,
    }


def validate_discovery_component_witness(m: int, cycles: int, witness: dict) -> dict:
    second = witness["second_fibre_matching"]
    third = witness["third_fibre_matching"]
    permutation = witness["cross_12_permutation"]
    assert matching_is_valid(second, m)
    assert matching_is_valid(third, m)
    assert sorted(permutation) == list(range(m))
    base = tuple(perfect_matchings(tuple(range(m))))[0]
    rows = component_core(
        m,
        (
            base,
            tuple(tuple(edge) for edge in second),
            tuple(tuple(edge) for edge in third),
        ),
        permutation,
    )
    assert component_sizes(rows) == (3 * m,)
    assert triangle_count(rows) == 0
    assert maximum_nonedge_codegree(rows) <= 2
    assert four_cycle_count(rows) == cycles
    return {
        "vertices": 3 * m,
        "C4": cycles,
        "edge_list_sha256": hashlib.sha256(canonical_bytes(edge_list(rows))).hexdigest(),
    }


def disjoint_union_from_witnesses(pieces: Sequence[tuple[int, dict]]) -> tuple[int, ...]:
    assert sum(m for m, _ in pieces) == 12
    global_rows = [0] * 36
    offset = 0
    for m, witness in pieces:
        base = tuple(perfect_matchings(tuple(range(m))))[0]
        local = component_core(
            m,
            (
                base,
                tuple(tuple(edge) for edge in witness["second_fibre_matching"]),
                tuple(tuple(edge) for edge in witness["third_fibre_matching"]),
            ),
            witness["cross_12_permutation"],
        )
        for local_left, neighbors in enumerate(local):
            fibre_left, index_left = divmod(local_left, m)
            global_left = fibre_left * 12 + offset + index_left
            remaining = neighbors
            while remaining:
                bit = remaining & -remaining
                remaining ^= bit
                local_right = bit.bit_length() - 1
                fibre_right, index_right = divmod(local_right, m)
                global_right = fibre_right * 12 + offset + index_right
                global_rows[global_left] |= 1 << global_right
        offset += m
    return tuple(global_rows)


def graph_summary(rows: Sequence[int]) -> dict:
    return {
        "vertices": len(rows),
        "degree_set": sorted({row.bit_count() for row in rows}),
        "component_sizes": list(component_sizes(rows)),
        "triangles": triangle_count(rows),
        "C4_X": four_cycle_count(rows),
        "maximum_nonedge_codegree": maximum_nonedge_codegree(rows),
        "edge_list_sha256": hashlib.sha256(
            canonical_bytes(edge_list(rows))
        ).hexdigest(),
    }


def quotient_rows(edges: Sequence[Sequence[int]]) -> tuple[int, ...]:
    rows = [0] * 18
    for left, right in edges:
        add_edge(rows, left, right)
    assert {row.bit_count() for row in rows} == {4}
    return tuple(rows)


def endpoint_assignment_map(qrows: Sequence[int]) -> dict[tuple[int, int], tuple[int, int]]:
    mapping = {}
    for vertex, row in enumerate(qrows):
        neighbors = [index for index in range(18) if row & (1 << index)]
        target_fibres = sorted({neighbor // 6 for neighbor in neighbors})
        assert len(target_fibres) == 2
        for coefficient, target_fibre in enumerate(target_fibres):
            targets = sorted(
                neighbor
                for neighbor in neighbors
                if neighbor // 6 == target_fibre
            )
            assert len(targets) == 2
            for constant, target in enumerate(targets):
                mapping[(vertex, target)] = (constant, coefficient)
    return mapping


def forbidden_triangle_patterns(
    qrows: Sequence[int],
    assignment: dict[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    patterns = []
    for left, middle, right in itertools.combinations(range(18), 3):
        if not (
            qrows[left] & (1 << middle)
            and qrows[left] & (1 << right)
            and qrows[middle] & (1 << right)
        ):
            continue
        mask = 0
        value = 0
        for vertex, first, second in (
            (left, middle, right),
            (middle, left, right),
            (right, left, middle),
        ):
            first_constant, first_coefficient = assignment[(vertex, first)]
            second_constant, second_coefficient = assignment[(vertex, second)]
            assert first_coefficient != second_coefficient
            required = first_constant ^ second_constant
            mask |= 1 << vertex
            value |= required << vertex
        patterns.append((mask, value))
    return tuple(patterns)


def lift_rows(
    qrows: Sequence[int],
    assignment: dict[tuple[int, int], tuple[int, int]],
    mask: int,
) -> tuple[int, ...]:
    rows = [0] * 36
    for vertex in range(18):
        add_edge(rows, 2 * vertex, 2 * vertex + 1)
    for left in range(18):
        neighbors = qrows[left] & ~((1 << (left + 1)) - 1)
        while neighbors:
            bit = neighbors & -neighbors
            neighbors ^= bit
            right = bit.bit_length() - 1
            lc, lv = assignment[(left, right)]
            rc, rv = assignment[(right, left)]
            left_endpoint = lc ^ (((mask >> left) & 1) if lv else 0)
            right_endpoint = rc ^ (((mask >> right) & 1) if rv else 0)
            add_edge(rows, 2 * left + left_endpoint, 2 * right + right_endpoint)
    assert {row.bit_count() for row in rows} == {3}
    return tuple(rows)


@lru_cache(maxsize=None)
def restricted_wave40_census(encoded_edges: tuple[tuple[int, int], ...]) -> dict:
    require_memory_headroom()
    qrows = quotient_rows(encoded_edges)
    assignment = endpoint_assignment_map(qrows)
    forbidden = forbidden_triangle_patterns(qrows, assignment)
    assert len(forbidden) == 16
    distribution: Counter[int] = Counter()
    profiles: Counter[tuple[int, ...]] = Counter()
    accepted = 0
    for mask in range(1 << 18):
        if mask % 8192 == 0:
            require_memory_headroom()
        if any(mask & positions == values for positions, values in forbidden):
            continue
        rows = lift_rows(qrows, assignment, mask)
        assert triangle_count(rows) == 0
        assert maximum_nonedge_codegree(rows) <= 2
        accepted += 1
        distribution[four_cycle_count(rows)] += 1
        profiles[component_sizes(rows)] += 1
    return {
        "raw_masks": 1 << 18,
        "triangle_free_masks": accepted,
        "component_profiles": {
            "+".join(map(str, key)): value for key, value in sorted(profiles.items())
        },
        "C4_distribution": dict(sorted(distribution.items())),
    }


def gram_rank_and_chronology_checks(wave36: dict) -> dict:
    assert wave36["claim_label"] == "VERIFIED"
    general = wave36["general_checks"]
    assert general["block_equations"]["xx"] == (
        "BB^T=12I-A_X+2J-RR^T-A_X^2"
    )
    assert general["block_equations"]["yy"] == "B^TB+H^2=12I-H+2J"
    assert general["component_patterns"]["surviving_partitions"] == [
        [4, 4, 4], [4, 8], [6, 6], [12]
    ]
    assert general["component_moments"]["equality"] == "z_y=m/2 for all 60 y"
    rows = []
    for kappa in (1, 2, 3):
        rank_b = 35 - kappa
        kernel_dimension = 60 - rank_b
        kernel_trace = 26 - 4 * kappa
        numerator_a = kernel_trace + 4 * kernel_dimension
        assert numerator_a % 7 == 0
        a = numerator_a // 7
        b = kernel_dimension - a
        assert (a, b) == (18, 7 + kappa)
        sample = general["spectral_transfer_samples"][str(kappa)]
        assert sample["gram_rank"] == rank_b
        assert sample["kernel_multiplicities"] == {"3": a, "-4": b}
        rows.append([a, b, kappa, rank_b])
    return {
        "source_claim_label": "VERIFIED",
        "novel_in_wave58": False,
        "rows_a_b_kappa_rankB": rows,
        "component_partitions": [[12], [4, 8], [6, 6], [4, 4, 4]],
    }


def gram_identity_checks() -> dict:
    # Diagonal values use degrees 8 in Y and 3 in X.
    assert 12 + 2 - 8 == 6
    assert 12 + 2 - 1 - 3 == 10
    # On the 33-dimensional within-fibre-zero space:
    # 12I-A-A^2=(3I-A)(4I+A).
    for eigenvalue in range(-3, 4):
        assert 12 - eigenvalue - eigenvalue**2 == (
            3 - eigenvalue
        ) * (4 + eigenvalue)
    return {
        "B_transpose_B": "12I-A_Y+2J-A_Y^2",
        "B_B_transpose": "12I-A_X+2J-blockdiag(J12,J12,J12)-A_X^2",
        "factor_on_within_fibre_zero": "(3I-A_X)(4I+A_X)",
        "kernel_B_transpose_dimension": "kappa+1",
        "rank_B": "35-kappa",
    }


def c4_bound_check() -> dict:
    wedges = 36 * (3 * 2 // 2)
    assert wedges == 108
    # Each wedge closes at most once because the endpoints are nonadjacent
    # and mu=2, with the wedge center already one common neighbor.
    assert wedges // 4 == 27
    return {
        "wedge_count": 108,
        "four_wedges_per_C4": 4,
        "C4_X_upper_bound": 27,
        "type": "universal upper bound, not an attainment claim",
    }


def residual_power_sums(a: int, b: int, q: int) -> list[int]:
    return [
        59 - a - b,
        -8 - 3 * a + 4 * b,
        416 - 9 * a - 16 * b,
        -320 - 27 * a + 64 * b,
        4472 + 8 * q - 81 * a - 256 * b,
    ]


def verify_scalar_counts(a: int, b: int, q: int, counts: Sequence[int]) -> dict:
    roots = (-3, -2, -1, 0, 1, 2)
    assert len(counts) == len(roots)
    assert all(isinstance(count, int) and count >= 0 for count in counts)
    actual = [
        sum(count * root**power for count, root in zip(counts, roots))
        for power in range(5)
    ]
    assert actual == residual_power_sums(a, b, q)
    return {
        "a": a,
        "b": b,
        "q": q,
        "counts": list(counts),
        "power_sums": actual,
        "graph_spectrum_claimed": False,
    }


def verify_discovery(data: dict, wave36: dict, wave40: dict) -> dict:
    assert data["claim_label"] == "DERIVED"
    assert data["upstream_novelty_guard"]["rank_and_multiplicity_identities_are_new"] is False
    assert data["gram_identities"]["B_transpose_B"] == "12I-A_Y+2J-A_Y^2"
    assert data["gram_identities"]["B_B_transpose"] == (
        "12I-A_X+2J-blockdiag(J12,J12,J12)-A_X^2"
    )
    assert data["result"]["surviving_a_b_kappa"] == [
        [18, 8, 1], [18, 9, 2], [18, 10, 3]
    ]
    assert data["result"]["wave57_rows_before"] == 18
    assert data["result"]["wave57_rows_after"] == 3
    assert data["result"]["universal_C4_X_upper_bound"] == 27
    assert data["result"]["contradiction"] is False
    assert data["result"]["endpoint"] == "UNKNOWN"
    assert data["result"]["conway_99"] == "UNKNOWN"
    kernel_rows = data["kernel_and_rank_derivation"]["rows"]
    assert [
        [
            row["a_mult_Y_3"],
            row["b_mult_Y_minus4"],
            row["kappa_components"],
            row["rank_B"],
            row["dim_kernel_B_transpose"],
            row["dim_kernel_B"],
        ]
        for row in kernel_rows
    ] == [
        [18, 8, 1, 34, 2, 26],
        [18, 9, 2, 33, 3, 27],
        [18, 10, 3, 32, 4, 28],
    ]

    chronology = gram_rank_and_chronology_checks(wave36)
    assert data["wave36_independent_replay"]["source_claim_label"] == "VERIFIED"
    assert data["wave36_independent_replay"]["rank_B"] == "35-kappa"
    assert data["wave36_independent_replay"]["mult_Y_3"] == 18
    assert data["wave36_independent_replay"]["mult_Y_minus4"] == "7+kappa"

    structural = data["component_structural_reduction"]
    discovery_censuses = structural["component_censuses"]
    local_results = {}
    for key, m, expected in (
        ("m4", 4, EXPECTED_M4_DISTRIBUTION),
        ("m6", 6, EXPECTED_M6_DISTRIBUTION),
    ):
        independent = normalized_component_census(m)
        assert independent["distribution"] == expected
        target = discovery_censuses[key]
        assert target["raw_labelled_configurations"] == independent["raw"]
        assert target[
            "accepted_connected_triangle_free_codegree_at_most_2"
        ] == independent["accepted"]
        assert {
            int(cycles): count
            for cycles, count in target["C4_distribution"].items()
        } == expected
        assert target["C4_values"] == sorted(expected)
        witness_summaries = {}
        for cycles, witness in target["canonical_witness_by_C4"].items():
            witness_summaries[cycles] = validate_discovery_component_witness(
                m, int(cycles), witness
            )
        assert {int(value) for value in witness_summaries} == set(expected)
        local_results[key] = {
            "normalization": (
                "complete coordinate-normalized presentations; counts are "
                "not graph-isomorphism class counts"
            ),
            "raw": independent["raw"],
            "accepted": independent["accepted"],
            "C4_distribution": expected,
            "stored_witnesses_checked": len(witness_summaries),
        }

    m4_values = set(EXPECTED_M4_DISTRIBUTION)
    m6_values = set(EXPECTED_M6_DISTRIBUTION)
    kappa3 = sorted(
        {x + y + z for x in m4_values for y in m4_values for z in m4_values}
    )
    kappa2_66 = sorted({x + y for x in m6_values for y in m6_values})
    assert kappa3 == [6, 8, 10, 12, 14, 16, 18]
    assert kappa2_66 == list(range(17)) + [18]
    assert structural["universal_kappa3_C4_X_values"] == kappa3
    assert structural["kappa2_partition_6_plus_6_C4_X_values"] == kappa2_66
    assert structural["kappa2_partition_4_plus_8_C4_X_bounds"] == [2, 24]
    assert structural["kappa2_union_C4_X_bounds"] == [0, 24]

    # Reconstruct the stored disjoint-union controls from their component
    # witnesses, rather than trusting discovery hashes.
    m6_zero = discovery_censuses["m6"]["canonical_witness_by_C4"]["0"]
    kappa2_rows = disjoint_union_from_witnesses(
        ((6, m6_zero), (6, m6_zero))
    )
    kappa2_summary = graph_summary(kappa2_rows)
    assert kappa2_summary == structural["kappa2_local_A_X_control"]

    m4_four = discovery_censuses["m4"]["canonical_witness_by_C4"]["4"]
    kappa3_rows = disjoint_union_from_witnesses(
        ((4, m4_four), (4, m4_four), (4, m4_four))
    )
    kappa3_summary = graph_summary(kappa3_rows)
    assert kappa3_summary == structural["kappa3_local_A_X_control"]

    scalar = structural["kappa3_aligned_scalar_control"]
    scalar_check = verify_scalar_counts(
        18, 10, 12, tuple(scalar["multiplicities"])
    )
    assert scalar_check["power_sums"] == scalar["power_sums_0_to_4"]

    # The q=0 Wave57 scalar controls for kappa 1 and 2.
    aligned = data["aligned_failure_of_obstruction_controls"]
    prior_core = wave36["restricted_core"]
    assert aligned["kappa_1"]["A_X_components"] == prior_core["components"] == 1
    assert aligned["kappa_1"]["A_X_C4"] == prior_core["four_cycles"] == 0
    assert (
        aligned["kappa_1"]["forced_gram_rank"]
        == prior_core["forced_gram_rank_over_Q"]
        == 34
    )
    for key, a, b in (("kappa_1", 18, 8), ("kappa_2", 18, 9)):
        target = aligned[key]["wave57_scalar_control"]
        counts = tuple(
            target["linear_root_counts"][str(root)]
            for root in (-3, -2, -1, 0, 1, 2)
        )
        verify_scalar_counts(a, b, 0, counts)
        assert target["graph_realization_claimed"] is False
    assert aligned["simultaneous_B_or_A_Y_claimed"] is False

    assert wave40["claim_label"] == "VERIFIED_SCOPED"
    explicit = wave40["explicit_rank_eleven_quotient"]
    assert explicit["rank_F3_2I_plus_A_Q"] == 11
    encoded_edges = tuple(tuple(edge) for edge in explicit["edges"])
    wave40_result = restricted_wave40_census(encoded_edges)
    assert wave40_result == {
        "raw_masks": 262144,
        "triangle_free_masks": 37378,
        "component_profiles": {"12+24": 37378},
        "C4_distribution": EXPECTED_WAVE40_DISTRIBUTION,
    }
    target_wave40 = data["wave40_restricted_lift_replay"]
    assert target_wave40["source_claim_label"] == "VERIFIED_SCOPED"
    assert target_wave40["normalized_rank_eleven_quotient_count"] == 8
    target_census = target_wave40["canonical_replay"]
    assert target_census["raw_masks"] == 262144
    assert target_census["triangle_free_masks"] == 37378
    assert target_census["component_profile_distribution"] == {"12+24": 37378}
    assert {
        int(cycles): count
        for cycles, count in target_census["C4_X_distribution"].items()
    } == EXPECTED_WAVE40_DISTRIBUTION
    assert target_census["C4_X_range"] == [4, 14]

    return {
        "chronology": chronology,
        "component_censuses": local_results,
        "component_specific_C4": {
            "kappa_1": {
                "bound": [0, 27],
                "exact_attainable_set_claimed": False,
            },
            "kappa_2_6_plus_6": {
                "exact_local_set": kappa2_66,
            },
            "kappa_2_4_plus_8": {
                "bound": [2, 24],
                "m8_enumerated": False,
            },
            "kappa_2_overall": {
                "bound": [0, 24],
                "exact_attainable_set_claimed": False,
            },
            "kappa_3": {
                "exact_local_set": kappa3,
            },
        },
        "controls": {
            "kappa_2_A_X": kappa2_summary,
            "kappa_3_A_X": kappa3_summary,
            "kappa_3_scalar": scalar_check,
            "simultaneous_B_or_A_Y": False,
        },
        "wave40_replay": {
            **wave40_result,
            "restriction": (
                "one of eight normalized rank-11 quotients, under all-222 "
                "and r3=12; not all endpoint cores"
            ),
        },
    }


def run_checks(
    discovery_path: Path = DISCOVERY,
    write_output: bool = True,
) -> dict:
    start_memory = require_memory_headroom()
    check_hash_file(HERE / "preinspection-freeze.sha256")
    if discovery_path.resolve() == DISCOVERY.resolve():
        check_hash_file(HERE / "discovery-freeze.sha256")
    discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
    wave36 = json.loads(WAVE36.read_text(encoding="utf-8"))
    wave40 = json.loads(WAVE40.read_text(encoding="utf-8"))

    gram = gram_identity_checks()
    c4 = c4_bound_check()
    verified = verify_discovery(discovery, wave36, wave40)
    result = {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "conditional n3=4158 fixed-triangle cross-incidence synthesis; "
            "coordinate-normalized m=4/m=6 component censuses and one "
            "explicitly restricted Wave40 lift only"
        ),
        "gram_and_rank": gram,
        "universal_C4_bound": c4,
        "independent_replay": verified,
        "wording_audit": {
            "normalized_component_counts_are_isomorphism_counts": False,
            "coordinate_normalization_uses_completed_graph_automorphism": False,
            "kappa_1_0_to_27_is_bound_not_exact_set": True,
            "kappa_2_0_to_24_is_bound_not_exact_set": True,
            "kappa_2_4_plus_8_m8_component_enumerated": False,
            "kappa_3_set_exact_for_local_component_class": True,
            "stored_canonical_witness_means": (
                "deterministic first normalized witness by C4, not canonical "
                "graph-isomorphism representative"
            ),
        },
        "status_boundary": {
            "simultaneous_B_or_A_Y_constructed": False,
            "endpoint_excluded": False,
            "endpoint_graph_constructed": False,
            "improved_general_n3_upper_bound": False,
            "conway_99_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "resource_guard": {
            "minimum_free_physical_memory_percent": 20,
            "start_free_physical_memory_percent": round(float(start_memory), 2),
            "finish_free_physical_memory_percent": round(
                float(require_memory_headroom()), 2
            ),
        },
        "limitations": [
            "All mathematics is conditional on the prism-free n3=4158 endpoint.",
            "Wave36 already proves the rank, component, and multiplicity identities.",
            "The m=8 and m=12 component spaces are not enumerated.",
            "Local A_X and scalar controls are separate and do not construct B or A_Y.",
            "The Wave40 replay covers one restricted quotient, not all endpoint cores.",
            "No graph, endpoint exclusion, or Conway-99 resolution is supplied.",
        ],
    }
    if write_output:
        OUTPUT.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return result


def verify_saved(path: Path) -> dict:
    expected = json.loads(json.dumps(run_checks(write_output=False)))
    actual = json.loads(path.read_text(encoding="utf-8"))
    for payload in (expected, actual):
        payload["resource_guard"].pop("start_free_physical_memory_percent")
        payload["resource_guard"].pop("finish_free_physical_memory_percent")
    assert actual == expected
    return actual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DISCOVERY)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        result = verify_saved(args.verify)
    else:
        result = run_checks(discovery_path=args.input, write_output=False)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "claim_label": result["claim_label"],
        "m4_accepted":
            result["independent_replay"]["component_censuses"]["m4"]["accepted"],
        "m6_accepted":
            result["independent_replay"]["component_censuses"]["m6"]["accepted"],
        "wave40_triangle_free":
            result["independent_replay"]["wave40_replay"]["triangle_free_masks"],
        "conway_99_status": result["status_boundary"]["conway_99_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
