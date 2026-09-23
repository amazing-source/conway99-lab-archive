#!/usr/bin/env python3
"""Tests for the Wave 37 polar/code discovery checker."""

from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave37_polar_strengthen_exact_check", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave37PolarStrengthenTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        CHECK.verify_frozen_inputs()

    def test_ternary_code_structure(self) -> None:
        result = CHECK.ternary_code_consequences(12)
        code = result["code"]
        self.assertTrue(code["self_orthogonal"])
        self.assertTrue(code["all_one_vector_in_dual"])
        self.assertTrue(code["projective"])
        self.assertEqual(code["dual_distance_lower_bound"], 3)
        self.assertEqual(
            result["distinguished_words"]["composition_n1_n2"], [36, 33]
        )
        self.assertEqual(
            result["distinguished_words"]["nonzero_word_count_including_negatives"],
            462,
        )

    def test_schur_square_rank_boundary(self) -> None:
        at_twelve = CHECK.ternary_code_consequences(12)["schur_square"]
        self.assertEqual(at_twelve["rank_ceiling"], 78)
        self.assertEqual(at_twelve["orthogonality_matrix_rank_ceiling"], 79)
        hostile = CHECK.ternary_code_consequences(13)["schur_square"]
        self.assertEqual(hostile["rank_ceiling"], 91)

    def test_exact_delsarte_hostile_relaxation(self) -> None:
        result = CHECK.ternary_delsarte_relaxation()
        self.assertEqual(result["sum_A"], 3**12)
        self.assertEqual(result["A_69"], 462)
        self.assertEqual(result["B_1"], 0)
        self.assertEqual(result["B_2"], 0)
        self.assertTrue(result["all_real_B_nonnegative"])
        self.assertTrue(result["all_real_B_at_least_A"])
        self.assertFalse(result["is_formal_weight_enumerator"])
        self.assertEqual(result["nonintegral_B_orders"], list(range(3, 232)))

    def test_ternary_oriented_scheme_exact(self) -> None:
        result = CHECK.ternary_oriented_scheme()
        self.assertEqual(result["valencies"], [1, 1, 58806, 59048, 59048])
        self.assertEqual(
            result["endpoint_inner_distribution"], [1, 0, 162, 36, 32]
        )
        self.assertEqual(
            [item["display"] for item in result["delsarte_positivity"]],
            ["231", "249/121", "123/121", "4767/7381", "60/61"],
        )
        self.assertFalse(result["excluded"])

    def test_divisibility_refines_but_does_not_exclude(self) -> None:
        result = CHECK.divisibility_refined_evans()
        self.assertEqual(result["outside_degree_sum"], 6754671)
        self.assertEqual(result["outside_degree_square_sum"], 523215693)
        self.assertEqual(
            result["ordinary_consecutive_integer_polynomial"],
            {"root_pair": [76, 77], "sum": 6020322},
        )
        self.assertEqual(
            result["divisibility_refined_polynomial"],
            {"root_pair": [75, 78], "sum": 5843880},
        )
        self.assertFalse(result["excluded"])

    def test_characteristic_polynomial_helper(self) -> None:
        # det(xI-[[1,2],[3,4]]) = x^2-5x-2.
        self.assertEqual(
            CHECK.characteristic_polynomial([[1, 2], [3, 4]]),
            [-2, -5, 1],
        )

    def test_q7_square_rank_eleven_scheme(self) -> None:
        result = CHECK.q7_projective_scheme(1)
        self.assertEqual(result["vertex_count"], 141229221)
        self.assertEqual(result["valencies"][1], 20178004)
        self.assertFalse(result["is_strongly_regular"])
        self.assertEqual(
            result["largest_nonprincipal_eigenvalue"],
            "2401*(1+sqrt(2))",
        )
        self.assertFalse(result["excluded"])

    def test_q7_nonsquare_rank_eleven_scheme(self) -> None:
        result = CHECK.q7_projective_scheme(3)
        self.assertEqual(result["vertex_count"], 141246028)
        self.assertEqual(result["valencies"][1], 20175603)
        self.assertFalse(result["is_strongly_regular"])
        self.assertEqual(result["largest_nonprincipal_eigenvalue"], "4802")
        self.assertFalse(result["excluded"])

    def test_q7_graph_is_not_srg_hostile_boundary(self) -> None:
        for determinant_class in (1, 3):
            result = CHECK.q7_projective_scheme(determinant_class)
            common = result["common_orthogonal_neighbors_by_relation"]
            self.assertGreater(len(set(common[2:])), 1)

    def test_signed_triangle_correction_and_new_count(self) -> None:
        result = CHECK.signed_triangle_geometry()
        self.assertEqual(result["balanced_minus_unbalanced_triangles"], 34034)
        self.assertEqual(result["maximum_collinear_selected_triples"], 2618)
        self.assertEqual(
            result["minimum_linearly_independent_balanced_triples"], 31416
        )
        self.assertEqual(result["minimum_distinct_degenerate_three_spaces"], 437)
        self.assertIn("does not imply", result["false_inference_refuted"])

    def test_boundary_rank_dichotomy(self) -> None:
        result = CHECK.boundary_rank_dichotomy()
        self.assertEqual(
            result["surviving_pair_count_after_wave36_bounds_and_parity"], 561
        )
        self.assertEqual(result["if_r3_equals_12"]["r7_minimum"], 12)
        self.assertEqual(result["if_r7_equals_11"]["r3_minimum"], 13)

    def test_top_level_status_stays_unknown(self) -> None:
        result = CHECK.build_results()
        conclusion = result["conclusion"]
        self.assertFalse(conclusion["new_rank_lower_bound"])
        self.assertFalse(conclusion["new_determinant_class_exclusion"])
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["upper_bound_improved_below_4158"])
        self.assertEqual(conclusion["target_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
