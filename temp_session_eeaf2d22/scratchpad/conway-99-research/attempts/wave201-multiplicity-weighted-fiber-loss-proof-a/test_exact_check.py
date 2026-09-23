"""Tests for Wave201 multiplicity-weighted fiber loss."""

import unittest

try:
    from .exact_check import derive
except ImportError:
    from exact_check import derive


class Wave201WeightedFiberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_same_fiber_multiple_labels(self) -> None:
        same = self.result["local_lemma"]["same_fiber"]
        self.assertIn("k-1>=0", same["degree5_after_baseline"])
        self.assertEqual(same["degree5_empty_case"], "rho-1>=0")

    def test_three_baselines(self) -> None:
        self.assertEqual(
            self.result["local_lemma"]["tight_center_baselines"], 3
        )

    def test_global_row(self) -> None:
        elimination = self.result["global_elimination"]
        self.assertEqual(elimination["floor"], 891)
        self.assertIn("-3*eta", elimination["derived_row"])

    def test_budget_difference(self) -> None:
        budget = self.result["budget_domination"]
        self.assertTrue(budget["all_difference_coefficients_nonnegative"])
        self.assertEqual(budget["difference_coefficients"]["eta"], 8)
        self.assertEqual(budget["difference_coefficients"]["delta"], 4)

    def test_bound(self) -> None:
        claim = self.result["claim"]
        self.assertEqual(claim["improved_rational_target"], "70587/10")
        self.assertEqual(claim["conditional_Q_lower_bound"], 7059)
        self.assertEqual(claim["edge_added_projective"], 7752)
        self.assertEqual(claim["scalar_words"], 15504)

    def test_scope(self) -> None:
        scope = self.result["search_scope"]
        self.assertIn("no graph", scope)
        self.assertIn("brute-force", scope)


if __name__ == "__main__":
    unittest.main()
