#!/usr/bin/env python3
"""Regression tests for the independent Wave 8 equality checker."""

from __future__ import annotations

import importlib.util
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERIFIER_PATH = ROOT / "n3-equality" / "verify.py"
SPEC = importlib.util.spec_from_file_location("n3_equality_verifier", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load the n3 equality verifier")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class N3EqualityVerifierTests(unittest.TestCase):
    def test_committed_checker_passes(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(VERIFIER.main([]), 0)
        rendered = output.getvalue()
        self.assertIn("PASS n3=30 equality exclusion arithmetic", rendered)
        self.assertIn("forced_overlap_h_degree 1", rendered)
        self.assertIn("global_n3_lower_bound 33", rendered)
        self.assertIn("global_p6_lower_bound 209319", rendered)

    def test_n3_30_active_sequence(self) -> None:
        self.assertEqual(VERIFIER.active_q_sequences(30), ((2,) * 10,))
        with self.assertRaises(ValueError):
            VERIFIER.active_q_sequences(1)

    def test_fixed_triangle_endpoint_profile(self) -> None:
        self.assertEqual(VERIFIER.fixed_triangle_profile(2), (10, 2, 4))
        self.assertEqual(VERIFIER.fixed_triangle_profile(12), (0, 12, 24))
        with self.assertRaises(ValueError):
            VERIFIER.fixed_triangle_profile(13)

    def test_point_size_equations(self) -> None:
        self.assertEqual(
            VERIFIER.point_size_solutions(
                incidence_total=30,
                edge_budget=15,
                maximum_size=3,
                forbid_singletons=True,
            ),
            ((0, 15, 0),),
        )
        with self.assertRaises(ValueError):
            VERIFIER.point_size_solutions(
                incidence_total=30,
                edge_budget=15,
                maximum_size=0,
                forbid_singletons=True,
            )

    def test_cubic_component_orders(self) -> None:
        self.assertEqual(VERIFIER.cubic_component_partitions(10), ((4, 6), (10,)))
        self.assertEqual(VERIFIER.cubic_component_partitions(8), ((4, 4), (8,)))

    def test_overlap_crossing_is_counted_once(self) -> None:
        first = frozenset((0, 1))
        second = frozenset((0, 2))
        self.assertEqual(
            VERIFIER.crossing_l_edges(first, second, frozenset(((1, 2),))),
            1,
        )

    def test_internal_edges_force_clique_neighborhoods(self) -> None:
        profiles = VERIFIER.internal_crossing_profiles(3)
        self.assertIn((1, 1, 0, 1), profiles)
        self.assertIn((1, 1, 1, 0), profiles)
        self.assertFalse(
            [
                profile
                for profile in profiles
                if profile[3] in VERIFIER.ALLOWED_H_DEGREES - {0}
            ]
        )
        with self.assertRaises(ValueError):
            VERIFIER.internal_crossing_profiles(-1)

    def test_wave8_branch_bounds(self) -> None:
        self.assertEqual(
            tuple(
                max(33, VERIFIER.ceil_multiple_of_three(4 * degree))
                for degree in VERIFIER.WAVE6_BRANCH_DEGREES
            ),
            (33, 33, 42, 48, 48, 33, 42, 48, 33, 48, 42, 48),
        )


if __name__ == "__main__":
    unittest.main()
