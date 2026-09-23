#!/usr/bin/env python3
"""Clean-room verifier for the Wave 38 higher-order endpoint claims.

This module does not import or execute the discovery implementation.  The
36-row hexadecimal adjacency encoding is treated as frozen candidate data.
All graph reconstruction, exact ranks, walk subtraction, and column counts
below are independent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, deque
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from typing import Iterable, Sequence


BASE_COMMIT = "3014f3b1c010cdde1687b8878d4ec58d2bb90f03"
P = 3

# Frozen candidate data copied from attempts/wave38-higher-order/exact-results.json.
# Vertex order is three consecutive fibres of size twelve.
CORE_ROWS_HEX = (
    "800080002",
    "80001001",
    "1004008",
    "100020004",
    "200002020",
    "2800010",
    "40100080",
    "400010040",
    "4040200",
    "10400100",
    "20200800",
    "8008400",
    "2002002",
    "400001010",
    "200008004",
    "20004800",
    "1020080",
    "800010008",
    "8080100",
    "40040001",
    "80200040",
    "4100400",
    "100800200",
    "10400020",
    "2010004",
    "1001020",
    "8200100",
    "4040800",
    "20800200",
    "10008400",
    "80080040",
    "40100002",
    "200400008",
    "100004010",
    "800002080",
    "400020001",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rank_mod(matrix: Sequence[Sequence[int]], prime: int = P) -> int:
    """Exact row rank over F_prime."""
    a = [[value % prime for value in row] for row in matrix]
    if not a:
        return 0
    rows, cols = len(a), len(a[0])
    require(all(len(row) == cols for row in a), "ragged matrix")
    rank = 0
    for col in range(cols):
        pivot = next((r for r in range(rank, rows) if a[r][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inverse = pow(a[rank][col], -1, prime)
        a[rank] = [(inverse * value) % prime for value in a[rank]]
        for r in range(rows):
            if r == rank or not a[r][col]:
                continue
            multiple = a[r][col]
            a[r] = [
                (left - multiple * right) % prime
                for left, right in zip(a[r], a[rank])
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def rank_rational(matrix: Sequence[Sequence[int]]) -> int:
    """Exact rational row rank using Fraction elimination."""
    a = [[Fraction(value) for value in row] for row in matrix]
    if not a:
        return 0
    rows, cols = len(a), len(a[0])
    require(all(len(row) == cols for row in a), "ragged matrix")
    rank = 0
    for col in range(cols):
        pivot = next((r for r in range(rank, rows) if a[r][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        pivot_value = a[rank][col]
        for r in range(rank + 1, rows):
            if not a[r][col]:
                continue
            multiple = a[r][col] / pivot_value
            for c in range(col, cols):
                a[r][c] -= multiple * a[rank][c]
        rank += 1
        if rank == rows:
            break
    return rank


def mat_vec_mod(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> list[int]:
    return [sum(a * b for a, b in zip(row, vector)) % P for row in matrix]


def trace_power(matrix: Sequence[Sequence[int]], exponent: int) -> int:
    """Small exact integer trace power, used only by hostile controls."""
    n = len(matrix)
    require(exponent >= 1 and all(len(row) == n for row in matrix), "bad matrix")
    current = [list(row) for row in matrix]
    for _ in range(1, exponent):
        current = [
            [
                sum(current[i][k] * matrix[k][j] for k in range(n))
                for j in range(n)
            ]
            for i in range(n)
        ]
    return sum(current[i][i] for i in range(n))


def signed_walk_counts() -> dict[str, int]:
    """Reconstruct the endpoint signed triangle and simple-C4 imbalances."""
    vertices = 231
    support_degree = 68
    trace_s3 = 44 * 17**3 + 187 * (-4) ** 3
    trace_s4 = 44 * 17**4 + 187 * (-4) ** 4

    # A non-simple closed four-walk has v0=v2 or v1=v3.  Each class has
    # n*d^2 members.  Alternating walks on one edge, n*d in number, lie in
    # both classes.  Repeated edges occur an even number of times, so every
    # such signed walk contributes +1 regardless of the edge signs.
    non_simple = vertices * support_degree * (2 * support_degree - 1)
    remainder = trace_s4 - non_simple
    require(remainder % 8 == 0, "simple four-walk remainder is not divisible by 8")
    return {
        "trace_S_cubed": trace_s3,
        "balanced_minus_unbalanced_support_triangles": trace_s3 // 6,
        "trace_S_fourth": trace_s4,
        "nonsimple_closed_signed_walks_length_four": non_simple,
        "balanced_minus_unbalanced_support_four_cycles": remainder // 8,
    }


def signed_four_cycle_control(edge_signs: Sequence[int]) -> dict[str, int]:
    """Direct four-vertex control for sign orientation and subtraction."""
    require(len(edge_signs) == 4 and all(abs(x) == 1 for x in edge_signs), "bad signs")
    matrix = [[0] * 4 for _ in range(4)]
    for i, sign in enumerate(edge_signs):
        j = (i + 1) % 4
        matrix[i][j] = matrix[j][i] = sign
    trace4 = trace_power(matrix, 4)
    non_simple = 4 * 2 * (2 * 2 - 1)
    product_sign = edge_signs[0] * edge_signs[1] * edge_signs[2] * edge_signs[3]
    return {
        "cycle_product": product_sign,
        "trace_fourth": trace4,
        "nonsimple": non_simple,
        "simple_contribution": trace4 - non_simple,
        "expected_simple_contribution": 8 * product_sign,
    }


def ternary_centering_checks() -> dict[str, object]:
    """Check every scalar and finite-dimensional step in the centering lemma."""
    mnt_values = (4, -2, 1)
    common_inner_products = tuple((2 * value) % P for value in mnt_values)
    require(common_inner_products == (2, 2, 2), "MN^T values do not reduce uniformly")

    star_size = 7
    row_norm = 2
    pair_inner_product = 0
    w_norm = (
        star_size * row_norm
        + star_size * (star_size - 1) * pair_inner_product
    ) % P
    common = 2
    centered_norm = (row_norm - common - common + w_norm) % P
    centered_to_w = (common - w_norm) % P
    centered_pair_shift = (-common - common + w_norm) % P
    star_centered_coefficient = (1 - star_size) % P

    clique_gram = [
        [0 if i == j else 1 for j in range(star_size)]
        for i in range(star_size)
    ]
    clique_rank = rank_mod(clique_gram)
    uncentered_clique_gram = [
        [row_norm if i == j else pair_inner_product for j in range(star_size)]
        for i in range(star_size)
    ]
    uncentered_clique_rank = rank_mod(uncentered_clique_gram)

    require(w_norm == 2, "common star sum is not anisotropic")
    require(centered_norm == 0, "centered rows are not isotropic")
    require(centered_to_w == 0, "centered rows are not orthogonal to w")
    require(centered_pair_shift == 1, "centered Gram is not C+J")
    require(star_centered_coefficient == 0, "centered vertex-star sum is not zero")
    require(clique_rank == 6, "seven-clique centered Gram rank is not six")
    require(uncentered_clique_rank == 7, "uncentered vertex-star Gram rank is not seven")

    return {
        "MNt_integer_values": list(mnt_values),
        "MNt_derivation": {
            "premises": [
                "Gamma=N^T N-3I",
                "N N^T=7I+A",
                "A^2=12I-A+2J",
                "M=21I+4Gamma-Gamma^2+J",
            ],
            "simplified_identity": "M N^T=9N^T-3N^T A+J",
            "vertex_cases_for_number_of_neighbors_in_T": [2, 1, 0],
            "resulting_values": [4, -2, 1],
        },
        "twice_MNt_mod_3": list(common_inner_products),
        "common_inner_product_with_vT": common,
        "star_size": star_size,
        "mutual_inner_product_in_star": pair_inner_product,
        "w_norm_mod_3": w_norm,
        "centered_row_norm_mod_3": centered_norm,
        "centered_row_inner_w_mod_3": centered_to_w,
        "centered_gram_shift_mod_3": centered_pair_shift,
        "vertex_star_centered_sum_coefficient_mod_3": star_centered_coefficient,
        "seven_clique_centered_gram_rank_F3": clique_rank,
        "seven_clique_uncentered_gram_rank_F3": uncentered_clique_rank,
        "wording_qualifier": (
            "The rank-six statement is for the centered z_T Gram D=C+J. "
            "The uncentered v_T Gram on a vertex star is 2I_7 and has rank seven."
        ),
        "rank_drop_lemma": {
            "hypotheses": [
                "C=V H V^T with V full column rank and H nondegenerate",
                "the factor rows v_T span the r3-dimensional factor space",
                "all vertex-star sums have inner product 2 with every v_T",
                "(w,w)=2, so w is anisotropic",
            ],
            "argument": (
                "All z_T=v_T-w lie in w-perp. Since v_T=z_T+w span the "
                "factor space and w is not in w-perp, the z_T span exactly "
                "w-perp. The form restricted to w-perp is nondegenerate, so "
                "their Gram matrix D=C+J has rank r3-1."
            ),
            "conclusion": "rank_F3(C+J)=r3-1",
        },
    }


def reconstruct_core() -> list[int]:
    rows = [int(text, 16) for text in CORE_ROWS_HEX]
    n = len(rows)
    require(n == 36, "core does not have 36 rows")
    require(all(0 <= row < 1 << n for row in rows), "row mask exceeds 36 vertices")
    for i, row in enumerate(rows):
        require(not ((row >> i) & 1), f"loop at vertex {i}")
        for j in range(n):
            require(
                ((row >> j) & 1) == ((rows[j] >> i) & 1),
                f"asymmetry at {i},{j}",
            )
    return rows


def neighbors(rows: Sequence[int], vertex: int) -> list[int]:
    return [j for j in range(len(rows)) if (rows[vertex] >> j) & 1]


def connected_components(rows: Sequence[int]) -> list[list[int]]:
    unseen = set(range(len(rows)))
    components: list[list[int]] = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        queue = deque([start])
        component = [start]
        while queue:
            u = queue.popleft()
            for v in neighbors(rows, u):
                if v in unseen:
                    unseen.remove(v)
                    queue.append(v)
                    component.append(v)
        components.append(sorted(component))
    return components


def canonical_upper_triangle_sha256(rows: Sequence[int]) -> str:
    bits = "".join(
        "1" if (rows[i] >> j) & 1 else "0"
        for i in range(len(rows))
        for j in range(i + 1, len(rows))
    )
    return hashlib.sha256(bits.encode("ascii")).hexdigest()


def triangle_count(rows: Sequence[int]) -> int:
    return sum(
        1
        for i, j, k in combinations(range(len(rows)), 3)
        if ((rows[i] >> j) & 1)
        and ((rows[i] >> k) & 1)
        and ((rows[j] >> k) & 1)
    )


def core_pair_codegrees(rows: Sequence[int]) -> dict[str, int]:
    histogram: Counter[str] = Counter()
    for i, j in combinations(range(len(rows)), 2):
        common = (rows[i] & rows[j]).bit_count()
        if (rows[i] >> j) & 1:
            key = f"edge:{common}"
        elif i // 12 == j // 12:
            key = f"same_fibre_nonedge:{common}"
        else:
            key = f"cross_fibre_nonedge:{common}"
        histogram[key] += 1
    return dict(sorted(histogram.items()))


def quotient_from_core(rows: Sequence[int]) -> tuple[list[list[int]], dict[str, object]]:
    """Contract each within-fibre matching edge to one of 18 labels."""
    n = len(rows)
    require(n == 36, "wrong core size")
    within_matchings: list[list[list[int]]] = []
    for fibre in range(3):
        offset = 12 * fibre
        expected = [[2 * i, 2 * i + 1] for i in range(6)]
        actual_edges = []
        for i, j in combinations(range(12), 2):
            if (rows[offset + i] >> (offset + j)) & 1:
                actual_edges.append([i, j])
        require(actual_edges == expected, f"fibre {fibre} is not the frozen matching")
        within_matchings.append(actual_edges)

    quotient_counts = [[0] * 18 for _ in range(18)]
    cross_edges_by_pair: Counter[str] = Counter()
    for u, v in combinations(range(36), 2):
        if not ((rows[u] >> v) & 1) or u // 12 == v // 12:
            continue
        fu, fv = u // 12, v // 12
        lu = 6 * fu + (u % 12) // 2
        lv = 6 * fv + (v % 12) // 2
        quotient_counts[lu][lv] += 1
        quotient_counts[lv][lu] += 1
        cross_edges_by_pair[f"{fu}-{fv}"] += 1

    maximum_multiplicity = max(max(row) for row in quotient_counts)
    require(maximum_multiplicity == 1, "doubled quotient edge found")
    quotient = [[1 if value else 0 for value in row] for row in quotient_counts]
    quotient_degrees = [sum(row) for row in quotient]
    require(set(quotient_degrees) == {4}, "quotient is not four-regular")
    require(
        cross_edges_by_pair == Counter({"0-1": 12, "0-2": 12, "1-2": 12}),
        "cross-fibre matchings do not each contain twelve edges",
    )
    block_degrees = {}
    for left, right in combinations(range(3), 2):
        values = []
        for u in range(6 * left, 6 * left + 6):
            values.append(sum(quotient[u][v] for v in range(6 * right, 6 * right + 6)))
        for v in range(6 * right, 6 * right + 6):
            values.append(sum(quotient[v][u] for u in range(6 * left, 6 * left + 6)))
        block_degrees[f"{left}-{right}"] = sorted(set(values))
        require(set(values) == {2}, f"quotient block {left}-{right} is not two-regular")

    return quotient, {
        "within_fibre_matchings": within_matchings,
        "cross_edges_by_fibre_pair": dict(sorted(cross_edges_by_pair.items())),
        "maximum_quotient_edge_multiplicity": maximum_multiplicity,
        "quotient_degree_set": sorted(set(quotient_degrees)),
        "quotient_bipartite_block_degree_sets": block_degrees,
    }


def local_rank_bridge(quotient: Sequence[Sequence[int]]) -> dict[str, object]:
    """Validate the 6+6+6 hypotheses and check the bordered-rank identity."""
    n = len(quotient)
    require(n == 18 and all(len(row) == n for row in quotient), "P must be 18-square")
    require(
        all(quotient[i][j] in (0, 1) for i in range(n) for j in range(n)),
        "P is not binary",
    )
    require(
        all(quotient[i][i] == 0 for i in range(n))
        and all(quotient[i][j] == quotient[j][i] for i in range(n) for j in range(n)),
        "P is not a simple undirected graph",
    )
    require(all(sum(row) == 4 for row in quotient), "P is not four-regular")
    for part in range(3):
        block = range(6 * part, 6 * part + 6)
        require(
            all(quotient[i][j] == 0 for i in block for j in block),
            "P has a within-part edge",
        )
    for left, right in combinations(range(3), 2):
        left_block = range(6 * left, 6 * left + 6)
        right_block = range(6 * right, 6 * right + 6)
        require(
            all(sum(quotient[i][j] for j in right_block) == 2 for i in left_block)
            and all(sum(quotient[j][i] for i in left_block) == 2 for j in right_block),
            "a bipartite quotient block is not two-regular",
        )

    identity = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    all_one = [[1] * n for _ in range(n)]
    ell = [[quotient[i][j] - identity[i][j] for j in range(n)] for i in range(n)]
    local_gram = [[0] * (n + 1) for _ in range(n + 1)]
    for j in range(n):
        local_gram[0][j + 1] = local_gram[j + 1][0] = 1
    for i in range(n):
        for j in range(n):
            local_gram[i + 1][j + 1] = all_one[i][j] + ell[i][j]

    # u=2*indicator(first part) witnesses L u = 1 and 1^T u=0.
    witness = [2 if i < 6 else 0 for i in range(n)]
    witness_image = mat_vec_mod(ell, witness)
    require(witness_image == [1] * n, "L u != 1")
    require(sum(witness) % P == 0, "1^T u != 0")
    require(mat_vec_mod(ell, [1] * n) == [0] * n, "L 1 != 0")

    rank_ell = rank_mod(ell)
    rank_local = rank_mod(local_gram)
    require(rank_ell == rank_local, "bordered local Gram rank differs from rank(P-I)")
    return {
        "matrix": "P-I over F_3",
        "quotient_parts": [6, 6, 6],
        "quotient_vertices": 18,
        "quotient_degree": 4,
        "each_bipartite_block_degree": 2,
        "witness_u": "2 times the indicator of the first six-point part",
        "L_u_equals_one": True,
        "one_transpose_u_mod_3": sum(witness) % P,
        "L_one_is_zero": True,
        "rank_P_minus_I_F3": rank_ell,
        "rank_local_19_gram_F3": rank_local,
        "rank_equality_kernel_argument": (
            "For D_T=[[0,1^T],[1,J+L]], kernel equations give 1^T x=0 "
            "and Lx=-a1. With Lu=1 and 1^Tu=0, (a,x) maps bijectively "
            "to x+a*u in ker(L); hence nullity(D_T)=nullity(L)+1."
        ),
        "global_scope": (
            "D_T is only a principal submatrix of D, so this proves "
            "rank(P_T-I)<=rank(D)=r3-1, never equality with the global rank."
        ),
    }


def required_bbt(rows: Sequence[int]) -> tuple[list[list[int]], dict[str, object]]:
    """Build 12I-A+2J-RR^T-A^2 exactly for the frozen core."""
    n = len(rows)
    a = [[(rows[i] >> j) & 1 for j in range(n)] for i in range(n)]
    a2 = [[sum(a[i][k] * a[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    gram = [
        [
            12 * (i == j)
            - a[i][j]
            + 2
            - (i // 12 == j // 12)
            - a2[i][j]
            for j in range(n)
        ]
        for i in range(n)
    ]
    rational_rank = rank_rational(gram)
    entries = Counter(value for row in gram for value in row)
    row_sums = [sum(row) for row in gram]
    diagonal = [gram[i][i] for i in range(n)]

    fibre_difference_vectors = [
        [1 if i < 12 else -1 if 12 <= i < 24 else 0 for i in range(n)],
        [1 if i < 12 else 0 if 12 <= i < 24 else -1 for i in range(n)],
    ]
    fibre_kernel = [
        [sum(row[j] * vector[j] for j in range(n)) for row in gram]
        for vector in fibre_difference_vectors
    ]
    constant_image = [sum(row) for row in gram]

    require(min(entries) >= 0, "required BB^T has a negative entry")
    require(set(diagonal) == {10}, "required BB^T diagonal is not ten")
    require(set(row_sums) == {60}, "required BB^T row sums are not sixty")
    require(all(all(value == 0 for value in image) for image in fibre_kernel), "fibre difference is not in kernel")
    require(set(constant_image) == {60}, "constant vector does not have eigenvalue sixty")
    require(rational_rank == 34, "required BB^T rational rank is not 34")

    return gram, {
        "formula": "12I-A_X+2J-RR^T-A_X^2",
        "entry_histogram": {str(key): value for key, value in sorted(entries.items())},
        "entry_minimum": min(entries),
        "entry_maximum": max(entries),
        "diagonal_set": sorted(set(diagonal)),
        "row_sum_set": sorted(set(row_sums)),
        "rational_rank": rational_rank,
        "kernel_contains_two_fibre_differences": True,
        "constant_eigenvalue": 60,
        "positive_semidefinite_argument": (
            "The fibre-indicator space has eigenvalues 60,0,0 for this Gram. "
            "On its 33-dimensional orthogonal complement the Gram equals "
            "(3I-A_X)(4I+A_X). A_X is symmetric cubic, so its spectrum lies "
            "in [-3,3]; connectedness keeps eigenvalue 3 out of this "
            "complement. The product is therefore positive there."
        ),
        "positive_semidefinite": True,
    }


def individual_column_census(rows: Sequence[int]) -> dict[str, object]:
    allowed: list[list[tuple[int, int]]] = []
    for fibre in range(3):
        offset = 12 * fibre
        pairs = [
            (offset + i, offset + j)
            for i, j in combinations(range(12), 2)
            if not ((rows[offset + i] >> (offset + j)) & 1)
        ]
        require(len(pairs) == 60, f"fibre {fibre} does not have 60 allowed pairs")
        allowed.append(pairs)

    induced_matching_survivors = 0
    mixed_survivors = 0
    mixed_by_edges: Counter[int] = Counter()
    for triple in product(*allowed):
        selected_vertices = tuple(v for pair in triple for v in pair)
        selected_mask = sum(1 << v for v in selected_vertices)
        selected_degrees = {
            v: (rows[v] & selected_mask).bit_count() for v in range(36)
        }
        if any(selected_degrees[v] > 1 for v in selected_vertices):
            continue
        induced_matching_survivors += 1
        if any(
            2 - int(bool((selected_mask >> v) & 1)) - selected_degrees[v] < 0
            for v in range(36)
        ):
            continue
        mixed_survivors += 1
        internal_edges = sum(selected_degrees[v] for v in selected_vertices) // 2
        mixed_by_edges[internal_edges] += 1

    require(induced_matching_survivors == 183596, "induced-matching census drift")
    require(mixed_survivors == 152399, "mixed-cut census drift")
    require(
        mixed_by_edges == Counter({0: 52517, 1: 76540, 2: 22610, 3: 732}),
        "mixed-cut internal-edge histogram drift",
    )
    return {
        "scope": "individual six-point columns only; no simultaneous 60-column B",
        "raw_pair_triples": 60**3,
        "allowed_pairs_per_fibre": [len(x) for x in allowed],
        "induced_matching_survivors": induced_matching_survivors,
        "mixed_equation_survivors": mixed_survivors,
        "mixed_survivors_by_internal_X_edges": {
            str(key): value for key, value in sorted(mixed_by_edges.items())
        },
    }


def core_checks() -> dict[str, object]:
    rows = reconstruct_core()
    degrees = [row.bit_count() for row in rows]
    components = connected_components(rows)
    edge_count = sum(degrees) // 2
    triangles = triangle_count(rows)
    require(set(degrees) == {3}, "core is not cubic")
    require(len(components) == 1, "core is not connected")
    require(triangles == 0, "core is not triangle-free")

    quotient, quotient_metadata = quotient_from_core(rows)
    bridge = local_rank_bridge(quotient)
    _, gram_metadata = required_bbt(rows)
    census = individual_column_census(rows)
    return {
        "adjacency_rows_hex": list(CORE_ROWS_HEX),
        "canonical_upper_triangle_bits_sha256": canonical_upper_triangle_sha256(rows),
        "vertices": len(rows),
        "edges": edge_count,
        "degree_set": sorted(set(degrees)),
        "connected": len(components) == 1,
        "component_partition_in_fibre_units": [len(c) // 3 for c in components],
        "triangle_free": triangles == 0,
        "pair_codegree_histogram": core_pair_codegrees(rows),
        "quotient_contraction": quotient_metadata,
        "local_rank_bridge": bridge,
        "required_BBt": gram_metadata,
        "individual_block_census": census,
    }


def compare_submission(result: dict[str, object], path: Path) -> dict[str, object]:
    """Compare selected public claims; never import or execute discovery code."""
    submitted = json.loads(path.read_text(encoding="utf-8"))
    signed = submitted["signed_higher_order_counts"]
    centered = submitted["ternary_vertex_clique_centering"]
    control = submitted["frozen_local_positive_control"]
    checks = {
        "signed_four_cycle_imbalance": (
            result["signed_higher_order_counts"]["balanced_minus_unbalanced_support_four_cycles"],
            signed["balanced_minus_unbalanced_support_four_cycles"],
        ),
        "signed_non_simple_walks": (
            result["signed_higher_order_counts"]["nonsimple_closed_signed_walks_length_four"],
            signed["nonsimple_closed_signed_walks_length_four"],
        ),
        "centered_clique_rank": (
            result["ternary_centering"]["seven_clique_centered_gram_rank_F3"],
            centered["seven_clique_gram_rank"],
        ),
        "core_hash": (
            result["frozen_local_positive_control"]["canonical_upper_triangle_bits_sha256"],
            control["adjacency_sha256_upper_triangle_bits"],
        ),
        "local_rank": (
            result["frozen_local_positive_control"]["local_rank_bridge"]["rank_P_minus_I_F3"],
            control["quotient_P_minus_I_rank_F3"],
        ),
        "BBt_rank": (
            result["frozen_local_positive_control"]["required_BBt"]["rational_rank"],
            control["required_BBt_rational_rank"],
        ),
        "induced_census": (
            result["frozen_local_positive_control"]["individual_block_census"]["induced_matching_survivors"],
            control["individual_block_census"]["induced_matching_survivors"],
        ),
        "mixed_census": (
            result["frozen_local_positive_control"]["individual_block_census"]["mixed_equation_survivors"],
            control["individual_block_census"]["mixed_equation_survivors"],
        ),
    }
    mismatches = {
        key: {"independent": values[0], "submitted": values[1]}
        for key, values in checks.items()
        if values[0] != values[1]
    }
    require(not mismatches, f"submission comparison mismatches: {mismatches}")
    return {
        "source": str(path).replace("\\", "/"),
        "method": "JSON value comparison only; discovery Python was not imported or executed",
        "matched_fields": sorted(checks),
        "mismatches": mismatches,
    }


def build_result(submission: Path | None = None) -> dict[str, object]:
    positive_sign_control = signed_four_cycle_control((1, 1, 1, 1))
    negative_sign_control = signed_four_cycle_control((-1, 1, 1, 1))
    require(
        positive_sign_control["simple_contribution"] == 8
        and negative_sign_control["simple_contribution"] == -8,
        "signed-cycle orientation control failed",
    )
    result: dict[str, object] = {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED_CONDITIONAL_WITH_WORDING_QUALIFIER",
        "scope": (
            "Conditional prism-free n3=4158 endpoint: signed trace subtraction, "
            "ternary centering, fixed-base 19-triangle contraction, and one "
            "frozen 36-vertex local relaxation"
        ),
        "frozen_commit": BASE_COMMIT,
        "signed_higher_order_counts": signed_walk_counts(),
        "signed_cycle_hostile_controls": {
            "balanced_cycle": positive_sign_control,
            "unbalanced_cycle": negative_sign_control,
            "balanced_definition": "edge-sign product +1",
            "unbalanced_definition": "edge-sign product -1",
        },
        "ternary_centering": ternary_centering_checks(),
        "frozen_local_positive_control": core_checks(),
        "conclusion": {
            "signed_four_cycle_imbalance": "VERIFIED_CONDITIONAL",
            "ternary_centered_rank_drop": "VERIFIED_CONDITIONAL",
            "seven_clique_rank_wording": (
                "QUALIFIED: centered Gram rank 6; uncentered Gram rank 7"
            ),
            "fixed_triangle_rank_bridge": "VERIFIED_CONDITIONAL",
            "frozen_rank_ten_local_relaxation": "VERIFIED",
            "simultaneous_60_column_B": "UNKNOWN",
            "compatible_H": "UNKNOWN",
            "endpoint_excluded": False,
            "rank_twelve_boundary_excluded": False,
            "upper_bound_improved_below_4158": False,
            "novelty_or_priority": "UNKNOWN_NOT_AUDITED",
            "target_status": "UNKNOWN",
        },
        "limitations": [
            "All general identities are conditional on the frozen hypothetical n3=4158 endpoint premises.",
            "The signed four-cycle imbalance is necessary and is not a contradiction.",
            "The local contraction gives only rank(P_T-I)<=r3-1; it does not identify the global rank.",
            "The frozen core and individual-column census do not construct sixty compatible columns, H, a 99-vertex graph, or an endpoint.",
            "No endpoint exclusion, improved n3 bound, or novelty claim is made.",
        ],
    }
    if submission is not None:
        result["submission_comparison"] = compare_submission(result, submission)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--compare-submission", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_result(args.compare_submission)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify is not None:
        require(args.verify.read_text(encoding="utf-8") == rendered, "verification output drift")
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    if args.output is None and args.verify is None:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
