from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("compare_discovery.py")
SPEC = importlib.util.spec_from_file_location(
    "wave100_compare_discovery", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
COMPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPARE)


class Wave100ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = COMPARE.comparison()

    def test_attempt_manifest_is_complete_and_frozen(self) -> None:
        self.assertEqual(len(COMPARE.verify_attempt_manifest()), 9)

    def test_verdict(self) -> None:
        self.assertEqual(self.result["claim_label"], "VERIFIED")
        self.assertIn("VERIFIED SCOPED", self.result["verdict"])

    def test_core_agreement(self) -> None:
        agreement = self.result["agreement"]
        self.assertEqual(agreement["floor_sum_upper"], "34650+15P")
        self.assertEqual(agreement["sum_f_identity"], "sum_o f_o=6P")
        self.assertEqual(agreement["n3_coefficient"], -5)
        self.assertEqual(agreement["compatible_rows_checked"], 1387)
        self.assertEqual(
            agreement["rows_strictly_improved_by_even_rounding"], 693
        )

    def test_scope_and_status(self) -> None:
        self.assertFalse(self.result["scope_audit"]["requires_P0"])
        self.assertFalse(self.result["scope_audit"]["requires_rank_28"])
        status = self.result["status_boundary"]
        self.assertEqual(status["strict_n3_upper_bound"], "NOT_PROVED")
        self.assertEqual(status["graph_nonexistence"], "NOT_PROVED")
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
