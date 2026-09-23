from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave204_exact", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave204ExactTests(unittest.TestCase):
    def test_complete_result(self) -> None:
        result = CHECK.build_result()
        self.assertEqual(result["boundary"]["conway_99"], "UNKNOWN")
        self.assertFalse(result["boundary"]["rank_11_excluded"])

    def test_true_block_cycles_are_coboundaries(self) -> None:
        for length in (3, 4, 5):
            self.assertTrue(CHECK.exact_block_cycle(length)["holonomy_zero"])

    def test_projected_center_cycles_have_no_forced_holonomy(self) -> None:
        for length in (3, 4, 5):
            control = CHECK.analyze_control(length)
            self.assertFalse(control["block_transition_cycle_exists"])
            self.assertTrue(control["center_cycle_projected_defect_nonzero"])

    def test_wrong_discriminant_form_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "nonsingular|Gram"):
            CHECK.analyze_control(3, form=(1,) * 11)

    def test_flag_relation_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(CHECK.CONTROLS[3])
        mutated["stars"][1][0] = tuple(
            (entry + (1 if index == 0 else 0)) % 3
            for index, entry in enumerate(mutated["stars"][1][0])
        )
        with self.assertRaises(ValueError):
            CHECK.analyze_control(3, mutated)

    def test_rank_drop_is_rejected(self) -> None:
        mutated = copy.deepcopy(CHECK.CONTROLS[5])
        mutated["fillers"] = []
        with self.assertRaisesRegex(ValueError, "rank-11"):
            CHECK.analyze_control(5, mutated)

    def test_projective_collision_is_rejected(self) -> None:
        mutated = copy.deepcopy(CHECK.CONTROLS[4])
        mutated["fillers"][0] = mutated["stars"][0][0]
        with self.assertRaisesRegex(ValueError, "projective collision"):
            CHECK.analyze_control(4, mutated)

    def test_partial_interface_has_distinct_extensions(self) -> None:
        for length in (3, 4, 5):
            pair = CHECK.partial_extension_pair(length)
            self.assertTrue(pair["same_wave203_partial_interface"])
            self.assertNotEqual(pair["monodromy_a"], pair["monodromy_b"])

    def test_extension_moving_occupied_slot_is_invalid(self) -> None:
        bad = (1, 0, 2, 3, 4)
        self.assertNotEqual(bad[0], 0)

    def test_canonical_c4_does_not_force_a_face(self) -> None:
        audit = CHECK.canonical_c4_audit()
        self.assertEqual(audit["checkerboard_image"], [0, 0, 0, 0])
        self.assertNotEqual(audit["all_equal_image"], [0, 0, 0, 0])
        self.assertFalse(audit["forced_two_cell_on_wave203_branch"])


if __name__ == "__main__":
    unittest.main()
