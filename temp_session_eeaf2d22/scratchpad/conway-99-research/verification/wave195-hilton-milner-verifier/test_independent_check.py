from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave195_hilton_milner_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave195HiltonMilnerVerifierTests(unittest.TestCase):
    def test_exact_three_flag_relation(self) -> None:
        result = CHECK.exact_three_flag_certificate()
        self.assertEqual(result["star_ground_set_size"], 7)
        self.assertEqual(result["A_size"], 3)
        self.assertTrue(result["one_flag_one_companion_pair"])

    def test_injectivity_and_pairwise_intersection(self) -> None:
        injection = CHECK.exact_three_flag_certificate()
        intersection = CHECK.pairwise_intersection_certificate()
        self.assertIn("weight-two", injection["same_center_same_A_injective"])
        self.assertEqual(intersection["contradiction_weight"], 3)
        self.assertEqual(intersection["dual_distance_lower_bound"], 4)

    def test_hilton_milner_specialization(self) -> None:
        result = CHECK.hilton_milner_certificate()
        self.assertTrue(result["theorem_hypotheses"]["pairwise_intersecting"])
        self.assertTrue(result["theorem_hypotheses"]["empty_total_intersection"])
        self.assertEqual(result["calculation"], "C(6,2)-C(3,2)+1=15-3+1=13")
        self.assertEqual(result["bound"], 13)

    def test_common_star_branch(self) -> None:
        result = CHECK.common_star_certificate()
        self.assertEqual(result["c_x_upper"], 15)
        self.assertIn("distinct leaf types", result["six_incidence_simplicity"])
        self.assertEqual(result["j_x_upper"], "12+12+c_x<=39")
        self.assertEqual(result["universal_j_x_upper"], 39)

    def test_oriented_label_lower_bound(self) -> None:
        result = CHECK.oriented_label_certificate()
        self.assertIn("opposite centers", result["b3_injection"])
        self.assertIn("different underlying", result["different_sources"])
        self.assertIn("cannot occur", result["outside_U"])
        self.assertEqual(
            result["lower"], "J>=|U|+a3+b3>=C-n1-2n2+a3+b3"
        )
        self.assertEqual(result["SG"], "n1+2n2-a3-b3-C/14>=0")

    def test_inherited_pool_separation(self) -> None:
        result = CHECK.inherited_pool_separation_certificate()
        self.assertTrue(result["all_relevant_exact3_flags_form_one_simple_family"])
        self.assertIn("distinct flags", result["flag_injectivity_across_pools"])

    def test_exact_certificate(self) -> None:
        result = CHECK.coefficient_certificate()
        self.assertEqual(result["lower"], "Q>=47C/28")
        self.assertEqual(result["exact_rational_lower"], "13959/2")
        self.assertIn("SG/6", result["identity"])
        self.assertIn("SE2/6", result["identity"])

    def test_integer_rounding_and_counts(self) -> None:
        result = CHECK.build_math_result()["bounds"]
        self.assertEqual(result["nonedge_projective_short_circuits_Q"], 6980)
        self.assertEqual(result["all_projective_short_circuits"], 7673)
        self.assertEqual(result["scalar_short_circuit_words"], 15346)

    def test_rational_null_is_not_object(self) -> None:
        result = CHECK.rational_null_control()
        self.assertEqual(result["Q0"], "13959/2")
        self.assertFalse(result["integral_at_C_4158"])
        self.assertFalse(
            result["asserted_to_be_graph_code_cover_or_flag_family"]
        )
        self.assertTrue(
            all(value == 0 for value in result["zero_certificate_slacks"].values())
        )

    def test_failed_route_quarantine(self) -> None:
        result = CHECK.failed_route_quarantine()
        self.assertEqual(result["status"], "QUARANTINED_FAILED_ROUTE")
        self.assertFalse(result["used_in_certificate"])
        self.assertIn("exactly one", result["safe_use"])

    def test_frozen_integrity_and_sources(self) -> None:
        integrity = CHECK.verify_frozen_inputs()
        comparison = CHECK.source_comparison()
        self.assertTrue(integrity["passed"])
        self.assertEqual(integrity["direct_files_checked"], 10)
        self.assertFalse(integrity["source_packages_opened_before_independent_freeze"])
        self.assertTrue(comparison["oriented_b3_and_J_rows_match"])
        self.assertTrue(comparison["failed_mixed_type1_route_quarantined"])

    def test_scope_boundary(self) -> None:
        result = CHECK.build_math_result()
        self.assertEqual(result["verdict"], "VERIFIED_WITH_SCOPE")
        self.assertFalse(result["boundary"]["rank_11_excluded"])
        self.assertFalse(result["boundary"]["endpoint_excluded"])
        self.assertEqual(result["boundary"]["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
