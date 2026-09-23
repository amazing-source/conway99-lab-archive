from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave203_b", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave203TwoCenterTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_relation_addition(self) -> None:
        relation = MODULE.relation_addition()
        self.assertTrue(relation["four_common_columns_pairwise_distinct"])
        self.assertEqual(
            relation["global_column_normalization"],
            "same frozen z_R columns; each c4 leaf coefficient is 1",
        )
        self.assertEqual(
            relation["normalized_four_column_word"], [1, 1, 1, 1]
        )

    def test_all_equal_rejected(self) -> None:
        quad = MODULE.derive()["canonical_quadrilateral"]
        self.assertEqual(quad["rank_mod3"], 3)
        self.assertEqual(quad["all_equal_image"], [1, 1, 1, 1])
        self.assertFalse(quad["all_equal_is_relation"])
        self.assertEqual(quad["checkerboard_image"], [0, 0, 0, 0])

    def test_partial_not_total_map(self) -> None:
        geometry = MODULE.derive()["candidate_geometry"]
        self.assertEqual(geometry["opposite_candidate_slots"], 5)
        self.assertEqual(
            geometry["common_slot_identification"], "identity bijection"
        )
        self.assertEqual(geometry["third_block_map"], "injective partial map")
        self.assertFalse(geometry["surjective_on_all_five"])
        self.assertEqual(geometry["matched_reverse_third_block"], "T")
        self.assertTrue(geometry["matched_pair_involution"])

    def test_combined_capacity(self) -> None:
        capacity = MODULE.derive()["capacity"]
        self.assertEqual(capacity["combined_directional_flag_cap"], 5)
        self.assertEqual(capacity["global_both_oriented_row"], "epsilon>=5*b")

    def test_low_multiplicity_losses(self) -> None:
        self.assertEqual(MODULE.orientation_deficit(1, 1), 8)
        self.assertEqual(MODULE.orientation_deficit(1, 2), 7)
        self.assertEqual(MODULE.orientation_deficit(2, 2), 6)

    def test_boundary(self) -> None:
        boundary = MODULE.derive()["boundary"]
        self.assertEqual(boundary["matched_reverse_flag"], "REFUTED")
        self.assertFalse(boundary["extra_circuit_from_low_multiplicity"])
        self.assertFalse(boundary["endpoint_contradiction"])


if __name__ == "__main__":
    unittest.main()
