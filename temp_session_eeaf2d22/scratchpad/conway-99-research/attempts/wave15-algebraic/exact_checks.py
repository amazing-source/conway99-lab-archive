#!/usr/bin/env python3
"""Exact arithmetic checks for the Wave 15 spectral obstruction.

This script is deliberately independent of every Wave 14 computation artifact.
It checks only integer/rational consequences stated in the accompanying report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


V = 99
K = 14
LAMBDA = 1
MU = 2
POSITIVE_RESTRICTED_EIGENVALUE = 3
NEGATIVE_RESTRICTED_EIGENVALUE = -4


def encode_fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def induced_edge_upper_bound(vertex_count: int) -> Fraction:
    """Return the spectral upper bound on edges induced by vertex_count vertices."""

    m = vertex_count
    twice_edges = (
        Fraction(K * m * m, V)
        + POSITIVE_RESTRICTED_EIGENVALUE * (m - Fraction(m * m, V))
    )
    return twice_edges / 2


def check_srg_spectrum() -> dict[str, object]:
    # Restricted eigenvalues solve x^2 + (mu-lambda)x + (mu-k) = 0.
    assert MU - LAMBDA == 1
    assert MU - K == -12
    assert POSITIVE_RESTRICTED_EIGENVALUE**2 + POSITIVE_RESTRICTED_EIGENVALUE - 12 == 0
    assert NEGATIVE_RESTRICTED_EIGENVALUE**2 + NEGATIVE_RESTRICTED_EIGENVALUE - 12 == 0

    # The two restricted multiplicities sum to v-1 and make trace(A)=0.
    positive_multiplicity = 54
    negative_multiplicity = 44
    assert positive_multiplicity + negative_multiplicity == V - 1
    assert (
        K
        + POSITIVE_RESTRICTED_EIGENVALUE * positive_multiplicity
        + NEGATIVE_RESTRICTED_EIGENVALUE * negative_multiplicity
        == 0
    )
    return {
        "spectrum": {"14": 1, "3": positive_multiplicity, "-4": negative_multiplicity},
        "restricted_maximum": POSITIVE_RESTRICTED_EIGENVALUE,
    }


def check_active_point_cases() -> dict[str, object]:
    rows = []
    # The audited residual has 2*x2 + 3*x3 = 48. Hence x3 is even.
    for x3 in range(0, 17, 2):
        x2_numerator = 48 - 3 * x3
        assert x2_numerator >= 0 and x2_numerator % 2 == 0
        x2 = x2_numerator // 2
        m = x2 + x3
        assert m == 24 - x3 // 2
        assert 16 <= m <= 24

        forced_lower = 3 * m
        spectral_upper = induced_edge_upper_bound(m)
        assert Fraction(forced_lower) > spectral_upper
        rows.append(
            {
                "size_two_points": x2,
                "size_three_points": x3,
                "active_vertices": m,
                "forced_edge_lower_bound": forced_lower,
                "spectral_edge_upper_bound": encode_fraction(spectral_upper),
                "exact_gap": encode_fraction(Fraction(forced_lower) - spectral_upper),
            }
        )

    # In general, e(S) >= 3m and the spectral upper bound imply m >= 27.
    # After multiplying by 198m^{-1}, this is 594 <= 22m.
    assert Fraction(3 * 99, 11) == 27
    return {
        "incidence_equation": "2*x2 + 3*x3 = 48",
        "active_vertex_upper_bound": 24,
        "spectral_minimum_order_at_average_degree_six": 27,
        "cases": rows,
    }


def check_triangle_intersection_moments(project_n3: int = 48) -> dict[str, object]:
    """Check the exact triangle-intersection identities retained as a failed lane."""

    triangle_count = V * 7 // 3
    assert triangle_count == 231
    q_degree = 18

    # Q has spectrum 18^1, 7^54, 0^44, (-3)^132.
    q_spectrum = {18: 1, 7: 54, 0: 44, -3: 132}
    assert sum(q_spectrum.values()) == triangle_count
    assert sum(eigenvalue * multiplicity for eigenvalue, multiplicity in q_spectrum.items()) == 0
    assert (
        sum(eigenvalue**2 * multiplicity for eigenvalue, multiplicity in q_spectrum.items())
        == triangle_count * q_degree
    )

    # p(Q)=Q^3-4Q^2-21Q equals 18J. On 1, p(18)=18*231.
    assert 18**3 - 4 * 18**2 - 21 * 18 == 18 * triangle_count

    q3_diagonal = 4 * q_degree + 18
    assert q3_diagonal == 90
    q4_diagonal = 4 * q3_diagonal + 21 * q_degree + 18 * q_degree
    assert q4_diagonal == 1062

    # For a fixed triangle, a_i counts disjoint triangles joined by i cross-edges.
    # The two moment equations are sum i*a_i=216 and sum i^2*a_i=288,
    # whence a_2+3a_3=36.
    weighted_sum_i_a_i = q_degree**2 - q_degree - q_degree * 5
    weighted_sum_i_squared_a_i = q4_diagonal - q_degree**2 - q_degree * 5**2
    assert weighted_sum_i_a_i == 216
    assert weighted_sum_i_squared_a_i == 288
    assert weighted_sum_i_squared_a_i - weighted_sum_i_a_i == 72

    # At project n3=48, the audited r=16 all-q=2 profile has a_2=6,
    # a_3=10 on 16 active triangles and (a_2,a_3)=(0,12) on 215 inactive ones.
    active_triangles = 16
    inactive_triangles = triangle_count - active_triangles
    a2_active, a3_active = 6, 10
    a2_inactive, a3_inactive = 0, 12
    assert a2_active + 3 * a3_active == 36
    assert a2_inactive + 3 * a3_inactive == 36
    assert (active_triangles * a2_active + inactive_triangles * a2_inactive) // 2 == project_n3

    prism_pairs = (
        active_triangles * a3_active + inactive_triangles * a3_inactive
    ) // 2
    nonadjacent_pairs = triangle_count * (triangle_count - 1 - q_degree) // 2
    weighted_cross_edges = triangle_count * weighted_sum_i_a_i // 2
    one_cross_edge_pairs = weighted_cross_edges - 2 * project_n3 - 3 * prism_pairs
    zero_cross_edge_pairs = (
        nonadjacent_pairs - one_cross_edge_pairs - project_n3 - prism_pairs
    )
    assert (zero_cross_edge_pairs, one_cross_edge_pairs, project_n3, prism_pairs) == (
        2326,
        20742,
        48,
        1370,
    )

    return {
        "triangle_intersection_graph_spectrum": {
            "18": 1,
            "7": 54,
            "0": 44,
            "-3": 132,
        },
        "polynomial_identity": "Q^3 - 4 Q^2 - 21 Q = 18 J",
        "fixed_triangle_moments": {
            "weighted_sum_i_a_i": weighted_sum_i_a_i,
            "weighted_sum_i_squared_a_i": weighted_sum_i_squared_a_i,
            "consequence": "a2 + 3*a3 = 36",
        },
        "project_n3": project_n3,
        "global_disjoint_triangle_pair_counts_by_cross_edges": {
            "0": zero_cross_edge_pairs,
            "1": one_cross_edge_pairs,
            "2": project_n3,
            "3": prism_pairs,
        },
        "disposition": "consistent_nonnegative_counts_no_obstruction",
    }


def build_payload() -> dict[str, object]:
    payload = {
        "claim_boundary": {
            "conditional_project_n3_48_exclusion": "DERIVED_PENDING_INDEPENDENT_AUDIT",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
            "catalogue_index_warning": (
                "All n3 values here denote the project induced-N3 count; "
                "no catalogue index n_45 or n_48 is used."
            ),
        },
        "srg_spectrum_check": check_srg_spectrum(),
        "active_point_spectral_check": check_active_point_cases(),
        "triangle_intersection_failed_lane": check_triangle_intersection_moments(),
    }
    semantic_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["semantic_sha256"] = hashlib.sha256(semantic_bytes).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = build_payload()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
        print(f"semantic_sha256 {payload['semantic_sha256']}")


if __name__ == "__main__":
    main()
