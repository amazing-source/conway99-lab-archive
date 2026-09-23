from __future__ import annotations

import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import independent_global_check as check  # noqa: E402


class GlobalReductionTests(unittest.TestCase):
    def test_pinned_inputs(self) -> None:
        self.assertTrue(check.authenticate_inputs()["all_match"])

    def test_q_profile_methods_and_exact_list(self) -> None:
        _, method_a = check.q_profiles_partition_method()
        method_b = check.q_profiles_histogram_method()
        self.assertEqual(method_a, method_b)
        expected = [
            (14, (2,) * 2 + (3,) * 12),
            (15, (2,) * 5 + (3,) * 10),
            (16, (2,) * 8 + (3,) * 8),
            (17, (2,) * 14 + (4,) * 3),
            (17, (2,) * 13 + (3,) * 2 + (4,) * 2),
            (17, (2,) * 12 + (3,) * 4 + (4,)),
            (17, (2,) * 11 + (3,) * 6),
            (18, (2,) * 16 + (4,) * 2),
            (18, (2,) * 15 + (3,) * 2 + (4,)),
            (18, (2,) * 14 + (3,) * 4),
            (19, (2,) * 18 + (4,)),
            (19, (2,) * 17 + (3,) * 2),
            (20, (2,) * 20),
        ]
        self.assertEqual(method_a, expected)

    def test_profile_mutations_are_rejected(self) -> None:
        _, profiles = check.q_profiles_partition_method()
        rows = check.profile_mutations(profiles)
        self.assertGreater(len(rows), len(profiles))
        self.assertTrue(all(row["rejected_by"] for row in rows))

    def test_dk_degree_three_obstruction(self) -> None:
        result = check.d_k_degree_three_obstruction()
        self.assertEqual(len(result["ordered_assignments_checked"]), 2)
        self.assertTrue(all(
            row["result"] == "REJECTED_BY_NO_BERGE_TRIANGLE"
            for row in result["ordered_assignments_checked"]
        ))

    def test_point_profile_methods(self) -> None:
        expected_counts = {
            (18, 27): 1,
            (19, 27): 3,
            (19, 28): 1,
            (20, 27): 11,
            (20, 28): 5,
            (20, 29): 2,
            (20, 30): 1,
        }
        for (r, m), expected_count in expected_counts.items():
            method_a = check.point_profiles_partition_method(r, m)
            method_b = check.point_profiles_histogram_method(r, m)
            self.assertEqual(method_a, method_b)
            self.assertEqual(len(method_a), expected_count)

    def test_crossing_methods(self) -> None:
        for left, right in (
            (0, 0), (1, 4), (2, 2), (2, 4), (3, 3), (3, 4), (4, 4), (6, 2)
        ):
            self.assertEqual(
                check.crossing_counts_bitmask(left, right),
                check.crossing_counts_formula(left, right),
            )
        self.assertEqual(check.crossing_counts_formula(3, 3), (0, 4, 6))

    def test_endpoint_harness(self) -> None:
        result = check.endpoint_semantic_harness()
        self.assertEqual(result["endpoint_swap_result"], "RETAINED_WITH_TRANSPOSED_CROSSING")
        self.assertGreaterEqual(len(result["hostile_mutations"]), 10)
        self.assertTrue(all(
            row["result"] == "REJECTED"
            for row in result["hostile_mutations"]
        ))

    def test_size_two_endpoint_table(self) -> None:
        rows = check.size_two_endpoint_table()
        by_pair = {tuple(row["q_pair"]): row for row in rows}
        self.assertEqual(by_pair[(2, 2)]["induced_degree_lower"], 6)
        self.assertFalse(by_pair[(2, 3)]["possible"])
        self.assertEqual(by_pair[(4, 4)]["induced_degree_lower"], 8)

    def test_graph_hostile_harness(self) -> None:
        result = check.graph_hostile_harness()
        self.assertEqual(result["K3,3_control"]["triangle_count"], 0)
        self.assertEqual(
            result["degree_preserving_2_switch"]["degree_only_result"]["triangle_count"],
            2,
        )
        self.assertEqual(
            result["disconnected_double_Petersen"]["component_count"], 2
        )
        self.assertEqual(
            result["disconnected_double_Petersen"]["result"], "RETAINED"
        )

    def test_spectral_boundary(self) -> None:
        result = check.spectral_replay()
        self.assertEqual(
            result["first_order_compatible_with_minimum_degree_6"], 27
        )
        rows = {row["m"]: row for row in result["rows_m_27_to_30"]}
        self.assertEqual(rows[27]["maximum_excess_T"], 0)
        self.assertEqual(rows[28]["maximum_excess_T"], 2)
        self.assertEqual(rows[29]["maximum_excess_T"], 6)
        self.assertEqual(rows[30]["maximum_excess_T"], 10)

    def test_outside_moment_toy(self) -> None:
        result = check.c5_outside_moment_toy()
        self.assertEqual(result["subsets_checked"], 32)
        self.assertTrue(result["all_direct_counts_match"])

    def test_integer_square_minimum_two_methods(self) -> None:
        for total, expected in ((226, 742), (228, 756), (234, 798)):
            formula, witness = check.balanced_min_square(70, total)
            dynamic = check.min_square_dp(70, total)
            self.assertEqual(formula, dynamic)
            self.assertEqual(formula, expected)
            self.assertEqual(sum(witness), total)

    def test_outside_histogram_mutations(self) -> None:
        result = check.outside_histogram_hostile_harness()
        self.assertEqual(
            result["target_impossible_row"]["unrestricted_integer_minimum_second"],
            742,
        )
        self.assertEqual(len(result["mutations"]), 3)
        collision = result["moment_collision_retained"]
        self.assertNotEqual(collision["histogram_a"], collision["histogram_b"])

    def test_exclusion_coverage(self) -> None:
        _, profiles = check.q_profiles_partition_method()
        points = {}
        for r, orders in {18: (27,), 19: (27, 28), 20: (27, 28, 29, 30)}.items():
            for m in orders:
                points[(r, m)] = check.point_profiles_partition_method(r, m)
        result = check.build_exclusions(profiles, points)
        self.assertEqual(result["coverage"]["admissible_q_profiles_through_r19"], 12)
        self.assertEqual(result["coverage"]["r20_m28_point_rows"], 5)
        self.assertEqual(result["coverage"]["r20_m29_point_rows"], 2)
        self.assertTrue(
            result["coverage"]["all_requested_cases_have_explicit_necessary_contradictions"]
        )

    def test_full_certificate_and_submitted_comparison(self) -> None:
        payload = check.build_certificate()
        self.assertEqual(payload["claim_label"], "DERIVED")
        self.assertTrue(
            payload["post_derivation_wave19_comparison"]["q_profile_set_exact_match"]
        )
        self.assertFalse(payload["status_boundary"]["self_promotion_to_VERIFIED"])

    def test_deterministic_json_replay(self) -> None:
        payload = check.build_certificate()
        first = check.canonical_json(payload)
        second = check.canonical_json(check.build_certificate())
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["q_profiles"]["admissible_count"], 13)


if __name__ == "__main__":
    unittest.main()
