#!/usr/bin/env python3
"""Hostile tests for the independent Wave 38 harvest verifier."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "wave38_harvest_independent_check",
    Path(__file__).resolve().with_name("independent_check.py"),
)
assert SPEC is not None and SPEC.loader is not None
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


class Wave38HarvestIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_results()
        cls.coverage = check.load_json(
            check.attempt_root() / "coverage-plan.json"
        )

    def test_exact_mapping_and_orbit_weights(self) -> None:
        coverage = self.result["coverage"]
        self.assertEqual(coverage["case_count"], 33)
        self.assertEqual(
            coverage["parent_orbit_weights"],
            {"4": 132, "5": 528, "8": 704, "10": 1056, "12": 4224},
        )
        self.assertEqual(coverage["endpoint_compatible_orbit_weight"], 6644)
        self.assertTrue(
            coverage["case_mapping_matches_independent_orbit_reconstruction"]
        )

    def test_path_plan_has_no_windows_collisions(self) -> None:
        plan = self.result["path_plan"]
        self.assertEqual(plan["case_owned_artifact_count"], 231)
        self.assertEqual(plan["casefold_collisions"], 0)
        self.assertEqual(plan["traversal_or_absolute_paths"], 0)

    def test_proof_coverage_remains_zero(self) -> None:
        boundary = self.result["proof_boundary"]
        self.assertEqual(boundary["proof_coverage_numerator"], 0)
        self.assertEqual(boundary["proof_coverage_denominator"], 33)
        self.assertEqual(boundary["planned_artifacts_present"], 0)
        self.assertEqual(self.result["conclusion"]["proof_coverage"], "0/33")

    def test_missing_case_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.coverage)
        mutated["cases"].pop()
        with self.assertRaisesRegex(AssertionError, "case count"):
            check.verify_coverage(mutated)

    def test_orbit_weight_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.coverage)
        mutated["cases"][0]["orbit_size"] += 1
        with self.assertRaisesRegex(AssertionError, "orbit_size"):
            check.verify_coverage(mutated)

    def test_casefold_path_collision_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.coverage)
        path = mutated["cases"][0]["planned_artifacts"]["opb"]
        mutated["cases"][1]["planned_artifacts"]["opb"] = path.upper()
        with self.assertRaises(AssertionError):
            check.verify_coverage(mutated)

    def test_path_traversal_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.coverage)
        mutated["cases"][0]["planned_artifacts"]["opb"] = (
            "logs/local/wave38-endpoint-33/../escape.opb"
        )
        with self.assertRaisesRegex(AssertionError, "traversal|changed"):
            check.verify_coverage(mutated)

    def test_uncertified_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.coverage)
        mutated["cases"][0]["proof_status"] = "VERIFIED_UNSAT"
        with self.assertRaisesRegex(AssertionError, "proof promoted"):
            check.verify_coverage(mutated)

    def test_snapshot_terminal_promotion_is_rejected(self) -> None:
        snapshot = check.load_json(
            check.attempt_root() / "process-snapshot.json"
        )
        live = check.load_json(check.verifier_root() / "live-observation.json")
        mutated = copy.deepcopy(snapshot)
        mutated["terminal_results"] = [{"case": 15, "status": "UNSAT"}]
        with self.assertRaisesRegex(AssertionError, "terminal results"):
            check.verify_snapshot(mutated, live, check.EXPECTED_IDS)

    def test_strict_json_rejects_duplicate_keys_and_nan(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            duplicate = Path(raw) / "duplicate.json"
            duplicate.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                check.load_json(duplicate)
            nan = Path(raw) / "nan.json"
            nan.write_text('{"a":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-standard"):
                check.load_json(nan)

    def test_privacy_scan_rejects_secret_and_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            secret = Path(raw) / "secret.txt"
            secret.write_text("Authorization: Bearer abc.def", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "privacy-sensitive"):
                check.verify_privacy([secret])
            absolute = Path(raw) / "absolute.txt"
            absolute.write_text("C:\\\\Users\\\\RESEARCHER", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "privacy-sensitive"):
                check.verify_privacy([absolute])

    def test_final_status_unknown(self) -> None:
        conclusion = self.result["conclusion"]
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["endpoint_constructed"])
        self.assertFalse(conclusion["upper_bound_improved_below_4158"])
        self.assertEqual(conclusion["target_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
