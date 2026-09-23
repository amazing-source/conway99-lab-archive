#!/usr/bin/env python3
"""Focused hostile tests for the independent Wave 19 residual checker."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave19_independent", HERE / "independent_residual_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class IndependentResidualTests(unittest.TestCase):
    def test_provenance(self) -> None:
        self.assertEqual(CHECK.authenticate_inputs(), CHECK.PINNED_INPUTS)

    def test_q_profiles_from_multiplicities(self) -> None:
        profiles = CHECK.q_profiles_by_multiplicity()
        self.assertEqual(len(profiles), 13)
        self.assertEqual(
            [len(profile) for profile in profiles],
            [14, 15, 16, 17, 17, 17, 17, 18, 18, 18, 19, 19, 20],
        )
        self.assertTrue(all(sum(profile) == 40 for profile in profiles))
        self.assertTrue(all(
            all(len(profile) - 1 - 3 * q >= 4 for q in profile)
            for profile in profiles
        ))

    def test_two_sided_crossings(self) -> None:
        self.assertEqual(CHECK.crossing_counts_from_row_supports(2, 1), (0,))
        self.assertEqual(CHECK.crossing_counts_from_row_supports(2, 3), (0, 4))
        self.assertEqual(CHECK.crossing_counts_from_row_supports(3, 3), (0, 4, 6))
        self.assertEqual(CHECK.crossing_counts_from_row_supports(4, 2), (0, 4))

    def test_one_sided_mutation_is_detected(self) -> None:
        self.assertIn(
            2,
            CHECK.crossing_counts_from_row_supports(
                2, 3, require_column_rule=False
            ),
        )
        self.assertNotIn(2, CHECK.crossing_counts_from_row_supports(2, 3))

    def test_r20_point_profiles_by_size_counts(self) -> None:
        self.assertEqual(len(CHECK.point_profiles_by_counts(60, 27)), 11)
        self.assertEqual(len(CHECK.point_profiles_by_counts(60, 28)), 5)
        self.assertEqual(len(CHECK.point_profiles_by_counts(60, 29)), 2)
        self.assertEqual(
            CHECK.point_profiles_by_counts(60, 30), ((2,) * 30,)
        )

    def test_outside_formula_against_direct_pair_count(self) -> None:
        self.assertEqual(
            CHECK.outside_moments_from_pair_count(27, [0] * 27),
            {
                "vertices": 72,
                "sum": 216,
                "sum_squares": 648,
                "T": 0,
                "U": 0,
            },
        )
        self.assertEqual(
            CHECK.outside_moments_from_pair_count(29, [6] + [0] * 28)[
                "sum_squares"
            ],
            698,
        )

    def test_m27_equality_histogram(self) -> None:
        self.assertEqual(
            CHECK.histogram_solver(72, 216, 648), (((3, 72),),)
        )

    def test_cubic_complement_classification_and_2switch(self) -> None:
        classification = CHECK.cubic_six_classification_via_complement()
        self.assertEqual(
            classification["isomorphism_types"],
            ("K3,3", "triangular_prism"),
        )
        self.assertEqual(
            classification["triangle_counts"],
            {"K3,3": 0, "triangular_prism": 2},
        )
        self.assertEqual(classification["labeled_cubic_graph_count"], 70)

    def test_both_cubic_types_survive_local_no_berge_layer(self) -> None:
        realizations = CHECK.local_size3_point_realizations()
        self.assertEqual(set(realizations), {"K3,3", "triangular_prism"})
        self.assertEqual(
            realizations["K3,3"]["meeting_degree_sequence"], [3] * 6
        )
        self.assertEqual(
            realizations["triangular_prism"]["meeting_degree_sequence"], [3] * 6
        )

    def test_cycle_partition_counts(self) -> None:
        self.assertEqual(CHECK.cycle_partition_count(21), 60)
        self.assertEqual(CHECK.cycle_partition_count(30), 331)

    def test_generated_z_topology_coverage(self) -> None:
        self.assertEqual(
            set(CHECK.generated_z_topologies()),
            {
                "empty", "K2", "2K2", "P3", "3K2",
                "P3_plus_K2", "P4", "K1,3", "K3",
            },
        )

    def test_outside_histogram_counts(self) -> None:
        requested = {
            "empty": (69, 240, 900, 1297),
            "K2": (69, 238, 872, 354),
            "2K2": (69, 236, 844, 69),
            "P3": (69, 236, 842, 52),
            "3K2": (69, 234, 816, 6),
            "P3_plus_K2": (69, 234, 814, 3),
            "P4": (69, 234, 812, 2),
            "K1,3": (69, 234, 810, 1),
            "K3": (69, 234, 810, 1),
        }
        for name, (count, total, squares, expected) in requested.items():
            with self.subTest(name=name):
                self.assertEqual(
                    len(CHECK.histogram_solver(count, total, squares)),
                    expected,
                )

    def test_four_edges_are_rejected_independent_of_topology(self) -> None:
        self.assertLess(
            900 - 13 * 8 - 8,
            CHECK.integer_minimum_square_sum(69, 232),
        )

    def test_simple_graph_impostors(self) -> None:
        with self.assertRaises(ValueError):
            CHECK.edges_from_bits(3, [(0, 0)])
        with self.assertRaises(ValueError):
            CHECK.edges_from_bits(3, [(0, 1), (1, 0)])

    def test_all_frozen_hostile_mutations(self) -> None:
        results = CHECK.mutation_results()
        self.assertEqual(len(results), 17)
        self.assertTrue(all(
            value.startswith(("REJECTED", "RETAINED", "CONFIRMED"))
            for value in results.values()
        ))

    def test_status_boundary(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(
            result["status_boundary"]["conditional_n3_60"],
            "UNKNOWN_FINITE_RESIDUAL",
        )
        self.assertEqual(result["status_boundary"]["conway_99_target"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
