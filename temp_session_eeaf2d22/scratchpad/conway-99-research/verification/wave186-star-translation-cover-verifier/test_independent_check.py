from __future__ import annotations

import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import independent_check as check  # noqa: E402


class Wave186IndependentTests(unittest.TestCase):
    def test_direct_frozen_manifests(self) -> None:
        result = check.verify_direct_freeze()
        self.assertTrue(result["passed"], result["failures"])
        self.assertEqual(len(result["lists_checked"]), 6)
        paths = {row["path"] for row in result["lists_checked"]}
        self.assertIn(
            "attempts/wave186-star-translation-cover/package-manifest.sha256",
            paths,
        )
        self.assertIn(
            "verification/wave181-c4-conic-equality/package-manifest.sha256",
            paths,
        )

    def test_multiplicity_two_translates(self) -> None:
        result = check.multiplicity_two_translation()
        self.assertEqual(result["conic_profile"], [2, 2])
        self.assertEqual(result["translate_profiles"], [[6, 2], [2, 6]])
        self.assertEqual(result["translate_weights"], [8, 8])
        self.assertEqual(result["translated_support_intersection"], 2)
        self.assertTrue(result["cross_circuit_forced_by_proper_star_independence"])
        self.assertTrue(result["translated_circuits_distinct_by_dual_distance_four"])
        self.assertEqual(result["forced_other_circuits_per_label"], 2)

    def test_multiplicity_three_leaf_translate(self) -> None:
        result = check.multiplicity_three_translation()
        self.assertEqual(result["companion_weights"], [4, 5])
        self.assertEqual(result["leaf_translate_profile"], [3, 6])
        self.assertEqual(result["leaf_translate_weight"], 9)
        self.assertFalse(result["leaf_translate_contains_T"])
        self.assertEqual(result["conic_translate_intersection"], 3)
        self.assertEqual(result["companion_translate_intersection"], 0)
        self.assertTrue(result["translate_distinct_from_both_companions"])
        self.assertEqual(result["forced_other_circuits_per_label"], 2)

    def test_private_assignment_allows_maximum_overlap(self) -> None:
        result = check.cover_certificate()
        assignment = result["outside_assignment"]
        self.assertEqual(assignment["assignments_per_private_label"], 2)
        self.assertEqual(assignment["maximum_assignments_per_outside_circuit"], 3)
        self.assertTrue(assignment["repeated_companions_and_translates_allowed"])
        self.assertTrue(assignment["same_circuit_label_double_charge_excluded"])
        self.assertTrue(
            result["triple_companions"]["may_overlap_private_assignment_pool"]
        )

    def test_coefficient_certificate(self) -> None:
        result = check.cover_certificate()
        rows = result["coefficient_rows_O_n1_n2_n3_C"]
        self.assertEqual(rows["private_assignment"], [6, 8, 8, 12, -8])
        self.assertEqual(rows["triple_companion"], [3, 1, 1, -3, 0])
        self.assertEqual(rows["sum"], [9, 9, 9, 9, -8])

    def test_exact_lower_bounds(self) -> None:
        result = check.cover_certificate()
        self.assertEqual(result["nonedge_projective_lower"], 3696)
        self.assertEqual(result["edge_isolated_projective"], 693)
        self.assertEqual(result["total_projective_lower"], 4389)
        self.assertEqual(result["dual_short_word_lower"], 8778)
        hostile = result["arithmetic_equality_control_not_construction"]
        self.assertEqual(3 * hostile["O"], 2 * hostile["p"])
        self.assertEqual(hostile["O"], hostile["n3"])

    def test_deterministic_and_discovery_independent(self) -> None:
        first = check.build_result()
        second = check.build_result()
        self.assertEqual(check.canonical_json(first), check.canonical_json(second))
        self.assertFalse(first["source_checker_imported_or_executed"])
        self.assertTrue(first["former_equality_Q_2079_excluded"])
        self.assertEqual(first["global_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
