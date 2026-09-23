"""Tests for the independent Wave 110 verifier."""

from __future__ import annotations

import unittest

import independent_verify as subject


class IndependentWave110Tests(unittest.TestCase):
    def test_frozen_manifest(self) -> None:
        result = subject.verify_discovery_manifest()
        self.assertTrue(result["all_entries_match"])
        self.assertEqual(result["entry_count"], 14)

    def test_domain_reconstruction(self) -> None:
        result = subject.independent_domain_counts()
        self.assertEqual(result["pattern_class_histogram"], {
            "1": 12,
            "2": 12,
            "3": 1,
            "4": 12,
        })
        self.assertEqual(result["edge_variables"], 3741)
        self.assertEqual(result["common_conjunction_variables"], 317985)
        self.assertEqual(result["lex_comparisons"], 50)
        self.assertEqual(result["lex_auxiliary_variables"], 4126)
        self.assertEqual(result["total_variables"], 325852)
        self.assertEqual(result["lex_cnf_clauses"], 24756)
        self.assertEqual(result["total_cnf_clauses"], 978711)
        self.assertEqual(result["distinct_linear_incidence_rows"], 1044)
        self.assertEqual(result["exact_cardinality_rows"], 4873)
        self.assertEqual(result["native_atmost_constraints"], 9746)

    def test_actual_lex_cnf_truth_table(self) -> None:
        result = subject.lex_cnf_truth_table()
        self.assertTrue(result["equivalent_to_boolean_lex_leq"])
        self.assertEqual(result["base_vector_pairs_checked"], 341)

    def test_shared_potential(self) -> None:
        result = subject.shared_potential_audit()
        self.assertTrue(result["all_minimizers_simultaneously_row_lex"])
        self.assertTrue(result["within_class_columns_omitted"])
        self.assertFalse(result["target_automorphism_assumed"])
        self.assertEqual(result["small_colored_graphs_exhaustively_checked"], 2048)

    def test_x0_partition(self) -> None:
        result = subject.x0_branch_audit()
        self.assertTrue(result["partition_is_complete"])
        self.assertEqual(
            result["edge_count_census"],
            {"0": 1, "1": 3, "2": 3, "3": 1},
        )
        self.assertFalse(result["canonical_labeling_fixed"])

    def test_archived_runs_fail_closed(self) -> None:
        result = subject.archived_run_audit()
        self.assertTrue(result["all_hashes_match_manifest_and_census"])
        self.assertEqual(result["all_statuses"], "UNKNOWN_TIMEOUT")
        self.assertGreater(result["minimum_archived_free_fraction"], 0.5)

    def test_fresh_reruns_fail_closed(self) -> None:
        result = subject.rerun_audit()
        self.assertEqual(result["all_statuses"], "UNKNOWN_TIMEOUT")
        self.assertTrue(result["all_submission_counts_match"])
        self.assertGreater(result["minimum_free_fraction"], 0.5)


if __name__ == "__main__":
    unittest.main()
