from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name("independent_verify.py")
SPEC = importlib.util.spec_from_file_location("wave156_independent", PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Wave156Tests(unittest.TestCase):
    def test_self_test(self) -> None:
        result = MODULE.self_test()
        self.assertEqual(result["dense_direction"], "PASS")
        self.assertEqual(result["base_graph_flag_semantics"], "PASS")

    def test_duplicate_direction_index_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "bad direction index"):
            MODULE.dense_direction(4, [1, 1], [2, 3])

    def test_out_of_range_direction_index_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "bad direction index"):
            MODULE.dense_direction(4, [4], [1])

    def test_fraction_exactness(self) -> None:
        self.assertEqual(MODULE.BASE.fraction("6/14"), MODULE.Fraction(3, 7))


if __name__ == "__main__":
    unittest.main()
