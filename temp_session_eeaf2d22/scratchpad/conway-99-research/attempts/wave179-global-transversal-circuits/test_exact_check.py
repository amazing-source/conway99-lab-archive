from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave179_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave179ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = MODULE.analyze()
        MODULE.verify(cls.data)

    def test_pair_partition(self) -> None:
        counts = self.data["pair_counts"]
        self.assertEqual(
            counts["edges"] + counts["nonedges"],
            counts["all_unordered_pairs"],
        )

    def test_multiplicity_cases(self) -> None:
        multiplicity = self.data["realizing_pair_multiplicity"]
        self.assertEqual(multiplicity["pairwise_intersecting_case_upper"], 3)
        self.assertEqual(multiplicity["disjoint_case_upper"], 2)

    def test_projective_count(self) -> None:
        self.assertEqual(
            self.data["edge_projective_circuit_lower_bound"], 693
        )
        self.assertEqual(
            self.data["additional_nonedge_projective_circuit_lower_bound"],
            1386,
        )
        self.assertEqual(self.data["projective_circuit_lower_bound"], 2079)

    def test_scalar_factor(self) -> None:
        self.assertEqual(
            self.data["dual_word_lower_bound"],
            self.data["ternary_nonzero_scalars_per_projective_class"]
            * self.data["projective_circuit_lower_bound"],
        )


if __name__ == "__main__":
    unittest.main()
