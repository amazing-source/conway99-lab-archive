from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave188_independent_check", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave188IndependentTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        result = CHECK.verify_frozen_inputs()
        self.assertTrue(result["passed"])
        self.assertEqual(result["frozen_manifest_count"], 6)
        self.assertFalse(result["discovery_code_imported_or_executed"])

    def test_precise_affine_profile_domain(self) -> None:
        result = CHECK.affine_profile_census()
        self.assertEqual(result["profiles_checked"], 438)
        self.assertEqual(result["minimum_short_projective_words"], 3)
        self.assertEqual(result["minimum_equality_profiles"], 36)
        self.assertEqual(
            result["short_count_spectrum"],
            {"3": 36, "4": 140, "5": 226, "6": 36},
        )

    def test_projective_orbit_distinctness(self) -> None:
        result = CHECK.projective_orbit_check()
        self.assertEqual(result["distinct_projective_classes"], 9)
        self.assertFalse(result["scalar_collision_possible"])

    def test_support_capacity(self) -> None:
        result = CHECK.support_capacity_certificate()
        self.assertEqual(result["type_two_6_plus_2_capacity"], 1)
        self.assertEqual(result["type_three_3_plus_6_capacity"], 1)
        self.assertEqual(
            result["capacity_if_both_sides_at_least_two"]["weight_four"], 2
        )

    def test_one_block_projector_and_relation_plane(self) -> None:
        result = CHECK.one_block_projector_and_orbit()
        self.assertEqual(result["one_adjacency_square_sum_mod3"], 1)
        self.assertTrue(result["one_adjacency_contradiction"])
        self.assertEqual(result["cross_projective_weights"], [4, 5, 8])
        self.assertEqual(result["star_only_projective_weights"], [7])

    def test_type_two_translates(self) -> None:
        result = CHECK.type_two_words()
        self.assertEqual(result["distinct_projective_axis_translates"], 4)
        self.assertEqual(result["axis_translate_weights"], [8, 8, 8, 8])
        self.assertTrue(result["exact_singleton_by_capacity_lemma"])

    def test_type_three_words(self) -> None:
        result = CHECK.type_three_words()
        self.assertEqual(result["base_cross_word_weights"], [4, 5, 8])
        self.assertEqual(result["additional_base_words_per_selected_triple"], 2)
        self.assertEqual(result["leaf_translate_profile"], [3, 6])
        self.assertEqual(result["leaf_translate_weight"], 9)

    def test_disjointness_certificate(self) -> None:
        result = CHECK.disjointness_certificate()
        self.assertEqual(result["cross_category_pairs_checked"], 10)
        self.assertTrue(result["selected_cover_collision_excluded_by_private_label"])

    def test_final_count(self) -> None:
        result = CHECK.cover_count_certificate()
        self.assertEqual(result["coefficient_difference"], [0, -1, 0, 3, 0])
        self.assertEqual(result["nonedge_projective_short_words"], 8316)
        self.assertEqual(result["total_projective_short_words"], 9009)
        self.assertEqual(result["B4_through_B9_lower"], 18018)


if __name__ == "__main__":
    unittest.main()
