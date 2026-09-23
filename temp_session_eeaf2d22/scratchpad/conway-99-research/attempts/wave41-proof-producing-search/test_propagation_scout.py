from __future__ import annotations

import gzip
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("propagation_scout.py")
SPEC = importlib.util.spec_from_file_location("wave41_propagation_scout", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PropagationScoutTests(unittest.TestCase):
    def test_parse_and_force(self) -> None:
        constraint = MODULE.parse_constraint(b"+1 x1 +1 ~x2 >= 2 ;\n")
        self.assertEqual(
            MODULE.evaluate_constraint(constraint, {1: True}),
            ("FORCE", ((2, False),)),
        )

    def test_open_constraint(self) -> None:
        constraint = MODULE.parse_constraint(b"+1 x1 +1 x2 >= 1 ;\n")
        self.assertEqual(
            MODULE.evaluate_constraint(constraint, {}),
            ("OPEN", ()),
        )

    def test_contradiction(self) -> None:
        constraint = MODULE.parse_constraint(b"+1 x1 +1 ~x2 >= 2 ;\n")
        self.assertEqual(
            MODULE.evaluate_constraint(constraint, {1: False}),
            ("CONTRADICTION", ()),
        )

    def test_rejects_non_unit_coefficient(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.parse_constraint(b"+2 x1 >= 1 ;\n")

    def test_frozen_source_closure_is_deterministic(self) -> None:
        first = MODULE.propagate(MODULE.DEFAULT_SOURCE)
        second = MODULE.propagate(MODULE.DEFAULT_SOURCE)
        self.assertEqual(first, second)
        self.assertGreater(first["result"]["total_forced_variables"], 0)
        self.assertEqual(
            first["result"]["status"],
            "CANDIDATE_PROPAGATION_FIXED_POINT",
        )
        self.assertIsNone(first["result"]["contradiction"])
        self.assertEqual(first["coverage"]["endpoint_cases_closed"], 0)


if __name__ == "__main__":
    unittest.main()
