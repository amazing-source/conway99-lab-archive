"""Focused tests for Wave74 outside-incidence closure."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave74_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave74ExactCheckTests(unittest.TestCase):
    def test_norm18_h2_adjacent_capacity_failure(self) -> None:
        lane = CHECK.lane_parameters(9, 2, "adjacent")
        self.assertEqual(lane["inside_pair_incidences_through_opposite_side"], 71)
        self.assertEqual(lane["same_side_pair_capacity"], 70)
        self.assertTrue(lane["pair_capacity_already_exceeded"])

    def test_norm18_h2_disjoint_pigeonhole(self) -> None:
        lane = CHECK.checked_lane("h2", 9, 2, "disjoint")
        self.assertEqual(lane["inside_pair_incidences_through_opposite_side"], 70)
        self.assertEqual(lane["same_side_pair_capacity"], 70)
        self.assertEqual(lane["outside_pair_incidences"], 0)
        self.assertEqual(lane["outside_vertices"], 81)
        self.assertEqual(lane["outside_incidences_per_side"], 82)
        self.assertEqual(lane["histogram_count"], 0)

    def test_norm16_histograms(self) -> None:
        lane = CHECK.checked_lane("norm16", 8, 0, "none")
        self.assertEqual(lane["outside_vertices"], 83)
        self.assertEqual(lane["outside_incidences_per_side"], 80)
        self.assertEqual(lane["outside_pair_incidences"], 8)
        self.assertEqual(lane["outside_induced_edges"], 501)
        self.assertEqual(lane["histogram_count"], 4)
        self.assertEqual(
            lane["histograms"],
            [
                [8, 72, 2, 0, 1, 0, 0, 0],
                [9, 70, 2, 2, 0, 0, 0, 0],
                [10, 67, 5, 1, 0, 0, 0, 0],
                [11, 64, 8, 0, 0, 0, 0, 0],
            ],
        )

    def test_norm18_remaining_histogram_counts(self) -> None:
        h0 = CHECK.checked_lane("h0", 9, 0, "none")
        h1 = CHECK.checked_lane("h1", 9, 1, "single")
        self.assertEqual(
            (
                h0["outside_incidences_per_side"],
                h0["outside_pair_incidences"],
                h0["outside_induced_edges"],
                h0["histogram_count"],
            ),
            (90, 18, 477, 20),
        )
        self.assertEqual(
            (
                h1["outside_incidences_per_side"],
                h1["outside_pair_incidences"],
                h1["outside_induced_edges"],
                h1["histogram_count"],
            ),
            (86, 9, 481, 6),
        )

    def test_histogram_moments(self) -> None:
        result = CHECK.build_results()
        for name in ("norm16_h0", "norm18_h0", "norm18_h1"):
            lane = result["lanes"][name]
            for histogram in lane["histograms"]:
                self.assertEqual(sum(histogram), lane["outside_vertices"])
                self.assertEqual(
                    sum(d * count for d, count in enumerate(histogram)),
                    lane["outside_incidences_per_side"],
                )
                self.assertEqual(
                    sum(CHECK.comb(d, 2) * count for d, count in enumerate(histogram)),
                    lane["outside_pair_incidences"],
                )

    def test_status_guards(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(result["claim_label"], "DERIVED")
        self.assertEqual(result["norm18_closure"]["surviving_h"], [0, 1])
        self.assertFalse(
            result["endpoint"]["all_short_vector_alternatives_excluded"]
        )
        self.assertEqual(result["endpoint"]["conway_status"], "UNKNOWN")
        self.assertEqual(result["endpoint"]["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
