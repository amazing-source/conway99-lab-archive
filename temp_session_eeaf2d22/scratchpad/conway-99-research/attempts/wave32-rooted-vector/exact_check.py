#!/usr/bin/env python3
"""Exact Wave 32 rooted-vector reductions.

Standard library only.  This checker audits necessary consequences of a
norm-two root in the frozen n3=708 actual-incidence endpoint package.  It
does not construct or exclude a target graph.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
FROZEN_INPUTS = {
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "verification/2026-07-22-n3-side-incidence-audit.md":
        "9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787",
    "verification/2026-07-23-wave20-global-schur-audit.md":
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave28-glue-discriminant/audit.md":
        "5c1dc7978d571a9471837b45a36663c7c457b6434800776501e4967146956b86",
    "verification/wave31-sign-commutant/audit.md":
        "f6145a3c4f4e787b23440a6ea071d606477821abab0ab8e7e5fe52042d6528a0",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True)
        .encode("utf-8")
        + b"\n"
    )


def hash_payload(payload: object) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    observed = {
        path: sha256_file(ROOT / path)
        for path in FROZEN_INPUTS
    }
    if observed != FROZEN_INPUTS:
        raise AssertionError(
            f"frozen input drift: expected={FROZEN_INPUTS}, observed={observed}"
        )
    return observed


def determinant(matrix: list[list[int]]) -> int:
    """Exact determinant by Fraction-valued elimination."""
    n = len(matrix)
    work = [[Fraction(value) for value in row] for row in matrix]
    result = Fraction(1)
    for col in range(n):
        pivot = next(
            (row for row in range(col, n) if work[row][col] != 0),
            None,
        )
        if pivot is None:
            return 0
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            result = -result
        pivot_value = work[col][col]
        result *= pivot_value
        for j in range(col, n):
            work[col][j] /= pivot_value
        for row in range(col + 1, n):
            factor = work[row][col]
            if factor:
                for j in range(col, n):
                    work[row][j] -= factor * work[col][j]
    if result.denominator != 1:
        raise AssertionError("integer matrix acquired nonintegral determinant")
    return result.numerator


def is_positive_semidefinite(matrix: list[list[int]]) -> bool:
    """Use the all-principal-minors criterion, exact in dimensions <=4."""
    n = len(matrix)
    for size in range(1, n + 1):
        for indices in itertools.combinations(range(n), size):
            minor = [
                [matrix[i][j] for j in indices]
                for i in indices
            ]
            if determinant(minor) < 0:
                return False
    return True


def extreme_fiber_screen() -> dict[str, object]:
    """Audit the matrix-only cap on coordinates with root product +/-2."""
    psd_counts: dict[str, int] = {}
    witnesses: dict[str, list[list[list[int]]]] = {}
    for size in range(1, 5):
        pairs = list(itertools.combinations(range(size), 2))
        accepted: list[list[list[int]]] = []
        for values in itertools.product((-2, -1), repeat=len(pairs)):
            gram = [
                [2 if i == j else 0 for j in range(size)]
                for i in range(size)
            ]
            for (i, j), value in zip(pairs, values):
                gram[i][j] = value
                gram[j][i] = value
            if is_positive_semidefinite(gram):
                accepted.append(gram)
        psd_counts[str(size)] = len(accepted)
        witnesses[str(size)] = accepted

    if psd_counts != {"1": 1, "2": 2, "3": 1, "4": 0}:
        raise AssertionError(f"extreme-fiber PSD census drifted: {psd_counts}")
    triple = witnesses["3"][0]
    expected_triple = [
        [2, -1, -1],
        [-1, 2, -1],
        [-1, -1, 2],
    ]
    if triple != expected_triple:
        raise AssertionError(f"unexpected triple Gram: {triple}")
    if [sum(row) for row in triple] != [0, 0, 0]:
        raise AssertionError("the size-three extreme fiber is not an A2 triple")

    # For a same-sign triple u1+u2+u3=0.  Every transformed root from the
    # opposite extreme fiber has nonpositive inner product with each ui.
    # Their sum is zero, so all three products vanish, and the original
    # frame products are -2.
    cross_inner_products = [0, 0, 0]
    cross_frame_products = [-2, -2, -2]
    return {
        "definition": "u_i=sign(y_i)*x_i-r for abs(y_i)=2",
        "same_sign_pair_alphabet": [-2, -1],
        "psd_gram_count_by_fiber_size": psd_counts,
        "maximum_same_sign_fiber_size": 3,
        "size_three_gram": triple,
        "size_three_relation": "u1+u2+u3=0",
        "size_three_frame_products": [1, 1, 1],
        "opposite_extreme_inner_products_if_triple": cross_inner_products,
        "opposite_extreme_frame_products_if_triple": cross_frame_products,
    }


def root_count_patterns() -> dict[str, object]:
    moment_patterns = []
    tensor_patterns = []
    extreme_patterns = []
    for plus_two in range(8):
        for minus_two in range(8):
            plus_one = 21 - 3 * plus_two - minus_two
            minus_one = 21 - plus_two - 3 * minus_two
            zero = 189 + 3 * (plus_two + minus_two)
            if min(plus_one, minus_one, zero) < 0:
                continue
            row = {
                "plus_2": plus_two,
                "plus_1": plus_one,
                "zero": zero,
                "minus_1": minus_one,
                "minus_2": minus_two,
                "cube_sum": 6 * (plus_two - minus_two),
            }
            moment_patterns.append(row)
            if abs(plus_two - minus_two) <= 3:
                tensor_patterns.append(row)
                if plus_two <= 3 and minus_two <= 3:
                    extreme_patterns.append(row)

    actual_pattern = [
        row for row in extreme_patterns
        if row["plus_2"] == 0 and row["minus_2"] == 0
    ]
    counts = {
        "moment_only": len(moment_patterns),
        "wave28_tensor_filtered": len(tensor_patterns),
        "matrix_only_extreme_filtered": len(extreme_patterns),
        "actual_incidence_filtered": len(actual_pattern),
    }
    if counts != {
        "moment_only": 46,
        "wave28_tensor_filtered": 32,
        "matrix_only_extreme_filtered": 16,
        "actual_incidence_filtered": 1,
    }:
        raise AssertionError(f"root pattern census drifted: {counts}")
    expected = {
        "plus_2": 0,
        "plus_1": 21,
        "zero": 189,
        "minus_1": 21,
        "minus_2": 0,
        "cube_sum": 0,
    }
    if actual_pattern != [expected]:
        raise AssertionError(f"hostile pattern drifted: {actual_pattern}")
    return {
        "counts": counts,
        "actual_incidence_pattern": expected,
        "matrix_only_patterns": extreme_patterns,
    }


def projector_and_incidence_transport() -> dict[str, object]:
    """Check the exact spectral and congruence coefficients."""
    projector_values = {
        "14_on_ones": Fraction(27 - 9 * 14 + 99, 63),
        "3": Fraction(27 - 9 * 3, 63),
        "minus_4": Fraction(27 - 9 * (-4), 63),
    }
    if projector_values != {
        "14_on_ones": Fraction(0),
        "3": Fraction(0),
        "minus_4": Fraction(1),
    }:
        raise AssertionError(f"minus-four projector drifted: {projector_values}")

    return {
        "triangle_projector": "E=M/21",
        "root_vector": "y=X*S*r is in 21L*=M*Z^231",
        "identities": [
            "M*y=21*y",
            "Gamma*y=0",
            "z=N*y",
            "A*z=-4*z",
            "sum(z)=0",
            "norm(z)^2=126",
        ],
        "minus_four_projector": "(27I-9A+J)/63",
        "projector_eigenvalues": {
            key: str(value) for key, value in projector_values.items()
        },
        "transport_identity": "N*M=(9I-3A)*N+J_(99x231)",
        "transport_mod_3": "every column of N*M is the all-ones vector mod 3",
        "consequence": "all 99 coordinates of z=N*y are congruent mod 3",
    }


def residue_reduction() -> dict[str, object]:
    cases = []
    for residue in (-1, 0, 1):
        k_sum = -33 * residue
        k_norm = 14 if residue == 0 else 25
        integer_lower_bound = abs(k_sum)
        accepted = k_norm >= integer_lower_bound
        cases.append({
            "residue": residue,
            "representation": f"z={residue}*1+3*k",
            "sum_k": k_sum,
            "norm_k_squared": k_norm,
            "integer_bound_sum_abs_le_norm_squared": integer_lower_bound,
            "accepted": accepted,
        })
    accepted = [row["residue"] for row in cases if row["accepted"]]
    if accepted != [0]:
        raise AssertionError(f"residue screen drifted: {cases}")
    return {
        "cases": cases,
        "conclusion": "z=3k with integral k, sum(k)=0, norm(k)^2=14, A*k=-4*k",
    }


def integer_k_distributions() -> list[tuple[int, ...]]:
    values = tuple(range(-3, 4))
    distributions: list[tuple[int, ...]] = []

    def recurse(
        index: int,
        remaining_count: int,
        remaining_sum: int,
        remaining_norm: int,
        counts: list[int],
    ) -> None:
        if index == len(values):
            if (
                remaining_count == 0
                and remaining_sum == 0
                and remaining_norm == 0
            ):
                distributions.append(tuple(counts))
            return
        value = values[index]
        if value == 0:
            maximum = remaining_count
        else:
            maximum = min(
                remaining_count,
                remaining_norm // (value * value),
            )
        for count in range(maximum + 1):
            recurse(
                index + 1,
                remaining_count - count,
                remaining_sum - count * value,
                remaining_norm - count * value * value,
                counts + [count],
            )

    recurse(0, 99, 0, 14, [])
    return distributions


def eigenvector_amplitude_screen(eigenvalue_magnitude: int = 4) -> dict[str, object]:
    values = tuple(range(-3, 4))
    distributions = integer_k_distributions()
    survivors = []
    for counts in distributions:
        positive_mass = sum(
            value * count
            for value, count in zip(values, counts)
            if value > 0
        )
        maximum = max(
            abs(value)
            for value, count in zip(values, counts)
            if count
        )
        if eigenvalue_magnitude * maximum <= positive_mass:
            survivors.append(counts)
    expected = (0, 0, 7, 85, 7, 0, 0)
    if eigenvalue_magnitude == 4 and survivors != [expected]:
        raise AssertionError(f"amplitude screen drifted: {survivors}")
    coordinate_bound = [
        magnitude
        for magnitude in range(4)
        if (
            14 - magnitude * magnitude
            >= (2 * eigenvalue_magnitude - 1) * magnitude
        )
    ]
    if eigenvalue_magnitude == 4 and coordinate_bound != [0, 1]:
        raise AssertionError(f"coordinate bound drifted: {coordinate_bound}")
    return {
        "raw_integer_distribution_count": len(distributions),
        "eigenvalue_magnitude": eigenvalue_magnitude,
        "surviving_distribution_count": len(survivors),
        "survivors": [
            {
                str(value): count
                for value, count in zip(values, counts)
                if count
            }
            for counts in survivors
        ],
        "proof_inequalities": [
            "2*positive_mass=sum(abs(k_i))<=sum(k_i^2)=14",
            (
                "at an entry of magnitude m, "
                f"{eigenvalue_magnitude}*m<=positive_mass"
            ),
            (
                "for eigenvalue magnitude q, the neighbor and nonneighbor "
                "sums are -q*a and (q-1)*a, so "
                "14-a^2>=(2*q-1)*abs(a)"
            ),
        ],
        "coordinate_bound_abs_values": coordinate_bound,
    }


def fano_complement() -> list[list[int]]:
    """Rows and columns are the seven nonzero vectors of F_2^3."""
    fano = []
    for normal in range(1, 8):
        row = []
        for point in range(1, 8):
            dot = (normal & point).bit_count() % 2
            row.append(1 if dot == 0 else 0)
        fano.append(row)
    return [[1 - value for value in row] for row in fano]


def pair_intersections(matrix: list[list[int]]) -> list[int]:
    return [
        sum(matrix[i][k] * matrix[j][k] for k in range(len(matrix[0])))
        for i, j in itertools.combinations(range(len(matrix)), 2)
    ]


def support_design_screen(mu: int = 2) -> dict[str, object]:
    # t is the number of same-sign edges in either seven-set.  The
    # eigenvector equations give cross degree 4+d at a vertex of internal
    # degree d.  Count P-pairs through N and compare with lambda/mu caps.
    rows = []
    for t in range(11):
        common_via_opposite_lower = 42 + 7 * t
        pair_cap = t + mu * (21 - t)
        rows.append({
            "same_sign_edges_t": t,
            "common_opposite_neighbors_lower": common_via_opposite_lower,
            "lambda_mu_pair_cap": pair_cap,
            "passes_weak_count": common_via_opposite_lower <= pair_cap,
        })
    passing = [
        row["same_sign_edges_t"]
        for row in rows
        if row["passes_weak_count"]
    ]
    if mu == 2 and passing != [0]:
        raise AssertionError(f"support design screen drifted: {rows}")

    complement = fano_complement()
    row_sums = [sum(row) for row in complement]
    col_sums = [
        sum(complement[i][j] for i in range(7))
        for j in range(7)
    ]
    row_intersections = pair_intersections(complement)
    col_intersections = pair_intersections(
        [list(column) for column in zip(*complement)]
    )
    if (
        row_sums != [4] * 7
        or col_sums != [4] * 7
        or row_intersections != [2] * 21
        or col_intersections != [2] * 21
    ):
        raise AssertionError("canonical Fano-complement design drifted")

    return {
        "mu": mu,
        "count_rows": rows,
        "passing_t": passing,
        "actual_conclusion": (
            "two independent seven-sets, cross incidence a symmetric "
            "2-(7,4,2) design"
        ) if mu == 2 else "hostile relaxed-mu control",
        "canonical_cross_incidence": complement,
        "canonical_cross_incidence_sha256": hash_payload(complement),
        "row_sums": row_sums,
        "column_sums": col_sums,
        "same_side_pair_intersections": sorted(set(row_intersections)),
    }


def build_hostile_partial_control() -> dict[str, object]:
    """Build all edges incident to the 14 signed support vertices.

    The 70 support-adjacent outside vertices are:
      * 28 unique completions of support edges;
      * two completions for each of the 21 support nonedges.
    Fifteen further outside vertices have no support neighbor.
    We also add the 42 forced matching edges between nonedge-completion
    vertices that make the three remaining triangles at each support point.
    The outside graph is intentionally incomplete.
    """
    cross = fano_complement()
    positive = list(range(7))
    negative = list(range(7, 14))
    edges: set[tuple[int, int]] = set()

    def add_edge(left: int, right: int) -> None:
        if left == right:
            raise AssertionError("loop in hostile partial control")
        edges.add(tuple(sorted((left, right))))

    edge_completion: dict[tuple[int, int], int] = {}
    nonedge_completion: dict[tuple[int, int, int], int] = {}
    next_vertex = 14

    for p in range(7):
        for n_local in range(7):
            n = 7 + n_local
            if cross[p][n_local]:
                add_edge(p, n)
                edge_completion[(p, n_local)] = next_vertex
                add_edge(p, next_vertex)
                add_edge(n, next_vertex)
                next_vertex += 1
    if next_vertex != 42:
        raise AssertionError("support-edge completion count drifted")

    for p in range(7):
        for n_local in range(7):
            if cross[p][n_local]:
                continue
            for copy in range(2):
                vertex = next_vertex
                nonedge_completion[(p, n_local, copy)] = vertex
                add_edge(p, vertex)
                add_edge(7 + n_local, vertex)
                next_vertex += 1
    if next_vertex != 84:
        raise AssertionError("support-nonedge completion count drifted")
    isolated_from_support = list(range(84, 99))

    singleton_triangle_edges: set[tuple[int, int]] = set()

    def add_three_pair_matching(groups: list[tuple[int, int]]) -> None:
        # groups are the two copies for each of three nonneighbors.
        (a0, a1), (b0, b1), (c0, c1) = groups
        for left, right in ((a0, b0), (b1, c0), (c1, a1)):
            edge = tuple(sorted((left, right)))
            if edge in singleton_triangle_edges:
                raise AssertionError("duplicate singleton-triangle edge")
            singleton_triangle_edges.add(edge)
            add_edge(*edge)

    for p in range(7):
        nonneighbors = [
            n_local for n_local in range(7)
            if not cross[p][n_local]
        ]
        groups = [
            (
                nonedge_completion[(p, n_local, 0)],
                nonedge_completion[(p, n_local, 1)],
            )
            for n_local in nonneighbors
        ]
        add_three_pair_matching(groups)

    for n_local in range(7):
        nonneighbors = [
            p for p in range(7)
            if not cross[p][n_local]
        ]
        groups = [
            (
                nonedge_completion[(p, n_local, 0)],
                nonedge_completion[(p, n_local, 1)],
            )
            for p in nonneighbors
        ]
        add_three_pair_matching(groups)

    adjacency = [set() for _ in range(99)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

    support = set(range(14))
    if [len(adjacency[v]) for v in range(14)] != [14] * 14:
        raise AssertionError("hostile support degrees are not saturated at 14")
    outside_support_degrees = [
        len(adjacency[v] & support)
        for v in range(14, 99)
    ]
    if sorted(outside_support_degrees) != [0] * 15 + [2] * 70:
        raise AssertionError("hostile outside support-degree census drifted")
    outside_total_degrees = [
        len(adjacency[v])
        for v in range(14, 99)
    ]
    if sorted(outside_total_degrees) != [0] * 15 + [2] * 28 + [4] * 42:
        raise AssertionError("hostile outside total-degree census drifted")
    outside_remaining_degrees = [
        14 - degree
        for degree in outside_total_degrees
    ]
    if sorted(outside_remaining_degrees) != [10] * 42 + [12] * 28 + [14] * 15:
        raise AssertionError("hostile outside residual-degree census drifted")

    # All support pairs already attain their exact SRG common-neighbor count.
    support_pair_counts = {"edge": [], "nonedge": []}
    for left, right in itertools.combinations(range(14), 2):
        common = len(adjacency[left] & adjacency[right])
        key = "edge" if right in adjacency[left] else "nonedge"
        support_pair_counts[key].append(common)
    if set(support_pair_counts["edge"]) != {1}:
        raise AssertionError("support edge lambda count drifted")
    if set(support_pair_counts["nonedge"]) != {2}:
        raise AssertionError("support nonedge mu count drifted")

    # Every edge incident with support has its unique triangle already.
    for left, right in edges:
        if left in support or right in support:
            if len(adjacency[left] & adjacency[right]) != 1:
                raise AssertionError(
                    f"support incident edge {(left, right)} lacks lambda=1"
                )

    signed = [1] * 7 + [-1] * 7 + [0] * 85
    adjacency_times_signed = [
        sum(signed[neighbor] for neighbor in adjacency[v])
        for v in range(99)
    ]
    if adjacency_times_signed != [-4 * value for value in signed]:
        raise AssertionError("hostile partial control lost the -4 eigenvector")

    edge_payload = [list(edge) for edge in sorted(edges)]
    return {
        "status": "PARTIAL_LOCAL_CONTROL_NOT_A_GRAPH",
        "vertex_count": 99,
        "support_size": 14,
        "support_edge_count": 28,
        "support_nonedge_count_across_signs": 21,
        "outside_type_counts": {
            "unique_support_edge_completion": 28,
            "two_per_support_nonedge": 42,
            "zero_support_neighbors": len(isolated_from_support),
        },
        "outside_support_degree_distribution": {
            "0": outside_support_degrees.count(0),
            "2": outside_support_degrees.count(2),
        },
        "outside_total_degree_distribution": {
            "0": outside_total_degrees.count(0),
            "2": outside_total_degrees.count(2),
            "4": outside_total_degrees.count(4),
        },
        "outside_remaining_degree_distribution": {
            "10": outside_remaining_degrees.count(10),
            "12": outside_remaining_degrees.count(12),
            "14": outside_remaining_degrees.count(14),
        },
        "forced_singleton_triangle_edge_count": len(singleton_triangle_edges),
        "support_degrees": [len(adjacency[v]) for v in range(14)],
        "support_pair_common_neighbor_values": {
            key: sorted(set(values))
            for key, values in support_pair_counts.items()
        },
        "partial_edge_count": len(edges),
        "partial_edge_list_sha256": hash_payload(edge_payload),
        "signed_vector_norm_squared": sum(value * value for value in signed),
        "signed_vector_eigenvalue": -4,
        "unfilled_boundary": (
            "outside vertices still need degrees 10, 12, or 14 and all "
            "outside-only lambda/mu/triangle constraints"
        ),
    }


def final_y_and_outside_census() -> dict[str, object]:
    return {
        "signed_vertex_support": {
            "plus_1": 7,
            "minus_1": 7,
            "zero": 85,
        },
        "support_induced_graph": "bipartite complement of the Fano incidence graph",
        "support_cross_edges": 28,
        "triangles_with_two_opposite_support_vertices": 28,
        "triangles_with_one_support_vertex": {
            "positive": 21,
            "negative": 21,
        },
        "triangles_disjoint_from_support": 161,
        "root_triangle_vector_y": {
            "plus_2": 0,
            "plus_1": 21,
            "zero": 189,
            "minus_1": 21,
            "minus_2": 0,
        },
        "outside_vertex_types": {
            "support_edge_completion": 28,
            "support_nonedge_completion": 42,
            "no_support_neighbor": 15,
        },
    }


def schur_and_a4_constraints() -> dict[str, object]:
    possible_double_contraction_norms = list(range(6, 79, 8))
    possible_first_contraction_norms = list(range(2, 79, 4))
    ne_edges = [(1134 - value) // 8 for value in possible_double_contraction_norms]
    if possible_double_contraction_norms != [
        6, 14, 22, 30, 38, 46, 54, 62, 70, 78
    ]:
        raise AssertionError("double-contraction norm list drifted")
    if ne_edges != list(range(141, 131, -1)):
        raise AssertionError(f"nonedge-type edge census drifted: {ne_edges}")
    if 23 * max(possible_double_contraction_norms) > 1800:
        raise AssertionError("harmonic contraction bound failed")
    if 23 * 86 <= 1800:
        raise AssertionError("hostile next residue should fail harmonic bound")

    return {
        "global_harmonic_cubic": {
            "tensor": "T=sum_i (S^(1/2)x_i)^(tensor 3)",
            "trace_free": True,
            "norm_squared": 60,
            "root_line_cubic": 0,
        },
        "double_contraction": {
            "p": "p=y coordinatewise squared",
            "g": "T(a,a,.)=S^(1/2)X^T p, where a=S^(1/2)r",
            "norm_squared_symbol": "g2=p^T M p",
            "incidence_formula": "g2=1134-8*f",
            "f_definition": (
                "number of edges among the 42 outside vertices completing "
                "support nonedges"
            ),
            "harmonic_bound": "23*g2<=1800",
            "possible_g2": possible_double_contraction_norms,
            "corresponding_f": ne_edges,
        },
        "first_contraction": {
            "H": "T(a,.,.)",
            "norm_squared_symbol": "H2=y^T W y",
            "coordinate_form": "H2=(S*r)^T Q (S*r)",
            "congruence": "H2=2 mod 4",
            "harmonic_bound": "23*H2<=1800",
            "possible_H2": possible_first_contraction_norms,
        },
        "A4": {
            "definition": "A4=M*W*M",
            "identity": "y^T A4 y=441*H2",
        },
        "dimension_constants": {
            "ambient_dimension": 44,
            "orthogonal_dimension": 43,
            "minimum_trace_lift_norm_factor": "3/(43+2)=1/15",
        },
    }


def root_reflection() -> dict[str, object]:
    return {
        "lattice_reflection": "rho_r(v)=v-(v,r)_S*r",
        "frame_rows": "x_i maps to x_i-y_i*r",
        "coordinate_reflection": "H_r=I-y*y^T/21",
        "coordinate_identities": [
            "H_r^2=I",
            "H_r^T=H_r",
            "H_r*X=X-y*r^T",
            "H_r commutes with E",
            "H_r*M*H_r=M",
        ],
        "vertex_reflection": "I-z*z^T/63=I-k*k^T/7 on the minus-four space",
        "status_wall": (
            "these are changes of frame factorization, not coordinate "
            "permutations and not graph automorphisms"
        ),
    }


def build_results() -> dict[str, object]:
    frozen = verify_frozen_inputs()
    return {
        "schema_version": 1,
        "claim_label": "DERIVED_VERIFICATION_PENDING",
        "scope": (
            "necessary rooted-vector reduction under the full actual "
            "vertex-triangle incidence n3=708 endpoint package"
        ),
        "frozen_inputs": frozen,
        "matrix_only_extreme_fibers": extreme_fiber_screen(),
        "root_count_patterns": root_count_patterns(),
        "projector_and_incidence_transport": projector_and_incidence_transport(),
        "mod3_residue_reduction": residue_reduction(),
        "integer_minus_four_vector": eigenvector_amplitude_screen(),
        "hostile_eigenvalue_minus_three": eigenvector_amplitude_screen(3),
        "support_design": support_design_screen(),
        "hostile_mu_three": support_design_screen(3),
        "final_y_and_outside_census": final_y_and_outside_census(),
        "schur_and_a4_constraints": schur_and_a4_constraints(),
        "root_reflection": root_reflection(),
        "hostile_partial_control": build_hostile_partial_control(),
        "status": {
            "root_pattern_reduction": "DERIVED_VERIFICATION_PENDING",
            "root_exclusion": "NOT_OBTAINED",
            "rooted_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = build_results()
    encoded = canonical_bytes(payload)
    if args.output:
        args.output.write_bytes(encoded)
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
