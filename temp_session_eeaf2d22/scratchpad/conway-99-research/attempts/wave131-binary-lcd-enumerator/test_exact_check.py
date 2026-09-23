"""Tests for the exact Wave131 discovery package."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave131_exact_check", HERE / "exact_check.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Wave131Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.exact_results()

    def test_canonical_result(self) -> None:
        expected = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.result, expected)

    def test_requested_image_counts(self) -> None:
        self.assertEqual(
            self.result["forced_distributions"]["image_forced_lower"],
            {
                "14": 99,
                "24": 4158,
                "26": 693,
                "30": 70686,
                "32": 41580,
                "34": 36036,
                "36": 8547,
            },
        )

    def test_requested_dual_counts(self) -> None:
        self.assertEqual(
            self.result["forced_distributions"]["dual_forced_lower"],
            {
                "15": 99,
                "24": 693,
                "26": 4158,
                "31": 41580,
                "33": 79002,
                "35": 8316,
                "37": 27720,
                "39": 231,
            },
        )

    def test_rational_witness(self) -> None:
        audit = self.result["rational_witness_audit"]
        self.assertTrue(
            audit["all_200_forward_and_inverse_MacWilliams_rows_pass"]
        )
        self.assertEqual(audit["image_minimum_nonzero_weight"], 14)
        self.assertEqual(audit["dual_minimum_nonzero_weight"], 15)
        self.assertFalse(audit["formal_integral_enumerator"])
        self.assertGreater(audit["image_nonintegral_coefficient_count"], 0)
        self.assertGreater(audit["dual_nonintegral_coefficient_count"], 0)

    def test_unknown_wall(self) -> None:
        self.assertEqual(
            self.result["integral_scout"]["result"]["status"],
            "UNKNOWN_HARD_TIMEOUT",
        )
        status = self.result["status"]
        self.assertEqual(status["integral_formal_enumerator"], "UNKNOWN")
        self.assertFalse(status["binary_code_constructed"])
        self.assertFalse(status["graph_constructed"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
