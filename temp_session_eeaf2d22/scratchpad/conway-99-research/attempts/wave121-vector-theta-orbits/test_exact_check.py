"""Regression tests for the sealed Wave 121 discovery calculation."""

from __future__ import annotations

import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave121_exact_check", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
WAVE121 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WAVE121)


class Wave121ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = WAVE121.build_results()

    def test_frozen_inputs_and_memory_budget(self) -> None:
        WAVE121.check_frozen_inputs()
        self.assertGreaterEqual(WAVE121.free_memory_percent(), 15.0)

    def test_minus_orbit_counts(self) -> None:
        for dimension in (14, 30):
            counts = WAVE121.orbit_counts(dimension)
            self.assertEqual(
                counts["zero"]
                + counts["nonzero_isotropic"]
                + counts["all_six_nonzero_values"],
                7**dimension,
            )
            self.assertEqual(
                counts["all_six_nonzero_values"],
                6 * counts["each_exact_nonzero_value"],
            )

    def test_exact_value_not_projective_reduction(self) -> None:
        spaces = self.result["quadratic_spaces"]
        self.assertIn("exact quadratic value", spaces["justified_reduction"])
        self.assertIn(
            "coordinate compositions", spaces["projective_reduction_rejected"]
        )
        known = self.result["coordinate_and_code_boundary"][
            "known_frozen_compositions"
        ]
        self.assertEqual([row["code_self_dot_mod7"] for row in known], [0, 4, 1])

    def test_orbit_inequality_dictionary(self) -> None:
        dictionary = self.result["orbit_theta_dictionary"]
        self.assertIn("x_(7m)-y_m", dictionary["L_discriminant_nonzero_isotropic"])
        self.assertIn("y_(7n)-x_n", dictionary["K_discriminant_nonzero_isotropic"])

    def test_prefix_optima_survive_added_constraints(self) -> None:
        bounds = self.result["prefix_bounds"]
        self.assertEqual(
            Fraction(bounds["through_norm_20"]["exact_optimum"]),
            Fraction(389888, 57),
        )
        self.assertEqual(
            Fraction(bounds["through_norm_22"]["exact_optimum"]),
            Fraction(4675706896, 9307),
        )
        for row in bounds.values():
            self.assertTrue(row["unchanged_from_verified_wave101"])
            self.assertTrue(
                row["extended_primal_control"][
                    "all_extended_coefficients_nonnegative"
                ]
            )

    def test_conditional_forcing_identities(self) -> None:
        conditional = self.result["conditional_no_norm_14_16_18"]
        self.assertTrue(conditional["x10_lower_bound"]["identity_exact"])
        self.assertTrue(
            conditional["x10_plus_x11_lower_bound"]["identity_exact"]
        )
        self.assertEqual(conditional["x10_lower_bound"]["value"], 2729216)
        self.assertEqual(
            conditional["x10_plus_x11_lower_bound"]["value"], 4144144
        )

    def test_even_integral_null_control(self) -> None:
        conditional = self.result["conditional_no_norm_14_16_18"]
        rational = conditional["x10_plus_x11_lower_bound"][
            "attaining_extended_rational_control"
        ]
        self.assertTrue(rational["all_extended_coefficients_nonnegative"])
        self.assertFalse(rational["all_extended_coefficients_integral"])
        control = conditional["formal_even_integral_null_control"]
        self.assertTrue(control["all_extended_coefficients_nonnegative"])
        self.assertTrue(control["all_extended_coefficients_integral"])
        self.assertTrue(control["all_nonconstant_coefficients_even"])
        self.assertEqual(control["x7_to_x14"]["x7"], "0")
        self.assertEqual(control["x7_to_x14"]["x8"], "0")
        self.assertEqual(control["x7_to_x14"]["x9"], "0")
        self.assertEqual(control["x7_to_x14"]["x10"], "2729216")
        self.assertEqual(control["x7_to_x14"]["x11"], "9904496")

    def test_upper_bound_has_slack_and_status_is_unknown(self) -> None:
        boundary = self.result["coordinate_and_code_boundary"]
        lower = self.result["conditional_no_norm_14_16_18"][
            "x10_plus_x11_lower_bound"
        ]["value"]
        self.assertGreater(
            boundary["abstract_anisotropic_codeword_upper_each_exact_value"],
            lower,
        )
        self.assertFalse(boundary["upper_bound_contradiction"])
        endpoint = self.result["boundary"]
        self.assertFalse(endpoint["rank30_excluded"])
        self.assertEqual(endpoint["Conway_99"], "UNKNOWN")
        self.assertEqual(endpoint["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
