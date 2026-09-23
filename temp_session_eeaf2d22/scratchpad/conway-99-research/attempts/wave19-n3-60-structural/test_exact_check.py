#!/usr/bin/env python3
"""Focused standard-library tests for the Wave 19 exact checker."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave19_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class ExactCheckTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        self.assertEqual(CHECK.check_frozen_inputs(), CHECK.EXPECTED_INPUTS)

    def test_thirteen_q_profiles(self) -> None:
        profiles = CHECK.admissible_profiles()
        self.assertEqual(len(profiles), 13)
        self.assertEqual(
            [len(profile) for profile in profiles],
            [14, 15, 16, 17, 17, 17, 17, 18, 18, 18, 19, 19, 20],
        )
        self.assertTrue(all(sum(profile) == 40 for profile in profiles))
        self.assertTrue(all(min(CHECK.d_k(profile)) >= 4 for profile in profiles))

    def test_crossing_enumeration_and_global_H_guard(self) -> None:
        self.assertEqual(CHECK.crossing_edge_counts(2, 1), (0,))
        self.assertEqual(CHECK.crossing_edge_counts(2, 3), (0, 4))
        self.assertEqual(CHECK.crossing_edge_counts(3, 1), (0,))
        self.assertEqual(CHECK.crossing_edge_counts(4, 2), (0, 4))
        self.assertEqual(CHECK.crossing_edge_counts(3, 3), (0, 4, 6))

    def test_q4_pair_table(self) -> None:
        expected = {
            (2, 2): 2, (2, 3): None, (2, 4): 3,
            (3, 3): 3, (3, 4): None, (4, 4): 4,
        }
        self.assertEqual(
            {pair: CHECK.size_two_support_count(*pair) for pair in expected},
            expected,
        )

    def test_r20_point_size_profiles(self) -> None:
        profiles27 = CHECK.point_size_profiles(60, 27)
        self.assertEqual(len(profiles27), 11)
        self.assertEqual(
            tuple(profile for profile in profiles27 if max(profile) <= 3),
            ((2,) * 21 + (3,) * 6,),
        )
        self.assertEqual(
            CHECK.point_size_profiles(60, 29),
            ((2,) * 28 + (4,), (2,) * 27 + (3, 3)),
        )
        self.assertEqual(CHECK.point_size_profiles(60, 30), ((2,) * 30,))

    def test_m27_exact_equality_and_cubic_dichotomy(self) -> None:
        moments = CHECK.outside_moments(27, [0] * 27)
        self.assertEqual(moments["sum"], 216)
        self.assertEqual(moments["sum_squares"], 648)
        self.assertEqual(CHECK.minimum_integer_square_sum(72, 216), 648)
        forms = CHECK.cubic_six_vertex_forms()
        self.assertEqual(set(forms), {"K3,3", "triangular_prism"})
        self.assertEqual(
            {name: len(CHECK.graph_triangles(matrix)) for name, matrix in forms.items()},
            {"K3,3": 0, "triangular_prism": 2},
        )
        self.assertEqual(len(CHECK.cycle_partitions(21)), 60)

    def test_m28_dense_four_vertex_graphs(self) -> None:
        self.assertEqual(
            CHECK.maximum_even_integer_at_most(CHECK.spectral_upper_degree_sum(28)),
            170,
        )
        self.assertTrue(CHECK.dense_four_vertex_graphs_force_overlapping_triangles())

    def test_m29_integer_second_moments(self) -> None:
        size4 = CHECK.outside_moments(29, [6] + [0] * 28)
        self.assertEqual((size4["sum"], size4["sum_squares"]), (226, 698))
        self.assertEqual(CHECK.minimum_integer_square_sum(70, 226), 742)
        self.assertLess(698, 742)
        self.assertLess(752, CHECK.minimum_integer_square_sum(70, 228))
        self.assertLess(724, CHECK.minimum_integer_square_sum(70, 226))

    def test_m30_moment_reduction(self) -> None:
        self.assertEqual(CHECK.spectral_upper_degree_sum(30), Fraction(190, 1))
        self.assertLess(788, CHECK.minimum_integer_square_sum(69, 232))
        self.assertLess(760, CHECK.minimum_integer_square_sum(69, 230))

    def test_m30_topologies_and_outside_profiles(self) -> None:
        cases = CHECK.z_topologies()
        self.assertEqual(
            {case["name"]: case["outside_degree_multiset_count"] for case in cases},
            {
                "empty": 1297,
                "K2": 354,
                "2K2": 69,
                "P3": 52,
                "3K2": 6,
                "P3_plus_K2": 3,
                "P4": 2,
                "K1,3": 1,
                "K3": 1,
            },
        )
        self.assertEqual(len(CHECK.cycle_partitions(30)), 331)

    def test_status_remains_unknown(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(
            result["status_boundary"]["conditional_n3_60"],
            "UNKNOWN_FINITE_RESIDUAL",
        )
        self.assertEqual(result["status_boundary"]["conway_99_target"], "UNKNOWN")
        self.assertEqual(result["status_boundary"]["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
