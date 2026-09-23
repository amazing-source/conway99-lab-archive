from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave178_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave178ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = MODULE.analyze()
        MODULE.verify(cls.data)

    def test_edge_and_word_counts(self) -> None:
        self.assertEqual(self.data["edge_count"], 693)
        self.assertEqual(
            self.data["dual_word_bound"], "B_4+B_6+B_8>=1386"
        )

    def test_all_short_profiles_are_even(self) -> None:
        weights = {
            profile["weight"]
            for item in self.data["cycle_types"].values()
            for profile in item["profiles"]
        }
        self.assertEqual(weights, {4, 6, 8})

    def test_all_short_profiles_are_side_balanced(self) -> None:
        for item in self.data["cycle_types"].values():
            for profile in item["profiles"]:
                self.assertEqual(
                    profile["left_support"], profile["right_support"]
                )

    def test_all_short_profiles_are_coefficient_balanced(self) -> None:
        for item in self.data["cycle_types"].values():
            for profile in item["profiles"]:
                self.assertEqual(
                    profile["coefficient_1_count"],
                    profile["coefficient_2_count"],
                )

    def test_enumeration_is_tiny(self) -> None:
        self.assertLessEqual(
            max(
                item["vectors_inspected"]
                for item in self.data["cycle_types"].values()
            ),
            243,
        )


if __name__ == "__main__":
    unittest.main()
