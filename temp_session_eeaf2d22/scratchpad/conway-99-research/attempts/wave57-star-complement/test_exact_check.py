#!/usr/bin/env python3
"""Unit tests for the standard-library Wave57 exact checker."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave57_exact_check", HERE / "exact_check.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave57ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.run_checks(write_output=False)

    def test_frozen_inputs(self) -> None:
        CHECK.check_frozen_inputs()

    def test_quotient_spectrum(self) -> None:
        quotient = self.result["quotient_and_supported_sectors"]
        self.assertEqual(tuple(quotient["eigenvalues"]), (14, 3, -4))
        self.assertEqual(
            quotient["supported_sector"]["dimension_each"], 2
        )

    def test_projector_ranks(self) -> None:
        projectors = self.result["projectors_and_restrictions"]
        self.assertTrue(projectors["idempotence_and_orthogonality"])
        self.assertEqual(projectors["ranks"], {"E3": 54, "E_minus4": 44})

    def test_multiplicity_box(self) -> None:
        ledger = self.result["multiplicity_fourth_moment_ledger"]
        pairs = {
            (row["a_mult_Y_3"], row["b_mult_Y_minus4"])
            for row in ledger
        }
        expected = {(a, b) for a in range(18, 21) for b in range(8, 14)}
        self.assertEqual(pairs, expected)

    def test_fourth_moment_ranges(self) -> None:
        ledger = self.result["multiplicity_fourth_moment_ledger"]
        self.assertTrue(all(row["C4_X_max"] == 89 for row in ledger))
        self.assertEqual(
            next(row for row in ledger
                 if (row["a_mult_Y_3"], row["b_mult_Y_minus4"]) == (20, 13))
            ["C4_X_min"],
            65,
        )

    def test_every_pair_has_scalar_control(self) -> None:
        controls = self.result["scalar_algebraic_integer_controls"]
        self.assertEqual(len(controls), 18)
        self.assertTrue(all(row["verified"] for row in controls))
        self.assertTrue(all(not row["graph_realization_claimed"]
                            for row in controls))

    def test_quadratic_controls_cover_integer_gaps(self) -> None:
        controls = {
            (row["a_mult_Y_3"], row["b_mult_Y_minus4"]): row
            for row in self.result["scalar_algebraic_integer_controls"]
        }
        self.assertIsNotNone(controls[(20, 8)]["quadratic_factor"])
        self.assertIsNotNone(controls[(20, 9)]["quadratic_factor"])
        self.assertEqual(controls[(20, 8)]["C4_X"], 45)
        self.assertEqual(controls[(20, 9)]["C4_X"], 50)

    def test_status_does_not_inflate(self) -> None:
        conclusion = self.result["conclusion"]
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["endpoint_graph_constructed"])
        self.assertEqual(conclusion["conway_99_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
