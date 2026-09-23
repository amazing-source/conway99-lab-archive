import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_verify.py")
SPEC = importlib.util.spec_from_file_location("wave80_independent", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class IndependentWave80Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODULE.build_results()

    def test_marked_span_and_injectivity(self):
        evaluation = self.result["evaluation_code"]
        self.assertEqual(
            evaluation["marked_span"]["quotient_consequence"], "3(L/N)=0"
        )
        self.assertTrue(evaluation["evaluation"]["injective"])
        self.assertEqual(evaluation["evaluation"]["dimension"], 44)

    def test_form_scale_and_hull(self):
        evaluation = self.result["evaluation_code"]
        self.assertEqual(
            evaluation["form"]["code_dot"],
            "63<y,z>=9 beta=2 beta mod 7",
        )
        self.assertEqual(
            evaluation["hull"]["identity"],
            "C intersect C^perp=row_F7(S)",
        )
        self.assertEqual(
            [row["dim_L_mod_7Lstar"] for row in evaluation["dimension_rows"]],
            [42, 40, 38, 36, 34, 32, 30, 28],
        )

    def test_all_orthogonal_types(self):
        rows = self.result["orthogonal_geometry_rows"]
        self.assertEqual(len(rows), 8)
        self.assertTrue(
            all(row["C_mod_hull"]["type"] == "minus" for row in rows)
        )
        self.assertTrue(all(row["W0"]["type"] == "minus" for row in rows))
        self.assertTrue(
            all(
                row["orthogonal_complement_in_W0"]["type"] == "plus"
                for row in rows
            )
        )

    def test_endpoint_types_and_indices(self):
        endpoint = self.result["endpoint_r28_q16"]
        self.assertEqual(endpoint["C_mod_hull"]["dimension"], 16)
        self.assertEqual(endpoint["C_mod_hull"]["witt_index"], 7)
        self.assertEqual(endpoint["W0"]["dimension"], 42)
        self.assertEqual(endpoint["W0"]["witt_index"], 20)
        self.assertEqual(
            endpoint["orthogonal_complement_in_W0"]["dimension"], 26
        )
        self.assertEqual(
            endpoint["orthogonal_complement_in_W0"]["witt_index"], 13
        )

    def test_principal_blocks_through_four(self):
        principal = self.result["dual_support"]["principal_blocks"]
        self.assertEqual(
            principal["2"]["determinant_residues_mod_7"], [6]
        )
        self.assertEqual(
            principal["3"]["determinant_residues_mod_7"], [2, 5]
        )
        self.assertEqual(
            principal["4"]["determinant_residues_mod_7"], [4, 5]
        )

    def test_complete_five_support_exclusion(self):
        five = self.result["dual_support"]["five_support"]
        self.assertEqual(five["all_labelled_graphs"], 1024)
        self.assertEqual(five["locally_admissible_graphs"], 683)
        self.assertEqual(five["singular_full_support_graphs"], 132)
        self.assertEqual(five["projective_relations_checked"], 132)
        self.assertEqual(
            five["relations_with_compatible_outside_pattern"], 0
        )
        self.assertEqual(len(five["isomorphism_classes"]), 3)

    def test_support_six_is_not_silently_excluded(self):
        control = self.result["dual_support"]["six_support_positive_control"]
        self.assertGreater(control["compatible_outside_pattern_count"], 0)
        self.assertEqual(len(control["projective_kernel_relation"]), 6)

    def test_short_vector_map_and_dots(self):
        rows = self.result["short_vectors"]["rows"]
        self.assertEqual(
            [row["evaluation_word"]["Hamming_weight"] for row in rows],
            [14, 16, 18],
        )
        self.assertEqual(
            [row["self_dot_mod_7"] for row in rows], [0, 4, 1]
        )
        self.assertEqual(
            rows[0]["class_in_C_mod_hull"], "zero_or_nonzero_isotropic"
        )
        self.assertTrue(
            all(
                row["class_in_C_mod_hull"] == "anisotropic"
                for row in rows[1:]
            )
        )

    def test_oa_strength_and_moment_boundary(self):
        self.assertEqual(
            self.result["dual_support"]["orthogonal_array_strength"], 5
        )
        moments = self.result["macwilliams_null_control"][
            "strength_five_OA_moments"
        ]
        self.assertEqual([row["degree"] for row in moments], list(range(6)))
        self.assertTrue(all(row["strict_slack"] > 0 for row in moments))
        self.assertFalse(
            self.result["macwilliams_null_control"][
                "full_weight_enumerator_constructed"
            ]
        )

    def test_status_boundary(self):
        self.assertEqual(self.result["verdict"], "VERIFIED")
        self.assertFalse(self.result["status"]["rank_28_excluded"])
        self.assertEqual(self.result["status"]["Conway_99"], "UNKNOWN")
        self.assertEqual(self.result["status"]["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
