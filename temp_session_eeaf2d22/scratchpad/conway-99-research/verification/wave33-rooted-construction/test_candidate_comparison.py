#!/usr/bin/env python3
"""Post-release tests for the frozen candidate comparison."""

from __future__ import annotations

import copy
import unittest

import candidate_comparison as comparison
import independent_check as pre


class CandidateComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = pre.load_json(
            comparison.ATTEMPT / "partial-design-certificate.json"
        )
        cls.parsed = comparison.parse_certificate(cls.certificate)
        cls.bounded = pre.load_json(
            comparison.ATTEMPT / "bounded-search-manifest.json"
        )

    def test_01_precomparison_and_candidate_manifests(self) -> None:
        checked = comparison.verify_manifests()
        self.assertEqual(checked["status"], "PASS")
        self.assertEqual(checked["precomparison_entry_count"], 5)
        self.assertEqual(checked["candidate_entry_count"], 17)
        self.assertEqual(checked["artifact_entry_count"], 16)

    def test_02_candidate_passes_frozen_checker(self) -> None:
        normalized = comparison.normalized_payload(self.parsed, self.bounded)
        result = pre.verify_payload(
            normalized,
            input_sha256=pre.sha256_path(
                comparison.ATTEMPT / "partial-design-certificate.json"
            ),
        )
        self.assertEqual(
            result["hostile_partial"]["BF"]["violation_count"], 10
        )
        self.assertEqual(
            result["hostile_partial"]["BF"]["squared_defect"], 10
        )
        self.assertEqual(
            result["hostile_partial"]["O_O_layer_certificate_status"],
            "UNSUPPLIED",
        )

    def test_03_exact_design_and_bf_metrics(self) -> None:
        self.assertEqual(
            pre.design_metrics(self.parsed["fixed_design"])[
                "pair_intersection_histogram"
            ],
            {"2": 105},
        )
        bf = comparison.direct_bf_metrics(self.parsed)
        self.assertEqual(bf["count_histogram"], {"1": 5, "2": 200, "3": 5})
        self.assertEqual(bf["defect_histogram"], {"-1": 5, "1": 5})
        self.assertEqual(bf["exact_support_group_count"], 9)

    def test_04_independent_assignment_encoding(self) -> None:
        encoding = comparison.independent_assignment_encoding(self.parsed)
        self.assertEqual(encoding["binary_variable_count"], 4900)
        self.assertEqual(encoding["total_equalities"], 350)
        self.assertEqual(encoding["row_width_histogram"], {"70": 140, "140": 210})
        checked = comparison.verify_bounded_manifest(self.bounded, encoding)
        self.assertFalse(checked["primal_point_returned"])
        self.assertFalse(checked["active_graph_phase_entered"])
        self.assertEqual(checked["interpretation"], "UNKNOWN_NO_EVIDENCE")

    def test_05_scope_metadata_tamper_rejected(self) -> None:
        hostile = copy.deepcopy(self.certificate)
        hostile["scope"] = "COMPLETE_GRAPH"
        with self.assertRaisesRegex(pre.VerificationError, "scope drift"):
            comparison.parse_certificate(hostile)

    def test_06_limitation_tamper_rejected(self) -> None:
        hostile = copy.deepcopy(self.certificate)
        hostile["limitations"] = []
        with self.assertRaisesRegex(pre.VerificationError, "limitation text drift"):
            comparison.parse_certificate(hostile)

    def test_07_o_o_layer_is_absent_not_empty_restriction(self) -> None:
        self.assertNotIn("active_edges", self.certificate)
        self.assertIn("no active-active edges", self.certificate["restrictions"][1])

    def test_08_source_and_solver_provenance(self) -> None:
        self.assertTrue(
            comparison.static_source_audit()["exact_checker_standard_library_only"]
        )
        self.assertEqual(
            comparison.verify_solver_environment_hashes()["status"], "PASS"
        )

    def test_09_recorded_results_and_status_wall(self) -> None:
        exact = pre.load_json(comparison.ATTEMPT / "exact-results.json")
        base = pre.load_json(comparison.ATTEMPT / "base-results.json")
        checked = comparison.verify_recorded_results(
            exact, base, comparison.direct_bf_metrics(self.parsed)
        )
        self.assertEqual(checked["status"], "PASS")
        self.assertEqual(exact["status_wall"]["Conway_99"], "UNKNOWN")

    def test_10_comparison_results_bind_core_recomputation(self) -> None:
        recorded = pre.load_json(
            comparison.HERE / "candidate-comparison-results.json"
        )
        bf = comparison.direct_bf_metrics(self.parsed)
        encoding = comparison.independent_assignment_encoding(self.parsed)
        self.assertEqual(recorded["claim_label"], "VERIFIED")
        self.assertEqual(
            recorded["hostile_partial"]["BF_violation_count"],
            bf["violation_count"],
        )
        self.assertEqual(
            recorded["hostile_partial"]["BF_squared_defect"],
            bf["squared_defect"],
        )
        self.assertEqual(
            recorded["assignment_encoding"]["row_system_sha256"],
            encoding["row_system_sha256"],
        )
        self.assertEqual(
            recorded["status_wall"]["complete_graph_extension"], "UNKNOWN"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
