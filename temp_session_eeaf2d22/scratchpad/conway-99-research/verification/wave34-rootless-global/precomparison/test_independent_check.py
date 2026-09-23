#!/usr/bin/env python3
"""Hostile exact tests for the Wave 34 clean-room verifier package."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from fractions import Fraction
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave34_rootless_precomparison", HERE / "independent_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class FrozenInputTests(unittest.TestCase):
    def test_all_frozen_inputs_match(self) -> None:
        result = CHECK.validate_inputs()
        self.assertTrue(result["all_match"], result["mismatches"])
        self.assertTrue(result["freeze_file_matches_expected"])
        self.assertEqual(result["entry_count"], 18)


class BoardTests(unittest.TestCase):
    def test_all_four_relation_boards(self) -> None:
        expected = {
            0: ([[2, 2, 2], [2, 2, 2], [2, 2, 2]], 48),
            1: ([[1, 1, 1], [1, 2, 2], [1, 2, 2]], 16),
            2: ([[1, 0, 1], [0, 1, 1], [1, 1, 2]], 4),
            3: ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1),
        }
        for r, (board, permanent) in expected.items():
            self.assertEqual(CHECK.outside_board(r), board)
            self.assertEqual(CHECK.weighted_permanent(board), permanent)

    def test_mu_three_hostile_mutation(self) -> None:
        board = CHECK.outside_board(2, mu=3)
        self.assertEqual(board, [[1, 1, 2], [1, 1, 2], [2, 2, 3]])
        self.assertEqual(CHECK.weighted_permanent(board), 22)


class FibreTests(unittest.TestCase):
    def test_permutation_moved_point_domain(self) -> None:
        with self.assertRaises(ValueError):
            CHECK.moved_permutation(1)
        for q in [0, *range(2, 13)]:
            p = CHECK.moved_permutation(q)
            self.assertEqual(12 - len(CHECK.fixed_points(p)), q)

    def test_degree_transport(self) -> None:
        for profile in CHECK.fibre_profiles():
            q = profile["q"]
            self.assertEqual(profile["R2_degree"], 3 * q)
            self.assertEqual(profile["R3_degree"], 12 - q)

    def test_three_disjoint_matchings_are_perfect(self) -> None:
        matchings = CHECK.disjoint_matchings()
        CHECK.validate_matchings(matchings)
        edge_sets = [{tuple(sorted(edge)) for edge in m} for m in matchings]
        self.assertFalse(edge_sets[0] & edge_sets[1])
        self.assertFalse(edge_sets[0] & edge_sets[2])
        self.assertFalse(edge_sets[1] & edge_sets[2])

    def test_zero_motif_controls_for_every_permitted_q(self) -> None:
        for profile in CHECK.fibre_profiles():
            self.assertEqual(profile["root_motif_count_centered_here"], 0)
            self.assertLessEqual(profile["maximum_weighted_relation_degree"], 3)

    def test_laplacian_quadratic_identity(self) -> None:
        matchings = CHECK.disjoint_matchings()
        fixed = set(CHECK.fixed_points(CHECK.moved_permutation(3)))
        maps = CHECK.matching_maps(matchings)
        values = {i: ((3 * i + 1) % 5) - 2 for i in fixed}
        left = 3 * sum(v * v for v in values.values())
        for mate in maps:
            for i in fixed:
                if mate[i] in fixed:
                    left -= values[i] * values[mate[i]]
        extended = {i: values.get(i, 0) for i in range(12)}
        right = 0
        for matching in matchings:
            right += sum((extended[u] - extended[v]) ** 2 for u, v in matching)
        self.assertEqual(left, right)
        self.assertGreaterEqual(left, 0)

    def test_r2_compatible_index_cap_and_tight_control(self) -> None:
        for q in [0, *range(2, 13)]:
            cap = CHECK.fibre_r2_candidate_cap(
                CHECK.moved_permutation(q), CHECK.disjoint_matchings()
            )
            self.assertLessEqual(cap, 1)
        witness = CHECK.tight_r2_candidate_witness()
        self.assertEqual(witness["compatible_index_cap"], 1)
        self.assertEqual(witness["centered_root_motifs_before_Z_closure"], 0)


class ProjectorTests(unittest.TestCase):
    def test_exact_common_r3_caps(self) -> None:
        caps = CHECK.projector_codegree_caps()
        self.assertEqual({s: caps[s]["maximum_common_R3"] for s in caps}, {
            1: 5,
            0: 3,
            -1: 1,
            -2: 1,
        })

    def test_cap_fractions(self) -> None:
        caps = CHECK.projector_codegree_caps()
        self.assertEqual(caps[1]["residual_diagonal"], "12/5")
        self.assertEqual(caps[1]["residual_off_diagonal_upper_bound"], "-3/5")
        self.assertEqual(caps[-1]["residual_diagonal"], "4/3")
        self.assertEqual(caps[-2]["residual_diagonal"], "0")

    def test_off_diagonal_alphabet_cap_is_active(self) -> None:
        mutated = CHECK.projector_codegree_caps(max_off_diagonal=2)
        self.assertGreater(mutated[1]["maximum_common_R3"], 5)

    def test_r0_biclique_determinants(self) -> None:
        expected = [15, 36, 81, 162, 243, 0, -2187]
        actual = [
            CHECK.bareiss_determinant(CHECK.r0_biclique_gram(m))
            for m in range(7)
        ]
        self.assertEqual(actual, expected)

    def test_r0_codegree_five_dependency(self) -> None:
        gram = CHECK.r0_biclique_gram(5)
        vector = [2, 2, 1, 1, 1, 1, 1]
        self.assertEqual(CHECK.matrix_vector(gram, vector), [0] * 7)

    def test_hostile_sixth_common_neighbour_is_indefinite(self) -> None:
        self.assertLess(
            CHECK.bareiss_determinant(CHECK.r0_biclique_gram(6)), 0
        )


class EndpointTests(unittest.TestCase):
    def test_endpoint_pair_census(self) -> None:
        result = CHECK.endpoint_counts()
        self.assertEqual(result["unordered"], {
            "Gamma": 2079,
            "R0": 2546,
            "R1": 20082,
            "R2": 708,
            "R3": 1150,
        })
        self.assertEqual(sum(result["unordered"].values()), comb(231, 2))

    def test_pointwise_r0_wedge_floor(self) -> None:
        for b in range(13):
            self.assertGreaterEqual(CHECK.local_r0_lower(b), 7 * b - 40)

    def test_global_r0_wedge_lower_and_sharp_scalar_profile(self) -> None:
        result = CHECK.global_r0_wedge_lower()
        self.assertEqual(result["minimum_R0_centered_wedges"], 6860)
        self.assertEqual(result["sharp_scalar_witness_b_counts"], {
            "8": 5,
            "10": 226,
        })

    def test_forced_r0_codegree_occupancy(self) -> None:
        result = CHECK.global_r0_wedge_lower()
        occupancy = result["forced_occupancy"]
        self.assertEqual(occupancy, {
            "pairs_with_codegree_at_least_1": 1372,
            "pairs_with_codegree_at_least_2": 1079,
            "pairs_with_codegree_at_least_3": 590,
        })
        self.assertEqual(result["minimum_sum_binom_R0_codegree_2"], 6082)
        self.assertEqual(result["R3_four_cycle_lower"], 3041)
        self.assertEqual(result["minimum_total_R3_wedges"], 10305)
        self.assertEqual(result["R3_adjacency_trace_fourth_lower"], 67848)

    def test_mixed_trace_cap_and_rootless_value(self) -> None:
        result = CHECK.build_results()["endpoint_global_overlap"]
        self.assertEqual(result["unrestricted_trace_cap_from_projector"], 1416)
        self.assertEqual(result["rootless_trace"], 0)


class TransportTests(unittest.TestCase):
    def test_one_leg_transport_entry_values(self) -> None:
        # K=9N-3AN+J; AN has entries 2,1,0 in the three incidence cases.
        self.assertEqual(9 - 3 * 2 + 1, 4)
        self.assertEqual(0 - 3 * 1 + 1, -2)
        self.assertEqual(0 - 3 * 0 + 1, 1)
        self.assertEqual(3 * 4 + 36 * (-2) + 60, 0)

    def test_column_norm_matches_63M_diagonal(self) -> None:
        norm = 3 * 4**2 + 36 * (-2) ** 2 + 60
        self.assertEqual(norm, 63 * 4)


if __name__ == "__main__":
    unittest.main()
