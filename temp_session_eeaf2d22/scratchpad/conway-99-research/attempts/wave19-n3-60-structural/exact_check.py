#!/usr/bin/env python3
"""Exact finite accompaniment for Wave 19 at conditional n3=60.

The program checks arithmetic, small graph classifications, crossing
matrices, point-size partitions, and outside-neighbor moments.  It does not
certify the human semantic bridges imported from the frozen audits.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Iterator, Sequence


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
            + json.dumps(
                {"expected": EXPECTED_INPUTS, "observed": observed},
                indent=2,
                sort_keys=True,
            )
        )
    return observed


def partitions(total: int, length: int, minimum: int = 2) -> Iterator[tuple[int, ...]]:
    if length == 0:
        if total == 0:
            yield ()
        return
    for first in range(minimum, total // length + 1):
        for tail in partitions(total - first, length - 1, first):
            yield (first,) + tail


def d_k(profile: Sequence[int]) -> tuple[int, ...]:
    r = len(profile)
    return tuple(r - 1 - 3 * q for q in profile)


def admissible_profiles(total: int = 40) -> tuple[tuple[int, ...], ...]:
    profiles = []
    for r in range(1, total // 2 + 1):
        for profile in partitions(total, r):
            if min(d_k(profile), default=-1) >= 4:
                profiles.append(profile)
    return tuple(profiles)


def multiplicities(values: Sequence[int]) -> str:
    groups = []
    for value, run in itertools.groupby(values):
        count = sum(1 for _ in run)
        groups.append(str(value) if count == 1 else f"{value}^{count}")
    return " ".join(groups)


def compact_q_profile(profile: Sequence[int]) -> dict[str, object]:
    return {
        "r": len(profile),
        "q": multiplicities(profile),
        "d_K": multiplicities(sorted(d_k(profile))),
        "point_count_cap": 3 * len(profile) // 2,
    }


def crossing_edge_counts(rows: int, columns: int) -> tuple[int, ...]:
    counts: set[int] = set()
    for mask in range(1 << (rows * columns)):
        row_degrees = [0] * rows
        column_degrees = [0] * columns
        for index in range(rows * columns):
            if mask & (1 << index):
                row, column = divmod(index, columns)
                row_degrees[row] += 1
                column_degrees[column] += 1
        if all(degree in (0, 2) for degree in row_degrees + column_degrees):
            counts.add(mask.bit_count())
    return tuple(sorted(counts))


def size_two_support_count(left_q: int, right_q: int) -> int | None:
    fixed_sum = 2 * (left_q + right_q)
    return fixed_sum // 4 if fixed_sum % 4 == 0 else None


def integer_partitions(total: int, maximum: int | None = None) -> Iterator[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    maximum = total if maximum is None else min(maximum, total)
    for first in range(maximum, 0, -1):
        for rest in integer_partitions(total - first, first):
            yield (first,) + rest


def point_size_profiles(incidences: int, points: int) -> tuple[tuple[int, ...], ...]:
    excess = incidences - 2 * points
    if excess < 0:
        return ()
    profiles = []
    for increments in integer_partitions(excess):
        if len(increments) <= points:
            profiles.append(
                tuple(sorted(
                    tuple(2 + increment for increment in increments)
                    + (2,) * (points - len(increments))
                ))
            )
    return tuple(profiles)


def spectral_upper_degree_sum(m: int) -> Fraction:
    return Fraction(3 * m, 1) + Fraction(m * m, 9)


def maximum_even_integer_at_most(value: Fraction) -> int:
    floor = value.numerator // value.denominator
    return floor if floor % 2 == 0 else floor - 1


def outside_moments(m: int, excess_degrees: Sequence[int]) -> dict[str, int]:
    """Exact moments for a_z=|N(z) intersect X|, z outside X."""
    total_excess = sum(excess_degrees)
    square_excess = sum(value * value for value in excess_degrees)
    return {
        "vertices": 99 - m,
        "sum": 8 * m - total_excess,
        "sum_squares": (
            2 * m * m - 30 * m - 13 * total_excess - square_excess
        ),
        "T": total_excess,
        "U": square_excess,
    }


def minimum_integer_square_sum(count: int, total: int) -> int:
    quotient, remainder = divmod(total, count)
    return (
        (count - remainder) * quotient * quotient
        + remainder * (quotient + 1) * (quotient + 1)
    )


def outside_degree_multisets(
    count: int, total: int, square_total: int, maximum_degree: int = 14
) -> tuple[tuple[tuple[int, int], ...], ...]:
    """Enumerate degree-count multisets using deviations from floor(total/n).

    For the residual calls the base is three.  The identity
    b^2-b=b(b-1) gives a small nonnegative exceptional budget.
    """
    base = total // count
    deviation_sum = total - base * count
    exceptional_budget = (
        square_total
        - base * base * count
        - (2 * base + 1) * deviation_sum
    )
    if exceptional_budget < 0:
        return ()
    exceptional_values = [
        b
        for b in range(-base, maximum_degree - base + 1)
        if b not in (0, 1) and b * (b - 1) <= exceptional_budget
    ]
    profiles: list[tuple[tuple[int, int], ...]] = []

    def recurse(
        index: int,
        budget: int,
        exceptional_sum: int,
        exceptional_count: int,
        counts: list[int],
    ) -> None:
        if index == len(exceptional_values):
            if budget != 0:
                return
            ones = deviation_sum - exceptional_sum
            zeros = count - exceptional_count - ones
            if ones < 0 or zeros < 0:
                return
            degree_counts: dict[int, int] = {}
            if zeros:
                degree_counts[base] = zeros
            if ones:
                degree_counts[base + 1] = ones
            for deviation, number in zip(exceptional_values, counts):
                if number:
                    degree = base + deviation
                    degree_counts[degree] = degree_counts.get(degree, 0) + number
            profile = tuple(sorted(degree_counts.items()))
            if sum(number for _, number in profile) != count:
                raise AssertionError("outside profile count mismatch")
            if sum(degree * number for degree, number in profile) != total:
                raise AssertionError("outside profile sum mismatch")
            if (
                sum(degree * degree * number for degree, number in profile)
                != square_total
            ):
                raise AssertionError("outside profile square mismatch")
            profiles.append(profile)
            return

        deviation = exceptional_values[index]
        cost = deviation * (deviation - 1)
        maximum_count = min(count - exceptional_count, budget // cost)
        for number in range(maximum_count + 1):
            recurse(
                index + 1,
                budget - number * cost,
                exceptional_sum + number * deviation,
                exceptional_count + number,
                counts + [number],
            )

    recurse(0, exceptional_budget, 0, 0, [])
    return tuple(sorted(set(profiles)))


def adjacency_matrix(vertex_count: int, edges: Iterable[tuple[int, int]]) -> list[list[int]]:
    matrix = [[0] * vertex_count for _ in range(vertex_count)]
    for left, right in edges:
        if left == right or matrix[left][right]:
            raise ValueError("edges must describe a simple graph")
        matrix[left][right] = matrix[right][left] = 1
    return matrix


def edge_set_from_matrix(matrix: Sequence[Sequence[int]]) -> frozenset[tuple[int, int]]:
    return frozenset(
        (left, right)
        for left in range(len(matrix))
        for right in range(left + 1, len(matrix))
        if matrix[left][right]
    )


def canonical_graph_code(matrix: Sequence[Sequence[int]]) -> tuple[int, ...]:
    vertex_count = len(matrix)
    codes = []
    for permutation in itertools.permutations(range(vertex_count)):
        codes.append(tuple(
            matrix[permutation[left]][permutation[right]]
            for left in range(vertex_count)
            for right in range(left + 1, vertex_count)
        ))
    return min(codes)


def cubic_six_vertex_forms() -> dict[str, list[list[int]]]:
    all_edges = tuple(itertools.combinations(range(6), 2))
    canonical_forms: set[tuple[int, ...]] = set()
    for edges in itertools.combinations(all_edges, 9):
        degrees = [0] * 6
        for left, right in edges:
            degrees[left] += 1
            degrees[right] += 1
        if degrees == [3] * 6:
            canonical_forms.add(canonical_graph_code(adjacency_matrix(6, edges)))

    k33_edges = tuple((left, right) for left in range(3) for right in range(3, 6))
    prism_edges = (
        (0, 1), (1, 2), (2, 0),
        (3, 4), (4, 5), (5, 3),
        (0, 3), (1, 4), (2, 5),
    )
    representatives = {
        "K3,3": adjacency_matrix(6, k33_edges),
        "triangular_prism": adjacency_matrix(6, prism_edges),
    }
    if canonical_forms != {
        canonical_graph_code(matrix) for matrix in representatives.values()
    }:
        raise AssertionError("six-vertex cubic classification mismatch")
    return representatives


def graph_triangles(matrix: Sequence[Sequence[int]]) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        triple
        for triple in itertools.combinations(range(len(matrix)), 3)
        if all(
            matrix[left][right]
            for left, right in itertools.combinations(triple, 2)
        )
    )


def dense_four_vertex_graphs_force_overlapping_triangles() -> bool:
    edges = tuple(itertools.combinations(range(4), 2))
    for edge_count in (5, 6):
        for chosen in itertools.combinations(edges, edge_count):
            matrix = adjacency_matrix(4, chosen)
            triangles = graph_triangles(matrix)
            if not any(
                len(set(first) & set(second)) == 2
                for first, second in itertools.combinations(triangles, 2)
            ):
                return False
    return True


def cycle_partitions(total: int, minimum: int = 3) -> tuple[tuple[int, ...], ...]:
    """Cycle-length multisets for a simple 2-regular graph."""
    if total == 0:
        return ((),)
    out = []
    for first in range(minimum, total + 1):
        for rest in cycle_partitions(total - first, first):
            out.append((first,) + rest)
    return tuple(out)


def z_topologies() -> tuple[dict[str, object], ...]:
    raw = (
        ("empty", 30, ()),
        ("K2", 30, ((0, 1),)),
        ("2K2", 30, ((0, 1), (2, 3))),
        ("P3", 30, ((0, 1), (1, 2))),
        ("3K2", 30, ((0, 1), (2, 3), (4, 5))),
        ("P3_plus_K2", 30, ((0, 1), (1, 2), (3, 4))),
        ("P4", 30, ((0, 1), (1, 2), (2, 3))),
        ("K1,3", 30, ((0, 1), (0, 2), (0, 3))),
        ("K3", 30, ((0, 1), (1, 2), (2, 0))),
    )
    out = []
    for name, vertex_count, edges in raw:
        degrees = [0] * vertex_count
        for left, right in edges:
            degrees[left] += 1
            degrees[right] += 1
        moments = outside_moments(30, degrees)
        outside_profiles = outside_degree_multisets(
            moments["vertices"], moments["sum"], moments["sum_squares"]
        )
        out.append({
            "name": name,
            "edges": [list(edge) for edge in edges],
            "degree_excess_multiset": multiplicities(sorted(
                degree for degree in degrees if degree
            )) if edges else "empty",
            "T": moments["T"],
            "U": moments["U"],
            "outside_vertex_count": moments["vertices"],
            "outside_degree_sum": moments["sum"],
            "outside_degree_square_sum": moments["sum_squares"],
            "outside_degree_multiset_count": len(outside_profiles),
            "outside_degree_multisets": [
                [[degree, count] for degree, count in profile]
                for profile in outside_profiles
            ] if len(outside_profiles) <= 10 else None,
        })
    return tuple(out)


def build_results() -> dict[str, object]:
    frozen = check_frozen_inputs()
    profiles = admissible_profiles()
    assert len(profiles) == 13
    assert [len(profile) for profile in profiles] == [
        14, 15, 16, 17, 17, 17, 17, 18, 18, 18, 19, 19, 20
    ]
    assert all(sum(profile) == 40 for profile in profiles)
    assert all(min(d_k(profile)) >= 4 for profile in profiles)
    assert max(max(profile) for profile in profiles) == 4

    crossings = {
        "meeting_1x1": crossing_edge_counts(1, 1),
        "meeting_1x2": crossing_edge_counts(1, 2),
        "meeting_2x1": crossing_edge_counts(2, 1),
        "meeting_2x2": crossing_edge_counts(2, 2),
        "meeting_2x3": crossing_edge_counts(2, 3),
        "meeting_3x1": crossing_edge_counts(3, 1),
        "disjoint_2x2": crossing_edge_counts(2, 2),
        "disjoint_3x2": crossing_edge_counts(3, 2),
        "disjoint_4x2": crossing_edge_counts(4, 2),
        "hostile_disjoint_3x3": crossing_edge_counts(3, 3),
    }
    assert crossings == {
        "meeting_1x1": (0,),
        "meeting_1x2": (0,),
        "meeting_2x1": (0,),
        "meeting_2x2": (0, 4),
        "meeting_2x3": (0, 4),
        "meeting_3x1": (0,),
        "disjoint_2x2": (0, 4),
        "disjoint_3x2": (0, 4),
        "disjoint_4x2": (0, 4),
        "hostile_disjoint_3x3": (0, 4, 6),
    }

    pair_support = {
        f"{left},{right}": size_two_support_count(left, right)
        for left in range(2, 5)
        for right in range(left, 5)
    }
    assert pair_support == {
        "2,2": 2, "2,3": None, "2,4": 3,
        "3,3": 3, "3,4": None, "4,4": 4,
    }

    by_r: dict[int, list[tuple[int, ...]]] = {}
    for profile in profiles:
        by_r.setdefault(len(profile), []).append(profile)
    assert max(3 * r // 2 for r in by_r if r <= 17) == 25
    assert spectral_upper_degree_sum(27) == 162

    # r=18: incidence 54 forces 27 size-two points and a simple cubic point
    # graph.  Odd/even q mixing is impossible.  The four-odd-label component
    # would be K4, forbidden by the audited no-Berge-triangle premise.
    assert point_size_profiles(54, 27) == ((2,) * 27,)
    assert {profile for profile in by_r[18]} == {
        (2,) * 16 + (4, 4),
        (2,) * 15 + (3, 3, 4),
        (2,) * 14 + (3, 3, 3, 3),
    }
    assert size_two_support_count(2, 3) is None
    assert 2 - 1 < 3
    assert 4 - 1 == 3
    assert 4 + size_two_support_count(2, 4) == 7

    # r=19: incidence 57 permits only m=27,28.  The arithmetic profiles are
    # the same regardless of the two surviving q multisets.
    assert len(by_r[19]) == 2
    assert point_size_profiles(57, 27) == (
        (2,) * 26 + (5,),
        (2,) * 25 + (3, 4),
        (2,) * 24 + (3, 3, 3),
    )
    assert point_size_profiles(57, 28) == ((2,) * 27 + (3,),)
    assert 2 * 4 > 6 and 2 * 5 > 6
    assert 2 * 4 < 2 * (2 + 2 + 2)
    assert maximum_even_integer_at_most(spectral_upper_degree_sum(28)) == 170
    assert 172 > 170

    # r=20 point profiles.
    assert by_r[20] == [(2,) * 20]
    r20_profiles = {
        m: point_size_profiles(60, m) for m in range(27, 31)
    }
    assert len(r20_profiles[27]) == 11
    assert tuple(profile for profile in r20_profiles[27] if max(profile) <= 3) == (
        (2,) * 21 + (3,) * 6,
    )
    assert len(r20_profiles[28]) == 5
    assert r20_profiles[29] == (
        (2,) * 28 + (4,),
        (2,) * 27 + (3, 3),
    )
    assert r20_profiles[30] == ((2,) * 30,)

    # m=27 residual equality.
    m27_moments = outside_moments(27, [0] * 27)
    assert m27_moments == {
        "vertices": 72, "sum": 216, "sum_squares": 648, "T": 0, "U": 0
    }
    assert minimum_integer_square_sum(72, 216) == 648
    cubic_forms = cubic_six_vertex_forms()
    assert {name: len(graph_triangles(matrix)) for name, matrix in cubic_forms.items()} == {
        "K3,3": 0,
        "triangular_prism": 2,
    }
    r_cycle_partitions_21 = cycle_partitions(21)
    assert len(r_cycle_partitions_21) == 60

    # m=28: degree-sum excess is at most two.  Four size-three points would
    # force a positive-meeting graph with at least five of six possible
    # edges; every such graph has two triangles sharing an edge.
    assert maximum_even_integer_at_most(spectral_upper_degree_sum(28)) - 6 * 28 == 2
    assert dense_four_vertex_graphs_force_overlapping_triangles()

    # m=29: the unique-size-four case forces excess vector (6,0,...), while
    # the two-size-three case has T=4 or 6 and U at least 8 or 10.
    m29_size4 = outside_moments(29, [6] + [0] * 28)
    assert m29_size4["sum_squares"] == 698
    assert minimum_integer_square_sum(70, m29_size4["sum"]) == 742
    assert m29_size4["sum_squares"] < 742
    m29_two_size3_cases = []
    for total_excess, minimum_u in ((4, 8), (6, 10)):
        sum_outside = 8 * 29 - total_excess
        square_upper = 2 * 29 * 29 - 30 * 29 - 13 * total_excess - minimum_u
        minimum_square = minimum_integer_square_sum(70, sum_outside)
        assert square_upper < minimum_square
        m29_two_size3_cases.append({
            "T": total_excess,
            "minimum_U": minimum_u,
            "outside_degree_sum": sum_outside,
            "maximum_outside_degree_square_sum": square_upper,
            "minimum_integer_square_sum": minimum_square,
        })

    # m=30: all points have size two.  Extra induced edges have zero crossing;
    # if Z is their graph then T=2e(Z), U=sum d_Z^2.  Spectral gives T<=10,
    # and outside integer moments reject T=8,10 even at the minimum U=T.
    assert maximum_even_integer_at_most(spectral_upper_degree_sum(30)) == 190
    rejected_m30 = []
    for total_excess in (8, 10):
        sum_outside = 240 - total_excess
        square_upper = 900 - 14 * total_excess
        minimum_square = minimum_integer_square_sum(69, sum_outside)
        assert square_upper < minimum_square
        rejected_m30.append({
            "T": total_excess,
            "minimum_U": total_excess,
            "outside_degree_sum": sum_outside,
            "maximum_outside_degree_square_sum": square_upper,
            "minimum_integer_square_sum": minimum_square,
        })
    z_cases = z_topologies()
    r_cycle_partitions_30 = cycle_partitions(30)
    assert len(r_cycle_partitions_30) == 331
    expected_counts = {
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
    assert {
        case["name"]: case["outside_degree_multiset_count"] for case in z_cases
    } == expected_counts

    return {
        "status_boundary": {
            "conditional_n3_60": "UNKNOWN_FINITE_RESIDUAL",
            "conway_99_target": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "frozen_inputs_sha256": frozen,
        "q_profile_count": len(profiles),
        "q_profiles": [compact_q_profile(profile) for profile in profiles],
        "crossing_edge_counts": {
            name: list(counts) for name, counts in crossings.items()
        },
        "size_two_q_pair_support_count": pair_support,
        "eliminated_ranges": {
            "r_at_most_17": "point cap at most 25 contradicts dense minimum 27",
            "r18": "all three equality profiles contradicted",
            "r19": "both profiles contradicted at m=27 and m=28",
            "r20_m28": "all five point-size profiles contradicted",
            "r20_m29": {
                "unique_size4": {
                    **m29_size4,
                    "minimum_integer_square_sum": 742,
                },
                "two_size3": m29_two_size3_cases,
            },
        },
        "r20_m27_residual": {
            "point_sizes": "2^21 3^6",
            "induced_degree": 6,
            "induced_edge_count": 81,
            "meeting_edge_count": 60,
            "outside_degree_multiset": "3^72",
            "positive_meeting_graph_on_six_size3_points": {
                name: {
                    "adjacency_matrix": matrix,
                    "triangles": [list(triangle) for triangle in graph_triangles(matrix)],
                }
                for name, matrix in cubic_forms.items()
            },
            "positive_disjoint_graph_on_21_size2_points": {
                "description": "simple spanning 2-factor",
                "edge_count": 21,
                "cycle_length_multiset_count": len(r_cycle_partitions_21),
                "cycle_length_multisets": [
                    list(profile) for profile in r_cycle_partitions_21
                ],
            },
            "claim": "FINITE_RESIDUAL_NOT_EXCLUDED",
        },
        "r20_m30_residual": {
            "point_sizes": "2^30",
            "point_graph_F": "simple cubic triangle-free on 20 labels",
            "meeting_graph": "line graph L(F), 4-regular on 30 points",
            "positive_crossing_graph_R": "spanning simple 2-factor, disjoint from L(F)",
            "positive_crossing_graph_R_edge_count": 30,
            "positive_crossing_graph_R_cycle_length_multiset_count":
                len(r_cycle_partitions_30),
            "extra_zero_crossing_graph_Z": "simple graph with at most 3 edges",
            "rejected_moment_cases": rejected_m30,
            "surviving_Z_topologies": list(z_cases),
            "claim": "FINITE_RESIDUAL_NOT_EXCLUDED",
        },
        "limitations": [
            "arithmetic and small-graph certificate, not a semantic proof certificate",
            "no global H-degree restriction",
            "no point-size upper bound",
            "no Wave 14 residual identity or automorphism",
            "no Wave 17 catalog and no Wave 18 result",
            "residual feasibility is not established",
        ],
    }


def residual_certificate(results: dict[str, object]) -> dict[str, object]:
    return {
        "certificate_type": "wave19_finite_residual_reduction",
        "frozen_inputs_sha256": results["frozen_inputs_sha256"],
        "status_boundary": results["status_boundary"],
        "r20_m27_residual": results["r20_m27_residual"],
        "r20_m30_residual": results["r20_m30_residual"],
        "limitations": results["limitations"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--residual-output", type=Path)
    parser.add_argument("--verify-residual", type=Path)
    args = parser.parse_args()
    results = build_results()
    rendered = json.dumps(results, indent=2, sort_keys=True) + "\n"
    residual_rendered = (
        json.dumps(residual_certificate(results), indent=2, sort_keys=True) + "\n"
    )
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    if args.verify is not None:
        observed = args.verify.read_text(encoding="utf-8")
        if observed != rendered:
            raise AssertionError(f"result mismatch: {args.verify}")
    if args.residual_output is not None:
        args.residual_output.write_text(
            residual_rendered, encoding="utf-8", newline="\n"
        )
    if args.verify_residual is not None:
        observed = args.verify_residual.read_text(encoding="utf-8")
        if observed != residual_rendered:
            raise AssertionError(f"residual result mismatch: {args.verify_residual}")
    if args.output is None and args.residual_output is None:
        print(rendered, end="")


if __name__ == "__main__":
    main()
