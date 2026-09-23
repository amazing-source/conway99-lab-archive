"""Tests for the exact Wave132 discovery package."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave132_exact_check", HERE / "exact_check.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Wave132Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.exact_results()

    def test_canonical_result(self) -> None:
        expected = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.result, expected)

    def test_strict_high_weight_cut(self) -> None:
        self.assertEqual(
            self.result["high_weight_cut"]["forced_zero_weights"],
            [94, 96, 98],
        )
        self.assertTrue(
            self.result["strictness_over_Wave131"][
                "Wave131_fails_distinguished_moment_cut"
            ]
        )

    def test_pair_tables(self) -> None:
        audit = self.result["pair_table_audit"]
        self.assertEqual(audit["ordered_edges"], 1386)
        self.assertEqual(audit["ordered_nonedges"], 8316)
        self.assertEqual(audit["image_ordered_pair_total"], 99**2)
        self.assertEqual(audit["dual_ordered_pair_total"], 99**2)
        self.assertEqual(audit["mixed_ordered_pair_total"], 99**2)

    def test_rational_split_witness(self) -> None:
        witness = self.result["rational_witness"]
        self.assertTrue(
            witness["ordinary_audit"]["all_200_MacWilliams_rows_pass"]
        )
        for audit in witness["split_audits"].values():
            self.assertTrue(
                audit["all_row_sums_first_moments_and_parities_pass"]
            )
        self.assertFalse(witness["formal_integral_split_enumerator"])
        self.assertFalse(witness["binary_code_realized"])

    def test_unknown_wall(self) -> None:
        self.assertEqual(
            self.result["integral_scout"]["result"]["status"],
            "UNKNOWN_HARD_TIMEOUT",
        )
        status = self.result["status"]
        self.assertEqual(status["integral_projection"], "UNKNOWN")
        self.assertEqual(status["full_genus_two"], "UNKNOWN")
        self.assertFalse(status["binary_code_constructed"])
        self.assertFalse(status["graph_constructed"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
