#!/usr/bin/env python3
"""Tests for the independent Wave 37 rooted-branch audit."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location(
    "wave37_rooted_independent_check",
    Path(__file__).resolve().with_name("independent_check.py"),
)
assert SPEC is not None and SPEC.loader is not None
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


class RootedBranchIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_results()

    def test_lambda_one_prism_lemma(self) -> None:
        lemma = self.result["lambda_one_prism_lemma"]
        self.assertTrue(lemma["required_six_edge_pattern_forces_induced_prism"])
        self.assertEqual(lemma["lambda_one_violations_detected"], 6)

    def test_complete_conditional_branch_scope(self) -> None:
        cover = self.result["branch_cover"]
        self.assertEqual(cover["parent_orbit_count"], 12)
        self.assertEqual(cover["parent_state_count"], 945)
        self.assertEqual(cover["refined_orbit_count"], 78)
        self.assertEqual(cover["refined_state_count"], 10_395)
        self.assertEqual(cover["endpoint_refined_case_count"], 33)
        self.assertFalse(cover["completed_graph_automorphism_assumed"])

    def test_all_five_catalogs_reconstructed(self) -> None:
        self.assertEqual(set(self.result["catalogs"]), {"4", "5", "8", "10", "12"})
        for branch, record in self.result["catalogs"].items():
            with self.subTest(branch=branch):
                self.assertEqual(record["fixed_triangle_count"], 6)
                self.assertEqual(record["deduplicated_active_clause_count"], 282_774)
                self.assertEqual(
                    record["clause_length_histogram"],
                    {"3": 606, "5": 282_168},
                )

    def test_budget_unknown_has_no_candidate(self) -> None:
        bounded = self.result["bounded_solver_artifact"]
        self.assertEqual(bounded["status"], "BUDGET_UNKNOWN")
        self.assertEqual(bounded["conflict_budget"], 100_000)
        self.assertEqual(bounded["conflicts"], 100_000)
        self.assertFalse(bounded["candidate_present"])
        self.assertEqual(bounded["mathematical_evidentiary_value"], "NONE")

    def test_status_remains_unknown(self) -> None:
        conclusion = self.result["conclusion"]
        self.assertTrue(conclusion["conditional_clause_family_verified"])
        self.assertFalse(conclusion["all_prisms_encoded"])
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["upper_bound_improved_below_4158"])
        self.assertEqual(conclusion["target_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
