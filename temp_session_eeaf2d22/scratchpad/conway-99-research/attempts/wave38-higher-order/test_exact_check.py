#!/usr/bin/env python3
"""Focused hostile tests for the Wave 38 higher-order discovery package."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave38_higher_order_exact_check",
    HERE / "exact_check.py",
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class HigherOrderTests(unittest.TestCase):
    def test_signed_four_cycle_subtraction(self) -> None:
        result = CHECK.signed_cycle_counts()
        self.assertEqual(
            result["balanced_minus_unbalanced_support_four_cycles"],
            200_277,
        )
        hostile = (
            CHECK.TRIANGLE_COUNT
            * CHECK.SUPPORT_DEGREE
            * (2 * CHECK.SUPPORT_DEGREE + 1)
        )
        self.assertNotEqual(
            (
                result["trace_S_fourth"] - hostile
            ) // 8,
            200_277,
        )

    def test_ternary_clique_sum_values(self) -> None:
        result = CHECK.ternary_centering()
        self.assertEqual(
            set(result["reduced_MNt_values"].values()),
            {2},
        )
        self.assertEqual(result["seven_clique_gram_rank"], 6)

    def test_rank_code_rejects_mutation(self) -> None:
        matrix = [[1, 0], [0, 1]]
        self.assertEqual(CHECK.rank_mod(matrix, 3), 2)
        matrix[1] = [2, 0]
        self.assertEqual(CHECK.rank_mod(matrix, 3), 1)

    def test_frozen_core_graph_axioms(self) -> None:
        adjacency = CHECK.core_adjacency()
        self.assertEqual(set(map(sum, adjacency)), {3})
        self.assertEqual(
            CHECK.connected_components(adjacency),
            [list(range(36))],
        )

    def test_prism_free_quotient_is_simple(self) -> None:
        quotient = CHECK.local_quotient(CHECK.core_adjacency())
        self.assertEqual(set(map(sum, quotient)), {4})
        self.assertEqual(
            set(entry for row in quotient for entry in row),
            {0, 1},
        )

    def test_local_rank_bridge(self) -> None:
        quotient = CHECK.local_quotient(CHECK.core_adjacency())
        shifted = [
            [
                (quotient[i][j] - int(i == j)) % 3
                for j in range(18)
            ]
            for i in range(18)
        ]
        local = CHECK.local_centered_gram(quotient)
        self.assertEqual(CHECK.rank_mod(shifted, 3), 10)
        self.assertEqual(CHECK.rank_mod(local, 3), 10)

    def test_required_block_gram(self) -> None:
        gram = CHECK.required_block_gram(CHECK.core_adjacency())
        self.assertGreaterEqual(min(map(min, gram)), 0)
        self.assertEqual(CHECK.rational_rank(gram), 34)
        self.assertEqual(set(map(sum, gram)), {60})

    def test_individual_block_census(self) -> None:
        census = CHECK.enumerate_individual_blocks(CHECK.core_adjacency())
        self.assertEqual(census["induced_matching_survivors"], 183_596)
        self.assertEqual(census["mixed_equation_survivors"], 152_399)

    def test_status_wall(self) -> None:
        conclusion = CHECK.build_results()["conclusion"]
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["upper_bound_improved_below_4158"])
        self.assertFalse(
            conclusion["local_rank_bridge_raises_verified_r3_floor"]
        )
        self.assertEqual(conclusion["target_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
