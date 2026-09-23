#!/usr/bin/env python3
"""Tests for the exact Wave149 triangle-root projection."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import exact_check


HERE = Path(__file__).resolve().parent


class TriangleRootTests(unittest.TestCase):
    def test_exact_reconstruction(self) -> None:
        payload = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        exact_check.verify_payload(payload)

    def test_prism_free_and_psd_rank(self) -> None:
        result = exact_check.build_result()
        witness = result["minimal_surviving_witness"]
        self.assertEqual(witness["rooted_prism_fixed_points"], 0)
        self.assertEqual(witness["gram_rank"], 32)
        self.assertEqual(witness["gram_minimum_entry"], 0)

    def test_character_certificate_is_exactly_nonnegative(self) -> None:
        records = exact_check.character_certificate()
        self.assertTrue(
            all(record["antisymmetric_eigenvalue"] >= 0 for record in records)
        )
        self.assertTrue(
            all(record["symmetric_2x2_determinant"] >= 0 for record in records)
        )


if __name__ == "__main__":
    unittest.main()
