#!/usr/bin/env python3
"""Tests for the Wave 38 solver-harvest checker."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import verify_harvest


class HarvestVerifierTests(unittest.TestCase):
    def write_json(self, root: Path, name: str, value: object) -> Path:
        path = root / name
        path.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return path

    def test_bundled_artifacts_pass(self) -> None:
        result = verify_harvest.verify()
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["case_count"], 33)
        self.assertEqual(result["terminal_result_count"], 0)

    def test_missing_case_fails(self) -> None:
        coverage = verify_harvest.load_json(verify_harvest.DEFAULT_COVERAGE)
        coverage["cases"].pop()
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_json(Path(temporary), "coverage.json", coverage)
            with self.assertRaisesRegex(AssertionError, "deterministic reconstruction"):
                verify_harvest.verify_coverage(path)

    def test_solver_timeout_cannot_be_promoted(self) -> None:
        snapshot = verify_harvest.load_json(verify_harvest.DEFAULT_SNAPSHOT)
        snapshot["runs"][0]["status"] = "UNSAT"
        snapshot["runs"][0]["terminal_result"] = "UNSAT"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_json(Path(temporary), "snapshot.json", snapshot)
            coverage = verify_harvest.verify_coverage(
                verify_harvest.DEFAULT_COVERAGE
            )
            with self.assertRaisesRegex(AssertionError, "promoted"):
                verify_harvest.verify_snapshot(path, coverage)

    def test_positive_cpu_is_not_a_result(self) -> None:
        snapshot = copy.deepcopy(
            verify_harvest.load_json(verify_harvest.DEFAULT_SNAPSHOT)
        )
        snapshot["evidentiary_value"] = "UNSAT_EVIDENCE"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_json(Path(temporary), "snapshot.json", snapshot)
            coverage = verify_harvest.verify_coverage(
                verify_harvest.DEFAULT_COVERAGE
            )
            with self.assertRaisesRegex(AssertionError, "no evidentiary value"):
                verify_harvest.verify_snapshot(path, coverage)


if __name__ == "__main__":
    unittest.main()
