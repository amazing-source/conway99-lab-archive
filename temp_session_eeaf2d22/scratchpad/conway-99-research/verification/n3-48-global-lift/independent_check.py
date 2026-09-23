#!/usr/bin/env python3
"""Independent exact checker for the Wave 15 n3=48 global lift.

This module does not import any Wave 15 discovery code.  It checks the
arithmetic consequences of the audited semantic bridge:

* active-point profiles have at most 24 indexed original vertices;
* a size-two meeting crossing has H-degree zero under the labeled two-sided
  0/2 rule, so its two R-neighbors are new;
* the resulting induced minimum degree is at least six;
* both the SRG spectral bound and the outside second moment exclude all
  resulting point-size profiles; and
* the inherited divisibility and induced-C6 identity give the next bounds.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from itertools import product


V = 99
K = 14
LAMBDA = 1
MU = 2
ACTIVE_INCIDENCES = 48
MIN_INTERNAL_DEGREE = 6


def srg_restricted_eigenvalues(
    k: int = K, lam: int = LAMBDA, mu: int = MU
) -> tuple[int, int]:
    """Return the two integral restricted eigenvalues for this SRG."""

    # theta^2 - (lambda-mu) theta - (k-mu) = 0.
    discriminant = (lam - mu) ** 2 + 4 * (k - mu)
    root = math.isqrt(discriminant)
    if root * root != discriminant:
        raise ValueError("restricted eigenvalues are not integral")
    numerators = ((lam - mu) + root, (lam - mu) - root)
    if any(value % 2 for value in numerators):
        raise ValueError("restricted eigenvalues are not integral")
    return tuple(value // 2 for value in numerators)


def spectral_twice_edge_upper_bound(
    m: int,
    *,
    v: int = V,
    k: int = K,
    positive_restricted_eigenvalue: int = 3,
) -> Fraction:
    """Exact upper bound on 2e(X) from the positive restricted eigenvalue."""

    r = positive_restricted_eigenvalue
    return Fraction(k * m * m + r * (v * m - m * m), v)


def spectral_contradiction_gap(
    m: int,
    *,
    minimum_degree: int = MIN_INTERNAL_DEGREE,
    positive_restricted_eigenvalue: int = 3,
) -> Fraction:
    """Lower bound minus upper bound for 2e(X); positive means impossible."""

    lower = minimum_degree * m
    upper = spectral_twice_edge_upper_bound(
        m,
        positive_restricted_eigenvalue=positive_restricted_eigenvalue,
    )
    return Fraction(lower) - upper


def point_size_profiles() -> list[tuple[int, int, int]]:
    """All nonnegative solutions of 2*x2+3*x3=48."""

    rows: list[tuple[int, int, int]] = []
    for x_2 in range(ACTIVE_INCIDENCES // 2 + 1):
        for x_3 in range(ACTIVE_INCIDENCES // 3 + 1):
            if 2 * x_2 + 3 * x_3 == ACTIVE_INCIDENCES:
                rows.append((x_2, x_3, x_2 + x_3))
    return rows


def crossing_sizes_after_shared_label(
    left_point_size: int,
    right_point_size: int,
    *,
    delete_shared_label: bool = True,
    enforce_rows: bool = True,
    enforce_columns: bool = True,
) -> set[int]:
    """Enumerate crossing sizes allowed by the labeled 0/2 degree rule."""

    rows = left_point_size - int(delete_shared_label)
    columns = right_point_size - int(delete_shared_label)
    if rows < 0 or columns < 0:
        raise ValueError("invalid point size")
    result: set[int] = set()
    for bits in product((0, 1), repeat=rows * columns):
        matrix = [
            bits[index * columns : (index + 1) * columns]
            for index in range(rows)
        ]
        row_degrees = [sum(row) for row in matrix]
        column_degrees = [
            sum(matrix[row][column] for row in range(rows))
            for column in range(columns)
        ]
        if enforce_rows and any(degree not in (0, 2) for degree in row_degrees):
            continue
        if enforce_columns and any(
            degree not in (0, 2) for degree in column_degrees
        ):
            continue
        result.add(sum(bits))
    return result


def mandatory_neighbor_lower_bound(
    point_size: int,
    *,
    support_degree: int | None = None,
    possible_support_triangle_overlaps: int = 0,
) -> int:
    """Count distinct mandatory neighbors used by the semantic lift."""

    active_triangle_neighbors = 2 * point_size
    if support_degree is None:
        support_degree = point_size
    return (
        active_triangle_neighbors
        + support_degree
        - possible_support_triangle_overlaps
    )


def aggregate_moment_defect(m: int, total_excess: int, square_excess: int) -> int:
    """Cauchy defect after d_x=6+s_x, T=sum s_x, U=sum s_x^2."""

    t = total_excess
    u = square_excess
    return (
        -2 * m * (m - 27) * (m - 55)
        + (29 * m - 1287) * t
        - (V - m) * u
        - t * t
    )


def direct_moment_defect(internal_degrees: tuple[int, ...]) -> int:
    """Compute N*sum(outside degrees^2)-sum(outside degrees)^2."""

    m = len(internal_degrees)
    degree_sum = sum(internal_degrees)
    outside_incidence_sum = K * m - degree_sum
    outside_square_sum = (
        2 * m * m
        + 12 * m
        - sum(degree * degree + degree for degree in internal_degrees)
    )
    return (V - m) * outside_square_sum - outside_incidence_sum**2


def next_multiple_strictly_above(value: int, divisor: int) -> int:
    return ((value // divisor) + 1) * divisor


def verify() -> dict[str, object]:
    eigenvalues = srg_restricted_eigenvalues()
    assert eigenvalues == (3, -4)

    profiles = point_size_profiles()
    assert profiles == [
        (0, 16, 16),
        (3, 14, 17),
        (6, 12, 18),
        (9, 10, 19),
        (12, 8, 20),
        (15, 6, 21),
        (18, 4, 22),
        (21, 2, 23),
        (24, 0, 24),
    ]

    # A meeting edge at a size-two point leaves one labeled crossing row.
    # With the two-sided 0/2 rule every such crossing is empty, for either
    # possible size of the other point.
    crossing_results = {
        str(right_size): sorted(
            crossing_sizes_after_shared_label(2, right_size)
        )
        for right_size in (2, 3)
    }
    assert crossing_results == {"2": [0], "3": [0]}

    # Therefore the R-neighbors at a size-two point cannot overlap the four
    # active-triangle neighbors.  A size-three point needs no support edge to
    # reach six.
    assert mandatory_neighbor_lower_bound(2, support_degree=2) == 6
    assert mandatory_neighbor_lower_bound(3, support_degree=0) == 6

    rows: list[dict[str, object]] = []
    for x_2, x_3, m in profiles:
        spectral_gap = spectral_contradiction_gap(m)
        assert m <= 24
        assert spectral_gap > 0

        base_defect = aggregate_moment_defect(m, 0, 0)
        assert base_defect < 0
        assert 29 * m - 1287 < 0
        assert -(V - m) < 0

        # Direct and expanded forms agree on the least dense degree sequence.
        direct_defect = direct_moment_defect((6,) * m)
        assert direct_defect == base_defect

        rows.append(
            {
                "x2": x_2,
                "x3": x_3,
                "m": m,
                "spectral_gap": {
                    "numerator": spectral_gap.numerator,
                    "denominator": spectral_gap.denominator,
                },
                "moment_defect_at_degree_six": base_defect,
            }
        )

    # The moment proof does not merely check the nine incidence profiles.
    # It excludes every positive m<=24 and every nonnegative aggregate excess.
    for m in range(1, 25):
        assert aggregate_moment_defect(m, 0, 0) < 0
        assert 29 * m - 1287 < 0
        for total_excess in range(0, 8 * m + 1):
            # U>=0, so U=0 is an intentionally generous upper bound.
            assert aggregate_moment_defect(m, total_excess, 0) < 0

    # Boundary and hostile-premise checks: the proof correctly stops at 27,
    # and either weakening the sixth neighbor or mutating r=3 destroys the
    # claimed m=24 contradiction.
    assert spectral_contradiction_gap(27) == 0
    assert spectral_contradiction_gap(24, minimum_degree=5) < 0
    assert (
        spectral_contradiction_gap(
            24, positive_restricted_eigenvalue=4
        )
        < 0
    )
    assert mandatory_neighbor_lower_bound(
        2, support_degree=2, possible_support_triangle_overlaps=1
    ) == 5

    # Retaining rather than deleting the shared active label admits an
    # H-degree-four 2-by-3 crossing, demonstrating that the deletion premise
    # is essential to the no-overlap bridge.
    assert 4 in crossing_sizes_after_shared_label(
        2, 3, delete_shared_label=False
    )

    n3_lower_bound = next_multiple_strictly_above(48, 3)
    induced_c6_lower_bound = 209_286 + n3_lower_bound
    assert n3_lower_bound == 51
    assert induced_c6_lower_bound == 209_337

    return {
        "status": "PASS",
        "restricted_eigenvalues": list(eigenvalues),
        "meeting_crossing_sizes_by_other_point_size": crossing_results,
        "point_size_profiles": rows,
        "all_m_from_1_through_24_moment_excluded": True,
        "spectral_boundary_m": 27,
        "conditional_n3_lower_bound": n3_lower_bound,
        "conditional_induced_c6_lower_bound": induced_c6_lower_bound,
        "target_result": "UNKNOWN",
        "novelty": "UNKNOWN",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
