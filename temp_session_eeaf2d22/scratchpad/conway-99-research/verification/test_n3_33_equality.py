#!/usr/bin/env python3
"""Regression tests for the independent Wave 9 equality checker."""

from __future__ import annotations

import importlib.util
import unittest
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERIFIER_PATH = ROOT / "n3-33-equality" / "verify.py"
SPEC = importlib.util.spec_from_file_location("n3_33_equality_verifier", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load the n3=33 equality verifier")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class N333EqualityVerifierTests(unittest.TestCase):
    def test_committed_checker_passes(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(VERIFIER.main([]), 0)
        rendered = output.getvalue()
        self.assertIn("PASS n3=33 equality exclusion arithmetic", rendered)
        self.assertIn("valid_residual_local_choices 0", rendered)
        self.assertIn("global_n3_lower_bound 36", rendered)
        self.assertIn("global_p6_lower_bound 209322", rendered)

    def test_active_q_sequences(self) -> None:
        self.assertEqual(
            VERIFIER.active_q_sequences(33),
            ((2,) * 11, (2,) * 8 + (3, 3)),
        )
        with self.assertRaises(ValueError):
            VERIFIER.active_q_sequences(1)

    def test_fixed_triangle_profiles(self) -> None:
        self.assertEqual(VERIFIER.fixed_triangle_profile(2), (10, 2, 4))
        self.assertEqual(VERIFIER.fixed_triangle_profile(3), (9, 3, 6))
        with self.assertRaises(ValueError):
            VERIFIER.fixed_triangle_profile(13)

    def test_mixed_profile_degree_sum(self) -> None:
        totals = VERIFIER.bounded_h_degree_sums(14, 4)
        self.assertNotIn(6, totals)
        self.assertIn(56, totals)
        with self.assertRaises(ValueError):
            VERIFIER.bounded_h_degree_sums(-1, 4)

    def test_singleton_two_regular_crossing(self) -> None:
        self.assertEqual(
            VERIFIER.singleton_biregular_crossing_counts(5),
            frozenset((0,)),
        )
        with self.assertRaises(ValueError):
            VERIFIER.singleton_biregular_crossing_counts(-1)

    def test_point_size_equations(self) -> None:
        self.assertEqual(
            VERIFIER.point_size_solutions(incidence_total=33, edge_budget=22),
            ((12, 3), (15, 1)),
        )
        with self.assertRaises(ValueError):
            VERIFIER.point_size_solutions(incidence_total=-1, edge_budget=22)

    def test_size_three_forces_k5(self) -> None:
        expected = frozenset(
            VERIFIER.normalized_edge(left, right)
            for left, right in combinations(range(5), 2)
        )
        self.assertEqual(VERIFIER.size_three_local_closures(), (expected,))

    def test_perfect_matchings(self) -> None:
        self.assertEqual(len(VERIFIER.perfect_matchings(range(6))), 15)
        self.assertEqual(len(VERIFIER.perfect_matchings(range(4))), 3)
        with self.assertRaises(ValueError):
            VERIFIER.perfect_matchings(range(5))

    def test_residual_k6_minus_matching_obstruction(self) -> None:
        self.assertEqual(VERIFIER.residual_local_choices(), (360, 0))

    def test_wave9_branch_bounds(self) -> None:
        self.assertEqual(
            tuple(
                max(36, VERIFIER.ceil_multiple_of_three(4 * degree))
                for degree in VERIFIER.WAVE6_BRANCH_DEGREES
            ),
            (36, 36, 42, 48, 48, 36, 42, 48, 36, 48, 42, 48),
        )


if __name__ == "__main__":
    unittest.main()
