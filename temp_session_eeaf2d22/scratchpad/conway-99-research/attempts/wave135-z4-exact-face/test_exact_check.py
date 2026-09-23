"""Tests for the Wave135 exact affine-face checkpoint."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave135_exact_check", HERE / "exact_check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rank = CHECK.verify_rank(HERE / "face-rank.json")

    def test_exact_rank_certificate(self):
        self.assertEqual(self.rank["forbidden_rank_Q"], 143)
        self.assertEqual(self.rank["dependency_dimension"], 18)
        self.assertEqual(self.rank["affine_rank_Q"], 146)
        self.assertEqual(self.rank["affine_dimension_Q"], 973)

    def test_unshifted_run_remains_unknown(self):
        payload = json.loads(
            (HERE / "row-generation-unshifted.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(payload["classification"], "UNKNOWN_WALL")
        self.assertEqual(len(payload["trace"]), 5)
        self.assertEqual(payload["trace"][-1]["violated_rows"], 451)

    def test_shifted_run_remains_unknown(self):
        result = CHECK.verify_search(HERE / "row-generation.json")
        self.assertEqual(result["classification"], "UNKNOWN_WALL")
        self.assertFalse(result["terminal_witness_replayed"])
        payload = json.loads(
            (HERE / "row-generation.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(payload["trace"]), 6)
        self.assertEqual(payload["trace"][-1]["violated_rows"], 521)

    def test_modular_rank_detects_dependence(self):
        self.assertEqual(CHECK.modular_rank([[1, 2], [2, 4]]), 1)
        self.assertEqual(CHECK.modular_rank([[1, 2], [2, 5]]), 2)


if __name__ == "__main__":
    unittest.main()
