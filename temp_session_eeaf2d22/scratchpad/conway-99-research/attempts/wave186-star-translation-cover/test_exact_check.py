from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave186_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave186ExactCheckTests(unittest.TestCase):
    def test_multiplicity_two_translates(self) -> None:
        data = CHECK.multiplicity_two_translates()
        self.assertEqual(data["conic_weight"], 4)
        self.assertEqual(data["x_translate_profile"], [6, 2])
        self.assertEqual(data["y_translate_profile"], [2, 6])
        self.assertEqual(data["translate_weights"], [8, 8])
        self.assertEqual(data["translated_support_intersection"], 2)
        self.assertLess(
            data["translated_support_intersection"],
            data["dual_distance_floor"],
        )

    def test_multiplicity_three_leaf_translate(self) -> None:
        data = CHECK.multiplicity_three_translate()
        self.assertEqual(data["conic_weight"], 4)
        self.assertEqual(data["companion_weight"], 5)
        self.assertEqual(data["leaf_translate_profile"], [3, 6])
        self.assertEqual(data["leaf_translate_weight"], 9)
        self.assertFalse(data["contains_T"])
        self.assertEqual(data["companion_translate_intersection"], 0)

    def test_cover_bound(self) -> None:
        data = CHECK.cover_bound()
        self.assertEqual(data["nonedge_projective_lower"], 3696)
        self.assertEqual(data["total_projective_lower"], 4389)
        self.assertEqual(data["dual_short_word_lower"], 8778)

    def test_global_scope(self) -> None:
        data = CHECK.derive()
        self.assertTrue(data["former_equality_Q_2079_excluded"])
        self.assertEqual(data["conditional_status"], "DERIVED")
        self.assertEqual(data["global_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
