#!/usr/bin/env python3
"""Small integration tests for the bounded branch scout."""

from __future__ import annotations

import unittest

from scout_branches import difference, run_scout


class BranchScoutTests(unittest.TestCase):
    def test_counter_differences(self) -> None:
        self.assertEqual(
            difference({"conflicts": 7, "decisions": 11}, {"conflicts": 2}),
            {"conflicts": 5, "decisions": 11},
        )

    def test_pair_count_two_runs_its_single_complete_branch(self) -> None:
        report = run_scout(
            pair_count=2,
            coordinate=0,
            conflict_budget=100,
            solver_name="cadical300",
            candidate_directory=None,
        )
        self.assertEqual(report["evidence_status"], "NON_EVIDENTIARY_SCOUT")
        self.assertEqual(report["branches_planned"], 1)
        self.assertEqual(report["branches_run"], 1)
        self.assertEqual(report["branches"][0]["partition"], [1])
        self.assertEqual(report["branches"][0]["result"], "SAT_MODEL")

    def test_native_pair_count_two_runs_with_a_fresh_minicard_solver(self) -> None:
        report = run_scout(
            pair_count=2,
            coordinate=0,
            conflict_budget=100,
            solver_name="minicard",
            candidate_directory=None,
            cardinality_backend="native",
            reuse_solver=False,
        )
        self.assertEqual(report["configuration"]["cardinality_backend"], "native")
        self.assertFalse(report["configuration"]["incremental_learned_clauses"])
        self.assertEqual(report["branches"][0]["result"], "SAT_MODEL")


if __name__ == "__main__":
    unittest.main()
