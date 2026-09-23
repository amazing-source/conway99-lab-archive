from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave181_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave181ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = MODULE.analyze()
        MODULE.verify(cls.data)

    def test_shared_center_projector_rejection(self) -> None:
        shared = self.data["shared_center_adjacent_third"]
        self.assertEqual(shared["pairing_profile"], [1, 2, 2, 1, 1, 1, 1])
        self.assertNotEqual(shared["singularity_residue"], 0)

    def test_canonical_involution_count(self) -> None:
        self.assertEqual(
            self.data["pair_counts"]["canonical_c4_orbits"],
            2079,
        )

    def test_checkerboard_kernel(self) -> None:
        self.assertEqual(self.data["canonical_c4_gram_rank"], 3)
        self.assertEqual(
            self.data["canonical_c4_projective_kernel"],
            [[1, 2, 2, 1]],
        )

    def test_switched_conic(self) -> None:
        self.assertEqual(
            self.data["switched_c4_gram_formula"],
            "2*(J_4-I_4)",
        )

    def test_incidence_double_count(self) -> None:
        incidences = self.data["incidences"]
        self.assertEqual(
            incidences["total_edge_c4"],
            incidences["total_c4_edges"],
        )
        self.assertEqual(incidences["c4_per_triangle_block"], 36)

    def test_equality_rank_target(self) -> None:
        equality = self.data["equality_boundary"]
        self.assertEqual(equality["signed_matrix_shape"], [2079, 231])
        self.assertEqual(equality["signed_matrix_rank_upper_if_equal"], 220)

    def test_projector_null_boundary(self) -> None:
        self.assertEqual(self.data["projector_sum_coefficient_mod3"], 0)


if __name__ == "__main__":
    unittest.main()
