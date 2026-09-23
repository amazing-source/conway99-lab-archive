#!/usr/bin/env python3
"""Tests for the Wave154 branch-diverse exact-factor portfolio."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import exact_check


HERE = Path(__file__).resolve().parent


class PortfolioTests(unittest.TestCase):
    def test_stored_result(self) -> None:
        exact_check.verify_payload(json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        ))

    def test_second_q1_is_exact_and_orbit_distinct(self) -> None:
        result = exact_check.build_result()
        record = result["second_exact_Q1_representative"]
        self.assertTrue(record["G01_replayed"])
        self.assertTrue(record["outside_Wave151_Q1_centralizer_orbit"])

    def test_joint_model_counts_and_unknown_status(self) -> None:
        result = exact_check.build_result()
        joint = result["joint_exact_cover"]
        self.assertEqual(joint["primary_triple_variables"], 69270)
        self.assertEqual(joint["triple_orbits_under_explicit_group"], 292)
        self.assertEqual(joint["complete_factor_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
