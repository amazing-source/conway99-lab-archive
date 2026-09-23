from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave180_independent", MODULE)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave180Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.analyze()

    def test_j_profiles(self) -> None:
        self.assertEqual(
            self.result["profiles"]["3"],
            {"m0": 4, "m1": 0, "m2": 3, "projector_residue": 0},
        )

    def test_projector_filter(self) -> None:
        self.assertEqual(self.result["projector_admissible_t"], [0, 3])

    def test_t0_duplicate(self) -> None:
        self.assertEqual(self.result["t0"]["duplicate_weight"], 2)

    def test_companion_weights(self) -> None:
        self.assertEqual(self.result["t3"]["projective_weights"], [4, 5, 7, 8])
        self.assertEqual(self.result["t3"]["companion_weights"], [4, 5])

    def test_conic_gram(self) -> None:
        self.assertEqual(
            self.result["t3"]["switched_conic_gram"],
            [
                [0, 1, 1, 1],
                [1, 0, 1, 1],
                [1, 1, 0, 1],
                [1, 1, 1, 0],
            ],
        )

    def test_cover_count(self) -> None:
        self.assertEqual(self.result["cover"]["total_projective_lower"], 2772)
        self.assertEqual(self.result["cover"]["dual_word_lower"], 5544)

    def test_scope(self) -> None:
        self.assertIn("endpoint remains unknown", self.result["scope"])


if __name__ == "__main__":
    unittest.main()

