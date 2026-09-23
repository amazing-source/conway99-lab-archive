#!/usr/bin/env python3
"""Mutation-oriented tests for the Wave 12 proof-side reduction checker."""

from __future__ import annotations

import importlib.util
import unittest
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERIFIER_PATH = ROOT / "n3-42-equality" / "verify_reduction.py"
SPEC = importlib.util.spec_from_file_location("n3_42_reduction_verifier", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load the n3=42 reduction verifier")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class N342ReductionVerifierTests(unittest.TestCase):
    def test_committed_checker_passes_with_explicit_boundary(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(VERIFIER.main([]), 0)
        rendered = output.getvalue()
        self.assertIn("PASS conditional n3=42 proof-side reduction", rendered)
        self.assertIn(
            "proof_side_terminal_state all_size_two_exact_H_support_frontier",
            rendered,
        )
        self.assertIn("external_support_exclusion_checked_here false", rendered)
        self.assertIn("conditional_global_n3_lower_bound 45", rendered)
        self.assertIn("conditional_global_induced_C6_lower_bound 209331", rendered)
        self.assertIn("target_result UNKNOWN", rendered)

    def test_all_six_raw_profiles_and_degrees(self) -> None:
        profiles = VERIFIER.active_q_sequences(42)
        self.assertEqual(
            profiles,
            (
                (2,) * 14,
                (2,) * 12 + (4,),
                (2,) * 11 + (3, 3),
                (2,) * 8 + (3,) * 4,
                (2,) * 5 + (3,) * 6,
                (2,) * 2 + (3,) * 8,
            ),
        )
        self.assertEqual(
            tuple(Counter(VERIFIER.k_degree_profile(profile)) for profile in profiles),
            (
                Counter({7: 14}),
                Counter({6: 12, 0: 1}),
                Counter({6: 11, 3: 2}),
                Counter({5: 8, 2: 4}),
                Counter({4: 5, 1: 6}),
                Counter({3: 2, 0: 8}),
            ),
        )
        with self.assertRaises(ValueError):
            VERIFIER.active_q_sequences(1)

    def test_degree_filter_and_degree_three_obstruction(self) -> None:
        profiles = VERIFIER.active_q_sequences(42)
        self.assertEqual(
            VERIFIER.degree_filtered_profiles(profiles),
            ((2,) * 14, (2,) * 11 + (3, 3)),
        )
        witness = VERIFIER.degree_three_obstruction_witness()
        self.assertEqual(witness["k_degree"], 3)
        self.assertEqual(len(witness["forced_neighbor_points"]), 3)
        self.assertTrue(witness["common_point_contradiction"])

        missing_complement = VERIFIER.PROOF_PREMISES - {
            VERIFIER.COMPLEMENT_PREMISE
        }
        with self.assertRaises(ValueError):
            VERIFIER.degree_three_obstruction_witness(missing_complement)

    def test_crossing_masks_guard_singletons_and_two_by_two_blocks(self) -> None:
        for other_order in (1, 2, 3):
            self.assertEqual(
                VERIFIER.crossing_edge_counts(1, other_order),
                frozenset((0,)),
            )
        self.assertEqual(
            VERIFIER.crossing_edge_counts(2, 2),
            frozenset((0, 4)),
        )
        with self.assertRaises(ValueError):
            VERIFIER.crossing_masks(-1, 2)

    def test_size_four_flower_counts_at_orders_thirteen_and_fourteen(self) -> None:
        order13 = VERIFIER.size_four_flower_statistics(13)
        order14 = VERIFIER.size_four_flower_statistics(14)
        self.assertEqual(order13["total_profiles"], 6561)
        self.assertEqual(order13["feasible_profiles"], 9)
        self.assertEqual(order13["capacity_rejections"], 6552)
        self.assertEqual(order13["singleton_petal_histogram"], {7: 8, 8: 1})
        self.assertEqual(order13["type_224_histogram"], {3: 8, 4: 1})
        self.assertEqual(order13["minimum_root_degree"], 10)

        self.assertEqual(order14["total_profiles"], 6561)
        self.assertEqual(order14["feasible_profiles"], 45)
        self.assertEqual(order14["capacity_rejections"], 6516)
        self.assertEqual(
            order14["singleton_petal_histogram"],
            {6: 28, 7: 16, 8: 1},
        )
        self.assertEqual(order14["type_224_histogram"], {2: 24, 3: 20, 4: 1})
        self.assertEqual(order14["minimum_root_degree"], 9)
        self.assertGreater(order14["minimum_root_degree"], VERIFIER.K_DEGREE)

        missing_crossing = VERIFIER.PROOF_PREMISES - {
            VERIFIER.CROSSING_PREMISE
        }
        with self.assertRaises(ValueError):
            VERIFIER.size_four_flower_statistics(14, missing_crossing)

    def test_t_triples_and_u_degree_coefficient_mutation(self) -> None:
        self.assertEqual(
            VERIFIER.admissible_size_three_t_triples(),
            ((2, 2, 2), (2, 3, 3)),
        )
        mutated = VERIFIER.admissible_size_three_t_triples(14, 5)
        self.assertIn((1, 1, 1), mutated)
        self.assertIn((2, 2, 3), mutated)
        with self.assertRaises(AssertionError):
            VERIFIER.audit_reduction(
                VERIFIER.ReductionConfig(u_base_degree=5)
            )

    def test_233_t_profile_fixed_point_arithmetic_and_mutation(self) -> None:
        witness = VERIFIER.t_profile_233_exclusion_witness()
        self.assertEqual(witness["t_profile"], (2, 3, 3))
        self.assertEqual(witness["u_degrees"], (2, 1, 1))
        self.assertEqual(witness["co_points_by_occurrence"], (1, 2, 2))
        self.assertEqual(witness["distinct_co_points"], 5)
        self.assertEqual(witness["forced_h_contribution"], 20)
        self.assertEqual(witness["fixed_point_total"], 12)
        self.assertTrue(witness["contradiction"])

        unsupported = VERIFIER.t_profile_233_exclusion_witness(7)
        self.assertEqual(unsupported["fixed_point_total"], 21)
        self.assertFalse(unsupported["contradiction"])
        with self.assertRaises(AssertionError):
            VERIFIER.audit_reduction(
                VERIFIER.ReductionConfig(fixed_point_coefficient=7)
            )

    def test_cubic_r_order_restriction_and_k33_classification(self) -> None:
        self.assertEqual(VERIFIER.candidate_cubic_r_orders(14), (4, 6))
        statistics = VERIFIER.cubic_r_statistics()
        self.assertEqual(statistics["labeled_cubic_order_4"], 1)
        self.assertEqual(statistics["triangle_free_cubic_order_4"], 0)
        self.assertEqual(statistics["labeled_cubic_order_6"], 70)
        self.assertEqual(statistics["triangle_free_cubic_order_6"], 10)
        self.assertTrue(statistics["all_triangle_free_order_6_are_k33"])
        self.assertEqual(statistics["k33_edge_labels"], 9)
        self.assertEqual(statistics["available_t0_labels"], 5)
        self.assertFalse(statistics["injection_possible"])

    def test_k33_line_graph_has_no_open_twins(self) -> None:
        cubic_six = VERIFIER.cubic_graphs(6)
        triangle_free = tuple(
            graph
            for graph in cubic_six
            if not VERIFIER.contains_triangle(graph, 6)
        )
        self.assertEqual(len(triangle_free), 10)
        for graph in triangle_free:
            self.assertTrue(VERIFIER.is_k33(graph))
            neighborhoods = VERIFIER.line_graph_open_neighborhoods(graph)
            self.assertEqual(len(neighborhoods), 9)
            self.assertFalse(VERIFIER.has_open_twins(neighborhoods))

        self.assertTrue(
            VERIFIER.has_open_twins(
                (frozenset((1,)), frozenset((1,)))
            )
        )

    def test_proof_side_frontier_does_not_self_exclude(self) -> None:
        frontier = VERIFIER.all_size_two_frontier()
        self.assertEqual(frontier["active_order"], 14)
        self.assertEqual(frontier["point_count"], 21)
        self.assertEqual(frontier["F_degree"], 3)
        self.assertEqual(frontier["U_degree"], 4)
        self.assertEqual(frontier["L_degree"], 6)
        self.assertFalse(frontier["excluded_by_this_checker"])

    def test_external_support_premise_is_mandatory_for_bound_45(self) -> None:
        missing_external = VERIFIER.INTEGRATION_PREMISES - {
            VERIFIER.EXTERNAL_SUPPORT_EXCLUSION_PREMISE
        }
        with self.assertRaises(ValueError):
            VERIFIER.strengthened_bounds(missing_external)
        missing_complement = VERIFIER.INTEGRATION_PREMISES - {
            VERIFIER.COMPLEMENT_PREMISE
        }
        with self.assertRaises(ValueError):
            VERIFIER.strengthened_bounds(missing_complement)

        bounds = VERIFIER.strengthened_bounds()
        self.assertFalse(bounds["external_support_exclusion_checked_here"])
        self.assertEqual(
            bounds["external_support_exclusion_premise"],
            VERIFIER.EXTERNAL_SUPPORT_EXCLUSION_PREMISE,
        )
        self.assertEqual(bounds["global_n3_lower_bound"], 45)
        self.assertEqual(bounds["global_induced_C6_lower_bound"], 209331)
        self.assertEqual(bounds["target_result"], "UNKNOWN")

    def test_strengthened_branch_bounds(self) -> None:
        bounds = VERIFIER.strengthened_bounds()
        self.assertEqual(
            bounds["branch_n3_bounds"],
            (45, 45, 45, 48, 48, 45, 45, 48, 45, 48, 45, 48),
        )
        self.assertEqual(
            tuple(
                max(45, VERIFIER.ceil_multiple_of_three(4 * degree))
                for degree in VERIFIER.WAVE6_BRANCH_DEGREES
            ),
            bounds["branch_n3_bounds"],
        )
        self.assertNotEqual(
            tuple(
                max(42, VERIFIER.ceil_multiple_of_three(4 * degree))
                for degree in VERIFIER.WAVE6_BRANCH_DEGREES
            ),
            bounds["branch_n3_bounds"],
        )

    def test_cli_and_parameter_guards(self) -> None:
        with self.assertRaises(ValueError):
            VERIFIER.main(["unexpected"])
        with self.assertRaises(ValueError):
            VERIFIER.cubic_graphs(8)
        with self.assertRaises(ValueError):
            VERIFIER.ceil_multiple_of_three(-1)
        with self.assertRaises(AssertionError):
            VERIFIER.audit_reduction(
                VERIFIER.ReductionConfig(active_order=15)
            )


if __name__ == "__main__":
    unittest.main()
