#!/usr/bin/env python3
"""Exact coverage tests for the legacy and N3-joint matching branches."""

from __future__ import annotations

import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

from matching_orbits import (
    canonical_branch_decisions,
    canonical_matching,
    integer_partitions,
    matching_type,
    main as matching_main,
    n3_joint_branch_decisions,
    n3_joint_matching_orbits,
    n3_joint_summary,
    n3_oriented_stabilizer_generators,
    n3_refined_branch_specification,
    n3_refined_orbits,
    n3_refined_summary,
    n3_unit_stabilizer_generators,
    orbit_sizes_via_generators,
    orbit_type_counts,
)
from root_model import RootModel


EXPECTED_COUNTS = {
    (6,): 3840,
    (5, 1): 2304,
    (4, 2): 1440,
    (4, 1, 1): 720,
    (3, 3): 640,
    (3, 2, 1): 960,
    (3, 1, 1, 1): 160,
    (2, 2, 2): 120,
    (2, 2, 1, 1): 180,
    (2, 1, 1, 1, 1): 30,
    (1, 1, 1, 1, 1, 1): 1,
}

EXPECTED_N3_ORBITS = (
    (((0, 4), (1, 5), (6, 7), (8, 9), (10, 11), (12, 13)), 1),
    (((0, 4), (1, 5), (6, 7), (8, 9), (10, 12), (11, 13)), 12),
    (((0, 4), (1, 5), (6, 7), (8, 10), (9, 12), (11, 13)), 32),
    (((0, 4), (1, 5), (6, 8), (7, 9), (10, 12), (11, 13)), 12),
    (((0, 4), (1, 5), (6, 8), (7, 10), (9, 12), (11, 13)), 48),
    (((0, 4), (1, 6), (5, 7), (8, 9), (10, 11), (12, 13)), 8),
    (((0, 4), (1, 6), (5, 7), (8, 9), (10, 12), (11, 13)), 48),
    (((0, 4), (1, 6), (5, 7), (8, 10), (9, 12), (11, 13)), 64),
    (((0, 4), (1, 6), (5, 8), (7, 9), (10, 11), (12, 13)), 48),
    (((0, 4), (1, 6), (5, 8), (7, 9), (10, 12), (11, 13)), 96),
    (((0, 4), (1, 6), (5, 8), (7, 10), (9, 11), (12, 13)), 192),
    (((0, 4), (1, 6), (5, 8), (7, 10), (9, 12), (11, 13)), 384),
)

EXPECTED_REFINED_ENDPOINTS = (
    (0, 1, 3, 6),
    (0, 1, 3, 6, 10),
    (0, 1, 3, 6, 8),
    (0, 1, 3, 6),
    (0, 1, 3, 6),
    (0, 1, 3, 6, 7, 8),
    (0, 1, 3, 6, 7, 8, 10),
    (0, 1, 3, 6, 7, 8),
    (0, 1, 3, 6, 7, 8, 9, 10),
    (0, 1, 3, 6, 7, 8, 9, 10),
    (0, 1, 3, 6, 7, 8, 9, 10, 11, 12),
    (0, 1, 3, 6, 7, 8, 9, 10, 11, 12, 13),
)

EXPECTED_REFINED_ORBIT_SIZES = (
    (1, 1, 1, 8),
    (12, 12, 12, 48, 48),
    (32, 32, 32, 64, 192),
    (12, 12, 12, 96),
    (48, 48, 48, 384),
    (8, 8, 8, 8, 8, 48),
    (48, 48, 48, 48, 48, 96, 192),
    (64, 64, 64, 64, 64, 384),
    (48, 48, 48, 48, 48, 48, 48, 192),
    (96, 96, 96, 96, 96, 96, 96, 384),
    (192, 192, 192, 192, 192, 192, 192, 192, 192, 384),
    (384,) * 11,
)


class MatchingOrbitTests(unittest.TestCase):
    def test_partitions_of_six_have_eleven_types(self) -> None:
        partitions = list(integer_partitions(6))
        self.assertEqual(len(partitions), 11)
        self.assertEqual(set(partitions), set(EXPECTED_COUNTS))

    def test_exhaustive_labeled_matching_counts(self) -> None:
        counts = orbit_type_counts(6)
        self.assertEqual(dict(counts), EXPECTED_COUNTS)
        self.assertEqual(sum(counts.values()), 10395)

    def test_generators_give_exactly_the_same_eleven_orbits(self) -> None:
        self.assertEqual(orbit_sizes_via_generators(6), EXPECTED_COUNTS)

    def test_each_canonical_representative_has_requested_type(self) -> None:
        for partition in EXPECTED_COUNTS:
            self.assertEqual(matching_type(canonical_matching(partition), 6), partition)

    def test_branch_fixes_one_perfect_matching_and_all_nonmatching_edges(self) -> None:
        root = RootModel.build(7)
        for partition in EXPECTED_COUNTS:
            with self.subTest(partition=partition):
                decisions = canonical_branch_decisions(root, 0, partition)
                self.assertEqual(len(decisions), 66)
                self.assertEqual(sum(decisions.values()), 6)
                fiber = set(root.containing(0))
                degrees = {vertex: 0 for vertex in fiber}
                for (first, second), present in decisions.items():
                    self.assertIn(first, fiber)
                    self.assertIn(second, fiber)
                    if present:
                        degrees[first] += 1
                        degrees[second] += 1
                self.assertEqual(set(degrees.values()), {1})

    def test_n3_unit_stabilizer_generators_have_order_768(self) -> None:
        generators = n3_unit_stabilizer_generators()
        self.assertEqual(len(generators), 8)
        identity = tuple(range(14))
        group = {identity}
        frontier = [identity]
        unit = {frozenset((0, 2)), frozenset((2, 4))}
        while frontier:
            current = frontier.pop()
            for generator in generators:
                image = tuple(generator[value] for value in current)
                if image not in group:
                    group.add(image)
                    frontier.append(image)
        self.assertEqual(len(group), 768)
        for permutation in group:
            self.assertEqual(sorted(permutation), list(range(14)))
            self.assertTrue(
                all(
                    permutation[coordinate ^ 1] == (permutation[coordinate] ^ 1)
                    for coordinate in range(14)
                )
            )
            image_unit = {
                frozenset(permutation[coordinate] for coordinate in label)
                for label in unit
            }
            self.assertEqual(image_unit, unit)

    def test_n3_joint_matching_orbits_are_the_expected_complete_cover(self) -> None:
        self.assertEqual(n3_joint_matching_orbits(), EXPECTED_N3_ORBITS)
        self.assertEqual(sum(size for _, size in EXPECTED_N3_ORBITS), 945)
        summary = n3_joint_summary()
        self.assertEqual(summary["orbit_count"], 12)
        self.assertEqual(summary["matching_count"], 945)
        self.assertEqual(summary["branch_coordinate"], 2)
        self.assertEqual(summary["fixed_endpoint_edge"], [0, 4])

    def test_each_n3_joint_branch_fixes_a_full_matching_on_shared_fiber(self) -> None:
        root = RootModel.build(7)
        indices = root.label_index()
        fixed_edge = tuple(sorted((indices[(0, 2)], indices[(2, 4)])))
        for branch_number in range(1, 13):
            with self.subTest(branch_number=branch_number):
                decisions = n3_joint_branch_decisions(root, branch_number)
                self.assertEqual(len(decisions), 66)
                self.assertEqual(sum(decisions.values()), 6)
                self.assertTrue(decisions[fixed_edge])
                fiber = set(root.containing(2))
                degrees = {vertex: 0 for vertex in fiber}
                for (first, second), present in decisions.items():
                    self.assertIn(first, fiber)
                    self.assertIn(second, fiber)
                    if present:
                        degrees[first] += 1
                        degrees[second] += 1
                self.assertEqual(set(degrees.values()), {1})

    def test_n3_joint_branch_rejects_wrong_scaffold_and_index(self) -> None:
        with self.assertRaisesRegex(ValueError, "only to pair_count 7"):
            n3_joint_branch_decisions(RootModel.build(3), 1)
        root = RootModel.build(7)
        for branch_number in (True, 0, 13):
            with self.subTest(branch_number=branch_number):
                with self.assertRaisesRegex(ValueError, "branch number"):
                    n3_joint_branch_decisions(root, branch_number)

    def test_n3_joint_cli_rejects_an_explicit_wrong_pair_count(self) -> None:
        with self.assertRaisesRegex(SystemExit, "only to --pair-count 7"):
            matching_main(["--n3-joint", "--pair-count", "3"])
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(matching_main(["--n3-joint"]), 0)
        self.assertEqual(json.loads(output.getvalue())["pair_count"], 7)

    def test_n3_oriented_stabilizer_and_refined_cover(self) -> None:
        generators = n3_oriented_stabilizer_generators()
        identity = tuple(range(14))
        group = {identity}
        frontier = [identity]
        while frontier:
            current = frontier.pop()
            for generator in generators:
                image = tuple(generator[value] for value in current)
                if image not in group:
                    group.add(image)
                    frontier.append(image)
        self.assertEqual(len(group), 384)
        self.assertTrue(all(permutation[:6] == identity[:6] for permutation in group))

        refined = n3_refined_orbits()
        self.assertEqual(len(refined), 78)
        self.assertEqual(sum(size for _, _, size in refined), 10_395)
        grouped_endpoints: list[tuple[int, ...]] = []
        grouped_sizes: list[tuple[int, ...]] = []
        for matching, _ in EXPECTED_N3_ORBITS:
            entries = [entry for entry in refined if entry[0] == matching]
            grouped_endpoints.append(tuple(endpoint for _, endpoint, _ in entries))
            grouped_sizes.append(tuple(size for _, _, size in entries))
        self.assertEqual(tuple(grouped_endpoints), EXPECTED_REFINED_ENDPOINTS)
        self.assertEqual(tuple(grouped_sizes), EXPECTED_REFINED_ORBIT_SIZES)

        summary = n3_refined_summary()
        self.assertEqual(summary["stabilizer_order"], 384)
        self.assertEqual(summary["state_count"], 10_395)
        self.assertEqual(summary["orbit_count"], 78)
        self.assertEqual(summary["burnside_fixed_sum"], 29_952)

    def test_refined_branch_specification_and_guards(self) -> None:
        root = RootModel.build(7)
        indices = root.label_index()
        for branch_number, expected_endpoint in ((1, 0), (78, 13)):
            decisions, refinement_edge, first_branch = (
                n3_refined_branch_specification(root, branch_number)
            )
            self.assertEqual(len(decisions), 66)
            self.assertNotIn(refinement_edge, decisions)
            self.assertEqual(
                refinement_edge,
                tuple(
                    sorted(
                        (
                            indices[(0, 2)],
                            indices[tuple(sorted((4, expected_endpoint)))],
                        )
                    )
                ),
            )
            self.assertEqual(first_branch, 1 if branch_number == 1 else 12)

        with self.assertRaisesRegex(ValueError, "only to pair_count 7"):
            n3_refined_branch_specification(RootModel.build(3), 1)
        for branch_number in (True, 0, 79):
            with self.subTest(branch_number=branch_number):
                with self.assertRaisesRegex(ValueError, "branch number"):
                    n3_refined_branch_specification(root, branch_number)

    def test_refined_cli_summary_and_mutual_exclusion(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(matching_main(["--n3-refined"]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["orbit_count"], 78)
        self.assertEqual(report["state_count"], 10_395)
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                matching_main(["--n3-joint", "--n3-refined"])
        with self.assertRaisesRegex(SystemExit, "only to --pair-count 7"):
            matching_main(["--n3-refined", "--pair-count", "3"])


if __name__ == "__main__":
    unittest.main()
