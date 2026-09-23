#!/usr/bin/env python3
"""Tests for the deterministic rooted residual scaffold."""

from __future__ import annotations

import unittest
from itertools import combinations

from root_model import RootModel


class ConwayRootModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = RootModel.build(7)

    def test_conway_dimensions(self) -> None:
        self.assertEqual(self.model.coordinate_count, 14)
        self.assertEqual(self.model.residual_count, 84)
        self.assertEqual(self.model.residual_degree, 12)
        self.assertEqual(self.model.edge_variable_count, 3486)

    def test_fixed_incidence_identities(self) -> None:
        self.model.validate_fixed_identities()

    def test_each_coordinate_occurs_twelve_times(self) -> None:
        self.assertEqual(
            [len(self.model.containing(coordinate)) for coordinate in range(14)],
            [12] * 14,
        )

    def test_neighbor_incidence_targets_force_degree_twelve(self) -> None:
        for label_index in range(84):
            target_sum = sum(
                self.model.coordinate_neighbor_target(coordinate, label_index)
                for coordinate in range(14)
            )
            self.assertEqual(target_sum // 2, 12)

    def test_common_neighbor_target_table(self) -> None:
        intersecting = next(
            (i, j)
            for i in range(84)
            for j in range(i + 1, 84)
            if set(self.model.labels[i]).intersection(self.model.labels[j])
        )
        disjoint = next(
            (i, j)
            for i in range(84)
            for j in range(i + 1, 84)
            if not set(self.model.labels[i]).intersection(self.model.labels[j])
        )
        self.assertEqual(self.model.common_neighbor_target(*intersecting, True), 0)
        self.assertEqual(self.model.common_neighbor_target(*intersecting, False), 1)
        self.assertEqual(self.model.common_neighbor_target(*disjoint, True), 1)
        self.assertEqual(self.model.common_neighbor_target(*disjoint, False), 2)

    def test_scaffold_generators_are_safe_label_permutations(self) -> None:
        generators = self.model.label_generators()
        self.assertEqual(len(generators), 13)
        for generator in generators:
            self.assertEqual(sorted(generator), list(range(84)))
            for i, image_i in enumerate(generator):
                for j, image_j in enumerate(generator):
                    before = len(set(self.model.labels[i]).intersection(self.model.labels[j]))
                    after = len(
                        set(self.model.labels[image_i]).intersection(
                            self.model.labels[image_j]
                        )
                    )
                    self.assertEqual(before, after)

    def test_pair_count_two_is_small_calibration_scaffold(self) -> None:
        small = RootModel.build(2)
        small.validate_fixed_identities()
        self.assertEqual(small.coordinate_count, 4)
        self.assertEqual(small.residual_count, 4)
        self.assertEqual(small.residual_degree, 2)

    def test_summary_constraint_counts(self) -> None:
        summary = self.model.summary()
        self.assertEqual(summary["residual_edge_count"], 504)
        self.assertEqual(summary["coordinate_incidence_equalities"], 1176)
        self.assertEqual(summary["common_neighbor_equalities"], 3486)
        self.assertEqual(summary["direct_and_auxiliaries"], 285852)
        self.assertEqual(len(summary["sha256"]), 64)

    def test_canonical_n3_edge_has_the_full_safe_scaffold_orbit(self) -> None:
        indices = self.model.label_index()
        canonical = frozenset((indices[(0, 2)], indices[(2, 4)]))
        orbit = {canonical}
        frontier = [canonical]
        generators = self.model.label_generators()
        while frontier:
            pair = frontier.pop()
            for generator in generators:
                image = frozenset(generator[index] for index in pair)
                if image not in orbit:
                    orbit.add(image)
                    frontier.append(image)

        expected = set()
        for first, second in combinations(range(self.model.residual_count), 2):
            left = set(self.model.labels[first])
            right = set(self.model.labels[second])
            if len(left & right) != 1:
                continue
            nonshared = tuple((left ^ right))
            if nonshared[1] != self.model.mate(nonshared[0]):
                expected.add(frozenset((first, second)))

        self.assertEqual(len(orbit), 840)
        self.assertEqual(orbit, expected)

    def test_canonical_n3_induced_table_is_fixed_except_one_edge(self) -> None:
        # Full numbering is root 0, coordinates 1..14, residual labels 15..98.
        indices = self.model.label_index()
        vertices = {
            "x": 0,
            "u": 1,
            "v": 2,
            "a": 3,
            "b": 15 + indices[(0, 2)],
            "c": 15 + indices[(2, 4)],
        }
        self.assertEqual(vertices, {"x": 0, "u": 1, "v": 2, "a": 3, "b": 15, "c": 39})

        fixed_present = {
            ("x", "u"),
            ("x", "v"),
            ("x", "a"),
            ("u", "v"),
            ("u", "b"),
            ("a", "b"),
            ("a", "c"),
        }
        residual_unit = ("b", "c")
        fixed_absent = {
            ("x", "b"),
            ("x", "c"),
            ("u", "a"),
            ("u", "c"),
            ("v", "a"),
            ("v", "b"),
            ("v", "c"),
        }
        all_pairs = {tuple(pair) for pair in combinations(vertices, 2)}
        self.assertEqual(fixed_present | {residual_unit} | fixed_absent, all_pairs)
        self.assertEqual(len(fixed_present), 7)
        self.assertEqual(len(fixed_absent), 7)


if __name__ == "__main__":
    unittest.main()
