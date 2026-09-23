#!/usr/bin/env python3
"""Exact Wave 58 synthesis of cross-incidence rank and star rows.

The rank/component formulas are replayed from the independently verified Wave
36 package and are not claimed as new.  This checker adds the exact
intersection with Wave 57 and bounded component enumerations.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence


MIN_FREE_PERCENT = 15.0
RELATIVE_ROOT = Path(__file__).resolve().parents[2]
WAVE57 = RELATIVE_ROOT / "attempts/wave57-star-complement/exact-results.json"
WAVE36 = (
    RELATIVE_ROOT
    / "verification/wave36-block-compatibility/independent-results.json"
)
WAVE40 = (
    RELATIVE_ROOT
    / "verification/wave40-edge-type-coupling/independent-results.json"
)

EXPECTED_INPUT_HASHES = {
    "attempts/wave57-star-complement/exact-results.json":
        "2b49b0bf3d52c0101cfcd59c3324279c1f153f4d48504c7ae67658e8786e6216",
    "verification/wave36-block-compatibility/independent-results.json":
        "b92ee5cde6a63ba3cce09bc2eae1518979aea09c4f5db39789b65f117b0768c4",
    "verification/wave40-edge-type-coupling/independent-results.json":
        "822f758e04bcf95576cf8c5adc5cff2131ffa13cd286a6924137149de0dc3a9e",
}


class MemoryStatus(ctypes.Structure):
    _fields_ = (
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_physical", ctypes.c_ulonglong),
        ("available_physical", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("available_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("available_virtual", ctypes.c_ulonglong),
        ("available_extended_virtual", ctypes.c_ulonglong),
    )


def free_memory_percent() -> float:
    if sys.platform != "win32":
        return 100.0
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.available_physical / status.total_physical


def require_memory() -> None:
    free = free_memory_percent()
    if free < MIN_FREE_PERCENT:
        raise MemoryError(
            f"{free:.2f}% free physical memory is below {MIN_FREE_PERCENT:.2f}%"
        )


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_inputs() -> None:
    for relative, expected in EXPECTED_INPUT_HASHES.items():
        actual = sha256_path(RELATIVE_ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"frozen input changed: {relative}: {actual} != {expected}"
            )


def load_inputs() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    verify_frozen_inputs()
    return tuple(
        json.loads(path.read_text(encoding="utf-8"))
        for path in (WAVE57, WAVE36, WAVE40)
    )  # type: ignore[return-value]


def gram_entry_ledger() -> dict[str, object]:
    """Entrywise common-neighbor derivation of both Gram formulas."""
    btb = {
        "diagonal": {
            "rhs": "12+2-deg_Y=6",
            "meaning": "each Y vertex has six X neighbors",
        },
        "adjacent_distinct": {
            "rhs": "1-(A_Y^2)_{yz}",
            "meaning": "the unique common neighbor minus those already in Y",
        },
        "nonadjacent_distinct": {
            "rhs": "2-(A_Y^2)_{yz}",
            "meaning": "the two common neighbors minus those already in Y",
        },
    }
    bb_t = {
        "diagonal": {
            "rhs": "12+2-1-deg_X=10",
            "meaning": "each X vertex has ten Y neighbors",
        },
        "same_sector_adjacent": {
            "rhs": "-1+2-1-0=0",
            "meaning": "the sector root is the adjacent pair's unique common neighbor",
        },
        "cross_sector_adjacent": {
            "rhs": "-1+2-0-0=1",
            "meaning": "the adjacent pair's unique common neighbor lies in Y",
        },
        "same_sector_nonadjacent": {
            "rhs": "1-(A_X^2)_{xx'}",
            "meaning": "one of the two common neighbors is the sector root",
        },
        "cross_sector_nonadjacent": {
            "rhs": "2-(A_X^2)_{xx'}",
            "meaning": "neither fixed-triangle vertex is common",
        },
    }
    return {
        "B_transpose_B": "12I-A_Y+2J-A_Y^2",
        "B_transpose_B_entry_cases": btb,
        "B_B_transpose": (
            "12I-A_X+2J-blockdiag(J12,J12,J12)-A_X^2"
        ),
        "B_B_transpose_entry_cases": bb_t,
    }


def replay_wave36(
    wave36: dict[str, object],
) -> dict[str, object]:
    general = wave36["general_checks"]
    moments = general["component_moments"]
    patterns = general["component_patterns"]
    spectral = general["spectral_general_form"]
    if general["block_equations"]["xx"] != (
        "BB^T=12I-A_X+2J-RR^T-A_X^2"
    ):
        raise AssertionError("Wave 36 XX Gram equation changed")
    expected_partitions = [[4, 4, 4], [4, 8], [6, 6], [12]]
    if patterns["surviving_partitions"] != expected_partitions:
        raise AssertionError("Wave 36 component partitions changed")
    if moments["equality"] != "z_y=m/2 for all 60 y":
        raise AssertionError("Wave 36 component balance changed")
    if "(t-3)^18" not in spectral["charpoly"] or "(t+4)^(7+c)" not in spectral[
        "charpoly"
    ]:
        raise AssertionError("Wave 36 spectral transfer changed")
    samples = general["spectral_transfer_samples"]
    for component_count in (1, 2, 3):
        sample = samples[str(component_count)]
        if sample["gram_rank"] != 35 - component_count:
            raise AssertionError("Wave 36 sample rank identity changed")
        if sample["kernel_multiplicities"] != {
            "-4": 7 + component_count,
            "3": 18,
        }:
            raise AssertionError("Wave 36 kernel multiplicities changed")
    return {
        "source_claim_label": wave36["claim_label"],
        "component_unit_partitions": expected_partitions,
        "component_count_values": [1, 2, 3],
        "rank_B": "35-kappa",
        "mult_Y_3": 18,
        "mult_Y_minus4": "7+kappa",
        "replay_passed": True,
    }


def kernel_rank_derivation() -> dict[str, object]:
    rows = []
    for kappa in (1, 2, 3):
        rank = 35 - kappa
        kernel_bt = 36 - rank
        sector_plane = 2
        within_sector_lambda3 = kappa - 1
        if kernel_bt != sector_plane + within_sector_lambda3:
            raise AssertionError("B^T kernel decomposition failed")
        kernel_b = 60 - rank
        a = 18
        b = 7 + kappa
        if kernel_b != a + b:
            raise AssertionError("B kernel multiplicity identity failed")
        if 3 * a - 4 * b != 26 - 4 * kappa:
            raise AssertionError("transferred trace identity failed")
        rows.append(
            {
                "kappa_components": kappa,
                "rank_B": rank,
                "dim_kernel_B_transpose": kernel_bt,
                "sector_constant_sum_zero_dimension": sector_plane,
                "within_sector_zero_A_X_eigenvalue_3_dimension": (
                    within_sector_lambda3
                ),
                "dim_kernel_B": kernel_b,
                "a_mult_Y_3": a,
                "b_mult_Y_minus4": b,
                "a_plus_b": a + b,
            }
        )
    return {
        "factor_on_within_sector_zero": "(3I-A_X)(4I+A_X)",
        "cubic_spectrum_interval": "[-3,3]",
        "minus4_cannot_be_A_X_eigenvalue": True,
        "kernel_B_transpose": (
            "two sector-constant sum-zero vectors plus the kappa-1 "
            "A_X eigenvalue-3 vectors in the within-sector-zero space"
        ),
        "rows": rows,
    }


def collapse_wave57(
    wave57: dict[str, object],
) -> dict[str, object]:
    ledger = wave57["multiplicity_fourth_moment_ledger"]
    if len(ledger) != 18:
        raise AssertionError("Wave 57 no longer has exactly 18 rows")
    keys = {
        (row["a_mult_Y_3"], row["b_mult_Y_minus4"]): row
        for row in ledger
    }
    expected_keys = {(a, b) for a in range(18, 21) for b in range(8, 14)}
    if set(keys) != expected_keys:
        raise AssertionError("Wave 57 multiplicity rectangle changed")
    survivors = []
    for kappa in (1, 2, 3):
        key = (18, 7 + kappa)
        row = keys[key]
        if not row["C4_X_min"] <= 0 <= row["C4_X_max"]:
            raise AssertionError("new row unexpectedly fails Wave 57 q=0")
        survivors.append(
            {
                "a_mult_Y_3": key[0],
                "b_mult_Y_minus4": key[1],
                "kappa_components": kappa,
                "wave57_C4_X_interval": [
                    row["C4_X_min"],
                    row["C4_X_max"],
                ],
                "residual_degree": row["residual_degree"],
                "minimum_U_hit_star_set_lambda3": (
                    row["minimum_U_hit_star_set_lambda3"]
                ),
                "minimum_U_hit_star_set_lambda_minus4": (
                    row["minimum_U_hit_star_set_lambda_minus4"]
                ),
            }
        )
    return {
        "input_row_count": len(ledger),
        "survivor_count": len(survivors),
        "eliminated_row_count": len(ledger) - len(survivors),
        "survivors": survivors,
    }


def perfect_matchings(items: tuple[int, ...]) -> Iterable[tuple[tuple[int, int], ...]]:
    if not items:
        yield ()
        return
    first = items[0]
    for index in range(1, len(items)):
        second = items[index]
        rest = items[1:index] + items[index + 1 :]
        for tail in perfect_matchings(rest):
            yield tuple(sorted(((first, second), *tail)))


def component_graph(
    m: int,
    matchings: Sequence[Sequence[tuple[int, int]]],
    permutation: Sequence[int],
) -> list[set[int]]:
    adjacency = [set() for _ in range(3 * m)]

    def add(left: int, right: int) -> None:
        adjacency[left].add(right)
        adjacency[right].add(left)

    for fibre, matching in enumerate(matchings):
        for left, right in matching:
            add(fibre * m + left, fibre * m + right)
    for index in range(m):
        add(index, m + index)
        add(index, 2 * m + index)
        add(m + index, 2 * m + permutation[index])
    if set(map(len, adjacency)) != {3}:
        raise AssertionError("component graph is not cubic")
    return adjacency


def component_sizes(adjacency: Sequence[set[int]]) -> tuple[int, ...]:
    unseen = set(range(len(adjacency)))
    sizes = []
    while unseen:
        stack = [unseen.pop()]
        size = 0
        while stack:
            vertex = stack.pop()
            size += 1
            for neighbor in adjacency[vertex]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
        sizes.append(size)
    return tuple(sorted(sizes))


def triangle_count(adjacency: Sequence[set[int]]) -> int:
    return sum(
        1
        for left in range(len(adjacency))
        for middle in adjacency[left]
        if left < middle
        for right in adjacency[left] & adjacency[middle]
        if middle < right
    )


def four_cycle_count(adjacency: Sequence[set[int]]) -> int:
    opposite_pair_count = sum(
        len(adjacency[left] & adjacency[right])
        * (len(adjacency[left] & adjacency[right]) - 1)
        // 2
        for left in range(len(adjacency))
        for right in range(left + 1, len(adjacency))
    )
    if opposite_pair_count % 2:
        raise AssertionError("four-cycle opposite-pair count is odd")
    return opposite_pair_count // 2


def max_nonedge_codegree(adjacency: Sequence[set[int]]) -> int:
    return max(
        len(adjacency[left] & adjacency[right])
        for left in range(len(adjacency))
        for right in range(left + 1, len(adjacency))
        if right not in adjacency[left]
    )


@lru_cache(maxsize=None)
def component_census(m: int) -> dict[str, object]:
    if m not in (4, 6):
        raise ValueError("only the tractable m=4,6 censuses are frozen")
    require_memory()
    matchings = tuple(perfect_matchings(tuple(range(m))))
    base = matchings[0]
    distribution: Counter[int] = Counter()
    witness_by_q: dict[int, dict[str, object]] = {}
    raw = 0
    accepted = 0
    for second in matchings:
        for third in matchings:
            for permutation in itertools.permutations(range(m)):
                raw += 1
                if raw % 4096 == 0:
                    require_memory()
                adjacency = component_graph(
                    m, (base, second, third), permutation
                )
                if component_sizes(adjacency) != (3 * m,):
                    continue
                if triangle_count(adjacency):
                    continue
                if max_nonedge_codegree(adjacency) > 2:
                    continue
                accepted += 1
                q = four_cycle_count(adjacency)
                distribution[q] += 1
                witness_by_q.setdefault(
                    q,
                    {
                        "second_fibre_matching": [list(edge) for edge in second],
                        "third_fibre_matching": [list(edge) for edge in third],
                        "cross_12_permutation": list(permutation),
                    },
                )
    return {
        "m_per_fibre": m,
        "normalization": (
            "fix fibre-0 matching and both cross matchings from fibre 0 "
            "by coordinate relabeling only; enumerate both remaining fibre "
            "matchings and the cross-12 permutation"
        ),
        "raw_labelled_configurations": raw,
        "accepted_connected_triangle_free_codegree_at_most_2": accepted,
        "C4_distribution": {
            str(key): distribution[key] for key in sorted(distribution)
        },
        "C4_values": sorted(distribution),
        "canonical_witness_by_C4": {
            str(key): witness_by_q[key] for key in sorted(witness_by_q)
        },
    }


def disjoint_union_component_controls(
    pieces: Sequence[tuple[int, int]]
) -> list[set[int]]:
    """Build full three-fibre X from (m,q) component witnesses."""
    if sum(m for m, _ in pieces) != 12:
        raise ValueError("component units must partition twelve")
    adjacency = [set() for _ in range(36)]
    offsets = [0, 0, 0]
    for m, q in pieces:
        census = component_census(m)
        witness = census["canonical_witness_by_C4"][str(q)]
        base = tuple(perfect_matchings(tuple(range(m))))[0]
        second = tuple(tuple(edge) for edge in witness["second_fibre_matching"])
        third = tuple(tuple(edge) for edge in witness["third_fibre_matching"])
        local = component_graph(
            m,
            (base, second, third),
            witness["cross_12_permutation"],
        )
        start = offsets[0]
        for local_left, neighbors in enumerate(local):
            fibre_left, index_left = divmod(local_left, m)
            global_left = fibre_left * 12 + start + index_left
            for local_right in neighbors:
                fibre_right, index_right = divmod(local_right, m)
                global_right = fibre_right * 12 + start + index_right
                adjacency[global_left].add(global_right)
        offsets = [value + m for value in offsets]
    return adjacency


def graph_control_summary(
    adjacency: Sequence[set[int]],
) -> dict[str, object]:
    edges = [
        [left, right]
        for left in range(len(adjacency))
        for right in sorted(adjacency[left])
        if left < right
    ]
    return {
        "vertices": len(adjacency),
        "degree_set": sorted(set(map(len, adjacency))),
        "component_sizes": list(component_sizes(adjacency)),
        "triangles": triangle_count(adjacency),
        "C4_X": four_cycle_count(adjacency),
        "maximum_nonedge_codegree": max_nonedge_codegree(adjacency),
        "edge_list_sha256": hashlib.sha256(canonical_bytes(edges)).hexdigest(),
    }


def residual_power_sums(a: int, b: int, q: int) -> list[int]:
    return [
        59 - a - b,
        -8 - 3 * a + 4 * b,
        416 - 9 * a - 16 * b,
        -320 - 27 * a + 64 * b,
        4472 + 8 * q - 81 * a - 256 * b,
    ]


def wedge_four_cycle_bound(vertices: int = 36, degree: int = 3) -> dict[str, object]:
    wedges = vertices * degree * (degree - 1) // 2
    # Triangle-freeness makes every neighbor pair at a vertex nonadjacent.
    # In the ambient SRG such a pair has exactly mu=2 common neighbors. One is
    # the wedge center, leaving at most one other center and hence at most one
    # four-cycle through the wedge.
    maximum = wedges // 4
    if wedges != 108 or maximum != 27:
        raise AssertionError("fixed cubic wedge bound changed")
    return {
        "vertices": vertices,
        "degree": degree,
        "neighbor_pair_wedges": wedges,
        "maximum_four_cycles_per_wedge": 1,
        "four_wedges_per_four_cycle": 4,
        "C4_X_upper_bound": maximum,
        "reason": (
            "triangle-free neighbor pairs are nonadjacent; mu=2 leaves at "
            "most one second common neighbor besides the wedge center"
        ),
    }


def verify_linear_spectral_control(
    a: int, b: int, q: int, counts: Sequence[int]
) -> dict[str, object]:
    roots = (-3, -2, -1, 0, 1, 2)
    actual = [
        sum(count * root**power for count, root in zip(counts, roots))
        for power in range(5)
    ]
    expected = residual_power_sums(a, b, q)
    if actual != expected:
        raise AssertionError("residual scalar control moments fail")
    return {
        "a_mult_Y_3": a,
        "b_mult_Y_minus4": b,
        "C4_X": q,
        "roots": list(roots),
        "multiplicities": list(counts),
        "power_sums_0_to_4": actual,
        "graph_spectrum_claimed": False,
    }


def structural_reduction() -> dict[str, object]:
    m4 = component_census(4)
    m6 = component_census(6)
    m4_values = set(m4["C4_values"])
    m6_values = set(m6["C4_values"])
    kappa3_values = sorted(
        {left + middle + right for left in m4_values for middle in m4_values for right in m4_values}
    )
    kappa2_66_values = sorted(
        {left + right for left in m6_values for right in m6_values}
    )
    if kappa3_values != [6, 8, 10, 12, 14, 16, 18]:
        raise AssertionError("kappa=3 C4 set changed")
    wedge_bound = wedge_four_cycle_bound()
    # For [4,8], the exhaustive m=4 component supplies 2<=q4<=6 and the
    # 24-vertex m=8 component has at most 24*C(3,2)/4=18 four-cycles.
    kappa2_48_bounds = [min(m4_values), max(m4_values) + 18]
    if kappa2_48_bounds != [2, 24]:
        raise AssertionError("kappa=2 [4,8] bounds changed")

    kappa2_graph = disjoint_union_component_controls(((6, 0), (6, 0)))
    kappa3_graph = disjoint_union_component_controls(
        ((4, 4), (4, 4), (4, 4))
    )
    kappa2_summary = graph_control_summary(kappa2_graph)
    kappa3_summary = graph_control_summary(kappa3_graph)
    if kappa2_summary["component_sizes"] != [18, 18]:
        raise AssertionError("kappa=2 control has wrong components")
    if kappa3_summary["component_sizes"] != [12, 12, 12]:
        raise AssertionError("kappa=3 control has wrong components")
    return {
        "component_censuses": {"m4": m4, "m6": m6},
        "universal_wedge_bound": wedge_bound,
        "kappa1_C4_X_bounds": [0, 27],
        "kappa2_partition_4_plus_8_C4_X_bounds": kappa2_48_bounds,
        "universal_kappa3_C4_X_values": kappa3_values,
        "kappa2_partition_6_plus_6_C4_X_values": kappa2_66_values,
        "kappa2_union_C4_X_bounds": [0, 24],
        "kappa2_local_A_X_control": kappa2_summary,
        "kappa3_local_A_X_control": kappa3_summary,
        "kappa3_aligned_scalar_control": verify_linear_spectral_control(
            18, 10, 12, (5, 6, 8, 1, 9, 2)
        ),
        "scope": (
            "component-graph and residual-scalar controls are separate; "
            "no simultaneous B or A_Y is constructed"
        ),
    }


def quotient_adjacency(
    edges: Sequence[Sequence[int]], order: int
) -> list[set[int]]:
    adjacency = [set() for _ in range(order)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    return adjacency


def quotient_half_assignments(
    quotient: Sequence[set[int]],
) -> dict[tuple[int, int], tuple[int, int]]:
    assignments = {}
    for vertex, neighbors in enumerate(quotient):
        other_fibres = sorted({neighbor // 6 for neighbor in neighbors})
        if len(other_fibres) != 2:
            raise AssertionError("bad quotient fibre incidence")
        for coefficient, fibre in enumerate(other_fibres):
            targets = sorted(
                neighbor for neighbor in neighbors if neighbor // 6 == fibre
            )
            if len(targets) != 2:
                raise AssertionError("bad quotient bidegree")
            for constant, target in enumerate(targets):
                assignments[(vertex, target)] = (constant, coefficient)
    return assignments


def quotient_triangle_patterns(
    quotient: Sequence[set[int]],
    assignments: dict[tuple[int, int], tuple[int, int]],
) -> list[list[tuple[int, int]]]:
    patterns = []
    for vertices in itertools.combinations(range(18), 3):
        left, middle, right = vertices
        if not (
            middle in quotient[left]
            and right in quotient[left]
            and right in quotient[middle]
        ):
            continue
        pattern = []
        for vertex, first, second in (
            (left, middle, right),
            (middle, left, right),
            (right, left, middle),
        ):
            first_constant, first_coefficient = assignments[(vertex, first)]
            second_constant, second_coefficient = assignments[(vertex, second)]
            if first_coefficient == second_coefficient:
                raise AssertionError("quotient triangle uses one fibre twice")
            pattern.append((vertex, first_constant ^ second_constant))
        patterns.append(pattern)
    return patterns


def lift_quotient(
    quotient: Sequence[set[int]],
    assignments: dict[tuple[int, int], tuple[int, int]],
    mask: int,
) -> list[set[int]]:
    adjacency = [set() for _ in range(36)]

    def add(left: int, right: int) -> None:
        adjacency[left].add(right)
        adjacency[right].add(left)

    for vertex in range(18):
        add(2 * vertex, 2 * vertex + 1)
    for left in range(18):
        for right in quotient[left]:
            if left >= right:
                continue
            left_constant, left_coefficient = assignments[(left, right)]
            right_constant, right_coefficient = assignments[(right, left)]
            left_endpoint = left_constant ^ (
                ((mask >> left) & 1) if left_coefficient else 0
            )
            right_endpoint = right_constant ^ (
                ((mask >> right) & 1) if right_coefficient else 0
            )
            add(2 * left + left_endpoint, 2 * right + right_endpoint)
    return adjacency


@lru_cache(maxsize=None)
def restricted_wave40_census(
    encoded_edges: tuple[tuple[int, int], ...],
) -> dict[str, object]:
    quotient = quotient_adjacency(encoded_edges, 18)
    if set(map(len, quotient)) != {4}:
        raise AssertionError("Wave 40 quotient is not 4-regular")
    assignments = quotient_half_assignments(quotient)
    patterns = quotient_triangle_patterns(quotient, assignments)
    distribution: Counter[int] = Counter()
    profiles: Counter[tuple[int, ...]] = Counter()
    accepted = 0
    for mask in range(1 << 18):
        if mask % 8192 == 0:
            require_memory()
        if any(
            all(((mask >> vertex) & 1) == value for vertex, value in pattern)
            for pattern in patterns
        ):
            continue
        adjacency = lift_quotient(quotient, assignments, mask)
        if triangle_count(adjacency):
            raise AssertionError("forbidden-pattern filter left a triangle")
        accepted += 1
        distribution[four_cycle_count(adjacency)] += 1
        profiles[component_sizes(adjacency)] += 1
        if max_nonedge_codegree(adjacency) > 2:
            raise AssertionError("restricted lift violates codegree cap")
    return {
        "restriction": (
            "one canonical rank-11 all-222 quotient from Wave 40; "
            "all 2^18 endpoint-pairing masks; not all endpoint cores"
        ),
        "raw_masks": 1 << 18,
        "triangle_free_masks": accepted,
        "component_profile_distribution": {
            "+".join(map(str, key)): value
            for key, value in sorted(profiles.items())
        },
        "C4_X_distribution": {
            str(key): distribution[key] for key in sorted(distribution)
        },
        "C4_X_range": [min(distribution), max(distribution)],
    }


def replay_wave40(wave40: dict[str, object]) -> dict[str, object]:
    if wave40["claim_label"] != "VERIFIED_SCOPED":
        raise AssertionError("Wave 40 verifier label changed")
    explicit = wave40["explicit_rank_eleven_quotient"]
    if explicit["rank_F3_2I_plus_A_Q"] != 11:
        raise AssertionError("Wave 40 explicit quotient rank changed")
    edges = tuple(tuple(edge) for edge in explicit["edges"])
    census = restricted_wave40_census(edges)
    if census["triangle_free_masks"] != 37378:
        raise AssertionError("Wave 40 triangle-free mask census changed")
    if census["component_profile_distribution"] != {"12+24": 37378}:
        raise AssertionError("Wave 40 restricted components changed")
    return {
        "source_claim_label": wave40["claim_label"],
        "normalized_rank_eleven_quotient_count": wave40[
            "normalized_quotient_enumeration"
        ]["rank_eleven_count"],
        "canonical_replay": census,
        "logical_effect": (
            "the canonical restricted all-222/r3=12 lane positively realizes "
            "kappa=2 and cannot exclude it; it supplies no universal exclusion "
            "of kappa=1 or kappa=3"
        ),
    }


def build_results() -> dict[str, object]:
    require_memory()
    wave57, wave36, wave40 = load_inputs()
    wave36_replay = replay_wave36(wave36)
    collapsed = collapse_wave57(wave57)
    structural = structural_reduction()
    wave40_replay = replay_wave40(wave40)

    # The Wave 57 controls at q=0 for kappa=1,2 are retained.  The kappa=3
    # q=3 control is incompatible with the exact component lower bound, so a
    # new exact integer-root scalar control is supplied at q=12.
    wave57_controls = {
        (
            row["a_mult_Y_3"],
            row["b_mult_Y_minus4"],
            row["C4_X"],
        ): row
        for row in wave57["scalar_algebraic_integer_controls"]
    }
    for key in ((18, 8, 0), (18, 9, 0)):
        if key not in wave57_controls:
            raise AssertionError(f"Wave 57 scalar control {key} missing")
    restricted_core = wave36["restricted_core"]
    if (
        restricted_core["components"] != 1
        or restricted_core["four_cycles"] != 0
        or restricted_core["forced_gram_rank_over_Q"] != 34
    ):
        raise AssertionError("Wave 36 kappa=1 local control changed")
    aligned_controls = {
        "kappa_1": {
            "A_X_control_source": "verified Wave 36 restricted core",
            "A_X_components": restricted_core["components"],
            "A_X_C4": restricted_core["four_cycles"],
            "forced_gram_rank": restricted_core["forced_gram_rank_over_Q"],
            "wave57_scalar_control": wave57_controls[(18, 8, 0)],
        },
        "kappa_2": {
            "A_X_control": structural["kappa2_local_A_X_control"],
            "wave57_scalar_control": wave57_controls[(18, 9, 0)],
        },
        "kappa_3": {
            "A_X_control": structural["kappa3_local_A_X_control"],
            "scalar_control": structural["kappa3_aligned_scalar_control"],
        },
        "simultaneous_B_or_A_Y_claimed": False,
    }

    return {
        "schema_version": "wave58-cross-incidence-rank-v1",
        "role": "proof_b",
        "claim_label": "DERIVED",
        "scope": (
            "conditional n3=4158 fixed-triangle cross-incidence synthesis; "
            "no simultaneous B/A_Y construction"
        ),
        "upstream_novelty_guard": {
            "rank_and_multiplicity_identities_are_new": False,
            "source": (
                "STRUCTURE.md Wave 36 one-triangle strengthening and "
                "verification/wave36-block-compatibility"
            ),
        },
        "gram_identities": gram_entry_ledger(),
        "wave36_independent_replay": wave36_replay,
        "kernel_and_rank_derivation": kernel_rank_derivation(),
        "wave57_row_collapse": collapsed,
        "component_structural_reduction": structural,
        "aligned_failure_of_obstruction_controls": aligned_controls,
        "wave40_restricted_lift_replay": wave40_replay,
        "result": {
            "wave57_rows_before": 18,
            "wave57_rows_after": 3,
            "surviving_a_b_kappa": [
                [18, 8, 1],
                [18, 9, 2],
                [18, 10, 3],
            ],
            "kappa3_C4_X_reduction": [6, 8, 10, 12, 14, 16, 18],
            "universal_C4_X_upper_bound": 27,
            "component_specific_C4_X": {
                "kappa_1": "0..27",
                "kappa_2": (
                    "bounds 0<=C4_X<=24 overall; [6,6] exact values "
                    "{0,1,...,16,18}; [4,8] bounded 2..24"
                ),
                "kappa_3": "{6,8,10,12,14,16,18}",
            },
            "kappa2_excluded": False,
            "kappa3_excluded": False,
            "contradiction": False,
            "endpoint": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
        "limitations": [
            "The rank, component, and Y-multiplicity formulas are prior verified Wave 36 results, not Wave 58 novelty.",
            "The m=4 and m=6 component censuses normalize only by coordinate relabeling, not graph automorphisms.",
            "The Wave 40 replay is restricted to one canonical rank-11 all-222 quotient.",
            "The local A_X and scalar residual-spectrum controls are separate and do not construct B or A_Y.",
            "No component/lift ledger exhausts all endpoint cores or proves nonexistence.",
        ],
        "resource_guard": {
            "minimum_free_physical_memory_percent": MIN_FREE_PERCENT,
            "enforced_during_censuses": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = canonical_bytes(build_results())
    if arguments.output is not None:
        arguments.output.write_bytes(payload)
        print(
            f"PASS_DERIVED sha256={hashlib.sha256(payload).hexdigest()} "
            f"path={arguments.output}"
        )
        return 0
    if arguments.verify is not None:
        if arguments.verify.read_bytes() != payload:
            print("FAIL_EXACT_REPLAY", file=sys.stderr)
            return 1
        print(
            "PASS_EXACT_REPLAY "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
        return 0
    sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
