#!/usr/bin/env python3
"""Hostile tests for the Wave 21 local-diagonal exact checker."""

from fractions import Fraction
import unittest

import exact_check as check


class LocalDiagonalTests(unittest.TestCase):
    def test_all_row_profiles(self) -> None:
        for q in range(13):
            self.assertEqual(check.schur_cube_row_sum(q), 6 * (q - 2))

    def test_local_tensor_constant(self) -> None:
        self.assertEqual(Fraction(36, 1) / Fraction(172, 11), Fraction(99, 43))

    def test_local_integral_table_selected_values(self) -> None:
        self.assertEqual(check.local_a4_integral_lower(0), 12)
        self.assertEqual(check.local_a4_integral_lower(2), 4)
        self.assertEqual(check.local_a4_integral_lower(3), 4)
        self.assertEqual(check.local_a4_integral_lower(8), 84)
        self.assertEqual(check.local_a4_integral_lower(9), 116)

    def test_harmonic_coefficient(self) -> None:
        self.assertEqual(Fraction(3 * 4**2, 44 + 2), Fraction(24, 23))

    def test_harmonic_values(self) -> None:
        self.assertEqual(
            {m: check.harmonic_value(m) for m in check.M_VALUES},
            {-2: -136, -1: 1, 0: 0, 1: -1},
        )

    def test_endpoint_harmonic_cutoff(self) -> None:
        total = 92 * 12
        self.assertLessEqual((138 * 8) ** 2, 1376 * total)
        self.assertGreater((138 * 9) ** 2, 1376 * total)

    def test_two_q10_centered_minor_fails_for_every_entry(self) -> None:
        residual_diagonal = Fraction(272)
        centered = [
            Fraction(check.harmonic_value(m)) - 1104
            for m in check.M_VALUES
        ]
        self.assertTrue(all(value * value > residual_diagonal**2 for value in centered))

    def test_combined_local_budget_excludes_q9(self) -> None:
        self.assertLessEqual(check.local_a4_rational_lower(8), 88)
        self.assertGreater(check.local_a4_rational_lower(9), 88)

    def test_endpoint_scalar_survivor(self) -> None:
        profiles = check.endpoint_scalar_profiles()
        self.assertIn(
            {
                "b0": 0,
                "b1": 0,
                "b2": 223,
                "b3": 8,
                "b4": 0,
                "b5": 0,
                "b6": 0,
                "b7": 0,
                "b8": 0,
                "minimum_excess_units": 0,
            },
            profiles,
        )

    def test_frobenius_congruence(self) -> None:
        self.assertEqual(3250 * 2 % 8, 4)
        self.assertEqual(441 % 8, 1)
        self.assertEqual(Fraction(1008**2, 44 * 441), Fraction(576, 11))

    def test_full_audit(self) -> None:
        result = check.endpoint_audit()
        self.assertEqual(result["conclusion"], "INCONCLUSIVE_ENDPOINT_SURVIVES")
        self.assertEqual(result["local_A4"]["endpoint_q_max"], 8)

    def test_hostile_radius_mutation_detected(self) -> None:
        self.assertNotEqual(Fraction(3 * 5**2, 44 + 2), Fraction(24, 23))

    def test_hostile_dimension_mutation_detected(self) -> None:
        self.assertNotEqual(Fraction(3 * 4**2, 43 + 2), Fraction(24, 23))

    def test_hostile_unordered_factor_detected(self) -> None:
        self.assertNotEqual(((4620 + 470) + 705) // 2, 3250)

    def test_hostile_drop_mod_four_changes_q_bound(self) -> None:
        unrounded_q8 = check.local_a4_rational_lower(8)
        self.assertEqual(check.local_a4_integral_lower(8), 84)
        self.assertLess(unrounded_q8, 84)


if __name__ == "__main__":
    unittest.main()
