#!/usr/bin/env python3
"""Focused exact tests for the Wave 36 rooted-branch strengthening."""

from __future__ import annotations

import itertools
import unittest

from rooted_branch_scout import (
    COORDINATE_OFFSET,
    FULL_VERTEX_COUNT,
    RESIDUAL_OFFSET,
    add_fixed_triangle_prism_constraints,
    add_endpoint_and_branch,
    branch_coordinate_triangles,
    endpoint_fixed_assignments,
    fixed_triangle_prism_clauses,
    full_edge_state,
    required_positive_variables,
)
from sat_model import EncodedRootModel
from refined_branch_scout import refined_cases


class FullScaffoldTests(unittest.TestCase):
    def setUp(self) -> None:
        self.encoded = EncodedRootModel.build(
            7, variant="compact", cardinality_backend="native"
        )

    def test_full_edge_state_matches_scaffold(self) -> None:
        self.assertTrue(full_edge_state(self.encoded, 0, 1))
        self.assertFalse(full_edge_state(self.encoded, 0, RESIDUAL_OFFSET))
        self.assertTrue(full_edge_state(self.encoded, 1, 2))
        self.assertFalse(full_edge_state(self.encoded, 1, 3))
        label_index = self.encoded.root.label_index()[(0, 2)]
        label_vertex = RESIDUAL_OFFSET + label_index
        self.assertTrue(full_edge_state(self.encoded, 1, label_vertex))
        self.assertTrue(full_edge_state(self.encoded, 3, label_vertex))
        self.assertFalse(full_edge_state(self.encoded, 2, label_vertex))
        other = RESIDUAL_OFFSET + self.encoded.root.label_index()[(0, 4)]
        self.assertIsInstance(full_edge_state(self.encoded, label_vertex, other), int)

    def test_required_edges_skip_fixed_nonedge(self) -> None:
        self.assertIsNone(
            required_positive_variables(self.encoded, ((0, RESIDUAL_OFFSET),))
        )

    def test_every_surviving_branch_has_six_fixed_triangles(self) -> None:
        for branch in (4, 5, 8, 10, 12):
            with self.subTest(branch=branch):
                triangles = branch_coordinate_triangles(self.encoded, branch)
                self.assertEqual(len(triangles), 6)
                self.assertEqual(
                    {triangle[0] for triangle in triangles},
                    {COORDINATE_OFFSET + 2},
                )
                self.assertEqual(len(set(triangles)), 6)
                assignments = endpoint_fixed_assignments(self.encoded, branch)
                self.assertTrue(assignments)

    def test_add_endpoint_and_branch_has_expected_units(self) -> None:
        add_endpoint_and_branch(self.encoded, 4)
        units = [clause[0] for clause in self.encoded.cnf.clauses if len(clause) == 1]
        self.assertEqual(len(units), 150)
        # Six branch-fixed negative fiber edges duplicate endpoint units.
        self.assertEqual(len(set(units)), 144)

    def test_refined_cover_has_exact_endpoint_case_ids(self) -> None:
        expected = {
            4: (15, 16, 17, 18),
            5: (19, 20, 21, 22),
            8: (36, 37, 38, 39, 40, 41),
            10: (50, 51, 52, 53, 54, 55, 56, 57),
            12: (68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78),
        }
        all_ids = []
        for parent, expected_ids in expected.items():
            cases = refined_cases(self.encoded, parent)
            actual = tuple(case[0] for case in cases)
            self.assertEqual(actual, expected_ids)
            self.assertEqual(len({case[1] for case in cases}), len(cases))
            all_ids.extend(actual)
        self.assertEqual(len(all_ids), 33)

    def test_all_five_clause_catalogs_are_deterministic(self) -> None:
        expected = {
            4: "f675391a81dd817fe45f805a9bc9309dba02910988b42988238b66e6c2f5ae2e",
            5: "1215e64d0b8ebd5c898278acdd828cb657d8f1a1485fba4893e34316d94edaf5",
            8: "bb9aac4e06e0d5f9b885aa0705b31d576d8cca7221075cfab938ce70f5716a53",
            10: "eedd27d0322694661a4142a54fca80c95e416b09b2d59d6b21cf74beb4ef2af5",
            12: "ac1aea55f24f3fd23045daa2195cadbd8c2a799b3a27f4755e1ad99290f238d7",
        }
        for branch, digest in expected.items():
            with self.subTest(branch=branch):
                encoded = EncodedRootModel.build(
                    7, variant="compact", cardinality_backend="native"
                )
                add_endpoint_and_branch(encoded, branch)
                result = add_fixed_triangle_prism_constraints(encoded, branch)
                self.assertEqual(result["fixed_triangle_count"], 6)
                self.assertEqual(
                    result["deduplicated_active_clause_count"], 282_774
                )
                self.assertEqual(
                    result["clause_length_histogram"],
                    {"3": 606, "5": 282_168},
                )
                self.assertEqual(result["clause_catalog_sha256"], digest)


class PrismClauseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.encoded = EncodedRootModel.build(
            7, variant="compact", cardinality_backend="native"
        )

    def test_clauses_are_negative_and_nonempty(self) -> None:
        triangle = branch_coordinate_triangles(self.encoded, 4)[0]
        clauses = fixed_triangle_prism_clauses(self.encoded, triangle)
        self.assertTrue(clauses)
        self.assertTrue(all(clause for clause in clauses))
        self.assertTrue(all(literal < 0 for clause in clauses for literal in clause))
        self.assertEqual(len(clauses), len(set(clauses)))

    def test_each_generated_clause_describes_six_possible_edges(self) -> None:
        triangle = branch_coordinate_triangles(self.encoded, 4)[0]
        clauses = set(fixed_triangle_prism_clauses(self.encoded, triangle))
        excluded = set(triangle)
        # Exhaustively reconstruct a small deterministic prefix of assignments
        # and ensure every feasible six-edge pattern has its blocking clause.
        checked = 0
        for matched in itertools.permutations(
            [vertex for vertex in range(FULL_VERTEX_COUNT) if vertex not in excluded],
            3,
        ):
            required = (
                (triangle[0], matched[0]),
                (triangle[1], matched[1]),
                (triangle[2], matched[2]),
                (matched[0], matched[1]),
                (matched[0], matched[2]),
                (matched[1], matched[2]),
            )
            variables = required_positive_variables(self.encoded, required)
            if variables:
                self.assertIn(tuple(-variable for variable in variables), clauses)
                checked += 1
                if checked == 100:
                    break
        self.assertEqual(checked, 100)


if __name__ == "__main__":
    unittest.main()
