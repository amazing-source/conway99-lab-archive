"""Regression tests for the Wave 121 one-variable C4 Jacobi audit."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave121_scalar_jacobi", HERE / "scalar_jacobi_check.py"
)
assert SPEC is not None and SPEC.loader is not None
SCALAR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCALAR)


class Wave121ScalarJacobiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = SCALAR.build_results()

    def test_frozen_inputs_and_memory(self) -> None:
        SCALAR.check_frozen_inputs()
        self.assertGreaterEqual(SCALAR.free_memory_percent(), 15.0)

    def test_alternating_vector_membership_and_norm(self) -> None:
        row = self.result["alternating_vector"]
        self.assertEqual(row["norm_d"], 20)
        self.assertTrue(row["primitive_in_L"])
        self.assertEqual(row["divisibility_in_L"], 1)
        self.assertIn("d_C in M", row["membership"])

    def test_reduced_markings(self) -> None:
        markings = self.result["markings"]
        self.assertEqual(markings["K"]["norm"], 140)
        self.assertEqual(markings["K"]["ordinary_scalar_Jacobi_index"], 70)
        self.assertEqual(markings["K"]["divisibility"], 7)
        self.assertEqual(
            markings["L_Fricke_partner"]["ordinary_scalar_Jacobi_index"], 10
        )
        self.assertEqual(
            markings["comparison_to_wave116"]["index_reduction_factor"], 9
        )

    def test_target_fourier_coefficient(self) -> None:
        target = self.result["incidence_coefficient"]
        self.assertEqual(target["K_Fourier_exponent"], 28)
        self.assertIn("iff", target["equivalence"])
        self.assertEqual(target["rank28_lower"], 52812)
        self.assertEqual(target["gap"], 837)

    def test_twenty_component_reduction(self) -> None:
        theta = self.result["theta_decomposition"]
        self.assertEqual(theta["K_naive_residue_count"], 140)
        self.assertEqual(theta["reduced_component_count"], 20)
        self.assertEqual(theta["after_z_to_minus_z_symmetry"], 11)
        self.assertEqual(theta["K_live_residues"], [7 * s for s in range(20)])

    def test_support_permits_all_targets(self) -> None:
        support = self.result["support"]
        self.assertEqual(
            support["margins"], {"7": 1176, "8": 1456, "9": 1736, "10": 2016}
        )
        self.assertTrue(support["all_q7_through_q10_targets_permitted"])

    def test_truncated_null_control(self) -> None:
        control = self.result["truncated_coefficient_cone"]
        coefficients = control["explicit_control"]
        self.assertEqual(coefficients["c(7,-28)"], coefficients["c(7,28)"])
        self.assertEqual(
            sum(
                coefficients[key]
                for key in ("c(7,-28)", "c(7,0)", "c(7,28)")
            ),
            control["q7_row_total"],
        )
        self.assertEqual(control["target_coefficient_sum"], 52812)
        self.assertTrue(control["exceeds_contradiction_threshold"])

    def test_status_boundary(self) -> None:
        assessment = self.result["basis_LP_assessment"]
        self.assertFalse(assessment["proof_producing_full_basis_constructed"])
        self.assertFalse(assessment["upper_bound_proved"])
        boundary = self.result["boundary"]
        self.assertFalse(boundary["rank28_excluded"])
        self.assertEqual(boundary["Conway_99"], "UNKNOWN")
        self.assertEqual(boundary["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
