"""Focused and hostile tests for the Wave 66 clean-room verifier."""

from __future__ import annotations

import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_verify.py")
SPEC = importlib.util.spec_from_file_location("wave66_independent", MODULE_PATH)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave66IndependentTests(unittest.TestCase):
    def test_primitive_idempotents_and_lift(self) -> None:
        data = VERIFY.primitive_idempotent_data()
        self.assertEqual(data["E3_diagonal"], "6/11")
        self.assertEqual(data["Eminus4_diagonal"], "4/9")
        self.assertEqual(data["lifted_inner_products"], ["-1/7", "1/7"])

    def test_seidel_sign_and_multiplicities(self) -> None:
        data = VERIFY.gram_and_centering_data()
        self.assertEqual(data["seidel_convention"], "S=2A-J+I")
        self.assertEqual(data["seidel_spectrum"], [-70, 7, -7])
        self.assertEqual(data["seidel_multiplicities"], [1, 54, 44])

    def test_centering_removes_constant_coordinate(self) -> None:
        data = VERIFY.gram_and_centering_data()
        self.assertEqual(data["gram_rank"], 45)
        self.assertEqual(data["centered_rank"], 44)
        self.assertEqual(data["centered_spectrum"], [0, 0, 7])
        self.assertEqual(data["difference_squared_norms_in_M"], [8, 6])

    def test_local_smith_profiles(self) -> None:
        self.assertEqual(
            VERIFY.enumerate_local_exponents(44, 43, 2, 2),
            [0] * 43 + [2],
        )
        self.assertEqual(
            VERIFY.enumerate_local_exponents(44, 40, 4, 1),
            [0] * 40 + [1] * 4,
        )

    def test_determinant_rows_include_universal_rank_27(self) -> None:
        data = VERIFY.determinant_and_group_data()
        rows = data["universal_pre_milgram_rows"]
        self.assertEqual(rows[0]["r"], 27)
        self.assertEqual(rows[-1]["r"], 44)
        self.assertEqual(rows[0]["determinant"], 9 * 7**17)
        self.assertTrue(
            all(
                row["sum_9n_plus_b"] == 0
                for row in data["dual_inclusion_exact_checks"]
            )
        )
        self.assertIn("exact lattice level is 63", data["level_argument"])

    def test_z9_gauss_residue_patterns(self) -> None:
        data = VERIFY.gauss_and_milgram_data()
        self.assertEqual(data["z9_phase_for_every_nondegenerate_form"], "+1")
        self.assertEqual(len(data["z9_residue_counts"]), 6)

    def test_milgram_phase_and_zero_dimensional_exception(self) -> None:
        data = VERIFY.gauss_and_milgram_data()
        self.assertEqual(data["phase_condition"], "q=44-r is positive and even")
        self.assertEqual(data["surviving_ranks"], list(range(28, 43, 2)))
        self.assertEqual(data["r_at_most"], 42)
        self.assertNotIn(44, data["surviving_ranks"])

    def test_fractional_dual_cosets(self) -> None:
        data = VERIFY.dual_minimum_data()
        self.assertEqual(data["fractional_energy"]["11"], "88/9")
        self.assertEqual(data["fractional_energy"]["22"], "154/9")
        self.assertEqual(data["a11_next_energy"], "142/9")
        self.assertGreater(Fraction(data["a11_next_energy"]), 14)

    def test_integral_low_norm_profiles_are_complete(self) -> None:
        self.assertEqual(
            VERIFY.primitive_low_norm_profiles(),
            {
                8: [{"abs1": 8, "abs2": 0, "abs3": 0}],
                10: [{"abs1": 10, "abs2": 0, "abs3": 0}],
                12: [
                    {"abs1": 8, "abs2": 1, "abs3": 0},
                    {"abs1": 12, "abs2": 0, "abs3": 0},
                ],
            },
        )

    def test_spectral_support_bounds(self) -> None:
        self.assertEqual(VERIFY.subset_edge_bound(10), Fraction(185, 9))
        self.assertEqual(VERIFY.subset_edge_bound(12), Fraction(26))

    def test_dual_minimum_branch_conclusions(self) -> None:
        data = VERIFY.dual_minimum_data()
        self.assertTrue(data["norm8_excluded"])
        self.assertTrue(data["norm10_excluded_by_mu2"])
        self.assertTrue(data["norm12_excluded_by_mu2"])
        self.assertEqual(data["dual_minimum_at_least"], 2)
        self.assertIn("not needed", data["weight8_import_verified_but_not_needed"])

    def test_blichfeldt_is_strictly_weaker(self) -> None:
        data = VERIFY.blichfeldt_data()
        self.assertEqual(data["r_at_least"], 18)
        self.assertTrue(data["rank17_excluded_exact"])
        self.assertTrue(data["rank18_survives_exact"])

    def test_hostile_controls(self) -> None:
        controls = VERIFY.hostile_controls()
        self.assertTrue(all(controls.values()))
        self.assertEqual(len(controls), 7)

    def test_scope_correction_does_not_change_survivors(self) -> None:
        data = VERIFY.build_results()
        self.assertEqual(data["verdict"], "VERIFIED_WITH_CORRECTION")
        self.assertIn("27<=r<=44", data["correction"]["verified_scope_fact"])
        self.assertEqual(data["status"]["surviving_ranks"], list(range(28, 43, 2)))
        self.assertEqual(data["status"]["graph"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
