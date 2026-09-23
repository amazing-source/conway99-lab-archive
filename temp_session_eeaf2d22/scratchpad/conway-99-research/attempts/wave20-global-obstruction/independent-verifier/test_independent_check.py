"""Hostile and exact tests for the independently reconstructed checker."""

from __future__ import annotations

import unittest
from fractions import Fraction

import independent_check as check


class ExactReconstructionTests(unittest.TestCase):
    def test_triangle_incidence_spectrum(self) -> None:
        self.assertEqual(check.gamma_spectrum(), {18: 1, 7: 54, 0: 44, -3: 132})

    def test_C_spectrum(self) -> None:
        self.assertEqual(check.c_spectrum(), {216: 1, -4: 54, -18: 44, 6: 132})

    def test_all_fixed_triangle_profiles(self) -> None:
        for q in range(13):
            with self.subTest(q=q):
                profile = check.fixed_profile(q)
                self.assertEqual(profile, check.solve_profile_from_a3(12 - q))
                self.assertEqual(check.profile_moments(profile), (212, 216, 36))

    def test_ordered_pair_count_requires_halving(self) -> None:
        ordered = 3 * 2 * 12
        self.assertEqual(ordered, 72)
        self.assertEqual(ordered // 2, 36)
        self.assertNotEqual(ordered, 36)

    def test_q_n3_relation_keeps_fixed_side_factor_two(self) -> None:
        self.assertEqual(check.q_sum_from_n3(705), 470)
        self.assertEqual(check.n3_from_q_sum(470), 705)
        self.assertNotEqual(Fraction(705, 3), check.q_sum_from_n3(705))

    def test_projector_polynomial_and_scaling(self) -> None:
        numerator = check.poly_mul((-18, 1), (-7, 1), (3, 1))
        self.assertEqual(numerator, (378, 51, -22, 1))
        self.assertEqual(
            {theta: check.poly_eval(numerator, theta) / 378 for theta in (18, 7, 0, -3)},
            {18: 0, 7: 0, 0: 1, -3: 0},
        )
        check.validate_exact_projector_scale(21)

    def test_hostile_wrong_scaling_is_rejected(self) -> None:
        with self.assertRaises(check.CheckFailure):
            check.validate_exact_projector_scale(20)
        self.assertEqual(check.scaled_projector_entries(20)["diagonal"], Fraction(80, 21))

    def test_exact_M_entry_set_and_row_identities(self) -> None:
        check.validate_m_entry_table(dict(check.EXPECTED_M_ENTRIES))
        for q in range(13):
            stats = check.m_row_statistics(q)
            self.assertEqual(stats["row_sum"], 0)
            self.assertEqual(stats["cubic_sum"], 6 * q - 12)
            self.assertEqual(stats["odd_support"], 20 + 4 * q)
            self.assertGreater(stats["odd_support"], 0)

    def test_hostile_missing_intersecting_zeros_is_rejected(self) -> None:
        missing = dict(check.EXPECTED_M_ENTRIES)
        del missing["intersecting"]
        with self.assertRaises(check.CheckFailure):
            check.validate_m_entry_table(missing)
        mutated = check.m_row_statistics(0, intersecting_entry=1)
        self.assertEqual(mutated["row_sum"], 18)
        self.assertEqual(mutated["cubic_sum"], 6)

    def test_trace_scaling(self) -> None:
        self.assertEqual(check.trace_mathcal_a(693), 0)
        self.assertEqual(check.trace_mathcal_a(705), 1008)
        self.assertEqual(21 * 4, 84)

    def test_D_diagonal_and_alternating_law(self) -> None:
        self.assertEqual(check.d_entry(4), 6)
        alternating = ((0, 1, 1), (1, 0, 1), (1, 1, 0))
        check.verify_alternating_quadratic_law(alternating)

    def test_hostile_nonzero_D_diagonal_mod2_is_rejected(self) -> None:
        hostile = ((1, 0), (0, 0))
        self.assertFalse(check.is_alternating_mod2(hostile))
        self.assertEqual(check.quadratic_value(hostile, (1, 0)) % 2, 1)
        with self.assertRaises(check.CheckFailure):
            check.verify_alternating_quadratic_law(hostile)

    def test_A_mod2_and_diagonal_mod4_coefficients(self) -> None:
        self.assertEqual(21**2, 441)
        self.assertEqual(441 % 2, 1)
        self.assertEqual((441 * 4) % 4, 0)

    def test_hostile_small_deltas_are_rejected(self) -> None:
        for delta in (0, 3, 6, 9):
            with self.subTest(delta=delta):
                self.assertTrue(check.diagonal_budget_rejects_delta(delta))
                self.assertLess(84 * delta, 4 * 231)
        self.assertFalse(check.diagonal_budget_rejects_delta(12))

    def test_final_bound_and_cycle_translation(self) -> None:
        self.assertEqual(693 + 12, 705)
        self.assertEqual(check.induced_c6_count(705), 209_991)

    def test_full_independent_checker_and_mutations(self) -> None:
        result = check.run_exact_checks()
        self.assertEqual(result["summary"]["obligations"], "PASS")
        self.assertEqual(result["summary"]["hostile_mutations"], "PASS")
        self.assertTrue(
            all(item["status"] == "DETECTED" for item in result["hostile_mutations"].values())
        )
        self.assertFalse(result["imports_submitted_candidate_code"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
