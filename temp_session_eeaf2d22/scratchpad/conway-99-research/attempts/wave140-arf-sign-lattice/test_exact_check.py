"""Hostile exact tests for the Wave140 Arf-sign controls."""

from __future__ import annotations

import unittest

import exact_check as check


class Wave140ArfSignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.main_results()

    def test_target_sign_remains_unknown(self) -> None:
        self.assertEqual(self.result["status"]["target_epsilon"], "UNKNOWN")
        self.assertEqual(self.result["status"]["Conway_99"], "UNKNOWN")

    def test_ambient_hyperplane_has_negative_sign(self) -> None:
        ambient = self.result["ambient_even_hyperplane"]
        self.assertEqual(ambient["dimension"], 98)
        self.assertEqual(ambient["E_plane_count"], 25)
        self.assertEqual(ambient["H_plane_count"], 24)
        self.assertEqual(ambient["Arf"], 1)
        self.assertEqual(ambient["epsilon"], -1)
        self.assertEqual(ambient["determinant_unit_mod_8"], 3)

    def test_opposite_arf_controls_exist(self) -> None:
        controls = self.result["opposite_sign_controls"]
        self.assertEqual([item["U"]["epsilon"] for item in controls], [1, -1])
        self.assertEqual(
            [item["U"]["determinant_unit_mod_8"] for item in controls],
            [7, 3],
        )
        self.assertEqual(
            [item["W"]["determinant_unit_mod_8"] for item in controls],
            [5, 1],
        )

    def test_both_binary_projections_replay(self) -> None:
        hashes = []
        for control in self.result["opposite_sign_controls"]:
            audit = control["binary_projection_control"]
            self.assertEqual(audit["rank"], 54)
            self.assertTrue(audit["symmetric"])
            self.assertTrue(audit["idempotent"])
            self.assertTrue(audit["zero_diagonal"])
            self.assertTrue(audit["kills_all_one"])
            hashes.append(audit["packed_matrix_sha256"])
        self.assertEqual(len(set(hashes)), 2)

    def test_complement_signs_are_opposite(self) -> None:
        for control in self.result["opposite_sign_controls"]:
            self.assertEqual(
                control["U"]["epsilon"] * control["W"]["epsilon"],
                -1,
            )

    def test_arf_determinant_bridge(self) -> None:
        for control in self.result["opposite_sign_controls"]:
            unit = control["U"]["determinant_unit_mod_8"]
            self.assertEqual(
                control["U"]["epsilon"],
                check.kronecker_two(unit),
            )
        self.assertEqual(check.kronecker_two(7), 1)
        self.assertEqual(check.kronecker_two(3), -1)

    def test_smith_reconstruction(self) -> None:
        smith = self.result["smith_reconstruction"]
        self.assertTrue(smith["all_divide_84"])
        self.assertTrue(smith["product_matches_spectrum"])
        self.assertEqual(
            (smith["rank_mod_2"], smith["rank_mod_3"], smith["rank_mod_7"]),
            (54, 45, 98),
        )
        self.assertEqual(
            smith["two_primary_operator_factors"],
            "1^54,2,4^44",
        )

    def test_scalar_operator_identities(self) -> None:
        checks = self.result["spectral_operator_control"][
            "scalar_identity_checks"
        ]
        self.assertTrue(checks["U"])
        self.assertTrue(checks["W"])
        self.assertTrue(checks["all_one_line"])
        self.assertTrue(checks["trace_zero"])
        self.assertEqual(checks["two_adic_determinant_valuation"], 89)

    def test_group_level_data_do_not_separate_controls(self) -> None:
        groups = {
            control["two_primary_adjacency_lattice_discriminant_group"]
            for control in self.result["opposite_sign_controls"]
        }
        self.assertEqual(groups, {"Z/4 + (Z/16)^44"})
        self.assertFalse(
            self.result["discriminant_boundary"][
                "verified_full_target_form_available"
            ]
        )

    def test_no_integral_adjacency_control_is_claimed(self) -> None:
        self.assertFalse(
            self.result["spectral_operator_control"][
                "entrywise_zero_one_zero_diagonal_integral_matrix_supplied"
            ]
        )
        self.assertFalse(self.result["status"]["graph_constructed"])

    def test_odd_kronecker_input_is_required(self) -> None:
        with self.assertRaises(ValueError):
            check.kronecker_two(2)


if __name__ == "__main__":
    unittest.main()
