#!/usr/bin/env python3
"""Exact discovery checks for the Wave 102 prism-incidence code route."""

from __future__ import annotations

import argparse
from collections import Counter
import ctypes
import hashlib
from itertools import combinations, permutations
import json
import os
from pathlib import Path
from typing import Any, Iterable


V = 99
K = 14
LAMBDA = 1
MU = 2
TRIANGLES = V * K // 6
OUTPUT = Path(__file__).with_name("exact-results.json")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0

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


def edge(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left < right else (right, left)


def canonical_prism_edges() -> frozenset[tuple[int, int]]:
    triangles = ((0, 1, 2), (3, 4, 5))
    edges = {
        edge(left, right)
        for triangle in triangles
        for left, right in combinations(triangle, 2)
    }
    edges.update({edge(0, 3), edge(1, 4), edge(2, 5)})
    return frozenset(edges)


PRISM_EDGES = canonical_prism_edges()


def labeled_prisms(
    vertices: tuple[int, ...],
) -> tuple[frozenset[tuple[int, int]], ...]:
    require(len(vertices) == 6, "a prism needs six vertices")
    rows = {
        frozenset(edge(mapping[left], mapping[right]) for left, right in PRISM_EDGES)
        for mapping in permutations(vertices)
    }
    require(len(rows) == 60, "labelled prism count changed")
    return tuple(sorted(rows, key=lambda row: sorted(row)))


def common_neighbor_count(
    edges: frozenset[tuple[int, int]] | set[tuple[int, int]],
    left: int,
    right: int,
    order: int,
) -> int:
    return sum(
        edge(left, point) in edges and edge(right, point) in edges
        for point in range(order)
        if point not in {left, right}
    )


def satisfies_srg_common_neighbor_caps(
    edges: frozenset[tuple[int, int]] | set[tuple[int, int]],
    order: int,
) -> bool:
    return all(
        common_neighbor_count(edges, left, right, order)
        <= (LAMBDA if edge(left, right) in edges else MU)
        for left, right in combinations(range(order), 2)
    )


def prism_overlap_gluings(overlap: int) -> list[frozenset[tuple[int, int]]]:
    """Glue two prisms on `overlap` vertices and retain SRG-cap-compatible rows."""

    require(0 <= overlap <= 5, "distinct supports have overlap at most five")
    rows = []
    for first_shared in combinations(range(6), overlap):
        for second_shared in combinations(range(6), overlap):
            for image in permutations(second_shared):
                mapping = dict(zip(first_shared, image))
                if any(
                    (edge(left, right) in PRISM_EDGES)
                    != (edge(mapping[left], mapping[right]) in PRISM_EDGES)
                    for left, right in combinations(first_shared, 2)
                ):
                    continue

                common_ids = {
                    source: index
                    for index, source in enumerate(first_shared)
                }
                next_id = overlap
                first_ids = dict(common_ids)
                for source in range(6):
                    if source not in first_ids:
                        first_ids[source] = next_id
                        next_id += 1
                inverse = {
                    second: first for first, second in mapping.items()
                }
                second_ids = {
                    source: common_ids[inverse[source]]
                    for source in second_shared
                }
                for source in range(6):
                    if source not in second_ids:
                        second_ids[source] = next_id
                        next_id += 1

                union_edges = {
                    edge(first_ids[left], first_ids[right])
                    for left, right in PRISM_EDGES
                }
                union_edges.update(
                    edge(second_ids[left], second_ids[right])
                    for left, right in PRISM_EDGES
                )
                frozen = frozenset(union_edges)
                if satisfies_srg_common_neighbor_caps(frozen, next_id):
                    rows.append(frozen)
    return rows


def overlap_certificate() -> dict[str, Any]:
    overlap_five = prism_overlap_gluings(5)
    overlap_four = prism_overlap_gluings(4)
    require(not overlap_five, "two prisms can share five vertices")
    require(overlap_four, "four-vertex overlap control disappeared")

    # A prism minus one vertex has degree multiset 2,2,2,3,3.  Restoring
    # the prism uniquely attaches the missing vertex to the three
    # degree-two vertices. Two distinct restorations would therefore share
    # three common neighbors, violating both lambda=1 and mu=2.
    deletion_profiles = []
    for deleted in range(6):
        remaining = [point for point in range(6) if point != deleted]
        degrees = {
            point: sum(edge(point, other) in PRISM_EDGES for other in remaining)
            for point in remaining
        }
        repair_neighbors = sorted(
            point for point, degree in degrees.items() if degree == 2
        )
        require(
            sorted(degrees.values()) == [2, 2, 2, 3, 3],
            "deleted-prism profile changed",
        )
        require(
            repair_neighbors
            == sorted(
                point
                for point in remaining
                if edge(point, deleted) in PRISM_EDGES
            ),
            "repair neighborhood is not unique",
        )
        deletion_profiles.append(
            {
                "deleted": deleted,
                "degree_multiset": sorted(degrees.values()),
                "repair_neighbors": repair_neighbors,
            }
        )
    return {
        "maximum_intersection_of_distinct_prism_supports": 4,
        "overlap_five_cap_compatible_gluings": len(overlap_five),
        "overlap_four_cap_compatible_gluings": len(overlap_four),
        "five_vertex_deletion_profiles": deletion_profiles,
        "proof": (
            "five shared vertices force the two missing vertices to have "
            "the same three neighbors, contradicting lambda=1 if adjacent "
            "and mu=2 if nonadjacent"
        ),
    }


def induced_prism_supports(
    vertices: tuple[int, ...],
    edges: frozenset[tuple[int, int]] | set[tuple[int, int]],
) -> tuple[frozenset[int], ...]:
    rows = []
    for support_tuple in combinations(vertices, 6):
        support = frozenset(support_tuple)
        triangles = [
            frozenset(triangle)
            for triangle in combinations(support_tuple, 3)
            if all(edge(left, right) in edges for left, right in combinations(triangle, 2))
        ]
        found = False
        for first in triangles:
            second = support - first
            if len(second) != 3 or not all(
                edge(left, right) in edges
                for left, right in combinations(sorted(second), 2)
            ):
                continue
            cross = [
                edge(left, right)
                for left in first
                for right in second
                if edge(left, right) in edges
            ]
            if len(cross) == 3 and all(
                sum(point in cross_edge for cross_edge in cross) == 1
                for point in support
            ):
                found = True
                break
        if found:
            rows.append(support)
    return tuple(rows)


def canonical_rook_edges() -> frozenset[tuple[int, int]]:
    rows = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    edges = {
        edge(left, right)
        for row in rows
        for left, right in combinations(row, 2)
    }
    edges.update(
        edge(first[index], second[index])
        for first, second in combinations(rows, 2)
        for index in range(3)
    )
    return frozenset(edges)


ROOK_EDGES = canonical_rook_edges()


def block_preserving_rook_isomorphism(
    candidate: frozenset[tuple[int, int]],
) -> bool:
    blocks = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    for first in permutations(blocks[0]):
        for second in permutations(blocks[1]):
            for third in permutations(blocks[2]):
                mapping = dict(
                    zip(
                        blocks[0] + blocks[1] + blocks[2],
                        first + second + third,
                    )
                )
                image = {
                    edge(mapping[left], mapping[right])
                    for left, right in candidate
                }
                if image == set(ROOK_EDGES):
                    return True
    return False


def three_prism_even_motif_certificate() -> dict[str, Any]:
    blocks = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    pair_rows = {
        (0, 1): labeled_prisms(blocks[0] + blocks[1]),
        (0, 2): labeled_prisms(blocks[0] + blocks[2]),
        (1, 2): labeled_prisms(blocks[1] + blocks[2]),
    }
    feasible = set()
    for first in pair_rows[(0, 1)]:
        first_a = frozenset(
            row for row in first if set(row) <= set(blocks[0])
        )
        first_b = frozenset(
            row for row in first if set(row) <= set(blocks[1])
        )
        for second in pair_rows[(0, 2)]:
            second_a = frozenset(
                row for row in second if set(row) <= set(blocks[0])
            )
            if second_a != first_a:
                continue
            second_c = frozenset(
                row for row in second if set(row) <= set(blocks[2])
            )
            for third in pair_rows[(1, 2)]:
                third_b = frozenset(
                    row for row in third if set(row) <= set(blocks[1])
                )
                third_c = frozenset(
                    row for row in third if set(row) <= set(blocks[2])
                )
                if third_b != first_b or third_c != second_c:
                    continue
                union = frozenset(set(first) | set(second) | set(third))
                if satisfies_srg_common_neighbor_caps(union, 9):
                    feasible.add(union)

    require(len(feasible) == 36, "three-prism motif census changed")
    require(
        all(block_preserving_rook_isomorphism(row) for row in feasible),
        "a feasible three-prism parity motif is not the rook graph",
    )
    prism_counts = {
        len(induced_prism_supports(tuple(range(9)), row))
        for row in feasible
    }
    require(prism_counts == {6}, "rook motif does not force six prisms")

    degrees = [
        sum(edge(point, other) in ROOK_EDGES for other in range(9) if other != point)
        for point in range(9)
    ]
    require(degrees == [4] * 9, "rook degrees changed")
    require(
        all(
            common_neighbor_count(ROOK_EDGES, left, right, 9)
            == (LAMBDA if edge(left, right) in ROOK_EDGES else MU)
            for left, right in combinations(range(9), 2)
        ),
        "rook graph does not saturate target common-neighbor counts",
    )
    boundary_edges = 9 * (K - 4)
    outside_vertices = V - 9
    require(boundary_edges == outside_vertices == 90, "rook boundary changed")
    return {
        "three_even_support_set_partition": (
            "three six-sets with zero symmetric difference partition their "
            "nine vertices into three size-three pairwise-intersection blocks"
        ),
        "labelled_cap_compatible_unions": len(feasible),
        "all_unions_isomorphic_to_rook_3_by_3": True,
        "induced_prisms_forced_inside_union": sorted(prism_counts),
        "consequence_for_total_P_3": (
            "f mod 2 cannot vanish when the whole graph has exactly three "
            "prisms, because the parity-cancelling union already contains six"
        ),
        "rook_boundary_edges": boundary_edges,
        "vertices_outside_rook": outside_vertices,
        "forced_outside_neighbors_per_vertex": 1,
        "equitable_quotient": [[4, 10], [1, 13]],
        "quotient_eigenvalues": [14, 3],
        "interpretation": (
            "the rook motif is locally and spectrally parameter-compatible; "
            "it is not a full 99-vertex graph construction"
        ),
    }


def cycle4_k3_edges() -> frozenset[tuple[int, int]]:
    edges = set()
    for layer in range(4):
        block = tuple(3 * layer + index for index in range(3))
        edges.update(edge(left, right) for left, right in combinations(block, 2))
        next_layer = (layer + 1) % 4
        edges.update(
            edge(3 * layer + index, 3 * next_layer + index)
            for index in range(3)
        )
    return frozenset(edges)


def cycle4_cancellation_certificate() -> dict[str, Any]:
    edges = cycle4_k3_edges()
    vertices = tuple(range(12))
    prisms = induced_prism_supports(vertices, edges)
    incidence = Counter(point for support in prisms for point in support)
    adjacent_max = max(
        common_neighbor_count(edges, left, right, 12)
        for left, right in combinations(vertices, 2)
        if edge(left, right) in edges
    )
    nonadjacent_max = max(
        common_neighbor_count(edges, left, right, 12)
        for left, right in combinations(vertices, 2)
        if edge(left, right) not in edges
    )
    require(len(prisms) == 4, "C4 box K3 prism count changed")
    require(set(incidence.values()) == {2}, "C4 box K3 parity did not cancel")
    require(
        (adjacent_max, nonadjacent_max) == (1, 2),
        "C4 box K3 violates target common-neighbor caps",
    )
    return {
        "motif": "Cartesian product C4 box K3",
        "vertices": len(vertices),
        "edges": len(edges),
        "induced_prisms": len(prisms),
        "prisms_through_each_motif_vertex": sorted(set(incidence.values())),
        "rooted_parity_vector_on_motif": "zero",
        "maximum_internal_common_neighbors_adjacent": adjacent_max,
        "maximum_internal_common_neighbors_nonadjacent": nonadjacent_max,
        "spectrum_with_multiplicities": {
            "-3": 2,
            "-1": 4,
            "0": 1,
            "1": 2,
            "2": 2,
            "4": 1,
        },
        "interlaces_target_interval_minus4_to14": True,
        "interpretation": (
            "four prisms can cancel every rooted parity using a motif that "
            "passes all induced lambda/mu upper-cap and interlacing controls; "
            "extendibility to 99 vertices remains unknown"
        ),
    }


def binary_code_certificate() -> dict[str, Any]:
    # The SRG spectrum is 14^1, 3^54, (-4)^44.
    spectrum = {14: 1, 3: 54, -4: 44}
    require(sum(spectrum.values()) == V, "spectrum multiplicities changed")
    require(
        sum(value * multiplicity for value, multiplicity in spectrum.items())
        == 0,
        "spectrum trace changed",
    )
    require(
        sum(value * value * multiplicity for value, multiplicity in spectrum.items())
        == V * K,
        "spectrum square trace changed",
    )

    # Modulo two, A^2=A and the characteristic polynomial is
    # x^45(x+1)^54. Idempotence makes A diagonalizable over F2.
    rank_A_mod2 = 54
    rank_I_plus_A_mod2 = V - rank_A_mod2
    rank_B_min = rank_I_plus_A_mod2
    rank_B_max = V
    even_triangle_code_dimension_range = [
        rank_B_min - 1,
        rank_B_max - 1,
    ]
    require(rank_I_plus_A_mod2 == 45, "binary adjacency rank changed")
    require(
        even_triangle_code_dimension_range == [44, 98],
        "even triangle-code range changed",
    )

    # If B^T x=0 and S=supp(x), every graph triangle meets S evenly.
    # Each v in S therefore has exactly one other S vertex in each of its
    # seven incident triangles, so G[S] is 7-regular.  Apply the two
    # restricted eigenvalue bounds to chi_S^T A chi_S=7|S|.
    triangle_even_support_min = 36
    triangle_even_support_max = 60
    feasible_even_weights = [
        size
        for size in range(2, V, 2)
        if 99 * 7 * size <= 99 * 3 * size + 11 * size * size
        and 99 * 7 * size >= 18 * size * size - 99 * 4 * size
    ]
    require(
        feasible_even_weights == list(range(36, 61, 2)),
        "triangle-even spectral support range changed",
    )
    return {
        "triangle_count": TRIANGLES,
        "integer_adjacency_identity": "A^2=12I-A+2J",
        "binary_adjacency_identity": "A^2=A",
        "binary_characteristic_polynomial": "x^45*(x+1)^54",
        "rank_F2_A": rank_A_mod2,
        "rank_F2_I_plus_A": rank_I_plus_A_mod2,
        "triangle_incidence_identity": "B*B^T=I+A over F2",
        "rank_F2_B_range": [rank_B_min, rank_B_max],
        "even_triangle_code": (
            "C0={Bz : z in F2^231 and wt(z) even}"
        ),
        "dimension_C0_range": even_triangle_code_dimension_range,
        "dual_characterization": (
            "C0^perp={x : B^T*x is constant on all 231 triangles}"
        ),
        "triangle_even_check_support": {
            "condition": "B^T*x=0",
            "induced_degree_on_support": 7,
            "nonzero_weight_range": [
                triangle_even_support_min,
                triangle_even_support_max,
            ],
            "proof": (
                "restricted eigenvalue bounds applied to "
                "chi_S^T*A*chi_S=7*|S|, plus even |S|"
            ),
        },
        "dual_minimum_distance_lower_bound": 36,
        "dual_locality_boundary": (
            "apart from zero, every universal parity check on f uses at "
            "least 36 vertices; the all-ones total-parity check has weight 99"
        ),
        "prism_factorization": (
            "H=B*D, where D is the triangle-versus-prism edge-incidence "
            "matrix and H is vertex-versus-prism incidence"
        ),
        "parity_vector": "f mod 2 = H*1 = B*(D*1) lies in C0",
        "cycle_space_boundary": (
            "D*1 is the odd-degree boundary of the selected edge set in "
            "the graph whose vertices are triangles and whose edges are prisms"
        ),
        "universal_congruences": [
            "wt(f mod 2) is even",
            "x dot f = 0 mod 2 whenever every graph triangle has the same x-sum",
        ],
        "boundary": (
            "C0 has at least 44 binary dimensions; these universal code "
            "relations alone do not force f mod 2 to be nonzero"
        ),
    }


def single_prism_external_profile() -> dict[str, int]:
    internal_common = {
        pair: common_neighbor_count(PRISM_EDGES, pair[0], pair[1], 6)
        for pair in combinations(range(6), 2)
    }
    external_pair_deficit = sum(
        (LAMBDA if edge(left, right) in PRISM_EDGES else MU)
        - internal_common[(left, right)]
        for left, right in combinations(range(6), 2)
    )
    # An outside vertex cannot meet three prism vertices: among three
    # vertices, two lie in the same base triangle, and that adjacent pair
    # already has its unique common neighbor inside the triangle.
    two_neighbors = external_pair_deficit
    boundary_edges = 6 * (K - 3)
    one_neighbor = boundary_edges - 2 * two_neighbors
    zero_neighbors = (V - 6) - one_neighbor - two_neighbors
    require(
        (zero_neighbors, one_neighbor, two_neighbors) == (30, 60, 3),
        "single-prism external profile changed",
    )
    return {
        "zero_neighbors": zero_neighbors,
        "one_neighbor": one_neighbor,
        "two_neighbors": two_neighbors,
    }


def adjacency_polynomial_boundary() -> dict[str, Any]:
    # The adjacency algebra of an SRG is span{I,A,J}; every ordinary
    # polynomial in A therefore has constant diagonal.
    return {
        "adjacency_algebra": "span_Q{I,A,J}",
        "ordinary_polynomial_diagonal": "constant on all 99 vertices",
        "consequence": (
            "a nonconstant rooted prism vector cannot be recovered as "
            "diag(p(A)); ordinary adjacency-polynomial identities see only "
            "walk-regular scalar data"
        ),
        "needed_extension": (
            "Hadamard products or explicit triangle/prism incidence tensors"
        ),
        "single_prism_external_neighbor_profile": (
            single_prism_external_profile()
        ),
        "single_prism_binary_identity": (
            "(I+A)*chi_S is the indicator of the 60 outside vertices "
            "having exactly one neighbor in the prism"
        ),
    }


def refined_n14_bound(n3: int, odd_roots: int) -> dict[str, int]:
    require(0 <= n3 <= 4158 and (4158 - n3) % 3 == 0, "incompatible n3")
    require(0 <= odd_roots <= 98 and odd_roots % 2 == 0, "invalid odd-root count")
    prisms = (4158 - n3) // 3
    scalar_numerator = 55440 - 5 * n3
    refined_numerator = scalar_numerator - odd_roots // 2
    even_upper = 2 * (refined_numerator // 14)
    return {
        "n3": n3,
        "P": prisms,
        "O": odd_roots,
        "seven_N14_scalar_numerator": scalar_numerator,
        "seven_N14_refined_numerator": refined_numerator,
        "N14_even_upper": even_upper,
    }


def vector_refined_bound_certificate() -> dict[str, Any]:
    p0 = refined_n14_bound(4158, 0)
    p1 = refined_n14_bound(4155, 6)
    p2 = refined_n14_bound(4152, 4)
    p3_minimal_nonzero = refined_n14_bound(4149, 2)
    require(p0["N14_even_upper"] == 4950, "P=0 row changed")
    require(p1["N14_even_upper"] == 4950, "P=1 improvement changed")
    require(p2["N14_even_upper"] == 4954, "P=2 row changed")
    return {
        "odd_root_definition": "O=#{v : f_v is odd}=wt(f mod 2)",
        "exact_floor_sum_identity": (
            "sum_v floor(5*f_v/2)=15P-O/2"
        ),
        "refined_incidence_inequality": (
            "7*N14<=34650+15P-O/2=55440-5*n3-O/2"
        ),
        "antipodal_form": (
            "N14<=2*floor((55440-5*n3-O/2)/14)"
        ),
        "low_prism_rows": {
            "P=0": p0,
            "P=1_exact_O=6": p1,
            "P=2_O_at_least_4": p2,
            "P=3_O_nonzero_but_only_2_used": p3_minimal_nonzero,
        },
        "strict_improvement": (
            "If P=1 (n3=4155), N14<=4950 instead of the Wave100 "
            "scalar bound 4952."
        ),
        "limitations": (
            "The P=2 overlap theorem sharpens the seven-N14 numerator but "
            "not its final even bound. For P>=4, local parity cancellation "
            "is parameter-compatible."
        ),
    }


def exact_result() -> dict[str, Any]:
    code = binary_code_certificate()
    overlap = overlap_certificate()
    three = three_prism_even_motif_certificate()
    four = cycle4_cancellation_certificate()
    refined = vector_refined_bound_certificate()
    adjacency = adjacency_polynomial_boundary()
    return {
        "format": "wave102-prism-incidence-code-v1",
        "role": "proof_b",
        "claim_label": "DERIVED",
        "scope": "hypothetical srg(99,14,1,2)",
        "theorems": {
            "binary_incidence_code": code,
            "vector_refined_N14_bound": refined,
            "distinct_prism_overlap": overlap,
            "three_prism_parity_branch": three,
        },
        "controls_and_boundaries": {
            "four_prism_parity_cancellation": four,
            "ordinary_adjacency_polynomials": adjacency,
        },
        "status": {
            "P_equals_1_N14_upper": 4950,
            "general_strict_n3_upper_bound": "NOT_PROVED",
            "all_even_f_excluded_for_P_at_least_4": "NOT_PROVED",
            "full_graph_constructed": False,
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "next_route": (
            "Test whether the locally compatible C4 box K3 parity-cancellation "
            "motif or the 3-by-3 rook regular set can extend through the full "
            "99-vertex lambda/mu closure. Incidence-code arguments need the "
            "actual binary rank/kernel of B or extra restrictions on the "
            "triangle-prism graph beyond its cycle space."
        ),
        "limitations": [
            "Discovery cannot certify itself.",
            "The code theorem constrains f mod 2 but does not force it nonzero in general.",
            "The 12-vertex cancellation motif is not a full target graph.",
            "No strict n3 upper bound or graph nonexistence result follows.",
            "Literature novelty remains UNKNOWN.",
        ],
    }


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--verify", action="store_true")
    arguments = parser.parse_args()
    if free_memory_percent() < 20:
        raise SystemExit("refusing to run below 20% free physical memory")
    rendered = canonical_json(exact_result())
    if arguments.verify:
        require(arguments.output.is_file(), "exact result is missing")
        require(
            arguments.output.read_text(encoding="utf-8") == rendered,
            "archived result mismatch",
        )
    else:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    print("PASS: Wave102 prism-incidence code checks")


if __name__ == "__main__":
    main()
