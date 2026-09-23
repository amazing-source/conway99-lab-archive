"""Tests for the sealed Wave 124 discovery arithmetic."""

from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave124_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave124Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = CHECK.build_results()

    def test_frozen_inputs(self) -> None:
        CHECK.verify_frozen_inputs()
        self.assertEqual(len(self.results["frozen_inputs"]), 4)

    def test_marking_norm_index_and_divisibility(self) -> None:
        row = self.results["c4_marking"]
        self.assertEqual(row["norm_d"], 20)
        self.assertEqual(row["norm_b"], 140)
        self.assertEqual(row["K_index"], 70)
        self.assertEqual(row["L_partner_index"], 10)
        self.assertEqual(row["divisibility_in_K"], 7)
        self.assertTrue(row["primitive_in_L"])

    def test_exact_shell_selection_through_norm20(self) -> None:
        row = self.results["coefficient_selection"]
        self.assertEqual([item["q_exponent"] for item in row["rows"]], [7, 8, 9, 10])
        self.assertTrue(all(item["K_fourier_exponent"] == 28 for item in row["rows"]))
        self.assertEqual(row["oriented_count_factor"], 2)

    def test_even_indicator(self) -> None:
        coefficients = [
            Fraction(value)
            for value in self.results["coefficient_selection"]["degree8_even_indicator"][
                "coefficients_low_to_high"
            ]
        ]
        for value in range(-4, 5):
            evaluated = sum(
                coefficient * Fraction(value) ** degree
                for degree, coefficient in enumerate(coefficients)
            )
            self.assertEqual(evaluated, int(abs(value) == 4))

    def test_frame_and_moments(self) -> None:
        frame = self.results["tight_frame"]
        self.assertEqual(83 - 13 * (-4), 135)
        self.assertEqual(135 * 7, 945)
        self.assertEqual(frame["eigenvalue_on_minus4_space"], 135)
        self.assertEqual(frame["forced_L_boundary_coefficient"]["value"], 2079)
        self.assertIn("13230", frame["K_second_moment"])
        self.assertIn("1890", frame["L_second_moment"])

    def test_weak_generators(self) -> None:
        aa = CHECK.phi_minus2(2)
        bb = CHECK.phi_zero(2)
        self.assertEqual(
            [aa.get((0, r), 0) for r in (-1, 0, 1)],
            [1, -2, 1],
        )
        self.assertEqual(
            [bb.get((0, r), 0) for r in (-1, 0, 1)],
            [1, 10, 1],
        )
        self.assertEqual(aa[(1, 0)], -12)
        self.assertEqual(bb[(1, 0)], 108)

    def test_full_level_dimensions_and_basis(self) -> None:
        audit = self.results["full_level_basis_audit"]
        self.assertEqual(audit["weak_monomial_count"], 34)
        self.assertEqual(audit["holomorphic_dimension"], 18)
        self.assertEqual(audit["cusp_dimension"], 17)
        self.assertEqual(len(audit["holomorphic_basis_monomial_coordinates"]), 18)
        self.assertEqual(len(audit["cusp_basis_monomial_coordinates"]), 17)
        self.assertTrue(all(len(vector) == 34 for vector in audit[
            "holomorphic_basis_monomial_coordinates"
        ]))

    def test_holomorphic_basis_has_no_polar_terms(self) -> None:
        _monomials, expansions = CHECK.monomial_expansions()
        audit = self.results["full_level_basis_audit"]
        columns = list(range(len(expansions)))
        for vector in audit["holomorphic_basis_monomial_coordinates"]:
            form = CHECK.linear_combination(
                expansions,
                columns,
                [Fraction(value) for value in vector],
            )
            self.assertFalse(
                any(4 * CHECK.INDEX_L * n - r * r < 0 for n, r in form)
            )

    def test_scalar_and_moment_invisible_directions(self) -> None:
        directions = self.results["full_level_basis_audit"][
            "scalar_invisible_fricke_directions_by_A_power"
        ]
        self.assertEqual([row["minimum_A_power"] for row in directions], [1, 2, 3, 4, 5])
        self.assertTrue(all(row["exists"] for row in directions))
        self.assertGreater(Fraction(directions[1]["target_coefficient"]), 0)
        self.assertGreaterEqual(directions[1]["vanishing_order_at_z_zero_at_least"], 4)
        self.assertGreaterEqual(directions[4]["vanishing_order_at_z_zero_at_least"], 10)

    def test_fricke_residue_split_and_status_wall(self) -> None:
        fricke = self.results["fricke_pair"]
        self.assertEqual((fricke["K_index"], fricke["L_index"]), (70, 10))
        self.assertTrue(fricke["not_fixed_index"])
        self.assertEqual(fricke["K_r_divisibility"], 7)
        self.assertIsNone(self.results["status"]["new_upper_bound"])
        self.assertEqual(self.results["status"]["Conway_99"], "UNKNOWN")

    def test_canonical_replay(self) -> None:
        expected = (HERE / "exact-results.json").read_text(encoding="utf-8")
        self.assertEqual(CHECK.canonical_json(self.results), expected)
        json.loads(expected)


if __name__ == "__main__":
    unittest.main()
