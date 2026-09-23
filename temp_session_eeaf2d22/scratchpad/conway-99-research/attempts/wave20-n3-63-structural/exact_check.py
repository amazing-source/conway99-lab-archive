#!/usr/bin/env python3
"""Exact arithmetic companion for the conditional Wave 20 n3=63 lane.

This checker deliberately contains no graph solver and uses only the Python
standard library.  It authenticates the audited pre-Wave-19 inputs, enumerates
the q-profiles and indexed-point size profiles, applies the exact SRG
inside/outside first and second moments, and checks the finite parity and
projector contradictions stated in the accompanying human report.

The checker is not a substitute for the semantic proof.  In particular, an
independent verifier must re-establish that the imported indexed-point and
crossing statements have exactly the quantifiers used here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Iterator


ROOT = Path(__file__).resolve().parents[2]

FROZEN_INPUTS = {
    "AGENTS.md": "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "CONJECTURE.md": "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "verification/2026-07-23-wave15-algebraic-audit.md":
        "b0541d05d2c1c359152b86223e2ebbdbd002b2ff42deb699f6a0b21d149a5b45",
    "verification/2026-07-23-wave16-n3-51-structural-audit.md":
        "99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6",
    "verification/2026-07-23-wave18-n3-57-structural-audit.md":
        "8534456ac92fd704ad7b24f5d7d2c262ea31476132018e9d14a8e4779b27ae5d",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate_inputs() -> dict[str, str]:
    observed = {}
    for relative, expected in FROZEN_INPUTS.items():
        actual = sha256_file(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"frozen input mismatch for {relative}: {actual} != {expected}"
            )
        observed[relative] = actual
    return observed


def partitions(
    total: int, minimum: int = 1, maximum: int | None = None
) -> Iterator[tuple[int, ...]]:
    """Yield nondecreasing positive integer partitions."""
    if total == 0:
        yield ()
        return
    if maximum is None:
        maximum = total
    for first in range(minimum, min(maximum, total) + 1):
        for tail in partitions(total - first, first, maximum):
            yield (first,) + tail


def fixed_length_partitions(
    total: int, length: int, minimum: int, maximum: int
) -> Iterator[tuple[int, ...]]:
    """Yield nondecreasing partitions with a fixed number of parts."""
    if length == 0:
        if total == 0:
            yield ()
        return
    upper = min(maximum, total // length)
    for first in range(minimum, upper + 1):
        for tail in fixed_length_partitions(
            total - first, length - 1, first, maximum
        ):
            yield (first,) + tail


def q_profiles(
    total_q: int = 42, minimum_dk: int = 4
) -> list[dict[str, object]]:
    """Enumerate active q-profiles under q>=2 and d_K=r-1-3q>=minimum_dk."""
    result = []
    for r in range(1, total_q // 2 + 1):
        maximum_q = (r - 1 - minimum_dk) // 3
        if maximum_q < 2:
            continue
        for profile in fixed_length_partitions(total_q, r, 2, maximum_q):
            dk = tuple(r - 1 - 3 * q for q in profile)
            assert min(dk) >= minimum_dk
            result.append({"r": r, "q": profile, "d_k": dk})
    return result


def point_size_profiles(m: int, incidence_sum: int) -> list[tuple[int, ...]]:
    """All nondecreasing point-size profiles with sizes at least two."""
    excess = incidence_sum - 2 * m
    if excess < 0:
        return []
    profiles = []
    for extra_parts in partitions(excess):
        if len(extra_parts) <= m:
            profiles.append(
                tuple([2] * (m - len(extra_parts)) + [2 + x for x in extra_parts])
            )
    return sorted(set(profiles))


def degree_lower_bound(point_size: int) -> int:
    """Imported endpoint-local lower bound for d_{G[X]} at a point."""
    if point_size == 2:
        return 6
    return 2 * point_size


def spectral_degree_sum_upper(m: int) -> Fraction:
    return Fraction(3 * m, 1) + Fraction(m * m, 9)


def group_degree_histograms(
    count: int, lower: int, slack: int
) -> set[tuple[int, ...]]:
    """Degree histograms for identical vertices, using small excess partitions."""
    if lower > 14:
        return set()
    histograms: set[tuple[int, ...]] = set()
    for extra_sum in range(slack + 1):
        for positive_extras in partitions(extra_sum):
            if len(positive_extras) > count:
                continue
            if positive_extras and positive_extras[-1] > 14 - lower:
                continue
            hist = [0] * 15
            hist[lower] = count - len(positive_extras)
            for extra in positive_extras:
                hist[lower + extra] += 1
            histograms.add(tuple(hist))
    return histograms


def add_histograms(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right))


def possible_degree_histograms(
    sizes: tuple[int, ...], maximum_sum: int
) -> set[tuple[int, ...]]:
    """All degree histograms consistent with the local lower bounds and d<=14."""
    lower_counts = Counter(degree_lower_bound(size) for size in sizes)
    minimum_sum = sum(lower * count for lower, count in lower_counts.items())
    if minimum_sum > maximum_sum or any(lower > 14 for lower in lower_counts):
        return set()
    total_slack = maximum_sum - minimum_sum
    states = {tuple([0] * 15)}
    used_minimum = 0
    for lower, count in sorted(lower_counts.items()):
        remaining_slack = maximum_sum - minimum_sum
        options = group_degree_histograms(count, lower, remaining_slack)
        next_states = set()
        for state in states:
            state_sum = sum(degree * multiplicity for degree, multiplicity in enumerate(state))
            for option in options:
                combined = add_histograms(state, option)
                combined_sum = sum(
                    degree * multiplicity
                    for degree, multiplicity in enumerate(combined)
                )
                if combined_sum + (
                    minimum_sum
                    - used_minimum
                    - lower * count
                ) <= maximum_sum:
                    next_states.add(combined)
        used_minimum += lower * count
        states = next_states
    return states


def histogram_sum(hist: tuple[int, ...]) -> int:
    return sum(degree * count for degree, count in enumerate(hist))


def histogram_square_sum(hist: tuple[int, ...]) -> int:
    return sum(degree * degree * count for degree, count in enumerate(hist))


def integer_square_minimum(count: int, total: int) -> int:
    """Minimum sum of squares of count nonnegative integers with fixed total."""
    quotient, remainder = divmod(total, count)
    return (
        (count - remainder) * quotient * quotient
        + remainder * (quotient + 1) * (quotient + 1)
    )


def bounded_integer_square_maximum(count: int, total: int, bound: int = 14) -> int:
    """Maximum square sum at fixed total when every entry is in [0,bound]."""
    if total < 0 or total > count * bound:
        return -1
    full, remainder = divmod(total, bound)
    if full > count or (full == count and remainder):
        return -1
    return full * bound * bound + remainder * remainder


def size_histogram(sizes: Iterable[int]) -> dict[str, int]:
    return {str(size): count for size, count in sorted(Counter(sizes).items())}


def degree_histogram(hist: tuple[int, ...]) -> dict[str, int]:
    return {str(degree): count for degree, count in enumerate(hist) if count}


def outside_moment_state(
    m: int, hist: tuple[int, ...]
) -> dict[str, object] | None:
    """Apply A^2=12I-A+2J and exact convex bounds to outside degrees."""
    inside_sum = histogram_sum(hist)
    inside_square_sum = histogram_square_sum(hist)
    if inside_sum % 2:
        return None
    outside_count = 99 - m
    outside_sum = 14 * m - inside_sum
    outside_square_sum = (
        12 * m - inside_sum + 2 * m * m - inside_square_sum
    )
    if outside_sum < 0 or outside_sum > 14 * outside_count:
        return None
    square_minimum = integer_square_minimum(outside_count, outside_sum)
    square_maximum = bounded_integer_square_maximum(
        outside_count, outside_sum, 14
    )
    if not (square_minimum <= outside_square_sum <= square_maximum):
        return None
    if (outside_square_sum - outside_sum) % 2:
        return None
    return {
        "inside_degree_sum": inside_sum,
        "inside_degree_square_sum": inside_square_sum,
        "outside_count": outside_count,
        "outside_degree_sum": outside_sum,
        "outside_degree_square_sum": outside_square_sum,
        "outside_square_minimum": square_minimum,
        "outside_square_maximum": square_maximum,
        "degree_histogram": degree_histogram(hist),
    }


def moment_survivors(m: int, incidence_sum: int) -> list[dict[str, object]]:
    upper = spectral_degree_sum_upper(m)
    maximum_sum = upper.numerator // upper.denominator
    survivors = []
    for sizes in point_size_profiles(m, incidence_sum):
        states = []
        for hist in possible_degree_histograms(sizes, maximum_sum):
            moment = outside_moment_state(m, hist)
            if moment is not None:
                states.append(moment)
        if states:
            states.sort(
                key=lambda row: (
                    row["inside_degree_sum"],
                    row["inside_degree_square_sum"],
                    tuple(
                        (int(k), v)
                        for k, v in row["degree_histogram"].items()
                    ),
                )
            )
            survivors.append(
                {
                    "sizes": size_histogram(sizes),
                    "degree_moment_states": states,
                }
            )
    return survivors


def crossing_weights(left_size: int, right_size: int, meeting: bool) -> tuple[int, ...]:
    """Possible crossing edge counts from the two-sided zero-or-two rule."""
    left = left_size - int(meeting)
    right = right_size - int(meeting)
    maximum_active = min(left, right)
    return tuple([0] + [2 * k for k in range(2, maximum_active + 1)])


def positive_weight_solutions(point_size: int) -> list[tuple[int, int]]:
    """Solutions 4*a+6*b=4*point_size used at size-three points."""
    target = 4 * point_size
    result = []
    for four_edges in range(target // 4 + 1):
        for six_edges in range(target // 6 + 1):
            if 4 * four_edges + 6 * six_edges == target:
                result.append((four_edges, six_edges))
    return result


def projector_contradiction_m30() -> dict[str, object]:
    """Exact Cauchy contradiction for the sole non-parity m=30 branch."""
    m = 30
    special_count = 3
    special_internal_edges = 3
    special_degree_lower = 8
    total_degree_lower = 27 * 6 + 3 * special_degree_lower

    z_m_z = (
        Fraction(3 * special_count, 1)
        - Fraction(2 * special_internal_edges, 1)
        + Fraction(special_count * special_count, 9)
    )
    one_m_one_upper = (
        Fraction(3 * m, 1)
        + Fraction(m * m, 9)
        - total_degree_lower
    )
    z_m_one_upper = (
        special_count * (Fraction(3, 1) + Fraction(m, 9))
        - special_count * special_degree_lower
    )
    lhs_lower = z_m_one_upper * z_m_one_upper
    rhs_upper = z_m_z * one_m_one_upper
    assert z_m_one_upper < 0
    assert lhs_lower > rhs_upper
    return {
        "psd_matrix": "3I-D+J/9",
        "special_vertices": special_count,
        "special_induced_edges": special_internal_edges,
        "special_degree_lower": special_degree_lower,
        "total_degree_sum_lower": total_degree_lower,
        "zMz": str(z_m_z),
        "oneMone_upper": str(one_m_one_upper),
        "zMone_upper": str(z_m_one_upper),
        "cauchy_lhs_lower": str(lhs_lower),
        "cauchy_rhs_upper": str(rhs_upper),
        "contradiction": True,
    }


def profile_key(sizes: dict[str, int]) -> str:
    parts_out = []
    for size, count in sorted((int(k), v) for k, v in sizes.items()):
        parts_out.append(str(size) if count == 1 else f"{size}^{count}")
    return " ".join(parts_out)


EXPECTED_MOMENT_PROFILE_STATE_COUNTS = {
    (54, 27): {"2^27": 1},
    (57, 27): {"2^24 3^3": 1},
    (57, 28): {"2^27 3": 1},
    (60, 27): {"2^21 3^6": 1},
    (60, 28): {"2^24 3^4": 1},
    (60, 29): {"2^28 4": 1, "2^27 3^2": 4},
    (60, 30): {"2^30": 13},
    (63, 27): {"2^18 3^9": 1},
    (63, 28): {"2^21 3^7": 1},
    (63, 29): {"2^24 3^5": 4, "2^25 3^3 4": 1},
    (63, 30): {"2^29 5": 1, "2^28 3 4": 9, "2^27 3^3": 13},
    (63, 31): {"2^30 3": 34},
}


EXPECTED_CRITICAL_DEGREE_HISTOGRAMS = {
    (54, 27, "2^27"): [{"6": 27}],
    (57, 27, "2^24 3^3"): [{"6": 27}],
    (57, 28, "2^27 3"): [{"6": 28}],
    (60, 27, "2^21 3^6"): [{"6": 27}],
    (60, 28, "2^24 3^4"): [{"6": 28}],
    (60, 29, "2^28 4"): [{"6": 28, "8": 1}],
    (60, 29, "2^27 3^2"): [
        {"6": 29},
        {"6": 28, "8": 1},
        {"6": 27, "7": 2},
        {"6": 25, "7": 4},
    ],
    (63, 27, "2^18 3^9"): [{"6": 27}],
    (63, 28, "2^21 3^7"): [{"6": 28}],
    (63, 29, "2^24 3^5"): [
        {"6": 29},
        {"6": 28, "8": 1},
        {"6": 27, "7": 2},
        {"6": 25, "7": 4},
    ],
    (63, 29, "2^25 3^3 4"): [{"6": 28, "8": 1}],
}


def get_moment_profile(
    all_survivors: dict[tuple[int, int], list[dict[str, object]]],
    incidence_sum: int,
    m: int,
    key: str,
) -> dict[str, object]:
    for profile in all_survivors[(incidence_sum, m)]:
        if profile_key(profile["sizes"]) == key:
            return profile
    raise AssertionError(f"missing moment profile {(incidence_sum, m, key)}")


def verify_expected_moment_boundary(
    all_survivors: dict[tuple[int, int], list[dict[str, object]]]
) -> None:
    observed_counts = {}
    for boundary, profiles in all_survivors.items():
        observed_counts[boundary] = {
            profile_key(profile["sizes"]): len(profile["degree_moment_states"])
            for profile in profiles
        }
    if observed_counts != EXPECTED_MOMENT_PROFILE_STATE_COUNTS:
        raise AssertionError(
            "unexpected moment profile/state counts: "
            f"{observed_counts}"
        )

    for (incidence_sum, m, key), expected in (
        EXPECTED_CRITICAL_DEGREE_HISTOGRAMS.items()
    ):
        profile = get_moment_profile(all_survivors, incidence_sum, m, key)
        observed = [
            state["degree_histogram"]
            for state in profile["degree_moment_states"]
        ]
        normalize = lambda rows: {
            tuple(sorted((int(degree), count) for degree, count in row.items()))
            for row in rows
        }
        if normalize(observed) != normalize(expected):
            raise AssertionError(
                f"unexpected critical histograms {(incidence_sum, m, key)}: "
                f"{observed}"
            )


def finite_contradictions(
    q_rows: list[dict[str, object]],
    all_survivors: dict[tuple[int, int], list[dict[str, object]]],
) -> dict[str, object]:
    verify_expected_moment_boundary(all_survivors)

    by_r: dict[int, list[dict[str, object]]] = {}
    for row in q_rows:
        by_r.setdefault(int(row["r"]), []).append(row)

    # r<=17 has at most 25 indexed points, whereas the audited minimum-degree
    # bridge and subset spectrum require at least 27.
    low_order = {}
    for r in range(14, 18):
        upper = 3 * r // 2
        assert upper <= 25
        low_order[str(r)] = {
            "q_profile_count": len(by_r[r]),
            "point_count_upper": upper,
            "spectral_point_count_lower": 27,
            "contradiction": True,
        }

    # r=18 has incidence 54.  The moment boundary is m=27, 27 size-two
    # points, all induced degree six.  Such a point must have q_i+q_j=4,
    # hence both labels have q=2.  Every one of the four r=18 profiles has a
    # q>2 label that must occur in three points.
    r18_profile = get_moment_profile(all_survivors, 54, 27, "2^27")
    assert r18_profile["degree_moment_states"][0]["degree_histogram"] == {"6": 27}
    assert len(by_r[18]) == 4
    assert all(max(row["q"]) > 2 for row in by_r[18])
    r18 = {
        "q_profile_count": 4,
        "point_profile": "2^27",
        "degree_histogram": {"6": 27},
        "size_two_degree_six_forces_q_pair": [2, 2],
        "every_profile_has_q_greater_than_2": True,
        "contradiction": True,
    }

    # r=19 has m=27 or 28.  In both exact moment survivors all size-two
    # points have degree six and hence contain only q=2 labels.  At m=27,
    # a special label would have to occur in all three large points; every
    # r=19 profile has at least two special labels, violating linearity.  At
    # m=28, one large point cannot host the three occurrences of even one
    # special label.
    r19_special_counts = [
        sum(1 for q in row["q"] if q > 2) for row in by_r[19]
    ]
    assert r19_special_counts == [2, 3, 4]
    r19 = {
        "q_profile_count": 3,
        "m27": {
            "point_profile": "2^24 3^3",
            "degree_histogram": {"6": 27},
            "large_points": 3,
            "minimum_special_labels": min(r19_special_counts),
            "forced_common_large_points_per_special_label": 3,
            "contradiction": "two labels would co-occur in three linear points",
        },
        "m28": {
            "point_profile": "2^27 3",
            "degree_histogram": {"6": 28},
            "large_points": 1,
            "required_occurrences_per_special_label": 3,
            "contradiction": "one point supplies at most one occurrence of a label",
        },
    }

    # r=20 has exactly q=2^19,4 and q=2^18,3^2.
    assert len(by_r[20]) == 2
    r20_q4 = next(row for row in by_r[20] if 4 in row["q"])
    r20_q3 = next(row for row in by_r[20] if 3 in row["q"])
    assert Counter(r20_q4["q"]) == Counter({2: 19, 4: 1})
    assert Counter(r20_q3["q"]) == Counter({2: 18, 3: 2})

    # m=27: six size-three points and all degrees six.
    r20_m27_q4_degree_sum = 3 * 4 + 3 * 3
    assert r20_m27_q4_degree_sum % 2 == 1

    # m=28: four size-three points and all degrees six.  A q=4 point needs
    # four positive size-three meeting neighbors, but only three exist.

    # m=29, 2^28 4: the unique size-four point is the sole degree-eight
    # vertex; all size-two points have degree six, so no special label can
    # realize three occurrences.

    # m=29, 2^27 3^2, q=4 branch.  A size-three point containing q=4 needs
    # four weight-four positive crossings.  At most one can be a meeting
    # edge to the other size-three point, so its induced degree is at least
    # nine.  The exact moment boundary has maximum degree eight.  Thus all
    # three q=4 occurrences are size-two points.  Only the four-degree-seven
    # state can hold those occurrences; the resulting positive-support
    # degree sum is odd.
    r20_m29_two_three = get_moment_profile(
        all_survivors, 60, 29, "2^27 3^2"
    )
    r20_m29_histograms = [
        state["degree_histogram"]
        for state in r20_m29_two_three["degree_moment_states"]
    ]
    assert max(max(int(k) for k in hist) for hist in r20_m29_histograms) == 8
    states_with_three_degree_at_least_seven = [
        hist
        for hist in r20_m29_histograms
        if sum(count for degree, count in (
            (int(k), v) for k, v in hist.items()
        ) if degree >= 7) >= 3
    ]
    assert states_with_three_degree_at_least_seven == [{"6": 25, "7": 4}]
    r20_m29_q4_support_sum = 3 * 3 + 24 * 2 + 2 * 3
    assert r20_m29_q4_support_sum % 2 == 1

    # m=30, q=4: its three point occurrences have positive-support degree
    # three and the other 27 size-two points have degree two.
    r20_m30_q4_support_sum = 3 * 3 + 27 * 2
    assert r20_m30_q4_support_sum % 2 == 1

    r20 = {
        "q_profiles": ["2^19 4", "2^18 3^2"],
        "m27": {
            "point_profile": "2^21 3^6",
            "degree_histogram": {"6": 27},
            "q4_branch_forced_size_three_positive_degrees": {
                "degree_4_count": 3,
                "degree_3_count": 3,
                "degree_sum": r20_m27_q4_degree_sum,
                "contradiction": "odd handshake sum",
            },
            "q3_branch_contradiction": (
                "a point with exactly one q=3 has fixed sum 14, not a "
                "multiple of the available meeting weight 4; co-locating "
                "both q=3 labels in all three occurrences violates linearity"
            ),
        },
        "m28": {
            "point_profile": "2^24 3^4",
            "degree_histogram": {"6": 28},
            "q4_branch": {
                "required_positive_size_three_neighbors": 4,
                "available_other_size_three_vertices": 3,
                "contradiction": True,
            },
            "q3_branch_contradiction": (
                "the same fixed-sum parity forces the two q=3 occurrence "
                "sets to coincide in three points, violating linearity"
            ),
        },
        "m29": {
            "2^28 4": {
                "degree_histogram": {"6": 28, "8": 1},
                "q4_contradiction": (
                    "one large point cannot realize three q=4 occurrences"
                ),
                "q3_contradiction": (
                    "one large point plus forbidden degree-seven size-two "
                    "points cannot realize either q=3 label"
                ),
            },
            "2^27 3^2": {
                "q4_large_point_degree_lower": 9,
                "moment_maximum_degree": 8,
                "remaining_special_size_two_points": 3,
                "only_compatible_moment_histogram":
                    {"6": 25, "7": 4},
                "positive_support_degree_sum": r20_m29_q4_support_sum,
                "q4_contradiction": "odd handshake sum",
                "q3_contradiction": (
                    "the unique q3-q3 size-two point and both large points "
                    "would all contain the same label pair, violating linearity"
                ),
            },
        },
        "m30": {
            "point_profile": "2^30",
            "q4_positive_support_degree_sum": r20_m30_q4_support_sum,
            "q4_contradiction": "odd handshake sum",
            "q3_contradiction": (
                "two odd labels can share at most one size-two point but "
                "each requires three occurrences"
            ),
        },
    }

    # r=21, m=27 and 28: all active induced degrees are six.  A size-three
    # point has no disjoint active neighbor, while its fixed sum 12 requires
    # three positive meeting crossings of weight four to other size-three
    # points.  A cubic graph cannot have odd order 9 or 7.
    odd_cubic = {}
    for m, size_three_count in ((27, 9), (28, 7)):
        handshake = 3 * size_three_count
        assert handshake % 2 == 1
        odd_cubic[str(m)] = {
            "size_three_vertices": size_three_count,
            "forced_positive_meeting_degree": 3,
            "degree_sum": handshake,
            "contradiction": "odd handshake sum",
        }

    # m=29, profile 2^25 3^3 4: the moment state is the local lower bound.
    # The unique size-four point is saturated by its eight meeting neighbors.
    # It needs four weight-four meeting crossings, necessarily to four
    # distinct size-three points, but only three exist.
    m29_size_four = {
        "profile": "2^25 3^3 4",
        "size_four_degree": 8,
        "fixed_crossing_sum": 16,
        "positive_crossing_weight": 4,
        "required_distinct_size_three_neighbors": 4,
        "available_size_three_vertices": 3,
        "contradiction": True,
    }

    # m=29, profile 2^24 3^5: a size-three point has either three
    # weight-four positive edges or two weight-six positive edges.  The
    # weight-six vertices form a simple 2-regular graph.  Support-degree
    # parity forces their number to be odd, hence 3 or 5.  Each then has
    # induced degree at least eight, while every moment survivor has at most
    # one vertex of degree at least eight.
    possible_six_type_counts = [
        count
        for count in range(6)
        if (count == 0 or count >= 3)
        and (2 * 24 + 3 * (5 - count) + 2 * count) % 2 == 0
    ]
    assert possible_six_type_counts == [3, 5]
    m29_all_three = get_moment_profile(
        all_survivors, 63, 29, "2^24 3^5"
    )
    high_degree_cap = max(
        sum(
            count
            for degree, count in (
                (int(k), v) for k, v in state["degree_histogram"].items()
            )
            if degree >= 8
        )
        for state in m29_all_three["degree_moment_states"]
    )
    assert high_degree_cap == 1
    assert min(possible_six_type_counts) > high_degree_cap
    m29_all_three_result = {
        "profile": "2^24 3^5",
        "size_three_weight_solutions": positive_weight_solutions(3),
        "possible_weight_six_type_counts_after_cycle_and_parity": possible_six_type_counts,
        "moment_cap_on_vertices_of_degree_at_least_8": high_degree_cap,
        "contradiction": True,
    }

    # m=30 parity branches.
    m30_size_five_sum = 2 * 29 + 5
    assert m30_size_five_sum % 2 == 1

    # A 6-crossing between the unique size-three and size-four points cannot
    # complete the size-three fixed sum with any number of 4-crossings.
    six_completion = [
        count for count in range(4) if 6 + 4 * count == 12
    ]
    assert six_completion == []
    m30_mixed_sum = 2 * 28 + 3 + 4
    assert m30_mixed_sum % 2 == 1

    # For 2^27 3^3, no six-crossing gives another odd handshake.  Any
    # six-crossing forces all three size-three points into a weight-six
    # triangle; the exact projector Cauchy inequality excludes it.
    m30_all_three_no_six_sum = 2 * 27 + 3 * 3
    assert m30_all_three_no_six_sum % 2 == 1
    projector = projector_contradiction_m30()

    # m=31 has one size-three point, necessarily of support degree three.
    m31_sum = 2 * 30 + 3
    assert m31_sum % 2 == 1

    return {
        "r14_through_r17": low_order,
        "r18": r18,
        "r19": r19,
        "r20": r20,
        "r21": {
            "m27_m28": odd_cubic,
            "m29_size_four": m29_size_four,
            "m29_all_size_three_excess": m29_all_three_result,
            "m30": {
                "2^29 5": {
                    "positive_support_degree_sum": m30_size_five_sum,
                    "contradiction": "odd handshake sum",
                },
                "2^28 3 4": {
                    "six_crossing_completion_counts": six_completion,
                    "positive_support_degree_sum_after_excluding_weight_6":
                        m30_mixed_sum,
                    "contradiction": "odd handshake sum",
                },
                "2^27 3^3": {
                    "all_weight_four_support_degree_sum":
                        m30_all_three_no_six_sum,
                    "all_weight_four_contradiction": "odd handshake sum",
                    "weight_six_residual":
                        "triangle on the three size-three points",
                    "weight_six_projector_contradiction": projector,
                },
            },
            "m31": {
                "profile": "2^30 3",
                "positive_support_degree_sum": m31_sum,
                "contradiction": "odd handshake sum",
            },
        },
    }


def build_result() -> dict[str, object]:
    inputs = authenticate_inputs()
    profiles = q_profiles()
    observed_q = [(row["r"], tuple(row["q"])) for row in profiles]
    expected_q = [
        (14, (3,) * 14),
        (15, (2,) * 3 + (3,) * 12),
        (16, (2,) * 6 + (3,) * 10),
        (17, (2,) * 13 + (4,) * 4),
        (17, (2,) * 12 + (3,) * 2 + (4,) * 3),
        (17, (2,) * 11 + (3,) * 4 + (4,) * 2),
        (17, (2,) * 10 + (3,) * 6 + (4,)),
        (17, (2,) * 9 + (3,) * 8),
        (18, (2,) * 15 + (4,) * 3),
        (18, (2,) * 14 + (3,) * 2 + (4,) * 2),
        (18, (2,) * 13 + (3,) * 4 + (4,)),
        (18, (2,) * 12 + (3,) * 6),
        (19, (2,) * 17 + (4,) * 2),
        (19, (2,) * 16 + (3,) * 2 + (4,)),
        (19, (2,) * 15 + (3,) * 4),
        (20, (2,) * 19 + (4,)),
        (20, (2,) * 18 + (3,) * 2),
        (21, (2,) * 21),
    ]
    if observed_q != expected_q:
        raise AssertionError(f"unexpected q profiles: {observed_q}")

    all_survivors = {}
    for r in range(18, 22):
        incidence_sum = 3 * r
        for m in range(27, 3 * r // 2 + 1):
            all_survivors[(incidence_sum, m)] = moment_survivors(
                m, incidence_sum
            )
    contradictions = finite_contradictions(profiles, all_survivors)

    point_census = {}
    for (incidence_sum, m), survivors in sorted(all_survivors.items()):
        key = f"incidence_{incidence_sum}_m_{m}"
        point_census[key] = {
            "r": incidence_sum // 3,
            "incidence_sum": incidence_sum,
            "m": m,
            "all_point_size_profile_count":
                len(point_size_profiles(m, incidence_sum)),
            "moment_survivor_profile_count": len(survivors),
            "moment_survivors": survivors,
            "spectral_degree_sum_upper": str(spectral_degree_sum_upper(m)),
        }

    return {
        "schema_version": 1,
        "role": "proof_a",
        "claim_label": "DERIVED",
        "scope": (
            "conditional exclusion of project n3=63 for a putative "
            "srg(99,14,1,2), using only authenticated framework through Wave18"
        ),
        "frozen_inputs": inputs,
        "q_profile_census": {
            "sum_q": 42,
            "minimum_d_k": 4,
            "count": len(profiles),
            "profiles": [
                {
                    "r": row["r"],
                    "q": list(row["q"]),
                    "d_k": list(row["d_k"]),
                    "point_count_upper": 3 * row["r"] // 2,
                }
                for row in profiles
            ],
            "counts_by_r": {
                str(r): sum(1 for row in profiles if row["r"] == r)
                for r in range(14, 22)
            },
            "rejected_initial_census": {
                "claim": "only r=14 q=3^14 and r=21 q=2^21 survive",
                "status": "REJECTED",
                "cause": (
                    "an exploratory partition generator propagated a "
                    "temporary average bound as a permanent maximum"
                ),
                "caught_by": "this complete fixed-length partition census",
            },
        },
        "crossing_weight_checks": {
            "size2_disjoint": crossing_weights(2, 7, False),
            "size2_meeting": crossing_weights(2, 7, True),
            "size3_size2_disjoint": crossing_weights(3, 2, False),
            "size3_size2_meeting": crossing_weights(3, 2, True),
            "size3_size3_disjoint": crossing_weights(3, 3, False),
            "size3_size3_meeting": crossing_weights(3, 3, True),
            "size4_size3_disjoint": crossing_weights(4, 3, False),
            "size4_size3_meeting": crossing_weights(4, 3, True),
            "size_three_fixed_sum_solutions_4a_plus_6b_eq_12":
                positive_weight_solutions(3),
        },
        "point_and_moment_census": point_census,
        "finite_contradictions": contradictions,
        "conditional_n3_63": "EXCLUDED_DERIVED_PENDING_INDEPENDENT_AUDIT",
        "prospective_conditional_n3_lower_bound": 66,
        "prospective_conditional_induced_C6_lower_bound": 209352,
        "conway_99_target": "UNKNOWN",
        "novelty": "UNKNOWN",
        "limitations": [
            "The semantic indexed-point and crossing bridge is imported from audited pre-Wave19 work.",
            "The finite checker validates arithmetic and case coverage, not the imported graph semantics.",
            "No Wave19 discovery or audit is an input.",
            "The first exploratory two-profile census was wrong, is explicitly rejected, and supplies no premise.",
            "No raw solver status, automorphism restriction, or catalog non-hit is used.",
            "No target existence/nonexistence or novelty conclusion is claimed.",
        ],
    }


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    payload = canonical_json_bytes(build_result())
    if args.verify is not None:
        frozen = args.verify.read_bytes()
        if payload != frozen:
            raise SystemExit("FAIL: regenerated payload differs from frozen JSON")
        print("PASS: regenerated payload is byte-identical")
        return
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
        print(f"WROTE {args.output} ({len(payload)} bytes)")
        return
    print(payload.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
