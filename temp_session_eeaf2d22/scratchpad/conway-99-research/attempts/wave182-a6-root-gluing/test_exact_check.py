from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave182_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave182ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = MODULE.analyze()
        MODULE.verify(cls.data)

    def test_local_root_multiplicity(self) -> None:
        local = self.data["local"]
        self.assertEqual(local["projective_difference_roots"], 21)
        self.assertEqual(local["nonedges_per_local_root"], 4)

    def test_support_bounds(self) -> None:
        global_data = self.data["global"]
        self.assertEqual(global_data["support_size_lower"], 5)
        self.assertEqual(global_data["support_size_upper"], 10)

    def test_second_moment(self) -> None:
        global_data = self.data["global"]
        self.assertEqual(global_data["pair_intersection_sum_upper"], 8316)
        self.assertEqual(global_data["multiplicity_square_sum_upper"], 18711)

    def test_root_count_interval(self) -> None:
        global_data = self.data["global"]
        self.assertEqual(global_data["distinct_root_lower"], 231)
        self.assertEqual(global_data["distinct_root_upper"], 415)

    def test_opposite_roots_orthogonal(self) -> None:
        c4 = self.data["canonical_c4_root_pair"]
        self.assertEqual(c4["norm"], 1)
        self.assertTrue(c4["orthogonal"])

    def test_extremal_design_spectrum(self) -> None:
        extremal = self.data["extremal_231_root_design"]
        self.assertEqual(extremal["multiplicity"], 9)
        self.assertEqual(extremal["incidence_real_rank"], 55)

    def test_extremal_frame_null(self) -> None:
        self.assertEqual(
            self.data["extremal_231_root_design"]["frame_coefficient_mod3"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
