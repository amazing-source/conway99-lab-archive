#!/usr/bin/env python3
"""Exact outside-incidence checks for the Wave74 short-vector closure."""

from __future__ import annotations

import argparse
import json
import os
from math import comb
from pathlib import Path


V = 99
K = 14
LAMBDA = 1
MU = 2


def free_memory_percent() -> float:
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


def internal_opposite_pair_incidences(
    side_size: int, same_edges: int, edge_shape: str
) -> int:
    """Count pair incidences through the opposite support side.

    A support vertex with same-side degree d has opposite-side degree 4+d.
    """
    if same_edges == 0:
        degrees = [0] * side_size
    elif same_edges == 1:
        degrees = [1, 1] + [0] * (side_size - 2)
    elif same_edges == 2 and edge_shape == "disjoint":
        degrees = [1, 1, 1, 1] + [0] * (side_size - 4)
    elif same_edges == 2 and edge_shape == "adjacent":
        degrees = [2, 1, 1] + [0] * (side_size - 3)
    else:
        raise ValueError("unsupported same-edge shape")
    return sum(comb(4 + degree, 2) for degree in degrees)


def side_pair_capacity(side_size: int, same_edges: int) -> int:
    """Total SRG common-neighbor capacity over unordered same-side pairs."""
    return (
        same_edges * LAMBDA
        + (comb(side_size, 2) - same_edges) * MU
    )


def lane_parameters(
    side_size: int, same_edges: int, edge_shape: str = "none"
) -> dict[str, int | str | bool]:
    outside_vertices = V - 2 * side_size
    cross_edges = 4 * side_size + 2 * same_edges
    support_degree_incidences_per_side = 2 * same_edges + cross_edges
    outside_incidences_per_side = (
        K * side_size - support_degree_incidences_per_side
    )
    inside_pair_incidences = internal_opposite_pair_incidences(
        side_size, same_edges, edge_shape
    )
    capacity = side_pair_capacity(side_size, same_edges)
    outside_pair_incidences = capacity - inside_pair_incidences
    return {
        "side_size": side_size,
        "same_edges_per_side": same_edges,
        "same_edge_shape": edge_shape,
        "outside_vertices": outside_vertices,
        "cross_edges": cross_edges,
        "support_degree_incidences_per_side": support_degree_incidences_per_side,
        "outside_incidences_per_side": outside_incidences_per_side,
        "inside_pair_incidences_through_opposite_side": inside_pair_incidences,
        "same_side_pair_capacity": capacity,
        "outside_pair_incidences": outside_pair_incidences,
        "outside_induced_edges": (
            K * outside_vertices - 2 * outside_incidences_per_side
        )
        // 2,
        "pair_capacity_already_exceeded": inside_pair_incidences > capacity,
    }


def enumerate_histograms(
    vertices: int, incidence_sum: int, pair_sum: int, maximum_d: int = 7
) -> list[list[int]]:
    """Enumerate n_d with sum n_d=vertices and two exact moments."""
    output: list[list[int]] = []

    def visit(
        d: int,
        remaining_vertices: int,
        remaining_incidence: int,
        remaining_pairs: int,
        prefix: list[int],
    ) -> None:
        if d > maximum_d:
            if (
                remaining_vertices == 0
                and remaining_incidence == 0
                and remaining_pairs == 0
            ):
                output.append(prefix)
            return
        pair_weight = comb(d, 2)
        upper = remaining_vertices
        if d:
            upper = min(upper, remaining_incidence // d)
        if pair_weight:
            upper = min(upper, remaining_pairs // pair_weight)
        for count in range(upper + 1):
            visit(
                d + 1,
                remaining_vertices - count,
                remaining_incidence - d * count,
                remaining_pairs - pair_weight * count,
                prefix + [count],
            )

    visit(0, vertices, incidence_sum, pair_sum, [])
    return output


def checked_lane(
    name: str, side_size: int, same_edges: int, edge_shape: str
) -> dict[str, object]:
    parameters = lane_parameters(side_size, same_edges, edge_shape)
    if parameters["pair_capacity_already_exceeded"]:
        histograms: list[list[int]] = []
    else:
        histograms = enumerate_histograms(
            int(parameters["outside_vertices"]),
            int(parameters["outside_incidences_per_side"]),
            int(parameters["outside_pair_incidences"]),
        )
    return {
        "name": name,
        **parameters,
        "histogram_convention": "[n0,n1,...,n7], where d hits each sign side",
        "histogram_count": len(histograms),
        "histograms": histograms,
    }


def build_results() -> dict[str, object]:
    norm16_h0 = checked_lane("norm16_h0", 8, 0, "none")
    norm18_h0 = checked_lane("norm18_h0", 9, 0, "none")
    norm18_h1 = checked_lane("norm18_h1", 9, 1, "single")
    norm18_h2_adjacent = checked_lane("norm18_h2_adjacent", 9, 2, "adjacent")
    norm18_h2_disjoint = checked_lane("norm18_h2_disjoint", 9, 2, "disjoint")

    assert norm18_h2_adjacent["pair_capacity_already_exceeded"]
    assert int(norm18_h2_adjacent["inside_pair_incidences_through_opposite_side"]) == 71
    assert int(norm18_h2_adjacent["same_side_pair_capacity"]) == 70

    # In the disjoint h=2 lane the pair budget is zero, so every outside
    # incidence number d is at most one.  But 82 incidences cannot fit into
    # 81 outside vertices.
    assert norm18_h2_disjoint["outside_pair_incidences"] == 0
    assert norm18_h2_disjoint["outside_vertices"] == 81
    assert norm18_h2_disjoint["outside_incidences_per_side"] == 82
    assert norm18_h2_disjoint["histogram_count"] == 0

    assert norm16_h0["histogram_count"] == 4
    assert norm18_h0["histogram_count"] == 20
    assert norm18_h1["histogram_count"] == 6

    return {
        "format": "wave74-short-vector-closure-v1",
        "claim_label": "DERIVED",
        "scope": (
            "conditional outside-incidence consequences for Wave71's "
            "signed norm-16 and norm-18 integer -4 eigenvectors"
        ),
        "lanes": {
            lane["name"]: lane
            for lane in (
                norm16_h0,
                norm18_h0,
                norm18_h1,
                norm18_h2_adjacent,
                norm18_h2_disjoint,
            )
        },
        "norm18_closure": {
            "h2_adjacent_already_excluded_by_wave71": True,
            "h2_disjoint_excluded_by_outside_pigeonhole": True,
            "surviving_h": [0, 1],
            "pigeonhole_certificate": {
                "outside_vertices": 81,
                "required_side_incidences": 82,
                "outside_pair_incidence_sum": 0,
                "consequence": "every d_x<=1, so sum d_x<=81<82",
            },
        },
        "remaining_exact_boundary": {
            "norm16_h0_histograms": 4,
            "norm18_h0_histograms": 20,
            "norm18_h1_histograms": 6,
            "further_contradiction_found": False,
        },
        "endpoint": {
            "wave71_q16_count_congruence_retained": (
                "N14+N16+N18=2 mod 14"
            ),
            "all_short_vector_alternatives_excluded": False,
            "conway_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Wave74 is conditional on Wave71 and does not validate it.",
            "Moment histograms are necessary incidence conditions, not constructions.",
            "Norm14, norm16, and norm18 h=0,1 alternatives remain.",
            "No automorphism or transitivity is assumed.",
        ],
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run with only {free:.1f}% free physical memory")
    encoded = canonical_bytes(build_results())
    canonical = Path(__file__).with_name("exact-results.json")
    if args.output:
        args.output.write_bytes(encoded)
    elif args.verify:
        if canonical.read_bytes() != encoded:
            raise SystemExit("exact-results.json is stale")
        print("PASS: Wave74 canonical artifact matches exact recomputation")
    else:
        print(encoded.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
