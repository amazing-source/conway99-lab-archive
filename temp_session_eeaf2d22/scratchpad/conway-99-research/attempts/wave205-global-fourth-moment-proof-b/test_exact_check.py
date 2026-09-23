"""Hostile and exact tests for the Wave 205 proof-B package."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave205_global_fourth", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave205GlobalFourthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = CHECK.analyze()
        CHECK.verify(cls.data)

    def test_frozen_inputs(self) -> None:
        self.assertEqual(CHECK.verify_inputs(), CHECK.EXPECTED_INPUTS)

    def test_operator_dimensions_are_not_representation_dimensions(self) -> None:
        dimensions = self.data["dimension_ledger"]
        self.assertEqual(dimensions["wedge2_V_dimension"], 55)
        self.assertEqual(
            dimensions["self_adjoint_End_wedge2_V_dimension"], 1540
        )
        self.assertEqual(dimensions["Sym2_V_dimension"], 66)
        self.assertEqual(
            dimensions["self_adjoint_End_Sym2_V_dimension"], 2211
        )
        self.assertGreater(
            dimensions["quadratic_feature_Sym2_of_trace_zero_dimension"], 99
        )

    def test_actual_star_pair_feature_has_full_rank(self) -> None:
        feature = self.data["actual_incidence_factorization"][
            "star_pair_feature_control"
        ]
        self.assertEqual(feature["unit_witness_columns"], 99)
        self.assertEqual(feature["unit_witness_matrix_rank"], 99)
        self.assertEqual(feature["star_pair_feature_rank"], 99)

    def test_feature_sum_is_quadratic_not_linear(self) -> None:
        feature = self.data["actual_incidence_factorization"][
            "star_pair_feature_control"
        ]
        self.assertEqual(feature["sum_feature_on_diagonal_pair"], 0)
        self.assertEqual(
            feature["sum_feature_on_distinct_intersecting_pair"], 1
        )
        self.assertEqual(feature["sum_feature_identity"], "sum_x u_x=vec(Q), Q=B^T B over F_3")

    def test_toy_fourth_factorization_and_row_localizer(self) -> None:
        toy = self.data["actual_incidence_factorization"]["toy_exact_replay"]
        self.assertTrue(toy["direct_equals_U_K_U_transpose"])
        self.assertTrue(toy["sum_feature_equals_vec_Q"])
        self.assertTrue(toy["line_vector_norm_identity"])
        self.assertEqual(len(toy["row_sums"]), 7)

    def test_relaxed_incidence_control_is_not_target_srg(self) -> None:
        feature = self.data["actual_incidence_factorization"][
            "star_pair_feature_control"
        ]
        self.assertEqual(feature["control_point_degrees"], {"14": 99})
        self.assertFalse(feature["control_is_srg_99_14_1_2"])
        self.assertNotEqual(
            feature["control_adjacent_common_neighbor_distribution"], {"1": 693}
        )

    def test_99_projectors_have_exact_local_star_geometry(self) -> None:
        control = self.data["positive_control"]
        self.assertEqual(control["projector_labels"], 99)
        self.assertEqual(control["ambient_form_discriminant"], 2)
        self.assertTrue(control["sum_projectors_zero"])
        each = control["each_projector"]
        self.assertEqual(each["rank"], 6)
        self.assertEqual(each["trace"], 0)
        self.assertTrue(each["seven_singular_simplex_columns"])
        self.assertEqual(each["simplex_gram"], "J_7-I_7")

    def test_sum_projectors_does_not_force_fourth_row_sum(self) -> None:
        control = self.data["positive_control"]
        self.assertEqual(control["pair_trace_row_sum_distribution"], {"0": 99})
        self.assertEqual(
            control["fourth_trace_row_sum_distribution"],
            {"0": 6, "1": 91, "2": 2},
        )
        self.assertEqual(
            control["quadratic_projector_moment_nonzero_coordinates"], 302
        )

    def test_pair_and_fourth_moments_separate(self) -> None:
        control = self.data["positive_control"]
        self.assertEqual(control["pair_trace_matrix_rank"], 8)
        self.assertEqual(control["fourth_trace_matrix_rank"], 9)
        self.assertEqual(
            control["ordered_entries_where_pair_and_fourth_trace_differ"], 740
        )

    def test_failed_target_premises_are_explicit(self) -> None:
        failed = self.data["positive_control"]["failed_target_premises"]
        self.assertGreaterEqual(len(failed), 6)
        self.assertTrue(any("231 projectively distinct" in item for item in failed))
        self.assertTrue(any("not an srg" in item for item in failed))

    def test_hostile_status_mutation_is_rejected(self) -> None:
        mutated = json.loads(json.dumps(self.data))
        mutated["conclusions"]["endpoint_excluded"] = True
        with self.assertRaises(AssertionError):
            CHECK.verify(mutated)

    def test_hostile_dimension_mutation_is_rejected(self) -> None:
        mutated = json.loads(json.dumps(self.data))
        mutated["dimension_ledger"]["self_adjoint_End_wedge2_V_dimension"] = 55
        with self.assertRaises(AssertionError):
            CHECK.verify(mutated)


if __name__ == "__main__":
    unittest.main()
