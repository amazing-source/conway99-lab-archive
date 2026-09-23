#!/usr/bin/env python3
"""Hostile tests for the Wave 40 equality-regime discovery package."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave40_rank19", HERE / "exact_check.py")
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class EqualityRegimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = CHECK.exact_record()

    def test_frozen_inputs(self) -> None:
        CHECK.verify_frozen_inputs()

    def test_local_ranks_and_nullities(self) -> None:
        blocks = self.record["local_blocks"]
        self.assertEqual((blocks["2+2+2"]["rank_F7"], blocks["2+2+2"]["nullity_F7"]), (19, 8))
        self.assertEqual((blocks["2+4"]["rank_F7"], blocks["2+4"]["nullity_F7"]), (21, 6))

    def test_complete_pattern_universe(self) -> None:
        self.assertEqual(len(CHECK.outside_patterns(1)), 144)
        self.assertEqual(len(CHECK.outside_patterns(0)), 4_356)
        for pattern in CHECK.outside_patterns(1):
            self.assertEqual(len(pattern["X_indices"]), 1)
            self.assertEqual(len(pattern["Y_indices"]), 1)
        for pattern in CHECK.outside_patterns(0):
            self.assertEqual(len(pattern["X_indices"]), 2)
            self.assertEqual(len(pattern["Y_indices"]), 2)

    def test_omitting_z_patterns_is_detected(self) -> None:
        incomplete = CHECK.outside_patterns(0)
        self.assertEqual(len(incomplete), 4_356)
        self.assertNotEqual(
            len(incomplete),
            self.record["local_blocks"]["2+2+2"]["combined_outside_pattern_count"],
        )
        mutated = copy.deepcopy(self.record)
        mutated["local_blocks"]["2+2+2"]["z_neighbor_pattern_count"] = 0
        with self.assertRaises(AssertionError):
            CHECK.validate_record(mutated)

    def test_affine_K_column_is_not_adjacency_indicator(self) -> None:
        pattern = CHECK.outside_patterns(1)[0]
        correct = CHECK.affine_k_column(pattern)
        wrong = CHECK.adjacency_indicator_column(pattern)
        self.assertEqual(set(correct), {1, 6})
        self.assertEqual(set(wrong), {0, 1})
        self.assertNotEqual(correct, wrong)
        block = self.record["local_blocks"]["2+2+2"]
        self.assertNotEqual(
            block["wrong_adjacency_indicator_survivor_count"],
            block["columns_in_local_column_space"],
        )

    def test_rank_19_column_space_census(self) -> None:
        block = self.record["local_blocks"]["2+2+2"]
        self.assertEqual(block["combined_outside_pattern_count"], 4_500)
        self.assertEqual(block["non_z_patterns_passing_visible_lambda_cap"], 4_116)
        self.assertEqual(block["columns_in_local_column_space"], 36)
        self.assertEqual(block["column_space_survivors_by_z_flag"], {"0": 36})
        self.assertEqual(block["z_neighbor_columns_in_local_column_space"], 0)

    def test_rank_20_projective_line_boundary(self) -> None:
        census = self.record["local_blocks"]["2+2+2"]["quotient_census_for_z_neighbors"]
        self.assertEqual(census["projective_line_count"], 66)
        self.assertEqual(census["line_pattern_multiplicity_distribution"], {"2": 60, "4": 6})
        self.assertEqual(census["maximum_patterns_on_one_line"], 4)

    def test_rank_21_two_space_boundary(self) -> None:
        census = self.record["local_blocks"]["2+2+2"]["quotient_census_for_z_neighbors"]
        self.assertEqual(census["two_space_count"], 1_923)
        self.assertEqual(
            census["two_space_matching_number_distribution"],
            {"2": 480, "4": 1251, "6": 168, "8": 24},
        )
        self.assertEqual(census["maximum_matching_in_a_two_space"], 8)
        self.assertLess(census["maximum_matching_in_a_two_space"], 12)

    def test_type_24_equality_branch_has_no_z_column(self) -> None:
        block = self.record["local_blocks"]["2+4"]
        self.assertEqual(block["rank_F7"], 21)
        self.assertEqual(block["z_neighbor_pattern_count"], 144)
        self.assertEqual(block["z_neighbor_columns_in_local_column_space"], 0)

    def test_rank_22_positive_control_stops_the_argument(self) -> None:
        control = self.record["local_blocks"]["2+2+2"]["rank_22_positive_control"]
        self.assertEqual(control["three_space_count"], 25_744)
        self.assertEqual(control["three_spaces_supporting_a_perfect_matching"], 32)
        matching = control["canonical_first_witness"]["perfect_matching"]
        self.assertEqual(len(matching), 12)
        self.assertEqual(sorted(left for left, _ in matching), list(range(12)))
        self.assertEqual(sorted(right for _, right in matching), list(range(12)))

    def test_candidate_floor_and_conservative_status(self) -> None:
        theorem = self.record["candidate_theorem"]
        self.assertEqual(theorem["new_conditional_floor"], 22)
        self.assertFalse(theorem["endpoint_excluded"])
        self.assertFalse(theorem["general_upper_bound_improved_below_4158"])
        self.assertEqual(self.record["claim_label"], "CANDIDATE")
        self.assertEqual(self.record["target_status"], "UNKNOWN")
        self.assertEqual(self.record["novelty_status"], "UNKNOWN")

    def test_status_inflation_is_rejected(self) -> None:
        for path, value in (
            (("claim_label",), "VERIFIED"),
            (("candidate_theorem", "endpoint_excluded"), True),
            (("candidate_theorem", "general_upper_bound_improved_below_4158"), True),
            (("target_status",), "SOLVED"),
            (("novelty_status",), "NOVEL"),
        ):
            mutated = copy.deepcopy(self.record)
            target = mutated
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.assertRaises(AssertionError):
                CHECK.validate_record(mutated)

    def test_stored_result_matches_regeneration(self) -> None:
        stored = CHECK.load_json(HERE / "exact-results.json")
        CHECK.validate_record(stored)
        self.assertEqual((HERE / "exact-results.json").read_bytes(), CHECK.canonical_json(self.record))


if __name__ == "__main__":
    unittest.main()
