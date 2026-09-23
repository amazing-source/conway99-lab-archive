"""Tests for the clean-room Wave 121 verifier."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave121_independent", HERE / "independent_verify.py"
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave121IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = VERIFY.build_results()

    def test_frozen_bytes(self) -> None:
        VERIFY.verify_frozen_bytes()

    def test_orthogonal_types_and_orbits(self) -> None:
        spaces = self.results["orthogonal_spaces"]
        self.assertEqual(spaces["D_L"], "O^-(14,7)")
        self.assertEqual(spaces["D_K"], "O^-(30,7)")
        for dimension in (14, 30):
            row = spaces["orbit_counts"][f"dimension{dimension}"]
            self.assertEqual(
                row["zero_including_zero_vector"]
                + 6 * row["each_exact_nonzero_value"],
                row["total"],
            )

    def test_exact_value_dictionary(self) -> None:
        row = self.results["orbit_dictionary"]
        self.assertEqual(row["D_L_nonzero_isotropic"], "x_(7m)-y_m")
        self.assertEqual(row["D_K_nonzero_isotropic"], "y_(7n)-x_n")
        self.assertEqual(len(row["new_inequalities_tested"]), 13)

    def test_extended_modular_basis(self) -> None:
        row = self.results["extended_scalar_model"]
        self.assertEqual(row["dimension"], 15)
        self.assertEqual(row["sturm_bound"], 14)
        self.assertEqual(row["theta_L_precision"], 77)
        self.assertEqual(len(row["basis_products"]), 15)

    def test_old_optimizers_remain_feasible(self) -> None:
        row = self.results["extended_scalar_model"]
        self.assertTrue(row["prefix10"]["audit"]["all_nonnegative"])
        self.assertTrue(row["prefix11"]["audit"]["all_nonnegative"])
        self.assertEqual(row["prefix10"]["old_exact_optimum"], "389888/57")
        self.assertEqual(row["prefix11"]["old_exact_optimum"], "4675706896/9307")

    def test_restricted_identities_and_controls(self) -> None:
        row = self.results["extended_scalar_model"]
        self.assertEqual(row["restricted_identities"][0]["lower_bound"], 2729216)
        self.assertEqual(row["restricted_identities"][1]["lower_bound"], 4144144)
        self.assertTrue(row["formal_even_integral_control"]["all_even_integers"])
        self.assertFalse(
            row["restricted_identities"][1]["attaining_rational_control"][
                "all_even_integers"
            ]
        )

    def test_short_code_upper(self) -> None:
        row = self.results["short_code_upper"]
        self.assertTrue(row["evaluation_injective_through_norm22"])
        self.assertGreater(row["difference_lower_if_same_word"], row["difference_upper_by_triangle"])
        self.assertEqual(row["norm20_self_dot_mod7"], 5)
        self.assertEqual(row["norm22_self_dot_mod7"], 2)
        self.assertEqual(row["each_anisotropic_value_upper"], 7**30 * (7**13 + 7**6))

    def test_scalar_marking_and_frozen_selection(self) -> None:
        row = self.results["scalar_c4_jacobi"]
        self.assertEqual(row["marking"]["d_norm"], 20)
        self.assertEqual(row["marking"]["b_norm"], 140)
        self.assertEqual(row["marking"]["b_divisibility_in_K"], 7)
        self.assertEqual(row["selection"]["valid_norms_under_frozen_inputs"], [14, 16, 18])
        self.assertEqual(row["selection"]["q10_interpretation"], "UNKNOWN_UNDER_FROZEN_INPUTS")

    def test_component_reduction_and_phase(self) -> None:
        row = self.results["scalar_c4_jacobi"]["components"]
        self.assertEqual(row["raw_index70_residues"], 140)
        self.assertEqual(row["divisibility_reduced_residues"], 20)
        self.assertEqual(row["even_independent_components"], 11)
        self.assertEqual(row["finite_fourier_square"], "20 times residue negation")
        self.assertIn("sqrt(-i*tau/20)", row["poisson_component_formula"])

    def test_truncated_null_is_not_promoted(self) -> None:
        row = self.results["scalar_c4_jacobi"]["truncated_null"]
        self.assertTrue(row["nonnegative_integral_symmetric"])
        self.assertFalse(row["is_Jacobi_form"])
        self.assertFalse(row["is_Fricke_compatible_all_orders"])
        self.assertEqual(row["coefficients_n_r"]["7,28"], 52812)

    def test_post_independent_comparison(self) -> None:
        row = json.loads((HERE / "comparison.json").read_text(encoding="utf-8"))
        self.assertEqual(row["checks_total"], row["checks_passed"])
        self.assertEqual(row["mismatches"], [])
        self.assertIn("CONSISTENCY_ONLY", row["wave124_comparison_status"])

    def test_replay_and_status_wall(self) -> None:
        expected = (HERE / "independent-results.json").read_text(encoding="utf-8")
        self.assertEqual(VERIFY.canonical_json(self.results), expected)
        self.assertFalse(self.results["status"]["rank30_excluded"])
        self.assertFalse(self.results["status"]["rank28_excluded"])
        self.assertEqual(self.results["status"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
