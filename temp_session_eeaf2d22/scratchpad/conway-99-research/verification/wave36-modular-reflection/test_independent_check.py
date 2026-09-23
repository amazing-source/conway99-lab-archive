#!/usr/bin/env python3
"""Hostile tests for the independent Wave 36 modular verifier."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave36_modular_independent_check", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ModularReflectionIndependentTests(unittest.TestCase):
    def test_ternary_counts_both_determinant_classes(self) -> None:
        self.assertEqual(
            CHECK.ternary_count_table(),
            {
                "1": [0, 1],
                "2": [2, 1],
                "3": [6, 3],
                "4": [12, 15],
                "5": [36, 45],
                "6": [126, 117],
                "7": [378, 351],
            },
        )

    def test_projective_enumerator_has_one_representative_per_line(self) -> None:
        for dimension in range(1, 8):
            points = list(CHECK.canonical_projective_vectors(3, dimension))
            self.assertEqual(len(points), (3**dimension - 1) // 2)
            self.assertTrue(all(next(value for value in vector if value) == 1 for vector in points))

    def test_mod3_total_point_boundary(self) -> None:
        table = CHECK.ternary_count_table()
        self.assertLess(max(table["6"]), CHECK.N)
        self.assertGreaterEqual(min(table["7"]), CHECK.N)

    def test_mod3_orthogonal_companion_boundary_is_strict(self) -> None:
        result = CHECK.mod3_rank_floor()
        self.assertEqual(result["six_space_maximum"], 126)
        self.assertGreater(CHECK.ROW_ZERO_COUNT, result["six_space_maximum"])
        self.assertFalse(126 > result["six_space_maximum"])

    def test_mod3_projective_points_are_not_proportional(self) -> None:
        result = CHECK.row_proportionality_check()
        self.assertEqual(result["forced_combination_norm_squared"], 450)
        self.assertEqual(result["orthogonal_row_combination_norm_squared"], 882)
        self.assertNotEqual(450, 882)

    def test_mod7_cubic_all_entry_types_and_diagonal(self) -> None:
        result = CHECK.mod7_cubic_check()
        self.assertEqual(result["gram_identity"], "C^(o3)=4(I+C) mod 7")
        for values in result["entry_checks"].values():
            self.assertEqual(values["cube"], values["four_times_entry"])
        self.assertEqual(
            result["diagonal_check"]["cube"],
            result["diagonal_check"]["four_times_I_plus_C"],
        )

    def test_symmetric_cube_dimension_boundary(self) -> None:
        self.assertEqual(CHECK.symmetric_cube_dimension(10), math.comb(12, 3))
        self.assertEqual(CHECK.symmetric_cube_dimension(11), math.comb(13, 3))
        self.assertEqual(CHECK.symmetric_cube_dimension(10), 220)
        self.assertEqual(CHECK.symmetric_cube_dimension(11), 286)
        self.assertLess(220, CHECK.N)
        self.assertGreaterEqual(286, CHECK.N)

    def test_reciprocal_smith_pairing_both_order_cases(self) -> None:
        for r3, r7 in ((8, 12), (12, 8), (11, 11), (44, 44)):
            factors = CHECK.smith_factors(r3, r7)
            self.assertEqual(len(factors), CHECK.N)
            self.assertTrue(all(a <= b for a, b in zip(factors, factors[1:])))
            self.assertTrue(
                all(a * b == 441 for a, b in zip(factors, reversed(factors)))
            )
            self.assertEqual(factors[CHECK.N // 2], 21)
            self.assertNotIn(0, factors)

    def test_smith_determinant_and_modular_ranks(self) -> None:
        for r3, r7 in ((8, 12), (9, 11), (44, 44), (43, 43)):
            factors = CHECK.smith_factors(r3, r7)
            self.assertEqual(math.prod(factors), 21**CHECK.N)
            self.assertEqual(sum(value % 3 != 0 for value in factors), r3)
            self.assertEqual(sum(value % 7 != 0 for value in factors), r7)

    def test_parity_survivor_count_and_hostile_odd_pair(self) -> None:
        result = CHECK.smith_and_survivor_check()
        self.assertEqual(result["admissible_rank_pair_count"], 629)
        self.assertEqual(result["hostile_odd_pair"], [8, 11])
        self.assertEqual(result["hostile_odd_pair_h_mod_4"], 3)

    def test_final_status_is_scoped(self) -> None:
        result = CHECK.build_result()
        self.assertEqual(result["verdict"]["mod3_rank_floor"], "VERIFIED")
        self.assertEqual(result["verdict"]["mod7_rank_floor"], "VERIFIED")
        self.assertFalse(result["verdict"]["endpoint_excluded"])
        self.assertFalse(result["verdict"]["upper_bound_improved_below_4158"])
        self.assertEqual(result["verdict"]["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
