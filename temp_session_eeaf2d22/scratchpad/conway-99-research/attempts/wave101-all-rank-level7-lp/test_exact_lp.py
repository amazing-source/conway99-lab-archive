"""Regression tests for the Wave 101 discovery calculation.

These tests replay exact arithmetic but are not an independent verification.
"""

from __future__ import annotations

import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave101_exact_lp", HERE / "exact_lp.py")
assert SPEC is not None and SPEC.loader is not None
WAVE101 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WAVE101)


class Wave101ExactLPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = WAVE101.build_results()
        cls.rows = {
            row["q_discriminant_length_L"]: row
            for row in cls.result["rows"]
        }

    def test_complete_modular_space_and_frozen_inputs(self) -> None:
        WAVE101.check_frozen_inputs()
        modular = self.result["modular_space"]
        self.assertEqual(modular["dimension"], 15)
        self.assertEqual(modular["sturm_bound"], 14)
        self.assertEqual(len(modular["basis_products"]), 15)
        self.assertTrue(modular["fricke_involution_exact"])

    def test_all_seven_rows_and_poisson_powers(self) -> None:
        self.assertEqual(sorted(self.rows), [2, 4, 6, 8, 10, 12, 14])
        for q_value, row in self.rows.items():
            exponent = 11 - q_value // 2
            self.assertEqual(
                row["poisson_relation"],
                f"Theta_L=-7^{exponent}*(Theta_K|W_7)",
            )
            self.assertEqual(row["r_rank_F7_Seidel"], 44 - q_value)

    def test_exact_total_bounds(self) -> None:
        expected_rational = {
            2: "717848/3971",
            4: "6286208/3971",
            6: "45264728/3971",
            8: "28919488/361",
            10: "2228061848/3971",
            12: "15580466396938/82045",
            14: "6793429016900/3709",
        }
        expected_even = {
            2: 182,
            4: 1584,
            6: 11400,
            8: 80110,
            10: 561084,
            12: 189901474,
            14: 1831606638,
        }
        for q_value, row in self.rows.items():
            total = row["certificates"][0]
            self.assertEqual(total["name"], "total_through_norm_28")
            self.assertEqual(
                total["rational_lp_optimum"], expected_rational[q_value]
            )
            self.assertEqual(
                total["even_integer_lower_bound"], expected_even[q_value]
            )

    def test_first_positive_prefixes(self) -> None:
        expected = {
            2: (13, 166),
            4: (12, 142),
            6: (12, 1328),
            8: (12, 9626),
            10: (11, 932),
            12: (11, 9748),
            14: (10, 6842),
        }
        for q_value, (end, lower) in expected.items():
            name = f"prefix_through_norm_{2 * end}"
            certificate = next(
                item
                for item in self.rows[q_value]["certificates"]
                if item["name"] == name
            )
            self.assertEqual(certificate["even_integer_lower_bound"], lower)
            zero_control = self.rows[q_value]["zero_prefix_null_control"]
            self.assertEqual(
                zero_control["last_prefix_with_exact_zero_lp_optimum"],
                f"x7+...+x{end - 1}",
            )

    def test_duals_primal_controls_and_mod7_status(self) -> None:
        for row in self.rows.values():
            for certificate in row["certificates"]:
                dual = certificate["dual_identity"]
                self.assertTrue(dual["all_multipliers_nonnegative"])
                for multiplier in dual["nonnegative_terms"].values():
                    self.assertGreaterEqual(Fraction(multiplier), 0)
                primal = certificate["exact_primal_optimizer"]
                self.assertTrue(primal["all_required_coefficients_nonnegative"])
                self.assertFalse(
                    certificate["wave71_mod7_check"]["fixed_residue"]
                )

    def test_no_upper_bound_contradiction(self) -> None:
        for row in self.rows.values():
            for certificate in row["certificates"]:
                comparison = certificate["rigorous_upper_comparison"]
                self.assertFalse(comparison["lower_bound_exceeds_upper"])
                self.assertFalse(comparison["contradiction"])
        self.assertFalse(
            self.result["global_assessment"][
                "any_rigorous_upper_bound_contradiction"
            ]
        )

    def test_zero_controls_are_even_integral_and_nonnegative(self) -> None:
        for q_value, row in self.rows.items():
            control = row["zero_prefix_null_control"]
            self.assertTrue(
                control["integral_even_nonnegative_first_15_coefficients"]
            )
            end = WAVE101.LAST_ZERO_PREFIX[q_value]
            for index in range(7, end + 1):
                self.assertEqual(Fraction(control["x7_to_x14"][f"x{index}"]), 0)
            for value in (
                list(control["x7_to_x14"].values())
                + list(control["y1_to_y14"].values())
            ):
                parsed = Fraction(value)
                self.assertGreaterEqual(parsed, 0)
                self.assertEqual(parsed.denominator, 1)
                self.assertEqual(parsed.numerator % 2, 0)

    def test_signed_unit_scope_is_not_extended(self) -> None:
        assessment = self.result["global_assessment"]
        self.assertIn("x7,x8,x9", assessment["short_signed_unit_range"])
        self.assertEqual(assessment["conway_99"], "UNKNOWN")
        self.assertEqual(assessment["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
