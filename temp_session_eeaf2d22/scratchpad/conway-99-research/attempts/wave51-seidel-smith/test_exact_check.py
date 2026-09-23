import json
import unittest
from pathlib import Path

import exact_check as ec


class ExactCheckTests(unittest.TestCase):
    def test_seidel_polynomial_expansion(self) -> None:
        # Expand (2A-J+I)^2 using A^2=12I-A+2J,
        # AJ=JA=14J, J^2=99J.
        coefficient_i = 4 * 12 + 1
        coefficient_a = 4 * (-1) + 4
        coefficient_j = 4 * 2 + 99 - 4 * 14 - 2
        self.assertEqual((coefficient_i, coefficient_a, coefficient_j), (49, 0, 49))

    def test_rank_of_pure_square_gram(self) -> None:
        self.assertEqual(ec.rank_mod(ec.j_minus_i(99), 7), 98)

    def test_symmetric_square_boundary(self) -> None:
        self.assertEqual(ec.symmetric_square_floor(98), 14)
        self.assertLess(13 * 14 // 2, 98)
        self.assertGreaterEqual(14 * 15 // 2, 98)

    def test_jordan_profiles(self) -> None:
        for rank in range(50):
            profile = ec.jordan_profile_mod_7(rank)
            self.assertEqual(
                2 * profile["J2_zero_blocks"] + profile["J1_zero_blocks"], 99
            )
            self.assertEqual(profile["J2_zero_blocks"], rank)

    def test_all_conditional_smith_profiles(self) -> None:
        for rank in range(1, 50):
            with self.subTest(rank=rank):
                self.assertTrue(ec.validate_smith_profile(rank)["all_checks_pass"])

    def test_last_factor_carries_two_and_five(self) -> None:
        factors = ec.smith_factors(28)
        self.assertEqual(factors[-1], 490)
        self.assertEqual(ec.modular_rank_from_smith(factors, 2), 98)
        self.assertEqual(ec.modular_rank_from_smith(factors, 5), 98)

    def test_endpoint_is_not_excluded(self) -> None:
        result = ec.build_results()["endpoint"]
        self.assertEqual(result["surviving_integer_ranks"], list(range(28, 45)))
        self.assertEqual(result["survivor_count"], 17)
        self.assertFalse(result["contradiction_found"])

    def test_committed_result_is_canonical_recomputation(self) -> None:
        path = Path(__file__).with_name("exact-results.json")
        payload = ec.build_results()
        self.assertEqual(path.read_bytes(), ec.canonical_bytes(payload))
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), payload)


if __name__ == "__main__":
    unittest.main()

