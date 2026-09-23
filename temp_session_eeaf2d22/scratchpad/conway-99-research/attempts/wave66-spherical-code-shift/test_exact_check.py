"""Focused tests for the Wave 66 exact arithmetic checker."""

from __future__ import annotations

import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave66_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave66ExactCheckTests(unittest.TestCase):
    def test_bose_mesner_identities(self) -> None:
        seidel = (1, 2, -1)
        gram = (6, -2, 1)
        self.assertEqual(CHECK.add(seidel, gram), (7, 0, 0))
        self.assertEqual(CHECK.multiply(seidel, seidel), (49, 0, 49))
        self.assertEqual(
            CHECK.multiply(gram, gram),
            CHECK.add(CHECK.scale(14, gram), (0, 0, 49)),
        )

    def test_equiangular_lift(self) -> None:
        data = CHECK.build_results()["spherical_embeddings"]["equiangular_lift"]
        self.assertEqual(data["adjacent"], "-1/7")
        self.assertEqual(data["nonadjacent"], "1/7")

    def test_gram_spectrum(self) -> None:
        gram = CHECK.build_results()["integral_gram"]
        spectrum = gram["spectrum"]
        self.assertEqual(
            spectrum,
            {
                "principal": 77,
                "eigenvalue_3_space": 0,
                "eigenvalue_minus4_space": 14,
            },
        )
        self.assertEqual(
            gram["seidel_spectrum"],
            {
                "principal": -70,
                "eigenvalue_3_space": 7,
                "eigenvalue_minus4_space": -7,
            },
        )
        self.assertIn("adjacent +1", gram["seidel_sign_convention"])

    def test_centering_removes_constant_direction(self) -> None:
        centered = CHECK.build_results()["centering"]
        self.assertEqual(
            centered["spectrum"],
            {
                "principal": "0",
                "eigenvalue_3_space": "0",
                "eigenvalue_minus4_space": "7",
            },
        )
        self.assertEqual(centered["rank"], 44)
        self.assertTrue(centered["all_ones_direction_removed"])
        self.assertEqual(
            centered["difference_norms_after_halving"],
            {"adjacent_to_reference": 8, "nonadjacent_to_reference": 6},
        )

    def test_fractional_cosets(self) -> None:
        self.assertEqual(CHECK.fractional_energy(11), Fraction(88, 9))
        self.assertEqual(CHECK.fractional_energy(22), Fraction(154, 9))
        self.assertEqual(CHECK.fractional_energy(88), Fraction(88, 9))

    def test_subset_spectral_bounds(self) -> None:
        self.assertEqual(CHECK.exact_subset_bound(10), Fraction(185, 9))
        self.assertEqual(int(CHECK.exact_subset_bound(10)), 20)
        self.assertEqual(CHECK.exact_subset_bound(12), Fraction(26, 1))
        self.assertEqual(int(CHECK.exact_subset_bound(12)), 26)

    def test_discriminant_rows(self) -> None:
        endpoint = CHECK.build_results()["endpoint"]
        all_rows = endpoint["all_determinant_rows_before_milgram"]
        rows = endpoint["surviving_rows"]
        self.assertEqual(len(all_rows), 17)
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0]["rank_F7_Seidel"], 28)
        self.assertEqual(rows[0]["determinant"], 9 * 7**16)
        self.assertEqual(rows[-1]["rank_F7_Seidel"], 42)
        self.assertEqual(rows[-1]["determinant"], 9 * 7**2)
        self.assertEqual(
            [row["rank_F7_Seidel"] for row in rows], list(range(28, 43, 2))
        )
        rank44 = all_rows[-1]
        self.assertEqual(rank44["rank_F7_Seidel"], 44)
        self.assertFalse(rank44["milgram_phase_possible"])

    def test_dual_denominator_and_minimum_are_explicit(self) -> None:
        lattice = CHECK.build_results()["difference_lattice"]
        self.assertEqual(lattice["dual_denominator"], "63 M* subset M")
        self.assertEqual(lattice["dual_minimum_lower_bound"], "2")
        self.assertEqual(lattice["rank_mod_3"], 43)
        self.assertEqual(lattice["milgram_congruence"], "r is even and r<=42")

    def test_milgram_and_blichfeldt_boundaries(self) -> None:
        data = CHECK.build_results()
        self.assertEqual(
            data["milgram"]["surviving_ranks_in_imported_interval"],
            list(range(28, 43, 2)),
        )
        self.assertEqual(data["milgram"]["exact_discriminant_form_level_for_survivors"], 63)
        for unit in (1, 2, 4, 5, 7, 8):
            gauss = CHECK.z9_gauss_cyclotomic_quotient(unit)
            self.assertEqual(gauss["normalized_phase"], "+1")
            self.assertIn(
                gauss["sum_minus_3_quotient_by_Phi9"], {"2*x", "2*x^2"}
            )
        phase_table = data["milgram"]["seven_dimension_phase_table"]
        self.assertFalse(phase_table[0]["can_match_signature_phase_minus_one"])
        self.assertFalse(phase_table[1]["can_match_signature_phase_minus_one"])
        self.assertTrue(phase_table[2]["can_match_signature_phase_minus_one"])
        blichfeldt = data["blichfeldt_cross_check"]
        self.assertEqual(blichfeldt["r_at_least"], 18)
        self.assertTrue(blichfeldt["rank_17_excluded_using_pi_gt_157_over_50"])
        self.assertTrue(blichfeldt["rank_18_survives_using_pi_lt_22_over_7"])
        self.assertTrue(blichfeldt["weaker_than_imported_r_at_least_28"])

    def test_scope_guards(self) -> None:
        data = CHECK.build_results()
        self.assertEqual(data["claim_label"], "CANDIDATE")
        self.assertFalse(data["endpoint"]["contradiction_found"])
        self.assertEqual(data["endpoint"]["graph_status"], "UNKNOWN")
        self.assertEqual(data["endpoint"]["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
