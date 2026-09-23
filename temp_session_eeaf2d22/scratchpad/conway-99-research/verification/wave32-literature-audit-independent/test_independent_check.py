from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import independent_check as check


class Wave32LiteratureIndependentTests(unittest.TestCase):
    def test_frozen_candidate_bytes(self) -> None:
        self.assertEqual(check.verify_frozen_bytes(), check.FROZEN)

    def test_supporting_input_bytes(self) -> None:
        self.assertEqual(check.verify_supporting_bytes(), check.SUPPORTING)

    def test_candidate_manifest(self) -> None:
        self.assertEqual(len(check.verify_candidate_manifest()), 6)

    def test_exact_endpoint_exhaustion(self) -> None:
        result = check.endpoint_arithmetic()
        self.assertEqual(result["derived_endpoints"], check.ENDPOINTS)
        self.assertEqual(result["h_cap"], 1305)

    def test_all_modularity_vetoes(self) -> None:
        rows = check.endpoint_arithmetic()["rows"]
        self.assertTrue(all(row["modularity_veto"] for row in rows))
        self.assertTrue(all(row["strong_21_modularity_veto"] for row in rows))

    def test_root_complement_determinants(self) -> None:
        rows = check.endpoint_arithmetic()["rows"]
        self.assertEqual(
            [row["root_complement_determinant"] for row in rows],
            [18, 42, 98, 162, 378, 882, 1458, 2058],
        )

    def test_triangle_incidence_spectrum(self) -> None:
        result = check.incidence_spectrum()
        self.assertEqual(result["triangle_count"], 231)
        self.assertEqual(
            result["gamma_spectrum"],
            [
                {"eigenvalue": 18, "multiplicity": 1},
                {"eigenvalue": 7, "multiplicity": 54},
                {"eigenvalue": 0, "multiplicity": 44},
                {"eigenvalue": -3, "multiplicity": 132},
            ],
        )

    def test_query_accounting(self) -> None:
        result = check.query_accounting()
        self.assertEqual(result["batch_count"], 17)
        self.assertEqual(result["query_count"], 68)
        self.assertEqual(result["unique_query_count"], 68)

    def test_failed_access_not_evidence(self) -> None:
        result = check.query_accounting()
        self.assertEqual(result["failed_or_incomplete_access_count"], 3)
        self.assertFalse(result["failed_access_used_as_evidence"])

    def test_source_accounting(self) -> None:
        result = check.source_accounting()
        self.assertEqual(result["record_count"], 15)
        self.assertEqual(result["source_ids"], [f"S{i:02d}" for i in range(1, 16)])
        self.assertEqual(result["originally_frozen_record_count"], 14)
        self.assertEqual(result["post_verifier_source_additions"], 1)
        self.assertEqual(set(result["raw_retention_counts"].values()), {0})

    def test_petro_phillips_metadata(self) -> None:
        result = check.source_accounting()["petro_phillips"]
        self.assertEqual(result["arxiv"], "2502.17845")
        self.assertEqual(result["doi"], "10.1016/j.disc.2025.114862")

    def test_phillips_thesis_chronology(self) -> None:
        result = check.source_accounting()["phillips_thesis"]
        self.assertEqual(result["arxiv"], "2605.22867")
        self.assertEqual(result["submitted_utc"], "2026-05-19T20:49:26Z")

    def test_source_quality_findings(self) -> None:
        result = check.source_quality_findings()
        self.assertFalse(result["fatal_source_or_applicability_defect"])
        self.assertTrue(result["v1_objections_preserved"])
        self.assertEqual(len(result["resolved_findings"]), 3)
        self.assertEqual(
            result["resolved_findings"][0]["corrected"],
            ["Rudolf Scharlau", "Britta Blaschke"],
        )
        self.assertEqual(
            {row["v2_status"] for row in result["resolved_findings"]},
            {"RESOLVED"},
        )

    def test_v1_correction_chronology_preserved(self) -> None:
        result = check.source_quality_findings()
        self.assertEqual(len(result["v1_frozen_hashes"]), 5)
        self.assertFalse(result["global_status_change"])
        self.assertEqual(
            check.source_accounting()["keramatipour"]["chronology"],
            "PRE_WAVE32_REPOSITORY_PRIOR_ART_ADDED_AFTER_INDEPENDENT_AUDIT",
        )

    def test_statement_scope_and_status_wall(self) -> None:
        result = check.statement_scope()
        self.assertEqual(
            result["actual_surviving_branches"],
            ["rooted", "rootless_integrally_indecomposable"],
        )
        self.assertTrue(result["all_eight_h_retained"])
        self.assertEqual(result["novelty"], "UNKNOWN")

    def test_weaker_package_boundary(self) -> None:
        result = check.statement_scope()
        self.assertEqual(
            result["weaker_matrix_package_decomposable_branch"],
            "not excluded by Wave 31 alone",
        )

    def test_deterministic_json(self) -> None:
        expected = check.canonical_bytes(check.build_results())
        parsed = json.loads(expected)
        self.assertEqual(parsed["schema_version"], 2)
        self.assertEqual(parsed["candidate_version"], "v2_corrected")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_bytes(expected)
            observed = path.read_bytes()
        self.assertEqual(observed, expected)
        self.assertEqual(
            hashlib.sha256(observed).hexdigest(),
            hashlib.sha256(expected).hexdigest(),
        )
        self.assertNotIn(b"\r\n", observed)


if __name__ == "__main__":
    unittest.main()
