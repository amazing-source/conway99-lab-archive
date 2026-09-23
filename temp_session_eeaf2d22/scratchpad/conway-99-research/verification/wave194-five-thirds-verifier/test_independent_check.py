from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave194_five_thirds_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave194FiveThirdsVerifierTests(unittest.TestCase):
    def test_type2_exact3_residual(self) -> None:
        result = CHECK.type2_exact3_residual_certificate()
        self.assertEqual(result["type2_translate_profiles"], [[6, 2], [2, 6]])
        self.assertEqual(result["translate_support_intersection_size"], 2)
        self.assertEqual(result["dual_distance_lower_bound"], 4)
        self.assertEqual(result["residual_exact_multiplicity"], [1, 3])

    def test_same_label_double_residual_distinctness(self) -> None:
        result = CHECK.type2_exact3_residual_certificate()
        self.assertIn("weight at most two", result["same_label_double_residuals_distinct"])
        self.assertIn("leaf coordinate", result["residual_differs_from_source_opposite_companion"])

    def test_complete_pool_collision_audit(self) -> None:
        result = CHECK.pool_collision_certificate()
        self.assertEqual(result["forced_residual_assignments"], "a2+c2+b3")
        self.assertEqual(
            result["old_exact3_combined_assignment_count"],
            "a2+a3+2b3+c2",
        )
        self.assertEqual(result["new_pool"]["label_capacity"], "y+3g")
        self.assertIn("2b3", result["RA"].replace("*", ""))

    def test_k_cancelled_low_target_row(self) -> None:
        result = CHECK.low_target_certificate()
        self.assertTrue(result["k_cancellation"])
        self.assertEqual(result["old_exact1_only_c1"].split()[0], "an")
        self.assertEqual(result["new_residual_low_capacity"], "y")
        self.assertNotIn("g", result["SL"])
        self.assertEqual(
            result["SL"], "n1+2n2+c1+2r2+y+2W-C>=0"
        )

    def test_exact_coefficient_identity(self) -> None:
        result = CHECK.coefficient_certificate()
        self.assertEqual(result["lower"], "3Q>=5C")
        self.assertEqual(result["nonedge_projective_Q"], 6930)
        self.assertIn("b3/2", result["identity"])

    def test_full_equality_face(self) -> None:
        result = CHECK.equality_face_certificate()
        self.assertEqual(result["parameter"], "m=n3, integer 0<=m<=1386")
        self.assertEqual(result["family"]["Q0"], 6930)
        self.assertIn("g", result["forced_zero"])
        self.assertFalse(
            result["asserted_to_be_graph_code_cover_or_circuit_family"]
        )
        self.assertEqual(
            [item["m"] for item in result["sample_rows"]], [0, 693, 1386]
        )

    def test_scope_boundary(self) -> None:
        result = CHECK.build_math_result()
        boundary = result["boundary"]
        self.assertEqual(result["verdict"], "VERIFIED_WITH_SCOPE")
        self.assertFalse(boundary["rank_11_excluded"])
        self.assertFalse(boundary["endpoint_excluded"])
        self.assertEqual(boundary["conway_99"], "UNKNOWN")

    def test_frozen_integrity(self) -> None:
        result = CHECK.verify_frozen_inputs()
        self.assertTrue(result["passed"])
        self.assertFalse(result["source_packages_opened_before_independent_freeze"])
        self.assertEqual(result["direct_files_checked"], 8)
        self.assertEqual(result["independent_result_entries_checked"], 1)

    def test_source_comparison(self) -> None:
        result = CHECK.source_comparison()
        self.assertTrue(result["RA_matches"])
        self.assertTrue(result["SL_and_k_cancellation_match"])
        self.assertTrue(result["equality_face_matches_after_parameter_reversal"])
        self.assertTrue(result["null_rows_arithmetic_only"])


if __name__ == "__main__":
    unittest.main()
