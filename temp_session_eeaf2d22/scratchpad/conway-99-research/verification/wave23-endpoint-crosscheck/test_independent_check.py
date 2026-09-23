from __future__ import annotations

import itertools
import unittest
from fractions import Fraction

import independent_check as check


class EndpointCrosscheckIndependentTests(unittest.TestCase):
    def test_scaled_dual_facts(self) -> None:
        facts = check.scaled_dual_facts()
        self.assertEqual(facts["determinant_mod_4"], 1)
        self.assertTrue(facts["h_one_excluded"])

    def test_wrong_scaled_dual_rank_and_scale(self) -> None:
        with self.assertRaises(AssertionError):
            check.scaled_dual_facts(rank=43)
        with self.assertRaises(AssertionError):
            check.scaled_dual_facts(scale=20)

    def test_odd_alternating_principal_controls(self) -> None:
        result = check.odd_alternating_principal_checks()
        self.assertGreater(result["finite_cases_checked"], 0)

    def test_even_gram_determinant_residues(self) -> None:
        self.assertEqual(check.even_gram_odd_determinant_residue(2), 3)
        self.assertEqual(check.even_gram_odd_determinant_residue(4), 1)
        self.assertEqual(check.even_gram_odd_determinant_residue(44), 1)

    def test_rank_two_residue_exhaustive_mod_four(self) -> None:
        seen = 0
        for first, second, off in itertools.product((0, 2), (0, 2), range(4)):
            determinant = check.exact_determinant([[first, off], [off, second]])
            if determinant % 2:
                seen += 1
                self.assertEqual(determinant % 4, 3)
        self.assertGreater(seen, 0)

    def test_trace_square_floor(self) -> None:
        result = check.trace_square_floor()
        self.assertEqual(result["trace_C"], 2)
        self.assertEqual(result["trace_C2_mod_2"], 0)
        self.assertEqual(result["trace_B2_mod_8"], 4)
        self.assertEqual(result["cauchy_lower"], Fraction(576, 11))
        self.assertEqual(result["minimum_trace_B2"], 60)
        self.assertEqual(result["minimum_trace_A4_squared"], 26460)

    def test_first_residue_integer(self) -> None:
        self.assertEqual(
            check.first_integer_with_residue_at_least(
                Fraction(576, 11),
                residue=4,
                modulus=8,
            ),
            60,
        )

    def test_abstract_sharp_spectrum(self) -> None:
        spectrum = [3, 3] + [1] * 42
        self.assertEqual(sum(spectrum), 48)
        self.assertEqual(sum(value * value for value in spectrum), 60)

    def test_newton_and_pair_product_maclaurin(self) -> None:
        result = check.pair_product_maclaurin(60)
        self.assertEqual(result["newton_e2_upper"], 1122)
        self.assertEqual(result["pair_count"], 946)
        self.assertEqual(result["normalized_pair_mean"], Fraction(51, 43))
        self.assertEqual(result["am_gm_exponent"], Fraction(1, 22))

    def test_exact_power_comparison(self) -> None:
        self.assertEqual(
            43**23 - 51**22,
            275207088848909643261540552061708906,
        )
        result = check.pair_product_maclaurin(60)
        self.assertLess(result["determinant_bound"], 43)
        self.assertEqual(result["integer_cap"], 42)

    def test_smooth_enumeration(self) -> None:
        self.assertEqual(check.smooth_3_7(8), [1, 3, 7])
        self.assertEqual(check.smooth_3_7(14), [1, 3, 7, 9])

    def test_final_factor_pairs_empty(self) -> None:
        self.assertEqual(check.factor_pairs(42), [])

    def test_before_h_one_obstruction(self) -> None:
        rows = check.factor_pairs(42, exclude_h_one=False)
        self.assertTrue(rows)
        self.assertEqual({h for h, _, _ in rows}, {1})

    def test_trace_square_hostile_relaxation(self) -> None:
        weak = check.pair_product_maclaurin(54)
        self.assertEqual(weak["integer_cap"], 45)
        self.assertIn((9, 5, 45), check.factor_pairs(45))

    def test_smoothness_hostile_relaxation(self) -> None:
        self.assertIn(
            (5, 5, 25),
            check.factor_pairs(42, require_smooth=False),
        )

    def test_candidate_det_q_three_hostile_needs_second_omission(self) -> None:
        one_omission = check.factor_pairs(
            42,
            det_q_minimum=3,
            require_det_q_residue=False,
        )
        self.assertNotIn((9, 3, 27), one_omission)
        two_omissions = check.factor_pairs(
            42,
            det_q_minimum=3,
            require_det_q_residue=False,
            require_det_b_residue=False,
        )
        self.assertIn((9, 3, 27), two_omissions)

    def test_full_audit_scope(self) -> None:
        result = check.audit()
        self.assertEqual(result["claim_label"], "VERIFIED")
        self.assertEqual(result["conclusion"]["conditional_n3_lower_bound"], 708)
        self.assertEqual(result["conclusion"]["target_status"], "UNKNOWN")
        self.assertEqual(result["conclusion"]["novelty"], "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
