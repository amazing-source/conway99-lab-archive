#!/usr/bin/env python3
"""Tests for the Wave 27 A20 trace-compression addendum."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import exact_check as check


class Wave27A20TraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = check.build_results()

    def test_frozen_inputs(self) -> None:
        self.assertTrue(all(
            row["matches"] for row in self.payload["frozen_inputs"].values()
        ))

    def test_rank_one_identity_for_every_relevant_rank(self) -> None:
        for rank in range(1, 45):
            result = check.rank_one_factorization(rank)
            self.assertTrue(result["sum_outer_products_equals_cartan"])
            self.assertEqual(result["vector_count"], rank + 1)

    def test_A20_local_floor(self) -> None:
        result = self.payload["A20_rank_one_factorization"]
        self.assertEqual(result["trace_pairing_floor"], 42)

    def test_endpoint_compression_contradiction(self) -> None:
        result = self.payload["endpoint_compression"]
        self.assertEqual(result["local_even_trace_floor"], 42)
        self.assertEqual(result["complement_AM_GM_trace_floor"], 24)
        self.assertEqual(result["aggregate_trace_floor"], 66)
        self.assertEqual(result["contradiction_margin"], 6)
        self.assertEqual(result["orthogonal_A20_summand"], "REFUTED")

    def test_general_threshold_is_sharp_for_this_argument(self) -> None:
        result = self.payload["general_A_n_threshold"]
        self.assertEqual(result["sharp_first_excluded_rank"], 15)
        self.assertEqual(result["A14_aggregate_floor"], 60)
        self.assertEqual(result["A15_aggregate_floor"], 61)

    def test_full_ADE_scope(self) -> None:
        result = self.payload["full_ADE_corollary"]
        self.assertTrue(result["rank_44_not_sum_of_E8_only"])
        self.assertIn("PENDING", result["conditional_full_ADE_status"])
        self.assertFalse(self.payload["scope"]["general_even_lattices_classified"])

    def test_hostile_controls_and_target_wall(self) -> None:
        controls = self.payload["hostile_controls"]
        self.assertIn("one", controls["drop_evenness"])
        self.assertIn("not contradictory", controls["A14_boundary"])
        self.assertFalse(self.payload["scope"]["n3_708_excluded"])
        self.assertEqual(self.payload["scope"]["conway_99_status"], "UNKNOWN")

    def test_deterministic_lf_json(self) -> None:
        expected = (
            json.dumps(self.payload, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result.json"
            output.write_bytes(expected)
            self.assertEqual(output.read_bytes(), expected)
            self.assertNotIn(b"\r\n", output.read_bytes())


if __name__ == "__main__":
    unittest.main()
