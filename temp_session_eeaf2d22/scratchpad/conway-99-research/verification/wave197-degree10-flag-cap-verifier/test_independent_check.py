from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave197_independent", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave197IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.math = MODULE.build_math_result()
        cls.results = MODULE.build_results()

    def test_frozen_math(self) -> None:
        expected = json.loads(
            (HERE / "independent-math-result.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.math, expected)

    def test_orientation_degree(self) -> None:
        degree = self.math["orientation_degree"]
        self.assertEqual(degree["third_block_choices"], 5)
        self.assertEqual(degree["oriented_degree_upper"], 5)
        self.assertEqual(degree["undirected_degree_upper"], 10)

    def test_selected_hypergraph(self) -> None:
        selected = self.math["selected_flag_hypergraph"]
        self.assertIn("exactly one", selected["private_labels"])
        self.assertEqual(selected["S10"], "10H-9p3-3n3>=0")

    def test_headroom_and_flag_caps(self) -> None:
        caps = self.math["headroom_and_flag_caps"]
        self.assertEqual(caps["SH"], "6C/7-H-a3-b3>=0")
        self.assertEqual(caps["SF"], "13C/42-n3-h-g>=0")
        self.assertEqual(caps["old_raw_capacity"], "R3=3h-a3-b3>=0")

    def test_certificate(self) -> None:
        cert = self.math["coefficient_certificate"]
        self.assertEqual(cert["exact_rational_target"], "70323/10")
        self.assertEqual(cert["integer_nonedge_projective_Q"], 7033)
        self.assertEqual(cert["weights"]["S10"], "1/90")

    def test_integer_rounding_control(self) -> None:
        control = self.math["integer_rounding_control"]
        self.assertEqual(control["Q0"], 7033)
        self.assertEqual(control["rounding_gap"], "7/10")
        self.assertEqual(control["gap_accounted_by"], "a1/10 with a1=7")
        self.assertFalse(
            control["asserted_to_be_graph_code_cover_or_flag_family"]
        )
        self.assertTrue(
            all(value == 0 for value in control["zero_certificate_slacks"].values())
        )

    def test_integrity(self) -> None:
        integrity = self.results["integrity"]
        self.assertTrue(integrity["passed"])
        self.assertFalse(integrity["sources_opened_before_independent_freeze"])

    def test_primary_comparison(self) -> None:
        comparison = self.results["primary_comparison"]
        self.assertTrue(comparison["independent_split_recombines_to_source_S10"])
        self.assertTrue(comparison["source_rational_null_replayed"])
        self.assertTrue(
            comparison["independent_integer_rounding_control_is_distinct"]
        )

    def test_proof_b_comparison(self) -> None:
        proof_b = self.results["proof_b_comparison"]
        self.assertEqual(proof_b["verdict"], "ACCEPT")
        self.assertFalse(proof_b["used_as_mathematical_premise"])

    def test_counts(self) -> None:
        bounds = self.math["bounds"]
        self.assertEqual(bounds["integer_nonedge_projective_Q"], 7033)
        self.assertEqual(bounds["all_projective_short_circuits"], 7726)
        self.assertEqual(bounds["scalar_short_circuit_words"], 15452)

    def test_verdict_boundary(self) -> None:
        self.assertEqual(self.results["verdict"], "VERIFIED_WITH_SCOPE")
        boundary = self.results["boundary"]
        self.assertFalse(boundary["rank_11_excluded"])
        self.assertFalse(boundary["endpoint_excluded"])
        self.assertEqual(boundary["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
