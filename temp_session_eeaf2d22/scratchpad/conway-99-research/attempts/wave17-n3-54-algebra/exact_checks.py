#!/usr/bin/env python3
"""Exact arithmetic checks for the conditional n3=54 algebraic boundary."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path


def zeros(n, m=None):
    return [[0] * (n if m is None else m) for _ in range(n)]


def matmul(a, b):
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def matsub(a, b):
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def max_abs(a):
    return max(abs(x) for row in a for x in row)


def rank_mod(a, p):
    m = [[x % p for x in row] for row in a]
    nr, nc = len(m), len(m[0])
    rank = 0
    for col in range(nc):
        pivot = next((r for r in range(rank, nr) if m[r][col]), None)
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        inv = pow(m[rank][col], -1, p)
        m[rank] = [(x * inv) % p for x in m[rank]]
        for r in range(nr):
            if r != rank and m[r][col]:
                factor = m[r][col]
                m[r] = [
                    (x - factor * y) % p for x, y in zip(m[r], m[rank])
                ]
        rank += 1
        if rank == nr:
            break
    return rank


def adjacency(n, edges):
    a = zeros(n)
    for u, v in edges:
        a[u][v] = a[v][u] = 1
    return a


def profile_key(qs):
    c = Counter(qs)
    return " ".join(f"{q}^{c[q]}" for q in sorted(c))


def enumerate_profiles(total=36):
    raw = []
    for r in range(1, total // 2 + 1):
        max_q = (r - 1) // 3
        if max_q < 2:
            continue
        for qs in itertools.combinations_with_replacement(range(2, max_q + 1), r):
            if sum(qs) != total:
                continue
            degrees = tuple(r - 1 - 3 * q for q in qs)
            raw.append(
                {
                    "r": r,
                    "q": profile_key(qs),
                    "q_values": list(qs),
                    "K_degrees": profile_key(degrees),
                    "survives_dK_ge_4": min(degrees) >= 4,
                    "active_vertex_cap": (3 * r) // 2,
                }
            )
    return raw


def integer_partitions(n, min_part=3):
    def rec(rem, lower):
        if rem == 0:
            yield ()
        for x in range(lower, rem + 1):
            for tail in rec(rem - x, x):
                yield (x,) + tail

    return list(rec(n, min_part))


def modular_cycle_filter():
    rows = []
    for c_f in (1, 2, 3):
        threshold = 9 - 2 * c_f
        allowed = []
        rejected = []
        for parts in integer_partitions(27):
            radical = len(parts) + sum(x % 2 == 0 for x in parts)
            record = {"cycles": list(parts), "radical_nullity_F2": radical}
            (allowed if radical >= threshold else rejected).append(record)
        rows.append(
            {
                "F_component_count": c_f,
                "required_R_radical_nullity": threshold,
                "allowed_cycle_partitions": len(allowed),
                "rejected_cycle_partitions": len(rejected),
                "minimum_R_cycle_count_among_allowed": min(
                    len(x["cycles"]) for x in allowed
                ),
                "hamiltonian_R_rejected": [27] in [
                    x["cycles"] for x in rejected
                ],
            }
        )
    return rows


def hamming_relaxation():
    vertices = list(itertools.product(range(3), repeat=3))
    idx = {x: i for i, x in enumerate(vertices)}

    c_edges = []
    d_edges = []
    r_edges = []
    for i, x in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            y = vertices[j]
            diff = [k for k in range(3) if x[k] != y[k]]
            if len(diff) == 1:
                c_edges.append((i, j))
                (r_edges if diff[0] == 2 else d_edges).append((i, j))
    c = adjacency(27, c_edges)

    distance_three_triangles = set()
    for i, x in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            y = vertices[j]
            if all(a != b for a, b in zip(x, y)):
                z = tuple(3 - a - b for a, b in zip(x, y))
                tri = tuple(sorted((i, j, idx[z])))
                distance_three_triangles.add(tri)
    triples = sorted(distance_three_triangles)
    columns = [list(t) for t in triples for _ in range(2)]
    nmat = zeros(27, 72)
    for j, tri in enumerate(columns):
        for i in tri:
            nmat[i][j] = 1

    # Any 11-regular outside graph suffices for the quotient-degree relaxation.
    e_edges = set()
    for u in range(72):
        for delta in (1, 2, 3, 4, 5, 36):
            v = (u + delta) % 72
            e_edges.add(tuple(sorted((u, v))))
            if delta != 36:
                v = (u - delta) % 72
                e_edges.add(tuple(sorted((u, v))))
    emat = adjacency(72, sorted(e_edges))

    c2 = matmul(c, c)
    nnt = matmul(nmat, list(map(list, zip(*nmat))))
    target = zeros(27)
    for i in range(27):
        for j in range(27):
            target[i][j] = 12 * (i == j) - c[i][j] + 2
    xx_defect = matsub([[c2[i][j] + nnt[i][j] for j in range(27)] for i in range(27)], target)

    # Active triangles: row/column triples in each fixed third-coordinate layer.
    active_triangles = []
    for layer in range(3):
        for a in range(3):
            active_triangles.append(
                sorted(idx[(a, b, layer)] for b in range(3))
            )
        for b in range(3):
            active_triangles.append(
                sorted(idx[(a, b, layer)] for a in range(3))
            )
    h = zeros(18, 27)
    for i, tri in enumerate(active_triangles):
        for p in tri:
            h[i][p] = 1
    rmat = adjacency(27, r_edges)
    coverage = matmul(matmul(h, rmat), list(map(list, zip(*h))))
    coverage_hist = Counter(
        coverage[i][j] for i in range(18) for j in range(i + 1, 18)
    )

    duplicate_pairs = 0
    max_column_intersection = 0
    for a in range(72):
        sa = {i for i in range(27) if nmat[i][a]}
        for b in range(a + 1, 72):
            sb = {i for i in range(27) if nmat[i][b]}
            overlap = len(sa & sb)
            duplicate_pairs += overlap == 3
            max_column_intersection = max(max_column_intersection, overlap)

    cn = matmul(c, nmat)
    ne = matmul(nmat, emat)
    cross_target = [
        [2 - nmat[i][j] for j in range(72)] for i in range(27)
    ]
    cross_defect = matsub(
        [[cn[i][j] + ne[i][j] for j in range(72)] for i in range(27)],
        cross_target,
    )
    nt = list(map(list, zip(*nmat)))
    ntn = matmul(nt, nmat)
    e2 = matmul(emat, emat)
    yy_target = zeros(72)
    for i in range(72):
        for j in range(72):
            yy_target[i][j] = 12 * (i == j) - emat[i][j] + 2
    yy_defect = matsub(
        [[ntn[i][j] + e2[i][j] for j in range(72)] for i in range(72)],
        yy_target,
    )

    return {
        "schema": "wave17-hamming-quotient-xx-relaxation-v1",
        "claim_label": "CANDIDATE",
        "scope": (
            "Exact 27+72 degree-quotient and X-X SRG block identity only; "
            "not the cross or Y-Y block identities and not the exact active "
            "rectangle coverage."
        ),
        "X_vertex_coordinates": [list(x) for x in vertices],
        "C_edges": [list(e) for e in c_edges],
        "D_active_triangle_edges": [list(e) for e in d_edges],
        "R_edges": [list(e) for e in r_edges],
        "active_triangles": active_triangles,
        "outside_X_neighborhoods": columns,
        "E_11_regular_edges_for_quotient_only": [list(e) for e in sorted(e_edges)],
        "checks": {
            "C_degrees": sorted(Counter(sum(row) for row in c).items()),
            "N_row_degrees": sorted(Counter(sum(row) for row in nmat).items()),
            "N_column_degrees": sorted(
                Counter(sum(nmat[i][j] for i in range(27)) for j in range(72)).items()
            ),
            "E_degrees": sorted(Counter(sum(row) for row in emat).items()),
            "quotient_matrix": [[6, 8], [3, 11]],
            "XX_block_identity_max_abs_defect": max_abs(xx_defect),
            "cross_block_identity_max_abs_defect": max_abs(cross_defect),
            "YY_block_identity_max_abs_defect": max_abs(yy_defect),
            "C_spectrum_exact": {"6": 1, "3": 6, "0": 12, "-3": 8},
            "rank_F2_C": rank_mod(c, 2),
            "rank_F3_C": rank_mod(c, 3),
            "distance_three_triangle_count": len(triples),
            "duplicate_outside_neighborhood_pairs": duplicate_pairs,
            "max_distinct_outside_column_intersection": max_column_intersection,
            "support_coverage_HRHt_histogram": {
                str(k): v for k, v in sorted(coverage_hist.items())
            },
            "support_coverage_required_values": [0, 2],
        },
        "fatal_lift_objections": [
            "The 72 outside X-neighborhoods occur in 36 identical pairs; each pair already has three common X-neighbors, impossible in an SRG with lambda=1 and mu=2.",
            "H R H^T has entries outside {0,2}, so R is not the exact twofold active-rectangle support required by the n3 framework.",
            "The arbitrary 11-regular E witnesses quotient degrees only and fails the cross and Y-Y block identities.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    profiles = enumerate_profiles()
    survivors = [p for p in profiles if p["survives_dK_ge_4"]]
    pair_types = []
    for a in (2, 3, 4):
        for b in range(a, 5):
            fixed = 2 * (a + b)
            pair_types.append(
                {
                    "q_pair": [a, b],
                    "fixed_H_degree_sum": fixed,
                    "possible_size_two_point": fixed % 4 == 0,
                    "positive_support_neighbors": (
                        fixed // 4 if fixed % 4 == 0 else None
                    ),
                }
            )

    result = {
        "schema": "wave17-n3-54-algebra-exact-checks-v1",
        "claim_label": "UNKNOWN",
        "scope": "conditional n3=54 boundary reductions and exact relaxation checks",
        "profile_reduction": {
            "identity": "sum_T q(T)=2*n3/3=36",
            "raw_profile_count": len(profiles),
            "raw_profiles": profiles,
            "dK_ge_4_survivor_count": len(survivors),
            "survivors": survivors,
            "size_two_endpoint_table": pair_types,
            "spectrally_unexcluded_profile": {
                "r": 18,
                "q": "2^18",
                "active_vertex_order": 27,
            },
        },
        "equality_boundary": {
            "active_incidence_sum": 54,
            "no_singleton_active_vertex_cap": 27,
            "minimum_internal_degree": 6,
            "spectral_edge_bound_at_m_27": 81,
            "forced_internal_edges": 81,
            "forced_internal_regular_degree": 6,
            "forced_outside_X_degree": 3,
            "quotient_matrix": [[6, 8], [3, 11]],
            "block_shapes": {"C": [27, 27], "N": [27, 72], "E": [72, 72]},
            "block_identities": [
                "C^2+N*N^T=12I-C+2J",
                "C*N+N*E=2J-N",
                "N^T*N+E^2=12I-E+2J",
            ],
            "outside_neighborhood_design": {
                "blocks": 72,
                "block_size": 3,
                "point_replication": 8,
                "pair_multiplicity": "s_pq=2-C_pq-(C^2)_pq",
                "binary_exact_cover_variables": (
                    "z_T in {0,1} for each 3-subset T of X; "
                    "sum_{T contains p}z_T=8 and "
                    "sum_{T contains p,q}z_T=s_pq"
                ),
            },
            "triangle_census_parameterized_by_R_3cycles_t": {
                "XXX": "18+t",
                "XXY": "27-3t",
                "XYY": "81+3t",
                "YYY": "105-t",
                "range_t": [0, 9],
            },
        },
        "mod2_active_support_constraint": {
            "integer_identity": "H*R*H^T=2L",
            "mod2_consequence": "row(H) is totally isotropic for adjacency(R)",
            "rank_H": "18-c(F)",
            "nullity_R": "c(R)+number_of_even_R_cycles",
            "inequality": (
                "c(R)+number_of_even_R_cycles >= 9-2*c(F)"
            ),
            "cycle_partition_counts": modular_cycle_filter(),
        },
        "hamming_relaxation": hamming_relaxation(),
        "status": {
            "conditional_n3_54_exclusion": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "raw_profiles": len(profiles),
                "survivors": len(survivors),
                "boundary": "r=18,q=2^18,m=27",
                "hamming_xx_defect": result["hamming_relaxation"]["checks"][
                    "XX_block_identity_max_abs_defect"
                ],
                "status": "UNKNOWN",
            }
        )
    )


if __name__ == "__main__":
    main()
