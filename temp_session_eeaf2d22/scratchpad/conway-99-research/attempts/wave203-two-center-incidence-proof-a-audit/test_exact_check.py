"""Tests for the Wave203 proof-A hostile audit."""

import unittest

try:
    from .exact_check import derive
except ImportError:
    from exact_check import derive


class Wave203ProofAAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_relation_addition(self) -> None:
        relations = self.result["paired_relations"]
        self.assertEqual(relations["leaf_coefficients"], [1, 1])
        self.assertEqual(relations["sum"], [0, 0, 2, 2, 2, 2])
        self.assertTrue(relations["common_columns_pairwise_distinct"])

    def test_gram(self) -> None:
        gram = self.result["gram"]
        self.assertEqual(gram["rank_mod3"], 3)
        self.assertFalse(gram["all_equal_in_kernel"])
        self.assertTrue(gram["checkerboard_in_kernel"])

    def test_slots(self) -> None:
        slots = self.result["slots"]
        self.assertEqual(slots["count"], 5)
        self.assertEqual(slots["combined_selected_capacity"], 5)
        self.assertEqual(slots["matched_occupancy"], "REFUTED")

    def test_selected_row(self) -> None:
        consequences = self.result["consequences"]
        self.assertEqual(
            consequences["selected_rearranged"], "3*n3+4*p3<=5*|U|"
        )
        self.assertEqual(consequences["both_oriented"], "epsilon>=5*b")

    def test_low_patterns(self) -> None:
        self.assertEqual(
            self.result["consequences"]["low_patterns"],
            {"1,1": 8, "1,2": 7, "2,2": 6},
        )

    def test_no_bound_inflation(self) -> None:
        boundary = self.result["boundary"]
        self.assertFalse(boundary["b_forced_positive"])
        self.assertFalse(boundary["Q0_7059_excluded"])
        self.assertEqual(boundary["conditional_Q_lower_bound"], 7059)

    def test_scope(self) -> None:
        scope = self.result["search_scope"]
        self.assertIn("no graph", scope)
        self.assertIn("brute-force", scope)


if __name__ == "__main__":
    unittest.main()
