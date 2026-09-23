from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave53_clean_verifier", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class IndependentWave53Tests(unittest.TestCase):
    def test_all_model_counts_and_merges(self) -> None:
        expected = {
            "K": (5, 31, 216, 0, 319),
            "B": (2, 36, 215, 1, 323),
            "C": (1, 37, 216, 0, 325),
            "D": (0, 38, 216, 0, 326),
        }
        for relation, values in expected.items():
            model = CHECKER.construct_model(relation)
            checks = CHECKER.validate_model(model)
            self.assertEqual(
                (
                    checks["common_K_neighbor_count"],
                    checks["triangle_core_order"],
                    checks["candidate_count"],
                    checks["shared_candidate_count"],
                    checks["expanded_order"],
                ),
                values,
            )

    def test_wrong_common_overlap_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            CHECKER.construct_geometry("K", overlap_override=4)

    def test_B_matching_and_graph_level_force(self) -> None:
        model = CHECKER.construct_model("B")
        key = CHECKER.unordered("joint_0", "joint_1")
        self.assertEqual(model.forced_true, {key})
        self.assertEqual(model.pair_relations[key], "B")
        self.assertEqual(len(model.contexts[key]), 2)

    def test_missing_B_force_rejected(self) -> None:
        model = CHECKER.construct_model("B")
        model.forced_true.clear()
        with self.assertRaises(AssertionError):
            CHECKER.validate_model(model)

    def test_all_local_positive_controls(self) -> None:
        for relation in CHECKER.RELATIONS:
            model = CHECKER.construct_model(relation)
            control = CHECKER.make_positive_control(model)
            selected = {
                CHECKER.unordered(
                    next(
                        internal
                        for internal, external in model.aliases.items()
                        if external == pair[0]
                    ),
                    next(
                        internal
                        for internal, external in model.aliases.items()
                        if external == pair[1]
                    ),
                )
                for pair in control["selected_external_pairs"]
            }
            CHECKER.verify_positive_control(model, selected)

    def test_deleted_control_edge_rejected(self) -> None:
        model = CHECKER.construct_model("B")
        control = CHECKER.make_positive_control(model)
        reverse_alias = {
            external: internal for internal, external in model.aliases.items()
        }
        selected = {
            CHECKER.unordered(reverse_alias[left], reverse_alias[right])
            for left, right in control["selected_external_pairs"]
        }
        selected.remove(next(iter(selected)))
        with self.assertRaises(AssertionError):
            CHECKER.verify_positive_control(model, selected)

    def test_missing_cap_rejected(self) -> None:
        model = CHECKER.construct_model("D")
        model.caps.pop(next(iter(model.caps)))
        with self.assertRaises(AssertionError):
            CHECKER.validate_model(model)

    def test_candidate_split_rejected(self) -> None:
        model = CHECKER.construct_model("B")
        key = CHECKER.unordered("joint_0", "joint_1")
        model.contexts[key] = model.contexts[key][:1]
        with self.assertRaises(AssertionError):
            CHECKER.validate_model(model)

    def test_small_WL_and_nonsquare_rejection(self) -> None:
        tokens = [[("d",), ("e",)], [("e",), ("d",)]]
        wl2 = CHECKER.exact_2wl(tokens)
        wl3 = CHECKER.exact_folklore_3wl(tokens)
        self.assertTrue(wl2["stable_replay_passed"])
        self.assertTrue(
            wl2["all_color_classes_have_constant_intersection_parameters"]
        )
        self.assertEqual(wl3["tuple_count"], 8)
        with self.assertRaises(ValueError):
            CHECKER.exact_2wl([[("x",), ("y",)]])
        with self.assertRaises(ValueError):
            CHECKER.exact_folklore_3wl([[("x",), ("y",)]])

    def test_partition_equivalence_rejects_split(self) -> None:
        self.assertTrue(CHECKER.same_partition([0, 0, 1], [7, 7, 9]))
        self.assertFalse(CHECKER.same_partition([0, 0, 1], [7, 8, 9]))

    def test_mutated_discovery_partition_hash_rejected(self) -> None:
        matrix = [[0, 1], [1, 0]]
        intersections = [[0, 0, 0, 1]]
        closure = {
            "pair_color_matrix": matrix,
            "intersection_numbers_nonzero": intersections,
            "partition_sha256": CHECKER.sha256_json(matrix),
            "intersection_tensor_sha256": CHECKER.sha256_json(intersections),
        }
        CHECKER.verify_discovery_wl2_hashes(closure)
        closure["partition_sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            CHECKER.verify_discovery_wl2_hashes(closure)

    def test_aliases_are_discovery_identity_compatible(self) -> None:
        for relation in CHECKER.RELATIONS:
            model = CHECKER.construct_model(relation)
            self.assertEqual(
                len(model.node_aliases), len(set(model.node_aliases.values()))
            )


if __name__ == "__main__":
    unittest.main()
