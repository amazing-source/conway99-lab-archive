"""Regression tests for Wave143 exact endpoint replay."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave143_exact_check",
    HERE / "exact_check.py",
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class EndpointTests(unittest.TestCase):
    def test_all_endpoints(self) -> None:
        expected = {
            "projection-optimum-plus-min.json": (
                1,
                "projection_optimum",
                "min",
                Fraction(0),
            ),
            "projection-optimum-plus-max.json": (
                1,
                "projection_optimum",
                "max",
                Fraction(838878579, 128),
            ),
            "projection-optimum-minus-min.json": (
                -1,
                "projection_optimum",
                "min",
                Fraction(0),
            ),
            "projection-optimum-minus-max.json": (
                -1,
                "projection_optimum",
                "max",
                Fraction(838878579, 128),
            ),
            "witness-plus-n3-708.json": (
                1,
                "fixed_n3",
                None,
                Fraction(708),
            ),
            "witness-plus-n3-4158.json": (
                1,
                "fixed_n3",
                None,
                Fraction(4158),
            ),
            "witness-minus-n3-708.json": (
                -1,
                "fixed_n3",
                None,
                Fraction(708),
            ),
            "witness-minus-n3-4158.json": (
                -1,
                "fixed_n3",
                None,
                Fraction(4158),
            ),
        }
        for filename, (sign, kind, sense, n3) in expected.items():
            with self.subTest(filename=filename):
                result = CHECK.verify(HERE / filename)
                self.assertEqual(result["sign"], sign)
                self.assertEqual(result["witness_kind"], kind)
                self.assertEqual(result["sense"], sense)
                self.assertEqual(Fraction(result["n3"]), n3)
                self.assertTrue(result["all_94_shadow_bounds_pass"])


if __name__ == "__main__":
    unittest.main()
