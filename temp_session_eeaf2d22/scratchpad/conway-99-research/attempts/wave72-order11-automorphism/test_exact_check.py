"""Hostile unit tests for the Wave 72 exact arithmetic audit."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave72_exact_check", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FixedPointTheoremTests(unittest.TestCase):
    def test_prime_orbit_fixed_counts_are_exhaustive(self) -> None:
        self.assertEqual(list(range(0, MODULE.V + 1, MODULE.P)), [0, 11, 22, 33, 44, 55, 66, 77, 88, 99])

    def test_fixed_neighborhood_degree_options_are_exact(self) -> None:
        self.assertEqual(MODULE.fixed_degree_options(), [3, 14])

    def test_f11_formal_local_solution_requires_impossible_high_type(self) -> None:
        # The two-step equation alone would give a degree-3 vertex one
        # degree-14 neighbor.  But a simple graph on 11 vertices cannot have
        # a degree-14 vertex, so the full model correctly rejects the branch.
        self.assertEqual(MODULE.local_type_solution(11, 3), 1)
        self.assertIsNone(MODULE.local_type_solution(11, 14))
        self.assertNotIn(11, [model["f"] for model in MODULE.feasible_fixed_degree_models()])

    def test_f22_forces_cross_type_neighbors(self) -> None:
        self.assertEqual(MODULE.local_type_solution(22, 3), 3)
        self.assertEqual(MODULE.local_type_solution(22, 14), 0)

    def test_f22_cross_edge_balance_is_impossible(self) -> None:
        solutions = [
            (a, b)
            for a in range(23)
            for b in range(23)
            if a + b == 22 and 3 * a == 14 * b
        ]
        self.assertEqual(solutions, [])

    def test_only_empty_and_identity_degree_models_survive(self) -> None:
        models = MODULE.feasible_fixed_degree_models()
        self.assertEqual([model["f"] for model in models], [0, 99])
        self.assertEqual(models[1]["degree14_vertices"], 99)
        self.assertEqual(models[1]["degree14_neighbors_of_degree14_vertex"], 14)

    def test_order_exactly_11_removes_identity_model(self) -> None:
        models = MODULE.feasible_fixed_degree_models()
        nonidentity_positive = [model for model in models if 0 < model["f"] < 99]
        self.assertEqual(nonidentity_positive, [])

    def test_fixed_free_action_has_nine_orbits(self) -> None:
        self.assertEqual(MODULE.V // MODULE.P, 9)
        self.assertEqual(MODULE.V % MODULE.P, 0)

    def test_sealed_result_verifies(self) -> None:
        MODULE.verify_result(MODULE.build_result())


if __name__ == "__main__":
    unittest.main()
