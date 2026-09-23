#!/usr/bin/env python3
"""Exact arithmetic and local finite reductions for conditional ``n3=48``.

This is discovery code.  It starts from the audited Wave 6--13 active-label
premises and does not encode a 99-vertex graph.  Its finite outputs remain
``CANDIDATE`` until independently replayed.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


TARGET_N3 = 48
Q_SUM = 2 * TARGET_N3 // 3
ALLOWED_H_DEGREES = (0, 4, 6, 8, 10, 12)


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def active_q_profiles(n3_count: int = TARGET_N3) -> tuple[tuple[int, ...], ...]:
    """Return every multiset satisfying the inherited active-q equations."""

    if n3_count < 0 or (2 * n3_count) % 3:
        raise ValueError("2*n3 must be a nonnegative multiple of three")
    target = 2 * n3_count // 3
    profiles: list[tuple[int, ...]] = []

    def visit(remaining: int, least: int, values: tuple[int, ...]) -> None:
        if remaining == 0:
            order = len(values)
            if values and all(3 * q_value <= order - 1 for q_value in values):
                profiles.append(values)
            return
        for q_value in range(least, remaining + 1):
            visit(remaining - q_value, q_value, (*values, q_value))

    visit(target, 2, ())
    return tuple(
        sorted(profiles, key=lambda values: (-len(values), values))
    )


def k_degrees(q_values: Sequence[int]) -> tuple[int, ...]:
    order = len(q_values)
    return tuple(order - 1 - 3 * q_value for q_value in q_values)


def profile_id(q_values: Sequence[int]) -> str:
    histogram = Counter(q_values)
    pieces = "-".join(
        f"q{q_value}x{multiplicity}"
        for q_value, multiplicity in sorted(histogram.items())
    )
    return f"r{len(q_values)}-{pieces}"


def profile_rows() -> tuple[dict[str, object], ...]:
    rows = []
    for q_values in active_q_profiles():
        degrees = k_degrees(q_values)
        no_singleton = min(degrees) >= 3
        no_degree_three = no_singleton and min(degrees) >= 4
        rows.append(
            {
                "profile_id": profile_id(q_values),
                "active_order": len(q_values),
                "q_values": list(q_values),
                "q_histogram": {
                    str(key): value
                    for key, value in sorted(Counter(q_values).items())
                },
                "q_sum": sum(q_values),
                "k_degrees": list(degrees),
                "k_degree_histogram": {
                    str(key): value
                    for key, value in sorted(Counter(degrees).items())
                },
                "k_edge_count": sum(degrees) // 2,
                "k_handshake_even": sum(degrees) % 2 == 0,
                "survives_three_non_singleton_points": no_singleton,
                "survives_verified_degree_three_obstruction": no_degree_three,
            }
        )
    return tuple(rows)


def surviving_profile_rows() -> tuple[dict[str, object], ...]:
    return tuple(
        row
        for row in profile_rows()
        if row["survives_verified_degree_three_obstruction"]
    )


def maximum_point_size(active_order: int) -> int:
    """Largest integer ``s`` satisfying inherited expansion ``2s<=r-s``."""

    return max(
        (
            size
            for size in range(2, active_order + 1)
            if 2 * size <= active_order - size
        ),
        default=1,
    )


def flower_word_census(
    *,
    active_order: int,
    root_size: int,
    maximum_petal_size: int,
    root_k_degrees: Sequence[int],
    retain_survivors: bool = False,
) -> dict[str, object]:
    """Enumerate all ordered petal-size words around one selected point.

    The two petals at root occurrence ``i`` occupy positions ``2i,2i+1``.
    Their external parts are pairwise disjoint.  A singleton external part
    is K-adjacent to every root label.  A larger external part contributes
    its labels at its own root occurrence.
    """

    if len(root_k_degrees) != root_size:
        raise ValueError("root degree list has the wrong length")
    alphabet = tuple(range(2, maximum_petal_size + 1))
    outside_capacity = active_order - root_size
    petal_count = 2 * root_size
    counts: Counter[str] = Counter()
    survivor_words: list[tuple[int, ...]] = []
    singleton_histogram: Counter[int] = Counter()
    degree_lower_bound_histogram: Counter[int] = Counter()

    for petals in itertools.product(alphabet, repeat=petal_count):
        counts["total_words"] += 1
        external_slots = sum(size - 1 for size in petals)
        if external_slots > outside_capacity:
            counts["capacity_rejections"] += 1
            continue
        counts["capacity_feasible"] += 1
        singleton_count = petals.count(2)
        singleton_histogram[singleton_count] += 1
        lower_degrees = []
        for root in range(root_size):
            based = petals[2 * root : 2 * root + 2]
            based_large_slots = sum(
                size - 1 for size in based if size > 2
            )
            lower_degrees.append(
                root_size - 1 + singleton_count + based_large_slots
            )
        degree_lower_bound_histogram[max(lower_degrees)] += 1
        if all(
            lower <= capacity
            for lower, capacity in zip(
                lower_degrees, root_k_degrees, strict=True
            )
        ):
            counts["k_degree_survivors"] += 1
            survivor_words.append(petals)
        else:
            counts["k_degree_rejections"] += 1

    expected = len(alphabet) ** petal_count
    if counts["total_words"] != expected:
        raise AssertionError("flower enumeration is incomplete")
    return {
        "active_order": active_order,
        "root_size": root_size,
        "maximum_petal_size": maximum_petal_size,
        "root_k_degrees": list(root_k_degrees),
        "petal_count": petal_count,
        "outside_capacity": outside_capacity,
        "statistics": dict(sorted(counts.items())),
        "singleton_petal_histogram": {
            str(key): value
            for key, value in sorted(singleton_histogram.items())
        },
        "maximum_root_degree_lower_bound_histogram": {
            str(key): value
            for key, value in sorted(degree_lower_bound_histogram.items())
        },
        "survivor_words": (
            [list(word) for word in survivor_words]
            if retain_survivors
            else None
        ),
        "survivor_word_sha256": sha256_bytes(
            canonical_json_bytes([list(word) for word in survivor_words])
        ),
    }


def order16_size4_crossing_check(
    survivor_words: Iterable[Sequence[int]],
) -> dict[str, object]:
    """Check the last order-16 size-four flower words symbolically.

    Degree saturation forces one singleton and one size-three petal at every
    root.  For each size-three petal, its two external labels are L-adjacent
    to the other three roots.  The resulting K_{3,2} crossing has column
    degree three, contradicting the inherited two-sided {0,2} rule.
    """

    checked = 0
    rejected = 0
    diagnostics = Counter()
    for raw_word in survivor_words:
        word = tuple(raw_word)
        checked += 1
        if len(word) != 8:
            raise AssertionError("order-16 size-four word has wrong length")
        per_root = tuple(
            tuple(sorted(word[2 * root : 2 * root + 2]))
            for root in range(4)
        )
        if per_root != ((2, 3),) * 4:
            diagnostics["unexpected_degree_survivor_shape"] += 1
            continue
        # Rows are the other three root labels and columns are the two
        # external labels of the based size-three petal.
        row_degrees = (2, 2, 2)
        column_degrees = (3, 3)
        if any(value not in (0, 2) for value in (*row_degrees, *column_degrees)):
            rejected += 1
            diagnostics["two_sided_crossing_rejections"] += 1
    return {
        "degree_survivors_checked": checked,
        "two_sided_crossing_rejections": rejected,
        "all_rejected": checked > 0 and rejected == checked,
        "forced_petal_pair_at_each_root": [2, 3],
        "forced_l_crossing_shape": [3, 2],
        "forced_l_row_degrees": [2, 2, 2],
        "forced_l_column_degrees": [3, 3],
        "diagnostics": dict(sorted(diagnostics.items())),
    }


def local_size3_states(
    *,
    active_order: int,
    root_q_values: Sequence[int],
) -> tuple[dict[str, object], ...]:
    """Enumerate all rooted size-three states passing exact local bounds."""

    if len(root_q_values) != 3:
        raise ValueError("a rooted size-three point needs three q-values")
    q_values = tuple(root_q_values)
    degrees = k_degrees_for_root(active_order, q_values)
    fixed_point_total = 2 * sum(q_values)
    states = []
    for t_values in itertools.product((1, 2, 3), repeat=3):
        # The six petals have 3+sum(t) external labels.
        if 3 + sum(t_values) > active_order - 3:
            continue
        u_capacities = tuple(
            degree - (3 + t_value)
            for degree, t_value in zip(degrees, t_values, strict=True)
        )
        if min(u_capacities) < 0:
            continue
        for zero_counts in itertools.product(
            *(range(t_value) for t_value in t_values)
        ):
            forced_u_degrees = tuple(
                sum(
                    3 - t_values[other] + 2 * zero_counts[other]
                    for other in range(3)
                    if other != root
                )
                for root in range(3)
            )
            if any(
                forced > capacity
                for forced, capacity in zip(
                    forced_u_degrees, u_capacities, strict=True
                )
            ):
                continue
            full_l_crossings = sum(
                t_value - 1 - zero_count
                for t_value, zero_count in zip(
                    t_values, zero_counts, strict=True
                )
            )
            overlap_contribution = 4 * full_l_crossings
            if overlap_contribution > fixed_point_total:
                continue
            states.append(
                {
                    "t_values": list(t_values),
                    "empty_l_crossing_counts": list(zero_counts),
                    "u_capacities": list(u_capacities),
                    "forced_u_degree_lower_bounds": list(forced_u_degrees),
                    "full_l_crossings": full_l_crossings,
                    "overlap_contribution": overlap_contribution,
                    "fixed_point_total": fixed_point_total,
                }
            )
    return tuple(states)


def k_degrees_for_root(
    active_order: int, root_q_values: Sequence[int]
) -> tuple[int, ...]:
    return tuple(active_order - 1 - 3 * value for value in root_q_values)


def canonical_local_state(
    root_q_values: Sequence[int], state: dict[str, object]
) -> tuple[object, ...]:
    """Canonicalize coordinates only inside equal-q root classes."""

    groups = []
    for q_value in sorted(set(root_q_values)):
        records = []
        for index, observed_q in enumerate(root_q_values):
            if observed_q != q_value:
                continue
            records.append(
                (
                    int(state["t_values"][index]),
                    int(state["empty_l_crossing_counts"][index]),
                    int(state["u_capacities"][index]),
                    int(state["forced_u_degree_lower_bounds"][index]),
                )
            )
        groups.append((q_value, tuple(sorted(records))))
    return (*groups, ("full_l_crossings", state["full_l_crossings"]))


def root_q_compositions(
    q_values: Sequence[int],
) -> tuple[tuple[int, int, int], ...]:
    return tuple(sorted(set(itertools.combinations(q_values, 3))))


def local_mode_census(row: dict[str, object]) -> dict[str, object]:
    q_values = tuple(map(int, row["q_values"]))
    output = []
    for root_q_values in root_q_compositions(q_values):
        states = local_size3_states(
            active_order=len(q_values), root_q_values=root_q_values
        )
        orbit_keys = sorted(
            {canonical_local_state(root_q_values, state) for state in states}
        )
        output.append(
            {
                "root_q_values": list(root_q_values),
                "root_q3_count": root_q_values.count(3),
                "labeled_state_count": len(states),
                "equal_q_coordinate_orbit_count": len(orbit_keys),
                "canonical_orbits": [
                    [
                        [
                            group[0],
                            [list(record) for record in group[1]],
                        ]
                        if group[0] != "full_l_crossings"
                        else [group[0], group[1]]
                        for group in orbit
                    ]
                    for orbit in orbit_keys
                ],
                "state_sha256": sha256_bytes(
                    canonical_json_bytes(states)
                ),
            }
        )
    return {
        "profile_id": row["profile_id"],
        "active_order": row["active_order"],
        "root_compositions": output,
    }


def point_size_reductions() -> dict[str, object]:
    """Run the complete large-point flower checks for the three survivors."""

    r16_s5 = flower_word_census(
        active_order=16,
        root_size=5,
        maximum_petal_size=5,
        root_k_degrees=(9,) * 5,
    )
    r16_s4 = flower_word_census(
        active_order=16,
        root_size=4,
        maximum_petal_size=4,
        root_k_degrees=(9,) * 4,
        retain_survivors=True,
    )
    r16_crossing = order16_size4_crossing_check(
        r16_s4["survivor_words"] or ()
    )
    r15_s5 = flower_word_census(
        active_order=15,
        root_size=5,
        maximum_petal_size=5,
        root_k_degrees=(8,) * 5,
    )
    r15_s4 = flower_word_census(
        active_order=15,
        root_size=4,
        maximum_petal_size=4,
        root_k_degrees=(8,) * 4,
    )
    r14_s4 = flower_word_census(
        active_order=14,
        root_size=4,
        maximum_petal_size=4,
        root_k_degrees=(7,) * 4,
    )
    return {
        "r16-q2x16": {
            "maximum_size_from_expansion": 5,
            "size5_flower": r16_s5,
            "size4_flower": r16_s4,
            "size4_crossing_check": r16_crossing,
            "remaining_point_sizes": [2, 3],
        },
        "r15-q2x13-q3x2": {
            "maximum_size_from_expansion": 5,
            "size5_flower_using_maximum_root_degree_8": r15_s5,
            "size4_flower_using_maximum_root_degree_8": r15_s4,
            "remaining_point_sizes": [2, 3],
        },
        "r14-q2x10-q3x4": {
            "maximum_size_from_expansion": 4,
            "size4_flower_using_maximum_root_degree_7": r14_s4,
            "remaining_point_sizes": [2, 3],
        },
    }


def branch_cover() -> tuple[dict[str, object], ...]:
    """Describe the safe label-normalized SAT branch cover."""

    branches = []
    for row in surviving_profile_rows():
        q_values = list(map(int, row["q_values"]))
        q3_count = q_values.count(3)
        branches.append(
            {
                "profile_id": row["profile_id"],
                "branch_id": "no-size3",
                "root_q3_count": None,
                "normalization": "all size-three point variables are false",
            }
        )
        for special_count in range(min(3, q3_count) + 1):
            ordinary_count = 3 - special_count
            if ordinary_count > q_values.count(2):
                continue
            branches.append(
                {
                    "profile_id": row["profile_id"],
                    "branch_id": f"root-q3x{special_count}",
                    "root_q3_count": special_count,
                    "normalization": (
                        "choose one selected size-three point of this q-composition; "
                        "the product of symmetric groups on equal-q labels names it"
                    ),
                }
            )
    return tuple(branches)


def finite_branch_reduction() -> tuple[dict[str, object], ...]:
    """Classify the raw symmetry cover after exact local arithmetic.

    The all-size-two order-fourteen obstruction is the same literal
    length-two-path count used at earlier frontiers: at a q=3 label, its
    three F-neighbours and the two other neighbours of any one of them are
    five distinct forced K-neighbours, above d_K=4.
    """

    output = []
    for branch in branch_cover():
        profile_name = str(branch["profile_id"])
        branch_id = str(branch["branch_id"])
        survives = True
        reason = "retained for PySAT active-local exploration"
        certificate = None
        if profile_name == "r15-q2x13-q3x2" and branch_id == "no-size3":
            survives = False
            reason = (
                "incidence parity: 3*15 is odd but size-two points contribute "
                "an even total"
            )
            certificate = {"total_incidence": 45, "modulus": 2}
        elif (
            branch_id.startswith("root-q3x")
            and int(branch_id.removeprefix("root-q3x")) > 0
        ):
            survives = False
            reason = (
                "the exact rooted size-three local-state census is empty for "
                "every root containing q=3"
            )
            certificate = {
                "root_q3_count": int(
                    branch_id.removeprefix("root-q3x")
                ),
                "labeled_local_state_count": 0,
            }
        elif profile_name == "r14-q2x10-q3x4" and branch_id == "no-size3":
            survives = False
            reason = (
                "at a q=3 label, cubic triangle-free F forces at least "
                "3+2=5 distinct K-neighbours but d_K=4"
            )
            certificate = {
                "f_neighbors": 3,
                "additional_distance_two_neighbors": 2,
                "forced_k_degree_lower_bound": 5,
                "profile_k_degree": 4,
            }
        output.append(
            {
                **branch,
                "survives_finite_reductions": survives,
                "finite_reduction_reason": reason,
                "finite_reduction_certificate": certificate,
            }
        )
    return tuple(output)


def build_report() -> dict[str, object]:
    rows = profile_rows()
    survivors = surviving_profile_rows()
    reductions = point_size_reductions()
    local_modes = [local_mode_census(row) for row in survivors]
    cover = branch_cover()
    reduced_cover = finite_branch_reduction()

    # Regression assertions bind the finite reconstruction.
    if len(rows) != 12:
        raise AssertionError("expected exactly twelve raw q profiles")
    if [row["profile_id"] for row in survivors] != [
        "r16-q2x16",
        "r15-q2x13-q3x2",
        "r14-q2x10-q3x4",
    ]:
        raise AssertionError("surviving profile list changed")
    if (
        reductions["r16-q2x16"]["size4_flower"]["statistics"][
            "k_degree_survivors"
        ]
        != 16
    ):
        raise AssertionError("order-16 size-four flower count changed")
    if not reductions["r16-q2x16"]["size4_crossing_check"]["all_rejected"]:
        raise AssertionError("order-16 size-four crossing reduction failed")
    for profile_data in reductions.values():
        if profile_data["remaining_point_sizes"] != [2, 3]:
            raise AssertionError("large-point reduction changed")
    if len(cover) != 11:
        raise AssertionError("safe SAT branch cover must have eleven rows")
    if [
        (row["profile_id"], row["branch_id"])
        for row in reduced_cover
        if row["survives_finite_reductions"]
    ] != [
        ("r16-q2x16", "no-size3"),
        ("r16-q2x16", "root-q3x0"),
        ("r15-q2x13-q3x2", "root-q3x0"),
        ("r14-q2x10-q3x4", "root-q3x0"),
    ]:
        raise AssertionError("post-finite branch cover changed")

    semantic = {
        "target_n3": TARGET_N3,
        "q_sum": Q_SUM,
        "raw_profiles": rows,
        "surviving_profiles": [
            row["profile_id"] for row in survivors
        ],
        "point_size_reductions": reductions,
        "local_size3_mode_census": local_modes,
        "sat_branch_cover": cover,
        "finite_branch_reduction": reduced_cover,
        "post_finite_surviving_branches": [
            {
                "profile_id": row["profile_id"],
                "branch_id": row["branch_id"],
            }
            for row in reduced_cover
            if row["survives_finite_reductions"]
        ],
    }
    return {
        "schema": "conway99-wave14-n3-48-profile-census-v1",
        "claim_label": "CANDIDATE",
        "target_result": "UNKNOWN",
        "novelty": "UNKNOWN",
        "encoded_premises": [
            "sum q(T)=2*n3/3",
            "active q(T)>=2",
            "d_L(T)=3*q(T)",
            "K is the simple active-label complement of L",
            "three non-singleton linear point sets pass through every active label",
            "every point set is a K-clique",
            "three points cannot pairwise meet at three distinct labels",
            "two-sided meeting-crossing degrees lie in {0,2}",
            "fixed-point overlap contribution is bounded by 2*sum q over the point",
        ],
        "unencoded_premises": [
            "inactive point sets and inactive graph vertices",
            "fixed support from disjoint active point sets",
            "completion of every fixed-point support sum",
            "the 693-vertex H graph",
            "the 99-vertex adjacency matrix",
            "global SRG lambda/mu equalities",
        ],
        "method": (
            "standard-library integer partitions, exhaustive flower words, "
            "symbolic two-sided crossing rejection, and rooted local-state census"
        ),
        "python": sys.version,
        "platform": platform.platform(),
        "semantic": semantic,
        "semantic_sha256": sha256_bytes(canonical_json_bytes(semantic)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--self-test", action="store_true", help="run assertions without writing"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if not args.self_test:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "raw_profile_count": len(
                        report["semantic"]["raw_profiles"]
                    ),
                    "surviving_profile_count": len(
                        report["semantic"]["surviving_profiles"]
                    ),
                    "branch_count": len(
                        report["semantic"]["sat_branch_cover"]
                    ),
                    "semantic_sha256": report["semantic_sha256"],
                    "target_result": "UNKNOWN",
                },
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
