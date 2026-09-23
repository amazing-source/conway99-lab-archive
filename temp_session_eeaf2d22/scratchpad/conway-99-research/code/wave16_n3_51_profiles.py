#!/usr/bin/env python3
"""Exact profile and local-state census for conditional ``n3=51``.

This discovery program works only inside the inherited active-label
framework.  Its deductions are labelled ``DERIVED_PENDING_AUDIT`` and do not
resolve the Conway-99 target.
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
from typing import Sequence


TARGET_N3 = 51
Q_SUM = 34
STARTING_COMMIT = "861cfeb6195b19b08feceff07be88a6ab5093fd4"

INPUT_PATHS = (
    Path("AGENTS.md"),
    Path("CONJECTURE.md"),
    Path("verification/2026-07-22-n3-side-incidence-audit.md"),
    Path("verification/2026-07-22-wave14-n3-48-computation-audit.md"),
)


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def source_manifest(paths: Sequence[Path] = INPUT_PATHS) -> dict[str, str]:
    return {
        path.as_posix(): file_sha256(path)
        for path in paths
    }


def active_q_profiles(
    n3_count: int = TARGET_N3,
) -> tuple[tuple[int, ...], ...]:
    """Enumerate all nondecreasing q-multisets from the inherited equations."""

    if n3_count < 0 or (2 * n3_count) % 3:
        raise ValueError("2*n3 must be a nonnegative multiple of three")
    target = 2 * n3_count // 3
    profiles: list[tuple[int, ...]] = []

    def visit(
        remaining: int,
        least: int,
        values: tuple[int, ...],
    ) -> None:
        if remaining == 0:
            order = len(values)
            if values and all(
                3 * q_value <= order - 1 for q_value in values
            ):
                profiles.append(values)
            return
        for q_value in range(least, remaining + 1):
            visit(
                remaining - q_value,
                q_value,
                (*values, q_value),
            )

    visit(target, 2, ())
    return tuple(
        sorted(profiles, key=lambda values: (-len(values), values))
    )


def k_degrees(q_values: Sequence[int]) -> tuple[int, ...]:
    order = len(q_values)
    return tuple(
        order - 1 - 3 * q_value for q_value in q_values
    )


def profile_id(q_values: Sequence[int]) -> str:
    histogram = Counter(q_values)
    suffix = "-".join(
        f"q{q_value}x{multiplicity}"
        for q_value, multiplicity in sorted(histogram.items())
    )
    return f"r{len(q_values)}-{suffix}"


def profile_rows() -> tuple[dict[str, object], ...]:
    rows = []
    for q_values in active_q_profiles():
        degrees = k_degrees(q_values)
        passes_minimum = min(degrees) >= 3
        passes_degree_three = passes_minimum and min(degrees) >= 4
        rows.append(
            {
                "profile_id": profile_id(q_values),
                "active_order": len(q_values),
                "q_values": list(q_values),
                "q_histogram": {
                    str(key): value
                    for key, value in sorted(
                        Counter(q_values).items()
                    )
                },
                "q_sum": sum(q_values),
                "k_degrees": list(degrees),
                "k_degree_histogram": {
                    str(key): value
                    for key, value in sorted(
                        Counter(degrees).items()
                    )
                },
                "k_edge_count": sum(degrees) // 2,
                "k_handshake_even": sum(degrees) % 2 == 0,
                "survives_minimum_degree_three": passes_minimum,
                "survives_degree_three_obstruction": (
                    passes_degree_three
                ),
            }
        )
    return tuple(rows)


def surviving_profile_rows() -> tuple[dict[str, object], ...]:
    return tuple(
        row
        for row in profile_rows()
        if row["survives_degree_three_obstruction"]
    )


def large_point_degree_obstruction(
    *,
    active_order: int,
    point_size: int,
    root_k_degrees: Sequence[int],
) -> dict[str, object]:
    """Give the crossing-based K-incidence contradiction for size >= 4.

    A root point P of size s has two petals at each root.  Their external
    parts are pairwise disjoint.  If a petal has t external labels, the
    meeting L-crossing has all row and column degrees in {0,2}.  For t=1 it
    is empty; for t>=2 it has at most 2t edges.  Thus the petal contributes
    at least s distinct K-incidences from P to its external part when s>=4.
    """

    size = point_size
    if size < 4:
        raise ValueError("the large-point obstruction starts at size four")
    if len(root_k_degrees) != size:
        raise ValueError("root degree list has wrong size")
    petal_count = 2 * size
    forced_external_k_incidence = petal_count * size
    internal_k_incidence = size * (size - 1)
    available_external_k_incidence = (
        sum(root_k_degrees) - internal_k_incidence
    )
    contradiction = (
        forced_external_k_incidence
        > available_external_k_incidence
    )
    return {
        "active_order": active_order,
        "point_size": size,
        "root_k_degrees": list(root_k_degrees),
        "petal_count": petal_count,
        "minimum_k_incidence_per_petal": size,
        "forced_external_k_incidence": (
            forced_external_k_incidence
        ),
        "internal_root_clique_k_incidence": internal_k_incidence,
        "available_external_k_incidence": (
            available_external_k_incidence
        ),
        "strict_contradiction": contradiction,
        "argument": [
            "two petals occur at each root label",
            "petal external parts are pairwise disjoint",
            "a singleton external side has an empty L-crossing",
            (
                "for external size t>=2, column L-degrees in {0,2} "
                "give at most 2t crossing L-edges"
            ),
            (
                "therefore each petal contributes at least s distinct "
                "K-incidences from the s root labels"
            ),
        ],
    }


def large_point_reductions() -> dict[str, object]:
    output: dict[str, object] = {}
    for row in surviving_profile_rows():
        order = int(row["active_order"])
        max_degree = max(map(int, row["k_degrees"]))
        by_size = {}
        for size in range(4, order // 3 + 1):
            obstruction = large_point_degree_obstruction(
                active_order=order,
                point_size=size,
                root_k_degrees=(max_degree,) * size,
            )
            if not obstruction["strict_contradiction"]:
                raise AssertionError("large-point contradiction failed")
            by_size[str(size)] = obstruction
        output[str(row["profile_id"])] = {
            "maximum_size_from_expansion": order // 3,
            "maximum_root_k_degree_used": max_degree,
            "size_obstructions": by_size,
            "remaining_point_sizes": [2, 3],
        }
    return output


def root_q_compositions(
    q_values: Sequence[int],
) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        sorted(set(itertools.combinations(q_values, 3)))
    )


def local_size3_states(
    *,
    active_order: int,
    root_q_values: Sequence[int],
) -> tuple[dict[str, object], ...]:
    """Enumerate every rooted triple state passing inherited exact bounds."""

    if len(root_q_values) != 3:
        raise ValueError("a size-three root needs three q-values")
    q_values = tuple(map(int, root_q_values))
    k_caps = tuple(
        active_order - 1 - 3 * value for value in q_values
    )
    fixed_point_total = 2 * sum(q_values)
    states = []
    for t_values in itertools.product((1, 2, 3), repeat=3):
        if 3 + sum(t_values) > active_order - 3:
            continue
        u_capacities = tuple(
            degree - (3 + t_value)
            for degree, t_value in zip(
                k_caps,
                t_values,
                strict=True,
            )
        )
        if min(u_capacities) < 0:
            continue
        for zero_counts in itertools.product(
            *(range(t_value) for t_value in t_values)
        ):
            forced_u = tuple(
                sum(
                    3 - t_values[other]
                    + 2 * zero_counts[other]
                    for other in range(3)
                    if other != root
                )
                for root in range(3)
            )
            if any(
                forced > capacity
                for forced, capacity in zip(
                    forced_u,
                    u_capacities,
                    strict=True,
                )
            ):
                continue
            full_crossings = sum(
                t_value - 1 - zero
                for t_value, zero in zip(
                    t_values,
                    zero_counts,
                    strict=True,
                )
            )
            overlap_contribution = 4 * full_crossings
            if overlap_contribution > fixed_point_total:
                continue
            states.append(
                {
                    "t_values": list(t_values),
                    "empty_l_crossing_counts": list(zero_counts),
                    "u_capacities": list(u_capacities),
                    "forced_u_degree_lower_bounds": list(forced_u),
                    "full_l_crossings": full_crossings,
                    "overlap_contribution": overlap_contribution,
                    "fixed_point_total": fixed_point_total,
                }
            )
    return tuple(states)


def canonical_local_state(
    root_q_values: Sequence[int],
    state: dict[str, object],
) -> tuple[object, ...]:
    groups = []
    for q_value in sorted(set(root_q_values)):
        records = []
        for index, observed in enumerate(root_q_values):
            if observed != q_value:
                continue
            records.append(
                (
                    int(state["t_values"][index]),
                    int(
                        state["empty_l_crossing_counts"][index]
                    ),
                    int(state["u_capacities"][index]),
                    int(
                        state[
                            "forced_u_degree_lower_bounds"
                        ][index]
                    ),
                )
            )
        groups.append((q_value, tuple(sorted(records))))
    groups.append(
        ("full_l_crossings", int(state["full_l_crossings"]))
    )
    return tuple(groups)


def local_mode_census(row: dict[str, object]) -> dict[str, object]:
    q_values = tuple(map(int, row["q_values"]))
    compositions = []
    for root_q_values in root_q_compositions(q_values):
        states = local_size3_states(
            active_order=len(q_values),
            root_q_values=root_q_values,
        )
        orbit_keys = {
            canonical_local_state(root_q_values, state)
            for state in states
        }
        compositions.append(
            {
                "root_q_values": list(root_q_values),
                "root_q3_count": root_q_values.count(3),
                "labeled_state_count": len(states),
                "equal_q_coordinate_orbit_count": len(orbit_keys),
                "state_sha256": sha256_bytes(
                    canonical_json_bytes(states)
                ),
            }
        )
    return {
        "profile_id": row["profile_id"],
        "active_order": row["active_order"],
        "root_compositions": compositions,
    }


def raw_branch_cover() -> tuple[dict[str, object], ...]:
    branches = []
    for row in surviving_profile_rows():
        q_values = list(map(int, row["q_values"]))
        branches.append(
            {
                "profile_id": row["profile_id"],
                "branch_id": "no-size3",
                "root_q3_count": None,
                "normalization": (
                    "all selected size-three point variables are false"
                ),
            }
        )
        for special_count in range(
            min(3, q_values.count(3)) + 1
        ):
            if 3 - special_count > q_values.count(2):
                continue
            branches.append(
                {
                    "profile_id": row["profile_id"],
                    "branch_id": f"root-q3x{special_count}",
                    "root_q3_count": special_count,
                    "normalization": (
                        "choose one selected triple of this q-type and "
                        "name it using permutations within equal-q classes"
                    ),
                }
            )
    return tuple(branches)


def local_state_count_by_branch(
    profile_name: str,
    root_q3_count: int,
) -> int:
    row = next(
        row
        for row in surviving_profile_rows()
        if row["profile_id"] == profile_name
    )
    q_values = tuple(map(int, row["q_values"]))
    root_type = tuple(
        [2] * (3 - root_q3_count)
        + [3] * root_q3_count
    )
    if root_type not in root_q_compositions(q_values):
        return 0
    return len(
        local_size3_states(
            active_order=len(q_values),
            root_q_values=root_type,
        )
    )


def finite_branch_reduction() -> tuple[dict[str, object], ...]:
    output = []
    for branch in raw_branch_cover():
        profile_name = str(branch["profile_id"])
        order = int(profile_name.split("-", 1)[0][1:])
        branch_id = str(branch["branch_id"])
        survives = True
        reason = "retained for exact active-local SAT exploration"
        certificate: dict[str, object] | None = None
        if branch_id == "no-size3" and order % 2:
            survives = False
            reason = (
                "incidence parity: 3r is odd while size-two points "
                "contribute even total incidence"
            )
            certificate = {
                "total_incidence": 3 * order,
                "modulus": 2,
            }
        elif branch_id.startswith("root-q3x"):
            count = int(branch_id.removeprefix("root-q3x"))
            state_count = local_state_count_by_branch(
                profile_name,
                count,
            )
            if state_count == 0:
                survives = False
                reason = (
                    "the exhaustive rooted size-three local-state "
                    "census is empty"
                )
                certificate = {
                    "root_q3_count": count,
                    "labeled_local_state_count": 0,
                }
        if (
            survives
            and profile_name == "r14-q2x8-q3x6"
            and branch_id == "no-size3"
        ):
            survives = False
            reason = (
                "at a q=3 label, cubic triangle-free F forces its "
                "three neighbours and two new distance-two labels "
                "as distinct K-neighbours, so d_K>=5>4"
            )
            certificate = {
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


def surviving_branches() -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "profile_id": row["profile_id"],
            "branch_id": row["branch_id"],
        }
        for row in finite_branch_reduction()
        if row["survives_finite_reductions"]
    )


EXPECTED_SURVIVING_PROFILES = (
    "r17-q2x17",
    "r16-q2x14-q3x2",
    "r15-q2x11-q3x4",
    "r14-q2x8-q3x6",
)

EXPECTED_SURVIVING_BRANCHES = (
    ("r17-q2x17", "root-q3x0"),
    ("r16-q2x14-q3x2", "no-size3"),
    ("r16-q2x14-q3x2", "root-q3x0"),
    ("r16-q2x14-q3x2", "root-q3x1"),
    ("r16-q2x14-q3x2", "root-q3x2"),
    ("r15-q2x11-q3x4", "root-q3x0"),
    ("r14-q2x8-q3x6", "root-q3x0"),
)


def build_report() -> dict[str, object]:
    rows = profile_rows()
    survivors = surviving_profile_rows()
    large_points = large_point_reductions()
    local_modes = [
        local_mode_census(row) for row in survivors
    ]
    raw_cover = raw_branch_cover()
    reduced_cover = finite_branch_reduction()
    post_finite = surviving_branches()

    if len(rows) != 16:
        raise AssertionError("expected sixteen raw q profiles")
    if tuple(
        str(row["profile_id"]) for row in survivors
    ) != EXPECTED_SURVIVING_PROFILES:
        raise AssertionError("surviving profile list changed")
    if len(raw_cover) != 16:
        raise AssertionError("raw branch cover must have sixteen rows")
    if tuple(
        (str(row["profile_id"]), str(row["branch_id"]))
        for row in post_finite
    ) != EXPECTED_SURVIVING_BRANCHES:
        raise AssertionError("post-finite branch cover changed")
    if any(
        details["remaining_point_sizes"] != [2, 3]
        for details in large_points.values()
    ):
        raise AssertionError("large-point reduction failed")

    semantic = {
        "target_n3": TARGET_N3,
        "q_sum": Q_SUM,
        "raw_profiles": rows,
        "surviving_profiles": [
            row["profile_id"] for row in survivors
        ],
        "large_point_reductions": large_points,
        "local_size3_mode_census": local_modes,
        "raw_branch_cover": raw_cover,
        "finite_branch_reduction": reduced_cover,
        "post_finite_surviving_branches": post_finite,
    }
    return {
        "schema": "conway99-wave16-n3-51-profile-census-v1",
        "claim_label": "DERIVED_PENDING_AUDIT",
        "target_result": "UNKNOWN",
        "conditional_n3_51_exclusion": "UNKNOWN",
        "novelty": "UNKNOWN",
        "starting_git_commit": STARTING_COMMIT,
        "source_manifest": source_manifest(),
        "encoded_premises": [
            "sum q(T)=2*n3/3",
            "active q(T)>=2",
            "d_L(T)=3*q(T)",
            "d_K(T)=r-1-3*q(T)",
            (
                "each active label lies in exactly three "
                "non-singleton linear point sets"
            ),
            "every selected point is a K-clique",
            (
                "three selected points cannot pairwise meet at "
                "three different labels"
            ),
            (
                "meeting L-crossings have every row and column "
                "degree in {0,2}"
            ),
            (
                "full 2-by-2 L-crossings contribute four to the "
                "fixed-point total"
            ),
            "the inherited degree-three obstruction",
        ],
        "unencoded_premises": [
            "inactive point sets and inactive graph vertices",
            "fixed support from disjoint selected points",
            "completion of fixed-point support equalities",
            "the 693-vertex H graph",
            "a 99-vertex adjacency matrix",
            "global SRG lambda/mu equations",
        ],
        "method": (
            "independent integer partitioning, a crossing-degree "
            "large-point incidence inequality, and exhaustive rooted "
            "size-three state enumeration"
        ),
        "python": sys.version,
        "platform": platform.platform(),
        "semantic": semantic,
        "semantic_sha256": sha256_bytes(
            canonical_json_bytes(semantic)
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
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
    if args.self_test:
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
                    "raw_branch_count": len(
                        report["semantic"]["raw_branch_cover"]
                    ),
                    "post_finite_branch_count": len(
                        report["semantic"][
                            "post_finite_surviving_branches"
                        ]
                    ),
                    "semantic_sha256": report["semantic_sha256"],
                    "target_result": "UNKNOWN",
                },
                sort_keys=True,
            )
        )
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
