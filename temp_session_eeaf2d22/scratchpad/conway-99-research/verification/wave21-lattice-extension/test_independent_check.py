from __future__ import annotations

import itertools
import unittest
from fractions import Fraction

import independent_check as check


class Wave21LatticeIndependentTests(unittest.TestCase):
    def test_exact_am_gm_cap(self) -> None:
        exact, cap = check.determinant_cap(12)
        self.assertEqual(cap, 45)
        self.assertLess(Fraction(45), exact)
        self.assertLess(exact, Fraction(46))

    def test_smooth_indices(self) -> None:
        self.assertEqual(check.smooth_3_7(45), [1, 3, 7, 9, 21, 27])

    def test_submitted_constraint_options(self) -> None:
        pairs = check.endpoint_pairs(use_even_determinant_congruence=False)
        self.assertEqual(sorted({row[0] for row in pairs}), [1, 3, 7, 9])

    def test_even_determinant_sharpening(self) -> None:
        pairs = check.endpoint_pairs(use_even_determinant_congruence=True)
        self.assertEqual(sorted({row[0] for row in pairs}), [1, 9])
        self.assertEqual(check.even_odd_determinant_residue(44), 1)

    def test_rank_two_even_gram_residue_exhaustively(self) -> None:
        seen = 0
        for a, b, c in itertools.product(range(-2, 3), repeat=3):
            matrix = [[2 * a, b], [b, 2 * c]]
            determinant = check.determinant(matrix)
            if determinant % 2:
                seen += 1
                self.assertEqual(determinant % 4, 3)
        self.assertGreater(seen, 0)

    def test_rank_four_even_gram_residue_exhaustively_mod_four(self) -> None:
        # Exhaust all symmetric representatives modulo four: 2^4 diagonal
        # choices and 4^6 off-diagonal choices.
        seen = 0
        for diagonal_halves in itertools.product(range(2), repeat=4):
            for off_diagonal in itertools.product(range(4), repeat=6):
                matrix = [[0] * 4 for _ in range(4)]
                for index, value in enumerate(diagonal_halves):
                    matrix[index][index] = 2 * value
                cursor = 0
                for row in range(4):
                    for column in range(row + 1, 4):
                        value = off_diagonal[cursor]
                        cursor += 1
                        matrix[row][column] = value
                        matrix[column][row] = value
                determinant = check.determinant(matrix)
                if determinant % 2:
                    seen += 1
                    self.assertEqual(determinant % 4, 1)
        self.assertGreater(seen, 0)

    def test_projection_index_direction(self) -> None:
        self.assertEqual(
            check.rank_one_projection_index((1, 1), 2)["index_direct"],
            1,
        )
        self.assertEqual(
            check.rank_one_projection_index((1, 2), 10)["index_direct"],
            2,
        )

    def test_harmonic_entries(self) -> None:
        self.assertEqual(
            check.harmonic_entries(),
            {4: 1376, 1: -1, 0: 0, -1: 1, -2: -136},
        )

    def test_harmonic_row_formula(self) -> None:
        for q in range(13):
            self.assertEqual(check.harmonic_row_sum(q), 138 * (q - 2))

    def test_harmonic_cauchy_endpoint(self) -> None:
        endpoint = check.harmonic_endpoint()
        self.assertEqual(endpoint["rejected_q"], [11, 12])
        self.assertIn(10, endpoint["allowed_q"])

    def test_traceless_bound_coefficient(self) -> None:
        self.assertEqual(check.contraction_bound(0), Fraction(396, 43))
        self.assertEqual(check.contraction_bound(6), Fraction(1584, 43))

    def test_contraction_floors(self) -> None:
        expected = {
            0: 12,
            1: 4,
            2: 4,
            3: 4,
            4: 12,
            5: 24,
            6: 40,
            7: 60,
            8: 84,
            9: 116,
            10: 148,
            11: 188,
            12: 232,
        }
        self.assertEqual(
            {q: check.contraction_floor(q) for q in range(13)},
            expected,
        )

    def test_endpoint_dp_and_witness(self) -> None:
        cost, profile = check.minimum_profile_cost(
            231,
            470,
            forbid_q_one=True,
        )
        self.assertEqual(cost, 924)
        self.assertEqual(profile, {2: 223, 3: 8})

    def test_q_one_hostile_mutation(self) -> None:
        cost, _ = check.minimum_profile_cost(
            231,
            470,
            forbid_q_one=False,
        )
        self.assertEqual(cost, 924)

    def test_h_at_least_twenty_one_excludes_endpoint(self) -> None:
        for h in check.smooth_3_7(45):
            if h >= 21:
                self.assertGreater(h * 3, 45)

    def test_full_audit_boundary(self) -> None:
        result = check.audit()
        self.assertFalse(result["boundary"]["unconditional_improvement"])
        self.assertFalse(result["boundary"]["index_h_determined"])
        self.assertEqual(
            result["audit_label"],
            "VERIFIED_SCOPED_WITH_NONBLOCKING_STRENGTHENING",
        )


if __name__ == "__main__":
    unittest.main()
