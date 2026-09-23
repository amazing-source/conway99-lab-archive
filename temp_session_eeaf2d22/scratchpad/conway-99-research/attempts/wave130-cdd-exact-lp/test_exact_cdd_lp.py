"""Focused tests for the Wave130 exact cddlib path."""

from __future__ import annotations

import unittest
from fractions import Fraction as Q

import cdd.gmp as cdd

import exact_cdd_lp as BASE
import incremental_cdd_lp as INCREMENTAL


class ExactCddTests(unittest.TestCase):
    def test_primitive_scale_preserves_row(self) -> None:
        source = [Q(2, 3), Q(-5, 14), Q(0), Q(11, 6)]
        scale, primitive = BASE.primitive_scale(source)
        self.assertGreater(scale, 0)
        self.assertEqual(
            [scale * value for value in source],
            [Q(value) for value in primitive],
        )

    def test_cutoff_label_parser(self) -> None:
        self.assertEqual(
            INCREMENTAL.label_cutoff("K:positive:n28:r-21"), 28
        )
        self.assertIsNone(INCREMENTAL.label_cutoff("K:constant"))

    def test_exact_margin_dual_is_farkas_certificate(self) -> None:
        # x >= 1 and x <= 0.  The common-margin optimum is -1/2,
        # with exact dual multipliers (1/2, 1/2).
        array = [
            [-1, 1, -1],
            [0, -1, -1],
            [0, 0, 1],
        ]
        lp = cdd.linprog_from_array(
            array, obj_type=cdd.LPObjType.MAX
        )
        cdd.linprog_solve(lp, cdd.LPSolverType.DUAL_SIMPLEX)
        self.assertEqual(lp.status, cdd.LPStatusType.OPTIMAL)
        self.assertEqual(Q(lp.obj_value), Q(-1, 2))
        dual = [Q(0), Q(0)]
        for index, value in lp.dual_solution:
            dual[index] = Q(value)
        self.assertEqual(dual, [Q(1, 2), Q(1, 2)])
        self.assertEqual(sum(dual), 1)
        self.assertEqual(dual[0] - dual[1], 0)
        self.assertEqual(-dual[0], Q(-1, 2))


if __name__ == "__main__":
    unittest.main()
