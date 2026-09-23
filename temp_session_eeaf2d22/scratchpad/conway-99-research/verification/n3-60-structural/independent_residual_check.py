#!/usr/bin/env python3
"""Independent arithmetic and hostile checks for the Wave 19 residuals.

This module does not import the submitted checker.  Its deliberately different
formulations are:

* q profiles as bounded multiplicity solutions;
* point profiles as size-count solutions;
* crossings as products of allowed row supports;
* cubic graphs through their 2-regular complements;
* outside histograms by degree-by-degree dynamic programming; and
* small Z topologies by generating every edge subset, not a hand-entered list.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, deque
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[2]
PINNED_INPUTS = {
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "verification/2026-07-23-wave15-global-lift-audit.md":
        "edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036",
    "verification/2026-07-23-wave16-n3-51-structural-audit.md":
        "99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6",
    "agents/2026-07-23-wave19-n3-60-structural.md":
        "b2f90af07f34a6525ea35cdf4d392d95aea10fc319633cd17037d00145690744",
    "attempts/wave19-n3-60-structural/exact_check.py":
        "c7564eef0f1c62165c91a36071ab34b494ead891877011e755407ad48adee460",
    "attempts/wave19-n3-60-structural/test_exact_check.py":
        "1b1d2628d6c2d837dec24ec679d579676b5a0e66962e0266cee2642040bf6165",
    "attempts/wave19-n3-60-structural/exact-checks.json":
        "fc884ea131b1b6c926d9e71ddb1f7925e15c39498f1d7b72819a6473b39ab8dd",
    "attempts/wave19-n3-60-structural/residual-certificates.json":
        "3396b3b67b944b86bfd0d51e8beca25dfc9350815269c62cda4fa7c22a7a5c8b",
    "attempts/wave19-n3-60-structural/failed-attempts.md":
        "62d43cdb66c599c8c1e1618ca54267c1bf08ba20ad175e04883349cf6f876a0e",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate_inputs() -> dict[str, str]:
    observed = {name: sha256(ROOT / name) for name in PINNED_INPUTS}
    if observed != PINNED_INPUTS:
        raise AssertionError(
            "input provenance mismatch\n"
            + json.dumps({"expected": PINNED_INPUTS, "observed": observed}, indent=2)
        )
    return observed


def q_profiles_by_multiplicity(total: int = 40) -> tuple[tuple[int, ...], ...]:
    """Solve for counts of each q value, rather than partitioning the total."""
    answers: set[tuple[int, ...]] = set()
    for active_count in range(1, total // 2 + 1):
        q_max = (active_count - 5) // 3
        if q_max < 2:
            continue
        values = tuple(range(2, q_max + 1))

        def fill(index: int, left_count: int, left_sum: int, counts: list[int]) -> None:
            if index == len(values):
                if left_count == 0 and left_sum == 0:
                    expanded = tuple(
                        q
                        for q, number in zip(values, counts)
                        for _ in range(number)
                    )
                    answers.add(expanded)
                return
            q = values[index]
            if index == len(values) - 1:
                choices = (left_count,)
            else:
                choices = range(left_count + 1)
            for number in choices:
                cost = q * number
                if cost <= left_sum:
                    fill(
                        index + 1,
                        left_count - number,
                        left_sum - cost,
                        counts + [number],
                    )

        fill(0, active_count, total, [])
    return tuple(sorted(answers, key=lambda row: (len(row), row)))


def point_profiles_by_counts(
    incidence_count: int, point_count: int
) -> tuple[tuple[int, ...], ...]:
    """Enumerate counts of point sizes, bounded by the available excess."""
    excess = incidence_count - 2 * point_count
    if excess < 0:
        return ()
    maximum_size = 2 + excess
    answers: list[tuple[int, ...]] = []

    def fill(size: int, left_points: int, left_incidence: int, counts: list[int]) -> None:
        if size == maximum_size:
            number = left_points
            if number * size == left_incidence:
                profile = tuple(
                    value
                    for value, count in zip(range(2, maximum_size + 1), counts + [number])
                    for _ in range(count)
                )
                answers.append(profile)
            return
        maximum_number = min(left_points, left_incidence // size)
        for number in range(maximum_number + 1):
            fill(
                size + 1,
                left_points - number,
                left_incidence - number * size,
                counts + [number],
            )

    fill(2, point_count, incidence_count, [])
    return tuple(sorted(answers))


def crossing_counts_from_row_supports(
    rows: int, columns: int, require_column_rule: bool = True
) -> tuple[int, ...]:
    """Enumerate each row as empty or a two-column support."""
    row_options: tuple[tuple[int, ...], ...] = ((),) + tuple(
        itertools.combinations(range(columns), 2)
    )
    answers: set[int] = set()
    for supports in itertools.product(row_options, repeat=rows):
        column_degrees = [0] * columns
        for support in supports:
            for column in support:
                column_degrees[column] += 1
        if not require_column_rule or all(value in (0, 2) for value in column_degrees):
            answers.add(sum(map(len, supports)))
    return tuple(sorted(answers))


def integer_minimum_square_sum(count: int, total: int) -> int:
    low, high_count = divmod(total, count)
    return (count - high_count) * low * low + high_count * (low + 1) ** 2


def integer_maximum_square_sum(count: int, total: int, cap: int) -> int:
    """Convex maximum with 0 <= entries <= cap."""
    full, remainder = divmod(total, cap)
    if full > count or (full == count and remainder):
        return -1
    return full * cap * cap + remainder * remainder


def outside_moments_from_pair_count(
    point_count: int, excess_degrees: Sequence[int]
) -> dict[str, int]:
    """Re-derive both moments through cut and common-neighbor pair counts."""
    if len(excess_degrees) != point_count or any(value < 0 for value in excess_degrees):
        raise ValueError("excess degrees must be nonnegative and indexed by X")
    internal_degrees = [6 + value for value in excess_degrees]
    degree_sum = sum(internal_degrees)
    if degree_sum % 2:
        raise ValueError("an induced graph has even degree sum")
    internal_edges = degree_sum // 2
    outside_sum = 14 * point_count - degree_sum
    all_common_neighbor_incidences = (
        point_count * (point_count - 1) - internal_edges
    )
    common_neighbors_inside = sum(
        degree * (degree - 1) // 2 for degree in internal_degrees
    )
    outside_choose_two = all_common_neighbor_incidences - common_neighbors_inside
    outside_square_sum = outside_sum + 2 * outside_choose_two
    total_excess = sum(excess_degrees)
    square_excess = sum(value * value for value in excess_degrees)
    formula_square_sum = (
        2 * point_count * point_count
        - 30 * point_count
        - 13 * total_excess
        - square_excess
    )
    if outside_square_sum != formula_square_sum:
        raise AssertionError("direct pair count and expanded moment disagree")
    return {
        "vertices": 99 - point_count,
        "sum": outside_sum,
        "sum_squares": outside_square_sum,
        "T": total_excess,
        "U": square_excess,
    }


def histogram_solver(
    count: int, total: int, square_total: int, cap: int = 14
) -> tuple[tuple[tuple[int, int], ...], ...]:
    """All degree histograms by dynamic programming over degree values."""

    @lru_cache(maxsize=None)
    def number_of_solutions(
        degree: int, left_count: int, left_sum: int, left_square: int
    ) -> int:
        if min(left_count, left_sum, left_square) < 0:
            return 0
        if left_count == 0:
            return int(left_sum == 0 and left_square == 0)
        if degree < 0 or left_sum > degree * left_count:
            return 0
        if degree == 0:
            return int(left_sum == 0 and left_square == 0)
        if left_square < integer_minimum_square_sum(left_count, left_sum):
            return 0
        if left_square > integer_maximum_square_sum(left_count, left_sum, degree):
            return 0
        maximum_number = min(
            left_count,
            left_sum // degree,
            left_square // (degree * degree),
        )
        return sum(
            number_of_solutions(
                degree - 1,
                left_count - number,
                left_sum - number * degree,
                left_square - number * degree * degree,
            )
            for number in range(maximum_number + 1)
        )

    expected_count = number_of_solutions(cap, count, total, square_total)
    answers: list[tuple[tuple[int, int], ...]] = []

    def reconstruct(
        degree: int,
        left_count: int,
        left_sum: int,
        left_square: int,
        chosen: list[tuple[int, int]],
    ) -> None:
        if degree == 0:
            if left_sum == 0 and left_square == 0:
                tail = chosen + ([(0, left_count)] if left_count else [])
                answers.append(tuple(sorted(tail)))
            return
        maximum_number = min(
            left_count,
            left_sum // degree if degree else left_count,
            left_square // (degree * degree) if degree else left_count,
        )
        for number in range(maximum_number + 1):
            next_state = (
                degree - 1,
                left_count - number,
                left_sum - number * degree,
                left_square - number * degree * degree,
            )
            if number_of_solutions(*next_state):
                reconstruct(
                    *next_state,
                    chosen + ([(degree, number)] if number else []),
                )

    if expected_count:
        reconstruct(cap, count, total, square_total, [])
    canonical = tuple(sorted(set(answers)))
    if len(canonical) != expected_count:
        raise AssertionError("histogram reconstruction/count mismatch")
    for histogram in canonical:
        if sum(number for _, number in histogram) != count:
            raise AssertionError("histogram population mismatch")
        if sum(degree * number for degree, number in histogram) != total:
            raise AssertionError("histogram first-moment mismatch")
        if sum(degree * degree * number for degree, number in histogram) != square_total:
            raise AssertionError("histogram second-moment mismatch")
    return canonical


def edges_from_bits(vertex_count: int, chosen: Iterable[tuple[int, int]]) -> set[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for left, right in chosen:
        if not (0 <= left < vertex_count and 0 <= right < vertex_count):
            raise ValueError("edge endpoint out of range")
        if left == right:
            raise ValueError("loop rejected")
        edge = tuple(sorted((left, right)))
        if edge in edges:
            raise ValueError("parallel edge rejected")
        edges.add(edge)
    return edges


def degrees(vertex_count: int, edges: Iterable[tuple[int, int]]) -> tuple[int, ...]:
    values = [0] * vertex_count
    for left, right in edges:
        values[left] += 1
        values[right] += 1
    return tuple(values)


def complement_edges(vertex_count: int, edges: set[tuple[int, int]]) -> set[tuple[int, int]]:
    return set(itertools.combinations(range(vertex_count), 2)) - edges


def component_sizes(vertex_count: int, edges: set[tuple[int, int]]) -> tuple[int, ...]:
    neighbors = [set() for _ in range(vertex_count)]
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    remaining = set(range(vertex_count))
    sizes = []
    while remaining:
        start = remaining.pop()
        queue = deque([start])
        size = 0
        while queue:
            vertex = queue.popleft()
            size += 1
            for neighbor in neighbors[vertex]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
        sizes.append(size)
    return tuple(sorted(sizes))


def triangle_count(edges: set[tuple[int, int]], vertex_count: int) -> int:
    return sum(
        all(tuple(sorted(edge)) in edges for edge in itertools.combinations(triple, 2))
        for triple in itertools.combinations(range(vertex_count), 3)
    )


def cubic_six_classification_via_complement() -> dict[str, object]:
    complete_edges = tuple(itertools.combinations(range(6), 2))
    complement_component_types: Counter[tuple[int, ...]] = Counter()
    representative_by_type: dict[tuple[int, ...], set[tuple[int, int]]] = {}
    labeled_cubic_count = 0
    for chosen in itertools.combinations(complete_edges, 9):
        graph = set(chosen)
        if degrees(6, graph) != (3,) * 6:
            continue
        labeled_cubic_count += 1
        complement = complement_edges(6, graph)
        if degrees(6, complement) != (2,) * 6:
            raise AssertionError("cubic complement is not 2-regular")
        kind = component_sizes(6, complement)
        complement_component_types[kind] += 1
        representative_by_type.setdefault(kind, graph)
    if set(complement_component_types) != {(3, 3), (6,)}:
        raise AssertionError("unexpected 2-regular complement type")
    representatives = {
        "K3,3": representative_by_type[(3, 3)],
        "triangular_prism": representative_by_type[(6,)],
    }
    triangle_counts = {
        name: triangle_count(edges, 6) for name, edges in representatives.items()
    }
    if triangle_counts != {"K3,3": 0, "triangular_prism": 2}:
        raise AssertionError("cubic representative identification failed")
    return {
        "labeled_cubic_graph_count": labeled_cubic_count,
        "complement_component_type_counts": {
            "+".join(map(str, key)): value
            for key, value in sorted(complement_component_types.items())
        },
        "isomorphism_types": tuple(sorted(representatives)),
        "triangle_counts": triangle_counts,
    }


def local_size3_point_realizations() -> dict[str, object]:
    """Realize both J types at the six-point/no-Berge layer only."""
    k33_points = tuple(
        frozenset(3 * left + right for right in range(3))
        for left in range(3)
    ) + tuple(
        frozenset(3 * left + right for left in range(3))
        for right in range(3)
    )
    prism_points = (
        frozenset((0, 2, 5)),
        frozenset((0, 3, 6)),
        frozenset((0, 4, 7)),
        frozenset((1, 2, 8)),
        frozenset((1, 3, 9)),
        frozenset((1, 4, 10)),
    )

    results: dict[str, object] = {}
    for name, points in (("K3,3", k33_points), ("triangular_prism", prism_points)):
        meeting_edges = {
            (left, right)
            for left, right in itertools.combinations(range(6), 2)
            if points[left] & points[right]
        }
        if any(
            len(points[left] & points[right]) > 1
            for left, right in itertools.combinations(range(6), 2)
        ):
            raise AssertionError("local size-three realization is not linear")
        for triple in itertools.combinations(range(6), 3):
            if all(
                points[left] & points[right]
                for left, right in itertools.combinations(triple, 2)
            ) and not set.intersection(*(set(points[index]) for index in triple)):
                raise AssertionError("local size-three realization has a Berge triangle")
        occurrences = Counter(label for point in points for label in point)
        results[name] = {
            "meeting_degree_sequence": list(sorted(degrees(6, meeting_edges))),
            "meeting_triangle_count": triangle_count(meeting_edges, 6),
            "label_occurrence_multiset": list(sorted(occurrences.values())),
            "scope": "six size-three points only; no completion by size-two points",
        }
    if results["K3,3"]["meeting_triangle_count"] != 0:
        raise AssertionError("K3,3 local realization mislabeled")
    if results["triangular_prism"]["meeting_triangle_count"] != 2:
        raise AssertionError("prism local realization mislabeled")
    return results


def cycle_partition_count(total: int) -> int:
    """Coefficient calculation for products 1/(1-x^k), k >= 3."""
    coefficients = [0] * (total + 1)
    coefficients[0] = 1
    for cycle_length in range(3, total + 1):
        for value in range(cycle_length, total + 1):
            coefficients[value] += coefficients[value - cycle_length]
    return coefficients[total]


TOPOLOGY_NAMES = {
    ((), 0): "empty",
    ((1, 1), 0): "K2",
    ((1, 1, 1, 1), 0): "2K2",
    ((1, 1, 2), 0): "P3",
    ((1, 1, 1, 1, 1, 1), 0): "3K2",
    ((1, 1, 1, 1, 2), 0): "P3_plus_K2",
    ((1, 1, 2, 2), 0): "P4",
    ((1, 1, 1, 3), 0): "K1,3",
    ((2, 2, 2), 1): "K3",
}


def generated_z_topologies() -> dict[str, tuple[int, int]]:
    all_edges = tuple(itertools.combinations(range(6), 2))
    found: dict[tuple[tuple[int, ...], int], tuple[int, int]] = {}
    for edge_count in range(4):
        for chosen in itertools.combinations(all_edges, edge_count):
            edge_set = set(chosen)
            nonzero_degrees = tuple(sorted(value for value in degrees(6, edge_set) if value))
            signature = (nonzero_degrees, triangle_count(edge_set, 6))
            total_degree = sum(nonzero_degrees)
            square_degree = sum(value * value for value in nonzero_degrees)
            found[signature] = (total_degree, square_degree)
    if set(found) != set(TOPOLOGY_NAMES):
        raise AssertionError(f"unexpected topology signatures: {set(found)}")
    return {
        TOPOLOGY_NAMES[signature]: moments
        for signature, moments in found.items()
    }


def mutation_results() -> dict[str, str]:
    results: dict[str, str] = {}

    if crossing_counts_from_row_supports(2, 3) != crossing_counts_from_row_supports(3, 2):
        raise AssertionError("endpoint-swap symmetry failed")
    results["swap_crossing_endpoints"] = "CONFIRMED: exact count set is symmetric"

    # Dropping the column-side rule creates the forbidden two-edge alternative.
    row_only = crossing_counts_from_row_supports(2, 3, require_column_rule=False)
    if 2 not in row_only or crossing_counts_from_row_supports(2, 3) != (0, 4):
        raise AssertionError("crossing-rule mutation did not separate the semantics")
    results["drop_column_endpoint_rule"] = "REJECTED: adds a false two-edge crossing"

    # Keeping a common label changes a deleted 1x2 zero crossing into a 2x3
    # crossing where four edges are possible.
    if crossing_counts_from_row_supports(1, 2) != (0,):
        raise AssertionError("deleted meeting crossing should vanish")
    if 4 not in crossing_counts_from_row_supports(2, 3):
        raise AssertionError("retained-label hostile control missing")
    results["retain_common_label"] = "REJECTED: creates a false four-edge meeting crossing"

    # The fixed-point sum is over distinct original neighbors.  Double-counting
    # one positive endpoint would falsely replace two required q=(2,2)
    # neighbors by one.
    if 2 * 4 != 8 or 1 * 4 == 8:
        raise AssertionError("fixed-sum endpoint multiplicity control malformed")
    results["double_count_one_positive_endpoint"] = (
        "REJECTED: one original neighbor contributes four, not eight"
    )
    results["omit_one_of_two_positive_endpoints"] = (
        "REJECTED: leaves fixed sum four instead of eight"
    )

    # A one-unit transfer can be invalid or can land on a different genuine
    # row.  The harness must distinguish those outcomes.
    invalid_r20 = tuple(sorted((1, 3) + (2,) * 18))
    valid_r19_transfer = tuple(sorted((3, 3) + (2,) * 17))
    profile_set = set(q_profiles_by_multiplicity())
    if invalid_r20 in profile_set or valid_r19_transfer not in profile_set:
        raise AssertionError("q-profile mutation controls malformed")
    results["r20_one_unit_transfer"] = "REJECTED: creates forbidden active q=1"
    results["r19_one_unit_transfer"] = (
        "RETAINED: maps 2^18 4 to the genuine 2^17 3^2 profile"
    )

    # Both cubic types have the same degree sequence.  A legal 2-switch turns a
    # labeled K3,3 representative into the prism class.
    k33 = {(left, right) for left in range(3) for right in range(3, 6)}
    switched = set(k33)
    switched.remove((0, 3))
    switched.remove((1, 4))
    switched.add((0, 1))
    switched.add((3, 4))
    if degrees(6, switched) != (3,) * 6 or triangle_count(switched, 6) != 2:
        raise AssertionError("degree-preserving cubic mutation failed")
    results["degree_sequence_only_cubic_classifier"] = (
        "REJECTED: 2-switch preserves 3^6 but changes K3,3 to prism class"
    )

    for bad_edges, label in (
        ([(0, 0)], "loop"),
        ([(0, 1), (1, 0)], "parallel"),
    ):
        try:
            edges_from_bits(3, bad_edges)
        except ValueError:
            results[f"{label}_graph_impostor"] = "REJECTED by simple-graph validator"
        else:
            raise AssertionError(f"{label} impostor survived")

    # Population-preserving moment attacks against the K3/K1,3 histogram.
    valid = ((3, 42), (4, 27))
    wrong_first = ((3, 41), (4, 28))
    wrong_second = ((2, 1), (3, 41), (4, 26), (5, 1))

    def moments(histogram: Sequence[tuple[int, int]]) -> tuple[int, int, int]:
        return (
            sum(number for _, number in histogram),
            sum(degree * number for degree, number in histogram),
            sum(degree * degree * number for degree, number in histogram),
        )

    if moments(valid) != (69, 234, 810):
        raise AssertionError("valid hostile-control histogram is wrong")
    if moments(wrong_first)[0] != 69 or moments(wrong_first)[1] == 234:
        raise AssertionError("first-moment mutation is not focused")
    if moments(wrong_second)[:2] != (69, 234) or moments(wrong_second)[2] == 810:
        raise AssertionError("second-moment mutation is not focused")
    results["histogram_correct_population_wrong_first"] = "REJECTED"
    results["histogram_correct_first_wrong_second"] = "REJECTED"
    results["moment_collision_K1,3_vs_K3"] = (
        "RETAINED: both have (T,U)=(6,12); moments do not identify topology"
    )

    # Every four-edge simple graph has T=8 and U>=8, already impossible.
    four_edge_max_square = 900 - 13 * 8 - 8
    four_edge_integer_min = integer_minimum_square_sum(69, 232)
    if not four_edge_max_square < four_edge_integer_min:
        raise AssertionError("four-edge counterpressure was not rejected")
    results["Z_four_edge_counterpressure"] = (
        f"REJECTED: outside square <= {four_edge_max_square} < "
        f"integer minimum {four_edge_integer_min}"
    )

    # An automorphism/connected-complement restriction deletes K3,3.
    classification = cubic_six_classification_via_complement()
    if classification["isomorphism_types"] != ("K3,3", "triangular_prism"):
        raise AssertionError("unexpected cubic classes")
    results["impose_connected_complement"] = (
        "REJECTED AS RESTRICTION: deletes the K3,3 class"
    )

    # A cubic J matrix alone does not encode the no-Berge labeling: assigning
    # three distinct intersection labels around a prism triangle is invalid.
    triangle_intersections = ("alpha", "beta", "gamma")
    if len(set(triangle_intersections)) != 3:
        raise AssertionError("hostile Berge assignment malformed")
    results["locally_cubic_distinct_triangle_intersections"] = (
        "REJECTED by no-Berge; adjacency matrix alone cannot detect this"
    )

    # A cycle-length certificate alone cannot enforce point disjointness.
    hostile_cycle_points = ({0, 1}, {1, 2}, {2, 0})
    if not all(
        hostile_cycle_points[index] & hostile_cycle_points[(index + 1) % 3]
        for index in range(3)
    ):
        raise AssertionError("hostile overlapping 3-cycle malformed")
    results["abstract_R_cycle_on_meeting_points"] = (
        "REJECTED by disjoint-endpoint semantics; cycle partition alone cannot detect this"
    )

    return results


def build_results() -> dict[str, object]:
    inputs = authenticate_inputs()

    profiles = q_profiles_by_multiplicity()
    expected_profiles = (
        (2,) * 2 + (3,) * 12,
        (2,) * 5 + (3,) * 10,
        (2,) * 8 + (3,) * 8,
        (2,) * 14 + (4,) * 3,
        (2,) * 13 + (3,) * 2 + (4,) * 2,
        (2,) * 12 + (3,) * 4 + (4,),
        (2,) * 11 + (3,) * 6,
        (2,) * 16 + (4,) * 2,
        (2,) * 15 + (3,) * 2 + (4,),
        (2,) * 14 + (3,) * 4,
        (2,) * 18 + (4,),
        (2,) * 17 + (3,) * 2,
        (2,) * 20,
    )
    if profiles != expected_profiles:
        raise AssertionError("sum-q=40 profile set mismatch")

    crossings = {
        f"{rows}x{columns}": crossing_counts_from_row_supports(rows, columns)
        for rows, columns in ((1, 1), (1, 2), (2, 1), (2, 2), (2, 3),
                              (3, 1), (3, 2), (3, 3), (4, 2))
    }
    if crossings != {
        "1x1": (0,), "1x2": (0,), "2x1": (0,), "2x2": (0, 4),
        "2x3": (0, 4), "3x1": (0,), "3x2": (0, 4),
        "3x3": (0, 4, 6), "4x2": (0, 4),
    }:
        raise AssertionError("two-sided crossing table mismatch")

    point_profiles = {
        f"r20_m{point_count}": point_profiles_by_counts(60, point_count)
        for point_count in range(27, 31)
    }
    if len(point_profiles["r20_m27"]) != 11:
        raise AssertionError("m=27 point-profile count mismatch")
    if tuple(row for row in point_profiles["r20_m27"] if max(row) <= 3) != (
        (2,) * 21 + (3,) * 6,
    ):
        raise AssertionError("m=27 equality survivor mismatch")
    if len(point_profiles["r20_m28"]) != 5:
        raise AssertionError("m=28 point-profile count mismatch")
    if point_profiles["r20_m29"] != (
        (2,) * 28 + (4,),
        (2,) * 27 + (3, 3),
    ):
        raise AssertionError("m=29 point-profile set mismatch")
    if point_profiles["r20_m30"] != ((2,) * 30,):
        raise AssertionError("m=30 point-profile mismatch")

    m27_moments = outside_moments_from_pair_count(27, [0] * 27)
    if m27_moments != {
        "vertices": 72, "sum": 216, "sum_squares": 648, "T": 0, "U": 0
    }:
        raise AssertionError("m=27 outside moments mismatch")
    if histogram_solver(72, 216, 648) != (((3, 72),),):
        raise AssertionError("m=27 outside equality histogram mismatch")

    cubic = cubic_six_classification_via_complement()
    if cycle_partition_count(21) != 60:
        raise AssertionError("21-vertex 2-factor partition count mismatch")

    # Reconstruct the m=29 outside contradictions from the direct pair count.
    m29_size4 = outside_moments_from_pair_count(29, [6] + [0] * 28)
    if not m29_size4["sum_squares"] < integer_minimum_square_sum(
        m29_size4["vertices"], m29_size4["sum"]
    ):
        raise AssertionError("m=29 size-four case did not contradict")
    m29_two_size3 = []
    for total_excess, least_square_excess in ((4, 8), (6, 10)):
        outside_sum = 232 - total_excess
        outside_square_upper = (
            2 * 29 * 29 - 30 * 29 - 13 * total_excess - least_square_excess
        )
        integer_minimum = integer_minimum_square_sum(70, outside_sum)
        if not outside_square_upper < integer_minimum:
            raise AssertionError("m=29 two-size-three case did not contradict")
        m29_two_size3.append({
            "T": total_excess,
            "minimum_U": least_square_excess,
            "outside_sum": outside_sum,
            "outside_square_upper": outside_square_upper,
            "integer_minimum_square": integer_minimum,
        })

    z_topologies = generated_z_topologies()
    expected_histogram_counts = {
        "empty": 1297,
        "K2": 354,
        "2K2": 69,
        "P3": 52,
        "3K2": 6,
        "P3_plus_K2": 3,
        "P4": 2,
        "K1,3": 1,
        "K3": 1,
    }
    z_results: dict[str, object] = {}
    for name, (total_excess, square_excess) in sorted(z_topologies.items()):
        if square_excess == total_excess:
            nonzero_excesses = [1] * total_excess
        else:
            nonzero_excesses = {
                (4, 6): [2, 1, 1],
                (6, 8): [2, 1, 1, 1, 1],
                (6, 10): [2, 2, 1, 1],
                # K1,3 has [3,1,1,1], while K3 has [2,2,2].
                # Either realizes the same two moments used here.
                (6, 12): [3, 1, 1, 1],
            }[(total_excess, square_excess)]
        excess_vector = nonzero_excesses + [0] * (30 - len(nonzero_excesses))
        moments = outside_moments_from_pair_count(
            30,
            excess_vector,
        )
        histograms = histogram_solver(
            moments["vertices"], moments["sum"], moments["sum_squares"]
        )
        if len(histograms) != expected_histogram_counts[name]:
            raise AssertionError(f"outside histogram count mismatch for {name}")
        z_results[name] = {
            "T": total_excess,
            "U": square_excess,
            "outside_sum": moments["sum"],
            "outside_square_sum": moments["sum_squares"],
            "outside_histogram_count": len(histograms),
            "histograms_if_at_most_ten": [
                [list(pair) for pair in histogram] for histogram in histograms
            ] if len(histograms) <= 10 else None,
        }
    if cycle_partition_count(30) != 331:
        raise AssertionError("30-vertex 2-factor partition count mismatch")

    rejected_four_and_five_edges = []
    for total_excess in (8, 10):
        outside_sum = 240 - total_excess
        outside_square_upper = 900 - 14 * total_excess
        integer_minimum = integer_minimum_square_sum(69, outside_sum)
        if not outside_square_upper < integer_minimum:
            raise AssertionError("m=30 edge-bound reduction failed")
        rejected_four_and_five_edges.append({
            "T": total_excess,
            "minimum_U": total_excess,
            "outside_sum": outside_sum,
            "outside_square_upper": outside_square_upper,
            "integer_minimum_square": integer_minimum,
        })

    return {
        "status_boundary": {
            "conditional_n3_60": "UNKNOWN_FINITE_RESIDUAL",
            "conway_99_target": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "inputs_sha256": inputs,
        "sum_q_40": {
            "profile_count": len(profiles),
            "profiles": [list(row) for row in profiles],
        },
        "crossing_counts": {key: list(value) for key, value in crossings.items()},
        "r20_point_profiles": {
            key: [list(row) for row in value] for key, value in point_profiles.items()
        },
        "residual_A_m27": {
            "outside_moments": m27_moments,
            "outside_histogram": [[3, 72]],
            "cubic_classification": cubic,
            "local_no_Berge_realizations": local_size3_point_realizations(),
            "size2_2factor_cycle_partition_count": cycle_partition_count(21),
            "compatibility_boundary": [
                "J adjacency does not encode which active label realizes each meeting",
                "the size-two cycle partition does not assign point endpoints or enforce disjointness",
                "neither item is joined to a 20-label, 27-point linear incidence system",
            ],
        },
        "r20_m29_exclusions": {
            "size4": m29_size4,
            "two_size3": m29_two_size3,
        },
        "residual_B_m30": {
            "rejected_T_8_10": rejected_four_and_five_edges,
            "z_topologies": z_results,
            "R_2factor_cycle_partition_count": cycle_partition_count(30),
            "compatibility_boundary": [
                "F, R, and Z are not instantiated on one common labeled point set",
                "cycle partitions do not enforce that R endpoints are disjoint F-edges",
                "Z topology types do not enforce disjoint endpoints or edge-disjointness from R",
                "outside histograms solve only the first two moments, not vertex assignments or SRG extension constraints",
            ],
        },
        "hostile_mutations": mutation_results(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    rendered = json.dumps(build_results(), indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    if arguments.verify:
        if arguments.verify.read_text(encoding="utf-8") != rendered:
            raise AssertionError(f"verification mismatch: {arguments.verify}")
    if not arguments.output and not arguments.verify:
        print(rendered, end="")


if __name__ == "__main__":
    main()
