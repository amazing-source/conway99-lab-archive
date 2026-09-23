from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Wave53IndependentVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checker = load_module(
            "wave53_independent_check_test", HERE / "independent_check.py"
        )
        cls.comparator = load_module(
            "wave53_postinspection_comparison_test",
            HERE / "postinspection_comparison.py",
        )
        cls.sealed = json.loads(
            (HERE / "independent-result.json").read_text(encoding="utf-8")
        )
        cls.sealed_comparison = json.loads(
            (HERE / "comparison-result.json").read_text(encoding="utf-8")
        )
        cls.replayed = cls.checker.verify()
        cls.replayed_comparison = cls.comparator.compare()

    def test_full_exact_replay_is_deterministic_except_live_memory(self) -> None:
        expected = copy.deepcopy(self.sealed)
        actual = copy.deepcopy(self.replayed)
        expected.pop("resource_guard")
        actual.pop("resource_guard")
        self.assertEqual(actual, expected)
        self.assertTrue(self.replayed["resource_guard"]["passed"])

    def test_postinspection_comparison_is_deterministic(self) -> None:
        self.assertEqual(self.replayed_comparison, self.sealed_comparison)

    def test_preinspection_freeze_is_intact(self) -> None:
        result = self.checker.verify_manifest(
            HERE / "preinspection-freeze.sha256", forbid_self=True
        )
        self.assertEqual(result["entry_count"], 16)
        self.assertTrue(result["all_match"])

    def test_exact_rational_parser_rejects_approximate_boundaries(self) -> None:
        self.assertEqual(self.checker.parse_fraction("3/4"), Fraction(3, 4))
        self.assertEqual(self.checker.parse_fraction(-2), Fraction(-2))
        for value in (True, 1.0, "1.0", "1e-3", "1/0", "01", "+1", "1/-2"):
            with self.assertRaises((TypeError, ValueError, ZeroDivisionError)):
                self.checker.parse_fraction(value)

    def test_all_four_witnesses_and_raw_cumulative_cuts(self) -> None:
        expected_supports = [136, 132, 136, 138]
        for iteration, support in zip(
            self.sealed["iterations"], expected_supports, strict=True
        ):
            self.assertEqual(iteration["witness"]["support_size"], support)
            self.assertTrue(iteration["witness"]["all_residuals_zero"])
            self.assertTrue(iteration["witness"]["all_208_counts_nonnegative"])
            self.assertTrue(iteration["witness"]["y_bounds_satisfied"])
            self.assertTrue(iteration["cuts"]["all_nonnegative"])
        raw = self.sealed_comparison["exact_raw_174_to_177_cut_replay"]
        self.assertTrue(raw["all_reported_scalings_and_slacks_match"])
        self.assertEqual(
            [record["cut_count"] for record in raw["iterations"]],
            [174, 175, 176, 177],
        )

    def test_three_wave49_cuts_are_reconstructed_and_reject_sources(self) -> None:
        expected = ["root_220", "root_62", "root_221"]
        additions = [
            iteration["added_cut"]
            for iteration in self.sealed["iterations"]
            if iteration["added_cut"] is not None
        ]
        self.assertEqual([cut["selected_family"] for cut in additions], expected)
        for cut in additions:
            self.assertTrue(cut["direction_equal"])
            self.assertTrue(cut["reconstructed_coefficients_equal"])
            self.assertTrue(cut["linearization_multiplier_equal"])
            self.assertTrue(cut["reported_matrix_value_equal"])
            self.assertTrue(cut["reported_source_value_equal"])
            self.assertTrue(cut["exactly_rejects_source"])
            self.assertTrue(cut["selected_by_correct_exact_rule"])

    def test_correct_matrix_census_refutes_all_128_indefinite_claim(self) -> None:
        totals = self.sealed["matrix_totals"]
        self.assertEqual(totals["checks"], 128)
        self.assertEqual(totals["reported_quadratics_matching_correct_matrices"], 116)
        self.assertEqual(totals["independently_indefinite"], 120)
        self.assertEqual(totals["independently_psd"], 8)
        corrections = self.sealed["corrections"]
        self.assertEqual(len(corrections), 12)
        self.assertEqual({item["layer"] for item in corrections}, {"wave45"})
        self.assertEqual(
            sum(item["correct_status"] == "EXACTLY_PSD" for item in corrections),
            8,
        )

    def test_double_offdiagonal_defect_is_reproduced_exactly(self) -> None:
        defect = self.sealed_comparison["wave45_double_offdiagonal_defect"]
        self.assertEqual(defect["checks"], 12)
        self.assertTrue(defect["all_source_matrices_and_quadratics_reproduced"])
        hashes = self.sealed_comparison["hash_checks"]["matrices"]
        self.assertEqual(hashes["checks"], 128)
        self.assertEqual(hashes["reported_hashes_matching_correct_matrices"], 116)

    def test_duplicate_normalization_attack(self) -> None:
        baseline = self.sealed["baseline_174_cut_reconstruction"]
        self.assertEqual(
            baseline["semantic_duplicate_count_after_primitive_normalization"], 68
        )
        self.assertEqual(baseline["semantic_duplicate_group_count"], 34)
        for iteration in self.sealed_comparison[
            "candidate_deduplication_and_selection"
        ]:
            self.assertEqual(iteration["unique_normalized_candidate_rows"], 28)
            self.assertEqual(
                iteration["unique_normalized_rows_rejecting_correct_source_matrix"],
                25,
            )
            self.assertTrue(
                iteration["selected_cut_still_minimizes_correct_exact_rule"]
            )

    def test_excluded_fourth_cut_is_not_a_farkas_certificate(self) -> None:
        fourth = self.sealed_comparison["excluded_fourth_dense_wave45_cut"]
        self.assertEqual(fourth["source_bug_nonzero_coefficients"], 208)
        self.assertLess(Fraction(fourth["source_bug_cut_value"]), 0)
        self.assertGreater(Fraction(fourth["correct_cut_value"]), 0)
        self.assertFalse(fourth["exact_farkas_certificate"])
        self.assertFalse(fourth["exact_multiplier_certificate_in_discovery_package"])

    def test_status_wall(self) -> None:
        conclusion = self.sealed_comparison["conclusion"]
        self.assertEqual(
            conclusion["fixed_177_cut_rational_relaxation"],
            "VERIFIED_EXACTLY_FEASIBLE",
        )
        self.assertEqual(conclusion["all_128_matrices_exactly_indefinite"], "REFUTED")
        self.assertEqual(conclusion["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(conclusion["strict_upper_bound_below_4158"], "NOT_PROVED")
        self.assertEqual(conclusion["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
