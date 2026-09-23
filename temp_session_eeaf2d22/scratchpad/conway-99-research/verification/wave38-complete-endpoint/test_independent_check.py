#!/usr/bin/env python3
"""Hostile tests for the independent Wave 38 complete-endpoint verifier."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import independent_check as check


class IndependentCompleteEndpointTests(unittest.TestCase):
    def test_closed_form_and_enumerated_triangle_counts_agree(self) -> None:
        result = check.independent_triangle_inventory()
        self.assertEqual(result["candidate_triangles"], 96_215)
        self.assertEqual(
            result["candidate_triangle_type_histogram"],
            {
                "coordinate_residual_residual": 924,
                "residual_only": 95_284,
                "root_triangle": 7,
            },
        )
        self.assertEqual(
            result["candidate_triangle_variable_edge_histogram"],
            {"0": 7, "1": 924, "3": 95_284},
        )
        self.assertEqual(result["exact_residual_only_prism_embeddings"], 24_388_892_640)

    def test_residual_partition_factor_is_exact(self) -> None:
        self.assertEqual(len(check.six_vertex_prism_patterns()), 60)

    def test_lambda_compression_has_no_proper_supergraph(self) -> None:
        result = check.verify_lambda_compression()
        self.assertEqual(result["supergraphs_checked"], 64)
        self.assertEqual(result["lambda_at_most_one_survivors"], 1)

    def test_endpoint_cover_is_independent_and_exact(self) -> None:
        self.assertEqual(check.independent_endpoint_cases(), check.EXPECTED_BY_PARENT)

    def test_fixture_is_bound_by_the_independent_checker(self) -> None:
        result = check.verify_fixture()
        self.assertEqual(result["prism_witness_count"], 1)
        self.assertEqual(result["cut_literal_count"], 9)

    def test_oracle_exhausts_every_six_vertex_graph(self) -> None:
        result = check.differential_oracle_check()
        self.assertEqual(result["all_six_vertex_graphs_checked"], 32_768)
        self.assertEqual(result["distinct_labelled_prism_graphs"], 60)
        self.assertEqual(result["hostile_prism_counts"]["two_disjoint_prisms"], 2)
        self.assertEqual(result["hostile_prism_counts"]["extra_cross_edge"], 0)

    def test_prior_validator_attacks_are_rejected_on_bound_paths(self) -> None:
        result = check.hostile_validator_check()
        self.assertTrue(all(result["semantic_tamper_rejections"].values()))
        self.assertTrue(all(result["hardening_regressions"].values()))
        self.assertTrue(all(result["intentional_unbound_api_boundary"].values()))

    def test_verify_only_clis_require_candidate_and_source_evidence(self) -> None:
        result = check.verify_only_cli_check()
        self.assertTrue(all(result.values()))

    def test_exporter_guard_separates_static_and_partial_routes(self) -> None:
        result = check.exporter_guard_check()
        self.assertTrue(result["wrong_acknowledgement_refused_before_write"])
        self.assertFalse(result["static_route_accepts_cut_pool"])
        self.assertEqual(result["partial_pool_formula_claim_label"], "CANDIDATE_FORMULA_ONLY")
        self.assertTrue(result["branch_outside_path_refused_before_write"])
        self.assertTrue(result["static_outside_path_refused_before_write"])
        self.assertTrue(result["identical_output_paths_refused_before_write"])

    def test_json_loader_rejects_duplicate_keys_and_nonfinite_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            path = Path(raw_tmp) / "hostile.json"
            path.write_text('{"x":1,"x":2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                check.load_json(path)
            path.write_text('{"x":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-standard JSON constant"):
                check.load_json(path)

    def test_yaml_loader_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            path = Path(raw_tmp) / "hostile.yaml"
            path.write_text("x: 1\nx: 2\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate YAML key"):
                check.load_yaml(path)

    def test_manifest_paths_reject_traversal_absolute_and_windows_forms(self) -> None:
        for raw in ("../escape", "/absolute", "C:/escape", r"logs\escape"):
            with self.subTest(raw=raw), self.assertRaises(AssertionError):
                check.safe_manifest_path(raw)

    def test_fixture_digest_tamper_is_caught_independently(self) -> None:
        source = check.load_json(check.attempt_root() / "fixture-residual-prism-cuts.json")
        altered = copy.deepcopy(source)
        altered["candidate"]["edge_catalog_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as raw_tmp:
            path = Path(raw_tmp) / "altered.json"
            path.write_text(json.dumps(altered), encoding="utf-8")
            self.assertNotEqual(
                check.load_json(path)["candidate"]["edge_catalog_sha256"],
                check.verify_fixture()["edge_catalog_sha256"],
            )

    def test_package_hash_schema_and_privacy_checks(self) -> None:
        result = check.package_integrity_check()
        self.assertTrue(result["package_manifest_exact_coverage"])
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["package_manifest_hash_mismatches"], [])
        self.assertEqual(result["run_report_output_hash_mismatches"], [])
        self.assertEqual(result["privacy_hits"], 0)

    def test_full_audit_preserves_unknown_target_status(self) -> None:
        result = check.audit()
        self.assertEqual(result["target_status"], "UNKNOWN")
        self.assertFalse(any(result["evidence_boundary"].values()))
        self.assertEqual(
            [finding["status"] for finding in result["findings"]],
            ["FIXED"] * 5,
        )
        self.assertEqual(result["findings"][4]["id"], "W38-CE-V5")


if __name__ == "__main__":
    unittest.main()
