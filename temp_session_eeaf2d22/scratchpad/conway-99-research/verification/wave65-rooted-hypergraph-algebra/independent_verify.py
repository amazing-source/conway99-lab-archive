#!/usr/bin/env python3
"""Clean-room exact verifier for the Wave 65 hypergraph-algebra package.

This program does not import or execute discovery code.  It reconstructs
the scaffold, orbital averages, scalar trace restrictions, and explicit
positive control from definitions.  Integer NumPy matrix multiplication is
used only where every intermediate is far below the signed 64-bit limit.
All rational calculations use fractions.Fraction.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter, deque
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np


F = Fraction
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DISCOVERY = REPO / "attempts" / "wave65-rooted-hypergraph-algebra"
N_POINTS = 84
N_BLOCKS = 140
TARGET_SPECTRUM = {-4: 30, -2: 6, 0: 7, 3: 40, 12: 1}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(raw)


def parse_fraction(text: str | int) -> F:
    return F(text)


def fraction_text(value: F) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def trace_powers(a: np.ndarray, maximum: int) -> dict[int, int]:
    """Return exact integer traces; safe here because values are < 2**63."""
    if a.dtype != np.int64 or a.shape[0] != a.shape[1]:
        raise AssertionError("expected a square int64 matrix")
    power = np.eye(a.shape[0], dtype=np.int64)
    out: dict[int, int] = {}
    for exponent in range(1, maximum + 1):
        power = power @ a
        if int(np.max(np.abs(power))) >= 2**62:
            raise AssertionError("int64 safety margin exhausted")
        out[exponent] = int(np.trace(power))
    return out


def degrees(a: np.ndarray) -> list[int]:
    return [int(x) for x in a.sum(axis=1)]


def triangle_count(a: np.ndarray) -> int:
    return int(np.trace(a @ a @ a)) // 6


def four_cycle_count(a: np.ndarray) -> int:
    common = a @ a
    diagonal_pairs = 0
    for i in range(a.shape[0]):
        for j in range(i + 1, a.shape[0]):
            c = int(common[i, j])
            diagonal_pairs += c * (c - 1) // 2
    if diagonal_pairs % 2:
        raise AssertionError("four-cycle diagonal count has wrong parity")
    return diagonal_pairs // 2


def adjacency(order: int, edges: set[tuple[int, int]]) -> np.ndarray:
    a = np.zeros((order, order), dtype=np.int64)
    for x, y in edges:
        if x == y:
            raise AssertionError("loop")
        x, y = sorted((x, y))
        if a[x, y]:
            raise AssertionError("duplicate edge")
        a[x, y] = a[y, x] = 1
    return a


def rank_mod(matrix: np.ndarray, prime: int) -> int:
    rows = [[int(x) % prime for x in row] for row in matrix.tolist()]
    nr = len(rows)
    nc = len(rows[0]) if nr else 0
    pivot = 0
    for column in range(nc):
        selected = next(
            (r for r in range(pivot, nr) if rows[r][column] % prime),
            None,
        )
        if selected is None:
            continue
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        inverse = pow(rows[pivot][column], -1, prime)
        rows[pivot] = [(inverse * x) % prime for x in rows[pivot]]
        for r in range(nr):
            if r == pivot:
                continue
            factor = rows[r][column]
            if factor:
                rows[r] = [
                    (x - factor * y) % prime
                    for x, y in zip(rows[r], rows[pivot])
                ]
        pivot += 1
        if pivot == nr:
            break
    return pivot


def mate(vertex: int) -> int:
    return vertex ^ 1


def rooted_scaffold() -> dict[str, object]:
    """Reconstruct H, its incidence Gram, Q, and the residual block RHS."""
    labels = [
        pair
        for pair in combinations(range(14), 2)
        if pair[1] != mate(pair[0])
    ]
    if len(labels) != 84:
        raise AssertionError("H edge count")
    incidence = np.zeros((14, 84), dtype=np.int64)
    for column, (a, b) in enumerate(labels):
        incidence[a, column] = 1
        incidence[b, column] = 1
    if degrees(incidence @ incidence.T - np.diag([12] * 14)) != [12] * 14:
        # This is A(H): off-diagonal incidence-row intersections.
        raise AssertionError("H adjacency reconstruction")
    if [int(x) for x in incidence.sum(axis=1)] != [12] * 14:
        raise AssertionError("H is not 12-regular")

    gram = incidence.T @ incidence
    q = gram - 2 * np.eye(84, dtype=np.int64)
    if not np.array_equal(q, q.T):
        raise AssertionError("Q not symmetric")
    if set(np.unique(q)) != {0, 1} or np.any(np.diag(q)):
        raise AssertionError("Q not a simple adjacency matrix")
    if degrees(q) != [22] * 84:
        raise AssertionError("line graph valency")

    identity = np.eye(84, dtype=np.int64)
    all_ones = np.ones((84, 84), dtype=np.int64)
    rhs_from_srg = 12 * identity + 2 * all_ones - gram
    stated_rhs = 10 * identity + 2 * all_ones - q
    if not np.array_equal(rhs_from_srg, stated_rhs):
        raise AssertionError("residual SRG block identity normalization")
    if [int(x) for x in stated_rhs.sum(axis=1)] != [156] * 84:
        raise AssertionError("residual block RHS row sum")

    # Derive Q's spectrum independently via an exact generic polynomial.
    q_moments = trace_powers(q, 4)
    expected_q_moments = {
        power: 22**power + 7 * 10**power + 6 * 8**power + 70 * (-2) ** power
        for power in range(1, 5)
    }
    if q_moments != expected_q_moments:
        raise AssertionError("Q spectrum")

    return {
        "h_order": 14,
        "h_degree": 12,
        "h_edges": len(labels),
        "residual_labels": len(labels),
        "q_degree": 22,
        "q_spectrum": {"22": 1, "10": 7, "8": 6, "-2": 70},
        "identity": "B^2+B=10I+2J-Q",
        "rhs_row_sum": 156,
    }


def signed_labels() -> list[tuple[int, int, int, int]]:
    return [
        (i, j, si, sj)
        for i, j in combinations(range(7), 2)
        for si in (-1, 1)
        for sj in (-1, 1)
    ]


def relation_index(
    u: tuple[int, int, int, int],
    v: tuple[int, int, int, int],
) -> int:
    if u == v:
        return 0
    support_u = {u[0], u[1]}
    support_v = {v[0], v[1]}
    signed_u = {(u[0], u[2]), (u[1], u[3])}
    signed_v = {(v[0], v[2]), (v[1], v[3])}
    support_overlap = len(support_u & support_v)
    signed_overlap = len(signed_u & signed_v)
    if support_overlap == 2:
        return 1 if signed_overlap == 1 else 2
    if support_overlap == 1:
        return 3 if signed_overlap == 1 else 4
    if support_overlap == 0:
        return 5
    raise AssertionError("unclassified signed pair")


def relation_matrices() -> list[np.ndarray]:
    labels = signed_labels()
    matrices = [
        np.zeros((len(labels), len(labels)), dtype=np.int64)
        for _ in range(6)
    ]
    for i, u in enumerate(labels):
        for j, v in enumerate(labels):
            matrices[relation_index(u, v)][i, j] = 1
    if sum(matrices).tolist() != np.ones((84, 84), dtype=np.int64).tolist():
        raise AssertionError("relations do not partition ordered pairs")
    return matrices


def exact_joint_spectrum(
    matrices: list[np.ndarray],
) -> list[dict[str, object]]:
    """Recover all six joint eigenspaces without a supplied eigenmatrix.

    A small integer linear combination has six visibly separated eigenvalues.
    Numerical diagonalization proposes those integers; the minimal-polynomial
    identity and polynomial spectral projectors are then checked exactly.
    """
    weights = [0, 1, 2, 3, 5, 11]
    c = sum((w * a for w, a in zip(weights, matrices)), start=np.zeros_like(matrices[0]))
    approximate = np.linalg.eigvalsh(c.astype(np.float64))
    rounded = [int(round(x)) for x in approximate]
    if max(abs(float(x) - r) for x, r in zip(approximate, rounded)) > 1e-7:
        raise AssertionError("generic-combination eigenvalue not integral")
    counter = Counter(rounded)
    eigenvalues = sorted(counter)
    if len(eigenvalues) != 6:
        raise AssertionError("generic combination did not split six spaces")

    identity = np.eye(84, dtype=np.int64)
    annihilator = identity.copy()
    for value in eigenvalues:
        annihilator = annihilator @ (c - value * identity)
    if np.any(annihilator):
        raise AssertionError("proposed exact minimal polynomial fails")

    lanes: list[dict[str, object]] = []
    for value in eigenvalues:
        numerator = identity.copy()
        denominator = 1
        for other in eigenvalues:
            if other == value:
                continue
            numerator = numerator @ (c - other * identity)
            denominator *= value - other
        numerator_trace = int(np.trace(numerator))
        if numerator_trace % denominator:
            raise AssertionError("projector rank not integral")
        multiplicity = numerator_trace // denominator
        if multiplicity != counter[value]:
            raise AssertionError("numerical and exact multiplicities differ")

        relation_eigenvalues: list[int] = []
        for a in matrices:
            trace_product = int(np.sum(a * numerator.T))
            divisor = denominator * multiplicity
            if trace_product % divisor:
                raise AssertionError("relation eigenvalue not integral")
            relation_value = trace_product // divisor
            if not np.array_equal(a @ numerator, relation_value * numerator):
                raise AssertionError("joint-eigenspace action mismatch")
            relation_eigenvalues.append(relation_value)
        lanes.append(
            {
                "generic_eigenvalue": value,
                "multiplicity": multiplicity,
                "relation_eigenvalues": relation_eigenvalues,
            }
        )
    if sum(int(lane["multiplicity"]) for lane in lanes) != 84:
        raise AssertionError("joint-space dimensions")
    return lanes


def averaged_psd_lanes() -> dict[str, object]:
    matrices = relation_matrices()
    valencies = degrees(matrices[0] * 0 + sum(matrices, start=np.zeros_like(matrices[0])))
    if valencies != [84] * 84:
        raise AssertionError("relation partition")
    relation_valencies = [degrees(a)[0] for a in matrices]
    if relation_valencies != [1, 2, 1, 20, 20, 40]:
        raise AssertionError("relation valencies")
    lanes = exact_joint_spectrum(matrices)

    samples: dict[str, list[str]] = {}
    all_values: dict[str, list[str]] = {}
    minimum: F | None = None
    negative: list[tuple[int, int, F]] = []
    capacities = [F(84 * k, 2) for k in relation_valencies]
    for y in range(43):
        b_edge_counts = [0, 0, y, 84, 84 - 2 * y, 336 + y]
        b_coefficients = [
            F(0) if r == 0 else F(b_edge_counts[r], capacities[r])
            for r in range(6)
        ]
        p_values: list[F] = []
        for lane_index, lane in enumerate(lanes):
            eig = [int(x) for x in lane["relation_eigenvalues"]]
            averaged_b = sum(
                b_coefficients[r] * eig[r] for r in range(1, 6)
            )
            averaged_t = F(eig[3], 10)
            p = F(5) + averaged_b - averaged_t
            p_values.append(p)
            if p < 0:
                negative.append((y, lane_index, p))
            minimum = p if minimum is None else min(minimum, p)
        texts = [fraction_text(x) for x in p_values]
        all_values[str(y)] = texts
        if y in (0, 21, 42):
            samples[str(y)] = texts
    if negative:
        raise AssertionError(f"negative averaged PSD lanes: {negative}")

    return {
        "relation_valencies": relation_valencies,
        "joint_lanes": lanes,
        "sample_eigenvalues": samples,
        "all_43_lane_eigenvalues": all_values,
        "minimum": fraction_text(minimum or F(0)),
        "negative_count": len(negative),
        "scope": "group-averaged necessary PSD only",
    }


def solve_fraction_system(
    matrix: list[list[F]], rhs: list[F]
) -> list[F]:
    augmented = [row[:] + [value] for row, value in zip(matrix, rhs)]
    nrows = len(augmented)
    ncols = len(matrix[0])
    row = 0
    pivots: list[int] = []
    for column in range(ncols):
        selected = next(
            (r for r in range(row, nrows) if augmented[r][column]),
            None,
        )
        if selected is None:
            continue
        augmented[row], augmented[selected] = augmented[selected], augmented[row]
        pivot = augmented[row][column]
        augmented[row] = [x / pivot for x in augmented[row]]
        for r in range(nrows):
            if r == row:
                continue
            factor = augmented[r][column]
            if factor:
                augmented[r] = [
                    x - factor * y
                    for x, y in zip(augmented[r], augmented[row])
                ]
        pivots.append(column)
        row += 1
    if len(pivots) != ncols:
        raise AssertionError("non-unique rational system")
    return [augmented[i][-1] for i in range(ncols)]


def scalar_coupling() -> dict[str, object]:
    """Derive affine projector traces from three mixed traces and regularity."""
    unknown_eigenvalues = [-4, -2, 0]
    coefficient_matrix = [
        [F(1) for _ in unknown_eigenvalues],
        [F(x) for x in unknown_eigenvalues],
        [F(x * x) for x in unknown_eigenvalues],
    ]

    def solve_at(w: F) -> dict[int, F]:
        # a_3=w and a_12=2.  The mixed traces for B^0,B^1,B^2 are 0,168,0.
        rhs = [
            F(0) - w - F(2),
            F(168) - 3 * w - 12 * F(2),
            F(0) - 9 * w - 144 * F(2),
        ]
        solved = solve_fraction_system(coefficient_matrix, rhs)
        return {
            -4: solved[0],
            -2: solved[1],
            0: solved[2],
            3: w,
            12: F(2),
        }

    at_zero = solve_at(F(0))
    at_one = solve_at(F(1))
    affine = {
        eigenvalue: (at_zero[eigenvalue], at_one[eigenvalue] - at_zero[eigenvalue])
        for eigenvalue in TARGET_SPECTRUM
    }
    expected_affine = {
        -4: (F(0), -F(15, 8)),
        -2: (-F(72), F(21, 4)),
        0: (F(70), -F(35, 8)),
        3: (F(0), F(1)),
        12: (F(2), F(0)),
    }
    if affine != expected_affine:
        raise AssertionError("projector-trace affine solution")

    lower: F | None = None
    upper: F | None = None
    bound_sources: list[dict[str, str]] = []
    for eigenvalue in sorted(TARGET_SPECTRUM):
        intercept, slope = affine[eigenvalue]
        rank = TARGET_SPECTRUM[eigenvalue]
        local_lower = -F(2 * rank)
        local_upper = F(2 * rank)
        if slope == 0:
            if not local_lower <= intercept <= local_upper:
                raise AssertionError("constant projector lane infeasible")
            continue
        candidates = [
            (local_lower - intercept) / slope,
            (local_upper - intercept) / slope,
        ]
        lane_lower, lane_upper = min(candidates), max(candidates)
        lower = lane_lower if lower is None else max(lower, lane_lower)
        upper = lane_upper if upper is None else min(upper, lane_upper)
        bound_sources.append(
            {
                "eigenvalue": str(eigenvalue),
                "lower": fraction_text(lane_lower),
                "upper": fraction_text(lane_upper),
            }
        )
    if (lower, upper) != (F(64, 5), F(16)):
        raise AssertionError("scalar contraction interval")

    def affine_mixed(power: int) -> tuple[F, F]:
        intercept = sum(
            F(eigenvalue**power) * affine[eigenvalue][0]
            for eigenvalue in TARGET_SPECTRUM
        )
        slope = sum(
            F(eigenvalue**power) * affine[eigenvalue][1]
            for eigenvalue in TARGET_SPECTRUM
        )
        return intercept, slope

    mixed3 = affine_mixed(3)
    mixed4 = affine_mixed(4)
    if mixed3 != (F(4032), F(105)):
        raise AssertionError("tr(B^3 T) affine expression")
    if mixed4 != (F(40320), -F(315)):
        raise AssertionError("tr(B^4 T) affine expression")
    if (mixed4[0] + 3 * mixed3[0], mixed4[1] + 3 * mixed3[1]) != (
        F(52416),
        F(0),
    ):
        raise AssertionError("mixed minimal-polynomial identity")

    w = F(14)
    overlaps = solve_at(w)
    p_traces = {
        eigenvalue: F(eigenvalue + 5) * multiplicity - overlaps[eigenvalue]
        for eigenvalue, multiplicity in TARGET_SPECTRUM.items()
    }
    if any(value < 0 for value in p_traces.values()):
        raise AssertionError("scalar positive control P trace")

    return {
        "affine_projector_traces": {
            str(eigenvalue): {
                "intercept": fraction_text(pair[0]),
                "w_coefficient": fraction_text(pair[1]),
            }
            for eigenvalue, pair in sorted(affine.items())
        },
        "interval_w": [fraction_text(lower), fraction_text(upper)],
        "bound_sources": bound_sources,
        "tr_B3T_range": [
            fraction_text(mixed3[0] + mixed3[1] * lower),
            fraction_text(mixed3[0] + mixed3[1] * upper),
        ],
        "identity": "tr(B^4 T)+3tr(B^3 T)=52416",
        "scalar_control_w": fraction_text(w),
        "scalar_control_tr_T_E": {
            str(key): fraction_text(value)
            for key, value in sorted(overlaps.items())
        },
        "scalar_control_tr_P_E": {
            str(key): fraction_text(value)
            for key, value in sorted(p_traces.items())
        },
        "scope": "scalar compression only; no compatible matrices supplied",
    }


def target_and_generic_moments() -> dict[str, object]:
    target = {
        power: sum(
            multiplicity * eigenvalue**power
            for eigenvalue, multiplicity in TARGET_SPECTRUM.items()
        )
        for power in range(1, 7)
    }
    expected = {
        1: 0,
        2: 1008,
        3: 840,
        4: 31752,
        5: 227640,
        6: 3138408,
    }
    if target != expected:
        raise AssertionError("target B spectral moments")
    target_c4 = (target[4] - 84 * 12 * 23) // 8
    if target_c4 != 1071:
        raise AssertionError("target B c4")

    # Independently brute-check the claimed 2-factor formulas on all single
    # cycles C_l, 4 <= l <= 84, which add over disjoint components.
    for length in range(4, 85):
        edges = {
            tuple(sorted((i, (i + 1) % length)))
            for i in range(length)
        }
        cycle = adjacency(length, edges)
        moments = trace_powers(cycle, 6)
        expected_cycle = {
            1: 0,
            2: 2 * length,
            3: 0,
            4: 6 * length + 8 * int(length == 4),
            5: 10 * int(length == 5),
            6: (
                20 * length
                + 48 * int(length == 4)
                + 12 * int(length == 6)
            ),
        }
        if moments != expected_cycle:
            raise AssertionError(("2-factor moment formula", length))
    return {
        "target_B_moments": {str(k): v for k, v in target.items()},
        "target_B_c4": target_c4,
        "generic_triangle_free_T_moments": {
            "1": "0",
            "2": "2n=168",
            "3": "0",
            "4": "6n+8c4=504+8c4",
            "5": "10c5",
            "6": "20n+48c4+12c6=1680+48c4+12c6",
        },
        "cycle_lengths_bruteforce_checked": [4, 84],
    }


def connected_component_sizes(a: np.ndarray, vertices: list[int]) -> list[int]:
    unseen = set(vertices)
    sizes: list[int] = []
    while unseen:
        seed = unseen.pop()
        queue = deque([seed])
        size = 1
        while queue:
            v = queue.popleft()
            reached = {w for w in unseen if a[v, w]}
            unseen.difference_update(reached)
            queue.extend(reached)
            size += len(reached)
        sizes.append(size)
    return sorted(sizes)


def positive_control() -> dict[str, object]:
    raw = json.loads((DISCOVERY / "positive-control.json").read_text(encoding="utf-8"))
    if raw.get("format") != "wave65-hypergraph-local-positive-control-v1":
        raise AssertionError("positive control format")
    blocks = [tuple(int(x) for x in block) for block in raw["blocks"]]
    cycle = [int(x) for x in raw["transition_cycle"]]
    if len(blocks) != 140 or any(len(block) != 3 for block in blocks):
        raise AssertionError("block shape/count")
    if any(len(set(block)) != 3 for block in blocks):
        raise AssertionError("repeated point within block")
    if len(cycle) != 84 or set(cycle) != set(range(84)):
        raise AssertionError("transition Hamilton cycle certificate")

    z = np.zeros((84, 140), dtype=np.int64)
    pair_owner: dict[tuple[int, int], int] = {}
    d_edges: set[tuple[int, int]] = set()
    for column, block in enumerate(blocks):
        if any(x < 0 or x >= 84 for x in block):
            raise AssertionError("block point outside range")
        for x in block:
            z[x, column] = 1
        for pair in combinations(sorted(block), 2):
            if pair in pair_owner:
                raise AssertionError("hypergraph not linear")
            pair_owner[pair] = column
            d_edges.add(pair)
    if [int(x) for x in z.sum(axis=1)] != [5] * 84:
        raise AssertionError("point degrees")
    if [int(x) for x in z.sum(axis=0)] != [3] * 140:
        raise AssertionError("block sizes")

    d = adjacency(84, d_edges)
    if degrees(d) != [10] * 84:
        raise AssertionError("D degree")
    if not np.array_equal(z @ z.T, d + 5 * np.eye(84, dtype=np.int64)):
        raise AssertionError("D+5I != ZZ^T")

    # Check that every D triangle is exactly one certificate block.
    triangles_d: set[tuple[int, int, int]] = set()
    for triple in combinations(range(84), 3):
        if d[triple[0], triple[1]] and d[triple[0], triple[2]] and d[triple[1], triple[2]]:
            triangles_d.add(triple)
    block_set = {tuple(sorted(block)) for block in blocks}
    if triangles_d != block_set:
        raise AssertionError("Berge triangle outside a point-star block")

    r = z.T @ z - 3 * np.eye(140, dtype=np.int64)
    if set(np.unique(r)) != {0, 1} or np.any(np.diag(r)):
        raise AssertionError("R not simple; linearity orientation error")
    if degrees(r) != [12] * 140:
        raise AssertionError("R degree")
    for root in range(140):
        neighborhood = [v for v in range(140) if r[root, v]]
        local_degrees = sorted(
            sum(int(r[v, w]) for w in neighborhood)
            for v in neighborhood
        )
        if local_degrees != [3] * 12:
            raise AssertionError("R local degree")
        if connected_component_sizes(r, neighborhood) != [4, 4, 4]:
            raise AssertionError("R local graph not 3K4")

    t_edges = {
        tuple(sorted((cycle[i], cycle[(i + 1) % 84])))
        for i in range(84)
    }
    if len(t_edges) != 84:
        raise AssertionError("transition cycle duplicate edge")
    if d_edges & t_edges:
        raise AssertionError("D/T overlap")
    t = adjacency(84, t_edges)
    b = d + t
    if degrees(t) != [2] * 84 or triangle_count(t) != 0:
        raise AssertionError("T local properties")
    if degrees(b) != [12] * 84:
        raise AssertionError("B local degree")
    for root in range(84):
        neighborhood = [v for v in range(84) if b[root, v]]
        local_degrees = sorted(
            sum(int(b[v, w]) for w in neighborhood)
            for v in neighborhood
        )
        if local_degrees != [0, 0] + [1] * 10:
            raise AssertionError("B local graph not 5K2+2K1")

    d_c4 = four_cycle_count(d)
    r_c4 = four_cycle_count(r)
    if r_c4 - d_c4 != 1260:
        raise AssertionError("positive-control c4 transfer")
    d_moments = trace_powers(d, 4)
    r_moments = trace_powers(r, 4)
    p = z @ z.T
    p_moments = trace_powers(p, 4)
    if p_moments != {
        1: 420,
        2: 2940,
        3: 23940,
        4: 201180 + 8 * r_c4,
    }:
        raise AssertionError("positive-control P moments")

    # Nonzero Gram spectra give equal positive-power traces in both orientations.
    r_plus_3 = r + 3 * np.eye(140, dtype=np.int64)
    if trace_powers(r_plus_3, 4) != p_moments:
        raise AssertionError("Gram trace orientation")

    b_moments = trace_powers(b, 6)
    target = target_and_generic_moments()["target_B_moments"]
    deltas = {
        exponent: b_moments[exponent] - int(target[str(exponent)])
        for exponent in range(1, 7)
    }
    expected_deltas = {1: 0, 2: 0, 3: 0, 4: 5496, 5: -12020, 6: 239772}
    if deltas != expected_deltas:
        raise AssertionError("positive-control target-moment deltas")

    ranks = {prime: rank_mod(z, prime) for prime in (2, 3, 5, 7)}
    if ranks != {2: 84, 3: 83, 5: 84, 7: 84}:
        raise AssertionError("positive-control finite-field ranks")
    if ranks[3] > 83:
        raise AssertionError("mod-3 kernel condition")

    return {
        "canonical_certificate_sha256": canonical_json_hash(raw),
        "block_count": len(blocks),
        "point_degrees": 5,
        "linear": True,
        "bergetriangles_outside_blocks": 0,
        "D": {
            "degree": 10,
            "triangles": len(triangles_d),
            "c4": d_c4,
            "moments": {str(k): v for k, v in d_moments.items()},
        },
        "R": {
            "degree": 12,
            "local_graph": "3K4",
            "triangles": triangle_count(r),
            "c4": r_c4,
            "moments": {str(k): v for k, v in r_moments.items()},
        },
        "T": {
            "cycle_lengths": [84],
            "degree": 2,
            "triangles": 0,
            "moments": {str(k): v for k, v in trace_powers(t, 6).items()},
        },
        "B": {
            "degree": 12,
            "local_graph": "5K2 disjoint union 2K1",
            "triangles": triangle_count(b),
            "moments": {str(k): v for k, v in b_moments.items()},
            "target_moment_deltas": {str(k): v for k, v in deltas.items()},
        },
        "P_moments": {str(k): v for k, v in p_moments.items()},
        "finite_field_ranks_Z": {str(k): v for k, v in ranks.items()},
        "scope": "unlabelled local relaxation only; not a target candidate",
    }


def generic_hypergraph_identities() -> dict[str, object]:
    """Check all scalar identities algebraically from degree/local parameters."""
    n_d, k_d, triangles_d = 84, 10, 140
    n_r, k_r, triangles_r = 140, 12, 840
    tr_d = {
        1: 0,
        2: n_d * k_d,
        3: 6 * triangles_d,
        4: f"{n_d * k_d * (2 * k_d - 1)}+8*c4(D)",
    }
    tr_r = {
        1: 0,
        2: n_r * k_r,
        3: 6 * triangles_r,
        4: f"{n_r * k_r * (2 * k_r - 1)}+8*c4(R)",
    }
    if tr_d != {1: 0, 2: 840, 3: 840, 4: "15960+8*c4(D)"}:
        raise AssertionError("generic D moments")
    if tr_r != {1: 0, 2: 1680, 3: 5040, 4: "38640+8*c4(R)"}:
        raise AssertionError("generic R moments")

    # P=D+5I and P shares nonzero spectral moments with R+3I.
    p_from_d_constant = (
        15960 + 20 * 840 + 150 * 840 + 625 * 84
    )
    p_from_r_constant = (
        38640 + 12 * 5040 + 54 * 1680 + 81 * 140
    )
    if (p_from_d_constant, p_from_r_constant) != (211260, 201180):
        raise AssertionError("fourth Gram moment constants")
    difference = (p_from_d_constant - p_from_r_constant) // 8
    if difference != 1260:
        raise AssertionError("c4 transfer constant")

    target_c4_b = target_and_generic_moments()["target_B_c4"]
    interval = [difference, difference + int(target_c4_b)]
    if interval != [1260, 2331]:
        raise AssertionError("target c4(R) interval")

    # Orientation and nullity: Z is 84x140, so nullity(Z) on block space >=56.
    rank_upper = min(84, 140)
    minus_three_multiplicity_lower = 140 - rank_upper
    if minus_three_multiplicity_lower != 56:
        raise AssertionError("R -3 multiplicity orientation")

    return {
        "D_moments": {str(k): v for k, v in tr_d.items()},
        "R_moments": {str(k): v for k, v in tr_r.items()},
        "P_moments": {
            "1": 420,
            "2": 2940,
            "3": 23940,
            "4": "201180+8*c4(R)",
        },
        "lambda_min_R": ">= -3",
        "multiplicity_R_minus_3": ">= 56",
        "c4_transfer": "c4(R)=1260+c4(D)",
        "target_c4_R_interval": interval,
    }


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise AssertionError(("malformed manifest line", line_number))
        digest, target = parts
        int(digest, 16)
        entries.append((digest.lower(), target))
    if len({target for _, target in entries}) != len(entries):
        raise AssertionError("duplicate manifest target")
    return entries


def manifest_audit() -> dict[str, object]:
    entries = parse_manifest(DISCOVERY / "package-manifest.sha256")
    observed: list[dict[str, str]] = []
    for expected, target in entries:
        if target.startswith("git:"):
            _, commit, git_path = target.split(":", 2)
            process = subprocess.run(
                ["git", "show", f"{commit}:{git_path}"],
                cwd=REPO,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            raw = process.stdout
        else:
            candidate = (REPO / target).resolve()
            if REPO.resolve() not in candidate.parents:
                raise AssertionError("manifest path escapes repository")
            raw = candidate.read_bytes()
        actual = sha256_bytes(raw)
        if actual != expected:
            raise AssertionError(("manifest mismatch", target, expected, actual))
        observed.append({"path": target, "sha256": actual})

    # The sealed package intentionally excludes its manifest from itself.
    package_files = {
        str(path.relative_to(REPO)).replace("\\", "/")
        for path in DISCOVERY.iterdir()
        if path.is_file() and path.name != "package-manifest.sha256"
    }
    local_manifest_targets = {
        target for _, target in entries if not target.startswith("git:")
    }
    if package_files != local_manifest_targets:
        raise AssertionError(
            (
                "manifest local coverage mismatch",
                sorted(package_files - local_manifest_targets),
                sorted(local_manifest_targets - package_files),
            )
        )
    return {
        "entries_verified": len(entries),
        "local_package_files_covered": len(package_files),
        "all_match": True,
        "entries": observed,
    }


def build_result() -> dict[str, object]:
    return {
        "format": "wave65-independent-verifier-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "Wave 65 exact rooted scaffold, generic hypergraph identities, "
            "scalar and averaged necessary relaxations, and explicitly local "
            "positive control only"
        ),
        "rooted_scaffold": rooted_scaffold(),
        "generic_hypergraph": generic_hypergraph_identities(),
        "target_and_T_moments": target_and_generic_moments(),
        "scalar_coupling": scalar_coupling(),
        "averaged_psd": averaged_psd_lanes(),
        "positive_control": positive_control(),
        "manifest": manifest_audit(),
        "limitations": [
            "No target automorphism was assumed; only a universally valid scaffold-group average was checked.",
            "The 43 PSD lanes and scalar projector traces are necessary relaxations, not matrix realizations.",
            "The explicit positive control is unlabelled and fails target moments; it is not a rooted residual graph.",
            "The initial preinspection inventory omitted hidden .gitattributes; this is recorded separately.",
            "Endpoint n3=4158, Conway-99, novelty, and priority remain UNKNOWN.",
        ],
    }


def main() -> int:
    result = build_result()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
