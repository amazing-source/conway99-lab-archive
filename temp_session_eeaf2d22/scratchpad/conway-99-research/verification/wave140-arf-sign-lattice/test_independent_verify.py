"""Hostile tests for the clean-room Wave 140 verifier."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_verify as verify  # noqa: E402


class IndependentWave140Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verify.main_results()

    def test_sealed_input_is_exact(self) -> None:
        package = self.result["frozen_package"]
        self.assertTrue(package["manifest_pass"])
        self.assertTrue(package["entries_pass"])
        self.assertEqual(package["entry_count"], 8)

    def test_ambient_space_is_nondegenerate_and_negative(self) -> None:
        ambient = self.result["ambient"]
        self.assertEqual(ambient["dimension"], 98)
        self.assertEqual(ambient["bilinear_rank"], 98)
        self.assertEqual((ambient["E2_count"], ambient["H2_count"]), (25, 24))
        self.assertEqual(ambient["gauss_sum"], -(1 << 49))
        self.assertEqual(ambient["epsilon"], -1)

    def test_plane_models_are_directly_enumerated(self) -> None:
        self.assertEqual(
            self.result["plane_models"]["H2"],
            {
                "gram": [[0, 1], [1, 0]],
                "det_mod_8": 7,
                "gauss_sum": 2,
                "epsilon": 1,
            },
        )
        self.assertEqual(
            self.result["plane_models"]["E2"],
            {
                "gram": [[2, 1], [1, 2]],
                "det_mod_8": 3,
                "gauss_sum": -2,
                "epsilon": -1,
            },
        )

    def test_determinant_bridge_survives_all_plane_counts(self) -> None:
        self.assertTrue(
            self.result["bridge"]["exhaustive_plane_count_check"]
        )
        with self.assertRaises(ValueError):
            verify.chi_two(0)

    def test_opposite_sign_controls_reconstruct(self) -> None:
        controls = self.result["controls"]
        self.assertEqual([item["U"]["epsilon"] for item in controls], [1, -1])
        self.assertEqual(
            [item["U"]["determinant_unit_mod_8"] for item in controls],
            [7, 3],
        )
        self.assertEqual(
            [item["W"]["determinant_unit_mod_8"] for item in controls],
            [5, 1],
        )
        self.assertTrue(self.result["control_hashes_match_discovery"])

    def test_binary_controls_are_exact_but_not_graphs(self) -> None:
        for control in self.result["controls"]:
            projection = control["binary_projection"]
            self.assertEqual(projection["rank"], 54)
            self.assertTrue(projection["symmetric"])
            self.assertTrue(projection["idempotent_mod_2"])
            self.assertTrue(projection["zero_diagonal_mod_2"])
            self.assertTrue(projection["kills_one_mod_2"])
            self.assertFalse(projection["integer_row_sums_all_14"])
            self.assertFalse(projection["integer_srg_identity"])

    def test_local_spectral_identity_is_only_local(self) -> None:
        for control in self.result["controls"]:
            operator = control["local_operator"]
            self.assertEqual(operator["trace"], 0)
            self.assertTrue(operator["polynomial_on_K"])
            self.assertTrue(operator["polynomial_on_one_line"])
        self.assertFalse(
            self.result["hostile_scope_checks"][
                "integral_zero_one_adjacency_supplied"
            ]
        )

    def test_full_smith_list_reconstructs_conditionally(self) -> None:
        smith = self.result["smith_reconstruction"]
        self.assertEqual(
            smith["counts"],
            {"1": 45, "3": 9, "6": 1, "12": 43, "84": 1},
        )
        self.assertEqual(smith["modular_ranks"], {"2": 54, "3": 45, "7": 98})
        self.assertTrue(smith["all_divide_84"])
        self.assertTrue(smith["product_matches_spectrum"])

    def test_group_is_same_but_form_unit_differs(self) -> None:
        boundary = self.result["discriminant_boundary"]
        self.assertTrue(boundary["groups_equal"])
        self.assertEqual(boundary["scale_16_form_units"], [5, 1])
        self.assertTrue(boundary["forms_separated_by_unit_square_class"])

    def test_unknown_status_is_preserved(self) -> None:
        self.assertEqual(self.result["status"]["target_epsilon"], "UNKNOWN")
        self.assertEqual(self.result["status"]["Conway_99"], "UNKNOWN")
        self.assertEqual(
            self.result["status"]["integral_graph"],
            "NOT_CONSTRUCTED",
        )


if __name__ == "__main__":
    unittest.main()
