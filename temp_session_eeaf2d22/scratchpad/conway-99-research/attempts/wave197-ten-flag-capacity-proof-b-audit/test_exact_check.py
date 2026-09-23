from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave197_b", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave197ProofBAuditTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_per_label_capacity(self) -> None:
        capacity = MODULE.local_capacity()
        self.assertEqual(capacity["triangles_through_leaf"], 7)
        self.assertEqual(capacity["triangles_meeting_center"], 2)
        self.assertEqual(capacity["flags_per_orientation"], 5)
        self.assertEqual(capacity["flags_per_unordered_nonedge"], 10)

    def test_private_weight(self) -> None:
        capacity = MODULE.local_capacity()
        self.assertEqual(capacity["private_label_selected_multiplicity"], 1)
        self.assertEqual(
            capacity["weighted_selected_row"],
            "3*n3+9*p3<=10*|U|",
        )

    def test_global_rows(self) -> None:
        rows = MODULE.derive()["global_rows"]
        self.assertIn("9*p3", rows["S10"])
        self.assertEqual(rows["SF"], "13*V-n3-h-g>=0")

    def test_certificate(self) -> None:
        cert = MODULE.certificate()
        self.assertEqual(cert["reduced_difference"], {})
        self.assertEqual(cert["target"], "70323/10")
        self.assertEqual(cert["integer_Q_lower_bound"], 7033)
        self.assertEqual(cert["edge_added_projective"], 7726)
        self.assertEqual(cert["circuit_scalar_words"], 15452)

    def test_active_null(self) -> None:
        null = MODULE.certificate()["active_null"]
        self.assertTrue(null["all_eight_slacks_zero"])
        self.assertFalse(null["asserted_object"])


if __name__ == "__main__":
    unittest.main()
