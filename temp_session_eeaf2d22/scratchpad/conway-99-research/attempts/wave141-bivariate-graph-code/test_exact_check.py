"""Regression tests for the exact Wave141 structural replay."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave141_exact_check",
    HERE / "exact_check.py",
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class ExactCheckTests(unittest.TestCase):
    def test_small_transform(self) -> None:
        result = CHECK.small_transform_replay()
        self.assertTrue(result["all_16_transform_rows_pass"])

    def test_d8_rank(self) -> None:
        result = CHECK.d8_rank_record()
        self.assertEqual(result["invariant_dimension"], 1275)
        self.assertEqual(
            result["combined_output_parity_and_transform_rank"],
            3725,
        )

    def test_signed_six_row(self) -> None:
        rows, _ = CHECK.signed_affine_rows()
        self.assertEqual(rows[6]["constant"], "2024484")
        self.assertEqual(rows[6]["n3_coefficient"], "512/3")

    def test_canonical_result(self) -> None:
        expected = CHECK.canonical_json(CHECK.build_results())
        observed = (HERE / "exact-results.json").read_text(encoding="utf-8")
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
