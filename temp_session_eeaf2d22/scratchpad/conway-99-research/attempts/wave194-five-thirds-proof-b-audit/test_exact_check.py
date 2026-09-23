from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave194_audit_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave194AuditTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_dual_identity(self) -> None:
        result = MODULE.derive()["certificate"]
        self.assertEqual(result["reduced_difference"], {})
        self.assertEqual(len(result["multipliers"]), 9)

    def test_endpoint_parent_intersection(self) -> None:
        local = MODULE.derive()["local_type2"]
        self.assertEqual(local["parent_x_profile"], [6, 2])
        self.assertEqual(local["parent_y_profile"], [2, 6])
        self.assertEqual(local["parent_intersection_size"], 2)
        self.assertLess(local["parent_intersection_size"], local["dual_distance"])

    def test_bound_and_null(self) -> None:
        result = MODULE.derive()
        self.assertEqual(result["bound"]["Q"], 6930)
        self.assertEqual(result["bound"]["edge_added_projective"], 7623)
        self.assertEqual(result["bound"]["scalar_short_circuit_words"], 15246)
        self.assertEqual(result["null_control"]["Q0"], 6930)
        self.assertFalse(result["null_control"]["asserted_object"])

    def test_joint_union_row(self) -> None:
        self.assertEqual(
            MODULE.derive()["rows"]["SL"],
            "n1+2*n2+c1+2*r2+y+2*W>=C",
        )


if __name__ == "__main__":
    unittest.main()
