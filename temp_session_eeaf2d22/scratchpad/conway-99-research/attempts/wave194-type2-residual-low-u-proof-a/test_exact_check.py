from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave194_proof_a", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave194ProofATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.derive()

    def test_certificate_remainder(self) -> None:
        self.assertTrue(
            self.result["certificate"]["all_remainder_coefficients_nonnegative"]
        )
        self.assertEqual(
            self.result["certificate"]["remainder_coefficients"],
            {
                "a1": "1/3",
                "b1": "1/6",
                "b3": "1/2",
                "r2": "1/3",
                "W": "1/3",
            },
        )

    def test_bound(self) -> None:
        bound = self.result["bound"]
        self.assertEqual(bound["Q"], 6930)
        self.assertEqual(bound["edge_added_projective"], 7623)
        self.assertEqual(bound["circuit_scalar_words"], 15246)

    def test_joint_capacity_rows(self) -> None:
        rows = self.result["capacity_rows"]
        self.assertIn("2*b3", rows["residual"])
        self.assertIn("2*n2", rows["leaf_joint"])
        self.assertNotIn("3*n2", rows["leaf_joint"])

    def test_equality_face(self) -> None:
        face = self.result["equality_face"]
        self.assertEqual(face["packet_identity"], "h+n3=C/3")
        self.assertEqual(face["nonzero_formulas"]["n1"], "3*t")
        self.assertEqual(face["nonzero_formulas"]["p3"], "C-3*t")
        self.assertFalse(face["is_construction"])

    def test_equality_controls(self) -> None:
        controls = self.result["equality_face"]["controls"]
        self.assertEqual([item["parameter_t"] for item in controls], [0, 693, 1386])
        for item in controls:
            self.assertEqual(item["I"], 8316)
            self.assertEqual(item["Q0"], 6930)
            self.assertEqual(item["incidence_slack"], 0)
            self.assertEqual(item["exact2_slack"], 0)
            self.assertEqual(item["exact3_slack"], 0)
            self.assertEqual(item["residual_slack"], 0)
            self.assertEqual(item["leaf_slack"], 0)
            self.assertFalse(item["is_object"])

    def test_endpoint_rows(self) -> None:
        left, _, right = self.result["equality_face"]["controls"]
        self.assertEqual(left["row"]["n3"], 1386)
        self.assertEqual(left["row"]["c1"], 4158)
        self.assertEqual(right["row"]["n1"], 4158)
        self.assertEqual(right["row"]["h"], 1386)

    def test_scope(self) -> None:
        scope = self.result["search_scope"].lower()
        self.assertIn("no graph", scope)
        self.assertIn("no graph", self.result["search_scope"])


if __name__ == "__main__":
    unittest.main()
