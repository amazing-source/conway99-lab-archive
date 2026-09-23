#!/usr/bin/env python3
"""Focused tests for the Wave 39 cross-base ternary-rank checker."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave39_cross_base", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class CrossBaseRankTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        self.assertEqual(CHECK.audit_inputs(), CHECK.FROZEN_INPUTS)

    def test_determinant_tower(self) -> None:
        result = CHECK.determinant_and_projection_spaces()
        self.assertEqual(
            result["centered_space"],
            {
                "dimension": 11,
                "determinant_class": "nonsquare",
                "determinant_representative": 2,
            },
        )
        self.assertEqual(
            result["orthogonal_complement"]["dimension"], 5
        )
        self.assertEqual(
            result["orthogonal_complement"]["determinant_representative"], 2
        )

    def test_five_space_counts(self) -> None:
        result = CHECK.quadratic_vector_counts()
        self.assertEqual(
            result["vector_counts_by_norm"], {"0": 81, "1": 72, "2": 90}
        )
        self.assertEqual(
            result["projective_point_counts_by_norm"],
            {"0": 40, "1": 36, "2": 45},
        )

    def test_adjacent_triangle_projection_profile(self) -> None:
        result = CHECK.adjacent_triangle_profile()
        self.assertEqual(result["triangles_adjacent_to_fixed_vertex"], 84)
        self.assertEqual(result["M_star_profile"], {"0": 5, "-1": 2})
        self.assertEqual(result["D_star_profile"], {"1": 5, "2": 2})
        self.assertEqual(result["projected_vector_norm"], 1)

    def test_collision_lower_bound_is_active(self) -> None:
        result = CHECK.projection_collision_theorem()
        self.assertEqual(
            result["forced_equal_projection_pairs_lower_bound"], 12
        )
        self.assertEqual(result["support_sizes"], [4, 6])
        self.assertEqual(CHECK.collision_lower_bound(84, 72), 12)
        with self.assertRaises(AssertionError):
            CHECK.collision_lower_bound(71, 72)

    def test_rank_ten_quotient_control(self) -> None:
        result = CHECK.local_rank_controls()["controls"][0]
        self.assertEqual(result["rank_F3_P_minus_I"], 10)
        self.assertEqual(result["degree"], 4)
        self.assertEqual(result["bipartite_block_degree"], 2)

    def test_determinant_compatible_rank_eleven_control(self) -> None:
        result = CHECK.local_rank_controls()["controls"][1]
        self.assertEqual(result["rank_F3_P_minus_I"], 11)
        self.assertEqual(result["discriminant_class"], "nonsquare")
        self.assertEqual(result["discriminant_representative"], 2)

    def test_mutated_quotient_is_rejected(self) -> None:
        mutated = list(CHECK.RANK_TEN_QUOTIENT)
        mutated[0] = tuple(range(6))
        with self.assertRaisesRegex(AssertionError, "derangement"):
            CHECK.build_quotient(tuple(mutated))

    def test_projection_positive_control(self) -> None:
        result = CHECK.projection_positive_control()
        self.assertEqual(result["adjacent_isotropic_vectors"], 84)
        self.assertEqual(result["distinct_adjacent_vectors"], 84)
        self.assertEqual(result["distinct_projection_values_used"], 72)
        self.assertEqual(result["equal_projection_pair_count"], 12)
        self.assertEqual(
            sum(result["short_dependency_support_histogram"].values()), 12
        )
        self.assertEqual(result["combined_gram_rank"], 11)

    def test_status_does_not_inflate(self) -> None:
        result = CHECK.build_results()
        conclusion = result["conclusion"]
        self.assertEqual(result["claim_label"], "DERIVED_INCONCLUSIVE")
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["upper_bound_improved_below_4158"])
        self.assertEqual(conclusion["target_status"], "UNKNOWN")
        self.assertEqual(
            conclusion["strongest_general_upper_bound_on_n3"], 4158
        )


if __name__ == "__main__":
    unittest.main()
