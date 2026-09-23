from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave181_independent", MODULE)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave181Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.analyze()

    def test_baseline_profile(self) -> None:
        self.assertEqual(
            self.result["shared_center"]["profile"], [1, 2, 2, 1, 1, 1, 1]
        )

    def test_projector_rejection(self) -> None:
        self.assertEqual(self.result["shared_center"]["square_sum_mod3"], 1)

    def test_involution(self) -> None:
        self.assertEqual(
            self.result["canonical_nonedge_involution"]["orbits"], 2079
        )

    def test_checkerboard(self) -> None:
        self.assertEqual(self.result["c4"]["projective_kernel"], [[1, 2, 2, 1]])

    def test_equality(self) -> None:
        self.assertEqual(self.result["equality"]["required_conics"], 2079)

    def test_signed_gram(self) -> None:
        self.assertEqual(
            self.result["signed_gram"]["integer_coefficients"],
            {"I": 36, "K": -4, "L": 1},
        )

    def test_projector_null(self) -> None:
        self.assertTrue(self.result["projector_sum"]["vanishes"])


if __name__ == "__main__":
    unittest.main()

