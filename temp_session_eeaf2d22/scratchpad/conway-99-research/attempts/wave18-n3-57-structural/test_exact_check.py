#!/usr/bin/env python3
"""Focused tests for the Wave 18 n3=57 arithmetic checker."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave18_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class ExactCheckTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        self.assertEqual(CHECK.check_frozen_inputs(), CHECK.EXPECTED_INPUTS)

    def test_nine_profiles_and_q4_boundary(self) -> None:
        profiles = CHECK.admissible_profiles()
        self.assertEqual(len(profiles), 9)
        self.assertEqual([len(profile) for profile in profiles],
                         [14, 15, 16, 17, 17, 17, 18, 18, 19])
        self.assertEqual(max(max(profile) for profile in profiles), 4)

    def test_degree_filter_is_exact(self) -> None:
        for profile in CHECK.admissible_profiles():
            self.assertEqual(sum(profile), 38)
            self.assertGreaterEqual(min(CHECK.d_k(profile)), 4)
        hostile = (2,) * 12 + (3,) * 2
        self.assertEqual(sum(hostile), 30)
        self.assertNotIn(hostile, CHECK.admissible_profiles())

    def test_overlap_deleted_crossings(self) -> None:
        self.assertEqual(CHECK.crossing_edge_counts(1, 2), (0,))
        self.assertEqual(CHECK.crossing_edge_counts(2, 1), (0,))
        self.assertEqual(CHECK.crossing_edge_counts(2, 2), (0, 4))
        self.assertEqual(CHECK.crossing_edge_counts(3, 2), (0, 4))

    def test_no_unsupported_global_H_degree(self) -> None:
        self.assertEqual(CHECK.crossing_edge_counts(3, 3), (0, 4, 6))

    def test_all_size_two_q_pairs_through_q4(self) -> None:
        expected = {
            (2, 2): 2,
            (2, 3): None,
            (2, 4): 3,
            (3, 3): 3,
            (3, 4): None,
            (4, 4): 4,
        }
        self.assertEqual(
            {pair: CHECK.size_two_support_count(*pair) for pair in expected},
            expected,
        )

    def test_r18_equality_case(self) -> None:
        self.assertEqual(CHECK.point_size_profiles(54, 27), ((2,) * 27,))
        self.assertEqual(CHECK.spectral_upper_degree_sum(27), 162)
        self.assertEqual(4 + CHECK.size_two_support_count(2, 4), 7)

    def test_r19_point_profiles(self) -> None:
        self.assertEqual(
            CHECK.point_size_profiles(57, 27),
            (
                (2,) * 26 + (5,),
                (2,) * 25 + (3, 4),
                (2,) * 24 + (3, 3, 3),
            ),
        )
        self.assertEqual(
            CHECK.point_size_profiles(57, 28),
            ((2,) * 27 + (3,),),
        )

    def test_m28_even_degree_sum_bound(self) -> None:
        self.assertEqual(CHECK.spectral_upper_degree_sum(28), Fraction(1540, 9))
        self.assertEqual(
            CHECK.maximum_even_integer_at_most(CHECK.spectral_upper_degree_sum(28)),
            170,
        )
        self.assertGreater(172, 170)

    def test_full_result_status_boundary(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(
            result["status_boundary"]["conditional_n3_57"],
            "EXCLUDED_DERIVED_NOT_INDEPENDENTLY_VERIFIED",
        )
        self.assertEqual(result["status_boundary"]["conway_99_target"], "UNKNOWN")
        self.assertEqual(result["status_boundary"]["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
