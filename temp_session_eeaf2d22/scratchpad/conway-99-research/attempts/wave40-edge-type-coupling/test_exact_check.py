#!/usr/bin/env python3
"""Hostile tests for the Wave 40 edge-type coupling discovery."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave40_edge_type", HERE / "exact_check.py")
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class EdgeTypeCouplingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = CHECK.exact_record()

    def test_frozen_counts(self) -> None:
        self.assertEqual(self.record["frozen_parameters"]["graph_edges"], 693)
        self.assertEqual(self.record["frozen_parameters"]["graph_triangles"], 231)
        self.assertEqual(self.record["frozen_parameters"]["graph_four_cycles"], 2079)
        self.assertEqual(self.record["frozen_parameters"]["J_edges"], 4158)

    def test_face_formula_all_222(self) -> None:
        special = self.record["global_edge_type_complex"]["all_222_specialization"]
        self.assertEqual(special["face_counts"]["length_4"], 2079)
        self.assertEqual(special["face_counts"]["boundary_sum"], 8316)
        self.assertEqual(special["euler_characteristic_range"], [-1848, -693])
        self.assertFalse(special["euler_route_is_contradictory"])

    def test_face_formula_rejects_wrong_total(self) -> None:
        with self.assertRaisesRegex(AssertionError, "total"):
            CHECK.face_counts({"222": 692, "24": 0, "33": 0, "6": 0})

    def test_all_222_rank_distribution(self) -> None:
        census = self.record["all_222_three_side_quotient_census"]
        self.assertEqual(census["normalized_labelled_case_count"], 4050)
        self.assertEqual(
            census["rank_F3_P_minus_I_distribution"],
            {"11": 8, "12": 1, "13": 400, "14": 46, "15": 2616, "16": 979},
        )
        self.assertEqual(census["rank_at_most_11_normalized_case_count"], 8)

    def test_all_low_cases_have_same_forced_profile(self) -> None:
        census = self.record["all_222_three_side_quotient_census"]
        self.assertEqual(census["rank_at_most_11_common_triangle_count_P"], 16)
        self.assertEqual(
            census["rank_at_most_11_common_component_profiles"],
            [[2, 2, 2], [4, 4, 4]],
        )
        for case in census["rank_at_most_11_cases"]:
            self.assertEqual(case["rank_F3_P_minus_I"], 11)
            self.assertEqual(case["relative_pairing_orbit"], "share_one_24")

    def test_positive_lift(self) -> None:
        control = self.record["one_triangle_positive_control"]
        self.assertEqual(control["quotient_side_types"], ["222", "222", "222"])
        self.assertEqual(control["quotient_rank_F3_P_minus_I"], 11)
        self.assertEqual(control["quotient_triangle_count"], 16)
        self.assertEqual(control["component_profiles"], [[4, 4, 4], [8, 8, 8]])
        self.assertEqual(control["triangle_count"], 0)
        self.assertEqual(control["required_BBt_rational_rank"], 33)

    def test_triangle_neighbor_rank_identity(self) -> None:
        result = self.record["triangle_neighbor_characteristic_seven_rank"]
        original = result["original_positive_lift"]
        self.assertEqual(
            original["transport_block_rank_F7"],
            1 + original["laplacian_rank_F7"],
        )
        self.assertIsNone(result["universal_rank_floor_from_this_lane"])

    def test_complete_pairing_census_for_one_quotient(self) -> None:
        census = self.record["triangle_neighbor_characteristic_seven_rank"][
            "one_quotient_complete_pairing_census"
        ]
        self.assertEqual(census["all_pairing_masks"], 2**18)
        self.assertEqual(census["triangle_free_pairing_masks"], 37_378)
        self.assertEqual(
            census["transport_rank_F7_distribution"],
            {"33": 264, "34": 7348, "35": 29766},
        )
        self.assertEqual(census["minimum_transport_rank_F7"], 33)
        witness = census["canonical_minimum_witness"]
        self.assertEqual(witness["pairing_mask_decimal"], 51_739)
        self.assertEqual(witness["transport_block_rank_F7"], 33)
        self.assertEqual(witness["laplacian_rank_F7"], 32)

    def test_quotient_does_not_fix_full_lift(self) -> None:
        quotient = CHECK.positive_quotient()
        first = CHECK.canonical_pairing_lift(quotient, 51_739)
        second = CHECK.canonical_pairing_lift(quotient, 63)
        self.assertEqual(CHECK.contract_lift(first), quotient)
        self.assertEqual(CHECK.contract_lift(second), quotient)
        first_rank = CHECK.triangle_neighbor_rank_identity(first)[
            "transport_block_rank_F7"
        ]
        second_rank = CHECK.triangle_neighbor_rank_identity(second)[
            "transport_block_rank_F7"
        ]
        self.assertNotEqual(first_rank, second_rank)

    def test_bad_orientation_bits_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "orientation"):
            CHECK.lift_quotient(CHECK.positive_quotient(), "0" * 35)

    def test_doubled_quotient_edge_rejected(self) -> None:
        quotient = CHECK.positive_quotient()
        bad = CHECK.lift_quotient(quotient, CHECK.POSITIVE_LIFT_BITS)
        bad[0][12] = bad[12][0] = 1
        bad[1][13] = bad[13][1] = 1
        with self.assertRaisesRegex(AssertionError, "doubled"):
            CHECK.contract_lift(bad)

    def test_status_is_conservative(self) -> None:
        conclusion = self.record["conclusion"]
        self.assertFalse(conclusion["new_general_upper_bound_on_n3"])
        self.assertFalse(conclusion["all_222_excluded"])
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["universal_39_block_rank_at_least_33_proved"])
        self.assertEqual(conclusion["target_status"], "UNKNOWN")

    def test_no_completed_graph_automorphism_assumption(self) -> None:
        limitations = " ".join(self.record["limitations"]).lower()
        self.assertIn("no automorphism or transitivity", limitations)

    def test_hostile_rank_mutation_detected(self) -> None:
        hostile = copy.deepcopy(self.record)
        hostile["all_222_three_side_quotient_census"][
            "rank_F3_P_minus_I_distribution"
        ]["11"] = 7
        self.assertNotEqual(CHECK.canonical_json(hostile), CHECK.canonical_json(self.record))

    def test_byte_exact_regeneration(self) -> None:
        expected = CHECK.canonical_json(self.record)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_bytes(expected)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), self.record)
            self.assertEqual(path.read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
