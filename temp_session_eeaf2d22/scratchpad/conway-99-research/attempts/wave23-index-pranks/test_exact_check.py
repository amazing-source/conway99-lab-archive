from __future__ import annotations

import copy
import unittest
from fractions import Fraction

import exact_check as check


class IndexPranksTests(unittest.TestCase):
    def test_full_result(self) -> None:
        result = check.build_results()
        self.assertEqual(
            result["endpoint_conclusion"]["conditional_lower_bound_n3"], 708
        )

    def test_square_root_brackets_are_exact(self) -> None:
        for case in check.stationary_cases():
            scale = check.SQRT_SCALE
            for radicand, floor_value in (
                (case.high_radicand, case.high_sqrt_floor),
                (case.low_radicand, case.low_sqrt_floor),
            ):
                self.assertLessEqual(
                    floor_value * floor_value * radicand.denominator,
                    radicand.numerator * scale * scale,
                )
                self.assertGreater(
                    (floor_value + 1) ** 2 * radicand.denominator,
                    radicand.numerator * scale * scale,
                )

    def test_all_38_stationary_products_are_strictly_below_13(self) -> None:
        cases = check.stationary_cases()
        self.assertEqual([case.high_multiplicity for case in cases], list(range(1, 39)))
        self.assertTrue(all(case.product_upper < 13 for case in cases))
        self.assertEqual(
            max(cases, key=lambda case: case.product_upper).high_multiplicity,
            1,
        )

    def test_weaker_square_moment_does_not_certify_cap(self) -> None:
        mutated = check.certify_product_cap(square_trace=59)
        self.assertFalse(mutated["all_exact_rational_upper_bounds_lt_13"])

    def test_trace_square_floor(self) -> None:
        self.assertEqual(check.trace_square_lower_bound()["minimum_trace_B2"], 60)

    def test_trace_square_parity_for_nonsymmetric_matrix(self) -> None:
        matrix = [[1, 2, 0], [3, 0, 4], [5, 6, 1]]
        self.assertEqual(check.trace_square_parity(matrix), (0, 0))
        matrix[0][0] = 0
        self.assertEqual(check.trace_square_parity(matrix), (1, 1))

    def test_smith_rank_formula(self) -> None:
        self.assertEqual(check.smith_rank_data(44, 0, 0, 0)["h"], 1)
        h9 = check.smith_rank_data(42, 2, 0, 0)
        self.assertEqual(h9["h"], 9)
        self.assertEqual((h9["rank_F3_M"], h9["rank_F7_M"]), (42, 44))

    def test_smith_count_mutation_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            check.smith_rank_data(43, 0, 0, 0)

    def test_adjacency_algebra(self) -> None:
        result = check.adjacency_algebra_checks()
        self.assertEqual(result["S2_coefficients_I_A_J"], ["49", "0", "49"])
        self.assertTrue(result["five_R_equals_S_mod_7"])

    def test_old_endpoint_list(self) -> None:
        rows = check.endpoint_index_survivors(45)
        self.assertEqual(sorted({row["h"] for row in rows}), [1, 9])

    def test_new_endpoint_list_before_h1_obstruction(self) -> None:
        rows = check.endpoint_index_survivors(12)
        self.assertEqual(sorted({row["h"] for row in rows}), [1])
        self.assertEqual(
            sorted({(row["det_Q"], row["det_B"]) for row in rows}),
            [(5, 5), (9, 9)],
        )

    def test_wrong_det_q_residue_restores_spurious_h3(self) -> None:
        # This hostile enumeration deliberately allows det(Q)=3 mod 4.
        rows = []
        for h in (1, 3, 7, 9):
            for det_q in range(3, 13, 2):
                det_b = h * det_q
                if det_b <= 12 and det_b % 4 == 1:
                    rows.append((h, det_q, det_b))
        self.assertIn((3, 3, 9), rows)

    def test_h_one_signature_obstruction(self) -> None:
        self.assertTrue(check.h_one_obstruction(rank=44)["h_equals_1_excluded"])
        self.assertFalse(check.h_one_obstruction(rank=40)["h_equals_1_excluded"])

    def test_odd_scale_is_required_for_parity_transfer(self) -> None:
        with self.assertRaises(AssertionError):
            check.h_one_obstruction(rank=44, scale=2)

    def test_decimal_output_does_not_decide_bound(self) -> None:
        case = check.stationary_cases()[0]
        displayed = check.decimal_floor_text(case.product_upper)
        self.assertTrue(displayed.startswith("12.211"))
        self.assertLess(case.product_upper, Fraction(13))


if __name__ == "__main__":
    unittest.main()
