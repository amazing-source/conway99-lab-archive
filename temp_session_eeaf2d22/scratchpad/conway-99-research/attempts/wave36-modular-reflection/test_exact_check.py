#!/usr/bin/env python3
"""Tests for the Wave 36 modular-reflection checker."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave36_modular_reflection", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class ModularReflectionTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        CHECK.verify_frozen_inputs()

    def test_endpoint_profile(self) -> None:
        self.assertEqual(
            CHECK.C_DIAGONAL + 2 * CHECK.C_PLUS - 2 * CHECK.C_MINUS,
            -21,
        )
        self.assertEqual(
            CHECK.C_DIAGONAL**2 + 4 * (CHECK.C_PLUS + CHECK.C_MINUS),
            441,
        )
        self.assertEqual(
            2 * CHECK.SCALE**2,
            882,
        )
        self.assertEqual(2 * 15**2, 450)
        self.assertNotEqual(882, 450)

    def test_ternary_counts_are_bruteforce_exact(self) -> None:
        self.assertEqual(
            CHECK.ternary_count_table(),
            {
                1: (0, 1),
                2: (2, 1),
                3: (6, 3),
                4: (12, 15),
                5: (36, 45),
                6: (126, 117),
                7: (378, 351),
            },
        )

    def test_ternary_rank_floor(self) -> None:
        self.assertEqual(CHECK.ternary_rank_lower_bound(), 8)
        # With only 126 orthogonal companions, the dimension-seven
        # obstruction would disappear; this is an active threshold.
        with self.assertRaises(AssertionError):
            CHECK.ternary_rank_lower_bound(orthogonal_companions=126)

    def test_mod7_cubic_identity_on_alphabet(self) -> None:
        residues = CHECK.mod7_cubic_residues()
        for value in (0, 2, -2):
            self.assertEqual(residues[value], 4 * value % 7)
        self.assertEqual(residues[1], 1)
        self.assertEqual(4 * (1 + 1) % 7, 1)

    def test_mod7_symmetric_cube_floor(self) -> None:
        self.assertEqual(CHECK.symmetric_cube_dimension(10), 220)
        self.assertEqual(CHECK.symmetric_cube_dimension(11), 286)
        self.assertEqual(CHECK.mod7_rank_lower_bound(), 11)
        self.assertEqual(CHECK.mod7_rank_lower_bound(point_count=220), 10)

    def test_smith_pairing_and_counts(self) -> None:
        factors = CHECK.smith_factors(8, 12)
        self.assertEqual(len(factors), 231)
        self.assertEqual(
            CHECK.smith_factor_counts(8, 12),
            {"1": 8, "3": 4, "21": 207, "147": 4, "441": 8},
        )
        self.assertTrue(
            all(
                factors[i] * factors[-1 - i] == 441
                for i in range(231)
            )
        )

    def test_smith_opposite_order(self) -> None:
        self.assertEqual(
            CHECK.smith_factor_counts(12, 8),
            {"1": 8, "7": 4, "21": 207, "63": 4, "441": 8},
        )
        self.assertEqual(
            CHECK.smith_factor_counts(44, 44),
            {"1": 44, "21": 143, "441": 44},
        )

    def test_rank_pair_census(self) -> None:
        pairs = CHECK.admissible_rank_pairs()
        self.assertEqual(len(pairs), 629)
        self.assertIn((8, 12), pairs)
        self.assertIn((9, 11), pairs)
        self.assertIn((44, 44), pairs)
        self.assertNotIn((8, 11), pairs)
        self.assertNotIn((7, 11), pairs)
        self.assertNotIn((8, 10), pairs)

    def test_index_bounds_and_parity(self) -> None:
        floor = CHECK.index_data(8, 11)
        self.assertEqual(floor["v3_h"], 36)
        self.assertEqual(floor["v7_h"], 33)
        self.assertEqual(floor["h_mod_4"], 3)
        allowed = CHECK.index_data(8, 12)
        self.assertEqual(allowed["h_mod_4"], 1)

    def test_result_status_wall(self) -> None:
        result = CHECK.build_results()
        self.assertFalse(result["conclusion"]["endpoint_excluded"])
        self.assertFalse(result["conclusion"]["upper_bound_improved_below_4158"])
        self.assertEqual(result["conclusion"]["target_status"], "UNKNOWN")
        self.assertEqual(
            result["combined_index_reduction"]["admissible_rank_pair_count"],
            629,
        )


if __name__ == "__main__":
    unittest.main()
