#!/usr/bin/env python3
"""Independent finite replay for the conditional n3=45 exclusion.

This module deliberately does not import the Wave 13 discovery programs.  It
checks only finite arithmetic and local graph consequences used by the human
proof.  It is a regression companion, not a formal proof of Conway-99.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from typing import Iterable, Iterator, Sequence


EXPECTED_PROFILES = (
    (15, (2,) * 15, (8,) * 15),
    (14, (2,) * 13 + (4,), (1,) + (7,) * 13),
    (14, (2,) * 12 + (3, 3), (4, 4) + (7,) * 12),
    (13, (2,) * 11 + (4, 4), (0, 0) + (6,) * 11),
    (13, (2,) * 10 + (3, 3, 4), (0, 3, 3) + (6,) * 10),
    (13, (2,) * 9 + (3,) * 4, (3,) * 4 + (6,) * 9),
    (12, (2,) * 6 + (3,) * 6, (2,) * 6 + (5,) * 6),
    (11, (2,) * 3 + (3,) * 8, (1,) * 8 + (4,) * 3),
    (10, (3,) * 10, (0,) * 10),
)

EXPECTED_R15_MODES = (
    ((1, 0), (1, 0), (1, 0)),
    ((1, 0), (2, 0), (2, 0)),
    ((2, 0), (2, 0), (2, 0)),
    ((2, 0), (2, 0), (3, 1)),
)


def fixed_length_partitions(
    total: int, length: int, minimum: int, maximum: int
) -> Iterator[tuple[int, ...]]:
    """Yield nondecreasing fixed-length integer partitions."""

    def rec(prefix: tuple[int, ...], remaining: int, slots: int, low: int):
        if slots == 0:
            if remaining == 0:
                yield prefix
            return
        high = min(maximum, remaining // slots)
        for value in range(low, high + 1):
            tail = remaining - value
            if tail < value * (slots - 1) or tail > maximum * (slots - 1):
                continue
            yield from rec(prefix + (value,), tail, slots - 1, value)

    yield from rec((), total, length, minimum)


def active_profiles(total_q: int = 30) -> tuple[tuple[int, tuple[int, ...], tuple[int, ...]], ...]:
    """Enumerate all active-q profiles under q>=2 and 3q<=r-1."""

    found = []
    for r in range(1, total_q // 2 + 1):
        maximum = (r - 1) // 3
        if maximum < 2:
            continue
        for q_values in fixed_length_partitions(total_q, r, 2, maximum):
            k_degrees = tuple(sorted(r - 1 - 3 * q for q in q_values))
            found.append((r, q_values, k_degrees))
    return tuple(sorted(found, key=lambda item: (-item[0], item[1])))


def profiles_after_non_singleton_filter():
    """Three non-singleton, linear point sets consume 3 distinct K-edges."""

    return tuple(profile for profile in active_profiles() if min(profile[2]) >= 3)


def ordered_nonempty_disjoint_parts(
    universe: Sequence[str], count: int
) -> tuple[tuple[frozenset[str], ...], ...]:
    """Enumerate ordered nonempty pairwise-disjoint subsets of universe."""

    answers = []
    choices = range(count + 1)  # zero means unused
    for assignment in product(choices, repeat=len(universe)):
        if any(label not in assignment for label in range(1, count + 1)):
            continue
        parts = tuple(
            frozenset(universe[pos] for pos, owner in enumerate(assignment) if owner == label)
            for label in range(1, count + 1)
        )
        answers.append(parts)
    return tuple(answers)


def degree_three_closure() -> dict[str, object]:
    """Replay the d_K=3 contradiction using only local point axioms."""

    neighbours = ("a", "b", "c")
    through_x = tuple(frozenset(("x", label)) for label in neighbours)
    forced_pairs = set()
    part_counts = {}
    for base in neighbours:
        available = tuple(label for label in neighbours if label != base)
        partitions = ordered_nonempty_disjoint_parts(available, 2)
        # Two nonempty disjoint external parts inside two labels must be the
        # two singleton parts, in either order.
        assert len(partitions) == 2
        assert {
            frozenset(parts) for parts in partitions
        } == {
            frozenset((frozenset((available[0],)), frozenset((available[1],))))
        }
        part_counts[base] = len(partitions)
        for endpoint in available:
            forced_pairs.add(frozenset((base, endpoint)))

    triangle_points = (
        frozenset(("a", "b")),
        frozenset(("a", "c")),
        frozenset(("b", "c")),
    )
    intersections = (
        triangle_points[0] & triangle_points[1],
        triangle_points[0] & triangle_points[2],
        triangle_points[1] & triangle_points[2],
    )
    assert all(len(value) == 1 for value in intersections)
    assert len(set().union(*intersections)) == 3
    assert set(triangle_points) <= forced_pairs
    return {
        "through_x": sorted(sorted(point) for point in through_x),
        "forced_triangle_points": sorted(sorted(point) for point in triangle_points),
        "ordered_partitions_per_base": part_counts,
        "berge_triangle_intersections": sorted(next(iter(value)) for value in intersections),
    }


def minimum_singleton_petals(r: int, point_size: int) -> int:
    """Minimum petals with one-label external part in the flower count."""

    petals = 2 * point_size
    outside = r - point_size
    # outside >= h + 2(petals-h) = 2*petals-h
    return max(0, 2 * petals - outside)


def large_point_flower_audit() -> dict[str, object]:
    """Check the r=14/r=15 size-four and size-five petal bounds."""

    mixed_s4_singletons = minimum_singleton_petals(14, 4)
    assert mixed_s4_singletons == 6
    assert 3 + mixed_s4_singletons == 9 > 7

    r15_s5_singletons = minimum_singleton_petals(15, 5)
    assert r15_s5_singletons == 10
    assert 4 + r15_s5_singletons == 14 > 8

    r15_s4_singletons = minimum_singleton_petals(15, 4)
    assert r15_s4_singletons == 5
    # With exactly five singleton petals, each of the other three has at
    # least two external labels.  At the base of any such petal the internal
    # root neighbours, all five common endpoints, and those two labels are
    # distinct.
    r15_s4_h5_root_degree = 3 + 5 + 2
    assert r15_s4_h5_root_degree == 10 > 8
    # Six or more singleton petals already exceed degree eight at every root.
    assert all(3 + h > 8 for h in range(6, 9))

    return {
        "mixed_r14_size4": {
            "minimum_singleton_petals": mixed_s4_singletons,
            "minimum_root_K_degree": 3 + mixed_s4_singletons,
            "maximum_available_K_degree": 7,
        },
        "r15_size5": {
            "singleton_petals": r15_s5_singletons,
            "minimum_root_K_degree": 4 + r15_s5_singletons,
            "available_K_degree": 8,
        },
        "r15_size4": {
            "minimum_singleton_petals": r15_s4_singletons,
            "h5_witness_root_K_degree": r15_s4_h5_root_degree,
            "h_ge_6_minimum_root_K_degree": 9,
            "available_K_degree": 8,
        },
    }


def mixed_flower_modes(reuse_forced_neighbours: bool = False) -> tuple[tuple[int, ...], ...]:
    """Enumerate (t_i) modes for an ordinary r=14 size-three point."""

    modes = set()
    for t_values in product(range(1, 4), repeat=3):
        if sum(t_values) > 8:
            continue
        valid = True
        for root in range(3):
            terms = [3 - t_values[base] for base in range(3) if base != root]
            forced = max(terms) if reuse_forced_neighbours else sum(terms)
            if forced > 4 - t_values[root]:
                valid = False
                break
        if valid:
            modes.add(tuple(sorted(t_values)))
    return tuple(sorted(modes))


def mixed_profile_local_audit() -> dict[str, object]:
    """Replay every local branch in the mixed r=14 profile."""

    # If a size-three point contains a special label x, then t_x=1 and
    # d_U(x)=0.  The cyclic flower inequality at x forces t_y=t_z=3.
    special_first_stage = []
    for t_y, t_z in product(range(1, 4), repeat=2):
        if (3 - t_y) + (3 - t_z) <= 0:
            special_first_stage.append((t_y, t_z))
    assert special_first_stage == [(3, 3)]
    # The two size-two petals at x then give two distinct U-neighbours at y,
    # while ordinary t_y=3 has capacity one.
    special_forced_at_y = 3 - 1
    special_capacity_at_y = 4 - 3
    assert special_forced_at_y == 2 > special_capacity_at_y == 1

    modes = mixed_flower_modes()
    assert modes == ((2, 2, 2), (2, 3, 3))

    # In mode 233, the unique size-two petal at the t=2 root saturates the
    # one available U-edge at both t=3 roots.  Every size-three co-point then
    # has one of those saturated roots on the P side of its crossing.
    t_values = (2, 3, 3)
    saturated_roots = {1, 2}
    full_crossing_bases = []
    for base, t_value in enumerate(t_values):
        for _ in range(t_value - 1):
            p_external = {root for root in range(3) if root != base}
            assert p_external & saturated_roots
            full_crossing_bases.append(base)
    assert Counter(full_crossing_bases) == Counter({0: 1, 1: 2, 2: 2})
    assert len(full_crossing_bases) * 4 == 20 > 12

    # In the all-size-two residue, a special label has three F-neighbours.
    # At any one F-neighbour, triangle-freeness puts its other two neighbours
    # outside N_F(x), giving five distinct K-neighbours of x.
    all_size_two_forced_K_degree = 3 + 2
    assert all_size_two_forced_K_degree == 5 > 4

    return {
        "special_size3": {
            "surviving_other_t_pair_before_second_contradiction": special_first_stage,
            "forced_U_at_ordinary_root": special_forced_at_y,
            "ordinary_root_U_capacity": special_capacity_at_y,
        },
        "ordinary_size3_modes": modes,
        "mode233": {
            "forced_full_crossing_bases": full_crossing_bases,
            "distinct_actual_neighbour_contribution": len(full_crossing_bases) * 4,
            "fixed_point_sum": 12,
        },
        "all_size_two": {
            "special_forced_K_degree": all_size_two_forced_K_degree,
            "special_available_K_degree": 4,
        },
    }


def r15_local_modes(
    *,
    empty_crossing_coefficient: int = 2,
    full_crossing_limit: int = 3,
) -> tuple[dict[str, object], ...]:
    """Enumerate labeled (t_i,a_i) states at an r=15 size-three point."""

    states = []
    for t_values in product(range(1, 4), repeat=3):
        for a_values in product(*(range(t_value) for t_value in t_values)):
            forced = tuple(
                sum(
                    3 - t_values[base] + empty_crossing_coefficient * a_values[base]
                    for base in range(3)
                    if base != root
                )
                for root in range(3)
            )
            capacities = tuple(5 - value for value in t_values)
            full_crossings = sum(t_values) - 3 - sum(a_values)
            if any(need > cap for need, cap in zip(forced, capacities)):
                continue
            if full_crossings > full_crossing_limit:
                continue
            states.append(
                {
                    "t": t_values,
                    "a": a_values,
                    "forced": forced,
                    "capacities": capacities,
                    "full_crossings": full_crossings,
                    "canonical": tuple(sorted(zip(t_values, a_values))),
                }
            )
    return tuple(states)


def canonical_r15_modes(**kwargs) -> tuple[tuple[tuple[int, int], ...], ...]:
    return tuple(sorted({state["canonical"] for state in r15_local_modes(**kwargs)}))


def explicit_forced_u_sets(
    t_values: tuple[int, int, int], a_values: tuple[int, int, int]
) -> tuple[frozenset[tuple[str, str]], ...]:
    """Build distinct symbolic flower endpoints and literal forced U-edges."""

    roots = ("p0", "p1", "p2")
    forced_by_root = [set(), set(), set()]
    endpoint_serial = 0
    for base in range(3):
        part_sizes = [1] * (3 - t_values[base]) + [2] * a_values[base]
        for part_size in part_sizes:
            endpoints = []
            for _ in range(part_size):
                endpoints.append(f"e{endpoint_serial}")
                endpoint_serial += 1
            for root in range(3):
                if root == base:
                    continue
                for endpoint in endpoints:
                    edge = tuple(sorted((roots[root], endpoint)))
                    forced_by_root[root].add(edge)
                    # A hypothetical owner of this cross-pair would meet the
                    # root point, the petal, and itself at three distinct
                    # labels: roots[root], roots[base], endpoint.
                    assert len({roots[root], roots[base], endpoint}) == 3
    expected = tuple(
        sum(3 - t_values[base] + 2 * a_values[base] for base in range(3) if base != root)
        for root in range(3)
    )
    actual = tuple(len(edges) for edges in forced_by_root)
    assert actual == expected
    return tuple(frozenset(edges) for edges in forced_by_root)


def bipartite_crossing_distribution(
    left_size: int, right_size: int, *, two_sided: bool = True
) -> dict[int, int]:
    """Enumerate simple crossings with every checked degree in {0,2}."""

    distribution: Counter[int] = Counter()
    edge_slots = left_size * right_size
    for bits in product((0, 1), repeat=edge_slots):
        rows = [
            sum(bits[row * right_size + column] for column in range(right_size))
            for row in range(left_size)
        ]
        columns = [
            sum(bits[row * right_size + column] for row in range(left_size))
            for column in range(right_size)
        ]
        if any(degree not in (0, 2) for degree in rows):
            continue
        if two_sided and any(degree not in (0, 2) for degree in columns):
            continue
        distribution[sum(bits)] += 1
    return dict(sorted(distribution.items()))


def crossing_case_table() -> dict[str, list[int]]:
    """All endpoint-size cases remaining after the flower bounds."""

    table = {}
    for left, right in combinations_with_replacement((0, 2, 3), 2):
        table[f"disjoint_{left}_{right}"] = sorted(
            bipartite_crossing_distribution(left, right)
        )
        if left and right:
            table[f"overlap_{left}_{right}"] = sorted(
                bipartite_crossing_distribution(left - 1, right - 1)
            )
    return table


def symmetric_degree_one_graphs_on_three() -> tuple[tuple[tuple[int, int], ...], ...]:
    """Enumerate undirected three-vertex graphs in which every degree is one."""

    possible_edges = tuple(combinations(range(3), 2))
    answers = []
    for mask in range(1 << len(possible_edges)):
        chosen = tuple(
            edge for position, edge in enumerate(possible_edges) if mask & (1 << position)
        )
        degrees = [0, 0, 0]
        for left, right in chosen:
            degrees[left] += 1
            degrees[right] += 1
        if degrees == [1, 1, 1]:
            answers.append(chosen)
    return tuple(answers)


def simple_edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(combinations(range(order), 2))


def is_triangle_free(order: int, edges: Iterable[tuple[int, int]]) -> bool:
    edge_set = {tuple(sorted(edge)) for edge in edges}
    return not any(
        tuple(sorted((a, b))) in edge_set
        and tuple(sorted((a, c))) in edge_set
        and tuple(sorted((b, c))) in edge_set
        for a, b, c in combinations(range(order), 3)
    )


def cubic_triangle_free_graphs(order: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    """Small labeled census used for the mixed-profile intersection graph."""

    if order % 2:
        return ()
    all_edges = simple_edges(order)
    target_edges = 3 * order // 2
    answers = []
    for chosen in combinations(all_edges, target_edges):
        degrees = [0] * order
        for left, right in chosen:
            degrees[left] += 1
            degrees[right] += 1
        if degrees != [3] * order:
            continue
        if is_triangle_free(order, chosen):
            answers.append(chosen)
    return tuple(answers)


def line_graph_open_neighbourhoods(
    edges: Sequence[tuple[int, int]]
) -> tuple[frozenset[int], ...]:
    return tuple(
        frozenset(
            other
            for other, candidate in enumerate(edges)
            if other != index and set(edge) & set(candidate)
        )
        for index, edge in enumerate(edges)
    )


def mixed_intersection_graph_census() -> dict[str, object]:
    order4 = cubic_triangle_free_graphs(4)
    order6 = cubic_triangle_free_graphs(6)
    assert not order4
    # The ten labeled graphs are the ten unordered 3+3 bipartitions.
    assert len(order6) == 10
    open_twin_counts = []
    for graph in order6:
        neighbourhoods = line_graph_open_neighbourhoods(graph)
        open_twin_counts.append(len(neighbourhoods) - len(set(neighbourhoods)))
    assert set(open_twin_counts) == {0}
    possible_edge_counts = [
        edges
        for edges in range(1, 10)
        if (2 * edges) % 3 == 0 and (2 * edges) // 3 in (4, 6)
    ]
    assert possible_edge_counts == [6, 9]
    return {
        "edge_counts_after_incidence_bound": possible_edge_counts,
        "order4_labeled_survivors": len(order4),
        "order6_labeled_survivors": len(order6),
        "order6_open_twin_counts": sorted(Counter(open_twin_counts).items()),
        "ordinary_t0_labels_after_e9": 3,
        "required_injective_images": 9,
    }


def mode111_saturation_audit() -> dict[str, object]:
    """Enumerate every remaining disjoint point candidate against a 111 point."""

    roots = ("i", "j", "k")
    endpoints = tuple(f"a{index}" for index in range(6))
    residual = tuple(f"z{index}" for index in range(6))
    assert len(set(roots + endpoints + residual)) == 15

    # Each endpoint is K-adjacent to all roots.  With the two internal root
    # neighbours this exactly saturates K-degree eight at each root.
    saturated_neighbourhoods = {
        root: frozenset((set(roots) - {root}) | set(endpoints)) for root in roots
    }
    assert {len(value) for value in saturated_neighbourhoods.values()} == {8}

    # A residual z has all three L-edges into the root point.  Any disjoint
    # candidate containing z has a crossing vertex of degree three and cannot
    # be an actual graph neighbour under the two-sided 0/2 rule.
    candidates = []
    valid_crossing_sizes = set()
    rejected_for_degree_three = 0
    outside = endpoints + residual
    for size in (2, 3):
        for candidate in combinations(outside, size):
            row_degrees = tuple(0 if label in endpoints else 3 for label in candidate)
            candidates.append(candidate)
            if any(degree not in (0, 2) for degree in row_degrees):
                rejected_for_degree_three += 1
                continue
            valid_crossing_sizes.add(sum(row_degrees))
    assert valid_crossing_sizes == {0}

    # The six overlapping petals have external sizes 1 by 2, hence empty.
    assert set(bipartite_crossing_distribution(1, 2)) == {0}
    return {
        "root_K_degree": 8,
        "disjoint_candidates_checked": len(candidates),
        "disjoint_candidates_rejected_for_degree_three": rejected_for_degree_three,
        "valid_disjoint_crossing_sizes": sorted(valid_crossing_sizes),
        "overlapping_petals_checked": 6,
        "inactive_crossing_size": 0,
    }


def final_degree_audit() -> dict[str, object]:
    table = crossing_case_table()
    expected = {
        "disjoint_0_0": [0],
        "disjoint_0_2": [0],
        "disjoint_0_3": [0],
        "disjoint_2_2": [0, 4],
        "disjoint_2_3": [0, 4],
        "disjoint_3_3": [0, 4, 6],
        "overlap_2_2": [0],
        "overlap_2_3": [0],
        "overlap_3_3": [0, 4],
    }
    assert table == expected

    # After t=3 and 111 are removed, the 122 and 222 modes start with two or
    # three distinct full overlapping crossings, respectively.
    size_three_modes = {
        "122": {"preloaded_degree": 8, "remaining_capacity": 4},
        "222": {"preloaded_degree": 12, "remaining_capacity": 0},
    }
    for data in size_three_modes.values():
        assert data["preloaded_degree"] + data["remaining_capacity"] == 12
        assert data["preloaded_degree"] + 6 > 12

    # The only raw degree six case is disjoint 3-by-3.  It is impossible at
    # either endpoint by the fixed-point capacities above.
    surviving_degrees = {0, 4}
    handshake_sum = 2 * 45
    assert handshake_sum % 4 == 2
    assert all(degree % 4 == 0 for degree in surviving_degrees)
    return {
        "crossing_cases": table,
        "size_three_modes": size_three_modes,
        "surviving_H_degrees": sorted(surviving_degrees),
        "H_edges": 45,
        "handshake_sum": handshake_sum,
        "handshake_mod_4": handshake_sum % 4,
    }


def adversarial_mutations() -> dict[str, object]:
    """Exhibit witnesses when a critical premise or inequality is weakened."""

    authentic_mixed = set(mixed_flower_modes())
    reused_mixed = set(mixed_flower_modes(reuse_forced_neighbours=True))
    reuse_witnesses = sorted(reused_mixed - authentic_mixed)
    assert reuse_witnesses

    authentic_r15 = set(canonical_r15_modes())
    one_endpoint_per_empty = set(
        canonical_r15_modes(empty_crossing_coefficient=1)
    )
    no_fixed_sum = set(canonical_r15_modes(full_crossing_limit=99))
    assert one_endpoint_per_empty - authentic_r15
    assert no_fixed_sum - authentic_r15

    one_sided_singleton = bipartite_crossing_distribution(1, 2, two_sided=False)
    assert 2 in one_sided_singleton
    assert set(bipartite_crossing_distribution(1, 2, two_sided=True)) == {0}

    assert not symmetric_degree_one_graphs_on_three()
    directed_cycle = ((0, 1), (1, 2), (2, 0))
    assert {left for left, _ in directed_cycle} == {0, 1, 2}

    # Without the common-point owner veto, the forced K-edge {i,a} could be
    # consumed by a third point.  The three pairwise intersections below are
    # distinct, exactly identifying the omitted forbidden Berge triangle.
    root_point = frozenset(("i", "j", "k"))
    petal = frozenset(("j", "a"))
    hypothetical_owner = frozenset(("i", "a"))
    owner_intersections = (
        root_point & petal,
        root_point & hypothetical_owner,
        petal & hypothetical_owner,
    )
    assert {next(iter(value)) for value in owner_intersections} == {"i", "j", "a"}

    # If degree six is not removed by the fixed-point capacity, the handshake
    # value has the explicit decomposition 90 = 6 + 21*4.
    weakened_handshake = [6] + [4] * 21
    assert sum(weakened_handshake) == 90
    assert (2 * (2 * 45)) % 4 == 0  # factor-of-two error in |E(H)| also hides it

    low_degree_profiles = tuple(
        profile for profile in active_profiles() if min(profile[2]) < 3
    )
    assert low_degree_profiles

    return {
        "drop_no_singleton_low_degree_profile": {
            "r": low_degree_profiles[0][0],
            "q": low_degree_profiles[0][1],
            "K_degrees": low_degree_profiles[0][2],
        },
        "reuse_forced_U_neighbours_extra_mixed_modes": reuse_witnesses,
        "count_one_U_neighbour_per_empty_crossing_extra_modes": sorted(
            one_endpoint_per_empty - authentic_r15
        ),
        "drop_fixed_point_full_crossing_limit_extra_modes": sorted(
            no_fixed_sum - authentic_r15
        ),
        "one_sided_singleton_crossing_distribution": one_sided_singleton,
        "directed_empty_crossing_cycle_witness": directed_cycle,
        "owner_veto_intersections": sorted(next(iter(value)) for value in owner_intersections),
        "allow_degree_six_handshake_witness": weakened_handshake,
        "double_count_H_edges_handshake_sum": 2 * (2 * 45),
    }


def run_all(include_mutations: bool = False) -> dict[str, object]:
    profiles = active_profiles()
    assert profiles == EXPECTED_PROFILES

    non_singleton_survivors = profiles_after_non_singleton_filter()
    assert tuple((r, q) for r, q, _ in non_singleton_survivors) == (
        (15, (2,) * 15),
        (14, (2,) * 12 + (3, 3)),
        (13, (2,) * 9 + (3,) * 4),
    )

    degree_three = degree_three_closure()
    # The r=13 survivor contains degree-three labels, so the local closure
    # eliminates it and leaves exactly r=14 and r=15.
    after_degree_three = tuple(
        profile for profile in non_singleton_survivors if 3 not in profile[2]
    )
    assert tuple(profile[0] for profile in after_degree_three) == (15, 14)

    assert minimum_singleton_petals(14, 4) == 6
    assert minimum_singleton_petals(15, 5) == 10
    assert minimum_singleton_petals(15, 4) == 5
    large_points = large_point_flower_audit()

    mixed_modes = mixed_flower_modes()
    assert mixed_modes == ((2, 2, 2), (2, 3, 3))
    mixed_local = mixed_profile_local_audit()

    # Literal symbolic flower construction checks both the coefficients and
    # distinctness of the forced-neighbour lower bounds.
    for t_values in mixed_modes:
        forced_sets = explicit_forced_u_sets(t_values, (0, 0, 0))
        expected_counts = tuple(
            sum(3 - t_values[base] for base in range(3) if base != root)
            for root in range(3)
        )
        assert tuple(len(edges) for edges in forced_sets) == expected_counts

    r15_modes = canonical_r15_modes()
    assert r15_modes == EXPECTED_R15_MODES
    for state in r15_local_modes():
        explicit = explicit_forced_u_sets(state["t"], state["a"])
        assert tuple(len(edges) for edges in explicit) == state["forced"]

    parity = symmetric_degree_one_graphs_on_three()
    assert parity == ()

    r_census = mixed_intersection_graph_census()
    mode111 = mode111_saturation_audit()
    final = final_degree_audit()

    result = {
        "schema_version": 1,
        "scope": "conditional Wave 13 n3=45 reduction",
        "target_result": "UNKNOWN",
        "novelty_status": "UNKNOWN",
        "active_profiles": [
            {"r": r, "q": q_values, "K_degrees": k_degrees}
            for r, q_values, k_degrees in profiles
        ],
        "profiles_after_dK_at_least_3": [
            {"r": r, "q": q_values, "K_degrees": k_degrees}
            for r, q_values, k_degrees in non_singleton_survivors
        ],
        "degree_three_closure": degree_three,
        "flower_singleton_bounds": {
            "r14_s4": 6,
            "r15_s5": 10,
            "r15_s4": 5,
        },
        "large_point_flower_audit": large_points,
        "mixed_r14_modes": mixed_modes,
        "mixed_r14_local_audit": mixed_local,
        "mixed_intersection_graph_census": r_census,
        "r15_modes": [
            {
                "aligned_t_a": mode,
                "representative_count": sum(
                    state["canonical"] == mode for state in r15_local_modes()
                ),
            }
            for mode in r15_modes
        ],
        "t3_symmetric_degree_one_graphs": len(parity),
        "mode111_saturation": mode111,
        "final_degree_audit": final,
        "verdict": "PASS",
    }
    if include_mutations:
        result["adversarial_mutations"] = adversarial_mutations()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mutations",
        action="store_true",
        help="also run and print weakened-premise countermodel witnesses",
    )
    args = parser.parse_args()
    result = run_all(include_mutations=args.mutations)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
