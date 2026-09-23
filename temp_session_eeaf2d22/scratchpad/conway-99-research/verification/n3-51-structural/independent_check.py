#!/usr/bin/env python3
"""Independent exact checks for the Wave 16 structural n3=51 argument.

This standard-library checker deliberately does not import discovery-lane
code.  It checks the finite arithmetic accompanying the human semantic
proof: q-profiles, the degree-three obstruction, overlap-deleted crossings,
fixed-point divisibility, active-set bounds, local minimum degree, and the
exact SRG subset spectral threshold.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from math import gcd
from pathlib import Path
from typing import Iterable, Sequence


TARGET_N3 = 51
SUM_Q = 2 * TARGET_N3 // 3
FINAL_WAVE15_AUDIT_SHA256 = (
    "edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036"
)
HISTORICAL_WAVE15_DECLARED_SHA256 = (
    "d5e931284407a2071eaf1e6523aac045c96df0b212c946cd4e9b074b9cf41191"
)
HISTORICAL_WAVE15_INTERMEDIATE_SHA256 = (
    "decaa1c2657071013159474d896e8a7c71212a4e4e2a37c2530e5cf18fe2c1d2"
)
FINAL_WAVE16_DISCOVERY_SHA256 = (
    "95d04a774397332417c9613718fe6699a5392ef5222fef1cfa00b12e2860af3f"
)
HISTORICAL_WAVE16_DISCOVERY_SHA256 = (
    "62c4dad2faa03a5f16e39e7b8efd6cc2bc1a7a93e445be3c2c87f50b4616d97d"
)
HISTORICAL_WAVE16_DISCOVERY_BASELINE_COMMIT = (
    "09c20e6c8774ff8676de789b631fd7b0973cf1f5"
)
FINAL_WAVE16_DISCOVERY_REPAIR_COMMIT = (
    "7530caebc2705dd3b5a6682cf89c51b55810db7a"
)
EXPECTED_RAW = (
    (12, (2,) * 2 + (3,) * 10),
    (13, (2,) * 9 + (4,) * 4),
    (13, (2,) * 8 + (3,) * 2 + (4,) * 3),
    (13, (2,) * 7 + (3,) * 4 + (4,) * 2),
    (13, (2,) * 6 + (3,) * 6 + (4,)),
    (13, (2,) * 5 + (3,) * 8),
    (14, (2,) * 11 + (4,) * 3),
    (14, (2,) * 10 + (3,) * 2 + (4,) * 2),
    (14, (2,) * 9 + (3,) * 4 + (4,)),
    (14, (2,) * 8 + (3,) * 6),
    (15, (2,) * 13 + (4,) * 2),
    (15, (2,) * 12 + (3,) * 2 + (4,)),
    (15, (2,) * 11 + (3,) * 4),
    (16, (2,) * 15 + (4,)),
    (16, (2,) * 14 + (3,) * 2),
    (17, (2,) * 17),
)
EXPECTED_DK3_SURVIVORS = (
    (13, (2,) * 5 + (3,) * 8),
    (14, (2,) * 8 + (3,) * 6),
    (15, (2,) * 11 + (3,) * 4),
    (16, (2,) * 15 + (4,)),
    (16, (2,) * 14 + (3,) * 2),
    (17, (2,) * 17),
)
EXPECTED_DK4_SURVIVORS = (
    (14, (2,) * 8 + (3,) * 6),
    (15, (2,) * 11 + (3,) * 4),
    (16, (2,) * 14 + (3,) * 2),
    (17, (2,) * 17),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def wave15_provenance() -> dict[str, object]:
    """Pin the final public Wave 15 audit without erasing earlier observations."""

    repository_root = Path(__file__).resolve().parents[2]
    audit_path = (
        repository_root
        / "verification"
        / "2026-07-23-wave15-global-lift-audit.md"
    )
    current = sha256_file(audit_path)
    return {
        "path": "verification/2026-07-23-wave15-global-lift-audit.md",
        "final_public_sha256": FINAL_WAVE15_AUDIT_SHA256,
        "observed_sha256": current,
        "matches_final_public_sha256": current == FINAL_WAVE15_AUDIT_SHA256,
        "historical_declared_sha256": HISTORICAL_WAVE15_DECLARED_SHA256,
        "historical_intermediate_uncommitted_sha256": (
            HISTORICAL_WAVE15_INTERMEDIATE_SHA256
        ),
    }


def wave16_discovery_provenance() -> dict[str, object]:
    """Pin the repaired discovery report while retaining its failed baseline."""

    repository_root = Path(__file__).resolve().parents[2]
    report_path = (
        repository_root
        / "agents"
        / "2026-07-23-wave16-n3-51-structural.md"
    )
    current = sha256_file(report_path)
    return {
        "path": "agents/2026-07-23-wave16-n3-51-structural.md",
        "final_public_sha256": FINAL_WAVE16_DISCOVERY_SHA256,
        "observed_sha256": current,
        "matches_final_public_sha256": current == FINAL_WAVE16_DISCOVERY_SHA256,
        "historical_pre_repair_sha256": HISTORICAL_WAVE16_DISCOVERY_SHA256,
        "historical_failed_baseline_commit": (
            HISTORICAL_WAVE16_DISCOVERY_BASELINE_COMMIT
        ),
        "final_provenance_repair_commit": (
            FINAL_WAVE16_DISCOVERY_REPAIR_COMMIT
        ),
    }


def enumerate_profiles(total: int = SUM_Q) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Enumerate all nondecreasing active q-profiles from first principles."""

    rows: list[tuple[int, tuple[int, ...]]] = []
    # q>=2 gives r<=total//2.  Values of r below one are harmless.
    for r in range(1, total // 2 + 1):
        q_max = (r - 1) // 3
        if q_max < 2:
            continue
        for profile in itertools.combinations_with_replacement(
            range(2, q_max + 1), r
        ):
            if sum(profile) == total:
                rows.append((r, profile))
    return tuple(rows)


def k_degrees(row: tuple[int, tuple[int, ...]]) -> tuple[int, ...]:
    r, profile = row
    return tuple(r - 1 - 3 * q for q in profile)


def filter_min_k_degree(
    rows: Iterable[tuple[int, tuple[int, ...]]], minimum: int
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    return tuple(row for row in rows if min(k_degrees(row)) >= minimum)


def degree_three_forced_point_systems() -> tuple[tuple[frozenset[str], ...], ...]:
    """Enumerate the local systems forced if d_K(x)=3.

    The three points through x consume the only neighbors a,b,c.  For each
    of the two remaining points through a, its external part is a nonempty
    subset of {b,c}; linearity makes the two external parts disjoint.
    """

    neighbors = frozenset(("b", "c"))
    nonempty = tuple(
        frozenset(s)
        for size in range(1, len(neighbors) + 1)
        for s in itertools.combinations(sorted(neighbors), size)
    )
    systems: list[tuple[frozenset[str], ...]] = []
    for left in nonempty:
        for right in nonempty:
            if left.isdisjoint(right):
                systems.append(
                    (
                        frozenset(("x", "a")),
                        frozenset(("x", "b")),
                        frozenset(("x", "c")),
                        frozenset(("a",)) | left,
                        frozenset(("a",)) | right,
                    )
                )
    return tuple(systems)


def has_three_distinct_pairwise_meetings(
    points: Sequence[frozenset[str]],
) -> bool:
    for triple in itertools.combinations(points, 3):
        meets = [triple[i] & triple[j] for i, j in ((0, 1), (0, 2), (1, 2))]
        if all(len(meeting) == 1 for meeting in meets):
            labels = {next(iter(meeting)) for meeting in meets}
            if len(labels) == 3:
                return True
    return False


def admissible_crossing_masks(rows: int, cols: int) -> tuple[int, ...]:
    """Return edge counts for all simple bipartite 0/2-degree crossings.

    Generation is by the row choices, avoiding a 2^(rows*cols) scan.  This
    checker needs only rows one and two, but keeping the interface explicit
    makes the overlap deletion visible in the call sites.
    """

    if rows not in (0, 1, 2, 3):
        raise ValueError("this audit enumerator is bounded to at most three rows")
    if cols < 0:
        raise ValueError("negative crossing width")
    row_choices: tuple[tuple[int, ...], ...] = ((),) + tuple(
        itertools.combinations(range(cols), 2)
    )
    counts: set[int] = set()
    for choices in itertools.product(row_choices, repeat=rows):
        col_degrees = [0] * cols
        for chosen in choices:
            for col in chosen:
                col_degrees[col] += 1
        if all(degree in (0, 2) for degree in col_degrees):
            counts.add(sum(map(len, choices)))
    return tuple(sorted(counts))


def row_only_crossing_counts(rows: int, cols: int) -> tuple[int, ...]:
    """Hostile weakening: impose 0/2 degrees on rows only."""

    row_choices = ((),) + tuple(itertools.combinations(range(cols), 2))
    return tuple(
        sorted({sum(map(len, choices)) for choices in itertools.product(row_choices, repeat=rows)})
    )


def endpoint_crossing_counts(point_size: int, other_size: int, overlap: int) -> tuple[int, ...]:
    """Crossing sizes after deleting the common label from both endpoints."""

    if point_size != 2:
        raise ValueError("the endpoint-specific claim is only for size two")
    if overlap not in (0, 1):
        raise ValueError("linearity permits overlap zero or one")
    if other_size < overlap:
        raise ValueError("overlap larger than the other point")
    return admissible_crossing_masks(point_size - overlap, other_size - overlap)


def positive_support_properties(
    other_size: int, overlap: int, crossing_edges: int
) -> dict[str, bool]:
    """Record consequences of a positive term at a fixed size-two endpoint."""

    allowed = crossing_edges in endpoint_crossing_counts(2, other_size, overlap)
    positive = allowed and crossing_edges > 0
    return {
        "allowed": allowed,
        "positive": positive,
        # S_v is nonempty exactly when its indexed original vertex is active.
        "other_endpoint_active": positive and other_size > 0,
        # Every meeting crossing is empty after deletion.
        "point_sets_disjoint": positive and overlap == 0,
        # An active-triangle neighbor shares that active triangle label.
        "not_an_active_triangle_neighbor": positive and overlap == 0,
    }


def fixed_sum_positive_counts(q_left: int, q_right: int) -> tuple[int, ...]:
    """Possible numbers of positive 4-contributions among 14 neighbors."""

    fixed_sum = 2 * (q_left + q_right)
    values: list[int] = []
    for mask in range(1 << 14):
        count = mask.bit_count()
        if 4 * count == fixed_sum:
            values.append(count)
    return tuple(sorted(set(values)))


def weakened_fixed_sum_positive_counts(
    q_left: int, q_right: int
) -> tuple[tuple[int, int], ...]:
    """Hostile weakening allowing contributions two as well as four."""

    target = 2 * (q_left + q_right)
    possibilities = []
    for twos in range(15):
        for fours in range(15 - twos):
            if 2 * twos + 4 * fours == target:
                possibilities.append((twos, fours))
    return tuple(possibilities)


def active_set_bounds(
    rows: Iterable[tuple[int, tuple[int, ...]]]
) -> tuple[tuple[int, int], ...]:
    return tuple((r, 3 * r // 2) for r, _ in rows)


def active_triangle_neighbors(point_size: int) -> tuple[str, ...]:
    """Create the 2s distinct original-neighbor indices forced by lambda=1."""

    if point_size < 1:
        return ()
    return tuple(
        f"triangle_{label}_neighbor_{side}"
        for label in range(point_size)
        for side in (0, 1)
    )


def valid_triangle_neighbor_family(
    point_size: int, neighbor_pairs: Sequence[Sequence[str]]
) -> bool:
    """Reject a repeated original neighbor across two triangle labels."""

    if len(neighbor_pairs) != point_size:
        return False
    flattened = [neighbor for pair in neighbor_pairs for neighbor in pair]
    return all(len(pair) == 2 and pair[0] != pair[1] for pair in neighbor_pairs) and (
        len(flattened) == len(set(flattened))
    )


def local_degree_rows(max_point_size: int = 17) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for size in range(2, max_point_size + 1):
        if size >= 3:
            feasible_under_degree_14 = 2 * size <= 14
            rows.append(
                {
                    "point_size": size,
                    "q_types": "arbitrary in {2,3}",
                    "triangle_neighbors": 2 * size,
                    "positive_support_neighbors": "not needed",
                    "minimum_active_degree": 2 * size,
                    "admissible": feasible_under_degree_14,
                    "reason_if_inadmissible": (
                        None
                        if feasible_under_degree_14
                        else "2|S_u| distinct triangle neighbors exceed degree 14"
                    ),
                }
            )
            continue
        for pair in ((2, 2), (2, 3), (3, 3)):
            support_counts = fixed_sum_positive_counts(*pair)
            admissible = bool(support_counts)
            support = support_counts[0] if admissible else None
            rows.append(
                {
                    "point_size": 2,
                    "q_types": list(pair),
                    "triangle_neighbors": 4,
                    "positive_support_neighbors": support,
                    "minimum_active_degree": 4 + support if admissible else None,
                    "admissible": admissible,
                }
            )
    return tuple(rows)


def spectral_upper_twice_edges(m: int, restricted_max: int = 3) -> Fraction:
    """Rayleigh upper bound x^T A x for an m-vertex subset."""

    return Fraction(14 * m * m, 99) + restricted_max * (
        Fraction(m, 1) - Fraction(m * m, 99)
    )


def first_order_allowed_by_spectral_bound(
    minimum_degree: int = 6, restricted_max: int = 3
) -> int:
    for m in range(1, 100):
        if minimum_degree * m <= spectral_upper_twice_edges(m, restricted_max):
            return m
    raise AssertionError("no subset order satisfies the supplied bound")


def divisibility_replay(n3: int, sum_q: int) -> dict[str, bool]:
    """Replay 3*sum(q)=2*n3 and the coprime cancellation giving 3|n3."""

    identity_holds = 3 * sum_q == 2 * n3
    return {
        "incidence_identity_holds": identity_holds,
        "two_and_three_are_coprime": gcd(2, 3) == 1,
        "n3_is_divisible_by_three": identity_holds and n3 % 3 == 0,
    }


def next_multiple_strictly_above(value: int, divisor: int) -> int:
    if divisor <= 0:
        raise ValueError("divisor must be positive")
    return divisor * (value // divisor + 1)


def induced_c6_count(n3: int) -> int:
    return 209286 + n3


def build_results() -> dict[str, object]:
    profiles = enumerate_profiles()
    dk3 = filter_min_k_degree(profiles, 3)
    dk4 = filter_min_k_degree(profiles, 4)

    systems = degree_three_forced_point_systems()
    crossing_table = []
    for other_size in range(0, 18):
        disjoint = endpoint_crossing_counts(2, other_size, 0)
        meeting = (
            endpoint_crossing_counts(2, other_size, 1)
            if other_size >= 1
            else None
        )
        crossing_table.append(
            {
                "other_size": other_size,
                "disjoint_counts": list(disjoint),
                "meeting_counts_after_deletion": (
                    list(meeting) if meeting is not None else None
                ),
            }
        )

    local_rows = local_degree_rows()
    admissible_minima = [
        int(row["minimum_active_degree"])
        for row in local_rows
        if row["admissible"]
    ]

    return {
        "wave15_provenance": wave15_provenance(),
        "wave16_discovery_provenance": wave16_discovery_provenance(),
        "target_n3": TARGET_N3,
        "sum_q": SUM_Q,
        "raw_profiles": [
            {
                "r": r,
                "q": list(profile),
                "d_k": list(k_degrees((r, profile))),
            }
            for r, profile in profiles
        ],
        "raw_profile_count": len(profiles),
        "d_k_at_least_3_profile_count": len(dk3),
        "d_k_at_least_4_profile_count": len(dk4),
        "surviving_profiles": [
            {"r": r, "q": list(profile), "d_k": list(k_degrees((r, profile)))}
            for r, profile in dk4
        ],
        "degree_three_local_system_count": len(systems),
        "degree_three_all_have_forbidden_meetings": all(
            has_three_distinct_pairwise_meetings(system) for system in systems
        ),
        "active_set_bounds": [
            {"r": r, "maximum_x": bound} for r, bound in active_set_bounds(dk4)
        ],
        "crossing_table": crossing_table,
        "fixed_sum_positive_neighbor_counts": {
            "2,2": list(fixed_sum_positive_counts(2, 2)),
            "2,3": list(fixed_sum_positive_counts(2, 3)),
            "3,3": list(fixed_sum_positive_counts(3, 3)),
        },
        "local_degree_rows": list(local_rows),
        "minimum_admissible_active_degree": min(admissible_minima),
        "spectral_first_order_at_min_degree_6": first_order_allowed_by_spectral_bound(),
        "spectral_upper_at_m25": str(spectral_upper_twice_edges(25)),
        "spectral_lower_at_m25": 6 * 25,
        "spectral_upper_at_m27": str(spectral_upper_twice_edges(27)),
        "spectral_lower_at_m27": 6 * 27,
        "consequence_replay": {
            "divisibility": divisibility_replay(TARGET_N3, SUM_Q),
            "next_n3_after_excluding_51": next_multiple_strictly_above(
                TARGET_N3, 3
            ),
            "induced_c6_at_next_n3": induced_c6_count(
                next_multiple_strictly_above(TARGET_N3, 3)
            ),
        },
        "hostile_mutations": {
            "d_k_3_extra_profiles": len(dk3) - len(dk4),
            "row_only_two_by_three_counts": list(row_only_crossing_counts(2, 3)),
            "three_by_three_two_sided_counts": list(
                admissible_crossing_masks(3, 3)
            ),
            "mixed_fixed_sum_if_two_allowed": [
                list(pair) for pair in weakened_fixed_sum_positive_counts(2, 3)
            ],
            "singleton_active_set_bound_at_r17": 3 * 17,
            "spectral_first_order_if_restricted_max_4": (
                first_order_allowed_by_spectral_bound(restricted_max=4)
            ),
        },
        "status": {
            "conditional_n3_51": "EXCLUDED_EXACT_ARITHMETIC_ACCOMPANIMENT",
            "conditional_n3_lower_bound": 54,
            "conditional_induced_c6_lower_bound": 209340,
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def verify_results(results: dict[str, object]) -> None:
    provenance = wave15_provenance()
    assert provenance["matches_final_public_sha256"]
    assert provenance["observed_sha256"] == FINAL_WAVE15_AUDIT_SHA256
    assert len(
        {
            HISTORICAL_WAVE15_DECLARED_SHA256,
            HISTORICAL_WAVE15_INTERMEDIATE_SHA256,
            FINAL_WAVE15_AUDIT_SHA256,
        }
    ) == 3
    assert results["wave15_provenance"] == provenance
    discovery_provenance = wave16_discovery_provenance()
    assert discovery_provenance["matches_final_public_sha256"]
    assert (
        discovery_provenance["observed_sha256"]
        == FINAL_WAVE16_DISCOVERY_SHA256
    )
    assert (
        HISTORICAL_WAVE16_DISCOVERY_SHA256
        != FINAL_WAVE16_DISCOVERY_SHA256
    )
    assert results["wave16_discovery_provenance"] == discovery_provenance

    profiles = enumerate_profiles()
    assert profiles == EXPECTED_RAW
    assert filter_min_k_degree(profiles, 3) == EXPECTED_DK3_SURVIVORS
    assert filter_min_k_degree(profiles, 4) == EXPECTED_DK4_SURVIVORS

    systems = degree_three_forced_point_systems()
    assert len(systems) == 2
    assert all(has_three_distinct_pairwise_meetings(system) for system in systems)

    assert active_set_bounds(EXPECTED_DK4_SURVIVORS) == (
        (14, 21),
        (15, 22),
        (16, 24),
        (17, 25),
    )

    # Empty other endpoint and every overlap-deleted one-row crossing vanish.
    assert endpoint_crossing_counts(2, 0, 0) == (0,)
    for other_size in range(1, 18):
        assert endpoint_crossing_counts(2, other_size, 1) == (0,)
    # A disjoint endpoint gives no crossing when empty/size one, and otherwise
    # exactly the alternatives zero or four.
    assert endpoint_crossing_counts(2, 1, 0) == (0,)
    for other_size in range(2, 18):
        assert endpoint_crossing_counts(2, other_size, 0) == (0, 4)

    assert fixed_sum_positive_counts(2, 2) == (2,)
    assert fixed_sum_positive_counts(2, 3) == ()
    assert fixed_sum_positive_counts(3, 3) == (3,)
    for other_size in range(2, 18):
        properties = positive_support_properties(other_size, 0, 4)
        assert all(properties.values())
    for other_size in range(1, 18):
        assert not positive_support_properties(other_size, 1, 4)["allowed"]
    # Six is possible away from a fixed size-two endpoint, so no global
    # H-degree {0,4} premise is smuggled into this checker.
    assert 6 in admissible_crossing_masks(3, 3)

    local_rows = local_degree_rows()
    admissible = [row for row in local_rows if row["admissible"]]
    assert min(int(row["minimum_active_degree"]) for row in admissible) == 6
    # Every feasible size beyond three was explicitly included and needs no
    # support premise.  Sizes above seven are themselves impossible in a
    # 14-regular graph because the 2s triangle neighbors are distinct.
    assert {int(row["point_size"]) for row in admissible} >= set(range(2, 8))
    for row in local_rows:
        if int(row["point_size"]) >= 8:
            assert not row["admissible"]

    generated = active_triangle_neighbors(17)
    assert len(generated) == 34 == len(set(generated))
    assert valid_triangle_neighbor_family(
        3, (("a", "b"), ("c", "d"), ("e", "f"))
    )

    assert spectral_upper_twice_edges(25) == Fraction(1300, 9)
    assert Fraction(6 * 25, 1) > spectral_upper_twice_edges(25)
    assert spectral_upper_twice_edges(27) == Fraction(162, 1)
    assert first_order_allowed_by_spectral_bound() == 27

    divisibility = divisibility_replay(TARGET_N3, SUM_Q)
    assert all(divisibility.values())
    assert next_multiple_strictly_above(TARGET_N3, 3) == 54
    assert induced_c6_count(54) == 209340

    assert results["raw_profile_count"] == 16
    assert results["d_k_at_least_4_profile_count"] == 4
    assert results["minimum_admissible_active_degree"] == 6
    assert results["spectral_first_order_at_min_degree_6"] == 27
    assert results["consequence_replay"] == {
        "divisibility": divisibility,
        "next_n3_after_excluding_51": 54,
        "induced_c6_at_next_n3": 209340,
    }


def canonical_sha256(payload: dict[str, object]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--compare",
        type=Path,
        help="optional JSON file that must equal the independently rebuilt payload",
    )
    args = parser.parse_args()

    results = build_results()
    verify_results(results)
    if args.compare:
        frozen = json.loads(args.compare.read_text(encoding="utf-8"))
        if frozen != results:
            raise SystemExit("independent payload differs from comparison JSON")
    print(json.dumps(results, indent=2, sort_keys=True))
    print(f"semantic_sha256={canonical_sha256(results)}")
    print("independent structural checks: PASS")


if __name__ == "__main__":
    main()
