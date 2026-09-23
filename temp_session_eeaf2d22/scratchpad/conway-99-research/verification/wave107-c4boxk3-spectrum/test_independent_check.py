"""Tests for the independent Wave 107 spectrum verifier."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import independent_check as check


PACKAGE = Path(__file__).resolve().parent


class IndependentSpectrumVerifierTests(unittest.TestCase):
    def test_discovery_manifest_is_frozen_and_valid(self) -> None:
        result = check.validate_discovery_manifest()
        self.assertEqual(
            result["manifest_sha256"],
            check.EXPECTED_MANIFEST_SHA256,
        )
        self.assertTrue(result["entries_valid"])
        self.assertEqual(result["entry_count"], 9)

    def test_motif_spectrum_from_newton_identities_and_ranks(self) -> None:
        result = check.verify_motif()
        self.assertEqual(
            result["spectrum"],
            {"-3": 2, "-1": 4, "0": 1, "1": 2, "2": 2, "4": 1},
        )
        self.assertEqual(result["eigenspace_nullities"], result["spectrum"])

    def test_incidence_census_is_independently_forced(self) -> None:
        result = check.motif_incidence_census()
        self.assertEqual(result["boundary_incidences"], 120)
        self.assertEqual(result["outside_pair_incidences"], 36)
        self.assertEqual(result["maximum_outside_motif_degree"], 2)
        self.assertEqual(result["motif_degree_counts"], {"0": 3, "1": 48, "2": 36})

    def test_resolvent_coefficient_cancellation(self) -> None:
        # I coefficient: x(x+1)-12=(x-3)(x+4).
        self.assertEqual([-12, 1, 1], check.poly_multiply([-3, 1], [4, 1]))
        # A coefficient: x-(x+1)+1; J numerator: 2x-28-2(x-14).
        self.assertEqual(0, 7 - (7 + 1) + 1)
        self.assertEqual(0, 2 * 7 - 28 - 2 * (7 - 14))

    def test_corrected_characteristic_polynomial(self) -> None:
        result = check.exact_results()["outside_characteristic_polynomial"]
        self.assertEqual(result["degree"], 87)
        self.assertIn("x^2-9x-46", result["factorization"])
        self.assertEqual(result["quadratic_discriminant"], 265)

    def test_wrong_quadratic_is_refuted_by_trace_two(self) -> None:
        result = check.exact_results()["wrong_quadratic_audit"]
        self.assertEqual(result["variant_trace_D2"], 1082)
        self.assertEqual(result["forced_trace_D2"], 1098)
        self.assertEqual(result["difference"], 16)
        self.assertEqual(result["verdict"], "REFUTED")

    def test_graph_invariants(self) -> None:
        result = check.exact_results()["forced_graph_invariants"]
        self.assertEqual(result["traces"], {"1": 0, "2": 1098, "3": 1002, "4": 37518})
        self.assertEqual(result["edges"], 549)
        self.assertEqual(result["triangles"], 167)
        self.assertEqual(result["four_cycles"], 1356)
        self.assertEqual(result["nullity_Q_D"], 4)
        self.assertEqual(result["rank_Q_D_minus_3I"], 45)
        self.assertEqual(result["rank_Q_D_plus_4I"], 55)

    def test_perron_connectedness_and_interlacing(self) -> None:
        result = check.exact_results()["perron_and_interlacing"]
        self.assertTrue(result["rho_is_simple"])
        self.assertTrue(result["outside_graph_connected"])
        self.assertTrue(result["cauchy_interlacing_passes"])

    def test_status_wall_is_fail_closed(self) -> None:
        wall = check.exact_results()["status_wall"]
        self.assertFalse(wall["spectral_obstruction_found"])
        self.assertFalse(wall["motif_excluded"])
        self.assertEqual(wall["motif_extension"], "UNKNOWN")
        self.assertEqual(wall["Conway_99"], "UNKNOWN")
        self.assertEqual(wall["literature_novelty"], "UNKNOWN")

    def test_archived_results_replay(self) -> None:
        archived = json.loads((PACKAGE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(archived, check.exact_results())


if __name__ == "__main__":
    unittest.main()
