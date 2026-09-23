"""Hostile controls for the Wave145 independent aggregation audit."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_verify as verify  # noqa: E402


class IndependentWave145Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verify.build_results()

    def test_discovery_package_and_inputs_are_frozen(self) -> None:
        self.assertTrue(self.result["frozen_inputs"]["pass"])
        package = self.result["sealed_discovery_package"]
        self.assertEqual(package["entry_count"], 12)
        self.assertTrue(package["manifest_pass"])
        self.assertTrue(package["entries_pass"])

    def test_exactly_five_state_collisions_require_sum(self) -> None:
        rows = self.result["aggregation"]["collisions_requiring_sum"]
        self.assertEqual(
            [tuple(row["state"]) for row in rows],
            [
                (84, 0, 15),
                (73, 0, 26),
                (66, 0, 33),
                (62, 0, 37),
                (60, 0, 39),
            ],
        )
        self.assertEqual(
            [row["correct_sum_lower"] for row in rows],
            [198, 8316, 149688, 55440, 462],
        )
        self.assertTrue(
            all(
                row["correct_sum_lower"] > row["discovery_max_lower"]
                for row in rows
            )
        )

    def test_nonzero_families_are_pairwise_disjoint(self) -> None:
        aggregation = self.result["aggregation"]
        self.assertTrue(aggregation["all_nonzero_families_pairwise_disjoint"])
        self.assertTrue(
            all(
                row["mixed_vs_pure_X_disjoint"]
                and row["mixed_vs_pure_Y_disjoint"]
                for row in aggregation["family_disjointness_checks"]
            )
        )

    def test_zero_word_is_not_summed(self) -> None:
        aggregation = self.result["aggregation"]
        self.assertEqual(aggregation["discovery_zero_state_lower"], 1)
        self.assertEqual(aggregation["correct_zero_state_lower"], 1)
        self.assertTrue(aggregation["zero_is_not_double_counted"])

    def test_minimum_eight_does_not_zero_8_10_12(self) -> None:
        audit = self.result["pure_Y_zero_audit"]
        self.assertEqual(audit["verified_image_minimum_lower"], 8)
        self.assertEqual(audit["minimum_forces_zero"], [2, 4, 6])
        self.assertEqual(audit["unsupported_from_minimum_eight"], [8, 10, 12])
        self.assertEqual(audit["correct_zero_weights"], [2, 4, 6, 94, 96, 98])

    def test_high_image_zeros_have_independent_row_union_proof(self) -> None:
        rows = self.result["pure_Y_zero_audit"]["high_weight_checks"]
        self.assertEqual(
            [
                (
                    row["image_weight"],
                    row["complement_weight"],
                    row["row_union_upper"],
                )
                for row in rows
            ],
            [(94, 5, 70), (96, 3, 42), (98, 1, 14)],
        )
        self.assertTrue(all(row["contradiction"] for row in rows))

    def test_shadow_transform_matches_explicit_cosets(self) -> None:
        audit = self.result["quantum_shadow_audit"]
        self.assertEqual(audit["graphs_checked"], 1099)
        self.assertEqual(audit["transform_coefficients_checked"], 6504)
        self.assertEqual(audit["failure_count"], 0)
        self.assertTrue(audit["formula_and_normalization_pass"])
        self.assertEqual(
            audit["triangle_control"],
            {
                "ordinary": [1, 0, 3, 4],
                "explicit_shadow": [0, 3, 0, 5],
                "transformed_shadow": [0, 3, 0, 5],
            },
        )

    def test_status_is_not_inflated(self) -> None:
        self.assertEqual(
            self.result["verdict"]["wave139_max_aggregation"],
            "REFUTED_UNDERCOUNT",
        )
        self.assertEqual(
            self.result["status_wall"]["corrected_formal_enumerator_feasibility"],
            "UNKNOWN",
        )
        self.assertEqual(self.result["status_wall"]["Conway_99"], "UNKNOWN")
        self.assertTrue(self.result["verdict"]["all_audit_checks_pass"])


if __name__ == "__main__":
    unittest.main()
