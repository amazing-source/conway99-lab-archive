from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave120_independent", HERE / "independent_check.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave120IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.independent_results()

    def test_frozen_packages_and_verified_wave96(self) -> None:
        provenance = self.result["provenance"]
        self.assertEqual(
            provenance["manifest_entry_counts"],
            {
                "attempts/wave120-fixedc4-sumdiff/package-manifest.sha256": 10,
                "verification/wave96-norm16-norm18-upper/package-manifest.sha256": 8,
                "verification/wave112-c4-short-vector-incidence/package-manifest.sha256": 8,
            },
        )
        self.assertEqual(
            provenance["wave96_norm20_source"],
            "VERIFIED_CONDITIONAL_ON_FROZEN_INPUTS",
        )

    def test_projector_real_minimum(self) -> None:
        row = self.result["projector"]
        self.assertEqual(row["unit_alternating_real_minimum"], "28/5")
        self.assertEqual(row["doubled_alternating_real_minimum"], "112/5")
        self.assertFalse(row["real_minimum_is_integral_attainment"])
        self.assertEqual(row["coordinate_kernel_dimension"], 40)

    def test_integer_anchor_bound(self) -> None:
        row = self.result["integer_anchor_bound"]
        self.assertEqual(row["r2_squared_norm_lower"], 32)
        self.assertEqual(row["general_squared_norm_lower"], "4*r^2+8*r")
        self.assertEqual(row["sample_values_r1_through_r40"]["40"], 6720)
        self.assertEqual(row["actual_norm32_eigenvector_exists"], "UNKNOWN")

    def test_all_six_pair_intervals(self) -> None:
        rows = self.result["pairwise_intervals"]
        self.assertEqual(
            [row["integer_inner_product_interval"] for row in rows],
            [[0, 9], [-1, 10], [-2, 11], [-2, 11], [-3, 12], [-4, 13]],
        )
        for row in rows:
            left, right = row["norm_pair"]
            lower, upper = row["integer_inner_product_interval"]
            self.assertGreaterEqual(left + right + 2 * lower, 32)
            self.assertGreaterEqual(left + right - 2 * upper, 14)

    def test_witness_types_anchors_and_pairs(self) -> None:
        row = self.result["formal_witness"]
        self.assertEqual(row["record_count"], 40)
        self.assertTrue(row["records_distinct"])
        self.assertEqual(row["ambient_binary_length"], 99)
        self.assertEqual(row["unused_type11_coordinates"], 4)
        self.assertTrue(row["all_four_anchor_equations_checked_per_record"])
        self.assertEqual(
            row["overlap_histogram"],
            {"0": 92, "1": 230, "2": 222, "3": 157, "4": 62, "5": 17},
        )
        self.assertEqual(
            row["difference_norm_histogram"],
            {"14": 17, "16": 62, "18": 157, "20": 222, "22": 230, "24": 92},
        )
        self.assertEqual(row["opposite_sign_overlap_maximum"], 0)

    def test_subset_and_binary_constraints(self) -> None:
        row = self.result["formal_witness"]
        self.assertEqual(row["binary_minimum_distance"], 14)
        subset = row["positive_subset_inequality"]
        self.assertTrue(subset["proof_applies_to_every_positive_subset"])
        self.assertEqual(subset["formal_support_squared_norm_lower"], "4*r^2+12*r")
        self.assertEqual(row["full_family"]["squared_norm"], 9836)
        self.assertEqual(row["full_family"]["anchor_lower"], 6720)

    def test_residual_gram_exact_PD_and_rank(self) -> None:
        row = self.result["formal_witness"]["residual_gram"]
        self.assertEqual(row["size"], 40)
        self.assertEqual(row["rank"], 40)
        self.assertTrue(row["positive_definite_by_sylvester"])
        determinants = [int(value) for value in row["leading_principal_determinants"]]
        self.assertEqual(len(determinants), 40)
        self.assertTrue(all(value > 0 for value in determinants))
        self.assertEqual(
            row["normalized_inner_products"],
            ["-2/13", "-3/52", "1/26", "7/52", "3/13", "17/52"],
        )

    def test_hostile_record_and_anchor_mutations_fail(self) -> None:
        raw = json.loads(
            (CHECK.DISCOVERY / "witness.json").read_text(encoding="utf-8")
        )
        duplicate = json.loads(json.dumps(raw))
        duplicate["records"][1] = duplicate["records"][0]
        with self.assertRaises(AssertionError):
            CHECK.normalize_records(duplicate)

        records = CHECK.normalize_records(raw)
        vector = CHECK.signed_record(records[0])
        coordinate = next(
            coordinate
            for coordinate in vector
            if coordinate[0] == "outside" and coordinate[1] == 3
        )
        vector[coordinate] = 1
        with self.assertRaises(AssertionError):
            CHECK.anchor_equations(vector)

    def test_hostile_non_PD_matrix_fails_sylvester(self) -> None:
        determinants = CHECK.bareiss_leading_determinants([[1, 0], [0, -1]])
        self.assertEqual(determinants, [1, -1])
        self.assertFalse(all(value > 0 for value in determinants))

    def test_evidence_boundary(self) -> None:
        boundary = self.result["evidence_boundary"]
        self.assertTrue(boundary["witness_is_formal_relaxation_only"])
        self.assertFalse(boundary["witness_is_integer_eigenvector_family"])
        self.assertEqual(boundary["cap25"], "UNKNOWN")
        self.assertEqual(boundary["cap24"], "UNKNOWN")
        self.assertEqual(boundary["rank28"], "UNKNOWN")
        self.assertEqual(boundary["rank30"], "UNKNOWN")
        self.assertEqual(boundary["Conway_99"], "UNKNOWN")

    def test_archived_result_replays(self) -> None:
        archived = json.loads(
            (HERE / "independent-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(archived, self.result)


if __name__ == "__main__":
    unittest.main()
