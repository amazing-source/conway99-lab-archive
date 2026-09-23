#!/usr/bin/env python3
"""Exact Wave 65 rooted hypergraph-algebra checks.

This package separates necessary consequences of a hypothetical endpoint
residual graph from an explicitly scoped local positive control.  It never
uses a scaffold automorphism as an automorphism of the hypothetical graph.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

F = Fraction
HERE = Path(__file__).resolve().parent
ORDER = 84
BLOCKS = 140
TARGET_SPECTRUM = {12: 1, 3: 40, 0: 7, -2: 6, -4: 30}

# Rows are the common eigenspaces of the six rooted-scaffold orbitals.  This
# table is reconstructed below from the 84 labels; it is not an assumption of
# target symmetry.
ORBIT_MULTIPLICITIES = [1, 6, 7, 14, 21, 35]
ORBIT_VALENCIES = [1, 2, 1, 20, 20, 40]
ORBIT_EIGENMATRIX = [
    [1, 2, 1, 20, 20, 40],
    [1, 2, 1, 6, 6, -16],
    [1, 0, -1, 10, -10, 0],
    [1, 2, 1, -4, -4, 4],
    [1, -2, 1, 0, 0, 0],
    [1, 0, -1, -2, 2, 0],
]


def mate(a: int) -> int:
    return a ^ 1


def labels14() -> list[tuple[int, int]]:
    return [
        (a, b)
        for a, b in combinations(range(14), 2)
        if b != mate(a)
    ]


def signed_labels() -> list[tuple[int, int, int, int]]:
    return [
        (i, j, si, sj)
        for i, j in combinations(range(7), 2)
        for si in (-1, 1)
        for sj in (-1, 1)
    ]


def support(v: tuple[int, int, int, int]) -> frozenset[int]:
    return frozenset(v[:2])


def signed_coordinates(
    v: tuple[int, int, int, int],
) -> frozenset[tuple[int, int]]:
    i, j, si, sj = v
    return frozenset(((i, si), (j, sj)))


def orbital(u: tuple[int, int, int, int], v: tuple[int, int, int, int]) -> int:
    if u == v:
        return 0
    support_overlap = len(support(u) & support(v))
    coordinate_overlap = len(signed_coordinates(u) & signed_coordinates(v))
    if support_overlap == 2:
        return 1 if coordinate_overlap == 1 else 2
    if support_overlap == 1:
        return 3 if coordinate_overlap == 1 else 4
    return 5


def zero_matrix(rows: int, columns: int | None = None) -> list[list[int]]:
    if columns is None:
        columns = rows
    return [[0] * columns for _ in range(rows)]


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, column)) for column in bt] for row in a]


def transpose(a: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*a)]


def trace(a: list[list[int]]) -> int:
    return sum(a[i][i] for i in range(len(a)))


def matrix_moments(a: list[list[int]], maximum: int) -> dict[str, int]:
    power = [row[:] for row in a]
    result: dict[str, int] = {}
    for exponent in range(1, maximum + 1):
        result[str(exponent)] = trace(power)
        power = matmul(power, a)
    return result


def graph_from_edges(order: int, edges: set[tuple[int, int]]) -> list[list[int]]:
    a = zero_matrix(order)
    for x, y in edges:
        if x == y:
            raise AssertionError("loop")
        if x > y:
            x, y = y, x
        if a[x][y]:
            raise AssertionError("duplicate edge")
        a[x][y] = a[y][x] = 1
    return a


def edges_of(a: list[list[int]]) -> set[tuple[int, int]]:
    return {
        (i, j)
        for i in range(len(a))
        for j in range(i + 1, len(a))
        if a[i][j]
    }


def degrees(a: list[list[int]]) -> list[int]:
    return [sum(row) for row in a]


def triangle_count(a: list[list[int]]) -> int:
    count = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if not a[i][j]:
                continue
            count += sum(a[i][k] and a[j][k] for k in range(j + 1, len(a)))
    return count


def four_cycle_count(a: list[list[int]]) -> int:
    diagonal_pair_count = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            common = sum(a[i][k] and a[j][k] for k in range(len(a)))
            diagonal_pair_count += common * (common - 1) // 2
    if diagonal_pair_count % 2:
        raise AssertionError("four-cycle diagonal count is odd")
    return diagonal_pair_count // 2


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    a = [[value % prime for value in row] for row in matrix]
    rows = len(a)
    columns = len(a[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (r for r in range(pivot_row, rows) if a[r][column]),
            None,
        )
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        inverse = pow(a[pivot_row][column], -1, prime)
        a[pivot_row] = [(inverse * value) % prime for value in a[pivot_row]]
        for r in range(rows):
            if r != pivot_row and a[r][column]:
                scale = a[r][column]
                a[r] = [
                    (x - scale * y) % prime
                    for x, y in zip(a[r], a[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def fraction_text(value: F) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def verify_rooted_scaffold() -> dict[str, object]:
    labels = labels14()
    if len(labels) != ORDER or len(set(labels)) != ORDER:
        raise AssertionError("H does not have 84 edges")
    endpoint_incidence = zero_matrix(14, ORDER)
    for column, (a, b) in enumerate(labels):
        endpoint_incidence[a][column] = 1
        endpoint_incidence[b][column] = 1
    if [sum(row) for row in endpoint_incidence] != [12] * 14:
        raise AssertionError("H is not 12-regular")

    gram = matmul(transpose(endpoint_incidence), endpoint_incidence)
    q = zero_matrix(ORDER)
    for i in range(ORDER):
        for j in range(ORDER):
            expected = 2 if i == j else int(bool(set(labels[i]) & set(labels[j])))
            if gram[i][j] != expected:
                raise AssertionError("endpoint incidence Gram mismatch")
            if i != j:
                q[i][j] = gram[i][j]
    if degrees(q) != [22] * ORDER:
        raise AssertionError("line graph of H is not 22-regular")

    rhs = [
        [
            10 * int(i == j) + 2 - q[i][j]
            for j in range(ORDER)
        ]
        for i in range(ORDER)
    ]
    if degrees(rhs) != [156] * ORDER:
        raise AssertionError("rooted block-equation RHS row sum mismatch")

    signed = signed_labels()
    observed_valencies = [
        sum(orbital(signed[0], v) == relation for v in signed)
        for relation in range(6)
    ]
    if observed_valencies != ORBIT_VALENCIES:
        raise AssertionError("scaffold orbital valencies mismatch")
    for relation in range(6):
        relation_matrix = [
            [int(orbital(u, v) == relation) for v in signed]
            for u in signed
        ]
        observed_moments = matrix_moments(relation_matrix, 6)
        predicted_moments = {
            str(power): sum(
                multiplicity * eigenrow[relation] ** power
                for multiplicity, eigenrow in zip(
                    ORBIT_MULTIPLICITIES, ORBIT_EIGENMATRIX
                )
            )
            for power in range(1, 7)
        }
        if observed_moments != predicted_moments:
            raise AssertionError(("orbital spectrum mismatch", relation))

    return {
        "H": "K_14 minus 7 K_2",
        "H_order": 14,
        "H_degree": 12,
        "H_edge_count": len(labels),
        "residual_label_count": ORDER,
        "line_graph_degree": 22,
        "endpoint_incidence_shape": [14, ORDER],
        "block_equation": "B^2+B=10I+2J-Q",
        "block_equation_rhs_row_sum": 156,
        "orbital_valencies": ORBIT_VALENCIES,
        "orbital_multiplicities": ORBIT_MULTIPLICITIES,
    }


def target_moments() -> dict[str, int]:
    moments = {
        str(power): sum(
            multiplicity * eigenvalue**power
            for eigenvalue, multiplicity in TARGET_SPECTRUM.items()
        )
        for power in range(1, 7)
    }
    if moments != {
        "1": 0,
        "2": 1008,
        "3": 840,
        "4": 31752,
        "5": 227640,
        "6": 3138408,
    }:
        raise AssertionError("target spectral moments changed")
    if (moments["4"] - ORDER * 12 * 23) % 8:
        raise AssertionError("target four-cycle count is not integral")
    return moments


def averaged_hypergraph_psd() -> dict[str, object]:
    samples: dict[str, list[str]] = {}
    minimum: F | None = None
    for y in range(43):
        edge_counts = [F(0), F(0), F(y), F(84), F(84 - 2 * y), F(336 + y)]
        capacities = [
            F(ORDER * valency, 2) for valency in ORBIT_VALENCIES
        ]
        probabilities = [F(0)] + [
            edge_counts[r] / capacities[r] for r in range(1, 6)
        ]
        b_eigenvalues = [
            sum(F(row[r]) * probabilities[r] for r in range(6))
            for row in ORBIT_EIGENMATRIX
        ]
        # Actual-coordinate-intersecting selected edges are exactly orbital 3.
        t_eigenvalues = [F(row[3], 10) for row in ORBIT_EIGENMATRIX]
        p_eigenvalues = [
            b - t + 5 for b, t in zip(b_eigenvalues, t_eigenvalues)
        ]
        if any(value < 0 for value in p_eigenvalues):
            raise AssertionError(("negative averaged D+5I block", y))
        local_minimum = min(p_eigenvalues)
        minimum = local_minimum if minimum is None else min(minimum, local_minimum)
        if y in (0, 21, 42):
            samples[str(y)] = [fraction_text(value) for value in p_eigenvalues]
    return {
        "parameter": "integer y in [0,42]",
        "meaning": "same K7 support, both signs flipped residual-edge count",
        "averaged_T": "(1/10) A_orbital_3",
        "averaged_D_plus_5I_eigenvalue_samples": samples,
        "minimum_over_all_43_integer_parameters": fraction_text(minimum or F(0)),
        "negative_blocks": 0,
        "scope": "Necessary group-averaged PSD only; not a target construction.",
    }


def spectral_overlap_control() -> dict[str, object]:
    # Let w=tr(T E_3).  The first three mixed moments force the other traces.
    lower = F(64, 5)
    upper = F(16)
    w = F(14)
    overlaps = {
        "-4": -F(15, 8) * w,
        "-2": F(21, 4) * w - 72,
        "0": 70 - F(35, 8) * w,
        "3": w,
        "12": F(2),
    }
    multiplicities = {"-4": 30, "-2": 6, "0": 7, "3": 40, "12": 1}
    eigenvalues = {key: int(key) for key in overlaps}
    if not all(
        -2 * multiplicities[key] <= value <= 2 * multiplicities[key]
        for key, value in overlaps.items()
    ):
        raise AssertionError("T contraction positive control failed")
    for power, expected in ((0, 0), (1, 168), (2, 0)):
        observed = sum(
            F(eigenvalues[key] ** power) * value
            for key, value in overlaps.items()
        )
        if observed != expected:
            raise AssertionError(("mixed trace control", power, observed))
    p_traces = {
        key: F(eigenvalues[key] + 5) * multiplicities[key] - overlaps[key]
        for key in overlaps
    }
    if any(value < 0 for value in p_traces.values()):
        raise AssertionError("D+5I spectral-block trace control failed")
    mixed3 = 4032 + 105 * w
    mixed4 = 40320 - 315 * w
    if mixed4 + 3 * mixed3 != 52416:
        raise AssertionError("mixed minimal-polynomial identity failed")
    return {
        "definition": "w=tr(T E_3), where E_3 is the B-eigenvalue-3 projector",
        "necessary_interval_from_minus_2I_le_T_le_2I": [
            fraction_text(lower),
            fraction_text(upper),
        ],
        "integer_mixed_trace_bound": {
            "tr(B^3 T)_minimum": 5376,
            "tr(B^3 T)_maximum": 5712,
            "identity": "tr(B^4 T)+3 tr(B^3 T)=52416",
        },
        "exact_positive_control": {
            "w": fraction_text(w),
            "tr_T_E_lambda": {
                key: fraction_text(value) for key, value in overlaps.items()
            },
            "tr_(D+5I)_E_lambda": {
                key: fraction_text(value) for key, value in p_traces.items()
            },
            "tr(B^3 T)": fraction_text(mixed3),
            "tr(B^4 T)": fraction_text(mixed4),
        },
        "scope": "Scalar compression only; it does not realize compatible matrices.",
    }


def load_positive_control() -> dict[str, object]:
    return json.loads((HERE / "positive-control.json").read_text(encoding="utf-8"))


def verify_positive_control() -> dict[str, object]:
    control = load_positive_control()
    blocks = [tuple(block) for block in control["blocks"]]
    cycle = list(control["transition_cycle"])
    if len(blocks) != BLOCKS or any(len(set(block)) != 3 for block in blocks):
        raise AssertionError("positive-control block count or size")
    if len(cycle) != ORDER or set(cycle) != set(range(ORDER)):
        raise AssertionError("transition cycle is not Hamiltonian")

    z = zero_matrix(ORDER, BLOCKS)
    pair_owner: dict[tuple[int, int], int] = {}
    d_edges: set[tuple[int, int]] = set()
    for column, block in enumerate(blocks):
        for vertex in block:
            if not 0 <= vertex < ORDER:
                raise AssertionError("block vertex outside range")
            z[vertex][column] = 1
        for pair in combinations(sorted(block), 2):
            if pair in pair_owner:
                raise AssertionError("positive control is not linear")
            pair_owner[pair] = column
            d_edges.add(pair)
    if [sum(row) for row in z] != [5] * ORDER:
        raise AssertionError("positive control is not 5-regular")
    if [sum(row) for row in transpose(z)] != [3] * BLOCKS:
        raise AssertionError("positive control is not 3-uniform")

    d = graph_from_edges(ORDER, d_edges)
    if degrees(d) != [10] * ORDER or triangle_count(d) != BLOCKS:
        raise AssertionError("positive-control point graph local parameters")
    zzt = matmul(z, transpose(z))
    expected_zzt = [
        [d[i][j] + 5 * int(i == j) for j in range(ORDER)]
        for i in range(ORDER)
    ]
    if zzt != expected_zzt:
        raise AssertionError("ZZ^T != D+5I")

    r = matmul(transpose(z), z)
    for i in range(BLOCKS):
        r[i][i] -= 3
    if degrees(r) != [12] * BLOCKS or triangle_count(r) != 840:
        raise AssertionError("block-intersection graph parameters")
    for root in range(BLOCKS):
        neighbors = [v for v in range(BLOCKS) if r[root][v]]
        local_degrees = [
            sum(r[v][w] for w in neighbors) for v in neighbors
        ]
        if local_degrees != [3] * 12:
            raise AssertionError("block-intersection local graph is not 3K4")
        # A 3-regular graph on 12 vertices with four-vertex components is 3K4.
        unseen = set(neighbors)
        component_sizes = []
        while unseen:
            seed = unseen.pop()
            stack = [seed]
            size = 1
            while stack:
                v = stack.pop()
                new = {w for w in unseen if r[v][w]}
                unseen -= new
                stack.extend(new)
                size += len(new)
            component_sizes.append(size)
        if sorted(component_sizes) != [4, 4, 4]:
            raise AssertionError("block-intersection local components")

    t_edges = {
        tuple(sorted((cycle[i], cycle[(i + 1) % ORDER])))
        for i in range(ORDER)
    }
    if d_edges & t_edges:
        raise AssertionError("D and T are not edge-disjoint")
    t = graph_from_edges(ORDER, t_edges)
    b = [
        [d[i][j] + t[i][j] for j in range(ORDER)]
        for i in range(ORDER)
    ]
    if degrees(t) != [2] * ORDER or triangle_count(t):
        raise AssertionError("T is not a triangle-free 2-factor")
    if degrees(b) != [12] * ORDER or triangle_count(b) != BLOCKS:
        raise AssertionError("B=D+T local control has a mixed triangle")
    for root in range(ORDER):
        neighbors = [v for v in range(ORDER) if b[root][v]]
        local_degrees = sorted(
            sum(b[v][w] for w in neighbors) for v in neighbors
        )
        if local_degrees != [0, 0] + [1] * 10:
            raise AssertionError("local graph is not 5K2 plus 2K1")

    d_c4 = four_cycle_count(d)
    r_c4 = four_cycle_count(r)
    if r_c4 - d_c4 != 1260:
        raise AssertionError("four-cycle transfer identity failed")
    p_moments = matrix_moments(zzt, 4)
    expected_p_moments = {
        "1": 420,
        "2": 2940,
        "3": 23940,
        "4": 201180 + 8 * r_c4,
    }
    if p_moments != expected_p_moments:
        raise AssertionError("Gram moments through degree four failed")

    b_moments = matrix_moments(b, 6)
    target = target_moments()
    if b_moments == target:
        raise AssertionError("local positive control unexpectedly met all target moments")
    return {
        "certificate_sha256": canonical_sha256(control),
        "hypergraph": {
            "vertices": ORDER,
            "blocks": BLOCKS,
            "uniformity": 3,
            "vertex_degree": 5,
            "linear": True,
            "Berge_triangles_outside_point_stars": 0,
        },
        "point_graph_D": {
            "degree": 10,
            "edges": len(d_edges),
            "triangles": triangle_count(d),
            "four_cycles": d_c4,
        },
        "block_intersection_graph_R": {
            "order": BLOCKS,
            "degree": 12,
            "local_graph": "3K4",
            "triangles": triangle_count(r),
            "four_cycles": r_c4,
            "forced_point_clique_four_cycles": 1260,
        },
        "transition_T": {
            "cycle_lengths": [84],
            "degree": 2,
            "triangles": 0,
        },
        "local_sum_B": {
            "degree": 12,
            "triangles": BLOCKS,
            "local_graph": "5K2 disjoint union 2K1",
            "moments_through_6": b_moments,
            "target_moment_differences": {
                power: b_moments[power] - target[power] for power in target
            },
        },
        "gram_D_plus_5I": {
            "moments_through_4": p_moments,
            "factorization": "D+5I=ZZ^T",
        },
        "finite_field_ranks_Z": {
            str(prime): rank_mod(z, prime) for prime in (2, 3, 5, 7)
        },
        "disposition": "EXACT_POSITIVE_CONTROL_FOR_LOCAL_DECOMPOSITION_ONLY",
    }


def generic_hypergraph_consequences() -> dict[str, object]:
    target = target_moments()
    c4_b = (target["4"] - ORDER * 12 * 23) // 8
    if c4_b != 1071:
        raise AssertionError("target B four-cycle count")
    # Each of the 84 point-stars is a K5 in R, contributing 15 four-cycles.
    forced_r_c4 = ORDER * 15
    if forced_r_c4 != 1260:
        raise AssertionError("forced block-graph four-cycle count")
    return {
        "D": {
            "order": ORDER,
            "degree": 10,
            "edges": 420,
            "triangles": 140,
            "local_graph": "5K2",
            "identity": "D=ZZ^T-5I",
            "least_eigenvalue_bound": "lambda_min(D)>=-5",
        },
        "Z": {
            "shape": [84, 140],
            "row_sum": 5,
            "column_sum": 3,
            "rank_upper_bound_over_R": 84,
            "rank_upper_bound_mod_3": 83,
            "mod_3_reason": "Z^T 1=3*1=0",
        },
        "R": {
            "definition": "R=Z^T Z-3I",
            "order": 140,
            "degree": 12,
            "local_graph": "3K4",
            "least_eigenvalue_bound": "lambda_min(R)>=-3",
            "minus_3_multiplicity_lower_bound": 56,
            "moments_through_4": {
                "tr(R)": 0,
                "tr(R^2)": 1680,
                "tr(R^3)": 5040,
                "tr(R^4)": "38640+8*c4(R)",
            },
        },
        "D_plus_5I_moments": {
            "tr(P)": 420,
            "tr(P^2)": 2940,
            "tr(P^3)": 23940,
            "tr(P^4)": "201180+8*c4(R)",
        },
        "four_cycle_transfer": {
            "identity": "c4(R)=1260+c4(D)",
            "target_c4(B)": c4_b,
            "necessary_bounds_if_D_subset_B": {
                "c4(D)": [0, c4_b],
                "c4(R)": [forced_r_c4, forced_r_c4 + c4_b],
            },
        },
        "T_trace_moments_through_6": {
            "tr(T)": 0,
            "tr(T^2)": 168,
            "tr(T^3)": 0,
            "tr(T^4)": "504+8*c4(T)",
            "tr(T^5)": "10*c5(T)",
            "tr(T^6)": "1680+48*c4(T)+12*c6(T)",
        },
        "target_B_trace_moments_through_6": target,
    }


def build_result() -> dict[str, object]:
    scaffold = verify_rooted_scaffold()
    generic = generic_hypergraph_consequences()
    averaged = averaged_hypergraph_psd()
    overlaps = spectral_overlap_control()
    control = verify_positive_control()
    return {
        "format": "wave65-rooted-hypergraph-algebra-v1",
        "role": "proof_b",
        "claim_label": "DERIVED",
        "scope": (
            "Prism-free endpoint n3=4158: exact rooted hypergraph/transition "
            "decomposition, finite-field ranks, moments, scalar spectral "
            "coupling, and a deliberately weaker local positive control."
        ),
        "automorphism_policy": (
            "The rooted scaffold is reconstructed exactly. Group averaging is "
            "used only for universally valid PSD; no target automorphism is assumed."
        ),
        "rooted_scaffold": scaffold,
        "generic_hypergraph_consequences": generic,
        "averaged_psd_null_calibration": averaged,
        "scalar_spectral_overlap": overlaps,
        "local_positive_control": control,
        "result": {
            "disposition": "EXACT_NULL_RESULT_FOR_SCALAR_AND_AVERAGED_ROUTES",
            "strict_n3_upper_bound": "NOT_OBTAINED",
            "endpoint_n3_4158": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "new_exact_restrictions": [
                "The block-intersection graph R has local graph 3K4, least eigenvalue at least -3, and eigenvalue -3 with multiplicity at least 56.",
                "c4(R)=1260+c4(D), hence a target requires 1260<=c4(R)<=2331.",
                "64/5<=tr(T E_3)<=16, equivalently 5376<=tr(B^3 T)<=5712, with tr(B^4 T)+3tr(B^3 T)=52416.",
            ],
            "first_missing_invariant": (
                "The noncommutative two-root placement of the 140 columns of Z "
                "and the transition 2-factor T relative to the fixed scaffold Q, "
                "including the entrywise equation (T+D)^2+(T+D)=10I+2J-Q."
            ),
        },
        "limitations": [
            "This is discovery-agent work and cannot self-promote to VERIFIED.",
            "The explicit positive control satisfies only the unlabelled local decomposition; it fails the target B moments and is not a graph candidate.",
            "Averaged PSD feasibility does not lift to compatible 0/1 matrices.",
            "Finite-field rank statements are necessary conditions, not exclusions.",
            "No endpoint exclusion, strict upper bound, construction, novelty, or priority claim follows.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    actual = build_result()
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if actual != expected:
            raise AssertionError("frozen result differs from exact reconstruction")
        print(f"PASS: {args.verify}")
    elif args.json:
        print(json.dumps(actual, indent=2, sort_keys=True))
    else:
        print("PASS: rooted scaffold, hypergraph algebra, and local positive control")
        print("RESULT: exact scalar/averaged null result; endpoint remains UNKNOWN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
