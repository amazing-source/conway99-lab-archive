#!/usr/bin/env python3
"""Exact arithmetic accompaniment for the Wave 18 n3=57 structural lane.

This checker deliberately verifies only finite/arithmetic consequences of the
frozen audited premises.  It does not certify the human semantic bridges.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterator, Sequence


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_INPUTS = {
    "AGENTS.md": "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "verification/2026-07-23-wave16-n3-51-structural-audit.md":
        "99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6",
    "verification/2026-07-23-wave15-global-lift-audit.md":
        "edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_frozen_inputs() -> dict[str, str]:
    observed = {name: sha256(ROOT / name) for name in EXPECTED_INPUTS}
    if observed != EXPECTED_INPUTS:
        raise AssertionError(
            "frozen input mismatch:\n"
            + json.dumps({"expected": EXPECTED_INPUTS, "observed": observed},
                         indent=2, sort_keys=True)
        )
    return observed


def partitions(total: int, length: int, minimum: int = 2) -> Iterator[tuple[int, ...]]:
    """Yield nondecreasing positive-active q profiles."""
    if length == 0:
        if total == 0:
            yield ()
        return
    maximum = total // length
    for first in range(minimum, maximum + 1):
        for rest in partitions(total - first, length - 1, first):
            yield (first,) + rest


def d_k(profile: Sequence[int]) -> tuple[int, ...]:
    r = len(profile)
    return tuple(r - 1 - 3 * q for q in profile)


def admissible_profiles(total: int = 38) -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = []
    for r in range(1, total // 2 + 1):
        for profile in partitions(total, r):
            if min(d_k(profile), default=-1) >= 4:
                out.append(profile)
    return out


def multiplicities(values: Sequence[int]) -> str:
    groups = []
    for value, run in itertools.groupby(values):
        count = sum(1 for _ in run)
        groups.append(str(value) if count == 1 else f"{value}^{count}")
    return " ".join(groups)


def crossing_edge_counts(rows: int, columns: int) -> tuple[int, ...]:
    """Enumerate bipartite crossings with every degree in {0,2}."""
    counts: set[int] = set()
    cells = rows * columns
    for mask in range(1 << cells):
        row_degrees = [0] * rows
        column_degrees = [0] * columns
        for index in range(cells):
            if mask & (1 << index):
                row, column = divmod(index, columns)
                row_degrees[row] += 1
                column_degrees[column] += 1
        if all(value in (0, 2) for value in row_degrees + column_degrees):
            counts.add(mask.bit_count())
    return tuple(sorted(counts))


def size_two_support_count(q_left: int, q_right: int) -> int | None:
    """Number of positive endpoint-local H terms, or None if impossible."""
    fixed_sum = 2 * (q_left + q_right)
    if fixed_sum % 4:
        return None
    return fixed_sum // 4


def integer_partitions(total: int, maximum: int | None = None) -> Iterator[tuple[int, ...]]:
    """Yield decreasing integer partitions of total."""
    if total == 0:
        yield ()
        return
    if maximum is None or maximum > total:
        maximum = total
    for first in range(maximum, 0, -1):
        for rest in integer_partitions(total - first, first):
            yield (first,) + rest


def point_size_profiles(incidences: int, points: int) -> tuple[tuple[int, ...], ...]:
    """All point-size multisets >=2 with the requested incidence sum."""
    excess = incidences - 2 * points
    if excess < 0:
        return ()
    profiles = []
    for increments in integer_partitions(excess):
        sizes = tuple(sorted(
            tuple(2 + increment for increment in increments)
            + (2,) * (points - len(increments))
        ))
        profiles.append(sizes)
    return tuple(profiles)


def spectral_upper_degree_sum(m: int) -> Fraction:
    return Fraction(3 * m, 1) + Fraction(m * m, 9)


def maximum_even_integer_at_most(value: Fraction) -> int:
    floor = value.numerator // value.denominator
    return floor if floor % 2 == 0 else floor - 1


def compact_profile(profile: Sequence[int]) -> dict[str, object]:
    return {
        "r": len(profile),
        "q": multiplicities(profile),
        "d_K": multiplicities(sorted(d_k(profile))),
        "active_point_cap": 3 * len(profile) // 2,
    }


def build_results() -> dict[str, object]:
    frozen = check_frozen_inputs()
    profiles = admissible_profiles()

    assert len(profiles) == 9
    assert [len(profile) for profile in profiles] == [
        14, 15, 16, 17, 17, 17, 18, 18, 19
    ]
    assert all(sum(profile) == 38 for profile in profiles)
    assert all(all(q >= 2 for q in profile) for profile in profiles)
    assert all(min(d_k(profile)) >= 4 for profile in profiles)
    assert max(max(profile) for profile in profiles) == 4

    crossings = {
        "meeting_size2_size2_after_deletion_1x1": crossing_edge_counts(1, 1),
        "meeting_size2_size3_after_deletion_1x2": crossing_edge_counts(1, 2),
        "meeting_size3_size2_after_deletion_2x1": crossing_edge_counts(2, 1),
        "meeting_size3_size3_after_deletion_2x2": crossing_edge_counts(2, 2),
        "disjoint_size2_size2_2x2": crossing_edge_counts(2, 2),
        "disjoint_size3_size2_3x2": crossing_edge_counts(3, 2),
        "hostile_global_3x3": crossing_edge_counts(3, 3),
    }
    assert crossings["meeting_size2_size2_after_deletion_1x1"] == (0,)
    assert crossings["meeting_size2_size3_after_deletion_1x2"] == (0,)
    assert crossings["meeting_size3_size2_after_deletion_2x1"] == (0,)
    assert crossings["meeting_size3_size3_after_deletion_2x2"] == (0, 4)
    assert crossings["disjoint_size2_size2_2x2"] == (0, 4)
    assert crossings["disjoint_size3_size2_3x2"] == (0, 4)
    assert crossings["hostile_global_3x3"] == (0, 4, 6)

    size_two_pairs = {
        f"{left},{right}": size_two_support_count(left, right)
        for left in range(2, 5)
        for right in range(left, 5)
    }
    assert size_two_pairs == {
        "2,2": 2,
        "2,3": None,
        "2,4": 3,
        "3,3": 3,
        "3,4": None,
        "4,4": 4,
    }
    minimum_induced_degrees = {
        key: None if count is None else 4 + count
        for key, count in size_two_pairs.items()
    }
    assert all(
        degree is None or degree >= 6
        for degree in minimum_induced_degrees.values()
    )

    by_r: dict[int, list[tuple[int, ...]]] = {}
    for profile in profiles:
        by_r.setdefault(len(profile), []).append(profile)
    assert max(3 * r // 2 for r in by_r if r <= 17) == 25

    r18 = by_r[18]
    assert {tuple(sorted(profile)) for profile in r18} == {
        (2,) * 17 + (4,),
        (2,) * 16 + (3, 3),
    }
    assert point_size_profiles(54, 27) == ((2,) * 27,)
    # In the 2^16 3^2 profile, mixed q parity is forbidden at a size-two
    # point.  A simple cubic point graph cannot give each of two q=3 labels
    # three neighbors within their two-vertex class.
    assert size_two_support_count(2, 3) is None
    assert 2 - 1 < 3
    # In the 2^17 4 profile, every point through q=4 has pair (2,4):
    # four meeting neighbors plus three positive disjoint support neighbors.
    assert 4 + size_two_support_count(2, 4) == 7
    assert spectral_upper_degree_sum(27) == 162

    r19 = by_r[19]
    assert r19 == [(2,) * 19]
    m27_profiles = point_size_profiles(57, 27)
    m28_profiles = point_size_profiles(57, 28)
    assert m27_profiles == (
        (2,) * 26 + (5,),
        (2,) * 25 + (3, 4),
        (2,) * 24 + (3, 3, 3),
    )
    assert m28_profiles == ((2,) * 27 + (3,),)

    # At m=27 spectral equality makes G[X] 6-regular.  A size-four or
    # size-five point already has 8 or 10 meeting neighbors.  In the remaining
    # 3^3 2^24 case, a size-three point has fixed H-sum 12, while its only
    # possible positive meeting crossings are to the other two size-three
    # points, at most four each.
    assert 2 * 4 > 6 and 2 * 5 > 6
    assert 2 * sum((2, 2, 2)) == 12
    assert 2 * max(crossings["meeting_size3_size3_after_deletion_2x2"]) == 8
    assert 8 < 12

    # At m=28 there is one size-three point.  Its six meeting neighbors are
    # size two and contribute zero H-crossing.  Every positive disjoint 3x2
    # crossing contributes four, so fixed sum 12 requires three additional
    # induced neighbors and degree at least nine.  The global degree sum is
    # even, while the spectral upper bound permits at most 170.
    upper28 = spectral_upper_degree_sum(28)
    max_even28 = maximum_even_integer_at_most(upper28)
    assert upper28 == Fraction(1540, 9)
    assert max_even28 == 170
    assert 6 * 28 == 168
    assert 6 + 12 // 4 == 9
    assert maximum_even_integer_at_most(Fraction(6 * 28 + 3, 1)) == 170
    assert 172 > max_even28

    return {
        "status_boundary": {
            "conditional_n3_57": "EXCLUDED_DERIVED_NOT_INDEPENDENTLY_VERIFIED",
            "conway_99_target": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "frozen_inputs_sha256": frozen,
        "q_profile_count": len(profiles),
        "q_profiles": [compact_profile(profile) for profile in profiles],
        "crossing_edge_counts": {key: list(value) for key, value in crossings.items()},
        "size_two_q_pair_support_count": size_two_pairs,
        "size_two_q_pair_minimum_induced_degree": minimum_induced_degrees,
        "r_at_most_17": {
            "maximum_active_point_count": 25,
            "spectral_minimum_active_point_count_at_delta_6": 27,
            "outcome": "contradiction",
        },
        "r18": {
            "incidences": 54,
            "active_points": 27,
            "point_sizes": ["2^27"],
            "spectral_equality_degree": 6,
            "profile_2^16_3^2": "mixed parity forbidden; two odd labels cannot form a simple cubic component",
            "profile_2^17_4": "a point through q=4 has induced degree at least 7",
            "outcome": "contradiction",
        },
        "r19": {
            "q": "2^19",
            "incidences": 57,
            "m27_point_sizes": [multiplicities(profile) for profile in m27_profiles],
            "m27_spectral_equality_degree": 6,
            "m27_outcome": "contradiction in every point-size profile",
            "m28_point_sizes": [multiplicities(profile) for profile in m28_profiles],
            "m28_spectral_upper_degree_sum": str(upper28),
            "m28_maximum_even_degree_sum": max_even28,
            "m28_size3_minimum_induced_degree": 9,
            "m28_outcome": "contradiction",
        },
        "prospective_consequence_if_wave17_n3_54_is_separately_accepted": {
            "n3_lower_bound": 60,
            "induced_C6_lower_bound": 209346,
        },
        "limitations": [
            "finite arithmetic accompaniment, not a semantic proof certificate",
            "no global H-degree restriction",
            "no point-size upper bound",
            "no Wave 14 residual cap or support-graph identity",
            "no Wave 17 premise",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    results = build_results()
    rendered = json.dumps(results, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    if args.verify is not None:
        observed = args.verify.read_text(encoding="utf-8")
        if observed != rendered:
            raise AssertionError(f"result mismatch: {args.verify}")
    if args.output is None:
        print(rendered, end="")


if __name__ == "__main__":
    main()
