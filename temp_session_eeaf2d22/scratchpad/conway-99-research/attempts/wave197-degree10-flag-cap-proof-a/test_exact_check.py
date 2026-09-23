from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave197_proof_a", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave197ProofATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.derive()

    def test_degree_ten(self) -> None:
        local = self.result["local_incidence"]
        self.assertEqual(local["flag_supports_per_orientation"], 5)
        self.assertEqual(local["selected_exact3_degree_cap"], 10)

    def test_global_caps(self) -> None:
        local = self.result["local_incidence"]
        self.assertEqual(local["global_flag_cap"], 1287)
        self.assertEqual(local["global_oriented_label_cap"], 3564)

    def test_certificate(self) -> None:
        certificate = self.result["certificate"]
        self.assertTrue(certificate["all_remainder_coefficients_nonnegative"])
        self.assertEqual(
            certificate["remainder_coefficients"],
            {
                "a1": "1/10",
                "b3": "3/5",
                "c2": "1/5",
                "g": "4/15",
                "W": "2/5",
            },
        )

    def test_null_control(self) -> None:
        control = self.result["rational_null_control"]
        self.assertFalse(control["is_object"])
        self.assertEqual(control["target"], "70323/10")
        for slack in ("SI", "S2", "SE2", "RA", "SL", "S10", "SH", "SF"):
            self.assertEqual(control["evaluation"][slack], "0")
        self.assertEqual(control["evaluation"]["S36"], "99/5")

    def test_bound(self) -> None:
        bound = self.result["bound"]
        self.assertEqual(bound["rational_Q0"], "70323/10")
        self.assertEqual(bound["integral_Q"], 7033)
        self.assertEqual(bound["edge_added_projective"], 7726)
        self.assertEqual(bound["circuit_scalar_words"], 15452)

    def test_scope(self) -> None:
        scope = self.result["search_scope"].lower()
        self.assertIn("no graph", scope)
        self.assertNotIn("numerical", scope)


if __name__ == "__main__":
    unittest.main()
