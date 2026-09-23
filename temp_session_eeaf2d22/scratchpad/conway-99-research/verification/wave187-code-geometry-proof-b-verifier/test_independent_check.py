from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave187_proof_b_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave187ProofBIndependentTests(unittest.TestCase):
    def test_frozen_inputs_and_separation(self) -> None:
        result = CHECK.verify_frozen_inputs()
        self.assertTrue(result["passed"])
        self.assertEqual(result["files_checked"], 8)
        self.assertFalse(result["discovery_checker_imported_or_executed"])

    def test_exact_masses_and_marked_family(self) -> None:
        result = CHECK.mass_certificate()
        self.assertTrue(result["all_masses_strictly_positive"])
        self.assertEqual(result["projective_scalar_pair_total"], 88573)
        self.assertEqual(result["marked_family"]["composition"], [36, 162])
        self.assertEqual(result["marked_family"]["mass"], 231)

    def test_complete_strength_three(self) -> None:
        result = CHECK.complete_strength_three_certificate()
        self.assertTrue(result["all_equal"])
        self.assertEqual(
            result["totals"],
            ["88573", "-231", "-26565", "-53130", "-6083385", "-2027795"],
        )

    def test_ordinary_macwilliams(self) -> None:
        result = CHECK.ordinary_certificate()
        self.assertEqual(result["B1_B2_B3"], ["0", "0", "0"])
        self.assertTrue(result["all_B_nonnegative"])
        self.assertTrue(result["all_B_at_least_A"])
        self.assertEqual(result["B4"], "126079749915623/131414760")
        self.assertEqual(
            result["B4_through_B9"],
            "721437869830147204193861/3066344400",
        )

    def test_complete_macwilliams_boundary(self) -> None:
        result = CHECK.complete_certificate()
        self.assertEqual(result["maximum_certified_nonnegative_total_degree"], 6)
        self.assertEqual(
            result["degree_four_row"],
            ["0", "0", "126079749915623/131414760", "0", "0"],
        )
        self.assertEqual(result["first_negative_total_degree"], 7)
        self.assertEqual(
            result["negative_degree_seven_cells"]["B_70"],
            "-10151603437954385741/508426957500",
        )
        for degree in range(7):
            self.assertEqual(result["degrees"][str(degree)]["negative_count"], 0)

    def test_quadratic_geometry(self) -> None:
        result = CHECK.quadratic_geometry_certificate()
        self.assertEqual(result["projective_points_enumerated"], 88573)
        self.assertEqual(result["class_sizes_S_plus_minus"], [29524, 29646, 29403])
        self.assertEqual(
            result["orthogonal_pair_complement_S_plus_minus"], [3280, 3402, 3159]
        )
        self.assertEqual(
            result["nonorthogonal_pair_complement_S_plus_minus"],
            [3280, 3321, 3240],
        )

    def test_typed_moments(self) -> None:
        result = CHECK.typed_moment_certificate()
        self.assertEqual(
            result["typed_factorial_moments"]["singular"],
            ["29524", "2273271", "87133200", "2233980128"],
        )
        self.assertEqual(result["third_moment_total"], "6651167600")

    def test_integral_triple_census(self) -> None:
        result = CHECK.triple_census_certificate()
        self.assertTrue(result["matches_typed_moments"])
        self.assertEqual(result["triple_total"], 2027795)
        self.assertEqual(result["wedge_incidence"], 114576)
        self.assertFalse(result["realizable_point_set_asserted"])

    def test_boundary_is_not_existence(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(result["verdict"], "VERIFIED_RELAXATION_BOUNDARY")
        self.assertTrue(result["boundary"]["rational_relaxation_only"])
        self.assertFalse(result["boundary"]["linear_code_constructed"])
        self.assertFalse(result["boundary"]["projective_point_set_constructed"])
        self.assertFalse(result["boundary"]["float_degree_nine_work_performed"])


if __name__ == "__main__":
    unittest.main()
