#!/usr/bin/env python3
"""Independent exact checks for the Wave 15 algebraic obstruction.

This module imports no discovery-lane code.  It checks the rational spectral
calculation, the finite active-point arithmetic, the delicate size-two
meeting/support separation, and the retained triangle-intersection moments.
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
RESTRICTED_MAX = 3
RESTRICTED_MIN = -4


class AuditFailure(AssertionError):
    """Raised when a required bridge premise is weakened or inconsistent."""


def integer_restricted_eigenvalues() -> tuple[int, int]:
    """Derive the two roots of x^2-(lambda-mu)x-(k-mu)."""

    roots = tuple(
        x
        for x in range(-K, K + 1)
        if x * x - (LAMBDA - MU) * x - (K - MU) == 0
    )
    if roots != (RESTRICTED_MIN, RESTRICTED_MAX):
        raise AuditFailure(f"unexpected restricted roots: {roots}")
    return roots


def spectrum() -> dict[int, int]:
    """Derive restricted multiplicities from dimension and trace."""

    negative, positive = integer_restricted_eigenvalues()
    multiplicities = []
    for positive_mult in range(V):
        negative_mult = V - 1 - positive_mult
        if K + positive * positive_mult + negative * negative_mult == 0:
            multiplicities.append((positive_mult, negative_mult))
    if multiplicities != [(54, 44)]:
        raise AuditFailure(f"unexpected multiplicity solutions: {multiplicities}")
    return {K: 1, positive: 54, negative: 44}


def twice_induced_edge_upper(vertex_count: int, restricted_max: int = 3) -> Fraction:
    """Return the exact upper bound on twice the induced edge count."""

    m = vertex_count
    return Fraction(restricted_max * m) + Fraction(
        (K - restricted_max) * m * m, V
    )


def twice_induced_edge_lower(vertex_count: int) -> Fraction:
    """Return the exact lower spectral bound on twice the induced edge count."""

    m = vertex_count
    return Fraction(RESTRICTED_MIN * m) + Fraction(
        (K - RESTRICTED_MIN) * m * m, V
    )


def required_order_for_average_degree(
    average_degree: int, restricted_max: int = 3
) -> Fraction:
    """Return the real threshold forced by the upper subset bound."""

    if average_degree <= restricted_max:
        return Fraction(0)
    return Fraction(V * (average_degree - restricted_max), K - restricted_max)


def certify_active_degree(
    point_size: int,
    *,
    lambda_unique_triangle: bool = True,
    support_degree_equals_size: bool = True,
    support_is_actual_adjacency: bool = True,
    support_graph_simple: bool = True,
    common_label_deleted: bool = True,
    residual_row_cap: int = 2,
    positive_h_degree: int = 4,
) -> int:
    """Certify the degree in G[X] supplied by one indexed active point.

    A return value is a proved lower bound.  Missing semantic premises raise
    ``AuditFailure`` rather than silently weakening the conclusion.
    """

    if point_size < 1:
        raise AuditFailure("active point must be nonempty")
    if not lambda_unique_triangle:
        raise AuditFailure("meeting vertices need not be distinct")

    meeting_neighbors = 2 * point_size
    if point_size >= 3:
        return meeting_neighbors

    if not support_degree_equals_size:
        raise AuditFailure("support degree is unavailable")
    if not support_is_actual_adjacency:
        raise AuditFailure("support edges need not contribute to G[X]")
    if not support_graph_simple:
        raise AuditFailure("support degree need not count distinct neighbors")
    if not common_label_deleted:
        raise AuditFailure("support/meeting overlap cannot be excluded")

    # For a meeting edge, deleting the common triangle leaves s-1 rows on
    # this endpoint.  At s=2 the exact row cap makes a four-crossing
    # impossible, so no R-neighbor can be one of the four meeting neighbors.
    maximum_meeting_crossing = (point_size - 1) * residual_row_cap
    if maximum_meeting_crossing >= positive_h_degree:
        raise AuditFailure("support/meeting overlap is not excluded")

    support_neighbors = point_size
    return meeting_neighbors + support_neighbors


def active_point_cases() -> list[dict[str, object]]:
    """Enumerate all size-two/size-three incidence solutions."""

    rows: list[dict[str, object]] = []
    for size_three in range(17):
        remainder = 48 - 3 * size_three
        if remainder < 0 or remainder % 2:
            continue
        size_two = remainder // 2
        active_vertices = size_two + size_three
        minimum_degree = min(
            certify_active_degree(size)
            for size, count in ((2, size_two), (3, size_three))
            if count
        )
        forced_edges = Fraction(minimum_degree * active_vertices, 2)
        upper_edges = twice_induced_edge_upper(active_vertices) / 2
        if not forced_edges > upper_edges:
            raise AuditFailure(
                f"no contradiction for x2={size_two}, x3={size_three}"
            )
        rows.append(
            {
                "x2": size_two,
                "x3": size_three,
                "m": active_vertices,
                "minimum_degree": minimum_degree,
                "forced_edges": forced_edges,
                "spectral_upper_edges": upper_edges,
                "gap": forced_edges - upper_edges,
            }
        )
    if [row["m"] for row in rows] != list(range(24, 15, -1)):
        raise AuditFailure("active-point enumeration mismatch")
    return rows


def triangle_intersection_moments() -> dict[str, object]:
    """Independently derive all retained triangle-graph moment claims."""

    triangles_per_vertex = K // 2
    triangle_count = V * triangles_per_vertex // 3
    if triangle_count != 231:
        raise AuditFailure("triangle count mismatch")

    # CC^T=7I+A has eigenvalues 21,10,3.  The nonzero eigenvalues
    # transfer to C^TC; subtracting 3I gives the Q spectrum.
    q_spectrum = {18: 1, 7: 54, 0: 44, -3: triangle_count - V}
    if q_spectrum[-3] != 132:
        raise AuditFailure("Q nullity shift mismatch")
    if sum(q_spectrum.values()) != triangle_count:
        raise AuditFailure("Q spectrum dimension mismatch")
    if sum(e * mult for e, mult in q_spectrum.items()) != 0:
        raise AuditFailure("Q trace mismatch")
    if sum(e * e * mult for e, mult in q_spectrum.items()) != 231 * 18:
        raise AuditFailure("Q second spectral moment mismatch")

    def polynomial(value: int) -> int:
        return value**3 - 4 * value**2 - 21 * value

    if any(polynomial(value) != 0 for value in (7, 0, -3)):
        raise AuditFailure("claimed Q polynomial does not kill restrictions")
    if Fraction(polynomial(18), triangle_count) != 18:
        raise AuditFailure("coefficient of J is not 18")

    q_degree = 18
    adjacent_common_neighbors = 5
    q3_diagonal = 4 * q_degree + 18
    q4_diagonal = (
        4 * q3_diagonal + 21 * q_degree + 18 * q_degree
    )
    first = (
        q_degree**2
        - q_degree
        - q_degree * adjacent_common_neighbors
    )
    second = (
        q4_diagonal
        - q_degree**2
        - q_degree * adjacent_common_neighbors**2
    )
    if (q3_diagonal, q4_diagonal, first, second) != (90, 1062, 216, 288):
        raise AuditFailure("fixed-triangle moment mismatch")
    if (second - first) // 2 != 36:
        raise AuditFailure("a2+3a3 consequence mismatch")

    active_count = 16
    inactive_count = triangle_count - active_count
    active = {"a2": 6, "a3": 10}
    inactive = {"a2": 0, "a3": 12}
    for values in (active, inactive):
        if values["a2"] + 3 * values["a3"] != 36:
            raise AuditFailure("local a2/a3 solution mismatch")
        a1 = first - 2 * values["a2"] - 3 * values["a3"]
        a0 = (
            triangle_count
            - 1
            - q_degree
            - a1
            - values["a2"]
            - values["a3"]
        )
        values["a1"] = a1
        values["a0"] = a0
        if min(values.values()) < 0:
            raise AuditFailure("negative local intersection count")

    pair_counts = {
        0: (active_count * active["a0"] + inactive_count * inactive["a0"]) // 2,
        1: (active_count * active["a1"] + inactive_count * inactive["a1"]) // 2,
        2: (active_count * active["a2"] + inactive_count * inactive["a2"]) // 2,
        3: (active_count * active["a3"] + inactive_count * inactive["a3"]) // 2,
    }
    if pair_counts != {0: 2326, 1: 20742, 2: 48, 3: 1370}:
        raise AuditFailure(f"global pair counts mismatch: {pair_counts}")
    if sum(pair_counts.values()) != triangle_count * 212 // 2:
        raise AuditFailure("disjoint-pair total mismatch")
    if sum(i * count for i, count in pair_counts.items()) != 231 * first // 2:
        raise AuditFailure("global cross-edge first moment mismatch")

    return {
        "q_spectrum": q_spectrum,
        "polynomial": "Q^3-4Q^2-21Q=18J",
        "first_moment": first,
        "second_moment": second,
        "active_local_counts": active,
        "inactive_local_counts": inactive,
        "pair_counts": pair_counts,
    }


def validate_submitted_artifact(path: Path) -> str:
    """Check the frozen JSON independently, including its semantic digest."""

    artifact = json.loads(path.read_text(encoding="utf-8"))
    semantic_sha = artifact.pop("semantic_sha256")
    encoded = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(encoded).hexdigest() != semantic_sha:
        raise AuditFailure("submitted semantic digest mismatch")

    if artifact["srg_spectrum_check"]["spectrum"] != {
        "14": 1,
        "3": 54,
        "-4": 44,
    }:
        raise AuditFailure("submitted target spectrum mismatch")
    if (
        artifact["active_point_spectral_check"][
            "spectral_minimum_order_at_average_degree_six"
        ]
        != 27
    ):
        raise AuditFailure("submitted subset threshold mismatch")
    moment_metadata = artifact["triangle_intersection_failed_lane"][
        "fixed_triangle_moments"
    ]
    expected_moment_keys = {
        "consequence",
        "weighted_sum_i_a_i",
        "weighted_sum_i_squared_a_i",
    }
    if set(moment_metadata) != expected_moment_keys:
        raise AuditFailure(
            f"submitted moment metadata keys mismatch: {sorted(moment_metadata)}"
        )
    if "sum_i_a_i" in moment_metadata or "sum_i_squared_a_i" in moment_metadata:
        raise AuditFailure("obsolete ambiguous moment key survived repair")
    if moment_metadata["weighted_sum_i_a_i"] != 216:
        raise AuditFailure("submitted first weighted moment mismatch")
    if moment_metadata["weighted_sum_i_squared_a_i"] != 288:
        raise AuditFailure("submitted second weighted moment mismatch")
    submitted_pairs = artifact["triangle_intersection_failed_lane"][
        "global_disjoint_triangle_pair_counts_by_cross_edges"
    ]
    if submitted_pairs != {"0": 2326, "1": 20742, "2": 48, "3": 1370}:
        raise AuditFailure("submitted global pair counts mismatch")
    return semantic_sha


def hostile_mutations() -> dict[str, str]:
    """Require the checker to reject weakened semantic or spectral bridges."""

    mutations = {
        "singleton_point_allowed": lambda: certify_active_degree(1),
        "support_not_actual_adjacency": lambda: certify_active_degree(
            2, support_is_actual_adjacency=False
        ),
        "support_multigraph": lambda: certify_active_degree(
            2, support_graph_simple=False
        ),
        "common_label_not_deleted": lambda: certify_active_degree(
            2, common_label_deleted=False
        ),
        "meeting_vertices_not_distinct": lambda: certify_active_degree(
            2, lambda_unique_triangle=False
        ),
        "crossing_cap_allows_four": lambda: certify_active_degree(
            2, residual_row_cap=4
        ),
    }
    results: dict[str, str] = {}
    for name, action in mutations.items():
        try:
            degree = action()
        except AuditFailure:
            results[name] = "REJECTED"
        else:
            # A singleton produces degree three rather than an exception.  It
            # is rejected because it cannot certify the required degree six.
            if name == "singleton_point_allowed" and degree < 6:
                results[name] = "REJECTED"
            else:
                raise AuditFailure(f"hostile mutation accepted: {name}")

    # With a weakened restricted maximum of four, m=24 is no longer
    # contradicted: the threshold drops to 99/5 < 24.
    if required_order_for_average_degree(6, restricted_max=4) >= 24:
        raise AuditFailure("weakened spectral mutation unexpectedly obstructs m=24")
    results["restricted_maximum_four"] = "REJECTED"
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact",
        type=Path,
        default=Path("attempts/wave15-algebraic/exact-checks.json"),
    )
    args = parser.parse_args()

    derived_spectrum = spectrum()
    cases = active_point_cases()
    moments = triangle_intersection_moments()
    semantic_sha = validate_submitted_artifact(args.artifact)
    mutations = hostile_mutations()

    assert required_order_for_average_degree(6) == 27
    assert twice_induced_edge_upper(24) / 2 == 68
    assert twice_induced_edge_lower(24) / 2 == Fraction(48, 11)
    assert cases[0]["forced_edges"] == 72

    print("independent Wave15 algebraic audit PASS")
    print(f"spectrum {derived_spectrum}")
    print("active cases 9/9 contradictory")
    print(f"triangle pair counts {moments['pair_counts']}")
    print(f"submitted semantic_sha256 {semantic_sha}")
    print(f"hostile mutations {len(mutations)}/{len(mutations)} rejected")


if __name__ == "__main__":
    main()
