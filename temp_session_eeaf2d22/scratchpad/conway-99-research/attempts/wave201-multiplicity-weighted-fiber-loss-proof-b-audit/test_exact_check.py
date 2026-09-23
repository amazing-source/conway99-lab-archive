from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave201_b", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave201WeightedFiberAuditTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_same_fiber_multiple_values(self) -> None:
        row = MODULE.fiber_charge(
            (3, 2), {0: 3, 1: 2},
            subtract_degree_five_baseline=True,
        )
        self.assertTrue(row["valid"])
        self.assertEqual(row["residual"], 1)

    def test_empty_degree_five_fiber(self) -> None:
        row = MODULE.fiber_charge(
            (2, 1, 1, 1), {},
            subtract_degree_five_baseline=True,
        )
        self.assertTrue(row["valid"])
        self.assertEqual(row["residual"], 0)

    def test_nonbaseline_multiple_values(self) -> None:
        row = MODULE.fiber_charge(
            (2, 2), {0: 2, 1: 2},
            subtract_degree_five_baseline=False,
        )
        self.assertTrue(row["valid"])
        self.assertEqual(row["residual"], 2)

    def test_three_tight_baselines(self) -> None:
        local = MODULE.derive()["local_to_global"]
        self.assertEqual(local["tight_center_degree_five_baselines"], 3)
        self.assertEqual(local["global"], "delta>=3*q-epsilon")

    def test_budget_difference(self) -> None:
        budget = MODULE.derive()["budget_domination"]
        self.assertTrue(budget["all_nonnegative"])
        self.assertEqual(budget["difference_coefficients"]["delta"], 4)
        self.assertEqual(budget["difference_coefficients"]["eta"], 8)
        self.assertNotIn("g", budget["difference_coefficients"])
        self.assertNotIn("epsilon", budget["difference_coefficients"])

    def test_consequence(self) -> None:
        consequence = MODULE.derive()["consequence"]
        self.assertEqual(consequence["improved_rational_target"], "70587/10")
        self.assertEqual(consequence["conditional_Q_lower_bound"], 7059)
        self.assertEqual(consequence["edge_added_projective"], 7752)
        self.assertEqual(consequence["scalar_words"], 15504)


if __name__ == "__main__":
    unittest.main()
