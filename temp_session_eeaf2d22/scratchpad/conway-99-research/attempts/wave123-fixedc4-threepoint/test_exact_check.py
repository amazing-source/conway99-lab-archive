"""Tests for the exact Wave123 discovery package."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave123_exact_check", HERE / "exact_check.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Wave123Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.exact_results()

    def test_canonical_result(self) -> None:
        expected = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.result, expected)

    def test_all40_and_first26_fail_leverage(self) -> None:
        self.assertEqual(
            len(self.result["all40"]["coordinates_above_threshold"]), 46
        )
        self.assertEqual(
            len(self.result["first26"]["coordinates_above_threshold"]), 6
        )
        self.assertFalse(self.result["all40"]["diagonal_gate_passes"])
        self.assertFalse(self.result["first26"]["diagonal_gate_passes"])

    def test_explicit26_boundary(self) -> None:
        audit = self.result["explicit26"]["projector_audit"]
        self.assertTrue(audit["diagonal_gate_passes"])
        completion = audit["graph_valued_two_by_two_completion"]
        self.assertEqual(completion["invalid_pair_count"], 352)
        self.assertFalse(completion["passes_every_two_by_two_minor"])

    def test_three_point_blocks(self) -> None:
        audit = self.result["explicit26"]["rooted_three_point_audit"]
        self.assertEqual(audit["triple_count"], 2600)
        self.assertEqual(
            audit["pair_overlap_tuples_with_multiple_triple_intersections"],
            28,
        )
        self.assertEqual(audit["rooted_psd_blocks"]["total"], 2340)
        self.assertTrue(audit["code_only_three_point_gate_passes"])
        self.assertEqual(audit["minimum_tested_signed_triple_norm"], 22)

    def test_unknown_wall(self) -> None:
        status = self.result["status"]
        self.assertEqual(
            status["some_26_subset_passes_full_projector_completion"],
            "UNKNOWN",
        )
        self.assertFalse(status["rank28_excluded"])
        self.assertFalse(status["rank30_excluded"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
