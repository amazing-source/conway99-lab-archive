#!/usr/bin/env python3
"""Regression tests for the Wave 16 conditional ``n3=51`` lane."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from pysat.solvers import Solver

import wave16_n3_51_active_sat as sat
import wave16_n3_51_profiles as profiles
import wave16_n3_51_verify as verify


ROOT = Path(__file__).resolve().parents[1]
ATTEMPTS = ROOT / "attempts" / "wave16-n3-51-computation"
PROFILE_PATH = ATTEMPTS / "n3-51-profile-census.json"
SCAN_PATH = ATTEMPTS / "n3-51-active-local-scan.json"
CANDIDATE_PATH = (
    ATTEMPTS
    / "n3-51-r16-q2x14-q3x2-no-size3-"
    "active-local-candidate.json"
)


class ProfileTests(unittest.TestCase):
    def test_exact_profile_and_branch_counts(self) -> None:
        report = profiles.build_report()
        semantic = report["semantic"]
        self.assertEqual(len(semantic["raw_profiles"]), 16)
        self.assertEqual(
            tuple(semantic["surviving_profiles"]),
            profiles.EXPECTED_SURVIVING_PROFILES,
        )
        self.assertEqual(
            tuple(
                (row["profile_id"], row["branch_id"])
                for row in semantic[
                    "post_finite_surviving_branches"
                ]
            ),
            profiles.EXPECTED_SURVIVING_BRANCHES,
        )

    def test_large_point_obstruction(self) -> None:
        report = profiles.build_report()
        for details in report["semantic"][
            "large_point_reductions"
        ].values():
            self.assertEqual(
                details["remaining_point_sizes"],
                [2, 3],
            )
            for obstruction in details[
                "size_obstructions"
            ].values():
                self.assertTrue(
                    obstruction["strict_contradiction"]
                )

    def test_profile_artifact_independent_replay(self) -> None:
        result = verify.validate_profile_artifact(PROFILE_PATH)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["raw_profile_count"], 16)
        self.assertEqual(result["post_finite_branch_count"], 7)


class CandidateTests(unittest.TestCase):
    def test_positive_active_local_candidate(self) -> None:
        candidate = json.loads(
            CANDIDATE_PATH.read_text(encoding="utf-8")
        )
        result = verify.validate_candidate_object(candidate)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["point_count"], 24)
        self.assertEqual(result["size3_point_count"], 0)
        self.assertEqual(result["k_edge_count"], 69)

    def test_positive_candidate_extends_to_cnf(self) -> None:
        candidate = json.loads(
            CANDIDATE_PATH.read_text(encoding="utf-8")
        )
        spec = sat.profile_specs()[candidate["profile_id"]]
        instance = sat.build_instance(spec)
        fixed = verify.fixed_candidate_assumptions(
            instance,
            candidate,
        )
        with Solver(
            name="glucose42",
            bootstrap_with=instance.cnf.clauses,
        ) as solver:
            self.assertTrue(solver.solve(assumptions=fixed))

    def test_hostile_mutations(self) -> None:
        candidate = json.loads(
            CANDIDATE_PATH.read_text(encoding="utf-8")
        )
        scan = json.loads(SCAN_PATH.read_text(encoding="utf-8"))
        result = verify.mutation_checks(candidate, scan)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["mutation_count"], 20)


class FormulaTests(unittest.TestCase):
    def test_all_archived_formula_streams(self) -> None:
        result = verify.validate_scan(
            SCAN_PATH,
            rebuild_formulas=True,
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["branch_count"], 7)
        self.assertEqual(
            result["status_histogram"]["SAT_CANDIDATE"],
            1,
        )
        self.assertFalse(result["negative_results_evidentiary"])

    def test_failure_history_is_bound_to_final_scan(self) -> None:
        result = verify.validate_run_failures(
            ATTEMPTS / "n3-51-run-failures.json",
            SCAN_PATH,
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(
            result["historical_budget_unknown_count"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
