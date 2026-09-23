#!/usr/bin/env python3
"""Focused tests for the post-source, independent JSON replay."""

from __future__ import annotations

import copy
import unittest

import post_source_replay as replay


class PostSourceReplayTests(unittest.TestCase):
    def test_complete_replay(self) -> None:
        result = replay.run()
        self.assertEqual(result["v1"]["certificate_predicates"], "VERIFIED")
        self.assertEqual(result["v2"]["fixed_column_coboundary"], "VERIFIED")
        self.assertEqual(result["v3"]["local_fourth_order_detector"], "VERIFIED")

    def test_v1_slot_mutation_rejected(self) -> None:
        data = replay.load_json(replay.V1_DIR / "countermodel.json")
        data["centers"][0]["flags"][0]["leaves"][0]["wave203_slot"] = 6
        with self.assertRaises(AssertionError):
            replay.verify_v1_json(data)

    def test_v2_flag_equation_mutation_rejected(self) -> None:
        data = replay.load_json(replay.V2_DIR / "exact-results.json")
        data["projected_center_cycle_controls"]["3"]["stars"][1][0][0] += 1
        with self.assertRaises(AssertionError):
            replay.verify_v2_json(data)

    def test_v3_compression_mutation_rejected(self) -> None:
        data = replay.load_json(replay.V3_DIR / "exact-results.json")
        data["adjacent_pair_reduction"]["cycle_types"]["4+2"]["compression"][0][0] = 0
        with self.assertRaises(AssertionError):
            replay.verify_v3_json(data)

    def test_v3_status_mutation_rejected(self) -> None:
        data = replay.load_json(replay.V3_DIR / "exact-results.json")
        data = copy.deepcopy(data)
        data["conclusions"]["endpoint_excluded"] = True
        with self.assertRaises(AssertionError):
            replay.verify_v3_json(data)


if __name__ == "__main__":
    unittest.main(verbosity=2)

