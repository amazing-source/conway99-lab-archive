from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave190_exact_check", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave190ExactCheckTests(unittest.TestCase):
    def test_coefficient_certificate(self) -> None:
        CHECK.check_coefficient_certificate()

    def test_sharp_relaxation_row(self) -> None:
        CHECK.check_sharp_relaxation_row()

    def test_frozen_results(self) -> None:
        results = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(results["claim_label"], "DERIVED")
        self.assertEqual(results["nonedge_projective_circuit_lower"], 5544)
        self.assertEqual(results["dual_short_circuit_word_lower"], 12474)
        self.assertEqual(results["rank_11_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
