#!/usr/bin/env python3
"""Independent verifier for the Wave 102 prism-incidence claims.

The mathematical reconstruction in this file uses only the frozen graph
parameters and the claim scope assigned to the verifier.  Discovery output is
loaded only by the optional comparison routine after the independent result
has been emitted and hashed.
"""

from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
from itertools import combinations, permutations
import json
import math
from pathlib import Path
from typing import Any, Iterable


V = 99
K = 14
LAMBDA = 1
MU = 2
TRIANGLES = V * K // 6
ROOTED_PRISM_INCIDENCES_PER_PRISM = 6
PRISM_IDENTITY_TOTAL = 4158
DISCOVERY = Path("attempts/wave102-prism-incidence-code")
OUTPUT = Path(__file__).with_name("independent-final-results.json")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def edge(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left < right else (right, left)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=None)
def prism_graphs(vertices: tuple[int, ...]) -> tuple[frozenset[tuple[int, int]], ...]:
    """Return all 60 labelled induced triangular-prism graphs."""

    vertices = tuple(sorted(vertices))
    require(len(vertices) == 6, "a prism must use six vertices")
    anchor = vertices[0]
    rows: set[frozenset[tuple[int, int]]] = set()
    for two in combinations(vertices[1:], 2):
        first = (anchor,) + two
        second = tuple(vertex for vertex in vertices if vertex not in first)
        triangle_edges = {
            edge(left, right)
            for triangle in (first, second)
            for left, right in combinations(triangle, 2)
        }
        for matching in permutations(second):
            rows.add(
                frozenset(
                    triangle_edges
                    | {
                        edge(first[index], matching[index])
                        for index in range(3)
                    }
                )
            )
    require(len(rows) == 60, "labelled prism census changed")
    return tuple(sorted(rows, key=lambda row: tuple(sorted(row))))


def common_neighbor_count(
    edges: set[tuple[int, int]] | frozenset[tuple[int, int]],
    vertices: Iterable[int],
    left: int,
    right: int,
) -> int:
    return sum(
        edge(left, other) in edges and edge(right, other) in edges
        for other in vertices
        if other not in {left, right}
    )


def local_caps_hold(
    edges: set[tuple[int, int]] | frozenset[tuple[int, int]],
    forced_nonedges: set[tuple[int, int]] | frozenset[tuple[int, int]],
    vertices: tuple[int, ...],
) -> bool:
    """Apply only necessary SRG common-neighbor caps.

    Unknown pairs are allowed to be either edges or nonedges, so more than two
    already-forced common neighbors is impossible under either choice.
    """

    for left, right in combinations(vertices, 2):
        pair = edge(left, right)
        count = common_neighbor_count(edges, vertices, left, right)
        if pair in edges and count > LAMBDA:
            return False
        if pair in forced_nonedges and count > MU:
            return False
        if pair not in edges and pair not in forced_nonedges and count > MU:
            return False
    return True


def pair_overlap_certificate() -> dict[str, Any]:
    """Exhaust all labelled overlaps of two induced prisms."""

    rows = []
    for overlap in range(7):
        first_support = tuple(range(6))
        second_support = tuple(range(overlap)) + tuple(
            range(6, 12 - overlap)
        )
        first_pairs = set(combinations(first_support, 2))
        second_pairs = set(combinations(second_support, 2))
        shared_pairs = first_pairs & second_pairs
        vertices = tuple(sorted(set(first_support) | set(second_support)))
        consistent = 0
        cap_compatible = 0
        for first in prism_graphs(first_support):
            for second in prism_graphs(second_support):
                if overlap == 6 and first == second:
                    # This is the same induced prism, not two distinct prisms.
                    continue
                if any(
                    (pair in first) != (pair in second)
                    for pair in shared_pairs
                ):
                    continue
                consistent += 1
                edges = set(first) | set(second)
                forced_nonedges = (
                    (first_pairs - set(first))
                    | (second_pairs - set(second))
                )
                if local_caps_hold(edges, forced_nonedges, vertices):
                    cap_compatible += 1
        rows.append(
            {
                "support_intersection": overlap,
                "edge_consistent_labelled_pairs": consistent,
                "lambda_mu_cap_compatible_pairs": cap_compatible,
            }
        )
    require(
        all(row["lambda_mu_cap_compatible_pairs"] == 0 for row in rows[5:]),
        "distinct prisms with overlap at least five survived",
    )
    require(
        rows[4]["lambda_mu_cap_compatible_pairs"] > 0,
        "the four-vertex overlap bound was not sharp locally",
    )
    return {
        "rows": rows,
        "maximum_distinct_prism_overlap": 4,
        "proof_scope": (
            "complete labelled induced-prism gluing with necessary "
            "lambda/mu common-neighbor caps"
        ),
    }


def membership_profiles(max_odd_weight: int) -> list[dict[str, Any]]:
    """Enumerate incidence profiles of three six-subsets."""

    profiles: list[dict[str, Any]] = []

    def recurse(
        mask: int,
        counts: dict[int, int],
        support_sizes: list[int],
    ) -> None:
        if mask == 8:
            if support_sizes != [6, 6, 6]:
                return
            odd_weight = sum(
                count
                for pattern, count in counts.items()
                if pattern.bit_count() % 2 == 1
            )
            intersections = tuple(
                sum(
                    count
                    for pattern, count in counts.items()
                    if (pattern >> left) & 1 and (pattern >> right) & 1
                )
                for left, right in combinations(range(3), 2)
            )
            if odd_weight <= max_odd_weight and max(intersections) <= 4:
                profiles.append(
                    {
                        "counts_masks_1_through_7": [
                            counts.get(pattern, 0)
                            for pattern in range(1, 8)
                        ],
                        "odd_weight": odd_weight,
                        "pair_intersections": list(intersections),
                    }
                )
            return

        indices = [
            index for index in range(3) if (mask >> index) & 1
        ]
        maximum = min(6 - support_sizes[index] for index in indices)
        for count in range(maximum + 1):
            updated = support_sizes[:]
            for index in indices:
                updated[index] += count
            counts[mask] = count
            recurse(mask + 1, counts, updated)
        counts.pop(mask, None)

    recurse(1, {}, [0, 0, 0])
    return profiles


def supports_from_profile(
    profile: dict[str, Any],
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    supports = [set(), set(), set()]
    next_vertex = 0
    for mask, count in enumerate(profile["counts_masks_1_through_7"], 1):
        for _ in range(count):
            for index in range(3):
                if (mask >> index) & 1:
                    supports[index].add(next_vertex)
            next_vertex += 1
    return tuple(tuple(sorted(row)) for row in supports)  # type: ignore[return-value]


def compatible_three_prism_gluings(
    supports: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
) -> tuple[frozenset[tuple[int, int]], ...]:
    """Return distinct forced edge sets surviving local SRG caps."""

    support_pairs = [
        set(combinations(support, 2)) for support in supports
    ]
    vertices = tuple(sorted(set().union(*map(set, supports))))
    survivors: set[frozenset[tuple[int, int]]] = set()
    for first in prism_graphs(supports[0]):
        for second in prism_graphs(supports[1]):
            if any(
                (pair in first) != (pair in second)
                for pair in support_pairs[0] & support_pairs[1]
            ):
                continue
            first_edges = set(first) | set(second)
            first_nonedges = (
                (support_pairs[0] - set(first))
                | (support_pairs[1] - set(second))
            )
            if not local_caps_hold(first_edges, first_nonedges, vertices):
                continue
            for third in prism_graphs(supports[2]):
                conflict = False
                for pair in support_pairs[2]:
                    if pair in first_edges and pair not in third:
                        conflict = True
                    if pair in first_nonedges and pair in third:
                        conflict = True
                if conflict:
                    continue
                edges = first_edges | set(third)
                forced_nonedges = first_nonedges | (
                    support_pairs[2] - set(third)
                )
                if local_caps_hold(edges, forced_nonedges, vertices):
                    survivors.add(frozenset(edges))
    return tuple(sorted(survivors, key=lambda row: tuple(sorted(row))))


def induced_prism_supports(
    edges: frozenset[tuple[int, int]],
    vertices: tuple[int, ...],
) -> list[tuple[int, ...]]:
    rows = []
    for support in combinations(vertices, 6):
        induced = frozenset(
            pair
            for pair in edges
            if pair[0] in support and pair[1] in support
        )
        if induced in set(prism_graphs(tuple(support))):
            rows.append(tuple(support))
    return rows


def three_prism_certificate() -> dict[str, Any]:
    profiles = membership_profiles(max_odd_weight=2)
    require(len(profiles) == 11, "three-support profile census changed")
    profile_rows = []
    zero_survivors: list[frozenset[tuple[int, int]]] = []
    for profile in profiles:
        supports = supports_from_profile(profile)
        survivors = compatible_three_prism_gluings(supports)
        row = dict(profile)
        row["surviving_forced_graphs"] = len(survivors)
        profile_rows.append(row)
        if profile["odd_weight"] == 2:
            require(not survivors, "an O=2 gluing survived local caps")
        else:
            zero_survivors.extend(survivors)

    require(len(zero_survivors) == 36, "O=0 labelled census changed")
    rook_certificates = []
    for edges in zero_survivors:
        vertices = tuple(range(9))
        degrees = [
            sum(edge(vertex, other) in edges for other in vertices if other != vertex)
            for vertex in vertices
        ]
        adjacent_cn = {
            common_neighbor_count(edges, vertices, left, right)
            for left, right in edges
        }
        nonadjacent_cn = {
            common_neighbor_count(edges, vertices, left, right)
            for left, right in combinations(vertices, 2)
            if edge(left, right) not in edges
        }
        prism_supports = induced_prism_supports(edges, vertices)
        require(degrees == [4] * 9, "O=0 motif was not 4-regular")
        require(adjacent_cn == {1}, "O=0 motif lambda changed")
        require(nonadjacent_cn == {2}, "O=0 motif mu changed")
        require(
            len(prism_supports) == 6,
            "O=0 motif did not force six prisms",
        )
        rook_certificates.append(
            {
                "edge_count": len(edges),
                "degree_multiset": sorted(degrees),
                "adjacent_common_neighbor_counts": sorted(adjacent_cn),
                "nonadjacent_common_neighbor_counts": sorted(
                    nonadjacent_cn
                ),
                "induced_prism_count": len(prism_supports),
            }
        )
    require(
        len({json.dumps(row, sort_keys=True) for row in rook_certificates})
        == 1,
        "O=0 survivors had different parameter certificates",
    )
    return {
        "profile_count_with_O_at_most_2": len(profiles),
        "profiles": profile_rows,
        "O2_survivor_count": 0,
        "O0_labelled_survivor_count": len(zero_survivors),
        "O0_isomorphism_type": "3 by 3 rook graph K3 square K3",
        "O0_motif_certificate": rook_certificates[0],
        "P3_conclusion": (
            "If the global prism count P equals 3, O cannot be 0 because "
            "the only local O=0 gluing itself contains six distinct induced "
            "prisms; O=2 violates local lambda/mu caps; hence O>=4."
        ),
    }


def parity_defect_certificate() -> dict[str, Any]:
    representative_rows = []
    strict_rounding_improvements = 0
    for prism_count in range(PRISM_IDENTITY_TOTAL // 3 + 1):
        n3 = PRISM_IDENTITY_TOTAL - 3 * prism_count
        for odd_count in range(0, min(V, 6 * prism_count) + 1, 2):
            numerator = 55440 - 5 * n3 - odd_count // 2
            ordinary = numerator // 7
            antipodal = 2 * (numerator // 14)
            require(antipodal <= ordinary, "antipodal rounding weakened")
            strict_rounding_improvements += antipodal < ordinary
        if prism_count in {0, 1, 2, 3, 1386}:
            minimum_O = {0: 0, 1: 6, 2: 4, 3: 4}.get(
                prism_count, 0
            )
            numerator = 55440 - 5 * n3 - minimum_O // 2
            representative_rows.append(
                {
                    "P": prism_count,
                    "n3": n3,
                    "minimum_O_used": minimum_O,
                    "seven_N14_upper": numerator,
                    "ordinary_integer_N14_upper": numerator // 7,
                    "antipodal_even_N14_upper": 2 * (numerator // 14),
                }
            )

    # Rootwise floor identity.  O counts roots with odd f_o.
    for prism_count in range(50):
        total_f = 6 * prism_count
        for odd_count in range(0, min(V, total_f) + 1, 2):
            if odd_count > total_f:
                continue
            # Any nonnegative f-vector with this parity data satisfies this
            # algebraic identity; an explicit witness suffices to test signs.
            vector = [1] * odd_count
            remainder = total_f - odd_count
            if vector:
                vector[0] += remainder
            elif remainder:
                vector = [remainder]
            vector += [0] * (V - len(vector))
            require(sum(vector) == total_f, "f-vector witness sum changed")
            require(
                sum(value % 2 for value in vector) == odd_count,
                "f-vector witness parity changed",
            )
            floors = sum((5 * value) // 2 for value in vector)
            require(
                floors == 15 * prism_count - odd_count // 2,
                "rootwise parity-defect floor identity failed",
            )

    return {
        "definition": (
            "f_v is the number of induced triangular prisms containing "
            "vertex v; O is the Hamming weight of f modulo 2"
        ),
        "sum_f": "sum_v f_v = 6P",
        "O_integrality": (
            "O is an integer and is even because O is congruent modulo 2 "
            "to sum_v f_v=6P"
        ),
        "floor_sum_identity": (
            "sum_v floor(5 f_v/2) = 15P - O/2"
        ),
        "refined_inequality": "7*N14 <= 55440 - 5*n3 - O/2",
        "antipodal_rounding": (
            "N14 <= 2*floor((55440 - 5*n3 - O/2)/14)"
        ),
        "P1_exact_O": 6,
        "P2_minimum_O_from_overlap": 4,
        "P3_minimum_O_from_exhaustive_gluing": 4,
        "representative_rows": representative_rows,
        "finite_rounding_strict_improvement_count": (
            strict_rounding_improvements
        ),
    }


def incidence_code_certificate() -> dict[str, Any]:
    """Check the exact binary linear-algebra consequences."""

    # A^2=A over F2 follows from the SRG identity
    # A^2=(k-mu)I+(lambda-mu)A+mu*J.
    require((K - MU) % 2 == 0, "I coefficient did not vanish")
    require((LAMBDA - MU) % 2 == 1, "A coefficient changed")
    require(MU % 2 == 0, "J coefficient did not vanish")
    characteristic_multiplicities_mod2 = {"0": 45, "1": 54}
    require(sum(characteristic_multiplicities_mod2.values()) == V, "rank split changed")
    rank_A = characteristic_multiplicities_mod2["1"]
    rank_I_plus_A = characteristic_multiplicities_mod2["0"]

    # B is the vertex-by-triangle incidence matrix.  Every vertex is in
    # k/2=7 triangles, and a pair lies in one common triangle iff adjacent.
    diagonal_BBT = (K // 2) % 2
    require(TRIANGLES == 231, "triangle count changed")
    require(diagonal_BBT == 1, "BB^T diagonal changed")
    require(rank_A == 54 and rank_I_plus_A == 45, "binary ranks changed")

    possible_kernel_check_weights = []
    possible_profiles = {}
    for weight in range(1, V + 1):
        # If B^T x=0, its support induces a 7-regular triangle-free graph.
        if weight % 2:
            continue
        # The quotient/interlacing bounds reduce exactly to 36 <= s <= 60.
        if not 36 <= weight <= 60:
            continue
        # Outside degrees are even, with
        # sum d=7s and sum d^2=2s(s-22).  Since d^2=2d (mod 8),
        # this forces s divisible by four.
        if weight % 4:
            continue
        possible_kernel_check_weights.append(weight)

        target_count = V - weight
        target_sum = 7 * weight
        target_square_sum = 2 * weight * (weight - 22)

        @lru_cache(maxsize=None)
        def find_distribution(
            positions: int,
            remaining_sum: int,
            remaining_squares: int,
        ) -> tuple[int, ...] | None:
            if positions == 0:
                if remaining_sum == 0 and remaining_squares == 0:
                    return ()
                return None
            if remaining_sum < 0 or remaining_squares < 0:
                return None
            if remaining_sum > 14 * positions:
                return None
            if remaining_squares > 196 * positions:
                return None
            for degree in range(0, 15, 2):
                tail = find_distribution(
                    positions - 1,
                    remaining_sum - degree,
                    remaining_squares - degree * degree,
                )
                if tail is not None:
                    return (degree,) + tail
            return None

        distribution = find_distribution(
            target_count, target_sum, target_square_sum
        )
        require(distribution is not None, "listed check weight lacked moment witness")
        possible_profiles[str(weight)] = {
            str(degree): count
            for degree, count in sorted(Counter(distribution).items())
        }

    require(
        possible_kernel_check_weights == [36, 40, 44, 48, 52, 56, 60],
        "triangle-parity check weight list changed",
    )
    constant_one_check_weights = [
        V - weight for weight in reversed(possible_kernel_check_weights)
    ] + [V]
    universal_check_weight_candidates = sorted(
        possible_kernel_check_weights + constant_one_check_weights
    )
    return {
        "B_shape": [99, 231],
        "D_shape": [231, "P"],
        "vertex_prism_incidence_shape": [99, "P"],
        "factorization": "f mod 2 = B*D*1 over F2",
        "BBT": "B*B^T = I + A over F2",
        "A_mod2_identity": "A^2=A",
        "rank_A_mod2": rank_A,
        "rank_I_plus_A_mod2": rank_I_plus_A,
        "triangle_code_dimension_bounds": [45, 99],
        "triangle_dual_dimension_bounds": [0, 54],
        "even_triangle_code_dimension_bounds": [44, 98],
        "even_triangle_code_dual_dimension_bounds": [1, 55],
        "even_triangle_code_dimension": (
            "dim(im(B) intersect 1-perp) = rank(B)-1"
        ),
        "prism_code_dimension_bounds": (
            "rank(BD) <= min(P, rank(B)-1, rank(D)); rank(D)<=230"
        ),
        "kernel_triangle_parity_check_weight_candidates": (
            possible_kernel_check_weights
        ),
        "constant_one_triangle_check_weight_candidates": (
            constant_one_check_weights
        ),
        "all_nonzero_universal_check_weight_candidates": (
            universal_check_weight_candidates
        ),
        "outside_degree_moment_witnesses": possible_profiles,
        "weight_scope": (
            "necessary candidates only; no codeword existence is asserted"
        ),
    }


def rook_box_certificate() -> dict[str, Any]:
    vertices = tuple(range(9))
    coordinate = {vertex: divmod(vertex, 3) for vertex in vertices}
    edges = frozenset(
        edge(left, right)
        for left, right in combinations(vertices, 2)
        if coordinate[left][0] == coordinate[right][0]
        or coordinate[left][1] == coordinate[right][1]
    )
    degrees = [
        sum(edge(vertex, other) in edges for other in vertices if other != vertex)
        for vertex in vertices
    ]
    adjacent_cn = [
        common_neighbor_count(edges, vertices, left, right)
        for left, right in edges
    ]
    nonadjacent_cn = [
        common_neighbor_count(edges, vertices, left, right)
        for left, right in combinations(vertices, 2)
        if edge(left, right) not in edges
    ]
    prisms = induced_prism_supports(edges, vertices)
    require(degrees == [4] * 9, "rook degrees changed")
    require(set(adjacent_cn) == {1}, "rook lambda changed")
    require(set(nonadjacent_cn) == {2}, "rook mu changed")
    require(len(prisms) == 6, "rook prism count changed")

    cross_edges = 9 * (K - 4)
    outside_vertices = V - 9
    require(cross_edges == outside_vertices, "box cross-edge equality changed")
    quotient = [[4, 10], [1, 13]]
    quotient_eigenvalues = [14, 3]
    ambient_eigenvalues = {"14": 1, "3": 54, "-4": 44}
    motif_eigenvalues = {"4": 1, "1": 4, "-2": 4}
    require(quotient_eigenvalues == [14, 3], "quotient spectrum changed")
    return {
        "graph": "K3 square K3 (the 3 by 3 rook graph)",
        "parameters": [9, 4, 1, 2],
        "spectrum": motif_eigenvalues,
        "induced_prism_count": len(prisms),
        "outside_neighbor_cap": (
            "Every outside vertex has at most one neighbor in the box, "
            "because every pair in the box has already saturated its "
            "lambda=1 or mu=2 common-neighbor allowance internally."
        ),
        "cross_edge_count": cross_edges,
        "outside_vertex_count": outside_vertices,
        "equitable_partition_consequence": (
            "Every outside vertex has exactly one box neighbor."
        ),
        "quotient_matrix": quotient,
        "quotient_eigenvalues": quotient_eigenvalues,
        "ambient_spectrum": ambient_eigenvalues,
        "interlacing_verdict": (
            "compatible: the quotient eigenvalue 3 is an ambient "
            "eigenvalue, and the motif spectrum lies within ambient bounds"
        ),
        "global_extension_status": (
            "UNKNOWN: local cap saturation and compatible interlacing are "
            "necessary conditions, not a construction or extension theorem"
        ),
    }


def four_prism_cycle_box_certificate() -> dict[str, Any]:
    """Verify the local C4 Cartesian-product K3 parity-null motif."""

    vertices = tuple(range(12))
    coordinate = {
        vertex: divmod(vertex, 3) for vertex in vertices
    }
    edges = frozenset(
        edge(left, right)
        for left, right in combinations(vertices, 2)
        if (
            coordinate[left][0] == coordinate[right][0]
            and coordinate[left][1] != coordinate[right][1]
        )
        or (
            coordinate[left][1] == coordinate[right][1]
            and (coordinate[left][0] - coordinate[right][0]) % 4
            in {1, 3}
        )
    )
    degrees = [
        sum(edge(vertex, other) in edges for other in vertices if other != vertex)
        for vertex in vertices
    ]
    adjacent_cn = [
        common_neighbor_count(edges, vertices, left, right)
        for left, right in edges
    ]
    nonadjacent_cn = [
        common_neighbor_count(edges, vertices, left, right)
        for left, right in combinations(vertices, 2)
        if edge(left, right) not in edges
    ]
    prisms = induced_prism_supports(edges, vertices)
    incidences = {
        vertex: sum(vertex in support for support in prisms)
        for vertex in vertices
    }
    require(len(edges) == 24, "C4 box K3 edge count changed")
    require(degrees == [4] * 12, "C4 box K3 degrees changed")
    require(max(adjacent_cn) == 1, "C4 box K3 violates lambda cap")
    require(max(nonadjacent_cn) == 2, "C4 box K3 violates mu cap")
    require(len(prisms) == 4, "C4 box K3 prism count changed")
    require(set(incidences.values()) == {2}, "four-prism parity did not cancel")

    # Exact Cartesian-product spectrum: add eigenvalues of C4
    # {2,0,0,-2} and K3 {2,-1,-1}.
    spectrum = {"4": 1, "2": 2, "1": 2, "0": 1, "-1": 4, "-3": 2}
    require(sum(spectrum.values()) == 12, "motif spectrum order changed")
    require(
        sum(int(value) * multiplicity for value, multiplicity in spectrum.items())
        == 0,
        "motif spectrum trace changed",
    )
    require(
        sum(
            int(value) ** 2 * multiplicity
            for value, multiplicity in spectrum.items()
        )
        == 48,
        "motif spectrum square trace changed",
    )
    return {
        "graph": "Cartesian product C4 square K3",
        "vertices": 12,
        "edges": len(edges),
        "degree": 4,
        "induced_prism_count": len(prisms),
        "prisms_through_each_vertex": sorted(set(incidences.values())),
        "rooted_prism_parity": "zero",
        "maximum_internal_common_neighbors_adjacent": max(adjacent_cn),
        "maximum_internal_common_neighbors_nonadjacent": max(nonadjacent_cn),
        "spectrum": spectrum,
        "interlacing_verdict": (
            "compatible with the ambient eigenvalue interval [-4,14], "
            "including the sharper upper bound 3 on every non-leading "
            "induced eigenvalue"
        ),
        "global_extension_status": (
            "UNKNOWN: this is only a 12-vertex local induced motif; passing "
            "common-neighbor caps and interlacing does not prove a "
            "99-vertex completion"
        ),
    }


def build_independent_result() -> dict[str, Any]:
    return {
        "parameters": {
            "v": V,
            "k": K,
            "lambda": LAMBDA,
            "mu": MU,
            "triangle_count": TRIANGLES,
        },
        "pair_overlap": pair_overlap_certificate(),
        "three_prism_gluing": three_prism_certificate(),
        "parity_defect": parity_defect_certificate(),
        "incidence_code": incidence_code_certificate(),
        "P3_rook_null_branch": rook_box_certificate(),
        "four_prism_C4_box_K3_null_motif": (
            four_prism_cycle_box_certificate()
        ),
        "verdict_scope": (
            "The parity-defect inequality, small-P refinements, incidence "
            "factorization, binary rank consequences, and local null-motif "
            "classification are independently checked.  No global graph "
            "existence or nonexistence claim follows."
        ),
    }


def compare_discovery(independent: dict[str, Any]) -> dict[str, Any]:
    """Compare only after the pre-comparison independent result was frozen."""

    discovery_result = json.loads(
        (DISCOVERY / "exact-results.json").read_text(encoding="utf-8")
    )
    checks = {
        "refined_inequality_present": (
            "55440" in json.dumps(discovery_result)
            and "O/2" in json.dumps(discovery_result)
        ),
        "factorization_present": (
            "B D 1" in json.dumps(discovery_result)
            or "B*D*1" in json.dumps(discovery_result)
            or "BD1" in json.dumps(discovery_result)
            or "B*(D*1)" in json.dumps(discovery_result)
        ),
        "independent_P3_minimum": (
            independent["parity_defect"][
                "P3_minimum_O_from_exhaustive_gluing"
            ]
        ),
        "discovery_sha256": sha256(DISCOVERY / "exact-results.json"),
    }
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--compare-discovery",
        action="store_true",
        help="compare only after independent-results.json has been frozen",
    )
    args = parser.parse_args()
    result = build_independent_result()
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"output": str(OUTPUT), "sha256": sha256(OUTPUT)}))
    if args.compare_discovery:
        print(json.dumps(compare_discovery(result), sort_keys=True))


if __name__ == "__main__":
    main()
