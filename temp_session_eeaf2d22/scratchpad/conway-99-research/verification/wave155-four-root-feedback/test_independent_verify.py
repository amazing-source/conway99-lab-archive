"""Tests for the Wave155 clean-room verifier and its emitted certificate."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
VERIFIER = HERE / "independent_verify.py"
RESULT = HERE / "verification-results.json"


class IndependentVerifierTests(unittest.TestCase):
    def test_lightweight_semantics_self_test(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VERIFIER), "--self-test"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["flag_counts"], {"3": 155, "12": 178})
        self.assertEqual(payload["covering_pair_counts"], {"2": 1, "3": 6, "4": 6})

    def test_emitted_exact_certificate(self) -> None:
        self.assertTrue(RESULT.is_file(), "run independent_verify.py first")
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(payload["claim_label"], "VERIFIED")
        self.assertFalse(payload["separation"]["discovery_python_imported"])
        self.assertFalse(payload["separation"]["discovery_python_executed"])
        self.assertFalse(payload["separation"]["solver_status_used_as_evidence"])
        self.assertEqual(len(payload["cuts"]), 4)
        self.assertEqual(
            payload["verdict"]["finite_relaxation_after_two_cuts"],
            "EXACT_RATIONAL_FEASIBLE",
        )
        self.assertEqual(
            payload["verdict"]["finite_relaxation_after_four_cuts"],
            "EXACT_RATIONAL_FEASIBLE",
        )
        self.assertEqual(payload["witnesses"]["after_two"]["all_equalities"], 10311)
        self.assertEqual(payload["witnesses"]["after_four"]["all_equalities"], 10312)
        self.assertTrue(
            payload["witnesses"]["after_two"]["selected_row_indices_exact_match"]
        )
        self.assertTrue(
            payload["witnesses"]["after_four"]["selected_row_indices_exact_match"]
        )
        self.assertGreaterEqual(
            payload["resource_report"]["minimum_free_physical_memory_percent"],
            15.0,
        )
        self.assertEqual(payload["verdict"]["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(payload["verdict"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
