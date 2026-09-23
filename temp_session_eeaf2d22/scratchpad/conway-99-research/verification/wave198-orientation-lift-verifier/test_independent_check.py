from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave198_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave198IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.math = MODULE.build_math_result()
        cls.results = MODULE.build_results()

    def test_frozen_math(self) -> None:
        expected = json.loads(
            (HERE / "independent-math-result.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.math, expected)

    def test_orientation(self) -> None:
        row = self.math["orientation"]
        self.assertEqual(row["m_upper"], 5)
        self.assertEqual(row["T_degree_sum"], "3n3<=p3+5(T-p3)=5T-4p3")
        self.assertEqual(row["S5"], "17820-3n3-4p3-5a3-5b3>=0")

    def test_certificate(self) -> None:
        cert = self.math["certificate"]
        self.assertEqual(cert["rational_target"], "281457/40")
        self.assertEqual(cert["integer_Q"], 7037)
        self.assertEqual(cert["weights"]["S5"], "1/40")

    def test_integer_control(self) -> None:
        control = self.math["integer_control"]
        self.assertEqual(control["derived"]["Q0"], 7037)
        self.assertEqual(control["rounding_gap"], "23/40")
        self.assertFalse(control["asserted_object"])

    def test_counts(self) -> None:
        bounds = self.math["bounds"]
        self.assertEqual(bounds["all_projective"], 7730)
        self.assertEqual(bounds["scalar_words"], 15460)

    def test_integrity(self) -> None:
        self.assertTrue(self.results["integrity"]["passed"])
        self.assertFalse(
            self.results["integrity"]["sources_opened_before_independent_freeze"]
        )

    def test_sources(self) -> None:
        sources = self.results["source_comparisons"]
        self.assertTrue(sources["primary_matches"])
        self.assertEqual(sources["hostile_verdict"], "ACCEPT")
        self.assertTrue(sources["independent_integer_control_distinct"])

    def test_boundary(self) -> None:
        self.assertEqual(self.results["verdict"], "VERIFIED_WITH_SCOPE")
        boundary = self.results["boundary"]
        self.assertFalse(boundary["rank_11_excluded"])
        self.assertFalse(boundary["endpoint_excluded"])
        self.assertEqual(boundary["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
