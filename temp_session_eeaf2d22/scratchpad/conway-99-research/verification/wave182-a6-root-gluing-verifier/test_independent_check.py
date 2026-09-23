from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave182_independent", MODULE)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave182Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.analyze()

    def test_local_counts(self) -> None:
        self.assertEqual(self.result["local"]["roots"], 21)
        self.assertEqual(self.result["local"]["nonedges_per_root"], 4)

    def test_support_bounds(self) -> None:
        self.assertEqual(
            (self.result["support"]["minimum"], self.result["support"]["maximum"]),
            (5, 10),
        )

    def test_edge_capacity(self) -> None:
        self.assertEqual(self.result["edge_projective_capacities"]["maximum"], 6)

    def test_second_moment(self) -> None:
        self.assertEqual(self.result["moments"]["square_sum_upper"], 18711)

    def test_root_interval(self) -> None:
        self.assertEqual(
            (self.result["moments"]["root_lower"], self.result["moments"]["root_upper"]),
            (231, 415),
        )

    def test_extremal_multiplicity(self) -> None:
        self.assertEqual(self.result["extremal"]["multiplicity"], 9)

    def test_extremal_spectrum(self) -> None:
        self.assertEqual(
            self.result["extremal"]["eigenvalues"], {"189": 1, "35": 54, "0": 44}
        )

    def test_no_status_inflation(self) -> None:
        self.assertFalse(self.result["extremal"]["contradiction"])


if __name__ == "__main__":
    unittest.main()

