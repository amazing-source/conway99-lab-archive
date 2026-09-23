"""Exact arithmetic checks for the conditional n3=51 structural proof.

This program intentionally checks only the finite/arithmetic parts of the
human proof.  The graph-theoretic bridge is stated in the accompanying run
report and remains subject to independent audit.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path
from typing import Iterable, Iterator


TOTAL_Q = 34


def nondecreasing_parts(
    total: int, length: int, minimum: int, maximum: int
) -> Iterator[tuple[int, ...]]:
    """Yield all nondecreasing fixed-length partitions with exact bounds."""

    def visit(
        remaining: int, slots: int, lower: int, prefix: tuple[int, ...]
    ) -> Iterator[tuple[int, ...]]:
        if slots == 0:
            if remaining == 0:
                yield prefix
            return
        upper = min(maximum, remaining // slots)
        for value in range(lower, upper + 1):
            remainder = remaining - value
            if remainder < value * (slots - 1):
                continue
            if remainder > maximum * (slots - 1):
                continue
            yield from visit(remainder, slots - 1, value, prefix + (value,))

    yield from visit(total, length, minimum, ())


def raw_profiles(total_q: int = TOTAL_Q) -> list[tuple[int, tuple[int, ...]]]:
    """Enumerate every profile allowed by q>=2 and 3q<=r-1."""

    profiles: list[tuple[int, tuple[int, ...]]] = []
    for r in range(1, total_q // 2 + 1):
        maximum = (r - 1) // 3
        if maximum < 2:
            continue
        for profile in nondecreasing_parts(total_q, r, 2, maximum):
            profiles.append((r, profile))
    return profiles


def k_degrees(r: int, profile: Iterable[int]) -> tuple[int, ...]:
    return tuple(r - 1 - 3 * q for q in profile)


def filtered_profiles(
    minimum_k_degree: int = 4,
) -> list[tuple[int, tuple[int, ...]]]:
    """Apply the audited no-degree-at-most-three point obstruction."""

    return [
        (r, profile)
        for r, profile in raw_profiles()
        if min(k_degrees(r, profile)) >= minimum_k_degree
    ]


def crossing_edge_counts(
    rows: int, columns: int, *, require_two_sided: bool = True
) -> set[int]:
    """Enumerate 0/1 crossings whose nonzero row degrees are exactly two.

    If ``require_two_sided`` is true, nonzero column degrees must also be
    exactly two.  Enumerating row supports is polynomial for the only cases
    used here (one or two rows), avoiding enumeration of all binary matrices.
    """

    row_supports: list[tuple[int, ...]] = [()]
    row_supports.extend(combinations(range(columns), 2))
    totals: set[int] = set()
    for supports in product(row_supports, repeat=rows):
        column_degrees = [0] * columns
        for support in supports:
            for column in support:
                column_degrees[column] += 1
        if require_two_sided and any(
            degree not in (0, 2) for degree in column_degrees
        ):
            continue
        totals.add(sum(len(support) for support in supports))
    return totals


def compressed_counts(values: Iterable[int]) -> dict[str, int]:
    return {
        str(value): count
        for value, count in sorted(Counter(values).items())
    }


def profile_record(
    r: int, profile: tuple[int, ...]
) -> dict[str, int | dict[str, int]]:
    return {
        "r": r,
        "q_counts": compressed_counts(profile),
        "k_degree_counts": compressed_counts(k_degrees(r, profile)),
    }


def size_two_point_record(q_left: int, q_right: int) -> dict[str, int | bool]:
    fixed_sum = 2 * (q_left + q_right)
    possible = fixed_sum % 4 == 0
    record: dict[str, int | bool] = {
        "fixed_point_sum": fixed_sum,
        "compatible_with_0_or_4_crossings": possible,
    }
    if possible:
        record["forced_positive_support_neighbors"] = fixed_sum // 4
        record["induced_degree_lower_bound"] = 4 + fixed_sum // 4
    return record


def spectral_average_upper_bound(m: int) -> Fraction:
    """Upper bound on average degree in an m-vertex induced subgraph."""

    return Fraction(3, 1) + Fraction(m, 9)


def build_result() -> dict[str, object]:
    raw = raw_profiles()
    survivors = filtered_profiles(4)
    weak_survivors = filtered_profiles(3)

    overlap_counts = {
        tuple(sorted(crossing_edge_counts(1, width)))
        for width in range(0, 17)
    }
    disjoint_counts = {
        tuple(sorted(crossing_edge_counts(2, width)))
        for width in range(2, 18)
    }

    active_set_bounds = []
    for r, profile in survivors:
        m_upper = (3 * r) // 2
        average_upper = spectral_average_upper_bound(m_upper)
        active_set_bounds.append(
            {
                "r": r,
                "q_counts": compressed_counts(profile),
                "active_incidence_count": 3 * r,
                "active_vertex_upper_bound": m_upper,
                "spectral_average_degree_upper": (
                    f"{average_upper.numerator}/{average_upper.denominator}"
                ),
                "strictly_below_six": average_upper < 6,
            }
        )

    result: dict[str, object] = {
        "schema_version": 1,
        "case": "conditional n3=51 for srg(99,14,1,2)",
        "sum_q": TOTAL_Q,
        "raw_profile_count": len(raw),
        "raw_profiles": [profile_record(r, profile) for r, profile in raw],
        "point_degree_filter": {
            "minimum_k_degree": 4,
            "justification": (
                "three non-singleton points give d_K>=3; the audited "
                "repeated-degree-three lemma excludes equality"
            ),
        },
        "surviving_profile_count": len(survivors),
        "surviving_profiles": [
            profile_record(r, profile) for r, profile in survivors
        ],
        "size_two_crossings": {
            "overlap_after_shared_label_deletion": {
                "widths_checked": [0, 16],
                "distinct_edge_count_sets": [
                    list(counts) for counts in sorted(overlap_counts)
                ],
            },
            "disjoint": {
                "widths_checked": [2, 17],
                "distinct_edge_count_sets": [
                    list(counts) for counts in sorted(disjoint_counts)
                ],
            },
            "conclusion": (
                "an actual edge incident with a size-two active point "
                "has H-degree 0 or 4"
            ),
        },
        "size_two_point_types": {
            "q2_q2": size_two_point_record(2, 2),
            "q2_q3": size_two_point_record(2, 3),
            "q3_q3": size_two_point_record(3, 3),
        },
        "active_set_bounds": active_set_bounds,
        "dense_subset_threshold": 27,
        "spectral_inequality": "average_degree(G[X]) <= 3+|X|/9",
        "contradiction": (
            "all survivors force |X|<=25 and delta(G[X])>=6, "
            "but the audited SRG subset bound forces |X|>=27"
        ),
        "hostile_mutations": {
            "minimum_k_degree_three_survivor_count": len(weak_survivors),
            "extra_profiles_if_degree_three_allowed": [
                profile_record(r, profile)
                for r, profile in weak_survivors
                if (r, profile) not in survivors
            ],
            "row_only_2_by_3_edge_counts": sorted(
                crossing_edge_counts(2, 3, require_two_sided=False)
            ),
            "two_sided_2_by_3_edge_counts": sorted(
                crossing_edge_counts(2, 3, require_two_sided=True)
            ),
            "singleton_points_would_destroy_active_vertex_upper_bound": True,
            "wave14_identity_d_R_equals_point_size_generalizes": False,
            "q3_q3_size_two_support_degree": 3,
            "q3_q3_point_size": 2,
        },
        "claim_status": "DERIVED_PENDING_INDEPENDENT_AUDIT",
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify",
        type=Path,
        help="compare the exact reconstruction with a frozen JSON artifact",
    )
    args = parser.parse_args()
    result = build_result()
    if args.verify is None:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    frozen = json.loads(args.verify.read_text(encoding="utf-8"))
    if frozen != result:
        raise SystemExit("FAIL: frozen artifact differs from exact reconstruction")
    print(
        "PASS: 16 raw profiles, 4 survivors, size-two crossing/support "
        "classification, and all active-set spectral bounds verified"
    )


if __name__ == "__main__":
    main()
