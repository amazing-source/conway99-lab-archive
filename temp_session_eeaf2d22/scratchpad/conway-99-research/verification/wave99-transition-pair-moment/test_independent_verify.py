from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("independent_verify.py")
SPEC = importlib.util.spec_from_file_location(
    "wave99_independent_verify", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave99IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = VERIFY.independent_result()

    def test_rooted_sets_reconstructed(self) -> None:
        rooted = self.result["rooted_reconstruction"]
        self.assertEqual(rooted["seed_count"], 560)
        self.assertEqual(rooted["transition_candidates"], 840)
        self.assertEqual(rooted["selected_transitions"], 84)
        self.assertEqual(rooted["transition_seed_multiplicity_values"], [8])
        self.assertEqual(rooted["local_perfect_matching_count"], 6040)

    def test_lambda_triangle_guard(self) -> None:
        guard = self.result["coincidence_cap"]["lambda_triangle_guard"]
        self.assertEqual(guard["target_lambda"], 1)
        self.assertEqual(
            len(guard["common_neighbors_of_fixed_adjacent_pair"]), 2
        )
        self.assertFalse(guard["all_three_transitions_allowed_together"])

    def test_original_center_guard_is_essential(self) -> None:
        original = self.result["coincidence_cap"]["center_partition"][
            "other_two_original_centers"
        ]
        self.assertEqual(original["maximum_without_lambda_guard"], 16)
        self.assertEqual(original["maximum_with_lambda_guard"], 10)

    def test_all_centers_partitioned(self) -> None:
        cap = self.result["coincidence_cap"]
        self.assertTrue(cap["all_possible_centers_partitioned"])
        fourth = cap["center_partition"]["eight_fourth_points"]
        self.assertEqual(len(fourth["points"]), 8)
        self.assertEqual(fourth["sum_of_maxima"], 8)
        self.assertEqual(cap["per_transition_coincidence_cap"], 18)

    def test_pair_moment_multiplicity(self) -> None:
        moments = self.result["moment_certificate"]
        self.assertEqual(moments["first_moment_exact"], 672)
        self.assertEqual(
            moments["ordered_transition_pair_moment_upper"], 1512
        )
        self.assertEqual(moments["unordered_pair_moment_upper"], 756)
        self.assertEqual(moments["same_triple_pair_multiplicity"], 8)
        self.assertEqual(moments["four_point_union_pair_multiplicity"], 1)

    def test_pointwise_rational_certificate(self) -> None:
        moments = self.result["moment_certificate"]
        self.assertEqual(
            moments["pointwise_formula"],
            "1[j=0] <= 1 - j/2 + C(j,2)/6 for 0<=j<=4",
        )
        self.assertEqual(
            [row["certificate_right_side"] for row in moments[
                "pointwise_certificate"
            ]],
            ["1", "1/2", "1/6", "0", "0"],
        )
        self.assertEqual(moments["zero_transition_seed_upper_bound"], 350)

    def test_formal_extremal_distribution(self) -> None:
        control = self.result["moment_certificate"][
            "extremal_moment_distribution_control"
        ]
        self.assertEqual(control["sum_n"], 560)
        self.assertEqual(control["sum_j_n"], 672)
        self.assertEqual(control["sum_Cj2_n"], 756)

    def test_sign_and_root_factor(self) -> None:
        count = self.result["sign_and_root_conversion"]
        self.assertTrue(count["N14_counts_both_signs"])
        self.assertEqual(count["positive_roots_per_oriented_vector"], 7)
        self.assertEqual(
            count["antipodal_pair_rooted_positive_incidences"], 14
        )
        self.assertTrue(count["no_extra_factor_of_two"])
        self.assertEqual(count["N14_upper_bound"], 4950)

    def test_wave86_weighted_rearrangement(self) -> None:
        weighted = self.result["wave86_weighted_rearrangement"]
        self.assertEqual(weighted["weighted_lower_bound"], 2165002)
        self.assertEqual(
            weighted["conclusion"], "407*N16+43*N18>=2165002"
        )

    def test_scope_is_intersection_not_union(self) -> None:
        scope = self.result["scope"]
        self.assertTrue(scope["N14_bound_requires_prism_free_P0"])
        self.assertFalse(scope["N14_bound_requires_rank_28"])
        self.assertTrue(
            scope["weighted_Wave86_conclusion_requires_prism_free_P0"]
        )
        self.assertTrue(
            scope["weighted_Wave86_conclusion_requires_rank_28_q16"]
        )

    def test_hostile_wrong_n14_factor_rejected(self) -> None:
        count = self.result["sign_and_root_conversion"]
        wrong = 99 * count["rooted_positive_vector_upper_bound"] // 14
        self.assertNotEqual(wrong, count["N14_upper_bound"])

    def test_precomparison_status_not_promoted(self) -> None:
        self.assertEqual(
            self.result["claim_label"], "PENDING_DISCOVERY_COMPARISON"
        )


if __name__ == "__main__":
    unittest.main()
