#!/usr/bin/env python3
"""Focused regression tests for the Wave 14 computational lane."""

from __future__ import annotations

import gc
import json
import unittest
from pathlib import Path

import wave14_n3_48_active_sat as sat
import wave14_n3_48_profiles as profiles
import wave14_n3_48_verify as verify
from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[1]
ATTEMPTS = ROOT / "attempts" / "wave14-computation"


def fixed_candidate_assumptions(
    instance: sat.Instance, candidate: dict[str, object]
) -> list[int]:
    selected_points = {
        frozenset(map(int, point)) for point in candidate["point_sets"]
    }
    selected_k_edges = {
        sat.edge(*map(int, item)) for item in candidate["K_edges"]
    }
    assumptions = list(
        sat.branch_assumptions(
            instance, candidate["branch"]["branch_id"]
        )
    )
    assumptions.extend(
        variable if point in selected_points else -variable
        for point, variable in instance.selected.items()
    )
    assumptions.extend(
        variable if item in selected_k_edges else -variable
        for item, variable in instance.k_edge.items()
    )
    return assumptions


class ProfileTests(unittest.TestCase):
    def test_exact_profiles_and_reduced_cover(self) -> None:
        report = profiles.build_report()
        semantic = report["semantic"]
        self.assertEqual(len(semantic["raw_profiles"]), 12)
        self.assertEqual(
            semantic["surviving_profiles"],
            [
                "r16-q2x16",
                "r15-q2x13-q3x2",
                "r14-q2x10-q3x4",
            ],
        )
        self.assertEqual(
            semantic["post_finite_surviving_branches"],
            [
                {
                    "profile_id": "r16-q2x16",
                    "branch_id": "no-size3",
                },
                {
                    "profile_id": "r16-q2x16",
                    "branch_id": "root-q3x0",
                },
                {
                    "profile_id": "r15-q2x13-q3x2",
                    "branch_id": "root-q3x0",
                },
                {
                    "profile_id": "r14-q2x10-q3x4",
                    "branch_id": "root-q3x0",
                },
            ],
        )

    def test_independent_profile_replay(self) -> None:
        result = verify.validate_profile_census(
            ATTEMPTS / "n3-48-profile-census.json"
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["post_finite_branch_count"], 4)


class CandidateTests(unittest.TestCase):
    def test_full_candidate(self) -> None:
        path = (
            ATTEMPTS
            / "n3-48-r16-q2x16-no-size3-full-candidate.json"
        )
        candidate = json.loads(path.read_text(encoding="utf-8"))
        result = verify.validate_candidate_object(candidate)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["variant"], sat.FULL)
        self.assertEqual(result["point_count"], 24)
        self.assertEqual(result["k_edge_count"], 72)

    def test_positive_controls(self) -> None:
        result = verify.validate_controls(
            ATTEMPTS / "n3-48-positive-controls.json"
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["control_count"], 2)

    def test_hostile_mutations(self) -> None:
        path = (
            ATTEMPTS
            / "n3-48-r16-q2x16-no-size3-full-candidate.json"
        )
        candidate = json.loads(path.read_text(encoding="utf-8"))
        result = verify.mutation_checks(candidate)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["mutation_count"], 9)


class FormulaTests(unittest.TestCase):
    def test_scan_formula_hashes_rebuild(self) -> None:
        scan = json.loads(
            (
                ATTEMPTS / "n3-48-active-local-scan.json"
            ).read_text(encoding="utf-8")
        )
        specs = sat.profile_specs()
        by_profile: dict[str, list[dict[str, object]]] = {}
        for row in scan["results"]:
            by_profile.setdefault(row["profile_id"], []).append(row)
        for profile_name, rows in by_profile.items():
            instance = sat.build_instance(specs[profile_name], sat.FULL)
            for row in rows:
                branch_id = row["branch"]["branch_id"]
                assumptions = sat.branch_assumptions(instance, branch_id)
                observed = sat.materialized_cnf_sha256(
                    instance, assumptions
                )
                expected = row["formula"]["materialized_dimacs_sha256"]
                self.assertEqual(observed, expected)
                self.assertEqual(
                    instance.pool.top, row["formula"]["variable_count"]
                )
                self.assertEqual(
                    len(instance.cnf.clauses) + len(assumptions),
                    row["formula"]["materialized_clause_count"],
                )
                if row["status"] == "SAT_CANDIDATE":
                    candidate = json.loads(
                        Path(row["candidate_path"]).read_text(
                            encoding="utf-8"
                        )
                    )
                    fixed = fixed_candidate_assumptions(
                        instance, candidate
                    )
                    with Solver(
                        name="glucose42",
                        bootstrap_with=instance.cnf.clauses,
                    ) as solver:
                        self.assertTrue(solver.solve(assumptions=fixed))
            del instance
            gc.collect()

    def test_control_formula_hashes_rebuild(self) -> None:
        controls = json.loads(
            (
                ATTEMPTS / "n3-48-positive-controls.json"
            ).read_text(encoding="utf-8")
        )
        specs = sat.profile_specs()
        for row in controls["results"]:
            instance = sat.build_instance(
                specs[row["profile_id"]], row["variant"]
            )
            assumptions = sat.branch_assumptions(
                instance, row["branch"]["branch_id"]
            )
            observed = sat.materialized_cnf_sha256(
                instance, assumptions
            )
            self.assertEqual(
                observed, row["formula"]["materialized_dimacs_sha256"]
            )
            candidate = json.loads(
                Path(row["candidate_path"]).read_text(encoding="utf-8")
            )
            fixed = fixed_candidate_assumptions(instance, candidate)
            with Solver(
                name="glucose42",
                bootstrap_with=instance.cnf.clauses,
            ) as solver:
                self.assertTrue(solver.solve(assumptions=fixed))
            del instance
            gc.collect()


if __name__ == "__main__":
    unittest.main()
