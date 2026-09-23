"""Tests for the frozen clean-room Wave148 row protocol."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import clean_room_rows as clean  # noqa: E402


class CleanRoomMarkedRowsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(
            (HERE / "expected-invariants.json").read_text(encoding="utf-8")
        )

    def test_protocol_is_not_discovery_verification(self) -> None:
        self.assertEqual(
            self.result["claim_label"],
            "DERIVED_PROTOCOL_NOT_DISCOVERY_VERIFICATION",
        )
        self.assertEqual(
            self.result["status"]["wave148_manifest"], "NOT_RECEIVED"
        )
        self.assertFalse(
            self.result["status"]["wave148_artifacts_verified"]
        )

    def test_root_conventions(self) -> None:
        conventions = self.result["conventions"]
        self.assertTrue(conventions["pair_ordered"])
        self.assertTrue(conventions["marks_fixed_pointwise"])
        self.assertFalse(conventions["automorphism_division"])
        self.assertEqual(conventions["target_parameters"], [99, 14, 1, 2])

    def test_source_multiplicities(self) -> None:
        dimensions = self.result["dimensions"]
        self.assertEqual(dimensions["order7_classes"], 208)
        self.assertEqual(dimensions["order8_classes"], 916)
        self.assertEqual(
            dimensions["vertex_source_multiplicity_total"], 208 * 7
        )
        self.assertEqual(
            dimensions["pair_source_multiplicity_total"], 208 * 42
        )

    def test_column_identities(self) -> None:
        identities = self.result["column_identities"]
        self.assertEqual(identities["classes_checked"], 916)
        self.assertTrue(identities["all_pass"])

    def test_micro_controls(self) -> None:
        controls = self.result["micro_controls"]
        self.assertEqual(
            controls["degree_empty7_to_one_edge8"]["coefficient"], 2
        )
        self.assertEqual(
            controls["nonedge_CN_empty7_to_path8"]["coefficient"], 2
        )
        self.assertEqual(
            controls["edge_CN_one_edge7_to_triangle8"]["coefficient"], 6
        )

    def test_rook_control(self) -> None:
        rook = self.result["rook_positive_control"]
        self.assertEqual(rook["parameters"], [9, 4, 1, 2])
        self.assertEqual(rook["order7_subset_total"], 36)
        self.assertEqual(rook["order8_subset_total"], 9)
        self.assertFalse(rook["vertex_row_failures"])
        self.assertFalse(rook["pair_row_failures"])
        self.assertTrue(rook["all_marked_rows_pass"])

    def test_zero_target_residual_support(self) -> None:
        residuals = self.result["target_residual_ranges"]
        self.assertGreaterEqual(residuals["vertex_min"], 0)
        self.assertGreaterEqual(residuals["pair_min"], 0)
        self.assertTrue(
            residuals["zero_pair_rows_have_zero_coefficient_support"]
        )


if __name__ == "__main__":
    unittest.main()
