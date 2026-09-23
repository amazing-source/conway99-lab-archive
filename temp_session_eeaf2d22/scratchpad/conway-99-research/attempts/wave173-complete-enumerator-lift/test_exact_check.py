from __future__ import annotations

import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave173_complete_enumerator_lift", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave173ExactCheckTests(unittest.TestCase):
    def test_complete_coefficient_formulas(self) -> None:
        self.assertTrue(CHECK.formula_cross_check())

    def test_forced_moments(self) -> None:
        result = CHECK.derive()["moments"]
        self.assertEqual(result["Q_total"], "13640319")
        self.assertEqual(result["T_total"], "-7617321/2")
        self.assertEqual(result["Q_remaining"], "9972963")
        self.assertEqual(result["T_remaining"], "469138959/2")

    def test_fixed_weight_198_rows(self) -> None:
        result = CHECK.derive()["moments"]
        self.assertEqual(result["Q_fixed_weight198"], "3667356")
        self.assertEqual(result["T_fixed_weight198"], "-238378140")

    def test_exact_gap(self) -> None:
        result = CHECK.derive()["moments"]
        self.assertEqual(result["T_remaining_upper_bound"], "159628644")
        self.assertEqual(result["contradiction_gap"], "149881671/2")

    def test_boundary(self) -> None:
        disposition = CHECK.derive()["disposition"]
        self.assertEqual(disposition["wave54_complete_lift"], "REFUTED")
        self.assertEqual(
            disposition["general_degree3_rational_relaxation"], "FEASIBLE"
        )
        self.assertEqual(
            disposition["all_ordinary_enumerators"], "NOT_CLASSIFIED"
        )
        self.assertEqual(disposition["endpoint"], "UNKNOWN")

    def test_paired_formula_samples(self) -> None:
        self.assertEqual(CHECK.paired_k20(18, 0), Fraction(41_412))
        self.assertEqual(CHECK.paired_k20(198, 126), Fraction(-7_485))
        self.assertEqual(CHECK.paired_k30(18, 0), Fraction(2_788_426))
        self.assertEqual(CHECK.paired_k30(198, 126), Fraction(673_921))

    def test_general_rational_control(self) -> None:
        control = CHECK.general_control_check()
        self.assertEqual(control["B30"], "2948614938535/963754929")
        self.assertTrue(all(control["checks"].values()))


if __name__ == "__main__":
    unittest.main()
