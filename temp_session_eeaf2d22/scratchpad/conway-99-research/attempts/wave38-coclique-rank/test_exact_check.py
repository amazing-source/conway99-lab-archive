#!/usr/bin/env python3
"""Tests for the Wave 38 coclique-rank discovery calculation."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave38_coclique_rank", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class CocliqueRankTests(unittest.TestCase):
    def test_eleven_matching_union_normal_forms(self) -> None:
        partitions = tuple(CHECK.integer_partitions(6))
        self.assertEqual(len(partitions), 11)
        self.assertEqual(partitions[0], (1, 1, 1, 1, 1, 1))
        self.assertEqual(partitions[-1], (6,))

    def test_every_local_normal_form_has_twelve_coclique_points(self) -> None:
        for partition in CHECK.integer_partitions(6):
            adjacency = CHECK.local_cycle_graph(partition)
            chosen = CHECK.bipartition(adjacency)
            self.assertEqual(len(chosen), 12)

    def test_endpoint_normal_forms_are_the_four_without_part_one(self) -> None:
        endpoint = tuple(
            partition
            for partition in CHECK.integer_partitions(6)
            if min(partition) >= 2
        )
        self.assertEqual(endpoint, ((2, 2, 2), (2, 4), (3, 3), (6,)))

    def test_projector_polynomial_on_three_adjacency_eigenspaces(self) -> None:
        # 63F = 27I-9A+J is 0 on the 14 and 3 eigenspaces and 63 on -4.
        self.assertEqual(27 - 9 * 14 + 99, 0)
        self.assertEqual(27 - 9 * 3, 0)
        self.assertEqual(27 - 9 * (-4), 63)

    def test_coclique_gram_entries(self) -> None:
        gram = CHECK.coclique_gram(13)
        self.assertTrue(all(gram[index][index] == 28 for index in range(13)))
        self.assertTrue(
            all(
                gram[left][right] == 1
                for left in range(13)
                for right in range(13)
                if left != right
            )
        )

    def test_coclique_gram_has_full_rank_modulo_seven(self) -> None:
        self.assertEqual(CHECK.rank_mod_prime(CHECK.coclique_gram(13), 7), 13)

    def test_determinant_formula_and_residue(self) -> None:
        determinant = 27**12 * 40
        self.assertEqual(determinant % 7, 5)
        self.assertNotEqual(determinant % 7, 0)

    def test_public_record_is_conservative(self) -> None:
        result = CHECK.exact_record()
        self.assertEqual(result["claim_label"], "CANDIDATE")
        self.assertEqual(result["result"]["rank_F7_M_lower_bound"], 13)
        self.assertIn(
            "does not exclude n3=4158",
            " ".join(result["limitations"]),
        )


if __name__ == "__main__":
    unittest.main()
