from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave200_b", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave200TwoFaceAuditTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_face_specific_bounds(self) -> None:
        rows = MODULE.derive()["faces"]["rows"]
        self.assertEqual(rows["7037"]["budget"], 23)
        self.assertEqual(rows["7037"]["s_lower"], 57)
        self.assertEqual(rows["7037"]["s_upper"], 1)
        self.assertEqual(rows["7038"]["budget"], 63)
        self.assertEqual(rows["7038"]["s_lower"], 27)
        self.assertEqual(rows["7038"]["s_upper"], 4)

    def test_fiber_partition_and_distinctness(self) -> None:
        fiber = MODULE.derive()["fiber_partition"]
        self.assertEqual(fiber["pair_types"] * fiber["vertices_per_fiber"], 84)
        self.assertTrue(fiber["unique_type_per_leaf"])
        self.assertTrue(
            fiber["saturated_type"][
                "distinct_saturated_labels_have_distinct_types"
            ]
        )
        self.assertEqual(fiber["saturated_type"]["loss"], 4)

    def test_tight_additive_loss(self) -> None:
        for saturated in range(4):
            row = MODULE.tight_center_loss(saturated)
            self.assertEqual(row["delta_lower"], 3 * saturated)

    def test_deficient_additive_loss(self) -> None:
        for c in range(13):
            for saturated in range((3 * c) // 5 + 1):
                row = MODULE.deficient_center_loss(c, saturated)
                self.assertGreaterEqual(row["delta_lower"], 4 * saturated)

    def test_contradiction_and_consequence(self) -> None:
        result = MODULE.derive()
        self.assertEqual(
            result["contradictions"],
            {"7037": "57<=s<=1", "7038": "27<=s<=4"},
        )
        self.assertEqual(result["consequence"]["conditional_Q_lower_bound"], 7039)
        self.assertEqual(result["consequence"]["edge_added_projective"], 7732)
        self.assertEqual(result["consequence"]["scalar_words"], 15464)

    def test_stopping_point(self) -> None:
        stop = MODULE.derive()["stopping_point"]
        self.assertEqual(stop["budget"], 103)
        self.assertEqual(stop["coarse_four_s_lower"], -12)
        self.assertFalse(stop["excluded_by_this_mechanism"])


if __name__ == "__main__":
    unittest.main()
