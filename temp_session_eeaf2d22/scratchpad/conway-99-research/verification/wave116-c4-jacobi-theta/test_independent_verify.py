from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave116_independent", HERE / "independent_verify.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave116IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.build_results()
        cls.archived = json.loads(
            (HERE / "independent-results.json").read_text(encoding="utf-8")
        )

    def test_archived_result(self) -> None:
        self.assertEqual(self.result, self.archived)

    def test_projector_exact(self) -> None:
        row = self.result["projector"]
        self.assertEqual(row["determinant"], "65/2401")
        self.assertEqual(
            row["eigenvalues_by_mode"],
            {
                "constant": "13/63",
                "alternating": "5/7",
                "zero_a": "3/7",
                "zero_b": "3/7",
            },
        )
        self.assertTrue(row["positive_definite"])

    def test_naive_index_rejected_and_scalings(self) -> None:
        rows = self.result["markings"]
        self.assertFalse(rows["naive_p"]["ordinary_index_justified"])
        self.assertEqual(rows["naive_p"]["actual_membership"], "p_i not in K*")
        self.assertEqual(rows["dual_a"]["membership"], "K*")
        self.assertEqual(rows["L_v"]["determinant"], 426465)
        self.assertEqual(rows["K_g"]["determinant"], 1023942465)
        self.assertEqual(rows["K_g"]["matrix_index"], "G_K/2")

    def test_discriminant_sector_non_degenerate(self) -> None:
        row = self.result["discriminant_sector"]
        self.assertEqual(row["rank_mod_7"], 4)
        self.assertEqual(row["determinant_mod_7"], 4)
        self.assertEqual(row["subgroup_size"], 2401)
        self.assertIn("orthogonal", row["closure_warning"])

    def test_poisson_normalization(self) -> None:
        row = self.result["poisson_fricke"]
        self.assertEqual(row["complex_phase"], "i^(-22)=-1")
        self.assertIn("-7^(q/2)", row["raw_formula"])
        self.assertEqual(row["slash_formula"], "Phi_K||W_7=-7^(q/2-11)Phi_L")
        self.assertEqual(
            row["scalar_solved_formula"],
            "Theta_L=-7^(11-q/2)(Theta_K|_22 W_7)",
        )
        q16 = row["rows"][-1]
        self.assertEqual(q16["raw_factor"], "-7^8")
        self.assertEqual(q16["jacobi_slash_factor"], "-7^-3")
        self.assertEqual(q16["solved_scalar_factor"], "-7^3")

    def test_common_index_needs_no_automorphism(self) -> None:
        row = self.result["cycle_sum"]
        self.assertTrue(row["common_gram_without_automorphisms"])
        self.assertTrue(row["dihedral_relabeling_preserves_index"])
        self.assertEqual(row["constant_coefficient"], 2079)

    def test_coefficient_count_and_threshold(self) -> None:
        row = self.result["incidence"]
        self.assertEqual(row["coefficient_sum_counts"], "antipodal C4 incidences")
        self.assertEqual(row["oriented_count_factor"], 2)
        self.assertEqual(row["oriented_lower"], 105624)
        self.assertEqual(row["antipodal_lower"], 52812)
        self.assertEqual(row["cap_25_total"], 51975)
        self.assertEqual(row["gap"], 837)

    def test_projected_norm_and_support(self) -> None:
        row = self.result["incidence"]
        self.assertEqual(row["projected_norm"], "28/5")
        self.assertEqual(
            row["support_discriminant_margins_2n_minus_projected_norm"],
            {"7": "42/5", "8": "52/5", "9": "62/5"},
        )

    def test_degree_32_interpolation_is_exact(self) -> None:
        row = self.result["harmonic_interpolation"]
        self.assertEqual(row["univariate_degree"], 8)
        self.assertEqual(row["four_coordinate_total_degree"], 32)
        self.assertTrue(row["exact_on_norm_at_most_18"])
        self.assertFalse(row["coefficientwise_positivity_retained"])

        for target, name in ((1, "indicator_plus_coefficients"), (-1, "indicator_minus_coefficients")):
            coefficients = [Fraction(value) for value in row[name]]
            for value in range(-4, 5):
                self.assertEqual(
                    MODULE.polynomial_value(coefficients, value),
                    int(value == target),
                )

    def test_hostile_wrong_projector_fails(self) -> None:
        mutated = MODULE.cycle_projector()
        mutated[0][0] -= Fraction(1, 63)
        self.assertNotEqual(MODULE.determinant(mutated), Fraction(65, 2401))

    def test_status_wall(self) -> None:
        row = self.result["status_wall"]
        self.assertFalse(row["upper_bound_proved"])
        self.assertFalse(row["rank28_excluded"])
        self.assertEqual(row["Conway_99"], "UNKNOWN")
        self.assertEqual(row["literature_novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
