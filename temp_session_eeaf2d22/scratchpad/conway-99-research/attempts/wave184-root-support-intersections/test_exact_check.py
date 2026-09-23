from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave184_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave184ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = MODULE.analyze()
        MODULE.verify(cls.data)

    def test_support_intersection_bound(self) -> None:
        self.assertEqual(self.data["support_intersection_upper"], 2)
        self.assertEqual(self.data["two_point_intersection_type"], "graph edge")

    def test_support_edge_counts(self) -> None:
        self.assertEqual(
            self.data["support_edge_counts"],
            {"5": 0, "6": 3, "7": 7},
        )

    def test_no_sub_twelve_residue(self) -> None:
        self.assertEqual(self.data["sub_twelve_residue_four_count"], 0)

    def test_arithmetic_sharpness(self) -> None:
        self.assertEqual(
            self.data["sharpness_distribution"],
            {"n5": 411, "n6": 4, "n7": 0},
        )
        self.assertEqual(self.data["sharpness_incidence_total"], 2079)

    def test_weight_four_floor(self) -> None:
        self.assertEqual(self.data["total_projective_weight4_lower"], 2091)
        self.assertEqual(self.data["dual_B4_lower"], 4182)


if __name__ == "__main__":
    unittest.main()

