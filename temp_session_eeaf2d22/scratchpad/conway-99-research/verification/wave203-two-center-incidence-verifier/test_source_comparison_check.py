from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("source_comparison_check.py")
SPEC = importlib.util.spec_from_file_location("wave203_source_comparison", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave203SourceComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_result()

    def test_sealed_hashes(self) -> None:
        self.assertEqual(
            self.result["sources"]["primary"]["manifest_sha256"],
            "b412cce1a737b3b50718aabb399978ca2956cea0edbbe1c1f955f8083447d5b8",
        )
        self.assertEqual(
            self.result["sources"]["hostile"]["manifest_sha256"],
            "62019dec2c954b2354279afd4dc114daffafbef0bff3678ddca2fcb61cb1edb8",
        )

    def test_local_geometry_agreement(self) -> None:
        agreement = self.result["agreement"]
        self.assertTrue(agreement["third_block_map_is_partial_injection"])
        self.assertTrue(agreement["reverse_matching_uses_j_eq_2"])
        self.assertTrue(agreement["four_c4_columns_distinct"])

    def test_relation_and_gram_agreement(self) -> None:
        agreement = self.result["agreement"]
        self.assertEqual(
            agreement["global_relation_coefficients"],
            [[1, 2, 2, 2, 0, 0], [2, 1, 0, 0, 2, 2]],
        )
        self.assertTrue(agreement["all_equal_rejected_by_wave181_gram"])

    def test_capacity_and_no_promotion(self) -> None:
        agreement = self.result["agreement"]
        self.assertEqual(agreement["combined_full_flag_capacity"], 5)
        self.assertEqual(agreement["combined_selected_capacity"], 5)
        self.assertFalse(agreement["Q_ge_7060_without_b_positive"])

    def test_no_repair(self) -> None:
        comparison = self.result["comparison"]
        self.assertFalse(comparison["mathematical_discrepancy"])
        self.assertFalse(comparison["repair_needed"])


if __name__ == "__main__":
    unittest.main()
