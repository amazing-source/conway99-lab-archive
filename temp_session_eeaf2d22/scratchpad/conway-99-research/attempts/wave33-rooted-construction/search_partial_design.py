#!/usr/bin/env python3
"""Deterministic bounded search for a hostile active-to-Z partial object.

The search never decides graph existence.  It permutes one explicit simple
2-(15,3,2) design over the 70 labeled active vertices.  Parallel classes make
the seven P-side support groups exact; fixed-budget annealing tries to reduce
the remaining R-side balance defect.  The explicit result is accepted only
after ``exact_check.py`` independently checks it.
"""

from __future__ import annotations

import argparse
import math
import random
from itertools import combinations
from pathlib import Path

import exact_check as exact


SECOND_STS_PERMUTATION = (
    5, 4, 0, 9, 12, 3, 13, 6, 1, 2, 14, 7, 8, 10, 11
)


def parallel_classes(
    blocks: list[tuple[int, int, int]],
) -> list[tuple[int, ...]]:
    result = []
    for candidate in combinations(range(35), 5):
        covered = {
            point for block_index in candidate for point in blocks[block_index]
        }
        if len(covered) == 15:
            result.append(candidate)
    if len(result) != 56:
        raise AssertionError("unexpected parallel-class census")
    return result


def resolutions(classes: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    by_block = {block: [] for block in range(35)}
    class_sets = [set(candidate) for candidate in classes]
    for class_index, candidate in enumerate(classes):
        for block in candidate:
            by_block[block].append(class_index)

    found: list[tuple[int, ...]] = []

    def visit(unused: set[int], chosen: list[int]) -> None:
        if not unused:
            found.append(tuple(chosen))
            return
        pivot = min(
            unused,
            key=lambda block: sum(
                class_sets[index] <= unused for index in by_block[block]
            ),
        )
        for class_index in by_block[pivot]:
            candidate = class_sets[class_index]
            if candidate <= unused:
                visit(unused - candidate, chosen + [class_index])

    visit(set(range(35)), [])
    if len(found) != 240:
        raise AssertionError("unexpected resolution census")
    return found


def search(
    restarts: int,
    steps: int,
    seed: int,
) -> tuple[list[int], dict[str, object]]:
    model = exact.build_model()
    first_blocks = exact.cyclic_sts15()
    second_blocks = sorted(
        tuple(sorted(SECOND_STS_PERMUTATION[point] for point in block))
        for block in first_blocks
    )
    first_classes = parallel_classes(first_blocks)
    second_classes = parallel_classes(second_blocks)
    first_resolutions = resolutions(first_classes)
    second_resolutions = resolutions(second_classes)
    design = exact.simple_twofold_triple_design()
    design_index = {block: index for index, block in enumerate(design)}
    p_groups = model["support_groups"][:7]
    r_of_active = [
        model["endpoints"][name][1] - 7 for name in model["active"]
    ]

    rng = random.Random(seed)
    best_energy: int | None = None
    best_assignment: list[int] | None = None
    best_restart = -1
    best_step = -1
    completed_restarts = 0

    for restart in range(restarts):
        first_resolution = list(
            first_resolutions[rng.randrange(len(first_resolutions))]
        )
        second_resolution = list(
            second_resolutions[rng.randrange(len(second_resolutions))]
        )
        rng.shuffle(first_resolution)
        rng.shuffle(second_resolution)

        packets: list[list[int]] = []
        for p in range(7):
            packet = [
                design_index[first_blocks[index]]
                for index in first_classes[first_resolution[p]]
            ] + [
                design_index[second_blocks[index]]
                for index in second_classes[second_resolution[p]]
            ]
            rng.shuffle(packet)
            packets.append(packet)

        chosen: list[int | None] = [None] * 70
        for p in range(7):
            positions = list(p_groups[p])
            rng.shuffle(positions)
            for vertex, block_index in zip(positions, packets[p]):
                chosen[vertex] = block_index
        if any(value is None for value in chosen):
            raise AssertionError("incomplete initial assignment")
        assignment = [int(value) for value in chosen]

        counts = [[0] * 15 for _ in range(7)]
        for vertex, block_index in enumerate(assignment):
            r = r_of_active[vertex]
            for zero in design[block_index]:
                counts[r][zero] += 1

        energy = sum(
            (count - 2) ** 2 for row in counts for count in row
        )
        if best_energy is None or energy < best_energy:
            best_energy = energy
            best_assignment = list(assignment)
            best_restart = restart
            best_step = -1

        for step in range(steps):
            p = rng.randrange(7)
            left, right = rng.sample(p_groups[p], 2)
            left_r = r_of_active[left]
            right_r = r_of_active[right]
            if left_r == right_r:
                continue

            left_block = design[assignment[left]]
            right_block = design[assignment[right]]
            old_local = sum(
                (counts[r][zero] - 2) ** 2
                for r in (left_r, right_r)
                for zero in range(15)
            )
            for zero in left_block:
                counts[left_r][zero] -= 1
                counts[right_r][zero] += 1
            for zero in right_block:
                counts[right_r][zero] -= 1
                counts[left_r][zero] += 1
            new_local = sum(
                (counts[r][zero] - 2) ** 2
                for r in (left_r, right_r)
                for zero in range(15)
            )
            delta = new_local - old_local
            temperature = max(0.02, 5.0 * (1.0 - step / steps))
            if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                assignment[left], assignment[right] = (
                    assignment[right], assignment[left]
                )
                energy += delta
            else:
                for zero in right_block:
                    counts[left_r][zero] -= 1
                    counts[right_r][zero] += 1
                for zero in left_block:
                    counts[right_r][zero] -= 1
                    counts[left_r][zero] += 1

            if best_energy is None or energy < best_energy:
                best_energy = energy
                best_assignment = list(assignment)
                best_restart = restart
                best_step = step
            if energy == 0:
                completed_restarts = restart + 1
                break
        else:
            completed_restarts = restart + 1
            continue
        break

    if best_assignment is None or best_energy is None:
        raise AssertionError("bounded search failed to retain a partial object")
    return best_assignment, {
        "method": (
            "fixed-budget seeded annealing within P-balanced parallel-class "
            "packets"
        ),
        "seed": seed,
        "requested_restarts": restarts,
        "completed_restarts": completed_restarts,
        "steps_per_restart": steps,
        "best_r_side_squared_defect": best_energy,
        "best_restart_zero_based": best_restart,
        "best_step_zero_based": best_step,
        "complete_search": False,
        "nonhit_has_negative_status": False,
        "status_is_certificate": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--restarts", type=int, default=9)
    parser.add_argument("--steps", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=3301)
    args = parser.parse_args()

    assignment, metadata = search(args.restarts, args.steps, args.seed)
    certificate = exact.partial_design_certificate(assignment, metadata)
    exact.verify_partial_design_certificate(certificate)
    args.output.write_bytes(exact.canonical_json(certificate))


if __name__ == "__main__":
    main()
