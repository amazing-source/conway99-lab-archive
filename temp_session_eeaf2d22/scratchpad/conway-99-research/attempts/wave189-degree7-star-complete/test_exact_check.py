from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave189_exact_check", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave189ExactCheckTests(unittest.TestCase):
    def test_star_polygon_lift(self) -> None:
        CHECK.check_star_polygon_lift()

    def test_complete_rows(self) -> None:
        CHECK.check_complete_rows()
        self.assertEqual(CHECK.complete_dual_coefficient(7, 0), 99)
        self.assertEqual(CHECK.complete_dual_coefficient(0, 7), 99)

    def test_ordinary_and_type_moments(self) -> None:
        _, dual = CHECK.ordinary_enumerator()
        self.assertGreaterEqual(sum(dual[4:10]), 18018)
        CHECK.check_quadratic_type_moments()

    def test_companion_orbit_certificate(self) -> None:
        CHECK.check_cover_separation_arithmetic()
        self.assertEqual(12 * 4851, 14 * CHECK.C)

    def test_equality_face_cancellation(self) -> None:
        CHECK.check_equality_face_cancellation()

    def test_frozen_results(self) -> None:
        results = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(results["claim_label"], "DERIVED")
        self.assertEqual(results["strict_circuit_bound_Q"], 4852)
        self.assertEqual(results["dual_short_circuit_word_lower"], 11090)
        self.assertEqual(results["rank_11_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
