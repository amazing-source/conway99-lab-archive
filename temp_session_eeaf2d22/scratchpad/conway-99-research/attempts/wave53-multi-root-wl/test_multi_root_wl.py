from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("multi_root_wl.py")
SPEC = importlib.util.spec_from_file_location("wave53_multi_root_wl", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class MultiRootWLTests(unittest.TestCase):
    def test_geometry_orders_and_overlaps(self) -> None:
        expected_orders = {"K": 31, "B": 36, "C": 37, "D": 38}
        expected_overlap = {"K": 5, "B": 2, "C": 1, "D": 0}
        for relation in MODULE.RELATION_ORDER:
            geometry = MODULE.build_geometry(relation)
            self.assertEqual(len(geometry.triangle_nodes), expected_orders[relation])
            r_petals = {node for sector in geometry.sectors["R"] for node in sector}
            s_petals = {node for sector in geometry.sectors["S"] for node in sector}
            self.assertEqual(len(r_petals & s_petals), expected_overlap[relation])

    def test_b_common_edges_use_distinct_sectors(self) -> None:
        geometry = MODULE.build_geometry("B")
        for root in MODULE.LOCAL_ROOTS:
            locations = [
                sector_index
                for sector_index, sector in enumerate(geometry.sectors[root])
                for node in geometry.common_petals
                if node in sector
            ]
            self.assertEqual(len(set(locations)), 2)

    def test_hostile_duplicate_sector_entry_rejected(self) -> None:
        geometry = copy.deepcopy(MODULE.build_geometry("C"))
        geometry.sectors["R"][0][1] = geometry.sectors["R"][0][0]
        with self.assertRaises(AssertionError):
            MODULE.validate_geometry(geometry)

    def test_template_orders_and_shared_candidates(self) -> None:
        expected_orders = {"K": 319, "B": 323, "C": 325, "D": 326}
        for relation in MODULE.RELATION_ORDER:
            template = MODULE.build_template(relation)
            self.assertEqual(len(template.nodes), expected_orders[relation])
            shared = [
                key
                for key, contexts in template.candidate_contexts.items()
                if len(contexts) > 1
            ]
            self.assertEqual(len(shared), 1 if relation == "B" else 0)

    def test_b_shared_candidate_is_forced_true(self) -> None:
        template = MODULE.build_template("B")
        self.assertEqual(template.forced_true, {MODULE.pair_key("h0", "h1")})
        self.assertEqual(
            template.triangle_relations[MODULE.pair_key("h0", "h1")], "B"
        )

    def test_all_positive_controls(self) -> None:
        for relation in MODULE.RELATION_ORDER:
            template = MODULE.build_template(relation)
            control = MODULE.deterministic_control(template)
            MODULE.verify_control(template, control)

    def test_hostile_deleted_control_choice_rejected(self) -> None:
        template = MODULE.build_template("B")
        control = MODULE.deterministic_control(template)
        control["selected_candidate_labels"].pop()
        with self.assertRaises(AssertionError):
            MODULE.verify_control(template, control)

    def test_hostile_missing_forced_truth_rejected(self) -> None:
        template = MODULE.build_template("B")
        control = MODULE.deterministic_control(template)
        forced_label = MODULE.candidate_label(MODULE.pair_key("h0", "h1"))
        control["selected_candidate_labels"].remove(forced_label)
        with self.assertRaises(AssertionError):
            MODULE.verify_control(template, control)

    def test_small_exact_2wl_stability(self) -> None:
        tokens = [["d", "e"], ["e", "d"]]
        closure = MODULE.wl2(tokens)
        self.assertTrue(closure["stable_replay_passed"])
        self.assertTrue(closure["all_intersection_numbers_nonnegative_integers"])

    def test_small_exact_3wl_stability(self) -> None:
        tokens = [["d", "e"], ["e", "d"]]
        closure = MODULE.wl3(tokens)
        self.assertTrue(closure["stable_replay_passed"])
        self.assertEqual(closure["tuple_count"], 8)

    def test_nonsquare_wl_inputs_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.wl2([["d", "e"]])
        with self.assertRaises(ValueError):
            MODULE.wl3([["d", "e"]])


if __name__ == "__main__":
    unittest.main()
