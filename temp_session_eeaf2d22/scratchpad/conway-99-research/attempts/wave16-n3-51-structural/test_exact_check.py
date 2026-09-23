"""Focused adversarial tests for the Wave 16 n3=51 exact checker."""

from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave16_n3_51_exact_check", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave16ExactCheckTests(unittest.TestCase):
    def test_raw_profiles_are_exhaustive(self) -> None:
        raw = CHECK.raw_profiles()
        self.assertEqual(len(raw), 16)
        self.assertEqual(
            {r: sum(1 for rr, _ in raw if rr == r) for r in range(12, 18)},
            {12: 1, 13: 5, 14: 4, 15: 3, 16: 2, 17: 1},
        )
        for r, profile in raw:
            self.assertEqual(len(profile), r)
            self.assertEqual(sum(profile), 34)
            self.assertTrue(all(q >= 2 and 3 * q <= r - 1 for q in profile))

    def test_exact_four_degree_filtered_profiles(self) -> None:
        survivors = CHECK.filtered_profiles(4)
        expected = [
            (14, (2,) * 8 + (3,) * 6),
            (15, (2,) * 11 + (3,) * 4),
            (16, (2,) * 14 + (3,) * 2),
            (17, (2,) * 17),
        ]
        self.assertEqual(survivors, expected)

    def test_repeated_degree_three_lemma_is_essential(self) -> None:
        weak = CHECK.filtered_profiles(3)
        strong = CHECK.filtered_profiles(4)
        extras = [profile for profile in weak if profile not in strong]
        self.assertIn((13, (2,) * 5 + (3,) * 8), extras)
        self.assertIn((16, (2,) * 15 + (4,)), extras)

    def test_two_sided_crossing_classification(self) -> None:
        for width in range(0, 17):
            self.assertEqual(CHECK.crossing_edge_counts(1, width), {0})
        for width in range(2, 18):
            self.assertEqual(CHECK.crossing_edge_counts(2, width), {0, 4})

    def test_one_sided_mutation_has_two_edge_witness(self) -> None:
        self.assertEqual(
            CHECK.crossing_edge_counts(2, 3, require_two_sided=False),
            {0, 2, 4},
        )
        self.assertEqual(CHECK.crossing_edge_counts(2, 3), {0, 4})

    def test_size_two_fixed_point_types(self) -> None:
        q22 = CHECK.size_two_point_record(2, 2)
        q23 = CHECK.size_two_point_record(2, 3)
        q33 = CHECK.size_two_point_record(3, 3)
        self.assertEqual(q22["forced_positive_support_neighbors"], 2)
        self.assertFalse(q23["compatible_with_0_or_4_crossings"])
        self.assertEqual(q33["forced_positive_support_neighbors"], 3)
        self.assertEqual(q33["induced_degree_lower_bound"], 7)

    def test_every_survivor_is_below_dense_subset_threshold(self) -> None:
        bounds = CHECK.build_result()["active_set_bounds"]
        self.assertEqual(
            [entry["active_vertex_upper_bound"] for entry in bounds],
            [21, 22, 24, 25],
        )
        for entry in bounds:
            m = entry["active_vertex_upper_bound"]
            self.assertLess(CHECK.spectral_average_upper_bound(m), Fraction(6))
        self.assertEqual(CHECK.spectral_average_upper_bound(27), Fraction(6))

    def test_frozen_artifact_matches(self) -> None:
        frozen = json.loads(
            (HERE / "exact-checks.json").read_text(encoding="utf-8")
        )
        self.assertEqual(frozen, CHECK.build_result())


if __name__ == "__main__":
    unittest.main(verbosity=2)
