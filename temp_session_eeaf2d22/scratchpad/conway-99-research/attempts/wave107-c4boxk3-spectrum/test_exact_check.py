"""Independent exact tests for the Wave 107 spectral derivation."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import exact_check


PACKAGE = Path(__file__).resolve().parent


class SpectralDerivationTests(unittest.TestCase):
    def test_motif_is_c4_cartesian_k3(self) -> None:
        adjacency = exact_check.motif_adjacency()
        self.assertEqual(len(adjacency), 12)
        self.assertTrue(all(sum(row) == 4 for row in adjacency))
        self.assertTrue(
            all(
                adjacency[i][j] == adjacency[j][i]
                for i in range(12)
                for j in range(12)
            )
        )

    def test_motif_characteristic_polynomial_exactly(self) -> None:
        for value in range(-6, 7):
            self.assertEqual(
                exact_check.motif_determinant_value(value),
                exact_check.motif_characteristic_value(value),
            )

    def test_corrected_jacobi_residual_exactly(self) -> None:
        for value in range(-7, 7):
            self.assertEqual(
                exact_check.resolvent_residual_determinant(value),
                exact_check.residual_characteristic_value(value, 46),
            )

    def test_wrong_quadratic_fails_forced_trace(self) -> None:
        self.assertEqual(exact_check.forced_degree_sum(), 1098)
        self.assertEqual(exact_check.outside_trace(2, 38), 1082)
        self.assertEqual(exact_check.outside_trace(2, 46), 1098)

    def test_forced_closed_walk_invariants(self) -> None:
        result = exact_check.exact_results()["forced_graph_invariants"]
        self.assertEqual(result["edges"], 549)
        self.assertEqual(result["triangles"], 167)
        self.assertEqual(result["four_cycles"], 1356)
        self.assertEqual(result["nullity_Q_D"], 4)
        self.assertEqual(result["rank_Q_D_minus_3I"], 45)
        self.assertEqual(result["rank_Q_D_plus_4I"], 55)

    def test_perron_vector_is_positive(self) -> None:
        # 16^2 < 265 < 17^2, so rho=(9+sqrt(265))/2 is in (12.5,13).
        # Its smallest coordinate is rho+5-2 > 15.5.
        self.assertLess(16 * 16, 265)
        self.assertLess(265, 17 * 17)
        self.assertTrue(
            exact_check.exact_results()["two_main_eigenvalue_structure"][
                "perron_vector_strictly_positive"
            ]
        )

    def test_archived_results_replay(self) -> None:
        archived = json.loads(
            (PACKAGE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(archived, exact_check.verify_exact())


if __name__ == "__main__":
    unittest.main()
