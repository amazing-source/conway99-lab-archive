from __future__ import annotations

import os
import unittest
from fractions import Fraction

import reduction


class RootedStructuralReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixed = reduction.fixed_operators()

    def test_01_fixed_support_and_ss_block(self) -> None:
        support = self.fixed["support"]
        p = self.fixed["support_to_o"]
        self.assertEqual({sum(row) for row in support}, {Fraction(4)})
        self.assertEqual({sum(row) for row in p}, {Fraction(10)})
        self.assertEqual(
            {
                sum(p[row][col] for row in range(14))
                for col in range(70)
            },
            {Fraction(2)},
        )
        support_squared = reduction.multiply(support, support)
        pp_t = reduction.multiply(p, reduction.transpose(p))
        expected = reduction.zeros(14, 14)
        for i in range(14):
            for j in range(14):
                expected[i][j] = (
                    12 * Fraction(i == j)
                    - support[i][j]
                    + 2
                    - support_squared[i][j]
                )
        self.assertEqual(pp_t, expected)

    def test_02_kernel_and_snf_witness(self) -> None:
        p = self.fixed["support_to_o"]
        labels = self.fixed["labels"]
        self.assertEqual(reduction.rank(p), 13)
        witness = reduction.spanning_tree_minor(p, labels)
        self.assertEqual(abs(witness["determinant"]), 1)
        signed = [[Fraction(1)] for _ in range(7)] + [
            [Fraction(-1)] for _ in range(7)
        ]
        self.assertEqual(
            reduction.multiply(reduction.transpose(signed), p),
            [[Fraction(0)] * 70],
        )

    def test_03_fixed_projectors_exactly(self) -> None:
        gram = self.fixed["gram"]
        gram_plus = self.fixed["gram_plus"]
        r = self.fixed["r_projector"]
        h_r = self.fixed["h_r"]
        p = self.fixed["support_to_o"]
        c_so = self.fixed["c_so"]
        self.assertEqual(
            reduction.multiply(reduction.multiply(gram, gram_plus), gram),
            gram,
        )
        self.assertEqual(reduction.multiply(r, r), r)
        self.assertEqual(reduction.transpose(r), r)
        self.assertEqual(reduction.matrix_trace(r), 13)
        self.assertEqual(reduction.transpose(h_r), h_r)
        self.assertEqual(reduction.multiply(h_r, r), h_r)
        self.assertEqual(reduction.matrix_trace(h_r), -3)
        self.assertEqual(reduction.multiply(p, h_r), c_so)

    def test_04_integral_C_and_modular_constraint(self) -> None:
        fixed_c = self.fixed["fixed_c"]
        diagonal = {
            value: sum(fixed_c[i][i] == value for i in range(70))
            for value in {fixed_c[i][i] for i in range(70)}
        }
        off_diagonal = {}
        for i in range(70):
            for j in range(i + 1, 70):
                off_diagonal[fixed_c[i][j]] = (
                    off_diagonal.get(fixed_c[i][j], 0) + 1
                )
        self.assertEqual(diagonal, {51: 28, 57: 42})
        self.assertEqual(
            off_diagonal,
            {-6: 21, -3: 84, 0: 336, 3: 168, 6: 714, 9: 840, 12: 252},
        )
        c_mod7 = [[value % 7 for value in row] for row in fixed_c]
        self.assertEqual(reduction.rank_mod(c_mod7, 7), 5)
        self.assertTrue(
            all(
                value == 0
                for row in reduction.square_mod(c_mod7, 7)
                for value in row
            )
        )

    def test_05_projector_diagonal_and_dimension_accounting(self) -> None:
        r = self.fixed["r_projector"]
        h_r = self.fixed["h_r"]
        labels = self.fixed["labels"]
        solution_l_diagonal = []
        for i, label in enumerate(labels):
            h0_diagonal = h_r[i][i] + Fraction(11, 5) - 3 * r[i][i]
            solution_l_diagonal.append(21 * h0_diagonal)
            expected = 36 if label["incident"] else 30
            self.assertEqual(21 * h0_diagonal, expected)
        self.assertEqual(solution_l_diagonal.count(36), 42)
        self.assertEqual(solution_l_diagonal.count(30), 28)
        self.assertEqual(sum(solution_l_diagonal), 147 * 16)
        self.assertEqual(70 - 13 - 14, 43)
        self.assertEqual(43 * 44 // 2, 946)
        self.assertEqual(16 * (43 - 16), 432)

    def test_06_exact_two_factor_column_count(self) -> None:
        self.assertEqual(
            reduction.two_factor_dp(),
            {
                "underlying_capacity_bounded_multigraphs": 4_946_952,
                "labeled_binary_columns": 574_118_037,
                "dp_states": 1090,
            },
        )

    @unittest.skipUnless(
        os.environ.get("WAVE34_FULL_CENSUS") == "1",
        "set WAVE34_FULL_CENSUS=1 for the 42-second exhaustive census",
    )
    def test_07_full_cycle_census(self) -> None:
        expected = {
            "7": 262_332_336,
            "6+1": 70_294_224,
            "5+2": 91_117_740,
            "5+1+1": 9_667_812,
            "4+3": 76_574_904,
            "4+2+1": 26_163_837,
            "4+1+1+1": 920_304,
            "3+3+1": 11_738_034,
            "3+2+2": 18_854_388,
            "3+2+1+1": 4_004_196,
            "3+1+1+1+1": 69_972,
            "2+2+2+1": 2_148_384,
            "2+2+1+1+1": 227_136,
            "2+1+1+1+1+1": 4_746,
            "1+1+1+1+1+1+1": 24,
        }
        actual = reduction.full_cycle_census()
        self.assertEqual(actual, expected)
        self.assertEqual(sum(actual.values()), 574_118_037)


if __name__ == "__main__":
    unittest.main()
