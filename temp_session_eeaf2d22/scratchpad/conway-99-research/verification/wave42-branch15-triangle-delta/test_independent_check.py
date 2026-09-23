from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave42_branch15_delta_independent", HERE / "independent_check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class Branch15TriangleDeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = CHECK.strict_load(HERE / "independent-results.json")

    def test_archived_result_validates(self):
        CHECK.validate(self.result)

    def test_exact_raw_census(self):
        delta = self.result["delta"]
        self.assertEqual(delta["raw_clause_count"], 64932)
        self.assertEqual(delta["raw_width_distribution"], {"3": 132, "5": 64800})

    def test_exact_active_census(self):
        delta = self.result["delta"]
        self.assertEqual(delta["active_clause_count"], 33778)
        self.assertEqual(
            delta["active_width_distribution"],
            {"3": 91, "4": 580, "5": 33107},
        )

    def test_x2_is_independently_forced(self):
        derivation = self.result["propagation"]["x2_derivation"]
        self.assertTrue(derivation["value"])
        self.assertEqual(derivation["source_term_count"], 1)
        self.assertEqual(derivation["source_bound"], 1)
        self.assertEqual(
            len(self.result["propagation"]["assignment_stream_sha256"]), 64
        )

    def test_triangle_uses_exact_rooted_labels(self):
        self.assertEqual(
            self.result["delta"]["triangle_full_vertices_zero_based"],
            [1, 15, 17],
        )
        self.assertEqual(self.result["delta"]["triangle_closing_variable"], 2)

    def test_no_unit_or_contradiction_is_claimed(self):
        delta = self.result["delta"]
        self.assertEqual(delta["active_unit_count"], 0)
        self.assertEqual(delta["active_empty_count"], 0)
        self.assertFalse(self.result["result"]["branch_15_closed"])

    def test_endpoint_scope_does_not_inflate(self):
        self.assertEqual(self.result["result"]["endpoint_cases_closed"], 0)
        self.assertEqual(self.result["result"]["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(self.result["result"]["conway_99"], "UNKNOWN")

    def test_mutated_count_is_rejected(self):
        hostile = copy.deepcopy(self.result)
        hostile["delta"]["active_clause_count"] += 1
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)

    def test_mutated_terminal_status_is_rejected(self):
        hostile = copy.deepcopy(self.result)
        hostile["result"]["branch_15_closed"] = True
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)

    def test_duplicate_json_keys_are_rejected(self):
        path = HERE / "_hostile_duplicate.json"
        try:
            path.write_text('{"x": 1, "x": 2}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                CHECK.strict_load(path)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
