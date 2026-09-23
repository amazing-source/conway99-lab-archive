"""Focused standard-library tests for the Wave134 checkpoint."""

from __future__ import annotations

import unittest
from math import comb

import exact_check as check


class Wave134Tests(unittest.TestCase):
    def test_code_types_and_orders(self) -> None:
        result = check.derive(None)
        self.assertEqual(result["code_types"]["C"]["type"], "4^54 2^1")
        self.assertEqual(
            result["code_types"]["Cperp"]["type"], "4^44 2^1"
        )
        self.assertEqual(result["smith_replay"]["rank_F2"], 54)
        self.assertEqual(result["smith_replay"]["rank_F3"], 45)

    def test_state_quotient(self) -> None:
        self.assertEqual(comb(101, 2), 5050)
        self.assertEqual(len(check.primal_states()), 1119)
        self.assertEqual(len(check.dual_states()), 1114)
        self.assertEqual(len(check.forbidden_dual_states()), 161)

    def test_forced_primal_counts(self) -> None:
        table = check.forced_primal()
        self.assertEqual(len(table), 42)
        self.assertEqual(2 * len(table), 84)
        self.assertEqual(2 * sum(table.values()), 8557760)
        self.assertEqual(table[(85, 14, 0)], 198)
        self.assertEqual(table[(72, 26, 1)], 1386)

    def test_forced_dual_sum_and_difference_are_distinct(self) -> None:
        table = check.forced_dual()
        self.assertEqual(len(table), 22)
        self.assertEqual(2 * len(table), 44)
        self.assertEqual(2 * sum(table.values()), 4126784)
        self.assertEqual(table[(72, 24, 3)], 1386)
        self.assertEqual(table[(75, 24, 0)], 1386)
        self.assertEqual(table[(71, 26, 2)], 8316)
        self.assertEqual(table[(73, 26, 0)], 8316)

    def test_transform_zero_monomial(self) -> None:
        for target in ((99, 0, 0), (85, 14, 0), (72, 24, 3)):
            a, b, c = target
            expected = comb(99, b) * comb(99 - b, c) * (1 << b)
            self.assertEqual(
                check.transform_coefficient((99, 0, 0), target),
                expected,
            )


if __name__ == "__main__":
    unittest.main()
