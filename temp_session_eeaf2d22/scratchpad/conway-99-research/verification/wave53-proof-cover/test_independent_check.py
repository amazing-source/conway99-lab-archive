from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_checker():
    specification = importlib.util.spec_from_file_location(
        "wave53_proof_cover_independent_check",
        ROOT / "independent_check.py",
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


checker = load_checker()


class IndependentProofCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = checker.build_results(run_tools=False)

    def test_exact_stabilizers_orbits_and_weights(self) -> None:
        audit = self.results["automorphism_and_prior_certificate_audit"]
        coverage = self.results["coverage"]
        self.assertEqual(audit["full_scaffold_automorphism_order"], 645_120)
        self.assertEqual(audit["n3_unit_stabilizer_order"], 768)
        self.assertEqual(audit["oriented_stabilizer_order"], 384)
        self.assertEqual(audit["refined_state_count"], 10_395)
        self.assertEqual(audit["refined_orbit_count"], 78)
        self.assertFalse(audit["completed_graph_automorphism_assumed"])
        self.assertEqual(
            coverage["endpoint_compatible_state_orbit_weight"], 6_644
        )
        self.assertEqual(
            coverage["endpoint_incompatible_state_orbit_weight"], 3_751
        )
        self.assertEqual(
            coverage["endpoint_compatible_state_orbit_weight"]
            + coverage["endpoint_incompatible_state_orbit_weight"],
            10_395,
        )

    def test_every_recorded_unit_literal_and_weight_matches(self) -> None:
        coverage = self.results["coverage"]
        self.assertEqual(coverage["endpoint_unit_count"], 84)
        self.assertEqual(coverage["parent_definition_count"], 12)
        self.assertEqual(coverage["units_per_parent"], [66])
        self.assertEqual(coverage["all_parent_unit_count"], 792)
        self.assertTrue(
            coverage["every_recorded_endpoint_parent_and_refinement_unit_checked"]
        )
        self.assertTrue(coverage["every_recorded_orbit_weight_checked"])
        self.assertEqual(len(coverage["case_ids"]), 33)

    def test_missing_case_is_rejected_independently(self) -> None:
        certificate = checker.load_json(checker.COVERAGE_CERTIFICATE)
        altered = copy.deepcopy(certificate)
        altered["case_definitions"].pop()
        with self.assertRaises(AssertionError):
            checker.verify_discovery_coverage(altered)

    def test_status_inflation_is_rejected_independently(self) -> None:
        certificate = checker.load_json(checker.COVERAGE_CERTIFICATE)
        altered = copy.deepcopy(certificate)
        altered["proof_status"]["complete_cases_checked_unsat"] = 1
        altered["proof_status"]["complete_case_proof_coverage"] = "1/33"
        with self.assertRaises(AssertionError):
            checker.verify_discovery_coverage(altered)

    def test_append_unit_transform_and_raw_gzip_mapping(self) -> None:
        formula = self.results["formula_and_retained_proof_audit"]
        self.assertTrue(formula["raw_equals_gzip_decompression"])
        self.assertEqual(formula["source_declared_constraints"], 574_615)
        self.assertEqual(formula["shard_declared_constraints"], 574_616)
        self.assertEqual(
            formula["exact_transformation"],
            "header +1 and append +1 ~x187 >= 1 ;",
        )
        self.assertEqual(
            formula["retained_no_conclusion_case_coverage_contribution"], 0
        )

    def test_terminal_status_cannot_hide_in_no_conclusion(self) -> None:
        with self.assertRaises(ValueError):
            checker.parse_no_conclusion(
                "s VERIFIED NO CONCLUSION\ns VERIFIED UNSATISFIABLE\n",
                "hostile",
            )

    def test_manifest_corrections_are_resolved_and_recorded(self) -> None:
        audit = self.results["hash_and_manifest_audit"]
        self.assertTrue(audit["all_listed_discovery_manifest_hashes_match"])
        self.assertTrue(audit["raw_opb_present"])
        self.assertFalse(audit["raw_opb_listed_in_discovery_manifest"])
        self.assertTrue(audit["raw_opb_git_ignored"])
        self.assertTrue(audit["readme_calls_raw_opb_ignored"])
        self.assertTrue(audit["run_report_lists_branch15_source_metadata"])
        self.assertTrue(audit["run_report_bounded_run_output_hash_current"])
        self.assertTrue(audit["correction_ledger_complete"])
        self.assertEqual(
            audit["correction_ledger_ids"],
            ["W53-PC-C001", "W53-PC-C002", "W53-PC-C003", "W53-PC-C004"],
        )
        self.assertTrue(audit["resolution_files_listed_in_manifest"])
        self.assertTrue(
            audit["agent_report_strict_three_second_wall_wording_absent"]
        )
        self.assertEqual(len(audit["resolved_corrections"]), 4)
        self.assertEqual(audit["corrections_required"], [])

    def test_no_conclusion_closes_no_complete_case(self) -> None:
        boundary = self.results["proof_boundary"]
        self.assertEqual(boundary["conditional_case_coverage"], "33/33")
        self.assertEqual(boundary["complete_case_unsat_coverage"], "0/33")
        self.assertEqual(
            boundary["verified_no_conclusion_unsat_coverage_contribution"], 0
        )
        self.assertEqual(boundary["endpoint_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
