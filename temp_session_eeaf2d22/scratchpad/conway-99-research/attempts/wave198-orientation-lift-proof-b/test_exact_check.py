from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave198_b", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave198OrientationLiftTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_orientation_capacity(self) -> None:
        row = MODULE.orientation_row()
        self.assertEqual(row["flags_per_orientation"], 5)
        self.assertEqual(row["unordered_capacity"], 10)
        self.assertEqual(row["private_weight_bonus"], 4)

    def test_strict_wave197_refinement(self) -> None:
        row = MODULE.orientation_row()
        self.assertEqual(row["wave197_relation"], "S10=2*S5+(3*n3-p3)")
        self.assertEqual(row["wave197_active_null_S5"], -165)

    def test_global_row(self) -> None:
        rows = MODULE.derive()["global_rows"]
        self.assertIn("4*p3", rows["S5"])
        self.assertEqual(rows["SF"], "13*V-n3-h-g>=0")

    def test_certificate(self) -> None:
        cert = MODULE.certificate()
        self.assertEqual(cert["reduced_difference"], {})
        self.assertEqual(cert["target"], "281457/40")
        self.assertEqual(cert["integer_Q_lower_bound"], 7037)
        self.assertEqual(cert["edge_added_projective"], 7730)
        self.assertEqual(cert["circuit_scalar_words"], 15460)

    def test_rational_null(self) -> None:
        null = MODULE.certificate()["rational_null"]
        self.assertTrue(null["all_eight_slacks_zero"])
        self.assertFalse(null["asserted_object"])


if __name__ == "__main__":
    unittest.main()
