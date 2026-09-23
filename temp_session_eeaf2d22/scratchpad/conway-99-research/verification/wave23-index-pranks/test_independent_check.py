from __future__ import annotations

import itertools
import unittest
from fractions import Fraction

import independent_check as check


class Wave23IndependentTests(unittest.TestCase):
    def test_trace_square_floor(self) -> None:
        result = check.trace_square_floor()
        self.assertEqual(result["trace_C"], 2)
        self.assertEqual(result["minimum_positive_trace_C2"], 2)
        self.assertEqual(result["minimum_trace_B2"], 60)

    def test_trace_square_parity_for_all_small_two_by_two_matrices(self) -> None:
        for entries in itertools.product(range(-2, 3), repeat=4):
            matrix = [list(entries[:2]), list(entries[2:])]
            self.assertEqual(*check.trace_square_parities(matrix))

    def test_dyadic_radical_brackets(self) -> None:
        for numerator in range(1, 30):
            for denominator in range(1, 20):
                value = Fraction(numerator, denominator)
                lower, upper = check.sqrt_dyadic_bracket(value, bits=64)
                self.assertLessEqual(lower * lower, value)
                self.assertGreater(upper * upper, value)

    def test_complete_positive_kkt_range(self) -> None:
        result = check.product_certificate()
        self.assertEqual(result["positive_high_counts"], list(range(1, 39)))
        self.assertEqual(result["nonpositive_low_counts"], list(range(39, 44)))

    def test_all_stationary_products_below_thirteen(self) -> None:
        result = check.product_certificate()
        self.assertTrue(result["all_product_upper_bounds_below_13"])
        self.assertEqual(result["largest_high_count"], 1)
        self.assertLess(result["largest_product_upper"], 13)

    def test_stationary_moments_are_bracketed(self) -> None:
        for high_count in range(1, 39):
            case = check.stationary_spectrum(high_count)
            high_low, high_high = case["high_interval"]
            low_low, low_high = case["low_interval"]
            for high in (high_low, high_high):
                for low in (low_low, low_high):
                    self.assertGreater(high, 0)
                    self.assertGreater(low, 0)
            # The exact values lie in these intervals and the defining
            # radical formulas solve both moments.
            self.assertEqual(
                case["high_radicand"],
                Fraction(21 * (44 - high_count), 121 * high_count),
            )
            self.assertEqual(
                case["low_radicand"],
                Fraction(21 * high_count, 121 * (44 - high_count)),
            )

    def test_square_trace_59_hostile_control(self) -> None:
        result = check.product_certificate(square_trace=59)
        self.assertFalse(result["all_product_upper_bounds_below_13"])

    def test_endpoint_determinant_pairs(self) -> None:
        self.assertEqual(
            check.determinant_pairs(12),
            [(1, 5, 5), (1, 9, 9)],
        )
        self.assertEqual(
            sorted({row[0] for row in check.determinant_pairs(45)}),
            [1, 9],
        )

    def test_det_q_mod_four(self) -> None:
        self.assertEqual(check.even_gram_odd_determinant_mod_four(44), 1)
        self.assertEqual(check.even_gram_odd_determinant_mod_four(2), 3)

    def test_h_one_rescaling_signature(self) -> None:
        self.assertTrue(
            check.h_one_rescaling(44)["excluded_by_even_unimodular_signature"]
        )
        self.assertFalse(
            check.h_one_rescaling(40)["excluded_by_even_unimodular_signature"]
        )
        with self.assertRaises(AssertionError):
            check.h_one_rescaling(44, 2)

    def test_smith_rank_controls(self) -> None:
        self.assertEqual(
            check.smith_data((1,) * 44),
            {"h": 1, "rank_mod_3": 44, "rank_mod_7": 44},
        )
        self.assertEqual(
            check.smith_data((1,) * 42 + (3, 3)),
            {"h": 9, "rank_mod_3": 42, "rank_mod_7": 44},
        )

    def test_smith_hostile_factor_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            check.smith_data((1,) * 43 + (9,))

    def test_adjacency_algebra_controls(self) -> None:
        result = check.adjacency_checks()
        self.assertEqual(result["S2"], ["49", "0", "49"])
        self.assertTrue(result["R2_equals_7R"])
        self.assertTrue(result["five_R_equals_S_mod_7"])

    def test_full_audit_scope(self) -> None:
        result = check.audit()
        self.assertEqual(result["claim_label"], "VERIFIED")
        self.assertEqual(result["conclusion"]["conditional_n3_lower_bound"], 708)
        self.assertEqual(result["conclusion"]["target_resolution"], "NOT_CLAIMED")
        self.assertEqual(result["conclusion"]["novelty"], "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
