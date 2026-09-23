#!/usr/bin/env python3
"""Tests for the Wave 41 multi-edge rank-packing discovery package."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

import exact_check as exact  # noqa: E402


class Wave41MultiedgeRankPackingTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        self.assertEqual(
            {path: exact.sha256_file(Path(path)) for path in exact.INPUTS},
            exact.INPUTS,
        )

    def test_matching_catalog(self) -> None:
        catalog = exact.matching_catalog()
        self.assertEqual(len(catalog), 11)
        self.assertEqual(sum(int(entry["count"]) for entry in catalog.values()), 10_395)
        self.assertEqual(set(catalog), set(exact.integer_partitions(6)))

    def test_eliminated_fibre_inverse(self) -> None:
        p_matrix = exact.permutation_matrix(exact.STANDARD_MATCHING)
        i_matrix = exact.identity(exact.SIDE)
        diagonal = exact.matrix_subtract(exact.scalar_multiply(3, i_matrix), p_matrix)
        claimed_inverse = exact.matrix_add(
            exact.scalar_multiply(3, i_matrix), p_matrix
        )
        self.assertEqual(
            exact.matrix_multiply(diagonal, claimed_inverse),
            i_matrix,
        )

    def test_rank_identity_for_all_types(self) -> None:
        for entry in exact.matching_catalog().values():
            q_matching = entry["representative"]
            self.assertIsInstance(q_matching, tuple)
            record = exact.full_block_rank_record(
                q_matching,
                exact.STANDARD_MATCHING,
                tuple(range(exact.SIDE)),
            )
            self.assertEqual(
                record["K39_rank_F7"],
                1 + record["laplacian_rank_F7"],
            )

    def test_all_odd_assignment_exhaustion(self) -> None:
        result = exact.all_odd_equality_obstruction()
        self.assertEqual(result["complete_assignment_checks"], 576)
        records = result["records"]
        self.assertEqual(
            set(records),
            {"1+1+1+1+1+1", "1+1+1+3", "1+5", "3+3"},
        )
        self.assertTrue(
            all(
                not record["rank_25_equality_possible"]
                for record in records.values()
            )
        )
        self.assertTrue(records["1+1+1+1+1+1"]["impossible_columns"])
        self.assertTrue(records["1+1+1+3"]["impossible_columns"])
        self.assertTrue(records["1+5"]["impossible_columns"])

    def test_three_plus_three_forced_target_is_not_matching(self) -> None:
        record = exact.all_odd_equality_obstruction()["records"]["3+3"]
        self.assertEqual(record["impossible_columns"], [])
        self.assertEqual(
            record["diagonal_isotropy_allowed_preimage_counts"],
            [1] * exact.SIDE,
        )
        self.assertFalse(record["forced_R_is_perfect_matching"])
        self.assertIn("2", record["forced_R_entry_histogram_F7"])
        self.assertIn("3", record["forced_R_entry_histogram_F7"])

    def test_structural_compact_kernel(self) -> None:
        result = exact.structural_compact_kernel_record()
        self.assertEqual(result["outside_column_check"]["integer_total"], 14)
        self.assertEqual(result["outside_column_check"]["residue_mod_7"], 0)
        self.assertEqual(len(result["block_checks"]), 11)
        self.assertTrue(
            all(
                record["kernel_vector_rank_F7"] == 3
                for record in result["block_checks"].values()
            )
        )

    def test_generic_low_rank_control(self) -> None:
        record = exact.low_rank_controls()["generic_three_fibre_control"]
        self.assertEqual(record["core_component_sizes"], [12, 12, 12])
        self.assertEqual(record["core_triangle_count"], 6)
        self.assertEqual(record["laplacian_nullity_F7"], 9)
        self.assertEqual(record["K39_rank_F7"], 28)

    def test_triangle_free_low_rank_control(self) -> None:
        record = exact.low_rank_controls()["triangle_free_three_fibre_control"]
        self.assertEqual(record["core_component_sizes"], [18, 18])
        self.assertEqual(record["core_triangle_count"], 0)
        self.assertEqual(record["laplacian_nullity_F7"], 8)
        self.assertEqual(record["K39_rank_F7"], 29)

    def test_status_wall(self) -> None:
        record = exact.exact_record()
        conclusion = record["conclusion"]
        self.assertEqual(record["claim_label"], "CANDIDATE")
        self.assertFalse(conclusion["new_universal_rank_floor_proved"])
        self.assertFalse(conclusion["new_endpoint_rank_floor_proved"])
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["new_general_upper_bound_on_n3"])
        self.assertEqual(conclusion["strongest_general_upper_bound_on_n3"], 4158)
        self.assertEqual(conclusion["conway_99_status"], "UNKNOWN")
        self.assertEqual(conclusion["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
