"""Tests for post-freeze Wave202 source comparison."""

import unittest

try:
    from .source_comparison_check import derive, m1_margin
except ImportError:
    from source_comparison_check import derive, m1_margin


class Wave202SourceComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_center_sizes(self) -> None:
        costs = self.result["center_sizes"]["costs"]
        self.assertGreater(costs["11"]["combined_cost"], 3)
        self.assertEqual(
            self.result["center_sizes"]["conclusion"],
            "c_x is 12 or 13 at every center",
        )

    def test_baseline_m1_margin(self) -> None:
        result = m1_margin(
            (1, 2, 1, 1),
            {0: 1},
            degree_five_baseline=True,
        )
        self.assertEqual(result["m1_values"], 1)
        self.assertEqual(result["local_term"], 1)
        self.assertEqual(result["margin_over_m1"], 0)

    def test_multiple_m1_values(self) -> None:
        result = m1_margin(
            (1, 1, 2, 1),
            {0: 1, 1: 1},
            degree_five_baseline=True,
        )
        self.assertEqual(result["m1_values"], 2)
        self.assertGreaterEqual(result["local_term"], 2)

    def test_global_m1_cap(self) -> None:
        self.assertEqual(
            self.result["multiplicity_one"]["global_conclusion"],
            "r<=SM<=3",
        )

    def test_two_center_null(self) -> None:
        two = self.result["two_center"]
        self.assertTrue(two["m1_orientation_forces_opposite_occupied"])
        self.assertFalse(two["opposite_multiplicity_forced_to_one"])
        self.assertFalse(two["parity_obstruction"])
        self.assertFalse(two["cross_center_fibre_multiset_coupling_available"])


if __name__ == "__main__":
    unittest.main()
