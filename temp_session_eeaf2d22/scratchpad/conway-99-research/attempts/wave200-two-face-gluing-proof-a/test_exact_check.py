"""Tests for Wave200 two-face gluing."""

import unittest

try:
    from .exact_check import derive
except ImportError:
    from exact_check import derive


class Wave200TwoFaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_budgets(self) -> None:
        self.assertEqual(
            self.result["faces"]["budgets"], {"7037": 23, "7038": 63}
        )

    def test_forced_saturation(self) -> None:
        self.assertEqual(self.result["forced_saturation"]["s_lower"], 27)

    def test_local_loss(self) -> None:
        local = self.result["local_loss"]
        self.assertEqual(local["delta_max"], 12)
        self.assertEqual(local["s_upper"], 4)
        self.assertEqual(self.result["contradiction"], "27<=s<=4")

    def test_bound(self) -> None:
        claim = self.result["claim"]
        self.assertEqual(claim["conditional_Q_lower_bound"], 7039)
        self.assertEqual(claim["edge_added_projective"], 7732)
        self.assertEqual(claim["scalar_words"], 15464)

    def test_stopping_point(self) -> None:
        stop = self.result["stopping_point"]
        self.assertEqual(stop["budget"], 103)
        self.assertFalse(stop["coarse_argument_excludes"])

    def test_scope(self) -> None:
        scope = self.result["search_scope"]
        self.assertIn("no graph", scope)
        self.assertIn("brute-force", scope)


if __name__ == "__main__":
    unittest.main()
