from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import rectangle_check as check  # noqa: E402


class RectangleIdentityTests(unittest.TestCase):
    def test_pinned_inputs(self) -> None:
        self.assertTrue(check.authenticate_inputs()["all_match"])

    def test_two_rank_implementations(self) -> None:
        matrices = [
            [],
            [[1, 0], [0, 1]],
            [[1, 1, 0], [0, 1, 1], [1, 0, 1]],
            [[1, 1, 1, 1], [1, 1, 1, 1]],
        ]
        for rows in matrices:
            columns = len(rows[0]) if rows else 0
            self.assertEqual(
                check.gf2_rank_dense(rows, columns),
                check.gf2_rank_bitsets(rows, columns),
            )

    def test_cycle_nullity_formula(self) -> None:
        for length in range(3, 31):
            matrix = check.adjacency_matrix(
                length,
                check.cycle_edges_from_order(list(range(length)), (length,)),
            )
            actual = length - check.checked_rank(matrix, length)
            self.assertEqual(actual, 1 if length % 2 else 2)

    def test_cycle_type_counts(self) -> None:
        census = check.cycle_type_census()
        self.assertEqual(census["all_cycle_length_multisets"], 331)
        self.assertEqual(
            census["necessary_nullity_threshold"]["counts_by_component_count"],
            {"1": 147, "2": 263, "3": 323},
        )
        self.assertEqual(
            census["if_some_F_component_is_nonbipartite"][
                "counts_by_component_count"
            ],
            {"1": 55, "2": 147, "3": 263},
        )

    def test_component_bound(self) -> None:
        result = check.component_bound()
        self.assertEqual(result["maximum_component_count"], 3)
        self.assertEqual(result["possible_component_orders"]["3"], [[6, 6, 8]])

    def test_incidence_rank_component_formula(self) -> None:
        connected = check.graph_audit(
            20, check.SCOUT_F_EDGES, degree=3, triangle_free=True
        )
        matrix = check.incidence_matrix(20, check.SCOUT_F_EDGES)
        self.assertEqual(check.checked_rank(matrix, 30), 20 - connected["component_count"])
        k33 = [(u, v) for u in range(3) for v in range(3, 6)]
        double = k33 + [(u + 6, v + 6) for u, v in k33]
        audit = check.graph_audit(12, double, degree=3, triangle_free=True)
        self.assertEqual(check.checked_rank(check.incidence_matrix(12, double), 18), 10)
        self.assertEqual(audit["component_count"], 2)

    def test_scout_F_is_connected_triangle_free_nonbipartite(self) -> None:
        audit = check.graph_audit(
            20, check.SCOUT_F_EDGES, degree=3, triangle_free=True
        )
        self.assertEqual(audit["component_count"], 1)
        self.assertEqual(audit["triangle_count"], 0)
        self.assertFalse(audit["bipartite"])

    def test_exact_rectangle_rejects_arbitrary_assignment(self) -> None:
        audit = check.rectangle_audit(
            check.SCOUT_F_EDGES, list(range(30)), (3,) * 10
        )
        self.assertFalse(audit["exact_rectangle_identity"])
        self.assertGreater(
            audit["diagonal_sum"] + audit["mod2_product_rank"], 0
        )

    def test_hostile_checks(self) -> None:
        result = check.hostile_checks()
        self.assertTrue(result["all_expected_outcomes_observed"])
        self.assertGreaterEqual(len(result["rows"]), 12)

    def test_certificate_without_scout(self) -> None:
        payload = check.build_certificate(include_scout=False)
        self.assertEqual(payload["claim_label"], "DERIVED")
        self.assertFalse(payload["status_boundary"]["self_promotion_to_VERIFIED"])
        self.assertEqual(payload["status_boundary"]["m30_residual"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
