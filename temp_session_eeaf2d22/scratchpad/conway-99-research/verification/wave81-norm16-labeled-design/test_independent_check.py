"""Focused hostile tests for the clean-room Wave 81 verifier."""

from __future__ import annotations

import importlib.util
import unittest
from collections import Counter
from pathlib import Path


MODULE = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave81_independent", MODULE)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave81Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_results()

    def test_frozen_discovery_manifest(self) -> None:
        self.assertEqual(
            self.result["discovery_manifest_sha256"],
            CHECK.EXPECTED_MANIFEST_SHA256,
        )

    def test_support_census_is_complete_modulo_labels_only(self) -> None:
        support = self.result["support"]
        self.assertEqual(support["anchored_supports"], 1800)
        self.assertEqual(support["S8xS8_orbits"], 5)
        self.assertFalse(support["automorphism_assumed"])
        rows = tuple(int(value, 16) for value in support["representatives_hex"][4])
        relabelled = tuple(
            sorted(
                CHECK.permute_mask(row, (6, 1, 4, 0, 7, 2, 5, 3))
                for row in reversed(rows)
            )
        )
        self.assertIn(relabelled, CHECK.support_orbit(rows))

    def test_supports_and_deficiencies_have_exact_local_parameters(self) -> None:
        for encoded in self.result["support"]["representatives_hex"]:
            rows = tuple(int(value, 16) for value in encoded)
            cols = CHECK.columns(rows)
            self.assertEqual([row.bit_count() for row in rows], [4] * 8)
            self.assertEqual([col.bit_count() for col in cols], [4] * 8)
            for blocks in (rows, cols):
                self.assertTrue(CHECK.same_side_codegrees_ok(blocks))
                pairs = CHECK.deficiencies(blocks)
                self.assertEqual(len(pairs), 8)
                self.assertEqual(
                    Counter(v for pair in pairs for v in pair),
                    Counter({v: 2 for v in range(8)}),
                )

    def test_wave78_histogram_is_reconstructed(self) -> None:
        self.assertEqual(
            {key: self.result["wave78_histogram"][key] for key in ("X0", "X1", "X2")},
            {"X0": 11, "X1": 64, "X2": 8},
        )

    def test_deficiency_couplings_and_local_flows(self) -> None:
        couplings = self.result["couplings"]
        self.assertEqual(couplings["per_orbit"], [90, 326, 681, 2068, 1820])
        self.assertEqual(couplings["total"], 4985)
        self.assertEqual(
            couplings["per_orbit_passing_local_flow"],
            [90, 326, 681, 2068, 1820],
        )
        self.assertEqual(couplings["total_passing_local_flow"], 4985)
        self.assertTrue(couplings["marginal_flow_null_control_rejected"])

    def test_six_moment_histogram_enumeration(self) -> None:
        histograms = self.result["outside_histograms"]
        self.assertEqual(histograms["counts_by_t"]["0"], 43)
        self.assertEqual(histograms["counts_by_t"]["1"], 7)
        self.assertTrue(
            all(histograms["counts_by_t"][str(t)] == 0 for t in range(2, 13))
        )
        self.assertEqual(len(histograms["six_pair_moments"]), 6)

    def test_new_graphical_strengthening_is_not_status_inflated(self) -> None:
        extension = self.result["outside_histograms"][
            "verifier_derived_strengthening"
        ]
        self.assertEqual(extension["claim_label"], "DERIVED")
        self.assertEqual(extension["counts_after_all_type_graphical_tests"]["0"], 40)
        self.assertEqual(extension["counts_after_all_type_graphical_tests"]["1"], 7)
        self.assertEqual(len(extension["rejections"]), 3)
        self.assertTrue(
            all(row["failed_checks"] == ["X0_induced"] for row in extension["rejections"])
        )
        for row in extension["rejections"]:
            self.assertFalse(CHECK.simple_graphical(row["X0_induced_degrees"]))

    def test_jacobi_residuals_and_trace_controls(self) -> None:
        spectrum = self.result["spectrum"]
        self.assertEqual(spectrum["full_SRG_multiplicities"], {"3": 54, "-4": 44})
        self.assertEqual(spectrum["principal_factor_exponents"], {"3": 38, "-4": 28})
        self.assertEqual(
            spectrum["traces_1_to_4_per_orbit"],
            [
                [0, 1002, 906, 32422],
                [0, 1002, 906, 32406],
                [0, 1002, 906, 32398],
                [0, 1002, 906, 32390],
                [0, 1002, 906, 32390],
            ],
        )
        self.assertEqual(spectrum["four_cycles_per_orbit"], [1135, 1133, 1132, 1131, 1131])
        self.assertEqual(spectrum["orbits_eliminated"], 0)
        self.assertTrue(
            all(
                len(coefficients) == 16 and coefficients[0] == 1
                for coefficients in spectrum["q_coefficients_descending_per_orbit"]
            )
        )

    def test_transient_exponent_swap_is_rejected(self) -> None:
        control = self.result["spectrum"]["exponent_control"]
        self.assertEqual(control["correct_trace"], 0)
        self.assertEqual(control["swapped_trace"], -70)

    def test_status_boundary(self) -> None:
        endpoint = self.result["endpoint"]
        self.assertFalse(endpoint["norm16_excluded"])
        self.assertEqual(endpoint["conway_status"], "UNKNOWN")
        self.assertEqual(endpoint["novelty"], "UNKNOWN")

if __name__ == "__main__":
    unittest.main()
