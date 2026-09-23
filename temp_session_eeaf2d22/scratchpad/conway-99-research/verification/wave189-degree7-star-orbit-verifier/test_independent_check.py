from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave189_degree7_orbit_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave189Degree7OrbitIndependentTests(unittest.TestCase):
    def test_frozen_inputs_and_source_separation(self) -> None:
        result = CHECK.verify_frozen_inputs()
        self.assertTrue(result["passed"])
        self.assertEqual(result["files_checked_directly"], 16)
        self.assertEqual(
            result["nested_source_entries_checked"], {"degree7": 10, "orbit": 9}
        )
        self.assertFalse(
            result["discovery_checkers_imported_or_executed_by_verifier"]
        )

    def test_exact_masses_and_local_polygon(self) -> None:
        masses = CHECK.mass_certificate()
        polygon = CHECK.star_polygon_certificate()
        self.assertEqual(masses["typed_cells"], 16)
        self.assertEqual(masses["projective_scalar_pair_total"], 88573)
        self.assertTrue(masses["all_masses_strictly_positive"])
        self.assertEqual(
            polygon["convex_hull_vertices"],
            [[0, 0], [6, 0], [5, 2], [2, 5], [0, 6]],
        )
        self.assertTrue(polygon["all_lifts_nonnegative_and_exact"])

    def test_ordinary_macwilliams_and_short_sum(self) -> None:
        result = CHECK.ordinary_certificate()
        self.assertEqual(result["primal_total"], "177147")
        self.assertEqual(result["B0_through_B9"][:4], ["1", "0", "0", "0"])
        self.assertTrue(result["all_232_B_rows_nonnegative"])
        self.assertTrue(result["all_232_B_rows_at_least_A"])
        self.assertEqual(
            result["B4_through_B9"],
            "303955951136016513013761953327276372487328891/"
            "2147091333645300550865262629325",
        )

    def test_complete_degree_seven_and_pair_rows(self) -> None:
        result = CHECK.complete_certificate()
        self.assertTrue(result["all_complete_rows_through_degree_seven_nonnegative"])
        self.assertEqual(result["degree_seven_endpoints"], {"B_7_0": "99", "B_0_7": "99"})
        self.assertEqual(result["degree_four_row"][0:2], ["0", "0"])
        self.assertEqual(result["degree_four_row"][3:5], ["0", "0"])
        for value in result["pair_row_slacks"].values():
            self.assertGreaterEqual(CHECK.Fraction(value), 0)
        self.assertTrue(
            result["star_pair_forcing"]["no_extra_total_degree_seven_pair_row"]
        )

    def test_typed_moments_and_rational_census(self) -> None:
        result = CHECK.typed_moment_and_census_certificate()
        self.assertEqual(
            result["typed_factorial_moments"]["singular"][:3],
            ["29524", "2273271", "87133200"],
        )
        self.assertTrue(result["all_census_entries_nonnegative"])
        self.assertEqual(result["triple_total"], "2027795")
        self.assertTrue(result["nonintegral_census_classes"])
        self.assertFalse(result["realizable_point_set_asserted"])

    def test_singleton_majority_translation(self) -> None:
        result = CHECK.singleton_majority_certificate()
        self.assertGreater(result["coefficient_splits_checked"], 0)
        self.assertEqual(result["maximum_of_best_axis_translate_weight"], 9)
        self.assertTrue(result["minimal_subcircuit_crosses_private_label"])
        self.assertTrue(result["outside_selected_cover_by_privacy"])

    def test_orbit_closure_and_scalar_identity(self) -> None:
        result = CHECK.orbit_packing_certificate()
        self.assertTrue(result["pool_separation"]["pairwise_disjoint"])
        self.assertEqual(result["fractional_bound"], {"inequality": "12*Q>=14*C", "Q": 4851})
        self.assertEqual(
            result["orbit_capacity"]["consequence"], "2*|X|>=A"
        )
        self.assertFalse(result["sharp_scalar_control_is_cover_or_graph"])

    def test_hoffman_row_is_only_a_null_boundary(self) -> None:
        result = CHECK.hoffman_null_certificate()
        self.assertEqual(result["candidate_flags"], 13860)
        self.assertEqual(result["conflict_degree"], 27)
        self.assertEqual(result["least_eigenvalue"], -3)
        self.assertEqual(result["hoffman_independence_bound"], "1386")
        self.assertEqual(
            result["status"], "TIGHT_NULL_BOUNDARY_NOT_INTEGRAL_FEASIBILITY"
        )

    def test_equality_saturation_and_weight_seven_residuals(self) -> None:
        result = CHECK.equality_cancellation_certificate()
        self.assertEqual(result["residual_side_profiles"], [[2, 5], [2, 5]])
        self.assertEqual(result["residual_weights"], [7, 7])
        self.assertTrue(result["proper_star_subsets_force_cross_circuit"])
        self.assertTrue(result["contradicts_Q_4851"])
        self.assertEqual(result["strict_Q_lower"], 4852)
        self.assertEqual(result["scalar_short_circuit_word_lower"], 11090)

    def test_status_boundaries(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(result["verdict"], "VERIFIED_WITH_SCOPE")
        self.assertEqual(
            result["degree7_relaxation"]["status"],
            "VERIFIED_RELAXATION_FEASIBILITY",
        )
        self.assertFalse(result["boundary"]["relaxation_feasibility_implies_code_existence"])
        self.assertTrue(result["boundary"]["conditional_Q_at_least_4852_verified"])
        self.assertFalse(result["boundary"]["conditional_theorem_implies_endpoint_exclusion"])
        self.assertEqual(result["boundary"]["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
