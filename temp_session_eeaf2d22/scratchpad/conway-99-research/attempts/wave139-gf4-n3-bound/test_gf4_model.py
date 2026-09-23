"""Exact unit controls for the GF(4) invariant basis."""

from __future__ import annotations

import unittest

import gf4_model as model


class GF4ModelTests(unittest.TestCase):
    def test_dimensions(self):
        self.assertEqual(len(model.states()), 2550)
        self.assertEqual(len(model.partitions3()), 867)
        self.assertEqual(
            model.exact_rank_record()["combined_equality_rank"], 1683
        )

    def test_basis_coefficient_sums(self):
        states = model.states()
        for partition in (
            (99, 0, 0),
            (50, 49, 0),
            (33, 33, 33),
        ):
            self.assertEqual(
                sum(
                    model.basis_coefficient(partition, state)
                    for state in states
                ),
                model.basis_evaluation(partition),
            )

    def test_forced_target(self):
        self.assertEqual(model.TARGET_STATE, (41, 4, 54))
        self.assertEqual(model.lower_bounds()[model.TARGET_STATE], 708)


if __name__ == "__main__":
    unittest.main()
