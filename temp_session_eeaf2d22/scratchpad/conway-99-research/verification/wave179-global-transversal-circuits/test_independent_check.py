from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave179_independent", MODULE)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave179Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.analyze()

    def test_pair_partition(self) -> None:
        counts = self.result["pair_counts"]
        self.assertEqual(counts, {"edges": 693, "nonedges": 4158, "all_pairs": 4851})

    def test_intersecting_triangle_impossible(self) -> None:
        self.assertEqual(
            self.result["finite_logic"]["triangle_membership_solutions"], 0
        )

    def test_disjoint_logic(self) -> None:
        logic = self.result["finite_logic"]
        self.assertEqual(logic["alternating_square_colourings"], 2)
        self.assertTrue(logic["diagonal_repetition_rejected_by_lambda"])

    def test_multiplicities(self) -> None:
        self.assertEqual(
            self.result["multiplicity"],
            {"edge_circuit": 1, "nonedge_circuit_upper": 3, "disjoint_case": 2},
        )

    def test_projective_count(self) -> None:
        self.assertEqual(
            self.result["projective_classes"],
            {"edge": 693, "additional_nonedge": 1386, "total": 2079},
        )

    def test_scalar_factor(self) -> None:
        self.assertEqual(self.result["dual_word_lower"], 4158)

    def test_scope(self) -> None:
        self.assertIn("endpoint remains unknown", self.result["scope"])


if __name__ == "__main__":
    unittest.main()

