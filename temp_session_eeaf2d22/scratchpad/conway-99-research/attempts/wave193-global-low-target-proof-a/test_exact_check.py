from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave193_proof_a", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave193ProofATest(unittest.TestCase):
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
                "a1": "17/39",
                "a2": "17/39",
                "a3": "5/39",
                "b1": "4/13",
                "r2": "35/117",
                "W": "37/39",
            },
        )

    def test_bound(self) -> None:
        bound = self.result["bound"]
        self.assertEqual(bound["Q"], 6291)
        self.assertEqual(bound["edge_added_projective"], 6984)
        self.assertEqual(bound["circuit_scalar_words"], 13968)

    def test_fractional_rounding(self) -> None:
        bound = self.result["bound"]
        self.assertEqual(bound["floor"], 6290)
        self.assertEqual(bound["remainder"], 12)

    def test_null_counts(self) -> None:
        null = self.result["integer_null"]
        self.assertEqual(null["I"], 8316)
        self.assertEqual(null["Q0"], 6291)
        self.assertFalse(null["is_object"])

    def test_null_slacks(self) -> None:
        null = self.result["integer_null"]
        self.assertEqual(null["exact3_slack"], 1)
        self.assertEqual(null["residual_slack"], "1")
        self.assertEqual(null["leaf_slack"], 1)

    def test_scope(self) -> None:
        self.assertIn("no graph", self.result["search_scope"].lower())
        self.assertIn("no graph", self.result["search_scope"])


if __name__ == "__main__":
    unittest.main()
