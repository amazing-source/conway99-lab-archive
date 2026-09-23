#!/usr/bin/env python3
"""Memory-light exact-marginal local search for a Wave 60 design.

The within-component Gram equations uniquely prescribe a multiset of sixty
local pairs for each component.  This search couples those three multisets,
so every local equation is satisfied throughout.  Only the three
cross-component Gram blocks remain in the objective.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
CHECK_PATH = HERE / "exact_check.py"
SPEC = importlib.util.spec_from_file_location("wave60_exact_check", CHECK_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import exact checker")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def pair_category(left: int, right: int) -> tuple[str, int]:
    fibre_left = left // 12
    fibre_right = right // 12
    if fibre_left == fibre_right:
        return ("A", fibre_left)
    missing = ({0, 1, 2} - {fibre_left, fibre_right}).pop()
    return ("B", missing)


def build_slots(x_aaa: int) -> tuple[
    list[tuple[tuple[str, int], ...]],
    list[dict[tuple[str, int], list[int]]],
]:
    """Return a symmetric pattern ledger for x=0,6,12 AAA slots."""

    if x_aaa not in (0, 6, 12):
        raise ValueError("the symmetric ledger supports x_aaa in {0,6,12}")
    slots: list[tuple[tuple[str, int], ...]] = []
    for orientation_permutation in itertools.permutations(range(3)):
        for _ in range(x_aaa // 6):
            slots.append(
                tuple(("A", value) for value in orientation_permutation)
            )
    abb_repetitions = 4 - x_aaa // 3
    for a_component in range(3):
        for orientation in range(3):
            for _ in range(abb_repetitions):
                categories = []
                for component in range(3):
                    categories.append(
                        ("A", orientation)
                        if component == a_component
                        else ("B", orientation)
                    )
                slots.append(tuple(categories))
    bbb_repetitions = (16 - 2 * abb_repetitions) // 2
    for zero_permutation in itertools.permutations(range(3)):
        for _ in range(bbb_repetitions):
            slots.append(tuple(("B", value) for value in zero_permutation))
    if len(slots) != 60:
        raise AssertionError("slot count changed")
    by_component = [defaultdict(list) for _ in range(3)]
    for slot, categories in enumerate(slots):
        for component, category in enumerate(categories):
            by_component[component][category].append(slot)
    expected = {
        **{("A", index): 4 for index in range(3)},
        **{("B", index): 16 for index in range(3)},
    }
    for groups in by_component:
        if {key: len(value) for key, value in groups.items()} != expected:
            raise AssertionError("slot category ledger changed")
    return slots, by_component


def local_pair_multisets(
    adjacency: Sequence[set[int]],
) -> list[dict[tuple[str, int], list[tuple[int, int]]]]:
    gram = CHECK.gram_target(adjacency)
    result = []
    for component in range(3):
        groups: dict[tuple[str, int], list[tuple[int, int]]] = defaultdict(list)
        vertices = [
            CHECK.global_vertex(component, local)
            for local in range(CHECK.COMPONENT_SIZE)
        ]
        for left, right in itertools.combinations(vertices, 2):
            for _ in range(gram[left][right]):
                groups[pair_category(left, right)].append((left, right))
        expected = {
            **{("A", index): 4 for index in range(3)},
            **{("B", index): 16 for index in range(3)},
        }
        if {key: len(value) for key, value in groups.items()} != expected:
            raise AssertionError("local target category ledger changed")
        result.append(groups)
    return result


def cross_target(left: int, right: int) -> int:
    return 1 if left // 12 == right // 12 else 2


def cross_key(
    component: int,
    other: int,
    left: int,
    right: int,
) -> tuple[int, int, int, int]:
    if component < other:
        return component, other, left, right
    return other, component, right, left


def initialize(
    rng: random.Random,
    local_pairs: Sequence[dict[tuple[str, int], list[tuple[int, int]]]],
    slots_by_component: Sequence[dict[tuple[str, int], list[int]]],
) -> list[list[tuple[int, int]]]:
    assigned: list[list[tuple[int, int]]] = [
        [(-1, -1)] * 60 for _ in range(3)
    ]
    for component in range(3):
        for category, slots in slots_by_component[component].items():
            pairs = local_pairs[component][category][:]
            rng.shuffle(pairs)
            for slot, pair in zip(slots, pairs):
                assigned[component][slot] = pair
    if any(pair == (-1, -1) for row in assigned for pair in row):
        raise AssertionError("incomplete initialization")
    return assigned


def build_cross_counts(
    assigned: Sequence[Sequence[tuple[int, int]]],
) -> Counter[tuple[int, int, int, int]]:
    counts: Counter[tuple[int, int, int, int]] = Counter()
    for slot in range(60):
        for component, other in itertools.combinations(range(3), 2):
            for left in assigned[component][slot]:
                for right in assigned[other][slot]:
                    counts[cross_key(component, other, left, right)] += 1
    return counts


def full_score(counts: Counter[tuple[int, int, int, int]]) -> int:
    score = 0
    for component, other in itertools.combinations(range(3), 2):
        for local_left in range(12):
            left = CHECK.global_vertex(component, local_left)
            for local_right in range(12):
                right = CHECK.global_vertex(other, local_right)
                difference = (
                    counts[cross_key(component, other, left, right)]
                    - cross_target(left, right)
                )
                score += difference * difference
    return score


def swap_delta(
    assigned: Sequence[Sequence[tuple[int, int]]],
    counts: Counter[tuple[int, int, int, int]],
    component: int,
    slot1: int,
    slot2: int,
) -> tuple[int, Counter[tuple[int, int, int, int]]]:
    if slot1 == slot2:
        return 0, Counter()
    pair1 = assigned[component][slot1]
    pair2 = assigned[component][slot2]
    if pair1 == pair2:
        return 0, Counter()
    changes: Counter[tuple[int, int, int, int]] = Counter()
    for other in range(3):
        if other == component:
            continue
        other1 = assigned[other][slot1]
        other2 = assigned[other][slot2]
        for left in pair1:
            for right in other1:
                changes[cross_key(component, other, left, right)] -= 1
        for left in pair2:
            for right in other2:
                changes[cross_key(component, other, left, right)] -= 1
        for left in pair2:
            for right in other1:
                changes[cross_key(component, other, left, right)] += 1
        for left in pair1:
            for right in other2:
                changes[cross_key(component, other, left, right)] += 1
    delta = 0
    for key, change in changes.items():
        old = counts[key]
        _, _, left, right = key
        target = cross_target(left, right)
        delta += (old + change - target) ** 2 - (old - target) ** 2
    return delta, changes


def duplicate_count(assigned: Sequence[Sequence[tuple[int, int]]]) -> int:
    columns = [
        tuple(
            sorted(
                (
                    *assigned[0][slot],
                    *assigned[1][slot],
                    *assigned[2][slot],
                )
            )
        )
        for slot in range(60)
    ]
    return len(columns) - len(set(columns))


def search(
    type_triple: Sequence[int],
    seed: int,
    restarts: int,
    steps: int,
    x_aaa: int,
) -> dict[str, object]:
    CHECK.require_memory()
    census = CHECK.component_census()
    types = census["types"]
    adjacency = CHECK.union_core([types[index] for index in type_triple])
    local_pairs = local_pair_multisets(adjacency)
    slots, by_component = build_slots(x_aaa)
    rng = random.Random(seed)
    best_score: int | None = None
    best_assigned: list[list[tuple[int, int]]] | None = None
    accepted = 0
    improving = 0
    start = time.perf_counter()

    group_choices = [
        (component, category, tuple(indices))
        for component in range(3)
        for category, indices in by_component[component].items()
    ]
    for restart in range(restarts):
        CHECK.require_memory()
        assigned = initialize(rng, local_pairs, by_component)
        counts = build_cross_counts(assigned)
        score = full_score(counts)
        if best_score is None or score < best_score:
            best_score = score
            best_assigned = [row[:] for row in assigned]
        stagnation = 0
        for step in range(steps):
            component, _category, indices = rng.choice(group_choices)
            slot1, slot2 = rng.sample(indices, 2)
            delta, changes = swap_delta(
                assigned, counts, component, slot1, slot2
            )
            progress = step / max(1, steps - 1)
            temperature = max(0.03, 2.5 * (1.0 - progress) ** 2)
            take = delta <= 0 or rng.random() < math.exp(-delta / temperature)
            if take:
                assigned[component][slot1], assigned[component][slot2] = (
                    assigned[component][slot2],
                    assigned[component][slot1],
                )
                counts.update(changes)
                score += delta
                accepted += 1
                if delta < 0:
                    improving += 1
                    stagnation = 0
                else:
                    stagnation += 1
            else:
                stagnation += 1
            if score < best_score:
                best_score = score
                best_assigned = [row[:] for row in assigned]
            if score == 0 and duplicate_count(assigned) == 0:
                masks = [
                    sum(
                        1 << vertex
                        for vertex in (
                            *assigned[0][slot],
                            *assigned[1][slot],
                            *assigned[2][slot],
                        )
                    )
                    for slot in range(60)
                ]
                all_candidates, _ = CHECK.candidate_columns(
                    adjacency, CHECK.gram_target(adjacency)
                )
                candidate_index = {
                    mask: index for index, mask in enumerate(all_candidates)
                }
                selected = [candidate_index[mask] for mask in masks]
                design = CHECK.verify_design(
                    adjacency, all_candidates, selected
                )
                return {
                    "status": "SAT",
                    "claim_label": "CANDIDATE",
                    "type_triple": list(type_triple),
                    "slot_pattern_parameter_x_AAA": x_aaa,
                    "seed": seed,
                    "restart": restart,
                    "step": step,
                    "elapsed_seconds": time.perf_counter() - start,
                    "best_squared_error": 0,
                    "duplicate_columns": 0,
                    "accepted_swaps": accepted,
                    "improving_swaps": improving,
                    "design": design,
                }
            if stagnation > 20000:
                break

    if best_assigned is None or best_score is None:
        raise AssertionError("search did not initialize")
    return {
        "status": "UNKNOWN",
        "claim_label": "UNKNOWN",
        "type_triple": list(type_triple),
        "slot_pattern_parameter_x_AAA": x_aaa,
        "seed": seed,
        "restarts": restarts,
        "steps_per_restart": steps,
        "elapsed_seconds": time.perf_counter() - start,
        "best_squared_error": best_score,
        "best_duplicate_columns": duplicate_count(best_assigned),
        "accepted_swaps": accepted,
        "improving_swaps": improving,
        "limitations": (
            "heuristic local search; a null result is not nonexistence evidence"
        ),
    }


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type-triple", type=int, nargs=3, required=True)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--restarts", type=int, default=20)
    parser.add_argument("--steps", type=int, default=500_000)
    parser.add_argument("--x-aaa", type=int, choices=(0, 6, 12), default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = search(
        args.type_triple, args.seed, args.restarts, args.steps, args.x_aaa
    )
    payload = canonical_bytes(result)
    if args.output:
        args.output.write_bytes(payload)
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
