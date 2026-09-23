from __future__ import annotations

import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_check as check  # noqa: E402


class HigherOrderIndependentAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_result(
            HERE.parent.parent / "attempts" / "wave38-higher-order" / "exact-results.json"
        )

    def test_signed_trace_subtraction_is_exact(self) -> None:
        signed = self.result["signed_higher_order_counts"]
        self.assertEqual(signed["trace_S_fourth"], 3_722_796)
        self.assertEqual(signed["nonsimple_closed_signed_walks_length_four"], 2_120_580)
        self.assertEqual(signed["balanced_minus_unbalanced_support_four_cycles"], 200_277)
        self.assertEqual(signed["balanced_minus_unbalanced_support_triangles"], 34_034)

    def test_hostile_nonsimple_walk_double_count_is_rejected(self) -> None:
        # Omitting the overlap of the two backtracking classes double-counts
        # the alternating v0-v1-v0-v1-v0 walks and even loses divisibility by 8.
        wrong_non_simple = 2 * 231 * 68**2
        remainder = 3_722_796 - wrong_non_simple
        self.assertNotEqual(remainder % 8, 0)
        self.assertNotEqual(wrong_non_simple, 2_120_580)

    def test_balanced_sign_means_cycle_product_positive(self) -> None:
        positive = check.signed_four_cycle_control((1, -1, 1, -1))
        negative = check.signed_four_cycle_control((1, -1, 1, 1))
        self.assertEqual(positive["cycle_product"], 1)
        self.assertEqual(positive["simple_contribution"], 8)
        self.assertEqual(negative["cycle_product"], -1)
        self.assertEqual(negative["simple_contribution"], -8)

    def test_ternary_star_centering_scalars_and_rank_drop_scope(self) -> None:
        centered = self.result["ternary_centering"]
        self.assertEqual(centered["twice_MNt_mod_3"], [2, 2, 2])
        self.assertEqual(centered["w_norm_mod_3"], 2)
        self.assertEqual(centered["centered_row_norm_mod_3"], 0)
        self.assertEqual(centered["centered_row_inner_w_mod_3"], 0)
        self.assertEqual(centered["centered_gram_shift_mod_3"], 1)
        self.assertEqual(centered["seven_clique_centered_gram_rank_F3"], 6)
        self.assertEqual(centered["seven_clique_uncentered_gram_rank_F3"], 7)
        self.assertIn("centered", centered["wording_qualifier"])
        self.assertEqual(
            centered["rank_drop_lemma"]["conclusion"], "rank_F3(C+J)=r3-1"
        )

    def test_frozen_core_reconstruction_and_hash(self) -> None:
        core = self.result["frozen_local_positive_control"]
        self.assertEqual(core["vertices"], 36)
        self.assertEqual(core["edges"], 54)
        self.assertEqual(core["degree_set"], [3])
        self.assertTrue(core["connected"])
        self.assertTrue(core["triangle_free"])
        self.assertEqual(
            core["canonical_upper_triangle_bits_sha256"],
            "b5a5d573b5eb1beba106e5735d5f4e2f71c8b23b036e0e44a1014718f0570984",
        )
        self.assertEqual(
            core["pair_codegree_histogram"],
            {
                "cross_fibre_nonedge:0": 296,
                "cross_fibre_nonedge:1": 92,
                "cross_fibre_nonedge:2": 8,
                "edge:0": 54,
                "same_fibre_nonedge:0": 180,
            },
        )

    def test_local_19_triangle_rank_equality(self) -> None:
        bridge = self.result["frozen_local_positive_control"]["local_rank_bridge"]
        self.assertEqual(bridge["rank_P_minus_I_F3"], 10)
        self.assertEqual(bridge["rank_local_19_gram_F3"], 10)
        self.assertEqual(bridge["one_transpose_u_mod_3"], 0)
        self.assertTrue(bridge["L_u_equals_one"])
        self.assertIn("principal submatrix", bridge["global_scope"])

    def test_hostile_mutated_quotient_is_not_covered_by_rank_lemma(self) -> None:
        rows = check.reconstruct_core()
        quotient, _ = check.quotient_from_core(rows)
        neighbor = next(j for j, value in enumerate(quotient[0]) if value)
        quotient[0][neighbor] = 0
        quotient[neighbor][0] = 0
        with self.assertRaisesRegex(AssertionError, "four-regular"):
            check.local_rank_bridge(quotient)

    def test_required_BBt_exact_properties(self) -> None:
        gram = self.result["frozen_local_positive_control"]["required_BBt"]
        self.assertEqual(gram["entry_minimum"], 0)
        self.assertEqual(gram["diagonal_set"], [10])
        self.assertEqual(gram["row_sum_set"], [60])
        self.assertEqual(gram["rational_rank"], 34)
        self.assertTrue(gram["kernel_contains_two_fibre_differences"])
        self.assertTrue(gram["positive_semidefinite"])

    def test_individual_column_census_is_not_a_design(self) -> None:
        census = self.result["frozen_local_positive_control"]["individual_block_census"]
        self.assertEqual(census["raw_pair_triples"], 216_000)
        self.assertEqual(census["induced_matching_survivors"], 183_596)
        self.assertEqual(census["mixed_equation_survivors"], 152_399)
        self.assertEqual(
            census["mixed_survivors_by_internal_X_edges"],
            {"0": 52_517, "1": 76_540, "2": 22_610, "3": 732},
        )
        self.assertIn("individual", census["scope"])
        self.assertIn("no simultaneous", census["scope"])

    def test_no_local_to_global_or_status_inflation(self) -> None:
        conclusion = self.result["conclusion"]
        self.assertEqual(conclusion["simultaneous_60_column_B"], "UNKNOWN")
        self.assertEqual(conclusion["compatible_H"], "UNKNOWN")
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["rank_twelve_boundary_excluded"])
        self.assertFalse(conclusion["upper_bound_improved_below_4158"])
        self.assertEqual(conclusion["novelty_or_priority"], "UNKNOWN_NOT_AUDITED")
        self.assertEqual(conclusion["target_status"], "UNKNOWN")

    def test_submission_comparison_uses_data_only(self) -> None:
        comparison = self.result["submission_comparison"]
        self.assertEqual(comparison["mismatches"], {})
        self.assertIn("not imported or executed", comparison["method"])
        self.assertEqual(len(comparison["matched_fields"]), 8)


if __name__ == "__main__":
    unittest.main()
