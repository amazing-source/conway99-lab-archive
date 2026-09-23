#!/usr/bin/env python3
"""Hostile tests for the independent Wave 15 global-lift checker."""

from __future__ import annotations

import unittest

import independent_check as check


class GlobalLiftAuditTests(unittest.TestCase):
    def test_exact_srg_spectrum(self) -> None:
        self.assertEqual(check.srg_restricted_eigenvalues(), (3, -4))
        with self.assertRaises(ValueError):
            check.srg_restricted_eigenvalues(k=15, lam=1, mu=2)

    def test_all_active_point_profiles_have_at_most_24_vertices(self) -> None:
        profiles = check.point_size_profiles()
        self.assertEqual(len(profiles), 9)
        self.assertEqual({m for _, _, m in profiles}, set(range(16, 25)))

    def test_size_two_meeting_crossing_is_empty(self) -> None:
        for right_size in (2, 3):
            self.assertEqual(
                check.crossing_sizes_after_shared_label(2, right_size),
                {0},
            )

    def test_deleting_the_shared_label_is_essential(self) -> None:
        self.assertIn(
            4,
            check.crossing_sizes_after_shared_label(
                2, 3, delete_shared_label=False
            ),
        )

    def test_six_neighbors_exclude_every_profile(self) -> None:
        for _, _, m in check.point_size_profiles():
            self.assertGreater(check.spectral_contradiction_gap(m), 0)
            self.assertLess(check.aggregate_moment_defect(m, 0, 0), 0)

    def test_spectral_bound_stops_exactly_at_27(self) -> None:
        self.assertGreater(check.spectral_contradiction_gap(26), 0)
        self.assertEqual(check.spectral_contradiction_gap(27), 0)
        self.assertLess(check.spectral_contradiction_gap(28), 0)

    def test_fifth_neighbor_is_not_enough(self) -> None:
        self.assertLess(
            check.spectral_contradiction_gap(24, minimum_degree=5),
            0,
        )
        self.assertEqual(
            check.mandatory_neighbor_lower_bound(
                2,
                support_degree=2,
                possible_support_triangle_overlaps=1,
            ),
            5,
        )

    def test_positive_eigenvalue_mutation_breaks_the_claimed_gap(self) -> None:
        self.assertLess(
            check.spectral_contradiction_gap(
                24, positive_restricted_eigenvalue=4
            ),
            0,
        )

    def test_direct_and_expanded_moments_agree(self) -> None:
        for m in range(1, 25):
            self.assertEqual(
                check.direct_moment_defect((6,) * m),
                check.aggregate_moment_defect(m, 0, 0),
            )

    def test_more_internal_degree_cannot_repair_the_moment_defect(self) -> None:
        for m in range(16, 25):
            previous = check.aggregate_moment_defect(m, 0, 0)
            for total_excess in range(1, 8 * m + 1):
                current = check.aggregate_moment_defect(
                    m, total_excess, 0
                )
                self.assertLess(current, previous)
                previous = current

    def test_final_arithmetic(self) -> None:
        self.assertEqual(check.next_multiple_strictly_above(48, 3), 51)
        self.assertEqual(209_286 + 51, 209_337)


if __name__ == "__main__":
    unittest.main()
