from __future__ import annotations

import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave86_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave86ExactTests(unittest.TestCase):
    def test_space_dimension_and_sturm_coordinates(self) -> None:
        basis = MODULE.independent_basis()
        self.assertEqual(len(basis), 15)
        self.assertEqual(MODULE.STURM, 14)

    def test_fricke_is_an_involution(self) -> None:
        _, fricke = MODULE.fricke_matrix()
        square = MODULE.matmul(fricke, fricke)
        self.assertEqual(
            square,
            [
                [Fraction(i == j) for j in range(15)]
                for i in range(15)
            ],
        )

    def test_theta_fricke_sign_and_power(self) -> None:
        result = MODULE.exact_result()
        self.assertEqual(
            result["theta_transfer"]["relation"],
            "Theta_L=-7^3*(Theta_K|W_7)",
        )
        x = result["formal_scalar_control"]["x0_to_x14"]
        _, fricke = MODULE.fricke_matrix()
        wrong_sign_constant = sum(
            Fraction(7**3) * fricke[0][j] * x[j] for j in range(15)
        )
        wrong_power_constant = sum(
            -Fraction(7**2) * fricke[0][j] * x[j] for j in range(15)
        )
        self.assertEqual(wrong_sign_constant, -1)
        self.assertEqual(wrong_power_constant, Fraction(1, 7))

    def test_exact_positive_coefficient_identity(self) -> None:
        result = MODULE.exact_result()
        identity = result["coefficient_identity"]
        self.assertEqual(identity["rational_lower_bound"], "1997236/341")
        self.assertEqual(identity["forced_integer_lower_bound"], 5868)
        self.assertEqual(identity["wave71_congruence"], "x7+x8+x9=2 mod 14")

    def test_formal_control_is_not_promoted(self) -> None:
        result = MODULE.exact_result()
        control = result["formal_scalar_control"]
        self.assertTrue(control["not_a_lattice_or_graph"])
        self.assertEqual(control["attains_short_sum"], 5868)
        self.assertEqual(result["status"]["q16_excluded"], False)
        self.assertEqual(result["status"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
