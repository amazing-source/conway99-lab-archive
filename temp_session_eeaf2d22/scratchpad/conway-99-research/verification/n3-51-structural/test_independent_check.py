#!/usr/bin/env python3
"""Hostile tests for the independent Wave 16 structural checker."""

from __future__ import annotations

import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as check


class ProvenanceTests(unittest.TestCase):
    def test_final_public_input_hashes_are_frozen(self) -> None:
        provenance = check.wave15_provenance()
        self.assertTrue(provenance["matches_final_public_sha256"])
        self.assertEqual(
            provenance["observed_sha256"], check.FINAL_WAVE15_AUDIT_SHA256
        )
        self.assertEqual(
            provenance["observed_sha256"],
            check.sha256_file(
                Path(__file__).resolve().parents[1]
                / "2026-07-23-wave15-global-lift-audit.md"
            ),
        )
        discovery = check.wave16_discovery_provenance()
        self.assertTrue(discovery["matches_final_public_sha256"])
        self.assertEqual(
            discovery["observed_sha256"],
            check.FINAL_WAVE16_DISCOVERY_SHA256,
        )
        self.assertEqual(
            discovery["observed_sha256"],
            check.sha256_file(
                Path(__file__).resolve().parents[2]
                / "agents"
                / "2026-07-23-wave16-n3-51-structural.md"
            ),
        )

    def test_historical_input_hashes_are_retained_but_not_current(self) -> None:
        provenance = check.wave15_provenance()
        self.assertEqual(
            provenance["historical_intermediate_uncommitted_sha256"],
            check.HISTORICAL_WAVE15_INTERMEDIATE_SHA256,
        )
        self.assertNotEqual(
            check.HISTORICAL_WAVE15_INTERMEDIATE_SHA256,
            check.FINAL_WAVE15_AUDIT_SHA256,
        )
        self.assertNotEqual(
            check.HISTORICAL_WAVE15_DECLARED_SHA256,
            check.FINAL_WAVE15_AUDIT_SHA256,
        )
        discovery = check.wave16_discovery_provenance()
        self.assertEqual(
            discovery["historical_pre_repair_sha256"],
            check.HISTORICAL_WAVE16_DISCOVERY_SHA256,
        )
        self.assertEqual(
            discovery["historical_failed_baseline_commit"],
            check.HISTORICAL_WAVE16_DISCOVERY_BASELINE_COMMIT,
        )
        self.assertEqual(
            discovery["final_provenance_repair_commit"],
            check.FINAL_WAVE16_DISCOVERY_REPAIR_COMMIT,
        )
        self.assertNotEqual(
            check.HISTORICAL_WAVE16_DISCOVERY_SHA256,
            check.FINAL_WAVE16_DISCOVERY_SHA256,
        )


class ExactProfileTests(unittest.TestCase):
    def test_exact_sixteen_profiles_and_four_survivors(self) -> None:
        raw = check.enumerate_profiles()
        self.assertEqual(raw, check.EXPECTED_RAW)
        self.assertEqual(
            check.filter_min_k_degree(raw, 4), check.EXPECTED_DK4_SURVIVORS
        )

    def test_degree_three_weakening_adds_exactly_two_rows(self) -> None:
        raw = check.enumerate_profiles()
        weak = check.filter_min_k_degree(raw, 3)
        strong = check.filter_min_k_degree(raw, 4)
        self.assertEqual(weak, check.EXPECTED_DK3_SURVIVORS)
        self.assertEqual(len(weak) - len(strong), 2)
        self.assertIn((13, (2,) * 5 + (3,) * 8), weak)
        self.assertIn((16, (2,) * 15 + (4,)), weak)

    def test_degree_three_forces_forbidden_point_triangle(self) -> None:
        systems = check.degree_three_forced_point_systems()
        self.assertEqual(len(systems), 2)
        for system in systems:
            self.assertTrue(check.has_three_distinct_pairwise_meetings(system))


class CrossingTests(unittest.TestCase):
    def test_meeting_crossings_are_empty_after_deletion(self) -> None:
        for other_size in range(1, 18):
            with self.subTest(other_size=other_size):
                self.assertEqual(
                    check.endpoint_crossing_counts(2, other_size, overlap=1),
                    (0,),
                )

    def test_disjoint_crossings_are_zero_or_four(self) -> None:
        self.assertEqual(check.endpoint_crossing_counts(2, 0, 0), (0,))
        self.assertEqual(check.endpoint_crossing_counts(2, 1, 0), (0,))
        for other_size in range(2, 18):
            with self.subTest(other_size=other_size):
                self.assertEqual(
                    check.endpoint_crossing_counts(2, other_size, overlap=0),
                    (0, 4),
                )

    def test_row_only_mutation_admits_two_edges(self) -> None:
        self.assertEqual(check.row_only_crossing_counts(2, 3), (0, 2, 4))
        self.assertNotIn(2, check.admissible_crossing_masks(2, 3))

    def test_retaining_common_label_can_admit_four(self) -> None:
        # With the shared label incorrectly retained, a size-two endpoint has
        # two rows rather than one; a 2-by-3 crossing can be K_(2,2).
        self.assertIn(4, check.admissible_crossing_masks(2, 3))
        # Correct deletion leaves one row and forces zero.
        self.assertEqual(check.admissible_crossing_masks(1, 2), (0,))

    def test_fixed_sums_and_two_edge_mutation(self) -> None:
        self.assertEqual(check.fixed_sum_positive_counts(2, 2), (2,))
        self.assertEqual(check.fixed_sum_positive_counts(2, 3), ())
        self.assertEqual(check.fixed_sum_positive_counts(3, 3), (3,))
        weakened = check.weakened_fixed_sum_positive_counts(2, 3)
        self.assertIn((1, 2), weakened)  # 2+4+4=10
        self.assertIn((5, 0), weakened)

    def test_positive_support_is_active_disjoint_and_nontriangle(self) -> None:
        for other_size in range(2, 18):
            properties = check.positive_support_properties(other_size, 0, 4)
            self.assertTrue(all(properties.values()))
        for other_size in range(1, 18):
            properties = check.positive_support_properties(other_size, 1, 4)
            self.assertFalse(properties["allowed"])
            self.assertFalse(properties["positive"])

    def test_global_zero_or_four_is_not_assumed(self) -> None:
        # A 3-by-3 two-sided 0/2 crossing can be a six-cycle.
        self.assertIn(6, check.admissible_crossing_masks(3, 3))


class OriginalVertexBridgeTests(unittest.TestCase):
    def test_triangle_neighbors_are_distinct(self) -> None:
        for size in range(2, 18):
            neighbors = check.active_triangle_neighbors(size)
            self.assertEqual(len(neighbors), 2 * size)
            self.assertEqual(len(set(neighbors)), 2 * size)

    def test_repeated_triangle_neighbor_is_rejected(self) -> None:
        good = (("a", "b"), ("c", "d"), ("e", "f"))
        bad = (("a", "b"), ("b", "d"), ("e", "f"))
        self.assertTrue(check.valid_triangle_neighbor_family(3, good))
        self.assertFalse(check.valid_triangle_neighbor_family(3, bad))

    def test_multiple_support_incidences_need_distinct_vertex_indices(self) -> None:
        positive_neighbor_ids = ("v1", "v2", "v3")
        repeated_ids = ("v1", "v1", "v3")
        self.assertEqual(len(positive_neighbor_ids), len(set(positive_neighbor_ids)))
        self.assertNotEqual(len(repeated_ids), len(set(repeated_ids)))

    def test_point_sizes_above_three_are_explicitly_covered(self) -> None:
        rows = check.local_degree_rows()
        for size in range(4, 8):
            [row] = [entry for entry in rows if entry["point_size"] == size]
            self.assertTrue(row["admissible"])
            self.assertEqual(row["triangle_neighbors"], 2 * size)
            self.assertGreaterEqual(row["minimum_active_degree"], 8)
        for size in range(8, 18):
            [row] = [entry for entry in rows if entry["point_size"] == size]
            self.assertFalse(row["admissible"])
            self.assertGreater(row["triangle_neighbors"], 14)

    def test_size_two_minimum_degree_and_mixed_exclusion(self) -> None:
        size_two = [
            row for row in check.local_degree_rows() if row["point_size"] == 2
        ]
        by_type = {tuple(row["q_types"]): row for row in size_two}
        self.assertEqual(by_type[(2, 2)]["minimum_active_degree"], 6)
        self.assertFalse(by_type[(2, 3)]["admissible"])
        self.assertEqual(by_type[(3, 3)]["minimum_active_degree"], 7)

    def test_singleton_mutation_destroys_active_set_bound(self) -> None:
        # With size>=2, r=17 gives at most floor(51/2)=25 indexed vertices.
        self.assertEqual(check.active_set_bounds(((17, (2,) * 17),)), ((17, 25),))
        # If singleton points were permitted, the same incidence total allows
        # 51 vertices and the spectral contradiction disappears.
        self.assertGreaterEqual(3 * 17, 27)


class SpectralTests(unittest.TestCase):
    def test_exact_threshold_is_27(self) -> None:
        self.assertEqual(check.first_order_allowed_by_spectral_bound(), 27)
        self.assertGreater(
            Fraction(6 * 25, 1), check.spectral_upper_twice_edges(25)
        )
        self.assertEqual(
            Fraction(6 * 27, 1), check.spectral_upper_twice_edges(27)
        )

    def test_wrong_restricted_eigenvalue_breaks_contradiction(self) -> None:
        self.assertEqual(
            check.first_order_allowed_by_spectral_bound(restricted_max=4), 20
        )
        self.assertLessEqual(
            Fraction(6 * 25, 1),
            check.spectral_upper_twice_edges(25, restricted_max=4),
        )

    def test_minimum_degree_five_is_insufficient(self) -> None:
        self.assertLessEqual(
            Fraction(5 * 25, 1), check.spectral_upper_twice_edges(25)
        )


class ConsequenceTests(unittest.TestCase):
    def test_incidence_identity_forces_three_to_divide_n3(self) -> None:
        replay = check.divisibility_replay(check.TARGET_N3, check.SUM_Q)
        self.assertTrue(all(replay.values()))
        self.assertFalse(
            check.divisibility_replay(check.TARGET_N3 + 1, check.SUM_Q)[
                "incidence_identity_holds"
            ]
        )

    def test_next_multiple_and_induced_c6_bound(self) -> None:
        next_n3 = check.next_multiple_strictly_above(check.TARGET_N3, 3)
        self.assertEqual(next_n3, 54)
        self.assertEqual(check.induced_c6_count(next_n3), 209340)
        with self.assertRaises(ValueError):
            check.next_multiple_strictly_above(check.TARGET_N3, 0)


class WholePayloadTests(unittest.TestCase):
    def test_built_payload_self_verifies(self) -> None:
        payload = check.build_results()
        check.verify_results(payload)
        self.assertEqual(payload["status"]["conway_99"], "UNKNOWN")
        self.assertEqual(payload["status"]["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
