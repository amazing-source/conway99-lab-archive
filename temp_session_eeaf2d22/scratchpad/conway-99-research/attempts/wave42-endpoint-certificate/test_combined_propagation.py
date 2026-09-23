#!/usr/bin/env python3
"""Tests for the combined branch-15 plus seventh-triangle propagation."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "combined_propagation.py"
SPEC = importlib.util.spec_from_file_location("wave42_combined", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load Wave 42 combined propagation")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CombinedPropagationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.closure = json.loads(
            MODULE.DEFAULT_CLOSURE_OUTPUT.read_text(encoding="utf-8")
        )
        cls.probes = json.loads(
            MODULE.DEFAULT_PROBE_OUTPUT.read_text(encoding="utf-8")
        )

    def test_unit_rule_forces_last_literal(self) -> None:
        constraint = MODULE.Constraint(((1, False), (2, False), (3, False)), 1)
        status, forced = MODULE.evaluate_constraint(
            constraint,
            {1: True, 2: True},
        )
        self.assertEqual(status, "FORCE")
        self.assertEqual(forced, ((3, False),))

    def test_unit_rule_detects_contradiction(self) -> None:
        constraint = MODULE.Constraint(((1, False), (2, False)), 1)
        status, forced = MODULE.evaluate_constraint(
            constraint,
            {1: True, 2: True},
        )
        self.assertEqual(status, "CONTRADICTION")
        self.assertEqual(forced, ())

    def test_combined_closure_exact_census(self) -> None:
        result = self.closure["result"]
        self.assertEqual(result["total_forced_variables"], 830)
        self.assertEqual(result["forced_primary_variables"], 174)
        self.assertEqual(result["delta_sourced_derivations"], 0)
        self.assertTrue(result["assignments_exactly_match_wave41_closure"])
        self.assertEqual(
            result["syntactically_open_base_constraints"],
            574_351,
        )
        self.assertEqual(
            result["syntactically_open_delta_constraints"],
            64_932,
        )
        self.assertEqual(result["active_delta_constraints"], 33_778)
        self.assertEqual(
            result["wave41_open_base_plus_active_delta"],
            608_129,
        )
        self.assertIsNone(result["contradiction"])

    def test_delta_has_no_slack_one_row_at_closure(self) -> None:
        result = self.closure["result"]
        self.assertEqual(result["slack_one_base_constraints"], 2_713)
        self.assertEqual(result["slack_one_delta_constraints"], 0)

    def test_probe_scope_is_exact(self) -> None:
        self.assertEqual(
            self.probes["probe_variables"],
            list(MODULE.PROBE_VARIABLES),
        )
        self.assertEqual(self.probes["probe_count"], 64)

    def test_probe_result_retains_unknown_status(self) -> None:
        result = self.probes["result"]
        self.assertEqual(result["candidate_implication_count"], 0)
        self.assertEqual(result["doubly_failed_variable_count"], 0)
        self.assertFalse(result["branch15_candidate_unsat_by_failed_literal"])
        self.assertEqual(result["branch15"], "UNKNOWN")
        self.assertEqual(result["endpoint_cases_closed"], 0)

    def test_committed_artifacts_replay_exactly(self) -> None:
        replay = MODULE.verify_committed()
        self.assertEqual(replay["status"], "PASS_EXACT_REPLAY")
        self.assertEqual(replay["forced_variables"], 830)
        self.assertEqual(replay["candidate_implications"], 0)


if __name__ == "__main__":
    unittest.main()
