from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave189_exact_check", ROOT / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave189ExactCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = MODULE.derive()

    def test_coefficient_certificate(self) -> None:
        cert = self.result["coefficient_certificate"]
        self.assertEqual(cert["lhs_12Q"], [18, 12, 24, 12, 6])
        self.assertEqual(cert["seven_I"], [14, 14, 21, 7, 7])
        self.assertEqual(cert["nonnegative_remainder"], [4, -2, 3, 5, -1])

    def test_orbit_closure(self) -> None:
        orbit = self.result["orbit_closure"]
        self.assertEqual(orbit["raw_assignment_bound"], "A<=2*r+3*h")
        self.assertTrue(orbit["type2_same_label_pair_excluded"])

    def test_equality_face(self) -> None:
        face = self.result["equality_face_before_strictness"]
        self.assertEqual(face["n3"], 1386)
        self.assertEqual(face["p3"], 4158)
        self.assertEqual(face["multiplicity_at_most_two_extraction_circuits"], 2079)
        self.assertEqual(face["exact_three_extraction_orbit_pairs"], 0)

    def test_local_weight_seven_relations(self) -> None:
        local = self.result["strict_local_relation"]
        self.assertEqual(local["difference_side_weights"], [[2, 5], [2, 5]])
        self.assertEqual(local["difference_weights"], [7, 7])

    def test_design_boundary(self) -> None:
        design = self.result["design_null_control"]
        self.assertEqual(design["candidate_flags"], 13860)
        self.assertEqual(design["conflict_graph_degree"], 27)
        self.assertEqual(design["hoffman_independence_bound"], 1386)

    def test_final_bounds(self) -> None:
        bounds = self.result["bounds"]
        self.assertEqual(bounds["nonedge_projective_circuits_Q"], 4852)
        self.assertEqual(bounds["all_projective_short_circuits"], 5545)
        self.assertEqual(bounds["scalar_short_circuit_words"], 11090)
        self.assertGreater(bounds["verified_Wave188_all_short_word_bound_remains"], 11090)

    def test_frozen_result(self) -> None:
        expected = json.loads((ROOT / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(self.result, expected)

    def test_input_freeze(self) -> None:
        self.assertEqual(MODULE.verify_input_freeze(), 7)


if __name__ == "__main__":
    unittest.main()
