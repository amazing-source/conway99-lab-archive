"""Tests for Wave199 near-face gluing."""

import unittest

try:
    from .exact_check import derive
except ImportError:
    from exact_check import derive


class Wave199NearFaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_budget(self) -> None:
        budget = self.result["budget"]
        self.assertEqual(budget["target"], "281457/40")
        self.assertEqual(budget["value"], 23)

    def test_slack_maxima(self) -> None:
        maxima = self.result["budget"]["maxima_used"]
        self.assertEqual(maxima, {"SF": 1, "g": 2, "SH": 7, "S5": 23})

    def test_forced_saturation(self) -> None:
        deficits = self.result["orientation_deficits"]
        self.assertEqual(deficits["q_lower"], 71)
        self.assertEqual(deficits["saturated_lower"], 48)

    def test_local_cap(self) -> None:
        self.assertEqual(self.result["local_cap"]["saturated_upper"], 7)
        self.assertEqual(self.result["contradiction"], "48<=s<=7")

    def test_bound(self) -> None:
        claim = self.result["claim"]
        self.assertEqual(claim["conditional_Q_lower_bound"], 7038)
        self.assertEqual(claim["edge_added_projective"], 7731)
        self.assertEqual(claim["scalar_words"], 15462)

    def test_scope(self) -> None:
        scope = self.result["search_scope"]
        self.assertIn("no graph", scope)
        self.assertIn("brute-force", scope)


if __name__ == "__main__":
    unittest.main()
