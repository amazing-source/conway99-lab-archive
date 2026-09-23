from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave42_branch15_delta_comparison", HERE / "comparison_check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class Branch15TriangleDeltaComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = CHECK.strict_load(HERE / "comparison.json")

    def test_archived_comparison_validates(self):
        CHECK.validate(self.result)

    def test_both_clause_sets_match_exactly(self):
        outcome = self.result["result"]
        self.assertTrue(outcome["raw_catalog_exact_match"])
        self.assertTrue(outcome["active_catalog_exact_match"])

    def test_discovery_remains_candidate(self):
        self.assertEqual(
            self.result["discovery_result"]["claim_label"], "CANDIDATE"
        )

    def test_terminal_scope_remains_unknown(self):
        outcome = self.result["result"]
        self.assertFalse(outcome["branch_15_closed"])
        self.assertEqual(outcome["endpoint_cases_closed"], 0)
        self.assertEqual(outcome["conway_99"], "UNKNOWN")

    def test_mutated_clause_digest_is_rejected(self):
        hostile = copy.deepcopy(self.result)
        hostile["active_catalog"]["normalized_clause_stream_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)

    def test_mutated_discovery_hash_is_rejected(self):
        hostile = copy.deepcopy(self.result)
        hostile["discovery_result"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)

    def test_inflated_terminal_status_is_rejected(self):
        hostile = copy.deepcopy(self.result)
        hostile["result"]["branch_15_closed"] = True
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)


if __name__ == "__main__":
    unittest.main()
