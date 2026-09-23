from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave193_audit_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave193AuditTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_dual_identity(self) -> None:
        result = MODULE.derive()
        self.assertEqual(result["certificate"]["reduced_difference"], {})
        self.assertEqual(len(result["certificate"]["multipliers"]), 12)

    def test_integral_bound(self) -> None:
        bound = MODULE.derive()["bound"]
        self.assertEqual(bound["reduced_fraction"], "81774/13")
        self.assertEqual(bound["Q"], 6291)
        self.assertEqual(bound["edge_added_projective"], 6984)
        self.assertEqual(bound["scalar_short_circuit_words"], 13968)

    def test_collision_rows_frozen(self) -> None:
        rows = MODULE.derive()["collision_rows"]
        self.assertEqual(rows["SR"], "3*h+3*Y/2>=a2+a3+b3+c2")
        self.assertEqual(rows["SL"], "2*n1+4*n2+r1+2*r2+Y+2*W>=C")


if __name__ == "__main__":
    unittest.main()

