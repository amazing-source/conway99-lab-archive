"""Hostile regression tests for the clean-room Wave 74 verifier."""

from __future__ import annotations

import importlib.util
import json
import unittest
from math import comb
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave74_verifier", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave74Tests(unittest.TestCase):
    def test_frozen_inputs_match_before_claim_checks(self) -> None:
        freeze = Path(__file__).with_name("input-freeze.sha256")
        for line in freeze.read_text(encoding="utf-8").splitlines():
            expected, relative = line.split("  ", 1)
            self.assertEqual(CHECK.sha256(CHECK.ROOT / relative), expected)

    def test_two_edge_shapes_are_exhaustive(self) -> None:
        classes = CHECK.two_edge_shape_degree_multisets(9)
        self.assertEqual(
            classes,
            {
                (2, 1, 1, 0, 0, 0, 0, 0, 0): 252,
                (1, 1, 1, 1, 0, 0, 0, 0, 0): 378,
            },
        )
        self.assertEqual(sum(classes.values()), comb(comb(9, 2), 2))

    def test_adjacent_h2_fails_before_outside_counts(self) -> None:
        lane = CHECK.lane_scalars(9, 2, "adjacent")
        self.assertEqual(lane["same_side_pair_capacity"], 70)
        self.assertEqual(
            lane["pair_incidences_through_opposite_support"], 71
        )
        self.assertEqual(lane["pair_incidences_through_same_support"], 1)
        self.assertEqual(lane["outside_pair_incidences"], -2)
        self.assertTrue(lane["opposite_support_already_exceeds_capacity"])

    def test_disjoint_h2_is_exact_82_into_81_contradiction(self) -> None:
        lane = CHECK.lane_scalars(9, 2, "disjoint")
        self.assertEqual(
            (
                lane["outside_vertices"],
                lane["outside_incidences_per_side"],
                lane["outside_pair_incidences"],
            ),
            (81, 82, 0),
        )
        self.assertEqual(CHECK.cartesian_histograms(81, 82, 0), [])
        self.assertEqual(
            CHECK.cartesian_histograms(81, 81, 0),
            [[0, 81, 0, 0, 0, 0, 0, 0]],
        )

    def test_all_remaining_histograms_match_discovery_bytes(self) -> None:
        result = CHECK.build_results()
        discovery = json.loads(
            CHECK.DISCOVERY_RESULT.read_text(encoding="utf-8")
        )
        for name, count in (
            ("norm16_h0", 4),
            ("norm18_h0", 20),
            ("norm18_h1", 6),
        ):
            observed = result["lanes"][name]
            claimed = discovery["lanes"][name]
            self.assertEqual(observed["histogram_count"], count)
            self.assertEqual(observed["histograms"], claimed["histograms"])

    def test_each_histogram_satisfies_all_three_moments(self) -> None:
        result = CHECK.build_results()
        for name in ("norm16_h0", "norm18_h0", "norm18_h1"):
            lane = result["lanes"][name]
            expected = (
                lane["outside_vertices"],
                lane["outside_incidences_per_side"],
                lane["outside_pair_incidences"],
            )
            for histogram in lane["histograms"]:
                self.assertEqual(CHECK.histogram_moments(histogram), expected)

    def test_status_and_realization_guards(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(result["claim_label"], "VERIFIED")
        self.assertFalse(
            result["endpoint"]["all_short_vector_alternatives_excluded"]
        )
        self.assertEqual(result["endpoint"]["conway_status"], "UNKNOWN")
        limitations = " ".join(result["limitations"])
        self.assertIn("necessary aggregate moments only", limitations)
        self.assertIn("No histogram is promoted", limitations)


if __name__ == "__main__":
    unittest.main()
