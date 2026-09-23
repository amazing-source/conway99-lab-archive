from __future__ import annotations

import unittest
from itertools import combinations

import exact_check as check


class EndpointIdentityTests(unittest.TestCase):
    def test_endpoint_profile(self) -> None:
        result = check.build_results()["endpoint"]
        self.assertEqual(result["triangular_prisms"], 0)
        self.assertEqual(result["q_per_triangle"], 12)
        self.assertEqual(
            result["disjoint_triangle_profile_a0_a1_a2_a3"],
            [32, 144, 36, 0],
        )

    def test_factorization_is_complete(self) -> None:
        edges = [edge for factor in check.FACTORS for edge in factor]
        self.assertEqual(len(edges), 66)
        self.assertEqual(set(edges), set(combinations(range(check.N), 2)))


class RestrictedCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adjacency = check.build_restricted_x_adjacency()
        self.gram = check.required_xy_gram(self.adjacency)

    def test_x_core_is_cubic_and_triangle_free(self) -> None:
        self.assertEqual(sorted(set(map(sum, self.adjacency))), [3])
        self.assertEqual(check.triangle_count(self.adjacency), 0)

    def test_cross_two_factor_has_six_hexagons(self) -> None:
        self.assertEqual(
            check.cycle_lengths(check.build_cross_two_factor()),
            (6, 6, 6, 6, 6, 6),
        )

    def test_required_gram_has_exact_rows(self) -> None:
        self.assertTrue(all(left == right for left, right in zip(self.gram, map(list, zip(*self.gram)))))
        self.assertEqual(sorted(set(map(sum, self.gram))), [60])
        self.assertEqual(min(map(min, self.gram)), 0)
        self.assertEqual(max(map(max, self.gram)), 10)

    def test_within_fibre_gram_rule(self) -> None:
        for fibre, factor_index in enumerate(check.WITHIN_FACTOR_INDICES):
            matching = set(check.FACTORS[factor_index])
            for left in range(check.N):
                for right in range(check.N):
                    value = self.gram[fibre * check.N + left][fibre * check.N + right]
                    if left == right:
                        self.assertEqual(value, 10)
                    elif tuple(sorted((left, right))) in matching:
                        self.assertEqual(value, 0)
                    else:
                        self.assertEqual(value, 1)

    def test_pairwise_control(self) -> None:
        pair_sets = tuple(
            check.allowed_pairs(index)
            for index in check.WITHIN_FACTOR_INDICES
        )
        actual = check.pair_concurrence(
            pair_sets[0],
            pair_sets[1],
            check.PAIR_01_CERTIFICATE,
        )
        expected = [row[check.N : 2 * check.N] for row in self.gram[: check.N]]
        self.assertEqual(actual, expected)

    def test_restricted_block_census(self) -> None:
        result = check.build_results()["restricted_core"]
        self.assertEqual(result["valid_single_block_type_count"], 183980)
        self.assertEqual(
            result["valid_single_block_types_by_internal_X_edges"],
            {"0": 68774, "1": 90364, "2": 24138, "3": 704},
        )

    def test_binary_ranks(self) -> None:
        self.assertEqual(check.gf2_rank(self.adjacency), 32)
        self.assertEqual(check.gf2_rank(self.gram), 28)


if __name__ == "__main__":
    unittest.main()
