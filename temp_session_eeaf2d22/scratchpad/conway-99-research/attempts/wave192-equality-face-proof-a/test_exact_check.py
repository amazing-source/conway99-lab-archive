from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave192_proof_a", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave192ProofATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.derive()

    def test_equality_rows(self) -> None:
        for row in self.result["equality_face"]["sample_rows"]:
            self.assertEqual(row["I"], 2 * row["C"])
            self.assertEqual(row["B"], row["C"])
            self.assertEqual(row["Q"], 6237)

    def test_raw_pair_saturation(self) -> None:
        for row in self.result["equality_face"]["sample_rows"]:
            self.assertEqual(
                2 * row["exact2_raw_circuits"],
                row["type1_raw_assignments"],
            )

    def test_affine_axis_profiles(self) -> None:
        self.assertEqual(
            self.result["affine_conic"]["profiles"],
            [[6, 2], [6, 2]],
        )

    def test_affine_support_separation(self) -> None:
        affine = self.result["affine_conic"]
        self.assertFalse(affine["conic_contained_in_axis_one"])
        self.assertFalse(affine["conic_contained_in_axis_two"])
        self.assertFalse(affine["axes_same_support"])

    def test_strict_counts(self) -> None:
        counts = self.result["strict_bound"]
        self.assertEqual(counts["nonedge_projective_Q"], 6238)
        self.assertEqual(counts["edge_added_projective"], 6931)
        self.assertEqual(counts["circuit_scalar_words"], 13862)

    def test_scope(self) -> None:
        self.assertIn("no graph", self.result["search_scope"])
        self.assertIn("no graph", self.result["search_scope"].lower())


if __name__ == "__main__":
    unittest.main()
