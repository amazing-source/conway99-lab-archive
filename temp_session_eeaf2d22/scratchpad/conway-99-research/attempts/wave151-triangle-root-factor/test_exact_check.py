#!/usr/bin/env python3
"""Tests for the Wave151 partial binary factor."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import exact_check


HERE = Path(__file__).resolve().parent


class BinaryFactorTests(unittest.TestCase):
    def test_stored_result(self) -> None:
        payload = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        exact_check.verify_payload(payload)

    def test_q1_is_exact_partial_factor(self) -> None:
        result = exact_check.build_result()
        partial = result["exact_partial_factor"]
        self.assertEqual(partial["shape"], [24, 60])
        self.assertTrue(partial["diagonal_and_G01_blocks_replayed"])

    def test_full_status_remains_unknown(self) -> None:
        result = exact_check.build_result()
        self.assertEqual(result["conclusion"]["complete_C_factor"], "UNKNOWN")
        self.assertEqual(result["residual_D_layer"]["status"], "NOT_REACHED")


if __name__ == "__main__":
    unittest.main()
