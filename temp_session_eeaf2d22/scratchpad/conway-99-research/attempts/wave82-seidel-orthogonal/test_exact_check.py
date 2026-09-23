from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave82_exact_check", HERE / "exact_check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)
ROOT = HERE.parents[1]


class Wave82Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seidel, cls.wave66 = CHECK.load_imports(ROOT)
        cls.result = CHECK.build_result(cls.seidel, cls.wave66)

    def test_symbolic_square(self) -> None:
        self.assertEqual(
            CHECK.multiply_algebra((0, 7, 9), (0, 7, 9)),
            (3969, 0, 0),
        )

    def test_exact_equivalence_entry_map(self) -> None:
        self.assertEqual((7 + 2 - 9) // 18, 0)
        self.assertEqual((16 + 2) // 18, 1)
        self.assertEqual((-2 + 2) // 18, 0)
        self.assertEqual((63 + 2 * 99 - 9) // 18, 14)

    def test_all_smith_profiles(self) -> None:
        self.assertEqual(
            [p["rank_f7"] for p in self.result["smith_form"]["profiles"]],
            CHECK.SURVIVING_RANKS,
        )
        for rank in CHECK.SURVIVING_RANKS:
            factors = CHECK.smith_factors(rank)
            self.assertEqual(len(factors), 99)
            self.assertEqual(__import__("math").prod(factors), 63 ** 99)
            self.assertTrue(
                all(
                    factors[i] * factors[98 - i] == 3969
                    for i in range(99)
                )
            )

    def test_hostile_spectrum_rejected(self) -> None:
        hostile = copy.deepcopy(self.seidel)
        hostile["rational_spectra"]["seidel"]["7"] = 44
        with self.assertRaises(AssertionError):
            CHECK.build_result(hostile, self.wave66)

    def test_hostile_rank_list_rejected(self) -> None:
        hostile = copy.deepcopy(self.wave66)
        hostile["gauss_and_milgram"]["surviving_ranks"].append(44)
        with self.assertRaises(AssertionError):
            CHECK.build_result(self.seidel, hostile)

    def test_frozen_artifact(self) -> None:
        artifact = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(artifact, self.result)


if __name__ == "__main__":
    unittest.main()
