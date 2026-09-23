from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave175_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave175ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = CHECK.analyze()
        CHECK.verify(cls.data)

    def test_polar_graph(self) -> None:
        self.assertEqual(
            self.data["polar_graph"]["eigenvalues"], [9_840, 80, -82]
        )

    def test_spectral_energies_survive(self) -> None:
        self.assertTrue(self.data["spectral_energies"]["both_positive"])

    def test_divisibility_refined_moment_survives(self) -> None:
        self.assertEqual(
            self.data["outside_singular_moments"]["evans_slack"], 1_008_018
        )

    def test_veronese_rank_caps(self) -> None:
        veronese = self.data["singular_veronese"]
        self.assertEqual(veronese["rank_F3_J_minus_I_minus_R_upper"], 65)
        self.assertEqual(veronese["rank_F3_I_plus_R_upper"], 66)

    def test_scope(self) -> None:
        self.assertEqual(
            self.data["conclusion"], "rank k=11 survives these exact polar tests"
        )


if __name__ == "__main__":
    unittest.main()
