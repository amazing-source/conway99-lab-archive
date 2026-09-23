#!/usr/bin/env python3
"""Independent global-reduction checker for the Wave 19 n3=60 audit.

This checker deliberately does not import any discovery module.  Its two
profile enumerators use different state spaces (ordered integer partitions
versus value histograms), and its crossing checker compares bit-mask
enumeration with a structural formula.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = Path(__file__).with_name("global-reduction-certificate.json")

PINNED_INPUTS = {
    "verification/n3-60-structural/preinspection-freeze.md":
        "983f90c1d150c6e14e5e2bc7a010e1a3809848ddb1e4b825e5fdfac70398d6af",
    "verification/2026-07-23-wave15-global-lift-audit.md":
        "edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036",
    "verification/2026-07-23-wave15-algebraic-audit.md":
        "b0541d05d2c1c359152b86223e2ebbdbd002b2ff42deb699f6a0b21d149a5b45",
    "verification/2026-07-23-wave16-n3-51-structural-audit.md":
        "99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6",
    "attempts/wave15-global-lift/subset-moment-certificate.json":
        "cb02ab80f92d7d2c8ec5140e3be2916354976442aa2e1869524aa728c73bd386",
    "attempts/wave15-global-lift/verify_subset_moment_certificate.py":
        "0429db33fa0a61864ff8456326379fab47a09e7b8ea7234130d12b018cd041c2",
    "attempts/wave16-n3-51-structural/exact_check.py":
        "5aef211ea7d457543fc3f494eea125bbd0fd6fae2533fd566b475ff3f971c5cf",
    "attempts/wave16-n3-51-structural/exact-checks.json":
        "7419a54effd68d6853e787616a82dc618163d472d8969772cd2e6220b336ab24",
    "agents/2026-07-23-wave19-n3-60-structural.md":
        "b2f90af07f34a6525ea35cdf4d392d95aea10fc319633cd17037d00145690744",
    "attempts/wave19-n3-60-structural/exact_check.py":
        "c7564eef0f1c62165c91a36071ab34b494ead891877011e755407ad48adee460",
    "attempts/wave19-n3-60-structural/exact-checks.json":
        "fc884ea131b1b6c926d9e71ddb1f7925e15c39498f1d7b72819a6473b39ab8dd",
    "attempts/wave19-n3-60-structural/test_exact_check.py":
        "1b1d2628d6c2d837dec24ec679d579676b5a0e66962e0266cee2642040bf6165",
    "attempts/wave19-n3-60-structural/failed-attempts.md":
        "62d43cdb66c599c8c1e1618ca54267c1bf08ba20ad175e04883349cf6f876a0e",
    "attempts/wave19-n3-60-structural/residual-certificates.json":
        "3396b3b67b944b86bfd0d51e8beca25dfc9350815269c62cda4fa7c22a7a5c8b",
}


class CheckError(ValueError):
    """A semantic or arithmetic invariant failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def authenticate_inputs() -> dict[str, Any]:
    rows = []
    for relative, expected in PINNED_INPUTS.items():
        path = ROOT / relative
        actual = sha256_file(path)
        rows.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "match": actual == expected,
            }
        )
    if not all(row["match"] for row in rows):
        bad = [row["path"] for row in rows if not row["match"]]
        raise CheckError(f"pinned input mismatch: {bad}")
    return {
        "all_match": True,
        "files": rows,
        "executed_premise_replays": [
            {
                "command": (
                    r".venv\Scripts\python.exe -B "
                    r"attempts\wave15-global-lift\verify_subset_moment_certificate.py "
                    r"attempts\wave15-global-lift\subset-moment-certificate.json"
                ),
                "result": "PASS; 9 size profiles; discovery label remained DERIVED",
            },
            {
                "command": (
                    r".venv\Scripts\python.exe -B "
                    r"attempts\wave16-n3-51-structural\exact_check.py "
                    r"--verify attempts\wave16-n3-51-structural\exact-checks.json"
                ),
                "result": (
                    "PASS; 16 raw profiles and 4 d_K>=4 survivors at sum(q)=34"
                ),
            },
        ],
    }


def nondedecreasing_partitions(
    total: int,
    length: int,
    minimum: int = 2,
    maximum: int | None = None,
    start: int | None = None,
) -> Iterator[tuple[int, ...]]:
    """Generate fixed-length nondecreasing positive integer partitions."""
    if length == 0:
        if total == 0:
            yield ()
        return
    if maximum is None:
        maximum = total
    if start is None:
        start = minimum
    low = max(minimum, start)
    high = min(maximum, total // length)
    for first in range(low, high + 1):
        remaining = total - first
        if remaining < first * (length - 1):
            continue
        if remaining > maximum * (length - 1):
            continue
        for tail in nondedecreasing_partitions(
            remaining, length - 1, minimum, maximum, first
        ):
            yield (first,) + tail


def q_profiles_partition_method(
    total: int = 40,
) -> tuple[dict[int, int], list[tuple[int, tuple[int, ...]]]]:
    """Enumerate all raw partitions, then filter by d_K(T)>=4."""
    raw_counts: dict[int, int] = {}
    survivors = []
    for r in range(1, total // 2 + 1):
        raw = list(nondedecreasing_partitions(total, r, minimum=2))
        raw_counts[r] = len(raw)
        for profile in raw:
            if all(r - 1 - 3 * q >= 4 for q in profile):
                survivors.append((r, profile))
    return raw_counts, survivors


def q_profiles_histogram_method(
    total: int = 40,
) -> list[tuple[int, tuple[int, ...]]]:
    """Solve count and weight equations over q-value histograms."""
    results: list[tuple[int, tuple[int, ...]]] = []
    for r in range(1, total // 2 + 1):
        cap = (r - 5) // 3
        if cap < 2:
            continue
        values = list(range(2, cap + 1))

        def visit(
            index: int,
            remaining_count: int,
            remaining_weight: int,
            counts: list[int],
        ) -> None:
            if index == len(values):
                if remaining_count == 0 and remaining_weight == 0:
                    profile = tuple(
                        value
                        for value, count in zip(values, counts)
                        for _ in range(count)
                    )
                    results.append((r, profile))
                return
            value = values[index]
            max_count = min(remaining_count, remaining_weight // value)
            for count in range(max_count + 1):
                next_count = remaining_count - count
                next_weight = remaining_weight - count * value
                if index + 1 < len(values):
                    remaining_values = values[index + 1 :]
                    if next_weight < next_count * min(remaining_values):
                        continue
                    if next_weight > next_count * max(remaining_values):
                        continue
                elif next_count or next_weight:
                    continue
                visit(index + 1, next_count, next_weight, counts + [count])

        visit(0, r, total, [])
    return sorted(set(results))


def format_multiset(values: Sequence[int]) -> str:
    pieces = []
    for value, count in sorted(Counter(values).items()):
        pieces.append(str(value) if count == 1 else f"{value}^{count}")
    return " ".join(pieces)


def profile_row(r: int, profile: tuple[int, ...]) -> dict[str, Any]:
    dk = tuple(sorted(r - 1 - 3 * q for q in profile))
    return {
        "r": r,
        "q_values": list(profile),
        "q_multiset": format_multiset(profile),
        "d_K_values": list(dk),
        "d_K_multiset": format_multiset(dk),
        "point_count_cap": 3 * r // 2,
        "checks": {
            "entry_minimum_2": min(profile) >= 2,
            "sum_q_40": sum(profile) == 40,
            "all_d_K_at_least_4": min(dk) >= 4,
            "incidence_cap_formula": 2 * (3 * r // 2) <= 3 * r,
        },
    }


def weakened_q_profiles(minimum_dk: int) -> list[tuple[int, tuple[int, ...]]]:
    _, raw = q_profiles_partition_method()
    if minimum_dk == 4:
        return raw
    results = []
    for r in range(1, 21):
        for profile in nondedecreasing_partitions(40, r, minimum=2):
            if all(r - 1 - 3 * q >= minimum_dk for q in profile):
                results.append((r, profile))
    return results


def profile_mutations(
    profiles: Sequence[tuple[int, tuple[int, ...]]],
) -> list[dict[str, Any]]:
    """Change one histogram unit while preserving the label count r."""
    rows = []
    for r, profile in profiles:
        counts = Counter(profile)
        for source in sorted(counts):
            targets = [source - 1, source + 1]
            for target in targets:
                if target < 2:
                    continue
                mutated = counts.copy()
                mutated[source] -= 1
                if mutated[source] == 0:
                    del mutated[source]
                mutated[target] += 1
                values = tuple(
                    value
                    for value, count in sorted(mutated.items())
                    for _ in range(count)
                )
                reasons = []
                if len(values) != r:
                    reasons.append("label_count")
                if sum(values) != 40:
                    reasons.append("sum_q")
                if any(r - 1 - 3 * q < 4 for q in values):
                    reasons.append("d_K")
                if not reasons:
                    raise CheckError(
                        f"one-unit profile mutation unexpectedly survived: {r}, {values}"
                    )
                rows.append(
                    {
                        "source": {"r": r, "q": format_multiset(profile)},
                        "mutation": f"one label q={source} -> q={target}",
                        "preserved_equation": "number of active labels r",
                        "rejected_by": reasons,
                    }
                )
    return rows


def labeled_orbit_size(profile: Sequence[int]) -> int:
    result = math.factorial(len(profile))
    for count in Counter(profile).values():
        result //= math.factorial(count)
    return result


def profile_canonicalization_tests(
    profiles: Sequence[tuple[int, tuple[int, ...]]],
) -> dict[str, Any]:
    rows = []
    for r, profile in profiles:
        variants = [
            tuple(reversed(profile)),
            profile[1:] + profile[:1],
            tuple(profile[index] for index in range(0, r, 2))
            + tuple(profile[index] for index in range(1, r, 2)),
        ]
        if any(tuple(sorted(variant)) != profile for variant in variants):
            raise CheckError("profile relabeling changed its canonical multiset")
        rows.append(
            {
                "r": r,
                "q": format_multiset(profile),
                "tested_relabelings": len(variants),
                "labeled_orbit_size": labeled_orbit_size(profile),
                "canonical_collision": False,
            }
        )
    homogeneous = [
        (r, profile) for r, profile in profiles if len(set(profile)) == 1
    ]
    if len(homogeneous) >= len(profiles):
        raise CheckError("hostile homogeneity restriction did not shrink space")
    return {
        "canonical_relabeling_rows": rows,
        "unlabeled_to_labeled_mapping": (
            "Every labeled assignment has exactly one sorted multiset; the "
            "orbit size is r!/product(count(q)!)."
        ),
        "hostile_automorphism_restriction": {
            "restriction": "force all active labels to have the same q",
            "unrestricted_multiset_count": len(profiles),
            "restricted_multiset_count": len(homogeneous),
            "restricted_survivors": [
                {"r": r, "q": format_multiset(profile)}
                for r, profile in homogeneous
            ],
            "result": "REJECTED_AS_SPACE_CHANGING",
        },
    }


def d_k_degree_three_obstruction() -> dict[str, Any]:
    """Finite replay of the two external-point assignments in the d_K=3 case."""
    available = ("b", "c")
    assignments = []
    for first in available:
        second = next(value for value in available if value != first)
        points = [
            frozenset(("x", "a")),
            frozenset(("x", first)),
            frozenset(("a", first)),
            frozenset(("a", second)),
        ]
        triple = points[:3]
        intersections = [
            tuple(sorted(triple[i] & triple[j]))
            for i, j in ((0, 1), (0, 2), (1, 2))
        ]
        distinct_singletons = sorted(value[0] for value in intersections)
        if distinct_singletons != sorted(("x", "a", first)):
            raise CheckError("degree-three obstruction did not form a Berge triple")
        assignments.append(
            {
                "ordered_external_assignment": [first, second],
                "forbidden_points": [sorted(point) for point in triple],
                "pairwise_intersection_labels": distinct_singletons,
                "result": "REJECTED_BY_NO_BERGE_TRIANGLE",
            }
        )
    return {
        "scope": "one active label x with d_K(x)=3",
        "semantic_steps": [
            "Each label lies in three non-singleton points; their nonempty external parts are pairwise disjoint K-neighbor sets, so d_K(x)>=3.",
            "The three non-singleton linear points through x use its three K-neighbors once each.",
            "For point {x,a}, the two other points through label a have nonempty disjoint external parts.",
            "After deleting a on the actual meeting edges, the two-sided rule confines those parts to {b,c}.",
            "The only ordered assignments create {x,a},{x,b},{a,b} or its b/c relabeling.",
        ],
        "ordered_assignments_checked": assignments,
        "conclusion": "d_K=3 is impossible; d_K>=4 is authenticated",
    }


def size_two_endpoint_table() -> list[dict[str, Any]]:
    """Derive the local fixed-sum alternatives used by every degree bound."""
    rows = []
    for first in range(2, 5):
        for second in range(first, 5):
            fixed_sum = 2 * (first + second)
            if fixed_sum % 4:
                rows.append(
                    {
                        "q_pair": [first, second],
                        "fixed_sum": fixed_sum,
                        "possible": False,
                        "reason": (
                            "Every actual edge at a size-two endpoint has "
                            "d_H in {0,4}, so its neighbor sum is divisible by four."
                        ),
                    }
                )
                continue
            positive_disjoint_neighbors = fixed_sum // 4
            rows.append(
                {
                    "q_pair": [first, second],
                    "fixed_sum": fixed_sum,
                    "possible": True,
                    "positive_disjoint_neighbors": positive_disjoint_neighbors,
                    "meeting_neighbors": 4,
                    "induced_degree_lower": 4 + positive_disjoint_neighbors,
                }
            )
    expected = [
        ([2, 2], True, 6),
        ([2, 3], False, None),
        ([2, 4], True, 7),
        ([3, 3], True, 7),
        ([3, 4], False, None),
        ([4, 4], True, 8),
    ]
    observed = [
        (
            row["q_pair"],
            row["possible"],
            row.get("induced_degree_lower"),
        )
        for row in rows
    ]
    if observed != expected:
        raise CheckError("size-two endpoint table mismatch")
    return rows


def excess_partitions(total: int, maximum: int | None = None) -> Iterator[tuple[int, ...]]:
    """Positive integer partitions in nonincreasing order."""
    if total == 0:
        yield ()
        return
    if maximum is None:
        maximum = total
    for first in range(min(total, maximum), 0, -1):
        for tail in excess_partitions(total - first, first):
            yield (first,) + tail


def point_profiles_partition_method(r: int, m: int) -> list[tuple[int, ...]]:
    excess = 3 * r - 2 * m
    if excess < 0:
        return []
    results = []
    for partition in excess_partitions(excess):
        if len(partition) <= m:
            sizes = tuple(sorted([2 + value for value in partition] + [2] * (m - len(partition))))
            results.append(sizes)
    return sorted(set(results))


def point_profiles_histogram_method(r: int, m: int) -> list[tuple[int, ...]]:
    excess = 3 * r - 2 * m
    if excess < 0:
        return []
    results: list[tuple[int, ...]] = []

    def visit(
        extra: int,
        remaining_excess: int,
        remaining_slots: int,
        counts: dict[int, int],
    ) -> None:
        if remaining_excess == 0:
            sizes = [2] * remaining_slots
            for increment, count in counts.items():
                sizes.extend([2 + increment] * count)
            if len(sizes) == m and sum(sizes) == 3 * r:
                results.append(tuple(sorted(sizes)))
            return
        if extra > remaining_excess or remaining_slots == 0:
            return
        max_count = min(remaining_slots, remaining_excess // extra)
        for count in range(max_count + 1):
            next_counts = dict(counts)
            if count:
                next_counts[extra] = count
            visit(
                extra + 1,
                remaining_excess - extra * count,
                remaining_slots - count,
                next_counts,
            )

    visit(1, excess, m, {})
    return sorted(set(results))


def point_profile_row(sizes: Sequence[int]) -> dict[str, Any]:
    return {
        "sizes": list(sizes),
        "multiset": format_multiset(sizes),
        "point_count": len(sizes),
        "incidence_sum": sum(sizes),
    }


def crossing_counts_formula(left_size: int, right_size: int) -> tuple[int, ...]:
    """Possible edge totals in a simple bipartite graph with degrees 0 or 2."""
    smaller = min(left_size, right_size)
    counts = {0}
    # A nonempty support has equally many active vertices on both sides.
    # For every k>=2, an alternating 2k-cycle realizes 2k edges.
    for active_per_side in range(2, smaller + 1):
        counts.add(2 * active_per_side)
    return tuple(sorted(counts))


def crossing_counts_bitmask(left_size: int, right_size: int) -> tuple[int, ...]:
    cells = left_size * right_size
    if cells > 18:
        raise CheckError("bit-mask crossing enumeration intentionally capped at 18 cells")
    possible = set()
    for mask in range(1 << cells):
        row_degrees = [0] * left_size
        column_degrees = [0] * right_size
        edge_count = 0
        for row in range(left_size):
            for column in range(right_size):
                bit = row * right_size + column
                if mask & (1 << bit):
                    row_degrees[row] += 1
                    column_degrees[column] += 1
                    edge_count += 1
        if all(degree in (0, 2) for degree in row_degrees + column_degrees):
            possible.add(edge_count)
    return tuple(sorted(possible))


def canon_edge(first: Any, second: Any) -> tuple[Any, Any]:
    return tuple(sorted((first, second), key=lambda item: (type(item).__name__, repr(item))))  # type: ignore[return-value]


def validate_simple_graph(
    vertices: Iterable[Any],
    edges: Sequence[Sequence[Any]],
    expected_degree: int | None = None,
    triangle_free: bool = False,
) -> dict[str, Any]:
    vertex_set = set(vertices)
    canonical = []
    for raw in edges:
        if len(raw) != 2:
            raise CheckError("edge must have exactly two endpoints")
        first, second = raw
        if first == second:
            raise CheckError("loop rejected")
        if first not in vertex_set or second not in vertex_set:
            raise CheckError("edge endpoint outside vertex set")
        canonical.append(canon_edge(first, second))
    if len(set(canonical)) != len(canonical):
        raise CheckError("parallel edge rejected")
    adjacency = {vertex: set() for vertex in vertex_set}
    for first, second in canonical:
        adjacency[first].add(second)
        adjacency[second].add(first)
    degrees = {vertex: len(neighbors) for vertex, neighbors in adjacency.items()}
    if expected_degree is not None and any(
        degree != expected_degree for degree in degrees.values()
    ):
        raise CheckError("degree condition rejected")
    triangles = []
    ordered_vertices = sorted(vertex_set, key=repr)
    for first, second, third in itertools.combinations(ordered_vertices, 3):
        if (
            second in adjacency[first]
            and third in adjacency[first]
            and third in adjacency[second]
        ):
            triangles.append((first, second, third))
    if triangle_free and triangles:
        raise CheckError("triangle-free condition rejected")
    unseen = set(vertex_set)
    components = []
    while unseen:
        start = next(iter(unseen))
        queue = deque([start])
        component = set()
        while queue:
            vertex = queue.popleft()
            if vertex in component:
                continue
            component.add(vertex)
            queue.extend(adjacency[vertex] - component)
        unseen -= component
        components.append(component)
    return {
        "vertex_count": len(vertex_set),
        "edge_count": len(canonical),
        "degree_multiset": sorted(degrees.values()),
        "triangle_count": len(triangles),
        "component_count": len(components),
        "connectedness_imposed": False,
    }


def normalized_cross_edges(
    left: set[Any],
    right: set[Any],
    l_edges: Sequence[Sequence[Any]],
) -> list[tuple[Any, Any]]:
    raw_canonical = []
    for edge in l_edges:
        if len(edge) != 2:
            raise CheckError("L edge must have exactly two endpoints")
        first, second = edge
        if first == second:
            raise CheckError("L loop rejected")
        raw_canonical.append(canon_edge(first, second))
    if len(raw_canonical) != len(set(raw_canonical)):
        raise CheckError("parallel L edge rejected")
    crossing = []
    for first, second in raw_canonical:
        if first in left and second in right:
            crossing.append((first, second))
        elif second in left and first in right:
            crossing.append((second, first))
    return crossing


def validate_endpoint_record(
    points: Mapping[Any, Iterable[Any]],
    actual_edges: Sequence[Sequence[Any]],
    l_edges: Sequence[Sequence[Any]],
    record: Mapping[str, Any],
) -> dict[str, Any]:
    endpoints = record.get("endpoints")
    if not isinstance(endpoints, list) or len(endpoints) != 2:
        raise CheckError("an endpoint record must name exactly two endpoints")
    u, v = endpoints
    if u == v:
        raise CheckError("an actual edge cannot count one endpoint twice")
    actual = [canon_edge(*edge) for edge in actual_edges]
    if len(actual) != len(set(actual)):
        raise CheckError("parallel actual edge rejected")
    if canon_edge(u, v) not in set(actual):
        raise CheckError("endpoint record is not an actual edge")
    if u not in points or v not in points:
        raise CheckError("endpoint has no declared point")
    point_u, point_v = set(points[u]), set(points[v])
    declared = record.get("declared_points")
    if (
        not isinstance(declared, list)
        or len(declared) != 2
        or set(declared[0]) != point_u
        or set(declared[1]) != point_v
    ):
        raise CheckError("inconsistent endpoint labels")
    common = point_u & point_v
    if len(common) > 1:
        raise CheckError("point linearity rejected")
    left = point_u - common
    right = point_v - common
    expected_crossing = normalized_cross_edges(left, right, l_edges)
    declared_crossing = record.get("cross_edges")
    if not isinstance(declared_crossing, list):
        raise CheckError("crossing edge list omitted")
    declared_pairs = []
    for edge in declared_crossing:
        if len(edge) != 2:
            raise CheckError("crossing edge must have two labels")
        declared_pairs.append((edge[0], edge[1]))
    if len(declared_pairs) != len(set(declared_pairs)):
        raise CheckError("parallel crossing edge rejected")
    if set(declared_pairs) != set(expected_crossing):
        raise CheckError("crossing/noncrossing label mismatch")
    row_degrees = Counter(first for first, _ in expected_crossing)
    column_degrees = Counter(second for _, second in expected_crossing)
    all_degrees = [
        row_degrees.get(label, 0) for label in left
    ] + [
        column_degrees.get(label, 0) for label in right
    ]
    if any(degree not in (0, 2) for degree in all_degrees):
        raise CheckError("two-sided zero-or-two rule rejected")
    claimed = record.get("d_H")
    if claimed != len(expected_crossing):
        raise CheckError("claimed d_H differs from crossing edge count")
    return {
        "endpoints": [u, v],
        "common_labels_deleted_at_both_endpoints": sorted(common, key=repr),
        "remaining_shape": [len(left), len(right)],
        "d_H": claimed,
        "row_degrees": sorted(row_degrees.values()),
        "column_degrees": sorted(column_degrees.values()),
    }


def validate_neighbor_ledger(
    expected_neighbors: Iterable[Any],
    records: Sequence[Mapping[str, Any]],
    claimed_sum: int,
) -> int:
    expected = set(expected_neighbors)
    observed = [record.get("neighbor") for record in records]
    if len(observed) != len(set(observed)):
        raise CheckError("an endpoint was counted twice")
    if set(observed) != expected:
        raise CheckError("an endpoint was omitted or introduced")
    total = sum(int(record["d_H"]) for record in records)
    if total != claimed_sum:
        raise CheckError("endpoint ledger sum mismatch")
    return total


def endpoint_semantic_harness() -> dict[str, Any]:
    points = {
        "u": {"a", "b"},
        "v": {"c", "d"},
        "w": {"x", "a", "b"},
        "z": {"x", "c", "d"},
    }
    l_edges = [["a", "c"], ["a", "d"], ["b", "c"], ["b", "d"]]
    actual_edges = [["u", "v"], ["w", "z"]]
    disjoint = {
        "endpoints": ["u", "v"],
        "declared_points": [["a", "b"], ["c", "d"]],
        "cross_edges": l_edges,
        "d_H": 4,
    }
    meeting = {
        "endpoints": ["w", "z"],
        "declared_points": [["x", "a", "b"], ["x", "c", "d"]],
        "cross_edges": l_edges,
        "d_H": 4,
    }
    swapped = {
        "endpoints": ["v", "u"],
        "declared_points": [["c", "d"], ["a", "b"]],
        "cross_edges": [["c", "a"], ["d", "a"], ["c", "b"], ["d", "b"]],
        "d_H": 4,
    }
    valid_rows = [
        validate_endpoint_record(points, actual_edges, l_edges, disjoint),
        validate_endpoint_record(points, actual_edges, l_edges, meeting),
        validate_endpoint_record(points, actual_edges, l_edges, swapped),
    ]
    if valid_rows[0]["d_H"] != valid_rows[2]["d_H"]:
        raise CheckError("endpoint swap changed the undirected crossing count")

    mutation_builders = {
        "endpoint_counted_twice": lambda: validate_endpoint_record(
            points,
            actual_edges,
            l_edges,
            {
                **disjoint,
                "endpoints": ["u", "u"],
                "declared_points": [["a", "b"], ["a", "b"]],
            },
        ),
        "endpoint_omitted": lambda: validate_endpoint_record(
            points, actual_edges, l_edges, {**disjoint, "endpoints": ["u"]}
        ),
        "inconsistent_endpoint_labels": lambda: validate_endpoint_record(
            points,
            actual_edges,
            l_edges,
            {**disjoint, "declared_points": [["a", "e"], ["c", "d"]]},
        ),
        "crossing_label_flip": lambda: validate_endpoint_record(
            points,
            actual_edges,
            l_edges,
            {
                **disjoint,
                "cross_edges": [["a", "c"], ["a", "d"], ["b", "c"], ["b", "e"]],
            },
        ),
        "crossing_edge_omitted": lambda: validate_endpoint_record(
            points,
            actual_edges,
            l_edges,
            {**disjoint, "cross_edges": l_edges[:-1], "d_H": 3},
        ),
        "parallel_crossing_edge": lambda: validate_endpoint_record(
            points,
            actual_edges,
            l_edges,
            {**disjoint, "cross_edges": l_edges + [l_edges[0]], "d_H": 5},
        ),
        "L_loop": lambda: validate_endpoint_record(
            points, actual_edges, l_edges + [["a", "a"]], disjoint
        ),
        "L_parallel_edge": lambda: validate_endpoint_record(
            points, actual_edges, l_edges + [["c", "a"]], disjoint
        ),
    }
    mutation_rows = []
    for name, builder in mutation_builders.items():
        try:
            builder()
        except CheckError as error:
            mutation_rows.append(
                {"mutation": name, "result": "REJECTED", "reason": str(error)}
            )
        else:
            raise CheckError(f"endpoint mutation unexpectedly survived: {name}")

    valid_ledger = [
        {"neighbor": "n1", "d_H": 4},
        {"neighbor": "n2", "d_H": 0},
        {"neighbor": "n3", "d_H": 4},
    ]
    validate_neighbor_ledger(("n1", "n2", "n3"), valid_ledger, 8)
    ledger_mutations = {
        "duplicate_n1_omit_n2": [valid_ledger[0], valid_ledger[0], valid_ledger[2]],
        "omit_n2": [valid_ledger[0], valid_ledger[2]],
    }
    for name, records in ledger_mutations.items():
        try:
            validate_neighbor_ledger(("n1", "n2", "n3"), records, 8)
        except CheckError as error:
            mutation_rows.append(
                {"mutation": name, "result": "REJECTED", "reason": str(error)}
            )
        else:
            raise CheckError(f"ledger mutation unexpectedly survived: {name}")

    return {
        "primitive_semantics": (
            "For an actual edge uv, delete the unique common active label from "
            "both indexed points; if P' and Q' are the remaining label sets, "
            "then d_H(uv)=e_L(P',Q') is the number of L-edges crossing them. "
            "Every remaining row and column has degree zero or two."
        ),
        "local_to_global_equality": (
            "The fixed-point sum is a ledger over the distinct original "
            "neighbors v of u. Each crossing is computed once from the two "
            "authenticated endpoint points, so summing the local crossing "
            "counts is exactly sum_{v~u} d_H(uv), with no support multiplicity."
        ),
        "valid_tiny_cases": valid_rows,
        "endpoint_swap_result": "RETAINED_WITH_TRANSPOSED_CROSSING",
        "valid_ledger_sum": 8,
        "hostile_mutations": mutation_rows,
    }


def graph_hostile_harness() -> dict[str, Any]:
    left, right = range(3), range(3, 6)
    k33_edges = [[u, v] for u in left for v in right]
    base = validate_simple_graph(range(6), k33_edges, 3, triangle_free=True)
    switched_edges = [
        edge
        for edge in k33_edges
        if canon_edge(*edge) not in {canon_edge(0, 3), canon_edge(1, 4)}
    ] + [[0, 1], [3, 4]]
    switched_degree_only = validate_simple_graph(range(6), switched_edges, 3)
    try:
        validate_simple_graph(range(6), switched_edges, 3, triangle_free=True)
    except CheckError as error:
        switch_result = {"result": "REJECTED", "reason": str(error)}
    else:
        raise CheckError("triangle-creating 2-switch survived triangle-free check")

    petersen = []
    for i in range(5):
        petersen.append([i, (i + 1) % 5])
        petersen.append([5 + i, 5 + ((i + 2) % 5)])
        petersen.append([i, 5 + i])
    double_petersen = petersen + [[u + 10, v + 10] for u, v in petersen]
    disconnected = validate_simple_graph(
        range(20), double_petersen, 3, triangle_free=True
    )
    if disconnected["component_count"] != 2:
        raise CheckError("disconnected cubic control was not disconnected")

    impostors = {}
    for name, edges in {
        "loop": k33_edges + [[0, 0]],
        "parallel": k33_edges + [[3, 0]],
    }.items():
        try:
            validate_simple_graph(range(6), edges, 3)
        except CheckError as error:
            impostors[name] = {"result": "REJECTED", "reason": str(error)}
        else:
            raise CheckError(f"graph impostor survived: {name}")

    return {
        "K3,3_control": base,
        "degree_preserving_2_switch": {
            "degree_only_result": switched_degree_only,
            "triangle_free_result": switch_result,
            "significance": "degree sequence alone does not enforce no-Berge/triangle-free",
        },
        "disconnected_double_Petersen": {
            **disconnected,
            "result": "RETAINED",
            "significance": "connectivity is not imposed anywhere in the reductions",
        },
        "impostors": impostors,
    }


def subset_upper(m: int) -> Fraction:
    return Fraction(3 * m, 1) + Fraction(m * m, 9)


def even_floor(value: Fraction) -> int:
    integer = value.numerator // value.denominator
    return integer if integer % 2 == 0 else integer - 1


def spectral_replay() -> dict[str, Any]:
    # From A^2=12I-A+2J, restricted eigenvalues solve theta^2+theta-12.
    roots = (-4, 3)
    rows = []
    for m in range(1, 31):
        upper = subset_upper(m)
        max_degree_sum = even_floor(upper)
        rows.append(
            {
                "m": m,
                "upper_fraction": f"{upper.numerator}/{upper.denominator}",
                "maximum_even_degree_sum": max_degree_sum,
                "baseline_6m": 6 * m,
                "maximum_excess_T": max_degree_sum - 6 * m,
            }
        )
    first_allowed = next(row["m"] for row in rows if row["maximum_excess_T"] >= 0)
    if first_allowed != 27:
        raise CheckError("spectral minimum-order replay failed")
    return {
        "target_matrix_equation": "A^2=12I-A+2J",
        "restricted_eigenvalues": list(roots),
        "indicator_decomposition": (
            "1_X=(m/99)1+y with y perpendicular to 1; use the largest "
            "restricted eigenvalue 3"
        ),
        "subset_bound": "2e(G[X]) <= 3m+m^2/9",
        "first_order_compatible_with_minimum_degree_6": first_allowed,
        "rows_m_27_to_30": [row for row in rows if 27 <= row["m"] <= 30],
    }


def outside_moments_target(m: int, excesses: Sequence[int]) -> tuple[int, int]:
    t_value = sum(excesses)
    u_value = sum(value * value for value in excesses)
    first = 8 * m - t_value
    second = 2 * m * m - 30 * m - 13 * t_value - u_value
    return first, second


def outside_moments_general(
    v: int,
    k: int,
    lam: int,
    mu: int,
    internal_degrees: Sequence[int],
) -> tuple[int, int]:
    m = len(internal_degrees)
    internal_edges_twice = sum(internal_degrees)
    if internal_edges_twice % 2:
        raise CheckError("internal degree sum must be even")
    internal_edges = internal_edges_twice // 2
    first = k * m - internal_edges_twice
    total_pair_common = (
        lam * internal_edges
        + mu * (math.comb(m, 2) - internal_edges)
    )
    inside_pair_contribution = sum(
        degree * (degree - 1) // 2 for degree in internal_degrees
    )
    outside_choose_two = total_pair_common - inside_pair_contribution
    second = first + 2 * outside_choose_two
    if v - m < 0:
        raise CheckError("subset exceeds graph order")
    return first, second


def c5_outside_moment_toy() -> dict[str, Any]:
    adjacency = {
        vertex: {(vertex - 1) % 5, (vertex + 1) % 5} for vertex in range(5)
    }
    rows = []
    for mask in range(1 << 5):
        subset = {vertex for vertex in range(5) if mask & (1 << vertex)}
        internal = [
            len(adjacency[vertex] & subset) for vertex in sorted(subset)
        ]
        outside = [
            len(adjacency[vertex] & subset)
            for vertex in range(5)
            if vertex not in subset
        ]
        derived = outside_moments_general(5, 2, 0, 1, internal)
        direct = (sum(outside), sum(value * value for value in outside))
        if derived != direct:
            raise CheckError(f"C5 outside moment mismatch at mask {mask}")
        rows.append(
            {
                "mask": mask,
                "m": len(subset),
                "direct": list(direct),
                "derived": list(derived),
            }
        )
    return {
        "toy_srg": "C5 = srg(5,2,0,1)",
        "subsets_checked": len(rows),
        "all_direct_counts_match": True,
        "sample_rows": rows[:4] + rows[-4:],
    }


def balanced_min_square(count: int, total: int) -> tuple[int, list[int]]:
    quotient, remainder = divmod(total, count)
    witness = [quotient] * (count - remainder) + [quotient + 1] * remainder
    return sum(value * value for value in witness), witness


def min_square_dp(count: int, total: int, maximum: int = 14) -> int:
    infinity = 10**18
    costs = [infinity] * (total + 1)
    costs[0] = 0
    for _ in range(count):
        next_costs = [infinity] * (total + 1)
        for subtotal, cost in enumerate(costs):
            if cost == infinity:
                continue
            for value in range(min(maximum, total - subtotal) + 1):
                candidate = cost + value * value
                if candidate < next_costs[subtotal + value]:
                    next_costs[subtotal + value] = candidate
        costs = next_costs
    return costs[total]


def fixed_square_witness(
    count: int, square_total: int, maximum: int = 14
) -> list[int]:
    states: list[dict[int, tuple[int, int]]] = [{0: (-1, -1)}]
    for _ in range(count):
        previous = states[-1]
        current: dict[int, tuple[int, int]] = {}
        for subtotal in previous:
            for value in range(maximum + 1):
                new_total = subtotal + value * value
                if new_total <= square_total and new_total not in current:
                    current[new_total] = (subtotal, value)
        states.append(current)
    if square_total not in states[-1]:
        raise CheckError("no fixed-square witness found")
    values = []
    subtotal = square_total
    for index in range(count, 0, -1):
        previous_total, value = states[index][subtotal]
        values.append(value)
        subtotal = previous_total
    return list(reversed(values))


def validate_histogram_moments(
    values: Sequence[int], count: int, first: int, second: int
) -> None:
    if len(values) != count:
        raise CheckError("outside population mismatch")
    if any(value < 0 or value > 14 for value in values):
        raise CheckError("outside degree outside 0..14")
    if sum(values) != first:
        raise CheckError("outside first moment mismatch")
    if sum(value * value for value in values) != second:
        raise CheckError("outside second moment mismatch")


def outside_histogram_hostile_harness() -> dict[str, Any]:
    count, target_first, target_second = 70, 226, 698
    minimum, balanced = balanced_min_square(count, target_first)
    if minimum != min_square_dp(count, target_first):
        raise CheckError("balanced and dynamic-programming square minima differ")
    if minimum != 742:
        raise CheckError("unexpected m=29 outside minimum")

    fixed_second = fixed_square_witness(count, target_second)
    mutations = []
    for name, values in {
        "correct_population_and_first_wrong_second": balanced,
        "correct_population_and_second_wrong_first": fixed_second,
        "correct_population_wrong_both": [3] * count,
    }.items():
        try:
            validate_histogram_moments(
                values, count, target_first, target_second
            )
        except CheckError as error:
            mutations.append(
                {
                    "mutation": name,
                    "population": len(values),
                    "first": sum(values),
                    "second": sum(value * value for value in values),
                    "result": "REJECTED",
                    "reason": str(error),
                }
            )
        else:
            raise CheckError(f"outside histogram mutation survived: {name}")

    collision_a = [0, 3, 3] + [3] * 67
    collision_b = [1, 1, 4] + [3] * 67
    collision_moments_a = (
        len(collision_a),
        sum(collision_a),
        sum(value * value for value in collision_a),
    )
    collision_moments_b = (
        len(collision_b),
        sum(collision_b),
        sum(value * value for value in collision_b),
    )
    if collision_moments_a != collision_moments_b:
        raise CheckError("moment-collision control does not collide")
    if Counter(collision_a) == Counter(collision_b):
        raise CheckError("moment-collision controls have equal histograms")

    return {
        "target_impossible_row": {
            "population": count,
            "first": target_first,
            "second": target_second,
            "unrestricted_integer_minimum_second": minimum,
        },
        "mutations": mutations,
        "moment_collision_retained": {
            "histogram_a": dict(sorted(Counter(collision_a).items())),
            "histogram_b": dict(sorted(Counter(collision_b).items())),
            "common_population_first_second": list(collision_moments_a),
            "result": "RETAINED_AS_TWO_DISTINCT_NECESSARY-MOMENT_WITNESSES",
            "limitation": "first and second moments do not determine a histogram",
        },
    }


def simple_regular_graphs(n: int, degree: int) -> list[list[tuple[int, int]]]:
    possible_edges = list(itertools.combinations(range(n), 2))
    target_edges = n * degree // 2
    results = []
    for chosen in itertools.combinations(possible_edges, target_edges):
        degrees = Counter(vertex for edge in chosen for vertex in edge)
        if all(degrees[vertex] == degree for vertex in range(n)):
            results.append(list(chosen))
    return results


def four_vertex_dense_graph_lemma() -> dict[str, Any]:
    possible = list(itertools.combinations(range(4), 2))
    checked = []
    for edge_count in (5, 6):
        for edges in itertools.combinations(possible, edge_count):
            edge_set = {canon_edge(*edge) for edge in edges}
            triangles = [
                triple
                for triple in itertools.combinations(range(4), 3)
                if all(canon_edge(*edge) in edge_set for edge in itertools.combinations(triple, 2))
            ]
            shared_pairs = []
            for first, second in itertools.combinations(triangles, 2):
                common = set(first) & set(second)
                if len(common) == 2 and canon_edge(*common) in edge_set:
                    shared_pairs.append([list(first), list(second)])
            if not shared_pairs:
                raise CheckError("dense four-vertex graph lacks edge-sharing triangles")
            checked.append(
                {
                    "edges": [list(edge) for edge in edges],
                    "triangle_count": len(triangles),
                    "edge_sharing_triangle_pair": shared_pairs[0],
                }
            )
    return {
        "labeled_graphs_checked": len(checked),
        "edge_counts": [5, 6],
        "all_have_two_triangles_sharing_an_edge": True,
        "witnesses": checked,
    }


def build_exclusions(
    profiles: Sequence[tuple[int, tuple[int, ...]]],
    point_profile_map: Mapping[tuple[int, int], list[tuple[int, ...]]],
) -> dict[str, Any]:
    profile_by_r: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for r, profile in profiles:
        profile_by_r[r].append(profile)

    through_17 = []
    for r in range(1, 18):
        for profile in profile_by_r.get(r, []):
            cap = 3 * r // 2
            if cap >= 27:
                raise CheckError("r<=17 incidence cap failed")
            through_17.append(
                {
                    "r": r,
                    "q": format_multiset(profile),
                    "maximum_m_from_non_singletons": cap,
                    "minimum_m_from_delta_6_and_spectrum": 27,
                    "result": "EXCLUDED",
                }
            )

    cubic_two = simple_regular_graphs(2, 3)
    cubic_four = simple_regular_graphs(4, 3)
    if cubic_two or len(cubic_four) != 1:
        raise CheckError("small cubic enumeration mismatch")
    k4_audit = validate_simple_graph(range(4), cubic_four[0], 3)
    if k4_audit["triangle_count"] != 4:
        raise CheckError("unique cubic graph on four vertices is not K4")

    r18_rows = []
    for profile in profile_by_r[18]:
        counts = Counter(profile)
        if counts[4] == 2:
            reason = {
                "type": "q4_point_degree",
                "q4_label_occurrences_in_points": 3 * counts[4],
                "incident_point_minimum_degree": 7,
                "equality_degree": 6,
            }
        elif counts[3] == 2:
            reason = {
                "type": "odd_component_too_small",
                "odd_label_count": 2,
                "required_degree_inside_odd_part": 3,
                "maximum_simple_degree": 1,
                "enumerated_cubic_graph_count": len(cubic_two),
            }
        elif counts[3] == 4:
            reason = {
                "type": "odd_component_forces_K4",
                "odd_label_count": 4,
                "enumerated_cubic_graph_count": len(cubic_four),
                "forced_triangle_count": k4_audit["triangle_count"],
                "contradiction": "no-Berge premise makes F triangle-free",
            }
        else:
            raise CheckError(f"unclassified r=18 profile {profile}")
        r18_rows.append(
            {
                "q": format_multiset(profile),
                "m": 27,
                "point_profiles": [
                    point_profile_row(row) for row in point_profile_map[(18, 27)]
                ],
                "spectral_equality_degree": 6,
                "F_restrictions": [
                    "simple (linearity forbids duplicate size-two points)",
                    "cubic (each label occurs in exactly three points)",
                    "triangle-free (a triangle would be a Berge triangle)",
                    "connectivity not assumed",
                ],
                "reason": reason,
                "result": "EXCLUDED",
            }
        )

    r19_rows = []
    for profile in profile_by_r[19]:
        for m in (27, 28):
            for sizes in point_profile_map[(19, m)]:
                counts = Counter(sizes)
                if m == 27 and max(sizes) >= 4:
                    reason = {
                        "type": "meeting_degree_exceeds_equality",
                        "largest_point": max(sizes),
                        "meeting_degree": 2 * max(sizes),
                        "equality_degree": 6,
                    }
                elif m == 27:
                    if counts != Counter({2: 24, 3: 3}):
                        raise CheckError("unexpected r19,m27 point profile")
                    reason = {
                        "type": "unique_3xsize3_profile",
                        "fixed_sum_lower": 12,
                        "size2_meeting_crossing_max": 0,
                        "other_size3_points": 2,
                        "crossing_max_each": 4,
                        "total_crossing_max": 8,
                    }
                else:
                    if counts != Counter({2: 27, 3: 1}):
                        raise CheckError("unexpected r19,m28 point profile")
                    upper = subset_upper(28)
                    reason = {
                        "type": "unique_size3_degree_parity",
                        "six_size2_meeting_crossings": 0,
                        "positive_disjoint_crossing_size": 4,
                        "fixed_sum_if_divisible_requires_at_least": 3,
                        "size3_degree_lower": 9,
                        "degree_sum_lower_before_parity": 171,
                        "degree_sum_lower_even": 172,
                        "spectral_upper_fraction": f"{upper.numerator}/{upper.denominator}",
                        "maximum_even_degree_sum": even_floor(upper),
                    }
                r19_rows.append(
                    {
                        "q": format_multiset(profile),
                        "m": m,
                        "point_profile": format_multiset(sizes),
                        "reason": reason,
                        "result": "EXCLUDED",
                    }
                )

    dense_lemma = four_vertex_dense_graph_lemma()
    r20_m28_rows = []
    for sizes in point_profile_map[(20, 28)]:
        counts = Counter(sizes)
        if max(sizes) == 6:
            reason = {
                "type": "meeting_excess",
                "forced_excess": 6,
                "spectral_excess_allowance": 2,
            }
        elif max(sizes) == 5:
            reason = {
                "type": "meeting_excess",
                "forced_excess": 4,
                "spectral_excess_allowance": 2,
            }
        elif counts[4] == 2:
            reason = {
                "type": "meeting_excess",
                "forced_excess": 4,
                "spectral_excess_allowance": 2,
            }
        elif counts[4] == 1:
            reason = {
                "type": "size3_fixed_sum_shortfall_after_size4_uses_allowance",
                "size4_forced_excess": 2,
                "remaining_excess_allowance": 0,
                "size3_fixed_sum": 12,
                "only_other_large_meeting_points": 2,
                "maximum_crossing_each": 4,
                "maximum_total": 8,
            }
        elif counts[3] == 4:
            reason = {
                "type": "four_size3_no_Berge_contradiction",
                "total_excess_allowance": 2,
                "six_crossing_excluded_because": (
                    "one 6 requires a second 6 at that endpoint; the two "
                    "disjoint Y-edges contribute at least four degree incidences"
                ),
                "positive_terms_per_Y_point": 3,
                "positive_disjoint_directed_terms_at_most": 2,
                "positive_meeting_edges_on_Y_at_least": 5,
                "dense_graph_lemma": dense_lemma,
                "no_Berge_bridge": (
                    "Each edge-sharing triangle of linear meeting points has "
                    "one common label; the shared point-pair forces the two "
                    "labels equal, putting one label in four points instead of three."
                ),
            }
        else:
            raise CheckError(f"unclassified r20,m28 point profile {sizes}")
        r20_m28_rows.append(
            {
                "point_profile": format_multiset(sizes),
                "reason": reason,
                "result": "EXCLUDED",
            }
        )

    r20_m29_rows = []
    for sizes in point_profile_map[(20, 29)]:
        counts = Counter(sizes)
        if counts[4] == 1:
            t_value, u_value = 6, 36
            first, second = outside_moments_target(
                29, [6] + [0] * 28
            )
            minimum, witness = balanced_min_square(70, first)
            if (first, second, minimum) != (226, 698, 742):
                raise CheckError("unique-size4 outside arithmetic mismatch")
            reason = {
                "type": "unique_size4_outside_moment",
                "meeting_degree": 8,
                "meeting_crossings_to_size2": 0,
                "positive_disjoint_neighbors_required": 4,
                "forced_degree": 12,
                "T": t_value,
                "U": u_value,
                "outside_population": 70,
                "outside_sum": first,
                "outside_square_sum": second,
                "integer_minimum_square_sum_formula": minimum,
                "integer_minimum_square_sum_dp": min_square_dp(70, first),
                "balanced_witness_multiset": format_multiset(witness),
            }
        elif counts[3] == 2:
            cases = []
            for t_value, minimum_u in ((4, 8), (6, 10)):
                # Use a square-minimizing excess vector with the mandatory
                # two size-three excesses at least two.
                if t_value == 4:
                    excesses = [2, 2] + [0] * 27
                else:
                    excesses = [2, 2, 1, 1] + [0] * 25
                first, second = outside_moments_target(29, excesses)
                minimum, witness = balanced_min_square(70, first)
                if sum(value * value for value in excesses) != minimum_u:
                    raise CheckError("two-size3 U minimization mismatch")
                if min_square_dp(70, first) != minimum:
                    raise CheckError("outside square minimizers disagree")
                cases.append(
                    {
                        "T": t_value,
                        "minimum_U": minimum_u,
                        "outside_sum": first,
                        "maximum_outside_square_sum": second,
                        "integer_minimum_square_sum": minimum,
                        "balanced_witness_multiset": format_multiset(witness),
                        "contradiction_gap": minimum - second,
                    }
                )
            if [(row["T"], row["maximum_outside_square_sum"], row["integer_minimum_square_sum"]) for row in cases] != [
                (4, 752, 756),
                (6, 724, 742),
            ]:
                raise CheckError("two-size3 outside arithmetic mismatch")
            reason = {
                "type": "two_size3_outside_moments",
                "local_excess_lemma": (
                    "Each size-three point has excess at least two; equality "
                    "requires the two size-three points to meet with a positive "
                    "four-edge crossing. Otherwise its excess is at least three."
                ),
                "spectral_and_parity_cases": [4, 6],
                "cases": cases,
            }
        else:
            raise CheckError(f"unclassified r20,m29 point profile {sizes}")
        r20_m29_rows.append(
            {
                "point_profile": format_multiset(sizes),
                "reason": reason,
                "result": "EXCLUDED",
            }
        )

    if (
        len(through_17),
        len(r18_rows),
        len(r19_rows),
        len(r20_m28_rows),
        len(r20_m29_rows),
    ) != (7, 3, 8, 5, 2):
        raise CheckError("exclusion coverage row count mismatch")

    return {
        "r_at_most_17": through_17,
        "r18": r18_rows,
        "r19": r19_rows,
        "r20_m28": r20_m28_rows,
        "r20_m29": r20_m29_rows,
        "coverage": {
            "admissible_q_profiles_through_r19": 12,
            "r_at_most_17_q_rows": len(through_17),
            "r18_q_rows": len(r18_rows),
            "r19_q_by_m_point_rows": len(r19_rows),
            "r20_m28_point_rows": len(r20_m28_rows),
            "r20_m29_point_rows": len(r20_m29_rows),
            "all_requested_cases_have_explicit_necessary_contradictions": True,
        },
    }


def parse_multiset(text: str) -> tuple[int, ...]:
    values = []
    for piece in text.split():
        if "^" in piece:
            value_text, count_text = piece.split("^", 1)
            values.extend([int(value_text)] * int(count_text))
        else:
            values.append(int(piece))
    return tuple(sorted(values))


def compare_wave19_artifact(
    independent_profiles: Sequence[tuple[int, tuple[int, ...]]],
    exclusions: Mapping[str, Any],
) -> dict[str, Any]:
    """Post-derivation comparison only; no discovery code is imported."""
    path = ROOT / "attempts/wave19-n3-60-structural/exact-checks.json"
    submitted = json.loads(path.read_text(encoding="utf-8"))
    submitted_profiles = sorted(
        (int(row["r"]), parse_multiset(row["q"])) for row in submitted["q_profiles"]
    )
    independent_sorted = sorted(independent_profiles)
    crossing_expectations = {
        "disjoint_2x2": [0, 4],
        "disjoint_3x2": [0, 4],
        "disjoint_4x2": [0, 4],
        "hostile_disjoint_3x3": [0, 4, 6],
        "meeting_1x1": [0],
        "meeting_1x2": [0],
        "meeting_2x1": [0],
        "meeting_2x2": [0, 4],
        "meeting_2x3": [0, 4],
        "meeting_3x1": [0],
    }
    crossing_match = all(
        submitted["crossing_edge_counts"].get(key) == value
        for key, value in crossing_expectations.items()
    )
    submitted_m29 = submitted["eliminated_ranges"]["r20_m29"]
    independent_unique = next(
        row["reason"]
        for row in exclusions["r20_m29"]
        if row["reason"]["type"] == "unique_size4_outside_moment"
    )
    independent_two = next(
        row["reason"]
        for row in exclusions["r20_m29"]
        if row["reason"]["type"] == "two_size3_outside_moments"
    )
    moment_match = (
        submitted_m29["unique_size4"]["sum"] == independent_unique["outside_sum"]
        and submitted_m29["unique_size4"]["sum_squares"]
        == independent_unique["outside_square_sum"]
        and [
            (
                row["T"],
                row["maximum_outside_degree_square_sum"],
                row["minimum_integer_square_sum"],
            )
            for row in submitted_m29["two_size3"]
        ]
        == [
            (
                row["T"],
                row["maximum_outside_square_sum"],
                row["integer_minimum_square_sum"],
            )
            for row in independent_two["cases"]
        ]
    )
    if not (
        submitted["q_profile_count"] == len(independent_profiles)
        and submitted_profiles == independent_sorted
        and crossing_match
        and moment_match
    ):
        raise CheckError("submitted Wave19 artifact disagrees with independent replay")
    return {
        "comparison_stage": "after independent derivation was frozen",
        "submitted_module_imported": False,
        "submitted_q_profile_count": submitted["q_profile_count"],
        "q_profile_set_exact_match": True,
        "crossing_rows_exact_match": crossing_match,
        "r20_m29_moment_rows_exact_match": moment_match,
        "limitation": (
            "Agreement with a submitted JSON is corroboration, not a certificate "
            "of the semantic proof."
        ),
    }


def build_certificate() -> dict[str, Any]:
    authentication = authenticate_inputs()
    raw_counts, partition_profiles = q_profiles_partition_method()
    histogram_profiles = q_profiles_histogram_method()
    if partition_profiles != histogram_profiles:
        raise CheckError("the two q-profile enumerators disagree")
    profiles = partition_profiles
    if len(profiles) != 13:
        raise CheckError(f"expected 13 admissible q profiles, got {len(profiles)}")

    point_profile_map: dict[tuple[int, int], list[tuple[int, ...]]] = {}
    for r, orders in {18: (27,), 19: (27, 28), 20: (27, 28, 29, 30)}.items():
        for m in orders:
            first = point_profiles_partition_method(r, m)
            second = point_profiles_histogram_method(r, m)
            if first != second:
                raise CheckError(f"point profile enumerators disagree at r={r},m={m}")
            point_profile_map[(r, m)] = first

    crossing_shapes = [
        (0, 0),
        (1, 1),
        (1, 4),
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (4, 2),
        (4, 3),
        (4, 4),
        (5, 1),
        (6, 2),
    ]
    crossing_rows = []
    for left, right in crossing_shapes:
        brute = crossing_counts_bitmask(left, right)
        formula = crossing_counts_formula(left, right)
        if brute != formula:
            raise CheckError(f"crossing methods disagree at {left}x{right}")
        crossing_rows.append(
            {
                "remaining_shape": [left, right],
                "bitmask_counts": list(brute),
                "structural_formula_counts": list(formula),
                "exact_match": True,
            }
        )

    exclusions = build_exclusions(profiles, point_profile_map)
    wave19_comparison = compare_wave19_artifact(profiles, exclusions)
    weakened_three = weakened_q_profiles(3)
    weakened_four = weakened_q_profiles(4)
    extra_at_three = sorted(set(weakened_three) - set(weakened_four))

    return {
        "certificate_type": "independent_wave19_global_reduction_audit",
        "claim_label": "DERIVED",
        "scope": (
            "sum(q)=40 profiles, endpoint crossing semantics, all exclusions "
            "through r=19, and r=20,m=28/29; residual m=27/30 not resolved"
        ),
        "premise_authentication": authentication,
        "premise_derivations": {
            "q_system": [
                "sum_T q(T)=40",
                "active q(T)>=2",
                "d_K(T)=r-1-3q(T)>=4",
            ],
            "d_K_degree_three_obstruction": d_k_degree_three_obstruction(),
            "indexed_incidence": [
                "each active label occurs in exactly three indexed points",
                "every nonempty point has size at least two",
                "sum_u |S_u|=3r and m<=floor(3r/2)",
            ],
            "spectral": spectral_replay(),
            "outside_moments": {
                "derivation": [
                    "sum_out a_z=14m-sum_in d_x",
                    "sum_out C(a_z,2)=2C(m,2)-e(X)-sum_in C(d_x,2)",
                    "therefore sum_out a_z^2=2m^2+12m-sum_in(d_x^2+d_x)",
                    "with d_x=6+s_x: first=8m-T, second=2m^2-30m-13T-U",
                ],
                "toy_direct_count": c5_outside_moment_toy(),
            },
        },
        "q_profiles": {
            "domain": {
                "raw_r_range": [1, 20],
                "raw_entry_lower_bound": 2,
                "weighted_total": 40,
                "filter": "r-1-3q>=4 for every active entry",
            },
            "raw_partition_count_by_r": {
                str(r): count for r, count in raw_counts.items()
            },
            "method_A": "fixed-length nondecreasing partitions then equation filter",
            "method_B": "q-value histogram recursion on label count and weighted sum",
            "method_sets_equal": True,
            "admissible_count": len(profiles),
            "rows": [profile_row(r, profile) for r, profile in profiles],
            "one_unit_histogram_mutations": profile_mutations(profiles),
            "canonicalization": profile_canonicalization_tests(profiles),
            "hostile_d_K_weakening": {
                "d_K_at_least_4_count": len(weakened_four),
                "d_K_at_least_3_count": len(weakened_three),
                "extra_profiles": [
                    {"r": r, "q": format_multiset(profile)}
                    for r, profile in extra_at_three
                ],
                "result": "SPACE_CHANGED; weakening rejected by degree-three obstruction",
            },
        },
        "point_profiles": {
            f"r{r}_m{m}": {
                "method_A": "partition the excess 3r-2m over point sizes above two",
                "method_B": "histogram recursion over positive excess sizes",
                "method_sets_equal": True,
                "count": len(rows),
                "rows": [point_profile_row(row) for row in rows],
            }
            for (r, m), rows in sorted(point_profile_map.items())
        },
        "endpoint_crossings": {
            "formula": (
                "A nonempty crossing support has k active rows and k active "
                "columns, each degree two; k=1 is impossible, while every "
                "2<=k<=min(a,b) is realized by an alternating 2k-cycle."
            ),
            "two_enumerations_equal": True,
            "shape_rows": crossing_rows,
            "size_two_fixed_sum_table": size_two_endpoint_table(),
            "universal_minimum_degree": (
                "A size-two point has four meeting neighbors plus the table's "
                "distinct positive disjoint neighbors; a point of size at "
                "least three has at least six distinct meeting neighbors. "
                "Therefore delta(G[X])>=6."
            ),
            "semantic_harness": endpoint_semantic_harness(),
        },
        "graph_encoding_hostile_tests": graph_hostile_harness(),
        "outside_histogram_hostile_tests": outside_histogram_hostile_harness(),
        "exclusions": exclusions,
        "post_derivation_wave19_comparison": wave19_comparison,
        "restrictions_and_limitations": [
            "Profiles are unlabeled multisets; sorting is a proved quotient under label relabeling, not an automorphism assumption.",
            "Point-size lists are incidence histograms only; no realizability or connectivity is inferred.",
            "The size-two incidence graph F is required to be simple, cubic, and triangle-free, but is not required to be connected.",
            "Crossing enumeration uses the authenticated labeled L-crossing relation and the two-sided zero-or-two rule after deleting a common label at both endpoints.",
            "Outside moment contradictions use only necessary integer moments; moment-colliding histograms are explicitly retained.",
            "No absence-of-construction, solver result, or search exit code is used.",
            "The r=20,m=27 and r=20,m=30 residual regimes are outside this subtask and remain UNKNOWN.",
            "No file or result from the prohibited later waves was read, executed, cited, or imported.",
        ],
        "status_boundary": {
            "r_at_most_19": "EXCLUDED_DERIVED",
            "r20_m28": "EXCLUDED_DERIVED",
            "r20_m29": "EXCLUDED_DERIVED",
            "r20_m27": "UNKNOWN_NOT_AUDITED_IN_THIS_SUBTASK",
            "r20_m30": "UNKNOWN_NOT_AUDITED_IN_THIS_SUBTASK",
            "conditional_n3_60": "UNKNOWN_FINITE_RESIDUAL",
            "self_promotion_to_VERIFIED": False,
        },
    }


def canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = build_certificate()
    encoded = canonical_json(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    if args.verify:
        existing = args.verify.read_text(encoding="utf-8")
        if existing != encoded:
            raise CheckError(f"certificate replay differs: {args.verify}")
    if not args.output and not args.verify:
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "claim_label": payload["claim_label"],
                    "q_profiles": payload["q_profiles"]["admissible_count"],
                    "coverage": payload["exclusions"]["coverage"],
                    "status_boundary": payload["status_boundary"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
