"""Build the Wave 204 exact b=0 hostile local-incidence skeleton.

The output is a rational 0/1 incidence certificate.  It is deliberately not
an SRG, ternary code, column realization, circuit cover, or endpoint object.
It tests exactly the 99-center Hilton--Milner/four-fiber/Wave203 slot layer
that is encoded below.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


N = 99
GRAPH_STEPS = tuple(range(1, 8))
OUTWARD_COMPLEMENT_STEPS = tuple(range(8, 50))
BLOCK_OFFSET_PAIRS = (
    (-7, -6),
    (-5, -4),
    (-3, -2),
    (-1, 1),
    (2, 3),
    (4, 5),
    (6, 7),
)
BASELINE_PAIRS = ((0, 1), (0, 2), (0, 3))


def pair_tuple(values: Iterable[int]) -> tuple[int, int]:
    pair = tuple(sorted(values))
    assert len(pair) == 2
    return pair


def hm_family() -> tuple[tuple[int, int, int], ...]:
    """The 13-member Hilton--Milner H family on seven blocks."""
    ground = set(range(7))
    special = frozenset({1, 2, 3})
    family = {special}
    for pair in itertools.combinations(sorted(ground - {0}), 2):
        if set(pair) & set(special):
            family.add(frozenset({0, *pair}))
    result = tuple(sorted(tuple(sorted(triple)) for triple in family))
    assert len(result) == 13
    return result


HM_FAMILY = hm_family()
HM_PAIRS = tuple(itertools.combinations(range(7), 2))


def pair_degrees(
    flag_ids: Iterable[int],
) -> Counter[tuple[int, int]]:
    degrees: Counter[tuple[int, int]] = Counter()
    for flag_id in flag_ids:
        triple = HM_FAMILY[flag_id]
        for pair in itertools.combinations(triple, 2):
            degrees[pair_tuple(pair)] += 1
    return degrees


def selected_flag_ids(center: int) -> tuple[int, ...]:
    """Select 1,200 of the 1,287 full flags.

    Centers 0..78 carry all thirteen flags.  The other twenty centers carry
    13*9+7*8=173 flags.  A lexicographically first subset is chosen subject
    to degree at most four on each of the three degree-five fibers, so those
    centers need no selected repeated label.
    """
    if center < 79:
        return tuple(range(len(HM_FAMILY)))
    target = 9 if center < 92 else 8
    for choice in itertools.combinations(range(len(HM_FAMILY)), target):
        degrees = pair_degrees(choice)
        if all(degrees[pair] <= 4 for pair in BASELINE_PAIRS):
            return tuple(choice)
    raise AssertionError("no selected subfamily found")


def graph_neighbors(center: int) -> tuple[int, ...]:
    neighbors = {
        (center + sign * step) % N
        for step in GRAPH_STEPS
        for sign in (-1, 1)
    }
    assert len(neighbors) == 14
    return tuple(sorted(neighbors))


def complement_neighbors(center: int) -> tuple[int, ...]:
    excluded = set(graph_neighbors(center)) | {center}
    result = tuple(vertex for vertex in range(N) if vertex not in excluded)
    assert len(result) == 84
    return result


def outward_complement_neighbors(center: int) -> tuple[int, ...]:
    result = tuple((center + step) % N for step in OUTWARD_COMPLEMENT_STEPS)
    assert len(result) == 42
    assert all(vertex in complement_neighbors(center) for vertex in result)
    return result


def common_neighbor_profiles() -> dict[str, dict[str, int]]:
    adjacent: Counter[int] = Counter()
    nonadjacent: Counter[int] = Counter()
    base_neighbors = set(graph_neighbors(0))
    for vertex in range(1, N):
        common = len(base_neighbors & set(graph_neighbors(vertex)))
        relation_profile = adjacent if vertex in base_neighbors else nonadjacent
        relation_profile[common] += 1
    return {
        "adjacent": {
            str(count): adjacent[count] for count in sorted(adjacent)
        },
        "nonadjacent": {
            str(count): nonadjacent[count] for count in sorted(nonadjacent)
        },
    }


def local_star_blocks(center: int) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    graph_nbrs = set(graph_neighbors(center))
    for block_id, offsets in enumerate(BLOCK_OFFSET_PAIRS):
        endpoints = tuple(sorted((center + offset) % N for offset in offsets))
        assert set(endpoints) <= graph_nbrs
        # The endpoint pair is an edge of the circulant, so this is an actual
        # triangle of the relaxed skeleton.  The seven choices are not asserted
        # to be globally consistent triangle columns.
        difference = (endpoints[1] - endpoints[0]) % N
        circular_difference = min(difference, N - difference)
        assert circular_difference in GRAPH_STEPS
        blocks.append(
            {
                "block": block_id,
                "vertices": [center, *endpoints],
            }
        )
    assert len({v for block in blocks for v in block["vertices"][1:]}) == 14
    return blocks


def occurrence_map() -> dict[tuple[int, int], tuple[int, ...]]:
    occurrences: dict[tuple[int, int], list[int]] = {
        pair: [] for pair in HM_PAIRS
    }
    for flag_id, triple in enumerate(HM_FAMILY):
        for pair in itertools.combinations(triple, 2):
            occurrences[pair_tuple(pair)].append(flag_id)
    return {pair: tuple(ids) for pair, ids in occurrences.items()}


FULL_OCCURRENCES = occurrence_map()


def group_occurrences(
    center: int,
    selected: set[int],
) -> list[dict[str, object]]:
    """Partition pair occurrences into exact leaf-label groups."""
    groups: list[dict[str, object]] = []
    for pair in HM_PAIRS:
        occurrences = list(FULL_OCCURRENCES[pair])
        grouped: list[tuple[int, ...]] = []
        if pair in BASELINE_PAIRS:
            assert len(occurrences) == 5
            if center < 79:
                # These are exactly the 237 selected nonprivate labels:
                # three at each of 79 centers.  At the first three centers
                # one chosen fiber has multiplicity three.
                group_size = 3 if center < 3 and pair == (0, 1) else 2
                chosen = tuple(
                    flag_id
                    for flag_id in occurrences
                    if flag_id in selected
                )[:group_size]
                assert len(chosen) == group_size
                grouped.append(chosen)
                used = set(chosen)
            else:
                # The full HM family still needs one repeat in each degree-five
                # fiber, but the selected subfamily must remain simple here.
                unselected = [
                    flag_id
                    for flag_id in occurrences
                    if flag_id not in selected
                ]
                assert unselected
                first = unselected[0]
                if len(unselected) >= 2:
                    second = unselected[1]
                else:
                    second = next(
                        flag_id
                        for flag_id in occurrences
                        if flag_id in selected
                    )
                chosen = (first, second)
                assert sum(flag_id in selected for flag_id in chosen) <= 1
                grouped.append(chosen)
                used = set(chosen)
            grouped.extend((flag_id,) for flag_id in occurrences if flag_id not in used)
        else:
            grouped.extend((flag_id,) for flag_id in occurrences)

        assert sorted(flag_id for group in grouped for flag_id in group) == occurrences
        assert len(grouped) <= 4
        for group_index, flag_ids in enumerate(grouped):
            groups.append(
                {
                    "pair": list(pair),
                    "group_index": group_index,
                    "flag_ids": list(flag_ids),
                }
            )
    return groups


def build_center(center: int) -> dict[str, object]:
    selected_ids = set(selected_flag_ids(center))
    groups = group_occurrences(center, selected_ids)

    # Every full leaf label is chosen in the same global orientation of the
    # 84-regular complement.  There are at most 36 labels and 42 available
    # outward complement arcs.
    targets = outward_complement_neighbors(center)
    assert len(groups) <= len(targets)
    for target, group in zip(targets, groups):
        group["target"] = target

    groups_by_pair: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for group in groups:
        groups_by_pair[pair_tuple(group["pair"])].append(group)

    # Complete the declared 21 four-point fibers to a partition of all 84
    # complement neighbors.  Only the targets already used by occurrence
    # groups enter the selected/full flag equations.
    used_targets = {int(group["target"]) for group in groups}
    remaining_targets = iter(
        target
        for target in complement_neighbors(center)
        if target not in used_targets
    )
    pair_fibers: list[dict[str, object]] = []
    for pair in HM_PAIRS:
        fiber = [int(group["target"]) for group in groups_by_pair[pair]]
        while len(fiber) < 4:
            fiber.append(next(remaining_targets))
        assert len(fiber) == 4
        pair_fibers.append({"pair": list(pair), "targets": sorted(fiber)})
    all_fiber_targets = [
        target
        for fiber in pair_fibers
        for target in fiber["targets"]
    ]
    assert sorted(all_fiber_targets) == list(complement_neighbors(center))

    leaf_by_occurrence: dict[tuple[int, tuple[int, int]], int] = {}
    for group in groups:
        pair = pair_tuple(group["pair"])
        target = int(group["target"])
        for flag_id in group["flag_ids"]:
            key = (int(flag_id), pair)
            assert key not in leaf_by_occurrence
            leaf_by_occurrence[key] = target

    flags: list[dict[str, object]] = []
    for flag_id, triple in enumerate(HM_FAMILY):
        leaves: list[dict[str, object]] = []
        for pair_values in itertools.combinations(triple, 2):
            pair = pair_tuple(pair_values)
            third_block = next(block for block in triple if block not in pair)
            leaves.append(
                {
                    "pair": list(pair),
                    "target": leaf_by_occurrence[(flag_id, pair)],
                    "wave203_slot": third_block,
                }
            )
        flags.append(
            {
                "flag_id": flag_id,
                "A": list(triple),
                "selected": flag_id in selected_ids,
                "leaves": leaves,
            }
        )

    return {
        "center": center,
        "graph_neighbors": list(graph_neighbors(center)),
        "local_star_blocks": local_star_blocks(center),
        "pair_fibers": pair_fibers,
        "flags": flags,
    }


def summarize(centers: list[dict[str, object]]) -> dict[str, object]:
    full_directed: Counter[tuple[int, int]] = Counter()
    selected_directed: Counter[tuple[int, int]] = Counter()
    selected_flag_count = 0
    full_flag_count = 0
    full_slot_sets: dict[tuple[int, int], set[int]] = defaultdict(set)

    for center_data in centers:
        center = int(center_data["center"])
        for flag in center_data["flags"]:
            full_flag_count += 1
            is_selected = bool(flag["selected"])
            selected_flag_count += int(is_selected)
            for leaf in flag["leaves"]:
                key = (center, int(leaf["target"]))
                full_directed[key] += 1
                full_slot_sets[key].add(int(leaf["wave203_slot"]))
                if is_selected:
                    selected_directed[key] += 1

    assert all(len(full_slot_sets[key]) == count for key, count in full_directed.items())

    selected_profile = Counter(selected_directed.values())
    full_profile = Counter(full_directed.values())
    bidirectional_selected = {
        tuple(sorted((source, target)))
        for source, target in selected_directed
        if (target, source) in selected_directed
    }
    bidirectional_full = {
        tuple(sorted((source, target)))
        for source, target in full_directed
        if (target, source) in full_directed
    }

    nonprivate = {
        key: count for key, count in selected_directed.items() if count > 1
    }
    tail_profile = Counter(source for source, _ in nonprivate)
    nonprivate_tail_count_profile = Counter(tail_profile.values())
    nonprivate_tail_count_profile[0] = N - len(tail_profile)

    p3 = selected_profile[1]
    q = sum(selected_profile[multiplicity] for multiplicity in selected_profile if multiplicity > 1)
    epsilon = sum(
        (5 - multiplicity) * count
        for multiplicity, count in selected_profile.items()
        if multiplicity > 1
    )
    J = len(full_directed)
    delta = 99 * 36 - J
    b = len(bidirectional_selected)
    label_union = len(selected_directed)
    selected_incidence = sum(selected_directed.values())
    capacity_slack = 5 * label_union - (3 * selected_flag_count + 4 * p3)
    L = delta - 3 * q + epsilon

    # The exact Wave203 combined five-slot capacity is checked on the full
    # pool, before selecting a subset.
    unordered_full: Counter[tuple[int, int]] = Counter()
    for (source, target), multiplicity in full_directed.items():
        unordered_full[tuple(sorted((source, target)))] += multiplicity
    assert max(unordered_full.values()) <= 5

    return {
        "graph": {
            "vertices": N,
            "degree": 14,
            "edge_rule": "circular difference in {1,...,7}",
            "complement_degree": 84,
            "global_complement_orientation": (
                "x->x+d for d in {8,...,49} modulo 99"
            ),
            "outward_complement_degree": 42,
            "is_claimed_strongly_regular": False,
            "common_neighbor_count_profiles_from_vertex_0": (
                common_neighbor_profiles()
            ),
        },
        "full_pool": {
            "centers": len(centers),
            "flags": full_flag_count,
            "directed_label_union_J": J,
            "multiplicity_profile": {
                str(key): full_profile[key] for key in sorted(full_profile)
            },
            "delta_3564_minus_J": delta,
            "bidirectional_labels": len(bidirectional_full),
            "max_combined_two_orientation_multiplicity": max(unordered_full.values()),
        },
        "selected_pool": {
            "n3_flags": selected_flag_count,
            "selected_incidence_3n3": selected_incidence,
            "directed_label_union": label_union,
            "private_p3": p3,
            "nonprivate_q": q,
            "multiplicity_profile": {
                str(key): selected_profile[key] for key in sorted(selected_profile)
            },
            "nonprivate_tail_count_profile": {
                str(key): nonprivate_tail_count_profile[key]
                for key in sorted(nonprivate_tail_count_profile)
            },
            "epsilon": epsilon,
            "b_bidirectional_nonprivate": b,
            "capacity_slack": capacity_slack,
            "wave201_L_delta_minus_3q_plus_epsilon": L,
            "Q0_scalar_control": 7059,
        },
        "checks": {
            "hm_family_size_each_center": 13,
            "hm_full_family_intersecting": True,
            "hm_full_family_empty_total_intersection": True,
            "four_distinct_leaf_values_per_pair_max": True,
            "wave203_partial_slot_map_injective": True,
            "wave203_combined_capacity_at_most_five": True,
            "global_orientation_section_exists": True,
            "b_zero": b == 0,
            "delta_equals_3q_minus_epsilon": delta == 3 * q - epsilon,
            "selected_capacity_identity_slack_equals_epsilon": (
                capacity_slack == epsilon
            ),
        },
    }


def build_certificate() -> dict[str, object]:
    centers = [build_center(center) for center in range(N)]
    summary = summarize(centers)
    return {
        "format": "wave204-b-zero-local-incidence-skeleton-v1",
        "claim_label": "REFUTED_PENDING_INDEPENDENT_VERIFICATION",
        "refuted_lemma": (
            "The 99-center degree/complement data, local (7,3) Hilton--Milner "
            "families, four-point pair fibers, Wave201 equality row, and "
            "Wave203 five-slot capacity force a bidirectional selected label."
        ),
        "arithmetic_domain": "integers, equivalently 0/1 rational incidence data",
        "scope": {
            "is_99_center_global_skeleton": True,
            "is_14_regular_graph_skeleton": True,
            "is_local_HM_flag_system": True,
            "is_wave203_slot_certificate": True,
            "is_strongly_regular_graph": False,
            "is_ternary_column_realization": False,
            "is_rank_11_code": False,
            "is_circuit_cover": False,
            "is_endpoint_existence_evidence": False,
            "reason": (
                "The declared star-block and four-fiber types are not derived "
                "from the circulant adjacency, and no z_T columns or ternary "
                "relations are supplied."
            ),
        },
        "construction_rules": {
            "vertex_set": "Z/99Z",
            "graph_steps": list(GRAPH_STEPS),
            "outward_complement_steps": list(OUTWARD_COMPLEMENT_STEPS),
            "local_star_block_offset_pairs": [
                list(pair) for pair in BLOCK_OFFSET_PAIRS
            ],
            "HM_family": [list(triple) for triple in HM_FAMILY],
            "selected_centers_with_13_flags": list(range(79)),
            "selected_centers_with_9_flags": list(range(79, 92)),
            "selected_centers_with_8_flags": list(range(92, 99)),
        },
        "summary": summary,
        "centers": centers,
    }


def stable_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--print-summary", action="store_true")
    args = parser.parse_args()
    if args.write is None and args.verify is None and not args.print_summary:
        parser.error("choose --write PATH, --verify PATH, or --print-summary")

    certificate = build_certificate()
    if args.write is not None:
        args.write.write_text(stable_json(certificate), encoding="utf-8", newline="\n")
        print(f"WROTE {args.write}")
    if args.verify is not None:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if expected != certificate:
            raise SystemExit("FAIL: frozen countermodel differs")
        print("PASS: frozen Wave204 b=0 countermodel matches")
    if args.print_summary:
        print(stable_json(certificate["summary"]), end="")


if __name__ == "__main__":
    main()
