from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave120_exact", HERE / "exact_check.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave120ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.exact_results()

    def test_projector_affine_minima(self) -> None:
        row = self.result["projector_affine_slice"]
        self.assertEqual(row["unit_alternating_minimum_squared_norm"], "28/5")
        self.assertEqual(
            row["doubled_alternating_minimum_squared_norm"], "112/5"
        )
        gram, inverse = MODULE.c4_projector()
        self.assertEqual(
            MODULE.multiply(gram, inverse),
            [
                [Fraction(i == j) for j in range(4)]
                for i in range(4)
            ],
        )

    def test_integer_anchor_sharpening(self) -> None:
        row = self.result["integer_anchor_sharpening"]
        self.assertEqual(row["universal_squared_norm_lower"], 32)
        profile = row["local_relaxation_equality_profile"]
        self.assertEqual(
            sum(value * value for value in profile["cycle_coordinates"])
            + profile["outside_positive_units"]
            + profile["outside_negative_units"],
            32,
        )
        self.assertEqual(row["positive_r_fold_sum_lower"], "4*r^2+8*r")

    def test_pairwise_interval_table(self) -> None:
        rows = self.result["pairwise_inner_products"]["rows"]
        self.assertEqual(
            [row["inner_product_interval"] for row in rows],
            [[0, 9], [-1, 10], [-2, 11], [-2, 11], [-3, 12], [-4, 13]],
        )
        for row in rows:
            left, right = row["norm_pair"]
            lower, upper = row["inner_product_interval"]
            self.assertGreaterEqual(left + right + 2 * lower, 32)
            self.assertGreaterEqual(left + right - 2 * upper, 14)

    def test_formal_witness_histograms(self) -> None:
        row = self.result["formal_pairwise_witness"]
        self.assertEqual(row["family_size"], 40)
        self.assertEqual(
            row["overlap_histogram"],
            {"0": 92, "1": 230, "2": 222, "3": 157, "4": 62, "5": 17},
        )
        self.assertEqual(
            row["difference_norm_histogram"],
            {"14": 17, "16": 62, "18": 157, "20": 222, "22": 230, "24": 92},
        )
        self.assertEqual(sum(row["overlap_histogram"].values()), 780)
        self.assertEqual(row["total_pair_inner_product"], 4598)
        self.assertEqual(row["full_family_sum_squared_norm"], 9836)
        self.assertEqual(row["full_family_anchor_lower"], 6720)
        self.assertTrue(row["every_positive_subset_anchor_lower_satisfied"])

    def test_gram_and_code_null_control(self) -> None:
        row = self.result["formal_pairwise_witness"]
        self.assertTrue(row["residual_gram_positive_definite"])
        self.assertEqual(row["residual_gram_rank"], 40)
        self.assertEqual(row["binary_support_minimum_distance"], 14)
        self.assertGreater(row["family_size"], 25)
        null = self.result["null_control"]
        self.assertFalse(
            null[
                "derived_norm_profile_PSD_or_Gram_relaxation_can_prove_either_cap"
            ]
        )
        self.assertFalse(
            null[
                "binary_minimum_distance_or_constant_weight_Delsarte_can_prove_either_cap"
            ]
        )

    def test_archived_result_replays(self) -> None:
        archived = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(archived, self.result)

    def test_status_wall(self) -> None:
        status = self.result["status"]
        self.assertFalse(status["rank28_excluded"])
        self.assertFalse(status["rank30_excluded"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
