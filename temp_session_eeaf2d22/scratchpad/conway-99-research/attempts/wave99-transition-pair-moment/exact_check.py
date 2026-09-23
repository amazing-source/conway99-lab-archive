"""Exact checks for the Wave 99 transition-pair moment bound.

Discovery only. The mathematical scope and imports are frozen in protocol.md.
"""

from __future__ import annotations

import argparse
import json
import os
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path


Q = Fraction
DEFAULT_OUTPUT = Path(__file__).with_name("exact-results.json")


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


def mate(vertex: int) -> int:
    return vertex ^ 1


def seeds() -> list[tuple[int, ...]]:
    result = []
    for groups in combinations(range(7), 4):
        for bits in product((0, 1), repeat=4):
            result.append(tuple(2 * group + bit for group, bit in zip(groups, bits)))
    return result


def perfect_matchings(center: int) -> list[tuple[tuple[int, int], ...]]:
    vertices = tuple(v for v in range(14) if v not in (center, mate(center)))
    result: list[tuple[tuple[int, int], ...]] = []

    def visit(remaining: tuple[int, ...], edges: list[tuple[int, int]]) -> None:
        if not remaining:
            result.append(tuple(edges))
            return
        first = remaining[0]
        for index in range(1, len(remaining)):
            second = remaining[index]
            if second == mate(first):
                continue
            rest = remaining[1:index] + remaining[index + 1 :]
            visit(rest, edges + [(first, second)])

    visit(vertices, [])
    return result


def edge_set(matching: tuple[tuple[int, int], ...]) -> set[frozenset[int]]:
    return {frozenset(edge) for edge in matching}


def extension_contribution(
    matching: tuple[tuple[int, int], ...],
    fixed_other_points: tuple[int, int],
    extension_points: tuple[int, ...],
) -> int:
    edges = edge_set(matching)
    count = 0
    for extension in extension_points:
        triple = (*fixed_other_points, extension)
        if any(frozenset(pair) in edges for pair in combinations(triple, 2)):
            count += 1
    return count


def exact_result() -> dict:
    all_seeds = seeds()
    assert len(all_seeds) == 560 and len(set(all_seeds)) == 560

    # Canonical selected transition centered at s=0 with other points a=2,b=4.
    # Its eight seed extensions use one endpoint from one of four unused groups.
    s, a, b = 0, 2, 4
    extensions = tuple(v for v in range(6, 14))
    containing = [
        seed for seed in all_seeds if {s, a, b}.issubset(seed)
    ]
    assert len(containing) == 8
    assert {next(iter(set(seed) - {s, a, b})) for seed in containing} == set(
        extensions
    )

    matchings_a = perfect_matchings(a)
    matchings_b = perfect_matchings(b)
    assert len(matchings_a) == len(matchings_b) == 6040

    def contribution_profile(matchings, fixed_pair, identical_pair):
        with_identical = []
        without_identical = []
        for matching in matchings:
            contribution = extension_contribution(
                matching, fixed_pair, extensions
            )
            bucket = (
                with_identical
                if frozenset(identical_pair) in edge_set(matching)
                else without_identical
            )
            bucket.append(contribution)
        return {
            "with_identical_count": len(with_identical),
            "without_identical_count": len(without_identical),
            "with_identical_values": sorted(set(with_identical)),
            "without_identical_values": sorted(set(without_identical)),
            "with_identical_max": max(with_identical),
            "without_identical_max": max(without_identical),
        }

    profile_a = contribution_profile(matchings_a, (s, b), (s, b))
    profile_b = contribution_profile(matchings_b, (s, a), (s, a))
    assert profile_a["with_identical_values"] == [8]
    assert profile_b["with_identical_values"] == [8]
    assert profile_a["without_identical_max"] == 2
    assert profile_b["without_identical_max"] == 2

    # The two identical-triple choices cannot coexist with the fixed transition:
    # the three residual labels would form a triangle, giving an edge two common
    # neighbors and violating lambda=1.
    other_original_centers_max = max(8 + 2, 2 + 8, 2 + 2)
    extension_centers_max = len(extensions)
    co_incidence_per_transition_max = (
        other_original_centers_max + extension_centers_max
    )
    assert co_incidence_per_transition_max == 18

    selected_transitions = 84
    first_moment = selected_transitions * 8
    pair_moment_upper = selected_transitions * co_incidence_per_transition_max // 2
    assert first_moment == 672
    assert pair_moment_upper == 756

    # For j=1,2,3,4, the pointwise certificate is
    #   1 >= j/2 - C(j,2)/6.
    pointwise = {
        j: Q(1) - Q(j, 2) + Q(j * (j - 1) // 2, 6)
        for j in range(1, 5)
    }
    assert all(value >= 0 for value in pointwise.values())
    bad_seed_lower = Q(first_moment, 2) - Q(pair_moment_upper, 6)
    assert bad_seed_lower == 210
    valid_seed_upper = len(all_seeds) - int(bad_seed_lower)
    assert valid_seed_upper == 350

    n14_upper = 99 * valid_seed_upper // 7
    assert 99 * valid_seed_upper % 7 == 0
    assert n14_upper == 4950

    modular_numerator = 1_997_236
    modular_denominator = 341
    residual_numerator = modular_numerator - n14_upper * modular_denominator
    assert residual_numerator == 309_286
    weighted_rhs = 7 * residual_numerator
    assert weighted_rhs == 2_165_002

    return {
        "format": "wave99-transition-pair-moment-v1",
        "claim_label": "DERIVED",
        "scope": {
            "target": "hypothetical srg(99,14,1,2)",
            "requires_prism_free_endpoint": True,
            "requires_n3": 4158,
            "rank_28_used_for_n14_bound": False,
            "rank_28_used_for_weighted_corollary": True,
            "n14_counts_both_signs": True,
        },
        "canonical_local_check": {
            "seed_count": len(all_seeds),
            "seed_extensions_per_transition": len(containing),
            "local_perfect_matchings": len(matchings_a),
            "center_a_profile": profile_a,
            "center_b_profile": profile_b,
            "lambda_one_forbids_both_identical_triple_transitions": True,
            "co_incidence_per_transition_max": co_incidence_per_transition_max,
        },
        "moments": {
            "first_transition_seed_moment": first_moment,
            "pair_transition_seed_moment_upper": pair_moment_upper,
            "pointwise_certificate_slacks": {
                str(j): str(value) for j, value in pointwise.items()
            },
            "bad_seed_lower": int(bad_seed_lower),
            "valid_seed_upper": valid_seed_upper,
        },
        "bounds": {
            "N14_upper": n14_upper,
            "prior_verified_N14_upper": 5544,
            "improvement": 5544 - n14_upper,
            "rank28_weighted_shell_inequality": "407*N16+43*N18>=2165002",
            "if_N18_zero_even_N16_lower": 5320,
            "if_N16_zero_even_N18_lower": 50350,
        },
        "status": {
            "N16_or_N18_upper_bound": "NOT_PROVED",
            "prism_free_rank28_excluded": False,
            "strict_n3_upper_bound": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Discovery cannot certify itself; independent verification is required.",
            "The N14 theorem assumes the prism-free endpoint.",
            "The weighted corollary additionally assumes q=16/r=28.",
            "No upper bound on N16 or N18 is proved.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if free_memory_percent() < 20:
        raise SystemExit("refusing to run below 20% free physical memory")
    result = exact_result()
    if args.verify:
        archived = json.loads(args.verify.read_text(encoding="utf-8"))
        if archived != result:
            raise SystemExit("archived result mismatch")
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if not args.verify:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")


if __name__ == "__main__":
    main()
