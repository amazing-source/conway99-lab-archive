from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave174_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave174ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = CHECK.analyze()
        CHECK.verify(cls.data)

    def test_only_eight_and_nine_survive_interlacing(self) -> None:
        self.assertEqual(self.data["psd_survivors"], [8, 9])

    def test_empty_cell_case_is_excluded_separately(self) -> None:
        self.assertEqual(
            self.data["c18_empty_cell_test"]["three_minus_adjacency_quadratic"],
            -1152,
        )

    def test_c8_fails_common_neighbor_convexity(self) -> None:
        test = self.data["c8_common_neighbor_test"]
        self.assertEqual((test["convex_lower"], test["srg_exact"]), (49, 48))

    def test_c9_is_forced_to_equality(self) -> None:
        test = self.data["c9_common_neighbor_test"]
        self.assertTrue(test["equality"])
        self.assertEqual(self.data["c9_color_sizes"], {"zero": 36, "one": 27, "two": 36})

    def test_z3_degrees_are_pointwise_forced(self) -> None:
        self.assertEqual(
            self.data["c9_forced_Z3_degrees"],
            {"U": 3, "Z0": 2, "O1": 1, "T2": 0, "Z3": 2},
        )

    def test_cycle_labels_have_period_three(self) -> None:
        self.assertTrue(self.data["cycle_label_period_three"])
        self.assertEqual(self.data["distinct_label_Z3_cycle_lengths"], [3])

    def test_endpoint_conclusion(self) -> None:
        self.assertEqual(self.data["forced_Z3_graph"], "3K3")
        self.assertEqual(
            self.data["conclusion"], "B1=B2=B3=0 for the endpoint centered-code dual"
        )


if __name__ == "__main__":
    unittest.main()
