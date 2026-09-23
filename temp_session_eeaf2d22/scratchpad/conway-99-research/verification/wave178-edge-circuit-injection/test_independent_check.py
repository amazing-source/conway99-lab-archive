from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave178_independent", MODULE)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave178Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.analyze()

    def test_injection_counts(self) -> None:
        self.assertEqual(self.result["support_multiplicity_upper"], 1)
        self.assertEqual(self.result["projective_circuit_lower"], 693)

    def test_scalar_factor(self) -> None:
        self.assertEqual(self.result["word_bound"], 1386)

    def test_only_even_short_weights(self) -> None:
        weights = {
            p["weight"]
            for item in self.result["cycle_types"].values()
            for p in item["profiles"]
        }
        self.assertEqual(weights, {4, 6, 8})

    def test_side_balance(self) -> None:
        for item in self.result["cycle_types"].values():
            for profile in item["profiles"]:
                self.assertEqual(
                    profile["left_support"], profile["right_support"]
                )

    def test_coefficient_balance(self) -> None:
        for item in self.result["cycle_types"].values():
            for profile in item["profiles"]:
                self.assertEqual(
                    profile["coefficient_1_count"],
                    profile["coefficient_2_count"],
                )

    def test_scope(self) -> None:
        self.assertIn("endpoint remains unknown", self.result["scope"])


if __name__ == "__main__":
    unittest.main()

