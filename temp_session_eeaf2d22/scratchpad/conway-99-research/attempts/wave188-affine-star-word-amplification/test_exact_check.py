from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave188_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave188ExactCheckTests(unittest.TestCase):
    def test_affine_orbit_minimum(self) -> None:
        orbit = CHECK.orbit_profile_check()
        self.assertEqual(orbit["profiles_checked"], 438)
        self.assertEqual(orbit["minimum_short_orbit_words"], 3)
        self.assertEqual(orbit["minimum_equality_profiles"], 36)
        self.assertEqual(
            orbit["short_count_spectrum"],
            {"3": 36, "4": 140, "5": 226, "6": 36},
        )

    def test_type_two_profile(self) -> None:
        weights = CHECK.orbit_weights((5, 1, 1), (5, 1, 1))
        self.assertEqual(weights, [4, 8, 8, 8, 8, 12, 12, 12, 12])

    def test_triple_leaf_profile(self) -> None:
        weights = CHECK.orbit_weights((4, 0, 3), (6, 1, 0))
        self.assertEqual([weight for weight in weights if weight <= 9], [4, 5, 8, 9])

    def test_global_bound(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(result["global_inequality"]["coefficient_difference"], [0, -1, 0, 3, 0])
        self.assertEqual(result["bounds"]["nonedge_projective_short_words"], 8316)
        self.assertEqual(result["bounds"]["total_projective_short_words"], 9009)
        self.assertEqual(result["bounds"]["dual_scalar_short_words"], 18018)


if __name__ == "__main__":
    unittest.main()
