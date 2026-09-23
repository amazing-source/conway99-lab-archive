#!/usr/bin/env python3
"""Regression tests for the independent Wave 7 incidence checker."""

from __future__ import annotations

import importlib.util
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERIFIER_PATH = ROOT / "n3-side-incidence" / "verify.py"
SPEC = importlib.util.spec_from_file_location("n3_side_incidence_verifier", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load the N3 side-incidence verifier")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)

GENERIC_PATH = ROOT / "n3-side-incidence" / "audit_generic.py"
GENERIC_SPEC = importlib.util.spec_from_file_location(
    "n3_side_incidence_generic_audit", GENERIC_PATH
)
if GENERIC_SPEC is None or GENERIC_SPEC.loader is None:
    raise RuntimeError("could not load the generic N3 side-incidence audit")
GENERIC = importlib.util.module_from_spec(GENERIC_SPEC)
GENERIC_SPEC.loader.exec_module(GENERIC)


class N3SideIncidenceVerifierTests(unittest.TestCase):
    def test_committed_checker_passes(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(VERIFIER.main([]), 0)
        rendered = output.getvalue()
        self.assertIn("PASS N3 side-incidence exact checks", rendered)
        self.assertIn("global_n3_lower_bound 30", rendered)
        self.assertIn("global_p6_lower_bound 209316", rendered)

    def test_cross_edge_count_equations(self) -> None:
        self.assertEqual(VERIFIER.partner_counts(0), (20, 180, 0, 12))
        self.assertEqual(VERIFIER.partner_counts(12), (32, 144, 36, 0))
        with self.assertRaises(ValueError):
            VERIFIER.partner_counts(13)

    def test_extremal_active_q_sequences(self) -> None:
        self.assertEqual(VERIFIER.active_q_sequences(24), ((2,) * 8,))
        self.assertEqual(VERIFIER.active_q_sequences(27), ((2,) * 9,))

    def test_support_enumerations(self) -> None:
        self.assertEqual(VERIFIER.matching_support_maximum(4), (6, {4}))
        self.assertEqual(
            VERIFIER.cycle_support_maximum((3, 6), require_triple=True)[:2],
            (9, {4, 6}),
        )
        self.assertEqual(
            VERIFIER.cycle_support_maximum((3, 3, 3), require_triple=True)[:2],
            (8, {4, 6}),
        )

    def test_overlap_crossings_are_counted_once(self) -> None:
        _, l_edges = VERIFIER.complement_cycle_graph((3, 6))
        left = frozenset((0, 1, 2))
        right = frozenset((2, 3))
        expected = len(
            {
                edge
                for edge in l_edges
                if (edge[0] in left and edge[1] in right)
                or (edge[1] in left and edge[0] in right)
            }
        )
        self.assertEqual(VERIFIER.crossing_l_edges(left, right, l_edges), expected)

    def test_generic_audit_passes(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(GENERIC.main(), 0)
        rendered = output.getvalue()
        self.assertIn("PASS generic N3 point-clique audit", rendered)
        self.assertIn("n3_27_c3_c6_support_maximum 9", rendered)
        self.assertIn("n3_27_3c3_support_maxima [8, 4, 0]", rendered)


if __name__ == "__main__":
    unittest.main()
