from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave116_exact", HERE / "exact_check.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave116ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.build_results()
        cls.archived = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))

    def test_archived_result(self) -> None:
        self.assertEqual(self.result, self.archived)

    def test_projector_spectrum_and_determinant(self) -> None:
        row = self.result["restricted_projector"]
        self.assertEqual(row["eigenvalues"], ["13/63", "5/7", "3/7", "3/7"])
        self.assertEqual(row["determinant"], "65/2401")
        self.assertTrue(row["positive_definite"])

    def test_integral_marking_matrices(self) -> None:
        evaluation = self.result["evaluation_lattices"]
        self.assertEqual(
            evaluation["ordinary_K_Jacobi_marking"]["eigenvalues"],
            [91, 315, 189, 189],
        )
        self.assertEqual(
            evaluation["Fricke_L_marking"]["eigenvalues"],
            [13, 45, 27, 27],
        )
        self.assertEqual(
            evaluation["dual_evaluation_vector"]["residue_determinant_mod_7"],
            4,
        )

    def test_naive_index_is_rejected(self) -> None:
        warning = self.result["evaluation_lattices"]["coordinate_vector"]["warning"]
        self.assertIn("not a justified ordinary Jacobi index", warning)

    def test_sum_needs_no_automorphism(self) -> None:
        cycle_sum = self.result["cycle_sum"]
        self.assertEqual(cycle_sum["constant_coefficient"], 2079)
        self.assertFalse(cycle_sum["automorphism_assumption"])

    def test_incidence_factor_of_two(self) -> None:
        row = self.result["incidence_coefficient"]
        self.assertEqual(row["rank28_coefficient_sum_lower"], 52812)
        self.assertEqual(row["rank28_oriented_incidence_lower"], 105624)
        self.assertEqual(
            2 * row["rank28_coefficient_sum_lower"],
            row["rank28_oriented_incidence_lower"],
        )
        self.assertEqual(row["sufficient_coefficient_sum_upper_for_contradiction"], 51975)
        self.assertEqual(row["gap"], 837)

    def test_fricKe_is_a_pair_not_a_self_map(self) -> None:
        row = self.result["Fricke_Poisson"]
        self.assertIn("G_K/2 to the L index G_L/2", row["warning"])
        self.assertIn("-7^(q/2-11)", row["normalized_formula"])

    def test_status_wall(self) -> None:
        row = self.result["current_boundary"]
        self.assertIsNone(row["new_Jacobi_upper_bound"])
        self.assertFalse(row["rank28_excluded"])
        self.assertEqual(row["Conway_99"], "UNKNOWN")
        self.assertEqual(row["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
