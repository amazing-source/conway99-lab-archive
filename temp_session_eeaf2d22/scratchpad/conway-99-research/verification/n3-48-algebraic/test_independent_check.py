"""Focused tests for the independent Wave 15 algebraic verifier."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave15_independent_check", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


class IndependentAlgebraicAuditTests(unittest.TestCase):
    def test_target_spectrum(self) -> None:
        self.assertEqual(audit.spectrum(), {14: 1, 3: 54, -4: 44})

    def test_exact_subset_bounds(self) -> None:
        self.assertEqual(audit.twice_induced_edge_upper(24), 136)
        self.assertEqual(audit.twice_induced_edge_lower(24), Fraction(96, 11))
        self.assertEqual(audit.required_order_for_average_degree(6), 27)

    def test_size_two_meeting_support_separation(self) -> None:
        self.assertEqual(audit.certify_active_degree(2), 6)
        self.assertEqual(audit.certify_active_degree(3), 6)

    def test_all_point_compositions_contradict_spectrum(self) -> None:
        rows = audit.active_point_cases()
        self.assertEqual(len(rows), 9)
        self.assertEqual(rows[0]["m"], 24)
        self.assertEqual(rows[0]["gap"], 4)
        self.assertEqual(rows[-1]["m"], 16)

    def test_triangle_moments(self) -> None:
        result = audit.triangle_intersection_moments()
        self.assertEqual(result["first_moment"], 216)
        self.assertEqual(result["second_moment"], 288)
        self.assertEqual(
            result["pair_counts"], {0: 2326, 1: 20742, 2: 48, 3: 1370}
        )

    def test_submitted_artifact(self) -> None:
        self.assertEqual(
            audit.validate_submitted_artifact(
                Path("attempts/wave15-algebraic/exact-checks.json")
            ),
            "40f5d81a71cc500c57e5f5858d11acde0afaf67d81233e68bf0794649e1a9ae8",
        )
        artifact = json.loads(
            Path("attempts/wave15-algebraic/exact-checks.json").read_text(
                encoding="utf-8"
            )
        )
        moments = artifact["triangle_intersection_failed_lane"][
            "fixed_triangle_moments"
        ]
        self.assertEqual(
            set(moments),
            {
                "consequence",
                "weighted_sum_i_a_i",
                "weighted_sum_i_squared_a_i",
            },
        )
        self.assertEqual(moments["weighted_sum_i_a_i"], 216)
        self.assertEqual(moments["weighted_sum_i_squared_a_i"], 288)
        self.assertNotIn("sum_i_a_i", moments)
        self.assertNotIn("sum_i_squared_a_i", moments)

    def test_hostile_mutations(self) -> None:
        results = audit.hostile_mutations()
        self.assertEqual(len(results), 7)
        self.assertEqual(set(results.values()), {"REJECTED"})


if __name__ == "__main__":
    unittest.main()
