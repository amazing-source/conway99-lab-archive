from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave183_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave183ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = MODULE.analyze()
        MODULE.verify(cls.data)

    def test_pair_capacity_excludes_nine_and_ten(self) -> None:
        rows = {row["multiplicity"]: row for row in self.data["support_rows"]}
        self.assertFalse(rows[9]["pair_bound_survives"])
        self.assertFalse(rows[10]["pair_bound_survives"])

    def test_pair_capacity_retains_eight_before_triangle_step(self) -> None:
        self.assertIn(8, self.data["pair_bound_survivors"])

    def test_cubic_triangle_lower_bound(self) -> None:
        cubic = self.data["cubic_case"]
        self.assertEqual(cubic["triangle_lower"], 3)
        self.assertEqual(cubic["vertex_disjoint_triangle_upper"], 2)
        self.assertTrue(cubic["contradiction"])

    def test_allowed_multiplicities(self) -> None:
        self.assertEqual(self.data["allowed_multiplicities"], [5, 6, 7])

    def test_support_shapes(self) -> None:
        self.assertEqual(
            self.data["support_shapes"],
            {"5": "5K1", "6": "3K2", "7": "C7"},
        )

    def test_root_count_interval(self) -> None:
        global_data = self.data["global"]
        self.assertEqual(global_data["distinct_root_lower"], 297)
        self.assertEqual(global_data["distinct_root_upper"], 415)

    def test_frame_coefficients(self) -> None:
        self.assertEqual(
            self.data["frame"]["coefficient_mod3"],
            {"5": 2, "6": 0, "7": 1},
        )


if __name__ == "__main__":
    unittest.main()

