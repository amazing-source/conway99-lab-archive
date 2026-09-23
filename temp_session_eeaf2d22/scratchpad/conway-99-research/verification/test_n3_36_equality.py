#!/usr/bin/env python3
"""Regression tests for the compact Wave 10 equality checker."""

from __future__ import annotations

import importlib.util
import unittest
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERIFIER_PATH = ROOT / "n3-36-equality" / "verify.py"
SPEC = importlib.util.spec_from_file_location("n3_36_equality_verifier", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load the n3=36 equality verifier")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class N336EqualityVerifierTests(unittest.TestCase):
    def test_committed_checker_passes(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(VERIFIER.main([]), 0)
        rendered = output.getvalue()
        self.assertIn("PASS n3=36 equality exclusion arithmetic", rendered)
        self.assertIn("global_n3_lower_bound 39", rendered)
        self.assertIn("global_p6_lower_bound 209325", rendered)

    def test_active_profiles_and_k_degrees(self) -> None:
        profiles = VERIFIER.active_q_sequences(36)
        self.assertEqual(
            profiles,
            ((2,) * 12, (2,) * 9 + (3, 3), (2,) * 6 + (3,) * 4),
        )
        self.assertEqual(Counter(VERIFIER.k_degree_profile(profiles[1])), Counter({4: 9, 1: 2}))
        with self.assertRaises(ValueError):
            VERIFIER.active_q_sequences(1)

    def test_singleton_crossing_and_forcing(self) -> None:
        self.assertEqual(VERIFIER.biregular_crossing_edge_counts(1, 4), frozenset((0,)))
        self.assertEqual(VERIFIER.forced_singletons_at_triangle(0), 3)
        self.assertEqual(VERIFIER.forced_singletons_at_triangle(1), 2)
        with self.assertRaises(ValueError):
            VERIFIER.biregular_crossing_edge_counts(-1, 2)

    def test_local_types_and_crossings(self) -> None:
        self.assertEqual(
            VERIFIER.local_point_types(),
            ((2, 2, 2), (2, 2, 3), (2, 2, 4), (2, 3, 3)),
        )
        self.assertEqual(VERIFIER.local_crossing_counts(2, 4), frozenset((0,)))
        self.assertEqual(VERIFIER.local_crossing_counts(3, 3), frozenset((0, 4)))
        self.assertEqual(VERIFIER.complete_cross_component_size_pairs(), ((2, 2),))

    def test_cubic_six_census(self) -> None:
        cubic = VERIFIER.cubic_graphs_on_six()
        triangle_free = tuple(graph for graph in cubic if not VERIFIER.contains_triangle(graph, 6))
        self.assertEqual(len(cubic), 70)
        self.assertEqual(len(triangle_free), 10)
        self.assertTrue(all(VERIFIER.is_k33(graph) for graph in triangle_free))

    def test_rook_saturation(self) -> None:
        adjacent, nonadjacent, common = VERIFIER.rook_graph_audit()
        self.assertEqual((adjacent, nonadjacent), (18, 18))
        self.assertEqual(Counter(common), Counter({1: 18, 2: 18}))

    def test_common_point_rule(self) -> None:
        self.assertTrue(
            VERIFIER.forbidden_common_point_triple(
                (
                    frozenset((0, 1, 2)),
                    frozenset((0, 3)),
                    frozenset((1, 3)),
                )
            )
        )
        self.assertFalse(
            VERIFIER.forbidden_common_point_triple(
                (
                    frozenset((0, 1, 2)),
                    frozenset((0, 3)),
                    frozenset((0, 4)),
                )
            )
        )

    def test_size_three_obstructions(self) -> None:
        self.assertEqual(VERIFIER.size_three_223_endpoint_choices(), (3, 0))
        self.assertEqual(VERIFIER.split_233_type222_mate_choices(), (2, 0))
        self.assertEqual(VERIFIER.line_twin_cross_configurations(), (1, 0))

    def test_all_size_two_pairing(self) -> None:
        pairings = VERIFIER.triangle_group_pairings()
        self.assertEqual(len(pairings), 3)
        self.assertTrue(all(VERIFIER.paired_group_k_components(item) == (6, 6) for item in pairings))
        with self.assertRaises(ValueError):
            VERIFIER.triangle_group_pairings(3)

    def test_wave10_branch_bounds(self) -> None:
        self.assertEqual(
            tuple(
                max(39, VERIFIER.ceil_multiple_of_three(4 * degree))
                for degree in VERIFIER.WAVE6_BRANCH_DEGREES
            ),
            (39, 39, 42, 48, 48, 39, 42, 48, 39, 48, 42, 48),
        )


if __name__ == "__main__":
    unittest.main()
