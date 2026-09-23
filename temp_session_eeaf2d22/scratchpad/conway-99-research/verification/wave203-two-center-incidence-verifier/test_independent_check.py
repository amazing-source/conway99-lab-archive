from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave203_independent_check", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave203IndependentTests(unittest.TestCase):
    def test_two_five_slot_sets(self) -> None:
        result = CHECK.build_result()
        geometry = result["slot_geometry"]
        self.assertEqual(geometry["remaining_blocks_each_side"], 5)
        self.assertIn("same five", geometry["reverse_map"])

    def test_partial_third_block_injection(self) -> None:
        result = CHECK.build_result()
        geometry = result["slot_geometry"]
        self.assertIn("unique third", geometry["forward_partial_map"])
        self.assertIn("equal A_x sets", geometry["forward_injective_reason"])

    def test_reverse_matching_uses_cross_edge_count(self) -> None:
        reason = CHECK.build_result()["slot_geometry"]["matched_slot_reverse_reason"]
        self.assertIn("j(S,T)=2", reason)
        self.assertIn("third A_y(S)", reason)

    def test_global_relation_normalization_and_cancellation(self) -> None:
        relations = CHECK.flag_relation_vectors()
        self.assertEqual(relations["forward"], (1, 2, 2, 2, 0, 0))
        self.assertEqual(relations["reverse"], (2, 1, 0, 0, 2, 2))
        self.assertEqual(relations["combined"], (0, 0, 2, 2, 2, 2))

    def test_local_rescaling_guard(self) -> None:
        # Replacing only the reverse star coefficient by 1 destroys the
        # asserted all-equal cancellation; projective support is insufficient.
        forward = CHECK.flag_relation_vectors()["forward"]
        hostile_reverse = (2, 1, 0, 0, 1, 1)
        self.assertNotEqual(
            CHECK.add_mod(forward, hostile_reverse),
            (0, 0, 2, 2, 2, 2),
        )

    def test_four_columns_are_canonical_and_distinct(self) -> None:
        c4 = CHECK.build_result()["canonical_c4"]
        self.assertTrue(c4["four_columns_distinct"])
        self.assertIn("nonadjacent", c4["distinctness_reason"])

    def test_wave181_gram_rejects_all_equal(self) -> None:
        self.assertEqual(CHECK.rank_mod(CHECK.C4_GRAM), 3)
        self.assertEqual(
            CHECK.mat_vec_mod(CHECK.C4_GRAM, (1, 2, 2, 1)),
            (0, 0, 0, 0),
        )
        self.assertEqual(
            CHECK.mat_vec_mod(CHECK.C4_GRAM, (1, 1, 1, 1)),
            (1, 1, 1, 1),
        )

    def test_selected_label_capacity(self) -> None:
        control = CHECK.selected_label_capacity(7, [2, 3, 5])
        self.assertTrue(control["holds"])
        self.assertEqual(control["lhs"], control["total_incidence"] + 28)
        self.assertEqual(control["rhs"], 5 * control["label_union"])

    def test_bidirectional_epsilon_bound(self) -> None:
        control = CHECK.orientation_epsilon([[2, 3], [1, 1], [4]])
        self.assertEqual(control["bidirectional_labels"], 2)
        self.assertEqual(control["lower_bound"], 10)
        self.assertTrue(control["holds"])

    def test_b_zero_control_blocks_bound_promotion(self) -> None:
        result = CHECK.build_result()
        control = result["b_zero_control"]
        self.assertEqual(control["b"], 0)
        self.assertEqual(control["capacity_slack"], 708)
        self.assertEqual(control["epsilon"], 708)
        self.assertFalse(control["asserted_object"])
        self.assertFalse(result["counting_consequences"]["uniform_Q_ge_7060"])

    def test_scope(self) -> None:
        result = CHECK.build_result()
        self.assertFalse(result["conditional_scope"]["graph_or_flag_enumeration"])
        self.assertFalse(result["boundary"]["rank_11_excluded"])
        self.assertEqual(result["boundary"]["current_conditional_Q_lower"], 7059)


if __name__ == "__main__":
    unittest.main()
